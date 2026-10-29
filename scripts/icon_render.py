import io
import re
import gzip
import hashlib

import numpy as np
import resvg_py
from PIL import Image

ATLAS_CELL = 95


def decode_svg(data):
    # A few Houdini SVGs are stored gzipped (svgz) under a plain .svg name
    if data[:2] == b'\x1f\x8b':
        data = gzip.decompress(data)
    return data.decode('utf-8', 'replace')


def svg_hash(svg):
    # Ignore comments/whitespace so re-exports with no drawing change still match
    s = re.sub(r'<!--.*?-->', '', svg, flags=re.S)
    s = re.sub(r'\s+', ' ', s)
    return hashlib.md5(s.encode()).hexdigest()


def _size_from_viewbox(svg):
    # Some Qt-exported SVGs give width/height in mm, which resvg rejects
    m = re.search(r'viewBox="\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', svg)
    if not m:
        return svg
    head, rest = svg.split('<svg', 1)
    tag, tail = rest.split('>', 1)
    tag = re.sub(r'\s(width|height)="[^"]*"', '', tag)
    return f'{head}<svg width="{m[1]}" height="{m[2]}"{tag}>{tail}'


def render_svg(svg, size=200):
    """Render with the longest side at `size` px, as RGBA."""
    try:
        png = resvg_py.svg_to_bytes(svg_string=svg)
    except ValueError:
        svg = _size_from_viewbox(svg)
        png = resvg_py.svg_to_bytes(svg_string=svg)

    w, h = Image.open(io.BytesIO(png)).size
    kw = {'width': size} if w >= h else {'height': size}
    return Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg, **kw))).convert('RGBA')


def atlas_image(svg):
    """The icon as it sits in its atlas cell: fitted to 95px, top-left aligned."""
    img = render_svg(svg)
    img.thumbnail((ATLAS_CELL, ATLAS_CELL))
    canvas = Image.new('RGBA', (ATLAS_CELL, ATLAS_CELL), (0, 0, 0, 0))
    canvas.paste(img, (0, 0))
    return canvas


def _premultiplied(img):
    a = np.asarray(img, dtype=np.float32).copy()
    a[..., :3] *= a[..., 3:4] / 255
    return a


def changed_fraction(img_a, img_b):
    """Fraction of pixels that differ noticeably between two atlas images.

    Each pixel is compared against the best match in the other image's 3x3
    neighbourhood, so anti-aliasing and half-pixel shifts don't count. That
    lookup is one-sided (a thin stroke only in the other image can hide next
    to its own transparent pixels), so both directions are measured.
    Identical drawings score ~0, redraws score above 0.02.
    """
    a, b = _premultiplied(img_a), _premultiplied(img_b)
    return max(_changed_one_way(a, b), _changed_one_way(b, a))


def _changed_one_way(a, b):
    pad = np.pad(b, ((1, 1), (1, 1), (0, 0)), mode='edge')
    best = np.full(a.shape[:2], np.inf)
    for dy in range(3):
        for dx in range(3):
            shifted = pad[dy:dy + a.shape[0], dx:dx + a.shape[1]]
            best = np.minimum(best, np.abs(a - shifted).max(axis=2))
    return float((best > 60).mean())
