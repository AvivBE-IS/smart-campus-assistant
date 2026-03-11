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
    # Importing all models to give Gemini full campus context
    from DB.models import Course, Lecturer, Group, Enrollment, Student, DATABASE_URL 
except ImportError as e:
    print(f"❌ Error importing DB models: {e}")

# Load environment variables (Make sure your .env file has GEMINI_API_KEY)
load_dotenv()

app = FastAPI(title="Smart Campus Assistant - Full DB Integration")

# Allow CORS for the frontend (Crucial for Live Server on port 5500)
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

@app.post("/ask")
async def ask_question(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main endpoint that connects the Database context with Gemini's reasoning.
    It categorizes the question and returns a formatted Hebrew response.
    """
    try:
        print(f"User input received: {request.message}")

        # 1. Fetching comprehensive data from all relevant tables
        courses = db.query(Course).all()
        lecturers = db.query(Lecturer).all()
        groups = db.query(Group).all()
        
        # Formatting data into a structured context for the LLM
        db_context = "### CAMPUS DATABASE CONTEXT ###\n"
        
        db_context += "COURSES:\n"
        for c in courses:
            db_context += f"- {c.name}: {c.credits} credits, Extra Fee: {c.extra_fee}\n"
            
        db_context += "\nLECTURERS:\n"
        for l in lecturers:
            db_context += f"- {l.rank} {l.first_name} {l.last_name}, Office: {l.office_location}\n"
            
        db_context += "\nSCHEDULE & EXAMS:\n"
        for g in groups:
            # Finding course name for the group
            course_name = next((c.name for c in courses if c.id == g.course_id), "Unknown")
            db_context += f"- {course_name} (Group {g.group_number}): {g.day_of_week}, Exam A: {g.exam_date_a}\n"


        final_prompt = f"""
ענה על שאלת המשתמש הבאה בהתבסס על המידע מהדאטה-בייס:
{db_context}

השאלה: {request.message}
"""
        # 2. Advanced Prompt Engineering (Classification + Formatting + RTL)
        final_prompt = f"""
ROLE: You are the official BGU Smart Campus Assistant. You are professional, helpful, and concise.

STRICT RULES:
1. Use ONLY the provided Database Context. If info is missing, say: "מצטער, המידע הזה לא קיים במערכת כרגע."
2. Never mention that you are an AI or that you are looking at a database.
3. If the answer contains more than 2 items, you MUST format it as a bulleted list using the character '•'.
4. Each bullet point MUST start on a new line using double backslash n (\\n).

CATEGORIZATION LOGIC:
- "לוח זמנים": Exam dates, class days, schedules.
- "מידע כללי": Course credits, department names.
- "סגל ומרצים": Names, ranks, office locations.
- "ציונים וממוצעים": Grades, individual student performance.
- "רישום ועלויות": Extra fees, registration status.
- "בעיה טכנית": Login issues, site bugs, or general help.

EXAMPLES:
User: "אילו קורסים יש?"
Output: {{"category": "מידע כללי", "answer": "להלן הקורסים הזמינים:\\n• פייתון\\n• חדו''א א"}}

DATABASE CONTEXT:
{db_context}

USER QUESTION: {request.message}

FINAL INSTRUCTION: Return ONLY a valid JSON object. No markdown. No explanations.
"""
        # 3. Call Gemini (Primary: 3 Flash Preview)
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                contents=final_prompt
            )
        except Exception as api_err:
            # Task 13: Fallback mechanism
            print(f"Primary model failed, triggering fallback: {api_err}")
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=final_prompt
            )

        # 4. Clean and Parse JSON
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean_text)
        
        print(f"Detected Category: {parsed['category']}")
        
        # 5. Response to Frontend
        return {
            "response": parsed["answer"],
            "category": parsed["category"]
        }
        
    except Exception as e:
        print(f"Critical Error: {e}")
        return {
            "response": "מצטער, חלה שגיאה במערכת. צוות התמיכה עודכן.",
            "category": "בעיה טכנית"
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)