# Configuration settings for Health Insurance Claim Processing System

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import centralized instructions and constants
from core.instructions import (
    AZURE_AGENT_INSTRUCTIONS,
    SEARCH_FIELD_MAPPINGS,
    XRAY_GRADE_DESCRIPTIONS
)

# Re-export for backward compatibility
AGENT_INSTRUCTIONS = AZURE_AGENT_INSTRUCTIONS

@dataclass
class AzureConfig:
    """Azure service configuration"""
    endpoint: str = field(default_factory=lambda: os.getenv("AZURE_ENDPOINT", "https://eastus2.api.azureml.ms"))
    resource_group: str = field(default_factory=lambda: os.getenv("AZURE_RESOURCE_GROUP", ""))
    subscription_id: str = field(default_factory=lambda: os.getenv("AZURE_SUBSCRIPTION_ID", ""))
    project_name: str = field(default_factory=lambda: os.getenv("AZURE_PROJECT_NAME", ""))

@dataclass
class SearchIndicesConfig:
    """Azure AI Search indices configuration"""
    billing_index: str = field(default_factory=lambda: os.getenv("AZURE_SEARCH_BILLING_INDEX", "healthbills"))
    medical_records_index: str = field(default_factory=lambda: os.getenv("AZURE_SEARCH_MEDICAL_INDEX", "healthmedicalrecords"))
    exclusions_index: str = field(default_factory=lambda: os.getenv("AZURE_SEARCH_EXCLUSIONS_INDEX", "healthclaims"))

@dataclass
class XRayConfig:
    """X-ray analysis configuration"""
    base_url: str = field(default_factory=lambda: os.getenv("CUSTOM_VISION_ENDPOINT", "https://abc.cognitiveservices.azure.com/customvision/v3.0/Prediction"))
    project_id: str = field(default_factory=lambda: os.getenv("CUSTOM_VISION_PROJECT_ID", ""))
    iteration_name: str = field(default_factory=lambda: os.getenv("CUSTOM_VISION_ITERATION_NAME", "Iteration4"))
    prediction_key: str = field(default_factory=lambda: os.getenv("CUSTOM_VISION_PREDICTION_KEY", ""))
    storage_account_name: str = field(default_factory=lambda: os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "fsidemo"))
    storage_account_key: str = field(default_factory=lambda: os.getenv("AZURE_STORAGE_ACCOUNT_KEY", ""))  # Optional - use Managed Identity
    container_name: str = field(default_factory=lambda: os.getenv("AZURE_STORAGE_CONTAINER_NAME", "health-insurance"))
    xray_path: str = field(default_factory=lambda: os.getenv("AZURE_STORAGE_XRAY_PATH", "xray"))

@dataclass
class WorkflowConfig:
    """Workflow processing configuration"""
    max_retry_attempts: int = 3
    timeout_seconds: int = 300
    enable_parallel_processing: bool = False
    save_intermediate_results: bool = True
    cleanup_agents_after_processing: bool = True

@dataclass
class AgentConfig:
    """Agent-specific configuration"""
    model_name: str = "gpt-4o"
    max_response_tokens: int = 4000
    temperature: float = 0.1  # Low temperature for consistent analysis
    enable_detailed_logging: bool = True

@dataclass
class SystemConfig:
    """Complete system configuration"""
    azure: AzureConfig
    search_indices: SearchIndicesConfig
    xray: XRayConfig
    workflow: WorkflowConfig
    agents: AgentConfig
    
    def __init__(self):
        self.azure = AzureConfig()
        self.search_indices = SearchIndicesConfig()
        self.xray = XRayConfig()
        self.workflow = WorkflowConfig()
        self.agents = AgentConfig()

# Global configuration instance
CONFIG = SystemConfig()

# Status transition rules
CLAIM_STATUS_RULES = {
    "auto_approve_threshold": 0.9,  # Confidence threshold for auto-approval
    "auto_reject_threshold": 0.1,   # Confidence threshold for auto-rejection
    "requires_manual_review": [
        "high_value_claim",  # Claims above certain amount
        "multiple_exclusions_found", 
        "inconsistent_medical_records",
        "fraud_indicators_detected"
    ]
}

def get_environment_config() -> Dict[str, str]:
    """Get configuration from environment variables"""
    return {
        "azure_endpoint": os.getenv("AZURE_ENDPOINT", CONFIG.azure.endpoint),
        "azure_resource_group": os.getenv("AZURE_RESOURCE_GROUP", CONFIG.azure.resource_group),
        "azure_subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID", CONFIG.azure.subscription_id),
        "azure_project_name": os.getenv("AZURE_PROJECT_NAME", CONFIG.azure.project_name),
        "custom_vision_key": os.getenv("CUSTOM_VISION_PREDICTION_KEY", CONFIG.xray.prediction_key),
        "storage_account_key": os.getenv("AZURE_STORAGE_ACCOUNT_KEY", CONFIG.xray.storage_account_key)
    }

def validate_config() -> List[str]:
    """Validate configuration and return list of issues"""
    issues = []
    
    # Check Azure configuration
    if not CONFIG.azure.subscription_id:
        issues.append("Azure subscription ID not configured")
    
    if not CONFIG.azure.project_name:
        issues.append("Azure project name not configured")
    
    # Check X-ray configuration
    if not CONFIG.xray.prediction_key:
        issues.append("Custom Vision prediction key not configured")
    
    if not CONFIG.xray.storage_account_key:
        issues.append("Azure Storage account key not configured")
    
    return issues

def print_config_status():
    """Print current configuration status"""
    print("📋 SYSTEM CONFIGURATION STATUS")
    print("=" * 50)
    print(f"Azure Project: {CONFIG.azure.project_name}")
    print(f"Resource Group: {CONFIG.azure.resource_group}")
    print(f"Search Indices:")
    print(f"  - Billing: {CONFIG.search_indices.billing_index}")
    print(f"  - Medical: {CONFIG.search_indices.medical_records_index}")
    print(f"  - Exclusions: {CONFIG.search_indices.exclusions_index}")
    print(f"X-ray Analysis: {'Enabled' if CONFIG.xray.prediction_key else 'Disabled'}")
    print(f"Model: {CONFIG.agents.model_name}")
    print(f"Auto-cleanup: {'Yes' if CONFIG.workflow.cleanup_agents_after_processing else 'No'}")
    
    # Check for issues
    issues = validate_config()
    if issues:
        print(f"\n⚠️ Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"\n✅ Configuration is valid")
    
    print("=" * 50)

if __name__ == "__main__":
    print_config_status()