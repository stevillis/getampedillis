import datetime
import io

import numpy as np
import streamlit as st
from PIL import Image

from backend.utils.image_utils import roulette_team_rows
from backend.utils.utils import hide_header_actions


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


def get_team_row_settings(team_num, num_rows):
    st.markdown(f"**Configurações do Time {team_num}**")
    avatar_row = 1
    all_rows = [i for i in range(num_rows) if i != (avatar_row - 1)]

    fixed_rows = st.multiselect(
        f"Linhas fixas (sempre presentes) - Time {team_num}",
        all_rows,
        default=[],
        key=f"fixed_rows_multiselect_team{team_num}",
    )

    eligible_rows = [i for i in all_rows if i not in fixed_rows]

    selectable_rows = st.multiselect(
        f"Linhas elegíveis para sorteio - Time {team_num}",
        eligible_rows,
        default=eligible_rows,
        key=f"selectable_rows_multiselect_team{team_num}",
    )

    max_selectable = len(selectable_rows)
    num_rows_to_draw = st.number_input(
        f"Quantidade de linhas a sortear - Time {team_num}",
        min_value=0,
        max_value=max_selectable if max_selectable > 0 else 0,
        value=1 if max_selectable > 0 else 0,
        key=f"num_rows_to_draw_team{team_num}",
        help=("Defina como 0 para usar " "apenas as linhas fixas"),
    )

    return fixed_rows, selectable_rows, num_rows_to_draw


def get_roulette_settings():
    num_rows = st.number_input(
        "Linhas na imagem (inclui players)",
        min_value=2,
        max_value=20,
        value=8,
    )

    col1, col2 = st.columns(2)

    # Team 1 settings
    with col1:
        fixed_rows_team1, selectable_rows_team1, num_rows_team1 = get_team_row_settings(
            1, num_rows
        )

    # Team 2 settings
    with col2:
        fixed_rows_team2, selectable_rows_team2, num_rows_team2 = get_team_row_settings(
            2, num_rows
        )

    col1, col2 = st.columns(2)
    with col1:
        roulette_clicked_team1 = st.button(
            "Sortear Time 1", key="roulette_button_team1"
        )
    with col2:
        roulette_clicked_team2 = st.button(
            "Sortear Time 2", key="roulette_button_team2"
        )

    return (
        num_rows,
        {"team1": num_rows_team1, "team2": num_rows_team2},
        {"team1": selectable_rows_team1, "team2": selectable_rows_team2},
        {"team1": fixed_rows_team1, "team2": fixed_rows_team2},
        roulette_clicked_team1,
        roulette_clicked_team2,
    )


def show_team_result(
    team_idx,
    sampled_rows,
    avatar_img,
    accessory_imgs_team,
    fixed_rows=None,
    team_image=None,
):
    st.subheader(f"Resultado do Time {team_idx + 1}")
    st.write(
        f"Linhas de acessórios sorteadas: {', '.join(str(r) for r in sampled_rows[0])}"
    )

    if fixed_rows:
        st.markdown(
            f"<b>Linhas fixas:</b> {', '.join(str(r) for r in fixed_rows)}",
            unsafe_allow_html=True,
        )

    rows_to_stack = [np.array(avatar_img)]

    # Add fixed rows from the original team image
    if fixed_rows and team_image is not None:
        arr = np.array(team_image)
        row_height = avatar_img.height  # Should be 94
        for row in sorted(fixed_rows):
            y0 = row * row_height
            y1 = y0 + row_height
            fixed_row_img = arr[y0:y1, :, :]
            rows_to_stack.append(fixed_row_img)

    # Add accessory rows
    rows_to_stack.extend(
        [np.array(acc) for acc in accessory_imgs_team if acc is not None]
    )

    if not rows_to_stack:
        st.warning("Nenhuma imagem para exibir.")
        return

    stacked = np.vstack(rows_to_stack)
    st.image(stacked, caption=f"Time {team_idx + 1}", width=300)

    # Download button
    img_pil = Image.fromarray(stacked)
    buf = io.BytesIO()
    img_pil.save(buf, format="PNG")

    now_str = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    file_name = f"time_{team_idx + 1}_{now_str}.png"

    st.download_button(
        label=f"Baixar imagem do Time {team_idx + 1}",
        data=buf.getvalue(),
        file_name=file_name,
        mime="image/png",
    )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Roleta do Dedé",
        page_icon=":flipper:",
    )

    hide_header_actions()

    st.title("Roleta do Dedé")

    team_images = get_uploaded_team_images()
    if len(team_images) == 2:
        show_team_rows_with_index(team_images)

        (
            num_rows,
            num_accessory_rows,
            selectable_rows,
            fixed_rows,
            roulette_clicked_team1,
            roulette_clicked_team2,
        ) = get_roulette_settings()

        if "roulette_results" not in st.session_state:
            st.session_state["roulette_results"] = {}

        if roulette_clicked_team1 or roulette_clicked_team2:
            team_num = "team1" if roulette_clicked_team1 else "team2"
            team_idx = 0 if roulette_clicked_team1 else 1
            try:
                # Process only the clicked team's image
                single_team_images = [team_images[team_idx]]
                sampled_rows, avatar_imgs, accessory_imgs = roulette_team_rows(
                    single_team_images,
                    num_rows=num_rows,
                    row_height=94,
                    num_accessory_rows=num_accessory_rows[team_num],
                    selectable_rows=selectable_rows[team_num],
                )

                # Store results for each team separately
                if "team_results" not in st.session_state["roulette_results"]:
                    st.session_state["roulette_results"]["team_results"] = [None, None]

                st.session_state["roulette_results"]["team_results"][team_idx] = {
                    "sampled_rows": sampled_rows,
                    "avatar_imgs": avatar_imgs,
                    "accessory_imgs": accessory_imgs,
                    "fixed_rows": fixed_rows[team_num],
                }
            except Exception as e:
                st.error(f"Erro ao sortear Time {team_idx + 1}: {str(e)}")

        results = st.session_state.get("roulette_results", {})
        team_results = results.get("team_results", [None, None])

        # Show results for each team if they exist
        result_cols = st.columns(2)
        for i in range(2):
            with result_cols[i]:
                if team_results[i] and team_results[i]["accessory_imgs"]:
                    show_team_result(
                        team_idx=i,
                        sampled_rows=[team_results[i]["sampled_rows"]],
                        avatar_img=(
                            team_results[i]["avatar_imgs"][0]
                            if team_results[i]["avatar_imgs"]
                            else None
                        ),
                        accessory_imgs_team=(
                            team_results[i]["accessory_imgs"][0]
                            if team_results[i]["accessory_imgs"]
                            else []
                        ),
                        fixed_rows=team_results[i].get("fixed_rows", []),
                        team_image=team_images[i] if i < len(team_images) else None,
                    )
    else:
        st.info("Carregue as imagens dos dois times para começar.")
