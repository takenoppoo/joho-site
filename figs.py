# -*- coding: utf-8 -*-
"""解説に入れる図（SVG）を作る。data/wNN/kakunin.json の各問題に
  "fig": {"type": "venn", ...}
と書くと、build.py がこのファイルの fig_○○ を呼んで、Webの解説とPDFの解説に図を入れる。
種類: venn / switching / bitop / ipsplit / doubling / matrix / boxplot / pdca /
      sampling / scatter / array / line / hist / binary
"""
import html, math

FONT = "'Hiragino Sans','Noto Sans JP','Noto Sans CJK JP','Yu Gothic',Meiryo,sans-serif"
NAVY, OR, BL, GR, RD, GY, LT, LINE, CR = "#14284B", "#F28C28", "#4A78C8", "#2E7D5B", "#c0283c", "#5A6478", "#EEF3FC", "#D9D2C0", "#FBF7EE"
ORL = "#FDE7CC"


def esc(s):
    return html.escape(str(s))


def svg(w, h, label, inner):
    defs = (f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{NAVY}"/></marker></defs>')
    return (f'<svg class="fig" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="{esc(label)}" font-family="{esc(FONT)}">{defs}{inner}</svg>')


def T(x, y, s, size=16, fill=NAVY, anchor="middle", weight="400"):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>'


def R(x, y, w, h, fill="#fff", stroke=NAVY, sw=2, rx=6, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def L(x1, y1, x2, y2, stroke=NAVY, sw=2, arrow=False, dash=""):
    a = ' marker-end="url(#ar)"' if arrow else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linecap="round"{a}{d}/>')


def C(x, y, r, fill="#fff", stroke=NAVY, sw=2, op=1):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"/>'


# ---------- ベン図 ----------
def fig_venn(s):
    total, a, b, none = s["total"], s["a"], s["b"], s["none"]
    either = total - none
    both = s.get("both", a + b - either)
    la, lb = s.get("la", "A"), s.get("lb", "B")
    o = R(10, 10, 580, 282, fill="#fff", stroke=GY, sw=2, rx=10)
    o += T(24, 34, f"全体 {total}人", 15, GY, "start", "700")
    o += T(576, 280, f"どちらにも入っていない {none}人", 15, GY, "end", "700")
    o += C(235, 166, 80, BL, BL, 2, .25) + C(365, 166, 80, OR, OR, 2, .25)
    o += T(190, 76, f"{la} {a}人", 15, BL, "middle", "700") + T(410, 76, f"{lb} {b}人", 15, OR, "middle", "700")
    o += T(185, 172, f"{a - both}人", 22) + T(300, 172, f"{both}人", 26, RD, "middle", "700") + T(415, 172, f"{b - both}人", 22)
    o += T(300, 202, "重なり", 13, RD) + T(185, 196, f"{la}だけ", 13, GY) + T(415, 196, f"{lb}だけ", 13, GY)
    o += T(300, 36, f"少なくとも1つ＝{total}−{none}＝{either}人", 14, GY)
    return svg(600, 302, f"ベン図。{la}{a}人と{lb}{b}人の重なりは{both}人", o)


# ---------- 回線交換とパケット交換 ----------
def fig_switching(s):
    hl = s.get("hl", "")
    o = ""
    if hl == "circle":
        o += R(6, 6, 292, 238, ORL, OR, 2, 10, "6 4")
    if hl == "packet":
        o += R(302, 6, 292, 238, ORL, OR, 2, 10, "6 4")
    # 左：回線交換
    o += T(152, 32, "回線交換方式", 17, NAVY, "middle", "700")
    o += C(40, 90, 17, "#fff", NAVY) + T(40, 96, "A", 16) + C(260, 90, 17, "#fff", NAVY) + T(260, 96, "B", 16)
    o += L(57, 90, 243, 90, OR, 9)
    o += T(152, 78, "A〜Bが通話中", 13, OR, "middle", "700")
    o += C(40, 168, 17, "#fff", GY) + T(40, 174, "C", 16, GY)
    o += L(57, 168, 130, 110, GY, 2, False, "5 4") + T(118, 146, "✕", 24, RD, "middle", "700") + T(160, 172, "話し中", 15, RD, "start", "700")
    o += T(152, 215, "通話の間、回線を貸し切る", 14, GY)
    # 右：パケット交換
    o += T(448, 32, "パケット交換方式", 17, NAVY, "middle", "700")
    o += C(336, 90, 17, "#fff", NAVY) + T(336, 96, "A", 16) + C(556, 90, 17, "#fff", NAVY) + T(556, 96, "B", 16)
    o += L(353, 90, 539, 90, "#B7BECC", 9)
    for i, col in enumerate([OR, BL, OR, BL, OR, BL]):
        x = 366 + i * 28
        o += R(x, 79, 22, 22, col, col, 1, 4) + T(x + 11, 95, str(i // 2 + 1), 13, "#fff", "middle", "700")
    o += C(336, 168, 17, "#fff", BL, 2) + T(336, 174, "C", 16, BL)
    o += L(353, 160, 420, 106, BL, 2, True)
    o += T(448, 215, "小さく分けて、回線を共用する", 14, GY)
    return svg(600, 250, "回線交換は回線を貸し切る。パケット交換は小さく分けて回線を共用する", o)


# ---------- ビットごとの論理演算 ----------
def fig_bitop(s):
    op, a, b = s["op"], s["a"], s["b"]
    f = {"AND": lambda x, y: x & y, "OR": lambda x, y: x | y, "XOR": lambda x, y: x ^ y}[op]
    r = "".join(str(f(int(x), int(y))) for x, y in zip(a, b))
    n = len(a)
    cw = min(70, 360 // n)
    x0 = 300 - cw * n / 2
    o = T(x0 - 14, 56, "A", 20, NAVY, "end", "700") + T(x0 - 14, 116, "B", 20, NAVY, "end", "700")
    o += T(x0 - 14, 196, f"{op}", 17, OR, "end", "700")
    o += L(x0 - 60, 140, x0 + cw * n + 10, 140, NAVY, 3)
    for i in range(n):
        x = x0 + i * cw
        o += R(x + 4, 28, cw - 8, 40, "#fff", NAVY) + T(x + cw / 2, 58, a[i], 24)
        o += R(x + 4, 88, cw - 8, 40, "#fff", NAVY) + T(x + cw / 2, 118, b[i], 24)
        hot = r[i] == "1"
        o += R(x + 4, 168, cw - 8, 40, ORL if hot else "#fff", OR if hot else NAVY) + T(x + cw / 2, 198, r[i], 24, RD if hot else NAVY, "middle", "700")
        o += T(x + cw / 2, 236, f"{a[i]}と{b[i]}→{r[i]}", 13, GY)
    rule = {"AND": "両方が1のときだけ1", "OR": "どちらかが1なら1", "XOR": "違うときだけ1"}[op]
    o += T(300, 262, f"{op}：{rule}　答え {r}", 14, NAVY, "middle", "700")
    return svg(600, 272, f"{a}と{b}のビットごとの{op}は{r}", o)


# ---------- IPアドレスのビット ----------
def fig_ipsplit(s):
    net = s["net"]
    host = 32 - net
    cw, gap = 16, 6
    x0 = 35
    def xpos(i):
        return x0 + i * cw + (i // 8) * gap
    o = ""
    for i in range(32):
        col = BL if i < net else OR
        o += R(xpos(i), 70, cw - 1.5, 30, col, "#fff", 1, 3)
    nx0, nx1 = xpos(0), xpos(net - 1) + cw
    hx0, hx1 = xpos(net), xpos(31) + cw
    o += L(nx0, 56, nx1 - 3, 56, BL, 3) + T((nx0 + nx1) / 2, 44, f"ネットワーク部 {net}ビット", 15, BL, "middle", "700")
    o += L(hx0, 56, hx1 - 3, 56, OR, 3)
    o += T(hx1 - 3, 44, f"ホスト部 {host}ビット", 15, OR, "end", "700")
    o += T(300, 22, "IPv4アドレス＝全部で32ビット", 14, GY)
    n = 2 ** host
    o += T(300, 140, f"ホスト部 {host}ビット → 2の{host}乗 ＝ {n}通り", 17, NAVY, "middle", "700")
    o += R(60, 160, 480, 40, CR, LINE, 1.5, 8) + T(300, 187, "全部0（ネットワークアドレス）と全部1（管理用）は使えない", 14, GY)
    o += T(300, 232, f"{n} − 2 ＝ {n - 2}台", 24, RD, "middle", "700")
    return svg(600, 246, f"IPアドレスの{net}ビットがネットワーク部、{host}ビットがホスト部。割り当てられる台数は{n - 2}台", o)


# ---------- 階調（2倍ずつ） ----------
def fig_doubling(s):
    bits = s["bits"]
    w, gap = 84, 34
    x0 = (600 - (bits * w + (bits - 1) * gap)) / 2
    o = ""
    for i in range(bits):
        x = x0 + i * (w + gap)
        last = i == bits - 1
        o += R(x, 36, w, 76, ORL if last else LT, OR if last else BL, 2, 8)
        o += T(x + w / 2, 64, f"{i + 1}ビット", 15, GY) + T(x + w / 2, 98, f"{2 ** (i + 1)}通り", 20, RD if last else NAVY, "middle", "700")
        if i < bits - 1:
            o += L(x + w + 3, 74, x + w + gap - 4, 74, NAVY, 2, True) + T(x + w + gap / 2, 62, "×2", 13, GY)
    o += T(300, 158, "＝ " + "×".join(["2"] * bits) + f" ＝ {2 ** bits}階調", 20, NAVY, "middle", "700")
    o += T(300, 192, "1ビット増えるごとに、表せる段階が2倍になる", 14, GY)
    return svg(600, 206, f"{bits}ビットで表せる階調は{2 ** bits}段階", o)


# ---------- マトリクス図 ----------
def fig_matrix(s):
    xs, ys = s["x"], s["y"]
    x0, y0, cw, ch = 140, 56, 210, 78
    o = ""
    for j, xl in enumerate(xs):
        o += T(x0 + cw * j + cw / 2, 46, xl, 16, NAVY, "middle", "700")
    for i, yl in enumerate(ys):
        o += T(x0 - 12, y0 + ch * i + ch / 2 + 6, yl, 15, NAVY, "end", "700")
        for j, xl in enumerate(xs):
            o += R(x0 + cw * j, y0 + ch * i, cw, ch, LT if (i + j) % 2 == 0 else "#fff", BL, 2, 0)
            o += T(x0 + cw * j + cw / 2, y0 + ch * i + ch / 2 - 2, xl, 14) + T(x0 + cw * j + cw / 2, y0 + ch * i + ch / 2 + 18, yl, 14)
    o += T(300, y0 + ch * 2 + 26, "2つの基準 → 縦と横の軸 → 4つの区分", 14, GY)
    return svg(600, y0 + ch * 2 + 40, "縦と横の十字で、2つの基準を組み合わせて4つの区分に分けるマトリクス図", o)


# ---------- 箱ひげ図 ----------
def _med(v):
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def fig_boxplot(s):
    d = sorted(s["data"])
    n = len(d)
    q2 = _med(d)
    q1, q3 = _med(d[: n // 2]), _med(d[(n + 1) // 2:])
    lo, hi = d[0], d[-1]
    a0, a1 = lo - 2, hi + 2
    sx = lambda v: 40 + (v - a0) / (a1 - a0) * 520
    fmt = lambda v: str(int(v)) if float(v).is_integer() else f"{v:g}"
    o = L(36, 160, 564, 160, GY, 2)
    for v in d:
        o += C(sx(v), 160, 4.5, NAVY, NAVY) + T(sx(v), 182, fmt(v), 13, GY)
    o += L(sx(lo), 100, sx(q1), 100, NAVY, 2.5) + L(sx(q3), 100, sx(hi), 100, NAVY, 2.5)
    o += L(sx(lo), 88, sx(lo), 112, NAVY, 2.5) + L(sx(hi), 88, sx(hi), 112, NAVY, 2.5)
    o += R(sx(q1), 78, sx(q3) - sx(q1), 44, LT, BL, 2.5, 0) + L(sx(q2), 78, sx(q2), 122, RD, 3.5)
    for v, name, col in ((lo, "最小値", NAVY), (q1, "第1四分位数", BL), (q2, "中央値", RD), (q3, "第3四分位数", BL), (hi, "最大値", NAVY)):
        o += T(sx(v), 52, name, 12.5, col, "middle", "700") + T(sx(v), 70, fmt(v), 15, col, "middle", "700")
    o += L(sx(q1), 210, sx(q3), 210, OR, 2.5) + L(sx(q1), 202, sx(q1), 218, OR, 2.5) + L(sx(q3), 202, sx(q3), 218, OR, 2.5)
    o += T((sx(q1) + sx(q3)) / 2, 238, f"四分位範囲 ＝ {fmt(q3)} − {fmt(q1)} ＝ {fmt(q3 - q1)}", 16, OR, "middle", "700")
    return svg(600, 252, f"箱ひげ図。第1四分位数{fmt(q1)}、中央値{fmt(q2)}、第3四分位数{fmt(q3)}、四分位範囲{fmt(q3 - q1)}", o)


# ---------- PDCA ----------
def fig_pdca(s):
    hl = s.get("hl", "")
    notes = s.get("notes", {})
    items = {"P": ("Plan 計画", 215, 6), "D": ("Do 実行", 400, 100), "C": ("Check 評価", 215, 194), "A": ("Action 改善", 30, 100)}
    o = ""
    for k, (lab, x, y) in items.items():
        hot = k == hl
        o += R(x, y, 170, 58, ORL if hot else LT, OR if hot else BL, 2.5, 10)
        o += T(x + 85, y + (24 if k in notes else 36), lab, 17, RD if hot else NAVY, "middle", "700")
        if k in notes:
            o += T(x + 85, y + 45, notes[k], 12.5, GY)
    o += L(385, 35, 475, 98, NAVY, 2.5, True) + L(485, 160, 385, 222, NAVY, 2.5, True)
    o += L(215, 223, 125, 162, NAVY, 2.5, True) + L(115, 98, 215, 36, NAVY, 2.5, True)
    o += T(300, 128, "くり返す", 14, GY) + T(300, 148, "↻", 22, GY)
    return svg(600, 262, "PDCAサイクル。計画、実行、評価、改善をくり返す", o)


# ---------- 標本化・量子化 ----------
def _wave(t):
    return 0.62 * math.sin(2 * math.pi * t) + 0.28 * math.sin(4 * math.pi * t + 1.0)


def fig_sampling(s):
    kind = s["kind"]
    o = ""
    for p, (px, title, n) in enumerate(((10, "少ない" if kind == "sample" else "段階が少ない", 6), (305, "多い" if kind == "sample" else "段階が多い", 24))):
        w, h, oy = 280, 150, 60
        o += R(px, 40, w, 180, "#fff", LINE, 1.5, 8)
        o += T(px + w / 2, 30, ("取り出す回数が" if kind == "sample" else "") + title + ("" if kind == "sample" else "（イメージ）"), 15, NAVY, "middle", "700")
        mx = lambda t: px + 14 + t * (w - 28)
        my = lambda v: oy + h / 2 - v * (h / 2 - 8) / 0.95
        o += L(px + 10, my(0), px + w - 10, my(0), "#C9CED8", 1)
        pts = " ".join(f"{mx(i / 120):.1f},{my(_wave(i / 120)):.1f}" for i in range(121))
        o += f'<polyline points="{pts}" fill="none" stroke="#B7BECC" stroke-width="2"/>'
        if kind == "sample":
            m = 6 if p == 0 else 16
            ts = [i / (m - 1) for i in range(m)]
            for t in ts:
                o += L(mx(t), my(0), mx(t), my(_wave(t)), BL, 1.2, False, "3 3") + C(mx(t), my(_wave(t)), 3.8, OR, OR, 1)
            o += f'<polyline points="{" ".join(f"{mx(t):.1f},{my(_wave(t)):.1f}" for t in ts)}" fill="none" stroke="{OR}" stroke-width="2"/>'
        else:
            lv = 6 if p == 0 else 24
            levels = [-0.95 + 1.9 * k / (lv - 1) for k in range(lv)]
            for v in levels:
                o += L(px + 10, my(v), px + w - 10, my(v), "#E3E6EC", 0.8)
            step = []
            m = 30
            for i in range(m):
                t0, t1 = i / m, (i + 1) / m
                v = min(levels, key=lambda z: abs(z - _wave((t0 + t1) / 2)))
                step.append(f"{mx(t0):.1f},{my(v):.1f} {mx(t1):.1f},{my(v):.1f}")
            o += f'<polyline points="{" ".join(step)}" fill="none" stroke="{OR}" stroke-width="2.4"/>'
        o += T(px + w / 2, 236, ("回数が少ない → 粗い記録" if kind == "sample" else "段階が少ない → 粗い記録") if p == 0 else ("回数が多い → 細かい記録" if kind == "sample" else "段階が多い → 細かい記録"), 13.5, GY)
    o += T(300, 254, "灰色＝元の音（連続）　橙＝記録した値" + ("" if kind == "sample" else "　※段階の数は絵のイメージです"), 12.5, GY)
    return svg(600, 264, "標本化と量子化の図。回数や段階が多いほど元の音に近い記録になる" if kind == "quant" else "標本化の図。取り出す回数が多いほど元の音に近い記録になる", o)


# ---------- 散布図 ----------
_JIT = [0.6, -0.9, 0.4, 1.0, -0.5, -0.7, 0.8, -0.3, 0.5, -0.8, 0.7, -0.4, 0.2, -0.1]


def fig_scatter(s):
    up = s.get("dir", "up") == "up"
    xl, yl = s.get("xl", "x"), s.get("yl", "y")
    x0, x1, y0, y1 = 80, 560, 28, 196
    o = L(x0, y1, x1 + 6, y1, NAVY, 2, True) + L(x0, y1, x0, y0 - 8, NAVY, 2, True)
    o += T((x0 + x1) / 2, 224, xl, 15, GY, "middle", "700") + T(40, (y0 + y1) / 2, yl, 15, GY, "middle", "700")
    n = len(_JIT)
    for i, j in enumerate(_JIT):
        t = i / (n - 1)
        v = (t if up else 1 - t) + j * 0.07
        v = min(max(v, 0.04), 0.96)
        o += C(x0 + 24 + t * (x1 - x0 - 48), y1 - 14 - v * (y1 - y0 - 28), 5.5, BL, "#fff", 1.5, .9)
    if up:
        o += L(x0 + 40, y1 - 28, x1 - 40, y0 + 12, OR, 3, True, "7 5")
    else:
        o += L(x0 + 40, y0 + 12, x1 - 40, y1 - 28, OR, 3, True, "7 5")
    o += T((x0 + x1) / 2, 18, s.get("note", ""), 15, RD, "middle", "700")
    return svg(600, 234, f"散布図。{s.get('note', '')}", o)


# ---------- 配列と添字 ----------
def fig_array(s):
    v, mk, name = s["values"], s.get("mark", -1), s.get("name", "A")
    n = len(v)
    w = 86
    x0 = 300 - n * w / 2 + 40
    o = T(x0 - 14, 62, "添字", 15, GY, "end", "700") + T(x0 - 14, 110, "値", 15, GY, "end", "700")
    for i, a in enumerate(v):
        x = x0 + i * w
        hot = i == mk
        o += T(x + w / 2 - 2, 64, str(i), 18, RD if hot else NAVY, "middle", "700")
        o += R(x, 78, w - 4, 50, ORL if hot else LT, OR if hot else BL, 2.5, 4) + T(x + w / 2 - 2, 112, str(a), 24, RD if hot else NAVY, "middle", "700")
        o += T(x + w / 2 - 2, 148, f"{name}[{i}]", 13, GY)
    o += T(300, 188, "添字は 0 から数える", 14, GY)
    if mk >= 0:
        o += T(300, 218, f"{name}[{mk}] ＝ {v[mk]}（{mk + 1}番目の要素）", 18, RD, "middle", "700")
    return svg(600, 232, f"配列{name}と添字。{name}[{mk}]は{v[mk] if mk >= 0 else ''}", o)


# ---------- 回帰直線 ----------
def fig_line(s):
    a, b, x = s["a"], s["b"], s["x"]
    xmax = x + 2
    ymax = int(math.ceil((a * xmax + b) / 10.0) * 10)
    px0, px1, py0, py1 = 70, 540, 190, 26
    sx = lambda v: px0 + v / xmax * (px1 - px0)
    sy = lambda v: py0 - v / ymax * (py0 - py1)
    o = L(px0, py0, px1 + 8, py0, NAVY, 2, True) + L(px0, py0, px0, py1 - 10, NAVY, 2, True)
    for xv in range(0, xmax + 1, 2):
        o += L(sx(xv), py0, sx(xv), py0 + 5, NAVY, 1.5) + T(sx(xv), py0 + 22, str(xv), 13, GY)
    for yv in range(0, ymax + 1, 10):
        o += L(px0 - 5, sy(yv), px0, sy(yv), NAVY, 1.5) + T(px0 - 10, sy(yv) + 5, str(yv), 13, GY, "end")
    o += L(sx(0), sy(b), sx(xmax), sy(a * xmax + b), BL, 3)
    o += T(sx(xmax) - 6, sy(a * xmax + b) - 12, f"y ＝ {a}x ＋ {b}", 15, BL, "end", "700")
    yv = a * x + b
    o += L(sx(x), py0, sx(x), sy(yv), OR, 1.8, False, "5 4") + L(px0, sy(yv), sx(x), sy(yv), OR, 1.8, False, "5 4")
    o += C(sx(x), sy(yv), 6.5, RD, "#fff", 2) + T(sx(x) + 12, sy(yv) + 24, f"x＝{x} → y＝{yv}", 15, RD, "start", "700")
    o += T(px1, py0 + 38, "x（勉強時間）", 13, GY, "end") + T(px0 + 6, py1 - 12, "y（得点）", 13, GY, "start")
    o += T(300, 244, f"y ＝ {a}×{x} ＋ {b} ＝ {a * x} ＋ {b} ＝ {yv}", 17, NAVY, "middle", "700")
    return svg(600, 258, f"回帰直線y={a}x+{b}。x={x}のときyは{yv}", o)


# ---------- ヒストグラム ----------
def fig_hist(s):
    hs = [1, 3, 7, 4, 2, 2, 5, 8, 4, 1]
    n = len(hs)
    x0, w = 70, 46
    base, top = 190, 40
    o = L(x0 - 6, base, x0 + n * w + 8, base, NAVY, 2, True) + L(x0 - 6, base, x0 - 6, top - 12, NAVY, 2, True)
    for i, hgt in enumerate(hs):
        hh = hgt / 8 * (base - top)
        hot = i in (2, 7)
        o += R(x0 + i * w, base - hh, w - 3, hh, ORL if hot else LT, OR if hot else BL, 2, 0)
        o += T(x0 + i * w + w / 2 - 1, base + 18, f"{i * 10}〜", 11.5, GY)
    o += T(x0 + n * w + 10, base + 4, "得点（点）", 13, GY, "start") + T(x0 - 6, top - 22, "人数", 13, GY, "middle")
    o += T(x0 + 2.5 * w, 46, "山①", 16, RD, "middle", "700") + T(x0 + 7.5 * w, 28, "山②", 16, RD, "middle", "700")
    o += T(300, 236, "山が2つ ＝ 人が集まる所が2か所 ＝ 2つのグループ", 15, NAVY, "middle", "700")
    return svg(600, 250, "ヒストグラム。山が2つあり、得点の高いグループと低いグループがある", o)


# ---------- 2進法の位 ----------
def fig_binary(s):
    v, bits = s["value"], s["bits"]
    digs = format(v, f"0{bits}b")
    w = 110
    x0 = 300 - bits * w / 2
    o = ""
    terms = []
    for i, d in enumerate(digs):
        p = bits - 1 - i
        x = x0 + i * w
        hot = d == "1"
        o += T(x + w / 2 - 2, 38, f"{2 ** p}の位", 15, GY) + T(x + w / 2 - 2, 56, f"（2の{p}乗）", 11.5, GY)
        o += R(x, 66, w - 6, 56, ORL if hot else "#fff", OR if hot else NAVY, 2.5, 6) + T(x + w / 2 - 3, 106, d, 30, RD if hot else NAVY, "middle", "700")
        terms.append(f"{2 ** p}×{d}")
    o += T(300, 158, " ＋ ".join(terms) + f" ＝ {v}", 17, NAVY, "middle", "700")
    o += T(300, 190, f"{2 ** bits}階調 ＝ 2の{bits}乗 → {bits}桁あれば表せる　答え：{digs}", 14, GY)
    return svg(600, 204, f"{v}を2進法で{bits}桁で表すと{digs}", o)


def render(spec):
    """data の "fig" 仕様 → SVG文字列"""
    return globals()["fig_" + spec["type"]](spec)
