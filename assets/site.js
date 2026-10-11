(function () {
  'use strict';
  var root = document.documentElement;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ----------------------------------------------------------------
     Spring. Apple's two parameters: damping ratio and response (s).
     The animation always starts from the current value and velocity,
     so retargeting mid-flight never jumps or hits a wall.
  ---------------------------------------------------------------- */
  function Spring(opts) {
    this.x = opts.from || 0;
    this.v = 0;
    this.target = this.x;
    this.damping = opts.damping == null ? 1 : opts.damping;
    this.response = opts.response || 0.35;
    this.onUpdate = opts.onUpdate || function () {};
    this.onRest = opts.onRest || function () {};
    this.eps = opts.eps || 0.01;
    this._raf = 0; this._last = 0;
    this._tick = this._tick.bind(this);
  }
  Spring.prototype.set = function (x) {
    this.stop(); this.x = this.target = x; this.v = 0; this.onUpdate(x); this.onRest(x);
  };
  Spring.prototype.to = function (target, velocity) {
    this.target = target;
    if (velocity != null) this.v = velocity;
    if (!this._raf) { this._last = performance.now(); this._raf = requestAnimationFrame(this._tick); }
  };
  Spring.prototype.stop = function () { if (this._raf) cancelAnimationFrame(this._raf); this._raf = 0; };
  Spring.prototype._tick = function (now) {
    var dt = Math.min(Math.max((now - this._last) / 1000, 0), 1 / 30); this._last = now;
    var w = (2 * Math.PI) / this.response;        // natural frequency
    var k = w * w, c = 2 * this.damping * w;      // stiffness, damping coefficient (mass = 1)
    var steps = Math.max(1, Math.round(dt * 240)), h = dt / steps;
    for (var i = 0; i < steps; i++) {
      var a = -k * (this.x - this.target) - c * this.v;
      this.v += a * h; this.x += this.v * h;
    }
    if (Math.abs(this.v) < this.eps && Math.abs(this.x - this.target) < this.eps) {
      this.x = this.target; this.v = 0; this._raf = 0; this.onUpdate(this.x); this.onRest(this.x); return;
    }
    this.onUpdate(this.x);
    this._raf = requestAnimationFrame(this._tick);
  };

  /* ----------------------------------------------------------------
     Theme switch. Knob travels 20px. Critically damped, 0.3s response.
  ---------------------------------------------------------------- */
  var themeBtn = document.getElementById('theme');
  var knob = document.getElementById('knob');
  var TRAVEL = 20;
  var darkQuery = window.matchMedia('(prefers-color-scheme: dark)');
  function isDark() {
    var t = root.getAttribute('data-theme');
    if (t) return t === 'dark';
    return darkQuery.matches;
  }
  var knobSpring = new Spring({
    from: isDark() ? TRAVEL : 0, damping: 1, response: 0.3, eps: 0.05,
    onUpdate: function (x) { knob.style.setProperty('--kx', x.toFixed(2) + 'px'); }
  });
  knobSpring.set(isDark() ? TRAVEL : 0);
  themeBtn.setAttribute('aria-pressed', String(isDark()));
  themeBtn.addEventListener('click', function () {
    var dark = !isDark();
    root.setAttribute('data-theme', dark ? 'dark' : 'light');
    try { localStorage.setItem('theme', dark ? 'dark' : 'light'); } catch (e) {}
    themeBtn.setAttribute('aria-pressed', String(dark));
    if (reduceMotion.matches) knobSpring.set(dark ? TRAVEL : 0);
    else knobSpring.to(dark ? TRAVEL : 0);
  });
  darkQuery.addEventListener('change', function () {
    if (!root.getAttribute('data-theme')) {
      themeBtn.setAttribute('aria-pressed', String(isDark()));
      knobSpring.to(isDark() ? TRAVEL : 0);
    }
  });

  /* ----------------------------------------------------------------
     Scroll edge on the nav: only once content meets the chrome.
  ---------------------------------------------------------------- */
  var nav = document.getElementById('nav');
  function onScroll() { nav.classList.toggle('scrolled', window.scrollY > 6); }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ----------------------------------------------------------------
     Mobile menu sheet. One spring drives translateY, scale and the
     scrim together so the surface arrives as a material, not a fade.
     Enter and exit share the same path. Interruptible at any time.
  ---------------------------------------------------------------- */
  var menuBtn = document.getElementById('menu-btn');
  var sheet = document.getElementById('sheet');
  var scrim = document.getElementById('scrim');
  var menuOpen = false;
  var sheetSpring = new Spring({
    from: 0, damping: 1, response: 0.38, eps: 0.002,
    onUpdate: function (p) {
      sheet.style.visibility = 'visible';
      sheet.style.transform = 'translateY(' + ((p - 1) * 100).toFixed(3) + '%) scale(' + (0.98 + 0.02 * p).toFixed(4) + ')';
      sheet.style.opacity = Math.min(1, p * 1.6).toFixed(3);
      scrim.style.opacity = p.toFixed(3);
      scrim.style.pointerEvents = p > 0.05 ? 'auto' : 'none';
    },
    onRest: function (p) { if (p <= 0) { sheet.style.visibility = 'hidden'; scrim.style.pointerEvents = 'none'; } }
  });
  function setMenu(open) {
    menuOpen = open;
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? menuBtn.getAttribute('data-close') : menuBtn.getAttribute('data-open'));
    if (reduceMotion.matches) sheetSpring.set(open ? 1 : 0);
    else sheetSpring.to(open ? 1 : 0);
  }
  menuBtn.addEventListener('click', function () { setMenu(!menuOpen); });
  scrim.addEventListener('click', function () { setMenu(false); });
  sheet.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menuOpen) { setMenu(false); menuBtn.focus(); } });
  window.matchMedia('(min-width: 761px)').addEventListener('change', function (m) { if (m.matches && menuOpen) setMenu(false); });

  /* ----------------------------------------------------------------
     Reveal on scroll.
  ---------------------------------------------------------------- */
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  /* ----------------------------------------------------------------
     Visit counter (GoatCounter), shown only if it responds.
  ---------------------------------------------------------------- */
  var el = document.getElementById('visits'), num = document.getElementById('visit-num');
  if (el && num) {
    fetch('https://berkekavak.goatcounter.com/counter/TOTAL.json')
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (d && d.count) { num.textContent = d.count.trim(); el.hidden = false; } })
      .catch(function () {});
  }
})();
