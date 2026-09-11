# Viper Plumbing — Project Notes

Site build for Viper Rooter & Plumbing (viperrooterandplumbing.com), family-owned, serving a 20-mile radius of Anaheim, CA. See `references/onboarding-info/` for the full client brief (services, pricing, service area, brand contacts).

Design direction: dark, near-black theme with brand blue (#0042aa) as the single glowing accent, gray (#919191) as secondary text. Saira Condensed for headlines/labels/numbers, Inter for body copy. Full-bleed stock video used in the hero and service-area sections (Span-style rhythm), inspired by the reference sites in `references/website-references/`.

## Git workflow — standing authorization

The user has authorized automatic git management for this repo. Unless told otherwise for a specific change:

- After making a meaningful set of file changes, stage, commit, and push to `origin main` without asking for confirmation each time.
- Still follow standard git hygiene: review `git status`/`git diff` before staging, write a clear commit message describing the "why," never force-push, never skip hooks, never amend existing commits (always create new ones).
- Still pause and ask before anything destructive or hard-to-reverse (history rewrites, branch deletion, resetting shared history) — auto-push of normal forward commits is in scope; those are not.
- If a commit touches something that looks like it could contain secrets/credentials, stop and flag it instead of pushing.
- Commit only the files relevant to the task just completed — don't sweep up unrelated untracked/modified files sitting in the working tree.
