# Fraud Detection Orchestrator - Refactored Version
# Uses Microsoft AutoGen for multi-agent fraud detection with Azure AI integration

import os
import time
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

try:
    from autogen import GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False

# Core modules
from core.config import get_llm_config, get_default_claim_data
from core.models import ClaimData, FraudDecision, WorkflowResult
from core.queries import (
    get_medical_evidence_query,
    get_billing_evidence_query,
    get_policy_coverage_query,
    get_exclusions_query
)
from core.utils import get_message_content

# Services
from services.agent_factory import AgentFactory
from services.decision_extractor import DecisionExtractor
from services.report_generator import ReportGenerator

# Workflow manager for Azure AI
from workflow_manager import HealthInsuranceWorkflowManager

# X-ray analysis
try:
    from agents.xrayanalysis import XRayAPI
    XRAY_AVAILABLE = True
except ImportError:
    XRAY_AVAILABLE = False

load_dotenv()


class FraudDetectionOrchestrator:
    """
    Multi-agent fraud detection orchestrator using Microsoft AutoGen.
    Coordinates specialized agents for comprehensive claim analysis.
    """
    
    def __init__(self, enable_xray: bool = True, enable_azure_evidence: bool = True):
        """
        Initialize the fraud detection orchestrator.
        
        Args:
            enable_xray: Enable X-ray analysis component
            enable_azure_evidence: Enable Azure AI evidence collection
        """
        self.enable_xray = enable_xray and XRAY_AVAILABLE
        self.enable_azure_evidence = enable_azure_evidence
        self.llm_config = get_llm_config()
        
        # Initialize components
        self._init_components()
        
        print("🚀 Fraud Detection Orchestrator initialized")
        print(f"   AutoGen: {'✅' if AUTOGEN_AVAILABLE else '❌'}")
        print(f"   X-ray Analysis: {'✅' if self.enable_xray else '❌'}")
        print(f"   Azure Evidence: {'✅' if self.enable_azure_evidence else '❌'}")
    
    def _init_components(self):
        """Initialize workflow and analysis components"""
        # Azure AI Workflow Manager
        if self.enable_azure_evidence:
            try:
                self.workflow = HealthInsuranceWorkflowManager()
            except Exception as e:
                print(f"⚠️ Azure workflow unavailable: {e}")
                self.workflow = None
                self.enable_azure_evidence = False
        else:
            self.workflow = None
        
        # X-ray Analysis API
        if self.enable_xray:
            try:
                self.xray_api = XRayAPI()
            except Exception as e:
                print(f"⚠️ X-ray API unavailable: {e}")
                self.xray_api = None
                self.enable_xray = False
        else:
            self.xray_api = None
    
    async def process_claim(self, claim_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a claim through the complete fraud detection workflow.
        
        Args:
            claim_data: Dictionary containing claim details. Uses defaults if not provided.
            
        Returns:
            Dictionary containing complete analysis results and fraud decision.
        """
        start_time = time.time()
        
        # Use default claim data if not provided
        if claim_data is None:
            claim_data = get_default_claim_data()
        
        print(f"\n{'='*80}")
        print(f"🏥 HEALTH INSURANCE FRAUD DETECTION SYSTEM")
        print(f"{'='*80}")
        print(f"Claim ID: {claim_data['claim_id']}")
        print(f"Patient: {claim_data['patient_name']}")
        print(f"Claim Amount: ₹{claim_data['claim_amount']:,.2f}")
        print(f"Diagnosis: {claim_data['diagnosis']}")
        print(f"{'='*80}")
        
        results = {
            "claim_id": claim_data["claim_id"],
            "patient_name": claim_data["patient_name"],
            "claim_amount": claim_data["claim_amount"],
            "processing_time": 0,
            "system_status": self._get_system_status(),
            "azure_evidence": {},
            "fraud_orchestration": {}
        }
        
        try:
            # Step 1: Collect Evidence
            evidence = await self._collect_evidence(claim_data)
            results["azure_evidence"] = evidence
            
            # Step 2: Run AutoGen multi-agent analysis
            fraud_result = await self._run_fraud_orchestration(claim_data, evidence)
            results["fraud_orchestration"] = fraud_result
            
        except Exception as e:
            results["error"] = str(e)
            results["fraud_orchestration"] = {
                "status": "failed",
                "error": str(e)
            }
        
        # Calculate processing time
        results["processing_time"] = time.time() - start_time
        
        # Print and save results
        reporter = ReportGenerator(claim_data)
        reporter.print_results(results)
        reporter.save_report(results)
        
        return results
    
    def _get_system_status(self) -> Dict[str, Any]:
        """Get current system component status"""
        return {
            "autogen_enabled": AUTOGEN_AVAILABLE,
            "xray_analysis_enabled": self.enable_xray,
            "azure_evidence_collection": self.enable_azure_evidence,
            "workflow_manager": self.workflow is not None,
            "xray_api": self.xray_api is not None
        }
    
    async def _collect_evidence(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect evidence from Azure AI indices"""
        
        if not self.enable_azure_evidence or not self.workflow:
            print("\n⚠️ Azure evidence collection disabled")
            return {"status": "disabled"}
        
        print("\n🔍 STEP 1: Collecting Evidence from Azure AI Indices")
        print("-" * 60)
        
        try:
            # Prepare queries
            queries = {
                "medical": get_medical_evidence_query(claim_data),
                "billing": get_billing_evidence_query(claim_data),
                "policy_coverage": get_policy_coverage_query(claim_data),
                "exclusions": get_exclusions_query(claim_data)
            }
            
            evidence = await self._collect_evidence_from_indices(claim_data, queries)
            
            print("\n✅ Evidence collection completed")
            return evidence
            
        except Exception as e:
            print(f"\n❌ Evidence collection failed: {e}")
            return {"error": str(e)}
    
    async def _collect_evidence_from_indices(
        self, claim_data: Dict[str, Any], queries: Dict[str, str]
    ) -> Dict[str, Any]:
        """Collect evidence from specific Azure AI indices"""
        
        evidence = {}
        thread_id = self.workflow.initialize_shared_thread()
        
        # Medical Evidence
        evidence["medical"] = await self._query_index(
            thread_id, "medical", "clm001-folder3-index", 
            queries["medical"], "Medical"
        )
        
        # Billing Evidence
        evidence["billing"] = await self._query_index(
            thread_id, "billing", "clm001-folder1-index",
            queries["billing"], "Billing"
        )
        
        # X-ray Evidence
        if self.enable_xray and self.xray_api:
            evidence["xray"] = await self._collect_xray_evidence(claim_data)
        
        # Policy Coverage
        evidence["policy_coverage"] = await self._query_index(
            thread_id, "exclusions", "clm001-folder3-index",
            queries["policy_coverage"], "Policy Coverage"
        )
        
        # Exclusions
        evidence["detailed_exclusions"] = await self._query_index(
            thread_id, "exclusions", "clm001-folder3-index",
            queries["exclusions"], "Exclusions"
        )
        
        # Exclusions Analysis
        evidence["exclusions_analysis"] = self._analyze_exclusions(claim_data)
        
        return evidence
    
    async def _query_index(
        self, thread_id: str, agent_type: str, index_name: str,
        query: str, evidence_type: str
    ) -> str:
        """Query a specific Azure AI index"""
        print(f"📋 Collecting {evidence_type} Evidence...")
        
        try:
            agent = self.workflow.create_specialist_agent(agent_type, index_name)
            
            self.workflow.project_client.agents.create_message(
                thread_id=thread_id, role="user", content=query
            )
            
            run = self.workflow.project_client.agents.create_and_process_run(
                thread_id=thread_id, agent_id=agent.id
            )
            
            if run.status != "failed":
                messages = self.workflow.project_client.agents.list_messages(thread_id=thread_id)
                last_msg = messages.get_last_text_message_by_role("assistant")
                result = last_msg.text.value if last_msg else f"No {evidence_type.lower()} evidence"
                print(f"   ✅ {evidence_type} evidence collected")
            else:
                result = f"{evidence_type} collection failed: {run.last_error}"
                print(f"   ❌ {evidence_type} evidence failed")
            
            # Cleanup
            try:
                self.workflow.project_client.agents.delete_agent(agent.id)
            except:
                pass
            
            return result
            
        except Exception as e:
            return f"{evidence_type} collection failed: {str(e)}"
    
    async def _collect_xray_evidence(self, claim_data: Dict[str, Any]) -> str:
        """Collect X-ray analysis evidence"""
        print("🩻 Collecting X-ray Evidence...")
        
        try:
            xray_results = self.xray_api.predict_all_images()
            analysis = self._analyze_xray_for_fraud(xray_results, claim_data)
            print("   ✅ X-ray evidence collected")
            return analysis
        except Exception as e:
            return f"X-ray evidence failed: {str(e)}"
    
    def _analyze_xray_for_fraud(self, xray_results: Dict[str, Any], claim_data: Dict[str, Any]) -> str:
        """Analyze X-ray results for fraud indicators"""
        analysis = f"X-ray Analysis for {claim_data['patient_name']}:\n\n"
        analysis += f"Images: {xray_results.get('total_images', 0)}\n"
        analysis += f"Successful: {xray_results.get('successful_predictions', 0)}\n\n"
        
        claimed_diagnosis = claim_data.get('diagnosis', '').lower()
        fraud_flags = []
        
        if xray_results.get("results"):
            for i, result in enumerate(xray_results["results"], 1):
                if result.get("success") and result.get("top_prediction"):
                    pred = result["top_prediction"]
                    grade = pred.get('tag_name', 'Unknown')
                    confidence = pred.get('confidence_percentage', '0%')
                    analysis += f"Image {i}: Grade {grade} ({confidence})\n"
                    
                    # Check for mismatches
                    if any(kw in claimed_diagnosis for kw in ["brain", "neuro", "cardiac", "heart"]):
                        if "osteoarthritis" in str(grade).lower():
                            fraud_flags.append(f"CRITICAL: {claimed_diagnosis} claimed but orthopedic X-ray found")
        
        if fraud_flags:
            analysis += "\n🚨 FRAUD INDICATORS:\n"
            for flag in fraud_flags:
                analysis += f"  ❌ {flag}\n"
        else:
            analysis += "\n✅ No obvious fraud indicators\n"
        
        return analysis
    
    def _analyze_exclusions(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze common policy exclusions"""
        exclusions = {
            "potential_exclusions": [],
            "coverage_concerns": [],
            "validation_required": []
        }
        
        diagnosis = claim_data.get('diagnosis', '').lower()
        
        # Pre-existing condition check
        if any(kw in diagnosis for kw in ["chronic", "degenerative", "arthritis"]):
            exclusions["potential_exclusions"].append({
                "type": "Pre-existing Condition",
                "concern": "May have waiting periods"
            })
        
        # High-value claim check
        if claim_data.get('claim_amount', 0) > 300000:
            exclusions["coverage_concerns"].append({
                "type": "High-Value Claim",
                "concern": "Requires enhanced validation"
            })
        
        return exclusions
    
    async def _run_fraud_orchestration(
        self, claim_data: Dict[str, Any], evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run AutoGen multi-agent fraud detection"""
        
        if not AUTOGEN_AVAILABLE:
            return {
                "status": "unavailable",
                "error": "AutoGen not installed"
            }
        
        print(f"\n🤖 STEP 2: AutoGen Multi-Agent Fraud Analysis")
        print("-" * 60)
        
        try:
            # Create agents
            factory = AgentFactory(claim_data, evidence)
            agents = factory.create_all_agents()
            agent_list = factory.get_agent_list(agents)
            
            print(f"Created {len(agents)} specialized agents")
            
            # Create group chat
            group_chat = GroupChat(
                agents=agent_list,
                messages=[],
                max_round=15,
                speaker_selection_method="round_robin"
            )
            
            manager = GroupChatManager(
                groupchat=group_chat,
                llm_config=self.llm_config
            )
            
            # Initial message
            initial_message = self._create_initial_message(claim_data)
            
            # Run conversation
            print("Starting fraud detection conversation...")
            await agents["user_proxy"].a_initiate_chat(
                manager,
                message=initial_message,
                clear_history=True
            )
            
            # Extract decision
            extractor = DecisionExtractor(claim_data)
            decision = extractor.extract_decision(group_chat.messages)
            
            return {
                "status": "completed",
                "fraud_decision": decision,
                "conversation_length": len(group_chat.messages)
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _create_initial_message(self, claim_data: Dict[str, Any]) -> str:
        """Create initial message for fraud detection workflow"""
        return f"""
        FRAUD DETECTION REQUEST - Claim Analysis Required
        
        Claim Details:
        - Claim ID: {claim_data['claim_id']}
        - Patient: {claim_data['patient_name']}
        - Age: {claim_data.get('age', 'Unknown')}
        - Claim Amount: ₹{claim_data['claim_amount']:,.2f}
        - Diagnosis: {claim_data['diagnosis']}
        - Treatment: {claim_data.get('treatment_type', 'Not specified')}
        - Hospital: {claim_data.get('hospital_name', 'Not specified')}
        
        Policy Information:
        - Policy Number: {claim_data.get('policy_number', 'Unknown')}
        - Coverage Limit: ₹{claim_data.get('policy_coverage_limit', 0):,.2f}
        - Previously Claimed: ₹{claim_data.get('previously_claimed_amount', 0):,.2f}
        - Available Balance: ₹{claim_data.get('available_balance', 0):,.2f}
        
        Please analyze this claim for fraud indicators and provide your assessment.
        """


async def main():
    """Main entry point"""
    orchestrator = FraudDetectionOrchestrator(
        enable_xray=True,
        enable_azure_evidence=True
    )
    
    results = await orchestrator.process_claim()
    
    print(f"\n✅ Fraud detection analysis completed in {results['processing_time']:.2f}s")
    return results


if __name__ == "__main__":
    asyncio.run(main())
