# Pixel Parity Playbook

Use this reference for demanding visual parity tasks where the user expects the live page to match a PDF/PNG/Figma/screenshot mockup exactly.

## 1. Build The Reference-State Matrix

List every visual state before editing:

- Default/collapsed page.
- User-provided alternate states such as toggle-down, modal open, tab selected, hover card, mobile menu open, form success, filtered category.
- Browser-comment viewport state, including the actual viewport dimensions in the comment.
- Breakpoint edge states, especially where the user reports Chrome/side-browser differences.

For each state, record:

- Reference path and dimensions.
- Live URL and state action, such as click selector or URL hash.
- Target viewport and device scale factor.
- Expected page height, section start rows, footer start row, and key component boxes.

## 2. Prepare References

- Prefer exact PNG/Figma exports when supplied.
- Convert PDF pages to PNG at the same pixel dimensions as the intended mockup when no PNG exists.
- Do not compare a scaled screenshot against a full-size mockup without noting the scale.
- If the reference includes browser chrome or an annotation overlay, crop it out before parity comparison.

## 3. Capture Live Evidence

Capture the live page in this order:

1. Current in-app browser or browser-comment viewport.
2. Canonical desktop mockup viewport, usually `1920x1080`.
3. Breakpoint edges, such as `1181px` and `1180px`.
4. Tablet and mobile references when provided.
5. Every state in the reference-state matrix.

Use deterministic screenshots. Avoid relying on what is visible in a scrolled browser tab unless the task is specifically about that viewport.

## 4. Compare In Layers

Use side-by-side screenshots as the primary review artifact. Inspect in this order:

1. Header height, logo size, nav positions, active/current states.
2. Hero image source, crop, overlay, title position, and section end row.
3. Main layout x/y/w/h, columns, gaps, sidebar width, content width.
4. Typography tiers: heading, sidebar, card title, body, metadata, footer.
5. Component states: accordion open/closed, selected tab, hover/open menus.
6. Footer row, column positions, thumbnails, link sizes, and recent-post content.
7. Color, borders, shadows, image compression, and fine antialiasing differences.

Treat a matching page height as necessary but not sufficient. A page can have the right height while text is visibly too small or content is vertically compensated by padding.

## 5. Typography Parity Rules

- Compare computed CSS first, then verify optical size with side-by-side screenshots.
- When text looks wrong, crop the same reference/live region and run OCR word-box comparison.
- Match word-box heights and line y-positions before adjusting surrounding padding.
- If larger text changes page height, preserve the proven text size and compensate with margin/padding/section gaps.
- Verify font loading and fallback fonts; identical CSS with a missing webfont can still look wrong.

## 6. Stateful Component Rules

- Do not infer state behavior from the default screenshot.
- Capture and compare each supplied state separately.
- When a reference state hides other groups or filters content, implement that state explicitly rather than only opening a native element.
- Re-check scroll position after click actions. Hash links and sticky headers can move the page and produce a false mismatch.

## 7. Asset Pipeline Rules

- Find how the project maps source assets to browser URLs.
- Update builder scripts or CMS data first, generated outputs second.
- Verify `currentSrc` in the browser.
- Use passthrough PNG/SVG for pixel-critical banners/icons if WebP compression changes the visual.
- Remove hardcoded fallback assets when source folders provide the required desktop/tablet/mobile variants.

## 8. Scoped CSS Rules

- Prefer route/page/component scopes such as `body.route-name .component`.
- Keep approved home/product/global systems untouched unless the user asks for shared-system changes.
- Match the exact reference viewport directly; then use responsive formulas for in-between widths.
- Avoid global typography changes to fix one page.

## 9. Acceptance Checklist

Before final response:

- All supplied mockup states have side-by-side reports.
- Reference/live image dimensions match or the remaining size delta is explained.
- Section start rows and footer rows match the reference.
- User-commented regions have been directly inspected after the fix.
- Typography has been checked at computed-style and visual/OCR levels when requested.
- Project syntax/build/data checks and cache flushes have run.
- Final answer links to the report artifacts and validation commands.

