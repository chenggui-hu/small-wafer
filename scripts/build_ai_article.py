# -*- coding: utf-8 -*-
"""把 _codex_article.md 转成 HTML 写入 ai.html，并改 AI 页标题为商店"""
import io, re

MD = r"C:\Users\chenggui\WorkBuddy\Skill\small-wafer\scripts\_codex_article.md"
AI = r"C:\Users\chenggui\WorkBuddy\Skill\small-wafer\ai.html"

md = io.open(MD, encoding="utf-8").read()
lines = md.split("\n")


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(t):
    # 加粗 **x** -> <strong>
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(t))


# 解析 markdown -> (h1 sections)
sections = []  # {title, blocks:[(kind, content)]}
cur = {"title": None, "blocks": []}
for raw in lines:
    line = raw.rstrip()
    if not line.strip():
        continue
    if line.startswith("## "):
        cur["blocks"].append(("h4", line[3:].strip()))
    elif line.startswith("# "):
        if cur["title"] is not None:
            sections.append(cur)
        cur = {"title": line[2:].strip(), "blocks": []}
    elif line.startswith("> "):
        cur["blocks"].append(("p", line[2:].strip()))
    elif line.startswith("- "):
        if cur["blocks"] and cur["blocks"][-1][0] == "ul":
            cur["blocks"][-1][1].append(line[2:].strip())
        else:
            cur["blocks"].append(("ul", [line[2:].strip()]))
    elif re.match(r"^\d+\. ", line):
        item = re.sub(r"^\d+\. ", "", line).strip()
        if cur["blocks"] and cur["blocks"][-1][0] == "ul":
            cur["blocks"][-1][1].append(item)
        else:
            cur["blocks"].append(("ul", [item]))
    else:
        cur["blocks"].append(("p", line.strip()))
if cur["title"] is not None:
    sections.append(cur)

print("sections:", len(sections))

# 生成 HTML
parts = []
for sec in sections:
    inner = []
    for kind, content in sec["blocks"]:
        if kind == "h4":
            inner.append("      <h4>" + inline(content) + "</h4>")
        elif kind == "p":
            inner.append("      <p>" + inline(content) + "</p>")
        elif kind == "ul":
            inner.append("      <ul class=\"doc-list\">")
            for it in content:
                inner.append("        <li>" + inline(it) + "</li>")
            inner.append("      </ul>")
    parts.append(
        "    <div class=\"doc-section\" id=\"codex-sec\">\n"
        "      <h3>" + inline(sec["title"]) + "</h3>\n"
        + "\n".join(inner) + "\n    </div>"
    )

article_html = (
    "  <!-- Codex 长文 -->\n"
    "  <section class=\"section section-alt\" id=\"codex\">\n"
    "    <div class=\"section-head\">\n"
    "      <span class=\"section-kicker\">AI NOTES</span>\n"
    "      <h2>Codex 从入门到精通</h2>\n"
    "    </div>\n"
    "    <p class=\"section-lead\">万字长文，从界面、任务、权限到 Skills / MCP / Automation 的完整学习路径。</p>\n"
    "    <div class=\"doc-src\">原文来自 X（推特）<a href=\"https://x.com/miles_mazy\" target=\"_blank\" rel=\"noopener\">@miles_mazy</a>"
    "《<a href=\"https://x.com/miles_mazy/status/2091339513134010554\" target=\"_blank\" rel=\"noopener\">万字长文｜Codex 从入门到精通</a>》（2026-08-23），本页全文转载，版权归原作者所有。</div>\n"
    + "\n".join(parts) + "\n"
    "  </section>"
)

s = io.open(AI, encoding="utf-8").read()

# 1) 标题区改成商店
old_head = """    <div class="section-head">
      <span class="section-kicker">AI</span>
      <h2>AI</h2>
    </div>
    <p class="section-lead">常用的 AI 工具、提示词与实践心得。</p>"""
new_head = """    <div class="section-head">
      <span class="section-kicker">AI SHOP</span>
      <h2>AI 会员与数字卡密商店</h2>
    </div>
    <p class="section-lead">AI 会员与数字卡密行情参考，随汇率与渠道波动。</p>"""
assert old_head in s, "section head not found"
s = s.replace(old_head, new_head)

# 2) 标题栏与描述同步
s = s.replace("<title>AI | 硅基火花 · chengguihu</title>",
              "<title>AI 会员与数字卡密商店 | chengguihu</title>")
s = s.replace('<meta name="description" content="常用的 AI 工具、提示词与实践心得。" />',
              '<meta name="description" content="AI 会员与数字卡密行情参考，附 Codex 从入门到精通万字笔记。" />')
s = s.replace("<p class=\"hero-motto\">AI 工具与使用笔记。</p>",
              "<p class=\"hero-motto\">AI 会员与数字卡密商店。</p>")

# 3) 追加文章样式
style_anchor = "    .ai-price-note { color: var(--ink-soft); font-size: 0.8rem; }"
doc_css = style_anchor + """

    /* Codex 长文排版 */
    .doc-section {
      background: var(--surface); border: 1px solid var(--line);
      border-radius: var(--radius); box-shadow: var(--shadow);
      padding: 26px 30px; margin-bottom: 22px;
    }
    .doc-section > h3 {
      margin: 0 0 12px; font-size: 1.15rem; color: var(--brand-dark);
      border-left: 4px solid var(--brand); padding-left: 12px;
    }
    .doc-section p { color: var(--ink-soft); font-size: 0.94rem; margin: 0 0 14px; }
    .doc-section h4 { margin: 20px 0 8px; font-size: 1rem; color: var(--ink); }
    .doc-section ul.doc-list { margin: 0 0 14px; padding-left: 20px; color: var(--ink-soft); font-size: 0.93rem; }
    .doc-section ul.doc-list li { margin: 6px 0; }
    .doc-src {
      background: #eef2f7; border-radius: 10px; padding: 12px 16px;
      font-size: 0.88rem; color: var(--ink-soft); margin: 0 0 20px;
    }
    .doc-src a { color: var(--brand); font-weight: 600; }
    @media (max-width: 640px) {
      .doc-section { padding: 20px 18px; }
    }"""
assert style_anchor in s
s = s.replace(style_anchor, doc_css)

# 4) 插入文章 section（页脚前）
anchor = "  </section>\n\n  <!-- 页脚 -->"
assert anchor in s
s = s.replace(anchor, "  </section>\n\n" + article_html + "\n\n  <!-- 页脚 -->")

io.open(AI, "w", encoding="utf-8", newline="\n").write(s)
print("ai.html updated, size:", len(s))
