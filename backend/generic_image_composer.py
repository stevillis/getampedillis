from PIL import Image

from backend.utils.image_utils import create_column_image, get_or_create_image
from backend.utils.utils import pad_list


class GenericImageComposer:
    def __init__(self, base_folder, modifier_folder):
        self.base_folder = base_folder
        self.modifier_folder = modifier_folder

    def _compose_columns(self, entities_data, image_size):
        columns = []
        for entity in entities_data:
            base_name = entity[0]
            modifiers = entity[1:]

            base_image = get_or_create_image(
                folder_path=self.base_folder,
                image_name=base_name,
                size=image_size,
            )
            column_images = [base_image]

            modifiers = pad_list(modifiers.copy())
            for modifier in modifiers:
                modifier_image = get_or_create_image(
                    folder_path=self.modifier_folder,
                    image_name=modifier,
                    size=image_size,
                )
                column_images.append(modifier_image)

            column_image = create_column_image(column_images)
            columns.append(column_image)

        return columns

    @staticmethod
    def _compose_columns_into_image(columns):
        if not columns:
            return None

        total_width = sum(img.width for img in columns)
        max_height = max(img.height for img in columns)
        composite_image = Image.new("RGB", (total_width, max_height))

        x_offset = 0
        for img in columns:
            composite_image.paste(img, (x_offset, 0))
            x_offset += img.width

        return composite_image

    def compose(self, entities_data, image_size):
        columns = self._compose_columns(entities_data, image_size)
        return self._compose_columns_into_image(columns)


class GenericTeamImageComposer:
    def __init__(self, generic_image_composer):
        self.generic_image_composer = generic_image_composer

    def compose_team(self, team_members, entities_data, image_size):
        filtered_entities = [
            data
            for member in team_members
            for data in entities_data
            if data[0] == member
        ]

        columns = self.generic_image_composer._compose_columns(
            filtered_entities, image_size
        )

        return self.generic_image_composer._compose_columns_into_image(columns)
