
markdown
# Smart Campus Assistant

An AI-powered chatbot web application built to instantly answer student queries about campus information at BGU. Developed as a capstone evaluation project for **Elad Systems**.

---

## Live URLs (Docker)

| Service | URL |
|---|---|
| Frontend | http://localhost:3001 |
| Backend API | http://localhost:8001 |
| API Docs (Swagger) | http://localhost:8001/docs |

---

## Architecture Overview

| Layer | Technology |
|---|---|
| **Frontend** | React 19 + Vite 8, React Router v7, CSS Flexbox |
| **Backend** | FastAPI (Python 3.11), Uvicorn, SQLAlchemy 2.x |
| **Database** | SQLite (`backend/DB/smart_campus.db`) |
| **AI** | Google Gemini API (`gemini-2.5-flash-lite` with `gemini-2.5-flash` fallback) |
| **Auth** | JWT (PyJWT) + bcrypt 4.0.1 via passlib |
| **Deployment** | Docker multi-stage builds + Docker Compose |

---

## Features

- **Secure Auth** — Register + Login screens with JWT; protected routes; session persisted via localStorage
- **Conversation Management** — Create, list, open, and delete chat conversations (sidebar)
- **AI Chat** — Context-aware answers scoped to each conversation's message history
- **Global State** — `AuthContext` (token/auth) + `ChatContext` (conversations/messages) via React Context API
- **Service Layer** — All API calls isolated in `authService.js` and `chatService.js`; no `fetch()` in components
- **Loading & Error States** — "Signing in…", "Loading messages…", "Thinking…" bubble; per-scope error banners
- **Gemini Categories** — Schedule, General Info, Faculty & Lecturers, Grades & Averages, Registration & Fees, Technical Issue
- **Responsive Layout** — Persistent 260px sidebar (left) + scrollable chat area (right); 768px/480px breakpoints

---

## Project Structure

```
smart-campus-assistant/
├── docker-compose.yml
├── .env                        # secrets (gitignored)
├── backend/
│   ├── Dockerfile
│   ├── main.py                 # FastAPI app — all endpoints
│   ├── auth_utils.py           # JWT helpers
│   ├── requirements.txt
│   └── DB/
│       ├── models.py           # SQLAlchemy models
│       └── seed.py             # DB seed script
└── frontend/
    ├── Dockerfile              # node:20 build → nginx:alpine
    ├── nginx.conf              # SPA fallback routing
    ├── .env                    # VITE_API_URL for local dev
    ├── .env.production         # VITE_API_URL for Docker build
    └── src/
        ├── App.jsx             # Routes + ProtectedRoute
        ├── main.jsx            # Providers: AuthProvider → ChatProvider
        ├── context/
        │   ├── AuthContext.jsx
        │   └── ChatContext.jsx
        ├── components/
        │   ├── Layout/
        │   │   └── Sidebar.jsx
        │   └── Chat/
        │       ├── MessageList.jsx
        │       ├── MessageBubble.jsx
        │       └── MessageInput.jsx
        ├── pages/
        │   ├── Home.jsx / Home.css
        │   ├── Login.jsx / Login.css
        │   └── Register.jsx / Register.css
        └── services/
            ├── authService.js  # POST /login, POST /register
            └── chatService.js  # /conversations, /ask, mapMessage()
```

---

## Backend API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/register` | No | Create new user account |
| `POST` | `/login` | No | Returns JWT access token |
| `POST` | `/ask` | JWT | Send message, get AI response |
| `GET` | `/history` | JWT | All messages for current user |
| `GET` | `/conversations` | JWT | List conversations |
| `POST` | `/conversations` | JWT | Create new conversation |
| `GET` | `/conversations/{id}` | JWT | Get conversation + messages |
| `DELETE` | `/conversations/{id}` | JWT | Delete conversation |

---

## Environment Variables

Create a `.env` file in the **project root** (gitignored):

```env
GEMINI_API_KEY=your_actual_api_key_here
SECRET_KEY=your_jwt_secret_key_here
```

---

## Running with Docker (Recommended)

Ensure Docker Desktop is running.

```bash
git clone https://github.com/AvivBE-IS/smart-campus-assistant.git
cd smart-campus-assistant

# Add your .env file with GEMINI_API_KEY and SECRET_KEY

docker compose up --build
```

- **Frontend:** http://localhost:3001
- **Backend:** http://localhost:8001
- **Swagger docs:** http://localhost:8001/docs

---

## Local Development (without Docker)

**Backend:**

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev                    # runs at http://localhost:5173
```

> Local dev uses `VITE_API_URL=http://localhost:8000` from `frontend/.env`.

---

## Database Seeding

To reset and reseed the SQLite database with English sample data:

```bash
cd backend
python DB/seed.py
```

Seed creates: 10 departments, 10 lecturers, 10 students, 10 courses, 10 groups, 12 enrollments.

---

## Testing

```bash
cd backend
pytest -v
```

---

## Key Dependencies

| Package | Version | Why pinned |
|---|---|---|
| `bcrypt` | `4.0.1` | v5.x breaks `passlib 1.7.4` |
| `google-genai` | latest | Gemini 2.5 Flash support |
| React | `19` | |
| Vite | `8` | |

