【情報屋　共通テスト「情報Ⅰ」対策サイト 一式】

■ 中身
docs/        公開するサイト本体（GitHub Pagesで公開するフォルダ）
  index.html 目次（週の一覧）/ syllabus.html 分野 / howto.html 使い方 / about・contact・privacy
  style.css app.js   見た目とボタンの動き（手で置いたファイル。週が増えても共通）
  assets/            ロゴ・アイコン
  w1/ w2/ …          週ごとのページ（index まとめ / tango 単語帳 / kakunin 確認テスト / shikou 思考問題）
    pdf/ img/        その週のPDF・図と表（手で置く／tools/make_pdf.py で作る）
data/        問題のデータ
  areas.json         4分野（全部の週で共通）
  w01/ w02/ …        週ごと：tango.json 単語帳20語 / kakunin.json 確認テスト40問 / shikou.json 思考問題4日分
build.py     docs/ のHTML・データ・sitemapを作り直す（Python3だけで動く）
figs.py      解説の図（SVG）を描く。data の "fig" に仕様を書くと図が出る
weeks.py     data/ を読む共通部分
tools/       make_pdf.py（解答・解説PDFを作る。Chromeが必要）ほか、第1週のデータを作った手順

■ 新しい週を足す手順（第2週の例）
1. data/w02/ を作り、tango.json / kakunin.json / shikou.json を置く（w01 をコピーして中身を書き換えるのが早い）
2. python3 build.py     → docs/w2/ のページと、トップの目次カード（第2週）ができる
3. python3 tools/make_pdf.py 2            → 確認テストの解答・解説PDF（図つき）
   python3 tools/make_pdf.py 2 mondai     → 確認テストの問題PDF
   （単語帳PDF・思考問題PDFは今は手で docs/w2/pdf/ に置く。置いたものは自動でリンクされる）
4. docs/ を GitHub に上げる

■ 解説に図を入れる
kakunin.json の問題に "fig": {"type": "venn", ...} を足すだけ。種類と書き方は figs.py の先頭と、data/w01/kakunin.json の例を見る。
種類: venn / switching / bitop / ipsplit / doubling / matrix / boxplot / pdca / sampling / scatter / array / line / hist / binary
（Webの解説とPDFの解説の両方に出る。新しい種類の図は figs.py に fig_○○ を書き足す）

■ 公開前に必ず書き換える所（build.py の先頭 CONFIG）
SITE_NAME / SITE_URL（公開するURL）/ EMAIL（連絡先）/ OWNER_TEXT（自己紹介）
書き換えたら `python3 build.py` で docs/ を作り直す。

■ 公開方法（GitHub Pages、無料）
1. GitHub でリポジトリを作る（Public）
2. このフォルダの中身をアップロード（フォルダ構造のまま）
3. Settings → Pages → Branch を main、フォルダを /docs にする

■ 問題を増やすとき
- 単語帳：data/tango.json に1語ぶん追加（area は 1〜4 の分野番号、ct は共通テストの大問）
- 確認テスト：data/kakunin.json に追加（answer は 0〜3 の番号。choices の順番は、表示のたびに自動で入れ替わる）
- 追加したら `python3 build.py`

■ 分野（学習指導要領「情報Ⅰ」の4内容）
1 情報社会の問題解決 / 2 コミュニケーションと情報デザイン / 3 コンピュータとプログラミング / 4 情報通信ネットワークとデータの活用
※ 各語をどの分野に入れたかは、このサイトでの整理（data/tango.json の area）。変えたい語は area を書き換える。

■ 広告（AdSense）
各ページの <!-- 広告枠 --> のコメントの所に、承認後に広告コードを貼る（build.py の AD_TOP / AD_BOTTOM と、各ページの head のコメント）。

■ ロゴを作り直すとき
python3 tools/make_logo.py（fontTools と Noto Sans CJK JP Black が必要。docs/assets/ に書き出される）

■ 今の状態
- 第1週：思考問題は、資料のPDFを公開する形（日ごとにPDFの該当ページへ）。画面で答え合わせする形は今後の追加。
- 第1週は資料のサンプル（20語・40問・4日分）。

■ 広告を載せるとき（忘れずに）
1. build.py の ADS_ENABLED を True にして `python3 build.py` → privacy.html の広告の文章がAdSense用に切り替わる
2. 各ページの head・AD_TOP / AD_BOTTOM のコメントの所に広告コードを貼る
3. docs/ を GitHub に上げ直す

【思考問題（ボタン式）】
 data/wNN/shikou.json を、tools/make_shikou_w01.py のように作ります（空欄・解答群・解説を1か所にまとめる）。
 python3 tools/make_shikou_w01.py → python3 build.py で wN/shikou.html と data-shikou.js ができます。
 単語帳の「図と表」は data/wNN/zu.json（表・図の仕様）に書きます。
