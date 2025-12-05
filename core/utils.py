# Utility functions for the fraud detection system

import re
from typing import List, Optional, Dict, Any


def format_currency(amount: float) -> str:
    """Format amount as Indian Rupees"""
    return f"₹{amount:,.2f}"


def calculate_utilization(previously_claimed: float, current_claim: float, coverage_limit: float) -> float:
    """Calculate policy utilization percentage"""
    if coverage_limit <= 0:
        return 0.0
    return ((previously_claimed + current_claim) / coverage_limit) * 100


def calculate_remaining_balance(available_balance: float, claim_amount: float) -> float:
    """Calculate remaining balance after claim"""
    return available_balance - claim_amount


def extract_pattern(content: str, pattern: str) -> Optional[str]:
    """Extract first match of a regex pattern from content"""
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(0) if match else None


def extract_all_amounts(content: str) -> List[str]:
    """Extract all currency amounts from content"""
    patterns = [
        r'₹[\d,]+\.?\d*',
        r'Rs\.?\s*[\d,]+\.?\d*',
        r'INR\s*[\d,]+\.?\d*'
    ]
    amounts = []
    for pattern in patterns:
        amounts.extend(re.findall(pattern, content, re.IGNORECASE))
    return amounts


def clean_amount_string(amount_str: str) -> float:
    """Convert amount string to float"""
    clean = re.sub(r'[^\d.]', '', str(amount_str))
    try:
        return float(clean)
    except ValueError:
        return 0.0


def check_keywords_in_text(text: str, keywords: List[str]) -> bool:
    """Check if any keywords exist in text"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def extract_decision_field(content: str, field_name: str, options: List[str]) -> Optional[str]:
    """Extract a decision field value from content"""
    content_upper = content.upper()
    for option in options:
        patterns = [
            f"{field_name.upper()}:** {option}",
            f"{field_name.upper()}: {option}"
        ]
        for pattern in patterns:
            if pattern in content_upper:
                return option
    return None


def get_message_content(msg: Any) -> str:
    """Extract content from various message formats"""
    if hasattr(msg, 'content') and msg.content:
        return msg.content
    elif isinstance(msg, dict):
        return msg.get('content', msg.get('message', str(msg)))
    elif isinstance(msg, str):
        return msg
    return str(msg)
