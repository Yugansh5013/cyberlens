# app/api/threat_hub.py
from fastapi import APIRouter, Query, HTTPException, UploadFile, File, Form
import os, json
from collections import defaultdict, Counter
from datetime import datetime
from urllib.parse import unquote
import uuid
import shutil

router = APIRouter()

CACHE_DIR = "app/data/analysis_cache"
DB_PATH = "app/data/knowledge_db.jsonl"
os.makedirs("app/data", exist_ok=True)


# -----------------------------------------------------------
# 🧠 Utility: Load all analyzed cases (cached JSONs)
# -----------------------------------------------------------
def load_all_cases():
    cases = []
    for file in os.listdir(CACHE_DIR):
        if file.endswith(".json"):
            try:
                with open(os.path.join(CACHE_DIR, file), "r", encoding="utf-8") as f:
                    cases.append(json.load(f))
            except Exception as e:
                print(f"⚠️ Skipping {file}: {e}")
    return cases


# -----------------------------------------------------------
# 🔍 1️⃣ Entity / Case Search
# -----------------------------------------------------------
@router.get("/cases/search")
def search_cases(q: str = Query("", description="Optional search filter")):
    """Return all analyzed cases (flattened summary for dashboard)."""
    results = []
    for case in load_all_cases():
        if q.lower() in json.dumps(case).lower():
            results.append({
                "file_id": case.get("file_id"),
                "scam_class": {
                    "category": case.get("scam_class", {}).get("category", "Unknown")
                },
                "risk": {
                    "score": case.get("risk", {}).get("score", 0.0),
                    "risk_level": case.get("risk", {}).get("risk_level", "N/A")
                },
                "analyzed_at": case.get("analyzed_at"),
            })
    return results



# -----------------------------------------------------------
# 📊 2️⃣ Top Entities Across Cases
# -----------------------------------------------------------
@router.get("/cases/top-entities")
def top_entities(limit: int = 10):
    """List most common entities across all cached cases."""
    freq = defaultdict(lambda: {"count": 0, "risk_sum": 0.0})
    for case in load_all_cases():
        for ent in case.get("entities", []):
            key = ent["value"].lower()
            freq[key]["count"] += 1
            freq[key]["risk_sum"] += case.get("risk", {}).get("score", 0.0)

    ranked = sorted(
        [
            {
                "entity": k,
                "count": v["count"],
                "avg_risk": round(v["risk_sum"] / v["count"], 2),
            }
            for k, v in freq.items()
        ],
        key=lambda x: x["count"],
        reverse=True,
    )

    return {"total_entities": len(freq), "top": ranked[:limit]}


# -----------------------------------------------------------
# 🧩 3️⃣ Entity Intelligence Profile
# -----------------------------------------------------------
# at top of file
from urllib.parse import unquote
from fastapi import Query, HTTPException

# replace existing endpoint with this
@router.get("/entities/profile")
def entity_profile(entity: str = Query(None), value: str = Query(None)):
    # Accept either ?entity=... or ?value=...; decode and normalize
    raw = entity or value or ""
    query_value = unquote(raw).strip().lower()

    if not query_value:
        raise HTTPException(status_code=422, detail="Missing 'entity' or 'value' query parameter")

    cases_found = []
    categories, risk_scores = set(), []

    for case in load_all_cases():
        for ent in case.get("entities", []):
            ent_val = (ent.get("value", "") or "").lower()
            if query_value in ent_val:
                cases_found.append({
                    "case_id": case["file_id"],
                    "category": case.get("scam_class", {}).get("category"),
                    "risk_score": case.get("risk", {}).get("score"),
                    "osint_hits": case.get("osint_hits", []),
                    "timestamp": case.get("analyzed_at"),
                })
                categories.add(case.get("scam_class", {}).get("category"))
                risk_scores.append(case.get("risk", {}).get("score", 0.0))

    if not cases_found:
        raise HTTPException(status_code=404, detail=f"Entity '{query_value}' not found in any case")

    avg_risk = round(sum(risk_scores) / len(risk_scores), 2) if risk_scores else 0.0
    return {
        "entity": query_value,
        "found_in": len(cases_found),
        "linked_categories": [c for c in categories if c],
        "avg_risk": avg_risk,
        "cases": cases_found,
    }





# -----------------------------------------------------------
# 🔗 4️⃣ Scam Cluster Detection
# -----------------------------------------------------------
@router.get("/cases/clusters")
def case_clusters():
    """Detect scam clusters based on shared entities."""
    cases = load_all_cases()
    graph = defaultdict(set)
    entity_to_cases = defaultdict(set)

    # Build map: entity → cases
    for case in cases:
        cid = case["file_id"]
        for ent in case.get("entities", []):
            entity_to_cases[ent["value"].lower()].add(cid)

    # Link cases sharing the same entity
    for entity, linked_cases in entity_to_cases.items():
        for c1 in linked_cases:
            for c2 in linked_cases:
                if c1 != c2:
                    graph[c1].add(c2)

    clusters = []
    visited = set()

    def dfs(case_id, cluster):
        if case_id in visited:
            return
        visited.add(case_id)
        cluster.add(case_id)
        for neighbor in graph[case_id]:
            dfs(neighbor, cluster)

    for cid in graph.keys():
        if cid not in visited:
            cluster = set()
            dfs(cid, cluster)
            if len(cluster) > 1:
                clusters.append(list(cluster))

    return {"total_clusters": len(clusters), "clusters": clusters}


# -----------------------------------------------------------
# 🧠 5️⃣ Persistent Threat Knowledge DB (Optional)
# -----------------------------------------------------------
def append_to_knowledge_db(case_data: dict):
    """Persist summarized entity knowledge for global search."""
    with open(DB_PATH, "a", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "file_id": case_data.get("file_id"),
                "entities": [e["value"] for e in case_data.get("entities", [])],
                "risk_score": case_data.get("risk", {}).get("score"),
                "category": case_data.get("scam_class", {}).get("category"),
            },
            f,
        )
        f.write("\n")
