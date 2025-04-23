"""
Module for the creating images for GetAmped Tournament.
"""

import time

import pandas as pd
import streamlit as st
from PIL import Image

from utils import (
    ACCESSORIES_FOLDER,
    ACCS_BY_YEAR_FILE,
    PLAYERS_FOLDER,
    SHOW_TROLL_INTRO,
    TIRIRICAS_PATH,
)
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

        st.write("### Lista de acessórios")
        printable_accs_df = get_printable_accs_df()

        acc_year_input = st.multiselect(
            label="Ano",
            options=printable_accs_df["Ano"].unique().tolist(),
            key="acc_year_input",
        )

        if acc_year_input:
            printable_accs_df = printable_accs_df[
                printable_accs_df["Ano"].isin(acc_year_input)
            ]

        edited_printable_accs_df = st.data_editor(
            printable_accs_df,
            width=500,
            disabled=["Name", "ID", "Ano", "Icon"],
            column_config={
                "Icon": st.column_config.ImageColumn("Icon", help=""),
            },
        )

    st.markdown("## Criar imagens de acessórios")

    st.markdown("### Torneio")

    player_options = players_df["Name"].tolist()

    player_name_input = st.selectbox(
        "Selecione o jogador",
        player_options,
        key="player_name_input",
    )

    accs_df = get_accs_df().sort_values(by="ID")
    acc_options = accs_df["ID"].tolist()
    selected_accs_input = st.multiselect(
        "Selecione os acessórios",
        acc_options,
        key="selected_accs_input",
    )

    if st.button("Adicionar seleção ao campo de texto"):
        if not selected_accs_input:
            st.error(
                "Selecione pelo menos um acessório, otário! Tá querendo ganhar título **JEGUE REI :horse::crown:**?"
            )
        else:
            # Compose the string: player,acc1,acc2,...
            line = player_name_input

            if selected_accs_input:
                line += "," + ",".join(selected_accs_input)

            if "tournament_data_input" not in st.session_state:
                st.session_state["tournament_data_input"] = ""

            if st.session_state["tournament_data_input"]:
                st.session_state["tournament_data_input"] += "\n" + line
            else:
                st.session_state["tournament_data_input"] = line

        selected_accs_input = []

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
        if len(st.session_state.tournament_data_input) == 0:
            st.error(
                """Insira os dados do torneio, otário! Tá querendo ganhar
                título **JEGUE REI :horse::crown:**?"""
            )
            return

        players_data = validate_tournament_data(st.session_state.tournament_data_input)
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

    # Get player names used in the Torneio section
    tournament_players = []
    if "tournament_data_input" in st.session_state:
        for line in st.session_state["tournament_data_input"].splitlines():
            if line.strip():
                player_name = line.split(",")[0].strip()
                if player_name:
                    tournament_players.append(player_name)

    tournament_players = sorted(set(tournament_players))

    selected_team_players = st.multiselect(
        "Selecione os jogadores para o time",
        options=tournament_players,
        key="selected_team_players_input",
    )

    if st.button("Adicionar seleção ao campo de times", key="add_team_players"):
        if not selected_team_players:
            st.error(
                "Selecione pelo menos um jogador para o time, otário! Tá querendo ganhar título **JEGUE REI :horse::crown:**?"
            )
        else:
            line = ", ".join(selected_team_players)
            if st.session_state.team_tournament_data_input:
                st.session_state.team_tournament_data_input += f"\n{line}"
            else:
                st.session_state.team_tournament_data_input = line

    team_tournament_data_input = st.text_area(
        "Insira apenas os nomes dos jogadores informados acima",
        height=200,
        key="team_tournament_data_input",
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
        if len(st.session_state.team_tournament_data_input) == 0:
            st.error(
                """Insira os dados dos times, otário! Tá querendo ganhar
                título **JEGUE REI :horse::crown:**?"""
            )
            return

        team_members_data = []
        for line in st.session_state.team_tournament_data_input.splitlines():
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

    if SHOW_TROLL_INTRO:
        if "click_counter" not in st.session_state:
            st.session_state.click_counter = 0

        if "showed_balloons" not in st.session_state:
            st.session_state.showed_balloons = 0

        placeholder = st.empty()

        if st.session_state.click_counter < 9:
            with placeholder.container():
                st.markdown("# 🚨 O SITE FOI DESATIVADO! 🚨")
                if st.button(
                    "Enviar mensagem para o Administrador", key="admin_message_button"
                ):
                    st.session_state.click_counter += 1
        else:
            if st.session_state.showed_balloons == 0:
                placeholder.empty()
                with placeholder.container():
                    st.balloons()
                    time.sleep(2)

                    st.image(TIRIRICAS_PATH, caption="BOA, JEGUE! :horse::crown:")
                    time.sleep(2)

                    st.session_state.showed_balloons = 1

                placeholder.empty()

            run_app()
    else:
        run_app()
