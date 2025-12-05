# Agent prompts/templates for the fraud detection system
# This module re-exports prompts from the centralized instructions module
# All instructions are now maintained in core/instructions.py for better maintainability

from typing import Dict, Any

# Re-export from centralized instructions
from core.instructions import (
    # AutoGen fraud detection prompts
    get_fraud_specialist_prompt,
    get_medical_validator_prompt,
    get_billing_validator_prompt,
    get_policy_balance_validator_prompt,
    get_coverage_exclusions_validator_prompt,
    get_fraud_coordinator_prompt,
    
    # Azure AI agent instructions
    AZURE_AGENT_INSTRUCTIONS,
    get_azure_agent_instruction,
    
    # X-ray descriptions
    XRAY_GRADE_DESCRIPTIONS,
    get_xray_grade_description,
    
    # Search field mappings
    SEARCH_FIELD_MAPPINGS,
)

# Export all symbols for backward compatibility
__all__ = [
    # AutoGen prompts
    'get_fraud_specialist_prompt',
    'get_medical_validator_prompt', 
    'get_billing_validator_prompt',
    'get_policy_balance_validator_prompt',
    'get_coverage_exclusions_validator_prompt',
    'get_fraud_coordinator_prompt',
    
    # Azure AI instructions
    'AZURE_AGENT_INSTRUCTIONS',
    'get_azure_agent_instruction',
    
    # X-ray
    'XRAY_GRADE_DESCRIPTIONS',
    'get_xray_grade_description',
    
    # Search
    'SEARCH_FIELD_MAPPINGS',
]

# Note: All prompt functions and instructions are now defined in core/instructions.py
# This file is kept for backward compatibility with existing imports
