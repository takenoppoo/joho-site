# -*- coding: utf-8 -*-
"""資料PDF（確認テスト40問）から data/kakunin.json を作る。
使い方: python3 tools/extract_kakunin.py 問題PDF 解説PDF"""
import re, sys, json, subprocess

def text(pdf):
    return subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout.splitlines()

CH = "⓪①②③"
def parse_questions(lines):
    qs, day, cur, ctx, state = [], 0, None, [], "skip"
    for raw in lines:
        s = raw.strip()
        if not s: continue
        m = re.match(r"^(\d)日目 確認テスト", s)
        if m:
            day, cur, ctx, state = int(m.group(1)), None, [], "skip"; continue
        if "確認テスト（サンプル問題版" in s or re.match(r"^\d日目（つづき）", s): continue
        if re.match(r"^No\.\s+\d", s) or s.startswith("解答") or s.startswith("できた数"): 
            state = "skip"; continue
        m = re.match(r"^No\.(\d+)\s+(基礎|応用)\s+(.*)$", s)
        if m:
            cur = dict(day=day, no=int(m.group(1)), kind=m.group(2), context=" ".join(ctx), stem=m.group(3), choices=[])
            qs.append(cur); ctx = []; state = "stem"; continue
        if s.startswith("やり方"): state = "skip"; continue
        if cur is None: continue
        if s[0] in CH and len(s) > 1 and s[1] == " ":
            cur["choices"].append(s[2:].strip()); state = "choices"; continue
        if state == "stem":
            cur["stem"] += s
        elif state == "choices" and len(cur["choices"]) >= 4:
            ctx.append(s)
        elif state == "choices":
            cur["choices"][-1] += s   # 折り返した選択肢
    return qs

def parse_kaisetsu(lines):
    out, day, blk = {}, 0, None
    def flush():
        if blk: out[(blk["day"], blk["no"])] = blk
    for raw in lines:
        s = raw.rstrip()
        m = re.match(r"^(\d)日目 解答一覧", s.strip())
        if m: flush(); blk = None; day = int(m.group(1)); continue
        m = re.match(r"^No\.(\d+)\s+(基礎|応用)\s+(.*?)\s+答え\s+([⓪①②③])\s*$", s.strip())
        if m:
            flush(); blk = dict(day=day, no=int(m.group(1)), word=m.group(3).strip("「」 "), answer=CH.index(m.group(4)), lines=[]); continue
        if blk is not None: blk["lines"].append(s)
    flush()
    for b in out.values():
        steps, rowlines, mode, cur = [], {}, None, None
        for s in b["lines"]:
            t = s.strip()
            if t.startswith("③ 解く手順"): mode = "steps"; continue
            if t.startswith("④ 答案"): mode = None; continue
            if mode != "steps" or not t: continue
            if re.match(r"^選択肢\s+判", t) or t == "定": continue
            m = re.match(r"^([⓪①②③])\s", t)
            if m: cur = CH.index(m.group(1)); rowlines[cur] = [t[1:].strip()]; continue
            if cur is not None: rowlines[cur].append(t); continue
            m = re.match(r"^(\d)\.\s+(.*)$", t)
            if m: steps.append(m.group(2)); continue
            if steps: steps[-1] += t
        b["steps"] = [x for x in steps if "（下の表）" not in x]
        b["rowraw"] = rowlines
    return out

def build_rows(raw, choices):
    """各選択肢の ○× と理由（選択肢の文は問題側のものを使う）"""
    rows = []
    for i in range(4):
        ls, mark, reason = raw.get(i, []), None, ""
        for j, l in enumerate(ls):
            m = re.search(r"\s([○×])\s+(.*)$", " " + l) if mark is None else None
            if m: mark, reason = m.group(1), m.group(2).strip(); rest = ls[j+1:]; break
        else:
            return None
        for l in rest:
            l = l.strip()
            if l and l not in choices[i]: reason += l      # 選択肢の折り返し部分は理由に入れない
        rows.append(dict(mark=mark, reason=re.sub(r"\s+", "", reason)))
    return rows


if __name__ == "__main__":
    qs = parse_questions(text(sys.argv[1])); kai = parse_kaisetsu(text(sys.argv[2]))
    bad = []
    for q in qs:
        k = kai.get((q["day"], q["no"]))
        rows = build_rows(k["rowraw"], q["choices"])
        q["word"] = k["word"]; q["answer"] = k["answer"]; q["steps"] = k["steps"]; q["rows"] = rows
        ok = len(q["choices"]) == 4 and rows and [r["mark"] for r in rows].count("○") == 1 and rows[q["answer"]]["mark"] == "○"
        if not ok: bad.append((q["day"], q["no"]))
    json.dump(qs, open("tools/kakunin_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(qs), "questions; problems:", bad)
