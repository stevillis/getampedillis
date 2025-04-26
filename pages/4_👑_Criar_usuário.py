from datetime import datetime

import streamlit as st

from backend.repository import user_repository
from backend.utils.auth import require_login

if __name__ == "__main__":
    st.set_page_config(page_title="Criar Usuário (Admin)", page_icon=":flipper:")
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

        try:
            roles = user_repository.fetch_roles()
        except Exception as e:
            st.error(str(e))
            roles = []

        role_options = {name: role_id for role_id, name in roles}
        role_name = st.selectbox("Papel do usuário", list(role_options.keys()))
        role_id = role_options.get(role_name)

        submit = st.form_submit_button("Criar usuário")

        if submit:
            if not login or not password or not role_id:
                st.warning("Login, senha e papel são obrigatórios.")
            else:
                try:
                    user_repository.create_user(created_at, login, password, role_id)
                    st.success(f"Usuário '{login}' criado com sucesso!")
                except Exception as e:
                    st.error(str(e))
