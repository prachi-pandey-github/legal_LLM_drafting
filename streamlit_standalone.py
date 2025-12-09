"""
Standalone Streamlit App with Built-in Document Generation
No external API needed - everything runs in Streamlit Cloud
"""

import streamlit as st
import json
import tempfile
import os
from datetime import datetime
from typing import Dict, Any

# Mock LLM for demonstration (replace with actual implementation)
class MockLLMHandler:
    """Mock LLM handler for demo purposes"""
    
    def generate_document(self, prompt: str, doc_type: str = "loan_agreement") -> Dict[str, Any]:
        """Generate a mock document based on prompt"""
        
        # Simple template-based generation
        templates = {
            "loan_agreement": {
                "title": "LOAN AGREEMENT",
                "content": f"""
LOAN AGREEMENT

This Loan Agreement is made on {datetime.now().strftime('%d/%m/%Y')} between:

LENDER: [Please fill in lender details]
BORROWER: [Please fill in borrower details]

LOAN DETAILS:
- Amount: [As specified in your request]
- Interest Rate: [As specified]
- Tenure: [As specified]
- Repayment: Monthly installments

TERMS AND CONDITIONS:
1. The borrower agrees to repay the loan amount with interest
2. Payment shall be made on or before the due date each month
3. In case of default, additional charges may apply
4. This agreement is governed by Indian law

Based on your request: {prompt}

SIGNATURES:
Lender: ________________    Date: _______
Borrower: ________________  Date: _______
                """,
                "sections": ["parties", "loan_details", "terms", "signatures"]
            },
            "rental_agreement": {
                "title": "RENTAL AGREEMENT", 
                "content": f"""
RENTAL AGREEMENT

This Rental Agreement is made on {datetime.now().strftime('%d/%m/%Y')} between:

LANDLORD: [Please fill in landlord details]
TENANT: [Please fill in tenant details]

PROPERTY DETAILS:
- Address: [Property address]
- Rent Amount: [Monthly rent]
- Security Deposit: [Deposit amount]
- Lease Period: [Duration]

TERMS AND CONDITIONS:
1. Tenant agrees to pay rent on time each month
2. Security deposit shall be refunded upon lease termination
3. Property shall be maintained in good condition
4. Either party may terminate with proper notice

Based on your request: {prompt}

SIGNATURES:
Landlord: ________________  Date: _______
Tenant: ________________    Date: _______
                """,
                "sections": ["parties", "property_details", "terms", "signatures"]
            }
        }
        
        template = templates.get(doc_type, templates["loan_agreement"])
        
        return {
            "title": template["title"],
            "content": template["content"],
            "sections": template["sections"],
            "document_type": doc_type,
            "generated_at": datetime.now().isoformat(),
            "metadata": {
                "generator": "Streamlit Demo",
                "version": "1.0"
            }
        }

# Initialize session state
if 'generated_documents' not in st.session_state:
    st.session_state.generated_documents = []

if 'llm_handler' not in st.session_state:
    st.session_state.llm_handler = MockLLMHandler()

# App Configuration
st.set_page_config(
    page_title="Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main App
st.title("⚖️ Legal Document Generator")
st.markdown("Generate professional legal documents with AI assistance")

# Sidebar
with st.sidebar:
    st.header("📋 Document Configuration")
    
    doc_type = st.selectbox(
        "Document Type",
        ["loan_agreement", "rental_agreement", "service_agreement", "nda"],
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    st.header("🌍 Jurisdiction")
    jurisdiction = st.selectbox("Select Jurisdiction", ["IN", "US", "UK", "CA", "AU"])
    
    st.header("📚 Sample Prompts")
    if st.button("💰 Loan Agreement Sample"):
        st.session_state.sample_prompt = "Draft a Loan Agreement for ₹5,00,000 between Rohit Gupta (Lender) and Akash Mehta (Borrower), tenure 12 months, interest 10%, monthly repayment"
    
    if st.button("🏠 Rental Agreement Sample"):
        st.session_state.sample_prompt = "Create a rental agreement for a 2BHK apartment in Mumbai, monthly rent ₹25,000, security deposit ₹50,000, 11-month lease"

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("✍️ Document Request")
    
    # Use sample prompt if available
    default_prompt = st.session_state.get('sample_prompt', '')
    
    prompt = st.text_area(
        "Describe the document you need:",
        value=default_prompt,
        height=150,
        help="Provide detailed information about the document you want to generate",
        placeholder="Example: Draft a loan agreement for ₹50,000 between John (lender) and Mary (borrower), 6 months tenure, 12% annual interest..."
    )
    
    # Clear sample prompt after use
    if 'sample_prompt' in st.session_state:
        del st.session_state.sample_prompt
    
    if st.button("🚀 Generate Document", type="primary", use_container_width=True):
        if prompt.strip():
            with st.spinner("Generating document..."):
                try:
                    # Generate document
                    document = st.session_state.llm_handler.generate_document(prompt, doc_type)
                    
                    # Add to history
                    document['id'] = len(st.session_state.generated_documents) + 1
                    st.session_state.generated_documents.append(document)
                    
                    st.success("✅ Document generated successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error generating document: {str(e)}")
        else:
            st.warning("⚠️ Please enter a document description")

with col2:
    st.header("📄 Generated Document")
    
    if st.session_state.generated_documents:
        latest_doc = st.session_state.generated_documents[-1]
        
        # Display document
        st.subheader(latest_doc['title'])
        
        # Show document content in a nice format
        st.text_area(
            "Document Content:",
            value=latest_doc['content'],
            height=400,
            disabled=True
        )
        
        # Download options
        col_download1, col_download2 = st.columns(2)
        
        with col_download1:
            # Create downloadable text file
            doc_text = f"{latest_doc['title']}\n{'='*50}\n{latest_doc['content']}"
            st.download_button(
                "📥 Download as Text",
                data=doc_text,
                file_name=f"{doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_download2:
            # Create JSON download
            doc_json = json.dumps(latest_doc, indent=2)
            st.download_button(
                "📥 Download as JSON", 
                data=doc_json,
                file_name=f"{doc_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Document metadata
        with st.expander("📊 Document Metadata"):
            st.json(latest_doc['metadata'])
    
    else:
        st.info("👆 Generate your first document using the form above")

# Document History
if st.session_state.generated_documents:
    st.header("📚 Document History")
    
    for i, doc in enumerate(reversed(st.session_state.generated_documents)):
        with st.expander(f"📄 {doc['title']} (Generated: {doc['generated_at'][:16]})"):
            st.text_area(f"Content {i+1}:", doc['content'][:500] + "...", height=100, disabled=True)
            
            col1, col2 = st.columns(2)
            with col1:
                doc_text = f"{doc['title']}\n{'='*50}\n{doc['content']}"
                st.download_button(
                    "📥 Download Text",
                    data=doc_text,
                    file_name=f"document_{doc['id']}.txt",
                    key=f"download_text_{doc['id']}"
                )
            with col2:
                doc_json = json.dumps(doc, indent=2)
                st.download_button(
                    "📥 Download JSON",
                    data=doc_json,
                    file_name=f"document_{doc['id']}.json",
                    key=f"download_json_{doc['id']}"
                )

# Footer
st.markdown("---")
st.markdown("**⚖️ Legal Document Generator** - Powered by Streamlit | Made with ❤️ for legal professionals")

# Instructions for users
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    ### 📝 Instructions:
    
    1. **Select Document Type**: Choose from loan agreement, rental agreement, etc.
    2. **Choose Jurisdiction**: Select your country/region
    3. **Describe Your Document**: Be specific about:
       - Parties involved (names, addresses)
       - Financial amounts
       - Terms and conditions
       - Timeline/duration
    4. **Generate**: Click the generate button
    5. **Download**: Save your document as text or JSON
    
    ### 💡 Tips:
    - Use sample prompts for quick start
    - Be as detailed as possible for better results
    - Generated documents are templates - review and customize as needed
    - Always have legal documents reviewed by a qualified attorney
    
    ### ⚠️ Disclaimer:
    This tool generates document templates for reference only. 
    Always consult with a qualified legal professional before using any legal document.
    """)