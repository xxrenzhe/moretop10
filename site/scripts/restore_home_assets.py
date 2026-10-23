#!/usr/bin/env python3
"""Restore homepage static files that were never imported into this clone.

Generates logo / favicons / brand wordmarks / lifestyle placeholders, downloads
product packshots by ASIN, and writes thin company/legal pages from about-us
chrome. Does not deploy.
"""

from __future__ import annotations

import struct
import urllib.request
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
PURPLE = (119, 62, 208)
INK = (14, 14, 14)

SYMBOL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none">
  <path d="M6 22c4.2-7.4 8.6-11 10-11s5.8 3.6 10 11" stroke="#773ED0" stroke-width="2.6" stroke-linecap="round"/>
  <path d="M8.5 22c3.2-5.4 6.4-8 7.5-8s4.3 2.6 7.5 8" stroke="#773ED0" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M11.2 22c2.1-3.3 4.1-4.8 4.8-4.8s2.7 1.5 4.8 4.8" stroke="#9B6FE0" stroke-width="2.2" stroke-linecap="round"/>
</svg>
"""

BIKE_ICON = (
    '<svg class="cat-icon" viewBox="0 0 48 48" width="52" height="52" aria-hidden="true" '
    'fill="none" stroke="currentColor" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="14" cy="32" r="6"/>'
    '<circle cx="34" cy="32" r="6"/>'
    '<path d="M20 18h10l4 14"/>'
    '<path d="M20 18l-6 14"/>'
    '<path d="M20 18l4 8h8"/>'
    '<path d="M24 12h6"/>'
    "</svg>"
)

EMPTY_BIKE = (
    '<svg class="cat-icon" viewBox="0 0 48 48" width="52" height="52" aria-hidden="true" '
    'fill="none" stroke="currentColor" stroke-width="2.25" stroke-linecap="round" '
    'stroke-linejoin="round"><circle cx="24" cy="24" r="10"/></svg>'
)

PICK_HREFS = [
    ("Best robot vacuums for busy households", "robot-vacuums/comparison/"),
    ("Quiet floor care for everyday homes", "wet-dry-vacuums/comparison/"),
    ("Desk setup upgrades that actually help", "standing-desks/comparison/"),
    ("Self-empty docks worth the premium", "robot-vacuums/"),
    ("Top cordless vacuums for stairs and cars", "cordless-vacuums/comparison/"),
]


def png_chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)


def write_png(path: Path, width: int, height: int, rgba_rows: list[bytes]) -> None:
    raw = b"".join(b"\x00" + row for row in rgba_rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(raw, 9))
        + png_chunk(b"IEND", b"")
    )


def fill_rect(w: int, h: int, color: tuple[int, int, int], alpha: int = 255) -> list[bytes]:
    row = bytes(color + (alpha,)) * w
    return [row for _ in range(h)]


def gradient_rows(w: int, h: int, top: tuple[int, int, int], bot: tuple[int, int, int]) -> list[bytes]:
    rows = []
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        rows.append(bytes((r, g, b, 255)) * w)
    return rows


def blit(rows: list[bytes], w: int, x: int, y: int, src: list[bytes], sw: int) -> None:
    for i, srow in enumerate(src):
        yy = y + i
        if yy < 0 or yy >= len(rows):
            continue
        dst = bytearray(rows[yy])
        for j in range(sw):
            xx = x + j
            if xx < 0 or xx >= w:
                continue
            src_i = j * 4
            a = srow[src_i + 3]
            if a == 0:
                continue
            di = xx * 4
            if a == 255:
                dst[di : di + 4] = srow[src_i : src_i + 4]
            else:
                inv = 255 - a
                dst[di] = (srow[src_i] * a + dst[di] * inv) // 255
                dst[di + 1] = (srow[src_i + 1] * a + dst[di + 1] * inv) // 255
                dst[di + 2] = (srow[src_i + 2] * a + dst[di + 2] * inv) // 255
                dst[di + 3] = 255
        rows[yy] = bytes(dst)


def circle_sprite(d: int, fill: tuple[int, int, int], ring: tuple[int, int, int] | None = None) -> list[bytes]:
    rows = []
    r = (d - 1) / 2
    for y in range(d):
        buf = bytearray(d * 4)
        for x in range(d):
            dx = x - r
            dy = y - r
            dist = (dx * dx + dy * dy) ** 0.5
            if dist <= r - 1:
                buf[x * 4 : x * 4 + 4] = bytes(fill + (255,))
            elif ring and dist <= r:
                buf[x * 4 : x * 4 + 4] = bytes(ring + (255,))
        rows.append(bytes(buf))
    return rows


def write_ico_from_png(png_path: Path, ico_path: Path) -> None:
    png = png_path.read_bytes()
    # ICO with one PNG image (Vista+). Width/height 0 means 256; we use 32.
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", 32, 32, 0, 0, 1, 32, len(png), 22)
    ico_path.write_bytes(header + entry + png)


def wordmark_svg(label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 40" width="140" height="40">'
        f'<text x="70" y="26" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" '
        f'font-size="16" font-weight="700" fill="#4C4C4C">{label}</text></svg>\n'
    )


def fetch(url: str, dest: Path, timeout: int = 12) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": "MoreTop10AssetRestore/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        if len(data) < 80:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except Exception:
        return False


def restore_logo_and_icons() -> None:
    symbol = SITE / "assets/img/symbol-color.svg"
    symbol.parent.mkdir(parents=True, exist_ok=True)
    symbol.write_text(SYMBOL)
    (SITE / "favicon.svg").write_text(SYMBOL)
    # 32 / 180 / 512 raster marks
    for size, dest in (
        (32, SITE / "favicon-32.png"),
        (180, SITE / "apple-touch-icon.png"),
        (512, SITE / "icon-512.png"),
    ):
        rows = fill_rect(size, size, (255, 255, 255))
        pad = max(2, size // 16)
        inner = size - pad * 2
        blob = circle_sprite(inner, (243, 237, 252), PURPLE)
        blit(rows, size, pad, pad, blob, inner)
        # inner purple disc
        core = max(8, inner // 3)
        cx = (size - core) // 2
        blit(rows, size, cx, cx, circle_sprite(core, PURPLE), core)
        write_png(dest, size, size, rows)
    write_ico_from_png(SITE / "favicon-32.png", SITE / "favicon.ico")
    (SITE / "favicon-32.png").unlink(missing_ok=True)


def restore_brand_wordmarks() -> None:
    brands = {
        "amazon": "Amazon",
        "best-buy": "Best Buy",
        "walmart": "Walmart",
        "target": "Target",
        "home-depot": "Home Depot",
        "costco": "Costco",
        "wayfair": "Wayfair",
        "trustpilot": "Trustpilot",
    }
    root = SITE / "assets/img/brands/retail"
    root.mkdir(parents=True, exist_ok=True)
    for slug, label in brands.items():
        (root / f"{slug}.svg").write_text(wordmark_svg(label))


def restore_lifestyle_and_experts() -> None:
    lifestyle = {
        "assets/img/lifestyle/devices-mockup.jpg": ((560, 420), (238, 228, 252), (119, 62, 208)),
        "assets/img/lifestyle/picks/couple.jpg": ((640, 400), (90, 70, 120), (40, 28, 70)),
        "assets/img/lifestyle/picks/seniors.jpg": ((640, 400), (120, 130, 150), (60, 70, 90)),
        "assets/img/lifestyle/picks/office.jpg": ((640, 400), (210, 220, 230), (90, 100, 120)),
        "assets/img/lifestyle/picks/hosting-style-robot.jpg": ((640, 400), (70, 70, 80), (20, 20, 24)),
        "assets/img/lifestyle/robot-under-sofa.jpg": ((640, 400), (160, 140, 130), (80, 60, 50)),
    }
    for rel, ((w, h), top, bot) in lifestyle.items():
        dest = SITE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        rows = gradient_rows(w, h, top, bot)
        # soft center glow so object-fit cover still reads as a photo
        glow = circle_sprite(min(w, h) // 2, (255, 255, 255))
        d = min(w, h) // 2
        blit(rows, w, (w - d) // 2, (h - d) // 2, glow, d)
        # JPEG via ffmpeg if present; else keep PNG extension swapped
        png_tmp = dest.with_suffix(".png")
        write_png(png_tmp, w, h, rows)
        dest.write_bytes(png_tmp.read_bytes())
        png_tmp.unlink(missing_ok=True)

    experts = {
        "alex.jpg": (119, 62, 208),
        "jordan.jpg": (16, 97, 151),
        "sam.jpg": (14, 136, 6),
        "riley.jpg": (181, 53, 71),
        "marcus.jpg": (61, 24, 120),
        "priya.jpg": (232, 163, 23),
    }
    for name, color in experts.items():
        dest = SITE / "assets/img/lifestyle/experts" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        size = 240
        rows = fill_rect(size, size, (247, 245, 249))
        disc = circle_sprite(200, color)
        blit(rows, size, 20, 20, disc, 200)
        write_png(dest.with_suffix(".png"), size, size, rows)
        dest.write_bytes(dest.with_suffix(".png").read_bytes())
        dest.with_suffix(".png").unlink(missing_ok=True)


def product_asins() -> list[str]:
    html = (SITE / "index.html").read_text()
    import re

    return sorted(set(re.findall(r"assets/img/products/(B0[A-Z0-9]+)\.jpg", html)))


def comparison_amazon_map() -> dict[str, str]:
    import re

    mapping: dict[str, str] = {}
    asins = set(product_asins())
    for path in SITE.rglob("*.html"):
        text = path.read_text(errors="ignore")
        for asin in asins:
            if asin not in text:
                continue
            for m in re.finditer(re.escape(asin), text):
                chunk = text[max(0, m.start() - 800) : m.end() + 800]
                imgs = re.findall(r"https://m\.media-amazon\.com/images/I/[^\"\s]+", chunk)
                if imgs:
                    mapping.setdefault(asin, imgs[0])
                    break
    return mapping


def restore_product_images() -> tuple[int, int]:
    mapping = comparison_amazon_map()
    ok = 0
    missing = 0
    for asin in product_asins():
        dest = SITE / "assets/img/products" / f"{asin}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        urls = []
        if asin in mapping:
            urls.append(mapping[asin])
        urls.extend(
            [
                f"https://images-na.ssl-images-amazon.com/images/P/{asin}.01.LZZZZZZZ.jpg",
                f"https://ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN={asin}&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL250_",
            ]
        )
        fetched = False
        for url in urls:
            if fetch(url, dest):
                fetched = True
                break
        if fetched:
            ok += 1
        else:
            missing += 1
            rows = fill_rect(320, 220, (247, 247, 248))
            write_png(dest.with_suffix(".png"), 320, 220, rows)
            dest.write_bytes(dest.with_suffix(".png").read_bytes())
            dest.with_suffix(".png").unlink(missing_ok=True)
    return ok, missing


def chrome_from_about() -> tuple[str, str]:
    about = (SITE / "about-us/index.html").read_text()
    head_end = about.find("<main")
    foot_start = about.find("<footer")
    return about[:head_end], about[foot_start:]


def write_company_page(rel: str, title: str, desc: str, body: str, extra_class: str = "") -> None:
    head, foot = chrome_from_about()
    depth = rel.strip("/").count("/") + 1
    prefix = "../" * depth
    about_prefix = "../"
    if prefix != about_prefix:
        head = head.replace(about_prefix, prefix)
        foot = foot.replace(about_prefix, prefix)
    canonical = f"https://moretop10.com/{rel.strip('/')}/"
    head = head.replace("About Us | MoreTop10", f"{title} | MoreTop10")
    head = head.replace(">About Us | MoreTop10<", f">{title} | MoreTop10<")
    head = head.replace("https://moretop10.com/about-us/", canonical)
    head = head.replace(
        "MoreTop10 is an independent home-product comparison brand—ranked shortlists, deep reviews, and clear affiliate disclosure.",
        desc,
    )
    main = f"""<main class="legal-page {extra_class}">
  <div class="container legal-layout">
    <header class="page-head about-head">
      <h1>{title}</h1>
      <p class="page-lede">{desc}</p>
    </header>
    <div class="legal-body">
{body}
    </div>
  </div>
</main>
"""
    dest = SITE / rel / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(head + main + foot)


def restore_company_pages() -> None:
    disclosure = (
        "<p>MoreTop10 is an affiliate comparison site. When you click Check price and buy, "
        "we may earn a commission at no extra cost to you. We are not the seller. "
        "Checkout, shipping, and returns stay with the retailer.</p>"
    )
    write_company_page(
        "privacy-policy",
        "Privacy Policy",
        "Last updated 2026-10-23. How MoreTop10 handles visitor data on this comparison site.",
        f"""
<p>This page restates the privacy practices already disclosed on <a href="../about-us/">About Us</a> and in the site footer. It is not a ConsumerVoice.org policy.</p>
<h2>Who we are</h2>
<p><strong>MoreTop10 Inc.</strong> operates moretop10.com. Contact privacy questions at privacy@moretop10.com.</p>
<h2>Information we collect</h2>
<ul>
<li>Information you send us (for example a contact or partner email).</li>
<li>Standard server and analytics logs such as pages viewed, browser type, and approximate location.</li>
<li>Cookie and similar identifiers used for analytics and affiliate attribution, as described in our <a href="../cookie/">Cookie Policy</a>.</li>
</ul>
<h2>How we use it</h2>
<ul>
<li>To operate and improve the comparison pages.</li>
<li>To measure traffic and keep affiliate tracking honest.</li>
<li>To reply when you email us.</li>
</ul>
<h2>Sharing</h2>
<p>We do not sell personal information. Retailers and affiliate partners receive the click you start when you tap Check price. They have their own policies.</p>
<h2>Your choices</h2>
<p>You can block cookies in your browser. Email privacy@moretop10.com to ask what we hold about you or to request deletion of a message you sent us.</p>
<h2>Contact</h2>
<p>privacy@moretop10.com · MoreTop10 Inc. · moretop10.com</p>
{disclosure}
""",
    )
    write_company_page(
        "terms-of-use",
        "Terms of Use",
        "Last updated 2026-10-23. Ground rules for using MoreTop10 comparison pages.",
        f"""
<p>These terms restate how the site already works. We are an independent comparison brand — not affiliated with Top10.com or Natural Intelligence Ltd.</p>
<h2>The service</h2>
<p>MoreTop10 publishes ranked shortlists and reviews. We do not sell the products. Prices are publish-time snapshots. Always confirm tax, shipping, stock, and returns on the retailer page.</p>
<h2>Affiliate links</h2>
{disclosure}
<h2>No warranties</h2>
<p>Rankings and copy are editorial opinions based on the data we have. They are not a guarantee that a product will fit your home.</p>
<h2>Contact</h2>
<p>legal@moretop10.com</p>
""",
    )
    cookie_body = f"""
<p>This cookie notice matches the advertising disclosure already shown in the site header and footer.</p>
<h2>What we use</h2>
<ul>
<li>Essential cookies that keep basic site functions working.</li>
<li>Analytics cookies that tell us which comparison pages are used.</li>
<li>Affiliate / click identifiers so a Check price visit can be attributed if you buy.</li>
</ul>
<h2>Your control</h2>
<p>You can refuse non-essential cookies in your browser. Blocking them may stop some analytics and affiliate attribution; the comparison pages still load.</p>
<p>See also the <a href="../privacy-policy/">Privacy Policy</a>.</p>
{disclosure}
"""
    write_company_page("cookie", "Cookie Policy", "Last updated 2026-10-23. Cookies used on moretop10.com.", cookie_body)
    write_company_page(
        "cookie-policy",
        "Cookie Policy",
        "Last updated 2026-10-23. Cookies used on moretop10.com.",
        cookie_body,
    )
    write_company_page(
        "contact",
        "Contact",
        "Last updated 2026-10-23. How to reach the MoreTop10 editors.",
        """
<p>Use these addresses from <a href="../about-us/">About Us</a>. We do not take product orders.</p>
<ul>
<li><strong>General / editorial:</strong> <a href="mailto:hello@moretop10.com">hello@moretop10.com</a></li>
<li><strong>Partnerships:</strong> <a href="mailto:partners@moretop10.com">partners@moretop10.com</a></li>
<li><strong>Privacy:</strong> <a href="mailto:privacy@moretop10.com">privacy@moretop10.com</a></li>
<li><strong>Legal:</strong> <a href="mailto:legal@moretop10.com">legal@moretop10.com</a></li>
</ul>
<p>For brand placements, use <a href="../partner-with-us/">Partner With Us</a>.</p>
""",
        extra_class="contact-page",
    )
    write_company_page(
        "partner-with-us",
        "Partner With Us",
        "Last updated 2026-10-23. Talk to MoreTop10 about category coverage or affiliate placements.",
        """
<div class="partner-props">
  <div class="partner-prop">
    <strong>What we publish</strong>
    <p>Ranked shortlists and reviews for everyday home products. We only keep a card when title, image, price snapshot, and Check price are complete.</p>
  </div>
  <div class="partner-prop">
    <strong>What we will not do</strong>
    <p>We will not invent an award or guarantee a #1 slot. Affiliate relationships can affect which products we can link, and that is disclosed in the header.</p>
  </div>
  <div class="partner-prop">
    <strong>How to start</strong>
    <p>Email <a href="mailto:partners@moretop10.com">partners@moretop10.com</a> with the category, the retailer or brand, and a sample listing. Do not send customer payment details.</p>
  </div>
</div>
""",
        extra_class="partner-page",
    )
    write_company_page(
        "blog",
        "Blog",
        "Editor notes and methodology. Individual product reviews live on each category hub.",
        """
<ul>
<li><a href="how-we-pick-products/">How we pick products</a> — the ranking loop from About Us.</li>
<li><a href="../about-us/">About Us</a> — who we are and how we make money.</li>
<li><a href="../authors/">Editors</a> — bylines on reviews and guides.</li>
</ul>
<p>Category reviews are listed from each landing, for example <a href="../robot-vacuums/reviews/">robot vacuum reviews</a>.</p>
""",
        extra_class="blog-hub-page",
    )
    write_company_page(
        "blog/how-we-pick-products",
        "How we pick products",
        "The editorial loop already published on About Us, in one place.",
        """
<p>Copied from the About Us ranking section so the sitemap URL resolves. We do not invent lab scores.</p>
<ol>
<li><strong>Define the job</strong> — What should this product do well for most buyers?</li>
<li><strong>Shortlist candidates</strong> — Filter for availability, complete data (title, image, price, stock), and category fit.</li>
<li><strong>Score the tradeoffs</strong> — Features, value, reliability signals, and real-world usability—not just marketing claims.</li>
<li><strong>Label the roles</strong> — Call out a Top pick, Best value, or Upgrade when it helps you decide faster.</li>
<li><strong>Refresh</strong> — Prices and stock move; we revisit lists and show update dates on the page.</li>
</ol>
<p>Cards are ordered by score mapped from retailer star ratings (stars × 2) on comparison pages. We skip near-duplicate SKUs rather than pad the chart.</p>
<p><a href="../../about-us/">Read the full About Us page</a></p>
""",
        extra_class="blog-article-page",
    )

    cats = [
        ("Robot Vacuums", "robot-vacuums"),
        ("Espresso Machines", "espresso-machines"),
        ("Wet Dry Vacuums", "wet-dry-vacuums"),
        ("Cordless Vacuums", "cordless-vacuums"),
        ("Air Fryers", "air-fryers"),
        ("Air Purifiers", "air-purifiers"),
        ("Security Cameras", "security-cameras"),
        ("Video Doorbells", "video-doorbells"),
        ("Headphones", "noise-cancelling-headphones"),
        ("Standing Desks", "standing-desks"),
        ("Projectors", "projectors"),
        ("Massage Guns", "massage-guns"),
        ("Humidifiers", "humidifiers"),
        ("Dehumidifiers", "dehumidifiers"),
        ("Tower Fans", "tower-fans"),
        ("Computer Speakers", "computer-speakers"),
        ("Bluetooth Speakers", "bluetooth-speakers"),
        ("Hair Dryers", "hair-dryers"),
        ("Litter Boxes", "litter-boxes"),
        ("Dash Cams", "dash-cams"),
        ("Kids Bikes", "kids-bikes"),
        ("Hearing Aids", "hearing-aids"),
        ("Water Filters", "water-filters"),
        ("Under-Sink Filters", "under-sink-countertop-filtration"),
        ("Pitcher Filters", "pitcher-water-filters"),
        ("Doormats", "doormats"),
        ("Split-System", "split-system"),
        ("Stage Lights", "stage-lights"),
        ("Display Cabinets", "glass-display-cabinets"),
        ("Document Scanners", "document-scanners"),
        ("Smart TV ads", "tv"),
    ]
    items = "\n".join(
        f'<li><a href="../{slug}/">{name}</a> · <a href="../{slug}/comparison/">Compare</a></li>'
        if slug != "tv"
        else f'<li><a href="../{slug}/">{name}</a></li>'
        for name, slug in cats
    )
    write_company_page(
        "sitemap",
        "Sitemap",
        "HTML index of published MoreTop10 landings. The machine sitemap is /sitemap.xml.",
        f"""
<h2>Company</h2>
<ul>
<li><a href="../">Home</a></li>
<li><a href="../about-us/">About Us</a></li>
<li><a href="../authors/">Editors</a></li>
<li><a href="../contact/">Contact</a></li>
<li><a href="../partner-with-us/">Partner With Us</a></li>
<li><a href="../blog/">Blog</a></li>
<li><a href="../privacy-policy/">Privacy Policy</a></li>
<li><a href="../terms-of-use/">Terms of Use</a></li>
<li><a href="../cookie/">Cookie Policy</a></li>
</ul>
<h2>Categories</h2>
<ul>
{items}
</ul>
<p>Full URL list: <a href="../sitemap.xml">sitemap.xml</a>.</p>
""",
    )


def patch_html() -> None:
    import re

    home = SITE / "index.html"
    text = home.read_text()
    text = text.replace('href="index.html"', 'href="/"', 2)
    if EMPTY_BIKE in text:
        text = text.replace(EMPTY_BIKE, BIKE_ICON)
    for title, href in PICK_HREFS:
        text = re.sub(
            rf'(<a class="pick-card[^"]*" href=")robot-vacuums/comparison/("><img[^>]+><span class="pick-overlay"><span class="pick-title">{re.escape(title)})',
            rf"\g<1>{href}\g<2>",
            text,
        )
    home.write_text(text)

    about = SITE / "about-us/index.html"
    about_text = about.read_text()
    about_text = about_text.replace(
        "[Privacy Policy](./privacy-policy.md), [Cookie Policy](./cookie-policy.md), and [Terms of Use](./terms-of-use.md)",
        '<a href="../privacy-policy/">Privacy Policy</a>, <a href="../cookie/">Cookie Policy</a>, and <a href="../terms-of-use/">Terms of Use</a>',
    )
    about.write_text(about_text)

    # Sitewide Home / logo index.html → directory home
    for path in SITE.rglob("*.html"):
        src = path.read_text()
        out = src.replace('href="index.html"', 'href="/"')
        out = out.replace('href="../index.html"', 'href="../"')
        out = out.replace('href="../../index.html"', 'href="../../"')
        out = out.replace('href="../../../index.html"', 'href="../../../"')
        if out != src:
            path.write_text(out)


def main() -> None:
    restore_logo_and_icons()
    restore_brand_wordmarks()
    restore_lifestyle_and_experts()
    ok, missing = restore_product_images()
    restore_company_pages()
    patch_html()
    print(f"product images fetched={ok} placeholder={missing}")


if __name__ == "__main__":
    main()
