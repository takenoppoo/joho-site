# -*- coding: utf-8 -*-
"""情報屋：静的サイト生成スクリプト。
下の CONFIG を書き換えて `python3 build.py` を実行すると、docs/ の HTML・データ・sitemap が作り直される。
週ごとの教材は data/w01/ w02/ … に置く（weeks.py の説明を見る）。docs/wN/ に週ごとのページができる。
（docs/style.css・docs/app.js・docs/assets・docs/wN/pdf・docs/wN/img は手で置いたものなので上書きしない）
"""
import json, os, html
from datetime import date
from weeks import load_areas, load_weeks, with_figs, with_shikou_figs
import figs

# ============ CONFIG（ここだけ書き換える） ============
SITE_NAME = "情報屋"
SITE_URL = "https://takenoppoo.github.io/joho-site"      # 公開URL（sitemap用）。末尾に / は付けない
EMAIL = "suugakuworakuni@gmail.com"                    # 連絡先メール（お問い合わせページに載る）
OWNER_TEXT = "共通テスト「情報Ⅰ」の対策サイトです。数学教師を目指して勉強している大学生が運営しています。"
ADS_ENABLED = False   # 広告（AdSense）を載せるときに True にして build.py を実行する → プライバシーポリシーの広告の文章が切り替わる
OUT = "docs"
# ====================================================

E = html.escape
ROOT = os.path.dirname(os.path.abspath(__file__))

AREAS = load_areas()
WEEKS = load_weeks()
AREA = {a["id"]: a for a in AREAS}

NAV = [("index.html", "ホーム"), ("syllabus.html", "分野（シラバス）"), ("howto.html", "使い方")]
ALL_PAGES = [h for h, _ in NAV] + ["about.html", "contact.html", "privacy.html"]

# 1週間の進め方（確認テスト3日分＋思考問題4日分＝7日）
PLAN = [("1日目", "単語帳（20語を1周）→ 確認テスト1日目"),
        ("2日目", "単語帳（赤字をかくして確認）→ 確認テスト2日目"),
        ("3日目", "確認テスト3日目 → まちがえた語を単語帳で復習"),
        ("4日目", "思考問題1日目"),
        ("5日目", "思考問題2日目"),
        ("6日目", "思考問題3日目"),
        ("7日目", "思考問題4日目 → まちがえた所をまとめて見直し")]


def plan_table():
    return ('<table class="w">' + "".join(f'<tr><td style="width:18%">{d}</td><td>{E(t)}</td></tr>' for d, t in PLAN)
            + "</table><p class=\"small\">自分のペースで、日数は増やしてかまいません。</p>")


def area_tag(a):
    return f'<span class="tag a{a}">{E(AREA[a]["short"])}</span>'


def page(fname, title, desc, body, active=None, scripts=(), base=""):
    """fname は docs からの相対パス。週のページ（w1/…）は base="../" にする"""
    full_title = SITE_NAME if fname == "index.html" else f"{title}｜{SITE_NAME}"
    nav = "".join(f'<a href="{base}{h}"{" class=on" if h == active else ""}>{n}</a>' for h, n in NAV)
    sc = "".join(f'<script src="{s}"></script>' for s in scripts)
    doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(full_title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="{base}favicon.ico" sizes="48x48">
<link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png">
<link rel="stylesheet" href="{base}style.css">
<!-- 広告（AdSense）承認後：ここに <script async src="https://pagead2.googlesyndication.com/..."></script> を貼る -->
</head>
<body>
<header class="site-h"><div class="wrap">
<a class="logo" href="{base}index.html"><img src="{base}assets/logo.svg" alt="{E(SITE_NAME)}" width="142" height="44"></a>
<nav>{nav}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site-f"><div class="wrap">
<p><a href="{base}howto.html">使い方</a>｜<a href="{base}about.html">このサイトについて</a>｜<a href="{base}contact.html">お問い合わせ</a>｜<a href="{base}privacy.html">プライバシーポリシー</a></p>
<p>© {E(SITE_NAME)}　掲載の問題・解説はオリジナルです。</p>
</div></footer>
{sc}
</body>
</html>
"""
    path = os.path.join(ROOT, OUT, fname)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


AD_TOP = "<!-- 広告枠（上）：AdSense承認後、ここに広告コードを貼る -->"
AD_BOTTOM = "<!-- 広告枠（下）：AdSense承認後、ここに広告コードを貼る -->"


def write_js(fname, var, obj):
    path = os.path.join(ROOT, OUT, fname)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"window.{var}=" + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";\n")


write_js("data-areas.js", "AREAS", AREAS)


def render_zu(sections):
    """単語帳の「図と表」（data/wNN/zu.json）をHTMLにする"""
    def table(t):
        h = ""
        if t.get("head"):
            h = "<thead><tr>" + "".join(f"<th>{E(c)}</th>" for c in t["head"]) + "</tr></thead>"
        rows = ""
        for r in t["rows"]:
            cells = "".join((f"<th>{E(c)}</th>" if (i == 0 and t.get("rowhead")) else f"<td>{E(c)}</td>") for i, c in enumerate(r))
            rows += f"<tr>{cells}</tr>"
        return f'<div class="tbwrap"><table class="tb">{h}<tbody>{rows}</tbody></table></div>'

    def item(it):
        if "table" in it:
            return table(it["table"])
        if "fig" in it:
            return f'<div class="figbox">{figs.render(it["fig"])}</div>'
        return f'<p>{E(it["p"])}</p>'

    html_, i = "", 0
    while i < len(sections):
        s = sections[i]
        if s.get("half"):
            group = []
            while i < len(sections) and sections[i].get("half"):
                group.append(sections[i])
                i += 1
            colnos = sorted({g.get("col", k) for k, g in enumerate(group)})
            html_ += '<div class="zu-row">' + "".join(
                "<div>" + "".join(f'<h3 class="zh">{E(g["h"])}</h3>' + "".join(item(x) for x in g["items"])
                                  for k, g in enumerate(group) if g.get("col", k) == c) + "</div>" for c in colnos) + "</div>"
            continue
        body = "".join(item(x) for x in s["items"])
        if s.get("cols") == 2:
            body = f'<div class="zu-cols">{body}</div>'
        html_ += f'<section class="zu-sec"><h3 class="zh">{E(s["h"])}</h3>{body}</section>'
        i += 1
    if not html_:
        return ""
    return '<h2 class="t">図と表</h2><p class="small">文字だけだと分かりにくい語を、図や表でまとめました。</p>' + html_


def weeknav(n, active):
    items = [("index.html", "まとめ"), ("tango.html", "単語帳"), ("kakunin.html", "確認テスト"), ("shikou.html", "思考問題")]
    return (f'<div class="wknav"><b>第{n}週</b>' +
            "".join(f'<a href="{h}"{" class=on" if h == active else ""}>{t}</a>' for h, t in items) + "</div>")


# ---------------- 週ごとのページ ----------------
for W in WEEKS:
    n, TANGO, KAKUNIN, SHIKOU = W["n"], W["tango"], W["kakunin"], W["shikou"]
    wd = f"w{n}"
    days = sorted({q["day"] for q in KAKUNIN})
    N_FIG = sum(1 for q in KAKUNIN if q.get("fig"))
    write_js(f"{wd}/data-kakunin.js", "KAKUNIN", with_figs(KAKUNIN))
    pdf = lambda name: os.path.exists(os.path.join(ROOT, OUT, wd, "pdf", name))

    # --- まとめ ---
    def pdf_links():
        links = []
        for f, label in (("tango.pdf", "単語帳"), ("kakunin-mondai.pdf", "確認テスト 問題"), ("kakunin-kaisetsu.pdf", "確認テスト 解答・解説"),
                         ("shikou-mondai.pdf", "思考問題 問題"), ("shikou-kaisetsu.pdf", "思考問題 解答・解説")):
            if pdf(f):
                links.append(f'<a href="pdf/{f}">{label}（PDF）</a>')
        return "<p>" + "｜".join(links) + "</p>" if links else ""

    page(f"{wd}/index.html", f"第{n}週", f"第{n}週：単語{len(TANGO)}語・確認テスト{len(KAKUNIN)}問・思考問題{len(SHIKOU)}日分。",
f"""{weeknav(n, "index.html")}
<h1>第{n}週</h1>
<p class="small">単語 {len(TANGO)}語・確認テスト {len(KAKUNIN)}問（{len(days)}日分）・思考問題 {len(SHIKOU)}日分。1週間で1セットです。</p>
{AD_TOP}
<div class="steps">
<div class="step"><h3><span class="n">1</span>単語帳</h3><p>最重要{len(TANGO)}語。意味は赤字で、ボタン1つで隠せます。</p><a class="btn" href="tango.html">ひらく</a></div>
<div class="step"><h3><span class="n">2</span>確認テスト</h3><p>基礎と応用の4択。全{len(KAKUNIN)}問を{len(days)}日に分けて。解説には図もあります。</p><a class="btn" href="kakunin.html">ひらく</a></div>
<div class="step"><h3><span class="n">3</span>思考問題</h3><p>共通テスト形式を{len(SHIKOU)}日分。1日約25分。</p><a class="btn" href="shikou.html">ひらく</a></div>
</div>
<h2 class="t">1週間の進め方（目安）</h2>
{plan_table()}
<h2 class="t">PDF</h2>
{pdf_links()}
<p><a href="../index.html">← 目次にもどる</a></p>
{AD_BOTTOM}
""", base="../")

    # --- 単語帳 ---
    pills = '<button type="button" class="pill on" data-area="0">全部</button>' + "".join(
        f'<button type="button" class="pill" data-area="{a["id"]}">{E(a["short"])}</button>' for a in AREAS)
    trs = ""
    for t in TANGO:
        trs += (f'<tr data-area="{t["area"]}"><td class="no">{t["no"]}</td>'
                f'<td><span class="tag g">第{t["ct"]}問</span>{area_tag(t["area"])}<br><b>{E(t["word"])}</b></td>'
                f'<td><span class="red meaning">{E(t["meaning"])}</span><div class="memo">{E(t["memo"])}</div></td>'
                f'<td class="chk">' + "".join(
                    f'<label><input type="checkbox" data-k="{t["no"]}-{k}" aria-label="{E(t["word"])} 復習{k}回目"></label>' for k in (1, 2, 3))
                + '</td></tr>')
    zu_html = render_zu(W.get("zu", []))
    tpdf = '　<a href="pdf/tango.pdf">単語帳PDFをダウンロード</a>' if pdf("tango.pdf") else ""
    page(f"{wd}/tango.html", f"第{n}週 単語帳 最重要{len(TANGO)}語",
         f"共通テスト情報Ⅰで知識問題として問われる最重要{len(TANGO)}語（第{n}週）。意味（赤字）はボタン1つで隠せます。分野別の絞り込みもできます。",
f"""{weeknav(n, "tango.html")}
<h1>第{n}週　単語帳　最重要{len(TANGO)}語</h1>
<p class="small">テストで知識問題として問われる語だけ。赤字＝意味。灰色の小さい字は覚え方。できたら右の□にチェック（このブラウザに保存されます）。</p>
{AD_TOP}
<div class="bar"><div class="pills" role="group" aria-label="分野で絞り込む">{pills}</div>
<button type="button" class="btn" id="toggle-red" aria-pressed="false">赤字をかくす</button></div>
<p class="small">赤字をかくしたあと、赤い帯をタップ（クリック）すると、その語だけ意味が見えます。</p>
<noscript><p class="note">ボタンや絞り込みを使うには、JavaScriptを有効にしてください。</p></noscript>
<table class="w tango" id="tango-table">
<thead><tr><th style="width:5%">No.</th><th style="width:26%">単語</th><th>意味（赤字）と覚え方</th><th style="width:15%">復習</th></tr></thead>
<tbody>{trs}</tbody></table>
<p><button type="button" class="btn g" id="reset-chk">チェックを全部消す</button>{tpdf}</p>
{zu_html}
<script>window.WEEK={n};</script>
{AD_BOTTOM}
""", scripts=("../app.js",), base="../")

    # --- 確認テスト ---
    kp = ""
    if pdf("kakunin-mondai.pdf") and pdf("kakunin-kaisetsu.pdf"):
        kp = ('<p class="small" style="margin-top:20px">紙で解きたい人は <a href="pdf/kakunin-mondai.pdf">問題PDF</a>・'
              '<a href="pdf/kakunin-kaisetsu.pdf">解答・解説PDF</a> をどうぞ。</p>')
    page(f"{wd}/kakunin.html", f"第{n}週 確認テスト",
         f"第{n}週の単語を、基礎と応用の4択で確認。全{len(KAKUNIN)}問・図つきの解説。まちがえた問題は選択肢の順番を変えてもう一度。",
f"""{weeknav(n, "kakunin.html")}
<h1>第{n}週　確認テスト</h1>
<p class="small">各語に「基礎」（単語帳そのまま）と「応用」（使い方・計算）を1問ずつ。単語帳は見ないで解こう。まちがえたら解説（図つき）を読んで、もう一度（選択肢の順番が変わります）。</p>
{AD_TOP}
<noscript><p class="note">確認テストを使うには、JavaScriptを有効にしてください。紙で解く場合はPDFをご利用ください。</p></noscript>
<div id="kakunin-app"></div>
{kp}
<script>window.WEEK={n};</script>
{AD_BOTTOM}
""", scripts=("../data-areas.js", "data-kakunin.js", "../app.js"), base="../")

    # --- 思考問題（ボタン式。PDFは印刷用） ---
    write_js(f"{wd}/data-shikou.js", "SHIKOU", with_shikou_figs(SHIKOU))
    spdf = ""
    if os.path.exists(os.path.join(ROOT, OUT, wd, "pdf", "shikou-mondai.pdf")):
        spdf = (f'<p class="small">印刷して解きたい人は：<a href="pdf/shikou-mondai.pdf">問題PDF（{len(SHIKOU)}日分）</a>｜'
                f'<a href="pdf/shikou-kaisetsu.pdf">解答・解説PDF</a></p>')
    page(f"{wd}/shikou.html", f"第{n}週 思考問題",
         f"第{n}週の共通テスト形式の思考問題（{len(SHIKOU)}日分）。ボタンで答えて、その場で答え合わせ。1日12か所の空欄・約25分。解説つき。",
f"""{weeknav(n, "shikou.html")}
<h1>第{n}週　思考問題</h1>
<p class="small">共通テストの形式で、会話文・図・表・プログラムを読んで空欄を埋めます。上の「日」を選び、解答欄のボタンで答えます。まちがえたら解説を読んで、選択肢の順番が変わった同じ問題にもう一度。1日約25分。計算用紙を使って解こう。</p>
{AD_TOP}
<div id="shikou-app" class="app"></div>
{spdf}
<noscript><p class="note">この問題はJavaScriptを使います。ブラウザの設定で有効にしてください。</p></noscript>
<script>window.WEEK={n};</script>
{AD_BOTTOM}
""", scripts=("../data-areas.js", "data-shikou.js", "../app.js"), base="../")
    ALL_PAGES += [f"{wd}/{p}" for p in ("index.html", "tango.html", "kakunin.html", "shikou.html")]

# ---------------- トップ（目次） ----------------
toc = ""
for W in WEEKS:
    ar = {t["area"] for t in W["tango"]}
    toc += (f'<a class="toc-c" href="w{W["n"]}/index.html"><span class="tg">第{W["n"]}週</span>'
            f'<h3>{len(ar)}分野・単語{len(W["tango"])}語</h3>'
            f'<p class="small">公開済み　確認テスト {len(W["kakunin"])}問・思考問題 {len(W["shikou"])}日分</p></a>')
first = WEEKS[0]
page("index.html", "共通テスト 情報Ⅰ 対策",
     "共通テスト「情報Ⅰ」の対策サイト。毎週20語。単語帳→確認テスト→思考問題の順で、知識問題で出る語に絞って学べます。",
f"""<section class="hero">
<div style="flex:1"><h1>共通テスト「情報Ⅰ」を、<br>毎週20語から始めよう。</h1>
<p>覚える語は1週間に20語だけ。知識問題で出る語に絞ったので、短い時間で続けられます。</p>
<p><a class="btn o" href="w{first["n"]}/index.html">第{first["n"]}週をはじめる</a></p></div>
<div class="ic"><img src="assets/icon.svg" alt="" width="84" height="84"></div>
</section>
{AD_TOP}
<h2 class="t">目次</h2>
<div class="toc">{toc}</div>
<h2 class="t">1週間の進め方</h2>
<div class="steps">
<div class="step"><h3><span class="n">1</span>単語帳</h3><p>最重要20語。意味は赤字で、ボタン1つで隠せます。</p></div>
<div class="step"><h3><span class="n">2</span>確認テスト</h3><p>基礎と応用の4択を40問、3日に分けて。図つきの解説。</p></div>
<div class="step"><h3><span class="n">3</span>思考問題</h3><p>共通テスト形式を4日分。1日約25分。</p></div>
</div>
<p class="small">くわしくは<a href="howto.html">使い方</a>、4つの分野は<a href="syllabus.html">分野（シラバス）</a>へ。</p>
<h2 class="t">このサイトの方針</h2>
<table class="w">
<tr><td style="width:32%"><b>単語は1週20語だけ</b></td><td>多すぎるとやる気がなくなるので、少なく区切ります。</td></tr>
<tr><td><b>知識問題に絞る</b></td><td>試験で「知らないと解けない語」だけを載せます。</td></tr>
<tr><td><b>予測できる語は載せない</b></td><td>問題文から意味が推測できる語は、覚える必要がないので入れません。</td></tr>
<tr><td><b>図で分かる所は図で</b></td><td>解説は、図にしたほうが分かりやすい問題に図をつけています。</td></tr>
</table>
{AD_BOTTOM}
""", active="index.html")

# ---------------- 分野（シラバス） ----------------
rows = ""
for a in AREAS:
    i = a["id"]
    cell = ""
    for W in WEEKS:
        words = "、".join(t["word"] for t in W["tango"] if t["area"] == i)
        if words:
            cell += (f'<p style="margin:0 0 6px"><b>第{W["n"]}週</b>：{E(words)}<br>'
                     f'<a href="w{W["n"]}/tango.html#area={i}">単語帳</a>｜<a href="w{W["n"]}/kakunin.html#area={i}">確認テスト</a></p>')
    rows += (f'<tr><td>{area_tag(i)}<br><b>{E(a["name"])}</b></td><td>{E(a["summary"])}<ul class="plain">'
             + "".join(f"<li>{E(x)}</li>" for x in a["topics"]) + f'</ul></td><td class="small">{cell}</td></tr>')
page("syllabus.html", "分野（シラバス）",
     "高校「情報Ⅰ」の4つの分野（学習指導要領）と、このサイトの語の対応表。",
f"""<h1>分野（シラバス）</h1>
<p>高校の科目「情報Ⅰ」は、学習指導要領で次の4つの内容に分かれています。このサイトの語も、この4分野に分けています。</p>
{AD_TOP}
<table class="w"><thead><tr><th style="width:24%">分野</th><th>主な内容</th><th style="width:36%">このサイトの語（週ごと）</th></tr></thead><tbody>{rows}</tbody></table>
<p class="small" style="margin-top:12px">※ 4つの分野名は文部科学省の学習指導要領による。各語をどの分野に入れるかは、このサイトでの整理です（教科書によって分け方が少し違うことがあります）。<br>
参考：<a href="https://www.mext.go.jp/content/000166201.pdf" rel="noopener">文部科学省「高等学校『情報』実践事例集」（目次に4つの内容が載っています）</a></p>
{AD_BOTTOM}
""", active="syllabus.html")

# ---------------- 使い方 ----------------
page("howto.html", "使い方", "情報屋の使い方と、1週間（7日）の進め方の目安。",
f"""<h1>使い方</h1>
<p>教材は「週」ごとに1セットです。1セット＝単語20語＋確認テスト3日分＋思考問題4日分で、1週間（7日）で終わる量にしてあります。</p>
<h2 class="t">3つのステップ</h2>
<ol class="plain">
<li><b>単語帳</b>：20語を見て、赤字（意味）をかくして思い出す。できたら□にチェック。</li>
<li><b>確認テスト</b>：基礎と応用の4択。まちがえたら解説（図つき）を読んでもう一度。</li>
<li><b>思考問題</b>：共通テスト形式。解説の「解く手順」をまねして解く。</li>
</ol>
<h2 class="t">1週間の進め方（目安）</h2>
{plan_table()}
{AD_TOP}
<h2 class="t">困ったとき</h2>
<ul class="plain">
<li>赤字がかくれたままのとき：赤い帯をタップ（クリック）すると、その語だけ見えます。</li>
<li>チェックは、お使いのブラウザにだけ保存されます（別の端末には引きつがれません）。</li>
<li>まちがいを見つけたら、<a href="contact.html">お問い合わせ</a>からお知らせください。</li>
</ul>
{AD_BOTTOM}
""", active="howto.html")

# ---------------- About / お問い合わせ / プライバシー ----------------
ABOUT_AD = ("当サイトは、Google AdSenseなどの広告を掲載しています。広告の扱いは<a href=\"privacy.html\">プライバシーポリシー</a>に書いています。"
            if ADS_ENABLED else
            "当サイトは、現在、広告を掲載していません。今後掲載する場合は、<a href=\"privacy.html\">プライバシーポリシー</a>でお知らせします。")
page("about.html", "このサイトについて", f"{SITE_NAME}の運営者情報。",
f"""<h1>このサイトについて</h1>
<div class="abt">
<section class="card"><h3>サイトの目的</h3><p>{E(SITE_NAME)}は、共通テスト「情報Ⅰ」を初めて学ぶ人でも、単語帳→確認テスト→思考問題の順に進めて理解できるように作った対策サイトです。単語は試験で知識として問われるものに絞り、1週間に20語から始められます。</p></section>
<section class="card"><h3>運営者</h3><p>{E(OWNER_TEXT)}</p></section>
<section class="card"><h3>掲載内容について</h3><p>掲載している問題・解説は、運営者がオリジナルで作成したものです。内容に誤りに気づかれた場合は<a href="contact.html">お問い合わせ</a>からご連絡ください。</p></section>
<section class="card"><h3>広告について</h3><p>{ABOUT_AD}</p></section>
</div>
""")
page("contact.html", "お問い合わせ", f"{SITE_NAME}へのお問い合わせ先。",
f"""<h1>お問い合わせ</h1>
<p>ご意見・まちがいのご指摘は、次のメールアドレスまでお願いします。</p>
<p><a href="mailto:{E(EMAIL)}">{E(EMAIL)}</a></p>
""")
AD_POLICY = (
"""<h2 class="t">広告について</h2>
<p>当サイトは、第三者配信の広告サービス「Google AdSense」を利用しています。Googleなどの第三者配信事業者は、Cookieを使って、利用者が当サイトや他のサイトに過去にアクセスした情報に基づいて広告を配信します。</p>
<p>GoogleによるCookieの使用により、利用者に合った広告が表示されます。パーソナライズ広告は、<a href="https://adssettings.google.com/" target="_blank" rel="noopener">広告設定</a>で無効にできます。また、<a href="https://policies.google.com/technologies/ads?hl=ja" target="_blank" rel="noopener">Googleの広告に関するポリシー</a>で、Cookieの使い方を確認できます。</p>"""
if ADS_ENABLED else
"""<h2 class="t">広告について</h2>
<p>当サイトは、現在、広告を表示していません。今後、Google AdSenseなどの第三者配信の広告サービスを利用する場合は、このページに利用するサービスとCookieの扱いを書き加えます。</p>""")
page("privacy.html", "プライバシーポリシー", f"{SITE_NAME}のプライバシーポリシー。",
f"""<h1>プライバシーポリシー</h1>
<h2 class="t">個人情報の取り扱い</h2>
<p>当サイトでは、お問い合わせの際にいただいたメールアドレスなどを、返信のためだけに使います。</p>
<h2 class="t">ブラウザへの保存</h2>
<p>単語帳の「復習チェック」は、お使いのブラウザ（localStorage）にだけ保存されます。サーバーには送られません。</p>
{AD_POLICY}
<h2 class="t">免責事項</h2>
<p>掲載内容の正確さには注意していますが、その利用によって生じた損害について責任を負いません。</p>
""")

# ---------------- sitemap / robots ----------------
today = date.today().isoformat()
with open(os.path.join(ROOT, OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in ALL_PAGES:
        loc = SITE_URL + "/" + ("" if u == "index.html" else u)
        f.write(f"<url><loc>{loc}</loc><lastmod>{today}</lastmod></url>\n")
    f.write("</urlset>\n")
with open(os.path.join(ROOT, OUT, "robots.txt"), "w", encoding="utf-8") as f:
    f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
open(os.path.join(ROOT, OUT, ".nojekyll"), "w").close()
print("OK:", len(ALL_PAGES), "pages,", len(WEEKS), "weeks →", OUT)
