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
})();
