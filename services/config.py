import os

import streamlit as st


def get_secret(name, default=None):
    value = os.getenv(name)
    if value not in (None, ""):
        return value

    try:
        return st.secrets.get(name, default)
    except FileNotFoundError:
        return default


def get_bool_secret(name, default=False):
    value = get_secret(name, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}