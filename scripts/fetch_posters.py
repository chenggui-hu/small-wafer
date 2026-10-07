# -*- coding: utf-8 -*-
"""下载三部年度视频海报到 assets/posters/，并抓豆瓣评分"""
import urllib.request, ssl, json, os, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx))

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

POSTERS = {
    'xiani.jpg': 'https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2896563963.jpg',
    'severance.jpg': 'https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2916136388.jpg',
    'lifewonders.jpg': 'https://img2.doubanio.com/view/photo/s_ratio_poster/public/p2935626681.jpg',
}
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'posters')
os.makedirs(OUT, exist_ok=True)

for name, url in POSTERS.items():
    req = urllib.request.Request(url, headers={**UA, 'Referer': 'https://movie.douban.com/'})
    data = opener.open(req, timeout=20).read()
    path = os.path.join(OUT, name)
    with open(path, 'wb') as f:
        f.write(data)
    print('saved', name, len(data), 'bytes')

SUBJECTS = {
    '仙逆 第一季': '35679839',
    '人生切割术 第二季': '35783948',
    '生命奇观2': '38646835',
}
for title, sid in SUBJECTS.items():
    try:
        req = urllib.request.Request('https://movie.douban.com/subject/%s/' % sid, headers=UA)
        html = opener.open(req, timeout=20).read().decode('utf-8', 'ignore')
        m = re.search(r'"ratingValue":\s*"?([\d.]+)"?', html)
        m2 = re.search(r'v:average">([\d.]+)<', html)
        rating = (m or m2).group(1) if (m or m2) else '?'
        n = re.search(r'(>\d+人评价)', html)
        print(title, 'rating:', rating, n.group(1) if n else '')
    except Exception as e:
        print(title, 'ERR', repr(e)[:80])
