# 🤖 Agents Module

This module contains specialized AI agents for the Health Insurance Fraud Detection System. These agents interact with Azure AI services for document analysis and X-ray classification.

## 📁 Files

### `xrayanalysis.py`
**X-Ray Classification using Azure Custom Vision**

The main agent for analyzing knee X-ray images to detect osteoarthritis severity.

```python
from agents.xrayanalysis import XRayPredictionAPI

# Initialize the API
api = XRayPredictionAPI()

# Predict all images from Azure Storage
results = api.predict_all_images()

# Predict from a specific URL
result = api.predict_from_url("https://...")

# Predict from local file
result = api.predict_from_file("path/to/xray.jpg")

# Predict from Azure Blob
result = api.predict_from_blob("CLM001/xray/image.jpg")
```

**Osteoarthritis Grading:**
| Grade | Description |
|-------|-------------|
| **Grade 0** | Healthy knee - No signs of osteoarthritis |
| **Grade 1** | Doubtful joint narrowing with possible osteophytic lipping |
| **Grade 2** | Definite osteophytes and possible joint space narrowing |
| **Grade 3** | Multiple osteophytes, definite joint narrowing, mild sclerosis |
| **Grade 4** | Large osteophytes, significant narrowing, severe sclerosis |

**Fraud Detection Use Case:**
```python
# Detect mismatch between claimed diagnosis and X-ray
if "brain surgery" in claimed_diagnosis and "osteoarthritis" in xray_grade:
    fraud_flag = "CRITICAL: Brain surgery claimed but knee X-ray found"
```

**Configuration (Environment Variables):**
```env
CUSTOM_VISION_ENDPOINT=https://your-cv.cognitiveservices.azure.com/customvision/v3.0/Prediction
CUSTOM_VISION_PROJECT_ID=your_project_id
CUSTOM_VISION_ITERATION_NAME=Iteration4
CUSTOM_VISION_PREDICTION_KEY=your_prediction_key
AZURE_STORAGE_ACCOUNT_NAME=fsidemo
# AZURE_STORAGE_ACCOUNT_KEY not needed - using Managed Identity
AZURE_STORAGE_CONTAINER_NAME=healthinsurance
AZURE_STORAGE_XRAY_PATH=CLM001/xray
```

### `bill.py`
**Billing Analysis Agent**

Agent for analyzing medical bills and detecting billing irregularities.

**Features:**
- Itemized bill verification
- Duplicate charge detection
- Price inflation detection
- Hospital consistency check
- Billing timeline validation

### `claim.py`
**Claim Processing Agent**

Agent for processing claim information and validation.

**Features:**
- Claim data validation
- Document completeness check
- Policy verification
- Claim amount calculation

### `patientsummary.py`
**Patient Summary Agent**

Agent for generating patient summaries and medical history analysis.

**Features:**
- Patient history compilation
- Treatment timeline generation
- Medical record summarization
- Pre-existing condition identification

## 🎯 Centralized Instructions

All agent instructions are centralized in `core/instructions.py` for maintainability. Agents import their instructions from this single source of truth:

```python
# In each agent file
from core.instructions import AZURE_AGENT_INSTRUCTIONS, SEARCH_FIELD_MAPPINGS

# Using instructions
instruction = AZURE_AGENT_INSTRUCTIONS["billing_specialist"]
instruction = AZURE_AGENT_INSTRUCTIONS["medical_specialist"]
instruction = AZURE_AGENT_INSTRUCTIONS["exclusions_specialist"]
instruction = AZURE_AGENT_INSTRUCTIONS["claim_coordinator"]
```

**Benefits:**
- ✅ Single source of truth for all agent instructions
- ✅ Easy to update instructions across all agents
- ✅ Consistent behavior across the system
- ✅ Better maintainability and code organization

## 🔗 Usage in Workflow Manager

```python
from agents.xrayanalysis import XRayPredictionAPI

# In workflow_manager.py
def _run_xray_analysis(self, claim_data):
    xray_results = self.xray_api.predict_all_images()
    analysis = self._format_xray_analysis(xray_results)
    return AgentResult(
        agent_name="X-ray Analysis Specialist",
        analysis=analysis,
        # ...
    )
```

## 🔗 Usage in Orchestrator

```python
from agents.xrayanalysis import XRayAPI

# In orchestrator.py
async def _collect_xray_evidence(self, claim_data):
    xray_results = self.xray_api.predict_all_images()
    analysis = self._analyze_xray_for_fraud(xray_results, claim_data)
    return analysis
```

## 🔧 Azure Custom Vision Setup

1. Create a Custom Vision project in Azure
2. Train the model with knee X-ray images labeled by grade
3. Publish the iteration
4. Copy the prediction endpoint and key to `.env`

## 📊 Output Format

```python
{
    "success": True,
    "total_images": 3,
    "successful_predictions": 3,
    "results": [
        {
            "success": True,
            "source": "Azure Blob: CLM001/xray/left_knee.jpg",
            "top_prediction": {
                "tag_name": "Grade 3",
                "probability": 0.92,
                "confidence_percentage": "92.00%",
                "description": "Multiple osteophytes, definite joint space narrowing, with mild sclerosis"
            },
            "all_predictions": [...]
        }
    ]
}
```

## 🔗 Dependencies

- `azure-storage-blob` - Azure Blob Storage access
- `requests` - HTTP requests to Custom Vision API
- `python-dotenv` - Environment variable management
