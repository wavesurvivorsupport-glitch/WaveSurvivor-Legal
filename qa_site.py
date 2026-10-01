"""Check published HTML links and required static assets before release."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
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

for name in ("legal/privacy.html", "legal/terms.html"):
    text = (docs / name).read_text(encoding="utf-8")
    if "wavesurvivor.support@gmail.com" not in text:
        errors.append(f"Missing support email in {name}")

if errors:
    raise SystemExit("\n".join(errors))
print(f"Checked {len(parsed)} HTML pages, local links, anchors, data JSON and legal contact.")
