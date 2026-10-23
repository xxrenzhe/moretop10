# P1c MT10 ceramic space heaters inventory (2026-10-23)

**waiting_for_部署上线:** yes
**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.

## /ceramic-space-heaters/

- Type: new plural main category (landing + comparison + reviews hub)
- Density: 4 (honest Lab feed; not padded to 10)
- Comparison order: B0C6FFK1GV, B097RG67QB, B0C6FCKQML, B095PP1GZR
- Top pick: DREO Space Heater, Portable Electric Heaters for Indoor Use with Remote `B0C6FFK1GV`
- Upgrade: DREO Space Heater, Portable Electric Heaters for Indoor Use with Thermostat `B097RG67QB` (Atom One)
- Deep reviews: Top pick + Upgrade only (3 unique paths; see notes/p1c-deep-reviews-2026-10-23.md)
- Tracks: B0C6FFK1GV=ok/pb, B097RG67QB=ok/pb, B0C6FCKQML=ok/pb, B095PP1GZR=ok/pb
- Cards omit was/% even when the Lab feed listed a list price.

## /ceramic-space-heaters/best-ceramic-space-heaters-for-large-rooms/

- Density: 4 (scene-reordered; not comparison order)
- Top pick: DREO Space Heaters for Indoor Use with Thermostat, 1500W Electric Heaters `B095PP1GZR` review `dreo-space-heaters-indoor-thermostat-1500w`
- Upgrade: DREO Space Heater, Portable Electric Heaters for Indoor Use with Thermostat `B097RG67QB` review `dreo-atom-one-space-heater-thermostat`
- New reviews: Top pick + Upgrade deep articles (unique paths, not a full Top 4)
- Tracks: B095PP1GZR=ok/pb, B097RG67QB=ok/pb, B0C6FFK1GV=ok/pb, B0C6FCKQML=ok/pb

## /ceramic-space-heaters/best-ceramic-space-heaters-for-garages/

- Density: 4 (scene-reordered; not comparison order)
- Top pick: DREO Space Heater, Portable Electric Heaters for Indoor Use with Thermostat `B097RG67QB` review `dreo-atom-one-space-heater-thermostat`
- Upgrade: DREO Space Heaters for Indoor Use with Thermostat, 1500W Electric Heaters `B095PP1GZR` review `dreo-space-heaters-indoor-thermostat-1500w`
- New reviews: Top pick + Upgrade deep articles (unique paths, not a full Top 4)
- Tracks: B097RG67QB=ok/pb, B095PP1GZR=ok/pb, B0C6FFK1GV=ok/pb, B0C6FCKQML=ok/pb

## Shortfalls (honest)

- Density is 4 healthy Lab feed cards, not a padded Top 10. No invented ASINs, prices, images, or was/%.
- Role blocks keep the live densify `###` inside `<p>` and append a truncated feed feature sentence.
- Neighbor slots include compact 34dB cards that do not list garage / 270 sq.ft so we do not invent claims.
- Reviews: Top pick + Upgrade deep articles at new `/{cat}/reviews/{slug}/` paths. Not a full Top 4. Gold `B0C6FCKQML` has no deep review.
- Lab `/shortlists/*` paths from the locked batch are out of scope (MT10 draft only).
- `robots` stays `index,follow` to match live type-07. The deploy gate is the draft PR + `waiting_for_部署上线=yes`. Do not Cloudflare Live deploy.
