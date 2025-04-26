import os
from datetime import datetime

import bcrypt
import psycopg2
import streamlit as st
from dotenv import load_dotenv

from backend.utils.auth import require_login

if __name__ == "__main__":
    load_dotenv()
    DB_USER = os.getenv("GETAMPEDVIVE_USER")
    DB_PASSWORD = os.getenv("GETAMPEDVIVE_PASSWORD")
    DB_HOST = os.getenv("GETAMPEDVIVE_HOST")
    DB_PORT = os.getenv("GETAMPEDVIVE_PORT")
    DB_NAME = os.getenv("GETAMPEDVIVE_DBNAME")

    st.set_page_config(page_title="Criar Usuário (Admin)", page_icon=":crown:")

    require_login("🔒Login.py")

    if st.session_state.get("role") != "admin":
        st.error("Apenas administradores podem acessar esta página.")
        st.stop()

    st.title("Criar novo usuário")

    with st.form("create_user_form"):
        created_at = st.date_input("Data de criação", value=datetime.now()).strftime(
            "%Y-%m-%d"
        )
        login = st.text_input("Login")
        password = st.text_input("Senha", type="password")

        roles = []
        try:
            conn = psycopg2.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
            )

            cur = conn.cursor()

            cur.execute("SELECT role_id, name FROM roles ORDER BY name")

            roles = cur.fetchall()

            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Erro ao buscar papéis: {e}")

        role_options = {name: role_id for role_id, name in roles}
        role_name = st.selectbox("Papel do usuário", list(role_options.keys()))
        role_id = role_options.get(role_name)

        submit = st.form_submit_button("Criar usuário")

        if submit:
            if not login or not password or not role_id:
                st.warning("Login, senha e papel são obrigatórios.")
            else:
                try:
                    hashed_pw = bcrypt.hashpw(
                        password.encode(), bcrypt.gensalt()
                    ).decode()
                    conn = psycopg2.connect(
                        user=DB_USER,
                        password=DB_PASSWORD,
                        host=DB_HOST,
                        port=DB_PORT,
                        dbname=DB_NAME,
                    )

                    cur = conn.cursor()

                    cur.execute(
                        "INSERT INTO users (created_at, login, password, role_id) VALUES (%s, %s, %s, %s)",
                        (created_at, login, hashed_pw, role_id),
                    )

                    conn.commit()

                    cur.close()
                    conn.close()

                    st.success(f"Usuário '{login}' criado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao criar usuário: {e}")
