# Visual Audit Checklist

Use this checklist when the request asks for complete PDF/PNG/Figma/screenshot parity, especially typography, color, UI/UX, CI, or CIS.

## Typography

- Compare `font-family`, source font files, fallback stack, and loaded webfont status.
- Compare `font-size`, `font-weight`, `line-height`, `letter-spacing`, `text-transform`, text alignment, and paragraph width.
- Check every text tier: navigation, hero title, subtitle, section heading, card heading, body copy, labels, helper text, button text, metadata, footer text, legal text.
- Compare optical weight, not just CSS weight. Browser font synthesis, missing font files, antialiasing, and different fallback fonts can make identical CSS look wrong.
- Verify long words and multilingual text do not overflow or wrap differently from the reference.

## Color And Brand Tokens

- Compare foreground/background colors as rendered RGB values, not only CSS variables.
- Check brand colors, neutral palette, hover/focus colors, disabled colors, border colors, dividers, shadows, overlays, gradients, and image tinting.
- Sample colors from the reference and live screenshots when CSS values do not explain a visual mismatch.
- Confirm `opacity`, `mix-blend-mode`, filters, and overlays do not alter brand colors unexpectedly.

## Layout And Spacing

- Compare page width, section heights, transition rows, grid columns, gaps, padding, margins, aspect ratios, and scroll height.
- Check stable dimensions for cards, forms, buttons, icons, media frames, counters, tabs, and toolbars.
- Inspect desktop target, side-browser width, breakpoint edges, tablet, and mobile.
- Check no horizontal overflow, text overlap, collapsed margins, or unexpected layout shift.

## Imagery And Icons

- Compare image source path, rendered dimensions, intrinsic size, object-fit, crop position, compression, color profile, and alpha.
- Use exact PNG/SVG passthrough for pixel-critical reference assets when compression changes the visual.
- Confirm icon stroke width, fill, corner radius, size, alignment, color, and hover/focus state.

## UI States

- Check default, hover, focus-visible, active, disabled, selected/current, error, success, loading, and empty states when the component supports them.
- For forms, verify required markers, validation messages, input height, border radius, focus ring, textarea resize handle, submit success/error copy, and email/notification behavior.
- For navigation, verify current page state, dropdown/menu state, mobile drawer, search, and keyboard focus order.

## UX And Accessibility

- Preserve expected workflows and click paths from the design/PPTX/spec.
- Ensure responsive behavior keeps content readable and actions reachable without zooming.
- Check focus visibility, keyboard navigation, semantic landmarks, labels, alt text, contrast, and pointer target sizes.
- Do not sacrifice usability to force a single static screenshot; if a reference conflicts with accessibility or responsive ergonomics, report the tradeoff and choose the smallest defensible implementation.

## CI/CIS Brand System

- Treat CI/CIS as the complete identity system: logo usage, clear space, brand color roles, typography hierarchy, icon family, photo treatment, shape language, CTA hierarchy, tone of microcopy, and repeated component behavior.
- Compare new pages against already-approved pages in the same project before inventing new styles.
- Keep completed approved pages untouched unless the user explicitly asks to update the shared system.

## Evidence To Capture

- Fixed viewport screenshots and full-page screenshots.
- Left/right side-by-side reference/live screenshots for every supplied mockup state.
- DOM geometry for major sections and components.
- Computed styles for representative text tiers and components.
- OCR word boxes or annotated crops when typography size/weight is disputed.
- Browser `currentSrc` for all critical images.
- Pixel diff summary and heatmap when a reference PNG exists.
- Console logs and network/image loading errors.
