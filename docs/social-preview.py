#!/usr/bin/env python3
"""Compose the repository's social preview (1280x640, GitHub's recommended size) and README banner.

  python docs/social-preview.py --hero docs/hero.png --out docs/social-preview.png

The hero is an illustration with its subject on the right half; this script fits it
to 1280x640, darkens it, fades the left half to the background color for legibility,
and sets the title, tagline, and a mono meta line in Inter and JetBrains Mono. The
two fonts are downloaded from Google Fonts into a temp folder on first run.
Requires Pillow.
"""

from __future__ import annotations

import argparse
import tempfile
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 640
BG = (14, 17, 22)
FG = (245, 246, 248)
MUTED = (168, 175, 188)
DIM = (120, 128, 142)
ACCENT = (217, 119, 87)
MARGIN = 72

FONTS = {
    "Inter.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    "JetBrainsMono.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
}


def font_dir() -> Path:
    d = Path(tempfile.gettempdir()) / "model-grade-fonts"
    d.mkdir(exist_ok=True)
    for name, url in FONTS.items():
        target = d / name
        if not target.exists():
            urllib.request.urlretrieve(url, target)
    return d


def load_font(path: Path, size: int, axes: list[float]) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(path), size)
    try:
        font.set_variation_by_axes(axes)
    except Exception:
        pass
    return font


def fit_cover(img: Image.Image, w: int, h: int) -> Image.Image:
    scale = max(w / img.width, h / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def fade_left(img: Image.Image, until: float = 0.60, strength: float = 0.92) -> Image.Image:
    """Blend the left part of the image toward BG so text sits on a quiet field."""
    mask = Image.new("L", (W, 1))
    px = mask.load()
    for x in range(W):
        t = min(1.0, x / (W * until))
        alpha = (1 - t) ** 1.6 * strength
        px[x, 0] = int(255 * alpha)
    mask = mask.resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), BG), img, mask)


def tracked(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font, fill, tracking: float = 0.0) -> None:
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--hero", type=Path, required=True, help="illustration with its subject on the right")
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("social-preview.png"))
    parser.add_argument("--title", default="model-grade")
    parser.add_argument("--subtitle", default="the right Claude for the job")
    parser.add_argument("--tagline", default="Grade a prompt. Pick the cheapest Claude model\nand effort level that will do it well.")
    parser.add_argument("--meta", default="4 tiers  ·  effort low to max  ·  24 evals  ·  Claude Code skill  ·  MIT")
    parser.add_argument("--eyebrow", default="CLAUDE CODE SKILL")
    args = parser.parse_args(argv)

    fd = font_dir()
    f_eyebrow = load_font(fd / "JetBrainsMono.ttf", 18, [600])
    f_title = load_font(fd / "Inter.ttf", 96, [32, 800])
    f_sub = load_font(fd / "Inter.ttf", 58, [32, 700])
    f_body = load_font(fd / "Inter.ttf", 27, [24, 400])
    f_meta = load_font(fd / "JetBrainsMono.ttf", 18, [500])

    hero = Image.open(args.hero).convert("RGB")
    canvas = fit_cover(hero, W, H)
    canvas = Image.blend(canvas, Image.new("RGB", (W, H), BG), 0.18)
    canvas = fade_left(canvas)
    draw = ImageDraw.Draw(canvas)

    y = 118
    draw.rectangle((MARGIN, y + 5, MARGIN + 12, y + 17), fill=ACCENT)
    tracked(draw, (MARGIN + 24, y), args.eyebrow, f_eyebrow, MUTED, tracking=2.2)

    y = 160
    draw.text((MARGIN - 4, y), args.title, font=f_title, fill=FG)
    y += 112
    draw.text((MARGIN - 2, y), args.subtitle, font=f_sub, fill=ACCENT)
    y += 92
    draw.rectangle((MARGIN, y, MARGIN + 56, y + 4), fill=ACCENT)
    y += 30
    for line in args.tagline.split("\n"):
        draw.text((MARGIN, y), line, font=f_body, fill=MUTED)
        y += 36

    y = H - 118
    draw.line((MARGIN, y, MARGIN + 530, y), fill=(52, 58, 68), width=1)
    tracked(draw, (MARGIN, y + 22), args.meta, f_meta, DIM, tracking=0.6)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out, "PNG", optimize=True)
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
