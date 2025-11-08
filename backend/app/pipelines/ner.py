import spacy
from collections import defaultdict

# ✅ Load spaCy model once
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Graceful fallback if model missing
    raise RuntimeError(
        "⚠️ spaCy model 'en_core_web_sm' not found. "
        "Run: python -m spacy download en_core_web_sm"
    )


def normalize_entity(text: str) -> str:
    """Normalize entities for deduplication & linking."""
    return text.strip().lower().replace("\n", " ").replace("\t", " ")


def extract_named_entities(text: str):
    """
    Extract PERSON / ORG / GPE / PRODUCT / EVENT entities with
    confidence & context awareness.
    Returns list of dicts: {type, value, confidence, context}
    """
    doc = nlp(text)
    raw_entities = []

    for ent in doc.ents:
        if ent.label_ in {"PERSON", "ORG", "GPE", "PRODUCT", "EVENT"}:
            # Assign confidence heuristically based on token count and capitalization
            confidence = 0.6
            if ent.label_ == "ORG" and any(t.is_upper for t in ent):
                confidence += 0.2
            if len(ent.text.split()) > 1:
                confidence += 0.1

            context_window = doc[max(0, ent.start - 5): min(len(doc), ent.end + 5)]
            context = context_window.text.strip()

            raw_entities.append({
                "type": ent.label_,
                "value": ent.text.strip(),
                "normalized": normalize_entity(ent.text),
                "confidence": round(min(confidence, 1.0), 2),
                "context": context,
            })

    # 🔁 Deduplicate based on normalized form (keep highest confidence)
    deduped = {}
    for e in raw_entities:
        key = e["normalized"]
        if key not in deduped or e["confidence"] > deduped[key]["confidence"]:
            deduped[key] = e

    return list(deduped.values())


# 🧪 Optional: Quick self-test
if __name__ == "__main__":
    sample = """
    The victim received an email from ICICI Bank Support asking to verify KYC.
    It claimed to be from Paytm Services, located in Mumbai, India.
    Contact person: Rahul Verma.
    """
    print(extract_named_entities(sample))
