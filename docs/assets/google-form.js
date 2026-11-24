(() => {
  const form = document.querySelector('[data-google-form]');
  const answer = form.querySelector('input, textarea');
  const status = form.querySelector('.form-status');
  const button = form.querySelector('button[type="submit"]');
  const subject = form.dataset.googleForm;

  function showInvalid(message) {
    answer.setAttribute('aria-invalid', 'true');
    status.dataset.state = 'error';
    status.textContent = message;
    answer.focus();
  }

  answer.addEventListener('invalid', (event) => {
    event.preventDefault();
    showInvalid(answer.validity.valueMissing
      ? answer.dataset.requiredMessage
      : answer.dataset.invalidMessage || answer.validationMessage);
  });

  answer.addEventListener('input', () => {
    answer.setCustomValidity(answer.value && !answer.value.trim() ? answer.dataset.requiredMessage : '');
    answer.removeAttribute('aria-invalid');
    status.removeAttribute('data-state');
    status.textContent = '';
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (button.disabled) return;

    const value = answer.value.trim();
    if (!value) {
      showInvalid(answer.dataset.requiredMessage);
      return;
    }

    const body = new URLSearchParams(new FormData(form));
    body.set(answer.name, value);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    button.disabled = true;
    answer.readOnly = true;
    status.removeAttribute('data-state');
    status.textContent = `Sending your ${subject}…`;

    try {
      await fetch(form.action, { method: 'POST', mode: 'no-cors', body, signal: controller.signal });
      // Google Forms returns an opaque response to the site.
      form.reset();
      status.dataset.state = 'sent';
      status.textContent = `Thanks! Your ${subject} was sent.`;
      const feedbackFields = form.querySelector('.feedback-fields');
      if (feedbackFields) {
        feedbackFields.remove();
        status.focus();
      }
    } catch {
      status.dataset.state = 'error';
      status.textContent = `We couldn’t send your ${subject}. Please try again.`;
    } finally {
      clearTimeout(timeout);
      button.disabled = false;
      answer.readOnly = false;
    }
  });
})();
