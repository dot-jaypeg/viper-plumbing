(function () {
  'use strict';

  // Splash screen — logo intro, once per browser session
  var splash = document.getElementById('splash');
  if (splash) {
    var splashSeen = false;
    try { splashSeen = sessionStorage.getItem('viper-splash-seen') === '1'; } catch (e) {}

    if (splashSeen) {
      splash.remove();
    } else {
      var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      document.body.classList.add('no-scroll');
      var hideDelay = reduceMotion ? 100 : 1400;
      setTimeout(function () {
        splash.classList.add('is-hidden');
        document.body.classList.remove('no-scroll');
        try { sessionStorage.setItem('viper-splash-seen', '1'); } catch (e) {}
        setTimeout(function () { splash.remove(); }, reduceMotion ? 0 : 650);
      }, hideDelay);
    }
  }

  // Hero trust-signal text rotator
  var rotatorWord = document.getElementById('hero-rotator-word');
  if (rotatorWord) {
    var rotatorPhrases = ['Licensed & Insured', '24/7 Emergency', 'Family Owned', 'Free Camera Scope'];
    var rotatorIndex = 0;
    var rotatorReduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    setInterval(function () {
      rotatorIndex = (rotatorIndex + 1) % rotatorPhrases.length;
      if (rotatorReduceMotion) {
        rotatorWord.textContent = rotatorPhrases[rotatorIndex];
        return;
      }
      rotatorWord.classList.add('is-out');
      setTimeout(function () {
        rotatorWord.textContent = rotatorPhrases[rotatorIndex];
        rotatorWord.classList.remove('is-out');
      }, 350);
    }, 2200);
  }

  // Sticky header background on scroll
  var header = document.getElementById('site-header');
  var scrollCue = document.querySelector('.scroll-cue');
  function updateHeaderState() {
    if (header) header.classList.toggle('is-scrolled', window.scrollY > 40);
    if (scrollCue) scrollCue.classList.toggle('is-hidden', window.scrollY > 80);
  }
  updateHeaderState();
  window.addEventListener('scroll', updateHeaderState, { passive: true });

  // Mobile nav toggle
  var toggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Live clock + location, header detail
  var clockEl = document.getElementById('header-clock');
  function updateClock() {
    if (!clockEl) return;
    var now = new Date();
    var time = now.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      timeZone: 'America/Los_Angeles'
    });
    clockEl.textContent = time + ' PT';
  }
  updateClock();
  setInterval(updateClock, 1000 * 30);

  // Scroll-triggered reveal animations
  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          entry.target.classList.toggle('is-visible', entry.isIntersecting);
        });
      },
      { threshold: 0, rootMargin: '0px 0px -10% 0px' }
    );
    revealEls.forEach(function (el) { observer.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-visible'); });
  }

  // Contact form — working prototype only, not yet wired to a live inbox
  // (destination CRM/integration to be decided; likely GoHighLevel)
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      form.classList.add('is-submitted');
    });
  }

  // Footer year
  var yearEl = document.getElementById('footer-year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();
})();
