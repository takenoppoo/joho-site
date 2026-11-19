# -*- coding: utf-8 -*-
"""情報屋：静的サイト生成スクリプト。
下の CONFIG を書き換えて `python3 build.py` を実行すると、docs/ の HTML・データ・sitemap が作り直される。
（docs/style.css・docs/app.js・docs/assets・docs/pdf・docs/img は手で置いたものなので上書きしない）
"""
import json, os, html
from datetime import date

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

def load(name):
    with open(os.path.join(ROOT, "data", name + ".json"), encoding="utf-8") as f:
        return json.load(f)

AREAS, TANGO, KAKUNIN, SHIKOU = load("areas"), load("tango"), load("kakunin"), load("shikou")
AREA = {a["id"]: a for a in AREAS}
N_WORDS = {a["id"]: sum(1 for t in TANGO if t["area"] == a["id"]) for a in AREAS}
N_Q = {a["id"]: sum(1 for q in KAKUNIN if q["area"] == a["id"]) for a in AREAS}

NAV = [("index.html", "ホーム"), ("tango.html", "単語帳"), ("kakunin.html", "確認テスト"),
       ("shikou.html", "思考問題"), ("syllabus.html", "分野（シラバス）"), ("howto.html", "使い方")]

def area_tag(a):
    return f'<span class="tag a{a}">{E(AREA[a]["short"])}</span>'

def page(fname, title, desc, body, active=None, scripts=()):
    full_title = SITE_NAME if fname == "index.html" else f"{title}｜{SITE_NAME}"
    nav = "".join(f'<a href="{h}"{" class=on" if h == active else ""}>{n}</a>' for h, n in NAV)
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
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="favicon.ico" sizes="48x48">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="stylesheet" href="style.css">
<!-- 広告（AdSense）承認後：ここに <script async src="https://pagead2.googlesyndication.com/..."></script> を貼る -->
</head>
<body>
<header class="site-h"><div class="wrap">
<a class="logo" href="index.html"><img src="assets/logo.svg" alt="{E(SITE_NAME)}" width="142" height="44"></a>
<nav>{nav}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site-f"><div class="wrap">
<p><a href="howto.html">使い方</a>｜<a href="about.html">このサイトについて</a>｜<a href="contact.html">お問い合わせ</a>｜<a href="privacy.html">プライバシーポリシー</a></p>
<p>© {E(SITE_NAME)}　掲載の問題・解説はオリジナルです。</p>
</div></footer>
{sc}
</body>
</html>
"""
    with open(os.path.join(ROOT, OUT, fname), "w", encoding="utf-8") as f:
        f.write(doc)

AD_TOP = "<!-- 広告枠（上）：AdSense承認後、ここに広告コードを貼る -->"
AD_BOTTOM = "<!-- 広告枠（下）：AdSense承認後、ここに広告コードを貼る -->"

# ---------------- データ（ブラウザ用） ----------------
def write_js(fname, var, obj):
    with open(os.path.join(ROOT, OUT, fname), "w", encoding="utf-8") as f:
        f.write(f"window.{var}=" + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";\n")

write_js("data-areas.js", "AREAS", AREAS)
write_js("data-kakunin.js", "KAKUNIN", KAKUNIN)

# ---------------- トップ ----------------
cards = ""
for a in AREAS:
    i = a["id"]
    cards += (f'<div class="card"><h3>{area_tag(i)} {E(a["name"])}</h3><p>{E(a["summary"])}</p>'
              f'<p class="small">単語 {N_WORDS[i]}語・確認テスト {N_Q[i]}問</p>'
              f'<div class="lk"><a class="btn g" href="tango.html#area={i}">単語帳</a>'
              f'<a class="btn g" href="kakunin.html#area={i}">確認テスト</a></div></div>')
page("index.html", "共通テスト 情報Ⅰ 対策",
     "共通テスト「情報Ⅰ」の対策サイト。単語は20語だけ。単語帳→確認テスト→思考問題の順で、知識問題で出る語に絞って学べます。",
f"""<section class="hero">
<div style="flex:1"><h1>共通テスト「情報Ⅰ」を、<br>20語から始めよう。</h1>
<p>覚える語は20語だけ。知識問題で出る語に絞ったので、短い時間で続けられます。</p>
<p><a class="btn o" href="tango.html">単語帳をひらく</a></p></div>
<div class="ic"><img src="assets/icon.svg" alt="" width="84" height="84"></div>
</section>
{AD_TOP}
<h2 class="t">学習の流れ</h2>
<div class="steps">
<div class="step"><h3><span class="n">1</span>単語帳</h3><p>最重要{len(TANGO)}語。意味は赤字で、ボタン1つで隠せます。</p><a class="btn" href="tango.html">ひらく</a></div>
<div class="step"><h3><span class="n">2</span>確認テスト</h3><p>基礎と応用の4択。全{len(KAKUNIN)}問を3日に分けて。</p><a class="btn" href="kakunin.html">ひらく</a></div>
<div class="step"><h3><span class="n">3</span>思考問題</h3><p>共通テスト形式を{len(SHIKOU)}日分。1日約25分。</p><a class="btn" href="shikou.html">ひらく</a></div>
</div>
<h2 class="t">分野から選ぶ</h2>
<p class="small">高校「情報Ⅰ」の4つの分野（学習指導要領）に分けています。くわしくは<a href="syllabus.html">分野（シラバス）</a>へ。</p>
<div class="cards">{cards}</div>
<h2 class="t">このサイトの方針</h2>
<table class="w">
<tr><td style="width:32%"><b>単語は20語だけ</b></td><td>多すぎるとやる気がなくなるので、少なく区切ります。</td></tr>
<tr><td><b>知識問題に絞る</b></td><td>試験で「知らないと解けない語」だけを載せます。</td></tr>
<tr><td><b>予測できる語は載せない</b></td><td>問題文から意味が推測できる語は、覚える必要がないので入れません。</td></tr>
</table>
{AD_BOTTOM}
""", active="index.html")

# ---------------- 単語帳 ----------------
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
page("tango.html", "単語帳 最重要20語",
     "共通テスト情報Ⅰで知識問題として問われる最重要20語。意味（赤字）はボタン1つで隠せます。分野別の絞り込みもできます。",
f"""<h1>単語帳　最重要{len(TANGO)}語</h1>
<p class="small">テストで知識問題として問われる語だけ。赤字＝意味。灰色の小さい字は覚え方。できたら右の□にチェック（このブラウザに保存されます）。</p>
{AD_TOP}
<div class="bar"><div class="pills" role="group" aria-label="分野で絞り込む">{pills}</div>
<button type="button" class="btn" id="toggle-red" aria-pressed="false">赤字をかくす</button></div>
<p class="small">赤字をかくしたあと、赤い帯をタップ（クリック）すると、その語だけ意味が見えます。</p>
<noscript><p class="note">ボタンや絞り込みを使うには、JavaScriptを有効にしてください。</p></noscript>
<table class="w tango" id="tango-table">
<thead><tr><th style="width:5%">No.</th><th style="width:26%">単語</th><th>意味（赤字）と覚え方</th><th style="width:15%">復習</th></tr></thead>
<tbody>{trs}</tbody></table>
<p><button type="button" class="btn g" id="reset-chk">チェックを全部消す</button>　<a href="pdf/tango.pdf">単語帳PDFをダウンロード</a></p>
<h2 class="t">図と表</h2>
<p class="small">文字だけだと分かりにくい語を、図や表でまとめました。</p>
<div class="zu"><img src="img/zu-2.png" alt="図と表（1）回線交換とパケット交換の比較、IPアドレス、デジタル化の3ステップ、階調、論理演算、配列と添字" loading="lazy">
<img src="img/zu-3.png" alt="図と表（2）ベン図とマトリクス図、散布図と相関、ヒストグラムと箱ひげ図、回帰直線、PDCAサイクル" loading="lazy"></div>
{AD_BOTTOM}
""", active="tango.html", scripts=("app.js",))

# ---------------- 確認テスト ----------------
page("kakunin.html", "確認テスト",
     "単語帳の20語を、基礎と応用の4択で確認。全40問・解説つき。まちがえた問題は選択肢の順番を変えてもう一度。",
f"""<h1>確認テスト</h1>
<p class="small">各語に「基礎」（単語帳そのまま）と「応用」（使い方・計算）を1問ずつ。単語帳は見ないで解こう。まちがえたら解説を読んで、もう一度（選択肢の順番が変わります）。</p>
{AD_TOP}
<noscript><p class="note">確認テストを使うには、JavaScriptを有効にしてください。紙で解く場合は <a href="pdf/kakunin-mondai.pdf">問題PDF</a> と <a href="pdf/kakunin-kaisetsu.pdf">解答・解説PDF</a> をご利用ください。</p></noscript>
<div id="kakunin-app"></div>
<p class="small" style="margin-top:20px">紙で解きたい人は <a href="pdf/kakunin-mondai.pdf">問題PDF</a>・<a href="pdf/kakunin-kaisetsu.pdf">解答・解説PDF</a> をどうぞ。</p>
{AD_BOTTOM}
""", active="kakunin.html", scripts=("data-areas.js", "data-kakunin.js", "app.js"))

# ---------------- 思考問題 ----------------
cs = ""
for s in SHIKOU:
    tags = "".join(area_tag(a) for a in s["areas"])
    cs += (f'<div class="card"><h3>{s["day"]}日目　{E(s["title"])}</h3><p>{E(s["theme"])}</p>'
           f'<p class="small">{tags}　空欄 {s["blanks"]}か所／約{s["minutes"]}分</p>'
           f'<div class="lk"><a class="btn" href="pdf/shikou-mondai.pdf#page={s["q_page"]}">問題をひらく</a>'
           f'<a class="btn g" href="pdf/shikou-kaisetsu.pdf#page={s["k_page"]}">解答・解説</a></div></div>')
page("shikou.html", "思考問題",
     "共通テスト形式の思考問題（4日分）。1日12か所の空欄・約25分。解答・解説つき。",
f"""<h1>思考問題</h1>
<p class="small">共通テストの形式で、会話文・図・表・プログラムを読んで空欄を埋めます。1日約25分。単語帳は見ないで、計算用紙を使って解こう。</p>
{AD_TOP}
<div class="cards">{cs}</div>
<h2 class="t">進め方</h2>
<ol class="plain">
<li>「問題をひらく」を開き、紙に書き写すか印刷して解く（解答欄に番号・数字を書く）。</li>
<li>解き終わったら「解答・解説」で答え合わせ。できた数を記録する。</li>
<li>まちがえた所は、解説の「解く手順」をなぞって、もう一度。</li>
</ol>
<p>全部まとめてダウンロード：<a href="pdf/shikou-mondai.pdf">問題（4日分）</a>｜<a href="pdf/shikou-kaisetsu.pdf">解答・解説（4日分）</a></p>
<p class="note">いまは問題をPDFで公開しています。画面で答え合わせできる形にするのは、あとから追加できます。</p>
{AD_BOTTOM}
""", active="shikou.html")

# ---------------- 分野（シラバス） ----------------
rows = ""
for a in AREAS:
    i = a["id"]
    words = "、".join(t["word"] for t in TANGO if t["area"] == i)
    rows += (f'<tr><td>{area_tag(i)}<br><b>{E(a["name"])}</b></td><td>{E(a["summary"])}<ul class="plain">'
             + "".join(f"<li>{E(x)}</li>" for x in a["topics"]) + f'</ul></td>'
             f'<td class="small">{E(words)}<br><a href="tango.html#area={i}">単語帳</a>｜<a href="kakunin.html#area={i}">確認テスト</a></td></tr>')
page("syllabus.html", "分野（シラバス）",
     "高校「情報Ⅰ」の4つの分野（学習指導要領）と、このサイトの20語の対応表。",
f"""<h1>分野（シラバス）</h1>
<p>高校の科目「情報Ⅰ」は、学習指導要領で次の4つの内容に分かれています。このサイトの語も、この4分野に分けています。</p>
{AD_TOP}
<table class="w"><thead><tr><th style="width:24%">分野</th><th>主な内容</th><th style="width:34%">このサイトの語</th></tr></thead><tbody>{rows}</tbody></table>
<p class="small" style="margin-top:12px">※ 4つの分野名は文部科学省の学習指導要領による。各語をどの分野に入れるかは、このサイトでの整理です（教科書によって分け方が少し違うことがあります）。<br>
参考：<a href="https://www.mext.go.jp/content/000166201.pdf" rel="noopener">文部科学省「高等学校『情報』実践事例集」（目次に4つの内容が載っています）</a></p>
{AD_BOTTOM}
""", active="syllabus.html")

# ---------------- 使い方 ----------------
page("howto.html", "使い方", "情報屋の使い方と、学習の進め方の目安（4日プラン）。",
f"""<h1>使い方</h1>
<h2 class="t">3つのステップ</h2>
<ol class="plain">
<li><b>単語帳</b>：20語を見て、赤字（意味）をかくして思い出す。できたら□にチェック。</li>
<li><b>確認テスト</b>：基礎と応用の4択。まちがえたら解説を読んでもう一度。</li>
<li><b>思考問題</b>：共通テスト形式。解説の「解く手順」をまねして解く。</li>
</ol>
<h2 class="t">4日プランの目安</h2>
<table class="w">
<tr><th>日</th><th>やること</th></tr>
<tr><td>1日目</td><td>単語帳（20語を1周）→ 確認テスト1日目 → 思考問題1日目</td></tr>
<tr><td>2日目</td><td>単語帳（赤字をかくして確認）→ 確認テスト2日目 → 思考問題2日目</td></tr>
<tr><td>3日目</td><td>確認テスト3日目 → 思考問題3日目</td></tr>
<tr><td>4日目</td><td>まちがえた語を単語帳で復習 → 思考問題4日目</td></tr>
</table>
<p class="small">自分のペースで、日数は増やしてかまいません。</p>
{AD_BOTTOM}
""", active="howto.html")

# ---------------- About / お問い合わせ / プライバシー ----------------
ABOUT_AD = ("当サイトは、Google AdSenseなどの広告を掲載しています。広告の扱いは<a href=\"privacy.html\">プライバシーポリシー</a>に書いています。"
            if ADS_ENABLED else
            "当サイトは、現在、広告を掲載していません。今後掲載する場合は、<a href=\"privacy.html\">プライバシーポリシー</a>でお知らせします。")
page("about.html", "このサイトについて", f"{SITE_NAME}の運営者情報。",
f"""<h1>このサイトについて</h1>
<div class="abt">
<section class="card"><h3>サイトの目的</h3><p>{E(SITE_NAME)}は、共通テスト「情報Ⅰ」を初めて学ぶ人でも、単語帳→確認テスト→思考問題の順に進めて理解できるように作った対策サイトです。単語は試験で知識として問われるものに絞り、20語から始められます。</p></section>
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
urls = [h for h, _ in NAV] + ["about.html", "contact.html", "privacy.html"]
with open(os.path.join(ROOT, OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in urls:
        loc = SITE_URL + "/" + ("" if u == "index.html" else u)
        f.write(f"<url><loc>{loc}</loc><lastmod>{today}</lastmod></url>\n")
    f.write("</urlset>\n")
with open(os.path.join(ROOT, OUT, "robots.txt"), "w", encoding="utf-8") as f:
    f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
open(os.path.join(ROOT, OUT, ".nojekyll"), "w").close()
print("OK:", len(urls), "pages →", OUT)
