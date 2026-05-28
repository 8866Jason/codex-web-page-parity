#!/usr/bin/env python3
"""Capture web page screenshots, DOM metrics, and optional PNG diffs."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


DEFAULT_VIEWPORTS = (
    "desktop1920:1920x1080",
    "side1449:1449x1079",
    "narrow1280:1280x900",
    "desktop-edge1181:1181x900",
    "tablet-edge1180:1180x900",
    "mobile390:390x844:mobile",
)


def parse_viewport(value: str) -> dict[str, object]:
    parts = value.split(":")
    if len(parts) not in {2, 3}:
        raise argparse.ArgumentTypeError("Use name:WIDTHxHEIGHT or name:WIDTHxHEIGHT:mobile")
    name, size = parts[0], parts[1]
    width_text, height_text = size.lower().split("x", 1)
    return {
        "name": name,
        "width": int(width_text),
        "height": int(height_text),
        "isMobile": len(parts) == 3 and parts[2] == "mobile",
    }


def run_playwright(
    url: str,
    out_dir: Path,
    viewports: list[dict[str, object]],
    *,
    include_console_logs: bool = False,
    include_text_content: bool = False,
) -> dict[str, object]:
    script = r"""
const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
let chromium;
try {
  chromium = createRequire(path.join(process.cwd(), 'package.json'))('playwright').chromium;
} catch (error) {
  chromium = require('playwright').chromium;
}

const url = process.argv[2];
const outDir = process.argv[3];
const viewports = JSON.parse(process.argv[4]);
const options = JSON.parse(process.argv[5]);

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const results = {};
  for (const vp of viewports) {
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      deviceScaleFactor: 1,
      isMobile: Boolean(vp.isMobile),
      ignoreHTTPSErrors: true,
    });
    const page = await context.newPage();
    const logs = [];
    if (options.includeConsoleLogs) {
      page.on('console', msg => logs.push({ type: msg.type(), text: msg.text() }));
    }
    await page.goto(url, { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(outDir, `${vp.name}-top.png`), fullPage: false });
    await page.screenshot({ path: path.join(outDir, `${vp.name}-full.png`), fullPage: true });
    const metrics = await page.evaluate((options) => {
      const rect = selector => {
        const node = document.querySelector(selector);
        if (!node) return null;
        const r = node.getBoundingClientRect();
        return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) };
      };
      const style = selector => {
        const node = document.querySelector(selector);
        if (!node) return null;
        const s = getComputedStyle(node);
        return {
          fontSize: s.fontSize,
          fontWeight: s.fontWeight,
          lineHeight: s.lineHeight,
          marginTop: s.marginTop,
          marginBottom: s.marginBottom,
          gap: s.gap,
          gridTemplateColumns: s.gridTemplateColumns,
          color: s.color,
          background: s.backgroundColor,
        };
      };
      const visualStyle = node => {
        const s = getComputedStyle(node);
        const r = node.getBoundingClientRect();
        const result = {
          selector: node.tagName.toLowerCase() + (node.id ? `#${node.id}` : '') + (node.className && typeof node.className === 'string' ? `.${node.className.trim().replace(/\s+/g, '.')}` : ''),
          rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) },
          fontFamily: s.fontFamily,
          fontSize: s.fontSize,
          fontWeight: s.fontWeight,
          lineHeight: s.lineHeight,
          letterSpacing: s.letterSpacing,
          textTransform: s.textTransform,
          textAlign: s.textAlign,
          color: s.color,
          backgroundColor: s.backgroundColor,
          borderColor: s.borderColor,
          borderRadius: s.borderRadius,
          boxShadow: s.boxShadow,
          opacity: s.opacity,
          display: s.display,
          gap: s.gap,
          padding: s.padding,
          margin: s.margin,
        };
        if (options.includeTextContent) {
          result.text = (node.innerText || node.getAttribute('aria-label') || node.getAttribute('alt') || '').trim().replace(/\s+/g, ' ').slice(0, 120);
        }
        return result;
      };
      const collectVisualTokens = selector => Array.from(document.querySelectorAll(selector)).slice(0, 20).map(visualStyle);
      const heroImg = document.querySelector('[data-hero] picture img, .hero picture img, .center-hero picture img, .page-hero picture img, .products-hero img, main img, img');
      return {
        viewport: { width: innerWidth, height: innerHeight, dpr: devicePixelRatio },
        media: {
          max1180: matchMedia('(max-width: 1180px)').matches,
          max720: matchMedia('(max-width: 720px)').matches,
        },
        documentWidth: document.documentElement.scrollWidth,
        bodyScrollHeight: document.documentElement.scrollHeight,
        header: rect('header, [role="banner"], .site-header'),
        hero: rect('[data-hero], .hero, .center-hero, .page-hero, .products-hero, main section:first-of-type'),
        heroTitle: rect('[data-hero] h1, .hero h1, .center-hero h1, .page-hero h1, .products-hero h1, main h1, h1'),
        layout: rect('main, [role="main"], .page, .content, .contact-layout, .news-index, .products-shell'),
        footer: rect('footer, [role="contentinfo"], .site-footer'),
        heroTitleStyle: style('[data-hero] h1, .hero h1, .center-hero h1, .page-hero h1, .products-hero h1, main h1, h1'),
        h2Style: style('h2'),
        buttonStyle: style('button, .btn'),
        visualTokens: {
          text: collectVisualTokens('h1, h2, h3, h4, p, li, label, small, figcaption'),
          links: collectVisualTokens('a'),
          controls: collectVisualTokens('button, .btn, input, textarea, select, [role="button"]'),
          media: collectVisualTokens('img, svg, picture, video'),
          landmarks: collectVisualTokens('header, nav, main, section, footer'),
        },
        heroImgSrc: heroImg ? heroImg.currentSrc || heroImg.src : null,
      };
    }, options);
    results[vp.name] = {
      ...metrics,
      captureOptions: {
        includeConsoleLogs: Boolean(options.includeConsoleLogs),
        includeTextContent: Boolean(options.includeTextContent),
      },
    };
    if (options.includeConsoleLogs) {
      results[vp.name].logs = logs;
    }
    await context.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(outDir, 'metrics.json'), JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
})();
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as handle:
        handle.write(script)
        node_script = Path(handle.name)
    try:
        completed = subprocess.run(
            [
                "node",
                str(node_script),
                url,
                str(out_dir),
                json.dumps(viewports),
                json.dumps(
                    {
                        "includeConsoleLogs": include_console_logs,
                        "includeTextContent": include_text_content,
                    }
                ),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
    finally:
        node_script.unlink(missing_ok=True)
    return json.loads(completed.stdout)


def diff_reference(reference: Path, live: Path, out_dir: Path) -> dict[str, object]:
    from PIL import Image, ImageChops, ImageStat

    ref = Image.open(reference).convert("RGB")
    img = Image.open(live).convert("RGB")
    original_sizes = {"reference": ref.size, "live": img.size}
    if ref.size != img.size:
        width = min(ref.width, img.width)
        height = min(ref.height, img.height)
        ref = ref.crop((0, 0, width, height))
        img = img.crop((0, 0, width, height))
    diff = ImageChops.difference(ref, img)
    stat = ImageStat.Stat(diff)
    data = diff.get_flattened_data() if hasattr(diff, "get_flattened_data") else diff.getdata()
    pixels = list(data)
    total = len(pixels)
    summary: dict[str, object] = {
        "sizes": original_sizes,
        "comparedSize": diff.size,
        "meanAbsDiff": sum(stat.mean) / 3,
        "maxDiff": max(max(pixel) for pixel in pixels) if pixels else 0,
    }
    for threshold in (10, 20, 28, 40):
        count = sum(1 for pixel in pixels if max(pixel) > threshold)
        summary[f"pixelsGt{threshold}"] = {"count": count, "ratio": count / total if total else 0}

    heat = Image.new("RGB", diff.size, "white")
    heat_px = heat.load()
    diff_px = diff.load()
    for y in range(diff.height):
        for x in range(diff.width):
            value = max(diff_px[x, y])
            heat_px[x, y] = (255, 0, 0) if value > 28 else ((255, 210, 0) if value > 10 else (255, 255, 255))
    heat_path = out_dir / "desktop1920-diff-heat.png"
    heat.save(heat_path)

    scale = 0.25
    thumbs = [image.resize((int(image.width * scale), int(image.height * scale))) for image in (ref, img, heat)]
    triptych = Image.new("RGB", (thumbs[0].width * 3, thumbs[0].height), "white")
    for index, thumb in enumerate(thumbs):
        triptych.paste(thumb, (index * thumb.width, 0))
    triptych_path = out_dir / "desktop1920-ref-live-heat-triptych.png"
    triptych.save(triptych_path)
    summary["heatPath"] = str(heat_path)
    summary["triptychPath"] = str(triptych_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--viewport", action="append", type=parse_viewport)
    parser.add_argument("--include-console-logs", action="store_true")
    parser.add_argument("--include-text-content", action="store_true")
    args = parser.parse_args()

    viewports = args.viewport or [parse_viewport(value) for value in DEFAULT_VIEWPORTS]
    args.out.mkdir(parents=True, exist_ok=True)
    results = run_playwright(
        args.url,
        args.out,
        viewports,
        include_console_logs=args.include_console_logs,
        include_text_content=args.include_text_content,
    )
    if args.reference:
        live = args.out / "desktop1920-full.png"
        if live.exists():
            results["desktop1920Diff"] = diff_reference(args.reference, live, args.out)
            (args.out / "diff-summary.json").write_text(
                json.dumps(results["desktop1920Diff"], indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    (args.out / "summary.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote parity artifacts to {args.out}")


if __name__ == "__main__":
    main()
