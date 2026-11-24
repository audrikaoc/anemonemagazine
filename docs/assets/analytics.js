(() => {
  const { hostname, pathname, protocol } = window.location;
  const magazineDomain = hostname === 'www.anemonemagazine.com' || hostname === 'anemonemagazine.com';
  const pagesDomain = hostname === 'audrikaoc.github.io' && pathname.startsWith('/anemonemagazine/');
  if (protocol !== 'https:' || (!magazineDomain && !pagesDomain)) return;

  const measurementId = document.currentScript.dataset.measurementId;
  const preferences = document.querySelector('#analytics-preferences');
  const notice = document.querySelector('#analytics-notice');
  const storageKey = 'anemone-analytics-consent';
  const disableKey = 'ga-disable-' + measurementId;
  let tagLoaded = false;

  function enableAnalytics() {
    window[disableKey] = false;
    if (tagLoaded) {
      window.gtag('consent', 'update', { analytics_storage: 'granted' });
      return;
    }

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      analytics_storage: 'denied',
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
    });
    window.gtag('consent', 'update', { analytics_storage: 'granted' });
    window.gtag('js', new Date());
    window.gtag('config', measurementId, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
    });

    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
    document.head.append(tag);
    tagLoaded = true;
  }

  function showNotice(visible) {
    notice.hidden = !visible;
    preferences.setAttribute('aria-expanded', String(visible));
  }

  preferences.parentElement.hidden = false;
  preferences.addEventListener('click', () => {
    showNotice(notice.hidden);
    if (!notice.hidden) notice.querySelector('h2').focus();
  });

  for (const button of notice.querySelectorAll('[data-analytics-choice]')) {
    button.addEventListener('click', () => {
      const choice = button.dataset.analyticsChoice;
      try {
        localStorage.setItem(storageKey, choice);
      } catch {
        // The choice still applies to this page if browser storage is unavailable.
      }

      if (choice === 'granted') {
        enableAnalytics();
      } else if (tagLoaded) {
        window[disableKey] = true;
        window.gtag('consent', 'update', { analytics_storage: 'denied' });
      }

      showNotice(false);
      preferences.focus({ preventScroll: true });
    });
  }

  let savedChoice;
  try {
    savedChoice = localStorage.getItem(storageKey);
  } catch {
    // Ask again when the browser cannot retrieve a saved choice.
  }
  if (savedChoice === 'granted') enableAnalytics();
  else if (savedChoice !== 'denied') showNotice(true);
})();
