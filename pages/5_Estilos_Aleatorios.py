from typing import List, Optional, Tuple

import streamlit as st

from backend.composers.style_image_composer import PlayerStyleImageComposer
from backend.utils import PLAYERS_FOLDER, STYLES_FOLDER
from backend.utils.utils import (
    assign_unique_styles_to_players,
    build_image_columns,
    get_players_df,
    apply_custom_theme,
    parse_teams_from_text,
)

IMAGE_SIZE: Tuple[int, int] = (94, 94)

STYLE_CATEGORIES = {
    "BASIC": [
        "Fighter",
        "Soldier",
        "Spy",
        "Superman",
        "Armor",
        "Esper",
        "SpacePolice",
        "Sumo",
        "Ninja",
        "Mercenary",
        "Scout",
        "Spriggan",
    ],
    "FUSION": [
        "Monge",
        "Juiz",
        "Swordsman",
        "Beast",
        "Android",
        "Phalanx",
        "Berserker",
        "HalfBrute",
        "Borg",
        "Colosso",
        "MasterDoll",
        "Gemini",
    ],
    "RIVAL": [
        "Corrupt",
        "Veteran",
        "dsg",
        "Demon",
        "Fortress",
        "Sorcerer",
        "BHunter",
        "Wrestler",
        "DMatter",
        "Golem",
        "DarkElf",
        "KingBeast",
    ],
}

ALL_STYLE_NAMES = sum(STYLE_CATEGORIES.values(), [])

CATEGORY_OPTIONS = list(STYLE_CATEGORIES.keys()) + ["Todos"]


def prefill_team_input(selected_players):
    if selected_players:
        return ", ".join(selected_players)
    return ""


def get_style_pool(selected):
    if "Todos" in selected or not selected:
        return ALL_STYLE_NAMES
    pool = []

    for cat in selected:
        pool.extend(STYLE_CATEGORIES.get(cat, []))

    return pool


def render_team_images_grid(
    teams: List[List[str]],
    player_style_pairs: List[List[str]],
    player_style_image_composer: PlayerStyleImageComposer,
    images_per_row: int = 2,
) -> None:
    """
    Render team images in a grid layout using Streamlit columns.
    """
    images_and_captions: List[Tuple[Optional[object], str]] = []
    for idx, team in enumerate(teams, 1):
        team_pairs = [pair for pair in player_style_pairs if pair[0] in team]
        columns = build_image_columns([team], team_pairs)
        if columns:
            try:
                img = player_style_image_composer.generic.compose(columns, IMAGE_SIZE)
                if img is not None:
                    images_and_captions.append((img, f"🏆 Time {idx}"))
                else:
                    images_and_captions.append(
                        (None, f"Imagem do time {idx} não pôde ser criada.")
                    )
            except Exception as e:
                images_and_captions.append(
                    (None, f"Erro ao criar imagem do time {idx}: {e}")
                )
        else:
            images_and_captions.append(
                (None, f"Nenhuma coluna de imagem gerada para o time {idx}.")
            )

    # Display in a grid
    st.markdown("### 🖼️ Imagens Geradas")
    with st.container(border=True):
        for i in range(0, len(images_and_captions), images_per_row):
            cols = st.columns(images_per_row)
            for j in range(images_per_row):
                if i + j < len(images_and_captions):
                    img, caption = images_and_captions[i + j]
                    with cols[j]:
                        if img is not None:
                            st.image(img, caption=caption, use_container_width=True)
                        else:
                            st.warning(caption)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Criar Imagens de Estilos Random", page_icon="🎲", layout="wide"
    )

    apply_custom_theme()

    st.title("🎲 Times Aleatórios (Estilos)")
    st.info(
        "**Como usar o Gerador Aleatório:**\n"
        "1. Configure a quantidade de estilos por jogador e quais categorias você deseja incluir no sorteio.\n"
        "2. Forme os times selecionando os jogadores na caixa abaixo (ou digitando manualmente na área de texto).\n"
        "3. Clique em **Sortear** para que o sistema gere imagens com estilos únicos e aleatórios para todos.\n"
        "4. As imagens finais podem ser usadas no **Draft Amped** ou **Roleta do Dedé**!"
    )
    st.markdown("---")

    player_style_image_composer = PlayerStyleImageComposer(
        PLAYERS_FOLDER, STYLES_FOLDER
    )

    with st.container(border=True):
        st.subheader("⚙️ Configurações do Sorteio")
        col1, col2 = st.columns([1, 2])
        with col1:
            num_styles_per_player = st.number_input(
                "Quantidade de estilos por jogador",
                min_value=1,
                max_value=10,
                value=1,
                step=1,
                key="num_styles_per_player_random_style",
            )

        with col2:
            selected_categories = st.multiselect(
                "Categorias de estilos permitidas",
                options=CATEGORY_OPTIONS,
                default=["Todos"],
                key="category_multiselect_random_style",
                help="Selecione 'Todos' para misturar qualquer estilo, ou limite a categorias específicas como 'BASIC'.",
            )

    with st.container(border=True):
        st.subheader("👥 Formação de Times")
        players_df = get_players_df()
        player_options = players_df["Name"].tolist()

        col_select, col_btn = st.columns([3, 1])
        with col_select:
            selected_players = st.multiselect(
                "Busque e selecione os jogadores do Time",
                options=player_options,
                key="selected_players_random_style",
            )

        if "team_input_random_style" not in st.session_state:
            st.session_state["team_input_random_style"] = ""

        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(
                "➕ Adicionar ao Campo",
                key="add_team_players_random_style",
                use_container_width=True,
            ):
                if selected_players:
                    line = ", ".join(selected_players)
                    if st.session_state.team_input_random_style:
                        st.session_state.team_input_random_style += f"\n{line}"
                    else:
                        st.session_state.team_input_random_style = line
                else:
                    st.warning("Selecione pelo menos um jogador!")

        st.text_area(
            "Times (cada linha representa um Time, nomes separados por vírgula)",
            placeholder="Exemplo:\nJogadorA, JogadorB, JogadorC\nJogadorX, JogadorY, JogadorZ",
            height=150,
            key="team_input_random_style",
        )

        if st.button(
            "🎲 Sortear Estilos e Gerar Imagens",
            key="draw_styles_btn",
            use_container_width=True,
        ):
            team_input = st.session_state.get("team_input_random_style", "")
            if not team_input.strip():
                st.error("Por favor, insira pelo menos um time contendo jogadores.")
            else:
                style_pool = get_style_pool(selected_categories)
                if not style_pool:
                    st.error(
                        "Nenhum estilo disponível na(s) categoria(s) selecionada(s)!"
                    )
                else:
                    teams = parse_teams_from_text(team_input)
                    if not teams:
                        st.error("Insira pelo menos um jogador válido!")
                    else:
                        player_style_pairs = assign_unique_styles_to_players(
                            teams,
                            style_pool,
                            num_styles_per_player,
                            warn_func=st.warning,
                        )
                        st.session_state["player_styles_data"] = player_style_pairs

                        render_team_images_grid(
                            teams, player_style_pairs, player_style_image_composer
                        )
