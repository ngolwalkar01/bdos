from backend.discovery_engine.adapters import discover_public_web_candidates, discover_remoteok, discover_remotive
from backend.qualification_engine.direct_listing import qualify_direct_listings

SOURCES = ("Public Web", "Remotive", "RemoteOK")


def run_discovery(repository, active_strategy, tavily_client, openai_client, business_dna):
    strategy = active_strategy.get("strategy") or {}
    if not strategy:
        raise ValueError("An active Discovery Strategy is required.")
    run = repository.start_run(active_strategy["id"], list(SOURCES))
    results, errors = [], []
    try:
        candidates = discover_public_web_candidates(strategy, tavily_client)
        repository.upsert_candidates(run["id"], candidates)
    except Exception as error:
        errors.append({"source": "Public Web", "message": str(error)})
    for source, adapter in (("Remotive", lambda: discover_remotive(strategy)), ("RemoteOK", lambda: discover_remoteok(strategy))):
        try:
            results.extend(adapter())
        except Exception as error:
            errors.append({"source": source, "message": str(error)})
    unique = {(item["source"].lower(), item["source_url"].rstrip("/").lower()): item for item in results if item.get("source_url")}
    direct_listings = list(unique.values())[:20]
    try:
        qualified = qualify_direct_listings(openai_client, business_dna, direct_listings)
        saved = repository.upsert_opportunities(run["id"], qualified)
    except Exception as error:
        errors.append({"source": "Business DNA Qualification", "message": str(error)})
        saved = []
    status = "partial" if errors and saved else "failed" if errors else "completed"
    repository.finish_run(run["id"], status, len(saved), errors)
    return {"run_id": run["id"], "status": status, "count": len(saved), "errors": errors}
