# Viper Plumbing

Marketing site for Viper Rooter & Plumbing (viperrooterandplumbing.com) — a family-owned plumbing company serving a 20-mile radius around Anaheim, CA.

## Status

Not started yet. Repo currently holds only brand assets and client reference material; no HTML pages exist.

## Structure

- `assets/logos/viper-logo.png` — primary logo
- `assets/fonts/saira-condensed/` — Saira Condensed family, self-hosted
- `assets/content/stock/` — raw stock video clips (gitignored, local only — see below)
- `assets/content/photo/`, `assets/content/video/` — placeholders for future client-provided media
- `references/onboarding-info/` — full client brief: services, pricing, service area, brand contacts
- `references/website-references/` — reference sites for style/layout direction

## Notes

- Brand colors: `#0042aa`, `#919191`
- No client-provided photos/videos yet — homepage will use stock media only until real content is available
- `assets/content/stock/` is gitignored: the raw clips include files over GitHub's 100MB push limit, and none of it is web-optimized. Only trimmed/compressed clips actually used on a page should be committed, under something like `assets/content/video/web/`.
