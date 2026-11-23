(() => {
  const tools = document.querySelector('.archive-tools');
  const form = tools.querySelector('.archive-filters');
  const status = tools.querySelector('.archive-status');
  const jumps = document.querySelector('.archive-jumps');
  const words = value => value.normalize('NFKD').toLowerCase()
    .replace(/\p{M}/gu, '').match(/[\p{L}\p{N}]+/gu) || [];

  const groups = Array.from(document.querySelectorAll('[data-issue-group]'), group => ({
    element: group,
    jump: jumps.querySelector(`a[href="#${group.getAttribute('aria-labelledby')}"]`),
    cards: Array.from(group.querySelectorAll('.issue-card'), card => ({
      element: card,
      words: words(`${card.querySelector('.issue-title').textContent} ${card.querySelector('.issue-meta').textContent}`),
    })),
  }));

  function update() {
    const query = words(form.elements.query.value);
    const issueType = form.elements.type.value;
    const year = form.elements.year.value;
    let count = 0;

    for (const group of groups) {
      const matchesType = !issueType || group.element.dataset.issueGroup === issueType;
      let groupCount = 0;
      for (const card of group.cards) {
        const matches = matchesType && (!year || card.element.dataset.year === year)
          && query.every(term => card.words.some(word => word === term || (!/^\d+$/.test(term) && word.startsWith(term))));
        card.element.hidden = !matches;
        if (matches) groupCount += 1;
      }
      group.element.hidden = groupCount === 0;
      group.jump.hidden = group.element.hidden;
      count += groupCount;
    }

    jumps.hidden = count === 0;
    status.textContent = count ? `${count} ${count === 1 ? 'issue' : 'issues'}` : 'No matching issues. Try another search or clear the filters.';
  }

  form.addEventListener('input', update);
  form.addEventListener('submit', event => {
    event.preventDefault();
    update();
  });
  form.addEventListener('reset', () => requestAnimationFrame(update));
  tools.hidden = false;
  update();
})();
