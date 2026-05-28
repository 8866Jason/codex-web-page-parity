#!/usr/bin/env python3
"""Create reference-vs-live screenshot review artifacts for visual parity work."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


def load_font(path: str, size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path, help="Reference PNG/JPG screenshot path.")
    parser.add_argument("--live", required=True, type=Path, help="Live screenshot PNG/JPG path.")
    parser.add_argument("--out", required=True, type=Path, help="Output directory.")
    parser.add_argument("--name", required=True, help="Artifact name prefix, e.g. faq-collapsed.")
    parser.add_argument("--reference-label", default="REFERENCE PDF/PNG")
    parser.add_argument("--live-label", default="LIVE SCREENSHOT")
    parser.add_argument("--title", default="Web page parity report")
    return parser.parse_args()


def diff_stats(reference: Image.Image, live: Image.Image) -> tuple[dict[str, object], Image.Image]:
    width = min(reference.width, live.width)
    height = min(reference.height, live.height)
    diff = ImageChops.difference(reference.crop((0, 0, width, height)), live.crop((0, 0, width, height)))
    stat = ImageStat.Stat(diff)
    mean_abs_diff = sum(stat.mean) / 3
    pixels = diff.load()
    thresholds: dict[str, object] = {}
    total = width * height
    for threshold in (10, 20, 28, 40):
        count = 0
        for y in range(height):
            for x in range(width):
                if max(pixels[x, y]) > threshold:
                    count += 1
        thresholds[f"pixelsGt{threshold}"] = {"count": count, "ratio": count / total if total else 0}
    stats = {
        "sizes": {"reference": reference.size, "live": live.size},
        "comparedSize": (width, height),
        "meanAbsDiff": mean_abs_diff,
        **thresholds,
    }
    heat = diff.convert("L").point(lambda value: min(255, value * 4))
    heat_rgb = Image.merge("RGB", (heat, Image.new("L", heat.size), Image.new("L", heat.size)))
    return stats, heat_rgb


def make_side_by_side(
    reference: Image.Image,
    live: Image.Image,
    reference_name: str,
    live_name: str,
    reference_label: str,
    live_label: str,
) -> Image.Image:
    width = max(reference.width, live.width)
    height = max(reference.height, live.height)
    label_height = 96
    gap = 16
    ref_canvas = Image.new("RGB", (width, height), "white")
    live_canvas = Image.new("RGB", (width, height), "white")
    ref_canvas.paste(reference, (0, 0))
    live_canvas.paste(live, (0, 0))

    canvas = Image.new("RGB", (width * 2 + gap, height + label_height), (245, 245, 245))
    draw = ImageDraw.Draw(canvas)
    font_big = load_font("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 38)
    font_small = load_font("/System/Library/Fonts/Supplemental/Arial.ttf", 24)
    draw.rectangle((0, 0, width, label_height), fill=(20, 20, 20))
    draw.rectangle((width + gap, 0, width * 2 + gap, label_height), fill=(20, 20, 20))
    draw.text((32, 22), reference_label, fill=(255, 255, 255), font=font_big)
    draw.text((width + gap + 32, 22), live_label, fill=(255, 255, 255), font=font_big)
    draw.text((32, 62), reference_name, fill=(210, 210, 210), font=font_small)
    draw.text((width + gap + 32, 62), live_name, fill=(210, 210, 210), font=font_small)
    canvas.paste(ref_canvas, (0, label_height))
    canvas.paste(live_canvas, (width + gap, label_height))
    return canvas


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    reference = Image.open(args.reference).convert("RGB")
    live = Image.open(args.live).convert("RGB")

    side_by_side = make_side_by_side(
        reference,
        live,
        args.reference.name,
        args.live.name,
        args.reference_label,
        args.live_label,
    )
    side_path = args.out / f"{args.name}-reference-vs-live.png"
    side_by_side.save(side_path, optimize=True)

    stats, heat = diff_stats(reference, live)
    heat_path = args.out / f"{args.name}-diff-heat.png"
    heat.save(heat_path, optimize=True)

    stats_path = args.out / f"{args.name}-diff-summary.json"
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    index_path = args.out / "index.html"
    existing = ""
    if index_path.exists():
        existing = index_path.read_text(encoding="utf-8")
    section = (
        f"<section><h2>{html.escape(args.name)}</h2>"
        f"<p>reference {stats['sizes']['reference']} / live {stats['sizes']['live']} / "
        f"meanAbsDiff <code>{stats['meanAbsDiff']:.4f}</code></p>"
        f'<img src="{html.escape(side_path.name)}" alt="{html.escape(args.name)} side by side">'
        f"<h3>Diff heat</h3>"
        f'<img src="{html.escape(heat_path.name)}" alt="{html.escape(args.name)} diff heat"></section>'
    )
    if "<body>" in existing:
        html_text = existing.replace("</body>", section + "\n</body>")
    else:
        html_text = (
            '<!doctype html><meta charset="utf-8">'
            f"<title>{html.escape(args.title)}</title>"
            "<style>body{font-family:Inter,Arial,sans-serif;margin:24px;background:#f5f5f5;color:#111}"
            "img{width:100%;height:auto;border:1px solid #ddd;background:white}"
            "section{margin:0 0 48px}code{background:#eee;padding:2px 6px}</style>"
            f"<body><h1>{html.escape(args.title)}</h1>{section}\n</body>"
        )
    index_path.write_text(html_text, encoding="utf-8")

    print(json.dumps({"sideBySide": str(side_path), "heat": str(heat_path), "summary": str(stats_path), "report": str(index_path), **stats}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
