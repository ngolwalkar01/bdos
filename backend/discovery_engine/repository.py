from services.database import get_database_client


class DiscoveryRepository:
    """Database access for discovery domain objects."""

    def __init__(self, user_id):
        self.user_id = user_id
        self.client = get_database_client()

    def overview(self):
        response = (
            self.client.table("opportunities").select("id,status")
            .eq("user_id", self.user_id).execute()
        )
        rows = response.data or []
        return {
            "total": len(rows),
            "new": sum(row.get("status") == "new" for row in rows),
            "saved": sum(row.get("status") == "saved" for row in rows),
            "ignored": sum(row.get("status") == "ignored" for row in rows),
        }

    def recent_opportunities(self, limit=12):
        response = (
            self.client.table("opportunities")
            .select("*,opportunity_scores(score,confidence)")
            .eq("user_id", self.user_id)
            .order("discovered_at", desc=True).limit(limit).execute()
        )
        return response.data or []
