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

  const issue = document.querySelector('[data-issue-slug]');
  if (issue) {
    window.gtag('event', 'issue_open', { issue_slug: issue.dataset.issueSlug });
  }

  function trackSubmissionForm(event) {
    if (event.defaultPrevented || event.button !== (event.type === 'auxclick' ? 1 : 0)) return;
    const link = event.target.closest('a[data-submission-form]');
    if (link) {
      window.gtag('event', 'submission_form_click', { submission_call: link.dataset.submissionForm });
    }
  }

  document.addEventListener('click', trackSubmissionForm);
  document.addEventListener('auxclick', trackSubmissionForm);
})();
