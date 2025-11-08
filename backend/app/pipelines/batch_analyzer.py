import os, json, uuid, time
from typing import List
from statistics import mean
from datetime import datetime

# ✅ Import all intelligence modules
from app.pipelines.ocr import extract_text_from_image
from app.pipelines.regex_extract import extract_entities
from app.pipelines.ner import extract_named_entities
from app.pipelines.osint_engine import osint_lookup
from app.pipelines.risk_assessor import assess_risk
from app.pipelines.scam_classifier import classify_scam
from app.pipelines.url_qr_scanner import scan_urls_and_qr
from app.services.chainlog import chain_log

UPLOAD_DIR = "app/data/uploads"
CACHE_DIR = "app/data/analysis_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


# -------------------------------------------------------
# 🧩 Process a Single File
# -------------------------------------------------------
def process_single_file(file_path: str):
    """Run full intelligence pipeline on a single file with timestamps."""
    file_id = os.path.basename(file_path)
    start_time = time.time()

    # 1️⃣ OCR Extraction
    raw_text = extract_text_from_image(file_path)

    # 2️⃣ Entity Recognition
    regex_hits = extract_entities(raw_text)
    ner_hits = extract_named_entities(raw_text)
    all_entities = regex_hits + ner_hits

    # 3️⃣ Scam Classification
    scam_class = classify_scam(raw_text)

    # 4️⃣ OSINT Cross-Check
    osint_hits = []
    for e in all_entities:
        try:
            osint_hits.extend(osint_lookup(e["value"]))
        except Exception as e:
            print(f"⚠️ OSINT lookup failed for {e['value']}: {e}")

    # 5️⃣ Risk Assessment
    risk_result = assess_risk(raw_text, all_entities, scam_class, osint_hits)

    # 6️⃣ URL + QR Scan
    url_qr_findings = scan_urls_and_qr(raw_text, file_path)

    # 7️⃣ Cache individual result
    result = {
        "file_id": file_id,
        "raw_text": raw_text,
        "entities": all_entities,
        "scam_class": scam_class,
        "osint_hits": osint_hits,
        "risk": risk_result,
        "url_qr_findings": url_qr_findings,
        "analyzed_at": datetime.now().isoformat(),
        "processing_time_sec": round(time.time() - start_time, 2),
    }

    cache_path = os.path.join(CACHE_DIR, f"{file_id}.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # 8️⃣ Log each file in chain-of-custody
    chain_log(
        action="BATCH_ANALYZE_ITEM",
        actor="system",
        target=file_id,
        meta={
            "risk_score": risk_result.get("score", 0),
            "risk_level": risk_result.get("risk_level", "Unknown"),
            "urls_detected": len(url_qr_findings),
            "entities_found": len(all_entities),
            "processing_time_sec": result["processing_time_sec"],
        },
    )

    return result


# -------------------------------------------------------
# 📊 Aggregate Batch Summary
# -------------------------------------------------------
def aggregate_results(results: List[dict]):
    """Aggregate multiple case results into a unified summary."""
    all_entities = []
    total_risk = []
    categories = {}

    for r in results:
        all_entities += [e["value"] for e in r.get("entities", [])]
        total_risk.append(r.get("risk", {}).get("score", 0))
        cat = r.get("scam_class", {}).get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1

    unique_entities = list(set(all_entities))
    avg_risk = round(mean(total_risk), 2) if total_risk else 0
    dominant_category = max(categories, key=categories.get) if categories else "Unknown"

    return {
        "total_cases": len(results),
        "unique_entities": len(unique_entities),
        "average_risk": avg_risk,
        "dominant_category": dominant_category,
        "categories": categories,
        "sample_entities": unique_entities[:10],
    }


# -------------------------------------------------------
# 🧠 Main Batch Analysis
# -------------------------------------------------------
def analyze_batch(file_paths: List[str]):
    """Analyze multiple evidence files as a single batch job."""
    batch_id = str(uuid.uuid4())[:8]
    print(f"🚀 Starting batch analysis {batch_id} on {len(file_paths)} files...")

    results = []
    for fp in file_paths:
        try:
            results.append(process_single_file(fp))
        except Exception as e:
            print(f"⚠️ Skipped {fp}: {e}")

    if not results:
        return {"error": "No valid results generated."}

    summary = aggregate_results(results)

    # ✅ Save final batch JSON
    final_data = {
        "batch_id": batch_id,
        "summary": summary,
        "cases": results,
        "analyzed_at": datetime.now().isoformat(),
    }

    summary_path = os.path.join(CACHE_DIR, f"batch_{batch_id}.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2)

    # ✅ Log completion in chain-of-custody
    chain_log(
        action="BATCH_ANALYZE_COMPLETE",
        actor="system",
        target=batch_id,
        meta={
            **summary,
            "timestamp": datetime.now().isoformat(),
        },
    )

    print(f"✅ Batch {batch_id} completed. Summary cached at {summary_path}")
    return final_data
