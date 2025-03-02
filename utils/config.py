import streamlit as st


def _set_variable_to_session(variable_name, variable_value):
    if variable_name not in st.session_state:
        st.session_state[variable_name] = variable_value


def _set_default_varibles_to_state():
    DEFAULT_PLAYERS_FOLDER = "players"
    DEFAULT_ACCESSORIES_FOLDER = "accs"
    DEFAULT_STYLES_FOLDER = "styles"
    DEFAULT_ACCS_BY_YEAR_FILE = "accs_by_year.xlsx"

    _set_variable_to_session("PLAYERS_FOLDER", DEFAULT_PLAYERS_FOLDER)
    _set_variable_to_session("ACCESSORIES_FOLDER", DEFAULT_ACCESSORIES_FOLDER)
    _set_variable_to_session("STYLES_FOLDER", DEFAULT_STYLES_FOLDER)
    _set_variable_to_session("ACCS_BY_YEAR_FILE", DEFAULT_ACCS_BY_YEAR_FILE)


def set_config_variables():
    _set_default_varibles_to_state()

    with open(file="config.txt", mode="r", encoding="utf-8") as f:
        for line in f:
            key, value = line.strip().split("=")
            _set_variable_to_session(key, value)
