from backend.discovery_engine.adapters import discover_public_web, discover_remoteok, discover_remotive

SOURCES = ("Public Web", "Remotive", "RemoteOK")


def run_discovery(repository, active_strategy, tavily_client):
    strategy = active_strategy.get("strategy") or {}
    if not strategy:
        raise ValueError("An active Discovery Strategy is required.")
    run = repository.start_run(active_strategy["id"], list(SOURCES))
    results, errors = [], []
    for source, adapter in (("Public Web", lambda: discover_public_web(strategy, tavily_client)), ("Remotive", lambda: discover_remotive(strategy)), ("RemoteOK", lambda: discover_remoteok(strategy))):
        try:
            results.extend(adapter())
        except Exception as error:
            errors.append({"source": source, "message": str(error)})
    unique = {(item["source"].lower(), item["source_url"].rstrip("/").lower()): item for item in results if item.get("source_url")}
    saved = repository.upsert_opportunities(run["id"], list(unique.values()))
    status = "partial" if errors and saved else "failed" if errors else "completed"
    repository.finish_run(run["id"], status, len(saved), errors)
    return {"run_id": run["id"], "status": status, "count": len(saved), "errors": errors}
