import streamlit as st


class TournamentDataValidator:
    @staticmethod
    def validate(tournament_data, error_message=None):
        """Validates the input data format."""
        players_data = []
        for line in tournament_data.splitlines():
            if line.strip():  # Skip empty lines
                player_data = [item.strip() for item in line.split(",")]
                if len(player_data) < 2:
                    st.error(
                        error_message
                        or "Formato inválido! Cada linha deve conter pelo menos dois itens separados por vírgula."
                    )
                    return None
                players_data.append(player_data)

        return players_data
