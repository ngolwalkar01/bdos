import streamlit as st
from supabase import Client, create_client

from services.config import get_secret


@st.cache_resource
def get_database_client():
    url = get_secret("SUPABASE_URL")
    secret_key = get_secret("SUPABASE_SECRET_KEY")

    if not url or not secret_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SECRET_KEY must be configured before authentication is enabled."
        )

    return create_client(url, secret_key)


def ensure_user(identity):
    subject = identity.get("subject")
    if not subject:
        raise RuntimeError("The identity provider did not return a stable user subject.")

    client: Client = get_database_client()
    payload = {
        "oidc_subject": subject,
        "email": identity.get("email"),
        "full_name": identity.get("name"),
        "picture_url": identity.get("picture"),
    }

    response = (
        client.table("users")
        .upsert(payload, on_conflict="oidc_subject")
        .select("*")
        .execute()
    )

    if not response.data:
        raise RuntimeError("The user profile could not be created or loaded.")

    return response.data[0]