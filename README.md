# 🏥 Health Insurance Claims - AI Fraud Detection System

A comprehensive **Multi-Agent AI-powered Health Insurance Fraud Detection and Claims Processing System** built with Microsoft AutoGen, Azure AI, and React.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-19-61DAFB.svg)
![Azure](https://img.shields.io/badge/Azure-AI%20Foundry-0078D4.svg)
![AutoGen](https://img.shields.io/badge/Microsoft-AutoGen-green.svg)

## 🌟 Features

### Backend (Python)
- **Multi-Agent Fraud Detection** using Microsoft AutoGen framework
- **Azure AI Foundry** integration for document analysis
- **X-Ray Analysis** using Azure Custom Vision (Osteoarthritis grading)
- **Policy Coverage Validation** with automatic exclusion detection
- **Real-time Claim Processing** with comprehensive reporting
- **Modular Architecture** with clean separation of concerns

### Frontend (React/TypeScript)
- **Interactive Claims Dashboard** for insurers
- **Multi-Agent Workflow Visualization**
- **Real-time Processing Simulation**
- **Document Viewer** for claim evidence

## 🤖 AI Agents

The system uses 6 specialized AI agents that collaborate via Microsoft AutoGen GroupChat:

| Agent | Role |
|-------|------|
| **Fraud Detection Specialist** | Identity verification, document authenticity |
| **Medical Validator** | Medical consistency, clinical appropriateness |
| **Billing Fraud Validator** | Billing accuracy, duplicate charge detection |
| **Policy Balance Validator** | Balance sufficiency, policy limit compliance |
| **Coverage Exclusions Validator** | Policy exclusions (walker, braces, dietary services) |
| **Fraud Decision Coordinator** | Final synthesis and decision making |

## 📁 Project Structure

```
HealthInsurance-ClaimsProcessing/
│
├── 📂 core/                    # Core business logic modules
│   ├── config.py              # LLM and system configuration
│   ├── models.py              # Data classes (ClaimData, FraudDecision, etc.)
│   ├── prompts.py             # Agent prompt templates
│   ├── queries.py             # Azure AI Search query templates
│   └── utils.py               # Utility functions
│
├── 📂 services/                # Service layer
│   ├── agent_factory.py       # AutoGen agent creation factory
│   ├── decision_extractor.py  # Decision parsing from agent messages
│   ├── evidence_collector.py  # Azure AI evidence collection
│   └── report_generator.py    # Report generation and printing
│
├── 📂 agents/                  # Specialized AI agents
│   ├── xrayanalysis.py        # X-ray classification (Azure Custom Vision)
│   ├── bill.py                # Billing analysis agent
│   ├── claim.py               # Claim processing agent
│   └── patientsummary.py      # Patient summary agent
│
├── 📂 health-insurance-frontend/  # React frontend dashboard
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── types/             # TypeScript type definitions
│   │   └── utils/             # Frontend utilities
│   └── README.md              # Frontend documentation
│
├── 🐍 orchestrator.py         # Main fraud detection orchestrator
├── 🐍 run_fraud_detection.py  # Main entry point
├── 🐍 workflow_manager.py     # Azure AI workflow orchestration
├── 🐍 main.py                 # Alternative entry point
├── 🐍 config.py               # Root configuration
│
├── 📄 requirements.txt        # Python dependencies
├── 📄 .env.example            # Environment variables template
└── 📄 autogen_config.json     # AutoGen configuration
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Azure Subscription** with the following services:
  - Azure AI Foundry
  - Azure OpenAI (GPT-4o)
  - Azure Custom Vision
  - Azure Blob Storage
  - Azure AI Search

### Installation

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/HealthInsurance-ClaimsProcessing.git
cd HealthInsurance-ClaimsProcessing
```

#### 2. Set up Python environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Configure environment variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Azure credentials
```

#### 4. Run the fraud detection system
```bash
python run_fraud_detection.py
```

#### 5. Set up the frontend (optional)
```bash
cd health-insurance-frontend
npm install
npm run dev
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Azure AI Foundry Configuration
AZURE_ENDPOINT=https://eastus2.api.azureml.ms
AZURE_RESOURCE_GROUP=your_resource_group
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_PROJECT_NAME=your_project_name

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_MODEL=gpt-4o

# Azure Custom Vision (X-ray Analysis)
CUSTOM_VISION_ENDPOINT=https://your-cv.cognitiveservices.azure.com/customvision/v3.0/Prediction
CUSTOM_VISION_PROJECT_ID=your_project_id
CUSTOM_VISION_ITERATION_NAME=Iteration4
CUSTOM_VISION_PREDICTION_KEY=your_prediction_key

# Azure Storage (for X-ray images)
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account
AZURE_STORAGE_ACCOUNT_KEY=your_storage_key
AZURE_STORAGE_CONTAINER_NAME=health-insurance
```

## 📊 How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                     1. CLAIM SUBMITTED                          │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              2. EVIDENCE COLLECTION (Azure AI)                  │
│  • Medical records from Azure AI Search                         │
│  • Billing documents from Azure AI Search                       │
│  • X-ray images from Azure Blob Storage                         │
│  • Policy coverage documents                                    │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│           3. MULTI-AGENT ANALYSIS (AutoGen GroupChat)           │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Fraud      │  │   Medical    │  │   Billing    │          │
│  │  Specialist  │  │  Validator   │  │  Validator   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Policy     │  │  Exclusions  │  │    Final     │          │
│  │  Validator   │  │  Validator   │  │ Coordinator  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      4. FINAL DECISION                          │
│  • APPROVED (with/without deductions)                           │
│  • REJECTED (fraud detected)                                    │
│  • PENDING (more information needed)                            │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    5. REPORT GENERATION                         │
│  • Detailed fraud analysis report                               │
│  • Recommendation with rationale                                │
│  • Approved amount calculation                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Technologies

| Component | Technology |
|-----------|------------|
| **AI Orchestration** | Microsoft AutoGen |
| **LLM** | Azure OpenAI (GPT-4o) |
| **Document Search** | Azure AI Search |
| **Image Analysis** | Azure Custom Vision |
| **Storage** | Azure Blob Storage |
| **Backend** | Python 3.9+ |
| **Frontend** | React 19, TypeScript, Vite |
| **Styling** | TailwindCSS |
| **Animation** | Framer Motion |

## 📝 Usage Examples

### Using the Fraud Detection Orchestrator

```python
from orchestrator import FraudDetectionOrchestrator
import asyncio

async def main():
    # Initialize the orchestrator
    orchestrator = FraudDetectionOrchestrator(
        enable_xray=True,
        enable_azure_evidence=True
    )
    
    # Process a claim
    results = await orchestrator.process_claim()
    
    # Get the decision
    decision = results['fraud_orchestration']['fraud_decision']['decision']
    print(f"Decision: {decision}")

asyncio.run(main())
```

### Using the Health Insurance Claim System

```python
from run_fraud_detection import HealthInsuranceClaimSystem
import asyncio

async def main():
    # Initialize the system
    system = HealthInsuranceClaimSystem(enable_fraud_detection=True)
    
    # Define claim data
    claim_data = {
        "claim_id": "CLM001",
        "patient_name": "John Doe",
        "policy_number": "POL123456789",
        "claim_amount": 75000.00,
        "claim_date": "2024-09-15",
        "diagnosis": "Knee Osteoarthritis",
        "treatment_type": "Total Knee Replacement",
        "hospital_name": "Apollo Hospital",
        "documents_available": ["medical_records", "x-ray", "bills"],
        "policy_coverage_limit": 500000.00,
        "available_balance": 450000.00
    }
    
    # Process the claim
    result = await system.process_claim_with_fraud_detection(claim_data)
    
    # Get summary
    print(system.get_processing_summary())

asyncio.run(main())
```

### Using the Workflow Manager

```python
from workflow_manager import HealthInsuranceWorkflowManager, ClaimData

# Initialize manager
manager = HealthInsuranceWorkflowManager()

# Create claim data
claim = ClaimData(
    claim_id="CLM001",
    patient_name="John Doe",
    policy_number="POL123456789",
    claim_amount=75000.00,
    claim_date="2024-09-15",
    diagnosis="Knee Osteoarthritis",
    treatment_type="Total Knee Replacement",
    hospital_name="Apollo Hospital",
    documents_available=["medical_records", "x-ray", "bills"]
)

# Process claim
result = manager.process_claim_with_workflow(claim)
print(f"Status: {result.final_status.value}")
print(f"Approved Amount: ₹{result.approved_amount:,.2f}")
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      orchestrator.py                            │
│                   (Main Entry Point)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────────────┐    │
│  │       core/         │    │        services/            │    │
│  │  ├── config.py      │    │  ├── agent_factory.py       │    │
│  │  ├── models.py      │    │  ├── evidence_collector.py  │    │
│  │  ├── prompts.py     │    │  ├── decision_extractor.py  │    │
│  │  ├── queries.py     │    │  └── report_generator.py    │    │
│  │  └── utils.py       │    │                             │    │
│  └─────────────────────┘    └─────────────────────────────┘    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    workflow_manager.py                          │
│                 (Azure AI Integration)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      agents/                             │   │
│  │  ├── xrayanalysis.py   (Azure Custom Vision)            │   │
│  │  ├── bill.py           (Billing Analysis)               │   │
│  │  ├── claim.py          (Claim Processing)               │   │
│  │  └── patientsummary.py (Patient Summary)                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔒 Security Notes

- ⚠️ **Never commit `.env` files** with real credentials
- 🔐 Use **Azure Key Vault** for production deployments
- 🔄 **Rotate API keys** regularly
- 🛡️ Enable **Azure AD authentication** for production
- 📋 Follow **HIPAA compliance** guidelines for health data

## 🧪 Testing

```bash
# Run the fraud detection demo
python run_fraud_detection.py

# Run with custom claim data
python -c "
from run_fraud_detection import HealthInsuranceClaimSystem
import asyncio
asyncio.run(HealthInsuranceClaimSystem().process_claim_with_fraud_detection())
"
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

<p align="center">
  Built with ❤️ using Microsoft AutoGen, Azure AI, and React
</p>
