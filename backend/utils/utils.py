"""Utility functions for list manipulation and other general-purpose operations."""

import datetime
import io
import os
import random
from collections import defaultdict
from typing import List

import pandas as pd
import streamlit as st
from PIL import Image

from backend.utils import PLAYERS_FOLDER, STYLES_FOLDER


def display_download_button(img: Image.Image, label: str, filename_prefix: str):
    """
    Renders a Streamlit download button for a PIL Image.
    """
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    now_str = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    file_name = f"{filename_prefix}_{now_str}.png"

    st.download_button(
        label=label,
        data=buf.getvalue(),
        file_name=file_name,
        mime="image/png",
        use_container_width=True,
    )


def parse_teams_from_text(text: str):
    """
    Parse teams from multiline text. Each line is a team, players separated by commas.
    Returns a list of teams, each team is a list of player names.
    """
    teams = []
    for line in text.strip().splitlines():
        team = [player.strip() for player in line.split(",") if player.strip()]
        if team:
            teams.append(team)

    return teams


def assign_unique_styles_to_players(
    teams, style_pool, num_styles_per_player, warn_func=None
):
    """
    Assign unique random styles to each player (no repeats for the same player).
    Returns a list of [player, style] pairs.
    If warn_func is provided, call it with a warning string if num_styles_per_player > len(style_pool).
    """
    player_style_pairs = []
    for team in teams:
        for player in team:
            if num_styles_per_player > len(style_pool):
                if warn_func:
                    warn_func(
                        f"Número de estilos por jogador ({num_styles_per_player}) excede o número de estilos disponíveis ({len(style_pool)}). Serão usados apenas estilos únicos."
                    )
                styles = random.sample(style_pool, len(style_pool))
                styles = styles[:num_styles_per_player]
            else:
                styles = random.sample(style_pool, num_styles_per_player)
            for style in styles:
                version = random.choice(["A", "B"])
                style_name = f"{style}{version}"
                player_style_pairs.append([player, style_name])

    return player_style_pairs


def build_image_columns(teams, player_style_pairs):
    """
    Build columns for the image composer:
    For single player: [player, style1, style2, ...]
    For multiple players: [[player1, style1, style2, ...], [player2, style1, style2, ...], ...]
    """
    columns = []
    if len(teams) == 1 and len(teams[0]) == 1:
        # Single player
        player = teams[0][0]
        player_styles = [pair[1] for pair in player_style_pairs if pair[0] == player]
        columns = [[player] + player_styles]
    else:
        # Multiple players
        player_styles_dict = defaultdict(list)
        for pair in player_style_pairs:
            player_styles_dict[pair[0]].append(pair[1])
        for team in teams:
            for player in team:
                columns.append([player] + player_styles_dict[player])

    return columns


def pad_list(
    lst: List[str], min_len: int = 5, max_len: int = 7, fill_with: str = "no"
) -> List[str]:
    """Pads the list with fill_with if it's shorter than max_len."""
    len_lst = len(lst)
    if min_len <= len_lst < max_len:
        lst.extend([fill_with] * (max_len - len_lst))

    return lst


def load_players_df():
    player_files = []
    for file in os.listdir(PLAYERS_FOLDER):
        if file.endswith(".png") or file.endswith(".jpg"):
            name = file.replace(".png", "").replace(".jpg", "")
            if name and name != "no":
                player_files.append(name)

    players_df = pd.DataFrame({"Name": player_files})
    return players_df.sort_values("Name")


@st.cache_data
def get_players_df():
    return load_players_df()


@st.cache_data
def get_styles_df():
    style_files = []
    for file in os.listdir(STYLES_FOLDER):
        if file.endswith(".png") or file.endswith(".jpg"):
            name = file.replace(".png", "").replace(".jpg", "")
            if name and name != "no":
                style_files.append(name)

    styles_df = pd.DataFrame({"Name": style_files})
    return styles_df.sort_values("Name")


def apply_custom_theme():
    """Aplica o tema customizado e estiliza a barra lateral."""
    st.markdown(
        """
        <style>
        /* Oculta os botões do cabeçalho */
        [data-testid="stHeaderActionElements"] {
            display: none;
        }

        /* Renomeia a Sidebar via CSS (Evita emojis e acentos nos arquivos) */
        [data-testid="stSidebarNav"] ul li:nth-child(1) span { font-size: 0; }
        [data-testid="stSidebarNav"] ul li:nth-child(1) span::after { content: "🏠 Início"; font-size: 1rem; }

        [data-testid="stSidebarNav"] ul li:nth-child(2) span { font-size: 0; }
        [data-testid="stSidebarNav"] ul li:nth-child(2) span::after { content: "🔧 Torneios e Acessórios"; font-size: 1rem; }

        [data-testid="stSidebarNav"] ul li:nth-child(3) span { font-size: 0; }
        [data-testid="stSidebarNav"] ul li:nth-child(3) span::after { content: "💪 Estilos de Luta"; font-size: 1rem; }

        [data-testid="stSidebarNav"] ul li:nth-child(4) span { font-size: 0; }
        [data-testid="stSidebarNav"] ul li:nth-child(4) span::after { content: "🍀 Roleta do Dedé"; font-size: 1rem; }

        [data-testid="stSidebarNav"] ul li:nth-child(5) span { font-size: 0; }
        [data-testid="stSidebarNav"] ul li:nth-child(5) span::after { content: "🐀 Draft Amped"; font-size: 1rem; }

        [data-testid="stSidebarNav"] ul li:nth-child(6) span { font-size: 0; }
        [data-testid="stSidebarNav"] ul li:nth-child(6) span::after { content: "🎲 Estilos Aleatórios"; font-size: 1rem; }

        [data-testid="stSidebarNav"] ul li:nth-child(7) span { font-size: 0; }
        [data-testid="stSidebarNav"] ul li:nth-child(7) span::after { content: "🔒 Login"; font-size: 1rem; }

        [data-testid="stSidebarNav"] ul li:nth-child(8) span { font-size: 0; }
        [data-testid="stSidebarNav"] ul li:nth-child(8) span::after { content: "👑 Painel Admin"; font-size: 1rem; }

        </style>
        """,
        unsafe_allow_html=True,
    )
