# -*- coding: utf-8 -*-
"""
通过搜狗微信搜索抓取「硅基火花」公众号文章列表，生成 assets/articles.json
用法：python scripts/fetch_articles.py [关键词，默认 硅基火花] [数量，默认6]

数据来源为搜狗微信搜索结果页（type=2 文章），包含：标题/摘要/公众号名/日期/缩略图。
文章链接为搜狗跳转链接，脚本会尝试解析出 mp.weixin.qq.com 真实链接；
解析失败时保留搜狗跳转链接（在浏览器中点击仍可打开）。
"""
import json
import os
import re
import sys
import html as html_mod
import urllib.parse
import urllib.request
import ssl
import http.cookiejar

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

_cj = http.cookiejar.CookieJar()
OPENER = urllib.request.build_opener(
    urllib.request.ProxyHandler({}),  # 绕过环境代理
    urllib.request.HTTPSHandler(context=CTX),
    urllib.request.HTTPCookieProcessor(_cj),
)
OPENER.addheaders = [("User-Agent", UA), ("Accept-Language", "zh-CN,zh;q=0.9")]


def get(url, referer=None):
    req = urllib.request.Request(url)
    if referer:
        req.add_header("Referer", referer)
    return OPENER.open(req, timeout=25).read().decode("utf-8", "ignore")


def clean(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return html_mod.unescape(s).strip()


def resolve_link(href, base="https://weixin.sogou.com"):
    """尝试把搜狗 /link 跳转链接解析成 mp.weixin.qq.com 真实链接"""
    absu = href if href.startswith("http") else base + href
    try:
        page = get(absu, referer="https://weixin.sogou.com/")
        # 跳转页用 url += '...'（单引号）分片拼接真实地址
        real = "".join(re.findall(r"url\s*\+=\s*['\"]([^'\"]*)['\"]", page))
        real = real.replace("@", "")
        if real.startswith("http"):
            return real
    except Exception:
        pass
    return absu  # 解析失败，退回搜狗跳转链接


def scrape(query, count):
    # 引号精确匹配，减少无关公众号结果
    q = urllib.parse.quote('"%s"' % query)
    url = "https://weixin.sogou.com/weixin?type=2&query=%s" % q
    page = get(url)
    if "antispider" in page.lower() or "验证码" in page:
        print("[!] 搜狗反爬触发（验证码）。可稍后重试，或先在浏览器里搜一次再跑脚本。")
        sys.exit(2)

    items = []
    blocks = re.split(r'<li id="sogou_vr', page)
    for b in blocks[1:]:
        title_m = re.search(r'uigs="article_title_\d+">(.*?)</a>', b, re.S)
        if not title_m:
            continue
        account_m = re.search(r'class="all-time-y2"[^>]*>([^<]+)</span>', b)
        account = clean(account_m.group(1)) if account_m else ""
        if account != query:  # 只保留目标公众号的文章
            continue
        title = clean(title_m.group(1))
        link_m = re.search(r'<a[^>]+href="(/link\?url=[^"]+)"[^>]*uigs="article_title_\d+"', b)
        digest_m = re.search(r'class="txt-info"[^>]*>(.*?)</p>', b, re.S)
        date_m = re.search(r"timeConvert\('(\d+)'\)", b) or re.search(r"(\d{4}-\d{1,2}-\d{1,2})", b)
        img_m = re.search(r'<img[^>]+src="((?:https?:)?//[^"]+)"', b)
        if date_m and date_m.group(1).isdigit():
            import time as _t
            date = _t.strftime("%Y-%m-%d", _t.localtime(int(date_m.group(1))))
        else:
            date = date_m.group(1) if date_m else ""
        thumb = html_mod.unescape(img_m.group(1)) if img_m else ""
        if thumb.startswith("//"):
            thumb = "https:" + thumb
        # 按标题去重（搜狗结果偶有重复条目）
        if any(it["title"] == title for it in items):
            continue
        items.append({
            "title": title,
            "digest": clean(digest_m.group(1)) if digest_m else "",
            "account": account,
            "date": date,
            "thumb": thumb,
            "link": ("https://weixin.sogou.com" + link_m.group(1)) if link_m else "",
        })
        if len(items) >= count:
            break
    return items, page


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "硅基火花"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    items, _ = scrape(query, count)
    if not items:
        print("[!] 未解析到结果，页面结构可能变了")
        sys.exit(1)
    print("[i] 抓到 %d 条，解析真实链接并下载缩略图..." % len(items))
    thumb_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "assets", "thumbs")
    os.makedirs(thumb_dir, exist_ok=True)
    for i, a in enumerate(items, 1):
        a["url"] = resolve_link(a["link"]) if a["link"] else ""
        if a["thumb"]:
            try:
                raw = OPENER.open(urllib.request.Request(a["thumb"], headers={"Referer": "https://weixin.sogou.com/"}),
                                  timeout=25).read()
                local = "assets/thumbs/thumb-%d.jpg" % i
                with open(os.path.join(thumb_dir, "thumb-%d.jpg" % i), "wb") as f:
                    f.write(raw)
                a["thumb"] = local
            except Exception as e:
                print("  [!] 缩略图下载失败:", type(e).__name__)
                a["thumb"] = ""
        print("  -", a["date"], a["title"][:30], "->", a["url"][:60])
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "assets", "articles.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print("[OK] 已写入", out)


if __name__ == "__main__":
    main()
