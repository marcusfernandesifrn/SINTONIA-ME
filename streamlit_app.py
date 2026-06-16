"""
SINTONIA — Máquinas Elétricas
Sistemas Interativos para Teoria e Otimização no Nível de Interpretação e Aprendizagem
streamlit_app.py — Entrypoint principal
Streamlit >= 1.36 — st.navigation com funções Python como páginas
"""

import streamlit as st
import importlib

st.set_page_config(
    page_title="SINTONIA — Máquinas Elétricas",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Utilitário: importa (ou recarrega) módulo e chama run() ──────────────────
def _rodar(nome_modulo: str):
    import sys
    if nome_modulo in sys.modules:
        mod = importlib.reload(sys.modules[nome_modulo])
    else:
        mod = importlib.import_module(nome_modulo)
    mod.run()

# ── Funções de página ────────────────────────────────────────────────────────
def pagina_intro():    _rodar("modulos.intro_conversao")
def pagina_transf():   _rodar("modulos.transformadores")
def pagina_cc():       _rodar("modulos.maquinas_cc")
def pagina_inducao():  _rodar("modulos.maquinas_inducao")
def pagina_sincrona(): _rodar("modulos.maquinas_sincrona")
def pagina_pp():       _rodar("modulos.maquinas_pequeno_porte")
def pagina_esp():      _rodar("modulos.maquinas_especiais")

# ── Definição das páginas com url_path explícito ─────────────────────────────
PG_HOME  = st.Page(lambda: _home(),  title="Página Inicial",                         icon="📘", default=True, url_path="home")
PG_INTRO = st.Page(pagina_intro,     title="Introdução à Conversão Eletromecânica",  icon="🔋", url_path="introducao")
PG_TRANSF= st.Page(pagina_transf,    title="Transformadores",                        icon="🔄", url_path="transformadores")
PG_CC    = st.Page(pagina_cc,        title="Máquinas de Corrente Contínua",          icon="⚙️", url_path="corrente-continua")
PG_IND   = st.Page(pagina_inducao,   title="Máquinas de Indução (CA Polifásica)",    icon="🌀", url_path="inducao")
PG_SINC  = st.Page(pagina_sincrona,  title="Máquinas Síncronas (CA Polifásica)",     icon="🔁", url_path="sincrona")
PG_PP    = st.Page(pagina_pp,        title="Máquinas de Pequeno Porte",              icon="🔌", url_path="pequeno-porte")
PG_ESP   = st.Page(pagina_esp,       title="Máquinas Especiais",                     icon="🔬", url_path="especiais")

# ── Navegação ─────────────────────────────────────────────────────────────────
_nav = st.navigation(
    {
        "🏠 Início":                        [PG_HOME],
        "🔋 Fundamentos":                   [PG_INTRO],
        "🔄 Transformadores":               [PG_TRANSF],
        "⚙️ Máquinas CC":                   [PG_CC],
        "🌀 Máquinas CA — Indução":         [PG_IND],
        "🔁 Máquinas CA — Síncronas":       [PG_SINC],
        "🔌 Máquinas de Pequeno Porte":     [PG_PP],
        "🔬 Máquinas Especiais":            [PG_ESP],
    },
    position="sidebar",
    expanded=True,
)

# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.5rem; font-weight: 800; line-height: 1.18; margin: 0 0 0.5rem;
}
.hero-sub  { font-size: 1.02rem; opacity: .72; max-width: 640px; margin-bottom: .55rem; }
.meta-line { font-size: .82rem; opacity: .50; margin-top: .4rem; }
.red-badge {
    display: inline-block;
    background: linear-gradient(135deg,#3d8ef0 0%,#6c47ff 100%);
    color: #fff; font-size: .7rem; font-weight: 700;
    letter-spacing: .12em; text-transform: uppercase;
    padding: 3px 10px; border-radius: 20px; margin-right: .5rem; vertical-align: middle;
}
.stat-row {
    display: flex; gap: 2.5rem; margin: 1.4rem 0 2rem; padding: 1rem 0;
    border-top: 1px solid rgba(128,128,128,.15);
    border-bottom: 1px solid rgba(128,128,128,.15);
    flex-wrap: wrap;
}
.stat-item { text-align: center; }
.stat-num   { font-size: 1.7rem; font-weight: 700; color: #3d8ef0; }
.stat-label { font-size: .68rem; text-transform: uppercase; letter-spacing: .09em; opacity: .48; }

.mod-card {
    border: 1.5px solid rgba(128,128,128,.18); border-radius: 14px;
    padding: 1.05rem 1.15rem .85rem;
    transition: border-color .18s, box-shadow .18s, transform .12s;
}
.mod-card:hover {
    border-color: #3d8ef0;
    box-shadow: 0 4px 18px rgba(61,142,240,.13);
    transform: translateY(-2px);
}
.mod-num  { font-size: .64rem; font-weight: 700; letter-spacing: .12em;
            text-transform: uppercase; opacity: .38; margin-bottom: .3rem; }
.mod-icon { font-size: 1.4rem; margin-bottom: .2rem; display: block; }
.mod-title { font-size: .95rem; font-weight: 700; margin-bottom: .15rem; }
.mod-sub   { font-size: .75rem; opacity: .48; font-style: italic; margin-bottom: .3rem; }
.mod-desc  { font-size: .79rem; opacity: .62; line-height: 1.55; margin-bottom: .5rem; }
.tag {
    display: inline-block; font-size: .67rem; padding: 2px 7px;
    border-radius: 4px; background: rgba(61,142,240,.10);
    color: #3d8ef0; margin: 2px 2px 0 0; font-weight: 500;
}
.exp-group-title {
    font-size: .8rem; font-weight: 700; opacity: .6;
    margin: .85rem 0 .2rem; letter-spacing: .03em;
}
.page-footer {
    margin-top: 3rem; padding: 1.2rem 0 .5rem;
    border-top: 1px solid rgba(128,128,128,.14);
    text-align: center; font-size: .79rem; opacity: .48; line-height: 1.9;
}
</style>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# CONTEÚDO DA HOME
# ═══════════════════════════════════════════════════════════════════════════════
def _home():
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
<div class="hero">
  <h1>⚡ SINTONIA<br><span style="font-size:1.4rem;font-weight:700;opacity:.7">Máquinas Elétricas</span></h1>
  <p class="hero-sub">
    <span class="red-badge">RED</span>
    <strong>S</strong>istemas <strong>I</strong>nterativos para <strong>T</strong>eoria e <strong>O</strong>timização
    no <strong>N</strong>ível de <strong>I</strong>nterpretação e <strong>A</strong>prendizagem —
    material didático interativo com exploradores de parâmetros, simulações numéricas
    e circuitos equivalentes para o estudo de Máquinas Elétricas.
  </p>
  <p class="meta-line">
    🏛️ IFRN — Campus Natal-Central (CNAT) &nbsp;·&nbsp; Diretoria de Indústria &nbsp;·&nbsp;
    👤 Marcus V A Fernandes &nbsp;·&nbsp;
    ✉️ marcus.fernandes@ifrn.edu.br &nbsp;·&nbsp; v1.0 · 2026
  </p>
</div>
<div class="stat-row">
  <div class="stat-item"><div class="stat-num">7</div><div class="stat-label">Módulos</div></div>
  <div class="stat-item"><div class="stat-num">40+</div><div class="stat-label">Seções</div></div>
  <div class="stat-item"><div class="stat-num">20+</div><div class="stat-label">Exploradores</div></div>
  <div class="stat-item"><div class="stat-num">50+</div><div class="stat-label">Figuras</div></div>
  <div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">Online</div></div>
</div>
""", unsafe_allow_html=True)

    # ── Sobre ─────────────────────────────────────────────────────────────────
    st.markdown("### 📖 Sobre o SINTONIA — Máquinas Elétricas")
    st.markdown("""
**SINTONIA** é um Recurso Educacional Digital de acesso livre voltado ao estudo de
*Máquinas Elétricas e Conversão Eletromecânica de Energia*. O material está organizado
em módulos progressivos — de fundamentos da conversão eletromecânica até máquinas especiais —
com ênfase em compreensão visual, circuitos equivalentes e exploração paramétrica.

Cada módulo combina **teoria** com equações e exemplos analíticos, **figuras** geradas
numericamente e **exploradores interativos** com controles deslizantes e campos de entrada
para observar o efeito de parâmetros em tempo real, sem necessidade de reexecução.

**Possibilidades de uso:**
- 🏛️ *Máquinas Elétricas* — Engenharia de Energia / Elétrica, IFRN-CNAT
- 🏛️ *Conversão Eletromecânica de Energia* — Engenharia Elétrica, UFRN
- Demais cursos de Engenharia com disciplinas de Máquinas e Acionamentos Elétricos
""")

    # ── Índice completo ───────────────────────────────────────────────────────
    with st.expander("📋 Índice geral com acesso direto", expanded=False):
        st.caption("Clique em qualquer item para acessar diretamente o conteúdo.")
        st.markdown("---")

        st.markdown("#### 🔋 1 · Introdução à Conversão Eletromecânica de Energia")
        st.page_link(PG_INTRO, label="Ir para o módulo →", icon="🔋")
        st.markdown("""
- **1.1** Princípios básicos de eletromagnetismo — Lei de Ampère, Lei de Faraday e Lei de Lenz
- **1.2** Materiais magnéticos: curva B-H, saturação, histerese e perdas no ferro
- **1.3** Circuitos magnéticos: relutância, fluxo, força magnetomotriz (FMM)
- **1.4** Indutância, energia armazenada no campo magnético e co-energia
- **1.5** Força e torque de origem eletromagnética — princípio da energia virtual
- **1.6** Conversão eletromecânica: gerador vs. motor — fluxo de potência e perdas
- **1.7** Rendimento e balanço de potência em máquinas elétricas
- 🎛️ Explorador: circuito magnético — relutância, fluxo e FMM
- 🎛️ Explorador: curva de magnetização e ponto de operação B-H
""")
        st.markdown("---")

        st.markdown("#### 🔄 2 · Transformadores")
        st.page_link(PG_TRANSF, label="Ir para o módulo →", icon="🔄")
        st.markdown("""
- **2.1** Princípio de funcionamento e relação de transformação $a = N_1/N_2$
- **2.2** Transformador ideal: tensões, correntes e impedâncias referidas
- **2.3** Circuito equivalente completo: $R_1$, $X_1$, $R_c$, $X_m$, $R_2'$, $X_2'$
- **2.4** Circuito equivalente simplificado referido ao primário e ao secundário
- **2.5** Ensaios de curto-circuito e circuito aberto — determinação de parâmetros
- **2.6** Regulação de tensão: definição, cálculo e diagrama fasorial
- **2.7** Perdas e rendimento: perdas no cobre e no ferro, rendimento máximo
- **2.8** Transformadores trifásicos: ligações Δ-Y, Y-Y, Δ-Δ e defasagem angular
- **2.9** Autotransformadores: relação de transformação e economia de cobre
- 🎛️ Explorador: circuito equivalente — variação de carga e fator de potência
- 🎛️ Explorador: regulação de tensão e diagrama fasorial interativo
- 🎛️ Explorador: rendimento vs. carga para diferentes características
""")
        st.markdown("---")

        st.markdown("#### ⚙️ 3 · Máquinas Elétricas de Corrente Contínua")
        st.page_link(PG_CC, label="Ir para o módulo →", icon="⚙️")
        st.markdown("""
- **3.1** Construção: polo, armadura, comutador e escovas
- **3.2** FEM induzida e torque eletromagnético: $E_A = K\\phi\\omega$ e $\\tau = K\\phi I_A$
- **3.3** Gerador CC: circuitos equivalentes — separada, shunt, série e compound
- **3.4** Motor CC: partida, controle de velocidade e reversão de giro
- **3.5** Características mecânicas: conjugado vs. rotação para cada tipo de excitação
- **3.6** Regulação de velocidade e rendimento em motores CC
- **3.7** Reação de armadura e comutação — compensação e interpolos
- 🎛️ Explorador: curvas características de geradores CC
- 🎛️ Explorador: característica mecânica e ponto de operação do motor
- 🎛️ Explorador: controle de velocidade — resistência, tensão e fluxo
""")
        st.markdown("---")

        st.markdown("#### 🌀 4 · Máquinas Elétricas Polifásicas de Corrente Alternada: Indução")
        st.page_link(PG_IND, label="Ir para o módulo →", icon="🌀")
        st.markdown("""
- **4.1** Campo girante trifásico — princípio e velocidade síncrona $n_s = 120f/p$
- **4.2** Escorregamento: definição, frequência do rotor e tensão induzida no rotor
- **4.3** Circuito equivalente por fase referido ao estator
- **4.4** Potência e torque: $P_{ag}$, $P_{conv}$, $P_{saída}$ e $\\tau_{ind}$
- **4.5** Curva de torque vs. escorregamento — escorregamento de torque máximo
- **4.6** Ensaios de rotor bloqueado e à vazio — determinação de parâmetros
- **4.7** Partida de motores de indução: direta, estrela-triângulo, autotransformador
- **4.8** Controle de velocidade: variação de frequência (inversor), número de polos
- **4.9** Motor de indução com rotor bobinado — inserção de resistência no rotor
- **4.10** Gerador de indução: operação, auto-excitação com banco de capacitores
- 🎛️ Explorador: circuito equivalente — variação de escorregamento e carga
- 🎛️ Explorador: curva de torque — efeito de $R_2'$, $X_1$, $X_2'$ e $V_1$
- 🎛️ Explorador: partida e transiente de corrente com diferentes métodos
""")
        st.markdown("---")

        st.markdown("#### 🔁 5 · Máquinas Elétricas Polifásicas de Corrente Alternada: Síncrona")
        st.page_link(PG_SINC, label="Ir para o módulo →", icon="🔁")
        st.markdown("""
- **5.1** Construção: pólos salientes vs. pólos lisos, excitação e enrolamentos
- **5.2** Gerador síncrono: FEM interna $E_A$, reatância síncrona $X_s$ e resistência $R_A$
- **5.3** Circuito equivalente e diagrama fasorial — operação a plena carga
- **5.4** Curva de capacidade (de capability) e carta circular
- **5.5** Regulação de tensão e curvas de compoundagem
- **5.6** Ensaio de curto-circuito e circuito aberto — reatância síncrona não saturada
- **5.7** Operação em paralelo com a rede — sincronização e controle $P$ e $Q$
- **5.8** Motor síncrono: partida, torque e controle de fator de potência
- **5.9** Máquina com pólos salientes: reatâncias $X_d$ e $X_q$, diagrama fasorial
- **5.10** Potência elétrica e estabilidade de estado estacionário — ângulo de carga $\\delta$
- 🎛️ Explorador: diagrama fasorial interativo — variação de $I_F$, $P$ e $fp$
- 🎛️ Explorador: curva $P-\\delta$ — limite de estabilidade e torque máximo
- 🎛️ Explorador: operação em paralelo — despacho de potência ativa e reativa
""")
        st.markdown("---")

        st.markdown("#### 🔌 6 · Máquinas Elétricas de Pequeno Porte")
        st.page_link(PG_PP, label="Ir para o módulo →", icon="🔌")
        st.markdown("""
- **6.1** Motor universal: operação em CA e CC, circuito equivalente e aplicações domésticas
- **6.2** Motor de indução monofásico: campo pulsante e teoria dos dois campos girantes
- **6.3** Partida com fase auxiliar: enrolamento auxiliar, chave centrífuga e ângulo de fase
- **6.4** Motor com capacitor permanente (PSC): campo elíptico e rendimento melhorado
- **6.5** Motor com capacitor de partida e de funcionamento: dois capacitores e chaveamento
- **6.6** Motor de polo sombreado: anel de curto-circuito, campo resultante e aplicações
- 🎛️ Explorador: campos progressivo e retrógrado — torque vs. escorregamento
- 🎛️ Explorador: comparação dos métodos de partida — corrente e torque
""")
        st.markdown("---")

        st.markdown("#### 🔬 7 · Máquinas Elétricas Especiais")
        st.page_link(PG_ESP, label="Ir para o módulo →", icon="🔬")
        st.markdown("""
- **7.1** Motor de relutância chaveado (SRM): pólos salientes, conversor assimétrico e características
- **7.2** Motor de histerese: torque de histerese, curva plana e aplicações de precisão
- **7.3** Motor de passo — tipos e construção: relutância variável, ímã permanente e híbrido
- **7.4** Motor de passo — excitação e controle: sequências unipolar/bipolar, meio-passo e microstepping
- **7.5** Motor brushless DC (BLDC): ímãs permanentes no rotor, sensores Hall e ESC
- **7.6** Motor síncrono de ímãs permanentes (PMSM): controle vetorial (FOC) e SVPWM
- **7.7** Motor linear: LIM, motor síncrono linear e aplicações em transporte e CNC
- **7.8** Servo-motores e transdutores: resolvers, encoders, malha PID e aplicações
- 🎛️ Explorador: motor de passo — sequências de excitação e ângulo de passo
- 🎛️ Explorador: motor BLDC — comutação por sinal Hall e correntes de fase
""")

    # ── Cards de módulos ──────────────────────────────────────────────────────
    st.markdown("### 🗂️ Módulos")
    st.caption("Clique em **Abrir** para acessar o módulo ou use o menu lateral.")

    CARDS = [
        ("MOD 01", "🔋", "Conversão Eletromecânica", "",
         "Eletromagnetismo aplicado: circuitos magnéticos, materiais, "
         "indutância, energia no campo e princípios de força e torque. "
         "Balanço de potência e rendimento em máquinas.",
         ["B-H", "Circuito magnético", "Relutância", "Co-energia"], PG_INTRO),

        ("MOD 02", "🔄", "Transformadores", "",
         "Transformador ideal e real, circuito equivalente, ensaios de "
         "parâmetros, regulação de tensão, rendimento e ligações trifásicas. "
         "Autotransformadores e banco trifásico.",
         ["Circuito equiv.", "Regulação", "Ensaios", "Trifásico"], PG_TRANSF),

        ("MOD 03", "⚙️", "Máquinas CC", "",
         "Gerador e motor CC com excitação separada, shunt, série e compound. "
         "Curvas características, controle de velocidade e reação de armadura.",
         ["FEM", "Torque", "Controle", "Comutação"], PG_CC),

        ("MOD 04", "🌀", "Máquinas de Indução", "CA Polifásica",
         "Campo girante, escorregamento, circuito equivalente e curva "
         "de torque. Partida, controle de velocidade e operação como gerador.",
         ["Escorregamento", "Torque", "Partida", "Inversor"], PG_IND),

        ("MOD 05", "🔁", "Máquinas Síncronas", "CA Polifásica",
         "Gerador e motor síncrono: circuito equivalente, diagrama fasorial, "
         "operação em paralelo, pólos salientes e estabilidade de estado estacionário.",
         ["Reatância $X_s$", "Diagrama fasorial", "Paralelo", "Ângulo $\\delta$"], PG_SINC),

        ("MOD 06", "🔌", "Máquinas de Pequeno Porte", "",
         "Motor universal e motor de indução monofásico com seus métodos de "
         "partida: fase auxiliar, capacitor permanente, capacitor de partida e polo sombreado.",
         ["Motor universal", "Monofásico", "Capacitor", "Polo sombreado"], PG_PP),

        ("MOD 07", "🔬", "Máquinas Especiais", "",
         "Motores de relutância, histerese, passo (stepper), brushless DC (BLDC), "
         "linear e PMSM. Servo-motores, encoders e controle de posição.",
         ["Motor de passo", "BLDC", "PMSM", "SRM"], PG_ESP),
    ]

    # Linha 1: 3 cards
    cols = st.columns(3, gap="medium")
    for ci, card in enumerate(CARDS[:3]):
        _render_card(cols[ci], card)

    # Linha 2: 3 cards
    cols = st.columns(3, gap="medium")
    for ci, card in enumerate(CARDS[3:6]):
        _render_card(cols[ci], card)

    # Linha 3: 1 card centralizado (col do meio)
    cols = st.columns(3, gap="medium")
    _render_card(cols[1], CARDS[6])

    # ── Exploradores ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🎛️ Exploradores interativos")
    st.markdown(
        "Os **exploradores** são o diferencial deste RED — controles deslizantes, "
        "menus de seleção e campos de entrada com atualização em tempo real, "
        "sem necessidade de reexecução."
    )

    EXP_GROUPS = [
        ("🔋 Conversão Eletromecânica", PG_INTRO, [
            "Circuito magnético — relutância, fluxo e FMM",
            "Curva B-H e ponto de operação",
        ]),
        ("🔄 Transformadores", PG_TRANSF, [
            "Circuito equivalente — carga e $fp$",
            "Regulação de tensão e fasorial interativo",
            "Rendimento vs. carga",
        ]),
        ("⚙️ Máquinas CC", PG_CC, [
            "Curvas características de geradores",
            "Característica mecânica e ponto de operação",
            "Controle de velocidade — $R_a$, $V$ e $\\phi$",
        ]),
        ("🌀 Máquinas de Indução", PG_IND, [
            "Circuito equivalente — escorregamento e carga",
            "Curva de torque — efeito de $R_2'$, $X_1$, $X_2'$",
            "Partida e transiente de corrente",
        ]),
        ("🔁 Máquinas Síncronas", PG_SINC, [
            "Diagrama fasorial — $I_F$, $P$ e $fp$",
            "Curva $P-\\delta$ e limite de estabilidade",
            "Operação em paralelo — despacho $P$ e $Q$",
        ]),
        ("🔌 Máquinas de Pequeno Porte", PG_PP, [
            "Campos progressivo e retrógrado — torque vs. $s$",
            "Comparação dos métodos de partida",
        ]),
        ("🔬 Máquinas Especiais", PG_ESP, [
            "Motor de passo — sequências e ângulo de passo",
            "Motor BLDC — comutação por sinal Hall",
        ]),
    ]

    half = (len(EXP_GROUPS) + 1) // 2
    col_l, col_r = st.columns(2)
    for col, grupo in zip([col_l, col_r], [EXP_GROUPS[:half], EXP_GROUPS[half:]]):
        with col:
            for gtitle, pg, items in grupo:
                st.markdown(f'<p class="exp-group-title">{gtitle}</p>',
                            unsafe_allow_html=True)
                for item in items:
                    st.page_link(pg, label=item, use_container_width=False)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
<div class="page-footer">
  SINTONIA — Máquinas Elétricas &nbsp;·&nbsp; Recurso Educacional Digital de acesso livre<br>
  Autor: Marcus V A Fernandes &nbsp;·&nbsp; Diretoria de Indústria &nbsp;·&nbsp; IFRN-CNAT<br>
  marcus.fernandes@ifrn.edu.br &nbsp;·&nbsp; v1.0 · 2026
</div>
""", unsafe_allow_html=True)


def _render_card(col, card):
    num, icon, title, sub, desc, tags, pg = card
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
    sub_html  = f'<div class="mod-sub">↳ {sub}</div>' if sub else ""
    with col:
        st.markdown(f"""
<div class="mod-card">
  <div class="mod-num">{num}</div>
  <span class="mod-icon">{icon}</span>
  <div class="mod-title">{title}</div>
  {sub_html}
  <div class="mod-desc">{desc}</div>
  <div style="margin-top:.4rem">{tags_html}</div>
</div>""", unsafe_allow_html=True)
        st.page_link(pg, label=f"Abrir — {title}" + (f" · {sub}" if sub else ""),
                     use_container_width=True)


# ── Executar ──────────────────────────────────────────────────────────────────
_nav.run()
