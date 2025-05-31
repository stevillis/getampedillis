"""
Module for the creating images for GetAmped Tournament.
"""

import logging

import pandas as pd
import streamlit as st
from PIL import Image

from backend.composers.image_composer import PlayerImageComposer, TeamImageComposer
from backend.services.accessory_agent_service import AccessoryAgentService
from backend.utils import ACCESSORIES_FOLDER, ACCS_BY_YEAR_FILE, PLAYERS_FOLDER
from backend.utils.image_utils import get_or_create_image
from backend.utils.utils import get_players_df, hide_header_actions
from backend.validators.tournament_validator import TournamentDataValidator


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


def get_accessory_id(accessory):
    if accessory == "no":
        return accessory

    accs_df = get_accs_df()
    acc_series = accs_df[accs_df["Name"].str.lower() == accessory.lower()]["ID"]


class TournamentApp:
    def __init__(self):
        self.player_image_composer = PlayerImageComposer(
            PLAYERS_FOLDER, ACCESSORIES_FOLDER
        )
        self.team_image_composer = TeamImageComposer(self.player_image_composer)
        self.validator = TournamentDataValidator()

        # Initialize the agent service for ID generation
        if "agent_service" not in st.session_state:
            try:
                st.session_state.agent_service = AccessoryAgentService()
                (
                    st.session_state.accessory_mapping,
                    st.session_state.original_names,
                ) = st.session_state.agent_service.load_accessories(ACCS_BY_YEAR_FILE)
            except Exception as e:
                st.error(f"Erro ao inicializar o serviço de geração de IDs: {str(e)}")
                st.stop()

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

            st.data_editor(
                printable_accs_df,
                width=500,
                disabled=["Name", "ID", "Ano", "Icon"],
                column_config={
                    "Icon": st.column_config.ImageColumn("Icon", help=""),
                },
            )

    def _render_tournament_section(self):
        st.markdown("## Criar imagens de acessórios")
        st.markdown("### Torneio")

        with st.expander("🔍 Gerar IDs a partir de nomes de acessórios"):
            st.markdown(
                "💡 Os nomes dos acessórios não precisam ser exatos, o sistema tentará encontrar a melhor correspondência"
            )
            input_text = st.text_area(
                "Informe a lista de jogadores e acessórios (um por linha)",
                height=200,
                placeholder="Jogador1, Long Boots, Drill Hand, Jyuzumaru\nJogador2, Impulse Frame, Bizarre Kangaroo Suit, Steam Slasher",
                key="id_generator_input",
            )

            if st.button("🚀 Gerar IDs", key="generate_ids_button"):
                if not input_text.strip():
                    st.warning("Por favor, insira a lista de jogadores e acessórios.")
                else:
                    with st.spinner("Processando..."):
                        try:
                            result = st.session_state.agent_service.get_accessory_ids(
                                input_text,
                                st.session_state.accessory_mapping,
                                st.session_state.original_names,
                            )
                            st.session_state.tournament_data_input = result
                            st.success(
                                "IDs gerados e copiados para o campo de dados do torneio!"
                            )
                        except Exception as e:
                            st.error(f"Ocorreu um erro ao processar os dados: {str(e)}")
                            logging.exception("Error processing accessory IDs")

        with st.expander("👆 Selecionar jogador e acessórios manualmente"):
            players_df = get_players_df()
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
                    line = player_name_input
                    if selected_accs_input:
                        line += "," + ",".join(selected_accs_input)
                    if "tournament_data_input" not in st.session_state:
                        st.session_state["tournament_data_input"] = ""
                    if st.session_state["tournament_data_input"]:
                        st.session_state["tournament_data_input"] += "\n" + line
                    else:
                        st.session_state["tournament_data_input"] = line

        tournament_data_input = st.text_area(
            label="Insira os dados do torneio",
            height=200,
            placeholder="jogador1, id_acessorio1, id_acessorio2\njogador2, id_acessorio1, id_acessorio2",
            key="tournament_data_input",
        )

        if st.button(label="Criar imagem do Torneio", key="create_tournament_image"):
            if len(st.session_state.tournament_data_input) == 0:
                st.error(
                    """Insira os dados do torneio, otário! Tá querendo ganhar\ntítulo **JEGUE REI :horse::crown:**?"""
                )
                return

            players_data = self.validator.validate(
                st.session_state.tournament_data_input,
                error_message="Formato inválido, otário! Cada linha deve conter o nome do jogador e pelo menos um acessório.",
            )
            if players_data is None:
                return

            st.session_state.players_data = players_data
            composite_image = self.player_image_composer.compose(
                players_data=players_data,
                image_size=(94, 94),
            )
            composite_image.save("generated_images/tournament_image.jpg")
            st.session_state.composite_image = composite_image

        if "composite_image" in st.session_state:
            st.image(
                image=Image.open("generated_images/tournament_image.jpg"),
                caption="Imagem do Torneio",
            )

        st.markdown("---")

    def _render_team_section(self):
        st.markdown("### Formação de Times")
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

        if st.button(label="Criar imagens dos Times", key="create_team_images"):
            if len(st.session_state.team_tournament_data_input) == 0:
                st.error(
                    """Insira os dados dos times, otário! Tá querendo ganhar\ntítulo **JEGUE REI :horse::crown:**?"""
                )
                return

            team_members_data = []
            for line in st.session_state.team_tournament_data_input.splitlines():
                if line.strip():  # Skip empty lines
                    team_members = [item.strip() for item in line.split(",")]
                    team_members_data.append(team_members)

            if "players_data" not in st.session_state:
                st.error(
                    """Crie a imagem do torneio primeiro, otário! Tá querendo\nganhar título **JEGUE REI :horse::crown:**?"""
                )
                return

            players_data = st.session_state.players_data
            for i, team_members in enumerate(team_members_data):
                team_image = self.team_image_composer.compose_team(
                    team_members=team_members,
                    players_data=players_data,
                    image_size=(94, 94),
                )

                if team_image is not None:
                    team_image.save(f"generated_images/team_{i+1}.jpg")
                    st.image(
                        image=Image.open(f"generated_images/team_{i+1}.jpg"),
                        caption=f"Time {i+1}",
                    )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Criar imagens de acessórios",
        page_icon=":flipper:",
    )

    hide_header_actions()
    TournamentApp().run()
