"""
🌀 Máquinas de Indução Polifásica
Disciplina: Máquinas Elétricas
Curso: Engenharia de Energia
Instituição: IFRN — Campus Natal-Central (CNAT)
Autor: Marcus V A Fernandes · marcus.fernandes@ifrn.edu.br · v1.0
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

    def fig_escorregamento_def():
        """Diagrama conceitual vertical: ns, n, n=0 com seta ns−n e equação de s."""
        fig, ax = plt.subplots(figsize=(5.8, 4.8))
        fig.patch.set_alpha(0); ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(0, 6.5); ax.set_ylim(0, 6.5)

        xv = 1.3  # posição x do eixo vertical

        # Eixo vertical de velocidade
        ax.annotate("", xy=(xv, 6.1), xytext=(xv, 0.4),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.8))
        ax.text(xv, 6.35, "$n$\n(rpm)", ha="center", fontsize=10,
                color=TX, va="bottom", fontweight="bold")

        # Três pontos notáveis
        y_ns, y_n, y_0 = 5.2, 3.7, 0.75
        ax.plot(xv, y_ns, "o", color=AZ, ms=13, zorder=5, markeredgecolor="white", markeredgewidth=1.5)
        ax.plot(xv, y_n,  "o", color=VD, ms=13, zorder=5, markeredgecolor="white", markeredgewidth=1.5)
        ax.plot(xv, y_0,  "o", color=LR, ms=13, zorder=5, markeredgecolor="white", markeredgewidth=1.5)

        # Linhas de referência horizontais curtas
        for y, cor in [(y_ns, AZ), (y_n, VD), (y_0, LR)]:
            ax.plot([xv - 0.18, xv + 0.18], [y, y], color=cor, lw=1.0)

        # Textos descritivos à direita
        ax.text(xv + 0.32, y_ns,
                r"$n_s = \dfrac{120\,f}{p}$  — velocidade síncrona",
                fontsize=10, color=AZ, va="center")
        ax.text(xv + 0.32, y_n,
                r"$n$ — velocidade do rotor  ($n < n_s$)",
                fontsize=10, color=VD, va="center")
        ax.text(xv + 0.32, y_0,
                r"$n = 0$  (rotor parado — partida)",
                fontsize=10, color=LR, va="center")

        # Seta dupla ↕ ns − n
        ax.annotate("", xy=(xv - 0.40, y_n + 0.06),
                    xytext=(xv - 0.40, y_ns - 0.06),
                    arrowprops=dict(arrowstyle="<->", color=RX, lw=2.0))
        ax.text(xv - 0.55, (y_ns + y_n) / 2, "$n_s - n$",
                ha="right", fontsize=10, color=RX, va="center", fontweight="bold")

        # Caixa da equação (quadrante direito inferior, sem sobrepor texto)
        eq_x, eq_y = 4.2, 2.4
        ax.text(eq_x, eq_y,
                r"$s = \dfrac{n_s - n}{n_s}$",
                fontsize=15, color=TX, ha="center", va="center",
                bbox=dict(fc="white", ec=CZ, lw=1.4,
                          boxstyle="round,pad=0.40", alpha=0.90))
        ax.text(eq_x, eq_y - 0.82,
                r"$0 \leq s \leq 1$ em operação motora",
                fontsize=9, color=CZ, ha="center", style="italic")

        ax.set_title("Definição de Escorregamento",
                     fontsize=12, fontweight="bold", color=TX, pad=6)
        fig.tight_layout()
        return fig

    def fig_velocidade_sincrona():
        """Velocidade síncrona ns = 120f/p — Plotly interativo."""
        polos = [2, 4, 6, 8, 10, 12]
        fig = go.Figure()
        for f0, cor, dash, sym in [(60, AZ, "solid", "circle"), (50, VD, "dash", "square")]:
            ns_vals = [120 * f0 / p for p in polos]
            hover = [f"p={p} polos<br>nₛ = {int(v)} rpm" for p, v in zip(polos, ns_vals)]
            fig.add_trace(go.Scatter(
                x=polos, y=ns_vals,
                mode="lines+markers+text",
                name=f"f = {f0} Hz",
                line=dict(color=cor, width=3, dash=dash),
                marker=dict(size=11, color=cor, symbol=sym),
                text=[f"<b>{int(v)}</b>" for v in ns_vals],
                textposition="top right",
                textfont=dict(size=12, color=cor),
                hovertext=hover, hoverinfo="text",
            ))
        fig.update_layout(
            title=dict(text="Velocidade Síncrona × Número de Polos",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Número de polos p", font=dict(size=14, color=TX)),
                       tickvals=polos, tickfont=dict(size=13, color=TX),
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Velocidade síncrona nₛ (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=14), bgcolor="rgba(0,0,0,0)"),
            height=420, margin=dict(l=70, r=30, t=60, b=60),
        )
        return fig

    def fig_tensao_induzida_estator():
        """Tensão induzida no estator — forma de onda senoidal, Plotly."""
        t = np.linspace(0, 2, 500)
        e = np.sin(2 * np.pi * t)
        hover = [f"t = {ti:.3f} p.u.<br>e = {ei:.3f} p.u." for ti, ei in zip(t, e)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t, y=e, mode="lines",
            line=dict(color=AZ, width=3),
            name="e(t) = E<sub>max</sub> sin(ωt)",
            hovertext=hover, hoverinfo="text",
        ))
        # Linha zero
        fig.add_hline(y=0, line=dict(color=CZ, width=1, dash="dot"))
        # Anotação da amplitude (segmento vertical no pico)
        fig.add_shape(type="line", x0=0.25, x1=0.25, y0=0, y1=1.0,
                      line=dict(color=VM, width=2.5, dash="dash"))
        fig.add_annotation(x=0.30, y=0.50,
                           text="<b>E<sub>max</sub></b>",
                           showarrow=False, font=dict(color=VM, size=15))
        # Equação
        fig.add_annotation(
            x=0.02, y=1.30, xref="paper", yref="y",
            text="<b>E<sub>A</sub> = 4,44 · K<sub>w</sub> · N<sub>ph</sub> · f · Φ<sub>m</sub></b>",
            showarrow=False, font=dict(size=14, color=TX),
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor=CZ, borderwidth=1.2, borderpad=7, align="left",
        )
        # Legenda parâmetros
        fig.add_annotation(
            x=0.50, y=-1.45, xref="paper", yref="y",
            text="K<sub>w</sub>: fator de enrolamento  ·  N<sub>ph</sub>: espiras por fase  ·  Φ<sub>m</sub>: fluxo por polo",
            showarrow=False, font=dict(size=12, color=CZ),
        )
        fig.update_layout(
            title=dict(text="Tensão Induzida — Enrolamento do Estator",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Tempo (p.u.)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX),
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="e(t) (p.u.)", font=dict(size=14, color=TX)),
                       range=[-1.62, 1.62],
                       tickfont=dict(size=13, color=TX),
                       gridcolor="rgba(128,128,128,.18)"),
            showlegend=True,
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
            height=420, margin=dict(l=70, r=30, t=60, b=80),
        )
        return fig

    def fig_tensao_rotor_escorregamento():
        """Er = s·Er0 e fr = s·f — dois subplots Plotly lado a lado."""
        s = np.linspace(0, 1, 300)
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["<b>Tensão no Rotor  Eᵣ = s · Eᵣ₀</b>",
                             "<b>Frequência do Rotor  fᵣ = s · f</b>"],
            horizontal_spacing=0.14,
        )
        # Painel esquerdo
        hover_l = [f"s = {si:.2f}<br>Eᵣ = {si:.2f} · Eᵣ₀" for si in s]
        fig.add_trace(go.Scatter(
            x=s, y=s, mode="lines",
            line=dict(color=AZ, width=3), name="Eᵣ = s·Eᵣ₀",
            hovertext=hover_l, hoverinfo="text",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1], mode="markers",
            marker=dict(size=12, color=AZ, symbol="circle"),
            showlegend=False,
            hovertext=["s=0 → Eᵣ=0", "s=1 → Eᵣ=Eᵣ₀"], hoverinfo="text",
        ), row=1, col=1)
        for s_p, text_p, ay_p in [(0.08, "s=0 → Eᵣ=0", 30), (0.88, "s=1 → Eᵣ=Eᵣ₀", -30)]:
            fig.add_annotation(x=s_p, y=s_p, text=text_p,
                               showarrow=True, ay=ay_p, ax=30,
                               font=dict(size=12, color=CZ),
                               arrowcolor=CZ, arrowwidth=1.2,
                               row=1, col=1)
        # Painel direito
        for f0, cor, dash, nm in [(60, AZ, "solid", "f = 60 Hz"), (50, VD, "dash", "f = 50 Hz")]:
            hover_r = [f"s = {si:.2f}<br>fᵣ = {si*f0:.1f} Hz" for si in s]
            fig.add_trace(go.Scatter(
                x=s, y=s * f0, mode="lines",
                line=dict(color=cor, width=3, dash=dash), name=nm,
                hovertext=hover_r, hoverinfo="text",
            ), row=1, col=2)
        # Eixos
        for col in [1, 2]:
            fig.update_xaxes(
                title=dict(text="Escorregamento s", font=dict(size=13, color=TX)),
                tickfont=dict(size=12, color=TX), range=[-0.02, 1.05],
                gridcolor="rgba(128,128,128,.18)", row=1, col=col,
            )
        fig.update_yaxes(
            title=dict(text="Eᵣ / Eᵣ₀ (p.u.)", font=dict(size=13, color=TX)),
            tickfont=dict(size=12, color=TX), range=[-0.02, 1.12],
            gridcolor="rgba(128,128,128,.18)", row=1, col=1,
        )
        fig.update_yaxes(
            title=dict(text="fᵣ (Hz)", font=dict(size=13, color=TX)),
            tickfont=dict(size=12, color=TX),
            gridcolor="rgba(128,128,128,.18)", row=1, col=2,
        )
        fig.update_annotations(font_size=14)
        fig.update_layout(
            height=420, margin=dict(l=70, r=30, t=70, b=60),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.18),
        )
        return fig

    def fig_modos_operacao():
        """Curva T × n nas três regiões de operação — Plotly interativo."""
        V1, R1, X1, R2, X2, Xm = 127.0, 0.5, 1.0, 0.4, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60

        s_all = np.concatenate([
            np.linspace(-1.2, -1e-3, 300),
            np.linspace( 1e-3, 2.2,  700),
        ])
        n_all = ns * (1 - s_all)

        def torque(s):
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I2  = (V1 / (R1 + 1j*X1 + Zeq)) * Zeq / Z2
            return 3 * abs(I2)**2 * (R2/s) / ws

        T_all = np.array([torque(s) for s in s_all])
        T_pk  = float(np.max(T_all[(n_all >= 0) & (n_all <= ns)]))

        hover = [f"n = {ni:.0f} rpm<br>s = {(ns-ni)/ns:.3f}<br>T = {ti:.2f} N·m"
                 for ni, ti in zip(n_all, T_all)]

        fig = go.Figure()
        # Regiões preenchidas (fill via scatter com tozeroy)
        for mask, fc, name in [
            ((n_all >= 0) & (n_all <= ns), "rgba(31,157,85,0.10)",  "Motor (0 < s < 1)"),
            (n_all > ns,                    "rgba(61,142,240,0.10)", "Gerador (s < 0)"),
            (n_all < 0,                     "rgba(224,62,62,0.10)",  "Frenagem (s > 1)"),
        ]:
            fig.add_trace(go.Scatter(
                x=n_all[mask], y=T_all[mask],
                fill="tozeroy", fillcolor=fc,
                line=dict(width=0), name=name, mode="lines",
                hoverinfo="skip",
            ))
        # Curva principal
        fig.add_trace(go.Scatter(
            x=n_all, y=T_all, mode="lines",
            line=dict(color=TX, width=3),
            name="T(n)", showlegend=False,
            hovertext=hover, hoverinfo="text",
        ))
        # Linhas de referência
        fig.add_vline(x=ns, line=dict(color=AZ, width=1.5, dash="dash"))
        fig.add_vline(x=0,  line=dict(color=CZ, width=1,   dash="dot"))
        fig.add_hline(y=0,  line=dict(color=CZ, width=1))
        # Anotações das regiões
        for x_pos, y_pos, texto, cor in [
            (ns * 0.50,  T_pk * 0.50, "<b>MOTOR</b><br>0 < s < 1", VD),
            (ns * 1.60,  T_pk * 0.28, "<b>GERADOR</b><br>s < 0",   AZ),
            (-ns * 0.42, T_pk * 0.28, "<b>FRENAGEM</b><br>s > 1",  VM),
        ]:
            fig.add_annotation(x=x_pos, y=y_pos, text=texto,
                               showarrow=False, font=dict(size=15, color=cor))
        # Label ns
        fig.add_annotation(x=ns, y=float(np.min(T_all)) * 0.82,
                           text="<b>nₛ</b>", showarrow=False,
                           font=dict(size=14, color=AZ))
        fig.update_layout(
            title=dict(text="Regiões de Operação — Máquina de Indução",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX), range=[-0.88 * ns, 2.28 * ns],
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Torque T (N·m)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.18),
            height=460, margin=dict(l=75, r=30, t=60, b=80),
        )
        return fig

    def fig_curva_torque_velocidade():
        """Curva T × n (região motora) com pontos notáveis — Plotly interativo."""
        V1, R1, X1, R2, X2, Xm = 127.0, 0.5, 1.0, 0.4, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60
        s_range = np.linspace(1e-3, 1.0, 800)
        n_range = ns * (1 - s_range)

        def T_s(s):
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I2  = (V1 / (R1 + 1j*X1 + Zeq)) * Zeq / Z2
            return 3 * abs(I2)**2 * (R2/s) / ws

        T_vals = np.array([T_s(s) for s in s_range])
        idx_max = int(np.argmax(T_vals))
        T_max_v = T_vals[idx_max]; n_max = n_range[idx_max]
        T_part  = T_s(1.0)
        s_nom   = 0.05; T_nom = T_s(s_nom); n_nom = ns * (1 - s_nom)

        hover = [f"n = {ni:.0f} rpm<br>s = {si:.4f}<br>T = {ti:.2f} N·m"
                 for ni, si, ti in zip(n_range, s_range, T_vals)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=n_range, y=T_vals, mode="lines",
            line=dict(color=AZ, width=3.5), name="T(n)",
            hovertext=hover, hoverinfo="text",
        ))
        # Pontos notáveis com anotações individuais
        pontos = [
            (0,     T_part,  "T<sub>part</sub>", VM,  "square",      "bottom right", (-30, 30)),
            (n_max, T_max_v, "T<sub>max</sub>",  LR,  "triangle-up", "top center",   (0, -35)),
            (n_nom, T_nom,   "T<sub>nom</sub>",  VD,  "circle",      "bottom right", (30, 30)),
            (ns,    0,       "nₛ",               AZ,  "diamond",     "bottom right", (30, 30)),
        ]
        fig.add_trace(go.Scatter(
            x=[p[0] for p in pontos],
            y=[p[1] for p in pontos],
            mode="markers",
            marker=dict(size=14,
                        color=[p[3] for p in pontos],
                        symbol=[p[4] for p in pontos],
                        line=dict(width=1.5, color="white")),
            hovertext=[f"{p[2]}<br>n = {p[0]:.0f} rpm<br>T = {p[1]:.2f} N·m"
                       for p in pontos],
            hoverinfo="text",
            name="Pontos notáveis", showlegend=True,
        ))
        for x, y, lbl, cor, sym, tpos, (ax, ay) in pontos:
            fig.add_annotation(x=x, y=y, text=f"<b>{lbl}</b>",
                               showarrow=True, ax=ax, ay=ay,
                               font=dict(size=13, color=cor),
                               arrowcolor=cor, arrowwidth=1.5)
        fig.add_vline(x=ns, line=dict(color=AZ, width=1.5, dash="dash"))
        fig.add_hline(y=0,  line=dict(color=CZ, width=1))
        fig.update_layout(
            title=dict(text="Curva Característica Torque × Velocidade (Região Motora)",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX), range=[-80, ns + 160],
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Torque T (N·m)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
            height=460, margin=dict(l=75, r=30, t=60, b=70),
        )
        return fig

    def fig_curva_torque_R2():
        """Família T × n para R'₂ crescente (rotor bobinado) — Plotly interativo."""
        V1, R1, X1, X2, Xm = 127.0, 0.5, 1.0, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60
        s_range = np.linspace(1e-3, 1.0, 600)
        n_range = ns * (1 - s_range)

        R2_vals = [0.2, 0.4, 0.6, 1.0, 1.5]
        cores_v = [AZ, VD, LR, RX, CI]
        dashes   = ["solid", "dash", "dashdot", "dot", "longdash"]

        fig = go.Figure()
        for R2, cor, dash in zip(R2_vals, cores_v, dashes):
            def T_fn(s, R2=R2):
                Z2  = R2/s + 1j*X2
                Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
                I2  = (V1 / (R1 + 1j*X1 + Zeq)) * Zeq / Z2
                return 3 * abs(I2)**2 * (R2/s) / ws
            T_v  = np.array([T_fn(s) for s in s_range])
            hover = [f"R'₂ = {R2} Ω<br>n = {ni:.0f} rpm<br>T = {ti:.2f} N·m"
                     for ni, ti in zip(n_range, T_v)]
            fig.add_trace(go.Scatter(
                x=n_range, y=T_v, mode="lines",
                line=dict(color=cor, width=2.8, dash=dash),
                name=f"R'₂ = {R2} Ω",
                hovertext=hover, hoverinfo="text",
            ))

        fig.add_vline(x=ns, line=dict(color=AZ, width=1.5, dash="dash"))
        fig.add_hline(y=0,  line=dict(color=CZ, width=1))
        fig.add_annotation(x=ns, y=-3, text="<b>nₛ</b>",
                           showarrow=False, font=dict(size=14, color=AZ))
        fig.add_annotation(
            x=0.50, y=1.06, xref="paper", yref="paper",
            text="<i>T<sub>max</sub> independe de R'₂ · s<sub>max</sub> desloca-se proporcionalmente a R'₂</i>",
            showarrow=False, font=dict(size=12, color=CZ),
            bgcolor="rgba(255,255,255,0.75)", borderpad=5,
        )
        fig.update_layout(
            title=dict(text="Efeito de R'₂ na Curva T × n — Rotor Bobinado",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX), range=[-80, ns + 120],
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Torque T (N·m)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.20),
            height=460, margin=dict(l=75, r=30, t=70, b=100),
        )
        return fig

    def fig_gaiola_dupla():
        """T × n: gaiola dupla = gaiola externa + interna — Plotly interativo."""
        V1, R1, X1, Xm = 127.0, 0.5, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60
        s_range = np.linspace(1e-3, 1.0, 600)
        n_range = ns * (1 - s_range)

        R2_ext, X2_ext = 2.0, 0.5   # externa: alta R, baixa X
        R2_int, X2_int = 0.3, 3.5   # interna: baixa R, alta X

        def T_single(s, R2, X2):
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I2  = (V1 / (R1 + 1j*X1 + Zeq)) * Zeq / Z2
            return 3 * abs(I2)**2 * (R2/s) / ws

        def T_double(s):
            Z_e = R2_ext/s + 1j*X2_ext; Z_i = R2_int/s + 1j*X2_int
            Z2p = Z_e * Z_i / (Z_e + Z_i)
            Zeq = (1j*Xm * Z2p) / (1j*Xm + Z2p)
            It  = V1 / (R1 + 1j*X1 + Zeq)
            Vq  = It * Zeq
            return 3*(abs(Vq/Z_e)**2*(R2_ext/s) + abs(Vq/Z_i)**2*(R2_int/s)) / ws

        T_ext = np.array([T_single(s, R2_ext, X2_ext) for s in s_range])
        T_int = np.array([T_single(s, R2_int, X2_int) for s in s_range])
        T_dup = np.array([T_double(s) for s in s_range])
        T_sim = np.array([T_single(s, R2_int, X2_int * 0.30) for s in s_range])

        traces = [
            (T_sim, CZ, "dash",    "Gaiola simples (ref.)"),
            (T_ext, VM, "dashdot", f"Gaiola externa  R={R2_ext} Ω, X={X2_ext} Ω"),
            (T_int, AZ, "dot",     f"Gaiola interna  R={R2_int} Ω, X={X2_int} Ω"),
            (T_dup, VD, "solid",   "Gaiola dupla (resultante)"),
        ]
        widths = [2.0, 2.4, 2.4, 3.5]
        fig = go.Figure()
        for (T_v, cor, dash, nm), w in zip(traces, widths):
            hover = [f"{nm}<br>n = {ni:.0f} rpm<br>T = {ti:.2f} N·m"
                     for ni, ti in zip(n_range, T_v)]
            fig.add_trace(go.Scatter(
                x=n_range, y=T_v, mode="lines",
                line=dict(color=cor, width=w, dash=dash), name=nm,
                hovertext=hover, hoverinfo="text",
            ))

        fig.add_vline(x=ns, line=dict(color=AZ, width=1.5, dash="dash"))
        fig.add_hline(y=0,  line=dict(color=CZ, width=1))
        fig.add_annotation(x=ns, y=-1.5, text="<b>nₛ</b>",
                           showarrow=False, font=dict(size=14, color=AZ))
        fig.add_annotation(
            x=0.50, y=1.06, xref="paper", yref="paper",
            text="<i>Alta s (partida): gaiola externa domina · Baixa s (regime): gaiola interna domina</i>",
            showarrow=False, font=dict(size=12, color=CZ),
            bgcolor="rgba(255,255,255,0.75)", borderpad=5,
        )
        fig.update_layout(
            title=dict(text="Motor com Gaiola de Esquilo Dupla — Curvas de Torque",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX), range=[-80, ns + 120],
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Torque T (N·m)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.22),
            height=470, margin=dict(l=75, r=30, t=60, b=110),
        )
        return fig



    def fig_circuito_estator():
        """Circuito do estator: V1 → R1 → jX1 → Rc∥jXm → terminais E1 abertos."""
        with schemdraw.Drawing() as d:
            d.config(unit=2)

            # ── Fonte V1 à esquerda (terminal aberto embaixo, sobe para o fio) ──
            V1n = elm.Line().left(d.unit * 0.5).dot(open=True)
            elm.Gap().up(d.unit * 1.75).label(("−", "$V_1$", "+")).dot(open=True)
            V1p = elm.Line().right(d.unit * 0.5)

            # ── Fio superior: R1 → jX1 → nó A ─────────────────────────────
            elm.Resistor().right().label("$R_1$")
            elm.Inductor().right().label("$jX_1$")
            elm.Line().right(d.unit * 0.25).dot(open=False)   # nó A

            # ── Ramo shunt: Xm e Rc em paralelo (nó A → fio inferior) ──────
            d.push()
            Ifi = elm.Line().down(d.unit * 0.375)
            Xm_e = elm.Inductor().down().label("$jX_m$", loc="bottom")
            elm.Line().down(d.unit * 0.375)
            d.pop()

            d.push()
            d.move(dx=0, dy=-0.5 * d.unit)
            elm.Line().left(d.unit * 0.28)
            Rc_e = elm.Resistor().down().label("$R_c$")
            elm.Line().right(d.unit * 0.28)
            d.pop()

            # ── Terminais E1 afastados à direita (evita sobreposição com jXm) ──
            elm.Line().right(d.unit * 1.2).dot(open=True)
            elm.Gap().down(d.unit * 1.75).label(("−", "$E_1$", "+")).dot(open=True)
            elm.Line().left(d.unit * 1.2)

            # ── Fio inferior: fecha o circuito voltando a V1− ───────────────
            elm.Line().toy(V1n.end.y)
            elm.Line().to(V1n.end)

            # ── Rótulos de corrente ─────────────────────────────────────────
            elm.CurrentLabel(top=True,  length=1.0,  ofst=0.3).at(V1p).label("$I_1$")
            elm.CurrentLabel(top=True,  length=0.75, ofst=0.3).at(Ifi).label(r"$I_\phi$")
            elm.CurrentLabel(top=False, length=0.75, ofst=0.7).at(Rc_e).label("$I_c$")
            elm.CurrentLabel(top=False, length=0.75, ofst=-1.2).at(Xm_e).label(
                "$I_m$", loc="bottom")

            d.save("/tmp/_mei_est.png", dpi=140)

        fig, ax2 = plt.subplots(figsize=(8.0, 3.2))
        fig.patch.set_alpha(0); ax2.set_facecolor("none"); ax2.axis("off")
        ax2.imshow(plt.imread("/tmp/_mei_est.png"))
        plt.close("all")
        return fig

    def fig_circuito_rotor():
        """Circuito do rotor: fonte sE2 aberta → jX2 → R2 em série (malha fechada)."""
        with schemdraw.Drawing() as d:
            d.config(unit=2)

            # ── Fonte sE2 à esquerda — mesma convenção que V1 no estator ───
            sE2n = elm.Line().left(d.unit * 0.5).dot(open=True)
            elm.Gap().up(d.unit * 1.75).label(("−", "$sE_2$", "+")).dot(open=True)
            I2_lbl = elm.Line().right(d.unit * 0.5)

            # ── Ramo série superior: jX2 → R2 ───────────────────────────────
            elm.Inductor().right().label("$jX_2$")
            elm.Resistor().right().label("$R_2$")
            elm.Line().right(d.unit * 0.25)

            # ── Fecha a malha pelo fio inferior ─────────────────────────────
            elm.Line().toy(sE2n.end.y)
            elm.Line().to(sE2n.end)

            # ── Corrente I2 ──────────────────────────────────────────────────
            elm.CurrentLabel(top=True, length=0.9, ofst=0.3).at(I2_lbl).label("$I_2$")

            d.save("/tmp/_mei_rot.png", dpi=140)

        fig, ax2 = plt.subplots(figsize=(7.0, 3.0))
        fig.patch.set_alpha(0); ax2.set_facecolor("none"); ax2.axis("off")
        ax2.imshow(plt.imread("/tmp/_mei_rot.png"))
        plt.close("all")
        return fig

    def fig_ensaios_parametros():
        """Diagrama comparativo: ensaio em vazio e rotor bloqueado (slide 7)."""
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
        fig.patch.set_alpha(0)

        for ax in axes:
            ax.set_facecolor("none"); ax.axis("off")
            ax.set_xlim(0, 10); ax.set_ylim(0, 9)

        # Ensaio em vazio (esquerda)
        ax0 = axes[0]
        ax0.text(5, 8.5, "Ensaio em Vazio", ha="center", fontsize=11.5,
                 fontweight="bold", color=AZ)
        ax0.text(5, 7.8, "(equiv. CA do transformador)",
                 ha="center", fontsize=8, color=CZ, style="italic")

        items_vazio = [
            ("Condicao",      "$s \\approx 0$,  $n \\approx n_s$"),
            ("Alimentacao",   "Tensao e freq. nominais"),
            ("Medicoes",      "$V_0$, $I_0$, $P_0$"),
            ("Parametros",    "$R_c$, $X_m$, $P_{rot}$"),
            ("Obs.",          "$I_0$ = corrente de excitacao $I_\\phi$"),
        ]
        y0 = 7.0
        for titulo, valor in items_vazio:
            ax0.text(0.5, y0, titulo + ":", ha="left",
                     fontsize=9.5, color=AZ, fontweight="bold")
            ax0.text(0.5, y0 - 0.48, valor, ha="left", fontsize=9, color=TX)
            y0 -= 1.28

        # Ensaio com rotor bloqueado (direita)
        ax1 = axes[1]
        ax1.text(5, 8.5, "Ensaio — Rotor Bloqueado", ha="center", fontsize=11.5,
                 fontweight="bold", color=VM)
        ax1.text(5, 7.8, "(equiv. CC do transformador)",
                 ha="center", fontsize=8, color=CZ, style="italic")

        items_bloq = [
            ("Condicao",      "$s = 1$,  $n = 0$ (travado)"),
            ("Alimentacao",   "Tensao reduzida, freq. nominal"),
            ("Medicoes",      "$V_{cc}$, $I_{cc}$, $P_{cc}$"),
            ("Parametros",    "$R_1 + R_2'$,  $X_1 + X_2'$"),
            ("Obs.",          "$R_c$, $X_m$ desprezados"),
        ]
        y0 = 7.0
        for titulo, valor in items_bloq:
            ax1.text(0.5, y0, titulo + ":", ha="left",
                     fontsize=9.5, color=VM, fontweight="bold")
            ax1.text(0.5, y0 - 0.48, valor, ha="left", fontsize=9, color=TX)
            y0 -= 1.28

        # Linha divisória central
        fig.add_artist(plt.Line2D([0.5, 0.5], [0.05, 0.92],
                                   transform=fig.transFigure,
                                   color=CZ, lw=0.8, linestyle="--", alpha=0.5))

        fig.suptitle("Ensaios para Determinacao dos Parametros da MIT",
                     fontsize=11.5, fontweight="bold", color=TX, y=1.0)
        fig.tight_layout(pad=0.5)
        return fig

    def fig_corrente_estator_s():
        """I1 × s (ou n): corrente de estator em função do escorregamento — Plotly."""
        V1, R1, X1, R2, X2, Xm = 127.0, 0.5, 1.0, 0.4, 1.0, 50.0
        ns = 1800.0
        s_range = np.linspace(1e-3, 1.0, 600)
        n_range = ns * (1 - s_range)

        I1_vals, Im_vals, I2_vals = [], [], []
        for s in s_range:
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I1  = V1 / (R1 + 1j*X1 + Zeq)
            I2  = (I1 * Zeq) / Z2
            Im  = (I1 * Zeq) / (1j*Xm)
            I1_vals.append(abs(I1))
            I2_vals.append(abs(I2))
            Im_vals.append(abs(Im))

        I1_vals = np.array(I1_vals)
        I2_vals = np.array(I2_vals)
        Im_vals = np.array(Im_vals)

        fig = go.Figure()
        for y_arr, cor, dash, nm in [
            (I1_vals, AZ, "solid", "|I₁| — Estator"),
            (I2_vals, VD, "dash",  "|I₂'| — Rotor (ref.)"),
            (Im_vals, LR, "dot",   "|Iₘ| — Magnetização"),
        ]:
            hover = [f"n = {ni:.0f} rpm  s = {si:.3f}<br>{nm} = {vi:.3f} A"
                     for ni, si, vi in zip(n_range, s_range, y_arr)]
            fig.add_trace(go.Scatter(
                x=n_range, y=y_arr, mode="lines",
                line=dict(color=cor, width=2.8, dash=dash),
                name=nm, hovertext=hover, hoverinfo="text",
            ))

        # Anotações em s=0 e s=1
        for s_pt, label, xr in [(0.0, "s=0<br>(n=nₛ)", 0.0), (1.0, "s=1<br>(partida)", 0.0)]:
            n_pt = ns * (1 - s_pt)
            if s_pt < 0.01:
                s_p = 1e-3
            else:
                s_p = s_pt
            Z2  = R2/s_p + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I1_pt = abs(V1 / (R1 + 1j*X1 + Zeq))
            fig.add_annotation(x=n_pt, y=I1_pt,
                               text=f"<b>{label}</b><br>I₁={I1_pt:.2f} A",
                               showarrow=True, ay=-40, ax=30,
                               font=dict(size=11, color=AZ),
                               arrowcolor=AZ, arrowwidth=1.5)

        fig.add_vline(x=ns, line=dict(color=AZ, width=1.5, dash="dash"))
        fig.add_hline(y=0,  line=dict(color=CZ, width=0.8))
        fig.update_layout(
            title=dict(text="Correntes I₁, I₂' e Iₘ × Velocidade",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX), range=[-60, ns + 120],
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Corrente (A)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
            height=430, margin=dict(l=75, r=30, t=60, b=70),
        )
        return fig

    def fig_fator_potencia_s():
        """Fator de potência fp × velocidade — Plotly."""
        V1, R1, X1, R2, X2, Xm = 127.0, 0.5, 1.0, 0.4, 1.0, 50.0
        ns = 1800.0
        s_range = np.linspace(1e-3, 1.0, 600)
        n_range = ns * (1 - s_range)

        fp_vals = []
        for s in s_range:
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I1  = V1 / (R1 + 1j*X1 + Zeq)
            fp_vals.append(np.cos(np.angle(I1)))
        fp_vals = np.array(fp_vals)

        hover = [f"n = {ni:.0f} rpm  s = {si:.3f}<br>fp = {fi:.4f}"
                 for ni, si, fi in zip(n_range, s_range, fp_vals)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=n_range, y=fp_vals, mode="lines",
            line=dict(color=RX, width=3),
            name="fp = cos φ",
            hovertext=hover, hoverinfo="text",
        ))

        # Ponto de fp máximo
        idx_max = int(np.argmax(fp_vals))
        fig.add_trace(go.Scatter(
            x=[n_range[idx_max]], y=[fp_vals[idx_max]],
            mode="markers+text",
            marker=dict(size=12, color=RX, symbol="star"),
            text=[f"fp_max = {fp_vals[idx_max]:.3f}"],
            textposition="top left",
            textfont=dict(size=12, color=RX),
            name="fp máximo", showlegend=True,
        ))

        # Ponto na partida (s=1)
        fig.add_annotation(
            x=0, y=fp_vals[-1],
            text=f"Partida<br>fp = {fp_vals[-1]:.3f}",
            showarrow=True, ay=40, ax=30,
            font=dict(size=11, color=CZ), arrowcolor=CZ, arrowwidth=1.2,
        )

        fig.add_vline(x=ns, line=dict(color=AZ, width=1.5, dash="dash"))
        fig.add_annotation(x=ns, y=fp_vals[0] * 0.8,
                           text="<b>nₛ</b>", showarrow=False,
                           font=dict(size=14, color=AZ))
        fig.update_layout(
            title=dict(text="Fator de Potência × Velocidade",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX), range=[-60, ns + 120],
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Fator de potência cos φ", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX), range=[0, 1.05],
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
            height=420, margin=dict(l=75, r=30, t=60, b=70),
        )
        return fig

    def fig_eficiencia_curva():
        """Curva de eficiência η × carga (%) para motor de indução — Plotly."""
        V1, R1, X1, R2, X2, Xm = 127.0, 0.5, 1.0, 0.4, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60
        Prot = 350.0; Pfe = 280.0  # W

        s_range = np.linspace(2e-3, 0.40, 400)
        n_range = ns * (1 - s_range)
        eta_vals, Pout_vals, Pin_vals = [], [], []

        for s in s_range:
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I1  = V1 / (R1 + 1j*X1 + Zeq)
            I2  = (I1 * Zeq) / Z2
            Pag = 3 * abs(I2)**2 * (R2/s)
            Pin = 3 * V1 * abs(I1) * np.cos(np.angle(I1)) + Pfe
            Pout = max(0.0, Pag * (1 - s) - Prot)
            eta  = Pout / Pin * 100 if Pin > 0 else 0
            eta_vals.append(max(0.0, eta))
            Pout_vals.append(Pout)
            Pin_vals.append(Pin)

        eta_vals  = np.array(eta_vals)
        Pout_vals = np.array(Pout_vals)
        # Normaliza Pout pela potência nominal (máximo)
        Pnom = float(np.max(Pout_vals))
        carga_pct = Pout_vals / Pnom * 100 if Pnom > 0 else Pout_vals

        hover = [f"Carga = {cp:.1f}%<br>η = {ei:.2f}%<br>Pout = {po:.0f} W"
                 for cp, ei, po in zip(carga_pct, eta_vals, Pout_vals)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=carga_pct, y=eta_vals, mode="lines",
            line=dict(color=VD, width=3),
            name="η (%) — Motor",
            hovertext=hover, hoverinfo="text",
        ))

        # Ponto de η máxima
        idx_max = int(np.argmax(eta_vals))
        fig.add_trace(go.Scatter(
            x=[carga_pct[idx_max]], y=[eta_vals[idx_max]],
            mode="markers+text",
            marker=dict(size=13, color=VD, symbol="star",
                        line=dict(width=1.5, color="white")),
            text=[f"η_max = {eta_vals[idx_max]:.1f}%"],
            textposition="top left",
            textfont=dict(size=12, color=VD),
            showlegend=False,
        ))

        # Linha de carga nominal (100%)
        fig.add_vline(x=100, line=dict(color=CZ, width=1.5, dash="dot"))
        fig.add_annotation(x=100, y=eta_vals[np.argmin(np.abs(carga_pct - 100))],
                           text="Carga<br>nominal",
                           showarrow=True, ax=30, ay=-30,
                           font=dict(size=11, color=CZ),
                           arrowcolor=CZ, arrowwidth=1.2)

        fig.update_layout(
            title=dict(text="Eficiência η × Carga (%)",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Carga (% da pot. nominal)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX), range=[0, 115],
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Eficiência η (%)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
            height=420, margin=dict(l=75, r=30, t=60, b=70),
        )
        return fig

    def fig_torque_linear_s():
        """Aproximação linear T × s para baixo escorregamento — Plotly."""
        V1, R1, X1, R2, X2, Xm = 127.0, 0.5, 1.0, 0.4, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60

        # Curva completa
        s_full = np.linspace(1e-3, 1.0, 600)
        def T_s(s):
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I2  = (V1 / (R1 + 1j*X1 + Zeq)) * Zeq / Z2
            return 3 * abs(I2)**2 * (R2/s) / ws
        T_full = np.array([T_s(s) for s in s_full])

        # Aproximação linear: T ≈ (3 Vth²/ ωs (Rth² + (Xth+X2')²)) · (R2'/ωs) · s
        Xm_val = Xm; X1v = X1; R1v = R1
        Vth = V1 * Xm_val / np.sqrt((X1v + Xm_val)**2 + R1v**2)
        Rth = R1v * (Xm_val / (X1v + Xm_val))**2
        Xth = X1v
        K_lin = 3 * Vth**2 / (ws * (Rth**2 + (Xth + X2)**2))

        s_lin = np.linspace(0, 0.15, 100)
        T_lin = K_lin * (R2 / ws) * s_lin * ws  # = K_lin * R2 * s

        # Em termos de n
        n_full = ns * (1 - s_full)
        n_lin  = ns * (1 - s_lin)

        hover_f = [f"n = {ni:.0f} rpm  s = {si:.4f}<br>T = {ti:.2f} N·m"
                   for ni, si, ti in zip(n_full, s_full, T_full)]
        hover_l = [f"n = {ni:.0f} rpm  s = {si:.4f}<br>T_lin = {ti:.2f} N·m"
                   for ni, si, ti in zip(n_lin, s_lin, T_lin)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=n_full, y=T_full, mode="lines",
            line=dict(color=AZ, width=3), name="T(s) — completo",
            hovertext=hover_f, hoverinfo="text",
        ))
        fig.add_trace(go.Scatter(
            x=n_lin, y=T_lin, mode="lines",
            line=dict(color=VM, width=2.5, dash="dash"),
            name="T ≈ K · s (aprox. linear, s pequeno)",
            hovertext=hover_l, hoverinfo="text",
        ))

        # Anotação da fórmula linear
        fig.add_annotation(
            x=0.50, y=0.92, xref="paper", yref="paper",
            text="<b>Para s pequeno:</b>  T ≈ (3V<sub>th</sub>²R₂') / (ω<sub>s</sub>(R<sub>th</sub>²+(X<sub>th</sub>+X₂')²)) · s",
            showarrow=False, font=dict(size=12, color=VM),
            bgcolor="rgba(255,255,255,0.80)", borderpad=6,
        )

        fig.add_vline(x=ns, line=dict(color=AZ, width=1.5, dash="dash"))
        fig.add_hline(y=0,  line=dict(color=CZ, width=0.8))
        fig.update_layout(
            title=dict(text="Torque × Velocidade — Região Linear (baixo s)",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX), range=[-60, ns + 120],
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Torque T (N·m)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13, color=TX),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.18),
            height=440, margin=dict(l=75, r=30, t=60, b=90),
        )
        return fig

    def fig_rotor_bobinado_R2():
        """T×n para diferentes R'2 no rotor bobinado — slide 3 PPTX-03."""
        V1, R1, X1, X2, Xm = 127.0, 0.5, 1.0, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60
        s_range = np.linspace(1e-3, 1.0, 500)
        n_range = ns * (1 - s_range)

        R2_cases = [
            (0.1,  AZ, "solid",   "R'₂ pequena — nominal"),
            (0.6,  VD, "dash",    "R'₂ média"),
            (1.4,  LR, "dashdot", "R'₂ = X'₂  (T_max na partida)"),
        ]
        fig = go.Figure()
        for R2, cor, dash, nm in R2_cases:
            def T_fn(s, R2=R2):
                Z2 = R2/s + 1j*X2
                Zeq = (1j*Xm*Z2)/(1j*Xm+Z2)
                I2 = (V1/(R1+1j*X1+Zeq))*Zeq/Z2
                return 3*abs(I2)**2*(R2/s)/ws
            T_v = np.array([T_fn(s) for s in s_range])
            hover = [f"n={ni:.0f} rpm  s={si:.3f}<br>T={ti:.2f} N·m  R'₂={R2} Ω"
                     for ni,si,ti in zip(n_range,s_range,T_v)]
            fig.add_trace(go.Scatter(x=n_range, y=T_v, mode="lines",
                line=dict(color=cor, width=2.8, dash=dash), name=nm,
                hovertext=hover, hoverinfo="text"))

        # Partida máxima annotation
        R2_opt = float(np.sqrt(R1**2 + (X1+X2)**2)) * 0.95
        def T_opt(s):
            Z2 = R2_opt/s + 1j*X2
            Zeq = (1j*Xm*Z2)/(1j*Xm+Z2)
            I2 = (V1/(R1+1j*X1+Zeq))*Zeq/Z2
            return 3*abs(I2)**2*(R2_opt/s)/ws
        T_part_opt = T_opt(1.0)
        fig.add_annotation(x=0, y=T_part_opt,
            text=f"<b>T_max na partida<br>R'₂ ≈ |Z_cc|</b>",
            showarrow=True, ax=80, ay=-40,
            font=dict(size=11, color=LR), arrowcolor=LR, arrowwidth=1.5)

        fig.add_vline(x=ns, line=dict(color=AZ, width=1.5, dash="dash"))
        fig.add_hline(y=0,  line=dict(color=CZ, width=0.8))
        fig.update_layout(
            title=dict(text="Efeito de R'₂ na Curva T×n — Rotor Bobinado",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13), range=[-60, ns+120],
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Torque T (N·m)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.22),
            height=440, margin=dict(l=75, r=30, t=60, b=100),
        )
        return fig

    def fig_barra_profunda():
        """Seção transversal de barra profunda e curvas de distribuição de corrente."""
        fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2))
        fig.patch.set_alpha(0)

        # ── Painel esquerdo: seção da barra profunda ──────────────────────
        ax0 = axes[0]; ax0.set_facecolor("none"); ax0.axis("off")
        ax0.set_xlim(-3, 3); ax0.set_ylim(-5, 3)

        # Barra retangular alta (representação)
        bar = mpatches.FancyBboxPatch((-0.55, -4.5), 1.1, 5.0,
            boxstyle="round,pad=0.05", fc=LR, ec=TX, lw=1.5, zorder=3)
        ax0.add_patch(bar)

        # Ranhura ao redor
        slot = mpatches.FancyBboxPatch((-0.75, -4.8), 1.5, 5.5,
            boxstyle="round,pad=0.0", fc="none", ec=CZ, lw=1.0, ls="--",
            zorder=2, alpha=0.6)
        ax0.add_patch(slot)

        # Distribuição de corrente por altura (skin effect)
        y_bar = np.linspace(-4.5, 0.5, 200)
        # Alta frequência (partida): concentração no topo
        J_alta = np.exp(-3.0 * (-y_bar / 4.5))
        J_alta /= J_alta.max()
        # Baixa frequência (regime): uniforme
        J_baixa = np.ones_like(y_bar)

        ax0.barh(y_bar, J_alta * 0.5, height=0.04, left=0.55,
                  color=VM, alpha=0.85, zorder=4)
        ax0.barh(y_bar, J_baixa * 0.5, height=0.04, left=-1.05,
                  color=AZ, alpha=0.70, zorder=4)

        ax0.text(0, 1.5, "Barra profunda",
                 ha="center", fontsize=10, fontweight="bold", color=TX)
        ax0.text(-1.5, -2.5, "Baixa freq.\n(regime)\nJ uniforme",
                 ha="center", fontsize=8, color=AZ, style="italic")
        ax0.text(1.5, -2.5, "Alta freq.\n(partida)\nJ concentrada\nno topo",
                 ha="center", fontsize=8, color=VM, style="italic")

        # ── Painel direito: curvas T×n comparativas ───────────────────────
        ax1 = axes[1]; ax1.set_facecolor("none")
        ax1.spines[["top","right"]].set_visible(False)
        ax1.spines[["bottom","left"]].set_color(CZ)
        ax1.tick_params(colors=CZ)

        V1, R1, X1, X2, Xm = 127.0, 0.5, 1.0, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60
        s_r = np.linspace(1e-3, 1.0, 400)
        n_r = ns*(1-s_r)

        def T_s(s, R2):
            Z2 = R2/s + 1j*X2
            Zeq = (1j*Xm*Z2)/(1j*Xm+Z2)
            I2 = (V1/(R1+1j*X1+Zeq))*Zeq/Z2
            return 3*abs(I2)**2*(R2/s)/ws

        # R2 efetivo varia com s (skin effect simplificado)
        T_deep = np.array([T_s(s, 0.3 + 1.2*s) for s in s_r])
        T_simple = np.array([T_s(s, 0.35) for s in s_r])

        ax1.plot(n_r, T_simple, color=AZ, lw=2.0, ls="--", label="Gaiola simples")
        ax1.plot(n_r, T_deep,   color=VM, lw=2.5, ls="-",  label="Barra profunda")
        ax1.axvline(ns, color=AZ, lw=1.0, ls="--", alpha=0.5)
        ax1.axhline(0,  color=CZ, lw=0.7)
        ax1.set_xlabel("Velocidade n (rpm)", fontsize=10, color=TX)
        ax1.set_ylabel("Torque T (N·m)", fontsize=10, color=TX)
        ax1.set_title("Curvas T×n", fontsize=10, fontweight="bold", color=TX)
        ax1.legend(fontsize=9, framealpha=0.0)
        ax1.grid(True, alpha=0.18, ls="--", color=CZ)
        ax1.set_xlim(-60, ns+80)

        fig.suptitle("Gaiola com Barra Profunda — Efeito Pelicular",
                     fontsize=11.5, fontweight="bold", color=TX, y=1.01)
        fig.tight_layout(pad=0.5)
        return fig

    def fig_nema_classes():
        """Curvas T×n para as classes NEMA A, B, C, D — slide 7 PPTX-03."""
        V1, R1_b, X1, X2, Xm = 127.0, 0.5, 1.0, 1.0, 50.0
        ns = 1800.0; ws = ns * 2*np.pi/60
        s_r = np.linspace(1e-3, 1.0, 600)
        n_r = ns*(1-s_r)

        def T_s(s, R2, X2_=None):
            X2_ = X2_ or X2
            Z2 = R2/s + 1j*X2_
            Zeq = (1j*Xm*Z2)/(1j*Xm+Z2)
            I2 = (V1/(R1_b+1j*X1+Zeq))*Zeq/Z2
            return 3*abs(I2)**2*(R2/s)/ws

        # NEMA characteristics (approximate)
        classes = {
            "A": dict(R2=0.20, X2_=1.0,  cor=AZ, dash="solid",
                      desc="Alta corrente de partida, alta eficiência"),
            "B": dict(R2=0.35, X2_=1.5,  cor=VD, dash="dash",
                      desc="Partida normal, alta eficiência (mais comum)"),
            "C": dict(R2=0.90, X2_=1.8,  cor=LR, dash="dashdot",
                      desc="Alto torque de partida, corrente moderada"),
            "D": dict(R2=1.80, X2_=0.8,  cor=VM, dash="dot",
                      desc="Torque de partida muito alto, alto escorregamento"),
        }

        fig = go.Figure()
        for cls, p in classes.items():
            T_v = np.array([T_s(s, p["R2"], p["X2_"]) for s in s_r])
            hover = [f"NEMA {cls}<br>n={ni:.0f} rpm  s={si:.3f}<br>T={ti:.2f} N·m"
                     for ni,si,ti in zip(n_r,s_r,T_v)]
            fig.add_trace(go.Scatter(
                x=n_r, y=T_v, mode="lines",
                line=dict(color=p["cor"], width=2.8, dash=p["dash"]),
                name=f"Classe {cls} — {p['desc']}",
                hovertext=hover, hoverinfo="text",
            ))

        fig.add_vline(x=ns, line=dict(color=AZ, width=1.5, dash="dash"))
        fig.add_hline(y=0,  line=dict(color=CZ, width=0.8))
        fig.update_layout(
            title=dict(text="Curvas T×n — Classes NEMA de Motores em Gaiola",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13), range=[-60, ns+120],
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Torque T (N·m)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.28),
            height=450, margin=dict(l=75, r=30, t=60, b=120),
        )
        return fig

    def fig_partida_direta():
        """Diagrama de partida direta (DOL): corrente e velocidade × tempo."""
        t = np.linspace(0, 5.0, 500)
        # Corrente: pico na partida, decai exponencialmente ao nominal
        I_nom = 1.0; I_part_pu = 6.5
        tau_I = 0.3
        I_t = I_nom + (I_part_pu - I_nom) * np.exp(-t / tau_I)

        # Velocidade: curva de aceleração sigmoidal
        tau_n = 1.2
        n_t = 1.0 * (1 - np.exp(-t / tau_n))

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                             subplot_titles=["Corrente de linha I/I<sub>nom</sub>",
                                             "Velocidade n/n<sub>s</sub>"],
                             vertical_spacing=0.12)

        fig.add_trace(go.Scatter(x=t, y=I_t, mode="lines",
            line=dict(color=VM, width=2.8), name="I(t)/Inom",
            hovertemplate="t=%{x:.2f} s<br>I=%{y:.2f} Inom"), row=1, col=1)
        fig.add_hline(y=I_nom, line=dict(color=CZ, width=1.2, dash="dot"),
                      annotation_text="I_nom", annotation_position="right", row=1, col=1)
        fig.add_hline(y=I_part_pu, line=dict(color=VM, width=0.8, dash="dash"),
                      annotation_text=f"{I_part_pu}×Inom", row=1, col=1)

        fig.add_trace(go.Scatter(x=t, y=n_t, mode="lines",
            line=dict(color=AZ, width=2.8), name="n(t)/ns",
            hovertemplate="t=%{x:.2f} s<br>n=%{y:.3f} ns"), row=2, col=1)
        fig.add_hline(y=1.0, line=dict(color=AZ, width=1.2, dash="dot"),
                      annotation_text="nₛ", annotation_position="right", row=2, col=1)

        fig.update_xaxes(title_text="Tempo (s)", tickfont=dict(size=12), row=2, col=1)
        fig.update_yaxes(tickfont=dict(size=12))
        fig.update_layout(
            title=dict(text="Partida Direta (DOL) — Transitório de Corrente e Velocidade",
                       font=dict(size=15, color=TX)),
            showlegend=False,
            height=430, margin=dict(l=70, r=60, t=70, b=60),
        )
        return fig

    def fig_partida_estrela_triangulo():
        """Esquema Y/Δ: diagrama de ligação correto (matplotlib)."""
        fig, axes = plt.subplots(1, 2, figsize=(8.5, 4.5))
        fig.patch.set_alpha(0)

        for ax in axes:
            ax.set_facecolor("none"); ax.axis("off")

        # ── Painel esquerdo: Ligação Y ─────────────────────────────────────
        ax0 = axes[0]
        ax0.set_xlim(-3.5, 3.5); ax0.set_ylim(-4.0, 4.5)
        ax0.set_title("Ligação Y  (partida)", fontsize=10.5,
                      fontweight="bold", color=VD, pad=6)

        # Barras de alimentação no topo (L1, L2, L3)
        for i, (lbl, cor, xb) in enumerate(
                [("L1", AZ, -1.8), ("L2", VD, 0.0), ("L3", LR, 1.8)]):
            ax0.plot([xb, xb], [3.8, 3.0], color=cor, lw=2.2)
            ax0.plot(xb, 3.8, "o", ms=8, color=cor)
            ax0.text(xb, 4.2, lbl, ha="center", fontsize=10,
                     color=cor, fontweight="bold")

        # Três bobinas verticais em paralelo
        for i, (xb, cor) in enumerate(
                [(-1.8, AZ), (0.0, VD), (1.8, LR)]):
            # Bobina = segmento com curvas (simula indutor)
            ax0.add_patch(mpatches.FancyBboxPatch(
                (xb - 0.35, -0.6), 0.70, 3.2,
                boxstyle="round,pad=0.25",
                fc=cor, ec=TX, lw=1.2, alpha=0.22))
            # Fio superior da bobina → terminal L
            ax0.plot([xb, xb], [3.0, 2.6], color=cor, lw=2.2)
            # Fio inferior da bobina → nó estrela
            ax0.plot([xb, xb], [-0.6, -1.4], color=TX, lw=2.0)

        # Nó estrela (neutro)
        ax0.plot([-1.8, 1.8], [-1.4, -1.4], color=TX, lw=2.0)
        ax0.plot(0.0, -1.4, "o", ms=12, color=TX, zorder=5)
        ax0.text(0.0, -2.0, "N  (neutro)", ha="center", fontsize=9.5, color=TX)
        ax0.text(0.0, -2.7,
                 r"$V_{fase} = V_L/\sqrt{3} \approx 58\%\,V_{nom}$",
                 ha="center", fontsize=9, color=CZ, style="italic")

        # ── Painel direito: Ligação Δ ───────────────────────────────────────
        ax1 = axes[1]
        ax1.set_xlim(-3.5, 3.5); ax1.set_ylim(-4.0, 4.5)
        ax1.set_title("Ligação Δ  (regime)", fontsize=10.5,
                      fontweight="bold", color=LR, pad=6)

        # Vértices do triângulo (onde ficam os terminais L1, L2, L3)
        Vx = [0.0, -2.2,  2.2]
        Vy = [3.0, -1.5, -1.5]
        cores_v = [AZ, VD, LR]
        labels_v = ["L1", "L2", "L3"]

        for xi, yi, cor, lbl in zip(Vx, Vy, cores_v, labels_v):
            ax1.plot(xi, yi, "o", ms=10, color=cor, zorder=5)
            off = (0, 0.55) if yi > 0 else (0, -0.65)
            ax1.text(xi + off[0], yi + off[1], lbl,
                     ha="center", fontsize=10, color=cor, fontweight="bold")

        # Arestas do triângulo — cada aresta tem uma bobina no meio
        for i in range(3):
            j = (i + 1) % 3
            x1_, y1_ = Vx[i], Vy[i]
            x2_, y2_ = Vx[j], Vy[j]
            mx, my = (x1_ + x2_) / 2, (y1_ + y2_) / 2
            # Linha da aresta
            ax1.plot([x1_, x2_], [y1_, y2_], color=TX, lw=1.5, alpha=0.35)
            # Bobina (retângulo) no centro da aresta
            angle_deg = np.degrees(np.arctan2(y2_ - y1_, x2_ - x1_))
            t = ax1.transData
            w_box, h_box = 1.4, 0.45
            ax1.add_patch(mpatches.FancyBboxPatch(
                (mx - w_box/2, my - h_box/2), w_box, h_box,
                boxstyle="round,pad=0.12",
                fc=cores_v[i], ec=TX, lw=1.2,
                alpha=0.30,
                transform=(mpatches.transforms.Affine2D()
                            .rotate_deg_around(mx, my, angle_deg) + t)))
            ax1.text(mx, my, ["A-B","B-C","C-A"][i],
                     ha="center", va="center", fontsize=8, color=TX)

        ax1.text(0.0, -2.7,
                 r"$V_{fase} = V_L$  (tensão nominal)",
                 ha="center", fontsize=9, color=CZ, style="italic")

        fig.suptitle("Partida Estrela-Triângulo (Y/Δ) — Ligações",
                     fontsize=12, fontweight="bold", color=TX, y=1.0)
        fig.tight_layout(pad=0.5)
        return fig

    def fig_partida_yd_transitorio():
        """Plotly: corrente de linha no transitório Y/Δ vs DOL."""
        t = np.linspace(0, 6.5, 600)
        ts = 2.8   # instante de comutação Y→Δ

        I_DOL = 1.0 + (6.0 - 1.0) * np.exp(-t / 0.35)
        I_YD  = np.where(t < ts,
                         1.0/3 + (2.0 - 1.0/3) * np.exp(-t / 0.38),
                         1.0 + 2.8 * np.exp(-(t - ts) / 0.55))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=I_DOL, mode="lines",
            line=dict(color=VM, width=2.5, dash="dash"),
            name="Partida Direta (DOL)",
            hovertemplate="t=%{x:.2f} s<br>I=%{y:.2f}×I_nom"))
        fig.add_trace(go.Scatter(x=t, y=I_YD, mode="lines",
            line=dict(color=VD, width=3.0),
            name="Estrela-Triângulo (Y/Δ)",
            hovertemplate="t=%{x:.2f} s<br>I=%{y:.2f}×I_nom"))

        # Linha Y→Δ
        fig.add_vline(x=ts, line=dict(color=CZ, width=1.2, dash="dot"))
        fig.add_annotation(x=ts + 0.08, y=4.5, text="<b>Y→Δ</b>",
                           showarrow=False, font=dict(size=12, color=CZ))
        # Corrente nominal
        fig.add_hline(y=1.0, line=dict(color=CZ, width=1.0, dash="dot"))
        fig.add_annotation(x=6.2, y=1.08, text="$I_{nom}$",
                           showarrow=False, font=dict(size=12, color=CZ))

        fig.update_layout(
            title=dict(text="Corrente de Linha — Y/Δ vs DOL",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Tempo (s)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13), range=[0, 6.5],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Corrente (× I_nom)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13), range=[0, 7.2],
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
            height=400, margin=dict(l=75, r=30, t=60, b=70),
        )
        return fig

    def fig_partida_compensadora():
        """Esquema do autotransformador — coordenadas explícitas, sem sobreposições."""
        fig, ax = plt.subplots(figsize=(12, 5), facecolor='white')
        ax.set_facecolor('white'); ax.axis('off')
        ax.set_xlim(0, 12); ax.set_ylim(0, 5)

        # ── Rede ─────────────────────────────────────────────────────────────
        for lbl, cor, y in [("L1", AZ, 3.5), ("L2", VD, 3.0), ("L3", LR, 2.5)]:
            ax.annotate("", xy=(1.2, y), xytext=(0.5, y),
                        arrowprops=dict(arrowstyle="-|>", color=cor,
                                        lw=2.0, mutation_scale=14))
            ax.text(0.2, y, lbl, fontsize=11, color=cor,
                    fontweight="bold", va="center", ha="center")

        # ── AT block (x:1.2→3.2, y:2.0→4.0) ─────────────────────────────────
        ax.add_patch(mpatches.FancyBboxPatch(
            (1.2, 2.0), 2.0, 2.0,
            boxstyle="round,pad=0.08", fc="#e8f0ff", ec=AZ, lw=2.2))
        ax.text(2.2, 3.0, "Auto-\ntransformador\n(3φ)",
                ha="center", va="center", fontsize=10.5, color=TX, fontweight="bold")

        # ── Taps: saem de x=3.2, chegam a x=5.2 ─────────────────────────────
        for tap, y, cor in [(0.80, 3.5, LR), (0.65, 3.0, VD), (0.50, 2.5, AZ)]:
            ax.plot([3.2, 5.2], [y, y], color=cor, lw=1.8, ls="--", zorder=3)
            ax.text(4.2, y + 0.18, f"{int(tap*100)}%",
                    fontsize=10, color=cor, ha="center", va="bottom",
                    fontweight="bold")

        # Seta no tap de 65% (principal, entra no K)
        ax.annotate("", xy=(5.2, 3.0), xytext=(4.8, 3.0),
                    arrowprops=dict(arrowstyle="-|>", color=VD,
                                    lw=2.0, mutation_scale=14))

        # ── Contator K (x:5.2→6.8, y:2.3→3.7) ───────────────────────────────
        ax.add_patch(mpatches.FancyBboxPatch(
            (5.2, 2.3), 1.6, 1.4,
            boxstyle="round,pad=0.08", fc="#e8fff0", ec=VD, lw=2.2))
        ax.text(6.0, 3.0, "Contator\n(K)",
                ha="center", va="center", fontsize=10.5, color=TX, fontweight="bold")

        # ── K → MIT (seta + label α·V₁ bem acima da seta) ───────────────────
        ax.annotate("", xy=(7.6, 3.0), xytext=(6.8, 3.0),
                    arrowprops=dict(arrowstyle="-|>", color=TX,
                                    lw=2.0, mutation_scale=14))
        ax.text(7.2, 3.38, "α·V₁",
                fontsize=12, color=VM, ha="center", va="bottom", fontweight="bold")

        # ── MIT (elipse, cx=8.7, cy=3.0) ─────────────────────────────────────
        ax.add_patch(mpatches.Ellipse(
            (8.7, 3.0), 2.0, 1.6, fc="#dce4f0", ec=TX, lw=2.0))
        ax.text(8.7, 3.0, "MIT",
                ha="center", va="center", fontsize=12, fontweight="bold", color=TX)

        # ── Fórmulas (caixa tracejada no rodapé) ─────────────────────────────
        ax.add_patch(mpatches.FancyBboxPatch(
            (1.5, 0.15), 9.0, 1.55,
            boxstyle="round,pad=0.12", fc="white", ec=CZ, lw=1.2, ls="--"))
        ax.text(6.0, 1.40, r"$I_{linha} = \alpha^2 \cdot I_{DOL}$",
                ha="center", va="center", fontsize=12, color=TX)
        ax.text(6.0, 0.88, r"$T_{partida} = \alpha^2 \cdot T_{DOL}$",
                ha="center", va="center", fontsize=12, color=TX)
        ax.text(6.0, 0.38,
                r"$\alpha \in \{0{,}50\;;\;0{,}65\;;\;0{,}80\}$",
                ha="center", va="center", fontsize=10.5,
                color=CZ, style="italic")

        ax.set_title("Partida com Autotransformador (Compensadora)",
                     fontsize=13, fontweight="bold", color=TX, pad=10)
        fig.tight_layout()
        return fig

    def fig_partida_compensadora_barras():
        """Plotly: corrente e torque × tap do autotransformador."""
        alphas = [0.50, 0.65, 0.80, 1.00]
        I_dol  = 6.0; T_dol = 1.50
        labels = ["50%", "65%", "80%", "DOL (100%)"]
        cores  = [AZ, VD, LR, VM]

        I_vals = [a**2 * I_dol for a in alphas]
        T_vals = [a**2 * T_dol for a in alphas]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=labels, y=I_vals,
            name="Corrente (× I_nom)",
            marker=dict(color=cores, opacity=0.85,
                        line=dict(color=TX, width=1.2)),
            text=[f"{v:.2f}" for v in I_vals],
            textposition="outside",
        ))
        fig.add_trace(go.Bar(
            x=labels, y=T_vals,
            name="Torque (× T_nom)",
            marker=dict(color=cores, opacity=0.42,
                        pattern_shape="/",
                        line=dict(color=TX, width=1.2)),
            text=[f"{v:.2f}" for v in T_vals],
            textposition="outside",
        ))
        fig.add_hline(y=1.0, line=dict(color=CZ, width=1.2, dash="dot"))
        fig.update_layout(
            title=dict(text="Corrente e Torque de Partida por Tap do AT",
                       font=dict(size=16, color=TX)),
            barmode="group",
            xaxis=dict(title=dict(text="Tap do Autotransformador",
                                  font=dict(size=14, color=TX)),
                       tickfont=dict(size=13),
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Valor relativo (p.u.)",
                                  font=dict(size=14, color=TX)),
                       tickfont=dict(size=13), range=[0, 7.2],
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.22),
            height=400, margin=dict(l=75, r=30, t=60, b=90),
        )
        return fig

    def fig_controle_tensao_terminal():
        """Família T×n para diferentes tensões terminais — eixo y limitado a 200 N·m."""
        V1_nom, R1, X1, R2, X2, Xm = 127.0, 0.5, 1.0, 0.4, 1.0, 50.0
        ns = 1800.0; ws = ns * 2 * np.pi / 60
        s_r = np.linspace(1e-3, 1.0, 500)
        n_r = ns * (1 - s_r)

        def T_fn(s, V1):
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I2  = (V1 / (R1 + 1j*X1 + Zeq)) * Zeq / Z2
            return 3 * abs(I2)**2 * (R2/s) / ws

        fracs = [1.0, 0.85, 0.70, 0.55]
        cores = [AZ, VD, LR, VM]
        fig = go.Figure()
        for frac, cor in zip(fracs, cores):
            V1 = frac * V1_nom
            T_v = np.array([T_fn(s, V1) for s in s_r])
            hover = [f"V₁={frac*100:.0f}%V_nom<br>n={ni:.0f} rpm<br>T={ti:.2f} N·m"
                     for ni, ti in zip(n_r, T_v)]
            fig.add_trace(go.Scatter(
                x=n_r, y=T_v, mode="lines",
                line=dict(color=cor, width=3.0),
                name=f"V₁ = {frac*100:.0f}% V_nom",
                hovertext=hover, hoverinfo="text"))

        # Curva de carga (constante — ventilador simplificado, clipada ao range)
        T_carga = np.clip(0.9e-4 * n_r**2, 0, 200)
        fig.add_trace(go.Scatter(
            x=n_r, y=T_carga, mode="lines",
            line=dict(color=CZ, width=1.8, dash="dot"),
            name="Conjugado da carga (ventilador  ∝ n²)"))

        fig.add_annotation(x=0.50, y=1.06, xref="paper", yref="paper",
            text="<i>T ∝ V₁²  —  redução de tensão desloca o ponto de operação para maior s</i>",
            showarrow=False, font=dict(size=12, color=CZ),
            bgcolor="rgba(255,255,255,0.85)", borderpad=5)
        fig.add_vline(x=ns, line=dict(color=AZ, width=1.5, dash="dash"))

        fig.update_layout(
            title=dict(text="Controle por Tensão Terminal — T×n para Diferentes V₁",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13), range=[-40, ns + 100],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Torque T (N·m)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13),
                       range=[0, 200],
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.24),
            height=460, margin=dict(l=75, r=30, t=65, b=110),
        )
        return fig

    def fig_controle_frequencia():
        """T×n para controle por frequência (V/f constante) — slide 17 PPTX-03."""
        R1, X1_base, R2, X2_base, Xm_base = 0.5, 1.0, 0.4, 1.0, 50.0
        ns_base = 1800.0; f_base = 60.0
        V1_base = 127.0

        fig = go.Figure()
        freqs = [60, 45, 30, 15]
        cores = [AZ, VD, LR, VM]

        for f, cor in zip(freqs, cores):
            ratio = f / f_base
            V1  = V1_base * ratio          # V/f constante
            X1  = X1_base * ratio
            X2  = X2_base * ratio
            Xm  = Xm_base * ratio
            ns  = ns_base * ratio
            ws  = ns * 2*np.pi/60

            s_r = np.linspace(1e-3, 1.0, 400)
            n_r = ns*(1-s_r)

            def T_fn(s, V1=V1, X1=X1, X2=X2, Xm=Xm, ws=ws):
                Z2 = R2/s + 1j*X2
                Zeq = (1j*Xm*Z2)/(1j*Xm+Z2)
                I2 = (V1/(R1+1j*X1+Zeq))*Zeq/Z2
                return 3*abs(I2)**2*(R2/s)/ws

            T_v = np.array([T_fn(s) for s in s_r])
            hover = [f"f={f} Hz  V₁={V1:.0f} V<br>n={ni:.0f} rpm  T={ti:.2f} N·m"
                     for ni,ti in zip(n_r,T_v)]
            fig.add_trace(go.Scatter(x=n_r, y=T_v, mode="lines",
                line=dict(color=cor, width=2.8),
                name=f"f = {f} Hz  (V₁ = {V1:.0f} V)",
                hovertext=hover, hoverinfo="text"))

            # Mark ns
            fig.add_vline(x=ns, line=dict(color=cor, width=0.8, dash="dot"),
                          annotation_text=f"nₛ@{f}Hz",
                          annotation_font=dict(size=9, color=cor),
                          annotation_position="top")

        fig.add_hline(y=0, line=dict(color=CZ, width=0.8))
        fig.add_annotation(x=0.50, y=1.06, xref="paper", yref="paper",
            text="<i>Controle V/f constante — fluxo e T_max mantidos · nₛ proporcional a f</i>",
            showarrow=False, font=dict(size=12, color=CZ),
            bgcolor="rgba(255,255,255,0.80)", borderpad=5)
        fig.update_layout(
            title=dict(text="Controle por Frequência (V/f constante) — Família T×n",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13),
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Torque T (N·m)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.22),
            height=450, margin=dict(l=75, r=30, t=60, b=100),
        )
        return fig

    def fig_malha_fechada_velocidade():
        """Diagrama de blocos em malha fechada.
        n* como texto (sem bloco). Seta de saída longa para a realimentação descer após ela.
        """
        CY  = 3.5   # y da linha de sinal principal
        FBY = 1.2   # y da linha de realimentação
        R   = 0.38  # raio do somador
        BW  = 1.1   # meia-largura dos blocos
        BH  = 0.7   # meia-altura dos blocos

        REF_X   = 1.0    # posição x do texto n* (sem bloco)
        SUM_CX  = 2.8
        CTRL_CX = 5.8
        INV_CX  = 9.0
        MIT_CX  = 12.2
        OUT_TIP = 15.0   # ponta da seta de saída; realimentação desce daqui

        fig, ax = plt.subplots(figsize=(14.5, 5.5), facecolor='white')
        ax.set_facecolor('white'); ax.axis('off')
        ax.set_xlim(0, 16); ax.set_ylim(0, 6)

        def box(cx, hw, hh, label, cor):
            ax.add_patch(mpatches.FancyBboxPatch(
                (cx - hw, CY - hh), 2*hw, 2*hh,
                boxstyle="round,pad=0.10", fc="white", ec=cor, lw=2.3, zorder=3))
            ax.text(cx, CY, label, ha="center", va="center",
                    fontsize=10.5, color=TX, zorder=4)

        def fwd(x1, x2, cor=TX):
            ax.annotate("", xy=(x2, CY), xytext=(x1, CY),
                        arrowprops=dict(arrowstyle="-|>", color=cor,
                                        lw=2.0, mutation_scale=16), zorder=5)

        def seg(x1, y1, x2, y2, cor=TX, lw=2.0):
            ax.plot([x1, x2], [y1, y2], color=cor, lw=lw, zorder=4)

        # ── n* como texto com seta (sem bloco) ───────────────────────────────
        ax.text(REF_X, CY, "$n^*$",
                fontsize=14, color=TX, fontweight="bold",
                ha="center", va="center", zorder=4)
        fwd(REF_X + 0.25, SUM_CX - R)

        # ── Somador (círculo, sem texto interno) ──────────────────────────────
        ax.add_patch(mpatches.Circle(
            (SUM_CX, CY), R, fc="white", ec=TX, lw=2.3, zorder=5))
        ax.text(SUM_CX, CY + R + 0.13, "+",
                fontsize=13, color=TX, ha="center", va="bottom",
                fontweight="bold", zorder=6)
        ax.text(SUM_CX, CY - R - 0.15, "−",
                fontsize=15, color=VM, ha="center", va="top",
                fontweight="bold", zorder=6)

        # ── Blocos ────────────────────────────────────────────────────────────
        box(CTRL_CX, BW, BH, "Controlador\nPI/PID", AZ)
        box(INV_CX,  BW, BH, "Inversor\n(VFD)",     VD)
        box(MIT_CX,  BW, BH, "MIT",                  LR)

        # ── Setas do caminho direto ───────────────────────────────────────────
        fwd(SUM_CX + R,   CTRL_CX - BW)
        fwd(CTRL_CX + BW, INV_CX - BW)
        fwd(INV_CX + BW,  MIT_CX - BW)
        fwd(MIT_CX + BW,  OUT_TIP)       # seta longa de saída

        ax.text(OUT_TIP + 0.18, CY, "$n$",
                fontsize=14, color=TX, fontweight="bold", va="center")

        # ── Labels dos sinais (acima dos conectores) ──────────────────────────
        def sig(x, txt, cor):
            ax.text(x, CY + 0.52, txt, fontsize=9.5, color=cor,
                    ha="center", va="bottom", style="italic")

        sig((SUM_CX + R + CTRL_CX - BW) / 2,  "e = n* − n", AZ)
        sig((CTRL_CX + BW + INV_CX - BW) / 2, "$f,\\ V_1$", VD)
        sig((INV_CX + BW + MIT_CX - BW) / 2,  "$i_{abc}$",  LR)

        # ── Realimentação: desce de OUT_TIP, percorre por baixo ──────────────
        seg(OUT_TIP - 0.5, CY,   OUT_TIP, FBY,   cor=VM)
        seg(OUT_TIP - 0.5, FBY,  SUM_CX,  FBY,   cor=VM)
        ax.annotate("", xy=(SUM_CX, CY - R), xytext=(SUM_CX, FBY),
                    arrowprops=dict(arrowstyle="-|>", color=VM,
                                    lw=2.0, mutation_scale=16), zorder=5)

        ax.text((OUT_TIP + SUM_CX) / 2, FBY - 0.30,
                "Sensor de velocidade  (encoder / tacômetro)",
                ha="center", fontsize=10, color=VM, style="italic")

        ax.set_title("Controle em Malha Fechada de Velocidade",
                     fontsize=13, fontweight="bold", color=TX, pad=10)
        fig.tight_layout(pad=0.5)
        return fig

    def fig_escorregamento_constante():
        """T×n ilustrando controle por escorregamento constante — slide 19."""
        V1_nom, R1, X1, R2, X2, Xm = 127.0, 0.5, 1.0, 0.4, 1.0, 50.0
        ns_base = 1800.0; f_base = 60.0

        fig = go.Figure()
        freqs = [60, 45, 30, 15]
        cores = [AZ, VD, LR, VM]
        s_op = 0.04   # escorregamento constante de operação

        n_op_pts = []  # pontos de operação (velocidade, torque)

        for f, cor in zip(freqs, cores):
            ratio = f / f_base
            V1 = V1_nom * ratio
            X1_ = X1 * ratio; X2_ = X2 * ratio; Xm_ = Xm * ratio
            ns = ns_base * ratio; ws = ns * 2*np.pi/60

            s_r = np.linspace(1e-3, 1.0, 400)
            n_r = ns*(1-s_r)

            def T_fn(s, V1=V1, X1_=X1_, X2_=X2_, Xm_=Xm_, ws=ws):
                Z2 = R2/s + 1j*X2_
                Zeq = (1j*Xm_*Z2)/(1j*Xm_+Z2)
                I2 = (V1/(R1+1j*X1_+Zeq))*Zeq/Z2
                return 3*abs(I2)**2*(R2/s)/ws

            T_v = np.array([T_fn(s) for s in s_r])
            fig.add_trace(go.Scatter(x=n_r, y=T_v, mode="lines",
                line=dict(color=cor, width=2.4),
                name=f"f = {f} Hz  (V₁ = {V1:.0f} V)",
                hovertemplate=f"f={f} Hz<br>n=%{{x:.0f}} rpm<br>T=%{{y:.2f}} N·m"))

            # Ponto de operação com s constante
            n_pt = ns * (1 - s_op)
            T_pt = T_fn(s_op)
            n_op_pts.append((n_pt, T_pt, cor))

        # Linha de escorregamento constante
        n_pts_line = [p[0] for p in n_op_pts]
        T_pts_line = [p[1] for p in n_op_pts]
        fig.add_trace(go.Scatter(
            x=n_pts_line, y=T_pts_line, mode="lines+markers",
            line=dict(color=TX, width=2.0, dash="dash"),
            marker=dict(size=11, color=[p[2] for p in n_op_pts],
                        line=dict(width=1.5, color="white")),
            name=f"Ponto de operação (s={s_op:.2f} = cte.)",
        ))

        fig.add_hline(y=0, line=dict(color=CZ, width=0.8))
        fig.add_annotation(x=0.50, y=1.06, xref="paper", yref="paper",
            text="<i>Escorregamento constante → eficiência e fp otimizados em qualquer velocidade</i>",
            showarrow=False, font=dict(size=12, color=CZ),
            bgcolor="rgba(255,255,255,0.80)", borderpad=5)
        fig.update_layout(
            title=dict(text="Controle em Malha Fechada — Escorregamento Constante",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n (rpm)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13),
                       gridcolor="rgba(128,128,128,.18)"),
            yaxis=dict(title=dict(text="Torque T (N·m)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=13),
                       gridcolor="rgba(128,128,128,.18)"),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.25),
            height=450, margin=dict(l=75, r=30, t=60, b=110),
        )
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

    def _fluxo_png(cells_fn, fname):
        """Executa a função schemdraw, salva PNG e retorna figura matplotlib."""
        cells_fn(fname)
        fig, ax2 = plt.subplots(figsize=(7.5, 3.2))
        fig.patch.set_alpha(0); ax2.set_facecolor("none"); ax2.axis("off")
        ax2.imshow(plt.imread(fname))
        plt.close("all")
        return fig

    def fig_fluxo_potencia_motor():
        """Fluxo de potência — motor de indução (reprodução fiel do MEI-DESENHOS.ipynb)."""
        def _build(fname):
            with schemdraw.Drawing() as d:
                d.config(unit=2)
                d.push()
                elm.Arrow().right(d.unit * 4.0)
                elm.Label().label("$P_{out}$", ofst=(.4, -.125))
                d.pop()
                d.push()
                d.move(dx=0, dy=-0.125 * d.unit)
                elm.Line().right(d.unit * 3.25)
                elm.Arrow().down(d.unit * 0.5)
                elm.Label().label("$P_{rot}$", ofst=(.125, -.125))
                d.pop()
                d.push()
                d.move(dx=2.5 * d.unit, dy=0.5 * d.unit)
                elm.Line().down(d.unit * 1.5).linestyle(":").color("lightgrey")
                elm.Label().label("$P_{mec}$", ofst=(-3.0, .5))
                elm.Label().label("$P_{ele}$", ofst=(-3.0, -.6))
                d.pop()
                d.push()
                d.move(dx=0, dy=-0.25 * d.unit)
                elm.Line().right(d.unit * 2.0)
                elm.Arrow().down(d.unit * 0.5)
                elm.Label().label("$P_{cu,2}$", ofst=(.125, -.125))
                d.pop()
                d.push()
                d.move(dx=1.25 * d.unit, dy=0.25 * d.unit)
                elm.Line().down(d.unit * 1.0).linestyle(":").color("lightgrey")
                elm.Label().label("$P_{ag}$", ofst=(.25, .0))
                d.pop()
                d.push()
                d.move(dx=0, dy=-0.375 * d.unit)
                elm.Line().right(d.unit * 0.5)
                elm.Arrow().down(d.unit * 0.5)
                elm.Label().label("$P_{cu,1}$", ofst=(.125, -.125))
                d.pop()
                d.push()
                d.move(dx=-0.4 * d.unit, dy=-0.125 * d.unit)
                elm.Label().label("$P_{in}$", ofst=(.125, -.125))
                d.pop()
                d.save(fname)
        return _fluxo_png(_build, "/tmp/_mei_fluxo_motor.png")

    def fig_fluxo_potencia_gerador():
        """Fluxo de potência — gerador de indução (reprodução fiel do MEI-DESENHOS.ipynb)."""
        def _build(fname):
            with schemdraw.Drawing() as d:
                d.config(unit=2)
                d.push()
                elm.Arrow().right(d.unit * 4.0).reverse()
                elm.Label().label("$P_{in}$", ofst=(.4, -.4))
                d.pop()
                d.push()
                d.move(dx=4.0 * d.unit, dy=-0.125 * d.unit)
                elm.Line().left(d.unit * 3.25)
                elm.Arrow().down(d.unit * 0.5)
                elm.Label().label("$P_{cu,1}$", ofst=(.125, -.125))
                d.pop()
                d.push()
                d.move(dx=2.5 * d.unit, dy=0.5 * d.unit)
                elm.Line().down(d.unit * 1.5).linestyle(":").color("lightgrey")
                elm.Label().label("$P_{mec}$", ofst=(-3.0, .5))
                elm.Label().label("$P_{ele}$", ofst=(-3.0, -.6))
                d.pop()
                d.push()
                d.move(dx=4.0 * d.unit, dy=-0.25 * d.unit)
                elm.Line().left(d.unit * 2.0)
                elm.Arrow().down(d.unit * 0.5)
                elm.Label().label("$P_{cu,2}$", ofst=(.125, -.125))
                d.pop()
                d.push()
                d.move(dx=1.25 * d.unit, dy=0.25 * d.unit)
                elm.Line().down(d.unit * 1.0).linestyle(":").color("lightgrey")
                elm.Label().label("$P_{ag}$", ofst=(.25, .0))
                d.pop()
                d.push()
                d.move(dx=4.0 * d.unit, dy=-0.375 * d.unit)
                elm.Line().left(d.unit * 0.5)
                elm.Arrow().down(d.unit * 0.5)
                elm.Label().label("$P_{rot}$", ofst=(.125, -.125))
                d.pop()
                d.push()
                d.move(dx=-0.4 * d.unit, dy=0)
                elm.Label().label("$P_{out}$", ofst=(.125, -.125))
                d.pop()
                d.save(fname)
        return _fluxo_png(_build, "/tmp/_mei_fluxo_gerador.png")

    def fig_fluxo_potencia_frenagem():
        """Fluxo de potência — frenagem (reprodução fiel do MEI-DESENHOS.ipynb)."""
        def _build(fname):
            with schemdraw.Drawing() as d:
                d.config(unit=2)
                d.push()
                elm.Arrow().right(d.unit * 1.0)
                elm.Line().right(d.unit * 1.0).dot()
                elm.Line().right(d.unit * 1.0)
                elm.Arrow().right(d.unit * 1.0).reverse()
                elm.Label().label("$P_{eixo}$", ofst=(.5, -.125))
                d.pop()
                d.push()
                d.move(dx=0, dy=-0.125 * d.unit)
                elm.Line().right(d.unit * 0.5)
                elm.Arrow().down(d.unit * 0.5)
                elm.Label().label("$P_{cu,1}$", ofst=(.125, -.25))
                d.pop()
                d.push()
                d.move(dx=2.5 * d.unit, dy=0.5 * d.unit)
                elm.Line().down(d.unit * 1.5).linestyle(":").color("lightgrey")
                elm.Label().label("$P_{mec}$", ofst=(-3.0, .5))
                elm.Label().label("$P_{ele}$", ofst=(-3.0, -.6))
                d.pop()
                d.push()
                d.move(dx=2.0 * d.unit, dy=0)
                elm.Arrow().down(d.unit * 0.5)
                elm.Label().label("$P_{cu,2}$", ofst=(.125, -.125))
                d.pop()
                d.push()
                d.move(dx=1.25 * d.unit, dy=0.25 * d.unit)
                elm.Line().down(d.unit * 1.0).linestyle(":").color("lightgrey")
                elm.Label().label("$P_{ag}$", ofst=(.25, .0))
                d.pop()
                d.push()
                d.move(dx=4.0 * d.unit, dy=-0.125 * d.unit)
                elm.Line().left(d.unit * 0.5)
                elm.Arrow().down(d.unit * 0.5)
                elm.Label().label("$P_{rot}$", ofst=(.125, -.125))
                d.pop()
                d.push()
                d.move(dx=-0.4 * d.unit, dy=0)
                elm.Label().label("$P_{terminal}$", ofst=(-.25, -.125))
                d.pop()
                d.save(fname)
        return _fluxo_png(_build, "/tmp/_mei_fluxo_frenagem.png")

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


    def exp_corrente_fator_potencia():
        """Explorador: corrente de estator e fator de potência vs escorregamento."""
        st.markdown("#### 🎛️ Explorador 6 — Corrente de Estator e Fator de Potência")
        col1, col2 = st.columns(2)
        with col1:
            V_line = st.slider("$V_L$ (V)", 100, 600, 220, 10, key="e6_V")
            R1 = st.slider("$R_1$ (Ω)", 0.05, 2.0, 0.5, 0.05, key="e6_R1")
            X1 = st.slider("$X_1$ (Ω)", 0.10, 3.0, 1.0, 0.05, key="e6_X1")
        with col2:
            R2 = st.slider("$R'_2$ (Ω)", 0.05, 3.0, 0.4, 0.05, key="e6_R2")
            X2 = st.slider("$X'_2$ (Ω)", 0.10, 3.0, 1.0, 0.05, key="e6_X2")
            Xm = st.slider("$X_m$ (Ω)", 5.0, 100.0, 50.0, 1.0,  key="e6_Xm")

        col3, col4 = st.columns(2)
        with col3:
            f  = st.selectbox("$f$ (Hz)", [50, 60], index=1, key="e6_f")
        with col4:
            p  = st.selectbox("Polos", [2, 4, 6, 8], index=1, key="e6_p")

        V1 = V_line / np.sqrt(3); ns = 120 * f / p
        s_range = np.linspace(1e-3, 1.0, 500)
        n_range = ns * (1 - s_range)

        I1v, I2v, Imv, fpv = [], [], [], []
        for s in s_range:
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I1  = V1 / (R1 + 1j*X1 + Zeq)
            I2  = (I1 * Zeq) / Z2
            Im  = (I1 * Zeq) / (1j*Xm)
            I1v.append(abs(I1)); I2v.append(abs(I2)); Imv.append(abs(Im))
            fpv.append(np.cos(np.angle(I1)))

        from plotly.subplots import make_subplots as _msp
        fig = _msp(rows=1, cols=2,
                   subplot_titles=["Correntes (A)", "Fator de Potência"])

        for y_arr, cor, dash, nm in [
            (I1v, AZ, "solid", "|I₁|"), (I2v, VD, "dash", "|I₂'|"), (Imv, LR, "dot", "|Iₘ|")
        ]:
            fig.add_trace(go.Scatter(x=n_range, y=y_arr, mode="lines",
                                     line=dict(color=cor, width=2.4, dash=dash),
                                     name=nm), row=1, col=1)
        fig.add_trace(go.Scatter(x=n_range, y=fpv, mode="lines",
                                  line=dict(color=RX, width=2.8),
                                  name="cos φ"), row=1, col=2)
        for col in [1, 2]:
            fig.add_vline(x=ns, line=dict(color=AZ, width=1.2, dash="dash"), row=1, col=col)
        fig.update_xaxes(title_text="n (rpm)", tickfont=dict(size=12))
        fig.update_yaxes(title_text="A", row=1, col=1, tickfont=dict(size=12))
        fig.update_yaxes(title_text="cos φ", range=[0, 1.05], row=1, col=2,
                         tickfont=dict(size=12))
        fig.update_layout(height=400, legend=dict(orientation="h", y=-0.22,
                                                   font=dict(size=12)),
                           margin=dict(l=65, r=20, t=55, b=80))
        show_plot(fig, key="exp6_ifp", height=400)

    def exp_eficiencia_carga():
        """Explorador: eficiência × % de carga com parâmetros ajustáveis."""
        st.markdown("#### 🎛️ Explorador 7 — Eficiência × Carga")
        col1, col2 = st.columns(2)
        with col1:
            V_line = st.number_input("$V_L$ (V)", 100.0, 15000.0, 460.0, key="e7_V")
            f      = st.selectbox("$f$ (Hz)", [50, 60], index=1, key="e7_f")
            p      = st.selectbox("Polos", [2, 4, 6, 8], index=1, key="e7_p")
        with col2:
            R1 = st.number_input("$R_1$ (Ω)",  0.001, 5.0, 0.07,  0.001, format="%.4f", key="e7_R1")
            R2 = st.number_input("$R'_2$ (Ω)", 0.001, 5.0, 0.152, 0.001, format="%.4f", key="e7_R2")
            X1 = st.number_input("$X_1$ (Ω)",  0.01, 20.0, 0.743, 0.001, format="%.3f", key="e7_X1")
            X2 = st.number_input("$X'_2$ (Ω)", 0.01, 20.0, 0.764, 0.001, format="%.3f", key="e7_X2")
            Xm = st.number_input("$X_m$ (Ω)",  1.0, 500.0, 40.1,  0.1,   format="%.1f", key="e7_Xm")

        Prot = st.slider("$P_{rot}$ (W)", 0, 5000, 390, 10, key="e7_Prot")
        Pfe  = st.slider("$P_{fe}$ (W)",  0, 5000, 325, 10, key="e7_Pfe")

        V1 = V_line / np.sqrt(3); ns = 120*f/p
        s_arr = np.linspace(2e-3, 0.45, 400)
        n_arr = ns * (1 - s_arr)
        eta_arr = []; Pout_arr = []; T_arr = []

        for s in s_arr:
            Z2  = R2/s + 1j*X2
            Zeq = (1j*Xm * Z2) / (1j*Xm + Z2)
            I1  = V1 / (R1 + 1j*X1 + Zeq)
            I2  = (I1 * Zeq) / Z2
            Pag = 3 * abs(I2)**2 * (R2/s)
            Pin = 3 * V1 * abs(I1) * np.cos(np.angle(I1)) + Pfe
            po  = max(0.0, Pag*(1-s) - Prot)
            eta_arr.append(max(0.0, po/Pin*100) if Pin > 0 else 0)
            Pout_arr.append(po)
            T_arr.append(po / (ns*(1-s)*2*np.pi/60) if ns*(1-s) > 1 else 0)

        Pnom = max(Pout_arr) if max(Pout_arr) > 0 else 1
        carga = [po / Pnom * 100 for po in Pout_arr]

        from plotly.subplots import make_subplots as _msp
        fig = _msp(rows=1, cols=2,
                   subplot_titles=["η (%) × Carga (%)", "Conjugado e Potência × n"])
        fig.add_trace(go.Scatter(x=carga, y=eta_arr, mode="lines",
                                  line=dict(color=VD, width=2.8), name="η (%)"),
                      row=1, col=1)
        idx_mx = int(np.argmax(eta_arr))
        fig.add_trace(go.Scatter(x=[carga[idx_mx]], y=[eta_arr[idx_mx]],
                                  mode="markers",
                                  marker=dict(size=12, color=VD, symbol="star",
                                              line=dict(width=1.5, color="white")),
                                  showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=n_arr, y=Pout_arr, mode="lines",
                                  line=dict(color=AZ, width=2.2), name="P_out (W)"),
                      row=1, col=2)
        fig.add_trace(go.Scatter(x=n_arr, y=T_arr, mode="lines",
                                  line=dict(color=LR, width=2.0, dash="dash"),
                                  name="T_eixo (N·m)"),
                      row=1, col=2)
        fig.update_xaxes(tickfont=dict(size=12))
        fig.update_yaxes(tickfont=dict(size=12))
        fig.update_layout(height=400, legend=dict(orientation="h", y=-0.25,
                                                   font=dict(size=12)),
                           margin=dict(l=65, r=20, t=55, b=90))
        show_plot(fig, key="exp7_ef", height=400)

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
**1. Conceitos Elementares e Aplicações**

**2. Estrutura Construtiva — Estator e Rotor**

**3. Campo Magnético Girante** · FMM trifásica · velocidade síncrona

**4. Escorregamento** · definição · faixas de operação

**5. Tensão Induzida** · equação EA · Er = s·Er0 · fr = s·f

**6. Circuito Equivalente (por fase)**
· 6.1 Estator · 6.2 Rotor · 6.3 Completo · 6.4 IEEE · 6.5 Thévenin

**7. Ensaios para Determinação dos Parâmetros**
· Ensaio em vazio · Ensaio com rotor bloqueado

**8. Fluxo de Potência** · tabela de grandezas · motor · gerador · frenagem

**9. Torque Eletromagnético** · Tem(s) · Tmax · smax · aproximação linear

**10. Modos de Operação e Curva T×n**
· Motor · Gerador · Frenagem · pontos notáveis · região estável

**11. Corrente no Estator e Fator de Potência**
· I1, I2', Im × velocidade · cos φ × carga · correção fp

**12. Eficiência** · perdas fixas e variáveis · η_max · classes IE · três modos

**13. Efeito da Resistência do Rotor**
· Rotor bobinado com Rext · barra profunda · efeito pelicular

**14. Gaiola de Esquilo Dupla** · gaiola externa · gaiola interna · curvas T×n

**15. Classificação NEMA** · classes A, B, C, D · tabela · curvas T×n

**16. Métodos de Partida**
· DOL · estrela-triângulo · autotransformador (compensadora)

**17. Controle de Velocidade**
· mudança de polos · tensão terminal · V/f constante · malha fechada · escorregamento constante

**🎛️ Exploradores Interativos**
· T×n · Circ. equiv. · Tensão→T×n · Partida · Eficiência · Corrente e fp · Efic.×Carga

**Referências** (ao final da página)
""")

    st.divider()

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

    show_plot(fig_velocidade_sincrona(), key="fig_3_ns")
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

    st.markdown(r"""
Os três modos de operação da MIT segundo o escorregamento:

| Modo | Faixa de $s$ | Velocidade $n$ | Descrição |
|---|---|---|---|
| **Motor** | $0 < s < 1$ | $0 < n < n_s$ | Potência elétrica → mecânica. Uso mais frequente. |
| **Gerador** | $s < 0$ | $n > n_s$ | Potência mecânica → elétrica. Ex.: turbinas eólicas. |
| **Frenagem** | $s > 1$ | $n < 0$ | Ambas as potências dissipadas no rotor. Frenagem rápida. |
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

    show_plot(fig_tensao_induzida_estator(), key="fig_5_ea")
    st.caption("**Figura 5.1** — Forma de onda de $e(t)$ e equação do valor eficaz $E_A$.")

    st.markdown(r"""
### Tensão no Rotor

Com o rotor **estacionário** ($s = 1$): $E_{r0} = (N_r/N_s)\,E_A$, com $f_{r0} = f$.

Com o rotor **girando** com escorregamento $s$:

$$\boxed{E_r = s \cdot E_{r0}} \qquad \boxed{f_r = s \cdot f}$$

A reatância de dispersão do rotor também escala: $X_r = s\,X_{r0}$,
onde $X_{r0} = 2\pi f L_r$.
""")

    show_plot(fig_tensao_rotor_escorregamento(), key="fig_5_er")
    st.caption("**Figura 5.2** — Variação de $E_r$ (esq.) e $f_r$ (dir.) com o escorregamento $s$.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 6
    # ═══════════════════════════════════════════════════════════════════════
    st.header("6. Circuito Equivalente (por fase)")
    st.markdown(r"""
A MIT pode ser modelada por um **circuito monofásico equivalente** por fase, construído a
partir dos circuitos individuais do estator e do rotor ligados através das grandezas de
entreferro — exatamente como o transformador, porém com o secundário girante.
""")

    st.markdown("### 6.1 Circuito do Estator")
    st.markdown(r"""
O circuito do estator é idêntico ao do primário de um transformador, com a diferença de que:
- A corrente de excitação $I_\phi$ é **maior** devido ao entreferro;
- A reatância $X_1$ é **maior** pela distribuição dos enrolamentos ao longo da periferia.

| Símbolo | Significado |
|---|---|
| $V_1$ | Tensão terminal por fase |
| $R_1$ | Resistência do enrolamento do estator |
| $X_1 = \omega L_1$ | Reatância de dispersão do estator |
| $R_c$ | Resistência de perda no núcleo |
| $X_m = \omega L_m$ | Reatância de magnetização |
| $E_1$ | Tensão induzida no estator |
""")

    show_fig(fig_circuito_estator(), width_frac=0.78)
    st.caption("**Figura 6.1** — Circuito equivalente do estator: ramo série $R_1 + jX_1$ "
               "e ramo de excitação $R_c ∥ jX_m$.")

    st.markdown("### 6.2 Circuito do Rotor")
    st.markdown(r"""
O rotor girando com escorregamento $s$ gera tensão $E_r = s E_2$ à frequência $f_r = s f$.
A corrente de rotor $I_2$ é determinada pela impedância:

$$Z_2 = R_2 + j s X_2$$

A potência dissipada no cobre do rotor por fase é:

$$P_{cu,2} = I_2^2 R_2 = s \cdot P_{ag}$$
""")

    show_fig(fig_circuito_rotor(), width_frac=0.62)
    st.caption("**Figura 6.1a** — Circuito equivalente do rotor com tensão $sE_2$ "
               "e impedância $R_2 + jsX_2$.")

    st.markdown(
        "Dividindo numerador e denominador da corrente de rotor por $s$, "
        "obtém-se o circuito referido ao estator com frequência do estator:"
    )
    st.latex(r"I_2 = \frac{s E_2}{R_2 + j s X_2} = \frac{E_2}{R_2/s + j X_2}")
    st.markdown("A resistência $R_2/s$ é decomposta como:")
    st.latex(r"\frac{R_2}{s} = R_2 + \underbrace{R_2 \frac{1-s}{s}}_{\text{carga mec.}}")
    st.markdown(r"""
$R_2$ representa as perdas Joule no rotor; $R_2(1-s)/s$ é a **resistência de carga mecânica**,
proporcional à potência convertida.

### 6.3 Circuito Completo

Inclui: ramo série do estator ($R_1 + jX_1$), ramo de excitação ($R_c \parallel jX_m$)
e ramo do rotor referido ($jX'_2 + R'_2/s$).
""")
    show_fig(fig_circuito_completo(), width_frac=0.82)
    st.caption("**Figura 6.1** — Circuito equivalente completo com $R_c$, $X_m$, "
               "$R_1$, $X_1$, $R'_2/s$ e $X'_2$.")


    st.markdown("### 6.4 Circuito IEEE Simplificado")
    st.markdown("Quando $R_c$ é omitido, o modelo IEEE move $X_m$ para os terminais de entrada:")


    show_fig(fig_circuito_ieee(), width_frac=0.78)
    st.caption("**Figura 6.2** — Circuito equivalente IEEE simplificado (sem $R_c$).")

    st.markdown("### 6.5 Equivalente de Thévenin")
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
    # SEÇÃO 7 — ENSAIOS
    # ═══════════════════════════════════════════════════════════════════════
    st.header("7. Ensaios para Determinação dos Parâmetros")
    st.markdown(r"""
Os parâmetros do circuito equivalente são obtidos experimentalmente por dois ensaios clássicos,
análogos aos ensaios do transformador. Antes dos ensaios, a **resistência do estator** $R_1$
é medida diretamente com a máquina desligada (método CC por fase).
""")

    show_fig(fig_ensaios_parametros(), width_frac=0.90)
    st.caption("**Figura 7.1** — Comparação dos ensaios em vazio e com rotor bloqueado.")

    st.markdown("### Ensaio em Vazio")
    st.markdown(
        "Com o motor operando sem carga ($s \\approx 0$, $n \\approx n_s$), "
        "na tensão e frequência nominais. Grandezas medidas: $V_0$, $I_0$, $P_0$."
    )
    st.latex(r"R_c = \frac{3 V_1^2}{P_0 - P_{R_1}} \qquad X_m = \frac{V_1}{I_\phi}")
    st.markdown(r"""
onde $P_0$ é a potência total medida, $P_{R_1} = 3 R_1 I_0^2$ é a perda no cobre do estator
e $I_\phi = \sqrt{I_0^2 - (P_0/3V_1)^2}$ é a corrente de magnetização.
As **perdas rotacionais** $P_{rot}$ são obtidas subtraindo as perdas no cobre e no ferro.

### Ensaio com Rotor Bloqueado

Com $n = 0$ ($s = 1$), aplicando tensão reduzida até a corrente nominal. Grandezas: $V_{cc}$, $I_{cc}$, $P_{cc}$.
""")
    st.latex(r"R_{eq} = R_1 + R_2' = \frac{P_{cc}}{3 I_{cc}^2} \qquad X_{eq} = X_1 + X_2' = \sqrt{\left(\frac{V_{cc}}{I_{cc}}\right)^2 - R_{eq}^2}")
    st.markdown(r"""
A repartição $X_1$ e $X'_2$ segue convenções de norma: tipicamente $X_1 = X'_2$ para motores
de gaiola, ou determinada por medições adicionais no rotor bobinado.
""")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 8 — FLUXO
    # ═══════════════════════════════════════════════════════════════════════
    st.header("8. Fluxo de Potência e Balanço de Energia")
    st.markdown(
        "As figuras abaixo ilustram o fluxo de potência nos três modos de operação. "
        "A tabela resume as grandezas envolvidas:"
    )
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
    st.caption("**Figura 8.1** — Fluxo de potência no **motor** de indução: "
               "$P_{in}$ (elétrica) → perdas → $P_{out}$ (mecânica no eixo).")

    show_fig(fig_fluxo_potencia_gerador(), width_frac=0.95)
    st.caption("**Figura 8.2** — Fluxo de potência no **gerador** de indução: "
               "$P_{in}$ (mecânica) → perdas → $P_{out}$ (elétrica no terminal).")

    show_fig(fig_fluxo_potencia_frenagem(), width_frac=0.95)
    st.caption("**Figura 8.3** — Fluxo de potência na **frenagem** ($s > 1$): "
               "potências elétrica e mecânica convergem para o rotor e são dissipadas como calor.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 9 — TORQUE
    # ════════════════════════════════════════════════════════════════════════
    st.header("9. Torque Eletromagnético")
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
    st.markdown("### Aproximação Linear para Baixo Escorregamento")
    st.markdown(
        "Para valores **pequenos** de escorregamento (região de operação nominal), "
        "a reatância $X\'_2$ é muito menor que $R\'_2/s$, e o denominador simplifica. "
        "O torque torna-se diretamente proporcional ao escorregamento:"
    )
    st.latex(r"T_{em}(s) \approx \frac{3\,V_{th}^2}{\omega_s\,(R_{th}^2+(X_{th}+X_2')^2)} \cdot \frac{R_2'}{1} \cdot s \qquad (s \ll s_{max})")
    st.markdown(r"""
Comportamento análogo ao de um motor CC de excitação independente com relação linear
torque-velocidade. Esta aproximação permite análise simplificada do ponto de operação nominal.
""")
    show_plot(fig_torque_linear_s(), key="fig_9_tlin")
    st.caption("**Figura 9.1** — Comparação entre a curva exata $T(s)$ (azul) e a "
               "aproximação linear T ≈ K·s (vermelho tracejado) para baixo s.")

    st.divider()
    # SEÇÃO 10 — MODOS
    # ═══════════════════════════════════════════════════════════════════════
    st.header("10. Modos de Operação e Curva T×n")
    st.markdown(
        "Os três modos de operação — **motor** ($0 < s < 1$), **gerador** ($s < 0$) "
        "e **frenagem** ($s > 1$) — foram definidos na Seção 4. "
        "A curva abaixo ilustra o torque eletromagnético nas três regiões."
    )

    show_plot(fig_modos_operacao(), key="fig_10_modos")
    st.caption("**Figura 10.1** — Curva $T \\times n$ nas três regiões de operação: "
               "motor (verde, $0 < s < 1$), gerador (azul, $s < 0$) e frenagem (vermelho, $s > 1$).")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    st.markdown("### Curva Característica T × n")
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

    show_plot(fig_curva_torque_velocidade(), key="fig_10_tv")
    st.caption("**Figura 10.2** — Curva $T \\times n$ (região motora) com pontos notáveis.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 11 — CORRENTE E FP
    # ═══════════════════════════════════════════════════════════════════════
    st.header("11. Corrente no Estator e Fator de Potência")
    st.markdown(r"""
A corrente de linha do estator $I_1$ varia significativamente com o escorregamento.
Dois casos extremos são importantes:

**Em velocidade síncrona ($s = 0$):** o ramo do rotor está em aberto ($R'_2/s 	o \infty$).
A corrente é apenas a de excitação $I_\phi$, tipicamente 20–40% da corrente nominal.

**Na partida ($s = 1$):** o ramo de excitação é desprezível. A corrente de partida pode
atingir **5 a 8 vezes** a corrente nominal — principal motivação dos métodos de partida suave.
""")
    st.latex(r"I_{1,partida} \approx \frac{V_1}{\sqrt{(R_1+R_2')^2 + (X_1+X_2')^2}}")

    show_plot(fig_corrente_estator_s(), key="fig_11_I1")
    st.caption("**Figura 11.1** — Correntes $|I_1|$, $|I_2'|$ e $|I_m|$ × velocidade. "
               "Alto valor de $I_1$ na partida ($n=0$) e queda para $I_\\phi$ em $n=n_s$.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════

    st.markdown("### Fator de Potência")
    st.markdown(
        "O fator de potência $\\cos\\varphi$ é o cosseno do ângulo de defasagem "
        "entre $V_1$ e $I_1$:"
    )
    st.latex(r"\cos\varphi = \cos\!\left(\angle\,\dfrac{V_1}{I_1}\right)")
    st.markdown(r"""
**Comportamento típico:**
- **Carga leve / vazio**: fp baixo (0,1–0,3) — corrente de excitação reativa domina;
- **Carga nominal**: fp elevado (0,80–0,92) — boa relação ativa/reativa;
- **Partida** ($s = 1$): fp moderado (0,35–0,55), determinado pela impedância total.

Motores operando cronicamente em carga leve causam baixo fp na instalação,
exigindo **correção por banco de capacitores**.
""")

    show_plot(fig_fator_potencia_s(), key="fig_11_fp")
    st.caption("**Figura 11.2** — Fator de potência cos φ × velocidade. "
               "fp baixo em vazio, máximo próximo da carga nominal, moderado na partida.")

    st.divider()
    # SEÇÃO 12 — EFICIÊNCIA
    # ═══════════════════════════════════════════════════════════════════════
    st.header("12. Eficiência")
    st.markdown("A eficiência do motor de indução é:")
    st.latex(r"\eta = \frac{P_{out}}{P_{in}} = \frac{P_{mec} - P_{rot}}{P_{in}} = 1 - \frac{P_{perdas}}{P_{in}}")
    st.markdown(r"""
As perdas totais são $P_{perdas} = P_{cu,1} + P_{fe} + P_{cu,2} + P_{rot}$.

**Eficiência máxima** ocorre quando perdas variáveis (cobre $\propto I^2$) igualam
as perdas fixas (ferro + rotacionais, aproximadamente constante):
""")
    st.latex(r"P_{cu,1} + P_{cu,2} \approx P_{fe} + P_{rot} \quad \Rightarrow \quad \eta_{max}")
    st.markdown(r"""
Motores de alto rendimento (classes IE2–IE4) atingem $\eta > 95\%$ na faixa 50–100% da carga.

**Nos três modos de operação:**
""")

    col_eff1, col_eff2, col_eff3 = st.columns(3)
    with col_eff1:
        st.markdown("**Motor** ($0 < s < 1$)\n\n"
                    r"$\eta = P_{out}/P_{in} < 1$" "\n\n"
                    "Potência elétrica → mecânica.")
    with col_eff2:
        st.markdown("**Gerador** ($s < 0$)\n\n"
                    r"$\eta = P_{out}/P_{in} < 1$" "\n\n"
                    "Potência mecânica → elétrica.")
    with col_eff3:
        st.markdown("**Frenagem** ($s > 1$)\n\n"
                    r"$\eta = 0$" "\n\n"
                    "Toda energia dissipada no rotor.")

    show_plot(fig_eficiencia_curva(), key="fig_12_eta")
    st.caption("**Figura 12.1** — Curva de eficiência η × carga (%). "
               "Eficiência máxima tipicamente entre 50–80% da carga nominal.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════

    # SEÇÃO 13 — EFEITO R2
    # ═══════════════════════════════════════════════════════════════════════
    st.header("13. Efeito da Resistência do Rotor")
    st.markdown(r"""
A resistência do rotor $R'_2$ influencia fortemente o desempenho da MIT,
criando um compromisso entre dois requisitos opostos:

- **Baixa $R'_2$** (necessária em regime permanente): escorregamento pequeno → alta eficiência;
- **Alta $R'_2$** (necessária na partida): alto fator de potência, alto torque e baixa corrente de partida.

Este conflito motivou o desenvolvimento das diversas construções de rotor estudadas a seguir.
""")

    st.markdown("### Rotor Bobinado com Resistência Externa")
    st.markdown(r"""
No rotor bobinado, resistências externas $R_{ext}$ são inseridas em série pelo circuito
dos anéis coletores. Como $T_{max}$ **não depende de $R'_2$**, mas $s_{max}$ é proporcional
a $R'_2$, a adição de resistência externa permite:

1. **Na partida**: ajustar $R_{ext}$ para que $s_{max} = 1$ → torque de partida máximo
   com corrente de linha reduzida;
2. **Durante a aceleração**: reduzir $R_{ext}$ gradualmente mantendo alto torque;
3. **Em regime**: $R_{ext} = 0$ → operação eficiente com baixo escorregamento.
""")

    show_plot(fig_rotor_bobinado_R2(), key="fig_13_rb")
    st.caption("**Figura 13.1** — Efeito de $R'_2$ crescente: $s_{max}$ desloca-se para a partida "
               "sem alterar $T_{max}$. A curva intermediária atinge $T_{max}$ exatamente em $n=0$.")

    st.markdown("### Gaiola com Barra Profunda")
    st.markdown(r"""
Em vez de resistência externa, a **barra profunda** usa o **efeito pelicular**
(*skin effect*) para variar a resistência efetiva automaticamente com a frequência do rotor:

| Condição | $f_r = sf$ | Distribuição de $J$ | $R_{2,ef}$ | Comportamento |
|---|---|---|---|---|
| Partida ($s=1$) | $f_r = f$ | Concentrada no topo | Alta | Alto torque, baixa corrente |
| Regime ($s\ll1$) | $f_r 	o 0$ | Uniforme | Baixa | Alta eficiência |

A seção transversal da barra é alta e estreita — quanto maior a profundidade, maior a
reatância de dispersão e menor a utilização da seção em alta frequência.
""")

    show_fig(fig_barra_profunda(), width_frac=0.88)
    st.caption("**Figura 13.2** — Seção da barra profunda: distribuição de corrente em alta "
               "frequência (partida, vermelho) e baixa frequência (regime, azul), e curvas T×n.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 14 — GAIOLA DUPLA
    # ═══════════════════════════════════════════════════════════════════════
    st.header("14. Gaiola de Esquilo Dupla")
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

    show_plot(fig_gaiola_dupla(), key="fig_14_dupla")
    st.caption("**Figura 14.1** — Curvas $T \\times n$: gaiola dupla (verde), "
               "gaiola externa (vermelho), gaiola interna (azul) e simples de referência (cinza).")

    st.divider()
    # SEÇÃO 15 — NEMA
    # ═══════════════════════════════════════════════════════════════════════
    st.header("15. Classificação NEMA de Motores em Gaiola")
    st.markdown(r"""
O NEMA (*National Electrical Manufacturers Association*) classifica os motores de indução
em gaiola de esquilo em classes segundo suas características de partida e regime,
estabelecendo um compromisso padronizado entre torque, corrente e eficiência.
""")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(r"""
**Classe A**
- Torque de partida: nominal (~150%)
- Corrente de partida: **alta** (6–8× $I_{nom}$)
- Escorregamento nominal: < 5%
- Aplicação: cargas com inércia baixa (ventiladores, bombas centrífugas)
- Construção: barras rasas, $R_2$ pequena

**Classe B** *(mais comum na indústria)*
- Torque de partida: normal (150%)
- Corrente de partida: **reduzida** (5–6× $I_{nom}$)
- Escorregamento nominal: < 5%
- Aplicação: uso geral — compressores, bombas, máquinas CNC
- Construção: barras profundas ou gaiola dupla
""")
    with col_b:
        st.markdown(r"""
**Classe C**
- Torque de partida: **alto** (200%)
- Corrente de partida: moderada (< 6× $I_{nom}$)
- Escorregamento nominal: < 5%
- Aplicação: cargas de difícil partida (britadeiras, compressores alternativos)
- Construção: gaiola dupla com gaiola externa de alta $R$

**Classe D**
- Torque de partida: **muito alto** (275%)
- Corrente de partida: moderada
- Escorregamento nominal: **alto** (8–13%)
- Aplicação: prensas, elevadores de carga, acionamentos com alto pico de torque
- Construção: barras de alta resistência (latão ou bronze)
""")

    show_plot(fig_nema_classes(), key="fig_15_nema")
    st.caption("**Figura 15.1** — Curvas T×n das classes NEMA A, B, C e D. "
               "A Classe D opera com alto escorregamento nominal; a Classe B é a mais utilizada.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 16 — PARTIDA
    # ═══════════════════════════════════════════════════════════════════════
    st.header("16. Métodos de Partida")
    st.markdown(r"""
A corrente de partida de um motor de indução pode atingir 5 a 8 vezes a corrente nominal,
causando queda de tensão na rede, solicitação mecânica e térmica excessivas.
Os métodos abaixo reduzem este impacto com diferentes graus de eficácia e custo.
""")

    st.markdown("### Partida Direta (DOL — *Direct On-Line*)")
    st.markdown(r"""
A forma mais simples: as três fases são conectadas diretamente ao motor sem limitação.

- **Vantagens**: custo mínimo, torque de partida máximo disponível, aceleração mais rápida;
- **Desvantagens**: pico de corrente elevado, queda de tensão na rede, solicitação mecânica;
- **Aplicação típica**: motores de 0,75 kW a 10 kW em redes com capacidade suficiente.

O transitório dura tipicamente 0,5 a 3 s dependendo da inércia da carga.
""")

    show_plot(fig_partida_direta(), key="fig_16_dol")
    st.caption("**Figura 16.1** — Transitório de corrente e velocidade na partida direta (DOL). "
               "A corrente cai exponencialmente enquanto a velocidade sobe em curva sigmoidal.")

    st.markdown("### Partida Estrela-Triângulo (Y/Δ)")
    st.markdown(r"""
O motor é ligado em **estrela (Y)** na partida — recebendo $V_{fase} = V_L/\sqrt{3}$ ≈ 58%
da tensão nominal — e comutado para **triângulo (Δ)** após atingir ~90% da velocidade.

| Grandeza | Ligação Y (partida) | Ligação Δ (regime) |
|---|---|---|
| Tensão de fase | $V_L / \sqrt{3}$ (58%) | $V_L$ (100%) |
| Corrente de linha | $I_{DOL} / 3$ | $I_{nom}$ |
| Torque de partida | $T_{DOL} / 3$ | Nominal |

**Requisito**: mínimo 6 terminais acessíveis. A comutação brusca Y→Δ cria um
segundo pico de corrente — a chave temporizadora deve ser ajustada com cuidado.
**Indicada para partida em vazio ou carga leve** (torque de partida reduzido 3×).
""")

    show_fig(fig_partida_estrela_triangulo(), width_frac=0.75)
    st.caption("**Figura 16.2** — Esquema das ligações Y (partida) e Δ (regime). "
               "Na ligação Y, as três bobinas compartilham o neutro; na ligação Δ, "
               "cada bobina recebe a tensão de linha completa.")

    show_plot(fig_partida_yd_transitorio(), key="fig_16_yd_trans")
    st.caption("**Figura 16.2b** — Corrente de linha no transitório Y/Δ vs DOL. "
               "Observar o segundo pico na comutação Y→Δ e a redução inicial de corrente.")

    st.markdown("### Partida Compensadora (Autotransformador)")
    st.markdown(r"""
Um **autotransformador** aplica tensão reduzida $α V_1$ ao motor durante a partida.
Após atingir a velocidade, o autotransformador é retirado do circuito.

Relações para relação de transformação $α$ (taps: 50%, 65%, 80%):

$$I_{linha} = α^2 \cdot I_{DOL} \qquad T_{partida} = α^2 \cdot T_{DOL}$$

- **Vantagem sobre Y/Δ**: $α$ ajustável → maior torque de partida para mesma corrente;
- **Vantagem**: comutação suave (sem segundo pico de corrente);
- **Desvantagem**: custo e volume maiores (autotransformador adicional).
- **Aplicação**: motores de médio e grande porte (15 kW a vários MW).
""")

    show_fig(fig_partida_compensadora(), width_frac=0.72)
    st.caption("**Figura 16.3** — Esquema da partida compensadora: "
               "rede → autotransformador (taps 50/65/80%) → motor. "
               "A tensão reduzida α·V₁ limita corrente e torque por α².")

    show_plot(fig_partida_compensadora_barras(), key="fig_16_comp_bar")
    st.caption("**Figura 16.3b** — Corrente e torque de partida para cada tap do AT. "
               "Em todos os casos, a redução é proporcional a α².")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # SEÇÃO 17 — CONTROLE VELOCIDADE
    # ═══════════════════════════════════════════════════════════════════════
    st.header("17. Controle de Velocidade")
    st.markdown(r"""
Historicamente, motores CC dominavam aplicações de velocidade variável pela
simplicidade do controle. Com o desenvolvimento dos **controladores de estado sólido**
(inversores de frequência / VFDs), os motores de indução gaiola tornaram-se competitivos:
mais baratos, robustos e adequados a altas velocidades — superando os motores CC.

Os principais métodos de controle de velocidade são:
""")

    st.markdown("### 1. Mudança do Número de Polos")
    st.markdown(r"""
Enrolamentos com dois ou mais conjuntos de bobinas permitem rearranjamento para
diferentes números de polos, alterando $n_s = 120f/p$.

- Velocidade **discreta** (2, 4, 6 ou 8 polos);
- Motor de **dois velocidades**: um único conjunto de bobinas com ligação dahlander
  (relação 2:1 de velocidades);
- Sem equipamento eletrônico adicional — chaveamento simples;
- Limitado a 2–3 velocidades fixas.
""")

    st.markdown("### 2. Controle por Tensão Terminal")
    st.markdown(r"""
Reduzindo $V_1$, o torque cai proporcionalmente a $V_1^2$, deslocando o ponto de
operação para maior escorregamento. O controle pode ser feito por:

- **Chaves de estado sólido** (SCRs / TRIACs) — controle de ângulo de disparo;
- **Variedades**: reguladores de tensão CA.

**Limitações**: eficiência cai (maior $s$ → maior $P_{cu,2}$); faixa de controle restrita;
torque cai mais rapidamente que a velocidade — instabilidade para cargas constantes.
Adequado apenas para cargas com torque proporcional à velocidade (ventiladores, bombas).
""")

    show_plot(fig_controle_tensao_terminal(), key="fig_17_V")
    st.caption("**Figura 17.1** — Controle por tensão terminal: T ∝ V₁². "
               "Para carga com torque variável (curva pontilhada), há ponto de operação estável "
               "em cada nível de tensão.")

    st.markdown("### 3. Controle por Frequência (V/f Constante)")
    st.markdown(r"""
Mantendo a relação $V_1/f$ constante, o **fluxo magnético** permanece constante e
$T_{max}$ é preservado em toda a faixa de velocidade:

$$\frac{V_1}{f} = 	ext{const} \quad \Rightarrow \quad \Phi_m \approx 	ext{const}$$

A velocidade síncrona é proporcional à frequência: $n_s = 120f/p$.

- **Implementação**: inversor de frequência (VFD) — retifica a rede e gera CA variável;
- **Faixa**: tipicamente 5–120 Hz (para frequência nominal de 60 Hz);
- **Abaixo da base**: V/f constante (torque constante);
- **Acima da base** (*field weakening*): $f$ aumenta mas $V_1$ fixo → fluxo cai → torque
  máximo cai, mas potência constante (análogo ao enfraquecimento de campo no motor CC).
""")

    show_plot(fig_controle_frequencia(), key="fig_17_f")
    st.caption("**Figura 17.2** — Controle V/f constante: a família de curvas T×n desloca-se "
               "proporcionalmente a $f$, mantendo $T_{max}$ constante e $n_s$ proporcional a $f$.")

    st.markdown("### 4. Controle em Malha Fechada")
    st.markdown(r"""
A malha fechada adiciona um **sensor de velocidade** (encoder ou tacômetro) e um
**controlador** (PI/PID) que ajusta continuamente a frequência e a tensão do inversor
para seguir a referência de velocidade $n^*$:

$$e(t) = n^* - n \quad \Rightarrow \quad 	ext{controlador} \quad \Rightarrow \quad f, V_1$$
""")

    show_fig(fig_malha_fechada_velocidade(), width_frac=0.88)
    st.caption("**Figura 17.3** — Diagrama de blocos do controle em malha fechada de velocidade: "
               "referência → controlador PI → inversor → MIT → realimentação do encoder.")

    st.markdown("#### Estratégia de Escorregamento Constante")
    st.markdown(r"""
Uma estratégia avançada dentro da malha fechada é manter o **escorregamento constante**
($s = 	ext{const}$), o que significa operar sempre no mesmo ponto relativo da curva T×n:

- Eficiência e fator de potência **otimizados** em qualquer velocidade;
- O controlador monitora $n$ e $n_s$ e ajusta $f$ para manter $s = (n_s - n)/n_s$ fixo;
- Equivalente ao controle de campo orientado simplificado.

Os pontos de operação formam uma linha quase linear sobre as curvas T×n da família V/f.
""")

    show_plot(fig_escorregamento_constante(), key="fig_17_s")
    st.caption("**Figura 17.4** — Controle por escorregamento constante: os pontos de operação "
               "(linha tracejada) seguem o mesmo valor de $s$ em todas as frequências, "
               "otimizando eficiência e fator de potência.")

    st.divider()

    st.header("🎛️ Exploradores Interativos")

    tabs = st.tabs([
        "1 — Curva T × n",
        "2 — Circ. Equivalente",
        "3 — Tensão → T × n",
        "4 — Partida",
        "5 — Eficiência",
        "6 — Corrente e fp",
        "7 — Efic. × Carga",
    ])
    with tabs[0]: exp_torque_velocidade()
    with tabs[1]: exp_circuito_equivalente()
    with tabs[2]: exp_efeito_tensao()
    with tabs[3]: exp_partida()
    with tabs[4]: exp_eficiencia()
    with tabs[5]: exp_corrente_fator_potencia()
    with tabs[6]: exp_eficiencia_carga()

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
