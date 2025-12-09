"""
Legal Drafting LLM - Streamlit Web Application
"""

import streamlit as st
import requests
import json
import tempfile
import os
from datetime import datetime
from typing import Dict, Any
from streamlit_components import (
    render_document_templates,
    render_document_history,
    render_help_section,
    render_settings
)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
DOCUMENT_TYPES = {
    "loan_agreement": "Loan Agreement",
    "rental_agreement": "Rental Agreement", 
    "service_agreement": "Service Agreement",
    "nda": "Non-Disclosure Agreement"
}

def init_session_state():
    """Initialize session state variables"""
    if 'generated_documents' not in st.session_state:
        st.session_state.generated_documents = []
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None

def check_api_connection():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_document_types():
    """Fetch document types from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/document-types")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def generate_document(document_data: Dict[str, Any]):
    """Generate document via API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/draft-document",
            json=document_data,
            timeout=60
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error generating document: {str(e)}")
        return None

def download_document(document_id: str):
    """Download generated document"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/download/{document_id}")
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

def render_sidebar():
    """Render sidebar with navigation and settings"""
    st.sidebar.title("🏛️ Legal Drafting LLM")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.selectbox(
        "📍 Navigation",
        ["Document Generator", "Templates", "History", "Help", "Settings"]
    )
    
    st.sidebar.markdown("---")
    
    # API Status
    if check_api_connection():
        st.sidebar.success("🟢 API Server Connected")
    else:
        st.sidebar.error("🔴 API Server Offline")
        st.sidebar.info("Please start the FastAPI server:\n`uvicorn main:app --reload`")
    
    return page

def render_document_form():
    """Render document generation form"""
    st.header("📝 Generate Legal Document")
    
    # Document type selection
    doc_type = st.selectbox(
        "Document Type *",
        options=list(DOCUMENT_TYPES.keys()),
        format_func=lambda x: DOCUMENT_TYPES[x],
        help="Select the type of legal document you want to generate"
    )
    
    # Main description
    description = st.text_area(
        "Document Description *",
        height=150,
        placeholder="Describe the legal document you need. Be specific about parties involved, terms, conditions, and any special requirements...",
        help="Provide a detailed description of what you need"
    )
    
    # Additional parameters in columns
    col1, col2 = st.columns(2)
    
    with col1:
        jurisdiction = st.selectbox(
            "Jurisdiction",
            ["IN", "US", "UK", "CA", "AU"],
            help="Legal jurisdiction for the document"
        )
        
        borrower = st.text_input(
            "Borrower",
            placeholder="e.g., John Doe",
            help="Name of the borrower"
        )
    
    with col2:
        effective_date = st.date_input(
            "Effective Date",
            help="When the agreement becomes effective"
        )
        
        lender = st.text_input(
            "Lender",
            placeholder="e.g., ABC Bank",
            help="Name of the lender"
        )
    
    # Loan specific fields (for loan agreements)
    if doc_type == "loan_agreement":
        st.subheader("💰 Loan Details")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            principal_amount = st.number_input(
                "Principal Amount",
                min_value=0.0,
                format="%.2f",
                help="The loan amount in your local currency"
            )
        
        with col4:
            interest_rate = st.number_input(
                "Interest Rate (% per annum)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.2f",
                help="Annual interest rate percentage"
            )
        
        with col5:
            loan_tenure = st.number_input(
                "Loan Tenure (months)",
                min_value=1,
                max_value=360,
                step=1,
                help="Loan duration in months"
            )
        
        # Purpose field (full width under loan details)
        loan_purpose = st.text_input(
            "Loan Purpose",
            placeholder="e.g., Home renovation, Business expansion, Education",
            help="Describe the purpose for which the loan will be used"
        )
    else:
        principal_amount = None
        interest_rate = None
        loan_tenure = None
        loan_purpose = None
    
    # Special terms field (full width)
    special_terms = st.text_input(
        "Special Terms/Clauses",
        placeholder="Any specific clauses or terms to include",
        help="Additional terms or clauses to include"
    )
    
    # Generate button
    if st.button("🚀 Generate Document", type="primary", disabled=not (doc_type and description)):
        if not check_api_connection():
            st.error("❌ API server is not running. Please start the FastAPI server first.")
            return
            
        with st.spinner("Generating your legal document... This may take a few moments."):
            # Create the prompt with all the information for proper legal document format
            if doc_type == "loan_agreement":
                prompt = f"Generate a Personal Loan Agreement with proper legal formatting.\n\n"
                prompt += f"The agreement should start with: 'This Loan Agreement (\"Agreement\") is entered into on {effective_date}, between:'\n"
                prompt += f"LENDER: {lender if lender else 'Lender'}\n"
                prompt += f"BORROWER: {borrower if borrower else 'Borrower'}\n\n"
                
                if principal_amount and interest_rate and loan_tenure:
                    prompt += f"Loan Details:\n"
                    prompt += f"- Principal Amount: {principal_amount:,.2f}\n"
                    prompt += f"- Interest Rate: {interest_rate}% per annum\n"
                    prompt += f"- Loan Tenure: {int(loan_tenure)} months\n"
                    if loan_purpose:
                        prompt += f"- Purpose: {loan_purpose}\n"
                
                prompt += f"\nJurisdiction: {jurisdiction}\n"
                if special_terms:
                    prompt += f"Special Terms: {special_terms}\n"
                
                prompt += f"\nAdditional Requirements: {description}"
            else:
                prompt = f"{description}\n\n"
                prompt += f"Document Type: {DOCUMENT_TYPES[doc_type]}\n"
                prompt += f"Jurisdiction: {jurisdiction}\n"
                prompt += f"Borrower: {borrower if borrower else 'Borrower'}\n"
                prompt += f"Lender: {lender if lender else 'Lender'}\n"
                prompt += f"Effective Date: {effective_date}\n"
                if special_terms:
                    prompt += f"Special Terms: {special_terms}\n"
            
            # Prepare variables dictionary
            variables = {
                "borrower_name": borrower if borrower else "Borrower",
                "lender_name": lender if lender else "Lender",
                "effective_date": str(effective_date),
                "special_terms": special_terms
            }
            
            # Add loan-specific variables if it's a loan agreement
            if doc_type == "loan_agreement":
                variables.update({
                    "amount": f"{principal_amount:,.2f}" if principal_amount else "[LOAN AMOUNT]",
                    "interest_rate": f"{interest_rate}" if interest_rate else "[INTEREST RATE]",
                    "tenure": f"{int(loan_tenure)}" if loan_tenure else "[LOAN TENURE]",
                    "purpose": loan_purpose if loan_purpose else "General financial needs"
                })
            
            document_data = {
                "prompt": prompt,
                "document_type": doc_type,
                "jurisdiction": jurisdiction,
                "variables": variables
            }
            
            result = generate_document(document_data)
            
            if result:
                st.success("✅ Document generated successfully!")
                st.session_state.current_document = result
                
                # Add to history
                st.session_state.generated_documents.append({
                    "title": f"{DOCUMENT_TYPES[doc_type]} - {effective_date}",
                    "type": doc_type,
                    "generated_at": str(datetime.now()),
                    "document_id": result.get('document_id', ''),
                    "status": "Completed"
                })
            else:
                st.error("❌ Failed to generate document. Please try again.")

def render_document_preview():
    """Render document preview and download"""
    if st.session_state.current_document:
        st.header("📄 Generated Document")
        
        doc = st.session_state.current_document
        
        # Document info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Document ID", doc.get('document_id', 'N/A'))
        with col2:
            st.metric("Status", doc.get('status', 'Generated'))
        with col3:
            st.metric("Pages", doc.get('pages', 1))
        
        # Content preview
        if 'content' in doc:
            st.subheader("📖 Preview")
            with st.expander("View Document Content", expanded=True):
                st.markdown(doc['content'])
        
        # Download button
        if 'document_id' in doc:
            if st.button("📥 Download Document (.docx)", type="primary"):
                content = download_document(doc['document_id'])
                if content:
                    st.download_button(
                        label="💾 Save Document",
                        data=content,
                        file_name=f"{doc.get('document_id', 'document')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error("Failed to download document")

def main():
    """Main application"""
    st.set_page_config(
        page_title="Legal Drafting LLM",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render main content based on selected page
    if page == "Document Generator":
        col1, col2 = st.columns([3, 2])
        
        with col1:
            render_document_form()
        
        with col2:
            render_document_preview()
    
    elif page == "Templates":
        render_document_templates()
    
    elif page == "History":
        render_document_history()
        
        # Show recent documents from session
        if st.session_state.generated_documents:
            st.subheader("📋 Current Session Documents")
            for i, doc in enumerate(reversed(st.session_state.generated_documents)):
                with st.expander(f"📄 {doc['title']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Type:** {DOCUMENT_TYPES.get(doc['type'], doc['type'])}")
                    with col2:
                        st.write(f"**Generated:** {doc['generated_at'][:19]}")
                    with col3:
                        st.write(f"**Status:** {doc['status']}")
    
    elif page == "Help":
        render_help_section()
    
    elif page == "Settings":
        render_settings()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 20px;'>"
        "Legal Drafting LLM v1.0.0 | Built with Streamlit & FastAPI"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()