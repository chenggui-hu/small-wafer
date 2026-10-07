# -*- coding: utf-8 -*-
"""从 youmind 页面 HTML 中提取 X Article（lexical JSON）全文为 Markdown"""
import io, json, re, sys

HTML = r"C:\Users\chenggui\WorkBuddy\Skill\small-wafer\scripts\_youmind.html"
OUT_MD = r"C:\Users\chenggui\WorkBuddy\Skill\small-wafer\scripts\_codex_article.md"

html = io.open(HTML, encoding="utf-8").read()
start = html.find('{\\"root\\":')
assert start > 0, "root JSON not found"

# 在转义文本上做平衡花括号扫描：
# 层级约定（HTML 内）：
#   \"   -> 结构性引号（JSON 语法）
#   \\"  -> 字面量引号字符
#   \\\t 等 -> 其他转义
# 所以字符串边界是 \"，扫描时：
#   未进字符串时遇到 \" 进入；进字符串后遇到 \" 退出；遇 \\" 或 \\x 跳 3 个字符
i = start
depth = 0
end = None
in_str = False
n = len(html)
while i < n:
    if in_str:
        if html.startswith('\\\\', i):      # \\" -> 字面引号，跳过整个转义
            i += 3
            continue
        if html.startswith('\\"', i):      # 结构性引号 -> 退出字符串
            in_str = False
            i += 2
            continue
        i += 1
    else:
        if html.startswith('\\"', i):      # 结构性引号 -> 进入字符串
            in_str = True
            i += 2
            continue
        c = html[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1

assert end, "unbalanced"
raw = html[start:end]
print("raw len:", len(raw))

# 解码：先处理最深层转义，再还原结构引号
s = raw
s = s.replace('\\\\"', '\x01')   # \\" -> 占位（字面引号）
s = s.replace("\\\\n", "\n")     # \\n -> 换行（字符串内）
s = s.replace("\\\\t", "\t")
s = s.replace('\\"', '"')        # \" -> 结构引号
s = s.replace('\x01', '"')       # 占位 -> 字面引号

data = json.loads(s, strict=False)
root = data["root"]["children"]
print("top blocks:", len(root))


def node_text(b):
    parts = []
    for c in b.get("children", []):
        if "text" in c:
            parts.append(c["text"])
        elif c.get("type") == "link":
            parts.append("".join(x.get("text", "") for x in c.get("children", [])))
    return "".join(parts)


out = []

def walk(blocks):
    for b in blocks:
        t = b.get("type")
        if t == "heading":
            tag = b.get("tag", "h3")
            level = int(tag[1]) if tag[:1] == "h" and tag[1:].isdigit() else 3
            txt = node_text(b).strip()
            if txt:
                out.append("#" * level + " " + txt)
        elif t == "paragraph":
            txt = node_text(b).strip()
            if txt:
                out.append(txt)
        elif t == "quote":
            txt = node_text(b).strip()
            if txt:
                out.append("> " + txt)
        elif t == "list":
            ordered = b.get("listType") == "number"
            k = 0
            for it in b.get("children", []):
                k += 1
                txt = node_text(it).strip()
                if txt:
                    out.append(("1. " if ordered else "- ") + txt)
        elif t == "code":
            txt = node_text(b)
            out.append("```\n" + txt + "\n```")

walk(root)
md = "\n\n".join(out)
io.open(OUT_MD, "w", encoding="utf-8", newline="\n").write(md)
print("total chars:", len(md))
print("--- head ---")
print(md[:600])
print("--- tail ---")
print(md[-400:])
