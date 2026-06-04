import time

import streamlit as st

from backend.utils.auth import authenticate_user
from backend.utils.utils import apply_custom_theme


def login_form():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div style='text-align: center;'>
                <h2>🔒 Acesso Seguro</h2>
                <p style='color: gray;'>Faça login para acessar o painel de administração e funcionalidades exclusivas.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        username = st.text_input(
            "Usuário",
            key="login_username",
            placeholder="Digite seu nome de usuário",
        )

        password = st.text_input(
            "Senha",
            type="password",
            key="login_password",
            placeholder="Digite sua senha",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        login_btn = st.button("Entrar", key="login_btn", use_container_width=True)

        placeholder = st.empty()

        if login_btn:
            if not username or not password:
                placeholder.error("Por favor, preencha usuário e senha.")
                return

            with st.spinner("Autenticando..."):
                success, role = authenticate_user(username, password)

            if success:
                placeholder.empty()

                st.session_state.logged_in = True
                st.session_state.login = username
                st.session_state.role = role

                if not st.session_state.get("showed_login_balloons", False):
                    st.balloons()
                    st.session_state["showed_login_balloons"] = True

                with placeholder.container():
                    st.success("Login realizado com sucesso! Redirecionando...")
                    time.sleep(1)

                placeholder.empty()
                st.rerun()
            else:
                st.session_state.logged_in = False
                placeholder.error("Usuário ou senha incorretos. Tente novamente.")


if __name__ == "__main__":
    st.set_page_config(page_title="Login", page_icon="🔒", layout="centered")

    apply_custom_theme()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        st.switch_page("pages/7_Painel_Admin.py")
    else:
        login_form()
