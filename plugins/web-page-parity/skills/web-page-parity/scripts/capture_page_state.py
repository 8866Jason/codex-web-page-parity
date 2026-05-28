#!/usr/bin/env python3
"""Capture a live page state after simple Playwright actions."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_viewport(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", 1)
        return int(width_text), int(height_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use WIDTHxHEIGHT, e.g. 1920x1080") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--viewport", default="1920x1080", type=parse_viewport)
    parser.add_argument("--click", action="append", default=[], help="CSS selector to click. Can be repeated.")
    parser.add_argument("--wait", type=int, default=700, help="Wait after load and each action in milliseconds.")
    parser.add_argument("--reference", type=Path, help="Optional reference image for side-by-side report.")
    parser.add_argument("--measure", action="append", default=[], help="Extra CSS selector to measure. Can be repeated.")
    parser.add_argument("--include-console-logs", action="store_true")
    parser.add_argument("--include-text-content", action="store_true")
    return parser.parse_args()


def run_capture(args: argparse.Namespace) -> dict[str, object]:
    args.out.mkdir(parents=True, exist_ok=True)
    width, height = args.viewport
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

const config = JSON.parse(process.argv[2]);

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({
    viewport: { width: config.width, height: config.height },
    deviceScaleFactor: 1,
    ignoreHTTPSErrors: true,
  });
  const logs = [];
  if (config.includeConsoleLogs) {
    page.on('console', msg => logs.push({ type: msg.type(), text: msg.text() }));
  }
  await page.goto(config.url, { waitUntil: 'load', timeout: 60000 });
  await page.waitForTimeout(config.wait);
  for (const selector of config.clicks) {
    await page.click(selector, { timeout: 15000 });
    await page.waitForTimeout(config.wait);
  }
  await page.screenshot({ path: path.join(config.out, `${config.name}-top.png`), fullPage: false });
  await page.screenshot({ path: path.join(config.out, `${config.name}-full.png`), fullPage: true });
  const metrics = await page.evaluate(({ extraSelectors, includeTextContent }) => {
    const rect = (selector) => {
      const node = document.querySelector(selector);
      if (!node) return null;
      const r = node.getBoundingClientRect();
      return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) };
    };
    const style = (selector) => {
      const node = document.querySelector(selector);
      if (!node) return null;
      const r = node.getBoundingClientRect();
      const s = getComputedStyle(node);
      const result = {
        rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) },
        fontSize: s.fontSize,
        fontWeight: s.fontWeight,
        lineHeight: s.lineHeight,
        letterSpacing: s.letterSpacing,
        textTransform: s.textTransform,
        color: s.color,
        backgroundColor: s.backgroundColor,
        padding: s.padding,
        margin: s.margin,
      };
      if (includeTextContent) {
        result.text = node.textContent.trim().slice(0, 160);
      }
      return result;
    };
    const measured = {};
    for (const selector of extraSelectors) {
      measured[selector] = style(selector);
    }
    return {
      url: location.href,
      viewport: { width: innerWidth, height: innerHeight, dpr: devicePixelRatio },
      documentWidth: document.documentElement.scrollWidth,
      bodyScrollHeight: document.body.scrollHeight,
      header: rect('header, .site-header'),
      main: rect('main, #content'),
      hero: rect('.hero, .page-hero, .center-hero, [class*="hero"]'),
      footer: rect('footer, .site-footer'),
      measured,
    };
  }, {
    extraSelectors: config.measure,
    includeTextContent: Boolean(config.includeTextContent),
  });
  metrics.captureOptions = {
    includeConsoleLogs: Boolean(config.includeConsoleLogs),
    includeTextContent: Boolean(config.includeTextContent),
  };
  if (config.includeConsoleLogs) {
    metrics.logs = logs;
  }
  fs.writeFileSync(path.join(config.out, `${config.name}-metrics.json`), JSON.stringify(metrics, null, 2));
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exit(1);
});
"""
    config = {
        "url": args.url,
        "out": str(args.out),
        "name": args.name,
        "width": width,
        "height": height,
        "clicks": args.click,
        "wait": args.wait,
        "measure": args.measure,
        "includeConsoleLogs": args.include_console_logs,
        "includeTextContent": args.include_text_content,
    }
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as handle:
        handle.write(script)
        script_path = Path(handle.name)
    try:
        subprocess.run(["node", str(script_path), json.dumps(config)], check=True)
    finally:
        script_path.unlink(missing_ok=True)
    metrics_path = args.out / f"{args.name}-metrics.json"
    return json.loads(metrics_path.read_text(encoding="utf-8"))


def main() -> None:
    args = parse_args()
    metrics = run_capture(args)
    full_path = args.out / f"{args.name}-full.png"
    result: dict[str, object] = {
        "full": str(full_path),
        "top": str(args.out / f"{args.name}-top.png"),
        "metrics": str(args.out / f"{args.name}-metrics.json"),
        "bodyScrollHeight": metrics.get("bodyScrollHeight"),
        "footer": metrics.get("footer"),
        "captureOptions": metrics.get("captureOptions"),
    }
    if args.reference:
        side_script = ROOT / "scripts" / "side_by_side_report.py"
        subprocess.run(
            [
                sys.executable,
                str(side_script),
                "--reference",
                str(args.reference),
                "--live",
                str(full_path),
                "--out",
                str(args.out),
                "--name",
                args.name,
            ],
            check=True,
        )
        result["report"] = str(args.out / "index.html")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

