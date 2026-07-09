"""
Optimotion Service Desk — FastAPI Application Entry Point

An AI-assisted service ticket flow for EV rental support.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes import conversations, tickets


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    print("[READY] Optimotion Service Desk API is ready")
    yield


app = FastAPI(
    title="Optimotion Service Desk API",
    description="AI-Assisted Service Ticket Flow for EV Rental Support",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(conversations.router)
app.include_router(tickets.router)


@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Optimotion Service Desk API"}
