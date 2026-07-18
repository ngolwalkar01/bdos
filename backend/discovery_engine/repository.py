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
            .eq("user_id",self.user_id).order("discovered_at",desc=True).limit(limit).execute())
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
