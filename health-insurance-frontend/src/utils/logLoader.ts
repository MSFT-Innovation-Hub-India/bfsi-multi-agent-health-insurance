// Utility to load the correct log file based on claim ID
import log1 from '@/log.json';
import log2 from '@/log2.json';

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

// Map of claim IDs to their corresponding log files
const claimLogMap: { [key: string]: LogData } = {
  'CLM001-2024-LAKSHMI': log1 as LogData,
  'CLM010-2025-AHSAN': log2 as LogData,
};

/**
 * Get the log data for a specific claim ID
 * @param claimId - The claim ID to get data for
 * @returns The log data for the claim, or the first log file as default
 */
export function getLogDataForClaim(claimId: string): LogData {
  return claimLogMap[claimId] || log1 as LogData;
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
