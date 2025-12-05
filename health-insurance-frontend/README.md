# 🏥 Health Insurance Claims Dashboard

A comprehensive React-based dashboard for managing and processing health insurance claims using Multi-Agent AI workflows.

![React](https://img.shields.io/badge/React-19-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg)
![Vite](https://img.shields.io/badge/Vite-5-646CFF.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3-06B6D4.svg)

## ✨ Features

- **Claims Management Dashboard**: Overview of all health insurance claims
- **Multi-Agent AI Workflow**: Visualize how specialized AI agents collaborate to process claims
- **Real-time Processing Simulation**: Watch agents analyze claims step-by-step
- **Detailed Claim Analysis**: Deep dive into individual claims with:
  - Patient summaries
  - Medical evidence analysis
  - Agent conversations
  - Risk assessments
  - Final recommendations
- **Interactive Workflow Pipeline**: See the flow of information between agents
- **Document Viewer**: View claim documents and evidence

## 🤖 AI Agents Visualization

The dashboard visualizes the collaboration between 6 specialized AI agents:

| Agent | Color | Role |
|-------|-------|------|
| **Fraud Detection Specialist** | 🔴 Red | Identity verification, document authenticity |
| **Medical Validator** | 🟢 Green | Medical consistency, clinical appropriateness |
| **Billing Validator** | 🔵 Blue | Billing accuracy, duplicate charges |
| **Policy Balance Validator** | 🟡 Yellow | Balance sufficiency, limits |
| **Coverage Exclusions Validator** | 🟣 Purple | Policy exclusions |
| **Fraud Coordinator** | ⚫ Black | Final decision |

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd health-insurance-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will open at `http://localhost:5173`

### Build for Production

```bash
npm run build
npm run preview
```

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | React 19 |
| **Language** | TypeScript 5 |
| **Build Tool** | Vite 5 |
| **Styling** | TailwindCSS 3 |
| **Animation** | Framer Motion |
| **Charts** | Recharts |
| **Icons** | Lucide React |
| **Components** | Radix UI |

## 📁 Project Structure

```
health-insurance-frontend/
│
├── src/
│   ├── App.tsx                    # Main app with routing
│   ├── InsurerDashboard.tsx       # Claims dashboard
│   ├── main.tsx                   # Entry point
│   ├── index.css                  # Global styles
│   │
│   ├── components/
│   │   ├── AgentConversation.tsx          # Agent chat view
│   │   ├── AgentModal.tsx                 # Agent details modal
│   │   ├── AgentWorkflow.tsx              # Workflow visualization
│   │   ├── ClaimAnalysis.tsx              # Claim analysis view
│   │   ├── ClaimAnalysisPage.tsx          # Full claim page
│   │   ├── ClaimOverview.tsx              # Claim summary
│   │   ├── DashboardStats.tsx             # Statistics cards
│   │   ├── DocumentViewer.tsx             # Document viewer
│   │   ├── EvidenceAnalysis.tsx           # Evidence review
│   │   ├── MultiAgentWorkflowPipeline.tsx # Main workflow
│   │   ├── PatientSummary.tsx             # Patient info
│   │   ├── SystemStatus.tsx               # System health
│   │   ├── WorkflowDemoCard.tsx           # Demo card
│   │   └── ui/                            # Reusable components
│   │       ├── badge.tsx
│   │       ├── card.tsx
│   │       ├── progress.tsx
│   │       ├── rupee-icon.tsx
│   │       └── tabs.tsx
│   │
│   ├── types/
│   │   ├── claim.ts                # Claim types
│   │   ├── dashboard.ts            # Dashboard types
│   │   ├── json.d.ts               # JSON declarations
│   │   └── underwriting.ts         # Underwriting types
│   │
│   ├── utils/
│   │   ├── agentParser.ts          # Parse agent responses
│   │   ├── azureStorage.ts         # Azure storage utils
│   │   ├── claimDataLoader.ts      # Load claim data
│   │   ├── logLoader.ts            # Load workflow logs
│   │   └── markdownSimplifier.ts   # Simplify markdown
│   │
│   ├── lib/
│   │   └── utils.ts                # Utility functions
│   │
│   └── styles/
│       └── workflow-animations.css  # Workflow animations
│
├── public/                         # Static assets
├── index.html                      # HTML template
├── package.json                    # Dependencies
├── vite.config.ts                  # Vite configuration
├── tailwind.config.js              # Tailwind configuration
├── tsconfig.json                   # TypeScript config
└── postcss.config.cjs              # PostCSS config
```

## 📊 Data Files

| File | Description |
|------|-------------|
| `dashboard-data.json` | Main claims dashboard data |
| `log.json` | Agent workflow logs (Claim 1) |
| `log2.json` | Agent workflow logs (Claim 2) |

## 🎨 Key Components

### `InsurerDashboard`
Main dashboard displaying:
- Claim statistics (total, approved, rejected, pending)
- Claims list with filtering
- Quick actions

### `MultiAgentWorkflowPipeline`
Interactive visualization showing:
- Agent processing steps
- Real-time progress animation
- Agent communication flow
- Final decision summary

### `ClaimAnalysisPage`
Comprehensive claim view with:
- Patient summary
- Evidence analysis tabs
- Agent conversation history
- Final recommendation

### `DocumentViewer`
View claim documents:
- Medical records
- Billing documents
- X-ray images
- Policy documents

## 🔧 Configuration

### Vite Configuration
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

### Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Custom colors for agents
      }
    }
  }
}
```

## 🎯 Screenshots

### Claims Dashboard
Overview of all claims with statistics and filtering.

### Workflow Pipeline
Visual representation of multi-agent collaboration.

### Claim Analysis
Detailed view with evidence and agent conversations.

## 📝 Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

## 🔗 Integration with Backend

The frontend connects to the Python backend for:
- Loading claim data
- Fetching agent workflow logs
- Displaying analysis results

```typescript
// Example: Loading claim data
import { loadClaimData } from '@/utils/claimDataLoader';

const claims = await loadClaimData();
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License

---

<p align="center">
  Built with ❤️ using React, TypeScript, and TailwindCSS
</p>
