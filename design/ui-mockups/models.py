"""Blocky placeholder models: the 15 MVP dinos, the 5 eggs, biome islands and shop art.

Run this file to (re)write every PNG into renders/. Coordinates: x forward (heads face +x),
y across (the +y side faces the viewer), z up.
"""
import math
import sys
from pathlib import Path

from voxels import Model, render

OUT = Path(__file__).with_name("renders")
EYE = "#15102a"
WHITE = "#ffffff"


def theropod(main, belly, *, w=4, leg=4, body=(7, 4), tail=7, neck=2, head=(5, 3), head_w=None, arm=True, stripes=None):
    """Two-legged dino. Returns (model, head_box) so species can add details."""
    m = Model()
    length, height = body
    t = tail
    m.box(t, t + length, 0, w, leg, leg + height, main)
    m.box(t, t + length, 0, w, leg, leg + 1, belly)
    # Legs: thick thighs, thinner shins.
    for y0 in (0, w - 1):
        m.box(t + 1, t + 3, y0, y0 + 1, leg - 1, leg, main)
        m.box(t + 1, t + 2, y0, y0 + 1, 0, leg - 1, main)
        m.box(t + 1, t + 3, y0, y0 + 1, 0, 1, belly)
    # Tail tapers back and down.
    top = leg + height
    for i in range(t):
        x = t - 1 - i
        th = max(1, height - 1 - (i * height) // t)
        tw = w if i < t // 3 else max(1, w - 2)
        y0 = (w - tw) // 2
        z_top = top - 1 - i // 3
        m.box(x, x + 1, y0, y0 + tw, z_top - th + 1, z_top + 1, main)
    # Neck and head.
    hl, hh = head
    hw = head_w or w
    hy = (w - hw) // 2
    nx = t + length - 2
    m.box(nx, nx + 2, max(0, hy), min(w, hy + hw), top, top + neck, main)
    hz = top + neck - 1
    hx = nx
    m.box(hx, hx + hl, hy, hy + hw, hz, hz + hh, main)
    m.box(hx + 1, hx + hl, hy, hy + hw, hz, hz + 1, belly)
    m[(hx + hl - 2, hy + hw - 1, hz + hh - 1)] = EYE
    if arm:
        m[(t + length, w - 1, leg + 1)] = main
        m[(t + length, 0, leg + 1)] = main
    if stripes:
        m.paint(lambda x, y, z: z >= leg + height - 1 and z < leg + height and t <= x < t + length and x % 2 == 0, stripes)
    return m, (hx, hy, hz, hl, hw, hh)


def quadruped(main, belly, *, w=5, leg=3, body=(8, 4), tail=6, head=(4, 3), head_z=None, neck=1):
    m = Model()
    length, height = body
    t = tail
    m.box(t, t + length, 0, w, leg, leg + height, main)
    m.box(t, t + length, 0, w, leg, leg + 1, belly)
    for x0 in (t + 1, t + length - 2):
        for y0 in (0, w - 1):
            m.box(x0, x0 + 1, y0, y0 + 1, 0, leg, main)
    top = leg + height
    for i in range(t):
        x = t - 1 - i
        th = max(1, height - 1 - (i * height) // t)
        tw = w - 2 if i < t // 2 else max(1, w - 4)
        y0 = (w - tw) // 2
        z_top = top - 1 - i // 2
        m.box(x, x + 1, y0, y0 + tw, max(leg - 1, z_top - th + 1), z_top + 1, main)
    hl, hh = head
    hz = head_z if head_z is not None else leg + 1
    hx = t + length + neck
    m.box(t + length, hx, 1, w - 1, hz, hz + hh - 1, main)
    m.box(hx, hx + hl, 0, w, hz, hz + hh, main)
    m.box(hx, hx + hl, 0, w, hz, hz + 1, belly)
    m[(hx + hl - 2, w - 1, hz + hh - 1)] = EYE
    return m, (hx, 0, hz, hl, w, hh)


# --- Fern Valley --------------------------------------------------------------------------

def compy():
    m, _ = theropod("#7ed957", "#e8f7b8", w=3, leg=3, body=(5, 3), tail=6, neck=1, head=(4, 2), stripes="#3e9f3a")
    return m


def gallimimus():
    m, (hx, hy, hz, hl, hw, hh) = theropod("#f2c14e", "#fff1c9", w=3, leg=6, body=(5, 3), tail=6, neck=5, head=(4, 2), arm=True)
    m.paint(lambda x, y, z: z > 9 and z < hz and x in (hx, hx + 1), "#e07b39")
    return m


def parasaur():
    m, (hx, hy, hz, hl, hw, hh) = theropod("#3fb6a8", "#c9f2e6", w=4, leg=4, body=(8, 4), tail=8, neck=3, head=(5, 3))
    # Long hollow crest sweeping back and up from the top of the head, two blocks thick so the
    # steps stay joined.
    for i in range(7):
        z = hz + hh - 1 + (i + 1) // 2
        for y in (hy + 1, hy + 2):
            m[(hx + 2 - i, y, z)] = "#ffb02e"
            m[(hx + 2 - i, y, z + 1)] = "#ffb02e"
    return m


def stego():
    m, _ = quadruped("#6fbf5a", "#d8f0b0", w=5, leg=3, body=(9, 4), tail=7, head=(3, 2), head_z=3, neck=1)
    # Two rows of plates along the back, tallest in the middle.
    for i, x in enumerate(range(5, 17, 2)):
        h = [1, 2, 3, 3, 2, 1][i]
        for y in (1, 3):
            m.box(x, x + 1, y, y + 1, 7, 7 + h, "#ff7a3d")
    # Tail spikes sit right on top of the tail.
    for x in (1, 3):
        top = max(z for (px, py, z) in m if px == x and py == 2)
        m[(x, 2, top + 1)] = "#fff3d6"
        m[(x, 2, top + 2)] = "#fff3d6"
    return m


def raptor():
    m, _ = theropod("#ff9a3c", "#ffe3b8", w=3, leg=4, body=(6, 3), tail=9, neck=2, head=(5, 2), stripes="#7a3b1e")
    m.paint(lambda x, y, z: z == 0 and x in (8, 9), "#fff3d6")
    return m


# --- Dry Plains ---------------------------------------------------------------------------

def pachy():
    m, (hx, hy, hz, hl, hw, hh) = theropod("#9b7bd6", "#e6dcff", w=4, leg=4, body=(6, 4), tail=7, neck=2, head=(4, 3))
    # Thick round dome on top of the head.
    m.box(hx, hx + 3, hy, hy + hw, hz + hh, hz + hh + 2, "#ffd23f")
    m.box(hx + 1, hx + 2, hy + 1, hy + hw - 1, hz + hh + 2, hz + hh + 3, "#ffd23f")
    return m


def ankylo():
    m, _ = quadruped("#a88a5a", "#efe0c0", w=7, leg=2, body=(9, 3), tail=8, head=(3, 3), head_z=2, neck=0)
    m.paint(lambda x, y, z: z == 5 and (x + y) % 2 == 0, "#6b5634")
    m.paint(lambda x, y, z: (y in (0, 6)) and z == 4 and x % 2 == 0, "#fff3d6")
    m.box(-2, 1, 2, 5, 2, 5, "#5a4630")  # club
    return m


def triceratops():
    m, (hx, hy, hz, hl, hw, hh) = quadruped("#4aa3df", "#cfeaff", w=5, leg=3, body=(9, 4), tail=6, head=(5, 4), head_z=3, neck=0)
    # Frill behind the head, wider and taller than the body.
    m.box(hx - 1, hx, -1, 6, hz + 1, hz + 7, "#ff6f91")
    m.box(hx - 1, hx, 0, 5, hz + 7, hz + 8, "#ff6f91")
    # Two brow horns and a nose horn.
    for y in (1, 3):
        m.box(hx + 2, hx + 6, y, y + 1, hz + 4, hz + 5, "#fff3d6")
    m.box(hx + 4, hx + 6, 2, 3, hz + 2, hz + 3, "#fff3d6")
    return m


def carno():
    m, (hx, hy, hz, hl, hw, hh) = theropod("#e2463c", "#ffd0c4", w=4, leg=5, body=(7, 4), tail=8, neck=2, head=(5, 3), stripes="#6b1a16")
    for y in (hy, hy + hw - 1):
        m[(hx + 1, y, hz + hh)] = "#6b1a16"
        m[(hx + 1, y, hz + hh + 1)] = "#6b1a16"
    return m


def trex():
    m, (hx, hy, hz, hl, hw, hh) = theropod("#5d9b4b", "#d9e8a8", w=5, leg=5, body=(9, 5), tail=10, neck=2, head=(8, 5), stripes="#3a6b30")
    # Teeth along the jaw line.
    for x in range(hx + 2, hx + hl, 2):
        m[(x, hy + hw - 1, hz + 1)] = WHITE
    return m


# --- Swamp --------------------------------------------------------------------------------

def bary():
    m, (hx, hy, hz, hl, hw, hh) = theropod("#7c9a8a", "#e3efe8", w=4, leg=4, body=(8, 4), tail=9, neck=2, head=(8, 2), stripes="#3f5a4d")
    return m


def dilo():
    m, (hx, hy, hz, hl, hw, hh) = theropod("#c7d94a", "#f4f7c8", w=4, leg=4, body=(7, 4), tail=8, neck=3, head=(5, 3))
    for y in (hy, hy + hw - 1):
        m.box(hx, hx + 4, y, y + 1, hz + hh, hz + hh + 2, "#ff4d6d")
    return m


def sarco():
    m = Model()
    m.box(6, 18, 0, 5, 1, 4, "#6f8a3a")
    m.box(6, 18, 0, 5, 1, 2, "#e1e6a5")
    for x0 in (7, 15):
        for y0 in (0, 4):
            m.box(x0, x0 + 2, y0, y0 + 1, 0, 1, "#6f8a3a")
    for i in range(6):
        m.box(5 - i, 6 - i, 1, 4, 1, 3 if i < 3 else 2, "#6f8a3a")
    m.box(18, 22, 0, 5, 1, 4, "#6f8a3a")
    m.box(22, 30, 1, 4, 1, 3, "#6f8a3a")  # long snout
    m.box(22, 30, 1, 4, 1, 2, "#e1e6a5")
    for x in range(23, 30, 2):
        m[(x, 3, 2)] = WHITE
    m[(20, 4, 3)] = EYE
    m.paint(lambda x, y, z: z == 3 and 6 <= x < 18 and (x + y) % 2 == 0, "#4a5e26")
    return m


def brachio():
    m, (hx, hy, hz, hl, hw, hh) = quadruped("#6aa8c7", "#dff1fa", w=5, leg=5, body=(9, 5), tail=9, head=(1, 1), head_z=8, neck=0)
    # Remove the stub head and build a long neck rising forward.
    for key in [k for k in m if k[0] >= hx]:
        del m[key]
    x, z = 14, 8
    for i in range(9):
        m.box(x, x + 2, 1, 4, z, z + 2, "#6aa8c7")
        x += 1 if i % 2 == 0 else 0
        z += 1
    m.box(x, x + 4, 1, 4, z, z + 2, "#6aa8c7")
    m.box(x, x + 2, 1, 4, z + 2, z + 3, "#6aa8c7")
    m[(x + 2, 3, z + 1)] = EYE
    m.paint(lambda px, py, pz: pz in (9, 10) and 6 < px < 14 and (px + py) % 3 == 0, "#3f7894")
    return m


def spino():
    m, (hx, hy, hz, hl, hw, hh) = theropod("#e8743b", "#ffd9b8", w=4, leg=5, body=(9, 4), tail=10, neck=2, head=(8, 2), stripes=None)
    # Tall sail along the back, highest in the middle.
    heights = [2, 4, 5, 6, 6, 5, 4, 2]
    for i, h in enumerate(heights):
        x = 10 + i
        m.box(x, x + 1, 1, 3, 9, 9 + h, "#ffcf3f")
        m.box(x, x + 1, 1, 3, 9 + h - 1, 9 + h, "#ff4d6d")
    return m


DINOS = {
    "Compy": (compy, "common"), "Gallimimus": (gallimimus, "uncommon"), "Parasaur": (parasaur, "rare"),
    "Stego": (stego, "epic"), "Raptor": (raptor, "legendary"),
    "Pachy": (pachy, "common"), "Ankylo": (ankylo, "uncommon"), "Triceratops": (triceratops, "rare"),
    "Carno": (carno, "epic"), "TRex": (trex, "legendary"),
    "Bary": (bary, "common"), "Dilo": (dilo, "uncommon"), "Sarco": (sarco, "rare"),
    "Brachio": (brachio, "epic"), "Spino": (spino, "legendary"),
}

# --- Eggs ---------------------------------------------------------------------------------

def egg_model(shell, spot, pattern="spots", r=6):
    m = Model()
    below, above = r * 1.05, r * 1.6  # the top half is taller, which gives the egg shape
    height = int(below + above)
    for z in range(height + 1):
        t = (z + 0.5 - below) / (below if z + 0.5 < below else above)
        if abs(t) > 1:
            continue
        radius = r * math.sqrt(1 - t * t)
        for x in range(-r, r + 1):
            for y in range(-r, r + 1):
                if x * x + y * y <= radius * radius:
                    m[(x, y, z)] = shell
    for (x, y, z) in list(m):
        if pattern == "spots" and (x * 7 + y * 3 + z * 5) % 11 == 0:
            m[(x, y, z)] = spot
        elif pattern == "cracks" and ((x + z) % 6 == 0 or (y - z) % 7 == 0):
            m[(x, y, z)] = spot
        elif pattern == "stars" and (x * 5 + y * 11 + z * 3) % 13 == 0:
            m[(x, y, z)] = spot
        elif pattern == "rainbow":
            bands = ["#ff4d6d", "#ff9a3c", "#ffd23f", "#7ed957", "#4aa3df", "#9b7bd6"]
            m[(x, y, z)] = bands[min(len(bands) - 1, z * len(bands) // (height + 1))]
    return m


EGGS = {
    "DirtyEgg": ("#d9c39b", "#8c6b3d", "spots"),
    "SpottedEgg": ("#bff0d1", "#2f9e5a", "spots"),
    "GoldenEgg": ("#ffd84a", "#f29e0c", "spots"),
    "LavaEgg": ("#ff7a3d", "#7a1f0a", "cracks"),
    "CosmicEgg": ("#7b5cff", "#ffe066", "stars"),
    "PrismEgg": ("#ffffff", "#ffffff", "rainbow"),
}

# --- Biome islands ------------------------------------------------------------------------

def island(top, dirt, size=12):
    m = Model()
    for layer in range(4):
        shrink = layer
        m.box(shrink, size - shrink, shrink, size - shrink, 6 - layer, 7 - layer, top if layer == 0 else dirt)
    return m


def fern_valley():
    m = island("#7ed957", "#a86b3c")
    m.box(7, 9, 3, 5, 7, 12, "#8a5a2b")
    m.box(5, 11, 1, 7, 12, 15, "#4fbf4a")
    m.box(6, 10, 2, 6, 15, 16, "#4fbf4a")
    for (x, y, c) in [(2, 8, "#ff4d6d"), (3, 10, "#ffd23f"), (9, 9, "#ff4d6d"), (2, 3, "#ffffff")]:
        m[(x, y, 7)] = c
    for (x, y) in [(4, 7), (4, 8), (10, 2)]:
        m.box(x, x + 1, y, y + 1, 7, 9, "#3e9f3a")
    return m


def dry_plains():
    m = island("#f2d27a", "#c98a4a")
    m.box(7, 8, 6, 7, 7, 13, "#4fa34a")
    m.box(6, 7, 6, 7, 9, 11, "#4fa34a")
    m.box(5, 6, 6, 7, 10, 12, "#4fa34a")
    m.box(8, 9, 6, 7, 10, 12, "#4fa34a")
    m.box(9, 10, 6, 7, 11, 13, "#4fa34a")
    m.box(2, 5, 7, 10, 7, 9, "#b5a48a")
    m.box(3, 4, 8, 9, 9, 10, "#b5a48a")
    m.box(9, 11, 2, 4, 7, 8, "#d9b05a")
    return m


def swamp():
    m = island("#5f7a3a", "#5a4630")
    m.box(3, 9, 4, 10, 6, 7, "#3fa9d6")
    for (x, y) in [(4, 6), (7, 8)]:
        m.box(x, x + 2, y, y + 1, 7, 8, "#6fd05b")
    for (x, y, h) in [(1, 2, 4), (2, 1, 3), (10, 9, 5), (10, 10, 3), (9, 2, 4)]:
        m.box(x, x + 1, y, y + 1, 7, 7 + h, "#9acd4a")
        m[(x, y, 7 + h)] = "#7a5230"
    m.box(1, 6, 9, 11, 7, 8, "#7a5230")
    return m


BIOMES = {"FernValley": fern_valley, "DryPlains": dry_plains, "Swamp": swamp}

# --- Shop art -----------------------------------------------------------------------------

def cash_bundle(m, x, y, z):
    m.box(x, x + 4, y, y + 2, z, z + 1, "#4fd15a")
    m.box(x + 1, x + 3, y, y + 2, z, z + 1, "#ffd23f")


def cash_pile(count):
    m = Model()
    spots = [(0, 0, 0), (0, 3, 0), (5, 0, 0), (5, 3, 0), (2, 1, 1), (2, 4, 1), (7, 1, 1), (0, 6, 0), (5, 6, 0),
             (3, 3, 2), (8, 4, 1), (-1, 2, 1), (4, 6, 1), (1, 5, 2), (6, 2, 2), (4, 0, 2)]
    for x, y, z in spots[:count]:
        cash_bundle(m, x, y, z)
    return m


def bolt(m, ox, oy, oz, colour="#ffd43b"):
    """A chunky lightning bolt standing up, three blocks thick, with an orange edge."""
    rows = ["....XXXX", "...XXXX.", "..XXXX..", ".XXXXXXX", "XXXXXXX.", "...XXX..", "..XXX...", "..XX....", ".XX.....", ".X......"]
    for i, row in enumerate(rows):
        for j, ch in enumerate(row):
            if ch == "X":
                for d in range(3):
                    m[(ox + j, oy + d, oz + len(rows) - i)] = colour if d < 2 else "#ff9a1f"


def bolt_pile(count):
    m = Model()
    spots = [(0, 0, 0), (7, 5, 0), (-6, 6, 0), (2, 11, 0), (9, -5, 0), (-4, -4, 0)]
    for x, y, z in spots[:count]:
        bolt(m, x, y, z)
    return m


def clover():
    m = Model()
    for cx, cz in [(-3, 3), (3, 3), (-3, -3), (3, -3)]:
        for x in range(-3, 4):
            for z in range(-3, 4):
                if x * x + z * z <= 9:
                    m[(cx + x, 0, cz + z + 12)] = "#4fd15a"
                    m[(cx + x, 1, cz + z + 12)] = "#4fd15a"
    for x in range(-1, 2):
        for z in range(-1, 2):
            m[(x, 2, 12 + z)] = "#9cf28f"
    for z in range(0, 7):
        m[(0 + z // 3, 0, z)] = "#3a9f3a"
    return m


def gift():
    m = Model()
    m.box(0, 8, 0, 8, 0, 6, "#ff4d6d")
    m.box(-1, 9, -1, 9, 6, 8, "#ff4d6d")
    m.box(3, 5, -1, 9, 0, 8, "#ffd23f")
    m.box(-1, 9, 3, 5, 0, 8, "#ffd23f")
    m.box(2, 4, 3, 5, 8, 10, "#ffd23f")
    m.box(4, 6, 3, 5, 8, 10, "#ffd23f")
    return m


def sunburst(path, size=520, rays=18):
    """Soft light rays for featured items: alternating translucent wedges from the centre."""
    from voxels import Canvas, SS
    import subprocess
    canvas = Canvas(size * SS, size * SS)
    c = size * SS / 2
    for i in range(rays):
        a0 = (i * 2) * math.pi / (rays * 2)
        a1 = (i * 2 + 1) * math.pi / (rays * 2)
        a0, a1 = a0 * 2, a1 * 2
        points = [(c, c), (c + math.cos(a0) * c * 1.5, c + math.sin(a0) * c * 1.5), (c + math.cos(a1) * c * 1.5, c + math.sin(a1) * c * 1.5)]
        canvas.fill_polygon(points, (255, 255, 255, 70))
    big = path.with_suffix(".ss.png")
    canvas.save_png(big)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(big), "-vf", f"scale={size}:{size}:flags=area", str(path)], check=True)
    big.unlink()


def build_all(only=None):
    OUT.mkdir(exist_ok=True)
    jobs = []
    for name, (fn, _) in DINOS.items():
        jobs.append((f"dino_{name}", fn, dict(width=360, height=300)))
        jobs.append((f"dino_{name}_shadow", fn, dict(width=360, height=300, silhouette=True)))
    for name, (shell, spot, pattern) in EGGS.items():
        jobs.append((f"egg_{name}", (lambda s=shell, p=spot, pt=pattern: egg_model(s, p, pt)), dict(width=260, height=300, margin=0.06)))
    for name, fn in BIOMES.items():
        jobs.append((f"biome_{name}", fn, dict(width=320, height=340, studs=True, margin=0.05)))
    for count, name in [(1, "S"), (3, "M"), (7, "L"), (16, "XL")]:
        jobs.append((f"cash_{name}", (lambda c=count: cash_pile(c)), dict(width=240, height=200)))
    for count, name in [(1, "S"), (2, "M"), (4, "L"), (6, "XL")]:
        jobs.append((f"bolts_{name}", (lambda c=count: bolt_pile(c)), dict(width=240, height=200)))
    jobs.append(("clover", clover, dict(width=220, height=220)))
    jobs.append(("gift", gift, dict(width=200, height=200)))
    if not only or any("sunburst" in o for o in only):
        sunburst(OUT / "sunburst.png")
    for name, fn, kwargs in jobs:
        if only and not any(o in name for o in only):
            continue
        render(fn(), OUT / f"{name}.png", **kwargs)
    return [j[0] for j in jobs]


def export_json(path):
    """Every model as {name: [[x, y, z, "#rrggbb"], ...]} for building in Blender."""
    import json
    models = {}
    for name, (fn, _) in DINOS.items():
        models[f"dino_{name}"] = fn()
    for name, (shell, spot, pattern) in EGGS.items():
        models[f"egg_{name}"] = egg_model(shell, spot, pattern)
    for name, fn in BIOMES.items():
        models[f"biome_{name}"] = fn()
    for count, name in [(1, "S"), (3, "M"), (7, "L"), (16, "XL")]:
        models[f"cash_{name}"] = cash_pile(count)
    for count, name in [(1, "S"), (2, "M"), (4, "L"), (6, "XL")]:
        models[f"bolts_{name}"] = bolt_pile(count)
    models["clover"] = clover()
    models["gift"] = gift()
    # In the game dinos are seen from both sides, so eyes and teeth on the viewer's side get a
    # twin on the far side.
    for name, m in models.items():
        if not name.startswith("dino_"):
            continue
        min_y = min(k[1] for k in m)
        max_y = max(k[1] for k in m)
        for (x, y, z), c in list(m.items()):
            if c in (EYE, WHITE) and y == max(k[1] for k in m if k[0] == x and k[2] == z):
                low = min(k[1] for k in m if k[0] == x and k[2] == z)
                m[(x, low, z)] = c
    data = {name: [[x, y, z, c] for (x, y, z), c in m.items()] for name, m in models.items()}
    Path(path).write_text(json.dumps(data, separators=(",", ":")))
    return {name: len(v) for name, v in data.items()}


if __name__ == "__main__":
    if sys.argv[1:2] == ["export"]:
        counts = export_json(sys.argv[2])
        print(len(counts), "models,", sum(counts.values()), "blocks")
        sys.exit()
    names = build_all(sys.argv[1:] or None)
    print(len(names), "images")
