import os, json, re, time, hashlib, requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from datetime import datetime

# 🔐 Load API keys
load_dotenv()
VT_API_KEY = os.getenv("VT_API_KEY", "")
ABUSEIPDB_KEY = os.getenv("ABUSEIPDB_KEY", "")
WHOIS_KEY = os.getenv("WHOIS_KEY", "")

# 📂 Fallbacks and cache
FALLBACK_DIR = "app/pipelines/fallback_osint"
CACHE_DIR = "app/data/osint_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
URL_RE   = re.compile(r"https?://([A-Za-z0-9.-]+\.[A-Za-z]{2,})(?:[^\s]*)")
IP_RE    = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

# ------------------------------------------------------------
# ⚙️ Utility Helpers
# ------------------------------------------------------------
def _read_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{hashlib.sha1(key.encode()).hexdigest()}.json")

def _from_cache(key: str, ttl_hours=24):
    path = _cache_path(key)
    if not os.path.exists(path):
        return None
    age = time.time() - os.path.getmtime(path)
    if age > ttl_hours * 3600:
        return None
    return _read_json(path)

def _save_cache(key: str, data: dict):
    try:
        with open(_cache_path(key), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def _safe_get_json(url: str, headers=None, params=None, timeout=10):
    try:
        r = requests.get(url, headers=headers, params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json(), False
        return {"error": f"status_{r.status_code}"}, True
    except Exception as e:
        return {"error": str(e)}, True

def _risk_label(score: int) -> str:
    if score >= 70: return "High"
    if score >= 40: return "Medium"
    return "Low"

# ------------------------------------------------------------
# 🌐 External Sources (VirusTotal, AbuseIPDB, Whois, OpenPhish)
# ------------------------------------------------------------
def vt_domain_report(domain: str):
    key = f"vt_domain_{domain}"
    cached = _from_cache(key)
    if cached: return cached

    if not VT_API_KEY:
        return {"source": "virustotal", "used_fallback": True, "note": "no_api_key"}

    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": VT_API_KEY}
    data, failed = _safe_get_json(url, headers=headers)
    if failed:
        return {"source": "virustotal", "used_fallback": True, **data}

    stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
    positives = stats.get("malicious", 0) + stats.get("suspicious", 0)
    score = min(100, positives * 20)
    out = {"source": "virustotal", "positives": positives, "score": score, "risk": _risk_label(score)}
    _save_cache(key, out)
    return out

def vt_url_report(url_str: str):
    key = f"vt_url_{url_str}"
    cached = _from_cache(key)
    if cached: return cached

    if not VT_API_KEY:
        return {"source": "virustotal_url", "used_fallback": True, "note": "no_api_key"}

    search_url = "https://www.virustotal.com/api/v3/search"
    data, failed = _safe_get_json(search_url, headers={"x-apikey": VT_API_KEY}, params={"query": url_str})
    if failed:
        return {"source": "virustotal_url", "used_fallback": True, **data}

    positives = 0
    for item in data.get("data", []):
        stats = item.get("attributes", {}).get("last_analysis_stats", {})
        positives = max(positives, stats.get("malicious", 0) + stats.get("suspicious", 0))
    score = min(100, positives * 20)
    out = {"source": "virustotal_url", "positives": positives, "score": score, "risk": _risk_label(score)}
    _save_cache(key, out)
    return out

def abuseipdb_report(ip: str):
    key = f"abuseip_{ip}"
    cached = _from_cache(key)
    if cached: return cached

    if not ABUSEIPDB_KEY:
        return {"source": "abuseipdb", "used_fallback": True, "note": "no_api_key"}

    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": ABUSEIPDB_KEY, "Accept": "application/json"}
    data, failed = _safe_get_json(url, headers=headers, params={"ipAddress": ip, "maxAgeInDays": "180"})
    if failed:
        return {"source": "abuseipdb", "used_fallback": True, **data}

    score = int(data.get("data", {}).get("abuseConfidenceScore", 0))
    out = {"source": "abuseipdb", "score": score, "risk": _risk_label(score)}
    _save_cache(key, out)
    return out

def whois_domain(domain: str):
    key = f"whois_{domain}"
    cached = _from_cache(key)
    if cached: return cached

    if not WHOIS_KEY:
        return {"source": "whois", "used_fallback": True, "note": "no_api_key"}

    url = "https://www.whoisxmlapi.com/whoisserver/WhoisService"
    params = {"apiKey": WHOIS_KEY, "domainName": domain, "outputFormat": "JSON"}
    data, failed = _safe_get_json(url, params=params)
    if failed:
        return {"source": "whois", "used_fallback": True, **data}

    rec = data.get("WhoisRecord", {})
    reg = rec.get("registrarName")
    cr  = rec.get("createdDateNormalized") or rec.get("createdDate")
    cn  = rec.get("registryData", {}).get("country")
    age_tag = "new_domain" if cr and str(cr).startswith(("2025","2024","2023")) else "established"
    out = {"source": "whois", "registrar": reg, "created": cr, "country": cn, "age_tag": age_tag}
    _save_cache(key, out)
    return out

def openphish_check(domain_or_url: str):
    key = f"openphish_{domain_or_url}"
    cached = _from_cache(key)
    if cached: return cached
    try:
        r = requests.get("https://openphish.com/feed.txt", timeout=5)
        if r.status_code == 200:
            hit = any(domain_or_url in line for line in r.text.splitlines()[:2000])
            out = {"source": "openphish", "listed": bool(hit)}
            _save_cache(key, out)
            return out
        return {"source": "openphish", "error": f"status_{r.status_code}"}
    except Exception as e:
        return {"source": "openphish", "error": str(e)}

# ------------------------------------------------------------
# 🧠 OSINT Fusion Layer
# ------------------------------------------------------------
def enrich_entity_osint(entity: Dict[str, Any]) -> Dict[str, Any]:
    """Central intelligence hub: combines multi-source OSINT into one dict."""
    etype = entity.get("type", "").lower()
    val = entity.get("value", "")
    result = {"entity": val, "type": etype, "timestamp": datetime.now().isoformat()}

    try:
        if "@" in val:  # email
            m = EMAIL_RE.search(val)
            domain = m.group(1) if m else None
            vt = vt_domain_report(domain)
            wh = whois_domain(domain)
            op = openphish_check(domain)
            score = int((vt.get("score", 0) + wh.get("age_tag") == "new_domain" and 10 or 0) + (op.get("listed") and 30 or 0))
            result.update({"domain": domain, "sources": [vt, wh, op], "aggregate_score": score, "risk": _risk_label(score)})
        elif re.match(URL_RE, val):
            m = URL_RE.search(val)
            domain = m.group(1) if m else None
            vt_u = vt_url_report(val)
            vt_d = vt_domain_report(domain)
            op = openphish_check(val)
            score = int((vt_u.get("score", 0) + vt_d.get("score", 0)) / 2 + (op.get("listed") and 20 or 0))
            result.update({"domain": domain, "sources": [vt_u, vt_d, op], "aggregate_score": score, "risk": _risk_label(score)})
        elif re.match(IP_RE, val):
            ab = abuseipdb_report(val)
            result.update({"sources": [ab], "aggregate_score": ab.get("score", 0), "risk": ab.get("risk", "Low")})
        elif "." in val:  # domain
            vt = vt_domain_report(val)
            wh = whois_domain(val)
            op = openphish_check(val)
            score = int((vt.get("score", 0) + (wh.get("age_tag") == "new_domain" and 15 or 0) + (op.get("listed") and 20 or 0)))
            result.update({"sources": [vt, wh, op], "aggregate_score": score, "risk": _risk_label(score)})
        else:
            result.update({"aggregate_score": 0, "risk": "Unknown"})
    except Exception as e:
        result.update({"error": str(e)})

    return result

# -------------------------------
# 🧩 Local Fallbacks (used by URL/QR scanner)
# -------------------------------

def fallback_domain(domain: str):
    return {
        "domain": domain,
        "risk": "unknown",
        "tags": ["no_local_match"],
        "sources": ["fallback"],
    }

def fallback_ip(ip: str):
    return {
        "ip": ip,
        "risk": "unknown",
        "tags": ["no_local_match"],
        "sources": ["fallback"],
    }

def fallback_email(email: str):
    return {
        "email": email,
        "risk": "unknown",
        "tags": ["no_local_match"],
        "sources": ["fallback"],
    }


