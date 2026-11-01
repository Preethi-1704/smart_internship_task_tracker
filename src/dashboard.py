import streamlit as st
from src.database import get_connection


def admin_dashboard_view():
    st.title("Admin Dashboard")

    with get_connection() as con:
        total = con.execute(
            "SELECT COUNT(*) FROM users WHERE role='intern'"
        ).fetchone()[0]

        tasks = con.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        completed = con.execute(
            "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
        ).fetchone()[0]

        pending = tasks - completed

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Interns", total)
    c2.metric("Total Tasks", tasks)
    c3.metric("Completed Tasks", completed)

    st.metric("Incomplete Tasks", pending)


def intern_dashboard_view(user_id):
    st.title("My Dashboard")
    st.subheader("My Progress")

    with get_connection() as con:
        total = con.execute(
            "SELECT COUNT(*) FROM tasks WHERE assignee_id=?",
            (user_id,)
        ).fetchone()[0]

        completed = con.execute(
            """SELECT COUNT(*) FROM tasks
            WHERE assignee_id=? AND status='Completed'""",
            (user_id,)
        ).fetchone()[0]

        progress = con.execute(
            """SELECT COUNT(*) FROM tasks
            WHERE assignee_id=? AND status='In Progress'""",
            (user_id,)
        ).fetchone()[0]

        incomplete = total - completed

        rows = con.execute(
            """SELECT title, status, priority, due_date
            FROM tasks WHERE assignee_id=?
            ORDER BY id DESC""",
            (user_id,)
        ).fetchall()

    percentage = (completed / total * 100) if total else 0

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Tasks", total)
    c2.metric("Completed", completed)
    c3.metric("Incomplete", incomplete)

    st.metric("In Progress", progress)

    st.subheader("Overall Progress")
    st.progress(int(percentage))
    st.write(f"{percentage:.1f}% Completed")

    st.subheader("Task Status Details")

    if rows:
        for row in rows:
            with st.expander(row["title"]):
                st.write("Status:", row["status"])
                st.write("Priority:", row["priority"])
                st.write("Due Date:", row["due_date"])
    else:
        st.info("No tasks assigned yet.")