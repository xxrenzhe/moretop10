# MoreTop10 SEO/GEO P1（cite / robots preview）— 2026-10-20

**Bake ≠ Deploy。** 本 PR 只改本地 `site/` 静态产物。**不要** wrangler / DNS / IndexNow / 合并后自动上 Live。须用户明示「部署上线」且只用 MT10 自己的 CF Token。

事实基线：舰队方案 §7.1 MoreTop10 **P1**；P0 已合入 `main`（#5 / `4639d5f`）并已 Live。

---

## 审计：P0 已覆盖（本 PR 不重做）

| 项 | 状态 |
|----|------|
| `/{cat}/` CollectionPage + ItemList + Product/Offer | 已在 main / Live |
| `/authors/` Hub 200 | 已在 main / Live |
| `robots.txt` Content-Signal | 已在 main / Live |
| `/.well-known/llms.txt` 双 200 | 已在 main / Live |
| `robot-vacuums-match/` `noindex,follow` + canonical Hub | 已在 main / Live |
| kids BoFu（`how-to-choose-a-kids-bike` 等） | Live 保留；本 clone 不生成 BoFu，未删除 |
| G-IL mega/footer 21 类、density=10 | 保持 |

P0 已在 **类目 Hub** 写入 cite + `#geo-{ASIN}`（`landing-pick`）。缺口在 comparison / reviews。

---

## P0 余留、本 P1 关闭

1. **全站可索引页** `<meta name="robots" content="index,follow,max-image-preview:large">`  
   原先仅 Hub / comparison / authors；home、about、reviews hub、单品评测仍是 `index,follow`。match 保持 `noindex,follow`。
2. **Comparison `#geo-{ASIN}` 未打上**  
   P0 `inject_geo_anchors` 要求 `pick_id`，comparison 卡没有 pick_id；cite 还插进了第一张 `product-card` 内部。
3. **`/{cat}/reviews/` Hub** 无 How to Cite、无 geo 锚点、无 max-image-preview。
4. **`/{cat}/reviews/{slug}/` 单品评测** 本仓未 bake；Live 无 cite / geo，且可见文案含 `completeness gate`。

未做（P2 / 纯运营）：OpenSEO 绑定、月度 GEO 探针、CF AI Crawl Control 人工核、**不上 Live**。

---

## 本 PR 改动（构建器，非手改 HTML）

生成器：`python3 site/scripts/build.py` + `site/scripts/seo_geo.py`。

- 默认对所有 bake 出的可索引页写 `ROBOTS_INDEX`；match/search 保持 noindex。
- Cite strip 统一为可见 **How to cite:**，插在 landing-article 末或 `</main>` 前（comparison 不再夹在第一张卡里）。日期仍是页面已有的 **日粒度** `YYYY-MM-DD`。
- Comparison `product-card`、reviews hub `rev-hub-card`、单品评测 `<main>` 写入 `id="geo-{ASIN}"`（ASIN 来自 Live `data-asin` / 评测 slug 对照 / packshot，不编造）。
- 从 sitemap 拉取 206 篇已发布单品评测并 bake；可见黑话沿用 P0 词表（`completeness gate` → 访客口径）。**无 AggregateRating。**
- G-IL：mega/footer 仍列出全部 21 个 published 类目；评测页 Compare CTA → 本类 comparison。

---

## 本地验收（已跑）

```bash
python3 site/scripts/build.py
python3 tests/seo_geo_p0_assert.py
python3 tests/seo_geo_p1_unit.py
python3 tests/seo_geo_p1_assert.py
node tests/pc-card-layout-assert.mjs

python3 -m http.server 8765 --directory site
# curl -s http://127.0.0.1:8765/air-fryers/comparison/ | grep -E 'id="geo-|How to cite:|max-image-preview'
# curl -s http://127.0.0.1:8765/air-fryers/reviews/ | grep -E 'How to cite:|id="geo-'
# curl -s http://127.0.0.1:8765/air-fryers/reviews/cosori-twinfry-9-qt-double-air/ | grep -E 'How to cite:|geo-B0GLX9TGJV|max-image-preview|AggregateRating|completeness gate'
# curl -s http://127.0.0.1:8765/ | grep 'max-image-preview'
# curl -s http://127.0.0.1:8765/robot-vacuums-match/ | grep 'noindex,follow'
```

**未部署 Live。**
