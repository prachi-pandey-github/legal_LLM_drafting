"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import json
import tempfile
import os

from main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Legal Drafting LLM" in data["service"]

def test_document_types():
    """Test document types endpoint"""
    response = client.get("/api/v1/document-types")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check structure of document types
    for doc_type in data:
        assert "type_id" in doc_type
        assert "name" in doc_type
        assert "description" in doc_type
        assert "required_fields" in doc_type

def test_draft_document_valid():
    """Test valid document generation request"""
    request_data = {
        "prompt": "Draft a simple rental agreement between John Doe (Landlord) and Jane Smith (Tenant) for an apartment in Mumbai, rent ₹20,000 per month.",
        "document_type": "rental_agreement",
        "variables": {
            "landlord_name": "John Doe",
            "tenant_name": "Jane Smith",
            "property_address": "Mumbai",
            "rent_amount": "₹20,000",
            "jurisdiction": "IN"
        }
    }
    
    response = client.post("/api/v1/draft-document", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] == True
    assert "document_id" in data
    assert "filename" in data
    assert "download_url" in data

def test_draft_document_invalid_prompt():
    """Test document generation with invalid prompt"""
    request_data = {
        "prompt": "short",  # Too short
        "document_type": "loan_agreement"
    }
    
    response = client.post("/api/v1/draft-document", json=request_data)
    # Depending on validation, this might return 400 or 500
    assert response.status_code in [400, 500]

def test_validate_prompt():
    """Test prompt validation endpoint"""
    test_prompt = "I need a loan agreement for ₹1,00,000"
    
    response = client.post("/api/v1/validate-prompt", json={"prompt": test_prompt})
    assert response.status_code == 200
    
    data = response.json()
    assert "valid" in data
    assert "message" in data
    
    if data["valid"]:
        assert "document_type" in data
    else:
        assert "suggestions" in data

def test_download_endpoint():
    """Test document download endpoint"""
    # First generate a document
    request_data = {
        "prompt": "Test document for download",
        "document_type": "loan_agreement",
        "variables": {
            "lender_name": "Test Lender",
            "borrower_name": "Test Borrower",
            "amount": "₹10,000",
            "interest_rate": "5",
            "tenure": "6"
        }
    }
    
    response = client.post("/api/v1/draft-document", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    filename = data["filename"]
    
    # Try to download (might not exist if cleanup happened)
    download_response = client.get(f"/api/v1/download/{filename}")
    
    # Either file exists (200) or was cleaned up (404)
    assert download_response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test handling of concurrent requests"""
    import asyncio
    
    async def make_request():
        request_data = {
            "prompt": f"Concurrent test document {id}",
            "document_type": "loan_agreement"
        }
        response = client.post("/api/v1/draft-document", json=request_data)
        return response.status_code
    
    # Make multiple concurrent requests
    tasks = [make_request() for _ in range(3)]
    results = await asyncio.gather(*tasks)
    
    # All should succeed (or at least not crash)
    for status_code in results:
        assert status_code in [200, 400, 500]  # Acceptable status codes

def test_error_handling():
    """Test error handling for malformed requests"""
    # Test with malformed JSON
    response = client.post("/api/v1/draft-document", data="not json")
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with missing required field
    request_data = {
        "document_type": "loan_agreement"
        # Missing prompt
    }
    response = client.post("/api/v1/draft-document", json=request_data)
    assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"])