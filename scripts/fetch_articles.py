# -*- coding: utf-8 -*-
"""
抓取「硅基火花」公众号文章列表，生成 assets/articles.json

通道1（优先）：微信公众号官方 API freepublish/batchget
  - 需要 WECHAT_APPID / WECHAT_SECRET 环境变量
  - 调用方 IP 需在公众号后台「基本配置 → IP白名单」里（否则 40164）
  - 返回的 url 是 mp.weixin.qq.com/s/xxx 永久链接

通道2（兜底）：搜狗微信搜索
  - 搜狗解析出的 mp.weixin.qq.com/s?src=11&timestamp=... 签名链接几小时就失效
  - 因此兜底模式存「标题搜索页」链接（type=2 搜标题，永不过期，用户多点一下）

用法：python scripts/fetch_articles.py [关键词，默认 硅基火花] [数量，默认6]
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

OP = urllib.request.build_opener(
    urllib.request.ProxyHandler({}),  # 绕过环境代理
    urllib.request.HTTPSHandler(context=CTX),
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
)
OP.addheaders = [("User-Agent", UA), ("Accept-Language", "zh-CN,zh;q=0.9")]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THUMB_DIR = os.path.join(ROOT, "assets", "thumbs")


def get(url, referer=None):
    req = urllib.request.Request(url)
    if referer:
        req.add_header("Referer", referer)
    return OP.open(req, timeout=25).read().decode("utf-8", "ignore")


def post_json(url, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    return OP.open(req, timeout=25).read().decode("utf-8", "ignore")


def clean(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return html_mod.unescape(s).strip()


def download_thumb(url, idx, referer=None):
    """下载缩略图到本地，成功返回相对路径，失败返回空串"""
    try:
        headers = {"Referer": referer} if referer else {}
        raw = OP.open(urllib.request.Request(url, headers=headers), timeout=25).read()
        local = "assets/thumbs/thumb-%d.jpg" % idx
        os.makedirs(THUMB_DIR, exist_ok=True)
        with open(os.path.join(THUMB_DIR, "thumb-%d.jpg" % idx), "wb") as f:
            f.write(raw)
        return local
    except Exception as e:
        print("  [!] 缩略图下载失败:", type(e).__name__)
        return ""


# ---------------- 通道1：官方 API ----------------

def fetch_via_api(count):
    appid = os.environ.get("WECHAT_APPID", "")
    secret = os.environ.get("WECHAT_SECRET", "")
    if not appid or not secret:
        print("[i] 未配置 WECHAT_APPID/SECRET，跳过官方 API")
        return None
    tok = json.loads(get(
        "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s"
        % (appid, secret)))
    if "access_token" not in tok:
        print("[!] 官方 API 获取 token 失败:", tok.get("errcode"), tok.get("errmsg", "")[:80])
        return None
    data = json.loads(post_json(
        "https://api.weixin.qq.com/cgi-bin/freepublish/batchget?access_token=" + tok["access_token"],
        {"offset": 0, "count": min(count, 30), "no_content": 1}))
    if data.get("errcode"):
        print("[!] 官方 API freepublish 失败:", data.get("errcode"), data.get("errmsg", "")[:80])
        return None

    items, seen = [], set()
    for pub in data.get("item", []):
        for news in (pub.get("content", {}).get("news_item") or [])[:1]:
            title = clean(news.get("title", ""))
            key = title[:15]
            if not title or key in seen:
                continue
            seen.add(key)
            import time as _t
            date = _t.strftime("%Y-%m-%d", _t.localtime(pub.get("content", {}).get("create_time",
                                                                                    pub.get("update_time", 0))))
            digest = clean(news.get("digest", ""))
            thumb_url = news.get("thumb_url", "")
            items.append({
                "title": title,
                "digest": digest,
                "account": "硅基火花",
                "date": date,
                "thumb": thumb_url,       # 先存 URL，稍后统一下载
                "thumb_src": thumb_url,
                "url": news.get("url", ""),
            })
            break
        if len(items) >= count:
            break
    return items


# ---------------- 通道2：搜狗搜索兜底 ----------------

def fetch_via_sogou(query, count):
    q = urllib.parse.quote('"%s"' % query)
    page = get("https://weixin.sogou.com/weixin?type=2&query=%s" % q)
    if "antispider" in page.lower() or "验证码" in page:
        print("[!] 搜狗反爬触发（验证码）")
        return None

    items, seen = [], set()
    for b in re.split(r'<li id="sogou_vr', page)[1:]:
        title_m = re.search(r'uigs="article_title_\d+">(.*?)</a>', b, re.S)
        if not title_m:
            continue
        account_m = re.search(r'class="all-time-y2"[^>]*>([^<]+)</span>', b)
        account = clean(account_m.group(1)) if account_m else ""
        if account != query:
            continue
        title = clean(title_m.group(1))
        key = title[:15]
        if key in seen:
            continue
        seen.add(key)
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
        # 兜底链接：标题搜索页（永不过期）。签名链接会过期，绝不入库
        search_link = ("https://weixin.sogou.com/weixin?type=2&query="
                       + urllib.parse.quote(title[:30]))
        items.append({
            "title": title,
            "digest": clean(digest_m.group(1)) if digest_m else "",
            "account": account,
            "date": date,
            "thumb": thumb,
            "thumb_src": thumb,
            "url": search_link,
        })
        if len(items) >= count:
            break
    return items


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "硅基火花"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 6

    print("[i] 尝试官方 API（永久链接）...")
    items = fetch_via_api(count)
    if items:
        print("[OK] 官方 API 抓到 %d 篇" % len(items))
    else:
        print("[i] 回退搜狗搜索...")
        items = fetch_via_sogou(query, count)
        if not items:
            print("[!] 两个通道都没抓到，退出")
            sys.exit(2)
        print("[OK] 搜狗抓到 %d 篇（链接为标题搜索页，点开后需再点一下目标文章）" % len(items))

    print("[i] 下载缩略图...")
    for i, a in enumerate(items, 1):
        if a.get("thumb_src"):
            referer = "https://weixin.sogou.com/" if not a["url"].startswith("http") or "mp.weixin" not in a["url"] else "https://mp.weixin.qq.com/"
            a["thumb"] = download_thumb(a["thumb_src"], i, referer=referer)
        a.pop("thumb_src", None)
        print("  -", a["date"], a["title"][:30], "->", a["url"][:55])

    out = os.path.join(ROOT, "assets", "articles.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print("[OK] 已写入", out, "共", len(items), "篇")


if __name__ == "__main__":
    main()
