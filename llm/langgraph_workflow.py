"""
LangGraph workflow for multi-step document generation
"""
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)

class DocumentGenerationState:
    """State for document generation workflow"""
    def __init__(self):
        self.prompt = ""
        self.document_type = ""
        self.variables = {}
        self.retrieved_clauses = []
        self.document_structure = {}
        self.generated_content = ""
        self.final_document = {}

# Define workflow states
class DocumentGenerationWorkflow:
    """Multi-step document generation workflow using LangGraph"""
    
    def __init__(self, llm_handler, rag_pipeline):
        self.llm_handler = llm_handler
        self.rag_pipeline = rag_pipeline
        self.workflow = self.create_workflow()
    
    def create_workflow(self):
        """Create the LangGraph workflow"""
        workflow = StateGraph(DocumentGenerationState)
        
        # Add nodes
        workflow.add_node("analyze_prompt", self.analyze_prompt)
        workflow.add_node("retrieve_clauses", self.retrieve_clauses)
        workflow.add_node("generate_outline", self.generate_outline)
        workflow.add_node("generate_content", self.generate_content)
        workflow.add_node("review_document", self.review_document)
        workflow.add_node("finalize_document", self.finalize_document)
        
        # Define edges
        workflow.set_entry_point("analyze_prompt")
        workflow.add_edge("analyze_prompt", "retrieve_clauses")
        workflow.add_edge("retrieve_clauses", "generate_outline")
        workflow.add_edge("generate_outline", "generate_content")
        workflow.add_edge("generate_content", "review_document")
        workflow.add_edge("review_document", "finalize_document")
        workflow.add_edge("finalize_document", END)
        
        # Add conditional edges for review
        workflow.add_conditional_edges(
            "review_document",
            self.should_revise,
            {
                "revise": "generate_content",
                "approve": "finalize_document"
            }
        )
        
        return workflow.compile()
    
    async def analyze_prompt(self, state: DocumentGenerationState) -> Dict[str, Any]:
        """Step 1: Analyze the user prompt"""
        logger.info("Step 1: Analyzing prompt")
        
        # Extract document type
        state.document_type = self.llm_handler.detect_document_type(state.prompt)
        
        # Extract variables (simplified)
        # In production, use more sophisticated NLP
        if "loan" in state.prompt.lower():
            # Extract loan-specific variables
            import re
            amount_match = re.search(r'₹?(\d+[,\d]*)', state.prompt)
            if amount_match:
                state.variables["amount"] = amount_match.group(1)
        
        logger.info(f"Detected document type: {state.document_type}")
        return {"document_type": state.document_type, "variables": state.variables}
    
    async def retrieve_clauses(self, state: DocumentGenerationState) -> Dict[str, Any]:
        """Step 2: Retrieve relevant legal clauses"""
        logger.info("Step 2: Retrieving legal clauses")
        
        clauses = self.rag_pipeline.retrieve_relevant_clauses(
            query=state.prompt,
            document_type=state.document_type,
            jurisdiction=state.variables.get("jurisdiction", "IN")
        )
        
        state.retrieved_clauses = clauses
        logger.info(f"Retrieved {len(clauses)} clauses")
        return {"retrieved_clauses": clauses}
    
    async def generate_outline(self, state: DocumentGenerationState) -> Dict[str, Any]:
        """Step 3: Generate document outline"""
        logger.info("Step 3: Generating document outline")
        
        # Prepare prompt for outline generation
        outline_prompt = f"""
        Generate a comprehensive outline for a {state.document_type} based on:
        
        User Requirements: {state.prompt}
        Retrieved Clauses: {len(state.retrieved_clauses)} relevant clauses found
        
        The outline should include:
        1. Title
        2. Preamble/Introduction
        3. Definitions (if needed)
        4. Main clauses and sections
        5. Standard legal clauses (termination, governing law, etc.)
        6. Signature blocks
        
        Return the outline as a structured JSON with section titles and brief descriptions.
        """
        
        # Call LLM for outline
        # This is simplified - in production, use actual LLM call
        outline = {
            "title": f"{state.document_type.replace('_', ' ').title()}",
            "sections": [
                {"title": "Parties", "description": "Identification of parties"},
                {"title": "Terms", "description": "Main terms and conditions"},
                {"title": "Obligations", "description": "Rights and obligations"},
                {"title": "Termination", "description": "Termination conditions"},
                {"title": "Governing Law", "description": "Applicable law and jurisdiction"},
                {"title": "Signatures", "description": "Signature blocks"}
            ]
        }
        
        state.document_structure = outline
        return {"document_structure": outline}
    
    async def generate_content(self, state: DocumentGenerationState) -> Dict[str, Any]:
        """Step 4: Generate detailed content for each section"""
        logger.info("Step 4: Generating document content")
        
        # This would use the LLM to generate content for each section
        # For now, use simplified content
        sections = []
        for section in state.document_structure.get("sections", []):
            sections.append({
                "type": "clause",
                "title": section["title"],
                "content": f"This section covers {section['description']}. Specific terms to be filled based on user requirements."
            })
        
        state.generated_content = {
            "title": state.document_structure["title"],
            "sections": sections
        }
        
        return {"generated_content": state.generated_content}
    
    async def review_document(self, state: DocumentGenerationState) -> Dict[str, Any]:
        """Step 5: Review and validate the generated document"""
        logger.info("Step 5: Reviewing document")
        
        # Check if document is complete
        content = state.generated_content
        is_complete = (
            content and
            "title" in content and
            "sections" in content and
            len(content["sections"]) > 0
        )
        
        # Check for placeholders
        has_placeholders = any(
            "placeholder" in str(section).lower() or 
            "fill" in str(section).lower() or
            "specific" in str(section).lower()
            for section in content.get("sections", [])
        )
        
        review_result = {
            "is_complete": is_complete,
            "has_placeholders": has_placeholders,
            "sections_count": len(content.get("sections", [])),
            "needs_revision": has_placeholders or not is_complete
        }
        
        return {"review_result": review_result}
    
    def should_revise(self, state: DocumentGenerationState) -> str:
        """Determine if document needs revision"""
        review_result = getattr(state, "review_result", {})
        
        if review_result.get("needs_revision", True):
            return "revise"
        else:
            return "approve"
    
    async def finalize_document(self, state: DocumentGenerationState) -> Dict[str, Any]:
        """Step 6: Finalize the document"""
        logger.info("Step 6: Finalizing document")
        
        # Add metadata and final touches
        final_doc = state.generated_content.copy()
        final_doc["metadata"] = {
            "generated_by": "LangGraph Workflow",
            "workflow_steps": 6,
            "clauses_used": len(state.retrieved_clauses),
            "document_type": state.document_type
        }
        
        # Add parties if not present
        if "parties" not in final_doc:
            final_doc["parties"] = [
                {"name": "Party A", "role": "First Party"},
                {"name": "Party B", "role": "Second Party"}
            ]
        
        state.final_document = final_doc
        return {"final_document": final_doc}
    
    async def run(self, prompt: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the complete workflow"""
        logger.info(f"Starting document generation workflow for prompt: {prompt[:50]}...")
        
        # Initialize state
        state = DocumentGenerationState()
        state.prompt = prompt
        state.variables = variables or {}
        
        # Run workflow
        try:
            result = await self.workflow.ainvoke(state)
            return result.get("final_document", {})
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            raise