# app/api/report.py
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
import os, json
from datetime import datetime
from app.pipelines.report_generator import generate_pdf_report
from app.services.chainlog import chain_log

router = APIRouter()

CACHE_DIR = "app/data/analysis_cache"
REPORT_DIR = "app/data/reports"
os.makedirs(REPORT_DIR, exist_ok=True)


@router.post("/report")
def generate_report(file_id: str = Form(...)):
    """
    Generates a detailed forensic PDF report using cached analysis results.
    Integrates all intelligence layers: OCR, Entities, Scam Classifier, OSINT, Risk, and QR/URL findings.
    """
    cache_path = os.path.join(CACHE_DIR, f"{file_id}.json")
    if not os.path.exists(cache_path):
        raise HTTPException(status_code=404, detail=f"Cached analysis not found for file_id: {file_id}")

    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 🧠 Pass all collected intelligence to report generator
    pdf_info = generate_pdf_report(
        file_id=file_id,
        raw_text=data.get("raw_text", ""),
        entities=data.get("entities", []),
        risk_report=data.get("risk", {}),
        threat_intel=data.get("osint_hits", []),
        scam_class=data.get("scam_class", {}),
        url_qr_findings=data.get("url_qr_findings", []),
    )

    pdf_path = pdf_info.get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Report generation failed — no file created")

    # 🧾 Log chain of custody entry
    chain_log(
        action="GENERATE_REPORT",
        actor="system",
        target=file_id,
        meta={
            "pdf_path": pdf_path,
            "timestamp": datetime.now().isoformat(),
            "entities": len(data.get("entities", [])),
            "risk_level": data.get("risk", {}).get("risk_level"),
        },
    )

    # ✅ Return downloadable file
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path),
    )
