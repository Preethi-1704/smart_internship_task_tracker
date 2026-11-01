import streamlit as st
import pandas as pd
from src.database import get_connection, log_activity

def admin_interns_view():
    st.title("👥 Intern Management")
    with st.expander("Add a new intern", expanded=True):
        with st.form("add_intern"):
            name = st.text_input("Full name")
            username = st.text_input("Username")
            password = st.text_input("Temporary password (8+ characters)", type="password")
            skills = st.text_input("Skills, separated by commas")
            save = st.form_submit_button("Add intern")
        if save:
            try:
                from src.auth import create_user
                create_user(name, username, password, "intern", skills)
                st.success("Intern account created.")
                st.rerun()
            except Exception as exc:
                st.error(f"Validation/database error: {exc}")
    with get_connection() as con:
        rows = con.execute("""SELECT id,name,username,skills,created_at,active
                              FROM users WHERE role='intern' ORDER BY id DESC""").fetchall()
    if rows:
        df = pd.DataFrame([dict(r) for r in rows])
        st.dataframe(df, use_container_width=True, hide_index=True)
        ids = {f"{r['name']} (@{r['username']})": r['id'] for r in rows}
        chosen = st.selectbox("Select intern to activate/deactivate", list(ids))
        active = st.selectbox("Account status", ["Active", "Inactive"])
        if st.button("Update account status"):
            with get_connection() as con:
                con.execute("UPDATE users SET active=? WHERE id=?", (1 if active=="Active" else 0, ids[chosen]))
            log_activity(st.session_state.user["id"], "ACCOUNT_STATUS", f"{chosen}: {active}")
            st.success("Account status updated.")
            st.rerun()
    else:
        st.info("No interns registered yet.")
