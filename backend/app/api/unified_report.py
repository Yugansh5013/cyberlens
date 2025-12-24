# app/api/unified_report.py
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
import os, json
from datetime import datetime

from app.reports.unified_report_generator import generate_unified_report
from app.services.chainlog import chain_log

router = APIRouter()

CACHE_ROOT = "app/data/analysis_cache"
BATCH_ROOT = "app/data/batches"
REPORT_DIR = "app/data/reports"
os.makedirs(REPORT_DIR, exist_ok=True)


@router.post("/unified-report")
def unified_report(batch_id: str = Form(...)):
    """
    Generates a unified forensic PDF report combining multiple cached analyses
    belonging to the given batch_id.
    """
    print("✅ Received unified-report request with batch_id:", batch_id)

    # ✅ Validate batch directory existence
    batch_dir = os.path.join(BATCH_ROOT, batch_id)
    if not os.path.exists(batch_dir):
        raise HTTPException(
            status_code=404,
            detail=f"Batch '{batch_id}' not found. Please run /batch-analyze first."
        )

    batch_cases = []
    missing_cache = []

    # ✅ Loop through files in batch folder
    for file_name in os.listdir(batch_dir):
        # Ignore non-image files
        if not file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        # Map to corresponding JSON cache file (e.g., "abc.jpg" → "abc.jpg.json")
        cache_file = os.path.join(CACHE_ROOT, f"{file_name}.json")

        if not os.path.exists(cache_file):
            missing_cache.append(file_name)
            continue

        # Load cached analysis safely
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                batch_cases.append(data)
        except Exception as e:
            print(f"⚠️ Error reading cache {cache_file}: {e}")

    # 🚫 If no valid analysis data found
    if not batch_cases:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "No valid case data found for this batch.",
                "missing_cache": missing_cache,
                "searched_batch_dir": os.listdir(batch_dir),
                "available_cache": [f for f in os.listdir(CACHE_ROOT) if f.endswith(".json")]
            },
        )

    # ✅ Generate unified report
    try:
        pdf_bytes, pdf_path = generate_unified_report(batch_cases, batch_id=batch_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unified report generation failed: {e}")

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="PDF generation failed — no file created.")

    # 🧾 Log chain-of-custody action
    chain_log(
        action="GENERATE_UNIFIED_REPORT",
        actor="system",
        target=batch_id,
        meta={
            "total_cases": len(batch_cases),
            "pdf_path": pdf_path,
            "timestamp": datetime.now().isoformat(),
        },
    )

    # ✅ Return generated report for download
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path),
    )
