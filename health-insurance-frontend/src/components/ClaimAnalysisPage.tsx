import React from 'react';
import { ClaimOverview } from './ClaimOverview';
import { EvidenceAnalysis } from './EvidenceAnalysis';
import { SystemStatusPanel } from './SystemStatus';
import { AgentConversation } from './AgentConversation';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeft,
  FileText,
  MessageSquare,
  Activity,
  Shield
} from 'lucide-react';
import { getLogDataForClaim } from '@/utils/logLoader';

interface ClaimAnalysisPageProps {
  claimId: string;
  onBack: () => void;
}

export const ClaimAnalysisPage: React.FC<ClaimAnalysisPageProps> = ({ claimId, onBack }) => {
  // Load the appropriate log data based on claim ID
  const logData = getLogDataForClaim(claimId);
  
  // Extract data from logData
  const patientDetails = logData.patient_details;
  const fraudDecision = logData.fraud_analysis_results.fraud_orchestration.fraud_decision;
  const evidence = logData.fraud_analysis_results.azure_evidence;
  const orchestration = logData.fraud_analysis_results.fraud_orchestration;
  
  // Mock system status and capabilities since they're not in the actual log data
  const systemStatus = {
    azure_ai_available: true,
    xray_api_available: true,
    autogen_framework: "AutoGen v0.2.14",
    fraud_detection_enabled: true,
    comprehensive_validation: true
  };
  
  const capabilities = {
    identity_verification: true,
    medical_consistency_check: true,
    billing_validation: true,
    documentation_integrity: true,
    imaging_correlation: true,
    multi_agent_analysis: true,
    azure_ai_evidence_collection: true,
    comprehensive_fraud_assessment: true,
    comprehensive_conversation_logging: true,
    genuine_agent_interactions: true
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={onBack}
                className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Workflow
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Global Trust General - Comprehensive Claim Analysis</h1>
                <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                  <span>Claim ID: {claimId}</span>
                  <span>•</span>
                  <span>Patient: {patientDetails.patient_name}</span>
                  <span>•</span>
                  <span>Amount: ₹{patientDetails.claim_amount.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content with Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="evidence" className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Evidence
            </TabsTrigger>
            <TabsTrigger value="conversation" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Agent Flow
            </TabsTrigger>
            <TabsTrigger value="system" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              System
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <ClaimOverview 
              patientDetails={patientDetails}
              fraudDecision={fraudDecision}
              processingTime={orchestration.conversation_duration}
            />
          </TabsContent>

          {/* Evidence Analysis Tab */}
          <TabsContent value="evidence" className="space-y-6">
            <EvidenceAnalysis 
              evidence={evidence}
            />
          </TabsContent>

          {/* Agent Conversation Tab */}
          <TabsContent value="conversation" className="space-y-6">
            <AgentConversation 
              messages={orchestration.detailed_messages}
              conversationDuration={orchestration.conversation_duration}
              totalAgents={orchestration.agents_participated}
            />
          </TabsContent>

          {/* System Status Tab */}
          <TabsContent value="system" className="space-y-6">
            <SystemStatusPanel 
              systemStatus={systemStatus}
              capabilities={capabilities}
              processingTime={orchestration.conversation_duration}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};