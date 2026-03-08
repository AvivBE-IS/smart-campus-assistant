# Smart Campus Assistant

An AI-powered web application built to instantly classify and answer student queries regarding campus information. Developed as an evaluation project for Elad Systems.

## Architecture Overview

The system is built using a modern full-stack architecture:
* **Frontend:** A lightweight web interface where students can submit natural language questions.
* **Backend:** A RESTful API built with **Python & FastAPI** that handles incoming requests, manages routing, and implements error handling/fallback mechanisms.
* **AI Integration:** The backend communicates with the Gemini API to classify the user's intent into predefined categories (Schedule, General Info, Technical Issue) and generate accurate responses based on structured campus data.

## Prerequisites

Before you begin, ensure you have the following installed:
* Python 3.10+
* Node.js & npm (if applicable for your frontend)
* Git

## Environment Variables

This project requires certain environment variables to run safely without hardcoding secrets. 

Create a `.env` file in the root directory (this file is ignored by git) and add the following keys:

AI_API_KEY=your_api_key_here
PORT=8000

## Installation & Running

Follow these steps to get the development environment running locally:

**1. Clone the repository**
git clone https://github.com/yourusername/smart-campus-assistant.git
cd smart-campus-assistant

**2. Backend Setup**
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt

**3. Frontend Setup**
cd ../frontend
npm install

**4. Start the Application**
Open two terminal windows:

*Terminal 1 (Backend):*
cd backend
uvicorn main:app --reload

*Terminal 2 (Frontend):*
cd frontend
npm start

## Testing

The AI service includes automated unit tests to verify categorization and fallback logic. 

To run the tests:
cd backend
pytest -v

*(Note: A screenshot of the passing test execution is included in the `/docs` folder as required.)*
