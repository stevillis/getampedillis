import numpy as np
import pytest
from PIL import Image

from backend.utils.image_utils import (
    apply_transparent_gray,
    create_column_image,
    draw_row_numbers,
    find_image,
    get_num_rows,
    get_or_create_image,
    handle_player_image_upload,
    remove_rows,
    resize_image,
    roulette_team_rows,
)


def test_apply_transparent_gray():
    img = Image.new("RGB", (10, 10), (100, 100, 100))
    out = apply_transparent_gray(img, alpha=128)

    assert isinstance(out, Image.Image)

    # Should not be identical to the original
    assert out.tobytes() != img.tobytes()


def test_get_num_rows():
    img = Image.new("RGB", (10, 30))

    assert get_num_rows(img, row_height=10) == 3
    assert get_num_rows(img, row_height=15) == 2


def test_draw_row_numbers():
    img = Image.new("RGBA", (50, 30), (255, 255, 255, 255))
    out = draw_row_numbers(img, excluded_rows=[1], row_height=10)

    assert isinstance(out, Image.Image)

    # Check that excluded row is grayed out (not pure white)
    arr = np.array(out)

    # The first pixel of row 1 (excluded) should not be pure white
    assert not (arr[10, 45] == [255, 255, 255, 255]).all()


def test_remove_rows():
    # Create image with 3 colored rows
    img = Image.new("RGB", (5, 15))
    for y in range(5):
        img.putpixel((0, y), (255, 0, 0))  # Row 0

    for y in range(5, 10):
        img.putpixel((0, y), (0, 255, 0))  # Row 1

    for y in range(10, 15):
        img.putpixel((0, y), (0, 0, 255))  # Row 2

    # Remove row 1
    out = remove_rows(img, excluded_rows=[1], row_height=5)

    assert isinstance(out, Image.Image)

    arr = np.array(out)

    # Should have only rows 0 and 2
    assert arr.shape[0] == 10

    # Top pixel should be red, bottom should be blue

    assert (arr[0, 0] == [255, 0, 0]).all()
    assert (arr[-1, 0] == [0, 0, 255]).all()

    # Remove all rows
    assert remove_rows(img, excluded_rows=[0, 1, 2], row_height=5) is None


class DummyUploadedFile:
    def __init__(self, name: str, content: bytes):
        self.name = name
        self._content = content

    def getvalue(self):
        return self._content


def test_create_column_image():
    img1 = Image.new("RGB", (10, 10), (255, 0, 0))
    img2 = Image.new("RGB", (10, 20), (0, 255, 0))
    column = create_column_image([img1, img2])

    assert column.size == (10, 30)


def test_find_image_found_and_not_found(tmp_path):
    # Found
    img_path = tmp_path / "foo.png"
    Image.new("RGB", (5, 5)).save(img_path)

    # Test different cases
    assert find_image(tmp_path, "foo") == str(img_path)
    assert find_image(tmp_path, "FOO") == str(img_path)
    assert find_image(tmp_path, "FoO") == str(img_path)

    # Not found
    assert find_image(tmp_path, "bar") is None


def test_resize_image(tmp_path):
    img_path = tmp_path / "img.png"
    Image.new("RGB", (10, 10)).save(img_path)
    resized = resize_image(img_path, (5, 5))

    assert resized.size == (5, 5)


def test_get_or_create_image_found_and_blank(tmp_path):
    # Found
    img_path = tmp_path / "foo.png"
    Image.new("RGB", (10, 10)).save(img_path)
    # Test different cases
    for case in ["foo", "FOO", "FoO"]:
        out = get_or_create_image(tmp_path, case, (5, 5))
        assert isinstance(out, Image.Image)
        assert out.size == (5, 5)

    # Not found
    out2 = get_or_create_image(tmp_path, "bar", (5, 5))
    assert isinstance(out2, Image.Image)
    assert out2.size == (5, 5)


def test_handle_player_image_upload_success(tmp_path, monkeypatch):
    player_name = "player1"
    img_content = b"fakeimagecontent"
    uploaded_file = DummyUploadedFile(f"{player_name}.png", img_content)

    monkeypatch.setattr("backend.utils.image_utils.PLAYERS_FOLDER", tmp_path)

    status, msg = handle_player_image_upload(
        player_name=player_name,
        uploaded_file=uploaded_file,
    )

    assert status == "success"
    assert "sucesso" in msg
    assert (tmp_path / f"{player_name}.png").exists()

    with open(tmp_path / f"{player_name}.png", "rb") as f:
        assert f.read() == img_content


def test_handle_player_image_upload_duplicate(tmp_path, monkeypatch):
    player_name = "player1"
    img_content = b"img"
    (tmp_path / f"{player_name}.jpg").write_bytes(img_content)
    uploaded_file = DummyUploadedFile(f"{player_name}.png", img_content)

    monkeypatch.setattr("backend.utils.image_utils.PLAYERS_FOLDER", tmp_path)

    status, msg = handle_player_image_upload(
        player_name=player_name,
        uploaded_file=uploaded_file,
    )

    assert status == "error"
    assert "Já existe" in msg


def test_handle_player_image_upload_empty_name(tmp_path, monkeypatch):
    img_content = b"img"
    uploaded_file = DummyUploadedFile("no_name.png", img_content)

    monkeypatch.setattr("backend.utils.image_utils.PLAYERS_FOLDER", tmp_path)

    status, msg = handle_player_image_upload(
        player_name=" ",
        uploaded_file=uploaded_file,
    )

    assert status == "error"
    assert "Coloque o nome" in msg


def test_roulette_team_rows_default_rng(monkeypatch):
    # Test that default rng (None) uses random
    called = {}

    class DummyRandom:
        def sample(self, seq, k):
            called["used"] = True
            return seq[:k]

    monkeypatch.setattr("random.sample", DummyRandom().sample)

    row_height = 10
    num_rows = 3
    width = 10
    height = row_height * num_rows
    img = Image.new("RGB", (width, height))

    for i, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
        for y in range(i * row_height, (i + 1) * row_height):
            for x in range(width):
                img.putpixel((x, y), color)

    roulette_team_rows(
        [img, img],
        num_rows=num_rows,
        row_height=row_height,
        avatar_row=1,
        num_accessory_rows=1,
    )

    assert called.get("used") is True


def test_roulette_team_rows_no_valid_rows():
    # Test ValueError if no valid rows
    row_height = 10
    num_rows = 1  # Only avatar row, no accessory rows
    width = 10
    height = row_height * num_rows
    img = Image.new("RGB", (width, height))

    with pytest.raises(ValueError) as excinfo:
        roulette_team_rows(
            [img, img],
            num_rows=num_rows,
            row_height=row_height,
            avatar_row=1,
            num_accessory_rows=1,
        )
    assert "Quantidade de linhas de acessório" in str(excinfo.value)


def test_roulette_team_rows_basic():
    # Create two images with 3 rows (avatar + 2 accessories), 10x30, each row 10px tall
    row_height = 10
    num_rows = 3
    width = 10
    height = row_height * num_rows

    # First image: red, green, blue rows
    img1 = Image.new("RGB", (width, height))
    for i, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
        for y in range(i * row_height, (i + 1) * row_height):
            for x in range(width):
                img1.putpixel((x, y), color)

    # Second image: yellow, magenta, cyan rows
    img2 = Image.new("RGB", (width, height))
    for i, color in enumerate([(255, 255, 0), (255, 0, 255), (0, 255, 255)]):
        for y in range(i * row_height, (i + 1) * row_height):
            for x in range(width):
                img2.putpixel((x, y), color)

    # Use a fixed random seed for deterministic roulette
    class DummyRNG:
        def sample(self, seq, k):
            return seq[:k]  # always pick the first k accessory rows

    sampled_rows, avatar_imgs, accessory_imgs = roulette_team_rows(
        [img1, img2],
        num_rows=num_rows,
        row_height=row_height,
        avatar_row=1,
        rng=DummyRNG(),
        num_accessory_rows=1,
    )

    assert sampled_rows == [1]

    # Check avatar rows
    for i, avatar_img in enumerate(avatar_imgs):
        arr = np.array(avatar_img)
        assert arr.shape == (row_height, width, 3)

    # Check accessory rows
    arr1 = np.array(accessory_imgs[0][0])
    arr2 = np.array(accessory_imgs[1][0])

    assert (
        (arr1 == [0, 255, 0]).all(axis=2).any()
    ), "First image's accessory row should be green"
    assert (
        (arr2 == [255, 0, 255]).all(axis=2).any()
    ), "Second image's accessory row should be magenta"
