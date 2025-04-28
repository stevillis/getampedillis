"""Utility functions for list manipulation and other general-purpose operations."""

import os
import random
from collections import defaultdict
from typing import List

import pandas as pd
import streamlit as st

from backend.utils import PLAYERS_FOLDER, STYLES_FOLDER


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
