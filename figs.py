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
    for (px_, py_) in s.get("points", []):
        o += C(sx(px_), sy(py_), 3.6, BL, "#fff", 1, .85)
    o += L(sx(0), sy(b), sx(xmax), sy(a * xmax + b), OR if s.get("points") else BL, 3)
    o += T(sx(xmax) - 6, sy(a * xmax + b) - 12, f"y ＝ {a}x ＋ {b}", 15, BL, "end", "700")
    yv = a * x + b
    o += L(sx(x), py0, sx(x), sy(yv), OR, 1.8, False, "5 4") + L(px0, sy(yv), sx(x), sy(yv), OR, 1.8, False, "5 4")
    o += C(sx(x), sy(yv), 6.5, RD, "#fff", 2) + T(sx(x) + 12, sy(yv) + 24, f"x＝{x} → y＝{yv}", 15, RD, "start", "700")
    o += T(px1, py0 + 38, "x（勉強時間）", 13, GY, "end") + T(px0 + 6, py1 - 12, "y（得点）", 13, GY, "start")
    o += T(300, 244, f"y ＝ {a}×{x} ＋ {b} ＝ {a * x} ＋ {b} ＝ {yv}", 17, NAVY, "middle", "700")
    return svg(600, 258, f"回帰直線y={a}x+{b}。x={x}のときyは{yv}", o)


# ---------- ヒストグラム ----------
def fig_hist(s):
    hs = s.get("values", [1, 3, 7, 4, 2, 2, 5, 8, 4, 1])
    start, step = s.get("start", 0), s.get("step", 10)
    peaks = s.get("peaks", [2, 7] if "values" not in s else [])
    n = len(hs)
    w = min(46, 440 // n)
    x0 = 70
    base, top = 190, 40
    ymax = max(hs)
    ymax = ymax if ymax % 5 == 0 else (ymax // 5 + 1) * 5
    o = L(x0 - 6, base, x0 + n * w + 8, base, NAVY, 2, True) + L(x0 - 6, base, x0 - 6, top - 12, NAVY, 2, True)
    for yv in range(0, ymax + 1, 5):
        yy = base - yv / ymax * (base - top)
        o += L(x0 - 10, yy, x0 - 6, yy, NAVY, 1.5) + T(x0 - 14, yy + 5, str(yv), 12, GY, "end")
    for i, hgt in enumerate(hs):
        hh = hgt / ymax * (base - top)
        hot = i in peaks
        o += R(x0 + i * w, base - hh, w - 2, hh, ORL if hot else LT, OR if hot else BL, 2, 0)
        o += T(x0 + i * w + w / 2 - 1, base + 18, f"{start + i * step}〜", 11.5, GY)
    o += T(x0 + n * w + 10, base + 4, f"{s.get('xl', '得点')}（点）", 13, GY, "start") + T(x0 - 6, top - 22, "人数", 13, GY, "middle")
    for k, pi in enumerate(peaks):
        hh = hs[pi] / ymax * (base - top)
        o += T(x0 + pi * w + w / 2, base - hh - 8, f"山{'①②③'[k]}", 16, RD, "middle", "700")
    cap = s.get("caption", "山が2つ ＝ 人が集まる所が2か所 ＝ 2つのグループ" if peaks else "")
    if cap:
        o += T(300, 236, cap, 15, NAVY, "middle", "700")
    return svg(600, 250, "ヒストグラム" + ("。山が2つあり、得点の高いグループと低いグループがある" if len(peaks) == 2 else ""), o)


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


# ---------- デジタル化の3ステップ ----------
def fig_digitize(s):
    f = lambda t: 3.1 + 2.3 * math.sin(2 * math.pi * t + 1.0)
    o = ""
    for px, title in ((10, "① 標本化：一定間隔で取り出す"), (205, "② 量子化：整数に丸める"), (400, "③ 符号化：0と1にする")):
        o += T(px + 90, 20, title, 13.5, NAVY, "middle", "700")
    for px in (10, 205):
        o += R(px, 32, 180, 170, "#fff", GY, 1.5, 0)
    mx = lambda px, t: px + 8 + t * 164
    my = lambda v: 196 - v / 6.4 * 158
    for px in (10, 205):
        pts = " ".join(f"{mx(px, i / 100):.1f},{my(f(i / 100)):.1f}" for i in range(101))
        o += f'<polyline points="{pts}" fill="none" stroke="#B7BECC" stroke-width="2"/>'
    ts = [i / 11 for i in range(12)]
    for t in ts:
        o += L(mx(10, t), 196, mx(10, t), my(f(t)), BL, 1.6) + C(mx(10, t), my(f(t)), 4, BL, BL, 1)
    q = [round(f(t)) for t in ts]
    step = []
    for i, t in enumerate(ts):
        step.append(f"{mx(205, t) - 7:.1f},{my(q[i]):.1f} {mx(205, t) + 7:.1f},{my(q[i]):.1f}")
        o += C(mx(205, t), my(q[i]), 3.6, OR, OR, 1)
    o += f'<polyline points="{" ".join(step)}" fill="none" stroke="{OR}" stroke-width="2"/>'
    for v in range(0, 7):
        o += T(203, my(v) + 4, str(v), 10.5, GY, "end")
    for k, (a, b) in enumerate(((3, "011"), (5, "101"), (2, "010"), (4, "100"))):
        o += T(430, 70 + k * 36, f"{a} → {b}", 18, BL, "start", "700")
    return svg(600, 214, "デジタル化の3ステップ。標本化で取り出し、量子化で整数にし、符号化で0と1にする", o)


# ---------- 散布図3つ（正・負・なし） ----------
def _lcg(seed):
    x = seed
    while True:
        x = (x * 1103515245 + 12345) % 2147483648
        yield x / 2147483648


def fig_scatter3(s):
    o = ""
    rnd = _lcg(7)
    kinds = (("正の相関（r＝約＋0.9）", "pos"), ("負の相関（r＝約−0.9）", "neg"), ("相関なし（r＝約0）", "none"))
    for k, (title, kind) in enumerate(kinds):
        px = 8 + k * 198
        o += T(px + 94, 20, title, 13.5, NAVY, "middle", "700") + R(px, 30, 188, 170, "#fff", GY, 1.5, 0)
        for i in range(26):
            t = i / 25
            if kind == "none":
                x, y = next(rnd), next(rnd)
            else:
                v = t + (next(rnd) - .5) * 0.18
                x, y = t, (v if kind == "pos" else 1 - v)
            x, y = min(max(x, .03), .97), min(max(y, .03), .97)
            o += C(px + 8 + x * 172, 192 - y * 152, 3.6, BL, BL, 1, .9)
    return svg(600, 212, "散布図。正の相関、負の相関、相関なしの3つ", o)


# ---------- 回帰直線つきの散布図2つ（決勝進出／予選敗退） ----------
def fig_regpair(s):
    o = ""
    for k, p in enumerate(s["panels"]):
        px = 4 + k * 298
        x0, x1, y0, y1 = px + 52, px + 280, 40, 190
        xmin, xmax, ymax = p["xmin"], p["xmax"], p.get("ymax", 2.5)
        sx = lambda v: x0 + (v - xmin) / (xmax - xmin) * (x1 - x0)
        sy = lambda v: y1 - v / ymax * (y1 - y0)
        o += T((x0 + x1) / 2, 18, p["title"], 14.5, NAVY, "middle", "700")
        o += R(x0, y0, x1 - x0, y1 - y0, "#fff", GY, 1.5, 0)
        for yv in (0, 0.5, 1.0, 1.5, 2.0, 2.5):
            o += L(x0, sy(yv), x1, sy(yv), "#E3E6EC", 1) + T(x0 - 6, sy(yv) + 4, f"{yv:.1f}", 11, GY, "end")
        for xv in p["xticks"]:
            o += L(sx(xv), y0, sx(xv), y1, "#E3E6EC", 1) + T(sx(xv), y1 + 15, str(xv), 11, GY)
        for (xx, yy) in p["points"]:
            o += C(sx(xx), sy(yy), 3.8, "#222", "#222", 1)
        a, b = p["a"], p["b"]
        o += L(sx(p["lx0"]), sy(a * p["lx0"] + b), sx(p["lx1"]), sy(a * p["lx1"] + b), "#111", 2.2, False, "2 3")
        o += T(x0 + 8, y0 + 18, p["eq"], 12.5, "#111", "start")
        o += T((x0 + x1) / 2, y1 + 32, "1試合当たりのパス成功数（本）", 11.5, GY)
        if k == 0:
            o += T(px + 9, (y0 + y1) / 2, "得点", 12, GY, "middle")
    return svg(600, 232, "パス成功数と得点の散布図と回帰直線（決勝進出チームと予選敗退チーム）", o)


# ---------- 選択肢に使う小さな図（ウ〜オの解答群など） ----------
def fig_choice(s):
    n = s["name"]
    D, M, Lg = "#444", "#999", "#ccc"
    o = ""
    if n == "cycle":
        for (cx, cy, c) in ((100, 32, D), (160, 78, M), (100, 124, Lg), (40, 78, M)):
            o += C(cx, cy, 22, c, c, 0)
        o += L(118, 40, 140, 58, D, 2, True) + L(146, 98, 124, 112, D, 2, True) + L(80, 118, 58, 98, D, 2, True) + L(54, 58, 80, 40, D, 2, True)
    elif n == "tree":
        o += R(72, 10, 56, 24, D, D, 0, 0) + L(100, 34, 100, 54, D, 3) + L(40, 54, 160, 54, D, 3)
        for cx in (40, 100, 160):
            o += L(cx, 54, cx, 72, D, 3) + R(cx - 22, 72, 44, 40, M, M, 0, 0)
    elif n == "venn3":
        o += C(82, 62, 46, "#bbb", "#999", 1.5, .55) + C(122, 62, 46, "#888", "#777", 1.5, .45) + C(102, 98, 46, "#444", "#333", 1.5, .55)
    elif n == "pyramid":
        o += f'<polygon points="100,8 118,38 82,38" fill="{D}"/>'
        rows = [(38, 62, 118, 82), (62, 86, 135, 65), (86, 110, 152, 48), (110, 134, 168, 32)]
        for k, (ya, yb, xr, xl) in enumerate(rows):
            wa = 18 + k * 17
            wb = 18 + (k + 1) * 17
            o += f'<polygon points="{100 - wa},{ya} {100 + wa},{ya} {100 + wb},{yb} {100 - wb},{yb}" fill="{[M, Lg, M, Lg][k]}" stroke="#fff" stroke-width="1.5"/>'
    elif n == "matrix":
        o += R(50, 14, 48, 54, D, D, 0, 4) + R(104, 14, 48, 54, M, M, 0, 4) + R(50, 74, 48, 54, Lg, Lg, 0, 4) + R(104, 74, 48, 54, Lg, Lg, 0, 4)
        o += L(101, 140, 101, 8, D, 1.8, True) + L(20, 71, 182, 71, D, 1.8, True)
    elif n == "radial":
        o += L(100, 70, 100, 30, D, 3) + L(100, 70, 62, 100, D, 3) + L(100, 70, 138, 100, D, 3)
        o += C(100, 30, 20, Lg, Lg, 0) + C(60, 104, 20, Lg, Lg, 0) + C(140, 104, 20, Lg, Lg, 0) + C(100, 72, 24, D, D, 0)
    return svg(200, 146, "図：" + n, o)


def render(spec):
    """data の "fig" 仕様 → SVG文字列"""
    return globals()["fig_" + spec["type"]](spec)
