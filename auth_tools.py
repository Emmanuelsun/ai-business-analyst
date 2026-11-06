import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def _get_setting(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return None


def get_client():
    if "sb_client" not in st.session_state:
        url = _get_setting("SUPABASE_URL")
        key = _get_setting("SUPABASE_KEY")
        if not url or not key:
            return None
        st.session_state["sb_client"] = create_client(url, key)
    return st.session_state["sb_client"]


def current_user_email():
    return st.session_state.get("user_email")


def sign_up(email, password):
    client = get_client()
    if client is None:
        return False, "The account service is not set up. Please check your settings."
    try:
        response = client.auth.sign_up({"email": email, "password": password})
    except Exception as error:
        return False, f"Sign up did not work: {error}"
    if response.session is not None:
        st.session_state["user_email"] = email
        return True, "Your account is ready and you are logged in."
    return True, "Account created. Please check your email, click the confirmation link, then log in here."


def sign_in(email, password):
    client = get_client()
    if client is None:
        return False, "The account service is not set up. Please check your settings."
    try:
        client.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as error:
        return False, f"Log in did not work: {error}"
    st.session_state["user_email"] = email
    return True, "You are logged in."


def sign_out():
    client = st.session_state.get("sb_client")
    if client is not None:
        try:
            client.auth.sign_out()
        except Exception:
            pass

    for name in ["sb_client", "user_email", "insights", "problems", "data_key", "flash"]:
        st.session_state.pop(name, None)

    st.session_state["uploader_version"] = st.session_state.get("uploader_version", 0) + 1


def save_report(title, html_text):
    client = get_client()
    if client is None:
        return False, "The account service is not set up."
    try:
        client.table("reports").insert({"title": title, "html": html_text}).execute()
    except Exception as error:
        return False, f"Could not save the report: {error}"
    return True, "Saved to your history."


def list_reports(limit=20):
    client = get_client()
    if client is None:
        return []
    try:
        result = (
            client.table("reports")
            .select("id, title, created_at, html")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
    except Exception:
        return []
    return result.data


def delete_report(report_id):
    client = get_client()
    if client is None:
        return False
    try:
        client.table("reports").delete().eq("id", report_id).execute()
    except Exception:
        return False
    return True