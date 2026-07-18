import streamlit as st

from backend.discovery_engine.repository import DiscoveryRepository
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


def render_discover(user):
    st.markdown('<span class="bdos-eyebrow">Discovery Engine</span>', unsafe_allow_html=True)
    st.title("Discover opportunities")
    st.write("BusinessDev OS will build a discovery strategy directly from your Business DNA.")
    try:
        opportunities = DiscoveryRepository(user["id"]).recent_opportunities()
    except Exception as error:
        st.error("The Discovery Foundation database migration is required.")
        st.code(str(error))
        return
    if not opportunities:
        st.info("No opportunities yet. Discovery Strategy generation arrives in Phase 2B.")
        return
    for opportunity in opportunities:
        with st.container(border=True):
            st.subheader(opportunity.get("company_name") or "Unknown company")
            st.write(opportunity.get("title") or "Opportunity")
            st.caption(f"{opportunity.get('source', '')} - {opportunity.get('country') or 'Location unknown'}")


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
