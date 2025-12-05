# 🎨 Streamlit Web App - Legal Drafting LLM

A user-friendly web interface for the Legal Drafting LLM system, built with Streamlit.

## 🚀 Quick Start

### Option 1: Automatic Startup (Recommended)
```bash
# Double-click or run:
start_app.bat
```

### Option 2: Manual Startup

1. **Start API Server:**
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Start Streamlit App:**
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```

3. **Access the App:**
   - Web Interface: http://localhost:8501
   - API Documentation: http://127.0.0.1:8000/docs

## ✨ Features

### 📄 Document Types Supported
- **Loan Agreements** - Personal and business loans
- **Rental Agreements** - Residential and commercial leases  
- **Service Agreements** - Professional service contracts
- **NDAs** - Non-disclosure agreements

### 🎯 Key Features
- **Intuitive Interface** - Easy-to-use web form
- **Dynamic Forms** - Context-aware input fields
- **Real-time Generation** - Instant document creation
- **Preview & Download** - View and save documents
- **Multi-jurisdiction** - Support for different legal systems
- **Sample Prompts** - Pre-built examples to get started

## 🖥️ User Interface

### Main Sections

1. **Sidebar Configuration**
   - Document type selection
   - Jurisdiction settings
   - Document information

2. **Input Panel** (Left Column)
   - Natural language prompt input
   - Required information fields
   - Optional details (expandable)
   - Generate button

3. **Output Panel** (Right Column)
   - Generated document display
   - Metadata and statistics
   - Download functionality
   - Document preview

## 📝 How to Use

1. **Select Document Type**
   - Choose from the dropdown in the sidebar
   - View document description and requirements

2. **Enter Description**
   - Write a natural language description
   - Be specific about your requirements
   - Use the sample prompts for guidance

3. **Fill Details**
   - Complete required fields (marked as mandatory)
   - Optionally fill additional information
   - Set jurisdiction as needed

4. **Generate Document**
   - Click "Generate Document" button
   - Wait for processing (usually 10-30 seconds)
   - View results and download

## 🎯 Sample Usage

### Example 1: Loan Agreement
```
Prompt: "Draft a personal loan agreement between ABC Bank and John Doe for ₹5,00,000"

Required Fields:
- Lender Name: ABC Bank
- Borrower Name: John Doe  
- Amount: ₹5,00,000
- Interest Rate: 12
- Tenure: 24

Result: Professional loan agreement with all legal clauses
```

### Example 2: Rental Agreement
```
Prompt: "Create a rental agreement for a 2BHK apartment in Mumbai"

Required Fields:
- Landlord Name: Mrs. Sharma
- Tenant Name: Mr. Kumar
- Property Address: 123 Marine Drive, Mumbai
- Rent Amount: ₹25,000

Result: Comprehensive rental agreement with standard terms
```

## 🔧 Technical Details

### Architecture
```
┌─────────────────┐    HTTP     ┌─────────────────┐
│  Streamlit App  │ ────────────▶ │   FastAPI      │
│  (Frontend)     │              │   (Backend)     │
│  Port: 8501     │              │   Port: 8000    │
└─────────────────┘              └─────────────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │   Gemini AI     │
                                 │   (LLM Engine)  │
                                 └─────────────────┘
```

### Dependencies
- `streamlit` - Web framework
- `requests` - HTTP client for API calls
- All FastAPI backend dependencies

### Configuration
- Streamlit config: `.streamlit/config.toml`
- API endpoint: `http://127.0.0.1:8000`
- Theme: Legal professional blue theme

## 🛠️ Troubleshooting

### Common Issues

1. **"API Server Not Running" Error**
   - Ensure FastAPI server is started on port 8000
   - Check if `uvicorn main:app --reload` is running

2. **Connection Refused**
   - Verify both servers are running
   - Check firewall settings
   - Ensure ports 8000 and 8501 are available

3. **Document Generation Fails**
   - Check API server logs
   - Verify Gemini API key is set
   - Ensure all required fields are filled

### Debug Mode
Enable debug information by expanding the "Debug Information" section when errors occur.

## 📋 Features Overview

### ✅ Current Features
- Multi-document type support
- Dynamic form generation
- Real-time API health checking
- Progress indicators
- Document metadata display
- Sample prompts
- Responsive design

### 🔄 Future Enhancements
- Document editing capabilities
- Template customization
- Batch document generation
- Document comparison
- Export to multiple formats
- User authentication
- Document history

## 🎨 UI/UX Features

- **Professional Theme** - Legal industry colors
- **Responsive Design** - Works on all screen sizes
- **Progress Indicators** - Visual feedback during generation
- **Error Handling** - Clear error messages and debug info
- **Sample Data** - Pre-filled examples for quick testing
- **Expandable Sections** - Clean, organized interface

## 📞 Support

For issues or questions:
1. Check the API server logs
2. Verify all dependencies are installed
3. Ensure environment variables are set
4. Review the troubleshooting section above

---
**Legal Drafting LLM** - Powered by Streamlit, FastAPI, and Gemini AI