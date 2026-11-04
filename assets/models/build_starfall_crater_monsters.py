"""Builds Starfall Crater's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_starfall_crater_monsters.py
    QUICK=1 Blender -b -P build_starfall_crater_monsters.py    (stills only, into QUICK_OUT or /tmp, for trying faces)

Saves starfall_crater_monsters.blend and renders to design/world/monsters_starfall_crater/. Starfall Crater's
props are in build_starfall_crater.py.

The last map breaks the run of ever-angrier faces on purpose: the owner asked for monsters that are nice to look
at and interesting, not cute and not aggressive, above all in the face. So these are calm, old and a little
strange, like things that fell with the stars. The starfall face: long half-closed almond eyes, dark as the
night sky, with a glowing star for an iris peeking out under a level lid (a level lid reads calm; slanted ones
read angry or sad), and a quiet closed mouth with no teeth. Inside the mouth is the night sky, dotted with
stars, so when they open it in the roar they look like they're singing. The map's colours: midnight blue,
pale moon dust, cyan crystal, gold star-stuff and magenta nebula glow.

  Craterback      a slow grazer carrying a whole little crater on its back, with a fallen star stuck in it
                  and crystals growing round it
  Stargazer       a tall stilt-legged bird that is always looking up, its beak to the sky, constellations on
                  its folded wings and gold stars on the tips of its plumes
  Comet Trike     a trike whose frill is the head of a comet, its tail streaming back over its body,
                  with crystal horns
  Ringhorn        a tall stag with crystal antlers and a planet's ring floating round them, two moons on the
                  ring, a coat of night sky dotted with stars and a star on its brow
  Nebulasaur      a long-necked giant whose body is a piece of the night sky: stars all over, a pink nebula
                  glowing on its flanks and a row of gold stars down its back
  Star Sovereign  the boss: a robed king of the stars with a moon-pale face and a stardust beard, a crown
                  and a halo, a cape full of stars, a star-topped staff, a moon in its other hand and
                  crystals floating round its shoulders

All have the Jaw bone, so they open their mouths in the game (the roar becomes a song). Extra parts ride bones
the game already moves: Stargazer's wings, and the Sovereign's floating crystals, are on the Wing bones.
Glowing parts are EyeGlow, StarGlow, CrystalGlow, NebulaGlow, Sparkle, CometHead, CometTail, Halo and Orb
(Neon in the game, shared/Roles.luau). Built at the first map's size; the game makes them 10x
(Config/Biomes standardScale). 1 Blender unit = 1 stud, models face +Y, feet on Z = 0.
"""
import math
import os
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_desert import beam, quad_legs  # noqa: E402
from build_forest import Model, biped_legs, tail  # noqa: E402
from build_starfall_crater import ball, crystal, gem, sparkle, star_prism  # noqa: E402
from build_volcano import prism, ring_at, top_of  # noqa: E402
from monster_stage import build_and_render, light_up, set_sky  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_starfall_crater"

GLOW_ROLES = {"EyeGlow", "StarGlow", "CrystalGlow", "NebulaGlow", "Sparkle", "CometHead", "CometTail", "Halo", "Orb"}
kit.NO_STUDS.update({"StarLine"})

# The starfall face, and the map's colours (build_starfall_crater.py).
FACE = {"Pupil": "#10143a", "EyeGlow": "#ffe48a", "Mouth": "#141a42", "Sparkle": "#fff4cf", "StarLine": "#a9b4ea"}
DUST, DUST_DARK, SCORCH = "#c3cbee", "#959fcc", "#232846"
CRYSTAL, CRYSTAL_GLOW = "#8ff0ff", "#3fdcff"
STAR_GLOW, STAR, STAR_DARK = "#ffe066", "#ffc93f", "#e09a2a"
NEBULA_GLOW = "#ff58d6"
SKY, FLOOR = "#141a40", "#303a72"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- shapes


def star_on(m, role, p, outer, normal="y", points=4, inner=0.36, depth=0.05, spin=0.0):
    """A flat star lying on a surface that faces `normal` ("x", "y" or "z")."""
    tilt = {"y": (0, spin, 0), "x": (0, spin, math.pi / 2), "z": (math.pi / 2, 0, spin)}[normal]
    star_prism(m, role, p, outer, outer * inner, depth, tilt, points)


def oval(m, role, x, y, z0, z1, rx0, ry0, rx1, ry1, sides=12):
    """An upright n-sided column with an oval section, rx/ry at the foot (0) and the top (1)."""
    verts = []
    for z, rx, ry in ((z0, rx0, ry0), (z1, rx1, ry1)):
        for i in range(sides):
            a = math.pi / sides + i * math.tau / sides
            verts.append((x + rx * math.cos(a), y + ry * math.sin(a), z))
    faces = [list(range(sides))[::-1], list(range(sides, 2 * sides))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides + j, sides + i])
    m._add(role, verts, faces)


def disc(m, role, x, y, z, r, depth, sides=10):
    """An upright n-sided slab facing +Y."""
    verts = []
    for dy in (-depth / 2, depth / 2):
        for i in range(sides):
            a = math.pi / 2 + i * math.tau / sides
            verts.append((x + r * math.cos(a), y + dy, z + r * math.sin(a)))
    faces = [list(range(sides))[::-1], list(range(sides, 2 * sides))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides + j, sides + i])
    m._add(role, verts, faces)


def ring(m, role, centre, radius, width, thick, tilt=0.0, upright=False, n=20):
    """A ring of beams: flat (tilted `tilt` about X), or upright in the XZ plane, facing Y. Returns its points."""
    cx, cy, cz = centre
    pts = []
    for i in range(n):
        a = i * math.tau / n
        u, v = radius * math.cos(a), radius * math.sin(a)
        pts.append((cx + u, cy, cz + v) if upright else (cx + u, cy + v * math.cos(tilt), cz + v * math.sin(tilt)))
    for i in range(n):
        if upright:
            beam(m, role, pts[i], pts[(i + 1) % n], width, thick)
        else:
            beam(m, role, pts[i], pts[(i + 1) % n], width, thick)
    return pts


def flank(pair, y, share, side, out=0.0):
    """A point on the side of a loft_y body: share -1 is its bottom edge, 1 its top."""
    r = ring_at(*pair, y)
    return (side * (r[3] / 2 + out), y, r[2] + share * r[4] / 2)


def constellation(m, points, normal, dot=0.13, line=0.05, big=()):
    """Stars joined by thin lines, drawn on a surface facing normal ("x", "-x", "y" or "z")."""
    n = {"x": (1, 0, 0), "-x": (-1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[normal]

    def lift(p, k):
        return tuple(p[i] + n[i] * k for i in range(3))

    for a, b in zip(points, points[1:]):
        if normal == "z":
            beam(m, "StarLine", lift(a, 0.015), lift(b, 0.015), line, 0.04)
        else:
            beam(m, "StarLine", lift(a, 0.015), lift(b, 0.015), 0.04, line)
    for i, p in enumerate(points):
        star_on(m, "Sparkle", lift(p, 0.035), dot * (1.7 if i in big else 1.0), normal.lstrip("-"))


def sprinkle(m, pair, sides, ys, shares, rng, size=(0.06, 0.1)):
    """Little stars scattered over the sides (and top, side 0) of a loft_y body."""
    for y in ys:
        for side in sides:
            if side == 0:
                r = ring_at(*pair, y)
                x = rng.uniform(-0.38, 0.38) * r[3]
                m.block("Sparkle", x, y, r[2] + r[4] / 2 + 0.01, *(rng.uniform(*size),) * 3)
            else:
                p = flank(pair, y + rng.uniform(-0.15, 0.15), rng.uniform(*shares), side, 0.01)
                s = rng.uniform(*size)
                m.block("Sparkle", *p, s, s, s)


# ---------------------------------------------------------------------- the starfall face


def star_eye(m, x, y, z, size, face=0, lid=0.3, lid_role="Body", look=0.0, mirror=1):
    """A long almond eye, dark as the night sky, with a glowing star for an iris, its top tucked under a level
    lid of skin with a dark lash line. face 0: on a front face, y is that face; face -1/1: on the left/right
    side face, x is that face. mirror flips which way the little twinkle beside the iris sits (pass the eye's
    side for front eyes)."""
    w, h, d = size * 1.4, size * 0.92, size * 0.4

    def at(u, n):
        return (x + u, y + n) if face == 0 else (x + face * n, y + u)

    def lens(role, u0, u1, n, h0, h1, depth, zc=z):
        a, b = at(u0, n), at(u1, n)
        if face == 0:
            m.loft_x(role, (a[0], a[1], zc, depth, h0), (b[0], b[1], zc, depth, h1))
        else:
            m.loft_y(role, (a[1], a[0], zc, depth, h0), (b[1], b[0], zc, depth, h1))

    n0 = -d / 2 + 0.03
    lens("Pupil", -w / 2, 0, n0, h * 0.3, h, d)
    lens("Pupil", 0, w / 2, n0, h, h * 0.3, d)
    tilt = (0, 0, 0) if face == 0 else (0, 0, math.pi / 2)
    outer = h * 0.46
    iz = z - h * 0.1
    c = at(look * w * 0.2, 0.035)
    star_prism(m, "EyeGlow", (c[0], c[1], iz), outer, outer * 0.3, 0.04, tilt, 4)
    t = at(look * w * 0.2 + mirror * w * 0.27, 0.03)
    star_prism(m, "Sparkle", (t[0], t[1], iz - outer * 0.45), outer * 0.28, outer * 0.09, 0.03, tilt, 4)
    if lid:
        top = z + h / 2 + size * 0.06
        bottom = z + h / 2 - h * lid
        lens(lid_role, -w / 2 - size * 0.05, w / 2 + size * 0.05, n0 + 0.015, top - bottom, top - bottom, d + 0.03,
             (top + bottom) / 2)
        lens("Pupil", -w / 2 - size * 0.05, w / 2 + size * 0.05, n0 + 0.02, size * 0.07, size * 0.07, d + 0.05, bottom)


def star_mouth(m, front, mouth_z, skull_w, length, snout_w, upper_h, lower_h, gap=0.05, upper="Body", lower="Belly",
               rng=None, on_jaw=None):
    """A quiet closed mouth with no teeth, the lower jaw on a Jaw bone hinged at the back of the mouth. Inside
    is the night sky with stars on the roof and the floor, seen only when it opens to sing. Call it on the
    head's bone. Returns the snout's tip and its top height along it."""
    rng = rng or random.Random(0)
    head_bone = m.bone
    upper_z = mouth_z + gap / 2 + upper_h / 2
    lower_z = mouth_z - gap / 2 - lower_h / 2
    back = (front - 0.05, 0, upper_z + upper_h * 0.1, skull_w * 0.94, upper_h * 1.2)
    tip = (front + length, 0, upper_z, snout_w, upper_h)
    m.loft_y(upper, back, tip)
    m.block("Mouth", 0, front + length * 0.42, mouth_z + gap * 0.05, snout_w * 0.84, length * 0.86, gap + 0.04)
    m.block("Mouth", 0, front + 0.05, mouth_z - lower_h * 0.45, snout_w * 0.78, 0.12, gap + lower_h * 0.9)
    roof = mouth_z + gap / 2 - 0.005
    for _ in range(4):
        s = rng.uniform(0.04, 0.07)
        m.block("Sparkle", rng.uniform(-0.3, 0.3) * snout_w, front + rng.uniform(0.15, 0.75) * length, roof - s / 2, s, s, s)

    m.use("Jaw", (0, front - 0.05, mouth_z), head_bone)
    lower_length = length * 0.92
    jaw_back = (front - 0.05, 0, lower_z, skull_w * 0.85, lower_h)
    jaw_tip = (front + lower_length, 0, lower_z, snout_w * 0.9, lower_h)
    m.loft_y(lower, jaw_back, jaw_tip)
    floor = mouth_z - gap / 2 + 0.01
    m.block("Mouth", 0, front + lower_length * 0.45, floor, snout_w * 0.7, lower_length * 0.8, 0.05)
    for _ in range(5):
        s = rng.uniform(0.04, 0.08)
        m.block("Sparkle", rng.uniform(-0.28, 0.28) * snout_w, front + rng.uniform(0.15, 0.8) * lower_length, floor + 0.03, s, s, s * 0.6)
    if on_jaw:
        on_jaw(m, front, mouth_z, gap, lower_length, lower_z - lower_h / 2)
    m.bone = head_bone
    return {"tip": front + length, "top": lambda y: top_of((back, tip), y), "lower_z": lower_z}


def slim_legs(m, x_front, y_front, x_back, y_back, top, width, hoof="Claw"):
    """Four long thin legs with hooves, named as the game's four-legged walk expects."""
    knee = top * 0.5
    for x_abs, y, end in ((x_front, y_front, "Front"), (x_back, y_back, "Back")):
        for side in (-1, 1):
            x = side * x_abs
            m.use(end + ("L" if side < 0 else "R"), (x, y, top))
            m.loft_z("Body", (knee, x, y, width * 0.72, width * 0.8), (top + 0.25, x, y, width * 1.35, width * 1.5))
            m.loft_z("Body", (0.3, x, y + 0.03, width * 0.55, width * 0.6), (knee + 0.05, x, y, width * 0.72, width * 0.8))
            m.block(hoof, x, y + 0.05, 0.17, width * 0.78, width * 0.95, 0.34)
    m.bone = "Spine"


# ---------------------------------------------------------------------- the common ones


def craterback():
    """A slow, heavy grazer with a little crater on its back where a star came down: the star is still stuck
    in it, crystals have grown round it, and moon dust is piled up round the rim. Long calm face, heavy lids."""
    m = monster("dino_Craterback", Body="#8a91c6", Accent="#5b6699", Belly="#c3cbee", Claw="#2e3560",
                Dust=DUST, DustDark=DUST_DARK, Scorch=SCORCH, Crystal=CRYSTAL, CrystalGlow=CRYSTAL_GLOW, StarGlow=STAR_GLOW)
    rng = random.Random(1)
    m.joint("Spine", (0, 0, 1.4))
    quad_legs(m, 1.2, 1.35, 1.2, -1.45, 1.05, 0.74)
    m.loft_y("Body", (-2.1, 0, 1.3, 2.5, 0.9), (2.0, 0, 1.35, 2.6, 1.0))
    # The shell, a skirt of moon dust round its edge, and the crater on top.
    oval(m, "Belly", 0, -0.1, 0.85, 1.12, 1.98, 2.62, 2.02, 2.68)
    oval(m, "Accent", 0, -0.1, 1.12, 2.05, 2.0, 2.66, 1.92, 2.56)
    oval(m, "Accent", 0, -0.1, 2.05, 2.5, 1.92, 2.56, 1.55, 2.08)
    oval(m, "Scorch", 0, -0.1, 2.48, 2.56, 1.25, 1.7, 1.2, 1.64)
    for i in range(14):
        a = i * math.tau / 14 + rng.uniform(-0.1, 0.1)
        s = rng.uniform(0.55, 0.78)
        hgt = rng.uniform(0.32, 0.58)
        m.block("Dust" if i % 3 else "DustDark", math.cos(a) * 1.42, -0.1 + math.sin(a) * 1.86, 2.45 + hgt / 2, s, s * 1.1, hgt)
    for x, y, height, lean in ((-0.65, 0.35, 1.0, (-0.25, 0.1)), (0.6, 0.6, 0.7, (0.2, 0.15)), (-0.35, -0.95, 0.8, (-0.1, -0.25)),
                               (0.55, -0.7, 0.55, (0.15, -0.1))):
        crystal(m, "Crystal", "CrystalGlow", x, y, 2.6, height, 0.17, lean)
    star_prism(m, "StarGlow", (0.05, -0.1, 3.05), 0.62, 0.28, 0.32, (0.25, 0.35, 0.2), 5)
    # Dust craters pocking the sides of the shell.
    for a, z in ((0.5, 1.6), (1.4, 1.8), (2.6, 1.55), (3.7, 1.75), (4.6, 1.5), (5.6, 1.7)):
        m.block("DustDark", math.cos(a) * 1.99, -0.1 + math.sin(a) * 2.63, z, 0.4, 0.4, 0.3)
    tail(m, (-2.4, 1.25, 0.7, 0.55), (-3.3, 0.95, 0.25, 0.2), 2)

    m.use("Neck", (0, 2.05, 1.5))
    m.loft_y("Body", (1.85, 0, 1.42, 1.3, 0.95), (2.7, 0, 1.55, 1.1, 0.9))
    m.stretch("Body", "Spine")
    w, d, h = 1.45, 1.25, 1.15
    yc, zc = 3.2, 1.72
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    m.block("Accent", 0, yc - 0.08, zc + h / 2 + 0.08, w * 0.88, d * 0.82, 0.2)  # a stony cap
    for side in (-1, 1):
        crystal(m, "Crystal", "CrystalGlow", side * 0.35, yc - 0.25, zc + h / 2 + 0.16, 0.42, 0.09, (side * 0.12, -0.12))
    snout = star_mouth(m, front, zc - 0.4, w, 0.62, 1.1, 0.38, 0.3, 0.05, rng=rng)
    for side in (-1, 1):
        y = snout["tip"] - 0.16
        m.block("DustDark", side * 0.25, y, snout["top"](y) + 0.01, 0.16, 0.18, 0.05)
        star_eye(m, side * 0.4, front, zc + 0.3, 0.44, 0, lid=0.32, mirror=side)
        for dy, dz in ((-0.1, -0.15), (-0.35, -0.3), (-0.6, -0.12)):  # star freckles on its cheeks
            m.block("Sparkle", side * (w / 2 + 0.01), front + dy, zc + dz, 0.05, 0.08, 0.08)
    m.head_centre = (0, front + 0.25, zc)
    return m


def stargazer():
    """A tall wading bird on stilt legs that never stops looking up: its long beak points at the sky, its
    folded wings carry constellations, and gold stars hang on the tips of its crest and its tail plumes."""
    m = monster("dino_Stargazer", Body="#2f3b7c", Accent="#1d2558", Belly="#c3cbee", Claw="#9aa3d6", Beak="#d3d8e8",
                BeakDark="#7d859e", Plume=DUST, StarGlow=STAR_GLOW)
    rng = random.Random(2)
    m.joint("Spine", (0, -0.1, 3.3))
    biped_legs(m, 0.42, -0.1, 3.0, 0.62, 0.95, 0.2, 1.1, 0.18)
    torso = ((-0.9, 0, 3.4, 0.95, 0.95), (0.35, 0, 3.55, 1.45, 1.4))
    m.loft_y("Body", *torso)
    m.loft_y("Body", (0.35, 0, 3.55, 1.45, 1.4), (0.95, 0, 3.8, 1.0, 1.05))
    m.loft_y("Belly", (-0.55, 0, 3.0, 0.8, 0.4), (0.98, 0, 3.55, 0.82, 0.75))
    tail(m, (-0.85, 3.45, 0.6, 0.5), (-1.5, 3.6, 0.32, 0.25), 1)
    m.bone = "Tail1"
    for dx, drop in ((-0.25, 0.0), (0.0, 0.25), (0.25, 0.0)):  # long tail plumes, gold stars on their tips
        end = (dx * 2.2, -3.4, 2.75 - drop)
        beam(m, "Plume", (dx * 0.6, -1.35, 3.6), (dx * 1.6, -2.6, 3.35 - drop * 0.5), 0.2, 0.1, 0.14)
        beam(m, "Plume", (dx * 1.6, -2.6, 3.35 - drop * 0.5), end, 0.14, 0.08, 0.05)
        sparkle(m, "StarGlow", end[0], end[1] - 0.1, end[2] - 0.05, 0.24)
    for side in (-1, 1):  # folded wings with a constellation each, on the Wing bones
        m.use("WingL" if side < 0 else "WingR", (side * 0.7, 0.4, 3.85))
        a, b = (0.6, side * 0.75, 3.72, 0.16, 0.95), (-1.05, side * 0.66, 3.55, 0.14, 0.78)
        m.loft_y("Accent", a, b)
        m.loft_y("Accent", b, (-2.05, side * 0.5, 3.35, 0.08, 0.22))
        pts = [(y, dz) for y, dz in ((0.35, 0.2), (-0.1, -0.12), (-0.55, 0.18), (-0.95, -0.05), (-1.45, 0.08))]
        stars = []
        for y, dz in pts:
            yy = max(y, -1.05)
            r = ring_at(a, b, yy)
            stars.append((r[1] + side * 0.085, y, r[2] + dz))
        constellation(m, stars, "x" if side > 0 else "-x", 0.11, 0.045, big=(2,))
    m.bone = "Spine"

    m.use("Neck", (0, 0.75, 3.95))
    beam(m, "Body", (0, 0.72, 3.85), (0, 1.05, 4.75), 0.56, None, 0.48)
    m.stretch("Body", "Spine")
    beam(m, "Body", (0, 1.05, 4.75), (0, 0.9, 5.55), 0.48, None, 0.42)
    m.block("Body", 0, 1.05, 4.75, 0.46, 0.46, 0.46)
    beam(m, "Body", (0, 0.9, 5.55), (0, 1.05, 6.2), 0.42, None, 0.4)
    m.block("Body", 0, 0.9, 5.55, 0.4, 0.4, 0.4)
    w, d, h = 0.72, 0.95, 0.7
    yc, zc = 1.2, 6.45
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    m.block("Belly", 0, yc + 0.08, zc - h / 2 + 0.06, w * 0.86, d * 0.8, 0.14)
    # The beak, pointing up at the sky; the lower half on the Jaw bone.
    up = Vector((0, 1.0, 0.62)).normalized()
    across = Vector((0, -up.z, up.y))  # perpendicular, pointing up and back
    base = Vector((0, front - 0.08, zc - 0.08))
    length = 1.45
    beam(m, "Beak", tuple(base + across * 0.09), tuple(base + up * length + across * 0.02), 0.34, 0.2, 0.05)
    beam(m, "BeakDark", tuple(base + up * 0.2 + across * 0.2), tuple(base + up * 0.75 + across * 0.16), 0.18, 0.04, 0.12)
    beam(m, "Mouth", tuple(base - across * 0.02), tuple(base + up * (length - 0.15) - across * 0.01), 0.24, 0.06, 0.04)
    m.use("Jaw", tuple(base - across * 0.05), "Head")
    beam(m, "Beak", tuple(base - across * 0.11), tuple(base + up * (length - 0.12) - across * 0.06), 0.3, 0.14, 0.05)
    for k in range(3):
        t = 0.25 + 0.2 * k
        p = base + up * (length * t) - across * 0.035
        m.block("Sparkle", p.x + (k - 1) * 0.04, p.y, p.z, 0.05, 0.05, 0.05)
    m.bone = "Head"
    for side in (-1, 1):
        star_eye(m, side * w / 2, yc + 0.16, zc + 0.08, 0.36, side, lid=0.26, look=0.6)
    for dx, height in ((-0.14, 0.95), (0.0, 1.25), (0.14, 0.95)):  # the crest, sweeping back, star-tipped
        end = (dx * 2.6, yc - 0.95, zc + height)
        beam(m, "Plume", (dx, yc - 0.2, zc + h / 2 - 0.05), end, 0.12, 0.08, 0.05)
        sparkle(m, "StarGlow", end[0], end[1] - 0.05, end[2] + 0.08, 0.18)
    m.head_centre = (0, front + 0.3, zc + 0.15)
    return m


def comet_trike():
    """A trike whose frill is the head of a comet: a dark disc ringed with light, its glowing tail streaming
    back over the trike's body. Crystal horns, a pale beak and a constellation down each flank."""
    m = monster("dino_CometTrike", Body="#3a4a92", Accent="#1f2759", Belly="#a9b8ee", Claw="#1b2150", Beak="#d3d8e8",
                Crystal=CRYSTAL, CrystalGlow=CRYSTAL_GLOW, CometHead="#fff0a8", CometTail="#7fe6ff")
    rng = random.Random(3)
    m.joint("Spine", (0, -0.3, 2.2))
    quad_legs(m, 0.95, 0.85, 0.95, -1.4, 1.45, 0.78)
    body = ((-2.0, 0, 2.1, 1.9, 1.7), (1.2, 0, 2.35, 2.35, 2.05))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-1.5, 0, 1.4, 1.6, 0.4), (1.1, 0, 1.5, 1.95, 0.5))
    tail(m, (-1.9, 2.15, 1.0, 0.85), (-3.9, 1.6, 0.2, 0.2), 3)
    for side in (-1, 1):
        pts = [flank(body, y, s, side, 0.0) for y, s in ((0.75, 0.25), (0.15, 0.55), (-0.45, 0.2), (-1.05, 0.5), (-1.55, 0.05))]
        constellation(m, pts, "x" if side > 0 else "-x", 0.13, 0.05, big=(1, 3))
    # The comet's tail, streaming from behind the frill back over the body: it stretches from the head bone
    # to the spine, so it follows the head as it turns.
    for k, a in enumerate((0.45, 0.95, 1.57, 2.19, 2.69)):
        r = 1.05
        start = (math.cos(a) * r * 0.9, 0.8, 3.15 + math.sin(a) * r * 0.75)
        mid = (math.cos(a) * 0.95, -1.0, 3.55 + math.sin(a) * 0.55)
        end = (math.cos(a) * 0.55, -3.0 - 0.35 * math.sin(a), 3.05 + math.sin(a) * 0.5)
        width = 0.5 if k == 2 else 0.36
        beam(m, "CometHead", start, mid, width, width * 0.55, width * 0.7)
        m.groups["CometHead"][-8:-4] = ["Head"] * 4
        beam(m, "CometTail", mid, end, width * 0.7, width * 0.38, 0.04)

    m.use("Neck", (0, 1.1, 2.45))
    m.loft_y("Body", (1.0, 0, 2.35, 1.5, 1.35), (1.55, 0, 2.45, 1.3, 1.2))
    m.stretch("Body", "Spine")
    w, d, h = 1.5, 1.35, 1.3
    yc, zc = 2.05, 2.5
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    # The frill: the comet's head, a dark disc ringed with light, with a few stars on it.
    fy, fz = yc - 0.5, zc + 0.75
    disc(m, "Accent", 0, fy, fz, 1.6, 0.22, 12)
    ring(m, "CometHead", (0, fy + 0.05, fz), 1.62, 0.26, 0.2, upright=True, n=24)
    for x, z, s in ((-0.85, 0.55, 0.12), (0.7, 0.85, 0.16), (-0.35, 1.15, 0.1), (1.05, 0.1, 0.1), (-1.1, -0.15, 0.09), (0.25, 1.3, 0.08)):
        star_on(m, "Sparkle", (x, fy + 0.13, fz + z - 0.15), s)
    snout = star_mouth(m, front, zc - 0.42, w, 0.85, 0.95, 0.38, 0.3, 0.05, rng=rng)
    tip = snout["tip"]
    y = tip - 0.45
    crystal(m, "Crystal", "CrystalGlow", 0, y, snout["top"](y) - 0.05, 0.55, 0.13, (0, 0.12), sides=4)
    for side in (-1, 1):
        beam(m, "Crystal", (side * 0.45, yc + 0.15, zc + 0.5), (side * 0.6, front + 0.6, zc + 1.35), 0.3, None, 0.13)
        beam(m, "CrystalGlow", (side * 0.6, front + 0.6, zc + 1.35), (side * 0.66, front + 0.95, zc + 1.75), 0.13, None, 0.03)
        star_eye(m, side * 0.4, front, zc + 0.3, 0.44, 0, lid=0.3, mirror=side)
    m.head_centre = (0, front + 0.4, zc + 0.2)
    return m


# ---------------------------------------------------------------------- the rare ones


def ringhorn():
    """A tall stag with a coat like the night sky, dotted with stars, over a pale moon-coloured body. Its
    antlers are crystal, a planet's ring floats round them with two little moons on it, and it has a star on
    its brow."""
    m = monster("dino_Ringhorn", Body="#b4bce6", Accent="#28316c", Belly="#e7eafb", Claw="#28316c", Crystal=CRYSTAL,
                CrystalGlow=CRYSTAL_GLOW, Halo="#ffd96b", Orb="#d6f8ff", StarGlow=STAR_GLOW)
    rng = random.Random(4)
    m.joint("Spine", (0, -0.2, 3.1))
    slim_legs(m, 0.5, 0.95, 0.5, -1.25, 2.75, 0.42)
    body = ((-1.6, 0, 3.05, 1.15, 1.1), (1.15, 0, 3.2, 1.3, 1.3))
    m.loft_y("Body", *body)
    coat = ((-1.63, 0, 3.32, 1.21, 0.6), (1.18, 0, 3.55, 1.36, 0.66))
    m.loft_y("Accent", *coat)
    m.loft_y("Belly", (-1.2, 0, 2.52, 0.9, 0.2), (1.0, 0, 2.58, 1.05, 0.25))
    sprinkle(m, coat, (-1, 0, 1), [-1.45 + 0.32 * k for k in range(9)], (-0.05, 0.85), rng, (0.06, 0.11))
    for y, x in ((-0.9, 0.25), (0.35, -0.2)):
        star_on(m, "StarGlow", (x, y, top_of(coat, y) + 0.02), 0.16, "z")
    tail(m, (-1.55, 3.4, 0.4, 0.4), (-2.05, 3.15, 0.2, 0.3), 1)
    m.bone = "Tail1"
    m.block("Belly", 0, -1.95, 3.05, 0.3, 0.3, 0.42)
    m.bone = "Spine"

    m.use("Neck", (0, 0.9, 3.45))
    m.loft_z("Body", (3.2, 0, 0.95, 0.75, 0.85), (4.75, 0, 1.55, 0.5, 0.6))
    m.stretch("Body", "Spine")
    m.loft_z("Accent", (3.35, 0, 0.56, 0.34, 0.24), (4.8, 0, 1.27, 0.26, 0.2))  # a dark mane down the back of the neck
    m.loft_z("Belly", (3.1, 0, 1.4, 0.7, 0.3), (4.2, 0, 1.75, 0.42, 0.22))  # pale throat
    w, d, h = 0.72, 0.95, 0.72
    yc, zc = 1.85, 5.0
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = star_mouth(m, front, zc - 0.2, w, 0.75, 0.48, 0.3, 0.2, 0.04, lower="Belly", rng=rng)
    m.block("Accent", 0, snout["tip"] - 0.08, zc + 0.02, 0.3, 0.18, 0.12)  # a dark nose
    star_on(m, "StarGlow", (0, front + 0.03, zc + 0.24), 0.17)  # the star on its brow
    for side in (-1, 1):
        star_eye(m, side * w / 2, yc + 0.17, zc + 0.08, 0.34, side, lid=0.3, look=0.4)
        beam(m, "Body", (side * 0.3, yc - 0.2, zc + 0.28), (side * 0.78, yc - 0.32, zc + 0.42), 0.24, 0.1, 0.14)  # ears
        beam(m, "Belly", (side * 0.34, yc - 0.17, zc + 0.3), (side * 0.7, yc - 0.27, zc + 0.41), 0.13, 0.11, 0.07)
        # Crystal antlers.
        base, knee, top = (side * 0.2, yc - 0.15, zc + 0.36), (side * 0.45, yc - 0.32, zc + 1.0), (side * 0.75, yc - 0.5, zc + 1.65)
        for p, q, w0, w1 in ((base, knee, 0.2, 0.16), (knee, top, 0.16, 0.12), (top, (side * 0.92, yc - 0.32, zc + 2.2), 0.12, 0.06),
                             (knee, (side * 0.72, yc + 0.12, zc + 1.42), 0.11, 0.05), (top, (side * 1.22, yc - 0.72, zc + 1.95), 0.1, 0.05)):
            beam(m, "Crystal", p, q, w0, None, w1)
        for p in ((side * 0.92, yc - 0.32, zc + 2.2), (side * 0.72, yc + 0.12, zc + 1.42), (side * 1.22, yc - 0.72, zc + 1.95)):
            gem(m, "CrystalGlow", *p, 0.07, 0.18, 0.04)
    # The planet's ring floating round the antlers, with two moons on it.
    pts = ring(m, "Halo", (0, yc - 0.3, zc + 1.45), 1.3, 0.15, 0.06, tilt=0.28, n=22)
    for i, r in ((3, 0.17), (14, 0.12)):
        ball(m, "Orb", *pts[i], r, 6, 4)
    m.head_centre = (0, front + 0.35, zc + 0.3)
    return m


def nebulasaur():
    """A long-necked giant whose body is a piece of the night sky: stars all over it, a band of pink nebula
    glowing across each flank like the Milky Way, constellations on its legs and gold stars standing along
    its back. A small, calm head way up at the top of a long neck."""
    m = monster("dino_Nebulasaur", Body="#262e6c", Accent="#151a40", Belly="#414a98", Claw="#151a40", Nebula="#5b3d9a",
                NebulaDeep="#3a2f7a", NebulaGlow=NEBULA_GLOW, StarGlow=STAR_GLOW)
    rng = random.Random(5)
    m.joint("Spine", (0, -0.4, 3.6))
    quad_legs(m, 1.15, 1.0, 1.15, -1.9, 2.7, 1.0)
    body = ((-2.7, 0, 3.4, 2.4, 2.3), (1.5, 0, 3.75, 2.8, 2.7))
    hump = ((-2.45, 0, 4.62, 1.9, 0.3), (1.25, 0, 5.2, 2.2, 0.34))
    m.loft_y("Body", *body)
    m.loft_y("Body", *hump)
    m.loft_y("Belly", (-2.2, 0, 2.2, 2.0, 0.35), (1.3, 0, 2.35, 2.35, 0.45))
    sprinkle(m, body, (-1, 1), [-2.5 + 0.22 * k for k in range(19)], (-0.7, 0.95), rng, (0.05, 0.1))
    sprinkle(m, hump, (0,), [-2.3 + 0.25 * k for k in range(14)], (0, 0), rng, (0.06, 0.1))
    for side in (-1, 1):
        # The nebula: a band of cloud rising across the flank, violet outside, pink glowing at its heart.
        def band(t):
            return 0.95 - 3.3 * t, -0.5 + 1.1 * t + 0.1 * math.sin(t * 9)

        for t in [k / 11 for k in range(12)]:
            y, share = band(t)
            y += rng.uniform(-0.1, 0.1)
            share += rng.uniform(-0.08, 0.08)
            swell = math.sin(math.pi * (0.1 + 0.85 * t))
            m.block("NebulaDeep", *flank(body, y, share, side, 0.02), 0.06, (0.8 + 0.45 * swell) * rng.uniform(0.85, 1.15),
                    (0.6 + 0.5 * swell) * rng.uniform(0.85, 1.15))
            m.block("Nebula", *flank(body, y + rng.uniform(-0.1, 0.15), share + rng.uniform(-0.05, 0.08), side, 0.04), 0.06,
                    0.45 + 0.3 * swell, 0.32 + 0.28 * swell)
        for t, lift, size in ((0.28, 0.1, 0.7), (0.43, -0.04, 1.0), (0.58, 0.09, 0.8), (0.72, -0.02, 0.5)):
            y, share = band(t)
            m.block("NebulaGlow", *flank(body, y + 0.1, share + lift, side, 0.06), 0.06, 0.32 * size, 0.24 * size)
        for p, s in (((0.4, 0.75), 0.2), ((-1.6, -0.2), 0.24), ((-0.4, 0.15), 0.16)):
            star_on(m, "Sparkle", flank(body, p[0], p[1], side, 0.09), s, "x")
        for leg, y in (("FrontL" if side < 0 else "FrontR", 1.0), ("BackL" if side < 0 else "BackR", -1.9)):
            m.bone = leg
            x = side * (1.15 + 0.52)
            constellation(m, [(x, y + 0.1, 0.8), (x, y - 0.1, 1.5), (x, y + 0.15, 2.2)], "x" if side > 0 else "-x", 0.1, 0.04)
        m.bone = "Spine"
    tail(m, (-2.6, 3.55, 1.5, 1.4), (-7.2, 2.0, 0.22, 0.22), 3)
    for bone, y, z, s in (("Tail1", -3.4, 3.3, 0.12), ("Tail2", -4.9, 2.8, 0.1), ("Tail3", -6.2, 2.35, 0.08)):
        m.bone = bone
        for side in (-1, 1):
            m.block("Sparkle", side * 0.5 * (7.4 + y) / 4.8, y, z, s, s, s)
    # Gold stars standing along its back, shrinking towards the tail.
    for bone, y, size in (("Spine", 0.55, 0.42), ("Spine", -0.75, 0.5), ("Spine", -2.0, 0.4), ("Tail1", -3.35, 0.3), ("Tail2", -4.75, 0.22)):
        m.bone = bone
        if y > -2.45:
            z = top_of(hump, y)
        else:
            t = (-2.6 - y) / 4.6
            z = 3.55 + (2.0 - 3.55) * t + (1.4 + (0.22 - 1.4) * t) / 2
        star_prism(m, "StarGlow", (0, y, z + size * 0.78), size, size * 0.45, 0.22, (0, 0, math.pi / 2), 5)
    m.bone = "Spine"

    m.use("Neck", (0, 1.3, 4.5))
    beam(m, "Body", (0, 1.15, 4.4), (0, 2.15, 6.4), 1.2, None, 0.9)
    m.stretch("Body", "Spine")
    beam(m, "Body", (0, 2.15, 6.4), (0, 2.55, 8.1), 0.9, None, 0.72)
    m.block("Body", 0, 2.15, 6.4, 0.86, 0.86, 0.86)
    beam(m, "Belly", (0, 1.7, 4.5), (0, 2.6, 6.35), 0.75, 0.16, 0.6)  # its throat
    beam(m, "Belly", (0, 2.6, 6.35), (0, 2.92, 7.9), 0.6, 0.14, 0.5)
    for p in ((0.36, 1.75, 5.3), (-0.4, 2.05, 5.9), (0.3, 2.35, 7.0), (-0.28, 2.45, 7.6), (0.4, 1.45, 4.8), (-0.35, 1.5, 4.7)):
        m.block("Sparkle", *p, 0.09, 0.09, 0.09)
    w, d, h = 0.95, 1.05, 0.95
    yc, zc = 2.85, 8.5
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    star_mouth(m, front, zc - 0.3, w, 0.7, 0.72, 0.26, 0.22, 0.04, rng=rng)
    for side in (-1, 1):
        star_eye(m, side * 0.27, front, zc + 0.2, 0.32, 0, lid=0.3, mirror=side)
    for x in (-0.16, 0.0, 0.16):  # three stars in a row across its brow
        star_on(m, "Sparkle", (x, front + 0.02, zc + 0.4 + x * 0.1), 0.06)
    m.head_centre = (0, front + 0.3, zc)
    return m


def star_sovereign():
    """Starfall Crater's boss, and the last monster in the game: a towering king of the stars. A calm,
    moon-pale face with heavy-lidded star eyes, a third star on its brow and a beard of stardust; a gold crown
    with a crystal in every point and a halo of light behind its head; a cape full of stars with a nebula
    glowing on it; a gold staff topped with a star in one hand and a little moon floating over the other;
    crystals drifting round its shoulders."""
    m = monster("dino_StarSovereign", Body="#c7cdf0", Accent="#232a62", Belly="#e8ebfb", Claw="#9aa3d6", Trim=STAR,
                TrimDark=STAR_DARK, DustDark=DUST_DARK, Beard=DUST, StarGlow=STAR_GLOW, CrystalGlow=CRYSTAL_GLOW,
                Halo="#ffe27a", NebulaGlow=NEBULA_GLOW, Orb="#e4fbff")
    rng = random.Random(6)
    m.joint("Spine", (0, 0, 3.4))
    biped_legs(m, 0.72, 0.0, 3.1, 1.1, 1.3, 0.78, 1.3, 0.4, claw=False)
    for side in (-1, 1):  # gold toe caps
        m.bone = "ShinL" if side < 0 else "ShinR"
        m.block("Trim", side * 0.72, 0.85, 0.22, 1.2, 0.3, 0.44)
    m.bone = "Spine"
    # The robe from the waist down, its gold hem, the belt and its star buckle.
    m.loft_z("Accent", (1.9, 0, 0.0, 3.1, 2.15), (4.25, 0, 0.0, 2.6, 1.8))
    m.loft_z("Trim", (1.82, 0, 0.0, 3.16, 2.21), (2.05, 0, 0.0, 3.13, 2.18))
    m.loft_z("Body", (4.1, 0, 0.0, 2.55, 1.75), (6.45, 0, 0.0, 3.5, 2.15))  # the chest
    m.block("Trim", 0, 0, 4.2, 2.68, 1.9, 0.32)
    star_on(m, "StarGlow", (0, 0.98, 4.2), 0.3, points=5, inner=0.45, depth=0.12)
    # A V of night sky down its chest, edged in gold.
    for side in (-1, 1):
        m.loft_z("Accent", (4.3, side * 0.08, 0.98, 0.2, 0.06), (6.4, side * 0.75, 1.08, 0.75, 0.06))
        beam(m, "Trim", (side * 0.06, 1.1, 4.32), (side * 1.12, 1.11, 6.4), 0.05, 0.1)
    for p in ((0.3, 1.13, 5.9), (-0.42, 1.13, 6.15), (0.12, 1.12, 5.2)):
        m.block("Sparkle", *p, 0.08, 0.04, 0.08)
    # The cape, from the shoulders to the ground, full of stars with a nebula glowing in it.
    cape = ((0.45, 0, -1.25, 3.5, 0.22), (6.4, 0, -0.98, 3.55, 0.3))
    m.loft_z("Accent", *cape)
    m.loft_z("Trim", (0.38, 0, -1.26, 3.56, 0.24), (0.62, 0, -1.25, 3.55, 0.24))
    for _ in range(26):
        z = rng.uniform(1.0, 6.0)
        s = rng.uniform(0.08, 0.15)
        y = -1.25 + (z - 0.45) / 5.95 * 0.27 - 0.13
        m.block("Sparkle", rng.uniform(-1.6, 1.6), y, z, s, 0.05, s)
    for x, z, w, hgt in ((-0.5, 3.6, 1.6, 0.9), (0.4, 2.6, 1.1, 0.6), (0.9, 4.4, 0.7, 0.5)):
        m.block("NebulaGlow", x, -1.25 + (z - 0.45) / 5.95 * 0.27 - 0.13, z, w, 0.05, hgt)
    constellation(m, [(-1.2, -1.36, 5.4), (-0.6, -1.36, 5.0), (0.1, -1.36, 5.55), (0.7, -1.36, 4.9), (1.25, -1.36, 5.3)], "y", 0.16, 0.06, big=(2,))
    # Shoulder plates, night blue edged in gold.
    for side in (-1, 1):
        m.block("Accent", side * 1.62, -0.05, 6.35, 1.15, 2.0, 0.55)
        m.block("Trim", side * 1.62, -0.05, 6.06, 1.2, 2.05, 0.12)
        star_on(m, "StarGlow", (side * 1.62, -0.05, 6.64), 0.24, "z", points=5, inner=0.45)

    # Crystals drifting round its shoulders, on the Wing bones so they bob as it walks.
    for side in (-1, 1):
        m.use("WingL" if side < 0 else "WingR", (side * 1.7, -0.2, 6.6))
        for dx, dy, z, r in ((1.05, -0.5, 7.5, 0.22), (1.45, 0.25, 6.75, 0.18), (1.0, -1.05, 6.4, 0.15)):
            gem(m, "CrystalGlow", side * (1.7 + dx), dy, z, r, r * 2.4, r * 2.0, 4, 0.3 * side)
    m.bone = "Spine"
    # Arms: the right holds the staff, a little moon floats over the left hand.
    for side in (-1, 1):
        arm = "ArmL" if side < 0 else "ArmR"
        sx = side * 1.75
        m.use(arm, (sx, 0.0, 6.05))
        beam(m, "Body", (sx, 0.0, 6.2), (side * 1.98, 0.25, 4.3), 0.85, None, 0.72)
        beam(m, "Accent", (side * 1.98, 0.25, 4.45), (side * 2.05, 0.6, 3.0), 0.92, None, 0.86)
        m.block("Trim", side * 2.05, 0.6, 3.0, 0.96, 0.96, 0.22)
        hand = (side * 2.07, 0.7, 2.6)
        m.block("Body", *hand, 0.7, 0.72, 0.7)
        if side > 0:
            m.block("Trim", hand[0], hand[1] + 0.05, 4.0, 0.2, 0.2, 7.4)
            m.block("TrimDark", hand[0], hand[1] + 0.05, 0.35, 0.3, 0.3, 0.3)
            ring(m, "Trim", (hand[0], hand[1] + 0.05, 8.25), 0.62, 0.12, 0.14, upright=True, n=14)
            star_on(m, "StarGlow", (hand[0], hand[1] + 0.05, 8.25), 0.52, points=5, inner=0.45, depth=0.2)
        else:
            ball(m, "Orb", hand[0], hand[1] + 0.25, hand[2] + 0.95, 0.32, 8, 5)
            for k in range(3):
                a = k * math.tau / 3
                m.block("Sparkle", hand[0] + math.cos(a) * 0.55, hand[1] + 0.25 + math.sin(a) * 0.55, hand[2] + 0.8, 0.07, 0.07, 0.07)
    m.bone = "Spine"

    m.use("Neck", (0, 0.1, 6.4))
    m.loft_z("Body", (6.3, 0, 0.1, 1.0, 0.9), (6.85, 0, 0.15, 0.92, 0.85))
    m.stretch("Body", "Spine")
    w, d, h = 1.75, 1.45, 1.9
    yc, zc = 0.3, 7.75
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2

    def beard(m, front, mouth_z, gap, lower_length, chin):
        m.loft_z("Beard", (chin - 0.7, 0, front - 0.05, 1.15, 0.55), (chin + 0.05, 0, front - 0.12, 1.25, 0.6))
        m.loft_z("Beard", (chin - 1.75, 0, front + 0.1, 0.14, 0.14), (chin - 0.7, 0, front - 0.05, 1.15, 0.55))
        for x, z in ((-0.3, chin - 0.4), (0.25, chin - 0.75), (-0.08, chin - 1.15), (0.36, chin - 0.2)):
            m.block("Sparkle", x, front + 0.24, z, 0.08, 0.06, 0.08)

    m.block("Body", 0, yc, zc, w, d, h)
    star_mouth(m, front, zc - 0.58, w, 0.24, 1.05, 0.26, 0.22, 0.05, lower="Body", rng=rng, on_jaw=beard)
    for side in (-1, 1):  # the corners of its mouth, turned up a touch: kindly, not smiling
        beam(m, "Mouth", (side * 0.38, front + 0.245, zc - 0.575), (side * 0.52, front + 0.245, zc - 0.52), 0.04, 0.045)
    m.block("Body", 0, front + 0.1, zc - 0.05, 0.3, 0.2, 0.42)  # a straight nose
    for side in (-1, 1):
        star_eye(m, side * 0.43, front, zc + 0.2, 0.5, 0, lid=0.36, mirror=side)
        for dy, z, s in ((-0.35, zc + 0.45, 0.32), (-0.85, zc - 0.25, 0.42), (-0.3, zc - 0.5, 0.2)):  # moon craters
            m.block("DustDark", side * (w / 2 + 0.01), yc + dy + 0.3, z, 0.05, s, s)
    # The third eye: a star on its brow in a gold setting.
    m.block("Trim", 0, front + 0.02, zc + 0.7, 0.36, 0.06, 0.36)
    star_on(m, "StarGlow", (0, front + 0.07, zc + 0.7), 0.24)
    # The crown: a gold band, five points with a crystal in each, the middle one tallest.
    top = zc + h / 2
    m.block("Trim", 0, yc, top + 0.12, w + 0.14, d + 0.14, 0.34)
    for x, height in ((-0.72, 0.6), (-0.36, 0.85), (0.0, 1.2), (0.36, 0.85), (0.72, 0.6)):
        prism(m, "Trim", x, front + 0.02 - 0.1, top + 0.25, top + 0.25 + height, 0.17, 0.02, 4, math.pi / 4)
        gem(m, "CrystalGlow", x, front + 0.12, top + 0.32 + height * 0.25, 0.09, 0.13, 0.1)
        for y in (yc - 0.4, yc - 0.85):
            prism(m, "Trim", x * 1.05, y, top + 0.25, top + 0.25 + height * 0.7, 0.15, 0.02, 4, math.pi / 4)
    # The halo behind its head, with twinkles on it.
    hpts = ring(m, "Halo", (0, yc - 0.95, zc + 0.45), 1.7, 0.1, 0.15, upright=True, n=26)
    for i in range(0, 26, 4):
        p = hpts[i]
        star_on(m, "Sparkle", (p[0], p[1] - 0.06, p[2]), 0.14)
    m.head_centre = (0, front + 0.3, zc + 0.1)
    return m


# ---------------------------------------------------------------------- previews


def quick_preview(models, out):
    """Stills only, for trying faces: each model whole and its face, and the lineup."""
    scene = kit.setup_scene()
    kit.RENDERS = out
    out.mkdir(parents=True, exist_ok=True)
    kit.NO_STUDS.update(GLOW_ROLES)
    animals = bpy.data.collections.new("Animals")
    scene.collection.children.link(animals)
    roots = []
    for i, model in enumerate(models):
        root = model.build(animals)
        root.location = (i * 16, 0, 0)
        roots.append(root)
    light_up(roots, GLOW_ROLES)
    ground = bpy.data.meshes.new("Ground")
    ground.from_pydata([(-300, -300, -0.01), (400, -300, -0.01), (400, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground.materials.append(kit.material("Ground", FLOOR, False))
    scene.collection.objects.link(bpy.data.objects.new("Ground", ground))
    set_sky(scene, SKY)
    bpy.context.view_layer.update()
    for model, root in zip(models, roots):
        kit.set_visible(roots, [root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 3)
        kit.shoot(scene, f"{model.name}_full", centre + Vector((0.62, 0.85, 0.32)) * reach * 1.15, centre, (640, 640), 50)
        head = root.location + Vector(model.head_centre)
        size = max(3.2, model.head_centre[2] * 0.75)
        kit.shoot(scene, f"{model.name}_face", head + Vector((0.55, 1.0, 0.14)) * size * 1.5, head, (560, 560), 50)
        kit.shoot(scene, f"{model.name}_front", head + Vector((0, 1, 0.1)) * size * 1.6, head, (560, 560), 50)
        kit.shoot(scene, f"{model.name}_close", head + Vector((0.5, 1.0, 0.12)) * 4.2, head, (560, 560), 50)
    kit.set_visible(roots, roots)
    middle = (len(models) - 1) * 16 / 2
    kit.shoot(scene, "lineup", (middle, 84, 20), (middle, 0, 4.5), (1800, 700), 26)


def main():
    builders = [craterback, stargazer, comet_trike, ringhorn, nebulasaur, star_sovereign]
    only = os.environ.get("ONLY")
    if only:
        builders = [b for b in builders if b.__name__ in only.split(",")]
    models = [b() for b in builders]
    if os.environ.get("QUICK"):
        quick_preview(models, Path(os.environ.get("QUICK_OUT", "/tmp/starfall_quick")))
        return
    build_and_render(models, RENDERS, HERE / "starfall_crater_monsters.blend", "starfall_crater_animation_preview.mp4",
                     sky=SKY, ground=FLOOR, glow_roles=GLOW_ROLES, spacing=16)


if __name__ == "__main__":
    main()
