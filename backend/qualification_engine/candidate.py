import json


ENGINE_VERSION = "candidate-qualification-v1"
DIMENSIONS = (
    "industry_fit", "skill_fit", "technology_fit", "business_problem_fit",
    "location_fit", "opportunity_type_fit", "budget_fit", "opportunity_signal",
)


def _parse_json(text):
    fence = chr(96) * 3
    value = text.strip()
    if value.startswith(fence + "json"):
        value = value[7:]
    elif value.startswith(fence):
        value = value[3:]
    if value.endswith(fence):
        value = value[:-3]
    return json.loads(value.strip())


def enforce_qualification(decision, threshold=80):
    dimensions = decision.get("dimensions") or {}
    score = max(0, min(100, int(decision.get("score") or 0)))
    hard_mismatches = decision.get("hard_mismatches") or []
    opportunity_signal = dimensions.get("opportunity_signal") or {}
    has_signal = opportunity_signal.get("status") == "match" and bool(
        opportunity_signal.get("evidence")
    )
    qualified = (
        decision.get("verdict") == "qualified"
        and score >= threshold
        and has_signal
        and not hard_mismatches
    )
    if qualified:
        verdict = "qualified"
    elif decision.get("verdict") == "needs_review" and score >= 60:
        verdict = "needs_review"
    else:
        verdict = "rejected"
    return {**decision, "score": score, "verdict": verdict, "gate_passed": qualified}


def qualify_researched_candidates(repository, openai_client, business_dna, limit=10):
    candidates = repository.researched_candidates_for_qualification(limit)
    if not candidates:
        return {"qualified": 0, "rejected": 0, "needs_review": 0}
    review = [
        {
            "index": index,
            "candidate": {
                "title": item.get("title"), "url": item.get("source_url"),
                "research": item.get("research_profile") or {},
                "evidence": item.get("research_evidence") or [],
            },
        }
        for index, item in enumerate(candidates)
    ]
    prompt = f"""
You are the strict Qualification Engine for BusinessDev OS. Compare each researched
business with the complete Business DNA. Use only stored research and evidence. Do not
convert a general company fit into an opportunity: qualification requires a concrete,
current buying, hiring, partnership, contract, RFP, operational, or technology-change signal.

BUSINESS DNA:
{json.dumps(business_dna, indent=2, default=str)}

RESEARCHED CANDIDATES:
{json.dumps(review, indent=2, default=str)}

Return only valid JSON: {{"decisions":[{{"index":0,"verdict":"qualified|rejected|needs_review",
"score":0,"dimensions":{{"industry_fit":{{"status":"match|mismatch|unknown","evidence":[]}},
"skill_fit":{{"status":"match|mismatch|unknown","evidence":[]}},"technology_fit":{{"status":"match|mismatch|unknown","evidence":[]}},
"business_problem_fit":{{"status":"match|mismatch|unknown","evidence":[]}},"location_fit":{{"status":"match|mismatch|unknown","evidence":[]}},
"opportunity_type_fit":{{"status":"match|mismatch|unknown","evidence":[]}},"budget_fit":{{"status":"match|mismatch|unknown","evidence":[]}},
"opportunity_signal":{{"status":"match|mismatch|unknown","evidence":[]}}}},"fit_reasons":[],"risk_signals":[],
"hard_mismatches":[],"missing_data":[],"opportunity":{{"title":"","type":"","summary":""}}}}]}}

Missing information must be unknown, never a match. A target business without a concrete
opportunity signal must be rejected or needs_review, never qualified.
"""
    response = openai_client.responses.create(model="gpt-4.1-mini", input=prompt)
    payload = _parse_json(response.output_text)
    decisions = {item.get("index"): item for item in payload.get("decisions", []) if isinstance(item, dict)}
    counts = {"qualified": 0, "rejected": 0, "needs_review": 0}
    for index, candidate in enumerate(candidates):
        decision = enforce_qualification(decisions.get(index, {}))
        repository.save_candidate_qualification(candidate["id"], decision, ENGINE_VERSION)
        counts[decision["verdict"]] += 1
        if decision["gate_passed"]:
            repository.promote_candidate(candidate, decision)
    return counts
