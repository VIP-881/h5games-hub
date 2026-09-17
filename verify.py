#!/usr/bin/env python3
"""
H5 Games Hub — 线上部署 / SEO / GEO 校验脚本（可复用）
用法：python3 verify.py [BASE_URL]
默认 BASE_URL=https://h5games-hub.pages.dev

覆盖三类检查：
  1) 部署：资源可访问、缓存策略、安全/HTTPS 头、路由回退（软 404）
  2) SEO：title/description/canonical/OG/Twitter/favicon/robots/sitemap、语义化与标题层级、移动端
  3) GEO：事实型文案（玩法/操作/场景/FAQ）、JSON-LD（WebSite/Organization/ItemList/FAQPage/BreadcrumbList/HowTo）
"""
import re
import sys
import time
import urllib.request
import urllib.error

# 游戏页 canonical 提取（<link rel="canonical" href="...">）
re_canon = re.compile(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', re.I)

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "https://h5games-hub.pages.dev"
UA = {"User-Agent": "Mozilla/5.0 (compatible; H5HubVerifier/1.0)"}


def fetch(path):
    """返回 (状态码, 响应体文本)"""
    req = urllib.request.Request(BASE + path, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001
        return -1, str(e)


def fetch_headers(path):
    """返回 (状态码, 响应头字典)。键统一小写，避免大小写导致误判。"""
    req = urllib.request.Request(BASE + path, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in (e.headers or {}).items()}
    except Exception:  # noqa: BLE001
        return -1, {}


ok_all = True


def check(ok, label, detail=""):
    global ok_all
    ok_all = ok_all and bool(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" ({detail})" if detail else ""))


print(f"== 校验目标：{BASE} ==")

# ── 1. 部署 ────────────────────────────────────────────────
print("-- 部署与托管 --")
status, html = fetch("/")
check(status == 200, "首页可访问", f"HTTP {status}")

st_root, hdr_root = fetch_headers("/")
cc_root = hdr_root.get("cache-control", "")
check("max-age" in cc_root, "首页 Cache-Control 生效", cc_root or "缺失")

st_game, hdr_game = fetch_headers("/games/snake/")
cc_game = hdr_game.get("cache-control", "")
check("max-age" in cc_game, "游戏页 Cache-Control 生效（目录型路径）", cc_game or "缺失")

# _headers 若让同一路径命中多条带 Cache-Control 的规则，响应会出现重复的 max-age，
# 浏览器行为不一致，属于配置缺陷——这里做回归防护。
check(cc_root.count("max-age") == 1, "首页 Cache-Control 无重复（单条规则命中）",
      f"max-age 出现 {cc_root.count('max-age')} 次")
check(cc_game.count("max-age") == 1, "游戏页 Cache-Control 无重复（单条规则命中）",
      f"max-age 出现 {cc_game.count('max-age')} 次")

nosniff = hdr_root.get("x-content-type-options", "")
check(nosniff.lower() == "nosniff", "安全头 X-Content-Type-Options", nosniff or "缺失")

hsts = hdr_root.get("strict-transport-security", "")
check("max-age" in hsts, "HSTS HTTPS 强化头", (hsts[:36] + "...") if hsts else "缺失")

# 软 404 防护：未知路径必须返回真 404，否则任意 URL 都会被当首页重复收录
s404, _ = fetch("/__soft404_probe__.html")
check(s404 == 404, "软 404 防护：未知路径返回真 404", f"HTTP {s404}")

# ── 2. SEO ─────────────────────────────────────────────────
print("-- SEO 元数据 --")
seo = {
    "title 标签": "<title>",
    "meta description": 'name="description"',
    "canonical 规范链接": 'rel="canonical"',
    "canonical 指向生效域名": f'href="{BASE}/"',
    "og:title": 'property="og:title"',
    "og:description": 'property="og:description"',
    "og:image 社交封面": 'property="og:image"',
    "twitter:card": 'name="twitter:card"',
    "twitter:image": 'name="twitter:image"',
    "favicon": 'rel="icon"',
    "viewport 移动端适配": 'name="viewport"',
    "lang 语言声明": 'lang="zh-CN"',
}
for name, needle in seo.items():
    check(needle in html, name)

print("-- 语义化与标题层级 --")
semantic = {
    "header 语义标签": "<header",
    "nav 语义标签": "<nav",
    "main 语义标签": "<main",
    "section 语义标签": "<section",
    "article 语义标签": "<article",
    "footer 语义标签": "<footer",
}
for name, needle in semantic.items():
    check(needle in html, name)

h1_count = html.count("<h1")
check(h1_count == 1, "存在且仅有一个 h1", f"h1 数量={h1_count}")
check("<h2" in html, "存在 h2 二级标题")
check("<h3" in html, "存在 h3 三级标题（游戏卡片）")

# ── 3. GEO ─────────────────────────────────────────────────
print("-- GEO 结构化数据 --")
geo_ld = {
    "JSON-LD 块": "application/ld+json",
    "WebSite 实体": '"WebSite"',
    "Organization 实体": '"Organization"',
    "ItemList 游戏列表": '"ItemList"',
    "ItemList 含游戏描述字段": '"gameGenre"',
    "FAQPage 结构化数据": '"FAQPage"',
    "BreadcrumbList 面包屑": '"BreadcrumbList"',
    "HowTo 操作步骤": '"HowTo"',
    "GeoCoordinates 地理坐标": '"GeoCoordinates"',
    "areaServed 区域服务": "areaServed",
}
for name, needle in geo_ld.items():
    check(needle in html, name)

print("-- GEO 事实型文案 --")
geo_text = {
    "玩法与操作段落": 'id="howto"',
    "适用场景段落": 'id="use-cases"',
    "玩法介绍文案": "玩法介绍",
    "操作方式文案": "操作方式",
    "常见问题段落": 'id="faq"',
    "llms.txt 链接（AI 可读摘要）": "llms.txt",
}
for name, needle in geo_text.items():
    check(needle in html, name)

# ── 4. 资源与站点地图 ──────────────────────────────────────
print("-- 资源与爬虫文件 --")
paths = ["/games/snake/", "/games/2048/", "/games/memory/", "/games/breakout/",
         "/games/tictactoe/", "/games/simon/", "/games/spaceshooter/", "/games/tetris/",
         "/games/minesweeper/", "/games/flappy/", "/games/puzzle15/", "/games/whackamole/",
         "/games/life/", "/games/hanoi/", "/games/pong/", "/games/sudoku/", "/games/gomoku/",
         "/games/lightsout/", "/games/maze/", "/games/dino/", "/games/game24/",
         "/llms.txt", "/sitemap.xml", "/robots.txt", "/assets/og-cover.svg",
         "/assets/css/style.css", "/assets/js/main.js"]
for p in paths:
    s, _ = fetch(p)
    check(s == 200, f"资源可访问 {p}", f"HTTP {s}")

# robots.txt 必须把 Sitemap 指向「当前生效域名」
s_rb, robots_txt = fetch("/robots.txt")
check(f"Sitemap: {BASE}/sitemap.xml" in robots_txt,
      "robots.txt 的 Sitemap 指向生效域名", BASE)

# sitemap 应包含全部游戏页
s_sm, sitemap_xml = fetch("/sitemap.xml")
game_paths = [p for p in paths if p.startswith("/games/")]
missing = [p for p in game_paths if (BASE + p) not in sitemap_xml]
check(not missing, "sitemap.xml 覆盖全部游戏页",
      ("缺失：" + ",".join(missing)) if missing else f"{len(game_paths)}/{len(game_paths)}")

# ── 5. 游戏子页 SEO（可索引 / canonical / OG / JSON-LD） ────
print("-- 游戏子页 SEO --")
game_slugs = [p.strip("/").split("/")[-1] for p in game_paths]
bad_canon, bad_robots, bad_og, bad_ld = [], [], [], []
for slug in game_slugs:
    s, ghtml = fetch(f"/games/{slug}/")
    if s != 200:
        bad_canon.append(slug + "(非200)")
        continue
    m = re_canon.search(ghtml)
    if not (m and f"/games/{slug}/" in m.group(1)):
        bad_canon.append(slug)
    if "noindex" in ghtml:
        bad_robots.append(slug)
    if 'property="og:title"' not in ghtml:
        bad_og.append(slug)
    if '"VideoGame"' not in ghtml:
        bad_ld.append(slug)

check(not bad_canon, "游戏页 canonical 指向自身路径",
      "缺失：" + ",".join(bad_canon) if bad_canon else f"{len(game_slugs)}/{len(game_slugs)}")
check(not bad_robots, "游戏页可索引（无 noindex）",
      "noindex：" + ",".join(bad_robots) if bad_robots else f"{len(game_slugs)}/{len(game_slugs)}")
check(not bad_og, "游戏页 OG 标签（og:title）",
      "缺失：" + ",".join(bad_og) if bad_og else f"{len(game_slugs)}/{len(game_slugs)}")
check(not bad_ld, "游戏页 VideoGame JSON-LD",
      "缺失：" + ",".join(bad_ld) if bad_ld else f"{len(game_slugs)}/{len(game_slugs)}")

# ── 6. 性能与可访问性 ──────────────────────────────────────
print("-- 性能与可访问性 --")
html_bytes = len(html.encode("utf-8"))
check(html_bytes <= 80 * 1024, "首页 HTML 体积 ≤ 80KB", f"{html_bytes / 1024:.1f} KB")

s_css, css_txt = fetch("/assets/css/style.css")
css_bytes = len(css_txt.encode("utf-8"))
check(s_css == 200 and css_bytes <= 30 * 1024, "样式表体积 ≤ 30KB", f"{css_bytes / 1024:.1f} KB")

t0 = time.time()
s_perf, _ = fetch("/")
elapsed = (time.time() - t0) * 1000
check(s_perf == 200 and elapsed <= 3000, "首页响应耗时 ≤ 3s", f"{elapsed:.0f} ms")

check('class="skip-link"' in html, "无障碍：跳转主内容链接（skip-link）")
check('aria-label="主导航"' in html, "无障碍：导航区 aria-label")

print("\n结果：", "全部通过" if ok_all else "存在失败项")
sys.exit(0 if ok_all else 1)
