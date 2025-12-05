# Evidence collection service for Azure AI

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class EvidenceCollector:
    """Collects evidence from Azure AI indices for fraud analysis"""
    
    def __init__(self, workflow_manager, xray_api=None):
        self.workflow = workflow_manager
        self.xray_api = xray_api
    
    async def collect_all_evidence(self, claim_data, queries: Dict[str, str]) -> Dict[str, Any]:
        """Collect all evidence types for a claim"""
        print("\n🔍 STEP 1: Collecting Evidence from Azure AI Indices")
        print("-" * 60)
        
        try:
            thread_id = self.workflow.initialize_shared_thread()
            evidence = {}
            agents_to_cleanup = []
            
            # Medical Evidence
            evidence["medical"] = await self._collect_evidence(
                thread_id, "medical", "clm001-folder3-index",
                queries.get("medical", ""), "Medical"
            )
            
            # Billing Evidence
            evidence["billing"] = await self._collect_evidence(
                thread_id, "billing", "clm001-folder1-index",
                queries.get("billing", ""), "Billing"
            )
            
            # X-ray Evidence
            if self.xray_api:
                evidence["xray"] = await self._collect_xray_evidence(claim_data)
            
            # Policy Coverage Evidence
            evidence["policy_coverage"] = await self._collect_evidence(
                thread_id, "exclusions", "clm001-folder3-index",
                queries.get("policy_coverage", ""), "Policy Coverage"
            )
            
            # Detailed Exclusions Evidence
            evidence["detailed_exclusions"] = await self._collect_evidence(
                thread_id, "exclusions", "clm001-folder3-index",
                queries.get("exclusions", ""), "Detailed Exclusions"
            )
            
            # Add exclusions analysis
            evidence["exclusions_analysis"] = self._analyze_exclusions(claim_data)
            
            return evidence
            
        except Exception as e:
            return {"error": f"Evidence collection failed: {str(e)}"}
    
    async def _collect_evidence(
        self, thread_id: str, agent_type: str, index_name: str, 
        query: str, evidence_type: str
    ) -> str:
        """Collect evidence from a specific Azure AI agent"""
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
                result = last_msg.text.value if last_msg else f"No {evidence_type.lower()} evidence found"
                print(f"   ✅ {evidence_type} evidence collected")
            else:
                result = f"{evidence_type} evidence collection failed: {run.last_error}"
                print(f"   ❌ {evidence_type} evidence failed")
            
            # Cleanup agent
            try:
                self.workflow.project_client.agents.delete_agent(agent.id)
            except:
                pass
            
            return result
            
        except Exception as e:
            return f"{evidence_type} evidence collection failed: {str(e)}"
    
    async def _collect_xray_evidence(self, claim_data) -> str:
        """Collect and analyze X-ray evidence"""
        print("🩻 Collecting X-ray Evidence...")
        
        try:
            xray_results = self.xray_api.predict_all_images()
            analysis = self._analyze_xray_for_fraud(xray_results, claim_data)
            print("   ✅ X-ray evidence collected")
            return analysis
        except Exception as e:
            return f"X-ray evidence collection failed: {str(e)}"
    
    def _analyze_xray_for_fraud(self, xray_results: Dict[str, Any], claim_data) -> str:
        """Analyze X-ray results for fraud indicators"""
        analysis = f"X-ray Fraud Analysis for {claim_data.patient_name}:\n\n"
        analysis += f"Images Analyzed: {xray_results.get('total_images', 0)}\n"
        analysis += f"Successful Predictions: {xray_results.get('successful_predictions', 0)}\n\n"
        
        claimed_diagnosis = claim_data.diagnosis.lower()
        fraud_flags = []
        
        if xray_results.get("results"):
            analysis += "Fraud Detection Analysis:\n"
            for i, result in enumerate(xray_results["results"], 1):
                if result.get("success") and result.get("top_prediction"):
                    pred = result["top_prediction"]
                    grade = pred.get('tag_name', 'Unknown')
                    confidence = pred.get('confidence_percentage', '0%')
                    analysis += f"\nImage {i}: Grade {grade} ({confidence} confidence)\n"
                    
                    # Check for diagnosis mismatches
                    if "brain" in claimed_diagnosis or "neuro" in claimed_diagnosis:
                        if "osteoarthritis" in str(grade).lower():
                            fraud_flags.append("CRITICAL: Brain surgery claimed but orthopedic X-ray evidence")
                    
                    if "cardiac" in claimed_diagnosis or "heart" in claimed_diagnosis:
                        if "osteoarthritis" in str(grade).lower():
                            fraud_flags.append("CRITICAL: Cardiac procedure claimed but orthopedic X-ray evidence")
        
        if fraud_flags:
            analysis += "\n🚨 FRAUD INDICATORS DETECTED:\n"
            for flag in fraud_flags:
                analysis += f"  ❌ {flag}\n"
        else:
            analysis += "\n✅ No obvious fraud indicators in X-ray analysis\n"
        
        return analysis
    
    def _analyze_exclusions(self, claim_data) -> Dict[str, Any]:
        """Analyze common policy exclusions"""
        exclusions = {
            "potential_exclusions": [],
            "coverage_concerns": [],
            "validation_required": []
        }
        
        diagnosis = claim_data.diagnosis.lower()
        treatment = claim_data.treatment_type.lower()
        
        # Pre-existing condition check
        if any(kw in diagnosis for kw in ["chronic", "degenerative", "arthritis", "osteoarthritis"]):
            exclusions["potential_exclusions"].append({
                "type": "Pre-existing Condition",
                "concern": "Degenerative/chronic conditions may have waiting periods",
                "validation": "Check policy for pre-existing condition clauses"
            })
        
        # High-value claim check
        if claim_data.claim_amount > 300000:
            exclusions["coverage_concerns"].append({
                "type": "High-Value Claim",
                "concern": "High-value claims require enhanced validation",
                "validation": "Verify policy limits and sub-limits"
            })
        
        # Provider network check
        exclusions["validation_required"].append({
            "type": "Provider Network",
            "concern": "Hospital/provider network status affects coverage",
            "validation": f"Confirm {claim_data.hospital_name} is in policy network"
        })
        
        print(f"   🚫 Found {len(exclusions['potential_exclusions'])} potential exclusions")
        
        return exclusions
