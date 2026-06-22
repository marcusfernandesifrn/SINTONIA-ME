"""
⚙️ Máquinas Elétricas de Corrente Contínua
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
import schemdraw
import schemdraw.elements as elm
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

    def _add_mech_load(fig, ax, Ea, ang_deg=235, shaft_len=1.85, label="Carga\nmecânica"):
        """Acrescenta um eixo + bloco de 'carga mecânica' (com seta de ωm) a um circuito de
        motor desenhado com schemdraw, ancorado no elemento Ea (Motor). Usado para mostrar a
        saída mecânica nos circuitos de motor CC, mantendo o estilo do desenho de referência."""
        cx, cy = Ea.center.x, Ea.center.y
        r = abs(Ea.end.y - Ea.start.y) / 2
        ang = np.radians(ang_deg)
        sx0, sy0 = cx + r*np.cos(ang), cy + r*np.sin(ang)
        sx1, sy1 = cx + (r+shaft_len)*np.cos(ang), cy + (r+shaft_len)*np.sin(ang)
        ax.plot([sx0, sx1], [sy0, sy1], color=TX, lw=2.2, zorder=4, solid_capstyle='round')
        box_w, box_h = 1.5, 0.85
        box_center = (sx1 - 0.55*np.cos(ang), sy1 - 0.55*np.sin(ang))
        rot = ang_deg - 180
        t = mtransforms.Affine2D().rotate_deg_around(box_center[0], box_center[1], rot) + ax.transData
        rect = mpatches.FancyBboxPatch((box_center[0]-box_w/2, box_center[1]-box_h/2), box_w, box_h,
                                        boxstyle="round,pad=0.02,rounding_size=0.05",
                                        fc="white", ec=TX, lw=1.4, zorder=5, transform=t)
        ax.add_patch(rect)
        ax.text(box_center[0], box_center[1], label, fontsize=8.5, color=TX,
                ha="center", va="center", zorder=6, rotation=rot, rotation_mode='anchor')
        mx, my = (sx0+sx1)/2, (sy0+sy1)/2
        perp = ang + np.radians(90)
        ox, oy = 0.25*np.cos(perp), 0.25*np.sin(perp)
        arc = np.linspace(np.radians(150), np.radians(40), 15)
        rr = 0.26
        ax.plot(mx+ox+rr*np.cos(arc), my+oy+rr*np.sin(arc), color=CZ, lw=1.2, zorder=6)
        ax.annotate("", xy=(mx+ox+rr*np.cos(arc[0]), my+oy+rr*np.sin(arc[0])),
                    xytext=(mx+ox+rr*np.cos(arc[2]), my+oy+rr*np.sin(arc[2])),
                    arrowprops=dict(arrowstyle="-|>", color=CZ, lw=1.2), zorder=6)
        ax.text(mx+ox-0.05, my+oy+0.42, "$\\omega_m$", fontsize=9.5, color=CZ, ha="center")
        # schemdraw fixa xlim/ylim a partir dos elementos do circuito; expandimos para caber
        # o bloco de carga mecânica acrescentado por cima, evitando que seja cortado
        diag = 0.5*(box_w+box_h)
        pts_x = [box_center[0]-diag, box_center[0]+diag]
        pts_y = [box_center[1]-diag, box_center[1]+diag]
        x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
        ax.set_xlim(min(x0, min(pts_x)-0.2), max(x1, max(pts_x)+0.2))
        ax.set_ylim(min(y0, min(pts_y)-0.2), max(y1, max(pts_y)+0.2))

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
            mark = "cross" if np.cos(a) < 0 else "dot"  # lado N: entrando; lado S: saindo — consistente com a convenção usada nas Seções 11 (Reação da Armadura) e 12 (Interpolos)
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
        """Comutador elementar de 2 segmentos: bobina única, escovas fixas B1/B2 no eixo q
        (neutro/interpolar — não no eixo dos polos), polos N/S no eixo d, terminais a/b."""
        fig, ax = _mpl_base((5.6, 5.6))
        ax.set_xlim(-4.2, 4.2); ax.set_ylim(-3.4, 3.4)

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
        ax.add_patch(mpatches.Wedge((0,0), R_com, 70, 250, width=R_com-0.18, fc="white", ec=TX, lw=1.3, zorder=7))
        ax.add_patch(mpatches.Wedge((0,0), R_com, 250, 70+360, width=R_com-0.18, fc="white", ec=TX, lw=1.3, zorder=7))
        ax.text(0, R_com-0.09, "$C_a$", fontsize=9, color=TX, ha="center", va="center", zorder=8)
        ax.text(0, -(R_com-0.09), "$C_b$", fontsize=9, color=TX, ha="center", va="center", zorder=8)

        # escovas B1 (topo) e B2 (base) — fixas no eixo q, entre os polos: é exatamente
        # onde e_ab passa por zero (Seção 4), garantindo comutação sem curto-circuitar
        # uma bobina com tensão induzida significativa
        bw, bh = 0.3, 0.85    # bw: espessura radial · bh: largura tangencial
        b_in = R_rot + 0.25
        ax.add_patch(mpatches.Rectangle((-bh/2, b_in), bh, bw, fc=LR, ec=TX, lw=1.2,
                                         hatch="//", alpha=.85, zorder=4))
        ax.add_patch(mpatches.Rectangle((-bh/2, -(b_in+bw)), bh, bw, fc=LR, ec=TX, lw=1.2,
                                         hatch="//", alpha=.85, zorder=4))
        ax.text(-bh/2-0.18, b_in+bw/2, "$B_1$", fontsize=11, color=TX, ha="right", va="center")
        ax.text(-bh/2-0.18, -(b_in+bw/2), "$B_2$", fontsize=11, color=TX, ha="right", va="center")

        # terminais a (+) e b (-) — tensão própria da bobina, e_ab
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

        # rotação n — deslocada para o vão entre a escova B1 e o polo S, sem sobrepor nada
        arc_n = np.linspace(np.radians(48), np.radians(8), 20)
        r_n = R_pole_in - 0.15
        ax.plot(r_n*np.cos(arc_n), r_n*np.sin(arc_n), color=TX, lw=1.4, zorder=6)
        ax.annotate("", xy=(r_n*np.cos(arc_n[0]), r_n*np.sin(arc_n[0])),
                    xytext=(r_n*np.cos(arc_n[2]), r_n*np.sin(arc_n[2])),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.4), zorder=6)
        ax.text(r_n*np.cos(np.radians(28))+0.05, r_n*np.sin(np.radians(28))+0.32,
                "n", fontsize=10.5, color=TX, ha="center")

        # saída externa e_12, via os terminais das escovas (eixo q)
        lead = 0.55
        ax.plot([0, 0], [b_in+bw, b_in+bw+lead], color=TX, lw=1.3, zorder=4)
        ax.plot([0, 0], [-(b_in+bw), -(b_in+bw+lead)], color=TX, lw=1.3, zorder=4)
        ax.add_patch(plt.Circle((0, b_in+bw+lead), .055, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.add_patch(plt.Circle((0, -(b_in+bw+lead)), .055, fc="white", ec=TX, lw=1.2, zorder=6))
        ax.text(0.26, b_in+bw+lead, "+", fontsize=11, color=TX, va="center")
        ax.text(0.26, -(b_in+bw+lead), "$-$", fontsize=11, color=TX, va="center")
        ax.text(0.95, 0, "$e_{12}$", fontsize=10.5, color=TX, ha="center", va="center")

        ax.set_title("Comutador elementar (2 segmentos)", fontsize=10.5, color=TX, pad=16)
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
        """Visão geral dos 5 esquemas de conexão do campo — independente, shunt, série,
        composto curto e composto longo — reaproveitando os circuitos schemdraw
        detalhados de cada tipo (Seções 14–17), compostos lado a lado em miniatura."""
        nomes_fig = [fig_gerador_independente_circuito, fig_gerador_shunt_circuito,
                     fig_gerador_serie_circuito, fig_gerador_composto_curto_circuito,
                     fig_gerador_composto_longo_circuito]
        titulos = ["(a) Independente", "(b) Shunt", "(c) Série",
                   "(d) Composto curto", "(e) Composto longo"]

        fig, axes = plt.subplots(1, 5, figsize=(15.5, 3.7))
        fig.patch.set_alpha(0)
        for ax, fn, titulo in zip(axes, nomes_fig, titulos):
            sub = fn()
            sub.canvas.draw()
            buf = np.asarray(sub.canvas.buffer_rgba())
            ax.imshow(buf)
            ax.axis("off")
            ax.set_title(titulo, fontsize=10.5, color=TX, pad=6)
            plt.close(sub)
        fig.tight_layout()
        return fig


    def fig_gerador_independente_circuito():
        """Circuito do gerador CC de excitação independente: malha de campo (Vf, Rfc, Rfw,
        Nf) isolada da malha de armadura (Ea, Ra) que alimenta a carga RL. Construído com
        schemdraw, fiel ao desenho de referência (MCC_Desenhos.ipynb)."""
        with schemdraw.Drawing() as d:
            d.config(unit=2.2)
            d.push()
            Nf = elm.Inductor().right().label('$N_f$').color(AZ)
            If = elm.Line().down().color(AZ)
            elm.Line().down().dot(open=True).color(AZ)
            d.pop()
            d.push()
            elm.Resistor().down().label('$R_{fw}$').color(AZ)
            elm.ResistorVar().down().label('$R_{fc}$').color(AZ).dot(open=True)
            elm.Gap().right().label(('+', '$V_f$', '-')).color(AZ)
            d.pop()

            d.move_from(Nf.end, dx=2, dy=1)
            d.push()
            Ea = elm.Motor().down().label('$E_a$').color(TX)
            elm.Line().down().color(TX)
            Vtm = elm.Line().right().dot(open=True).color(TX)
            d.pop()
            Ia = elm.Line().up().color(TX)
            Vtp = elm.Resistor().right().label('$R_a$').color(TX).dot(open=True)

            elm.Line().right().color(TX)
            elm.Line().down().color(TX)
            elm.ResistorVar().down().label('$R_L$').color(TX)
            elm.Line().down().color(TX)
            elm.Line().left().color(TX)

            elm.Gap().down().label(('+', '$V_t$', '-')).endpoints(Vtp.end, Vtm.end).color(TX)

            elm.CurrentLabel(top=False, length=1.25, ofst=.3).at(Ia).label('$I_a$').color(TX)
            elm.CurrentLabel(top=False, length=1.25, ofst=.3).at(If).label('$I_f$').color(AZ)

        fig = d.fig.getfig()
        fig.patch.set_alpha(0)
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
        """Circuito do gerador CC shunt (autoexcitado): campo (Nf, Rfw, Rfc) conectado em
        paralelo com a própria armadura (Ea, Ra), alimentando a carga RL. Construído com
        schemdraw, fiel ao desenho de referência (MCC_Desenhos.ipynb)."""
        with schemdraw.Drawing() as d:
            d.config(unit=2.2)
            d.push()
            Nf = elm.Inductor().right().label('$N_{f}$').color(AZ)
            If = elm.Line().up().color(AZ)
            Rfw = elm.Resistor().up().label('$R_{fw}$').color(AZ)
            elm.Line().right().dot(open=True).color(AZ)
            d.pop()
            elm.ResistorVar().down().label('$R_{fc}$').color(AZ)
            elm.Line().right().color(AZ)
            elm.Line().right().dot(open=True).color(AZ)
            d.push()
            Vtm = elm.Line().right().dot(open=True).color(TX)
            d.pop()
            elm.Line().up().color(TX)
            Ea = elm.Motor().up().label('$E_a$').color(TX)
            Ra = elm.Resistor().up().label('$R_{a}$').color(TX)
            Vtp = elm.Line().right().dot(open=True).color(TX)

            elm.Line().right().color(TX)
            elm.Line().down().color(TX)
            elm.ResistorVar().down().label('$R_{L}$').color(TX)
            elm.Line().down().color(TX)
            elm.Line().left().color(TX)

            elm.Gap().down().label(('+', '$V_t$', '-')).endpoints(Vtp.end, Vtm.end).color(TX)

            elm.CurrentLabel(top=False, length=1.25, ofst=.3).at(Ra).label('$I_a$').color(TX)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).reverse().at(If).label('$I_f$').color(AZ)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).at(Vtp).label('$I_t$').color(TX)

        fig = d.fig.getfig()
        fig.patch.set_alpha(0)
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


    def fig_gerador_composto_curto_circuito():
        """Circuito do gerador CC composto, ligação curta (short shunt): o campo shunt
        (Nf, Rfw, Rfc) é tomado em paralelo apenas com a armadura (Ea, Ra) — antes do
        enrolamento série (Nsr, Rsr). Construído com schemdraw, fiel ao desenho de
        referência (MCC_Desenhos.ipynb)."""
        with schemdraw.Drawing() as d:
            d.config(unit=2.2)
            d.push()
            Nf = elm.Inductor().right().label('$N_{f}$').color(AZ)
            Rfc = elm.ResistorVar().up().label('$R_{fc}$').color(AZ)
            If = elm.Line().right().dot(open=False).color(AZ)
            d.pop()
            Rfw = elm.Resistor().down().label('$R_{fw}$').color(AZ)
            elm.Line().right().color(TX)
            elm.Line().right().dot(open=False).color(TX)
            d.push()
            elm.Line().right().color(TX)
            elm.Line().right().color(TX)
            Vtm = elm.Line().right().dot(open=True).color(TX)
            d.pop()
            Ea = elm.Motor().up().label('$E_a$').color(TX)
            Ra = elm.Resistor().up().label('$R_{a}$').color(TX)
            Ns = elm.Inductor().right().label('$N_{sr}$').color(VD)
            Rs = elm.Resistor().right().label('$R_{sr}$').color(VD)
            Vtp = elm.Line().right().dot(open=True).color(TX)

            elm.Line().right().color(TX)
            elm.Line().down(length=1.0).color(TX)
            elm.ResistorVar().down().label('$R_{L}$').color(TX)
            elm.Line().toy(Vtm.end.y).color(TX)
            elm.Line().to(Vtm.end).color(TX)

            elm.Gap().down().label(('+', '$V_t$', '-')).endpoints(Vtp.end, Vtm.end).color(TX)

            elm.CurrentLabel(top=False, length=1.25, ofst=.3).at(Ra).label('$I_a$').color(TX)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).reverse().at(If).label('$I_f$').color(AZ)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).at(Vtp).label('$I_t$').color(TX)

        fig = d.fig.getfig()
        fig.patch.set_alpha(0)
        return fig


    def fig_gerador_composto_longo_circuito():
        """Circuito do gerador CC composto, ligação longa (long shunt): o campo shunt
        (Nf, Rfw, Rfc) é tomado em paralelo com a armadura somada ao enrolamento série
        (Ea, Ra, Nsr, Rsr). Construído com schemdraw, fiel ao desenho de referência
        (MCC_Desenhos.ipynb)."""
        with schemdraw.Drawing() as d:
            d.config(unit=2.2)
            d.push()
            Nf = elm.Inductor().right().label('$N_{f}$').color(AZ)
            elm.Line().up().color(AZ)
            Rfc = elm.ResistorVar().up().label('$R_{fc}$').color(AZ)
            elm.Line().right().color(AZ)
            Rfw = elm.Resistor().right().label('$R_{fw}$').color(AZ)
            If = elm.Line().right().color(AZ)
            elm.Line().down().dot(open=False).color(AZ)
            d.pop()
            elm.Line().down().color(TX)
            elm.Line().right().color(TX)
            elm.Line().right().dot(open=False).color(TX)
            d.push()
            elm.Line().right().color(TX)
            elm.Line().right().color(TX)
            Vtm = elm.Line().right().dot(open=True).color(TX)
            d.pop()
            Ea = elm.Motor().up().label('$E_a$').color(TX)
            Ra = elm.Resistor().up().label('$R_{a}$').color(TX)
            Ns = elm.Inductor().right().label('$N_{sr}$').color(VD)
            Rs = elm.Resistor().right().label('$R_{sr}$').color(VD)
            Vtp = elm.Line().right().dot(open=True).color(TX)

            elm.Line().right().color(TX)
            elm.Line().down(length=1.0).color(TX)
            elm.ResistorVar().down().label('$R_{L}$').color(TX)
            elm.Line().toy(Vtm.end.y).color(TX)
            elm.Line().to(Vtm.end).color(TX)

            elm.Gap().down().label(('+', '$V_t$', '-')).endpoints(Vtp.end, Vtm.end).color(TX)

            elm.CurrentLabel(top=False, length=1.25, ofst=.3).at(Ra).label('$I_a$').color(TX)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).reverse().at(If).label('$I_f$').color(AZ)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).at(Vtp).label('$I_t$').color(TX)

        fig = d.fig.getfig()
        fig.patch.set_alpha(0)
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
        """Circuito do gerador CC série: enrolamento de campo (Nsr, Rsr) em série com a
        armadura (Ea, Ra) e a carga RL — uma única malha de corrente. Construído com
        schemdraw, fiel ao desenho de referência (MCC_Desenhos.ipynb)."""
        with schemdraw.Drawing() as d:
            d.config(unit=2.2)
            d.push()
            Ea = elm.Motor().down().label('$E_a$').color(TX)
            elm.Line().right().color(TX)
            elm.Line().right().color(TX)
            elm.Line().right().color(TX)
            T2 = elm.Dot(open=True).color(TX)
            d.pop()
            Ra = elm.Resistor().up().label('$R_{a}$').color(TX)
            elm.Line().right().color(TX)
            elm.Line().down().color(TX)
            elm.Inductor().right().label('$N_{sr}$').color(VD)
            elm.Line().up().color(TX)
            elm.Resistor().right().label('$R_{sr}$').color(VD)
            T1 = elm.Dot(open=True).color(TX)
            elm.Line().right().color(TX)
            elm.Line().down(length=1.0).color(TX)
            elm.ResistorVar().down().label('$R_{L}$').color(TX)
            elm.Line().toy(T2.end.y).color(TX)
            elm.Line().to(T2.end).color(TX)

            elm.Gap().down().label(('+', '$V_t$', '-')).endpoints(T1.end, T2.end).color(TX)

            elm.CurrentLabel(top=False, length=1.25, ofst=.3).at(Ra).label('$I_a$').color(TX)

        fig = d.fig.getfig()
        fig.patch.set_alpha(0)
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
    # FIGURAS — OPERAÇÃO COMO MOTOR E CONTROLE DE VELOCIDADE (schemdraw + matplotlib)
    # ════════════════════════════════════════════════════════════════════════

    def fig_motor_shunt_circuito():
        """Circuito do motor CC shunt (campo em paralelo): convenção de motor — Ia, If e
        It entram pelos terminais — alimentando a armadura (Ea, Ra) e a carga mecânica
        acoplada ao eixo. Reaproveitado também para o controle por fluxo de campo."""
        with schemdraw.Drawing() as d:
            d.config(unit=2.2)
            d.push()
            Nf = elm.Inductor().right().label('$N_{f}$').color(AZ)
            If = elm.Line().up().color(AZ)
            Rfw = elm.Resistor().up().label('$R_{fw}$').color(AZ)
            elm.Line().right().dot(open=True).color(AZ)
            d.pop()
            elm.ResistorVar().down().label('$R_{fc}$').color(AZ)
            elm.Line().right().color(AZ)
            elm.Line().right().dot(open=True).color(AZ)
            d.push()
            Vtm = elm.Line().right().dot(open=True).color(TX)
            d.pop()
            elm.Line().up().color(TX)
            Ea = elm.Motor().up().label('$E_a$').color(TX)
            Ra = elm.Resistor().up().label('$R_{a}$').color(TX)
            Vtp = elm.Line().right().dot(open=True).color(TX)
            elm.Line().right().color(TX)
            elm.Line().toy(Vtm.end.y).color(TX)
            elm.Line().to(Vtm.end).color(TX)
            elm.Gap().down().label(('+', '$V_t$', '-')).endpoints(Vtp.end, Vtm.end).color(TX)
            elm.CurrentLabel(top=False, length=1.25, ofst=.3).reverse().at(Ra).label('$I_a$').color(TX)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).at(If).label('$I_f$').color(AZ)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).reverse().at(Vtp).label('$I_t$').color(TX)
        fig = d.fig.getfig()
        ax = fig.axes[0]
        _add_mech_load(fig, ax, Ea, ang_deg=235, shaft_len=1.85)
        fig.patch.set_alpha(0)
        return fig

    def fig_motor_independente_circuito():
        """Circuito do motor CC de excitação independente: malha de campo isolada
        (Vf, Rfc, Rfw, Nf) e malha de armadura (Ea, Ra) acoplada à carga mecânica."""
        with schemdraw.Drawing() as d:
            d.config(unit=2.2)
            d.push()
            Nf = elm.Inductor().right().label('$N_f$').color(AZ)
            If = elm.Line().down().color(AZ)
            elm.Line().down().dot(open=True).color(AZ)
            d.pop()
            d.push()
            elm.Resistor().down().label('$R_{fw}$').color(AZ)
            elm.ResistorVar().down().label('$R_{fc}$').color(AZ).dot(open=True)
            elm.Gap().right().label(('+', '$V_f$', '-')).color(AZ)
            d.pop()
            d.move_from(Nf.end, dx=2, dy=1)
            d.push()
            Ea = elm.Motor().down().label('$E_a$').color(TX)
            elm.Line().down().color(TX)
            Vtm = elm.Line().right().dot(open=True).color(TX)
            d.pop()
            Ia = elm.Line().up().color(TX)
            Vtp = elm.Resistor().right().label('$R_a$').color(TX).dot(open=True)
            elm.Line().right().color(TX)
            elm.Line().toy(Vtm.end.y).color(TX)
            elm.Line().to(Vtm.end).color(TX)
            elm.Gap().down().label(('+', '$V_t$', '-')).endpoints(Vtp.end, Vtm.end).color(TX)
            elm.CurrentLabel(top=False, length=1.25, ofst=.3).reverse().at(Ia).label('$I_a$').color(TX)
            elm.CurrentLabel(top=False, length=1.25, ofst=.3).at(If).label('$I_f$').color(AZ)
        fig = d.fig.getfig()
        ax = fig.axes[0]
        _add_mech_load(fig, ax, Ea, ang_deg=235, shaft_len=1.85)
        fig.patch.set_alpha(0)
        return fig

    def fig_motor_shunt_rae_circuito():
        """Motor shunt com resistência de armadura adicional (Rae) em série com Ra,
        para controle de velocidade por resistência de armadura."""
        with schemdraw.Drawing() as d:
            d.config(unit=2.2)
            d.push()
            Nf = elm.Inductor().right().label('$N_{f}$').color(AZ)
            If = elm.Line().up().color(AZ)
            Rfw = elm.Resistor().up().label('$R_{fw}$').color(AZ)
            elm.Line().up().color(AZ)
            elm.Line().right().dot(open=True).color(AZ)
            d.pop()
            elm.ResistorVar().down().label('$R_{fc}$').color(AZ)
            elm.Line().right().color(AZ)
            elm.Line().right().dot(open=True).color(AZ)
            d.push()
            Vtm = elm.Line().right().dot(open=True).color(TX)
            d.pop()
            elm.Line().up().color(TX)
            Ea = elm.Motor().up().label('$E_a$').color(TX)
            Ra = elm.Resistor().up().label('$R_{a}$').color(TX)
            Rae = elm.ResistorVar().up().label('$R_{ae}$').color(TX)
            Vtp = elm.Line().right().dot(open=True).color(TX)
            elm.Line().right().color(TX)
            elm.Line().toy(Vtm.end.y).color(TX)
            elm.Line().to(Vtm.end).color(TX)
            elm.Gap().down().label(('+', '$V_t$', '-')).endpoints(Vtp.end, Vtm.end).color(TX)
            elm.CurrentLabel(top=False, length=1.25, ofst=.3).reverse().at(Ra).label('$I_a$').color(TX)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).at(If).label('$I_f$').color(AZ)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).reverse().at(Vtp).label('$I_t$').color(TX)
        fig = d.fig.getfig()
        ax = fig.axes[0]
        _add_mech_load(fig, ax, Ea, ang_deg=235, shaft_len=1.85)
        fig.patch.set_alpha(0)
        return fig

    def fig_motor_serie_rae_circuito():
        """Motor série com resistência de armadura adicional (Rae): Ra+Rae em série com
        Ea e com o próprio enrolamento de campo série (Nsr, Rsr)."""
        with schemdraw.Drawing() as d:
            d.config(unit=2.2)
            d.push()
            Ea = elm.Motor().down().label('$E_a$').color(TX)
            elm.Line().right().color(TX)
            elm.Line().right().color(TX)
            elm.Line().right().color(TX)
            T2 = elm.Dot(open=True).color(TX)
            d.pop()
            Ra = elm.Resistor().up().label('$R_{a}$').color(TX)
            Rae = elm.ResistorVar().up().label('$R_{ae}$').color(TX)
            elm.Line().right().color(TX)
            elm.Line().down().color(TX)
            elm.Inductor().right().label('$N_{sr}$').color(VD)
            elm.Line().up().color(TX)
            elm.Resistor().right().label('$R_{sr}$').color(VD)
            T1 = elm.Dot(open=True).color(TX)
            elm.Line().right().color(TX)
            elm.Line().toy(T2.end.y).color(TX)
            elm.Line().to(T2.end).color(TX)
            elm.Gap().down().label(('+', '$V_t$', '-')).endpoints(T1.end, T2.end).color(TX)
            elm.CurrentLabel(top=False, length=1.25, ofst=.3).reverse().at(Ra).label('$I_a$').color(TX)
        fig = d.fig.getfig()
        ax = fig.axes[0]
        _add_mech_load(fig, ax, Ea, ang_deg=210, shaft_len=2.0)
        fig.patch.set_alpha(0)
        return fig

    def fig_motor_partida_circuito():
        """Motor shunt com resistor de partida (Rpartida) em série com a armadura,
        curto-circuitado gradualmente conforme o motor acelera."""
        with schemdraw.Drawing() as d:
            d.config(unit=2.2)
            d.push()
            Nf = elm.Inductor().right().label('$N_{f}$').color(AZ)
            If = elm.Line().up().color(AZ)
            Rfw = elm.Resistor().up().label('$R_{fw}$').color(AZ)
            elm.Line().up().color(AZ)
            elm.Line().right().dot(open=True).color(AZ)
            d.pop()
            elm.ResistorVar().down().label('$R_{fc}$').color(AZ)
            elm.Line().right().color(AZ)
            elm.Line().right().dot(open=True).color(AZ)
            d.push()
            Vtm = elm.Line().right().dot(open=True).color(TX)
            d.pop()
            elm.Line().up().color(TX)
            Ea = elm.Motor().up().label('$E_a$').color(TX)
            Ra = elm.Resistor().up().label('$R_{a}$').color(TX)
            Rp = elm.ResistorVar().up().label('$R_{partida}$').color(LR)
            Vtp = elm.Line().right().dot(open=True).color(TX)
            elm.Line().right().color(TX)
            elm.Line().toy(Vtm.end.y).color(TX)
            elm.Line().to(Vtm.end).color(TX)
            elm.Gap().down().label(('+', '$V_t$', '-')).endpoints(Vtp.end, Vtm.end).color(TX)
            elm.CurrentLabel(top=False, length=1.25, ofst=.3).reverse().at(Ra).label('$I_a$').color(TX)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).at(If).label('$I_f$').color(AZ)
        fig = d.fig.getfig()
        ax = fig.axes[0]
        _add_mech_load(fig, ax, Ea, ang_deg=235, shaft_len=1.85)
        ax.annotate("curto-circuitado\ngradualmente\napós a partida", xy=(Rp.center.x+0.15, Rp.center.y),
                    xytext=(Rp.center.x+1.4, Rp.center.y+0.9), fontsize=8, color=LR, ha="left",
                    arrowprops=dict(arrowstyle="-|>", color=LR, lw=1.0))
        fig.patch.set_alpha(0)
        return fig

    def fig_eficiencia_circuito():
        """Circuito da máquina composta usado para a análise de eficiência (convenção de
        motor: Ia, If, It entrando pelos terminais; basta inverter as setas para a
        convenção de gerador)."""
        with schemdraw.Drawing() as d:
            d.config(unit=2.2)
            d.push()
            Nf = elm.Inductor().right().label('$N_{f}$').color(AZ)
            elm.Line().up().color(AZ)
            Rfc = elm.ResistorVar().up().label('$R_{fc}$').color(AZ)
            elm.Line().right().color(AZ)
            Rfw = elm.Resistor().right().label('$R_{fw}$').color(AZ)
            If = elm.Line().right().color(AZ)
            elm.Line().down().dot(open=False).color(AZ)
            d.pop()
            elm.Line().down().color(TX)
            elm.Line().right().color(TX)
            elm.Line().right().dot(open=False).color(TX)
            d.push()
            elm.Line().right().color(TX)
            elm.Line().right().color(TX)
            Vtm = elm.Line().right().dot(open=True).color(TX)
            d.pop()
            Ea = elm.Motor().up().label('$E_a$').color(TX)
            Ra = elm.Resistor().up().label('$R_{a}$').color(TX)
            Va = elm.Dot(open=False).color(TX)
            Nsr = elm.Inductor().right().label('$N_{sr}$').color(VD)
            Rsr = elm.Resistor().right().label('$R_{sr}$').color(VD)
            Vtp = elm.Line().right().dot(open=True).color(TX)
            elm.Line().right().color(TX)
            elm.Line().toy(Vtm.end.y).color(TX)
            elm.Line().to(Vtm.end).color(TX)
            elm.Gap().down().label(('+', '$V_t$', '-')).endpoints(Vtp.end, Vtm.end).color(TX)
            elm.CurrentLabel(top=False, length=1.25, ofst=.3).reverse().at(Ra).label('$I_a$').color(TX)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).at(If).label('$I_f$').color(AZ)
            elm.CurrentLabel(top=True, length=1.25, ofst=.3).reverse().at(Vtp).label('$I_t$').color(TX)
        fig = d.fig.getfig()
        ax = fig.axes[0]
        _add_mech_load(fig, ax, Ea, ang_deg=238, shaft_len=1.5)
        fig.patch.set_alpha(0)
        return fig

    def fig_motor_malha_fechada_diagrama():
        """Diagrama de blocos do controle em malha fechada (cascata velocidade→corrente)
        de um acionamento de motor CC."""
        fig, ax = plt.subplots(figsize=(12, 5.6))
        fig.patch.set_alpha(0); ax.set_facecolor("none")
        ax.set_xlim(-0.5, 14.2); ax.set_ylim(-3.0, 3.0)
        ax.axis("off"); ax.set_aspect("equal")

        def box(x, y, w, h, text, fontsize=9.5):
            ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.04",
                                                  fc="white", ec=TX, lw=1.4, zorder=4))
            ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fontsize, color=TX, zorder=5)

        def arrow(x0, y0, x1, y1, color=TX, lw=1.4):
            ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw), zorder=3)

        def sumjunction(x, y, r=0.22, signs=("+", "-"), positions=("left", "bottom")):
            ax.add_patch(plt.Circle((x, y), r, fc="white", ec=TX, lw=1.4, zorder=4))
            ax.text(x, y, "$\\Sigma$", ha="center", va="center", fontsize=10, color=TX, zorder=5)
            offs = {"left": (-r-0.13, 0.1), "bottom": (-0.08, -r-0.18), "top": (-0.08, r+0.05)}
            for s, p in zip(signs, positions):
                dx, dy = offs[p]
                ax.text(x+dx, y+dy, s, fontsize=9, color=TX, zorder=5, ha="center")

        y0 = 0.8
        ax.text(-0.4, y0, "$N^{*}$", fontsize=11, color=TX, ha="right", va="center")
        arrow(-0.25, y0, 0.55, y0)
        sumjunction(0.85, y0, signs=("+", "-"), positions=("top", "bottom"))
        arrow(1.07, y0, 1.55, y0)
        box(1.6, y0-0.4, 1.7, 0.8, "Controlador\nde velocidade", fontsize=8.5)
        arrow(3.3, y0, 3.85, y0)
        ax.text(3.55, y0+0.28, "$I_a^{*}$", fontsize=9.5, color=TX, ha="center")
        sumjunction(4.15, y0, signs=("+", "-"), positions=("top", "bottom"))
        arrow(4.37, y0, 4.85, y0)
        box(4.9, y0-0.4, 1.7, 0.8, "Controlador\nde corrente", fontsize=8.5)
        arrow(6.6, y0, 7.15, y0)
        ax.text(6.85, y0+0.28, "$V_c$", fontsize=9.5, color=TX, ha="center")
        box(7.2, y0-0.4, 1.5, 0.8, "Conversor", fontsize=9)
        arrow(8.7, y0, 9.25, y0)
        ax.text(8.97, y0+0.28, "$V_t$", fontsize=9.5, color=TX, ha="center")
        arrow(7.95, 2.1, 7.95, y0+0.42)
        ax.text(7.95, 2.3, "Fonte de\nalimentação", fontsize=8, color=CZ, ha="center", va="bottom")
        box(9.3, y0-0.4, 1.4, 0.8, "Motor", fontsize=9.5)
        arrow(10.7, y0, 11.25, y0)
        ax.text(10.97, y0+0.28, "$N$", fontsize=9.5, color=TX, ha="center")
        box(11.3, y0-0.4, 1.2, 0.8, "Carga", fontsize=9.5)

        ax.plot([9.95, 9.95], [y0-0.4, -1.15], color=TX, lw=1.3, zorder=3)
        ax.text(10.1, -0.85, "$I_a$", fontsize=9, color=TX)
        ax.plot([9.95, 6.5], [-1.15, -1.15], color=TX, lw=1.3, zorder=3)
        box(5.95, -1.45, 0.85, 0.6, "$K$", fontsize=9.5)
        arrow(5.95, -1.15, 4.37, -1.15)
        ax.plot([4.15, 4.15], [-1.15, y0-0.22], color=TX, lw=1.3, zorder=3)
        arrow(4.15, -0.5, 4.15, y0-0.23)

        ax.plot([11.0, 11.0], [y0-0.4, -2.35], color=TX, lw=1.3, zorder=3)
        ax.plot([11.0, 2.95], [-2.35, -2.35], color=TX, lw=1.3, zorder=3)
        box(2.0, -2.65, 1.55, 0.6, "Realimentação", fontsize=8.2)
        arrow(2.0, -2.35, 0.85, -2.35)
        ax.plot([0.85, 0.85], [-2.35, y0-0.22], color=TX, lw=1.3, zorder=3)
        arrow(0.85, -0.5, 0.85, y0-0.23)
        ax.text(0.55, -1.3, "$N$", fontsize=9, color=TX)

        fig.tight_layout()
        return fig

    def fig_caracteristica_torque_velocidade_tipos():
        """Comparação da característica ωm × T para os quatro tipos de motor CC."""
        fig, ax = plt.subplots(figsize=(7.0, 4.8))
        fig.patch.set_alpha(0); ax.set_facecolor("none")

        T = np.linspace(0, 10, 200)
        w0 = 10.0
        w_sep = w0 - 0.45*T
        w_cum = w0 - 0.10*T - 0.075*T**2
        w_dif = w0 + 0.30*np.sqrt(T)
        w_ser = w0/np.sqrt(1+0.55*T)
        w_ser[0] = w0

        ax.plot(T, w_dif, color=VD, lw=2.2)
        ax.plot(T, w_sep, color=AZ, lw=2.2)
        ax.plot(T, w_cum, color=LR, lw=2.2)
        ax.plot(T, w_ser, color=RX, lw=2.2)
        ax.plot(T, np.full_like(T, w0), color=CZ, lw=1.0, ls="--")

        ax.text(10.2, w_dif[-1], "Composto\ndiferencial", fontsize=9.5, color=VD, va="center")
        ax.text(7.7, w_sep[154], "Excitação\nindependente", fontsize=9.5, color=AZ, va="center")
        ax.text(5.6, w_cum[112]+0.6, "Composto\ncumulativo", fontsize=9.5, color=LR, va="bottom")
        ax.text(3.0, w_ser[60]-1.0, "Série", fontsize=9.5, color=RX, va="top")

        ax.set_xlim(0, 14.5); ax.set_ylim(0, 13.0)
        ax.set_xlabel("$T$", fontsize=11, color=TX)
        ax.set_ylabel("$\\omega_m$", fontsize=11, color=TX)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.set_xticks([]); ax.set_yticks([])
        ax.spines["left"].set_position(("data", 0))
        ax.spines["bottom"].set_position(("data", 0))
        fig.tight_layout()
        return fig

    def fig_regulacao_velocidade_def():
        """Ilustra a definição de regulação de velocidade: ωm,sc (vazio) e ωm,nom
        (carga nominal) sobre a reta característica ωm × T."""
        fig, ax = plt.subplots(figsize=(6.6, 4.6))
        fig.patch.set_alpha(0); ax.set_facecolor("none")

        T = np.linspace(0, 10, 200)
        w_sc = 10.0
        T_nom = 8.0
        w = w_sc - 0.2*T
        wn = w_sc - 0.2*T_nom

        ax.plot(T, w, color=AZ, lw=2.4)
        ax.plot([T_nom, T_nom], [0, wn], color=CZ, lw=1.0, ls=":")
        ax.plot([0, T_nom], [wn, wn], color=CZ, lw=1.0, ls=":")
        ax.plot(0, w_sc, marker="o", color=TX, ms=6, zorder=5)
        ax.plot(T_nom, wn, marker="o", color=TX, ms=6, zorder=5)

        ax.annotate("", xy=(-0.55, wn), xytext=(-0.55, w_sc),
                    arrowprops=dict(arrowstyle="<->", color=RX, lw=1.3))
        ax.text(-0.95, (wn+w_sc)/2, "$\\Delta\\omega_m$", fontsize=10.5, color=RX, ha="center", va="center")
        ax.text(-0.25, w_sc, "$\\omega_{m,sc}$", fontsize=10.5, color=TX, ha="right", va="center")
        ax.text(-0.25, wn, "$\\omega_{m,nom}$", fontsize=10.5, color=TX, ha="right", va="center")
        ax.text(T_nom, -0.55, "$T_{nom}$", fontsize=10.5, color=TX, ha="center")

        ax.set_xlim(-2.3, 11); ax.set_ylim(0, 11.3)
        ax.set_xlabel("$T$", fontsize=11, color=TX)
        ax.set_ylabel("$\\omega_m$", fontsize=11, color=TX)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.set_xticks([]); ax.set_yticks([])
        ax.spines["left"].set_position(("data", 0))
        ax.spines["bottom"].set_position(("data", 0))
        fig.tight_layout()
        return fig

    def fig_motor_linear_tv():
        """Reta ωm × T (ou Ia) do motor de excitação independente/shunt, com a
        inclinação Ra/(KaΦ)² destacada."""
        fig, ax = plt.subplots(figsize=(6.6, 4.4))
        fig.patch.set_alpha(0); ax.set_facecolor("none")

        T = np.linspace(0, 10, 50)
        w0 = 9.5
        w = w0 - 0.55*T

        ax.plot(T, w, color=AZ, lw=2.6)
        ax.plot(0, w0, marker="o", color=TX, ms=6, zorder=5)
        ax.plot(T[-1], w[-1], marker="o", color=TX, ms=6, zorder=5)

        ax.annotate("", xy=(2.6, w0-0.55*2.6-0.35), xytext=(1.7, w0-0.55*1.7+0.65),
                    arrowprops=dict(arrowstyle="-|>", color=CZ, lw=1.2, connectionstyle="arc3,rad=-0.35"))
        ax.text(6.0, w0-0.55*4.6+0.3, "Inclinação $\\dfrac{R_a}{(K_a\\Phi)^2}$", fontsize=11, color=TX, va="center")

        ax.set_xlim(-0.6, 11); ax.set_ylim(0, 10.6)
        ax.set_xlabel("$T,\\ I_a$", fontsize=11, color=TX)
        ax.set_ylabel("$\\omega_m$", fontsize=11, color=TX)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.set_xticks([]); ax.set_yticks([])
        ax.spines["left"].set_position(("data", 0))
        ax.spines["bottom"].set_position(("data", 0))
        fig.tight_layout()
        return fig

    def fig_motor_tensao_painel():
        """Controle por tensão terminal: (a) ωm × Vt para diferentes torques;
        (b) ωm × T para diferentes tensões terminais (retas paralelas deslocadas)."""
        fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.6))
        fig.patch.set_alpha(0)

        ax = axes[0]
        ax.set_facecolor("none")
        Vt = np.linspace(0, 10, 50)
        Ts = [0, 2.0, 4.0]
        labels = ["$T=0$", "$T_1$", "$T_2$"]
        colors = [TX, AZ, "#7fb2ee"]
        for Tv, c, lb in zip(Ts, colors, labels):
            w = np.clip(Vt - Tv*0.55, 0, None)
            ax.plot(Vt, w, color=c, lw=2.2)
            ax.text(Vt[-1]*0.62, (Vt[-1]*0.62-Tv*0.55)+0.35, lb, fontsize=9.5, color=c, ha="center")
        ax.set_xlim(0, 11); ax.set_ylim(0, 12.5)
        ax.set_xlabel("$V_t$", fontsize=10.5, color=TX); ax.set_ylabel("$\\omega_m$", fontsize=10.5, color=TX)
        ax.text(0.3, 11.6, "(a)", fontsize=10, color=CZ)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.set_xticks([]); ax.set_yticks([])

        ax = axes[1]
        ax.set_facecolor("none")
        T = np.linspace(0, 7, 50)
        Vts = [10.0, 8.2, 6.4, 4.6]
        labels = ["$V_{t1}$", "$V_{t2}$", "$V_{t3}$", "$V_{t4}$"]
        colors = [TX, AZ, "#6fa8e8", "#aecdf2"]
        for Vtv, c, lb in zip(Vts, colors, labels):
            w = Vtv - 0.35*T
            ax.plot(T, w, color=c, lw=2.2)
            ax.text(T[-1]+0.2, w[-1], lb, fontsize=9.5, color=c, va="center")
        ax.annotate("", xy=(3.6, 9.2), xytext=(3.6, 4.2), arrowprops=dict(arrowstyle="-|>", color=CZ, lw=1.1))
        ax.text(3.85, 6.5, "$V_t$", fontsize=10, color=CZ)
        ax.set_xlim(0, 8.8); ax.set_ylim(0, 12.5)
        ax.set_xlabel("$T$", fontsize=10.5, color=TX)
        ax.text(0.2, 11.6, "(b)", fontsize=10, color=CZ)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.set_xticks([]); ax.set_yticks([])

        fig.tight_layout()
        return fig

    def fig_motor_campo_curva():
        """Curva ωm × If do controle por fluxo de campo: do reostato Rfc máximo
        (menor If, maior ωm) até Rfc = 0 (maior If, menor ωm)."""
        fig, ax = plt.subplots(figsize=(6.2, 4.6))
        fig.patch.set_alpha(0); ax.set_facecolor("none")

        If = np.linspace(2.4, 6.0, 100)
        w = 3.0 + 18.0/If

        ax.plot(If, w, color=AZ, lw=2.6)
        ax.plot(If[0], w[0], marker="o", color=TX, ms=6, zorder=5)
        ax.plot(If[-1], w[-1], marker="o", color=TX, ms=6, zorder=5)

        ax.annotate("$R_{fc,max}$", xy=(If[0], w[0]), xytext=(If[0]+0.8, w[0]+0.5),
                    fontsize=10.5, color=TX, arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.0,
                                                               connectionstyle="arc3,rad=0.3"))
        ax.annotate("$R_{fc}=0$", xy=(If[-1], w[-1]), xytext=(If[-1]+0.15, w[-1]+1.4),
                    fontsize=10.5, color=TX, arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.0,
                                                               connectionstyle="arc3,rad=0.25"))

        ax.set_xlim(0, 7.6); ax.set_ylim(0, 11.0)
        ax.set_xlabel("$I_f$", fontsize=11, color=TX)
        ax.set_ylabel("$\\omega_m$", fontsize=11, color=TX)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.set_xticks([]); ax.set_yticks([])
        fig.tight_layout()
        return fig

    def fig_motor_campo_familia_combinado():
        """(esquerda) Família de retas ωm × T para diferentes correntes de campo;
        (direita) estratégia combinada Vt (torque constante) + If (potência
        constante), em torno de ωbase."""
        fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.6))
        fig.patch.set_alpha(0)

        ax = axes[0]
        ax.set_facecolor("none")
        T = np.linspace(0, 10, 50)
        Ifs = [1.0, 1.22, 1.5, 1.9]
        colors = [TX, AZ, "#6fa8e8", "#aecdf2"]
        labels = ["$I_{f1}$", "$I_{f2}$", "$I_{f3}$", "$I_{f4}$"]
        for i, (If_, c) in enumerate(zip(Ifs, colors)):
            w0 = 4.0 + 7.0/If_
            slope = 0.15/If_
            w = w0 - slope*T
            ax.plot(T, w, color=c, lw=2.2)
            ax.text(T[-1]+0.2, w[-1], labels[i], fontsize=9.5, color=c, va="center")
        ax.annotate("$R_{fc}=0$", xy=(1.6, 4.0+7.0/Ifs[0]-0.15/Ifs[0]*1.6), xytext=(0.4, 3.0),
                    fontsize=9, color=TX, arrowprops=dict(arrowstyle="-|>", color=TX, lw=0.9))
        ax.annotate("$R_{fc}\\,máx$", xy=(1.6, 4.0+7.0/Ifs[-1]-0.15/Ifs[-1]*1.6), xytext=(3.4, 10.6),
                    fontsize=9, color=TX, arrowprops=dict(arrowstyle="-|>", color=TX, lw=0.9))
        ax.set_xlim(0, 13.5); ax.set_ylim(0, 12.2)
        ax.set_xlabel("$T$", fontsize=10.5, color=TX); ax.set_ylabel("$\\omega_m$", fontsize=10.5, color=TX)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.set_xticks([]); ax.set_yticks([])

        ax = axes[1]
        ax.set_facecolor("none")
        wbase = 5.0
        w1 = np.linspace(0, wbase, 60)
        T1 = np.full_like(w1, 8.0)
        P1 = (8.0/wbase)*w1
        w2 = np.linspace(wbase, 9.5, 60)
        P2 = np.full_like(w2, 8.0)
        T2 = 8.0*wbase/w2
        ax.plot(w1, T1, color=TX, lw=2.2)
        ax.plot(w2, T2, color=TX, lw=2.2)
        ax.plot(w1, P1, color=LR, lw=2.2)
        ax.plot(w2, P2, color=LR, lw=2.2)
        ax.axvline(wbase, color=CZ, lw=1.0, ls="--")
        ax.text(wbase, -0.7, "$\\omega_{base}$", fontsize=9.5, color=TX, ha="center")
        ax.text(wbase/2, 8.5, "$T$", fontsize=10, color=TX, ha="center")
        ax.text(wbase+2.0, 5.0, "$T$", fontsize=10, color=TX, ha="center")
        ax.text(wbase/2, 3.0, "$P$", fontsize=10, color=LR, ha="center")
        ax.text(wbase+2.0, 8.9, "$P$", fontsize=10, color=LR, ha="center")
        ax.annotate("", xy=(wbase-0.15, 9.7), xytext=(0.15, 9.7), arrowprops=dict(arrowstyle="<->", color=CZ, lw=1.0))
        ax.text(wbase/2, 10.0, "Controle por $V_t$\n(torque constante)", fontsize=8, color=CZ, ha="center")
        ax.annotate("", xy=(9.3, 9.7), xytext=(wbase+0.15, 9.7), arrowprops=dict(arrowstyle="<->", color=CZ, lw=1.0))
        ax.text(wbase+2.2, 10.0, "Controle por $I_f$\n(potência constante)", fontsize=8, color=CZ, ha="center")
        ax.set_xlim(0, 9.8); ax.set_ylim(0, 10.8)
        ax.set_xlabel("$\\omega_m$", fontsize=10.5, color=TX)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.set_xticks([]); ax.set_yticks([])

        fig.tight_layout()
        return fig

    def fig_motor_rae_familia():
        """(esquerda) Família de retas ωm × T para Rae crescente, todas convergindo
        para a mesma velocidade a vazio; (direita) T constante e P decrescente
        conforme Rae aumenta."""
        fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.6))
        fig.patch.set_alpha(0)

        ax = axes[0]
        ax.set_facecolor("none")
        T = np.linspace(0, 10, 50)
        w0 = 10.0
        Raes = [0, 0.35, 0.75, 1.25]
        colors = [TX, AZ, "#6fa8e8", "#aecdf2"]
        for Rae, c in zip(Raes, colors):
            slope = 0.45 + Rae*0.85
            w = w0 - slope*T
            ax.plot(T, w, color=c, lw=2.2)
        ax.annotate("$R_{ae}=0$", xy=(8.5, w0-0.45*8.5), xytext=(9.6, w0-0.45*8.5+0.6),
                    fontsize=9, color=TX, arrowprops=dict(arrowstyle="-|>", color=TX, lw=0.9))
        ax.annotate("$R_{ae}\\,máx$", xy=(3.2, w0-(0.45+1.25*0.85)*3.2), xytext=(4.6, 3.2),
                    fontsize=9, color=TX, arrowprops=dict(arrowstyle="-|>", color=TX, lw=0.9))
        ax.set_xlim(0, 11.5); ax.set_ylim(0, 11)
        ax.set_xlabel("$T$", fontsize=10.5, color=TX); ax.set_ylabel("$\\omega_m$", fontsize=10.5, color=TX)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.set_xticks([]); ax.set_yticks([])

        ax = axes[1]
        ax.set_facecolor("none")
        Rae_ax = np.linspace(0, 10, 50)
        T_curve = np.full_like(Rae_ax, 8.0)
        P_curve = 8.0 - 0.55*Rae_ax
        ax.plot(Rae_ax, T_curve, color=TX, lw=2.2)
        ax.plot(Rae_ax, P_curve, color=LR, lw=2.2)
        ax.text(8.5, 8.4, "$T$", fontsize=10.5, color=TX)
        ax.text(8.5, P_curve[-2]-0.9, "$P$", fontsize=10.5, color=LR)
        ax.set_xlim(0, 11); ax.set_ylim(0, 10)
        ax.set_xlabel("$R_{ae}$", fontsize=10.5, color=TX)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.set_xticks([]); ax.set_yticks([])

        fig.tight_layout()
        return fig

    def fig_motor_serie_rae_curvas():
        """Família de curvas hiperbólicas ωm × T do motor série, para Rae crescente
        (Vt constante): torques altos em baixas velocidades."""
        fig, ax = plt.subplots(figsize=(6.8, 4.8))
        fig.patch.set_alpha(0); ax.set_facecolor("none")

        T = np.linspace(0.4, 10, 100)
        Raes = [0, 0.3, 0.7, 1.3, 2.2]
        colors = [TX, AZ, "#5b9bea", "#8fbdf0", "#bdd9f7"]
        for Rae, c in zip(Raes, colors):
            w = 9.0/np.sqrt(T) - 0.55 - Rae*0.55
            w = np.clip(w, 0, None)
            ax.plot(T, w, color=c, lw=2.2)

        ax.annotate("$R_{ae}=0$", xy=(2.0, 9.0/np.sqrt(2.0)-0.55), xytext=(2.7, 8.6),
                    fontsize=9.5, color=TX, arrowprops=dict(arrowstyle="-|>", color=TX, lw=0.9))
        ax.annotate("$R_{ae}$", xy=(1.1, 9.0/np.sqrt(1.1)-0.55-2.2*0.55), xytext=(0.35, 2.3),
                    fontsize=9.5, color=TX, arrowprops=dict(arrowstyle="-|>", color=TX, lw=0.9,
                                                               connectionstyle="arc3,rad=-0.3"))
        ax.text(7.0, 5.3, "$V_t = $ constante", fontsize=9.5, color=CZ)

        ax.set_xlim(0, 10.5); ax.set_ylim(0, 10)
        ax.set_xlabel("$T$", fontsize=11, color=TX)
        ax.set_ylabel("$\\omega_m$", fontsize=11, color=TX)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(TX); ax.spines["bottom"].set_color(TX)
        ax.set_xticks([]); ax.set_yticks([])
        fig.tight_layout()
        return fig

    def fig_eficiencia_fluxo_potencia():
        """Fluxo de potência do gerador (acima) e do motor (abaixo): perdas
        rotacionais, de armadura, de campo shunt e de campo série subtraídas
        progressivamente da potência de entrada."""
        def panel(ax, mode="motor"):
            y_lines = [0.9, 0.6, 0.3]
            x0, x1 = 0.5, 9.5
            for y in y_lines:
                ax.plot([x0, x1], [y, y], color=TX, lw=1.6, zorder=2)
            ax.annotate("", xy=(x1+0.4, 0.6), xytext=(x1, 0.6),
                        arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.6))
            if mode == "motor":
                in_label = "$P_{input}$\n$=P_{elétrica}$\n$=V_tI_t$"
                out_label = "$P_{output}$\n$=P_{mecânica}$\n$=P_{eixo}$"
                loss_labels = ["$I_t^2R_{sr}$\n1–2%", "$I_f^2R_f$\n1–5%", "$I_a^2R_a$\n2–4%",
                                "Perdas\nrotacionais\n3–15%"]
            else:
                in_label = "$P_{input}$\n$=P_{mecânica}$\n$=P_{eixo}$"
                out_label = "$P_{output}$\n$=P_{elétrica}$\n$=V_tI_t$"
                loss_labels = ["Perdas\nrotacionais\n3–15%", "$I_a^2R_a$\n2–4%", "$I_f^2R_f$\n1–5%",
                                "$I_t^2R_{sr}$\n1–2%"]
            loss_x = [1.6, 3.7, 5.8, 7.6]
            ax.text(x0-0.15, 0.6, in_label, fontsize=8.5, color=TX, ha="right", va="center")
            ax.text(x1+0.55, 0.6, out_label, fontsize=8.5, color=TX, ha="left", va="center")
            for lx, lb in zip(loss_x, loss_labels):
                ax.annotate("", xy=(lx, -0.55), xytext=(lx, 0.85),
                            arrowprops=dict(arrowstyle="-|>", color=LR, lw=1.3))
                ax.text(lx, -0.75, lb, fontsize=7.6, color=LR, ha="center", va="top")
            ax.set_xlim(-2.3, 11.5); ax.set_ylim(-1.9, 1.3)
            ax.axis("off")
            title = ("Motor (entrada elétrica → saída mecânica)" if mode == "motor"
                      else "Gerador (entrada mecânica → saída elétrica)")
            ax.set_title(title, fontsize=10, color=TX, pad=4)

        fig, axes = plt.subplots(2, 1, figsize=(10.5, 6.6))
        fig.patch.set_alpha(0)
        for ax in axes: ax.set_facecolor("none")
        panel(axes[0], mode="gerador")
        panel(axes[1], mode="motor")
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

    Motores CC de grande potência acionam cargas como laminadores, guindastes, esteiras
    transportadoras e máquinas de papel — aplicações em que o controle fino de velocidade e
    torque é decisivo. Motores CC de pequeno porte são amplamente empregados como
    **dispositivos de controle** (servomotores, atuadores) em malhas de automação.

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

    $$V_f = R_f\cdot I_f \qquad\quad V_t = E_a - R_a\cdot I_a \qquad\quad E_a = K_a\,\Phi\,\omega_m \qquad\quad I_a = I_t \qquad\quad V_t = R_L\cdot I_t$$

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

    $$V_t = E_a - R_a\cdot I_a \qquad\quad V_f = V_t = R_f\cdot I_f \qquad\quad I_a = I_t + I_f \qquad\quad V_t = R_L\cdot I_t$$

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

    col_curto, col_longo = st.columns(2)
    with col_curto:
        st.markdown("<p style='text-align:center;'><b>Ligação curta</b> (short shunt)</p>",
                    unsafe_allow_html=True)
        show_fig(fig_gerador_composto_curto_circuito(), 1.0)
    with col_longo:
        st.markdown("<p style='text-align:center;'><b>Ligação longa</b> (long shunt)</p>",
                    unsafe_allow_html=True)
        show_fig(fig_gerador_composto_longo_circuito(), 1.0)

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
    # SEÇÃO 18 — OPERAÇÃO COMO MOTOR
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("18. Operação como Motor")

    st.markdown(r"""
    Até aqui tratamos a máquina CC como **gerador**: energia mecânica entra pelo eixo e
    energia elétrica sai pelos terminais. A mesma máquina, com a mesma estrutura física,
    opera igualmente bem como **motor** — basta inverter o sentido do fluxo de potência.
    Os circuitos equivalentes permanecem os mesmos; o que muda é a convenção de sinais:
    $I_a$, $I_f$ e $I_t$ passam a **entrar** pelos terminais, alimentados por uma fonte
    externa $V_t$, e a máquina entrega potência mecânica à carga acoplada ao seu eixo.

    O exemplo abaixo mostra um motor CC com enrolamento de campo em paralelo (shunt):
    """)

    show_fig(fig_motor_shunt_circuito(), 0.62)

    st.markdown(r"""
    $$V_f = V_t \qquad\quad V_t = R_a\cdot I_a + E_a \qquad\quad I_t = I_a + I_f \qquad\quad E_a = K_a\,\Phi\,\omega_m \qquad\quad V_f = R_f\cdot I_f$$

    Note a diferença em relação ao gerador: agora $V_t$ é **imposta** pela fonte externa,
    e a malha de armadura satisfaz $V_t = E_a + R_a\cdot I_a$ — a tensão aplicada é maior
    que a força contraeletromotriz $E_a$, com a diferença caindo sobre $R_a$. É essa
    diferença $(V_t - E_a)$, dividida por $R_a$, que determina a corrente de armadura e,
    por consequência, o torque desenvolvido no eixo.
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 19 — CARACTERÍSTICA TORQUE-VELOCIDADE E REGULAÇÃO DE VELOCIDADE
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("19. Característica Torque-Velocidade e Regulação de Velocidade")

    st.markdown(r"""
    A forma como a velocidade $\omega_m$ varia com o torque de carga $T$ depende do tipo
    de excitação do motor. Comparando os quatro tipos lado a lado:
    """)

    show_fig(fig_caracteristica_torque_velocidade_tipos(), 0.66)

    st.markdown(r"""
    - **Excitação independente (ou shunt)**: queda suave, aproximadamente linear — o fluxo
      $\Phi$ é mantido praticamente constante, e apenas a queda $R_a\cdot I_a$ reduz a
      velocidade com a carga.
    - **Composto cumulativo**: o enrolamento série reforça o campo shunt conforme $I_a$
      cresce, acentuando a queda de velocidade.
    - **Composto diferencial**: o enrolamento série se opõe ao shunt, enfraquecendo o
      fluxo total com a carga — tendendo a **elevar** a velocidade (efeito instável,
      raramente desejado).
    - **Série**: fluxo proporcional à própria corrente de armadura — característica mais
      acentuada, com altíssimo torque de partida e velocidade que cresce sem limite teórico
      quando a carga se aproxima de zero. Por isso, **nunca deve operar sem carga mecânica**
      acoplada.

    Essa sensibilidade da velocidade à carga é quantificada pela **regulação de
    velocidade**:
    """)

    show_fig(fig_regulacao_velocidade_def(), 0.58)

    st.markdown(r"""
    $$R_{\omega_m} = \dfrac{\omega_{m,sc} - \omega_{m,nom}}{\omega_{m,nom}}$$

    em que $\omega_{m,sc}$ é a velocidade angular a vazio (sem carga) e $\omega_{m,nom}$
    é a velocidade na carga nominal. Quanto **menor** a regulação, mais "rígida" é a
    velocidade do motor frente a variações de carga — característica desejável na maioria
    das aplicações industriais, e a razão pela qual motores de excitação independente ou
    shunt dominam aplicações que exigem velocidade estável.
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 20 — CONTROLE DE TORQUE E VELOCIDADE: PRINCÍPIOS
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("20. Controle de Torque e Velocidade — Princípios")

    st.markdown(r"""
    Tome o motor de excitação independente como referência — sua característica linear
    torna a análise direta e o resultado se generaliza, com adaptações, aos demais tipos.
    """)

    show_fig(fig_motor_independente_circuito(), 0.62)

    st.markdown(r"""
    Partindo da malha de armadura e da equação de torque, isolamos $\omega_m$:

    $$E_a = K_a\,\Phi\,\omega_m = V_t - R_a\cdot I_a \qquad\quad T = K_a\,\Phi\,I_a$$

    $$\omega_m = \dfrac{V_t - R_a\cdot I_a}{K_a\,\Phi} = \dfrac{V_t}{K_a\,\Phi} - \dfrac{R_a\cdot I_a}{K_a\,\Phi}$$

    Substituindo $I_a = T/(K_a\Phi)$ a partir da equação de torque, chega-se à forma mais
    útil — $\omega_m$ como função **direta** do torque de carga:

    $$\omega_m = \dfrac{V_t}{K_a\,\Phi} - \dfrac{R_a}{(K_a\,\Phi)^2}\cdot T$$

    Esta é a equação de uma **reta**: o termo $V_t/(K_a\Phi)$ é a velocidade a vazio
    (intercepto), e o coeficiente $R_a/(K_a\Phi)^2$ é a inclinação — quanto **menor** a
    resistência de armadura, mais "rígida" (plana) é a reta:
    """)

    show_fig(fig_motor_linear_tv(), 0.58)

    st.markdown(r"""
    A equação evidencia exatamente os **três** parâmetros disponíveis para controlar
    $\omega_m$ a um dado torque de carga, cada um atuando de forma diferente:
    """)

    st.markdown(r"""
    - **Tensão terminal** $V_t$ — controle **diretamente proporcional**: desloca a reta
      inteira para cima ou para baixo, mantendo a inclinação;
    - **Fluxo de campo** $\Phi$ — controle **inversamente proporcional**: altera tanto o
      intercepto quanto a inclinação (ao quadrado), permitindo velocidades **acima** da
      nominal;
    - **Resistência de armadura** $R_a$ (via $R_{ae}$ adicional) — controle **inversamente
      proporcional** apenas na inclinação: mantém o intercepto e "inclina" a reta,
      reduzindo a velocidade para um mesmo torque.
    """)

    st.markdown(r"""
    O controle por tensão terminal exige uma fonte de tensão variável (maior custo), mas
    em compensação produz variação suave, rápida e linear de velocidade — é o método
    preferido sempre que a eletrônica de potência permitir.
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 21 — CONTROLE POR TENSÃO TERMINAL
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("21. Controle por Tensão Terminal")

    st.markdown(r"""
    Como o intercepto $V_t/(K_a\Phi)$ depende linearmente de $V_t$, variar a tensão
    terminal desloca a reta $\omega_m \times T$ inteira, **sem alterar sua inclinação** —
    todas as retas permanecem paralelas:
    """)

    show_fig(fig_motor_tensao_painel(), 0.86)

    st.markdown(r"""
    No painel (a), para um torque fixo, $\omega_m$ cresce linearmente com $V_t$. No painel
    (b), cada valor de $V_t$ gera uma reta $\omega_m \times T$ paralela às demais — elevar
    $V_t$ aumenta a velocidade em todo o intervalo de torque, sem comprometer a rigidez da
    característica. É o método mais "limpo" de controle, mas tem como limite físico a
    própria tensão nominal de projeto da armadura: **não é possível elevar $V_t$
    indefinidamente** sem ultrapassar o isolamento e a saturação da máquina. Por isso, ele
    cobre a faixa de velocidades **da zero até a nominal** ($\omega_{base}$), em **torque
    constante** — acima dela, é necessário recorrer ao enfraquecimento de campo (Seção 22).
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 22 — CONTROLE POR FLUXO DE CAMPO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("22. Controle por Fluxo de Campo")

    st.markdown(r"""
    O controle por fluxo atua sobre a corrente de campo $I_f$ — tipicamente variando o
    reostato $R_{fc}$ em série com o enrolamento shunt. É um método de **baixo custo** e
    simples implementação, já que a potência manipulada no circuito de campo é pequena
    (apenas $I_f$, não $I_a$); em compensação, a resposta é **lenta** (o enrolamento de
    campo tem indutância elevada) e **não linear**.

    Reescrevendo o fluxo como $\Phi = k\cdot I_f$ e definindo $K_f = k\cdot K_a$, a
    equação de velocidade da Seção 20 torna-se:
    """)

    show_fig(fig_motor_shunt_circuito(), 0.62)

    st.markdown(r"""
    $$\Phi = k\cdot I_f \qquad\quad K_f = k\cdot K_a \qquad\quad \omega_m = \dfrac{V_t}{K_f\,I_f} - \dfrac{R_a}{(K_f\,I_f)^2}\cdot T$$

    Como $I_f$ aparece no **denominador**, a relação é inversa: **reduzir** $I_f$ (aumentando
    $R_{fc}$) **eleva** a velocidade — o efeito chamado de "enfraquecimento de campo"
    (*field weakening*):
    """)

    show_fig(fig_motor_campo_curva(), 0.56)

    st.markdown(r"""
    Variando $R_{fc}$ entre zero e seu valor máximo obtém-se uma família de retas
    $\omega_m \times T$, cada uma com intercepto **e** inclinação diferentes — diferente do
    controle por tensão, aqui as retas **não são paralelas**:
    """)

    show_fig(fig_motor_campo_familia_combinado(), 0.86)

    st.markdown(r"""
    O enfraquecimento de campo complementa o controle por tensão terminal: eleva a
    velocidade **além** da nominal, à custa de reduzir o torque máximo disponível (já que
    $T = K_a\Phi I_a$ também cai com $\Phi$). Por isso os dois métodos são tipicamente
    combinados — tensão terminal até $\omega_{base}$ (**torque constante**), enfraquecimento
    de campo de $\omega_{base}$ até $\omega_{max}$ (**potência constante**, painel à direita
    acima) — formando a base do controle de velocidade na maioria dos acionamentos
    industriais de motores CC.
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 23 — CONTROLE POR RESISTÊNCIA DE ARMADURA
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("23. Controle por Resistência de Armadura")

    st.markdown(r"""
    O terceiro método insere uma resistência adicional $R_{ae}$ em série com a armadura.
    É de implementação simples — basta um reostato de potência — mas **ineficiente**: a
    energia dissipada em $R_{ae}$ é proporcional a $I_a^2$, e como $I_a > I_f$ na maioria
    das máquinas, a potência manipulada (e o custo do reostato) é **maior** que no
    controle por fluxo.
    """)

    show_fig(fig_motor_shunt_rae_circuito(), 0.62)

    st.markdown(r"""
    $$\omega_m = \dfrac{V_t}{K_a\,\Phi} - \dfrac{R_a + R_{ae}}{(K_a\,\Phi)^2}\cdot T$$

    Como $R_{ae}$ soma-se a $R_a$ apenas no termo de **inclinação**, o intercepto (velocidade
    a vazio) permanece inalterado — todas as retas convergem para o mesmo ponto em $T=0$,
    "abrindo-se em leque" conforme $R_{ae}$ cresce:
    """)

    show_fig(fig_motor_rae_familia(), 0.86)

    st.markdown(r"""
    Esse "leque" reduz a velocidade disponível em qualquer torque de carga não nulo, à
    custa de dissipar energia em $R_{ae}$ — por isso a potência útil entregue à carga cai
    conforme $R_{ae}$ aumenta (painel à direita), mesmo mantendo o torque constante.

    O mesmo princípio se aplica ao motor **série**, com uma diferença importante: como o
    próprio enrolamento série conduz a corrente de armadura, o fluxo passa a depender de
    $I_a$ — e a álgebra muda:
    """)

    show_fig(fig_motor_serie_rae_circuito(), 0.62)

    st.markdown(r"""
    $$E_a = K_a\,\Phi\,\omega_m = V_t - (R_a + R_{ae} + R_{sr})\cdot I_a \qquad\quad T = K_a\,\Phi\,I_a \qquad\quad \Phi = k\cdot I_a$$

    Substituindo $\Phi = k\cdot I_a$ na equação de torque obtém-se $T = K_a\,k\,I_a^2$.
    Definindo $K_{sr} = K_a\,k$, o torque do motor série é proporcional ao **quadrado**
    da corrente de armadura — $T = K_{sr}\,I_a^2$ — o que, isolando $I_a = \sqrt{T/K_{sr}}$
    e substituindo de volta na equação de $\omega_m$, leva à característica **hiperbólica**
    do motor série:

    $$\omega_m = \dfrac{V_t}{\sqrt{K_{sr}}\,\sqrt{T}} - \dfrac{R_a + R_{ae} + R_{sr}}{K_{sr}}$$
    """)

    show_fig(fig_motor_serie_rae_curvas(), 0.6)

    st.markdown(r"""
    Essa relação $\omega_m \propto 1/\sqrt{T}$ é a assinatura do motor série: torques
    extremamente altos em baixas velocidades (ideal para partida sob carga pesada, como em
    tração elétrica e guindastes), com a velocidade subindo rapidamente conforme o torque
    de carga diminui — reforçando, mais uma vez, por que esse motor nunca deve ser operado
    sem carga mecânica firmemente acoplada ao eixo.
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 24 — PARTIDA DE MOTORES CC
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("24. Partida de Motores CC")

    st.markdown(r"""
    No instante da partida, $\omega_m=0$ e, portanto, $E_a=0$ — não há força
    contraeletromotriz para limitar a corrente, e a malha de armadura se reduz a
    $V_t = R_a\cdot I_a$. Como $R_a$ é tipicamente pequena, a corrente de partida pode
    atingir **dezenas de vezes** a corrente nominal — o suficiente para danificar o
    comutador, queimar o isolamento ou disparar a proteção de sobrecorrente.

    A solução clássica é inserir uma resistência de partida $R_{partida}$ em série com a
    armadura apenas durante a aceleração, retirando-a (curto-circuitando-a) gradualmente
    à medida que $\omega_m$ — e, com ela, $E_a$ — cresce e passa a limitar naturalmente a
    corrente:
    """)

    show_fig(fig_motor_partida_circuito(), 0.62)

    st.markdown(r"""
    $$I_{a,partida} = \dfrac{V_t}{R_a + R_{partida}}$$

    Na prática, $R_{partida}$ é retirada em **degraus** discretos (reostato de contatos
    progressivos, historicamente com retenção eletromagnética), mantendo a corrente de
    armadura dentro de uma faixa segura a cada passo. Alternativas modernas dispensam o
    reostato e elevam $V_t$ suavemente — em rampa ou perfil exponencial — desde zero até o
    nominal, aplicando o próprio controle por tensão terminal (Seção 21) já na partida.
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 25 — CONTROLE EM MALHA FECHADA
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("25. Controle em Malha Fechada")

    st.markdown(r"""
    Os métodos anteriores especificam **como** atuar sobre $V_t$, $\Phi$ ou $R_a$ — mas em
    malha aberta, qualquer variação de carga desloca o ponto de operação ao longo da reta
    $\omega_m \times T$, afastando a velocidade real da pretendida. Acionamentos industriais
    corrigem isso com controle em **malha fechada**, tipicamente em cascata: um laço externo
    de velocidade define a corrente de armadura necessária, e um laço interno, mais rápido,
    garante que ela seja entregue à máquina:
    """)

    show_fig(fig_motor_malha_fechada_diagrama(), 0.92)

    st.markdown(r"""
    A velocidade medida $N$ é comparada à referência $N^{*}$; o erro alimenta o
    controlador de velocidade, que define a corrente de armadura de referência $I_a^{*}$.
    Esse sinal é comparado à corrente medida $I_a$ em um segundo somador, cujo erro
    alimenta o controlador de corrente — que produz o comando $V_c$ para o conversor,
    responsável por sintetizar a tensão terminal $V_t$ aplicada ao motor.

    A cascata é deliberada: o laço de corrente, muito mais rápido que a dinâmica mecânica,
    mantém o torque sob controle quase instantâneo — inclusive limitando-o com segurança
    durante transitórios, como a própria partida (substituindo o resistor da Seção 24). O
    laço de velocidade, mais lento, ajusta esse limite para que a velocidade real convirja
    à referência mesmo sob variações de carga.
    """)

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 26 — EFICIÊNCIA E FLUXO DE POTÊNCIA
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("26. Eficiência e Fluxo de Potência")

    st.markdown(r"""
    Gerador e motor são a mesma máquina operando com o fluxo de potência invertido — o
    que torna natural analisar as perdas de ambos a partir de um único circuito composto,
    bastando inverter o sentido das correntes:
    """)

    show_fig(fig_eficiencia_circuito(), 0.62)

    st.markdown(r"""
    Em qualquer um dos dois sentidos, a potência de entrada não é integralmente convertida:
    parte se dissipa em cada elemento resistivo do circuito **e** no atrito/ventilação do
    rotor (perdas rotacionais — mancais, ventilação e perdas no núcleo por
    histerese/correntes parasitas). A eficiência é a razão entre o que sai e o que entra:

    $$\eta = \dfrac{P_{out}}{P_{in}}$$

    O diagrama abaixo mostra, passo a passo, como a potência de entrada é reduzida por
    cada parcela de perda até restar a potência de saída — para o gerador (entrada
    mecânica, saída elétrica) e para o motor (entrada elétrica, saída mecânica), com
    faixas típicas de cada perda em máquinas CC de porte industrial:
    """)

    show_fig(fig_eficiencia_fluxo_potencia(), 0.78)

    st.markdown(r"""
    As perdas **rotacionais** (3–15%) tendem a ser a maior parcela isolada, seguidas pelas
    perdas na **armadura** ($I_a^2R_a$, 2–4%). As perdas nos enrolamentos de campo — shunt
    ($I_f^2R_f$, 1–5%) e série ($I_t^2R_{sr}$, 1–2%) — são menores, já que $I_f \ll I_a$ e
    $R_{sr}$ é deliberadamente pequena. A ordem em que aparecem reflete o fluxo físico de
    potência: no motor, as perdas elétricas ocorrem primeiro (conversão elétrica →
    entreferro) e a rotacional por último (etapa mecânica até o eixo); no gerador, a ordem
    se inverte.
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
