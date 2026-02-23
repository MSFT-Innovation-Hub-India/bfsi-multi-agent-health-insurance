// Utility to load the correct log file based on claim ID
// Supports fetching from Cosmos DB API with fallback to static JSON
import log1 from '@/log.json';
import log2 from '@/log2.json';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface LogData {
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
    processing_time: number;
    azure_evidence: {
      medical: string;
      billing: string;
      xray?: string;
      lab_reports?: string;
      policy: string;
    };
    fraud_orchestration: {
      status: string;
      framework: string;
      orchestration_result: string;
      total_messages: number;
      agents_participated: number;
      conversation_duration: number;
      fraud_decision: {
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
    system_status: {
      azure_ai_available: boolean;
      xray_api_available?: boolean;
      lab_report_api_available?: boolean;
      autogen_framework: string;
      fraud_detection_enabled: boolean;
      comprehensive_validation: boolean;
    };
    timestamp: string;
  };
  fraud_detection_capabilities: {
    identity_verification: boolean;
    medical_consistency_check: boolean;
    billing_validation: boolean;
    documentation_integrity?: boolean;
    imaging_correlation?: boolean;
    multi_agent_analysis?: boolean;
    azure_ai_evidence_collection?: boolean;
    comprehensive_conversation_logging?: boolean;
    genuine_agent_interactions?: boolean;
    policy_limit_validation?: boolean;
  };
}

// Map of claim IDs to their corresponding static log files (fallback)
const claimLogMap: { [key: string]: LogData } = {
  'CLM001-2024-LAKSHMI': log1 as LogData,
  'CLM001-2024-LAKSHMI-APPROVED': log1 as LogData,
  'CLM010-2025-AHSAN': log2 as LogData,
};

/**
 * Get the log data for a specific claim ID (synchronous, static fallback)
 * @param claimId - The claim ID to get data for
 * @returns The log data for the claim, or the first log file as default
 */
export function getLogDataForClaim(claimId: string): LogData {
  return claimLogMap[claimId] || log1 as LogData;
}

/**
 * Fetch log data from Cosmos DB API, falling back to static JSON on failure.
 * Fetches the specific seeded log document ({claimId}_seed) so we always
 * get the original rich analysis data, not placeholder logs.
 * @param claimId - The claim ID to get data for
 * @returns Promise resolving to the log data
 */
export async function fetchLogDataForClaim(claimId: string, signal?: AbortSignal): Promise<LogData> {
  // Map approved variant to the original claim's seed document
  const baseClaimId = claimId.replace(/-APPROVED$/, '');
  const logId = `${baseClaimId}_seed`;
  try {
    // Use the caller-provided signal (e.g. from AbortController in useEffect cleanup)
    // or fall back to a 5-second timeout signal.
    const fetchSignal = signal ?? AbortSignal.timeout(5000);
    const response = await fetch(
      `${API_BASE_URL}/api/claims/${encodeURIComponent(baseClaimId)}/logs/by-id/${encodeURIComponent(logId)}`,
      { signal: fetchSignal }
    );
    if (response.ok) {
      const result = await response.json();
      if (result.success && result.log) {
        console.log(`✅ Loaded log for ${claimId} from Cosmos DB`);
        return result.log as LogData;
      }
    }
  } catch (error) {
    // If the request was intentionally aborted (e.g. React StrictMode cleanup), stay silent
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error; // re-throw so the caller's .catch ignores it
    }
    console.log(`ℹ️ API unavailable for ${claimId}, using static JSON fallback`);
  }
  // Fallback to static JSON
  return getLogDataForClaim(claimId);
}

/**
 * Get all available claim IDs
 * @returns Array of claim IDs that have log data
 */
export function getAvailableClaimIds(): string[] {
  return Object.keys(claimLogMap);
}

/**
 * Check if a claim ID has log data available
 * @param claimId - The claim ID to check
 * @returns True if log data exists for this claim
 */
export function hasLogData(claimId: string): boolean {
  return claimId in claimLogMap;
}
