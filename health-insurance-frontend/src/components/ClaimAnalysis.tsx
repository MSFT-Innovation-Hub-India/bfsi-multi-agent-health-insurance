import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ClaimSummary, ClaimAnalysis as ClaimAnalysisType, AgentMetrics } from '@/types/dashboard';
import { 
  Clock, 
  Users, 
  CheckCircle,
  XCircle,
  Timer,
  Activity,
  Eye
} from 'lucide-react';
import { DocumentViewer } from './DocumentViewer';

interface ClaimAnalysisProps {
  claims: ClaimSummary[];
  claimAnalysis: ClaimAnalysisType;
  agentMetrics: AgentMetrics;
  onClaimClick: (claimId: string) => void;
}

export const ClaimAnalysis: React.FC<ClaimAnalysisProps> = ({ 
  claims, 
  claimAnalysis, 
  agentMetrics,
  onClaimClick 
}) => {
  const [documentViewerClaimId, setDocumentViewerClaimId] = useState<string | null>(null);

  const handleViewDocuments = (claimId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDocumentViewerClaimId(claimId);
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'ACCEPTED': return 'success';
      case 'REJECTED': return 'danger';
      case 'PROCESSING': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ACCEPTED': return <CheckCircle className="h-4 w-4" />;
      case 'REJECTED': return <XCircle className="h-4 w-4" />;
      case 'PROCESSING': return <Timer className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const formatCurrency = (amount: number) => {
    return `₹${amount.toLocaleString()}`;
  };

  const getRiskColor = (score: number) => {
    if (score < 30) return 'text-green-600';
    if (score < 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const totalClaims = claimAnalysis.byStatus.accepted.count + 
                     claimAnalysis.byStatus.rejected.count + 
                     claimAnalysis.byStatus.processing.count;

  const acceptanceRate = (claimAnalysis.byStatus.accepted.count / totalClaims) * 100;
  const rejectionRate = (claimAnalysis.byStatus.rejected.count / totalClaims) * 100;

  return (
    <div className="space-y-6">
      {/* Status Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Accepted Claims
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-end">
                <span className="text-3xl font-bold text-green-600">
                  {claimAnalysis.byStatus.accepted.count}
                </span>
                <span className="text-sm text-gray-500">
                  {acceptanceRate.toFixed(1)}%
                </span>
              </div>
              <div className="text-sm text-gray-500">
                Avg Value: {formatCurrency(claimAnalysis.byStatus.accepted.averageValue)}
              </div>
              <div className="text-sm text-gray-500">
                Avg Agents: {claimAnalysis.byStatus.accepted.averageAgents.toFixed(1)}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <XCircle className="h-5 w-5 text-red-600" />
              Rejected Claims
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-end">
                <span className="text-3xl font-bold text-red-600">
                  {claimAnalysis.byStatus.rejected.count}
                </span>
                <span className="text-sm text-gray-500">
                  {rejectionRate.toFixed(1)}%
                </span>
              </div>
              <div className="text-sm text-gray-500">
                Avg Value: {formatCurrency(claimAnalysis.byStatus.rejected.averageValue)}
              </div>
              <div className="text-sm text-gray-500">
                Avg Agents: {claimAnalysis.byStatus.rejected.averageAgents.toFixed(1)}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Timer className="h-5 w-5 text-yellow-600" />
              Processing Claims
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-end">
                <span className="text-3xl font-bold text-yellow-600">
                  {claimAnalysis.byStatus.processing.count}
                </span>
                <span className="text-sm text-gray-500">
                  {((claimAnalysis.byStatus.processing.count / totalClaims) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="text-sm text-gray-500">
                Avg Value: {formatCurrency(claimAnalysis.byStatus.processing.averageValue)}
              </div>
              <div className="text-sm text-gray-500">
                Avg Agents: {claimAnalysis.byStatus.processing.averageAgents.toFixed(1)}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Agent Usage Analytics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                <span className="font-medium">Total Active Agents</span>
                <span className="text-2xl font-bold text-blue-600">
                  {agentMetrics.totalAgents}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                <span className="font-medium">Avg Agents per Claim</span>
                <span className="text-2xl font-bold text-green-600">
                  {agentMetrics.averageAgentsPerClaim.toFixed(1)}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                <span className="font-medium">Most Active Agent</span>
                <span className="text-lg font-bold text-purple-600">
                  {agentMetrics.mostActiveAgent}
                </span>
              </div>
            </div>
            <div className="space-y-3">
              <h4 className="font-medium text-gray-700">Agent Distribution</h4>
              {Object.entries(agentMetrics.agentUsageDistribution).map(([agent, count]) => (
                <div key={agent} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>{agent.replace('_', ' ')}</span>
                    <span className="font-medium">{count}</span>
                  </div>
                  <Progress value={(count / Math.max(...Object.values(agentMetrics.agentUsageDistribution))) * 100} className="h-2" />
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Claims List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Claim requests
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {claims.slice(0, 10).map((claim) => (
              <div
                key={claim.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                onClick={() => onClaimClick(claim.id)}
              >
                <div className="flex items-center gap-4">
                  <div className="flex items-center justify-center w-10 h-10 bg-gray-100 rounded-full">
                    {getStatusIcon(claim.status)}
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{claim.patientName}</span>
                      <Badge variant={getStatusBadgeVariant(claim.status)} className="text-xs">
                        {claim.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>ID: {claim.id}</span>
                      <span>Submitted: {new Date(claim.submissionDate).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-6 text-right">
                  <div>
                    <p className="text-sm text-gray-500">Claim Amount</p>
                    <p className="font-semibold">{formatCurrency(claim.claimAmount)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Agents Used</p>
                    <p className="font-semibold text-center">{claim.agentsUsed}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Risk Score</p>
                    <p className={`font-semibold text-center ${getRiskColor(claim.riskScore)}`}>
                      {claim.riskScore}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Processing Time</p>
                    <p className="font-semibold text-center">{claim.processingTime.toFixed(1)}s</p>
                  </div>
                  <button
                    onClick={(e) => handleViewDocuments(claim.id, e)}
                    className="flex items-center gap-2 px-3 py-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
                    title="View Documents"
                  >
                    <Eye className="h-4 w-4" />
                    <span className="text-sm font-medium">Docs</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Document Viewer Modal */}
      {documentViewerClaimId && (
        <DocumentViewer
          claimId={documentViewerClaimId}
          onClose={() => setDocumentViewerClaimId(null)}
        />
      )}
    </div>
  );
};