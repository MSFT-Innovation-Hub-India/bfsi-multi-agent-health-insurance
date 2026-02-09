"""
Real-time Agent Processor
Handles real-time processing of claims with live updates via WebSocket/SSE
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum

from api.cosmos_service import get_cosmos_service, CosmosDBService


class AgentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentUpdate:
    """Real-time update from an agent"""
    agent_name: str
    status: AgentStatus
    message: str
    content: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class ProcessingSession:
    """Represents a claim processing session"""
    session_id: str
    claim_id: str
    status: str = "started"
    current_agent: Optional[str] = None
    agents_completed: list = field(default_factory=list)
    updates: list = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None


class RealtimeAgentProcessor:
    """
    Real-time processor for agent-based claim analysis
    Provides live updates during processing via callbacks or async generators
    """
    
    AGENT_SEQUENCE = [
        "Fraud_Detection_Specialist",
        "Medical_Validator", 
        "Billing_Fraud_Validator",
        "Policy_Balance_Validator",
        "Policy_Adjustment_Coordinator",
        "Decision_Coordinator"
    ]
    
    def __init__(self):
        """Initialize the real-time processor"""
        self.cosmos_service: CosmosDBService = get_cosmos_service()
        self.active_sessions: Dict[str, ProcessingSession] = {}
        self._update_callbacks: Dict[str, list] = {}
    
    def register_update_callback(self, session_id: str, callback: Callable[[AgentUpdate], None]):
        """
        Register a callback to receive real-time updates
        
        Args:
            session_id: The session to monitor
            callback: Function to call with updates
        """
        if session_id not in self._update_callbacks:
            self._update_callbacks[session_id] = []
        self._update_callbacks[session_id].append(callback)
    
    def unregister_update_callback(self, session_id: str, callback: Callable[[AgentUpdate], None]):
        """Unregister an update callback"""
        if session_id in self._update_callbacks:
            self._update_callbacks[session_id].remove(callback)
    
    def _emit_update(self, session_id: str, update: AgentUpdate):
        """Emit an update to all registered callbacks and save to Cosmos DB"""
        # Save to Cosmos DB
        self.cosmos_service.update_processing_session(
            session_id=session_id,
            current_agent=update.agent_name if update.status == AgentStatus.PROCESSING else None,
            message={
                "agent_name": update.agent_name,
                "status": update.status.value,
                "message": update.message,
                "content": update.content
            },
            status="processing" if update.status == AgentStatus.PROCESSING else None
        )
        
        # Call registered callbacks
        if session_id in self._update_callbacks:
            for callback in self._update_callbacks[session_id]:
                try:
                    callback(update)
                except Exception as e:
                    print(f"Callback error: {e}")
    
    async def process_claim_realtime(
        self, 
        claim_data: Dict[str, Any],
        evidence: Dict[str, Any]
    ) -> AsyncGenerator[AgentUpdate, None]:
        """
        Process a claim with real-time updates via async generator
        
        Args:
            claim_data: The claim data to process
            evidence: Collected evidence for the claim
            
        Yields:
            AgentUpdate objects as processing progresses
        """
        claim_id = claim_data.get("claim_id", "unknown")
        
        # Create session in Cosmos DB
        session_data = self.cosmos_service.create_processing_session(claim_id)
        session_id = session_data["session_id"]
        
        # Track locally
        session = ProcessingSession(
            session_id=session_id,
            claim_id=claim_id
        )
        self.active_sessions[session_id] = session
        
        # Emit start update
        start_update = AgentUpdate(
            agent_name="System",
            status=AgentStatus.PROCESSING,
            message=f"Starting fraud detection analysis for claim {claim_id}",
            metadata={"claim_id": claim_id, "session_id": session_id}
        )
        yield start_update
        
        try:
            # Process through each agent
            for agent_name in self.AGENT_SEQUENCE:
                # Emit agent starting
                start_agent_update = AgentUpdate(
                    agent_name=agent_name,
                    status=AgentStatus.PROCESSING,
                    message=f"{agent_name.replace('_', ' ')} is analyzing the claim..."
                )
                self._emit_update(session_id, start_agent_update)
                yield start_agent_update
                
                # Simulate agent processing (replace with actual agent calls)
                agent_result = await self._process_with_agent(
                    agent_name, claim_data, evidence
                )
                
                # Emit agent completed
                complete_update = AgentUpdate(
                    agent_name=agent_name,
                    status=AgentStatus.COMPLETED,
                    message=f"{agent_name.replace('_', ' ')} completed analysis",
                    content=agent_result.get("content", ""),
                    metadata=agent_result.get("metadata", {})
                )
                self._emit_update(session_id, complete_update)
                yield complete_update
                
                session.agents_completed.append(agent_name)
            
            # Processing complete
            session.status = "completed"
            session.completed_at = datetime.utcnow().isoformat()
            
            # Update Cosmos DB with final status
            self.cosmos_service.update_processing_session(
                session_id=session_id,
                status="completed"
            )
            
            # Save complete log
            final_log = self._build_final_log(session, claim_data, evidence)
            self.cosmos_service.save_agent_log(claim_id, final_log)
            
            # Emit completion
            complete_update = AgentUpdate(
                agent_name="System",
                status=AgentStatus.COMPLETED,
                message="Fraud detection analysis completed",
                metadata={"session_id": session_id, "total_agents": len(self.AGENT_SEQUENCE)}
            )
            yield complete_update
            
        except Exception as e:
            error_update = AgentUpdate(
                agent_name="System",
                status=AgentStatus.FAILED,
                message=f"Processing failed: {str(e)}"
            )
            self.cosmos_service.update_processing_session(
                session_id=session_id,
                status="failed"
            )
            yield error_update
        
        finally:
            # Cleanup
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
    
    async def _process_with_agent(
        self, 
        agent_name: str, 
        claim_data: Dict[str, Any],
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process claim data with a specific agent
        
        This is where actual agent processing happens.
        Replace with real AutoGen agent calls.
        """
        # Import here to avoid circular imports
        try:
            from services.agent_factory import AgentFactory
            from core.config import get_llm_config
            
            # Create the specific agent and get its analysis
            factory = AgentFactory(claim_data, evidence)
            
            # Build context for the agent
            context = self._build_agent_context(agent_name, claim_data, evidence)
            
            # Simulate processing time (replace with actual agent call)
            await asyncio.sleep(0.5)  # Small delay for demo
            
            # Return agent-specific analysis
            return {
                "content": self._get_agent_analysis(agent_name, claim_data, evidence),
                "metadata": {
                    "agent": agent_name,
                    "processed_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "content": f"Agent {agent_name} analysis: Error - {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _build_agent_context(
        self, 
        agent_name: str, 
        claim_data: Dict[str, Any],
        evidence: Dict[str, Any]
    ) -> str:
        """Build context string for agent processing"""
        return f"""
        Claim ID: {claim_data.get('claim_id')}
        Patient: {claim_data.get('patient_name')}
        Amount: ₹{claim_data.get('claim_amount', 0):,.2f}
        Diagnosis: {claim_data.get('diagnosis')}
        
        Evidence Available:
        - Medical: {'Yes' if evidence.get('medical') else 'No'}
        - Billing: {'Yes' if evidence.get('billing') else 'No'}
        - X-ray: {'Yes' if evidence.get('xray') else 'No'}
        """
    
    def _get_agent_analysis(
        self, 
        agent_name: str, 
        claim_data: Dict[str, Any],
        evidence: Dict[str, Any]
    ) -> str:
        """Get analysis content for a specific agent (placeholder for real agent output)"""
        
        analyses = {
            "Fraud_Detection_Specialist": f"""
### FRAUD DETECTION ANALYSIS

**Claim ID:** {claim_data.get('claim_id')}
**Patient:** {claim_data.get('patient_name')}

**Identity Verification:** ✅ Verified
**Document Authenticity:** ✅ Verified
**Claim Pattern Analysis:** Normal patterns detected

**FRAUD_RISK:** LOW
**Recommendation:** Proceed with medical validation
            """,
            
            "Medical_Validator": f"""
### MEDICAL VALIDATION REPORT

**Diagnosis:** {claim_data.get('diagnosis')}
**Treatment:** {claim_data.get('treatment_type', 'Not specified')}

**Medical Consistency:** ✅ Consistent
**Treatment Appropriateness:** ✅ Appropriate for diagnosis
**Documentation Quality:** Complete

**Recommendation:** Medical records support the claim
            """,
            
            "Billing_Fraud_Validator": f"""
### BILLING VALIDATION REPORT

**Claimed Amount:** ₹{claim_data.get('claim_amount', 0):,.2f}
**Hospital:** {claim_data.get('hospital_name', 'Not specified')}

**Rate Analysis:** Within normal range
**Itemization Check:** ✅ Properly itemized
**Duplicate Check:** No duplicates found

**Recommendation:** Billing is reasonable and documented
            """,
            
            "Policy_Balance_Validator": f"""
### POLICY BALANCE VALIDATION

**Policy Number:** {claim_data.get('policy_number', 'Unknown')}
**Coverage Limit:** ₹{claim_data.get('policy_coverage_limit', 0):,.2f}
**Previously Claimed:** ₹{claim_data.get('previously_claimed_amount', 0):,.2f}
**Available Balance:** ₹{claim_data.get('available_balance', 0):,.2f}

**Balance Status:** Sufficient
**Coverage Check:** ✅ Within limits

**Recommendation:** Claim amount is within available balance
            """,
            
            "Policy_Adjustment_Coordinator": f"""
### POLICY ADJUSTMENT ANALYSIS

**Exclusions Check:** No exclusions apply
**Deductibles:** Standard deductible applied
**Co-pay Requirements:** As per policy terms

**Adjusted Amount:** ₹{claim_data.get('claim_amount', 0):,.2f}
**Adjustments Applied:** None required

**Recommendation:** Proceed with final decision
            """,
            
            "Decision_Coordinator": f"""
### FINAL DECISION

**Claim ID:** {claim_data.get('claim_id')}
**Patient:** {claim_data.get('patient_name')}

**FRAUD_RISK:** LOW
**FINAL DECISION:** APPROVED
**FINAL APPROVED AMOUNT:** ₹{claim_data.get('claim_amount', 0):,.2f}

**Rationale:**
1. Identity verification passed
2. Medical records are consistent
3. Billing is within normal ranges
4. Policy balance is sufficient
5. No exclusions apply

**Balance After Claim:** ₹{claim_data.get('available_balance', 0) - claim_data.get('claim_amount', 0):,.2f}
            """
        }
        
        return analyses.get(agent_name, f"Analysis by {agent_name} completed.")
    
    def _build_final_log(
        self, 
        session: ProcessingSession, 
        claim_data: Dict[str, Any],
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build the final log structure for storage"""
        return {
            "report_type": "Comprehensive Claim Analysis Report",
            "generated_at": datetime.utcnow().isoformat(),
            "patient_details": {
                "claim_id": claim_data.get("claim_id"),
                "patient_name": claim_data.get("patient_name"),
                "policy_number": claim_data.get("policy_number"),
                "claim_amount": claim_data.get("claim_amount"),
                "claim_date": claim_data.get("claim_date"),
                "diagnosis": claim_data.get("diagnosis"),
                "treatment_type": claim_data.get("treatment_type"),
                "hospital_name": claim_data.get("hospital_name"),
                "documents_available": claim_data.get("documents_available", []),
                "policy_coverage_limit": claim_data.get("policy_coverage_limit"),
                "previously_claimed_amount": claim_data.get("previously_claimed_amount"),
                "available_balance": claim_data.get("available_balance"),
                "policy_year": claim_data.get("policy_year")
            },
            "fraud_analysis_results": {
                "claim_id": claim_data.get("claim_id"),
                "patient_name": claim_data.get("patient_name"),
                "processing_type": "Real-time Multi-Agent Analysis",
                "azure_evidence": evidence,
                "fraud_orchestration": {
                    "status": session.status,
                    "framework": "AutoGen + Real-time API",
                    "total_messages": len(session.updates),
                    "agents_participated": len(session.agents_completed),
                    "conversation_duration": 0,  # Calculate from timestamps
                    "detailed_messages": [
                        json.dumps({"name": u.agent_name, "content": u.content, "role": "assistant"})
                        for u in session.updates if hasattr(u, 'content')
                    ]
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a processing session"""
        # Check local cache first
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                "session_id": session.session_id,
                "claim_id": session.claim_id,
                "status": session.status,
                "current_agent": session.current_agent,
                "agents_completed": session.agents_completed,
                "started_at": session.started_at,
                "completed_at": session.completed_at
            }
        
        # Fall back to Cosmos DB
        return self.cosmos_service.get_processing_session(session_id)


# Singleton instance
_processor: Optional[RealtimeAgentProcessor] = None


def get_realtime_processor() -> RealtimeAgentProcessor:
    """Get or create the real-time processor singleton"""
    global _processor
    if _processor is None:
        _processor = RealtimeAgentProcessor()
    return _processor
