# -*- coding: utf-8 -*-
"""情報屋ロゴを、文字をパス化したSVG（フォントがなくても同じ見た目）として書き出す。
使い方: python3 tools/make_logo.py   → docs/assets/ に logo.svg, logo-dark.svg, icon.svg, favicon.svg ほか
"""
import os
from fontTools.ttLib import TTCollection
from fontTools.pens.svgPathPen import SVGPathPen

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"   # 0番 = Noto Sans CJK JP Black
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "assets")
os.makedirs(OUT, exist_ok=True)

font = TTCollection(FONT).fonts[0]
gs = font.getGlyphSet()
cmap = font.getBestCmap()

def glyph(ch, x, y, size, sx=1.0):
    """文字を、左端x・ベースラインyに置いたパス（transform付き）にする"""
    pen = SVGPathPen(gs)
    gs[cmap[ord(ch)]].draw(pen)
    k = size / 1000.0
    return f'<path transform="translate({x} {y}) scale({k*sx:.5f} {-k:.5f})" d="{pen.getCommands()}"/>'

NAVY, ORANGE, CREAM = "#14284B", "#F28C28", "#FBF7EE"

def zyo(text_fill, dots_fill):
    """「情」＝虫めがね（りっしんべんの縦棒＋目）＋左払い・右払い＋青"""
    return (
        f'<g fill="{text_fill}">{glyph("青", 168, 200, 180, 0.66)}</g>'
        f'<rect x="121" y="128" width="14" height="80" rx="7" fill="{ORANGE}"/>'
        f'<circle cx="128" cy="98" r="30" fill="#FFE7BF" stroke="{ORANGE}" stroke-width="12"/>'
        f'<circle cx="118" cy="100" r="5.5" fill="{NAVY}"/><circle cx="138" cy="100" r="5.5" fill="{NAVY}"/>'
        f'<path d="M104 140 L117 142 Q112 164 94 184 Q99 162 104 140 Z" fill="{dots_fill}"/>'
        f'<path d="M152 140 L139 142 Q144 164 162 184 Q157 162 152 140 Z" fill="{dots_fill}"/>'
        f'<path d="M109 86 A22 22 0 0 1 119 77" stroke="#FFFFFF" stroke-width="4" fill="none" stroke-linecap="round"/>'
    )

def detective(dark):
    c = dict(
        shadow=("#000000", 0.25) if dark else (NAVY, 0.12),
        leg="#2C4F8F" if dark else NAVY,
        arm="#3E67B0" if dark else "#1E3A6E",
        coat="#3E67B0" if dark else "#1E3A6E",
        collar="#2C4F8F" if dark else NAVY,
        hat="#223E73" if dark else NAVY,
        hatline=f' stroke="{CREAM}" stroke-width="1.5"' if dark else "",
    )
    return (
        '<g transform="translate(14 0)">'
        f'<ellipse cx="735" cy="244" rx="42" ry="5" fill="{c["shadow"][0]}" opacity="{c["shadow"][1]}"/>'
        f'<rect x="712" y="205" width="12" height="32" fill="{c["leg"]}"/><rect x="746" y="205" width="12" height="32" fill="{c["leg"]}"/>'
        f'<ellipse cx="716" cy="238" rx="14" ry="6" fill="{c["leg"]}"/><ellipse cx="754" cy="238" rx="14" ry="6" fill="{c["leg"]}"/>'
        f'<path d="M700 128 L676 156" stroke="{c["arm"]}" stroke-width="16" stroke-linecap="round" fill="none"/>'
        '<circle cx="672" cy="160" r="7" fill="#F6D7B0"/>'
        f'<path d="M696 118 Q735 106 774 118 L786 214 L684 214 Z" fill="{c["coat"]}"/>'
        f'<rect x="690" y="160" width="90" height="9" fill="{ORANGE}"/>'
        f'<line x1="735" y1="150" x2="735" y2="214" stroke="{NAVY}" stroke-width="2"/>'
        '<circle cx="735" cy="84" r="22" fill="#F6D7B0"/>'
        f'<polygon points="735,114 706,104 700,136 735,150" fill="{c["collar"]}" stroke="{CREAM}" stroke-width="1.5" stroke-linejoin="round"/>'
        f'<polygon points="735,114 764,104 770,136 735,150" fill="{c["collar"]}" stroke="{CREAM}" stroke-width="1.5" stroke-linejoin="round"/>'
        f'<ellipse cx="735" cy="68" rx="42" ry="9" fill="{c["hat"]}"{c["hatline"]}/>'
        f'<path d="M711 68 L713 44 Q735 34 757 44 L759 68 Z" fill="{c["hat"]}"{c["hatline"]} stroke-linejoin="round"/>'
        f'<rect x="712" y="56" width="46" height="8" fill="{ORANGE}"/>'
        f'<circle cx="726" cy="87" r="2.2" fill="{NAVY}"/><circle cx="744" cy="87" r="2.2" fill="{NAVY}"/>'
        f'<path d="M729 95 Q735 99 741 95" stroke="{NAVY}" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
        '</g>'
    )

def logo(dark):
    fill = CREAM if dark else NAVY
    body = (zyo(fill, fill)
            + f'<g fill="{fill}">{glyph("報", 290, 200, 180)}{glyph("屋", 470, 200, 180)}</g>'
            + detective(dark))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="44 28 724 224" role="img" aria-label="情報屋">'
            f'<g transform="translate(-40 0)">{body}</g></svg>')

def icon():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 260" role="img" aria-label="情報屋">'
            f'<rect width="260" height="260" rx="56" fill="{NAVY}"/>'
            '<g transform="translate(130 130) scale(0.85) translate(-190 -131)">'
            + zyo(CREAM, CREAM) + '</g></svg>')

def write(name, s):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(s)

write("logo.svg", logo(False))
write("logo-dark.svg", logo(True))
write("icon.svg", icon())
write("favicon.svg", icon())
print("OK", os.path.abspath(OUT))
