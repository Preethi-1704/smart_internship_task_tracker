import sys
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Internship Task Tracker",
    page_icon="📌",
    layout="wide"
)

st.title("Internship Task Tracker")

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

# Initialize database
init_db()
seed_admin()

# Login and application flow
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    login_view()
else:
    user = st.session_state.user

    with st.sidebar:
        st.write(f"Welcome, {user.get('name', 'User')}")
        if st.button("Logout"):
            logout()
            st.rerun()

    if user.get("role") == "admin":
        page = st.sidebar.radio(
            "Navigation",
            ["Dashboard", "Interns", "Tasks", "Reports", "Announcements"]
        )

        if page == "Dashboard":
            admin_dashboard_view()
        elif page == "Interns":
            admin_interns_view()
        elif page == "Tasks":
            admin_tasks_view()
        elif page == "Reports":
            reports_view()
        elif page == "Announcements":
            admin_announcements_view()

    else:
        page = st.sidebar.radio(
            "Navigation",
            ["Dashboard", "My Tasks", "Announcements"]
        )

        if page == "Dashboard":
            intern_dashboard_view()
        elif page == "My Tasks":
            intern_tasks_view(user["id"])
        elif page == "Announcements":
            intern_announcements_view()
