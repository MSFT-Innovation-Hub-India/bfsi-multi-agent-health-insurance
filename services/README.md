# 🔧 Services Module

This module contains the service layer for the Health Insurance Fraud Detection System. Services handle agent creation, evidence collection, decision extraction, and report generation.

## 📁 Files

### `agent_factory.py`
**AutoGen Agent Factory**

Factory class for creating Microsoft AutoGen agents for fraud detection.

```python
from services.agent_factory import AgentFactory

# Initialize factory with claim data and evidence
factory = AgentFactory(claim_data, evidence)

# Create all agents
agents = factory.create_all_agents()

# Get ordered list for group chat
agent_list = factory.get_agent_list(agents)
```

**Created Agents:**
| Agent | Role |
|-------|------|
| `Fraud_Detection_Specialist` | Identity verification |
| `Medical_Consistency_Validator` | Medical validation |
| `Billing_Analysis_Validator` | Billing accuracy |
| `Policy_Balance_Validator` | Balance validation |
| `Coverage_Exclusions_Validator` | Exclusions check |
| `Fraud_Decision_Coordinator` | Final decision |
| `Claim_Processing_System` | User proxy |

### `decision_extractor.py`
**Decision Parsing from Agent Messages**

Extracts and parses the final fraud decision from agent conversation messages.

```python
from services.decision_extractor import DecisionExtractor

# Initialize extractor
extractor = DecisionExtractor(claim_data)

# Extract decision from conversation
decision = extractor.extract_decision(group_chat_messages)

# Returns FraudDecision object with:
# - decision: APPROVED/REJECTED
# - approved_amount: ₹XX,XXX
# - fraud_risk_level: HIGH/MEDIUM/LOW
# - coverage_assessment: COVERED/EXCLUDED/PARTIAL
# - exclusions_applicable: YES/NO
# - rationale: explanation
```

**Parsed Fields:**
- Final decision (APPROVED/REJECTED)
- Approved amount with deductions
- Fraud risk level
- Coverage assessment
- Balance status
- Exclusions found
- Detailed rationale

### `evidence_collector.py`
**Azure AI Evidence Collection**

Collects evidence from Azure AI Search indices for claim analysis.

```python
from services.evidence_collector import EvidenceCollector

# Initialize collector
collector = EvidenceCollector(workflow_manager)

# Collect all evidence for a claim
evidence = await collector.collect_evidence(claim_data)

# Returns dictionary with:
# - medical: Medical records
# - billing: Billing documents
# - xray: X-ray analysis results
# - policy_coverage: Policy details
# - exclusions: Exclusion information
```

**Evidence Types:**
| Type | Source |
|------|--------|
| Medical | `clm001-folder3-index` |
| Billing | `clm001-folder1-index` |
| X-ray | Azure Custom Vision |
| Policy | `clm001-folder3-index` |
| Exclusions | `claims` index |

### `report_generator.py`
**Report Generation and Printing**

Generates formatted reports and saves analysis results.

```python
from services.report_generator import ReportGenerator

# Initialize generator
reporter = ReportGenerator(claim_data)

# Print formatted results
reporter.print_results(results)

# Save to JSON file
filepath = reporter.save_report(results)
```

**Output Format:**
```
================================================================================
🏥 HEALTH INSURANCE FRAUD DETECTION REPORT
================================================================================
Claim ID: CLM001
Patient: John Doe
Claim Amount: ₹75,000.00

📊 FRAUD DECISION
Decision: APPROVED
Approved Amount: ₹72,500.00
Fraud Risk: LOW
...
================================================================================
```

### `__init__.py`
**Module Exports**

```python
from services import (
    AgentFactory,
    DecisionExtractor,
    EvidenceCollector,
    ReportGenerator
)
```

## 🔗 Usage in Orchestrator

```python
from services.agent_factory import AgentFactory
from services.decision_extractor import DecisionExtractor
from services.report_generator import ReportGenerator

# In orchestrator.py
async def _run_fraud_orchestration(self, claim_data, evidence):
    # Create agents
    factory = AgentFactory(claim_data, evidence)
    agents = factory.create_all_agents()
    
    # Run group chat...
    
    # Extract decision
    extractor = DecisionExtractor(claim_data)
    decision = extractor.extract_decision(messages)
    
    # Generate report
    reporter = ReportGenerator(claim_data)
    reporter.print_results(results)
```

## 🔗 Dependencies

- `core/` - Data models and prompts
- `autogen` - Microsoft AutoGen framework
- `workflow_manager.py` - Azure AI integration
