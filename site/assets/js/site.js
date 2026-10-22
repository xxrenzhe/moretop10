(function () {
  var burger = document.querySelector("[data-burger]");
  var mobile = document.querySelector("[data-mobile-nav]");
  if (burger && mobile) {
    burger.addEventListener("click", function () {
      var open = mobile.classList.toggle("open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* Advertising disclosure toggle */
  var disc = document.querySelector("[data-disclosure]");
  if (disc) {
    var btn = disc.querySelector("[data-disclosure-btn]");
    var panel = disc.querySelector("[data-disclosure-panel]");
    if (btn && panel) {
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        var hide = !panel.hasAttribute("hidden");
        if (hide) panel.setAttribute("hidden", "");
        else panel.removeAttribute("hidden");
      });
      document.addEventListener("click", function () {
        panel.setAttribute("hidden", "");
      });
      panel.addEventListener("click", function (e) {
        e.stopPropagation();
      });
    }
  }

  /* Sticky CTA bar — follow the product card nearest viewport center */
  var bar = document.querySelector("[data-sticky-cta]");
  var cards = Array.prototype.slice.call(
    document.querySelectorAll('.product-card[data-sticky="product-card"]')
  );
  if (bar && cards.length) {
    var imgEl = bar.querySelector("[data-sticky-img]");
    var nameEl = bar.querySelector("[data-sticky-name]");
    var linkEl = bar.querySelector("[data-sticky-link]");
    var current = null;

    function activate(card) {
      if (!card || card === current) return;
      current = card;
      var name = card.getAttribute("data-product-name") || "";
      var cta = card.getAttribute("data-cta") || "#";
      var src = card.getAttribute("data-img") || "";
      if (nameEl) nameEl.textContent = name;
      if (linkEl) linkEl.setAttribute("href", cta);
      if (imgEl) {
        if (src) {
          imgEl.src = src;
          imgEl.removeAttribute("hidden");
        } else {
          imgEl.removeAttribute("src");
          imgEl.setAttribute("hidden", "");
        }
      }
      bar.removeAttribute("hidden");
      bar.classList.add("is-visible");
      document.body.classList.add("has-sticky-cta");
    }

    function pick() {
      var mid = window.innerHeight * 0.42;
      var best = null;
      var bestDist = Infinity;
      for (var i = 0; i < cards.length; i++) {
        var r = cards[i].getBoundingClientRect();
        if (r.bottom < 80 || r.top > window.innerHeight - 40) continue;
        var c = (r.top + r.bottom) / 2;
        var d = Math.abs(c - mid);
        if (d < bestDist) {
          bestDist = d;
          best = cards[i];
        }
      }
      if (best) activate(best);
      else {
        bar.classList.remove("is-visible");
        document.body.classList.remove("has-sticky-cta");
        /* keep hidden attr off once shown so transition works; use class only */
        if (!current) bar.setAttribute("hidden", "");
      }
    }

    var ticking = false;
    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(function () {
          pick();
          ticking = false;
        });
      },
      { passive: true }
    );
    window.addEventListener("resize", pick, { passive: true });
    pick();
  }


  /* Top affiliate bar disclosure */
  var topBar = document.querySelector("[data-top-bar]");
  if (topBar) {
    var tBtn = topBar.querySelector("[data-top-disc-btn]");
    var tPanel = topBar.querySelector("[data-top-disc-panel]");
    if (tBtn && tPanel) {
      tBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        if (tPanel.hasAttribute("hidden")) tPanel.removeAttribute("hidden");
        else tPanel.setAttribute("hidden", "");
      });
      document.addEventListener("click", function () {
        tPanel.setAttribute("hidden", "");
      });
      tPanel.addEventListener("click", function (e) {
        e.stopPropagation();
      });
    }
  }

  /* Home Explore-by-category tabs + in-panel subcategory switchers */
  var explore = document.querySelector("[data-home-explore]");
  if (explore) {
    var tabs = explore.querySelectorAll("[data-explore-tab]");
    var panels = explore.querySelectorAll("[data-explore-panel]");
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        var id = tab.getAttribute("data-explore-tab");
        tabs.forEach(function (t) {
          var on = t.getAttribute("data-explore-tab") === id;
          t.classList.toggle("is-active", on);
          t.setAttribute("aria-selected", on ? "true" : "false");
        });
        panels.forEach(function (panel) {
          var on = panel.getAttribute("data-explore-panel") === id;
          panel.classList.toggle("is-active", on);
          if (on) panel.removeAttribute("hidden");
          else panel.setAttribute("hidden", "");
        });
      });
    });
    panels.forEach(function (panel) {
      var catBtns = panel.querySelectorAll("[data-explore-cat]");
      var cardSets = panel.querySelectorAll("[data-explore-cards]");
      catBtns.forEach(function (btn) {
        btn.addEventListener("click", function () {
          var cid = btn.getAttribute("data-explore-cat");
          catBtns.forEach(function (b) {
            var on = b.getAttribute("data-explore-cat") === cid;
            b.classList.toggle("is-selected", on);
            b.setAttribute("aria-pressed", on ? "true" : "false");
          });
          cardSets.forEach(function (set) {
            var on = set.getAttribute("data-explore-cards") === cid;
            if (on) set.removeAttribute("hidden");
            else set.setAttribute("hidden", "");
          });
        });
      });
    });
  }

  /* Home Show more tiles */
  var showMore = document.querySelector("[data-home-show-more]");
  var tileGrid = document.querySelector("[data-home-tile-grid]");
  if (showMore && tileGrid) {
    showMore.addEventListener("click", function () {
      var open = tileGrid.classList.toggle("is-expanded");
      showMore.setAttribute("aria-expanded", open ? "true" : "false");
      showMore.childNodes[0].textContent = open ? "Show less " : "Show more ";
    });
  }

  /* Match demo — choice card selection */
  var matchForm = document.querySelector("[data-match-form]");
  if (matchForm) {
    var cards = matchForm.querySelectorAll(".match-choice-card");
    cards.forEach(function (card) {
      card.addEventListener("click", function () {
        cards.forEach(function (c) { c.classList.remove("is-selected"); });
        card.classList.add("is-selected");
      });
    });
    matchForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var sel = matchForm.querySelector(".match-choice-card.is-selected");
      var href = matchForm.querySelector(".match-actions .btn-ghost");
      if (href && href.getAttribute("href")) window.location.href = href.getAttribute("href");
    });
  }



  /* Partner lead capture — POST /api/leads (D1; no outbound email) */
  var partnerForm = document.querySelector("[data-partner-form]");
  if (partnerForm) {
    var statusEl = partnerForm.querySelector("[data-partner-status]");
    var submitBtn = partnerForm.querySelector(".partner-submit");
    function setStatus(msg, kind) {
      if (!statusEl) return;
      statusEl.hidden = !msg;
      statusEl.textContent = msg || "";
      statusEl.classList.remove("is-ok", "is-err");
      if (kind) statusEl.classList.add(kind === "ok" ? "is-ok" : "is-err");
    }
    partnerForm.addEventListener("submit", function (e) {
      e.preventDefault();
      setStatus("", "");
      var emailInput = partnerForm.querySelector('input[name="email"]');
      var honeyInput = partnerForm.querySelector('input[name="website"]');
      var email = emailInput ? String(emailInput.value || "").trim() : "";
      if (!email || email.indexOf("@") < 1) {
        setStatus("Please enter a valid work email.", "err");
        if (emailInput) emailInput.focus();
        return;
      }
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.setAttribute("aria-busy", "true");
      }
      var payload = {
        email: email,
        source: "partner-with-us",
        website: honeyInput ? String(honeyInput.value || "") : ""
      };
      fetch("/api/leads", {
        method: "POST",
        headers: { "content-type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify(payload)
      })
        .then(function (res) {
          return res.json().then(function (data) {
            return { ok: res.ok, status: res.status, data: data || {} };
          }).catch(function () {
            return { ok: res.ok, status: res.status, data: {} };
          });
        })
        .then(function (result) {
          if (result.ok && result.data && result.data.ok) {
            setStatus("Thanks — we saved your email.", "ok");
            partnerForm.reset();
            return;
          }
          if (result.status === 429) {
            setStatus("Too many tries. Please wait a minute and try again.", "err");
            return;
          }
          if (result.data && result.data.error === "invalid_email") {
            setStatus("Please enter a valid work email.", "err");
            return;
          }
          setStatus("Something went wrong. Please try again.", "err");
        })
        .catch(function () {
          setStatus("Network error. Please try again.", "err");
        })
        .finally(function () {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.removeAttribute("aria-busy");
          }
        });
    });
  }

  /* Author page Show more posts */
  var authorMore = document.querySelector("[data-author-show-more]");
  var authorPosts = document.querySelector("[data-author-posts]");
  if (authorMore && authorPosts) {
    authorMore.addEventListener("click", function () {
      var open = authorMore.getAttribute("aria-expanded") === "true";
      open = !open;
      authorMore.setAttribute("aria-expanded", open ? "true" : "false");
      authorPosts.querySelectorAll("[data-author-post][hidden]").forEach(function () {});
      authorPosts.querySelectorAll("[data-author-post]").forEach(function (row, i) {
        if (i < 7) return;
        if (open) row.removeAttribute("hidden");
        else row.setAttribute("hidden", "");
      });
      var label = authorMore.querySelector("span");
      if (label) label.textContent = open ? "Show less" : "Show more";
    });
  }

})();
