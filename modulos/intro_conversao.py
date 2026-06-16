"""
SINTONIA — Máquinas Elétricas · Módulo 1
Introdução à Conversão Eletromecânica de Energia
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


# ═══════════════════════════════════════════════════════════════════════════════
# CSS compartilhado (injetado uma vez por módulo)
# ═══════════════════════════════════════════════════════════════════════════════
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
.mod-header { font-family:'Syne',sans-serif; font-size:2rem; font-weight:700;
              letter-spacing:-.02em; margin-bottom:.15rem; }
.mod-sub    { font-size:.9rem; opacity:.55; margin-bottom:1.2rem;
              font-family:'IBM Plex Mono',monospace; }
.section-title { font-family:'Syne',sans-serif; font-size:1.1rem;
                 font-weight:700; margin:1.6rem 0 .5rem; }
.wip-box {
    border:1.5px dashed rgba(232,93,4,.35); border-radius:8px;
    padding:1.2rem 1.5rem; background:rgba(232,93,4,.04);
    margin:1.5rem 0;
}
.wip-box h4 { margin:0 0 .4rem; font-family:'Syne',sans-serif;
              font-size:.95rem; color:#3d8ef0; }
.wip-box p  { margin:0; font-size:.82rem; opacity:.65; line-height:1.6; }
</style>
"""


def run():
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Cabeçalho ─────────────────────────────────────────────────────────────
    st.markdown('<div class="mod-header">🔋 Conversão Eletromecânica de Energia</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="mod-sub">MOD 01 &nbsp;·&nbsp; Fundamentos</div>',
                unsafe_allow_html=True)

    st.markdown("""
Este módulo estabelece os fundamentos eletromagnéticos necessários para compreender
o funcionamento de todas as máquinas elétricas. Parte das leis de Maxwell aplicadas
a circuitos magnéticos e avança até o princípio da conversão eletromecânica de energia.
""")

    # ── Marcador de conteúdo em construção ───────────────────────────────────
    st.markdown('<div class="wip-box"><h4>🚧 Módulo em construção</h4>'
                '<p>O conteúdo completo deste módulo está sendo elaborado. '
                'As seções e exploradores interativos serão adicionados progressivamente. '
                'Veja abaixo o esboço do que será coberto.</p></div>',
                unsafe_allow_html=True)

    # ── Esboço das seções ─────────────────────────────────────────────────────
    st.markdown("#### 📋 Conteúdo previsto")

    secoes = [
        ("1.1", "Princípios básicos de eletromagnetismo",
         "Lei de Ampère, Lei de Faraday e Lei de Lenz — fundamentos para análise de máquinas."),
        ("1.2", "Materiais magnéticos",
         "Curva B-H, saturação, histerese e perdas no ferro (Steinmetz)."),
        ("1.3", "Circuitos magnéticos",
         "Relutância $\\mathcal{R}$, fluxo $\\Phi$ e força magnetomotriz (FMM = $NI$)."),
        ("1.4", "Indutância e energia no campo magnético",
         "Energia armazenada $W = \\frac{1}{2}Li^2$, co-energia $W'$ e indutância de entreferro."),
        ("1.5", "Força e torque de origem eletromagnética",
         "Princípio da energia virtual: $f = \\partial W'/\\partial x|_{i=\\text{cte}}$."),
        ("1.6", "Conversão eletromecânica",
         "Gerador vs. motor — diagrama de fluxo de potência e perdas."),
        ("1.7", "Rendimento e balanço de potência",
         "Definição de rendimento $\\eta = P_{saída}/P_{entrada}$, perdas por categoria."),
    ]

    for num, titulo, desc in secoes:
        with st.expander(f"**{num} · {titulo}**", expanded=False):
            st.markdown(f"_{desc}_")
            st.info("⏳ Conteúdo em elaboração.", icon="📝")

    # ── Placeholder de exploradores ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🎛️ Exploradores previstos")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Explorador 1 — Circuito Magnético**")
            st.caption("Relutância, fluxo e FMM com variação de geometria e material.")
            st.info("Em construção.", icon="🔧")

    with col2:
        with st.container(border=True):
            st.markdown("**Explorador 2 — Curva B-H**")
            st.caption("Ponto de operação em materiais magnéticos com saturação.")
            st.info("Em construção.", icon="🔧")
