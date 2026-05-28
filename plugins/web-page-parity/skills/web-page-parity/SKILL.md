---
name: web-page-parity
description: Use when matching any website or app page to a PDF, PNG, screenshot, Figma export, or browser comment; when the user says "完全一致", "對齊", "排版對照", "示意圖", "pixel-perfect", "same as mockup", "actual screenshot comparison", "左右並排比對", "screenshot diff", "breakpoint issue", "UI UX", "CI", "CIS", or reports typography, font size, weight, color, spacing, image, brand, or responsive layout mismatch.
---

# Web Page Parity

Use this skill to turn visual-reference requests into a repeatable inspect, compare, edit, and verify loop across any frontend project. Treat the current browser page, local design files, screenshots, and source code as evidence.

## Operating Standard

- Treat "完全一致" as a measurable target, not a rough visual direction.
- Produce human-reviewable side-by-side screenshots for every relevant page state before claiming parity.
- Use numbers to guide edits, but use the side-by-side image to decide whether the page still looks wrong.
- Do not stop at a single full-page diff. Inspect the regions the user points at: sidebar, text blocks, card bodies, footer, hero crop, toggles, and breakpoint-specific layouts.
- Keep fixes scoped to the page/route/component unless the approved design system itself needs to change.

## Workflow

1. Establish the target:
   - Identify the live URL or local file route.
   - Locate the reference PDF/PNG/screenshot/Figma export and any asset/source folders.
   - Read project instructions such as `AGENTS.md`, `CLAUDE.md`, package scripts, theme docs, or page-specific notes.
   - Build a reference-state matrix when more than one mockup exists. Example: `collapsed`, `toggle-down`, `mobile-menu-open`, `hover-card`, `form-success`.

2. Inspect before editing:
   - Use the in-app Browser when the user says it is already open.
   - Use Chrome/Playwright for fixed viewport screenshots, DOM geometry, computed styles, image `currentSrc`, media query state, and console logs.
   - Check desktop target width, side-browser width, breakpoint edge widths, and mobile.
   - Compare section transition rows, total scroll height, key element rects, font family/size/weight/line-height/letter-spacing, text transform, colors, image sources, border radius, shadows, opacity, and overflow.
   - When a stateful component is in the reference, capture each visual state separately. Examples: collapsed accordion, toggle-down accordion, hover/open drawer, active tab, filtered category, modal open, mobile nav open.
   - When the user asks for full UI/UX/CI/CIS parity, read `references/visual-audit-checklist.md`.
   - For complex or repeated parity work, read `references/parity-playbook.md`.

3. Generate actual screenshot comparison artifacts before and after edits:
   - Convert PDFs to PNGs when needed, or use the supplied PNG/Figma export directly.
   - Capture the live page at the same reference viewport, usually `1920x1080` for full desktop mockups, plus the user's side-browser viewport when they comment in the browser.
   - Produce a visual review image with the reference on the left and the live screenshot on the right. Use the `side_by_side_report.py` script below for a repeatable report.
   - Also keep the heatmap/diff output from `page_parity_capture.py`, but do not rely on the number alone. Use the side-by-side image to inspect human-visible mismatches: text size, line height, column width, image crop, empty space, footer position, and state-specific content.
   - If the user says text looks too small or too large, crop the relevant reference/live regions and compare OCR word boxes or pixel text boxes. `tesseract ... tsv` is useful when installed; computed CSS alone can be misleading after image/report scaling.
   - If a user comments in the browser, capture the same viewport dimensions as the comment before fixing, then also verify the canonical mockup viewport.

4. Map source assets correctly:
   - Prefer the project's current asset pipeline over hardcoded one-off URLs.
   - Verify generated URLs in the browser, not just source paths.
   - For pixel-critical artwork, avoid unnecessary image compression/resizing. Add a narrow passthrough or high-quality export only for the affected assets.

5. Make scoped changes:
   - Preserve unrelated completed pages/components.
   - Use route/page/component scoped selectors, feature flags, or local styles rather than broad global changes.
   - At the exact reference viewport, match the mockup dimensions directly.
   - Between breakpoints, scale columns, gaps, padding, and typography with `clamp()`, `min()`, grid/flex constraints, or container units instead of keeping fixed wide-desktop values.
   - Keep brand tokens consistent: logo treatment, brand colors, typography scale, button shapes, icon style, imagery treatment, and repeated component states must match the reference system.
   - Iterate in this order when a full page is off: section start/end rows, main column geometry, typography/OCR boxes, component state dimensions, footer/header, then fine color/image differences.
   - After increasing typography, re-check total page height and footer `y`; compensate with margins/padding instead of shrinking the text back down when the reference proves the text size.

6. Verify and report:
   - Run the project's cheapest syntax/build/data checks.
   - Clear local app/cache layers when the stack needs it.
   - Re-capture screenshots and metrics after edits.
   - Regenerate the side-by-side report for every supplied reference state.
   - Report exact reference/live image sizes, footer or section `y` positions, state counts, and mean diff only as supporting evidence.
   - Include exact file links, validation commands, and screenshot/diff artifact paths in the final answer.
   - If any reference-visible mismatch remains, state it plainly and keep iterating unless the user explicitly pauses.

## Tools

- Use Browser plugin first for an already-open local page.
- Use Playwright or Chrome automation for deterministic viewport screenshots.
- Use `rg`, `find`, `sed`, `nl`, app build scripts, formatters, linters, and syntax checks.
- Use image tooling such as PIL/Pillow for PNG diffs, section bands, side-by-side reports, and heatmaps.
- Use OCR tooling such as `tesseract ... tsv` only when typography size/weight looks wrong or computed CSS does not explain the visual mismatch.
- Use AppleScript only for coarse Chrome tab/window discovery; Chrome JavaScript execution through AppleScript may be disabled.

## Scripts

Resolve `scripts/...` relative to this skill directory. If you are running the tools manually from a shell, either `cd` into the skill directory first or expand the relative path to the installed skill location.

The capture scripts default to privacy-preserving mode: they do not collect browser console logs or sampled text snippets unless you explicitly opt in with `--include-console-logs` or `--include-text-content`.

Run the bundled script from any project root that has Node, Chrome, Playwright, and Pillow available:

```bash
python3 scripts/page_parity_capture.py \
  --url https://example.local/page/ \
  --reference /absolute/path/to/reference.png \
  --out /tmp/page-parity
```

The script writes:

- `*-top.png` and `*-full.png` screenshots for multiple viewports.
- `metrics.json` and `summary.json` with DOM geometry, computed styles, and sampled visual tokens.
- `diff-summary.json`, `desktop1920-diff-heat.png`, and `desktop1920-ref-live-heat-triptych.png` when a reference PNG is supplied.

Capture a stateful page after clicks or other simple interactions:

```bash
python3 scripts/capture_page_state.py \
  --url https://example.local/page/ \
  --out /tmp/page-state \
  --name toggle-down \
  --viewport 1920x1080 \
  --click '.faq-sidebar a[href="#faq-company-information"]' \
  --reference /absolute/path/to/toggle-reference.png
```

The state capture script writes `NAME-top.png`, `NAME-full.png`, `NAME-metrics.json`, and when `--reference` is supplied also writes side-by-side/diff artifacts.

Use this script whenever the user wants to review parity visually, or when a browser comment says something "looks" wrong. It creates the review format used in repeatable parity work: left = `REFERENCE PDF/PNG`, right = `LIVE SCREENSHOT`, plus a red heatmap and an HTML report.

```bash
python3 scripts/side_by_side_report.py \
  --reference /absolute/path/to/reference.png \
  --live /tmp/page-parity/desktop1920-full.png \
  --out /absolute/path/to/parity-report \
  --name page-state
```

For stateful pages, run it once per state:

```bash
python3 scripts/side_by_side_report.py \
  --reference "/absolute/path/FAQ 示意圖.png" \
  --live /tmp/faq-collapsed/desktop1920-full.png \
  --out /absolute/path/parity-reports/faq \
  --name faq-collapsed

python3 scripts/side_by_side_report.py \
  --reference "/absolute/path/FAQ toggle down 示意圖.png" \
  --live /tmp/faq-toggle/toggle1920-full.png \
  --out /absolute/path/parity-reports/faq \
  --name faq-toggle-down
```

Use the generated `*-reference-vs-live.png` as the primary review artifact with the user. Use `*-diff-heat.png` to find small residual mismatches after the human-visible layout is close.

Compare typography boxes with OCR when visual size is disputed:

```bash
python3 scripts/ocr_box_compare.py \
  --reference /absolute/path/reference.png \
  --live /absolute/path/live.png \
  --crop 500,1000,1300,500 \
  --out /tmp/ocr-compare \
  --name faq-content
```

Use the JSON and annotated images to compare word box heights, line positions, and whether text is optically smaller/larger even when layout height matches.

## Detailed References

Read `references/visual-audit-checklist.md` when the request includes typography, color, UI/UX, brand, CI, or CIS parity.
Read `references/parity-playbook.md` when the task requires full-page exactness, multiple mockup states, browser comments, or repeated iteration.
Read `references/measurement-recipes.md` when you need OCR typography checks, row/section detection, footer/header alignment, or image crop/color diagnostics.
Read `references/project-adapters.md` only when the project uses WordPress, DDEV, CMS data, generated assets, or other framework-specific pipelines.
