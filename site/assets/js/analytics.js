/* Optional GA4 hook. No-ops when window.__MT10_ANALYTICS__.ga4 is unset. */
(function () {
  var cfg = window.__MT10_ANALYTICS__ || {};
  if (!cfg.ga4) return;
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", cfg.ga4);
  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(cfg.ga4);
  document.head.appendChild(s);
})();
