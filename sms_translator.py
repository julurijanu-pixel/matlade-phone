import re
from typing import Dict, Any, List


SAMPLE_ALERTS: List[Dict[str, str]] = [
    {
        "id": "bank_debit",
        "title": "Bank Debit Alert",
        "sms": "Acct XX4821 debited for INR 1,250.00 on 27-Nov-26 at UPI/Swiggy. Avl Bal: INR 14,820.50. -HDFC Bank",
    },
    {
        "id": "bank_credit",
        "title": "Salary / Credit Alert",
        "sms": "Your A/c XX4821 is credited with Rs. 25,000.00 on 26-Nov-26 via NEFT. Total Bal is Rs. 39,820.50.",
    },
    {
        "id": "bill_due",
        "title": "Electricity Bill Reminder",
        "sms": "Reminder: Your electricity bill of INR 940.00 for consumer no 908123 is due on 30-Nov-26. Pay early to avoid late fee.",
    },
    {
        "id": "otp_alert",
        "title": "Security OTP Alert",
        "sms": "Your OTP for online payment of Rs. 650.00 is 482910. Do not share this OTP with anyone.",
    },
]


def _extract_amount(text: str) -> str:
    patterns = [
        r"(?:INR|Rs\.?|₹)\s*([0-9]+(?:,[0-9]{2,3})*(?:\.[0-9]{1,2})?)",
        r"([0-9]+(?:,[0-9]{2,3})*(?:\.[0-9]{1,2})?)\s*(?:INR|Rs\.?|₹)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _extract_balance(text: str) -> str:
    patterns = [
        r"(?:avl\.?\s*bal(?:ance)?|available\s*balance|total\s*bal(?:ance)?|bal(?:ance)?)[:\s-]*(?:INR|Rs\.?|₹)?\s*([0-9]+(?:,[0-9]{2,3})*(?:\.[0-9]{1,2})?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _extract_account(text: str) -> str:
    match = re.search(r"(?:acct|a/c|account|card)\s*(?:no\.?|num)?\s*([xX*]*\d{3,4})", text, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


def _extract_date(text: str) -> str:
    match = re.search(r"\b(\d{1,2}[-/][A-Za-z]{3,9}[-/]\d{2,4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b", text)
    if match:
        return match.group(1)
    return ""


def _extract_otp(text: str) -> str:
    match = re.search(r"\b(?:otp|code|pin)\s*(?:is|:)?\s*(\d{4,8})\b", text, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


def _detect_category(lower_text: str) -> str:
    if any(word in lower_text for word in ["otp", "one time password", "verification code", "do not share"]):
        return "otp"
    if any(word in lower_text for word in ["credited", "credit", "received", "salary", "refund", "deposited"]):
        return "credit"
    if any(word in lower_text for word in ["debited", "debit", "spent", "paid", "withdrawn", "purchase"]):
        return "debit"
    if any(word in lower_text for word in ["bill", "due", "recharge", "emi", "invoice", "overdue"]):
        return "bill"
    return "general"


def _build_telugu_message(category: str, details: Dict[str, str], raw_sms: str) -> str:
    amount = details["amount"]
    balance = details["balance"]
    account = details["account"]
    date = details["date"]
    otp = details["otp"]

    parts: List[str] = []

    if category == "debit":
        if amount:
            parts.append(f"మీ ఖాతా నుండి {amount} రూపాయలు ఖర్చు అయ్యాయి.")
        else:
            parts.append("మీ ఖాతా నుండి డబ్బు కట్ అయింది.")
    elif category == "credit":
        if amount:
            parts.append(f"మీ ఖాతాలోకి {amount} రూపాయలు జమ అయ్యాయి.")
        else:
            parts.append("మీ ఖాతాలోకి డబ్బు జమ అయింది.")
    elif category == "bill":
        if amount:
            parts.append(f"మీ బిల్లు మొత్తం {amount} రూపాయలు ఉంది.")
        else:
            parts.append("మీ బిల్లు చెల్లింపు గురించిన సందేశం వచ్చింది.")
        if date:
            parts.append(f"గడువు తేదీ {date}.")
    elif category == "otp":
        if otp:
            parts.append(f"మీ ఓటీపీ కోడ్ {otp}. దీన్ని ఎవరికీ చెప్పవద్దు.")
        else:
            parts.append("భద్రత కోసం ఓటీపీ సందేశం వచ్చింది. దీన్ని ఎవరికీ చెప్పవద్దు.")
    else:
        cleaned_snippet = re.sub(r"\s+", " ", raw_sms).strip()[:110]
        parts.append(f"కొత్త సందేశం వచ్చింది: {cleaned_snippet}")

    if account and category != "otp":
        parts.append(f"ఖాతా: {account}.")
    if balance and category in ("debit", "credit"):
        parts.append(f"మిగిలిన బ్యాలెన్స్ {balance} రూపాయలు.")
    if date and category != "bill":
        parts.append(f"తేదీ {date}.")

    return " ".join(parts).strip()


def translate_sms_to_telugu(sms_text: str, has_optional_key: bool = False) -> Dict[str, Any]:
    normalized = " ".join((sms_text or "").strip().split())
    if not normalized:
        return {
            "ok": False,
            "error": "Please enter or select an English SMS message.",
            "telugu_text": "",
            "category": "none",
            "extracted": {},
            "mode_status": "Key not set — running local rule-based Telugu mode" if not has_optional_key else "Local mode active",
        }

    category = _detect_category(normalized.lower())
    extracted = {
        "amount": _extract_amount(normalized) or "Not found",
        "balance": _extract_balance(normalized) or "Not found",
        "account": _extract_account(normalized) or "Not found",
        "date": _extract_date(normalized) or "Not found",
        "otp": _extract_otp(normalized) or "Not found",
    }

    telugu_text = _build_telugu_message(
        category=category,
        details={
            "amount": "" if extracted["amount"] == "Not found" else extracted["amount"],
            "balance": "" if extracted["balance"] == "Not found" else extracted["balance"],
            "account": "" if extracted["account"] == "Not found" else extracted["account"],
            "date": "" if extracted["date"] == "Not found" else extracted["date"],
            "otp": "" if extracted["otp"] == "Not found" else extracted["otp"],
        },
        raw_sms=normalized,
    )

    key_notice = (
        "Optional cloud key detected — local offline parser active for zero-cost reliability"
        if has_optional_key
        else "Key not set — running local rule-based Telugu mode (no API key required)"
    )

    return {
        "ok": True,
        "original_sms": normalized,
        "category": category,
        "extracted": extracted,
        "telugu_text": telugu_text,
        "mode_status": key_notice,
    }