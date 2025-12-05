import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  ArrowLeft,
  Bot,
  CheckCircle,
  FileText,
  Shield,
  CreditCard,
  Activity,
  Eye,
  Workflow
} from 'lucide-react';
import { RupeeIcon } from '@/components/ui/rupee-icon';
import { AgentMessage, parseAgentMessages, formatAgentName, extractSummary } from '@/utils/agentParser';
import { AgentModal } from './AgentModal';
import logData from '@/log.json';

interface AgentWorkflowProps {
  claimId: string;
  onBack: () => void;
  onReviewApprove?: () => void;
}

// Parse agent messages from the log data
const agentMessages: AgentMessage[] = parseAgentMessages(
  logData?.fraud_analysis_results?.fraud_orchestration?.detailed_messages || []
);

const agentIcons: { [key: string]: React.ReactNode } = {
  'Fraud_Detection_Specialist': <Shield className="h-5 w-5 text-blue-600" />,
  'Medical_Validator': <FileText className="h-5 w-5 text-blue-700" />,
  'Billing_Fraud_Validator': <CreditCard className="h-5 w-5 text-blue-800" />,
  'Policy_Balance_Validator': <RupeeIcon className="h-5 w-5 text-blue-600" />,
  'Policy_Adjustment_Coordinator': <Activity className="h-5 w-5 text-blue-700" />,
  'Decision_Coordinator': <CheckCircle className="h-5 w-5 text-blue-800" />
};

const agentColors: { [key: string]: string } = {
  'Fraud_Detection_Specialist': 'border-blue-200 bg-blue-50',
  'Medical_Validator': 'border-blue-300 bg-blue-100',
  'Billing_Fraud_Validator': 'border-blue-400 bg-blue-200',
  'Policy_Balance_Validator': 'border-blue-300 bg-blue-100',
  'Policy_Adjustment_Coordinator': 'border-blue-200 bg-blue-50',
  'Decision_Coordinator': 'border-blue-400 bg-blue-200'
};

const getAgentDescription = (agentName: string): string => {
  const descriptions: { [key: string]: string } = {
    'Fraud_Detection_Specialist': 'Performs initial fraud risk assessment and identity verification across all claim documents.',
    'Medical_Validator': 'Reviews medical evidence consistency, validates diagnosis appropriateness, and checks treatment protocols.',
    'Billing_Fraud_Validator': 'Analyzes billing accuracy, checks for duplicate charges, and validates hospital invoice authenticity.',
    'Policy_Balance_Validator': 'Verifies policy coverage limits, calculates available balance, and ensures claim compliance.',
    'Policy_Adjustment_Coordinator': 'Applies policy exclusions, calculates final approved amounts, and manages adjustments.',
    'Decision_Coordinator': 'Consolidates all agent findings and provides final claim approval or rejection decision.'
  };
  return descriptions[agentName] || 'AI agent responsible for specialized claim analysis tasks.';
};

export const AgentWorkflow: React.FC<AgentWorkflowProps> = ({ claimId, onBack, onReviewApprove }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isProcessing, setIsProcessing] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<AgentMessage | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    if (currentStep < agentMessages.length) {
      const timer = setTimeout(() => {
        setCurrentStep(prev => prev + 1);
      }, 6000); // 6 second delay between each message

      return () => clearTimeout(timer);
    } else {
      setIsProcessing(false);
    }
  }, [currentStep]);



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
                Back to Dashboard
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                  <Workflow className="h-6 w-6 text-blue-600" />
                  Agent Analysis Workflow
                </h1>
                <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                  <span>Claim ID: {claimId}</span>
                  <span>•</span>
                  <span>Patient: {logData?.patient_details?.patient_name || 'Lakshmisrinivas T'}</span>
                  <span>•</span>
                  <span>Amount: ₹{logData?.patient_details?.claim_amount?.toLocaleString() || '396,591'}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant={isProcessing ? "warning" : "success"} className="px-3 py-1">
                {isProcessing ? "Processing..." : "Completed"}
              </Badge>
              <div className="text-sm text-gray-500">
                Step {currentStep} of {agentMessages.length}
              </div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <Progress 
              value={(currentStep / agentMessages.length) * 100} 
              className="h-2"
            />
          </div>
        </div>

        {/* Workflow Hierarchy/Flowchart View */}
        <div className="relative">
          {/* Workflow Path Line */}
          <div className="absolute left-1/2 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-300 via-blue-400 to-blue-500 transform -translate-x-1/2 z-0"></div>
          
          <div className="space-y-8 relative z-10">
            {agentMessages.slice(0, currentStep).map((message, index) => {
              const summary = extractSummary(message.content);
              const isLastCompleted = index === currentStep - 1;
              
              return (
                <div key={index} className="relative">
                  {/* Flow Connector */}
                  <div className="absolute left-1/2 -top-4 w-4 h-4 bg-white border-4 border-blue-500 rounded-full transform -translate-x-1/2 z-20"></div>
                  
                  {/* Agent Card - Simplified Version */}
                  <Card 
                    className={`${agentColors[message.name]} mx-auto max-w-2xl cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:scale-105 ${isLastCompleted ? 'ring-2 ring-blue-500 ring-opacity-60' : ''}`}
                    onClick={() => {
                      setSelectedAgent(message);
                      setIsModalOpen(true);
                    }}
                  >
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="flex items-center justify-center w-14 h-14 bg-white rounded-full shadow-lg border-2 border-gray-200">
                            {agentIcons[message.name]}
                          </div>
                          <div>
                            <h3 className="text-xl font-bold text-gray-900">{formatAgentName(message.name)}</h3>
                            <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                              <Badge variant="outline" className="text-xs">Step {index + 1}</Badge>
                              <CheckCircle className="h-4 w-4 text-blue-600" />
                              <span>Complete</span>
                            </div>
                          </div>
                        </div>
                        <button className="px-4 py-2 bg-white bg-opacity-80 rounded-lg text-sm font-medium hover:bg-opacity-100 transition-colors flex items-center gap-2 shadow-sm">
                          <Eye className="h-4 w-4" />
                          View Details
                        </button>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Agent Role & Responsibility */}
                        <div className="bg-white bg-opacity-60 rounded-lg p-4 border border-white border-opacity-40">
                          <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                            <Bot className="h-4 w-4" />
                            Agent Role
                          </h4>
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {getAgentDescription(message.name)}
                          </p>
                        </div>
                        
                        {/* Summary & Recommendation */}
                        <div className="bg-white bg-opacity-60 rounded-lg p-4 border border-white border-opacity-40">
                          <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                            <FileText className="h-4 w-4" />
                            Key Finding
                          </h4>
                          <p className="text-sm text-gray-700 mb-2">
                            <strong>Summary:</strong> {summary.summary.slice(0, 80)}...
                          </p>
                          <p className="text-sm text-gray-700">
                            <strong>Recommendation:</strong> {summary.recommendation.slice(0, 60)}...
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              );
            })}

            {/* Current Processing Step */}
            {isProcessing && currentStep < agentMessages.length && (
              <div className="relative">
                <div className="absolute left-1/2 -top-4 w-4 h-4 bg-blue-500 rounded-full transform -translate-x-1/2 z-20 animate-pulse"></div>
                
                <Card className="border-2 border-dashed border-blue-300 bg-blue-50/70 mx-auto max-w-2xl">
                  <CardContent className="flex items-center justify-center py-12">
                    <div className="text-center">
                      <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4 shadow-lg">
                        <div className="animate-spin">
                          <Bot className="h-8 w-8 text-blue-600" />
                        </div>
                      </div>
                      <h3 className="text-lg font-semibold text-blue-900 mb-2">
                        {formatAgentName(agentMessages[currentStep]?.name || 'Processing')}
                      </h3>
                      <p className="text-blue-700">Analyzing claim data...</p>
                      <div className="mt-3">
                        <Badge className="bg-blue-100 text-blue-800">In Progress</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Final Decision Node */}
            {!isProcessing && (
              <div className="relative">
                <div className="absolute left-1/2 -top-4 w-4 h-4 bg-blue-600 rounded-full transform -translate-x-1/2 z-20"></div>
                
                <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200 mx-auto max-w-2xl shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-center gap-3 text-blue-800">
                      <CheckCircle className="h-8 w-8" />
                      <span className="text-2xl">Final Decision</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                        <p className="text-sm text-gray-600 mb-1">Approved Amount</p>
                        <p className="text-2xl font-bold text-blue-600">
                          {logData?.fraud_analysis_results?.fraud_orchestration?.fraud_decision?.approved_amount || '₹392,117'}
                        </p>
                      </div>
                      <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                        <p className="text-sm text-gray-600 mb-1">Risk Level</p>
                        <p className="text-2xl font-bold text-blue-600">
                          {logData?.fraud_analysis_results?.fraud_orchestration?.fraud_decision?.fraud_risk_level || 'LOW'}
                        </p>
                      </div>
                      <div 
                        className="text-center p-4 bg-white rounded-lg shadow-sm cursor-pointer hover:bg-blue-50 hover:shadow-md transition-all duration-200 border-2 border-transparent hover:border-blue-200"
                        onClick={() => onReviewApprove && onReviewApprove()}
                      >
                        <p className="text-sm text-gray-600 mb-1">Decision</p>
                        <p className="text-2xl font-bold text-green-600 hover:text-green-700">
                          View Details
                        </p>
                        <p className="text-xs text-gray-500 mt-1">Click to see full analysis</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>

        {/* Agent Modal */}
        {selectedAgent && (
          <AgentModal
            agent={selectedAgent}
            isOpen={isModalOpen}
            onClose={() => {
              setIsModalOpen(false);
              setSelectedAgent(null);
            }}
            stepNumber={agentMessages.findIndex(msg => msg.name === selectedAgent.name) + 1}
          />
        )}
      </div>
    </div>
  );
};