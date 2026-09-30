#!/usr/bin/env python3
"""Pre-push audit of the generated blog. Run after build_blog.py; exits non-zero on any error.

    python3 _build/audit_blog.py

Errors: leftover Markdown or template placeholders in visible text, dashes in article copy,
straight quotes, research/brief notes leaking into copy, wrong phone or license number,
broken local links or images, missing alt text, bad head tags or JSON-LD, repeated sentences.
Warnings: title/description length, image weight.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PHONE = "(657) 637-8529"
ALLOWED_NUMBERS = {PHONE, "800-321-2752"}   # Viper, CSLB
LICENSE = "1022901"

MARKDOWN = [(r"\*\*|__", "bold markers"), (r"(^|\n)\s*#{1,6}\s", "heading hashes"), (r"\]\(", "link syntax"),
            (r"`", "backtick"), (r"(^|\n)\s*[-*>|]\s", "list/quote/table marker"), (r"\[[^\]]*\]", "square brackets")]
PLACEHOLDERS = r"IMAGE SLOT|\bplacement:|suggested alt|\bTODO\b|\bTBD\b|lorem|\bXXX\b|\{\{|\}\}|\bpending\b|\bINSERT\b"
NOTES_LEAK = (r"\bpersona\b|primary keyword|word count|we looked|corroborat|secondary sources|"
              r"sourcing|stand behind|content-gated|ChatGPT|\bAI\b|Jonathan|Fenn|Openverse|"
              r"we do not claim|we describe Viper")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.text, self.article, self.imgs, self.links = [], [], [], [], []
        self.h1 = 0
        self.title = self.desc = None
        self.jsonld, self._ld = [], None
        self._title = False
        self._skip = 0
        self._in_article = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self._skip += 1
            if a.get("type") == "application/ld+json":
                self._ld = []
        if tag == "title":
            self._title = True
        if tag == "h1":
            self.h1 += 1
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content", "")
        if tag == "img":
            self.imgs.append(a)
        if tag in ("a", "link") and a.get("href"):
            self.links.append(a["href"])
        if tag == "script" and a.get("src"):
            self.links.append(a["src"])
        if tag == "article" and "post-body" in a.get("class", ""):
            self._in_article = 1
        elif self._in_article and tag not in ("img", "br", "meta", "link", "input"):
            self._in_article += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1
            if self._ld is not None:
                self.jsonld.append("".join(self._ld))
                self._ld = None
        if tag == "title":
            self._title = False
        if self._in_article and tag not in ("img", "br", "meta", "link", "input"):
            self._in_article -= 1

    def handle_data(self, data):
        if self._ld is not None:
            self._ld.append(data)
        if self._title:
            self.title = (self.title or "") + data
        if self._skip:
            return
        self.text.append(data)
        if self._in_article:
            self.article.append(data)


def audit(path):
    errors, warns = [], []
    p = Page()
    p.feed(path.read_text())
    text = " ".join(" ".join(p.text).split())
    body = "\n".join(p.article)
    body_flat = " ".join(body.split())
    is_post = path.parent.name != "blog"

    for pat, label in MARKDOWN:
        for m in re.finditer(pat, body if is_post else text):
            errors.append(f"markdown residue ({label}): …{(body if is_post else text)[max(0, m.start()-30):m.end()+30]!r}…")
    for m in re.finditer(PLACEHOLDERS, text, re.I):
        errors.append(f"placeholder text: …{text[max(0, m.start()-40):m.end()+40]}…")
    for m in re.finditer(NOTES_LEAK, text):
        errors.append(f"internal note leaked into copy: …{text[max(0, m.start()-50):m.end()+50]}…")
    if is_post:
        for m in re.finditer("[–—]", body_flat):
            errors.append(f"dash in article copy: …{body_flat[max(0, m.start()-30):m.end()+30]}…")
        for m in re.finditer("[\"']", body_flat):
            errors.append(f"straight quote in article copy: …{body_flat[max(0, m.start()-30):m.end()+30]}…")
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body_flat) if len(s.split()) >= 8]
        seen = set()
        for s in sentences:
            if s in seen:
                errors.append(f"repeated sentence: {s[:90]}")
            seen.add(s)
        n_imgs = sum(1 for i in p.imgs if "/assets/images/blog/" in i.get("src", "") and "-card" not in i["src"])
        n_credits = len(re.findall(r": photo by ", body_flat))
        if n_imgs == 0:
            errors.append("post has no images")
        if n_imgs != n_credits:
            errors.append(f"{n_imgs} article images but {n_credits} photo credits")

    for num in re.findall(r"\(?\b\d{3}\)?[ .-]\d{3}-\d{4}\b", text):
        if num not in ALLOWED_NUMBERS:
            errors.append(f"unexpected phone number: {num}")
    for lic in re.findall(r"(?:LIC|Lic|License|license)(?: number)? #?\s?(\d{5,})", text):
        if lic != LICENSE:
            errors.append(f"unexpected license number: {lic}")

    if p.h1 != 1:
        errors.append(f"{p.h1} <h1> tags (want 1)")
    title = (p.title or "").strip()
    if not title:
        errors.append("missing <title>")
    elif len(title) > 60:
        warns.append(f"title is {len(title)} chars (>60 may truncate): {title}")
    if not p.desc:
        errors.append("missing meta description")
    elif not 70 <= len(p.desc) <= 160:
        warns.append(f"meta description is {len(p.desc)} chars (aim 70-160)")
    for block in p.jsonld:
        try:
            json.loads(block)
        except ValueError as e:
            errors.append(f"invalid JSON-LD: {e}")

    for img in p.imgs:
        if img.get("alt") is None:
            errors.append(f"img missing alt: {img.get('src')}")
        elif not img["alt"].strip() and "page-hero" not in path.read_text() and "/blog/" in img.get("src", ""):
            errors.append(f"blog image with empty alt: {img.get('src')}")
        check_local(img.get("src", ""), errors)
        f = local_file(img.get("src", ""))
        if f and f.exists() and f.stat().st_size > 450_000 and "/blog/" in img["src"]:
            warns.append(f"heavy image {f.stat().st_size // 1024} KB: {img['src']}")
    for href in p.links:
        check_local(href, errors)
    return errors, warns


def local_file(url):
    u = urlparse(url)
    if u.scheme or u.netloc or not u.path.startswith("/"):
        return None
    f = ROOT / u.path.lstrip("/")
    return f / "index.html" if u.path.endswith("/") else f


def check_local(url, errors):
    if url.startswith(("tel:", "mailto:", "#", "http")) or not url:
        return
    f = local_file(url)
    if f is None:
        errors.append(f"relative link (use root-relative): {url}")
    elif not f.exists() and not Path(str(f) + ".html").exists():
        errors.append(f"broken local link: {url}")


def main():
    pages = [ROOT / "blog" / "index.html"] + sorted((ROOT / "blog").glob("*/index.html"))
    total_e = total_w = 0
    for page in pages:
        errors, warns = audit(page)
        total_e += len(errors)
        total_w += len(warns)
        status = "FAIL" if errors else ("warn" if warns else "ok")
        print(f"[{status:4}] {page.relative_to(ROOT)}")
        for e in errors:
            print("       ERROR", e)
        for w in warns:
            print("       warn ", w)
    print(f"\n{len(pages)} pages, {total_e} errors, {total_w} warnings")
    sys.exit(1 if total_e else 0)


if __name__ == "__main__":
    main()
