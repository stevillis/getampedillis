import numpy as np
import streamlit as st
from PIL import Image

from backend.utils.auth import require_login
from backend.utils.image_utils import roulette_team_rows


def get_uploaded_team_images():
    uploaded_team1 = st.sidebar.file_uploader(
        "Carregue a imagem do Time 1", type=["png", "jpg", "jpeg"], key="team1"
    )
    uploaded_team2 = st.sidebar.file_uploader(
        "Carregue a imagem do Time 2", type=["png", "jpg", "jpeg"], key="team2"
    )
    team_images = []
    if uploaded_team1:
        team_images.append(Image.open(uploaded_team1))
    if uploaded_team2:
        team_images.append(Image.open(uploaded_team2))

    return team_images


def show_team_previews(team_images):
    cols = st.columns(2)
    for i, img in enumerate(team_images):
        cols[i].image(img, caption=f"Time {i+1}", width=300)


def get_roulette_settings():
    st.markdown(
        """
        <style>
        .button-bottom-container {
            display: flex;
            flex-direction: column;
            justify-content: end;
            justify-items: end;
            height: 25.6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        num_rows = st.number_input(
            "Número de linhas na imagem (incluindo players)",
            min_value=2,
            max_value=20,
            value=8,
        )

    roulette_clicked = False
    with col2:
        st.markdown('<div class="button-bottom-container">', unsafe_allow_html=True)
        roulette_clicked = st.button("Sortear!")
        st.markdown("</div>", unsafe_allow_html=True)

    return num_rows, roulette_clicked


def show_roulette_results(roulette_row, avatar_imgs, roulette_results):
    st.subheader(f"Resultado do Roulette: Linha {roulette_row}")
    result_cols = st.columns(2)
    for i in range(2):
        stacked = np.vstack([np.array(avatar_imgs[i]), np.array(roulette_results[i])])
        result_cols[i].image(stacked, caption=f"Time {i+1}", width=300)


if __name__ == "__main__":
    require_login("🔒Login.py")

    st.set_page_config(
        page_title="Roleta de Times",
        page_icon=":flipper:",
    )

    st.title("Roleta de Times")

    team_images = get_uploaded_team_images()
    if len(team_images) == 2:
        show_team_previews(team_images)

        num_rows, roulette_clicked = get_roulette_settings()

        roulette_row = None
        avatar_imgs = []
        roulette_results = []
        if roulette_clicked:
            try:
                roulette_row, avatar_imgs, roulette_results = roulette_team_rows(
                    team_images,
                    num_rows=num_rows,
                    row_height=94,
                )
            except Exception as e:
                st.error(str(e))

        if roulette_results and roulette_row is not None:
            show_roulette_results(roulette_row, avatar_imgs, roulette_results)
    else:
        st.info("Carregue as imagens dos dois times para começar.")
