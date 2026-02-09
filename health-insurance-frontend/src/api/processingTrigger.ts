/**
 * Processing Trigger - Fire and Forget API calls
 * Triggers the backend processing API without waiting for response
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Trigger processing for a claim (fire and forget)
 * This sends a request to the backend but doesn't wait for a response
 * The frontend continues to use static JSON data for display
 */
export function triggerProcessing(claimId: string): void {
  // Fire and forget - don't await, don't handle response
  fetch(`${API_BASE_URL}/api/process/${encodeURIComponent(claimId)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((response) => {
      if (response.ok) {
        console.log(`✅ Processing triggered for claim: ${claimId}`);
      } else {
        console.log(`⚠️ Processing trigger returned status: ${response.status}`);
      }
    })
    .catch((error) => {
      // Silently fail - this is fire and forget
      console.log(`ℹ️ Processing API not available (fire and forget): ${error.message}`);
    });
}

/**
 * Trigger claim creation/update in Cosmos DB (fire and forget)
 */
export function triggerClaimSave(claimData: {
  claim_id: string;
  patient_name: string;
  claim_amount: number;
  diagnosis: string;
  [key: string]: unknown;
}): void {
  fetch(`${API_BASE_URL}/api/claims`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(claimData),
  })
    .then((response) => {
      if (response.ok) {
        console.log(`✅ Claim saved to Cosmos DB: ${claimData.claim_id}`);
      }
    })
    .catch((error) => {
      console.log(`ℹ️ Claim save API not available: ${error.message}`);
    });
}

/**
 * Check if API is available (useful for debugging)
 */
export async function isApiAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(2000), // 2 second timeout
    });
    return response.ok;
  } catch {
    return false;
  }
}
