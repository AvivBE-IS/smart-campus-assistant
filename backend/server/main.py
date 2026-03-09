import sys
import pathlib
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from google import genai

# ---------------------------------------------------------
# Path Handling
# ---------------------------------------------------------
# Ensure we can import from backend/database
current_dir = pathlib.Path(__file__).parent.resolve()
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

try:
    from DB.models import Base, Student, Course, DATABASE_URL
except ImportError as e:
    print(f"Error importing models: {e}")
    sys.exit(1)

# ---------------------------------------------------------
# Software Lifecycle Integration
# ---------------------------------------------------------
# Infrastructure & Deployment: This server acts as the bridge between the persistent data layer (SQLite DB)
# and the client-facing application. By managing database connections efficiently via session pooling, 
# it ensures data integrity and stability.
#
# System Development: It exposes a RESTful API that decouples the frontend from backend logic, 
# allowing parallel development. The 'get_db' dependency ensures clean resource management.
#
# System Analysis: The lightweight FastAPI framework and optimized SQLAlchemy queries ensure low latency,
# meeting the non-functional requirement of a response time under 8 seconds for student queries.

app = FastAPI(title="Smart Campus Assistant")

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
# Endpoints
# ---------------------------------------------------------

@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Campus Assistant API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Execute a simple query to check connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/test-data")
def get_test_data(db: Session = Depends(get_db)):
    return {
        "student_count": db.query(Student).count(),
        "course_count": db.query(Course).count(),
        "message": "Connection verified successfully"
    }



@app.post("/chat")
async def chat_with_db(question: str):
    # This is your 'small DB' data for the POC
    mock_db_data = [{"id": 1, "item": "Laptop", "price": 1200}, {"id": 2, "item": "Mouse", "price": 25}]
    
    answer = get_ai_response(question, mock_db_data)
    return {"gemini_says": answer}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)