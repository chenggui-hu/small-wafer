# -*- coding: utf-8 -*-
"""
抓取 RSS 订阅文章（科技博客），聚合生成 assets/rss.json
前端在首页「常用网页集」下方以时间线展示。

订阅源：
  - 异次元软件世界  https://www.iplaysoft.com/feed    (RSS 2.0)
  - 拾月的博客(TW93) https://tw93.fun/feed.xml        (RSS 2.0)
  - 阮一峰的网络日志 https://www.ruanyifeng.com/blog/atom.xml (Atom)

合并按发布时间倒序取 Top N（默认 15）。
网络通道：直连 → Clash 7890 → 10809 → 1080 → 8889 → 33210
内容无变化时不写文件（避免空提交）。

用法：python scripts/fetch_rss.py [数量，默认15]
"""
import json
import os
import re
import ssl
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "rss.json")

FEEDS = [
    ("异次元软件世界", "https://www.iplaysoft.com/feed"),
    ("拾月的博客",     "https://tw93.fun/feed.xml"),
    ("阮一峰的网络日志", "https://www.ruanyifeng.com/blog/atom.xml"),
]

PROXIES = [
    None,
    "http://127.0.0.1:7890",
    "http://127.0.0.1:10809",
    "http://127.0.0.1:1080",
    "http://127.0.0.1:8889",
    "http://127.0.0.1:33210",
]

ATOM = "http://www.w3.org/2005/Atom"


def fetch(url, proxy):
    if proxy:
        handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
    else:
        handler = urllib.request.ProxyHandler({})  # 绕过环境变量里的死代理
    op = urllib.request.build_opener(handler, urllib.request.HTTPSHandler(context=CTX))
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    return op.open(req, timeout=20).read().decode("utf-8", "ignore")


def get_feed(url):
    """直连优先，失败走代理列表"""
    last = None
    for px in PROXIES:
        try:
            return fetch(url, px)
        except Exception as e:
            last = e
            print("  [..] %-26s %-8s 失败: %s" % (url.split("/")[2], px or "直连", type(e).__name__))
    print("  [!] %s 所有通道失败: %s" % (url.split("/")[2], last))
    return None


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fmt_date(raw):
    raw = (raw or "").strip()
    if not raw:
        return ""
    try:
        return parsedate_to_datetime(raw).strftime("%Y-%m-%d")
    except Exception:
        pass
    m = re.match(r"(\d{4}-\d{2}-\d{2})", raw)
    return m.group(1) if m else raw[:16]


def parse_feed(xml_text, source_name):
    """同时兼容 RSS 2.0 与 Atom"""
    out = []
    try:
        root = ET.fromstring(xml_text.encode("utf-8", "ignore") if isinstance(xml_text, str) else xml_text)
    except Exception as e:
        print("  [!] %s XML 解析失败: %s" % (source_name, e))
        return out

    is_atom = root.tag == "{%s}feed" % ATOM or root.tag == "feed"
    if is_atom:
        entries = root.findall("{%s}entry" % ATOM) or root.findall("entry")
        for e in entries:
            title = clean(e.findtext("{%s}title" % ATOM) or e.findtext("title") or "")
            link = ""
            for le in e.findall("{%s}link" % ATOM) + e.findall("link"):
                href = le.get("href") or le.get("HREF") or ""
                rel = (le.get("rel") or "alternate").lower()
                if href and rel == "alternate":
                    link = href
                    break
                if href and not link:
                    link = href
            date = fmt_date(e.findtext("{%s}published" % ATOM) or e.findtext("{%s}updated" % ATOM)
                            or e.findtext("published") or e.findtext("updated"))
            if title and link:
                out.append({"title": title, "url": link, "source": source_name, "date": date})
    else:
        for item in root.iter("item"):
            title = clean(item.findtext("title") or "")
            link = (item.findtext("link") or "").strip()
            date = fmt_date(item.findtext("pubDate"))
            if title and link:
                out.append({"title": title, "url": link, "source": source_name, "date": date})
    return out


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 15

    all_items = []
    ok_sources = 0
    for name, url in FEEDS:
        print("[..] 拉取 %s ..." % name)
        raw = get_feed(url)
        if raw:
            items = parse_feed(raw, name)
            print("  [OK] %s：%d 条" % (name, len(items)))
            if items:
                ok_sources += 1
            all_items.extend(items)

    if not all_items:
        print("[!] 所有源都失败，保留现有 rss.json 不覆盖")
        sys.exit(2)

    seen, uniq = set(), []
    for it in all_items:
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        uniq.append(it)

    # 有日期的按时间倒序在前，无日期的排后面
    dated = [it for it in uniq if it["date"]]
    undated = [it for it in uniq if not it["date"]]
    dated.sort(key=lambda x: x["date"], reverse=True)
    picked = (dated + undated)[:count]
    for i, it in enumerate(picked, 1):
        it["rank"] = i

    payload = {
        "updated": time.strftime("%Y-%m-%d %H:%M"),
        "note": "每周一 07:00 自动更新",
        "sources": [name for name, _ in FEEDS],
        "items": picked,
    }

    if os.path.exists(OUT):
        try:
            with open(OUT, "r", encoding="utf-8") as f:
                old = json.load(f)
            if old.get("items") == payload["items"]:
                print("[=] 内容无变化，跳过写入")
                return
        except Exception:
            pass

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("[OK] 已写入 %s（成功源 %d/%d，共 %d 条）" % (OUT, ok_sources, len(FEEDS), len(picked)))
    for it in picked[:3]:
        print("   %d. [%s] %s" % (it["rank"], it["source"], it["title"][:40]))


if __name__ == "__main__":
    main()
