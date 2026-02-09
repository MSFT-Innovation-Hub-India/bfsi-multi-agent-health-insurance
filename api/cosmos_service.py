"""
Cosmos DB Service for Health Insurance Claims Processing
Handles storing and retrieving claim logs and agent processing results
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential, ChainedTokenCredential, AzureCliCredential, ManagedIdentityCredential
from dotenv import load_dotenv

load_dotenv()


class CosmosDBService:
    """Service for interacting with Azure Cosmos DB"""
    
    def __init__(self):
        """Initialize Cosmos DB connection"""
        self.endpoint = os.getenv("COSMOS_ENDPOINT", "")
        self.key = os.getenv("COSMOS_KEY", "")  # Optional - only used if AAD is disabled
        self.database_name = os.getenv("COSMOS_DATABASE", "HealthInsuranceClaims")
        self.claims_container_name = os.getenv("COSMOS_CLAIMS_CONTAINER", "claims")
        self.logs_container_name = os.getenv("COSMOS_LOGS_CONTAINER", "agent_logs")
        self.sessions_container_name = os.getenv("COSMOS_SESSIONS_CONTAINER", "processing_sessions")
        
        # AAD authentication flag
        self.use_aad_auth = os.getenv("COSMOS_USE_AAD", "true").lower() == "true"
        
        self.client = None
        self.database = None
        self.claims_container = None
        self.logs_container = None
        self.sessions_container = None
        
        if self.endpoint:
            self._initialize_client()
    
    def _get_credential(self):
        """Get Azure credential for AAD authentication"""
        # Use a chained credential that tries multiple authentication methods
        # 1. Managed Identity (for Azure App Service)
        # 2. Azure CLI (for local development)
        # 3. Default credential chain
        try:
            credential = ChainedTokenCredential(
                ManagedIdentityCredential(),
                AzureCliCredential(),
                DefaultAzureCredential()
            )
            return credential
        except Exception as e:
            print(f"⚠️ Failed to create credential chain: {e}")
            return DefaultAzureCredential()
    
    def _initialize_client(self):
        """Initialize the Cosmos DB client and containers"""
        try:
            if self.use_aad_auth:
                # Use AAD authentication
                print("🔐 Using AAD authentication for Cosmos DB...")
                credential = self._get_credential()
                self.client = CosmosClient(self.endpoint, credential=credential)
            elif self.key:
                # Use key-based authentication
                print("🔑 Using key-based authentication for Cosmos DB...")
                self.client = CosmosClient(self.endpoint, self.key)
            else:
                raise ValueError("No authentication method available. Set COSMOS_KEY or enable AAD auth.")
            
            self.database = self._get_or_create_database()
            self.claims_container = self._get_or_create_container(
                self.claims_container_name, "/claim_id"
            )
            self.logs_container = self._get_or_create_container(
                self.logs_container_name, "/claim_id"
            )
            self.sessions_container = self._get_or_create_container(
                self.sessions_container_name, "/session_id"
            )
            print("✅ Cosmos DB connection established")
        except Exception as e:
            print(f"❌ Cosmos DB connection failed: {e}")
            raise
    
    def _get_or_create_database(self):
        """Get the database (assumes it exists, falls back to creating)"""
        try:
            # Try to get existing database first (no write permission needed)
            return self.client.get_database_client(self.database_name)
        except Exception:
            # Fall back to creating if it doesn't exist
            try:
                return self.client.create_database_if_not_exists(id=self.database_name)
            except exceptions.CosmosResourceExistsError:
                return self.client.get_database_client(self.database_name)
    
    def _get_or_create_container(self, container_name: str, partition_key: str):
        """Get the container (assumes it exists, falls back to creating)"""
        try:
            # Try to get existing container first (no write permission needed)
            return self.database.get_container_client(container_name)
        except Exception:
            # Fall back to creating if it doesn't exist
            try:
                return self.database.create_container_if_not_exists(
                    id=container_name,
                    partition_key=PartitionKey(path=partition_key),
                    offer_throughput=400
                )
            except exceptions.CosmosResourceExistsError:
                return self.database.get_container_client(container_name)
    
    # ==================== CLAIM OPERATIONS ====================
    
    def save_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a claim to Cosmos DB
        
        Args:
            claim_data: The claim data to save
            
        Returns:
            The saved claim with Cosmos DB metadata
        """
        claim_data["id"] = claim_data.get("claim_id", str(datetime.utcnow().timestamp()))
        claim_data["created_at"] = claim_data.get("created_at", datetime.utcnow().isoformat())
        claim_data["updated_at"] = datetime.utcnow().isoformat()
        
        return self.claims_container.upsert_item(claim_data)
    
    def get_claim(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a claim by ID
        
        Args:
            claim_id: The claim ID
            
        Returns:
            The claim data or None if not found
        """
        try:
            return self.claims_container.read_item(item=claim_id, partition_key=claim_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
    
    def get_all_claims(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all claims
        
        Args:
            limit: Maximum number of claims to return
            
        Returns:
            List of claims
        """
        query = f"SELECT * FROM c ORDER BY c.created_at DESC OFFSET 0 LIMIT {limit}"
        return list(self.claims_container.query_items(query, enable_cross_partition_query=True))
    
    def delete_claim(self, claim_id: str) -> bool:
        """
        Delete a claim
        
        Args:
            claim_id: The claim ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            self.claims_container.delete_item(item=claim_id, partition_key=claim_id)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
    
    # ==================== AGENT LOG OPERATIONS ====================
    
    def save_agent_log(self, claim_id: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save agent processing log
        
        Args:
            claim_id: The claim ID this log belongs to
            log_data: The log data including agent messages and results
            
        Returns:
            The saved log with Cosmos DB metadata
        """
        log_id = f"{claim_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        log_data["id"] = log_id
        log_data["claim_id"] = claim_id
        log_data["created_at"] = datetime.utcnow().isoformat()
        
        return self.logs_container.upsert_item(log_data)
    
    def get_agent_logs(self, claim_id: str) -> List[Dict[str, Any]]:
        """
        Get all agent logs for a claim
        
        Args:
            claim_id: The claim ID
            
        Returns:
            List of agent logs
        """
        query = f"SELECT * FROM c WHERE c.claim_id = '{claim_id}' ORDER BY c.created_at DESC"
        return list(self.logs_container.query_items(query, enable_cross_partition_query=True))
    
    def get_latest_agent_log(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest agent log for a claim
        
        Args:
            claim_id: The claim ID
            
        Returns:
            The latest agent log or None
        """
        logs = self.get_agent_logs(claim_id)
        return logs[0] if logs else None
    
    # ==================== PROCESSING SESSION OPERATIONS ====================
    
    def create_processing_session(self, claim_id: str) -> Dict[str, Any]:
        """
        Create a new processing session for real-time updates
        
        Args:
            claim_id: The claim ID being processed
            
        Returns:
            The session data
        """
        session_id = f"session_{claim_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        session_data = {
            "id": session_id,
            "session_id": session_id,
            "claim_id": claim_id,
            "status": "started",
            "current_agent": None,
            "agents_completed": [],
            "messages": [],
            "started_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "completed_at": None
        }
        
        return self.sessions_container.upsert_item(session_data)
    
    def update_processing_session(
        self, 
        session_id: str, 
        current_agent: Optional[str] = None,
        message: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a processing session with real-time agent updates
        
        Args:
            session_id: The session ID
            current_agent: The currently active agent
            message: A new message to append
            status: New status
            
        Returns:
            The updated session data
        """
        try:
            session = self.sessions_container.read_item(item=session_id, partition_key=session_id)
            
            if current_agent:
                if session["current_agent"] and session["current_agent"] not in session["agents_completed"]:
                    session["agents_completed"].append(session["current_agent"])
                session["current_agent"] = current_agent
            
            if message:
                session["messages"].append({
                    **message,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            if status:
                session["status"] = status
                if status == "completed":
                    session["completed_at"] = datetime.utcnow().isoformat()
            
            session["updated_at"] = datetime.utcnow().isoformat()
            
            return self.sessions_container.upsert_item(session)
        except exceptions.CosmosResourceNotFoundError:
            return None
    
    def get_processing_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a processing session
        
        Args:
            session_id: The session ID
            
        Returns:
            The session data or None
        """
        try:
            return self.sessions_container.read_item(item=session_id, partition_key=session_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all active processing sessions
        
        Returns:
            List of active sessions
        """
        query = "SELECT * FROM c WHERE c.status IN ('started', 'processing') ORDER BY c.started_at DESC"
        return list(self.sessions_container.query_items(query, enable_cross_partition_query=True))


# Singleton instance
_cosmos_service: Optional[CosmosDBService] = None


def get_cosmos_service() -> CosmosDBService:
    """Get or create the Cosmos DB service singleton"""
    global _cosmos_service
    if _cosmos_service is None:
        _cosmos_service = CosmosDBService()
    return _cosmos_service
