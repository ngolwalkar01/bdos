from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class OpportunityStatus(StrEnum):
    NEW = "new"
    SAVED = "saved"
    IGNORED = "ignored"
    QUALIFIED = "qualified"
    REJECTED = "rejected"


class QualificationVerdict(StrEnum):
    QUALIFIED = "qualified"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


@dataclass(slots=True)
class Opportunity:
    title: str
    company_name: str
    source: str
    source_url: str
    opportunity_type: str | None = None
    country: str | None = None
    summary: str | None = None
    external_key: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)
