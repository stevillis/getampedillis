import streamlit as st

from backend.utils import PLAYERS_FOLDER
from backend.utils.auth import require_login
from backend.utils.image_utils import get_or_create_image, handle_player_image_upload
from backend.utils.utils import load_players_df

if __name__ == "__main__":
    require_login("🔒Login.py")

    st.set_page_config(
        page_title="Adicionar imagens de jogadores",
        page_icon=":flipper:",
    )

    st.markdown("## Adicionar imagens de jogadores")

    if st.session_state.get("role") in ("admin", "player"):
        uploaded_file = st.file_uploader(
            label="Adicionar imagem de jogador",
            type=["png", "jpg", "jpeg"],
        )

        if uploaded_file is not None:
            player_name_input = st.text_input(
                label="Nome do jogador", key="player_name_input", max_chars=20
            )
            if st.button(label="Fazer upload"):
                status, message = handle_player_image_upload(
                    player_name=player_name_input,
                    uploaded_file=uploaded_file,
                )

                if status == "error":
                    st.error(message)
                elif status == "success":
                    st.success(message)
    else:
        st.info("Você não tem permissão para fazer upload de imagens de jogadores.")

    with st.sidebar:
        st.write("### Lista de jogadores")
        with st.container(height=250):
            players_df = load_players_df()
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
