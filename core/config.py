# Configuration management for the fraud detection system

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


def get_llm_config() -> Dict[str, Any]:
    """Get AutoGen LLM configuration from environment variables"""
    return {
        "config_list": [{
            "model": os.getenv("AZURE_OPENAI_MODEL", "gpt-4o"),
            "api_type": "azure",
            "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        }],
        "temperature": 0.1,
        "max_tokens": 1000,
        "timeout": 120
    }


def get_default_claim_data() -> Dict[str, Any]:
    """Get default claim data - Single source of truth for claim information"""
    return {
        "claim_id": "CLM001-2024-LAKSHMI",
        "patient_name": "Lakshmisrinivas T",
        "policy_number": "POL789456123",
        "claim_amount": 396591.00,
        "claim_date": "2024-09-16",
        "diagnosis": "Orthopedic surgery and rehabilitation",
        "treatment_type": "Orthopedic Surgery with post-operative care",
        "hospital_name": "Ramakrishna hospital, Bangalore",
        "documents_available": ["medical_records", "x-ray", "bills", "discharge_summary", "lab_reports"],
        "policy_coverage_limit": 1000000.00,
        "previously_claimed_amount": 150000.00,
        "available_balance": 850000.00,
        "policy_year": "2024-2025"
    }


# Policy exclusion keywords for analysis
EXCLUSION_KEYWORDS = {
    "pre_existing": ["chronic", "degenerative", "arthritis", "osteoarthritis"],
    "experimental": ["experimental", "investigational", "trial"],
    "cosmetic": ["cosmetic", "elective", "aesthetic"],
    "age_related": ["bilateral", "total"]
}

# Known excluded items with authoritative amounts
KNOWN_EXCLUSIONS = {
    "walker": {"amount": 3334, "keywords": ["walker", "walking aid", "mobility aid"]},
    "knee_brace": {"amount": 1140, "keywords": ["knee brace", "brace", "support", "orthotic"]},
    "consumables": {"amount": 3315, "keywords": ["consumables", "syringes", "bandages"]}
}

# High-value claim threshold
HIGH_VALUE_THRESHOLD = 300000
