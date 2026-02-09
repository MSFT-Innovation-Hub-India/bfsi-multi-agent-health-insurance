"""
Health Insurance Claims Processing API
FastAPI application providing REST and WebSocket endpoints for claim processing
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

from api.cosmos_service import get_cosmos_service, CosmosDBService
from api.realtime_processor import get_realtime_processor, RealtimeAgentProcessor, AgentUpdate


# ==================== PYDANTIC MODELS ====================

class ClaimInput(BaseModel):
    """Input model for claim data"""
    claim_id: str
    patient_name: str
    policy_number: str
    claim_amount: float
    claim_date: str
    diagnosis: str
    treatment_type: Optional[str] = None
    hospital_name: Optional[str] = None
    documents_available: Optional[List[str]] = []
    policy_coverage_limit: Optional[float] = 500000
    previously_claimed_amount: Optional[float] = 0
    available_balance: Optional[float] = None
    policy_year: Optional[str] = "2024-2025"
    age: Optional[int] = None


class ClaimResponse(BaseModel):
    """Response model for claim operations"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ProcessingSessionResponse(BaseModel):
    """Response model for processing session"""
    session_id: str
    claim_id: str
    status: str
    current_agent: Optional[str] = None
    agents_completed: List[str] = []
    started_at: str
    completed_at: Optional[str] = None


class AgentLogResponse(BaseModel):
    """Response model for agent logs"""
    claim_id: str
    logs: List[Dict[str, Any]]


# ==================== CONNECTION MANAGER ====================

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def broadcast(self, session_id: str, message: Dict[str, Any]):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()


# ==================== APP LIFECYCLE ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Health Insurance Claims API...")
    try:
        cosmos_service = get_cosmos_service()
        print("✅ Cosmos DB connection established")
    except Exception as e:
        print(f"⚠️ Cosmos DB connection failed: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Health Insurance Claims API...")


# ==================== FASTAPI APP ====================

app = FastAPI(
    title="Health Insurance Claims Processing API",
    description="Real-time multi-agent fraud detection and claims processing API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== HEALTH CHECK ====================

@app.get("/")
async def root():
    """Root endpoint - API welcome"""
    return {
        "name": "Health Insurance Claims Processing API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "api_status": "/api/status"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Health Insurance Claims API"
    }


@app.get("/api/status")
async def api_status():
    """Get API and service status"""
    cosmos_available = False
    try:
        cosmos_service = get_cosmos_service()
        cosmos_available = cosmos_service.client is not None
    except:
        pass
    
    return {
        "api_version": "1.0.0",
        "cosmos_db": "connected" if cosmos_available else "disconnected",
        "realtime_processing": "available",
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== CLAIM ENDPOINTS ====================

@app.post("/api/claims", response_model=ClaimResponse)
async def create_claim(claim: ClaimInput):
    """Create or update a claim"""
    try:
        cosmos_service = get_cosmos_service()
        claim_data = claim.model_dump()
        
        # Calculate available balance if not provided
        if claim_data.get("available_balance") is None:
            claim_data["available_balance"] = (
                claim_data.get("policy_coverage_limit", 500000) - 
                claim_data.get("previously_claimed_amount", 0)
            )
        
        saved_claim = cosmos_service.save_claim(claim_data)
        return ClaimResponse(
            success=True,
            message=f"Claim {claim.claim_id} saved successfully",
            data=saved_claim
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/claims", response_model=ClaimResponse)
async def get_claims(limit: int = Query(default=100, le=1000)):
    """Get all claims"""
    try:
        cosmos_service = get_cosmos_service()
        claims = cosmos_service.get_all_claims(limit=limit)
        return ClaimResponse(
            success=True,
            message=f"Retrieved {len(claims)} claims",
            data={"claims": claims, "total": len(claims)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/claims/{claim_id}", response_model=ClaimResponse)
async def get_claim(claim_id: str):
    """Get a specific claim by ID"""
    try:
        cosmos_service = get_cosmos_service()
        claim = cosmos_service.get_claim(claim_id)
        if claim is None:
            raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
        return ClaimResponse(
            success=True,
            message=f"Retrieved claim {claim_id}",
            data=claim
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/claims/{claim_id}", response_model=ClaimResponse)
async def delete_claim(claim_id: str):
    """Delete a claim"""
    try:
        cosmos_service = get_cosmos_service()
        deleted = cosmos_service.delete_claim(claim_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
        return ClaimResponse(
            success=True,
            message=f"Claim {claim_id} deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AGENT LOGS ENDPOINTS ====================

@app.get("/api/claims/{claim_id}/logs")
async def get_claim_logs(claim_id: str):
    """Get all agent processing logs for a claim"""
    try:
        cosmos_service = get_cosmos_service()
        logs = cosmos_service.get_agent_logs(claim_id)
        return {
            "success": True,
            "claim_id": claim_id,
            "logs": logs,
            "total": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/claims/{claim_id}/logs/latest")
async def get_latest_claim_log(claim_id: str):
    """Get the latest agent processing log for a claim"""
    try:
        cosmos_service = get_cosmos_service()
        log = cosmos_service.get_latest_agent_log(claim_id)
        if log is None:
            raise HTTPException(status_code=404, detail=f"No logs found for claim {claim_id}")
        return {
            "success": True,
            "claim_id": claim_id,
            "log": log
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== REAL-TIME PROCESSING ENDPOINTS ====================

@app.post("/api/process/{claim_id}")
async def start_processing(claim_id: str, background_tasks: BackgroundTasks):
    """Start real-time processing for a claim"""
    try:
        cosmos_service = get_cosmos_service()
        claim = cosmos_service.get_claim(claim_id)
        
        # If claim doesn't exist in Cosmos DB, create a placeholder
        # This supports fire-and-forget from frontend using static JSON
        if claim is None:
            print(f"📝 Creating placeholder claim for: {claim_id}")
            claim = {
                "claim_id": claim_id,
                "patient_name": "Demo Patient",
                "policy_number": "DEMO-POLICY",
                "claim_amount": 100000,
                "claim_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "diagnosis": "Demo Diagnosis",
                "source": "frontend_trigger"
            }
            cosmos_service.save_claim(claim)
        
        # Create processing session
        session = cosmos_service.create_processing_session(claim_id)
        
        print(f"🚀 Processing started for claim: {claim_id}, session: {session['session_id']}")
        
        return {
            "success": True,
            "message": f"Processing started for claim {claim_id}",
            "session_id": session["session_id"],
            "websocket_url": f"/ws/process/{session['session_id']}",
            "sse_url": f"/api/process/{claim_id}/stream"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/process/{claim_id}/stream")
async def stream_processing(claim_id: str):
    """
    Server-Sent Events (SSE) endpoint for real-time processing updates
    Alternative to WebSocket for clients that don't support WebSocket
    """
    try:
        cosmos_service = get_cosmos_service()
        claim = cosmos_service.get_claim(claim_id)
        
        if claim is None:
            raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
        
        processor = get_realtime_processor()
        
        async def event_generator():
            """Generate SSE events"""
            async for update in processor.process_claim_realtime(claim, {}):
                yield f"data: {update.to_json()}\n\n"
            yield "data: {\"status\": \"complete\"}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get the status of a processing session"""
    try:
        processor = get_realtime_processor()
        session = processor.get_session_status(session_id)
        
        if session is None:
            # Try Cosmos DB
            cosmos_service = get_cosmos_service()
            session = cosmos_service.get_processing_session(session_id)
        
        if session is None:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "success": True,
            "session": session
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/active")
async def get_active_sessions():
    """Get all active processing sessions"""
    try:
        cosmos_service = get_cosmos_service()
        sessions = cosmos_service.get_active_sessions()
        return {
            "success": True,
            "sessions": sessions,
            "total": len(sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WEBSOCKET ENDPOINT ====================

@app.websocket("/ws/process/{session_id}")
async def websocket_processing(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time processing updates
    Connect to receive live updates during claim processing
    """
    await manager.connect(websocket, session_id)
    
    try:
        cosmos_service = get_cosmos_service()
        session = cosmos_service.get_processing_session(session_id)
        
        if session is None:
            await websocket.send_json({
                "error": "Session not found",
                "session_id": session_id
            })
            return
        
        claim_id = session["claim_id"]
        claim = cosmos_service.get_claim(claim_id)
        
        if claim is None:
            await websocket.send_json({
                "error": "Claim not found",
                "claim_id": claim_id
            })
            return
        
        # Start processing
        processor = get_realtime_processor()
        
        # Send initial status
        await websocket.send_json({
            "type": "session_started",
            "session_id": session_id,
            "claim_id": claim_id
        })
        
        # Process and stream updates
        async for update in processor.process_claim_realtime(claim, {}):
            await websocket.send_json({
                "type": "agent_update",
                **update.to_dict()
            })
        
        # Send completion
        await websocket.send_json({
            "type": "processing_complete",
            "session_id": session_id
        })
        
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        manager.disconnect(websocket, session_id)


# ==================== BLOB STORAGE CONFIGURATION ====================

@app.get("/api/config/storage")
async def get_storage_config():
    """Get blob storage configuration (public info only)"""
    return {
        "storage_account": os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "fsidemo"),
        "container_name": os.getenv("AZURE_STORAGE_CONTAINER_NAME", "healthinsurance"),
        "base_url": f"https://{os.getenv('AZURE_STORAGE_ACCOUNT_NAME', 'fsidemo')}.blob.core.windows.net/{os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'healthinsurance')}"
    }


# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
