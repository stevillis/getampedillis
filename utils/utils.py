import os
from typing import List

import boto3
import pandas as pd
import streamlit as st

from utils import S3_BUCKET_NAME, S3_REGION

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
    s3 = boto3.client("s3", region_name=S3_REGION)
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix="players/")
    player_files = []
    for obj in response.get("Contents", []):
        key = obj["Key"]
        if key.endswith(".png") or key.endswith(".jpg"):
            name = key.split("/")[-1].replace(".png", "").replace(".jpg", "")
            if name and name != "no":
                player_files.append(name)

    players_df = pd.DataFrame({"Name": player_files})
    return players_df.sort_values("Name")


@st.cache_data
def get_styles_df():
    s3 = boto3.client("s3", region_name=S3_REGION)
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix="styles/")
    style_files = []
    for obj in response.get("Contents", []):
        key = obj["Key"]
        if key.endswith(".png") or key.endswith(".jpg"):
            name = key.split("/")[-1].replace(".png", "").replace(".jpg", "")
            if name and name != "no":
                style_files.append(name)

    styles_df = pd.DataFrame({"Name": style_files})
    return styles_df.sort_values("Name")
