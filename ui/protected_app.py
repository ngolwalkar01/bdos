import json
from html import escape

from urllib.parse import urlparse
from zoneinfo import available_timezones

import streamlit as st

from services.database import (
    advance_onboarding,
    complete_onboarding,
    get_basic_profile,
    get_business_dna_profile,
    get_business_experience,
    get_communication_style,
    get_decision_maker_preferences,
    get_opportunity_preferences,
    get_professional_experience,
    save_basic_profile,
    save_business_dna_profile,
    save_business_experience,
    save_communication_style,
    save_decision_maker_preferences,
    save_opportunity_preferences,
    save_professional_experience,
    upload_resume,
)
from ui.theme import brand_wordmark
from frontend.dashboard import (
    render_business_dna,
    render_coming_soon,
    render_discover,
    render_home,
)


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
    "Home",
    "Discover",
    "Relationships",
    "Outreach",
    "Proposals",
    "Intelligence",
    "Business DNA",
    "Settings",
]
NAVIGATION_LABELS = {
    "Home": "⌂  Home",
    "Discover": "⌕  Discover",
    "Relationships": "◇  Relationships",
    "Outreach": "↗  Outreach",
    "Proposals": "▤  Proposals",
    "Intelligence": "▥  Intelligence",
    "Business DNA": "✦  Business DNA",
    "Settings": "⚙  Settings",
}
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

INDUSTRY_OPTIONS = [
    "Ecommerce", "Grocery Delivery", "Dairy", "Logistics", "Healthcare",
    "Education", "Manufacturing", "Real Estate", "SaaS", "Finance",
    "Wellness", "Marketplace", "Social Network", "Hospitality", "Others",
]

BUSINESS_PROBLEM_OPTIONS = [
    "Subscription Commerce", "Payment Integration", "Checkout Optimization",
    "Business Automation", "API Integration", "CRM", "ERP",
    "Performance Optimization", "Customer Portal", "Order Management",
    "Inventory", "AI Automation", "Reporting", "Analytics",
]


OPPORTUNITY_TYPE_OPTIONS = [
    "Freelance", "Contract", "Part Time", "Full Time", "Consulting",
    "Technical Advisor", "Long-term Partnership", "Equity Based",
    "Agency Partnership",
]

COMPANY_SIZE_OPTIONS = [
    "Startup", "Small Business", "Mid-size", "Enterprise", "No Preference",
]

COUNTRY_OPTIONS = [
    "Australia", "Austria", "Belgium", "Brazil", "Canada", "Denmark", "Finland",
    "France", "Germany", "India", "Ireland", "Italy", "Japan", "Netherlands",
    "New Zealand", "Norway", "Poland", "Portugal", "Singapore", "South Africa",
    "Spain", "Sweden", "Switzerland", "United Arab Emirates", "United Kingdom",
    "United States",
]

BUDGET_TYPE_OPTIONS = ["Hourly", "Monthly", "Fixed Project"]
CURRENCY_OPTIONS = ["USD", "EUR", "GBP", "INR", "AUD", "CAD", "DKK", "SEK", "NOK"]
REMOTE_OPTIONS = ["Remote", "Hybrid", "Onsite"]

DECISION_MAKER_OPTIONS = [
    "Founder", "CEO", "COO", "CTO", "CIO", "Head of Ecommerce",
    "Product Manager", "Operations Manager", "Engineering Manager", "HR",
    "Recruiter",
]


TONE_OPTIONS = [
    "Professional", "Friendly", "Casual", "Technical", "Founder-to-Founder",
    "Consultant", "Executive",
]
WRITING_LENGTH_OPTIONS = ["Short", "Medium", "Detailed"]
COMMUNICATION_PREFERENCE_OPTIONS = [
    "LinkedIn", "Email", "Proposal", "Cold Outreach",
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



def render_business_experience(user, existing):
    st.markdown('<span class="bdos-eyebrow">Step 3 of 7</span>', unsafe_allow_html=True)
    st.markdown(
        '<h2 class="bdos-page-heading" style="font-size:2.15rem">'
        "Define your business experience</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="bdos-page-copy">Capture the industries you understand and the '
        "business problems you have already solved.</p>",
        unsafe_allow_html=True,
    )

    with st.form("business_experience_form"):
        industries = st.multiselect(
            "Which industries have you worked in? *",
            options_with_saved(INDUSTRY_OPTIONS, existing.get("industries")),
            default=existing.get("industries") or [],
        )
        custom_industries = st.text_input(
            "Add other industries",
            placeholder="Comma-separated, for example: Agritech, Renewable Energy",
        )

        st.divider()

        business_problems = st.multiselect(
            "Which business problems have you solved? *",
            options_with_saved(
                BUSINESS_PROBLEM_OPTIONS, existing.get("business_problems")
            ),
            default=existing.get("business_problems") or [],
        )
        custom_problems = st.text_input(
            "Add other business problems",
            placeholder="Comma-separated, for example: Delivery Scheduling, Renewal Recovery",
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
        "industries": merge_custom_values(industries, custom_industries),
        "business_problems": merge_custom_values(
            business_problems, custom_problems
        ),
    }

    if save_continue and not experience["industries"]:
        st.error("Select or add at least one industry.")
        return
    if save_continue and not experience["business_problems"]:
        st.error("Select or add at least one business problem.")
        return

    try:
        save_business_experience(user["id"], experience)
        if save_continue:
            advance_onboarding(user["id"], 3)
            st.session_state["edit_business_experience"] = False
            st.success("Business Experience completed.")
            st.rerun()
        else:
            st.success("Draft saved.")
    except Exception as error:
        st.error("Your Business Experience could not be saved.")
        st.code(str(error))


def select_index(options, saved_value, default=0):
    return options.index(saved_value) if saved_value in options else default


def render_opportunity_preferences(user, existing):
    st.markdown('<span class="bdos-eyebrow">Step 4 of 7</span>', unsafe_allow_html=True)
    st.markdown(
        '<h2 class="bdos-page-heading" style="font-size:2.15rem">'
        "Describe your ideal opportunity</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="bdos-page-copy">Define the work, companies, locations, and '
        "commercial range the discovery engine should prioritize.</p>",
        unsafe_allow_html=True,
    )

    with st.form("opportunity_preferences_form"):
        opportunity_types = st.multiselect(
            "Preferred Opportunity Type *",
            options_with_saved(
                OPPORTUNITY_TYPE_OPTIONS, existing.get("opportunity_types")
            ),
            default=existing.get("opportunity_types") or [],
        )

        company_sizes = st.multiselect(
            "Preferred Company Size *",
            COMPANY_SIZE_OPTIONS,
            default=existing.get("company_sizes") or [],
        )

        preferred_industries = st.multiselect(
            "Preferred Industries *",
            options_with_saved(
                INDUSTRY_OPTIONS, existing.get("preferred_industries")
            ),
            default=existing.get("preferred_industries") or [],
        )
        custom_industries = st.text_input(
            "Add other preferred industries",
            placeholder="Comma-separated",
        )

        preferred_countries = st.multiselect(
            "Preferred Countries *",
            options_with_saved(
                COUNTRY_OPTIONS, existing.get("preferred_countries")
            ),
            default=existing.get("preferred_countries") or [],
        )
        custom_countries = st.text_input(
            "Add other preferred countries",
            placeholder="Comma-separated",
        )

        st.markdown("#### Preferred Budget")
        budget_type_column, currency_column = st.columns(2)
        with budget_type_column:
            budget_type = st.selectbox(
                "Budget Type",
                BUDGET_TYPE_OPTIONS,
                index=select_index(
                    BUDGET_TYPE_OPTIONS, existing.get("budget_type")
                ),
            )
        with currency_column:
            currency = st.selectbox(
                "Currency",
                CURRENCY_OPTIONS,
                index=select_index(
                    CURRENCY_OPTIONS, existing.get("budget_currency")
                ),
            )

        minimum_column, maximum_column = st.columns(2)
        with minimum_column:
            budget_min = st.number_input(
                "Minimum",
                min_value=0.0,
                value=float(existing.get("budget_min") or 0),
                step=100.0,
            )
        with maximum_column:
            budget_max = st.number_input(
                "Maximum",
                min_value=0.0,
                value=float(existing.get("budget_max") or 0),
                step=100.0,
            )

        remote_preferences = st.multiselect(
            "Remote Preference *",
            REMOTE_OPTIONS,
            default=existing.get("remote_preferences") or [],
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

    if "No Preference" in company_sizes:
        company_sizes = ["No Preference"]

    preferences = {
        "opportunity_types": opportunity_types,
        "company_sizes": company_sizes,
        "preferred_industries": merge_custom_values(
            preferred_industries, custom_industries
        ),
        "preferred_countries": merge_custom_values(
            preferred_countries, custom_countries
        ),
        "budget_type": budget_type,
        "budget_currency": currency,
        "budget_min": float(budget_min),
        "budget_max": float(budget_max),
        "remote_preferences": remote_preferences,
    }

    if save_continue:
        required_lists = {
            "Preferred Opportunity Type": preferences["opportunity_types"],
            "Preferred Company Size": preferences["company_sizes"],
            "Preferred Industries": preferences["preferred_industries"],
            "Preferred Countries": preferences["preferred_countries"],
            "Remote Preference": preferences["remote_preferences"],
        }
        missing = [
            label for label, values in required_lists.items() if not values
        ]
        if missing:
            st.error("Complete the following fields: " + ", ".join(missing))
            return
        if budget_max and budget_max < budget_min:
            st.error("Maximum budget must be greater than or equal to Minimum.")
            return

    try:
        save_opportunity_preferences(user["id"], preferences)
        if save_continue:
            advance_onboarding(user["id"], 4)
            st.session_state["edit_opportunity_preferences"] = False
            st.success("Ideal Opportunity completed.")
            st.rerun()
        else:
            st.success("Draft saved.")
    except Exception as error:
        st.error("Your Opportunity Preferences could not be saved.")
        st.code(str(error))


def render_decision_maker_preferences(user, existing):
    st.markdown('<span class="bdos-eyebrow">Step 5 of 7</span>', unsafe_allow_html=True)
    st.markdown('<h2 class="bdos-page-heading" style="font-size:2.15rem">Choose your ideal decision makers</h2>', unsafe_allow_html=True)
    st.markdown('<p class="bdos-page-copy">Identify the people Business Discovery and Outreach should prioritize inside your ideal companies.</p>', unsafe_allow_html=True)
    with st.form("decision_maker_preferences_form"):
        roles = st.multiselect(
            "Who would you like to connect with? *",
            options_with_saved(DECISION_MAKER_OPTIONS, existing.get("decision_maker_roles")),
            default=existing.get("decision_maker_roles") or [],
            help="Select every role that commonly influences or owns the problems you solve.",
        )
        custom_roles = st.text_input("Add other decision-maker roles", placeholder="Comma-separated, for example: VP of Growth, Head of Partnerships")
        draft_column, continue_column = st.columns(2)
        with draft_column:
            save_draft = st.form_submit_button("Save Draft", use_container_width=True)
        with continue_column:
            save_continue = st.form_submit_button("Save & Continue", type="primary", use_container_width=True)
    if not save_draft and not save_continue:
        return
    preferences = {"decision_maker_roles": merge_custom_values(roles, custom_roles)}
    if save_continue and not preferences["decision_maker_roles"]:
        st.error("Select or add at least one decision-maker role.")
        return
    try:
        save_decision_maker_preferences(user["id"], preferences)
        if save_continue:
            advance_onboarding(user["id"], 5)
            st.session_state["edit_decision_maker_preferences"] = False
            st.success("Ideal Decision Makers completed.")
            st.rerun()
        else:
            st.success("Draft saved.")
    except Exception as error:
        st.error("Your Decision Maker Profile could not be saved.")
        st.code(str(error))



def render_communication_style(user, existing):
    st.markdown('<span class="bdos-eyebrow">Step 6 of 7</span>', unsafe_allow_html=True)
    st.markdown(
        '<h2 class="bdos-page-heading" style="font-size:2.15rem">Define your communication style</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="bdos-page-copy">Teach the AI how your outreach, proposals, and professional messages should sound.</p>',
        unsafe_allow_html=True,
    )
    with st.form("communication_style_form"):
        tone = st.selectbox(
            "Preferred Tone *",
            TONE_OPTIONS,
            index=select_index(TONE_OPTIONS, existing.get("tone")),
            help="Choose the voice that should guide AI-generated writing.",
        )
        writing_length = st.segmented_control(
            "Writing Length *",
            WRITING_LENGTH_OPTIONS,
            default=existing.get("writing_length") or "Medium",
            selection_mode="single",
        )
        communication_preferences = st.multiselect(
            "Communication Preference *",
            COMMUNICATION_PREFERENCE_OPTIONS,
            default=existing.get("communication_preferences") or [],
            help="Select every format you expect the app to help you create.",
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
    style = {
        "tone": tone,
        "writing_length": writing_length,
        "communication_preferences": communication_preferences,
    }
    if save_continue and not style["writing_length"]:
        st.error("Select a Writing Length.")
        return
    if save_continue and not style["communication_preferences"]:
        st.error("Select at least one Communication Preference.")
        return
    try:
        save_communication_style(user["id"], style)
        if save_continue:
            advance_onboarding(user["id"], 6)
            st.session_state["edit_communication_style"] = False
            st.success("Communication Style completed.")
            st.rerun()
        else:
            st.success("Draft saved.")
    except Exception as error:
        st.error("Your Communication Style could not be saved.")
        st.code(str(error))



DNA_FIELDS = [
    ("identity", "Identity"), ("experience", "Experience"), ("skills", "Skills"),
    ("industries", "Industries"), ("business_problems_solved", "Business Problems Solved"),
    ("ideal_opportunities", "Ideal Opportunities"), ("ideal_companies", "Ideal Companies"),
    ("ideal_decision_makers", "Ideal Decision Makers"), ("writing_style", "Writing Style"),
    ("strengths", "Strengths"), ("weaknesses", "Development Areas"),
    ("recommended_positioning", "Recommended Positioning"),
]


def parse_ai_json(text):
    fence = chr(96) * 3
    value = text.strip()
    if value.startswith(fence + "json"):
        value = value[7:]
    elif value.startswith(fence):
        value = value[3:]
    if value.endswith(fence):
        value = value[:-3]
    return json.loads(value.strip())


def render_dna_value(value):
    if isinstance(value, list):
        st.markdown("\n".join(f"- {item}" for item in value) or "Not specified")
    else:
        st.write(value or "Not specified")


def build_knowledge_documents(profile, source):
    def bullets(values):
        return "\n".join(f"- {value}" for value in (values or [])) or "- Not specified"
    return {
        "user_profile.md": f"# User Profile\n\n## Identity\n{profile.get('identity', '')}\n\n## Experience\n{profile.get('experience', '')}\n\n## Positioning\n{profile.get('recommended_positioning', '')}",
        "business_dna.md": f"# Business DNA\n\n## Problems Solved\n{profile.get('business_problems_solved', '')}\n\n## Strengths\n{bullets(profile.get('strengths'))}\n\n## Development Areas\n{bullets(profile.get('weaknesses'))}",
        "skills.md": f"# Skills\n\n{bullets(source['professional'].get('primary_skills'))}\n\n{profile.get('skills', '')}",
        "industries.md": f"# Industries\n\n{bullets(source['business'].get('industries'))}\n\n{profile.get('industries', '')}",
        "ideal_opportunities.md": f"# Ideal Opportunities\n\n{profile.get('ideal_opportunities', '')}",
        "ideal_clients.md": f"# Ideal Clients\n\n{profile.get('ideal_companies', '')}",
        "decision_makers.md": f"# Decision Makers\n\n{profile.get('ideal_decision_makers', '')}",
        "writing_style.md": f"# Writing Style\n\n{profile.get('writing_style', '')}",
        "case_studies.md": f"# Case Study Directions\n\n{bullets(profile.get('case_study_directions'))}",
        "value_propositions.md": f"# Value Propositions\n\n{bullets(profile.get('value_propositions'))}",
    }


def generate_business_dna(client, source):
    prompt = """You are a senior business-positioning strategist. Build an accurate Business DNA
using only the onboarding data below. Never invent employers, clients, revenue, outcomes,
certifications, or case-study facts.

DATA:
%s

Return only valid JSON with exactly these keys:
identity, experience, skills, industries, business_problems_solved, ideal_opportunities,
ideal_companies, ideal_decision_makers, writing_style, recommended_positioning as concise
strings; strengths, weaknesses, case_study_directions, value_propositions as arrays of
3-5 concise items. Weaknesses must be constructive positioning gaps.
""" % json.dumps(source, indent=2, default=str)
    response = client.responses.create(model="gpt-4.1-mini", input=prompt)
    profile = parse_ai_json(response.output_text)
    missing = [key for key, _ in DNA_FIELDS if key not in profile]
    if missing:
        raise RuntimeError("AI response omitted: " + ", ".join(missing))
    return profile


def render_business_dna_review(user, source, existing, client):
    st.markdown('<span class="bdos-eyebrow">Step 7 of 7</span>', unsafe_allow_html=True)
    st.markdown('<h2 class="bdos-page-heading" style="font-size:2.15rem">Review your Business DNA</h2>', unsafe_allow_html=True)
    st.markdown('<p class="bdos-page-copy">Review the positioning intelligence generated from your onboarding answers before entering the dashboard.</p>', unsafe_allow_html=True)
    profile = existing.get("profile") or {}
    label = "Regenerate Business DNA" if profile else "Generate Business DNA"
    if st.button(label, type="secondary" if profile else "primary", use_container_width=True):
        try:
            with st.spinner("Turning your experience into a focused Business DNA..."):
                profile = generate_business_dna(client, source)
                documents = build_knowledge_documents(profile, source)
                save_business_dna_profile(user["id"], profile, documents)
            st.rerun()
        except Exception as error:
            st.error("Your Business DNA could not be generated.")
            st.code(str(error))
            return
    if not profile:
        st.info("Generate your Business DNA to review and complete onboarding.")
        return
    columns = st.columns(2)
    for index, (key, label) in enumerate(DNA_FIELDS):
        with columns[index % 2]:
            with st.container(border=True):
                st.markdown(f"#### {label}")
                render_dna_value(profile.get(key))
    documents = existing.get("knowledge_documents") or build_knowledge_documents(profile, source)
    with st.expander("Generated knowledge files"):
        st.caption("These private documents are stored in your application database.")
        for filename, content in documents.items():
            with st.expander(filename):
                st.markdown(content)
    st.info("Use Review & edit above to change source information, then regenerate.")
    if st.button("Accept & Continue to Dashboard", type="primary", use_container_width=True):
        try:
            complete_onboarding(user["id"])
            st.rerun()
        except Exception as error:
            st.error("Onboarding could not be completed.")
            st.code(str(error))


def render_review_menu(completed_steps):
    if completed_steps < 1:
        return

    spacer, review_column = st.columns([5, 1.25])
    with review_column:
        with st.popover("Review & edit", use_container_width=True):
            st.caption("Completed sections")

            if completed_steps >= 1 and st.button(
                "Basic Profile", key="review_basic_profile", use_container_width=True
            ):
                st.session_state["edit_basic_profile"] = True
                st.session_state["edit_professional_experience"] = False
                st.session_state["edit_business_experience"] = False
                st.session_state["edit_opportunity_preferences"] = False
                st.session_state["edit_decision_maker_preferences"] = False
                st.session_state["edit_communication_style"] = False
                st.rerun()

            if completed_steps >= 2 and st.button(
                "Professional Experience",
                key="review_professional_experience",
                use_container_width=True,
            ):
                st.session_state["edit_basic_profile"] = False
                st.session_state["edit_professional_experience"] = True
                st.session_state["edit_business_experience"] = False
                st.session_state["edit_opportunity_preferences"] = False
                st.session_state["edit_decision_maker_preferences"] = False
                st.session_state["edit_communication_style"] = False
                st.rerun()

            if completed_steps >= 3 and st.button(
                "Business Experience",
                key="review_business_experience",
                use_container_width=True,
            ):
                st.session_state["edit_basic_profile"] = False
                st.session_state["edit_professional_experience"] = False
                st.session_state["edit_business_experience"] = True
                st.session_state["edit_opportunity_preferences"] = False
                st.session_state["edit_decision_maker_preferences"] = False
                st.session_state["edit_communication_style"] = False
                st.rerun()

            if completed_steps >= 4 and st.button(
                "Ideal Opportunity",
                key="review_opportunity_preferences",
                use_container_width=True,
            ):
                st.session_state["edit_basic_profile"] = False
                st.session_state["edit_professional_experience"] = False
                st.session_state["edit_business_experience"] = False
                st.session_state["edit_opportunity_preferences"] = True
                st.session_state["edit_decision_maker_preferences"] = False
                st.session_state["edit_communication_style"] = False
                st.rerun()

            if completed_steps >= 5 and st.button(
                "Ideal Decision Makers", key="review_decision_maker_preferences", use_container_width=True
            ):
                st.session_state["edit_basic_profile"] = False
                st.session_state["edit_professional_experience"] = False
                st.session_state["edit_business_experience"] = False
                st.session_state["edit_opportunity_preferences"] = False
                st.session_state["edit_decision_maker_preferences"] = True
                st.session_state["edit_communication_style"] = False
                st.rerun()

            if completed_steps >= 6 and st.button(
                "Communication Style",
                key="review_communication_style",
                use_container_width=True,
            ):
                st.session_state["edit_basic_profile"] = False
                st.session_state["edit_professional_experience"] = False
                st.session_state["edit_business_experience"] = False
                st.session_state["edit_opportunity_preferences"] = False
                st.session_state["edit_decision_maker_preferences"] = False
                st.session_state["edit_communication_style"] = True
                st.rerun()

def render_onboarding(user, openai_client=None):
    current_step = int(user.get("onboarding_step") or 0)
    editing_basic = st.session_state.get("edit_basic_profile", False)
    editing_professional = st.session_state.get(
        "edit_professional_experience", False
    )
    editing_business = st.session_state.get("edit_business_experience", False)
    editing_opportunity = st.session_state.get(
        "edit_opportunity_preferences", False
    )
    editing_decision_makers = st.session_state.get(
        "edit_decision_maker_preferences", False
    )
    editing_communication = st.session_state.get(
        "edit_communication_style", False
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
    render_review_menu(current_step)

    try:
        basic_profile = get_basic_profile(user["id"])
    except Exception as error:
        st.error("The Basic Profile database migration is required.")
        st.code(str(error))
        return

    if current_step == 0 or editing_basic:
        with st.container(key="onboarding_card"):
            render_basic_profile(user, basic_profile)
        if editing_basic and st.button("Return to current step"):
            st.session_state["edit_basic_profile"] = False
            st.rerun()
    else:
        try:
            professional_profile = get_professional_experience(user["id"])
        except Exception as error:
            st.error("The Professional Experience database migration is required.")
            st.code(str(error))
            return

        if current_step == 1 or editing_professional:
            with st.container(key="onboarding_card"):
                render_professional_experience(user, professional_profile)
            if editing_professional and st.button("Return to current step"):
                st.session_state["edit_professional_experience"] = False
                st.rerun()
        else:
            try:
                business_profile = get_business_experience(user["id"])
            except Exception as error:
                st.error("The Business Experience database migration is required.")
                st.code(str(error))
                return

            if current_step == 2 or editing_business:
                with st.container(key="onboarding_card"):
                    render_business_experience(user, business_profile)
                if editing_business and st.button("Return to current step"):
                    st.session_state["edit_business_experience"] = False
                    st.rerun()
            else:
                try:
                    opportunity_profile = get_opportunity_preferences(user["id"])
                except Exception as error:
                    st.error(
                        "Phase 5 database migration is required before Step 4 can continue."
                    )
                    st.code(str(error))
                    return

                if current_step == 3 or editing_opportunity:
                    with st.container(key="onboarding_card"):
                        render_opportunity_preferences(
                            user, opportunity_profile
                        )
                    if editing_opportunity and st.button("Return to current step"):
                        st.session_state["edit_opportunity_preferences"] = False
                        st.rerun()
                else:
                    try:
                        decision_maker_profile = get_decision_maker_preferences(user["id"])
                    except Exception as error:
                        st.error("Phase 6 database migration is required before Step 5 can continue.")
                        st.code(str(error))
                        return
                    if current_step == 4 or editing_decision_makers:
                        with st.container(key="onboarding_card"):
                            render_decision_maker_preferences(user, decision_maker_profile)
                        if editing_decision_makers and st.button("Return to current step"):
                            st.session_state["edit_decision_maker_preferences"] = False
                            st.rerun()
                    else:
                        try:
                            communication_style = get_communication_style(user["id"])
                        except Exception as error:
                            st.error(
                                "Phase 7 database migration is required before Step 6 can continue."
                            )
                            st.code(str(error))
                            return
                        if current_step == 5 or editing_communication:
                            with st.container(key="onboarding_card"):
                                render_communication_style(user, communication_style)
                            if editing_communication and st.button("Return to current step"):
                                st.session_state["edit_communication_style"] = False
                                st.rerun()
                        else:
                            try:
                                business_dna = get_business_dna_profile(user["id"])
                            except Exception as error:
                                st.error("Phase 8 database migration is required before Step 7 can continue.")
                                st.code(str(error))
                                return
                            source = {
                                "basic": basic_profile,
                                "professional": professional_profile,
                                "business": business_profile,
                                "opportunity": opportunity_profile,
                                "decision_makers": decision_maker_profile,
                                "communication": communication_style,
                            }
                            with st.container(key="onboarding_card"):
                                render_business_dna_review(
                                    user, source, business_dna, openai_client
                                )

    st.divider()
    if st.button("Log out"):
        st.logout()

def render_dashboard(user):
    with st.sidebar:
        with st.container(key="sidebar_brand"):
            brand_wordmark()
            st.caption("Opportunity Intelligence")
        st.markdown('<div class="sidebar-section-label">Workspace</div>', unsafe_allow_html=True)
        selected = st.radio(
            "Navigation",
            NAVIGATION,
            format_func=lambda item: NAVIGATION_LABELS[item],
            label_visibility="collapsed",
            key="dashboard_navigation",
        )
        full_name = escape(user.get("full_name") or "BusinessDev User")
        email = escape(user.get("email") or "Private workspace")
        initial = escape(full_name[:1].upper())
        st.markdown(
            f'<div class="sidebar-user"><span class="sidebar-avatar">{initial}</span>'
            f'<span class="sidebar-user-copy"><strong>{full_name}</strong>'
            f'<small>{email}</small></span></div>',
            unsafe_allow_html=True,
        )
        if st.button("Log out", use_container_width=True, key="sidebar_logout"):
            st.logout()

    if selected == "Home":
        render_home(user)
    elif selected == "Discover":
        render_discover(user)
    elif selected == "Business DNA":
        render_business_dna(user)
    else:
        render_coming_soon(selected)
