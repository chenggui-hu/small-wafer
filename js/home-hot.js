// small-wafer 首页「全网热搜」板块
// 数据源：
//   小红书 / 知乎 —— 60s API（CORS 开放，浏览器可直连，实时）
//   V2EX       —— assets/v2ex.json（V2EX 无 CORS 且国内直连超时，由脚本定时生成）

(function () {
  "use strict";

  // 60s API 公共实例（主域名优先，失败自动切换）
  var INSTANCES = [
    "https://60s.viki.moe",
    "https://60api.09cdn.xyz",
    "https://60s.zeabur.app",
    "https://60s.crystelf.top",
    "https://cqxx.site",
    "https://api.elysiayanyu.top",
    "https://60s.tmini.net",
    "https://60s.7se.cn",
    "https://60s.mizhoubaobei.top",
    "https://api.cczo.cc/60s",
    "https://60s.zellon.top",
    "https://60s.okbaike.com"
  ];

  var SOURCES = [
    { key: "rednote", name: "小红书", icon: "📕", color: "#ff2442", path: "/v2/rednote" },
    { key: "zhihu",   name: "知乎",   icon: "🔵", color: "#0084ff", path: "/v2/zhihu" },
    { key: "v2ex",    name: "V2EX",   icon: "🟫", color: "#778087", local: "assets/v2ex.json" }
  ];

  var TOP_N = 10;
  var TIMEOUT = 10000;

  var board = document.getElementById("hotBoard");
  if (!board) return;
  var updatedEl = document.getElementById("hotUpdated");
  var refreshBtn = document.getElementById("hotRefresh");

  var state = {};
  var activeBase = null;
  var basePromise = null;

  // ---------- 工具 ----------
  function delay(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  function fetchJSON(url, ms) {
    var ctrl = ("AbortController" in window) ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, ms || TIMEOUT);
    return fetch(url, { cache: "no-store", signal: ctrl ? ctrl.signal : undefined })
      .then(function (r) {
        clearTimeout(timer);
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .catch(function (e) { clearTimeout(timer); throw e; });
  }

  function fmtHot(n) {
    n = Number(n) || 0;
    if (n >= 100000000) return (n / 100000000).toFixed(1).replace(/\.0$/, "") + "亿";
    if (n >= 10000) return (n / 10000).toFixed(1).replace(/\.0$/, "") + "w";
    return String(n);
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function searchLink(key, title) {
    var q = encodeURIComponent(title || "");
    if (key === "rednote") return "https://www.xiaohongshu.com/search_result?keyword=" + q + "&type=51";
    if (key === "zhihu") return "https://www.zhihu.com/search?type=content&q=" + q;
    return "https://www.baidu.com/s?wd=" + q;
  }

  // ---------- 实例探测 ----------
  function resolveBase() {
    if (basePromise) return basePromise;
    basePromise = new Promise(function (resolve) {
      (function next(i) {
        if (i >= INSTANCES.length) { resolve(null); return; }
        fetchJSON(INSTANCES[i] + "/v2/rednote", 6000)
          .then(function () { resolve(INSTANCES[i]); })
          .catch(function () { next(i + 1); });
      })(0);
    });
    return basePromise;
  }

  // ---------- 归一化 ----------
  function normalize(src, payload) {
    var arr = src.local
      ? ((payload && payload.items) || [])
      : ((payload && payload.data) || []);
    var out = [];
    for (var i = 0; i < arr.length && out.length < TOP_N; i++) {
      var it = arr[i] || {};
      var title = it.title || it.name || "";
      if (!title) continue;
      var hot = "", badge = "", link = "";
      if (src.local) {
        link = it.url || "";
        badge = it.node || "";
        hot = (it.replies != null) ? (it.replies + " 回复") : "";
      } else {
        var h = it.score_desc || it.hot_value_desc || it.score || it.hot_value || "";
        if (typeof h === "number") h = fmtHot(h);
        hot = h ? String(h) : "";
        badge = (it.word_type && it.word_type !== "无") ? it.word_type : "";
        link = it.link || it.url || searchLink(src.key, title);
      }
      out.push({ rank: it.rank || (out.length + 1), title: title, hot: hot, badge: badge, link: link });
    }
    return out;
  }

  function loadSource(src, force) {
    if (!force && state[src.key] && state[src.key].items) return Promise.resolve();
    state[src.key] = { loading: true };

    var req;
    if (src.local) {
      req = fetchJSON(src.local + "?t=" + Date.now(), TIMEOUT);
    } else {
      req = resolveBase().then(function (base) {
        if (!base) throw new Error("no-instance");
        activeBase = base;
        return fetchJSON(base + src.path, TIMEOUT).catch(function () {
          return delay(1200).then(function () { return fetchJSON(base + src.path, TIMEOUT); });
        });
      });
    }

    return req.then(function (payload) {
      var items = normalize(src, payload);
      if (!items.length) throw new Error("empty");
      state[src.key] = { items: items, updated: payload && payload.updated };
    }).catch(function () {
      state[src.key] = { error: true };
    });
  }

  // ---------- 渲染 ----------
  function makeCol(src, entry) {
    var col = document.createElement("section");
    col.className = "hot-col";

    var head = document.createElement("div");
    head.className = "hot-col-head";
    head.innerHTML = '<span class="dot" style="background:' + src.color + '"></span>' +
      esc(src.icon + " " + src.name) +
      '<span class="count">' + (entry && entry.items ? entry.items.length + " 条" : "") + "</span>";
    col.appendChild(head);

    if (!entry || entry.loading) {
      var sk = document.createElement("div");
      sk.className = "hot-skeleton";
      sk.innerHTML = "<i></i><i></i><i></i><i></i><i></i>";
      col.appendChild(sk);
      return col;
    }

    if (entry.error) {
      var msg = document.createElement("div");
      msg.className = "hot-msg";
      msg.textContent = "暂时获取不到，稍后重试";
      col.appendChild(msg);
      return col;
    }

    var ul = document.createElement("ul");
    ul.className = "hot-list";
    entry.items.forEach(function (it) {
      var li = document.createElement("li");
      var rankCls = it.rank === 1 ? " top1" : it.rank === 2 ? " top2" : it.rank === 3 ? " top3" : "";
      var sub = "";
      if (it.badge) sub += '<span class="hot-badge">' + esc(it.badge) + "</span>";
      if (it.hot) sub += '<span class="hot-hot">' + esc(it.hot) + "</span>";
      li.innerHTML =
        '<a class="hot-item" href="' + esc(it.link) + '" target="_blank" rel="noopener">' +
        '<span class="hot-rank' + rankCls + '">' + it.rank + "</span>" +
        '<span class="hot-body"><span class="hot-title">' + esc(it.title) + "</span>" +
        (sub ? '<span class="hot-sub">' + sub + "</span>" : "") +
        "</span></a>";
      ul.appendChild(li);
    });
    col.appendChild(ul);
    return col;
  }

  function render() {
    board.innerHTML = "";
    SOURCES.forEach(function (s) { board.appendChild(makeCol(s, state[s.key])); });
  }

  function stamp() {
    var d = new Date();
    function pad(n) { return (n < 10 ? "0" : "") + n; }
    if (updatedEl) updatedEl.textContent = "更新于 " + pad(d.getHours()) + ":" + pad(d.getMinutes());
  }

  function loadAll(force) {
    var i = 0;
    function step() {
      if (i >= SOURCES.length) return Promise.resolve();
      var s = SOURCES[i++];
      return loadSource(s, force).then(function () {
        render();
        return delay(200).then(step);
      });
    }
    return step();
  }

  // ---------- 启动 ----------
  render();
  loadAll(false).then(function () { stamp(); render(); });

  if (refreshBtn) {
    refreshBtn.addEventListener("click", function () {
      refreshBtn.classList.add("spin");
      basePromise = null;
      loadAll(true).then(function () {
        stamp();
        render();
        refreshBtn.classList.remove("spin");
      });
    });
  }
})();
