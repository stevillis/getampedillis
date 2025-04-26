import time

import streamlit as st

from backend.utils.auth import authenticate_user


def login_form():
    st.header("Login")

    username = st.text_input(
        "Usuário",
        key="login_username",
    )

    password = st.text_input(
        "Senha",
        type="password",
        key="login_password",
    )

    login_btn = st.button("Entrar", key="login_btn")

    placeholder = st.empty()
    with placeholder.container():
        st.info(
            "Para testar o site como visitante, use o usuário **guest** e a senha **guest**."
        )

    if login_btn:
        success, role = authenticate_user(username, password)
        if success:
            placeholder.empty()

            st.session_state.logged_in = True
            st.session_state.login = username
            st.session_state.role = role

            if not st.session_state.get("showed_login_balloons", False):
                st.balloons()
                time.sleep(2)
                st.session_state["showed_login_balloons"] = True

            with placeholder.container():
                st.success("Login realizado com sucesso! Redirecionando...")
                time.sleep(2)

            placeholder.empty()

            st.rerun()  # Ensures session state is updated before redirect
        else:
            st.session_state.logged_in = False
            st.error("Usuário ou senha incorretos.")


if __name__ == "__main__":
    st.set_page_config(page_title="Login", page_icon=":lock:")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        st.switch_page("pages/1_🗡️_Criar_imagens_de_acessórios.py")
    else:
        login_form()
