import streamlit as st

from backend.discovery_engine.repository import DiscoveryRepository
from backend.discovery_engine.strategy import generate_discovery_strategy
from backend.discovery_engine.service import run_discovery
from backend.research_engine.service import research_candidates
from backend.qualification_engine.candidate import qualify_researched_candidates
from backend.scoring_engine.service import score_qualified_opportunities
from services.database import get_business_dna_profile


FEEDBACK_REASONS = {
    "Wrong skill match": "wrong_skill",
    "Wrong industry": "wrong_industry",
    "Wrong opportunity type": "wrong_opportunity_type",
    "Location mismatch": "location_mismatch",
    "Budget mismatch": "budget_mismatch",
    "Evidence is too weak": "weak_evidence",
    "Not an actual opportunity": "not_an_opportunity",
    "Opportunity is already closed": "already_closed",
    "Other": "other",
}


def ensure_strategy(repository, client, dna):
    active = repository.active_strategy()
    if active:
        return active
    if not dna.get("profile"):
        raise RuntimeError("Business DNA is required before opportunity discovery can start.")
    strategy = generate_discovery_strategy(client, dna)
    return repository.save_strategy(strategy)


def render_home(user, openai_client):
    first_name = (user.get("full_name") or "there").split()[0]
    st.markdown('<span class="bdos-eyebrow">BusinessDev OS</span>', unsafe_allow_html=True)
    st.title(f"Good morning, {first_name}")
    st.caption("Your opportunity intelligence workspace")
    try:
        repository = DiscoveryRepository(user["id"])
        overview = repository.overview()
        dna = get_business_dna_profile(user["id"])
        if not repository.active_strategy() and dna.get("profile") and openai_client:
            with st.spinner("Preparing your private opportunity discovery profile..."):
                ensure_strategy(repository, openai_client, dna)
    except Exception as error:
        st.error("Your opportunity workspace could not be prepared.")
        st.code(str(error))
        return
    columns = st.columns(4)
    columns[0].metric("Business DNA", "Complete" if dna.get("profile") else "Missing")
    columns[1].metric("Today's Opportunities", overview["new"])
    columns[2].metric("Saved", overview["saved"])
    columns[3].metric("Total Discovered", overview["total"])
    st.markdown("### Recommended opportunities")
    st.info("Your highest-value opportunities will appear here as discovery runs complete.")


def render_opportunities(user, openai_client, tavily_client):
    st.markdown('<span class="bdos-eyebrow">Opportunity Feed</span>', unsafe_allow_html=True)
    st.title("Opportunities")
    st.write("Relevant opportunities selected from your Business DNA, preferences, and experience.")
    view = st.radio("Opportunity view", ["For you", "Saved"], horizontal=True, label_visibility="collapsed")
    try:
        repository = DiscoveryRepository(user["id"])
        dna = get_business_dna_profile(user["id"])
        active_strategy = repository.active_strategy()
        if not active_strategy:
            with st.spinner("Preparing your opportunity discovery profile..."):
                active_strategy = ensure_strategy(repository, openai_client, dna)
        statuses = ["saved"] if view == "Saved" else ["qualified"]
        opportunities = repository.recent_opportunities(statuses=statuses)
    except Exception as error:
        st.error("Your opportunity feed could not be prepared.")
        st.code(str(error))
        return
    if st.button("Find new opportunities", type="primary", use_container_width=True):
        try:
            with st.spinner("Searching selected sources and removing duplicates..."):
                result = run_discovery(repository, active_strategy, tavily_client, openai_client, dna)
                research = research_candidates(repository, tavily_client, openai_client, dna, limit=5)
                qualification_counts = qualify_researched_candidates(repository, openai_client, dna, limit=10)
                scoring = score_qualified_opportunities(repository)
            if result["errors"]:
                st.warning(f"Found {result['count']} opportunities. Some sources were unavailable.")
            else:
                st.success(f"Found and stored {result['count']} opportunities.")
            if research["researched"]:
                st.caption(f"Privately researched {research['researched']} web candidates; rejected {research['rejected']} non-target/service-provider results.")
            if any(qualification_counts.values()):
                st.caption(
                    f"Private qualification: {qualification_counts['qualified']} qualified, "
                    f"{qualification_counts['needs_review']} need review, and {qualification_counts['rejected']} rejected."
                )
            if scoring["scored"]:
                st.caption(f"Scored and ranked {scoring['scored']} qualified opportunities.")
            st.rerun()
        except Exception as error:
            st.error("Opportunity discovery could not be completed.")
            st.code(str(error))
    st.caption("Only direct listings that pass strict Business DNA qualification at 80+ are shown. Raw web candidates are researched privately.")
    if not opportunities:
        if view == "Saved":
            st.info("You have not saved any opportunities yet.")
        else:
            st.info("No opportunities yet. Run discovery to build your personalized feed.")
        return
    for opportunity in opportunities:
        with st.container(border=True):
            scores = opportunity.get("opportunity_scores") or []
            score_record = scores[0] if scores else {}
            score = score_record.get("score")
            title = opportunity.get("company_name") or "Unknown company"
            st.subheader(f"{title}{f' · {score}/100' if score is not None else ''}")
            st.write(opportunity.get("title") or "Opportunity")
            st.caption(f"{opportunity.get('source','')} - {opportunity.get('country') or 'Location unknown'}")
            raw_data = opportunity.get("raw_data") or {}
            qualification = raw_data.get("business_dna_qualification") or raw_data.get("candidate_qualification") or {}
            if qualification:
                st.markdown(f"**Business DNA fit: {qualification.get('fit_score', qualification.get('score', 0))}/100**")
                for reason in qualification.get("fit_reasons", qualification.get("reasons", [])):
                    st.write(f"✓ {reason}")
            if score_record.get("confidence"):
                st.caption(f"Ranking confidence: {score_record['confidence'].title()}")
                with st.expander("Why this ranks here"):
                    breakdown = score_record.get("breakdown") or {}
                    for label, key in (
                        ("Business DNA fit", "business_dna_fit"),
                        ("Opportunity strength", "opportunity_strength"),
                        ("Evidence quality", "evidence_quality"),
                        ("Urgency", "urgency"),
                        ("Commercial fit", "commercial_fit"),
                    ):
                        st.write(f"{label}: {breakdown.get(key, 0)} points")
                    for signal in score_record.get("positive_signals") or []:
                        st.write(f"? {signal}")
                    for risk in score_record.get("risk_signals") or []:
                        st.write(f"Risk: {risk}")
            action_columns = st.columns([2, 1, 1])
            if opportunity.get("source_url"):
                action_columns[0].link_button(
                    f"View on {opportunity.get('source') or 'source'}", opportunity["source_url"],
                    use_container_width=True,
                )
            if opportunity.get("status") == "saved":
                if action_columns[1].button("Return to feed", key=f"restore_{opportunity['id']}", use_container_width=True):
                    try:
                        repository.set_opportunity_feedback(opportunity["id"], "restored")
                        st.rerun()
                    except Exception as error:
                        st.error(f"The opportunity could not be restored: {error}")
            else:
                if action_columns[1].button("Save", key=f"save_{opportunity['id']}", use_container_width=True):
                    try:
                        repository.set_opportunity_feedback(opportunity["id"], "saved")
                        st.rerun()
                    except Exception as error:
                        st.error(f"The opportunity could not be saved: {error}")
                with action_columns[2].popover("Not relevant", use_container_width=True):
                    with st.form(key=f"feedback_{opportunity['id']}"):
                        reason_label = st.selectbox("What was wrong?", list(FEEDBACK_REASONS))
                        details = st.text_input("Optional detail", max_chars=500)
                        submitted = st.form_submit_button("Remove opportunity", use_container_width=True)
                    if submitted:
                        try:
                            repository.set_opportunity_feedback(
                                opportunity["id"], "not_relevant", FEEDBACK_REASONS[reason_label], details
                            )
                            st.rerun()
                        except Exception as error:
                            st.error(f"Your feedback could not be saved: {error}")


def render_business_dna(user):
    st.title("Business DNA")
    try:
        record = get_business_dna_profile(user["id"])
    except Exception as error:
        st.error("Your Business DNA could not be loaded.")
        st.code(str(error))
        return
    profile = record.get("profile") or {}
    if not profile:
        st.info("No Business DNA has been generated yet.")
        return
    for label, key in [
        ("Identity","identity"),("Recommended Positioning","recommended_positioning"),
        ("Skills","skills"),("Industries","industries"),
        ("Ideal Opportunities","ideal_opportunities"),("Writing Style","writing_style"),
    ]:
        with st.container(border=True):
            st.markdown(f"#### {label}")
            st.write(profile.get(key) or "Not available")


def render_settings(user, openai_client):
    st.markdown('<span class="bdos-eyebrow">Preferences</span>', unsafe_allow_html=True)
    st.title("Settings")
    st.write("Manage your account and opportunity-discovery preferences.")
    try:
        repository = DiscoveryRepository(user["id"])
        active = repository.active_strategy()
        dna = get_business_dna_profile(user["id"])
    except Exception as error:
        st.error("Settings could not be loaded.")
        st.code(str(error))
        return
    with st.expander("Advanced discovery settings"):
        st.caption("Normally managed automatically from your Business DNA.")
        strategy = active.get("strategy") or {}
        if strategy:
            st.write(f"Discovery profile version: {active.get('version',1)}")
            st.write(f"Configured search paths: {len(strategy.get('search_queries',[]))}")
            st.write("Priority sources: " + ", ".join(strategy.get("priority_sources",[])))
            if st.checkbox("Show technical discovery queries"):
                for query in strategy.get("search_queries",[]):
                    st.code(query)
            candidate_counts = repository.candidate_overview()
            st.markdown("#### Private research pipeline")
            columns = st.columns(3)
            columns[0].metric("Awaiting research", candidate_counts["pending"])
            columns[1].metric("Target businesses", candidate_counts["researched"])
            columns[2].metric("Rejected noise", candidate_counts["rejected"])
            qualification_counts = repository.qualification_overview()
            st.markdown("#### Private qualification gate")
            columns = st.columns(3)
            columns[0].metric("Qualified", qualification_counts["qualified"])
            columns[1].metric("Needs review", qualification_counts["needs_review"])
            columns[2].metric("Rejected", qualification_counts["rejected"])
        else:
            st.info("The discovery profile will be created automatically.")
        if st.button("Regenerate discovery profile", use_container_width=True):
            try:
                with st.spinner("Refreshing your discovery profile..."):
                    repository.save_strategy(generate_discovery_strategy(openai_client, dna))
                st.rerun()
            except Exception as error:
                st.error("The discovery profile could not be regenerated.")
                st.code(str(error))
