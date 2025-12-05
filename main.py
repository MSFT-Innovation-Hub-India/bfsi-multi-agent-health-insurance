# Health Insurance Claim Processing System
# Main entry point for comprehensive claim processing using Azure AI Foundry agents

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from workflow_manager import HealthInsuranceWorkflowManager, ClaimData, ClaimStatus

class HealthInsuranceClaimSystem:
    """
    Main system interface for health insurance claim processing
    Provides easy-to-use methods for processing claims and generating reports
    """
    
    def __init__(self):
        self.workflow_manager = HealthInsuranceWorkflowManager()
        self.processed_claims = []
        
        print("🏥 Health Insurance Claim Processing System Initialized")
        print("   ✅ Azure AI Foundry agents ready")
        print("   ✅ X-ray analysis API connected")
        print("   ✅ Shared thread coordination enabled")
    
    def process_single_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single insurance claim
        
        Args:
            claim_data: Dictionary containing claim information
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Convert dictionary to ClaimData object
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
            
            # Process the claim using workflow manager
            result = self.workflow_manager.process_claim_with_workflow(claim)
            
            # Store processed claim
            self.processed_claims.append(result)
            
            # Convert to dictionary format
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
            print(f"❌ Error processing claim: {str(e)}")
            return {
                "claim_id": claim_data.get("claim_id", "unknown"),
                "status": "error",
                "error": str(e),
                "approved_amount": 0,
                "processing_time": 0
            }
    
    def process_batch_claims(self, claims_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process multiple insurance claims in batch
        
        Args:
            claims_list: List of claim dictionaries
            
        Returns:
            Batch processing results
        """
        print(f"\n📋 BATCH PROCESSING: {len(claims_list)} claims")
        print("=" * 60)
        
        batch_results = {
            "total_claims": len(claims_list),
            "processed_claims": 0,
            "approved_claims": 0,
            "rejected_claims": 0,
            "pending_claims": 0,
            "total_approved_amount": 0.0,
            "total_processing_time": 0.0,
            "results": []
        }
        
        for i, claim_data in enumerate(claims_list, 1):
            print(f"\n📄 Processing Claim {i}/{len(claims_list)}: {claim_data.get('claim_id', 'Unknown')}")
            
            result = self.process_single_claim(claim_data)
            batch_results["results"].append(result)
            
            # Update batch statistics
            if result.get("status") != "error":
                batch_results["processed_claims"] += 1
                batch_results["total_processing_time"] += result.get("processing_time", 0)
                batch_results["total_approved_amount"] += result.get("approved_amount", 0)
                
                if result.get("status") == "approved":
                    batch_results["approved_claims"] += 1
                elif result.get("status") == "rejected":
                    batch_results["rejected_claims"] += 1
                else:
                    batch_results["pending_claims"] += 1
        
        # Print batch summary
        self._print_batch_summary(batch_results)
        return batch_results
    
    def get_claim_status(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific claim
        
        Args:
            claim_id: Claim identifier
            
        Returns:
            Claim status information or None if not found
        """
        for claim in self.processed_claims:
            if claim.claim_id == claim_id:
                return {
                    "claim_id": claim.claim_id,
                    "status": claim.final_status.value,
                    "approved_amount": claim.approved_amount,
                    "completed_at": claim.completed_at,
                    "total_agents": len(claim.agent_results),
                    "processing_time": claim.total_processing_time
                }
        return None
    
    def generate_system_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive system performance report
        
        Returns:
            System performance statistics
        """
        if not self.processed_claims:
            return {"message": "No claims processed yet"}
        
        total_claims = len(self.processed_claims)
        approved_claims = sum(1 for c in self.processed_claims if c.final_status == ClaimStatus.APPROVED)
        rejected_claims = sum(1 for c in self.processed_claims if c.final_status == ClaimStatus.REJECTED)
        pending_claims = sum(1 for c in self.processed_claims if c.final_status == ClaimStatus.PENDING_INFO)
        
        total_approved_amount = sum(c.approved_amount for c in self.processed_claims if c.final_status == ClaimStatus.APPROVED)
        avg_processing_time = sum(c.total_processing_time for c in self.processed_claims) / total_claims
        
        report = {
            "total_claims_processed": total_claims,
            "approval_rate": f"{(approved_claims/total_claims)*100:.1f}%",
            "rejection_rate": f"{(rejected_claims/total_claims)*100:.1f}%",
            "pending_rate": f"{(pending_claims/total_claims)*100:.1f}%",
            "total_approved_amount": f"₹{total_approved_amount:,.2f}",
            "average_processing_time": f"{avg_processing_time:.2f} seconds",
            "claims_breakdown": {
                "approved": approved_claims,
                "rejected": rejected_claims,
                "pending": pending_claims
            },
            "agent_performance": self._calculate_agent_performance()
        }
        
        self._print_system_report(report)
        return report
    
    def save_results_to_file(self, filename: str = None) -> str:
        """
        Save all processed claims to a JSON file
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"claim_processing_results_{timestamp}.json"
        
        # Convert results to serializable format
        results_data = {
            "system_info": {
                "processed_at": datetime.now().isoformat(),
                "total_claims": len(self.processed_claims),
                "system_version": "1.0"
            },
            "claims": []
        }
        
        for claim in self.processed_claims:
            claim_data = {
                "claim_id": claim.claim_id,
                "final_status": claim.final_status.value,
                "approved_amount": claim.approved_amount,
                "total_processing_time": claim.total_processing_time,
                "completed_at": claim.completed_at,
                "agent_results": [
                    {
                        "agent_name": agent.agent_name,
                        "status": agent.status,
                        "processing_time": agent.processing_time,
                        "recommendations": agent.recommendations,
                        "timestamp": agent.timestamp
                    }
                    for agent in claim.agent_results
                ],
                "final_report": claim.final_report,
                "recommendations": claim.recommendations
            }
            results_data["claims"].append(claim_data)
        
        # Save to file
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filepath}")
        return filepath
    
    def _calculate_agent_performance(self) -> Dict[str, Any]:
        """Calculate performance metrics for each agent type"""
        agent_stats = {}
        
        for claim in self.processed_claims:
            for agent_result in claim.agent_results:
                agent_name = agent_result.agent_name
                if agent_name not in agent_stats:
                    agent_stats[agent_name] = {
                        "total_runs": 0,
                        "successful_runs": 0,
                        "total_time": 0,
                        "avg_time": 0
                    }
                
                agent_stats[agent_name]["total_runs"] += 1
                agent_stats[agent_name]["total_time"] += agent_result.processing_time
                
                if agent_result.status == "completed":
                    agent_stats[agent_name]["successful_runs"] += 1
        
        # Calculate averages
        for agent_name, stats in agent_stats.items():
            if stats["total_runs"] > 0:
                stats["avg_time"] = stats["total_time"] / stats["total_runs"]
                stats["success_rate"] = f"{(stats['successful_runs']/stats['total_runs'])*100:.1f}%"
        
        return agent_stats
    
    def _print_batch_summary(self, batch_results: Dict[str, Any]):
        """Print batch processing summary"""
        print("\n" + "="*60)
        print("📊 BATCH PROCESSING SUMMARY")
        print("="*60)
        print(f"Total Claims: {batch_results['total_claims']}")
        print(f"Successfully Processed: {batch_results['processed_claims']}")
        print(f"Approved: {batch_results['approved_claims']}")
        print(f"Rejected: {batch_results['rejected_claims']}")
        print(f"Pending: {batch_results['pending_claims']}")
        print(f"Total Approved Amount: ₹{batch_results['total_approved_amount']:,.2f}")
        print(f"Total Processing Time: {batch_results['total_processing_time']:.2f} seconds")
        
        if batch_results['processed_claims'] > 0:
            avg_time = batch_results['total_processing_time'] / batch_results['processed_claims']
            approval_rate = (batch_results['approved_claims'] / batch_results['processed_claims']) * 100
            print(f"Average Processing Time: {avg_time:.2f} seconds")
            print(f"Approval Rate: {approval_rate:.1f}%")
        
        print("="*60)
    
    def _print_system_report(self, report: Dict[str, Any]):
        """Print system performance report"""
        print("\n" + "="*60)
        print("🎯 SYSTEM PERFORMANCE REPORT")
        print("="*60)
        print(f"Total Claims Processed: {report['total_claims_processed']}")
        print(f"Approval Rate: {report['approval_rate']}")
        print(f"Rejection Rate: {report['rejection_rate']}")
        print(f"Pending Rate: {report['pending_rate']}")
        print(f"Total Approved Amount: {report['total_approved_amount']}")
        print(f"Average Processing Time: {report['average_processing_time']}")
        
        print("\n📋 Claims Breakdown:")
        for status, count in report['claims_breakdown'].items():
            print(f"  {status.title()}: {count}")
        
        print("\n🤖 Agent Performance:")
        for agent_name, stats in report['agent_performance'].items():
            print(f"  {agent_name}:")
            print(f"    Success Rate: {stats['success_rate']}")
            print(f"    Average Time: {stats['avg_time']:.2f}s")
            print(f"    Total Runs: {stats['total_runs']}")
        
        print("="*60)


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
            "documents_available": ["medical_records", "x-ray", "bills", "discharge_summary"]
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
            "documents_available": ["medical_records", "ecg", "bills", "lab_reports"]
        },
        {
            "claim_id": "CLM001-2024-003",
            "patient_name": "Robert Johnson",
            "policy_number": "POL456789123",
            "claim_amount": 25000.00,
            "claim_date": "2024-09-17",
            "diagnosis": "Diabetes management and complications",
            "treatment_type": "Endocrinology - Diabetes care and monitoring",
            "hospital_name": "Max Hospital, Bangalore",
            "documents_available": ["medical_records", "blood_tests", "bills"]
        }
    ]


def main():
    """Main function demonstrating the complete claim processing system"""
    
    print("🚀 Starting Health Insurance Claim Processing System")
    print("="*60)
    
    # Initialize the claim processing system
    claim_system = HealthInsuranceClaimSystem()
    
    # Get sample claims
    sample_claims = create_sample_claims()
    
    print(f"\n📋 Processing {len(sample_claims)} sample claims...")
    
    # Option 1: Process claims individually
    print("\n🔄 INDIVIDUAL CLAIM PROCESSING:")
    for claim_data in sample_claims[:1]:  # Process first claim individually
        print(f"\nProcessing claim: {claim_data['claim_id']}")
        result = claim_system.process_single_claim(claim_data)
        print(f"Result: {result['status']} - ₹{result['approved_amount']:,.2f}")
    
    # Option 2: Process remaining claims in batch
    print("\n🔄 BATCH CLAIM PROCESSING:")
    if len(sample_claims) > 1:
        batch_result = claim_system.process_batch_claims(sample_claims[1:])
    
    # Generate system report
    print("\n📊 GENERATING SYSTEM REPORT:")
    system_report = claim_system.generate_system_report()
    
    # Save results to file
    print("\n💾 SAVING RESULTS:")
    saved_file = claim_system.save_results_to_file()
    
    # Demonstrate claim status lookup
    print("\n🔍 CLAIM STATUS LOOKUP:")
    for claim_data in sample_claims:
        status = claim_system.get_claim_status(claim_data['claim_id'])
        if status:
            print(f"Claim {status['claim_id']}: {status['status']} - ₹{status['approved_amount']:,.2f}")
    
    print("\n✅ SYSTEM DEMONSTRATION COMPLETE!")
    print("="*60)
    
    return claim_system


if __name__ == "__main__":
    # Run the main demonstration
    system = main()
    
    print("\n💡 USAGE EXAMPLES:")
    print("="*60)
    print("# Process a single claim:")
    print("result = system.process_single_claim(claim_data)")
    print()
    print("# Process multiple claims:")
    print("batch_result = system.process_batch_claims(claims_list)")
    print()
    print("# Get claim status:")
    print("status = system.get_claim_status('CLM001-2024-001')")
    print()
    print("# Generate system report:")
    print("report = system.generate_system_report()")
    print()
    print("# Save results:")
    print("filepath = system.save_results_to_file()")
    print("="*60)
