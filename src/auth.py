import streamlit as st
import hashlib
import hmac
import os

from src.database import get_connection, log_activity


def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200000
    ).hex()

    return digest, salt


def verify_password(password, stored_hash, salt):
    digest, _ = hash_password(password, salt)
    return hmac.compare_digest(digest, stored_hash)


def create_user(name, username, password, role="intern", skills=""):
    if not name.strip() or not username.strip() or not password:
        raise ValueError("All fields are required.")

    if len(password) < 8:
        raise ValueError("Password must have at least 8 characters.")

    digest, salt = hash_password(password)

    with get_connection() as con:
        con.execute(
            """
            INSERT INTO users
            (name, username, password_hash, salt, role, skills)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name.strip(), username.strip().lower(),
             digest, salt, role, skills.strip())
        )

    return True


def authenticate(username, password):
    with get_connection() as con:
        row = con.execute(
            "SELECT * FROM users WHERE username=? AND active=1",
            (username.strip().lower(),)
        ).fetchone()

    if row and verify_password(
        password, row["password_hash"], row["salt"]
    ):
        user = dict(row)
        log_activity(user["id"], "LOGIN", "Successful login")
        return user

    return None


def logout():
    st.session_state.user = None


def login_view():
    st.title("📌 Smart Internship Task Tracking System")

    if st.session_state.pop("show_login_after_register", False):
        st.success("Registration successful!")
        page = "Intern Login"
    else:
        page = st.radio(
            "Select Login Type",
            ["Admin Login", "Intern Login", "Intern Registration"],
            horizontal=True
        )

    if page in ["Admin Login", "Intern Login"]:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = authenticate(username, password)

            if user:
                if page == "Admin Login" and user["role"] != "admin":
                    st.error("Please use an Admin account.")
                elif page == "Intern Login" and user["role"] != "intern":
                    st.error("Please use an Intern account.")
                else:
                    st.session_state.user = user
                    st.rerun()
            else:
                st.error("Invalid username or password.")

    else:
        name = st.text_input("Full Name")
        new_username = st.text_input("Choose Username")
        new_password = st.text_input(
            "Create Password (minimum 8 characters)",
            type="password"
        )
        skills = st.text_input("Skills")

        if st.button("Register Intern"):
            try:
                create_user(
                    name, new_username, new_password, "intern", skills
                )
                st.session_state.show_login_after_register = True
                st.rerun()
            except Exception as exc:
                st.error(f"Registration failed: {exc}")