import re


GENERIC_SIGNALS = {
    "business", "company", "consulting", "contract", "expert", "hiring",
    "job", "remote", "services", "solutions", "specialist",
}


def normalize(value):
    return re.sub(r"[^a-z0-9+#.]+", " ", str(value or "").lower()).strip()


def meaningful_signals(strategy):
    values = [*strategy.get("keywords", []), *strategy.get("job_titles", [])]
    return list(dict.fromkeys(
        normalized for value in values
        if (normalized := normalize(value)) and normalized not in GENERIC_SIGNALS
    ))


def direct_listing_evidence(title, tags, description, strategy):
    signals = meaningful_signals(strategy)
    title_text = normalize(title)
    tag_text = normalize(" ".join(tags or []))
    description_text = normalize(description)
    title_hits = [signal for signal in signals if signal in title_text]
    tag_hits = [signal for signal in signals if signal in tag_text]
    description_hits = [signal for signal in signals if signal in description_text]
    accepted = bool(title_hits or tag_hits or len(description_hits) >= 2)
    return {
        "accepted": accepted,
        "title_matches": title_hits,
        "tag_matches": tag_hits,
        "description_matches": description_hits[:10],
        "reason": "direct_listing_with_strategy_evidence" if accepted else "insufficient_strategy_evidence",
    }
