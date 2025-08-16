(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var cfgEl = document.getElementById('page-config') || { dataset: {} };
    var reverseUrl = cfgEl.dataset.reverseUrl || '/map/reverse_geocode';
    var aiServiceConfigured = (cfgEl.dataset.aiConfigured === 'true');
    var isAuthenticated = (cfgEl.dataset.authenticated === 'true');

    var map = L.map('map', {
      attributionControl: false,
      zoomControl: true
    }).setView([20, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(map);

    var modalContent = document.getElementById('modal-content');
    var likePlaceSection = document.getElementById('like-place-modal-section');
    function openModal() {
      if (window.$) { $('#aiInfoModal').modal('show'); }
    }

    function processLocation(latlng, locationName) {
      if (locationName === void 0) { locationName = null; }
      var lat = latlng.lat.toFixed(6);
      var lon = latlng.lng.toFixed(6);

      var loadingPopup = L.popup()
        .setLatLng(latlng)
        .setContent('Получаем данные от ИИ...')
        .openOn(map);

      modalContent.innerHTML = '<p class="text-secondary">Загрузка информации...</p>';
      if (likePlaceSection) likePlaceSection.style.display = 'none';

      if (!aiServiceConfigured) {
        loadingPopup.close();
        modalContent.innerHTML = '<div class="alert alert-warning">Сервис ИИ недоступен.</div>';
        openModal();
        return;
      }

      fetch(reverseUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: parseFloat(lat), longitude: parseFloat(lon) })
      })
      .then(function (response) { return response.json().then(function (data) { return ({ ok: response.ok, data: data }); }); })
      .then(function (_a) {
        var ok = _a.ok, data = _a.data;
        loadingPopup.close();
        if (!ok || data.error) {
          var errorMessage = data.error || 'Произошла сетевая ошибка';
          modalContent.innerHTML = '<div class="alert alert-danger"><strong>Ошибка:</strong> ' + errorMessage + '</div>';
        } else {
          var addr = data.address ? ('<div class="mb-2"><strong>Адрес (OSM):</strong> ' + ('' + data.address).replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</div>') : '';
          var ai = '';
          if (data.ai_description) {
            try {
              var md = (typeof marked !== 'undefined') ? marked.parse(String(data.ai_description)) : String(data.ai_description);
              var safe = (typeof DOMPurify !== 'undefined') ? DOMPurify.sanitize(md) : md;
              ai = '<div><strong>Описание:</strong><div class="mt-2">' + safe + '</div></div>';
            } catch (e) {
              ai = '<div><strong>Описание:</strong> ' + ('' + data.ai_description).replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</div>';
            }
          } else {
            ai = '<div class="text-secondary">Описание недоступно.</div>';
          }
          modalContent.innerHTML = addr + ai;
          if (isAuthenticated && likePlaceSection) {
            likePlaceSection.style.display = 'block';
            document.getElementById('form-latitude').value = lat;
            document.getElementById('form-longitude').value = lon;
            var cityNameInput = document.getElementById('form-city-name');
            cityNameInput.value = locationName || ('Место у (' + lat + ', ' + lon + ')');
          }
        }
        openModal();
      })
      .catch(function (error) {
        console.error('Ошибка при получении данных:', error);
        loadingPopup.close();
        var errorMessage = 'Не удалось получить информацию. Проверьте консоль браузера.';
        modalContent.innerHTML = '<div class="alert alert-danger">' + errorMessage + '</div>';
        openModal();
      });
    }

    var search = new GeoSearch.GeoSearchControl({
      provider: new GeoSearch.OpenStreetMapProvider(),
      style: 'bar',
      autoClose: true,
      keepResult: true,
      searchLabel: 'Поиск города или адреса...'
    });
    map.addControl(search);

    map.on('geosearch/showlocation', function (result) {
      processLocation({ lat: result.location.y, lng: result.location.x }, result.location.label);
    });
    map.on('click', function (e) { return processLocation(e.latlng); });

    // Закрытие модалки обрабатывается Bootstrap'ом

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        function (position) { return map.setView([position.coords.latitude, position.coords.longitude], 13); },
        function () { return console.warn('Геолокация не удалась.'); }
      );
    }
  });
})();
