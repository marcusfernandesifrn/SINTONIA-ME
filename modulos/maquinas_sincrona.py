"""
🌐 Máquinas Síncronas Polifásicas
Disciplina: Conversão Eletromecânica de Energia I
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
import cmath
import math
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

    # ═══════════════════════════════════════════════════════════════════════════
    # FIGURAS — matplotlib
    # ═══════════════════════════════════════════════════════════════════════════

    def fig_estrutura_construtiva_mes():
        """Seção transversal comparativa: rotor cilíndrico vs polos salientes."""
        fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))
        fig.patch.set_alpha(0)

        for ax in axes:
            ax.set_facecolor("none")
            ax.set_aspect("equal")
            ax.axis("off")
            ax.set_xlim(-5.5, 5.5)
            ax.set_ylim(-5.5, 5.8)

        def draw_stator(ax):
            """Estator comum aos dois tipos."""
            ax.add_patch(mpatches.Wedge(
                (0, 0), 4.8, 0, 360, width=0.9,
                fc="#d0d8e8", ec=TX, lw=1.2))
            # Enrolamentos do estator (fase A, B, C) — 6 bobinas
            fase_info = [
                (30,  AZ, "a"), (210, AZ, "a'"),
                (150, VD, "b"), (330, VD, "b'"),
                (270, LR, "c"), (90,  LR, "c'"),
            ]
            for ang_deg, cor, lbl in fase_info:
                ang = math.radians(ang_deg)
                rx, ry = 3.85 * math.cos(ang), 3.85 * math.sin(ang)
                ax.add_patch(mpatches.Circle(
                    (rx, ry), 0.42, fc=cor, ec="white", lw=1.2, alpha=0.88, zorder=4))
                ax.text(rx, ry, lbl, ha="center", va="center",
                        fontsize=7.5, color="white", fontweight="bold", zorder=5)

        # ── Painel esquerdo: Rotor Cilíndrico ─────────────────────────────────
        ax0 = axes[0]
        draw_stator(ax0)
        # Entreferro
        ax0.add_patch(mpatches.Wedge(
            (0, 0), 3.45, 0, 360, width=0.35, fc="#f0f4ff", ec=CZ, lw=0.5, alpha=0.6))
        # Rotor cilíndrico (núcleo homogêneo)
        ax0.add_patch(mpatches.Wedge(
            (0, 0), 3.1, 0, 360, width=2.2, fc="#c8d8f0", ec=TX, lw=1.2))
        # Enrolamento de campo distribuído (ranhuras)
        for ang_deg in range(0, 360, 30):
            ang = math.radians(ang_deg)
            rx, ry = 2.55 * math.cos(ang), 2.55 * math.sin(ang)
            ax0.add_patch(mpatches.Circle(
                (rx, ry), 0.28, fc=LR, ec="white", lw=0.8, alpha=0.75, zorder=4))
        # Eixo
        ax0.add_patch(mpatches.Circle((0, 0), 0.55, fc=CZ, ec=TX, lw=1.0, zorder=5))
        ax0.text(0, 0, "⊕", ha="center", va="center",
                 fontsize=14, color="white", zorder=6)
        ax0.set_title("Rotor Cilíndrico\n(polos não-salientes, alta velocidade)",
                      fontsize=10, fontweight="bold", color=AZ, pad=8)
        # Legendas
        ax0.text(-5.2, -5.1, "● Estator (armadura)", fontsize=8, color=TX)
        ax0.text(-5.2, -5.6, "● Enrol. de campo If distribuído", fontsize=8, color=LR)

        # ── Painel direito: Polos Salientes ───────────────────────────────────
        ax1 = axes[1]
        draw_stator(ax1)
        ax1.add_patch(mpatches.Wedge(
            (0, 0), 3.45, 0, 360, width=0.35, fc="#f0f4ff", ec=CZ, lw=0.5, alpha=0.6))
        # Dois polos salientes (N e S)
        for ang_base, cor, lbl in [(90, VM, "N"), (270, AZ, "S")]:
            for dang in range(-38, 39, 4):
                ang = math.radians(ang_base + dang)
                for r in np.linspace(1.2, 2.9, 6):
                    rx, ry = r * math.cos(ang), r * math.sin(ang)
                    ax1.add_patch(mpatches.Circle(
                        (rx, ry), 0.16,
                        fc=cor, ec="none", alpha=0.18, zorder=2))
            # Polo sólido
            polo_angulos = np.linspace(
                math.radians(ang_base - 40), math.radians(ang_base + 40), 60)
            rx_out = [3.0 * math.cos(a) for a in polo_angulos]
            ry_out = [3.0 * math.sin(a) for a in polo_angulos]
            rx_in  = [1.1 * math.cos(a) for a in reversed(polo_angulos)]
            ry_in  = [1.1 * math.sin(a) for a in reversed(polo_angulos)]
            ax1.fill(rx_out + rx_in, ry_out + ry_in,
                     fc="#b8cce4", ec=TX, lw=1.0, alpha=0.90, zorder=3)
            # Enrolamento de campo concentrado
            for r_coil in [1.7, 2.2, 2.65]:
                for side in [-0.38, 0.38]:
                    ang_s = math.radians(ang_base + side * 60)
                    ax1.add_patch(mpatches.Circle(
                        (r_coil * math.cos(ang_s), r_coil * math.sin(ang_s)),
                        0.22, fc=LR, ec="white", lw=0.7, alpha=0.82, zorder=4))
            ang_r = math.radians(ang_base)
            ax1.text(1.95 * math.cos(ang_r), 1.95 * math.sin(ang_r), lbl,
                     ha="center", va="center", fontsize=15,
                     color=cor, fontweight="bold", zorder=5)
        # Eixo
        ax1.add_patch(mpatches.Circle((0, 0), 0.55, fc=CZ, ec=TX, lw=1.0, zorder=6))
        ax1.set_title("Polos Salientes\n(enrolamento concentrado, baixa velocidade)",
                      fontsize=10, fontweight="bold", color=VM, pad=8)
        ax1.text(-5.2, -5.1, "● Estator (armadura)", fontsize=8, color=TX)
        ax1.text(-5.2, -5.6, "● Enrol. de campo If concentrado", fontsize=8, color=LR)

        fig.suptitle("Estrutura Construtiva da Máquina Síncrona",
                     fontsize=13, fontweight="bold", color=TX, y=1.01)
        fig.tight_layout(pad=0.8)
        return fig

    def fig_velocidade_sincrona_mes():
        """Plotly: velocidade síncrona ns × número de polos para 50 e 60 Hz."""
        polos = np.array([2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 60])
        ns_60 = 120 * 60 / polos
        ns_50 = 120 * 50 / polos

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=polos, y=ns_60, mode="lines+markers",
            name="60 Hz (Brasil/EUA)",
            line=dict(color=AZ, width=2.8),
            marker=dict(size=8, color=AZ),
            hovertemplate="p=%{x}<br>nₛ=%{y:.0f} rpm"))
        fig.add_trace(go.Scatter(
            x=polos, y=ns_50, mode="lines+markers",
            name="50 Hz (Europa)",
            line=dict(color=VM, width=2.8, dash="dash"),
            marker=dict(size=8, color=VM, symbol="diamond"),
            hovertemplate="p=%{x}<br>nₛ=%{y:.0f} rpm"))

        fig.update_layout(
            title=dict(text="Velocidade Síncrona  nₛ = 120f / p",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Número de polos (p)", font=dict(size=14, color=TX)),
                       tickvals=list(polos), tickfont=dict(size=12),
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Velocidade síncrona nₛ (rpm)",
                                  font=dict(size=14, color=TX)),
                       tickfont=dict(size=12),
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
            height=420, margin=dict(l=75, r=30, t=60, b=70),
        )
        return fig

    def fig_geracao_tensao_mes():
        """Esquema de geração de Ef por rotação de Φf — sem sobreposições."""
        fig, ax = plt.subplots(figsize=(12, 4.5), facecolor='white')
        ax.set_facecolor('white'); ax.axis('off')
        ax.set_xlim(0, 14); ax.set_ylim(0, 5)

        def arrow(x1, y1, x2, y2, cor, lw=2.2, ms=14):
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="-|>", color=cor,
                                        lw=lw, mutation_scale=ms))

        # ── Rotor ─────────────────────────────────────────────────────────────
        ax.add_patch(mpatches.Circle((2.2, 3.0), 1.3,
                                      fc="#dce8f8", ec=AZ, lw=1.8))
        ax.text(2.2, 3.20, "Rotor", ha="center",
                fontsize=10, color=AZ, fontweight="bold")
        ax.text(2.2, 2.70, r"(excitado por $I_f$)", ha="center",
                fontsize=8.5, color=CZ, style="italic")

        # Arco de rotação
        arc = np.linspace(0.28, 1.42, 40)
        ax.plot(2.2 + 1.7*np.cos(arc), 3.0 + 1.7*np.sin(arc), color=LR, lw=2.2)
        ax.annotate("",
            xy=(2.2 + 1.7*math.cos(1.42), 3.0 + 1.7*math.sin(1.42)),
            xytext=(2.2 + 1.7*math.cos(1.32), 3.0 + 1.7*math.sin(1.32)),
            arrowprops=dict(arrowstyle="-|>", color=LR, lw=2.2, mutation_scale=14))
        ax.text(4.2, 4.50, r"$n_s$", fontsize=13, color=LR, fontweight="bold")

        # Φf: de x=3.5 (borda rotor) até x=4.8 (antes do bloco estator em x=5.5)
        arrow(3.5, 3.0, 4.8, 3.0, VM)
        ax.text(4.15, 3.33, r"$\Phi_f$", fontsize=13, color=VM, fontweight="bold")

        # ── Estator ────────────────────────────────────────────────────────────
        ax.add_patch(mpatches.FancyBboxPatch(
            (5.5, 2.0), 2.0, 2.0,
            boxstyle="round,pad=0.10", fc="#f0f4ff", ec=AZ, lw=1.8))
        ax.text(6.5, 3.20, "Estator", ha="center",
                fontsize=10, color=AZ, fontweight="bold")
        ax.text(6.5, 2.72, r"(armadura, $N$ voltas)", ha="center",
                fontsize=8.5, color=CZ, style="italic")

        # Ef: de x=7.5 até x=9.2
        arrow(7.5, 3.0, 9.2, 3.0, VD)
        ax.text(8.35, 3.33, r"$E_f$", fontsize=13, color=VD, fontweight="bold")

        # Sinal senoidal
        t_s = np.linspace(0, 2*np.pi, 200)
        ax.plot(9.5 + t_s * 0.60, 3.0 + 1.0*np.sin(t_s), color=VD, lw=2.2)
        ax.text(12.2, 2.48, r"$f,\ 3\phi$", fontsize=11, color=VD)

        # ── Equações (rodapé) ─────────────────────────────────────────────────
        ax.text(1.2, 1.20, r"$n_s = \dfrac{120\,f}{p}$",
                fontsize=13, color=TX, va="center")
        ax.text(5.2, 1.20,
                r"$E_f = 4{,}44\,f\,N\,\Phi_f\,K_w = k_f\,n_s\,\Phi_f$",
                fontsize=13, color=TX, va="center")

        ax.set_title(
            r"Geração de Tensão — Rotação de $\Phi_f$ induz $E_f$ no Estator",
            fontsize=13, fontweight="bold", color=TX, pad=10)
        fig.tight_layout(pad=0.5)
        return fig

    def fig_curva_occ_mes():
        """Plotly: Curva de Circuito Aberto (OCC) com dados reais 195 MVA, 15 kV."""
        # Dados SEN6 Q3 — 195 MVA, 15 kV, 60 Hz
        If_pts = np.array([0, 150, 300, 450, 600, 750, 900, 1200])
        Ef_pts = np.array([0, 3.75, 7.5, 11.2, 13.6, 15.0, 15.8, 16.5])  # kV L-L

        # Linha do entreferro (AGL) — linear pelos dois primeiros pontos não nulos
        m_agl = Ef_pts[2] / If_pts[2]
        If_full = np.linspace(0, 1300, 300)
        Ef_agl  = m_agl * If_full

        # Interpolação suave da OCC
        from numpy.polynomial import polynomial as P
        coeffs = np.polyfit(If_pts, Ef_pts, 5)
        Ef_occ = np.clip(np.polyval(coeffs, If_full), 0, 18)

        # Linha de Xs saturado (na corrente nominal If=750 A)
        If_scc = 750; Ia_scc = 7000
        Ef_nom_fase = 15.0 / math.sqrt(3)  # kV fase
        Xs_sat = (Ef_nom_fase * 1000) / Ia_scc  # Ω

        fig = go.Figure()
        # AGL
        fig.add_trace(go.Scatter(
            x=If_full, y=Ef_agl, mode="lines", name="Linha do entreferro (AGL)",
            line=dict(color=CZ, width=1.8, dash="dash")))
        # OCC suave
        fig.add_trace(go.Scatter(
            x=If_full, y=Ef_occ, mode="lines", name="OCC (circuito aberto)",
            line=dict(color=AZ, width=3.0)))
        # Pontos medidos
        fig.add_trace(go.Scatter(
            x=If_pts, y=Ef_pts, mode="markers", name="Pontos medidos",
            marker=dict(color=AZ, size=9, symbol="circle",
                        line=dict(color="white", width=1.5))))
        # Tensão nominal
        fig.add_hline(y=15.0, line=dict(color=VM, width=1.4, dash="dot"))
        fig.add_annotation(x=1250, y=15.3, text="<b>V_nom = 15 kV</b>",
                           showarrow=False, font=dict(size=11, color=VM))
        # If nominal
        fig.add_vline(x=750, line=dict(color=LR, width=1.2, dash="dot"))
        fig.add_annotation(x=780, y=3.0, text="If = 750 A", textangle=-90,
                           showarrow=False, font=dict(size=10, color=LR))

        fig.update_layout(
            title=dict(text="Curva de Magnetização (OCC) — 195 MVA, 15 kV, 60 Hz",
                       font=dict(size=16, color=TX)),
            xaxis=dict(title=dict(text="Corrente de campo If (A)",
                                  font=dict(size=14, color=TX)),
                       tickfont=dict(size=13), range=[0, 1350],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Tensão de linha Vₗₗ (kV)",
                                  font=dict(size=14, color=TX)),
                       tickfont=dict(size=13), range=[0, 18],
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
            height=440, margin=dict(l=75, r=30, t=65, b=70),
        )
        return fig

    def fig_reacao_armadura_mes():
        """Plotly: composição vetorial Φf + Φa = Φr — reação da armadura."""
        fig = go.Figure()

        # Vetores definidos como (ox, oy, dx, dy, cor, nome)
        # Φf: do ponto P até o topo (campo do rotor)
        # Φa: do topo de Φf
        # Φr: de P até o topo de Φa (resultante)
        ox, oy = 0.0, 0.0

        # Coordenadas dos fasores
        Pf_x, Pf_y = 2.4, 2.2    # Φf
        Pa_x, Pa_y = 1.5, -1.0   # Φa (a partir da ponta de Φf)
        Pr_x = Pf_x + Pa_x       # Φr = Φf + Φa
        Pr_y = Pf_y + Pa_y

        def arrow(ox, oy, dx, dy, cor, nome, dash="solid", w=3.0):
            fig.add_trace(go.Scatter(
                x=[ox, ox+dx], y=[oy, oy+dy], mode="lines",
                line=dict(color=cor, width=w, dash=dash),
                name=nome, showlegend=True,
                hovertemplate=f"{nome}: |F|={math.hypot(dx,dy):.2f} pu<extra></extra>"))
            fig.add_annotation(
                x=ox+dx, y=oy+dy, ax=ox, ay=oy,
                xref="x", yref="y", axref="x", ayref="y",
                arrowhead=2, arrowsize=1.5, arrowwidth=3.0,
                arrowcolor=cor, showarrow=True, text="")
            # Label no meio do fasor
            fig.add_annotation(
                x=ox+dx*0.55, y=oy+dy*0.55,
                text=f"<b>{nome}</b>", showarrow=False,
                font=dict(size=14, color=cor),
                bgcolor="rgba(255,255,255,0.80)", borderpad=3)

        # Φf (origem → ponta)
        arrow(ox, oy, Pf_x, Pf_y, VM, "Φ<sub>f</sub>")
        # Φa (ponta de Φf → ponta de Φr)
        arrow(ox+Pf_x, oy+Pf_y, Pa_x, Pa_y, VD, "Φ<sub>a</sub>")
        # Φr (origem → ponta final, resultado)
        arrow(ox, oy, Pr_x, Pr_y, AZ, "Φ<sub>r</sub>", dash="dot", w=2.5)

        # Ponto de fechamento
        fig.add_trace(go.Scatter(
            x=[ox+Pr_x], y=[oy+Pr_y], mode="markers",
            marker=dict(color=TX, size=10, symbol="circle"),
            showlegend=False, hoverinfo="skip"))

        # Equação como anotação
        fig.add_annotation(
            x=0.05, y=0.97, xref="paper", yref="paper",
            text="<b>Φ<sub>r</sub> = Φ<sub>f</sub> + Φ<sub>a</sub></b>",
            showarrow=False,
            font=dict(size=16, color=TX),
            bgcolor="rgba(240,244,255,0.90)",
            bordercolor=AZ, borderwidth=1.5, borderpad=6)

        # Legenda dos efeitos por fp
        fig.add_annotation(
            x=1.02, y=0.95, xref="paper", yref="paper",
            text=(
                "<b>Efeito por fator de potência:</b><br>"
                "fp=1 → Φ<sub>a</sub> ⊥ Φ<sub>f</sub> (distorção)<br>"
                "fp atr. → Φ<sub>a</sub> opõe Φ<sub>f</sub> (desmagnetiza)<br>"
                "fp adi. → Φ<sub>a</sub> reforça Φ<sub>f</sub> (magnetiza)"
            ),
            showarrow=False,
            font=dict(size=11, color=TX),
            bgcolor="rgba(255,255,255,0.90)",
            bordercolor=CZ, borderwidth=1, borderpad=8,
            align="left", xanchor="left", yanchor="top")

        fig.add_hline(y=0, line=dict(color=CZ, width=0.6, dash="dot"))
        fig.add_vline(x=0, line=dict(color=CZ, width=0.6, dash="dot"))

        fig.update_layout(
            title=dict(
                text="Reação da Armadura — Composição Vetorial dos Fluxos",
                font=dict(size=16, color=TX)),
            xaxis=dict(
                range=[-0.5, 4.5], scaleanchor="y",
                showgrid=True, gridcolor="rgba(128,128,128,.15)",
                zeroline=False, tickfont=dict(size=12),
                title=dict(text="Componente horizontal (pu)", font=dict(size=12, color=CZ))),
            yaxis=dict(
                range=[-0.8, 3.2],
                showgrid=True, gridcolor="rgba(128,128,128,.15)",
                zeroline=False, tickfont=dict(size=12),
                title=dict(text="Componente vertical (pu)", font=dict(size=12, color=CZ))),
            legend=dict(font=dict(size=13), bgcolor="rgba(255,255,255,0.88)",
                        x=0.01, y=0.01, xanchor="left", yanchor="bottom"),
            height=480, margin=dict(l=65, r=220, t=65, b=60),
        )
        return fig

    def fig_circuito_equivalente_gerador_mes():
        """Schemdraw: circuito equivalente por fase — modo GERADOR.
        Labels +/− adicionados via matplotlib com fontsize uniforme."""
        import tempfile, os
        with schemdraw.Drawing(show=False) as d:
            d.config(unit=3.2, fontsize=12)

            d.push()
            elm.Line().down(d.unit * 0.5)
            elm.SourceSin().down().label(r"$E_f$", loc="bottom")
            elm.Line().down(d.unit * 0.5)
            elm.Line().right(d.unit * 3.0).dot(open=True)
            d.pop()

            elm.Line().right(d.unit * 0.5)
            elm.Inductor().right().label(r"$jX_s$", loc="top")
            elm.Resistor().right().label(r"$R_a$")
            Ia_elm = elm.Line().right(d.unit * 0.5).dot(open=True)
            elm.Gap().down(d.unit * 2.0)   # sem label — adicionado abaixo

            elm.CurrentLabel(top=True, length=1, ofst=0.3).at(Ia_elm).label(r"$I_a$")

            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.close()
            d.save(tmp.name, dpi=160)

            # Labels com coordenadas numéricas fixas (Gap em x=9.6, y: 0→-6.4)
            mpl_fig = d.fig.getfig()
            ax = mpl_fig.get_axes()[0]
            ax.text(10.15, -0.35, "+",     ha="left", va="center", fontsize=13)
            ax.text(10.15, -3.2,  r"$V_t$", ha="left", va="center", fontsize=13)
            ax.text(10.15, -6.05, "−",     ha="left", va="center", fontsize=13)
            mpl_fig.savefig(tmp.name, dpi=160, bbox_inches="tight")
            plt.close(mpl_fig)

        with open(tmp.name, "rb") as fh:
            buf = io.BytesIO(fh.read())
        os.unlink(tmp.name)
        buf.seek(0)
        return buf

    def fig_circuito_equivalente_motor_mes():
        """Schemdraw: circuito equivalente por fase — modo MOTOR.
        Labels +/− adicionados via matplotlib com fontsize uniforme."""
        import tempfile, os
        with schemdraw.Drawing(show=False) as d:
            d.config(unit=3.2, fontsize=12)

            d.push()
            elm.Line().down(d.unit * 0.5)
            elm.SourceSin().down().label(r"$E_f$", loc="bottom")
            elm.Line().down(d.unit * 0.5)
            elm.Line().right(d.unit * 3.0).dot(open=True)
            d.pop()

            elm.Line().right(d.unit * 0.5)
            elm.Inductor().right().label(r"$jX_s$", loc="top")
            elm.Resistor().right().label(r"$R_a$")
            Ia_elm = elm.Line().right(d.unit * 0.5).dot(open=True)
            elm.Gap().down(d.unit * 2.0)   # sem label — adicionado abaixo

            elm.CurrentLabel(top=True, length=1, ofst=0.3).at(Ia_elm).label(r"$I_a$").reverse()

            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.close()
            d.save(tmp.name, dpi=160)

            # Labels com coordenadas numéricas fixas
            mpl_fig = d.fig.getfig()
            ax = mpl_fig.get_axes()[0]
            ax.text(10.15, -0.35, "+",      ha="left", va="center", fontsize=13)
            ax.text(10.15, -3.2,  r"$V_t$", ha="left", va="center", fontsize=13)
            ax.text(10.15, -6.05, "−",      ha="left", va="center", fontsize=13)
            mpl_fig.savefig(tmp.name, dpi=160, bbox_inches="tight")
            plt.close(mpl_fig)

        with open(tmp.name, "rb") as fh:
            buf = io.BytesIO(fh.read())
        os.unlink(tmp.name)
        buf.seek(0)
        return buf

    def fig_diagrama_fasorial_mes(Vt=1.0, Ef=1.2, delta_deg=25.0,
                                   Xs=1.0, Ra=0.0, modo="Gerador"):
        """Plotly: diagrama fasorial cilíndrico interativo."""
        delta = math.radians(delta_deg)
        Vt_c  = complex(Vt, 0)
        Ef_c  = complex(Ef * math.cos(delta), Ef * math.sin(delta))

        if modo == "Gerador":
            Ia_c  = (Ef_c - Vt_c) / complex(Ra, Xs)
            RaIa  =  Ra * Ia_c
            jXsIa =  complex(0, Xs) * Ia_c
        else:
            Ia_c  = (Vt_c - Ef_c) / complex(Ra, Xs)
            RaIa  = -Ra * Ia_c
            jXsIa = -complex(0, Xs) * Ia_c

        fig = go.Figure()

        def fasor(ox, oy, dx, dy, cor, nome, dash="solid", width=2.8):
            fig.add_trace(go.Scatter(
                x=[ox, ox+dx], y=[oy, oy+dy], mode="lines",
                line=dict(color=cor, width=width, dash=dash),
                showlegend=True, name=nome,
                hovertemplate=f"{nome}: {math.hypot(dx,dy):.3f} pu<extra></extra>"))
            fig.add_annotation(
                x=ox+dx, y=oy+dy, ax=ox, ay=oy,
                xref="x", yref="y", axref="x", ayref="y",
                arrowhead=2, arrowsize=1.4, arrowwidth=2.5,
                arrowcolor=cor, showarrow=True, text="")
            mx = ox + dx*0.55; my = oy + dy*0.55
            fig.add_annotation(x=mx, y=my, text=f"<b>{nome}</b>",
                               showarrow=False,
                               font=dict(size=13, color=cor),
                               bgcolor="rgba(255,255,255,0.78)", borderpad=2)

        fasor(0, 0, Vt_c.real, Vt_c.imag, AZ, "Vₜ", width=3.0)
        Ia_sc = Ia_c * 0.75
        fasor(0, 0, Ia_sc.real, Ia_sc.imag, VD, "Iₐ", dash="dot", width=2.2)
        fasor(0, 0, Ef_c.real, Ef_c.imag, VM, "Eƒ", width=3.0)
        if abs(RaIa) > 0.01:
            fasor(Vt_c.real, Vt_c.imag, RaIa.real, RaIa.imag, LR, "Rₐ·Iₐ", width=2.2)
        origin = Vt_c + RaIa
        fasor(origin.real, origin.imag, jXsIa.real, jXsIa.imag, CZ, "jXₛ·Iₐ", width=2.2)

        # Arco do ângulo δ
        arc_r = 0.22
        arc_t = np.linspace(0, delta, 30)
        fig.add_trace(go.Scatter(
            x=arc_r*np.cos(arc_t), y=arc_r*np.sin(arc_t),
            mode="lines", line=dict(color=TX, width=1.5, dash="dash"),
            showlegend=False, hoverinfo="skip"))
        fig.add_annotation(
            x=arc_r*math.cos(delta/2)*1.6, y=arc_r*math.sin(delta/2)*1.6,
            text="<b>δ</b>", showarrow=False, font=dict(size=14, color=TX))

        fig.add_hline(y=0, line=dict(color=CZ, width=0.8, dash="dot"))
        fig.add_vline(x=0, line=dict(color=CZ, width=0.8, dash="dot"))

        lim = max(Vt, Ef, abs(Ia_c)*0.75) * 1.35
        fig.update_layout(
            title=dict(
                text=f"Diagrama Fasorial — {modo} Cilíndrico  (δ = {delta_deg:.0f}°)",
                font=dict(size=16, color=TX)),
            xaxis=dict(range=[-lim*0.4, lim*1.15], scaleanchor="y",
                       showgrid=True, gridcolor="rgba(128,128,128,.15)",
                       zeroline=False, tickfont=dict(size=12),
                       title=dict(text="Real (pu)", font=dict(size=12, color=CZ))),
            yaxis=dict(range=[-lim*0.55, lim*0.9],
                       showgrid=True, gridcolor="rgba(128,128,128,.15)",
                       zeroline=False, tickfont=dict(size=12),
                       title=dict(text="Imaginário (pu)", font=dict(size=12, color=CZ))),
            legend=dict(font=dict(size=12), bgcolor="rgba(255,255,255,0.85)",
                        x=0.01, y=0.99, xanchor="left", yanchor="top"),
            height=480, margin=dict(l=65, r=30, t=60, b=60),
        )
        return fig

    def fig_occ_scc_mes():
        """Plotly: OCC + SCC + AGL sobrepostas com Xs_sat e Xs_nsat."""
        If_pts = np.array([0, 150, 300, 450, 600, 750, 900, 1200])
        Ef_pts = np.array([0, 3.75, 7.5, 11.2, 13.6, 15.0, 15.8, 16.5])
        Ifscc = 750; Iascc = 7000

        coeffs = np.polyfit(If_pts, Ef_pts, 5)
        If_full = np.linspace(0, 1300, 300)
        Ef_occ  = np.clip(np.polyval(coeffs, If_full), 0, 18)

        m_agl = Ef_pts[2] / If_pts[2]
        Ef_agl = m_agl * If_full

        m_ia = (Iascc / Ifscc) / 1000
        Ia_scc = If_full * m_ia

        # Valores nominais
        Vf_nom = 15.0 / math.sqrt(3)    # kV fase
        m_Vs   = Ef_pts[5] / If_pts[5]  # slope saturado
        m_Vns  = Ef_pts[3] / If_pts[3]  # slope AGL

        Xs_sat = (m_Vs / math.sqrt(3) * 1000) / (m_ia * 1000)
        Xs_nsat= (m_Vns / math.sqrt(3) * 1000) / (m_ia * 1000)

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Scatter(x=If_full, y=Ef_agl, mode="lines",
            name="AGL", line=dict(color=CZ, width=1.8, dash="dash")),
            secondary_y=False)
        fig.add_trace(go.Scatter(x=If_full, y=Ef_occ, mode="lines",
            name="OCC (kV L-L)", line=dict(color=AZ, width=3.0)),
            secondary_y=False)
        fig.add_trace(go.Scatter(x=If_pts, y=Ef_pts, mode="markers",
            name="OCC — pontos",
            marker=dict(color=AZ, size=9, line=dict(color="white", width=1.5))),
            secondary_y=False)
        fig.add_trace(go.Scatter(x=If_full, y=Ia_scc, mode="lines",
            name="SCC (kA)", line=dict(color=VM, width=2.5)),
            secondary_y=True)
        fig.add_trace(go.Scatter(x=[If_pts[5]], y=[Ia_scc[list(If_full).index(
            min(If_full, key=lambda x: abs(x - 750)))]],
            mode="markers", name="SCC — ponto nominal",
            marker=dict(color=VM, size=10, symbol="x",
                        line=dict(color=VM, width=2))),
            secondary_y=True)

        # Anotações Xs
        fig.add_annotation(x=750, y=2.0,
            text=f"Xs_sat ≈ {Xs_sat:.2f} Ω<br>Xs_nsat ≈ {Xs_nsat:.2f} Ω",
            showarrow=False, bgcolor="rgba(255,255,255,0.9)",
            bordercolor=CZ, borderwidth=1,
            font=dict(size=12, color=TX))

        fig.update_layout(
            title=dict(text="OCC + SCC + AGL — Determinação de Xs saturado e não-saturado",
                       font=dict(size=15, color=TX)),
            xaxis=dict(title=dict(text="Corrente de campo If (A)",
                                  font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[0, 1350],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Tensão de linha Vₗₗ (kV)",
                                  font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[0, 19],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis2=dict(title=dict(text="Corrente de armadura Ia (kA)",
                                   font=dict(size=14, color=VM)),
                        tickfont=dict(size=12, color=VM),
                        range=[0, 25], gridcolor="rgba(0,0,0,0)"),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.22),
            height=460, margin=dict(l=75, r=75, t=65, b=110),
        )
        return fig

    def fig_barramento_infinito_mes():
        """Matplotlib: diagrama de blocos — gerador → barramento infinito."""
        fig, ax = plt.subplots(figsize=(11, 3.8), facecolor='white')
        ax.set_facecolor('white'); ax.axis('off')
        ax.set_xlim(0, 14); ax.set_ylim(0, 4)

        def bloco(cx, cy, w, h, txt, cor, fs=10):
            ax.add_patch(mpatches.FancyBboxPatch(
                (cx - w/2, cy - h/2), w, h,
                boxstyle="round,pad=0.10", fc="#f0f4ff", ec=cor, lw=2.0))
            ax.text(cx, cy, txt, ha="center", va="center",
                    fontsize=fs, color=TX, fontweight="bold")

        def seta(x1, y1, x2, y2, cor=TX, lw=1.8):
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="-|>", color=cor,
                                        lw=lw, mutation_scale=14))

        CY = 2.0
        bloco(1.4,  CY, 2.2, 1.2, "Turbina /\nPrimário",      LR)
        bloco(4.0,  CY, 2.2, 1.2, "Gerador\nSíncrono (GS)",   AZ)
        bloco(7.0,  CY, 2.2, 1.2, "Transformador\nElevador",   VD)
        bloco(10.2, CY, 2.4, 1.2, "Barramento\nInfinito",      VM)

        seta(2.5, CY, 2.9, CY)
        seta(5.1, CY, 5.9, CY)
        seta(8.1, CY, 9.0, CY)
        seta(11.4, CY, 12.5, CY)
        ax.text(13.0, CY, "≡ Rede", ha="center", va="center",
                fontsize=10, color=VM, fontweight="bold")

        # Sinais
        ax.text(3.0, CY + 0.80, r"$T_{mec}$", ha="center",
                fontsize=10, color=LR, style="italic")
        ax.text(6.5, CY + 0.80, r"$E_f, I_a$", ha="center",
                fontsize=10, color=AZ, style="italic")
        ax.text(9.6, CY + 0.80, r"$V_\infty, f$", ha="center",
                fontsize=10, color=VM, style="italic")

        # Excitação de campo
        ax.plot([4.0, 4.0], [CY - 0.6, CY - 1.4], color=LR, lw=1.8, ls="--")
        ax.text(4.0, CY - 1.65, r"$I_f$ (excitação CC)", ha="center",
                fontsize=9.5, color=LR, style="italic")

        ax.set_title("Gerador Síncrono conectado ao Barramento Infinito",
                     fontsize=12, fontweight="bold", color=TX, pad=8)
        fig.tight_layout()
        return fig

    def fig_partida_motor_mes():
        """Matplotlib: métodos de partida do motor síncrono."""
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), facecolor='white')

        for ax in axes:
            ax.set_facecolor('white'); ax.axis('off')

        def bloco(ax, cx, cy, w, h, txt, cor, fs=9.5):
            ax.add_patch(mpatches.FancyBboxPatch(
                (cx - w/2, cy - h/2), w, h,
                boxstyle="round,pad=0.08", fc="#f0f4ff", ec=cor, lw=1.8))
            ax.text(cx, cy, txt, ha="center", va="center",
                    fontsize=fs, color=TX, fontweight="bold")

        def seta(ax, x1, y1, x2, y2, cor=TX, lw=1.6):
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="-|>", color=cor,
                                        lw=lw, mutation_scale=13))

        # ── Painel E: Partida por frequência variável (VFD) ───────────────────
        ax0 = axes[0]
        ax0.set_xlim(0, 10); ax0.set_ylim(0, 5)
        ax0.set_title("Partida por Frequência Variável (VFD)",
                      fontsize=10.5, fontweight="bold", color=AZ, pad=6)

        bloco(ax0, 1.5, 2.5, 2.2, 1.2, "Rede CA\n(60 Hz)", CZ)
        bloco(ax0, 4.5, 2.5, 2.4, 1.4, "Conversor de\nFrequência\n(VFD)", VD)
        bloco(ax0, 8.0, 2.5, 2.2, 1.2, "Motor\nSíncrono", AZ)
        seta(ax0, 2.6, 2.5, 3.3, 2.5)
        seta(ax0, 5.7, 2.5, 6.9, 2.5)

        ax0.text(4.5, 1.3, r"$0 \rightarrow f_{nom}$  (rampa)",
                 ha="center", fontsize=9.5, color=VD, style="italic")
        ax0.text(7.25, 2.85, r"$f,V$", fontsize=10, color=VD, style="italic")

        # Curva de rampa de frequência
        t  = np.linspace(0, 3, 100)
        ft = np.clip(t / 2.5 * 60, 0, 60)
        ax0.plot(0.2 + t * 0.8, 0.3 + ft * 0.012, color=VD, lw=1.8, ls="--")
        ax0.text(1.0, 1.1, "f (Hz)", fontsize=8.5, color=VD)

        # ── Painel D: Partida como motor de indução (amortecedor) ─────────────
        ax1 = axes[1]
        ax1.set_xlim(0, 10); ax1.set_ylim(0, 5)
        ax1.set_title("Partida com Enrolamento Amortecedor",
                      fontsize=10.5, fontweight="bold", color=VM, pad=6)

        bloco(ax1, 1.5, 2.5, 2.2, 1.2, "Rede CA\n(60 Hz)", CZ)
        bloco(ax1, 5.0, 2.5, 2.8, 2.6, "Motor\nSíncrono\n(+ amortecedor)", AZ)
        seta(ax1, 2.6, 2.5, 3.6, 2.5)

        # Campo de campo sem excitação + resistência
        ax1.add_patch(mpatches.FancyBboxPatch(
            (7.8, 1.8), 1.5, 0.9,
            boxstyle="round,pad=0.06", fc="#fff0e8", ec=LR, lw=1.5))
        ax1.text(8.55, 2.25, r"$R_{ext}$", ha="center", va="center",
                 fontsize=10, color=LR, fontweight="bold")
        ax1.plot([6.4, 7.8], [2.25, 2.25], color=LR, lw=1.5, ls="--")
        ax1.text(7.1, 2.50, r"$I_f = 0$", ha="center", fontsize=9, color=LR)

        # Fases
        ax1.text(5.0, 4.1, "1. Parte como MIT\n    (amortecedor = gaiola)",
                 ha="center", fontsize=8.5, color=VD)
        ax1.text(5.0, 0.55, "2. n ≈ nₛ  →  aciona If  →  sincronismo",
                 ha="center", fontsize=8.5, color=VM)

        fig.suptitle("Métodos de Partida do Motor Síncrono",
                     fontsize=12, fontweight="bold", color=TX, y=1.01)
        fig.tight_layout(pad=0.6)
        return fig


    def fig_potencia_delta_mes():
        """Plotly: P×δ para gerador e motor, com Pmax e limites de estabilidade."""
        delta_arr = np.linspace(-180, 180, 500)
        delta_rad = np.radians(delta_arr)

        # Parâmetros nominais (pu)
        Vt, Ef, Xs = 1.0, 1.35, 1.0
        P_arr = (3 * Vt * Ef / Xs) * np.sin(delta_rad)
        P_max = 3 * Vt * Ef / Xs

        fig = go.Figure()

        # Curva P×δ
        fig.add_trace(go.Scatter(
            x=delta_arr, y=P_arr, mode="lines",
            line=dict(color=AZ, width=3.0),
            name=r"P = (3VtEf/Xs)·sin δ",
            hovertemplate="δ=%{x:.1f}°<br>P=%{y:.3f} pu"))

        # Pmax
        fig.add_hline(y=P_max, line=dict(color=VM, width=1.4, dash="dot"))
        fig.add_hline(y=-P_max, line=dict(color=VM, width=1.4, dash="dot"))
        fig.add_annotation(x=130, y=P_max + 0.06,
            text=f"<b>P_max = {P_max:.2f} pu</b>",
            showarrow=False, font=dict(size=12, color=VM))

        # Limites de estabilidade
        for xv, label in [(90, "δ=+90°<br>(gerador)"), (-90, "δ=−90°<br>(motor)")]:
            fig.add_vline(x=xv, line=dict(color=LR, width=1.5, dash="dash"))
            fig.add_annotation(x=xv + (5 if xv > 0 else -5), y=0.25,
                text=f"<b>{label}</b>", showarrow=False,
                font=dict(size=10.5, color=LR),
                xanchor="left" if xv > 0 else "right")

        # Regiões
        fig.add_vrect(x0=-90, x1=90,
            fillcolor="rgba(61,142,240,0.06)", line_width=0,
            annotation_text="<b>Zona estável</b>",
            annotation_position="top right",
            annotation_font_size=11)

        fig.add_annotation(x=45, y=P_max * 0.55,
            text="GERADOR<br>(δ > 0)", showarrow=False,
            font=dict(size=11, color=AZ), bgcolor="rgba(255,255,255,0.7)")
        fig.add_annotation(x=-45, y=-P_max * 0.55,
            text="MOTOR<br>(δ < 0)", showarrow=False,
            font=dict(size=11, color=VD), bgcolor="rgba(255,255,255,0.7)")

        fig.update_layout(
            title=dict(text="Potência Ativa × Ângulo de Carga δ  (Vt=1 pu, Ef=1,35 pu, Xs=1 pu)",
                       font=dict(size=15, color=TX)),
            xaxis=dict(title=dict(text="Ângulo de carga δ (°)", font=dict(size=14, color=TX)),
                       tickvals=[-180,-135,-90,-45,0,45,90,135,180],
                       tickfont=dict(size=12), range=[-185, 185],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Potência P (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12),
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
            height=440, margin=dict(l=70, r=30, t=65, b=70),
        )
        return fig

    def fig_potencia_reativa_mes():
        """Plotly: Q × Ef para diferentes P (gerador no barramento infinito)."""
        Vt, Xs = 1.0, 1.0
        Ef_arr = np.linspace(0.3, 2.5, 300)

        fig = go.Figure()
        for P_pu, cor, dash in [
                (0.0, CZ, "dash"),
                (0.3, AZ, "solid"),
                (0.6, VD, "solid"),
                (0.9, LR, "solid"),
                (1.0, VM, "solid"),
        ]:
            Q_arr = []
            for Ef in Ef_arr:
                # delta from P = 3VtEf/Xs sin(delta)
                sin_d = P_pu * Xs / (3 * Vt * Ef) if Ef > 0.01 else 0
                if abs(sin_d) > 1:
                    Q_arr.append(float('nan'))
                    continue
                delta = math.asin(np.clip(sin_d, -1, 1))
                Q = (3 * Vt * (Ef * math.cos(delta) - Vt)) / Xs
                Q_arr.append(Q)
            fig.add_trace(go.Scatter(
                x=Ef_arr, y=Q_arr, mode="lines",
                line=dict(color=cor, width=2.5, dash=dash),
                name=f"P = {P_pu:.1f} pu",
                hovertemplate="Ef=%{x:.2f}<br>Q=%{y:.3f} pu"))

        fig.add_hline(y=0, line=dict(color=TX, width=1.0, dash="dot"))
        fig.add_vline(x=1.0, line=dict(color=CZ, width=1.0, dash="dot"))
        fig.add_annotation(x=1.0, y=-1.2, text="Ef = Vt",
            showarrow=False, font=dict(size=11, color=CZ))
        fig.add_annotation(x=1.8, y=1.2, text="Super-excitado<br>Fornece Q →",
            showarrow=False, font=dict(size=10, color=VM),
            bgcolor="rgba(255,255,255,0.8)")
        fig.add_annotation(x=0.55, y=-1.1, text="← Sub-excitado<br>Absorve Q",
            showarrow=False, font=dict(size=10, color=AZ),
            bgcolor="rgba(255,255,255,0.8)")

        fig.update_layout(
            title=dict(text="Potência Reativa Q × Excitação Ef  (barramento infinito, Vt=1 pu)",
                       font=dict(size=15, color=TX)),
            xaxis=dict(title=dict(text="Tensão de excitação Ef (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[0.2, 2.6],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Potência reativa Q (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[-2.0, 3.0],
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.22),
            height=440, margin=dict(l=70, r=30, t=65, b=110),
        )
        return fig

    def fig_curva_capacidade_mes():
        """Plotly: Capability curve no plano P×Q (pu)."""
        # Parâmetros nominais
        Vt, Xs = 1.0, 1.0
        Ia_nom, If_nom = 1.0, 1.5
        S_nom = 3 * Vt * Ia_nom   # potência aparente nominal = 3 pu

        theta = np.linspace(0, 2 * np.pi, 500)

        # 1. Limite de armadura: círculo de raio S_nom centrado na origem
        P_arm = S_nom * np.cos(theta)
        Q_arm = S_nom * np.sin(theta)
        # Somente o arco superior (Q ≥ limite)
        mask_arm = (P_arm >= 0) & (P_arm <= S_nom)
        P_arm = P_arm[mask_arm]; Q_arm = Q_arm[mask_arm]

        # 2. Limite de campo: arco centrado em (0, -3Vt²/Xs)
        Q_center = -3 * Vt**2 / Xs  # = -3 pu
        R_field  =  3 * Vt * If_nom * Vt / Xs  # proporcional a If_nom·Ef_nom
        # Para If_nom gerando Ef_nom=1.5 pu: R_field = 3*1*1.5/1 = 4.5 pu
        # Simplificação pedagógica: raio = 3*Vt*Ef_max/Xs com Ef_max=1.5
        Ef_max = 1.5
        R_field = 3 * Vt * Ef_max / Xs
        phi_field = np.linspace(-np.pi/2, np.pi/2, 300)
        P_field = R_field * np.cos(phi_field)
        Q_field = Q_center + R_field * np.sin(phi_field)
        # Clip to valid region
        mask_f = (P_field >= 0) & (Q_field >= -2.5)
        P_field = P_field[mask_f]; Q_field = Q_field[mask_f]

        # 3. Limite de estabilidade: P = Pmax = 3VtEf/Xs → vertical em P=Ef_max*3
        P_stab = 3 * Vt * Ef_max / Xs  # 4.5 pu → clamp to S_nom
        P_stab = min(P_stab, S_nom)

        fig = go.Figure()

        # Armadura
        fig.add_trace(go.Scatter(
            x=P_arm, y=Q_arm, mode="lines",
            line=dict(color=AZ, width=3.0),
            name=f"Limite de armadura (Ia = {Ia_nom} pu)",
            fill=None))

        # Campo
        fig.add_trace(go.Scatter(
            x=P_field, y=Q_field, mode="lines",
            line=dict(color=VM, width=2.5),
            name=f"Limite de campo (Ef_max = {Ef_max} pu)"))

        # Estabilidade
        Q_stab = np.linspace(-2.5, 3.2, 100)
        fig.add_trace(go.Scatter(
            x=[P_stab]*100, y=list(Q_stab), mode="lines",
            line=dict(color=LR, width=2.0, dash="dash"),
            name=f"Limite de estabilidade (δ = 90°)"))

        # Ponto nominal (fp=0.8 atrasado por convenção)
        fp_nom = 0.8
        theta_nom = math.acos(fp_nom)
        P_nom = S_nom * fp_nom
        Q_nom = S_nom * math.sin(theta_nom)
        fig.add_trace(go.Scatter(
            x=[P_nom], y=[Q_nom], mode="markers",
            marker=dict(color=TX, size=12, symbol="star"),
            name=f"Ponto nominal (fp={fp_nom}, S={S_nom:.0f} pu)"))

        # Eixos Q=0 e P=0
        fig.add_hline(y=0, line=dict(color=CZ, width=0.8, dash="dot"))
        fig.add_vline(x=0, line=dict(color=CZ, width=0.8, dash="dot"))

        # Anotações de região
        fig.add_annotation(x=1.5, y=2.2, text="Super-excitado<br>(fornece Q)",
            showarrow=False, font=dict(size=11, color=VM),
            bgcolor="rgba(255,255,255,0.8)")
        fig.add_annotation(x=1.5, y=-1.5, text="Sub-excitado<br>(absorve Q)",
            showarrow=False, font=dict(size=11, color=AZ),
            bgcolor="rgba(255,255,255,0.8)")

        fig.update_layout(
            title=dict(text="Curva de Capacidade — Gerador Síncrono (plano P × Q, pu)",
                       font=dict(size=15, color=TX)),
            xaxis=dict(title=dict(text="Potência ativa P (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[-0.2, S_nom + 0.5],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Potência reativa Q (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[-2.8, 3.5],
                       gridcolor="rgba(128,128,128,.15)", scaleanchor="x", scaleratio=1),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
            height=520, margin=dict(l=70, r=30, t=65, b=70),
        )
        return fig

    def fig_curvas_v_mes():
        """Plotly: família de curvas V — Ia × If para diferentes P."""
        Vt, Xs = 1.0, 1.0
        If_range = np.linspace(0.05, 3.0, 400)  # If em pu (= Ef/Vt)

        fig = go.Figure()
        fp1_x, fp1_y = [], []  # lugar geométrico fp=1

        for P_pu, cor, dash in [
                (0.0, CZ,  "dash"),
                (0.25, AZ, "solid"),
                (0.50, VD, "solid"),
                (0.75, LR, "solid"),
                (1.00, VM, "solid"),
        ]:
            Ia_list = []
            for Ef in If_range:
                sin_d = P_pu * Xs / (3 * Vt * Ef) if Ef > 0.01 else 0
                if abs(sin_d) > 1:
                    Ia_list.append(float('nan'))
                    continue
                delta = math.asin(np.clip(sin_d, -1, 1))
                Ef_c  = complex(Ef * math.cos(delta), Ef * math.sin(delta))
                Vt_c  = complex(Vt, 0)
                Ia_c  = (Vt_c - Ef_c) / complex(0, Xs)  # motor convention
                Ia_list.append(abs(Ia_c))

            Ia_arr = np.array(Ia_list)
            fig.add_trace(go.Scatter(
                x=If_range, y=Ia_arr, mode="lines",
                line=dict(color=cor, width=2.5, dash=dash),
                name=f"P = {P_pu:.2f} pu",
                hovertemplate="If=%{x:.2f}<br>Ia=%{y:.3f} pu"))

            # Ponto fp=1: Ia mínimo (onde Q=0, i.e., Ef cosδ = Vt)
            valid = ~np.isnan(Ia_arr)
            if valid.any():
                idx_min = np.nanargmin(Ia_arr)
                fp1_x.append(If_range[idx_min])
                fp1_y.append(Ia_arr[idx_min])

        # Linha de fp=1
        if fp1_x:
            order = np.argsort(fp1_x)
            fig.add_trace(go.Scatter(
                x=np.array(fp1_x)[order], y=np.array(fp1_y)[order],
                mode="lines+markers",
                line=dict(color=TX, width=1.8, dash="longdash"),
                marker=dict(size=8, color=TX),
                name="fp = 1 (Ia mínimo)"))

        fig.add_annotation(x=0.6, y=2.0, text="Sub-excitado<br>(Q absorvida)",
            showarrow=False, font=dict(size=11, color=AZ),
            bgcolor="rgba(255,255,255,0.8)")
        fig.add_annotation(x=2.2, y=2.0, text="Super-excitado<br>(Q fornecida)",
            showarrow=False, font=dict(size=11, color=VM),
            bgcolor="rgba(255,255,255,0.8)")

        fig.update_layout(
            title=dict(text="Curvas V — Corrente de Armadura Ia × Excitação Ef (motor síncrono)",
                       font=dict(size=15, color=TX)),
            xaxis=dict(title=dict(text="Excitação Ef / Vt (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[0, 3.1],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Corrente de armadura Ia (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[0, 3.2],
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
            height=440, margin=dict(l=70, r=30, t=65, b=70),
        )
        return fig

    def fig_condensador_sincrono_mes():
        """Plotly: diagramas fasoriais do condensador síncrono (P≈0, 3 condições)."""
        Vt, Xs = 1.0, 1.0
        configs = [
            ("Sub-excitado", 0.6, AZ),
            ("Normal",       1.0, VD),
            ("Super-excitado", 1.5, VM),
        ]

        fig = go.Figure()
        x_offset = 0

        for label, Ef, cor in configs:
            # Condensador síncrono: P=0, δ≈0 → Ia puramente imaginário
            Ia_c = (complex(Vt, 0) - complex(Ef, 0)) / complex(0, Xs)

            def add_arrow(x1, y1, x2, y2, c, name, dash="solid", w=2.5, show=True):
                fig.add_trace(go.Scatter(
                    x=[x1+x_offset, x2+x_offset], y=[y1, y2],
                    mode="lines", line=dict(color=c, width=w, dash=dash),
                    showlegend=False, hoverinfo="skip"))
                fig.add_annotation(
                    x=x2+x_offset, y=y2, ax=x1+x_offset, ay=y1,
                    xref="x", yref="y", axref="x", ayref="y",
                    arrowhead=2, arrowsize=1.3, arrowwidth=2.5,
                    arrowcolor=c, showarrow=True, text="")

            # Vt (referência horizontal)
            add_arrow(0, 0, Vt, 0, TX, "Vt")
            fig.add_annotation(x=Vt*0.5+x_offset, y=0.08,
                text="<b>Vₜ</b>", showarrow=False, font=dict(size=12, color=TX))

            # Ef (mesma fase que Vt, magnitude diferente)
            add_arrow(0, 0, Ef, 0, cor, label, dash="dot" if label=="Normal" else "solid")
            fig.add_annotation(x=Ef*0.5+x_offset, y=-0.12,
                text=f"<b>Eƒ</b>", showarrow=False, font=dict(size=12, color=cor))

            # Ia (vertical — puramente reativa)
            Ia_mag = abs(Ia_c)
            Ia_sign = 1 if Ia_c.imag > 0 else -1
            if Ia_mag > 0.01:
                add_arrow(0, 0, 0, Ia_sign * Ia_mag, LR, "Ia")
                fig.add_annotation(x=0.10+x_offset, y=Ia_sign*Ia_mag*0.5,
                    text="<b>Iₐ</b>", showarrow=False, font=dict(size=12, color=LR))

            # Label do modo
            fig.add_annotation(x=x_offset + 0.5, y=-0.65,
                text=f"<b>{label}</b><br><span style='font-size:10px;color:{cor}'>"
                     f"Ef={Ef:.1f} pu</span>",
                showarrow=False, font=dict(size=11, color=cor),
                bgcolor="rgba(255,255,255,0.85)", borderpad=3)

            x_offset += 2.5

        fig.add_hline(y=0, line=dict(color=CZ, width=0.6, dash="dot"))
        fig.update_layout(
            title=dict(text="Condensador Síncrono — Diagramas Fasoriais (P ≈ 0)",
                       font=dict(size=15, color=TX)),
            xaxis=dict(range=[-0.3, 7.5], showgrid=True,
                       gridcolor="rgba(128,128,128,.12)",
                       tickfont=dict(size=12),
                       title=dict(text="Real (pu)", font=dict(size=12, color=CZ))),
            yaxis=dict(range=[-0.9, 1.1], showgrid=True,
                       gridcolor="rgba(128,128,128,.12)",
                       tickfont=dict(size=12), scaleanchor="x", scaleratio=1,
                       title=dict(text="Imaginário (pu)", font=dict(size=12, color=CZ))),
            height=380, margin=dict(l=65, r=30, t=60, b=60),
        )
        return fig


    def fig_dq_decomposition_mes():
        """Plotly: decomposição Id/Iq no plano fasorial de polos salientes."""
        # Parâmetros fixos para a figura estática
        delta_deg = 25.0; phi_deg = 30.0
        Vt = 1.0; Ef = 1.35; Xd = 1.0; Xq = 0.6

        delta = math.radians(delta_deg)
        phi   = math.radians(phi_deg)
        psi   = phi + delta  # angle of Ia from q-axis

        # Ia via circuit: Iq = (Ef - Vt*cos δ)/Xq, Id = Vt*sin δ / Xd
        Iq = (Ef - Vt * math.cos(delta)) / Xq
        Id = Vt * math.sin(delta) / Xd
        Ia_mag = math.sqrt(Id**2 + Iq**2)

        # Phasor directions
        q_cos, q_sin = math.cos(delta), math.sin(delta)   # q-axis unit vector
        d_cos, d_sin = -math.sin(delta), math.cos(delta)  # d-axis unit vector

        # Ia phasor components in x-y
        Ia_x = Iq * q_cos + Id * d_cos
        Ia_y = Iq * q_sin + Id * d_sin

        fig = go.Figure()

        def fasor(ox, oy, dx, dy, cor, nome, dash="solid", w=2.8, lx=0.04, ly=0.05):
            fig.add_trace(go.Scatter(
                x=[ox, ox+dx], y=[oy, oy+dy], mode="lines",
                line=dict(color=cor, width=w, dash=dash),
                name=nome, showlegend=True,
                hovertemplate=f"{nome}: {math.hypot(dx,dy):.3f} pu<extra></extra>"))
            fig.add_annotation(
                x=ox+dx, y=oy+dy, ax=ox, ay=oy,
                xref="x", yref="y", axref="x", ayref="y",
                arrowhead=2, arrowsize=1.4, arrowwidth=2.5,
                arrowcolor=cor, showarrow=True, text="")
            fig.add_annotation(
                x=ox+dx/2+lx, y=oy+dy/2+ly,
                text=f"<b>{nome}</b>", showarrow=False,
                font=dict(size=13, color=cor),
                bgcolor="rgba(255,255,255,0.78)", borderpad=2)

        # Vt (reference, horizontal)
        fasor(0, 0, Vt, 0, AZ, "Vₜ", lx=-0.12, ly=0.07)
        # Ef
        fasor(0, 0, Ef*q_cos, Ef*q_sin, VM, "Eƒ", lx=0.05, ly=0.05)
        # Ia (full, scaled)
        sc = 0.75
        fasor(0, 0, Ia_x*sc, Ia_y*sc, VD, "Iₐ", dash="dot", w=2.2, lx=0.05, ly=-0.10)
        # Iq component
        fasor(0, 0, Iq*q_cos*sc, Iq*q_sin*sc, LR, "Iᵩ", dash="dot", w=1.8, lx=0.05, ly=0.06)
        # Id component (from tip of Iq to tip of Ia)
        fasor(Iq*q_cos*sc, Iq*q_sin*sc,
              Id*d_cos*sc, Id*d_sin*sc, CI, "I_d", dash="dot", w=1.8, lx=0.04, ly=-0.09)

        # Axes q and d (dashed guidelines)
        L = 1.6
        fig.add_trace(go.Scatter(
            x=[0, L*q_cos], y=[0, L*q_sin], mode="lines",
            line=dict(color=CZ, width=1.0, dash="dash"),
            showlegend=False, hoverinfo="skip"))
        fig.add_annotation(x=L*q_cos+0.04, y=L*q_sin,
            text="<b>q</b>", showarrow=False, font=dict(size=12, color=CZ))

        fig.add_trace(go.Scatter(
            x=[0, 0.55*d_cos], y=[0, 0.55*d_sin], mode="lines",
            line=dict(color=CZ, width=1.0, dash="dash"),
            showlegend=False, hoverinfo="skip"))
        fig.add_annotation(x=0.58*d_cos, y=0.58*d_sin,
            text="<b>d</b>", showarrow=False, font=dict(size=12, color=CZ))

        # Angle arcs
        for ang_end, col, lbl, rad, loff in [
            (delta,       VM, "δ", 0.28, (0.08, 0.05)),
            (-phi,        VD, "φ", 0.20, (0.08,-0.10)),
            (delta-phi,   TX, "ψ", 0.13, (0.05, 0.02)),
        ]:
            arc = np.linspace(0, ang_end, 40)
            fig.add_trace(go.Scatter(
                x=rad*np.cos(arc), y=rad*np.sin(arc), mode="lines",
                line=dict(color=col, width=1.5, dash="dot"),
                showlegend=False, hoverinfo="skip"))
            mid = ang_end / 2
            fig.add_annotation(
                x=(rad+0.08)*math.cos(mid)+loff[0],
                y=(rad+0.08)*math.sin(mid)+loff[1],
                text=f"<b>{lbl}</b>", showarrow=False,
                font=dict(size=12, color=col))

        fig.add_hline(y=0, line=dict(color=CZ, width=0.7, dash="dot"))
        fig.add_vline(x=0, line=dict(color=CZ, width=0.7, dash="dot"))

        fig.update_layout(
            title=dict(
                text=r"Decomposição Id/Iq — Polos Salientes (δ=25°, φ=30°, Xd=1,0, Xq=0,6)",
                font=dict(size=15, color=TX)),
            xaxis=dict(range=[-0.3, 1.6], scaleanchor="y",
                       showgrid=True, gridcolor="rgba(128,128,128,.15)",
                       zeroline=False, tickfont=dict(size=12),
                       title=dict(text="Real (pu)", font=dict(size=12, color=CZ))),
            yaxis=dict(range=[-0.8, 1.4],
                       showgrid=True, gridcolor="rgba(128,128,128,.15)",
                       zeroline=False, tickfont=dict(size=12),
                       title=dict(text="Imaginário (pu)", font=dict(size=12, color=CZ))),
            legend=dict(font=dict(size=12), bgcolor="rgba(255,255,255,0.88)",
                        x=0.01, y=0.99, xanchor="left", yanchor="top"),
            height=480, margin=dict(l=65, r=30, t=60, b=60),
        )
        return fig

    def fig_potencia_saliente_mes():
        """Plotly: P×δ com e sem componente de relutância (polos salientes)."""
        delta_arr = np.linspace(-180, 180, 500)
        delta_rad = np.radians(delta_arr)

        Vt = 1.0; Ef = 1.2; Xd = 1.0; Xq = 0.6

        P_cil    = (3*Vt*Ef / Xd) * np.sin(delta_rad)
        P_rel    = (3*Vt**2*(Xd-Xq) / (2*Xd*Xq)) * np.sin(2*delta_rad)
        P_sal    = P_cil + P_rel
        P_max_sal = float(np.max(P_sal[:250]))  # max in generator region

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=delta_arr, y=P_cil, mode="lines",
            line=dict(color=AZ, width=2.2, dash="dash"),
            name="Cilíndrica (Xd=Xq)  P = (VtEf/Xd)sinδ"))
        fig.add_trace(go.Scatter(x=delta_arr, y=P_rel, mode="lines",
            line=dict(color=LR, width=1.8, dash="dot"),
            name="Relutância  P_rel = (Vt²(Xd−Xq)/2XdXq)sin2δ"))
        fig.add_trace(go.Scatter(x=delta_arr, y=P_sal, mode="lines",
            line=dict(color=VM, width=3.0),
            name="Polos Salientes  P_total = P_cil + P_rel"))

        # Mark maximum of salient pole
        idx_max = int(np.argmax(P_sal[:250]))
        fig.add_trace(go.Scatter(x=[delta_arr[idx_max]], y=[P_sal[idx_max]],
            mode="markers", marker=dict(color=VM, size=12, symbol="star"),
            name=f"P_max ≈ {P_sal[idx_max]:.2f} pu (δ ≈ {delta_arr[idx_max]:.0f}°)"))

        fig.add_vline(x=90,  line=dict(color=CZ, width=1, dash="dot"))
        fig.add_vline(x=-90, line=dict(color=CZ, width=1, dash="dot"))
        fig.add_hline(y=0,   line=dict(color=CZ, width=0.8))
        fig.add_annotation(x=50, y=P_sal[idx_max]+0.06,
            text=f"δ_max ≈ {delta_arr[idx_max]:.0f}° < 90°<br>(saliente mais estável)",
            showarrow=False, font=dict(size=11, color=VM),
            bgcolor="rgba(255,255,255,0.85)")

        fig.update_layout(
            title=dict(text="Potência × δ — Cilíndrica vs Polos Salientes (Vt=1, Ef=1,2, Xd=1, Xq=0,6)",
                       font=dict(size=14, color=TX)),
            xaxis=dict(title=dict(text="Ângulo de carga δ (°)", font=dict(size=14, color=TX)),
                       tickvals=[-180,-135,-90,-45,0,45,90,135,180],
                       tickfont=dict(size=12), range=[-185,185],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Potência P (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12),
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.24),
            height=460, margin=dict(l=70, r=30, t=60, b=110),
        )
        return fig

    def fig_curto_circuito_mes():
        """Plotly: envelope da corrente de curto-circuito (3 períodos)."""
        t = np.linspace(0, 1.5, 1000)

        # Typical values (pu): Xd''=0.2, Xd'=0.3, Xd=1.0, Ef=1.0
        Ef  = 1.0
        Icc  = Ef / 1.0   # steady-state
        Itr  = Ef / 0.3   # transient amplitude
        Isub = Ef / 0.2   # subtransient amplitude

        # Time constants
        td0pp = 0.06   # subtransient (s)
        td0p  = 6.0    # transient (s) — use 0.8 for display
        td0p_display = 0.8
        ta    = 0.15   # DC offset

        # Envelope (upper)
        env_upper = (Isub - Itr)*np.exp(-t/td0pp) + (Itr - Icc)*np.exp(-t/td0p_display) + Icc
        env_dc    = np.sqrt(2) * Isub * np.exp(-t/ta)  # DC offset component
        env_total_upper = env_upper + env_dc

        # Actual current (sinusoidal × envelope)
        f_el = 60
        i_ac  = env_upper * np.sin(2*np.pi*f_el*t)
        i_dc  = np.sqrt(2)*Isub*np.exp(-t/ta)
        i_tot = i_ac - i_dc

        fig = go.Figure()
        # Envelopes
        fig.add_trace(go.Scatter(x=t, y=env_upper, mode="lines",
            line=dict(color=CZ, width=1.5, dash="dash"),
            name="Envoltória AC (sem DC)"))
        fig.add_trace(go.Scatter(x=t, y=-env_upper, mode="lines",
            line=dict(color=CZ, width=1.5, dash="dash"),
            showlegend=False))
        fig.add_trace(go.Scatter(x=t, y=env_total_upper, mode="lines",
            line=dict(color=LR, width=1.5, dash="dot"),
            name="Envoltória total (com DC)"))

        # Corrente total
        fig.add_trace(go.Scatter(x=t, y=i_tot, mode="lines",
            line=dict(color=AZ, width=1.8),
            name="Corrente total i(t)"))

        # Reference lines for each period
        t_sub = 3/f_el  # ~3 cycles
        t_tr  = 0.4
        for tv, lbl, cor in [(t_sub,"Subtransiente→Transiente",LR),(t_tr,"Transiente→Permanente",VD)]:
            fig.add_vline(x=tv, line=dict(color=cor, width=1.2, dash="dash"))
            fig.add_annotation(x=tv+0.01, y=4.2, text=f"<b>{lbl}</b>",
                showarrow=False, font=dict(size=9.5, color=cor), xanchor="left")

        # Icc steady state
        fig.add_hline(y=Icc*math.sqrt(2), line=dict(color=VM, width=1.2, dash="dot"))
        fig.add_annotation(x=1.3, y=Icc*math.sqrt(2)+0.15,
            text=f"I_cc (regime) = {Icc*math.sqrt(2):.2f} pu",
            showarrow=False, font=dict(size=10, color=VM))

        # Labels de região
        for xc, yc, lbl in [
            (t_sub/2,       5.0, "Subtransiente\n(X_d'')"),
            ((t_sub+t_tr)/2, 3.5, "Transiente\n(X_d')"),
            (1.1,            1.8, "Regime\n(X_d)"),
        ]:
            fig.add_annotation(x=xc, y=yc, text=f"<b>{lbl}</b>",
                showarrow=False, font=dict(size=10, color=TX),
                bgcolor="rgba(255,255,255,0.8)", borderpad=3)

        fig.update_layout(
            title=dict(text="Corrente de Curto-Circuito — 3 Períodos (Subtransiente, Transiente, Regime)",
                       font=dict(size=14, color=TX)),
            xaxis=dict(title=dict(text="Tempo (s)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[-0.02, 1.52],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Corrente (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12),
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.22),
            height=460, margin=dict(l=70, r=30, t=65, b=110),
        )
        return fig

    def fig_area_equivalente_mes():
        """Plotly: método das áreas equivalentes (estabilidade dinâmica)."""
        delta_arr = np.linspace(0, np.pi, 400)
        Vt = 1.0; Ef = 1.2; Xs = 1.0
        P_arr = (3*Vt*Ef/Xs) * np.sin(delta_arr)
        P_max = 3*Vt*Ef/Xs

        # Operating point before fault
        Pm = 0.6  # mechanical power
        delta0 = math.asin(Pm / P_max)          # initial angle
        delta1 = np.pi - delta0                  # unstable equilibrium
        delta_cc = math.radians(70)              # fault clearing angle

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=np.degrees(delta_arr), y=P_arr, mode="lines",
            line=dict(color=AZ, width=2.8),
            name="P_e = (VtEf/Xs)sinδ"))

        # Pm line
        fig.add_hline(y=Pm, line=dict(color=VD, width=2.0, dash="dash"))
        fig.add_annotation(x=170, y=Pm+0.05, text="<b>P_m</b>",
            showarrow=False, font=dict(size=12, color=VD))

        # Area A1 (accelerating — under Pm, above Pe curve, from delta0 to delta_cc)
        mask_a1 = (delta_arr >= delta0) & (delta_arr <= delta_cc)
        d_a1 = delta_arr[mask_a1]
        p_a1 = P_arr[mask_a1]
        fig.add_trace(go.Scatter(
            x=np.concatenate([np.degrees(d_a1), np.degrees(d_a1[::-1])]),
            y=np.concatenate([np.full_like(d_a1, Pm), p_a1[::-1]]),
            fill="toself", fillcolor="rgba(224,123,0,0.30)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Área A₁ (acelerante)"))

        # Area A2 (decelerating — above Pm, under Pe curve, from delta_cc to delta_max)
        delta_max = np.pi - delta_cc  # conservative estimate
        mask_a2 = (delta_arr >= delta_cc) & (delta_arr <= delta_max)
        d_a2 = delta_arr[mask_a2]
        p_a2 = P_arr[mask_a2]
        fig.add_trace(go.Scatter(
            x=np.concatenate([np.degrees(d_a2), np.degrees(d_a2[::-1])]),
            y=np.concatenate([p_a2, np.full_like(d_a2, Pm)[::-1]]),
            fill="toself", fillcolor="rgba(61,142,240,0.30)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Área A₂ (desacelerante)"))

        # Key angles
        for ang, lbl, cor in [
            (math.degrees(delta0),  "δ₀", VD),
            (math.degrees(delta_cc),"δ_cc",LR),
            (math.degrees(delta_max),"δ_max",AZ),
            (math.degrees(delta1),  "δ₁",CZ),
        ]:
            fig.add_vline(x=ang, line=dict(color=cor, width=1.2, dash="dot"))
            fig.add_annotation(x=ang+1, y=P_max+0.08, text=f"<b>{lbl}</b>",
                showarrow=False, font=dict(size=11, color=cor), xanchor="left")

        fig.add_annotation(x=55, y=0.25, text="<b>A₁</b>",
            showarrow=False, font=dict(size=14, color=LR))
        fig.add_annotation(x=100, y=0.95, text="<b>A₂</b>",
            showarrow=False, font=dict(size=14, color=AZ))
        fig.add_annotation(x=20, y=P_max*0.9,
            text="Estável se A₂ ≥ A₁",
            showarrow=False, font=dict(size=11, color=TX),
            bgcolor="rgba(255,255,255,0.85)")

        fig.update_layout(
            title=dict(text="Método das Áreas Equivalentes — Limite de Estabilidade Dinâmica",
                       font=dict(size=14, color=TX)),
            xaxis=dict(title=dict(text="Ângulo de carga δ (°)", font=dict(size=14, color=TX)),
                       tickvals=[0,30,60,90,120,150,180],
                       tickfont=dict(size=12), range=[0, 185],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Potência (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[-0.1, P_max+0.3],
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.22),
            height=460, margin=dict(l=70, r=30, t=60, b=110),
        )
        return fig

    def fig_fasorial_saliente_mes(Vt=1.0, Ef=1.2, delta_deg=25.0,
                                   Xd=1.0, Xq=0.6):
        """Plotly: diagrama fasorial de polos salientes com Id/Iq."""
        delta = math.radians(delta_deg)
        Vt_c  = complex(Vt, 0)
        Ef_c  = complex(Ef*math.cos(delta), Ef*math.sin(delta))

        # Id e Iq (Ra=0, gerador)
        # Vt + jXq*Iq + jXd*Id = Ef  (decomposed)
        # delta obtido pela relação: tan(delta) = XqIacos(phi)/(Vt+XqIasin(phi))
        # Here we compute Ia from the salient pole equations
        # Use the standard approach: find Iq, Id from geometry
        # Since Ra=0:  Ef = Vt + jXd*Id + jXq*Iq
        # Iq = (Ef - Vt*cos(delta)) / Xq  (only approximate — use direct formula)
        Iq = (Ef - Vt*math.cos(delta)) / Xq
        Id = Vt * math.sin(delta) / Xd

        phi = math.atan2(Xq*Iq - 0, Vt + Xd*Id)   # power factor angle approx

        Ia_mag = math.sqrt(Id**2 + Iq**2)
        psi    = math.atan2(Id, Iq)  # angle from q-axis to Ia
        phi_ia = delta - psi          # lag angle from Vt

        Ia_c  = complex(Ia_mag*math.cos(-phi_ia), Ia_mag*math.sin(-phi_ia))
        jXdId_c = complex(0, Xd) * complex(Id*(-math.sin(delta)),
                                             Id*math.cos(delta))
        jXqIq_c = complex(0, Xq) * complex(Iq*math.cos(delta),
                                             Iq*math.sin(delta))

        fig = go.Figure()

        def arrow_trace(ox, oy, dx, dy, cor, nome, dash="solid", w=2.8):
            fig.add_trace(go.Scatter(
                x=[ox, ox+dx], y=[oy, oy+dy], mode="lines",
                line=dict(color=cor, width=w, dash=dash),
                name=nome, showlegend=True,
                hovertemplate=f"{nome}: {math.hypot(dx,dy):.3f} pu<extra></extra>"))
            fig.add_annotation(x=ox+dx, y=oy+dy, ax=ox, ay=oy,
                xref="x", yref="y", axref="x", ayref="y",
                arrowhead=2, arrowsize=1.4, arrowwidth=2.5,
                arrowcolor=cor, showarrow=True, text="")
            fig.add_annotation(x=ox+dx/2+0.03, y=oy+dy/2+0.04,
                text=f"<b>{nome}</b>", showarrow=False,
                font=dict(size=12, color=cor),
                bgcolor="rgba(255,255,255,0.75)", borderpad=2)

        arrow_trace(0, 0, Vt_c.real, Vt_c.imag, AZ,  "Vₜ", w=3.0)
        arrow_trace(0, 0, Ef_c.real, Ef_c.imag, VM,  "Eƒ", w=3.0)
        arrow_trace(0, 0, Ia_c.real*0.7, Ia_c.imag*0.7, VD, "Iₐ", dash="dot", w=2.0)
        arrow_trace(0, 0,
                    Iq*math.cos(delta)*0.7, Iq*math.sin(delta)*0.7,
                    LR, "Iᵩ", dash="dot", w=1.8)
        arrow_trace(0, 0,
                    Id*(-math.sin(delta))*0.7, Id*math.cos(delta)*0.7,
                    CI, "I_d", dash="dot", w=1.8)
        arrow_trace(Vt_c.real, Vt_c.imag,
                    jXqIq_c.real, jXqIq_c.imag, LR, "jXᵩIᵩ", w=2.0)
        arrow_trace(Vt_c.real + jXqIq_c.real, Vt_c.imag + jXqIq_c.imag,
                    jXdId_c.real, jXdId_c.imag, CI, "jX_dI_d", w=2.0)

        # delta arc
        arc_t = np.linspace(0, delta, 30)
        fig.add_trace(go.Scatter(x=0.25*np.cos(arc_t), y=0.25*np.sin(arc_t),
            mode="lines", line=dict(color=TX, width=1.5, dash="dash"),
            showlegend=False, hoverinfo="skip"))
        fig.add_annotation(x=0.32*math.cos(delta/2), y=0.32*math.sin(delta/2),
            text="<b>δ</b>", showarrow=False, font=dict(size=13, color=TX))

        fig.add_hline(y=0, line=dict(color=CZ, width=0.7, dash="dot"))
        fig.add_vline(x=0, line=dict(color=CZ, width=0.7, dash="dot"))

        lim = max(Vt, Ef) * 1.3
        fig.update_layout(
            title=dict(text=f"Fasorial — Polos Salientes (δ={delta_deg:.0f}°, Xd={Xd}, Xq={Xq})",
                       font=dict(size=15, color=TX)),
            xaxis=dict(range=[-0.3, lim*1.1], scaleanchor="y",
                       showgrid=True, gridcolor="rgba(128,128,128,.15)",
                       zeroline=False, tickfont=dict(size=12),
                       title=dict(text="Real (pu)", font=dict(size=12, color=CZ))),
            yaxis=dict(range=[-lim*0.5, lim*0.9],
                       showgrid=True, gridcolor="rgba(128,128,128,.15)",
                       zeroline=False, tickfont=dict(size=12),
                       title=dict(text="Imaginário (pu)", font=dict(size=12, color=CZ))),
            legend=dict(font=dict(size=11), bgcolor="rgba(255,255,255,0.85)",
                        x=0.01, y=0.99, xanchor="left", yanchor="top"),
            height=500, margin=dict(l=65, r=30, t=60, b=60),
        )
        return fig

    # ═══════════════════════════════════════════════════════════════════════════
    # CABEÇALHO
    # ═══════════════════════════════════════════════════════════════════════════
    st.title("🌐 Máquinas Síncronas Polifásicas")
    st.caption(
        "⚡ SINTONIA · Máquinas Elétricas · "
        "👤 Marcus V A Fernandes · ✉️ marcus.fernandes@ifrn.edu.br"
    )
    st.markdown("---")

    # ── Índice ────────────────────────────────────────────────────────────────
    with st.expander("📑 Índice do Módulo — clique em qualquer item para navegar", expanded=True):
        st.markdown("""
<style>
.idx-group { font-size:0.78rem; font-weight:700; color:#6b7280;
             text-transform:uppercase; letter-spacing:.07em;
             margin:0.9rem 0 0.25rem; }
.idx-link  { display:block; font-size:0.93rem; color:#3d8ef0;
             text-decoration:none; padding:0.18rem 0 0.18rem 0.6rem;
             border-left:2px solid rgba(61,142,240,.25);
             margin-bottom:0.1rem; }
.idx-link:hover { border-left-color:#3d8ef0; background:rgba(61,142,240,.06);
                  border-radius:0 4px 4px 0; }
.idx-sub   { display:block; font-size:0.84rem; color:#1a1f2b;
             text-decoration:none; padding:0.12rem 0 0.12rem 1.4rem;
             border-left:2px solid rgba(108,71,255,.18);
             margin-bottom:0.08rem; }
.idx-sub:hover { border-left-color:#6c47ff; background:rgba(108,71,255,.05);
                 border-radius:0 4px 4px 0; }
</style>

<div class="idx-group">🔵 Fundamentos (PPTX-01)</div>
<a class="idx-link" href="#1-conceitos-elementares-e-aplicações">1. Conceitos Elementares e Aplicações</a>
<a class="idx-link" href="#2-estrutura-construtiva">2. Estrutura Construtiva</a>
<a class="idx-sub"  href="#2-estrutura-construtiva">↳ Rotor cilíndrico · Polos salientes</a>
<a class="idx-link" href="#3-geração-de-tensão-modo-gerador">3. Geração de Tensão — Modo Gerador</a>
<a class="idx-sub"  href="#3-geração-de-tensão-modo-gerador">↳ nₛ = 120f/p · Ef = kf·nₛ·Φf</a>
<a class="idx-link" href="#4-curva-de-magnetização-occ">4. Curva de Magnetização (OCC)</a>
<a class="idx-sub"  href="#4-curva-de-magnetização-occ">↳ AGL · Saturação · Magnetismo residual</a>
<a class="idx-link" href="#5-reação-da-armadura">5. Reação da Armadura</a>
<a class="idx-sub"  href="#5-reação-da-armadura">↳ Φr = Φf + Φa · Efeito do fator de potência</a>
<a class="idx-link" href="#6-circuito-equivalente-por-fase">6. Circuito Equivalente por Fase</a>
<a class="idx-sub"  href="#6-circuito-equivalente-por-fase">↳ Ef, Xs, Ra, Zs · Gerador e Motor</a>
<a class="idx-link" href="#7-diagrama-fasorial">7. Diagrama Fasorial</a>
<a class="idx-sub"  href="#7-diagrama-fasorial">↳ Ângulo de carga δ · Sub/super-excitação</a>
<a class="idx-link" href="#8-barramento-infinito-e-sincronismo">8. Barramento Infinito e Sincronismo</a>
<a class="idx-sub"  href="#8-barramento-infinito-e-sincronismo">↳ Condições de sincronismo · Controle P e Q</a>
<a class="idx-link" href="#9-modo-motor-partida">9. Modo Motor — Partida</a>
<a class="idx-sub"  href="#9-modo-motor-partida">↳ VFD · Enrolamento amortecedor</a>
<a class="idx-link" href="#10-ensaios-occ-scc-determinação-dos-parâmetros">10. Ensaios OCC + SCC — Parâmetros</a>
<a class="idx-sub"  href="#10-ensaios-occ-scc-determinação-dos-parâmetros">↳ Xs_sat · Xs_nsat · Ensaio de escorregamento</a>

<div class="idx-group">⚡ Características de Operação (PPTX-02)</div>
<a class="idx-link" href="#11-potência-ativa-reativa-e-torque">11. Potência Ativa, Reativa e Torque</a>
<a class="idx-sub"  href="#11-potência-ativa-reativa-e-torque">↳ P = (3VtEf/Xs)sinδ · Q · Pmax · δ_max = 90°</a>
<a class="idx-link" href="#12-curva-de-capacidade-capability-curve">12. Curva de Capacidade</a>
<a class="idx-sub"  href="#12-curva-de-capacidade-capability-curve">↳ Limites de armadura, campo e estabilidade</a>
<a class="idx-link" href="#13-controle-de-fator-de-potência-condensador-síncrono">13. Controle de Fator de Potência</a>
<a class="idx-sub"  href="#13-controle-de-fator-de-potência-condensador-síncrono">↳ Condensador síncrono · Curvas V</a>

<div class="idx-group">🔴 Polos Salientes e Transitórios (PPTX-03)</div>
<a class="idx-link" href="#14-máquina-síncrona-com-polos-salientes">14. Máquina com Polos Salientes</a>
<a class="idx-sub"  href="#14-máquina-síncrona-com-polos-salientes">↳ Eixos d-q · Xd > Xq · Ensaio de escorregamento</a>
<a class="idx-link" href="#15-potência-e-torque-em-máquinas-de-polos-salientes">15. Potência e Torque em Polos Salientes</a>
<a class="idx-sub"  href="#15-potência-e-torque-em-máquinas-de-polos-salientes">↳ Parcela de excitação + relutância · δ_max &lt; 90°</a>
<a class="idx-link" href="#16-dinâmicas-de-transitório">16. Dinâmicas de Transitório</a>
<a class="idx-sub"  href="#16-dinâmicas-de-transitório">↳ Xd″ · Xd′ · Xd · Áreas equivalentes</a>

<div class="idx-group">🎛️ Ferramentas Interativas</div>
<a class="idx-link" href="#exploradores-interativos">Exploradores Interativos</a>
<a class="idx-sub"  href="#exploradores-interativos">↳ Fasorial cilíndrico · Curva V · P×δ · Polos salientes</a>
""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 1 — Conceitos Elementares
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("1. Conceitos Elementares e Aplicações")

    st.markdown(r"""
A **máquina síncrona** é a principal máquina elétrica usada na geração de energia elétrica
no mundo. Seu nome vem da operação em velocidade constante em regime permanente — o rotor
gira em **sincronismo** com o campo magnético girante do estator.

**Características fundamentais:**

- **Dupla excitação**: os polos do rotor são excitados por corrente contínua (If),
  enquanto o estator é conectado a uma fonte de corrente alternada (ou à rede).
- **Velocidade constante**: em regime permanente,
  $n_s = \dfrac{120\,f}{p}$ — independente da carga.
- **Operação reversível**: funciona como **gerador** (alternador) — convertendo energia
  mecânica em elétrica — ou como **motor** — convertendo energia elétrica em mecânica.

**Aplicações típicas:**

| Modo | Aplicação | Porte |
|---|---|---|
| Gerador (alternador) | Usinas hidroelétricas, termelétricas, nucleares | Dezenas a centenas de MVA |
| Gerador | Grupos de emergência, geração distribuída | Dezenas de kVA a MVA |
| Motor | Compressores, bombas de grande porte, laminadores | Centenas de kW a MW |
| Motor | Correção de fator de potência (compensador síncrono) | Vários MVA |
""")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 2 — Estrutura Construtiva
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("2. Estrutura Construtiva")

    st.markdown(r"""
A máquina síncrona é constituída por:

- **Estator (armadura)**: enrolamento trifásico distribuído nas ranhuras do núcleo
  laminado, projetado para suportar alta tensão e corrente.
- **Rotor (enrolamento de campo)**: alimentado por corrente contínua via
  anéis deslizantes e escovas, criando o fluxo $\Phi_f$.

As máquinas síncronas se dividem em dois grupos segundo a construção do rotor:
""")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(r"""
**🔵 Rotor Cilíndrico (polos não-salientes)**
- Rotor longo e de pequeno diâmetro
- Enrolamento de campo **distribuído** nas ranhuras
- Alta velocidade: 2 ou 4 polos (1800 ou 3600 rpm em 60 Hz)
- Grandes geradores acoplados a **turbinas a gás ou vapor**
- Porte: centenas de MVA
""")
    with col2:
        st.markdown(r"""
**🔴 Rotor com Polos Salientes**
- Rotor curto e de grande diâmetro
- Enrolamento de campo **concentrado** em cada polo
- Baixa velocidade: muitos polos (até 50 ou mais)
- Geradores de **usinas hidroelétricas** (turbinas Pelton/Francis)
- Porte: dezenas de MVA
""")

    show_fig(fig_estrutura_construtiva_mes(), width_frac=0.90)
    st.caption(
        "**Figura 2.1** — Seção transversal comparativa: rotor cilíndrico (polos "
        "não-salientes) à esquerda e rotor com polos salientes à direita. "
        "Em ambos, o estator (armadura) apresenta os enrolamentos trifásicos a, b, c."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 3 — Geração de Tensão
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("3. Geração de Tensão — Modo Gerador")

    st.markdown(r"""
Quando o rotor gira à velocidade síncrona $n_s$ — impulsionado por uma turbina —
o fluxo $\Phi_f$ varia senoidalmente no estator, induzindo a **tensão de excitação $E_f$**:

$$n_s = \frac{120\,f}{p} \quad \text{(rpm)}$$

$$E_f = 4{,}44\,f\,N\,\Phi_f\,K_w = k_f\,n_s\,\Phi_f \quad \text{(V, fase, RMS)}$$

onde $N$ é o número de espiras por fase, $K_w$ é o fator de enrolamento
($K_w \leq 1$) e $\Phi_f$ é o fluxo por polo produzido pela corrente $I_f$.

A tensão $E_f$ é diretamente proporcional à **velocidade de rotação** e ao **fluxo de campo**
— ambos controláveis: a velocidade pela turbina/regulador e o fluxo pela corrente $I_f$.
""")

    show_fig(fig_geracao_tensao_mes(), width_frac=0.85)
    st.caption(
        r"**Figura 3.1** — Geração da tensão $E_f$: a rotação do rotor "
        r"(excitado por $I_f$) faz o fluxo $\Phi_f$ variar no estator, "
        r"induzindo tensão trifásica senoidal $E_f$ à frequência $f$."
    )

    show_plot(fig_velocidade_sincrona_mes(), key="fig_3_ns")
    st.caption(
        "**Figura 3.2** — Velocidade síncrona em função do número de polos "
        "para 50 Hz (Europa) e 60 Hz (Brasil/EUA). "
        "Geradores de usinas a vapor operam com 2 polos (3000 ou 3600 rpm); "
        "hidroelétricas usam dezenas de polos (velocidades baixas)."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 4 — Curva de Magnetização OCC
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("4. Curva de Magnetização (OCC)")

    st.markdown(r"""
A **Curva Característica de Circuito Aberto** (OCC — *Open Circuit Characteristic*)
relaciona a tensão de excitação $E_f$ com a corrente de campo $I_f$ com os terminais
do estator em aberto ($I_a = 0$).

**Características observadas:**

- **Região linear (entreferro — AGL)**: para $I_f$ baixo, $E_f \propto I_f$
  (comportamento da *Air Gap Line* — AGL). Aqui o núcleo não está saturado.
- **Saturação magnética**: com o aumento de $I_f$, o núcleo entra em saturação
  e $E_f$ cresce mais lentamente que $I_f$.
- **Magnetismo residual**: a OCC real parte de um valor ligeiramente positivo
  de $E_f$ para $I_f = 0$, reflexo do fluxo remanente.

A AGL é usada para calcular a **reatância síncrona não-saturada** ($X_{s,nsat}$),
enquanto o ponto de operação nominal fornece o valor **saturado** ($X_{s,sat}$).
""")

    show_plot(fig_curva_occ_mes(), key="fig_4_occ")
    st.caption(
        "**Figura 4.1** — OCC (curva de circuito aberto) para a máquina "
        "195 MVA, 15 kV, 60 Hz (dados do ensaio real — SEN6 Q3). "
        "A linha tracejada é a AGL (Air Gap Line — região linear). "
        "A saturação ocorre acima de $I_f \\approx 450$ A."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 5 — Reação da Armadura
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("5. Reação da Armadura")

    st.markdown(r"""
Quando o gerador opera em carga ($I_a \neq 0$), as correntes no estator criam um
**campo magnético girante** $\Phi_a$ — chamado campo de reação da armadura.
O campo resultante total é a composição vetorial:

$$\Phi_r = \Phi_f + \Phi_a$$

O efeito de $\Phi_a$ sobre $\Phi_f$ depende do ângulo de defasagem entre $E_f$ e $I_a$
(ou seja, do fator de potência da carga):

| Fator de potência | Efeito de $\Phi_a$ | Resultado |
|---|---|---|
| Unitário (fp = 1) | $\Phi_a \perp \Phi_f$ | Distorção (cruzado) |
| Atrasado (indutivo) | $\Phi_a$ opõe $\Phi_f$ | **Desmagnetização** — $|\Phi_r| < |\Phi_f|$ |
| Adiantado (capacitivo) | $\Phi_a$ reforça $\Phi_f$ | **Magnetização** — $|\Phi_r| > |\Phi_f|$ |

No circuito equivalente, o efeito de $\Phi_a$ é modelado pela **reatância de reação
da armadura** $X_{ar}$, que junto com a reatância de dispersão $X_l$ forma a
**reatância síncrona** $X_s = X_{ar} + X_l$.
""")

    show_plot(fig_reacao_armadura_mes(), key="fig_5_1_reacao")
    st.caption(
        r"**Figura 5.1** — Composição vetorial dos fluxos: "
        r"$\Phi_f$ (campo do rotor), $\Phi_a$ (reação da armadura) "
        r"e $\Phi_r = \Phi_f + \Phi_a$ (fluxo resultante)."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 6 — Circuito Equivalente
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("6. Circuito Equivalente por Fase")

    st.markdown(r"""
O circuito equivalente monofásico da máquina síncrona cilíndrica por fase é:

$$E_f = V_t + I_a\,(R_a + jX_s) \quad \text{(Gerador)}$$

$$V_t = E_f + I_a\,(R_a + jX_s) \quad \text{(Motor)}$$

onde:
- $E_f$ — tensão de excitação (proporcional a $I_f$ e $n_s$)
- $V_t$ — tensão terminal por fase
- $I_a$ — corrente de armadura
- $R_a$ — resistência da armadura (geralmente $R_a \ll X_s$, muitas vezes desprezada)
- $X_s = X_{ar} + X_l$ — reatância síncrona
- $Z_s = R_a + jX_s$ — impedância síncrona

A **convenção de sinal** de $I_a$ distingue os dois modos:
no **gerador**, $I_a$ sai dos terminais; no **motor**, $I_a$ entra.
""")

    tab_g, tab_m = st.tabs(["⚡ Gerador", "🔌 Motor"])

    with tab_g:
        st.markdown(
            r"**Modo Gerador:** $E_f$ é a fonte; $I_a$ flui para a carga. "
            r"$E_f = V_t + I_a Z_s$"
        )
        buf_g = fig_circuito_equivalente_gerador_mes()
        b64_g = base64.b64encode(buf_g.read()).decode()
        st.markdown(
            f'<div class="fig-wrap"><div style="--fw:72%">'
            f'<img src="data:image/png;base64,{b64_g}" '
            f'style="width:100%;height:auto;display:block;"/>'
            f'</div></div>', unsafe_allow_html=True)
        st.caption(
            r"**Figura 6.1** — Circuito equivalente por fase no modo **gerador**: "
            r"$E_f$ (fonte interna), queda em $R_a$ e $jX_s$, tensão terminal $V_t$. "
            r"Corrente $I_a$ saindo dos terminais."
        )

    with tab_m:
        st.markdown(
            r"**Modo Motor:** $V_t$ é a fonte; $I_a$ é imposto pela rede. "
            r"$E_f = V_t - I_a Z_s$"
        )
        buf_m = fig_circuito_equivalente_motor_mes()
        b64_m = base64.b64encode(buf_m.read()).decode()
        st.markdown(
            f'<div class="fig-wrap"><div style="--fw:72%">'
            f'<img src="data:image/png;base64,{b64_m}" '
            f'style="width:100%;height:auto;display:block;"/>'
            f'</div></div>', unsafe_allow_html=True)
        st.caption(
            r"**Figura 6.2** — Circuito equivalente por fase no modo **motor**: "
            r"$V_t$ alimenta o circuito; $I_a$ entra pela armadura. "
            r"$E_f$ opõe-se parcialmente a $V_t$."
        )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 7 — Diagrama Fasorial
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("7. Diagrama Fasorial")

    st.markdown(r"""
O diagrama fasorial representa graficamente a equação do circuito equivalente
no plano complexo. Para a máquina cilíndrica (**gerador**):

$$\vec{E}_f = \vec{V}_t + R_a \vec{I}_a + jX_s \vec{I}_a$$

O **ângulo de carga** $\delta$ (ou ângulo de potência) é o ângulo entre $E_f$ e $V_t$:
- **Gerador**: $\delta > 0$ ($E_f$ adianta-se em relação a $V_t$)
- **Motor**: $\delta < 0$ ($E_f$ atrasa-se em relação a $V_t$)

O fator de potência afeta o posicionamento de $I_a$:
- **Carga indutiva (atrasada)**: $I_a$ atrasa $V_t$ — $E_f > V_t$ (sub-excitado no motor)
- **Carga capacitiva (adiantada)**: $I_a$ adianta $V_t$ — $E_f < V_t$ pode ocorrer
""")

    show_plot(fig_diagrama_fasorial_mes(
        Vt=1.0, Ef=1.35, delta_deg=28, Xs=1.0, Ra=0.05, modo="Gerador"),
        key="fig_7_1_static")
    st.caption(
        r"**Figura 7.1** — Diagrama fasorial do gerador síncrono cilíndrico: "
        r"$V_t$ (referência), $E_f$ adiantado por $\delta$, queda $R_a I_a$ e $jX_s I_a$. "
        r"Carga indutiva ($I_a$ atrasado)."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 8 — Barramento Infinito e Sincronismo
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("8. Barramento Infinito e Sincronismo")

    st.markdown(r"""
Na prática, geradores síncronos raramente alimentam cargas individuais — eles são
conectados a um **barramento infinito**: uma rede de potência com tantos geradores
em paralelo que sua tensão e frequência permanecem constantes independentemente
das ações de um único gerador.

**Condições para conexão ao barramento infinito:**
Para conectar um gerador à rede sem choque de corrente, é necessário sincronismo:

| Parâmetro | Condição |
|---|---|
| Tensão de linha | $V_{gerador} = V_{barramento}$ |
| Frequência | $f_{gerador} = f_{barramento}$ |
| Sequência de fases | Mesma sequência (A-B-C) |
| Ângulo de fase | Mesma fase instantânea |

O **sincronoscópio** é o instrumento que indica se as condições estão satisfeitas.
As **lâmpadas de sincronismo** são um método alternativo simples: quando apagadas
(tensão diferencial nula), o gerador está em sincronismo com a rede.

**Controle após conexão:**
- **Controle de potência ativa** P → ajuste da turbina (torque mecânico ↑ → $\delta$ ↑)
- **Controle de potência reativa** Q → ajuste da excitação $I_f$ ($I_f$ ↑ → $E_f$ ↑ → Q ↑)
""")

    show_fig(fig_barramento_infinito_mes(), width_frac=0.88)
    st.caption(
        "**Figura 8.1** — Esquema de conexão: turbina → gerador síncrono → "
        "transformador elevador → barramento infinito. "
        "A excitação CC controla $E_f$ (e portanto Q); a turbina controla P."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 9 — Modo Motor — Partida
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("9. Modo Motor — Partida")

    st.markdown(r"""
O motor síncrono **não parte diretamente da rede** em tensão e frequência nominais:
ao conectar o rotor parado ao campo girante do estator (que gira a $n_s$), o torque
médio resultante é **nulo** — o motor vibra sem partir.

Dois métodos de partida são utilizados:

**Método 1 — Partida por Frequência Variável (VFD)**

Um conversor de frequência parte de $f = 0$ e eleva gradualmente até $f_{nom}$,
mantendo $V/f$ constante. O rotor acompanha o campo em sincronismo durante
toda a aceleração. É o método preferido quando a máquina opera em velocidade variável.

**Método 2 — Partida com Enrolamento Amortecedor**

Um enrolamento tipo gaiola de esquilo é adicionado ao rotor (enrolamento amortecedor).
Com $I_f = 0$ e o estator alimentado na frequência nominal, o motor parte como
motor de indução. Ao atingir $n \approx n_s$, a corrente de campo $I_f$ é aplicada
e o rotor entra em sincronismo. O enrolamento amortecedor também serve para
amortecer oscilações em torno da velocidade síncrona durante perturbações.
""")

    show_fig(fig_partida_motor_mes(), width_frac=0.92)
    st.caption(
        "**Figura 9.1** — Métodos de partida do motor síncrono. "
        "Esquerda: VFD eleva gradualmente $f$ de 0 a $f_{nom}$. "
        "Direita: enrolamento amortecedor permite partida como motor de indução; "
        "ao atingir $n \\approx n_s$ o campo de excitação é ligado."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 10 — Ensaios OCC + SCC
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("10. Ensaios OCC + SCC — Determinação dos Parâmetros")

    st.markdown(r"""
Os parâmetros do circuito equivalente ($R_a$, $X_s$) são obtidos por ensaios:

**Resistência da armadura $R_a$**: medida direta com a máquina desligada
(método volt-ampere ou ponte de Wheatstone).

**Ensaio de Circuito Aberto (OCC)**: rotor em velocidade síncrona, terminais abertos.
Varia-se $I_f$ e mede-se $V_t = E_f$. Fornece a curva OCC e a AGL.

**Ensaio de Curto-Circuito (SCC)**: terminais em curto-circuito, rotor em $n_s$.
Varia-se $I_f$ e mede-se $I_a$. A característica é linear (a máquina não satura
pois o fluxo de entreferro é pequeno).

**Cálculo de $X_s$:**

$$X_{s,nsat} = \frac{E_{f,AGL}(I_{f0})/\sqrt{3}}{I_{a,SCC}(I_{f0})}$$

$$X_{s,sat} = \frac{E_{f,OCC}(I_{f0})/\sqrt{3}}{I_{a,SCC}(I_{f0})}$$

onde $E_{f,AGL}(I_{f0})$ é a tensão de linha lida na **linha do entreferro (AGL)**
e $E_{f,OCC}(I_{f0})$ é a tensão de linha lida na **curva OCC saturada** — ambas
avaliadas na mesma corrente de campo $I_{f0}$.
Na região saturada, a OCC dá tensão menor que a AGL para o mesmo $I_f$,
portanto $E_{f,OCC} \leq E_{f,AGL}$ e consequentemente $X_{s,sat} \leq X_{s,nsat}$.
Na prática, usa-se $X_{s,sat}$ para estudos de curto-circuito (condição saturada)
e $X_{s,nsat}$ como limite teórico superior (máquina não saturada).
""")

    show_plot(fig_occ_scc_mes(), key="fig_10_occ_scc")
    st.caption(
        "**Figura 10.1** — OCC (azul, eixo esquerdo) + SCC (vermelho, eixo direito) + AGL "
        "(tracejada cinza) para a máquina 195 MVA, 15 kV, 60 Hz. "
        "Os valores de $X_{s,sat}$ e $X_{s,nsat}$ são determinados no ponto de "
        "corrente de campo nominal ($I_f = 750$ A)."
    )


    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 11 — Potência e Torque
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("11. Potência Ativa, Reativa e Torque")

    st.markdown(r"""
**Potência ativa entregue à rede** (por fase e trifásica, $R_a \approx 0$):

$$P_{1\phi} = \frac{V_t E_f}{X_s} \sin\delta$$

$$P_{3\phi} = \frac{3\,V_t E_f}{X_s} \sin\delta$$

**Potência reativa** (por fase e trifásica):

$$Q_{1\phi} = \frac{V_t E_f \cos\delta - V_t^2}{X_s}$$

$$Q_{3\phi} = \frac{3\,V_t(E_f \cos\delta - V_t)}{X_s}$$

**Torque eletromagnético:**

$$T_{ind} = \frac{P_{3\phi}}{\omega_s} = \frac{3\,V_t E_f}{X_s\,\omega_s} \sin\delta$$

**Limites de estabilidade estática** ($R_a = 0$):

$$P_{max} = \frac{3\,V_t E_f}{X_s} \quad \text{(em } \delta = 90°\text{)}$$

$$T_{max} = \frac{3\,V_t E_f}{X_s\,\omega_s}$$

Para $|\delta| > 90°$ a máquina **perde sincronismo** — o rotor não consegue
acompanhar o campo girante. A operação estável é restrita a $0 < \delta < 90°$
no modo gerador e $-90° < \delta < 0$ no modo motor.

| Grandeza | Gerador | Motor |
|---|---|---|
| Sentido de $\delta$ | $\delta > 0$ ($E_f$ adianta $V_t$) | $\delta < 0$ ($E_f$ atrasa $V_t$) |
| Controle de P | ↑ torque da turbina → ↑ $\delta$ | ↑ carga mecânica → ↑ $|\delta|$ |
| Controle de Q | ↑ $I_f$ → ↑ $E_f$ → Q capacitivo | ↑ $I_f$ → corrige fp atrasado |
""")

    show_plot(fig_potencia_delta_mes(), key="fig_11_pdelta")
    st.caption(
        r"**Figura 11.1** — Curva $P \times \delta$ para gerador e motor: "
        r"potência máxima em $|\delta| = 90°$, limites de estabilidade marcados. "
        r"Região estável: $|\delta| < 90°$."
    )

    show_plot(fig_potencia_reativa_mes(), key="fig_11_qef")
    st.caption(
        r"**Figura 11.2** — Potência reativa $Q$ em função de $E_f$ (excitação) "
        r"para diferentes cargas ativas $P$. Sub-excitação → $Q < 0$ (absorve Q); "
        r"super-excitação → $Q > 0$ (fornece Q)."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 12 — Curva de Capacidade
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("12. Curva de Capacidade (Capability Curve)")

    st.markdown(r"""
A **curva de capacidade** (ou carta de capacidade) delimita a região de operação
segura de um gerador síncrono no plano $P \times Q$, respeitando simultaneamente
três limites físicos:

| Limite | Restrição | Causa |
|---|---|---|
| **Corrente de armadura** $I_a \leq I_{a,nom}$ | Círculo de raio $S_{nom} = 3V_t I_{a,nom}$ | Aquecimento do estator |
| **Corrente de campo** $I_f \leq I_{f,nom}$ | Arco de círculo com centro em $(0, -3V_t^2/X_s)$ | Aquecimento do rotor |
| **Limite de estabilidade** $\delta < 90°$ | Reta vertical $P = 3V_tE_f/X_s$ | Perda de sincronismo |

No plano $P \times Q$:
- O eixo $P$ representa potência ativa (MW).
- O eixo $Q$ positivo representa operação **capacitiva** (fornece Q à rede — super-excitado).
- O eixo $Q$ negativo representa operação **indutiva** (absorve Q da rede — sub-excitado).

O ponto de operação nominal está na interseção dos três limites.
""")

    show_plot(fig_curva_capacidade_mes(), key="fig_12_capability")
    st.caption(
        "**Figura 12.1** — Curva de capacidade (capability curve) de um gerador síncrono "
        "no plano $P \\times Q$ (pu). Região de operação segura delimitada pelo limite de "
        "armadura (arco externo), limite de campo (arco interno) e limite de estabilidade "
        "(reta vertical). Ponto nominal marcado."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 13 — Controle de Fator de Potência
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("13. Controle de Fator de Potência — Condensador Síncrono")

    st.markdown(r"""
Um motor síncrono operando **sem carga mecânica** — chamado **condensador síncrono**
(ou *compensador síncrono*) — pode ser usado exclusivamente para controle de fator
de potência em subestações e sistemas de transmissão.

**Princípio:** a tensão de excitação $E_f$ varia linearmente com $I_f$.
Com $V_t$ fixo (barramento infinito) e potência ativa $P \approx 0$:

$$I_a \approx \frac{E_f - V_t}{jX_s} \quad \text{(puramente reativa)}$$

| Excitação | $E_f$ vs $V_t$ | $I_a$ | Efeito na rede |
|---|---|---|---|
| **Sub-excitada** ($I_f$ baixo) | $E_f < V_t$ | Grande, **atrasada** | Absorve Q (reator) |
| **Excitação normal** | $E_f = V_t$ | Mínima (fp ≈ 1) | Neutro |
| **Super-excitada** ($I_f$ alto) | $E_f > V_t$ | Grande, **adiantada** | Fornece Q (capacitor) |

**Curva V ($I_a \times I_f$):** para cada nível de potência ativa $P$, a curva
$I_a \times I_f$ tem formato de "V" — corrente mínima no ponto de fp unitário
e crescente nos dois sentidos (sub e super-excitação). O conjunto de curvas V
para diferentes $P$ forma a **família de curvas V** da máquina.
""")

    show_plot(fig_curvas_v_mes(), key="fig_13_curvas_v")
    st.caption(
        r"**Figura 13.1** — Família de curvas V: corrente de armadura $I_a$ "
        r"em função da corrente de campo $I_f$ (pu) para diferentes cargas $P$. "
        r"Ponto de mínimo de cada curva corresponde ao fp unitário. "
        r"Linha tracejada: lugar geométrico dos pontos de fp = 1."
    )

    show_plot(fig_condensador_sincrono_mes(), key="fig_13_cond")
    st.caption(
        r"**Figura 13.2** — Diagrama fasorial do condensador síncrono: "
        r"sub-excitado (absorve Q, $I_a$ atrasado), normal e super-excitado "
        r"(fornece Q, $I_a$ adiantado). Potência ativa $P \approx 0$ em todos os casos."
    )

    # SEÇÃO 14 — Polos Salientes
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("14. Máquina Síncrona com Polos Salientes")

    st.markdown(r"""
Em máquinas com **polos salientes**, o entreferro é **não uniforme**: menor ao longo
dos polos (eixo direto **d**) e maior entre os polos (eixo em quadratura **q**).
Isso cria relutâncias diferentes nos dois eixos, tornando a análise fasorial mais complexa.

**Eixos d e q:**
- **Eixo direto (d)** — alinhado com o polo (fluxo de campo $\Phi_f$); relutância baixa → $X_d$ alto
- **Eixo em quadratura (q)** — interpolar; relutância alta → $X_q$ baixo

Relação típica: $X_d > X_q$, com $X_q \approx 50\text{--}80\%\,X_d$

**Reatâncias síncronas:**

$$X_d = X_{ad} + X_{al} \quad \text{(eixo direto)}$$

$$X_q = X_{aq} + X_{al} \quad \text{(eixo em quadratura)}$$

onde $X_{al}$ é a reatância de dispersão (igual nos dois eixos) e
$X_{ad} > X_{aq}$ pela diferença de relutância.

**Decomposição de $I_a$ em componentes d-q:**

$$I_d = I_a \sin\psi \qquad I_q = I_a \cos\psi \qquad \psi = \phi + \delta$$

onde $\phi$ é o ângulo de defasagem de $I_a$ em relação a $V_t$ e
$\delta$ é o ângulo de carga.

**Ensaio de escorregamento** — determina $X_d$ e $X_q$:
o rotor gira em velocidade próxima à síncrona com campo em aberto. A corrente
de estator oscila entre $I_{min}$ (eixo d, baixa relutância) e $I_{max}$ (eixo q, alta relutância):

$$X_d = \frac{V_{max}}{I_{min}} \qquad X_q = \frac{V_{min}}{I_{max}}$$
""")

    show_plot(fig_dq_decomposition_mes(), key="fig_14_1_dq")
    st.caption(
        r"**Figura 14.1** — Decomposição fasorial de $I_a$ em componentes "
        r"$I_d$ (eixo direto) e $I_q$ (eixo em quadratura). "
        r"$\psi = \phi + \delta$ é o ângulo de $I_a$ em relação ao eixo q."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 15 — Potência em Polos Salientes
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("15. Potência e Torque em Máquinas de Polos Salientes")

    st.markdown(r"""
### 15.1 Modelo d-q e Componentes de Corrente

Com $R_a = 0$, decompõe-se $I_a$ em:

- **Componente de eixo direto (d):** $I_d = I_a \sin\psi$,  onde $\psi = \phi + \delta$
- **Componente de eixo em quadratura (q):** $I_q = I_a \cos\psi$

Do diagrama fasorial obtém-se:

$$I_d = \frac{V_t \sin\delta}{X_d} \qquad I_q = \frac{E_f - V_t \cos\delta}{X_q}$$

### 15.2 Potência Ativa

A potência ativa trifásica ($R_a = 0$) resulta em **duas parcelas**:

$$P_{3\phi} = \frac{3\,V_t E_f}{X_d} \sin\delta + \frac{3\,V_t^2\,(X_d - X_q)}{2\,X_d\,X_q} \sin 2\delta$$

| Parcela | Expressão | Característica |
|---|---|---|
| **Excitação** | $\dfrac{3V_tE_f}{X_d}\sin\delta$ | Proporcional a $E_f$; idêntica à cilíndrica com $X_d$ |
| **Relutância** | $\dfrac{3V_t^2(X_d-X_q)}{2X_dX_q}\sin 2\delta$ | Independente de $E_f$; exclusiva dos polos salientes |

### 15.3 Potência Reativa

$$Q_{3\phi} = \frac{3\,V_t E_f}{X_d}\cos\delta - 3\,V_t^2\!\left(\frac{\cos^2\delta}{X_d} + \frac{\sin^2\delta}{X_q}\right)$$

| Condição | Sinal de Q | Efeito na rede |
|---|---|---|
| Super-excitado ($E_f \cos\delta > V_t$) | $Q > 0$ | Fornece reativo (capacitivo) |
| Excitação normal | $Q \approx 0$ | Neutro |
| Sub-excitado ($E_f \cos\delta < V_t$) | $Q < 0$ | Absorve reativo (indutivo) |

Para $X_d = X_q$ (cilíndrica), simplifica para $Q = \dfrac{3V_t(E_f\cos\delta - V_t)}{X_s}$.

### 15.4 Torque Eletromagnético

$$T_{ind} = \frac{P_{3\phi}}{\omega_s} = \frac{3\,V_t E_f}{X_d\,\omega_s}\sin\delta + \frac{3\,V_t^2(X_d-X_q)}{2\,X_d\,X_q\,\omega_s}\sin 2\delta$$

### 15.5 Comparação com a Máquina Cilíndrica

| Grandeza | Cilíndrica ($X_d = X_q = X_s$) | Polos Salientes ($X_d > X_q$) |
|---|---|---|
| $P_{max}$ | $\dfrac{3V_tE_f}{X_s}$ em $\delta = 90°$ | $> \dfrac{3V_tE_f}{X_d}$ em $\delta < 90°$ |
| Torque com $E_f = 0$ | Zero | $\neq 0$ (relutância) |
| Margem de estabilidade | Menor | Maior |
| Análise | Uma reatância $X_s$ | Duas reatâncias $X_d$, $X_q$ |
""")

    show_plot(fig_potencia_saliente_mes(), key="fig_15_psal")
    st.caption(
        r"**Figura 15.1** — Curva $P \times \delta$ para polos salientes (vermelho) "
        r"decomposta em componente de excitação (azul tracejado) e "
        r"componente de relutância (laranja pontilhado). "
        r"A máxima potência ocorre em $\delta < 90°$ — maior margem de estabilidade que a cilíndrica."
    )

    st.divider()

    # SEÇÃO 16 — Dinâmicas de Transitório
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("16. Dinâmicas de Transitório")

    st.markdown(r"""
### 16.1 Curto-Circuito Trifásico — Três Períodos

Ao aplicar um curto-circuito súbito nos terminais de um gerador em operação,
a corrente passa por **três períodos distintos** antes de atingir o regime permanente:

| Período | Duração | Reatância | Constante de tempo |
|---|---|---|---|
| **Subtransiente** | Alguns ciclos (ms) | $X_d''$ | $\tau_d'' \approx 0{,}06$ s |
| **Transiente** | Décimos de segundo | $X_d'$ | $\tau_d' \approx 6$ s |
| **Regime permanente** | Contínuo | $X_d$ | — |

Relação típica: $X_d'' < X_d' < X_d$ (ex.: 0,2 / 0,3 / 1,0 pu)

A corrente de curto-circuito máxima no instante $t = 0^+$:

$$I''_{cc} = \frac{E_f}{X_d''} \quad \text{(subtransiente)}$$

**Componente DC:** ao fechar o curto, pode existir componente DC que decai com
$\tau_a \approx 0{,}15$ s. A corrente total máxima instantânea é:

$$i_{total}(0^+) = \sqrt{2}\,I''_{cc} + \sqrt{2}\,I''_{cc} = 2\sqrt{2}\,I''_{cc}$$

(quando a componente DC é máxima — depende do ângulo de fechamento do curto).

**Valores típicos** em geradores de polos salientes:
$X_d = 1$ pu · $X_d' = 0{,}3$ pu · $X_d'' = 0{,}2$ pu ·
$\tau_d' = 6$ s · $\tau_d'' = 0{,}06$ s · $\tau_a = 0{,}15$ s
""")

    show_plot(fig_curto_circuito_mes(), key="fig_16_icc")
    st.caption(
        "**Figura 16.1** — Corrente de curto-circuito trifásico: envoltória AC (cinza), "
        "envoltória total com componente DC (laranja) e corrente instantânea (azul). "
        "Regiões subtransiente, transiente e regime permanente marcadas."
    )

    st.markdown(r"""
### 16.2 Estabilidade Dinâmica — Método das Áreas Equivalentes

Após uma perturbação (ex.: curto-circuito seguido de abertura da linha),
o gerador pode permanecer em sincronismo ou perder o sincronismo.

O **método das áreas equivalentes** determina graficamente o limite de estabilidade:

- **Área A₁** (acelerante): durante a falta, $P_e < P_m$ → o rotor acelera, $\delta$ aumenta.
- **Área A₂** (desacelerante): após o isolamento da falta, $P_e > P_m$ → o rotor desacelera.

**Critério de estabilidade:**

$$A_2 \geq A_1 \quad \Rightarrow \quad \text{sistema permanece em sincronismo}$$

O **ângulo crítico de abertura** $\delta_{cc}$ é o maior ângulo em que é possível
abrir o disjuntor e ainda manter $A_2 = A_1$ (limite de estabilidade).
""")

    show_plot(fig_area_equivalente_mes(), key="fig_16_area")
    st.caption(
        r"**Figura 16.2** — Método das áreas equivalentes: "
        r"área A₁ (acelerante, laranja) e A₂ (desacelerante, azul) na curva P×δ. "
        r"O sistema é estável enquanto $A_2 \geq A_1$. "
        r"$\delta_0$: pré-falta; $\delta_{cc}$: abertura do disjuntor; "
        r"$\delta_{max}$: máximo atingido; $\delta_1$: equilíbrio instável."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # EXPLORADORES INTERATIVOS
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("🎛️ Exploradores Interativos")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📐 Diagrama Fasorial",
        "📊 Curva V (Ia × If)",
        "📐 Potência × Ângulo δ",
        "🔵 Polos Salientes — Fasorial",
        "⚡ Polos Salientes — P×δ",
    ])

    # ── Aba 1: Diagrama Fasorial ──────────────────────────────────────────────
    with tab1:
        st.markdown("**Explore o diagrama fasorial da máquina cilíndrica.**")
        col_a, col_b = st.columns([1, 2])
        with col_a:
            modo_exp = st.radio("Modo:", ["Gerador", "Motor"], key="exp_ms_modo")
            Vt_exp   = st.slider("Vt (pu)", 0.5, 1.5, 1.0, 0.05, key="exp_ms_vt")
            Ef_exp   = st.slider("Ef (pu)", 0.3, 2.0, 1.25, 0.05, key="exp_ms_ef")
            Xs_exp   = st.slider("Xs (pu)", 0.3, 2.0, 1.0, 0.05, key="exp_ms_xs")
            Ra_exp   = st.slider("Ra (pu)", 0.0, 0.3, 0.0, 0.01, key="exp_ms_ra")
            dl_exp   = st.slider("δ (°)", -60, 60, 20, 1, key="exp_ms_delta")

        with col_b:
            fig_exp1 = fig_diagrama_fasorial_mes(
                Vt=Vt_exp, Ef=Ef_exp, delta_deg=dl_exp,
                Xs=Xs_exp, Ra=Ra_exp, modo=modo_exp)
            show_plot(fig_exp1, key="exp_fasorial_dyn")

    # ── Aba 2: Curva V ────────────────────────────────────────────────────────
    with tab2:
        st.markdown(
            r"**Curva V:** corrente de armadura $I_a$ em função da corrente de "
            r"campo $I_f$ para diferentes cargas ativas (motor)."
        )
        P_cv = st.slider("Potência ativa P (pu)", 0.0, 1.0, 0.5, 0.1, key="exp_ms_P")
        Xs_cv = st.slider("Xs (pu)", 0.5, 2.0, 1.0, 0.1, key="exp_ms_xs2")
        Vt_cv = 1.0

        If_range = np.linspace(0.2, 3.0, 200)
        fig_cv = go.Figure()
        for P_val, cor in [(P_cv, AZ)]:
            Ia_list = []
            for Ef_val in If_range:
                try:
                    Ef_c = complex(Ef_val * math.cos(0), Ef_val * math.sin(0))
                    Vt_c = complex(Vt_cv, 0)
                    # Motor: Ia = (Vt - Ef) / jXs
                    Ia_c = (Vt_c - Ef_c) / complex(0, Xs_cv)
                    Ia_list.append(abs(Ia_c))
                except Exception:
                    Ia_list.append(float('nan'))

            fig_cv.add_trace(go.Scatter(
                x=If_range, y=Ia_list,
                mode="lines", line=dict(color=AZ, width=2.5),
                name=f"P = {P_val:.1f} pu",
                hovertemplate="If=%{x:.2f}<br>Ia=%{y:.3f} pu"))

        fig_cv.add_vline(x=1.0, line=dict(color=VM, width=1.2, dash="dot"))
        fig_cv.update_layout(
            title=dict(text="Curva V — Ia × If (Motor Síncrono)",
                       font=dict(size=15, color=TX)),
            xaxis=dict(title=dict(text="Excitação de campo Ef/V_nom (pu)",
                                  font=dict(size=13, color=TX)),
                       tickfont=dict(size=12),
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Corrente de armadura Ia (pu)",
                                  font=dict(size=13, color=TX)),
                       tickfont=dict(size=12), range=[0, 3],
                       gridcolor="rgba(128,128,128,.15)"),
            height=380, margin=dict(l=65, r=20, t=55, b=65),
        )
        show_plot(fig_cv, key="exp_cv_plot")

    # ── Aba 3: Potência × Ângulo δ ────────────────────────────────────────────
    with tab3:
        st.markdown(
            r"**Curva P×δ:** potência ativa em função do ângulo de carga $\delta$ "
            r"(gerador). Limite de estabilidade em $\delta = 90°$."
        )
        Ef_pd = st.slider("Ef (pu)", 0.5, 2.0, 1.3, 0.1, key="exp_ms_ef3")
        Xs_pd = st.slider("Xs (pu)", 0.3, 2.0, 1.0, 0.1, key="exp_ms_xs3")
        Vt_pd = 1.0

        delta_arr = np.linspace(-180, 180, 400)
        P_arr = (Vt_pd * Ef_pd / Xs_pd) * np.sin(np.radians(delta_arr))

        fig_pd = go.Figure()
        fig_pd.add_trace(go.Scatter(
            x=delta_arr, y=P_arr, mode="lines",
            line=dict(color=AZ, width=2.8),
            name=f"Ef={Ef_pd:.1f} pu, Xs={Xs_pd:.1f} pu",
            hovertemplate="δ=%{x:.0f}°<br>P=%{y:.3f} pu"))

        P_max = Vt_pd * Ef_pd / Xs_pd
        fig_pd.add_hline(y=P_max, line=dict(color=VM, width=1.3, dash="dot"))
        fig_pd.add_annotation(x=120, y=P_max + 0.05,
            text=f"<b>P_max = {P_max:.2f} pu</b>",
            showarrow=False, font=dict(size=12, color=VM))
        fig_pd.add_vline(x=90, line=dict(color=CZ, width=1.0, dash="dot"))
        fig_pd.add_vline(x=-90, line=dict(color=CZ, width=1.0, dash="dot"))

        fig_pd.update_layout(
            title=dict(text=r"Potência Ativa × Ângulo de Carga δ  —  P = (Vt·Ef/Xs)·sin δ",
                       font=dict(size=14, color=TX)),
            xaxis=dict(title=dict(text="Ângulo de carga δ (°)",
                                  font=dict(size=13, color=TX)),
                       tickfont=dict(size=12), range=[-180, 180],
                       tickvals=[-180,-135,-90,-45,0,45,90,135,180],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Potência ativa P (pu)",
                                  font=dict(size=13, color=TX)),
                       tickfont=dict(size=12),
                       gridcolor="rgba(128,128,128,.15)"),
            height=380, margin=dict(l=65, r=20, t=55, b=65),
        )
        show_plot(fig_pd, key="exp_pd_plot")

    # ── Aba 4: Polos Salientes — Fasorial ─────────────────────────────────────
    with tab4:
        st.markdown("**Diagrama fasorial da máquina de polos salientes** com decomposição $I_d$/$I_q$.")
        col_a4, col_b4 = st.columns([1, 2])
        with col_a4:
            Vt_s  = st.slider("Vt (pu)", 0.5, 1.5, 1.0, 0.05, key="exp_sal_vt")
            Ef_s  = st.slider("Ef (pu)", 0.3, 2.0, 1.2, 0.05, key="exp_sal_ef")
            Xd_s  = st.slider("Xd (pu)", 0.5, 2.0, 1.0, 0.05, key="exp_sal_xd")
            Xq_s  = st.slider("Xq (pu)", 0.2, 1.5, 0.6, 0.05, key="exp_sal_xq")
            dl_s  = st.slider("δ (°)",   5,   80,  25,  1,    key="exp_sal_delta")
            if Xq_s >= Xd_s:
                st.warning("Xq deve ser < Xd para polos salientes.")
                Xq_s = Xd_s * 0.65
        with col_b4:
            show_plot(fig_fasorial_saliente_mes(
                Vt=Vt_s, Ef=Ef_s, delta_deg=dl_s, Xd=Xd_s, Xq=Xq_s),
                key="exp_sal_fas")

    # ── Aba 5: Polos Salientes — P×δ ──────────────────────────────────────────
    with tab5:
        st.markdown(
            r"**Curva P×δ de polos salientes:** componente de excitação + componente de relutância."
        )
        col_c5, col_d5 = st.columns([1, 3])
        with col_c5:
            Vt_p  = st.slider("Vt (pu)", 0.5, 1.5, 1.0, 0.05, key="exp_psal_vt")
            Ef_p  = st.slider("Ef (pu)", 0.0, 2.0, 1.2, 0.05, key="exp_psal_ef")
            Xd_p  = st.slider("Xd (pu)", 0.5, 2.0, 1.0, 0.05, key="exp_psal_xd")
            Xq_p  = st.slider("Xq (pu)", 0.2, 1.5, 0.6, 0.05, key="exp_psal_xq")
            if Xq_p >= Xd_p:
                st.warning("Xq deve ser < Xd.")
                Xq_p = Xd_p * 0.65
        with col_d5:
            delta_e = np.linspace(-180, 180, 500)
            dr = np.radians(delta_e)
            P_e_cil = (3*Vt_p*Ef_p / Xd_p) * np.sin(dr)
            P_e_rel = (3*Vt_p**2*(Xd_p-Xq_p)/(2*Xd_p*Xq_p)) * np.sin(2*dr)
            P_e_sal = P_e_cil + P_e_rel
            fig_ps = go.Figure()
            fig_ps.add_trace(go.Scatter(x=delta_e, y=P_e_cil, mode="lines",
                line=dict(color=AZ, width=2.0, dash="dash"), name="Excitação"))
            fig_ps.add_trace(go.Scatter(x=delta_e, y=P_e_rel, mode="lines",
                line=dict(color=LR, width=1.8, dash="dot"), name="Relutância"))
            fig_ps.add_trace(go.Scatter(x=delta_e, y=P_e_sal, mode="lines",
                line=dict(color=VM, width=3.0), name="Total (saliente)"))
            idx_mx = int(np.argmax(P_e_sal[:250]))
            fig_ps.add_trace(go.Scatter(
                x=[delta_e[idx_mx]], y=[P_e_sal[idx_mx]], mode="markers",
                marker=dict(color=VM, size=11, symbol="star"),
                name=f"P_max={P_e_sal[idx_mx]:.2f} pu @ δ={delta_e[idx_mx]:.0f}°"))
            fig_ps.add_hline(y=0, line=dict(color=CZ, width=0.8))
            fig_ps.add_vline(x=90,  line=dict(color=CZ, width=1, dash="dot"))
            fig_ps.add_vline(x=-90, line=dict(color=CZ, width=1, dash="dot"))
            fig_ps.update_layout(
                xaxis=dict(tickvals=[-180,-90,0,90,180], range=[-185,185],
                           gridcolor="rgba(128,128,128,.15)",
                           title=dict(text="δ (°)", font=dict(size=13, color=TX))),
                yaxis=dict(gridcolor="rgba(128,128,128,.15)",
                           title=dict(text="P (pu)", font=dict(size=13, color=TX))),
                legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
                height=400, margin=dict(l=65, r=20, t=40, b=65),
            )
            show_plot(fig_ps, key="exp_psal_plot")


    # ═══════════════════════════════════════════════════════════════════════════
    # REFERÊNCIAS
    # ═══════════════════════════════════════════════════════════════════════════
    with st.expander("📚 Referências Bibliográficas"):
        st.markdown("""
- BARBI, I. *Teoria Fundamental do Motor de Indução*. Santa Catarina: Editora UFSC, 1985.
- CHAPMAN, S. J. *Fundamentos de Máquinas Elétricas*. São Paulo: McGraw-Hill, 5ª ed., 2013.
- JACOBINA, C.; LIMA, A. M. *Acionamentos de Máquinas Elétricas de Alto Desempenho*. Minicurso XIV CBA, Natal, 2002.
- KOSOW, I. *Máquinas Elétricas e Transformadores*. São Paulo: Globo, 14ª reimp., 2000.
- UMANS, S. D. *Máquinas Elétricas de Fitzgerald e Kingsley*. São Paulo: McGraw-Hill, 7ª ed., 2014.
- BIM, E. *Máquinas Elétricas e Acionamento*. Rio de Janeiro: Campus Elsevier, 2009.
- SEN, P. C. *Princípios de Máquinas Elétricas e Eletrônica de Potência*. Wiley, 3ª ed., 2013.
""")

    # ── Rodapé ────────────────────────────────────────────────────────────────
    st.markdown("""
<div style="text-align:center; color:#6b7280; font-size:0.82em; margin-top:2rem;">
⚡ SINTONIA — Máquinas Elétricas<br>
Prof. Marcus V A Fernandes · IFRN-CNAT · marcus.fernandes@ifrn.edu.br<br>
🌐 Módulo 5 — Máquinas Síncronas Polifásicas · v1.0
</div>
""", unsafe_allow_html=True)
