# small-wafer

硅基火花 · 半导体工程师的个人主页

- 网址（开启 Pages 后）：https://blackhacher.github.io/small-wafer
- 托管：GitHub Pages（纯静态，无需构建）

## 目录结构

```
small-wafer/
├── index.html       # 页面结构（所有内容都在这里改）
├── css/style.css    # 样式（含 hero 背景图设置）
├── js/main.js       # 滚动渐显 + 导航高亮 + 背景音乐按钮
├── assets/
│   ├── hero-bg.jpg     # 英雄区背景图（已就位）
│   ├── bgm.mp3         # 可选：背景音乐
│   └── wechat-qr.png   # 可选：公众号二维码
└── README.md
```

## 区块一览（导航顺序）

1. **关于** `#about` — 个人简介 + 技能坐标
2. **文章** `#articles` — 微信公众号文章列表（每篇：日期 + 标题 + 摘要 + 跳转）
3. **工具** `#tools` — 常用软件集（桌面软件卡片，点击直达官网）
4. **网页** `#webapps` — 常用网页集（在线工具与平台，按分类整理）
5. **关注** `#social` — 微信公众号（带二维码位）、小红书、B 站

## 我想改内容，怎么动？

全部内容都在 `index.html` 里，搜索对应中文区块即可：

- **关于我**：`#about` 区块的 `<p>` 文案与技能标签
- **公众号文章**：`#articles` 区块
  - 每篇：`<time class="article-date">` 改日期，`<h3>` 改标题，`<p>` 改摘要，`href="#"` 换成公众号文章链接
  - 新增：复制 `<article class="article">…</article>` 块
- **常用软件集**：`#tools` 区块
  - 每个 `<a class="tool-card">` 改 emoji、名称、描述、官网链接
  - 删/新增：直接复制或删除整张卡片
- **常用网页集**：`#webapps` 区块，按分类改 `<div class="webapp-group">…</div>`
- **关注我**：`#social` 区块
  - 微信公众号：`href="#"` 换成公众号主页；二维码图片命名为 `wechat-qr.png` 放到 `assets/`
  - 小红书 / B 站：换链接
- **背景音乐**：把音频命名为 `bgm.mp3` 放进 `assets/`，右下角 🎵 按钮可播放/暂停
- **背景图**：替换 `assets/hero-bg.jpg` 即可，CSS 里直接引用

改完直接 `git push`（或在 GitHub 网页上编辑提交），Pages 会自动更新。

## 开启 GitHub Pages

仓库 → Settings → Pages → Source 选 `Deploy from a branch` → Branch 选 `main` / `/ (root)` → Save。
约 1–2 分钟后网站上线。

## 本地预览

```bash
# 任选其一，在仓库根目录起一个本地服务器
python -m http.server 8000
# 然后浏览器打开 http://localhost:8000
```