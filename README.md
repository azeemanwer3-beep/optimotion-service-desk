# 🚗⚡ Optimotion Service Desk

**AI-Assisted Service Ticket Flow for EV Rental Support**

An intelligent support system that uses AI to troubleshoot customer issues with rented electric vehicles before escalating to service tickets — reducing unnecessary ticket creation and improving customer experience.

🌍 **Live Website:** [https://optimotion-service-desk.vercel.app/](https://optimotion-service-desk.vercel.app/)
🐙 **GitHub Repository:** [https://github.com/azeemanwer3-beep/optimotion-service-desk](https://github.com/azeemanwer3-beep)

![Tech Stack](https://img.shields.io/badge/React-18-blue?logo=react) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi) ![Gemini](https://img.shields.io/badge/Gemini-2.0-orange?logo=google) ![SQLite](https://img.shields.io/badge/SQLite-3-lightblue?logo=sqlite)

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [API Reference](#api-reference)
- [Design Decisions](#design-decisions)
- [Assumptions](#assumptions)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React + Vite)                │
│                                                             │
│  ┌──────────┐  ┌───────────────┐  ┌──────────────────────┐ │
│  │ Sidebar  │  │ Chat Interface│  │  Ticket Dashboard    │ │
│  │          │  │               │  │                      │ │
│  │ • Convos │  │ • Messages    │  │  • Stats Cards       │ │
│  │ • Nav    │  │ • Streaming   │  │  • Ticket List       │ │
│  │ • Status │  │ • Resolution  │  │  • Priority/Status   │ │
│  └──────────┘  └───────┬───────┘  └──────────────────────┘ │
│                        │ SSE Stream                         │
└────────────────────────┼────────────────────────────────────┘
                         │ HTTP / SSE
┌────────────────────────┼────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│                        │                                    │
│  ┌─────────────────────▼─────────────────────────────────┐ │
│  │              API Layer (Routes)                        │ │
│  │                                                        │ │
│  │  POST /api/conversations        → Create conversation  │ │
│  │  POST /api/conversations/:id/messages → Stream AI resp │ │
│  │  POST /api/conversations/:id/resolve  → Mark resolved  │ │
│  │  POST /api/conversations/:id/escalate → Create ticket  │ │
│  │  GET  /api/tickets              → List tickets         │ │
│  └──────────────┬──────────────────┬──────────────────────┘ │
│                 │                  │                         │
│  ┌──────────────▼──────┐ ┌────────▼─────────────────────┐  │
│  │    AI Service       │ │    Database (SQLAlchemy)      │  │
│  │                     │ │                               │  │
│  │ • Gemini 2.0 Flash  │ │ ┌─────────────┐              │  │
│  │ • Streaming resp.   │ │ │Conversations│              │  │
│  │ • Issue categorize  │ │ │  ├─Messages  │              │  │
│  │ • Ticket summarize  │ │ │  └─Tickets   │              │  │
│  │ • Mock fallback     │ │ └─────────────┘              │  │
│  └─────────────────────┘ │        SQLite                 │  │
│                          └───────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Customer Reports Issue
       │
       ▼
  ┌──────────┐     ┌─────────────┐     ┌──────────┐
  │ Frontend │────▶│  FastAPI     │────▶│  Gemini  │
  │ (React)  │◀────│  Backend     │◀────│  AI API  │
  └──────────┘ SSE └─────────────┘     └──────────┘
       │                │
       ▼                ▼
  Did it help?    Save to SQLite
       │
  ┌────┴────┐
  │         │
 YES       NO
  │         │
Close    AI generates
Conv.    ticket summary
         → Create Ticket
```

---

## ✨ Features

### Core
- **AI Troubleshooting** — Gemini-powered step-by-step guidance for common EV issues
- **Real-time Streaming** — SSE-based streaming for instant, character-by-character AI responses
- **Resolution Flow** — One-click resolve or escalate to service ticket
- **Auto Ticket Creation** — AI generates structured tickets with title, priority, category, and summary

### Bonus Features
- **Issue Categorization** — AI auto-categorizes issues (battery, charging, starting, app, etc.)
- **Priority Scoring** — AI-assessed severity for created tickets
- **Ticket Dashboard** — Admin view with stats and ticket management
- **Streaming Responses** — Real-time SSE streaming for premium UX
- **Mock Mode** — Full demo without API key using keyword-based responses
- **Conversation History** — Persistent multi-turn conversations
- **Premium Dark UI** — Glassmorphism, animations, and a polished EV-themed design

---

## 🛠️ Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React 18 + Vite | Fast dev, preferred stack per requirements |
| **Styling** | Vanilla CSS | Custom design system, no framework bloat |
| **Icons** | Lucide React | Consistent, lightweight icon set |
| **Backend** | FastAPI (Python) | Async support, auto docs, first-class LLM SDK support |
| **AI** | Google Gemini 2.0 Flash | Fast, capable, generous free tier |
| **Database** | SQLite + SQLAlchemy ORM | Zero-config persistence, production-ready ORM |
| **Streaming** | Server-Sent Events (SSE) | Native browser support, simple real-time communication |

---

## 🚀 Setup Instructions

### Prerequisites
- **Python** 3.10+ ([download](https://www.python.org/downloads/))
- **Node.js** 18+ ([download](https://nodejs.org/))
- **Google API Key** (optional — app works in mock mode without it)

### 1. Clone the Repository

```bash
git clone https://github.com/azeemanwer3-beep/optimotion-service-desk.git
cd optimotion-service-desk
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional — works without API key in mock mode)
copy .env.example .env
# Edit .env and add your GOOGLE_API_KEY from https://aistudio.google.com/apikey

# Start the server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app will be available at `http://localhost:3000`.

### 4. (Optional) Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key
3. Add it to `backend/.env` as `GOOGLE_API_KEY=your_key_here`
4. Restart the backend server

> **Note:** The app works perfectly in **mock mode** without an API key. Mock mode provides realistic troubleshooting responses based on keyword matching.

---

## 📡 API Reference

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/conversations` | Create a new conversation |
| `GET` | `/api/conversations` | List all conversations |
| `GET` | `/api/conversations/:id` | Get conversation with messages |
| `POST` | `/api/conversations/:id/messages` | Send message (SSE streaming response) |
| `POST` | `/api/conversations/:id/resolve` | Mark as resolved |
| `POST` | `/api/conversations/:id/escalate` | Escalate to service ticket |

### Tickets

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tickets` | List all tickets |
| `GET` | `/api/tickets/:id` | Get ticket details |
| `PATCH` | `/api/tickets/:id` | Update ticket status/priority |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |

---

## 🎯 Design Decisions

1. **Python over Java** — Faster prototyping with first-class AI SDK support. FastAPI provides the same enterprise patterns (DI, validation, auto-docs) as Spring Boot.

2. **SSE over WebSocket** — Simpler for unidirectional streaming (server → client). No connection management overhead. Native browser support.

3. **SQLite over In-Memory** — Zero-config persistence that survives restarts. SQLAlchemy ORM means migrating to PostgreSQL is a one-line config change.

4. **Mock Mode** — Allows immediate testing without API key setup. Demonstrates keyword-based fallback strategy — useful for rate limiting scenarios in production.

5. **Structured AI Output** — AI doesn't just chat — it categorizes issues and generates structured ticket summaries. This makes the data actionable for operations teams.

6. **Conversation State Machine** — Clean `ACTIVE → RESOLVED | ESCALATED` transitions prevent invalid operations (e.g., messaging a closed conversation).

---

## 📝 Assumptions

1. **Vehicle IDs** are freeform strings (no validation against a vehicle database)
2. **No authentication** — This is a prototype; in production, OAuth2/JWT would secure all endpoints
3. **Single-user** — No concurrent session management; production would use user accounts
4. **Gemini Flash** — Used for speed over quality; production might use Gemini Pro for complex diagnostics
5. **Issue categories** are predefined (battery, charging, starting, app, infotainment, tire, safety, other)
6. **Mock responses** are keyword-based for demo purposes; actual AI provides context-aware responses

---

## 🔮 Production Considerations

If deploying to production, consider:

- **Authentication**: OAuth2 + JWT token-based auth
- **Rate Limiting**: Per-user API rate limits for AI endpoints
- **Database**: Migrate from SQLite to PostgreSQL
- **Caching**: Redis for session/conversation caching
- **Monitoring**: Structured logging, APM (e.g., Datadog)
- **CI/CD**: GitHub Actions → Docker → Cloud Run/ECS
- **Testing**: Unit tests (pytest), integration tests, E2E tests (Playwright)
- **Multi-tenancy**: Support multiple fleet operators

---

## 📄 License

MIT
