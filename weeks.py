# -*- coding: utf-8 -*-
"""data/ を読む共通部分（build.py と tools/make_pdf.py が使う）。
data/areas.json …… 4分野（全部の週で共通）
data/w01/ w02/ …… 週ごとのデータ（tango.json 単語帳 / kakunin.json 確認テスト / shikou.json 思考問題）
新しい週を足すときは data/w02/ を作って3つのJSONを置き、python3 build.py を実行する。
"""
import json, os, re
import figs

ROOT = os.path.dirname(os.path.abspath(__file__))


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_areas():
    return _load(os.path.join(ROOT, "data", "areas.json"))


def load_weeks():
    weeks = []
    for name in sorted(os.listdir(os.path.join(ROOT, "data"))):
        m = re.fullmatch(r"w(\d+)", name)
        d = os.path.join(ROOT, "data", name)
        if not (m and os.path.isdir(d)):
            continue
        weeks.append(dict(
            n=int(m.group(1)),
            tango=_load(os.path.join(d, "tango.json")),
            kakunin=_load(os.path.join(d, "kakunin.json")),
            shikou=_load(os.path.join(d, "shikou.json")),
            zu=_load(os.path.join(d, "zu.json")) if os.path.exists(os.path.join(d, "zu.json")) else [],
        ))
    return sorted(weeks, key=lambda w: w["n"])


def with_figs(kakunin):
    """fig の仕様（辞書）を SVG の文字列に置き換えたコピーを返す"""
    out = []
    for q in kakunin:
        q = dict(q)
        if q.get("fig"):
            q["fig"] = figs.render(q["fig"])
        out.append(q)
    return out


def _opt(o):
    if isinstance(o, dict) and "fig" in o:
        return {"svg": figs.render({"type": "choice", "name": o["fig"]})}
    return {"t": o}


def with_shikou_figs(days):
    """思考問題のデータ：選択肢の図・本文中の図（"fig" 仕様）を SVG に、選択肢の文字を {"t": …} にそろえる"""
    out = []
    for d in days:
        d = json.loads(json.dumps(d))
        for g in d.get("groups", {}).values():
            g["options"] = [_opt(o) for o in g["options"]]
        for p in d.get("parts", []):
            for b in p.get("blocks", []):
                if b.get("t") == "fig":
                    b["svg"] = figs.render(b.pop("spec"))
        out.append(d)
    return out
