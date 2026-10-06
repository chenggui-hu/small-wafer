# -*- coding: utf-8 -*-
"""下载常用网页集各站点 favicon 到 assets/icons/，供 webapps.html 横排 logo 使用。

用法：
  python fetch_icons.py
依赖：无第三方库。网络优先直连，失败自动切 Clash 代理 127.0.0.1:7890。
"""
import os
import ssl
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")
PROXY = "http://127.0.0.1:7890"

# name -> 用于取 favicon 的域名
SITES = {
    "chatgpt": "chatgpt.com",
    "gemini": "gemini.google.com",
    "yuanbao": "yuanbao.tencent.com",
    "sophnet": "sophnet.com",
    "waytoagi": "waytoagi.feishu.cn",
    "x": "x.com",
    "zhihu": "zhihu.com",
    "csdn": "csdn.net",
    "xueqiu": "xueqiu.com",
    "stackoverflow": "stackoverflow.com",
    "base64": "base64.us",
    "scibot": "sci-bot.ru",
    "masuit": "masuit.net",
    "removebg": "remove.bg",
    "jsq3000": "jsq3000.com",
    "douyin": "douyin.com",
    "bilibili": "bilibili.com",
    "seedhub": "seedhub.cc",
    "flacdownloader": "flacdownloader.com",
    "instagram": "instagram.com",
    "wanmeikk": "wanmeikk.film",
    "susuifa": "susuifa.com",
    "zgtv": "top1.zgtv.online",
    "yikm": "yikm.net",
}


def opener_with(proxy):
    handler = urllib.request.ProxyHandler(
        {"http": proxy, "https": proxy} if proxy else {}
    )
    return urllib.request.build_opener(
        handler, urllib.request.HTTPSHandler(context=CTX)
    )


def fetch(url, use_proxy):
    op = opener_with(PROXY if use_proxy else None)
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    return op.open(req, timeout=15).read()


def sources(domain):
    return [
        "https://icons.duckduckgo.com/ip3/%s.ico" % domain,
        "https://www.google.com/s2/favicons?domain=%s&sz=64" % domain,
        "https://%s/favicon.ico" % domain,
    ]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    failed = []
    for name, domain in SITES.items():
        out_path = os.path.join(OUT_DIR, name + ".png")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 300:
            print("[skip] %-16s 已存在" % name)
            continue
        data = None
        for i, url in enumerate(sources(domain)):
            for use_proxy in (False, True):
                try:
                    data = fetch(url, use_proxy)
                    if data and len(data) > 200:
                        break
                except Exception:
                    data = None
            if data and len(data) > 200:
                print("[ok]   %-16s <- %s" % (name, url))
                break
        if data and len(data) > 200:
            with open(out_path, "wb") as f:
                f.write(data)
        else:
            failed.append(name)
            print("[fail] %-16s" % name)
    print("\n完成。失败：%s" % (failed if failed else "无"))


if __name__ == "__main__":
    main()
