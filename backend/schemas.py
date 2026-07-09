"""
Pydantic schemas for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── Request Schemas ──────────────────────────────────────────────────────────

class CreateConversation(BaseModel):
    vehicle_id: str = Field(..., min_length=1, max_length=50, description="Vehicle identifier")
    issue_description: str = Field(..., min_length=5, max_length=2000, description="Description of the issue")


class SendMessage(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None


# ─── Response Schemas ─────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: str
    vehicle_id: str
    issue_description: str
    category: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    id: str
    vehicle_id: str
    issue_description: str
    category: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    id: str
    conversation_id: str
    vehicle_id: str
    title: str
    description: str
    category: Optional[str] = None
    priority: str
    status: str
    ai_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
