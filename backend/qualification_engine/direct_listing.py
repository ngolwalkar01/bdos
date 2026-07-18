import json


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


def qualify_direct_listings(client, business_dna, listings, threshold=80):
    if not listings:
        return []
    review_items = [
        {
            "index": index,
            "title": item.get("title"),
            "company": item.get("company_name"),
            "type": item.get("opportunity_type"),
            "location": item.get("country"),
            "summary": item.get("summary"),
            "tags": (item.get("raw_data") or {}).get("tags", []),
        }
        for index, item in enumerate(listings)
    ]
    prompt = f"""
You are the strict qualification gate for BusinessDev OS. Decide whether each direct
listing is genuinely worth showing to this specific professional. Keyword overlap is
not enough. Require concrete alignment with the person's positioning, primary skills,
solved business problems, preferred opportunity types, industries, location/remote
preferences, and commercial fit when known.

Reject listings that are generic, primarily outside the Business DNA, require a
different profession, or have insufficient evidence. Never fill gaps with assumptions.
Quality is more important than quantity. A valid result may contain zero qualified listings.

BUSINESS DNA:
{json.dumps(business_dna, indent=2, default=str)}

DIRECT LISTINGS:
{json.dumps(review_items, indent=2, default=str)}

Return only valid JSON:
{{"decisions":[{{"index":0,"qualified":false,"fit_score":0,
"fit_reasons":[],"mismatch_reasons":["specific reason"],"summary":"one sentence"}}]}}

Score 80 or higher only for strong, evidence-supported fit. Return one decision for
every index and do not change the index.
"""
    response = client.responses.create(model="gpt-4.1-mini", input=prompt)
    payload = _parse_json(response.output_text)
    decisions = {
        decision.get("index"): decision
        for decision in payload.get("decisions", [])
        if isinstance(decision, dict) and isinstance(decision.get("index"), int)
    }
    qualified = []
    for index, listing in enumerate(listings):
        decision = decisions.get(index, {})
        score = int(decision.get("fit_score") or 0)
        accepted = decision.get("qualified") is True and score >= threshold
        listing["raw_data"] = {
            **(listing.get("raw_data") or {}),
            "business_dna_qualification": {**decision, "accepted": accepted, "threshold": threshold},
        }
        if accepted:
            listing["status"] = "qualified"
            qualified.append(listing)
    return qualified
