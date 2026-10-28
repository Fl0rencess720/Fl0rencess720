#!/usr/bin/env python3
"""Generate the two character-portrait PNGs used by README.md.

Requires Pillow: python3 -m pip install Pillow
Usage: python3 scripts/avatar_art.py
Replace assets/avatar.png to update the source portrait. Use --font to select
another font with Unicode Braille support on non-macOS systems.
No network requests, README edits, or unused intermediate files are produced.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BRAILLE_BITS = ((0, 0, 0), (0, 1, 1), (0, 2, 2), (1, 0, 3),
                (1, 1, 4), (1, 2, 5), (0, 3, 6), (1, 3, 7))


def braille(image, columns=56):
    gray = ImageOps.grayscale(image).resize((columns * 2, columns * 2), Image.Resampling.LANCZOS)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.35)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=0.8, percent=120, threshold=3))
    dots = gray.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
    rows = []
    for y in range(0, dots.height, 4):
        row = []
        for x in range(0, dots.width, 2):
            value = sum(1 << bit for dx, dy, bit in BRAILLE_BITS
                        if y + dy < dots.height and dots.getpixel((x + dx, y + dy)))
            row.append(chr(0x2800 + value))
        rows.append(''.join(row))
    return rows


def render_portraits(art, output_dir, font_path):
    font = ImageFont.truetype(font_path, 24)
    cell_width, cell_height, padding = 16, 32, 56
    size = (len(art[0]) * cell_width + 2 * padding, len(art) * cell_height + 2 * padding)
    glyph_mask = Image.new('L', size)
    drawing = ImageDraw.Draw(glyph_mask)
    for row, line in enumerate(art):
        for column, char in enumerate(line):
            drawing.text((padding + column * cell_width, padding + row * cell_height + 5),
                         char, font=font, fill=255, stroke_width=1, stroke_fill=255)
    round_mask = Image.new('L', size)
    ImageDraw.Draw(round_mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=32, fill=255)
    output_dir.mkdir(parents=True, exist_ok=True)
    for theme, background, top_color, bottom_color in (
        ('dark', '#1a1b27', (159, 223, 210), (164, 185, 243)),
        ('light', '#f6f8fa', (48, 70, 85), (56, 63, 85)),
    ):
        image = Image.new('RGBA', size, background)
        gradient = Image.new('RGBA', size)
        draw_gradient = ImageDraw.Draw(gradient)
        for y in range(size[1]):
            t = y / (size[1] - 1)
            color = tuple(round(a + (b - a) * t) for a, b in zip(top_color, bottom_color))
            draw_gradient.line((0, y, size[0], y), fill=color + (255,))
        image.paste(gradient, (0, 0), glyph_mask)
        image.putalpha(round_mask)
        destination = output_dir / f'avatar-art-{theme}.png'
        image.save(destination, optimize=True)
        print(f'Generated {destination}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', default='/System/Library/Fonts/Apple Symbols.ttf',
                        help='Font with Unicode Braille support.')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'assets',
                        help='Output directory for the two README portrait images.')
    args = parser.parse_args()
    with Image.open(ROOT / 'assets/avatar.png') as source:
        art = braille(source.convert('RGB'))
    render_portraits(art, args.output_dir, args.font)


if __name__ == '__main__':
    main()
