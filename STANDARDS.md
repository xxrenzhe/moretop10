# MoreTop10 standards

House index for in-repo specs. **Bake ≠ Deploy** — these documents do not authorize a Live wrangler/CF ship.

## Project artifacts

| Artifact | Path | Role |
| --- | --- | --- |
| Page-type taxonomy (types 01–21) | [`site/page-type-taxonomy.md`](site/page-type-taxonomy.md) | Canonical page classes, URL patterns, and FAQ omit/include flags |
| FAQ by page type | [`site/FAQ-BY-PAGE-TYPE.md`](site/FAQ-BY-PAGE-TYPE.md) | Buyer-intent FAQ规范 keyed to taxonomy types — not one generic FAQ |
| Site instance catalog | [`site/instances/moretop10.site.yaml`](site/instances/moretop10.site.yaml) | Published category slugs for nav / footer / home tiles |
| Bake notes | [`notes/`](notes/) | Per-PR handoffs (SEO/GEO, copy, layout, blog hub). Not visitor-facing. |
| Blog hub index | [`notes/blog-hub-article-index-2026-10-23.md`](notes/blog-hub-article-index-2026-10-23.md) | What `/blog/` includes, ordering, rebuild |

## Related tests

Existing bake asserts live under [`tests/`](tests/). FAQ content rules are **spec-first**; the named follow-on assert is `tests/faq_by_page_type_assert.py` (see the FAQ doc).
