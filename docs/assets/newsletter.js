const newsletterForm = document.querySelector('.newsletter-form');
const newsletterResult = document.querySelector('#newsletter-result');
const newsletterStatus = document.querySelector('#newsletter-status');

newsletterResult.hidden = true;
newsletterForm.addEventListener('submit', () => {
  newsletterStatus.textContent = 'Submitting your signup…';
  newsletterResult.hidden = false;
  newsletterResult.scrollIntoView({ block: 'nearest' });
});

newsletterResult.addEventListener('load', () => {
  if (!newsletterResult.hidden) {
    newsletterStatus.textContent = 'See your signup result below.';
  }
});
