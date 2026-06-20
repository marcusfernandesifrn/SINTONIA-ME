"""
🔋 Introdução à Conversão Eletromecânica de Energia
Disciplina: Máquinas Elétricas
Curso: Engenharia de Energia
Instituição: IFRN — Campus Natal-Central (CNAT)
Autor: Marcus V A Fernandes · marcus.fernandes@ifrn.edu.br · v1.0
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from PIL import Image
import schemdraw
import schemdraw.elements as elm
import warnings


def run():

    warnings.filterwarnings("ignore")

    # ── Paleta de cores ───────────────────────────────────────────────────────
    AZ = "#3d8ef0"; RX = "#6c47ff"; VD = "#1f9d55"; LR = "#e07b00"
    CI = "#0097a7"; TX = "#1a1f2b"; CZ = "#6b7280"

    # ── CSS responsivo — injetado uma única vez ───────────────────────────────
    # No desktop (>768 px) cada figura fica centralizada com largura controlada.
    # Em telas estreitas (≤768 px, mobile/vertical) a figura ocupa 100% da tela.
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

    def show_png(png_bytes, width_frac=0.55):
        """Mesmo helper, para bytes PNG já prontos (circuitos schemdraw)."""
        b64 = base64.b64encode(png_bytes).decode()
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

    def _schem_png(build_fn, color=TX):
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
        ax.set_title("Campo H — regra da mão direita", fontsize=9, color=TX, pad=6)
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
        ax.set_title("Lei de Ampère — contorno fechado", fontsize=9, color=TX, pad=6)
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
        ax.set_title("Campo H a distância r de um condutor", fontsize=9, color=TX, pad=6)
        fig.tight_layout(); return fig

    def fig_circuito_mag():
        fig, ax = _mpl_base((5.6, 4.2))
        ax.set_xlim(-3.3, 3.3); ax.set_ylim(-2.6, 2.6)
        Ro, Ri = 2., 1.1
        ring = mpatches.Wedge((0, 0), Ro, 0, 360, width=Ro-Ri, facecolor="#3d8ef028",
                               edgecolor="none", zorder=2)
        ax.add_patch(ring)
        t = np.linspace(0, 2*np.pi, 400)
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
        ax.set_title("Núcleo toroidal: φ, ℱ e ℛ", fontsize=9, color=TX, pad=6)
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
        ax.set_title("Geometria do núcleo com entreferro", fontsize=9, color=TX, pad=6)
        fig.tight_layout(); return fig

    def fig_frangeamento():
        fig, axes = plt.subplots(1, 2, figsize=(8.6, 4))
        fig.patch.set_alpha(0)
        ax = axes[0]; ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(-3.5, 3.5); ax.set_ylim(-3.5, 3.5); ax.set_aspect("equal")
        ax.set_title("Máquina rotativa (seção)", color=TX, fontsize=10)
        ax.add_patch(plt.Circle((0,0), 3.,  color="#3d8ef022", ec=CZ, lw=1.6, zorder=2))
        ax.add_patch(plt.Circle((0,0), 2.2, color="none",     ec=CZ, lw=1.2, zorder=3))
        ring = mpatches.Wedge((0, 0), 2.2, 0, 360, width=2.2-1.9, color=LR, alpha=.30, zorder=3)
        ax.add_patch(ring)
        ax.text(0, 2.6, "Estator", color=TX, fontsize=9, ha="center")
        ax.add_patch(plt.Circle((0,0), 1.9, color="#3d8ef022", ec=CZ, lw=1.4, zorder=4))
        ax.add_patch(plt.Circle((0,0), 1.1, color="none",     ec=CZ, lw=1.,  zorder=5))
        ax.add_patch(plt.Circle((0,0), .25, color=CZ, zorder=6))
        ax.text(0, 1.5, "Rotor",   color=TX, fontsize=9, ha="center")
        ax.text(2.55, .55, "Entreferro\n$\\ell_g$", color=LR, fontsize=8, ha="center")
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
        ax.set_title("Indutância mútua entre duas bobinas", fontsize=9, color=TX, pad=6)
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
        ax.set_title("Correntes parasitas e laminação do núcleo", fontsize=9, color=TX, pad=6)
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
        return _schem_png(build)

    def schem_analogia_magnetico():
        def build(d):
            d.add(elm.SourceV().up().label("$\\mathcal{F}=Ni$", loc="left").color(AZ))
            d.add(elm.Resistor().right().label("$\\mathcal{R}$", loc="top").color(AZ))
            d.add(elm.Line().down())
            d.add(elm.Line().left())
        return _schem_png(build)

    def fig_analogia_combinada():
        """Combina os dois circuitos da analogia em uma única figura com painéis de
        tamanho idêntico, garantindo alinhamento perfeito (o PNG do schemdraw tem fundo
        branco opaco mesmo com transparent=True, então cada circuito é centralizado em
        um canvas branco do mesmo tamanho antes de ser posicionado lado a lado)."""
        img1 = np.array(Image.open(io.BytesIO(schem_analogia_eletrico())).convert("RGBA"))
        img2 = np.array(Image.open(io.BytesIO(schem_analogia_magnetico())).convert("RGBA"))
        h1, w1 = img1.shape[:2]; h2, w2 = img2.shape[:2]
        H, W = max(h1, h2), max(w1, w2)

        def pad_to(img, H, W):
            h, w = img.shape[:2]
            canvas = np.full((H, W, 4), 255, dtype=np.uint8)
            top = (H - h) // 2; left = (W - w) // 2
            canvas[top:top+h, left:left+w] = img
            return canvas

        img1p = pad_to(img1, H, W)
        img2p = pad_to(img2, H, W)

        fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.6))
        fig.patch.set_alpha(0)
        for ax, img, title in zip(axes, [img1p, img2p],
                                    ["Circuito elétrico", "Circuito magnético"]):
            ax.set_facecolor("none")
            ax.imshow(img)
            ax.set_xticks([]); ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.set_title(title, fontsize=10, color=TX, pad=8)
        fig.subplots_adjust(wspace=0.05, left=0.02, right=0.98)
        return fig

    def schem_entreferro():
        def build(d):
            d.add(elm.SourceV().up().label("$\\mathcal{F}=Ni$", loc="left").color(AZ))
            d.add(elm.Resistor().right().label("$\\mathcal{R}_c$", loc="top").color(CZ))
            d.add(elm.Resistor().right().label("$\\mathcal{R}_g$", loc="top").color(LR))
            d.add(elm.Line().down())
            d.add(elm.Line().left().tox(0))
        return _schem_png(build)

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
                               showlegend=False)
            show_plot(fig, key="m1_exp1_fluxo", height=320)
        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=H_a, y=B_a, mode="lines",
                                       line=dict(color=VD, width=3)))
            fig2.add_trace(go.Scatter(x=[Hc], y=[B], mode="markers",
                                       marker=dict(color=LR, size=11),
                                       showlegend=False))
            fig2.update_layout(title="Ponto de Operação B-H (linear)",
                                xaxis_title="H (A/m)", yaxis_title="B (T)",
                                showlegend=False)
            show_plot(fig2, key="m1_exp1_bh", height=320)

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
                               legend=dict(orientation="h", y=-0.3))
            show_plot(fig, key="m1_exp2_bh", height=380)
        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=H_a[1:], y=mur_loc[1:], mode="lines",
                                       line=dict(color=VD, width=3)))
            fig2.add_trace(go.Scatter(x=[H_op], y=[mr_op], mode="markers",
                                       marker=dict(color=LR, size=11),
                                       name=f"μᵣ local={mr_op:.0f}"))
            fig2.update_layout(title="Permeabilidade Relativa Local vs. H",
                                xaxis_title="H (A/m)", yaxis_title="μᵣ local",
                                showlegend=False)
            show_plot(fig2, key="m1_exp2_mur", height=380)

        for col, (lab, val) in zip(st.columns(4), [
            ("B (T)",        f"{B_op:.4f}"),
            ("μᵣ local",     f"{mr_op:.0f}"),
            ("μ (H/m)",      f"{mr_op*mu0:.2e}"),
            ("B/B_sat",      f"{B_op/Bsat*100:.1f}%"),
        ]):
            with col: st.metric(lab, val)

    # ════════════════════════════════════════════════════════════════════════
    # FIGURAS — CONVERSÃO ELETROMECÂNICA (geometria, matplotlib)
    # ════════════════════════════════════════════════════════════════════════

    def fig_fluxo_conversao():
        """Diagrama de blocos: Sistema Elétrico -> Campo Magnético -> Sistema Mecânico."""
        fig, ax = _mpl_base((7.5, 3.6))
        ax.set_xlim(0, 13); ax.set_ylim(-2.6, 2.2)
        w, h = 2.6, 1.1
        boxes = [(2, 0, "Sistema\nElétrico"), (6.5, 0, "Campo\nMagnético"),
                 (11, 0, "Sistema\nMecânico")]
        for x, y, label in boxes:
            ax.add_patch(mpatches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.05",
                                                  fc="#3d8ef015", ec=AZ, lw=1.8, zorder=3))
            ax.text(x, y, label, ha="center", va="center", fontsize=11, color=TX, zorder=4)
        for (x1, _, _), (x2, _, _) in zip(boxes[:-1], boxes[1:]):
            ax.annotate("", xy=(x2-w/2, 0), xytext=(x1+w/2, 0),
                        arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.8))
        ax.annotate("", xy=(12.8, 0), xytext=(11+w/2, 0),
                    arrowprops=dict(arrowstyle="-|>", color=VD, lw=2))
        ax.text(13, 0, "Potência\nmecânica\nentregue", ha="left", va="center", fontsize=9, color=VD)
        labels_perdas = ["perdas\nelétricas", "perdas\nno campo", "perdas\nmecânicas"]
        for (x, y, _), lp in zip(boxes, labels_perdas):
            ax.annotate("", xy=(x, y-h/2-0.9), xytext=(x, y-h/2-0.05),
                        arrowprops=dict(arrowstyle="-|>", color=LR, lw=1.6))
            ax.text(x, y-h/2-1.15, lp, ha="center", va="top", fontsize=8.5, color=LR)
        ax.set_title("Processo de Conversão Eletromecânica de Energia", fontsize=10, color=TX, pad=4)
        fig.tight_layout(); return fig

    def fig_energia_coenergia():
        """Curva λ-i com áreas de energia (Wf) e coenergia (W'f) destacadas."""
        fig, ax = plt.subplots(figsize=(5.6, 4.4))
        fig.patch.set_alpha(0); ax.set_facecolor("none")
        i_a = np.linspace(0, 5, 400)
        lam = 1.3*np.sqrt(i_a)
        i0 = 1.0; lam0 = 1.3*np.sqrt(i0)
        ax.plot(i_a, lam, color=TX, lw=2.6, label="$\\lambda = \\lambda(i)$")
        i_below = np.interp(np.linspace(0, lam0, 150), lam, i_a)
        lam_below = np.linspace(0, lam0, 150)
        ax.fill_betweenx(lam_below, 0, i_below, color=AZ, alpha=.85, ec="#1a5fc4", lw=1.5,
                          label="$W_f$ (energia) — área A")
        mask = i_a <= i0
        ax.fill_between(i_a[mask], lam[mask], lam0, color=VD, alpha=.45, ec=VD, lw=1.2,
                         label="$W_f'$ (coenergia) — área B")
        ax.plot([i0, i0], [0, lam0], "--", color=CZ, lw=1)
        ax.plot([0, i0], [lam0, lam0], "--", color=CZ, lw=1)
        ax.plot(i0, lam0, "o", color=LR, ms=9, zorder=5)
        ax.annotate("área A\n($W_f$)", xy=(0.06, 0.55), xytext=(0.55, 0.35),
                    fontsize=8.5, color="#1a5fc4", ha="left",
                    arrowprops=dict(arrowstyle="->", color="#1a5fc4", lw=1.2))
        ax.legend(loc="lower right", fontsize=8.5, frameon=False, labelcolor=TX)
        ax.set_xlabel("$i$", color=TX); ax.set_ylabel("$\\lambda$", color=TX)
        ax.set_xlim(0, 2.2); ax.set_ylim(0, 1.5)
        ax.tick_params(colors=CZ)
        for sp in ax.spines.values(): sp.set_edgecolor("#bbb")
        ax.set_title("Energia e Coenergia no Campo Magnético", fontsize=10, color=TX, pad=6)
        fig.tight_layout(); return fig

    def _zigzag(ax, x0, x1, y, n_zig=6, amp=0.18, color=TX, lw=1.4, lead_frac=0.08):
        """Linha em zigue-zague triangular (usada para resistor e mola)."""
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

    def fig_sistema_dinamico():
        """Sistema elétrico -> bloco de conversão -> sistema mecânico massa-mola-amortecedor."""
        fig, ax = plt.subplots(figsize=(8.5, 4.5))
        fig.patch.set_alpha(0); ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(0, 15); ax.set_ylim(-3.4, 2.8); ax.set_aspect("equal")

        # --- Fonte de tensão ---
        src_x, src_y = 1.1, 0
        ax.add_patch(plt.Circle((src_x, src_y), .5, fc="none", ec=TX, lw=1.6, zorder=5))
        ax.text(src_x, src_y, "~", ha="center", va="center", fontsize=14, color=TX, zorder=6)
        ax.text(src_x-0.75, 1.0, "$v_0$", fontsize=11, color=TX)

        # --- Fio superior: fonte -> resistor -> bloco (malha fechada) ---
        top_y = 0.9
        ax.plot([src_x, src_x], [0.5, top_y], color=TX, lw=1.4, zorder=2)
        R_x0, R_x1 = 2.1, 3.1
        ax.plot([src_x, R_x0], [top_y, top_y], color=TX, lw=1.4, zorder=2)
        ax.annotate("", xy=(1.75, top_y), xytext=(1.45, top_y),
                    arrowprops=dict(arrowstyle="->", color=TX, lw=1.2))
        ax.text(1.6, top_y+0.32, "$i$", fontsize=10, color=TX, ha="center")
        block_x0 = 3.7
        ax.plot([R_x1, block_x0], [top_y, top_y], color=TX, lw=1.4, zorder=2)

        # --- Fio inferior: retorno fonte -> bloco ---
        bot_y = -0.9
        ax.plot([src_x, src_x], [-0.5, bot_y], color=TX, lw=1.4, zorder=2)
        ax.plot([src_x, block_x0], [bot_y, bot_y], color=TX, lw=1.4, zorder=2)

        # --- Bloco de conversão eletromecânica ---
        block_w, block_h = 3.0, 2.2
        ax.add_patch(mpatches.FancyBboxPatch((block_x0, -block_h/2), block_w, block_h,
                                              boxstyle="round,pad=0.05",
                                              fc="#3d8ef015", ec=AZ, lw=1.8, zorder=3))
        ax.text(block_x0 + block_w/2, 0, "Sistema de\nconversão\neletromecânica",
                ha="center", va="center", fontsize=9.5, color=TX, zorder=4)
        ax.text(block_x0+0.15, 1.25, r"$\lambda,\,e$", fontsize=10, color=TX)
        block_x1 = block_x0 + block_w

        # --- Resistor R (zigue-zague triangular padrão) — desenhado por cima do fio ---
        _zigzag(ax, R_x0, R_x1, top_y, n_zig=5, amp=0.16, lead_frac=0.0)
        ax.text((R_x0+R_x1)/2, top_y+0.35, "$R$", fontsize=11, color=TX, ha="center")

        # --- Saída de força f_fld ---
        ax.annotate("", xy=(block_x1+1.1, 0), xytext=(block_x1+0.1, 0),
                    arrowprops=dict(arrowstyle="-|>", color=VD, lw=2))
        ax.text(block_x1+0.6, 0.35, "$f_{fld}$", fontsize=10, color=VD, ha="center")

        # --- Parede fixa ---
        wall_x = 13.6
        ax.plot([wall_x, wall_x], [-2.8, 2.4], color=TX, lw=2.5, zorder=2)
        for yy in np.linspace(-2.7, 2.3, 9):
            ax.plot([wall_x, wall_x+0.3], [yy, yy-0.25], color=TX, lw=1, zorder=2)

        # --- Barra móvel (recebe f_fld; conecta K, B, M e f0) ---
        bar_x = block_x1 + 1.4
        ax.plot([bar_x, bar_x], [-2.8, 2.4], color=CZ, lw=2.2, zorder=2)

        # --- Mola K (zigue-zague regular) ---
        y_k = 1.7
        _zigzag(ax, bar_x, wall_x, y_k, n_zig=7, amp=0.22, lead_frac=0.06)
        ax.text((bar_x+wall_x)/2, y_k+0.5, "$K$", ha="center", fontsize=10, color=TX)

        # --- Amortecedor B (símbolo padrão dashpot: pistão dentro de cilindro) ---
        y_b = 0.6
        cyl_x0, cyl_x1 = bar_x+2.1, bar_x+3.0
        ax.plot([bar_x, cyl_x0], [y_b, y_b], color=TX, lw=1.4, zorder=2)
        ax.plot([cyl_x0, cyl_x0], [y_b-0.3, y_b+0.3], color=TX, lw=1.4, zorder=3)
        ax.plot([cyl_x0, cyl_x1], [y_b+0.3, y_b+0.3], color=TX, lw=1.4, zorder=3)
        ax.plot([cyl_x0, cyl_x1], [y_b-0.3, y_b-0.3], color=TX, lw=1.4, zorder=3)
        piston_x = cyl_x0 + 0.55
        ax.plot([piston_x, piston_x], [y_b-0.22, y_b+0.22], color=TX, lw=3, zorder=4,
                solid_capstyle="butt")
        ax.plot([piston_x, wall_x], [y_b, y_b], color=TX, lw=1.4, zorder=2)
        ax.text((bar_x+wall_x)/2, y_b+0.5, "$B$", ha="center", fontsize=10, color=TX)

        # --- Massa M ---
        y_m = -0.6
        mass_x0, mass_x1 = bar_x+2.1, bar_x+3.1
        ax.plot([bar_x, mass_x0], [y_m, y_m], color=TX, lw=1.4, zorder=2)
        ax.add_patch(mpatches.Rectangle((mass_x0, y_m-0.4), mass_x1-mass_x0, 0.8,
                                         fc="#6c47ff15", ec=RX, lw=1.4, zorder=3))
        ax.text((mass_x0+mass_x1)/2, y_m, "$M$", ha="center", va="center",
                fontsize=10, color=TX, zorder=4)
        ax.plot([mass_x1, wall_x], [y_m, y_m], color=TX, lw=1.4, zorder=2)

        # --- Força externa f0 (aplicada diretamente na barra — sem ligação à parede,
        #     pois f0 não é um elemento físico conectado ao apoio fixo, apenas uma
        #     força externa atuando sobre a massa móvel) ---
        y_f0 = -1.9
        ax.annotate("", xy=(bar_x-0.7, y_f0), xytext=(bar_x+0.3, y_f0),
                    arrowprops=dict(arrowstyle="-|>", color=LR, lw=2))
        ax.text(bar_x-0.6, y_f0-0.35, "$f_0$", fontsize=10, color=LR, ha="center")

        # --- Eixo de posição x ---
        ax.annotate("", xy=(bar_x+0.8, 2.6), xytext=(bar_x, 2.6),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.2))
        ax.text(bar_x+0.4, 2.8, "$x$", ha="center", fontsize=10, color=TX)

        ax.set_title("Equações Dinâmicas — Sistema Eletromecânico Acoplado",
                      fontsize=10.5, color=TX, pad=10)
        fig.tight_layout(); return fig

    def fig_acao_geradora_motora():
        """Comparação entre ação geradora e ação motora."""
        fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
        fig.patch.set_alpha(0)
        titles = ["Ação Geradora", "Ação Motora"]
        for ax, title, gen in zip(axes, titles, [True, False]):
            ax.set_facecolor("none"); ax.axis("off")
            ax.set_xlim(0, 10); ax.set_ylim(-1, 5)
            ax.set_aspect("equal")
            ax.set_title(title, fontsize=11, color=TX, fontweight="bold", pad=6)
            for y in np.linspace(0.5, 4, 6):
                ax.annotate("", xy=(9.3, y), xytext=(0.7, y),
                            arrowprops=dict(arrowstyle="->", color=CI, lw=1, alpha=.55))
            ax.text(9.6, 2.25, "$B$", color=CI, fontsize=12, ha="left", va="center")
            ax.plot([5, 5], [0.5, 4], color=TX, lw=4, solid_capstyle="round", zorder=4)
            ax.add_patch(plt.Circle((5, 4), .12, color=TX, zorder=5))
            ax.add_patch(plt.Circle((5, 0.5), .12, color=TX, zorder=5))
            if gen:
                ax.annotate("", xy=(6.3, 2.25), xytext=(5.25, 2.25),
                            arrowprops=dict(arrowstyle="-|>", color=VD, lw=2.4))
                ax.text(5.75, 2.65, "$u$ (velocidade)", color=VD, fontsize=9, ha="center")
                ax.text(5, -0.6, "$e$ induzida no condutor", color=LR, fontsize=9.5, ha="center")
            else:
                ax.annotate("", xy=(5, 4.3), xytext=(5, 0.7),
                            arrowprops=dict(arrowstyle="-|>", color=RX, lw=2.2))
                ax.text(4.55, 2.25, "$i$", color=RX, fontsize=12, ha="right")
                ax.annotate("", xy=(6.4, 2.25), xytext=(5.3, 2.25),
                            arrowprops=dict(arrowstyle="-|>", color=LR, lw=2.4))
                ax.text(5.85, 2.65, "$f_m$ (força)", color=LR, fontsize=9, ha="center")
        fig.suptitle("Tipos de Ação na Conversão Eletromecânica", fontsize=11.5, color=TX, y=1.03)
        fig.tight_layout(); return fig

    # ════════════════════════════════════════════════════════════════════════
    # FIGURAS — MÁQUINAS ROTATIVAS (geometria, matplotlib)
    # ════════════════════════════════════════════════════════════════════════

    def fig_maquina_cilindrica():
        """Seção transversal de máquina cilíndrica: entreferro uniforme, eixos do
        estator e do rotor, condutores S/-S e r/-r, ângulo θ = ωm·t + δ."""
        fig, ax = plt.subplots(figsize=(5.6, 5.0))
        fig.patch.set_alpha(0); ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(-3.2, 4.6); ax.set_ylim(-3.2, 3.6); ax.set_aspect("equal")

        R_out, R_in, R_rotor = 2.6, 2.05, 1.55
        t = np.linspace(0, 2*np.pi, 200)
        ax.plot(R_out*np.cos(t), R_out*np.sin(t), color=TX, lw=1.8, zorder=2)
        ax.plot(R_in*np.cos(t), R_in*np.sin(t), color=CZ, lw=1.3, zorder=2)
        ax.plot(R_rotor*np.cos(t), R_rotor*np.sin(t), color=CZ, lw=1.3, zorder=2)
        ax.add_patch(plt.Circle((0,0), R_rotor, fc="#1f9d5510", zorder=1))

        def cross(x, y, s=.12, color=TX):
            ax.plot([x-s,x+s],[y-s,y+s], color=color, lw=1.6, zorder=5)
            ax.plot([x-s,x+s],[y+s,y-s], color=color, lw=1.6, zorder=5)
        def dot(x, y, s=.06, color=TX):
            ax.add_patch(plt.Circle((x,y), s, fc=color, ec=color, zorder=5))

        rs = (R_out+R_in)/2
        cross(rs*np.cos(np.pi/2), rs*np.sin(np.pi/2), color=AZ)
        ax.text(rs*np.cos(np.pi/2)-0.05, rs*np.sin(np.pi/2)+0.35, "S", color=AZ, fontsize=11, ha="center")
        dot(rs*np.cos(-np.pi/2), rs*np.sin(-np.pi/2), color=AZ)
        ax.text(rs*np.cos(-np.pi/2)-0.05, rs*np.sin(-np.pi/2)-0.4, "-S", color=AZ, fontsize=11, ha="center")

        ang = 35
        rr = (R_in+R_rotor)/2 * 0.9
        a1 = np.radians(90+ang)
        cross(rr*np.cos(a1), rr*np.sin(a1), s=.10, color=VD)
        ax.text(rr*np.cos(a1)-0.35, rr*np.sin(a1)+0.05, "r", color=VD, fontsize=11, ha="center")
        a2 = np.radians(-90+ang)
        dot(rr*np.cos(a2), rr*np.sin(a2), s=.05, color=VD)
        ax.text(rr*np.cos(a2)+0.35, rr*np.sin(a2)-0.05, "-r", color=VD, fontsize=11, ha="center")

        ax.annotate("", xy=(R_out+0.7, 0), xytext=(-R_out-0.3, 0),
                    arrowprops=dict(arrowstyle="-|>", color=TX, lw=1.3))
        ax.text(R_out+0.85, 0, "eixo do\nestator", color=TX, fontsize=9, va="center")

        dxr, dyr = (R_out+0.7)*np.cos(np.radians(ang)), (R_out+0.7)*np.sin(np.radians(ang))
        ax.annotate("", xy=(dxr, dyr), xytext=(-0.3*dxr, -0.3*dyr),
                    arrowprops=dict(arrowstyle="-|>", color=VD, lw=1.3))
        ax.text(dxr+0.15, dyr+0.15, "eixo do\nrotor", color=VD, fontsize=9)

        t_arc = np.linspace(0, np.radians(ang), 30)
        r_arc = 1.0
        ax.plot(r_arc*np.cos(t_arc), r_arc*np.sin(t_arc), color=LR, lw=1.4, zorder=4)
        ax.text(1.25, 0.45, r"$\theta=\omega_m t+\delta$", color=LR, fontsize=10)

        ax.set_title("Máquina cilíndrica — entreferro uniforme", fontsize=10.5, color=TX, pad=8)
        fig.tight_layout(); return fig

    def fig_taxonomia():
        """Diagrama hierárquico de classificação das máquinas elétricas."""
        fig, ax = plt.subplots(figsize=(9.5, 4.6))
        fig.patch.set_alpha(0); ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(0, 16); ax.set_ylim(2.3, 11)

        def box(x, y, w, h, text, fc="#3d8ef012", ec=AZ, fs=9.5, fw="normal"):
            ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                                                  fc=fc, ec=ec, lw=1.4, zorder=3))
            ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs,
                    color=TX, fontweight=fw, zorder=4)

        box(0.5, 9.3, 15, 1.0, "Máquinas Elétricas", fc="#3d8ef022", fs=13, fw="bold")
        box(0.5, 7.7, 12.7, 1.0, "Máquinas rotativas", fc="#3d8ef018", fs=12)
        box(13.5, 7.0, 2.0, 1.7, "Máquinas\nestacionárias", fc="#6b728018", ec=CZ, fs=8.5)
        box(0.5, 6.1, 5.6, 1.0, "Corrente Contínua", fc=VD+"18", ec=VD, fs=11)
        box(6.4, 6.1, 6.8, 1.0, "Corrente Alternada", fc=LR+"18", ec=LR, fs=11)

        cc_items = ["Excitação\nIndependente", "Série/\nParalelo", "Servo-\nmotores", "Motores\nde passo"]
        for i, it in enumerate(cc_items):
            box(0.5+i*1.4, 4.5, 1.3, 1.3, it, fc=VD+"10", ec=VD, fs=7.8)

        box(6.4, 4.5, 3.1, 1.3, "Máquina\nSíncrona", fc=LR+"12", ec=LR, fs=10)
        box(9.7, 4.5, 3.5, 1.3, "Máquina Assíncrona\n(Indução)", fc=LR+"12", ec=LR, fs=9.5)

        sync_items = ["Mono-\nfásico", "Tri-\nfásico"]
        for i, it in enumerate(sync_items):
            box(6.4+i*1.6, 2.9, 1.4, 1.3, it, fc=LR+"08", ec=LR, fs=8)
        async_items = ["Mono-\nfásico", "Tri-\nfásico", "Servo-\nmotores", "Sincro-\nnizadores"]
        for i, it in enumerate(async_items):
            box(9.7+i*0.9, 2.9, 0.8, 1.3, it, fc=LR+"08", ec=LR, fs=6.8)

        box(13.5, 5.4, 2.0, 1.3, "Transfor-\nmadores", fc="#6b728010", ec=CZ, fs=8.5)

        def link(x1, y1, x2, y2):
            ax.plot([x1, x2], [y1, y2], color=CZ, lw=1.0, zorder=1)

        link(7.85, 9.3, 6.8, 8.7); link(7.85, 9.3, 14.5, 8.7)
        link(6.8, 7.7, 3.3, 7.1); link(6.8, 7.7, 9.8, 7.1)
        link(3.3, 6.1, 1.15, 5.8); link(3.3, 6.1, 2.55, 5.8)
        link(3.3, 6.1, 3.95, 5.8); link(3.3, 6.1, 5.35, 5.8)
        link(9.8, 6.1, 7.95, 5.8); link(9.8, 6.1, 11.45, 5.8)
        link(7.95, 4.5, 7.1, 4.2); link(7.95, 4.5, 8.5, 4.2)
        for i in range(4):
            link(11.45, 4.5, 10.1+i*0.9, 4.2)

        ax.set_title("Classificação das Máquinas Elétricas", fontsize=12, color=TX,
                     fontweight="bold", pad=10)
        fig.tight_layout(); return fig

    def plotly_torque_pulsante():
        """Compara torque oscilante (caso geral) com torque médio constante
        (máquinas síncrona e assíncrona)."""
        I_rm, I_sm, M, delta, alpha = 1.0, 1.0, 1.0, 0.3, 0.2
        t = np.linspace(0, 4, 800)

        ws = 2*np.pi*1.0
        wr = 2*np.pi*0.3
        T_sync = -(I_rm*I_sm*M/2) * (np.sin(2*ws*t + delta) + np.sin(delta))
        mean_sync = -(I_rm*I_sm*M/2)*np.sin(delta)

        T_async = -(I_rm*I_sm*M/4) * (
            np.sin(2*ws*t + alpha + delta) + np.sin(-2*wr*t - alpha + delta) +
            np.sin(2*ws*t - 2*wr*t - alpha + delta) + np.sin(alpha + delta))
        mean_async = -(I_rm*I_sm*M/4)*np.sin(alpha+delta)

        wm_geral = 2*np.pi*0.62
        T_geral = -(I_rm*I_sm*M/4) * (
            np.sin((wm_geral+ws+wr)*t + alpha + delta) + np.sin((wm_geral-ws-wr)*t - alpha + delta) +
            np.sin((wm_geral+ws-wr)*t - alpha + delta) + np.sin((wm_geral-ws+wr)*t + alpha + delta))

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                             subplot_titles=(
                                 "Caso geral (|ωm| ≠ |ωs ± ωr|): torque médio nulo",
                                 "Máquina síncrona (ωm = ωs): torque médio constante",
                                 "Máquina assíncrona (ωm = ωs − ωr): torque médio constante"),
                             vertical_spacing=0.1)

        fig.add_trace(go.Scatter(x=t, y=T_geral, mode="lines", line=dict(color=CZ, width=2),
                                  showlegend=False), row=1, col=1)
        fig.add_hline(y=0, line=dict(color=TX, dash="dash", width=1), row=1, col=1)

        fig.add_trace(go.Scatter(x=t, y=T_sync, mode="lines", line=dict(color=LR, width=2),
                                  showlegend=False), row=2, col=1)
        fig.add_hline(y=mean_sync, line=dict(color=TX, dash="dash", width=1), row=2, col=1)

        fig.add_trace(go.Scatter(x=t, y=T_async, mode="lines", line=dict(color=VD, width=2),
                                  showlegend=False), row=3, col=1)
        fig.add_hline(y=mean_async, line=dict(color=TX, dash="dash", width=1), row=3, col=1)

        fig.update_yaxes(title_text="T (N·m)", row=1, col=1)
        fig.update_yaxes(title_text="T (N·m)", row=2, col=1)
        fig.update_yaxes(title_text="T (N·m)", row=3, col=1)
        fig.update_xaxes(title_text="t (s)", row=3, col=1)
        fig.update_layout(height=620, title="Torque eletromagnético: oscilante vs. médio constante",
                           showlegend=False)
        for ann in fig.layout.annotations:
            ann.font.size = 11
        return fig

    # ════════════════════════════════════════════════════════════════════════
    # EXPLORADOR 3 — FORÇA ELETROMAGNÉTICA EM SISTEMA LINEAR
    # ════════════════════════════════════════════════════════════════════════

    def exp_forca():
        st.markdown("**Sistema linear com indutância dependente da posição** "
                     "$L(x) = \\dfrac{k}{x} + L_0$ (eletroímã/relé — entreferro $x$ variável):")
        c1, c2 = st.columns(2)
        with c1:
            i_const = st.slider("Corrente i (A)", 0.5, 10.0, 2.0, step=0.1, key="m1_exp3_i")
            k_ind   = st.slider("Constante k (geometria)", 1.0, 20.0, 8.0, step=0.5, key="m1_exp3_k")
        with c2:
            L0   = st.slider("Indutância residual L₀ (H)", 0.0, 2.0, 0.3, step=0.05, key="m1_exp3_L0")
            x_op = st.slider("Posição de operação x (cm)", 0.5, 5.0, 1.5, step=0.1, key="m1_exp3_x")

        x_a = np.linspace(0.4, 5, 300)
        L_a = k_ind/x_a + L0
        dLdx_a = -k_ind/x_a**2
        fm_a = 0.5 * i_const**2 * dLdx_a

        L_op = k_ind/x_op + L0
        dLdx_op = -k_ind/x_op**2
        fm_op = 0.5 * i_const**2 * dLdx_op

        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_a, y=L_a, mode="lines",
                                      line=dict(color=AZ, width=3)))
            fig.add_trace(go.Scatter(x=[x_op], y=[L_op], mode="markers",
                                      marker=dict(color=LR, size=11), showlegend=False))
            fig.update_layout(title="Indutância L(x) vs. Posição",
                               xaxis_title="x (cm)", yaxis_title="L (H)", showlegend=False)
            show_plot(fig, key="m1_exp3_L", height=340)
        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=x_a, y=fm_a, mode="lines",
                                       line=dict(color=LR, width=3)))
            fig2.add_trace(go.Scatter(x=[x_op], y=[fm_op], mode="markers",
                                       marker=dict(color=VD, size=11), showlegend=False))
            fig2.add_hline(y=0, line=dict(color=CZ, width=1))
            fig2.update_layout(title="Força Eletromagnética fm(x), i constante",
                                xaxis_title="x (cm)", yaxis_title="fm (N)", showlegend=False)
            show_plot(fig2, key="m1_exp3_fm", height=340)

        cols = st.columns(3)
        for col, (lab, val) in zip(cols, [
            ("L(x) no ponto", f"{L_op:.3f} H"),
            ("dL/dx no ponto", f"{dLdx_op:.3f} H/cm"),
            ("fm no ponto", f"{fm_op:.3f} N"),
        ]):
            with col: st.metric(lab, val)
        st.info("A força é **negativa** (atrativa): o sistema sempre tende a reduzir o "
                "entreferro x, aumentando L(x) — coerente com $f_m = -\\frac{1}{2}i^2\\,dL/dx$ "
                "quando dL/dx < 0.")

    def fig_maquina_elementar():
        """Máquina elementar de dois enrolamentos: núcleo C do estator + rotor
        cilíndrico bobinado, inserido no entreferro a um ângulo θ do eixo do estator."""
        fig, ax = _mpl_base((6.8, 6.2))
        ax.set_xlim(-2.4, 10.4); ax.set_ylim(-0.3, 8.3)

        # --- Núcleo em C do estator ---
        out_pts = [(1.5,0.8),(7.5,0.8),(7.5,3.4),(6.0,3.4),
                   (6.0,1.6),(2.7,1.6),(2.7,6.4),(6.0,6.4),(6.0,4.6),(7.5,4.6),
                   (7.5,7.2),(1.5,7.2)]
        ax.add_patch(plt.Polygon(out_pts, closed=True, fc="#1a1f2b08", ec=TX, lw=2.0, zorder=2))
        ax.annotate("Estator", xy=(2.1, 7.25), xytext=(-0.3, 7.95),
                    fontsize=11, color=TX, ha="left",
                    arrowprops=dict(arrowstyle="->", color=TX, lw=1.2))

        # --- Bobina do estator (enrolamento concentrado na perna esquerda) ---
        for y0 in np.linspace(2.1, 5.9, 6):
            ax.add_patch(mpatches.Ellipse((2.7, y0), .55, .32, fc="white", ec=AZ, lw=1.6, zorder=4))
        ax.plot([0.6, 2.0], [5.9, 5.9], color=AZ, lw=1.5, zorder=3)
        ax.plot([0.6, 2.0], [2.1, 2.1], color=AZ, lw=1.5, zorder=3)
        ax.add_patch(plt.Circle((0.6, 2.1), .09, fc="white", ec=AZ, lw=1.5, zorder=5))
        ax.annotate("", xy=(0.05, 5.9), xytext=(0.6, 5.9),
                    arrowprops=dict(arrowstyle="->", color=AZ, lw=1.6))
        ax.text(-0.15, 6.15, "$i_s$", color=AZ, fontsize=12, ha="center")

        # --- Eixo do estator (referência vertical, fixo) ---
        x_axis = 7.5
        ax.plot([x_axis, x_axis], [0.2, 8.0], color=CZ, lw=1.1, ls=(0,(6,3,1,3)), zorder=1)

        # --- Rotor cilíndrico bobinado, inserido no entreferro a ângulo θ ---
        theta_deg = 33
        th = np.radians(theta_deg)
        u = np.array([np.sin(th), np.cos(th)])
        v = np.array([np.cos(th), -np.sin(th)])
        rc = np.array([7.05, 4.30])
        half_L, half_W = 1.18, 0.36

        p_in  = rc - half_L*u
        p_out = rc + half_L*u

        # vértice de anotação do ângulo (acima do rotor, sobre o eixo do estator)
        vertex = np.array([x_axis, 5.85])

        c1 = p_in - half_W*v; c2 = p_in + half_W*v
        c3 = p_out + half_W*v; c4 = p_out - half_W*v
        ax.add_patch(plt.Polygon([c1,c2,c3,c4], closed=True, fc="#6c47ff14", ec=RX, lw=1.7, zorder=6))
        ax.plot([c1[0],c2[0]],[c1[1],c2[1]], color=RX, lw=1.7, zorder=7)
        ax.plot([c3[0],c4[0]],[c3[1],c4[1]], color=RX, lw=1.7, zorder=7)

        n_turns = 6
        for t in np.linspace(-half_L+0.16, half_L-0.16, n_turns):
            pc = rc + t*u
            a = pc - half_W*v*0.92
            b = pc + half_W*v*0.92
            ax.plot([a[0],b[0]], [a[1],b[1]], color=RX, lw=1.3, zorder=8)
            ax.add_patch(plt.Circle((b[0],b[1]), .045, fc=RX, ec=RX, zorder=9))

        ax.annotate("Rotor", xy=(p_in[0]+0.3*u[0]-0.32*v[0], p_in[1]+0.3*u[1]-0.32*v[1]),
                    xytext=(5.55, 1.0), fontsize=10.5, color=TX, ha="left",
                    arrowprops=dict(arrowstyle="->", color=TX, lw=1.1))

        # --- Terminais i_r (saída externa do rotor, retas horizontais) ---
        t1 = p_out + half_W*0.6*v
        t2 = p_out - half_W*0.6*v
        e1 = t1 + np.array([1.15, 0.0])
        e2 = t2 + np.array([1.15, 0.0])
        ax.plot([t1[0],e1[0]],[t1[1],e1[1]], color=RX, lw=1.5, zorder=7)
        ax.plot([t2[0],e2[0]],[t2[1],e2[1]], color=RX, lw=1.5, zorder=7)
        ax.add_patch(plt.Circle(e2, .09, fc="white", ec=RX, lw=1.5, zorder=8))
        ax.annotate("", xy=(e1[0]+0.5, e1[1]), xytext=e1,
                    arrowprops=dict(arrowstyle="->", color=RX, lw=1.6))
        ax.text(e1[0]+0.65, e1[1]+0.04, "$i_r$", color=RX, fontsize=12, va="center")

        # --- Ângulo θ (vértice de anotação) ---
        theta_arc_r = 0.78
        t_arc = np.linspace(np.pi/2, np.pi/2 - th, 30)
        arc_pts = vertex[:, None] + theta_arc_r*np.array([np.cos(t_arc), np.sin(t_arc)])
        ax.plot(arc_pts[0], arc_pts[1], color=LR, lw=1.6, zorder=10)
        mid_a = np.pi/2 - th/2
        ax.text(vertex[0]+1.02*theta_arc_r*np.cos(mid_a), vertex[1]+1.25*theta_arc_r*np.sin(mid_a),
                r"$\theta$", color=LR, fontsize=13, ha="center")

        # --- ω_m (sentido de rotação, arco menor aninhado, mesmo vértice) ---
        r_om = 0.46
        t_om = np.linspace(np.pi/2 - 0.12, np.pi/2 - th + 0.12, 18)
        om_pts = vertex[:, None] + r_om*np.array([np.cos(t_om), np.sin(t_om)])
        ax.plot(om_pts[0], om_pts[1], color=RX, lw=1.6, zorder=10)
        ax.annotate("", xy=(om_pts[0][-1], om_pts[1][-1]), xytext=(om_pts[0][-3], om_pts[1][-3]),
                    arrowprops=dict(arrowstyle="-|>", color=RX, lw=1.6), zorder=10)
        ax.text(vertex[0]-0.85, vertex[1]-0.32, r"$\omega_m$", color=RX, fontsize=11, ha="center")

        ax.set_title("Máquina elementar de dois enrolamentos", fontsize=10.5, color=TX, pad=10)
        fig.tight_layout(); return fig

    def fig_maquina_cilindrica():
        """Seção transversal de máquina cilíndrica: entreferro uniforme, eixos estator/rotor."""
        fig, ax = _mpl_base((6.2, 5.4))
        ax.set_xlim(-3.6, 4.6); ax.set_ylim(-3.2, 3.5)

        R_out, R_in = 2.3, 1.85

        ring = mpatches.Wedge((0, 0), R_out, 0, 360, width=R_out-R_in,
                               facecolor="#3d8ef022", edgecolor=TX, lw=1.6, zorder=2)
        ax.add_patch(ring)
        ax.add_patch(plt.Circle((0, 0), R_in, fc="white", ec=TX, lw=1.6, zorder=3))

        theta = np.radians(35)

        ax.plot([-3.3, 3.3], [0, 0], color=AZ, lw=1.3, ls="--", zorder=4)
        ax.annotate("", xy=(3.3, 0), xytext=(3.0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=AZ, lw=1.3), zorder=4)
        ax.text(3.45, 0, "Eixo do\nestator", fontsize=9, color=AZ, ha="left", va="center")

        ax.plot([-2.4*np.cos(theta), 2.4*np.cos(theta)], [-2.4*np.sin(theta), 2.4*np.sin(theta)],
                color=RX, lw=1.3, ls="--", zorder=4)
        ax.annotate("", xy=(2.4*np.cos(theta), 2.4*np.sin(theta)),
                    xytext=(2.1*np.cos(theta), 2.1*np.sin(theta)),
                    arrowprops=dict(arrowstyle="-|>", color=RX, lw=1.3), zorder=4)
        ax.text(2.55*np.cos(theta), 2.55*np.sin(theta)+0.2, "Eixo do\nrotor",
                fontsize=9, color=RX, ha="left", va="bottom")

        rs = (R_out+R_in)/2
        ax.add_patch(plt.Circle((0, rs), .07, fc="none", ec=AZ, lw=1.6, zorder=5))
        ax.text(0, rs, "·", fontsize=14, color=AZ, ha="center", va="center", zorder=6)
        ax.text(-0.35, rs, "$S$", fontsize=11, color=AZ, ha="right", va="center")
        ax.add_patch(plt.Circle((0, -rs), .07, fc=AZ, ec=AZ, lw=1.6, zorder=5))
        ax.text(0.4, -rs, "$-S$", fontsize=11, color=AZ, ha="left", va="center")

        rr = 0.55
        rrx, rry = rr*np.cos(theta+np.pi/2), rr*np.sin(theta+np.pi/2)
        ax.add_patch(plt.Circle((rrx, rry), .06, fc="none", ec=RX, lw=1.6, zorder=5))
        ax.text(rrx-0.3, rry+0.15, "$R$", fontsize=11, color=RX, ha="right", va="center")
        ax.add_patch(plt.Circle((-rrx, -rry), .06, fc=RX, ec=RX, lw=1.6, zorder=5))
        ax.text(-rrx+0.3, -rry-0.15, "$-R$", fontsize=11, color=RX, ha="left", va="center")

        arc = np.linspace(0, theta, 30)
        ax.plot(1.15*np.cos(arc), 1.15*np.sin(arc), color=TX, lw=1.3, zorder=6)
        ax.text(1.4*np.cos(theta/2), 1.4*np.sin(theta/2), r"$\theta=\omega_m t+\delta$",
                fontsize=10, color=TX, ha="left", va="center")

        ax.set_title("Máquina cilíndrica — entreferro uniforme", fontsize=10, color=TX, pad=10)
        fig.tight_layout(); return fig

    def fig_taxonomia():
        """Diagrama hierárquico de classificação das máquinas elétricas."""
        fig, ax = plt.subplots(figsize=(11, 6.5))
        fig.patch.set_alpha(0); ax.set_facecolor("none"); ax.axis("off")
        ax.set_xlim(0, 100); ax.set_ylim(0, 60)

        def box(x, y, w, h, label, fc="white", fontsize=9, lw=1.4):
            ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                                                  fc=fc, ec=TX, lw=lw, zorder=3))
            ax.text(x+w/2, y+h/2, label, ha="center", va="center", fontsize=fontsize,
                    color=TX, zorder=4)

        def link(x1, y1, x2, y2):
            ax.plot([x1, x2], [y1, y2], color=CZ, lw=1.1, zorder=1)

        box(20, 53, 60, 5.5, "Máquinas Elétricas", fc="#3d8ef018", fontsize=11)

        box(10, 45, 55, 5, "Máquinas rotativas", fc="#3d8ef012", fontsize=10)
        box(72, 45, 22, 5, "Máquinas\nestacionárias", fc="#6b728015", fontsize=8.5)
        link(50, 53, 37, 50); link(50, 53, 83, 50)

        box(7, 37, 25, 5, "Corrente Contínua", fc="#1f9d5515", fontsize=9)
        box(35, 37, 28, 5, "Corrente Alternada", fc="#e07b0015", fontsize=9)
        box(74, 37, 18, 5, "Transformadores", fc="#6b728010", fontsize=8.5)
        link(37, 45, 19.5, 42); link(37, 45, 49, 42); link(83, 45, 83, 42)

        cc_labels = ["Excitação\nindependente", "Série/\nParalelo", "Servo-\nmotores", "Motores\nde passo"]
        cc_x0 = 5.5
        for i, lab in enumerate(cc_labels):
            x = cc_x0 + i*6.7
            box(x, 28, 6.3, 6.5, lab, fc="#1f9d550c", fontsize=7.2)
            link(19.5, 37, x+3.15, 34.5)

        box(35, 28, 14, 5, "Máquina\nSíncrona", fc="#e07b0018", fontsize=9)
        box(51, 28, 22, 5, "Máquina Assíncrona\n(Indução)", fc="#e07b0018", fontsize=9)
        link(49, 37, 42, 33); link(49, 37, 62, 33)

        box(33, 19, 9, 6, "Monofásico", fc="#e07b000c", fontsize=7.3)
        box(43, 19, 9, 6, "Trifásico", fc="#e07b000c", fontsize=7.3)
        link(42, 28, 37.5, 25); link(42, 28, 47.5, 25)

        asy_labels = ["Monofásico", "Trifásico", "Servo-\nmotores", "Sincro-\nnizadores"]
        asy_x0 = 54
        for i, lab in enumerate(asy_labels):
            x = asy_x0 + i*6.7
            box(x, 19, 6.3, 6, lab, fc="#e07b000c", fontsize=7.3)
            link(62, 28, x+3.1, 25)

        ax.set_title("Classificação das Máquinas Elétricas", fontsize=11.5, color=TX, pad=10)
        fig.tight_layout(); return fig

    # ════════════════════════════════════════════════════════════════════════
    # EXPLORADOR 4 — TORQUE PULSANTE EM MÁQUINAS CILÍNDRICAS
    # ════════════════════════════════════════════════════════════════════════

    def exp_torque():
        st.markdown("**Torque instantâneo em máquina cilíndrica** — compare o torque "
                     "pulsante com seu valor médio nos casos síncrono e assíncrono:")
        caso = st.radio("Caso", ["Síncrona ($\\omega_m=\\omega_s$, $\\omega_r=0$)",
                                  "Assíncrona ($\\omega_m=\\omega_s-\\omega_r$)"],
                         key="m1_exp4_caso", horizontal=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            Irm = st.slider("$I_{rm}$ (A)", 0.5, 5.0, 2.0, step=0.1, key="m1_exp4_Irm")
        with c2:
            Ism = st.slider("$I_{sm}$ (A)", 0.5, 5.0, 2.0, step=0.1, key="m1_exp4_Ism")
        with c3:
            delta = st.slider("δ (graus)", -90, 90, 30, step=5, key="m1_exp4_delta")

        M = 1.0
        ws = 2*np.pi*1.0
        delta_r = np.radians(delta)
        t = np.linspace(0, 2.0, 600)

        if caso.startswith("Síncrona"):
            T_inst = -(Irm*Ism*M/2) * (np.sin(2*ws*t + delta_r) + np.sin(delta_r))
            T_med = -(Irm*Ism*M/2) * np.sin(delta_r)
        else:
            wr = st.slider("$\\omega_r$ / $\\omega_s$ (escorregamento)", 0.05, 0.95, 0.3,
                            step=0.05, key="m1_exp4_wr")
            wr_abs = wr*ws
            alpha = np.radians(20)
            T_inst = -(Irm*Ism*M/4) * (
                np.sin(2*ws*t + alpha + delta_r) + np.sin(-2*wr_abs*t - alpha + delta_r)
                + np.sin(2*ws*t - 2*wr_abs*t - alpha + delta_r) + np.sin(alpha + delta_r))
            T_med = -(Irm*Ism*M/4) * np.sin(alpha + delta_r)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=T_inst, mode="lines",
                                  line=dict(color=AZ, width=2.5), name="T(t) instantâneo"))
        fig.add_trace(go.Scatter(x=[t[0], t[-1]], y=[T_med, T_med], mode="lines",
                                  line=dict(color=LR, width=2, dash="dash"),
                                  name=f"T médio = {T_med:.3f} N·m"))
        fig.update_layout(title="Torque eletromagnético — componente pulsante + valor médio",
                           xaxis_title="t (s)", yaxis_title="Torque (N·m)",
                           legend=dict(orientation="h", y=-0.25))
        show_plot(fig, key="m1_exp4_torque", height=380)

        st.metric("Torque médio", f"{T_med:.3f} N·m")
        st.info("No caso **síncrono**, o torque pulsa em $2\\omega_s$ em torno de um valor "
                "médio não-nulo — condição $|\\omega_m|=|\\omega_s|$ satisfeita para qualquer "
                "$\\delta$. No caso **assíncrono**, o valor médio depende do escorregamento "
                "através do ângulo $\\alpha$; em máquinas de indução reais $\\alpha$ e $I_{rm}$ "
                "resultam da própria indução no rotor, não são livres como aqui.")

    # ═══════════════════════════════════════════════════════════════════════════════
    # CABEÇALHO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.title("🔋 Introdução à Conversão Eletromecânica de Energia")
    st.caption("⚡ SINTONIA · Máquinas Elétricas · 👤 Marcus V A Fernandes · ✉️ marcus.fernandes@ifrn.edu.br")
    st.markdown("---")

    # ── Índice ────────────────────────────────────────────────────────────────────
    with st.expander("📋 Índice — clique para expandir", expanded=False):
        st.markdown("""
    **[1. Relação i-H — Lei Circuital de Ampère](#1-relacao-i-h-lei-circuital-de-ampere)**

    **[2. Relação B-H — Permeabilidade Magnética](#2-relacao-b-h-permeabilidade-magnetica)**

    **[3. Circuito Magnético Equivalente](#3-circuito-magnetico-equivalente)**
    - 3.1 Presença de entreferro · 3.2 Máquina rotativa e frangeamento

    **[4. Indutância e Lei de Faraday](#4-indutancia-e-lei-de-faraday)**
    - 4.1 Indutância mútua e energia armazenada

    **[5. Histerese Magnética](#5-histerese-magnetica)**

    **[6. Correntes Parasitas e Perdas no Núcleo](#6-correntes-parasitas-e-perdas-no-nucleo)**

    **[7. Processo de Conversão Eletromecânica de Energia](#7-processo-de-conversao-eletromecanica-de-energia)**

    **[8. Energia e Coenergia no Campo Magnético](#8-energia-e-coenergia-no-campo-magnetico)**
    - 8.1 Especialização para sistemas lineares

    **[9. Equações Dinâmicas e Tipos de Ação](#9-equacoes-dinamicas-e-tipos-de-acao)**

    **[10. Conceitos Básicos de Máquinas Rotativas](#10-conceitos-basicos-de-maquinas-rotativas)**
    - Estator, rotor e máquina elementar de dois enrolamentos
    - Fluxos concatenados e energia armazenada

    **[11. Torque Eletromagnético](#11-torque-eletromagnetico)**
    - Torque via coenergia · Máquinas cilíndricas
    - Condição de torque médio não-nulo · Casos síncrono e assíncrono

    **[12. Classificação das Máquinas Elétricas](#12-classificacao-das-maquinas-eletricas)**

    **[🎛️ Exploradores Interativos](#exploradores-interativos)**
    - Circuito magnético · Curva B-H · Força eletromagnética · Torque pulsante

    **Referências** (ao final da página)
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 1 — RELAÇÃO i-H
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("1. Relação i-H — Lei Circuital de Ampère")

    st.markdown(r"""
    **Regra da mão direita:** com o polegar no sentido da corrente $i$, os dedos indicam o
    sentido das linhas de campo $\vec{H}$.

    A **lei circuital de Ampère** estabelece que a integral de linha de $\vec{H}$ ao longo de
    qualquer contorno fechado $C$ é igual à soma das correntes que atravessam a superfície
    delimitada por esse contorno:

    $$\oint_C \vec{H} \cdot d\vec{l} = \sum_k N_k\, i_k$$

    Para um **condutor isolado** percorrido por corrente $i$, a simetria circular permite
    resolver a integral diretamente, a uma distância $r$ do condutor:

    $$H \cdot 2\pi r = i \quad\Rightarrow\quad H = \frac{i}{2\pi r}$$

    Essa relação entre corrente e campo $H$ é a base para definir o **circuito magnético
    equivalente**, apresentado na Seção 3.
    """)

    show_fig(fig_regra_mao(), 0.45)

    col1, col2 = st.columns(2)
    with col1:
        show_fig(fig_campo_r(), 0.95)
    with col2:
        show_fig(fig_ampere_contorno(), 0.95)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 2 — RELAÇÃO B-H
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("2. Relação B-H — Permeabilidade Magnética")

    st.markdown(r"""
    A **densidade de fluxo magnético** $B$ (T = Wb/m²) relaciona-se com $H$ pela permeabilidade
    do meio:

    $$B = \mu\,H = \mu_0\,\mu_r\,H$$

    - $\mu_0 = 4\pi\times10^{-7}$ H/m: permeabilidade do vácuo
    - $\mu_r$: permeabilidade relativa (adimensional)

    | Material | $\mu_r$ |
    |----------|-----------|
    | Ar, vácuo, Cu, Al | ≈ 1 |
    | Ferrite | 100 – 1 000 |
    | Aço elétrico (máquinas) | **2 000 – 6 000** |

    > ⚠️ Para materiais ferromagnéticos, $\mu_r$ **não é constante**: varia com $H$ (curva de
    > magnetização não-linear) e com a história magnética do material — efeito detalhado na
    > Seção 5 (Histerese).
    """)

    show_plot(plotly_BH(), key="m1_fig_bh", height=380)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 3 — CIRCUITO MAGNÉTICO EQUIVALENTE
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("3. Circuito Magnético Equivalente")

    st.markdown(r"""
    Combinando a lei de Ampère, $B=\mu H$ e $\phi=B\,A$, obtém-se a **lei do circuito
    magnético**, que relaciona força magnetomotriz, relutância e fluxo de forma análoga à
    lei de Ohm:

    $$\mathcal{F} = N\,i \quad \text{(FMM, A·t)}$$

    $$\mathcal{R} = \frac{\ell}{\mu\,A} \quad \text{(relutância, A·t/Wb)}$$

    $$\phi = \frac{\mathcal{F}}{\mathcal{R}} = \frac{N\,i\,\mu\,A}{\ell}$$
    """)

    show_fig(fig_circuito_mag(), 0.5)

    st.markdown("**Analogia: circuito elétrico ↔ circuito magnético**")
    show_fig(fig_analogia_combinada(), 0.7)

    st.markdown(r"""
    | Circuito Elétrico | Circuito Magnético |
    |-------------------|--------------------|
    | FEM $e$ (V) | FMM $\mathcal{F}=Ni$ (A·t) |
    | Corrente $i$ (A) | Fluxo $\phi$ (Wb) |
    | Resistência $R$ (Ω) | Relutância $\mathcal{R}$ (A·t/Wb) |
    | $e = R\,i$ | $\mathcal{F} = \mathcal{R}\,\phi$ |
    """)

    st.markdown("### 3.1 Presença de Entreferro")
    st.markdown(r"""
    Com um entreferro $\ell_g$, as relutâncias do núcleo e do ar somam-se em série:

    $$N\,i = (\mathcal{R}_c + \mathcal{R}_g)\,\phi$$

    $$\mathcal{R}_c = \frac{\ell_c}{\mu_r\mu_0 A_c}, \quad \mathcal{R}_g = \frac{\ell_g}{\mu_0 A_g}$$

    > ⚠️ **Dominância do entreferro:** com $\mu_r=2000$, 1 mm de ar equivale a 2 m de ferro de
    > mesma seção — o entreferro domina a relutância total do circuito.
    """)

    col1, col2 = st.columns(2)
    with col1:
        show_fig(fig_entreferro_geom(), 0.95)
    with col2:
        show_png(schem_entreferro(), 0.95)
        st.caption("Circuito equivalente: ℱ em série com ℛc e ℛg")

    st.markdown("### 3.2 Máquina Rotativa e Frangeamento")
    st.markdown(r"""
    Em máquinas rotativas, o entreferro separa estator e rotor. O **frangeamento**
    (_fringing_) alarga as linhas de campo no ar, aumentando a área efetiva $A_g > A_c$.
    Para um polo retangular de dimensões $a\times b$, uma correção usual é:

    $$A_g \approx (a + \ell_g)(b + \ell_g) \qquad \mathcal{R}_g = \frac{\ell_g}{\mu_0 A_g}$$
    """)

    show_fig(fig_frangeamento(), 0.75)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 4 — INDUTÂNCIA E LEI DE FARADAY
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("4. Indutância e Lei de Faraday")

    st.markdown(r"""
    O **fluxo concatenado** $\lambda$ (Wb·t) é o fluxo total que atravessa todas as $N$ espiras:

    $$\lambda = N\,\phi = \frac{N^2}{\mathcal{R}}\,i = L\,i$$

    A **indutância** $L$ (H = Wb/A) depende apenas da geometria e do material do núcleo:

    $$L = \frac{\lambda}{i} = \frac{N^2}{\mathcal{R}} = \frac{N^2\,\mu\,A}{\ell}$$

    A **lei de Faraday** descreve a FEM induzida pela variação do fluxo concatenado. Na
    convenção adotada neste material (mesma da Seção 8, onde $dW_e = e\,i\,dt$):

    $$e = \frac{d\lambda}{dt} = N\frac{d\phi}{dt}$$

    Para $L$ constante (sistema linear), essa relação se reduz à forma mais familiar:

    $$e = L\frac{di}{dt}$$

    **Energia armazenada no campo magnético** de uma bobina, em sistema linear:

    $$W_L = \frac{1}{2}\,L\,i^2 = \frac{\lambda^2}{2L} = \frac{1}{2}\,\mathcal{R}\,\phi^2$$

    > A variação de $W_L$ com a posição do rotor é o mecanismo de **geração de força e torque
    > eletromagnético** — princípio retomado nas Seções 9 (força) e 11 (torque) deste módulo.
    """)

    show_plot(plotly_energia_indutiva(), key="m1_fig_energia", height=340)

    st.markdown("### 4.1 Indutância Mútua")

    col1, col2 = st.columns([1, 1])
    with col1:
        show_fig(fig_acoplamento(), 0.95)
    with col2:
        st.markdown(r"""
    Para **duas bobinas acopladas** num mesmo núcleo:

    $$\lambda_1 = L_{11}\,i_1 + L_{12}\,i_2$$
    $$\lambda_2 = L_{21}\,i_1 + L_{22}\,i_2 \quad (L_{12}=L_{21})$$

    - $L_{11}$, $L_{22}$: **indutâncias próprias** (auto-induzidas)
    - $L_{12} = L_{21}$: **indutância mútua** (reciprocidade de Neumann)
    - Análise linear válida para $\mu$ constante (região linear da curva $B$-$H$)
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 5 — HISTERESE MAGNÉTICA
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("5. Histerese Magnética")

    st.markdown(r"""
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

    A **área interna do laço** corresponde à energia dissipada como calor em cada ciclo de
    magnetização:

    $$W_h = \oint H\,dB \quad\text{(área do laço)}$$

    $$P_h = k_h\,f\,B_{max}^n \quad (n \approx 1{,}6 \text{ a } 2)$$
    """)

    show_plot(plotly_histerese(), key="m1_fig_hist", height=380)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 6 — CORRENTES PARASITAS E PERDAS NO NÚCLEO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("6. Correntes Parasitas e Perdas no Núcleo")

    st.markdown(r"""
    **Correntes parasitas** (_Eddy currents_) são induzidas no núcleo condutor pela variação
    de $B$ no tempo, formando laços fechados que dissipam energia como calor (efeito Joule).

    **Redução:**
    - Material de **alta resistividade** (ferrite, aço silício): dificulta a circulação das
      correntes
    - **Laminação**: chapas finas isoladas entre si interrompem os laços de corrente — como
      $P_e \propto d^2$, reduzir a espessura $d$ das chapas diminui as perdas rapidamente

    **Perdas por correntes parasitas** (por volume):

    $$P_e = k_e\,f^2\,B_{max}^2\,d^2$$

    **Perdas totais no núcleo** (perdas no ferro):

    $$P_c = P_h + P_e = k_h\,f\,B_{max}^n + k_e\,f^2\,B_{max}^2$$

    > As perdas no núcleo ocorrem mesmo a vazio, pois dependem de $B_{max}$ e $f$, não da
    > corrente de carga.
    """)

    show_fig(fig_parasita_geom(), 0.6)
    show_plot(plotly_perdas_nucleo(), key="m1_fig_perdas", height=380)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 7 — PROCESSO DE CONVERSÃO ELETROMECÂNICA DE ENERGIA
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("7. Processo de Conversão Eletromecânica de Energia")

    st.markdown(r"""
    A conversão eletromecânica de energia ocorre através do **campo magnético**, elo entre
    o sistema elétrico (fonte, enrolamentos) e o sistema mecânico (parte móvel, carga). Há
    dissipação de energia em cada estágio:
    """)

    show_fig(fig_fluxo_conversao(), 0.75)

    st.markdown(r"""
    O balanço de energia para uma variação infinitesimal $dt$ relaciona a energia elétrica de
    entrada ($dW_e$), a energia mecânica entregue ($dW_m$), a energia armazenada no campo
    ($dW_f$) e as perdas:

    $$dW_e = dW_m + dW_f + Perdas$$

    Isolando cada termo sob hipóteses simplificadoras (perdas nulas; parte móvel fixa ou em
    movimento), obtêm-se as expressões de energia e força desenvolvidas a seguir.
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 8 — ENERGIA E COENERGIA NO CAMPO MAGNÉTICO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("8. Energia e Coenergia no Campo Magnético")

    st.markdown(r"""
    **Energia do campo — parte móvel fixa.** Com perdas nulas e a parte móvel fixa
    ($dW_m=0$), o balanço da Seção 7 se reduz a $dW_e = dW_f$. Como $dW_e = e\,i\,dt$ e, pela
    lei de Faraday, $e = d\lambda/dt$:

    $$dW_e = e\,i\,dt = i\,d\lambda \qquad\Rightarrow\qquad W_f = \int_0^{\lambda} i\,d\lambda$$

    Usando as relações de circuito magnético da Seção 3 ($Ni = H_c\ell_c + H_g\ell_g$ e
    $\lambda = N\phi$), essa integral se separa em uma parcela do núcleo e uma do entreferro:

    $$W_f = W_{fc} + W_{fg} \qquad\text{com}\qquad W_{fc} = \int H_c\,dB\;V_c \qquad W_{fg} = \frac{B_g^2}{2\mu_0}\,V_g$$

    onde $V_c = \ell_c A$ e $V_g = \ell_g A$ são os volumes do núcleo e do entreferro.
    """)

    st.markdown(r"""
    **Energia e coenergia.** No plano $\lambda$-$i$, a energia corresponde à área entre a
    curva e o eixo $\lambda$ (área A), e a **coenergia** $W_f'$, à área entre a curva e o eixo
    $i$ (área B):

    $$W_f = \int_0^{\lambda} i\,d\lambda \qquad\qquad W_f' = \int_0^{i} \lambda\,di$$

    > Em regiões de maior entreferro, a curva $\lambda$-$i$ se aproxima de uma reta e
    > $W_f' = W_f$. Em núcleos saturados (figura abaixo), $W_f' > W_f$ — a coenergia não tem
    > significado físico direto, mas é a ferramenta usada para calcular a força mecânica.
    """)

    show_fig(fig_energia_coenergia(), 0.55)

    st.markdown("### 8.1 Energia Mecânica e Força")
    st.markdown(r"""
    Com perdas nulas e a parte móvel deslocando-se de $x_1$ a $x_2$:

    **Posição variando lentamente** (corrente ≈ constante): $dW_m = dW_f'$, e a força é a
    derivada da coenergia com $i$ constante:

    $$f_m = \left.\frac{\partial W_f'(i,x)}{\partial x}\right|_{i=\text{constante}}$$

    **Posição variando rapidamente** ($\lambda$ ≈ constante, $i\,d\lambda\approx 0$):
    $dW_m = dW_f$, e a força é a derivada da energia com sinal trocado, $\lambda$ constante:

    $$f_m = -\left.\frac{\partial W_f(i,x)}{\partial x}\right|_{\lambda=\text{constante}}$$

    Os dois resultados são equivalentes: decorrem da relação $W_f + W_f' = \lambda\,i$, que
    relaciona as derivadas de $W_f$ e $W_f'$ com sinais opostos.
    """)

    st.markdown("#### Especialização para sistemas lineares")
    st.markdown(r"""
    Em um sistema **linear** ($\lambda = L(x)\,i$, $W_f = \frac{1}{2}L(x)i^2$), as duas
    expressões da força se reduzem a:

    $$f_m = -\frac{1}{2}\,i^2\,\frac{dL(x)}{dx} \quad(\lambda\text{ constante})$$

    $$f_m = \frac{1}{2}\,i^2\,\frac{dL(x)}{dx} \quad(i\text{ constante})$$

    > Na prática usa-se a forma via coenergia (sinal positivo), pois $i$ é a variável
    > tipicamente controlada: a força sempre tende a deslocar a parte móvel no sentido de
    > **aumentar** $L(x)$.
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 9 — EQUAÇÕES DINÂMICAS E TIPOS DE AÇÃO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("9. Equações Dinâmicas e Tipos de Ação")

    st.markdown(r"""
    O acoplamento entre os sistemas elétrico e mecânico, incluindo os elementos mecânicos
    usuais (mola $K$, amortecedor $B$, massa $M$) e uma força externa $f_0(t)$, resulta na
    equação dinâmica completa do sistema:
    """)

    show_fig(fig_sistema_dinamico(), 0.85)

    st.markdown(r"""
    Pela 2ª lei de Newton, com $f_K = -K(x-x_0)$, $f_D = -B\,\dfrac{dx}{dt}$ e
    $f_M = -M\,\dfrac{d^2x}{dt^2}$:

    $$f_0(t) = M\frac{d^2x}{dt^2} + B\frac{dx}{dt} + K(x-x_0) + f_m(x,i)$$

    Para um sistema **linear sem perdas**, substituindo a força eletromagnética obtida na
    Seção 8.1:

    $$f_0(t) = M\frac{d^2x}{dt^2} + B\frac{dx}{dt} + K(x-x_0) + \frac{1}{2}\,i^2\,\frac{dL(x)}{dx}$$

    Essa equação acopla a dinâmica mecânica (posição $x$) à variável elétrica (corrente $i$),
    e é a base para a modelagem de atuadores eletromagnéticos, relés e, de forma generalizada,
    das máquinas elétricas rotativas estudadas a seguir.
    """)

    st.markdown("### Tipos de Ação")
    st.markdown(r"""
    Toda conversão eletromecânica de energia ocorre por uma de duas ações fundamentais:

    - **Ação geradora:** quando um condutor se move em um campo magnético, uma tensão é
      induzida no condutor (lei de Faraday).
    - **Ação motora:** quando um condutor percorrido por corrente é posicionado em um campo
      magnético, uma força mecânica é exercida sobre o condutor (força de Laplace, $F=Bi\ell$).
    """)

    show_fig(fig_acao_geradora_motora(), 0.78)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 10 — CONCEITOS BÁSICOS DE MÁQUINAS ROTATIVAS
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("10. Conceitos Básicos de Máquinas Rotativas")

    st.markdown(r"""
    Uma máquina rotativa tem duas partes principais: o **estator**, parte estática, e o
    **rotor**, parte móvel que gira em torno de um eixo. A máquina elementar de dois
    enrolamentos abaixo ilustra os elementos comuns a toda máquina rotativa: um enrolamento
    de estator percorrido por $i_s$, um enrolamento de rotor percorrido por $i_r$, e um
    ângulo $\theta$ entre os eixos magnéticos dos dois enrolamentos, que varia com a
    velocidade angular do rotor $\omega_m$.
    """)

    show_fig(fig_maquina_elementar(), 0.7)

    st.markdown(r"""
    **Fluxos concatenados.** Cada enrolamento é concatenado pelo fluxo produzido por ambas as
    correntes, através das indutâncias próprias ($L_{ss}$, $L_{rr}$) e da indutância mútua
    ($L_{sr}=L_{rs}$), que depende da posição relativa $\theta$ entre os enrolamentos:

    $$\lambda_s = L_{ss}\,i_s + L_{sr}\,i_r \qquad\qquad \lambda_r = L_{sr}\,i_s + L_{rr}\,i_r$$

    **Energia do campo.** Substituindo na expressão diferencial de $W_f$ (Seção 8) e
    integrando cada termo de $0$ até o valor final de cada corrente:

    $$dW_f = i_s\,L_{ss}\,di_s + i_r\,L_{rr}\,di_r + L_{sr}\,d(i_r\,i_s)$$

    $$W_f = \frac{1}{2}L_{ss}\,i_s^2 + \frac{1}{2}L_{rr}\,i_r^2 + L_{sr}\,i_r\,i_s$$

    Essa expressão de energia é o ponto de partida para obter o torque eletromagnético,
    desenvolvido na próxima seção.
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 11 — TORQUE ELETROMAGNÉTICO
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("11. Torque Eletromagnético")

    st.markdown(r"""
    Por analogia com a força mecânica linear (Seção 8.1), o torque é obtido derivando a
    coenergia em relação à posição angular $\theta$, com as correntes mantidas constantes:

    $$T = \left.\frac{\partial W_f'(i,\theta)}{\partial\theta}\right|_{i=\text{constante}}$$

    Aplicando à energia da Seção 10 (em sistemas magneticamente lineares, $W_f=W_f'$):

    $$T = \frac{1}{2}i_s^2\frac{dL_{ss}}{d\theta} + \frac{1}{2}i_r^2\frac{dL_{rr}}{d\theta} + i_r\,i_s\,\frac{dL_{sr}}{d\theta}$$
    """)

    st.markdown("### Máquinas cilíndricas")
    st.markdown(r"""
    Numa **máquina cilíndrica**, o entreferro é uniforme: $L_{ss}$ e $L_{rr}$ não dependem de
    $\theta$, e os dois primeiros termos do torque se anulam, restando apenas o termo de
    acoplamento mútuo:

    $$T = i_r\,i_s\,\frac{dL_{sr}}{d\theta}$$
    """)

    show_fig(fig_maquina_cilindrica(), 0.55)

    st.markdown(r"""
    Considerando o rotor girando a velocidade constante, com a indutância mútua variando
    senoidalmente com $\theta$, e correntes senoidais de estator e rotor com frequências
    elétricas próprias:

    $$\theta = \omega_m t + \delta \qquad L_{sr} = M\cos\theta$$

    $$i_r = I_{rm}\cos(\omega_r t+\alpha) \qquad i_s = I_{sm}\cos(\omega_s t)$$

    Substituindo e expandindo o produto de cossenos em soma de senos, o torque instantâneo
    resulta em **quatro componentes oscilatórias**, cada uma numa combinação distinta das
    três frequências envolvidas:

    $$T = -\frac{I_{rm}I_{sm}M}{4}\left(\sin[(\omega_m+\omega_s+\omega_r)t+\alpha+\delta] + \sin[(\omega_m-\omega_s-\omega_r)t-\alpha+\delta] + \sin[(\omega_m+\omega_s-\omega_r)t-\alpha+\delta] + \sin[(\omega_m-\omega_s+\omega_r)t+\alpha+\delta]\right)$$

    > Cada termo oscila no tempo e tem média nula — **exceto** quando o argumento do seno
    > perde a dependência temporal, isto é, quando o coeficiente de $t$ se anula. Isso só
    > ocorre quando:
    > $$|\omega_m| = |\omega_s \pm \omega_r|$$
    > Essa é a condição fundamental para que uma máquina cilíndrica produza **torque médio
    > não-nulo** — a base para distinguir máquinas síncronas de assíncronas.
    """)

    st.markdown("### Máquina síncrona")
    st.markdown(r"""
    Com $\omega_m=\omega_s$, $\omega_r=0$ (corrente de rotor contínua) e $\alpha=0$, os quatro
    termos colapsam em apenas dois: um oscilante em $2\omega_s$ e um constante:

    $$T = -\frac{I_r\,I_{sm}\,M}{2}\left[\sin(2\omega_s t+\delta)+\sin(\delta)\right]$$

    O torque pulsa em $2\omega_s$ em torno do valor médio $-\frac{1}{2}I_rI_{sm}M\sin\delta$,
    não-nulo para qualquer $\delta \ne 0,\pi$.
    """)

    st.markdown("### Máquina assíncrona")
    st.markdown(r"""
    Com $\omega_m=\omega_s-\omega_r$ (rotor girando mais devagar que o campo do estator —
    escorregamento), o torque instantâneo é:

    $$T = -\frac{I_{rm}I_{sm}M}{4}\left(\sin(2\omega_s t+\alpha+\delta) + \sin(-2\omega_r t-\alpha+\delta) + \sin(2\omega_s t-2\omega_r t-\alpha+\delta) + \sin(\alpha+\delta)\right)$$

    Novamente há uma parcela constante, $-\frac{1}{4}I_{rm}I_{sm}M\sin(\alpha+\delta)$, que
    sustenta o torque médio — mas aqui $\alpha$ e $I_{rm}$ não são impostos externamente: em
    uma máquina de indução real, eles resultam da própria corrente induzida no rotor pelo
    escorregamento entre o campo girante e o rotor.
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # SEÇÃO 12 — CLASSIFICAÇÃO DAS MÁQUINAS ELÉTRICAS
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("12. Classificação das Máquinas Elétricas")

    st.markdown(r"""
    As máquinas elétricas dividem-se primeiro em **rotativas** (estator e rotor, como
    estudado na Seção 10) e **estacionárias** (transformadores, sem partes móveis). Dentro
    das rotativas, a classificação principal é pelo tipo de alimentação — corrente contínua
    ou corrente alternada — e, dentro de cada uma, pelo princípio de operação:
    """)

    show_fig(fig_taxonomia(), 0.95)

    st.markdown(r"""
    A distinção entre **máquina síncrona** e **máquina assíncrona (de indução)**, vista na
    Seção 11, é a divisão fundamental dentro das máquinas de corrente alternada: na síncrona
    o rotor gira exatamente na velocidade do campo girante ($\omega_m=\omega_s$); na
    assíncrona há escorregamento ($\omega_m=\omega_s-\omega_r$), característico do
    funcionamento por indução. Os módulos seguintes detalham cada uma dessas famílias.
    """)

    st.divider()


    # ═══════════════════════════════════════════════════════════════════════════════
    # EXPLORADORES INTERATIVOS
    # ═══════════════════════════════════════════════════════════════════════════════
    st.header("🎛️ Exploradores Interativos")

    tab1, tab2, tab3, tab4 = st.tabs(["Explorador 1 — Circuito Magnético",
                                       "Explorador 2 — Curva B-H",
                                       "Explorador 3 — Força Eletromagnética",
                                       "Explorador 4 — Torque Pulsante"])
    with tab1: exp_circuito()
    with tab2: exp_BH()
    with tab3: exp_forca()
    with tab4: exp_torque()

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
        "🔋 Conversão Eletromecânica de Energia &nbsp;·&nbsp; ⚡ SINTONIA — Máquinas Elétricas<br>"
        "👤 Marcus V A Fernandes &nbsp;·&nbsp; 🏛️ IFRN-CNAT"
        " &nbsp;·&nbsp; 🏷️ v1.0 &nbsp;·&nbsp; 📅 2026"
        "</div>",
        unsafe_allow_html=True,
    )
