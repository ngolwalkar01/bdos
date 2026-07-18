ACTIONS = {"saved", "not_relevant", "restored"}
REASONS = {
    "wrong_skill", "wrong_industry", "wrong_opportunity_type", "location_mismatch",
    "budget_mismatch", "weak_evidence", "not_an_opportunity", "already_closed", "other",
}


def build_feedback(opportunity_id, user_id, action, reason=None, details=None):
    if action not in ACTIONS:
        raise ValueError("Unsupported opportunity feedback action.")
    if reason is not None and reason not in REASONS:
        raise ValueError("Unsupported opportunity feedback reason.")
    if action == "not_relevant" and not reason:
        raise ValueError("A reason is required when an opportunity is not relevant.")
    return {
        "opportunity_id": opportunity_id, "user_id": user_id, "action": action,
        "reason": reason, "details": (details or "").strip()[:500] or None,
    }
