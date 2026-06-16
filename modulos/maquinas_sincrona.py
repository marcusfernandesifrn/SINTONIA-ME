"""
SINTONIA — Máquinas Elétricas · Módulo 5
Máquinas Elétricas Polifásicas de CA: Síncrona
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

    st.markdown('<div class="mod-header">🔁 Máquinas Síncronas</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="mod-sub">MOD 05 &nbsp;·&nbsp; CA Polifásica — Gerador e Motor Síncrono</div>',
                unsafe_allow_html=True)

    st.markdown("""
As máquinas síncronas são a principal fonte de geração de energia elétrica no mundo —
toda a eletricidade da rede é produzida por geradores síncronos em usinas hidrelétricas,
termelétricas e nucleares. Este módulo cobre o gerador e o motor síncrono, desde o circuito
equivalente até a operação em paralelo com a rede e a máquina com pólos salientes.
""")

    st.markdown('<div class="wip-box"><h4>🚧 Módulo em construção</h4>'
                '<p>O conteúdo completo está sendo elaborado. '
                'Veja abaixo o esboço do que será coberto.</p></div>',
                unsafe_allow_html=True)

    st.markdown("#### 📋 Conteúdo previsto")

    secoes = [
        ("5.1", "Construção",
         "Pólos salientes vs. lisos, excitação por escovas e sem escovas (brushless), enrolamentos."),
        ("5.2", "FEM interna e circuito equivalente",
         "$E_A = K\\phi\\omega$, reatância síncrona $X_s$, resistência $R_A$ e modelo por fase."),
        ("5.3", "Diagrama fasorial do gerador",
         "Operação a plena carga: lagging, unity e leading — triângulo de potência."),
        ("5.4", "Curva de capacidade",
         "Região de operação no plano $P$-$Q$ — limites de $I_A$, $I_F$ e estabilidade."),
        ("5.5", "Regulação de tensão e compoundagem",
         "$RV = (V_{nl} - V_{fl})/V_{fl}$ — curvas de compoundagem para diferentes $fp$."),
        ("5.6", "Ensaios de parâmetros",
         "Circuito aberto e curto-circuito — reatância síncrona não saturada $X_s$."),
        ("5.7", "Operação em paralelo com a rede",
         "Sincronização, controle de $P$ (regulador de velocidade) e $Q$ (excitação)."),
        ("5.8", "Motor síncrono",
         "Partida, torque de relutância, motor sub/super-excitado e condensador síncrono."),
        ("5.9", "Máquina com pólos salientes",
         "Reatâncias $X_d$ e $X_q$, diagrama fasorial e torque de relutância."),
        ("5.10", "Potência e estabilidade de estado estacionário",
         "$P = (V_\\phi E_A / X_s)\\sin\\delta$ — ângulo de carga e limite de estabilidade."),
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
        ["Explorador 1 — Diagrama Fasorial",
         "Explorador 2 — Curva P-δ",
         "Explorador 3 — Paralelo com Rede"],
        ["Variação de $I_F$, $P$ e $fp$ — gerador e motor.",
         "Curva de potência vs. ângulo de carga e limite de estabilidade.",
         "Despacho de potência ativa e reativa em paralelo com barra infinita."],
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.caption(desc)
                st.info("Em construção.", icon="🔧")
