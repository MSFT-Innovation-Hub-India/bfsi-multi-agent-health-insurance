# Azure AI Search Index Creation — Portal Guide

## Overview

This guide explains how to create Azure AI Search indexes using the Azure Portal for a Health Insurance document processing solution.

### Integrated Services

- **Azure AI Search** — Core search and indexing engine
- **Azure Blob Storage** — Document source for indexing
- **Azure OpenAI** — Embedding model for semantic search
- **Azure AI Multi-Service Account** — Enrichment and AI capabilities

### Indexes to Create

Three separate indexes are required for this solution. The index creation process must be repeated for each:

| Index | Purpose |
|---|---|
| **Bills Index** | Bills, invoices, and payment records |
| **Claims / Exclusions / Inclusions Index** | Policy claims, exclusions, and inclusions |
| **Diagnostic Data Index** | Diagnostic reports and medical test results |

> **Prerequisites:** Blob Storage must be configured correctly before creating any index.

---

## Step 1 — Configure Blob Storage Structure

Each patient/customer must have a dedicated folder containing three subdirectories.

### Required Folder Structure

```
<person-folder>/
│
├── bills/
├── claims-exclusions-inclusions/
└── diagnostic-data/
```

### Directory Descriptions

| Directory | Contents |
|---|---|
| `bills/` | Bills, invoices, and payment records |
| `claims-exclusions-inclusions/` | Claims documents, policy exclusions, policy inclusions, and insurance policy data |
| `diagnostic-data/` | Diagnostic reports, medical test results, and analysis documents |

---

## Step 2 — Create the Azure AI Search Resource

1. Open the [Azure Portal](https://portal.azure.com).
2. Create a new **Azure AI Search** resource and wait for deployment to complete.
3. Once deployed, navigate to the resource **Overview** page.
4. Click **Import and vectorize data**.

---

## Step 3 — Configure the Data Source

1. On the import wizard, select **Azure Blob Storage** as the data source.


---

## Step 4 — Configure type (Optional)

1. When prompted, select **RAG** as the import mode.
after that
2. Fill in the following details:

   - **Subscription** — Your Azure subscription
   - **Storage Account** — The account containing your documents
   - **Blob Container / Blob Folder** — Point to the specific folder for the index being created (e.g., `bills/`)

---

## Step 5 — Configure Azure OpenAI Embeddings

1. Select your **Azure OpenAI** account.
2. Choose the desired embedding model deployment (e.g., `text-embedding-ada-002` or any supported model).

> **Notes:**
> - Any supported embedding model can be used.
> - Use the **same embedding model** consistently across all three indexes and all environments.
> - API key authentication can be used if required.

---

## Step 6 — Configure the Search Index

Leave the index configuration at its default settings unless specific field customization is required.

---

## Step 7 — Review and Create

1. Review all configuration settings.
2. Click **Create**.

The wizard will automatically:
- Connect to Blob Storage
- Process and parse the source documents
- Generate vector embeddings via Azure OpenAI
- Create and populate the Azure AI Search index

---

> **Reminder:** Repeat Steps 2–7 for each of the three indexes, pointing to the corresponding Blob folder (`bills/`, `claims-exclusions-inclusions/`, `diagnostic-data/`) each time.
