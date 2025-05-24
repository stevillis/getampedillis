from typing import List, Optional, Tuple

import streamlit as st

from backend.composers.style_image_composer import PlayerStyleImageComposer
from backend.utils import PLAYERS_FOLDER, STYLES_FOLDER
from backend.utils.utils import (
    assign_unique_styles_to_players,
    build_image_columns,
    get_players_df,
    hide_header_actions,
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
                    images_and_captions.append((img, f"Time {idx}"))
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
    for i in range(0, len(images_and_captions), images_per_row):
        cols = st.columns(images_per_row)
        for j in range(images_per_row):
            if i + j < len(images_and_captions):
                img, caption = images_and_captions[i + j]
                with cols[j]:
                    if img is not None:
                        st.image(img, caption=caption)
                    else:
                        st.warning(caption)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Criar imagens de estilos random", page_icon=":game_die:"
    )

    hide_header_actions()

    st.title("Criar imagens de estilos random")

    player_style_image_composer = PlayerStyleImageComposer(
        PLAYERS_FOLDER, STYLES_FOLDER
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        num_styles_per_player = st.number_input(
            "Quantidade de estilos",
            min_value=1,
            max_value=10,
            value=1,
            step=1,
            key="num_styles_per_player_random_style",
        )

    with col2:
        selected_categories = st.multiselect(
            "Categorias de estilos",
            options=CATEGORY_OPTIONS,
            default=["Todos"],
            key="category_multiselect_random_style",
        )

    players_df = get_players_df()
    player_options = players_df["Name"].tolist()
    selected_players = st.multiselect(
        "Selecione os jogadores",
        options=player_options,
        key="selected_players_random_style",
    )

    if "team_input_random_style" not in st.session_state:
        st.session_state["team_input_random_style"] = ""

    if st.button(
        "Adicionar seleção ao campo de times de estilos",
        key="add_team_players_random_style",
    ):
        if selected_players:
            line = ", ".join(selected_players)
            if st.session_state.team_input_random_style:
                st.session_state.team_input_random_style += f"\n{line}"
            else:
                st.session_state.team_input_random_style = line
        else:
            st.warning("Selecione pelo menos um jogador para adicionar ao time!")

    st.text_area(
        "Jogadores (um time por linha, nomes separados por vírgula)",
        placeholder="jogador1, jogador2, jogador3\njogador4, jogador5, jogador6",
        height=200,
        key="team_input_random_style",
    )

    if st.button("Sortear", key="draw_styles_btn"):
        team_input = st.session_state.get("team_input_random_style", "")
        if not team_input.strip():
            st.error("Insira pelo menos um time e jogador!")
        else:
            style_pool = get_style_pool(selected_categories)
            if not style_pool:
                st.error("Nenhum estilo disponível na(s) categoria(s) selecionada(s)!")
            else:
                teams = parse_teams_from_text(team_input)
                if not teams:
                    st.error("Insira pelo menos um jogador válido!")
                else:
                    player_style_pairs = assign_unique_styles_to_players(
                        teams, style_pool, num_styles_per_player, warn_func=st.warning
                    )
                    st.session_state["player_styles_data"] = player_style_pairs

                    render_team_images_grid(
                        teams, player_style_pairs, player_style_image_composer
                    )
