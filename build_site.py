"""Generate the static pages. Legal documents are maintained separately."""
from pathlib import Path
from html import escape
from datetime import date, datetime, time, timezone
from email.utils import format_datetime
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
BASE = "https://wavesurvivorsupport-glitch.github.io/WaveSurvivor-Legal/"
STEAM = "https://store.steampowered.com/app/5170710/WaveSurvivor/"
EMAIL = "wavesurvivor.support@gmail.com"
ASSET_VERSION = "20261001b"


def update_url(item):
    return f"updates/{item['id']}.html"


def update_label(item):
    version = item.get("version")
    day = item.get("date")
    parts = []
    if version:
        parts.append("v" + version)
    if day:
        published = date.fromisoformat(day)
        parts.append(f"{published:%B} {published.day}, {published.year}")
    return " · ".join(parts) or "Earlier update"


def load_updates():
    data = json.loads((DOCS / "data" / "updates.json").read_text(encoding="utf-8"))
    updates = data.get("updates")
    if not isinstance(updates, list):
        raise ValueError("updates.json requires an updates array")
    seen = set()
    for item in updates:
        slug = item.get("id", "")
        if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in seen:
            raise ValueError(f"Invalid or duplicate update id: {slug!r}")
        seen.add(slug)
        for field in ("headline", "summary"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"{slug}: missing {field}")
        if item.get("date"):
            date.fromisoformat(item["date"])
        if not isinstance(item.get("categories"), list) or not item["categories"]:
            raise ValueError(f"{slug}: categories must be nonempty")
        for category in item["categories"]:
            if not category.get("name") or not isinstance(category.get("changes"), list) or not category["changes"]:
                raise ValueError(f"{slug}: invalid category")
            if any(not isinstance(change, str) or not change.strip() for change in category["changes"]):
                raise ValueError(f"{slug}: empty change")
    def sort_key(item):
        version = tuple(int(part) for part in re.findall(r"\d+", item.get("version") or ""))
        return (item.get("date") or "", version)
    return sorted(updates, key=sort_key, reverse=True)


def update_cards(updates):
    cards = []
    for item in updates:
        label = escape(update_label(item))
        headline = escape(item["headline"])
        summary = escape(item["summary"])
        tags = "".join(f"<span>{escape(category['name'])}</span>" for category in item["categories"])
        cards.append(f'<article class="update-card"><div class="version">{label}</div><div><h2>{headline}</h2><p>{summary}</p><div class="update-tags">{tags}</div></div><a href="{escape(item["id"])}.html" aria-label="Read {headline}">Read update →</a></article>')
    return "\n".join(cards)


def update_article(item, index, updates):
    sections = []
    for category in item["categories"]:
        name = category["name"]
        prefix = name.upper() + ": "
        changes = "".join(f"<li>{escape(change[len(prefix):] if change.upper().startswith(prefix) else change)}</li>" for change in category["changes"])
        sections.append(f"<section class=\"update-section\"><h2>{escape(name)}</h2><ul>{changes}</ul></section>")
    navigation = []
    if index > 0:
        newer = updates[index - 1]
        navigation.append(f'<a href="{escape(newer["id"])}.html">← Newer: {escape(newer["headline"])}</a>')
    if index + 1 < len(updates):
        older = updates[index + 1]
        navigation.append(f'<a href="{escape(older["id"])}.html">Older: {escape(older["headline"])} →</a>')
    image = ""
    if item.get("image") and item.get("imageAlt"):
        image = f'<figure><img src="../{escape(item["image"], quote=True)}" alt="{escape(item["imageAlt"], quote=True)}" loading="lazy"></figure>'
    return (f'<section class="content-section"><div class="wrap article"><a class="text-link back" href="index.html">← All updates</a>'
            f'<article class="update-detail"><p class="eyebrow">{escape(update_label(item))}</p><h1>{escape(item["headline"])}</h1>'
            f'<p class="lead">{escape(item["summary"])}</p>{"".join(sections)}{image}</article>'
            f'<nav class="update-navigation" aria-label="Browse updates">{"".join(navigation)}</nav></div></section>')


def write_feed(updates):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    for tag, value in (("title", "WaveSurvivor Updates"), ("link", BASE + "updates/"),
                       ("description", "Official WaveSurvivor patch notes from Haider Games"), ("language", "en-us")):
        ET.SubElement(channel, tag).text = value
    for item in updates:
        node = ET.SubElement(channel, "item")
        url = BASE + update_url(item)
        for tag, value in (("title", item["headline"]), ("link", url), ("guid", url),
                           ("description", item["summary"])):
            ET.SubElement(node, tag).text = value
        if item.get("date"):
            published = datetime.combine(date.fromisoformat(item["date"]), time.min, tzinfo=timezone.utc)
            ET.SubElement(node, "pubDate").text = format_datetime(published, usegmt=True)
    ET.indent(rss, space="  ")
    ET.ElementTree(rss).write(DOCS / "updates.xml", encoding="utf-8", xml_declaration=True)


def write_sitemap(updates):
    urls = ["", "media.html", "updates/", "support.html", "legal/", "legal/privacy.html", "legal/terms.html"]
    urls.extend(update_url(item) for item in updates)
    body = "\n".join(f"  <url><loc>{escape(BASE + path)}</loc></url>" for path in urls)
    (DOCS / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '\n</urlset>\n', encoding="utf-8")


def page(title, description, url, prefix, content, current):
    destinations = [
        ("Home", "index.html"), ("Game", "index.html#game"),
        ("Story", "index.html#story"), ("Roles", "index.html#roles"),
        ("Media", "media.html"), ("Updates", "updates/index.html"),
        ("FAQ", "index.html#faq"), ("Support", "support.html")
    ]
    nav = "".join(
        '<a href="{}{}"{}>{}</a>'.format(
            prefix, href, ' aria-current="page"' if name == current else "", name
        ) for name, href in destinations
    )
    canonical = BASE + url
    return f"""<!doctype html>
<html lang="en" data-root="{prefix}">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <meta name="description" content="{escape(description, quote=True)}">
  <title>{escape(title)} | WaveSurvivor</title>
  <link rel="canonical" href="{canonical}">
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{prefix}assets/site.css?v={ASSET_VERSION}">
  <link rel="alternate" type="application/rss+xml" title="WaveSurvivor Updates" href="{prefix}updates.xml">
  <meta property="og:type" content="website"><meta property="og:site_name" content="WaveSurvivor">
  <meta property="og:title" content="{escape(title, quote=True)} | WaveSurvivor">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{BASE}assets/og-card.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title, quote=True)} | WaveSurvivor">
  <meta name="twitter:description" content="{escape(description, quote=True)}">
  <meta name="twitter:image" content="{BASE}assets/og-card.png">
  <script defer src="{prefix}assets/site.js?v={ASSET_VERSION}"></script>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header"><div class="wrap head-inner">
    <a class="brand" href="{prefix}index.html" aria-label="WaveSurvivor home"><span class="brand-mark" aria-hidden="true">W</span><span>WAVE<b>SURVIVOR</b></span></a>
    <nav class="desktop-nav" aria-label="Main navigation">{nav}</nav>
    <a class="header-cta" href="{STEAM}" rel="noopener noreferrer">View on Steam ↗</a>
    <details class="mobile-menu"><summary>Menu</summary><nav class="mobile-nav" aria-label="Mobile navigation">{nav}<a href="{STEAM}" rel="noopener noreferrer">View on Steam ↗</a></nav></details>
  </div></header>
  <main id="main">{content}</main>
  <footer class="site-footer"><div class="wrap">
    <div class="footer-grid">
      <div><a class="brand" href="{prefix}index.html"><span class="brand-mark" aria-hidden="true">W</span><span>WAVE<b>SURVIVOR</b></span></a><p>A sci-fi FPS built around teamwork, roles and evolving runs.<br>By Haider Games.</p></div>
      <div><h3>Explore</h3><a href="{prefix}index.html#game">The game</a><a href="{prefix}index.html#story">Story</a><a href="{prefix}index.html#roles">Roles</a><a href="{prefix}media.html">Media</a></div>
      <div><h3>Stay informed</h3><a href="{prefix}updates/index.html">Updates</a><a href="{prefix}index.html#faq">FAQ</a><a href="{prefix}support.html">Support</a><a href="{STEAM}" rel="noopener noreferrer">Steam ↗</a></div>
      <div><h3>Legal & contact</h3><a href="{prefix}legal/privacy.html">Privacy Policy</a><a href="{prefix}legal/terms.html">Terms of Service</a><a href="mailto:{EMAIL}">{EMAIL}</a></div>
    </div>
    <div class="footer-bottom"><span>© 2026 Haider Games · WaveSurvivor</span><span>Official game website · Windows PC</span></div>
  </div></footer>
</body></html>"""


updates = load_updates()
latest = updates[0] if updates else None
latest_html = (f'<p class="overline">Latest public update</p><p class="update-date">{escape(update_label(latest))}</p><h3>{escape(latest["headline"])}</h3><p>{escape(latest["summary"])}</p><a class="text-link" href="{update_url(latest)}">Read update →</a>' if latest else '<p class="overline">Latest public update</p><h3>Game updates are coming.</h3><p>Public patch notes will appear here when they are ready to share.</p><a class="text-link" href="updates/index.html">View updates →</a>')
PAGES = [
    ("index.html", "Official Site", "WaveSurvivor is a sci-fi first-person shooter for offline solo or online co-op. Choose Story or Endless, pick a role and shape your build.", "", "./", "home", "Home"),
    ("media.html", "Media", "Official WaveSurvivor gameplay screenshots, trailer and promotional artwork will appear here.", "media.html", "./", "media", "Media"),
    ("support.html", "Support", "Contact Haider Games for WaveSurvivor technical help, bug reports and multiplayer support.", "support.html", "./", "support", "Support"),
    ("updates/index.html", "Updates", "Official WaveSurvivor public updates and patch notes.", "updates/", "../", "updates", "Updates"),
    ("updates/article.html", "Update Note", "Read a published WaveSurvivor update or patch note.", "updates/article.html", "../", "article", "Updates"),
]
for filename, title, description, url, prefix, fragment, current in PAGES:
    content = (ROOT / "fragments" / (fragment + ".html")).read_text(encoding="utf-8")
    content = content.replace("{{LATEST_UPDATE}}", latest_html)
    content = content.replace("{{UPDATE_COUNT}}", str(len(updates)))
    content = content.replace("{{UPDATES_LIST}}", update_cards(updates))
    target = DOCS / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page(title, description, url, prefix, content, current), encoding="utf-8")
for index, item in enumerate(updates):
    target = DOCS / update_url(item)
    target.write_text(page(item["headline"], item["summary"], update_url(item), "../", update_article(item, index, updates), "Updates"), encoding="utf-8")
write_feed(updates)
write_sitemap(updates)
