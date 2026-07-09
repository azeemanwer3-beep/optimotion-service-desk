"""
Ticket API routes.

Endpoints:
  GET    /api/tickets              — List all service tickets
  GET    /api/tickets/{id}         — Get a single ticket
  PATCH  /api/tickets/{id}         — Update ticket status/priority
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Ticket
from schemas import TicketResponse, TicketUpdate

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.get("", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    """List all service tickets, newest first."""
    return db.query(Ticket).order_by(Ticket.created_at.desc()).all()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Get a single ticket by ID."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: str, data: TicketUpdate, db: Session = Depends(get_db)):
    """Update a ticket's status or priority."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if data.status is not None:
        ticket.status = data.status
    if data.priority is not None:
        ticket.priority = data.priority

    db.commit()
    db.refresh(ticket)
    return ticket
