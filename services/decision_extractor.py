# Decision extraction service for parsing agent responses

import re
from typing import Dict, Any, List, Optional
from core.utils import get_message_content, extract_all_amounts, extract_decision_field


class DecisionExtractor:
    """Extracts fraud detection decisions from agent messages"""
    
    def __init__(self, claim_data: Dict[str, Any]):
        self.claim = claim_data
    
    def extract_decision(self, messages: List) -> Dict[str, Any]:
        """Extract fraud decision from AutoGen conversation messages"""
        
        decision_data = {
            "decision": None,
            "amount": None,
            "fraud_risk": None,
            "coverage_risk": None,
            "coverage_assessment": None,
            "balance_status": None,
            "exclusions_applicable": None,
            "rationale": ""
        }
        
        for msg in messages:
            content = get_message_content(msg)
            
            if self._is_final_decision(content):
                decision_data = self._parse_decision_content(content)
                break
        
        return self._format_decision(decision_data)
    
    def _is_final_decision(self, content: str) -> bool:
        """Check if message contains final decision"""
        content_upper = content.upper()
        return ("FINAL DECISION:" in content_upper and 
                ("APPROVED" in content_upper or "REJECTED" in content_upper))
    
    def _parse_decision_content(self, content: str) -> Dict[str, Any]:
        """Parse decision fields from content"""
        return {
            "decision": self._extract_final_decision(content),
            "amount": self._extract_amount(content),
            "fraud_risk": extract_decision_field(content, "FRAUD RISK LEVEL", ["HIGH", "MEDIUM", "LOW"]),
            "coverage_risk": extract_decision_field(content, "COVERAGE RISK LEVEL", ["HIGH", "MEDIUM", "LOW"]),
            "coverage_assessment": extract_decision_field(content, "COVERAGE ASSESSMENT", ["EXCLUDED", "COVERED", "PARTIAL"]),
            "balance_status": extract_decision_field(content, "POLICY BALANCE STATUS", ["SUFFICIENT", "INSUFFICIENT", "EXCEEDED"]),
            "exclusions_applicable": extract_decision_field(content, "EXCLUSIONS APPLICABLE", ["YES", "NO"]),
            "rationale": content
        }
    
    def _extract_final_decision(self, content: str) -> Optional[str]:
        """Extract final decision (APPROVED/REJECTED)"""
        content_upper = content.upper()
        
        # Check for REJECTED first (priority)
        if "FINAL DECISION:** REJECTED" in content_upper or "FINAL DECISION: REJECTED" in content_upper:
            return "REJECTED"
        
        if "FINAL DECISION:** APPROVED" in content_upper or "FINAL DECISION: APPROVED" in content_upper:
            return "APPROVED"
        
        # Fallback check
        if "REJECTED" in content_upper:
            return "REJECTED"
        if "APPROVED" in content_upper:
            return "APPROVED"
        
        return None
    
    def _extract_amount(self, content: str) -> Optional[str]:
        """Extract approved amount"""
        amounts = extract_all_amounts(content)
        return amounts[0] if amounts else None
    
    def _format_decision(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format decision into final structure"""
        
        if data["decision"] is None:
            return self._get_failed_decision()
        
        # Calculate balances
        if data["decision"] == "APPROVED" and data["amount"] and data["amount"] != "₹0":
            remaining = self.claim['available_balance'] - self.claim['claim_amount']
            utilization = ((self.claim['previously_claimed_amount'] + self.claim['claim_amount']) 
                          / self.claim['policy_coverage_limit']) * 100
        else:
            remaining = self.claim['available_balance']
            utilization = (self.claim['previously_claimed_amount'] / self.claim['policy_coverage_limit']) * 100
        
        return {
            "decision": data["decision"],
            "approved_amount": data["amount"] or "₹0.00",
            "fraud_risk_level": data["fraud_risk"] or "UNKNOWN",
            "coverage_risk_level": data["coverage_risk"] or "UNKNOWN",
            "coverage_assessment": data["coverage_assessment"] or "UNKNOWN",
            "balance_status": data["balance_status"] or "UNKNOWN",
            "exclusions_applicable": data["exclusions_applicable"] or "UNKNOWN",
            "remaining_balance": f"₹{remaining:,.2f}",
            "policy_utilization": f"{utilization:.1f}%",
            "fraud_indicators": [],
            "rationale": f"AutoGen Coordinator Decision: {data['rationale'][:200]}...",
            "decision_source": "AutoGen Fraud_Decision_Coordinator"
        }
    
    def _get_failed_decision(self) -> Dict[str, Any]:
        """Return failed orchestration decision"""
        utilization = (self.claim['previously_claimed_amount'] / self.claim['policy_coverage_limit']) * 100
        
        return {
            "decision": "ORCHESTRATION_FAILED",
            "approved_amount": "₹0.00",
            "fraud_risk_level": "UNKNOWN",
            "coverage_risk_level": "UNKNOWN",
            "coverage_assessment": "UNKNOWN",
            "balance_status": "UNKNOWN",
            "exclusions_applicable": "UNKNOWN",
            "remaining_balance": f"₹{self.claim['available_balance']:,.2f}",
            "policy_utilization": f"{utilization:.1f}%",
            "fraud_indicators": ["Coordinator did not provide final decision"],
            "rationale": "AutoGen orchestration failed - coordinator did not make final decision",
            "decision_source": "FAILED - No coordinator decision found"
        }
