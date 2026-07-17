import streamlit as st


GLOBAL_CSS = """
<style>
:root {
    --bdos-navy: #0f172a;
    --bdos-slate: #475569;
    --bdos-muted: #64748b;
    --bdos-border: #e2e8f0;
    --bdos-surface: #ffffff;
    --bdos-canvas: #f6f8fc;
    --bdos-primary: #4f46e5;
    --bdos-primary-dark: #3730a3;
    --bdos-accent: #06b6d4;
    --bdos-success: #059669;
    --bdos-radius: 18px;
    --bdos-shadow: 0 24px 70px rgba(15, 23, 42, 0.11);
}

html, body, [data-testid="stAppViewContainer"] {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 8% 0%, rgba(79, 70, 229, 0.08), transparent 28rem),
        radial-gradient(circle at 100% 8%, rgba(6, 182, 212, 0.07), transparent 30rem),
        var(--bdos-canvas);
    color: var(--bdos-navy);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"],
#MainMenu,
footer {
    visibility: hidden;
}

.block-container {
    max-width: 1180px;
    padding-top: 2.4rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: var(--bdos-navy);
    letter-spacing: -0.035em;
}

p, label, [data-testid="stCaptionContainer"] {
    color: var(--bdos-slate);
}

div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button {
    min-height: 46px;
    border-radius: 12px;
    border: 1px solid var(--bdos-border);
    font-weight: 700;
    transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
}

div[data-testid="stButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-1px);
    border-color: #a5b4fc;
    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.13);
}

button[kind="primary"],
div[data-testid="stFormSubmitButton"] button[kind="primary"] {
    color: #ffffff;
    border: 0;
    background: linear-gradient(135deg, var(--bdos-primary), #6366f1);
    box-shadow: 0 10px 24px rgba(79, 70, 229, 0.24);
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-testid="stNumberInputContainer"] > div,
textarea {
    border-radius: 11px !important;
    border-color: #dbe3ef !important;
    background: #ffffff !important;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within,
div[data-testid="stNumberInputContainer"] > div:focus-within {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12) !important;
}

[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed #c7d2fe;
    background: #f8faff;
    border-radius: 14px;
}

[data-testid="stAlert"] {
    border-radius: 14px;
    border: 1px solid var(--bdos-border);
}

.bdos-wordmark {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-weight: 800;
    font-size: 1.02rem;
    letter-spacing: -0.025em;
    color: var(--bdos-navy);
}

.bdos-logo {
    display: inline-grid;
    place-items: center;
    width: 34px;
    height: 34px;
    border-radius: 10px;
    color: white;
    background: linear-gradient(135deg, var(--bdos-primary), var(--bdos-accent));
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.22);
}

.bdos-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: var(--bdos-primary);
    background: #eef2ff;
    border: 1px solid #dfe4ff;
    border-radius: 999px;
    padding: 7px 11px;
    font-size: 0.74rem;
    line-height: 1;
    font-weight: 800;
    letter-spacing: 0.09em;
    text-transform: uppercase;
}

.bdos-page-heading {
    margin: 0.9rem 0 0.4rem;
    font-size: clamp(2rem, 4vw, 3rem);
    line-height: 1.05;
    font-weight: 850;
    letter-spacing: -0.05em;
    color: var(--bdos-navy);
}

.bdos-page-copy {
    max-width: 650px;
    margin: 0 0 1.5rem;
    color: var(--bdos-muted);
    font-size: 1.02rem;
    line-height: 1.7;
}

/* Login */
.st-key-login_page {
    max-width: 1060px;
    margin: min(8vh, 5rem) auto 0;
    padding: 0 !important;
    overflow: hidden;
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 24px;
    background: var(--bdos-surface);
    box-shadow: var(--bdos-shadow);
}

.st-key-login_page > div {
    gap: 0 !important;
}

.login-hero {
    min-height: 560px;
    padding: 52px 48px;
    color: white;
    background:
        radial-gradient(circle at 85% 12%, rgba(34, 211, 238, 0.35), transparent 17rem),
        radial-gradient(circle at 0% 100%, rgba(129, 140, 248, 0.35), transparent 18rem),
        linear-gradient(145deg, #11183a 0%, #312e81 55%, #4338ca 100%);
}

.login-hero .bdos-wordmark,
.login-hero .bdos-wordmark span {
    color: white;
}

.login-hero h1 {
    max-width: 530px;
    margin: 5.2rem 0 1.25rem;
    color: white;
    font-size: clamp(2.5rem, 4.4vw, 4.3rem);
    line-height: 0.98;
    letter-spacing: -0.065em;
}

.login-hero p {
    max-width: 510px;
    color: rgba(255,255,255,0.76);
    font-size: 1.04rem;
    line-height: 1.7;
}

.login-benefits {
    display: grid;
    gap: 13px;
    margin-top: 2rem;
}

.login-benefit {
    display: flex;
    align-items: center;
    gap: 11px;
    color: rgba(255,255,255,0.9);
    font-weight: 600;
    font-size: 0.92rem;
}

.login-check {
    display: inline-grid;
    place-items: center;
    width: 23px;
    height: 23px;
    border-radius: 50%;
    color: #0f172a;
    background: #67e8f9;
    font-size: 0.75rem;
    font-weight: 900;
}

.login-panel,
.st-key-login_panel {
    min-height: 560px;
    padding: 105px 48px 36px;
    background: white;
}

.login-panel h2,
.st-key-login_panel h2 {
    margin: 1.5rem 0 0.65rem;
    font-size: 2rem;
    line-height: 1.1;
}

.login-panel p,
.st-key-login_panel p {
    margin-bottom: 1.75rem;
    line-height: 1.65;
}

.st-key-google_login button {
    width: 100%;
    min-height: 52px !important;
    color: #1e293b !important;
    background: white !important;
    border: 1px solid #d8e0ec !important;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.07);
}

.login-trust {
    margin-top: 1.25rem;
    color: #94a3b8;
    font-size: 0.76rem;
    line-height: 1.55;
    text-align: center;
}

/* Onboarding */
.onboarding-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2.4rem;
}

.onboarding-progress {
    display: flex;
    gap: 0;
    overflow-x: auto;
    margin: 1.7rem 0 2rem;
    padding: 0.3rem 0 0.8rem;
}

.onboarding-step {
    position: relative;
    flex: 1 0 125px;
    min-width: 0;
    text-align: center;
    color: #94a3b8;
    font-size: 0.72rem;
    font-weight: 650;
}

.onboarding-step:not(:last-child)::after {
    content: "";
    position: absolute;
    z-index: 0;
    top: 17px;
    left: 62%;
    width: 76%;
    height: 2px;
    background: #e2e8f0;
}

.onboarding-step.done:not(:last-child)::after {
    background: #818cf8;
}

.step-dot {
    position: relative;
    z-index: 1;
    display: grid;
    place-items: center;
    width: 35px;
    height: 35px;
    margin: 0 auto 8px;
    border: 2px solid #dbe3ef;
    border-radius: 50%;
    color: #94a3b8;
    background: #ffffff;
    font-weight: 800;
}

.onboarding-step.done .step-dot {
    color: white;
    border-color: var(--bdos-primary);
    background: var(--bdos-primary);
}

.onboarding-step.active .step-dot {
    color: var(--bdos-primary);
    border-color: var(--bdos-primary);
    box-shadow: 0 0 0 5px rgba(99,102,241,0.12);
}

.st-key-onboarding_card,
.st-key-coming_soon_card {
    padding: 2rem 2.1rem 1.6rem;
    border: 1px solid var(--bdos-border);
    border-radius: var(--bdos-radius);
    background: white;
    box-shadow: 0 15px 45px rgba(15, 23, 42, 0.06);
}

.st-key-basic_profile_form {
    margin-top: 1.2rem;
}

@media (max-width: 800px) {
    .block-container {
        padding: 1rem 1rem 2rem;
    }

    .st-key-login_page {
        margin-top: 0;
        border-radius: 18px;
    }

    .login-hero {
        min-height: auto;
        padding: 30px 26px 34px;
    }

    .login-hero h1 {
        margin-top: 2.8rem;
        font-size: 2.65rem;
    }

    .login-panel,
.st-key-login_panel {
        min-height: auto;
        padding: 38px 26px 32px;
    }

    .onboarding-topbar {
        margin-bottom: 1.4rem;
    }

    .st-key-onboarding_card {
        padding: 1.35rem 1rem 1rem;
    }
}

/* UI correction layer */
button[kind="primary"],
button[kind="primary"] p,
button[kind="primary"] span,
div[data-testid="stFormSubmitButton"] button[kind="primary"] p,
div[data-testid="stFormSubmitButton"] button[kind="primary"] span {
    color: #ffffff !important;
}

.st-key-google_login button {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 50px !important;
    padding: 0 18px 0 50px !important;
    color: #1f1f1f !important;
    border: 1px solid #747775 !important;
    border-radius: 10px !important;
    background: #ffffff !important;
    box-shadow: none !important;
    font-family: Roboto, Arial, sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
}

.st-key-google_login button p,
.st-key-google_login button span {
    margin: 0 !important;
    color: #1f1f1f !important;
    line-height: 1 !important;
}

.st-key-google_login button::before {
    content: "";
    position: absolute;
    left: 17px;
    width: 20px;
    height: 20px;
    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%234285F4' d='M21.6 12.23c0-.71-.06-1.39-.18-2.05H12v3.87h5.38a4.6 4.6 0 0 1-2 3.02v2.51h3.24c1.9-1.75 2.98-4.33 2.98-7.35Z'/%3E%3Cpath fill='%2334A853' d='M12 22c2.7 0 4.96-.9 6.62-2.42l-3.24-2.51c-.9.6-2.04.96-3.38.96-2.6 0-4.81-1.76-5.6-4.13H3.05v2.59A10 10 0 0 0 12 22Z'/%3E%3Cpath fill='%23FBBC05' d='M6.4 13.9A6 6 0 0 1 6.09 12c0-.66.11-1.3.31-1.9V7.51H3.05A10 10 0 0 0 2 12c0 1.61.38 3.14 1.05 4.49L6.4 13.9Z'/%3E%3Cpath fill='%23EA4335' d='M12 5.97c1.47 0 2.79.51 3.83 1.5l2.87-2.88A9.64 9.64 0 0 0 12 2a10 10 0 0 0-8.95 5.51L6.4 10.1C7.19 7.73 9.4 5.97 12 5.97Z'/%3E%3C/svg%3E");
}

.st-key-google_login button:hover {
    background: #f8fafd !important;
    border-color: #5f6368 !important;
    box-shadow: 0 2px 5px rgba(60, 64, 67, 0.18) !important;
    transform: none !important;
}

[data-testid="stFileUploaderDropzone"] button {
    min-width: 118px;
    font-size: 0 !important;
    color: transparent !important;
}

[data-testid="stFileUploaderDropzone"] button::after {
    content: "Choose file";
    color: #334155;
    font-size: 0.88rem;
    font-weight: 700;
    white-space: nowrap;
}

[data-testid="stHeaderActionElements"],
[data-testid="stHeadingWithActionElements"] a {
    display: none !important;
}
</style>
"""


def apply_theme():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def brand_wordmark():
    st.markdown(
        '<div class="bdos-wordmark"><span class="bdos-logo">B</span>'
        "<span>BusinessDev OS</span></div>",
        unsafe_allow_html=True,
    )