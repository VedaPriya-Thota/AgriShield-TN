"""
AgriShield-TN · Multi-page Streamlit entry point.
Navigation is rendered by inject_sidebar_brand() via st.page_link so we have
full CSS control. st.navigation uses position="hidden".
"""
import sys
from pathlib import Path

_APP_DIR      = Path(__file__).resolve().parent
_PROJECT_ROOT = _APP_DIR.parent
for _p in [str(_PROJECT_ROOT), str(_APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

st.set_page_config(
    page_title="AgriShield-TN · Paddy Disease AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

from _shared import inject_css, inject_sidebar_brand, inject_header  # noqa: E402

inject_css()

# st.navigation MUST be called before any st.page_link call so pages are registered.
pg = st.navigation(
    [
        st.Page("pages/1_Home.py",            title="Home",        icon="🏠", default=True),
        st.Page("pages/2_Analyze_Leaf.py",    title="Diagnose",    icon="🩺"),
        st.Page("pages/3_What_To_Do.py",      title="Action Plan", icon="⚡"),
        st.Page("pages/6_Disease_Library.py", title="Field Guide", icon="📖"),
    ],
    position="hidden",
)

inject_header()         # after st.navigation() — st.page_link now resolves url_pathname
inject_sidebar_brand()
pg.run()
