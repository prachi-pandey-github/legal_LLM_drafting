"""
RAG (Retrieval-Augmented Generation) pipeline for legal clauses
"""
import json
import os
from typing import List, Dict, Any
import logging

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import chromadb
from chromadb.config import Settings

from config import Config

logger = logging.getLogger(__name__)

class RAGPipeline:
    """RAG pipeline for legal document generation"""
    
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.chroma_client = None
        self.collection = None
        self.embeddings = None
        
        # Initialize in background or skip if offline
        try:
            self.initialize_embeddings()
            self.initialize_vector_store()
        except Exception as e:
            logger.warning(f"Could not initialize embeddings/vector store: {e}")
            logger.info("Running in offline mode without RAG capabilities")
    
    def initialize_embeddings(self):
        """Initialize embedding model"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=Config.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': False}
            )
            logger.info(f"Initialized embeddings with model: {Config.EMBEDDING_MODEL}")
        except Exception as e:
            logger.warning(f"Failed to initialize HuggingFace embeddings: {str(e)}")
            logger.info("Falling back to dummy embeddings for offline mode")
            self.embeddings = None
            # Set a flag to indicate we're in offline mode
            self._offline_mode = True
    
    def initialize_vector_store(self):
        """Initialize vector store for legal clauses"""
        if hasattr(self, '_offline_mode') and self._offline_mode:
            logger.info("Running in offline mode - vector store disabled")
            self.vector_store = None
            return
            
        try:
            # Try to load existing vector store
            if os.path.exists(Config.VECTOR_STORE_PATH) and self.embeddings:
                logger.info(f"Loading existing vector store from {Config.VECTOR_STORE_PATH}")
                self.vector_store = FAISS.load_local(
                    Config.VECTOR_STORE_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                logger.info("Creating new vector store")
                self.create_vector_store()
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            logger.info("Running without vector store")
            self.vector_store = None
    
    def load_legal_clauses(self) -> List[Dict[str, Any]]:
        """Load legal clauses from JSON files"""
        clauses = []
        clause_dir = Config.CLAUSE_DATABASE_PATH
        
        if not os.path.exists(clause_dir):
            logger.warning(f"Clause directory not found: {clause_dir}")
            return self.get_default_clauses()
        
        for filename in os.listdir(clause_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(clause_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_clauses = json.load(f)
                        if isinstance(file_clauses, list):
                            clauses.extend(file_clauses)
                        else:
                            clauses.append(file_clauses)
                    logger.info(f"Loaded clauses from {filename}")
                except Exception as e:
                    logger.error(f"Error loading {filename}: {str(e)}")
        
        return clauses
    
    def get_default_clauses(self) -> List[Dict[str, Any]]:
        """Get default legal clauses if no files are found"""
        logger.info("Loading default legal clauses")
        
        default_clauses = [
            {
                "id": "loan_interest_1",
                "document_type": "loan_agreement",
                "clause_title": "Interest Calculation",
                "clause_content": "Interest on the Loan Amount shall be calculated on a monthly basis at the rate specified in Clause [X] and shall be payable along with the principal repayment.",
                "jurisdiction": "IN",
                "keywords": ["interest", "calculation", "monthly"]
            },
            {
                "id": "loan_repayment_1",
                "document_type": "loan_agreement",
                "clause_title": "Repayment Schedule",
                "clause_content": "The Borrower shall repay the Loan Amount in [NUMBER] equal monthly installments of [AMOUNT] each, commencing from [DATE], and on the same date of each succeeding month.",
                "jurisdiction": "IN",
                "keywords": ["repayment", "installments", "schedule"]
            },
            {
                "id": "rental_deposit_1",
                "document_type": "rental_agreement",
                "clause_title": "Security Deposit",
                "clause_content": "The Tenant has deposited a sum of [AMOUNT] as security deposit, which shall be refundable at the termination of this agreement, subject to deduction for any damages or outstanding dues.",
                "jurisdiction": "IN",
                "keywords": ["security", "deposit", "refundable"]
            },
            {
                "id": "termination_1",
                "document_type": "general",
                "clause_title": "Termination Clause",
                "clause_content": "Either party may terminate this agreement by giving [NUMBER] days' written notice to the other party. In case of material breach, the non-breaching party may terminate immediately upon written notice.",
                "jurisdiction": "general",
                "keywords": ["termination", "notice", "breach"]
            },
            {
                "id": "governing_law_1",
                "document_type": "general",
                "clause_title": "Governing Law and Jurisdiction",
                "clause_content": "This agreement shall be governed by and construed in accordance with the laws of [JURISDICTION]. Any disputes arising under this agreement shall be subject to the exclusive jurisdiction of the courts in [CITY/STATE].",
                "jurisdiction": "general",
                "keywords": ["governing", "law", "jurisdiction"]
            }
        ]
        
        return default_clauses
    
    def create_vector_store(self):
        """Create and populate vector store with legal clauses"""
        try:
            # Load clauses
            clauses = self.load_legal_clauses()
            
            if not clauses:
                logger.warning("No clauses loaded, using default clauses")
                clauses = self.get_default_clauses()
            
            # Prepare documents for embedding
            documents = []
            for clause in clauses:
                # Combine relevant information for embedding
                content = f"""
                Document Type: {clause.get('document_type', 'general')}
                Clause Title: {clause.get('clause_title', '')}
                Content: {clause.get('clause_content', '')}
                Jurisdiction: {clause.get('jurisdiction', 'general')}
                Keywords: {', '.join(clause.get('keywords', []))}
                """
                
                metadata = {
                    "document_type": clause.get("document_type", "general"),
                    "clause_title": clause.get("clause_title", ""),
                    "jurisdiction": clause.get("jurisdiction", "general"),
                    "clause_id": clause.get("id", ""),
                    "keywords": ", ".join(clause.get("keywords", []))
                }
                
                documents.append(Document(
                    page_content=content.strip(),
                    metadata=metadata
                ))
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            split_docs = text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")
            
            # Create vector store
            self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
            
            # Save vector store
            os.makedirs(os.path.dirname(Config.VECTOR_STORE_PATH), exist_ok=True)
            self.vector_store.save_local(Config.VECTOR_STORE_PATH)
            logger.info(f"Saved vector store to {Config.VECTOR_STORE_PATH}")
            
        except Exception as e:
            logger.error(f"Failed to create vector store: {str(e)}")
            raise
    
    def retrieve_relevant_clauses(self, query: str, document_type: str = None, 
                                 jurisdiction: str = "IN", k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant legal clauses based on query
        
        Args:
            query: Search query
            document_type: Type of document (optional filter)
            jurisdiction: Legal jurisdiction (optional filter)
            k: Number of results to return
        
        Returns:
            List of relevant clauses with metadata
        """
        try:
            if not self.vector_store:
                logger.warning("Vector store not available - running in offline mode")
                # Return some default/sample clauses for offline mode
                return self._get_default_clauses(document_type)
            
            # Enhance query with context
            enhanced_query = f"""
            Legal document generation query:
            {query}
            Document Type: {document_type or 'Not specified'}
            Jurisdiction: {jurisdiction}
            """
            
            # Perform similarity search
            docs = self.vector_store.similarity_search(enhanced_query, k=k)
            
            # Process results
            results = []
            for doc in docs:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 1.0  # FAISS doesn't return scores by default
                }
                
                # Apply filters if specified
                if document_type and doc.metadata.get("document_type") != document_type:
                    continue
                if jurisdiction and doc.metadata.get("jurisdiction") not in [jurisdiction, "general"]:
                    continue
                
                results.append(result)
            
            logger.info(f"Retrieved {len(results)} relevant clauses for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving clauses: {str(e)}")
            return []
    
    def format_clauses_for_prompt(self, clauses: List[Dict[str, Any]]) -> str:
        """Format retrieved clauses for inclusion in LLM prompt"""
        if not clauses:
            return "No relevant clauses found in database."
        
        formatted = "RELEVANT LEGAL CLAUSES FROM DATABASE:\n\n"
        
        for i, clause in enumerate(clauses, 1):
            metadata = clause.get("metadata", {})
            content = clause.get("content", "")
            
            formatted += f"CLAUSE {i}:\n"
            formatted += f"Title: {metadata.get('clause_title', 'N/A')}\n"
            formatted += f"Document Type: {metadata.get('document_type', 'N/A')}\n"
            formatted += f"Jurisdiction: {metadata.get('jurisdiction', 'N/A')}\n"
            formatted += f"Content:\n{content}\n"
            formatted += "-" * 50 + "\n\n"
        
        return formatted
    
    def add_clause_to_database(self, clause_data: Dict[str, Any]):
        """Add a new clause to the database"""
        try:
            # Load existing clauses
            clauses = self.load_legal_clauses()
            
            # Add new clause
            clauses.append(clause_data)
            
            # Save back to appropriate file
            doc_type = clause_data.get("document_type", "general")
            filename = f"{doc_type}_clauses.json"
            filepath = os.path.join(Config.CLAUSE_DATABASE_PATH, filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Load existing file content if exists
            existing_clauses = []
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_clauses = json.load(f)
            
            # Add new clause
            existing_clauses.append(clause_data)
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_clauses, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Added new clause to {filename}")
            
            # Recreate vector store to include new clause
            self.create_vector_store()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add clause to database: {str(e)}")
            return False
    
    def _get_default_clauses(self, document_type: str = None) -> List[Dict[str, Any]]:
        """Return default clauses for offline mode"""
        default_clauses = [
            {
                "id": "default_1",
                "type": "introduction",
                "content": "This agreement is entered into between the parties for the purpose of establishing legal obligations.",
                "document_types": ["general_agreement", "service_agreement"],
                "jurisdiction": "IN",
                "metadata": {"source": "default_offline"}
            },
            {
                "id": "default_2", 
                "type": "terms_conditions",
                "content": "The parties agree to the following terms and conditions as outlined herein.",
                "document_types": ["general_agreement"],
                "jurisdiction": "IN",
                "metadata": {"source": "default_offline"}
            },
            {
                "id": "default_3",
                "type": "payment",
                "content": "Payment terms shall be as mutually agreed upon by both parties.",
                "document_types": ["service_agreement", "loan_agreement"],
                "jurisdiction": "IN", 
                "metadata": {"source": "default_offline"}
            }
        ]
        
        # Filter by document type if provided
        if document_type:
            filtered_clauses = [
                clause for clause in default_clauses 
                if document_type in clause.get("document_types", [])
            ]
            return filtered_clauses if filtered_clauses else default_clauses[:2]
        
        return default_clauses