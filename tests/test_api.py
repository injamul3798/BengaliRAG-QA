import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from pathlib import Path
import json

client = TestClient(app)

def test_query_endpoint():
    """Test the query endpoint with both English and Bengali queries."""
    # Test Bengali query
    response = client.post(
        "/api/query",
        json={
            "query": "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?",
            "chat_history": []
        }
    )
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "evaluation" in response.json()

    # Test English query
    response = client.post(
        "/api/query",
        json={
            "query": "Who is described as a gentleman in Anupam's language?",
            "chat_history": []
        }
    )
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "evaluation" in response.json()

def test_document_ingestion():
    """Test document ingestion endpoint."""
    # Create a sample PDF file for testing
    test_file_path = Path("tests/data/test.pdf")
    
    with open(test_file_path, "rb") as f:
        response = client.post(
            "/api/ingest",
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Document ingested successfully"

def test_system_evaluation():
    """Test system evaluation endpoint."""
    response = client.get("/api/evaluate")
    assert response.status_code == 200
    assert "metrics" in response.json()
    assert response.json()["metrics"]["status"] == "operational"
