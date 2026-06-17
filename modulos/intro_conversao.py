"""
SINTONIA — Máquinas Elétricas · Módulo 1
Introdução à Conversão Eletromecânica de Energia: Circuitos Magnéticos
Baseado em: CEEI – IME – Magnéticos (Prof. Marcus Fernandes, IFRN-CNAT)
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import plotly.graph_objects as go
import io
import schemdraw
import schemdraw.elements as elm


def run():
    # ── Paleta (cores escuras — legíveis em fundo claro/transparente) ────────
    AZ = "#3d8ef0"; RX = "#6c47ff"; VD = "#1f9d55"; LR = "#e07b00"
    CI = "#0097a7"; TX = "#1a1f2b"; CZ = "#6b7280"

    # ── CSS ──────────────────────────────────────────────────────────────────
    CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');
.mod-header{font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;letter-spacing:-.02em;margin-bottom:.1rem}
.mod-sub{font-size:.88rem;opacity:.50;margin-bottom:1.4rem}
.sec-title{font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;margin:2rem 0 .6rem;
           padding-bottom:.3rem;border-bottom:2px solid rgba(61,142,240,.25)}
.subsec{font-family:'Syne',sans-serif;font-size:.98rem;font-weight:700;margin:1.4rem 0 .4rem;color:#3d8ef0}
.eq-box{background:rgba(61,142,240,.07);border-left:3px solid #3d8ef0;
        border-radius:0 8px 8px 0;padding:.65rem 1rem;margin:.55rem 0}
.def-box{background:rgba(108,71,255,.07);border-left:3px solid #6c47ff;
         border-radius:0 8px 8px 0;padding:.65rem 1rem;margin:.55rem 0}
.nota-box{background:rgba(224,123,0,.08);border-left:3px solid #e07b00;
          border-radius:0 8px 8px 0;padding:.65rem 1rem;margin:.55rem 0}
.ref-item{font-size:.82rem;opacity:.65;line-height:1.7;margin:.15rem 0}
.fig-cap{font-size:.78rem;opacity:.55;text-align:center;margin-top:-.4rem;margin-bottom:.6rem}
</style>"""

    # ── Helpers de figura (matplotlib → PNG transparente) ─────────────────────
    def _buf(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=160, bbox_inches="tight",
                    transparent=True)
        buf.seek(0); plt.close(fig); return buf

    def _show(fig, caption=""):
        st.image(_buf(fig), use_container_width=True)
        if caption:
            st.markdown(f'<div class="fig-cap">{caption}</div>', unsafe_allow_html=True)

    def _plot(fig, key=None):
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

    def _schem_to_png(build_fn, color=TX):
        """build_fn(d) monta o circuito; retorna bytes PNG transparente."""
        d = schemdraw.Drawing(transparent=True, show=False)
        d.config(fontsize=12, color=color)
        build_fn(d)
        return d.get_imagedata("png")

    # ════════════════════════════════════════════════════════════════════════
    # FIGURAS — GEOMETRIA (matplotlib, fundo transparente)
    # ════════════════════════════════════════════════════════════════════════

    def fig_regra_mao():
        fig, ax = _mpl_base((4.6, 4))
        ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5)
        ax.add_patch(plt.Circle((0, 0), .22, color=AZ, zorder=5))
        ax.plot(0, 0, ".", color="white", ms=8, zorder=6)
        for r, a in zip([.7, 1.15, 1.65, 2.1], [.95, .8, .65, .5]):
            t = np.linspace(0, 2*np.pi, 300)
            ax.plot(r*np.cos(t), r*np.sin(t), color=AZ, alpha=a, lw=1.6)
            idx = 60
            dx = -r*np.sin(t[idx])*.001; dy = r*np.cos(t[idx])*.001
            ax.annotate("", xy=(r*np.cos(t[idx])+dx*300, r*np.sin(t[idx])+dy*300),
                        xytext=(r*np.cos(t[idx]), r*np.sin(t[idx])),
                        arrowprops=dict(arrowstyle="->", color=AZ, lw=1.4))
        ax.annotate("$H$", xy=(1.9*np.cos(np.pi/5), 1.9*np.sin(np.pi/5)),
                    fontsize=15, color=TX, ha="center")
        ax.text(0, .38, "$i$", fontsize=14, color=TX, ha="center", va="bottom")
        ax.annotate("", xy=(1.15, 0), xytext=(.22, 0),
                    arrowprops=dict(arrowstyle="-|>", color=CI, lw=1.4))
        ax.text(.68, .14, "$r$", fontsize=13, color=CI)
        fig.tight_layout(); return fig

    def fig_ampere_contorno():
        fig, ax = _mpl_base((5.6, 4))
        ax.set_xlim(-3, 3); ax.set_ylim(-2.2, 2.2)
        outer = mpatches.FancyBboxPatch((-2.2, -1.5), 4.4, 3., boxstyle="round,pad=.3",
                                         lw=1.8, ec=CZ, fc="#3d8ef018", zorder=2)
        inner = mpatches.FancyBboxPatch((-1., -.7), 2., 1.4, boxstyle="round,pad=.1",
                                         lw=1.8, ec=CZ, fc="none", zorder=3)
        ax.add_patch(outer); ax.add_patch(inner)
        t = np.linspace(0, 2*np.pi, 400); rm = 1.45
        ax.plot(rm*np.cos(t), rm*np.sin(t)*.85, "--", color=LR, lw=1.8, zorder=4)
        idx = 120
        ax.annotate("", xy=(rm*np.cos(t[idx+3]), rm*.85*np.sin(t[idx+3])),
                    xytext=(rm*np.cos(t[idx]), rm*.85*np.sin(t[idx])),
                    arrowprops=dict(arrowstyle="->", color=LR, lw=1.8), zorder=5)
        for x0 in np.linspace(-1.8, 1.8, 8):
            ax.plot([x0, x0], [1.5, 2.], color=AZ, lw=2.4, zorder=5)
            ax.plot([x0, x0], [-2., -1.5], color=AZ, lw=2.4, zorder=5)
        ax.text(0, 0, "$N$ espiras", color=TX, fontsize=11, ha="center", va="center", zorder=5)
        ax.text(rm+.25, .6, "$C$", color=LR, fontsize=14, zorder=6)
        ax.text(-2.85, 1.6, "$i$", color=AZ, fontsize=14)
        fig.tight_layout(); return fig

    def fig_campo_r():
        fig, ax = _mpl_base((5.6, 3.6))
        ax.set_xlim(-3, 3); ax.set_ylim(-2, 2)
        ax.add_patch(plt.Circle((0, 0), .18, color=AZ, zorder=5))
        ax.plot(0, 0, ".", color="white", ms=7, zorder=6)
        for r in [.6, 1., 1.4, 1.8]:
            t = np.linspace(0, 2*np.pi, 300)
            ax.plot(r*np.cos(t), r*np.sin(t), color=AZ, alpha=max(.35, 1-r*.35), lw=1.5)
        ang = np.pi/4; xp, yp = 1.4*np.cos(ang), 1.4*np.sin(ang)
        ax.annotate("", xy=(xp, yp), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=CI, lw=1.6))
        ax.text(xp/2+.12, yp/2+.12, "$r$", color=CI, fontsize=14)
        ax.text(1.95, .35, r"$H\cdot 2\pi r = i$", color=TX, fontsize=12)
        ax.text(1.95, -.35, r"$H = \dfrac{i}{2\pi r}$", color=TX, fontsize=12)
        fig.tight_layout(); return fig

    def fig_circuito_mag():
        fig, ax = _mpl_base((5.6, 4.2))
        ax.set_xlim(-3.3, 3.3); ax.set_ylim(-2.6, 2.6)
        t = np.linspace(0, 2*np.pi, 400); Ro, Ri = 2., 1.1
        ax.fill_between(Ro*np.cos(t), Ro*np.sin(t), Ri*np.cos(t), Ri*np.sin(t),
                        color="#3d8ef028", zorder=2)
        ax.plot(Ro*np.cos(t), Ro*np.sin(t), color=CZ, lw=1.4, zorder=3)
        ax.plot(Ri*np.cos(t), Ri*np.sin(t), color=CZ, lw=1.4, zorder=3)
        for ang in np.linspace(np.pi*.25, np.pi*.75, 9):
            xc, yc = 1.55*np.cos(ang), 1.55*np.sin(ang)
            ax.add_patch(mpatches.Ellipse((xc, yc), .35, .18,
                                          angle=np.degrees(ang)+90,
                                          color=AZ, zorder=4, alpha=.9))
        tf = np.linspace(np.pi*.1, np.pi*1.85, 200); rf = 1.55
        ax.plot(rf*np.cos(tf), rf*np.sin(tf), color=VD, lw=2.2, zorder=5, alpha=.9)
        ax.annotate("", xy=(rf*np.cos(tf[-1]+.05), rf*np.sin(tf[-1]+.05)),
                    xytext=(rf*np.cos(tf[-1]), rf*np.sin(tf[-1])),
                    arrowprops=dict(arrowstyle="->", color=VD, lw=2.2), zorder=6)
        ax.text(-.32, .15, "$\\phi$", color=VD, fontsize=17, zorder=7)
        ax.text(0, 2.35, "$N$ espiras", color=AZ, fontsize=11, ha="center")
        fig.tight_layout(); return fig

    def fig_entreferro_geom():
        fig, ax = _mpl_base((5.6, 4.4))
        ax.set_xlim(0, 10); ax.set_ylim(0, 8.2)
        for pts in [[(1,1),(9,1),(9,2.2),(1,2.2)],
                    [(1,2.2),(2.5,2.2),(2.5,6.4),(1,6.4)],
                    [(7.5,2.2),(9,2.2),(9,6.4),(7.5,6.4)],
                    [(1,6.4),(4.5,6.4),(4.5,7.4),(1,7.4)],
                    [(5.5,6.4),(9,6.4),(9,7.4),(5.5,7.4)]]:
            ax.add_patch(plt.Polygon(pts, color="#3d8ef022", ec=CZ, lw=1.5, zorder=2))
        ax.add_patch(Rectangle((4.5,6.4), 1., 1., color="none", ec=LR, lw=1.8, ls="--", zorder=3))
        ax.text(5., 6.1, "Entreferro  $\\ell_g$", color=LR, fontsize=9, ha="center", va="top")
        for y0 in np.linspace(2.6, 5.8, 7):
            ax.add_patch(mpatches.Ellipse((1.75, y0), .85, .35,
                                          color=AZ, zorder=4, alpha=.85))
        ax.text(.45, 4.2, "$N$\nespiras", color=AZ, fontsize=9, ha="center")
        xs = [2.25,2.25,5.,7.75,7.75,5.,4.7]
        ys = [4.1, 6.9,6.9,6.9, 4.1, 4.1,4.1]
        ax.plot(xs, ys, "--", color=VD, lw=1.8, alpha=.85)
        ax.annotate("", xy=(4.8,4.1), xytext=(4.5,4.1),
                    arrowprops=dict(arrowstyle="->", color=VD, lw=1.8))
        ax.text(3.8, 3.7, "$\\phi$", color=VD, fontsize=13)
        fig.tight_layout(); return fig

    def fig_frangeamento():
        fig, axes = plt.subplots(1, 2, figsize=(8.6, 4))
        fig.patch.set_alpha(0)
        # — seção da máquina rotativa —
        ax = axes[0]; ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(-3.5, 3.5); ax.set_ylim(-3.5, 3.5); ax.set_aspect("equal")
        ax.set_title("Máquina rotativa (seção)", color=TX, fontsize=10)
        ax.add_patch(plt.Circle((0,0), 3.,  color="#3d8ef022", ec=CZ, lw=1.6, zorder=2))
        ax.add_patch(plt.Circle((0,0), 2.2, color="none",     ec=CZ, lw=1.2, zorder=3))
        ax.add_patch(plt.Circle((0,0), 1.9, color="#3d8ef022", ec=CZ, lw=1.4, zorder=4))
        ax.add_patch(plt.Circle((0,0), 1.1, color="none",     ec=CZ, lw=1.,  zorder=5))
        ax.add_patch(plt.Circle((0,0), .25, color=CZ, zorder=6))
        ring = mpatches.Wedge((0, 0), 2.2, 0, 360, width=2.2-1.9, color=LR, alpha=.30, zorder=3)
        ax.add_patch(ring)
        ax.text(0, 2.6, "Estator", color=TX, fontsize=9, ha="center")
        ax.text(0, 1.5, "Rotor",   color=TX, fontsize=9, ha="center")
        ax.text(2.55, .55, "Entreferro\n$\\ell_g$", color=LR, fontsize=8, ha="center")
        # — frangeamento —
        ax2 = axes[1]; ax2.set_facecolor("none"); ax2.axis("off")
        ax2.set_xlim(0, 10); ax2.set_ylim(0, 8)
        ax2.set_title("Frangeamento no entreferro", color=TX, fontsize=10)
        ax2.add_patch(Rectangle((3, 5.5), 4, 2, color="#3d8ef022", ec=CZ, lw=1.4))
        ax2.add_patch(Rectangle((3,  .8), 4, 2, color="#3d8ef022", ec=CZ, lw=1.4))
        for x in np.linspace(3.6, 6.4, 5):
            ax2.annotate("", xy=(x, 5.5), xytext=(x, 2.8),
                         arrowprops=dict(arrowstyle="-|>", color=VD, lw=1.4, mutation_scale=10))
        for xb in [3., 7.]:
            t2 = np.linspace(0, np.pi, 50)
            side = -1 if xb < 5 else 1
            ax2.plot(xb + side*.5 + (-side)*.7*np.sin(t2),
                     4.15 + 1.35*np.cos(t2), "--", color=RX, lw=1.6, alpha=.85)
        ax2.text(5., 4.15, "$\\ell_g$", color=LR, fontsize=13, ha="center")
        ax2.annotate("", xy=(2.2, 5.5), xytext=(7.8, 5.5),
                     arrowprops=dict(arrowstyle="<->", color=RX, lw=1.4))
        ax2.text(5., 5.8, "$A_{ef}>A_c$", color=RX, fontsize=9, ha="center")
        fig.tight_layout(); return fig

    def fig_acoplamento():
        """Duas bobinas acopladas — geometria (para indutância mútua)."""
        fig, ax = _mpl_base((5.6, 4.2))
        ax.set_xlim(-0.8, 10.8); ax.set_ylim(0, 8)
        for pts in [[(0.5,1),(9.5,1),(9.5,2),(0.5,2)],
                    [(0.5,2),(2.,2),(2.,7),(0.5,7)],
                    [(8.,2),(9.5,2),(9.5,7),(8.,7)],
                    [(0.5,7),(9.5,7),(9.5,6),(0.5,6)]]:
            ax.add_patch(plt.Polygon(pts, color="#3d8ef022", ec=CZ, lw=1.4, zorder=2))
        for y0 in np.linspace(2.5, 5.8, 7):
            ax.add_patch(mpatches.Ellipse((1.25, y0), 1., .38, color=AZ, zorder=4, alpha=.9))
        ax.text(-.7, 4.1, "$N_1\\,i_1$", color=AZ, fontsize=10, ha="left", va="center")
        for y0 in np.linspace(2.5, 5.8, 7):
            ax.add_patch(mpatches.Ellipse((8.75, y0), 1., .38, color=VD, zorder=4, alpha=.9))
        ax.text(10.7, 4.1, "$N_2\\,i_2$", color=VD, fontsize=10, ha="right", va="center")
        ax.plot([2., 2., 8., 8., 5.], [4.1, 6.5, 6.5, 4.1, 4.1], color=RX, lw=2.2, alpha=.9)
        ax.annotate("", xy=(5.1, 4.1), xytext=(4.9, 4.1),
                    arrowprops=dict(arrowstyle="->", color=RX, lw=2.2))
        ax.text(5., 5.5, "$\\phi_{12}$", color=RX, fontsize=13, ha="center")
        fig.tight_layout(); return fig

    def fig_parasita_geom():
        fig, ax = _mpl_base((6.6, 4.))
        ax.set_xlim(0, 10); ax.set_ylim(0, 8)
        ax.add_patch(Rectangle((.3, 1.5), 3.5, 5., color="#3d8ef022", ec=CZ, lw=1.4))
        ax.text(2.05, 7.1, "Núcleo sólido", color=TX, fontsize=9, ha="center")
        for cy in [3., 4.5, 6.]:
            t = np.linspace(0, 2*np.pi, 100)
            ax.plot(2.05+1.2*np.cos(t), cy+.7*np.sin(t), color=LR, lw=1.7, alpha=.9)
            ax.annotate("", xy=(2.05+1.2*np.cos(.1), cy+.7*np.sin(.1)),
                        xytext=(2.05+1.2*np.cos(0), cy+.7*np.sin(0)),
                        arrowprops=dict(arrowstyle="->", color=LR, lw=1.4))
        ax.text(2.05, 1., "$i_e$ (parasitas)", color=LR, fontsize=8, ha="center")
        ax.annotate("", xy=(2.05, 6.8), xytext=(2.05, 5.5),
                    arrowprops=dict(arrowstyle="-|>", color=VD, lw=2.2))
        ax.text(2.6, 6.2, "$B(t)$", color=VD, fontsize=12)
        x0 = 5.5; n = 8; wl = 3.2/n
        for k in range(n):
            shade = "#3d8ef033" if k % 2 == 0 else "#3d8ef015"
            ax.add_patch(Rectangle((x0+k*wl, 1.5), wl*.82, 5., color=shade, ec=CZ, lw=.8))
        ax.text(x0+1.6, 7.1, "Núcleo laminado", color=TX, fontsize=9, ha="center")
        ax.text(x0+1.6, 1., "correntes reduzidas", color=VD, fontsize=8, ha="center")
        ax.annotate("", xy=(x0+1.6, 6.8), xytext=(x0+1.6, 5.5),
                    arrowprops=dict(arrowstyle="-|>", color=VD, lw=2.2))
        ax.text(x0+2.2, 6.2, "$B(t)$", color=VD, fontsize=12)
        fig.tight_layout(); return fig

    # ════════════════════════════════════════════════════════════════════════
    # FIGURAS — CIRCUITOS (schemdraw, fundo transparente, malha fechada)
    # ════════════════════════════════════════════════════════════════════════

    def schem_analogia_eletrico():
        def build(d):
            d.add(elm.SourceV().up().label("$e$", loc="left").color(VD))
            d.add(elm.Resistor().right().label("$R$", loc="top").color(CI))
            d.add(elm.Line().down())
            d.add(elm.Line().left())
        return _schem_to_png(build)

    def schem_analogia_magnetico():
        def build(d):
            d.add(elm.SourceV().up().label("$\\mathcal{F}=Ni$", loc="left").color(AZ))
            d.add(elm.Resistor().right().label("$\\mathcal{R}$", loc="top").color(AZ))
            d.add(elm.Line().down())
            d.add(elm.Line().left())
        return _schem_to_png(build)

    def schem_entreferro():
        def build(d):
            d.add(elm.SourceV().up().label("$\\mathcal{F}=Ni$", loc="left").color(AZ))
            d.add(elm.Resistor().right().label("$\\mathcal{R}_c$", loc="top").color(CZ))
            d.add(elm.Resistor().right().label("$\\mathcal{R}_g$", loc="top").color(LR))
            d.add(elm.Line().down())
            d.add(elm.Line().left().tox(0))
        return _schem_to_png(build)

    # ════════════════════════════════════════════════════════════════════════
    # FIGURAS — CURVAS (Plotly, interativas e responsivas)
    # ════════════════════════════════════════════════════════════════════════

    def plotly_BH():
        H = np.linspace(0, 2000, 400)
        B_lin = 4*np.pi*1e-7 * H * 1e3
        B_lin = B_lin / B_lin.max() * .25
        Bsat = 1.8; mur = 3500
        B_fe = Bsat*(1 - np.exp(-mur*4*np.pi*1e-7*H/Bsat))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=H, y=B_lin, mode="lines", name="Ar / cobre (μᵣ≈1)",
                                  line=dict(color=CI, dash="dash", width=2)))
        fig.add_trace(go.Scatter(x=H, y=B_fe, mode="lines",
                                  name="Ferromagnético (μᵣ≈2000–6000)",
                                  line=dict(color=AZ, width=3)))
        fig.add_hline(y=Bsat, line=dict(color=CZ, dash="dot", width=1),
                      annotation_text="B_sat", annotation_font_color=CZ)
        fig.update_layout(
            title="Relação B-H: linear vs. ferromagnético",
            xaxis_title="H (A/m)", yaxis_title="B (T)",
            legend=dict(orientation="h", y=-0.25),
            height=380,
        )
        return fig

    def plotly_histerese():
        Hmax = 1000; Bsat = 1.7
        def branch(H, hc=200, upper=True):
            s = 1 if upper else -1
            return Bsat * np.tanh((H + s*hc) / (Hmax*.4))
        Hp = np.linspace(-Hmax, Hmax, 400)
        Hn = np.linspace(Hmax, -Hmax, 400)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=Hp, y=branch(Hp, upper=True), mode="lines",
                                  name="Magnetização", line=dict(color=AZ, width=3)))
        fig.add_trace(go.Scatter(x=Hn, y=branch(Hn, upper=False), mode="lines",
                                  name="Desmagnetização", line=dict(color=RX, width=3)))
        fig.add_annotation(x=0, y=1.2, text="B_r (remanência)", showarrow=True,
                            arrowcolor=VD, font=dict(color=VD), ax=80, ay=-30)
        fig.add_annotation(x=200, y=0, text="H_c (coercividade)", showarrow=True,
                            arrowcolor=LR, font=dict(color=LR), ax=80, ay=30)
        fig.update_layout(
            title="Laço de Histerese B-H",
            xaxis_title="H (A/m)", yaxis_title="B (T)",
            legend=dict(orientation="h", y=-0.25),
            height=380,
        )
        return fig

    def plotly_perdas_nucleo():
        f = np.linspace(10, 400, 200); Bm = 1.5
        Ph = .005*f*Bm**1.8
        Pe = .000012*f**2*Bm**2
        Pc = Ph + Pe

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=f, y=Ph, mode="lines", name="Histerese Pₕ",
                                  line=dict(color=AZ, dash="dash", width=2)))
        fig.add_trace(go.Scatter(x=f, y=Pe, mode="lines", name="Corrente parasita Pₑ",
                                  line=dict(color=LR, dash="dash", width=2)))
        fig.add_trace(go.Scatter(x=f, y=Pc, mode="lines", name="Total Pc = Pₕ+Pₑ",
                                  line=dict(color=TX, width=3)))
        fig.update_layout(
            title="Perdas no Núcleo vs. Frequência",
            xaxis_title="f (Hz)", yaxis_title="Perdas (W/kg)",
            legend=dict(orientation="h", y=-0.25),
            height=380,
        )
        return fig

    def plotly_energia_indutiva():
        i_a = np.linspace(0, 4, 200)
        L_val = .5
        W = .5 * L_val * i_a**2

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=i_a, y=W, mode="lines", name="Wₗ = ½Li²",
                                  line=dict(color=AZ, width=3), fill="tozeroy",
                                  fillcolor="rgba(61,142,240,.15)"))
        fig.update_layout(
            title="Energia Armazenada no Campo Magnético",
            xaxis_title="i (A)", yaxis_title="Wₗ (J)",
            height=340,
        )
        return fig

    # ════════════════════════════════════════════════════════════════════════
    # EXPLORADORES (Plotly, totalmente interativos)
    # ════════════════════════════════════════════════════════════════════════

    def exp_circuito():
        st.markdown("**Ajuste os parâmetros do circuito magnético:**")
        c1, c2, c3 = st.columns(3)
        with c1:
            N  = st.slider("Espiras N",         10, 1000, 200, step=10, key="m1_N")
            i  = st.slider("Corrente i (A)",    .1,  20.,  2., step=.1, key="m1_i")
        with c2:
            mur  = st.slider("μᵣ",                1, 6000, 2000, step=50, key="m1_mur")
            A_c  = st.slider("Seção A (cm²)",    1.,  50.,  10., step=.5, key="m1_A")
        with c3:
            l_c  = st.slider("Comprimento ℓ (cm)", 5., 100., 30., step=1., key="m1_l")
            lg   = st.slider("Entreferro ℓg (mm)",  0.,  10.,  0., step=.1, key="m1_lg")

        mu0 = 4*np.pi*1e-7
        A = A_c*1e-4; l = l_c*1e-2; lg_m = lg*1e-3
        Rc = l/(mur*mu0*A); Rg = lg_m/(mu0*A) if lg_m > 0 else 0; Rt = Rc + Rg
        FMM = N*i; phi = FMM/Rt; B = phi/A; Hc = B/(mur*mu0); WL = .5*(N**2/Rt)*i**2

        cols = st.columns(5)
        for col, (lab, val) in zip(cols, [
            ("ℱ (A·t)", f"{FMM:.1f}"),
            ("φ (mWb)", f"{phi*1e3:.3f}"),
            ("B (T)",   f"{B:.4f}"),
            ("ℛ (A·t/Wb)", f"{Rt:.2e}"),
            ("Wₗ (mJ)", f"{WL*1e3:.2f}"),
        ]):
            with col: st.metric(lab, val)

        i_a = np.linspace(0, i*1.6+.1, 200); phi_a = N*i_a/Rt
        H_a = Hc*i_a/max(i, 1e-9); B_a = B*i_a/max(i, 1e-9)

        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=i_a, y=phi_a*1e3, mode="lines",
                                      line=dict(color=AZ, width=3)))
            fig.add_trace(go.Scatter(x=[i], y=[phi*1e3], mode="markers",
                                      marker=dict(color=LR, size=11),
                                      showlegend=False))
            fig.update_layout(title="Fluxo vs. Corrente",
                               xaxis_title="i (A)", yaxis_title="φ (mWb)",
                               height=320, showlegend=False)
            _plot(fig, key="m1_exp1_fluxo")
        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=H_a, y=B_a, mode="lines",
                                       line=dict(color=VD, width=3)))
            fig2.add_trace(go.Scatter(x=[Hc], y=[B], mode="markers",
                                       marker=dict(color=LR, size=11),
                                       showlegend=False))
            fig2.update_layout(title="Ponto de Operação B-H (linear)",
                                xaxis_title="H (A/m)", yaxis_title="B (T)",
                                height=320, showlegend=False)
            _plot(fig2, key="m1_exp1_bh")

        if lg > 0:
            st.info(f"ℛ_c = {Rc:.2e} A·t/Wb  |  ℛ_g = {Rg:.2e} A·t/Wb  |  "
                    f"ℛ_g/ℛ_c = {Rg/Rc:.1f}×  — o entreferro domina!")

    def exp_BH():
        st.markdown("**Ajuste os parâmetros da curva de magnetização:**")
        c1, c2 = st.columns(2)
        with c1:
            mur_max = st.slider("μᵣ máxima (pico)", 500, 8000, 3000, step=100, key="m1_murmax")
            Bsat    = st.slider("B_sat (T)",          .5,  2.2,  1.8, step=.05, key="m1_bsat")
        with c2:
            H_op = st.slider("Ponto de operação H (A/m)", 10, 4000, 500, step=10, key="m1_hop")
            show_hist = st.checkbox("Mostrar laço de histerese simplificado",
                                     value=False, key="m1_showhist")

        mu0 = 4*np.pi*1e-7
        H_a = np.linspace(0, 5000, 400)
        def Bmag(H, mr, Bs):
            mi = mr*mu0; a = Bs/mi; return Bs*H/(a+H)
        B_a = Bmag(H_a, mur_max, Bsat); B_op = Bmag(H_op, mur_max, Bsat)
        dBdH = np.gradient(B_a, H_a); mur_loc = dBdH/mu0
        mr_op = float(np.interp(H_op, H_a, mur_loc))

        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=H_a, y=B_a, mode="lines", name="B-H ferromagnético",
                                      line=dict(color=AZ, width=3)))
            if show_hist:
                Hc2 = H_op*.15
                fig.add_trace(go.Scatter(x=H_a, y=Bmag(H_a-Hc2, mur_max*.8, Bsat),
                                          mode="lines", name="Laço superior",
                                          line=dict(color=RX, dash="dash", width=1.6)))
                fig.add_trace(go.Scatter(x=H_a, y=Bmag(H_a+Hc2, mur_max*.8, Bsat),
                                          mode="lines", name="Laço inferior",
                                          line=dict(color=LR, dash="dash", width=1.6)))
            fig.add_trace(go.Scatter(x=[H_op], y=[B_op], mode="markers",
                                      marker=dict(color=LR, size=11),
                                      name=f"Op: H={H_op}, B={B_op:.3f}"))
            fig.add_hline(y=Bsat, line=dict(color=CZ, dash="dot", width=1))
            fig.update_layout(title="Curva B-H e Ponto de Operação",
                               xaxis_title="H (A/m)", yaxis_title="B (T)",
                               legend=dict(orientation="h", y=-0.3), height=380)
            _plot(fig, key="m1_exp2_bh")
        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=H_a[1:], y=mur_loc[1:], mode="lines",
                                       line=dict(color=VD, width=3)))
            fig2.add_trace(go.Scatter(x=[H_op], y=[mr_op], mode="markers",
                                       marker=dict(color=LR, size=11),
                                       name=f"μᵣ local={mr_op:.0f}"))
            fig2.update_layout(title="Permeabilidade Relativa Local vs. H",
                                xaxis_title="H (A/m)", yaxis_title="μᵣ local",
                                showlegend=False, height=380)
            _plot(fig2, key="m1_exp2_mur")

        for col, (lab, val) in zip(st.columns(4), [
            ("B (T)",        f"{B_op:.4f}"),
            ("μᵣ local",     f"{mr_op:.0f}"),
            ("μ (H/m)",      f"{mr_op*mu0:.2e}"),
            ("B/B_sat",      f"{B_op/Bsat*100:.1f}%"),
        ]):
            with col: st.metric(lab, val)

    # ════════════════════════════════════════════════════════════════════════
    # CONTEÚDO DA PÁGINA
    # ════════════════════════════════════════════════════════════════════════

    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown('<div class="mod-header">🔋 Circuitos Magnéticos</div>', unsafe_allow_html=True)
    st.markdown('<div class="mod-sub">MOD 01 &nbsp;·&nbsp; '
                'Introdução à Conversão Eletromecânica de Energia</div>',
                unsafe_allow_html=True)
    st.markdown("""
Este módulo estabelece os fundamentos eletromagnéticos para o estudo de todas as máquinas elétricas.
Parte da relação $i$-$H$ (Lei de Ampère) e avança pelos circuitos magnéticos equivalentes,
indutância, histerese e perdas no núcleo.
""")

    # ── 1. Relação i-H ────────────────────────────────────────────────────────
    st.markdown('<div class="sec-title">1 · Relação i–H — Lei Circuital de Ampère</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("""
**Regra da mão direita:** com o polegar no sentido de $i$, os dedos indicam o sentido das linhas de $\\vec{H}$.

A **lei circuital de Ampère** estabelece que a integral de linha de $\\vec{H}$ ao longo
de qualquer contorno fechado $C$ é igual à soma das correntes que atravessam a superfície delimitada:
""")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"\oint_C \vec{H} \cdot d\vec{l} = \sum_k N_k\, i_k")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("Para um **condutor isolado** a distância $r$:")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"H \cdot 2\pi r = i \quad\Rightarrow\quad H = \frac{i}{2\pi r}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("Considerando ângulo $\\theta$ entre $\\vec{H}$ e $d\\vec{l}$:")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"\oint \vec{H} \cdot d\vec{l} = \oint H\, dl\, \cos\theta = N\,i")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("Essa relação entre corrente e campo $H$ é a base para definir o "
                    "**circuito magnético equivalente**, apresentado na Seção 3.")
    with c2:
        _show(fig_regra_mao(), "Campo H ao redor de um condutor (regra da mão direita)")

    c1, c2 = st.columns([1, 1])
    with c1:
        _show(fig_campo_r(), "Campo H a distância r de um condutor isolado")
    with c2:
        _show(fig_ampere_contorno(), "Lei de Ampère — contorno fechado num núcleo toroidal")

    # ── 2. Relação B-H ────────────────────────────────────────────────────────
    st.markdown('<div class="sec-title">2 · Relação B–H — Permeabilidade Magnética</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([1.1, 1])
    with c1:
        st.markdown("""
A **densidade de fluxo magnético** $B$ (T = Wb/m²) relaciona-se com $H$ pela permeabilidade do meio:
""")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"B = \mu\,H = \mu_0\,\mu_r\,H")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("- $\\mu_0 = 4\\pi\\times10^{-7}$ H/m: permeabilidade do vácuo\n"
                    "- $\\mu_r$: permeabilidade relativa (adimensional)")
        st.markdown('<div class="def-box">', unsafe_allow_html=True)
        st.markdown("""
**Valores típicos de $\\mu_r$:**

| Material | $\\mu_r$ |
|----------|-----------|
| Ar, vácuo, Cu, Al | ≈ 1 |
| Ferrite | 100 – 1 000 |
| Aço elétrico (máquinas) | **2 000 – 6 000** |
""")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="nota-box">', unsafe_allow_html=True)
        st.markdown("⚠️ Para ferromagnéticos, $\\mu_r$ **não é constante**: varia com $H$ "
                    "(curva de magnetização não-linear) e com a história magnética do material "
                    "— efeito detalhado na Seção 5 (Histerese).")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        _plot(plotly_BH(), key="m1_fig_bh")

    # ── 3. Circuito Magnético Equivalente ─────────────────────────────────────
    st.markdown('<div class="sec-title">3 · Circuito Magnético Equivalente</div>',
                unsafe_allow_html=True)
    st.markdown("Combinando Ampère, $B=\\mu H$ e $\\phi=B\\,A$ obtém-se a **lei do circuito magnético**:")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"\mathcal{F} = N\,i \quad \text{(FMM, A·t)}")
        st.latex(r"\mathcal{R} = \frac{\ell}{\mu\,A} \quad \text{(relutância, A·t/Wb)}")
        st.latex(r"\phi = \frac{\mathcal{F}}{\mathcal{R}} = \frac{N\,i\,\mu\,A}{\ell}")
        st.markdown('</div>', unsafe_allow_html=True)
        _show(fig_circuito_mag(), "Núcleo toroidal: φ, ℱ e ℛ")
    with c2:
        st.markdown("**Analogia: circuito elétrico ↔ circuito magnético**")
        cc1, cc2 = st.columns(2)
        with cc1:
            st.image(schem_analogia_eletrico(), use_container_width=True)
            st.markdown('<div class="fig-cap">Circuito elétrico</div>', unsafe_allow_html=True)
        with cc2:
            st.image(schem_analogia_magnetico(), use_container_width=True)
            st.markdown('<div class="fig-cap">Circuito magnético</div>', unsafe_allow_html=True)
        st.markdown('<div class="def-box">', unsafe_allow_html=True)
        st.markdown("""
| Circuito Elétrico | Circuito Magnético |
|-------------------|--------------------|
| FEM $e$ (V) | FMM $\\mathcal{F}=Ni$ (A·t) |
| Corrente $i$ (A) | Fluxo $\\phi$ (Wb) |
| Resistência $R$ (Ω) | Relutância $\\mathcal{R}$ (A·t/Wb) |
| $e = R\\,i$ | $\\mathcal{F} = \\mathcal{R}\\,\\phi$ |
""")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="subsec">3.1 · Presença de Entreferro</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("Com entreferro $\\ell_g$, as relutâncias somam-se em série:")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"N\,i = (\mathcal{R}_c + \mathcal{R}_g)\,\phi")
        st.latex(r"\mathcal{R}_c = \frac{\ell_c}{\mu_r\mu_0 A_c}, \quad "
                 r"\mathcal{R}_g = \frac{\ell_g}{\mu_0 A_g}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="nota-box">', unsafe_allow_html=True)
        st.markdown("⚠️ **Dominância do entreferro:** com $\\mu_r=2000$, 1 mm de ar equivale "
                    "a 2 m de ferro de mesma seção — o entreferro domina a relutância total.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.image(schem_entreferro(), use_container_width=True)
        st.markdown('<div class="fig-cap">Circuito magnético equivalente com entreferro: '
                    'ℱ em série com ℛ_c e ℛ_g</div>', unsafe_allow_html=True)
    with c2:
        _show(fig_entreferro_geom(), "Geometria do núcleo com entreferro")

    st.markdown('<div class="subsec">3.2 · Máquina Rotativa e Frangeamento</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("""
Em máquinas rotativas, o entreferro separa estator e rotor.
O **frangeamento** (_fringing_) alarga as linhas de campo no ar, aumentando a área efetiva $A_g > A_c$.

Correção para polo retangular ($a\\times b$):
""")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"A_g \approx (a + \ell_g)(b + \ell_g)")
        st.latex(r"\mathcal{R}_g = \frac{\ell_g}{\mu_0 A_g}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        _show(fig_frangeamento(), "Máquina rotativa e frangeamento no entreferro")

    # ── 4. Indutância e Lei de Faraday ────────────────────────────────────────
    st.markdown('<div class="sec-title">4 · Indutância e Lei de Faraday</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("O **fluxo concatenado** $\\lambda$ (Wb·t) é o fluxo total em todas as espiras:")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"\lambda = N\,\phi = \frac{N^2}{\mathcal{R}}\,i = L\,i")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("A **indutância** $L$ (H = Wb/A):")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"L = \frac{\lambda}{i} = \frac{N^2}{\mathcal{R}} = \frac{N^2\,\mu\,A}{\ell}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("A **lei de Faraday** — FEM induzida pela variação de fluxo:")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"e = -\frac{d\lambda}{dt} = -N\frac{d\phi}{dt}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("Para $L$ constante (sistema linear):")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"e = L\frac{di}{dt}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        _show(fig_circuito_mag(), "Núcleo com N espiras — base para definição de λ e L")

    st.markdown('<div class="subsec">4.1 · Indutância Mútua e Energia Armazenada</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        _show(fig_acoplamento(), "Indutância mútua entre duas bobinas acopladas")
    with c2:
        st.markdown("Para **duas bobinas acopladas** num mesmo núcleo:")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"\lambda_1 = L_{11}\,i_1 + L_{12}\,i_2")
        st.latex(r"\lambda_2 = L_{21}\,i_1 + L_{22}\,i_2 \quad (L_{12}=L_{21})")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""
- $L_{11}$, $L_{22}$: **indutâncias próprias** (auto-induzidas)
- $L_{12} = L_{21}$: **indutância mútua** (reciprocidade de Neumann)
- Análise linear válida para $\\mu$ constante (região linear da curva $B$-$H$)
""")

    st.markdown("**Energia armazenada no campo magnético:**")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"W_L = \frac{1}{2}\,L\,i^2 = \frac{\lambda^2}{2L} = \frac{1}{2}\,\mathcal{R}\,\phi^2")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="nota-box">', unsafe_allow_html=True)
        st.markdown("A variação de $W_L$ com a posição do rotor é o mecanismo de "
                    "**geração de força e torque eletromagnético** — princípio que será "
                    "retomado nos módulos sobre máquinas CC, de indução e síncronas.")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        _plot(plotly_energia_indutiva(), key="m1_fig_energia")

    # ── 5. Histerese ─────────────────────────────────────────────────────────
    st.markdown('<div class="sec-title">5 · Histerese Magnética</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1.1, 1])
    with c1:
        _plot(plotly_histerese(), key="m1_fig_hist")
    with c2:
        st.markdown("""
A **histerese** é o fenômeno pelo qual o estado magnético do material depende da história
de magnetização, não apenas do campo atual $H$. Por isso, magnetização e desmagnetização
seguem trajetórias distintas no plano $B$-$H$, formando um **laço**.

**Grandezas do laço:**
- $B_r$ (T): **remanência** — $B$ remanescente quando $H=0$
- $H_c$ (A/m): **coercividade** — campo necessário para anular $B$
- $B_{sat}$ (T): **saturação** — valor máximo de $B$

| Tipo | $H_c$ | Aplicação |
|------|--------|-----------|
| Mole (_soft_) | baixo | Núcleos de máquinas e transformadores |
| Duro (_hard_) | alto | Ímãs permanentes |

A **área interna do laço** corresponde à energia dissipada como calor em cada ciclo de magnetização:
""")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"W_h = \oint H\,dB \quad\text{(área do laço)}")
        st.latex(r"P_h = k_h\,f\,B_{max}^n \quad (n \approx 1{,}6 \text{ a } 2)")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── 6. Correntes Parasitas ────────────────────────────────────────────────
    st.markdown('<div class="sec-title">6 · Correntes Parasitas e Perdas no Núcleo</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        _show(fig_parasita_geom(), "Correntes parasitas e laminação do núcleo")
    with c2:
        st.markdown("""
**Correntes parasitas** (_Eddy currents_) são induzidas no núcleo condutor
pela variação de $B$ no tempo, formando laços fechados que dissipam energia como calor (efeito Joule).

**Redução:**
- Material de **alta resistividade** (ferrite, aço silício): dificulta a circulação das correntes
- **Laminação**: chapas finas isoladas entre si interrompem os laços de corrente — como
  $P_e \\propto d^2$, reduzir a espessura $d$ das chapas diminui as perdas rapidamente

**Perdas por correntes parasitas** (por volume):
""")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"P_e = k_e\,f^2\,B_{max}^2\,d^2")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("**Perdas totais no núcleo** (perdas no ferro):")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"P_c = P_h + P_e = k_h\,f\,B_{max}^n + k_e\,f^2\,B_{max}^2")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="nota-box">', unsafe_allow_html=True)
    st.markdown("As perdas no núcleo ocorrem mesmo a vazio, pois dependem "
                "de $B_{max}$ e $f$, não da corrente de carga.")
    st.markdown('</div>', unsafe_allow_html=True)
    _plot(plotly_perdas_nucleo(), key="m1_fig_perdas")

    # ── Exploradores ──────────────────────────────────────────────────────────
    st.markdown('<div class="sec-title">🎛️ Exploradores Interativos</div>',
                unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Explorador 1 — Circuito Magnético",
                           "Explorador 2 — Curva B-H"])
    with tab1: exp_circuito()
    with tab2: exp_BH()

    # ── Referências ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📚 Referências")
    for r in [
        "CHAPMAN, S. J. *Fundamentos de Máquinas Elétricas*. McGraw-Hill, 5ª ed., 2013.",
        "UMANS, S. D. *Máquinas Elétricas de Fitzgerald e Kingsley*. McGraw-Hill, 7ª ed., 2014.",
        "KOSOW, I. *Máquinas Elétricas e Transformadores*. Globo, 14ª reimp., 2000.",
        "BIM, E. *Máquinas Elétricas e Acionamento*. Campus Elsevier, 2009.",
        "SEN, P. C. *Princípios de Máquinas Elétricas e Eletrônica de Potência*. Wiley, 3ª ed., 2013.",
        "JACOBINA, C.; LIMA, A. M. *Acionamentos de Máquinas Elétricas de Alto Desempenho*. "
        "XIV CBA, Natal, 2002.",
    ]:
        st.markdown(f'<div class="ref-item">• {r}</div>', unsafe_allow_html=True)
