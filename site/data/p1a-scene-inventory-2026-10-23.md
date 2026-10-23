# P1a MT10 scene inventory (2026-10-23)

**waiting_for_部署上线:** yes
**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.

## /dehumidifiers/best-dehumidifiers-for-basements/

- Density: 10 (scene-reordered; not comparison order)
- Top pick: Waykar 80 Pints 2025 Energy Star Dehumidifier `B0C9THG48W` review `waykar-80-pints-2025-energy-star` (reused)
- Upgrade: AEOCKY 5500 Sq.Ft Energy Star Most Efficient `B0D1C6HWFF` review `aeocky-5500-sqft-energy-star-most` (reused)
- New reviews: none
- Tracks: B0C9THG48W=ok/pb, B0B5V6MBMR=ok/pb, B0D1C6HWFF=ok/pb, B0FWB57KYQ=ok/pb, B0H41K4PQN=ok/pb, B0GXYD5JBY=ok/pb, B0H26KMQHT=ok/pb, B0FRQVWSS4=ok/pb, B081RG8JYR=ok/pb, B0FCDZM4JL=ok/pb

## /air-purifiers/best-air-purifiers-for-pets/

- Density: 10 (scene-reordered; not comparison order)
- Top pick: LEVOIT Smart Pet Air Purifier for Home Pets `B0GXKSC38S` review `levoit-smart-pet-air-purifier-home` (reused)
- Upgrade: Dreame Pet Air Purifier AP10, Suck Up Floating `B0FS68R44C` review `dreame-pet-air-purifier-ap10-suck` (reused)
- New reviews: none
- Tracks: B0GXKSC38S=ok/pb, B0FS68R44C=ok/pb, B0CXJ97TV1=ok/pb, B09LMF648R=ok/pb, B0F32TGRMR=ok/pb, B0F2G5DPJN=ok/pb, B07X25BNBR=ok/pb, B0FK53C7B9=ok/pb, B0H4SVJ2RF=ok/pb, B08BR1CR78=ok/pb

## /robot-vacuums/pet-homes/

- Density: 10 (scene-reordered; not comparison order)
- Top pick: eufy E25 Robot Vacuum and Mop Combo, 20,000 Pa `B0FK2HPNCB` review `eufy-e25-robot-vacuum-mop-combo` (reused)
- Upgrade: Roborock 2026 New Qrevo S Pro Robot Vacuum `B0GGRTD2ZY` review `roborock-2026-new-qrevo-s-pro` (reused)
- New reviews: none
- Tracks: B0FK2HPNCB=ok/pb, B0GGRTD2ZY=ok/pb, B0DWX69JVG=ok/pb, B0DWXBCQVP=ok/pb, B0DX1DQKMD=ok/pb, B0GTLY9Z1K=ok/pb, B0GCDZBK9Q=ok/pb, B0F3337BV7=ok/pb, B0DHCJ571Z=ok/pb, B0CQ7JCN6Z=ok/pb

## Shortfalls (honest)

- Density is 10 scene-reordered live cards (type-07 / bedroom humidifier pattern). Not a 4-item Lab shortlist.
- Role blocks keep the live densify `###` inside `<p>` and append a truncated live-card feature sentence. No invented prices/images/was.
- Neighbor slots include cards whose pet/basement copy is thin (AEOCKY YearChange, Dreame compact, refurbished Qrevo MaxV, Waykar 30/34). They stay last so we do not invent claims.
- Reviews: Top pick + Upgrade reused only. No new `/{cat}/reviews/{slug}/` files.
- Lab `/shortlists/*` paths from the locked batch are out of scope (MT10 draft only).
- `robots` stays `index,follow` to match live type-07. The deploy gate is the draft PR + `waiting_for_部署上线=yes`. Do not Cloudflare Live deploy.
