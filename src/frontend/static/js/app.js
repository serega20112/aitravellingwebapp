// Global app-level JS (placeholder)
// Put shared helpers and initializations here.
(function () {
  // Helpers namespace
  window.App = window.App || {};
  window.App.setCode = function (el, text) {
    if (!el) return;
    el.textContent = String(text || '');
  };

  // Universal Markdown render: any element with [data-markdown] or .markdown
  function renderMarkdownInDocument() {
    try {
      var nodes = Array.prototype.slice.call(document.querySelectorAll('[data-markdown], .markdown'));
      nodes.forEach(function (node) {
        // Use textContent as source (escaping from templates stays safe)
        var src = node.textContent || '';
        var html = (typeof marked !== 'undefined') ? marked.parse(String(src)) : src;
        var safe = (typeof DOMPurify !== 'undefined') ? DOMPurify.sanitize(html) : html;
        node.innerHTML = safe;
      });
    } catch (e) {
      // no-op
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderMarkdownInDocument);
  } else {
    renderMarkdownInDocument();
  }
})();
