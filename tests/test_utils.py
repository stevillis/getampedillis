from PIL import Image

from backend.generic_image_composer import GenericImageComposer
from backend.utils.image_utils import (
    create_column_image,
    find_image,
    get_or_create_image,
    resize_image,
)
from backend.utils.utils import get_players_df, get_styles_df, pad_list


def test_create_column_image():
    img1 = Image.new("RGB", (10, 10), (255, 0, 0))
    img2 = Image.new("RGB", (10, 20), (0, 255, 0))
    column = create_column_image([img1, img2])
    assert column.size == (10, 30)


def test_compose_columns_into_image_empty():
    assert GenericImageComposer._compose_columns_into_image([]) is None


def test_find_image_found_and_not_found(tmp_path):
    # Found
    img_path = tmp_path / "foo.png"
    Image.new("RGB", (5, 5)).save(img_path)
    result = find_image(tmp_path, "foo")
    assert result == str(img_path)
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
    out = get_or_create_image(tmp_path, "foo", (5, 5))
    assert isinstance(out, Image.Image)
    assert out.size == (5, 5)
    # Not found
    out2 = get_or_create_image(tmp_path, "bar", (5, 5))
    assert isinstance(out2, Image.Image)
    assert out2.size == (5, 5)


def test_pad_list_behavior():
    # shorter than min
    assert pad_list(["a"], min_len=3, max_len=5, fill_with="x") == ["a"]
    # between min and max
    assert pad_list(["a", "b", "c"], min_len=2, max_len=5, fill_with="x") == [
        "a",
        "b",
        "c",
        "x",
        "x",
    ]
    # longer than max
    assert pad_list(
        ["a", "b", "c", "d", "e", "f"], min_len=2, max_len=5, fill_with="x"
    ) == ["a", "b", "c", "d", "e", "f"]


def test_get_players_df(tmp_path, monkeypatch):
    players_dir = tmp_path / "players"
    players_dir.mkdir()
    (players_dir / "foo.png").touch()
    (players_dir / "bar.jpg").touch()
    (players_dir / "notplayer.txt").touch()
    (players_dir / "no.png").touch()
    monkeypatch.setattr("backend.utils.utils.PLAYERS_FOLDER", players_dir)
    df = get_players_df()
    assert set(df["Name"]) == {"foo", "bar"}


def test_get_styles_df(tmp_path, monkeypatch):
    styles_dir = tmp_path / "styles"
    styles_dir.mkdir()
    (styles_dir / "style1.png").touch()
    (styles_dir / "style2.jpg").touch()
    (styles_dir / "no.jpg").touch()
    monkeypatch.setattr("backend.utils.utils.STYLES_FOLDER", styles_dir)
    df = get_styles_df()
    assert set(df["Name"]) == {"style1", "style2"}
