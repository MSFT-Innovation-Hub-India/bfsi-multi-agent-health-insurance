// Azure Storage - proxied through backend API (AAD auth)
// The backend fetches blobs using DefaultAzureCredential since
// the storage account has public access and SAS disabled.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Get document URL routed through the backend proxy
 * @param claimId - The claim ID (folder name in storage)
 * @param fileName - The file name
 * @returns The proxy URL
 */
export async function getDocumentUrl(claimId: string, fileName: string): Promise<string> {
  return `${API_BASE_URL}/api/documents/${encodeURIComponent(claimId)}/${encodeURIComponent(fileName)}`;
}

/**
 * List all documents for a specific claim ID from the backend
 * @param claimId - The claim ID
 * @returns Promise with array of document file names
 */
export async function listClaimDocuments(claimId: string): Promise<string[]> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/documents/${encodeURIComponent(claimId)}`,
      { signal: AbortSignal.timeout(5000) }
    );
    if (response.ok) {
      const data = await response.json();
      return data.documents || [];
    }
  } catch {
    console.warn(`Failed to list documents for ${claimId} from API, using fallback`);
  }

  // Fallback: hardcoded list
  const documentMap: { [key: string]: string[] } = {
    'CLM001-2024-LAKSHMI': [
      'Bill-Blood-Bank-1 1.pdf',
      'Discharge-Summary.pdf',
      'Investigation-Surgery_compressed.pdf',
      'kneexray aftersurgery.jpg',
      'kneexray beforesurgery.jpg'
    ],
    'CLM010-2025-AHSAN': [
      'Bill-Blood-Bank-1 1.pdf',
      'Discharge-Summary_compressed.pdf'
    ]
  };

  return documentMap[claimId] || [];
}

/**
 * Get all document URLs for a claim
 * @param claimId - The claim ID
 * @returns Promise with array of objects containing filename and URL
 */
export async function getAllDocumentUrls(claimId: string): Promise<Array<{ fileName: string; url: string; type: string }>> {
  try {
    const fileNames = await listClaimDocuments(claimId);
    const documents = await Promise.all(
      fileNames.map(async (fileName) => {
        const url = await getDocumentUrl(claimId, fileName);
        return {
          fileName,
          url,
          type: getDocumentType(fileName),
        };
      })
    );
    return documents;
  } catch (error) {
    console.error('Error getting all document URLs:', error);
    throw error;
  }
}

/**
 * Determine document type from filename
 */
function getDocumentType(fileName: string): string {
  const name = fileName.toLowerCase();
  if (name.includes('medical') || name.includes('record')) return 'Medical Records';
  if (name.includes('xray') || name.includes('x-ray')) return 'X-Ray';
  if (name.includes('bill') || name.includes('invoice')) return 'Bills';
  if (name.includes('discharge')) return 'Discharge Summary';
  if (name.includes('prescription')) return 'Prescription';
  if (name.includes('lab')) return 'Lab Reports';
  return 'Document';
}

/**
 * Download a document
 * @param claimId - The claim ID
 * @param fileName - The file name
 */
export async function downloadDocument(claimId: string, fileName: string): Promise<void> {
  try {
    const url = await getDocumentUrl(claimId, fileName);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('Error downloading document:', error);
    throw error;
  }
}
