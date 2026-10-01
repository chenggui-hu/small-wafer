# small-wafer

硅基火花 · 半导体工程师 · 个人主页

- 网址：https://chenggui-hu.github.io/small-wafer
- 工具页：https://chenggui-hu.github.io/small-wafer/tools.html
- 托管：GitHub Pages（纯静态，无需构建）

## 目录结构

```
small-wafer/
├── index.html        # 首页（含「全网热搜」板块）
├── articles.html     # 半导体（公众号文章合集）
├── tools.html        # 常用软件集
├── webapps.html      # 常用网页集
├── social.html       # 关注我
├── css/style.css     # 样式（含热榜通用样式）
├── js/main.js        # 全站交互（导航 / 音乐 / 倒计时 / 搜索 / 文章列表）
├── js/home-hot.js    # 首页「全网热搜」脚本（小红书 / 知乎 / V2EX）
├── scripts/          # 数据抓取脚本
│   ├── fetch_articles.py  # 公众号文章 → assets/articles.json
│   └── fetch_v2ex.py      # V2EX 热帖 → assets/v2ex.json
├── README.md
└── assets/
    ├── hero-bg.jpg   # 首页背景图
    ├── avatar.jpg    # small wafer 头像
    ├── wechat-qr.png # 微信公众号二维码
    ├── articles.json # 公众号文章数据
    ├── v2ex.json     # V2EX 热帖数据
    └── bgm.mp3       # 背景音乐（曲1）
```

## 我想改内容，怎么动？

### 首页 `index.html`

- **座右铭**：hero 区 `hero-motto`
- **搜索框**：hero 区 `hero-search`（公众号搜索 / Sci-Hub 双模式）
- **全网热搜**：`#hot` 区块，小红书 + 知乎 + V2EX 三栏
  - 小红书、知乎：由 `js/home-hot.js` 前端实时抓取（60s API，CORS 开放）
  - V2EX：读取 `assets/v2ex.json`（V2EX 无 CORS 且国内直连超时，改由脚本生成）
  - 想增删平台：编辑 `js/home-hot.js` 里的 `SOURCES` 数组
  - 手动刷新 V2EX 数据：`python scripts/fetch_v2ex.py 10`，然后 `git push`
  - 已配定时任务，每 3 小时自动刷新 V2EX 数据并推送

### 半导体 `articles.html`

- 公众号「硅基火花」文章合集（原本在首页，现独立成页，导航名「半导体」）
- 数据来自 `assets/articles.json`，由 `scripts/fetch_articles.py` 抓取（已配每周定时任务）
- 手动更新：`python scripts/fetch_articles.py 硅基火花 6`，然后 `git push`

### 工具页 `tools.html`

- 常用软件集内容都在这里改

### 导航音乐

- 曲目 1/2/3 对应 `assets/bgm.mp3` / `bgm-2.mp3` / `bgm-3.mp3`
- 鼠标悬停导航栏的音乐按钮展开曲目列表

### 倒计时

- 自动显示当天日期与「今年剩余 X 天」，无需手动改

## 本地预览

```bash
python -m http.server 8000
# 浏览器打开 http://localhost:8000
```

## 推送到 GitHub

```bash
cd "C:/Users/chenggui/WorkBuddy/Skill/small-wafer"
git add .
git commit -m "更新说明"
git push
```

约 1–2 分钟后，网站自动更新。
