import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { DashboardStats } from '@/components/DashboardStats';
import { PatientSummary } from '@/components/PatientSummary';
import { ClaimAnalysis } from '@/components/ClaimAnalysis';
import { WorkflowDemoCard } from '@/components/WorkflowDemoCard';
import { InsuranceDashboardData } from '@/types/dashboard';
import { 
  Shield, 
  Users, 
  FileText, 
  RefreshCw,
  Download,
  Calendar,
  Clock
} from 'lucide-react';

// Import the dashboard data
import dashboardData from './dashboard-data.json';

interface InsurerDashboardProps {
  onClaimClick: (claimId: string) => void;
}

function InsurerDashboard({ onClaimClick }: InsurerDashboardProps) {
  const [data] = useState<InsuranceDashboardData>(dashboardData as InsuranceDashboardData);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
    }, 2000);
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(data, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `insurer-dashboard-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Shield className="h-8 w-8 text-primary" />
                <div>
                  <h1 className="text-2xl font-bold text-foreground">
                    Global Trust General
                  </h1>
                  <p className="text-sm text-gray-500">
                    AI-Powered Insurance Claims Management Dashboard
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Calendar className="h-4 w-4" />
                  <span>{currentTime.toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Clock className="h-4 w-4" />
                  <span>{currentTime.toLocaleTimeString()}</span>
                </div>
              </div>
              
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="flex items-center gap-2 px-3 py-2 text-sm border rounded-md hover:bg-gray-100/50 transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              
              <button
                onClick={handleExport}
                className="flex items-center gap-2 px-3 py-2 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
              >
                <Download className="h-4 w-4" />
                Export
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Workflow Demo Card */}
        <WorkflowDemoCard onClaimClick={onClaimClick} />
        
        {/* Top Statistics Section */}
        <DashboardStats data={data} />

        {/* Main Dashboard Tabs */}
        <Tabs defaultValue="patients" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="patients" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Claimant
            </TabsTrigger>
            <TabsTrigger value="claims" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Claims Analysis
            </TabsTrigger>
          </TabsList>

          <TabsContent value="patients" className="space-y-6">
            <PatientSummary patients={data.patients} onClaimClick={onClaimClick} />
          </TabsContent>

          <TabsContent value="claims" className="space-y-6">
            <ClaimAnalysis 
              claims={data.claims}
              claimAnalysis={data.claimAnalysis}
              agentMetrics={data.agentMetrics}
              onClaimClick={onClaimClick}
            />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t bg-gray-100/30 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              © 2024 Global Trust General. Powered by Azure AI and AutoGen Framework.
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span>Active Customers: {data.totalCustomers.toLocaleString()}</span>
              <span>•</span>
              <span>Claims Processed: {data.totalClaims.toLocaleString()}</span>
              <span>•</span>
              <span>Framework: AutoGen Multi-Agent</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default InsurerDashboard;
