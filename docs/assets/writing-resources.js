(() => {
  const actions = document.querySelector('.resource-actions');
  actions.querySelector('.resource-print').addEventListener('click', () => window.print());
  actions.hidden = false;
})();
