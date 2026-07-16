import streamlit as st


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

NAVIGATION_ICONS = {
    "Dashboard": "🏠",
    "Discover Businesses": "🔎",
    "My Companies": "👥",
    "Decision Makers": "👤",
    "Outreach": "💬",
    "Freelance Jobs": "💼",
    "Analytics": "📊",
    "Settings": "⚙️",
}


def render_onboarding_start(user):
    st.title("Welcome")
    st.subheader(f"Hello, {user.get('full_name') or 'there'}")
    st.write(
        "Your account is ready. The seven-step onboarding experience is the next phase of development."
    )
    st.progress(0, text="Onboarding: 0 of 7 steps completed")
    st.info("Basic Profile — coming in Phase 2")

    if st.button("Log out"):
        st.logout()


def render_dashboard(user):
    with st.sidebar:
        st.markdown(f"### {user.get('full_name') or 'User'}")
        labels = [f"{NAVIGATION_ICONS[item]}  {item}" for item in NAVIGATION]
        selected_label = st.radio("Navigation", labels, label_visibility="collapsed")
        selected = NAVIGATION[labels.index(selected_label)]
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