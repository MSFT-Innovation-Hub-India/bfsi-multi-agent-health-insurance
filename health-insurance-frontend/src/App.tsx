// Health Insurance Claims - App.tsx
import { useEffect } from 'react';
import { Routes, Route, useNavigate, useParams, useLocation } from 'react-router-dom';
import InsurerDashboard from './InsurerDashboard';
import { MultiAgentWorkflowPipeline } from './components/MultiAgentWorkflowPipeline';
import { ClaimAnalysisPage } from './components/ClaimAnalysisPage';
import { triggerProcessing } from './api/processingTrigger';

// Wrapper components that read URL params and wire up navigation

function DashboardPage() {
  const navigate = useNavigate();

  const handleClaimClick = (claimId: string) => {
    // Fire and forget - trigger processing API in background
    triggerProcessing(claimId);
    navigate(`/claims/${claimId}/workflow`);
  };

  const handleProcessedClaimClick = (claimId: string) => {
    navigate(`/claims/${claimId}/workflow?processed=true`);
  };

  return (
    <InsurerDashboard
      onClaimClick={handleClaimClick}
      onProcessedClaimClick={handleProcessedClaimClick}
    />
  );
}

function WorkflowPage() {
  const { claimId } = useParams<{ claimId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const isPreProcessed = new URLSearchParams(location.search).get('processed') === 'true';

  if (!claimId) return null;

  return (
    <MultiAgentWorkflowPipeline
      claimId={claimId}
      onBack={() => navigate('/')}
      onReviewApprove={() => navigate(`/claims/${claimId}/analysis`)}
      isPreProcessed={isPreProcessed}
    />
  );
}

function AnalysisPage() {
  const { claimId } = useParams<{ claimId: string }>();
  const navigate = useNavigate();

  if (!claimId) return null;

  return (
    <ClaimAnalysisPage
      claimId={claimId}
      onBack={() => navigate(`/claims/${claimId}/workflow`)}
    />
  );
}

function App() {
  const location = useLocation();

  // Scroll to top whenever route changes
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [location.pathname]);

  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/claims/:claimId/workflow" element={<WorkflowPage />} />
      <Route path="/claims/:claimId/analysis" element={<AnalysisPage />} />
    </Routes>
  );
}

export default App;
