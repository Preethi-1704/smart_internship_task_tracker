import streamlit as st
import pandas as pd
from datetime import date
import hashlib

from src.database import get_connection, log_activity

STATUSES = ["To Do", "In Progress", "Testing", "Completed"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]


def manual_email_import(intern_map):
    st.subheader("Manual Email Import")

    with st.form("manual_email_import"):
        sender = st.text_input("Sender Email")

        subject = st.text_input("Email Subject")
        message = st.text_area("Email Task Details")

        assignee = st.selectbox(
            "Select Intern",
            list(intern_map)
        )

        priority = st.selectbox("Priority", PRIORITIES)
        due = st.date_input("Deadline", min_value=date.today())

        submit = st.form_submit_button("Import and Assign Task")

    if submit:
        if not subject.strip() or not message.strip():
            st.error("Enter email subject and task details.")
            return

        email_key = hashlib.sha256(
            (
                sender.strip().lower()
                + subject.strip().lower()
                + message.strip().lower()
            ).encode("utf-8")
        ).hexdigest()

        try:
            with get_connection() as con:
                existing = con.execute(
                    "SELECT id FROM gmail_imports WHERE message_id=?",
                    (email_key,)
                ).fetchone()

                if existing:
                    st.warning("This email is already imported.")
                    return

                cursor = con.execute(
                    """
                    INSERT INTO tasks
                    (title, description, assignee_id, priority,
                     due_date, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        subject.strip(),
                        message.strip(),
                        intern_map[assignee],
                        priority,
                        due.isoformat(),
                        st.session_state.user["id"]
                    )
                )

                con.execute(
                    """
                    INSERT INTO gmail_imports
                    (message_id, subject, sender, email_date, task_id)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        email_key,
                        subject.strip(),
                        sender.strip(),
                        "",
                        cursor.lastrowid
                    )
                )

            log_activity(
                st.session_state.user["id"],
                "TASK_CREATED",
                "Manual email: " + subject
            )

            st.success("Email task imported and assigned!")
            st.rerun()

        except Exception as e:
            st.error(f"Import failed: {e}")


def admin_tasks_view():
    st.title("Task Assignment & Tracking")

    with get_connection() as con:
        interns = con.execute("""
            SELECT id, name FROM users
            WHERE role='intern' AND active=1
            ORDER BY name
        """).fetchall()

    if not interns:
        st.warning("Create an active intern account first.")
        return

    intern_map = {
        f"{r['name']} (ID {r['id']})": r["id"]
        for r in interns
    }

    manual_email_import(intern_map)

    st.divider()
    st.subheader("Create Task Manually")

    with st.form("create_task"):
        title = st.text_input("Task Title")
        description = st.text_area("Task Description")
        assignee = st.selectbox("Assign Intern", list(intern_map))
        due = st.date_input("Task Deadline", min_value=date.today())
        priority = st.selectbox("Priority", PRIORITIES)

        save = st.form_submit_button("Assign Task")

    if save:
        if not title.strip() or not description.strip():
            st.error("Enter task title and description.")
        else:
            with get_connection() as con:
                con.execute("""
                    INSERT INTO tasks
                    (title, description, assignee_id, priority,
                     due_date, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    title.strip(),
                    description.strip(),
                    intern_map[assignee],
                    priority,
                    due.isoformat(),
                    st.session_state.user["id"]
                ))

            log_activity(
                st.session_state.user["id"],
                "TASK_CREATED",
                title
            )

            st.success("Task assigned successfully!")
            st.rerun()

    st.divider()
    st.subheader("All Intern Tasks")

    with get_connection() as con:
        rows = con.execute("""
            SELECT t.id, t.title, u.name AS intern,
                   t.priority, t.status, t.due_date
            FROM tasks t
            JOIN users u ON t.assignee_id = u.id
            ORDER BY t.id DESC
        """).fetchall()

    if rows:
        df = pd.DataFrame([dict(r) for r in rows])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Update Task Status")

        task_map = {
            f"#{r['id']} - {r['title']} ({r['intern']})": r["id"]
            for r in rows
        }

        selected = st.selectbox("Select Task", list(task_map))
        task_id = task_map[selected]
        status = st.selectbox("New Status", STATUSES)

        if st.button("Update Task"):
            with get_connection() as con:
                con.execute("""
                    UPDATE tasks SET status=?,
                    updated_at=CURRENT_TIMESTAMP WHERE id=?
                """, (status, task_id))

            log_activity(
                st.session_state.user["id"],
                "TASK_UPDATED",
                f"Task {task_id}: {status}"
            )

            st.success("Task updated!")
            st.rerun()
    else:
        st.info("No tasks created yet.")

    st.divider()
    st.subheader("Task History")

    with get_connection() as con:
        history = con.execute("""
            SELECT a.action, a.details, a.created_at, u.name
            FROM activity_logs a
            LEFT JOIN users u ON a.user_id=u.id
            WHERE a.action LIKE 'TASK_%'
               OR a.action='INTERN_TASK_UPDATE'
            ORDER BY a.id DESC
        """).fetchall()

    if history:
        st.dataframe(
            pd.DataFrame([dict(r) for r in history]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No task history yet.")


def intern_tasks_view(intern_id):
    st.title("My Assigned Tasks")

    with get_connection() as con:
        rows = con.execute("""
            SELECT * FROM tasks
            WHERE assignee_id=?
            ORDER BY due_date
        """, (intern_id,)).fetchall()

    if not rows:
        st.info("No tasks assigned to you yet.")
        return

    df = pd.DataFrame([dict(r) for r in rows])

    st.dataframe(
        df[["id", "title", "description", "priority",
            "status", "due_date"]],
        use_container_width=True,
        hide_index=True
    )

    task_map = {
        f"#{r.id} - {r.title}": int(r.id)
        for r in df.itertuples()
    }

    selected = st.selectbox("Select Your Task", list(task_map))
    task_id = task_map[selected]
    current = df[df.id == task_id].iloc[0]

    with st.form("intern_update"):
        status = st.selectbox(
            "Update Status",
            STATUSES,
            index=STATUSES.index(current.status)
        )
        details = st.text_area("Work Progress Details")
        submit = st.form_submit_button("Submit Work")

    if submit:
        with get_connection() as con:
            con.execute("""
                UPDATE tasks SET status=?,
                updated_at=CURRENT_TIMESTAMP
                WHERE id=? AND assignee_id=?
            """, (status, task_id, intern_id))

            if details.strip():
                con.execute("""
                    INSERT INTO submissions
                    (task_id, intern_id, work_details)
                    VALUES (?, ?, ?)
                """, (task_id, intern_id, details.strip()))

        log_activity(
            intern_id,
            "INTERN_TASK_UPDATE",
            f"Task {task_id}: {status}"
        )

        st.success("Work submitted successfully!")
        st.rerun()