import sys
from pathlib import Path

import streamlit as st

st.set_page_config(
    st.title("Internship Task Tracker")
    st.success("Streamlit App is Working!")
    page_title="Internship Task Tracker",
    page_icon="📌",
    layout="wide"
)

# Project root path
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

sys.path.insert(0, str(PROJECT_ROOT))

# Import project modules
try:
    from src.database import init_db, seed_admin
    from src.auth import login_view, logout
    from src.interns import admin_interns_view
    from src.tasks import admin_tasks_view, intern_tasks_view
    from src.dashboard import admin_dashboard_view, intern_dashboard_view
    from src.reports import reports_view
    from src.announcements import (
        admin_announcements_view,
        intern_announcements_view
    )

except ModuleNotFoundError as e:
    st.error(f"Module not found: {e}")
    st.info("Please check the Python files inside the src folder.")
    st.stop()
