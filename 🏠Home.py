"""
Module for the creating images for GetAmped Tournament.
"""

import pandas as pd
import streamlit as st
from PIL import Image

from utils import ACCESSORIES_FOLDER, ACCS_BY_YEAR_FILE, PLAYERS_FOLDER
from utils.image_utils import create_column_image, get_or_create_image
from utils.utils import pad_list


@st.cache_data
def get_accs_df():
    """Returns a dataframe containing the accessory data by year.

    The dataframe contains the columns:
        - ID: The accessory ID.
        - Icon: The accessory icon (not used).
        - Name: The accessory name.
        - Ano: The year the accessory was released.
    """
    return pd.read_excel(ACCS_BY_YEAR_FILE)


@st.cache_data
def get_printable_accs_df():
    """Returns a dataframe containing the accessory data by year.

    The dataframe contains the columns:
        - ID: The accessory ID.
        - Name: The accessory name.
        - Ano: The year the accessory was released.
    """
    accs_df = pd.read_excel(ACCS_BY_YEAR_FILE)
    accs_df.drop(columns=["Icon"], inplace=True)

    return accs_df


def create_composite_image(players_data, image_size):
    """Creates a composite image from a list of player data."""
    player_columns = []

    for player in players_data:
        name = player[0]
        accessories = player[1:]

        player_image = get_or_create_image(
            folder_path=PLAYERS_FOLDER,
            image_name=name,
            size=image_size,
        )
        column_images = [player_image]

        accessories = pad_list(accessories.copy())
        for accessory_id in accessories:
            # accessory_id = get_accessory_id(accessory)
            accessory_image = get_or_create_image(
                folder_path=ACCESSORIES_FOLDER,
                image_name=accessory_id,
                size=image_size,
            )
            column_images.append(accessory_image)

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


def create_team_image(team_members, players_data, image_size):
    """Creates an image for a team."""
    team_columns = []
    for member in team_members:
        # Find the member's data in players_data
        member_data = next((data for data in players_data if data[0] == member), None)
        if member_data is None:
            st.error(
                f"""A imagem do jogador {member} não foi encontrada. Talvez
                ele seja feio demais..."""
            )
            return None

        member_image = get_or_create_image(
            folder_path=PLAYERS_FOLDER,
            image_name=member,
            size=image_size,
        )
        column_images = [member_image]

        accessories = member_data[1:]
        accessories = pad_list(accessories.copy())
        for accessory_id in accessories:
            # accessory_id = get_accessory_id(accessory)
            accessory_image = get_or_create_image(
                folder_path=ACCESSORIES_FOLDER,
                image_name=accessory_id,
                size=image_size,
            )
            column_images.append(accessory_image)

        column_image = create_column_image(column_images)
        team_columns.append(column_image)

    # Create the team image
    total_width = sum(img.width for img in team_columns)
    max_height = max(img.height for img in team_columns)
    team_image = Image.new("RGB", (total_width, max_height))

    x_offset = 0
    for img in team_columns:
        team_image.paste(img, (x_offset, 0))
        x_offset += img.width

    return team_image


def get_accessory_id(accessory):
    if accessory == "no":
        return accessory

    accs_df = get_accs_df()
    acc_series = accs_df[accs_df["Name"].str.lower() == accessory.lower()]["ID"]
    if len(acc_series) > 0:
        return acc_series.values[0]

    return ""


def run_app():
    """Streamlit app for creating tournament and team images for GetAmped."""

    with st.sidebar:
        st.write("### Lista de acessórios")

        accs_df = get_printable_accs_df()

        acc_year_input = st.multiselect(
            label="Ano", options=accs_df["Ano"].unique().tolist(), key="acc_year_input"
        )

        if acc_year_input:
            accs_df = accs_df[accs_df["Ano"].isin(acc_year_input)]

        st.dataframe(accs_df.set_index(accs_df.columns[0]))

    st.markdown("## Criar imagens de acessórios")

    st.markdown("### Torneio")
    tournament_data_input = st.text_area(
        label="Insira os dados do torneio",
        height=200,
        placeholder="jogador1, id_acessorio1, id_acessorio2\njogador2, id_acessorio1, id_acessorio2",
        key="tournament_data_input",
    )

    input_tournament_image_size = st.selectbox(
        label="Selecione o tamanho da imagem",
        options=(32, 64, 94, 128),
        index=2,
        format_func=lambda x: f"{x}px",
        key="input_tournament_image_size",
    )

    if st.button(label="Criar imagem do Torneio", key="create_tournament_image"):
        if len(tournament_data_input) == 0:
            st.error(
                """Insira os dados do torneio, otário! Tá querendo ganhar
                título **JEGUE REI :horse::crown:**?"""
            )
            return

        players_data = validate_tournament_data(tournament_data_input)
        if players_data is None:
            return

        if "players_data" not in st.session_state:
            st.session_state.players_data = players_data
        else:
            st.session_state.players_data = players_data

        composite_image = create_composite_image(
            players_data=players_data,
            image_size=(input_tournament_image_size, input_tournament_image_size),
        )
        composite_image.save("generated_images/tournament_image.jpg")

        st.session_state.composite_image = composite_image

    if "composite_image" in st.session_state:
        st.image(
            image=Image.open("generated_images/tournament_image.jpg"),
            caption="Imagem do Torneio",
        )

    st.markdown("---")
    st.markdown("### Formação de Times")

    team_tournament_data_input = st.text_area(
        "Insira apenas os nomes dos jogadores informados acima",
        height=200,
        key="team_input",
        placeholder="jogador1, jogador2, jogador3\njogador4, jogador5, jogador6",
    )

    input_team_image_size = st.selectbox(
        label="Selecione o tamanho da imagem",
        options=(32, 64, 94, 128),
        index=2,
        format_func=lambda x: f"{x}px",
        key="input_team_image_size",
    )

    if st.button(label="Criar imagens dos Times", key="create_team_images"):
        if len(team_tournament_data_input) == 0:
            st.error(
                """Insira os dados dos times, otário! Tá querendo ganhar
                título **JEGUE REI :horse::crown:**?"""
            )
            return

        team_members_data = []
        for line in team_tournament_data_input.splitlines():
            if line.strip():  # Skip empty lines
                team_members = [item.strip() for item in line.split(",")]
                team_members_data.append(team_members)

        if "players_data" not in st.session_state:
            st.error(
                """Crie a imagem do torneio primeiro, otário! Tá querendo
                ganhar título **JEGUE REI :horse::crown:**?"""
            )
            return

        players_data = st.session_state.players_data

        for i, team_members in enumerate(team_members_data):
            team_image = create_team_image(
                team_members=team_members,
                players_data=players_data,
                image_size=(input_team_image_size, input_team_image_size),
            )
            if team_image is not None:
                team_image.save(f"generated_images/team_{i+1}.jpg")
                st.image(
                    image=Image.open(f"generated_images/team_{i+1}.jpg"),
                    caption=f"Time {i+1}",
                )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Lojas Boto Produções",
        page_icon=":flipper:",
    )

    run_app()
