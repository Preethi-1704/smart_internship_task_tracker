import sys
from pathlib import Path

import streamlit as st

# Project folder path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(SRC_DIR))

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
    st.info("Please check that all Python files are inside the src folder.")
    st.stop()


st.set_page_config(
    page_title="Internship Task Tracker",
    page_icon="📌",
    layout="wide"
)


# Initialize database
init_db()
seed_admin()


def main():

    if "user" not in st.session_state:
        st.session_state.user = None

    if not st.session_state.user:
        login_view()
        return

    user = st.session_state.user

    with st.sidebar:
        st.title("📌 Internship Task Tracker")
        st.caption(f"Signed in as {user['name']}")
        st.caption(user["role"].title())

        if user["role"] == "admin":
            pages = [
                "Dashboard",
                "Manage Interns",
                "Manage Tasks",
                "Publish Announcements",
                "Reports"
            ]
        else:
            pages = [
                "My Dashboard",
                "My Tasks",
                "Announcements"
            ]

        page = st.radio("Navigation", pages)

        st.divider()

        if st.button("Log out", use_container_width=True):
            logout()
            st.rerun()

    if page == "Dashboard":
        admin_dashboard_view()

    elif page == "Manage Interns":
        admin_interns_view()

    elif page == "Manage Tasks":
        admin_tasks_view()

    elif page == "Publish Announcements":
        admin_announcements_view()

    elif page == "Reports":
        reports_view()

    elif page == "My Dashboard":
        intern_dashboard_view(user["id"])

    elif page == "My Tasks":
        intern_tasks_view(user["id"])

    elif page == "Announcements":
        intern_announcements_view()


if __name__ == "__main__":
    main()
