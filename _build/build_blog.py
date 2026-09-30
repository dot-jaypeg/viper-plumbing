#!/usr/bin/env python3
"""Generates the blog: /blog/index.html and /blog/<slug>/index.html.

Posts live in _build/blog-src/<NN>-<slug>/post.md (audited copy, front matter + a small
Markdown subset) with images-provenance.md beside it. Edit those and re-run; don't
hand-edit the generated HTML.

    python3 _build/build_blog.py                  # render pages
    python3 _build/build_blog.py --images <dir>   # also (re)process images from the Drive
                                                  # package folder (blog-NN-<slug>/ subfolders); needs Pillow
    python3 _build/audit_blog.py                  # check the output before pushing

Markdown handled: ## / ### headings, paragraphs, **bold**, [text](/link), "- " bullet lists,
and the "**Question?**\\nAnswer" FAQ blocks. Anything else is a build error, so stray
Markdown can't leak onto the site.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_landing import (ROOT, DOMAIN, BIZ, PHONE, TEL, CALL, LICENSE, ASSET_V,  # noqa: E402
                           ICON_PHONE, ICON_CHECK, business_schema)

SRC = ROOT / "_build" / "blog-src"
OUT = ROOT / "blog"
IMG_DIR = ROOT / "assets" / "images" / "blog"
BLOG_CSS_V = "20260930c"   # bump when css/blog.css changes
PUBLISHED = "2026-09-30"   # default publish date; override per post with "date" in POSTS

# Per-post settings. "images" lists the files to use, lead image first (it's the card/OG
# image and sits under the intro). Files in the Drive folder but left out here were
# rejected in the audit (weak subject match).
POSTS = {
    "01": {"topic": "Sewer", "images": ["t01-01_Trenchless_Sewer_Repair.jpg", "t01-03_Horizontalbohrung_mit_Erdrakete.png"]},
    "02": {"topic": "Repipes", "images": ["t02-03_wikimedia_2019_07_21_Madlow_rusty_water_pipe.png", "t02-01_flickr_Plumbing.jpg", "t02-02_flickr_Rusty_Old_Pipe_And_Spigot.jpg"]},
    "03": {"topic": "Sewer", "images": ["t03-01_wikimedia_Plumbers_snake_24695.jpg"]},
    "04": {"topic": "Water Heaters", "images": ["t04-01_Rheem_home_gas_water_heater_tank_Dial.jpg", "t04-02_21kW_400Volts_3phase_tankless_water_heater_20100201_1144_1.jpg"]},
    "05": {"topic": "Drains", "images": ["t05-02_Electric_Drain_Cleaner.png", "t05-03_Handheld_Drain_Auger.png"]},
    "06": {"topic": "Leaks", "images": ["t06-01_Water_damage.jpg", "t06-02_Ceiling_water_damage.jpg"]},
    "07": {"topic": "Water Heaters", "images": ["t07-01_Hard_Water_Calcification.jpg", "t07-02_Limescale_deposit_cooking_pot.jpg"]},
    "08": {"topic": "Gas Lines", "images": ["t08-01_Gas_installation_in_Sibulak_la.jpg", "t08-02_20190918_192129_Gas_meter_in_Lodz_Poland_2019.jpg"]},
    "09": {"topic": "Repipes", "images": ["t09-02_Pipe_Relining_Service.jpg", "t09-01_Cured_in_place_pipe_lining_inflation_in_Cambridge_Massachuse.jp.jpg"]},
    "10": {"topic": "Drains", "images": ["t10-02_flickr_Cleaning_out_the_Grease_Trap_1.jpg", "t10-01_Grease_trap_for_greywater_5293658840.jpg", "t10-03_flickr_Cleaning_out_the_Grease_Trap_5.jpg"]},
    "11": {"topic": "Emergencies", "images": ["t11-02_wikimedia_Leaking_PVC_Pipe_Under_Sink_P_Trap_52842.jpg", "t11-01_Water_Pipe_Shutoff_Valve_54273678839.jpg"]},
    "12": {"topic": "Water Heaters", "images": ["t12-02_flickr_superhot_water_heater_burner.jpg", "t12-01_Burner_assembly_of_a_water_heater.jpg"]},
    "13": {"topic": "Sewer", "images": ["t13-01_Search_Camera_With_Image.png"]},
    "14": {"topic": "Code &amp; Permits", "images": ["t14-03_2006_02_15_Piping.jpg", "t14-02_05_06_13_plumbing_2_8716084472.jpg"]},
    "15": {"topic": "Hiring a Plumber", "images": ["t15-02_flickr_Sink_repair_by_female_plumber.jpg", "t15-01_Cameroon_male_plumbier_at_work_05.jpg"]},
}

ICON_ARROW = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


# ---------------------------------------------------------------- parsing
def parse_front_matter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        v = v.strip()
        meta[k.strip()] = json.loads(v) if v[:1] in '["' else v
    return meta, text[m.end():]


def image_file(name):
    """Published file name: t01-01_Trenchless_Sewer_Repair.png -> t01-01-trenchless-sewer-repair.jpg"""
    stem = re.sub(r"(\.jp)?\.(jpe?g|png)$", "", name, flags=re.I)
    return re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-") + ".jpg"


def parse_provenance(path):
    out = {}
    for block in re.split(r"\n## ", path.read_text())[1:]:
        name, _, body = block.partition("\n")
        f = dict(re.findall(r"- \*\*(.+?):\*\* (.*)", body))
        lic_m = re.match(r"(.*?)\s*\((https?://[^)]*)\)", f.get("License", ""))
        lic, lic_url = (lic_m.group(1), lic_m.group(2)) if lic_m else (f.get("License", ""), "")
        if lic.startswith("BY"):
            lic = "CC " + lic
        attr = f.get("Attribution string", "")
        a = re.match(r'".*?" by (.+?) is licensed under', attr) or re.match(r"(.+?) \u2014 ", attr)
        author = re.sub(r"^User:", "", a.group(1)).strip() if a else ""
        library = "Flickr" if "flickr" in f.get("Library", "").lower() else "Wikimedia Commons"
        out[name.strip()] = {"alt": f["Subject / alt text"].strip(), "source": f.get("Source page", "").strip(),
                             "license": lic, "license_url": lic_url, "author": author, "library": library}
    return out


def load_posts():
    posts = []
    for d in sorted(SRC.iterdir()):
        if not d.is_dir():
            continue
        num, slug = d.name.split("-", 1)
        meta, body = parse_front_matter((d / "post.md").read_text())
        body = body.strip()
        h1 = re.match(r"# (.+)\n", body)
        if not h1 or h1.group(1) != meta["h1"]:
            raise ValueError(f"{d.name}: body H1 must match front matter h1")
        prov = parse_provenance(d / "images-provenance.md")
        cfg = POSTS[num]
        images = []
        for name in cfg["images"]:
            if name not in prov:
                raise ValueError(f"{d.name}: {name} has no provenance entry")
            images.append({**prov[name], "src": f"/assets/images/blog/{slug}/{image_file(name)}",
                           "card": f"/assets/images/blog/{slug}/{image_file(name)[:-4]}-card.jpg", "orig": name})
        words = len(re.sub(r"[#*\[\]()]", " ", body).split())
        posts.append({"num": num, "slug": slug, "meta": meta, "body": body[h1.end():].strip(),
                      "topic": cfg["topic"], "images": images, "date": cfg.get("date", PUBLISHED),
                      "minutes": max(1, round(words / 225)), "url": f"/blog/{slug}/"})
    return posts


# ---------------------------------------------------------------- inline markdown
def smart_quotes(s):
    s = re.sub(r'(^|[\s(\[*\u2014])"', "\\1\u201c", s)
    s = s.replace('"', "\u201d")
    return s.replace("'", "\u2019")


def inline(s):
    s = smart_quotes(s)
    parts = re.split(r"(\[[^\]]+\]\([^)]+\))", s)
    out = []
    for part in parts:
        link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", part)
        if link:
            out.append(f'<a href="{html.escape(link.group(2))}">{inline_text(link.group(1))}</a>')
        else:
            out.append(inline_text(part))
    return "".join(out)


def inline_text(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = s.replace(PHONE, f'<a href="tel:{TEL}">{PHONE}</a>')
    return s


def heading_id(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def figure(img, lead=False):
    cls = "post-figure post-figure-lead" if lead else "post-figure"
    return f"""<figure class="{cls}">
  <img src="{img['src']}" alt="{html.escape(img['alt'])}" loading="{'eager' if lead else 'lazy'}" decoding="async">
  <figcaption>{html.escape(img['alt'])}.</figcaption>
</figure>"""


# ---------------------------------------------------------------- body
def render_body(post):
    """Returns (lede_html, sections_html, faqs, cta, toc)."""
    blocks = [b.strip() for b in post["body"].split("\n\n") if b.strip()]
    lede = blocks.pop(0)
    if lede.startswith("#"):
        raise ValueError(f"{post['slug']}: post must open with an intro paragraph")

    sections = []   # [(heading, [html blocks])]
    faqs, cta = [], None
    mode = "body"
    for b in blocks:
        if b.startswith("## "):
            title = b[3:].strip()
            if "\n" in title:
                raise ValueError(f"{post['slug']}: heading followed by text without a blank line: {title[:40]}")
            if title.lower() == "frequently asked questions":
                mode = "faq"
            elif mode == "faq":
                mode, cta = "cta", {"title": title, "paras": []}
            else:
                sections.append((title, []))
            continue
        if mode == "faq":
            q = re.fullmatch(r"\*\*(.+?)\*\*\n(.+)", b, re.S)
            if not q:
                raise ValueError(f"{post['slug']}: malformed FAQ block: {b[:60]}")
            faqs.append((q.group(1).strip(), " ".join(q.group(2).split())))
        elif mode == "cta":
            cta["paras"].append(b)
        else:
            if not sections:
                raise ValueError(f"{post['slug']}: text between the intro and the first heading")
            sections[-1][1].append(render_block(b, post["slug"]))
    if not faqs or not cta:
        raise ValueError(f"{post['slug']}: needs a FAQ section and a closing call-to-action section")

    # Lead image under the intro; the rest spread evenly across the section ends.
    extra = post["images"][1:]
    slots = {}
    for i, img in enumerate(extra):
        slots.setdefault(max(0, round((i + 1) * len(sections) / (len(extra) + 1)) - 1), []).append(img)

    out = []
    for i, (title, parts) in enumerate(sections):
        hid = heading_id(title)
        out.append(f'<h2 id="{hid}">{inline(title)}</h2>')
        out.extend(parts)
        out.extend(figure(img) for img in slots.get(i, []))
    toc = [(heading_id(t), inline(t)) for t, _ in sections] + [("faq", "Frequently Asked Questions")]
    return inline(lede), "\n".join(out), faqs, cta, toc


def render_block(b, slug):
    if b.startswith("### "):
        return f"<h3>{inline(b[4:])}</h3>"
    lines = b.split("\n")
    if all(l.startswith("- ") for l in lines):
        return "<ul>\n" + "\n".join(f"  <li>{inline(l[2:])}</li>" for l in lines) + "\n</ul>"
    if b.startswith(("#", "- ", "* ", "> ", "|", "```")) or re.match(r"\d+\. ", b):
        raise ValueError(f"{slug}: unsupported Markdown block: {b[:60]}")
    return f"<p>{inline(' '.join(lines))}</p>"


# ---------------------------------------------------------------- shell
def head(title, description, canonical, og_image, og_type="website", jsonld=()):
    parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{html.escape(BIZ)}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{DOMAIN}{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/logos/viper-logo-transparent.png">
<link rel="stylesheet" href="/css/styles.css?v={ASSET_V}">
<link rel="stylesheet" href="/css/blog.css?v={BLOG_CSS_V}">"""]
    for block in jsonld:
        parts.append('<script type="application/ld+json">\n' + json.dumps(block, indent=2) + "\n</script>")
    parts.append("</head>")
    return "\n".join(parts)


def header():
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
        <li><a href="/blog/" aria-current="page">Blog</a></li>
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
      <a href="/blog/">Blog</a>
      <a href="/#reviews">Reviews</a>
      <a href="/contact.html">Contact</a>
    </nav>

    <nav class="footer-nav">
      <span class="footer-heading">Services</span>
      <a href="/services.html">Sewer Liners</a>
      <a href="/services.html">Water &amp; Gas Repipes</a>
      <a href="/services.html">Water Heaters &amp; Tankless</a>
      <a href="/services.html">Drain Cleaning &amp; Hydro Jetting</a>
    </nav>

    <div class="footer-contact">
      <span class="footer-heading">Contact</span>
      <a href="tel:{TEL}">{PHONE}</a>
      <span>1840 W Lincoln Ave, Anaheim, CA 92804</span>
      <span>Mon&ndash;Sun, 24 Hours</span>
    </div>
  </div>

  <div class="container footer-bottom">
    <span>&copy; <span id="footer-year">2026</span> Viper Rooter &amp; Plumbing. Contractor License #{LICENSE}.</span>
  </div>
</footer>

<script src="/js/app.js?v={ASSET_V}"></script>
</body>
</html>
"""


def nice_date(iso):
    import datetime
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


def card(post, heading="h2"):
    img = post["images"][0]
    return f"""<article class="post-card reveal" data-topic="{html.escape(html.unescape(post['topic']))}">
  <a class="post-card-link" href="{post['url']}">
    <div class="post-card-media"><img src="{img['card']}" alt="{html.escape(img['alt'])}" loading="lazy" decoding="async"></div>
    <div class="post-card-body">
      <span class="post-tag">{post['topic']}</span>
      <{heading} class="post-card-title">{inline(post['meta']['h1'])}</{heading}>
      <p>{inline(post['meta']['meta_description'])}</p>
      <span class="post-card-more">{post['minutes']} min read {ICON_ARROW}</span>
    </div>
  </a>
</article>"""


def publisher():
    return {"@type": "Organization", "name": BIZ, "url": DOMAIN + "/",
            "logo": {"@type": "ImageObject", "url": DOMAIN + "/assets/logos/viper-logo.png"}}


# ---------------------------------------------------------------- pages
def render_post(post, posts):
    m = post["meta"]
    canonical = DOMAIN + post["url"]
    lede, body, faqs, cta, toc = render_body(post)
    title = html.escape(m["title_tag"], quote=False)
    desc = html.escape(m["meta_description"])

    ld_article = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": m["h1"],
                  "description": m["meta_description"], "image": [DOMAIN + i["src"] for i in post["images"]],
                  "datePublished": post["date"], "dateModified": post["date"],
                  "author": {"@type": "Organization", "name": BIZ, "url": DOMAIN + "/"},
                  "publisher": publisher(), "mainEntityOfPage": canonical,
                  "keywords": ", ".join([m["primary_keyword"]] + m.get("secondary_keywords", [])),
                  "about": {**business_schema(), "url": DOMAIN + "/"}}
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    ld_crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": DOMAIN + "/blog/"},
        {"@type": "ListItem", "position": 3, "name": m["h1"], "item": canonical}]}

    same = [p for p in posts if p is not post and p["topic"] == post["topic"]]
    rest = sorted((p for p in posts if p is not post and p not in same),
                  key=lambda p: abs(int(p["num"]) - int(post["num"])))
    related = (same + rest)[:3]

    toc_html = "\n".join(f'          <li><a href="#{hid}">{label}</a></li>' for hid, label in toc)
    faq_html = "\n".join(f"""      <details class="faq-item">
        <summary>{inline(q)}</summary>
        <p>{inline(a)}</p>
      </details>""" for q, a in faqs)
    cta_paras = "\n".join(f"      <p>{inline(p)}</p>" for p in cta["paras"])
    credits = "\n".join(credit(i) for i in post["images"])

    return "\n".join([
        head(title, desc, canonical, post["images"][0]["src"], "article", [ld_article, ld_faq, ld_crumbs]),
        "<body class=\"blog-page\">\n",
        header(),
        f"""
<main id="main">

  <section class="post-hero">
    <div class="container">
      <nav class="breadcrumbs" aria-label="Breadcrumb">
        <a href="/">Home</a><span aria-hidden="true">/</span><a href="/blog/">Blog</a><span aria-hidden="true">/</span><span>{post['topic']}</span>
      </nav>
      <span class="post-tag">{post['topic']}</span>
      <h1>{inline(m['h1'])}</h1>
      <div class="post-meta">
        <span>By {html.escape(BIZ)}</span>
        <span class="post-meta-dot" aria-hidden="true">&middot;</span>
        <time datetime="{post['date']}">{nice_date(post['date'])}</time>
        <span class="post-meta-dot" aria-hidden="true">&middot;</span>
        <span>{post['minutes']} min read</span>
      </div>
    </div>
  </section>

  <div class="container post-layout">
    <article class="post-body">
      <p class="post-lede">{lede}</p>
{figure(post['images'][0], lead=True)}
{body}

      <section class="post-faq" id="faq">
        <h2>Frequently Asked Questions</h2>
{faq_html}
      </section>

      <section class="post-cta">
        <h2>{inline(cta['title'])}</h2>
{cta_paras}
        <div class="post-cta-actions">
          <a class="btn btn-primary btn-large" href="tel:{TEL}">{ICON_PHONE} {CALL}</a>
          <a class="btn btn-ghost btn-large" href="/contact.html">Request a Free Quote</a>
        </div>
      </section>

      <section class="post-credits">
        <h2>Photo credits</h2>
        <ul>
{credits}
        </ul>
      </section>
    </article>

    <aside class="post-aside">
      <div class="aside-card aside-toc">
        <span class="aside-heading">In this article</span>
        <ol>
{toc_html}
        </ol>
      </div>
      <div class="aside-card aside-offer">
        <span class="aside-heading">Drain Cleaning Special</span>
        <p class="aside-price">$89</p>
        <p>From a proper clean-out access, plus a free camera scope.</p>
        <a class="btn btn-primary btn-block" href="tel:{TEL}">{ICON_PHONE} {CALL}</a>
        <ul class="aside-checks">
          <li>{ICON_CHECK} Open 24/7, Mon&ndash;Sun</li>
          <li>{ICON_CHECK} Licensed &amp; Insured, Lic #{LICENSE}</li>
          <li>{ICON_CHECK} Family owned in Anaheim</li>
        </ul>
      </div>
    </aside>
  </div>

  <section class="related">
    <div class="container">
      <h2 class="related-heading">Keep Reading</h2>
      <div class="post-grid">
{chr(10).join(card(p, 'h3') for p in related)}
      </div>
    </div>
  </section>

</main>
""",
        footer(),
    ])


def credit(img):
    who = html.escape(img["author"]) if img["author"] else "Unknown author"
    lic = html.escape(img["license"])
    if img["license_url"]:
        lic = f'<a href="{html.escape(img["license_url"])}" rel="noopener license" target="_blank">{lic}</a>'
    src = f'<a href="{html.escape(img["source"])}" rel="noopener" target="_blank">{img["library"]}</a>'
    return f"          <li>{html.escape(img['alt'])}: photo by {who}, {lic}, via {src}.</li>"


def render_index(posts):
    canonical = DOMAIN + "/blog/"
    title = "Plumbing Guides &amp; Tips | Viper Rooter &amp; Plumbing Blog"
    desc = ("Straight answers from a family-owned Anaheim plumber on sewer lines, repipes, water heaters, "
            "drains, gas lines, and plumbing code for Orange County homes.")
    topics = []
    for p in posts:
        if p["topic"] not in topics:
            topics.append(p["topic"])
    chips = "\n".join(f'        <button class="topic-chip" type="button" data-topic="{html.escape(html.unescape(t))}" aria-pressed="false">{t}</button>'
                      for t in topics)
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": f"{BIZ} Blog", "url": canonical,
          "description": desc, "publisher": publisher(),
          "blogPost": [{"@type": "BlogPosting", "headline": p["meta"]["h1"], "url": DOMAIN + p["url"],
                        "datePublished": p["date"], "image": DOMAIN + p["images"][0]["src"]} for p in posts]}
    return "\n".join([
        head(title, html.escape(desc), canonical, "/assets/images/page-heroes/services-hero.jpg", jsonld=[ld]),
        "<body class=\"blog-page\">\n",
        header(),
        f"""
<main id="main">

  <section class="page-hero">
    <div class="page-hero-media"><img src="/assets/images/page-heroes/services-hero.jpg" alt=""></div>
    <div class="container">
      <h1 class="reveal">Plumbing Guides</h1>
      <p class="reveal">Straight answers from a family-owned Anaheim plumber. What is actually wrong, what fixes it, and when the cheaper fix is the right one.</p>
    </div>
  </section>

  <section class="blog-index">
    <div class="container">
      <div class="topic-filter" role="group" aria-label="Filter by topic">
        <button class="topic-chip" type="button" data-topic="all" aria-pressed="true">All topics</button>
{chips}
      </div>
      <div class="post-grid" id="post-grid">
{chr(10).join(card(p) for p in posts)}
      </div>
    </div>
  </section>

  <section class="promo">
    <div class="container promo-inner">
      <div class="promo-text">
        <h2>$89 Drain Cleaning Special</h2>
        <p>From a proper clean-out access, plus a free camera scope with your service.</p>
      </div>
      <a class="btn btn-invert btn-large" href="tel:{TEL}">{CALL}</a>
    </div>
  </section>

</main>

<script>
  (function () {{
    var chips = document.querySelectorAll('.topic-chip');
    var cards = document.querySelectorAll('#post-grid .post-card');
    chips.forEach(function (chip) {{
      chip.addEventListener('click', function () {{
        var t = chip.getAttribute('data-topic');
        chips.forEach(function (c) {{ c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); }});
        cards.forEach(function (card) {{
          var show = t === 'all' || card.getAttribute('data-topic') === t;
          card.hidden = !show;
          if (show) card.classList.add('is-visible');
        }});
      }});
    }});
  }})();
</script>
""",
        footer(),
    ])


# ---------------------------------------------------------------- images
def process_images(pkg, posts):
    from PIL import Image, ImageOps
    Image.MAX_IMAGE_PIXELS = None
    for post in posts:
        folder = next(Path(pkg).glob(f"blog-{post['num']}-*"))
        dest = IMG_DIR / post["slug"]
        dest.mkdir(parents=True, exist_ok=True)
        for img in post["images"]:
            im = ImageOps.exif_transpose(Image.open(folder / img["orig"]))
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                bg = Image.new("RGB", im.size, (0, 16, 41))
                bg.paste(im, mask=im.split()[-1])
                im = bg
            im = im.convert("RGB")
            full = im.copy()
            full.thumbnail((1400, 1400), Image.LANCZOS)
            full.save(ROOT / img["src"].lstrip("/"), "JPEG", quality=76, optimize=True, progressive=True)
            thumb = ImageOps.fit(im, (720, 450), Image.LANCZOS, centering=(0.5, 0.45))
            thumb.save(ROOT / img["card"].lstrip("/"), "JPEG", quality=78, optimize=True, progressive=True)
        print("images", post["slug"], len(post["images"]))


def main():
    posts = load_posts()
    if "--images" in sys.argv:
        process_images(sys.argv[sys.argv.index("--images") + 1], posts)
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(render_index(posts))
    print("wrote blog/index.html")
    for post in posts:
        out = OUT / post["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(render_post(post, posts))
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
