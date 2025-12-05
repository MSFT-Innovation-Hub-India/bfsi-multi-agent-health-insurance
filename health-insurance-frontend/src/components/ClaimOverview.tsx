import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { PatientDetails, FraudDecision } from '@/types/claim';
import { 
  User, 
  CreditCard, 
  Calendar, 
  Hospital, 
  FileText, 
  Shield,
  Clock
} from 'lucide-react';
import { RupeeIcon } from '@/components/ui/rupee-icon';

interface ClaimOverviewProps {
  patientDetails: PatientDetails;
  fraudDecision: FraudDecision;
  processingTime: number;
}

export const ClaimOverview: React.FC<ClaimOverviewProps> = ({
  patientDetails,
  fraudDecision,
  processingTime
}) => {
  const utilizationPercentage = parseFloat(fraudDecision.policy_utilization);
  
  const getRiskBadgeVariant = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW': return 'success';
      case 'MEDIUM': return 'warning';
      case 'HIGH': return 'danger';
      default: return 'default';
    }
  };

  const getDecisionBadgeVariant = (decision: string) => {
    switch (decision) {
      case 'APPROVED': return 'success';
      case 'REJECTED': return 'danger';
      case 'PENDING': return 'warning';
      default: return 'default';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Patient Information */}
      <Card className="col-span-1 md:col-span-2 lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Patient Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm">Name:</span>
                <span className="text-sm">{patientDetails.patient_name}</span>
              </div>
              <div className="flex items-center gap-2">
                <CreditCard className="h-4 w-4" />
                <span className="font-medium text-sm">Policy:</span>
                <span className="text-sm font-mono">{patientDetails.policy_number}</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <span className="font-medium text-sm">Claim Date:</span>
                <span className="text-sm">{new Date(patientDetails.claim_date).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center gap-2">
                <Hospital className="h-4 w-4" />
                <span className="font-medium text-sm">Hospital:</span>
                <span className="text-sm">{patientDetails.hospital_name}</span>
              </div>
            </div>
            <div className="space-y-3">
              <div>
                <span className="font-medium text-sm">Diagnosis:</span>
                <p className="text-sm mt-1">{patientDetails.diagnosis}</p>
              </div>
              <div>
                <span className="font-medium text-sm">Treatment:</span>
                <p className="text-sm mt-1">{patientDetails.treatment_type}</p>
              </div>
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                <span className="font-medium text-sm">Documents:</span>
                <div className="flex flex-wrap gap-1">
                  {patientDetails.documents_available.map((doc, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {doc.replace('_', ' ')}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Claim Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Claim Status
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <Badge 
              variant={getDecisionBadgeVariant(fraudDecision.decision)} 
              className="text-lg px-4 py-2"
            >
              {fraudDecision.decision}
            </Badge>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Risk Level:</span>
              <Badge variant={getRiskBadgeVariant(fraudDecision.fraud_risk_level)}>
                {fraudDecision.fraud_risk_level}
              </Badge>
            </div>
            
            <div className="flex justify-between text-sm">
              <span>Balance Status:</span>
              <Badge variant="outline">{fraudDecision.balance_status}</Badge>
            </div>
            
            <div className="flex items-center gap-2 text-sm">
              <Clock className="h-4 w-4" />
              <span>Processed in:</span>
              <span className="font-mono">{processingTime.toFixed(2)}s</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Financial Summary */}
      <Card className="col-span-1 md:col-span-2 lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RupeeIcon className="h-5 w-5" />
            Financial Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-100 rounded-lg">
              <p className="text-sm text-gray-500">Claimed Amount</p>
              <p className="text-2xl font-bold">₹{patientDetails.claim_amount.toLocaleString()}</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-500">Approved Amount</p>
              <p className="text-2xl font-bold text-green-600">
                {fraudDecision.approved_amount}
              </p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-500">Remaining Balance</p>
              <p className="text-2xl font-bold text-blue-600">
                {fraudDecision.remaining_balance}
              </p>
            </div>
          </div>
          
          <div className="mt-6">
            <div className="flex justify-between text-sm mb-2">
              <span>Policy Utilization</span>
              <span>{fraudDecision.policy_utilization}</span>
            </div>
            <Progress value={utilizationPercentage} className="h-3" />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>₹0</span>
              <span>₹{patientDetails.policy_coverage_limit.toLocaleString()}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Decision Rationale */}
      <Card>
        <CardHeader>
          <CardTitle>Decision Rationale</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500 leading-relaxed">
            {fraudDecision.rationale}
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
