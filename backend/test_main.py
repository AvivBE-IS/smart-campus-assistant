import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app, get_db

# Initialize the TestClient
client = TestClient(app)

# Dependency override to mock the database session
def override_get_db():
    mock_db = MagicMock()
    # Mocking query.all() to return an empty list for simplicity
    mock_db.query.return_value.all.return_value = []
    return mock_db

# Apply the override
app.dependency_overrides[get_db] = override_get_db

@patch("main.genai.Client")
def test_ask_question_success(mock_genai_client):
    """
    Tests the /ask endpoint to ensure it correctly parses a JSON response from Gemini.
    """
    # 1. Setup the Mock objects
    mock_model = MagicMock()
    mock_response = MagicMock()
    
    # Simulate the JSON structure your prompt expects from the AI
    fake_ai_json = json.dumps({
        "category": "General Information",
        "answer": "The test passed successfully!\n• Python\n• Calculus"
    })
    
    mock_response.text = fake_ai_json
    
    # Mocking the client.models.generate_content call chain
    instance = mock_genai_client.return_value
    instance.models.generate_content.return_value = mock_response

    # 2. Execute the POST request
    response = client.post("/ask", json={"message": "What courses are available?"})

    # 3. Assertions
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "category" in data
    assert data["category"] == "General Information"
    assert "The test passed successfully" in data["response"]

@patch("main.genai.Client")
def test_ask_question_error_handling(mock_genai_client):
    """
    Tests the system's resilience when the Gemini API returns an error.
    """
    # Simulate an API failure (e.g., connection error or invalid key)
    instance = mock_genai_client.return_value
    instance.models.generate_content.side_effect = Exception("API Connection Failed")

    response = client.post("/ask", json={"message": "Hello"})

    # The system should catch the error and return a friendly Hebrew error message
    assert response.status_code == 200
    assert response.json()["category"] == "בעיה טכנית"