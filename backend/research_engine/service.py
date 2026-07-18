import json
from datetime import datetime, timezone


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


def research_candidates(repository, tavily_client, openai_client, business_dna, limit=5):
    candidates = repository.pending_candidates(limit)
    if not candidates:
        return {"researched": 0, "rejected": 0, "failed": 0}
    urls = [candidate["source_url"] for candidate in candidates]
    extraction = tavily_client.extract(urls=urls, extract_depth="basic", format="markdown")
    extracted = {item.get("url"): item.get("raw_content", "") for item in extraction.get("results", [])}
    evidence = [
        {
            "index": index,
            "url": candidate["source_url"],
            "search_title": candidate.get("title"),
            "search_snippet": candidate.get("snippet"),
            "website_content": extracted.get(candidate["source_url"], "")[:8000],
        }
        for index, candidate in enumerate(candidates)
    ]
    prompt = f"""
You are the evidence-grounded Research Engine for BusinessDev OS. Research each candidate
objectively from the supplied webpage evidence. Do not qualify it or invent missing facts.
Distinguish a target operating business from an agency, consultant directory, software
vendor, publisher, training provider, or service provider. A matching service page is not
an opportunity signal.

BUSINESS DNA CONTEXT (used only to identify potentially relevant signals):
{json.dumps(business_dna, indent=2, default=str)}

CANDIDATE EVIDENCE:
{json.dumps(evidence, indent=2, default=str)}

Return only valid JSON with one result per index:
{{"results":[{{"index":0,"company_name":"","products":[],"business_model":"",
"industry":"","country":"","company_size":"unknown","technology_signals":[],
"growth_signals":[],"hiring_signals":[],"pain_point_hypotheses":[],
"opportunity_signals":[],"decision_maker_roles":[],"is_service_provider":false,
"is_target_business":false,"confidence":"low|medium|high","evidence_limitations":[]}}]}}

Rules: use only evidence supplied; hypotheses must be labelled as hypotheses; an empty
opportunity_signals array is valid and preferred over speculation.
"""
    response = openai_client.responses.create(model="gpt-4.1-mini", input=prompt)
    payload = _parse_json(response.output_text)
    results = {item.get("index"): item for item in payload.get("results", []) if isinstance(item, dict)}
    researched = rejected = failed = 0
    now = datetime.now(timezone.utc).isoformat()
    for index, candidate in enumerate(candidates):
        profile = results.get(index)
        page_content = extracted.get(candidate["source_url"], "")
        if not profile or not page_content:
            repository.save_candidate_research(candidate["id"], "failed", {}, [], "Missing extraction or AI result", now)
            failed += 1
            continue
        evidence_record = [{"url": candidate["source_url"], "excerpt": page_content[:1500]}]
        repository.save_candidate_research(candidate["id"], "completed", profile, evidence_record, None, now)
        researched += 1
        if profile.get("is_service_provider") is True or profile.get("is_target_business") is not True:
            repository.set_candidate_status(candidate["id"], "rejected", profile)
            rejected += 1
        else:
            repository.set_candidate_status(candidate["id"], "promoted", profile)
    return {"researched": researched, "rejected": rejected, "failed": failed}
