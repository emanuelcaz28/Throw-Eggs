"""Writes the stud textures: see-through images, so a part's own Color shows through.

    python3 make_stud_textures.py

stud.png is one stud for animals and props. checker_studs_overlay.png is a 2 x 2 checker with 4 studs per
square, for floors and walls. Their UVs are set in build_fern_valley.py and build_world_kit.py.
"""
import math
import struct
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent


def write_png(path, size, pixel):
    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            rows.extend(pixel(x, y))

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b""))


def stud(u, v):
    """Light level at a point in one stud: above 0 lightens, below 0 darkens."""
    dx, dy = u - 0.5, v - 0.5
    dist = math.hypot(dx, dy)
    if max(abs(dx), abs(dy)) > 0.47:
        return -0.14
    if dist > 0.34:
        return 0
    if dist > 0.27:
        return -0.34 if dx - dy > 0 else 0.34
    return 0.1


def rgba(level, base_dark=0.0):
    """One see-through pixel: black to darken, white to lighten."""
    dark = base_dark + max(-level, 0)
    light = max(level, 0)
    if light > dark:
        return (255, 255, 255, round((light - dark) * 255))
    return (0, 0, 0, round(dark * 255))


def stud_pixel(x, y):
    return rgba(stud((x + 0.5) / 128, (y + 0.5) / 128))


def checker_pixel(x, y):
    size, per_tile = 512, 8
    square = (x // (size // 2) + y // (size // 2)) % 2 == 1
    u, v = (x + 0.5) * per_tile / size % 1, (y + 0.5) * per_tile / size % 1
    return rgba(stud(u, v), 0.2 if square else 0)


write_png(HERE / "stud.png", 128, stud_pixel)
write_png(HERE / "checker_studs_overlay.png", 512, checker_pixel)
print("written")
