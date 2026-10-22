# MT10 /tv/ OG cover — 2026-10-23

**状态**：draft PR · 未合 · 未 Live（须「部署上线」）

`/tv/` hub and cluster pages inherited about-us chrome, so `og:image` /
`twitter:image` were `icon-512.png`. Bake now emits the Live Google TV hero
product image (ASIN `B0F1DRNWP7` Hisense 55" U8), same Amazon CDN pattern as
`/hair-dryers/`:

`https://m.media-amazon.com/images/I/81IgwvJG9GL._AC_SL1500_.jpg`

SoT: `site/scripts/bake_tv.py` (`HUB_OG_IMAGE`). Organization logo may stay
`icon-512`. Rebake with `python3 site/scripts/bake_tv.py`. Bake ≠ deploy.
