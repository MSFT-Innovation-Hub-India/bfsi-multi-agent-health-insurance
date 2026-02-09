# Health Insurance Claim Processing Workflow Manager
# This orchestrates multiple specialized agents using shared threads for comprehensive claim processing

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchTool, Tool

# Import our custom agents
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))
from xrayanalysis import XRayPredictionAPI

# Import centralized instructions
from core.instructions import AZURE_AGENT_INSTRUCTIONS, SEARCH_FIELD_MAPPINGS

# Load environment variables
load_dotenv()

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

class HealthInsuranceWorkflowManager:
    """
    Orchestrates multiple Azure AI Foundry agents for comprehensive health insurance claim processing
    """
    
    def __init__(self):
        # Azure AI Project config from environment variables
        self.endpoint = os.getenv("AZURE_ENDPOINT", "https://eastus2.api.azureml.ms")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP", "")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID", "")
        self.project_name = os.getenv("AZURE_PROJECT_NAME", "")
        
        # Initialize Azure AI Project client
        self.project_client = AIProjectClient(
            endpoint=self.endpoint,
            resource_group_name=self.resource_group,
            subscription_id=self.subscription_id,
            project_name=self.project_name,
            credential=DefaultAzureCredential()
        )
        
        # Find Azure AI Search connection
        self.conn_id = self._find_search_connection()
        
        # Initialize X-ray analysis API
        self.xray_api = XRayPredictionAPI()
        
        # Shared thread for agent coordination
        self.shared_thread = None
        
        # Agent instances
        self.agents = {}
        
        print(f"✅ Health Insurance Workflow Manager initialized")
        print(f"   Project: {self.project_name}")
        print(f"   Search Connection: {self.conn_id}")
    
    def _find_search_connection(self) -> str:
        """Find and return the Azure AI Search connection ID"""
        conn_list = self.project_client.connections.list()
        
        # Try to find fsisearchindex connection first
        for conn in conn_list:
            if conn.connection_type == "CognitiveSearch" and "fsisearchindex" in conn.id.lower():
                return conn.id
        
        # If not found, try fsi
        for conn in conn_list:
            if conn.connection_type == "CognitiveSearch" and "fsi" in conn.id.lower():
                return conn.id
        
        # Final fallback
        for conn in conn_list:
            if conn.connection_type == "CognitiveSearch":
                return conn.id
        
        raise ValueError("No Azure AI Search connection found")
    
    def initialize_shared_thread(self) -> str:
        """Initialize a shared thread for agent coordination"""
        if self.shared_thread is None:
            self.shared_thread = self.project_client.agents.create_thread()
            print(f"📧 Shared thread created: {self.shared_thread.id}")
        return self.shared_thread.id
    
    def create_specialist_agent(self, agent_type: str, index_name: str) -> Any:
        """Create a specialized agent based on type"""
        
        # Common AI Search tool setup using centralized field mappings
        try:
            ai_search = AzureAISearchTool(
                index_connection_id=self.conn_id,
                index_name=index_name,
                field_mappings=SEARCH_FIELD_MAPPINGS
            )
        except TypeError:
            ai_search = AzureAISearchTool(
                index_connection_id=self.conn_id,
                index_name=index_name
            )
        
        # Map agent_type to instruction keys
        instruction_key_map = {
            "billing": "billing_specialist",
            "medical": "medical_specialist",
            "exclusions": "exclusions_specialist",
            "coordinator": "claim_coordinator"
        }
        
        agent_name_map = {
            "billing": "billing-specialist",
            "medical": "medical-specialist",
            "exclusions": "exclusions-specialist",
            "coordinator": "claim-coordinator"
        }
        
        if agent_type not in instruction_key_map:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        instruction_key = instruction_key_map[agent_type]
        agent_name = agent_name_map[agent_type]
        
        agent = self.project_client.agents.create_agent(
            model="gpt-4o",
            name=agent_name,
            instructions=AZURE_AGENT_INSTRUCTIONS[instruction_key],
            tools=ai_search.definitions,
            tool_resources=ai_search.resources,
        )
        
        return agent
    
    def process_claim_with_workflow(self, claim_data: ClaimData) -> WorkflowResult:
        """
        Process a complete insurance claim using coordinated agent workflow
        """
        start_time = datetime.now()
        agent_results = []
        
        print(f"\n🏥 PROCESSING INSURANCE CLAIM: {claim_data.claim_id}")
        print(f"Patient: {claim_data.patient_name}")
        print(f"Claim Amount: ₹{claim_data.claim_amount:,.2f}")
        print(f"Diagnosis: {claim_data.diagnosis}")
        print("=" * 60)
        
        # Initialize shared thread
        thread_id = self.initialize_shared_thread()
        
        try:
            # Step 1: Medical Records Analysis
            print("\n📋 Step 1: Medical Records Analysis")
            medical_result = self._run_medical_analysis(claim_data, thread_id)
            agent_results.append(medical_result)
            
            # Step 2: Exclusions Check
            print("\n🚫 Step 2: Exclusions and Coverage Check")
            exclusions_result = self._run_exclusions_analysis(claim_data, thread_id)
            agent_results.append(exclusions_result)
            
            # Step 3: X-ray Analysis (if applicable)
            if "x-ray" in claim_data.documents_available or "xray" in claim_data.diagnosis.lower():
                print("\n🩻 Step 3: X-ray Analysis")
                xray_result = self._run_xray_analysis(claim_data)
                agent_results.append(xray_result)
            
            # Step 4: Billing Analysis
            print("\n💰 Step 4: Billing and Settlement Analysis")
            billing_result = self._run_billing_analysis(claim_data, thread_id)
            agent_results.append(billing_result)
            
            # Step 5: Final Coordination and Decision
            print("\n📊 Step 5: Final Coordination and Decision")
            final_result = self._run_final_coordination(claim_data, agent_results, thread_id)
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Generate final workflow result
            workflow_result = WorkflowResult(
                claim_id=claim_data.claim_id,
                final_status=self._determine_final_status(final_result),
                approved_amount=self._extract_approved_amount(final_result),
                total_processing_time=processing_time,
                agent_results=agent_results,
                final_report=final_result,
                recommendations=self._extract_recommendations(agent_results)
            )
            
            self._print_final_report(workflow_result)
            return workflow_result
            
        except Exception as e:
            print(f"❌ Error processing claim: {str(e)}")
            raise
        finally:
            # Clean up agents
            self._cleanup_agents()
    
    def _run_medical_analysis(self, claim_data: ClaimData, thread_id: str) -> AgentResult:
        """Run medical records analysis"""
        start_time = datetime.now()
        
        # Create medical specialist agent
        agent = self.create_specialist_agent("medical", "healthmedicalrecords")
        self.agents["medical"] = agent
        
        # Create analysis query
        query = f"""
        Analyze medical records for claim {claim_data.claim_id}:
        - Patient: {claim_data.patient_name}
        - Diagnosis: {claim_data.diagnosis}
        - Treatment: {claim_data.treatment_type}
        - Hospital: {claim_data.hospital_name}
        - Documents: {', '.join(claim_data.documents_available)}
        
        Provide medical necessity validation, treatment appropriateness assessment, 
        and clinical documentation review. Focus on:
        1) Medical history and diagnosis validation
        2) Treatment protocol compliance
        3) Documentation completeness
        4) Pre-existing condition assessment
        """
        
        # Add message to shared thread
        self.project_client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=query
        )
        
        # Run the agent
        run = self.project_client.agents.create_and_process_run(
            thread_id=thread_id,
            agent_id=agent.id
        )
        
        # Get results
        if run.status == "failed":
            analysis = f"Medical analysis failed: {run.last_error}"
            recommendations = ["Manual medical review required"]
        else:
            messages = self.project_client.agents.list_messages(thread_id=thread_id)
            last_msg = messages.get_last_text_message_by_role("assistant")
            analysis = last_msg.text.value if last_msg else "No medical analysis available"
            recommendations = self._extract_medical_recommendations(analysis)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return AgentResult(
            agent_name="Medical Records Specialist",
            status="completed" if run.status != "failed" else "failed",
            analysis=analysis,
            recommendations=recommendations,
            findings={"medical_necessity": "validated" if run.status != "failed" else "needs_review"},
            processing_time=processing_time
        )
    
    def _run_exclusions_analysis(self, claim_data: ClaimData, thread_id: str) -> AgentResult:
        """Run exclusions and coverage analysis"""
        start_time = datetime.now()
        
        # Create exclusions specialist agent
        agent = self.create_specialist_agent("exclusions", "healthclaims")
        self.agents["exclusions"] = agent
        
        # Create analysis query
        query = f"""
        Check exclusions and coverage for claim {claim_data.claim_id}:
        - Diagnosis: {claim_data.diagnosis}
        - Treatment: {claim_data.treatment_type}
        - Claim Amount: ₹{claim_data.claim_amount:,.2f}
        
        Review policy exclusions, coverage limitations, and restrictions that may apply.
        Focus on:
        1) Treatment-specific exclusions
        2) Policy coverage limits
        3) Pre-existing condition exclusions
        4) Non-medical items exclusions
        5) Coverage recommendations
        """
        
        # Add message to shared thread
        self.project_client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=query
        )
        
        # Run the agent
        run = self.project_client.agents.create_and_process_run(
            thread_id=thread_id,
            agent_id=agent.id
        )
        
        # Get results
        if run.status == "failed":
            analysis = f"Exclusions analysis failed: {run.last_error}"
            recommendations = ["Manual exclusions review required"]
        else:
            messages = self.project_client.agents.list_messages(thread_id=thread_id)
            last_msg = messages.get_last_text_message_by_role("assistant")
            analysis = last_msg.text.value if last_msg else "No exclusions analysis available"
            recommendations = self._extract_exclusions_recommendations(analysis)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return AgentResult(
            agent_name="Exclusions Specialist",
            status="completed" if run.status != "failed" else "failed",
            analysis=analysis,
            recommendations=recommendations,
            findings={"exclusions_found": self._check_exclusions_found(analysis)},
            processing_time=processing_time
        )
    
    def _run_xray_analysis(self, claim_data: ClaimData) -> AgentResult:
        """Run X-ray analysis using Custom Vision API"""
        start_time = datetime.now()
        
        try:
            # Run X-ray analysis
            xray_results = self.xray_api.predict_all_images()
            
            # Format analysis
            if xray_results.get("success", False) or xray_results.get("total_images", 0) > 0:
                analysis = self._format_xray_analysis(xray_results)
                recommendations = self._extract_xray_recommendations(xray_results)
                status = "completed"
                findings = {
                    "total_images": xray_results.get("total_images", 0),
                    "successful_predictions": xray_results.get("successful_predictions", 0),
                    "has_abnormalities": self._check_xray_abnormalities(xray_results)
                }
            else:
                analysis = "No X-ray images found or analysis failed"
                recommendations = ["Manual X-ray review recommended"]
                status = "failed"
                findings = {"total_images": 0}
            
        except Exception as e:
            analysis = f"X-ray analysis error: {str(e)}"
            recommendations = ["Technical issue - manual X-ray review required"]
            status = "failed"
            findings = {"error": str(e)}
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return AgentResult(
            agent_name="X-ray Analysis Specialist",
            status=status,
            analysis=analysis,
            recommendations=recommendations,
            findings=findings,
            processing_time=processing_time
        )
    
    def _run_billing_analysis(self, claim_data: ClaimData, thread_id: str) -> AgentResult:
        """Run billing and settlement analysis"""
        start_time = datetime.now()
        
        # Create billing specialist agent
        agent = self.create_specialist_agent("billing", "healthbills")
        self.agents["billing"] = agent
        
        # Create analysis query
        query = f"""
        Analyze billing and settlement for claim {claim_data.claim_id}:
        - Claim Amount: ₹{claim_data.claim_amount:,.2f}
        - Diagnosis: {claim_data.diagnosis}
        - Treatment: {claim_data.treatment_type}
        - Hospital: {claim_data.hospital_name}
        
        Calculate final settlement considering:
        1) Eligible medical expenses
        2) Policy coverage limits and sub-limits
        3) Co-payment and deductibles
        4) Room rent restrictions
        5) Network vs non-network differences
        6) Final approved amount recommendation
        
        Provide itemized breakdown with specific amounts in Indian Rupees.
        """
        
        # Add message to shared thread
        self.project_client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=query
        )
        
        # Run the agent
        run = self.project_client.agents.create_and_process_run(
            thread_id=thread_id,
            agent_id=agent.id
        )
        
        # Get results
        if run.status == "failed":
            analysis = f"Billing analysis failed: {run.last_error}"
            recommendations = ["Manual billing review required"]
        else:
            messages = self.project_client.agents.list_messages(thread_id=thread_id)
            last_msg = messages.get_last_text_message_by_role("assistant")
            analysis = last_msg.text.value if last_msg else "No billing analysis available"
            recommendations = self._extract_billing_recommendations(analysis)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return AgentResult(
            agent_name="Billing Specialist",
            status="completed" if run.status != "failed" else "failed",
            analysis=analysis,
            recommendations=recommendations,
            findings={"settlement_calculated": run.status != "failed"},
            processing_time=processing_time
        )
    
    def _run_final_coordination(self, claim_data: ClaimData, agent_results: List[AgentResult], thread_id: str) -> str:
        """Run final coordination and decision making"""
        
        # Create coordinator agent
        agent = self.create_specialist_agent("coordinator", "healthbills")
        self.agents["coordinator"] = agent
        
        # Summarize all agent findings
        summary = f"""
        Final coordination for claim {claim_data.claim_id}:
        
        CLAIM DETAILS:
        - Patient: {claim_data.patient_name}
        - Claim Amount: ₹{claim_data.claim_amount:,.2f}
        - Diagnosis: {claim_data.diagnosis}
        
        AGENT ANALYSES:
        """
        
        for result in agent_results:
            summary += f"\n{result.agent_name} ({result.status}):\n"
            summary += f"Key findings: {result.findings}\n"
            summary += f"Recommendations: {', '.join(result.recommendations[:3])}\n"
        
        summary += """
        
        REQUIRED FINAL DECISION:
        1) Final claim status (APPROVED/REJECTED/PENDING)
        2) Approved amount with detailed justification
        3) Overall recommendations and next steps
        4) Summary of key factors influencing the decision
        
        Provide comprehensive final report with clear decision rationale.
        """
        
        # Add message to shared thread
        self.project_client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=summary
        )
        
        # Run the coordinator agent
        run = self.project_client.agents.create_and_process_run(
            thread_id=thread_id,
            agent_id=agent.id
        )
        
        # Get final results
        if run.status == "failed":
            return f"Final coordination failed: {run.last_error}"
        else:
            messages = self.project_client.agents.list_messages(thread_id=thread_id)
            last_msg = messages.get_last_text_message_by_role("assistant")
            return last_msg.text.value if last_msg else "No final coordination analysis available"
    
    def _determine_final_status(self, final_report: str) -> ClaimStatus:
        """Determine final claim status from coordinator report"""
        report_lower = final_report.lower()
        
        if "approved" in report_lower and "rejected" not in report_lower:
            return ClaimStatus.APPROVED
        elif "rejected" in report_lower:
            return ClaimStatus.REJECTED
        elif "pending" in report_lower or "additional" in report_lower:
            return ClaimStatus.PENDING_INFO
        else:
            return ClaimStatus.UNDER_REVIEW
    
    def _extract_approved_amount(self, final_report: str) -> float:
        """Extract approved amount from final report"""
        # Look for currency patterns in the report
        import re
        
        # Pattern for Indian Rupees
        patterns = [
            r'₹[\d,]+\.?\d*',
            r'Rs\.?\s*[\d,]+\.?\d*',
            r'INR\s*[\d,]+\.?\d*',
            r'approved.*?(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'settlement.*?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, final_report, re.IGNORECASE)
            for match in matches:
                # Clean and convert to float
                clean_amount = re.sub(r'[^\d.]', '', str(match))
                try:
                    amounts.append(float(clean_amount))
                except ValueError:
                    continue
        
        # Return the largest amount found (likely the approved amount)
        return max(amounts) if amounts else 0.0
    
    def _extract_recommendations(self, agent_results: List[AgentResult]) -> List[str]:
        """Extract key recommendations from all agent results"""
        all_recommendations = []
        for result in agent_results:
            all_recommendations.extend(result.recommendations[:2])  # Top 2 from each agent
        return all_recommendations[:8]  # Limit to top 8 overall
    
    def _cleanup_agents(self):
        """Clean up all created agents"""
        for agent_name, agent in self.agents.items():
            try:
                self.project_client.agents.delete_agent(agent.id)
                print(f"✅ Cleaned up {agent_name} agent")
            except Exception as e:
                print(f"⚠️ Warning: Could not clean up {agent_name} agent: {e}")
        self.agents.clear()
    
    def _print_final_report(self, result: WorkflowResult):
        """Print comprehensive final report"""
        print("\n" + "="*80)
        print("🏥 HEALTH INSURANCE CLAIM PROCESSING REPORT")
        print("="*80)
        print(f"Claim ID: {result.claim_id}")
        print(f"Final Status: {result.final_status.value.upper()}")
        print(f"Approved Amount: ₹{result.approved_amount:,.2f}")
        print(f"Processing Time: {result.total_processing_time:.2f} seconds")
        print(f"Completed: {result.completed_at}")
        
        print(f"\n📋 AGENT PROCESSING SUMMARY:")
        print("-" * 40)
        for agent_result in result.agent_results:
            print(f"{agent_result.agent_name}: {agent_result.status} ({agent_result.processing_time:.1f}s)")
        
        print(f"\n🎯 KEY RECOMMENDATIONS:")
        print("-" * 40)
        for i, rec in enumerate(result.recommendations, 1):
            print(f"{i}. {rec}")
        
        print(f"\n📊 DETAILED FINAL ANALYSIS:")
        print("-" * 40)
        print(result.final_report)
        print("="*80)
    
    # Helper methods for extracting information from agent responses
    def _extract_medical_recommendations(self, analysis: str) -> List[str]:
        """Extract medical recommendations from analysis"""
        # Simple extraction - in production, use more sophisticated NLP
        recommendations = []
        if "pre-existing" in analysis.lower():
            recommendations.append("Review pre-existing conditions")
        if "medical necessity" in analysis.lower():
            recommendations.append("Medical necessity validated")
        if "documentation" in analysis.lower():
            recommendations.append("Check documentation completeness")
        return recommendations[:3]
    
    def _extract_exclusions_recommendations(self, analysis: str) -> List[str]:
        """Extract exclusions recommendations from analysis"""
        recommendations = []
        if "excluded" in analysis.lower():
            recommendations.append("Exclusions identified - review coverage")
        if "covered" in analysis.lower():
            recommendations.append("Treatment appears covered")
        if "limitation" in analysis.lower():
            recommendations.append("Policy limitations apply")
        return recommendations[:3]
    
    def _extract_billing_recommendations(self, analysis: str) -> List[str]:
        """Extract billing recommendations from analysis"""
        recommendations = []
        if "approved" in analysis.lower():
            recommendations.append("Settlement calculation completed")
        if "deductible" in analysis.lower():
            recommendations.append("Apply policy deductibles")
        if "co-payment" in analysis.lower():
            recommendations.append("Co-payment applicable")
        return recommendations[:3]
    
    def _check_exclusions_found(self, analysis: str) -> bool:
        """Check if exclusions were found in analysis"""
        return "excluded" in analysis.lower() or "not covered" in analysis.lower()
    
    def _format_xray_analysis(self, xray_results: Dict[str, Any]) -> str:
        """Format X-ray analysis results"""
        if not xray_results.get("results"):
            return "No X-ray analysis results available"
        
        analysis = f"X-ray Analysis Summary:\n"
        analysis += f"Total Images Analyzed: {xray_results.get('total_images', 0)}\n"
        analysis += f"Successful Predictions: {xray_results.get('successful_predictions', 0)}\n\n"
        
        for i, result in enumerate(xray_results.get("results", [])[:3], 1):  # Show top 3
            if result.get("success") and result.get("top_prediction"):
                pred = result["top_prediction"]
                analysis += f"Image {i}: {pred.get('tag_name', 'Unknown')} "
                analysis += f"({pred.get('confidence_percentage', '0%')})\n"
                analysis += f"Description: {pred.get('description', 'No description')}\n\n"
        
        return analysis
    
    def _extract_xray_recommendations(self, xray_results: Dict[str, Any]) -> List[str]:
        """Extract X-ray recommendations"""
        recommendations = []
        
        if xray_results.get("successful_predictions", 0) > 0:
            # Check for severe findings
            for result in xray_results.get("results", []):
                if result.get("success") and result.get("top_prediction"):
                    grade = result["top_prediction"].get("tag_name", "").lower()
                    if "grade 4" in grade or "severe" in grade:
                        recommendations.append("Severe osteoarthritis detected - specialist consultation recommended")
                    elif "grade 3" in grade or "moderate" in grade:
                        recommendations.append("Moderate osteoarthritis detected - treatment justified")
                    elif "grade 0" in grade or "healthy" in grade:
                        recommendations.append("Normal X-ray findings")
        else:
            recommendations.append("X-ray analysis inconclusive - manual review required")
        
        return recommendations[:3]
    
    def _check_xray_abnormalities(self, xray_results: Dict[str, Any]) -> bool:
        """Check if X-ray shows abnormalities"""
        for result in xray_results.get("results", []):
            if result.get("success") and result.get("top_prediction"):
                grade = result["top_prediction"].get("tag_name", "").lower()
                if "grade" in grade and not "grade 0" in grade:
                    return True
        return False


# Example usage and testing
def main():
    """Main function for testing the workflow manager"""
    
    # Create sample claim data
    sample_claim = ClaimData(
        claim_id="CLM001-2024-001",
        patient_name="John Doe",
        policy_number="POL123456789",
        claim_amount=75000.00,
        claim_date="2024-09-15",
        diagnosis="Knee Osteoarthritis with joint replacement surgery",
        treatment_type="Orthopedic Surgery - Total Knee Replacement",
        hospital_name="Apollo Hospital, Delhi",
        documents_available=["medical_records", "x-ray", "bills", "discharge_summary"]
    )
    
    # Initialize workflow manager
    workflow_manager = HealthInsuranceWorkflowManager()
    
    # Process the claim
    print("🚀 Starting comprehensive claim processing workflow...")
    result = workflow_manager.process_claim_with_workflow(sample_claim)
    
    # Print additional insights
    print(f"\n💡 WORKFLOW INSIGHTS:")
    print(f"   Total agents used: {len(result.agent_results)}")
    print(f"   Processing efficiency: {result.total_processing_time:.1f}s total")
    print(f"   Final decision: {result.final_status.value}")
    
    return result

if __name__ == "__main__":
    main()