import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(page_title="FKPhone Tracker", page_icon="📱", layout="wide")

from pages import dashboard, history, lookup, osint, settings  # noqa: E402
from pages import about, location  # noqa: E402

nav = st.navigation([
    st.Page(dashboard.render, title="Dashboard", icon="📊", url_path="dashboard", default=True),
    st.Page(lookup.render, title="Phone Number Lookup", icon="🔎", url_path="lookup"),
    st.Page(osint.render, title="OSINT Search", icon="🌐", url_path="osint"),
    st.Page(location.render, title="Location Sharing", icon="📍", url_path="location"),
    st.Page(history.render, title="Search History", icon="🕘", url_path="history"),
    st.Page(settings.render, title="Settings", icon="⚙️", url_path="settings"),
    st.Page(about.render, title="About Application", icon="ℹ️", url_path="about"),
])
st.sidebar.caption("FKPhone Tracker v1.0.0 · FKStudio IT Solution")
nav.run()
