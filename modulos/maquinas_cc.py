"""
⚙️ Máquinas Elétricas de Corrente Contínua
Disciplina: Máquinas Elétricas
Curso: Engenharia de Energia
Instituição: IFRN — Campus Natal-Central (CNAT)
Autor: Marcus V A Fernandes · marcus.fernandes@ifrn.edu.br · v1.0

Fonte: 1º e 2º PPTX-fonte do Módulo 3 — "CEEI - MCC - 01 - Conceitos" (conceitos
elementares, estrutura construtiva, tensão na armadura, torque eletromagnético,
curva de magnetização, reação da armadura e interpolos) e "CEEI - MCC - 02 - Gerador"
(classificação dos geradores, regulação de tensão, excitação independente, shunt,
composto e série). Tópicos de motor e dinâmica de regime aguardam o 3º PPTX-fonte.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import io
import base64
import warnings


def run():

    warnings.filterwarnings("ignore")

    # ── Paleta de cores ───────────────────────────────────────────────────────
    AZ = "#3d8ef0"; RX = "#6c47ff"; VD = "#1f9d55"; LR = "#e07b00"
    CI = "#0097a7"; TX = "#1a1f2b"; CZ = "#6b7280"

    # ── CSS responsivo — injetado uma única vez ───────────────────────────────
    st.markdown("""
    <style>
    .fig-wrap {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    .fig-wrap > div {
        width: 100%;
    }
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

    # ── Helper de exibição responsivo (figuras matplotlib) ──────────────────────
    def show_fig(fig, width_frac=0.65):
        """
        Renderiza `fig` de forma responsiva:
          • Desktop (>768 px): figura centralizada com largura = width_frac × 100 %
          • Mobile  (≤768 px): figura expande para 100 % da tela automaticamente
        width_frac: 0.0–1.0
        """
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
        if height: fig.update_layout(height=height)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=TX, size=12),
            margin=dict(l=50, r=20, t=40, b=45),
            autosize=True,
        )
        fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,.18)",
                          zeroline=True, zerolinecolor="rgba(128,128,128,.35)")
        fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,.18)",
                          zeroline=True, zerolinecolor="rgba(128,128,128,.35)")
        st.plotly_chart(fig, use_container_width=True,
                         config={"displayModeBar": False, "responsive": True},
                         key=key)

    def _mpl_base(figsize=(5, 4)):
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_alpha(0); ax.set_facecolor("none")
        ax.set_aspect("equal"); ax.axis("off")
        return fig, ax

    def _zigzag(ax, x0, x1, y, n_zig=6, amp=0.18, color=TX, lw=1.4, lead_frac=0.08):
        """Linha em zigue-zague triangular (usada para bobinas/enrolamentos em corte)."""
        lead = (x1 - x0) * lead_frac
        body_x0, body_x1 = x0 + lead, x1 - lead
        n_seg = n_zig * 2
        xb = np.linspace(body_x0, body_x1, n_seg + 1)
        yb = [y]
        for k in range(1, n_seg + 1):
            yb.append(y + amp if k % 2 == 1 else y - amp)
        yb[0] = y; yb[-1] = y
        xs = [x0] + list(xb) + [x1]
        ys = [y] + yb + [y]
        ax.plot(xs, ys, color=color, lw=lw, solid_joinstyle="round", solid_capstyle="round")

    def _zigzag_v(ax, y0, y1, x, n_zig=6, amp=0.16, color=TX, lw=1.4, lead_frac=0.0):
        """Mesma ideia de _zigzag, mas na vertical (usada nos circuitos de enrolamento)."""
        lead = (y1 - y0) * lead_frac
        body_y0, body_y1 = y0 + lead, y1 - lead
        n_seg = n_zig * 2
        yb = np.linspace(body_y0, body_y1, n_seg + 1)
        xb = [x]
        for k in range(1, n_seg + 1):
            xb.append(x + amp if k % 2 == 1 else x - amp)
        xb[0] = x; xb[-1] = x
        ys = [y0] + list(yb) + [y1]
        xs = [x] + xb + [x]
        ax.plot(xs, ys, color=color, lw=lw, solid_joinstyle="round", solid_capstyle="round")

    # ════════════════════════════════════════════════════════════════════════
    # FIGURAS — ESTRUTURA CONSTRUTIVA E ENROLAMENTOS (matplotlib)
    # ════════════════════════════════════════════════════════════════════════

    def fig_secao_maquina_cc():
        """Seção transversal idealizada da máquina CC: polos principais (N/S), interpolos,
        enrolamento de campo, enrolamento de compensação, enrolamento de armadura,
        eixos d (polar) e q (interpolar)."""
        fig, ax = _mpl_base((6.6, 6.6))
        ax.set_xlim(-4.8, 4.8); ax.set_ylim(-4.8, 5.3)

        R_yoke_out, R_yoke_in = 4.3, 3.55
        R_field    = 3.05          # raio dos "dentes" de bobina de campo
        R_pole     = 2.55          # face polar / raio externo do entreferro
        R_comp     = 2.35          # enrolamento de compensação (embutido na face polar)
        R_arm      = 1.95          # enrolamento de armadura (periferia do rotor)
        R_rotor_in = 1.25          # núcleo do rotor (eixo)

        # --- Jugo do estator (anel externo) ---
        ax.add_patch(mpatches.Wedge((0, 0), R_yoke_out, 0, 360, width=R_yoke_out-R_yoke_in,
                                     fc="#1a1f2b08", ec=TX, lw=1.8, zorder=2))

        # --- Polos principais N (esquerda) e S (direita) ---
        half_pole = 68   # meia-largura angular do polo
        ax.add_patch(mpatches.Wedge((0, 0), R_yoke_in, 180-half_pole, 180+half_pole,
                                     width=R_yoke_in-R_pole, fc="#3d8ef012", ec=TX, lw=1.6, zorder=3))
        ax.add_patch(mpatches.Wedge((0, 0), R_yoke_in, -half_pole, half_pole,
                                     width=R_yoke_in-R_pole, fc="#e07b0012", ec=TX, lw=1.6, zorder=3))
        ax.text(-(R_yoke_in+R_pole)/2-0.1, 0, "N", fontsize=15, color=TX, ha="center", va="center", fontweight="bold")
        ax.text((R_yoke_in+R_pole)/2+0.1, 0, "S", fontsize=15, color=TX, ha="center", va="center", fontweight="bold")

        # --- Interpolos (topo e base, no eixo q) ---
        for sgn in (1, -1):
            iw, ih = 0.55, R_yoke_in - R_pole
            ax.add_patch(mpatches.Rectangle((-iw/2, sgn*R_pole), iw, sgn*ih if sgn>0 else -ih,
                                             fc="#6c47ff14", ec=TX, lw=1.6, zorder=4))
        ax.annotate("Interpolo", xy=(0.22, R_yoke_in-0.15), xytext=(1.7, R_yoke_out+0.55),
                    fontsize=10, color=TX, ha="left",
                    arrowprops=dict(arrowstyle="->", color=TX, lw=1.0))

        # --- Bobinas de campo (seção transversal, "dentes" triangulares) ---
        def field_coil(ang_deg, mark):
            a = np.radians(ang_deg)
            cx, cy = R_field*np.cos(a), R_field*np.sin(a)
            size = 0.5
            rad = np.array([np.cos(a), np.sin(a)])
            tan = np.array([-np.sin(a), np.cos(a)])
            p1 = np.array([cx, cy]) + rad*size*0.55
            p2 = np.array([cx, cy]) - rad*size*0.35 + tan*size*0.6
            p3 = np.array([cx, cy]) - rad*size*0.35 - tan*size*0.6
            ax.add_patch(plt.Polygon([p1, p2, p3], closed=True, fc="white", ec=AZ, lw=1.5, zorder=6))
            mx, my = np.array([cx, cy]) - rad*size*0.05
            if mark == "dot":
                ax.add_patch(plt.Circle((mx, my), 0.06, fc=AZ, ec=AZ, zorder=7))
            else:
                s = 0.07
                ax.plot([mx-s, mx+s], [my-s, my+s], color=AZ, lw=1.3, zorder=7)
                ax.plot([mx-s, mx+s], [my+s, my-s], color=AZ, lw=1.3, zorder=7)
        for ang, mark in [(45, "dot"), (135, "dot"), (225, "cross"), (315, "cross")]:
            field_coil(ang, mark)
        ax.annotate("Enrolamento de campo\n(shunt e série)", xy=(R_field*np.cos(np.radians(45))+0.1,
                    R_field*np.sin(np.radians(45))+0.1), xytext=(2.0, R_yoke_out-0.3),
                    fontsize=9.5, color=AZ, ha="left",
                    arrowprops=dict(arrowstyle="->", color=AZ, lw=1.0))

        # --- Enrolamento de compensação (face polar) ---
        n_comp = 5
        for base_ang in (180, 0):
            for off in np.linspace(-half_pole+14, half_pole-14, n_comp):
                a = np.radians(base_ang+off)
                ax.add_patch(plt.Circle((R_comp*np.cos(a), R_comp*np.sin(a)), .075,
                                         fc="white", ec=CZ, lw=1.2, zorder=6))
        ax.annotate("Enrolamento de\ncompensação", xy=(R_comp*np.cos(np.radians(20)), R_comp*np.sin(np.radians(20))),
                    xytext=(3.5, 1.55), fontsize=9.5, color=CZ, ha="left",
                    arrowprops=dict(arrowstyle="->", color=CZ, lw=1.0))

        # --- Enrolamento de armadura (periferia do rotor) ---
        n_arm = 20
        for k in range(n_arm):
            a = np.radians(k*360/n_arm)
            mark = "dot" if np.cos(a) < 0 else "cross"  # lado N: saindo; lado S: entrando (ilustrativo)
            cx, cy = R_arm*np.cos(a), R_arm*np.sin(a)
            ax.add_patch(plt.Circle((cx, cy), .085, fc="white", ec=RX, lw=1.2, zorder=6))
            if mark == "dot":
                ax.add_patch(plt.Circle((cx, cy), .028, fc=RX, ec=RX, zorder=7))
            else:
                s = 0.045
                ax.plot([cx-s, cx+s], [cy-s, cy+s], color=RX, lw=1.1, zorder=7)
                ax.plot([cx-s, cx+s], [cy+s, cy-s], color=RX, lw=1.1, zorder=7)
        ax.annotate("Enrolamento de\narmadura", xy=(R_arm*np.cos(np.radians(-20)), R_arm*np.sin(np.radians(-20))),
                    xytext=(2.3, -3.3), fontsize=9.5, color=RX, ha="left",
                    arrowprops=dict(arrowstyle="->", color=RX, lw=1.0))

        # --- Núcleo do rotor (eixo) ---
        ax.add_patch(plt.Circle((0, 0), R_rotor_in, fc="white", ec=TX, lw=1.6, zorder=5))

        # --- Eixos d (polar) e q (interpolar) ---
        ax.annotate("", xy=(R_yoke_out+0.5, 0), xytext=(-0.3, 0),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.3), zorder=8)
        ax.text(R_yoke_out+0.6, 0, "eixo d\n(eixo polar)", fontsize=9.5, color=TX, va="center")
        ax.annotate("", xy=(0, R_yoke_out+0.5), xytext=(0, -0.3),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.3), zorder=8)
        ax.text(0.15, R_yoke_out+0.55, "eixo q", fontsize=9.5, color=TX, ha="left")

        ax.set_title("Seção transversal idealizada da máquina CC", fontsize=11, color=TX, pad=22)
        fig.tight_layout(); return fig


    def fig_comutador_basico():
        """Comutador elementar de 2 segmentos: bobina única, escovas fixas B1/B2,
        polos N/S, terminais a/b."""
        fig, ax = _mpl_base((5.6, 5.6))
        ax.set_xlim(-4.2, 4.2); ax.set_ylim(-3.6, 3.4)

        R_pole_out, R_pole_in = 3.2, 2.1
        half_pole = 62
        ax.add_patch(mpatches.Wedge((0,0), R_pole_out, 180-half_pole, 180+half_pole,
                                     width=R_pole_out-R_pole_in, fc="none", ec=TX, lw=1.8, zorder=2))
        ax.add_patch(mpatches.Wedge((0,0), R_pole_out, -half_pole, half_pole,
                                     width=R_pole_out-R_pole_in, fc="none", ec=TX, lw=1.8, zorder=2))
        ax.text(-(R_pole_out+R_pole_in)/2, 0, "N", fontsize=14, color=TX, ha="center", va="center", fontweight="bold")
        ax.text((R_pole_out+R_pole_in)/2, 0, "S", fontsize=14, color=TX, ha="center", va="center", fontweight="bold")

        R_rot = 1.55
        ax.add_patch(plt.Circle((0,0), R_rot, fc="white", ec=TX, lw=1.6, zorder=3))

        # bobina (dois arcos representando os lados da bobina no rotor)
        th1 = np.linspace(np.radians(35), np.radians(150), 30)
        th2 = np.linspace(np.radians(215), np.radians(330), 30)
        r_coil = 0.95
        ax.plot(r_coil*np.cos(th1), r_coil*np.sin(th1), color=RX, lw=2.2, zorder=5)
        ax.plot(r_coil*np.cos(th2), r_coil*np.sin(th2), color=RX, lw=2.2, zorder=5)
        ax.add_patch(plt.Circle((0,0), 0.12, fc=TX, ec=TX, zorder=6))

        # comutador (2 segmentos) - pequeno anel central
        R_com = 0.45
        for k, lbl, dx in [(0, "$C_a$", 0.05), (1, "$C_b$", -0.05)]:
            a0 = np.radians(90+180*k)
            a1 = np.radians(270+180*k)
        ax.add_patch(mpatches.Wedge((0,0), R_com, 70, 250, width=R_com-0.18, fc="white", ec=TX, lw=1.3, zorder=7))
        ax.add_patch(mpatches.Wedge((0,0), R_com, 250, 70+360, width=R_com-0.18, fc="white", ec=TX, lw=1.3, zorder=7))
        ax.text(0, R_com-0.09, "$C_a$", fontsize=9, color=TX, ha="center", va="center", zorder=8)
        ax.text(0, -(R_com-0.09), "$C_b$", fontsize=9, color=TX, ha="center", va="center", zorder=8)

        # escovas B1 (esquerda) e B2 (direita), fixas, hachuradas
        bw, bh = 0.3, 0.85
        ax.add_patch(mpatches.Rectangle((-R_pole_in, -bh/2), bw, bh, fc=LR, ec=TX, lw=1.2,
                                         hatch="//", alpha=.85, zorder=4))
        ax.add_patch(mpatches.Rectangle((R_pole_in-bw, -bh/2), bw, bh, fc=LR, ec=TX, lw=1.2,
                                         hatch="//", alpha=.85, zorder=4))
        ax.text(-R_pole_in-0.15, -bh/2-0.25, "$B_1$", fontsize=11, color=TX, ha="center")
        ax.text(R_pole_in+0.15, -bh/2-0.25, "$B_2$", fontsize=11, color=TX, ha="center")

        # terminais a (+) e b (-)
        a_pt = r_coil*np.array([np.cos(np.radians(150)), np.sin(np.radians(150))])
        b_pt = r_coil*np.array([np.cos(np.radians(330)), np.sin(np.radians(330))])
        ext_a = a_pt*1.55
        ext_b = b_pt*1.55
        ax.plot([a_pt[0], ext_a[0]], [a_pt[1], ext_a[1]], color=RX, lw=1.3, zorder=5)
        ax.plot([b_pt[0], ext_b[0]], [b_pt[1], ext_b[1]], color=RX, lw=1.3, zorder=5)
        ax.add_patch(plt.Circle(ext_a, .07, fc="white", ec=RX, lw=1.3, zorder=6))
        ax.add_patch(plt.Circle(ext_b, .07, fc="white", ec=RX, lw=1.3, zorder=6))
        ax.text(ext_a[0]-0.15, ext_a[1]+0.25, "a", fontsize=11, color=TX, ha="center")
        ax.text(ext_a[0]-0.15, ext_a[1]+0.45, "+", fontsize=11, color=TX, ha="center")
        ax.text(ext_b[0]+0.15, ext_b[1]-0.25, "b", fontsize=11, color=TX, ha="center")
        ax.text(ext_b[0]+0.15, ext_b[1]-0.45, "$-$", fontsize=11, color=TX, ha="center")

        # rotacao n
        arc_n = np.linspace(np.radians(110), np.radians(70), 20)
        r_n = R_rot+0.35
        ax.plot(r_n*np.cos(arc_n), r_n*np.sin(arc_n), color=TX, lw=1.4, zorder=6)
        ax.annotate("", xy=(r_n*np.cos(arc_n[0]), r_n*np.sin(arc_n[0])),
                    xytext=(r_n*np.cos(arc_n[2]), r_n*np.sin(arc_n[2])),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.4), zorder=6)
        ax.text(0, r_n+0.22, "n", fontsize=10.5, color=TX, ha="center")

        ax.text(0, -3.35, r"$+\;\;e_{12}\;\;-$", fontsize=10.5, color=TX, ha="center")
        ax.plot([-bw/2-R_pole_in+0.15, -bw/2-R_pole_in+0.15], [-bh/2-0.55, -2.9], color=TX, lw=1, zorder=2)
        ax.plot([R_pole_in-bw/2-0.15, R_pole_in-bw/2-0.15], [-bh/2-0.55, -2.9], color=TX, lw=1, zorder=2)
        ax.plot([-bw/2-R_pole_in+0.15, R_pole_in-bw/2-0.15], [-2.9,-2.9], color=TX, lw=1, zorder=2)

        ax.set_title("Comutador elementar (2 segmentos)", fontsize=10.5, color=TX, pad=10)
        fig.tight_layout(); return fig


    def _trapezoid(theta, period=360, flat=90, rise=30, amp=1.0, phase=0):
        """Onda trapezoidal periódica (em graus), amplitude +-amp."""
        t = (theta - phase) % period
        half = period/2
        out = np.zeros_like(t)
        # subida 0->flat (positivo)
        m1 = t < rise
        out[m1] = amp * (t[m1]/rise)
        m2 = (t >= rise) & (t < rise+flat)
        out[m2] = amp
        m3 = (t >= rise+flat) & (t < 2*rise+flat)
        out[m3] = amp * (1 - (t[m3]-(rise+flat))/rise)
        m4 = (t >= 2*rise+flat) & (t < half)
        out[m4] = 0
        m5 = (t >= half) & (t < half+rise)
        out[m5] = -amp * (t[m5]-half)/rise
        m6 = (t >= half+rise) & (t < half+rise+flat)
        out[m6] = -amp
        m7 = (t >= half+rise+flat) & (t < half+2*rise+flat)
        out[m7] = -amp*(1-(t[m7]-(half+rise+flat))/rise)
        m8 = t >= half+2*rise+flat
        out[m8] = 0
        return out

    def fig_forma_onda_comutacao_simples():
        """e_ab (tensão induzida na bobina, alternada) e e_12 (tensão nos terminais,
        já comutada/retificada) — caso de uma única bobina."""
        fig, axes = plt.subplots(2, 1, figsize=(7.4, 5.2), sharex=True)
        fig.patch.set_alpha(0)
        theta = np.linspace(0, 720, 1200)

        eab = _trapezoid(theta, period=360, flat=90, rise=30, amp=1.0)
        ax = axes[0]
        ax.set_facecolor("none")
        ax.plot(theta, eab, color=AZ, lw=2.2)
        ax.axhline(0, color=TX, lw=1)
        ax.set_ylabel("$e_{ab}$", fontsize=11, color=TX, rotation=0, labelpad=18)
        ax.set_yticks([]); ax.set_xticks([])
        for s in ax.spines.values(): s.set_visible(False)
        ax.set_ylim(-1.35, 1.35)
        ax.annotate("", xy=(745,0), xytext=(0,0), arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.1))
        ax.text(750, 0, r"$\theta$", fontsize=11, color=TX, va="center")

        e12 = np.abs(eab)
        # pequenos "entalhes" de comutação: forçar a zero perto de theta=0,180,360,...
        notch_w = 8
        for center in [0, 180, 360, 540, 720]:
            mask = np.abs(((theta-center+180)%360)-180) < notch_w
            e12 = np.where(mask, e12*np.abs(((theta-center+180)%360-180)/notch_w), e12)
        ax2 = axes[1]
        ax2.set_facecolor("none")
        ax2.plot(theta, e12, color=RX, lw=2.2)
        ax2.axhline(np.mean(e12), color=CZ, lw=1.2, ls="--")
        ax2.text(620, np.mean(e12)+0.12, r"$E_{12}\,$(méd.)", fontsize=9.5, color=CZ)
        ax2.set_ylabel("$e_{12}$", fontsize=11, color=TX, rotation=0, labelpad=18)
        ax2.set_yticks([]); ax2.set_xticks([])
        for s in ax2.spines.values(): s.set_visible(False)
        ax2.set_ylim(-0.15, 1.35)
        ax2.axhline(0, color=TX, lw=1)
        ax2.annotate("", xy=(745,0), xytext=(0,0), arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.1))
        ax2.text(750, 0, r"$\theta$", fontsize=11, color=TX, va="center")

        fig.suptitle("Tensão de uma bobina (a) e tensão comutada nos terminais (b)", fontsize=10.5, color=TX, y=0.98)
        fig.tight_layout()
        return fig

    def fig_forma_onda_comutacao_multipla(n_coils=8):
        """e_12 com múltiplos segmentos de comutador: soma de n bobinas defasadas
        (aproximação senoidal retificada) — ondulação decresce conforme n cresce."""
        fig, ax = plt.subplots(figsize=(7.6, 3.0))
        fig.patch.set_alpha(0); ax.set_facecolor("none")
        theta = np.linspace(0, 720, 2000)
        rad = np.radians(theta)
        delta = np.pi / n_coils
        total = np.zeros_like(rad)
        for k in range(n_coils):
            comp = np.abs(np.cos(rad - k*delta))
            ax.plot(theta, comp*0.62, color=CZ, lw=0.8, alpha=.45, ls="--", zorder=2)
            total += comp
        total /= n_coils
        ax.plot(theta, total, color=RX, lw=2.4, zorder=5)
        ax.axhline(total.mean(), color=TX, lw=1, ls=":", zorder=3)
        ax.set_ylim(-0.05, 1.05); ax.set_yticks([]); ax.set_xticks([])
        for s in ax.spines.values(): s.set_visible(False)
        ax.axhline(0, color=TX, lw=1)
        ax.annotate("", xy=(745,0), xytext=(0,0), arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.1))
        ax.text(752, 0, r"$\theta$", fontsize=11, color=TX, va="center")
        ax.text(-25, total.mean(), "$e_{12}$", fontsize=11, color=TX, ha="right", va="center")
        ax.set_title(f"Tensão comutada com {n_coils} segmentos — ondulação reduzida", fontsize=10.5, color=TX, pad=10)
        fig.tight_layout()
        return fig


    def fig_volta_bobina_enrolamento():
        """Hierarquia volta -> bobina -> enrolamento: diamantes concêntricos."""
        fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.6))
        fig.patch.set_alpha(0)

        def diamond(ax, cx, n_turns, color, leads=True, lbl=None):
            for i in range(n_turns):
                w = 0.55 - i*0.07
                h = 1.25 - i*0.10
                pts = [(cx, h), (cx+w, h*0.45), (cx+w*0.18, -h), (cx-w*0.18, -h), (cx-w, h*0.45)]
                pts2 = [(cx, h), (cx+w, h*0.45), (cx+w*0.18, -h)]
                top = (cx, h)
                ax.plot([top[0], cx+w, cx+w*0.22, cx-w*0.22, cx-w, top[0]],
                        [top[1], h*0.45, -h, -h, h*0.45, top[1]], color=color, lw=1.8, zorder=3-i*0.01)
            if leads:
                ax.plot([cx, cx], [1.25, 1.55], color=color, lw=1.8)
                ax.plot([cx-0.18, cx-0.05], [-1.15, -1.45], color=color, lw=1.8)
                ax.plot([cx+0.22, cx+0.05], [-1.15, -1.45], color=color, lw=1.8)
                ax.add_patch(plt.Circle((cx-0.05,-1.5), .05, fc="white", ec=color, lw=1.4, zorder=5))
                ax.add_patch(plt.Circle((cx+0.05,-1.5), .05, fc="white", ec=color, lw=1.4, zorder=5))
            if lbl:
                ax.text(cx, -1.85, lbl, fontsize=9, color=TX, ha="center")

        titles = ["Volta (turn)", "Bobina (coil)", "Enrolamento (winding)"]
        for ax, title in zip(axes, titles):
            ax.set_facecolor("none"); ax.axis("off"); ax.set_aspect("equal")
            ax.set_xlim(-2.3, 2.3); ax.set_ylim(-2.2, 2.0)
            ax.set_title(title, fontsize=11, color=TX, pad=8)

        diamond(axes[0], 0, 1, AZ, lbl="1 condutor (ida + volta)")
        diamond(axes[1], 0, 3, AZ, lbl="N voltas em série")

        ax3 = axes[2]
        centers = [-1.5, 0, 1.5]
        for j, cx in enumerate(centers):
            diamond(ax3, cx, 3, AZ, leads=False)
            ax3.plot([cx, cx], [1.25, 1.55], color=AZ, lw=1.6)
            ax3.plot([cx-0.18, cx-0.05], [-1.15, -1.45], color=AZ, lw=1.6)
            ax3.plot([cx+0.22, cx+0.05], [-1.15, -1.45], color=AZ, lw=1.6)
            ax3.text(cx-0.05, -1.62, f"$S_{j+1}$", fontsize=8, color=TX, ha="center")
            ax3.text(cx+0.05, -1.62, f"$F_{j+1}$", fontsize=8, color=TX, ha="right" if False else "left")
        for j in range(len(centers)-1):
            ax3.plot([centers[j]+0.05, centers[j+1]-0.05], [-1.5, -1.5], color=TX, lw=1.3)
        ax3.plot([centers[0]-0.05, centers[0]-0.05],[-1.5,-1.65], color=AZ, lw=1.6)
        ax3.add_patch(plt.Circle((centers[0]-0.05,-1.5), .045, fc="white", ec=AZ, lw=1.3, zorder=5))
        ax3.add_patch(plt.Circle((centers[-1]+0.05,-1.5), .045, fc="white", ec=AZ, lw=1.3, zorder=5))
        ax3.text((centers[0]+centers[-1])/2, -2.0, "bobinas conectadas em série", fontsize=9, color=TX, ha="center")

        fig.tight_layout()
        return fig


    def fig_enrolamento_lap(p=4):
        """Enrolamento imbricado (lap): representação em anel com p escovas/caminhos
        e circuito equivalente com a=p caminhos paralelos."""
        fig, axes = plt.subplots(1, 2, figsize=(8.6, 4.0))
        fig.patch.set_alpha(0)

        # --- (esquerda) anel com p escovas ---
        ax = axes[0]; ax.set_facecolor("none"); ax.axis("off"); ax.set_aspect("equal")
        ax.set_xlim(-1.8,1.8); ax.set_ylim(-1.8,1.8)
        R = 1.0
        n_coil = 16
        th = np.linspace(0, 2*np.pi, n_coil*2+1)
        rr = R + 0.13*np.array([1 if i%2==0 else -1 for i in range(len(th))])
        ax.plot(rr*np.cos(th), rr*np.sin(th), color=RX, lw=1.8, zorder=3)
        for k in range(p):
            a = np.pi/2 - k*2*np.pi/p
            bx, by = (R+0.22)*np.cos(a), (R+0.22)*np.sin(a)
            ax.add_patch(mpatches.Rectangle((bx-0.1, by-0.1), 0.2, 0.2, angle=np.degrees(a)-90,
                                             fc=LR, ec=TX, lw=1.0, zorder=4))
            sign = "+" if k % 2 == 0 else "$-$"
            ax.text(bx*1.32, by*1.32, sign, fontsize=12, color=TX, ha="center", va="center")
        ax.set_title(f"Enrolamento imbricado (lap)\n$p={p}$ escovas, $a=p={p}$ caminhos", fontsize=10, color=TX)

        # --- (direita) circuito equivalente: p ramos em paralelo ---
        ax2 = axes[1]; ax2.set_facecolor("none"); ax2.axis("off")
        ax2.set_xlim(-0.6, p+0.6); ax2.set_ylim(-0.4, 3.2)
        ytop, ybot = 2.7, 0.3
        ax2.plot([0, p], [ytop, ytop], color=TX, lw=1.6)
        ax2.plot([0, p], [ybot, ybot], color=TX, lw=1.6)
        for k in range(p):
            x = 0.5 + k
            n_zig = 3
            amp = 0.13
            ys = np.linspace(ybot+0.25, ytop-0.25, n_zig*2+1)
            xs = [x + (amp if i%2 else -amp) for i in range(len(ys))]
            xs[0] = x; xs[-1] = x
            ax2.plot([x,x],[ytop, ytop-0.25], color=TX, lw=1.4)
            ax2.plot(xs, ys, color=RX, lw=1.6)
            ax2.plot([x,x],[ybot+0.25, ybot], color=TX, lw=1.4)
        ax2.add_patch(plt.Circle((0,ytop), .055, fc="white", ec=TX, lw=1.3, zorder=5))
        ax2.add_patch(plt.Circle((0,ybot), .055, fc="white", ec=TX, lw=1.3, zorder=5))
        ax2.text(-0.35, ytop, "+", fontsize=13, color=TX, ha="center", va="center")
        ax2.text(-0.35, ybot, "$-$", fontsize=13, color=TX, ha="center", va="center")
        ax2.text(p/2, ytop+0.35, "$I_a$", fontsize=11, color=TX, ha="center")
        ax2.annotate("", xy=(p*0.5-0.6, ytop+0.05), xytext=(p*0.5+0.6, ytop+0.05),
                     arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.1))
        ax2.text(0.5, ybot-0.3, "$I_{coil}=I_a/a$", fontsize=9.5, color=RX, ha="center")
        ax2.set_title(f"Circuito equivalente\n($a={p}$ caminhos em paralelo)", fontsize=10, color=TX)

        fig.tight_layout()
        return fig


    def fig_enrolamento_wave():
        """Enrolamento ondulado (wave): representação em anel com 2 escovas
        e circuito equivalente com a=2 caminhos (série longa por polo)."""
        fig, axes = plt.subplots(1, 2, figsize=(8.6, 4.0))
        fig.patch.set_alpha(0)

        ax = axes[0]; ax.set_facecolor("none"); ax.axis("off"); ax.set_aspect("equal")
        ax.set_xlim(-1.8,1.8); ax.set_ylim(-1.8,1.8)
        R = 1.0
        n_coil = 16
        th = np.linspace(0, 2*np.pi, n_coil*2+1)
        rr = R + 0.13*np.array([1 if i%2==0 else -1 for i in range(len(th))])
        ax.plot(rr*np.cos(th), rr*np.sin(th), color=VD, lw=1.8, zorder=3)
        for k in range(2):
            a = np.pi/2 - k*np.pi
            bx, by = (R+0.22)*np.cos(a), (R+0.22)*np.sin(a)
            ax.add_patch(mpatches.Rectangle((bx-0.1, by-0.1), 0.2, 0.2, angle=np.degrees(a)-90,
                                             fc=LR, ec=TX, lw=1.0, zorder=4))
            sign = "+" if k == 0 else "$-$"
            ax.text(bx*1.32, by*1.32, sign, fontsize=12, color=TX, ha="center", va="center")
        ax.set_title("Enrolamento ondulado (wave)\n2 escovas, $a=2$ (independe de $p$)", fontsize=10, color=TX)

        ax2 = axes[1]; ax2.set_facecolor("none"); ax2.axis("off")
        ax2.set_xlim(-0.7, 2.7); ax2.set_ylim(-0.4, 3.2)
        ytop, ybot = 2.7, 0.3
        x = 1.0
        n_zig = 9
        amp = 0.16
        ys = np.linspace(ybot, ytop, n_zig*2+1)
        xs = [x + (amp if i%2 else -amp) for i in range(len(ys))]
        xs[0] = x; xs[-1] = x
        ax2.plot(xs, ys, color=VD, lw=1.8)
        ax2.add_patch(plt.Circle((x,ytop), .055, fc="white", ec=TX, lw=1.3, zorder=5))
        ax2.add_patch(plt.Circle((x,ybot), .055, fc="white", ec=TX, lw=1.3, zorder=5))
        ax2.text(x-0.35, ytop, "+", fontsize=13, color=TX, ha="center", va="center")
        ax2.text(x-0.35, ybot, "$-$", fontsize=13, color=TX, ha="center", va="center")
        ax2.text(x+0.45, ytop, "$I_a$", fontsize=11, color=TX, ha="center")
        ax2.annotate("", xy=(x+0.35, ytop-0.05), xytext=(x+0.05, ytop-0.05),
                     arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.1))
        ax2.text(x, ybot-0.3, "$I_{coil}=I_a/2$", fontsize=9.5, color=VD, ha="center")
        ax2.set_title("Circuito equivalente\n($a=2$ caminhos, muitas bobinas em série)", fontsize=10, color=TX)

        fig.tight_layout()
        return fig


    def fig_polos_4p():
        """Seção transversal com 4 polos alternados N-S-N-S e ângulo θ."""
        fig, ax = _mpl_base((3.6, 3.6))
        ax.set_xlim(-2.4, 2.4); ax.set_ylim(-2.4, 2.4)
        R_out, R_in = 1.9, 1.15
        half = 38
        labels = ["N", "S", "N", "S"]
        for k in range(4):
            center = 90 - k*90
            ax.add_patch(mpatches.Wedge((0,0), R_out, center-half, center+half,
                                         width=R_out-R_in, fc="#3d8ef015" if labels[k]=="N" else "#e07b0015",
                                         ec=TX, lw=1.5, zorder=2))
            a = np.radians(center)
            ax.text((R_out+R_in)/2*np.cos(a), (R_out+R_in)/2*np.sin(a), labels[k],
                    fontsize=12, color=TX, ha="center", va="center", fontweight="bold")
        ax.add_patch(plt.Circle((0,0), R_in, fc="white", ec=TX, lw=1.4, zorder=3))
        ax.add_patch(plt.Circle((0,0), 0.07, fc=TX, ec=TX, zorder=4))
        arc = np.linspace(np.radians(90), np.radians(58), 20)
        ax.plot(0.65*np.cos(arc), 0.65*np.sin(arc), color=LR, lw=1.5, zorder=4)
        ax.annotate("", xy=(0.85*np.cos(np.radians(58)), 0.85*np.sin(np.radians(58))),
                    xytext=(0,0), arrowprops=dict(arrowstyle="-", color=LR, lw=1.3), zorder=4)
        ax.text(0.55*np.cos(np.radians(74)), 0.55*np.sin(np.radians(74))+0.12, r"$\theta$",
                color=LR, fontsize=12)
        ax.set_title("Máquina de 4 polos ($p=4$)", fontsize=10.5, color=TX, pad=8)
        fig.tight_layout(); return fig


    def fig_curva_Btheta(p=4):
        """B(θ) trapezoidal ao longo do entreferro — eixo elétrico (θ_ed) e mecânico (θ_md)."""
        fig, ax = plt.subplots(figsize=(7.2, 3.6))
        fig.patch.set_alpha(0); ax.set_facecolor("none")

        theta_ed = np.linspace(0, 4*np.pi, 1200)
        r = 0.30*np.pi    # largura angular da rampa (fração do passo polar)
        t = theta_ed % (2*np.pi)
        B = np.zeros_like(t)
        m1 = t < r;                          B[m1] = t[m1]/r
        m2 = (t>=r)&(t<np.pi-r);             B[m2] = 1
        m3 = (t>=np.pi-r)&(t<np.pi+r);       B[m3] = 1 - (t[m3]-(np.pi-r))/r
        m4 = (t>=np.pi+r)&(t<2*np.pi-r);     B[m4] = -1
        m5 = t>=2*np.pi-r;                   B[m5] = -1 + (t[m5]-(2*np.pi-r))/r

        ax.plot(theta_ed, B, color=AZ, lw=2.2)
        ax.axhline(0, color=TX, lw=1)
        ax.text(np.pi*0.5, 1.18, "N", fontsize=11, color=TX, ha="center")
        ax.text(np.pi*1.5, -1.18, "S", fontsize=11, color=TX, ha="center")
        ax.text(np.pi*2.5, 1.18, "N", fontsize=11, color=TX, ha="center")
        ax.text(np.pi*3.5, -1.18, "S", fontsize=11, color=TX, ha="center")

        ax.annotate("", xy=(np.pi, 1.45), xytext=(0, 1.45), arrowprops=dict(arrowstyle="<->", color=CZ, lw=1.1))
        ax.text(np.pi/2, 1.55, "passo polar", fontsize=8.5, color=CZ, ha="center")

        xt = [0, np.pi, 2*np.pi, 3*np.pi, 4*np.pi]
        ax.set_xticks(xt); ax.set_xticklabels(["0","$\\pi$","$2\\pi$","$3\\pi$","$4\\pi$"])
        ax.set_yticks([])
        ax2 = ax.secondary_xaxis(-0.38)
        ax2.set_xticks([0, 2*np.pi, 4*np.pi])
        ax2.set_xticklabels(["0","$\\pi$","$2\\pi$"])
        ax2.set_xlabel(r"$\theta_{md}$ (mecânico)", fontsize=9.5, color=TX)
        ax.set_xlabel(r"$\theta_{ed}$ (elétrico)", fontsize=9.5, color=TX, labelpad=6)
        for s in ["top","right","left"]: ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(TX)
        ax.tick_params(colors=TX)
        ax.set_ylim(-1.7, 1.8)
        ax.set_title(r"$B(\theta)$ — distribuição da densidade de fluxo (p=4)   $\Rightarrow\;\theta_{ed}=\dfrac{p}{2}\theta_{md}$",
                     fontsize=10.5, color=TX, pad=10)
        fig.tight_layout()
        return fig


    def fig_condutor_campo(modo="tensao"):
        """Condutor de comprimento l em campo B (entrando na página).
        modo='tensao': mostra v->e (regra da mão direita, gerador)
        modo='forca':  mostra i->f (regra da mão direita, força de Laplace, motor)"""
        fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.6), gridspec_kw={'width_ratios':[1.3,1]})
        fig.patch.set_alpha(0)

        ax = axes[0]; ax.set_facecolor("none"); ax.axis("off"); ax.set_aspect("equal")
        ax.set_xlim(-2.6, 3.0); ax.set_ylim(-2.0, 2.0)
        for xq in (-1.7,-0.85,0.85,1.7):
            for yq in (1.15,0.4,-0.4,-1.15):
                ax.plot(xq, yq, marker='x', color=TX, ms=7, mew=1.6, zorder=2)
        ax.add_patch(mpatches.Rectangle((-0.07,-1.35), 0.14, 2.7, fc=AZ if modo=="tensao" else LR,
                                         ec=TX, lw=1.2, zorder=4))
        ax.annotate("", xy=(0,1.55), xytext=(0,-1.55), arrowprops=dict(arrowstyle="<->", color=TX, lw=1.0), zorder=1)
        ax.text(-0.32, 0, "$l$", fontsize=12, color=TX, ha="center")
        if modo == "tensao":
            ax.annotate("", xy=(2.0,0), xytext=(0.12,0), arrowprops=dict(arrowstyle="-|>", color=VD, lw=2.0), zorder=5)
            ax.text(1.1, 0.28, "$v$", fontsize=12, color=VD, ha="center")
            ax.text(0.12, 1.55, "$+$", fontsize=12, color=TX, ha="center")
            ax.text(0.12, 1.30, "$e$", fontsize=11, color=TX, ha="center")
            ax.text(0.12, -1.6, "$-$", fontsize=12, color=TX, ha="center")
        else:
            ax.text(0.12, 1.55, "$+$", fontsize=12, color=TX, ha="center")
            ax.text(0.12, 1.30, "$i$", fontsize=11, color=TX, ha="center")
            ax.text(0.12, -1.6, "$-$", fontsize=12, color=TX, ha="center")
            ax.annotate("", xy=(2.0,0), xytext=(0.12,0), arrowprops=dict(arrowstyle="-|>", color=LR, lw=2.0), zorder=5)
            ax.text(1.1, 0.28, "$f$", fontsize=12, color=LR, ha="center")
        ax.text(2.55, -1.75, "$B$", fontsize=12, color=TX, ha="center")
        ax.text(0, 1.9, "$\\times$ indica $B$ entrando na página", fontsize=8.5, color=CZ, ha="center")

        ax2 = axes[1]; ax2.set_facecolor("none"); ax2.axis("off")
        ax2.set_xlim(-0.3, 3.0); ax2.set_ylim(-0.3, 2.6)
        ax2.annotate("", xy=(0,2.5), xytext=(0,0), arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.2))
        ax2.annotate("", xy=(2.8,0), xytext=(0,0), arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.2))
        xs = np.linspace(0,2.3,10)
        color = VD if modo=="tensao" else LR
        ax2.plot(xs, xs*0.95, color=color, lw=2.0, ls="--")
        ax2.text(2.45, 2.25, "$B$", fontsize=11, color=TX)
        if modo=="tensao":
            ax2.text(-0.18, 2.55, "$+$\n$e$", fontsize=11, color=TX, ha="center", va="top")
            ax2.text(2.95, -0.05, "$v$", fontsize=11, color=TX)
        else:
            ax2.text(-0.18, 2.55, "$+$\n$f$", fontsize=11, color=TX, ha="center", va="top")
            ax2.text(2.95, -0.05, "$i$", fontsize=11, color=TX)

        fig.tight_layout()
        return fig


    def fig_curva_magnetizacao():
        """Curva de magnetização E_a vs F_p para duas velocidades (saturação)."""
        fig, ax = plt.subplots(figsize=(6.4, 4.6))
        fig.patch.set_alpha(0); ax.set_facecolor("none")

        Fp = np.linspace(0, 10, 300)
        def sat(x, k, knee=4.0, p=1.6):
            lin = k*x
            s = lin / (1 + (lin/ (k*knee))**p)**(1/p)
            return s

        E_full = sat(Fp, k=1.0)
        E_half = 0.5*E_full

        ax.plot(Fp, E_full, color=AZ, lw=2.4, label=r"Velocidade $\omega_m$")
        ax.plot(Fp, E_half, color=CI, lw=2.4, label=r"Velocidade $\omega_m/2$")
        ax.text(Fp[-1]*0.78, E_full[-1]*0.97+0.15, r"Velocidade, $\omega_m$", fontsize=10, color=AZ)
        ax.text(Fp[-1]*0.80, E_half[-1]*0.80, r"$\dfrac{\omega_m}{2}$", fontsize=12, color=CI)

        ax.set_xlim(0, 10.3); ax.set_ylim(0, max(E_full)*1.18)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ["top","right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.annotate("", xy=(10.5,0), xytext=(0,0), arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.3))
        ax.annotate("", xy=(0,max(E_full)*1.25), xytext=(0,0), arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.3))
        ax.text(10.65, -0.15*max(E_full)*0+(-0.25), "$F_p$", fontsize=12, color=TX, ha="left")
        ax.text(-0.3, max(E_full)*1.28, "$E_a$", fontsize=12, color=TX, ha="center")

        ax.set_title("Curva de magnetização — saturação magnética", fontsize=11, color=TX, pad=12)
        fig.tight_layout()
        return fig


    def fig_reacao_armadura():
        """Reação da armadura: campo principal B_f (horizontal, N->S) distorcido pelo
        campo da própria armadura B_a (loops em torno dos condutores)."""
        fig, ax = _mpl_base((6.6, 4.2))
        ax.set_xlim(-4.6, 4.6); ax.set_ylim(-2.6, 2.6)

        # --- linhas de campo principal B_f, N (esq) -> S (dir) ---
        for y in np.linspace(-2.1, 2.1, 7):
            ax.annotate("", xy=(-2.6, y), xytext=(-4.3, y),
                        arrowprops=dict(arrowstyle="->", color=AZ, lw=1.3, alpha=.8))
            ax.annotate("", xy=(4.3, y), xytext=(2.6, y),
                        arrowprops=dict(arrowstyle="->", color=AZ, lw=1.3, alpha=.8))
        ax.text(-3.9, 2.35, "$B_f$", color=AZ, fontsize=11)

        # --- rotor com 2 grupos de condutores (loops de fluxo da armadura) ---
        R = 1.55
        ax.add_patch(plt.Circle((0,0), R, fc="white", ec=TX, lw=1.6, zorder=5))
        for cx, mark, color in [(-0.95, "dot", RX), (0.95, "cross", RX)]:
            for rr, alpha in [(0.55,1.0),(0.95,0.7),(1.35,0.45)]:
                ell = mpatches.Ellipse((cx,0), rr*1.7, rr*2.1, fc="none", ec=color, lw=1.3, alpha=alpha, zorder=3)
                ax.add_patch(ell)
            if mark=="dot":
                ax.add_patch(plt.Circle((cx,0), .09, fc=color, ec=color, zorder=6))
            else:
                s=.12
                ax.plot([cx-s,cx+s],[-s,s], color=color, lw=1.8, zorder=6)
                ax.plot([cx-s,cx+s],[s,-s], color=color, lw=1.8, zorder=6)
        ax.text(0, 1.85, "$B_a$", color=RX, fontsize=11, ha="center")

        # marcadores de condutores ao redor do rotor
        n=16
        for k in range(n):
            a = 2*np.pi*k/n
            mark = "dot" if np.cos(a) > 0.15 else ("cross" if np.cos(a) < -0.15 else None)
            if mark is None: continue
            cx, cy = R*0.92*np.cos(a), R*0.92*np.sin(a)
            if mark=="dot":
                ax.add_patch(plt.Circle((cx,cy), .055, fc="white", ec=TX, lw=1.0, zorder=7))
                ax.add_patch(plt.Circle((cx,cy), .02, fc=TX, ec=TX, zorder=8))
            else:
                ax.add_patch(plt.Circle((cx,cy), .055, fc="white", ec=TX, lw=1.0, zorder=7))
                s=.032
                ax.plot([cx-s,cx+s],[cy-s,cy+s], color=TX, lw=0.9, zorder=8)
                ax.plot([cx-s,cx+s],[cy+s,cy-s], color=TX, lw=0.9, zorder=8)

        ax.text(-4.3, -2.4, "N", fontsize=13, color=AZ, fontweight="bold")
        ax.text(4.0, -2.4, "S", fontsize=13, color=AZ, fontweight="bold")
        ax.set_title("Reação da armadura — distorção do campo principal", fontsize=10.5, color=TX, pad=10)
        fig.tight_layout(); return fig


    def fig_interpolos():
        """Interpolos: polo auxiliar no eixo q, em série com a armadura,
        com fluxo Phi_i opondo-se ao fluxo de reação Phi_a."""
        fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.4), gridspec_kw={'width_ratios':[1.3,1]})
        fig.patch.set_alpha(0)

        # --- esquerda: seção transversal com interpolo ---
        ax = axes[0]; ax.set_facecolor("none"); ax.axis("off"); ax.set_aspect("equal")
        ax.set_xlim(-3.0, 3.0); ax.set_ylim(-3.0, 3.2)
        R_out, R_in = 2.5, 1.7
        half = 62
        ax.add_patch(mpatches.Wedge((0,0), R_out, 180-half, 180+half, width=R_out-R_in,
                                     fc="#3d8ef012", ec=TX, lw=1.6, zorder=2))
        ax.add_patch(mpatches.Wedge((0,0), R_out, -half, half, width=R_out-R_in,
                                     fc="#e07b0012", ec=TX, lw=1.6, zorder=2))
        ax.text(-(R_out+R_in)/2, 0, "N", fontsize=13, color=TX, ha="center", va="center", fontweight="bold")
        ax.text((R_out+R_in)/2, 0, "S", fontsize=13, color=TX, ha="center", va="center", fontweight="bold")

        iw, ih = 0.5, R_in-1.0
        ax.add_patch(mpatches.Rectangle((-iw/2, 1.0), iw, ih, fc="#6c47ff18", ec=TX, lw=1.5, zorder=3))
        ax.annotate("Interpolo", xy=(0.2, 1.0+ih*0.6), xytext=(1.3, R_out+0.5),
                    fontsize=10, color=TX, ha="left", arrowprops=dict(arrowstyle="->", color=TX, lw=1.0))

        R_rot = 0.95
        ax.add_patch(plt.Circle((0,0), R_rot, fc="white", ec=TX, lw=1.5, zorder=4))
        ax.add_patch(mpatches.Rectangle((-0.13,R_rot-0.06), 0.26, 0.12, fc=LR, ec=TX, lw=1.0, zorder=5, hatch="//"))
        ax.add_patch(mpatches.Rectangle((-0.13,-R_rot-0.06), 0.26, 0.12, fc=LR, ec=TX, lw=1.0, zorder=5, hatch="//"))
        n=14
        for k in range(n):
            a = 2*np.pi*k/n
            cx, cy = R_rot*0.8*np.cos(a), R_rot*0.8*np.sin(a)
            mark = "dot" if np.cos(a) > 0 else "cross"
            ax.add_patch(plt.Circle((cx,cy), .065, fc="white", ec=RX, lw=1.0, zorder=6))
            if mark=="dot":
                ax.add_patch(plt.Circle((cx,cy), .024, fc=RX, ec=RX, zorder=7))
            else:
                s=.035
                ax.plot([cx-s,cx+s],[cy-s,cy+s], color=RX, lw=1.1, zorder=7)
                ax.plot([cx-s,cx+s],[cy+s,cy-s], color=RX, lw=1.1, zorder=7)

        ax.annotate("", xy=(0.45, R_in+0.05), xytext=(0.45, R_rot+0.15),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.4))
        ax.text(0.6, (R_in+R_rot)/2+0.1, "$I_a$", fontsize=10, color=TX)
        ax.annotate("", xy=(2.85,2.0), xytext=(2.85,2.7), arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.3))
        ax.text(3.0, 2.35, "$\\Phi_i$", fontsize=10.5, color=TX, va="center")
        ax.annotate("", xy=(2.85,1.0), xytext=(2.85,0.3), arrowprops=dict(arrowstyle="-|>", color=RX, lw=1.3))
        ax.text(3.0, 0.65, "$\\Phi_a$", fontsize=10.5, color=RX, va="center")
        ax.set_title("Polo auxiliar (interpolo) no eixo q", fontsize=10.5, color=TX, pad=10)

        # --- direita: enrolamento em série ---
        ax2 = axes[1]; ax2.set_facecolor("none"); ax2.axis("off")
        ax2.set_xlim(-1.0, 1.6); ax2.set_ylim(-0.3, 3.75)
        x = 0
        ytop, ymid, ybot = 3.0, 1.65, 0.3
        n_zig = 4; amp=.16
        ys1 = np.linspace(ymid+0.25, ytop-0.25, n_zig*2+1)
        xs1 = [x+(amp if i%2 else -amp) for i in range(len(ys1))]; xs1[0]=x; xs1[-1]=x
        ax2.plot([x,x],[ytop,ytop-0.25], color=TX, lw=1.3)
        ax2.plot(xs1, ys1, color=TX, lw=1.8)
        ax2.plot([x,x],[ymid+0.25,ymid], color=TX, lw=1.3)
        ax2.text(0.45, (ymid+ytop)/2, "Interpolo", fontsize=9.5, color=TX, ha="left", va="center")
        ax2.annotate("", xy=(0.95,(ymid+ytop)/2-0.05), xytext=(0.95,(ymid+ytop)/2+0.35),
                     arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.0))
        ax2.text(1.15,(ymid+ytop)/2+0.15, "$\\Phi_i$", fontsize=9.5, color=TX, va="center")

        n_zig2 = 5
        ys2 = np.linspace(ybot+0.25, ymid-0.25, n_zig2*2+1)
        xs2 = [x+(amp if i%2 else -amp) for i in range(len(ys2))]; xs2[0]=x; xs2[-1]=x
        ax2.plot([x,x],[ymid,ymid-0.25], color=RX, lw=1.3)
        ax2.plot(xs2, ys2, color=RX, lw=1.8)
        ax2.plot([x,x],[ybot+0.25,ybot], color=RX, lw=1.3)
        ax2.text(0.45,(ybot+ymid)/2, "Armadura", fontsize=9.5, color=RX, ha="left", va="center")
        ax2.annotate("", xy=(0.95,(ybot+ymid)/2+0.35), xytext=(0.95,(ybot+ymid)/2-0.05),
                     arrowprops=dict(arrowstyle="-|>", color=RX, lw=1.0))
        ax2.text(1.15,(ybot+ymid)/2+0.15, "$\\Phi_a$", fontsize=9.5, color=RX, va="center")

        ax2.add_patch(plt.Circle((x,ytop), .055, fc="white", ec=TX, lw=1.3, zorder=5))
        ax2.add_patch(plt.Circle((x,ybot), .055, fc="white", ec=TX, lw=1.3, zorder=5))
        ax2.annotate("", xy=(x-0.05,ytop+0.35), xytext=(x-0.05,ytop+0.05),
                     arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.1))
        ax2.text(x-0.15, ytop+0.45, "$I_a$", fontsize=10, color=TX, ha="center")
        ax2.text(x, -0.15, r"$\Phi_a,\,\Phi_i$ opõem-se, independente do sentido de $I_a$",
                  fontsize=8.7, color=TX, ha="center")
        ax2.set_title("Enrolamento do interpolo em série\ncom a armadura", fontsize=10.5, color=TX, pad=18)

        fig.tight_layout()
        return fig

    # ════════════════════════════════════════════════════════════════════════
    # FIGURAS — OPERAÇÃO COMO GERADOR (matplotlib)
    # ════════════════════════════════════════════════════════════════════════

    def fig_classificacao_geradores():
        """5 esquemas de conexão do campo: independente, shunt, série, composto
        curto e composto longo."""
        fig, axes = plt.subplots(1, 5, figsize=(13.5, 3.4))
        fig.patch.set_alpha(0)

        def armature(ax, cx, cy, r=0.34):
            ax.add_patch(plt.Circle((cx, cy), r, fc="white", ec=TX, lw=1.6, zorder=5))
            ax.text(cx, cy, "$E_a$", fontsize=9, color=TX, ha="center", va="center", zorder=6)
            return cx, cy, r

        def rheostat(ax, x0, x1, y, color=AZ):
            _zigzag(ax, x0, x1, y, n_zig=3, amp=0.1, color=color, lw=1.4)
            mx = (x0+x1)/2
            ax.annotate("", xy=(mx+0.18, y+0.22), xytext=(mx-0.18, y-0.18),
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2), zorder=6)

        # ---- (a) Independente ----
        ax = axes[0]; ax.set_facecolor("none"); ax.axis("off"); ax.set_aspect("equal")
        ax.set_xlim(-0.3, 2.6); ax.set_ylim(-1.6, 1.6)
        cx, cy, r = armature(ax, 1.6, 0)
        ax.plot([cx, cx], [cy+r, 1.3], color=TX, lw=1.4); ax.plot([cx-0.05,cx+0.05],[1.3,1.3],color=TX,lw=0)
        ax.add_patch(plt.Circle((cx,1.35),.05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(cx+0.15,1.35,"+",fontsize=10,color=TX, va="center")
        ax.plot([cx, cx], [cy-r, -1.3], color=TX, lw=1.4)
        ax.add_patch(plt.Circle((cx,-1.35),.05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(cx+0.15,-1.35,"$-$",fontsize=10,color=TX, va="center")
        # campo separado, à esquerda
        ax.plot([0.1,0.1],[-0.55,0.55], color=AZ, lw=1.4)
        _zigzag_v(ax, -0.2, 0.2, 0.1, n_zig=3, amp=0.1, color=AZ, lw=1.4)
        rheostat(ax, -0.05, 0.25, 0.55, color=AZ)
        ax.add_patch(plt.Circle((0.1,-0.55),.05, fc="white", ec=AZ, lw=1.2, zorder=6))
        ax.add_patch(plt.Circle((0.1,0.85),.05, fc="white", ec=AZ, lw=1.2, zorder=6))
        ax.plot([0.1,0.1],[0.55,0.85], color=AZ, lw=1.4)
        ax.set_title("(a) Independente", fontsize=9.5, color=TX, pad=6)

        # ---- (b) Shunt (paralelo) ----
        ax = axes[1]; ax.set_facecolor("none"); ax.axis("off"); ax.set_aspect("equal")
        ax.set_xlim(-0.3, 2.6); ax.set_ylim(-1.6, 1.6)
        cx, cy, r = armature(ax, 1.0, 0)
        ax.plot([cx,cx],[cy+r,1.3], color=TX, lw=1.4)
        ax.plot([cx,cx],[cy-r,-1.3], color=TX, lw=1.4)
        ax.plot([cx,2.3],[1.3,1.3], color=TX, lw=1.4)
        ax.plot([cx,2.3],[-1.3,-1.3], color=TX, lw=1.4)
        ax.add_patch(plt.Circle((2.3,1.3),.05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.add_patch(plt.Circle((2.3,-1.3),.05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(2.45,1.3,"+",fontsize=10,color=TX, va="center")
        ax.text(2.45,-1.3,"$-$",fontsize=10,color=TX, va="center")
        fx = 0.25
        ax.plot([fx,cx],[1.3,1.3], color=AZ, lw=1.4)
        ax.plot([fx,cx],[-1.3,-1.3], color=AZ, lw=1.4)
        _zigzag_v(ax, -0.6, 0.4, fx, n_zig=4, amp=0.1, color=AZ, lw=1.4)
        rheostat(ax, fx-0.15, fx+0.15, 0.8, color=AZ)
        ax.plot([fx,fx],[0.4,0.65], color=AZ, lw=1.4); ax.plot([fx,fx],[0.95,1.3], color=AZ, lw=1.4)
        ax.plot([fx,fx],[-1.3,-0.6], color=AZ, lw=1.4)
        ax.set_title("(b) Shunt (paralelo)", fontsize=9.5, color=TX, pad=6)

        # ---- (c) Série ----
        ax = axes[2]; ax.set_facecolor("none"); ax.axis("off"); ax.set_aspect("equal")
        ax.set_xlim(-0.3, 2.6); ax.set_ylim(-1.6, 1.6)
        cx, cy, r = armature(ax, 0.6, 0)
        ax.plot([cx,cx],[cy+r,1.3], color=TX, lw=1.4)
        ax.plot([cx,cx],[cy-r,-1.3], color=TX, lw=1.4)
        ax.plot([cx,1.3],[1.3,1.3], color=TX, lw=1.4)
        _zigzag(ax, 1.3, 2.0, 1.3, n_zig=3, amp=0.1, color=VD, lw=1.5)
        ax.plot([2.0,2.3],[1.3,1.3], color=TX, lw=1.4)
        ax.plot([cx,2.3],[-1.3,-1.3], color=TX, lw=1.4)
        ax.add_patch(plt.Circle((2.3,1.3),.05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.add_patch(plt.Circle((2.3,-1.3),.05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(2.45,1.3,"+",fontsize=10,color=TX, va="center")
        ax.text(2.45,-1.3,"$-$",fontsize=10,color=TX, va="center")
        ax.set_title("(c) Série", fontsize=9.5, color=TX, pad=6)

        # ---- (d) Composto curto (short shunt) ----
        ax = axes[3]; ax.set_facecolor("none"); ax.axis("off"); ax.set_aspect("equal")
        ax.set_xlim(-0.3, 2.7); ax.set_ylim(-1.6, 1.6)
        cx, cy, r = armature(ax, 0.6, 0)
        ax.plot([cx,cx],[cy+r,1.3], color=TX, lw=1.4)
        ax.plot([cx,cx],[cy-r,-1.3], color=TX, lw=1.4)
        nodex = 1.0
        ax.plot([cx,nodex],[1.3,1.3], color=TX, lw=1.4)
        ax.add_patch(plt.Circle((nodex,1.3), .035, fc=TX, ec=TX, zorder=7))
        _zigzag(ax, nodex+0.3, nodex+1.0, 1.3, n_zig=3, amp=0.1, color=VD, lw=1.5)
        ax.plot([nodex,nodex+0.3],[1.3,1.3], color=TX, lw=1.4)
        ax.plot([nodex+1.0,2.4],[1.3,1.3], color=TX, lw=1.4)
        ax.plot([cx,2.4],[-1.3,-1.3], color=TX, lw=1.4)
        ax.add_patch(plt.Circle((2.4,1.3),.05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.add_patch(plt.Circle((2.4,-1.3),.05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(2.55,1.3,"+",fontsize=9,color=TX, va="center")
        ax.text(2.55,-1.3,"$-$",fontsize=9,color=TX, va="center")
        fx = nodex
        _zigzag_v(ax, -0.6, 0.4, fx, n_zig=4, amp=0.1, color=AZ, lw=1.4)
        rheostat(ax, fx-0.15, fx+0.15, 0.8, color=AZ)
        ax.plot([fx,fx],[0.4,0.65], color=AZ, lw=1.4); ax.plot([fx,fx],[0.95,1.3], color=AZ, lw=1.4)
        ax.plot([fx,fx],[-1.3,-0.6], color=AZ, lw=1.4)
        ax.set_title("(d) Composto curto", fontsize=9.5, color=TX, pad=6)

        # ---- (e) Composto longo (long shunt) ----
        ax = axes[4]; ax.set_facecolor("none"); ax.axis("off"); ax.set_aspect("equal")
        ax.set_xlim(-0.3, 2.7); ax.set_ylim(-1.6, 1.6)
        cx, cy, r = armature(ax, 0.6, 0)
        ax.plot([cx,cx],[cy+r,1.3], color=TX, lw=1.4)
        ax.plot([cx,cx],[cy-r,-1.3], color=TX, lw=1.4)
        _zigzag(ax, cx+0.3, cx+1.0, 1.3, n_zig=3, amp=0.1, color=VD, lw=1.5)
        ax.plot([cx,cx+0.3],[1.3,1.3], color=TX, lw=1.4)
        nodex = cx+1.0
        ax.plot([nodex,2.4],[1.3,1.3], color=TX, lw=1.4)
        ax.add_patch(plt.Circle((nodex,1.3), .035, fc=TX, ec=TX, zorder=7))
        ax.plot([cx,2.4],[-1.3,-1.3], color=TX, lw=1.4)
        ax.add_patch(plt.Circle((2.4,1.3),.05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.add_patch(plt.Circle((2.4,-1.3),.05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(2.55,1.3,"+",fontsize=9,color=TX, va="center")
        ax.text(2.55,-1.3,"$-$",fontsize=9,color=TX, va="center")
        fx = nodex
        _zigzag_v(ax, -0.6, 0.4, fx, n_zig=4, amp=0.1, color=AZ, lw=1.4)
        rheostat(ax, fx-0.15, fx+0.15, 0.8, color=AZ)
        ax.plot([fx,fx],[0.4,0.65], color=AZ, lw=1.4); ax.plot([fx,fx],[0.95,1.3], color=AZ, lw=1.4)
        ax.plot([fx,fx],[-1.3,-0.6], color=AZ, lw=1.4)
        ax.set_title("(e) Composto longo", fontsize=9.5, color=TX, pad=6)

        fig.tight_layout()
        return fig


    def fig_gerador_independente_circuito():
        """Circuito do gerador CC de excitação independente: malha de campo (Vf, Rfc, Rfw)
        e malha de armadura (Ea, Ra) alimentando a carga RL."""
        fig, ax = _mpl_base((7.2, 4.0))
        ax.set_xlim(-0.5, 9.4); ax.set_ylim(-2.3, 2.3)

        # --- malha de campo (esquerda) ---
        fx0 = 0.0
        ax.plot([fx0, fx0], [-1.0, 0.0], color=AZ, lw=1.5)
        _zigzag_v(ax, 0.0, 0.9, fx0, n_zig=3, amp=0.12, color=AZ, lw=1.5)
        ax.text(fx0-0.35, 0.45, "$R_{fc}$", fontsize=9.5, color=AZ, ha="center")
        ax.plot([fx0, fx0+1.0], [0.9, 0.9], color=AZ, lw=1.5)
        _zigzag(ax, fx0+1.0, fx0+2.0, 0.9, n_zig=3, amp=0.12, color=AZ, lw=1.5)
        ax.text(fx0+1.5, 1.18, "$R_{fw}$", fontsize=9.5, color=AZ, ha="center")
        ax.plot([fx0+2.0, fx0+2.4], [0.9, 0.9], color=AZ, lw=1.5)
        ax.plot([fx0+2.4, fx0+2.4], [0.9, -1.0], color=AZ, lw=1.5)
        ax.plot([fx0+2.4, fx0], [-1.0, -1.0], color=AZ, lw=1.5)
        ax.add_patch(plt.Circle((fx0, -1.0), .045, fc="white", ec=AZ, lw=1.2, zorder=6))
        ax.text(fx0-0.25, -1.0, "+", fontsize=10, color=AZ, va="center")
        ax.text(fx0-0.55, -1.0, "$V_f$", fontsize=9.5, color=AZ, va="center")
        ax.annotate("", xy=(fx0+0.45, -0.55), xytext=(fx0+0.05, -0.95),
                    arrowprops=dict(arrowstyle="-|>", color=AZ, lw=1.1))
        ax.text(fx0+0.65, -0.6, "$I_f$", fontsize=9.5, color=AZ)

        # --- malha de armadura (centro) ---
        ax0 = 3.6
        ax.add_patch(plt.Circle((ax0, 0), 0.5, fc="white", ec=TX, lw=1.7, zorder=5))
        ax.text(ax0, 0, "$E_a$", fontsize=11, color=TX, ha="center", va="center", zorder=6)
        ax.annotate("", xy=(ax0-0.75, -0.6), xytext=(ax0-0.4, -0.35),
                    arrowprops=dict(arrowstyle="-|>", color=CZ, lw=1.1))
        ax.text(ax0-1.0, -0.7, "$\\omega_m$", fontsize=9.5, color=CZ)
        ax.plot([ax0, ax0], [0.5, 1.3], color=TX, lw=1.5)
        _zigzag_v(ax, 1.3, 2.0, ax0, n_zig=3, amp=0.12, color=TX, lw=1.5)
        ax.text(ax0+0.32, 1.65, "$R_a$", fontsize=9.5, color=TX)
        ax.plot([ax0, ax0+1.6], [2.0, 2.0], color=TX, lw=1.5)
        ax.annotate("", xy=(ax0+0.9, 2.0), xytext=(ax0+0.5, 2.0),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.1))
        ax.text(ax0+0.7, 2.18, "$I_a$", fontsize=9.5, color=TX, ha="center")
        ax.plot([ax0, ax0], [-0.5, -2.0], color=TX, lw=1.5)
        ax.plot([ax0, ax0+5.0], [-2.0, -2.0], color=TX, lw=1.5)
        ax.text(ax0+0.15, 0.65, "+", fontsize=10, color=TX)
        ax.text(ax0+0.15, -0.65, "$-$", fontsize=10, color=TX)

        # --- terminais / carga (direita) ---
        tx = ax0+1.6
        ax.add_patch(plt.Circle((tx, 2.0), .05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(tx+0.18, 2.0, "+", fontsize=10, color=TX, va="center")
        ax.text(tx-0.35, 2.25, "$I_t$", fontsize=9.5, color=TX)
        ax.annotate("", xy=(tx+0.05, 2.0), xytext=(tx-0.35, 2.0),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.0))
        ax.text(ax0+2.5, 0, "$V_t$", fontsize=10.5, color=TX, ha="center")
        lx = ax0+5.0
        ax.plot([lx, lx], [-2.0, 2.0], color=LR, lw=1.5)
        _zigzag_v(ax, -1.4, 1.4, lx, n_zig=5, amp=0.13, color=LR, lw=1.5)
        ax.plot([tx, lx], [2.0, 2.0], color=TX, lw=1.5)
        ax.text(lx+0.3, 0, "$R_L$", fontsize=9.5, color=LR, va="center")
        ax.add_patch(plt.Circle((tx, -2.0), .05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(tx+0.18, -2.0, "$-$", fontsize=10, color=TX, va="center")

        fig.tight_layout()
        return fig


    def fig_caracteristica_terminal():
        """Curva característica terminal Vt x It: queda IaRa, efeito da reação de armadura
        e ponto de operação com a reta de carga."""
        fig, ax = plt.subplots(figsize=(6.6, 4.4))
        fig.patch.set_alpha(0); ax.set_facecolor("none")

        It = np.linspace(0, 120, 200)
        Ea = 100 - 0.03*It                      # leve queda por reação de armadura na FEM
        Vt_no_ar = 100 - 0.18*It                  # reta: só queda IaRa
        Vt_ar = 100 - 0.18*It - 0.0028*It**2      # com reação de armadura (achatamento)

        ax.plot(It, np.full_like(It, 100), color=CZ, lw=1.3, ls=":")
        ax.plot(It, Ea, color=AZ, lw=2.0, ls="--", label="$E_a$ (com reação de armadura)")
        ax.plot(It, Vt_no_ar, color=CZ, lw=1.8, ls="-.", label="Terminal sem reação de armadura")
        ax.plot(It, Vt_ar, color=RX, lw=2.6, label="Terminal com reação de armadura")

        RL_slope = 0.65
        load = RL_slope*It
        ax.plot(It, load, color=LR, lw=1.8, label="Reta de carga ($R_L$)")

        # ponto de operação (interseção aproximada)
        idx = np.argmin(np.abs(Vt_ar-load))
        ax.plot(It[idx], Vt_ar[idx], marker="o", color=TX, ms=7, zorder=6)
        ax.annotate("Ponto de\noperação", xy=(It[idx], Vt_ar[idx]), xytext=(It[idx]+12, Vt_ar[idx]-18),
                    fontsize=9, color=TX, arrowprops=dict(arrowstyle="->", color=TX, lw=1.0))

        ax.annotate("", xy=(60, Ea[np.argmin(np.abs(It-60))]), xytext=(60, Vt_no_ar[np.argmin(np.abs(It-60))]),
                    arrowprops=dict(arrowstyle="<->", color=TX, lw=1.0))
        ax.text(62, (Ea[np.argmin(np.abs(It-60))]+Vt_no_ar[np.argmin(np.abs(It-60))])/2, "$I_aR_a$",
                fontsize=9, color=TX)

        ax.set_xlim(0, 120); ax.set_ylim(0, 110)
        ax.set_xlabel("$I_t$ (% corrente nominal)", fontsize=10, color=TX)
        ax.set_ylabel("$V_t$ (% tensão nominal)", fontsize=10, color=TX)
        ax.legend(fontsize=8, loc="lower left", frameon=False)
        for s in ["top","right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.tick_params(colors=TX, labelsize=8)
        ax.set_title("Característica terminal — excitação independente", fontsize=10.5, color=TX, pad=10)
        fig.tight_layout()
        return fig


    def fig_gerador_shunt_circuito():
        """Circuito do gerador CC shunt (autoexcitado): campo conectado em paralelo
        com a própria armadura."""
        fig, ax = _mpl_base((6.6, 4.0))
        ax.set_xlim(-1.0, 7.4); ax.set_ylim(-2.3, 2.3)

        ax0 = 2.0
        ax.add_patch(plt.Circle((ax0, 0), 0.5, fc="white", ec=TX, lw=1.7, zorder=5))
        ax.text(ax0, 0, "$E_a$", fontsize=11, color=TX, ha="center", va="center", zorder=6)
        ax.annotate("", xy=(ax0-0.75, -0.6), xytext=(ax0-0.4, -0.35),
                    arrowprops=dict(arrowstyle="-|>", color=CZ, lw=1.1))
        ax.text(ax0-1.0, -0.7, "$\\omega_m$", fontsize=9.5, color=CZ)
        ax.plot([ax0, ax0], [0.5, 1.3], color=TX, lw=1.5)
        _zigzag_v(ax, 1.3, 2.0, ax0, n_zig=3, amp=0.12, color=TX, lw=1.5)
        ax.text(ax0+0.32, 1.65, "$R_a$", fontsize=9.5, color=TX)
        ax.plot([ax0, ax0], [-0.5, -2.0], color=TX, lw=1.5)
        nodex = ax0
        ax.plot([nodex, nodex+3.6], [2.0, 2.0], color=TX, lw=1.5)
        ax.plot([nodex, nodex+3.6], [-2.0, -2.0], color=TX, lw=1.5)
        ax.annotate("", xy=(ax0+0.9, 2.0), xytext=(ax0+0.5, 2.0),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.1))
        ax.text(ax0+0.7, 2.2, "$I_a$", fontsize=9.5, color=TX, ha="center")
        ax.text(ax0+0.15, 0.65, "+", fontsize=10, color=TX)
        ax.text(ax0+0.15, -0.65, "$-$", fontsize=10, color=TX)

        # campo (shunt), entre a armadura e os terminais
        fx = ax0 + 1.3
        ax.add_patch(plt.Circle((fx, 2.0), .035, fc=TX, ec=TX, zorder=7))
        ax.add_patch(plt.Circle((fx, -2.0), .035, fc=TX, ec=TX, zorder=7))
        _zigzag_v(ax, -1.2, 0.3, fx, n_zig=4, amp=0.12, color=AZ, lw=1.5)
        mx = fx
        ax.annotate("", xy=(mx+0.22, 0.75), xytext=(mx-0.18, 0.35),
                    arrowprops=dict(arrowstyle="-|>", color=AZ, lw=1.2))
        ax.plot([fx, fx], [0.3, 0.55], color=AZ, lw=1.5)
        _zigzag_v(ax, 0.55, 1.0, fx, n_zig=2, amp=0.1, color=AZ, lw=1.5)
        ax.plot([fx, fx], [1.0, 2.0], color=AZ, lw=1.5)
        ax.plot([fx, fx], [-2.0, -1.2], color=AZ, lw=1.5)
        ax.annotate("", xy=(fx-0.45, 1.55), xytext=(fx-0.05, 1.85),
                    arrowprops=dict(arrowstyle="-|>", color=AZ, lw=1.1))
        ax.text(fx-0.75, 1.5, "$I_f$", fontsize=9.5, color=AZ)
        ax.text(fx+0.3, -0.4, "$R_{fc}{+}R_{fw}$", fontsize=8.5, color=AZ, rotation=90, va="center")

        # terminais / carga
        tx = nodex+3.6
        ax.add_patch(plt.Circle((tx, 2.0), .05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.add_patch(plt.Circle((tx, -2.0), .05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(tx+0.18, 2.0, "+", fontsize=10, color=TX, va="center")
        ax.text(tx+0.18, -2.0, "$-$", fontsize=10, color=TX, va="center")
        ax.text((fx+tx)/2, 0, "$V_t$", fontsize=10.5, color=TX, ha="center")
        ax.annotate("", xy=(fx+0.7, 2.0), xytext=(fx+0.3, 2.0),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.0))
        ax.text(fx+0.5, 2.2, "$I_t$", fontsize=9, color=TX, ha="center")

        fig.tight_layout()
        return fig


    def fig_autoexcitacao(Rf_slope=1.0, show_buildup=True):
        """Curva de autoexcitação do gerador shunt: curva de magnetização Ea x If
        e reta de resistência de campo Rf — convergência no ponto de operação."""
        fig, ax = plt.subplots(figsize=(6.6, 4.6))
        fig.patch.set_alpha(0); ax.set_facecolor("none")

        If = np.linspace(0, 10, 300)
        Ear = 4.0   # tensão residual
        def mag(x, k=11.0, knee=4.5, p=1.7):
            lin = k*x + Ear
            sat = lin/(1+((k*x)/(k*knee))**p)**(1/p)
            return sat + Ear*(1 - x/(x+0.3))*0  # placeholder, simplificado abaixo

        # curva de magnetização com tensão residual em If=0
        Ea = Ear + (100-Ear) * (1 - np.exp(-If/2.2))
        Ea = np.clip(Ea, 0, None)
        # achatar mais para saturação
        Ea = Ear + (100-Ear) * (If/(If+2.0)) ** 0.85
        ax.plot(If, Ea, color=AZ, lw=2.6, label="Curva de magnetização $E_a(I_f)$")

        line = Rf_slope*100/8.5 * If
        ax.plot(If, line, color=LR, lw=2.2, label=f"Reta $R_f\\!\\cdot\\!I_f$")

        # interseção
        idx = np.argmin(np.abs(Ea-line))
        if If[idx] > 0.3:
            ax.plot(If[idx], Ea[idx], marker="o", color=TX, ms=8, zorder=6)
            ax.annotate("Ponto de\noperação P", xy=(If[idx], Ea[idx]), xytext=(If[idx]-3.0, Ea[idx]+12),
                        fontsize=9, color=TX, arrowprops=dict(arrowstyle="->", color=TX, lw=1.0))

        if show_buildup:
            # escada ilustrativa de autoexcitação
            x = 0.15
            pts = [(0, Ear)]
            for _ in range(6):
                y_on_mag = np.interp(x, If, Ea)
                pts.append((x, y_on_mag))
                x_on_line = y_on_mag / (Rf_slope*100/8.5) if Rf_slope > 0 else x
                pts.append((x_on_line, y_on_mag))
                x = x_on_line
                if x > If[idx]*0.97: break
            xs, ys = zip(*pts)
            ax.plot(xs, ys, color=CZ, lw=1.1, ls="--", zorder=3)

        ax.plot(0, Ear, marker="o", color=VD, ms=6, zorder=6)
        ax.annotate("$E_{ar}$ (residual)", xy=(0, Ear), xytext=(0.35, Ear+9),
                    fontsize=8.5, color=VD)

        ax.set_xlim(0, 10); ax.set_ylim(0, 115)
        ax.set_xlabel("$I_f$ (A)", fontsize=10, color=TX)
        ax.set_ylabel("$E_a$ (% nominal)", fontsize=10, color=TX)
        ax.legend(fontsize=8.5, loc="lower right", frameon=False)
        for s in ["top","right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.tick_params(colors=TX, labelsize=8)
        ax.set_title("Autoexcitação do gerador shunt", fontsize=10.5, color=TX, pad=10)
        fig.tight_layout()
        return fig


    def _gerador_composto_painel(ax, short_shunt=True):
        ax.set_facecolor("none"); ax.axis("off"); ax.set_aspect("equal")
        ax.set_xlim(-1.0, 6.6); ax.set_ylim(-2.3, 2.3)

        ax0 = 1.6
        ax.add_patch(plt.Circle((ax0, 0), 0.5, fc="white", ec=TX, lw=1.7, zorder=5))
        ax.text(ax0, 0, "$E_a$", fontsize=11, color=TX, ha="center", va="center", zorder=6)
        ax.plot([ax0, ax0], [0.5, 1.3], color=TX, lw=1.5)
        _zigzag_v(ax, 1.3, 2.0, ax0, n_zig=3, amp=0.12, color=TX, lw=1.5)
        ax.text(ax0+0.32, 1.65, "$R_a$", fontsize=9, color=TX)
        ax.plot([ax0, ax0], [-0.5, -2.0], color=TX, lw=1.5)
        ax.text(ax0+0.15, 0.65, "+", fontsize=10, color=TX)
        ax.text(ax0+0.15, -0.65, "$-$", fontsize=10, color=TX)

        if short_shunt:
            node1 = ax0
            ax.plot([node1, node1+1.0], [2.0, 2.0], color=TX, lw=1.5)
            fx = node1 + 1.0
            ax.add_patch(plt.Circle((fx, 2.0), .035, fc=TX, ec=TX, zorder=7))
            _zigzag(ax, fx+0.4, fx+1.5, 2.0, n_zig=3, amp=0.12, color=VD, lw=1.5)
            ax.text(fx+0.95, 2.3, "$R_{sr}$", fontsize=9, color=VD, ha="center")
            ax.plot([fx+1.5, fx+2.4], [2.0, 2.0], color=TX, lw=1.5)
            tx = fx+2.4
        else:
            ax.plot([ax0, ax0+1.0], [2.0, 2.0], color=TX, lw=1.5)
            _zigzag(ax, ax0+0.3, ax0+1.0, 2.0, n_zig=3, amp=0.12, color=VD, lw=1.5)
            ax.text(ax0+0.65, 2.3, "$R_{sr}$", fontsize=9, color=VD, ha="center")
            fx = ax0 + 1.7
            ax.plot([ax0+1.0, fx], [2.0,2.0], color=TX, lw=1.5)
            ax.add_patch(plt.Circle((fx, 2.0), .035, fc=TX, ec=TX, zorder=7))
            ax.plot([fx, fx+1.5], [2.0, 2.0], color=TX, lw=1.5)
            tx = fx+1.5

        ax.plot([ax0, tx], [-2.0, -2.0], color=TX, lw=1.5)
        ax.add_patch(plt.Circle((fx, -2.0), .035, fc=TX, ec=TX, zorder=7))

        _zigzag_v(ax, -1.2, 0.3, fx, n_zig=4, amp=0.11, color=AZ, lw=1.4)
        ax.plot([fx, fx], [0.3, 0.5], color=AZ, lw=1.4)
        _zigzag_v(ax, 0.5, 0.95, fx, n_zig=2, amp=0.09, color=AZ, lw=1.4)
        ax.plot([fx, fx], [0.95, 2.0], color=AZ, lw=1.4)
        ax.plot([fx, fx], [-2.0, -1.2], color=AZ, lw=1.4)
        ax.text(fx+0.28, -0.4, "$R_{fc}{+}R_{fw}$", fontsize=7.5, color=AZ, rotation=90, va="center")

        ax.add_patch(plt.Circle((tx, 2.0), .05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.add_patch(plt.Circle((tx, -2.0), .05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(tx+0.18, 2.0, "+", fontsize=10, color=TX, va="center")
        ax.text(tx+0.18, -2.0, "$-$", fontsize=10, color=TX, va="center")
        title = "Composto curto (short shunt)" if short_shunt else "Composto longo (long shunt)"
        ax.set_title(title, fontsize=10, color=TX, pad=10)


    def fig_gerador_composto_circuitos():
        fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.0))
        fig.patch.set_alpha(0)
        _gerador_composto_painel(axes[0], short_shunt=True)
        _gerador_composto_painel(axes[1], short_shunt=False)
        fig.tight_layout()
        return fig


    def fig_caracteristica_composto():
        """Família de curvas Vt x Ia para composto: sobrecomposto, plano, subcomposto
        e diferencial."""
        fig, ax = plt.subplots(figsize=(6.8, 4.6))
        fig.patch.set_alpha(0); ax.set_facecolor("none")

        Ia = np.linspace(0, 130, 200)
        Vt_rated = 100
        over = Vt_rated + 0.22*Ia - 0.0009*Ia**2
        flat = Vt_rated + 0.0*Ia - 0.0003*Ia**2
        under = Vt_rated - 0.07*Ia
        diff = Vt_rated - 0.55*Ia + 0.0008*Ia**2
        diff = np.clip(diff, -100, None)

        ax.plot(Ia, over, color=AZ, lw=2.2, label="Sobrecomposto")
        ax.plot(Ia, flat, color=VD, lw=2.2, label="Composto plano")
        ax.plot(Ia, under, color=LR, lw=2.2, label="Subcomposto")
        ax.plot(Ia, diff, color=RX, lw=2.2, label="Diferencial")
        ax.axvline(100, color=CZ, lw=1.0, ls=":")
        ax.text(101, 8, "$I_{a(nom)}$", fontsize=8.5, color=CZ)
        ax.plot(0, Vt_rated, marker="o", color=TX, ms=5, zorder=6)

        ax.set_xlim(0, 130); ax.set_ylim(0, 130)
        ax.set_xlabel("$I_a$ (% nominal)", fontsize=10, color=TX)
        ax.set_ylabel("$V_t$ (% nominal)", fontsize=10, color=TX)
        ax.legend(fontsize=8.5, loc="lower left", frameon=False)
        for s in ["top","right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.tick_params(colors=TX, labelsize=8)
        ax.set_title("Característica terminal — gerador composto", fontsize=10.5, color=TX, pad=10)
        fig.tight_layout()
        return fig


    def fig_gerador_serie_circuito():
        """Circuito do gerador CC série: enrolamento de campo em série com a
        armadura e a carga — uma única malha de corrente."""
        fig, ax = _mpl_base((6.6, 3.8))
        ax.set_xlim(-0.6, 7.6); ax.set_ylim(-2.1, 2.1)

        ax0 = 1.4
        ax.add_patch(plt.Circle((ax0, 0), 0.5, fc="white", ec=TX, lw=1.7, zorder=5))
        ax.text(ax0, 0, "$E_a$", fontsize=11, color=TX, ha="center", va="center", zorder=6)
        ax.annotate("", xy=(ax0-0.75, -0.6), xytext=(ax0-0.4, -0.35),
                    arrowprops=dict(arrowstyle="-|>", color=CZ, lw=1.1))
        ax.text(ax0-1.0, -0.7, "$\\omega_m$", fontsize=9.5, color=CZ)
        ax.plot([ax0, ax0], [0.5, 1.2], color=TX, lw=1.5)
        _zigzag_v(ax, 1.2, 1.9, ax0, n_zig=3, amp=0.12, color=TX, lw=1.5)
        ax.text(ax0+0.32, 1.55, "$R_a$", fontsize=9.5, color=TX)
        ax.plot([ax0, ax0], [-0.5, -1.9], color=TX, lw=1.5)
        ax.annotate("", xy=(ax0+0.7, 1.9), xytext=(ax0+0.3, 1.9),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.1))
        ax.text(ax0+0.5, 2.1, "$I_a$", fontsize=9.5, color=TX, ha="center")

        ax.plot([ax0, ax0+1.6], [1.9, 1.9], color=TX, lw=1.5)
        _zigzag(ax, ax0+1.6, ax0+2.7, 1.9, n_zig=3, amp=0.13, color=VD, lw=1.6)
        ax.text(ax0+2.15, 2.18, "$R_{sr}$", fontsize=9.5, color=VD, ha="center")
        ax.plot([ax0+2.7, ax0+3.6], [1.9, 1.9], color=TX, lw=1.5)

        tx = ax0+3.6
        ax.add_patch(plt.Circle((tx, 1.9), .05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(tx+0.18, 1.9, "+", fontsize=10, color=TX, va="center")
        ax.text(tx-0.4, 2.15, "$I_t$", fontsize=9.5, color=TX)
        ax.text((ax0+0.5+tx)/2+0.6, 0, "$V_t$", fontsize=10.5, color=TX, ha="center")

        lx = ax0+5.6
        ax.plot([tx, lx], [1.9, 1.9], color=TX, lw=1.5)
        ax.plot([ax0, lx], [-1.9, -1.9], color=TX, lw=1.5)
        ax.plot([lx, lx], [-1.9, 1.9], color=LR, lw=1.5)
        _zigzag_v(ax, -1.3, 1.3, lx, n_zig=5, amp=0.13, color=LR, lw=1.5)
        ax.text(lx+0.3, 0, "$R_L$", fontsize=9.5, color=LR, va="center")
        ax.add_patch(plt.Circle((tx, -1.9), .05, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(tx+0.18, -1.9, "$-$", fontsize=10, color=TX, va="center")

        fig.tight_layout()
        return fig


    def fig_caracteristica_serie():
        """Curva característica do gerador série: Vt cresce com It seguindo a
        saturação, depois cai por reação de armadura; reta de carga RL."""
        fig, ax = plt.subplots(figsize=(6.6, 4.4))
        fig.patch.set_alpha(0); ax.set_facecolor("none")

        It = np.linspace(0.001, 130, 300)
        Vt = 120*(It/(It+22))**0.9 - 0.0022*It**2
        Vt = np.clip(Vt, 0, None)

        ax.plot(It, Vt, color=RX, lw=2.6, label="Característica terminal ($V_t \\times I_t$)")
        RL_slope = 0.62
        load = RL_slope*It
        ax.plot(It, load, color=LR, lw=1.8, label="Reta de carga ($R_L$)")
        mask = It > 20
        idx_local = np.argmin(np.abs(Vt[mask]-load[mask]))
        idx = np.where(mask)[0][idx_local]
        if idx > 3:
            ax.plot(It[idx], Vt[idx], marker="o", color=TX, ms=7, zorder=6)
            ax.annotate("P", xy=(It[idx], Vt[idx]), xytext=(It[idx]+6, Vt[idx]+6),
                        fontsize=10, color=TX)

        ax.set_xlim(0, 130); ax.set_ylim(0, 90)
        ax.set_xlabel("$I_t$ (A)", fontsize=10, color=TX)
        ax.set_ylabel("$V_t$ (V)", fontsize=10, color=TX)
        ax.legend(fontsize=8.5, loc="upper left", frameon=False)
        for s in ["top","right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.tick_params(colors=TX, labelsize=8)
        ax.set_title("Característica terminal — gerador série", fontsize=10.5, color=TX, pad=10)
        fig.tight_layout()
        return fig

    # ════════════════════════════════════════════════════════════════════════
    # EXPLORADORES INTERATIVOS (Plotly)
    # ════════════════════════════════════════════════════════════════════════

    def exp_tensao_torque():
        st.markdown("**Ajuste os parâmetros construtivos e o ponto de operação:**")
        c1, c2 = st.columns(2)
        with c1:
            Ka = st.slider("Constante de máquina $K_a$", 0.5, 5.0, 2.0, step=0.1, key="m3_e1_ka")
            Phi = st.slider("Fluxo por polo $\\Phi$ (Wb)", 0.005, 0.05, 0.02, step=0.001,
                             format="%.3f", key="m3_e1_phi")
        with c2:
            wm_op = st.slider("Velocidade $\\omega_m$ (rad/s)", 0.0, 200.0, 120.0, step=5.0, key="m3_e1_wm")
            Ia_op = st.slider("Corrente de armadura $I_a$ (A)", 0.0, 100.0, 60.0, step=5.0, key="m3_e1_ia")

        wm_a = np.linspace(0, 210, 200)
        Ea_a = Ka*Phi*wm_a
        Ea_op = Ka*Phi*wm_op

        Ia_a = np.linspace(0, 110, 200)
        T_a = Ka*Phi*Ia_a
        T_op = Ka*Phi*Ia_op

        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=wm_a, y=Ea_a, mode="lines", name="$E_a=K_a\\Phi\\omega_m$",
                                      line=dict(color=AZ, width=3)))
            fig.add_trace(go.Scatter(x=[wm_op], y=[Ea_op], mode="markers",
                                      marker=dict(color=LR, size=11),
                                      name=f"Op: ωm={wm_op:.0f}, Ea={Ea_op:.1f} V"))
            fig.update_layout(title="Tensão Induzida $E_a$ vs. Velocidade",
                               xaxis_title="ωm (rad/s)", yaxis_title="Ea (V)",
                               legend=dict(orientation="h", y=-0.3))
            show_plot(fig, key="m3_exp1_ea", height=380)
        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=Ia_a, y=T_a, mode="lines", name="$T=K_a\\Phi I_a$",
                                       line=dict(color=RX, width=3)))
            fig2.add_trace(go.Scatter(x=[Ia_op], y=[T_op], mode="markers",
                                       marker=dict(color=LR, size=11),
                                       name=f"Op: Ia={Ia_op:.0f}, T={T_op:.1f} N·m"))
            fig2.update_layout(title="Torque Eletromagnético $T$ vs. Corrente",
                                xaxis_title="Ia (A)", yaxis_title="T (N·m)",
                                legend=dict(orientation="h", y=-0.3))
            show_plot(fig2, key="m3_exp1_t", height=380)

        Pe = Ea_op*Ia_op
        for col, (lab, val) in zip(st.columns(4), [
            ("Ea (V)",        f"{Ea_op:.2f}"),
            ("T (N·m)",       f"{T_op:.2f}"),
            ("Pe = Ea·Ia (W)",f"{Pe:.1f}"),
            ("Pm = T·ωm (W)", f"{T_op*wm_op:.1f}"),
        ]):
            with col: st.metric(lab, val)
        st.caption("Observe que $P_e=E_a I_a$ e $P_m=T\\,\\omega_m$ resultam sempre iguais — "
                   "consequência direta de $E_a=K_a\\Phi\\omega_m$ e $T=K_a\\Phi I_a$ compartilharem a mesma constante $K_a$.")


    def exp_magnetizacao():
        st.markdown("**Ajuste a velocidade e o ponto de operação na curva de saturação:**")
        c1, c2 = st.columns(2)
        with c1:
            wm_frac = st.slider("Velocidade (fração da nominal)", 0.2, 1.0, 1.0, step=0.05, key="m3_e2_wf")
        with c2:
            Fp_op = st.slider("Força magnetomotriz de campo $F_p$", 0.0, 10.0, 5.0, step=0.1, key="m3_e2_fp")

        Fp = np.linspace(0, 10, 300)
        def sat(x, k, knee=4.0, p=1.6):
            lin = k*x
            return lin / (1 + (lin/(k*knee))**p)**(1/p)
        E_nom = sat(Fp, k=1.0)
        E_cur = E_nom*wm_frac
        E_op = float(np.interp(Fp_op, Fp, E_cur))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=Fp, y=E_nom, mode="lines", name="Velocidade nominal",
                                  line=dict(color=CZ, width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=Fp, y=E_cur, mode="lines",
                                  name=f"{wm_frac*100:.0f}% da velocidade nominal",
                                  line=dict(color=AZ, width=3)))
        fig.add_trace(go.Scatter(x=[Fp_op], y=[E_op], mode="markers",
                                  marker=dict(color=LR, size=12),
                                  name=f"Op: Fp={Fp_op:.1f}, Ea={E_op:.2f}"))
        fig.update_layout(title="Curva de Magnetização — Efeito da Velocidade e Saturação",
                           xaxis_title="Fp (FMM de campo)", yaxis_title="Ea (p.u.)",
                           legend=dict(orientation="h", y=-0.3))
        show_plot(fig, key="m3_exp2_mag", height=420)

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Ea no ponto de operação", f"{E_op:.3f} p.u.")
        with c2: st.metric("Inclinação local (≈μ)", f"{(np.interp(Fp_op+.05,Fp,E_cur)-np.interp(Fp_op-.05,Fp,E_cur))/.1:.3f}")
        with c3: st.metric("Grau de saturação", f"{(1 - E_op/(wm_frac*Fp_op if Fp_op>0 else 1))*100:.0f}%" if Fp_op>0 else "—")
        st.caption("A curva tracejada é a referência na velocidade nominal; a curva cheia mostra o "
                   "efeito de operar a uma fração diferente da velocidade. Em baixos valores de $F_p$ "
                   "a resposta é aproximadamente linear; em valores elevados, a saturação do núcleo "
                   "achata a curva. Como $E_a\\propto\\omega_m$ para um mesmo $F_p$, as duas curvas têm "
                   "sempre a mesma forma — apenas escaladas verticalmente uma em relação à outra.")


    def exp_comutacao():
        st.markdown("**Ajuste o número de segmentos do comutador (lâminas):**")
        n_seg = st.slider("Número de segmentos do comutador", 2, 24, 8, step=1, key="m3_e3_nseg")

        theta = np.linspace(0, 720, 1500)
        rad = np.radians(theta)
        delta = np.pi/n_seg
        total = np.zeros_like(rad)
        for k in range(n_seg):
            total += np.abs(np.cos(rad - k*delta))
        total /= n_seg

        ripple = (total.max()-total.min())/total.mean()*100

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=theta, y=total, mode="lines", name="$e_{12}(\\theta)$",
                                  line=dict(color=RX, width=3)))
        fig.add_hline(y=total.mean(), line=dict(color=CZ, dash="dash", width=1.4),
                      annotation_text="média", annotation_position="top left")
        fig.update_layout(title=f"Tensão Comutada — {n_seg} segmentos (ondulação ≈ {ripple:.1f}%)",
                           xaxis_title="θ (graus elétricos)", yaxis_title="e₁₂ (p.u.)",
                           showlegend=False)
        show_plot(fig, key="m3_exp3_comut", height=400)

        c1, c2 = st.columns(2)
        with c1: st.metric("Ondulação (ripple)", f"{ripple:.1f}%")
        with c2: st.metric("Valor médio E₁₂", f"{total.mean():.3f} p.u.")
        st.caption("Quanto maior o número de segmentos do comutador (e, portanto, de bobinas na armadura), "
                   "menor a ondulação da tensão de saída — no limite, a tensão se aproxima de um valor contínuo puro.")


    def exp_enrolamentos():
        st.markdown("**Compare os enrolamentos imbricado (lap) e ondulado (wave):**")
        c1, c2 = st.columns(2)
        with c1:
            p = st.slider("Número de polos $p$", 2, 12, 4, step=2, key="m3_e4_p")
        with c2:
            Ia_total = st.slider("Corrente total de armadura $I_a$ (A)", 10, 200, 100, step=10, key="m3_e4_ia")

        a_lap, a_wave = p, 2
        Icoil_lap, Icoil_wave = Ia_total/a_lap, Ia_total/a_wave
        Krel_lap, Krel_wave = 1.0, p/2

        fig = go.Figure()
        fig.add_trace(go.Bar(x=["Imbricado (lap)", "Ondulado (wave)"],
                              y=[Icoil_lap, Icoil_wave], name="Corrente por caminho (A)",
                              marker_color=RX))
        fig.update_layout(title="Corrente por caminho paralelo ($I_a/a$)",
                           yaxis_title="Corrente (A)", showlegend=False)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=["Imbricado (lap)", "Ondulado (wave)"],
                               y=[Krel_lap, Krel_wave], name="Tensão relativa",
                               marker_color=AZ))
        fig2.update_layout(title="Tensão relativa (mesmo Z, Φ, ωm)",
                            yaxis_title="Ea / Ea(lap)", showlegend=False)

        c1, c2 = st.columns(2)
        with c1: show_plot(fig, key="m3_exp4_i", height=360)
        with c2: show_plot(fig2, key="m3_exp4_v", height=360)

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("a (lap)", f"{a_lap}")
        with c2: st.metric("a (wave)", "2")
        with c3: st.metric("I_coil (lap)", f"{Icoil_lap:.1f} A")
        with c4: st.metric("I_coil (wave)", f"{Icoil_wave:.1f} A")
        st.caption(f"Com $p={p}$ polos: o enrolamento imbricado oferece $a=p={p}$ caminhos paralelos "
                   "(mais corrente, menos tensão), enquanto o ondulado mantém sempre $a=2$ "
                   "(menos corrente por caminho, tensão $p/2$ vezes maior, para o mesmo número de condutores).")

    def exp_regulacao_tensao():
        st.markdown("**Ajuste a resistência de armadura, a reação de armadura e a carga:**")
        c1, c2, c3 = st.columns(3)
        with c1:
            Ra_e = st.slider("Queda por $R_a$ (% em $I_t$ nominal)", 2, 25, 12, step=1, key="m3_e5_ra")
        with c2:
            ar_e = st.slider("Intensidade da reação de armadura", 0, 10, 4, step=1, key="m3_e5_ar")
        with c3:
            RL_e = st.slider("Carga — inclinação da reta ($R_L$, relativo)", 20, 150, 70, step=5, key="m3_e5_rl")

        It = np.linspace(0, 130, 250)
        Ea = 100 - 0.15*ar_e/10*It
        Vt_no_ar = 100 - (Ra_e/100)*It
        Vt_ar = 100 - (Ra_e/100)*It - (ar_e/1000)*It**2
        Vt_ar = np.clip(Vt_ar, 0, None)
        load = (RL_e/100)*It

        mask = It > 5
        idx_local = np.argmin(np.abs(Vt_ar[mask]-load[mask]))
        idx = np.where(mask)[0][idx_local]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=It, y=Ea, mode="lines", name="Ea (com reação)",
                                  line=dict(color=AZ, width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=It, y=Vt_no_ar, mode="lines", name="Terminal sem reação de armadura",
                                  line=dict(color=CZ, width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=It, y=Vt_ar, mode="lines", name="Terminal com reação de armadura",
                                  line=dict(color=RX, width=3)))
        fig.add_trace(go.Scatter(x=It, y=load, mode="lines", name="Reta de carga",
                                  line=dict(color=LR, width=2)))
        fig.add_trace(go.Scatter(x=[It[idx]], y=[Vt_ar[idx]], mode="markers",
                                  marker=dict(color=TX, size=11), name="Ponto de operação"))
        fig.update_layout(title="Característica Terminal e Ponto de Operação",
                           xaxis_title="It (% nominal)", yaxis_title="Vt (% nominal)",
                           legend=dict(orientation="h", y=-0.3))
        show_plot(fig, key="m3_exp5_term", height=420)

        Vnl = Vt_ar[0]
        Vfl = float(np.interp(100, It, Vt_ar))
        reg = (Vnl-Vfl)/Vfl*100 if Vfl > 0 else float("nan")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Vt a vazio", f"{Vnl:.1f}%")
        with c2: st.metric("Vt em carga nominal", f"{Vfl:.1f}%")
        with c3: st.metric("Regulação de tensão", f"{reg:.1f}%")
        st.caption("$R_{V_t}=(V_{tsc}-V_{tnom})/V_{tnom}$ — quanto maior a queda por $R_a$ e mais forte a "
                   "reação de armadura, maior a regulação (pior a estabilidade da tensão terminal sob carga).")


    def exp_autoexcitacao():
        st.markdown("**Ajuste a resistência do circuito de campo $R_f$ e observe a autoexcitação:**")
        Rf_e = st.slider("Resistência de campo $R_f$ (relativa)", 0.3, 4.5, 1.0, step=0.05, key="m3_e6_rf")

        If = np.linspace(0, 10, 300)
        Ear = 4.0
        Ea = Ear + (100-Ear) * (If/(If+2.0)) ** 0.85
        i_ref = np.argmin(np.abs(If-1.0))
        slope0 = Ea[i_ref]/If[i_ref]   # secante origem->1A (resistência crítica aprox.)
        line = Rf_e*100/8.5 * If

        diff = Ea - line
        sign_changes = np.where(np.diff(np.sign(diff[3:])) != 0)[0]
        has_intersection = len(sign_changes) > 0 and Rf_e*100/8.5 < slope0

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=If, y=Ea, mode="lines", name="Curva de magnetização",
                                  line=dict(color=AZ, width=3)))
        fig.add_trace(go.Scatter(x=If, y=line, mode="lines", name=f"Reta Rf·If",
                                  line=dict(color=LR, width=2.5)))
        if has_intersection:
            idx = sign_changes[-1]+3
            fig.add_trace(go.Scatter(x=[If[idx]], y=[Ea[idx]], mode="markers",
                                      marker=dict(color=TX, size=12), name="Ponto de operação"))
            Vbuild = Ea[idx]
        else:
            Vbuild = Ear
        fig.update_layout(title="Autoexcitação do Gerador Shunt",
                           xaxis_title="If (A)", yaxis_title="Ea (% nominal)",
                           legend=dict(orientation="h", y=-0.3))
        show_plot(fig, key="m3_exp6_auto", height=420)

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Tensão residual", f"{Ear:.1f}%")
        with c2: st.metric("Tensão de regime", f"{Vbuild:.1f}%")
        with c3: st.metric("Resistência crítica (aprox.)", f"{slope0*8.5/100:.2f} (relativa)")
        if not has_intersection:
            st.warning("⚠️ $R_f$ acima da resistência crítica: a reta não cruza a curva de magnetização "
                       "de forma útil — o gerador **não consegue se autoexcitar** além da tensão residual.")
        st.caption("Quanto mais inclinada a reta $R_f\\cdot I_f$ (maior $R_f$), menor a tensão final de "
                   "regime. Acima da **resistência crítica** — quando a reta se aproxima da inclinação "
                   "inicial da curva de magnetização —, a autoexcitação deixa de ocorrer.")

    # ═══════════════════════════════════════════════════════════════════════════════
    # CABEÇALHO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.title("⚙️ Máquinas Elétricas de Corrente Contínua")
    st.caption("⚡ SINTONIA · Máquinas Elétricas · 👤 Marcus V A Fernandes · ✉️ marcus.fernandes@ifrn.edu.br")
    st.markdown("---")

    # ── Índice ────────────────────────────────────────────────────────────────────
    with st.expander("📋 Índice — clique para expandir", expanded=False):
        st.markdown("""
    **[1. Conceitos Elementares e Aplicações](#1-conceitos-elementares-e-aplicacoes)**

    **[2. Estrutura Construtiva — Campo e Armadura](#2-estrutura-construtiva-campo-e-armadura)**

    **[3. Comutador e Escovas](#3-comutador-e-escovas)**

    **[4. Distribuição da Força Magnetomotriz e Comutação](#4-distribuicao-da-forca-magnetomotriz-e-comutacao)**

    **[5. Enrolamento da Armadura — Volta, Bobina e Enrolamento](#5-enrolamento-da-armadura-volta-bobina-e-enrolamento)**

    **[6. Número de Polos e Ângulo Elétrico](#6-numero-de-polos-e-angulo-eletrico)**

    **[7. Tipos de Enrolamento — Imbricado e Ondulado](#7-tipos-de-enrolamento-imbricado-e-ondulado)**

    **[8. Tensão Induzida na Armadura](#8-tensao-induzida-na-armadura)**

    **[9. Torque Eletromagnético](#9-torque-eletromagnetico)**

    **[10. Curva de Magnetização](#10-curva-de-magnetizacao)**

    **[11. Reação da Armadura](#11-reacao-da-armadura)**

    **[12. Interpolos](#12-interpolos)**

    **[13. Classificação dos Geradores CC e Regulação de Tensão](#13-classificacao-dos-geradores-cc-e-regulacao-de-tensao)**

    **[14. Gerador de Excitação Independente](#14-gerador-de-excitacao-independente)**

    **[15. Gerador Shunt (Autoexcitado)](#15-gerador-shunt-autoexcitado)**

    **[16. Gerador Composto (Compound)](#16-gerador-composto-compound)**

    **[17. Gerador Série](#17-gerador-serie)**

    **[🎛️ Exploradores Interativos](#exploradores-interativos)**
    - Tensão e torque induzidos · Curva de magnetização · Ondulação de comutação · Lap vs. wave
    - Regulação de tensão · Autoexcitação shunt

    **Referências** (ao final da página)
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 1 — CONCEITOS ELEMENTARES
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("1. Conceitos Elementares e Aplicações")

    st.markdown(r"""
    A **máquina de corrente contínua (CC)** é um conversor eletromecânico reversível: a
    mesma máquina pode operar como **gerador** (entrada mecânica, saída elétrica em CC) ou
    como **motor** (entrada elétrica em CC, saída mecânica). Na prática industrial, o uso
    como **motor** é amplamente predominante, sobretudo pela facilidade de **controle de
    velocidade**, historicamente mais simples na máquina CC do que nas máquinas CA.

    Motores CC de grande potência acionam cargas como prensas de impressão, esteiras
    transportadoras, ventiladores, bombas, guinchos, guindastes, máquinas de papel e
    laminadores — aplicações em que o controle fino de velocidade e torque é decisivo.
    Motores CC de pequeno porte, por sua vez, são amplamente empregados como **dispositivos
    de controle** (servomotores, atuadores) em malhas de automação.

    > Hoje, motores CA com acionamento eletrônico já substituem boa parte dessas aplicações,
    > mas a máquina CC permanece a porta de entrada conceitual mais direta para torque,
    > tensão induzida e conversão eletromecânica — princípios que reaparecem, generalizados,
    > nas máquinas CA.
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 2 — ESTRUTURA CONSTRUTIVA: CAMPO E ARMADURA
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("2. Estrutura Construtiva — Campo e Armadura")

    st.markdown(r"""
    A máquina CC é construída em torno de dois enrolamentos com papéis bem distintos:

    - **Enrolamento de campo** (no estator): aquele que produz o **fluxo magnético
      principal** da máquina. É percorrido por uma corrente essencialmente contínua e fica
      alojado nos polos salientes do estator.
    - **Enrolamento de armadura** (no rotor): aquele que **conduz corrente alternada**
      internamente — mesmo a máquina operando em CC nos terminais, a corrente em cada
      condutor da armadura se inverte a cada passagem sob um polo de polaridade oposta.
      É justamente essa inversão, sincronizada mecanicamente pelo comutador (Seção 3), que
      permite operação em corrente contínua nos terminais externos.

    A figura a seguir mostra a seção transversal idealizada de uma máquina CC de 2 polos,
    com todos os enrolamentos típicos: campo (shunt e série), interpolos, enrolamento de
    compensação e enrolamento de armadura. O **eixo d** (eixo polar) é o eixo magnético do
    campo principal; o **eixo q** é o eixo interpolar, perpendicular ao eixo d — é sobre o
    eixo q que ficam os interpolos e, fisicamente, o eixo das escovas.
    """)

    show_fig(fig_secao_maquina_cc(), 0.62)

    st.markdown(r"""
    Interpolos (Seção 12) e enrolamento de compensação (Seção 11) não são estritamente
    necessários ao princípio de funcionamento: são refinamentos que corrigem efeitos de
    segunda ordem (reação da armadura, centelhamento na comutação), típicos de máquinas de
    médio e grande porte.
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 3 — COMUTADOR E ESCOVAS
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("3. Comutador e Escovas")

    st.markdown(r"""
    ### 3.1 Comutador

    O **comutador** é o elemento que converte a corrente alternada que circula pela
    armadura em corrente contínua nos terminais externos da máquina. Construtivamente, é
    formado por **segmentos (lâminas) de cobre** montados no eixo do rotor, isolados uns
    dos outros por lâminas de mica — cada par de segmentos corresponde a uma bobina (ou
    grupo de bobinas) do enrolamento de armadura.

    ### 3.2 Escovas

    As **escovas** são contatos fixos de grafita, montados no estator sobre molas que as
    mantêm pressionadas contra o comutador, permitindo que elas **deslizem** sobre os
    segmentos à medida que o rotor gira. É através das escovas que a corrente entra e sai
    da armadura.

    A figura abaixo mostra o caso mais simples possível: uma única bobina, um comutador de
    apenas **2 segmentos** ($C_a$ e $C_b$) e duas escovas fixas ($B_1$, $B_2$). À medida que
    o rotor gira, cada escova entra em contato alternadamente com um segmento e depois com
    o outro — e é exatamente nesse instante de troca que a polaridade da bobina em relação
    à escova se inverte, compensando a inversão natural da tensão induzida na bobina.
    """)

    show_fig(fig_comutador_basico(), 0.46)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 4 — DISTRIBUIÇÃO DA FMM E COMUTAÇÃO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("4. Distribuição da Força Magnetomotriz e Comutação")

    st.markdown(r"""
    Tomando o comutador elementar de 2 segmentos da Seção 3, é instrutivo observar a forma
    de onda da tensão **antes** e **depois** da comutação:

    - $e_{ab}$ — tensão induzida na própria bobina, entre seus dois terminais $a$ e $b$:
      uma onda **alternada** (trapezoidal), já que cada lado da bobina passa
      alternadamente sob um polo N e um polo S.
    - $e_{12}$ — tensão medida nos terminais externos (escovas 1 e 2), **após** a ação do
      comutador: o comutador troca a conexão dos terminais exatamente quando $e_{ab}$ passa
      por zero, de modo que $e_{12}$ é sempre **unidirecional** (retificada) — com pequenas
      reentrâncias (chegando a zero) nos instantes de comutação, quando a bobina em curto
      sob a escova não contribui com tensão útil.
    """)

    show_fig(fig_forma_onda_comutacao_simples(), 0.74)

    st.markdown(r"""
    Esse padrão de "ondulação" é bastante acentuado com apenas uma bobina. Na prática, o
    enrolamento de armadura é formado por **muitas bobinas** distribuídas ao longo da
    periferia do rotor, conectadas a um comutador com **muitos segmentos**. Como cada
    bobina contribui com sua própria tensão retificada, ligeiramente defasada das demais no
    tempo, a **soma** das contribuições resulta em uma tensão de saída com ondulação muito
    menor — tanto menor quanto maior o número de segmentos do comutador. Esse efeito pode
    ser explorado interativamente no [Explorador 3](#exploradores-interativos), ao final da
    página.
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 5 — ENROLAMENTO DA ARMADURA: VOLTA, BOBINA E ENROLAMENTO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("5. Enrolamento da Armadura — Volta, Bobina e Enrolamento")

    st.markdown(r"""
    A organização do enrolamento de armadura segue uma hierarquia de três níveis:

    - **Volta (*turn*)**: um único condutor fechado — fio de ida e volta — em torno do
      núcleo da armadura.
    - **Bobina (*coil*)**: um conjunto de $N$ voltas conectadas em série, ocupando as
      mesmas ranhuras do núcleo.
    - **Enrolamento (*winding*)**: o conjunto completo de bobinas interligadas (de uma
      extremidade $F$ de uma bobina à extremidade inicial $S$ da seguinte), distribuídas ao
      longo de toda a periferia da armadura e conectadas ao comutador.
    """)

    show_fig(fig_volta_bobina_enrolamento(), 0.85)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 6 — NÚMERO DE POLOS E ÂNGULO ELÉTRICO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("6. Número de Polos e Ângulo Elétrico")

    st.markdown(r"""
    Máquinas CC podem ter mais de um par de polos. Para descrever corretamente fenômenos
    periódicos ao longo do entreferro (como a própria tensão induzida), é necessário
    distinguir dois ângulos:

    - $\theta_{md}$ — **ângulo espacial (mecânico)**: posição física ao longo da
      circunferência do entreferro, de $0$ a $2\pi$ rad em uma volta completa do rotor.
    - $\theta_{ed}$ — **ângulo elétrico**: mede os "ciclos elétricos" completados — uma
      grandeza periodicamente relevante para tensões e correntes, já que cada par de polos
      percorrido corresponde a um ciclo elétrico completo.

    Com $p$ polos, cada volta mecânica completa corresponde a $p/2$ ciclos elétricos:

    $$\theta_{ed} = \frac{p}{2}\,\theta_{md}$$

    A figura abaixo ilustra o caso $p=4$: a densidade de fluxo $B(\theta)$ ao longo do
    entreferro é aproximadamente trapezoidal, alternando entre polos N e S a cada **passo
    polar**. Em uma volta mecânica completa ($\theta_{md}: 0\to2\pi$), o ângulo elétrico
    percorre **duas** voltas completas ($\theta_{ed}: 0\to4\pi$), exatamente como prevê a
    relação $\theta_{ed}=(p/2)\theta_{md}$ com $p=4$.
    """)

    col1, col2 = st.columns([0.85, 1.15])
    with col1:
        show_fig(fig_polos_4p(), 0.95)
    with col2:
        show_fig(fig_curva_Btheta(), 0.95)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 7 — TIPOS DE ENROLAMENTO: IMBRICADO E ONDULADO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("7. Tipos de Enrolamento — Imbricado e Ondulado")

    st.markdown(r"""
    A forma como as bobinas da armadura são conectadas ao comutador define o número de
    **caminhos paralelos** $a$ entre as escovas — e esse número determina diretamente a
    relação entre corrente e tensão disponíveis nos terminais.

    ### 7.1 Enrolamento imbricado (*lap*)

    No enrolamento **imbricado**, o número de caminhos paralelos é igual ao número de
    polos:

    $$a = p$$

    Cada par de escovas conecta-se a um caminho independente, de modo que a corrente total
    de armadura $I_a$ se divide em $p$ caminhos. Resultado: **corrente alta, tensão baixa**
    por caminho — adequado para máquinas de baixa tensão e alta corrente.
    """)

    show_fig(fig_enrolamento_lap(4), 0.78)

    st.markdown(r"""
    ### 7.2 Enrolamento ondulado (*wave*)

    No enrolamento **ondulado**, o número de caminhos paralelos é sempre **2**,
    independentemente do número de polos:

    $$a = 2$$

    Cada caminho percorre, em série, bobinas sob **todos** os pares de polos antes de
    fechar o circuito. Resultado: **tensão alta, corrente baixa** — adequado para máquinas
    de alta tensão e baixa corrente.
    """)

    show_fig(fig_enrolamento_wave(), 0.78)

    st.markdown(r"""
    A escolha entre imbricado e ondulado é, portanto, uma decisão de projeto ligada à
    relação tensão/corrente desejada nos terminais da máquina — explore essa relação no
    [Explorador 4](#exploradores-interativos).
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 8 — TENSÃO INDUZIDA NA ARMADURA
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("8. Tensão Induzida na Armadura")

    st.markdown(r"""
    ### 8.1 Tensão em um condutor

    Um condutor de comprimento $l$, deslocando-se com velocidade linear $v$ perpendicular a
    um campo de densidade de fluxo $B$, tem tensão induzida em seus terminais — consequência
    direta da lei de Faraday aplicada a um condutor em movimento:

    $$e = B\,l\,v$$
    """)

    col1, col2 = st.columns(2)
    with col1:
        show_fig(fig_condutor_campo("tensao"), 0.92)
    with col2:
        st.markdown(r"""
        A relação $e=Blv$ é **linear** em $v$ para um campo $B$ fixo — dobrar a
        velocidade dobra a tensão induzida. A polaridade segue a regra da mão direita
        (sentido de $\vec{v}\times\vec{B}$).
        """)

    st.markdown(r"""
    ### 8.2 Tensão em uma volta

    Substituindo $v=r\,\omega_m$ (velocidade linear do condutor a um raio $r$ do eixo,
    girando a $\omega_m$ rad/s) e somando a contribuição dos **dois lados** da volta:

    $$e_t = 2\,B(\theta)\,l\,r\,\omega_m$$

    Com $\Phi$ o fluxo por polo e $A=2\pi r l/p$ a área de uma face polar, a densidade de
    fluxo média sob o polo é:

    $$B(\theta) = \frac{\Phi}{A} = \frac{\Phi}{\dfrac{2\pi r l}{p}} = \frac{\Phi\,p}{2\pi r l} \quad\Rightarrow\quad e_t = \frac{\Phi\,p}{\pi}\,\omega_m$$

    ### 8.3 Tensão no enrolamento

    Com $N$ voltas em série por caminho e $a$ caminhos paralelos, a tensão induzida total
    nos terminais da armadura — a **força eletromotriz induzida** $E_a$ — é:

    $$E_a = \frac{N}{a}\,e_t \quad\Rightarrow\quad E_a = \frac{N}{a}\cdot\frac{\Phi\,p}{\pi}\,\omega_m \equiv K_a\,\Phi\,\omega_m$$

    onde $K_a$ é a **constante de máquina**, que depende apenas de parâmetros construtivos
    fixos (número de condutores, polos e caminhos paralelos):

    $$K_a \equiv \frac{N\,p}{\pi\,a} \quad\Rightarrow\quad K_a = \frac{Z\,p}{2\,\pi\,a}$$

    sendo $Z$ o número total de condutores da armadura ($Z=2N$, já que cada volta contém 2
    condutores).

    > A equação $E_a = K_a\Phi\omega_m$ é uma das mais importantes de toda a teoria de
    > máquinas CC: ela mostra que a tensão induzida é diretamente proporcional ao **fluxo**
    > e à **velocidade** — base de todo o controle de velocidade por enfraquecimento de
    > campo, estudado em seções futuras.
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 9 — TORQUE ELETROMAGNÉTICO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("9. Torque Eletromagnético")

    st.markdown(r"""
    ### 9.1 Força em um condutor

    Por simetria com a Seção 8, um condutor de comprimento $l$ percorrido por corrente $i$
    em um campo $B$ sofre uma força eletromagnética (força de Laplace sobre um condutor):

    $$f = B\,l\,i$$
    """)

    col1, col2 = st.columns(2)
    with col1:
        show_fig(fig_condutor_campo("forca"), 0.92)
    with col2:
        st.markdown(r"""
        Também aqui a relação é **linear**: a força (e, por extensão, o torque) cresce
        proporcionalmente à corrente, para um fluxo de campo fixo. O sentido de $f$ segue
        a mesma regra da mão direita da Seção 8.1, agora aplicada ao produto vetorial
        $\vec{f}=i\,\vec{l}\times\vec{B}$, com a corrente no lugar da velocidade.
        """)

    st.markdown(r"""
    ### 9.2 Torque em uma volta

    Cada caminho paralelo conduz uma fração $I_a/a$ da corrente total de armadura, de modo
    que a corrente em cada condutor é $i_c = I_a/a$. A força sobre cada lado da volta é:

    $$f_c = B(\theta)\,l\,i_c = B(\theta)\,l\,\frac{I_a}{a}$$

    e o torque induzido em um condutor, a um raio $r$ do eixo:

    $$T_c = f_c\,r = B(\theta)\,l\,r\,\frac{I_a}{a} \quad\Rightarrow\quad T_c = \frac{\Phi\,p}{2\pi r l}\cdot l\,r\,\frac{I_a}{a} = \frac{\Phi\,p\,I_a}{2\pi a}$$

    ### 9.3 Torque no enrolamento

    Todos os condutores da armadura desenvolvem torque na **mesma direção** — a expressão
    é válida tanto para operação como motor quanto como gerador. Somando a contribuição de
    todos os $2N$ condutores:

    $$T = 2\,N\,T_c \quad\Rightarrow\quad T = K_a\,\Phi\,I_a$$

    com a **mesma constante** $K_a$ definida na Seção 8.3. Desprezando perdas, a potência
    elétrica convertida deve igualar a potência mecânica desenvolvida:

    $$P_e = E_a\,I_a \qquad P_m = T\,\omega_m \qquad\Rightarrow\qquad P_e = P_m$$

    Essa igualdade pode ser verificada diretamente substituindo $E_a=K_a\Phi\omega_m$ e
    $T=K_a\Phi I_a$: ambos os lados resultam em $K_a\Phi\,I_a\,\omega_m$ — confirmando que
    $E_a$ e $T$ não são duas constantes independentes, mas duas manifestações da **mesma**
    constante de máquina $K_a$. Explore essa relação interativamente no
    [Explorador 1](#exploradores-interativos).
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 10 — CURVA DE MAGNETIZAÇÃO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("10. Curva de Magnetização")

    st.markdown(r"""
    A relação $E_a=K_a\Phi\omega_m$ pressupõe um fluxo $\Phi$ conhecido — mas $\Phi$, por
    sua vez, depende da **força magnetomotriz de campo** $F_p$ (proporcional à corrente de
    campo) através do circuito magnético da máquina, que inclui o núcleo polar, o
    entreferro, os dentes e o núcleo do rotor. Como o ferro satura, essa relação **não é
    linear** em toda a faixa de operação.

    A **curva de magnetização** (ou curva de saturação) relaciona $E_a$ — medida a vazio, a
    uma velocidade de referência — com $F_p$:

    - Para valores **baixos** de $F_p$, a relação é aproximadamente linear (regime não
      saturado, dominado pela relutância do entreferro).
    - Para valores **altos** de $F_p$, a curva se achata, refletindo a saturação magnética
      do ferro do núcleo.

    Como $E_a\propto\omega_m$ para um mesmo $\Phi$, a curva medida em uma velocidade
    diferente da referência é simplesmente **escalada verticalmente** — a curva à metade da
    velocidade nominal ($\omega_m/2$) reproduz a mesma forma, com metade da amplitude.
    """)

    show_fig(fig_curva_magnetizacao(), 0.62)

    st.markdown(r"""
    A curva de magnetização é a ferramenta gráfica fundamental para determinar o ponto de
    operação real da máquina (tensão induzida efetiva) a partir da corrente de campo — ela
    será usada extensivamente no estudo de geradores e motores CC. Explore o efeito conjunto
    de velocidade e saturação no [Explorador 2](#exploradores-interativos).
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 11 — REAÇÃO DA ARMADURA
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("11. Reação da Armadura")

    st.markdown(r"""
    Até aqui, tratamos o campo magnético como produzido exclusivamente pelo enrolamento de
    campo. Na realidade, a própria corrente de armadura $I_a$ produz seu **próprio** campo
    magnético $B_a$ — e esse campo se soma (vetorialmente) ao campo principal $B_f$,
    distorcendo a distribuição de fluxo no entreferro. Esse fenômeno é chamado **reação da
    armadura**.

    A reação da armadura tem duas consequências principais:

    - **Efeito de desmagnetização**: acima da corrente nominal, a distorção do fluxo entra
      na região não linear (saturação) sob uma metade do polo, de modo que o fluxo
      resultante **líquido** é menor do que a soma algébrica sugeriria — reduzindo $E_a$ e
      a tensão terminal $V_t$.
    - **Deslocamento da zona neutra**: o eixo de fluxo resultante se desloca em relação ao
      eixo do campo principal, podendo causar **centelhamento** nas escovas durante a
      comutação, caso elas permaneçam fixas no eixo geométrico original.
    """)

    show_fig(fig_reacao_armadura(), 0.62)

    st.markdown(r"""
    Duas estratégias construtivas mitigam a reação da armadura:

    - **Enrolamento de compensação**: bobinas embutidas nas faces polares, conectadas em
      série com a armadura e dispostas de modo a produzir um campo que **se opõe**
      diretamente ao campo da própria armadura na região do entreferro sob o polo.
    - **Interpolos**: tratados em detalhe na Seção 12, atuam especificamente na região do
      eixo q (zona de comutação).
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 12 — INTERPOLOS
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("12. Interpolos")

    st.markdown(r"""
    Os **interpolos** (também chamados polos de comutação) são polos auxiliares,
    estreitos, posicionados exatamente no **eixo q** — entre os polos principais, na mesma
    região onde se encontram as escovas. Seu enrolamento é conectado **em série** com a
    armadura, de modo que é percorrido pela própria corrente $I_a$.

    Por estar no eixo q — exatamente onde a reação da armadura é mais intensa e onde ocorre
    a comutação —, o fluxo do interpolo $\Phi_i$ pode ser dimensionado para **cancelar** o
    fluxo de reação da armadura $\Phi_a$ naquela região. Por estar em série com a própria
    armadura, esse cancelamento se mantém proporcional **qualquer que seja o valor — e
    mesmo o sentido — de $I_a$**: se $I_a$ inverte, $\Phi_a$ e $\Phi_i$ invertem juntos,
    preservando a oposição entre eles.
    """)

    show_fig(fig_interpolos(), 0.92)

    st.markdown(r"""
    Ao neutralizar o fluxo de reação na zona de comutação, os interpolos suprimem a tensão
    induzida indesejada na bobina em curto sob a escova durante a comutação — reduzindo
    drasticamente o centelhamento e o desgaste das escovas e do comutador. São item padrão
    em praticamente todas as máquinas CC de médio e grande porte.
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 13 — CLASSIFICAÇÃO DOS GERADORES CC E REGULAÇÃO DE TENSÃO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("13. Classificação dos Geradores CC e Regulação de Tensão")

    st.markdown(r"""
    Até aqui tratamos a máquina CC de forma genérica. A partir de agora, o foco passa a
    ser a **operação como gerador**: o eixo é acionado mecanicamente a $\omega_m$ e a
    máquina entrega potência elétrica nos terminais da armadura. A forma como o
    enrolamento de campo é conectado define o **tipo de gerador** — e essa escolha tem
    impacto direto sobre como a tensão terminal se comporta sob carga.

    - **Independente**: o campo é alimentado por uma fonte externa (outro gerador CC,
      retificador ou bateria) — circuito de campo e circuito de armadura totalmente
      desacoplados.
    - **Shunt (paralelo)**: o campo é conectado diretamente aos terminais da própria
      armadura — a máquina se **autoexcita**, sem fonte externa.
    - **Série**: o enrolamento de campo é percorrido pela própria corrente de carga —
      poucas espiras, grande seção, suporta correntes elevadas.
    - **Composto (compound)**: combina um enrolamento shunt e um enrolamento série no
      mesmo polo. Conforme o ponto em que o ramo shunt é conectado em relação ao
      enrolamento série, a ligação é dita **curta** (*short shunt*, shunt antes do
      enrolamento série) ou **longa** (*long shunt*, shunt depois do enrolamento série).
    """)

    show_fig(fig_classificacao_geradores(), 0.96)

    st.markdown(r"""
    Um parâmetro comum a todos os tipos é a **regulação de tensão**: o quanto a tensão
    terminal varia entre a operação a vazio e a operação em carga nominal.

    $$R_{V_t} \equiv \frac{V_{tsc}-V_{tnom}}{V_{tnom}}$$

    sendo $V_{tsc}$ a tensão terminal a vazio (sem carga) e $V_{tnom}$ a tensão terminal
    com a corrente de carga nominal. Quanto **menor** $R_{V_t}$, mais estável é a tensão
    terminal da máquina frente a variações de carga — um critério central na escolha do
    tipo de gerador para cada aplicação, como ficará claro nas seções seguintes.
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 14 — GERADOR DE EXCITAÇÃO INDEPENDENTE
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("14. Gerador de Excitação Independente")

    st.markdown(r"""
    No gerador de excitação independente, o circuito de campo é alimentado por uma fonte
    própria $V_f$, totalmente desacoplada da armadura. A corrente de campo fica então sob
    controle direto do reostato $R_{fc}$, sem depender da tensão gerada — característica
    que torna esse tipo de gerador o mais previsível e estável dos quatro.
    """)

    show_fig(fig_gerador_independente_circuito(), 0.74)

    st.markdown(r"""
    As equações do circuito seguem diretamente das leis de Kirchhoff e da relação
    $E_a=K_a\Phi\omega_m$ já estabelecida na Seção 8:

    $$V_f \equiv R_f\cdot I_f \qquad\quad V_t \equiv E_a - R_a\cdot I_a \qquad\quad E_a = K_a\,\Phi\,\omega_m \qquad\quad I_a = I_t \qquad\quad V_t = R_L\cdot I_t$$

    com $R_f=R_{fw}+R_{fc}$ a resistência total do circuito de campo, e $R_a$ a resistência
    do circuito de armadura (incluindo, se necessário, o efeito das escovas — quando não
    modelado dentro de $R_a$, costuma-se considerá-lo uma queda fixa de cerca de 2 V).

    Como $I_a=I_t$, toda a corrente de carga atravessa $R_a$: a tensão terminal cai
    **linearmente** com a corrente de carga, segundo $V_t=E_a-R_aI_a$. Em máquinas reais,
    soma-se a esse efeito a **reação da armadura** (Seção 11), que reduz ainda mais $E_a$
    em correntes elevadas — resultando em uma curva ligeiramente côncava, abaixo da reta
    ideal:
    """)

    show_fig(fig_caracteristica_terminal(), 0.62)

    st.markdown(r"""
    A interseção entre a característica terminal e a **reta de carga** ($V_t=R_LI_t$,
    inclinação $R_L$) define o **ponto de operação** real do conjunto gerador-carga. Por
    ter excitação independente da própria tensão gerada, esse gerador apresenta **boa
    regulação de tensão** — a queda é dominada apenas por $R_a$ e pela reação de armadura,
    sem o efeito adicional de realimentação que aparece no gerador shunt (Seção 15).
    Explore esse comportamento no [Explorador 5](#exploradores-interativos).
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 15 — GERADOR SHUNT (AUTOEXCITADO)
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("15. Gerador Shunt (Autoexcitado)")

    st.markdown(r"""
    No gerador shunt (ou paralelo), o enrolamento de campo é conectado **diretamente aos
    terminais da própria armadura** — não há fonte de campo externa. A máquina precisa,
    portanto, **se autoexcitar**: gerar sua própria tensão de campo a partir do zero.
    """)

    show_fig(fig_gerador_shunt_circuito(), 0.62)

    st.markdown(r"""
    As equações mudam em um ponto essencial — a corrente de armadura agora se divide
    entre a carga e o próprio campo:

    $$V_t \equiv E_a - R_a\cdot I_a \qquad\quad V_f = V_t = R_f\cdot I_f \qquad\quad I_a \equiv I_t + I_f \qquad\quad V_t = R_L\cdot I_t$$

    ### 15.1 Como a autoexcitação ocorre

    Sem corrente de campo, como a máquina pode gerar tensão para alimentar o próprio
    campo? A resposta está no **magnetismo residual** do núcleo polar: mesmo sem corrente
    de campo, um pequeno fluxo residual produz uma tensão residual $E_{ar}$ quando o rotor
    gira — suficiente para fazer circular uma pequena corrente de campo, que reforça o
    fluxo e aumenta a tensão gerada. É um processo de realimentação positiva que se repete
    em pequenos incrementos, convergindo para um ponto de equilíbrio.

    Esse processo aparece ao sobrepor a **curva de magnetização** $E_a(I_f)$ (Seção 10)
    com a **reta de resistência de campo** $R_f\cdot I_f$: o ponto de operação final é
    onde as duas se cruzam — ali, a tensão gerada é exatamente a necessária para
    impulsionar, através de $R_f$, a corrente de campo que sustenta aquele mesmo fluxo.
    """)

    show_fig(fig_autoexcitacao(), 0.62)

    st.markdown(r"""
    Quanto **maior** $R_f$ (reta mais inclinada), **menor** a tensão final de regime, até a
    **resistência crítica de campo**: além dela, a reta deixa de cruzar a porção útil da
    curva de magnetização e a máquina não se autoexcita além da tensão residual. Por
    depender da própria tensão gerada para excitar o campo, o gerador shunt também tem
    regulação de tensão **pior** que o de excitação independente: a queda em $R_a$ sob
    carga reduz $V_t$, que reduz $I_f$ e $E_a$, agravando ainda mais a queda — um efeito
    cumulativo ausente na excitação independente. Explore a autoexcitação e a resistência
    crítica no [Explorador 6](#exploradores-interativos).
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 16 — GERADOR COMPOSTO (COMPOUND)
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("16. Gerador Composto (Compound)")

    st.markdown(r"""
    O gerador composto combina um enrolamento shunt (muitas espiras, alta resistência,
    corrente pequena e aproximadamente constante) com um enrolamento série (poucas
    espiras, baixa resistência, percorrido pela corrente de carga) no mesmo polo. Conforme
    o ponto em que o ramo shunt se conecta — antes ou depois do enrolamento série —, fala-se
    em ligação **curta** ou **longa**:
    """)

    show_fig(fig_gerador_composto_circuitos(), 0.92)

    st.markdown(r"""
    Em ambos os casos, o fluxo total por polo passa a ser a combinação dos dois
    enrolamentos, e a tensão induzida reflete essa soma. Tomando a ligação longa como
    referência (o enrolamento série soma sua queda à da armadura):

    $$E_a = K_a\,(\Phi_{sh}\pm\Phi_{sr})\,\omega_m \qquad\quad V_t = E_a - R_a\cdot I_a - R_{sr}\cdot I_a \qquad\quad I_a = I_t + I_f \qquad\quad V_t = R_L\cdot I_t$$

    O sinal $\pm$ indica que a composição pode ser:

    - **Cumulativa**: $\Phi_{sr}$ reforça $\Phi_{sh}$ — à medida que a carga (e portanto
      $I_a$) aumenta, o fluxo série cresce e **compensa** a queda que ocorreria por
      $R_a$ e pela reação de armadura.
    - **Diferencial**: $\Phi_{sr}$ se opõe a $\Phi_{sh}$ — o fluxo série **soma-se** à
      queda de tensão sob carga, agravando-a.

    Dentro da composição cumulativa, o número de espiras do enrolamento série $N_{sr}$
    determina o quanto o fluxo série compensa a queda de tensão — dando origem a uma
    família de comportamentos possíveis:
    """)

    show_fig(fig_caracteristica_composto(), 0.62)

    st.markdown(r"""
    - **Sobrecomposto**: $N_{sr}$ grande o suficiente para que $V_t$ **suba** com a carga.
    - **Composto plano**: $V_t$ permanece aproximadamente constante entre vazio e plena
      carga — a configuração mais comum em aplicações que exigem tensão estável.
    - **Subcomposto**: a compensação é parcial — $V_t$ ainda cai com a carga, porém menos
      do que cairia em um gerador puramente shunt.
    - **Diferencial**: usado propositalmente em aplicações que exigem corrente
      praticamente constante e tensão fortemente decrescente, como geradores para solda.
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 17 — GERADOR SÉRIE
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("17. Gerador Série")

    st.markdown(r"""
    No gerador série, não há enrolamento shunt: o único enrolamento de campo é percorrido
    pela própria corrente de carga, em uma única malha.
    """)

    show_fig(fig_gerador_serie_circuito(), 0.62)

    st.markdown(r"""
    $$E_a = K_a\,\Phi\,\omega_m \qquad\quad V_t = E_a - R_a\cdot I_a - R_{sr}\cdot I_a \qquad\quad I_t = I_a \qquad\quad V_t = R_L\cdot I_t$$

    Sem corrente de carga não há corrente de campo — e, portanto, praticamente nenhuma
    tensão gerada (apenas o pequeno efeito do magnetismo residual). À medida que a carga
    cresce, o fluxo cresce junto, e $V_t$ sobe seguindo a forma da curva de magnetização;
    em correntes elevadas, porém, a saturação do núcleo e a reação de armadura fazem a
    tensão **cair** novamente:
    """)

    show_fig(fig_caracteristica_serie(), 0.62)

    st.markdown(r"""
    Essa característica — tensão fortemente dependente da carga, sem nenhuma estabilidade
    a vazio — torna o gerador série **inadequado** para a maioria das aplicações que
    exigem tensão controlada, sendo raramente empregado como gerador autônomo na prática.
    Seu enrolamento série, no entanto, é o mesmo princípio construtivo reaproveitado no
    gerador composto (Seção 16), onde a contribuição do fluxo série é dosada para
    **complementar** — e não substituir — a excitação shunt.
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # EXPLORADORES INTERATIVOS
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("🎛️ Exploradores Interativos")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Explorador 1 — Tensão e Torque",
                                       "Explorador 2 — Curva de Magnetização",
                                       "Explorador 3 — Ondulação de Comutação",
                                       "Explorador 4 — Lap vs. Wave",
                                       "Explorador 5 — Regulação de Tensão",
                                       "Explorador 6 — Autoexcitação Shunt"])
    with tab1: exp_tensao_torque()
    with tab2: exp_magnetizacao()
    with tab3: exp_comutacao()
    with tab4: exp_enrolamentos()
    with tab5: exp_regulacao_tensao()
    with tab6: exp_autoexcitacao()

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # REFERÊNCIAS
    # ═══════════════════════════════════════════════════════════════════════════════
    with st.expander("Referências", expanded=False):
        st.markdown("""
    - **CHAPMAN, S. J.** *Fundamentos de Máquinas Elétricas*. 5ª ed. McGraw-Hill, 2013.
    - **UMANS, S. D.** *Máquinas Elétricas de Fitzgerald e Kingsley*. 7ª ed. McGraw-Hill, 2014.
    - **KOSOW, I.** *Máquinas Elétricas e Transformadores*. 14ª reimp. Globo, 2000.
    - **BIM, E.** *Máquinas Elétricas e Acionamento*. Campus Elsevier, 2009.
    - **SEN, P. C.** *Princípios de Máquinas Elétricas e Eletrônica de Potência*. 3ª ed. Wiley, 2013.
    - **JACOBINA, C.; LIMA, A. M.** *Acionamentos de Máquinas Elétricas de Alto Desempenho*. XIV CBA, Natal, 2002.
    """)

    st.divider()

    st.markdown(
        "<div style='text-align:center;color:gray;font-size:12px'>"
        "⚙️ Máquinas Elétricas de Corrente Contínua &nbsp;·&nbsp; ⚡ SINTONIA — Máquinas Elétricas<br>"
        "👤 Marcus V A Fernandes &nbsp;·&nbsp; 🏛️ IFRN-CNAT"
        " &nbsp;·&nbsp; 🏷️ v1.0 &nbsp;·&nbsp; 📅 2026"
        "</div>",
        unsafe_allow_html=True,
    )
