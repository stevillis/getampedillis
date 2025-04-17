import streamlit as st
from PIL import Image

from utils import PLAYERS_FOLDER, STYLES_FOLDER
from utils.image_utils import create_column_image, get_or_create_image
from utils.utils import get_players_df, get_styles_df, pad_list


def create_composite_image(players_data, image_size):
    """Creates a composite image from a list of player data."""
    player_columns = []

    for player in players_data:
        name = player[0]
        styles = player[1:]

        player_image = get_or_create_image(
            folder_path=PLAYERS_FOLDER,
            image_name=name,
            size=image_size,
        )
        column_images = [player_image]

        styles = pad_list(styles.copy())
        for style_name in styles:
            style_image = get_or_create_image(
                folder_path=STYLES_FOLDER,
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


def create_team_image(team_members, players_data, image_size):
    """Creates an image for a team with their styles."""
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

        styles = member_data[1:]
        styles = pad_list(styles.copy())
        for style_name in styles:
            style_image = get_or_create_image(
                folder_path=STYLES_FOLDER,
                image_name=style_name,
                size=image_size,
            )
            column_images.append(style_image)

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


def run_app():
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

        st.write("### Lista de estilos")

        with st.container(height=250):
            styles_df = get_styles_df()
            num_cols = 5
            num_rows = (len(styles_df) + num_cols - 1) // num_cols

            for i in range(num_rows):
                cols = st.columns(num_cols)
                for j, col in enumerate(cols):
                    index = i * num_cols + j
                    if index < len(styles_df):
                        style_name = styles_df.iloc[index]["Name"]
                        player_image = get_or_create_image(
                            folder_path=STYLES_FOLDER,
                            image_name=style_name,
                            size=(32, 32),
                        )
                        with col:
                            st.image(player_image)
                            st.write(
                                f'<span style="font-size: 10px;">{style_name}</span>',
                                unsafe_allow_html=True,
                            )

    st.markdown("## Criar imagem de estilos")
    st.markdown("### Torneio")

    player_options = players_df["Name"].tolist()
    style_player_name_input = st.selectbox(
        "Selecione o jogador",
        player_options,
        key="style_player_name_input",
    )

    style_options = styles_df["Name"].tolist()
    selected_styles_input = st.multiselect(
        "Selecione os estilos",
        style_options,
        key="selected_styles_input",
    )

    if st.button("Adicionar seleção ao campo de texto", key="add_style_selection"):
        if not selected_styles_input:
            st.error(
                "Selecione pelo menos um estilo, otário! Tá querendo ganhar título **JEGUE REI :horse::crown:**?"
            )
        else:
            line = style_player_name_input
            if selected_styles_input:
                line += ", " + ", ".join(selected_styles_input)
            if st.session_state.style_tournament_data_input:
                st.session_state.style_tournament_data_input += f"\n{line}"
            else:
                st.session_state.style_tournament_data_input = line

    style_tournament_data_input = st.text_area(
        label="Insira os dados dos jogadores e seus estilos",
        height=200,
        placeholder="jogador1, estilo1, estilo2\njogador2, estilo1, estilo2",
        key="style_tournament_data_input",
    )

    input_style_image_size = st.selectbox(
        label="Selecione o tamanho da imagem",
        options=(32, 64, 72, 128),
        index=2,
        format_func=lambda x: f"{x}px",
        key="input_style_image_size",
    )

    if st.button(label="Criar imagem de estilos", key="create_tournament_image"):
        if len(st.session_state.style_tournament_data_input) == 0:
            st.error(
                """Insira os dados dos jogadores e seus estilos, otário! Tá querendo ganhar
                título **JEGUE REI :horse::crown:**?"""
            )
            return

        players_data = validate_tournament_data(
            st.session_state.style_tournament_data_input
        )
        if players_data is None:
            return

        if "player_styles_data" not in st.session_state:
            st.session_state.player_styles_data = players_data
        else:
            st.session_state.player_styles_data = players_data

        composite_image = create_composite_image(
            players_data=players_data,
            image_size=(input_style_image_size, input_style_image_size),
        )
        composite_image.save("generated_images/tournament_style_image.jpg")

        st.session_state.composite_style_image = composite_image

    if "composite_style_image" in st.session_state:
        st.image(
            image=Image.open("generated_images/tournament_style_image.jpg"),
            caption="Imagem dos jogadores e seus estilos",
        )

    # Add the team formation section
    st.markdown("---")
    st.markdown("### Formação de Times")

    styles_players = []
    if "style_tournament_data_input" in st.session_state:
        for line in st.session_state["style_tournament_data_input"].splitlines():
            if line.strip():
                player_name = line.split(",")[0].strip()
                if player_name:
                    styles_players.append(player_name)

    styles_players = sorted(set(styles_players))

    selected_team_style_players = st.multiselect(
        "Selecione os jogadores para o time",
        options=styles_players,
        key="selected_team_style_players",
    )

    if st.button("Adicionar seleção ao campo de times", key="add_team_style_players"):
        if not selected_team_style_players:
            st.error(
                "Selecione pelo menos um jogador para o time, otário! Tá querendo ganhar título **JEGUE REI :horse::crown:**?"
            )
        else:
            line = ", ".join(selected_team_style_players)
            if st.session_state.team_style_tournament_data_input:
                st.session_state.team_style_tournament_data_input += f"\n{line}"
            else:
                st.session_state.team_style_tournament_data_input = line

    team_style_tournament_data_input = st.text_area(
        "Insira apenas os nomes dos jogadores informados acima",
        height=200,
        key="team_style_tournament_data_input",
        placeholder="jogador1, jogador2, jogador3\njogador4, jogador5, jogador6",
    )

    input_team_style_image_size = st.selectbox(
        label="Selecione o tamanho da imagem dos times",
        options=(32, 64, 72, 128),
        index=2,
        format_func=lambda x: f"{x}px",
        key="input_team_style_image_size",
    )

    if st.button(label="Criar imagens dos Times", key="create_team_style_images"):
        if len(st.session_state.team_style_tournament_data_input) == 0:
            st.error(
                """Insira os dados dos times, otário! Tá querendo ganhar
                título **JEGUE REI :horse::crown:**?"""
            )
            return

        team_members_data = []
        for line in st.session_state.team_style_tournament_data_input.splitlines():
            if line.strip():  # Skip empty lines
                team_members = [item.strip() for item in line.split(",")]
                team_members_data.append(team_members)

        if "player_styles_data" not in st.session_state:
            st.error(
                """Crie a imagem de estilos primeiro, otário! Tá querendo
                ganhar título **JEGUE REI :horse::crown:**?"""
            )
            return

        players_data = st.session_state.player_styles_data

        for i, team_members in enumerate(team_members_data):
            team_image = create_team_image(
                team_members=team_members,
                players_data=players_data,
                image_size=(input_team_style_image_size, input_team_style_image_size),
            )
            if team_image is not None:
                team_image.save(f"generated_images/team_styles_{i+1}.jpg")
                st.image(
                    image=Image.open(f"generated_images/team_styles_{i+1}.jpg"),
                    caption=f"Time {i+1} com Estilos",
                )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Lojas Boto Produções",
        page_icon=":flipper:",
    )

    run_app()
