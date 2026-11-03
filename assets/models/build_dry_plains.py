"""Builds Dry Plains' animals and props and renders them (run with Blender in background mode).

    Blender -b -P build_dry_plains.py

Saves dry_plains_models.blend and renders to design/world/models_dry_plains/. Uses the same parts and
bones as build_fern_valley.py, so the game's walk and idle work unchanged. The first three animals are
the silly ones and the last three the fierce ones (docs/GAME_SPEC.md "The style as you advance").

Animals are built at the first map's size, like every map's: the game makes them this map's size
(Config/Biomes standardScale), so the size lives in one place and can be tuned there.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_fern_valley as kit  # noqa: E402
from build_fern_valley import Model, biped_legs, eyes, jaws, nostrils, spikes_along_y, tail, teeth  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "models_dry_plains"


def quad_legs(m, x_front, y_front, x_back, y_back, top, width):
    """Four stout legs. Front and back bones are named as the game's walk expects."""
    for x_abs, y, end in ((x_front, y_front, "Front"), (x_back, y_back, "Back")):
        for side in (-1, 1):
            x = side * x_abs
            m.use(end + ("L" if side < 0 else "R"), (x, y, top))
            m.loft_z("Body", (0.3, x, y, width * 0.8, width * 0.8), (top + 0.2, x, y, width, width * 1.1))
            m.block("Belly", x, y + width * 0.12, width * 0.16, width * 1.02, width * 1.15, width * 0.32)
            for offset in (-0.3, 0, 0.3):
                claw = width * 0.18
                m.block("Claw", x + offset * width, y + width * 0.68, claw * 0.7, claw, claw, claw * 1.3)
    m.bone = "Spine"


def lower_teeth(m, spots, z, size):
    """Teeth pointing up from the lower jaw."""
    for x, y in spots:
        m.loft_z("Teeth", (z, x, y, size, size), (z + size, x, y, size * 0.15, size * 0.15))


def fangs(m, front, length, snout, mouth_z, gap, size, per_side):
    """A full set for an open mouth: both jaws, along the sides and across the front."""
    upper, lower = [], []
    for side in (-1, 1):
        for i in range(per_side):
            y = front + length * (0.12 + 0.76 * i / max(per_side - 1, 1))
            upper.append((side * (snout / 2 - size * 0.5), y))
            if i % 2 == 0:
                lower.append((side * (snout * 0.45 - size * 0.5), y + size * 0.4))
        upper.append((side * snout * 0.18, front + length - size * 0.5))
    teeth(m, upper, mouth_z + gap / 2 + 0.02, size)
    lower_teeth(m, lower, mouth_z - gap / 2 - 0.02, size * 0.8)


def dusty_proto():
    """Silly: a dopey little frill-head with its tongue hanging out and eyes that don't agree."""
    m = Model("dino_Proto", {"Body": "#e3b768", "Accent": "#c9743c", "Belly": "#f7e7bd", "Claw": "#7c4a24"})
    m.joint("Spine", (0, -0.1, 1.6))
    quad_legs(m, 0.62, 1.0, 0.68, -1.0, 1.5, 0.62)
    m.loft_y("Body", (-1.7, 0, 1.55, 1.3, 1.2), (1.4, 0, 1.75, 1.6, 1.5))
    m.loft_y("Belly", (-1.2, 0, 1.1, 1.1, 0.45), (1.45, 0, 1.25, 1.3, 0.6))
    tail(m, (-1.65, 1.5, 0.9, 0.8), (-3.1, 1.65, 0.15, 0.15), 2)
    w, d, h = 1.5, 1.3, 1.2
    yc, zc = 2.0, 2.05
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    mouth = zc - 0.32
    jaws(m, front, mouth, w, 0.72, 0.95, 0.36, 0.2, 0.2, upper="Accent", lower="Belly", grin=0.14, skull_d=d)
    m.block("Tongue", 0.18, front + 0.72, mouth - 0.3, 0.34, 0.2, 0.75)
    eyes(m, w / 2, front, zc + 0.2, 0.82, look=((0, 0.15), (0, -0.14)))
    nostrils(m, front + 0.55, mouth + 0.42, 0.2, 0.09)
    m.loft_z("Accent", (zc - 0.25, 0, yc - 0.72, 1.6, 0.26), (zc + 1.3, 0, yc - 0.95, 2.6, 0.2))
    for x in (-0.8, 0, 0.8):
        m.block("Belly", x, yc - 0.82, zc + 0.92, 0.3, 0.3, 0.3)
    m.head_centre = (0, front + 0.1, zc)
    return m


def bonkhead():
    """Silly: all dome and no thoughts. Cross-eyed from headbutting things, with a bandage to prove it."""
    m = Model("dino_Pachy", {"Body": "#8cc0d6", "Accent": "#f28a4b", "Belly": "#e8f4f7", "Claw": "#3f6b80"})
    m.joint("Spine", (0, -0.3, 2.3))
    biped_legs(m, 0.5, -0.3, 2.0, 0.8, 0.95, 0.32, 0.95, 0.24)
    m.loft_y("Body", (-1.2, 0, 2.4, 0.95, 0.95), (0.7, 0, 2.8, 1.35, 1.45))
    m.loft_y("Belly", (-0.6, 0, 2.05, 0.9, 0.5), (0.75, 0, 2.35, 1.1, 0.75))
    tail(m, (-1.15, 2.42, 0.8, 0.75), (-3.4, 2.75, 0.15, 0.15), 3)
    for side in (-1, 1):
        m.use("ArmL" if side < 0 else "ArmR", (side * 0.72, 0.55, 2.7))
        m.loft_y("Body", (0.55, side * 0.72, 2.7, 0.2, 0.22), (1.05, side * 0.72, 2.4, 0.14, 0.15))
    m.use("Neck", (0, 0.6, 3.35))
    m.loft_z("Body", (3.35, 0, 0.6, 0.92, 0.98), (3.95, 0, 0.85, 0.74, 0.74))
    m.stretch("Body", "Spine")
    w, d, h = 1.2, 1.2, 0.9
    yc, zc = 1.05, 4.25
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    jaws(m, front, zc - 0.28, w, 0.5, 0.85, 0.26, 0.16, 0.12, grin=0.22, skull_d=d)
    eyes(m, w / 2, front, zc + 0.05, 0.62, look=((-0.14, -0.06), (-0.14, 0.05)))
    # The dome is the whole personality.
    m.loft_z("Accent", (zc + 0.35, 0, yc - 0.12, 1.3, 1.35), (zc + 1.05, 0, yc - 0.12, 1.5, 1.5))
    m.loft_z("Accent", (zc + 1.05, 0, yc - 0.12, 1.5, 1.5), (zc + 1.6, 0, yc - 0.12, 0.8, 0.8))
    m.block("Belly", 0.3, yc + 0.6, zc + 1.12, 0.85, 0.2, 0.26)
    m.block("Belly", 0.3, yc + 0.62, zc + 1.12, 0.26, 0.2, 0.75)
    m.head_centre = (0, front, zc + 0.3)
    return m


def grumposaurus():
    """Silly: a low armoured tank with a club tail that hates mornings, walking and you."""
    m = Model("dino_Ankylo", {"Body": "#9c8a64", "Accent": "#6a5a44", "Belly": "#e0d2a8", "Claw": "#3f3528"})
    m.joint("Spine", (0, 0, 1.75))
    quad_legs(m, 1.15, 1.3, 1.2, -1.5, 1.5, 0.82)
    m.loft_y("Body", (-2.6, 0, 1.7, 2.2, 1.6), (0, 0, 2.05, 3.2, 2.2))
    m.loft_y("Body", (0, 0, 2.05, 3.2, 2.2), (2.2, 0, 1.6, 2.3, 1.5))
    m.loft_y("Belly", (-2.2, 0, 0.98, 2, 0.3), (2, 0, 0.92, 2.1, 0.3))
    for y in (-1.8, -0.7, 0.4, 1.4):
        size = 0.8 if abs(y) > 1 else 1
        for x in (-0.9, 0, 0.9):
            m.block("Accent", x, y, 3.14 - abs(y) * 0.22, size, size * 0.8, 0.26)
    for y in (-1.6, -0.5, 0.6, 1.6):
        for side in (-1, 1):
            start = side * (1.45 - abs(y) * 0.15)
            m.loft_x("Teeth", (start, y, 1.85, 0.5, 0.5), (start + side * 0.85, y, 1.75, 0.05, 0.05))
    tail(m, (-2.5, 1.65, 1.1, 0.9), (-5.3, 1.7, 0.42, 0.36), 3)
    m.bone = "Tail3"
    m.block("Accent", 0, -5.6, 1.7, 1.5, 1.1, 1)
    for side in (-1, 1):
        m.loft_x("Teeth", (side * 0.7, -5.6, 1.7, 0.5, 0.5), (side * 1.25, -5.6, 1.7, 0.05, 0.05))
    m.use("Neck", (0, 2.1, 1.65))
    m.loft_y("Body", (2.1, 0, 1.65, 1.8, 1.3), (2.6, 0, 1.55, 1.5, 1.1))
    m.stretch("Body", "Spine")
    w, d, h = 1.7, 1.2, 1
    yc, zc = 2.95, 1.55
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    jaws(m, front, zc - 0.3, w, 0.45, 1.3, 0.34, 0.18, 0.06, tongue=False, grin=-0.14, skull_d=d)
    eyes(m, w / 2, front, zc + 0.14, 0.6, lid=0.3, brow=-0.55)
    nostrils(m, front + 0.32, zc + 0.02, 0.3, 0.1)
    m.head_centre = (0, front, zc)
    return m


def triceratops():
    """Fierce: head down, three horns forward, a great shield of a frill."""
    m = Model("dino_Triceratops", {"Body": "#5f8f6a", "Accent": "#b9482f", "Belly": "#dcd8a6", "Claw": "#2e4a36"})
    m.joint("Spine", (0, 0, 2.5))
    quad_legs(m, 1.2, 1.6, 1.25, -1.9, 2.1, 0.95)
    m.loft_y("Body", (-3, 0, 2.5, 2.3, 2.1), (-0.2, 0, 3.05, 3.2, 3))
    m.loft_y("Body", (-0.2, 0, 3.05, 3.2, 3), (2.5, 0, 2.7, 2.5, 2.3))
    m.loft_y("Belly", (-2.5, 0, 1.55, 2, 0.4), (2.3, 0, 1.6, 2.1, 0.4))
    for y in (-1.8, -0.4, 1):
        m.block("Accent", 0, y, 4.55 - abs(y) * 0.2, 2, 0.5, 0.14)
    tail(m, (-2.9, 2.4, 1.6, 1.4), (-6, 2.4, 0.2, 0.2), 3)
    w, d, h = 2.1, 1.7, 1.6
    yc, zc = 3.3, 2.5
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    jaws(m, front, zc - 0.48, w, 0.85, 1.05, 0.5, 0.26, 0.14, upper="Accent", lower="Belly", tongue=False, grin=-0.1, skull_d=d)
    eyes(m, w / 2, front, zc + 0.3, 0.62, lid=0.22, brow=-0.5)
    nostrils(m, front + 0.55, zc + 0.02, 0.26, 0.11)
    # The frill, then the horns.
    m.loft_z("Accent", (zc - 0.6, 0, yc - 0.9, 2.2, 0.3), (zc + 2, 0, yc - 1.55, 4, 0.24))
    m.loft_z("Body", (zc - 0.4, 0, yc - 1, 1.9, 0.3), (zc + 1.7, 0, yc - 1.6, 3.4, 0.26))
    for x in (-1.5, -0.75, 0, 0.75, 1.5):
        m.loft_z("Teeth", (zc + 1.95 - abs(x) * 0.25, x, yc - 1.55, 0.45, 0.2), (zc + 2.5 - abs(x) * 0.25, x, yc - 1.6, 0.04, 0.04))
    for side in (-1, 1):
        x = side * 0.62
        m.loft_y("Teeth", (front - 0.15, x, zc + 0.85, 0.5, 0.5), (front + 2.1, x, zc + 1.45, 0.05, 0.05))
    m.loft_z("Teeth", (zc - 0.02, 0, front + 0.6, 0.38, 0.42), (zc + 0.72, 0, front + 0.72, 0.04, 0.04))
    m.head_centre = (0, front + 0.3, zc + 0.2)
    return m


def carnotaurus():
    """Fierce: lean, red and horned like a bull, with the meanest stare on the plains."""
    m = Model("dino_Carno", {"Body": "#c8402f", "Accent": "#2b2230", "Belly": "#f2d3a8", "Claw": "#1c1820"})
    m.joint("Spine", (0, -0.6, 3.1))
    biped_legs(m, 0.62, -0.6, 2.8, 1, 1.2, 0.42, 1.25, 0.3)
    m.loft_y("Body", (-1.9, 0, 3.1, 1.25, 1.2), (1, 0, 3.55, 1.65, 1.75))
    m.loft_y("Belly", (-1, 0, 2.65, 1.2, 0.55), (1.05, 0, 3, 1.4, 0.85))
    tail(m, (-1.85, 3.12, 1.05, 1), (-5.8, 3.5, 0.15, 0.15), 3)
    for y in (-1.4, -0.6, 0.2, 0.9):
        m.block("Accent", 0, y, 3.72 + y * 0.17, 1.28, 0.34, 0.1)
    m.bone = "Tail1"
    m.block("Accent", 0, -2.5, 3.6, 0.72, 0.3, 0.1)
    for side in (-1, 1):
        m.use("ArmL" if side < 0 else "ArmR", (side * 0.88, 0.8, 3.35))
        m.loft_y("Body", (0.7, side * 0.88, 3.35, 0.2, 0.22), (1.1, side * 0.88, 3.1, 0.13, 0.14))
        m.block("Claw", side * 0.88, 1.15, 3.05, 0.14, 0.14, 0.1)
    m.use("Neck", (0, 1.1, 4.1))
    m.loft_z("Body", (4.1, 0, 1.15, 1.15, 1.2), (4.7, 0, 1.45, 1, 1))
    m.stretch("Body", "Spine")
    w, d, h = 1.6, 1.6, 1.2
    yc, zc = 1.9, 5.05
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    length, snout = 1.2, 1.12
    mouth = zc - 0.42
    jaws(m, front, mouth, w, length, snout, 0.42, 0.26, 0.42, grin=0.32, skull_d=d)
    fangs(m, front, length, snout, mouth, 0.42, 0.2, 4)
    eyes(m, w / 2, front, zc + 0.22, 0.56, lid=0.2, brow=-0.6)
    nostrils(m, front + length - 0.2, mouth + 0.5, 0.3, 0.12)
    for side in (-1, 1):
        m.loft_x("Accent", (side * 0.55, yc - 0.1, zc + 0.68, 0.6, 0.5), (side * 1.55, yc + 0.15, zc + 1.2, 0.05, 0.05))
    m.head_centre = (0, front + 0.3, zc)
    return m


def t_rex():
    """Fierce: the map's boss. A huge head, a wall of teeth, a scar, and arms it's sensitive about."""
    m = Model("dino_TRex", {"Body": "#355e4f", "Accent": "#b3312c", "Belly": "#e9d9a8", "Claw": "#17171d"})
    m.joint("Spine", (0, -0.8, 4.4))
    biped_legs(m, 0.95, -0.8, 3.9, 1.5, 1.7, 0.7, 1.9, 0.4)
    m.loft_y("Body", (-2.4, 0, 4.2, 1.8, 1.9), (1.4, 0, 5, 2.7, 3))
    m.loft_y("Belly", (-1.1, 0, 3.55, 1.75, 0.8), (1.45, 0, 4.1, 2.3, 1.45))
    tail(m, (-2.3, 4.25, 1.6, 1.6), (-7.2, 4.8, 0.2, 0.2), 3)
    for y, z, size in ((1, 6.4, 0.55), (0.1, 6.15, 0.65), (-0.8, 5.75, 0.6), (-1.7, 5.4, 0.5)):
        spikes_along_y(m, "Accent", [(y, z, size, size * 1.1)])
    m.bone = "Tail1"
    spikes_along_y(m, "Accent", [(-3, 5.15, 0.42, 0.5)])
    m.bone = "Tail2"
    spikes_along_y(m, "Accent", [(-4.3, 5.15, 0.32, 0.42)])
    for side in (-1, 1):
        m.use("ArmL" if side < 0 else "ArmR", (side * 1.38, 1.2, 4.85))
        m.loft_y("Body", (1, side * 1.38, 4.85, 0.3, 0.32), (1.75, side * 1.38, 4.45, 0.2, 0.2))
        for offset in (-0.07, 0.07):
            m.loft_y("Claw", (1.72, side * 1.38 + offset, 4.42, 0.08, 0.1), (2, side * 1.38 + offset, 4.3, 0.03, 0.03))
    m.use("Neck", (0, 1.5, 5.9))
    m.loft_z("Body", (5.9, 0, 1.5, 2, 2.1), (6.65, 0, 1.95, 1.75, 1.75))
    m.stretch("Body", "Spine")
    w, d, h = 2.6, 2.6, 1.9
    yc, zc = 2.9, 7.3
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    length, snout = 2, 2.1
    mouth = zc - 0.55
    jaws(m, front, mouth, w, length, snout, 0.72, 0.48, 0.75, grin=0.4, skull_d=d)
    fangs(m, front, length, snout, mouth, 0.75, 0.36, 5)
    eyes(m, w / 2, front, zc + 0.48, 0.8, lid=0.2, brow=-0.6)
    nostrils(m, front + length - 0.32, mouth + 0.95, 0.55, 0.2)
    # A scar across the snout, and ridges down the back of the head.
    m.loft_y("Belly", (front + 0.35, 0.45, mouth + 1.13, 0.16, 0.05), (front + 1.25, -0.25, mouth + 1.1, 0.16, 0.05))
    for y, height in ((yc + 0.6, 0.42), (yc - 0.3, 0.5), (yc - 1.1, 0.4)):
        spikes_along_y(m, "Accent", [(y, zc + h / 2, height, 0.6)])
    m.head_centre = (0, front + 0.6, zc)
    return m


# ---------------------------------------------------------------------- props
# Dry Plains swaps Fern Valley's ferns and trees for cacti, dry grass, red rock and the bones of
# huge old monsters. Big shapes and strong colours, since the egg passes in about a second.


def prop(name, **colours):
    return Model(f"prop_{name}", colours)


def beam(m, role, a, b, width, height=None, end_width=None):
    """A block running from point a to point b, for branches, ribs and twigs at any angle.
    It tapers to end_width at b, keeping its section's shape."""
    height = height or width
    end_width = width if end_width is None else end_width
    end_height = height * end_width / width
    start, end = Vector(a), Vector(b)
    along = (end - start).normalized()
    side = along.cross(Vector((0, 0, 1)))
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    lift = side.cross(along)
    verts = []
    for point, w, h in ((start, width, height), (end, end_width, end_height)):
        for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            verts.append(tuple(point + side * sx * w / 2 + lift * sz * h / 2))
    faces = [[0, 1, 2, 3], [7, 6, 5, 4]] + [[i, i + 4, (i + 1) % 4 + 4, (i + 1) % 4] for i in range(4)]
    m._add(role, verts, faces)


def cactus_ribs(m, x, y, bottom, top, half):
    """Four raised strips down a cactus column, one on each side."""
    for dx, dy in ((half, 0), (-half, 0), (0, half), (0, -half)):
        m.block("Rib", x + dx, y + dy, (bottom + top) / 2, 0.35 if dx else 0.6, 0.6 if dx else 0.35, top - bottom)


def saguaro():
    """The map's signature: a tall cactus with two arms up, like it's being robbed."""
    m = prop("Saguaro", Cactus="#5cae4a", Rib="#3f8c3a", Flower="#ff7fae")
    m.loft_z("Cactus", (0, 0, 0, 3, 3), (11, 0, 0, 2.6, 2.6))
    m.loft_z("Cactus", (11, 0, 0, 2.6, 2.6), (12.3, 0, 0, 1.5, 1.5))
    cactus_ribs(m, 0, 0, 0.3, 11, 1.4)
    for side, low, high in ((1, 4.6, 9.4), (-1, 6.4, 10.6)):
        x = side * 3.7
        m.loft_x("Cactus", (side * 1.2, 0, low, 1.7, 1.7), (x, 0, low, 1.7, 1.7))
        m.loft_z("Cactus", (low - 0.85, x, 0, 1.8, 1.8), (high, x, 0, 1.7, 1.7))
        m.loft_z("Cactus", (high, x, 0, 1.7, 1.7), (high + 0.8, x, 0, 1, 1))
        cactus_ribs(m, x, 0, low, high, 0.88)
        m.block("Flower", x, 0, high + 0.95, 0.7, 0.7, 0.35)
    m.block("Flower", 0, 0, 12.45, 0.9, 0.9, 0.4)
    m.block("Flower", 0.55, 0.3, 12.2, 0.5, 0.5, 0.4)
    return m


def barrel_cactus():
    """Two squat barrels with needles and a crown of flowers."""
    m = prop("BarrelCactus", Cactus="#4fa046", Rib="#357d34", Needle="#fff1c4", Flower="#ffcf3a")
    for x, y, size in ((0, 0, 3.4), (2.9, 1.2, 2.2)):
        m.loft_z("Cactus", (0, x, y, size * 0.9, size * 0.9), (size * 0.6, x, y, size, size))
        m.loft_z("Cactus", (size * 0.6, x, y, size, size), (size * 0.95, x, y, size * 0.62, size * 0.62))
        cactus_ribs(m, x, y, 0.2, size * 0.75, size * 0.48)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for z in (0.3, 0.55):
                m.block("Needle", x + dx * size * 0.56, y + dy * size * 0.56, size * z, 0.18 + 0.3 * abs(dx), 0.18 + 0.3 * abs(dy), 0.12)
        m.block("Flower", x, y, size * 0.97, size * 0.4, size * 0.4, size * 0.12)
    return m


def tumbleweed(seed=4):
    """A ball of dry twigs, chords crossing a sphere so it reads as a tangle from any side."""
    m = prop("Tumbleweed", Twig="#c99d56", TwigDark="#9b7339")
    rng = random.Random(seed)
    centre, radius = Vector((0, 0, 2.3)), 2.3

    def on_sphere():
        z = rng.uniform(-1, 1)
        angle = rng.uniform(0, 2 * math.pi)
        r = math.sqrt(1 - z * z)
        return centre + Vector((r * math.cos(angle), r * math.sin(angle), z)) * radius

    for i in range(26):
        beam(m, "Twig" if i % 3 else "TwigDark", on_sphere(), on_sphere(), 0.32)
    return m


def skull():
    """The bleached skull of something very big, lying in the sand with its jaw dropped. The eye
    sockets wrap onto the top, so it reads as a skull from the flight camera up high."""
    m = prop("Skull", Bone="#f2e9d3", BoneShade="#d4c39d", Socket="#3a2b22", Teeth="#fffaf0")
    m.loft_y("Bone", (-2.4, 0, 2.2, 4.0, 3.4), (0.2, 0, 2.4, 4.4, 3.8))  # cranium
    m.loft_y("Bone", (0.2, 0, 2.3, 3.6, 3.0), (4.6, 0, 1.8, 2.2, 1.6))  # snout
    for side in (-1, 1):
        m.block("Socket", side * 2.19, -0.6, 2.85, 0.14, 2.0, 1.7)
        m.block("Socket", side * 1.45, -0.6, 4.22, 1.2, 2.0, 0.12)
        m.block("BoneShade", side * 1.45, 0.75, 4.35, 1.4, 0.6, 0.35)  # brow over each socket
        m.block("Socket", side * 0.45, 3.8, 2.84, 0.55, 0.7, 0.1)  # nostrils
        m.block("BoneShade", side * 2.05, -1.9, 1.4, 0.2, 0.9, 1.4)  # hollow behind the cheek
    m.block("BoneShade", 0, -1.5, 4.22, 0.3, 1.5, 0.12)  # a crack across the top
    # The lower jaw lies on the ground, a little open, with teeth in both jaws.
    m.loft_y("Bone", (-1.6, 0, 0.25, 3.8, 0.5), (4.4, 0, 0.22, 2.0, 0.4))
    for side in (-1, 1):
        for i in range(4):
            y = 1.4 + i * 0.85
            x = side * (1.45 - i * 0.12)
            m.loft_z("Teeth", (1.05, x, y, 0.55, 0.55), (0.5, x, y, 0.1, 0.1))
            m.loft_z("Teeth", (0.45, x * 0.85, y + 0.4, 0.42, 0.42), (0.85, x * 0.85, y + 0.4, 0.1, 0.1))
    return m


def rib_cage():
    """Ribs of a giant arching out of the sand, the spine still on top."""
    m = prop("RibCage", Bone="#f2e9d3", BoneShade="#d4c39d", Sand="#e8cd8a")
    beam(m, "Bone", (0, -5.6, 6.0), (0, 5.4, 6.7), 1.3, 1.1, 0.9)
    for i in range(7):
        m.block("BoneShade", 0, -4.8 + i * 1.6, 6.9 + i * 0.07, 0.8, 0.6, 0.8)
    for i in range(5):
        y = -4 + i * 2
        shrink = 1 - abs(i - 2) * 0.08
        for side in (-1, 1):
            points = [(0, y, 6.2), (side * 2.6 * shrink, y, 6.7), (side * 4.3 * shrink, y, 4.8 * shrink + 0.4),
                      (side * 4.7 * shrink, y, 2.2), (side * 4.3 * shrink, y, -0.3)]
            for (a, b), w in zip(zip(points, points[1:]), (0.75, 0.7, 0.62, 0.55)):
                beam(m, "Bone", a, b, w, 0.6, w * 0.9)
            m.block("Sand", side * 4.3 * shrink, y, 0.2, 2.2, 1.8, 0.4)
    return m


def mesa():
    """A stepped red rock butte with dry grass on top, big enough to read from the rim."""
    m = prop("Mesa", Rock="#c8683a", RockLight="#e48d55", Stripe="#a24b2a", Top="#d9bd77")
    m.block("Rock", 0, 0, 2, 12, 9, 4)
    m.block("Stripe", 0, 0, 3.9, 12.2, 9.2, 0.6)
    m.block("RockLight", 0.4, 0.3, 5.1, 10.2, 7.6, 2.2)
    m.block("Rock", 0.6, 0.5, 7.3, 8.4, 6.2, 2.2)
    m.block("Stripe", 0.6, 0.5, 8.1, 8.6, 6.4, 0.5)
    m.block("Top", 0.6, 0.5, 8.65, 8.2, 6, 0.3)
    m.block("RockLight", -3.6, -2.6, 1.6, 4.4, 4.4, 3.2)  # a fallen chunk at the foot
    m.block("Rock", 4.8, 3.4, 0.9, 3, 2.6, 1.8)
    return m


def dead_tree(seed=6):
    """A bare, twisted tree with forked branches."""
    m = prop("DeadTree", Wood="#8f6c4c", WoodDark="#6b4e35")
    rng = random.Random(seed)
    beam(m, "Wood", (0, 0, 0), (0.6, 0.2, 4.5), 2.2, None, 1.6)
    beam(m, "Wood", (0.6, 0.2, 4.5), (0.1, -0.2, 8.5), 1.6, None, 1.0)
    m.loft_z("WoodDark", (0, 0, 0, 3.2, 3.2), (0.6, 0, 0, 2.2, 2.2))  # roots flaring
    for start, angle, length, rise in (((0.5, 0.2, 4.2), 0.3, 3.8, 2.6), ((0.4, 0, 6.2), 2.8, 3.4, 2.2), ((0.2, -0.1, 8.1), 4.6, 2.6, 2.4)):
        sx, sy, sz = start
        end = (sx + math.cos(angle) * length, sy + math.sin(angle) * length, sz + rise)
        beam(m, "Wood", start, end, 0.9, None, 0.5)
        for turn in (-0.6, 0.7):
            twig = angle + turn + rng.uniform(-0.2, 0.2)
            tip = (end[0] + math.cos(twig) * 1.6, end[1] + math.sin(twig) * 1.6, end[2] + rng.uniform(0.6, 1.4))
            beam(m, "WoodDark", end, tip, 0.45, None, 0.2)
    return m


def dry_grass(seed=2):
    """A spiky tuft of straw-yellow grass."""
    m = prop("DryGrass", Grass="#e6c55f", GrassDark="#c49b3c")
    rng = random.Random(seed)
    m.loft_z("GrassDark", (0, 0, 0, 1.6, 1.6), (0.5, 0, 0, 1.2, 1.2))
    for i in range(11):
        angle = i * 2 * math.pi / 11 + rng.uniform(-0.15, 0.15)
        reach = rng.uniform(1.2, 2.2)
        tip = (math.cos(angle) * reach, math.sin(angle) * reach, rng.uniform(1.8, 3))
        beam(m, "Grass" if i % 2 else "GrassDark", (math.cos(angle) * 0.4, math.sin(angle) * 0.4, 0.3), tip, 0.4, None, 0.08)
    return m


def boulder():
    """Sandstone boulders, one big and one small, with cracks."""
    m = prop("Boulder", Stone="#d8aa74", StoneDark="#b88350", Crack="#7b5232")
    m.loft_z("Stone", (0, 0, 0, 6, 5), (2.4, 0.2, 0.1, 6.2, 5.2))
    m.loft_z("Stone", (2.4, 0.2, 0.1, 6.2, 5.2), (4.2, 0.4, 0.2, 4, 3.4))
    m.loft_z("StoneDark", (0, 3.9, -1.5, 2.8, 2.6), (1.6, 3.8, -1.4, 2, 1.8))
    m.block("Crack", 3.12, 0.2, 2.3, 0.15, 0.4, 2.2)
    m.block("Crack", 3.1, 0.9, 1.4, 0.15, 1.2, 0.3)
    m.block("Crack", 0.4, 0.5, 4.25, 2.2, 0.3, 0.12)
    return m


# ---------------------------------------------------------------------- scene and renders


def main():
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    animals = bpy.data.collections.new("Animals")
    props = bpy.data.collections.new("Props")
    stage = bpy.data.collections.new("Preview stage")
    for col in (animals, props, stage):
        scene.collection.children.link(col)

    models = [dusty_proto(), bonkhead(), grumposaurus(), triceratops(), carnotaurus(), t_rex()]
    prop_models = [saguaro(), barrel_cactus(), tumbleweed(), skull(), rib_cage(), mesa(), dead_tree(), dry_grass(), boulder()]
    roots = []
    x = 0
    for model in models:
        root = model.build(animals)
        root.location = (x, 0, 0)
        roots.append(root)
        x += 16
    prop_roots = []
    x = 0
    for model in prop_models:
        root = model.build(props)
        root.location = (x, -40, 0)
        prop_roots.append(root)
        x += 24
    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-300, -300, -0.01), (400, -300, -0.01), (400, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", "#ead08f", False))
    stage.objects.link(bpy.data.objects.new("Ground", ground_mesh))
    player = Model("Player", {"Skin": "#3f4553"})
    player.bone = "Root"
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    player_root = player.build(stage)
    player_root.location = (-9, 0, 0)
    bpy.context.view_layer.update()

    everything = roots + prop_roots + [player_root]
    for model, root in zip(models, roots):
        kit.set_visible(everything, [root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 3)
        kit.shoot(scene, f"{model.name}_full", centre + Vector((0.62, 0.85, 0.32)) * reach * 1.15, centre, (800, 800), 50)
        head = root.location + Vector(model.head_centre)
        size = max(3.2, model.head_centre[2] * 0.75)
        kit.shoot(scene, f"{model.name}_face", head + Vector((0.55, 1.0, 0.14)) * size * 1.5, head, (700, 700), 50)
    kit.set_visible(everything, roots + [player_root])
    kit.shoot(scene, "lineup", (40, 80, 19), (40, 0, 4), (1800, 700), 24)

    for model, root in zip(prop_models, prop_roots):
        player_root.location = root.location + Vector((-8, 2, 0))
        bpy.context.view_layer.update()
        kit.set_visible(everything, [root, player_root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 7)
        kit.shoot(scene, model.name, centre + Vector((0.5, 0.9, 0.42)) * reach * 1.25, centre, (600, 600), 50)
    player_root.location = (-9, -40, 0)
    bpy.context.view_layer.update()
    kit.set_visible(everything, prop_roots + [player_root])
    kit.shoot(scene, "props", (96, 50, 34), (96, -40, 3), (1800, 700), 18)

    player_root.location = (-9, 0, 0)
    kit.set_visible(everything, everything)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "dry_plains_models.blend"))
    print("saved", HERE / "dry_plains_models.blend")
    for model in models + prop_models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


main()
