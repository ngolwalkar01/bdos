ENGINE_VERSION = "opportunity-scoring-v1"


def _status(dimensions, name):
    return (dimensions.get(name) or {}).get("status")


def _evidence(dimensions, name):
    return (dimensions.get(name) or {}).get("evidence") or []


def score_opportunity(opportunity):
    raw = opportunity.get("raw_data") or {}
    qualification = raw.get("candidate_qualification") or raw.get("business_dna_qualification") or {}
    researched = bool(raw.get("candidate_qualification"))
    fit_score = int(qualification.get("score", qualification.get("fit_score", 0)) or 0)
    dimensions = qualification.get("dimensions") or {}
    profile = raw.get("research_profile") or {}

    dna_fit = round(max(0, min(100, fit_score)) * 0.45)
    if researched:
        signal_evidence = _evidence(dimensions, "opportunity_signal")
        opportunity_strength = 20 if _status(dimensions, "opportunity_signal") == "match" and signal_evidence else 0
        evidence_count = sum(len(_evidence(dimensions, name)) for name in dimensions)
        evidence_count += len(raw.get("research_evidence") or [])
        evidence_quality = min(15, evidence_count * 3)
        urgency_signals = [
            *(profile.get("hiring_signals") or []), *(profile.get("growth_signals") or []),
            *(profile.get("opportunity_signals") or []),
        ]
        urgency = min(10, len(urgency_signals) * 3)
        commercial_fit = 5 * sum(
            _status(dimensions, name) == "match" for name in ("opportunity_type_fit", "budget_fit")
        )
    else:
        opportunity_strength = 20
        evidence_quality = min(15, 5 + 3 * sum(bool(opportunity.get(key)) for key in ("source_url", "summary", "country")))
        urgency = 5
        commercial_fit = 5 if opportunity.get("opportunity_type") else 0

    risks = qualification.get("risk_signals") or qualification.get("mismatch_reasons") or []
    hard_mismatches = qualification.get("hard_mismatches") or []
    risk_penalty = min(20, len(risks) * 3 + len(hard_mismatches) * 8)
    breakdown = {
        "business_dna_fit": dna_fit, "opportunity_strength": opportunity_strength,
        "evidence_quality": evidence_quality, "urgency": urgency,
        "commercial_fit": commercial_fit, "risk_penalty": -risk_penalty,
    }
    score = max(0, min(100, sum(breakdown.values())))
    positives = list(qualification.get("fit_reasons") or [])
    if opportunity_strength:
        positives.append("Concrete opportunity signal supported by evidence")
    if urgency:
        positives.append("Current activity indicates timely potential")
    known = sum(value > 0 for key, value in breakdown.items() if key != "risk_penalty")
    confidence = "high" if known >= 4 and evidence_quality >= 9 else "medium" if known >= 3 else "low"
    return {
        "score": score, "confidence": confidence, "breakdown": breakdown,
        "positive_signals": list(dict.fromkeys(positives))[:5],
        "risk_signals": risks[:5], "engine_version": ENGINE_VERSION,
    }


def score_qualified_opportunities(repository, limit=100):
    opportunities = repository.opportunities_for_scoring(ENGINE_VERSION, limit)
    for opportunity in opportunities:
        repository.save_opportunity_score(opportunity["id"], score_opportunity(opportunity))
    return {"scored": len(opportunities)}
