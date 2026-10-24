#!/usr/bin/env python3
"""Build the Updates pages, sitemap.xml and feed.xml from posts/*.html.

Each post file starts with an HTML comment holding JSON:
  {"version": "...", "date": "YYYY-MM-DD", "title": "...", "summary": "..."}
followed by the post body as HTML.

Run from the repo root:  python3 tools/build.py
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://in-sky.eu"
TAGLINE = "mc.in-sky.eu: a vanilla-style OneBlock server where every island is its own private world."


def load_posts():
    posts = []
    for path in sorted((ROOT / "posts").glob("*.html")):
        text = path.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--(.*?)-->(.*)", text, re.S)
        if not m:
            raise SystemExit(f"{path.name}: missing JSON header comment")
        meta = json.loads(m.group(1))
        meta["body"] = m.group(2).strip()
        meta["slug"] = path.stem
        meta["url"] = f"{SITE}/updates/{path.stem}/"
        date.fromisoformat(meta["date"])  # fail early on a bad date
        posts.append(meta)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def page(title, description, canonical, body, jsonld):
    e = html.escape
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta name="color-scheme" content="light dark">
<link rel="alternate" type="application/rss+xml" title="IN-SKY.EU updates" href="/feed.xml">
<link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">
{json.dumps(jsonld, indent=2, ensure_ascii=False)}
</script>
</head>
<body>
<nav aria-label="Site">
  <div class="wrap">
    <ul>
      <li><a href="/">IN-SKY.EU</a></li>
      <li><a href="/#features">Features</a></li>
      <li><a href="/#join">How to join</a></li>
      <li><a href="/updates/">Updates</a></li>
      <li><a href="/#faq">FAQ</a></li>
    </ul>
  </div>
</nav>
<main class="wrap">
{body}
</main>
<footer>
  <div class="wrap">
    <p><strong>IN-SKY.EU</strong> · Server address: <code>mc.in-sky.eu</code> · Java Edition 26.3 · Open beta</p>
    <p><a href="https://discord.in-sky.eu">Discord</a> · <a href="https://feedback.in-sky.eu">Report a bug</a> · <a href="/feed.xml">RSS feed</a></p>
    <p>Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft.</p>
  </div>
</footer>
</body>
</html>
"""


def pretty_date(d):
    return date.fromisoformat(d).strftime("%-d %B %Y")


def build_post(p, newer, older):
    e = html.escape
    pager = []
    if older:
        pager.append(f'<a href="/updates/{older["slug"]}/">← {e(older["version"])}</a>')
    if newer:
        pager.append(f'<a href="/updates/{newer["slug"]}/">{e(newer["version"])} →</a>')
    body = f"""<article>
<header class="post-head">
  <p class="crumbs"><a href="/updates/">Updates</a></p>
  <h1>{e(p["title"])}</h1>
  <p class="meta">Version {e(p["version"])} · <time datetime="{p["date"]}">{pretty_date(p["date"])}</time></p>
  <p class="lead">{e(p["summary"])}</p>
</header>
{p["body"]}
<p class="note">Found a bug? Report it at <a href="https://feedback.in-sky.eu">feedback.in-sky.eu</a> or tell us on <a href="https://discord.in-sky.eu">Discord</a>.</p>
</article>
<p class="pager">{" ".join(pager)}</p>"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": p["title"],
        "description": p["summary"],
        "datePublished": p["date"],
        "url": p["url"],
        "mainEntityOfPage": p["url"],
        "inLanguage": "en",
        "author": {"@type": "Organization", "name": "IN-SKY.EU", "url": SITE + "/"},
        "publisher": {"@id": SITE + "/#org"},
        "isPartOf": {"@type": "Blog", "@id": SITE + "/updates/#blog"},
    }
    out = ROOT / "updates" / p["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(f'{p["title"]} | IN-SKY.EU', p["summary"], p["url"], body, jsonld), encoding="utf-8")


def build_index(posts):
    e = html.escape
    items = "\n".join(
        f"""  <li>
    <h2><a href="/updates/{p["slug"]}/">{e(p["title"])}</a></h2>
    <p class="meta">Version {e(p["version"])} · <time datetime="{p["date"]}">{pretty_date(p["date"])}</time></p>
    <p>{e(p["summary"])}</p>
  </li>"""
        for p in posts
    )
    body = f"""<header class="post-head">
  <h1>Updates</h1>
  <p class="lead">What changed on IN-SKY.EU, newest first. We are in open beta, so updates come often.</p>
</header>
<ul class="posts">
{items}
</ul>"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "@id": SITE + "/updates/#blog",
        "name": "IN-SKY.EU updates",
        "url": SITE + "/updates/",
        "description": "Release notes for the IN-SKY.EU OneBlock server.",
        "publisher": {"@id": SITE + "/#org"},
        "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"], "datePublished": p["date"]} for p in posts],
    }
    out = ROOT / "updates" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page("Updates | IN-SKY.EU OneBlock server", "Release notes for IN-SKY.EU, a vanilla-style OneBlock server for Minecraft Java 26.3.", SITE + "/updates/", body, jsonld), encoding="utf-8")


def build_sitemap(posts):
    newest = posts[0]["date"] if posts else date.today().isoformat()
    home_mod = max(newest, (ROOT / ".home-lastmod").read_text().strip()) if (ROOT / ".home-lastmod").exists() else newest
    urls = [(SITE + "/", home_mod), (SITE + "/updates/", newest)] + [(p["url"], p["date"]) for p in posts]
    rows = "\n".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n  </url>" for u, d in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n',
        encoding="utf-8")


def build_feed(posts):
    e = html.escape
    def rfc822(d):
        return date.fromisoformat(d).strftime("%a, %d %b %Y 00:00:00 +0000")
    items = "\n".join(
        f"""  <item>
    <title>{e(p["title"])}</title>
    <link>{p["url"]}</link>
    <guid>{p["url"]}</guid>
    <pubDate>{rfc822(p["date"])}</pubDate>
    <description>{e(p["summary"])}</description>
  </item>"""
        for p in posts
    )
    (ROOT / "feed.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>IN-SKY.EU updates</title>
  <link>{SITE}/updates/</link>
  <description>{e(TAGLINE)}</description>
  <language>en</language>
{items}
</channel>
</rss>
""", encoding="utf-8")


def main():
    posts = load_posts()
    for i, p in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        build_post(p, newer, older)
    build_index(posts)
    build_sitemap(posts)
    build_feed(posts)
    print(f"Built {len(posts)} posts: " + ", ".join(p["version"] for p in posts))


if __name__ == "__main__":
    main()
