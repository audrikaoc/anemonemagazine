(() => {
  const actions = document.querySelector('.resource-actions');
  const copy = actions.querySelector('.resource-copy');
  const print = actions.querySelector('.resource-print');
  const status = document.querySelector('.resource-copy-status');

  if (navigator.clipboard?.writeText) {
    copy.hidden = false;
    copy.addEventListener('click', async () => {
      const url = new URL(window.location.href);
      url.search = '';
      url.hash = '';
      try {
        await navigator.clipboard.writeText(url.href);
        status.textContent = 'Link copied.';
      } catch {
        status.textContent = 'Copy the link from your address bar.';
      }
    });
  }

  print.addEventListener('click', () => window.print());
  actions.hidden = false;
})();
