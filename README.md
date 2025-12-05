# 🏛️ Legal LLM Drafting System

An AI-powered legal document generation system that uses Large Language Models (LLMs) with Retrieval-Augmented Generation (RAG) to create professional legal documents.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Web Interface](#-web-interface)
- [Document Types](#-document-types)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **AI-Powered Document Generation**: Uses LLMs to generate legally sound documents
- **RAG Integration**: Retrieves relevant legal clauses from a knowledge base
- **Multiple Document Types**: Supports loan agreements, rental agreements, service agreements, and NDAs
- **RESTful API**: FastAPI-based backend for programmatic access
- **Web Interface**: User-friendly Streamlit frontend
- **Document Templates**: Pre-built templates for common legal documents
- **Multi-jurisdiction Support**: Supports different legal jurisdictions (IN, US, UK, CA, AU)
- **DOCX Export**: Generates professional Microsoft Word documents
- **Comprehensive Testing**: Unit tests for all major components

## 🏗️ Architecture

```
legal_drafting_llm/
├── api/                    # FastAPI backend
│   ├── dependencies.py    # Dependency injection
│   ├── routes.py          # API endpoints
│   └── schemas.py         # Pydantic models
├── llm/                   # LLM and AI components
│   ├── model_handler.py   # Main LLM handler
│   ├── prompt_templates.py # Document-specific prompts
│   ├── rag_pipeline.py    # RAG implementation
│   └── langgraph_workflow.py # Multi-step workflows
├── document_generation/   # Document processing
│   ├── docx_builder.py    # DOCX document creation
│   └── template_processor.py # Template handling
├── data/                  # Data storage
│   ├── legal_clauses/     # Legal clause database
│   └── embeddings/        # Vector embeddings
├── utils/                 # Utility functions
├── tests/                 # Test suite
├── main.py               # FastAPI application
└── streamlit_app.py      # Web interface
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/prachi-pandey-github/legal_LLM_drafting.git
   cd legal_LLM_drafting
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the knowledge base:**
   ```bash
   python -c "from llm.rag_pipeline import RAGPipeline; RAGPipeline().build_index()"
   ```

## 💻 Usage

### Starting the Application

1. **Start the FastAPI backend:**
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Streamlit frontend:**
   ```bash
   streamlit run streamlit_app.py
   ```
   The web interface will be available at `http://localhost:8501`

### Quick Start Example

```python
import requests

# Generate a loan agreement
response = requests.post("http://localhost:8000/api/v1/draft-document", json={
    "document_type": "loan_agreement",
    "prompt": "Draft a loan agreement for ₹5,00,000 between John Doe (Lender) and Jane Smith (Borrower), 12 months tenure, 10% interest",
    "variables": {
        "lender_name": "John Doe",
        "borrower_name": "Jane Smith",
        "amount": "₹5,00,000",
        "interest_rate": "10",
        "tenure": "12"
    },
    "jurisdiction": "IN"
})

document = response.json()
```

## 📚 API Documentation

### Main Endpoints

- **POST** `/api/v1/draft-document` - Generate a legal document
- **GET** `/api/v1/document-types` - List available document types
- **POST** `/api/v1/validate-prompt` - Validate document generation prompt
- **GET** `/api/v1/download/{document_id}` - Download generated document

### Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger documentation.

## 🖥️ Web Interface

The Streamlit web interface provides:

- **Document Generator**: Interactive form for document creation
- **Templates**: Pre-built document templates
- **History**: View previously generated documents
- **Help**: User guide and troubleshooting
- **Settings**: Application configuration

### Features:

- Real-time API status monitoring
- Form validation and error handling
- Document preview and download
- Multi-step document generation workflow

## 📄 Document Types

### Supported Document Types

1. **Loan Agreements** (`loan_agreement`)
   - Personal and business loans
   - Customizable interest rates and terms
   - Repayment schedules
   - Security and collateral clauses

2. **Rental Agreements** (`rental_agreement`)
   - Residential and commercial properties
   - Lease terms and conditions
   - Rent and security deposit details
   - Maintenance responsibilities

3. **Service Agreements** (`service_agreement`)
   - Professional service contracts
   - Scope of work and deliverables
   - Payment terms and milestones
   - Intellectual property clauses

4. **Non-Disclosure Agreements** (`nda`)
   - Mutual and one-way NDAs
   - Confidential information definitions
   - Term and survival provisions
   - Remedies and enforcement

## ⚙️ Configuration

### Environment Variables

```env
# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-3.5-turbo

# RAG Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
FAISS_INDEX_PATH=data/embeddings/legal_clauses/index.faiss

# Application Settings
DEFAULT_JURISDICTION=IN
MAX_PROMPT_LENGTH=5000
DOCUMENT_OUTPUT_DIR=generated_documents

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Customization

- **Add new document types**: Modify `llm/prompt_templates.py`
- **Custom legal clauses**: Add to `data/legal_clauses/`
- **UI customization**: Edit `streamlit_app.py` and `streamlit_components.py`

## 🛠️ Development

### Project Structure

- **Backend**: FastAPI with async support
- **Frontend**: Streamlit for rapid prototyping
- **LLM Integration**: OpenAI GPT models with custom prompts
- **RAG System**: FAISS vector database with sentence transformers
- **Document Generation**: Python-docx for DOCX creation

### Development Commands

```bash
# Run tests
python -m pytest tests/

# Run with auto-reload
uvicorn main:app --reload

# Format code
black .
isort .

# Type checking
mypy .
```

### Adding New Document Types

1. Add prompt template in `llm/prompt_templates.py`
2. Create document builder in `main.py`
3. Add validation in `api/schemas.py`
4. Update frontend in `streamlit_app.py`

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_api.py -v
```

### Test Coverage

- API endpoint testing
- LLM integration tests
- Document generation validation
- RAG pipeline functionality


### Code Style

- Follow PEP 8 conventions
- Use type hints where possible
- Write comprehensive docstrings
- Add tests for new features


