# Viper Plumbing

Marketing site for Viper Rooter & Plumbing (viperrooterandplumbing.com) — a family-owned plumbing company serving a 20-mile radius around Anaheim, CA.

## Status

Homepage built: pure HTML/CSS/JS, no build step. Other pages (about, services, contact as standalone pages) are not started yet — nav currently links to in-page anchors.

## Structure

- `index.html` / `css/styles.css` / `js/app.js` — the homepage
- `assets/logos/viper-logo.png` — primary logo, as provided by client (opaque white background)
- `assets/logos/viper-logo-transparent.png` — background-removed version, used across the site
- `assets/fonts/saira-condensed/` — Saira Condensed family (headlines/labels/numbers), self-hosted
- `assets/fonts/inter/` — Inter variable font (body copy), self-hosted
- `assets/content/stock/` — raw stock video clips (gitignored, local only — see below)
- `assets/content/video/web/` — trimmed/compressed clips actually used on the page, plus poster frames
- `assets/content/photo/` — placeholder for future client-provided photos
- `references/onboarding-info/` — full client brief: services, pricing, service area, brand contacts
- `references/website-references/` — reference sites for style/layout direction
- `CLAUDE.md` — working agreement for this repo (git workflow, etc.)

## Design

Dark, near-black theme with brand blue (#0042aa) as the single glowing accent and gray (#919191) as secondary text — modeled on Linear / Stella Petkova / Span's video rhythm rather than a typical trade-site layout. Saira Condensed carries headlines, labels, and numbers; Inter handles body copy. Full-bleed stock video anchors the hero and service-area sections.

## Notes

- Brand colors: `#0042aa`, `#919191`
- No client-provided photos/videos yet — homepage uses stock media only until real content is available
- `assets/content/stock/` is gitignored: the raw clips include files over GitHub's 100MB push limit, and none of it is web-optimized. Only trimmed/compressed clips actually used on a page are committed, under `assets/content/video/web/`.
- Contact form is a working prototype (not yet wired to a live inbox/CRM)
