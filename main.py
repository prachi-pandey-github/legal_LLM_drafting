# main_working.py - Working version with actual document generation
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import DocumentRequest, DocumentResponse
import uuid
import json
import os
import tempfile
from datetime import datetime
from document_generation.docx_builder import DocxBuilder

app = FastAPI(title="Legal Drafting LLM - Working Version", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store generated documents in memory for demo
generated_documents = {}

@app.get("/")
async def root():
    return {
        "message": "Legal Drafting LLM API - Working Version",
        "status": "active",
        "endpoints": [
            "/api/v1/document-types",
            "/api/v1/draft-document",
            "/api/v1/download/{document_id}"
        ]
    }

@app.get("/api/v1/document-types")
async def get_document_types():
    """Get supported document types"""
    return {
        "document_types": [
            {
                "type_id": "loan_agreement",
                "name": "Loan Agreement",
                "description": "Personal and business loan agreements"
            },
            {
                "type_id": "rental_agreement", 
                "name": "Rental Agreement",
                "description": "Residential and commercial rental agreements"
            },
            {
                "type_id": "service_agreement",
                "name": "Service Agreement", 
                "description": "Professional service contracts"
            },
            {
                "type_id": "nda",
                "name": "Non-Disclosure Agreement",
                "description": "Confidentiality agreements"
            },
            {
                "type_id": "employment_contract",
                "name": "Employment Contract",
                "description": "Employee agreements and contracts"
            }
        ]
    }

@app.post("/api/v1/draft-document", response_model=DocumentResponse)
async def draft_document(request: DocumentRequest):
    """Generate a legal document with actual DOCX creation"""
    
    # Basic validation
    if not request.prompt or len(request.prompt.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Prompt must be at least 10 characters long"
        )
    
    # Generate unique document ID
    document_id = str(uuid.uuid4())[:8]
    
    try:
        # Create DOCX document
        builder = DocxBuilder()
        
        # Get document content based on type
        if request.document_type == "loan_agreement":
            builder = create_loan_agreement(builder, request)
            sections_count = 3
        elif request.document_type == "rental_agreement":
            builder = create_rental_agreement(builder, request)
            sections_count = 3
        elif request.document_type == "service_agreement":
            builder = create_service_agreement(builder, request)
            sections_count = 3
        elif request.document_type == "nda":
            builder = create_nda(builder, request)
            sections_count = 3
        elif request.document_type == "employment_contract":
            builder = create_employment_contract(builder, request)
            sections_count = 3
        else:
            builder = create_generic_document(builder, request)
            sections_count = 3
        
        # Save document
        filename = f"legal_document_{document_id}.docx"
        filepath = builder.save_to_temp(filename)
        
        # Store document info
        generated_documents[document_id] = {
            "filepath": filepath,
            "filename": filename,
            "document_type": request.document_type,
            "created_at": datetime.now(),
            "variables": request.variables
        }
        
        return DocumentResponse(
            success=True,
            message="Document generated successfully",
            document_id=document_id,
            filename=filename,
            document_type=request.document_type,
            sections_count=sections_count,
            generated_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating document: {str(e)}"
        )

def create_loan_agreement(builder: DocxBuilder, request: DocumentRequest):
    """Create a compact loan agreement document for single page"""
    builder.add_title("PERSONAL LOAN AGREEMENT")
    
    # Get variables
    lender_name = request.variables.get('lender_name', '[LENDER NAME]')
    borrower_name = request.variables.get('borrower_name', '[BORROWER NAME]')
    amount = request.variables.get('amount', '[LOAN AMOUNT]')
    interest_rate = request.variables.get('interest_rate', '[INTEREST RATE]')
    tenure = request.variables.get('tenure', '[LOAN TENURE]')
    purpose = request.variables.get('purpose', 'General financial needs')
    
    # Proper agreement header
    builder.add_paragraph(f"This Loan Agreement ('Agreement') is entered into on {datetime.now().strftime('%B %d, %Y')}, between:")
    builder.add_paragraph(f"LENDER: {lender_name}")
    builder.add_paragraph(f"BORROWER: {borrower_name}")
    
    # Loan terms in compact format
    builder.add_heading("LOAN TERMS", level=1)
    builder.add_paragraph(f"Principal: {amount} | Interest: {interest_rate}% p.a. | Tenure: {tenure} months | Purpose: {purpose}")
    
    # Very compact terms and conditions
    builder.add_heading("TERMS", level=1)
    builder.add_paragraph(f"Repayment in equal monthly installments. Late payment incurs charges. Default makes full amount due immediately. Governed by {request.jurisdiction} law. Both parties acknowledge agreement.")
    
    # Ultra-compact signatures on same line
    builder.add_paragraph("SIGNATURES: ____________________    ____________________")
    builder.add_paragraph(f"                    {lender_name} (LENDER)                {borrower_name} (BORROWER)")
    
    return builder

def create_rental_agreement(builder: DocxBuilder, request: DocumentRequest):
    """Create a compact rental agreement document for single page"""
    builder.add_title("RENTAL AGREEMENT")
    
    # Get variables
    landlord_name = request.variables.get('landlord_name', '[LANDLORD NAME]')
    tenant_name = request.variables.get('tenant_name', '[TENANT NAME]')
    property_address = request.variables.get('property_address', '[PROPERTY ADDRESS]')
    rent_amount = request.variables.get('rent_amount', '[MONTHLY RENT]')
    lease_term = request.variables.get('lease_term', '[LEASE DURATION]')
    
    # Compact format
    builder.add_heading("PARTIES & PROPERTY", level=1)
    builder.add_paragraph(f"Agreement dated {datetime.now().strftime('%B %d, %Y')} between LANDLORD: {landlord_name} and TENANT: {tenant_name}.")
    builder.add_paragraph(f"Property: {property_address} | Rent: {rent_amount}/month | Term: {lease_term}")
    
    # Compact terms
    builder.add_heading("TERMS & CONDITIONS", level=1)
    builder.add_paragraph("1. Rent due 1st of each month. 2. Security deposit per regulations. 3. Tenant maintains property condition. 4. Either party terminates with 30-day notice.")
    builder.add_paragraph(f"Governed by laws of {request.jurisdiction}.")
    
    # Signatures
    builder.add_paragraph("\nSIGNATURES:")
    builder.add_signature_block(landlord_name, "LANDLORD")
    builder.add_signature_block(tenant_name, "TENANT")
    
    return builder

def create_service_agreement(builder: DocxBuilder, request: DocumentRequest):
    """Create a compact service agreement document for single page"""
    builder.add_title("SERVICE AGREEMENT")
    
    # Get variables
    service_provider = request.variables.get('service_provider', '[SERVICE PROVIDER]')
    client_name = request.variables.get('client_name', '[CLIENT NAME]')
    service_description = request.variables.get('service_description', 'Professional services')
    payment_amount = request.variables.get('payment_amount', '[PAYMENT AMOUNT]')
    contract_duration = request.variables.get('contract_duration', '[DURATION]')
    
    # Compact format
    builder.add_heading("PARTIES & SERVICES", level=1)
    builder.add_paragraph(f"Agreement dated {datetime.now().strftime('%B %d, %Y')} between PROVIDER: {service_provider} and CLIENT: {client_name}.")
    builder.add_paragraph(f"Services: {service_description} | Payment: {payment_amount} | Duration: {contract_duration}")
    
    # Terms
    builder.add_heading("TERMS & CONDITIONS", level=1)
    builder.add_paragraph(f"Provider delivers agreed services professionally and timely. Client pays as scheduled. Governed by {request.jurisdiction} law.")
    
    # Signatures
    builder.add_paragraph("\nSIGNATURES:")
    builder.add_signature_block(service_provider, "PROVIDER")
    builder.add_signature_block(client_name, "CLIENT")
    
    return builder

def create_nda(builder: DocxBuilder, request: DocumentRequest):
    """Create a compact NDA document for single page"""
    builder.add_title("NON-DISCLOSURE AGREEMENT")
    
    # Get variables
    disclosing_party = request.variables.get('disclosing_party', '[DISCLOSING PARTY]')
    receiving_party = request.variables.get('receiving_party', '[RECEIVING PARTY]')
    nda_duration = request.variables.get('nda_duration', '2 years')
    
    # Compact format
    builder.add_heading("PARTIES & CONFIDENTIALITY", level=1)
    builder.add_paragraph(f"Agreement dated {datetime.now().strftime('%B %d, %Y')} between DISCLOSING PARTY: {disclosing_party} and RECEIVING PARTY: {receiving_party}.")
    builder.add_paragraph(f"Duration: {nda_duration} | All non-public information shared remains strictly confidential.")
    
    # Terms
    builder.add_heading("OBLIGATIONS", level=1)
    builder.add_paragraph(f"Receiving party maintains confidentiality, uses info only for intended purpose, returns/destroys upon request. Governed by {request.jurisdiction} law.")
    
    # Signatures
    builder.add_paragraph("\nSIGNATURES:")
    builder.add_signature_block(disclosing_party, "DISCLOSING")
    builder.add_signature_block(receiving_party, "RECEIVING")
    
    return builder

def create_employment_contract(builder: DocxBuilder, request: DocumentRequest):
    """Create a compact employment contract document for single page"""
    builder.add_title("EMPLOYMENT CONTRACT")
    
    # Get variables
    employer_name = request.variables.get('employer_name', '[EMPLOYER NAME]')
    employee_name = request.variables.get('employee_name', '[EMPLOYEE NAME]')
    job_title = request.variables.get('job_title', '[JOB TITLE]')
    start_date = request.variables.get('start_date', '[START DATE]')
    salary = request.variables.get('salary', '[ANNUAL SALARY]')
    working_hours = request.variables.get('working_hours', '40 hrs/week')
    
    # Compact format
    builder.add_heading("EMPLOYMENT DETAILS", level=1)
    builder.add_paragraph(f"Contract dated {datetime.now().strftime('%B %d, %Y')} between EMPLOYER: {employer_name} and EMPLOYEE: {employee_name}.")
    builder.add_paragraph(f"Position: {job_title} | Start: {start_date} | Salary: {salary} | Hours: {working_hours}")
    
    # Terms
    builder.add_heading("TERMS & CONDITIONS", level=1)
    builder.add_paragraph(f"Employee performs duties professionally. Either party terminates with 2 weeks notice. Governed by {request.jurisdiction} law.")
    
    # Signatures
    builder.add_paragraph("\nSIGNATURES:")
    builder.add_signature_block(employer_name, "EMPLOYER")
    builder.add_signature_block(employee_name, "EMPLOYEE")
    
    return builder

def create_generic_document(builder: DocxBuilder, request: DocumentRequest):
    """Create a generic legal document"""
    doc_type_name = request.document_type.replace('_', ' ').title() if request.document_type else 'Legal Document'
    builder.add_title(doc_type_name.upper())
    
    # Introduction
    builder.add_heading("1. INTRODUCTION", level=1)
    builder.add_paragraph(f"This document was generated based on the following requirements:")
    builder.add_paragraph(f"'{request.prompt}'")
    
    # Variables
    if request.variables:
        builder.add_heading("2. DETAILS", level=1)
        for key, value in request.variables.items():
            builder.add_paragraph(f"• {key.replace('_', ' ').title()}: {value}")
    
    # Governing law
    builder.add_heading("3. GOVERNING LAW", level=1)
    builder.add_paragraph(f"This document shall be governed by the laws of {request.jurisdiction}.")
    
    return builder

@app.get("/api/v1/download/{document_id}")
async def download_document(document_id: str):
    """Download generated document"""
    if document_id not in generated_documents:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    
    doc_info = generated_documents[document_id]
    filepath = doc_info["filepath"]
    filename = doc_info["filename"]
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail="Document file not found on server"
        )
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)