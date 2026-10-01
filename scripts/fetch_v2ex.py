# -*- coding: utf-8 -*-
"""
抓取 V2EX 热帖，生成 assets/v2ex.json

为什么不用前端直连？
  - V2EX 官方 API（https://www.v2ex.com/api/topics/hot.json）不返回 CORS 头，
    浏览器跨域会被拦；且 v2ex.com 在国内直连基本超时。
  - 因此改为「本地/定时脚本生成静态 JSON」方案，前端同源读取，任何访客都能看到。

网络通道（按顺序尝试）：
  直连 → 本地代理 7890(Clash) → 10809 → 1080 → 8889 → 33210

用法：python scripts/fetch_v2ex.py [数量，默认10]
内容无变化时不写文件（避免空提交）。
"""
import json
import os
import ssl
import sys
import time
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "v2ex.json")

API = "https://www.v2ex.com/api/topics/hot.json"

PROXIES = [
    None,
    "http://127.0.0.1:7890",
    "http://127.0.0.1:10809",
    "http://127.0.0.1:1080",
    "http://127.0.0.1:8889",
    "http://127.0.0.1:33210",
]


def fetch(proxy):
    if proxy:
        handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
    else:
        handler = urllib.request.ProxyHandler({})  # 绕过环境变量里的死代理
    op = urllib.request.build_opener(handler, urllib.request.HTTPSHandler(context=CTX))
    req = urllib.request.Request(API, headers={
        "User-Agent": UA,
        "Accept": "application/json",
    })
    return op.open(req, timeout=20).read().decode("utf-8", "ignore")


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    raw = None
    for px in PROXIES:
        try:
            raw = fetch(px)
            print("[OK] 通道 %s 抓取成功" % (px or "直连"))
            break
        except Exception as e:
            print("[..] 通道 %-24s 失败: %s" % (px or "直连", type(e).__name__))
    if not raw:
        print("[!] 所有通道都失败，保留现有 v2ex.json 不覆盖")
        sys.exit(2)

    data = json.loads(raw)
    items = []
    for i, t in enumerate(data[:count], 1):
        title = (t.get("title") or "").strip()
        url = t.get("url") or ("https://www.v2ex.com/t/%s" % t.get("id", ""))
        if not title or not url:
            continue
        node = (t.get("node") or {}).get("title") or (t.get("node") or {}).get("name") or ""
        items.append({
            "rank": i,
            "title": title,
            "url": url,
            "replies": t.get("replies", 0),
            "node": node,
        })

    if not items:
        print("[!] 解析结果为空，不覆盖")
        sys.exit(2)

    payload = {
        "updated": time.strftime("%Y-%m-%d %H:%M"),
        "items": items,
    }

    # 内容无变化则跳过，避免空提交
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
    print("[OK] 已写入 %s（%d 条）" % (OUT, len(items)))
    for it in items[:3]:
        print("   %d. %s" % (it["rank"], it["title"][:36]))


if __name__ == "__main__":
    main()
