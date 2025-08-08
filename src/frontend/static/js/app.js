// Global app-level JS (placeholder)
// Put shared helpers and initializations here.
(function () {
  // Example: expose a helper to safely set innerHTML as text
  window.App = window.App || {};
  window.App.setCode = function (el, text) {
    if (!el) return;
    el.textContent = String(text || '');
  };
})();
