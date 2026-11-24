(() => {
  const now = new Date();
  const today = [now.getFullYear(), now.getMonth() + 1, now.getDate()]
    .map(part => String(part).padStart(2, '0')).join('-');

  for (const call of document.querySelectorAll('[data-submission-call]')) {
    const badge = call.querySelector('[data-call-status]');
    if (!badge) continue;

    const {opens, closes} = call.dataset;
    let status = '';
    if (closes && today > closes) status = 'Closed';
    else if (opens && today < opens) status = 'Upcoming';
    else if (opens && closes) status = 'Open';

    if (status) {
      badge.textContent = status;
      badge.dataset.status = status.toLowerCase();
      badge.hidden = false;
    }
  }

  const nextDeadline = Array.from(document.querySelectorAll('[data-deadline]'))
    .find(item => item.dataset.deadline >= today);
  if (nextDeadline) nextDeadline.hidden = false;
})();
