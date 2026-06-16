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
import io
import schemdraw
import schemdraw.elements as elm


def run():
    # ── Constantes de cor ────────────────────────────────────────────────────
    AZ = "#3d8ef0"; RX = "#6c47ff"; VD = "#2ecc71"; LR = "#f39c12"
    CI = "#00bcd4"; CZ = "#aaaaaa"; BR = "#e8e8e8"
    BG = "#0e1117"; BG2 = "#1a2233"

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
.nota-box{background:rgba(243,156,18,.07);border-left:3px solid #f39c12;
          border-radius:0 8px 8px 0;padding:.65rem 1rem;margin:.55rem 0}
.ref-item{font-size:.82rem;opacity:.65;line-height:1.7;margin:.15rem 0}
</style>"""

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _buf(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        buf.seek(0); plt.close(fig); return buf

    def _show(fig, caption=""):
        st.image(_buf(fig), caption=caption, use_container_width=True)

    def _base(w=7, h=4):
        fig, ax = plt.subplots(figsize=(w, h))
        fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
        ax.tick_params(colors=CZ)
        ax.xaxis.label.set_color(CZ); ax.yaxis.label.set_color(CZ)
        for sp in ax.spines.values(): sp.set_edgecolor("#444")
        return fig, ax

    # ════════════════════════════════════════════════════════════════════════
    # FIGURAS
    # ════════════════════════════════════════════════════════════════════════

    def fig_regra_mao():
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
        ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5)
        ax.set_aspect("equal"); ax.axis("off")
        ax.add_patch(plt.Circle((0, 0), .22, color=AZ, zorder=5))
        ax.plot(0, 0, "w.", ms=10, zorder=6)
        for r, a in zip([.7, 1.15, 1.65, 2.1], [.9, .75, .65, .55]):
            t = np.linspace(0, 2*np.pi, 300)
            ax.plot(r*np.cos(t), r*np.sin(t), color=AZ, alpha=a, lw=1.4)
            idx = 60
            dx = -r*np.sin(t[idx])*.001; dy = r*np.cos(t[idx])*.001
            ax.annotate("", xy=(r*np.cos(t[idx])+dx*300, r*np.sin(t[idx])+dy*300),
                        xytext=(r*np.cos(t[idx]), r*np.sin(t[idx])),
                        arrowprops=dict(arrowstyle="->", color=AZ, lw=1.2))
        ax.annotate("$H$", xy=(1.9*np.cos(np.pi/5), 1.9*np.sin(np.pi/5)),
                    fontsize=14, color=BR, ha="center")
        ax.text(0, .38, "$i$", fontsize=13, color=BR, ha="center", va="bottom")
        ax.annotate("", xy=(1.15, 0), xytext=(.22, 0),
                    arrowprops=dict(arrowstyle="-|>", color=CI, lw=1.2))
        ax.text(.68, .12, "$r$", fontsize=12, color=CI)
        ax.set_title("Campo $H$ ao redor de um condutor\n(regra da mão direita)",
                     color=BR, fontsize=9, pad=6)
        fig.tight_layout(); return fig

    def fig_ampere_contorno():
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
        ax.set_xlim(-3, 3); ax.set_ylim(-2.2, 2.2)
        ax.set_aspect("equal"); ax.axis("off")
        outer = mpatches.FancyBboxPatch((-2.2, -1.5), 4.4, 3., boxstyle="round,pad=.3",
                                         lw=1.5, ec=CZ, fc=BG2, zorder=2)
        inner = mpatches.FancyBboxPatch((-1., -.7), 2., 1.4, boxstyle="round,pad=.1",
                                         lw=1.5, ec=CZ, fc=BG, zorder=3)
        ax.add_patch(outer); ax.add_patch(inner)
        t = np.linspace(0, 2*np.pi, 400); rm = 1.45
        ax.plot(rm*np.cos(t), rm*np.sin(t)*.85, "--", color=LR, lw=1.5, zorder=4)
        idx = 120
        ax.annotate("", xy=(rm*np.cos(t[idx+3]), rm*.85*np.sin(t[idx+3])),
                    xytext=(rm*np.cos(t[idx]), rm*.85*np.sin(t[idx])),
                    arrowprops=dict(arrowstyle="->", color=LR, lw=1.5), zorder=5)
        for x0 in np.linspace(-1.8, 1.8, 8):
            ax.plot([x0, x0], [1.5, 2.], color=AZ, lw=2, zorder=5)
            ax.plot([x0, x0], [-2., -1.5], color=AZ, lw=2, zorder=5)
        ax.text(0, 0, "$N$ espiras", color=BR, fontsize=10, ha="center", va="center", zorder=5)
        ax.text(rm+.25, .6, "$C$", color=LR, fontsize=13, zorder=6)
        ax.text(-2.85, 1.6, "$i$", color=AZ, fontsize=13)
        ax.text(0, -2.1, r"$\oint_C \vec{H}\cdot d\vec{l} = N\,i$",
                color=BR, fontsize=13, ha="center", va="bottom",
                bbox=dict(boxstyle="round,pad=.3", fc=BG2, ec=AZ, alpha=.8))
        ax.set_title("Lei Circuital de Ampère — contorno fechado", color=BR, fontsize=9, pad=6)
        fig.tight_layout(); return fig

    def fig_campo_r():
        fig, ax = plt.subplots(figsize=(6, 3.5))
        fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
        ax.set_xlim(-3, 3); ax.set_ylim(-2, 2); ax.set_aspect("equal"); ax.axis("off")
        ax.add_patch(plt.Circle((0, 0), .18, color=AZ, zorder=5))
        ax.plot(0, 0, "w.", ms=8, zorder=6)
        for r in [.6, 1., 1.4, 1.8]:
            t = np.linspace(0, 2*np.pi, 300)
            ax.plot(r*np.cos(t), r*np.sin(t), color=AZ, alpha=max(.3, 1-r*.35), lw=1.3)
        ang = np.pi/4; xp, yp = 1.4*np.cos(ang), 1.4*np.sin(ang)
        ax.annotate("", xy=(xp, yp), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=CI, lw=1.4))
        ax.text(xp/2+.1, yp/2+.1, "$r$", color=CI, fontsize=13)
        ax.text(1.7, .4, r"$\oint \vec{H}\cdot d\vec{l} = H\cdot 2\pi r = i$",
                color=BR, fontsize=11)
        ax.text(1.7, -.45, r"$\Rightarrow\quad H = \dfrac{i}{2\pi r}$", color=BR, fontsize=11)
        ax.set_title("Campo magnético a distância $r$ de um condutor", color=BR, fontsize=9, pad=6)
        fig.tight_layout(); return fig

    def fig_BH():
        fig, ax = _base(6, 4)
        H = np.linspace(0, 2000, 400)
        B_lin = 4*np.pi*1e-7 * H * 1e3
        ax.plot(H, B_lin/B_lin.max()*.25, "--", color=CI, lw=1.8,
                label="Ar / cobre ($\\mu_r=1$)")
        Bsat = 1.8; mur = 3500
        B_fe = Bsat*(1 - np.exp(-mur*4*np.pi*1e-7*H/Bsat))
        ax.plot(H, B_fe, color=AZ, lw=2.2,
                label="Ferromagnético ($\\mu_r\\approx 2000$–$6000$)")
        idx = 60
        ax.annotate("$\\mu$ variável\n(região não-linear)", xy=(H[idx], B_fe[idx]),
                    xytext=(400, .6), color=LR, fontsize=8,
                    arrowprops=dict(arrowstyle="->", color=LR))
        ax.axhline(Bsat, color=CZ, lw=.8, ls=":")
        ax.text(1800, Bsat+.05, "$B_{sat}$", color=CZ, fontsize=9)
        ax.set_xlabel("$H$ (A/m)"); ax.set_ylabel("$B$ (T)")
        ax.legend(fontsize=9, facecolor=BG2, edgecolor=CZ, labelcolor=BR)
        ax.set_title("Relação $B$-$H$: linear vs. ferromagnético", color=BR, fontsize=9)
        ax.set_xlim(0, 2000); ax.set_ylim(0, 2.1); fig.tight_layout(); return fig

    def fig_circuito_mag():
        fig, ax = plt.subplots(figsize=(6.5, 4.5))
        fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
        ax.set_xlim(-3.5, 3.5); ax.set_ylim(-2.5, 2.5)
        ax.set_aspect("equal"); ax.axis("off")
        t = np.linspace(0, 2*np.pi, 400); Ro, Ri = 2., 1.1
        ax.fill_between(Ro*np.cos(t), Ro*np.sin(t), Ri*np.cos(t), Ri*np.sin(t),
                        color="#1a3055", zorder=2)
        ax.plot(Ro*np.cos(t), Ro*np.sin(t), color=CZ, lw=1.2, zorder=3)
        ax.plot(Ri*np.cos(t), Ri*np.sin(t), color=CZ, lw=1.2, zorder=3)
        for ang in np.linspace(np.pi*.25, np.pi*.75, 9):
            xc, yc = 1.55*np.cos(ang), 1.55*np.sin(ang)
            ax.add_patch(mpatches.Ellipse((xc, yc), .35, .18,
                                          angle=np.degrees(ang)+90,
                                          color=AZ, zorder=4, alpha=.85))
        tf = np.linspace(np.pi*.1, np.pi*1.85, 200); rf = 1.55
        ax.plot(rf*np.cos(tf), rf*np.sin(tf), color=VD, lw=2, zorder=5, alpha=.8)
        ax.annotate("", xy=(rf*np.cos(tf[-1]+.05), rf*np.sin(tf[-1]+.05)),
                    xytext=(rf*np.cos(tf[-1]), rf*np.sin(tf[-1])),
                    arrowprops=dict(arrowstyle="->", color=VD, lw=2), zorder=6)
        ax.text(-.3, .15, "$\\phi$", color=VD, fontsize=16, zorder=7)
        ax.text(0, 2.3, "$N$ espiras", color=AZ, fontsize=10, ha="center")
        ax.text(0, -2.3,
                r"$\mathcal{F}=N\,i$   $\mathcal{R}=\frac{\ell}{\mu A}$   "
                r"$\phi=\frac{\mathcal{F}}{\mathcal{R}}$",
                color=BR, fontsize=10, ha="center", va="top",
                bbox=dict(boxstyle="round,pad=.4", fc=BG2, ec=AZ, alpha=.85))
        ax.set_title("Circuito magnético — núcleo toroidal", color=BR, fontsize=9, pad=6)
        fig.tight_layout(); return fig

    def fig_analogia():
        fig, axes = plt.subplots(1, 2, figsize=(9, 4))
        fig.patch.set_facecolor(BG)
        for col, ax in enumerate(axes):
            ax.set_facecolor(BG); ax.axis("off")
            titulo = ["Circuito Elétrico", "Circuito Magnético"][col]
            cor    = [CI, AZ][col]
            ax.set_title(titulo, color=cor, fontsize=13, fontweight="bold", pad=8)
            linhas = [("Fonte",    "FEM ($e$)",          "FMM ($\\mathcal{F}=Ni$)"),
                      ("Produzindo","Corrente ($i$)",     "Fluxo ($\\phi$)"),
                      ("Limitador","Resistência ($R$)",   "Relutância ($\\mathcal{R}$)"),
                      ("Lei",      "$e = R\\,i$",         "$\\mathcal{F}=\\mathcal{R}\\,\\phi$")]
            for k, (nome, el, em) in enumerate(linhas):
                y = .82 - k*.19; val = el if col == 0 else em
                ax.text(.08, y, f"{nome}:", color=CZ, fontsize=9,
                        ha="left", va="center", transform=ax.transAxes)
                ax.text(.58, y, val, color=BR, fontsize=10,
                        ha="center", va="center", transform=ax.transAxes,
                        bbox=dict(boxstyle="round,pad=.25",
                                  fc=("#1a2a1a" if col == 0 else "#1a3055"),
                                  ec=(VD if col == 0 else AZ), alpha=.8))
            ax_ins = ax.inset_axes([.05, .02, .9, .2])
            ax_ins.set_facecolor(BG); ax_ins.axis("off")
            with schemdraw.Drawing(canvas=ax_ins) as d:
                d.config(fontsize=9, color=BR)
                lbl = "$e$" if col == 0 else "$\\mathcal{F}$"
                ec  = VD   if col == 0 else AZ
                V = d.add(elm.SourceV().label(lbl, loc="left").color(ec))
                d.add(elm.Line().right())
                d.add(elm.Resistor().label("$R$" if col == 0 else "$\\mathcal{R}$",
                                            loc="top").color(CI if col == 0 else AZ))
                d.add(elm.Line().down())
                d.add(elm.Line().left())
                d.add(elm.Line().up().toy(V.start))
        fig.suptitle("Analogia: Circuito Elétrico ↔ Circuito Magnético",
                     color=BR, fontsize=11, y=1.01)
        fig.tight_layout(); return fig

    def fig_entreferro():
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
        fig.patch.set_facecolor(BG)
        # — esboço físico —
        ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
        ax.set_xlim(0, 10); ax.set_ylim(0, 8)
        ax.set_title("Geometria — Núcleo com Entreferro", color=BR, fontsize=9)
        for pts, c in [([(1,1),(9,1),(9,2.2),(1,2.2)], "#1a3055"),
                       ([(1,2.2),(2.5,2.2),(2.5,6.4),(1,6.4)], "#1a3055"),
                       ([(7.5,2.2),(9,2.2),(9,6.4),(7.5,6.4)], "#1a3055"),
                       ([(1,6.4),(4.5,6.4),(4.5,7.4),(1,7.4)], "#1a3055"),
                       ([(5.5,6.4),(9,6.4),(9,7.4),(5.5,7.4)], "#1a3055")]:
            ax.add_patch(plt.Polygon(pts, color=c, ec=CZ, lw=1.2, zorder=2))
        ax.add_patch(Rectangle((4.5,6.4), 1., 1., color=BG, ec=LR, lw=1.5, ls="--", zorder=3))
        ax.text(5., 6.1, "Entreferro\n$\\ell_g$", color=LR, fontsize=7, ha="center", va="top")
        for y0 in np.linspace(2.6, 5.8, 7):
            ax.add_patch(mpatches.Ellipse((1.75, y0), .85, .35,
                                          color=AZ, zorder=4, alpha=.8))
        ax.text(.4, 4.2, "$N$\nespiras", color=AZ, fontsize=8, ha="center")
        xs = [2.25,2.25,5.,7.75,7.75,5.,4.7]
        ys = [4.1, 6.9,6.9,6.9, 4.1, 4.1,4.1]
        ax.plot(xs, ys, "--", color=VD, lw=1.5, alpha=.7)
        ax.annotate("", xy=(4.8,4.1), xytext=(4.5,4.1),
                    arrowprops=dict(arrowstyle="->", color=VD, lw=1.5))
        ax.text(3.8, 3.7, "$\\phi$", color=VD, fontsize=12)
        # — circuito equivalente —
        ax2 = axes[1]; ax2.set_facecolor(BG); ax2.axis("off")
        ax2.set_title("Circuito Magnético Equivalente", color=BR, fontsize=9)
        with schemdraw.Drawing(canvas=ax2) as d:
            d.config(fontsize=10, color=BR)
            F = d.add(elm.SourceV().label("$\\mathcal{F}=Ni$", loc="left").color(AZ))
            d.add(elm.Line().right(1.5))
            d.add(elm.Resistor().label("$\\mathcal{R}_c$", loc="top").color(CZ))
            d.add(elm.Line().right(1.5))
            d.add(elm.Resistor().label("$\\mathcal{R}_g$", loc="top").color(LR))
            d.add(elm.Line().down(3))
            d.add(elm.Line().left().tox(F.start))
            d.add(elm.Line().up().toy(F.start))
        ax2.text(.5, .08, r"$N\,i = (\mathcal{R}_c+\mathcal{R}_g)\,\phi$",
                 color=BR, fontsize=11, ha="center", va="bottom", transform=ax2.transAxes,
                 bbox=dict(boxstyle="round,pad=.4", fc=BG2, ec=AZ, alpha=.8))
        fig.suptitle("Circuito Magnético com Entreferro", color=BR, fontsize=11)
        fig.tight_layout(); return fig

    def fig_frangeamento():
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
        fig.patch.set_facecolor(BG)
        # — seção da máquina rotativa —
        ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
        ax.set_xlim(-3.5, 3.5); ax.set_ylim(-3.5, 3.5); ax.set_aspect("equal")
        ax.set_title("Máquina Elétrica Rotativa (seção)", color=BR, fontsize=9)
        ax.add_patch(plt.Circle((0,0), 3.,  color="#1a3055", ec=CZ, lw=1.5, zorder=2))
        ax.add_patch(plt.Circle((0,0), 2.2, color=BG,       ec=CZ, lw=1.,  zorder=3))
        ax.add_patch(plt.Circle((0,0), 1.9, color="#1a3055", ec=CZ, lw=1.2, zorder=4))
        ax.add_patch(plt.Circle((0,0), 1.1, color=BG,       ec=CZ, lw=.8,  zorder=5))
        ax.add_patch(plt.Circle((0,0), .25, color=CZ, zorder=6))
        t = np.linspace(0, 2*np.pi, 200)
        ax.fill_between(2.2*np.cos(t), 2.2*np.sin(t),
                        1.9*np.cos(t), 1.9*np.sin(t), color=LR, alpha=.25, zorder=3)
        ax.text(0, 2.55, "Estator", color=BR, fontsize=8, ha="center")
        ax.text(0, 1.5,  "Rotor",   color=BR, fontsize=8, ha="center")
        ax.text(2.5, .5, "Entreferro\n($\\ell_g$)", color=LR, fontsize=7, ha="center")
        # — frangeamento —
        ax2 = axes[1]; ax2.set_facecolor(BG); ax2.axis("off")
        ax2.set_xlim(0, 10); ax2.set_ylim(0, 8)
        ax2.set_title("Efeito de Frangeamento no Entreferro", color=BR, fontsize=9)
        ax2.add_patch(Rectangle((3, 5.5), 4, 2, color="#1a3055", ec=CZ, lw=1.2))
        ax2.add_patch(Rectangle((3,  .8), 4, 2, color="#1a3055", ec=CZ, lw=1.2))
        for x in np.linspace(3.6, 6.4, 5):
            ax2.annotate("", xy=(x, 5.5), xytext=(x, 2.8),
                         arrowprops=dict(arrowstyle="-|>", color=VD, lw=1.2, mutation_scale=10))
        for xb in [3., 7.]:
            t2 = np.linspace(0, np.pi, 50)
            side = -1 if xb < 5 else 1
            ax2.plot(xb + side*.5 + (-side)*.7*np.sin(t2),
                     4.15 + 1.35*np.cos(t2), "--", color=RX, lw=1.3, alpha=.8)
        ax2.text(5., 4.15, "$\\ell_g$", color=LR, fontsize=12, ha="center")
        ax2.annotate("", xy=(2.2, 5.5), xytext=(7.8, 5.5),
                     arrowprops=dict(arrowstyle="<->", color=RX, lw=1.2))
        ax2.text(5., 5.75, "$A_{ef}>A_c$ (frangeamento)", color=RX, fontsize=8, ha="center")
        ax2.text(5., .2, r"$\mathcal{R}_g=\frac{\ell_g}{\mu_0 A_g}$",
                 color=BR, fontsize=9, ha="center",
                 bbox=dict(boxstyle="round,pad=.3", fc=BG2, ec=AZ, alpha=.8))
        fig.suptitle("Máquina Rotativa e Frangeamento", color=BR, fontsize=11)
        fig.tight_layout(); return fig

    def fig_indutancia():
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        fig.patch.set_facecolor(BG)
        ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
        ax.set_xlim(0, 10); ax.set_ylim(0, 8)
        ax.set_title("Fluxo Concatenado $\\lambda=N\\phi$", color=BR, fontsize=9)
        for pts, c in [([(1,1),(9,1),(9,2),(1,2)], "#1a3055"),
                       ([(1,2),(2.5,2),(2.5,7),(1,7)], "#1a3055"),
                       ([(7.5,2),(9,2),(9,7),(7.5,7)], "#1a3055"),
                       ([(1,7),(9,7),(9,6),(1,6)], "#1a3055")]:
            ax.add_patch(plt.Polygon(pts, color=c, ec=CZ, lw=1.1, zorder=2))
        for y0 in np.linspace(2.5, 6., 8):
            ax.add_patch(mpatches.Ellipse((1.75, y0), 1., .4,
                                          color=AZ, zorder=4, alpha=.8))
        ax.text(.5, 4.2, "$N$", color=AZ, fontsize=14, ha="center")
        ax.plot([2.5, 2.5, 7.5, 7.5, 5.], [4., 6.5, 6.5, 4., 4.],
                color=VD, lw=2, alpha=.8)
        ax.annotate("", xy=(5.1, 4.), xytext=(4.8, 4.),
                    arrowprops=dict(arrowstyle="->", color=VD, lw=2))
        ax.text(5., 5.2, "$\\phi$", color=VD, fontsize=14, ha="center")
        ax.text(5., .3,
                r"$\lambda=N\phi=\frac{N^2}{\mathcal{R}}i=Li$"
                "\n" r"$L=\frac{N^2}{\mathcal{R}}=\frac{N^2\mu A}{\ell}$",
                color=BR, fontsize=9, ha="center", va="bottom",
                bbox=dict(boxstyle="round,pad=.35", fc=BG2, ec=AZ, alpha=.85))
        ax2 = axes[1]; ax2.set_facecolor(BG); ax2.axis("off")
        ax2.set_title("Lei de Faraday e Energia", color=BR, fontsize=9)
        eqs = [(r"$e=-\frac{d\lambda}{dt}=-N\frac{d\phi}{dt}$", "FEM induzida"),
               (r"$e=L\frac{di}{dt}$",                          "para $L$ constante"),
               (r"$L=\frac{N^2}{\mathcal{R}}$",                 "Indutância [H = Wb/A]"),
               (r"$W_L=\frac{1}{2}Li^2$",                       "Energia armazenada")]
        for k, (eq, desc) in enumerate(eqs):
            y = .88 - k*.22
            ax2.text(.5, y, eq, color=BR, fontsize=11, ha="center", va="center",
                     transform=ax2.transAxes,
                     bbox=dict(boxstyle="round,pad=.3", fc=BG2, ec=AZ, alpha=.7))
            ax2.text(.5, y-.09, desc, color=CZ, fontsize=8, ha="center", va="center",
                     transform=ax2.transAxes, style="italic")
        fig.suptitle("Indutância e Lei de Faraday", color=BR, fontsize=11)
        fig.tight_layout(); return fig

    def fig_indutancia_mutua():
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
        fig.patch.set_facecolor(BG)
        ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
        ax.set_xlim(0, 10); ax.set_ylim(0, 8)
        ax.set_title("Indutância Própria e Mútua", color=BR, fontsize=9)
        for pts, c in [([(0.5,1),(9.5,1),(9.5,2),(0.5,2)], "#1a3055"),
                       ([(0.5,2),(2.,2),(2.,7),(0.5,7)],   "#1a3055"),
                       ([(8.,2),(9.5,2),(9.5,7),(8.,7)],   "#1a3055"),
                       ([(0.5,7),(9.5,7),(9.5,6),(0.5,6)], "#1a3055")]:
            ax.add_patch(plt.Polygon(pts, color=c, ec=CZ, lw=1.1, zorder=2))
        for y0 in np.linspace(2.5, 5.8, 7):
            ax.add_patch(mpatches.Ellipse((1.25, y0), 1., .38,
                                          color=AZ, zorder=4, alpha=.85))
        ax.text(.05, 4.1, "$N_1\\ i_1$", color=AZ, fontsize=9, ha="left")
        for y0 in np.linspace(2.5, 5.8, 7):
            ax.add_patch(mpatches.Ellipse((8.75, y0), 1., .38,
                                          color=VD, zorder=4, alpha=.85))
        ax.text(9.6, 4.1, "$N_2\\ i_2$", color=VD, fontsize=9, ha="right")
        ax.plot([2., 2., 8., 8., 5.], [4.1, 6.5, 6.5, 4.1, 4.1],
                color=RX, lw=2, alpha=.8)
        ax.annotate("", xy=(5.1, 4.1), xytext=(4.9, 4.1),
                    arrowprops=dict(arrowstyle="->", color=RX, lw=2))
        ax.text(5., 5.4, "$\\phi_{12}$", color=RX, fontsize=12, ha="center")
        ax.text(5., .3,
                r"$\lambda_1=L_{11}i_1+L_{12}i_2$" + "\n" +
                r"$\lambda_2=L_{21}i_1+L_{22}i_2$" + "\n" +
                "$L_{12}=L_{21}$ (reciprocidade)",
                color=BR, fontsize=9, ha="center", va="bottom",
                bbox=dict(boxstyle="round,pad=.35", fc=BG2, ec=RX, alpha=.85))
        ax2 = axes[1]; ax2.set_facecolor(BG)
        ax2.set_title("Energia Armazenada $W_L=\\frac{1}{2}Li^2$", color=BR, fontsize=9)
        i_a = np.linspace(0, 4, 200); W_a = .5*.5*i_a**2
        ax2.plot(i_a, W_a, color=AZ, lw=2)
        ax2.fill_between(i_a, W_a, alpha=.15, color=AZ)
        ax2.set_xlabel("$i$ (A)", color=BR); ax2.set_ylabel("$W_L$ (J)", color=BR)
        ax2.tick_params(colors=CZ)
        for sp in ax2.spines.values(): sp.set_edgecolor("#444")
        ax2.set_facecolor(BG)
        fig.suptitle("Indutância Mútua e Energia", color=BR, fontsize=11)
        fig.tight_layout(); return fig

    def fig_histerese():
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        fig.patch.set_facecolor(BG)
        Hmax = 1000; Bsat = 1.7
        def branch(H, hc=200, upper=True):
            s = 1 if upper else -1
            return Bsat * np.tanh((H + s*hc) / (Hmax*.4))
        Hp = np.linspace(-Hmax, Hmax, 500)
        Hn = np.linspace(Hmax, -Hmax, 500)
        for i, (ax, title) in enumerate(zip(axes, ["Laço de Histerese",
                                                     "Laços para Diferentes Amplitudes"])):
            ax.set_facecolor(BG)
            ax.axhline(0, color=CZ, lw=.6); ax.axvline(0, color=CZ, lw=.6)
            ax.set_xlabel("$H$ (A/m)", color=BR); ax.set_ylabel("$B$ (T)", color=BR)
            ax.tick_params(colors=CZ)
            for sp in ax.spines.values(): sp.set_edgecolor("#444")
            ax.set_xlim(-Hmax, Hmax); ax.set_ylim(-2., 2.)
            ax.set_title(title, color=BR, fontsize=9)
            if i == 0:
                ax.plot(Hp, branch(Hp, upper=True),  color=AZ, lw=2.2, label="Magnetização")
                ax.plot(Hn, branch(Hn, upper=False), color=RX, lw=2.2, label="Desmagnetização")
                ax.fill_between(np.concatenate([Hp, Hn]),
                                np.concatenate([branch(Hp), branch(Hn, upper=False)]),
                                alpha=.1, color=AZ)
                ax.annotate("$B_r$", xy=(0, 1.2),  xytext=(200, .6),  color=VD, fontsize=8,
                            arrowprops=dict(arrowstyle="->", color=VD))
                ax.annotate("$H_c$", xy=(200, 0), xytext=(350, .45), color=LR, fontsize=8,
                            arrowprops=dict(arrowstyle="->", color=LR))
                ax.legend(fontsize=8, facecolor=BG2, edgecolor=CZ, labelcolor=BR,
                          loc="lower right")
            else:
                cores = [CI, AZ, RX, LR]
                for k, Ha in enumerate([250, 500, 750, Hmax]):
                    Hp2 = np.linspace(-Ha, Ha, 400)
                    Hn2 = np.linspace(Ha, -Ha, 400)
                    hc2 = 200*(Ha/Hmax)**.5
                    ax.plot(Hp2, Bsat*np.tanh((Hp2+hc2)/(Ha*.45)), color=cores[k], lw=1.6, alpha=.85)
                    ax.plot(Hn2, Bsat*np.tanh((Hn2-hc2)/(Ha*.45)), color=cores[k], lw=1.6, alpha=.85)
                ax.text(0, -1.85, "Área do laço ∝ Perda $P_h$ por ciclo",
                        color=CZ, fontsize=8, ha="center", style="italic")
        fig.suptitle("Histerese Magnética — Curva $B$-$H$", color=BR, fontsize=11)
        fig.tight_layout(); return fig

    def fig_parasita():
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        fig.patch.set_facecolor(BG)
        ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
        ax.set_xlim(0, 10); ax.set_ylim(0, 8)
        ax.set_title("Correntes Parasitas e Laminação", color=BR, fontsize=9)
        ax.add_patch(Rectangle((.3, 1.5), 3.5, 5., color="#1a3055", ec=CZ, lw=1.2))
        ax.text(2.05, 7., "Núcleo Sólido", color=BR, fontsize=8, ha="center")
        for cy in [3., 4.5, 6.]:
            t = np.linspace(0, 2*np.pi, 100)
            ax.plot(2.05+1.2*np.cos(t), cy+.7*np.sin(t), color=LR, lw=1.5, alpha=.85)
            ax.annotate("", xy=(2.05+1.2*np.cos(.1), cy+.7*np.sin(.1)),
                        xytext=(2.05+1.2*np.cos(0), cy+.7*np.sin(0)),
                        arrowprops=dict(arrowstyle="->", color=LR, lw=1.2))
        ax.text(2.05, 1., "$i_e$ (correntes\nparasitas)", color=LR, fontsize=7, ha="center")
        ax.annotate("", xy=(2.05, 6.8), xytext=(2.05, 5.5),
                    arrowprops=dict(arrowstyle="-|>", color=VD, lw=2))
        ax.text(2.55, 6.2, "$B$", color=VD, fontsize=12)
        x0 = 5.5; n = 8; wl = 3.2/n
        for k in range(n):
            c = "#1a3055" if k % 2 == 0 else "#0e2240"
            ax.add_patch(Rectangle((x0+k*wl, 1.5), wl*.82, 5., color=c, ec=CZ, lw=.6))
        ax.text(x0+1.6, 7., "Núcleo Laminado", color=BR, fontsize=8, ha="center")
        ax.text(x0+1.6, 1., "Correntes\nreduzidas", color=VD, fontsize=7, ha="center")
        ax.annotate("", xy=(x0+1.6, 6.8), xytext=(x0+1.6, 5.5),
                    arrowprops=dict(arrowstyle="-|>", color=VD, lw=2))
        ax.text(x0+2.15, 6.2, "$B$", color=VD, fontsize=12)
        ax2 = axes[1]; ax2.set_facecolor(BG)
        ax2.set_title("Perdas no Núcleo vs. Frequência", color=BR, fontsize=9)
        f = np.linspace(10, 400, 300); Bm = 1.5
        Ph = .005*f*Bm**1.8; Pe = .000012*f**2*Bm**2; Pc = Ph + Pe
        ax2.plot(f, Ph, "--", color=AZ, lw=2.,  label="Histerese $P_h$")
        ax2.plot(f, Pe, "--", color=LR, lw=2.,  label="Corrente parasita $P_e$")
        ax2.plot(f, Pc, "-",  color=BR, lw=2.5, label="Total $P_c=P_h+P_e$")
        ax2.fill_between(f, Ph, alpha=.12, color=AZ)
        ax2.fill_between(f, Pe, alpha=.12, color=LR)
        ax2.set_xlabel("$f$ (Hz)", color=BR); ax2.set_ylabel("Perdas (W/kg)", color=BR)
        ax2.legend(fontsize=8, facecolor=BG2, edgecolor=CZ, labelcolor=BR)
        ax2.tick_params(colors=CZ)
        for sp in ax2.spines.values(): sp.set_edgecolor("#444")
        ax2.set_facecolor(BG)
        ax2.text(180, .07,
                 r"$P_c=P_h+P_e$" + "\n" + r"$P_h\propto f B_{max}^n$" + "\n" +
                 r"$P_e\propto f^2 B_{max}^2$",
                 color=BR, fontsize=8, va="bottom",
                 bbox=dict(boxstyle="round,pad=.3", fc=BG2, ec=AZ, alpha=.8))
        fig.suptitle("Correntes Parasitas e Perdas no Núcleo", color=BR, fontsize=11)
        fig.tight_layout(); return fig

    # ════════════════════════════════════════════════════════════════════════
    # EXPLORADORES
    # ════════════════════════════════════════════════════════════════════════

    def exp_circuito():
        st.markdown("**Ajuste os parâmetros do circuito magnético:**")
        c1, c2, c3 = st.columns(3)
        with c1:
            N  = st.slider("Espiras $N$",         10, 1000, 200, step=10)
            i  = st.slider("Corrente $i$ (A)",    .1,  20.,  2., step=.1)
        with c2:
            mur  = st.slider("$\\mu_r$",            1, 6000, 2000, step=50)
            A_c  = st.slider("Seção $A$ (cm²)",    1.,  50.,  10., step=.5)
        with c3:
            l_c  = st.slider("Comprimento $\\ell$ (cm)", 5., 100., 30., step=1.)
            lg   = st.slider("Entreferro $\\ell_g$ (mm)", 0.,  10.,   0., step=.1)

        mu0 = 4*np.pi*1e-7
        A = A_c*1e-4; l = l_c*1e-2; lg_m = lg*1e-3
        Rc = l/(mur*mu0*A); Rg = lg_m/(mu0*A) if lg_m > 0 else 0; Rt = Rc + Rg
        FMM = N*i; phi = FMM/Rt; B = phi/A; Hc = B/(mur*mu0); WL = .5*(N**2/Rt)*i**2

        cols = st.columns(5)
        for col, (lab, val) in zip(cols, [
            ("$\\mathcal{F}$ (A·t)", f"{FMM:.1f}"),
            ("$\\phi$ (mWb)",        f"{phi*1e3:.3f}"),
            ("$B$ (T)",              f"{B:.4f}"),
            ("$\\mathcal{R}$ (A·t/Wb)", f"{Rt:.2e}"),
            ("$W_L$ (mJ)",           f"{WL*1e3:.2f}"),
        ]):
            with col: st.metric(lab, val)

        fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
        fig.patch.set_facecolor(BG)
        i_a = np.linspace(0, i*1.6+.1, 200); phi_a = N*i_a/Rt
        for ax_, xs, ys, xl, yl, tit, xv, yv in [
            (axes[0], i_a, phi_a*1e3, "$i$ (A)", "$\\phi$ (mWb)",
             "Fluxo vs. Corrente", i, phi*1e3),
            (axes[1], Hc*i_a/max(i,1e-9), B*i_a/max(i,1e-9),
             "$H$ (A/m)", "$B$ (T)", "Ponto B-H (linear)", Hc, B),
        ]:
            ax_.set_facecolor(BG)
            ax_.plot(xs, ys, color=AZ, lw=2)
            ax_.axvline(xv, color=LR, lw=1.5, ls="--", alpha=.8)
            ax_.axhline(yv, color=LR, lw=1.5, ls="--", alpha=.8)
            ax_.plot(xv, yv, "o", color=LR, ms=8, zorder=5)
            ax_.set_xlabel(xl, color=BR); ax_.set_ylabel(yl, color=BR)
            ax_.set_title(tit, color=BR, fontsize=9)
            ax_.tick_params(colors=CZ)
            for sp in ax_.spines.values(): sp.set_edgecolor("#444")
        fig.tight_layout(); _show(fig)
        if lg > 0:
            st.info(f"ℛ_c = {Rc:.2e} A·t/Wb  |  ℛ_g = {Rg:.2e} A·t/Wb  |  "
                    f"ℛ_g/ℛ_c = {Rg/Rc:.1f}×  — o entreferro domina!")

    def exp_BH():
        st.markdown("**Ajuste os parâmetros da curva de magnetização:**")
        c1, c2 = st.columns(2)
        with c1:
            mur_max  = st.slider("$\\mu_r$ máxima (pico)",  500, 8000, 3000, step=100)
            Bsat     = st.slider("$B_{sat}$ (T)",            .5,  2.2,  1.8, step=.05)
        with c2:
            H_op     = st.slider("Ponto de operação $H$ (A/m)", 10, 4000, 500, step=10)
            show_hist = st.checkbox("Mostrar laço de histerese simplificado", value=False)

        mu0 = 4*np.pi*1e-7
        H_a = np.linspace(0, 5000, 600)
        def Bmag(H, mr, Bs):
            mi = mr*mu0; a = Bs/mi; return Bs*H/(a+H)
        B_a = Bmag(H_a, mur_max, Bsat); B_op = Bmag(H_op, mur_max, Bsat)
        dBdH = np.gradient(B_a, H_a); mur_loc = dBdH/mu0
        mr_op = float(np.interp(H_op, H_a, mur_loc))

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        fig.patch.set_facecolor(BG)
        ax = axes[0]; ax.set_facecolor(BG)
        ax.plot(H_a, B_a, color=AZ, lw=2.2, label="$B$-$H$ ferromagnético")
        if show_hist:
            Hc2 = H_op*.15
            ax.plot(H_a, Bmag(H_a-Hc2, mur_max*.8, Bsat),
                    "--", color=RX, lw=1.4, alpha=.7, label="Laço superior")
            ax.plot(H_a, Bmag(H_a+Hc2, mur_max*.8, Bsat),
                    "--", color=LR, lw=1.4, alpha=.7, label="Laço inferior")
        ax.axvline(H_op, color=LR, lw=1.5, ls="--", alpha=.8)
        ax.axhline(B_op, color=LR, lw=1.5, ls="--", alpha=.8)
        ax.plot(H_op, B_op, "o", color=LR, ms=9, zorder=5,
                label=f"Op. $H$={H_op} A/m, $B$={B_op:.3f} T")
        ax.plot(H_a, mur_max*mu0*H_a, ":", color=CI, lw=1.3, alpha=.6,
                label=f"Inclinação inicial $\\mu_r$={mur_max}")
        ax.axhline(Bsat, color=CZ, lw=.8, ls=":")
        ax.text(4500, Bsat+.04, "$B_{sat}$", color=CZ, fontsize=8)
        ax.set_xlabel("$H$ (A/m)", color=BR); ax.set_ylabel("$B$ (T)", color=BR)
        ax.set_xlim(0, 5000); ax.set_ylim(0, Bsat*1.15)
        ax.legend(fontsize=8, facecolor=BG2, edgecolor=CZ, labelcolor=BR)
        ax.tick_params(colors=CZ)
        for sp in ax.spines.values(): sp.set_edgecolor("#444")
        ax2 = axes[1]; ax2.set_facecolor(BG)
        ax2.plot(H_a[1:], mur_loc[1:], color=VD, lw=2)
        ax2.axvline(H_op, color=LR, lw=1.5, ls="--", alpha=.8)
        ax2.axhline(mr_op, color=LR, lw=1.5, ls="--", alpha=.8)
        ax2.plot(H_op, mr_op, "o", color=LR, ms=9, zorder=5,
                 label=f"$\\mu_r$ local={mr_op:.0f}")
        ax2.set_xlabel("$H$ (A/m)", color=BR); ax2.set_ylabel("$\\mu_r$ local", color=BR)
        ax2.set_title("Permeabilidade Relativa vs. $H$", color=BR, fontsize=9)
        ax2.set_xlim(0, 5000)
        ax2.legend(fontsize=8, facecolor=BG2, edgecolor=CZ, labelcolor=BR)
        ax2.tick_params(colors=CZ)
        for sp in ax2.spines.values(): sp.set_edgecolor("#444")
        fig.tight_layout(); _show(fig)
        for col, (lab, val) in zip(st.columns(4), [
            ("$B$ (T)",        f"{B_op:.4f}"),
            ("$\\mu_r$ local", f"{mr_op:.0f}"),
            ("$\\mu$ (H/m)",   f"{mr_op*mu0:.2e}"),
            ("$B/B_{sat}$",    f"{B_op/Bsat*100:.1f}%"),
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
    st.markdown('<div class="sec-title">1 · Relação $i$-$H$ — Lei Circuital de Ampère</div>',
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
    with c2:
        _show(fig_regra_mao(), "Campo H ao redor de um condutor (regra da mão direita)")

    c1, c2 = st.columns([1, 1])
    with c1:
        _show(fig_campo_r(), "Campo H a distância r de um condutor isolado")
    with c2:
        _show(fig_ampere_contorno(), "Lei de Ampère — contorno fechado num núcleo toroidal")

    # ── 2. Relação B-H ────────────────────────────────────────────────────────
    st.markdown('<div class="sec-title">2 · Relação $B$-$H$ — Permeabilidade Magnética</div>',
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
                    "(curva de magnetização não-linear) e com a história magnética (histerese).")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        _show(fig_BH(), "Curva B-H: material linear vs. ferromagnético")

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
        _show(fig_analogia(), "Analogia: circuito elétrico ↔ circuito magnético")
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
    with c2:
        _show(fig_entreferro(), "Circuito magnético com entreferro")

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
        _show(fig_indutancia(), "Indutância, Lei de Faraday e energia armazenada")

    st.markdown('<div class="subsec">4.1 · Indutância Mútua e Energia Armazenada</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        _show(fig_indutancia_mutua(), "Indutância mútua entre duas bobinas")
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

**Energia armazenada no campo magnético:**
""")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"W_L = \frac{1}{2}\,L\,i^2 = \frac{\lambda^2}{2L} = \frac{1}{2}\,\mathcal{R}\,\phi^2")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="nota-box">', unsafe_allow_html=True)
        st.markdown("A variação de $W_L$ com a posição do rotor é o mecanismo de "
                    "**geração de força e torque eletromagnético** nas máquinas elétricas.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── 5. Histerese ─────────────────────────────────────────────────────────
    st.markdown('<div class="sec-title">5 · Histerese Magnética</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1.1, 1])
    with c1:
        _show(fig_histerese(), "Laço de histerese B-H e laços para diferentes amplitudes")
    with c2:
        st.markdown("""
A **histerese** é o fenômeno pelo qual o estado magnético depende da história
de magnetização, não apenas do campo atual $H$.

**Grandezas do laço:**
- $B_r$ (T): **remanência** — $B$ remanescente quando $H=0$
- $H_c$ (A/m): **coercividade** — campo para anular $B$
- $B_{sat}$ (T): **saturação** — valor máximo de $B$

| Tipo | $H_c$ | Aplicação |
|------|--------|-----------|
| Mole (_soft_) | baixo | Núcleos de máquinas e transformadores |
| Duro (_hard_) | alto | Ímãs permanentes |

**Perdas por histerese** (por ciclo, por volume):
""")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"W_h = \oint H\,dB \quad\text{(área do laço)}")
        st.latex(r"P_h = k_h\,f\,B_{max}^n \quad (n \approx 1{,}6 \text{ a } 2)")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── 6. Correntes Parasitas ────────────────────────────────────────────────
    st.markdown('<div class="sec-title">6 · Correntes Parasitas e Perdas no Núcleo</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([1.1, 1])
    with c1:
        _show(fig_parasita(), "Correntes parasitas, laminação e perdas no núcleo")
    with c2:
        st.markdown("""
**Correntes parasitas** (_Eddy currents_) são induzidas no núcleo condutor
pela variação de $B$, dissipando energia como calor.

**Redução:**
- Material de **alta resistividade** (ferrite, aço silício)
- **Laminação**: chapas finas isoladas — $P_e \\propto d^2$

**Perdas por correntes parasitas:**
""")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"P_e = k_e\,f^2\,B_{max}^2\,d^2")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("**Perdas totais no núcleo** (perdas no ferro):")
        st.markdown('<div class="eq-box">', unsafe_allow_html=True)
        st.latex(r"P_c = P_h + P_e = k_h\,f\,B_{max}^n + k_e\,f^2\,B_{max}^2")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="nota-box">', unsafe_allow_html=True)
        st.markdown("As perdas no núcleo ocorrem mesmo a vazio, pois dependem de $B_{max}$ "
                    "e $f$, não da corrente de carga.")
        st.markdown('</div>', unsafe_allow_html=True)

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
