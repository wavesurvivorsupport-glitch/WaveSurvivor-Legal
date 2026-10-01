(() => {
  'use strict';
  const root = document.documentElement.dataset.root || './';

  document.querySelectorAll('.mobile-nav a').forEach(link => {
    link.addEventListener('click', () => {
      const menu = document.querySelector('.mobile-menu');
      if (menu) menu.open = false;
    });
  });

  const tabs = [...document.querySelectorAll('[role="tab"][data-role]')];
  function selectRole(tab, focus = false) {
    tabs.forEach(item => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
      const panel = document.getElementById(item.getAttribute('aria-controls'));
      if (panel) panel.hidden = !selected;
    });
    if (focus) tab.focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectRole(tab));
    tab.addEventListener('keydown', event => {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight' && event.key !== 'Home' && event.key !== 'End') return;
      event.preventDefault();
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 :
        (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
      selectRole(tabs[next], true);
    });
  });

  const scenes = [...document.querySelectorAll('.scene-step')];
  const screen = document.querySelector('.scene-screen');
  let setSceneSlots = () => {};
  if (screen && scenes.length) {
    let activeScene = scenes[0];
    let sceneSlots = {};
    const updateSceneImage = () => {
      const config = sceneSlots[activeScene.dataset.scenePath];
      let image = screen.querySelector('.scene-image');
      if (!config || !config.src || !config.alt) {
        if (image) image.remove();
        screen.classList.remove('has-media');
        screen.setAttribute('role', 'img');
        screen.setAttribute('aria-label', 'Changing concept panel reserved for real environmental and gameplay captures');
        return;
      }
      if (!image) {
        image = document.createElement('img');
        image.className = 'slot-image scene-image';
        image.loading = 'lazy';
        screen.prepend(image);
      }
      if (image.getAttribute('src') !== root + config.src) image.src = root + config.src;
      image.alt = config.alt;
      screen.classList.add('has-media');
      screen.removeAttribute('role');
      screen.removeAttribute('aria-label');
    };
    setSceneSlots = slots => { sceneSlots = slots; updateSceneImage(); };
    const activate = step => {
      activeScene = step;
      scenes.forEach(item => item.classList.toggle('is-active', item === step));
      screen.dataset.scene = step.dataset.scene;
      const label = screen.querySelector('[data-scene-label]');
      const title = screen.querySelector('[data-scene-title]');
      if (label) label.textContent = step.dataset.sceneLabel;
      if (title) title.textContent = step.dataset.sceneTitle;
      updateSceneImage();
    };
    activate(scenes[0]);
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => { if (entry.isIntersecting) activate(entry.target); });
      }, { rootMargin: '-35% 0px -45% 0px' });
      scenes.forEach(step => observer.observe(step));
    }
  }

  const reveal = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.documentElement.classList.add('motion-ready');
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); }
      });
    }, { threshold: .08 });
    reveal.forEach(item => observer.observe(item));
  } else reveal.forEach(item => item.classList.add('is-visible'));

  const fetchData = async path => {
    const response = await fetch(root + path);
    if (!response.ok) throw new Error('Data unavailable');
    return response.json();
  };

  const gallery = document.querySelector('[data-gallery]');
  const mediaSlots = [...document.querySelectorAll('[data-asset-path]')];
  const trailerSlot = document.querySelector('[data-trailer]');
  if (gallery || mediaSlots.length || trailerSlot) {
    fetchData('data/media.json').then(data => {
      const slots = data.slots || {};
      setSceneSlots(slots);
      mediaSlots.forEach(slot => {
        const config = slots[slot.dataset.assetPath];
        if (!config || !config.src || !config.alt) return;
        const img = document.createElement('img');
        img.src = root + config.src;
        img.alt = config.alt;
        img.className = 'slot-image';
        img.loading = slot.classList.contains('hero-media') ? 'eager' : 'lazy';
        slot.prepend(img);
        slot.classList.add('has-media');
        slot.removeAttribute('role');
        slot.removeAttribute('aria-label');
      });
      if (trailerSlot && data.trailer && data.trailer.src) {
        const video = document.createElement('video');
        video.className = 'trailer-video';
        video.controls = true;
        video.preload = 'none';
        video.playsInline = true;
        video.setAttribute('aria-label', data.trailer.label || 'WaveSurvivor trailer');
        video.src = root + data.trailer.src;
        if (data.trailer.poster) video.poster = root + data.trailer.poster;
        trailerSlot.replaceChildren(video);
        trailerSlot.removeAttribute('role');
        trailerSlot.removeAttribute('aria-label');
      }
      if (!gallery) return;
      const items = Array.isArray(data.items) ? data.items : [];
      if (!items.length) return;
      gallery.replaceChildren();
      items.forEach(item => {
        if (!item.src || !item.alt) return;
        const figure = document.createElement('figure');
        const img = document.createElement('img');
        img.src = root + item.src;
        img.alt = item.alt;
        img.loading = 'lazy';
        img.width = item.width || 1600;
        img.height = item.height || 900;
        figure.append(img, text('figcaption', item.caption || 'WaveSurvivor media'));
        gallery.append(figure);
      });
    }).catch(() => {});
  }
})();
