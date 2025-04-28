from backend.utils.utils import (
    assign_unique_styles_to_players,
    build_image_columns,
    get_players_df,
    get_styles_df,
    pad_list,
    parse_teams_from_text,
)


def test_parse_teams_from_text():
    # Single team, comma-separated
    assert parse_teams_from_text("a, b, c") == [["a", "b", "c"]]

    # Multiple teams, newline-separated
    assert parse_teams_from_text("a, b\nc, d") == [["a", "b"], ["c", "d"]]

    # Extra spaces and empty lines
    assert parse_teams_from_text(" a , b \n\n c ") == [["a", "b"], ["c"]]

    # Trailing commas
    assert parse_teams_from_text("a, b,\nc,") == [["a", "b"], ["c"]]

    # Only empty/whitespace
    assert parse_teams_from_text("   \n  ") == []


def test_assign_unique_styles_to_players():
    teams = [["alice", "bob"], ["bob", "carol"]]
    style_pool = ["Style1", "Style2", "Style3", "Style4"]
    num_styles = 2
    pairs = assign_unique_styles_to_players(teams, style_pool, num_styles)

    # There should be sum(len(team) for team in teams) * num_styles assignments
    expected = sum(len(team) for team in teams) * num_styles

    assert len(pairs) == expected
    # For each team, each player should get num_styles assignments, and all styles should be unique for that player in that team occurrence
    idx = 0
    for team in teams:
        for player in team:
            styles = [pairs[idx + i][1] for i in range(num_styles)]

            assert len(styles) == num_styles
            assert len(styles) == len(
                set(styles)
            )  # no repeats for same player in same team occurrence

            idx += num_styles

    # Warn if not enough styles
    warnings = []
    assign_unique_styles_to_players(teams, ["A"], 2, warn_func=warnings.append)

    assert warnings


def test_build_image_columns():
    # Each player gets a style, columns should be list of lists
    teams = [["alice", "bob"]]
    player_style_pairs = [["alice", "Style1"], ["bob", "Style2"]]
    columns = build_image_columns(teams, player_style_pairs)

    assert isinstance(columns, list)
    assert all(isinstance(col, list) for col in columns)

    # Should match number of players
    assert len(columns) == len(teams[0])

    # Empty input
    assert build_image_columns([], []) == []


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
