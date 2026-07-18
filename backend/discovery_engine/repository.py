from datetime import datetime, timezone

from services.database import get_database_client
from backend.learning_engine.feedback import build_feedback


class DiscoveryRepository:
    """Database access for discovery domain objects."""

    def __init__(self, user_id):
        self.user_id = user_id
        self.client = get_database_client()

    def overview(self):
        response = self.client.table("opportunities").select("id,status").eq("user_id", self.user_id).execute()
        rows = response.data or []
        return {"total":len(rows),"new":sum(x.get("status")=="new" for x in rows),"saved":sum(x.get("status")=="saved" for x in rows),"ignored":sum(x.get("status")=="ignored" for x in rows)}

    def recent_opportunities(self, statuses=None, limit=12):
        statuses = statuses or ["qualified"]
        response = (self.client.table("opportunities").select("*,opportunity_scores(score,confidence,breakdown,positive_signals,risk_signals)")
            .eq("user_id",self.user_id).in_("status", statuses).neq("source","Public Web").execute())
        rows = response.data or []
        rows.sort(key=lambda item: (
            (item.get("opportunity_scores") or [{}])[0].get("score", -1),
            item.get("discovered_at") or "",
        ), reverse=True)
        return rows[:limit]

    def opportunities_for_scoring(self, engine_version, limit=100):
        response = (self.client.table("opportunities").select("*,opportunity_scores(engine_version)")
            .eq("user_id", self.user_id).eq("status", "qualified").neq("source", "Public Web")
            .order("discovered_at", desc=True).limit(limit).execute())
        return [row for row in (response.data or []) if not (row.get("opportunity_scores") or [])
            or row["opportunity_scores"][0].get("engine_version") != engine_version]

    def save_opportunity_score(self, opportunity_id, score):
        payload = {"opportunity_id": opportunity_id, **score}
        return self.client.table("opportunity_scores").upsert(payload, on_conflict="opportunity_id").execute().data or []

    def set_opportunity_feedback(self, opportunity_id, action, reason=None, details=None):
        feedback = build_feedback(opportunity_id, self.user_id, action, reason, details)
        status = {"saved": "saved", "not_relevant": "ignored", "restored": "qualified"}[action]
        owned = (self.client.table("opportunities").select("id")
            .eq("id", opportunity_id).eq("user_id", self.user_id).limit(1).execute())
        if not owned.data:
            raise RuntimeError("The opportunity could not be found.")
        self.client.table("opportunity_feedback").insert(feedback).execute()
        response = (self.client.table("opportunities").update({"status": status})
            .eq("id", opportunity_id).eq("user_id", self.user_id).execute())
        if not response.data:
            raise RuntimeError("The opportunity could not be updated.")
        return response.data[0]

    def active_strategy(self):
        response = (self.client.table("discovery_strategies").select("*").eq("user_id",self.user_id)
            .eq("status","active").order("version",desc=True).limit(1).execute())
        return response.data[0] if response.data else {}

    def save_strategy(self, strategy, prompt_version="discovery-strategy-v1"):
        versions = (self.client.table("discovery_strategies").select("version").eq("user_id",self.user_id)
            .order("version",desc=True).limit(1).execute())
        version = versions.data[0]["version"] + 1 if versions.data else 1
        self.client.table("discovery_strategies").update({"status":"archived"}).eq("user_id",self.user_id).eq("status","active").execute()
        response = self.client.table("discovery_strategies").insert({"user_id":self.user_id,"version":version,"status":"active","strategy":strategy,"prompt_version":prompt_version}).execute()
        if not response.data:
            raise RuntimeError("The Discovery Strategy could not be saved.")
        return response.data[0]

    def start_run(self, strategy_id, sources):
        response = self.client.table("discovery_runs").insert({"user_id":self.user_id,"strategy_id":strategy_id,"status":"running","sources":sources,"started_at":datetime.now(timezone.utc).isoformat()}).execute()
        if not response.data:
            raise RuntimeError("The discovery run could not be started.")
        return response.data[0]

    def upsert_opportunities(self, run_id, opportunities):
        if not opportunities:
            return []
        protected = (self.client.table("opportunities").select("source,source_url,status")
            .eq("user_id", self.user_id).in_("status", ["saved", "ignored"]).execute())
        statuses = {(row["source"].lower(), row["source_url"].rstrip("/").lower()): row["status"] for row in (protected.data or [])}
        payload=[]
        for item in opportunities:
            key = (item["source"].lower(), item["source_url"].rstrip("/").lower())
            payload.append({"user_id":self.user_id,"discovery_run_id":run_id,**item,
                "status": statuses.get(key, item.get("status", "new"))})
        return self.client.table("opportunities").upsert(payload,on_conflict="user_id,source,source_url").execute().data or []

    def upsert_candidates(self, run_id, candidates):
        if not candidates:
            return []
        payload=[{"user_id":self.user_id,"discovery_run_id":run_id,**item} for item in candidates]
        return self.client.table("discovery_candidates").upsert(payload,on_conflict="user_id,source,source_url").execute().data or []

    def pending_candidates(self, limit=5):
        response=(self.client.table("discovery_candidates").select("id,source,source_url,title,snippet,raw_data")
            .eq("user_id",self.user_id).eq("status","pending").order("created_at",desc=True).limit(limit).execute())
        return response.data or []

    def save_candidate_research(self, candidate_id, status, profile, evidence, error, researched_at):
        response=self.client.table("candidate_research_profiles").upsert({"candidate_id":candidate_id,"status":status,"profile":profile,"evidence":evidence,"error_message":error,"researched_at":researched_at},on_conflict="candidate_id").execute()
        return response.data or []

    def set_candidate_status(self, candidate_id, status, classification):
        response=self.client.table("discovery_candidates").update({"status":status,"classification":classification}).eq("id",candidate_id).eq("user_id",self.user_id).execute()
        return response.data or []

    def candidate_overview(self):
        response=self.client.table("discovery_candidates").select("status").eq("user_id",self.user_id).execute()
        rows=response.data or []
        return {"pending":sum(x.get("status")=="pending" for x in rows),"rejected":sum(x.get("status")=="rejected" for x in rows),"researched":sum(x.get("status")=="promoted" for x in rows)}

    def researched_candidates_for_qualification(self, limit=10):
        candidates = (self.client.table("discovery_candidates")
            .select("id,discovery_run_id,source,source_url,title,snippet,raw_data")
            .eq("user_id", self.user_id).eq("status", "promoted")
            .order("updated_at", desc=True).limit(100).execute())
        candidate_rows = candidates.data or []
        if not candidate_rows:
            return []
        qualified = (self.client.table("candidate_qualifications").select("candidate_id")
            .in_("candidate_id", [row["id"] for row in candidate_rows]).execute())
        processed = {row["candidate_id"] for row in (qualified.data or [])}
        rows = [row for row in candidate_rows if row["id"] not in processed][:limit]
        if not rows:
            return []
        profiles = (self.client.table("candidate_research_profiles")
            .select("candidate_id,status,profile,evidence").in_("candidate_id", [row["id"] for row in rows])
            .eq("status", "completed").execute())
        by_candidate = {row["candidate_id"]: row for row in (profiles.data or [])}
        return [
            {**row, "research_profile": by_candidate[row["id"]].get("profile") or {},
             "research_evidence": by_candidate[row["id"]].get("evidence") or []}
            for row in rows if row["id"] in by_candidate
        ]

    def save_candidate_qualification(self, candidate_id, decision, engine_version):
        payload = {
            "candidate_id": candidate_id, "verdict": decision["verdict"],
            "score": decision["score"], "dimensions": decision.get("dimensions") or {},
            "reasons": decision.get("fit_reasons") or [], "risks": decision.get("risk_signals") or [],
            "missing_data": decision.get("missing_data") or [],
            "opportunity": decision.get("opportunity") or {}, "engine_version": engine_version,
        }
        return self.client.table("candidate_qualifications").upsert(payload, on_conflict="candidate_id").execute().data or []

    def promote_candidate(self, candidate, decision):
        profile = candidate.get("research_profile") or {}
        opportunity = decision.get("opportunity") or {}
        payload = {
            "user_id": self.user_id, "discovery_run_id": candidate.get("discovery_run_id"),
            "external_key": str(candidate["id"]),
            "title": opportunity.get("title") or candidate.get("title") or "Qualified opportunity",
            "company_name": profile.get("company_name") or candidate.get("title") or "Unknown company",
            "source": "Researched Company", "source_url": candidate["source_url"],
            "opportunity_type": opportunity.get("type") or "Business Opportunity",
            "country": profile.get("country"), "summary": opportunity.get("summary") or candidate.get("snippet"),
            "status": "qualified", "raw_data": {
                "research_profile": profile, "research_evidence": candidate.get("research_evidence") or [],
                "candidate_qualification": decision,
            },
        }
        return self.client.table("opportunities").upsert(payload, on_conflict="user_id,source,source_url").execute().data or []

    def qualification_overview(self):
        candidates = self.client.table("discovery_candidates").select("id").eq("user_id", self.user_id).execute()
        candidate_ids = [row["id"] for row in (candidates.data or [])]
        if not candidate_ids:
            return {"qualified": 0, "needs_review": 0, "rejected": 0}
        response = self.client.table("candidate_qualifications").select("verdict").in_("candidate_id", candidate_ids).execute()
        rows = response.data or []
        return {key: sum(row.get("verdict") == key for row in rows) for key in ("qualified", "needs_review", "rejected")}

    def finish_run(self, run_id, status, count, errors):
        return self.client.table("discovery_runs").update({"status":status,"discovered_count":count,"errors":errors,"completed_at":datetime.now(timezone.utc).isoformat()}).eq("id",run_id).execute().data
