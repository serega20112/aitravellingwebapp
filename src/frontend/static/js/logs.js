// Logs dashboard client-side logic
(function () {
  const rows = document.getElementById('rows');
  const totalEl = document.getElementById('total');
  const pager = document.getElementById('pager');
  const form = document.getElementById('search-form');
  let page = 0;
  let size = 50;

  function tsToLocal(ts) {
    if (!ts) return '';
    const d = new Date(ts);
    return d.toLocaleString();
  }

  function badge(level) {
    const cls = 'badge badge-level badge-' + (level || 'INFO');
    return '<span class="' + cls + '">' + (level || '') + '</span>';
  }

  async function load() {
    const params = new URLSearchParams();
    const q = document.getElementById('q').value.trim();
    const level = document.getElementById('level').value;
    const from = document.getElementById('from').value;
    const to = document.getElementById('to').value;
    if (q) params.set('q', q);
    if (level) params.set('level', level);
    if (from) params.set('from', new Date(from).toISOString());
    if (to) params.set('to', new Date(to).toISOString());
    params.set('page', page);
    params.set('size', size);

    const res = await fetch('/logs/api/search?' + params.toString());
    const data = await res.json();

    totalEl.textContent = 'Всего: ' + data.total;
    rows.innerHTML = data.hits.map(function (h) {
      const ts = tsToLocal(h.timestamp);
      const lvl = badge(h.level);
      const msg = (h.message || '').replace(/</g,'&lt;');
      const req = (h.method || '') + ' ' + (h.path || '') + ' ' + (h.status_code || '');
      return (
        '<tr class="log-row">' +
          '<td>' + ts + '</td>' +
          '<td>' + lvl + '</td>' +
          '<td><code>' + msg + '</code></td>' +
          '<td>' + req + '</td>' +
        '</tr>'
      );
    }).join('');

    // simple pager (prev/next)
    pager.innerHTML = (
      '<li class="page-item ' + (page<=0?'disabled':'') + '">' +
        '<a class="page-link" href="#" id="btn-prev">Назад</a>' +
      '</li>' +
      '<li class="page-item ' + (data.hits.length < size ? 'disabled' : '') + '">' +
        '<a class="page-link" href="#" id="btn-next">Вперёд</a>' +
      '</li>'
    );

    const prev = document.getElementById('btn-prev');
    const next = document.getElementById('btn-next');
    if (prev) prev.onclick = function (e) { e.preventDefault(); page = Math.max(0, page - 1); load(); };
    if (next) next.onclick = function (e) { e.preventDefault(); page = page + 1; load(); };
  }

  if (form) {
    form.addEventListener('submit', function (e) { e.preventDefault(); page = 0; load(); });
  }

  document.addEventListener('DOMContentLoaded', load);
})();
