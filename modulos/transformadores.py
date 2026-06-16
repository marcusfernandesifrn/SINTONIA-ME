"""
SINTONIA — Máquinas Elétricas · Módulo 2
Transformadores
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

    st.markdown('<div class="mod-header">🔄 Transformadores</div>', unsafe_allow_html=True)
    st.markdown('<div class="mod-sub">MOD 02 &nbsp;·&nbsp; Fundamentos e Circuito Equivalente</div>',
                unsafe_allow_html=True)

    st.markdown("""
Os transformadores são dispositivos estáticos de conversão eletromagnética que permitem
alterar níveis de tensão e corrente em sistemas de corrente alternada, com altíssimo
rendimento. Este módulo cobre desde o transformador ideal até ligações trifásicas e
autotransformadores.
""")

    st.markdown('<div class="wip-box"><h4>🚧 Módulo em construção</h4>'
                '<p>O conteúdo completo está sendo elaborado. '
                'Veja abaixo o esboço do que será coberto.</p></div>',
                unsafe_allow_html=True)

    st.markdown("#### 📋 Conteúdo previsto")

    secoes = [
        ("2.1", "Princípio de funcionamento",
         "Relação de transformação $a = N_1/N_2$ — tensões, correntes e impedâncias."),
        ("2.2", "Transformador ideal",
         "Hipóteses simplificadoras, potência e referenciamento de grandezas."),
        ("2.3", "Circuito equivalente completo",
         "$R_1$, $X_1$, $R_c$, $X_m$, $R_2'$ e $X_2'$ — parâmetros e significado físico."),
        ("2.4", "Circuito equivalente simplificado",
         "Referido ao primário e ao secundário — quando é válido simplificar."),
        ("2.5", "Ensaios de parâmetros",
         "Ensaio de curto-circuito (CC) e circuito aberto (CA) — procedimento e cálculo."),
        ("2.6", "Regulação de tensão",
         "$RV = (V_{2,vazio} - V_{2,carga})/V_{2,nominal}$ — diagrama fasorial."),
        ("2.7", "Perdas e rendimento",
         "Perdas no cobre ($P_{cu}$) e no ferro ($P_{fe}$) — rendimento máximo."),
        ("2.8", "Transformadores trifásicos",
         "Ligações Δ-Y, Y-Y, Δ-Δ e Y-Δ — defasagem e grupo de ligação."),
        ("2.9", "Autotransformadores",
         "Relação de transformação, potência conduzida e aparente, economia de cobre."),
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
        ["Explorador 1 — Circuito Equivalente",
         "Explorador 2 — Regulação e Fasorial",
         "Explorador 3 — Rendimento vs. Carga"],
        ["Variação de carga, fator de potência e ramo de magnetização.",
         "Diagrama fasorial interativo com variação de $fp$ e carga.",
         "Curvas de rendimento para diferentes características de perdas."],
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.caption(desc)
                st.info("Em construção.", icon="🔧")
