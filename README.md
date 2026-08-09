# small-wafer

硅基火花 · 半导体工程师 · 个人主页

- 网址：https://chenggui-hu.github.io/small-wafer
- 工具页：https://chenggui-hu.github.io/small-wafer/tools.html
- 托管：GitHub Pages（纯静态，无需构建）

## 目录结构

```
small-wafer/
├── index.html        # 首页
├── tools.html        # 常用软件集页面
├── css/style.css     # 样式
├── js/main.js        # 交互脚本
├── README.md
└── assets/
    ├── hero-bg.jpg   # 首页背景图
    ├── avatar.jpg    # small wafer 头像
    ├── wechat-qr.png # 微信公众号二维码
    └── bgm.mp3       # 背景音乐（曲1）
```

## 我想改内容，怎么动？

### 首页 `index.html`

- **座右铭**：hero 区 `hero-motto`
- **技能坐标**：`#about` 区块的 `.skill-groups`，按「专业 / 掌握 / 特长」分组
- **公众号文章**：`#articles` 区块，改标题、链接
- **常用网页集**：`#webapps` 区块
- **关注我**：`#social` 区块，换二维码 / 公众号链接

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
