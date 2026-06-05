import os
import json
import streamlit as st

from backend.utils import STYLES_FOLDER, STYLE_CATEGORIES
from backend.utils.utils import apply_custom_theme


class RoletaDoVitinApp:
    def __init__(self):
        self.default_regras = list(STYLE_CATEGORIES.keys()) + [
            "ESTILO + GEAR EXCLUSIVO",
            "SWORD/BLADE/GLOVES/HANDS/BOOTS/CHAIN",
            "ARCANA/SUIT/MASK/ARTS/SCYTE/SHIELD",
            "ESTILO IGUAL + ITEM BOMBA",
            "2010",
            "2012",
            "2014",
            "ESTILO + GEAR EXCLUSIVO",
            "GEARS ELEMENTAIS",
        ]
        self.default_estilos = self._get_available_styles()

        if "roleta_regras_v4" not in st.session_state:
            st.session_state.roleta_regras_v4 = self.default_regras.copy()

    def _get_available_styles(self):
        if not os.path.exists(STYLES_FOLDER):
            return ["Sem estilos"]
        styles = set()
        for file in os.listdir(STYLES_FOLDER):
            if file.endswith(".png") or file.endswith(".jpg"):
                name = file.replace(".png", "").replace(".jpg", "")
                if name.lower() == "no":
                    continue
                if name.endswith("A") or name.endswith("B"):
                    styles.add(name[:-1])
                else:
                    styles.add(name)

        result = sorted(list(styles))
        return result if result else ["Sem estilos"]

    def run(self):
        self._render_header()
        self._render_configuration_section()
        self._render_wheel_section()

    def _render_header(self):
        st.markdown(
            """
            <div style="margin-bottom: 2rem;">
                <h1 style="font-weight: 800; font-size: clamp(2rem, 4vw, 3rem); letter-spacing: -0.04em; margin-bottom: 0.5rem; color: #ececec;">🎯 Roleta do Vitin</h1>
                <p style="font-size: 1.1rem; opacity: 0.8; margin-top: 0; max-width: 600px;">
                    Adicione ou remova opções abaixo e gire a roleta principal. As configurações e a roleta de estilos são atualizadas e filtradas automaticamente.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _render_configuration_section(self):
        with st.container(border=True):
            st.markdown(
                '<h3 style="font-weight: 600; font-size: 1.2rem; margin-bottom: 1rem; color: #4197FF;">📝 Configuração da Roda Principal (Regras)</h3>',
                unsafe_allow_html=True,
            )

            edited_regras = st.data_editor(
                {"Regras": st.session_state.roleta_regras_v4},
                num_rows="dynamic",
                key="editor_regras",
                hide_index=True,
                use_container_width=True,
            )
            # Ensure there's at least one item
            new_regras = [
                str(r).strip() for r in edited_regras["Regras"] if r and str(r).strip()
            ]
            if not new_regras:
                new_regras = ["Sem regras"]
            st.session_state.roleta_regras_v4 = new_regras

    def _render_wheel_section(self):
        # Convert lists to JSON to pass to JS
        regras_json = json.dumps(st.session_state.roleta_regras_v4)
        estilos_json = json.dumps(self.default_estilos)
        style_categories_json = json.dumps(STYLE_CATEGORIES)

        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    margin: 0;
                    padding: 40px 20px;
                    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
                    display: flex;
                    justify-content: space-around;
                    background: transparent;
                    color: #ececec;
                }}
                .wheel-container {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    width: 48%;
                    background: rgba(30, 30, 35, 0.4);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 24px;
                    padding: 30px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.2);
                }}
                canvas {{
                    border-radius: 50%;
                    box-shadow: 0 10px 35px rgba(0,0,0,0.4), inset 0 5px 15px rgba(255,255,255,0.1);
                    cursor: pointer;
                    transition: transform 0.15s cubic-bezier(0.4, 0, 0.2, 1);
                    border: 6px solid #1a1a1a;
                    display: block;
                }}
                canvas:active {{ transform: scale(0.97); }}
                .arrow {{
                    width: 0;
                    height: 0;
                    border-top: 20px solid transparent;
                    border-bottom: 20px solid transparent;
                    border-right: 35px solid #fff;
                    position: absolute;
                    right: -15px;
                    top: 50%;
                    transform: translateY(-50%);
                    z-index: 10;
                    filter: drop-shadow(-2px 0px 8px rgba(0,0,0,0.8));
                }}
                .canvas-wrapper {{ position: relative; margin-top: 20px; margin-bottom: 20px; }}
                .result-text {{
                    font-size: 28px;
                    font-weight: 800;
                    min-height: 40px;
                    margin-top: 20px;
                    text-align: center;
                    color: #4197FF;
                    text-shadow: 0 4px 10px rgba(0,0,0,0.5);
                    padding: 15px;
                    border-radius: 12px;
                    background: rgba(0,0,0,0.4);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    width: 100%;
                    box-sizing: border-box;
                    letter-spacing: -0.02em;
                    transition: all 0.3s ease;
                }}
                .title {{
                    font-size: 22px;
                    font-weight: 800;
                    margin-bottom: 10px;
                    text-align: center;
                    color: #fff;
                    letter-spacing: -0.02em;
                }}
                .spin-btn {{
                    margin-top: 15px;
                    padding: 16px 40px;
                    font-size: 18px;
                    font-weight: 800;
                    cursor: pointer;
                    background: #4197FF;
                    color: #fff;
                    border: none;
                    border-radius: 40px;
                    box-shadow: 0 8px 20px rgba(65, 151, 255, 0.3);
                    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }}
                .spin-btn:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 12px 25px rgba(65, 151, 255, 0.4);
                    background: #2b84f0;
                }}
                .spin-btn:active {{
                    transform: translateY(1px);
                    box-shadow: 0 4px 10px rgba(65, 151, 255, 0.2);
                }}
            </style>
        </head>
        <body>

            <div class="wheel-container">
                <div class="title">Roda de Regras</div>
                <div class="canvas-wrapper">
                    <div class="arrow"></div>
                    <canvas id="canvas-regras" width="400" height="400"></canvas>
                </div>
                <button class="spin-btn" id="btn-regras">Girar</button>
                <div class="result-text" id="result-regras">Pronto para girar</div>
            </div>

            <div class="wheel-container">
                <div class="title">Roda de Estilos</div>
                <div class="canvas-wrapper">
                    <div class="arrow"></div>
                    <canvas id="canvas-estilos" width="400" height="400"></canvas>
                </div>
                <button class="spin-btn" id="btn-estilos">Girar</button>
                <div class="result-text" id="result-estilos">Pronto para girar</div>
            </div>

            <script>
                const regras = {regras_json};
                const defaultEstilos = {estilos_json};
                const styleCategories = {style_categories_json};

                const colors = [
                    '#FF3B30', '#FF9500', '#FFCC00', '#4CD964', '#5AC8FA', '#007AFF', '#5856D6', '#FF2D55',
                    '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#3498db', '#9b59b6', '#34495e', '#16a085',
                    '#ff7979', '#badc58', '#dff9fb', '#f6e58d', '#ffbe76', '#ff4d4d', '#c7ecee', '#7ed6df',
                    '#e056fd', '#686de0', '#30336b', '#95afc0', '#22a6b3', '#be2edd', '#4834d4', '#130f40'
                ];

                class Wheel {{
                    constructor(canvasId, items, resultId, btnId) {{
                        this.canvas = document.getElementById(canvasId);
                        this.ctx = this.canvas.getContext('2d');
                        this.items = items;
                        this.numItems = items.length;
                        this.arc = Math.PI / (this.numItems / 2);
                        this.spinAngleStart = 0;
                        this.spinTime = 0;
                        this.spinTimeTotal = 0;
                        this.angle = 0;
                        this.resultEl = document.getElementById(resultId);
                        this.isSpinning = false;

                        this.centerX = this.canvas.width / 2;
                        this.centerY = this.canvas.height / 2;
                        this.radius = this.canvas.width / 2 - 8; // leave room for thick stroke

                        this.draw();

                        const btn = document.getElementById(btnId);
                        btn.addEventListener('click', () => this.spin());
                        this.canvas.addEventListener('click', () => this.spin());
                    }}

                    draw() {{
                        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                        this.ctx.strokeStyle = '#1a1a1a';
                        this.ctx.lineWidth = 3;
                        this.ctx.font = 'bold 16px -apple-system, BlinkMacSystemFont, sans-serif';

                        for (let i = 0; i < this.numItems; i++) {{
                            const angle = this.angle + i * this.arc;
                            this.ctx.fillStyle = colors[i % colors.length];

                            this.ctx.beginPath();
                            this.ctx.arc(this.centerX, this.centerY, this.radius, angle, angle + this.arc, false);
                            this.ctx.lineTo(this.centerX, this.centerY);
                            this.ctx.fill();
                            this.ctx.stroke();

                            this.ctx.save();
                            this.ctx.fillStyle = '#fff';
                            this.ctx.shadowColor = 'rgba(0,0,0,0.9)';
                            this.ctx.shadowBlur = 4;
                            this.ctx.shadowOffsetX = 1;
                            this.ctx.shadowOffsetY = 1;

                            this.ctx.translate(
                                this.centerX + Math.cos(angle + this.arc / 2) * (this.radius - 20),
                                this.centerY + Math.sin(angle + this.arc / 2) * (this.radius - 20)
                            );
                            this.ctx.rotate(angle + this.arc / 2);

                            const text = this.items[i];
                            // Truncate based on number of items (more items -> smaller slices)
                            const maxLen = this.numItems > 20 ? 12 : 20;
                            const shortText = text.length > maxLen ? text.substring(0, maxLen - 2) + '...' : text;

                            this.ctx.textAlign = 'right';
                            this.ctx.textBaseline = 'middle';
                            this.ctx.fillText(shortText, 0, 0);
                            this.ctx.restore();
                        }}

                        // Center circle
                        this.ctx.fillStyle = '#1a1a1a';
                        this.ctx.beginPath();
                        this.ctx.arc(this.centerX, this.centerY, 40, 0, 2 * Math.PI);
                        this.ctx.fill();

                        this.ctx.strokeStyle = '#333';
                        this.ctx.lineWidth = 4;
                        this.ctx.beginPath();
                        this.ctx.arc(this.centerX, this.centerY, 36, 0, 2 * Math.PI);
                        this.ctx.stroke();

                        this.ctx.fillStyle = '#666';
                        this.ctx.beginPath();
                        this.ctx.arc(this.centerX, this.centerY, 10, 0, 2 * Math.PI);
                        this.ctx.fill();
                    }}

                    updateItems(items) {{
                        this.items = items;
                        this.numItems = items.length;
                        this.arc = Math.PI / (this.numItems / 2);
                        this.angle = 0;
                        this.draw();
                        this.resultEl.innerText = "Pronto para girar";
                        this.resultEl.style.color = '#4197FF';
                    }}

                    spin() {{
                        if (this.isSpinning) return;
                        this.isSpinning = true;

                        // Add minimum spins (10-20 full rotations) + random end
                        this.spinAngleStart = Math.random() * 10 + 20;
                        this.spinTime = 0;
                        this.spinTimeTotal = Math.random() * 3000 + 4000;
                        this.resultEl.innerText = 'Girando...';
                        this.resultEl.style.color = '#888';
                        this.rotate();
                    }}

                    rotate() {{
                        this.spinTime += 30;
                        if (this.spinTime >= this.spinTimeTotal) {{
                            this.stop();
                            return;
                        }}
                        const spinAngle = this.spinAngleStart - easeOut(this.spinTime, 0, this.spinAngleStart, this.spinTimeTotal);
                        this.angle += (spinAngle * Math.PI / 180);
                        this.draw();
                        requestAnimationFrame(() => this.rotate());
                    }}

                    stop() {{
                        this.isSpinning = false;

                        let normalizedAngle = this.angle % (2 * Math.PI);
                        if (normalizedAngle < 0) normalizedAngle += 2 * Math.PI;

                        // Adding a tiny epsilon to handle floating point precision when exactly on the line
                        let winIdx = Math.floor(((2 * Math.PI - normalizedAngle) / this.arc) + 0.000001) % this.numItems;

                        if(winIdx >= 0 && winIdx < this.numItems) {{
                            const winner = this.items[winIdx];
                            this.resultEl.innerText = '🎉 ' + winner + ' 🎉';
                            this.resultEl.style.color = '#ffda44';

                            // Simple pop animation
                            this.resultEl.style.transform = 'scale(1.05)';
                            setTimeout(() => {{ this.resultEl.style.transform = 'scale(1)'; }}, 200);

                            // Dynamic updating for the Estilos wheel
                            if (this.canvas.id === 'canvas-regras') {{
                                let newEstilos = styleCategories[winner];
                                if (!newEstilos) {{
                                    newEstilos = defaultEstilos;
                                }}
                                if (window.wheelEstilos) {{
                                    window.wheelEstilos.updateItems(newEstilos);
                                }}
                            }}

                            // Show balloons inside the iframe
                            showBalloons();
                        }} else {{
                            this.resultEl.innerText = "Erro ao calcular";
                        }}
                    }}
                }}

                function easeOut(t, b, c, d) {{
                    t /= d;
                    t--;
                    return c * (Math.pow(t, 5) + 1) + b;
                }}

                function showBalloons() {{
                    const colors = ['#FF3B30', '#FF9500', '#FFCC00', '#4CD964', '#5AC8FA', '#007AFF', '#5856D6', '#FF2D55', '#e056fd', '#be2edd'];
                    for(let i = 0; i < 40; i++) {{
                        const balloon = document.createElement('div');
                        balloon.style.position = 'fixed';
                        balloon.style.bottom = '-100px';
                        balloon.style.left = (Math.random() * 100) + 'vw';
                        balloon.style.width = (Math.random() * 20 + 20) + 'px';
                        balloon.style.height = (parseFloat(balloon.style.width) * 1.3) + 'px';
                        balloon.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                        balloon.style.borderRadius = '50% 50% 50% 50% / 40% 40% 60% 60%';
                        balloon.style.zIndex = '9999';
                        balloon.style.opacity = '0.9';
                        balloon.style.boxShadow = 'inset -5px -5px 15px rgba(0,0,0,0.2)';

                        const string = document.createElement('div');
                        string.style.position = 'absolute';
                        string.style.bottom = '-20px';
                        string.style.left = '50%';
                        string.style.transform = 'translateX(-50%)';
                        string.style.width = '1px';
                        string.style.height = '20px';
                        string.style.backgroundColor = 'rgba(255,255,255,0.5)';
                        balloon.appendChild(string);

                        document.body.appendChild(balloon);

                        const duration = Math.random() * 2000 + 3000;
                        balloon.animate([
                            {{ transform: `translateY(0) rotate(${{Math.random()*20-10}}deg)` }},
                            {{ transform: `translateY(-120vh) rotate(${{Math.random()*40-20}}deg)` }}
                        ], {{
                            duration: duration,
                            easing: 'ease-out',
                            fill: 'forwards'
                        }});

                        setTimeout(() => balloon.remove(), duration);
                    }}
                }}

                // Initialize and keep references
                window.wheelRegras = null;
                window.wheelEstilos = null;
                if (regras.length > 0) window.wheelRegras = new Wheel('canvas-regras', regras, 'result-regras', 'btn-regras');
                if (defaultEstilos.length > 0) window.wheelEstilos = new Wheel('canvas-estilos', defaultEstilos, 'result-estilos', 'btn-estilos');

            </script>
        </body>
        </html>
        """
        st.components.v1.html(html_code, height=750)


if __name__ == "__main__":
    st.set_page_config(page_title="Roleta do Vitin", page_icon="🎯", layout="wide")
    apply_custom_theme()
    app = RoletaDoVitinApp()
    app.run()
