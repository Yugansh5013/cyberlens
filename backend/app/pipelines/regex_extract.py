import re

patterns = {
    "phone": r"\b(?:\+91[\s\-]?)?[6-9]\d{9}\b",
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "url": r"https?://[^\s]+",
    "upi": r"[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}"
}

def extract_entities(text: str):
    results = []
    for entity_type, pattern in patterns.items():
        matches = re.findall(pattern, text)
        for m in matches:
            results.append({"type": entity_type, "value": m})
    return results
