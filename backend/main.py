import os
import sys
import asyncio
import pathlib
import uvicorn
import json
from typing import List, Optional
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from auth_utils import hash_password, verify_password, create_access_token, get_current_user
from DB.models import User, Message, Conversation

# ---------------------------------------------------------
# Path Handling & DB Imports
# ---------------------------------------------------------
current_dir = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(current_dir))

try:
    # Importing all models to give Gemini full campus context
    from DB.models import Base, Course, Lecturer, Group, Enrollment, Student, DATABASE_URL 
except ImportError as e:
    print(f"Error importing DB models: {e}")

# Load environment variables
load_dotenv()

app = FastAPI(title="Smart Campus Assistant - Full DB Integration")

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Database Setup
# ---------------------------------------------------------
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# Data Models
# ---------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ConversationCreate(BaseModel):
    title: Optional[str] = None

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.get("/")
def root():
    return {"status": "Smart Campus Assistant API is running", "docs": "/docs"}

@app.post("/ask")
async def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Main endpoint that connects the Database context with Gemini's reasoning.
    It categorizes the question and returns a structured English response.
    """
    # Auto-create a conversation if none is provided
    conversation_id = request.conversation_id
    if not conversation_id:
        conv = Conversation(user_id=user_id, title=request.message[:40])
        db.add(conv)
        db.flush()
        conversation_id = conv.id

    # 1. Save the user message first
    user_msg = Message(
        user_id=user_id,
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    db.flush()

    try:
        # 2. Fetch the last 10 messages in this conversation for context
        recent_messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.desc()).limit(10).all()
        
        recent_messages.reverse()

        # Format history for the Gemini API
        gemini_history = []
        for msg in recent_messages:
            gemini_role = "model" if msg.role == "assistant" else "user"
            gemini_history.append({
                "role": gemini_role,
                "parts": [{"text": msg.content}]
            })

        # 3. Fetching comprehensive data from all relevant tables
        courses = db.query(Course).all()
        lecturers = db.query(Lecturer).all()
        groups = db.query(Group).all()

        db_context = "### CAMPUS DATABASE CONTEXT ###\n"

        db_context += "COURSES:\n"
        for c in courses:
            db_context += f"- {c.name}: {c.credits} credits, Extra Fee: {c.extra_fee}\n"

        db_context += "\nLECTURERS:\n"
        for l in lecturers:
            db_context += f"- {l.rank} {l.first_name} {l.last_name}, Office: {l.office_location}\n"

        db_context += "\nSCHEDULE & EXAMS:\n"
        for g in groups:
            course_name = next((c.name for c in courses if c.id == g.course_id), "Unknown")
            db_context += f"- {course_name} (Group {g.group_number}): {g.day_of_week}, Exam A: {g.exam_date_a}\n"

        # 4. Advanced Prompt Engineering
        final_prompt = f"""
ROLE: You are the official BGU Smart Campus Assistant. You are professional, helpful, and concise.

STRICT RULES:
1. Use ONLY the provided Database Context. If info is missing, say: "Sorry, this information is not currently available in the system."
2. Never mention that you are an AI or that you are looking at a database.
3. If the answer contains more than 2 items, you MUST format it as a bulleted list using the character '•'.
4. Each bullet point MUST start on a new line using double backslash n (\\n).

CATEGORIZATION LOGIC:
- "Schedule": Exam dates, class days, schedules.
- "General Info": Course credits, department names.
- "Faculty & Lecturers": Names, ranks, office locations.
- "Grades & Averages": Grades, individual student performance.
- "Registration & Fees": Extra fees, registration status.
- "Technical Issue": Login issues, site bugs, or general help.

EXAMPLES:
User: "What courses are available?"
Output: {{"category": "General Info", "answer": "The available courses are:\\n• Python\\n• Calculus A"}}

DATABASE CONTEXT:
{db_context}

USER QUESTION: {request.message}

FINAL INSTRUCTION: Return ONLY a valid JSON object. No markdown. No explanations.
"""
        # Append the structured prompt as the latest user message
        gemini_history.append({
            "role": "user",
            "parts": [{"text": final_prompt}]
        })

        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)

        def call_gemini():
            try:
                return client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=gemini_history,
                )
            except Exception as api_err:
                print(f"Primary model failed, triggering fallback: {api_err}")
                return client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=gemini_history,
                )

        response = await asyncio.to_thread(call_gemini)

        # 5. Parse AI response
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean_text)
        ai_content = parsed["answer"]

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

    # 6. Save Gemini response and commit both records together
    ai_msg = Message(
        user_id=user_id,
        conversation_id=conversation_id,
        role="assistant",
        content=ai_content,
    )
    db.add(ai_msg)
    db.commit()

    return {
        "response": ai_content,
        "category": parsed.get("category", "General Info"),
        "conversation_id": conversation_id,
        "user": user_id,
    }

@app.get("/history")
async def get_chat_history(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
    conversation_id: Optional[int] = None,
):
    """
    Fetches chat messages. If conversation_id is provided, returns messages
    for that conversation only; otherwise returns all messages for the user.
    """
    query = db.query(Message).filter(Message.user_id == current_user_id)
    if conversation_id is not None:
        query = query.filter(Message.conversation_id == conversation_id)
    messages = query.order_by(Message.timestamp.asc()).all()

    history: List[dict] = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
        }
        for msg in messages
    ]

    return {"history": history}

# ---------------------------------------------------------
# Conversation Endpoints
# ---------------------------------------------------------

@app.get("/conversations")
async def list_conversations(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    return {
        "conversations": [
            {"id": c.id, "title": c.title or f"Chat {c.id}", "created_at": c.created_at.isoformat()}
            for c in convs
        ]
    }

@app.post("/conversations")
async def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    conv = Conversation(user_id=user_id, title=data.title or "New Chat")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"conversation_id": conv.id, "title": conv.title, "created_at": conv.created_at.isoformat()}

@app.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.asc())
        .all()
    )
    return {
        "id": conv.id,
        "title": conv.title or f"Chat {conv.id}",
        "messages": [
            {"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()}
            for m in messages
        ],
    }

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted"}

@app.post("/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        return {"error": "User already exists"}

    hashed = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed 
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"user_id": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)