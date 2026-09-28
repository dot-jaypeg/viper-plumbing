#!/usr/bin/env python3
"""Generates the service landing pages (/<slug>/index.html), thank-you.html and 404.html.

Per-page content lives in PAGES below; the shared shell (head, header, footer, mobile bar)
is rendered around it. Edit this file and re-run it; don't hand-edit the generated HTML.

    python3 _build/build_landing.py

Copy rules: facts, offers, reviews and photos come from the existing site only.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://viperrooterandplumbing.com"
BIZ = "Viper Rooter & Plumbing"
PHONE = "(657) 637-8529"          # exactly as the site displays it (number-swap matching)
TEL = "+16576378529"
CALL = f"Call {PHONE}"
LICENSE = "1022901"
ADDRESS = {"street": "1840 W Lincoln Ave", "city": "Anaheim", "region": "CA", "zip": "92804"}
YELP = "https://www.yelp.com/biz/viper-rooter-and-plumbing-anaheim-7"
CITIES = ["Anaheim", "Santa Ana", "Orange", "Fullerton", "Garden Grove", "Buena Park",
          "Placentia", "Yorba Linda", "Brea", "Tustin"]

# Service options match the homepage/contact form so GHL sees the same values.
SERVICE_OPTIONS = ["General Plumbing Repair", "Sewer Liners", "Epoxy Pipe Lining", "Water Repipes",
                   "Gas Repipes", "Water Heater Swap", "Tankless Install", "Drain Cleaning",
                   "Hydro Jetting", "Something Else"]

# Verbatim from the site's review cards.
REVIEWS = {
    "daniel": ("The first ones to reply with an actual person instead of a bot &mdash; they showed up in about 1.5 hours, way faster than anyone else we called.", "Daniel H.", "Fremont, CA"),
    "jisoo": ("He operates with strong integrity, is fair with pricing, and never upsells. He tells you exactly what you need, no pressure.", "Jisoo Y.", "Diamond Bar, CA"),
    "adriana": ("Professional, responsive, and efficient &mdash; some of the most affordable plumbing services around, with full transparency and very fair pricing.", "Adriana F.", "Los Angeles, CA"),
    "elaine": ("Responsive and reliable &mdash; was able to solve the issue and serviced our outdoor drain through the pouring rain.", "Elaine C.", "Irvine, CA"),
}

LANDING_PAGES = [("plumbing-services", "Plumbing Services")]   # footer Services column, in order

PAGES = [
    {
        "slug": "plumbing-services",
        "name": "Plumbing Services",
        "title": "Plumbing Services in Anaheim, CA | Local Plumbers | Viper Rooter &amp; Plumbing",
        "description": "Plumbing services and repairs from local, family-owned plumbers in Anaheim and surrounding areas. Open 24/7, licensed &amp; insured (Lic #1022901), $89 drain cleaning special. Call (657) 637-8529.",
        "og_image": "/assets/images/page-heroes/services-hero.jpg",
        "hero_video": ("/assets/content/video/web/hero-plumber-pipes.mp4", "/assets/content/video/web/hero-plumber-pipes-poster.jpg"),
        "eyebrow": "Anaheim Plumbing Services",
        "h1": ("Local Plumbers.", "No Shortcuts."),
        "lead_lg": "Family-owned plumbing services for Anaheim and the surrounding cities. From drain cleaning and water heaters to full water and gas repipes, you get an honest answer, upfront pricing and plumbing repairs done right the first time, 24 hours a day, 7 days a week.",
        "lead_sm": "Family-owned plumbing repairs in Anaheim and nearby cities, on call 24/7.",
        "checks": [f"Licensed &amp; Insured, Lic #{LICENSE}", "Open 24/7, Mon&ndash;Sun", "Upfront, Honest Pricing"],
        "service": "General Plumbing Repair",
        "stats": [("24/7", "Mon&ndash;Sun, 24 hours"), ("$89", "Drain cleaning special"),
                  ("20 mi", "Radius of Anaheim"), (f"#{LICENSE}", "Licensed &amp; insured")],
        "offer": True,
        "grid": {
            "heading": "Plumbing Services &amp; Repairs",
            "intro": "One local team for the whole system, from the drain line to the water heater. Pick what you need and we&rsquo;ll get you a free quote.",
            "cards": [
                ("Drain Cleaning", "Drain Cleaning", "Clogs cleared through a proper clean-out access, then confirmed clear on camera. Backed by our $89 special and free camera scope."),
                ("Hydro Jetting", "Hydro Jetting", "High-pressure hydro jetting to clear stubborn buildup and roots for good."),
                ("Sewer Liners", "Sewer Liners", "Trenchless sewer liner installation that restores your line without tearing up the yard."),
                ("Epoxy Pipe Lining", "Epoxy Pipe Lining", "Structural epoxy pipe restoration for aging or damaged lines, sealing cracks, corrosion and small leaks from the inside."),
                ("Water Repipes", "Water Repipes", "Full home repiping when patch repairs stop making sense, for better pressure and fewer future leaks."),
                ("Gas Repipes", "Gas Repipes", "Gas line replacement and repiping to current code, pressure-tested and verified safe."),
                ("Water Heater Swaps", "Water Heater Swap", "Straightforward water heater replacement, sized right for your household and tested for safe operation."),
                ("Tankless Installs", "Tankless Install", "Tankless water heater installation for continuous hot water and a smaller footprint."),
            ],
            "emergency": ("24/7 Emergency Plumbing", "Burst pipe, major leak or a sewer line backing up at 2 a.m.? We&rsquo;re available Monday through Sunday, 24 hours a day. Call and talk to our team."),
        },
        "values_heading": "Why Viper",
        "values": [
            ("check", "Honest Answers", "We tell you exactly what you need and nothing you don&rsquo;t, with upfront, honest pricing and no surprise fees."),
            ("home", "Family Owned", "Viper carries forward the standard set by twenty years in the industry. It&rsquo;s our family name on every job."),
            ("clock", "On Call 24/7", "Leaks and backups don&rsquo;t keep business hours, so neither do we. Call any time, Monday through Sunday."),
        ],
        "steps": [
            ("Call or Request a Quote", f"Call {PHONE} or send the form, any time of day or night."),
            ("We Find the Cause", "We diagnose the real problem, using a camera scope on drain and sewer lines where it helps."),
            ("You Get an Upfront Price", "An honest recommendation and a clear price before any work starts. No pressure."),
            ("Done Right, Tested", "We complete the work and test it before we leave, so it&rsquo;s fixed right the first time."),
        ],
        "reviews": ["daniel", "jisoo", "adriana"],
        "area_heading": "Plumbing Services Across Anaheim &amp; Surrounding Areas",
        "area_copy": "Based at 1840 W Lincoln Ave in Anaheim, our local plumbers cover a 20-mile radius, including Santa Ana, Orange, Fullerton, Garden Grove, Buena Park, Placentia, Yorba Linda, Brea and Tustin.",
        "faqs": [
            ("How much do plumbing repairs cost in Anaheim?",
             "It depends on the problem, so we look first and give you an upfront, honest price before any work begins, with no surprise fees. Drain cleaning starts with our $89 special from a proper clean-out access, and a free camera scope comes with your service."),
            ("Do you offer 24/7 emergency plumbing?",
             f"Yes. We&rsquo;re available 24 hours a day, 7 days a week, weekends included. For a burst pipe, major leak or sewage backup, call <a href=\"tel:{TEL}\">{PHONE}</a> instead of filling out the form. If water is spreading and you can safely reach it, shutting off the main water valve limits the damage until we arrive."),
            ("How do I choose the best plumber near me?",
             f"Look for a licensed contractor (you can look up any license on the California Contractors State License Board site), clear upfront pricing and recent reviews from real customers. Viper is licensed and insured under contractor license #{LICENSE}, and you can read our reviews on <a href=\"{YELP}\" target=\"_blank\" rel=\"noopener\">Yelp</a>."),
            ("What areas do your plumbers serve?",
             "Anaheim and a 20-mile radius around it, including Santa Ana, Orange, Fullerton, Garden Grove, Buena Park, Placentia, Yorba Linda, Brea and Tustin. Not sure you&rsquo;re in range? Give us a call and ask."),
        ],
        "cta": ("Need a Plumber Near You?", "Call anytime, we&rsquo;re on 24/7, or send the details and we&rsquo;ll get back to you fast."),
    },
]

# ---------------------------------------------------------------- icons
ICON_PHONE = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
ICON_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="m8 12.5 2.6 2.6L16.5 9"/></svg>'
VALUE_ICONS = {
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 10.5 12 3l9 7.5V21h-6v-6H9v6H3z"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
}


def strip_tags(s):
    import re
    return html.unescape(re.sub(r"<[^>]+>", "", s))


# ---------------------------------------------------------------- shell
def head(title, description, canonical=None, og_image=None, noindex=False, jsonld=()):
    parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- Google Tag Manager: paste the container snippet here once the GTM ID is issued.
     ghl-form.js already pushes generate_lead to the dataLayer on every successful lead. -->
<script>window.dataLayer = window.dataLayer || [];</script>
<title>{title}</title>
<meta name="description" content="{description}">"""]
    if noindex:
        parts.append('<meta name="robots" content="noindex">')
    if canonical:
        parts.append(f"""<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{html.escape(BIZ)}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">""")
    if og_image:
        parts.append(f'<meta property="og:image" content="{DOMAIN}{og_image}">')
    parts.append("""<link rel="icon" href="/assets/logos/viper-logo-transparent.png">
<link rel="stylesheet" href="/css/styles.css">
<link rel="stylesheet" href="/css/landing.css">""")
    for block in jsonld:
        parts.append('<script type="application/ld+json">\n' + json.dumps(block, indent=2) + "\n</script>")
    parts.append("</head>")
    return "\n".join(parts)


def header(quote_href="/contact.html"):
    return f"""<a class="skip-link" href="#main">Skip to content</a>

<div class="announce-bar">
  <div class="announce-track">
    <span>24/7 Emergency Service</span>
    <span class="announce-sep">&middot;</span>
    <span>20-Mile Radius of Anaheim</span>
    <span class="announce-sep">&middot;</span>
    <span>Licensed &amp; Insured &mdash; Lic #{LICENSE}</span>
    <span class="announce-sep">&middot;</span>
    <span>Family Owned &amp; Operated</span>
  </div>
</div>

<header class="site-header" id="site-header">
  <div class="container header-inner">
    <a class="brand" href="/" aria-label="Viper Rooter &amp; Plumbing — Home">
      <img src="/assets/logos/viper-logo-white.png" alt="Viper Rooter &amp; Plumbing">
    </a>

    <nav class="main-nav" id="main-nav">
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/about.html">About</a></li>
        <li><a href="/services.html">Services</a></li>
        <li><a href="/contact.html">Contact</a></li>
      </ul>
    </nav>

    <div class="header-right">
      <div class="header-meta" id="header-meta" aria-hidden="true">
        <span class="header-clock" id="header-clock">--:-- --</span>
        <span class="header-dot">&middot;</span>
        <span class="header-location">Anaheim, CA</span>
      </div>
      <a class="btn btn-primary btn-small" href="tel:{TEL}">{CALL}</a>
      <button class="nav-toggle" id="nav-toggle" aria-label="Toggle menu" aria-expanded="false" aria-controls="main-nav">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>"""


def footer():
    lp_links = "\n".join(f'      <a href="/{slug}/">{name}</a>' for slug, name in LANDING_PAGES)
    return f"""<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-brand">
      <img src="/assets/logos/viper-logo-white.png" alt="Viper Rooter &amp; Plumbing">
      <p>Family owned. Honest solutions. Highest level of service.</p>
    </div>

    <nav class="footer-nav">
      <span class="footer-heading">Site</span>
      <a href="/">Home</a>
      <a href="/about.html">About</a>
      <a href="/services.html">Services</a>
      <a href="/#reviews">Reviews</a>
      <a href="/contact.html">Contact</a>
    </nav>

    <nav class="footer-nav">
      <span class="footer-heading">Services</span>
{lp_links}
      <a href="/services.html">Sewer Liners</a>
      <a href="/services.html">Water &amp; Gas Repipes</a>
      <a href="/services.html">Water Heaters &amp; Tankless</a>
      <a href="/services.html">Drain Cleaning &amp; Hydro Jetting</a>
    </nav>

    <div class="footer-contact">
      <span class="footer-heading">Contact</span>
      <a href="tel:{TEL}">{PHONE}</a>
      <span>{ADDRESS['street']}, {ADDRESS['city']}, {ADDRESS['region']} {ADDRESS['zip']}</span>
      <span>Mon&ndash;Sun, 24 Hours</span>
    </div>
  </div>

  <div class="container footer-bottom">
    <span>&copy; <span id="footer-year">2026</span> Viper Rooter &amp; Plumbing. Contractor License #{LICENSE}.</span>
  </div>
</footer>"""


def call_btn(cls="btn btn-primary btn-large"):
    return f'<a class="{cls}" href="tel:{TEL}">{ICON_PHONE} {CALL}</a>'


def business_schema():
    return {
        "@type": "Plumber",
        "name": BIZ,
        "url": DOMAIN + "/",
        "telephone": TEL,
        "image": DOMAIN + "/assets/logos/viper-logo.png",
        "address": {"@type": "PostalAddress", "streetAddress": ADDRESS["street"], "addressLocality": ADDRESS["city"],
                    "addressRegion": ADDRESS["region"], "postalCode": ADDRESS["zip"], "addressCountry": "US"},
        "openingHoursSpecification": {"@type": "OpeningHoursSpecification",
                                      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                      "opens": "00:00", "closes": "23:59"},
    }


# ---------------------------------------------------------------- landing page
def quote_form(p):
    opts = "\n".join(
        f'              <option{" selected" if o == p["service"] else ""}>{o}</option>' for o in SERVICE_OPTIONS)
    return f"""      <form class="contact-form lp-form" id="quote" data-ghl-form novalidate>
        <h2 class="form-title">Get a Free Quote</h2>
        <p class="form-sub">Tell us what&rsquo;s going on. A member of the Viper team will be in touch shortly.</p>
        <div class="form-hp" aria-hidden="true">
          <label for="q-company-website">Company website</label>
          <input type="text" id="q-company-website" name="company_website" tabindex="-1" autocomplete="off">
        </div>
        <div class="form-grid">
          <div class="form-row full">
            <label for="q-name">Full Name</label>
            <input type="text" id="q-name" name="name" autocomplete="name" required data-msg="Please enter your name">
            <span class="field-err" data-err-for="q-name"></span>
          </div>
          <div class="form-row">
            <label for="q-phone">Phone</label>
            <input type="tel" id="q-phone" name="phone" autocomplete="tel" inputmode="tel" required data-msg="Please enter a 10-digit phone number">
            <span class="field-err" data-err-for="q-phone"></span>
          </div>
          <div class="form-row">
            <label for="q-email">Email</label>
            <input type="email" id="q-email" name="email" autocomplete="email">
            <span class="field-err" data-err-for="q-email"></span>
          </div>
          <div class="form-row">
            <label for="q-zip">ZIP Code</label>
            <input type="text" id="q-zip" name="zip" autocomplete="postal-code" inputmode="numeric" maxlength="10">
          </div>
          <div class="form-row">
            <label for="q-service">Service Needed</label>
            <select id="q-service" name="service">
{opts}
            </select>
            <span class="field-err" data-err-for="q-service"></span>
          </div>
        </div>
        <button type="submit" class="btn btn-ghost btn-block">Request My Free Quote</button>
        <p class="form-status" role="alert"></p>
        <p class="form-note">Or call <a href="tel:{TEL}">{PHONE}</a>, we&rsquo;re on 24/7.</p>
      </form>"""


def hero(p):
    video, poster = p["hero_video"]
    checks = "\n".join(f"          <li>{ICON_CHECK}{c}</li>" for c in p["checks"])
    l1, l2 = p["h1"]
    return f"""  <section class="lp-hero">
    <div class="hero-media">
      <video autoplay muted loop playsinline poster="{poster}">
        <source src="{video}" type="video/mp4">
      </video>
      <div class="hero-overlay"></div>
    </div>

    <div class="container hero-grid">
      <div class="hero-copy">
        <p class="eyebrow">{p['eyebrow']}</p>
        <h1>{l1}<br><span class="accent">{l2}</span></h1>
        <p class="lead lead-lg">{p['lead_lg']}</p>
        <p class="lead lead-sm">{p['lead_sm']}</p>
        <div class="hero-actions btn-row">
          {call_btn()}
          <a class="btn btn-ghost btn-large hero-quote" href="#quote">Get a Free Quote</a>
        </div>
        <ul class="hero-checks">
{checks}
        </ul>
      </div>

{quote_form(p)}
    </div>
  </section>"""


def stats(p):
    items = "\n".join(
        f'      <div class="stat"><span class="stat-num">{n}</span><span class="stat-label">{l}</span></div>'
        for n, l in p["stats"])
    return f"""  <section class="lp-stats" aria-label="At a glance">
    <div class="container stats-grid">
{items}
    </div>
  </section>"""


def offer():
    return """  <section class="promo">
    <div class="container promo-inner reveal">
      <div class="promo-text">
        <h2>$89 Drain Cleaning Special</h2>
        <p>From a proper clean-out access, plus a free camera scope with your service.</p>
      </div>
      <a class="btn btn-invert btn-large" href="#quote" data-service="Drain Cleaning">Claim This Offer</a>
    </div>
  </section>"""


def grid(p, tone):
    g = p["grid"]
    cards = []
    for i, (title, svc, desc) in enumerate(g["cards"], 1):
        cards.append(f"""        <div class="service-card reveal">
          <span class="service-num">{i:02d}</span>
          <h3>{title}</h3>
          <p>{desc}</p>
          <a class="card-link" href="#quote" data-service="{svc}">Get a Free Quote &rarr;</a>
        </div>""")
    et, ed = g["emergency"]
    cards.append(f"""        <div class="service-card is-emergency reveal">
          <div>
            <h3>{et}</h3>
            <p>{ed}</p>
          </div>
          {call_btn("btn btn-primary btn-large")}
        </div>""")
    return f"""  <section class="lp-section lp-services {tone}" id="services">
    <div class="container">
      <div class="section-head">
        <h2 class="section-heading reveal">{g['heading']}</h2>
        <p class="section-intro reveal">{g['intro']}</p>
      </div>
      <div class="services-grid">
{chr(10).join(cards)}
      </div>
    </div>
  </section>"""


def values(p, tone):
    cards = "\n".join(f"""        <div class="value-card reveal">
          <span class="value-icon">{VALUE_ICONS[icon]}</span>
          <h3>{t}</h3>
          <p>{d}</p>
        </div>""" for icon, t, d in p["values"])
    return f"""  <section class="lp-section {tone}">
    <div class="container">
      <div class="section-head">
        <h2 class="section-heading reveal">{p['values_heading']}</h2>
      </div>
      <div class="value-grid">
{cards}
      </div>
    </div>
  </section>"""


def steps(p, tone):
    items = "\n".join(f"""        <li class="step reveal">
          <h3>{t}</h3>
          <p>{d}</p>
        </li>""" for t, d in p["steps"])
    return f"""  <section class="lp-section {tone}">
    <div class="container">
      <div class="section-head">
        <h2 class="section-heading reveal">How It Works</h2>
      </div>
      <ol class="steps">
{items}
      </ol>
      <div class="hero-actions section-cta reveal">
        <a class="btn btn-ghost btn-large" href="#quote">Get a Free Quote</a>
        {call_btn()}
      </div>
    </div>
  </section>"""


def reviews(p, tone):
    cards = []
    for key in p["reviews"]:
        q, who, where = REVIEWS[key]
        cards.append(f"""        <div class="review-card reveal">
          <div class="review-stars" aria-label="5 stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
          <p class="review-quote">&ldquo;{q}&rdquo;</p>
          <p class="review-author">{who} <span>{where}</span></p>
        </div>""")
    return f"""  <section class="reviews lp-reviews {tone}" id="reviews">
    <div class="container">
      <h2 class="section-heading reveal">On Yelp</h2>
      <div class="reviews-grid">
{chr(10).join(cards)}
      </div>
      <a class="btn btn-ghost btn-large reveal" href="{YELP}" target="_blank" rel="noopener">Read More on Yelp</a>
    </div>
  </section>"""


def area(p):
    chips = "\n".join(f"        <span>{c}</span>" for c in CITIES)
    return f"""  <section class="area lp-area" id="area">
    <div class="hero-media">
      <video autoplay muted loop playsinline preload="none" poster="/assets/content/video/web/service-area-santa-ana-poster.jpg">
        <source src="/assets/content/video/web/service-area-santa-ana.mp4" type="video/mp4">
      </video>
      <div class="hero-overlay hero-overlay-area"></div>
    </div>
    <div class="container area-content">
      <h2 class="section-heading reveal">{p['area_heading']}</h2>
      <p class="reveal">{p['area_copy']}</p>
      <div class="area-chips reveal">
{chips}
      </div>
    </div>
  </section>"""


def faq(p, tone):
    items = "\n".join(f"""        <details class="reveal">
          <summary>{q}</summary>
          <p>{a}</p>
        </details>""" for q, a in p["faqs"])
    return f"""  <section class="lp-section {tone}" id="faq">
    <div class="container">
      <div class="section-head">
        <h2 class="section-heading reveal">Questions, Answered</h2>
      </div>
      <div class="faq">
{items}
      </div>
    </div>
  </section>"""


def cta(p, tone):
    h, sub = p["cta"]
    return f"""  <section class="lp-cta {tone}">
    <div class="container">
      <h2 class="section-heading reveal">{h}</h2>
      <p class="reveal">{sub}</p>
      <div class="hero-actions reveal">
        {call_btn()}
        <a class="btn btn-ghost btn-large" href="#quote">Get a Free Quote</a>
      </div>
    </div>
  </section>"""


# Service-card / offer links preselect the matching option before jumping to the form.
PRESELECT_JS = """<script>
document.querySelectorAll('a[data-service]').forEach(function (a) {
  a.addEventListener('click', function () {
    var sel = document.getElementById('q-service');
    if (sel) sel.value = a.getAttribute('data-service');
  });
});
</script>"""


def render_landing(p):
    canonical = f"{DOMAIN}/{p['slug']}/"
    service_ld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": p["name"],
        "serviceType": p["name"],
        "url": canonical,
        "description": strip_tags(p["description"]),
        "areaServed": [{"@type": "City", "name": f"{c}, CA"} for c in CITIES],
        "provider": business_schema(),
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": strip_tags(q),
                        "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in p["faqs"]],
    }
    # Section tones alternate: hero (video) > stats (alt) > offer (alt, bordered promo) > grid (bg)
    # > values (alt) > steps (bg) > reviews (alt) > area (video) > faq (alt) > cta (bg) > footer (alt)
    body = [
        head(p["title"], p["description"], canonical, p["og_image"], jsonld=[service_ld, faq_ld]),
        '<body class="has-mobile-bar">\n',
        header(),
        '\n<main id="main">\n',
        hero(p),
        stats(p),
    ]
    if p.get("offer"):
        body.append(offer())
    body += [grid(p, ""), values(p, "tone-alt"), steps(p, ""), reviews(p, "tone-alt"), area(p),
             faq(p, "tone-alt"), cta(p, "")]
    body += [
        "\n</main>\n",
        footer(),
        f"""
<div class="mobile-bar">
  <a class="btn btn-primary" href="tel:{TEL}">{CALL}</a>
  <a class="btn btn-ghost" href="#quote">Free Quote</a>
</div>

{PRESELECT_JS}
<script src="/js/ghl-form.js"></script>
<script src="/js/app.js"></script>
</body>
</html>
""",
    ]
    return "\n".join(body)


def render_simple(title, description, h1, copy, actions, noindex=True, hero_img="/assets/images/page-heroes/contact-hero.jpg"):
    return "\n".join([
        head(title, description, noindex=noindex),
        "<body>\n",
        header(),
        f"""
<main id="main">
  <section class="page-hero lp-simple">
    <div class="page-hero-media"><img src="{hero_img}" alt=""></div>
    <div class="container">
      <h1>{h1}</h1>
      <p>{copy}</p>
      <div class="hero-actions">
        {actions}
      </div>
    </div>
  </section>
</main>
""",
        footer(),
        """
<script src="/js/ghl-form.js"></script>
<script src="/js/app.js"></script>
</body>
</html>
""",
    ])


def main():
    for p in PAGES:
        out = ROOT / p["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(render_landing(p))
        print("wrote", out.relative_to(ROOT))

    (ROOT / "thank-you.html").write_text(render_simple(
        "Thank You | Viper Rooter &amp; Plumbing",
        "Thanks for contacting Viper Rooter &amp; Plumbing.",
        "Thanks<span data-thanks-name></span>.<br>We&rsquo;ve Got It.",
        "Your request is in. A member of the Viper team will be in touch shortly. Need help right now? Call us, we&rsquo;re on 24/7.",
        f'{call_btn()}\n        <a class="btn btn-ghost btn-large" href="/">Back to Home</a>',
    ))
    print("wrote thank-you.html")

    (ROOT / "404.html").write_text(render_simple(
        "Page Not Found | Viper Rooter &amp; Plumbing",
        "That page couldn’t be found.",
        "Page Not Found",
        "The page you&rsquo;re looking for has moved or doesn&rsquo;t exist. Head back home, or call us, we&rsquo;re on 24/7.",
        f'<a class="btn btn-ghost btn-large" href="/">Back to Home</a>\n        {call_btn()}',
        hero_img="/assets/images/page-heroes/services-hero.jpg",
    ))
    print("wrote 404.html")


if __name__ == "__main__":
    main()
