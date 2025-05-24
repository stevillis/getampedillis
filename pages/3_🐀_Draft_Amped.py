"""
Page for uploading two images, selecting rows to exclude, and downloading the processed images.
"""

from io import BytesIO

import numpy as np
import streamlit as st
from PIL import Image

from backend.utils.image_utils import (
    apply_transparent_gray,
    draw_row_numbers,
    get_num_rows,
    remove_rows,
)
from backend.utils.utils import hide_header_actions

ROW_HEIGHT = 94


def upload_image(label):
    uploaded = st.file_uploader(label, type=["png", "jpg", "jpeg"], key=label)
    if uploaded:
        img = Image.open(uploaded).convert("RGBA")
        return img
    return None


def download_image(img, label):
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        f"Baixar {label}",
        buf.getvalue(),
        file_name=f"{label}.png",
        mime="image/png",
    )


if __name__ == "__main__":
    st.set_page_config(page_title="Draft Amped", layout="wide")

    hide_header_actions()

    st.title("Draft Amped")

    st.markdown(
        """
        <style>
        [data-testid="stImageContainer"] {
            max-width: 275px !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        img1 = upload_image("Imagem do Time 1")
        if img1:
            num_rows1 = get_num_rows(img1)
            excluded_rows1 = []
            row_segments1 = []
            arr1 = np.array(img1)
            for i in range(num_rows1):
                y0 = i * ROW_HEIGHT
                y1 = y0 + ROW_HEIGHT
                row_img = Image.fromarray(arr1[y0:y1, :, :])
                cols = st.columns([1, 12])
                with cols[0]:
                    if i == 0:
                        exclude = st.checkbox(
                            str(i), value=False, key=f"exclude1_{i}", disabled=True
                        )
                    else:
                        exclude = st.checkbox(str(i), key=f"exclude1_{i}")
                with cols[1]:
                    display_img = row_img
                    if exclude:
                        display_img = apply_transparent_gray(row_img)
                    st.image(display_img, use_container_width=True)
                if exclude:
                    excluded_rows1.append(i)
                row_segments1.append((row_img, exclude))

    with col2:
        img2 = upload_image("Imagem do Time 2")
        if img2:
            num_rows2 = get_num_rows(img2)
            excluded_rows2 = []
            row_segments2 = []
            arr2 = np.array(img2)
            for i in range(num_rows2):
                y0 = i * ROW_HEIGHT
                y1 = y0 + ROW_HEIGHT
                row_img = Image.fromarray(arr2[y0:y1, :, :])
                cols = st.columns([1, 12])
                with cols[0]:
                    if i == 0:
                        exclude = st.checkbox(
                            str(i), value=False, key=f"exclude2_{i}", disabled=True
                        )
                    else:
                        exclude = st.checkbox(str(i), key=f"exclude2_{i}")
                with cols[1]:
                    display_img = row_img
                    if exclude:
                        display_img = apply_transparent_gray(row_img)
                    st.image(display_img, use_container_width=True)
                if exclude:
                    excluded_rows2.append(i)
                row_segments2.append((row_img, exclude))
        else:
            excluded_rows2 = []

    with col1:
        # Team 1 download button after Team 1 rows
        if img1:
            img1_final = remove_rows(img1, excluded_rows1)
            if img1_final:
                download_image(img1_final, "Draft 1")
            else:
                st.warning("Nenhuma linha selecionada para manter em Time 1.")

    with col2:
        # Team 2 download button after Team 2 rows
        if img2:
            img2_final = remove_rows(img2, excluded_rows2)
            if img2_final:
                download_image(img2_final, "Draft 2")
            else:
                st.warning("Nenhuma linha selecionada para manter em Time 2.")
