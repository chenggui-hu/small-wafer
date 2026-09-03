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
})();
