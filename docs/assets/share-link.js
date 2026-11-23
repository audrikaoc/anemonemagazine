(() => {
  if (!navigator.clipboard?.writeText) return;

  for (const button of document.querySelectorAll('[data-copy-link]')) {
    const status = document.getElementById(button.dataset.copyLink);
    button.addEventListener('click', async () => {
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
    button.hidden = false;
  }
})();
