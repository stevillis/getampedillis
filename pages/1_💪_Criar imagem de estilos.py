import streamlit as st
from PIL import Image

from utils.config import set_config_variables
from utils.image_utils import create_column_image, get_or_create_image
from utils.utils import pad_list


def create_composite_image(players_data, image_size):
    """Creates a composite image from a list of player data."""
    player_columns = []

    for player in players_data:
        name = player[0]
        styles = player[1:]

        player_image = get_or_create_image(
            folder_path=st.session_state.PLAYERS_FOLDER,
            image_name=name,
            size=image_size,
        )
        column_images = [player_image]

        styles = pad_list(styles.copy())
        for style_name in styles:
            style_image = get_or_create_image(
                folder_path=st.session_state.STYLES_FOLDER,
                image_name=style_name,
                size=image_size,
            )
            column_images.append(style_image)

        column_image = create_column_image(column_images)
        player_columns.append(column_image)

    # Create the final composite image
    total_width = sum(img.width for img in player_columns)
    max_height = max(img.height for img in player_columns)
    composite_image = Image.new("RGB", (total_width, max_height))

    x_offset = 0
    for img in player_columns:
        composite_image.paste(img, (x_offset, 0))
        x_offset += img.width

    return composite_image


def validate_tournament_data(tournament_data):
    """Validates the input data format."""
    players_data = []
    for line in tournament_data.splitlines():
        if line.strip():  # Skip empty lines
            player_data = [item.strip() for item in line.split(",")]
            if len(player_data) < 2:
                st.error(
                    """Formato inválido, otário! Tá querendo ganhar título
                    **JEGUE REI :horse::crown:**?
                    """
                )
                return None
            players_data.append(player_data)
    return players_data


def run_app():
    st.markdown("## Criar imagem de estilos")

    tournament_data_input = st.text_area(
        label="Insira os dados dos jogadores e seus estilos",
        height=200,
        placeholder="jogador1, estilo1, estilo2\njogador2, estilo1, estilo2",
        key="tournament_data_input",
    )

    style_slider_image_size = st.slider(
        label="Selecione o tamanho da imagem",
        min_value=32,
        max_value=300,
        value=72,
        key="style_slider_image_size",
    )

    if st.button(label="Criar imagem de estilos", key="create_tournament_image"):
        if len(tournament_data_input) == 0:
            st.error(
                """Insira os dados dos jogadores e seus estilos, otário! Tá querendo ganhar
                título **JEGUE REI :horse::crown:**?"""
            )
            return

        players_data = validate_tournament_data(tournament_data_input)
        if players_data is None:
            return

        if "player_styles_data" not in st.session_state:
            st.session_state.player_styles_data = players_data
        else:
            st.session_state.player_styles_data = players_data

        composite_image = create_composite_image(
            players_data=players_data,
            image_size=(style_slider_image_size, style_slider_image_size),
        )
        composite_image.save("generated_images/tournament_style_image.jpg")

        st.session_state.composite_style_image = composite_image

    if "composite_style_image" in st.session_state:
        st.image(
            image=Image.open("generated_images/tournament_style_image.jpg"),
            caption="Imagem dos jogadores e seus estilos",
        )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Lojas Boto Produções",
        page_icon=":flipper:",
    )

    set_config_variables()
    run_app()
