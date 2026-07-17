import streamlit as st

from services.config import get_bool_secret
from ui.theme import brand_wordmark


def auth_enabled():
    return get_bool_secret("AUTH_ENABLED", False)


def require_authenticated_user():
    if not st.user.is_logged_in:
        with st.container(key="login_page"):
            hero_column, login_column = st.columns([1.18, 0.82], gap=None)

            with hero_column:
                st.markdown(
                    """
                    <div class="login-hero">
                        <div class="bdos-wordmark">
                            <span class="bdos-logo">B</span>
                            <span>BusinessDev OS</span>
                        </div>
                        <h1>Your experience deserves better opportunities.</h1>
                        <p>
                            Build your professional Business DNA, discover companies that
                            fit your expertise, and create outreach that sounds like you.
                        </p>
                        <div class="login-benefits">
                            <div class="login-benefit">
                                <span class="login-check">✓</span>
                                Personalized opportunity discovery
                            </div>
                            <div class="login-benefit">
                                <span class="login-check">✓</span>
                                AI-assisted decision-maker research
                            </div>
                            <div class="login-benefit">
                                <span class="login-check">✓</span>
                                Private, reusable professional profile
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with login_column:
                with st.container(key="login_panel"):
                    st.markdown(
                        """
                        <span class="bdos-eyebrow">Welcome</span>
                        <h2>Sign in to continue</h2>
                        <p>
                            Start building a private intelligence layer for your
                            business-development workflow.
                        </p>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        "Continue with Google",
                        key="google_login",
                        use_container_width=True,
                    ):
                        st.login()
                    st.markdown(
                        """
                        <div class="login-trust">
                            Secure authentication powered by Google.<br>
                            Your profile data is never published to GitHub.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        st.stop()

    return {
        "subject": st.user.get("sub"),
        "email": st.user.get("email"),
        "name": st.user.get("name") or st.user.get("email") or "User",
        "picture": st.user.get("picture"),
    }