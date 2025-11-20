#!/usr/bin/env python3
"""
Batch process images in the `images/` folder to produce outlined versions in `images/outlined/`.
This uses Pillow to detect edges and expand them into a thicker, rounded outline, then
composites the original image on top.

Usage:
    python3 process_images.py

Requirements: Pillow
"""
from PIL import Image, ImageFilter, ImageOps
from pathlib import Path

SRC_DIR = Path(__file__).parent / 'images'
OUT_DIR = SRC_DIR / 'outlined'
OUT_DIR.mkdir(exist_ok=True)

# tweak these as needed
THICKNESS = 3
EDGE_THRESHOLD = 30  # 0-255, lower -> more edges


def process_image(src_path: Path, out_path: Path, thickness: int = THICKNESS, threshold: int = EDGE_THRESHOLD):
    print(f'Processing {src_path.name} -> {out_path.name}')
    img = Image.open(src_path).convert('RGBA')

    # grayscale and edge detection
    gray = img.convert('L')
    edges = gray.filter(ImageFilter.FIND_EDGES)

    # binary threshold
    bw = edges.point(lambda p: 255 if p > threshold else 0)

    # expand/dilate the mask to thicken the outline using MaxFilter
    for _ in range(thickness):
        bw = bw.filter(ImageFilter.MaxFilter(3))

    # create black RGBA image where mask is present
    black = Image.new('RGBA', img.size, (0, 0, 0, 255))

    # compose black outline using the mask
    outlined = Image.composite(black, Image.new('RGBA', img.size, (0, 0, 0, 0)), bw)

    # paste original image on top so interior details remain
    outlined.paste(img, (0, 0), img)

    # save
    outlined.save(out_path)


if __name__ == '__main__':
    files = [p for p in SRC_DIR.iterdir() if p.is_file() and p.suffix.lower() in ('.png', '.jpg', '.jpeg')]
    if not files:
        print('No images found in', SRC_DIR)
    for f in files:
        out = OUT_DIR / f.name
        try:
            process_image(f, out)
        except Exception as e:
            print('Failed for', f, e)
    print('Done.')
