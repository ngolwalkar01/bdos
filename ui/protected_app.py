from urllib.parse import urlparse
from zoneinfo import available_timezones

import streamlit as st

from services.database import advance_onboarding, get_basic_profile, save_basic_profile, upload_resume


STEPS = [
    "Basic Profile",
    "Professional Experience",
    "Business Experience",
    "Ideal Opportunity",
    "Decision Makers",
    "Communication Style",
    "Business DNA Review",
]

NAVIGATION = [
    "Dashboard",
    "Discover Businesses",
    "My Companies",
    "Decision Makers",
    "Outreach",
    "Freelance Jobs",
    "Analytics",
    "Settings",
]


def valid_url(value, required_host=None):
    if not value:
        return True
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    return not required_host or required_host in parsed.netloc.lower()


def render_progress(completed):
    completed = max(0, min(int(completed or 0), 7))
    st.progress(completed / 7, text=f"Onboarding: {completed} of 7 steps completed")
    columns = st.columns(7)
    for number, (column, label) in enumerate(zip(columns, STEPS), start=1):
        column.markdown(f"**{'✓' if number <= completed else number}**")
        column.caption(label)


def render_basic_profile(user, existing):
    st.header("Step 1 - Basic Profile")
    st.write("Create the professional identity used throughout your Business DNA.")

    timezones = sorted(available_timezones())
    saved_timezone = existing.get("preferred_timezone") or "Asia/Kolkata"
    timezone_index = timezones.index(saved_timezone) if saved_timezone in timezones else 0

    with st.form("basic_profile_form"):
        full_name = st.text_input(
            "Full Name *", value=existing.get("full_name") or user.get("full_name") or ""
        )
        headline = st.text_input(
            "Professional Headline *",
            value=existing.get("professional_headline") or "",
            placeholder="Example: WooCommerce Engineer | Subscription Commerce Specialist",
        )

        role_column, experience_column = st.columns(2)
        with role_column:
            role = st.text_input("Current Role *", value=existing.get("current_job_role") or "")
        with experience_column:
            years = st.number_input(
                "Years of Experience *",
                min_value=0,
                max_value=80,
                value=int(existing.get("years_experience") or 0),
                step=1,
            )

        country_column, timezone_column = st.columns(2)
        with country_column:
            country = st.text_input("Country *", value=existing.get("country") or "")
        with timezone_column:
            timezone = st.selectbox(
                "Preferred Timezone *", timezones, index=timezone_index
            )

        linkedin = st.text_input(
            "LinkedIn Profile (Optional)",
            value=existing.get("linkedin_url") or "",
            placeholder="https://www.linkedin.com/in/your-profile",
        )
        portfolio = st.text_input(
            "Portfolio Website (Optional)",
            value=existing.get("portfolio_url") or "",
            placeholder="https://yourwebsite.com",
        )
        resume = st.file_uploader(
            "Resume Upload (Optional)",
            type=["pdf", "docx"],
            max_upload_size=10,
            help="PDF or DOCX, up to 10 MB. Stored privately.",
        )
        if existing.get("resume_filename"):
            st.caption(
                f"Current resume: {existing['resume_filename']}. "
                "Upload another file only to replace it."
            )

        draft_column, continue_column = st.columns(2)
        with draft_column:
            save_draft = st.form_submit_button("Save Draft", use_container_width=True)
        with continue_column:
            save_continue = st.form_submit_button(
                "Save & Continue", type="primary", use_container_width=True
            )

    if not save_draft and not save_continue:
        return

    errors = []
    if save_continue:
        required = {
            "Full Name": full_name,
            "Professional Headline": headline,
            "Current Role": role,
            "Country": country,
        }
        errors.extend(
            f"{label} is required." for label, value in required.items() if not value.strip()
        )
    if not valid_url(linkedin, "linkedin.com"):
        errors.append("LinkedIn Profile must be a valid linkedin.com URL.")
    if not valid_url(portfolio):
        errors.append("Portfolio Website must be a valid http:// or https:// URL.")
    if resume and resume.size > 10 * 1024 * 1024:
        errors.append("Resume must be 10 MB or smaller.")

    if errors:
        for error in errors:
            st.error(error)
        return

    profile = {
        "full_name": full_name.strip() or None,
        "professional_headline": headline.strip() or None,
        "current_job_role": role.strip() or None,
        "years_experience": int(years),
        "country": country.strip() or None,
        "preferred_timezone": timezone,
        "linkedin_url": linkedin.strip() or None,
        "portfolio_url": portfolio.strip() or None,
    }

    try:
        if resume:
            profile.update(upload_resume(user["id"], resume))
        save_basic_profile(user["id"], profile)

        if save_continue:
            advance_onboarding(user["id"], 1)
            st.session_state["edit_basic_profile"] = False
            st.success("Basic Profile completed.")
            st.rerun()
        else:
            st.success("Draft saved.")
    except Exception as error:
        st.error("Your Basic Profile could not be saved.")
        st.code(str(error))


def render_onboarding(user):
    current_step = int(user.get("onboarding_step") or 0)
    editing = st.session_state.get("edit_basic_profile", False)

    st.title("Professional Onboarding")
    render_progress(current_step)

    try:
        existing = get_basic_profile(user["id"])
    except Exception as error:
        st.error("Phase 2 database migration is required before onboarding can continue.")
        st.code(str(error))
        if st.button("Log out"):
            st.logout()
        return

    if current_step >= 1 and not editing:
        st.success("Step 1 - Basic Profile is complete.")
        st.header("Step 2 - Professional Experience")
        st.info("Coming in Phase 3")

        edit_column, logout_column = st.columns(2)
        with edit_column:
            if st.button("Edit Basic Profile", use_container_width=True):
                st.session_state["edit_basic_profile"] = True
                st.rerun()
        with logout_column:
            if st.button("Log out", use_container_width=True):
                st.logout()
        return

    render_basic_profile(user, existing)

    if editing and st.button("Cancel editing"):
        st.session_state["edit_basic_profile"] = False
        st.rerun()

    st.divider()
    if st.button("Log out"):
        st.logout()


def render_dashboard(user):
    with st.sidebar:
        st.markdown(f"### {user.get('full_name') or 'User'}")
        selected = st.radio("Navigation", NAVIGATION, label_visibility="collapsed")
        st.divider()
        if st.button("Log out", use_container_width=True):
            st.logout()

    if selected == "Dashboard":
        st.title("Dashboard")
        st.write("Your personalized opportunity dashboard is being prepared.")
        st.info("Complete onboarding to generate your Business DNA.")
        return

    st.title(selected)
    st.info("Coming soon")