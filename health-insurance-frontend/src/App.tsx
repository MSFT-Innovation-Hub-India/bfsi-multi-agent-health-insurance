// Health Insurance Claims - App.tsx
import { useState, useEffect } from 'react';
import InsurerDashboard from './InsurerDashboard';
import { MultiAgentWorkflowPipeline } from './components/MultiAgentWorkflowPipeline';
import { ClaimAnalysisPage } from './components/ClaimAnalysisPage';
import { triggerProcessing } from './api/processingTrigger';

function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'workflow' | 'overview'>('dashboard');
  const [selectedClaimId, setSelectedClaimId] = useState<string>('');

  // Scroll to top whenever view changes
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentView]);

  const handleClaimClick = (claimId: string) => {
    setSelectedClaimId(claimId);
    setCurrentView('workflow');
    
    // Fire and forget - trigger processing API in background
    // Frontend continues using static JSON for display
    triggerProcessing(claimId);
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    setSelectedClaimId('');
  };

  const handleViewDetails = () => {
    setCurrentView('overview');
  };

  const handleBackToWorkflow = () => {
    setCurrentView('workflow');
  };

  if (currentView === 'overview') {
    return (
      <ClaimAnalysisPage 
        claimId={selectedClaimId} 
        onBack={handleBackToWorkflow} 
      />
    );
  }

  if (currentView === 'workflow') {
    return (
      <MultiAgentWorkflowPipeline 
        claimId={selectedClaimId} 
        onBack={handleBackToDashboard}
        onReviewApprove={handleViewDetails}
      />
    );
  }

  return (
    <InsurerDashboard onClaimClick={handleClaimClick} />
  );
}

export default App;
