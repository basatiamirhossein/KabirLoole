"""Static site generator for the Kabirloole website.

Usage:  python3 build/build.py
Output: {fa,ar,en}/*.html, index.html, 404.html, site.webmanifest, assets/css/*.css and, when a
TypeScript compiler (tsc) is on PATH, assets/js/main.js. sitemap.xml and robots.txt need SITE_URL.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).resolve().parent))

from assets import ROOT, build_css, build_embedded_fonts, build_js, check_fonts  # noqa: E402
from blog import ARTICLE_LANG, ARTICLES, article_body, article_info  # noqa: E402
from components import e  # noqa: E402
from data import ASSET_VERSION, DEFAULT_LANG, LANGS, PAGES, SITE_URL  # noqa: E402
from i18n import CONTENT, check_content  # noqa: E402
from layout import page_url, render_page  # noqa: E402
from pages import PAGE_BUILDERS  # noqa: E402

LANG_STORAGE_KEY: Final[str] = "kl-lang"


def render_root() -> str:
    """Language picker that forwards to the saved or browser language."""
    t = CONTENT[DEFAULT_LANG]
    cards = "".join(
        f'<a class="lang-card neu" href="{l}/index.html" lang="{l}" dir="{CONTENT[l]["dir"]}">'
        f'<strong>{e(CONTENT[l]["brand"])}</strong><span>{e(CONTENT[l]["label"])}</span></a>'
        for l in LANGS
    )
    return f"""<!doctype html>
<html lang="{DEFAULT_LANG}" dir="{t['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>کبیر لوله | Kabirloole</title>
<meta name="description" content="{e(t['meta']['index']['desc'])}">
<link rel="icon" type="image/png" sizes="32x32" href="assets/img/logo-32.png">
<link rel="stylesheet" href="assets/css/main.css?v={ASSET_VERSION}">
<script>
(function () {{
  var langs = {json.dumps(list(LANGS))}, saved = null;
  try {{ saved = window.localStorage.getItem("{LANG_STORAGE_KEY}"); }} catch (err) {{ saved = null; }}
  var nav = (navigator.language || "").slice(0, 2).toLowerCase();
  var pick = langs.indexOf(saved) > -1 ? saved : (langs.indexOf(nav) > -1 ? nav : "{DEFAULT_LANG}");
  window.location.replace(pick + "/index.html");
}})();
</script>
<noscript><meta http-equiv="refresh" content="0; url={DEFAULT_LANG}/index.html"></noscript>
</head>
<body class="page-root">
<div class="paper" aria-hidden="true"></div>
<main class="root-splash">
  <img class="root-splash__logo" src="assets/img/logo-192.png" width="120" height="120" alt="Kabirloole">
  <div class="root-splash__langs">{cards}</div>
</main>
</body>
</html>
"""


def render_404() -> str:
    """Served by the web server for any missing URL, so asset paths are absolute."""
    blocks = "".join(
        f'<section lang="{l}" dir="{CONTENT[l]["dir"]}" class="nf__block"><h1>{e(CONTENT[l]["notfound"]["title"])}</h1>'
        f'<p>{e(CONTENT[l]["notfound"]["text"])}</p><a class="btn btn--primary" href="/{l}/index.html">{e(CONTENT[l]["ui"]["home"])}</a></section>'
        for l in LANGS
    )
    return f"""<!doctype html>
<html lang="{DEFAULT_LANG}" dir="{CONTENT[DEFAULT_LANG]['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>404 | Kabirloole</title>
<meta name="robots" content="noindex">
<link rel="stylesheet" href="/assets/css/main.css?v={ASSET_VERSION}">
</head>
<body class="page-root">
<div class="paper" aria-hidden="true"></div>
<main class="root-splash nf">
  <strong class="nf__code">۴۰۴</strong>
  {blocks}
</main>
</body>
</html>
"""


def render_manifest() -> str:
    t = CONTENT[DEFAULT_LANG]
    return json.dumps(
        {
            "name": f"{t['brand']} | Kabirloole",
            "short_name": t["brand"],
            "lang": DEFAULT_LANG,
            "dir": t["dir"],
            "start_url": f"{DEFAULT_LANG}/index.html",
            "display": "standalone",
            "background_color": "#f2efe6",
            "theme_color": "#2e8b4a",
            "icons": [
                {"src": "assets/img/logo-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "assets/img/logo-512.png", "sizes": "512x512", "type": "image/png"},
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


def write_articles() -> None:
    t = CONTENT[ARTICLE_LANG]
    for article in ARTICLES:
        html = render_page(ARTICLE_LANG, article.page, lambda _t, a=article: article_body(a, t), article_info(article, t))
        (ROOT / ARTICLE_LANG / f"{article.page}.html").write_text(html, encoding="utf-8")


def remove_stale_articles() -> None:
    """Article pages whose Markdown file was deleted or renamed."""
    current = {f"{a.page}.html" for a in ARTICLES}
    for lang in LANGS:
        for path in (ROOT / lang).glob("blog-*.html"):
            if path.name not in current or lang != ARTICLE_LANG:
                path.unlink()


def write_seo_files() -> None:
    pages = [(l, p) for l in LANGS for p in PAGES] + [(ARTICLE_LANG, a.page) for a in ARTICLES]
    urls = "".join(f"<url><loc>{page_url(l, p)}</loc></url>" for l, p in pages)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nDisallow: /admin/\nDisallow: /api/\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8"
    )


def main() -> None:
    check_content()
    check_fonts()
    for lang in LANGS:
        out_dir = ROOT / lang
        out_dir.mkdir(exist_ok=True)
        for page in PAGES:
            (out_dir / f"{page}.html").write_text(render_page(lang, page, PAGE_BUILDERS[page]), encoding="utf-8")
    remove_stale_articles()
    write_articles()
    (ROOT / "index.html").write_text(render_root(), encoding="utf-8")
    (ROOT / "404.html").write_text(render_404(), encoding="utf-8")
    (ROOT / "site.webmanifest").write_text(render_manifest() + "\n", encoding="utf-8")
    if SITE_URL:
        write_seo_files()
    css = build_css()
    fonts = build_embedded_fonts()
    js = build_js()
    js_note = f"main.js {js / 1024:.1f} KB" if js is not None else "main.js skipped (no tsc on PATH)"
    print(
        f"Built {len(LANGS) * len(PAGES)} pages, {len(ARTICLES)} articles + index, 404, manifest; "
        f"main.css {css / 1024:.1f} KB, fonts-embedded.css {fonts / 1024:.0f} KB, {js_note}"
    )


if __name__ == "__main__":
    main()
