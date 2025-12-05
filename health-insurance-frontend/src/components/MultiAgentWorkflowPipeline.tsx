import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  ArrowLeft,
  CheckCircle,
  FileText,
  Shield,
  CreditCard,
  Activity,
  Eye,
  Workflow,
  ArrowDown,
  ArrowRight,
  Clock,
  XCircle,
  PlayCircle,
  Pause
} from 'lucide-react';
import { RupeeIcon } from '@/components/ui/rupee-icon';
import { AgentMessage, parseAgentMessages, formatAgentName, extractSummary } from '@/utils/agentParser';
import { AgentModal } from './AgentModal';
import { getLogDataForClaim } from '@/utils/logLoader';

interface MultiAgentWorkflowPipelineProps {
  claimId: string;
  onBack: () => void;
  onReviewApprove?: () => void;
}

// Agent workflow stages configuration
const WORKFLOW_STAGES = [
  {
    id: 1,
    type: 'sequential',
    agents: ['Fraud_Detection_Specialist'],
    name: 'Preliminary Fraud Detection',
    description: 'Primary fraud risk assessment and identity verification'
  },
  {
    id: 2,
    type: 'parallel',
    agents: ['Diagnostic_Validator', 'Billing_Fraud_Validator'],
    name: 'Diagnostic and Billing Validation',
    description: 'Diagnostic evidence and billing fraud validation'
  },
  {
    id: 3,
    type: 'sequential',
    agents: ['Policy_Balance_Validator'],
    name: 'Policy Validation',
    description: 'Policy coverage and balance verification'
  },
  {
    id: 4,
    type: 'sequential',
    agents: ['Policy_Adjustment_Coordinator'],
    name: 'Policy Adjustment',
    description: 'Policy exclusions and amount calculations'
  },
  {
    id: 5,
    type: 'sequential',
    agents: ['Decision_Coordinator'],
    name: 'Final Decision',
    description: 'Consolidation and final claim decision'
  }
];

interface AgentStatus {
  name: string;
  status: 'pending' | 'in-progress' | 'completed' | 'error';
  startTime?: number;
  endTime?: number;
  progress: number;
}

const agentIcons: { [key: string]: React.ReactNode } = {
  'Fraud_Detection_Specialist': <Shield className="h-5 w-5" />,
  'Diagnostic_Validator': <FileText className="h-5 w-5" />,
  'Medical_Validator': <FileText className="h-5 w-5" />,
  'Billing_Fraud_Validator': <CreditCard className="h-5 w-5" />,
  'Policy_Balance_Validator': <RupeeIcon className="h-5 w-5" />,
  'Policy_Adjustment_Coordinator': <Activity className="h-5 w-5" />,
  'Decision_Coordinator': <CheckCircle className="h-5 w-5" />
};

const statusColors = {
  pending: 'bg-gray-100 border-gray-300 text-gray-600',
  'in-progress': 'bg-blue-100 border-blue-400 text-blue-800',
  completed: 'bg-blue-50 border-blue-300 text-blue-700',
  error: 'bg-red-100 border-red-400 text-red-800'
};

const statusIcons = {
  pending: <Clock className="h-4 w-4" />,
  'in-progress': <PlayCircle className="h-4 w-4" />,
  completed: <CheckCircle className="h-4 w-4" />,
  error: <XCircle className="h-4 w-4" />
};

const getAgentDescription = (agentName: string): string => {
  const descriptions: { [key: string]: string } = {
    'Fraud_Detection_Specialist': 'Performs initial fraud risk assessment and identity verification across all claim documents.',
    'Diagnostic_Validator': 'Reviews medical evidence consistency, validates diagnosis appropriateness, and checks treatment protocols.',
    'Medical_Validator': 'Reviews medical evidence consistency, validates diagnosis appropriateness, and checks treatment protocols.',
    'Billing_Fraud_Validator': 'Analyzes billing accuracy, checks for duplicate charges, and validates hospital invoice authenticity.',
    'Policy_Balance_Validator': 'Verifies policy coverage limits, calculates available balance, and ensures claim compliance.',
    'Policy_Adjustment_Coordinator': 'Applies policy exclusions, calculates final approved amounts, and manages adjustments.',
    'Decision_Coordinator': 'Consolidates all agent findings and provides final claim approval or rejection decision.'
  };
  return descriptions[agentName] || 'AI agent responsible for specialized claim analysis tasks.';
};

export const MultiAgentWorkflowPipeline: React.FC<MultiAgentWorkflowPipelineProps> = ({ 
  claimId, 
  onBack, 
  onReviewApprove 
}) => {
  // Load the appropriate log data based on claim ID
  const logData = getLogDataForClaim(claimId);
  
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [agentStatuses, setAgentStatuses] = useState<{ [key: string]: AgentStatus }>({});
  const [isProcessing, setIsProcessing] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<AgentMessage | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [allMessages] = useState<AgentMessage[]>(
    parseAgentMessages(logData?.fraud_analysis_results?.fraud_orchestration?.detailed_messages || [])
  );

  // Initialize agent statuses and reset workflow
  useEffect(() => {
    const initialStatuses: { [key: string]: AgentStatus } = {};
    WORKFLOW_STAGES.forEach(stage => {
      stage.agents.forEach(agentName => {
        initialStatuses[agentName] = {
          name: agentName,
          status: 'pending',
          progress: 0
        };
      });
    });
    setAgentStatuses(initialStatuses);
    setCurrentStageIndex(0);
    setIsProcessing(true);
    setIsPaused(false);
  }, [claimId]); // Reset when claimId changes

  // Workflow progression logic
  useEffect(() => {
    console.log(`Stage ${currentStageIndex + 1}: Starting workflow stage`, WORKFLOW_STAGES[currentStageIndex]?.name);
    
    if (isPaused || currentStageIndex >= WORKFLOW_STAGES.length) {
      console.log('Workflow completed or paused');
      setIsProcessing(false);
      return;
    }

    const currentStage = WORKFLOW_STAGES[currentStageIndex];
    const stageAgents = currentStage.agents;
    console.log(`Processing agents: ${stageAgents.join(', ')}`);

    // Start agents in current stage
    setAgentStatuses(prev => {
      const updated = { ...prev };
      stageAgents.forEach(agentName => {
        if (updated[agentName]?.status === 'pending') {
          updated[agentName] = {
            ...updated[agentName],
            status: 'in-progress',
            startTime: Date.now()
          };
        }
      });
      return updated;
    });

    // Simulate agent processing with different durations
    const processingTimers = stageAgents.map((agentName, index) => {
      const duration = currentStage.type === 'parallel' ? 7000 + (index * 1500) : 6000;
      
      return setTimeout(() => {
        console.log(`Agent ${agentName} completed processing`);
        setAgentStatuses(prev => ({
          ...prev,
          [agentName]: {
            ...prev[agentName],
            status: 'completed',
            endTime: Date.now(),
            progress: 100
          }
        }));
      }, duration);
    });

    // Progress simulation for in-progress agents
    const progressInterval = setInterval(() => {
      setAgentStatuses(prev => {
        const updated = { ...prev };
        stageAgents.forEach(agentName => {
          if (updated[agentName]?.status === 'in-progress' && updated[agentName].progress < 95) {
            updated[agentName] = {
              ...updated[agentName],
              progress: Math.min(95, updated[agentName].progress + Math.random() * 10)
            };
          }
        });
        return updated;
      });
    }, 500);

    // Move to next stage timer
    const maxDuration = Math.max(...stageAgents.map((_, index) => 
      currentStage.type === 'parallel' ? 7000 + (index * 1500) : 6000
    ));
    
    const stageTimer = setTimeout(() => {
      console.log(`Stage ${currentStageIndex + 1} completed, moving to next stage`);
      setCurrentStageIndex(prev => prev + 1);
    }, maxDuration + 1500);

    return () => {
      processingTimers.forEach(timer => clearTimeout(timer));
      clearInterval(progressInterval);
      clearTimeout(stageTimer);
    };
  }, [currentStageIndex, isPaused]);

  const getOverallProgress = () => {
    const totalAgents = Object.keys(agentStatuses).length;
    const completedAgents = Object.values(agentStatuses).filter(status => status.status === 'completed').length;
    return totalAgents > 0 ? (completedAgents / totalAgents) * 100 : 0;
  };

  const handleAgentClick = (agentName: string) => {
    // Map Diagnostic_Validator to Medical_Validator for backward compatibility
    const mappedName = agentName === 'Diagnostic_Validator' ? 'Medical_Validator' : agentName;
    const agentMessage = allMessages.find(msg => msg.name === mappedName || msg.name === agentName);
    if (agentMessage) {
      setSelectedAgent(agentMessage);
      setIsModalOpen(true);
    }
  };

  const renderAgent = (agentName: string, isParallel: boolean = false, parallelIndex: number = 0) => {
    const status = agentStatuses[agentName];
    if (!status) return null;

    // Map Diagnostic_Validator to Medical_Validator for backward compatibility
    const mappedName = agentName === 'Diagnostic_Validator' ? 'Medical_Validator' : agentName;
    const agentMessage = allMessages.find(msg => msg.name === mappedName || msg.name === agentName);
    const summary = agentMessage ? extractSummary(agentMessage.content) : null;

    return (
      <motion.div
        key={agentName}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: isParallel ? parallelIndex * 0.2 : 0 }}
        className={`relative ${isParallel ? 'flex-1' : 'w-full max-w-md mx-auto'}`}
      >
        <Card 
          className={`cursor-pointer transition-all duration-300 hover:shadow-lg border-2 ${statusColors[status.status]} ${
            status.status === 'in-progress' ? 'animate-pulse' : ''
          }`}
          onClick={() => handleAgentClick(agentName)}
        >
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  status.status === 'completed' ? 'bg-green-100 border-green-400' :
                  status.status === 'in-progress' ? 'bg-blue-100 border-blue-400' :
                  status.status === 'error' ? 'bg-red-100 border-red-400' :
                  'bg-gray-100 border-gray-300'
                }`}>
                  {status.status === 'completed' ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : status.status === 'in-progress' ? (
                    <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}>
                      {agentIcons[agentName]}
                    </motion.div>
                  ) : status.status === 'error' ? (
                    <XCircle className="h-5 w-5 text-red-600" />
                  ) : (
                    agentIcons[agentName]
                  )}
                </div>
                <div>
                  <h4 className="font-semibold text-sm">{formatAgentName(agentName)}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                      {statusIcons[status.status]}
                      <span className="ml-1 capitalize">{status.status.replace('-', ' ')}</span>
                    </Badge>
                  </div>
                </div>
              </div>
              {(status.status === 'completed' || status.status === 'in-progress') && (
                <button className="text-xs px-2 py-1 bg-white bg-opacity-70 rounded hover:bg-opacity-100 transition-colors">
                  <Eye className="h-3 w-3" />
                </button>
              )}
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <p className="text-xs text-gray-600 mb-3">
              {getAgentDescription(agentName)}
            </p>
            
            {status.status === 'in-progress' && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span>Progress</span>
                  <span>{Math.round(status.progress)}%</span>
                </div>
                <Progress value={status.progress} className="h-1" />
              </div>
            )}
            
            {status.status === 'completed' && (
              <div className="bg-white bg-opacity-60 rounded p-2 text-xs">
                {summary && summary.summary.length > 10 && !summary.summary.includes('Analysis in progress') ? (
                  <>
                    <p className="font-medium text-gray-700 mb-1">Key Finding:</p>
                    <p className="text-gray-600 line-clamp-2">
                      {summary.summary.slice(0, 60)}...
                    </p>
                  </>
                ) : (
                  <>
                    <p className="font-medium text-gray-700 mb-1">Analysis Complete:</p>
                    <p className="text-gray-600">
                      {agentName === 'Fraud_Detection_Specialist' && 'Fraud risk assessment completed'}
                      {agentName === 'Diagnostic_Validator' && 'Diagnostic evidence verified'}
                      {agentName === 'Medical_Validator' && 'Medical evidence verified'}
                      {agentName === 'Billing_Fraud_Validator' && 'Billing accuracy confirmed'}
                      {agentName === 'Policy_Balance_Validator' && 'Policy balance validated'}
                      {agentName === 'Policy_Adjustment_Coordinator' && 'Policy adjustments applied'}
                      {agentName === 'Decision_Coordinator' && 'Final decision rendered'}
                      {!['Fraud_Detection_Specialist', 'Diagnostic_Validator', 'Medical_Validator', 'Billing_Fraud_Validator', 
                         'Policy_Balance_Validator', 'Policy_Adjustment_Coordinator', 'Decision_Coordinator'].includes(agentName) 
                         && 'Click to view full details'}
                    </p>
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  const renderFlowConnector = (direction: 'down' | 'right' = 'down', isActive: boolean = true) => {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: isActive ? 1 : 0.3 }}
        className="flex items-center justify-center py-4"
      >
        {direction === 'down' ? (
          <motion.div
            animate={isActive ? { y: [0, 5, 0] } : {}}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <ArrowDown className={`h-6 w-6 ${isActive ? 'text-blue-500' : 'text-gray-300'}`} />
          </motion.div>
        ) : (
          <motion.div
            animate={isActive ? { x: [0, 5, 0] } : {}}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <ArrowRight className={`h-6 w-6 ${isActive ? 'text-blue-500' : 'text-gray-300'}`} />
          </motion.div>
        )}
      </motion.div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow-md p-6 mb-6"
        >
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
                  Multi-Agent Workflow Pipeline
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
              <button
                onClick={() => setIsPaused(!isPaused)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  isPaused 
                    ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                    : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                }`}
              >
                {isPaused ? <PlayCircle className="h-4 w-4 mr-2" /> : <Pause className="h-4 w-4 mr-2" />}
                {isPaused ? 'Resume' : 'Pause'}
              </button>
              <Badge variant={isProcessing ? "warning" : "success"} className="px-3 py-1">
                {isProcessing ? "Processing..." : "Completed"}
              </Badge>
              <div className="text-sm text-gray-500">
                Stage {Math.min(currentStageIndex + 1, WORKFLOW_STAGES.length)} of {WORKFLOW_STAGES.length}
              </div>
            </div>
          </div>
          
          {/* Overall Progress */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Overall Progress</span>
              <span>{Math.round(getOverallProgress())}%</span>
            </div>
            <Progress value={getOverallProgress()} className="h-2" />
          </div>
        </motion.div>

        {/* Workflow Pipeline */}
        <div className="space-y-6">
          {WORKFLOW_STAGES.map((stage, stageIndex) => (
            <motion.div
              key={stage.id}
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: stageIndex * 0.1 }}
              className={`${stageIndex <= currentStageIndex ? 'opacity-100' : 'opacity-50'}`}
            >
              {/* Stage Header */}
              <div className="text-center mb-4">
                <motion.div
                  animate={stageIndex === currentStageIndex ? { scale: [1, 1.05, 1] } : {}}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Badge 
                    variant={stageIndex < currentStageIndex ? "success" : stageIndex === currentStageIndex ? "warning" : "outline"}
                    className="px-4 py-2 text-sm font-medium"
                  >
                    Stage {stage.id}: {stage.name}
                  </Badge>
                </motion.div>
                <p className="text-sm text-gray-600 mt-1">{stage.description}</p>
              </div>

              {/* Agents Layout */}
              {stage.type === 'parallel' ? (
                <div className="flex gap-6 justify-center">
                  {stage.agents.map((agentName, index) => (
                    <React.Fragment key={agentName}>
                      {renderAgent(agentName, true, index)}
                    </React.Fragment>
                  ))}
                </div>
              ) : (
                <div className="flex justify-center">
                  {renderAgent(stage.agents[0])}
                </div>
              )}

              {/* Flow Connector */}
              {stageIndex < WORKFLOW_STAGES.length - 1 && (
                renderFlowConnector('down', stageIndex < currentStageIndex)
              )}
            </motion.div>
          ))}

          {/* Final Decision Summary */}
          {!isProcessing && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 }}
            >
              <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200 shadow-xl max-w-2xl mx-auto">
                <CardHeader>
                  <CardTitle className="flex items-center justify-center gap-3 text-blue-800">
                    <CheckCircle className="h-8 w-8" />
                    <span className="text-2xl">Workflow Complete</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <motion.div 
                      whileHover={{ scale: 1.05 }}
                      className="text-center p-4 bg-white rounded-lg shadow-sm"
                    >
                      <p className="text-sm text-gray-600 mb-1">Approved Amount</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {logData?.fraud_analysis_results?.fraud_orchestration?.fraud_decision?.approved_amount || '₹392,117'}
                      </p>
                    </motion.div>
                    <motion.div 
                      whileHover={{ scale: 1.05 }}
                      className="text-center p-4 bg-white rounded-lg shadow-sm"
                    >
                      <p className="text-sm text-gray-600 mb-1">Risk Level</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {logData?.fraud_analysis_results?.fraud_orchestration?.fraud_decision?.fraud_risk_level || 'LOW'}
                      </p>
                    </motion.div>
                    <motion.div 
                      whileHover={{ scale: 1.05 }}
                      className="text-center p-4 bg-white rounded-lg shadow-sm cursor-pointer hover:bg-blue-50 transition-colors"
                      onClick={() => onReviewApprove && onReviewApprove()}
                    >
                      <p className="text-sm text-gray-600 mb-1">Decision</p>
                      <p className="text-2xl font-bold text-green-600">
                        APPROVED
                      </p>
                      <p className="text-xs text-gray-500 mt-1">Click for details</p>
                    </motion.div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>

        {/* Agent Modal */}
        <AnimatePresence>
          {selectedAgent && (
            <AgentModal
              agent={selectedAgent}
              isOpen={isModalOpen}
              onClose={() => {
                setIsModalOpen(false);
                setSelectedAgent(null);
              }}
              stepNumber={allMessages.findIndex(msg => msg.name === selectedAgent.name) + 1}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};