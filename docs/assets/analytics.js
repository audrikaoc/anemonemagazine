(() => {
  const { hostname, pathname, protocol } = window.location;
  const magazineDomain = hostname === 'www.anemonemagazine.com' || hostname === 'anemonemagazine.com';
  const pagesDomain = hostname === 'audrikaoc.github.io' && pathname.startsWith('/anemonemagazine/');
  if (protocol !== 'https:' || (!magazineDomain && !pagesDomain)) return;

  const measurementId = document.currentScript.dataset.measurementId;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', measurementId, {
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
  });

  const tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
  document.head.append(tag);
})();
