const newsletterForm = document.querySelector('.newsletter-form');
const newsletterStatus = document.querySelector('#newsletter-status');
const newsletterButton = newsletterForm.querySelector('button[type="submit"]');

newsletterForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (newsletterButton.disabled) return;

  const body = new URLSearchParams(new FormData(newsletterForm));
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  newsletterButton.disabled = true;
  newsletterStatus.removeAttribute('data-state');
  newsletterStatus.textContent = 'Submitting your signup…';

  try {
    await fetch(newsletterForm.action, {
      method: 'POST',
      mode: 'no-cors',
      body,
      signal: controller.signal,
    });
    // Google Forms returns an opaque response to the homepage.
    newsletterForm.reset();
    newsletterStatus.dataset.state = 'sent';
    newsletterStatus.textContent = 'Thanks! Your newsletter signup was sent.';
  } catch {
    newsletterStatus.dataset.state = 'error';
    newsletterStatus.textContent = 'We couldn’t send your signup. Please try again.';
  } finally {
    clearTimeout(timeout);
    newsletterButton.disabled = false;
  }
});
