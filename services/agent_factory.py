# Agent factory for AutoGen multi-agent setup

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

try:
    from autogen import AssistantAgent, UserProxyAgent
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False

from core.prompts import (
    get_fraud_specialist_prompt,
    get_medical_validator_prompt,
    get_billing_validator_prompt,
    get_policy_balance_validator_prompt,
    get_coverage_exclusions_validator_prompt,
    get_fraud_coordinator_prompt
)
from core.config import get_llm_config

load_dotenv()


class AgentFactory:
    """Factory for creating AutoGen fraud detection agents"""
    
    def __init__(self, claim_data: Dict[str, Any], evidence: Dict[str, Any]):
        self.claim = claim_data
        self.evidence = evidence
        self.llm_config = get_llm_config()
    
    def create_all_agents(self) -> Dict[str, Any]:
        """Create all fraud detection agents"""
        
        if not AUTOGEN_AVAILABLE:
            raise ImportError("AutoGen is not installed. Install with: pip install pyautogen")
        
        agents = {
            "fraud_specialist": self._create_fraud_specialist(),
            "medical_validator": self._create_medical_validator(),
            "billing_validator": self._create_billing_validator(),
            "policy_balance_validator": self._create_policy_balance_validator(),
            "coverage_exclusions_validator": self._create_coverage_exclusions_validator(),
            "fraud_coordinator": self._create_fraud_coordinator(),
            "user_proxy": self._create_user_proxy()
        }
        
        return agents
    
    def _create_fraud_specialist(self) -> 'AssistantAgent':
        """Create fraud detection specialist agent"""
        return AssistantAgent(
            name="Fraud_Detection_Specialist",
            system_message=get_fraud_specialist_prompt(
                self.evidence.get("medical", ""),
                self.evidence.get("billing", ""),
                self.evidence.get("xray", "")
            ),
            llm_config=self.llm_config
        )
    
    def _create_medical_validator(self) -> 'AssistantAgent':
        """Create medical consistency validator agent"""
        return AssistantAgent(
            name="Medical_Consistency_Validator",
            system_message=get_medical_validator_prompt(
                self.evidence.get("medical", ""),
                self.evidence.get("xray", "")
            ),
            llm_config=self.llm_config
        )
    
    def _create_billing_validator(self) -> 'AssistantAgent':
        """Create billing analysis agent"""
        return AssistantAgent(
            name="Billing_Analysis_Validator",
            system_message=get_billing_validator_prompt(
                self.evidence.get("billing", "")
            ),
            llm_config=self.llm_config
        )
    
    def _create_policy_balance_validator(self) -> 'AssistantAgent':
        """Create policy balance validator agent"""
        return AssistantAgent(
            name="Policy_Balance_Validator",
            system_message=get_policy_balance_validator_prompt(
                self.claim,
                self.evidence.get("policy_coverage", "")
            ),
            llm_config=self.llm_config
        )
    
    def _create_coverage_exclusions_validator(self) -> 'AssistantAgent':
        """Create coverage exclusions validator agent"""
        return AssistantAgent(
            name="Coverage_Exclusions_Validator",
            system_message=get_coverage_exclusions_validator_prompt(
                self.evidence.get("detailed_exclusions", ""),
                self.evidence.get("exclusions_analysis", {})
            ),
            llm_config=self.llm_config
        )
    
    def _create_fraud_coordinator(self) -> 'AssistantAgent':
        """Create fraud decision coordinator agent"""
        return AssistantAgent(
            name="Fraud_Decision_Coordinator",
            system_message=get_fraud_coordinator_prompt(self.claim),
            llm_config=self.llm_config
        )
    
    def _create_user_proxy(self) -> 'UserProxyAgent':
        """Create user proxy agent"""
        return UserProxyAgent(
            name="Claim_Processing_System",
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=lambda x: self._is_termination(x)
        )
    
    def _is_termination(self, message: Dict) -> bool:
        """Check if message indicates termination"""
        content = message.get("content", "") if isinstance(message, dict) else str(message)
        content_upper = content.upper()
        return ("FINAL DECISION:" in content_upper and 
                ("APPROVED" in content_upper or "REJECTED" in content_upper))
    
    def get_agent_list(self, agents: Dict[str, Any]) -> List:
        """Get ordered list of agents for group chat"""
        return [
            agents["user_proxy"],
            agents["fraud_specialist"],
            agents["medical_validator"],
            agents["billing_validator"],
            agents["policy_balance_validator"],
            agents["coverage_exclusions_validator"],
            agents["fraud_coordinator"]
        ]
