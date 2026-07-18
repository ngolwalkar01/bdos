import streamlit as st

from backend.discovery_engine.repository import DiscoveryRepository
from backend.discovery_engine.strategy import generate_discovery_strategy
from services.database import get_business_dna_profile


def render_home(user):
    first_name = (user.get("full_name") or "there").split()[0]
    st.markdown('<span class="bdos-eyebrow">BusinessDev OS</span>', unsafe_allow_html=True)
    st.title(f"Good morning, {first_name}")
    st.caption("Your opportunity intelligence workspace")
    try:
        overview = DiscoveryRepository(user["id"]).overview()
        dna = get_business_dna_profile(user["id"])
    except Exception as error:
        st.error("The Discovery Foundation database migration is required.")
        st.code(str(error))
        return
    columns = st.columns(4)
    columns[0].metric("Business DNA", "Complete" if dna.get("profile") else "Missing")
    columns[1].metric("Today's Opportunities", overview["new"])
    columns[2].metric("Saved", overview["saved"])
    columns[3].metric("Total Discovered", overview["total"])
    st.markdown("### Recommended opportunities")
    st.info("Your first recommendations will appear after a Discovery Strategy is generated and run.")


def _render_strategy_list(label, values):
    with st.container(border=True):
        st.markdown(f"#### {label}")
        st.markdown(" · ".join(values)) if values else st.caption("Not specified")


def render_discover(user, openai_client):
    st.markdown('<span class="bdos-eyebrow">Discovery Engine</span>', unsafe_allow_html=True)
    st.title("Discover opportunities")
    st.write("BusinessDev OS builds this strategy directly from your Business DNA.")
    try:
        repository = DiscoveryRepository(user["id"])
        active = repository.active_strategy()
        dna = get_business_dna_profile(user["id"])
        opportunities = repository.recent_opportunities()
    except Exception as error:
        st.error("The Discovery Foundation database migration is required.")
        st.code(str(error))
        return
    strategy = active.get("strategy") or {}
    label = "Regenerate Discovery Strategy" if strategy else "Generate Discovery Strategy"
    if st.button(label, type="secondary" if strategy else "primary", use_container_width=True):
        if not dna.get("profile"):
            st.error("Generate your Business DNA before creating a Discovery Strategy.")
        else:
            try:
                with st.spinner("Building a focused strategy from your Business DNA..."):
                    repository.save_strategy(generate_discovery_strategy(openai_client, dna))
                st.rerun()
            except Exception as error:
                st.error("Your Discovery Strategy could not be generated.")
                st.code(str(error))
    if strategy:
        st.caption(f"Active strategy v{active.get('version',1)} · {len(strategy.get('search_queries',[]))} discovery queries")
        left,right=st.columns(2)
        with left:
            _render_strategy_list("Industries",strategy.get("industries"))
            _render_strategy_list("Business Models",strategy.get("business_models"))
            _render_strategy_list("Countries",strategy.get("countries"))
            _render_strategy_list("Decision Makers",strategy.get("decision_makers"))
        with right:
            _render_strategy_list("Keywords",strategy.get("keywords"))
            _render_strategy_list("Company Sizes",strategy.get("company_sizes"))
            _render_strategy_list("Opportunity Titles",strategy.get("job_titles"))
            _render_strategy_list("Priority Sources",strategy.get("priority_sources"))
        with st.expander(f"Search queries ({len(strategy.get('search_queries',[]))})"):
            for query in strategy.get("search_queries",[]):
                st.code(query)
        with st.expander("Negative keywords"):
            st.write(" · ".join(strategy.get("negative_keywords",[])) or "None")
    else:
        st.info("Generate a strategy to translate your Business DNA into discovery targets and queries.")
    st.divider()
    st.markdown("### Discovered opportunities")
    if not opportunities:
        st.info("No opportunities yet. Multi-source discovery arrives in Phase 2C.")
        return
    for opportunity in opportunities:
        with st.container(border=True):
            st.subheader(opportunity.get("company_name") or "Unknown company")
            st.write(opportunity.get("title") or "Opportunity")
            st.caption(f"{opportunity.get('source','')} - {opportunity.get('country') or 'Location unknown'}")


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
        ("Identity", "identity"), ("Recommended Positioning", "recommended_positioning"),
        ("Skills", "skills"), ("Industries", "industries"),
        ("Ideal Opportunities", "ideal_opportunities"), ("Writing Style", "writing_style"),
    ]:
        with st.container(border=True):
            st.markdown(f"#### {label}")
            st.write(profile.get(key) or "Not available")


def render_coming_soon(section):
    st.title(section)
    st.info("Coming soon in the frozen V1 roadmap.")
