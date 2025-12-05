# Health Insurance Fraud Detection System - Main Entry Point
# Uses the refactored modular orchestrator

import asyncio
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import the refactored orchestrator
from orchestrator import FraudDetectionOrchestrator
from core.config import get_default_claim_data

# Import legacy workflow manager for backwards compatibility
from workflow_manager import HealthInsuranceWorkflowManager, ClaimData, ClaimStatus


class HealthInsuranceClaimSystem:
    """
    Main system interface for health insurance claim processing.
    Provides both fraud detection (AutoGen) and legacy workflow processing.
    """
    
    def __init__(self, enable_fraud_detection: bool = True):
        """
        Initialize the claim processing system.
        
        Args:
            enable_fraud_detection: Enable AutoGen-based fraud detection
        """
        self.enable_fraud_detection = enable_fraud_detection
        self.processed_claims: List[Dict[str, Any]] = []
        
        # Initialize fraud detection orchestrator
        if enable_fraud_detection:
            self.fraud_orchestrator = FraudDetectionOrchestrator(
                enable_xray=True,
                enable_azure_evidence=True
            )
        
        # Initialize legacy workflow manager
        try:
            self.workflow_manager = HealthInsuranceWorkflowManager()
        except Exception as e:
            print(f"⚠️ Legacy workflow unavailable: {e}")
            self.workflow_manager = None
        
        print("\n🏥 Health Insurance Claim Processing System Initialized")
        print(f"   Fraud Detection: {'✅' if enable_fraud_detection else '❌'}")
        print(f"   Legacy Workflow: {'✅' if self.workflow_manager else '❌'}")
    
    async def process_claim_with_fraud_detection(
        self, claim_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process claim using AutoGen multi-agent fraud detection.
        
        Args:
            claim_data: Claim details dictionary
            
        Returns:
            Comprehensive fraud analysis results
        """
        if not self.enable_fraud_detection:
            return {"error": "Fraud detection not enabled"}
        
        if claim_data is None:
            claim_data = get_default_claim_data()
        
        result = await self.fraud_orchestrator.process_claim(claim_data)
        self.processed_claims.append(result)
        
        return result
    
    def process_claim_legacy(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process claim using legacy workflow manager.
        
        Args:
            claim_data: Claim details dictionary
            
        Returns:
            Processing results
        """
        if not self.workflow_manager:
            return {"error": "Legacy workflow not available"}
        
        try:
            claim = ClaimData(
                claim_id=claim_data.get("claim_id"),
                patient_name=claim_data.get("patient_name"),
                policy_number=claim_data.get("policy_number"),
                claim_amount=float(claim_data.get("claim_amount", 0)),
                claim_date=claim_data.get("claim_date"),
                diagnosis=claim_data.get("diagnosis"),
                treatment_type=claim_data.get("treatment_type"),
                hospital_name=claim_data.get("hospital_name"),
                documents_available=claim_data.get("documents_available", [])
            )
            
            result = self.workflow_manager.process_claim_with_workflow(claim)
            
            return {
                "claim_id": result.claim_id,
                "status": result.final_status.value,
                "approved_amount": result.approved_amount,
                "processing_time": result.total_processing_time,
                "agent_results": [
                    {
                        "agent": agent.agent_name,
                        "status": agent.status,
                        "recommendations": agent.recommendations,
                        "processing_time": agent.processing_time
                    }
                    for agent in result.agent_results
                ],
                "final_report": result.final_report,
                "recommendations": result.recommendations,
                "completed_at": result.completed_at
            }
            
        except Exception as e:
            return {
                "claim_id": claim_data.get("claim_id", "unknown"),
                "status": "error",
                "error": str(e)
            }
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of all processed claims"""
        if not self.processed_claims:
            return {"message": "No claims processed yet"}
        
        total = len(self.processed_claims)
        approved = sum(1 for c in self.processed_claims 
                      if c.get('fraud_orchestration', {}).get('fraud_decision', {}).get('decision') == 'APPROVED')
        rejected = sum(1 for c in self.processed_claims 
                      if c.get('fraud_orchestration', {}).get('fraud_decision', {}).get('decision') == 'REJECTED')
        
        return {
            "total_processed": total,
            "approved": approved,
            "rejected": rejected,
            "approval_rate": f"{(approved/total)*100:.1f}%" if total > 0 else "0%",
            "avg_processing_time": sum(c.get('processing_time', 0) for c in self.processed_claims) / total
        }


def create_sample_claims() -> List[Dict[str, Any]]:
    """Create sample claim data for testing"""
    return [
        {
            "claim_id": "CLM001-2024-001",
            "patient_name": "John Doe",
            "policy_number": "POL123456789",
            "claim_amount": 75000.00,
            "claim_date": "2024-09-15",
            "diagnosis": "Knee Osteoarthritis with joint replacement surgery",
            "treatment_type": "Orthopedic Surgery - Total Knee Replacement",
            "hospital_name": "Apollo Hospital, Delhi",
            "documents_available": ["medical_records", "x-ray", "bills", "discharge_summary"],
            "policy_coverage_limit": 500000.00,
            "previously_claimed_amount": 50000.00,
            "available_balance": 450000.00
        },
        {
            "claim_id": "CLM001-2024-002",
            "patient_name": "Jane Smith",
            "policy_number": "POL987654321",
            "claim_amount": 45000.00,
            "claim_date": "2024-09-16",
            "diagnosis": "Cardiac catheterization and angioplasty",
            "treatment_type": "Cardiology - Angioplasty with stent placement",
            "hospital_name": "Fortis Hospital, Mumbai",
            "documents_available": ["medical_records", "ecg", "bills", "lab_reports"],
            "policy_coverage_limit": 1000000.00,
            "previously_claimed_amount": 100000.00,
            "available_balance": 900000.00
        }
    ]


async def run_fraud_detection_demo():
    """Run fraud detection demonstration"""
    print("\n" + "="*80)
    print("🚀 FRAUD DETECTION SYSTEM DEMONSTRATION")
    print("="*80)
    
    # Initialize system
    system = HealthInsuranceClaimSystem(enable_fraud_detection=True)
    
    # Process default claim with full fraud detection
    print("\n📋 Processing claim with fraud detection...")
    result = await system.process_claim_with_fraud_detection()
    
    # Show summary
    summary = system.get_processing_summary()
    print("\n📊 Processing Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    return result


async def main():
    """Main entry point"""
    result = await run_fraud_detection_demo()
    
    print("\n" + "="*80)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*80)
    
    print("\n💡 USAGE EXAMPLES:")
    print("-" * 40)
    print("# Initialize system")
    print("system = HealthInsuranceClaimSystem()")
    print()
    print("# Process claim with fraud detection")
    print("result = await system.process_claim_with_fraud_detection(claim_data)")
    print()
    print("# Get processing summary")
    print("summary = system.get_processing_summary()")
    print("-" * 40)
    
    return result


if __name__ == "__main__":
    asyncio.run(main())
