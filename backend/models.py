"""
SQLAlchemy ORM models for the Optimotion Service Desk.

Schema:
  - Conversation: tracks a customer support session
  - Message: individual messages within a conversation
  - Ticket: service tickets created when issues can't be resolved via AI
"""

import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


# ─── Enums ────────────────────────────────────────────────────────────────────

class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


# ─── Models ───────────────────────────────────────────────────────────────────

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = Column(String, nullable=False, index=True)
    issue_description = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    status = Column(String, default=ConversationStatus.ACTIVE.value)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    messages = relationship(
        "Message", back_populates="conversation", order_by="Message.created_at"
    )
    ticket = relationship("Ticket", back_populates="conversation", uselist=False)


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    vehicle_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    priority = Column(String, default=TicketPriority.MEDIUM.value)
    status = Column(String, default=TicketStatus.OPEN.value)
    ai_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    conversation = relationship("Conversation", back_populates="ticket")
