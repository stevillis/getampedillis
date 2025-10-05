"""
GetAmpedillis - Tournament Image Creator
Main intro page for the GetAmped Tournament image creation app.
"""

import streamlit as st

from backend.utils.utils import hide_header_actions


def render_intro_page():
    """Renders the main introduction page for the GetAmpedillis app."""

    st.title("🎮 GetAmpedillis")
    st.subheader("Tournament Image Creator para GetAmped")

    st.markdown(
        """
    Bem-vindo ao **GetAmpedillis**, uma ferramenta especializada para criar
    imagens de torneios e times do GetAmped de forma rápida e profissional!
    """
    )

    # Features section
    st.markdown("## ✨ Funcionalidades")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        ### 🔧 Criação de Imagens de Acessórios
        - Geração automática de IDs de acessórios
        - Seleção manual de jogadores e equipamentos
        - Criação de imagens de torneios completos
        - Formação automática de times
        """
        )

        st.markdown(
            """
        ### 🐀 Draft Amped
        - Sistema completo de draft para torneios
        - Seleção alternada de jogadores
        - Organização automática de times
        """
        )

    with col2:
        st.markdown(
            """
        ### 💪 Imagens de Estilos
        - Criação de imagens com estilos de luta
        - Combinação de jogadores e seus estilos
        - Geração de times com estilos específicos
        """
        )

        st.markdown(
            """
        ### 🎲 Estilos Random
        - Geração aleatória de combinações de estilos
        - Criação de imagens com estilos surpresa
        - Diversão garantida para eventos casuais
        """
        )

    with col3:
        st.markdown(
            """
        ### 🍀 Roleta do Dedé
        - Sorteios aleatórios para torneios
        - Sistema de roleta interativa
        - Geração de resultados justos e transparentes
        """
        )

        st.markdown(
            """
        ### 🔒 Login & 👑 Admin
        - Sistema seguro de autenticação
        - Roles: Admin, Player, Guest
        - Área administrativa para gerenciar usuários
        - Controle completo de permissões
        """
        )

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center'>
        <small>🎮 GetAmpedillis - Criado para a comunidade GetAmped
        Brasil</small>
    </div>
    """,
        unsafe_allow_html=True,
    )


def main():
    """Main function to run the intro page."""
    st.set_page_config(
        page_title="GetAmpedillis - Tournament Image Creator",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    hide_header_actions()

    # Render the main intro page
    render_intro_page()


if __name__ == "__main__":
    main()
