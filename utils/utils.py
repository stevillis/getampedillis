import os
from typing import List

import pandas as pd
import streamlit as st

from utils import PLAYERS_FOLDER

"""Utility functions for list manipulation and other general-purpose operations."""


def pad_list(
    lst: List[str], min_len: int = 5, max_len: int = 7, fill_with: str = "no"
) -> List[str]:
    """Pads the list with fill_with if it's shorter than max_len."""
    len_lst = len(lst)
    if min_len <= len_lst < max_len:
        lst.extend([fill_with] * (max_len - len_lst))

    return lst


@st.cache_data
def get_players_df():
    player_files = [
        f.replace(".png", "").replace(".jpg", "")
        for f in os.listdir(PLAYERS_FOLDER)
        if (f.endswith(".png") or f.endswith(".jpg"))
    ]

    players_df = pd.DataFrame({"Name": player_files})
    players_df = players_df[players_df["Name"] != "no"]

    return players_df.sort_values("Name")
