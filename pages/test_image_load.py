import os
from PIL import Image
import streamlit as st

from backend.utils import PLAYERS_FOLDER, STYLES_FOLDER
from backend.utils.image_utils import get_or_create_image

import PIL

st.title("Teste de carregamento de imagens")
st.write(f"Pillow version: {PIL.__version__}")

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
        full_path = os.path.join(STYLES_FOLDER, filename)
        st.write(f"{filename} - {os.path.getsize(full_path)} bytes")
        try:

            img = Image.open(full_path)
            st.image(img, caption=filename)
        except Exception as e:
            st.write(f"ERROR loading {filename}: {e}")
else:
    st.write(f"Folder '{STYLES_FOLDER}' does not exist.")
