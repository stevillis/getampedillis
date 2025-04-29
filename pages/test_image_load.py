import os

import streamlit as st

from backend.utils import PLAYERS_FOLDER, STYLES_FOLDER
from backend.utils.image_utils import get_or_create_image

st.title("Teste de carregamento de imagens")

st.image(get_or_create_image(PLAYERS_FOLDER, "aalegria", (32, 32)))
st.image(get_or_create_image(STYLES_FOLDER, "dsgA", (32, 32)))
st.image(get_or_create_image(STYLES_FOLDER, "dsgB", (32, 32)))
st.image(get_or_create_image(STYLES_FOLDER, "FighterB", (32, 32)))
st.image(get_or_create_image(STYLES_FOLDER, "FighterA", (32, 32)))


if os.path.exists(STYLES_FOLDER):
    files = [
        f
        for f in os.listdir(STYLES_FOLDER)
        if os.path.isfile(os.path.join(STYLES_FOLDER, f))
    ]
    for filename in sorted(files):
        st.write(filename)
else:
    st.write(f"Folder '{STYLES_FOLDER}' does not exist.")
