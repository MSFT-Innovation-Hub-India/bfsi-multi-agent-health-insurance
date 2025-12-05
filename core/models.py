# Data models for the fraud detection system

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class ClaimStatus(Enum):
    """Claim processing status enumeration"""
    INITIATED = "initiated"
    UNDER_REVIEW = "under_review"
    MEDICAL_REVIEW = "medical_review"
    BILLING_REVIEW = "billing_review"
    EXCLUSION_CHECK = "exclusion_check"
    XRAY_ANALYSIS = "xray_analysis"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_INFO = "pending_information"
    COMPLETED = "completed"


@dataclass
class ClaimData:
    """Data structure for claim information"""
    claim_id: str
    patient_name: str
    policy_number: str
    claim_amount: float
    claim_date: str
    diagnosis: str
    treatment_type: str
    hospital_name: str
    documents_available: List[str]
    status: ClaimStatus = ClaimStatus.INITIATED
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class FraudIndicator:
    """Class to represent a fraud indicator"""
    fraud_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClaimValidationResult:
    """Result of comprehensive claim validation"""
    is_consistent: bool = True
    fraud_indicators: List[FraudIndicator] = field(default_factory=list)
    medical_analysis: Dict[str, Any] = field(default_factory=dict)
    billing_analysis: Dict[str, Any] = field(default_factory=dict)
    documentation_analysis: Dict[str, Any] = field(default_factory=dict)
    final_recommendation: str = "APPROVE"
    confidence_score: float = 0.0


@dataclass
class AgentResult:
    """Result from an individual agent"""
    agent_name: str
    status: str
    analysis: str
    recommendations: List[str]
    findings: Dict[str, Any]
    processing_time: float
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class WorkflowResult:
    """Complete workflow processing result"""
    claim_id: str
    final_status: ClaimStatus
    approved_amount: float
    total_processing_time: float
    agent_results: List[AgentResult]
    final_report: str
    recommendations: List[str]
    completed_at: str = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now().isoformat()


@dataclass
class FraudDecision:
    """Final fraud detection decision"""
    decision: str  # APPROVED, REJECTED, ORCHESTRATION_FAILED
    approved_amount: str
    fraud_risk_level: str
    coverage_risk_level: str
    coverage_assessment: str
    balance_status: str
    exclusions_applicable: str
    remaining_balance: str
    policy_utilization: str
    fraud_indicators: List[str] = field(default_factory=list)
    rationale: str = ""
    conversation_length: int = 0
    decision_source: str = ""
