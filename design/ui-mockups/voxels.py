"""A tiny voxel renderer (pure Python, no dependencies) for placeholder art.

Each model is a dict {(x, y, z): colour}. x points forward (heads face +x), y across the body and
z up. Models render as isometric 3D blocks with a lit top, two shaded sides and dark edges, then
get saved as transparent PNGs. They stand in for the real 3D models until those exist.
"""
import math
import struct
import subprocess
import zlib
from pathlib import Path

SS = 3  # supersampling factor; images are drawn this much bigger, then scaled down by ffmpeg


def hex_rgb(value: str):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def shade(rgb, factor):
    return tuple(max(0, min(255, round(c * factor))) for c in rgb)


def lighten(rgb, amount):
    return tuple(round(c + (255 - c) * amount) for c in rgb)


class Canvas:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.px = bytearray(width * height * 4)

    def fill_polygon(self, points, rgba):
        ys = [p[1] for p in points]
        top, bottom = max(0, int(math.floor(min(ys)))), min(self.h - 1, int(math.ceil(max(ys))))
        colour = bytes(rgba)
        n = len(points)
        for y in range(top, bottom + 1):
            sy = y + 0.5
            xs = []
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= sy < y1) or (y1 <= sy < y0):
                    xs.append(x0 + (sy - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                start = max(0, int(round(xs[i])))
                end = min(self.w, int(round(xs[i + 1])))
                if end > start:
                    offset = (y * self.w + start) * 4
                    self.px[offset:offset + (end - start) * 4] = colour * (end - start)

    def save_png(self, path: Path):
        raw = bytearray()
        stride = self.w * 4
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * stride:(y + 1) * stride]

        def chunk(kind, data):
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b"")
        path.write_bytes(png)


def inset(points, amount):
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    out = []
    for x, y in points:
        dx, dy = x - cx, y - cy
        length = math.hypot(dx, dy) or 1
        out.append((x - dx / length * amount, y - dy / length * amount))
    return out


def render(model: dict, path: Path, width=360, height=300, silhouette=False, studs=False, margin=0.08, yaw=34, pitch=26):
    """Draws the model to fit width x height (final pixels) and writes a PNG.

    The camera turns yaw degrees around the vertical axis and looks down pitch degrees, so the
    viewer sees the top, the +y side (the flank) and the +x side (the front).
    """
    W, H = width * SS, height * SS
    sa, ca = math.sin(math.radians(yaw)), math.cos(math.radians(yaw))
    sp, cp = math.sin(math.radians(pitch)), math.cos(math.radians(pitch))

    def project(x, y, z):
        return (x * ca - y * sa, (x * sa + y * ca) * sp - z * cp)

    def depth(v):
        x, y, z = v
        return (x * sa + y * ca) * cp + z * sp

    corners = [project(x + dx, y + dy, z + dz) for (x, y, z) in model for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)]
    min_x = min(c[0] for c in corners)
    max_x = max(c[0] for c in corners)
    min_y = min(c[1] for c in corners)
    max_y = max(c[1] for c in corners)
    unit = min(W * (1 - 2 * margin) / (max_x - min_x), H * (1 - 2 * margin) / (max_y - min_y))
    ox = (W - (max_x - min_x) * unit) / 2 - min_x * unit
    oy = (H - (max_y - min_y) * unit) / 2 - min_y * unit
    edge = max(1.0, unit * 0.035)

    def screen(x, y, z):
        sx, sy = project(x, y, z)
        return (ox + sx * unit, oy + sy * unit)

    canvas = Canvas(W, H)
    for (x, y, z) in sorted(model, key=depth):
        rgb = (21, 16, 42) if silhouette else hex_rgb(model[(x, y, z)])
        faces = []
        if (x, y, z + 1) not in model:
            faces.append(([screen(x, y, z + 1), screen(x + 1, y, z + 1), screen(x + 1, y + 1, z + 1), screen(x, y + 1, z + 1)], lighten(rgb, 0.12), True))
        if (x, y + 1, z) not in model:
            faces.append(([screen(x, y + 1, z), screen(x + 1, y + 1, z), screen(x + 1, y + 1, z + 1), screen(x, y + 1, z + 1)], shade(rgb, 0.9), False))
        if (x + 1, y, z) not in model:
            faces.append(([screen(x + 1, y, z), screen(x + 1, y + 1, z), screen(x + 1, y + 1, z + 1), screen(x + 1, y, z + 1)], shade(rgb, 0.72), False))
        for points, colour, is_top in faces:
            if silhouette:
                canvas.fill_polygon(points, (*rgb, 255))
                continue
            canvas.fill_polygon(points, (*shade(colour, 0.84), 255))
            canvas.fill_polygon(inset(points, edge), (*colour, 255))
            if studs and is_top and unit > 14:
                cx = sum(p[0] for p in points) / 4
                cy = sum(p[1] for p in points) / 4
                r = unit * 0.22
                stud = [(cx + math.cos(a) * r, cy + math.sin(a) * r * sp) for a in [i * math.pi / 8 for i in range(16)]]
                canvas.fill_polygon([(px, py + r * 0.18) for px, py in stud], (*shade(colour, 0.82), 255))
                canvas.fill_polygon(stud, (*lighten(colour, 0.18), 255))

    big = path.with_suffix(".ss.png")
    canvas.save_png(big)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(big), "-vf", f"scale={width}:{height}:flags=area", str(path)], check=True)
    big.unlink()


class Model(dict):
    """Helpers for building blocky models."""

    def box(self, x0, x1, y0, y1, z0, z1, colour):
        for x in range(x0, x1):
            for y in range(y0, y1):
                for z in range(z0, z1):
                    self[(x, y, z)] = colour
        return self

    def paint(self, test, colour):
        for key in list(self):
            if test(*key):
                self[key] = colour
        return self
