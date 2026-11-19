# -*- coding: utf-8 -*-
"""確認テストの「解答・解説」PDF（図つき）を作る。Google Chrome（headless）が必要。
使い方（リポジトリの一番上のフォルダで）:
    python3 tools/make_pdf.py 1            # 第1週の解答・解説 → docs/w1/pdf/kakunin-kaisetsu.pdf
    python3 tools/make_pdf.py 2 mondai     # 第2週の問題 → docs/w2/pdf/kakunin-mondai.pdf
問題PDFは、すでに docs/wN/pdf/ に手で置いたものがあるときは作り直さないこと（上書きされます）。
"""
import html, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from weeks import ROOT, load_weeks, with_figs

E = html.escape
CH = "⓪①②③"

CSS = """
@page{size:A4;margin:13mm 14mm}
*{box-sizing:border-box}
body{margin:0;font-family:'Noto Sans CJK JP','Noto Sans JP','Hiragino Sans',sans-serif;font-size:10.5pt;line-height:1.65;color:#1d2433}
h1{font-size:17pt;color:#14284B;margin:0 0 8px;border-bottom:3px solid #14284B;padding-bottom:4px}
.day{background:#1F4E9A;color:#fff;font-weight:700;padding:5px 12px;border-radius:5px;margin:0 0 6px;font-size:12pt}
.chips{margin:0 0 10px;font-size:8.5pt}
.chips span{display:inline-block;border:1px solid #14284B;border-radius:9px;padding:0 7px;margin:0 3px 3px 0}
.q{page-break-after:always;border:1.5px solid #b9c6e0;border-radius:8px;overflow:hidden;margin:0}
.q:last-child{page-break-after:auto}
.qh{display:flex;justify-content:space-between;align-items:center;background:#EEF3FC;padding:6px 12px;font-weight:700;font-size:12.5pt;color:#14284B}
.qh .k{font-size:8.5pt;border:1px solid #5A6478;border-radius:3px;padding:0 6px;margin:0 6px;color:#333;font-weight:400}
.qh .a{background:#F28C28;color:#fff;border-radius:4px;padding:1px 12px;font-size:11pt}
.sec{padding:8px 14px 2px}
.sec h3{display:inline-block;margin:0 0 5px;font-size:9.5pt;color:#fff;padding:0 9px;border-radius:3px}
.s1 h3{background:#5A6478}.s2 h3{background:#2E7D5B}.s3 h3{background:#1F4E9A}.s4 h3{background:#F28C28}
.sec p{margin:2px 0}.ch{padding-left:1.4em;text-indent:-1.4em;margin:2px 0}
.sec ol,.sec ul{margin:2px 0 6px;padding-left:1.6em}
table{border-collapse:collapse;width:100%;font-size:9.5pt;margin:6px 0 8px}
th{background:#EEF3FC;text-align:left;padding:3px 8px;border:1px solid #b9c6e0}
td{padding:3px 8px;border:1px solid #b9c6e0}
.o{color:#2E7D5B;font-weight:700;text-align:center}.x{color:#c0283c;font-weight:700;text-align:center}
.fig{display:block;width:100%;max-width:150mm;height:auto;margin:4px auto}
.figcap{text-align:center;font-size:8.5pt;color:#5A6478;margin:0 0 4px}
.ans{background:#FFF5E6;padding:6px 14px 8px;font-weight:700;border-top:1px solid #F5C98F}
"""


def kaisetsu_html(W):
    K = with_figs(W["kakunin"])
    out = [f"<h1>確認テスト（{len(K)}問） 解答・解説　第{W['n']}週</h1>"]
    seen = set()
    for q in K:
        if q["day"] not in seen:
            seen.add(q["day"])
            day_q = [x for x in K if x["day"] == q["day"]]
            head = f'<div class="day">{q["day"]}日目　解答一覧</div><div class="chips">' + "".join(
                f'<span>No.{x["no"]} {CH[x["answer"]]}</span>' for x in day_q) + "</div>"
            first = True
        else:
            head, first = "", False
        step_last = "各選択肢をこの意味と比べ、○×を付ける（下の表）。" if q["kind"] == "基礎" else "各選択肢を求めた答えと比べ、○×を付ける（下の表）。"
        steps = "".join(f"<li>{E(s)}</li>" for s in q["steps"] + [step_last])
        ch = "".join(f'<p class="ch">{CH[i]} {E(c)}</p>' for i, c in enumerate(q["choices"]))
        org = "".join(f"<li>{E(x)}</li>" for x in q.get("organize", []))
        fig = f'<div class="figcap">図</div>{q["fig"]}' if q.get("fig") else ""
        rows = "".join(
            f'<tr><td>{CH[i]} {E(c)}</td><td class="{"o" if q["rows"][i]["mark"] == "○" else "x"}">{q["rows"][i]["mark"]}</td><td>{E(q["rows"][i]["reason"])}</td></tr>'
            for i, c in enumerate(q["choices"]))
        ctx = f'<p>{E(q["context"])}</p>' if q["context"] else ""
        out.append(f"""{head}<div class="q">
<div class="qh"><span>No.{q["no"]}<span class="k">{q["kind"]}</span>「{E(q["word"])}」</span><span class="a">答え {CH[q["answer"]]}</span></div>
<div class="sec s1"><h3>① 問題</h3>{ctx}<p>{E(q["stem"])}</p>{ch}</div>
<div class="sec s2"><h3>② 問題の整理</h3><ul>{org}</ul></div>
<div class="sec s3"><h3>③ 解く手順（考え方）</h3><ol>{steps}</ol>{fig}
<table><thead><tr><th>選択肢</th><th style="width:9%">判定</th><th>理由</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="ans">④ 答案　No.{q["no"]} {CH[q["answer"]]} {E(q["choices"][q["answer"]])}</div>
</div>""")
    return out


def mondai_html(W):
    K = W["kakunin"]
    out = [f"<h1>確認テスト（{len(K)}問） 問題　第{W['n']}週</h1>"]
    for q in K:
        ctx = f'<p>{E(q["context"])}</p>' if q["context"] else ""
        ch = "".join(f'<p class="ch">{CH[i]} {E(c)}</p>' for i, c in enumerate(q["choices"]))
        out.append(f"""<div class="q"><div class="qh"><span>No.{q["no"]}<span class="k">{q["kind"]}</span>{q["day"]}日目</span><span>答え（　　）</span></div>
<div class="sec s1">{ctx}<p>{E(q["stem"])}</p>{ch}</div><div style="height:150mm"></div></div>""")
    return out


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    kind = sys.argv[2] if len(sys.argv) > 2 else "kaisetsu"
    W = [w for w in load_weeks() if w["n"] == n][0]
    body = (kaisetsu_html if kind == "kaisetsu" else mondai_html)(W)
    doc = f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(body)}</body></html>'
    outdir = os.path.join(ROOT, "docs", f"w{n}", "pdf")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f"kakunin-{kind.replace('kaisetsu', 'kaisetsu')}.pdf")
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "p.html")
        open(src, "w", encoding="utf-8").write(doc)
        subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={out}", "file://" + src], check=True, capture_output=True, timeout=180)
    print("OK:", out)


if __name__ == "__main__":
    main()
