# PDF Document Viewer Feature

## Overview
The Health Insurance Claims Dashboard now includes a PDF document viewer that allows users to view claim-related documents directly from Azure Blob Storage.

## Azure Storage Configuration

**Storage Account:** `fsidemo`
**Container:** `healthinsurance`
**Structure:** `/{claimId}/{filename}.pdf`

Example:
- `CLM001-2024-LAKSHMI/medical_records.pdf`
- `CLM001-2024-LAKSHMI/xray_results.pdf`

## Features

### 1. **View Documents Button (Eye Icon)**
- Available in **Claimant** tab (PatientSummary component)
- Available in **Claims Analysis** tab (ClaimAnalysis component)
- Click the Eye icon (👁️) or "View Docs" button to open the document viewer

### 2. **Document Viewer Modal**
- **Sidebar Navigation:** Shows all available documents for the claim
- **PDF Viewer:** Displays PDFs using browser's built-in viewer
- **Download:** One-click download for any document
- **Loading States:** Shows spinner while fetching documents
- **Error Handling:** Displays helpful error messages if documents can't be loaded

### 3. **Security**
- Uses SAS (Shared Access Signature) tokens for secure access
- Tokens are valid for 1 hour
- Read-only permissions

## Components Added

### `/src/utils/azureStorage.ts`
Utility functions for Azure Blob Storage:
- `getDocumentUrl(claimId, fileName)` - Generate SAS token URL for a document
- `listClaimDocuments(claimId)` - List all documents for a claim
- `getAllDocumentUrls(claimId)` - Get URLs for all documents
- `downloadDocument(claimId, fileName)` - Download a document

### `/src/components/DocumentViewer.tsx`
Modal component for viewing PDFs:
- Responsive layout with document list sidebar
- PDF iframe viewer
- Download functionality
- Loading and error states

## Usage

### Upload Documents to Azure Storage
Documents should be organized by claim ID:

```
Container: healthinsurance
├── CLM001-2024-LAKSHMI/
│   ├── medical_records.pdf
│   ├── xray_results.pdf
│   └── discharge_summary.pdf
└── CLM010-2025-AHSAN/
    ├── medical_records.pdf
    └── bills.pdf
```

### Access from Dashboard
1. Navigate to **Claimant** or **Claims Analysis** tab
2. Click the **Eye icon** (👁️) or **"View Docs"** button next to any claim
3. Browse and view documents in the modal
4. Download documents as needed

## Document Type Detection
The system automatically categorizes documents based on filename:
- `medical` or `record` → Medical Records
- `xray` or `x-ray` → X-Ray
- `bill` or `invoice` → Bills
- `discharge` → Discharge Summary
- `prescription` → Prescription
- `lab` → Lab Reports

## Dependencies
- `@azure/storage-blob` - Azure Storage SDK for JavaScript

## Environment Configuration
Credentials are currently hardcoded in `azureStorage.ts`. For production, move these to environment variables:

```env
VITE_AZURE_STORAGE_ACCOUNT=fsidemo
VITE_AZURE_STORAGE_KEY=  # Not needed with Managed Identity or public access
VITE_AZURE_STORAGE_CONTAINER=healthinsurance
```

## Browser Compatibility
- Works with all modern browsers that support PDF viewing
- Requires JavaScript enabled
- Best viewed on desktop/tablet (responsive on mobile)
