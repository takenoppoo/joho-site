【情報屋　共通テスト「情報Ⅰ」対策サイト 一式】

■ 中身
docs/        公開するサイト本体（GitHub Pagesで公開するフォルダ）
  index.html 単語帳 tango.html 確認テスト kakunin.html 思考問題 shikou.html
  分野（シラバス）syllabus.html 使い方 howto.html ほか about / contact / privacy
  style.css app.js          見た目とボタンの動き（手で置いたファイル）
  assets/    ロゴ（logo.svg, logo-dark.svg）・アイコン（icon.svg, favicon.svg, PNG）
  pdf/       資料のPDF（単語帳・確認テスト・思考問題）  img/  単語帳の図と表
data/        問題のデータ（ここを書き換えて build.py を実行すると問題が変わる）
  tango.json 単語帳20語   kakunin.json 確認テスト40問   shikou.json 思考問題4日分   areas.json 4分野
build.py     docs/ のHTMLとデータを作り直すスクリプト（Python3だけで動く）
tools/       make_logo.py（ロゴのSVGを書き出す）, extract_kakunin.py / make_data.py（資料PDFからデータを作った手順）

■ 公開前に必ず書き換える所（build.py の先頭 CONFIG）
SITE_NAME / SITE_URL（公開するURL）/ EMAIL（連絡先）/ OWNER_TEXT（自己紹介）
書き換えたら `python3 build.py` で docs/ を作り直す。

■ 公開方法（GitHub Pages、無料）
1. GitHub でリポジトリを作る（Public）
2. このフォルダの中身をアップロード（docs フォルダごと）
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
- 思考問題は、資料のPDFを公開する形（日ごとにPDFの該当ページへ）。画面で答え合わせする形は今後の追加。
- 問題・単語は資料のサンプル（20語・40問・4日分）。

■ 広告を載せるとき（忘れずに）
1. build.py の ADS_ENABLED を True にして `python3 build.py` → privacy.html の広告の文章がAdSense用に切り替わる
2. 各ページの head・AD_TOP / AD_BOTTOM のコメントの所に広告コードを貼る
3. docs/ を GitHub に上げ直す
