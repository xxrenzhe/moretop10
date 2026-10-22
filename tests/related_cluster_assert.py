#!/usr/bin/env python3
"""Site-wide Related / landing-related-cluster: no self-links, no Lab."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "site" / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from bake_tv import RELATED_LINKS  # noqa: E402
from tv_cluster_assert import RELATED_REQUIRED_PATHS  # noqa: E402

CLUSTER_RE = re.compile(
    r'<p[^>]*class="[^"]*landing-related-cluster[^"]*"[^>]*>.*?</p>',
    re.S,
)
LIVE_HOSTS = ("https://moretop10.com", "http://moretop10.com")


def page_url_path(rel: str) -> str:
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def resolve_href(page_dir: str, href: str) -> str | None:
    href = href.split("#", 1)[0].split("?", 1)[0]
    if href.startswith(LIVE_HOSTS):
        for host in LIVE_HOSTS:
            if href.startswith(host):
                href = href[len(host) :] or "/"
                break
    elif href.startswith("http://") or href.startswith("https://"):
        return None
    if href.startswith("/"):
        path = href
    else:
        parts = [p for p in page_dir.strip("/").split("/") if p]
        for part in href.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        path = "/" + "/".join(parts)
        if path != "/" and not path.endswith("/") and not path.endswith(".html"):
            path += "/"
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    if path != "/" and not path.endswith("/") and not path.endswith(".html"):
        path += "/"
    return path


def main() -> None:
    errors: list[str] = []
    found = 0
    tv_pages = 0
    related_paths = {path for path, _label in RELATED_LINKS}

    for needed in RELATED_REQUIRED_PATHS:
        if needed not in related_paths:
            errors.append(f"RELATED_LINKS missing locked route {needed}")

    for path in sorted(SITE.rglob("index.html")):
        rel = path.relative_to(SITE).as_posix()
        if "/.cache/" in f"/{rel}":
            continue
        html = path.read_text(encoding="utf-8")
        page_dir = str(Path(rel).parent).replace("\\", "/")
        if page_dir == ".":
            page_dir = ""
        current = page_url_path(rel)
        for match in CLUSTER_RE.finditer(html):
            found += 1
            block = match.group(0)
            if "shortlistlab" in block.lower():
                errors.append(f"{rel} Related leaked a Lab link")
            if "/tv/cleanyourtv" in block.lower():
                errors.append(f"{rel} Related revived a cleanyourtv path")
            hrefs = re.findall(r'href="([^"]+)"', block)
            dests = []
            for href in hrefs:
                dest = resolve_href(page_dir, href)
                if dest is None:
                    continue
                dests.append(dest)
                if dest.rstrip("/") == current.rstrip("/"):
                    errors.append(f"{rel} Related self-links {current} via {href}")
            if "tv-related" in block:
                tv_pages += 1
                for needed in RELATED_REQUIRED_PATHS:
                    if needed.rstrip("/") == current.rstrip("/"):
                        continue
                    if needed not in dests:
                        errors.append(f"{rel} tv-related missing {needed}")

    if found < 70:
        errors.append(f"expected 70+ Related clusters, found {found}")
    if tv_pages != 12:
        errors.append(f"expected 12 tv-related clusters, found {tv_pages}")

    if errors:
        raise SystemExit("related_cluster_assert failed:\n- " + "\n- ".join(errors))
    print(f"related_cluster_assert ok ({found} clusters)")


if __name__ == "__main__":
    main()
