# Azure AI Search Index Creation — Python Script

## Overview

This script (`create_index.py`) automates the creation of Azure AI Search indexes for the Health Insurance Claims Processing solution. It replaces the manual portal-based workflow by programmatically:

1. Reading patient/customer documents from Azure Blob Storage
2. Extracting text using **Azure Document Intelligence** (prebuilt layout model)
3. Chunking and generating vector embeddings via **Azure OpenAI**
4. Uploading indexed, searchable chunks to **Azure AI Search**

### Required Azure Services

| Service | Purpose |
|---|---|
| **Azure Blob Storage** | Source document storage |
| **Azure Document Intelligence** | OCR and text extraction from documents |
| **Azure OpenAI** | Generating vector embeddings |
| **Azure AI Search** | Storing and querying the search index |

---

## Blob Storage Structure

Documents must be organized in the following folder structure inside your Blob container. The script only processes paths matching `CUST{id}/{document_type}/` — other folders are ignored.

```
<container>/
├── CUST0001/
│   ├── bills/
│   ├── claims-exclusions-inclusions/
│   └── diagnostic-data/
├── CUST0002/
│   ├── bills/
│   ├── claims-exclusions-inclusions/
│   └── diagnostic-data/
└── ...
```

### Index-to-Folder Mapping

Each of the three required indexes maps to a specific document type folder:

| Index | Blob Folder | Contents |
|---|---|---|
| **Bills Index** | `bills/` | Bills, invoices, payment records |
| **Claims Index** | `claims-exclusions-inclusions/` | Policy claims, exclusions, inclusions |
| **Diagnostic Index** | `diagnostic-data/` | Diagnostic reports, medical test results |

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:

```
azure-storage-blob
azure-ai-documentintelligence
azure-search-documents
openai
numpy
python-dotenv
```

### 2. Configure Environment Variables

Copy the template and fill in your Azure credentials:

```bash
cp .env.template .env
```

Edit `.env` with the following variables:

```env
# Azure Blob Storage
STORAGE_ACCOUNT_NAME=your-storage-account-name
STORAGE_ACCOUNT_KEY=your-storage-account-key
CONTAINER_NAME=your-blob-container-name

# Azure Document Intelligence
DOC_INTEL_ENDPOINT=https://your-doc-intel-resource.cognitiveservices.azure.com/
DOC_INTEL_KEY=your-document-intelligence-key

# Azure OpenAI
OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
OPENAI_SUBSCRIPTION_KEY=your-openai-api-key
OPENAI_API_VERSION=2024-02-01
OPENAI_DEPLOYMENT_NAME=your-chat-deployment-name
EMBEDDING_MODEL_NAME=text-embedding-ada-002

# Azure AI Search
SEARCH_SERVICE_ENDPOINT=https://your-search-service.search.windows.net
SEARCH_SERVICE_KEY=your-search-admin-key
SEARCH_INDEX_NAME=bills-index
```

> **Note:** `EMBEDDING_MODEL_NAME` should match the deployment name of your embedding model in Azure OpenAI. Use the same model consistently across all three indexes.

---

## Running the Script

The script supports two execution modes.

### Interactive Mode

Run without arguments to get a guided prompt:

```bash
python create_index.py
```

The script will:
1. Scan the container and display all detected customers and document types
2. Ask you to choose between processing a specific customer or all customers
3. Prompt for the customer ID and document type if needed

**Sample interaction:**

```
Choose processing mode:
1. Process specific customer and document type
2. Process all customer documents
Enter choice (1 or 2): 1

Customer ID (e.g., CUST0001): CUST0001
Document Type (e.g., bills): bills
```

### Command-Line Mode

Pass the customer ID and document type directly as arguments:

```bash
python create_index.py CUST0001 bills
```

To process all customers at once, use the interactive mode and select option `2`.

---

## Creating All Three Indexes

Since each index targets a different document type, you must run the script three times — once per index. Update `SEARCH_INDEX_NAME` in your `.env` file before each run.

### Step-by-Step

**1. Bills Index**

```env
SEARCH_INDEX_NAME=bills-index
```
```bash
python create_index.py CUST0001 bills
```

**2. Claims / Exclusions / Inclusions Index**

```env
SEARCH_INDEX_NAME=claims-index
```
```bash
python create_index.py CUST0001 claims-exclusions-inclusions
```

**3. Diagnostic Data Index**

```env
SEARCH_INDEX_NAME=diagnostic-index
```
```bash
python create_index.py CUST0001 diagnostic-data
```

> To index all customers in one run, use interactive mode (option `2`) — it processes all `CUST*/` folders in the container for the configured `SEARCH_INDEX_NAME`.

---

## Index Schema

Each index created by the script contains the following fields:

| Field | Type | Description |
|---|---|---|
| `id` | String (key) | Unique chunk identifier |
| `content` | String (searchable) | Extracted and chunked document text |
| `file_name` | String (filterable) | Original blob file path |
| `customer_id` | String (filterable) | Customer folder ID (e.g., `CUST0001`) |
| `document_type` | String (filterable) | Document category (e.g., `bills`) |
| `embedding_str` | String | Serialized vector embedding |

> If an index with the same name already exists, the script will delete and recreate it automatically.

---

## How It Works

```
Blob Storage
    │
    ▼
Azure Document Intelligence  ← Extracts text (prebuilt-layout model)
    │
    ▼
Text Chunker                 ← Splits text into ~500-token chunks
    │
    ▼
Azure OpenAI Embeddings      ← Generates a vector per chunk
    │
    ▼
Azure AI Search              ← Uploads documents with embeddings
```

Each chunk is tagged with the customer ID and document type for filtered retrieval:

```
[CUST0001/bills] invoice_march.pdf
<extracted text chunk>
```

---

## Troubleshooting

| Issue | Likely Cause | Fix |
|---|---|---|
| `Missing required environment variables` | `.env` not configured | Copy `.env.template` to `.env` and fill all values |
| `No customer documents found` | Wrong container or folder structure | Verify blobs follow `CUST{id}/{type}/file` structure |
| `No text extracted` | Unsupported or empty file | Ensure files are readable PDFs, images, or documents |
| `Upload failed` | Search service key/endpoint mismatch | Verify `SEARCH_SERVICE_ENDPOINT` and `SEARCH_SERVICE_KEY` |
| `Error analyzing document` | Doc Intelligence quota or key issue | Check `DOC_INTEL_ENDPOINT` and `DOC_INTEL_KEY` |
