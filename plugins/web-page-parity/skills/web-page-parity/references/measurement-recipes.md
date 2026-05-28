# Measurement Recipes

Use these recipes when visual parity needs concrete measurements beyond a basic screenshot diff.

## Section And Footer Rows

Detect likely white/content/footer transitions with Pillow by scanning rows for dominant colors. Use this to compare reference/live starts such as hero end, content start, and footer start.

```python
from PIL import Image

im = Image.open("screenshot.png").convert("RGB")
for name, pred in [
    ("white", lambda r, g, b: r > 245 and g > 245 and b > 245),
    ("dark", lambda r, g, b: r < 25 and g < 25 and b < 25),
]:
    rows = []
    step = max(1, im.width // 300)
    for y in range(im.height):
        hits = total = 0
        for x in range(0, im.width, step):
            total += 1
            if pred(*im.getpixel((x, y))):
                hits += 1
        if hits / total > 0.8:
            rows.append(y)
    print(name, rows[0] if rows else None, rows[-1] if rows else None)
```

## Component Border Rows

To compare repeated cards or accordion rows, scan a content x-range for long non-white horizontal lines.

```python
from PIL import Image

im = Image.open("screenshot.png").convert("RGB")
rows = []
for y in range(950, min(im.height, 5600)):
    count = 0
    for x in range(560, 1850):
        r, g, b = im.getpixel((x, y))
        if not (r > 248 and g > 248 and b > 248):
            count += 1
    if count > 900:
        rows.append(y)
print(rows[:20], rows[-20:])
```

## Typography OCR Boxes

Use OCR when text appears visually too small/large even if the overall page height matches.

```bash
tesseract crop.png stdout --psm 6 tsv \
  | awk -F '\t' 'NR>1 && $12 != "" && $11 > 30 {print $7,$8,$9,$10,$11,$12}'
```

Compare word-box heights (`$10`), y-positions (`$8`), and confidence (`$11`). OCR is a measurement aid, not the sole truth; inspect the side-by-side crop too.

## Computed Style Snapshot

Use Playwright to capture rects and computed text styles:

```js
const pick = (selector) => {
  const el = document.querySelector(selector);
  const r = el.getBoundingClientRect();
  const s = getComputedStyle(el);
  return {
    text: el.textContent.trim().slice(0, 120),
    rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) },
    fontSize: s.fontSize,
    fontWeight: s.fontWeight,
    lineHeight: s.lineHeight,
    letterSpacing: s.letterSpacing,
    color: s.color,
    padding: s.padding,
    margin: s.margin,
  };
};
```

## Image Source And Crop

For each critical image, capture:

- `currentSrc`
- `naturalWidth` / `naturalHeight`
- rendered `getBoundingClientRect()`
- `object-fit` and `object-position`
- whether the served file is compressed or resized

## Browser Comment Viewports

When a browser comment marks an element, use the comment viewport dimensions as a target in addition to the canonical mockup viewport. A layout can be correct at `1920px` and wrong at side-browser widths such as `1440px`.

