from fastapi import FastAPI
from app.api.evidence import router as evidence_router
from app.api.analyze import router as analyze_router  # 👈 add this line

app = FastAPI()

app.include_router(evidence_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")  # 👈 add this line

@app.get("/health")
def health():
    return {"status": "ok"}
