"""Utility functions for list manipulation and other general-purpose operations."""

import os
from typing import List

import pandas as pd
import streamlit as st

from backend.utils import PLAYERS_FOLDER, STYLES_FOLDER


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
