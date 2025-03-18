import streamlit as st

if __name__ == "__main__":
    st.set_page_config(
        page_title="Lojas Boto Produções",
        page_icon=":flipper:",
    )

    uploaded_file = st.file_uploader(
        label="Adicionar imagem de jogador", type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:
        player_name_input = st.text_input(
            label="Nome do jogador", key="player_name_input"
        )
        if st.button(label="Fazer upload"):
            if player_name_input == "":
                st.error(
                    """Coloque o nome do jogador, otário! Tá querendo ganhar
                    título **JEGUE REI :horse::crown:**?
                    """
                )
            else:
                with open(f"data/players/{player_name_input}.png", "wb") as f:
                    f.write(uploaded_file.getvalue())

                st.success("Imagem adicionada com sucesso!")
