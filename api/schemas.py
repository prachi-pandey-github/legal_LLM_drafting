"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

class DocumentType(str, Enum):
    """Supported document types"""
    LOAN_AGREEMENT = "loan_agreement"
    RENTAL_AGREEMENT = "rental_agreement"
    SERVICE_AGREEMENT = "service_agreement"
    NDA = "nda"
    EMPLOYMENT_CONTRACT = "employment_contract"
    PARTNERSHIP_DEED = "partnership_deed"
    AFFIDAVIT = "affidavit"
    OTHER = "other"

class DocumentRequest(BaseModel):
    """Request model for document generation"""
    prompt: str = Field(
        ...,
        description="Natural language description of the document needed",
        min_length=10,
        max_length=5000,
        example="Draft a Loan Agreement for ₹5,00,000 between Rohit Gupta (Lender) and Akash Mehta (Borrower), tenure 12 months, interest 10 percent, monthly repayment."
    )
    
    document_type: Optional[DocumentType] = Field(
        None,
        description="Specific type of document to generate"
    )
    
    variables: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Structured variables for document generation"
    )
    
    format_preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Formatting preferences for the document"
    )
    
    jurisdiction: Optional[str] = Field(
        "IN",
        description="Legal jurisdiction (e.g., IN, US, UK)",
        max_length=10
    )
    
    @validator('prompt')
    def validate_prompt_length(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Prompt must be at least 10 characters long')
        return v.strip()
    
    @validator('variables')
    def validate_variables(cls, v):
        # Remove any None values
        return {k: v for k, v in v.items() if v is not None}

class DocumentResponse(BaseModel):
    """Response model for document generation"""
    success: bool = Field(..., description="Whether generation was successful")
    message: str = Field(..., description="Status message")
    document_id: str = Field(..., description="Unique identifier for the document")
    filename: str = Field(..., description="Name of the generated file")
    document_type: Optional[str] = Field(None, description="Type of document generated")
    sections_count: int = Field(0, description="Number of sections in the document")
    download_url: Optional[str] = Field(None, description="URL to download the document")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentTypeInfo(BaseModel):
    """Information about a supported document type"""
    type_id: str = Field(..., description="Identifier for the document type")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Brief description")
    required_fields: List[str] = Field(..., description="Required fields for this document type")
    example_prompt: Optional[str] = Field(None, description="Example prompt")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: bool = True
    message: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationResult(BaseModel):
    """Validation result for a prompt"""
    valid: bool
    message: str
    document_type: Optional[str] = None
    suggestions: Optional[List[str]] = None
    missing_fields: Optional[List[str]] = None