from backend.composers.generic_image_composer import (
    GenericImageComposer,
    GenericTeamImageComposer,
)


class PlayerStyleImageComposer:
    def __init__(self, players_folder, styles_folder):
        self.generic = GenericImageComposer(players_folder, styles_folder)

    def compose(self, players_data, image_size):
        return self.generic.compose(players_data, image_size)


class TeamStyleImageComposer:
    def __init__(self, player_style_image_composer):
        self.generic_team = GenericTeamImageComposer(
            player_style_image_composer.generic
        )
        self.player_style_image_composer = player_style_image_composer

    def compose_team(self, team_members, players_data, image_size):
        return self.generic_team.compose_team(team_members, players_data, image_size)
