(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const still = reduce || /[?&#]static\b/.test(location.href);
  const stage = document.getElementById('cc-stage');

  // fit fixed-width mockups to their frames ----------------------------------
  const mks = [...document.querySelectorAll('.mk')];
  const fit = m => {
    const dw = parseFloat(getComputedStyle(m).getPropertyValue('--dw')) || m.clientWidth;
    m.style.setProperty('--s', (m.clientWidth / dw).toFixed(5));
  };
  mks.forEach(fit);
  if ('ResizeObserver' in window) {
    const ro = new ResizeObserver(es => es.forEach(e => fit(e.target)));
    mks.forEach(m => ro.observe(m));
  } else {
    window.addEventListener('resize', () => mks.forEach(fit));
  }

  // scroll reveals ----------------------------------------------------------
  const rv = document.querySelectorAll('.rv');
  if (still || !('IntersectionObserver' in window)) {
    rv.forEach(el => el.classList.add('in'));
  } else {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    rv.forEach(el => io.observe(el));
  }

  // concept animation: line → model → mass ---------------------------------
  if (stage) {
    const play = () => {
      stage.classList.remove('play', 'done');
      void stage.getBoundingClientRect();
      stage.classList.add('play');
    };
    if (still) {
      stage.classList.add('done');
    } else {
      const so = new IntersectionObserver(es => {
        if (es[0].isIntersecting) { play(); so.disconnect(); }
      }, { threshold: 0.35 });
      so.observe(stage);
    }
    stage.querySelector('.cc-replay').addEventListener('click', () => {
      if (reduce) return;
      play();
    });
  }

  // nav: active section + light/dark ----------------------------------------
  const nav = document.getElementById('nav');
  const links = [...nav.querySelectorAll('nav a')];
  const dark = new Set(['dir-c', 'next']);
  const secs = [...document.querySelectorAll('[data-nav]')];
  const setActive = id => {
    links.forEach(a => a.classList.toggle('act', a.dataset.k === id));
    nav.classList.toggle('on-dark', dark.has(id));
  };
  const onScroll = () => {
    const y = 60;
    let cur = secs[0];
    for (const s of secs) if (s.getBoundingClientRect().top <= y) cur = s;
    // B's opener is navy: treat its first screen as dark
    let id = cur.dataset.nav;
    setActive(id);
    if (id === 'dir-b') {
      const op = cur.querySelector('.dir-open').getBoundingClientRect();
      nav.classList.toggle('on-dark', op.bottom > y);
    }
  };
  let tick = false;
  window.addEventListener('scroll', () => {
    if (!tick) { requestAnimationFrame(() => { onScroll(); tick = false; }); tick = true; }
  }, { passive: true });
  onScroll();
})();
