import os

import bcrypt
import psycopg2
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def require_login(login_page="🔒Login.py"):
    """Redirects to login page if user is not logged in."""
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.switch_page(login_page)


def authenticate_user(login: str, password: str):
    """
    Authenticate user against the users and roles tables.
    Returns (True, role_name) if successful, else (False, None).
    """
    try:
        connection = psycopg2.connect(
            user=os.getenv("GETAMPEDVIVE_USER"),
            password=os.getenv("GETAMPEDVIVE_PASSWORD"),
            host=os.getenv("GETAMPEDVIVE_HOST"),
            port=os.getenv("GETAMPEDVIVE_PORT"),
            dbname=os.getenv("GETAMPEDVIVE_DBNAME"),
        )

        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT u.password, r.name
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.login = %s
            """,
            (login,),
        )

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result is None:
            return False, None

        stored_password, role_name = result

        if bcrypt.checkpw(password.encode(), stored_password.encode()):
            return True, role_name
        else:
            return False, None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return False, None
