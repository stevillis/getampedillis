import streamlit as st

from utils.config import set_config_variables


def run_app():
    st.write("## Criador de Imagens de Torneio GetAmped")

    col1, col2 = st.columns(2)
    with col1:
        btn_create_accs_images = st.button(
            label="Criar imagens com acessórios", key="create_accs_images"
        )
        if btn_create_accs_images:
            st.switch_page(page="./pages/1_🔨_Criar imagem de acessórios.py")

    with col2:
        btn_create_styles_images = st.button(
            label="Criar imagens com estilos", key="create_styles_images"
        )
        if btn_create_styles_images:
            st.switch_page(page="./pages/2_💪_Criar imagem de estilos.py")

    st.image("lojas_boto.png")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Lojas Boto Produções",
        page_icon=":house:",
    )

    set_config_variables()
    run_app()
