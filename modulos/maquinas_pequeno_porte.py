"""
SINTONIA — Máquinas Elétricas · Módulo 6
Máquinas Elétricas de Pequeno Porte
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

    st.markdown('<div class="mod-header">🔌 Máquinas de Pequeno Porte</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="mod-sub">MOD 06 &nbsp;·&nbsp; Motor Universal e Motor de Indução Monofásico</div>',
                unsafe_allow_html=True)

    st.markdown("""
Motores de pequeno porte estão presentes em praticamente todos os eletrodomésticos e
equipamentos de uso cotidiano. Este módulo cobre o motor universal — que opera tanto em
corrente contínua quanto alternada — e o motor de indução monofásico em suas diversas
variantes de partida, desde o motor com fase auxiliar até o polo sombreado.
""")

    st.markdown('<div class="wip-box"><h4>🚧 Módulo em construção</h4>'
                '<p>O conteúdo completo está sendo elaborado. '
                'Veja abaixo o esboço do que será coberto.</p></div>',
                unsafe_allow_html=True)

    st.markdown("#### 📋 Conteúdo previsto")

    secoes = [
        ("6.1", "Motor universal",
         "Operação em CA e CC, circuito equivalente, características torque-velocidade "
         "e aplicações domésticas (aspiradores, furadeiras, batedeiras)."),
        ("6.2", "Motor de indução monofásico — princípio",
         "Campo pulsante e teoria dos dois campos girantes — decomposição em componentes "
         "progressiva e retrógrada. Torque resultante vs. escorregamento $s$."),
        ("6.3", "Partida com fase auxiliar",
         "Enrolamento auxiliar deslocado no espaço, capacitor de partida vs. resistência "
         "— chave centrífuga e ângulo de fase entre correntes."),
        ("6.4", "Motor com capacitor permanente (PSC)",
         "Capacitor em série com o enrolamento auxiliar em operação contínua — "
         "campo elíptico, rendimento e fator de potência melhorado."),
        ("6.5", "Motor com capacitor de partida e de funcionamento",
         "Dois capacitores: capacitor de partida (maior) chaveado por centrífuga e "
         "capacitor de funcionamento (menor) permanente — compromisso partida × operação."),
        ("6.6", "Motor de polo sombreado",
         "Anel de curto-circuito no polo — princípio, campo giratório resultante, "
         "baixo torque de partida e aplicações (ventiladores, exaustores)."),
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
        ["Explorador 1 — Motor Monofásico",
         "Explorador 2 — Métodos de Partida"],
        ["Componentes de campo progressivo e retrógrado e torque resultante vs. escorregamento.",
         "Comparação de corrente e torque de partida entre fase auxiliar, capacitor e polo sombreado."],
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.caption(desc)
                st.info("Em construção.", icon="🔧")
