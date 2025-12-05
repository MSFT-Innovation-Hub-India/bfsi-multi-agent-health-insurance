# Report generation service

import os
import json
from datetime import datetime
from typing import Dict, Any


class ReportGenerator:
    """Generates fraud detection reports"""
    
    def __init__(self, claim_data: Dict[str, Any]):
        self.claim = claim_data
    
    def save_report(self, results: Dict[str, Any], filename: str = None) -> str:
        """Save comprehensive fraud detection report"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fraud_detection_analysis_{timestamp}.json"
        
        report = {
            "report_type": "Comprehensive Fraud Detection Analysis",
            "generated_at": datetime.now().isoformat(),
            "patient_details": self.claim,
            "fraud_analysis_results": results,
            "fraud_detection_capabilities": {
                "identity_verification": True,
                "medical_consistency_check": True,
                "billing_validation": True,
                "documentation_integrity": True,
                "imaging_correlation": True,
                "multi_agent_analysis": True,
                "azure_ai_evidence_collection": True
            }
        }
        
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📊 Fraud detection report saved: {filepath}")
        return filepath
    
    def print_results(self, results: Dict[str, Any]):
        """Print comprehensive fraud detection results"""
        
        print(f"\n{'='*80}")
        print(f"🚨 FRAUD DETECTION ANALYSIS RESULTS")
        print(f"{'='*80}")
        print(f"Claim ID: {results['claim_id']}")
        print(f"Patient: {results['patient_name']}")
        print(f"Processing Time: {results['processing_time']:.2f} seconds")
        
        # Print system status
        self._print_system_status(results.get('system_status', {}))
        
        # Print evidence collection status
        self._print_evidence_status(results.get('azure_evidence', {}))
        
        # Print fraud analysis
        self._print_fraud_analysis(results.get('fraud_orchestration', {}))
        
        # Print final summary
        self._print_final_summary(results)
    
    def _print_system_status(self, status: Dict[str, Any]):
        """Print system status section"""
        print(f"\n🔧 SYSTEM STATUS:")
        for component, value in status.items():
            if isinstance(value, bool):
                icon = "✅" if value else "❌"
                text = 'Enabled' if value else 'Disabled'
            else:
                icon = "✅"
                text = str(value)
            print(f"  {icon} {component.replace('_', ' ').title()}: {text}")
    
    def _print_evidence_status(self, evidence: Dict[str, Any]):
        """Print evidence collection status"""
        print(f"\n🔍 EVIDENCE COLLECTION:")
        for source, data in evidence.items():
            if source != 'error':
                icon = "✅" if data and 'failed' not in str(data) else "❌"
                status = 'Collected' if data and 'failed' not in str(data) else 'Failed'
                print(f"  {icon} {source.replace('_', ' ').title()}: {status}")
    
    def _print_fraud_analysis(self, analysis: Dict[str, Any]):
        """Print fraud analysis section"""
        print(f"\n🕵️‍♂️ FRAUD DETECTION ANALYSIS:")
        icon = "✅" if analysis.get('status') == 'completed' else "❌"
        print(f"  {icon} Status: {analysis.get('status', 'unknown')}")
        
        decision = analysis.get('fraud_decision', {})
        if decision:
            if decision.get('decision') == 'ORCHESTRATION_FAILED':
                print(f"\n📋 ORCHESTRATION STATUS:")
                print(f"  ⚠️ Status: ORCHESTRATION FAILED")
                print(f"  ❌ Issue: AutoGen agents did not provide final decision")
            else:
                icon = "❌" if decision.get('decision') == 'REJECTED' else "✅"
                print(f"\n📋 FRAUD DETECTION DECISION:")
                print(f"  {icon} Decision: {decision.get('decision', 'Unknown')}")
                print(f"  💰 Amount: {decision.get('approved_amount', 'Unknown')}")
                print(f"  ⚠️ Fraud Risk: {decision.get('fraud_risk_level', 'Unknown')}")
                print(f"  📋 Coverage Assessment: {decision.get('coverage_assessment', 'Unknown')}")
                print(f"  🛡️ Balance Status: {decision.get('balance_status', 'Unknown')}")
                print(f"  🚫 Exclusions Apply: {decision.get('exclusions_applicable', 'Unknown')}")
                print(f"  📊 Remaining Balance: {decision.get('remaining_balance', 'Unknown')}")
                print(f"  📈 Policy Utilization: {decision.get('policy_utilization', 'Unknown')}")
    
    def _print_final_summary(self, results: Dict[str, Any]):
        """Print final summary"""
        print(f"\n{'='*80}")
        decision = results.get('fraud_orchestration', {}).get('fraud_decision', {})
        status = decision.get('decision', 'UNKNOWN')
        
        if status == 'ORCHESTRATION_FAILED':
            print(f"⚠️ ORCHESTRATION FAILED - AGENTS DID NOT DECIDE")
        elif status == 'REJECTED':
            print(f"🚨 CLAIM REJECTED - FRAUD DETECTED")
        elif status == 'APPROVED':
            print(f"✅ CLAIM APPROVED - NO FRAUD DETECTED")
        else:
            print(f"❓ UNKNOWN DECISION STATUS")
        print(f"{'='*80}")
