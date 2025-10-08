"""
Prompt templates for LLM operations.

This module provides pre-defined prompt templates for common EGRC operations
including document analysis, risk assessment, and compliance checking.
"""

from typing import Any


class PromptTemplate:
    """Base class for prompt templates."""

    def __init__(self, name: str, template: str, variables: list[str]):
        """
        Initialize prompt template.

        Args:
            name: Template name
            template: Template string with placeholders
            variables: List of required variables
        """
        self.name = name
        self.template = template
        self.variables = variables

    def format(self, **kwargs: Any) -> str:
        """
        Format template with provided variables.

        Args:
            **kwargs: Template variables

        Returns:
            Formatted prompt

        Raises:
            ValueError: If required variables are missing
        """
        missing_vars = [var for var in self.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        return self.template.format(**kwargs)


# System Prompts
SYSTEM_PROMPTS = {
    "compliance_expert": PromptTemplate(
        name="compliance_expert",
        template="""You are a compliance expert specializing in enterprise governance,
             risk,
             and compliance (EGRC) operations.
Your role is to analyze documents, assess risks, and provide recommendations for
compliance with various regulations including GDPR, SOX, HIPAA, and industry standards.

Key responsibilities:
- Analyze documents for compliance issues
- Identify potential risks and vulnerabilities
- Provide actionable recommendations
- Ensure accuracy and thoroughness in assessments
- Consider both technical and business implications

Always provide clear, structured responses with specific recommendations.""",
        variables=[],
    ),
    "risk_assessor": PromptTemplate(
        name="risk_assessor",
        template="""You are a risk assessment expert with deep knowledge of enterprise risk management frameworks.
Your expertise includes identifying, analyzing, and evaluating risks across various business domains.

Key responsibilities:
- Assess risk levels and impact
- Identify risk factors and root causes
- Evaluate control effectiveness
- Provide risk mitigation strategies
- Consider both quantitative and qualitative factors

Always provide structured risk assessments with clear recommendations for mitigation.""",
        variables=[],
    ),
    "document_analyst": PromptTemplate(
        name="document_analyst",
        template="""You are a document analysis specialist focused on extracting insights from business documents.
Your role is to analyze documents for key information, compliance requirements, and actionable insights.

Key responsibilities:
- Extract key information and insights
- Identify compliance requirements
- Summarize complex documents
- Highlight important findings
- Provide structured analysis

Always provide clear, organized analysis with actionable insights.""",
        variables=[],
    ),
    "audit_specialist": PromptTemplate(
        name="audit_specialist",
        template="""You are an audit specialist with expertise in internal and external auditing processes.
Your role is to review processes, identify control gaps, and provide audit recommendations.

Key responsibilities:
- Review processes and controls
- Identify control gaps and weaknesses
- Assess compliance with policies and procedures
- Provide audit recommendations
- Ensure thorough and objective analysis

Always provide structured audit findings with specific recommendations.""",
        variables=[],
    ),
}


# User Prompts
USER_PROMPTS = {
    "analyze_document": PromptTemplate(
        name="analyze_document",
        template="""Please analyze the following document for compliance and risk issues:

Document Type: {document_type}
Document Content:
{document_content}

Please provide:
1. Compliance assessment
2. Risk identification
3. Key findings
4. Recommendations
5. Priority level (High/Medium/Low)""",
        variables=["document_type", "document_content"],
    ),
    "assess_risk": PromptTemplate(
        name="assess_risk",
        template="""Please assess the following risk scenario:

Risk Type: {risk_type}
Risk Description: {risk_description}
Business Context: {business_context}

Please provide:
1. Risk level assessment (High/Medium/Low)
2. Impact analysis
3. Likelihood assessment
4. Risk factors
5. Mitigation strategies
6. Monitoring recommendations""",
        variables=["risk_type", "risk_description", "business_context"],
    ),
    "summarize_document": PromptTemplate(
        name="summarize_document",
        template="""Please provide a comprehensive summary of the following document:

Document Title: {document_title}
Document Type: {document_type}
Document Content:
{document_content}

Please provide:
1. Executive summary
2. Key points
3. Important findings
4. Action items
5. Compliance considerations""",
        variables=["document_title", "document_type", "document_content"],
    ),
    "audit_finding": PromptTemplate(
        name="audit_finding",
        template="""Please analyze the following audit finding:

Finding Type: {finding_type}
Finding Description: {finding_description}
Affected Process: {affected_process}
Business Impact: {business_impact}

Please provide:
1. Finding severity (Critical/High/Medium/Low)
2. Root cause analysis
3. Business impact assessment
4. Remediation recommendations
5. Timeline for resolution
6. Preventive measures""",
        variables=[
            "finding_type",
            "finding_description",
            "affected_process",
            "business_impact",
        ],
    ),
}


def get_system_prompt(prompt_type: str) -> str:
    """
    Get system prompt by type.

    Args:
        prompt_type: Type of system prompt

    Returns:
        System prompt string

    Raises:
        ValueError: If prompt type not found
    """
    if prompt_type not in SYSTEM_PROMPTS:
        raise ValueError(f"Unknown system prompt type: {prompt_type}")

    return SYSTEM_PROMPTS[prompt_type].template


def get_user_prompt(prompt_type: str, **kwargs: Any) -> str:
    """
    Get formatted user prompt by type.

    Args:
        prompt_type: Type of user prompt
        **kwargs: Template variables

    Returns:
        Formatted user prompt

    Raises:
        ValueError: If prompt type not found or variables missing
    """
    if prompt_type not in USER_PROMPTS:
        raise ValueError(f"Unknown user prompt type: {prompt_type}")

    return USER_PROMPTS[prompt_type].format(**kwargs)


def create_conversation_prompt(
    system_prompt_type: str, user_prompt_type: str, **kwargs: Any
) -> list[dict[str, str]]:
    """
    Create a complete conversation prompt.

    Args:
        system_prompt_type: Type of system prompt
        user_prompt_type: Type of user prompt
        **kwargs: Template variables

    Returns:
        List of messages for conversation
    """
    system_prompt = get_system_prompt(system_prompt_type)
    user_prompt = get_user_prompt(user_prompt_type, **kwargs)

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


# EGRC-specific prompt templates
EGRC_PROMPTS = {
    "gdpr_compliance_check": PromptTemplate(
        name="gdpr_compliance_check",
        template="""Analyze the following document for GDPR compliance:

Document: {document_content}

Please check for:
1. Data processing lawfulness
2. Consent mechanisms
3. Data subject rights
4. Data protection by design
5. Privacy notices
6. Data breach procedures
7. Data retention policies

Provide a compliance score (0-100) and specific recommendations.""",
        variables=["document_content"],
    ),
    "sox_compliance_review": PromptTemplate(
        name="sox_compliance_review",
        template="""Review the following process for SOX compliance:

Process: {process_description}
Controls: {controls_description}

Please assess:
1. Control design effectiveness
2. Control operating effectiveness
3. Segregation of duties
4. Documentation completeness
5. Monitoring and testing
6. Remediation needs

Provide a compliance assessment and improvement recommendations.""",
        variables=["process_description", "controls_description"],
    ),
    "risk_register_update": PromptTemplate(
        name="risk_register_update",
        template="""Update the risk register with the following information:

Risk Event: {risk_event}
Risk Category: {risk_category}
Current Controls: {current_controls}
Recent Changes: {recent_changes}

Please provide:
1. Updated risk rating
2. Control effectiveness assessment
3. Residual risk level
4. Additional controls needed
5. Monitoring recommendations""",
        variables=["risk_event", "risk_category", "current_controls", "recent_changes"],
    ),
    "audit_planning": PromptTemplate(
        name="audit_planning",
        template="""Plan an audit for the following area:

Audit Area: {audit_area}
Business Process: {business_process}
Regulatory Requirements: {regulatory_requirements}
Previous Findings: {previous_findings}

Please provide:
1. Audit objectives
2. Key risks to focus on
3. Audit procedures
4. Resource requirements
5. Timeline recommendations
6. Success criteria""",
        variables=[
            "audit_area",
            "business_process",
            "regulatory_requirements",
            "previous_findings",
        ],
    ),
}


def get_egrc_prompt(prompt_type: str, **kwargs: Any) -> str:
    """
    Get EGRC-specific prompt.

    Args:
        prompt_type: Type of EGRC prompt
        **kwargs: Template variables

    Returns:
        Formatted EGRC prompt

    Raises:
        ValueError: If prompt type not found or variables missing
    """
    if prompt_type not in EGRC_PROMPTS:
        raise ValueError(f"Unknown EGRC prompt type: {prompt_type}")

    return EGRC_PROMPTS[prompt_type].format(**kwargs)


def list_available_prompts() -> dict[str, list[str]]:
    """
    List all available prompt types.

    Returns:
        Dictionary of prompt categories and types
    """
    return {
        "system_prompts": list(SYSTEM_PROMPTS.keys()),
        "user_prompts": list(USER_PROMPTS.keys()),
        "egrc_prompts": list(EGRC_PROMPTS.keys()),
    }
