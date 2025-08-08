// Front page (map) logic extracted from template
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    // Read config from data attributes
    var cfgEl = document.getElementById('page-config') || { dataset: {} };
    var getInfoUrl = cfgEl.dataset.getInfoUrl || '/map/get_location_info';
    var aiServiceConfigured = (cfgEl.dataset.aiConfigured === 'true');
    var isAuthenticated = (cfgEl.dataset.authenticated === 'true');

    // 1. Init map
    var map = L.map('map', {
      attributionControl: false,
      zoomControl: true
    }).setView([20, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(map);

    // 3. Modal elements
    var modalOverlay = document.getElementById('modal-overlay');
    var infoModal = document.getElementById('info-modal');
    var modalContent = document.getElementById('modal-content');
    var modalCloseBtn = document.getElementById('modal-close-btn');
    var likePlaceSection = document.getElementById('like-place-modal-section');

    // 4. Modal helpers
    function openModal() { modalOverlay.classList.add('visible'); }
    function closeModal() { modalOverlay.classList.remove('visible'); }

    // 5. Process click or search
    function processLocation(latlng, locationName) {
      if (locationName === void 0) { locationName = null; }
      var lat = latlng.lat.toFixed(6);
      var lon = latlng.lng.toFixed(6);

      // Show loading popup
      var loadingPopup = L.popup()
        .setLatLng(latlng)
        .setContent('Получаем данные от AI...')
        .openOn(map);

      modalContent.innerHTML = '<p class="text-secondary">Загрузка информации...</p>';
      if (likePlaceSection) likePlaceSection.style.display = 'none';

      if (!aiServiceConfigured) {
        loadingPopup.close();
        modalContent.innerHTML = '<div class="alert alert-warning">Сервис Google AI недоступен.</div>';
        openModal();
        return;
      }

      // Request backend
      fetch(getInfoUrl, {
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
          modalContent.innerHTML = '<p>' + data.info + '</p>';
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
        // eslint-disable-next-line no-console
        console.error('Ошибка при получении данных:', error);
        loadingPopup.close();
        var errorMessage = 'Не удалось получить информацию. Проверьте консоль браузера.';
        modalContent.innerHTML = '<div class="alert alert-danger">' + errorMessage + '</div>';
        openModal();
      });
    }

    // 7. Search & handlers
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

    // 8. Close modal
    modalCloseBtn.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', function (e) {
      if (e.target === modalOverlay) { closeModal(); }
    });

    // 9. Try geolocation
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        function (position) { return map.setView([position.coords.latitude, position.coords.longitude], 13); },
        function () { return console.warn('Геолокация не удалась.'); }
      );
    }
  });
})();
