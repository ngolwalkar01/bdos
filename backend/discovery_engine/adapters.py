import re
import requests

from backend.discovery_engine.relevance import direct_listing_evidence

HEADERS = {"User-Agent": "BusinessDevOS/1.0 (+https://businessdevos.streamlit.app/)"}


def _text(value):
    return re.sub(r"<[^>]+>", " ", str(value or "")).strip()


def _matches(text, strategy):
    signals = [*strategy.get("keywords", []), *strategy.get("industries", []), *strategy.get("job_titles", [])]
    return any(signal.lower() in text.lower() for signal in signals if signal)


def discover_public_web_candidates(strategy, client, query_limit=5):
    items = []
    for query in strategy.get("search_queries", [])[:query_limit]:
        for result in client.search(query=query, search_depth="basic", max_results=5).get("results", []):
            if result.get("url"):
                title = result.get("title") or "Business opportunity"
                items.append({"title": title, "source": "Public Web", "source_url": result["url"], "snippet": result.get("content") or "", "raw_data": {"query": query, "search_score": result.get("score")}})
    return items


def discover_remotive(strategy, limit=100):
    response = requests.get("https://remotive.com/api/remote-jobs", headers=HEADERS, timeout=20)
    response.raise_for_status()
    items = []
    for job in response.json().get("jobs", [])[:limit]:
        searchable = " ".join(str(job.get(key) or "") for key in ("title", "company_name", "category", "tags", "description"))
        evidence = direct_listing_evidence(job.get("title"), job.get("tags"), job.get("description"), strategy)
        if evidence["accepted"] and job.get("url"):
            items.append({"title": job.get("title") or "Remote opportunity", "company_name": job.get("company_name") or "Unknown company", "source": "Remotive", "source_url": job["url"], "opportunity_type": job.get("job_type") or "Remote Job", "country": job.get("candidate_required_location"), "summary": _text(job.get("description"))[:1200], "external_key": str(job.get("id") or job["url"]), "raw_data": {"category": job.get("category"), "tags": job.get("tags", []), "relevance_evidence": evidence}})
    return items


def discover_remoteok(strategy, limit=100):
    response = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=20)
    response.raise_for_status()
    payload = response.json()
    jobs = payload[1:] if payload and "legal" in payload[0] else payload
    items = []
    for job in jobs[:limit]:
        searchable = " ".join(str(job.get(key) or "") for key in ("position", "company", "tags", "description", "location"))
        url = job.get("url") or (f"https://remoteok.com/remote-jobs/{job.get('id')}" if job.get("id") else None)
        evidence = direct_listing_evidence(job.get("position"), job.get("tags"), job.get("description"), strategy)
        if evidence["accepted"] and url:
            items.append({"title": job.get("position") or "Remote opportunity", "company_name": job.get("company") or "Unknown company", "source": "RemoteOK", "source_url": url, "opportunity_type": "Remote Job", "country": job.get("location"), "summary": _text(job.get("description"))[:1200], "external_key": str(job.get("id") or url), "raw_data": {"tags": job.get("tags", []), "salary_min": job.get("salary_min"), "salary_max": job.get("salary_max"), "relevance_evidence": evidence}})
    return items
