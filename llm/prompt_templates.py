"""
Prompt templates for different legal document types
"""

PROMPT_TEMPLATES = {
    "loan_agreement": {
        "system": """You are an expert legal drafter specializing in loan agreements. 
        Generate professional, legally sound loan agreements based on the provided information.
        Ensure compliance with relevant laws and include all necessary clauses for enforceability.""",
        
        "user": """Draft a comprehensive Loan Agreement with the following details:

**PARTIES:**
- Lender: {lender_name}
- Borrower: {borrower_name}
- Lender Address: {lender_address}
- Borrower Address: {borrower_address}

**LOAN TERMS:**
- Principal Amount: {amount}
- Interest Rate: {interest_rate}% per annum
- Loan Term: {tenure} months
- Repayment Schedule: {repayment_frequency}
- Purpose of Loan: {purpose}
- Disbursement Date: {disbursement_date}

**ADDITIONAL TERMS:**
{additional_terms}

**JURISDICTION:** {jurisdiction}

**RELEVANT CLAUSES:**
{relevant_clauses}

**INSTRUCTIONS:**
1. Generate a complete, professionally formatted loan agreement
2. Include all standard clauses: Preamble, Definitions, Loan Terms, Interest, Repayment, Default, Representations & Warranties, Governing Law, Jurisdiction, Signatures
3. Use clear, unambiguous legal language
4. Include appropriate placeholders: [DATE], [PLACE], [SIGNATURE]
5. Ensure the document is ready for execution
6. Number all clauses and sub-clauses appropriately
7. Include a definitions section for key terms

**OUTPUT FORMAT:**
Return a JSON object with:
- title: Document title
- sections: List of sections, each with type, title, and content
- parties: List of parties with name and role
- metadata: Document metadata""",
        
        "variables": [
            "lender_name", "borrower_name", "amount", "interest_rate", 
            "tenure", "repayment_frequency", "purpose", "jurisdiction"
        ]
    },
    
    "rental_agreement": {
        "system": """You are a legal expert specializing in rental and lease agreements.
        Draft comprehensive rental agreements that protect both landlord and tenant interests.""",
        
        "user": """Draft a detailed Rental Agreement with:

**PROPERTY DETAILS:**
- Address: {property_address}
- Type: {property_type}
- Furnishing: {furnishing_status}

**PARTIES:**
- Landlord: {landlord_name}
- Tenant: {tenant_name}
- Landlord Address: {landlord_address}
- Tenant Address: {tenant_address}

**LEASE TERMS:**
- Monthly Rent: {rent_amount}
- Security Deposit: {security_deposit}
- Lease Term: {lease_term}
- Commencement Date: {start_date}
- Utilities Responsibility: {utilities_responsibility}
- Maintenance Responsibility: {maintenance_responsibility}

**SPECIAL CONDITIONS:**
{special_conditions}

**JURISDICTION:** {jurisdiction}

**RELEVANT CLAUSES:**
{relevant_clauses}

**INSTRUCTIONS:**
1. Include clauses for: Parties, Property Description, Term, Rent, Security Deposit, Maintenance, Utilities, Entry Rights, Termination, Renewal, Dispute Resolution
2. Add schedules for inventory and condition report
3. Include notice periods and procedures
4. Add landlord and tenant obligations""",
        
        "variables": [
            "landlord_name", "tenant_name", "property_address", "rent_amount",
            "security_deposit", "lease_term", "start_date", "jurisdiction"
        ]
    },
    
    "service_agreement": {
        "system": """You are a legal professional drafting service agreements.
        Create clear agreements that define scope, deliverables, and terms of service.""",
        
        "user": """Draft a Service Agreement with:

**SERVICE DETAILS:**
- Service Provider: {service_provider}
- Client: {client_name}
- Services: {services_description}
- Scope of Work: {scope_of_work}
- Deliverables: {deliverables}
- Timeline: {timeline}

**FINANCIAL TERMS:**
- Service Fee: {service_fee}
- Payment Terms: {payment_terms}
- Expenses: {expenses_handling}

**TERMS & CONDITIONS:**
- Term: {agreement_term}
- Termination: {termination_conditions}
- Confidentiality: {confidentiality_required}
- Intellectual Property: {ip_ownership}

**JURISDICTION:** {jurisdiction}

**INSTRUCTIONS:**
1. Include clauses for: Services, Compensation, Term, Termination, Confidentiality, IP, Liability, Insurance, Dispute Resolution
2. Define clear deliverables and acceptance criteria
3. Include change order procedures
4. Add force majeure clause""",
        
        "variables": [
            "service_provider", "client_name", "services_description", 
            "service_fee", "agreement_term", "jurisdiction"
        ]
    },
    
    "nda": {
        "system": """You are drafting Non-Disclosure Agreements to protect confidential information.
        Create balanced NDAs that protect interests while being fair to both parties.""",
        
        "user": """Draft a Mutual Non-Disclosure Agreement with:

**PARTIES:**
- Disclosing Party: {disclosing_party}
- Receiving Party: {receiving_party}

**CONFIDENTIAL INFORMATION:**
- Type of Information: {information_type}
- Purpose of Disclosure: {purpose}
- Exclusions: {exclusions}

**TERMS:**
- Term Duration: {term_duration}
- Return of Information: {return_provisions}
- Remedies: {remedies}

**JURISDICTION:** {jurisdiction}

**INSTRUCTIONS:**
1. Define confidential information clearly
2. Include obligations of receiving party
3. Specify exclusions from confidentiality
4. Include term and survival provisions
5. Add dispute resolution and governing law""",
        
        "variables": [
            "disclosing_party", "receiving_party", "information_type",
            "purpose", "term_duration", "jurisdiction"
        ]
    }
}

# Default template for unspecified document types
DEFAULT_TEMPLATE = {
    "system": """You are an expert legal drafter. Generate professional legal documents based on the user's requirements.""",
    
    "user": """Draft a legal document based on the following description:

{user_prompt}

**ADDITIONAL CONTEXT:**
Jurisdiction: {jurisdiction}
Variables: {variables}

**INSTRUCTIONS:**
1. Create a comprehensive legal document
2. Include appropriate sections and clauses
3. Use professional legal language
4. Include placeholders for signatures and dates
5. Ensure document is structured properly and everthing is in one page

**OUTPUT FORMAT:**
Return a JSON object with:
- title: Document title
- sections: List of sections with type, title, and content
- parties: List of parties involved
- metadata: Any relevant metadata""",
    
    "variables": ["jurisdiction"]
}

def get_template_for_type(doc_type: str):
    """Get prompt template for document type"""
    return PROMPT_TEMPLATES.get(doc_type, DEFAULT_TEMPLATE)

def generate_prompt(doc_type: str, variables: dict, user_prompt: str = "") -> tuple[str, str]:
    """Generate system and user prompts for LLM"""
    template = get_template_for_type(doc_type)
    
    # Prepare variables with defaults
    prompt_vars = variables.copy()
    prompt_vars["user_prompt"] = user_prompt
    
    # Add default values for common missing variables
    defaults = {
        "lender_address": "[TO BE FILLED]",
        "borrower_address": "[TO BE FILLED]", 
        "property_type": "[TO BE SPECIFIED]",
        "furnishing_status": "[TO BE SPECIFIED]",
        "landlord_address": "[TO BE FILLED]",
        "tenant_address": "[TO BE FILLED]",
        "security_deposit": "[TO BE SPECIFIED]",
        "lease_term": "[TO BE SPECIFIED]",
        "start_date": "[TO BE FILLED]",
        "utilities_responsibility": "[TO BE SPECIFIED]",
        "maintenance_responsibility": "[TO BE SPECIFIED]",
        "special_conditions": "[NONE SPECIFIED]",
        "repayment_frequency": "Monthly",
        "purpose": "[TO BE SPECIFIED]",
        "disbursement_date": "[TO BE FILLED]",
        "additional_terms": "[NONE SPECIFIED]",
        "relevant_clauses": "No relevant clauses found in database."
    }
    
    # Fill in missing variables with defaults
    for key, default_value in defaults.items():
        if key not in prompt_vars:
            prompt_vars[key] = default_value
    
    # Fill in template
    system_prompt = template["system"]
    try:
        user_prompt_filled = template["user"].format(**prompt_vars)
    except KeyError as e:
        # If still missing variables, use fallback template
        fallback_template = f"""Draft a {doc_type.replace('_', ' ')} document based on:

User Request: {user_prompt}

Provided Information:
{chr(10).join([f"- {k}: {v}" for k, v in variables.items()])}

Jurisdiction: {variables.get('jurisdiction', 'IN')}

Relevant Clauses:
{variables.get('relevant_clauses', 'None found')}

Please generate a comprehensive legal document with appropriate sections and clauses."""
        user_prompt_filled = fallback_template
    
    return system_prompt, user_prompt_filled