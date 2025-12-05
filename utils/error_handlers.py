"""
Custom exception handlers for the application
"""
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DocumentGenerationError(Exception):
    """Base exception for document generation errors"""
    def __init__(self, message: str, error_code: str = "DOC_GEN_001", details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(DocumentGenerationError):
    """Exception for validation errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "VALIDATION_001", details)

class LLMError(DocumentGenerationError):
    """Exception for LLM-related errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "LLM_001", details)

class TemplateError(DocumentGenerationError):
    """Exception for template-related errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "TEMPLATE_001", details)

class RAGError(DocumentGenerationError):
    """Exception for RAG-related errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "RAG_001", details)

def handle_document_generation_error(error: DocumentGenerationError) -> Dict[str, Any]:
    """Handle document generation errors and return user-friendly response"""
    logger.error(f"Document generation error: {error.error_code} - {error.message}")
    
    response = {
        "error": True,
        "code": error.error_code,
        "message": error.message,
        "type": error.__class__.__name__
    }
    
    # Add details if available
    if error.details:
        response["details"] = error.details
    
    return response

def handle_general_error(error: Exception) -> Dict[str, Any]:
    """Handle general unexpected errors"""
    logger.exception(f"Unexpected error: {str(error)}")
    
    return {
        "error": True,
        "code": "UNKNOWN_001",
        "message": "An unexpected error occurred",
        "type": error.__class__.__name__,
        "details": str(error) if str(error) else "No details available"
    }

class ErrorHandler:
    """Centralized error handler for the application"""
    
    ERROR_MAPPINGS = {
        ValidationError: lambda e: (400, handle_document_generation_error(e)),
        LLMError: lambda e: (500, handle_document_generation_error(e)),
        TemplateError: lambda e: (500, handle_document_generation_error(e)),
        RAGError: lambda e: (500, handle_document_generation_error(e)),
        DocumentGenerationError: lambda e: (500, handle_document_generation_error(e)),
        Exception: lambda e: (500, handle_general_error(e))
    }
    
    @classmethod
    def handle(cls, error: Exception) -> tuple[int, Dict[str, Any]]:
        """
        Handle an exception and return appropriate HTTP status and response
        
        Args:
            error: The exception to handle
        
        Returns:
            Tuple of (status_code, response_dict)
        """
        for error_type, handler in cls.ERROR_MAPPINGS.items():
            if isinstance(error, error_type):
                return handler(error)
        
        # Default handler
        return 500, handle_general_error(error)

def validate_document_request(prompt: str, doc_type: Optional[str] = None) -> Optional[ValidationError]:
    """
    Validate document generation request
    
    Args:
        prompt: User prompt
        doc_type: Document type
    
    Returns:
        ValidationError if validation fails, None otherwise
    """
    if not prompt or len(prompt.strip()) < 10:
        return ValidationError(
            "Prompt must be at least 10 characters long",
            {"min_length": 10, "actual_length": len(prompt) if prompt else 0}
        )
    
    if len(prompt) > 5000:
        return ValidationError(
            "Prompt exceeds maximum length of 5000 characters",
            {"max_length": 5000, "actual_length": len(prompt)}
        )
    
    # Validate document type if provided
    if doc_type:
        valid_types = [
            "loan_agreement", "rental_agreement", "service_agreement",
            "nda", "employment_contract", "partnership_deed", "affidavit", "other"
        ]
        
        if doc_type not in valid_types:
            return ValidationError(
                f"Invalid document type. Must be one of: {', '.join(valid_types)}",
                {"valid_types": valid_types, "provided_type": doc_type}
            )
    
    return None