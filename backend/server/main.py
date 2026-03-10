import os
import sys
import pathlib
import uvicorn
import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# ---------------------------------------------------------
# Path Handling & DB Imports
# ---------------------------------------------------------
current_dir = pathlib.Path(__file__).parent.resolve()
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

try:
    from DB.models import Course, DATABASE_URL 
except ImportError as e:
    print(f"❌ Error importing DB models: {e}")

# Load environment variables
load_dotenv()

app = FastAPI(title="Smart Campus Assistant - Task 11 Integrated")

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

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

# FIXED: Changed from /chat to /ask to match Task 9 and Frontend calls
@app.post("/ask")
async def ask_question(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Print user input to console (as requested)
        print(f"User input received: {request.message}")

        # 1. Fetch relevant data from the DB
        courses = db.query(Course).all()
        db_context = "Current campus database data:\n"
        for course in courses:
            db_context += f"- Course: {course.name}, Credits: {course.credits}\n"
        
        # 2. Advanced Prompt Engineering (Classification + Context)
        final_prompt = f"""
        You are a Smart Campus Assistant. 
        Analyze the user's question and fulfill these two requirements:
        
        Requirement 1: Categorize the question into exactly one: 
        "לוח זמנים", "מידע כללי", or "בעיה טכנית".
        
        Requirement 2: Answer in Hebrew based ONLY on the context below. 
        If info is missing, say you don't know.

        IMPORTANT: Return the output ONLY as a valid JSON object (no markdown) with keys:
        {{
            "category": "category_name",
            "answer": "your_hebrew_answer"
        }}
        
        Database Context:
        {db_context}
        
        User Question: {request.message}
        """

        # 3. Primary API call (Gemini 3 Flash)
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                contents=final_prompt
            )
        except Exception as api_err:
            # Task 13: Fallback mechanism if primary model fails
            print(f"Fallback triggered: {api_err}")
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=final_prompt
            )

        # 4. Parse JSON result
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean_text)
        
        print(f"Detected Category: {parsed['category']}")
        
        # 5. Return JSON to frontend
        return {
            "response": parsed["answer"],
            "category": parsed["category"]
        }
        
    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            "response": "מצטער, חלה שגיאה בעיבוד הבקשה. נסה שוב מאוחר יותר.",
            "category": "בעיה טכנית"
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)