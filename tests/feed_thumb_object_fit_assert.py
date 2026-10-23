#!/usr/bin/env python3
"""Guard: feed/author thumbs crop instead of stretch when .feed-thumb is on the img.

Live author markup (and the bake) puts both classes on the <img>:

    <img class="author-post-thumb feed-thumb" width="231" height="130" …>

.feed-thumb img { object-fit: cover } only matches a wrapper .feed-thumb with a
descendant img, so it never fires. Combined with aspect-ratio:231/130 the
browser uses object-fit:fill and horizontally stretches packshots.

This assert requires a rule that targets the img itself (img.feed-thumb and/or
img.author-post-thumb) and sets object-fit:cover. Wrapper .feed-thumb img is
still allowed for blog-hub / top-reads if those pages wrap the image.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
AUTHOR_SAMPLE = (
    "authors/sam-chen/index.html",
    "authors/marcus-webb/index.html",
    "authors/alex-rivera/index.html",
)

_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]+)\}")
_IMG_SELF_SEL = re.compile(
    r"(?:^|,)\s*img\.(?:feed-thumb|author-post-thumb)\b",
    re.I,
)
_AUTHOR_IMG_RE = re.compile(
    r"<img\b[^>]*\bclass=\"[^\"]*\bauthor-post-thumb\b[^\"]*\"[^>]*>",
    re.I,
)


def _strip_comments(css: str) -> str:
    return _COMMENT_RE.sub("", css)


def _object_fit_cover(body: str) -> bool:
    return bool(re.search(r"object-fit\s*:\s*cover\b", body, re.I))


def collect_errors(site: Path = SITE) -> list[str]:
    errors: list[str] = []
    css_path = site / "assets" / "css" / "site.css"
    if not css_path.is_file():
        return ["missing assets/css/site.css"]

    css = _strip_comments(css_path.read_text(encoding="utf-8"))
    img_self_cover = False
    for sel_list, body in _RULE_RE.findall(css):
        if _IMG_SELF_SEL.search(sel_list) and _object_fit_cover(body):
            img_self_cover = True
            break
    if not img_self_cover:
        errors.append(
            "site.css must set object-fit:cover on img.feed-thumb and/or "
            "img.author-post-thumb (not only .feed-thumb img)"
        )

    found_author_imgs = 0
    for rel in AUTHOR_SAMPLE:
        path = site / rel
        if not path.is_file():
            errors.append(f"missing sample author page {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        imgs = _AUTHOR_IMG_RE.findall(html)
        if not imgs:
            errors.append(f"{rel} has no author-post-thumb img")
            continue
        found_author_imgs += len(imgs)
        for tag in imgs:
            classes = re.search(r'\bclass="([^"]*)"', tag)
            cls = classes.group(1) if classes else ""
            if "feed-thumb" not in cls.split():
                errors.append(
                    f"{rel} author thumb is not img.feed-thumb: {tag[:120]}"
                )
    if found_author_imgs < 6:
        errors.append(
            f"expected 6+ author-post-thumb imgs across samples, got {found_author_imgs}"
        )

    return errors


def main() -> int:
    errors = collect_errors()
    if errors:
        print("feed_thumb_object_fit_assert FAILED")
        for err in errors:
            print(" -", err)
        return 1
    print("feed_thumb_object_fit_assert OK img.feed-thumb|img.author-post-thumb object-fit:cover")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
