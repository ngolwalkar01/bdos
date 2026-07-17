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


def get_basic_profile(user_id):
    response = (
        get_database_client()
        .table("user_profiles")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else {}


def save_basic_profile(user_id, profile):
    payload = {"user_id": user_id, **profile}
    response = (
        get_database_client()
        .table("user_profiles")
        .upsert(payload, on_conflict="user_id")
        .select("*")
        .execute()
    )
    if not response.data:
        raise RuntimeError("The basic profile could not be saved.")
    return response.data[0]


def get_professional_experience(user_id):
    response = (
        get_database_client()
        .table("professional_experience")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else {}


def save_professional_experience(user_id, experience):
    payload = {"user_id": user_id, **experience}
    response = (
        get_database_client()
        .table("professional_experience")
        .upsert(payload, on_conflict="user_id")
        .select("*")
        .execute()
    )
    if not response.data:
        raise RuntimeError("The professional experience profile could not be saved.")
    return response.data[0]

def get_business_experience(user_id):
    response = (
        get_database_client()
        .table("business_experience")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else {}


def save_business_experience(user_id, experience):
    payload = {"user_id": user_id, **experience}
    response = (
        get_database_client()
        .table("business_experience")
        .upsert(payload, on_conflict="user_id")
        .select("*")
        .execute()
    )
    if not response.data:
        raise RuntimeError("The business experience profile could not be saved.")
    return response.data[0]

def get_opportunity_preferences(user_id):
    response = (
        get_database_client()
        .table("opportunity_preferences")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else {}


def save_opportunity_preferences(user_id, preferences):
    payload = {"user_id": user_id, **preferences}
    response = (
        get_database_client()
        .table("opportunity_preferences")
        .upsert(payload, on_conflict="user_id")
        .select("*")
        .execute()
    )
    if not response.data:
        raise RuntimeError("The opportunity preferences could not be saved.")
    return response.data[0]


def get_decision_maker_preferences(user_id):
    response = (
        get_database_client().table("decision_maker_preferences").select("*")
        .eq("user_id", user_id).limit(1).execute()
    )
    return response.data[0] if response.data else {}


def save_decision_maker_preferences(user_id, preferences):
    payload = {"user_id": user_id, **preferences}
    response = (
        get_database_client().table("decision_maker_preferences")
        .upsert(payload, on_conflict="user_id").select("*").execute()
    )
    if not response.data:
        raise RuntimeError("The decision maker preferences could not be saved.")
    return response.data[0]


def advance_onboarding(user_id, step):
    response = (
        get_database_client()
        .table("users")
        .update({"onboarding_step": step})
        .eq("id", user_id)
        .lt("onboarding_step", step)
        .execute()
    )
    return response.data


def upload_resume(user_id, uploaded_file):
    client = get_database_client()
    bucket_name = "resumes"

    try:
        client.storage.get_bucket(bucket_name)
    except Exception:
        client.storage.create_bucket(
            bucket_name,
            options={
                "public": False,
                "allowed_mime_types": [
                    "application/pdf",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ],
                "file_size_limit": 10 * 1024 * 1024,
            },
        )

    extension = uploaded_file.name.rsplit(".", 1)[-1].lower()
    object_path = f"{user_id}/resume.{extension}"
    client.storage.from_(bucket_name).upload(
        path=object_path,
        file=uploaded_file.getvalue(),
        file_options={
            "content-type": uploaded_file.type,
            "cache-control": "3600",
            "upsert": "true",
        },
    )
    return {
        "resume_path": object_path,
        "resume_filename": uploaded_file.name,
        "resume_content_type": uploaded_file.type,
        "resume_size_bytes": uploaded_file.size,
    }