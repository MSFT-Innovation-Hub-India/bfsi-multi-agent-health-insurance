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
├── 📄 autogen_config.json     # AutoGen configuration
├── 🐳 Dockerfile.backend      # Backend API Docker image
├── 🐳 Dockerfile.frontend     # Frontend multi-stage Docker image
├── 📄 nginx.conf              # Nginx config for frontend container
├── 📄 deploy-containerapp.ps1 # Azure Container Apps deployment (PowerShell)
└── 📄 deploy-containerapp.sh  # Azure Container Apps deployment (Bash)
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
git clone https://github.com/MSFT-Innovation-Hub-India/bfsi-multi-agent-health-insurance.git
cd bfsi-multi-agent-health-insurance
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

# Azure Storage (for X-ray images) - Using Managed Identity
AZURE_STORAGE_ACCOUNT_NAME=fsidemo
# AZURE_STORAGE_ACCOUNT_KEY not needed - using Managed Identity
AZURE_STORAGE_CONTAINER_NAME=healthinsurance
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

## ☁️ Deploying to Azure Container Apps

This project includes production-ready Docker images and deployment scripts for **Azure Container Apps** with **Managed Identity** authentication.

### Prerequisites

- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and logged in
- [Docker](https://www.docker.com/get-started) installed and running
- An **Azure Container Registry (ACR)** instance
- An **Azure Container Apps Environment**
- Azure services provisioned: Azure AI Search, Azure Cosmos DB, Azure Blob Storage, Azure OpenAI

### Docker Images

| Image | Dockerfile | Description |
|-------|-----------|-------------|
| **healthclaims-api** | `Dockerfile.backend` | Python 3.11 slim image running FastAPI with Uvicorn |
| **healthclaims-frontend** | `Dockerfile.frontend` | Multi-stage build: Node 20 builder → Nginx Alpine |

### Step-by-Step Deployment

#### 1. Configure your environment

Create a `deploy-containerapp.ps1` (Windows) or `deploy-containerapp.sh` (Linux/macOS) with your Azure resource details:

```bash
# Key variables to configure
RESOURCE_GROUP="your-resource-group"
LOCATION="eastus2"
ENVIRONMENT_NAME="your-container-apps-environment"
ACR_NAME="your-acr-name"
ACR_LOGIN_SERVER="your-acr-name.azurecr.io"
```

#### 2. Build and push Docker images

```bash
# Login to Azure Container Registry
az acr login --name $ACR_NAME

# Build and push backend
docker build -t $ACR_LOGIN_SERVER/healthclaims-api:latest -f Dockerfile.backend .
docker push $ACR_LOGIN_SERVER/healthclaims-api:latest

# Build and push frontend (pass API URL as build arg)
docker build -t $ACR_LOGIN_SERVER/healthclaims-frontend:latest -f Dockerfile.frontend \
    --build-arg VITE_API_BASE_URL="https://healthclaims-api.eastus2.azurecontainerapps.io" .
docker push $ACR_LOGIN_SERVER/healthclaims-frontend:latest
```

#### 3. Deploy the backend Container App

```bash
az containerapp create \
    --name healthclaims-api \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $ACR_LOGIN_SERVER/healthclaims-api:latest \
    --registry-server $ACR_LOGIN_SERVER \
    --target-port 8000 \
    --ingress external \
    --min-replicas 0 --max-replicas 3 \
    --cpu 0.5 --memory 1Gi \
    --system-assigned \
    --env-vars \
        AZURE_ENDPOINT="https://eastus2.api.azureml.ms" \
        COSMOS_ENDPOINT="https://your-cosmos.documents.azure.com:443/" \
        COSMOS_DATABASE="HealthInsuranceClaims" \
        COSMOS_USE_AAD="true"
```

#### 4. Assign Managed Identity roles

The backend app uses **System-Assigned Managed Identity** — no secrets or API keys needed at runtime:

```bash
# Get the principal ID of the backend app
BACKEND_PRINCIPAL_ID=$(az containerapp show \
    --name healthclaims-api --resource-group $RESOURCE_GROUP \
    --query identity.principalId --output tsv)

# Azure AI Search — read index data
az role assignment create --assignee-object-id $BACKEND_PRINCIPAL_ID \
    --assignee-principal-type ServicePrincipal \
    --role "Search Index Data Reader" \
    --scope /subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Search/searchServices/$SEARCH

# Azure Blob Storage — read claim documents & X-rays
az role assignment create --assignee-object-id $BACKEND_PRINCIPAL_ID \
    --assignee-principal-type ServicePrincipal \
    --role "Storage Blob Data Reader" \
    --scope /subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/$STORAGE

# Azure Cosmos DB — read/write claims data
az cosmosdb sql role assignment create \
    --account-name $COSMOS_ACCOUNT --resource-group $RESOURCE_GROUP \
    --principal-id $BACKEND_PRINCIPAL_ID \
    --role-definition-name "Cosmos DB Built-in Data Contributor" --scope "/"
```

#### 5. Deploy the frontend Container App

```bash
az containerapp create \
    --name healthclaims-frontend \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $ACR_LOGIN_SERVER/healthclaims-frontend:latest \
    --registry-server $ACR_LOGIN_SERVER \
    --target-port 80 \
    --ingress external \
    --min-replicas 0 --max-replicas 3 \
    --cpu 0.25 --memory 0.5Gi
```

#### 6. Verify the deployment

```bash
# Get deployed URLs
az containerapp show --name healthclaims-api --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn --output tsv

az containerapp show --name healthclaims-frontend --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn --output tsv
```

After deployment you will have:
- **Frontend**: `https://healthclaims-frontend.<region>.azurecontainerapps.io`
- **Backend API**: `https://healthclaims-api.<region>.azurecontainerapps.io`
- **API Docs (Swagger)**: `https://healthclaims-api.<region>.azurecontainerapps.io/docs`

## � Azure AI Search Index Setup

Before running the system, three Azure AI Search indexes must be created — one for each document category:

| Index | Blob Folder |
|---|---|
| Bills Index | `CUST{id}/bills/` |
| Claims / Exclusions / Inclusions Index | `CUST{id}/claims-exclusions-inclusions/` |
| Diagnostic Data Index | `CUST{id}/diagnostic-data/` |

### Option A — Python Script (recommended)

Configure `.env` and run the script for each index:

```bash
cd Index-Creation
cp .env.template .env   # fill in your Azure credentials
python create_index.py  # interactive mode
```

See [`Index-Creation/README.md`](Index-Creation/README.md) for full setup instructions.

### Option B — Azure Portal

Use the **Import and vectorize data** wizard in Azure AI Search, pointing to the corresponding Blob folder for each index.

See [`index-creation-portal/index_setup-portal.md`](index-creation-portal/index_setup-portal.md) for step-by-step guidance.

---

## �🔧 Technologies

| Component | Technology |
|-----------|------------|
| **AI Orchestration** | Microsoft AutoGen |
| **LLM** | Azure OpenAI (GPT-4o) |
| **Document Search** | Azure AI Search |
| **Image Analysis** | Azure Custom Vision |
| **Storage** | Azure Blob Storage |
| **Hosting** | Azure Container Apps |
| **Containers** | Docker (multi-stage builds) |
| **Identity** | Azure Managed Identity (passwordless) |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Frontend** | React 19, TypeScript, Vite |
| **Styling** | TailwindCSS |
| **Animation** | Framer Motion |


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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.

<p align="center">
  Built with ❤️ using Microsoft AutoGen, Azure AI, and React
</p>
