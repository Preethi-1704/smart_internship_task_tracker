import streamlit as st
import uuid
from src.database import get_connection


def create_announcement_table():
    with get_connection() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                subject TEXT,
                sender TEXT,
                email_date TEXT,
                message TEXT,
                published_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def admin_announcements_view():
    create_announcement_table()

    st.title("📢 Publish Announcements")
    st.write("Share important updates with all interns.")

    with st.form("publish_message"):
        subject = st.text_input("Announcement Title")
        message = st.text_area("Announcement Message")

        publish = st.form_submit_button(
            "Publish to All Interns"
        )

    if publish:
        if subject.strip() and message.strip():
            with get_connection() as con:
                con.execute("""
                    INSERT INTO announcements
                    (message_id, subject, sender, message)
                    VALUES (?, ?, ?, ?)
                """, (
                    uuid.uuid4().hex,
                    subject.strip(),
                    st.session_state.user["name"],
                    message.strip()
                ))

            st.success("Announcement published successfully!")
            st.rerun()
        else:
            st.warning("Please enter title and message.")

    st.divider()
    st.subheader("Published Announcements")

    with get_connection() as con:
        rows = con.execute("""
            SELECT * FROM announcements
            ORDER BY id DESC
        """).fetchall()

    if rows:
        for row in rows:
            with st.expander(row["subject"]):
                st.write(row["message"])
                st.write("Published by:", row["sender"])
                st.caption("Published: " + row["published_at"])
    else:
        st.info("No announcements published yet.")


def intern_announcements_view():
    create_announcement_table()

    st.title("📢 Announcements")
    st.write("Important updates and announcements.")

    with get_connection() as con:
        rows = con.execute("""
            SELECT subject, sender, message, published_at
            FROM announcements
            ORDER BY id DESC
        """).fetchall()

    if rows:
        for row in rows:
            with st.expander(row["subject"]):
                st.write(row["message"])
                st.write("Published by:", row["sender"])
                st.caption("Published: " + row["published_at"])
    else:
        st.info("No announcements available.")