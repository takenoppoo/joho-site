/* 情報屋：単語帳（赤字をかくす）と確認テストの動き。外部ライブラリなし。 */
(function () {
  "use strict";
  var CH = ["⓪", "①", "②", "③"];

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }
  function hashParam(k) {
    var m = location.hash.match(new RegExp("[#&]" + k + "=([^&]*)"));
    return m ? decodeURIComponent(m[1]) : null;
  }
  function store(k, v) {
    try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; }
    return null;
  }
  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  /* ---------------- 単語帳 ---------------- */
  var table = $("#tango-table");
  if (table) {
    var toggle = $("#toggle-red"), rows = $$("tbody tr", table), pills = $$(".pill[data-area]");
    toggle.addEventListener("click", function () {
      var on = document.body.classList.toggle("hide-red");
      $$(".meaning.shown").forEach(function (e) { e.classList.remove("shown"); });
      toggle.textContent = on ? "赤字を見る" : "赤字をかくす";
      toggle.classList.toggle("o", on);
      toggle.setAttribute("aria-pressed", on ? "true" : "false");
    });
    $$(".meaning").forEach(function (e) {
      e.addEventListener("click", function () {
        if (document.body.classList.contains("hide-red")) e.classList.toggle("shown");
      });
    });
    function filter(area) {
      pills.forEach(function (p) { p.classList.toggle("on", p.getAttribute("data-area") === area); });
      rows.forEach(function (r) { r.hidden = !(area === "0" || r.getAttribute("data-area") === area); });
    }
    pills.forEach(function (p) { p.addEventListener("click", function () { filter(p.getAttribute("data-area")); }); });
    filter(hashParam("area") || "0");

    var KEY = "joho_tango_chk_w" + (window.WEEK || 1), saved = {};
    try { saved = JSON.parse(store(KEY) || "{}"); } catch (e) { saved = {}; }
    var boxes = $$("input[type=checkbox][data-k]");
    boxes.forEach(function (b) {
      b.checked = !!saved[b.getAttribute("data-k")];
      b.addEventListener("change", function () {
        saved[b.getAttribute("data-k")] = b.checked ? 1 : 0;
        store(KEY, JSON.stringify(saved));
      });
    });
    var reset = $("#reset-chk");
    if (reset) reset.addEventListener("click", function () {
      boxes.forEach(function (b) { b.checked = false; });
      saved = {}; store(KEY, "{}");
    });
  }

  /* ---------------- 確認テスト ---------------- */
  var app = $("#kakunin-app");
  if (app && window.KAKUNIN) {
    var DATA = window.KAKUNIN, AREAS = window.AREAS || [];
    var st = { list: [], i: 0, first: {}, missed: [], hist: [], cnt: [0, 0, 0, 0], prevOrder: null, prevId: null, q: null, p: null, sel: null, title: "" };

    // 並びを決める：正解の位置が3回続けて同じにならない／もう一度のときは前と違う並びにする
    function makeOrder(q) {
      var tries = 0, p, pos, h, bad, lo = Math.min.apply(null, st.cnt);
      do {
        p = shuffle([0, 1, 2, 3]); pos = p.indexOf(q.answer); h = st.hist; tries++;
        bad = (h.length >= 2 && h[h.length - 1] === pos && h[h.length - 2] === pos) ||   // 3回続けて同じ位置にしない
              (st.cnt[pos] > lo + 1) ||                                                    // 特定の位置にかたよらせない
              (st.prevId === q.id && st.prevOrder === p.join(""));                         // もう一度は前と違う並び
      } while (bad && tries < 200);
      st.cnt[pos]++; st.hist.push(pos); st.prevOrder = p.join(""); st.prevId = q.id;
      return p;
    }

    var menu = el("div", "menu"), body = el("div", "body");
    app.appendChild(menu); app.appendChild(body);
    var menuBtns = [];
    function group(label, items) {
      var g = el("div", "grp"); g.appendChild(el("b", "", label));
      var box = el("span", "pills");
      items.forEach(function (it) {
        var b = el("button", "pill", it.text); b.type = "button";
        b.addEventListener("click", function () { choose(it); });
        box.appendChild(b); menuBtns.push([b, it]);
      });
      g.appendChild(box); menu.appendChild(g);
    }
    var dayNums = [];
    DATA.forEach(function (q) { if (dayNums.indexOf(q.day) < 0) dayNums.push(q.day); });
    dayNums.sort(function (a, b) { return a - b; });
    var days = dayNums.map(function (d) {
      var l = DATA.filter(function (q) { return q.day === d; });
      return { key: "day" + d, text: d + "日目（" + l.length + "問）", list: l, title: d + "日目" };
    });
    var areaItems = AREAS.map(function (a) {
      var l = DATA.filter(function (q) { return q.area === a.id; });
      return { key: "area" + a.id, text: a.short + "（" + l.length + "問）", list: l, title: "分野" + a.id + "：" + a.name };
    });
    group("日ごと", days.concat([{ key: "all", text: "全部（" + DATA.length + "問）", list: DATA, title: "全部" }]));
    group("分野ごと", areaItems);

    function choose(it) {
      menuBtns.forEach(function (x) { x[0].classList.toggle("on", x[1] === it); });
      start(it.list, it.title);
    }
    function start(list, title) {
      st.list = list.slice(); st.i = 0; st.first = {}; st.missed = []; st.hist = []; st.cnt = [0, 0, 0, 0]; st.title = title; render();
    }

    function render() {
      body.innerHTML = "";
      if (st.i >= st.list.length) return finish();
      var q = st.q = st.list[st.i];
      st.p = makeOrder(q); st.sel = null;

      var head = el("div", "bar");
      var left = el("div");
      left.appendChild(el("span", "tag", q.kind));
      var a = AREAS.filter(function (x) { return x.id === q.area; })[0];
      if (a) left.appendChild(el("span", "tag a" + a.id, a.short));
      head.appendChild(left);
      head.appendChild(el("span", "small", st.title + "　" + (st.i + 1) + " ／ " + st.list.length + " 問"));
      body.appendChild(head);

      var qb = el("div", "qbox");
      if (q.context) qb.appendChild(el("p", "", q.context));
      qb.appendChild(el("p", "", q.stem));
      body.appendChild(qb);

      var btns = [];
      st.p.forEach(function (orig, k) {
        var b = el("button", "ch"); b.type = "button";
        b.appendChild(el("span", "lb", CH[k])); b.appendChild(document.createTextNode(q.choices[orig]));
        b.addEventListener("click", function () {
          if (b.disabled) return;
          btns.forEach(function (x) { x.classList.remove("sel"); });
          b.classList.add("sel"); st.sel = k; go.disabled = false;
        });
        btns.push(b); body.appendChild(b);
      });
      var act = el("div", "grp");
      var go = el("button", "btn o", "答え合わせ"); go.type = "button"; go.disabled = true;
      act.appendChild(go); body.appendChild(act);
      var out = el("div"); body.appendChild(out);

      go.addEventListener("click", function () {
        if (st.sel == null) return;
        var okPos = st.p.indexOf(q.answer), correct = st.sel === okPos;
        btns.forEach(function (b) { b.disabled = true; b.classList.remove("sel"); });
        btns[okPos].classList.add("ok");
        if (!correct) btns[st.sel].classList.add("ng");
        go.hidden = true;
        if (st.first[q.id] === undefined) { st.first[q.id] = correct; if (!correct) st.missed.push(q); }

        var msg = el("p", correct ? "ok-t" : "ng-t", correct ? "正解！" : "ざんねん。解説を読んで、もう一度やってみよう。");
        msg.style.fontSize = "1.15rem"; out.appendChild(msg);
        out.appendChild(explain(q));
        var nav = el("div", "grp");
        if (!correct) {
          var again = el("button", "btn o", "もう一度（選択肢の順番が変わります）"); again.type = "button";
          again.addEventListener("click", render); nav.appendChild(again);
          nav.appendChild(document.createTextNode(" "));
        }
        var next = el("button", correct ? "btn o" : "btn g", correct ? "次の問題へ" : "とばして次へ"); next.type = "button";
        next.addEventListener("click", function () { st.i++; render(); window.scrollTo(0, app.offsetTop); });
        nav.appendChild(next); out.appendChild(nav);
      });
    }

    function explain(q) {
      var d = el("div", "exp");
      d.appendChild(el("h4", "", "解説：" + q.word));
      var ol = el("ol");
      q.steps.forEach(function (s) { ol.appendChild(el("li", "", s)); });
      d.appendChild(ol);
      if (q.fig) {                       // 図（build.py が作ったSVG。自サイトで作った文字列だけを入れる）
        var fb = el("div", "figbox"); fb.innerHTML = q.fig; d.appendChild(fb);
      }
      var t = el("table", "w"), tb = el("tbody");
      var th = el("tr");
      ["選択肢", "判定", "理由"].forEach(function (x) { th.appendChild(el("th", "", x)); });
      t.appendChild(el("thead")).appendChild(th);
      q.choices.forEach(function (c, i) {
        var tr = el("tr"), r = q.rows[i];
        tr.appendChild(el("td", "", c));
        tr.appendChild(el("td", r.mark === "○" ? "ok-t" : "ng-t", r.mark));
        tr.appendChild(el("td", "", r.reason));
        tb.appendChild(tr);
      });
      t.appendChild(tb); d.appendChild(t);
      return d;
    }

    function finish() {
      var n = st.list.length, good = n - st.missed.length;
      body.appendChild(el("p", "score", "できた数　" + good + " ／ " + n));
      body.appendChild(el("p", "small", "（1回目で正解した数です）"));
      if (st.missed.length) {
        body.appendChild(el("p", "", "まちがえた語："));
        var ul = el("ul", "plain");
        st.missed.forEach(function (q) { ul.appendChild(el("li", "", q.word + "（" + q.kind + "）")); });
        body.appendChild(ul);
      } else {
        body.appendChild(el("p", "ok-t", "全問、1回で正解！"));
      }
      var nav = el("div", "grp");
      if (st.missed.length) {
        var re = el("button", "btn o", "まちがえた問題だけやり直す"); re.type = "button";
        re.addEventListener("click", function () { start(st.missed, st.title + "（やり直し）"); });
        nav.appendChild(re); nav.appendChild(document.createTextNode(" "));
      }
      var all = el("button", "btn g", "最初からやり直す"); all.type = "button";
      var keep = st.list.slice(), t0 = st.title;
      all.addEventListener("click", function () { start(keep, t0); });
      nav.appendChild(all); body.appendChild(nav);
    }

    var hd = hashParam("day"), ha = hashParam("area");
    var first = days[0];
    if (hd) first = days.filter(function (x) { return x.key === "day" + hd; })[0] || first;
    if (ha) first = areaItems.filter(function (x) { return x.key === "area" + ha; })[0] || first;
    choose(first);
  }

  /* ---------------- 思考問題（ボタン式） ---------------- */
  var sapp = $("#shikou-app");
  if (sapp && window.SHIKOU) {
    var SD = window.SHIKOU, SKEY = "joho_shikou_w" + (window.WEEK || 1);
    var DIG = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
    var scores = {};
    try { scores = JSON.parse(store(SKEY) || "{}"); } catch (e) { scores = {}; }
    var sm = el("div", "menu"), sb = el("div", "body");
    sapp.appendChild(sm); sapp.appendChild(sb);
    var tabs = [], prevPerm = {}, sday = null;

    function tabText(d) {
      var s = scores[d.day];
      return d.day + "日目" + (s != null ? "（最高 " + s + "／" + d.blanks + "）" : "");
    }
    SD.forEach(function (d) {
      var b = el("button", "pill", tabText(d)); b.type = "button";
      b.addEventListener("click", function () { openDay(d); });
      sm.appendChild(b); tabs.push([b, d]);
    });

    // 解答群ごとに表示の並びを決める：正解の位置が3回続けて同じにならず、同じ位置が3回以上にならない／やり直しは前と違う並び
    function makePerms(d) {
      var names = Object.keys(d.groups), best = null;
      for (var t = 0; t < 400; t++) {
        var perms = {};
        names.forEach(function (g) {
          var n = d.groups[g].options.length, idx = [];
          for (var i = 0; i < n; i++) idx.push(i);
          perms[g] = shuffle(idx);
        });
        var seq = [], cnt = {}, ok = true;
        d.blanks_list.forEach(function (b) {
          if (b.type !== "choice") return;
          var pos = perms[b.group].indexOf(b.answer);
          seq.push(pos); cnt[pos] = (cnt[pos] || 0) + 1;
        });
        for (var k = 2; k < seq.length; k++) if (seq[k] === seq[k - 1] && seq[k] === seq[k - 2]) ok = false;
        for (var p in cnt) if (cnt[p] > 2) ok = false;
        names.forEach(function (g) { if (prevPerm[d.day] && prevPerm[d.day][g] === perms[g].join("")) ok = false; });
        if (ok) { best = perms; break; }
        if (!best) best = perms;
      }
      prevPerm[d.day] = {};
      names.forEach(function (g) { prevPerm[d.day][g] = best[g].join(""); });
      return best;
    }

    function openDay(d) {
      tabs.forEach(function (x) { x[0].classList.toggle("on", x[1] === d); x[0].textContent = tabText(x[1]); });
      sday = d; run(d, false);
    }

    function run(d, retry) {
      sb.innerHTML = "";
      var perms = makePerms(d), ans = {}, spans = {}, rows = {}, graded = false;
      d.blanks_list.forEach(function (b) { spans[b.id] = []; });
      var byId = {}; d.blanks_list.forEach(function (b) { byId[b.id] = b; });

      function shown(b) {          // 空欄に表示する値
        var v = ans[b.id];
        if (v == null) return "　" + b.id + "　";
        return b.type === "digit" ? String(v) : String(perms[b.group].indexOf(v) + 1);
      }
      function refresh(b) { spans[b.id].forEach(function (s) { s.textContent = shown(b); s.classList.toggle("fill", ans[b.id] != null); }); }
      function fill(node, str) {   // 文字列の中の {ア} を空欄ボタンにする
        String(str).split(/(\{.\})/).forEach(function (part) {
          var m = part.match(/^\{(.)\}$/);
          if (m && byId[m[1]]) {
            var b = byId[m[1]], s = el("span", "bl", shown(b));
            s.title = "空欄 " + b.id; s.tabIndex = 0;
            s.addEventListener("click", function () { if (rows[b.id]) { rows[b.id].scrollIntoView({ block: "center", behavior: "smooth" }); rows[b.id].classList.add("flash"); setTimeout(function () { rows[b.id].classList.remove("flash"); }, 900); } });
            spans[b.id].push(s); node.appendChild(s);
          } else if (part) node.appendChild(document.createTextNode(part));
        });
        return node;
      }
      function tableEl(t) {
        var wrap = el("div", "tbwrap"), tb = el("table", "tb");
        if (t.cap) { tb.appendChild(el("caption", "", t.cap)); }
        if (t.head) {
          var hr = el("tr"); t.head.forEach(function (c) { fill(hr.appendChild(el("th")), c); });
          tb.appendChild(el("thead")).appendChild(hr);
        }
        var body = el("tbody");
        t.rows.forEach(function (r) {
          var tr = el("tr"), skip = 0;
          r.forEach(function (c, i) {
            var span = (c && typeof c === "object") ? c.span : 1, txt = (c && typeof c === "object") ? c.text : c;
            var cell = el((i === 0 && t.rowhead) ? "th" : "td");
            if (span > 1) cell.colSpan = span;
            fill(cell, txt); tr.appendChild(cell);
          });
          body.appendChild(tr);
        });
        tb.appendChild(body); wrap.appendChild(tb); return wrap;
      }
      function groupEl(g) {
        var G = d.groups[g], box = el("div", "gbox" + (G.figs ? " figs" : ""));
        box.appendChild(el("b", "gt", G.title));
        var list = el("div", "gl");
        perms[g].forEach(function (orig, k) {
          var o = G.options[orig], it = el("div", "gi");
          it.appendChild(el("span", "gn", String(k + 1)));
          if (o.svg) { var f = el("span", "gf"); f.innerHTML = o.svg; it.appendChild(f); } else it.appendChild(el("span", "", o.t));
          list.appendChild(it);
        });
        box.appendChild(list); return box;
      }

      var bar = el("div", "bar");
      bar.appendChild(el("b", "", d.day + "日目　" + d.title + "　" + d.theme));
      bar.appendChild(el("span", "small", "空欄 " + d.blanks + "か所／約" + d.minutes + "分" + (retry ? "（選択肢の順番を変えました）" : "")));
      sb.appendChild(bar);
      if (d.intro) sb.appendChild(el("div", "qbox")).appendChild(fill(el("p"), d.intro));

      d.parts.forEach(function (p) {
        var box = el("div", "qbox part");
        box.appendChild(el("b", "pl", p.label));
        fill(box.appendChild(el("p")), p.lead);
        p.blocks.forEach(function (bl) {
          if (bl.t === "p") fill(box.appendChild(el("p")), bl.text);
          else if (bl.t === "talk") bl.lines.forEach(function (ln) {
            var r = el("p", "talk"); r.appendChild(el("b", "who", ln[0])); fill(r, ln[1]); box.appendChild(r);
          });
          else if (bl.t === "code") {
            if (bl.cap) box.appendChild(el("div", "cap", bl.cap));
            var pre = el("pre", "code"); bl.lines.forEach(function (l) { fill(pre, l); pre.appendChild(document.createTextNode("\n")); }); box.appendChild(pre);
          }
          else if (bl.t === "table") box.appendChild(tableEl(bl));
          else if (bl.t === "choices") box.appendChild(groupEl(bl.group));
          else if (bl.t === "fig") {
            var fb = el("div", "figbox"); fb.innerHTML = bl.svg; box.appendChild(fb);
            if (bl.cap) box.appendChild(el("div", "cap", bl.cap));
          }
        });
        sb.appendChild(box);
      });

      // 解答欄
      var panel = el("div", "qbox ansp");
      panel.appendChild(el("b", "pl", "解答欄（ボタンを押して答える）"));
      d.blanks_list.forEach(function (b) {
        var r = el("div", "arow"), lab = el("span", "al", b.id); r.appendChild(lab);
        var bs = el("span", "abtn");
        var n = b.type === "digit" ? 10 : d.groups[b.group].options.length, btns = [];
        for (var k = 0; k < n; k++) (function (k) {
          var val = b.type === "digit" ? k : perms[b.group][k];
          var x = el("button", "ab", b.type === "digit" ? String(k) : String(k + 1)); x.type = "button";
          x.addEventListener("click", function () {
            if (graded) return;
            ans[b.id] = val; btns.forEach(function (y) { y.classList.remove("sel"); }); x.classList.add("sel"); refresh(b); upd();
          });
          bs.appendChild(x); btns.push(x);
        })(k);
        r.appendChild(bs); rows[b.id] = r; r._btns = btns; panel.appendChild(r);
      });
      sb.appendChild(panel);

      var act = el("div", "grp"), go = el("button", "btn o", "答え合わせ"); go.type = "button"; go.disabled = true;
      var dk = el("button", "btn g", "わからない（解説を見る）"); dk.type = "button";
      act.appendChild(go); act.appendChild(document.createTextNode(" ")); act.appendChild(dk); sb.appendChild(act);
      var cnt = el("p", "small"); sb.appendChild(cnt);
      var out = el("div"); sb.appendChild(out);
      function upd() {
        var n = d.blanks_list.filter(function (b) { return ans[b.id] != null; }).length;
        cnt.textContent = "答えた数：" + n + " ／ " + d.blanks; go.disabled = n === 0 || graded;
      }
      upd();

      function showExplain(ok) {
        d.explain.forEach(function (e) {
          var open = e.blanks.some(function (id) { return ok ? !ok[id] : true; });
          var det = el("details", "exd"); if (open) det.open = true;
          var sm = el("summary", "", e.title + (ok ? (e.blanks.every(function (id) { return ok[id]; }) ? "　○" : "　×") : ""));
          if (ok) sm.className = e.blanks.every(function (id) { return ok[id]; }) ? "ok-t" : "ng-t";
          det.appendChild(sm);
          var ex = el("div", "exp");
          if (e.organize.length) { ex.appendChild(el("h4", "", "問題の整理")); var u = el("ul"); e.organize.forEach(function (s) { u.appendChild(el("li", "", s)); }); ex.appendChild(u); }
          ex.appendChild(el("h4", "", "解く手順")); var o = el("ol"); e.steps.forEach(function (s) { o.appendChild(el("li", "", s)); }); ex.appendChild(o);
          if (e.table) ex.appendChild(tableEl(e.table));
          var ansl = el("p", "fin"); ansl.appendChild(el("b", "", "答案　")); ansl.appendChild(document.createTextNode(e.final)); ex.appendChild(ansl);
          det.appendChild(ex); out.appendChild(det);
        });
      }
      function finishBtns(next) {
        var nav = el("div", "grp");
        var again = el("button", "btn o", "もう一度（選択肢の順番が変わります）"); again.type = "button";
        again.addEventListener("click", function () { run(d, true); window.scrollTo(0, sapp.offsetTop); });
        nav.appendChild(again); nav.appendChild(document.createTextNode(" "));
        var i = SD.indexOf(d);
        if (next && SD[i + 1]) {
          var nx = el("button", "btn g", (i + 2) + "日目へ"); nx.type = "button";
          nx.addEventListener("click", function () { openDay(SD[i + 1]); window.scrollTo(0, sapp.offsetTop); });
          nav.appendChild(nx);
        }
        out.appendChild(nav);
      }

      go.addEventListener("click", function () {
        graded = true; go.hidden = true; dk.hidden = true; out.innerHTML = "";
        var ok = {};
        d.blanks_list.forEach(function (b) {
          if (b.pool) return;
          ok[b.id] = ans[b.id] === b.answer;
        });
        // 順序を問わない空欄：答えの組が合っていれば正解
        var pools = {};
        d.blanks_list.forEach(function (b) { if (b.pool) { var k = b.pool.join(""); (pools[k] = pools[k] || []).push(b); } });
        Object.keys(pools).forEach(function (k) {
          var bs = pools[k], mine = bs.map(function (b) { return ans[b.id]; }).sort().join(","), key = bs.map(function (b) { return b.answer; }).sort().join(",");
          bs.forEach(function (b) { ok[b.id] = mine === key; });
        });
        var good = 0;
        d.blanks_list.forEach(function (b) {
          if (ok[b.id]) good++;
          rows[b.id].classList.add(ok[b.id] ? "ok" : "ng");
          rows[b.id]._btns.forEach(function (x) { x.disabled = true; });
          if (!ok[b.id]) {                       // 正しい答えを示す
            var ca = b.type === "digit" ? b.answer : perms[b.group].indexOf(b.answer);
            rows[b.id]._btns[ca].classList.add("right");
          }
        });
        if (scores[d.day] == null || good > scores[d.day]) { scores[d.day] = good; store(SKEY, JSON.stringify(scores)); }
        tabs.forEach(function (x) { x[0].textContent = tabText(x[1]); });
        out.appendChild(el("p", "score", "できた数　" + good + " ／ " + d.blanks));
        out.appendChild(el("p", good === d.blanks ? "ok-t" : "ng-t", good === d.blanks ? "全部正解！" : "まちがえた所の解説を開いています。読んでから、もう一度やってみよう。"));
        showExplain(ok); finishBtns(true);
        out.firstChild.scrollIntoView({ behavior: "smooth", block: "start" });
      });
      dk.addEventListener("click", function () {
        graded = true; go.hidden = true; dk.hidden = true; out.innerHTML = "";
        out.appendChild(el("p", "", "解説です。手順をなぞってから、もう一度やってみよう。"));
        showExplain(null); finishBtns(false);
      });
    }
    var hd2 = hashParam("day");
    openDay(SD.filter(function (x) { return String(x.day) === hd2; })[0] || SD[0]);
  }
})();
