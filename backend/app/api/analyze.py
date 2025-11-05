from fastapi import APIRouter, Form
from app.pipelines.ocr import extract_text_from_image
from app.pipelines.regex_extract import extract_entities
from app.pipelines.ner import extract_named_entities
from app.services.chainlog import chain_log
import os

router = APIRouter()

UPLOAD_DIR = "app/data/uploads"

@router.post("/analyze")
def analyze(file_id: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file_id)

    if not os.path.exists(file_path):
        return {"error": "File not found", "file_id": file_id}

    raw_text = extract_text_from_image(file_path)
    regex_hits = extract_entities(raw_text)
    ner_hits = extract_named_entities(raw_text)

    all_entities = regex_hits + ner_hits

    chain_log(
        action="ANALYZE_EVIDENCE",
        actor="system",
        target=file_id,
        sha256=None,
        meta={"entities_found": len(all_entities)}
    )

    return {
        "file_id": file_id,
        "raw_text": raw_text,
        "entities": all_entities
    }
