"""
GetAmpedVive - Criador de Imagens para Torneios
Página principal de introdução do aplicativo GetAmpedVive.
"""

import streamlit as st

from backend.utils.utils import apply_custom_theme


def render_custom_css():
    """Injeta CSS customizado para melhorar a estética da interface."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

        /* Aplica a fonte principal */
        html, body, [class*="st-"] {
            font-family: 'Outfit', sans-serif;
        }

        /* Hero Section (Área de Destaque) */
        .hero-container {
            text-align: center;
            padding: 4rem 2rem;
            background-color: #4197FF;
            border-radius: 24px;
            margin-bottom: 3rem;
            color: white;
            box-shadow: 0 20px 40px rgba(255, 65, 108, 0.2);
            animation: fadeInDown 0.8s ease-out;
        }

        .hero-title {
            font-size: clamp(2.5rem, 5vw, 4.5rem);
            font-weight: 800;
            margin-bottom: 1rem;
            letter-spacing: -0.04em;
            line-height: 1.1;
            color: white !important;
        }

        .hero-subtitle {
            font-size: clamp(1.1rem, 2vw, 1.5rem);
            font-weight: 400;
            opacity: 0.95;
            margin: 0 auto;
            color: white !important;
        }

        /* Feature Cards (Cartões de Funcionalidades) */
        .feature-card {
            background-color: var(--secondary-background-color);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(150, 150, 150, 0.1);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            height: calc(100% - 1.5rem);
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        }

        .feature-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.1);
            border-color: #4197FF;
        }

        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            display: inline-block;
        }

        .feature-title {
            font-weight: 800;
            font-size: 1.4rem;
            margin-bottom: 1rem;
            color: var(--text-color);
            letter-spacing: -0.02em;
        }

        .feature-desc {
            font-size: 1rem;
            color: var(--text-color);
            opacity: 0.8;
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }

        .feature-list {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }

        .feature-list li {
            font-size: 0.95rem;
            color: var(--text-color);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: flex-start;
            opacity: 0.9;
        }

        .feature-list li::before {
            content: "✓";
            color: #4197FF;
            font-weight: bold;
            display: inline-block;
            margin-right: 0.5rem;
        }

        /* Animações */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Rodapé */
        .footer-container {
            text-align: center;
            margin-top: 5rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(150, 150, 150, 0.2);
            color: var(--text-color);
            opacity: 0.6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_intro_page():
    """Renderiza a página principal de introdução da aplicação GetAmpedVive."""

    render_custom_css()

    # Hero Section
    st.markdown(
        """
        <div class="hero-container">
            <h1 class="hero-title">🎮 GetAmpedVive</h1>
            <p class="hero-subtitle">
                Sua central para criar imagens, organizar torneios e realizar sorteios para a comunidade de GetAmped Brasil.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Grid de Funcionalidades
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card" style="margin-bottom: 0.5rem;">
                <div class="feature-icon">🔧</div>
                <h3 class="feature-title">Torneios e Acessórios</h3>
                <p class="feature-desc">Crie chaves visuais com acessórios e jogadores em poucos cliques.</p>
                <ul class="feature-list">
                    <li>Busca fácil de acessórios por Nome e ID</li>
                    <li>Escolha manual de jogadores e equipamentos</li>
                    <li>Agrupamento automático de equipes para torneios</li>
                    <li>Download rápido das imagens prontas</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/1_Torneios_e_Acessorios.py",
            label="Acessar ferramenta",
            icon="👉",
            use_container_width=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="feature-card" style="margin-bottom: 0.5rem;">
                <div class="feature-icon">🐀</div>
                <h3 class="feature-title">Draft Amped</h3>
                <p class="feature-desc">Sistema interativo de draft para campeonatos competitivos.</p>
                <ul class="feature-list">
                    <li>Seleção alternada justa de jogadores</li>
                    <li>Organização e balanceamento em tempo real</li>
                    <li>Formação final das equipes pronta para divulgar</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/4_Draft_Amped.py",
            label="Acessar ferramenta",
            icon="👉",
            use_container_width=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card" style="margin-bottom: 0.5rem;">
                <div class="feature-icon">💪</div>
                <h3 class="feature-title">Estilos de Luta</h3>
                <p class="feature-desc">Gere composições unindo os jogadores aos seus estilos de luta.</p>
                <ul class="feature-list">
                    <li>Combinação visual de personagens e estilos</li>
                    <li>Criação de times com estilos padronizados</li>
                    <li>Interface simples para montar a chave completa</li>
                    <li>Download imediato das composições formadas</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/2_Estilos_de_Luta.py",
            label="Acessar ferramenta",
            icon="👉",
            use_container_width=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="feature-card" style="margin-bottom: 0.5rem;">
                <div class="feature-icon">🎲</div>
                <h3 class="feature-title">Estilos Aleatórios</h3>
                <p class="feature-desc">Geração randômica para eventos casuais e divertidos.</p>
                <ul class="feature-list">
                    <li>Sorteio surpresa de combinações de estilos</li>
                    <li>Diversão garantida sem complicação</li>
                    <li>Imagens prontas com os resultados instantâneos</li>
                    <li>Download universal dos times sorteados</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/5_Estilos_Aleatorios.py",
            label="Acessar ferramenta",
            icon="👉",
            use_container_width=True,
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card" style="margin-bottom: 0.5rem;">
                <div class="feature-icon">🍀</div>
                <h3 class="feature-title">Roleta do Dedé</h3>
                <p class="feature-desc">Sorteios aleatórios, justos e transparentes para a comunidade.</p>
                <ul class="feature-list">
                    <li>Sistema de roleta visual e interativa</li>
                    <li>Definição rápida de regras e participantes</li>
                    <li>Resultados fáceis de compartilhar</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/3_Roleta_do_Dede.py",
            label="Acessar ferramenta",
            icon="👉",
            use_container_width=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="feature-card" style="margin-bottom: 0.5rem;">
                <div class="feature-icon">🔒</div>
                <h3 class="feature-title">Login & Admin</h3>
                <p class="feature-desc">Controle total de permissões para manter o ambiente organizado.</p>
                <ul class="feature-list">
                    <li>Área administrativa completa (Admin)</li>
                    <li>Acesso para jogadores salvarem preferências</li>
                    <li>Modo visitante para experimentar ferramentas</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/6_Login.py",
            label="Ir para o Login",
            icon="👉",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(
            """
            <div class="feature-card" style="margin-bottom: 0.5rem;">
                <div class="feature-icon">🎯</div>
                <h3 class="feature-title">Roleta do Vitin</h3>
                <p class="feature-desc">Roletas duplas simultâneas para configurações dinâmicas.</p>
                <ul class="feature-list">
                    <li>Sorteio de Regras e Estilos visuais</li>
                    <li>Filtros automáticos baseados nos resultados</li>
                    <li>Edição de regras em tempo real</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/8_Roleta_do_Vitin.py",
            label="Acessar ferramenta",
            icon="👉",
            use_container_width=True,
        )

    # Footer
    st.markdown(
        """
        <div class="footer-container">
            <p>Desenvolvido com dedicação para a comunidade de <strong>GetAmped Brasil</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    """Função principal para executar a página inicial."""
    st.set_page_config(
        page_title="GetAmpedVive - Torneios & Ferramentas",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_custom_theme()

    render_intro_page()


if __name__ == "__main__":
    main()
