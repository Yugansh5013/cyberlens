import re

# 🔍 Comprehensive regex patterns
PATTERNS = {
    "phone": r"\b(?:\+91[\s\-]?)?(?<!\d)(?:[6-9]\d{9})(?!\d)\b",
    "email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b",
    "url": r"https?://[^\s<>()\"']+",
    "upi": r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b",
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "ifsc": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    "pan": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
    "crypto_wallet": r"\b(?:0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b",
    "invoice_id": r"\bINV[-_]?\d{5,10}\b",
    "qr_placeholder": r"QR\s?Code|Scan\s?(?:Here|Now|to\s?Pay)",
    "domain": r"\b[a-zA-Z0-9.-]+\.(?:com|in|net|org|xyz|shop|co|io|gov|edu)\b",
}

# 💡 Keyword-based hints for scam detection context (optional)
SCAM_KEYWORDS = [
    "kyc", "verify", "account", "update", "bank", "payment", "lottery",
    "offer", "cashback", "refund", "prize", "winner", "secure", "otp",
    "support", "login", "credentials", "reward", "paytm", "upi"
]


def _confidence_boost(entity_type: str, value: str) -> float:
    """Assign confidence heuristically based on pattern reliability."""
    base = {
        "email": 0.9,
        "url": 0.85,
        "upi": 0.88,
        "phone": 0.75,
        "ip": 0.8,
        "domain": 0.8,
        "ifsc": 0.95,
        "crypto_wallet": 0.7,
        "invoice_id": 0.6,
        "pan": 0.9,
        "qr_placeholder": 0.5,
    }.get(entity_type, 0.5)

    # Small confidence boosts for scam-like words near entities
    if any(k in value.lower() for k in SCAM_KEYWORDS):
        base += 0.1

    return round(min(base, 1.0), 2)


def _normalize_value(value: str) -> str:
    """Clean up extracted values for consistency."""
    return value.strip().strip(".,;:").replace("\n", " ")


def extract_entities(text: str):
    """
    Extract multiple types of entities from raw text using regex patterns.
    Returns list of {type, value, confidence, context_snippet}
    """
    entities = []
    lowered = text.lower()

    for entity_type, pattern in PATTERNS.items():
        matches = list(re.finditer(pattern, text))
        for m in matches:
            val = _normalize_value(m.group())
            conf = _confidence_boost(entity_type, val)
            start, end = m.start(), m.end()

            # Extract surrounding context (useful for OSINT + Risk)
            context = text[max(0, start - 40): min(len(text), end + 40)]

            entities.append({
                "type": entity_type,
                "value": val,
                "confidence": conf,
                "context": context.strip(),
            })

    # Deduplicate by (type, value)
    seen = set()
    unique_entities = []
    for e in entities:
        key = (e["type"], e["value"].lower())
        if key not in seen:
            seen.add(key)
            unique_entities.append(e)

    return unique_entities


# 🧪 Optional quick test
if __name__ == "__main__":
    sample = """
    Contact our KYC team at support@icicibank-verify.com or call +919876543210.
    Pay using UPI: fraudpayment@upi or visit https://fakebank.xyz/secure.
    IFSC: HDFC0001234 | PAN: ABCDE1234F | Invoice INV_90345
    Crypto: 0x1a2b3c4d5e6f7890123456789abcdef987654321
    """
    from pprint import pprint
    pprint(extract_entities(sample))
