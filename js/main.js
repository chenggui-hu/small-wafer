// small-wafer 个人主页 · 交互脚本
// 1) 导航高亮
// 2) 滚动渐显
// 3) 导航音乐播放器
// 4) 今年剩余天数倒计时

(function () {
  "use strict";

  // ---- 滚动渐显 ----
  var revealEls = document.querySelectorAll(".section, .article, .webapp-group, .about-card, .social-card, .tool-category");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    revealEls.forEach(function (el) {
      el.classList.add("reveal");
      io.observe(el);
    });
  }

  // ---- 导航高亮 ----
  var sections = document.querySelectorAll("section[id]");
  var navLinks = document.querySelectorAll(".nav-links a[href]");
  var currentPath = window.location.pathname;

  // 当前页面高亮（tools.html 等子页面）
  navLinks.forEach(function (a) {
    var href = a.getAttribute("href");
    if (!href) return;
    if (href.indexOf(".html") > -1) {
      if (currentPath.indexOf(href) > -1) {
        a.classList.add("active");
      }
    }
  });

  // 滚动区块高亮
  if ("IntersectionObserver" in window && sections.length) {
    var navIo = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var id = entry.target.getAttribute("id");
            navLinks.forEach(function (a) {
              var href = a.getAttribute("href") || "";
              a.classList.toggle("active", href === "#" + id);
            });
          }
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach(function (s) { navIo.observe(s); });
  }

  // ---- 导航下拉菜单（点击展开，点击外部关闭） ----
  var drops = document.querySelectorAll(".nav-drop");
  drops.forEach(function (drop) {
    var btn = drop.querySelector(".nav-drop-btn");
    if (!btn) return;
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      drops.forEach(function (d) {
        if (d !== drop) d.classList.remove("open");
      });
      drop.classList.toggle("open");
    });
    drop.querySelectorAll(".nav-drop-menu a").forEach(function (link) {
      link.addEventListener("click", function () {
        drop.classList.remove("open");
      });
    });
  });
  document.addEventListener("click", function () {
    drops.forEach(function (d) { d.classList.remove("open"); });
  });

  // ---- 倒计时 ----
  function updateCountdown() {
    var now = new Date();
    var year = now.getFullYear();
    var endOfYear = new Date(year, 11, 31, 23, 59, 59);
    var diff = endOfYear - now;
    var days = Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
    var month = now.getMonth() + 1;
    var date = now.getDate();
    var dateStr = (month < 10 ? "0" : "") + month + "/" + (date < 10 ? "0" : "") + date;

    var countdownEl = document.getElementById("navCountdown");
    if (countdownEl) {
      var dateSpan = countdownEl.querySelector(".countdown-date");
      var daysSpan = countdownEl.querySelector(".countdown-days");
      if (dateSpan) dateSpan.textContent = dateStr;
      if (daysSpan) daysSpan.textContent = year + " 还剩 " + days + " 天";
    }
  }
  updateCountdown();
  setInterval(updateCountdown, 60000);

  // ---- 导航音乐播放器 ----
  var bgm = document.getElementById("bgm");
  var musicToggle = document.getElementById("navMusicToggle");
  var musicMenu = document.getElementById("navMusicMenu");
  var musicTracks = document.querySelectorAll(".nav-music-track");

  if (bgm && musicToggle && musicTracks.length) {
    var currentSrc = "";
    var playing = false;

    function selectTrack(btn) {
      var src = btn.getAttribute("data-src");
      if (!src) return;

      if (currentSrc !== src) {
        bgm.pause();
        bgm.src = src;
        currentSrc = src;
        bgm.load();
        playing = false;
      }

      musicTracks.forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");

      var p = bgm.play();
      if (p && p.catch) {
        p.catch(function () {
          playing = false;
          updateMusicUI();
        });
      }
      playing = true;
      updateMusicUI();
    }

    function updateMusicUI() {
      musicToggle.textContent = playing ? "⏸" : "▶";
      musicToggle.classList.toggle("playing", playing);
    }

    musicTracks.forEach(function (btn) {
      btn.addEventListener("click", function () { selectTrack(btn); });
    });

    musicToggle.addEventListener("click", function () {
      if (!currentSrc && musicTracks.length) {
        selectTrack(musicTracks[0]);
        return;
      }
      if (playing) {
        bgm.pause();
        playing = false;
      } else {
        var p = bgm.play();
        if (p && p.catch) {
          p.catch(function () { playing = false; });
        }
        playing = true;
      }
      updateMusicUI();
    });

    bgm.addEventListener("ended", function () {
      playing = false;
      updateMusicUI();
    });

    // 移动端：点击 toggle 也展开菜单
    musicToggle.addEventListener("mouseenter", function () {
      if (musicMenu) musicMenu.classList.add("open");
    });
    if (musicMenu) {
      musicMenu.addEventListener("mouseleave", function () {
        musicMenu.classList.remove("open");
      });
    }
  }

  // ---- Hero 搜索框（公众号 / Sci-Hub） ----
  var searchForm = document.getElementById("heroSearch");
  if (searchForm) {
    var searchMode = "wechat";
    var searchInput = document.getElementById("searchInput");
    var tabs = searchForm.parentElement.querySelectorAll(".search-tab");

    var placeholders = {
      wechat: "输入关键词，搜索微信公众号文章",
      scihub: "输入 DOI（如 10.1038/s41586-020-2649-2）"
    };

    // Sci-Hub 镜像列表：后台提前探测，结果缓存；提交时同步打开窗口（避免弹窗拦截产生 about:blank）
    var sciHubMirrors = [
      "https://sci-hub.ren/",
      "https://sci-hub.ee/",
      "https://sci-hub.wf/",
      "https://sci-hub.se/"
    ];
    var sciHubBase = sciHubMirrors[0]; // 默认镜像，探测成功后更新
    var sciHubProbed = false;

    function probeMirror(base) {
      return new Promise(function (resolve) {
        var settled = false;
        var timer = setTimeout(function () { if (!settled) { settled = true; resolve(false); } }, 4000);
        fetch(base, { mode: "no-cors", cache: "no-store" })
          .then(function () { if (!settled) { settled = true; clearTimeout(timer); resolve(true); } })
          .catch(function () { if (!settled) { settled = true; clearTimeout(timer); resolve(false); } });
      });
    }

    function probeSciHub() {
      if (sciHubProbed) return;
      sciHubProbed = true;
      (function next(idx) {
        if (idx >= sciHubMirrors.length) return; // 全部失败则保留默认
        probeMirror(sciHubMirrors[idx]).then(function (ok) {
          if (ok) { sciHubBase = sciHubMirrors[idx]; }
          else { next(idx + 1); }
        });
      })(0);
    }

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        tabs.forEach(function (t) { t.classList.remove("active"); });
        tab.classList.add("active");
        searchMode = tab.getAttribute("data-mode");
        searchInput.placeholder = placeholders[searchMode];
        if (searchMode === "scihub") { probeSciHub(); } // 切到 Sci-Hub 时后台探测
        searchInput.focus();
      });
    });

    searchForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var q = searchInput.value.trim();
      if (!q) { searchInput.focus(); return; }
      var url;
      if (searchMode === "scihub") {
        // 同步打开，保证不被弹窗拦截；镜像用后台探测的缓存结果
        url = sciHubBase + q.replace(/\s+/g, "");
      } else {
        // 搜狗微信搜索：type=2 文章
        url = "https://weixin.sogou.com/weixin?type=2&query=" + encodeURIComponent(q);
      }
      window.open(url, "_blank", "noopener");
    });
  }

  // ---- 公众号文章列表：加载 assets/articles.json 动态渲染 ----
  var articleList = document.getElementById("articleList");
  if (articleList) {
    function esc(s) {
      return String(s || "").replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
      });
    }
    fetch("assets/articles.json", { cache: "no-store" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (articles) {
        if (!Array.isArray(articles) || !articles.length) return;
        articleList.innerHTML = articles.map(function (a) {
          var thumb = a.thumb
            ? '<img class="article-thumb" src="' + esc(a.thumb) + '" alt="" loading="lazy" referrerpolicy="no-referrer" />'
            : "";
          var meta = '<div class="article-meta"><span>' + esc(a.account || "硅基火花") + "</span>" +
            (a.date ? "<span>" + esc(a.date) + "</span>" : "") + "</div>";
          return '<article class="article-item">' +
            '<div class="article-body">' +
            '<h3><a href="' + esc(a.url) + '" target="_blank" rel="noopener">' + esc(a.title) + "</a></h3>" +
            (a.digest ? '<p class="article-digest">' + esc(a.digest) + "</p>" : "") +
            meta + "</div>" + thumb + "</article>";
        }).join("");
      })
      .catch(function () { /* 加载失败保留兜底内容 */ });
  }
})();
