# MT10 日加滤水器/滤壶主品 densify · 2026-10-23（Asia/Shanghai）

**PR**: https://github.com/xxrenzhe/moretop10/pull/33  
**waiting_for_部署上线**: yes（未合、未部署）  
**约束**: 日加去除配件 — 禁止滤芯/挂架/支架臂/线材；Main = 台下/台面 RO/整机、滤壶设备

## 结论

| slug | 主品候选 | 密度 10 可达 | PB fromsll track |
|------|---------|-------------|------------------|
| `water-filters` | **10** | **是** | 全部有 |
| `pitcher-water-filters` | **10** | **是** | 全部有 |

- 发现：PB brand catalog（WFT-Waterdrop `138654` / Waterdrop `103211` / Frizzlife `135821`）；YP 未用（PB 已够）。
- **未**跑 Mac L2（本任务仅 propose + track 核验）；未回填 #33；未部署。
- `under-sink-countertop-filtration` dens10 的 10 个 ASIN **保留不动**（未挪用进 water-filters）。

## 重要纠偏

原先 water-filters 唯一「保留」`B01CC87G86` 实为 **冰箱滤芯 3 包装**（`WF1CB Refrigerator Water Filter`），已按配件剔除。水滤类相当于从 0 重建 10 主品。

## water-filters 提案（10）

| ASIN | 品牌 | 为何是主品 |
|------|------|-----------|
| `B0GWCWN64R` | WFT-Waterdrop | Waterdrop C1S Countertop Reverse Osmosis Water Filter, 6-Stage Filtrat — countertop filtration / RO appliance (complete unit), not a replacement cartridge |
| `B0FCFLX4ZR` | WFT-Waterdrop | Waterdrop C1H Instant Hot Countertop RO System, No Installation Requir — countertop filtration / RO appliance (complete unit), not a replacement cartridge |
| `B0GYRWYBZY` | WFT-Waterdrop | Waterdrop C2S Countertop RO Filtration System, 40oz Autofill Glass Pit — countertop filtration / RO appliance (complete unit), not a replacement cartridge |
| `B0H6WKMXPB` | WFT-Waterdrop | Waterdrop 15UA Under Sink Water Filter System with 2 Filters, 4 Years — under-sink water filter system (complete install unit), not fridge/Brita cartridge |
| `B087R2V8V7` | WFT-Waterdrop | Waterdrop DST Under Sink Water Filter System, No Drill Required for Re — under-sink water filter system (complete install unit), not fridge/Brita cartridge |
| `B0H5JZZ3GK` | WFT-Waterdrop | Waterdrop WHF21-PBL 2-Stage Whole House Water Filter System, NSF/ANSI  — whole-house filtration system (main equipment), not a drop-in replacement pack |
| `B097YC4VC2` | WFT-Waterdrop | Waterdrop TSB 8 Layer Under Sink Water Filter System, with Dedicated F — under-sink water filter system (complete install unit), not fridge/Brita cartridge |
| `B09W1Y557B` | Frizzlife AMZ | Frizzlife SW15F Under Sink Water Filter System with Brushed Nickel Fau — under-sink water filter system (complete install unit), not fridge/Brita cartridge |
| `B08R8FD43K` | Frizzlife AMZ | Frizzlife PX500-A Under Sink Tankless Reverse Osmosis Water Filtration — under-sink water filter system (complete install unit), not fridge/Brita cartridge |
| `B0CJ2QC33R` | Frizzlife AMZ | Frizzlife TS99 Countertop Water Filter System, NSF 42&372 Certified 9- — countertop filtration / RO appliance (complete unit), not a replacement cartridge |

## pitcher-water-filters 提案（10）

保留主品 5 + 新补 5（已剔 Brita 替换滤芯 3 个）。

| ASIN | source | 标题 |
|------|--------|------|
| `B0F8VVH6PN` | keep | Waterdrop ED06W Electric Water Filter Pitcher with 2 Filters, Last 4 Months |
| `B0GGQKB4TX` | keep | Waterdrop PT-11W 7-Cup Water Filter Pitcher with 3 Filters, White |
| `B0F5Q2FNTV` | keep | Waterdrop WFD-02L 35-Cup Water Filter Dispenser, Fluoride Reduction, Black |
| `B0H44DKV6V` | keep | Waterdrop PT-13P TDS-Reducing Glass Water Filter Pitcher, Large 10-Cup |
| `B0FS6DT3WK` | densify | Waterdrop ED01W Electric Water Filter Pitcher with 2 Filters, 15-Cup, White |
| `B0GWGSW2XB` | densify | Waterdrop PT-05B-AL Alkaline Water Filter Pitcher, 7-Cup, Up to pH 9.5 |
| `B0H3TLNCLG` | densify | Waterdrop WFD-40L-L Water Filter Dispenser with 3 Filters, 35-Cup Large Capacity |
| `B0F62NRGGY` | densify | Frizzlife MD40 Electric Water Filter Dispenser with 2 Filters, 400 Gallon, NSF/A |
| `B0DMVYB9B1` | densify | Waterdrop ED12W Glass Rechargeable Water Filter Dispenser, Large 22-Cup, Reduce  |
| `B0GGQCHLK1` | keep | Waterdrop PT-11BL 7-Cup Alkaline Water Filter Pitcher with 3 Filters, Blue |

## 可选补位

- **kvm-switches**（缺 1 主品开关）：推荐 `B0GYPJ97Z2` — AV Access KVM Switch Docking Station for a Laptop and 2 Desktop PCs Du
- **glass-display-cabinets**（替 L2 blocked `B0HKK8PJJR` / `B0HJNLKK9R`）：`B0HDKZKXS9, B0H9YH5DF9`

## 产物

- JSON: `/workspace/shared/mt10-day-add-filter-densify-2026-10-23.json`
- 本笔记: `/workspace/shared/mt10-day-add-filter-densify-2026-10-23.md`

## 建议下一步（仍不部署）

1. 对 `l2.suggested_new_asins_for_l2` 跑 Mac CDP L2（9333）
2. 用 ok packs + 本 JSON 的 `pb_track`（uid=fromsll）回填 #33 water/pitcher
3. 用户说「部署上线」后再合/bake/Live
