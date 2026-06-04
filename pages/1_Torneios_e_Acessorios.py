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
from backend.utils.utils import get_players_df, apply_custom_theme
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
        lambda x: (
            f"https://github.com/stevillis/tournament_image_creator/blob/master/data/accs/{x}.png?raw=true"
        )
    )

    return accs_df


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

        tab_ai, tab_manual = st.tabs(
            [
                "🔍 Gerar IDs a partir de nomes",
                "👆 Selecionar manualmente",
            ]
        )

        with tab_ai:
            st.caption(
                "Use IA para encontrar os IDs dos acessórios a partir dos nomes. "
                "Os nomes não precisam ser exatos, o sistema tentará encontrar a melhor correspondência."
            )
            input_text = st.text_area(
                "Informe a lista de jogadores e acessórios (um por linha)",
                height=200,
                placeholder="Jogador1, Long Boots, Drill Hand, Jyuzumaru\nJogador2, Impulse Frame, Bizarre Kangaroo Suit, Steam Slasher",
                key="id_generator_input",
            )

            if st.button(
                "🚀 Gerar IDs", key="generate_ids_button", use_container_width=True
            ):
                if not input_text.strip():
                    st.warning("Por favor, insira a lista de jogadores e acessórios.")
                else:
                    with st.spinner("Processando..."):
                        try:
                            result = st.session_state.agent_service.get_accessory_ids(
                                input_text
                            )
                            st.session_state.tournament_data_input = result
                            st.success(
                                "IDs gerados e copiados para o campo de dados do torneio!"
                            )
                        except Exception as e:
                            st.error(f"Ocorreu um erro ao processar os dados: {str(e)}")
                            logging.exception("Error processing accessory IDs")

        with tab_manual:
            st.info(
                "Selecione o jogador e os IDs dos acessórios manualmente usando os campos abaixo."
            )
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

            if st.button(
                "➕ Adicionar seleção ao campo de texto", use_container_width=True
            ):
                if not selected_accs_input:
                    st.error("Selecione pelo menos um acessório, para continuar.")
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

        st.markdown("#### Dados do Torneio")
        _ = st.text_area(
            label="Insira ou verifique os dados gerados abaixo",
            height=200,
            placeholder="Exemplo:\njogador1, id_acessorio1, id_acessorio2\njogador2, id_acessorio1, id_acessorio2",
            key="tournament_data_input",
        )

        if st.button(
            label="🖼️ Criar Imagem do Torneio",
            key="create_tournament_image",
            use_container_width=True,
        ):
            if len(st.session_state.tournament_data_input) == 0:
                st.error(
                    "Por favor, insira os dados do torneio antes de criar a imagem."
                )
                return

            players_data = self.validator.validate(
                st.session_state.tournament_data_input,
                error_message="Formato inválido. Cada linha deve conter o nome do jogador e pelo menos um acessório.",
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
                caption="Imagem Oficial do Torneio",
                use_container_width=True,
            )

        st.markdown("---")

    def _render_team_section(self):
        st.markdown("### 👥 Formação de Times")
        with st.container(border=True):
            tournament_players = []
            if "tournament_data_input" in st.session_state:
                for line in st.session_state["tournament_data_input"].splitlines():
                    if line.strip():
                        player_name = line.split(",")[0].strip()
                        if player_name:
                            tournament_players.append(player_name)

            tournament_players = sorted(set(tournament_players))

            col_select, col_btn = st.columns([3, 1])
            with col_select:
                selected_team_players = st.multiselect(
                    "Selecione os jogadores para agrupar em um Time",
                    options=tournament_players,
                    key="selected_team_players_input",
                )

            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(
                    "➕ Adicionar Time",
                    key="add_team_players",
                    use_container_width=True,
                ):
                    if not selected_team_players:
                        st.error("Selecione pelo menos um jogador para o time.")
                    else:
                        line = ", ".join(selected_team_players)
                        if "team_tournament_data_input" not in st.session_state:
                            st.session_state.team_tournament_data_input = ""
                        if st.session_state.team_tournament_data_input:
                            st.session_state.team_tournament_data_input += f"\n{line}"
                        else:
                            st.session_state.team_tournament_data_input = line

            _ = st.text_area(
                "Times (cada linha representa um Time, contendo os nomes dos jogadores)",
                height=150,
                key="team_tournament_data_input",
                placeholder="Exemplo:\njogador1, jogador2, jogador3\njogador4, jogador5, jogador6",
            )

            if st.button(
                label="🖼️ Gerar Imagens dos Times",
                key="create_team_images",
                use_container_width=True,
            ):
                if len(st.session_state.team_tournament_data_input) == 0:
                    st.error("Por favor, insira os dados dos times primeiro.")
                    return

                team_members_data = []
                for line in st.session_state.team_tournament_data_input.splitlines():
                    if line.strip():  # Skip empty lines
                        team_members = [item.strip() for item in line.split(",")]
                        team_members_data.append(team_members)

                if "players_data" not in st.session_state:
                    st.error(
                        "Crie a Imagem do Torneio (etapa anterior) primeiro para poder formar times!"
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
                        team_image.save(f"generated_images/team_{i + 1}.jpg")
                        st.image(
                            image=Image.open(f"generated_images/team_{i + 1}.jpg"),
                            caption=f"🏆 Time {i + 1}",
                            use_container_width=True,
                        )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Torneios e Acessórios", page_icon="🔧", layout="wide"
    )

    apply_custom_theme()

    st.title("🔧 Torneios e Acessórios")
    st.info(
        "**Como usar o Gerador de Acessórios:**\n"
        "1. Na aba **Gerar IDs a partir de nomes**, cole a lista de jogadores e seus equipamentos e deixe a IA encontrar os IDs corretos.\n"
        "2. Clique em **Criar Imagem do Torneio** para processar a base de dados.\n"
        "3. Com a imagem do torneio gerada, vá para a seção **Formação de Times**, selecione os jogadores que formam cada equipe e clique para Gerar as Imagens dos Times.\n"
        "4. Você poderá usar essas imagens de Time na **Roleta do Dedé** ou no **Draft Amped**."
    )
    st.markdown("---")

    TournamentApp().run()
