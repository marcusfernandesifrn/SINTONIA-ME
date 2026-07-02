"""
⚙️ Motores de Baixa Potência: Indução Monofásica
Disciplina: Conversão Eletromecânica de Energia I
Curso: Engenharia de Energia
Instituição: IFRN — Campus Natal-Central (CNAT)
Autor: Marcus V A Fernandes · marcus.fernandes@ifrn.edu.br · v1.0

Fonte: PPTX-fonte do Módulo 6 — "CEEI - MMF - 01 - Inducao"
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
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
    .fig-wrap { display:flex; justify-content:center; width:100%; }
    .fig-wrap > div { width:100%; }
    @media (min-width: 769px) {
        .fig-wrap > div { width:var(--fw,65%); max-width:var(--fw,65%); }
    }
    .fig-wrap img { width:100% !important; height:auto !important; }
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
            f'<div class="fig-wrap"><div style="--fw:{pct}">'
            f'<img src="data:image/png;base64,{b64}" '
            f'style="width:100%;height:auto;display:block;"/>'
            f'</div></div>', unsafe_allow_html=True)

    def show_plot(fig, key=None, height=None):
        if height:
            fig.update_layout(height=height)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=TX, size=12), margin=dict(l=55, r=20, t=40, b=45),
            autosize=True)
        fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,.18)",
                         zeroline=True, zerolinecolor="rgba(128,128,128,.35)")
        fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,.18)",
                         zeroline=True, zerolinecolor="rgba(128,128,128,.35)")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False, "responsive": True}, key=key)

    def _mpl_base_off(figsize=(6, 5)):
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_alpha(0); ax.set_facecolor("none")
        ax.set_aspect("equal"); ax.axis("off")
        return fig, ax

    # ═══════════════════════════════════════════════════════════════════════════
    # FIGURAS
    # ═══════════════════════════════════════════════════════════════════════════

    def fig_estrutura_monofasico():
        """Seção transversal do motor de indução monofásico com polo saliente."""
        fig, ax = _mpl_base_off((8, 5.5))
        ax.set_xlim(-1, 13); ax.set_ylim(-0.5, 6)

        # ── Painel esquerdo: motor monofásico básico ─────────────────────────
        cx, cy, R_ext, R_int, R_rot = 3.0, 3.0, 2.6, 2.1, 1.55

        # Carcaça / estator
        ax.add_patch(mpatches.Wedge((cx,cy), R_ext, 0, 360,
            width=R_ext-R_int, fc="#d0d8e8", ec=TX, lw=1.2))
        # Enrolamento principal (em cima e em baixo)
        for ang, lbl in [(90,"M"),(270,"M")]:
            r = (R_ext+R_int)/2
            ax.add_patch(mpatches.Circle(
                (cx+r*math.cos(math.radians(ang)),
                 cy+r*math.sin(math.radians(ang))),
                0.32, fc=AZ, ec="white", lw=1.0, zorder=4))
            ax.text(cx+r*math.cos(math.radians(ang)),
                    cy+r*math.sin(math.radians(ang)),
                    lbl, ha="center", va="center",
                    fontsize=7, color="white", fontweight="bold", zorder=5)
        # Enrolamento auxiliar (lateral)
        for ang, lbl in [(0,"A"),(180,"A")]:
            r = (R_ext+R_int)/2
            ax.add_patch(mpatches.Circle(
                (cx+r*math.cos(math.radians(ang)),
                 cy+r*math.sin(math.radians(ang))),
                0.28, fc=LR, ec="white", lw=1.0, zorder=4))
            ax.text(cx+r*math.cos(math.radians(ang)),
                    cy+r*math.sin(math.radians(ang)),
                    lbl, ha="center", va="center",
                    fontsize=7, color="white", fontweight="bold", zorder=5)
        # Entreferro
        ax.add_patch(mpatches.Wedge((cx,cy), R_int, 0, 360,
            width=R_int-R_rot, fc="#f0f4ff", ec=CZ, lw=0.5, alpha=0.5))
        # Rotor (gaiola)
        ax.add_patch(mpatches.Circle((cx,cy), R_rot, fc="#c8d8f0", ec=TX, lw=1.2))
        for a in range(0, 360, 30):
            ax.add_patch(mpatches.Circle(
                (cx+R_rot*0.78*math.cos(math.radians(a)),
                 cy+R_rot*0.78*math.sin(math.radians(a))),
                0.15, fc=LR, ec="white", lw=0.7, alpha=0.9, zorder=4))
        ax.add_patch(mpatches.Circle((cx,cy), 0.35, fc=CZ, ec=TX, lw=1.0, zorder=5))

        ax.text(cx, -0.3, "Motor Monofásico\n(rotor gaiola)",
                ha="center", fontsize=9.5, fontweight="bold", color=TX)
        ax.text(cx-3.5, 4.0, "M — enrol. principal", fontsize=8.5, color=AZ)
        ax.text(cx-3.5, 3.5, "A — enrol. auxiliar",  fontsize=8.5, color=LR)

        # ── Painel direito: polo sombreado ────────────────────────────────────
        px = 8.5
        # Polo principal (retângulo arredondado)
        ax.add_patch(mpatches.FancyBboxPatch(
            (px-1.4, 1.2), 2.8, 3.6,
            boxstyle="round,pad=0.1", fc="#d0d8e8", ec=TX, lw=1.5))
        ax.text(px, 3.0, "Polo\nprincipal", ha="center", fontsize=9.5,
                color=TX, fontweight="bold")
        # Parte sombreada (anel de cobre)
        ax.add_patch(mpatches.FancyBboxPatch(
            (px+0.25, 1.35), 0.95, 3.3,
            boxstyle="round,pad=0.08", fc="#c8a800", ec="#8b6000", lw=1.8, alpha=0.85))
        ax.text(px+0.72, 3.0, "Parte\nsombreada\n(anel Cu)",
                ha="center", fontsize=7.5, color="#4a3000", fontweight="bold")
        # Rotor simplificado
        ax.add_patch(mpatches.FancyBboxPatch(
            (px-1.6, 0.2), 3.2, 0.8,
            boxstyle="round,pad=0.1", fc="#c8d8f0", ec=TX, lw=1.2))
        ax.text(px, 0.6, "Rotor (gaiola)", ha="center", fontsize=9, color=TX)
        # Seta de rotação
        ax.annotate("", xy=(px+2.2, 0.6), xytext=(px-2.0, 0.6),
                    arrowprops=dict(arrowstyle="-|>", color=VD, lw=2.0, mutation_scale=14))
        ax.text(px, -0.3, "Motor de Polos Sombreados",
                ha="center", fontsize=9.5, fontweight="bold", color=TX)
        # Fluxo
        ax.annotate("", xy=(px-0.5, 5.3), xytext=(px-0.5, 4.8),
                    arrowprops=dict(arrowstyle="-|>", color=VM, lw=1.8, mutation_scale=12))
        ax.text(px-0.5, 5.5, r"$\Phi_{ns}$", ha="center", fontsize=11, color=VM)
        ax.annotate("", xy=(px+0.72, 5.3), xytext=(px+0.72, 4.8),
                    arrowprops=dict(arrowstyle="-|>", color=AZ, lw=1.8, mutation_scale=12))
        ax.text(px+0.72, 5.5, r"$\Phi_s$", ha="center", fontsize=11, color=AZ)

        fig.suptitle("Estrutura dos Motores de Indução Monofásicos",
                     fontsize=12, fontweight="bold", color=TX, y=1.01)
        fig.tight_layout(pad=0.5)
        return fig

    def fig_campos_direto_oposto():
        """Plotly: Ff e Fb — campos direto e oposto em função do escorregamento."""
        s = np.linspace(0.01, 1.0, 300)
        sb = 2 - s

        # Modelo simplificado: correntes proporcionais a 1/Z
        R2 = 0.18; X2 = 0.25
        Zf = np.sqrt((R2/s)**2     + X2**2)
        Zb = np.sqrt((R2/sb)**2   + X2**2)
        If = 1.0 / Zf
        Ib = 1.0 / Zb

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=s, y=If/If.max(), mode="lines",
            line=dict(color=AZ, width=2.8), name="I₂f (campo direto)",
            hovertemplate="s=%{x:.3f}<br>I₂f=%{y:.3f} pu"))
        fig.add_trace(go.Scatter(x=s, y=Ib/If.max(), mode="lines",
            line=dict(color=VM, width=2.8), name="I₂b (campo oposto)",
            hovertemplate="s=%{x:.3f}<br>I₂b=%{y:.3f} pu"))

        fig.add_vline(x=0, line=dict(color=CZ, width=1, dash="dot"))
        fig.add_vline(x=1, line=dict(color=CZ, width=1, dash="dot"))
        fig.add_annotation(x=0.08, y=0.95,
            text="Repouso<br>(s=1)", showarrow=False,
            font=dict(size=10, color=CZ), bgcolor="rgba(255,255,255,0.8)")
        fig.add_annotation(x=0.92, y=0.95,
            text="Síncrono<br>(s=0)", showarrow=False,
            font=dict(size=10, color=CZ), bgcolor="rgba(255,255,255,0.8)",
            xanchor="right")

        fig.update_layout(
            title=dict(text="Correntes dos Campos Direto e Oposto × Escorregamento",
                       font=dict(size=15, color=TX)),
            xaxis=dict(title=dict(text="Escorregamento s", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[0, 1.02],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Corrente (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12),
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
            height=400, margin=dict(l=70, r=30, t=60, b=70))
        return fig

    def fig_torque_direto_oposto():
        """Plotly: Tf, Tb e Tresultante × escorregamento."""
        s = np.linspace(0.01, 1.99, 600)
        sb = 2 - s

        R2 = 0.20; X2 = 0.30; Xm = 3.5; V1 = 1.0
        ws = 1.0

        def torque(sl, R2, X2, Xm, V1, ws):
            Zr = R2/sl + 1j*X2
            Zm = 1j*Xm
            Z2eq = Zm*Zr/(Zm+Zr)
            I1 = V1 / (1j*X2 + Z2eq)
            E1 = I1 * Z2eq
            I2 = E1 / Zr
            P = 3*abs(I2)**2 * R2*(1-sl)/sl
            return P / ws

        Tf = np.array([torque(si, R2, X2, Xm, V1/2, ws) for si in s])
        Tb = np.array([torque(si, R2, X2, Xm, V1/2, ws) for si in sb])
        Tnet = Tf - Tb

        # Only show s in [0,1] for the resultant
        mask = (s >= 0) & (s <= 1)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=s[mask], y=Tf[mask], mode="lines",
            line=dict(color=AZ, width=2.2, dash="dash"),
            name="T_f (campo direto)"))
        fig.add_trace(go.Scatter(x=s[mask], y=-Tb[mask], mode="lines",
            line=dict(color=VM, width=2.2, dash="dash"),
            name="T_b (campo oposto, negativo)"))
        fig.add_trace(go.Scatter(x=s[mask], y=Tnet[mask], mode="lines",
            line=dict(color=VD, width=3.0),
            name="T_resultante = T_f − T_b"))

        fig.add_hline(y=0, line=dict(color=CZ, width=1.0))
        fig.add_annotation(x=0.5, y=max(Tnet[mask])*1.05,
            text="<b>T_resultante</b>", showarrow=False,
            font=dict(size=12, color=VD))

        fig.update_layout(
            title=dict(text="Torques Direto, Oposto e Resultante × Escorregamento",
                       font=dict(size=15, color=TX)),
            xaxis=dict(title=dict(text="Escorregamento s", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[0, 1.02],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Torque (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12),
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.22),
            height=440, margin=dict(l=70, r=30, t=60, b=100))
        return fig

    def fig_escorregamentos():
        """Matplotlib: diagrama explicativo de sf e sb."""
        fig, ax = plt.subplots(figsize=(10, 3.2), facecolor='white')
        ax.set_facecolor('white'); ax.axis('off')
        ax.set_xlim(0, 12); ax.set_ylim(0, 3.5)

        def bloco(cx, cy, w, h, txt, cor, fs=9.5):
            ax.add_patch(mpatches.FancyBboxPatch(
                (cx-w/2, cy-h/2), w, h,
                boxstyle="round,pad=0.1", fc="#f0f4ff", ec=cor, lw=1.8))
            ax.text(cx, cy, txt, ha="center", va="center",
                    fontsize=fs, color=TX, fontweight="bold")

        def seta(x1, y1, x2, y2, cor=TX):
            ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle="-|>", color=cor, lw=1.8, mutation_scale=13))

        # Linha de velocidades
        for x, lbl, cor in [(1.5,"−ns\n(s=2)",VM),(4.0,"0\n(s=1)",CZ),
                             (7.0,"n\n(0<s<1)",VD),(10.5,"ns\n(s=0)",AZ)]:
            ax.plot(x, 2.0, "o", ms=10, color=cor, zorder=5)
            ax.text(x, 1.55, lbl, ha="center", fontsize=9, color=cor, fontweight="bold")

        ax.plot([1.5, 10.5], [2.0, 2.0], color=CZ, lw=2.0, zorder=3)

        # Setas de escorregamento
        ax.annotate("", xy=(7.0, 2.6), xytext=(10.5, 2.6),
            arrowprops=dict(arrowstyle="-|>", color=AZ, lw=2.0, mutation_scale=13))
        ax.text(8.75, 2.85, r"$s_f = \dfrac{n_s - n}{n_s}$",
                ha="center", fontsize=11, color=AZ)

        ax.annotate("", xy=(7.0, 3.35), xytext=(1.5, 3.35),
            arrowprops=dict(arrowstyle="-|>", color=VM, lw=2.0, mutation_scale=13))
        ax.text(4.25, 3.55, r"$s_b = \dfrac{n_s + n}{n_s} = 2 - s_f$",
                ha="center", fontsize=11, color=VM)

        ax.set_title("Escorregamentos em relação aos campos direto (f) e oposto (b)",
                     fontsize=11, fontweight="bold", color=TX, pad=6)
        fig.tight_layout(pad=0.4)
        return fig

    def fig_circuito_equivalente_mono():
        """Matplotlib: circuito equivalente do motor monofásico (modelo dividido)."""
        fig, ax = plt.subplots(figsize=(12, 4.5), facecolor='white')
        ax.set_facecolor('white'); ax.axis('off')
        ax.set_xlim(0, 14); ax.set_ylim(0, 5)

        def seg(x1,y1,x2,y2,cor=TX,lw=1.8):
            ax.plot([x1,x2],[y1,y2],color=cor,lw=lw)

        def seta(x1,y1,x2,y2,cor=TX,lw=1.8):
            ax.annotate("",xy=(x2,y2),xytext=(x1,y1),
                arrowprops=dict(arrowstyle="-|>",color=cor,lw=lw,mutation_scale=13))

        def elem(cx,cy,w,h,lbl,cor,fs=9):
            ax.add_patch(mpatches.FancyBboxPatch(
                (cx-w/2,cy-h/2),w,h,boxstyle="round,pad=0.06",
                fc="white",ec=cor,lw=1.8))
            ax.text(cx,cy,lbl,ha="center",va="center",fontsize=fs,color=TX)

        CY = 3.5
        # Fonte V1
        ax.add_patch(mpatches.Circle((0.8,CY),0.38,fc="white",ec=TX,lw=1.8))
        ax.plot([0.8-0.25,0.8+0.25],[CY,CY],color=TX,lw=1.0)
        ax.text(0.8,CY+0.6,"$V_1$",ha="center",fontsize=11,color=AZ,fontweight="bold")

        # R1, X1
        seg(1.18,CY,1.8,CY)
        elem(2.2,CY,0.8,0.55,r"$R_1$",TX)
        seg(2.6,CY,3.0,CY)
        elem(3.5,CY,0.8,0.55,r"$X_1$",TX)
        seg(3.9,CY,4.3,CY)

        # Bifurcação
        ax.plot(4.3,CY,".",ms=10,color=TX,zorder=5)

        # Ramo Xmag
        seg(4.3,CY,4.3,2.0)
        elem(4.3,1.6,0.8,0.55,r"$X_{mag}$",CI,8.5)
        seg(4.3,1.3,4.3,0.8)
        seg(0.8,0.8,12.0,0.8)
        seg(0.8,CY-0.38,0.8,0.8)

        # Ramo campo direto: ½Xm + ½R2/s
        seg(4.3,CY,5.2,CY)
        seg(5.2,CY,5.2,CY+0.6)
        elem(5.8,CY+0.6,0.9,0.5,r"$\frac{1}{2}X_2'$",AZ,8)
        seg(6.25,CY+0.6,6.7,CY+0.6)
        elem(7.3,CY+0.6,0.9,0.5,r"$\frac{R_2'}{2s}$",AZ,8)
        seg(7.75,CY+0.6,8.1,CY+0.6)
        seg(8.1,CY+0.6,8.1,CY)
        ax.text(6.65,CY+1.2,"Campo direto ($Z_f$)",ha="center",fontsize=9,color=AZ)

        # Ramo campo oposto: ½Xm + ½R2/(2-s)
        seg(5.2,CY,5.2,CY-0.6)
        elem(5.8,CY-0.6,0.9,0.5,r"$\frac{1}{2}X_2'$",VM,8)
        seg(6.25,CY-0.6,6.7,CY-0.6)
        elem(7.3,CY-0.6,1.1,0.5,r"$\frac{R_2'}{2(2-s)}$",VM,7.5)
        seg(7.85,CY-0.6,8.1,CY-0.6)
        seg(8.1,CY-0.6,8.1,CY)
        ax.text(6.65,CY-1.2,"Campo oposto ($Z_b$)",ha="center",fontsize=9,color=VM)

        # Reunião e carga R2'(1-s)/s
        seg(8.1,CY,9.0,CY)
        ax.plot(8.1,CY,".",ms=10,color=TX,zorder=5)
        ax.plot(9.0,CY,".",ms=10,color=TX,zorder=5)
        seg(9.0,CY,9.0,0.8)

        # Corrente Ia
        seta(4.6,CY+0.2,6.5,CY+0.2,AZ)

        ax.set_title("Circuito Equivalente do Motor de Indução Monofásico",
                     fontsize=12, fontweight="bold", color=TX, pad=8)
        fig.tight_layout(pad=0.3)
        return fig

    def fig_metodos_partida():
        """Plotly: torque × velocidade para os quatro métodos de partida."""
        n = np.linspace(0, 1, 300)  # n/ns normalizado
        s = 1 - n

        def T_perfil(s, Tst_pu, Tmax_pu, s_max=0.12):
            # Aproximação com componente de resistência no rotor
            Tf = Tmax_pu * 2 / (s/s_max + s_max/s + 0.15)
            Tb = Tmax_pu * 0.18 / (1 + (2-s)/0.08)
            return np.clip(Tf - Tb + (Tst_pu - (Tmax_pu*2/(1/s_max+s_max)-Tmax_pu*0.18/(1+1/0.08)))*np.exp(-s*3), 0, None)

        configs = [
            ("Fase dividida",            0.15, 0.85, VM,  "solid",  1.5),
            ("Capacitor de partida",     0.35, 0.90, AZ,  "solid",  2.5),
            ("Capacitor permanente",     0.12, 0.80, VD,  "dash",   2.0),
            ("Polos sombreados",         0.06, 0.65, LR,  "dot",    2.0),
        ]

        fig = go.Figure()
        for nome, tst, tmax, cor, dash, lw in configs:
            T = T_perfil(s, tst, tmax)
            fig.add_trace(go.Scatter(
                x=n*100, y=T, mode="lines",
                line=dict(color=cor, width=lw, dash=dash),
                name=nome,
                hovertemplate=f"{nome}<br>n/ns=%{{x:.1f}}%<br>T=%{{y:.3f}} pu"))

        fig.add_vline(x=0,   line=dict(color=CZ, width=1.0, dash="dot"))
        fig.add_vline(x=100, line=dict(color=CZ, width=1.0, dash="dot"))
        fig.add_hline(y=0,   line=dict(color=CZ, width=0.8))

        fig.update_layout(
            title=dict(text="Curva T×n — Comparativo dos Métodos de Partida",
                       font=dict(size=15, color=TX)),
            xaxis=dict(title=dict(text="Velocidade n/nₛ (%)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[-2, 103],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Torque (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[-0.05, 1.15],
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)",
                        orientation="h", y=-0.22),
            height=440, margin=dict(l=70, r=30, t=60, b=100))
        return fig

    def fig_fase_dividida():
        """Matplotlib: esquema da partida por fase dividida."""
        fig, ax = plt.subplots(figsize=(10, 4.0), facecolor='white')
        ax.set_facecolor('white'); ax.axis('off')
        ax.set_xlim(0, 12); ax.set_ylim(0, 4.5)

        def bloco(cx, cy, w, h, txt, cor, fs=9.5):
            ax.add_patch(mpatches.FancyBboxPatch(
                (cx-w/2, cy-h/2), w, h,
                boxstyle="round,pad=0.1", fc="#f0f4ff", ec=cor, lw=2.0))
            ax.text(cx, cy, txt, ha="center", va="center",
                    fontsize=fs, color=TX, fontweight="bold")

        def seta(x1,y1,x2,y2,cor=TX,lw=1.8):
            ax.annotate("",xy=(x2,y2),xytext=(x1,y1),
                arrowprops=dict(arrowstyle="-|>",color=cor,lw=lw,mutation_scale=13))

        # Fonte monofásica
        ax.add_patch(mpatches.Circle((1.2,2.5),0.4,fc="white",ec=TX,lw=1.8))
        ax.text(1.2,3.1,"$V_1$",ha="center",fontsize=12,color=AZ,fontweight="bold")
        ax.text(1.2,2.5,"~",ha="center",fontsize=16,color=TX)

        # Enrolamento principal
        ax.plot([1.6,2.8],[3.2,3.2],color=TX,lw=1.8)
        bloco(3.5,3.2,1.2,0.6,"Enrol.\nPrincipal\n(Lm, Rm)",AZ,8.5)
        seta(4.1,3.2,5.2,3.2)

        # Chave centrífuga + enrolamento auxiliar
        ax.plot([1.6,2.8],[1.8,1.8],color=TX,lw=1.8)
        # Chave centrífuga
        ax.plot([2.8,3.0],[1.8,2.1],color=LR,lw=2.0)
        ax.plot(2.8,1.8,"o",ms=6,color=LR)
        ax.plot(3.0,2.1,"o",ms=6,color=LR)
        ax.text(2.9,1.4,"Chave\ncentrífuga",ha="center",fontsize=8,color=LR)
        bloco(3.9,1.8,1.3,0.6,"Enrol.\nAuxiliar\n(La, Ra>Rm)",LR,8.5)
        seta(4.55,1.8,5.2,1.8)

        # Motor
        ax.add_patch(mpatches.Ellipse((6.5,2.5),2.2,1.8,fc="#dce4f0",ec=TX,lw=2.0))
        ax.text(6.5,2.5,"Motor\n1φ",ha="center",va="center",fontsize=11,fontweight="bold",color=TX)

        seta(5.2,3.2,5.8,3.2); seta(5.2,1.8,5.8,1.8)

        # Reta de volta
        ax.plot([7.6,8.5],[2.5,2.5],color=TX,lw=1.8)
        ax.plot([8.5,8.5],[2.5,0.8],color=TX,lw=1.8)
        ax.plot([8.5,1.2],[0.8,0.8],color=TX,lw=1.8)
        ax.plot([1.2,1.2],[0.8,2.1],color=TX,lw=1.8)

        # Fasores de corrente
        ax.annotate("",xy=(10.5,3.5),xytext=(9.2,2.5),
            arrowprops=dict(arrowstyle="-|>",color=AZ,lw=2.2,mutation_scale=14))
        ax.text(10.6,3.5,"$I_m$",fontsize=12,color=AZ,fontweight="bold")

        ax.annotate("",xy=(10.5,2.1),xytext=(9.2,2.5),
            arrowprops=dict(arrowstyle="-|>",color=LR,lw=2.2,mutation_scale=14))
        ax.text(10.6,2.0,"$I_a$\n(adiantada)",fontsize=10,color=LR)

        ax.annotate("",xy=(9.2,2.0),xytext=(9.2,2.5),
            arrowprops=dict(arrowstyle="-",color=CZ,lw=1.0,linestyle="dashed"))
        arc = np.linspace(-math.pi/2, -math.pi/6, 20)
        ax.plot(9.2+0.4*np.cos(arc), 2.5+0.4*np.sin(arc), color=CZ, lw=1.2)
        ax.text(9.7,2.1,"α",fontsize=11,color=CZ)

        ax.set_title("Partida por Fase Dividida — Esquema e Defasagem de Correntes",
                     fontsize=11, fontweight="bold", color=TX, pad=8)
        fig.tight_layout(pad=0.3)
        return fig

    def fig_capacitor_partida():
        """Plotly: defasagem de corrente Im e Ia com capacitor vs fase dividida."""
        alpha_vals = np.linspace(10, 90, 200)  # defasagem em graus

        # Torque de partida ∝ Im * Ia * sin(alpha)
        Im = 1.0; Ia = 1.2
        T_div  = Im * Ia * np.sin(np.radians(np.clip(alpha_vals, 20, 35)))  # fase dividida ~30°
        T_cap  = Im * Ia * np.sin(np.radians(alpha_vals))                   # com capacitor

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=alpha_vals, y=T_cap/T_cap.max(), mode="lines",
            line=dict(color=AZ, width=2.8),
            name="Com capacitor (α variável)",
            hovertemplate="α=%{x:.0f}°<br>T=%{y:.3f} pu"))
        fig.add_vline(x=30, line=dict(color=LR, width=1.5, dash="dash"))
        fig.add_annotation(x=32, y=0.85, text="Fase dividida<br>(α ≈ 30°)",
            showarrow=False, font=dict(size=10, color=LR),
            bgcolor="rgba(255,255,255,0.85)")
        fig.add_vline(x=90, line=dict(color=AZ, width=1.5, dash="dot"))
        fig.add_annotation(x=88, y=0.5, text="Ideal (α=90°)",
            showarrow=False, font=dict(size=10, color=AZ),
            bgcolor="rgba(255,255,255,0.85)", xanchor="right")

        fig.update_layout(
            title=dict(text="Torque de Partida × Ângulo de Defasagem α  (T ∝ Im·Ia·sin α)",
                       font=dict(size=14, color=TX)),
            xaxis=dict(title=dict(text="Ângulo de defasagem α (°)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[5, 95],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Torque de partida (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[0, 1.08],
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
            height=380, margin=dict(l=70, r=30, t=60, b=70))
        return fig

    def fig_polo_sombreado():
        """Plotly: fluxo na parte não-sombreada vs sombreada — defasagem temporal."""
        t = np.linspace(0, 2*math.pi, 300)

        phi_ns = np.sin(t)                       # fluxo não-sombreado
        phi_s  = np.sin(t - math.radians(40))   # fluxo sombreado (atrasado ~40°)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=np.degrees(t), y=phi_ns, mode="lines",
            line=dict(color=AZ, width=2.8), name="Φ não-sombreado",
            hovertemplate="ωt=%{x:.0f}°<br>Φ=%{y:.3f} pu"))
        fig.add_trace(go.Scatter(x=np.degrees(t), y=phi_s, mode="lines",
            line=dict(color=VM, width=2.8, dash="dash"), name="Φ sombreado (atrasado)",
            hovertemplate="ωt=%{x:.0f}°<br>Φ=%{y:.3f} pu"))

        fig.add_annotation(x=130, y=0.05,
            text="← Sentido de rotação (ns → s)",
            showarrow=False, font=dict(size=11, color=VD),
            bgcolor="rgba(255,255,255,0.85)")

        fig.update_layout(
            title=dict(text="Polo Sombreado — Defasagem Temporal dos Fluxos",
                       font=dict(size=15, color=TX)),
            xaxis=dict(title=dict(text="ωt (°)", font=dict(size=14, color=TX)),
                       tickvals=[0,90,180,270,360],
                       tickfont=dict(size=12),
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Fluxo (pu)", font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[-1.15, 1.15],
                       gridcolor="rgba(128,128,128,.15)"),
            legend=dict(font=dict(size=13), bgcolor="rgba(0,0,0,0)"),
            height=380, margin=dict(l=70, r=30, t=60, b=70))
        return fig

    # ═══════════════════════════════════════════════════════════════════════════
    # CABEÇALHO
    # ═══════════════════════════════════════════════════════════════════════════
    st.title("⚙️ Motores de Baixa Potência: Indução Monofásica")
    st.caption(
        "⚡ SINTONIA · Máquinas Elétricas · "
        "👤 Marcus V A Fernandes · ✉️ marcus.fernandes@ifrn.edu.br"
    )
    st.markdown("---")

    # ── Índice ────────────────────────────────────────────────────────────────
    with st.expander("📑 Índice do Módulo", expanded=False):
        st.markdown("""
<style>
.idx-group { font-size:0.78rem; font-weight:700; color:#6b7280;
             text-transform:uppercase; letter-spacing:.07em; margin:0.9rem 0 0.25rem; }
.idx-link  { display:block; font-size:0.93rem; color:#3d8ef0; text-decoration:none;
             padding:0.18rem 0 0.18rem 0.6rem;
             border-left:2px solid rgba(61,142,240,.25); margin-bottom:0.1rem; }
.idx-link:hover { border-left-color:#3d8ef0; background:rgba(61,142,240,.06);
                  border-radius:0 4px 4px 0; }
.idx-sub   { display:block; font-size:0.84rem; color:#1a1f2b; text-decoration:none;
             padding:0.12rem 0 0.12rem 1.4rem;
             border-left:2px solid rgba(108,71,255,.18); margin-bottom:0.08rem; }
.idx-sub:hover { border-left-color:#6c47ff; background:rgba(108,71,255,.05);
                 border-radius:0 4px 4px 0; }
</style>

<div class="idx-group">Fundamentos</div>
<a class="idx-link" href="#1-conceitos-elementares-e-aplicações">1. Conceitos Elementares e Aplicações</a>
<a class="idx-link" href="#2-princípio-de-operação-campos-direto-e-oposto">2. Princípio de Operação — Campos Direto e Oposto</a>
<a class="idx-sub"  href="#2-princípio-de-operação-campos-direto-e-oposto">↳ Teoria dos campos girantes · sf e sb</a>
<a class="idx-link" href="#3-escorregamentos-direto-e-oposto">3. Escorregamentos Direto e Oposto</a>
<a class="idx-sub"  href="#3-escorregamentos-direto-e-oposto">↳ sf = (ns−n)/ns · sb = 2−sf</a>
<a class="idx-link" href="#4-circuito-equivalente">4. Circuito Equivalente</a>
<a class="idx-sub"  href="#4-circuito-equivalente">↳ Modelo Zf e Zb · Potência · Torque resultante</a>

<div class="idx-group">Métodos de Partida</div>
<a class="idx-link" href="#5-partida-por-fase-dividida">5. Partida por Fase Dividida</a>
<a class="idx-sub"  href="#5-partida-por-fase-dividida">↳ Enrolamentos principal e auxiliar · Chave centrífuga</a>
<a class="idx-link" href="#6-partida-com-capacitor">6. Partida com Capacitor</a>
<a class="idx-sub"  href="#6-partida-com-capacitor">↳ Capacitor de partida · Capacitor permanente · Cap. duplo</a>
<a class="idx-link" href="#7-motor-de-polos-sombreados">7. Motor de Polos Sombreados</a>
<a class="idx-sub"  href="#7-motor-de-polos-sombreados">↳ Anel de cobre · Defasagem de fluxo · Aplicações</a>
<a class="idx-link" href="#8-comparativo-dos-tipos">8. Comparativo dos Tipos</a>
<a class="idx-sub"  href="#8-comparativo-dos-tipos">↳ Torque · Eficiência · Custo · Aplicações típicas</a>

<div class="idx-group">Ferramentas</div>
<a class="idx-link" href="#-exploradores-interativos">🎛️ Exploradores Interativos</a>
<a class="idx-sub"  href="#-exploradores-interativos">↳ Torque vs s · Circuito equivalente · Defasagem</a>
""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 1 — Conceitos Elementares
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("1. Conceitos Elementares e Aplicações")

    st.markdown(r"""
Os **motores de baixa potência** são construídos majoritariamente para operar com
frações de 1 hp e são alimentados por redes monofásicas domésticas (127 V ou 220 V).

A quantidade de equipamentos monofásicos em operação **supera** a de motores
trifásicos, principalmente nos setores doméstico e comercial.

**Exemplos de aplicação:**
máquinas de lavar roupa, cortadores de grama, liquidificadores, processadores
de alimentos, espremedores, toca-discos, ventiladores de teto, compressores
domésticos, condicionadores de ar, bombas de piscina.

**Três tipos básicos:**

| Tipo | Princípio de partida | Faixa de potência |
|---|---|---|
| **Motor de indução** | Campo girante com enrolamento auxiliar | 1/200 hp a 1 hp |
| **Motor síncrono de relutância** | Rotor com saliências magnéticas | Pequena fração de hp |
| **Motor universal (série)** | Comutador + enrolamento em série | 1/4 a vários hp |

Este módulo aborda exclusivamente os **motores de indução monofásicos**.
""")

    show_fig(fig_estrutura_monofasico(), width_frac=0.92)
    st.caption(
        "**Figura 1.1** — Estruturas típicas: motor de indução monofásico com "
        "enrolamentos principal (M, azul) e auxiliar (A, laranja) no estator "
        "e rotor em gaiola (esquerda); motor de polos sombreados com anel de cobre "
        "na parte sombreada do polo (direita)."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 2 — Princípio de Operação
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("2. Princípio de Operação — Campos Direto e Oposto")

    st.markdown(r"""
Um enrolamento monofásico alimentado por corrente alternada produz um
**campo magnético pulsante** (não girante). Pela teoria de Ferraris,
esse campo pulsante pode ser decomposto em **dois campos girantes de mesma
amplitude, mas em sentidos opostos**:

$$\Phi(t) = \Phi_{max}\cos(\omega t) = \frac{\Phi_{max}}{2}\cos(\omega t - \theta)
+ \frac{\Phi_{max}}{2}\cos(\omega t + \theta)$$

- **Campo direto** $\Phi_f$: gira no sentido positivo (mesmo sentido da rotação do rotor)
- **Campo oposto** $\Phi_b$: gira no sentido negativo (contra-rotação)

**Consequência:** com o rotor parado ($n = 0$), os torques produzidos pelos dois
campos são **iguais e opostos** → torque resultante nulo → o motor não parte sozinho.

Entretanto, se o rotor receber um impulso externo em qualquer direção, o torque
do campo naquela direção supera o do campo oposto e o motor acelera e mantém
a rotação.

A potência instantânea do motor monofásico **pulsa com o dobro da frequência**
da rede, causando vibração e ruído maiores que nos motores trifásicos.
""")

    show_plot(fig_torque_direto_oposto(), key="fig_2_torques")
    st.caption(
        "**Figura 2.1** — Torques do campo direto $T_f$ (azul), campo oposto $T_b$ "
        "(vermelho, negativo) e torque resultante $T_{net} = T_f - T_b$ (verde). "
        "Em $s=1$ (repouso), $T_{net}=0$. Para $s<1$, $T_f > T_b$ e o motor acelera."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 3 — Escorregamentos
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("3. Escorregamentos Direto e Oposto")

    st.markdown(r"""
Assumindo que o rotor gira com velocidade $n$ rpm no sentido do campo direto
e a velocidade síncrona é $n_s$ rpm:

**Escorregamento em relação ao campo direto:**

$$s_f = \frac{n_s - n}{n_s} = s$$

**Escorregamento em relação ao campo oposto:**

$$s_b = \frac{n_s - (-n)}{n_s} = \frac{n_s + n}{n_s} = 2 - s$$

| Condição | $s_f$ | $s_b$ |
|---|---|---|
| Repouso ($n=0$) | 1 | 1 |
| Plena carga ($n \approx 0{,}95\,n_s$) | ≈ 0,05 | ≈ 1,95 |
| Síncrono ($n = n_s$) | 0 | 2 |

Como $s_b \gg s_f$ em operação normal, a frequência da corrente no rotor pelo
campo oposto é $f_{rb} = (2-s)f$ — muito maior que $f_{rf} = s \cdot f$.
Isso faz $Z_b \ll Z_f$ em plena operação, reduzindo significativamente o
torque oposto.
""")

    show_fig(fig_escorregamentos(), width_frac=0.88)
    st.caption(
        r"**Figura 3.1** — Linha de velocidades mostrando $s_f$ (azul) medido a "
        r"partir de $n_s$ e $s_b$ (vermelho) medido a partir de $-n_s$. "
        r"Em $n=0$ (repouso): $s_f = s_b = 1$."
    )

    show_plot(fig_campos_direto_oposto(), key="fig_3_correntes")
    st.caption(
        "**Figura 3.2** — Correntes $I_{2f}$ (campo direto, azul) e $I_{2b}$ "
        "(campo oposto, vermelho) em função do escorregamento $s$. "
        "À medida que o motor acelera ($s$ decresce), $I_{2f}$ cresce e $I_{2b}$ diminui."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 4 — Circuito Equivalente
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("4. Circuito Equivalente")

    st.markdown(r"""
O motor monofásico é modelado por **dois circuitos de rotor em paralelo**
(um para cada campo girante), ligados em série com a impedância do estator.

**Elementos do circuito:**

| Símbolo | Grandeza |
|---|---|
| $R_1$ | Resistência do enrolamento do estator |
| $X_1$ | Reatância de dispersão do estator |
| $X_{mag}$ | Reatância de magnetização |
| $X_2'$ | Reatância do rotor referida ao estator |
| $R_2'$ | Resistência do rotor referida ao estator |
| $Z_f = \frac{1}{2}\left(\frac{R_2'}{s} + jX_2'\right) \| jX_{mag}$ | Impedância do ramo direto |
| $Z_b = \frac{1}{2}\left(\frac{R_2'}{2-s} + jX_2'\right) \| jX_{mag}$ | Impedância do ramo oposto |

**Tensão induzida no estator:**
$$E = V_1 - I_1(R_1 + jX_1)$$

**Potência convertida** (modelo simplificado):
$$P_{conv} = I_1^2 \left[\frac{R_2'}{2}\left(\frac{1-s}{s}\right) - \frac{R_2'}{2}\left(\frac{1-s_b}{s_b}\right)\right]$$

**Perdas no cobre do rotor:**
$$P_{Cu,r} = I_1^2 \frac{R_2'}{2}\left(\frac{1}{s} - 1 + \frac{1}{s_b} - 1\right)$$
""")

    show_fig(fig_circuito_equivalente_mono(), width_frac=0.96)
    st.caption(
        "**Figura 4.1** — Circuito equivalente do motor de indução monofásico: "
        "impedâncias do estator ($R_1$, $X_1$) em série com os ramos paralelos "
        "do campo direto ($Z_f$, azul) e do campo oposto ($Z_b$, vermelho). "
        "O ramo de magnetização $X_{mag}$ é compartilhado."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 5 — Partida por Fase Dividida
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("5. Partida por Fase Dividida")

    st.markdown(r"""
O método de **fase dividida** utiliza dois enrolamentos no estator, defasados
90° mecânicos entre si:

- **Enrolamento principal** (M): baixa resistência, alta indutância → corrente $I_m$ atrasada
- **Enrolamento auxiliar** (A): alta resistência, baixa indutância → corrente $I_a$ menos atrasada

A defasagem temporal entre $I_m$ e $I_a$ cria um campo girante aproximado
suficiente para produzir torque de partida.

**Torque de partida:**
$$T_{partida} \propto I_m \cdot I_a \cdot \sin\alpha$$

onde $\alpha$ é o ângulo de defasagem entre as correntes (tipicamente 25°–35°).

**Chave centrífuga:** ao atingir ~75–80% da velocidade síncrona, a chave abre
o circuito do enrolamento auxiliar — que não foi projetado para operação contínua.

**Características:**
- Torque de partida: 100–250% do nominal
- Torque máximo: ~300% do nominal
- Potência típica: 1/20 a 1 hp
- Aplicações: ventiladores, bombas centrífugas, máquinas de lavar de baixo torque
""")

    show_fig(fig_fase_dividida(), width_frac=0.88)
    st.caption(
        "**Figura 5.1** — Esquema da partida por fase dividida: dois enrolamentos "
        "com impedâncias distintas criam defasagem α entre $I_m$ e $I_a$, "
        "gerando torque de partida. A chave centrífuga desconecta o enrolamento "
        "auxiliar após a aceleração."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 6 — Partida com Capacitor
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("6. Partida com Capacitor")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(r"""
**Capacitor de partida** (eletrolítico)

Um capacitor em série com o enrolamento auxiliar aumenta a defasagem $\alpha$
entre as correntes, podendo atingir até 90° — o ideal para um campo girante
perfeitamente circular.

- Torque de partida: **250–400%** do nominal
- Desconectado pela chave centrífuga após partida
- Capacitâncias típicas: 100–400 µF
- Aplicação: compressores, bombas, refrigeradores
""")
    with col2:
        st.markdown(r"""
**Capacitor permanente** (a óleo)

O capacitor permanece no circuito durante toda a operação, funcionando
como motor bifásico em regime.

- Melhor fator de potência e eficiência
- Menor pulsação de torque → menos ruído
- Torque de partida menor (100–200%) — limitado pela capacitância fixa
- Capacitor permanente: 4–50 µF (menor que o de partida)
- Aplicação: ventiladores, climatizadores silenciosos

**Capacitor duplo:** combina capacitor permanente ($C_r$) com capacitor de
partida ($C_s$) em paralelo, obtendo alto torque de partida e boa operação em regime.
Valores típicos (0,5 hp): $C_s = 300\,\mu F$, $C_r = 40\,\mu F$.
""")

    show_plot(fig_capacitor_partida(), key="fig_6_cap")
    st.caption(
        r"**Figura 6.1** — Torque de partida em função do ângulo de defasagem α. "
        r"A fase dividida opera com α ≈ 30° (linha vermelha); o capacitor de partida "
        r"permite α → 90°, maximizando o torque ($T \propto \sin\alpha$)."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 7 — Polos Sombreados
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("7. Motor de Polos Sombreados")

    st.markdown(r"""
O motor de polos sombreados usa uma **construção de polo saliente** no estator,
sem enrolamento auxiliar separado. Um **anel de cobre** (curto-circuitado)
envolve parte de cada polo.

**Princípio de funcionamento:**
1. O fluxo alternado do polo principal atravessa o anel de cobre
2. O anel induz uma corrente que **atrasa o fluxo** na parte sombreada
3. O fluxo da parte sombreada ($\Phi_s$) fica temporalmente atrasado em relação
   ao fluxo da parte não-sombreada ($\Phi_{ns}$)
4. O efeito combinado imita um campo girante — da parte não-sombreada **para** a sombreada

**Características:**
- Torque de partida muito baixo: 40–60% do nominal
- Eficiência e fator de potência muito baixos (25–40%)
- **Custo mais baixo** de todos os tipos (~60% relativo)
- Sem partes móveis além do rotor → alta confiabilidade
- Sentido de rotação fixo (determinado pelo posicionamento do anel)
- Potência típica: 1/200 a 1/20 hp
- Aplicações: ventiladores pequenos, secadores de cabelo, brinquedos, relógios
""")

    show_plot(fig_polo_sombreado(), key="fig_7_polo")
    st.caption(
        r"**Figura 7.1** — Fluxo da parte não-sombreada $\Phi_{ns}$ (azul) e da "
        r"parte sombreada $\Phi_s$ (vermelho tracejado). O atraso temporal de ~40° "
        r"cria o efeito de campo girante da esquerda para a direita."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 8 — Comparativo dos Tipos
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("8. Comparativo dos Tipos")

    st.markdown("""
<table style="width:100%;border-collapse:collapse;font-size:0.88rem;">
<thead><tr style="background:#f0f4ff;">
  <th style="padding:8px 10px;border:1px solid #d0d8e8;">Tipo</th>
  <th style="padding:8px 10px;border:1px solid #d0d8e8;">T_partida (%T_nom)</th>
  <th style="padding:8px 10px;border:1px solid #d0d8e8;">T_máx (%T_nom)</th>
  <th style="padding:8px 10px;border:1px solid #d0d8e8;">fp (%)</th>
  <th style="padding:8px 10px;border:1px solid #d0d8e8;">η (%)</th>
  <th style="padding:8px 10px;border:1px solid #d0d8e8;">Potência (hp)</th>
  <th style="padding:8px 10px;border:1px solid #d0d8e8;">Custo (%)</th>
  <th style="padding:8px 10px;border:1px solid #d0d8e8;">Aplicação típica</th>
</tr></thead>
<tbody>
<tr><td style="padding:6px 10px;border:1px solid #d0d8e8;font-weight:bold;color:#3d8ef0;">Fase dividida</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">100–250</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">300</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">50–65</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">55–65</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">1/20 – 1</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">100</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">Ventiladores, bombas centrífugas, máq. de lavar (baixo torque)</td></tr>
<tr style="background:#fafbff;"><td style="padding:6px 10px;border:1px solid #d0d8e8;font-weight:bold;color:#1f9d55;">Capacitor de partida</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">250–400</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">350</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">50–65</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">55–65</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">1/8 – 1</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">125</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">Compressores, bombas, refrigeradores, ar-condicionado</td></tr>
<tr><td style="padding:6px 10px;border:1px solid #d0d8e8;font-weight:bold;color:#0097a7;">Capacitor permanente</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">100–200</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">250</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">75–90</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">60–70</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">1/8 – 1</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">140</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">Ventiladores silenciosos, climatizadores, bombas</td></tr>
<tr style="background:#fafbff;"><td style="padding:6px 10px;border:1px solid #d0d8e8;font-weight:bold;color:#6c47ff;">Cap. perm. + partida</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">200–300</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">250</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">75–90</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">60–70</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">1/8 – 1</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">180</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">Compressores silenciosos, bombas de alto torque</td></tr>
<tr><td style="padding:6px 10px;border:1px solid #d0d8e8;font-weight:bold;color:#e07b00;">Polos sombreados</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">40–60</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">140</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">25–40</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">25–40</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">1/200 – 1/20</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">60</td>
    <td style="padding:6px 10px;border:1px solid #d0d8e8;">Ventiladores, secadores, brinquedos (baixíssimo torque)</td></tr>
</tbody></table>
""", unsafe_allow_html=True)

    show_plot(fig_metodos_partida(), key="fig_8_comp")
    st.caption(
        "**Figura 8.1** — Curvas T×n comparativas dos quatro tipos de motor monofásico. "
        "O capacitor de partida (azul sólido) apresenta maior torque na partida. "
        "O capacitor permanente (verde tracejado) tem melhor perfil em regime. "
        "Polos sombreados (laranja pontilhado) possuem o menor torque de partida."
    )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # EXPLORADORES INTERATIVOS
    # ═══════════════════════════════════════════════════════════════════════════
    st.header("🎛️ Exploradores Interativos")

    tab1, tab2, tab3 = st.tabs([
        "⚙️ Torque × Escorregamento",
        "📊 Defasagem de Correntes",
        "🔌 Circuito Equivalente",
    ])

    # ── Aba 1: Torque vs s ────────────────────────────────────────────────────
    with tab1:
        st.markdown(r"**Explore como os parâmetros do rotor afetam as curvas de torque.**")
        col_a, col_b = st.columns([1, 2])
        with col_a:
            R2_e = st.slider("R₂' (pu)", 0.05, 0.6, 0.20, 0.01, key="exp_m6_r2")
            X2_e = st.slider("X₂' (pu)", 0.1, 0.8, 0.30, 0.01, key="exp_m6_x2")
            Xm_e = st.slider("Xmag (pu)", 1.0, 8.0, 3.5, 0.1,  key="exp_m6_xm")
            V1_e = st.slider("V₁ (pu)",   0.5, 1.2, 1.0, 0.05, key="exp_m6_v1")

        with col_b:
            s_e  = np.linspace(0.005, 0.999, 400)
            sb_e = 2 - s_e
            ws_e = 1.0

            def T_calc(sl, R2, X2, Xm, V1, ws):
                Zr  = R2/sl + 1j*X2
                Zm  = 1j*Xm
                Z2e = Zm*Zr/(Zm+Zr)
                I1  = V1 / (1j*X2 + Z2e)
                E1  = I1 * Z2e
                I2  = E1 / Zr
                P   = abs(I2)**2 * R2*(1-sl)/sl
                return max(P/ws, 0)

            Tf_e = np.array([T_calc(si, R2_e, X2_e, Xm_e, V1_e/2, ws_e) for si in s_e])
            Tb_e = np.array([T_calc(si, R2_e, X2_e, Xm_e, V1_e/2, ws_e) for si in sb_e])
            Tn_e = Tf_e - Tb_e

            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(x=s_e, y=Tf_e, mode="lines",
                line=dict(color=AZ, width=2.0, dash="dash"), name="T_f (direto)"))
            fig_t.add_trace(go.Scatter(x=s_e, y=-Tb_e, mode="lines",
                line=dict(color=VM, width=2.0, dash="dash"), name="−T_b (oposto)"))
            fig_t.add_trace(go.Scatter(x=s_e, y=Tn_e, mode="lines",
                line=dict(color=VD, width=3.0), name="T_net"))
            fig_t.add_hline(y=0, line=dict(color=CZ, width=0.8))
            fig_t.update_layout(
                xaxis=dict(title=dict(text="Escorregamento s", font=dict(size=13, color=TX)),
                           tickfont=dict(size=11), range=[0, 1.02],
                           gridcolor="rgba(128,128,128,.15)"),
                yaxis=dict(title=dict(text="Torque (pu)", font=dict(size=13, color=TX)),
                           tickfont=dict(size=11),
                           gridcolor="rgba(128,128,128,.15)"),
                legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
                height=380, margin=dict(l=65, r=20, t=30, b=55))
            show_plot(fig_t, key="exp_m6_torque")

    # ── Aba 2: Defasagem de correntes ─────────────────────────────────────────
    with tab2:
        st.markdown(
            r"**Efeito da defasagem α entre enrolamentos principal e auxiliar** "
            r"no torque de partida $T \propto I_m \cdot I_a \cdot \sin\alpha$."
        )
        Im_e2 = st.slider("Im (pu)", 0.5, 2.0, 1.0, 0.1, key="exp_m6_Im")
        Ia_e2 = st.slider("Ia (pu)", 0.5, 2.0, 1.2, 0.1, key="exp_m6_Ia")

        alpha_e = np.linspace(0, 180, 300)
        T_e2 = Im_e2 * Ia_e2 * np.sin(np.radians(alpha_e))

        fig_a = go.Figure()
        fig_a.add_trace(go.Scatter(x=alpha_e, y=T_e2, mode="lines",
            line=dict(color=AZ, width=3.0),
            name=f"T = {Im_e2:.1f}·{Ia_e2:.1f}·sin α",
            hovertemplate="α=%{x:.0f}°<br>T=%{y:.3f} pu"))
        for x_mark, lbl, cor in [(30,"Fase dividida (~30°)",LR),
                                   (90,"Cap. partida (90°)",VD)]:
            fig_a.add_vline(x=x_mark, line=dict(color=cor, width=1.5, dash="dash"))
            fig_a.add_annotation(x=x_mark+3, y=Im_e2*Ia_e2*0.9,
                text=lbl, showarrow=False, font=dict(size=10, color=cor),
                bgcolor="rgba(255,255,255,0.85)", xanchor="left")
        fig_a.update_layout(
            xaxis=dict(title=dict(text="Defasagem α (°)", font=dict(size=13, color=TX)),
                       tickfont=dict(size=11), range=[0, 185],
                       gridcolor="rgba(128,128,128,.15)"),
            yaxis=dict(title=dict(text="Torque de partida (pu)", font=dict(size=13, color=TX)),
                       tickfont=dict(size=11),
                       gridcolor="rgba(128,128,128,.15)"),
            height=360, margin=dict(l=65, r=20, t=30, b=55))
        show_plot(fig_a, key="exp_m6_alpha")

    # ── Aba 3: Circuito Equivalente ───────────────────────────────────────────
    with tab3:
        st.markdown(
            r"**Impedâncias dos ramos direto e oposto** em função do escorregamento $s$."
        )
        col_c, col_d = st.columns([1, 2])
        with col_c:
            R2_c = st.slider("R₂' (pu)", 0.05, 0.5, 0.18, 0.01, key="exp_m6_r2c")
            X2_c = st.slider("X₂' (pu)", 0.1,  0.6, 0.25, 0.01, key="exp_m6_x2c")
            Xm_c = st.slider("Xmag (pu)", 1.0,  8.0, 3.5,  0.1,  key="exp_m6_xmc")
        with col_d:
            s_c  = np.linspace(0.01, 0.99, 300)
            sb_c = 2 - s_c

            def Z_ramo(sl, R2, X2, Xm):
                Zr = 0.5*(R2/sl + 1j*X2)
                Zm = 1j*Xm/2
                return abs(Zm*Zr/(Zm+Zr))

            Zf_c = np.array([Z_ramo(si, R2_c, X2_c, Xm_c) for si in s_c])
            Zb_c = np.array([Z_ramo(si, R2_c, X2_c, Xm_c) for si in sb_c])

            fig_z = go.Figure()
            fig_z.add_trace(go.Scatter(x=s_c, y=Zf_c, mode="lines",
                line=dict(color=AZ, width=2.8), name="|Zf| (campo direto)"))
            fig_z.add_trace(go.Scatter(x=s_c, y=Zb_c, mode="lines",
                line=dict(color=VM, width=2.8, dash="dash"), name="|Zb| (campo oposto)"))
            fig_z.update_layout(
                xaxis=dict(title=dict(text="Escorregamento s", font=dict(size=13, color=TX)),
                           tickfont=dict(size=11), range=[0, 1],
                           gridcolor="rgba(128,128,128,.15)"),
                yaxis=dict(title=dict(text="|Z| (pu)", font=dict(size=13, color=TX)),
                           tickfont=dict(size=11),
                           gridcolor="rgba(128,128,128,.15)"),
                legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
                height=360, margin=dict(l=65, r=20, t=30, b=55))
            show_plot(fig_z, key="exp_m6_Z")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════
    # REFERÊNCIAS
    # ═══════════════════════════════════════════════════════════════════════════
    with st.expander("📚 Referências Bibliográficas"):
        st.markdown("""
- CHAPMAN, S. J. *Fundamentos de Máquinas Elétricas*. São Paulo: McGraw-Hill, 5ª ed., 2013.
- KRAUSE, P.; EASYNCZUK, O.; SUDHOFF, S.; PEKAREK, S. *Analysis of Electric Machinery and Drive Systems*. IEEE Press, 3ª ed., 2013.
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
⚙️ Módulo 6 — Motores de Baixa Potência: Indução Monofásica · v1.0
</div>
""", unsafe_allow_html=True)
