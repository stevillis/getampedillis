import streamlit as st
from PIL import Image

from backend.composers.style_image_composer import (
    PlayerStyleImageComposer,
    TeamStyleImageComposer,
)
from backend.utils import PLAYERS_FOLDER, STYLES_FOLDER
from backend.utils.auth import require_login
from backend.utils.utils import get_players_df, get_styles_df
from backend.validators.tournament_validator import TournamentDataValidator


class StyleTournamentApp:
    def __init__(self):
        self.player_style_image_composer = PlayerStyleImageComposer(
            PLAYERS_FOLDER, STYLES_FOLDER
        )
        self.team_style_image_composer = TeamStyleImageComposer(
            self.player_style_image_composer
        )
        self.validator = TournamentDataValidator()

    def run(self):
        self._render_sidebar()
        self._render_tournament_section()
        self._render_team_section()

    def _render_sidebar(self):
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
                            player_image = self.player_style_image_composer.compose(
                                [[player_name]], (32, 32)
                            )
                            with col:
                                st.image(player_image)
                                st.write(
                                    f'<span style="font-size: 10px;">{player_name}</span>',
                                    unsafe_allow_html=True,
                                )

            st.write("### Lista de estilos")

            styles_df = get_styles_df().copy()
            styles_df["Icon"] = styles_df["Name"].apply(
                lambda x: f"https://github.com/stevillis/tournament_image_creator/blob/master/data/styles/{x}.png?raw=true"
            )
            st.data_editor(
                styles_df,
                width=500,
                disabled=["Name", "Icon"],
                column_config={
                    "Icon": st.column_config.ImageColumn("Icon", help=""),
                },
            )

    def _render_tournament_section(self):
        st.markdown("## Criar imagens de estilos")

        st.markdown("### Torneio de Estilos")

        players_df = get_players_df()
        player_options = players_df["Name"].tolist()
        player_name_input = st.selectbox(
            "Selecione o jogador",
            player_options,
            key="player_style_name_input",
        )

        styles_df = get_styles_df()
        style_options = styles_df["Name"].tolist()
        selected_styles_input = st.multiselect(
            "Selecione os estilos",
            style_options,
            key="selected_styles_input",
        )

        if st.button("Adicionar seleção ao campo de texto de estilos"):
            if not selected_styles_input:
                st.error("Selecione pelo menos um estilo!")
            else:
                line = player_name_input
                if selected_styles_input:
                    line += "," + ",".join(selected_styles_input)
                if "style_tournament_data_input" not in st.session_state:
                    st.session_state["style_tournament_data_input"] = ""
                if st.session_state["style_tournament_data_input"]:
                    st.session_state["style_tournament_data_input"] += "\n" + line
                else:
                    st.session_state["style_tournament_data_input"] = line

        style_tournament_data_input = st.text_area(
            label="Insira os dados do torneio de estilos",
            height=200,
            placeholder="jogador1, estilo1, estilo2\njogador2, estilo1, estilo2",
            key="style_tournament_data_input",
        )

        if st.button(
            label="Criar imagem do Torneio de Estilos",
            key="create_tournament_style_image",
        ):
            if len(st.session_state.style_tournament_data_input) == 0:
                st.error("Insira os dados do torneio de estilos!")
                return

            players_data = self.validator.validate(
                st.session_state.style_tournament_data_input,
                error_message="Formato inválido, otário! Cada linha deve conter o nome do jogador e pelo menos um estilo.",
            )

            if players_data is None:
                return

            st.session_state.player_styles_data = players_data
            composite_image = self.player_style_image_composer.compose(
                players_data=players_data,
                image_size=(94, 94),
            )

            composite_image.save("generated_images/tournament_style_image.jpg")
            st.session_state.composite_style_image = composite_image

        if "composite_style_image" in st.session_state:
            st.image(
                image=Image.open("generated_images/tournament_style_image.jpg"),
                caption="Imagem dos jogadores e seus estilos",
            )

        st.markdown("---")

    def _render_team_section(self):
        st.markdown("### Formação de Times com Estilos")
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

        if st.button(
            "Adicionar seleção ao campo de times de estilos",
            key="add_team_style_players",
        ):
            if not selected_team_style_players:
                st.error("Selecione pelo menos um jogador para o time!")
            else:
                line = ", ".join(selected_team_style_players)
                if st.session_state.team_style_tournament_data_input:
                    st.session_state.team_style_tournament_data_input += f"\n{line}"
                else:
                    st.session_state.team_style_tournament_data_input = line

        st.text_area(
            "Insira apenas os nomes dos jogadores informados acima",
            height=200,
            key="team_style_tournament_data_input",
            placeholder="jogador1, jogador2, jogador3\njogador4, jogador5, jogador6",
        )

        if st.button(
            label="Criar imagens dos Times de Estilos", key="create_team_style_images"
        ):
            if len(st.session_state.team_style_tournament_data_input) == 0:
                st.error("Insira os dados dos times!")
                return

            team_members_data = []
            for line in st.session_state.team_style_tournament_data_input.splitlines():
                if line.strip():  # Skip empty lines
                    team_members = [item.strip() for item in line.split(",")]
                    team_members_data.append(team_members)

            if "player_styles_data" not in st.session_state:
                st.error("Crie a imagem de estilos primeiro!")
                return

            players_data = st.session_state.player_styles_data
            for i, team_members in enumerate(team_members_data):
                team_image = self.team_style_image_composer.compose_team(
                    team_members=team_members,
                    players_data=players_data,
                    image_size=(94, 94),
                )
                if team_image is not None:
                    team_image.save(f"generated_images/team_styles_{i+1}.jpg")
                    st.image(
                        image=Image.open(f"generated_images/team_styles_{i+1}.jpg"),
                        caption=f"Time {i+1} com Estilos",
                    )


if __name__ == "__main__":
    require_login("🔒Login.py")

    st.set_page_config(
        page_title="Criar imagens de estilos",
        page_icon=":flipper:",
    )

    StyleTournamentApp().run()
