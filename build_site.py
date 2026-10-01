"""Generate the static pages. Legal documents are maintained separately."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
BASE = "https://wavesurvivorsupport-glitch.github.io/WaveSurvivor-Legal/"
STEAM = "https://store.steampowered.com/app/5170710/WaveSurvivor/"
EMAIL = "wavesurvivor.support@gmail.com"
ASSET_VERSION = "20261001a"


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


PAGES = [
    ("index.html", "Official Site", "WaveSurvivor is a sci-fi first-person shooter for offline solo or online co-op. Choose Story or Endless, pick a role and shape your build.", "", "./", "home", "Home"),
    ("media.html", "Media", "Official WaveSurvivor gameplay screenshots, trailer and promotional artwork will appear here.", "media.html", "./", "media", "Media"),
    ("support.html", "Support", "Contact Haider Games for WaveSurvivor technical help, bug reports and multiplayer support.", "support.html", "./", "support", "Support"),
    ("updates/index.html", "Updates", "Official WaveSurvivor public updates and patch notes.", "updates/", "../", "updates", "Updates"),
    ("updates/article.html", "Update Note", "Read a published WaveSurvivor update or patch note.", "updates/article.html", "../", "article", "Updates"),
]
for filename, title, description, url, prefix, fragment, current in PAGES:
    content = (ROOT / "fragments" / (fragment + ".html")).read_text(encoding="utf-8")
    target = DOCS / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page(title, description, url, prefix, content, current), encoding="utf-8")
