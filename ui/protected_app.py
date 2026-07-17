from urllib.parse import urlparse
from zoneinfo import available_timezones

import streamlit as st

from services.database import (
    advance_onboarding,
    get_basic_profile,
    get_professional_experience,
    save_basic_profile,
    save_professional_experience,
    upload_resume,
)
from ui.theme import brand_wordmark


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
SKILL_OPTIONS = [
    "WordPress", "WooCommerce", "PHP", "Python", "JavaScript", "TypeScript",
    "SQL", "REST APIs", "GraphQL", "Ecommerce", "Subscription Commerce",
    "Business Automation", "API Integration", "System Architecture",
    "Performance Optimization", "Technical Consulting",
]

TECHNOLOGY_OPTIONS = [
    "MySQL", "PostgreSQL", "Redis", "Docker", "Git", "GitHub", "Node.js",
    "Stripe", "OpenAI API", "Tavily", "Elasticsearch", "Linux",
]

FRAMEWORK_OPTIONS = [
    "React", "Next.js", "Laravel", "Django", "FastAPI", "Flask", "Streamlit",
    "Express.js", "Vue.js", "Angular", "Tailwind CSS",
]

PLATFORM_OPTIONS = [
    "AWS", "Google Cloud", "Microsoft Azure", "Vercel", "Cloudflare",
    "Supabase", "Firebase", "Shopify", "HubSpot", "Salesforce",
]

CERTIFICATION_OPTIONS = [
    "AWS Certified", "Google Cloud Certified", "Microsoft Certified",
    "Scrum Master", "PMP", "HubSpot Certified", "Shopify Partner",
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
    items = []
    for number, label in enumerate(STEPS, start=1):
        state = "done" if number <= completed else ""
        if number == completed + 1:
            state = "active"
        marker = "&#10003;" if number <= completed else str(number)
        items.append(
            f'<div class="onboarding-step {state}">'
            f'<div class="step-dot">{marker}</div>'
            f"<span>{label}</span></div>"
        )

    st.markdown(
        '<div class="onboarding-progress">' + "".join(items) + "</div>",
        unsafe_allow_html=True,
    )


def render_basic_profile(user, existing):
    st.markdown('<span class="bdos-eyebrow">Step 1 of 7</span>', unsafe_allow_html=True)
    st.markdown(
        '<h2 class="bdos-page-heading" style="font-size:2.15rem">Build your basic profile</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="bdos-page-copy">Create the professional identity used throughout '
        "your Business DNA and opportunity recommendations.</p>",
        unsafe_allow_html=True,
    )

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



def merge_custom_values(selected, custom_text):
    custom_values = [
        value.strip()
        for value in custom_text.replace(";", ",").replace("\n", ",").split(",")
        if value.strip()
    ]
    return list(dict.fromkeys([*selected, *custom_values]))


def options_with_saved(options, saved):
    return list(dict.fromkeys([*options, *(saved or [])]))


def render_professional_experience(user, existing):
    st.markdown('<span class="bdos-eyebrow">Step 2 of 7</span>', unsafe_allow_html=True)
    st.markdown(
        '<h2 class="bdos-page-heading" style="font-size:2.15rem">'
        "Map your professional expertise</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="bdos-page-copy">Select the skills and tools that best represent '
        "the work you can confidently deliver.</p>",
        unsafe_allow_html=True,
    )

    with st.form("professional_experience_form"):
        primary = st.multiselect(
            "Primary Skills *",
            options_with_saved(SKILL_OPTIONS, existing.get("primary_skills")),
            default=existing.get("primary_skills") or [],
            help="Choose the skills you want to be primarily known for.",
        )
        custom_primary = st.text_input(
            "Add custom primary skills",
            placeholder="Comma-separated, for example: Headless Commerce, Plugin Architecture",
        )

        secondary = st.multiselect(
            "Secondary Skills",
            options_with_saved(SKILL_OPTIONS, existing.get("secondary_skills")),
            default=existing.get("secondary_skills") or [],
        )
        custom_secondary = st.text_input(
            "Add custom secondary skills",
            placeholder="Comma-separated",
        )

        left_column, right_column = st.columns(2)
        with left_column:
            technologies = st.multiselect(
                "Technologies",
                options_with_saved(TECHNOLOGY_OPTIONS, existing.get("technologies")),
                default=existing.get("technologies") or [],
            )
            custom_technologies = st.text_input(
                "Add custom technologies", placeholder="Comma-separated"
            )
            frameworks = st.multiselect(
                "Frameworks",
                options_with_saved(FRAMEWORK_OPTIONS, existing.get("frameworks")),
                default=existing.get("frameworks") or [],
            )
            custom_frameworks = st.text_input(
                "Add custom frameworks", placeholder="Comma-separated"
            )

        with right_column:
            platforms = st.multiselect(
                "Platforms",
                options_with_saved(PLATFORM_OPTIONS, existing.get("platforms")),
                default=existing.get("platforms") or [],
            )
            custom_platforms = st.text_input(
                "Add custom platforms", placeholder="Comma-separated"
            )
            certifications = st.multiselect(
                "Certifications (Optional)",
                options_with_saved(
                    CERTIFICATION_OPTIONS, existing.get("certifications")
                ),
                default=existing.get("certifications") or [],
            )
            custom_certifications = st.text_input(
                "Add custom certifications", placeholder="Comma-separated"
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

    experience = {
        "primary_skills": merge_custom_values(primary, custom_primary),
        "secondary_skills": merge_custom_values(secondary, custom_secondary),
        "technologies": merge_custom_values(technologies, custom_technologies),
        "frameworks": merge_custom_values(frameworks, custom_frameworks),
        "platforms": merge_custom_values(platforms, custom_platforms),
        "certifications": merge_custom_values(
            certifications, custom_certifications
        ),
    }

    if save_continue and not experience["primary_skills"]:
        st.error("Select or add at least one Primary Skill.")
        return

    try:
        save_professional_experience(user["id"], experience)
        if save_continue:
            advance_onboarding(user["id"], 2)
            st.session_state["edit_professional_experience"] = False
            st.success("Professional Experience completed.")
            st.rerun()
        else:
            st.success("Draft saved.")
    except Exception as error:
        st.error("Your Professional Experience could not be saved.")
        st.code(str(error))

def render_onboarding(user):
    current_step = int(user.get("onboarding_step") or 0)
    editing_basic = st.session_state.get("edit_basic_profile", False)
    editing_professional = st.session_state.get(
        "edit_professional_experience", False
    )

    with st.container(key="onboarding_topbar"):
        brand_wordmark()
    st.markdown(
        '<span class="bdos-eyebrow">Personalized setup</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h1 class="bdos-page-heading">Shape your professional Business DNA.</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="bdos-page-copy">A focused seven-step setup that teaches the app '
        "what you do, where you create value, and which opportunities fit you.</p>",
        unsafe_allow_html=True,
    )
    render_progress(current_step)

    try:
        basic_profile = get_basic_profile(user["id"])
    except Exception as error:
        st.error("The Basic Profile database migration is required.")
        st.code(str(error))
        return

    if current_step == 0 or editing_basic:
        with st.container(key="onboarding_card"):
            render_basic_profile(user, basic_profile)

        if editing_basic and st.button("Cancel editing"):
            st.session_state["edit_basic_profile"] = False
            st.rerun()
    else:
        try:
            professional_profile = get_professional_experience(user["id"])
        except Exception as error:
            st.error(
                "Phase 3 database migration is required before Step 2 can continue."
            )
            st.code(str(error))
            return

        if current_step == 1 or editing_professional:
            with st.container(key="onboarding_card"):
                render_professional_experience(user, professional_profile)

            controls = st.columns(2)
            with controls[0]:
                if st.button("Back to Basic Profile", use_container_width=True):
                    st.session_state["edit_basic_profile"] = True
                    st.rerun()
            with controls[1]:
                if editing_professional and st.button(
                    "Cancel editing", use_container_width=True
                ):
                    st.session_state["edit_professional_experience"] = False
                    st.rerun()
        else:
            st.success("Steps 1 and 2 are complete.")
            with st.container(key="coming_soon_card"):
                st.markdown(
                    '<span class="bdos-eyebrow">Step 3 of 7</span>',
                    unsafe_allow_html=True,
                )
                st.header("Business Experience")
                st.info("Coming in Phase 4")

            edit_basic, edit_professional = st.columns(2)
            with edit_basic:
                if st.button("Edit Basic Profile", use_container_width=True):
                    st.session_state["edit_basic_profile"] = True
                    st.rerun()
            with edit_professional:
                if st.button(
                    "Edit Professional Experience", use_container_width=True
                ):
                    st.session_state["edit_professional_experience"] = True
                    st.rerun()

    st.divider()
    if st.button("Log out"):
        st.logout()

def render_dashboard(user):
    with st.sidebar:
        brand_wordmark()
        st.caption(user.get("full_name") or "User")
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