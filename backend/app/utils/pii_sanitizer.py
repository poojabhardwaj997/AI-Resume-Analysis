import re
from typing import Any, Dict


def mask_email(email: str) -> str:
    """
    Masks an email address for safe logging and display.
    Example: 'vikram.patel@example.com' -> 'v***l@example.com'
    """
    if not email or "@" not in email:
        return email or ""
    
    parts = email.split("@", 1)
    user_part, domain_part = parts[0], parts[1]
    
    if len(user_part) <= 2:
        masked_user = user_part[0] + "***"
    else:
        masked_user = user_part[0] + "***" + user_part[-1]
        
    return f"{masked_user}@{domain_part}"


def mask_phone(phone: str) -> str:
    """
    Masks a phone number, preserving the last 4 digits.
    Example: '+1-555-234-5678' -> '***-***-5678'
    """
    if not phone:
        return ""
    
    # Strip whitespace and dashes to get raw digits
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 4:
        return "****"
    
    last_four = digits[-4:]
    return f"***-***-{last_four}"


def sanitize_profile_for_logs(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produces a shallow copy of candidate profile with PII fields masked
    so it can be safely emitted to server stdout or monitoring logs.
    """
    if not isinstance(profile, dict):
        return {}
    
    safe_profile = dict(profile)
    if "email" in safe_profile and safe_profile["email"]:
        safe_profile["email"] = mask_email(str(safe_profile["email"]))
        
    if "phone" in safe_profile and safe_profile["phone"]:
        safe_profile["phone"] = mask_phone(str(safe_profile["phone"]))
        
    return safe_profile


def redact_sensitive_text(text: str) -> str:
    """
    Redacts obvious email addresses and phone numbers from raw strings
    to prevent accidental PII leakage in debug traces.
    """
    if not text:
        return ""
    
    # Redact email addresses
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    text = re.sub(email_pattern, "[REDACTED_EMAIL]", text)
    
    # Redact standard 10-12 digit phone numbers
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    text = re.sub(phone_pattern, "[REDACTED_PHONE]", text)
    
    return text
