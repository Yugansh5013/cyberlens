# app/api/batch_analyze.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os, shutil, json, traceback, uuid
from datetime import datetime

from app.pipelines.batch_analyzer import analyze_batch
from app.reports.unified_report_generator import generate_unified_report  # ✅ Correct import
from app.services.chainlog import chain_log

router = APIRouter()

UPLOAD_DIR = "app/data/uploads"
CACHE_DIR = "app/data/analysis_cache"
REPORT_DIR = "app/data/reports"
BATCH_DIR = "app/data/batches"

# Ensure all directories exist
for d in [UPLOAD_DIR, CACHE_DIR, REPORT_DIR, BATCH_DIR]:
    os.makedirs(d, exist_ok=True)


@router.post("/batch-analyze")
async def batch_analyze(files: list[UploadFile] = File(...)):
    """
    Handles multi-file evidence analysis and creates a unique batch directory.
    Each file is analyzed through OCR + NER + OSINT + Risk pipeline.
    Returns a batch_id and summary of analyzed cases.
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided.")

        # ✅ Create batch folder
        batch_id = str(uuid.uuid4())[:8]
        batch_path = os.path.join(BATCH_DIR, batch_id)
        os.makedirs(batch_path, exist_ok=True)

        file_paths = []
        for f in files:
            dest_path = os.path.join(batch_path, f.filename)
            with open(dest_path, "wb") as out:
                shutil.copyfileobj(f.file, out)
            file_paths.append(dest_path)

        # 🧾 Log upload batch
        chain_log(
            action="BATCH_UPLOAD",
            actor="system",
            target=batch_id,
            meta={
                "file_count": len(file_paths),
                "files": [os.path.basename(p) for p in file_paths],
                "timestamp": datetime.now().isoformat(),
            },
        )

        # 🧠 Run batch analysis pipeline (your existing analyzer)
        batch_results = analyze_batch(file_paths)

        # 🗂 Save each file’s analysis result to cache
        for result in batch_results:
            file_id = os.path.splitext(os.path.basename(result["file_id"]))[0]
            cache_path = os.path.join(CACHE_DIR, f"{file_id}.json")
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        # ✅ Optional: also generate unified PDF automatically
        pdf_bytes, pdf_path = generate_unified_report(batch_results, batch_id=batch_id)

        # 🧾 Log completion
        chain_log(
            action="BATCH_ANALYSIS_COMPLETE",
            actor="system",
            target=batch_id,
            meta={
                "total_cases": len(batch_results),
                "report_path": pdf_path,
                "timestamp": datetime.now().isoformat(),
            },
        )

        # ✅ Return structured response for frontend
        return {
            "status": "success",
            "batch_id": batch_id,
            "total_files": len(batch_results),
            "files_processed": [os.path.basename(p) for p in file_paths],
            "unified_report": pdf_path,
            "message": f"Batch {batch_id} analyzed successfully.",
        }

    except Exception as e:
        print("❌ Batch analyze error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")
