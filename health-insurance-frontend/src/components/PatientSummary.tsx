import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { PatientSummary as PatientSummaryType } from '@/types/dashboard';
import { 
  User, 
  CreditCard, 
  FileText, 
  Shield,
  Calendar,
  TrendingUp,
  AlertTriangle,
  Eye
} from 'lucide-react';
import { DocumentViewer } from './DocumentViewer';

interface PatientSummaryProps {
  patients: PatientSummaryType[];
  onClaimClick: (claimId: string) => void;
}

export const PatientSummary: React.FC<PatientSummaryProps> = ({ patients, onClaimClick }) => {
  const [documentViewerClaimId, setDocumentViewerClaimId] = useState<string | null>(null);

  const handleViewDocuments = (claimId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDocumentViewerClaimId(claimId);
  };

  // Map patient IDs to their claim IDs
  const patientToClaimMap: { [key: string]: string } = {
    'PAT001': 'CLM001-2024-LAKSHMI',
    'PAT016': 'CLM010-2025-AHSAN',
    // Add more mappings as needed
  };

  const getRiskBadgeVariant = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW': return 'success';
      case 'MEDIUM': return 'warning';
      case 'HIGH': return 'danger';
      default: return 'default';
    }
  };

  const formatCurrency = (amount: number) => {
    return `₹${amount.toLocaleString()}`;
  };

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5" />
          Policyholder Information
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {patients.map((patient) => {
            const claimId = patientToClaimMap[patient.id] || `CLM001-2024-${patient.name.split(' ')[0].toUpperCase()}`;
            return (
            <div
              key={patient.id}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
              onClick={() => onClaimClick(claimId)}
            >
              <div className="flex items-center gap-4">
                <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full">
                  <User className="h-6 w-6 text-blue-600" />
                </div>
                <div className="space-y-1">
                  <h3 className="font-semibold text-lg">{patient.name}</h3>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <CreditCard className="h-4 w-4" />
                      <span>{patient.policyNumber}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      <span>Age: {patient.age}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <FileText className="h-4 w-4" />
                      <span>{patient.claimCount} Claims</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-sm text-gray-500">Total Claim Value</p>
                  <p className="text-xl font-bold text-green-600">
                    {formatCurrency(patient.totalClaimValue)}
                  </p>
                </div>
                
                <div className="text-right">
                  <p className="text-sm text-gray-500">Last Claim</p>
                  <p className="text-sm font-medium">
                    {new Date(patient.lastClaimDate).toLocaleDateString()}
                  </p>
                </div>

                <div className="flex flex-col items-center gap-2">
                  <Badge variant={getRiskBadgeVariant(patient.riskLevel)}>
                    <Shield className="h-3 w-3 mr-1" />
                    {patient.riskLevel}
                  </Badge>
                  <div className="flex items-center gap-1">
                    {patient.activePolicy ? (
                      <div className="flex items-center text-green-600 text-xs">
                        <TrendingUp className="h-3 w-3 mr-1" />
                        Active
                      </div>
                    ) : (
                      <div className="flex items-center text-red-600 text-xs">
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        Inactive
                      </div>
                    )}
                  </div>
                </div>

                <button
                  onClick={(e) => handleViewDocuments(claimId, e)}
                  className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors border border-blue-200"
                  title="View Documents"
                >
                  <Eye className="h-4 w-4" />
                  <span className="text-sm font-medium">View Docs</span>
                </button>
              </div>
            </div>
            );
          })}
        </div>
      </CardContent>

      {/* Document Viewer Modal */}
      {documentViewerClaimId && (
        <DocumentViewer
          claimId={documentViewerClaimId}
          onClose={() => setDocumentViewerClaimId(null)}
        />
      )}
    </Card>
  );
};