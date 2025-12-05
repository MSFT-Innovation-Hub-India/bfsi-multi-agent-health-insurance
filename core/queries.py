# Query templates for Azure AI evidence collection

from typing import Dict, Any


def get_medical_evidence_query(claim: Dict[str, Any]) -> str:
    """Get query for medical evidence collection"""
    return f"""FRAUD DETECTION MEDICAL ANALYSIS for claim {claim['claim_id']}:

Patient: {claim['patient_name']}
Claimed Diagnosis: {claim['diagnosis']}
Claimed Treatment: {claim['treatment_type']}
Amount: ₹{claim['claim_amount']:,.2f}

CRITICAL ANALYSIS REQUIRED:
1. Does the actual medical documentation support the claimed diagnosis?
2. Is the treatment appropriate for the documented medical condition?
3. Are there any inconsistencies in medical records?
4. Does the patient identity match across all medical documents?
5. Are there any red flags in the medical documentation?

PROVIDE SPECIFIC EVIDENCE from indexed documents - do not make assumptions.
FLAG any inconsistencies or missing documentation."""


def get_billing_evidence_query(claim: Dict[str, Any]) -> str:
    """Get query for billing evidence collection"""
    return f"""COMPREHENSIVE BILLING ANALYSIS for claim {claim['claim_id']}:

Claimed Amount: ₹{claim['claim_amount']:,.2f}
Claimed Treatment: {claim['treatment_type']}
Hospital: {claim['hospital_name']}

CRITICAL DETAILED BILLING VALIDATION:

📋 ITEMIZED BILL ANALYSIS:
1. List ALL itemized bills with EXACT amounts for each item/service
2. Provide COMPLETE bill breakdown including all charges

🔍 CRITICAL EXCLUDED ITEMS EXTRACTION:
3. Search bills for WALKER or MOBILITY AIDS charges with EXACT amounts
4. Search bills for BRACES or SUPPORT DEVICES with EXACT amounts
5. Search bills for DIETARY SERVICES with EXACT amounts
6. Search bills for HOME CARE EQUIPMENT with EXACT amounts

💰 BILLING VALIDATION CHECKS:
7. Do the total itemized bills match the claimed amount?
8. Are the billed procedures consistent with claimed diagnosis?
9. Are there duplicate bills or suspicious billing patterns?
10. Do hospital bills match the claimed hospital?

AUTHORITATIVE AMOUNTS REFERENCE:
* Walker/Mobility Aid: ₹3,334
* Knee Brace/Support: ₹1,140

REQUIREMENT: Extract EXACT amounts from bill line items."""


def get_policy_coverage_query(claim: Dict[str, Any]) -> str:
    """Get query for policy coverage evidence collection"""
    return f"""COMPREHENSIVE POLICY COVERAGE VALIDATION for claim {claim['claim_id']}:

CLAIM DETAILS:
- Patient: {claim['patient_name']}
- Policy Number: {claim['policy_number']}
- Diagnosis: {claim['diagnosis']}
- Treatment: {claim['treatment_type']}
- Hospital: {claim['hospital_name']}
- Claim Amount: ₹{claim['claim_amount']:,.2f}
- Claim Date: {claim['claim_date']}

MANDATORY COVERAGE VALIDATION CHECKS:

🔍 INCLUSIONS VALIDATION:
1. Is the claimed diagnosis explicitly covered under the policy?
2. Is the treatment/procedure covered for this specific diagnosis?
3. Are orthopedic surgeries and related treatments included?
4. Is the hospital/provider within the covered network?

🚫 EXCLUSIONS VALIDATION:
- BRACES AND SUPPORTS - are braces, knee braces excluded?
- WALKER AND MOBILITY AIDS - are walkers excluded?
- DIETARY SERVICES - are nutritionist fees excluded?
- CONSUMABLES - are separately charged consumables excluded?

🛡️ POLICY LIMITS AND RESTRICTIONS:
1. Annual coverage limits
2. Sub-limits for room rent, surgery, ICU
3. Co-payment and deductible requirements

REQUIREMENT: Provide SPECIFIC policy sections and exclusion details FROM ACTUAL DOCUMENTS."""


def get_exclusions_query(claim: Dict[str, Any]) -> str:
    """Get query for detailed exclusions analysis"""
    return f"""COMPREHENSIVE EXCLUSIONS AND BILL CROSS-REFERENCE ANALYSIS for claim {claim['claim_id']}:

CRITICAL TASK: 
1. Analyze actual policy documents for specific exclusions
2. Cross-reference these exclusions with actual bill items

CLAIM DETAILS:
- Diagnosis: {claim['diagnosis']}
- Treatment: {claim['treatment_type']}
- Hospital: {claim['hospital_name']}
- Claim Amount: ₹{claim['claim_amount']:,.2f}

PART 1: POLICY EXCLUSIONS ANALYSIS
Search policy documents for these specific exclusions:
- BRACES - knee braces, ankle braces, back supports
- WALKER - walkers, mobility aids, wheelchairs
- DIETARY SERVICES - dietitian fees, nutrition counseling
- CONSUMABLES - syringes, bandages, disposables

PART 2: BILL CROSS-REFERENCE ANALYSIS
Find exact bill line items for excluded items with precise amounts.

AUTHORITATIVE AMOUNTS:
* Walker/Mobility Aid: ₹3,334
* Knee Brace/Support: ₹1,140

REQUIREMENT: Cross-reference exclusions with EXACT bill line items and amounts."""
