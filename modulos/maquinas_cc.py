"""
SINTONIA — Máquinas Elétricas · Módulo 3
Máquinas Elétricas de Corrente Contínua
"""

import streamlit as st


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
.mod-header { font-family:'Syne',sans-serif; font-size:2rem; font-weight:700;
              letter-spacing:-.02em; margin-bottom:.15rem; }
.mod-sub    { font-size:.9rem; opacity:.55; margin-bottom:1.2rem;
              font-family:'IBM Plex Mono',monospace; }
.wip-box {
    border:1.5px dashed rgba(232,93,4,.35); border-radius:8px;
    padding:1.2rem 1.5rem; background:rgba(232,93,4,.04); margin:1.5rem 0;
}
.wip-box h4 { margin:0 0 .4rem; font-family:'Syne',sans-serif;
              font-size:.95rem; color:#3d8ef0; }
.wip-box p  { margin:0; font-size:.82rem; opacity:.65; line-height:1.6; }
</style>
"""


def run():
    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown('<div class="mod-header">⚙️ Máquinas de Corrente Contínua</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="mod-sub">MOD 03 &nbsp;·&nbsp; Gerador e Motor CC</div>',
                unsafe_allow_html=True)

    st.markdown("""
As máquinas de corrente contínua foram historicamente as primeiras máquinas elétricas
de uso industrial e ainda ocupam papel importante em acionamentos de precisão. Este módulo
cobre a teoria de geradores e motores CC com diferentes tipos de excitação e seus métodos
de controle.
""")

    st.markdown('<div class="wip-box"><h4>🚧 Módulo em construção</h4>'
                '<p>O conteúdo completo está sendo elaborado. '
                'Veja abaixo o esboço do que será coberto.</p></div>',
                unsafe_allow_html=True)

    st.markdown("#### 📋 Conteúdo previsto")

    secoes = [
        ("3.1", "Construção da máquina CC",
         "Polo indutor, armadura, comutador, escovas e enrolamentos de compensação."),
        ("3.2", "FEM induzida e torque eletromagnético",
         "$E_A = K\\phi\\omega$ e $\\tau = K\\phi I_A$ — derivação e significado físico."),
        ("3.3", "Gerador CC",
         "Circuitos equivalentes: excitação separada, shunt, série e compound (curto e longo)."),
        ("3.4", "Motor CC — operação",
         "Equação de velocidade $n = (V_T - I_A R_A)/(K\\phi)$, partida e reversão."),
        ("3.5", "Características mecânicas",
         "Conjugado vs. rotação para excitação shunt, série e compound."),
        ("3.6", "Controle e regulação de velocidade",
         "Variação de $R_a$, variação de $V_T$ (conversor), enfraquecimento de campo."),
        ("3.7", "Reação de armadura e comutação",
         "Distorção do campo, interpolos e enrolamentos de compensação."),
    ]

    for num, titulo, desc in secoes:
        with st.expander(f"**{num} · {titulo}**", expanded=False):
            st.markdown(f"_{desc}_")
            st.info("⏳ Conteúdo em elaboração.", icon="📝")

    st.markdown("---")
    st.markdown("#### 🎛️ Exploradores previstos")

    col1, col2, col3 = st.columns(3)
    for col, titulo, desc in zip(
        [col1, col2, col3],
        ["Explorador 1 — Geradores CC",
         "Explorador 2 — Característica Mecânica",
         "Explorador 3 — Controle de Velocidade"],
        ["Curvas $V \times I$ para cada tipo de excitação.",
         "Curva $\\tau \times n$ e ponto de operação com carga.",
         "Efeito de $R_a$, tensão e fluxo na velocidade e torque."],
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.caption(desc)
                st.info("Em construção.", icon="🔧")
