#!/usr/bin/env node
/**
 * Regression guard: comparison product-card chrome cascade.
 *
 * Live load order: tokens.css → site.css → pages-comparison.css.
 *
 * Wave2 split inverted that cascade: site.css (earlier) held
 * display:grid + areas; pages-comparison.css (later) kept unscoped
 * display:flex and at @768 only set flex-direction:row. Flex won,
 * grid-area was ignored, title/score/price overlapped.
 *
 * Contract:
 *  1. site.css must NOT set display:grid on .pc-main
 *  2. pages-comparison.css must set display:grid + areas at >=768px
 *     AFTER any unscoped display:flex, so flex cannot win on desktop
 *  3. Concatenated cascade at 1024px: display:grid, 3-col + price row + footer
 *  4. Concatenated cascade at 375px: display:flex; flex-direction:column
 *  5. Fixture HTML: score in .pc-right; .pc-price-decision is a sibling
 *     ABOVE .pc-footer (not in the score block, not under border-top).
 *     Footer is one row: Read review | Check price.
 *  6. CSS: desktop areas include pc-price above pc-foot; .pc-right does
 *     not use space-between to float price mid-card.
 */
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const cssDir = join(root, "site/assets/css");
const bundle = ["tokens.css", "site.css", "pages-comparison.css"];

function stripComments(css) {
  return css.replace(/\/\*[\s\S]*?\*\//g, "");
}

function mediaMatches(prelude, width) {
  const q = prelude.replace(/^@media/i, "").trim();
  if (!q) return true;
  const min = q.match(/min-width:\s*(\d+)px/i);
  const max = q.match(/max-width:\s*(\d+)px/i);
  if (min && width < Number(min[1])) return false;
  if (max && width > Number(max[1])) return false;
  return true;
}

function matchingClose(css, openIdx) {
  let depth = 0;
  for (let i = openIdx; i < css.length; i++) {
    if (css[i] === "{") depth++;
    else if (css[i] === "}") {
      depth--;
      if (depth === 0) return i;
    }
  }
  return -1;
}

function applyDecls(selMap, selectorList, body) {
  const decls = {};
  for (const part of body.split(";")) {
    const idx = part.indexOf(":");
    if (idx < 0) continue;
    const prop = part.slice(0, idx).trim().toLowerCase();
    const val = part.slice(idx + 1).trim();
    if (prop) decls[prop] = val;
  }
  for (const raw of selectorList.split(",")) {
    const sel = raw.trim();
    if (!sel || sel.startsWith("@")) continue;
    selMap[sel] ??= {};
    Object.assign(selMap[sel], decls);
  }
}

function parseDecls(body) {
  const decls = {};
  for (const part of body.split(";")) {
    const idx = part.indexOf(":");
    if (idx < 0) continue;
    const prop = part.slice(0, idx).trim().toLowerCase();
    const val = part.slice(idx + 1).trim();
    if (prop) decls[prop] = val;
  }
  return decls;
}

function walk(css, width, selMap) {
  let i = 0;
  const n = css.length;
  while (i < n) {
    const open = css.indexOf("{", i);
    if (open < 0) break;
    const prelude = css.slice(i, open).trim();
    const close = matchingClose(css, open);
    if (close < 0) break;
    const body = css.slice(open + 1, close);
    if (prelude.toLowerCase().startsWith("@media")) {
      if (mediaMatches(prelude, width)) walk(body, width, selMap);
    } else if (!prelude.startsWith("@")) {
      applyDecls(selMap, prelude, body);
    }
    i = close + 1;
  }
}

function walkAll(css, onRule, media) {
  let i = 0;
  const n = css.length;
  while (i < n) {
    const open = css.indexOf("{", i);
    if (open < 0) break;
    const prelude = css.slice(i, open).trim();
    const close = matchingClose(css, open);
    if (close < 0) break;
    const body = css.slice(open + 1, close);
    if (prelude.toLowerCase().startsWith("@media")) {
      walkAll(body, onRule, prelude);
    } else if (!prelude.startsWith("@")) {
      const decls = parseDecls(body);
      for (const raw of prelude.split(",")) {
        const sel = raw.trim();
        if (sel) onRule(sel, decls, media || "(all)");
      }
    }
    i = close + 1;
  }
}

function cascade(fileList, width) {
  const selMap = {};
  for (const file of fileList) {
    walk(stripComments(readFileSync(join(cssDir, file), "utf8")), width, selMap);
  }
  return selMap;
}

function collectDisplayRules(file, selector) {
  const rules = [];
  walkAll(
    stripComments(readFileSync(join(cssDir, file), "utf8")),
    (sel, decls, media) => {
      if (sel === selector && decls.display) {
        rules.push({
          media: media || "(all)",
          display: decls.display,
          areas: decls["grid-template-areas"] || "",
        });
      }
    },
  );
  return rules;
}

function normalizeAreas(value) {
  return String(value || "")
    .replace(/["']/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

const sitePcRules = collectDisplayRules("site.css", ".pc-main");
assert(
  sitePcRules.every((r) => r.display !== "grid"),
  `site.css must not set display:grid on .pc-main (SoT is pages-comparison.css). Found: ${JSON.stringify(sitePcRules)}`,
);

const pagePcRules = collectDisplayRules("pages-comparison.css", ".pc-main");
const pageHasUnscopedFlex = pagePcRules.some(
  (r) => r.media === "(all)" && r.display === "flex",
);
const pageDesktopGrid = [...pagePcRules]
  .reverse()
  .find((r) => r.display === "grid" && /min-width:\s*768px/i.test(r.media));
assert(
  Boolean(pageDesktopGrid),
  `pages-comparison.css must set .pc-main{display:grid} inside @media (min-width:768px). Rules: ${JSON.stringify(pagePcRules)}`,
);
if (pageHasUnscopedFlex) {
  const flexIdx = pagePcRules.findIndex(
    (r) => r.media === "(all)" && r.display === "flex",
  );
  const gridIdx = pagePcRules.findIndex(
    (r) => r === pageDesktopGrid || (r.display === "grid" && r === pageDesktopGrid),
  );
  const lastGridIdx = pagePcRules.reduce(
    (acc, r, i) =>
      r.display === "grid" && /min-width:\s*768px/i.test(r.media) ? i : acc,
    -1,
  );
  assert(
    lastGridIdx > flexIdx,
    "pages-comparison.css unscoped display:flex on .pc-main must be followed by a later @768 display:grid so flex cannot win on desktop",
  );
}
assert(
  /pc-left pc-mid pc-right/.test(normalizeAreas(pageDesktopGrid.areas)) &&
    /pc-left pc-mid pc-price/.test(normalizeAreas(pageDesktopGrid.areas)) &&
    /pc-foot pc-foot pc-foot/.test(normalizeAreas(pageDesktopGrid.areas)),
  `pages-comparison.css desktop grid must include score row + price row + full-width footer, got "${pageDesktopGrid.areas}"`,
);

const desktop = cascade(bundle, 1024);
const mobile = cascade(bundle, 375);
const pc = desktop[".pc-main"] || {};
const pcMob = mobile[".pc-main"] || {};
const areas = normalizeAreas(pc["grid-template-areas"]);
const cols = String(pc["grid-template-columns"] || "");

assert(
  pc.display === "grid",
  `desktop .pc-main display must be grid, got "${pc.display || ""}"`,
);
assert(
  /200px/.test(cols) && /minmax\(0,\s*1fr\)/.test(cols) && /168px/.test(cols),
  `desktop .pc-main columns must be 200px | minmax(0,1fr) | 168px, got "${cols}"`,
);
assert(
  areas.includes("pc-left pc-mid pc-right") &&
    areas.includes("pc-left pc-mid pc-price") &&
    areas.includes("pc-foot pc-foot pc-foot"),
  `desktop .pc-main areas must be score | price-above-divider | footer, got "${areas}"`,
);
assert(
  (desktop[".pc-left"] || {})["grid-area"] === "pc-left",
  "desktop .pc-left must use grid-area pc-left",
);
assert(
  (desktop[".pc-mid"] || {})["grid-area"] === "pc-mid",
  "desktop .pc-mid must use grid-area pc-mid",
);
assert(
  (desktop[".pc-right"] || {})["grid-area"] === "pc-right",
  "desktop .pc-right must use grid-area pc-right",
);
assert(
  (desktop[".pc-price-decision"] || {})["grid-area"] === "pc-price",
  "desktop .pc-price-decision must use grid-area pc-price (above the footer divider)",
);
assert(
  (desktop[".pc-footer"] || {})["grid-area"] === "pc-foot",
  "desktop .pc-footer must use grid-area pc-foot",
);
assert(
  pcMob.display === "flex",
  `mobile .pc-main display must stay flex, got "${pcMob.display || ""}"`,
);
assert(
  (pcMob["flex-direction"] || "column") === "column",
  `mobile .pc-main must stack as a column, got "${pcMob["flex-direction"] || ""}"`,
);

const pageSheets = readdirSync(cssDir).filter(
  (f) => f.startsWith("pages-") && f.endsWith(".css") && f !== "pages-comparison.css",
);
for (const sheet of pageSheets) {
  const rules = collectDisplayRules(sheet, ".pc-main");
  assert(
    rules.length === 0,
    `${sheet} must not touch .pc-main display (only pages-comparison.css owns it). Found: ${JSON.stringify(rules)}`,
  );
}

const rightDesk = desktop[".pc-right"] || {};
assert(
  !/space-between/.test(rightDesk["justify-content"] || ""),
  `desktop .pc-right must not space-between (price left the score column). got "${rightDesk["justify-content"] || ""}"`,
);
assert(
  /flex-start|start/.test(rightDesk["justify-content"] || "flex-start"),
  `desktop .pc-right must keep the score at the top, got "${rightDesk["justify-content"] || ""}"`,
);
const rightMob = mobile[".pc-right"] || {};
assert(
  /flex-end|end/.test(rightMob["align-items"] || ""),
  `mobile .pc-right must keep the score on the right, got align-items="${rightMob["align-items"] || ""}"`,
);
const scoreMob = mobile[".pc-score-block"] || {};
assert(
  scoreMob.width === "auto",
  `mobile .pc-score-block must shrink (not full-bleed) so it can sit top-right, got width="${scoreMob.width || ""}"`,
);

const footerDesk = desktop[".pc-footer"] || {};
assert(
  /center/.test(footerDesk["align-items"] || "center"),
  `desktop .pc-footer is one button row (Read review | Check price), got align-items="${footerDesk["align-items"] || ""}"`,
);
assert(
  /border-top/.test(footerDesk["border-top"] ? "border-top" : "") ||
    Boolean(footerDesk["border-top"]),
  `desktop .pc-footer must keep the divider (border-top), got "${footerDesk["border-top"] || ""}"`,
);

const priceDesk = desktop[".pc-price-decision"] || {};
assert(
  priceDesk.display === "flex" && priceDesk["flex-direction"] === "column",
  `price block must stack value + Checked date, got ${JSON.stringify(priceDesk)}`,
);
assert(
  /end/.test(priceDesk["align-items"] || "") ||
    /end/.test(priceDesk["justify-self"] || ""),
  `desktop price must right-align onto the CTA, got align-items="${priceDesk["align-items"] || ""}" justify-self="${priceDesk["justify-self"] || ""}"`,
);
assert(
  priceDesk.margin === "0" || priceDesk["margin-top"] === "0",
  `price must not add mid-card gap. got margin="${priceDesk.margin || ""}" margin-top="${priceDesk["margin-top"] || ""}"`,
);
const priceMob = mobile[".pc-price-decision"] || {};
assert(
  /flex-end|end/.test(priceMob["align-self"] || priceMob["align-items"] || "flex-end"),
  `mobile price must stay on the CTA side, got align-self="${priceMob["align-self"] || ""}" align-items="${priceMob["align-items"] || ""}"`,
);

const fixturePath = join(root, "site/fixtures/comparison-card.html");
const fixture = readFileSync(fixturePath, "utf8");
const cards = [...fixture.matchAll(/<article\s+class="product-card"[\s\S]*?<\/article>/g)].map(
  (m) => m[0],
);
assert(cards.length >= 1, "fixture must contain at least one .product-card");

for (const [i, card] of cards.entries()) {
  const scorePos = card.indexOf('class="pc-score-block"');
  const rightPos = card.indexOf('class="pc-right"');
  const footerPos = card.indexOf('class="pc-footer"');
  const pricePos = card.indexOf('class="pc-price-decision"');
  const ctaPos = card.search(/class="[^"]*product-cta/);
  const reviewPos = card.indexOf('class="pc-secondary-link"');
  assert(rightPos >= 0 && scorePos > rightPos, `card ${i}: score block lives in .pc-right`);
  assert(footerPos > scorePos, `card ${i}: footer follows the score column`);
  assert(
    pricePos > rightPos && pricePos < footerPos,
    `card ${i}: .pc-price-decision must sit above .pc-footer (not under border-top)`,
  );
  assert(
    !card.includes("pc-footer-buy"),
    `card ${i}: do not wrap price inside .pc-footer-buy (that put it below the divider)`,
  );
  const footerChunk = card.slice(footerPos);
  assert(
    !footerChunk.includes("pc-price-decision") && !footerChunk.includes("pc-price-value"),
    `card ${i}: price must not live inside .pc-footer`,
  );
  assert(
    reviewPos > footerPos && ctaPos > reviewPos,
    `card ${i}: footer is one row — Read review then Check price`,
  );
  const scoreChunk = card.slice(scorePos, pricePos);
  assert(
    !scoreChunk.includes("pc-price-decision") && !scoreChunk.includes("pc-price-value"),
    `card ${i}: price must not remain inside .pc-score-block`,
  );
  assert(
    /Checked \d{4}-\d{2}-\d{2}/.test(card),
    `card ${i}: Checked date must stay day-only YYYY-MM-DD`,
  );
  assert(/Check price/.test(card), `card ${i}: Check price CTA copy unchanged`);
  assert(/Read review/.test(card), `card ${i}: Read review stays in the footer`);
}

assert(
  /eufy E25 Robot Vacuum and Mop Combo, 20,000 Pa/.test(fixture),
  "fixture should include the robot-vacuums eufy E25 card used to verify /robot-vacuums/",
);
assert(
  !/pboost\.me/.test(fixture),
  "fixture must not rewrite or copy live affiliate hop URLs",
);

console.log("pc-card-layout-assert: ok");
console.log("  site.css .pc-main display:grid: none");
console.log("  pages-comparison.css desktop SoT: grid", normalizeAreas(pageDesktopGrid.areas));
console.log("  concatenated desktop .pc-main display:", pc.display);
console.log("  concatenated mobile .pc-main display:", pcMob.display, pcMob["flex-direction"]);
console.log("  price grid-area:", (desktop[".pc-price-decision"] || {})["grid-area"]);
console.log("  fixture cards:", cards.length, "(price above divider, footer = review|CTA)");
