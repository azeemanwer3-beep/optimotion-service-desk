"""
Conversation API routes.

Endpoints:
  POST   /api/conversations                      — Start a new conversation
  GET    /api/conversations                      — List all conversations
  GET    /api/conversations/{id}                 — Get conversation with messages
  POST   /api/conversations/{id}/messages        — Send message (SSE streaming response)
  POST   /api/conversations/{id}/resolve         — Mark conversation as resolved
  POST   /api/conversations/{id}/escalate        — Escalate to service ticket
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db, SessionLocal
from models import Conversation, Message, Ticket, ConversationStatus
from schemas import (
    CreateConversation,
    SendMessage,
    ConversationResponse,
    ConversationListItem,
)
from services.ai_service import ai_service

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationResponse, status_code=201)
def create_conversation(data: CreateConversation, db: Session = Depends(get_db)):
    """Start a new support conversation. Categorizes the issue and sends an initial AI response."""
    # AI-powered issue categorization
    category = ai_service.categorize_issue(data.issue_description)

    conversation = Conversation(
        vehicle_id=data.vehicle_id,
        issue_description=data.issue_description,
        category=category,
        status=ConversationStatus.ACTIVE.value,
    )
    db.add(conversation)
    db.flush()

    # Save the user's initial message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=data.issue_description,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get("", response_model=list[ConversationListItem])
def list_conversations(db: Session = Depends(get_db)):
    """List all conversations, newest first."""
    return (
        db.query(Conversation)
        .order_by(Conversation.created_at.desc())
        .all()
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Get a single conversation with its full message history."""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/{conversation_id}/messages")
def send_message(conversation_id: str, data: SendMessage, db: Session = Depends(get_db)):
    """
    Send a message in a conversation and stream the AI response via SSE.

    Returns a text/event-stream with events:
      - type=chunk   → partial AI response text
      - type=done    → streaming complete, includes message_id
      - type=error   → error occurred
    """
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.status != ConversationStatus.ACTIVE.value:
        raise HTTPException(status_code=400, detail="Conversation is no longer active")

    # Persist user message
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=data.content,
    )
    db.add(user_msg)
    db.commit()

    # Build conversation history for the AI
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )
    message_history = [{"role": m.role, "content": m.content} for m in messages]

    def event_stream():
        """Generator that streams AI response chunks as SSE events."""
        full_response = ""
        try:
            for chunk in ai_service.stream_response(message_history):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            return

        # Save the complete AI response to the database
        stream_db = SessionLocal()
        try:
            assistant_msg = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=full_response,
            )
            stream_db.add(assistant_msg)
            stream_db.commit()
            yield f"data: {json.dumps({'type': 'done', 'message_id': assistant_msg.id})}\n\n"
        finally:
            stream_db.close()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{conversation_id}/resolve")
def resolve_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Mark a conversation as resolved (issue fixed via troubleshooting)."""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.status = ConversationStatus.RESOLVED.value
    db.commit()

    return {
        "status": "resolved",
        "message": "Glad we could help! The conversation has been closed.",
    }


@router.post("/{conversation_id}/escalate")
def escalate_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Escalate a conversation to a service ticket.
    Uses AI to generate a structured ticket summary from the conversation.
    """
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.status == ConversationStatus.ESCALATED.value:
        raise HTTPException(status_code=400, detail="Conversation already escalated")

    # Get full conversation history
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )
    message_history = [{"role": m.role, "content": m.content} for m in messages]

    # AI-generated ticket summary
    ticket_data = ai_service.generate_ticket_summary(message_history)

    # Create the service ticket
    ticket = Ticket(
        conversation_id=conversation_id,
        vehicle_id=conversation.vehicle_id,
        title=ticket_data.get("title", "Service Required"),
        description=ticket_data.get("description", conversation.issue_description),
        category=ticket_data.get("category", conversation.category),
        priority=ticket_data.get("priority", "medium"),
        ai_summary=ticket_data.get("ai_summary", ""),
    )
    db.add(ticket)

    conversation.status = ConversationStatus.ESCALATED.value
    db.commit()
    db.refresh(ticket)

    return {
        "status": "escalated",
        "message": "A service ticket has been created for your issue.",
        "ticket": {
            "id": ticket.id,
            "title": ticket.title,
            "priority": ticket.priority,
            "category": ticket.category,
        },
    }
