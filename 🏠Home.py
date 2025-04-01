"""
Module for the creating images for GetAmped Tournament.
"""

import pandas as pd
import streamlit as st
from PIL import Image

from utils import ACCESSORIES_FOLDER, ACCS_BY_YEAR_FILE, PLAYERS_FOLDER
from utils.image_utils import create_column_image, get_or_create_image
from utils.utils import get_players_df, pad_list


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
    accs_df.set_index("Name", inplace=True)
    accs_df["Icon"] = accs_df["ID"].apply(
        lambda x: f"https://github.com/stevillis/tournament_image_creator/blob/master/data/accs/{x}.png?raw=true"
    )
    accs_df["selected"] = False

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


def update_tournament_data():
    st.session_state.tournament_data = st.session_state.tournament_data_input


def update_team_data():
    st.session_state.team_tournament_data = st.session_state.team_tournament_data_input


def run_app():
    """Streamlit app for creating tournament and team images for GetAmped."""

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

    st.markdown("## Criar imagens de acessórios")

    st.write("#### Lista de acessórios")

    accs_df = get_printable_accs_df()

    acc_year_input = st.multiselect(
        label="Ano", options=accs_df["Ano"].unique().tolist(), key="acc_year_input"
    )

    if acc_year_input:
        accs_df = accs_df[accs_df["Ano"].isin(acc_year_input)]

    edited_accs_df = st.data_editor(
        accs_df,
        width=500,
        column_config={
            "selected": st.column_config.CheckboxColumn(
                "Adicionar acessório",
                help="Marque para adicionar o acessório ao torneio",
                default=False,
            ),
            "Icon": st.column_config.ImageColumn("Icon", help=""),
        },
        disabled=["Name", "ID", "Ano", "Icon"],
    )

    selected_ids = edited_accs_df[edited_accs_df["selected"] == True]["ID"].tolist()
    for acc_id in selected_ids:
        st.session_state.tournament_data += f", {acc_id}"
        edited_accs_df.loc[edited_accs_df["ID"] == acc_id, "selected"] = False

    st.session_state.accs_df = edited_accs_df

    st.markdown("### Torneio")

    if "tournament_data" not in st.session_state:
        st.session_state.tournament_data = ""

    tournament_data_input = st.text_area(
        label="Insira os dados do torneio",
        height=200,
        placeholder="jogador1, id_acessorio1, id_acessorio2\njogador2, id_acessorio1, id_acessorio2",
        value=st.session_state.tournament_data,
        key="tournament_data_input",
        on_change=update_tournament_data,
    )

    input_tournament_image_size = st.selectbox(
        label="Selecione o tamanho da imagem",
        options=(32, 64, 94, 128),
        index=2,
        format_func=lambda x: f"{x}px",
        key="input_tournament_image_size",
    )

    if st.button(label="Criar imagem do Torneio", key="create_tournament_image"):
        if len(st.session_state.tournament_data) == 0:
            st.error(
                """Insira os dados do torneio, otário! Tá querendo ganhar
                título **JEGUE REI :horse::crown:**?"""
            )
            return

        players_data = validate_tournament_data(st.session_state.tournament_data)
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

    if "team_tournament_data" not in st.session_state:
        st.session_state.team_tournament_data = ""

    team_tournament_data_input = st.text_area(
        "Insira apenas os nomes dos jogadores informados acima",
        height=200,
        key="team_tournament_data_input",
        placeholder="jogador1, jogador2, jogador3\njogador4, jogador5, jogador6",
        value=st.session_state.team_tournament_data,
        on_change=update_team_data,
    )

    input_team_image_size = st.selectbox(
        label="Selecione o tamanho da imagem",
        options=(32, 64, 94, 128),
        index=2,
        format_func=lambda x: f"{x}px",
        key="input_team_image_size",
    )

    if st.button(label="Criar imagens dos Times", key="create_team_images"):
        if len(st.session_state.team_tournament_data) == 0:
            st.error(
                """Insira os dados dos times, otário! Tá querendo ganhar
                título **JEGUE REI :horse::crown:**?"""
            )
            return

        team_members_data = []
        for line in st.session_state.team_tournament_data.splitlines():
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
