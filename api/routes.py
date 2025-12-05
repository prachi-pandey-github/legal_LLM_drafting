"""
FastAPI routes for legal document drafting
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
import uuid
import logging

from api.schemas import DocumentRequest, DocumentResponse, DocumentTypeInfo
from llm.model_handler import LLMHandler
from document_generation.docx_builder import DocxBuilder
from utils.error_handlers import DocumentGenerationError, ValidationError
from utils.file_handlers import cleanup_temp_file
from config import Config

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize handlers
llm_handler = LLMHandler()

@router.post(
    "/draft-document",
    response_model=DocumentResponse,
    summary="Generate a legal document",
    description="Generate a complete legal document based on the provided prompt and parameters"
)
async def draft_document(
    request: DocumentRequest,
    background_tasks: BackgroundTasks
):
    """
    Main endpoint for document generation
    
    Args:
        request: Document request with prompt and parameters
        background_tasks: FastAPI background tasks for cleanup
    
    Returns:
        FileResponse: Generated .docx document
    """
    try:
        logger.info(f"Received document generation request: {request.document_type}")
        
        # Generate document content using LLM
        document_content = await llm_handler.generate_document(
            prompt=request.prompt,
            doc_type=request.document_type,
            variables=request.variables
        )
        
        # Build DOCX document
        doc_builder = DocxBuilder()
        
        # Add title
        doc_builder.add_title(document_content.get("title", "Legal Agreement"))
        
        # Add document metadata
        if "metadata" in document_content:
            doc_builder.add_paragraph(f"Document ID: {document_content['metadata'].get('document_id', str(uuid.uuid4()))}")
            doc_builder.add_paragraph(f"Generated on: {document_content['metadata'].get('generated_date', '')}")
            doc_builder.add_paragraph("")
        
        # Add sections
        for section in document_content.get("sections", []):
            section_type = section.get("type", "clause")
            if section_type == "heading":
                doc_builder.add_heading(section["content"], level=section.get("level", 1))
            elif section_type == "clause":
                doc_builder.add_clause(section.get("title", ""), section["content"])
            elif section_type == "paragraph":
                doc_builder.add_paragraph(section["content"])
            elif section_type == "list":
                doc_builder.add_list(section["items"], ordered=section.get("ordered", False))
        
        # Add parties and signature blocks
        if "parties" in document_content:
            doc_builder.add_heading("Signatures", level=1)
            for party in document_content["parties"]:
                doc_builder.add_signature_block(
                    party["name"],
                    party.get("role", ""),
                    party.get("address", ""),
                    party.get("contact", "")
                )
        
        # Add footer/notes
        if "footer" in document_content:
            doc_builder.add_paragraph("")
            doc_builder.add_paragraph(document_content["footer"], italic=True)
        
        # Save to temporary file
        filename = f"legal_document_{uuid.uuid4().hex[:8]}.docx"
        temp_file = doc_builder.save_to_temp(filename)
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_file, temp_file)
        
        # Prepare response
        response_data = DocumentResponse(
            success=True,
            message="Document generated successfully",
            document_id=str(uuid.uuid4()),
            filename=filename,
            document_type=request.document_type,
            sections_count=len(document_content.get("sections", [])),
            download_url=f"/api/v1/download/{filename}"  # This would need a download endpoint
        )
        
        # Return both JSON response and file
        return JSONResponse(
            content=response_data.dict(),
            headers={
                "X-Document-File": filename,
                "X-Document-ID": response_data.document_id
            }
        )
        
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except DocumentGenerationError as e:
        logger.error(f"Document generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/document-types", response_model=List[DocumentTypeInfo])
async def get_document_types():
    """
    Get list of supported document types
    """
    document_types = [
        DocumentTypeInfo(
            type_id="loan_agreement",
            name="Loan Agreement",
            description="Agreement between lender and borrower",
            required_fields=["lender", "borrower", "amount", "interest_rate", "tenure"]
        ),
        DocumentTypeInfo(
            type_id="rental_agreement",
            name="Rental Agreement",
            description="Agreement between landlord and tenant",
            required_fields=["landlord", "tenant", "property_address", "rent_amount", "security_deposit"]
        ),
        DocumentTypeInfo(
            type_id="service_agreement",
            name="Service Agreement",
            description="Agreement for provision of services",
            required_fields=["service_provider", "client", "services", "payment_terms"]
        ),
        DocumentTypeInfo(
            type_id="nda",
            name="Non-Disclosure Agreement",
            description="Confidentiality agreement",
            required_fields=["disclosing_party", "receiving_party", "confidential_info"]
        ),
        DocumentTypeInfo(
            type_id="employment_contract",
            name="Employment Contract",
            description="Contract between employer and employee",
            required_fields=["employer", "employee", "position", "salary", "start_date"]
        ),
        DocumentTypeInfo(
            type_id="partnership_deed",
            name="Partnership Deed",
            description="Agreement between business partners",
            required_fields=["partners", "business_name", "capital_contribution", "profit_sharing"]
        ),
        DocumentTypeInfo(
            type_id="affidavit",
            name="Affidavit",
            description="Sworn written statement",
            required_fields=["affiant", "statement", "purpose"]
        )
    ]
    return document_types

@router.get("/download/{filename}")
async def download_document(filename: str):
    """
    Download a generated document
    """
    import os
    filepath = os.path.join(Config.TEMP_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=filepath,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )

@router.post("/validate-prompt")
async def validate_prompt(prompt: str):
    """
    Validate if a prompt contains sufficient information for document generation
    """
    # Basic validation logic
    required_keywords = {
        "loan_agreement": ["loan", "lender", "borrower", "amount"],
        "rental_agreement": ["rent", "landlord", "tenant", "property"],
        "service_agreement": ["service", "provider", "client", "terms"],
    }
    
    # Check for document type indicators
    doc_type = None
    for doc_type_name, keywords in required_keywords.items():
        if any(keyword in prompt.lower() for keyword in keywords):
            doc_type = doc_type_name
            break
    
    if not doc_type:
        return {
            "valid": False,
            "message": "Prompt does not clearly indicate a document type",
            "suggestions": [
                "Specify the type of document (e.g., loan agreement, rental agreement)",
                "Include key parties involved",
                "Mention important terms and amounts"
            ]
        }
    
    return {
        "valid": True,
        "document_type": doc_type,
        "message": "Prompt appears sufficient for document generation"
    }