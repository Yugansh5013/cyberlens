# app/api/unified_report.py
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
import os, json
from datetime import datetime

from app.reports.unified_report_generator import generate_unified_report
from app.services.chainlog import chain_log

router = APIRouter()

CACHE_DIR = "app/data/analysis_cache"
REPORT_DIR = "app/data/reports"
os.makedirs(REPORT_DIR, exist_ok=True)


@router.post("/unified-report")
def unified_report(batch_id: str = Form(...)):
    """
    Generates a unified forensic PDF report combining multiple cached case analyses.
    """
    batch_dir = os.path.join(CACHE_DIR, batch_id)
    if not os.path.exists(CACHE_DIR):
        raise HTTPException(status_code=404, detail="No analysis cache found.")
    
    # Load all cached case files
    batch_cases = []
    for file in os.listdir(CACHE_DIR):
        if file.endswith(".json"):
            path = os.path.join(CACHE_DIR, file)
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    batch_cases.append(data)
                except Exception as e:
                    print(f"⚠️ Skipped invalid cache file {file}: {e}")

    if not batch_cases:
        raise HTTPException(status_code=404, detail="No valid case data found to generate report.")

    # 🧠 Generate unified PDF
    pdf_bytes, pdf_path = generate_unified_report(batch_cases, batch_id=batch_id)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Unified report generation failed")

    # 🧾 Chain-of-Custody Log
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
