
markdown
# Smart Campus Assistant

An AI-powered web application built to instantly classify and answer student queries regarding campus information. Developed as a capstone evaluation project for **Elad Systems**.

---

## Architecture Overview

The system is built using a modern full-stack and highly available architecture:

* **Frontend:** A lightweight, responsive web interface where students can submit natural language questions.
* **Backend:** A RESTful API built with **Python & FastAPI** that handles incoming requests, manages routing, and retrieves context from a local **SQLite** database.
* **AI Integration:** The backend communicates with the **Google Gemini API** to classify the user's intent into predefined categories (*Schedule, General Info, Technical Issue*) and generates JSON-formatted responses.
* **Resilience (Fallback):** Implemented an automatic fallback mechanism routing queries from **Gemini 3 Flash** to **Gemini 2.5 Flash** during server overloads (HTTP 503/429) to ensure an 8-second SLA.

---

## Infrastructure & DevOps (CI/CD)

* **Containerization:** The entire application is dockerized using a multi-stage Dockerfile and orchestrated via `docker-compose.yml` for isolated and secure deployment.
* **Continuous Integration:** A **GitHub Actions** pipeline is configured to automatically run code linting (**Flake8**) and Unit Tests (**Pytest**) on every push to the main branch.

---

## Environment Variables

This project requires certain environment variables to run safely without hardcoding secrets. 
Create a `.env` file in the root directory (this file is ignored by git) and add the following:

```env
GEMINI_API_KEY=your_actual_api_key_here
PORT=8000

```

---

## Installation & Running

The easiest and recommended way to run the system is via Docker.

### Method 1: Running with Docker (Recommended)

Ensure Docker Desktop is installed and running.

1. **Clone the repository:**
```bash
git clone [https://github.com/yourusername/smart-campus-assistant.git](https://github.com/yourusername/smart-campus-assistant.git)
cd smart-campus-assistant

```


2. **Build and run the containers:**
```bash
docker compose up --build

```


3. **Access the application:**
* **Frontend:** `http://localhost:8000` (or your defined port)
* **API Docs (Swagger):** `http://localhost:8000/docs`



### Method 2: Local Development (Manual Setup)

If you prefer running without Docker:

**Backend Setup:**

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload

```

**Frontend Setup:**
Open the `index.html` file in your browser, or serve it using a simple local server.

---

## Testing

The AI service includes automated unit tests to verify API categorization and the fallback logic mechanism using mocks.

To run the tests locally:

```bash
cd backend
pytest -v

```

> **Note:** A screenshot of the passing test execution and the GitHub Actions green pipeline is included in the `/docs` folder as required.



