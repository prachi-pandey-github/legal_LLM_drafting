"""
LLM model handler for document generation
"""
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

from config import Config
from llm.prompt_templates import generate_prompt
from llm.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)

class LLMHandler:
    """Handler for LLM interactions"""
    
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
        self.initialize_llm()
    
    def initialize_llm(self):
        """Initialize LLM based on configuration"""
        self.llm_provider = Config.LLM_PROVIDER
        
        if self.llm_provider == "openai":
            self.initialize_openai()
        elif self.llm_provider == "llama":
            self.initialize_llama()
        elif self.llm_provider == "mistral":
            self.initialize_mistral()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def initialize_openai(self):
        """Initialize OpenAI client"""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
        
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        logger.info(f"Initialized OpenAI with model: {self.model}")
    
    def initialize_llama(self):
        """Initialize Llama model (local)"""
        # This is a placeholder for local Llama setup
        # In practice, you would use Ollama, llama.cpp, or similar
        logger.info("Initializing Llama model (local)")
        self.model = Config.LOCAL_MODEL_PATH
        # Add actual initialization code here
    
    def initialize_mistral(self):
        """Initialize Mistral model"""
        # Placeholder for Mistral AI integration
        logger.info("Initializing Mistral model")
        # Add actual initialization code here
    
    async def generate_document(self, prompt: str, doc_type: Optional[str] = None, 
                              variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a legal document using LLM with RAG
        
        Args:
            prompt: User prompt describing the document
            doc_type: Type of document to generate
            variables: Structured variables for document
        
        Returns:
            Dictionary containing document structure
        """
        try:
            logger.info(f"Generating document of type: {doc_type}")
            
            # Extract document type from prompt if not specified
            if not doc_type:
                doc_type = self.detect_document_type(prompt)
            
            # Retrieve relevant clauses using RAG
            relevant_clauses = self.rag_pipeline.retrieve_relevant_clauses(
                query=prompt,
                document_type=doc_type,
                jurisdiction=variables.get("jurisdiction", "IN") if variables else "IN"
            )
            
            # Format clauses for prompt
            clauses_context = self.rag_pipeline.format_clauses_for_prompt(relevant_clauses)
            
            # Prepare variables
            if variables is None:
                variables = {}
            variables["relevant_clauses"] = clauses_context
            
            # Generate prompts
            system_prompt, user_prompt = generate_prompt(doc_type, variables, prompt)
            
            # Call LLM
            document_structure = await self.call_llm(system_prompt, user_prompt)
            
            # Parse and validate response
            parsed_document = self.parse_llm_response(document_structure)
            
            # Add metadata
            parsed_document["metadata"] = {
                "document_type": doc_type,
                "generated_with": self.llm_provider,
                "rag_used": len(relevant_clauses) > 0,
                "clauses_retrieved": len(relevant_clauses)
            }
            
            logger.info(f"Document generated successfully: {parsed_document.get('title', 'Unknown')}")
            return parsed_document
            
        except Exception as e:
            logger.error(f"Failed to generate document: {str(e)}")
            raise
    
    async def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the LLM with given prompts"""
        try:
            if self.llm_provider == "openai":
                return await self.call_openai(system_prompt, user_prompt)
            elif self.llm_provider == "llama":
                return await self.call_llama(system_prompt, user_prompt)
            elif self.llm_provider == "mistral":
                return await self.call_mistral(system_prompt, user_prompt)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise
    
    async def call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent legal documents
                max_tokens=4000,
                response_format={"type": "json_object"}  # Request JSON response
            )
            
            content = response.choices[0].message.content
            logger.info(f"OpenAI response received: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            # Fallback to simpler generation
            return self.generate_fallback_document(system_prompt, user_prompt)
    
    async def call_llama(self, system_prompt: str, user_prompt: str) -> str:
        """Call local Llama model"""
        # Placeholder implementation
        # In practice, use Ollama, llama.cpp, or similar
        logger.info("Calling Llama model (placeholder)")
        
        # Simulate response
        fallback_response = self.generate_fallback_document(system_prompt, user_prompt)
        return json.dumps(fallback_response)
    
    async def call_mistral(self, system_prompt: str, user_prompt: str) -> str:
        """Call Mistral AI API"""
        # Placeholder implementation
        logger.info("Calling Mistral model (placeholder)")
        
        # Simulate response
        fallback_response = self.generate_fallback_document(system_prompt, user_prompt)
        return json.dumps(fallback_response)
    
    def generate_fallback_document(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate a fallback document if LLM fails"""
        logger.warning("Using fallback document generation")
        
        # Extract key information from prompts
        document_type = "legal_agreement"
        if "loan" in user_prompt.lower():
            document_type = "loan_agreement"
        elif "rent" in user_prompt.lower():
            document_type = "rental_agreement"
        elif "service" in user_prompt.lower():
            document_type = "service_agreement"
        elif "nda" in user_prompt.lower() or "non-disclosure" in user_prompt.lower():
            document_type = "nda"
        
        return {
            "title": f"{document_type.replace('_', ' ').title()}",
            "sections": [
                {
                    "type": "heading",
                    "title": "Agreement",
                    "content": f"This is a {document_type.replace('_', ' ')} generated by the Legal Drafting System.",
                    "level": 1
                },
                {
                    "type": "clause",
                    "title": "Parties",
                    "content": "This agreement is made between the parties as described in the user prompt."
                },
                {
                    "type": "clause",
                    "title": "Terms and Conditions",
                    "content": "The terms and conditions shall be as mutually agreed upon by the parties."
                },
                {
                    "type": "clause",
                    "title": "Governing Law",
                    "content": "This agreement shall be governed by the applicable laws."
                }
            ],
            "parties": [
                {"name": "Party A", "role": "First Party"},
                {"name": "Party B", "role": "Second Party"}
            ]
        }
    
    def parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured document"""
        try:
            # Try to parse as JSON
            parsed = json.loads(response_text)
            
            # Validate structure
            if not isinstance(parsed, dict):
                raise ValueError("Response is not a JSON object")
            
            # Ensure required fields
            if "title" not in parsed:
                parsed["title"] = "Legal Agreement"
            
            if "sections" not in parsed or not isinstance(parsed["sections"], list):
                parsed["sections"] = []
            
            if "parties" not in parsed or not isinstance(parsed["parties"], list):
                parsed["parties"] = []
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {str(e)}")
            
            # Try to extract structure from plain text
            return self.parse_text_response(response_text)
    
    def parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse plain text response into structure"""
        lines = text.strip().split('\n')
        sections = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect headings
            if line.startswith('# '):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "type": "heading",
                    "title": line[2:],
                    "content": "",
                    "level": 1
                }
            elif line.startswith('## '):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "type": "heading",
                    "title": line[3:],
                    "content": "",
                    "level": 2
                }
            elif line.startswith('### '):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "type": "heading",
                    "title": line[4:],
                    "content": "",
                    "level": 3
                }
            elif current_section:
                if current_section["content"]:
                    current_section["content"] += "\n" + line
                else:
                    current_section["content"] = line
            else:
                # Start a new paragraph section
                current_section = {
                    "type": "paragraph",
                    "content": line
                }
        
        if current_section:
            sections.append(current_section)
        
        return {
            "title": "Legal Document",
            "sections": sections,
            "parties": []
        }
    
    def detect_document_type(self, prompt: str) -> str:
        """Detect document type from prompt text"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["loan", "lender", "borrower", "interest rate"]):
            return "loan_agreement"
        elif any(word in prompt_lower for word in ["rent", "landlord", "tenant", "lease", "property"]):
            return "rental_agreement"
        elif any(word in prompt_lower for word in ["service", "provider", "client", "deliverables"]):
            return "service_agreement"
        elif any(word in prompt_lower for word in ["nda", "non-disclosure", "confidential", "proprietary"]):
            return "nda"
        elif any(word in prompt_lower for word in ["employment", "employee", "employer", "salary"]):
            return "employment_contract"
        elif any(word in prompt_lower for word in ["partnership", "partners", "business", "share"]):
            return "partnership_deed"
        elif any(word in prompt_lower for word in ["affidavit", "sworn", "declare", "oath"]):
            return "affidavit"
        else:
            return "other"
