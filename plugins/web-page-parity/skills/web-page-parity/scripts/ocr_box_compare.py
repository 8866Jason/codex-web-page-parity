#!/usr/bin/env python3
"""Compare OCR word boxes in matching reference/live screenshot crops."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


def parse_crop(value: str) -> tuple[int, int, int, int]:
    parts = [int(part.strip()) for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("Use x,y,w,h")
    x, y, w, h = parts
    return x, y, x + w, y + h


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--live", required=True, type=Path)
    parser.add_argument("--crop", required=True, type=parse_crop, help="Crop as x,y,w,h in source image pixels.")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--psm", default="6")
    return parser.parse_args()


def run_tesseract(image_path: Path, psm: str) -> list[dict[str, object]]:
    if not shutil.which("tesseract"):
        raise SystemExit("tesseract is not installed or not in PATH")
    output = subprocess.check_output(["tesseract", str(image_path), "stdout", "--psm", psm, "tsv"], text=True, stderr=subprocess.DEVNULL)
    rows: list[dict[str, object]] = []
    reader = csv.DictReader(output.splitlines(), delimiter="\t")
    for row in reader:
        text = (row.get("text") or "").strip()
        if not text:
            continue
        try:
            conf = float(row.get("conf") or "-1")
            left = int(row.get("left") or "0")
            top = int(row.get("top") or "0")
            width = int(row.get("width") or "0")
            height = int(row.get("height") or "0")
        except ValueError:
            continue
        if conf < 0:
            continue
        rows.append({"text": text, "conf": conf, "left": left, "top": top, "width": width, "height": height})
    return rows


def annotate(image_path: Path, boxes: list[dict[str, object]], out_path: Path) -> None:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    for box in boxes:
        left = int(box["left"])
        top = int(box["top"])
        right = left + int(box["width"])
        bottom = top + int(box["height"])
        draw.rectangle((left, top, right, bottom), outline=(255, 0, 0), width=2)
    image.save(out_path, optimize=True)


def summarize(boxes: list[dict[str, object]]) -> dict[str, object]:
    heights = [int(box["height"]) for box in boxes]
    tops = [int(box["top"]) for box in boxes]
    return {
        "wordCount": len(boxes),
        "medianHeight": sorted(heights)[len(heights) // 2] if heights else None,
        "minTop": min(tops) if tops else None,
        "maxBottom": max((int(box["top"]) + int(box["height"]) for box in boxes), default=None),
    }


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp_text:
        tmp = Path(tmp_text)
        crops: dict[str, Path] = {}
        for label, source in (("reference", args.reference), ("live", args.live)):
            crop_path = tmp / f"{label}.png"
            Image.open(source).convert("RGB").crop(args.crop).save(crop_path)
            crops[label] = crop_path
        ref_boxes = run_tesseract(crops["reference"], args.psm)
        live_boxes = run_tesseract(crops["live"], args.psm)
        ref_annotated = args.out / f"{args.name}-reference-ocr.png"
        live_annotated = args.out / f"{args.name}-live-ocr.png"
        annotate(crops["reference"], ref_boxes, ref_annotated)
        annotate(crops["live"], live_boxes, live_annotated)
        data = {
            "reference": {"summary": summarize(ref_boxes), "boxes": ref_boxes, "annotated": str(ref_annotated)},
            "live": {"summary": summarize(live_boxes), "boxes": live_boxes, "annotated": str(live_annotated)},
        }
        out_json = args.out / f"{args.name}-ocr-boxes.json"
        out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"json": str(out_json), **data}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

