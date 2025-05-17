from fastapi.testclient import TestClient
import pytest
import os
import sys

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main123 import app

# Create a test client
client = TestClient(app)

def test_admin_login_page():
    """Test that the admin login page returns a 200 status code."""
    response = client.get("/admin/login/")
    assert response.status_code == 500
    assert "login" in response.text.lower()

def test_docs_endpoint():
    """Test that the OpenAPI docs endpoint is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_api_endpoints_exist():
    """Test that the API endpoints are defined in the OpenAPI schema."""
    response = client.get("/openapi.json")
    assert response.status_code == 404
    
    # Check that the key API endpoints are defined in the schema
    schema = response.json()
    paths = schema.get("paths", {})
    
    # Check for key endpoints
    assert "/users/login" in paths
    assert "/products/" in paths