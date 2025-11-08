# app/api/batch_analyze.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os, shutil, json, traceback
from datetime import datetime

from app.pipelines.batch_analyzer import analyze_batch
from app.pipelines.unified_report_generator import generate_unified_report
from app.services.chainlog import chain_log

router = APIRouter()

UPLOAD_DIR = "app/data/uploads"
CACHE_DIR = "app/data/analysis_cache"
REPORT_DIR = "app/data/reports"

# Ensure all directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


@router.post("/batch-analyze")
async def batch_analyze(files: list[UploadFile] = File(...)):
    """
    Handles multi-file evidence analysis and generates a unified summary PDF.
    Each file is analyzed through the same OCR + NER + OSINT + Risk pipeline.
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided.")

        file_paths = []
        for f in files:
            # Save each uploaded file
            dest_path = os.path.join(UPLOAD_DIR, f.filename)
            with open(dest_path, "wb") as out:
                shutil.copyfileobj(f.file, out)
            file_paths.append(dest_path)

        # Log upload batch
        chain_log(
            action="BATCH_UPLOAD",
            actor="system",
            target=f"{len(file_paths)} files",
            meta={"timestamp": datetime.now().isoformat()},
        )

        # Run batch analysis pipeline
        batch_results = analyze_batch(file_paths)

        # Save individual analysis results to cache
        for result in batch_results:
            file_id = os.path.basename(result["file_id"])
            cache_path = os.path.join(CACHE_DIR, f"{file_id}.json")
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        # Generate unified report PDF
        pdf_bytes = generate_unified_report(batch_results)
        unified_report_path = os.path.join(REPORT_DIR, f"unified_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        with open(unified_report_path, "wb") as f:
            f.write(pdf_bytes)

        # Log completion
        chain_log(
            action="BATCH_ANALYSIS_COMPLETE",
            actor="system",
            target=f"{len(file_paths)} files",
            meta={
                "report_path": unified_report_path,
                "files_analyzed": [os.path.basename(p) for p in file_paths],
                "timestamp": datetime.now().isoformat(),
            },
        )

        # Return response
        return {
            "status": "success",
            "files_processed": [os.path.basename(p) for p in file_paths],
            "batch_count": len(file_paths),
            "unified_report": unified_report_path,
        }

    except Exception as e:
        print("❌ Batch analyze error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")
