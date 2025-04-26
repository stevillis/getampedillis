from backend.utils.utils import get_players_df, get_styles_df, pad_list


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

    monkeypatch.setattr("backend.utils.utils.STYLES_FOLDER", styles_dir)

    df = get_styles_df()
    assert set(df["Name"]) == {"style1", "style2"}
