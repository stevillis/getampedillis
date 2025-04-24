"""
Image processing utilities for tournament.
"""

from pathlib import Path
from typing import List, Optional, Tuple

import boto3
from PIL import Image

from backend.utils import S3_BUCKET_NAME, S3_REGION


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


def find_image(folder_path: Path, image_name: str) -> Optional[str]:
    """Finds an image locally or downloads from S3 and caches it locally."""
    # Check for local file first
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
    img = Image.open(image_path)
    img = img.resize(size)
    return img


def get_or_create_image(
    folder_path: Path, image_name: str, size: Tuple[int, int]
) -> Image.Image:
    """Finds an image or creates a blank one if not found."""
    image_path = find_image(folder_path, image_name)
    if image_path is None:
        return create_blank_image(size=size)

    return resize_image(image_path=image_path, size=size)
