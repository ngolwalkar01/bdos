import streamlit as st

from services.config import get_bool_secret


def auth_enabled():
    return get_bool_secret("AUTH_ENABLED", False)


def require_authenticated_user():
    if not st.user.is_logged_in:
        st.title("LinkedIn BD Agent")
        st.subheader("Turn your experience into better business opportunities")
        st.write(
            "Sign in to create your private Business DNA and personalized discovery profile."
        )
        if st.button("Continue with Google", type="primary", use_container_width=True):
            st.login()
        st.stop()

    return {
        "subject": st.user.get("sub"),
        "email": st.user.get("email"),
        "name": st.user.get("name") or st.user.get("email") or "User",
        "picture": st.user.get("picture"),
    }