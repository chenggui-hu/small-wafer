// small-wafer 个人主页 · 交互脚本
// 1) 导航高亮：滚动到对应区块时高亮菜单
// 2) 滚动渐显：区块进入视口时淡入

(function () {
  "use strict";

  // ---- 滚动渐显 ----
  var revealEls = document.querySelectorAll(".section, .article, .tool-card, .webapp-group, .about-card, .social-card");
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
  var navLinks = document.querySelectorAll(".nav-links a[href^='#']");
  if ("IntersectionObserver" in window && sections.length) {
    var navIo = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var id = entry.target.getAttribute("id");
            navLinks.forEach(function (a) {
              a.classList.toggle("active", a.getAttribute("href") === "#" + id);
            });
          }
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach(function (s) { navIo.observe(s); });
  }

  // ---- 背景音乐开关 ----
  var bgm = document.getElementById("bgm");
  var musicBtn = document.getElementById("musicBtn");
  if (bgm && musicBtn) {
    var playing = false;
    musicBtn.addEventListener("click", function () {
      if (playing) {
        bgm.pause();
        musicBtn.classList.remove("playing");
      } else {
        var p = bgm.play();
        if (p && p.catch) {
          p.catch(function () {
            // 浏览器可能因缺少音频文件或自动播放策略而拒绝，静默处理
            musicBtn.classList.remove("playing");
          });
        }
        musicBtn.classList.add("playing");
      }
      playing = !playing;
    });
  }
})();
