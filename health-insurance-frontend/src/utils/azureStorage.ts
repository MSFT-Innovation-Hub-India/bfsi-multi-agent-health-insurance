// Azure Storage configuration
const STORAGE_ACCOUNT_NAME = 'dataexc';
const CONTAINER_NAME = 'healthinsurance';
const BASE_URL = `https://${STORAGE_ACCOUNT_NAME}.blob.core.windows.net/${CONTAINER_NAME}`;

// For production: Generate a SAS token from Azure Portal with read permissions
// and append it to all URLs. For now, we'll use public access.
// Example SAS token format: ?sv=2021-06-08&ss=b&srt=sco&sp=r&se=2025-12-31T23:59:59Z&st=2025-01-01T00:00:00Z&spr=https&sig=...
const SAS_TOKEN = ''; // Add your SAS token here if not using public access

/**
 * Get document URL for a specific file
 * @param claimId - The claim ID (folder name in storage)
 * @param fileName - The PDF file name
 * @returns The full URL to the document
 */
export async function getDocumentUrl(claimId: string, fileName: string): Promise<string> {
  const blobUrl = `${BASE_URL}/${claimId}/${fileName}`;
  return SAS_TOKEN ? `${blobUrl}${SAS_TOKEN}` : blobUrl;
}

/**
 * List all documents for a specific claim ID
 * For browser compatibility, we'll use a predefined list
 * @param claimId - The claim ID
 * @returns Promise with array of document file names
 */
export async function listClaimDocuments(claimId: string): Promise<string[]> {
  // Since we can't list blobs from the browser without the SDK,
  // we'll return a predefined list based on claim ID
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
