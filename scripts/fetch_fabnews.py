# -*- coding: utf-8 -*-
"""
抓取半导体 Fab 技术类新闻 RSS，聚合生成 assets/fabnews.json
输出中英文各 Top10（en / cn 两个数组），前端左右两列展示。

英文源：
  - SemiEngineering.com      （半导体工程深度博客，全 fab 向）
  - EE Times                 （电子工程行业，含大量半导体报道）
  - IEEE Spectrum 半导体频道 （IEEE 半导体专题）
  - SemiWiki                 （半导体工艺/设备社区）
中文源：
  - IT之家                   （科技资讯，关键词过滤出芯片/半导体内容）
  - Solidot                  （科技杂谈，关键词过滤）

过滤：标题/摘要命中关键词优先；不足 10 条时按时间补齐。
网络通道：直连 → Clash 7890 → 10809 → 1080 → 8889 → 33210
内容无变化时不写文件（避免空提交）。

用法：python scripts/fetch_fabnews.py [每列数量，默认10]
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
OUT = os.path.join(ROOT, "assets", "fabnews.json")

FEEDS_EN = [
    ("SemiEngineering", "https://semiengineering.com/feed/"),
    ("EE Times",        "https://www.eetimes.com/feed/"),
    ("IEEE Spectrum",   "https://spectrum.ieee.org/feeds/topic/semiconductors.rss"),
    ("SemiWiki",        "https://semiwiki.com/feed/"),
]

FEEDS_CN = [
    ("IT之家", "https://www.ithome.com/rss/"),
    ("Solidot", "https://www.solidot.org/index.rss"),
]

PROXIES = [
    None,
    "http://127.0.0.1:7890",
    "http://127.0.0.1:10809",
    "http://127.0.0.1:1080",
    "http://127.0.0.1:8889",
    "http://127.0.0.1:33210",
]

# 英文关键词
KEYWORDS = re.compile(
    r"fab|foundry|wafer|litho|lithography|EUV|DUV|etch|deposit|yield|TSMC|"
    r"SMIC|UMC|GlobalFoundries|packaging|chiplet|advanced node|gate[- ]all[- ]around|"
    r"GAA|FinFET|DRAM|NAND|HBM|cleanroom|metrology|CMP|photomask|ASML|"
    r"semiconductor|process node|Moore|die|substrate|memory chip|NOR|"
    r"coWoS|fan-?out|silicon|晶圆|光刻|封装|良率|代工",
    re.I,
)

# 中文关键词（IT之家/Solidot 是综合源，必须过滤）
KEYWORDS_CN = re.compile(
    r"芯片|半导体|晶圆|光刻|封装|良率|代工|台积电|中芯国际|存储|闪存|内存颗粒|"
    r"DRAM|NAND|HBM|EUV|制程|晶圆厂|fab|SoC|GPU|CPU|纳米|Chiplet|先进封装|"
    r"离子注入|刻蚀|薄膜|靶材|光刻胶|MOS|碳化硅|氮化镓",
    re.I,
)


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


def parse_rss(xml_text, source_name):
    out = []
    try:
        root = ET.fromstring(xml_text.encode("utf-8", "ignore") if isinstance(xml_text, str) else xml_text)
    except Exception as e:
        print("  [!] %s XML 解析失败: %s" % (source_name, e))
        return out
    for item in root.iter("item"):
        title = clean(item.findtext("title") or "")
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        desc = clean(item.findtext("description") or "")[:160]
        date = ""
        if pub:
            try:
                date = parsedate_to_datetime(pub).strftime("%Y-%m-%d")
            except Exception:
                date = pub[:16]
        if title and link:
            out.append({
                "title": title,
                "url": link,
                "source": source_name,
                "date": date,
                "summary": desc,
            })
    return out


def collect(feeds, count, kw):
    """抓一组源，关键词命中优先 + 按日期补齐，返回 top count 条"""
    all_items = []
    for name, url in feeds:
        print("[..] 拉取 %s ..." % name)
        raw = get_feed(url)
        if raw:
            items = parse_rss(raw, name)
            print("  [OK] %s：%d 条" % (name, len(items)))
            all_items.extend(items)

    seen, uniq = set(), []
    for it in all_items:
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        it["hit"] = bool(kw.search(it["title"] + " " + it["summary"]))
        uniq.append(it)

    hits = [it for it in uniq if it["date"] and it["hit"]]
    hits.sort(key=lambda x: x["date"], reverse=True)
    picked = hits[:count]

    # 命中的太少时，用未命中但带日期的补齐
    if len(picked) < count:
        rest = [it for it in uniq if it["date"] and not it["hit"]]
        rest.sort(key=lambda x: x["date"], reverse=True)
        picked += rest[: count - len(picked)]

    for i, it in enumerate(picked, 1):
        it["rank"] = i
        it.pop("hit", None)
    return picked


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    en = collect(FEEDS_EN, count, KEYWORDS)
    cn = collect(FEEDS_CN, count, KEYWORDS_CN)

    if not en and not cn:
        print("[!] 所有源都失败，保留现有 fabnews.json 不覆盖")
        sys.exit(2)

    payload = {
        "updated": time.strftime("%Y-%m-%d %H:%M"),
        "note": "每周一 07:00 自动更新",
        "en": en,
        "cn": cn,
    }

    if os.path.exists(OUT):
        try:
            with open(OUT, "r", encoding="utf-8") as f:
                old = json.load(f)
            if old.get("en") == payload["en"] and old.get("cn") == payload["cn"]:
                print("[=] 内容无变化，跳过写入")
                return
        except Exception:
            pass

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("[OK] 已写入 %s（EN %d 条 / CN %d 条）" % (OUT, len(en), len(cn)))
    for it in en[:2]:
        print("   EN %d. [%s] %s" % (it["rank"], it["source"], it["title"][:40]))
    for it in cn[:2]:
        print("   CN %d. [%s] %s" % (it["rank"], it["source"], it["title"][:40]))


if __name__ == "__main__":
    main()
