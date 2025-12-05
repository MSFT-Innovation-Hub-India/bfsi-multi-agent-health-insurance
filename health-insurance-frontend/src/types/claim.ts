export interface ClaimData {
  report_type: string;
  generated_at: string;
  patient_details: PatientDetails;
  fraud_analysis_results: FraudAnalysisResults;
  fraud_detection_capabilities: FraudDetectionCapabilities;
}

export interface PatientDetails {
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
}

export interface FraudAnalysisResults {
  claim_id: string;
  patient_name: string;
  processing_type: string;
  processing_time: number;
  azure_evidence: AzureEvidence;
  fraud_orchestration: FraudOrchestration;
  system_status: SystemStatus;
  timestamp: string;
}

export interface AzureEvidence {
  medical: string;
  billing: string;
  xray?: string;
  lab_reports?: string;
  policy: string;
}

export interface FraudOrchestration {
  status: string;
  framework: string;
  orchestration_result: string;
  total_messages: number;
  agents_participated: number;
  agent_call_counts: Record<string, unknown>;
  conversation_duration: number;
  fraud_decision: FraudDecision;
  conversation_complete: boolean;
  fraud_analysis: boolean;
  detailed_messages: string[];
}

export interface FraudDecision {
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
}

export interface SystemStatus {
  azure_ai_available: boolean;
  xray_api_available?: boolean;
  lab_report_api_available?: boolean;
  autogen_framework: string;
  fraud_detection_enabled: boolean;
  comprehensive_validation: boolean;
}

export interface FraudDetectionCapabilities {
  identity_verification: boolean;
  medical_consistency_check: boolean;
  billing_validation: boolean;
  documentation_integrity: boolean;
  imaging_correlation: boolean;
  multi_agent_analysis: boolean;
  azure_ai_evidence_collection: boolean;
  comprehensive_conversation_logging: boolean;
  genuine_agent_interactions: boolean;
}

export interface AgentMessage {
  content: string;
  role: string;
  name: string;
  timestamp?: string;
}

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type DecisionStatus = 'APPROVED' | 'REJECTED' | 'PENDING' | 'UNDER_REVIEW';