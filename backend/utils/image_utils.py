"""
Image processing utilities for tournament.
"""

import random
from pathlib import Path
from typing import List, Optional, Tuple

# import boto3
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw

# from backend.utils import S3_BUCKET_NAME, S3_REGION
from backend.utils import PLAYERS_FOLDER


def create_blank_image(size: Tuple[int, int]) -> Image.Image:
    """Creates a blank white image."""
    return Image.new("RGB", size, (255, 255, 255))


def create_column_image(images: List[Image.Image]) -> Image.Image:
    """Creates a column image from a list of images."""
    column_width = images[0].width
    column_height = sum(img.height for img in images)
    column_image = Image.new("RGB", (column_width, column_height))
    y_offset = 0
    for img in images:
        column_image.paste(img, (0, y_offset))
        y_offset += img.height

    return column_image


def roulette_team_rows(
    images: list,
    num_rows: int,
    row_height: int = 94,
    avatar_row: int = 1,
    num_accessory_rows: int = 1,
    rng=None,
):
    """
    For each image, crops the avatar row and N randomly selected accessory rows (excluding avatar_row).
    Returns (sampled_rows, avatar_imgs, accessory_imgs), where:
        - sampled_rows: list of int (row indices sampled for accessories)
        - avatar_imgs: list of PIL.Image (one per image)
        - accessory_imgs: list of lists of PIL.Image (one list per image, each containing N accessory rows)
    """
    if rng is None:
        rng = random

    height = images[0].height
    max_possible_rows = height // row_height
    valid_rows = [
        i for i in range(num_rows) if i != (avatar_row - 1) and i < max_possible_rows
    ]

    if not valid_rows or num_accessory_rows > len(valid_rows):
        raise ValueError(
            "Quantidade de linhas de acessórios inválida. Verifique o número de linhas ou o tamanho da imagem."
        )

    sampled_rows = rng.sample(valid_rows, num_accessory_rows)
    sampled_rows.sort()  # For visual consistency
    avatar_imgs = []
    accessory_imgs = []
    for img in images:
        np_img = np.array(img)
        avatar_crop = np_img[
            (avatar_row - 1) * row_height : avatar_row * row_height, :, :
        ]
        avatar_imgs.append(Image.fromarray(avatar_crop))
        acc_list = []
        for row in sampled_rows:
            acc_crop = np_img[row * row_height : (row + 1) * row_height, :, :]
            acc_list.append(Image.fromarray(acc_crop))
        accessory_imgs.append(acc_list)

    return sampled_rows, avatar_imgs, accessory_imgs


def find_image(folder_path: Path, image_name: str) -> Optional[str]:
    """Finds an image locally or downloads from S3 and caches it locally."""
    # Always use lowercase for image_name to ensure case-insensitive lookup
    image_name = image_name.lower()
    for ext in [".png", ".jpg"]:
        local_path = folder_path / f"{image_name}{ext}"
        if local_path.exists():
            return str(local_path)

    # If not found locally, try S3
    # s3 = boto3.client("s3", region_name=S3_REGION)
    # folder = folder_path.name  # "players", "accs", or "styles"
    # for ext in [".png", ".jpg"]:
    #     key = f"{folder}/{image_name}{ext}"
    #     try:
    #         response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
    #         # Save to local file for future use
    #         local_path = folder_path / f"{image_name}{ext}"
    #         with open(local_path, "wb") as f:
    #             f.write(response["Body"].read())
    #         return str(local_path)
    #     except s3.exceptions.NoSuchKey:
    #         continue
    #     except Exception:
    #         continue

    return None


def resize_image(image_path: Path, size: Tuple[int, int]) -> Image.Image:
    """Resizes an image to the specified size."""
    st.write(
        f"[resize_image] Resizing image: {image_path} (type: {type(image_path)}) to size {size}"
    )
    try:
        img = Image.open(image_path)
        st.write(f"[resize_image] Original mode: {img.mode}, size: {img.size}")
        img = img.convert("RGB")  # Ensure compatibility
        img = img.resize(size)
        st.write(f"[resize_image] Resized image size: {img.size}")
        return img
    except Exception as e:
        st.error(f"[resize_image] Error resizing image {image_path}: {e}")
        raise


def get_or_create_image(
    folder_path: Path, image_name: str, size: Tuple[int, int]
) -> Image.Image:
    """Finds an image or creates a blank one if not found."""
    # Always use lowercase for image_name to ensure case-insensitive lookup
    image_name = image_name.lower()
    image_path = find_image(folder_path, image_name)
    st.write(
        f"[get_or_create_image] folder={folder_path}, image_name={image_name}, found={image_path}"
    )
    if image_path is None:
        st.write("[get_or_create_image] Returning blank image")
        return create_blank_image(size=size)
    return resize_image(image_path=image_path, size=size)


def apply_transparent_gray(img, alpha=200):
    """
    Apply a semi-transparent gray overlay to a PIL image.
    """
    overlay = Image.new("RGBA", img.size, (60, 60, 60, alpha))
    img_rgba = img.convert("RGBA")
    blended = Image.alpha_composite(img_rgba, overlay)

    return blended.convert("RGB")


def get_num_rows(image, row_height=94):
    """
    Calculate the number of rows in an image given a row height.
    """
    return image.height // row_height


def draw_row_numbers(image, excluded_rows, row_height=94):
    """
    Draw row numbers and gray out excluded rows on the image.
    """
    img = image.copy()
    draw = ImageDraw.Draw(img)
    num_rows = get_num_rows(img, row_height)
    for i in range(num_rows):
        y0 = i * row_height
        y1 = y0 + row_height
        color = (200, 200, 200, 180) if i in excluded_rows else (255, 255, 255, 180)

        # Draw background for number
        draw.rectangle([0, y0, 40, y1], fill=color)

        # Draw row number
        draw.text((8, y0 + row_height // 3), str(i), fill="black")

        # Gray out excluded row
        if i in excluded_rows:
            draw.rectangle([40, y0, img.width, y1], fill=(180, 180, 180, 120))

    return img


def remove_rows(image, excluded_rows, row_height=94):
    """
    Remove specified rows from the image and return the new image.
    """
    num_rows = get_num_rows(image, row_height)
    rows = [i for i in range(num_rows) if i not in excluded_rows]
    if not rows:
        return None

    arr = np.array(image)
    new_img_rows = [arr[i * row_height : (i + 1) * row_height, :, :] for i in rows]
    new_arr = np.vstack(new_img_rows)

    return Image.fromarray(new_arr)


def handle_player_image_upload(
    player_name: str,
    uploaded_file: object,
) -> Tuple[str, str]:
    """
    Handles the upload of player image, checking for duplicated images.
    Returns a tuple: (status, message)
    """
    if player_name.strip() == "":
        return "error", (
            """Coloque o nome do jogador, otário! Tá querendo ganhar\n"""
            "título **JEGUE REI :horse::crown:**?\n"
            ""
        )

    for ext in ["png", "jpg", "jpeg"]:
        if (PLAYERS_FOLDER / f"{player_name}.{ext}").exists():
            return "error", "Já existe uma imagem para este jogador!"

    extension = uploaded_file.name.split(".")[-1].lower()
    save_path = PLAYERS_FOLDER / f"{player_name}.{extension}"

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    return "success", "Imagem adicionada com sucesso!"
