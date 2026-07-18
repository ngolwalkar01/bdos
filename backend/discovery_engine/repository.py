from datetime import datetime, timezone

from services.database import get_database_client


class DiscoveryRepository:
    """Database access for discovery domain objects."""

    def __init__(self, user_id):
        self.user_id = user_id
        self.client = get_database_client()

    def overview(self):
        response = self.client.table("opportunities").select("id,status").eq("user_id", self.user_id).execute()
        rows = response.data or []
        return {"total":len(rows),"new":sum(x.get("status")=="new" for x in rows),"saved":sum(x.get("status")=="saved" for x in rows),"ignored":sum(x.get("status")=="ignored" for x in rows)}

    def recent_opportunities(self, limit=12):
        response = (self.client.table("opportunities").select("*,opportunity_scores(score,confidence)")
            .eq("user_id",self.user_id).in_("status", ["saved","qualified"]).neq("source","Public Web").order("discovered_at",desc=True).limit(limit).execute())
        return response.data or []

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
        payload=[{"user_id":self.user_id,"discovery_run_id":run_id,**item} for item in opportunities]
        return self.client.table("opportunities").upsert(payload,on_conflict="user_id,source,source_url").execute().data or []

    def upsert_candidates(self, run_id, candidates):
        if not candidates:
            return []
        payload=[{"user_id":self.user_id,"discovery_run_id":run_id,**item} for item in candidates]
        return self.client.table("discovery_candidates").upsert(payload,on_conflict="user_id,source,source_url").execute().data or []

    def finish_run(self, run_id, status, count, errors):
        return self.client.table("discovery_runs").update({"status":status,"discovered_count":count,"errors":errors,"completed_at":datetime.now(timezone.utc).isoformat()}).eq("id",run_id).execute().data
