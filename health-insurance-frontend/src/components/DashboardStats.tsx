import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RupeeIcon } from '@/components/ui/rupee-icon';
import { InsuranceDashboardData } from '@/types/dashboard';
import { 
  Users, 
  FileText, 
  TrendingUp,
  Activity,
  Shield
} from 'lucide-react';

interface DashboardStatsProps {
  data: InsuranceDashboardData;
}

export const DashboardStats: React.FC<DashboardStatsProps> = ({ data }) => {
  const formatCurrency = (amount: number) => {
    return `₹${(amount / 10000000).toFixed(1)}Cr`;
  };

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  const totalAccepted = data.claimAnalysis.byStatus.accepted.count;
  const totalRejected = data.claimAnalysis.byStatus.rejected.count;
  const totalProcessing = data.claimAnalysis.byStatus.processing.count;
  const totalClaims = totalAccepted + totalRejected + totalProcessing;
  const acceptanceRate = ((totalAccepted / totalClaims) * 100).toFixed(1);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {/* Total Customers */}
      <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">Total Customers</span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-1">
            <div className="text-3xl font-bold text-blue-900">
              {formatNumber(data.totalCustomers)}
            </div>
            <div className="flex items-center gap-1 text-sm text-blue-600">
              <TrendingUp className="h-4 w-4" />
              <span>Active Policies</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Total Claims */}
      <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">Total Claims</span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-1">
            <div className="text-3xl font-bold text-blue-900">
              {formatNumber(data.totalClaims)}
            </div>
            <div className="flex items-center gap-1 text-sm text-blue-600">
              <Activity className="h-4 w-4" />
              <span>{acceptanceRate}% Accepted</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Total Claim Value */}
      <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <RupeeIcon className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">Total Claim Value</span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-1">
            <div className="text-3xl font-bold text-blue-900">
              {formatCurrency(data.totalClaimValue)}
            </div>
            <div className="flex items-center gap-1 text-sm text-blue-600">
              <TrendingUp className="h-4 w-4" />
              <span>Claims Processed</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Processing Efficiency */}
      <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">Avg Processing</span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-1">
            <div className="text-3xl font-bold text-blue-900">
              {data.claimAnalysis.processingMetrics.averageProcessingTime.toFixed(1)}s
            </div>
            <div className="flex items-center gap-1 text-sm text-blue-600">
              <Activity className="h-4 w-4" />
              <span>{data.agentMetrics.averageAgentsPerClaim.toFixed(1)} Agents Avg</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};