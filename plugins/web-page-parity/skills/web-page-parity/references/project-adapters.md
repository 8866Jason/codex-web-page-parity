# Project Adapters

Use this reference only when a project has an asset/data pipeline or a known parity pattern. Keep the main skill generic.

## Generic Project Checklist

- Find project instructions first: `AGENTS.md`, `CLAUDE.md`, README, framework config, package scripts, theme docs.
- Identify how assets reach the browser: static public folder, bundler import, CMS field, generated JSON, database option, CDN, or optimized media map.
- Check cache layers: browser cache, framework build cache, CMS cache, reverse proxy, CDN, service worker.
- Prefer a route/component-scoped patch before touching global typography, grid, or header/footer rules.
- When a project has approved pages, compare typography, color, button, and component treatment against those pages as the local CI/CIS baseline.
- Validate the smallest relevant unit first: syntax/lint/build, then browser screenshot and console checks.

## WordPress/DDEV Adapter

- Prefer DDEV commands when the project already uses DDEV.
- Read PHP templates/render helpers before editing CSS.
- Validate PHP with `php -l` and project-specific validators.
- Run `ddev wp cache flush` after theme/data/media changes.
- For generated data/media, update the builder script first, regenerate outputs second, and verify the browser `currentSrc`.

## Generated Assets Adapter

- Identify the source of truth before editing: design exports, CMS fields, generated JSON, media maps, or static assets.
- Update the builder or authored data first, then regenerate derived outputs.
- Verify rendered browser URLs with `currentSrc` or network inspection rather than trusting source file names.
- When a project has approved pages, use them as the local baseline for typography, buttons, footer/header treatment, and brand colors.
- For pixel-critical banners, icons, or logos, prefer lossless or passthrough assets when compression changes visible parity.
- Match the canonical mockup viewport first, then scale widths, gaps, padding, and typography between breakpoint edges rather than keeping fixed wide-desktop values.

## Stateful Page Adapter

- Capture each supplied state separately instead of inferring behavior from the default screenshot.
- Prevent hash-link or sticky-header scroll drift after click actions when the reference expects the page from `y=0`.
- When typography changes alter page height, preserve the proven text size and compensate with spacing rather than shrinking text back down.
- Full-page parity includes footer geometry and repeated components, not only the main content band.
- Regenerate a separate side-by-side report for each state after every CSS or JS change.

## CMS/Data Pipeline Adapter

- Find where content is authored: CMS fields, JSON, database options, markdown, or remote content services.
- Identify cache layers: browser cache, object cache, build cache, CDN, reverse proxy, and service workers.
- When content or images differ from the reference, verify both the authored data and the rendered browser output.
- Keep builder scripts idempotent and versioned when they regenerate assets or structured data.

Final report shape:

- Summarize what changed.
- Link exact files and line numbers.
- List validations run.
- Include screenshot/diff artifact paths when useful.
- Note cache/hard-reload or browser zoom caveats.
