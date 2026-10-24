/* RSS 订阅文章（首页「常用网页集」下方） */
(function () {
  var listEl = document.getElementById("rssList");
  var updatedEl = document.getElementById("rssUpdated");
  if (!listEl) return;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  fetch("assets/rss.json?v=" + Date.now(), { cache: "no-store" })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var items = data && data.items ? data.items : [];
      if (!items.length) throw new Error("empty");
      listEl.innerHTML = items
        .map(function (it) {
          return (
            '<li class="rss-item">' +
              '<a class="rss-link" href="' + esc(it.url) + '" target="_blank" rel="noopener">' +
                '<span class="rss-source">' + esc(it.source) + "</span>" +
                '<span class="rss-title">' + esc(it.title) + "</span>" +
              "</a>" +
              '<span class="rss-date">' + esc(it.date) + "</span>" +
            "</li>"
          );
        })
        .join("");
      if (updatedEl) {
        updatedEl.textContent =
          "订阅源：" + (data.sources || []).join(" · ") + " · 更新于 " + (data.updated || "--");
      }
    })
    .catch(function () {
      listEl.innerHTML = '<li class="rss-item rss-error">RSS 文章加载失败，稍后再来看看。</li>';
      if (updatedEl) updatedEl.textContent = "";
    });
})();
