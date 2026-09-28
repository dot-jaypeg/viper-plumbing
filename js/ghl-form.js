/* ghl-form.js - AM landing page lead form -> GoHighLevel inbound webhook (direct post).
   Viper Rooter & Plumbing landing pages (from the am-landing-pages skill template).

   Works on any <form data-ghl-form> whose fields use these names (all optional except
   name + phone): name, phone, email, zip, service (select), message, company_website
   (honeypot). Error text goes into [data-err-for="<field id>"], send errors into
   .form-status. Validates, waits SEND_DELAY_MS, posts JSON, waits for the response,
   pushes generate_lead, waits AFTER_LEAD_MS, then redirects to the thank-you page. */
(function () {
  "use strict";

  var CONFIG = {
    // GHL inbound webhook - Viper Rooter & Plumbing sub-account (location Znb6kB9cRNv6WN1qmd1M),
    // workflow "ENDPOINT - website-forms": the same trigger js/app.js posts to, so landing
    // page leads land in the existing workflow. form_name (the page slug) tells them apart.
    GHL_WEBHOOK_URL: "https://services.leadconnectorhq.com/hooks/Znb6kB9cRNv6WN1qmd1M/webhook-trigger/112ad8aa-ff53-4105-8ebb-955733c8c171",
    THANK_YOU_URL: "/thank-you.html",
    PHONE_DISPLAY: "(657) 637-8529",   // exactly as shown on the site (number-swap matching)
    PHONE_TEL: "+16576378529",
    ATTR_KEY: "viper-lp-attr",
    NAME_KEY: "viper-lead-first"
  };
  var UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "gbraid", "wbraid", "fbclid"];
  var SEND_DELAY_MS = 1500;   // required: the webhook sometimes won't post without it
  var AFTER_LEAD_MS = 500;    // let GTM tags fire before leaving the page
  var MIN_FILL_MS = 2500;     // faster than this is a bot
  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  var shownAt = Date.now();

  // ---- attribution: kept for the visit; a new tagged landing replaces the whole set ----
  function readAttribution() {
    var qs = new URLSearchParams(location.search);
    var tagged = UTM_KEYS.some(function (k) { return qs.get(k); });
    var stored = null;
    try { stored = JSON.parse(sessionStorage.getItem(CONFIG.ATTR_KEY) || "null"); } catch (e) {}
    if (stored && !tagged) return stored;
    var attr = { landing_page: location.pathname + location.search, referrer: document.referrer || "" };
    UTM_KEYS.forEach(function (k) { attr[k] = qs.get(k) || ""; });
    try { sessionStorage.setItem(CONFIG.ATTR_KEY, JSON.stringify(attr)); } catch (e) {}
    return attr;
  }
  var attribution = readAttribution();

  // Thank-you page: greet by first name if we have it (<span data-thanks-name></span>)
  var thanks = document.querySelector("[data-thanks-name]");
  if (thanks) { try { var n = sessionStorage.getItem(CONFIG.NAME_KEY); if (n) thanks.textContent = ", " + n; } catch (e) {} }

  // ---- helpers ----
  function toE164(raw) {
    var d = String(raw || "").replace(/\D/g, "");
    if (d.length === 10) return "+1" + d;
    if (d.length === 11 && d.charAt(0) === "1") return "+" + d;
    return String(raw || "").trim();
  }
  function pageSlug() {
    var p = location.pathname.replace(/\/+$/, "").replace(/\.html$/, "").replace(/^\/+/, "").replace(/\/index$/, "");
    return p || "home";
  }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function track(name, params) {
    try { if (typeof window.gtag === "function") window.gtag("event", name, params || {}); } catch (e) {}
    try { (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: name }, params || {})); } catch (e) {}
  }
  function field(form, n) { return form.elements[n]; }
  function val(form, n) { var el = field(form, n); return el ? (el.value || "").trim() : ""; }
  function setError(form, el, msg) {
    var slot = form.querySelector('[data-err-for="' + el.id + '"]');
    if (slot) slot.textContent = msg || "";
    el.setAttribute("aria-invalid", msg ? "true" : "false");
  }
  function validate(form) {
    var firstBad = null;
    ["name", "phone", "email", "service"].forEach(function (n) {
      var el = field(form, n);
      if (!el) return;
      var v = (el.value || "").trim();
      var msg = "";
      if (el.required && !v) msg = el.getAttribute("data-msg") || "Required";
      else if (n === "phone" && v && v.replace(/\D/g, "").length !== 10) msg = el.getAttribute("data-msg") || "Please enter a 10-digit phone number";
      else if (n === "email" && v && !EMAIL.test(v)) msg = "Please enter a valid email";
      setError(form, el, msg);
      if (msg && !firstBad) firstBad = el;
    });
    if (firstBad) firstBad.focus();
    return !firstBad;
  }
  function buildPayload(form) {
    var name = val(form, "name");
    var parts = name.split(/\s+/).filter(Boolean);
    var svc = field(form, "service");
    var service = svc && svc.value ? svc.options[svc.selectedIndex].text : "";
    var data = {
      first_name: parts.shift() || "",
      last_name: parts.join(" "),
      full_name: name,
      email: val(form, "email").toLowerCase(),
      phone: toE164(val(form, "phone")),
      postal_code: val(form, "zip"),
      service: service,
      service_needed: service,   // key the homepage/contact forms send; keeps the existing GHL mapping working
      message: val(form, "message"),
      source: "Website",
      form_source: "Website - " + (document.title.split("|")[0].trim() || pageSlug()),
      form_name: pageSlug(),
      page_url: location.href.split("#")[0],
      landing_page: attribution.landing_page || "",
      referrer: attribution.referrer || "",
      submitted_at: new Date().toISOString()
    };
    UTM_KEYS.forEach(function (k) { data[k] = attribution[k] || ""; });
    data.form_summary = [
      service && "Service needed: " + service,
      data.postal_code && "ZIP: " + data.postal_code,
      data.message && "Details: " + data.message,
      "Page: " + data.page_url
    ].filter(Boolean).join("\n");
    return data;
  }

  // ---- phone formatting as they type ----
  document.querySelectorAll('form[data-ghl-form] [name="phone"]').forEach(function (el) {
    el.addEventListener("input", function () {
      var d = el.value.replace(/\D/g, "").slice(0, 10), out = d;
      if (d.length > 6) out = "(" + d.slice(0, 3) + ") " + d.slice(3, 6) + "-" + d.slice(6);
      else if (d.length > 3) out = "(" + d.slice(0, 3) + ") " + d.slice(3);
      else if (d.length > 0) out = "(" + d;
      el.value = out;
    });
  });

  // ---- wire every form ----
  document.querySelectorAll("form[data-ghl-form]").forEach(function (form) {
    var btn = form.querySelector("button[type=submit]");
    var status = form.querySelector(".form-status");
    var btnHTML = btn.innerHTML;

    form.addEventListener("input", function (e) {
      if (e.target.getAttribute("aria-invalid") === "true") setError(form, e.target, "");
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (btn.disabled) return;
      if (status) status.textContent = "";
      if (!validate(form)) return;

      // Honeypot filled or filled in faster than a person can = bot: pretend success, send nothing.
      if (val(form, "company_website") || Date.now() - shownAt < MIN_FILL_MS) { location.href = CONFIG.THANK_YOU_URL; return; }

      var data = buildPayload(form);
      btn.disabled = true;
      btn.textContent = "Sending…";

      wait(SEND_DELAY_MS)
        .then(function () {
          if (!CONFIG.GHL_WEBHOOK_URL) throw new Error("webhook URL not set");
          return fetch(CONFIG.GHL_WEBHOOK_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Accept": "application/json" },
            body: JSON.stringify(data)
          });
        })
        .then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          track("generate_lead", { form_name: data.form_name, service: data.service });
          try { sessionStorage.setItem(CONFIG.NAME_KEY, data.first_name); } catch (err) {}
          return wait(AFTER_LEAD_MS).then(function () { location.href = CONFIG.THANK_YOU_URL; });
        })
        .catch(function () {
          btn.disabled = false;
          btn.innerHTML = btnHTML;
          if (status) status.innerHTML = 'Something went wrong sending your request. Please try again or call us at <a href="tel:' + CONFIG.PHONE_TEL + '">' + CONFIG.PHONE_DISPLAY + "</a>.";
        });
    });
  });
})();
