# app/api/upload_evidence.py
import hashlib, os, uuid, json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.chainlog import chain_log
from app.pipelines.url_qr_scanner import scan_urls_and_qr

router = APIRouter()

UPLOAD_DIR = "app/data/uploads"
META_DIR = "app/data/metadata"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)


# -------------------------------------------------------
# 🧠 Utility: Compute SHA-256 for file integrity
# -------------------------------------------------------
def sha256_file(file_path: str) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()


# -------------------------------------------------------
# 🚀 Upload Route
# -------------------------------------------------------
@router.post("/upload-evidence")
async def upload_evidence(file: UploadFile = File(...)):
    """
    Uploads digital evidence, verifies integrity, logs the chain-of-custody,
    and performs instant QR/URL pre-scan for early threat signals.
    """
    # ✅ Step 1: Validate file type
    allowed_exts = {".png", ".jpg", ".jpeg", ".pdf", ".txt"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_exts)}",
        )

    # ✅ Step 2: Save file with UUID
    new_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, new_name)

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # ✅ Step 3: Compute file hash
    file_hash = sha256_file(file_path)

    # ✅ Step 4: Log to chain of custody
    chain_log(
        action="UPLOAD_EVIDENCE",
        actor="system",
        target=new_name,
        sha256=file_hash,
        meta={
            "original_name": file.filename,
            "uploaded_at": datetime.now().isoformat(),
            "file_type": ext,
            "size_bytes": os.path.getsize(file_path),
        },
    )

    # ✅ Step 5: Instant URL/QR Scan (non-blocking preview)
    try:
        pre_scan_result = scan_urls_and_qr(None, file_path)
    except Exception as e:
        pre_scan_result = {"error": f"Pre-scan failed: {str(e)}"}

    # ✅ Step 6: Store structured metadata
    metadata = {
        "file_id": new_name,
        "original_name": file.filename,
        "sha256": file_hash,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stored_at": file_path,
        "file_type": ext,
        "file_size": os.path.getsize(file_path),
        "pre_scan": pre_scan_result,
    }

    meta_path = os.path.join(META_DIR, f"{new_name}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # ✅ Step 7: Return response
    return {
        "status": "success",
        "file_id": new_name,
        "sha256": file_hash,
        "original_name": file.filename,
        "stored_at": file_path,
        "pre_scan": pre_scan_result,
        "message": "Evidence successfully uploaded, verified, logged, and scanned.",
    }
