/**
 * Real-time Processing Hooks
 * React hooks for real-time claim processing updates
 * 
 * NOTE: These hooks are NOT YET CONNECTED to the frontend components
 * To use, import into your React components
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { claimsApi, AgentUpdate, ProcessingSession } from './claimsApi';

// ==================== TYPES ====================

export interface UseRealtimeProcessingOptions {
  autoStart?: boolean;
  useWebSocket?: boolean;  // Use WebSocket instead of SSE
}

export interface UseRealtimeProcessingResult {
  // State
  isProcessing: boolean;
  isConnected: boolean;
  currentAgent: string | null;
  agentsCompleted: string[];
  updates: AgentUpdate[];
  error: Error | null;
  
  // Actions
  startProcessing: () => Promise<void>;
  stopProcessing: () => void;
  clearUpdates: () => void;
}

// ==================== HOOKS ====================

/**
 * Hook for real-time claim processing with SSE or WebSocket
 */
export function useRealtimeProcessing(
  claimId: string,
  options: UseRealtimeProcessingOptions = {}
): UseRealtimeProcessingResult {
  const { autoStart = false, useWebSocket = false } = options;
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [agentsCompleted, setAgentsCompleted] = useState<string[]>([]);
  const [updates, setUpdates] = useState<AgentUpdate[]>([]);
  const [error, setError] = useState<Error | null>(null);
  
  const cleanupRef = useRef<(() => void) | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  
  const handleUpdate = useCallback((update: AgentUpdate) => {
    setUpdates(prev => [...prev, update]);
    
    if (update.status === 'processing') {
      setCurrentAgent(update.agent_name);
    } else if (update.status === 'completed' && update.agent_name !== 'System') {
      setAgentsCompleted(prev => [...prev, update.agent_name]);
      setCurrentAgent(null);
    }
  }, []);
  
  const handleComplete = useCallback(() => {
    setIsProcessing(false);
    setIsConnected(false);
    setCurrentAgent(null);
  }, []);
  
  const handleError = useCallback((err: Error) => {
    setError(err);
    setIsProcessing(false);
    setIsConnected(false);
  }, []);
  
  const startProcessing = useCallback(async () => {
    try {
      setError(null);
      setUpdates([]);
      setAgentsCompleted([]);
      setIsProcessing(true);
      
      if (useWebSocket) {
        // WebSocket approach
        const { session_id } = await claimsApi.startProcessing(claimId);
        
        wsRef.current = claimsApi.connectWebSocket(session_id, {
          onOpen: () => setIsConnected(true),
          onUpdate: handleUpdate,
          onComplete: handleComplete,
          onError: handleError,
          onClose: () => setIsConnected(false),
        });
      } else {
        // SSE approach
        setIsConnected(true);
        cleanupRef.current = claimsApi.subscribeToProcessing(claimId, {
          onUpdate: handleUpdate,
          onComplete: handleComplete,
          onError: handleError,
        });
      }
    } catch (err) {
      handleError(err as Error);
    }
  }, [claimId, useWebSocket, handleUpdate, handleComplete, handleError]);
  
  const stopProcessing = useCallback(() => {
    if (cleanupRef.current) {
      cleanupRef.current();
      cleanupRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsProcessing(false);
    setIsConnected(false);
  }, []);
  
  const clearUpdates = useCallback(() => {
    setUpdates([]);
    setAgentsCompleted([]);
    setCurrentAgent(null);
    setError(null);
  }, []);
  
  // Auto-start if enabled
  useEffect(() => {
    if (autoStart && claimId) {
      startProcessing();
    }
    
    return () => {
      stopProcessing();
    };
  }, [autoStart, claimId]);
  
  return {
    isProcessing,
    isConnected,
    currentAgent,
    agentsCompleted,
    updates,
    error,
    startProcessing,
    stopProcessing,
    clearUpdates,
  };
}

/**
 * Hook for fetching and tracking session status
 */
export function useProcessingSession(sessionId: string | null) {
  const [session, setSession] = useState<ProcessingSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const fetchSession = useCallback(async () => {
    if (!sessionId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await claimsApi.getSession(sessionId);
      setSession(response.session);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);
  
  useEffect(() => {
    fetchSession();
  }, [fetchSession]);
  
  return {
    session,
    isLoading,
    error,
    refetch: fetchSession,
  };
}

/**
 * Hook for tracking active processing sessions
 */
export function useActiveSessions(pollInterval: number = 5000) {
  const [sessions, setSessions] = useState<ProcessingSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const fetchSessions = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await claimsApi.getActiveSessions();
      setSessions(response.sessions);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  useEffect(() => {
    fetchSessions();
    
    if (pollInterval > 0) {
      const interval = setInterval(fetchSessions, pollInterval);
      return () => clearInterval(interval);
    }
  }, [fetchSessions, pollInterval]);
  
  return {
    sessions,
    isLoading,
    error,
    refetch: fetchSessions,
  };
}

/**
 * Hook for fetching claim logs from Cosmos DB
 */
export function useClaimLogs(claimId: string) {
  const [logs, setLogs] = useState<any[]>([]);
  const [latestLog, setLatestLog] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const fetchLogs = useCallback(async () => {
    if (!claimId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const [logsResponse, latestResponse] = await Promise.all([
        claimsApi.getClaimLogs(claimId),
        claimsApi.getLatestClaimLog(claimId).catch(() => null),
      ]);
      
      setLogs(logsResponse.logs);
      if (latestResponse) {
        setLatestLog(latestResponse.log);
      }
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [claimId]);
  
  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);
  
  return {
    logs,
    latestLog,
    isLoading,
    error,
    refetch: fetchLogs,
  };
}

export default {
  useRealtimeProcessing,
  useProcessingSession,
  useActiveSessions,
  useClaimLogs,
};
