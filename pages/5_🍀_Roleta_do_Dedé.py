import datetime
import io

import numpy as np
import streamlit as st
from PIL import Image

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


def show_team_rows_with_index(team_images):
    ROW_HEIGHT = 94

    cols = st.columns(2)
    for team_idx, img in enumerate(team_images):
        if img is None:
            continue

        arr = np.array(img)
        num_rows = arr.shape[0] // ROW_HEIGHT

        with cols[team_idx]:
            st.markdown(f"<b>Time {team_idx+1}</b>", unsafe_allow_html=True)
            for i in range(num_rows):
                y0 = i * ROW_HEIGHT
                y1 = y0 + ROW_HEIGHT
                row_img = Image.fromarray(arr[y0:y1, :, :])

                row_cols = st.columns([1, 12])
                with row_cols[0]:
                    st.markdown(
                        f'<div style="font-size:16px;text-align:center;">{i}</div>',
                        unsafe_allow_html=True,
                    )

                with row_cols[1]:
                    st.image(row_img, use_container_width=True)


def get_roulette_settings():
    col1, col2 = st.columns(2)
    with col1:
        num_rows = st.number_input(
            "Linhas na imagem (inclui players)",
            min_value=2,
            max_value=20,
            value=8,
        )

    avatar_row = 1
    eligible_rows = [i for i in range(num_rows) if i != (avatar_row - 1)]
    selectable_rows = st.multiselect(
        "Linhas elegíveis para sorteio",
        eligible_rows,
        default=eligible_rows,
        key="selectable_rows_multiselect",
    )

    with col2:
        max_accessory = max(1, len(selectable_rows))
        num_accessory_rows = st.number_input(
            "Quantidade de linhas a sortear",
            min_value=1,
            max_value=max_accessory,
            value=1,
        )

    roulette_clicked = st.button("Sortear!", key="roulette_button")

    return num_rows, num_accessory_rows, selectable_rows, roulette_clicked


def show_roulette_results(sampled_rows, avatar_imgs, accessory_imgs):
    st.subheader(
        f"Linhas de acessórios sorteadas: {', '.join(str(r) for r in sampled_rows)}"
    )
    result_cols = st.columns(2)

    now_str = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    for i in range(2):
        # Stack avatar row + all accessory rows
        stacked = np.vstack(
            [np.array(avatar_imgs[i]), *[np.array(acc) for acc in accessory_imgs[i]]]
        )
        result_cols[i].image(stacked, caption=f"Time {i+1}", width=300)

        img_pil = Image.fromarray(stacked)
        buf = io.BytesIO()
        img_pil.save(buf, format="PNG")

        file_name = f"time_{i+1}_{now_str}.png"
        result_cols[i].download_button(
            label=f"Baixar imagem do Time {i+1}",
            data=buf.getvalue(),
            file_name=file_name,
            mime="image/png",
        )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Roleta do Dedé",
        page_icon=":flipper:",
    )

    st.title("Roleta do Dedé")

    team_images = get_uploaded_team_images()
    if len(team_images) == 2:
        show_team_rows_with_index(team_images)

        (
            num_rows,
            num_accessory_rows,
            selectable_rows,
            roulette_clicked,
        ) = get_roulette_settings()

        if "roulette_results" not in st.session_state:
            st.session_state["roulette_results"] = None

        if roulette_clicked:
            try:
                sampled_rows, avatar_imgs, accessory_imgs = roulette_team_rows(
                    team_images,
                    num_rows=num_rows,
                    row_height=94,
                    num_accessory_rows=num_accessory_rows,
                    selectable_rows=selectable_rows,
                )

                st.session_state["roulette_results"] = {
                    "sampled_rows": sampled_rows,
                    "avatar_imgs": avatar_imgs,
                    "accessory_imgs": accessory_imgs,
                }
            except Exception as e:
                st.error(str(e))

        results = st.session_state.get("roulette_results")
        if results and results["accessory_imgs"]:
            show_roulette_results(
                results["sampled_rows"],
                results["avatar_imgs"],
                results["accessory_imgs"],
            )
    else:
        st.info("Carregue as imagens dos dois times para começar.")
