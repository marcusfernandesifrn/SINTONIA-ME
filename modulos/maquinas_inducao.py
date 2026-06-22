"""
🌀 Máquinas de Indução Polifásica
Disciplina: Máquinas Elétricas
Curso: Engenharia de Energia
Instituição: IFRN — Campus Natal-Central (CNAT)
Autor: Marcus V A Fernandes · marcus.fernandes@ifrn.edu.br · v1.0

Fonte: PPTX-fonte do Módulo 4 — "CEEI - MEI - 01 - Conceitos" (conceitos elementares,
estrutura construtiva, campo magnético rotórico, tensão induzida e modos de operação).
Exercícios resolvidos adaptados dos notebooks SEN5.ipynb, UMANS6.ipynb e MEI-DESENHOS.ipynb.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import schemdraw
import schemdraw.elements as elm
import io
import base64
import warnings


def run():

    warnings.filterwarnings("ignore")

    # ── Paleta de cores ───────────────────────────────────────────────────────
    AZ = "#3d8ef0";  RX = "#6c47ff";  VD = "#1f9d55";  LR = "#e07b00"
    CI = "#0097a7";  TX = "#1a1f2b";  CZ = "#6b7280";  VM = "#e03e3e"

    # ── CSS responsivo ────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .fig-wrap {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    .fig-wrap > div { width: 100%; }
    @media (min-width: 769px) {
        .fig-wrap > div {
            width: var(--fw, 65%);
            max-width: var(--fw, 65%);
        }
    }
    .fig-wrap img,
    .fig-wrap [data-testid="stImage"] img {
        width: 100% !important;
        height: auto !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def show_fig(fig, width_frac=0.65):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=160, transparent=True)
        plt.close(fig)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        pct = f"{int(width_frac * 100)}%"
        st.markdown(
            f'<div class="fig-wrap">'
            f'<div style="--fw:{pct}">'
            f'<img src="data:image/png;base64,{b64}" style="width:100%;height:auto;display:block;"/>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    def show_plot(fig, key=None, height=None):
        if height:
            fig.update_layout(height=height)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=TX, size=12),
            margin=dict(l=55, r=20, t=40, b=45),
            autosize=True,
        )
        fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,.18)",
                         zeroline=True, zerolinecolor="rgba(128,128,128,.35)")
        fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,.18)",
                         zeroline=True, zerolinecolor="rgba(128,128,128,.35)")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False, "responsive": True},
                        key=key)

    def _mpl_base(figsize=(6, 4)):
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        return fig, ax

    def _mpl_base_off(figsize=(6, 4)):
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        ax.set_aspect("equal")
        ax.axis("off")
        return fig, ax

    # ════════════════════════════════════════════════════════════════════════
    # FIGURAS — matplotlib
    # ════════════════════════════════════════════════════════════════════════

    def fig_secao_transversal_mei():
        """Seção transversal idealizada da máquina de indução: estator laminado,
        enrolamentos trifásicos (aa', bb', cc') no estator e gaiola de esquilo no rotor."""
        fig, ax = _mpl_base_off((6.5, 6.5))
        ax.set_xlim(-4.5, 4.5); ax.set_ylim(-4.5, 5.0)

        R_ext   = 4.1    # raio externo do estator (jugo)
        R_int_s = 3.0    # raio interno do estator (base das ranhuras)
        R_ext_r = 2.6    # raio externo do rotor (base das ranhuras rotóricas)
        R_int_r = 1.1    # eixo (núcleo do rotor)
        R_gap_s = 2.85   # periferia interna do estator (face da ranhura)
        R_gap_r = 2.75   # periferia externa do rotor (face da ranhura)

        # Jugo do estator
        ax.add_patch(mpatches.Wedge((0,0), R_ext, 0, 360,
                                     width=R_ext - R_int_s,
                                     fc="#e8edf5", ec=TX, lw=1.6, zorder=2))
        # Núcleo do rotor
        ax.add_patch(mpatches.Circle((0,0), R_ext_r,
                                      fc="#e8edf5", ec=TX, lw=1.6, zorder=2))
        # Eixo
        ax.add_patch(mpatches.Circle((0,0), R_int_r,
                                      fc="#c8d0de", ec=TX, lw=1.2, zorder=4))
        # Entreferro (espaço em branco)
        ax.add_patch(mpatches.Wedge((0,0), R_gap_s, 0, 360,
                                     width=R_gap_s - R_gap_r,
                                     fc="white", ec="none", zorder=3))

        # Enrolamentos do estator — 3 fases, 2 polos, 4 ranhuras por fase por polo
        fase_cores  = [AZ, VD, LR]
        fase_labels = ["a", "b", "c"]
        # Posições angulares das bobinas (graus). 2P, 6 grupos, cada um com 2 condutores (ida/volta)
        # Disposição sequencial: a(0°), b(60°), c(120°), a'(180°), b'(240°), c'(300°)
        n_slots_per_group = 2
        slot_span = 10  # graus por ranhura
        group_angles = [0, 60, 120, 180, 240, 300]
        slot_r = 0.55  # raio-espessura do condutor
        slot_mid_r = (R_int_s + R_gap_s) / 2 - 0.05

        for gi, base_ang in enumerate(group_angles):
            fi  = gi % 3
            cor = fase_cores[fi]
            # positivo ou negativo?
            sinal = "+" if gi < 3 else "−"
            label_char = fase_labels[fi]
            for k in range(n_slots_per_group):
                ang_deg = base_ang + (k - 0.5) * slot_span
                ang_rad = np.radians(ang_deg)
                cx = slot_mid_r * np.cos(ang_rad)
                cy = slot_mid_r * np.sin(ang_rad)
                ax.add_patch(mpatches.Circle((cx, cy), slot_r * 0.42,
                                              fc=cor, ec=TX, lw=0.8,
                                              alpha=0.82, zorder=5))
                # símbolo de corrente (ponto = saindo, x = entrando)
                if gi < 3:
                    ax.plot(cx, cy, ".", color="white", ms=4, zorder=6)
                else:
                    ax.plot([cx-0.12, cx+0.12], [cy-0.12, cy+0.12],
                            color="white", lw=1.2, zorder=6)
                    ax.plot([cx+0.12, cx-0.12], [cy-0.12, cy+0.12],
                            color="white", lw=1.2, zorder=6)
            # label da fase
            label_ang = np.radians(base_ang)
            lx = (slot_mid_r + 0.55) * np.cos(label_ang)
            ly = (slot_mid_r + 0.55) * np.sin(label_ang)
            lbl = f"${label_char}$" if gi < 3 else f"${label_char}'$"
            ax.text(lx, ly, lbl, color=cor, fontsize=10, ha="center", va="center",
                    fontweight="bold", zorder=7)

        # Barras da gaiola de esquilo no rotor
        n_bars = 16
        bar_r = 0.22
        bar_mid_r = (R_ext_r + R_int_r) / 2 + 0.3
        for i in range(n_bars):
            ang = np.radians(360 * i / n_bars)
            bx = bar_mid_r * np.cos(ang)
            by = bar_mid_r * np.sin(ang)
            ax.add_patch(mpatches.Circle((bx, by), bar_r,
                                          fc=LR, ec=TX, lw=0.7,
                                          alpha=0.85, zorder=5))
        ax.text(0, 0, "Eixo", fontsize=7.5, color=TX,
                ha="center", va="center", zorder=6)

        # Anel de curto-circuito (indicativo)
        ring_r = bar_mid_r
        anel = mpatches.Wedge((0,0), ring_r + bar_r + 0.05, 0, 360,
                               width=2 * (bar_r + 0.05),
                               fc="none", ec=LR, lw=2.5, linestyle="--",
                               alpha=0.55, zorder=4)
        ax.add_patch(anel)

        # Eixos magnéticos das fases
        for gi, (base_ang, fi) in enumerate(zip(group_angles[:3], range(3))):
            ang_rad = np.radians(base_ang)
            ax.annotate("", xy=(3.65*np.cos(ang_rad), 3.65*np.sin(ang_rad)),
                        xytext=(0, 0),
                        arrowprops=dict(arrowstyle="-|>", color=fase_cores[fi],
                                        lw=1.2, alpha=0.5))

        ax.text(0, 4.5, "Seção Transversal — MIT Polifásica (2 Polos)",
                ha="center", fontsize=10.5, fontweight="bold", color=TX, zorder=8)
        ax.text(-4.2, -4.1, "■ Estator laminado", fontsize=8, color=TX)
        ax.text(-4.2, -4.4,
                f"■ Enrol. fase a (azul)  ■ fase b (verde)  ■ fase c (laranja)",
                fontsize=7.5, color=TX)
        ax.text(-4.2, -4.7, "■ Barras da gaiola (laranja) + anéis terminais (tracejado)",
                fontsize=7.5, color=TX)
        return fig

    def fig_rotor_bobinado():
        """Comparação esquemática rotor gaiola de esquilo vs rotor bobinado."""
        fig, axes = plt.subplots(1, 2, figsize=(9, 4.5))
        fig.patch.set_alpha(0)

        for ax in axes:
            ax.set_facecolor("none")
            ax.set_aspect("equal")
            ax.axis("off")

        # Gaiola de esquilo (esquerda)
        ax0 = axes[0]
        ax0.set_xlim(-3.5, 3.5); ax0.set_ylim(-3.5, 4.0)
        R = 2.6; R_in = 1.0; bar_r = 0.22
        ax0.add_patch(mpatches.Circle((0,0), R, fc="#e8edf5", ec=TX, lw=1.5))
        ax0.add_patch(mpatches.Circle((0,0), R_in, fc="#c8d0de", ec=TX, lw=1.2))
        n_bars = 12; bar_mid = (R + R_in)/2
        for i in range(n_bars):
            ang = np.radians(360*i/n_bars)
            ax0.add_patch(mpatches.Circle((bar_mid*np.cos(ang), bar_mid*np.sin(ang)),
                                           bar_r, fc=LR, ec=TX, lw=0.7, alpha=0.9, zorder=4))
        ax0.add_patch(mpatches.Wedge((0,0), bar_mid+bar_r+0.08, 0, 360,
                                      width=2*(bar_r+0.08), fc="none",
                                      ec=LR, lw=2.5, ls="--", alpha=0.6))
        ax0.text(0, 3.35, "Rotor Gaiola de Esquilo", ha="center",
                 fontsize=9.5, fontweight="bold", color=TX)
        ax0.text(0, -3.3,
                 "Barras de alumínio (ou cobre)\ncurto-circuitadas pelos anéis terminais",
                 ha="center", fontsize=8, color=CZ, style="italic")

        # Rotor bobinado (direita)
        ax1 = axes[1]
        ax1.set_xlim(-3.5, 3.5); ax1.set_ylim(-3.5, 4.0)
        ax1.add_patch(mpatches.Circle((0,0), R, fc="#e8edf5", ec=TX, lw=1.5))
        ax1.add_patch(mpatches.Circle((0,0), R_in, fc="#c8d0de", ec=TX, lw=1.2))
        # Enrolamentos trifásicos (simplificado)
        slot_r_pos = 0.3
        slot_mid = (R + R_in)/2
        cores_r = [AZ, VD, LR]
        for fi, base in enumerate([0, 60, 120, 180, 240, 300]):
            cor = cores_r[fi % 3]
            for k in [-0.5, 0.5]:
                ang = np.radians(base + k*10)
                cx, cy = slot_mid*np.cos(ang), slot_mid*np.sin(ang)
                ax1.add_patch(mpatches.Circle((cx,cy), slot_r_pos*0.9,
                                               fc=cor, ec=TX, lw=0.7,
                                               alpha=0.8, zorder=4))
        # Anéis coletores (esquemático)
        for ri, rc in enumerate([LR, VD, AZ]):
            r_ring = R - 0.05 - ri*0.22
            ax1.add_patch(mpatches.Wedge((0,0), r_ring, -8, 8,
                                          width=0.14, fc=rc, ec=TX, lw=0.5, zorder=5))
        ax1.text(2.85, 0, "Anéis\ncoletores", fontsize=7.5, color=TX, ha="center", va="center")
        ax1.annotate("", xy=(2.3, 0), xytext=(1.85, 0),
                     arrowprops=dict(arrowstyle="-|>", color=CZ, lw=1.0))
        ax1.text(0, 3.35, "Rotor Bobinado (Wound)", ha="center",
                 fontsize=9.5, fontweight="bold", color=TX)
        ax1.text(0, -3.3,
                 "Enrolamento trifásico — terminais acessíveis\npelos anéis coletores (resistências externas)",
                 ha="center", fontsize=8, color=CZ, style="italic")

        fig.tight_layout()
        return fig

    def fig_campo_girante():
        """Campo magnético girante: 4 instantes (0°, 60°, 90°, 180°) mostrando
        a composição vetorial de Ha, Hb, Hc → H_resultante girante."""
        fig, axes = plt.subplots(1, 4, figsize=(11, 3.2))
        fig.patch.set_alpha(0)
        instantes_deg = [0, 60, 90, 180]
        titles = ["$\\omega t = 0°$", "$\\omega t = 60°$",
                  "$\\omega t = 90°$", "$\\omega t = 180°$"]

        for ax, wt_deg, title in zip(axes, instantes_deg, titles):
            ax.set_facecolor("none")
            ax.set_xlim(-1.6, 1.6); ax.set_ylim(-1.6, 1.6)
            ax.set_aspect("equal"); ax.axis("off")

            # Círculo do estator
            ax.add_patch(mpatches.Circle((0,0), 1.4, fc="none", ec=CZ, lw=1.0, alpha=0.4))

            wt = np.radians(wt_deg)
            # Amplitudes instantâneas das três fases
            Ha_mag = np.cos(wt)
            Hb_mag = np.cos(wt - np.radians(120))
            Hc_mag = np.cos(wt - np.radians(240))

            # Direções dos eixos magnéticos das fases (estator 2P)
            axes_ang = [np.radians(90), np.radians(90-120), np.radians(90-240)]
            Hx = [Ha_mag*np.cos(a) for a in axes_ang]
            Hy = [Ha_mag*np.sin(a) for a in [axes_ang[0]]] + \
                 [Hb_mag*np.sin(axes_ang[1]), Hc_mag*np.sin(axes_ang[2])]
            Hx = [Ha_mag*np.cos(axes_ang[0]), Hb_mag*np.cos(axes_ang[1]),
                  Hc_mag*np.cos(axes_ang[2])]

            cores = [AZ, VD, LR]
            labels_f = ["$H_a$", "$H_b$", "$H_c$"]
            for i, (hx, hy, c, lbl) in enumerate(zip(Hx, Hy, cores, labels_f)):
                if abs(hx**2 + hy**2) > 0.005:
                    ax.annotate("", xy=(hx, hy), xytext=(0,0),
                                arrowprops=dict(arrowstyle="-|>", color=c, lw=1.5))
                ax.text(np.cos(axes_ang[i])*1.52, np.sin(axes_ang[i])*1.52,
                        labels_f[i], color=c, fontsize=8, ha="center", va="center")

            # Vetor resultante
            Hr_x = sum(Hx); Hr_y = sum(Hy)
            if abs(Hr_x**2 + Hr_y**2) > 0.01:
                ax.annotate("", xy=(Hr_x*0.95, Hr_y*0.95), xytext=(0,0),
                            arrowprops=dict(arrowstyle="-|>", color=TX, lw=2.2))
            ax.text(0, -1.55, title, ha="center", fontsize=8.5,
                    fontweight="bold", color=TX)

        fig.suptitle("Campo Magnético Girante — Composição Fasorial em 4 Instantes",
                     fontsize=9.5, color=TX, y=1.01)
        fig.tight_layout(pad=0.4)
        return fig

    def fig_velocidade_sincrona():
        """Relação ns = 120f/p para f=50 e 60 Hz e p=2,4,6,8,10,12 polos."""
        fig, ax = _mpl_base((6.5, 4.0))
        ax.set_facecolor("none")
        ax.set_aspect("auto")
        ax.axis("on")
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["bottom", "left"]].set_color(CZ)
        ax.tick_params(colors=CZ)

        polos = [2, 4, 6, 8, 10, 12]
        for f, cor, lbl in [(60, AZ, "60 Hz"), (50, VD, "50 Hz")]:
            ns_vals = [120*f/p for p in polos]
            ax.plot(polos, ns_vals, "o-", color=cor, lw=2.0, ms=7,
                    label=f"$f = {f}$ Hz", zorder=4)
            for p, ns in zip(polos, ns_vals):
                ax.text(p+0.12, ns+18, f"{ns:.0f}", fontsize=7.8,
                        color=cor, ha="left")

        ax.set_xlabel("Número de polos $p$", fontsize=11, color=TX)
        ax.set_ylabel("Velocidade síncrona $n_s$ (rpm)", fontsize=11, color=TX)
        ax.set_title("Velocidade Síncrona vs Número de Polos", fontsize=11.5,
                     fontweight="bold", color=TX)
        ax.legend(fontsize=9, framealpha=0.0)
        ax.set_xticks(polos)
        ax.grid(True, alpha=0.2, linestyle="--", color=CZ)
        return fig

    def fig_escorregamento_def():
        """Diagrama velocidade × escorregamento: ns, n, s definido graficamente."""
        fig, ax = _mpl_base((6, 4))
        ax.set_facecolor("none"); ax.axis("off")

        # Timeline vertical
        ax.set_xlim(-1, 5); ax.set_ylim(-0.5, 6.0)

        # Eixo de velocidade
        ax.annotate("", xy=(0.5, 5.6), xytext=(0.5, 0.2),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.5))
        ax.text(0.5, 5.8, "$n$ (rpm)", ha="center", fontsize=10, color=TX)

        # Marcadores
        ax.plot([0.5], [4.8], "o", color=AZ, ms=10, zorder=5)
        ax.plot([0.5], [3.6], "o", color=VD, ms=10, zorder=5)
        ax.plot([0.5], [0.35], "o", color=LR, ms=10, zorder=5)

        ax.text(1.0, 4.8, "$n_s = \\dfrac{120f}{p}$  (vel. síncrona)",
                fontsize=9.5, color=AZ, va="center")
        ax.text(1.0, 3.6, "$n$  (vel. do rotor, $n < n_s$)",
                fontsize=9.5, color=VD, va="center")
        ax.text(1.0, 0.35, "$n = 0$  (parado — partida)",
                fontsize=9.5, color=LR, va="center")

        # Seta de escorregamento
        ax.annotate("", xy=(0.05, 3.65), xytext=(0.05, 4.75),
                    arrowprops=dict(arrowstyle="<->", color=RX, lw=1.8))
        ax.text(-0.05, 4.2, "$n_s - n$", ha="right", fontsize=9.5, color=RX, va="center")

        # Definição do escorregamento
        ax.text(2.5, 1.9,
                "$s = \\dfrac{n_s - n}{n_s}$",
                fontsize=14, color=TX, ha="center",
                bbox=dict(fc="white", ec=CZ, lw=1.2, boxstyle="round,pad=0.35",
                          alpha=0.85))
        ax.text(2.5, 1.1,
                r"$0 \leq s \leq 1$ em operação motora",
                fontsize=9, color=CZ, ha="center", style="italic")

        ax.set_title("Definição de Escorregamento", fontsize=11,
                     fontweight="bold", color=TX, pad=8)
        return fig

    def fig_tensao_induzida_estator():
        """Tensão induzida no enrolamento do estator: forma de onda e equação."""
        fig, ax = _mpl_base((7, 3.8))
        ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(-0.5, 8.5); ax.set_ylim(-1.8, 2.8)

        t = np.linspace(0, 4*np.pi, 400)
        e = np.sin(t)
        # Normalizado: escala em radianos → 0–8.5
        tn = t * 8.5 / (4*np.pi)
        ax.plot(tn, e, color=AZ, lw=2.2, zorder=4, label="$e(t) = E_\\mathrm{max}\\sin(\\omega t)$")
        ax.axhline(0, color=CZ, lw=0.8)

        # Anotação E_max
        ax.annotate("", xy=(tn[np.argmax(e)], 1.0), xytext=(tn[np.argmax(e)], 0),
                    arrowprops=dict(arrowstyle="<->", color=VM, lw=1.6))
        ax.text(tn[np.argmax(e)] + 0.18, 0.5, "$E_\\mathrm{max}$",
                fontsize=10, color=VM)

        # Equação do valor eficaz
        eq_box = dict(fc="white", ec=CZ, lw=1.1, boxstyle="round,pad=0.4", alpha=0.88)
        ax.text(4.3, 2.35,
                "$E_{\\!A} = 4{,}44 \\cdot K_w \\cdot N_{ph} \\cdot f \\cdot \\Phi_m$",
                fontsize=11, color=TX, ha="center", bbox=eq_box)
        ax.text(4.3, 1.7,
                "$K_w$: fator de enrolamento   $N_{ph}$: espiras/fase   $\\Phi_m$: fluxo por polo",
                fontsize=8, color=CZ, ha="center")

        ax.set_title("Tensão Induzida — Enrolamento do Estator", fontsize=11,
                     fontweight="bold", color=TX, pad=8)
        ax.legend(loc="upper right", fontsize=9, framealpha=0)
        # Eixos mínimos
        ax.annotate("", xy=(8.5, -1.5), xytext=(0, -1.5),
                    arrowprops=dict(arrowstyle="-|>", color=CZ, lw=1.0))
        ax.annotate("", xy=(0, 2.6), xytext=(0, -1.5),
                    arrowprops=dict(arrowstyle="-|>", color=CZ, lw=1.0))
        ax.text(8.6, -1.5, "$t$", fontsize=9, color=CZ)
        ax.text(0.05, 2.65, "$e$", fontsize=9, color=CZ)
        return fig

    def fig_tensao_rotor_escorregamento():
        """Tensão e frequência induzidas no rotor em função do escorregamento s."""
        fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
        fig.patch.set_alpha(0)

        s_vals = np.linspace(0.001, 1.0, 300)

        # Tensão no rotor: E_r = s * E_r0
        ax0 = axes[0]; ax0.set_facecolor("none")
        ax0.spines[["top","right"]].set_visible(False)
        ax0.spines[["bottom","left"]].set_color(CZ)
        ax0.tick_params(colors=CZ)
        Er0 = 1.0  # p.u.
        ax0.plot(s_vals, s_vals * Er0, color=AZ, lw=2.2, zorder=4)
        ax0.set_xlabel("Escorregamento $s$", fontsize=10, color=TX)
        ax0.set_ylabel("$E_r = s \\cdot E_{r0}$ (p.u.)", fontsize=10, color=TX)
        ax0.set_title("Tensão Induzida no Rotor", fontsize=10, fontweight="bold", color=TX)
        ax0.text(0.5, 0.25, "$E_r = s \\cdot E_{r0}$", fontsize=12, color=AZ, ha="center",
                 transform=ax0.transAxes)
        ax0.grid(True, alpha=0.18, linestyle="--", color=CZ)
        ax0.plot([0, 1], [0, 0], "o", color=AZ, ms=6)
        ax0.annotate("$s=0\\Rightarrow E_r=0$", xy=(0,0), xytext=(0.12, 0.08),
                     fontsize=7.5, color=CZ, arrowprops=dict(arrowstyle="-", color=CZ, lw=0.7))
        ax0.annotate("$s=1\\Rightarrow E_r=E_{r0}$", xy=(1,1), xytext=(0.72, 0.82),
                     fontsize=7.5, color=CZ, arrowprops=dict(arrowstyle="-", color=CZ, lw=0.7))

        # Frequência no rotor: f_r = s * f
        ax1 = axes[1]; ax1.set_facecolor("none")
        ax1.spines[["top","right"]].set_visible(False)
        ax1.spines[["bottom","left"]].set_color(CZ)
        ax1.tick_params(colors=CZ)
        f_vals = [60, 50]
        for f0, cor, lbl in zip(f_vals, [AZ, VD], ["60 Hz", "50 Hz"]):
            ax1.plot(s_vals, s_vals * f0, color=cor, lw=2.0, label=f"$f={f0}$ Hz")
        ax1.set_xlabel("Escorregamento $s$", fontsize=10, color=TX)
        ax1.set_ylabel("$f_r = s \\cdot f$ (Hz)", fontsize=10, color=TX)
        ax1.set_title("Frequência do Rotor", fontsize=10, fontweight="bold", color=TX)
        ax1.legend(fontsize=8.5, framealpha=0)
        ax1.grid(True, alpha=0.18, linestyle="--", color=CZ)

        fig.tight_layout(pad=1.0)
        return fig

    def fig_modos_operacao():
        """Curva torque × velocidade mostrando as 3 regiões: motor, gerador, frenagem."""
        fig, ax = _mpl_base((7, 4.5))
        ax.set_facecolor("none")
        ax.set_aspect("auto"); ax.axis("on")
        ax.spines[["top","right"]].set_visible(False)
        ax.spines[["bottom","left"]].set_color(CZ)
        ax.tick_params(colors=CZ)

        # Parâmetros típicos para curva ilustrativa
        V1, R1, X1, R2, X2, Xm = 1.0, 0.05, 0.15, 0.08, 0.18, 3.0
        ns = 1800.0; ws = ns * 2*np.pi/60

        s_all = np.concatenate([np.linspace(-1.5, -0.001, 300),
                                 np.linspace(0.001, 2.0, 600)])
        n_all = ns * (1 - s_all)

        def torque_s(s):
            Z2 = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            Zt = R1 + 1j*X1 + Zeq
            I1 = V1 / Zt
            Veq = I1 * Zeq
            I2 = Veq / Z2
            Pag = 3 * abs(I2)**2 * (R2/s)
            return Pag / ws

        T_all = np.array([torque_s(s) for s in s_all])

        # Regiões de cor
        mask_motor   = (n_all >= 0) & (n_all <= ns)
        mask_gen     = n_all > ns
        mask_frein   = n_all < 0

        ax.fill_betweenx(T_all, n_all, ns, where=mask_motor,
                          color=VD, alpha=0.08, zorder=1)
        ax.fill_betweenx(T_all, n_all, ns, where=mask_gen,
                          color=AZ, alpha=0.08, zorder=1)
        ax.fill_betweenx(T_all, n_all, 0,  where=mask_frein,
                          color=VM, alpha=0.08, zorder=1)

        ax.plot(n_all, T_all, color=TX, lw=2.2, zorder=4)
        ax.axhline(0, color=CZ, lw=0.8)
        ax.axvline(ns, color=AZ, lw=1.0, ls="--", alpha=0.6)
        ax.axvline(0,  color=CZ, lw=0.8, ls="--", alpha=0.5)

        # Labels regiões
        ax.text(ns/2, max(T_all)*0.55, "MOTOR\n$0 < s < 1$",
                ha="center", fontsize=9.5, color=VD, fontweight="bold", alpha=0.8)
        ax.text(ns*1.35, max(T_all)*0.35, "GERADOR\n$s < 0$",
                ha="center", fontsize=9.5, color=AZ, fontweight="bold", alpha=0.8)
        ax.text(-ns*0.5, min(T_all)*0.55, "FRENAGEM\n$s > 1$",
                ha="center", fontsize=9.5, color=VM, fontweight="bold", alpha=0.8)

        ax.set_xlabel("Velocidade $n$ (rpm)", fontsize=11, color=TX)
        ax.set_ylabel("Torque $T$ (p.u.)", fontsize=11, color=TX)
        ax.set_title("Regiões de Operação — Máquina de Indução", fontsize=11.5,
                     fontweight="bold", color=TX)
        ax.set_xlim(-0.8*ns, 2.1*ns)

        # Anotações de s
        for s_val, x_pos, lbl in [(1.0, 0, "$s=1$"), (-0.3, ns*1.3, "$s=-0{,}3$")]:
            n_val = ns*(1-s_val)
            ax.axvline(n_val, color=CZ, lw=0.7, ls=":", alpha=0.6)
        ax.text(ns, ax.get_ylim()[0]*0.95, "$n_s$",
                ha="center", fontsize=9, color=AZ)
        ax.text(0, ax.get_ylim()[0]*0.95, "$0$",
                ha="center", fontsize=9, color=CZ)
        ax.grid(True, alpha=0.15, linestyle="--", color=CZ)
        return fig

    # ════════════════════════════════════════════════════════════════════════
    # FIGURAS — schemdraw (circuitos equivalentes)
    # ════════════════════════════════════════════════════════════════════════

    def fig_circuito_completo():
        """Circuito equivalente completo (por fase) com Rc e Xm em paralelo."""
        with schemdraw.Drawing() as d:
            d.config(unit=2)

            d.push()
            elm.Line().right(d.unit*0.25)
            X2 = elm.Inductor().right().label("$jX'_2$")
            I2 = elm.Line().right(d.unit*0.5)
            elm.Line().down(d.unit*0.375)
            elm.ResistorVar().down().label(r"$\dfrac{R'_2}{s}$", loc="bottom")
            elm.Line().down(d.unit*0.375)
            elm.Line().left(d.unit*0.5)
            elm.Line().left(d.unit*1.25).dot(open=False)
            elm.Line().left(d.unit*1.25)
            elm.Line().left()
            elm.Line().left(d.unit*0.5).dot(open=True)
            elm.Gap().up(d.unit*1.75).label(("-", "$V_1$", "+")).dot(open=True)
            V1p = elm.Line().right(d.unit*0.5)
            R1 = elm.Resistor().right().label("$R_1$")
            elm.Inductor().right().label("$jX_1$")
            elm.Line().right(d.unit*0.25).dot(open=False)
            d.pop()

            d.push()
            Ifi = elm.Line().down(d.unit*0.5).dot(open=False)
            elm.Line().right(d.unit*0.25)
            Xm_elm = elm.Inductor().down().label("$jX_m$", loc="bottom")
            elm.Line().left(d.unit*0.25).dot(open=False)
            elm.Line().down(d.unit*0.25)
            d.pop()

            d.push()
            d.move(dx=0, dy=-0.5*d.unit)
            elm.Line().left(d.unit*0.25)
            Rc_elm = elm.Resistor().down().label("$R_c$")
            elm.Line().right(d.unit*0.25)
            d.pop()

            elm.CurrentLabel(top=True, length=1, ofst=.3).at(V1p).label("$I_1$")
            elm.CurrentLabel(top=True, length=1, ofst=.3).at(I2).label(r"$I'_2$")
            elm.CurrentLabel(top=True, length=0.75, ofst=.3).at(Ifi).label(r"$I_\phi$")
            elm.CurrentLabel(top=False, length=0.75, ofst=.75).at(Rc_elm).label("$I_c$")
            elm.CurrentLabel(top=False, length=0.75, ofst=-1.25).at(Xm_elm).label("$I_m$", loc="bottom")
            d.save('/tmp/_ci_completo.png', dpi=130)

        fig, ax2 = plt.subplots(figsize=(7, 3.2))
        fig.patch.set_alpha(0); ax2.set_facecolor("none"); ax2.axis("off")
        img = plt.imread('/tmp/_ci_completo.png')
        ax2.imshow(img)
        plt.close('all')
        return fig

    def fig_circuito_ieee():
        """Circuito equivalente IEEE simplificado (Rc omitido, Xm apenas)."""
        with schemdraw.Drawing() as d:
            d.config(unit=2)

            d.push()
            elm.Line().right(d.unit*0.25)
            elm.Inductor().right().label("$jX'_2$")
            I2 = elm.Line().right(d.unit*0.5)
            elm.Line().down(d.unit*0.375)
            elm.ResistorVar().down().label(r"$\dfrac{R'_2}{s}$", loc="bottom")
            elm.Line().down(d.unit*0.375)
            elm.Line().left(d.unit*0.5)
            elm.Line().left(d.unit*1.25).dot(open=False)
            elm.Line().left(d.unit*1.25)
            elm.Line().left()
            elm.Line().left(d.unit*0.5).dot(open=True)
            elm.Gap().up(d.unit*1.75).label(("-", "$V_1$", "+")).dot(open=True)
            V1p = elm.Line().right(d.unit*0.5)
            elm.Resistor().right().label("$R_1$")
            elm.Inductor().right().label("$jX_1$")
            elm.Line().right(d.unit*0.25).dot(open=False)
            d.pop()

            d.push()
            elm.Line().down(d.unit*0.375)
            Xm_elm = elm.Inductor().down().label("$jX_m$", loc="bottom")
            elm.Line().down(d.unit*0.375)
            d.pop()

            elm.CurrentLabel(top=True, length=1, ofst=.3).at(V1p).label("$I_1$")
            elm.CurrentLabel(top=True, length=1, ofst=.3).at(I2).label(r"$I'_2$")
            elm.CurrentLabel(top=False, length=0.75, ofst=-1.25).at(Xm_elm).label("$I_m$", loc="bottom")
            d.save('/tmp/_ci_ieee.png', dpi=130)

        fig, ax2 = plt.subplots(figsize=(7, 3.0))
        fig.patch.set_alpha(0); ax2.set_facecolor("none"); ax2.axis("off")
        img = plt.imread('/tmp/_ci_ieee.png')
        ax2.imshow(img)
        plt.close('all')
        return fig

    def fig_circuito_thevenin():
        """Circuito equivalente de Thévenin: Vth, Rth, Xth em série com R'2/s e X'2."""
        with schemdraw.Drawing() as d:
            d.config(unit=2)

            d.push()
            elm.Line().right(d.unit*0.25)
            elm.Inductor().right().label("$jX'_2$")
            elm.Line().right(d.unit*0.5)
            elm.Line().down(d.unit*0.375)
            elm.ResistorVar().down().label(r"$\dfrac{R'_2}{s}$", loc="bottom")
            elm.Line().down(d.unit*0.375)
            elm.Line().left(d.unit*0.5)
            elm.Line().left(d.unit*1.25)
            elm.Line().left(d.unit*1.25)
            elm.Line().left()
            elm.Line().left(d.unit*0.5).dot(open=True)
            elm.Gap().up(d.unit*1.75).label(("-", "$V_{th}$", "+")).dot(open=True)
            V1p = elm.Line().right(d.unit*0.5)
            elm.Resistor().right().label("$R_{th}$")
            elm.Inductor().right().label("$jX_{th}$")
            elm.Line().right(d.unit*0.25)
            d.pop()

            elm.CurrentLabel(top=True, length=1, ofst=.3).at(V1p).label("$I'_2$")
            d.save('/tmp/_ci_thevenin.png', dpi=130)

        fig, ax2 = plt.subplots(figsize=(6.5, 3.0))
        fig.patch.set_alpha(0); ax2.set_facecolor("none"); ax2.axis("off")
        img = plt.imread('/tmp/_ci_thevenin.png')
        ax2.imshow(img)
        plt.close('all')
        return fig

    def fig_fluxo_potencia_motor():
        """Diagrama de fluxo de potência — motor de indução."""
        fig, ax = _mpl_base((8, 3.8))
        ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(-0.5, 9.5); ax.set_ylim(-1.0, 3.0)

        # Caixas e setas
        blocos = [
            (0.5, 1.5, "$P_{in}$\n(elétrica\nno terminal)", AZ),
            (2.8, 1.5, "$P_{cu,1}$\n(cobre\nestator)", VM),
            (5.1, 1.5, "$P_{fe}$\n(ferro /\nnúcleo)", LR),
            (6.9, 1.5, "$P_{ag}$\n(gap de\nar)", CZ),
            (8.7, 1.5, "$P_{mec}$\n(mecânica\nbrutaem)", VD),
        ]

        # Setas horizontais principais
        arrow_kw = dict(arrowstyle="-|>", color=TX, lw=1.8)
        xs = [1.4, 3.7, 5.85, 7.65]
        for x in xs:
            ax.annotate("", xy=(x+0.25, 1.5), xytext=(x, 1.5),
                        arrowprops=arrow_kw)

        # Setas de perdas para baixo
        perdas = [
            (2.0,  "$P_{cu,1}$\nCopper estator", VM),
            (4.4,  "$P_{fe}$\nNúcleo", LR),
            (7.8,  "$P_{cu,2}$\nCopper rotor", VM),
            (9.2,  "$P_{rot}$\nAtrito e\nventilação", LR),
        ]

        # Redesenhando de forma mais clara
        ax.cla(); ax.axis("off")
        ax.set_xlim(-0.3, 11.5); ax.set_ylim(-2.0, 3.0)

        # Fluxo principal (linha horizontal)
        etapas_x = [0, 2.0, 4.0, 6.0, 8.2, 10.5]
        labels_fluxo = ["$P_{in}$", "", "$P_{ag}$", "", "$P_{mec}$", "$P_{out}$"]
        cores_fluxo  = [AZ, AZ, CI, CI, VD, VD]

        for i in range(len(etapas_x)-1):
            ax.annotate("", xy=(etapas_x[i+1]-0.05, 0.5),
                        xytext=(etapas_x[i]+0.05, 0.5),
                        arrowprops=dict(arrowstyle="-|>", color=TX, lw=2.0))

        # Labels no fluxo
        for x, lbl, cor in zip(etapas_x, labels_fluxo, cores_fluxo):
            if lbl:
                ax.text(x, 0.5, lbl, ha="center", va="bottom", fontsize=9.5,
                        color=cor, fontweight="bold")

        # Perdas (setas para baixo)
        perdas_pos = [
            (1.0,  "$P_{cu,1}$", VM,  "Cobre\nEstator"),
            (3.0,  "$P_{fe}$",   LR,  "Ferro /\nNúcleo"),
            (7.1,  "$P_{cu,2}$", VM,  "Cobre\nRotor"),
            (9.35, "$P_{rot}$",  LR,  "Atrito e\nVentilação"),
        ]
        for xp, lbl, cor, descr in perdas_pos:
            ax.annotate("", xy=(xp, -0.8), xytext=(xp, 0.45),
                        arrowprops=dict(arrowstyle="-|>", color=cor, lw=1.6))
            ax.text(xp, -1.1, lbl, ha="center", fontsize=9, color=cor, fontweight="bold")
            ax.text(xp, -1.55, descr, ha="center", fontsize=7.5, color=CZ, style="italic")

        # Linha divisória mec/ele
        ax.axvline(5.1, color=CZ, lw=0.8, ls=":", alpha=0.5)
        ax.text(5.1, 2.5, "↑ Elétrico    Mecânico ↑", ha="center",
                fontsize=8, color=CZ, style="italic")

        ax.set_title("Fluxo de Potência — Motor de Indução", fontsize=11.5,
                     fontweight="bold", color=TX, pad=10)
        return fig

    def fig_fluxo_potencia_gerador():
        """Diagrama de fluxo de potência — gerador de indução."""
        fig, ax = _mpl_base((8.5, 3.5))
        ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(-0.5, 11.8); ax.set_ylim(-2.0, 3.0)

        etapas_x = [0, 2.0, 4.2, 6.2, 8.4, 10.7]

        for i in range(len(etapas_x)-1):
            ax.annotate("", xy=(etapas_x[i+1]-0.05, 0.5),
                        xytext=(etapas_x[i]+0.05, 0.5),
                        arrowprops=dict(arrowstyle="-|>", color=TX, lw=2.0))

        labels_fl = ["$P_{in}$\n(mecânica)", "", "$P_{ag}$", "", "", "$P_{out}$\n(elétrica)"]
        cores_fl  = [VD, VD, CI, CI, AZ, AZ]
        for x, lbl, cor in zip(etapas_x, labels_fl, cores_fl):
            if lbl:
                ax.text(x, 0.5, lbl, ha="center", va="bottom", fontsize=9,
                        color=cor, fontweight="bold")

        perdas_pos = [
            (1.0,  "$P_{rot}$",  LR, "Atrito e\nVentilação"),
            (3.1,  "$P_{fe}$",   LR, "Ferro /\nNúcleo"),
            (7.3,  "$P_{cu,2}$", VM, "Cobre\nRotor"),
            (9.55, "$P_{cu,1}$", VM, "Cobre\nEstator"),
        ]
        for xp, lbl, cor, descr in perdas_pos:
            ax.annotate("", xy=(xp, -0.8), xytext=(xp, 0.45),
                        arrowprops=dict(arrowstyle="-|>", color=cor, lw=1.6))
            ax.text(xp, -1.1, lbl, ha="center", fontsize=9, color=cor, fontweight="bold")
            ax.text(xp, -1.55, descr, ha="center", fontsize=7.5, color=CZ, style="italic")

        ax.axvline(5.3, color=CZ, lw=0.8, ls=":", alpha=0.5)
        ax.text(5.3, 2.5, "← Mecânico    Elétrico →", ha="center",
                fontsize=8, color=CZ, style="italic")

        ax.set_title("Fluxo de Potência — Gerador de Indução", fontsize=11.5,
                     fontweight="bold", color=TX, pad=10)
        return fig

    def fig_curva_torque_velocidade():
        """Curva T × n completa com pontos notáveis: T_part, T_max, T_nom."""
        fig, ax = _mpl_base((7, 4.5))
        ax.set_facecolor("none"); ax.set_aspect("auto"); ax.axis("on")
        ax.spines[["top","right"]].set_visible(False)
        ax.spines[["bottom","left"]].set_color(CZ)
        ax.tick_params(colors=CZ)

        V1, R1, X1, R2, X2, Xm = 220/np.sqrt(3), 0.5, 1.0, 0.4, 1.0, 50.0
        ns = 1800.0; ws = ns * 2*np.pi/60

        s_range = np.concatenate([np.linspace(0.001, 1.0, 600)])
        n_range = ns * (1 - s_range)

        def T_s(s):
            Z2 = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            Zt = R1 + 1j*X1 + Zeq
            I2 = (V1/Zt) * Zeq / Z2
            return 3 * abs(I2)**2 * (R2/s) / ws

        T_vals = np.array([T_s(s) for s in s_range])

        ax.plot(n_range, T_vals, color=AZ, lw=2.4, zorder=4)

        # Pontos notáveis
        idx_max = np.argmax(T_vals)
        T_max = T_vals[idx_max]; n_max = n_range[idx_max]
        T_part = T_s(1.0); n_part = 0.0
        idx_nom = np.argmin(np.abs(s_range - 0.05))
        T_nom = T_vals[idx_nom]; n_nom = n_range[idx_nom]

        for x, y, lbl, mk, cor in [
            (n_part, T_part, "$T_{part}$", "s", VM),
            (n_max,  T_max,  "$T_{max}$",  "^", LR),
            (n_nom,  T_nom,  "$T_{nom}$",  "o", VD),
            (ns,     0,      "$n_s$",       "D", AZ),
        ]:
            ax.plot(x, y, mk, color=cor, ms=8, zorder=6)
            ax.annotate(lbl, xy=(x,y), xytext=(x+30, y+5),
                        fontsize=9, color=cor,
                        arrowprops=dict(arrowstyle="-", color=cor, lw=0.8))

        ax.axvline(ns, color=AZ, lw=1.0, ls="--", alpha=0.5)
        ax.axhline(0,  color=CZ, lw=0.7)

        ax.set_xlabel("Velocidade $n$ (rpm)", fontsize=11, color=TX)
        ax.set_ylabel("Torque $T$ (N·m)", fontsize=11, color=TX)
        ax.set_title("Curva Característica Torque × Velocidade", fontsize=11.5,
                     fontweight="bold", color=TX)
        ax.grid(True, alpha=0.18, linestyle="--", color=CZ)
        return fig

    def fig_curva_torque_R2():
        """Família de curvas T × n para diferentes valores de R'2 (rotor bobinado)."""
        fig, ax = _mpl_base((7, 4.5))
        ax.set_facecolor("none"); ax.set_aspect("auto"); ax.axis("on")
        ax.spines[["top","right"]].set_visible(False)
        ax.spines[["bottom","left"]].set_color(CZ)
        ax.tick_params(colors=CZ)

        V1, R1, X1, X2, Xm = 220/np.sqrt(3), 0.5, 1.0, 1.0, 50.0
        ns = 1800.0; ws = ns * 2*np.pi/60
        R2_vals = [0.2, 0.4, 0.6, 1.0, 1.5]
        cores = [AZ, VD, LR, RX, CI]
        ls_list = ["-", "--", "-.", ":", (0,(3,1,1,1))]

        s_range = np.linspace(0.001, 1.0, 500)
        n_range = ns * (1 - s_range)

        for R2, cor, ls in zip(R2_vals, cores, ls_list):
            def T_s(s, R2=R2):
                Z2 = R2/s + 1j*X2
                Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
                Zt = R1 + 1j*X1 + Zeq
                I2 = (V1/Zt) * Zeq / Z2
                return 3 * abs(I2)**2 * (R2/s) / ws
            T_vals = np.array([T_s(s) for s in s_range])
            ax.plot(n_range, T_vals, color=cor, lw=1.8, ls=ls,
                    label=f"$R'_2 = {R2}\\,\\Omega$", zorder=4)

        ax.axvline(ns, color=AZ, lw=1.0, ls="--", alpha=0.5)
        ax.axhline(0,  color=CZ, lw=0.7)
        ax.set_xlabel("Velocidade $n$ (rpm)", fontsize=11, color=TX)
        ax.set_ylabel("Torque $T$ (N·m)", fontsize=11, color=TX)
        ax.set_title("Efeito de $R'_2$ na Curva $T \\times n$ (Rotor Bobinado)",
                     fontsize=11, fontweight="bold", color=TX)
        ax.legend(fontsize=8.5, framealpha=0.0, ncol=2)
        ax.grid(True, alpha=0.18, linestyle="--", color=CZ)
        return fig

    def fig_gaiola_dupla():
        """Curvas de torque × velocidade: gaiola simples, gaiola externa, gaiola interna e dupla."""
        fig, ax = _mpl_base((7, 4.5))
        ax.set_facecolor("none"); ax.set_aspect("auto"); ax.axis("on")
        ax.spines[["top","right"]].set_visible(False)
        ax.spines[["bottom","left"]].set_color(CZ)
        ax.tick_params(colors=CZ)

        V1, R1, X1, Xm = 220/np.sqrt(3), 0.5, 1.0, 50.0
        ns = 1800.0; ws = ns * 2*np.pi/60
        s_range = np.linspace(0.001, 1.0, 500)
        n_range = ns * (1 - s_range)

        def T_single(s, R2, X2):
            Z2 = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I2 = (V1/(R1 + 1j*X1 + Zeq)) * Zeq / Z2
            return 3 * abs(I2)**2 * (R2/s) / ws

        def T_double(s):
            # Gaiola externa: alta R, baixa X
            R2o, X2o = 4.0, 1.5
            # Gaiola interna: baixa R, alta X
            R2i, X2i = 0.5, 4.5
            Z_ext = R2o/s + 1j*X2o
            Z_int = R2i/s + 1j*X2i
            Z2_par = Z_ext * Z_int / (Z_ext + Z_int)
            Zeq = (1j*Xm * Z2_par) / (1j*Xm + Z2_par)
            I_total = V1 / (R1 + 1j*X1 + Zeq)
            Veq = I_total * Zeq
            I_ext = Veq / Z_ext; I_int = Veq / Z_int
            Pag_ext = 3 * abs(I_ext)**2 * (R2o/s)
            Pag_int = 3 * abs(I_int)**2 * (R2i/s)
            return (Pag_ext + Pag_int) / ws

        T_ext = np.array([T_single(s, 4.0, 1.5) for s in s_range])
        T_int = np.array([T_single(s, 0.5, 4.5) for s in s_range])
        T_dup = np.array([T_double(s) for s in s_range])
        T_sim = np.array([T_single(s, 0.4, 1.0) for s in s_range])

        ax.plot(n_range, T_sim, color=CZ, lw=1.5, ls="--",
                label="Gaiola simples (referência)")
        ax.plot(n_range, T_ext, color=VM,  lw=1.5, ls="-.",
                label="Gaiola externa ($R$ alta, $X$ baixa)")
        ax.plot(n_range, T_int, color=AZ,  lw=1.5, ls=":",
                label="Gaiola interna ($R$ baixa, $X$ alta)")
        ax.plot(n_range, T_dup, color=VD,  lw=2.4, ls="-",
                label="Gaiola dupla (resultante)", zorder=5)

        ax.axvline(ns, color=AZ, lw=1.0, ls="--", alpha=0.5)
        ax.axhline(0,  color=CZ, lw=0.7)
        ax.set_xlabel("Velocidade $n$ (rpm)", fontsize=11, color=TX)
        ax.set_ylabel("Torque $T$ (N·m)", fontsize=11, color=TX)
        ax.set_title("Motor com Gaiola de Esquilo Dupla — Curvas de Torque",
                     fontsize=11, fontweight="bold", color=TX)
        ax.legend(fontsize=8.5, framealpha=0.0)
        ax.grid(True, alpha=0.18, linestyle="--", color=CZ)
        return fig

    # ════════════════════════════════════════════════════════════════════════
    # EXPLORADORES PLOTLY
    # ════════════════════════════════════════════════════════════════════════

    def _calc_torque_plotly(V1, R1, X1, R2, X2, Xm, ns, s_arr):
        """Calcula curva de torque por array de s usando circuito IEEE."""
        ws = ns * 2*np.pi/60
        T_out = []
        for s in s_arr:
            s_safe = s if abs(s) > 1e-4 else 1e-4
            Z2 = R2/s_safe + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            Zt  = R1 + 1j*X1 + Zeq
            I1  = V1 / Zt
            I2  = (I1 * Zeq) / Z2
            Pag = 3 * abs(I2)**2 * (R2/s_safe)
            T_out.append(Pag / ws)
        return np.array(T_out)

    def exp_torque_velocidade():
        """Explorador interativo: curva T × n com parâmetros ajustáveis."""
        st.markdown("#### 🎛️ Explorador — Curva Torque × Velocidade")

        col1, col2 = st.columns(2)
        with col1:
            V_line = st.slider("Tensão de linha $V_L$ (V)", 100, 600, 220, 10,
                               key="ei_Vline")
            R1  = st.slider("$R_1$ (Ω)", 0.05, 2.0, 0.5, 0.05, key="ei_R1")
            X1  = st.slider("$X_1$ (Ω)", 0.1,  3.0, 1.0, 0.05, key="ei_X1")
        with col2:
            R2  = st.slider("$R'_2$ (Ω)", 0.05, 3.0, 0.4, 0.05, key="ei_R2")
            X2  = st.slider("$X'_2$ (Ω)", 0.1,  3.0, 1.0, 0.05, key="ei_X2")
            Xm  = st.slider("$X_m$ (Ω)",  5.0, 100.0, 50.0, 1.0,  key="ei_Xm")

        col3, col4 = st.columns(2)
        with col3:
            f    = st.selectbox("Frequência (Hz)", [50, 60], index=1, key="ei_f")
            p    = st.selectbox("Número de polos", [2, 4, 6, 8], index=1, key="ei_p")
        with col4:
            mostrar_reg = st.checkbox("Mostrar regiões de operação", True, key="ei_reg")
            mostrar_pts = st.checkbox("Mostrar pontos notáveis",     True, key="ei_pts")

        V1 = V_line / np.sqrt(3)
        ns = 120*f/p

        s_all  = np.concatenate([np.linspace(-0.8, -1e-4, 200),
                                  np.linspace(1e-4, 2.0,  600)])
        n_all  = ns * (1 - s_all)
        T_all  = _calc_torque_plotly(V1, R1, X1, R2, X2, Xm, ns, s_all)

        fig = go.Figure()

        if mostrar_reg:
            for cond, col, name in [
                ((n_all >= 0) & (n_all <= ns), "rgba(31,157,85,0.06)", "Região Motor"),
                (n_all > ns,                    "rgba(61,142,240,0.06)", "Região Gerador"),
                (n_all < 0,                     "rgba(224,62,62,0.06)", "Região Frenagem"),
            ]:
                fig.add_trace(go.Scatter(
                    x=n_all[cond], y=T_all[cond],
                    fill="tozeroy", fillcolor=col,
                    line=dict(width=0), name=name, showlegend=True,
                ))

        fig.add_trace(go.Scatter(
            x=n_all, y=T_all, mode="lines",
            line=dict(color=AZ, width=2.5), name="Curva T(n)",
        ))

        if mostrar_pts:
            # Motor region only
            mask_m = (n_all >= 0) & (n_all <= ns)
            if mask_m.any():
                T_m = T_all[mask_m]; n_m = n_all[mask_m]
                idx_max = np.argmax(T_m)
                s_motor = np.linspace(1e-4, 1.0, 100)
                T_part = _calc_torque_plotly(V1,R1,X1,R2,X2,Xm,ns,[1.0])[0]
                fig.add_trace(go.Scatter(
                    x=[0, n_m[idx_max], ns],
                    y=[T_part, T_m[idx_max], 0],
                    mode="markers+text",
                    marker=dict(color=[VM, LR, AZ], size=10, symbol=["square","triangle-up","diamond"]),
                    text=["T_part", "T_max", "ns"],
                    textposition="top center",
                    name="Pontos notáveis",
                ))

        fig.add_hline(y=0, line=dict(color=CZ, width=0.8))
        fig.add_vline(x=ns, line=dict(color=AZ, width=1.0, dash="dash"))
        fig.update_layout(
            xaxis_title="Velocidade n (rpm)",
            yaxis_title="Torque T (N·m)",
            title=f"T × n — ns = {ns:.0f} rpm  |  V₁ = {V1:.1f} V",
            legend=dict(orientation="h", y=-0.2),
        )
        show_plot(fig, key="exp_tv", height=400)

    def exp_circuito_equivalente():
        """Explorador: cálculo de grandezas do circuito equivalente para dado s."""
        st.markdown("#### 🎛️ Explorador — Circuito Equivalente (Ponto de Operação)")

        col1, col2 = st.columns(2)
        with col1:
            V_line = st.number_input("Tensão de linha $V_L$ (V)", 100.0, 15000.0, 460.0, 10.0,
                                     key="eice_V")
            f   = st.selectbox("Frequência (Hz)", [50, 60], index=1, key="eice_f")
            p   = st.selectbox("Polos", [2, 4, 6, 8], index=1, key="eice_p")
            s   = st.slider("Escorregamento $s$", 0.001, 0.99, 0.05, 0.001, key="eice_s",
                            format="%.3f")
        with col2:
            R1  = st.number_input("$R_1$ (Ω)", 0.01, 10.0, 0.5, 0.01, format="%.3f", key="eice_R1")
            X1  = st.number_input("$X_1$ (Ω)", 0.01, 20.0, 1.0, 0.01, format="%.3f", key="eice_X1")
            R2  = st.number_input("$R'_2$ (Ω)",0.01, 10.0, 0.4, 0.01, format="%.3f", key="eice_R2")
            X2  = st.number_input("$X'_2$ (Ω)",0.01, 20.0, 1.0, 0.01, format="%.3f", key="eice_X2")
            Xm  = st.number_input("$X_m$ (Ω)", 1.0, 500.0, 50.0, 1.0, format="%.1f", key="eice_Xm")

        V1 = V_line / np.sqrt(3)
        ns = 120*f/p; ws = ns * 2*np.pi/60
        n  = ns * (1 - s)

        Z2  = R2/s + 1j*X2
        Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
        Zt  = R1 + 1j*X1 + Zeq
        I1  = V1 / Zt
        Veq = I1 * Zeq
        I2  = Veq / Z2
        Im  = Veq / (1j*Xm)

        Pin   = 3 * V1 * abs(I1) * np.cos(np.angle(I1))
        Pcu1  = 3 * abs(I1)**2 * R1
        Pag   = 3 * abs(I2)**2 * (R2/s)
        Pcu2  = s * Pag
        Pmec  = (1-s) * Pag
        T_em  = Pag / ws
        fp    = np.cos(np.angle(I1))

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("$I_1$ (A)", f"{abs(I1):.3f}")
        c1.metric("$I'_2$ (A)", f"{abs(I2):.3f}")
        c2.metric("$P_{in}$ (W)", f"{Pin:.1f}")
        c2.metric("$P_{ag}$ (W)", f"{Pag:.1f}")
        c3.metric("$P_{mec}$ (W)", f"{Pmec:.1f}")
        c3.metric("$P_{cu,2}$ (W)", f"{Pcu2:.1f}")
        c4.metric("$T_{em}$ (N·m)", f"{T_em:.3f}")
        c4.metric("$fp$", f"{fp:.4f}")

        st.markdown(f"**Velocidade do rotor:** $n = {n:.1f}$ rpm  |  "
                    f"**Vel. síncrona:** $n_s = {ns:.0f}$ rpm  |  "
                    f"**Escorregamento:** $s = {s:.3f}$")

        # Gráfico de barras de potências
        fig_bar = go.Figure()
        nomes = ["$P_{in}$", "$P_{cu,1}$", "$P_{ag}$", "$P_{cu,2}$", "$P_{mec}$"]
        vals  = [Pin, Pcu1, Pag, Pcu2, Pmec]
        cores_bar = [AZ, VM, CI, VM, VD]
        fig_bar.add_trace(go.Bar(x=nomes, y=vals,
                                  marker_color=cores_bar, showlegend=False))
        fig_bar.update_layout(title="Distribuição de Potências (W)",
                               yaxis_title="Potência (W)", height=300)
        show_plot(fig_bar, key="exp_ce_bar", height=300)

    def exp_escorregamento_tensao():
        """Explorador: efeito de variação de tensão na curva T × n."""
        st.markdown("#### 🎛️ Explorador — Efeito da Tensão na Curva T × n")

        col1, col2 = st.columns([1, 2])
        with col1:
            f  = st.selectbox("Frequência (Hz)", [50, 60], index=1, key="eetv_f")
            p  = st.selectbox("Polos", [2, 4, 6, 8], index=1, key="eetv_p")
            R1 = st.slider("$R_1$ (Ω)", 0.05, 2.0, 0.5, 0.05, key="eetv_R1")
            R2 = st.slider("$R'_2$ (Ω)",0.05, 2.0, 0.4, 0.05, key="eetv_R2")
            X1 = st.slider("$X_1$ (Ω)", 0.1,  3.0, 1.0, 0.1,  key="eetv_X1")
            X2 = st.slider("$X'_2$ (Ω)",0.1,  3.0, 1.0, 0.1,  key="eetv_X2")
            Xm = st.slider("$X_m$ (Ω)", 5.0, 100.0,50.0,1.0,  key="eetv_Xm")

        ns = 120*f/p
        s_range = np.linspace(0.001, 1.0, 500)
        n_range = ns * (1 - s_range)

        V_list = [0.7, 0.85, 1.0, 1.1]
        cores_v = [VM, LR, AZ, VD]
        V_nom = 220 / np.sqrt(3)

        fig = go.Figure()
        for frac, cor in zip(V_list, cores_v):
            V1 = frac * V_nom
            T  = _calc_torque_plotly(V1, R1, X1, R2, X2, Xm, ns, s_range)
            fig.add_trace(go.Scatter(
                x=n_range, y=T, mode="lines",
                line=dict(color=cor, width=2.0),
                name=f"{frac*100:.0f}% $V_{{nom}}$  ({V1*np.sqrt(3):.0f} V)",
            ))

        fig.add_vline(x=ns, line=dict(color=AZ, dash="dash", width=1.0))
        fig.update_layout(
            xaxis_title="Velocidade n (rpm)",
            yaxis_title="Torque T (N·m)",
            title="Efeito da Tensão Terminal na Curva T × n  (T ∝ V²)",
            legend=dict(orientation="h", y=-0.22),
        )
        show_plot(fig, key="exp_etv", height=400)

    def exp_partida_autotransformador():
        """Explorador: métodos de partida — corrente e torque normalizados."""
        st.markdown("#### 🎛️ Explorador — Métodos de Partida")

        col1, col2 = st.columns(2)
        with col1:
            Ipart_fn = st.slider("Corrente de partida direta ($I_{part}/I_{nom}$)",
                                  3.0, 8.0, 6.0, 0.5, key="ep_Ifn")
            Tpart_fn = st.slider("Torque de partida direta ($T_{part}/T_{nom}$)",
                                  0.5, 2.5, 1.5, 0.1, key="ep_Tfn")
        with col2:
            alfa = st.slider("Relação do autotransformador $\\alpha$ (0–1)",
                             0.40, 0.95, 0.65, 0.05, key="ep_alfa")
            k_yd = 3.0  # Relação Y/Δ fixo

        # Cálculos por método
        metodos = {
            "Direta (DOL)":            (Ipart_fn,             Tpart_fn),
            "Y/Δ":                     (Ipart_fn/k_yd,         Tpart_fn/k_yd),
            f"Autotransf. α={alfa:.2f}": (alfa**2 * Ipart_fn, alfa**2 * Tpart_fn),
            "Resistor série (50%)":    (Ipart_fn*0.5,          Tpart_fn*0.25),
        }

        nomes = list(metodos.keys())
        Is    = [v[0] for v in metodos.values()]
        Ts    = [v[1] for v in metodos.values()]

        fig = make_subplots(rows=1, cols=2,
                             subplot_titles=["Corrente de Partida (× $I_{nom}$)",
                                             "Torque de Partida (× $T_{nom}$)"])
        fig.add_trace(go.Bar(x=nomes, y=Is, marker_color=[VM, LR, AZ, VD],
                              name="Corrente", showlegend=False), row=1, col=1)
        fig.add_trace(go.Bar(x=nomes, y=Ts, marker_color=[VM, LR, AZ, VD],
                              name="Torque", showlegend=False), row=1, col=2)
        fig.add_hline(y=1.0, line=dict(color=CZ, dash="dash"), row=1, col=1)
        fig.add_hline(y=1.0, line=dict(color=CZ, dash="dash"), row=1, col=2)
        fig.update_layout(height=380, title="Comparação dos Métodos de Partida")
        show_plot(fig, key="exp_part", height=380)

    def exp_eficiencia():
        """Explorador: eficiência e rendimento em função da carga."""
        st.markdown("#### 🎛️ Explorador — Eficiência × Carga")

        col1, col2 = st.columns(2)
        with col1:
            V_line  = st.number_input("$V_L$ (V)", 100.0, 15000.0, 460.0, key="eef_V")
            P_nom   = st.number_input("$P_{nom}$ (kW)", 1.0, 2000.0, 75.0, key="eef_Pnom")
            f       = st.selectbox("Frequência (Hz)", [50,60], index=1, key="eef_f")
            p       = st.selectbox("Polos", [2,4,6,8], index=1, key="eef_p")
        with col2:
            R1 = st.number_input("$R_1$ (Ω)", 0.001, 5.0, 0.07, 0.001, format="%.3f", key="eef_R1")
            R2 = st.number_input("$R'_2$ (Ω)",0.001, 5.0, 0.152,0.001, format="%.3f", key="eef_R2")
            X1 = st.number_input("$X_1$ (Ω)", 0.01, 10.0, 0.743,0.001, format="%.3f", key="eef_X1")
            X2 = st.number_input("$X'_2$ (Ω)",0.01, 10.0, 0.764,0.001, format="%.3f", key="eef_X2")
            Xm = st.number_input("$X_m$ (Ω)", 1.0, 500.0, 40.1, 0.1,  format="%.1f", key="eef_Xm")

        Prot   = st.slider("Perdas rotacionais $P_{rot}$ (W)", 0, 5000, 390, 10, key="eef_Prot")
        P_nucl = st.slider("Perdas no núcleo $P_{fe}$ (W)",   0, 5000, 325, 10, key="eef_Pfe")

        V1 = V_line / np.sqrt(3)
        ns = 120*f/p; ws = ns * 2*np.pi/60
        P_nom_W = P_nom * 1000

        s_arr = np.linspace(0.002, 0.50, 400)
        n_arr = ns * (1 - s_arr)
        efic_arr = []; Pout_arr = []; Tsh_arr = []

        for s in s_arr:
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I1  = V1 / (R1 + 1j*X1 + Zeq)
            I2  = (I1 * Zeq) / Z2
            Pag = 3 * abs(I2)**2 * (R2/s)
            Pin = 3 * V1 * abs(I1) * np.cos(np.angle(I1)) + P_nucl
            Pcu1= 3 * abs(I1)**2 * R1
            Pout= Pag*(1-s) - Prot
            Tsh = Pout / (ns*(1-s)*2*np.pi/60) if (ns*(1-s)) > 1 else 0
            eta = Pout/Pin * 100 if Pin > 0 else 0
            efic_arr.append(max(0, eta)); Pout_arr.append(max(0, Pout)); Tsh_arr.append(Tsh)

        fig = make_subplots(rows=1, cols=2,
                             subplot_titles=["Eficiência × Velocidade",
                                             "Conjugado e Potência × Velocidade"])
        fig.add_trace(go.Scatter(x=n_arr, y=efic_arr, mode="lines",
                                  line=dict(color=AZ, width=2.2), name="η (%)"),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=n_arr, y=Pout_arr, mode="lines",
                                  line=dict(color=VD, width=2.0), name="P_out (W)"),
                      row=1, col=2)
        fig.add_trace(go.Scatter(x=n_arr, y=Tsh_arr, mode="lines",
                                  line=dict(color=LR, width=2.0, dash="dash"),
                                  name="T_eixo (N·m)"),
                      row=1, col=2)
        fig.update_layout(height=380, legend=dict(orientation="h", y=-0.22))
        show_plot(fig, key="exp_ef", height=380)

    # ════════════════════════════════════════════════════════════════════════
    # LAYOUT PRINCIPAL — SEÇÕES
    # ════════════════════════════════════════════════════════════════════════

    st.markdown("# 🌀 Máquinas de Indução Polifásica")
    st.markdown(
        "_Módulo 4 — Campo magnético girante, escorregamento, circuito equivalente, "
        "curva de torque, fluxo de potência e modos de operação._"
    )
    st.markdown("---")

    # Sumário de navegação
    with st.expander("📋 Sumário do Módulo", expanded=False):
        st.markdown("""
**Seções de teoria**
1. Conceitos Elementares e Aplicações
2. Estrutura Construtiva — Estator e Rotor
3. Campo Magnético Girante
4. Escorregamento
5. Tensão Induzida — Estator e Rotor
6. Circuito Equivalente (por fase)
7. Fluxo de Potência e Balanço de Energia
8. Torque Eletromagnético
9. Modos de Operação: Motor / Gerador / Frenagem
10. Curva Característica T × n
11. Métodos de Partida
12. Gaiola de Esquilo Dupla

**Exploradores interativos**
- 🎛️ Curva Torque × Velocidade
- 🎛️ Circuito Equivalente — Ponto de Operação
- 🎛️ Efeito da Tensão na Curva T × n
- 🎛️ Métodos de Partida
- 🎛️ Eficiência × Carga
""")

    # ── Seção 1 ───────────────────────────────────────────────────────────────
    st.markdown("## 1 · Conceitos Elementares e Aplicações")
    st.markdown("""
A **máquina de indução polifásica** (MIT) é a mais empregada na indústria, tanto pelo baixo
custo quanto pela robustez e simplicidade construtiva. Ao contrário das máquinas CC, em que o
campo e a armadura são alimentados separadamente, na MIT *ambos* os enrolamentos — estator e
rotor — operam com corrente alternada.

O aspecto central que dá nome à máquina é o **princípio da indução**: a tensão no rotor é
induzida pelo campo girante do estator, exatamente como no secundário de um transformador
(por isso, Chapman a chama de "transformador com entreferro e secundário girante").

**Aplicações típicas por faixa de potência**

| Faixa | Exemplos de uso |
|---|---|
| Grande porte (> 100 kW) | Bombas, ventiladores industriais, compressores, moinhos, papel e celulose |
| Médio porte (1–100 kW) | Acionamentos de máquinas CNC, transportadores, bombas hidráulicas |
| Pequeno porte (< 1 kW) | Liquidificadores, espremedores de fruta, máquinas de lavar, refrigeradores |

A operação como **gerador** é também possível — com escorregamento negativo — sendo aplicada
principalmente em turbinas eólicas e pequenas centrais hidrelétricas de velocidade
aproximadamente constante.
""")

    # ── Seção 2 ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 2 · Estrutura Construtiva — Estator e Rotor")
    st.markdown("""
### Estator
O **estator** é estruturalmente semelhante ao de qualquer máquina CA: um núcleo
de lâminas de aço silício (para reduzir as perdas no ferro) provido de ranhuras
onde são instalados os enrolamentos trifásicos. As bobinas das três fases são
deslocadas 120° elétricos entre si, produzindo um campo resultante girante de
amplitude constante.

### Tipos de Rotor
Existem dois tipos construtivos básicos:
""")

    show_fig(fig_rotor_bobinado(), width_frac=0.80)
    st.caption("Figura — Comparação entre o rotor gaiola de esquilo (esquerda) e o rotor bobinado (direita).")

    st.markdown("""
**Rotor gaiola de esquilo** (*squirrel-cage*): consiste em barras de alumínio (ou cobre) dispostas
paralelamente ao eixo, encaixadas nas fendas do núcleo e curto-circuitadas em ambas as
extremidades por anéis terminais sólidos. É o tipo mais simples, econômico e robusto — sendo
amplamente dominante na indústria.

**Rotor bobinado** (*wound rotor*): possui enrolamento trifásico isolado análogo ao do estator,
com terminais acessíveis ao exterior por meio de anéis coletores montados sobre o eixo.
Isso permite a inserção de resistências externas no circuito do rotor, viabilizando o controle
de corrente de partida e a ajuste da velocidade em regime — porém com maior complexidade e custo.
""")

    show_fig(fig_secao_transversal_mei(), width_frac=0.62)
    st.caption("Figura — Seção transversal idealizada de uma MIT 2 polos: estator laminado com "
               "enrolamentos trifásicos (azul, verde, laranja) e rotor gaiola (barras + anéis).")

    # ── Seção 3 ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 3 · Campo Magnético Girante")
    st.markdown("""
Quando as três fases do estator são alimentadas por um sistema trifásico equilibrado, cada
enrolamento produz uma força magnetomotriz (FMM) pulsante ao longo do seu eixo magnético,
defasadas 120° elétricos no tempo. A superposição das três FMM resulta em um **campo
magnético resultante de amplitude constante que gira uniformemente** no espaço.

Analiticamente, para um estator com polo N próximo ao eixo positivo da fase $a$:

$$H_a(\\theta) = H_m\\cos(\\omega t)\\cos\\theta$$
$$H_b(\\theta) = H_m\\cos\\!\\left(\\omega t - \\frac{2\\pi}{3}\\right)\\cos\\!\\left(\\theta - \\frac{2\\pi}{3}\\right)$$
$$H_c(\\theta) = H_m\\cos\\!\\left(\\omega t - \\frac{4\\pi}{3}\\right)\\cos\\!\\left(\\theta - \\frac{4\\pi}{3}\\right)$$

A resultante é:

$$H_{res}(\\theta, t) = H_a + H_b + H_c = \\frac{3}{2}H_m\\cos(\\theta - \\omega t)$$

O argumento $\\theta - \\omega t = \\text{const}$ confirma que o pico da distribuição de campo
percorre o entreferro com velocidade angular $\\omega$ rad/s elétricos — o **campo girante**.
""")

    show_fig(fig_campo_girante(), width_frac=0.90)
    st.caption("Figura — Composição vetorial das FMM das três fases em quatro instantes. "
               "O vetor resultante (preto) mantém amplitude constante $3H_m/2$ e gira a $\\omega$.")

    st.markdown("""
### Velocidade Síncrona

A velocidade de rotação do campo, chamada **velocidade síncrona** $n_s$, depende da frequência
da rede elétrica e do número de polos da máquina:

$$\\boxed{n_s = \\frac{120\\,f}{p} \\quad \\text{(rpm)}}$$

onde $f$ é a frequência em Hz e $p$ é o número de polos.

Em radianos por segundo: $\\omega_s = 2\\pi n_s / 60$.
""")

    show_fig(fig_velocidade_sincrona(), width_frac=0.70)
    st.caption("Figura — Velocidade síncrona para 50 Hz e 60 Hz em função do número de polos.")

    # ── Seção 4 ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 4 · Escorregamento")
    st.markdown("""
Quando o rotor (com enrolamento em curto ou gaiola) é submetido ao campo girante do estator,
tensões são induzidas nas bobinas ou barras do rotor. Essas tensões produzem correntes que,
interagindo com o campo, geram um **torque** que acelera o rotor na direção do campo.

Em regime permanente como motor, o rotor atinge uma velocidade $n$ **ligeiramente inferior** a
$n_s$ — se $n = n_s$ não haveria variação de fluxo no rotor, logo não haveria tensão, corrente
nem torque. A diferença relativa entre a velocidade do campo e a do rotor é o **escorregamento**:

$$\\boxed{s = \\frac{n_s - n}{n_s}}$$

ou equivalentemente em velocidades angulares: $s = (\\omega_s - \\omega)/{\\omega_s}$.

A velocidade do rotor em função de $s$ é:

$$n = n_s(1 - s)$$

**Faixas de escorregamento típicas:**

| Condição | $s$ | $n$ |
|---|---|---|
| Rotor estacionário (partida) | $s = 1$ | $n = 0$ |
| Operação nominal como motor | $0{,}01 < s < 0{,}10$ | $n \\approx n_s$ |
| Velocidade síncrona (ideal, sem torque) | $s = 0$ | $n = n_s$ |
| Gerador (sobreexcitado) | $s < 0$ | $n > n_s$ |
| Frenagem (fase invertida) | $s > 1$ | $n < 0$ |
""")

    show_fig(fig_escorregamento_def(), width_frac=0.60)
    st.caption("Figura — Definição de escorregamento: posição relativa entre $n_s$, $n$ e $n=0$.")

    # ── Seção 5 ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 5 · Tensão Induzida — Estator e Rotor")
    st.markdown("""
### Tensão no Estator

Aplicando a lei de Faraday ao enrolamento do estator (análogo a um transformador), o valor
eficaz da tensão induzida por fase no estator é:

$$\\boxed{E_A = 4{,}44 \\cdot K_w \\cdot N_{ph} \\cdot f \\cdot \\Phi_m}$$

onde:
- $K_w$ — fator de enrolamento ($0{,}85 \\leq K_w \\leq 0{,}95$), que considera o
  efeito do passo fracionário e da distribuição das bobinas nas ranhuras;
- $N_{ph}$ — número de espiras em série por fase;
- $f$ — frequência da rede;
- $\\Phi_m$ — fluxo máximo por polo.

Em máquinas reais, os enrolamentos são distribuídos ao longo das ranhuras para melhorar a
forma de onda; isso causa uma pequena redução da tensão induzida, corrigida pelo fator $K_w$.
""")

    show_fig(fig_tensao_induzida_estator(), width_frac=0.72)
    st.caption("Figura — Forma de onda da tensão induzida no estator e equação do valor eficaz.")

    st.markdown("""
### Tensão no Rotor

Com o rotor **estacionário** ($s = 1$), a frequência e a tensão induzida no rotor são iguais
às do estator (relação de transformação):

$$E_{r0} = \\frac{N_r}{N_s} \\cdot E_A \\qquad f_{r0} = f$$

Com o rotor **girando** com escorregamento $s$, a velocidade relativa entre o campo e o
rotor cai, reduzindo proporcionalmente a tensão induzida e a frequência no rotor:

$$\\boxed{E_r = s \\cdot E_{r0}} \\qquad \\boxed{f_r = s \\cdot f}$$

Quando $s \\to 0$ (rotor quase em sincronismo), $E_r \\to 0$ e $f_r \\to 0$.
Na partida ($s = 1$), $E_r = E_{r0}$ e $f_r = f$.

**Implicação importante:** a reatância do rotor também escala com $s$:
$X_r = s\\,X_{r0}$, onde $X_{r0} = 2\\pi f L_r$.
""")

    show_fig(fig_tensao_rotor_escorregamento(), width_frac=0.82)
    st.caption("Figura — Variação de $E_r$ e $f_r$ com o escorregamento $s$.")

    # ── Seção 6 ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 6 · Circuito Equivalente (por fase)")
    st.markdown("""
A MIT pode ser modelada por um **circuito equivalente monofásico** semelhante ao do
transformador, porém com resistência variável no secundário (rotor referido ao estator)
que captura a conversão eletromecânica.

### Circuito Completo

O circuito completo inclui:
- Ramo série do estator: $R_1$ (resistência) + $jX_1$ (reatância de dispersão);
- Ramo de excitação em paralelo: $R_c$ (perdas no ferro) em paralelo com $jX_m$ (magnetização);
- Ramo série do rotor (referido): $jX'_2$ (reatância de dispersão) + $R'_2/s$ (resistência
  variável com o escorregamento).

A resistência $R'_2/s$ pode ser decomposta como:

$$\\frac{R'_2}{s} = R'_2 + R'_2\\frac{1-s}{s}$$

onde $R'_2$ representa as perdas Joule no rotor e $R'_2(1-s)/s$ representa a **potência
mecânica convertida** (potência no "resistor de carga").
""")

    show_fig(fig_circuito_completo(), width_frac=0.82)
    st.caption("Figura — Circuito equivalente completo com $R_c$, $X_m$, $R_1$, $X_1$, $R'_2/s$, $X'_2$.")

    st.markdown("""
### Circuito IEEE Simplificado

Para simplificar a análise (e quando $R_c$ é omitido), o modelo IEEE move o ramo de
magnetização $X_m$ para os terminais de entrada, eliminando $R_c$:
""")

    show_fig(fig_circuito_ieee(), width_frac=0.78)
    st.caption("Figura — Circuito equivalente IEEE simplificado (sem $R_c$).")

    st.markdown("""
### Equivalente de Thévenin

Para facilitar o cálculo de torque, o circuito visto pelo rotor pode ser reduzido ao
equivalente de Thévenin visto pelos terminais do ramo do rotor. As fórmulas simplificadas
(válidas quando $R_1 \\ll X_1 + X_m$) são:

$$V_{th} \\approx V_1 \\frac{X_m}{X_1 + X_m}$$

$$R_{th} \\approx R_1 \\left(\\frac{X_m}{X_1 + X_m}\\right)^2$$

$$X_{th} \\approx X_1$$
""")

    show_fig(fig_circuito_thevenin(), width_frac=0.72)
    st.caption("Figura — Circuito equivalente de Thévenin: $V_{th}$, $R_{th}$, $X_{th}$ em série com $R'_2/s + jX'_2$.")

    # ── Seção 7 ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 7 · Fluxo de Potência e Balanço de Energia")
    st.markdown("""
O balanço de potência do motor de indução segue uma cadeia linear de conversão. A partir
da potência elétrica inserida nos terminais do estator, as perdas vão sendo subtraídas
sucessivamente até chegar à potência mecânica útil no eixo.

$$P_{in} \\xrightarrow{-P_{cu,1}} \\xrightarrow{-P_{fe}} P_{ag} \\xrightarrow{-P_{cu,2}} P_{mec} \\xrightarrow{-P_{rot}} P_{out}$$

| Grandeza | Expressão | Descrição |
|---|---|---|
| $P_{in}$ | $3\\,V_1 I_1 \\cos\\varphi$ | Potência elétrica de entrada (3 fases) |
| $P_{cu,1}$ | $3\\,R_1 I_1^2$ | Perdas Joule no estator |
| $P_{fe}$ | $3\\,V_1^2/R_c$ | Perdas no ferro (histerese + correntes parasitas) |
| $P_{ag}$ | $3\\,(R'_2/s)\\,I_2^{'2}$ | Potência transferida ao rotor pelo entreferro |
| $P_{cu,2}$ | $s\\,P_{ag}$ | Perdas Joule no rotor |
| $P_{mec}$ | $(1-s)\\,P_{ag}$ | Potência mecânica desenvolvida |
| $P_{rot}$ | constante | Perdas por atrito, ventilação e suplementares |
| $P_{out}$ | $P_{mec} - P_{rot}$ | Potência útil no eixo |

A relação $P_{cu,2} = s\\,P_{ag}$ é fundamental: em um motor operando a $s = 5\\%$,
apenas $5\\%$ da potência do entreferro é dissipada como calor no rotor — o restante
$95\\%$ é convertido em potência mecânica.
""")

    show_fig(fig_fluxo_potencia_motor(), width_frac=0.90)
    st.caption("Figura — Fluxo de potência no motor de indução com indicação de cada perda.")

    # ── Seção 8 ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 8 · Torque Eletromagnético")
    st.markdown("""
O **torque eletromagnético** desenvolvido pela máquina pode ser obtido diretamente da
potência de entreferro $P_{ag}$, que é toda transferida ao rotor (antes das perdas Joule
rotóricas):

$$\\boxed{T_{em} = \\frac{P_{ag}}{\\omega_s} = \\frac{3\\,I_2^{'2}\\,(R'_2/s)}{\\omega_s}}$$

Usando o circuito de Thévenin, a expressão analítica do torque em função de $s$ é:

$$T_{em}(s) = \\frac{3\\,V_{th}^2\\,(R'_2/s)}{\\omega_s \\left[(R_{th} + R'_2/s)^2 + (X_{th} + X'_2)^2\\right]}$$

**Torque máximo** (torque de pull-out) $T_{max}$ ocorre no escorregamento crítico:

$$s_{max} = \\frac{R'_2}{\\sqrt{R_{th}^2 + (X_{th}+X'_2)^2}}$$

$$T_{max} = \\frac{3\\,V_{th}^2}{2\\,\\omega_s \\left[R_{th} + \\sqrt{R_{th}^2+(X_{th}+X'_2)^2}\\right]}$$

Note que $T_{max}$ **independe de $R'_2$**, enquanto o escorregamento $s_{max}$ é
diretamente proporcional a $R'_2$. Isso é explorado no rotor bobinado: inserindo resistência
externa no rotor, desloca-se $s_{max}$ para 1 (partida com torque máximo),
sem alterar o valor de $T_{max}$.
""")

    # ── Seção 9 ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 9 · Modos de Operação")
    st.markdown("""
A máquina de indução pode operar em três regiões distintas, dependendo do escorregamento:

### Motor ($0 < s < 1$)
O estator é alimentado e o rotor gira na mesma direção do campo, com velocidade
inferior à síncrona. A potência elétrica entra pelo estator e é convertida em potência
mecânica disponível no eixo. É a operação mais comum.

### Gerador ($s < 0$)
O rotor é acionado por uma fonte mecânica a velocidade superior à síncrona
($n > n_s$). O fluxo relativo entre rotor e campo girante se inverte, invertendo o
sentido do torque eletromagnético — agora o torque freia o rotor e a potência flui do
eixo para a rede elétrica. Aplicação: turbinas eólicas conectadas diretamente à rede.

### Frenagem ($s > 1$)
O sentido de rotação do rotor é oposto ao do campo girante (mudança de sequência de fases
ou aplicação de carga mecânica invertida). Nesta condição, tanto a potência elétrica
quanto a mecânica são consumidas como perdas no rotor: $P_{cu,2} = s\\,P_{ag} > P_{ag}$.
Usado em frenagem rápida de cargas de inércia elevada.

### Modo "invertido" (alimentação pelo rotor)
Em rotores bobinados, também é possível alimentar o rotor pelos anéis coletores com o
estator em curto. Neste caso, o motor gira no sentido **oposto** ao campo do estator.
""")

    show_fig(fig_modos_operacao(), width_frac=0.75)
    st.caption("Figura — Curva $T \\times n$ nas três regiões: motor (verde), gerador (azul) "
               "e frenagem (vermelho). O torque é positivo no sentido do campo girante.")

    # ── Seção 10 ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 10 · Curva Característica T × n")
    st.markdown("""
A curva $T \\times n$ (ou $T \\times s$) é a **assinatura dinâmica** do motor de indução.
Seus pontos notáveis determinam as capacidades de partida, operação nominal e sobrecargas:

| Ponto | Símbolo | Condição |
|---|---|---|
| Torque de partida | $T_{part}$ | $s=1$, $n=0$ |
| Torque máximo (pull-out) | $T_{max}$ | $s = s_{max}$ |
| Torque nominal | $T_{nom}$ | $s_{nom} \\approx 1{-}10\\%$ |
| Velocidade síncrona | $n_s$ | $T=0$, $s=0$ |

A operação estável do motor ocorre na região à **direita** do $T_{max}$ (baixo escorregamento),
onde um aumento de carga aumenta $s$, aumenta $T_{em}$ e reestabelece o equilíbrio.
Na região à **esquerda** do $T_{max}$ (alto escorregamento), qualquer aumento de carga reduz
$T_{em}$ — operação instável.
""")

    show_fig(fig_curva_torque_velocidade(), width_frac=0.75)
    st.caption("Figura — Curva característica $T \\times n$ na região motora com pontos notáveis.")

    # ── Seção 11 ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 11 · Métodos de Partida")
    st.markdown("""
Na partida direta (DOL — *Direct On-Line*), a corrente de partida pode atingir 5 a 8 vezes
a corrente nominal, o que pode causar queda de tensão na rede, danos aos contatos e
solicitação mecânica excessiva. Os principais métodos para limitar a corrente de partida são:

### 1. Partida estrela-triângulo (Y/Δ)
O estator é ligado em Y na partida (reduzindo a tensão de fase por $1/\\sqrt{3}$) e,
após atingir velocidade próxima à nominal, comuta para Δ. Reduz a corrente e o torque
de partida por um fator **3** em relação à ligação Δ direta.

### 2. Autotransformador
Uma tensão reduzida $\\alpha V_1$ é aplicada ao motor, onde $\\alpha < 1$. A corrente
de partida na linha cai por $\\alpha^2$ e o torque de partida também cai por $\\alpha^2$.
Oferece mais flexibilidade que o Y/Δ.

### 3. Resistência em série no estator
Resistores (ou reatores) são inseridos em série no estator durante a partida e
curto-circuitados após. Dissipam calor, reduzindo o torque de partida.

### 4. Resistência no rotor (rotor bobinado)
Inserir $R_{ext}$ no rotor desloca o $s_{max}$ para 1, maximizando o torque de
partida enquanto limita a corrente. Gradualmente, $R_{ext}$ é reduzida até zero em plena
carga.

### 5. Inversor de frequência (VFD)
Alimentar o motor com frequência e tensão crescentes a partir de zero (relação V/f
constante) mantém o fluxo constante e o torque de partida elevado com corrente controlada.
É o método mais moderno e flexível.
""")

    # ── Seção 12 ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 12 · Gaiola de Esquilo Dupla")
    st.markdown("""
Uma solução construtiva para melhorar a partida sem o custo do rotor bobinado é a
**gaiola dupla**. O rotor possui dois conjuntos de barras concêntricos:

- **Gaiola externa**: barras de alta resistência e baixa reatância (seção menor, posição
  próxima ao entreferro → pequena indutância de dispersão);
- **Gaiola interna**: barras de baixa resistência e alta reatância (seção maior, posição
  profunda → grande indutância de dispersão).

**Por que funciona na partida ($s ≈ 1$, $f_r = f$)?**
A alta frequência no rotor aumenta a reatância da gaiola interna, confinando a corrente
na gaiola externa (alta $R$). Isso produz alto torque de partida com escorregamento elevado.

**Por que funciona em regime ($s \\ll 1$, $f_r \\to 0$)?**
A baixa frequência no rotor torna ambas as reatâncias desprezíveis. A corrente divide-se
principalmente pela gaiola interna (baixa $R$), reduzindo as perdas e melhorando a
eficiência em regime permanente.

O efeito pelicular (*skin effect*) é o mecanismo físico subjacente: em alta frequência, a
densidade de corrente se concentra na superfície das barras, equivalente à gaiola externa.
""")

    show_fig(fig_gaiola_dupla(), width_frac=0.75)
    st.caption("Figura — Curvas $T \\times n$ da gaiola dupla (verde sólida), gaiola externa "
               "(vermelha), gaiola interna (azul) e gaiola simples de referência (cinza).")

    # ── Exploradores Interativos ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🎛️ Exploradores Interativos")

    tab_labels = [
        "T × n",
        "Circuito Equiv.",
        "Tensão → T × n",
        "Partida",
        "Eficiência",
    ]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        exp_torque_velocidade()

    with tabs[1]:
        exp_circuito_equivalente()

    with tabs[2]:
        exp_escorregamento_tensao()

    with tabs[3]:
        exp_partida_autotransformador()

    with tabs[4]:
        exp_eficiencia()

    # ── Referências ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 📚 Referências")
    st.markdown("""
- BARBI, I. *Teoria Fundamental do Motor de Indução*. Santa Catarina: Ed. UFSC, 1985.
- CHAPMAN, S. J. *Fundamentos de Máquinas Elétricas*. 5. ed. São Paulo: McGraw-Hill, 2013.
- JACOBINA, C.; LIMA, A. M. *Acionamentos de Máquinas Elétricas de Alto Desempenho*. Minicurso XIV CBA, Natal, 2002.
- KOSOW, I. *Máquinas Elétricas e Transformadores*. 14. reimp. São Paulo: Globo, 2000.
- UMANS, S. D. *Máquinas Elétricas de Fitzgerald e Kingsley*. 7. ed. São Paulo: McGraw-Hill, 2014.
- BIM, E. *Máquinas Elétricas e Acionamento*. Rio de Janeiro: Campus Elsevier, 2009.
- SEN, P. C. *Princípios de Máquinas Elétricas e Eletrônica de Potência*. 3. ed. Wiley, 2013.
""")
