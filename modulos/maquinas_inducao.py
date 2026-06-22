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

    # ── CSS responsivo — injetado uma única vez ───────────────────────────────
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

    # ── Helper de exibição responsivo (figuras matplotlib) ────────────────────
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
        """Plotly — transparente, com grade leve e fonte escura, responsivo nativo."""
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

    def _mpl_base_off(figsize=(6, 5)):
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        ax.set_aspect("equal")
        ax.axis("off")
        return fig, ax

    def _mpl_base_on(figsize=(6, 4)):
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["bottom", "left"]].set_color(CZ)
        ax.tick_params(colors=CZ)
        return fig, ax

    # ════════════════════════════════════════════════════════════════════════
    # FIGURAS — matplotlib
    # ════════════════════════════════════════════════════════════════════════

    def fig_secao_transversal_mei():
        """Seção transversal 2P: estator com três fases e rotor gaiola de esquilo."""
        fig, ax = _mpl_base_off((6.0, 6.8))
        ax.set_xlim(-4.8, 4.8)
        ax.set_ylim(-4.8, 5.4)

        R_yoke_out = 4.2
        R_yoke_in  = 3.5    # face interna do jugo (base das ranhuras do estator)
        R_slot_mid = 3.15   # centro dos enrolamentos do estator
        R_ext_r    = 2.55   # raio externo do núcleo do rotor
        R_int_r    = 0.85   # eixo
        R_bar      = 2.10   # raio das barras da gaiola

        # ── Jugo do estator ──────────────────────────────────────────────
        ax.add_patch(mpatches.Wedge(
            (0, 0), R_yoke_out, 0, 360,
            width=R_yoke_out - R_yoke_in,
            fc="#dce4f0", ec=TX, lw=1.6, zorder=2))

        # ── Entreferro (branco) ──────────────────────────────────────────
        ax.add_patch(mpatches.Wedge(
            (0, 0), R_yoke_in, 0, 360,
            width=R_yoke_in - R_ext_r - 0.05,
            fc="white", ec="none", zorder=3))

        # ── Núcleo do rotor ──────────────────────────────────────────────
        ax.add_patch(mpatches.Circle(
            (0, 0), R_ext_r,
            fc="#dce4f0", ec=TX, lw=1.4, zorder=2))

        # ── Eixo ─────────────────────────────────────────────────────────
        ax.add_patch(mpatches.Circle(
            (0, 0), R_int_r,
            fc="#b0bcd0", ec=TX, lw=1.0, zorder=5))
        ax.text(0, 0, "Eixo", fontsize=7.5, color=TX,
                ha="center", va="center", zorder=6)

        # ── Enrolamentos do estator (3 fases, 2 polos, 2 ranhuras/fase/polo) ──
        # Sequência de grupos de 0° a 300°, 60° entre fases
        # Condutores do mesmo grupo ficam a ±8° do ângulo central
        fases = [
            (0,   AZ, "a",  "+"),   # fase a, polo N
            (60,  VD, "b",  "+"),
            (120, LR, "c",  "+"),
            (180, AZ, "a'", "−"),   # fase a, polo S
            (240, VD, "b'", "−"),
            (300, LR, "c'", "−"),
        ]
        cond_r = 0.32   # raio dos discos de condutor

        for ang_base, cor, lbl, sinal in fases:
            for delta in [-9, 9]:               # dois condutores por grupo
                ang = np.radians(ang_base + delta)
                cx  = R_slot_mid * np.cos(ang)
                cy  = R_slot_mid * np.sin(ang)
                ax.add_patch(mpatches.Circle(
                    (cx, cy), cond_r,
                    fc=cor, ec=TX, lw=0.7, alpha=0.90, zorder=6))
                # símbolo de corrente
                if sinal == "+":
                    ax.plot(cx, cy, ".", color="white", ms=5, zorder=7)
                else:
                    for dx, dy in [(-0.10, -0.10), (0.10, 0.10)]:
                        ax.plot([cx + dx, cx - dx], [cy + dy, cy - dy],
                                color="white", lw=1.2, zorder=7)

            # Label da fase, fora do jugo
            ang_lbl = np.radians(ang_base)
            lx = (R_yoke_out + 0.38) * np.cos(ang_lbl)
            ly = (R_yoke_out + 0.38) * np.sin(ang_lbl)
            ax.text(lx, ly, f"${lbl}$", color=cor, fontsize=10,
                    ha="center", va="center", fontweight="bold", zorder=8)

        # ── Barras da gaiola de esquilo (12 barras) ───────────────────────
        n_bars = 12
        bar_r  = 0.20
        for i in range(n_bars):
            ang = np.radians(360 * i / n_bars)
            bx  = R_bar * np.cos(ang)
            by  = R_bar * np.sin(ang)
            ax.add_patch(mpatches.Circle(
                (bx, by), bar_r,
                fc=LR, ec=TX, lw=0.6, alpha=0.88, zorder=5))

        # Anel de curto-circuito (tracejado)
        ax.add_patch(mpatches.Wedge(
            (0, 0), R_bar + bar_r + 0.08, 0, 360,
            width=2 * (bar_r + 0.08),
            fc="none", ec=LR, lw=2.0, linestyle="--", alpha=0.55, zorder=4))

        # ── Título ───────────────────────────────────────────────────────
        ax.text(0, 4.72,
                "Seção Transversal — MIT Polifásica (2 Polos)",
                ha="center", fontsize=10.5, fontweight="bold", color=TX, zorder=8)

        # ── Legenda ──────────────────────────────────────────────────────
        patches = [
            mpatches.Patch(fc="#dce4f0", ec=TX, lw=0.8, label="Estator laminado"),
            mpatches.Patch(fc=AZ, label="Fase a (⊙/⊗)"),
            mpatches.Patch(fc=VD, label="Fase b (⊙/⊗)"),
            mpatches.Patch(fc=LR, label="Fase c / barras da gaiola"),
        ]
        ax.legend(handles=patches, loc="lower center",
                  fontsize=7.5, framealpha=0.0,
                  bbox_to_anchor=(0.5, -0.04), ncol=2)
        return fig

    def fig_rotor_bobinado():
        """Comparação: rotor gaiola de esquilo (esq.) vs rotor bobinado (dir.)."""
        fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.6))
        fig.patch.set_alpha(0)

        for ax in axes:
            ax.set_facecolor("none")
            ax.set_aspect("equal")
            ax.axis("off")

        R = 2.5; R_in = 0.9; bar_r = 0.20

        # ── Gaiola de esquilo (esquerda) ──────────────────────────────────
        ax0 = axes[0]
        ax0.set_xlim(-3.6, 3.6); ax0.set_ylim(-3.6, 4.2)

        ax0.add_patch(mpatches.Circle((0,0), R, fc="#dce4f0", ec=TX, lw=1.5, zorder=2))
        ax0.add_patch(mpatches.Circle((0,0), R_in, fc="#b0bcd0", ec=TX, lw=1.2, zorder=4))
        # Barras
        n_bars = 14; bar_mid = (R + R_in) / 2
        for i in range(n_bars):
            ang = np.radians(360 * i / n_bars)
            ax0.add_patch(mpatches.Circle(
                (bar_mid*np.cos(ang), bar_mid*np.sin(ang)),
                bar_r, fc=LR, ec=TX, lw=0.6, alpha=0.90, zorder=5))
        # Anel de curto
        ax0.add_patch(mpatches.Wedge(
            (0,0), bar_mid+bar_r+0.10, 0, 360,
            width=2*(bar_r+0.10), fc="none",
            ec=LR, lw=2.5, ls="--", alpha=0.60, zorder=3))
        ax0.text(0, 0, "Eixo", fontsize=8, color=TX, ha="center", va="center", zorder=6)
        ax0.text(0, R+0.55, "Rotor Gaiola de Esquilo",
                 ha="center", fontsize=10, fontweight="bold", color=TX)
        ax0.text(0, -R-0.55,
                 "Barras de alumínio curto-circuitadas\npelos anéis terminais",
                 ha="center", fontsize=8, color=CZ, style="italic")
        # Legenda barras
        ax0.text(bar_mid*np.cos(np.radians(45))+0.4,
                 bar_mid*np.sin(np.radians(45))+0.3,
                 "barra", fontsize=7, color=LR)
        ax0.annotate("", xy=(bar_mid*np.cos(np.radians(45)),
                              bar_mid*np.sin(np.radians(45))),
                     xytext=(bar_mid*np.cos(np.radians(45))+0.4,
                              bar_mid*np.sin(np.radians(45))+0.25),
                     arrowprops=dict(arrowstyle="-|>", color=LR, lw=0.9))

        # ── Rotor bobinado (direita) ───────────────────────────────────────
        ax1 = axes[1]
        ax1.set_xlim(-3.6, 3.6); ax1.set_ylim(-3.6, 4.2)

        ax1.add_patch(mpatches.Circle((0,0), R, fc="#dce4f0", ec=TX, lw=1.5, zorder=2))
        ax1.add_patch(mpatches.Circle((0,0), R_in, fc="#b0bcd0", ec=TX, lw=1.2, zorder=4))
        ax1.text(0, 0, "Eixo", fontsize=8, color=TX, ha="center", va="center", zorder=6)

        # Enrolamentos trifásicos do rotor (6 grupos ×2 condutores)
        slot_mid_r = (R + R_in) / 2
        cond_r = 0.28
        fases_r = [
            (0,   AZ, "+"), (60,  VD, "+"), (120, LR, "+"),
            (180, AZ, "−"), (240, VD, "−"), (300, LR, "−"),
        ]
        for ang_base, cor, sinal in fases_r:
            for delta in [-8, 8]:
                ang = np.radians(ang_base + delta)
                cx, cy = slot_mid_r*np.cos(ang), slot_mid_r*np.sin(ang)
                ax1.add_patch(mpatches.Circle(
                    (cx, cy), cond_r, fc=cor, ec=TX, lw=0.6, alpha=0.88, zorder=5))
                if sinal == "+":
                    ax1.plot(cx, cy, ".", color="white", ms=4.5, zorder=6)
                else:
                    for dx, dy in [(-0.09, -0.09), (0.09, 0.09)]:
                        ax1.plot([cx+dx, cx-dx], [cy+dy, cy-dy],
                                 color="white", lw=1.1, zorder=6)

        # Anéis coletores — 3 arcos coloridos no lado direito
        for ri, cor_r in enumerate([AZ, VD, LR]):
            r_ring = R - 0.12 - ri * 0.22
            ax1.add_patch(mpatches.Wedge(
                (0,0), r_ring, -12, 12,
                width=0.14, fc=cor_r, ec=TX, lw=0.5, zorder=6))

        # Label anéis coletores (dentro do eixo x do painel)
        ax1.annotate("Anéis\ncoletores",
                     xy=(R - 0.25, 0), xytext=(R + 0.5, 0.5),
                     fontsize=8, color=TX, ha="left",
                     arrowprops=dict(arrowstyle="-|>", color=CZ, lw=0.9))

        ax1.text(0, R+0.55, "Rotor Bobinado (Wound)",
                 ha="center", fontsize=10, fontweight="bold", color=TX)
        ax1.text(0, -R-0.55,
                 "Enrolamento trifásico — terminais acessíveis\npelos anéis coletores",
                 ha="center", fontsize=8, color=CZ, style="italic")

        fig.tight_layout(pad=0.5)
        return fig

    def fig_campo_girante():
        """Campo magnético girante: 4 instantes com composição vetorial Ha, Hb, Hc → Hr."""
        fig, axes = plt.subplots(1, 4, figsize=(11, 3.4))
        fig.patch.set_alpha(0)

        # Eixos magnéticos das fases no estator (ângulo do eixo de campo de cada fase)
        eixos_fase = [np.radians(90), np.radians(90 - 120), np.radians(90 - 240)]
        cores_f    = [AZ, VD, LR]
        labels_f   = ["$H_a$", "$H_b$", "$H_c$"]
        instantes  = [0, 60, 90, 180]

        for ax, wt_deg in zip(axes, instantes):
            ax.set_facecolor("none")
            ax.set_xlim(-1.7, 1.7); ax.set_ylim(-1.7, 1.9)
            ax.set_aspect("equal"); ax.axis("off")

            # Círculo do estator
            ax.add_patch(mpatches.Circle(
                (0,0), 1.45, fc="none", ec=CZ, lw=0.9, alpha=0.35, zorder=1))

            wt = np.radians(wt_deg)
            # Amplitudes instantâneas (senoide)
            mags = [
                np.cos(wt),
                np.cos(wt - np.radians(120)),
                np.cos(wt - np.radians(240)),
            ]

            # Componentes x e y de cada vetor de campo
            Hvx = [m * np.cos(a) for m, a in zip(mags, eixos_fase)]
            Hvy = [m * np.sin(a) for m, a in zip(mags, eixos_fase)]

            # Vetores das três fases
            for i, (hx, hy, cor, lbl) in enumerate(zip(Hvx, Hvy, cores_f, labels_f)):
                if abs(hx)**2 + abs(hy)**2 > 1e-4:
                    ax.annotate("",
                                xy=(hx * 0.90, hy * 0.90),
                                xytext=(0, 0),
                                arrowprops=dict(
                                    arrowstyle="-|>", color=cor,
                                    lw=1.6, mutation_scale=12))
                # Labels dos eixos magnéticos (fixos, na periferia)
                lx = 1.62 * np.cos(eixos_fase[i])
                ly = 1.62 * np.sin(eixos_fase[i])
                ax.text(lx, ly, lbl, color=cor, fontsize=8.5,
                        ha="center", va="center", zorder=8)

            # Vetor resultante Hr
            Hr_x = sum(Hvx); Hr_y = sum(Hvy)
            if Hr_x**2 + Hr_y**2 > 0.01:
                ax.annotate("",
                            xy=(Hr_x * 0.88, Hr_y * 0.88),
                            xytext=(0, 0),
                            arrowprops=dict(
                                arrowstyle="-|>", color=TX,
                                lw=2.4, mutation_scale=15))
                ax.text(Hr_x * 1.05, Hr_y * 1.05, "$H_r$",
                        fontsize=8, color=TX, ha="center", va="center", zorder=9)

            # Título do painel
            ax.text(0, -1.62, f"$\\omega t = {wt_deg}°$",
                    ha="center", fontsize=9, fontweight="bold", color=TX)

        fig.suptitle(
            "Campo Magnético Girante — Composição das FMM em 4 Instantes",
            fontsize=9.5, color=TX, y=1.00)
        fig.tight_layout(pad=0.3)
        return fig

    def fig_velocidade_sincrona():
        """ns = 120f/p para f = 50 e 60 Hz, p = 2, 4, 6, 8, 10, 12."""
        fig, ax = _mpl_base_on((6.5, 4.0))
        polos   = [2, 4, 6, 8, 10, 12]
        for f0, cor, lbl in [(60, AZ, "60 Hz"), (50, VD, "50 Hz")]:
            ns_vals = [120 * f0 / p for p in polos]
            ax.plot(polos, ns_vals, "o-", color=cor, lw=2.0, ms=7,
                    label=f"$f = {f0}$ Hz", zorder=4)
            for p, ns in zip(polos, ns_vals):
                ax.text(p + 0.15, ns + 25, f"{int(ns)}", fontsize=8,
                        color=cor, ha="left")
        ax.set_xlabel("Número de polos $p$", fontsize=11, color=TX)
        ax.set_ylabel("Velocidade síncrona $n_s$ (rpm)", fontsize=11, color=TX)
        ax.set_title("Velocidade Síncrona × Número de Polos",
                     fontsize=11.5, fontweight="bold", color=TX)
        ax.legend(fontsize=9, framealpha=0.0)
        ax.set_xticks(polos)
        ax.grid(True, alpha=0.20, linestyle="--", color=CZ)
        fig.tight_layout()
        return fig

    def fig_escorregamento_def():
        """Diagrama vertical: ns, n, n=0 com seta de escorregamento e equação."""
        fig, ax = plt.subplots(figsize=(5.8, 4.6))
        fig.patch.set_alpha(0); ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(0, 6); ax.set_ylim(0, 6)

        # Eixo de velocidade vertical (x=1.2)
        xv = 1.2
        ax.annotate("", xy=(xv, 5.8), xytext=(xv, 0.3),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.6))
        ax.text(xv, 6.0, "$n$\n(rpm)", ha="center", fontsize=9.5, color=TX, va="bottom")

        # ns (topo)
        y_ns = 5.0; y_n = 3.6; y_0 = 0.7
        ax.plot(xv, y_ns, "o", color=AZ, ms=11, zorder=5)
        ax.plot(xv, y_n,  "o", color=VD, ms=11, zorder=5)
        ax.plot(xv, y_0,  "o", color=LR, ms=11, zorder=5)

        # Linhas horizontais de referência (tracejadas)
        for y, cor in [(y_ns, AZ), (y_n, VD), (y_0, LR)]:
            ax.plot([xv - 0.15, xv + 0.15], [y, y], color=cor, lw=0.8)

        # Textos à direita do eixo
        ax.text(xv + 0.28, y_ns, r"$n_s = \dfrac{120\,f}{p}$  (vel. síncrona)",
                fontsize=9.5, color=AZ, va="center")
        ax.text(xv + 0.28, y_n, r"$n$  — vel. do rotor ($n < n_s$)",
                fontsize=9.5, color=VD, va="center")
        ax.text(xv + 0.28, y_0, r"$n = 0$  (rotor parado — partida)",
                fontsize=9.5, color=LR, va="center")

        # Seta dupla ns − n
        ax.annotate("", xy=(xv - 0.35, y_n + 0.05),
                    xytext=(xv - 0.35, y_ns - 0.05),
                    arrowprops=dict(arrowstyle="<->", color=RX, lw=1.8))
        ax.text(xv - 0.50, (y_ns + y_n) / 2, "$n_s - n$",
                ha="right", fontsize=9.5, color=RX, va="center")

        # Caixa da equação (centrada, sem sobrepor texto)
        eq_x, eq_y = 3.8, 2.6
        ax.text(eq_x, eq_y,
                r"$s = \dfrac{n_s - n}{n_s}$",
                fontsize=14, color=TX, ha="center", va="center",
                bbox=dict(fc="white", ec=CZ, lw=1.2,
                          boxstyle="round,pad=0.35", alpha=0.88))
        ax.text(eq_x, eq_y - 0.75,
                r"$0 \leq s \leq 1$ em operação motora",
                fontsize=8.5, color=CZ, ha="center", style="italic")

        ax.set_title("Definição de Escorregamento",
                     fontsize=11.5, fontweight="bold", color=TX, pad=6)
        fig.tight_layout()
        return fig

    def fig_tensao_induzida_estator():
        """Tensão induzida no estator: forma de onda e equação do valor eficaz."""
        fig, ax = plt.subplots(figsize=(7, 3.6))
        fig.patch.set_alpha(0); ax.set_facecolor("none")
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["bottom", "left"]].set_color(CZ)
        ax.tick_params(colors=CZ, labelsize=8)

        t  = np.linspace(0, 2, 400)  # 2 períodos normalizados
        e  = np.sin(2 * np.pi * t)
        ax.plot(t, e, color=AZ, lw=2.4, zorder=4)
        ax.axhline(0, color=CZ, lw=0.8)

        # Anotação E_max (seta dupla vertical)
        t_pico = 0.25
        ax.annotate("", xy=(t_pico, 1.0), xytext=(t_pico, 0.0),
                    arrowprops=dict(arrowstyle="<->", color=VM, lw=1.8))
        ax.text(t_pico + 0.04, 0.52, "$E_{\\mathrm{max}}$",
                fontsize=10, color=VM, va="center")

        # Equação fora da área da curva (canto superior esquerdo)
        ax.text(0.02, 0.97,
                r"$E_A = 4{,}44 \cdot K_w \cdot N_{ph} \cdot f \cdot \Phi_m$",
                fontsize=10.5, color=TX, va="top",
                transform=ax.transAxes,
                bbox=dict(fc="white", ec=CZ, lw=1.0,
                          boxstyle="round,pad=0.3", alpha=0.90))

        # Legenda dos parâmetros — abaixo do eixo x, dentro do axes
        ax.text(0.5, -0.22,
                "$K_w$: fator de enrolamento     "
                "$N_{ph}$: espiras por fase     "
                "$\\Phi_m$: fluxo por polo",
                fontsize=7.5, color=CZ, ha="center", transform=ax.transAxes)

        ax.set_xlabel("tempo (p.u.)", fontsize=9, color=TX)
        ax.set_ylabel("$e(t)$ (p.u.)", fontsize=9, color=TX)
        ax.set_title("Tensão Induzida — Enrolamento do Estator",
                     fontsize=11, fontweight="bold", color=TX, pad=6)
        ax.set_ylim(-1.25, 1.40)
        fig.subplots_adjust(bottom=0.22)
        return fig

    def fig_tensao_rotor_escorregamento():
        """Er = s·Er0 e fr = s·f em função do escorregamento."""
        fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
        fig.patch.set_alpha(0)
        s = np.linspace(0, 1, 300)

        # Tensão no rotor
        ax0 = axes[0]; ax0.set_facecolor("none")
        ax0.spines[["top","right"]].set_visible(False)
        ax0.spines[["bottom","left"]].set_color(CZ)
        ax0.tick_params(colors=CZ)
        ax0.plot(s, s, color=AZ, lw=2.4, zorder=4)
        ax0.scatter([0, 1], [0, 1], color=AZ, s=55, zorder=6)
        ax0.text(0.05, 0.10,  r"$s=0 \Rightarrow E_r=0$",   fontsize=8, color=CZ)
        ax0.text(0.55, 0.88,  r"$s=1 \Rightarrow E_r=E_{r0}$", fontsize=8, color=CZ)
        ax0.text(0.50, 0.38,  r"$E_r = s \cdot E_{r0}$",
                 fontsize=12, color=AZ, ha="center")
        ax0.set_xlabel(r"Escorregamento $s$", fontsize=10, color=TX)
        ax0.set_ylabel(r"$E_r / E_{r0}$ (p.u.)", fontsize=10, color=TX)
        ax0.set_title("Tensão Induzida no Rotor",
                      fontsize=10.5, fontweight="bold", color=TX)
        ax0.grid(True, alpha=0.18, linestyle="--", color=CZ)
        ax0.set_xlim(-0.02, 1.05); ax0.set_ylim(-0.02, 1.10)

        # Frequência no rotor
        ax1 = axes[1]; ax1.set_facecolor("none")
        ax1.spines[["top","right"]].set_visible(False)
        ax1.spines[["bottom","left"]].set_color(CZ)
        ax1.tick_params(colors=CZ)
        for f0, cor, lbl in [(60, AZ, "60 Hz"), (50, VD, "50 Hz")]:
            ax1.plot(s, s * f0, color=cor, lw=2.0, label=f"$f={f0}$ Hz")
        ax1.set_xlabel(r"Escorregamento $s$", fontsize=10, color=TX)
        ax1.set_ylabel(r"$f_r = s \cdot f$ (Hz)", fontsize=10, color=TX)
        ax1.set_title("Frequência do Rotor",
                      fontsize=10.5, fontweight="bold", color=TX)
        ax1.legend(fontsize=9, framealpha=0.0)
        ax1.grid(True, alpha=0.18, linestyle="--", color=CZ)
        ax1.set_xlim(-0.02, 1.05)

        fig.tight_layout(pad=1.0)
        return fig

    def fig_modos_operacao():
        """Curva T × n nas três regiões: motor, gerador e frenagem."""
        fig, ax = _mpl_base_on((7.5, 4.6))

        V1, R1, X1, R2, X2, Xm = 127.0, 0.5, 1.0, 0.4, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60

        s_all  = np.concatenate([
            np.linspace(-1.2, -1e-3, 250),
            np.linspace( 1e-3, 2.2,  550),
        ])
        n_all = ns * (1 - s_all)

        def torque(s):
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I2  = (V1 / (R1 + 1j*X1 + Zeq)) * Zeq / Z2
            return 3 * abs(I2)**2 * (R2/s) / ws

        T_all = np.array([torque(s) for s in s_all])

        # Faixas de cor por região
        m_mot  = (n_all >= 0) & (n_all <= ns)
        m_gen  = n_all > ns
        m_fre  = n_all < 0

        ax.fill_between(n_all, T_all, 0, where=m_mot,
                        color=VD, alpha=0.09, zorder=1)
        ax.fill_between(n_all, T_all, 0, where=m_gen,
                        color=AZ, alpha=0.09, zorder=1)
        ax.fill_between(n_all, T_all, 0, where=m_fre,
                        color=VM, alpha=0.09, zorder=1)

        ax.plot(n_all, T_all, color=TX, lw=2.3, zorder=4)
        ax.axhline(0, color=CZ, lw=0.8)
        ax.axvline(ns, color=AZ, lw=1.0, ls="--", alpha=0.55)
        ax.axvline(0,  color=CZ, lw=0.8, ls="--", alpha=0.45)

        T_max_motor = float(np.max(T_all[m_mot])) if m_mot.any() else 1.0

        # Labels das regiões (posicionados dentro da faixa correta)
        ax.text(ns * 0.50,  T_max_motor * 0.50, "MOTOR\n$0 < s < 1$",
                ha="center", fontsize=10, color=VD, fontweight="bold", alpha=0.8)
        ax.text(ns * 1.55,  T_max_motor * 0.28, "GERADOR\n$s < 0$",
                ha="center", fontsize=10, color=AZ, fontweight="bold", alpha=0.8)
        ax.text(-ns * 0.45, T_max_motor * 0.28, "FRENAGEM\n$s > 1$",
                ha="center", fontsize=10, color=VM, fontweight="bold", alpha=0.8)

        ax.text(ns + 30,  ax.get_ylim()[0] * 0.90 if ax.get_ylim()[0] < 0 else -0.8,
                "$n_s$", ha="left", fontsize=9, color=AZ)

        ax.set_xlabel("Velocidade $n$ (rpm)", fontsize=11, color=TX)
        ax.set_ylabel("Torque $T$ (N·m)", fontsize=11, color=TX)
        ax.set_title("Regiões de Operação — Máquina de Indução",
                     fontsize=11.5, fontweight="bold", color=TX)
        ax.set_xlim(-0.80 * ns, 2.20 * ns)
        ax.grid(True, alpha=0.15, linestyle="--", color=CZ)
        fig.tight_layout()
        return fig

    def fig_curva_torque_velocidade():
        """Curva T × n (região motora) com pontos T_part, T_max e T_nom."""
        fig, ax = _mpl_base_on((7.0, 4.5))

        V1, R1, X1, R2, X2, Xm = 127.0, 0.5, 1.0, 0.4, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60
        s_range = np.linspace(1e-3, 1.0, 600)
        n_range = ns * (1 - s_range)

        def T_s(s):
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I2  = (V1 / (R1 + 1j*X1 + Zeq)) * Zeq / Z2
            return 3 * abs(I2)**2 * (R2/s) / ws

        T_vals = np.array([T_s(s) for s in s_range])

        ax.plot(n_range, T_vals, color=AZ, lw=2.5, zorder=4)
        ax.axhline(0, color=CZ, lw=0.7)
        ax.axvline(ns, color=AZ, lw=1.0, ls="--", alpha=0.5)

        idx_max = int(np.argmax(T_vals))
        T_max  = T_vals[idx_max]; n_max = n_range[idx_max]
        T_part = T_s(1.0)
        s_nom  = 0.05
        T_nom  = T_s(s_nom); n_nom = ns * (1 - s_nom)

        # Pontos notáveis com offset de texto para não sobrepor
        pontos = [
            (0,      T_part, "$T_{part}$", "s",  VM,  ( 80, -15)),
            (n_max,  T_max,  "$T_{max}$",  "^",  LR,  (-20,  10)),
            (n_nom,  T_nom,  "$T_{nom}$",  "o",  VD,  ( 20, -18)),
            (ns,     0,      "$n_s$",       "D",  AZ,  (  8,  10)),
        ]
        for x, y, lbl, mk, cor, (dx, dy) in pontos:
            ax.plot(x, y, mk, color=cor, ms=9, zorder=6)
            ax.annotate(lbl, xy=(x, y), xytext=(x + dx, y + dy),
                        fontsize=9, color=cor,
                        arrowprops=dict(arrowstyle="-", color=cor, lw=0.7))

        ax.set_xlabel("Velocidade $n$ (rpm)", fontsize=11, color=TX)
        ax.set_ylabel("Torque $T$ (N·m)", fontsize=11, color=TX)
        ax.set_title("Curva Característica Torque × Velocidade",
                     fontsize=11.5, fontweight="bold", color=TX)
        ax.set_xlim(-50, ns + 120)
        ax.grid(True, alpha=0.18, linestyle="--", color=CZ)
        fig.tight_layout()
        return fig

    def fig_curva_torque_R2():
        """Família T × n para R'2 crescente (rotor bobinado com resistência externa)."""
        fig, ax = _mpl_base_on((7.0, 4.5))

        V1, R1, X1, X2, Xm = 127.0, 0.5, 1.0, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60
        s_range = np.linspace(1e-3, 1.0, 500)
        n_range = ns * (1 - s_range)

        R2_vals  = [0.2, 0.4, 0.6, 1.0, 1.5]
        cores_v  = [AZ, VD, LR, RX, CI]
        ls_list  = ["-", "--", "-.", ":", (0, (3,1,1,1))]

        for R2, cor, ls in zip(R2_vals, cores_v, ls_list):
            def T_fn(s, R2=R2):
                Z2  = R2/s + 1j*X2
                Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
                I2  = (V1 / (R1 + 1j*X1 + Zeq)) * Zeq / Z2
                return 3 * abs(I2)**2 * (R2/s) / ws
            T_v = np.array([T_fn(s) for s in s_range])
            ax.plot(n_range, T_v, color=cor, lw=1.9, ls=ls,
                    label=f"$R'_2 = {R2}\\,\\Omega$", zorder=4)

        ax.axvline(ns, color=AZ, lw=1.0, ls="--", alpha=0.5)
        ax.axhline(0,  color=CZ, lw=0.7)
        ax.set_xlabel("Velocidade $n$ (rpm)", fontsize=11, color=TX)
        ax.set_ylabel("Torque $T$ (N·m)", fontsize=11, color=TX)
        ax.set_title("Efeito de $R'_2$ na Curva $T \\times n$ (Rotor Bobinado)",
                     fontsize=11, fontweight="bold", color=TX)
        ax.legend(fontsize=8.5, framealpha=0.0, ncol=2,
                  loc="upper left")
        ax.set_xlim(-50, ns + 80)
        ax.grid(True, alpha=0.18, linestyle="--", color=CZ)
        fig.tight_layout()
        return fig

    def fig_gaiola_dupla():
        """T × n: gaiola dupla resulta de gaiola externa (alta R) + interna (baixa R)."""
        fig, ax = _mpl_base_on((7.0, 4.5))

        V1, R1, X1, Xm = 127.0, 0.5, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60
        s_range = np.linspace(1e-3, 1.0, 500)
        n_range = ns * (1 - s_range)

        def T_single(s, R2, X2):
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I2  = (V1 / (R1 + 1j*X1 + Zeq)) * Zeq / Z2
            return 3 * abs(I2)**2 * (R2/s) / ws

        # Gaiola dupla: paralelo das duas gaiolas
        R2_ext, X2_ext = 2.0, 0.5   # externa: alta R, baixa X
        R2_int, X2_int = 0.3, 3.5   # interna: baixa R, alta X

        def T_double(s):
            Z_ext = R2_ext/s + 1j*X2_ext
            Z_int = R2_int/s + 1j*X2_int
            Z2_par = Z_ext * Z_int / (Z_ext + Z_int)
            Zeq    = (1j*Xm * Z2_par) / (1j*Xm + Z2_par)
            I_tot  = V1 / (R1 + 1j*X1 + Zeq)
            Veq    = I_tot * Zeq
            I_e    = Veq / Z_ext
            I_i    = Veq / Z_int
            Pag    = 3*(abs(I_e)**2*(R2_ext/s) + abs(I_i)**2*(R2_int/s))
            return Pag / ws

        T_ext = np.array([T_single(s, R2_ext, X2_ext) for s in s_range])
        T_int = np.array([T_single(s, R2_int, X2_int) for s in s_range])
        T_dup = np.array([T_double(s) for s in s_range])
        # Gaiola simples de referência: R2 = R2_int, mesma resistência nominal
        T_sim = np.array([T_single(s, R2_int, X2_int * 0.30) for s in s_range])

        ax.plot(n_range, T_sim, color=CZ, lw=1.4, ls="--",
                label="Gaiola simples (ref.)", zorder=3)
        ax.plot(n_range, T_ext, color=VM,  lw=1.6, ls="-.",
                label=f"Gaiola externa ($R={R2_ext}\\,\\Omega$, $X={X2_ext}\\,\\Omega$)",
                zorder=4)
        ax.plot(n_range, T_int, color=AZ,  lw=1.6, ls=":",
                label=f"Gaiola interna ($R={R2_int}\\,\\Omega$, $X={X2_int}\\,\\Omega$)",
                zorder=4)
        ax.plot(n_range, T_dup, color=VD,  lw=2.6, ls="-",
                label="Gaiola dupla (resultante)", zorder=5)

        ax.axvline(ns, color=AZ, lw=1.0, ls="--", alpha=0.5)
        ax.axhline(0,  color=CZ, lw=0.7)
        ax.set_xlabel("Velocidade $n$ (rpm)", fontsize=11, color=TX)
        ax.set_ylabel("Torque $T$ (N·m)", fontsize=11, color=TX)
        ax.set_title("Motor com Gaiola de Esquilo Dupla",
                     fontsize=11, fontweight="bold", color=TX)
        ax.legend(fontsize=8.0, framealpha=0.0, loc="upper left")
        ax.set_xlim(-50, ns + 80)
        ax.grid(True, alpha=0.18, linestyle="--", color=CZ)
        fig.tight_layout()
        return fig

    # ════════════════════════════════════════════════════════════════════════
    # CIRCUITOS EQUIVALENTES — schemdraw → PNG → matplotlib
    # ════════════════════════════════════════════════════════════════════════

    def fig_circuito_completo():
        """Circuito equivalente completo (por fase): R1, X1, Rc, Xm, X'2, R'2/s."""
        with schemdraw.Drawing() as d:
            d.config(unit=2)
            d.push()
            elm.Line().right(d.unit * 0.25)
            X2_e = elm.Inductor().right().label("$jX'_2$")
            I2_e = elm.Line().right(d.unit * 0.5)
            elm.Line().down(d.unit * 0.375)
            R2_e = elm.ResistorVar().down().label(r"$\dfrac{R'_2}{s}$", loc="bottom")
            elm.Line().down(d.unit * 0.375)
            elm.Line().left(d.unit * 0.5)
            elm.Line().left(d.unit * 1.25).dot(open=False)
            elm.Line().left(d.unit * 1.25)
            elm.Line().left()
            elm.Line().left(d.unit * 0.5).dot(open=True)
            elm.Gap().up(d.unit * 1.75).label(("-", "$V_1$", "+")).dot(open=True)
            V1p = elm.Line().right(d.unit * 0.5)
            elm.Resistor().right().label("$R_1$")
            elm.Inductor().right().label("$jX_1$")
            elm.Line().right(d.unit * 0.25).dot(open=False)
            d.pop()
            d.push()
            Ifi = elm.Line().down(d.unit * 0.5).dot(open=False)
            elm.Line().right(d.unit * 0.25)
            Xm_e = elm.Inductor().down().label("$jX_m$", loc="bottom")
            elm.Line().left(d.unit * 0.25).dot(open=False)
            elm.Line().down(d.unit * 0.25)
            d.pop()
            d.push()
            d.move(dx=0, dy=-0.5 * d.unit)
            elm.Line().left(d.unit * 0.25)
            Rc_e = elm.Resistor().down().label("$R_c$")
            elm.Line().right(d.unit * 0.25)
            d.pop()
            elm.CurrentLabel(top=True,  length=1,    ofst=.30).at(V1p).label("$I_1$")
            elm.CurrentLabel(top=True,  length=1,    ofst=.30).at(I2_e).label(r"$I'_2$")
            elm.CurrentLabel(top=True,  length=0.75, ofst=.30).at(Ifi).label(r"$I_\phi$")
            elm.CurrentLabel(top=False, length=0.75, ofst=.75).at(Rc_e).label("$I_c$")
            elm.CurrentLabel(top=False, length=0.75, ofst=-1.25).at(Xm_e).label("$I_m$", loc="bottom")
            d.save("/tmp/_mei_completo.png", dpi=140)
        fig, ax2 = plt.subplots(figsize=(7.2, 3.2))
        fig.patch.set_alpha(0); ax2.set_facecolor("none"); ax2.axis("off")
        ax2.imshow(plt.imread("/tmp/_mei_completo.png"))
        plt.close("all")
        return fig

    def fig_circuito_ieee():
        """Circuito equivalente IEEE simplificado: sem Rc, Xm como único ramo shunt."""
        with schemdraw.Drawing() as d:
            d.config(unit=2)
            d.push()
            elm.Line().right(d.unit * 0.25)
            elm.Inductor().right().label("$jX'_2$")
            I2_e = elm.Line().right(d.unit * 0.5)
            elm.Line().down(d.unit * 0.375)
            elm.ResistorVar().down().label(r"$\dfrac{R'_2}{s}$", loc="bottom")
            elm.Line().down(d.unit * 0.375)
            elm.Line().left(d.unit * 0.5)
            elm.Line().left(d.unit * 1.25).dot(open=False)
            elm.Line().left(d.unit * 1.25)
            elm.Line().left()
            elm.Line().left(d.unit * 0.5).dot(open=True)
            elm.Gap().up(d.unit * 1.75).label(("-", "$V_1$", "+")).dot(open=True)
            V1p = elm.Line().right(d.unit * 0.5)
            elm.Resistor().right().label("$R_1$")
            elm.Inductor().right().label("$jX_1$")
            elm.Line().right(d.unit * 0.25).dot(open=False)
            d.pop()
            d.push()
            elm.Line().down(d.unit * 0.375)
            Xm_e = elm.Inductor().down().label("$jX_m$", loc="bottom")
            elm.Line().down(d.unit * 0.375)
            d.pop()
            elm.CurrentLabel(top=True,  length=1,    ofst=.30).at(V1p).label("$I_1$")
            elm.CurrentLabel(top=True,  length=1,    ofst=.30).at(I2_e).label(r"$I'_2$")
            elm.CurrentLabel(top=False, length=0.75, ofst=-1.25).at(Xm_e).label("$I_m$", loc="bottom")
            d.save("/tmp/_mei_ieee.png", dpi=140)
        fig, ax2 = plt.subplots(figsize=(7.0, 3.0))
        fig.patch.set_alpha(0); ax2.set_facecolor("none"); ax2.axis("off")
        ax2.imshow(plt.imread("/tmp/_mei_ieee.png"))
        plt.close("all")
        return fig

    def fig_circuito_thevenin():
        """Circuito equivalente de Thévenin: Vth, Rth, Xth + R'2/s, X'2."""
        with schemdraw.Drawing() as d:
            d.config(unit=2)
            d.push()
            elm.Line().right(d.unit * 0.25)
            elm.Inductor().right().label("$jX'_2$")
            elm.Line().right(d.unit * 0.5)
            elm.Line().down(d.unit * 0.375)
            elm.ResistorVar().down().label(r"$\dfrac{R'_2}{s}$", loc="bottom")
            elm.Line().down(d.unit * 0.375)
            elm.Line().left(d.unit * 0.5)
            elm.Line().left(d.unit * 1.25)
            elm.Line().left(d.unit * 1.25)
            elm.Line().left()
            elm.Line().left(d.unit * 0.5).dot(open=True)
            elm.Gap().up(d.unit * 1.75).label(("-", "$V_{th}$", "+")).dot(open=True)
            V1p = elm.Line().right(d.unit * 0.5)
            elm.Resistor().right().label("$R_{th}$")
            elm.Inductor().right().label("$jX_{th}$")
            elm.Line().right(d.unit * 0.25)
            d.pop()
            elm.CurrentLabel(top=True, length=1, ofst=.30).at(V1p).label("$I'_2$")
            d.save("/tmp/_mei_thevenin.png", dpi=140)
        fig, ax2 = plt.subplots(figsize=(6.5, 3.0))
        fig.patch.set_alpha(0); ax2.set_facecolor("none"); ax2.axis("off")
        ax2.imshow(plt.imread("/tmp/_mei_thevenin.png"))
        plt.close("all")
        return fig

    def _fluxo_base(titulo, etapas, perdas, sentido="→"):
        """
        Desenha um diagrama de fluxo de potência genérico.
        etapas: lista de (x, label, cor) para os nós do fluxo principal
        perdas: lista de (x, label, cor, descr) para perdas (setas para baixo)
        sentido: "→" motor/frenagem, "←" gerador
        """
        fig, ax = plt.subplots(figsize=(10, 3.8))
        fig.patch.set_alpha(0); ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(0, 11); ax.set_ylim(-2.8, 2.6)

        y0 = 0.6  # linha do fluxo principal

        # Setas do fluxo principal
        xs_nos = [e[0] for e in etapas]
        for i in range(len(xs_nos) - 1):
            ax.annotate("",
                        xy   =(xs_nos[i+1] - 0.12, y0),
                        xytext=(xs_nos[i]  + 0.12, y0),
                        arrowprops=dict(arrowstyle="-|>", color=TX, lw=2.2))

        # Labels dos nós
        for x, lbl, cor in etapas:
            ax.text(x, y0 + 0.42, lbl, ha="center", fontsize=10.5,
                    color=cor, fontweight="bold")

        # Perdas (setas para baixo)
        for xp, lbl, cor, descr in perdas:
            ax.annotate("",
                        xy   =(xp, -0.80),
                        xytext=(xp, y0 - 0.10),
                        arrowprops=dict(arrowstyle="-|>", color=cor, lw=1.8))
            ax.text(xp, -1.00, lbl,   ha="center", fontsize=9.5,
                    color=cor, fontweight="bold", va="top")
            ax.text(xp, -1.60, descr, ha="center", fontsize=8.0,
                    color=CZ, style="italic", va="top")

        ax.set_title(titulo, fontsize=12, fontweight="bold", color=TX, pad=6)
        fig.tight_layout()
        return fig

    def fig_fluxo_potencia_motor():
        """Diagrama de fluxo de potência — motor de indução."""
        etapas = [
            (0.7,  "$P_{in}$\n(elétrica)",  AZ),
            (3.2,  "$P_{ag}$\n(entreferro)", CI),
            (7.2,  "$P_{mec}$\n(mecânica\ndesenv.)", VD),
            (10.3, "$P_{out}$\n(eixo)", VD),
        ]
        perdas = [
            (1.95, "$P_{cu,1}$", VM, "Cobre / Estator"),
            (3.20, "$P_{fe}$",   LR, "Ferro / Núcleo"),   # coincide com P_ag mas abaixo
            (5.20, "$P_{cu,2}$", VM, "Cobre / Rotor"),
            (8.75, "$P_{rot}$",  LR, "Atrito e\nVentilação"),
        ]
        # posição das perdas ajustada para não coincidir com nós
        perdas = [
            (1.95, "$P_{cu,1}$", VM, "Cobre / Estator"),
            (3.95, "$P_{fe}$",   LR, "Ferro / Núcleo"),
            (5.20, "$P_{cu,2}$", VM, "Cobre / Rotor"),
            (8.75, "$P_{rot}$",  LR, "Atrito /\nVentilação"),
        ]
        fig = _fluxo_base("Fluxo de Potência — Motor de Indução",
                           etapas, perdas)
        # Linha divisória elétrico/mecânico
        ax = fig.axes[0]
        ax.axvline(6.2, color=CZ, lw=0.9, ls=":", alpha=0.6)
        ax.text(6.2, 2.2, "← Elétrico  |  Mecânico →",
                ha="center", fontsize=8, color=CZ, style="italic")
        return fig

    def fig_fluxo_potencia_gerador():
        """Diagrama de fluxo de potência — gerador de indução."""
        etapas = [
            (0.7,  "$P_{in}$\n(mecânica\nno eixo)", VD),
            (3.8,  "$P_{ag}$\n(entreferro)", CI),
            (7.2,  "$P_{ele}$\n(elétrica\nconvert.)", AZ),
            (10.3, "$P_{out}$\n(terminal)", AZ),
        ]
        perdas = [
            (2.25, "$P_{rot}$",  LR, "Atrito /\nVentilação"),
            (3.80, "$P_{fe}$",   LR, "Ferro / Núcleo"),
            (5.50, "$P_{cu,2}$", VM, "Cobre / Rotor"),
            (8.75, "$P_{cu,1}$", VM, "Cobre / Estator"),
        ]
        fig = _fluxo_base("Fluxo de Potência — Gerador de Indução",
                           etapas, perdas)
        ax = fig.axes[0]
        ax.axvline(6.4, color=CZ, lw=0.9, ls=":", alpha=0.6)
        ax.text(6.4, 2.2, "← Mecânico  |  Elétrico →",
                ha="center", fontsize=8, color=CZ, style="italic")
        return fig

    def fig_fluxo_potencia_frenagem():
        """Diagrama de fluxo de potência — frenagem por inversão de fase."""
        # Na frenagem: Pin (elétrica) entra + P_eixo (mecânica) entra → tudo dissipado no rotor
        fig, ax = plt.subplots(figsize=(10, 3.8))
        fig.patch.set_alpha(0); ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(0, 11); ax.set_ylim(-2.8, 2.6)

        y0 = 0.6

        # Fluxo elétrico (esquerda → centro)
        ax.annotate("", xy=(4.8, y0), xytext=(0.6, y0),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=2.2))
        ax.text(0.6, y0+0.42, "$P_{terminal}$\n(elétrica)", ha="center",
                fontsize=10, color=AZ, fontweight="bold")

        # Fluxo mecânico (direita → centro)
        ax.annotate("", xy=(5.2, y0), xytext=(10.4, y0),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=2.2))
        ax.text(10.4, y0+0.42, "$P_{eixo}$\n(mecânica)", ha="center",
                fontsize=10, color=VD, fontweight="bold")

        # Nó central (potência de entreferro — soma das duas entradas)
        ax.add_patch(mpatches.FancyBboxPatch(
            (4.55, y0-0.30), 0.90, 0.60,
            boxstyle="round,pad=0.05",
            fc="#fff5e0", ec=LR, lw=1.5, zorder=4))
        ax.text(5.0, y0, "$P_{ag}$", ha="center", fontsize=10.5,
                color=LR, fontweight="bold", zorder=5)

        # Perdas para baixo (todas dissipadas)
        perdas_f = [
            (1.8,  "$P_{cu,1}$", VM, "Cobre / Estator"),
            (5.00, "$P_{cu,2}$", VM, "Cobre / Rotor\n(dominante)"),
            (8.6,  "$P_{rot}$",  LR, "Atrito /\nVentilação"),
        ]
        for xp, lbl, cor, descr in perdas_f:
            ax.annotate("", xy=(xp, -0.80), xytext=(xp, y0-0.10),
                        arrowprops=dict(arrowstyle="-|>", color=cor, lw=1.8))
            ax.text(xp, -1.00, lbl,   ha="center", fontsize=9.5,
                    color=cor, fontweight="bold", va="top")
            ax.text(xp, -1.60, descr, ha="center", fontsize=8.0,
                    color=CZ, style="italic", va="top")

        # Nota
        ax.text(5.0, 2.1,
                "Frenagem: $s > 1$  — toda a energia (elétrica + mecânica) é dissipada no rotor",
                ha="center", fontsize=8.5, color=TX, style="italic")

        ax.set_title("Fluxo de Potência — Frenagem (Inversão de Fase)",
                     fontsize=12, fontweight="bold", color=TX, pad=6)
        fig.tight_layout()
        return fig

    # ════════════════════════════════════════════════════════════════════════
    # EXPLORADORES PLOTLY
    # ════════════════════════════════════════════════════════════════════════

    def _T_curve(V1, R1, X1, R2, X2, Xm, ns, s_arr):
        ws = ns * 2 * np.pi / 60
        out = []
        for s in s_arr:
            s_  = s if abs(s) > 1e-4 else 1e-4
            Z2  = R2/s_ + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I2  = (V1 / (R1 + 1j*X1 + Zeq)) * Zeq / Z2
            out.append(3 * abs(I2)**2 * (R2/s_) / ws)
        return np.array(out)

    def exp_torque_velocidade():
        st.markdown("#### 🎛️ Explorador 1 — Curva Torque × Velocidade")
        col1, col2, col3 = st.columns(3)
        with col1:
            V_line = st.slider("$V_L$ (V)", 100, 600, 220, 10, key="e1_V")
            R1 = st.slider("$R_1$ (Ω)", 0.05, 2.0, 0.5, 0.05, key="e1_R1")
            X1 = st.slider("$X_1$ (Ω)", 0.10, 3.0, 1.0, 0.05, key="e1_X1")
        with col2:
            R2 = st.slider("$R'_2$ (Ω)", 0.05, 3.0, 0.4, 0.05, key="e1_R2")
            X2 = st.slider("$X'_2$ (Ω)", 0.10, 3.0, 1.0, 0.05, key="e1_X2")
            Xm = st.slider("$X_m$ (Ω)", 5.0, 100.0, 50.0, 1.0, key="e1_Xm")
        with col3:
            f  = st.selectbox("$f$ (Hz)", [50, 60], index=1, key="e1_f")
            p  = st.selectbox("Polos", [2, 4, 6, 8], index=1, key="e1_p")
            mostrar_regioes = st.checkbox("Regiões de operação", True, key="e1_reg")
            mostrar_pts     = st.checkbox("Pontos notáveis",     True, key="e1_pts")

        V1 = V_line / np.sqrt(3); ns = 120 * f / p
        s_all = np.concatenate([np.linspace(-0.8, -1e-4, 200),
                                  np.linspace( 1e-4, 2.0,  600)])
        n_all = ns * (1 - s_all)
        T_all = _T_curve(V1, R1, X1, R2, X2, Xm, ns, s_all)

        fig = go.Figure()
        if mostrar_regioes:
            for cond, col_r, nome in [
                ((n_all >= 0) & (n_all <= ns), "rgba(31,157,85,0.07)", "Motor"),
                (n_all > ns,                    "rgba(61,142,240,0.07)", "Gerador"),
                (n_all < 0,                     "rgba(224,62,62,0.07)",  "Frenagem"),
            ]:
                fig.add_trace(go.Scatter(
                    x=n_all[cond], y=T_all[cond],
                    fill="tozeroy", fillcolor=col_r,
                    line=dict(width=0), name=nome, showlegend=True))
        fig.add_trace(go.Scatter(
            x=n_all, y=T_all, mode="lines",
            line=dict(color=AZ, width=2.5), name="T(n)"))
        if mostrar_pts:
            m = (n_all >= 0) & (n_all <= ns)
            if m.any():
                T_m = T_all[m]; n_m = n_all[m]
                idx_mx = int(np.argmax(T_m))
                T_pt = _T_curve(V1,R1,X1,R2,X2,Xm,ns,[1.0])[0]
                fig.add_trace(go.Scatter(
                    x=[0, n_m[idx_mx], ns], y=[T_pt, T_m[idx_mx], 0],
                    mode="markers+text",
                    marker=dict(color=[VM, LR, AZ], size=10,
                                symbol=["square","triangle-up","diamond"]),
                    text=["T_part","T_max","nₛ"], textposition="top center",
                    name="Pontos notáveis"))
        fig.add_hline(y=0, line=dict(color=CZ, width=0.8))
        fig.add_vline(x=ns, line=dict(color=AZ, width=1.0, dash="dash"))
        fig.update_layout(
            xaxis_title="Velocidade n (rpm)",
            yaxis_title="Torque T (N·m)",
            title=f"T × n   nₛ = {ns:.0f} rpm  |  V₁ = {V1:.1f} V",
            legend=dict(orientation="h", y=-0.22))
        show_plot(fig, key="exp1_tv", height=420)

    def exp_circuito_equivalente():
        st.markdown("#### 🎛️ Explorador 2 — Ponto de Operação no Circuito Equivalente")
        col1, col2 = st.columns(2)
        with col1:
            V_line = st.number_input("$V_L$ (V)", 100.0, 15000.0, 460.0, 10.0, key="e2_V")
            f  = st.selectbox("$f$ (Hz)", [50, 60], index=1, key="e2_f")
            p  = st.selectbox("Polos", [2, 4, 6, 8], index=1, key="e2_p")
            s  = st.slider("Escorregamento $s$", 0.001, 0.99, 0.05, 0.001,
                           key="e2_s", format="%.3f")
        with col2:
            R1 = st.number_input("$R_1$ (Ω)", 0.01, 10.0, 0.5, 0.01, format="%.3f", key="e2_R1")
            X1 = st.number_input("$X_1$ (Ω)", 0.01, 20.0, 1.0, 0.01, format="%.3f", key="e2_X1")
            R2 = st.number_input("$R'_2$ (Ω)",0.01, 10.0, 0.4, 0.01, format="%.3f", key="e2_R2")
            X2 = st.number_input("$X'_2$ (Ω)",0.01, 20.0, 1.0, 0.01, format="%.3f", key="e2_X2")
            Xm = st.number_input("$X_m$ (Ω)", 1.0, 500.0, 50.0, 1.0, format="%.1f", key="e2_Xm")

        V1 = V_line / np.sqrt(3); ns = 120*f/p; ws = ns * 2*np.pi/60
        Z2  = R2/s + 1j*X2
        Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
        I1  = V1 / (R1 + 1j*X1 + Zeq)
        I2  = (I1 * Zeq) / Z2
        Pag = 3 * abs(I2)**2 * (R2/s)
        Pin = 3 * V1 * abs(I1) * np.cos(np.angle(I1))
        Pcu1= 3 * abs(I1)**2 * R1
        Pcu2= s * Pag; Pmec = (1-s)*Pag
        T_em= Pag / ws; fp = np.cos(np.angle(I1))
        n   = ns * (1-s)

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("$I_1$ (A)",     f"{abs(I1):.3f}")
        c1.metric("$I'_2$ (A)",    f"{abs(I2):.3f}")
        c2.metric("$P_{in}$ (W)",  f"{Pin:.1f}")
        c2.metric("$P_{ag}$ (W)",  f"{Pag:.1f}")
        c3.metric("$P_{mec}$ (W)", f"{Pmec:.1f}")
        c3.metric("$P_{cu,2}$ (W)",f"{Pcu2:.1f}")
        c4.metric("$T_{em}$ (N·m)",f"{T_em:.3f}")
        c4.metric("$fp$",          f"{fp:.4f}")
        st.caption(f"n = {n:.1f} rpm  |  nₛ = {ns:.0f} rpm  |  s = {s:.3f}")

        fig_b = go.Figure()
        fig_b.add_trace(go.Bar(
            x=["$P_{in}$", "$P_{cu,1}$", "$P_{ag}$", "$P_{cu,2}$", "$P_{mec}$"],
            y=[Pin, Pcu1, Pag, Pcu2, Pmec],
            marker_color=[AZ, VM, CI, VM, VD]))
        fig_b.update_layout(title="Distribuição de Potências (W)",
                             yaxis_title="W", height=280)
        show_plot(fig_b, key="exp2_bar", height=280)

    def exp_efeito_tensao():
        st.markdown("#### 🎛️ Explorador 3 — Efeito da Tensão na Curva T × n")
        col1, col2 = st.columns([1, 2])
        with col1:
            f  = st.selectbox("$f$ (Hz)", [50, 60], index=1, key="e3_f")
            p  = st.selectbox("Polos", [2, 4, 6, 8], index=1, key="e3_p")
            R1 = st.slider("$R_1$ (Ω)", 0.05, 2.0, 0.5, 0.05, key="e3_R1")
            R2 = st.slider("$R'_2$ (Ω)",0.05, 2.0, 0.4, 0.05, key="e3_R2")
            X1 = st.slider("$X_1$ (Ω)", 0.1,  3.0, 1.0, 0.1,  key="e3_X1")
            X2 = st.slider("$X'_2$ (Ω)",0.1,  3.0, 1.0, 0.1,  key="e3_X2")
            Xm = st.slider("$X_m$ (Ω)", 5.0, 100.0, 50.0, 1.0, key="e3_Xm")
        ns = 120*f/p
        s_r = np.linspace(1e-3, 1.0, 500)
        n_r = ns * (1 - s_r)
        V_nom = 220 / np.sqrt(3)
        fig = go.Figure()
        for frac, cor in zip([0.70, 0.85, 1.0, 1.10], [VM, LR, AZ, VD]):
            V1 = frac * V_nom
            T  = _T_curve(V1, R1, X1, R2, X2, Xm, ns, s_r)
            fig.add_trace(go.Scatter(
                x=n_r, y=T, mode="lines",
                line=dict(color=cor, width=2.0),
                name=f"{frac*100:.0f}% V_nom"))
        fig.add_vline(x=ns, line=dict(color=AZ, dash="dash", width=1.0))
        fig.update_layout(
            xaxis_title="n (rpm)", yaxis_title="T (N·m)",
            title="T ∝ V² — efeito da tensão terminal na curva T × n",
            legend=dict(orientation="h", y=-0.22))
        show_plot(fig, key="exp3_etv", height=400)

    def exp_partida():
        st.markdown("#### 🎛️ Explorador 4 — Métodos de Partida")
        col1, col2 = st.columns(2)
        with col1:
            Ifn  = st.slider("$I_{part}/I_{nom}$ (partida direta)", 3.0, 8.0, 6.0, 0.5, key="e4_I")
            Tfn  = st.slider("$T_{part}/T_{nom}$ (partida direta)", 0.5, 2.5, 1.5, 0.1, key="e4_T")
        with col2:
            alfa = st.slider("Razão autotransf. $\\alpha$", 0.40, 0.95, 0.65, 0.05, key="e4_a")

        k_yd = 3.0
        metodos = {
            "DOL (direta)":                  (Ifn,              Tfn),
            "Y / Δ":                         (Ifn / k_yd,       Tfn / k_yd),
            f"Autotransf. α={alfa:.2f}":     (alfa**2 * Ifn,    alfa**2 * Tfn),
            "Resist. série (50 %)":          (0.50 * Ifn,       0.25 * Tfn),
        }
        nomes = list(metodos.keys())
        Is = [v[0] for v in metodos.values()]
        Ts = [v[1] for v in metodos.values()]
        cores_b = [VM, LR, AZ, VD]

        fig = make_subplots(rows=1, cols=2,
                             subplot_titles=["Corrente de partida (× Inom)",
                                             "Torque de partida (× Tnom)"])
        fig.add_trace(go.Bar(x=nomes, y=Is, marker_color=cores_b,
                              showlegend=False), row=1, col=1)
        fig.add_trace(go.Bar(x=nomes, y=Ts, marker_color=cores_b,
                              showlegend=False), row=1, col=2)
        fig.add_hline(y=1.0, line=dict(color=CZ, dash="dash"), row=1, col=1)
        fig.add_hline(y=1.0, line=dict(color=CZ, dash="dash"), row=1, col=2)
        fig.update_layout(height=370, title="Comparação dos Métodos de Partida")
        show_plot(fig, key="exp4_part", height=370)

    def exp_eficiencia():
        st.markdown("#### 🎛️ Explorador 5 — Eficiência × Carga")
        col1, col2 = st.columns(2)
        with col1:
            V_line  = st.number_input("$V_L$ (V)", 100.0, 15000.0, 460.0, key="e5_V")
            f       = st.selectbox("$f$ (Hz)", [50, 60], index=1, key="e5_f")
            p       = st.selectbox("Polos", [2, 4, 6, 8], index=1, key="e5_p")
        with col2:
            R1 = st.number_input("$R_1$ (Ω)", 0.001, 5.0, 0.07,  0.001, format="%.4f", key="e5_R1")
            R2 = st.number_input("$R'_2$ (Ω)",0.001, 5.0, 0.152, 0.001, format="%.4f", key="e5_R2")
            X1 = st.number_input("$X_1$ (Ω)", 0.01, 20.0, 0.743, 0.001, format="%.3f", key="e5_X1")
            X2 = st.number_input("$X'_2$ (Ω)",0.01, 20.0, 0.764, 0.001, format="%.3f", key="e5_X2")
            Xm = st.number_input("$X_m$ (Ω)", 1.0, 500.0, 40.1,  0.1,   format="%.1f", key="e5_Xm")

        Prot  = st.slider("$P_{rot}$ (W)", 0, 5000, 390,  10, key="e5_Prot")
        Pfe   = st.slider("$P_{fe}$ (W)",  0, 5000, 325,  10, key="e5_Pfe")

        V1 = V_line / np.sqrt(3); ns = 120*f/p; ws = ns * 2*np.pi/60
        s_arr = np.linspace(0.003, 0.50, 400)
        n_arr = ns * (1 - s_arr)
        efic = []; Pout = []

        for s in s_arr:
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I1  = V1 / (R1 + 1j*X1 + Zeq)
            I2  = (I1 * Zeq) / Z2
            Pag = 3 * abs(I2)**2 * (R2/s)
            Pin = 3 * V1 * abs(I1) * np.cos(np.angle(I1)) + Pfe
            po  = max(0.0, Pag*(1-s) - Prot)
            efic.append(max(0.0, po/Pin*100) if Pin > 0 else 0)
            Pout.append(po)

        fig = make_subplots(rows=1, cols=2,
                             subplot_titles=["Eficiência η (%)", "Pot. de saída (W)"])
        fig.add_trace(go.Scatter(x=n_arr, y=efic, mode="lines",
                                  line=dict(color=AZ, width=2.2), name="η (%)"),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=n_arr, y=Pout, mode="lines",
                                  line=dict(color=VD, width=2.0), name="P_out (W)"),
                      row=1, col=2)
        fig.update_xaxes(title_text="n (rpm)")
        fig.update_layout(height=360, legend=dict(orientation="h", y=-0.22))
        show_plot(fig, key="exp5_ef", height=360)

    # ════════════════════════════════════════════════════════════════════════
    # LAYOUT PRINCIPAL
    # ════════════════════════════════════════════════════════════════════════

    # ── Cabeçalho ─────────────────────────────────────────────────────────
    st.title("🌀 Máquinas de Indução Polifásica")
    st.caption("⚡ SINTONIA · Máquinas Elétricas · 👤 Marcus V A Fernandes · ✉️ marcus.fernandes@ifrn.edu.br")
    st.markdown("---")

    # ── Índice ─────────────────────────────────────────────────────────────
    with st.expander("📋 Índice — clique para expandir", expanded=False):
        st.markdown("""
**[1. Conceitos Elementares e Aplicações](#1-conceitos-elementares-e-aplicacoes)**

**[2. Estrutura Construtiva — Estator e Rotor](#2-estrutura-construtiva-estator-e-rotor)**

**[3. Campo Magnético Girante](#3-campo-magnetico-girante)**
- Composição vetorial das FMM · Velocidade síncrona

**[4. Escorregamento](#4-escorregamento)**
- Definição · Faixas de operação

**[5. Tensão Induzida — Estator e Rotor](#5-tensao-induzida-estator-e-rotor)**
- Equação do estator · Er = s·Er0 · fr = s·f

**[6. Circuito Equivalente (por fase)](#6-circuito-equivalente-por-fase)**
- Circuito completo · Modelo IEEE · Equivalente de Thévenin

**[7. Fluxo de Potência e Balanço de Energia](#7-fluxo-de-potencia-e-balanco-de-energia)**
- Tabela de grandezas · Diagramas motor e gerador

**[8. Torque Eletromagnético](#8-torque-eletromagnetico)**
- Expressão analítica · Torque máximo · Escorregamento crítico

**[9. Modos de Operação](#9-modos-de-operacao)**
- Motor · Gerador · Frenagem · Modo invertido

**[10. Curva Característica T × n](#10-curva-caracteristica-t-n)**
- Pontos notáveis · Região estável

**[11. Métodos de Partida](#11-metodos-de-partida)**
- DOL · Y/Δ · Autotransformador · Resistência no rotor · Inversor (VFD)

**[12. Gaiola de Esquilo Dupla](#12-gaiola-de-esquilo-dupla)**
- Efeito pelicular · Curvas de torque

**[🎛️ Exploradores Interativos](#exploradores-interativos)**
- T × n · Circuito equivalente · Efeito da tensão · Métodos de partida · Eficiência

**Referências** (ao final da página)
""")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 1
    # ═══════════════════════════════════════════════════════════════════════
    st.header("1. Conceitos Elementares e Aplicações")
    st.markdown(r"""
A **máquina de indução polifásica** (MIT) é a mais empregada na indústria, tanto pelo baixo
custo quanto pela robustez e simplicidade construtiva. Ao contrário das máquinas CC, em que o
campo e a armadura são alimentados separadamente, na MIT *ambos* os enrolamentos — estator e
rotor — operam com corrente alternada.

O aspecto central que dá nome à máquina é o **princípio da indução**: a tensão no rotor é
induzida pelo campo girante do estator, exatamente como no secundário de um transformador.
Por esse motivo Chapman a descreve como "transformador com entreferro e secundário girante".

| Porte | Exemplos de aplicação |
|---|---|
| Grande (> 100 kW) | Bombas, ventiladores industriais, compressores, moinhos, papel e celulose |
| Médio (1–100 kW) | Máquinas CNC, transportadores, bombas hidráulicas |
| Pequeno (< 1 kW) | Liquidificadores, máquinas de lavar, refrigeradores, espremedores |

A operação como **gerador** — com escorregamento negativo — é aplicada principalmente em
turbinas eólicas e pequenas centrais hidrelétricas de velocidade aproximadamente constante.
""")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 2
    # ═══════════════════════════════════════════════════════════════════════
    st.header("2. Estrutura Construtiva — Estator e Rotor")
    st.markdown(r"""
### Estator

O **estator** é formado por um núcleo laminado de aço silício, provido de ranhuras onde são
instalados os enrolamentos trifásicos. As bobinas das três fases são distribuídas com
defasagem de 120° elétricos, de forma a produzir um campo resultante girante de amplitude
constante.

### Tipos de Rotor
""")

    show_fig(fig_rotor_bobinado(), width_frac=0.85)
    st.caption("**Figura 2.1** — Rotor gaiola de esquilo (esquerda) e rotor bobinado (direita).")

    st.markdown(r"""
**Rotor gaiola de esquilo** (*squirrel-cage*): barras condutoras de alumínio (ou cobre)
dispostas paralelamente ao eixo, curto-circuitadas pelas duas extremidades por anéis terminais
sólidos. É o tipo mais simples, econômico e robusto — dominante na indústria.

**Rotor bobinado** (*wound rotor*): enrolamento trifásico isolado com terminais acessíveis
pelos anéis coletores. Permite inserção de resistências externas no rotor para controle de
corrente de partida e ajuste de velocidade — porém com maior custo e manutenção.
""")

    show_fig(fig_secao_transversal_mei(), width_frac=0.58)
    st.caption("**Figura 2.2** — Seção transversal idealizada (2 polos): estator laminado com "
               "enrolamentos trifásicos e rotor gaiola de esquilo.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 3
    # ═══════════════════════════════════════════════════════════════════════
    st.header("3. Campo Magnético Girante")
    st.markdown(r"""
Quando as três fases do estator são alimentadas por um sistema trifásico equilibrado, cada
enrolamento produz uma FMM pulsante ao longo do seu eixo magnético, defasadas 120° no tempo.
A superposição das três FMM resulta em um **campo resultante de amplitude constante que gira
uniformemente no espaço**.

Analiticamente, as distribuições de campo das três fases ao longo do entreferro são:

$$H_a(\theta, t) = H_m\cos(\omega t)\cos\theta$$
$$H_b(\theta, t) = H_m\cos\!\left(\omega t - \tfrac{2\pi}{3}\right)\cos\!\left(\theta - \tfrac{2\pi}{3}\right)$$
$$H_c(\theta, t) = H_m\cos\!\left(\omega t - \tfrac{4\pi}{3}\right)\cos\!\left(\theta - \tfrac{4\pi}{3}\right)$$

A resultante é:

$$H_{res}(\theta, t) = H_a + H_b + H_c = \frac{3}{2}H_m\cos(\theta - \omega t)$$

O argumento $(\theta - \omega t) = \mathrm{const}$ confirma que o pico do campo percorre o
entreferro com velocidade angular $\omega$ rad/s — o **campo girante**.
""")

    show_fig(fig_campo_girante(), width_frac=0.95)
    st.caption("**Figura 3.1** — Composição vetorial das FMM em 4 instantes. "
               "O vetor resultante $H_r$ (preto) mantém amplitude $\\frac{3}{2}H_m$ e gira.")

    st.markdown(r"""
### Velocidade Síncrona

A velocidade de rotação do campo, a **velocidade síncrona** $n_s$, é:

$$\boxed{n_s = \frac{120\,f}{p} \quad \text{(rpm)}} \qquad \omega_s = \frac{2\pi n_s}{60} \quad \text{(rad/s)}$$

onde $f$ é a frequência da rede (Hz) e $p$ é o número de polos da máquina.
""")

    show_fig(fig_velocidade_sincrona(), width_frac=0.68)
    st.caption("**Figura 3.2** — Velocidade síncrona para $f = 50$ e $60$ Hz.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 4
    # ═══════════════════════════════════════════════════════════════════════
    st.header("4. Escorregamento")
    st.markdown(r"""
O campo girante induz tensões no rotor, que produzem correntes e, portanto, um torque que
acelera o rotor na direção do campo. Em regime permanente como motor, o rotor gira a uma
velocidade $n$ **ligeiramente inferior** a $n_s$ — se $n = n_s$ não haveria variação de fluxo,
logo nenhum torque. A diferença relativa é o **escorregamento**:

$$\boxed{s = \frac{n_s - n}{n_s}} \qquad n = n_s(1 - s)$$

| Condição | $s$ | $n$ |
|---|---|---|
| Rotor parado (partida) | $s = 1$ | $n = 0$ |
| Operação nominal (motor) | $1\% \lesssim s \lesssim 10\%$ | $n \lesssim n_s$ |
| Velocidade síncrona (sem torque) | $s = 0$ | $n = n_s$ |
| Gerador | $s < 0$ | $n > n_s$ |
| Frenagem (fase invertida) | $s > 1$ | $n < 0$ |
""")

    show_fig(fig_escorregamento_def(), width_frac=0.58)
    st.caption("**Figura 4.1** — Relação entre $n_s$, $n$ e o escorregamento $s$.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 5
    # ═══════════════════════════════════════════════════════════════════════
    st.header("5. Tensão Induzida — Estator e Rotor")
    st.markdown(r"""
### Tensão no Estator

Análoga ao transformador, a tensão eficaz induzida por fase no estator é:

$$\boxed{E_A = 4{,}44 \cdot K_w \cdot N_{ph} \cdot f \cdot \Phi_m}$$

- $K_w$: fator de enrolamento ($0{,}85 \leq K_w \leq 0{,}95$) — corrige o efeito da
  distribuição das bobinas nas ranhuras e do passo fracionário;
- $N_{ph}$: número de espiras em série por fase;
- $\Phi_m$: fluxo máximo por polo.
""")

    show_fig(fig_tensao_induzida_estator(), width_frac=0.72)
    st.caption("**Figura 5.1** — Forma de onda de $e(t)$ e equação do valor eficaz $E_A$.")

    st.markdown(r"""
### Tensão no Rotor

Com o rotor **estacionário** ($s = 1$): $E_{r0} = (N_r/N_s)\,E_A$, com $f_{r0} = f$.

Com o rotor **girando** com escorregamento $s$:

$$\boxed{E_r = s \cdot E_{r0}} \qquad \boxed{f_r = s \cdot f}$$

A reatância de dispersão do rotor também escala: $X_r = s\,X_{r0}$,
onde $X_{r0} = 2\pi f L_r$.
""")

    show_fig(fig_tensao_rotor_escorregamento(), width_frac=0.82)
    st.caption("**Figura 5.2** — Variação de $E_r$ (esq.) e $f_r$ (dir.) com o escorregamento $s$.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 6
    # ═══════════════════════════════════════════════════════════════════════
    st.header("6. Circuito Equivalente (por fase)")
    st.markdown(r"""
A MIT é modelada por um **circuito monofásico equivalente** semelhante ao do transformador,
porém com uma resistência variável no ramo do rotor que captura a conversão eletromecânica.

### Circuito Completo

Inclui: ramo série do estator ($R_1 + jX_1$), ramo de excitação em paralelo
($R_c \parallel jX_m$) e ramo do rotor referido ($jX'_2 + R'_2/s$).
""")

    show_fig(fig_circuito_completo(), width_frac=0.82)
    st.caption("**Figura 6.1** — Circuito equivalente completo com $R_c$, $X_m$, "
               "$R_1$, $X_1$, $R'_2/s$ e $X'_2$.")

    st.markdown(r"""
A resistência $R'_2/s$ é decomposta como:

$$\frac{R'_2}{s} = R'_2 + R'_2\frac{1-s}{s}$$

onde $R'_2$ representa as perdas Joule no rotor e $R'_2(1-s)/s$ é a **resistência de carga**
equivalente à potência mecânica convertida.

### Circuito IEEE Simplificado

Quando $R_c$ é omitido, o modelo IEEE move $X_m$ para os terminais de entrada:
""")

    show_fig(fig_circuito_ieee(), width_frac=0.78)
    st.caption("**Figura 6.2** — Circuito equivalente IEEE simplificado (sem $R_c$).")

    st.markdown("### Equivalente de Thévenin")
    st.markdown(
        "Para facilitar o cálculo analítico do torque, o circuito à esquerda do ramo "
        "do rotor é substituído pelo seu equivalente de Thévenin. "
        "As fórmulas simplificadas (válidas quando $R_1 \\ll X_1 + X_m$) são:"
    )
    st.latex(r"""
V_{th} \approx V_1 \frac{X_m}{X_1 + X_m}
\qquad
R_{th} \approx R_1 \left(\frac{X_m}{X_1 + X_m}\right)^{2}
\qquad
X_{th} \approx X_1
""")

    show_fig(fig_circuito_thevenin(), width_frac=0.72)
    st.caption("**Figura 6.3** — Circuito de Thévenin: $V_{th}$, $R_{th}$, $X_{th}$ "
               "em série com $R'_2/s + jX'_2$.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 7
    # ═══════════════════════════════════════════════════════════════════════
    st.header("7. Fluxo de Potência e Balanço de Energia")
    st.markdown("A conversão de energia segue uma cadeia de perdas sucessivas:")
    st.latex(r"P_{in} \xrightarrow{-P_{cu,1}} \xrightarrow{-P_{fe}} P_{ag} \xrightarrow{-P_{cu,2}} P_{mec} \xrightarrow{-P_{rot}} P_{out}")
    st.markdown(r"""
| Grandeza | Expressão | Significado |
|---|---|---|
| $P_{in}$ | $3\,V_1 I_1 \cos\varphi$ | Potência elétrica de entrada |
| $P_{cu,1}$ | $3\,R_1 I_1^2$ | Perdas Joule no estator |
| $P_{fe}$ | $3\,V_1^2/R_c$ | Perdas no ferro |
| $P_{ag}$ | $3\,(R_2'/s)\,I_2'^{\,2}$ | Potência de entreferro |
| $P_{cu,2}$ | $s\,P_{ag}$ | Perdas Joule no rotor |
| $P_{mec}$ | $(1-s)\,P_{ag}$ | Potência mecânica desenvolvida |
| $P_{rot}$ | constante | Atrito, ventilação e suplementares |
| $P_{out}$ | $P_{mec} - P_{rot}$ | Potência útil no eixo |

A relação $P_{cu,2} = s\,P_{ag}$ é fundamental: operando a $s = 5\%$, apenas $5\%$
da potência do entreferro é dissipada como calor no rotor — os outros $95\%$ são
convertidos em potência mecânica.
""")

    show_fig(fig_fluxo_potencia_motor(), width_frac=0.95)
    st.caption("**Figura 7.1** — Fluxo de potência no **motor** de indução: "
               "$P_{in}$ (elétrica) → perdas → $P_{out}$ (mecânica no eixo).")

    show_fig(fig_fluxo_potencia_gerador(), width_frac=0.95)
    st.caption("**Figura 7.2** — Fluxo de potência no **gerador** de indução: "
               "$P_{in}$ (mecânica) → perdas → $P_{out}$ (elétrica no terminal).")

    show_fig(fig_fluxo_potencia_frenagem(), width_frac=0.95)
    st.caption("**Figura 7.3** — Fluxo de potência na **frenagem** ($s > 1$): "
               "potências elétrica e mecânica convergem para o rotor e são dissipadas como calor.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 8
    # ═══════════════════════════════════════════════════════════════════════
    st.header("8. Torque Eletromagnético")
    st.markdown(
        "O torque eletromagnético é obtido da potência de entreferro "
        "dividida pela velocidade síncrona angular:"
    )
    st.latex(r"T_{em} = \frac{P_{ag}}{\omega_s} = \frac{3\,I_2'^{\,2}\,(R_2'/s)}{\omega_s}")
    st.markdown(
        "Usando o equivalente de Thévenin, a expressão analítica completa em função de $s$ é:"
    )
    st.latex(r"""
T_{em}(s) = \frac{3\,V_{th}^2\,(R_2'/s)}
            {\omega_s \left[(R_{th} + R_2'/s)^2 + (X_{th}+X_2')^2\right]}
""")
    st.markdown("### Torque Máximo (Pull-out)")
    st.markdown(
        "O torque máximo $T_{max}$ (torque de pull-out) ocorre no escorregamento crítico $s_{max}$:"
    )
    st.latex(r"s_{max} = \frac{R_2'}{\sqrt{R_{th}^2 + (X_{th}+X_2')^2}}")
    st.latex(r"T_{max} = \frac{3\,V_{th}^2}{2\,\omega_s \left[R_{th} + \sqrt{R_{th}^2+(X_{th}+X_2')^2}\right]}")
    st.markdown(r"""
Note que $T_{max}$ **independe de $R_2'$**, enquanto o escorregamento crítico $s_{max}$ é
diretamente proporcional a $R_2'$. Ao inserir resistência externa no rotor bobinado,
desloca-se $s_{max}$ para 1 (torque máximo na partida) sem alterar o valor de $T_{max}$.
""")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 9
    # ═══════════════════════════════════════════════════════════════════════
    st.header("9. Modos de Operação")
    st.markdown(r"""
A MIT pode operar em três regiões distintas segundo o escorregamento:

### Motor ($0 < s < 1$)
O estator é alimentado e o rotor gira na direção do campo com $n < n_s$.
Potência elétrica entra pelo estator e é convertida em potência mecânica. Uso mais frequente.

### Gerador ($s < 0$)
O rotor é acionado mecanicamente com $n > n_s$. O fluxo relativo inverte,
invertendo o sentido do torque — a máquina devolve potência à rede.
Aplicação: turbinas eólicas conectadas diretamente à rede.

### Frenagem ($s > 1$)
O rotor gira no sentido oposto ao campo ($n < 0$, obtido pela inversão de fase).
Tanto a potência elétrica quanto a mecânica são dissipadas como calor no rotor.
Utilizado em frenagem rápida de cargas de alta inércia.

### Modo Invertido
Em rotores bobinados, alimentando o rotor pelos anéis coletores com o estator em curto,
o motor gira no sentido **oposto** ao campo do estator.
""")

    show_fig(fig_modos_operacao(), width_frac=0.78)
    st.caption("**Figura 9.1** — Curva $T \\times n$ nas três regiões: "
               "motor (verde), gerador (azul) e frenagem (vermelho).")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 10
    # ═══════════════════════════════════════════════════════════════════════
    st.header("10. Curva Característica T × n")
    st.markdown(r"""
A curva $T \times n$ na região motora possui pontos notáveis que definem as capacidades
de partida e operação:

| Ponto | Símbolo | Condição |
|---|---|---|
| Torque de partida | $T_{part}$ | $s = 1$, $n = 0$ |
| Torque máximo | $T_{max}$ | $s = s_{max}$ |
| Torque nominal | $T_{nom}$ | $s_{nom} \approx 1\text{–}10\%$ |
| Velocidade síncrona | $n_s$ | $T = 0$, $s = 0$ |

A operação **estável** ocorre à direita do $T_{max}$ (baixo $s$): qualquer aumento de carga
aumenta $s$, aumenta $T_{em}$ e reequilibra o sistema. À esquerda do $T_{max}$ (alto $s$)
a operação é instável — aumento de carga reduz $T_{em}$.
""")

    show_fig(fig_curva_torque_velocidade(), width_frac=0.75)
    st.caption("**Figura 10.1** — Curva $T \\times n$ (região motora) com pontos notáveis.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 11
    # ═══════════════════════════════════════════════════════════════════════
    st.header("11. Métodos de Partida")
    st.markdown(r"""
Na partida direta (DOL), a corrente pode atingir 5 a 8 vezes a corrente nominal, causando
queda de tensão na rede e solicitação mecânica excessiva. Métodos para limitar a corrente:

### 1. Partida estrela-triângulo (Y/Δ)
Conexão em Y na partida reduz a tensão de fase por $1/\sqrt{3}$.
Corrente e torque de partida são reduzidos por um fator **3** em relação à ligação Δ direta.

### 2. Autotransformador
Aplica tensão $\alpha V_1$ ao motor ($\alpha < 1$). Corrente e torque caem por $\alpha^2$.
Mais flexível que Y/Δ.

### 3. Resistência em série no estator
Resistores inseridos em série e curto-circuitados após a aceleração. Dissipam calor.

### 4. Resistência no rotor (rotor bobinado)
Desloca $s_{max}$ para 1, maximizando o torque de partida com corrente controlada.
Resistência reduzida gradualmente até zero em plena carga.

### 5. Inversor de frequência (VFD)
Partida com frequência e tensão crescentes (relação $V/f$ constante). Mantém fluxo constante
e torque de partida elevado com corrente controlada. Método mais moderno e flexível.
""")

    show_fig(fig_curva_torque_R2(), width_frac=0.75)
    st.caption("**Figura 11.1** — Efeito de $R'_2$ crescente (rotor bobinado): "
               "$s_{max}$ se desloca para a partida sem alterar $T_{max}$.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 12
    # ═══════════════════════════════════════════════════════════════════════
    st.header("12. Gaiola de Esquilo Dupla")
    st.markdown(r"""
A **gaiola dupla** melhora a partida sem recorrer ao rotor bobinado. O rotor possui dois
conjuntos de barras concêntricos:

- **Gaiola externa**: barras de alta resistência e baixa reatância (seção pequena, posição
  próxima ao entreferro → baixa indutância de dispersão);
- **Gaiola interna**: barras de baixa resistência e alta reatância (seção grande, posição
  profunda → alta indutância de dispersão).

**Na partida** ($s \approx 1$, $f_r = f$): a alta frequência no rotor aumenta a reatância da
gaiola interna, concentrando a corrente na gaiola externa (alta $R$) → alto torque de partida.

**Em regime** ($s \ll 1$, $f_r \to 0$): ambas as reatâncias tornam-se desprezíveis; a corrente
divide-se predominantemente pela gaiola interna (baixa $R$) → baixas perdas e boa eficiência.

O mecanismo físico subjacente é o **efeito pelicular** (*skin effect*): em alta frequência,
a corrente concentra-se na superfície das barras, equivalente à gaiola externa.
""")

    show_fig(fig_gaiola_dupla(), width_frac=0.75)
    st.caption("**Figura 12.1** — Curvas $T \\times n$: gaiola dupla (verde), "
               "gaiola externa (vermelho), gaiola interna (azul) e simples de referência (cinza).")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # EXPLORADORES INTERATIVOS
    # ═══════════════════════════════════════════════════════════════════════
    st.header("🎛️ Exploradores Interativos")

    tabs = st.tabs([
        "1 — Curva T × n",
        "2 — Circ. Equivalente",
        "3 — Tensão → T × n",
        "4 — Partida",
        "5 — Eficiência",
    ])
    with tabs[0]: exp_torque_velocidade()
    with tabs[1]: exp_circuito_equivalente()
    with tabs[2]: exp_efeito_tensao()
    with tabs[3]: exp_partida()
    with tabs[4]: exp_eficiencia()

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # REFERÊNCIAS
    # ═══════════════════════════════════════════════════════════════════════
    with st.expander("Referências", expanded=False):
        st.markdown("""
- **BARBI, I.** *Teoria Fundamental do Motor de Indução*. Santa Catarina: Ed. UFSC, 1985.
- **CHAPMAN, S. J.** *Fundamentos de Máquinas Elétricas*. 5ª ed. São Paulo: McGraw-Hill, 2013.
- **JACOBINA, C.; LIMA, A. M.** *Acionamentos de Máquinas Elétricas de Alto Desempenho*. Minicurso XIV CBA, Natal, 2002.
- **KOSOW, I.** *Máquinas Elétricas e Transformadores*. 14ª reimp. São Paulo: Globo, 2000.
- **UMANS, S. D.** *Máquinas Elétricas de Fitzgerald e Kingsley*. 7ª ed. São Paulo: McGraw-Hill, 2014.
- **BIM, E.** *Máquinas Elétricas e Acionamento*. Rio de Janeiro: Campus Elsevier, 2009.
- **SEN, P. C.** *Princípios de Máquinas Elétricas e Eletrônica de Potência*. 3ª ed. Wiley, 2013.
""")

    st.divider()

    st.markdown(
        "<div style='text-align:center;color:gray;font-size:12px'>"
        "🌀 Máquinas de Indução Polifásica &nbsp;·&nbsp; ⚡ SINTONIA — Máquinas Elétricas<br>"
        "👤 Marcus V A Fernandes &nbsp;·&nbsp; 🏛️ IFRN-CNAT"
        " &nbsp;·&nbsp; 🏷️ v1.0 &nbsp;·&nbsp; 📅 2026"
        "</div>",
        unsafe_allow_html=True,
    )
