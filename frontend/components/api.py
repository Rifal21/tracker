import os

import httpx
import streamlit as st

DEFAULT_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def settings() -> tuple[str, str]:
    return (st.session_state.get("backend_url", DEFAULT_URL),
            st.session_state.get("api_key", os.getenv("API_KEY", "")))


def call(method: str, path: str, **kw):
    url, key = settings()
    try:
        r = httpx.request(method, url + path, headers={"X-API-Key": key}, timeout=20, **kw)
    except httpx.HTTPError as e:
        st.error(f"Backend tidak dapat dihubungi: {e}")
        return None
    if r.status_code >= 400:
        st.error(f"Error {r.status_code}: {r.json().get('detail', r.text) if r.content else ''}")
        return None
    return r.json()
