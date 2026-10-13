// small-wafer 首页「半导体新闻」板块
// 数据源：assets/fabnews.json —— 由 scripts/fetch_fabnews.py 抓取生成，
// 每周一 07:00 自动更新（合并于「每周一早7点抓取公众号文章并更新网站」定时任务）。
// 新闻源：SemiEngineering / EE Times / IEEE Spectrum / SemiWiki 的 RSS 聚合。

(function () {
  "use strict";

  var SRC = "assets/fabnews.json";
  var board = document.getElementById("hotBoard");
  if (!board) return;
  var updatedEl = document.getElementById("hotUpdated");
  var refreshBtn = document.getElementById("hotRefresh");

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function skeleton() {
    return '<div class="hot-skeleton"><i></i><i></i><i></i><i></i><i></i></div>';
  }

  function render(payload, err) {
    board.className = "hot-board single";
    board.innerHTML = "";

    var col = document.createElement("section");
    col.className = "hot-col";

    var head = document.createElement("div");
    head.className = "hot-col-head";
    head.innerHTML = '<span class="dot" style="background:#0ea5a4"></span>📡 Fab 技术动态' +
      '<span class="count">' + (payload && payload.items ? payload.items.length + " 条" : "") + "</span>";
    col.appendChild(head);

    if (err || !payload || !payload.items || !payload.items.length) {
      var msg = document.createElement("div");
      msg.className = "hot-msg";
      msg.textContent = "暂时获取不到，稍后重试";
      col.appendChild(msg);
      board.appendChild(col);
      return;
    }

    var ul = document.createElement("ul");
    ul.className = "hot-list";
    payload.items.forEach(function (it) {
      var li = document.createElement("li");
      var rankCls = it.rank === 1 ? " top1" : it.rank === 2 ? " top2" : it.rank === 3 ? " top3" : "";
      var sub = "";
      if (it.source) sub += '<span class="hot-badge">' + esc(it.source) + "</span>";
      if (it.date) sub += '<span class="hot-hot">' + esc(it.date) + "</span>";
      li.innerHTML =
        '<a class="hot-item" href="' + esc(it.url) + '" target="_blank" rel="noopener">' +
        '<span class="hot-rank' + rankCls + '">' + (it.rank || "") + "</span>" +
        '<span class="hot-body"><span class="hot-title">' + esc(it.title) + "</span>" +
        (sub ? '<span class="hot-sub">' + sub + "</span>" : "") +
        "</span></a>";
      ul.appendChild(li);
    });
    col.appendChild(ul);
    board.appendChild(col);
  }

  function stamp(payload) {
    if (!updatedEl) return;
    var t = payload && payload.updated ? payload.updated : "";
    updatedEl.textContent = "更新于 " + (t || "—") + " · 每周一 07:00 自动抓取";
  }

  function load() {
    board.innerHTML = skeleton();
    fetch(SRC + "?t=" + Date.now(), { cache: "no-store" })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (payload) {
        render(payload, false);
        stamp(payload);
      })
      .catch(function () {
        render(null, true);
        stamp(null);
      });
  }

  // ---------- 启动 ----------
  load();

  if (refreshBtn) {
    refreshBtn.addEventListener("click", function () {
      refreshBtn.classList.add("spin");
      load();
      setTimeout(function () { refreshBtn.classList.remove("spin"); }, 800);
    });
  }
})();
