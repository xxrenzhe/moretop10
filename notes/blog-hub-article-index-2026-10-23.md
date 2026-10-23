# /blog/ article index

Date: 2026-10-23. Bake ≠ Deploy — do not wrangler-ship from this note.

Nav label stays **Articles** → `/blog/`. The hub is now a generated editorial
index, not a methodology stub.

## What is included

`site/scripts/build_blog.py` walks local `site/**/index.html` and keeps:

| Kind | URL pattern |
| --- | --- |
| How-to / guide | `/{cat}/how-to-*`, `/tv/remove-*`, `/tv/adb-*`, other `/tv/{slug}/` |
| Versus | `/{cat}/*-vs-*` |
| Alternatives | `/{cat}/*-alternatives/`, `/tv/*-alternatives/` |
| Best-of | `/{cat}/best-*`, `/tv/best-*` |
| Top reads | `/{cat}/top-reads/` when that HTML exists |
| Blog essay | `/blog/{slug}/` except methodology |
| TV cluster hub | `/tv/` |

Only pages that already exist as baked HTML are listed (no 404 rows).

## What is excluded

- Category landings `/{cat}/`, comparison charts `/{cat}/comparison/`
- Reviews hubs and **SKU product reviews** `/{cat}/reviews/…`
- Home, authors, about, contact, partner, legal, sitemap, search
- `/robot-vacuums-match/` demo
- `/blog/how-we-pick-products/` (type 20 methodology — sidebar only)
- Unpatterned niche / scene pages (`/{cat}/pet-homes/`, basement, pets, …)
  so this PR does not collide with those drafts

Author profile feeds still mix landings and SKUs. `/blog/` does **not** copy
those lists.

## Ordering

One chronological feed, **newest first**.

1. Date from the page (`Last updated YYYY-MM-DD`, `<time datetime>`, or
   `article:modified_time`)
2. Else `lastmod` read from `site/sitemap.xml` (read-only — this builder does
   not patch the sitemap)
3. Missing dates sink
4. Ties: how-to → guide → versus → alternatives → best-of → top-reads → article,
   then title A–Z

Each row shows a `Kind · Category` kicker. Thumbs reuse the author-feed cover
pipeline (`allocate_unique_covers` / `resolve_page_cover`) and CSS
`object-fit: cover` on `.blog-hub-page .feed-thumb img`.

## How to rebuild

```bash
python3 site/scripts/build_blog.py
# or, with verify:
python3 site/scripts/build.py --blog-only
# full bake (after TV cluster) also rewrites /blog/:
python3 site/scripts/build.py
```

`npm run bake:blog` is the same as the first command.

New matching editorial HTML (for example a later `/{cat}/best-*` page) appears
on the next rebuild. Do not hand-edit `site/blog/index.html`.
