import os

from PIL import Image


def create_blank_image(size):
    """Creates a blank white image."""
    return Image.new("RGB", size, (255, 255, 255))


def create_column_image(images):
    """Creates a column image from a list of images."""
    column_width = images[0].width
    column_height = sum(img.height for img in images)
    column_image = Image.new("RGB", (column_width, column_height))
    y_offset = 0
    for img in images:
        column_image.paste(img, (0, y_offset))
        y_offset += img.height
    return column_image


def find_image(folder_path, image_name):
    """Finds an image by name in the given folder."""
    for file in os.listdir(folder_path):
        if (
            file.lower() == f"{image_name.lower()}.jpg"
            or file.lower() == f"{image_name.lower()}.png"
        ):
            return os.path.join(folder_path, file)
    return None


def resize_image(image_path, size):
    """Resizes an image to the specified size."""
    img = Image.open(image_path)
    img = img.resize(size)
    return img


def get_or_create_image(folder_path, image_name, size):
    """Finds an image or creates a blank one if not found."""
    image_path = find_image(folder_path, image_name)
    if image_path is None:
        return create_blank_image(size=size)

    return resize_image(image_path=image_path, size=size)
