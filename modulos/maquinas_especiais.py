"""
SINTONIA — Máquinas Elétricas · Módulo 7
Máquinas Elétricas Especiais
"""

import streamlit as st


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');
.mod-header { font-family:'Syne',sans-serif; font-size:2rem; font-weight:700;
              letter-spacing:-.02em; margin-bottom:.15rem; }
.mod-sub    { font-size:.9rem; opacity:.55; margin-bottom:1.2rem;
              font-family:'DM Sans',sans-serif; }
.wip-box {
    border:1.5px dashed rgba(61,142,240,.35); border-radius:8px;
    padding:1.2rem 1.5rem; background:rgba(61,142,240,.04); margin:1.5rem 0;
}
.wip-box h4 { margin:0 0 .4rem; font-family:'Syne',sans-serif;
              font-size:.95rem; color:#3d8ef0; }
.wip-box p  { margin:0; font-size:.82rem; opacity:.65; line-height:1.6; }
</style>
"""


def run():
    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown('<div class="mod-header">🔬 Máquinas Elétricas Especiais</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="mod-sub">MOD 07 &nbsp;·&nbsp; Relutância, Histerese, Passo, BLDC e Linear</div>',
                unsafe_allow_html=True)

    st.markdown("""
Máquinas elétricas especiais são concebidas para aplicações específicas em robótica,
automação industrial, veículos elétricos e sistemas de posicionamento de precisão.
Este módulo cobre motores de relutância, histerese, passo, brushless DC, lineares
e servo-motores com seus respectivos transdutores de posição.
""")

    st.markdown('<div class="wip-box"><h4>🚧 Módulo em construção</h4>'
                '<p>O conteúdo completo está sendo elaborado. '
                'Veja abaixo o esboço do que será coberto.</p></div>',
                unsafe_allow_html=True)

    st.markdown("#### 📋 Conteúdo previsto")

    secoes = [
        ("7.1", "Motor de relutância chaveado (SRM)",
         "Princípio de mínima relutância, construção com pólos salientes no estator e rotor, "
         "acionamento por conversor assimétrico e características torque-velocidade."),
        ("7.2", "Motor de histerese",
         "Torque de histerese e torque de correntes parasitas — curva de operação plana, "
         "partida suave e aplicações em equipamentos de alta precisão e relógios."),
        ("7.3", "Motor de passo (stepper) — tipos e construção",
         "Motor de relutância variável, de ímã permanente e híbrido — "
         "ângulo de passo, resolução e torque de retenção (holding torque)."),
        ("7.4", "Motor de passo — excitação e controle",
         "Sequências de excitação unipolar e bipolar, passo completo, meio-passo "
         "e microstepping — drivers L298, A4988, TMC e controle por Arduino/CNC."),
        ("7.5", "Motor brushless DC (BLDC)",
         "Construção com ímãs permanentes no rotor, comutação eletrônica por sensores "
         "Hall ou encoder, controlador ESC e comparação com motor CC convencional."),
        ("7.6", "Motor síncrono de ímãs permanentes (PMSM)",
         "Diferença entre BLDC e PMSM — controle vetorial (FOC), SVPWM "
         "e aplicações em veículos elétricos e robôs industriais."),
        ("7.7", "Motor linear",
         "Desenvolvimento do motor de indução rotativo em linear — motor de indução "
         "linear (LIM), motor síncrono linear e aplicações em trens de levitação e CNC."),
        ("7.8", "Servo-motores e transdutores de posição",
         "Resolvers, encoders incrementais e absolutos, tacômetros — malha de controle "
         "de posição e velocidade, ganhos PID e aplicações em CNC e robótica."),
    ]

    for num, titulo, desc in secoes:
        with st.expander(f"**{num} · {titulo}**", expanded=False):
            st.markdown(f"_{desc}_")
            st.info("⏳ Conteúdo em elaboração.", icon="📝")

    st.markdown("---")
    st.markdown("#### 🎛️ Exploradores previstos")

    col1, col2 = st.columns(2)
    for col, titulo, desc in zip(
        [col1, col2],
        ["Explorador 1 — Motor de Passo",
         "Explorador 2 — Motor BLDC"],
        ["Sequências de excitação unipolar/bipolar, ângulo de passo e microstepping interativo.",
         "Comutação eletrônica por sinal Hall — posição do rotor e correntes de fase."],
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.caption(desc)
                st.info("Em construção.", icon="🔧")
