import re
import numpy as np
from textblob import TextBlob
from datetime import datetime

# -----------------------------------
# Entity-level Risk Analyzer
# -----------------------------------

def domain_from_email(email):
    match = re.search(r'@([\w.-]+)', email)
    return match.group(1) if match else None


def calculate_risk(entity):
    """
    Assigns a risk score to a single entity based on pattern heuristics.
    Integrates both technical markers and phishing indicators.
    """
    value = entity["value"].lower()
    etype = entity.get("type", "")
    score = 0
    tags = []

    # 1️⃣ Suspicious TLDs / domains
    if any(tld in value for tld in [".xyz", ".top", ".tk", ".pw", ".cf", ".club"]):
        score += 20
        tags.append("suspicious_tld")

    # 2️⃣ Financial/credential-related keywords
    if any(k in value for k in ["verify", "kyc", "secure", "update", "payment", "login"]):
        score += 25
        tags.append("phishing_keyword")

    # 3️⃣ Email reputation
    if etype == "email":
        domain = domain_from_email(value)
        if domain and not any(ok in domain for ok in ["gov", "edu", "amazon", "hdfcbank", "icici", "paytm"]):
            score += 30
            tags.append("unverified_domain")

    # 4️⃣ Foreign domains
    if any(cc in value for cc in [".ru", ".cn", ".br", ".cl", ".io"]):
        score += 15
        tags.append("foreign_domain")

    # 5️⃣ UPI or Crypto presence
    if etype in ["upi", "crypto_wallet"]:
        score += 10
        tags.append("financial_channel")

    # 6️⃣ Adjust using regex confidence (if available)
    if "confidence" in entity:
        score *= entity["confidence"]

    score = min(100, round(score, 2))

    risk_level = "High" if score >= 70 else "Medium" if score >= 40 else "Low"

    return {
        "entity": entity["value"],
        "type": etype,
        "risk_score": score,
        "risk_level": risk_level,
        "tags": tags
    }

# -----------------------------------
# Case-Level Aggregation
# -----------------------------------

HIGH_RISK_KEYWORDS = [
    "urgent", "verify", "immediately", "transfer", "payment", "otp",
    "win", "claim", "refund", "block", "suspended", "update", "login", "secure"
]

MEDIUM_RISK_KEYWORDS = [
    "helpdesk", "support", "account", "service", "offer", "promotion", "congratulations"
]

DECEPTIVE_TONE_PATTERNS = [
    r"(act\s+now)", r"(limited\s+time)", r"(verify\s+account)",
    r"(update\s+details)", r"(click\s+here)", r"(avoid\s+suspension)"
]


def _detect_deceptive_tone(text):
    """Detects psychological manipulation cues in scam-like language."""
    text_lower = text.lower()
    count = sum(1 for pattern in DECEPTIVE_TONE_PATTERNS if re.search(pattern, text_lower))
    return min(1.0, count * 0.15)  # scale 0–1


def assess_risk(text, entities, scam_class, osint_hits=None):
    """
    ⚖️ Multi-factor risk fusion engine
    Combines AI classifier, entities, OSINT, sentiment, tone, and keyword signals.
    """
    if osint_hits is None:
        osint_hits = []

    text_lower = text.lower()

    # --- 1️⃣ Scam classifier weight ---
    scam_conf = scam_class.get("confidence", 0)
    scam_type = scam_class.get("category", "Unknown")

    # --- 2️⃣ Entity-level aggregate risk ---
    entity_results = [calculate_risk(e) for e in entities]
    avg_entity_risk = np.mean([e["risk_score"] for e in entity_results]) / 100 if entity_results else 0

    # --- 3️⃣ Keyword & tone toxicity ---
    high_kw = sum(1 for kw in HIGH_RISK_KEYWORDS if kw in text_lower)
    med_kw = sum(1 for kw in MEDIUM_RISK_KEYWORDS if kw in text_lower)
    kw_score = min(1.0, (high_kw * 0.12) + (med_kw * 0.05))
    tone_score = _detect_deceptive_tone(text)

    # --- 4️⃣ Sentiment neutrality ---
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    sentiment_score = 1 - abs(sentiment)

    # --- 5️⃣ OSINT intelligence impact ---
    osint_confidence = 0
    for hit in osint_hits:
        agg = hit.get("aggregate_score", 0)
        osint_confidence += min(1.0, agg / 100 * 0.3)
    osint_score = min(1.0, osint_confidence)

    # --- 6️⃣ Dynamic weight tuning ---
    # Adjust relative weights depending on scam type
    base_weights = {
        "scam_conf": 0.4,
        "entity_risk": 0.25,
        "keyword_toxicity": 0.15,
        "sentiment": 0.05,
        "osint": 0.1,
        "tone": 0.05
    }

    if "investment" in scam_type.lower():
        base_weights["osint"] += 0.05
    elif "phishing" in scam_type.lower():
        base_weights["keyword_toxicity"] += 0.05
    elif "loan" in scam_type.lower():
        base_weights["entity_risk"] += 0.05

    # --- 7️⃣ Weighted fusion ---
    final_score = (
        scam_conf * base_weights["scam_conf"]
        + avg_entity_risk * base_weights["entity_risk"]
        + kw_score * base_weights["keyword_toxicity"]
        + tone_score * base_weights["tone"]
        + sentiment_score * base_weights["sentiment"]
        + osint_score * base_weights["osint"]
    )
    final_score = round(final_score, 3)

    # --- 8️⃣ Risk classification ---
    if final_score >= 0.75:
        risk_level = "HIGH 🔴"
    elif final_score >= 0.45:
        risk_level = "MEDIUM 🟠"
    else:
        risk_level = "LOW 🟢"

    # --- 9️⃣ Explainable reasoning ---
    reasons = []
    if scam_conf > 0.7:
        reasons.append(f"AI classified as {scam_type} ({int(scam_conf * 100)}% confidence)")
    if avg_entity_risk > 0.3:
        reasons.append("Suspicious entities or financial channels detected")
    if kw_score > 0.3:
        reasons.append("Urgent or manipulative keywords found")
    if tone_score > 0.3:
        reasons.append("Deceptive tone detected in language")
    if osint_score > 0.1:
        reasons.append("Entity flagged in OSINT threat feeds")

    rationale = "; ".join(reasons) if reasons else "No major fraud indicators found."

    # --- 🔟 Return full structured intelligence ---
    return {
        "score": final_score,
        "risk_level": risk_level,
        "rationale": rationale,
        "timestamp": datetime.now().isoformat(),
        "entity_details": entity_results,
        "factors": {
            "scam_confidence": scam_conf,
            "avg_entity_risk": round(avg_entity_risk, 2),
            "keyword_toxicity": kw_score,
            "tone_score": tone_score,
            "sentiment_neutrality": sentiment_score,
            "osint_weight": osint_score,
        },
        "scam_type": scam_type,
    }
