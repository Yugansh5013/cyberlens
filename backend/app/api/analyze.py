from fastapi import APIRouter, Form, HTTPException
from app.pipelines.ocr import extract_text_from_image
from app.pipelines.regex_extract import extract_entities
from app.pipelines.ner import extract_named_entities
from app.pipelines.osint_engine import enrich_entity_osint
from app.pipelines.risk_assessor import assess_risk
from app.pipelines.scam_classifier import classify_scam
from app.pipelines.url_qr_scanner import scan_urls_and_qr
from app.services.chainlog import chain_log
import os, json, traceback
from datetime import datetime
from collections import Counter

router = APIRouter()

UPLOAD_DIR = "app/data/uploads"
CACHE_DIR = "app/data/analysis_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


@router.post("/analyze")
def analyze(file_id: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file_id)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")

    try:
        # 1️⃣ OCR Extraction
        raw_text = extract_text_from_image(file_path)

        # 2️⃣ Entity Recognition (Regex + NER)
        regex_hits = extract_entities(raw_text)
        ner_hits = extract_named_entities(raw_text)
        all_entities = regex_hits + ner_hits

        # 3️⃣ AI Scam Classifier (hybrid ML + embeddings)
        scam_class = classify_scam(raw_text)

        # 4️⃣ OSINT Cross-Verification for Entities
        osint_hits = []
        for e in all_entities:
            result = enrich_entity_osint(e)
            if result and isinstance(result, dict):
                osint_hits.append(result)



        # 5️⃣ Risk Assessment (multi-factor AI risk fusion)
        risk_result = assess_risk(raw_text, all_entities, scam_class, osint_hits)
        risk_score = risk_result.get("score", 0.0)

        # 6️⃣ URL + QR Analysis (Heuristic + OSINT-integrated)
        url_qr_findings = scan_urls_and_qr(raw_text, file_path)

        # ✅ Derive Summary from URL + QR results
        risk_levels = [u["risk_level"] for u in url_qr_findings] if url_qr_findings else []
        summary_counter = Counter(risk_levels)
        total_urls = len(url_qr_findings)
        high_risk_domains = [u["domain"] for u in url_qr_findings if u["risk_level"] == "High"]

        url_summary = {
            "total_urls_scanned": total_urls,
            "high_risk": summary_counter.get("High", 0),
            "medium_risk": summary_counter.get("Medium", 0),
            "low_risk": summary_counter.get("Low", 0),
            "top_high_risk_domains": list(set(high_risk_domains))[:5],
        }

        # 7️⃣ Chain-of-Custody Logging
        chain_log(
            action="ANALYZE_EVIDENCE",
            actor="system",
            target=file_id,
            meta={
                "timestamp": datetime.now().isoformat(),
                "entities_found": len(all_entities),
                "urls_scanned": total_urls,
                "category": scam_class.get("category"),
                "risk_score": risk_score,
                "risk_level": risk_result.get("risk_level"),
                "high_risk_urls": url_summary["high_risk"],
            },
        )

        # 8️⃣ Cache Result for Reports / Dashboard
        result = {
            "file_id": file_id,
            "raw_text": raw_text,
            "entities": all_entities,
            "scam_class": scam_class,
            "osint_hits": osint_hits,
            "risk": risk_result,
            "url_qr_findings": url_qr_findings,
            "url_summary": url_summary,
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        cache_path = os.path.join(CACHE_DIR, f"{file_id}.json")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return {
            "status": "success ✅",
            "message": "Full AI–OSINT–risk analysis completed.",
            **result
        }

    except Exception as e:
        error_trace = traceback.format_exc()
        print("❌ Analyze error:", error_trace)

        chain_log(
            action="ANALYZE_FAILED",
            actor="system",
            target=file_id,
            meta={"error": str(e), "trace": error_trace},
        )

        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
