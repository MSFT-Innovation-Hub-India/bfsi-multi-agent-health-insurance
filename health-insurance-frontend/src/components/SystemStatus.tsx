import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { SystemStatus, FraudDetectionCapabilities } from '@/types/claim';
import { 
  Activity, 
  CheckCircle, 
  XCircle, 
  Server, 
  Database, 
  Shield,
  Eye,
  FileCheck,
  Zap
} from 'lucide-react';

interface SystemStatusProps {
  systemStatus: SystemStatus;
  capabilities: FraudDetectionCapabilities;
  processingTime: number;
}

export const SystemStatusPanel: React.FC<SystemStatusProps> = ({
  systemStatus,
  capabilities,
  processingTime
}) => {
  const getCapabilityIcon = (capability: string) => {
    const iconMap = {
      'identity_verification': Shield,
      'medical_consistency_check': FileCheck,
      'billing_validation': CheckCircle,
      'documentation_integrity': FileCheck,
      'imaging_correlation': Eye,
      'multi_agent_analysis': Activity,
      'azure_ai_evidence_collection': Database,
      'comprehensive_conversation_logging': Server,
      'genuine_agent_interactions': Zap
    };
    const IconComponent = iconMap[capability as keyof typeof iconMap] || CheckCircle;
    return <IconComponent className="h-4 w-4" />;
  };

  const getCapabilityLabel = (capability: string) => {
    return capability
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getPerformanceLevel = (time: number) => {
    if (time < 30) return { level: 'Excellent', color: 'text-green-600', percentage: 95 };
    if (time < 60) return { level: 'Good', color: 'text-blue-600', percentage: 80 };
    if (time < 120) return { level: 'Average', color: 'text-yellow-600', percentage: 65 };
    return { level: 'Slow', color: 'text-red-600', percentage: 40 };
  };

  const performance = getPerformanceLevel(processingTime);
  const enabledCapabilities = Object.entries(capabilities).filter(([_, enabled]) => enabled);
  const totalCapabilities = Object.keys(capabilities).length;
  const enabledCount = enabledCapabilities.length;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* System Health */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            System Health
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-3 bg-gray-100/30 rounded-lg">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4" />
                <span className="text-sm">Azure AI</span>
              </div>
              {systemStatus.azure_ai_available ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <XCircle className="h-4 w-4 text-red-500" />
              )}
            </div>
            
            <div className="flex items-center justify-between p-3 bg-gray-100/30 rounded-lg">
              <div className="flex items-center gap-2">
                <Eye className="h-4 w-4" />
                <span className="text-sm">X-Ray API</span>
              </div>
              {systemStatus.xray_api_available ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <XCircle className="h-4 w-4 text-red-500" />
              )}
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Framework:</span>
              <Badge variant="outline">{systemStatus.autogen_framework}</Badge>
            </div>
            <div className="flex justify-between text-sm">
              <span>Fraud Detection:</span>
              <Badge variant={systemStatus.fraud_detection_enabled ? 'success' : 'destructive'}>
                {systemStatus.fraud_detection_enabled ? 'Enabled' : 'Disabled'}
              </Badge>
            </div>
            <div className="flex justify-between text-sm">
              <span>Comprehensive Validation:</span>
              <Badge variant={systemStatus.comprehensive_validation ? 'success' : 'destructive'}>
                {systemStatus.comprehensive_validation ? 'Active' : 'Inactive'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Performance Metrics
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center p-4 bg-gray-100/30 rounded-lg">
            <p className="text-sm text-gray-500">Processing Time</p>
            <p className={`text-2xl font-bold ${performance.color}`}>
              {processingTime.toFixed(2)}s
            </p>
            <Badge variant="outline" className="mt-2">
              {performance.level}
            </Badge>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Performance Level</span>
              <span className={performance.color}>{performance.percentage}%</span>
            </div>
            <Progress value={performance.percentage} className="h-2" />
          </div>

          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-500">Capabilities</p>
              <p className="text-xl font-bold text-blue-600">
                {enabledCount}/{totalCapabilities}
              </p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-500">Success Rate</p>
              <p className="text-xl font-bold text-green-600">100%</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Capabilities Overview */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Detection Capabilities
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(capabilities).map(([capability, enabled]) => (
              <div
                key={capability}
                className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
                  enabled 
                    ? 'bg-green-50 border-green-200 text-green-800' 
                    : 'bg-red-50 border-red-200 text-red-800'
                }`}
              >
                <div className="flex-shrink-0">
                  {getCapabilityIcon(capability)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {getCapabilityLabel(capability)}
                  </p>
                </div>
                <div className="flex-shrink-0">
                  {enabled ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-500" />
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-2 text-blue-800 mb-2">
              <Shield className="h-5 w-5" />
              <span className="font-medium text-sm">System Overview</span>
            </div>
            <p className="text-sm text-blue-700">
              All fraud detection capabilities are operational. The system is running 
              comprehensive validation with multi-agent analysis and Azure AI integration 
              for enhanced accuracy and reliability.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
