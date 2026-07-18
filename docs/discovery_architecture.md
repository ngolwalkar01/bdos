# Discovery Architecture

Business DNA is the source of truth for every discovery decision.

The Phase 2 pipeline is:

1. Discovery Strategy
2. Discovery Run
3. Opportunity
4. Research Profile
5. Qualification
6. Explainable Opportunity Score

The `backend` package owns domain logic and persistence. The `frontend` package
only renders state and invokes backend services. Source adapters, AI prompts,
qualification rules, and scoring rules will be added in their corresponding
engine packages in later Phase 2 increments.

Raw source data, research evidence, engine versions, and scoring breakdowns are
stored so every recommendation remains traceable and explainable.
