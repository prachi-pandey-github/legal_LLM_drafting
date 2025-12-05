"""
Advanced Streamlit Components for Legal Drafting LLM
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

def render_document_templates():
    """Render document templates section"""
    st.header("📋 Document Templates")
    
    templates = {
        "Basic Loan Agreement": {
            "description": "Simple personal loan template",
            "fields": 6,
            "complexity": "Low"
        },
        "Commercial Rental": {
            "description": "Commercial property rental agreement",
            "fields": 12,
            "complexity": "High"
        },
        "Software Service Agreement": {
            "description": "IT service provider contract",
            "fields": 9,
            "complexity": "Medium"
        }
    }
    
    for name, info in templates.items():
        with st.expander(f"📄 {name}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Fields:** {info['fields']}")
            with col2:
                st.write(f"**Complexity:** {info['complexity']}")
            with col3:
                if st.button(f"Use Template", key=f"template_{name}"):
                    st.success(f"Template '{name}' loaded!")

def render_document_history():
    """Render document generation history"""
    st.header("📚 Document History")
    
    # Show message when no history is available
    st.info("📝 No document history available. Generate your first document to see it here!")

def render_help_section():
    """Render help and documentation"""
    st.header("❓ Help & Documentation")
    
    tabs = st.tabs(["🚀 Quick Start", "📖 User Guide", "🔧 Troubleshooting", "📞 Support"])
    
    with tabs[0]:
        st.markdown("""
        ## Quick Start Guide
        
        ### 1. Select Document Type
        Choose the type of legal document you want to generate from the sidebar.
        
        ### 2. Describe Your Needs
        Write a clear description of what you need in the text area.
        
        ### 3. Fill Required Information
        Complete all required fields marked with (*).
        
        ### 4. Generate & Download
        Click the generate button and wait for your document to be ready.
        """)
        
        st.info("💡 **Tip**: Use detailed descriptions for better results!")
    
    with tabs[1]:
        st.markdown("""
        ## Detailed User Guide
        
        ### Document Types
        
        **Loan Agreements**
        - Personal loans
        - Business loans
        - Secured/unsecured loans
        - Custom repayment terms
        
        **Rental Agreements**
        - Residential properties
        - Commercial spaces
        - Short-term/long-term leases
        - Custom clauses
        
        **Service Agreements**
        - Professional services
        - Consulting contracts
        - Software development
        - Maintenance agreements
        
        **NDAs (Non-Disclosure Agreements)**
        - Mutual confidentiality
        - One-way disclosure
        - Employee NDAs
        - Business partnerships
        """)
    
    with tabs[2]:
        st.markdown("""
        ## Troubleshooting
        
        ### Common Issues
        
        **"API Server Not Running"**
        - Check if the FastAPI server is started
        - Verify port 8000 is available
        - Restart the server if needed
        
        **Document Generation Fails**
        - Ensure all required fields are filled
        - Check your internet connection
        - Verify API key is configured
        
        **Download Not Working**
        - Try refreshing the page
        - Check browser download settings
        - Contact support if issue persists
        """)
    
    with tabs[3]:
        st.markdown("""
        ## Support & Contact
        
        ### Getting Help
        
        **Technical Issues**
        - Check the troubleshooting guide above
        - Review server logs for errors
        - Ensure all dependencies are installed
        
        **Feature Requests**
        - Use the feedback form below
        - Describe your use case clearly
        - Include examples if possible
        
        **Bug Reports**
        - Include steps to reproduce
        - Provide error messages
        - Mention browser/system info
        """)
        
        # Feedback form
        st.subheader("📝 Feedback Form")
        with st.form("feedback_form"):
            feedback_type = st.selectbox("Type", ["Bug Report", "Feature Request", "General Feedback"])
            feedback_text = st.text_area("Your Message", height=100)
            
            if st.form_submit_button("Submit Feedback"):
                st.success("Thank you for your feedback! We'll review it soon.")

def render_settings():
    """Render application settings"""
    st.header("⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 Appearance")
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        language = st.selectbox("Language", ["English", "Hindi", "Marathi"])
        
        st.subheader("📄 Document Preferences")
        default_jurisdiction = st.selectbox("Default Jurisdiction", ["IN", "US", "UK", "CA", "AU"])
        auto_download = st.checkbox("Auto-download generated documents")
        
    with col2:
        st.subheader("🔔 Notifications")
        email_notifications = st.checkbox("Email notifications")
        browser_notifications = st.checkbox("Browser notifications")
        
        st.subheader("🔒 Privacy")
        save_history = st.checkbox("Save document history", value=True)
        analytics = st.checkbox("Share usage analytics", value=True)
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")

# Export functions for use in main app
__all__ = [
    'render_document_templates', 
    'render_document_history',
    'render_help_section',
    'render_settings'
]