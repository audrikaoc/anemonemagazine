(() => {
  const container = document.querySelector('[data-google-maps-key]');
  const switcher = container.closest('.reach-switcher');
  let unavailable = false;

  function loadMaps() {
    return new Promise((resolve, reject) => {
      function fail() {
        unavailable = true;
        container.hidden = true;
        clearTimeout(timeout);
        reject(new Error('Google Maps is unavailable.'));
      }

      const timeout = setTimeout(fail, 12000);
      window.gm_authFailure = fail;
      window.initAnemoneReachMap = () => {
        if (!window.google?.maps?.Map) {
          fail();
          return;
        }
        clearTimeout(timeout);
        resolve(window.google.maps);
      };

      const url = new URL('https://maps.googleapis.com/maps/api/js');
      url.search = new URLSearchParams({
        key: container.dataset.googleMapsKey,
        callback: 'initAnemoneReachMap',
        loading: 'async',
        v: 'quarterly',
      });
      const script = document.createElement('script');
      script.src = url.href;
      script.async = true;
      script.onerror = fail;
      document.head.append(script);
    });
  }

  async function showMap() {
    const [maps, response] = await Promise.all([loadMaps(), fetch(container.dataset.boundaries)]);
    if (!response.ok) throw new Error('Country boundaries are unavailable.');
    const boundaries = await response.json();
    if (unavailable) return;

    container.hidden = false;
    const map = new maps.Map(container, {
      center: { lat: 15, lng: 0 },
      zoom: 1,
      isFractionalZoomEnabled: true,
      gestureHandling: 'cooperative',
      streetViewControl: false,
      mapTypeControl: false,
    });
    map.data.addGeoJson(boundaries);
    map.fitBounds({ south: -58, west: -179.99, north: 79, east: 179.99 }, 12);

    function highlightAudience() {
      const { value } = switcher.querySelector('input[name="reach-audience"]:checked');
      const panel = switcher.querySelector('.reach-' + value);
      const countries = new Set(panel.dataset.countryCodes.split(' '));
      const fillColor = getComputedStyle(panel).getPropertyValue('--map-highlight').trim();
      container.setAttribute('aria-label', value === 'readers' ? 'Reader countries on Google Maps' : 'Contributor countries on Google Maps');
      map.data.setStyle(feature => {
        if (!countries.has(feature.getProperty('country'))) return { visible: false };
        if (feature.getGeometry().getType() === 'Point') {
          return { clickable: false, icon: {
            path: maps.SymbolPath.CIRCLE,
            scale: 4,
            fillColor,
            fillOpacity: .9,
            strokeColor: '#fff',
            strokeWeight: 1,
          } };
        }
        return { clickable: false, fillColor, fillOpacity: .58, strokeColor: fillColor, strokeWeight: 1 };
      });
    }

    highlightAudience();
    switcher.addEventListener('change', highlightAudience);
  }

  showMap().catch(() => { container.hidden = true; });
})();
