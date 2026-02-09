/**
 * Claims API Client
 * Frontend API client for communicating with the backend claims processing API
 * 
 * NOTE: This is the API client - NOT YET CONNECTED to the frontend components
 * To use this, import and call these functions from your components
 */

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ==================== TYPES ====================

export interface ClaimInput {
  claim_id: string;
  patient_name: string;
  policy_number: string;
  claim_amount: number;
  claim_date: string;
  diagnosis: string;
  treatment_type?: string;
  hospital_name?: string;
  documents_available?: string[];
  policy_coverage_limit?: number;
  previously_claimed_amount?: number;
  available_balance?: number;
  policy_year?: string;
  age?: number;
}

export interface ClaimResponse {
  success: boolean;
  message: string;
  data?: any;
}

export interface AgentUpdate {
  agent_name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
  content?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface ProcessingSession {
  session_id: string;
  claim_id: string;
  status: string;
  current_agent?: string;
  agents_completed: string[];
  started_at: string;
  completed_at?: string;
}

export interface AgentLog {
  report_type: string;
  generated_at: string;
  patient_details: {
    claim_id: string;
    patient_name: string;
    policy_number: string;
    claim_amount: number;
    claim_date: string;
    diagnosis: string;
    treatment_type: string;
    hospital_name: string;
    documents_available: string[];
    policy_coverage_limit: number;
    previously_claimed_amount: number;
    available_balance: number;
    policy_year: string;
  };
  fraud_analysis_results: {
    claim_id: string;
    patient_name: string;
    processing_type: string;
    processing_time?: number;
    azure_evidence: Record<string, string>;
    fraud_orchestration: {
      status: string;
      framework: string;
      orchestration_result?: string;
      total_messages: number;
      agents_participated: number;
      conversation_duration: number;
      fraud_decision?: {
        decision: string;
        approved_amount: string;
        fraud_risk_level: string;
        balance_status: string;
        remaining_balance: string;
        policy_utilization: string;
        fraud_indicators: string[];
        rationale: string;
        conversation_length: number;
        decision_source: string;
      };
      detailed_messages: string[];
    };
    system_status?: {
      azure_ai_available: boolean;
      xray_api_available?: boolean;
      lab_report_api_available?: boolean;
      autogen_framework: string;
      fraud_detection_enabled: boolean;
      comprehensive_validation: boolean;
    };
    timestamp: string;
  };
  fraud_detection_capabilities?: Record<string, boolean>;
}

// ==================== API CLIENT CLASS ====================

class ClaimsApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Make an API request
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return response.json();
  }

  // ==================== HEALTH CHECK ====================

  /**
   * Check API health
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/health');
  }

  /**
   * Get API status
   */
  async getStatus(): Promise<{
    api_version: string;
    cosmos_db: string;
    realtime_processing: string;
    timestamp: string;
  }> {
    return this.request('/api/status');
  }

  // ==================== CLAIMS ====================

  /**
   * Create or update a claim
   */
  async createClaim(claim: ClaimInput): Promise<ClaimResponse> {
    return this.request('/api/claims', {
      method: 'POST',
      body: JSON.stringify(claim),
    });
  }

  /**
   * Get all claims
   */
  async getClaims(limit: number = 100): Promise<ClaimResponse> {
    return this.request(`/api/claims?limit=${limit}`);
  }

  /**
   * Get a specific claim by ID
   */
  async getClaim(claimId: string): Promise<ClaimResponse> {
    return this.request(`/api/claims/${encodeURIComponent(claimId)}`);
  }

  /**
   * Delete a claim
   */
  async deleteClaim(claimId: string): Promise<ClaimResponse> {
    return this.request(`/api/claims/${encodeURIComponent(claimId)}`, {
      method: 'DELETE',
    });
  }

  // ==================== AGENT LOGS ====================

  /**
   * Get all agent logs for a claim
   */
  async getClaimLogs(claimId: string): Promise<{
    success: boolean;
    claim_id: string;
    logs: AgentLog[];
    total: number;
  }> {
    return this.request(`/api/claims/${encodeURIComponent(claimId)}/logs`);
  }

  /**
   * Get the latest agent log for a claim
   */
  async getLatestClaimLog(claimId: string): Promise<{
    success: boolean;
    claim_id: string;
    log: AgentLog;
  }> {
    return this.request(`/api/claims/${encodeURIComponent(claimId)}/logs/latest`);
  }

  // ==================== REAL-TIME PROCESSING ====================

  /**
   * Start processing a claim
   */
  async startProcessing(claimId: string): Promise<{
    success: boolean;
    message: string;
    session_id: string;
    websocket_url: string;
    sse_url: string;
  }> {
    return this.request(`/api/process/${encodeURIComponent(claimId)}`, {
      method: 'POST',
    });
  }

  /**
   * Get session status
   */
  async getSession(sessionId: string): Promise<{
    success: boolean;
    session: ProcessingSession;
  }> {
    return this.request(`/api/sessions/${encodeURIComponent(sessionId)}`);
  }

  /**
   * Get all active sessions
   */
  async getActiveSessions(): Promise<{
    success: boolean;
    sessions: ProcessingSession[];
    total: number;
  }> {
    return this.request('/api/sessions/active');
  }

  /**
   * Get storage configuration
   */
  async getStorageConfig(): Promise<{
    storage_account: string;
    container_name: string;
    base_url: string;
  }> {
    return this.request('/api/config/storage');
  }

  // ==================== REAL-TIME STREAMING ====================

  /**
   * Subscribe to real-time processing updates via Server-Sent Events (SSE)
   */
  subscribeToProcessing(
    claimId: string,
    callbacks: {
      onUpdate: (update: AgentUpdate) => void;
      onComplete: () => void;
      onError: (error: Error) => void;
    }
  ): () => void {
    const eventSource = new EventSource(
      `${this.baseUrl}/api/process/${encodeURIComponent(claimId)}/stream`
    );

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.status === 'complete') {
          callbacks.onComplete();
          eventSource.close();
        } else {
          callbacks.onUpdate(data as AgentUpdate);
        }
      } catch (error) {
        callbacks.onError(error as Error);
      }
    };

    eventSource.onerror = () => {
      callbacks.onError(new Error('SSE connection error'));
      eventSource.close();
    };

    // Return cleanup function
    return () => eventSource.close();
  }

  /**
   * Connect to WebSocket for real-time processing updates
   */
  connectWebSocket(
    sessionId: string,
    callbacks: {
      onOpen: () => void;
      onUpdate: (update: AgentUpdate) => void;
      onComplete: () => void;
      onError: (error: Error) => void;
      onClose: () => void;
    }
  ): WebSocket {
    const wsUrl = this.baseUrl.replace('http', 'ws');
    const ws = new WebSocket(`${wsUrl}/ws/process/${sessionId}`);

    ws.onopen = () => {
      callbacks.onOpen();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'processing_complete') {
          callbacks.onComplete();
        } else if (data.type === 'agent_update') {
          callbacks.onUpdate(data as AgentUpdate);
        } else if (data.type === 'error') {
          callbacks.onError(new Error(data.message));
        }
      } catch (error) {
        callbacks.onError(error as Error);
      }
    };

    ws.onerror = () => {
      callbacks.onError(new Error('WebSocket error'));
    };

    ws.onclose = () => {
      callbacks.onClose();
    };

    return ws;
  }
}

// ==================== SINGLETON INSTANCE ====================

export const claimsApi = new ClaimsApiClient();

// ==================== CONVENIENCE FUNCTIONS ====================

/**
 * Check if the API is available
 */
export async function isApiAvailable(): Promise<boolean> {
  try {
    await claimsApi.healthCheck();
    return true;
  } catch {
    return false;
  }
}

/**
 * Fetch claim data with fallback to local JSON
 * This can be used during migration to API
 */
export async function getClaimDataWithFallback(
  claimId: string,
  localFallback: () => AgentLog
): Promise<AgentLog> {
  try {
    const response = await claimsApi.getLatestClaimLog(claimId);
    return response.log;
  } catch {
    console.warn(`API unavailable, using local fallback for claim ${claimId}`);
    return localFallback();
  }
}

export default claimsApi;
