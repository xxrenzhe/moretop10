/* MoreTop10 site chrome — disclosure, burger, home Show more, explore tabs. */
(function () {
  "use strict";

  function onReady(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function toggleHidden(el, forceHide) {
    if (!el) return;
    var hide = forceHide === undefined ? !el.hasAttribute("hidden") : forceHide;
    if (hide) el.setAttribute("hidden", "");
    else el.removeAttribute("hidden");
  }

  function initDisclosures() {
    document.querySelectorAll("[data-top-disc-btn]").forEach(function (btn) {
      var bar = btn.closest("[data-top-bar]");
      var panel = bar ? bar.querySelector("[data-top-disc-panel]") : null;
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        toggleHidden(panel);
      });
    });
    document.querySelectorAll("[data-disclosure-btn]").forEach(function (btn) {
      var wrap = btn.closest("[data-disclosure]");
      var panel = wrap ? wrap.querySelector("[data-disclosure-panel]") : null;
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        toggleHidden(panel);
      });
    });
    document.addEventListener("click", function () {
      document.querySelectorAll("[data-top-disc-panel], [data-disclosure-panel]").forEach(function (p) {
        p.setAttribute("hidden", "");
      });
    });
  }

  function initBurger() {
    var burger = document.querySelector("[data-burger]");
    var nav = document.querySelector("[data-mobile-nav]");
    if (!burger || !nav) return;
    burger.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  function initHomeShowMore() {
    var grid = document.querySelector("[data-home-tile-grid]");
    var btn = document.querySelector("[data-home-show-more]");
    if (!grid || !btn) return;
    btn.addEventListener("click", function () {
      grid.classList.add("is-expanded");
      btn.setAttribute("aria-expanded", "true");
      btn.hidden = true;
    });
  }

  function comparisonFromCards(cards) {
    if (!cards) return "";
    var review = cards.querySelector(".explore-read");
    if (!review) return "";
    var href = review.getAttribute("href") || "";
    var parts = href.split("/").filter(Boolean);
    if (!parts.length) return "";
    return parts[0] + "/comparison/";
  }

  function activateExplore(root, tabIndex, catIndex) {
    root.querySelectorAll("[data-explore-tab]").forEach(function (tab) {
      var on = tab.getAttribute("data-explore-tab") === String(tabIndex);
      tab.classList.toggle("is-active", on);
      tab.setAttribute("aria-selected", on ? "true" : "false");
    });
    root.querySelectorAll("[data-explore-panel]").forEach(function (panel) {
      var on = panel.getAttribute("data-explore-panel") === String(tabIndex);
      panel.classList.toggle("is-active", on);
      if (!on) return;
      var cats = panel.querySelectorAll("[data-explore-cat]");
      var chosen = catIndex;
      if (![].some.call(cats, function (c) { return c.getAttribute("data-explore-cat") === String(chosen); })) {
        chosen = cats[0] ? cats[0].getAttribute("data-explore-cat") : "0";
      }
      cats.forEach(function (cat) {
        var sel = cat.getAttribute("data-explore-cat") === String(chosen);
        cat.classList.toggle("is-selected", sel);
        cat.setAttribute("aria-pressed", sel ? "true" : "false");
      });
      var activeCards = null;
      panel.querySelectorAll("[data-explore-cards]").forEach(function (cards) {
        var sel = cards.getAttribute("data-explore-cards") === String(chosen);
        cards.classList.toggle("is-active", sel);
        if (sel) activeCards = cards;
      });
      var more = root.querySelector(".explore-show-more");
      if (more && activeCards) {
        var next = comparisonFromCards(activeCards);
        if (next) more.setAttribute("href", next);
      }
    });
  }

  function initExplore() {
    var root = document.querySelector("[data-home-explore]");
    if (!root) return;
    root.querySelectorAll("[data-explore-tab]").forEach(function (tab) {
      tab.addEventListener("click", function () {
        activateExplore(root, tab.getAttribute("data-explore-tab"), "0");
      });
    });
    root.querySelectorAll("[data-explore-panel]").forEach(function (panel) {
      panel.querySelectorAll("[data-explore-cat]").forEach(function (cat) {
        cat.addEventListener("click", function () {
          activateExplore(root, panel.getAttribute("data-explore-panel"), cat.getAttribute("data-explore-cat"));
        });
      });
    });
    var current = root.querySelector(".explore-tab.is-active") || root.querySelector("[data-explore-tab]");
    var panel = root.querySelector(".explore-panel.is-active") || root.querySelector("[data-explore-panel]");
    var cat = panel ? panel.querySelector(".explore-cat-link.is-selected") || panel.querySelector("[data-explore-cat]") : null;
    activateExplore(
      root,
      current ? current.getAttribute("data-explore-tab") : "0",
      cat ? cat.getAttribute("data-explore-cat") : "0"
    );
  }

  onReady(function () {
    initDisclosures();
    initBurger();
    initHomeShowMore();
    initExplore();
  });
})();
