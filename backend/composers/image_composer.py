from backend.composers.generic_image_composer import (
    GenericImageComposer,
    GenericTeamImageComposer,
)


class PlayerImageComposer:
    def __init__(self, players_folder, accessories_folder):
        self.generic = GenericImageComposer(players_folder, accessories_folder)
        self.players_folder = players_folder
        self.accessories_folder = accessories_folder

    def compose(self, players_data, image_size):
        return self.generic.compose(players_data, image_size)


class TeamImageComposer:
    def __init__(self, player_image_composer):
        self.generic_team = GenericTeamImageComposer(player_image_composer.generic)
        self.player_image_composer = player_image_composer

    def compose_team(self, team_members, players_data, image_size):
        return self.generic_team.compose_team(team_members, players_data, image_size)
