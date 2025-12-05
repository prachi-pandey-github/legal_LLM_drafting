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
            sections_count = 6
        elif request.document_type == "rental_agreement":
            builder = create_rental_agreement(builder, request)
            sections_count = 5
        elif request.document_type == "service_agreement":
            builder = create_service_agreement(builder, request)
            sections_count = 5
        elif request.document_type == "nda":
            builder = create_nda(builder, request)
            sections_count = 4
        elif request.document_type == "employment_contract":
            builder = create_employment_contract(builder, request)
            sections_count = 7
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
    """Create a loan agreement document"""
    builder.add_title("PERSONAL LOAN AGREEMENT")
    
    # Parties section
    builder.add_heading("1. PARTIES", level=1)
    lender_name = request.variables.get('lender_name', '[LENDER NAME]')
    borrower_name = request.variables.get('borrower_name', '[BORROWER NAME]')
    builder.add_paragraph(f"This Loan Agreement ('Agreement') is entered into on {datetime.now().strftime('%B %d, %Y')}, between:")
    builder.add_paragraph(f"• LENDER: {lender_name}")
    builder.add_paragraph(f"• BORROWER: {borrower_name}")
    
    # Loan terms
    builder.add_heading("2. LOAN TERMS", level=1)
    amount = request.variables.get('amount', '[LOAN AMOUNT]')
    interest_rate = request.variables.get('interest_rate', '[INTEREST RATE]')
    tenure = request.variables.get('tenure', '[LOAN TENURE]')
    
    builder.add_paragraph(f"• Principal Amount: {amount}")
    builder.add_paragraph(f"• Interest Rate: {interest_rate}% per annum")
    builder.add_paragraph(f"• Loan Tenure: {tenure} months")
    builder.add_paragraph(f"• Repayment: Equal monthly installments")
    
    # Purpose
    builder.add_heading("3. PURPOSE", level=1)
    purpose = request.variables.get('purpose', 'General financial needs')
    builder.add_paragraph(f"The loan shall be used for: {purpose}")
    
    # Repayment terms
    builder.add_heading("4. REPAYMENT TERMS", level=1)
    builder.add_paragraph("1. The Borrower shall repay the loan in equal monthly installments.")
    builder.add_paragraph("2. Each installment includes principal and interest components.")
    builder.add_paragraph("3. Payments are due on the same date each month.")
    builder.add_paragraph("4. Late payment may incur additional charges.")
    
    # Default clause
    builder.add_heading("5. DEFAULT", level=1)
    builder.add_paragraph("In case of default, the entire outstanding amount becomes immediately due and payable.")
    
    # Governing law
    builder.add_heading("6. GOVERNING LAW", level=1)
    builder.add_paragraph(f"This Agreement shall be governed by the laws of {request.jurisdiction}.")
    
    # Signatures
    builder.add_paragraph("\n\nSIGNATURES:")
    builder.add_signature_block(lender_name, "LENDER")
    builder.add_paragraph("\n")
    builder.add_signature_block(borrower_name, "BORROWER")
    
    return builder

def create_rental_agreement(builder: DocxBuilder, request: DocumentRequest):
    """Create a rental agreement document"""
    builder.add_title("RENTAL AGREEMENT")
    
    # Parties
    builder.add_heading("1. PARTIES", level=1)
    landlord_name = request.variables.get('landlord_name', '[LANDLORD NAME]')
    tenant_name = request.variables.get('tenant_name', '[TENANT NAME]')
    builder.add_paragraph(f"This Rental Agreement is made on {datetime.now().strftime('%B %d, %Y')}, between:")
    builder.add_paragraph(f"• LANDLORD: {landlord_name}")
    builder.add_paragraph(f"• TENANT: {tenant_name}")
    
    # Property details
    builder.add_heading("2. PROPERTY DETAILS", level=1)
    property_address = request.variables.get('property_address', '[PROPERTY ADDRESS]')
    rent_amount = request.variables.get('rent_amount', '[MONTHLY RENT]')
    lease_term = request.variables.get('lease_term', '[LEASE DURATION]')
    
    builder.add_paragraph(f"• Property Address: {property_address}")
    builder.add_paragraph(f"• Monthly Rent: {rent_amount}")
    builder.add_paragraph(f"• Lease Term: {lease_term}")
    
    # Terms and conditions
    builder.add_heading("3. TERMS AND CONDITIONS", level=1)
    builder.add_paragraph("1. Rent is due on the 1st of each month.")
    builder.add_paragraph("2. Security deposit as per local regulations.")
    builder.add_paragraph("3. Tenant responsible for utilities unless specified.")
    builder.add_paragraph("4. Property to be maintained in good condition.")
    
    # Termination
    builder.add_heading("4. TERMINATION", level=1)
    notice_period = request.variables.get('notice_period', '30 days')
    builder.add_paragraph(f"Either party may terminate with {notice_period} written notice.")
    
    # Governing law
    builder.add_heading("5. GOVERNING LAW", level=1)
    builder.add_paragraph(f"This Agreement shall be governed by the laws of {request.jurisdiction}.")
    
    # Signatures
    builder.add_paragraph("\n\nSIGNATURES:")
    builder.add_signature_block(landlord_name, "LANDLORD")
    builder.add_paragraph("\n")
    builder.add_signature_block(tenant_name, "TENANT")
    
    return builder

def create_service_agreement(builder: DocxBuilder, request: DocumentRequest):
    """Create a service agreement document"""
    builder.add_title("SERVICE AGREEMENT")
    
    # Parties
    builder.add_heading("1. PARTIES", level=1)
    service_provider = request.variables.get('service_provider', '[SERVICE PROVIDER]')
    client_name = request.variables.get('client_name', '[CLIENT NAME]')
    builder.add_paragraph(f"This Service Agreement is entered into on {datetime.now().strftime('%B %d, %Y')}, between:")
    builder.add_paragraph(f"• SERVICE PROVIDER: {service_provider}")
    builder.add_paragraph(f"• CLIENT: {client_name}")
    
    # Services
    builder.add_heading("2. SERVICES", level=1)
    service_description = request.variables.get('service_description', 'Professional services as outlined')
    builder.add_paragraph(f"Services to be provided: {service_description}")
    
    # Compensation
    builder.add_heading("3. COMPENSATION", level=1)
    payment_amount = request.variables.get('payment_amount', '[PAYMENT AMOUNT]')
    payment_schedule = request.variables.get('payment_schedule', 'As agreed')
    builder.add_paragraph(f"• Total Compensation: {payment_amount}")
    builder.add_paragraph(f"• Payment Schedule: {payment_schedule}")
    
    # Term
    builder.add_heading("4. TERM", level=1)
    contract_duration = request.variables.get('contract_duration', '[CONTRACT DURATION]')
    builder.add_paragraph(f"This agreement shall remain in effect for: {contract_duration}")
    
    # Governing law
    builder.add_heading("5. GOVERNING LAW", level=1)
    builder.add_paragraph(f"This Agreement shall be governed by the laws of {request.jurisdiction}.")
    
    # Signatures
    builder.add_paragraph("\n\nSIGNATURES:")
    builder.add_signature_block(service_provider, "SERVICE PROVIDER")
    builder.add_paragraph("\n")
    builder.add_signature_block(client_name, "CLIENT")
    
    return builder

def create_nda(builder: DocxBuilder, request: DocumentRequest):
    """Create an NDA document"""
    builder.add_title("NON-DISCLOSURE AGREEMENT")
    
    # Parties
    builder.add_heading("1. PARTIES", level=1)
    disclosing_party = request.variables.get('disclosing_party', '[DISCLOSING PARTY]')
    receiving_party = request.variables.get('receiving_party', '[RECEIVING PARTY]')
    builder.add_paragraph(f"This Non-Disclosure Agreement is made on {datetime.now().strftime('%B %d, %Y')}, between:")
    builder.add_paragraph(f"• DISCLOSING PARTY: {disclosing_party}")
    builder.add_paragraph(f"• RECEIVING PARTY: {receiving_party}")
    
    # Confidential information
    builder.add_heading("2. CONFIDENTIAL INFORMATION", level=1)
    builder.add_paragraph("All non-public, proprietary information shared between parties.")
    
    # Obligations
    builder.add_heading("3. OBLIGATIONS", level=1)
    builder.add_paragraph("1. Maintain strict confidentiality of all shared information.")
    builder.add_paragraph("2. Use information solely for the intended purpose.")
    builder.add_paragraph("3. Return or destroy information upon request.")
    
    # Term
    builder.add_heading("4. TERM", level=1)
    nda_duration = request.variables.get('nda_duration', '2 years')
    builder.add_paragraph(f"This agreement remains in effect for: {nda_duration}")
    builder.add_paragraph(f"Governed by the laws of {request.jurisdiction}.")
    
    # Signatures
    builder.add_paragraph("\n\nSIGNATURES:")
    builder.add_signature_block(disclosing_party, "DISCLOSING PARTY")
    builder.add_paragraph("\n")
    builder.add_signature_block(receiving_party, "RECEIVING PARTY")
    
    return builder

def create_employment_contract(builder: DocxBuilder, request: DocumentRequest):
    """Create an employment contract document"""
    builder.add_title("EMPLOYMENT CONTRACT")
    
    # Parties
    builder.add_heading("1. PARTIES", level=1)
    employer_name = request.variables.get('employer_name', '[EMPLOYER NAME]')
    employee_name = request.variables.get('employee_name', '[EMPLOYEE NAME]')
    builder.add_paragraph(f"This Employment Contract is made on {datetime.now().strftime('%B %d, %Y')}, between:")
    builder.add_paragraph(f"• EMPLOYER: {employer_name}")
    builder.add_paragraph(f"• EMPLOYEE: {employee_name}")
    
    # Position
    builder.add_heading("2. POSITION", level=1)
    job_title = request.variables.get('job_title', '[JOB TITLE]')
    start_date = request.variables.get('start_date', '[START DATE]')
    builder.add_paragraph(f"• Job Title: {job_title}")
    builder.add_paragraph(f"• Start Date: {start_date}")
    
    # Compensation
    builder.add_heading("3. COMPENSATION", level=1)
    salary = request.variables.get('salary', '[ANNUAL SALARY]')
    builder.add_paragraph(f"• Annual Salary: {salary}")
    builder.add_paragraph("• Benefits as per company policy")
    
    # Working hours
    builder.add_heading("4. WORKING HOURS", level=1)
    working_hours = request.variables.get('working_hours', '40 hours per week')
    builder.add_paragraph(f"Standard working hours: {working_hours}")
    
    # Duties
    builder.add_heading("5. DUTIES AND RESPONSIBILITIES", level=1)
    job_description = request.variables.get('job_description', 'As outlined in job description')
    builder.add_paragraph(f"Employee shall perform: {job_description}")
    
    # Termination
    builder.add_heading("6. TERMINATION", level=1)
    notice_period = request.variables.get('notice_period', '2 weeks')
    builder.add_paragraph(f"Either party may terminate with {notice_period} written notice.")
    
    # Governing law
    builder.add_heading("7. GOVERNING LAW", level=1)
    builder.add_paragraph(f"This Contract shall be governed by the laws of {request.jurisdiction}.")
    
    # Signatures
    builder.add_paragraph("\n\nSIGNATURES:")
    builder.add_signature_block(employer_name, "EMPLOYER")
    builder.add_paragraph("\n")
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