import streamlit as st

from backend.utils.auth import authenticate_user


def login_form():
    st.header("Login")
    st.info(
        "Para testar o site como visitante, use o usuário **guest** e a senha **guest**."
    )
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
    if login_btn:
        if username == "guest" and password == "guest":
            st.session_state.logged_in = True
            st.session_state.login = username
            st.session_state.role = "guest"
            st.success("Login como visitante realizado com sucesso! Redirecionando...")
            st.rerun()
        else:
            success, role = authenticate_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.login = username
                st.session_state.role = role
                st.success("Login realizado com sucesso! Redirecionando...")
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
