# app/api/threat_hub.py
from fastapi import APIRouter, Query, HTTPException
import os, json
from collections import defaultdict, Counter
from datetime import datetime

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
def search_cases(query: str = Query(..., description="Entity value (email, UPI, phone, domain, etc.)")):
    """Search all cases for a given entity."""
    results = []
    for case in load_all_cases():
        for ent in case.get("entities", []):
            if query.lower() in ent["value"].lower():
                results.append({
                    "case_id": case["file_id"],
                    "category": case.get("scam_class", {}).get("category"),
                    "risk": case.get("risk", {}).get("score"),
                    "risk_level": case.get("risk", {}).get("risk_level"),
                    "timestamp": case.get("analyzed_at"),
                })
                break

    return {
        "query": query,
        "total_hits": len(results),
        "cases": results,
    }


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
@router.get("/entities/profile")
def entity_profile(value: str):
    """Full intelligence profile for an entity across all cases."""
    cases_found = []
    categories, risk_scores = set(), []
    for case in load_all_cases():
        for ent in case.get("entities", []):
            if value.lower() in ent["value"].lower():
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
        raise HTTPException(status_code=404, detail="Entity not found in any case")

    avg_risk = round(sum(risk_scores) / len(risk_scores), 2)
    return {
        "entity": value,
        "found_in": len(cases_found),
        "linked_categories": list(categories),
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
