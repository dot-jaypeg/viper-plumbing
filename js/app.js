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

  // Lead forms — post straight from the browser to the GHL inbound webhook
  // (workflow "ENDPOINT - website-forms"). No server hop; GHL is the only backend.
  var GHL_WEBHOOK_URL = 'https://services.leadconnectorhq.com/hooks/Znb6kB9cRNv6WN1qmd1M/webhook-trigger/112ad8aa-ff53-4105-8ebb-955733c8c171';
  var PHONE_DISPLAY = '(657) 637-8529';
  var ATTR_KEY = 'viper-attr';
  var ATTR_MAX_AGE_MS = 90 * 24 * 60 * 60 * 1000;   // matches Google Ads' 90-day gclid window
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'gbraid', 'wbraid', 'fbclid'];

  // Latest-touch attribution: an ad-tagged visit replaces the saved source;
  // an untagged visit keeps it (up to 90 days) so return visits stay credited.
  function captureAttribution() {
    var query = new URLSearchParams(window.location.search);
    var tagged = UTM_KEYS.some(function (k) { return query.get(k); });
    var stored = null;
    try { stored = JSON.parse(localStorage.getItem(ATTR_KEY) || 'null'); } catch (e) {}
    var fresh = stored && stored._captured && (Date.now() - Date.parse(stored._captured) < ATTR_MAX_AGE_MS);
    if (!tagged && fresh) return stored;
    var attr = {
      _captured: new Date().toISOString(),
      landing_page: window.location.pathname + window.location.search,
      referrer: document.referrer || ''
    };
    UTM_KEYS.forEach(function (k) { attr[k] = query.get(k) || ''; });
    try { localStorage.setItem(ATTR_KEY, JSON.stringify(attr)); } catch (e) {}
    return attr;
  }
  var attribution = captureAttribution();

  function toKey(name) {
    return String(name).trim().toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
  }

  // US numbers -> +1XXXXXXXXXX (GHL dedupes contacts on E.164)
  function toE164(raw) {
    var digits = String(raw || '').replace(/\D/g, '');
    if (digits.length === 10) return '+1' + digits;
    if (digits.length === 11 && digits[0] === '1') return '+' + digits;
    return String(raw || '').trim();
  }

  function newEventId() {
    return (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2);
  }

  function buildLeadPayload(form) {
    var data = {};
    new FormData(form).forEach(function (value, key) {
      if (key === 'website') return; // never send the honeypot
      data[key === 'Source' ? 'form_source' : toKey(key)] = typeof value === 'string' ? value.trim() : value;
    });
    var parts = (data.name || '').split(/\s+/).filter(Boolean);
    data.full_name = data.name || '';
    data.first_name = parts.shift() || '';
    data.last_name = parts.join(' ');
    delete data.name;
    data.phone = toE164(data.phone);
    data.source = 'Website';
    data.form_name = window.location.pathname.replace(/\/+$/, '').replace(/\.html$/, '').replace(/^\/+/, '') || 'home';
    if (data.form_name === 'index') data.form_name = 'home';
    data.form_id = form.id || '';
    data.page_url = window.location.href.split('#')[0];
    data.submitted_at = new Date().toISOString();
    return data;
  }

  function fillHiddenFields(form) {
    UTM_KEYS.concat(['referrer', 'landing_page']).forEach(function (k) {
      var el = form.querySelector('input[name="' + k + '"]');
      if (el) el.value = attribution[k] || '';
    });
    var eid = form.querySelector('input[name="event_id"]');
    if (eid) eid.value = newEventId();
  }

  function validateLead(form) {
    var errors = [];
    var name = form.querySelector('[name="name"]');
    var phone = form.querySelector('[name="phone"]');
    var email = form.querySelector('[name="email"]');
    form.querySelectorAll('.is-invalid').forEach(function (el) { el.classList.remove('is-invalid'); });
    if (name && !name.value.trim()) errors.push([name, 'your name']);
    if (phone && String(phone.value).replace(/\D/g, '').length < 10) errors.push([phone, 'a valid phone number']);
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) errors.push([email, 'a valid email']);
    errors.forEach(function (err) {
      err[0].classList.add('is-invalid');
      err[0].setAttribute('aria-invalid', 'true');
    });
    if (errors.length) errors[0][0].focus();
    return errors.map(function (err) { return err[1]; });
  }

  document.querySelectorAll('form[data-contact-form]').forEach(function (form) {
    fillHiddenFields(form);
    form.setAttribute('novalidate', '');
    var status = form.querySelector('[data-form-status]');
    var btn = form.querySelector('[type="submit"]');
    var btnLabel = btn ? btn.textContent : '';
    var busy = false;

    function showStatus(msg, isError) {
      if (!status) return;
      status.hidden = false;
      status.textContent = msg;
      status.classList.toggle('is-error', !!isError);
    }

    function showSuccess() {
      if (status) status.hidden = true;
      form.reset();
      fillHiddenFields(form);
      form.classList.add('is-submitted');
    }

    form.querySelectorAll('input, select, textarea').forEach(function (el) {
      el.addEventListener('input', function () {
        el.classList.remove('is-invalid');
        el.removeAttribute('aria-invalid');
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (busy) return; // duplicate-submit guard

      var hp = form.querySelector('input[name="website"]');
      if (hp && hp.value.trim()) { showSuccess(); return; } // bot: fake success, send nothing

      var missing = validateLead(form);
      if (missing.length) {
        showStatus('Please enter ' + missing.join(', ') + '.', true);
        return;
      }

      var payload = buildLeadPayload(form);
      busy = true;
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      if (status) status.hidden = true;

      fetch(GHL_WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (res) {
          if (res.ok) {
            if (window.gtag) gtag('event', 'generate_lead', { event_id: payload.event_id, currency: 'USD' });
            showSuccess();
          } else {
            showStatus('Something went wrong sending your request. Please call us at ' + PHONE_DISPLAY + '.', true);
          }
        })
        .catch(function () {
          showStatus('We couldn’t send your request. Please call us at ' + PHONE_DISPLAY + '.', true);
        })
        .finally(function () {
          busy = false;
          if (btn) { btn.disabled = false; btn.textContent = btnLabel; }
        });
    });
  });

  // Footer year
  var yearEl = document.getElementById('footer-year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();
})();
