from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from backend.generic_image_composer import (
    GenericImageComposer,
    GenericTeamImageComposer,
)
from backend.image_composer import PlayerImageComposer, TeamImageComposer
from backend.style_image_composer import (
    PlayerStyleImageComposer,
    TeamStyleImageComposer,
)
from backend.validators import TournamentDataValidator


@pytest.fixture
def dummy_image():
    return Image.new("RGB", (10, 20), (255, 255, 255))


@patch("backend.generic_image_composer.get_or_create_image")
@patch("backend.generic_image_composer.create_column_image")
def test_generic_image_composer_compose(
    mock_create_column_image, mock_get_or_create_image, dummy_image
):
    mock_get_or_create_image.return_value = dummy_image
    mock_create_column_image.return_value = dummy_image
    composer = GenericImageComposer(Path("base"), Path("modifier"))
    entities_data = [["player1", "mod1", "mod2"], ["player2"]]
    image_size = (10, 20)
    result = composer.compose(entities_data, image_size)
    assert result is not None
    assert mock_create_column_image.call_count == 2


@patch("backend.generic_image_composer.get_or_create_image")
@patch("backend.generic_image_composer.create_column_image")
def test_generic_team_image_composer_compose_team(
    mock_create_column_image, mock_get_or_create_image, dummy_image
):
    mock_get_or_create_image.return_value = dummy_image
    mock_create_column_image.return_value = dummy_image
    composer = GenericImageComposer(Path("base"), Path("modifier"))
    team_composer = GenericTeamImageComposer(composer)
    team_members = ["player1"]
    entities_data = [["player1", "mod1"], ["player2", "mod2"]]
    image_size = (10, 20)
    result = team_composer.compose_team(team_members, entities_data, image_size)
    assert result is not None
    assert mock_create_column_image.call_count == 1


def test_player_image_composer_compose():
    pic = PlayerImageComposer("players", "accessories")
    with patch.object(pic.generic, "compose", return_value="image") as mock_compose:
        result = pic.compose([["player1", "acc1"]], (10, 20))
        assert result == "image"
        mock_compose.assert_called_once()


def test_team_image_composer_compose_team():
    pic = PlayerImageComposer("players", "accessories")
    tic = TeamImageComposer(pic)
    with patch.object(
        tic.generic_team, "compose_team", return_value="team_image"
    ) as mock_team:
        result = tic.compose_team(["player1"], [["player1", "acc1"]], (10, 20))
        assert result == "team_image"
        mock_team.assert_called_once()


def test_player_style_image_composer_compose():
    pic = PlayerStyleImageComposer("players", "styles")
    with patch.object(pic.generic, "compose", return_value="image") as mock_compose:
        result = pic.compose([["player1", "style1"]], (10, 20))
        assert result == "image"
        mock_compose.assert_called_once()


def test_team_style_image_composer_compose_team():
    pic = PlayerStyleImageComposer("players", "styles")
    tic = TeamStyleImageComposer(pic)
    with patch.object(
        tic.generic_team, "compose_team", return_value="team_image"
    ) as mock_team:
        result = tic.compose_team(["player1"], [["player1", "style1"]], (10, 20))
        assert result == "team_image"
        mock_team.assert_called_once()


def test_tournament_data_validator_valid():
    data = "player1, acc1\nplayer2, acc2"
    result = TournamentDataValidator.validate(data)
    assert result == [["player1", "acc1"], ["player2", "acc2"]]


def test_tournament_data_validator_invalid():
    data = "player1\nplayer2, acc2"
    with patch("streamlit.error") as mock_error:
        result = TournamentDataValidator.validate(data)
        assert result is None
        mock_error.assert_called_once()
