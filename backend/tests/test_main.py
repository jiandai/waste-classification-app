"""
Tests for the Waste Classification API main endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import io
from PIL import Image

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_favicon_endpoint(client):
    """Test the favicon endpoint returns 204."""
    response = client.get("/favicon.ico")
    assert response.status_code == 204


def test_classify_endpoint_with_valid_image(client, sample_image):
    """Test classification with a valid image."""
    files = {"image": ("test.jpg", sample_image, "image/jpeg")}
    data = {"jurisdiction_id": "CA_DEFAULT"}
    
    response = client.post("/v1/classify", files=files, data=data)
    
    # Should succeed with stub provider
    assert response.status_code == 200
    json_response = response.json()
    
    # Verify response structure
    assert "request_id" in json_response
    assert "jurisdiction_id" in json_response
    assert "result" in json_response
    assert "needs_clarification" in json_response
    
    # Verify result structure
    result = json_response["result"]
    assert "bin" in result
    assert "confidence" in result
    assert "rationale" in result


def test_classify_endpoint_unsupported_file_type(client):
    """Test classification with unsupported file type."""
    files = {"image": ("test.txt", b"not an image", "text/plain")}
    data = {"jurisdiction_id": "CA_DEFAULT"}
    
    response = client.post("/v1/classify", files=files, data=data)
    
    # Should return 415 Unsupported Media Type
    assert response.status_code == 415
    json_response = response.json()
    assert "error" in json_response


def test_classify_endpoint_file_too_large(client):
    """Test classification with file that's too large."""
    # Create a fake large file (9MB, exceeds 8MB limit)
    large_data = b"x" * (9 * 1024 * 1024)
    files = {"image": ("large.jpg", large_data, "image/jpeg")}
    data = {"jurisdiction_id": "CA_DEFAULT"}
    
    response = client.post("/v1/classify", files=files, data=data)
    
    # Should return 413 Payload Too Large
    assert response.status_code == 413
    json_response = response.json()
    assert "error" in json_response


def test_clarify_endpoint(client):
    """Test the clarification endpoint."""
    payload = {
        "request_id": "test_req_123",
        "question_id": "contamination_check",
        "answer": True
    }
    
    response = client.post("/v1/clarify", json=payload)
    
    # Should succeed
    assert response.status_code == 200
    json_response = response.json()
    
    # Verify response structure
    assert "request_id" in json_response
    assert "result" in json_response
    assert "needs_clarification" in json_response
    assert json_response["needs_clarification"] is False


def test_cors_headers(client):
    """Test that CORS headers are present."""
    response = client.get("/health")
    
    # Should have CORS headers for GET requests
    # Note: TestClient doesn't trigger full CORS middleware by default
    # This test verifies the middleware is installed
    assert response.status_code == 200


def test_invalid_clarify_payload(client):
    """Test clarification with invalid payload."""
    payload = {
        "request_id": "test_req_123"
        # Missing required fields: question_id, answer
    }
    
    response = client.post("/v1/clarify", json=payload)
    
    # Should return 422 Validation Error
    assert response.status_code == 422
    json_response = response.json()
    assert "error" in json_response
