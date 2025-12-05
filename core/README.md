# 📦 Core Module

This module contains the core business logic, data models, and configuration for the Health Insurance Fraud Detection System.

## 📁 Files

### `instructions.py` ⭐ NEW
**Centralized Agent Instructions (Single Source of Truth)**

Contains ALL agent instructions in one place for maintainability:

| Constant | Description |
|----------|-------------|
| `AZURE_AGENT_INSTRUCTIONS` | Dictionary of Azure AI agent instructions |
| `SEARCH_FIELD_MAPPINGS` | Azure AI Search field mappings |
| `XRAY_GRADE_DESCRIPTIONS` | X-ray osteoarthritis grade descriptions |

**Prompt Functions:**
| Function | Agent |
|----------|-------|
| `get_fraud_specialist_prompt()` | Identity & document verification |
| `get_medical_validator_prompt()` | Medical consistency validation |
| `get_billing_validator_prompt()` | Billing accuracy validation |
| `get_policy_balance_validator_prompt()` | Policy limit compliance |
| `get_coverage_exclusions_validator_prompt()` | Exclusions detection |
| `get_fraud_coordinator_prompt()` | Final decision synthesis |

**Helper Functions:**
| Function | Purpose |
|----------|---------|
| `get_azure_agent_instruction()` | Get instruction by agent type |
| `get_xray_grade_description()` | Get grade description by grade name |

```python
from core.instructions import (
    AZURE_AGENT_INSTRUCTIONS,
    SEARCH_FIELD_MAPPINGS,
    get_fraud_specialist_prompt
)

# Get billing specialist instruction
instruction = AZURE_AGENT_INSTRUCTIONS["billing_specialist"]

# Get X-ray prompt with evidence
prompt = get_fraud_specialist_prompt(
    medical_evidence="...",
    billing_evidence="...",
    xray_evidence="..."
)
```

### `config.py`
**LLM and System Configuration**

Contains configuration settings for:
- Azure OpenAI LLM settings (model, temperature, tokens)
- Default claim data for testing
- System-wide configuration parameters

```python
from core.config import get_llm_config, get_default_claim_data

# Get LLM configuration for AutoGen agents
llm_config = get_llm_config()

# Get sample claim data for testing
claim_data = get_default_claim_data()
```

### `models.py`
**Data Classes and Enums**

Defines the data structures used throughout the system:

| Class | Description |
|-------|-------------|
| `ClaimStatus` | Enum for claim processing states (INITIATED, APPROVED, REJECTED, etc.) |
| `ClaimData` | Main claim information dataclass |
| `FraudIndicator` | Represents a detected fraud indicator |
| `ClaimValidationResult` | Result of claim validation |
| `AgentResult` | Result from an individual agent |
| `WorkflowResult` | Complete workflow processing result |
| `FraudDecision` | Final fraud detection decision |

```python
from core.models import ClaimData, FraudDecision, ClaimStatus

# Create a claim
claim = ClaimData(
    claim_id="CLM001",
    patient_name="John Doe",
    claim_amount=75000.00,
    # ... other fields
)
```

### `prompts.py`
**Agent Prompt Templates (Re-exports from instructions.py)**

Re-exports prompts from `instructions.py` for backward compatibility:

```python
from core.prompts import get_fraud_specialist_prompt

prompt = get_fraud_specialist_prompt(
    medical_evidence="...",
    billing_evidence="...",
    xray_evidence="..."
)
```

### `queries.py`
**Azure AI Search Query Templates**

Query templates for retrieving evidence from Azure AI Search indices:

| Function | Purpose |
|----------|---------|
| `get_medical_evidence_query()` | Query for medical records |
| `get_billing_evidence_query()` | Query for billing documents |
| `get_policy_coverage_query()` | Query for policy coverage |
| `get_exclusions_query()` | Query for policy exclusions |

```python
from core.queries import get_medical_evidence_query

query = get_medical_evidence_query(claim_data)
```

### `utils.py`
**Utility Functions**

Helper functions used across the system:

| Function | Purpose |
|----------|---------|
| `get_message_content()` | Extract content from agent messages |
| `format_currency()` | Format amounts in Indian Rupees |
| `parse_decision()` | Parse decision from text |

```python
from core.utils import get_message_content

content = get_message_content(message)
```

### `__init__.py`
**Module Exports**

Exports all public classes and functions for easy importing:

```python
from core import ClaimData, FraudDecision, get_llm_config
```

## 🔗 Dependencies

This module is used by:
- `orchestrator.py` - Main fraud detection orchestrator
- `workflow_manager.py` - Azure workflow orchestration
- `agents/*.py` - All specialized agents
- `services/agent_factory.py` - Agent creation
- `services/decision_extractor.py` - Decision parsing
- `services/report_generator.py` - Report generation
