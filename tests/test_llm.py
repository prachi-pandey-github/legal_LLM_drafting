"""
Tests for LLM components
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock

from llm.model_handler import LLMHandler
from llm.rag_pipeline import RAGPipeline
from llm.prompt_templates import generate_prompt

def test_prompt_generation():
    """Test prompt template generation"""
    doc_type = "loan_agreement"
    variables = {
        "lender_name": "John Doe",
        "borrower_name": "Jane Smith",
        "amount": "₹1,00,000",
        "interest_rate": "10",
        "tenure": "12"
    }
    
    system_prompt, user_prompt = generate_prompt(doc_type, variables, "Test prompt")
    
    assert isinstance(system_prompt, str)
    assert isinstance(user_prompt, str)
    assert "John Doe" in user_prompt
    assert "₹1,00,000" in user_prompt
    assert "loan agreement" in system_prompt.lower()

def test_document_type_detection():
    """Test automatic document type detection"""
    handler = LLMHandler()
    
    test_cases = [
        ("I need a loan agreement", "loan_agreement"),
        ("Create a rental contract", "rental_agreement"),
        ("Draft an NDA for my business", "nda"),
        ("Generate a service agreement", "service_agreement"),
        ("Make an employment contract", "employment_contract"),
        ("Unknown document type", "other")
    ]
    
    for prompt, expected_type in test_cases:
        detected = handler.detect_document_type(prompt)
        assert detected == expected_type, f"Failed for: {prompt}"

@patch('llm.model_handler.genai')
def test_gemini_initialization(mock_genai):
    """Test Gemini client initialization"""
    # Mock the Gemini client
    mock_genai.configure = Mock()
    
    # Test with Gemini provider
    handler = LLMHandler()
    handler.llm_provider = "gemini"
    handler.initialize_gemini()
    
    assert handler.model is not None
    mock_genai.configure.assert_called_once()

def test_rag_pipeline_initialization():
    """Test RAG pipeline initialization"""
    with patch.object(RAGPipeline, 'initialize_embeddings'):
        with patch.object(RAGPipeline, 'initialize_vector_store'):
            pipeline = RAGPipeline()
            
            assert pipeline.embeddings is None  # Mocked
            assert pipeline.vector_store is None  # Mocked

@patch('llm.rag_pipeline.FAISS')
def test_vector_store_creation(mock_faiss):
    """Test vector store creation"""
    mock_vector_store = Mock()
    mock_faiss.from_documents.return_value = mock_vector_store
    
    pipeline = RAGPipeline()
    pipeline.embeddings = Mock()
    
    with patch.object(pipeline, 'load_legal_clauses', return_value=[]):
        with patch.object(pipeline, 'get_default_clauses', return_value=[]):
            pipeline.create_vector_store()
            
            mock_faiss.from_documents.assert_called_once()
            mock_vector_store.save_local.assert_called_once()

def test_clause_retrieval():
    """Test clause retrieval functionality"""
    pipeline = RAGPipeline()
    pipeline.vector_store = Mock()
    
    mock_docs = [
        Mock(page_content="Test clause 1", metadata={"document_type": "loan_agreement"}),
        Mock(page_content="Test clause 2", metadata={"document_type": "rental_agreement"})
    ]
    
    pipeline.vector_store.similarity_search.return_value = mock_docs
    
    results = pipeline.retrieve_relevant_clauses("loan agreement", "loan_agreement")
    
    assert len(results) == 1  # Only one matches document_type filter
    assert results[0]["metadata"]["document_type"] == "loan_agreement"

def test_clause_formatting():
    """Test formatting of clauses for prompt"""
    pipeline = RAGPipeline()
    
    test_clauses = [
        {
            "content": "Interest clause content",
            "metadata": {
                "clause_title": "Interest Rate",
                "document_type": "loan_agreement",
                "jurisdiction": "IN"
            }
        }
    ]
    
    formatted = pipeline.format_clauses_for_prompt(test_clauses)
    
    assert isinstance(formatted, str)
    assert "Interest Rate" in formatted
    assert "loan_agreement" in formatted
    assert "RELEVANT LEGAL CLAUSES" in formatted

def test_parse_llm_response_json():
    """Test parsing of LLM JSON response"""
    handler = LLMHandler()
    
    valid_json_response = json.dumps({
        "title": "Test Agreement",
        "sections": [
            {"type": "heading", "title": "Test", "content": "Content"}
        ],
        "parties": [{"name": "Test Party", "role": "Test"}]
    })
    
    parsed = handler.parse_llm_response(valid_json_response)
    
    assert parsed["title"] == "Test Agreement"
    assert len(parsed["sections"]) == 1
    assert len(parsed["parties"]) == 1

def test_parse_llm_response_text():
    """Test parsing of plain text LLM response"""
    handler = LLMHandler()
    
    text_response = """
    # Test Document
    
    This is a test document.
    
    ## Section 1
    
    Content of section 1.
    
    ## Section 2
    
    Content of section 2.
    """
    
    parsed = handler.parse_llm_response(text_response)
    
    assert parsed["title"] == "Legal Document"
    assert len(parsed["sections"]) > 0
    assert any(s["type"] == "heading" for s in parsed["sections"])

def test_fallback_document_generation():
    """Test fallback document generation when LLM fails"""
    handler = LLMHandler()
    
    fallback = handler.generate_fallback_document(
        "System prompt",
        "User prompt for loan agreement"
    )
    
    assert isinstance(fallback, dict)
    assert "title" in fallback
    assert "sections" in fallback
    assert "parties" in fallback
    
    # Should detect loan agreement from prompt
    assert "loan" in fallback["title"].lower()

@pytest.mark.asyncio
async def test_document_generation_flow():
    """Test complete document generation flow"""
    handler = LLMHandler()
    
    # Mock LLM call
    mock_response = json.dumps({
        "title": "Generated Document",
        "sections": [{"type": "clause", "title": "Test", "content": "Content"}],
        "parties": [{"name": "Party A", "role": "Role"}]
    })
    
    with patch.object(handler, 'call_llm', AsyncMock(return_value=mock_response)):
        with patch.object(handler.rag_pipeline, 'retrieve_relevant_clauses', return_value=[]):
            
            result = await handler.generate_document(
                prompt="Test prompt",
                doc_type="loan_agreement",
                variables={"jurisdiction": "IN"}
            )
            
            assert result["title"] == "Generated Document"
            assert "metadata" in result
            assert result["metadata"]["document_type"] == "loan_agreement"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])