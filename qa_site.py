"""Check published HTML links and required static assets before release."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
import json

docs = Path(__file__).parent / "docs"
errors = []


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag in ("a", "script", "link", "img", "source"):
            value = values.get("href") or values.get("src")
            if value:
                self.links.append((tag, value))
        if tag == "script" and values.get("src", "").startswith(("http:", "https:")):
            errors.append("External script in " + str(self))


parsed = {}
for file in docs.rglob("*.html"):
    parser = Inspector()
    parser.feed(file.read_text(encoding="utf-8"))
    parsed[file.resolve()] = parser

for file, parser in parsed.items():
    for tag, raw in parser.links:
        parts = urlsplit(raw)
        if parts.scheme or parts.netloc:
            continue
        target = (file.parent / unquote(parts.path)).resolve() if parts.path else file
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            errors.append(f"Missing target: {file.name}: {raw}")
        elif tag == "a" and parts.fragment and target in parsed and parts.fragment not in parsed[target].ids:
            errors.append(f"Missing anchor: {file.name}: {raw}")

for name in ("updates.json", "media.json"):
    json.loads((docs / "data" / name).read_text(encoding="utf-8"))

updates = json.loads((docs / "data" / "updates.json").read_text(encoding="utf-8"))["updates"]
ids = [item["id"] for item in updates]
if len(ids) != len(set(ids)):
    errors.append("Duplicate update ids")
feed_items = ET.parse(docs / "updates.xml").getroot().findall("./channel/item")
if len(feed_items) != len(updates):
    errors.append("Updates feed count differs from JSON")
sitemap = (docs / "sitemap.xml").read_text(encoding="utf-8")
for item in updates:
    target = docs / "updates" / (item["id"] + ".html")
    url = "https://wavesurvivorsupport-glitch.github.io/WaveSurvivor-Legal/updates/" + item["id"] + ".html"
    if not target.exists() or item["headline"] not in target.read_text(encoding="utf-8"):
        errors.append("Missing or stale update page: " + item["id"])
    if url not in sitemap:
        errors.append("Update missing from sitemap: " + item["id"])
feed_links = [node.findtext("link") for node in feed_items]
expected_links = ["https://wavesurvivorsupport-glitch.github.io/WaveSurvivor-Legal/updates/" + item["id"] + ".html" for item in updates]
if set(feed_links) != set(expected_links):
    errors.append("Updates feed links differ from JSON")
feed_by_link = {node.findtext("link"): node for node in feed_items}
for item, url in zip(updates, expected_links):
    node = feed_by_link.get(url)
    if node is None:
        continue
    if node.findtext("title") != item["headline"] or node.findtext("description") != item["summary"]:
        errors.append("Updates feed content differs from JSON: " + item["id"])
    published = node.findtext("pubDate")
    if (parsedate_to_datetime(published).date().isoformat() if published else None) != item.get("date"):
        errors.append("Updates feed date differs from JSON: " + item["id"])
if feed_links:
    home = (docs / "index.html").read_text(encoding="utf-8")
    if 'href="updates/' + feed_links[0].rsplit("/", 1)[1] + '"' not in home:
        errors.append("Homepage latest update is stale")

for name in ("legal/privacy.html", "legal/terms.html"):
    text = (docs / name).read_text(encoding="utf-8")
    if "wavesurvivor.support@gmail.com" not in text:
        errors.append(f"Missing support email in {name}")

if errors:
    raise SystemExit("\n".join(errors))
print(f"Checked {len(parsed)} HTML pages, local links, anchors, data JSON and legal contact.")
