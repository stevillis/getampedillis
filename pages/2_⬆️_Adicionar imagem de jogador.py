import streamlit as st

from backend.utils import PLAYERS_FOLDER
from backend.utils.image_utils import get_or_create_image
from backend.utils.utils import get_players_df

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
            label="Nome do jogador", key="player_name_input", max_chars=20
        )
        if st.button(label="Fazer upload"):
            if player_name_input == "":
                st.error(
                    """Coloque o nome do jogador, otário! Tá querendo ganhar
                    título **JEGUE REI :horse::crown:**?
                    """
                )
            else:
                with open(f"{PLAYERS_FOLDER}/{player_name_input}.png", "wb") as f:
                    f.write(uploaded_file.getvalue())

                st.success("Imagem adicionada com sucesso!")

    with st.sidebar:
        st.write("### Lista de jogadores")
        with st.container(height=250):
            players_df = get_players_df()
            num_cols = 5
            num_rows = (len(players_df) + num_cols - 1) // num_cols

            for i in range(num_rows):
                cols = st.columns(num_cols)
                for j, col in enumerate(cols):
                    index = i * num_cols + j
                    if index < len(players_df):
                        player_name = players_df.iloc[index]["Name"]
                        player_image = get_or_create_image(
                            folder_path=PLAYERS_FOLDER,
                            image_name=player_name,
                            size=(32, 32),
                        )
                        with col:
                            st.image(player_image)
                            st.write(
                                f'<span style="font-size: 10px;">{player_name}</span>',
                                unsafe_allow_html=True,
                            )
