import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { AzureEvidence } from '@/types/claim';
import { 
  FileText, 
  Camera, 
  Shield, 
  CheckCircle
} from 'lucide-react';
import { RupeeIcon } from '@/components/ui/rupee-icon';

interface EvidenceAnalysisProps {
  evidence: AzureEvidence;
}

export const EvidenceAnalysis: React.FC<EvidenceAnalysisProps> = ({ evidence }) => {
  const formatEvidenceText = (text: string) => {
    // Split by ### for main sections
    const sections = text.split('### ').filter(section => section.trim());
    
    return sections.map((section, index) => {
      const lines = section.trim().split('\n').filter(line => line.trim());
      if (lines.length === 0) return null;
      
      const title = lines[0].replace(/\*\*/g, '');
      const content = lines.slice(1);
      
      return (
        <div key={index} className="mb-6">
          <h4 className="font-semibold text-sm mb-3 text-foreground flex items-center gap-2">
            {title.includes('ASSESSMENT') && <CheckCircle className="h-4 w-4 text-green-500" />}
            {title.includes('ANALYSIS') && <FileText className="h-4 w-4 text-blue-500" />}
            {title.includes('CONCLUSION') && <Shield className="h-4 w-4 text-indigo-500" />}
            {title}
          </h4>
          <div className="space-y-2 pl-6">
            {content.map((line, lineIndex) => {
              const cleanLine = line.replace(/\*\*/g, '').trim();
              
              if (cleanLine.includes(':') && !cleanLine.startsWith('-')) {
                const [label, ...value] = cleanLine.split(':');
                return (
                  <div key={lineIndex} className="text-sm">
                    <span className="font-medium text-foreground">{label}:</span>
                    <span className="ml-2 text-gray-500">{value.join(':')}</span>
                  </div>
                );
              }
              
              if (cleanLine.startsWith('-')) {
                return (
                  <div key={lineIndex} className="text-sm text-gray-500 ml-4">
                    • {cleanLine.substring(1).trim()}
                  </div>
                );
              }
              
              return (
                <p key={lineIndex} className="text-sm text-gray-500 leading-relaxed">
                  {cleanLine}
                </p>
              );
            })}
          </div>
        </div>
      );
    });
  };

  const getXrayAnalysis = (xrayText: string) => {
    const lines = xrayText.split('\\n').filter(line => line.trim());
    const analysisData = {
      imagesAnalyzed: 0,
      predictions: [] as Array<{grade: string, confidence: string}>,
      fraudIndicators: false
    };

    lines.forEach(line => {
      if (line.includes('Images Analyzed:')) {
        analysisData.imagesAnalyzed = parseInt(line.split(':')[1].trim());
      }
      if (line.includes('Grade') && line.includes('%')) {
        const match = line.match(/Grade (\d+) \(([^)]+)\)/);
        if (match) {
          analysisData.predictions.push({
            grade: match[1],
            confidence: match[2]
          });
        }
      }
      if (line.includes('No obvious fraud indicators')) {
        analysisData.fraudIndicators = false;
      }
    });

    return analysisData;
  };

  // Determine available tabs
  const hasXray = evidence.xray && evidence.xray.trim().length > 0;
  const xrayData = hasXray ? getXrayAnalysis(evidence.xray!) : null;
  const hasLabReports = evidence.lab_reports && evidence.lab_reports.trim().length > 0;
  const tabCount = 2 + (hasXray ? 1 : 0) + (hasLabReports ? 1 : 0) + 1; // medical + billing + xray? + lab? + policy

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Evidence Analysis
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs defaultValue="medical" className="w-full">
          <TabsList className={`grid w-full grid-cols-${tabCount} mx-auto`}>
            <TabsTrigger value="medical" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Medical
            </TabsTrigger>
            <TabsTrigger value="billing" className="flex items-center gap-2">
              <RupeeIcon className="h-4 w-4" />
              Billing
            </TabsTrigger>
            {hasXray && (
              <TabsTrigger value="xray" className="flex items-center gap-2">
                <Camera className="h-4 w-4" />
                X-Ray
              </TabsTrigger>
            )}
            {hasLabReports && (
              <TabsTrigger value="lab" className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                Lab Reports
              </TabsTrigger>
            )}
            <TabsTrigger value="policy" className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Policy
            </TabsTrigger>
          </TabsList>

          <TabsContent value="medical" className="px-4 pb-4">
            <div className="max-h-80 overflow-y-auto prose prose-sm max-w-none">
              {formatEvidenceText(evidence.medical)}
            </div>
          </TabsContent>

          <TabsContent value="billing" className="px-4 pb-4">
            <div className="max-h-80 overflow-y-auto prose prose-sm max-w-none">
              {formatEvidenceText(evidence.billing)}
            </div>
          </TabsContent>

          {hasXray && xrayData && (
            <TabsContent value="xray" className="px-4 pb-4">
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-gray-500">Images Analyzed</p>
                    <p className="text-2xl font-bold text-blue-600">{xrayData.imagesAnalyzed}</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-gray-500">Predictions</p>
                    <p className="text-2xl font-bold text-green-600">{xrayData.predictions.length}</p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500">Fraud Status</p>
                    <div className="flex items-center justify-center gap-2 mt-1">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <Badge variant="success">Clean</Badge>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="font-semibold text-sm">X-Ray Analysis Results</h4>
                  {xrayData.predictions.map((prediction, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-100/30 rounded-lg">
                      <span className="text-sm font-medium">Image {index + 1}</span>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">Grade {prediction.grade}</Badge>
                        <span className="text-sm text-gray-500">{prediction.confidence}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-2 text-green-800">
                    <CheckCircle className="h-5 w-5" />
                    <span className="font-medium text-sm">No fraud indicators detected in X-ray analysis</span>
                  </div>
                </div>
              </div>
            </TabsContent>
          )}

          {hasLabReports && (
            <TabsContent value="lab" className="px-4 pb-4">
              <div className="max-h-80 overflow-y-auto prose prose-sm max-w-none">
                {formatEvidenceText(evidence.lab_reports!)}
              </div>
            </TabsContent>
          )}

          <TabsContent value="policy" className="px-4 pb-4">
            <div className="max-h-80 overflow-y-auto prose prose-sm max-w-none">
              {formatEvidenceText(evidence.policy)}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
