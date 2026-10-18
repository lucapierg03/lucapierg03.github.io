// Navigation toggle, project filters and image lightbox.
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Project filters (projects page). The URL hash (#university) preselects a chapter.
  var filters = document.querySelectorAll('.filter');
  if (filters.length) {
    var cards = document.querySelectorAll('.project-grid .card');
    var apply = function (key) {
      filters.forEach(function (b) { b.classList.toggle('is-active', b.dataset.filter === key); });
      cards.forEach(function (c) {
        c.hidden = key !== 'all' && c.dataset.chapters.split(' ').indexOf(key) === -1;
      });
    };
    filters.forEach(function (b) {
      b.addEventListener('click', function () {
        apply(b.dataset.filter);
        history.replaceState(null, '', b.dataset.filter === 'all' ? location.pathname : '#' + b.dataset.filter);
      });
    });
    var start = location.hash.slice(1);
    if (document.querySelector('.filter[data-filter="' + start + '"]')) apply(start);
  }

  // Lightbox
  var box = document.querySelector('.lightbox');
  var links = Array.prototype.slice.call(document.querySelectorAll('a.lb'));
  if (!box || !links.length) return;
  var bimg = box.querySelector('img'), bcap = box.querySelector('figcaption');
  var group = [], idx = 0, last = null;
  var show = function (i) {
    idx = (i + group.length) % group.length;
    var a = group[idx];
    bimg.src = a.getAttribute('href');
    bimg.alt = a.dataset.caption || '';
    bcap.textContent = a.dataset.caption || '';
    var multi = group.length > 1;
    box.querySelector('.lb-prev').hidden = !multi;
    box.querySelector('.lb-next').hidden = !multi;
  };
  var open = function (a) {
    last = a;
    group = links.filter(function (l) { return l.dataset.group === a.dataset.group; });
    show(group.indexOf(a));
    box.hidden = false;
    document.body.style.overflow = 'hidden';
    box.querySelector('.lb-close').focus();
  };
  var close = function () {
    box.hidden = true;
    document.body.style.overflow = '';
    bimg.removeAttribute('src');
    if (last) last.focus();
  };
  links.forEach(function (a) {
    a.addEventListener('click', function (ev) { ev.preventDefault(); open(a); });
  });
  box.querySelector('.lb-close').addEventListener('click', close);
  box.querySelector('.lb-prev').addEventListener('click', function () { show(idx - 1); });
  box.querySelector('.lb-next').addEventListener('click', function () { show(idx + 1); });
  box.addEventListener('click', function (ev) { if (ev.target === box) close(); });
  document.addEventListener('keydown', function (ev) {
    if (box.hidden) return;
    if (ev.key === 'Escape') close();
    if (ev.key === 'ArrowLeft') show(idx - 1);
    if (ev.key === 'ArrowRight') show(idx + 1);
  });
})();
