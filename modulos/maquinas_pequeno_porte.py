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
        """Estrutura: seção transversal + polo sombreado."""
        fig, axes = plt.subplots(1, 2, figsize=(11, 5.5), facecolor='white')
        fig.patch.set_facecolor('white')

        # ── Painel esquerdo: seção transversal ─────────────────────────────
        ax0 = axes[0]; ax0.set_facecolor('white')
        ax0.set_aspect('equal'); ax0.axis('off')
        ax0.set_xlim(-3.8, 3.8); ax0.set_ylim(-3.8, 4.2)

        ax0.add_patch(mpatches.Wedge((0,0), 3.5, 0, 360,
            width=0.7, fc='#d0d8e8', ec=TX, lw=1.2))
        for ang, lbl, cor in [(90,'M',AZ),(270,'M',AZ)]:
            r=2.85; a=math.radians(ang)
            ax0.add_patch(mpatches.Circle((r*math.cos(a),r*math.sin(a)),
                0.38, fc=cor, ec='white', lw=1.0, zorder=4))
            ax0.text(r*math.cos(a),r*math.sin(a),lbl,ha='center',va='center',
                fontsize=8,color='white',fontweight='bold',zorder=5)
        for ang, lbl, cor in [(0,'A',LR),(180,'A',LR)]:
            r=2.85; a=math.radians(ang)
            ax0.add_patch(mpatches.Circle((r*math.cos(a),r*math.sin(a)),
                0.35, fc=cor, ec='white', lw=1.0, zorder=4))
            ax0.text(r*math.cos(a),r*math.sin(a),lbl,ha='center',va='center',
                fontsize=8,color='white',fontweight='bold',zorder=5)
        ax0.add_patch(mpatches.Wedge((0,0), 2.8, 0, 360,
            width=0.2, fc='#f0f4ff', ec=CZ, lw=0.5, alpha=0.6))
        ax0.add_patch(mpatches.Circle((0,0), 2.6, fc='#c8d8f0', ec=TX, lw=1.3))
        for a in range(0, 360, 30):
            ax0.add_patch(mpatches.Circle(
                (2.6*0.78*math.cos(math.radians(a)),
                 2.6*0.78*math.sin(math.radians(a))),
                0.16, fc=LR, ec='white', lw=0.7, alpha=0.9, zorder=4))
        ax0.add_patch(mpatches.Circle((0,0), 0.40, fc=CZ, ec=TX, lw=1.0, zorder=5))
        ax0.text(0, 3.72, 'Estator', ha='center', fontsize=9, color=TX, fontweight='bold')
        ax0.text(-3.6, 2.85, '● M: enrol. principal', fontsize=7.5, color=AZ)
        ax0.text(-3.6, 2.35, '● A: enrol. auxiliar',  fontsize=7.5, color=LR)
        ax0.text(-3.6, 1.85, '● Rotor (gaiola)',       fontsize=7.5, color='#4a6080')
        ax0.set_title('Motor de Indução Monofásico\n(seção transversal)',
                      fontsize=10, fontweight='bold', color=TX, pad=6)

        # ── Painel direito: polo sombreado ────────────────────────────────
        ax1 = axes[1]; ax1.set_facecolor('white'); ax1.axis('off')
        ax1.set_xlim(0, 10); ax1.set_ylim(0, 6)

        polo_pts = [(1.5,0.5),(1.5,5.2),(4.5,5.2),(4.5,3.8),(2.8,3.8),(2.8,0.5)]
        ax1.add_patch(plt.Polygon(polo_pts, closed=True, fc='#d0d8e8', ec=TX, lw=1.8))
        ax1.text(2.15, 2.8, 'Polo\nprincipal', ha='center', fontsize=9.5,
                 color=TX, fontweight='bold')
        for y_slot in [1.5, 2.2, 2.9, 3.5]:
            ax1.add_patch(mpatches.FancyBboxPatch((1.6, y_slot), 1.0, 0.5,
                boxstyle='round,pad=0.04', fc=AZ, ec='white', lw=0.8, alpha=0.7))
        ax1.text(2.1, 4.1, 'Enrol.\nprincipal', ha='center', fontsize=8, color=AZ)
        ax1.add_patch(mpatches.FancyBboxPatch((3.2,0.6), 1.1, 4.5,
            boxstyle='round,pad=0.08', fc='#c8a800', ec='#7a5000', lw=2.0, alpha=0.85))
        ax1.text(3.75, 3.0, 'Anel\nde Cu\n(curto)', ha='center', fontsize=8,
                 color='#4a3000', fontweight='bold')
        ax1.add_patch(mpatches.FancyBboxPatch((1.4,0.3), 3.0, 0.22,
            boxstyle='square,pad=0.0', fc='#b8c8e0', ec=TX, lw=0.8))
        ax1.add_patch(mpatches.FancyBboxPatch((0.8,-0.5), 4.0, 0.6,
            boxstyle='round,pad=0.05', fc='#c8d8f0', ec=TX, lw=1.5))
        ax1.text(2.8, -0.2, 'Rotor (gaiola)', ha='center', fontsize=9, color=TX)

        ax1.annotate('',xy=(2.0,0.53),xytext=(2.0,5.3),
            arrowprops=dict(arrowstyle='-|>',color=AZ,lw=2.2,mutation_scale=14))
        ax1.text(2.0,5.6,r'$\Phi_{ns}$',ha='center',fontsize=12,color=AZ,fontweight='bold')
        ax1.annotate('',xy=(3.75,0.53),xytext=(3.75,5.3),
            arrowprops=dict(arrowstyle='-|>',color=VM,lw=2.2,mutation_scale=14))
        ax1.text(3.75,5.6,r'$\Phi_s$',ha='center',fontsize=12,color=VM,fontweight='bold')
        ax1.annotate('',xy=(7.5,-0.2),xytext=(5.5,-0.2),
            arrowprops=dict(arrowstyle='-|>',color=VD,lw=2.5,mutation_scale=15))
        ax1.text(6.5,0.1,'Rotação',ha='center',fontsize=9.5,color=VD,fontweight='bold')
        ax1.annotate('',xy=(6.5,3.5),xytext=(6.5,5.2),
            arrowprops=dict(arrowstyle='<->',color=CZ,lw=1.5,mutation_scale=12))
        ax1.text(7.2,4.3,'defasagem\ntemporal\n~40°',ha='left',fontsize=8.5,color=CZ)
        ax1.set_title('Motor de Polos Sombreados\n(polo saliente com anel de cobre)',
                      fontsize=10, fontweight='bold', color=TX, pad=6)

        fig.suptitle('Estrutura dos Motores de Indução Monofásicos',
                     fontsize=12, fontweight='bold', color=TX, y=1.01)
        fig.tight_layout(pad=1.0)
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
        """Linha de velocidades com sf e sb."""
        fig, ax = plt.subplots(figsize=(11, 3.5), facecolor='white')
        ax.set_facecolor('white'); ax.axis('off')
        ax.set_xlim(0, 13); ax.set_ylim(0, 4.5)

        ax.annotate('',xy=(12.5,2.0),xytext=(0.5,2.0),
            arrowprops=dict(arrowstyle='-|>',color=TX,lw=1.5,mutation_scale=12))
        ax.text(12.7,2.0,'n',ha='left',va='center',fontsize=12,color=TX,fontweight='bold')

        for x, lbl, sub, cor in [
            (1.5,  r'$-n_s$',  r'$s_b=2$',         VM),
            (4.5,  r'$0$',     r'$s_f=s_b=1$',      CZ),
            (8.5,  r'$n$',     r'$0<s_f<1$',         VD),
            (11.5, r'$n_s$',   r'$s_f=0,\ s_b=2$',  AZ)]:
            ax.plot(x, 2.0, 'o', ms=10, color=cor, zorder=5)
            ax.plot([x,x],[1.6,2.0], color=cor, lw=1.2, ls='--')
            ax.text(x, 1.25, lbl, ha='center', fontsize=11, color=cor, fontweight='bold')
            ax.text(x, 0.5, sub, ha='center', fontsize=8.5, color=cor)

        ax.annotate('',xy=(11.5,3.0),xytext=(8.5,3.0),
            arrowprops=dict(arrowstyle='-|>',color=AZ,lw=2.2,mutation_scale=14))
        ax.text(10.0,3.38,r'$s_f = \dfrac{n_s - n}{n_s}$',
                ha='center',fontsize=12,color=AZ)
        ax.annotate('',xy=(1.5,3.85),xytext=(8.5,3.85),
            arrowprops=dict(arrowstyle='-|>',color=VM,lw=2.2,mutation_scale=14))
        ax.text(5.0,4.28,r'$s_b = \dfrac{n_s + n}{n_s} = 2 - s_f$',
                ha='center',fontsize=12,color=VM)

        ax.set_title(r'Escorregamentos — Campo Direto ($s_f$) e Campo Oposto ($s_b$)',
                     fontsize=11, fontweight='bold', color=TX, pad=4)
        fig.tight_layout(pad=0.3)
        return fig

    def fig_circuito_equivalente_mono():
        """Circuito equivalente monofásico com Zf e Zb."""
        fig, ax = plt.subplots(figsize=(13, 6), facecolor='white')
        ax.set_facecolor('white'); ax.axis('off')
        ax.set_xlim(0, 14); ax.set_ylim(0, 7)

        def seg(x1,y1,x2,y2,cor=TX,lw=1.8):
            ax.plot([x1,x2],[y1,y2],color=cor,lw=lw)

        def indutor(cx,cy,lbl,cor):
            ax.add_patch(mpatches.FancyBboxPatch((cx-0.45,cy-0.28),0.9,0.56,
                boxstyle='round,pad=0.08',fc='white',ec=cor,lw=1.8))
            ax.text(cx,cy,lbl,ha='center',va='center',fontsize=9,color=TX)

        def resistor(cx,cy,lbl,cor):
            ax.add_patch(mpatches.FancyBboxPatch((cx-0.55,cy-0.28),1.1,0.56,
                boxstyle='square,pad=0.05',fc='#fff8f0',ec=cor,lw=1.8))
            ax.text(cx,cy,lbl,ha='center',va='center',fontsize=9,color=TX)

        CY_TOP = 5.8; Y_BOT = 1.5; X_NOA = 5.0; X_NOB = 11.5

        # Fonte V1
        ax.add_patch(mpatches.Circle((0.9,CY_TOP),0.45,fc='white',ec=TX,lw=1.8))
        ax.text(0.9,CY_TOP,'~',ha='center',va='center',fontsize=16,color=TX)
        ax.text(0.9,CY_TOP+0.75,r'$V_1$',ha='center',fontsize=11,color=AZ,fontweight='bold')

        # R1, X1 no fio de topo
        seg(1.35,CY_TOP,2.0,CY_TOP)
        resistor(2.55,CY_TOP,r'$R_1$',TX)
        seg(3.1,CY_TOP,3.5,CY_TOP)
        indutor(4.0,CY_TOP,r'$X_1$',TX)
        seg(4.45,CY_TOP,X_NOA,CY_TOP)
        ax.plot(X_NOA,CY_TOP,'.',ms=12,color=TX,zorder=6)

        # Ramo Xmag (vertical)
        seg(X_NOA,CY_TOP,X_NOA,CY_TOP-0.9)
        indutor(X_NOA,CY_TOP-1.35,r'$X_{mag}$',CI)
        seg(X_NOA,CY_TOP-1.85,X_NOA,Y_BOT)

        # Ramo Zf (campo direto, fio superior)
        CY_ZF = 4.5
        seg(X_NOA,CY_TOP,X_NOA,CY_ZF)
        seg(X_NOA,CY_ZF,6.0,CY_ZF)
        indutor(6.65,CY_ZF,r"$\frac{1}{2}X_2'$",AZ)
        seg(7.1,CY_ZF,7.55,CY_ZF)
        resistor(8.2,CY_ZF,r"$\frac{R_2'}{2s}$",AZ)
        seg(8.75,CY_ZF,9.2,CY_ZF)
        resistor(10.1,CY_ZF,r"$\frac{R_2'(1-s)}{2s}$",VD)
        seg(11.0,CY_ZF,X_NOB,CY_ZF)
        seg(X_NOB,CY_ZF,X_NOB,Y_BOT)
        ax.text(7.2,CY_ZF+0.52,'Campo direto  $Z_f$',fontsize=9,color=AZ,fontweight='bold')
        ax.text(10.1,CY_ZF+0.52,r'$P_{conv,f}$',fontsize=8,color=VD,style='italic')

        # Ramo Zb (campo oposto, fio inferior)
        CY_ZB = 2.8
        seg(X_NOA,CY_ZB,6.0,CY_ZB)
        ax.plot(X_NOA,CY_ZB,'.',ms=8,color=TX,zorder=5)
        indutor(6.65,CY_ZB,r"$\frac{1}{2}X_2'$",VM)
        seg(7.1,CY_ZB,7.55,CY_ZB)
        resistor(8.3,CY_ZB,r"$\frac{R_2'}{2(2-s)}$",VM)
        seg(9.1,CY_ZB,9.2,CY_ZB)
        resistor(10.1,CY_ZB,r"$\frac{-R_2'(1-s_b)}{2s_b}$",LR)
        seg(11.05,CY_ZB,X_NOB,CY_ZB)
        ax.text(7.2,CY_ZB-0.55,'Campo oposto  $Z_b$',fontsize=9,color=VM,fontweight='bold')
        ax.text(10.1,CY_ZB-0.55,r'$P_{conv,b}$',fontsize=8,color=LR,style='italic')

        # Fio inferior de retorno
        seg(0.9,Y_BOT,X_NOB,Y_BOT)
        seg(0.9,CY_TOP-0.45,0.9,Y_BOT)

        # Nó B e saída
        ax.plot(X_NOB,CY_TOP,'.',ms=12,color=TX,zorder=6)
        seg(X_NOB,CY_TOP,X_NOB,CY_ZF)
        seg(X_NOB,CY_ZB,X_NOB,Y_BOT)
        ax.annotate('',xy=(X_NOB+0.9,CY_TOP),xytext=(X_NOB,CY_TOP),
            arrowprops=dict(arrowstyle='-|>',color=TX,lw=1.8,mutation_scale=13))
        ax.text(X_NOB+1.0,CY_TOP+0.22,r'$I_1$',fontsize=11,color=TX,fontweight='bold')

        # Ligação nó A → Zb
        seg(X_NOA,CY_TOP,X_NOA,CY_ZB)

        ax.set_title('Circuito Equivalente — Motor de Indução Monofásico\n'
                     r'(ramo $Z_f$: campo direto · ramo $Z_b$: campo oposto)',
                     fontsize=11, fontweight='bold', color=TX, pad=8)
        fig.tight_layout(pad=0.5)
        return fig

    def fig_metodos_partida():
        """Plotly: curvas T×n comparativas dos quatro métodos de partida."""
        s   = np.linspace(0.005, 0.999, 500)
        sb  = 2 - s
        ws  = 1.0

        R2 = 0.22; X2 = 0.28

        def T_half(sl, Xm_val):
            Zr  = (R2/sl) + 1j*X2
            Zm  = 1j*Xm_val
            Z2e = Zm*Zr/(Zm+Zr)
            # tensão induzida simplificada
            E   = 1.0 / (1.0 + Z2e/(1j*X2))
            I2  = E / Zr
            return np.maximum(abs(I2)**2 * R2*(1-sl)/sl / ws, 0)

        # Torques de partida alvo (% do máximo nominal)
        targets = {
            'Fase dividida':    0.18,
            'Cap. de partida':  0.38,
            'Cap. permanente':  0.14,
            'Polos sombreados': 0.06,
        }
        styles = {
            'Fase dividida':    dict(color=AZ, width=2.0, dash='solid'),
            'Cap. de partida':  dict(color=VD, width=2.8, dash='solid'),
            'Cap. permanente':  dict(color=CI, width=2.2, dash='dash'),
            'Polos sombreados': dict(color=LR, width=2.0, dash='dot'),
        }
        Xm_vals = {
            'Fase dividida':    3.5,
            'Cap. de partida':  4.2,
            'Cap. permanente':  3.2,
            'Polos sombreados': 2.5,
        }

        n_pct = (1-s)*100
        fig = go.Figure()

        for nome, tgt in targets.items():
            Xm_v = Xm_vals[nome]
            Tf_i = T_half(s,  Xm_v)
            Tb_i = T_half(sb, Xm_v)
            Tn_i = Tf_i - Tb_i
            # Escalar para torque de partida correto
            T_start = max(abs(float(np.interp(0.99, s, Tn_i))), 1e-6)
            scale   = tgt / T_start
            Tn_i   *= scale

            fig.add_trace(go.Scatter(
                x=n_pct, y=np.clip(Tn_i, -0.02, None), mode="lines",
                line=styles[nome], name=nome,
                hovertemplate=f"{nome}<br>n=%{{x:.1f}}% nₛ<br>T=%{{y:.3f}} pu"))

        fig.add_hline(y=0, line=dict(color=CZ, width=0.8))
        fig.add_vline(x=0,   line=dict(color=CZ, width=1.0, dash='dot'))
        fig.add_vline(x=100, line=dict(color=CZ, width=1.0, dash='dot'))

        fig.update_layout(
            title=dict(text='Curva T×n — Comparativo dos Métodos de Partida (1φ)',
                       font=dict(size=15, color=TX)),
            xaxis=dict(title=dict(text='Velocidade n/nₛ (%)', font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[-2, 103],
                       gridcolor='rgba(128,128,128,.15)'),
            yaxis=dict(title=dict(text='Torque (pu)', font=dict(size=14, color=TX)),
                       tickfont=dict(size=12), range=[-0.05, 1.15],
                       gridcolor='rgba(128,128,128,.15)'),
            legend=dict(font=dict(size=12), bgcolor='rgba(0,0,0,0)',
                        orientation='h', y=-0.25),
            height=460, margin=dict(l=70,r=30,t=60,b=110))
        return fig

    def fig_fase_dividida():
        """Esquema de ligação + diagrama fasorial da partida por fase dividida."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor='white')
        fig.patch.set_facecolor('white')

        # ── Painel esquerdo: esquema ──────────────────────────────────────
        ax0 = axes[0]; ax0.set_facecolor('white'); ax0.axis('off')
        ax0.set_xlim(0, 10); ax0.set_ylim(0, 6.5)

        def bloco0(cx,cy,w,h,txt,cor,fs=9):
            ax0.add_patch(mpatches.FancyBboxPatch((cx-w/2,cy-h/2),w,h,
                boxstyle='round,pad=0.1',fc='#f0f4ff',ec=cor,lw=2.0))
            ax0.text(cx,cy,txt,ha='center',va='center',fontsize=fs,color=TX,fontweight='bold')

        # Fonte
        ax0.add_patch(mpatches.Circle((1.2,3.5),0.48,fc='white',ec=TX,lw=1.8))
        ax0.text(1.2,3.5,'~',ha='center',va='center',fontsize=18,color=TX)
        ax0.text(1.2,4.2,r'$V_1$',ha='center',fontsize=12,color=AZ,fontweight='bold')

        # Enrol. principal (fio superior)
        ax0.plot([1.68,2.5,2.5],[4.0,4.0,4.8],color=TX,lw=1.8)
        bloco0(3.5,4.8,1.8,0.8,'Enrol. Principal\n(baixa R)',AZ)
        ax0.plot([4.4,5.5],[4.8,4.8],color=TX,lw=1.8)
        ax0.annotate('',xy=(6.5,4.8),xytext=(5.5,4.8),
            arrowprops=dict(arrowstyle='-|>',color=AZ,lw=1.8,mutation_scale=13))

        # Enrol. auxiliar (fio inferior) + chave centrífuga
        ax0.plot([1.68,2.5,2.5],[3.0,3.0,2.5],color=TX,lw=1.8)
        ax0.plot([2.5,2.75],[2.5,2.9],color=LR,lw=2.2)
        ax0.plot(2.5,2.5,'o',ms=7,color=LR); ax0.plot(2.75,2.9,'o',ms=7,color=LR)
        ax0.text(2.3,2.05,'Chave\ncentrífuga',ha='center',fontsize=7.5,color=LR)
        ax0.plot([2.5,3.0],[2.5,2.5],color=TX,lw=1.8)
        bloco0(4.0,2.5,2.0,0.8,'Enrol. Auxiliar\n(alta R)',LR)
        ax0.plot([5.0,5.5],[2.5,2.5],color=TX,lw=1.8)
        ax0.annotate('',xy=(6.5,2.5),xytext=(5.5,2.5),
            arrowprops=dict(arrowstyle='-|>',color=LR,lw=1.8,mutation_scale=13))

        # Motor
        ax0.add_patch(mpatches.Ellipse((7.8,3.65),2.4,2.0,fc='#dce4f0',ec=TX,lw=2.0))
        ax0.text(7.8,3.65,'Motor\n1φ',ha='center',va='center',
                 fontsize=11,fontweight='bold',color=TX)

        # Retorno
        ax0.plot([8.9,9.2,9.2,1.2,1.2],[3.65,3.65,1.0,1.0,3.02],color=TX,lw=1.8)
        ax0.set_title('Esquema de Ligação — Fase Dividida',
                      fontsize=10.5, fontweight='bold', color=TX, pad=5)

        # ── Painel direito: diagrama fasorial ─────────────────────────────
        ax1 = axes[1]; ax1.set_facecolor('white')
        ax1.set_aspect('equal'); ax1.axis('off')
        ax1.set_xlim(-0.3, 2.2); ax1.set_ylim(-0.85, 1.6)
        ax1.axhline(0,color=CZ,lw=0.6,ls='--',alpha=0.5)
        ax1.axvline(0,color=CZ,lw=0.6,ls='--',alpha=0.5)

        # V1 referência
        ax1.annotate('',xy=(1.2,0),xytext=(0,0),
            arrowprops=dict(arrowstyle='-|>',color=TX,lw=2.5,mutation_scale=15))
        ax1.text(0.6,0.12,r'$V_1$',ha='center',fontsize=13,color=TX,fontweight='bold')

        # Im (enrol. principal — mais atrasado ~40°)
        phi_m = -40; Im_r = math.cos(math.radians(phi_m)); Im_i = math.sin(math.radians(phi_m))
        ax1.annotate('',xy=(Im_r,Im_i),xytext=(0,0),
            arrowprops=dict(arrowstyle='-|>',color=AZ,lw=2.5,mutation_scale=15))
        ax1.text(Im_r/2+0.10,Im_i/2-0.10,r'$I_m$',ha='center',fontsize=13,
                 color=AZ,fontweight='bold')

        # Ia (enrol. auxiliar — menos atrasado ~15°)
        phi_a = -15; sc_a = 0.75
        Ia_r = sc_a*math.cos(math.radians(phi_a)); Ia_i = sc_a*math.sin(math.radians(phi_a))
        ax1.annotate('',xy=(Ia_r,Ia_i),xytext=(0,0),
            arrowprops=dict(arrowstyle='-|>',color=LR,lw=2.5,mutation_scale=15))
        ax1.text(Ia_r/2+0.12,Ia_i/2+0.08,r'$I_a$',ha='center',fontsize=13,
                 color=LR,fontweight='bold')

        # Arco α
        arc_t = np.linspace(math.radians(phi_m), math.radians(phi_a), 40)
        ax1.plot(0.38*np.cos(arc_t), 0.38*np.sin(arc_t), color=VD, lw=1.8)
        ax1.text(0.46*math.cos(math.radians((phi_m+phi_a)/2))+0.04,
                 0.46*math.sin(math.radians((phi_m+phi_a)/2)),
                 'α', ha='center', fontsize=13, color=VD, fontweight='bold')

        ax1.text(0.0,-0.72,r'$T_{part} \propto I_m \cdot I_a \cdot \sin\alpha$',
                 ha='center',fontsize=10.5,color=TX)
        ax1.set_title('Diagrama Fasorial\n(defasagem entre correntes)',
                      fontsize=10.5, fontweight='bold', color=TX, pad=5)

        fig.suptitle('Partida por Fase Dividida',
                     fontsize=12, fontweight='bold', color=TX, y=1.01)
        fig.tight_layout(pad=0.8)
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
