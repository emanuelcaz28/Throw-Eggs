"""Makes the stud material's maps (assets/textures/studs_*.png): 4 x 4 classic round Roblox studs per tile, to go
in a MaterialVariant with StudsPerTile 4 (one stud per stud). Plain Python, no libraries:

    python3 assets/textures/make_studs.py

studs_normal.png  the bumps, so each stud catches the light and shades itself like a real raised stud (OpenGL
                  convention, green up, which is what Roblox reads)
studs_color.png   almost white, a soft shadow round each stud's foot; the part's own colour tints it, so the
                  colour stays clean
studs_rough.png   tops a touch shinier than the gaps, like plastic
"""
import math
import struct
import zlib
from pathlib import Path

SIZE, PER = 512, 4  # pixels per tile, studs per side
CELL = SIZE // PER
RADIUS = CELL * 0.30  # the stud's top
BEVEL = CELL * 0.035  # the rounded rim round its top
HEIGHT = 1.0


def height(x, y):
    """Stud height at a pixel, wrapping so the tile repeats seamlessly."""
    cx = (x % CELL) - CELL / 2 + 0.5
    cy = (y % CELL) - CELL / 2 + 0.5
    d = math.hypot(cx, cy)
    if d <= RADIUS - BEVEL:
        return HEIGHT
    if d >= RADIUS + BEVEL:
        return 0.0
    t = (d - (RADIUS - BEVEL)) / (2 * BEVEL)
    return HEIGHT * (0.5 + 0.5 * math.cos(t * math.pi))


def write_png(path, pixels):
    raw = b"".join(b"\x00" + bytes(row) for row in pixels)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(png)


def main():
    out = Path(__file__).resolve().parent
    h = [[height(x, y) for x in range(SIZE)] for y in range(SIZE)]
    strength = 22.0
    normal, color, rough = [], [], []
    for y in range(SIZE):
        nrow, crow, rrow = [], [], []
        for x in range(SIZE):
            dx = (h[y][(x + 1) % SIZE] - h[y][(x - 1) % SIZE]) * strength
            dy = (h[(y + 1) % SIZE][x] - h[(y - 1) % SIZE][x]) * strength
            nx, ny, nz = -dx, dy, 1.0  # image rows run down, so flip to green-up
            k = 1 / math.sqrt(nx * nx + ny * ny + nz * nz)
            nrow += [int((nx * k * 0.5 + 0.5) * 255), int((ny * k * 0.5 + 0.5) * 255), int((nz * k * 0.5 + 0.5) * 255)]
            cx = (x % CELL) - CELL / 2 + 0.5
            cy = (y % CELL) - CELL / 2 + 0.5
            d = math.hypot(cx, cy)
            shade = 1.0
            if d > RADIUS:  # a soft contact shadow round the stud's foot
                shade -= 0.16 * math.exp(-((d - RADIUS) / (CELL * 0.06)) ** 2)
            v = int(242 * shade)
            crow += [v, v, v]
            r = 150 if d < RADIUS else 185
            rrow += [r, r, r]
        normal.append(nrow)
        color.append(crow)
        rough.append(rrow)
    write_png(out / "studs_normal.png", normal)
    write_png(out / "studs_color.png", color)
    write_png(out / "studs_rough.png", rough)
    print("wrote studs_normal.png, studs_color.png, studs_rough.png")


main()
