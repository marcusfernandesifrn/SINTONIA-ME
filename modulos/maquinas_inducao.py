"""
SINTONIA — Máquinas Elétricas · Módulo 4
Máquinas Elétricas Polifásicas de CA: Indução
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

    st.markdown('<div class="mod-header">🌀 Máquinas de Indução</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="mod-sub">MOD 04 &nbsp;·&nbsp; CA Polifásica — Rotor Gaiola e Bobinado</div>',
                unsafe_allow_html=True)

    st.markdown("""
O motor de indução trifásico é a máquina elétrica mais utilizada na indústria mundial,
responsável por cerca de 70% do consumo elétrico industrial. Este módulo cobre desde o
princípio do campo girante até técnicas de partida, controle de velocidade por inversor
de frequência e operação como gerador.
""")

    st.markdown('<div class="wip-box"><h4>🚧 Módulo em construção</h4>'
                '<p>O conteúdo completo está sendo elaborado. '
                'Veja abaixo o esboço do que será coberto.</p></div>',
                unsafe_allow_html=True)

    st.markdown("#### 📋 Conteúdo previsto")

    secoes = [
        ("4.1", "Campo girante trifásico",
         "Princípio de geração, velocidade síncrona $n_s = 120f/p$ e número de polos."),
        ("4.2", "Escorregamento",
         "$s = (n_s - n)/n_s$ — frequência do rotor $f_r = s \\cdot f$ e tensão induzida."),
        ("4.3", "Circuito equivalente por fase",
         "Referido ao estator: $R_1$, $X_1$, $R_c$, $X_m$, $R_2'/s$ e $X_2'$."),
        ("4.4", "Potência e torque",
         "$P_{ag}$, $P_{conv} = (1-s)P_{ag}$, $P_{saída}$ e $\\tau_{ind} = P_{ag}/\\omega_s$."),
        ("4.5", "Curva de torque vs. escorregamento",
         "Torque máximo $\\tau_{max}$, escorregamento crítico $s_{max}$ e torque de partida."),
        ("4.6", "Ensaios de parâmetros",
         "Rotor bloqueado e à vazio — determinação de $R_1$, $X_1$, $R_2'$, $X_2'$, $X_m$."),
        ("4.7", "Métodos de partida",
         "Direta, estrela-triângulo, autotransformador, soft-starter — corrente e torque."),
        ("4.8", "Controle de velocidade",
         "Variação de frequência (V/f e vetorial), número de polos, resistência no rotor."),
        ("4.9", "Motor com rotor bobinado",
         "Inserção de resistência externa — curvas de torque e controle de partida."),
        ("4.10", "Gerador de indução",
         "Operação acima da velocidade síncrona, auto-excitação com capacitores."),
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
         "Explorador 2 — Curva de Torque",
         "Explorador 3 — Partida"],
        ["Potência e torque em função do escorregamento e da carga.",
         "Efeito de $R_2'$, $X_1$, $X_2'$ e $V_1$ na curva $\\tau \\times s$.",
         "Transiente de corrente e torque com diferentes métodos de partida."],
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.caption(desc)
                st.info("Em construção.", icon="🔧")
