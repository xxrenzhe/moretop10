# Supported models table — refresh path

Intent URL stays `/tv/supported-android-tv-models/`. Never put `cleanyourtv` in a site path.

## Provenance

Rows are a **vendored snapshot** of the unofficial CleanYourTV project’s
`examples/README.md` table (Folder · TV · OS · Notes). That project is
third-party open-source, non-official, and not affiliated with MoreTop10.

- Upstream repo: https://github.com/Gathin23/cleanyourtv
- Snapshot file: `site/data/tv-supported-models.json`
- Bake reads the snapshot; it does not invent models.

## Refresh (no Live deploy)

```bash
python3 site/scripts/fetch_tv_models.py
python3 site/scripts/bake_tv.py
python3 tests/tv_models_parse_unit.py
python3 tests/tv_cluster_assert.py
```

`fetch_tv_models.py` downloads `examples/README.md` from GitHub `main`,
parses only real table rows, and overwrites the JSON. Use
`--from-file path/to/examples-README.md` to vendor without a network fetch.

Bake ≠ Live. Do not deploy from this note. Wait for an explicit 「部署上线」.
