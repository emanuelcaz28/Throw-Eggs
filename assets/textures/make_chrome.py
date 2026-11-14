"""Makes the maps for Shattered Mirror's chrome (assets/textures/chrome_*.png, gold_*.png): two MaterialVariants in
MaterialService, "HoloChrome" and "PolishedGold", made by assets/models/studio_chrome.luau. Plain Python, no libraries:

    python3 assets/textures/make_chrome.py

chrome_color.png  holographic chrome: a silver base with soft bands of rainbow (rose, amber, mint, sky, violet) flowing
                  through it, and bare silver streaks between them. A metal tints what it reflects with this, so the
                  sky and light it reflects come back in shifting colours. The part's own colour tints it again, so a
                  part coloured white shows it all and a dark grey part is dark chrome
chrome_rough.png  almost mirror smooth, with a faint unevenness so the reflections don't look printed on
gold_color.png    near-white with soft warm brushed streaks; the part's gold colour does the rest
gold_rough.png    a little less smooth than the chrome, like polished gold leaf
metal.png         fully metal (white), for both

Every map tiles seamlessly (every wave fits a whole number of times into the tile).
"""
import colorsys
import math
import struct
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIZE = 512
TAU = math.tau


def write_png(path, size, pixel):
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            row.extend(pixel(x / size, y / size))
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(png)
    print("wrote", path.name)


def waves(u, v, terms):
    """A sum of waves that wraps at the tile's edges: each term is (times across, times down, phase, weight)."""
    return sum(w * math.sin(TAU * (a * u + b * v) + p) for a, b, p, w in terms)


FLOW = ((1, 2, 0.3, 1.0), (2, -1, 1.7, 0.7), (3, 1, 4.1, 0.45), (-1, 3, 2.6, 0.35), (4, 3, 5.2, 0.2))
STREAK = ((2, 1, 0.9, 1.0), (-3, 2, 3.3, 0.6), (1, 4, 5.7, 0.4))
WARP = ((1, -1, 2.2, 1.0), (2, 3, 0.4, 0.5))


def chrome(u, v):
    w = 0.06 * waves(u, v, WARP)  # bend the bands so they flow like oil on water
    flow = waves(u + w, v - w, FLOW)
    hue = (0.55 + 0.16 * flow) % 1.0  # sweeps round the rainbow along the bands
    streak = abs(waves(u - w, v + w, STREAK)) / 2.0  # 0 on the silver streaks, up to 1 in the colour
    sat = 0.1 + 0.42 * min(streak, 1.0) ** 0.8
    val = 0.9 + 0.08 * math.sin(TAU * (u + 2 * v) + flow)
    r, g, b = colorsys.hsv_to_rgb(hue, sat, min(val, 1.0))
    return round(r * 255), round(g * 255), round(b * 255)


def chrome_rough(u, v):
    k = 12 + 6 * (0.5 + 0.5 * math.sin(TAU * (3 * u + 2 * v) + waves(u, v, WARP)))
    return (round(k),) * 3


def gold(u, v):
    brush = waves(u, v, ((0, 7, 0.4, 1.0), (1, 13, 2.1, 0.5), (0, 23, 4.0, 0.3)))  # streaks running one way
    k = 0.95 + 0.02 * brush
    return round(255 * min(k, 1.0)), round(246 * min(k, 1.0)), round(226 * min(k, 1.0))


def gold_rough(u, v):
    k = 34 + 8 * waves(u, v, ((0, 7, 1.1, 0.6), (2, 11, 3.0, 0.4)))
    return (round(k),) * 3


if __name__ == "__main__":
    write_png(HERE / "chrome_color.png", SIZE, chrome)
    write_png(HERE / "chrome_rough.png", 256, chrome_rough)
    write_png(HERE / "gold_color.png", 256, gold)
    write_png(HERE / "gold_rough.png", 256, gold_rough)
    write_png(HERE / "metal.png", 16, lambda u, v: (255, 255, 255))
