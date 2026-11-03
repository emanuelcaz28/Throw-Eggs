"""Builds the Frozen Peaks's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_frozen_peaks_monsters.py

Saves frozen_peaks_monsters.blend and renders to design/world/monsters_frozen_peaks/. Frozen Peaks' props are in
build_frozen_peaks.py.

Silly first, fierce last, both a step further than the Volcano's. The silly ones keep the first maps' white
eyes, freezing in their own ways: an ice cream to the head, fur grown over the eyes, a mammoth in a hat and
scarf with an icicle hanging off its trunk. The fierce ones get the frost face: eyes glowing icy blue under a
heavy brow (the Volcano's eye shape, cold instead of hot), icicle teeth and glowing ice crystals (IceGlow,
Neon in the game). Blizzard Rex is the boss: a shaggy white rex in armour of glowing ice, an ice crown, and
frost breath pouring out of its jaws. All have the Jaw bone, so they snap and roar in the game.
Built at the first map's size; the game makes them 3.7x.
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_desert import beam, quad_legs  # noqa: E402
from build_forest import Model, biped_legs, tail  # noqa: E402
from build_volcano import ember_eyes, prism, ring_at, top_of  # noqa: E402
from face_kit import classic_mouth, icicle, top_nostrils  # noqa: E402
from monster_stage import build_and_render  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_frozen_peaks"

FROST_EYES = {"EyeGlow": "#2ec4ff", "Pupil": "#0e2236", "Highlight": "#ffffff"}
GLOW_ROLES = {"EyeGlow", "IceGlow"}


def fringe(m, role, pair, ys, rng, length=(0.5, 0.9), width=0.55, sides=(-1, 1), under=True):
    """Shaggy fur hanging off a body loft's lower edges (and its belly, if under)."""
    for y in ys:
        r = ring_at(*pair, y)
        top = r[2] - r[4] * 0.25
        for side in sides:
            m.block(role, side * (r[3] / 2 + 0.04), y, top - (L := rng.uniform(*length)) / 2 + 0.1, 0.22, width, L)
        if under:
            m.block(role, rng.uniform(-0.3, 0.3) * r[3], y, r[2] - r[4] / 2 - (L := rng.uniform(*length)) / 2 * 0.6, width * 1.4, width, L * 0.6)


def crystal(m, role, x, y, z, height, r, lean=(0, 0), sides=6, turn=0.0):
    """An ice crystal pointing up from z: a six-sided column with a pointed top."""
    mid = height * 0.6
    prism(m, role, x, y, z - 0.15, z + mid, r, r * 0.9, sides, turn, (lean[0] * 0.6, lean[1] * 0.6))
    prism(m, role, x + lean[0] * 0.6, y + lean[1] * 0.6, z + mid, z + height, r * 0.9, 0.03, sides, turn, (lean[0] * 0.4, lean[1] * 0.4))


def closed_eye(m, half_width, front_y, z, size, side, skin="Body", wrap=0.22):
    """Covers one of kit.eyes' eyes with skin and draws it squeezed shut: a dark > pointing at the nose."""
    outer = side * (half_width + size * wrap)
    w, d, h = size * 0.9, size, size * 1.15
    cx, cy = outer - side * w / 2, front_y - size * 0.3
    m.block(skin, cx, cy + size * 0.04, z, w + size * 0.14, d + size * 0.14, h + size * 0.1)
    fy = cy + d / 2 + size * 0.12
    inner_x, outer_x = cx - side * w * 0.35, cx + side * w * 0.38
    beam(m, "Mouth", (outer_x, fy, z + h * 0.28), (inner_x, fy, z), size * 0.16, size * 0.08)
    beam(m, "Mouth", (inner_x, fy, z), (outer_x, fy, z - h * 0.28), size * 0.16, size * 0.08)


# ---------------------------------------------------------------------- silly


def brain_freeze():
    """Silly: ate its ice cream far too fast. The scoop is splatted on its head with the cone sticking up
    like a horn, both hands clutching its skull, one eye squeezed shut, teeth gritted."""
    m = Model("dino_BrainFreeze", {"Body": "#9fd3ef", "Accent": "#5a9cc9", "Belly": "#eaf6ff", "Claw": "#2f5a7a",
                                    "Scoop": "#ffb3d1", "ScoopMint": "#bff2d6", "Cone": "#e0a35a", "ConeDark": "#b9783a", "Sprinkle": "#ffe14d"})
    m.joint("Spine", (0, -0.2, 1.6))
    biped_legs(m, 0.48, -0.2, 1.2, 0.72, 0.82, 0.32, 0.85, 0.24)
    m.loft_y("Body", (-0.95, 0, 1.5, 1.05, 1.05), (0.6, 0, 1.7, 1.4, 1.5))
    m.loft_y("Belly", (-0.45, 0, 1.25, 0.95, 0.6), (0.65, 0, 1.4, 1.2, 0.95))
    tail(m, (-0.9, 1.45, 0.75, 0.7), (-2.3, 1.75, 0.14, 0.14), 2)
    w, d, h = 1.45, 1.35, 1.2
    yc, zc = 1.05, 3.05
    # Both hands up on its head.
    for side in (-1, 1):
        x = side * 0.72
        m.use("ArmL" if side < 0 else "ArmR", (x, 0.45, 2.05))
        beam(m, "Body", (x, 0.45, 2.05), (side * 0.95, 0.75, 2.75), 0.28, None, 0.22)
        beam(m, "Body", (side * 0.95, 0.75, 2.75), (side * (w / 2 + 0.12), yc - 0.1, zc + 0.15), 0.22, None, 0.2)
        m.block("Claw", side * (w / 2 + 0.12), yc - 0.1, zc + 0.15, 0.24, 0.32, 0.32)
    m.use("Neck", (0, 0.55, 2.2))
    m.loft_z("Body", (2.15, 0, 0.55, 0.9, 0.95), (2.6, 0, 0.8, 0.8, 0.8))
    m.stretch("Body", "Spine")
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = classic_mouth(m, front, zc - 0.38, w, 0.62, 1.1, 0.3, 0.24, 0.14, tooth=0.13, per_side=3, lower_teeth=True,
                          tongue=False, skull_d=d)
    eye_z, size = zc + 0.25, 0.6
    kit.eyes(m, w / 2, front, eye_z, size, brow=0.45, look=((0, 0), (-0.06, 0.08)))
    closed_eye(m, w / 2, front, eye_z, size, -1)
    top_nostrils(m, snout, 0.22, 0.1)
    # The ice cream: a squashed scoop on top, dripping down, the cone sticking up out of it.
    top = zc + h / 2
    m.block("Scoop", 0.05, yc - 0.05, top + 0.2, 1.25, 1.15, 0.42)
    m.block("ScoopMint", -0.25, yc - 0.35, top + 0.5, 0.75, 0.7, 0.3)
    for x, y, length in ((0.62, yc + 0.35, 0.65), (-0.5, yc + 0.52, 0.45), (0.15, yc + 0.6, 0.85), (0.66, yc - 0.45, 0.5)):
        icicle(m, "Scoop", x, y, top + 0.05, length, 0.26)
    m.loft_z("Cone", (top + 0.55, 0.15, yc, 0.85, 0.85), (top + 2.0, 0.28, yc - 0.15, 0.07, 0.07))
    for z, w_ in ((top + 0.85, 0.66), (top + 1.25, 0.43)):
        m.block("ConeDark", 0.15 + (z - top) * 0.09, yc - (z - top) * 0.1, z, w_ + 0.04, w_ + 0.04, 0.07)
    for x, y in ((0.4, yc + 0.2), (-0.3, yc - 0.3), (0.25, yc - 0.45), (-0.45, yc + 0.25), (0.5, yc - 0.15)):
        m.block("Sprinkle", x, y, top + 0.43, 0.08, 0.2, 0.06)
    m.head_centre = (0, front + 0.1, zc + 0.2)
    return m


def woolly_rhino():
    """Silly: a round ball of shaggy fur with two horns and a nose. Its fringe has grown right over its eyes,
    one eye just peeking out, and a snowflake is stuck on its horn."""
    m = Model("dino_WoollyRhino", {"Body": "#8a6a4a", "Accent": "#6b4f35", "Belly": "#a8865f", "Claw": "#2e2218",
                                    "Horn": "#ece0c2", "Snow": "#f4f9ff", "Skin": "#5a4a40"})
    rng = random.Random(3)
    m.joint("Spine", (0, 0, 1.7))
    quad_legs(m, 0.9, 1.15, 0.95, -1.15, 1.25, 0.72)
    body = ((-2.0, 0, 2.0, 2.4, 2.1), (1.5, 0, 2.15, 2.6, 2.3))
    m.loft_y("Body", *body)
    fringe(m, "Accent", body, [-1.8, -1.2, -0.6, 0, 0.6, 1.2], rng, length=(0.7, 1.1), width=0.6)
    for y in (-1.3, -0.3, 0.7):
        for x in (-0.6, 0.5):
            m.block("Accent", x + rng.uniform(-0.15, 0.15), y, top_of(body, y) + 0.12, 0.7, 0.8, 0.3)
    tail(m, (-1.95, 2.1, 0.4, 0.4), (-2.6, 1.6, 0.2, 0.2), 2)
    m.bone = "Tail2"
    m.block("Accent", 0, -2.65, 1.45, 0.45, 0.4, 0.6)
    w, d, h = 1.8, 1.3, 1.4
    yc, zc = 2.35, 1.95
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = classic_mouth(m, front, zc - 0.42, w, 0.75, 1.45, 0.42, 0.26, 0.12, upper="Skin", lower="Skin", grin=0.16, skull_d=d)
    top_nostrils(m, snout, 0.32, 0.13)
    eye_z, size = zc + 0.18, 0.5
    kit.eyes(m, w / 2, front, eye_z, size, look=((0, 0), (0.08, -0.12)))
    # The fringe hanging over its face: covers the left eye and most of the right one.
    for i in range(9):
        x = -w / 2 + 0.1 + i * (w - 0.2) / 8
        length = 0.95 if x < 0.15 else 0.55
        m.block("Belly", x, front + 0.08, zc + h / 2 - length / 2 + 0.2, 0.25, 0.26, length + rng.uniform(-0.05, 0.08))
    m.block("Belly", 0, yc - 0.05, zc + h / 2 + 0.2, w + 0.2, d + 0.2, 0.4)
    for side in (-1, 1):  # little ears poking out of the fur
        m.loft_z("Accent", (zc + h / 2 + 0.2, side * 0.62, yc - 0.3, 0.32, 0.25), (zc + h / 2 + 0.65, side * 0.72, yc - 0.32, 0.08, 0.08))
    # Two horns on the snout, the big one with a snowflake stuck to it.
    y1, y2 = front + 0.58, front + 0.22
    t1, t2 = snout["top"](y1), snout["top"](y2)
    m.loft_z("Horn", (t1 - 0.05, 0, y1, 0.48, 0.52), (t1 + 1.0, 0, y1 + 0.3, 0.05, 0.05))
    m.loft_z("Horn", (t2 - 0.05, 0, y2, 0.32, 0.34), (t2 + 0.45, 0, y2 + 0.1, 0.04, 0.04))
    fz, fy = t1 + 0.5, y1 + 0.2
    for angle in (0, 60, 120):
        a = math.radians(angle)
        beam(m, "Snow", (0.28 + math.cos(a) * 0.3, fy, fz + math.sin(a) * 0.3), (0.28 - math.cos(a) * 0.3, fy, fz - math.sin(a) * 0.3), 0.08, 0.08)
    m.head_centre = (0, front + 0.3, zc + 0.1)
    return m


def chilly_mammoth():
    """Silly: a mammoth that can't get warm. A knitted hat with a bobble, a striped scarf, teeth chattering
    under its trunk, worried eyebrows and an icicle hanging off the end of its trunk."""
    m = Model("dino_ChillyMammoth", {"Body": "#8a5a3a", "Accent": "#6b4229", "Belly": "#a87650", "Claw": "#2e1e14",
                                      "Tusk": "#f2e6c8", "Knit": "#e04848", "KnitStripe": "#ffffff", "Ice": "#bdeeff", "Snow": "#f4f9ff"})
    rng = random.Random(4)
    m.joint("Spine", (0, 0, 3.0))
    quad_legs(m, 1.2, 1.5, 1.25, -1.5, 2.5, 1.1)
    body = ((-2.5, 0, 3.4, 2.7, 2.5), (1.6, 0, 3.9, 3.1, 3.1))
    m.loft_y("Body", *body)
    m.loft_y("Body", (0.2, 0, 4.6, 2.4, 2.0), (1.4, 0, 5.1, 2.1, 1.6))  # the hump
    fringe(m, "Accent", body, [-2.2, -1.5, -0.8, -0.1, 0.6, 1.3], rng, length=(0.8, 1.3), width=0.7)
    m.block("Snow", -0.4, -0.6, top_of(body, -0.6) + 0.12, 1.8, 1.4, 0.26)
    tail(m, (-2.45, 3.6, 0.5, 0.5), (-3.4, 2.6, 0.25, 0.25), 2)
    m.bone = "Tail2"
    m.block("Accent", 0, -3.45, 2.3, 0.45, 0.45, 0.6)
    m.bone = "Spine"
    # The scarf, round its neck, one end hanging down the front.
    m.block("Knit", 0, 1.75, 4.15, 2.9, 0.8, 2.5)
    for z in (3.4, 4.15, 4.9):
        m.block("KnitStripe", 0, 1.75, z, 2.94, 0.84, 0.2)
    m.block("Knit", 1.0, 2.2, 2.75, 0.62, 0.26, 1.9)
    for z in (2.2, 2.9, 3.5):
        m.block("KnitStripe", 1.0, 2.22, z, 0.66, 0.3, 0.16)
    for x in (0.8, 1.0, 1.2):
        m.block("Knit", x, 2.22, 1.7, 0.12, 0.1, 0.3)

    w, d, h = 2.2, 1.8, 2.0
    yc, zc = 2.75, 4.5
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    for side in (-1, 1):  # big flat ears
        m.block("Accent", side * (w / 2 + 0.15), yc - 0.2, zc - 0.1, 0.3, 1.4, 1.8)
        m.block("Belly", side * (w / 2 + 0.31), yc - 0.15, zc - 0.15, 0.04, 1.0, 1.3)
    kit.eyes(m, w / 2, front, zc + 0.35, 0.62, brow=0.6, look=(0, -0.1))
    # The trunk, curling forward at the end, with an icicle hanging off it.
    trunk = [((0, front - 0.1, zc - 0.25), (0, front + 0.45, zc - 1.35), 0.95, 0.8), ((0, front + 0.45, zc - 1.35), (0, front + 0.65, zc - 2.4), 0.8, 0.62),
             ((0, front + 0.65, zc - 2.4), (0, front + 1.05, zc - 2.95), 0.62, 0.5)]
    for a, b, w0, w1 in trunk:
        beam(m, "Body", a, b, w0, None, w1)
        m.block("Body", *b, w1 * 0.95, w1 * 0.95, w1 * 0.95)
    for t in (0.3, 0.65):
        a, b, w0, w1 = trunk[0]
        p = [a[i] + (b[i] - a[i]) * t for i in range(3)]
        m.block("Accent", p[0], p[1] + 0.08, p[2], w0 * 1.04, 0.3, 0.12)
    tip = trunk[-1][1]
    icicle(m, "Ice", 0.05, tip[1] + 0.1, tip[2] - 0.2, 0.75, 0.24)
    # The tusks, curving out and up.
    for side in (-1, 1):
        pts = [(side * 0.6, front - 0.05, zc - 0.85), (side * 0.85, front + 0.75, zc - 1.75), (side * 1.0, front + 1.55, zc - 1.6), (side * 0.85, front + 1.95, zc - 0.85)]
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            beam(m, "Tusk", a, b, 0.42 - i * 0.1, None, 0.32 - i * 0.1)
            if i:
                m.block("Tusk", *a, 0.34 - i * 0.08, 0.34 - i * 0.08, 0.34 - i * 0.08)
    # Chattering teeth under the trunk: a little mouth, the lower lip on the Jaw bone.
    mouth_z = zc - 0.75
    m.block("Mouth", 0, front + 0.02, mouth_z, 0.8, 0.12, 0.3)
    for x in (-0.24, 0, 0.24):
        m.block("Teeth", x, front + 0.06, mouth_z + 0.08, 0.2, 0.08, 0.16)
    m.use("Jaw", (0, front - 0.1, mouth_z), "Head")
    m.block("Belly", 0, front - 0.05, mouth_z - 0.32, 0.9, 0.4, 0.3)
    for x in (-0.24, 0, 0.24):
        m.block("Teeth", x, front + 0.17, mouth_z - 0.1, 0.2, 0.08, 0.15)
    m.bone = "Head"
    # The knitted hat, with a bobble.
    top = zc + h / 2
    m.block("Knit", 0, yc - 0.1, top + 0.4, w * 0.9, d * 0.85, 0.8)
    m.block("KnitStripe", 0, yc - 0.1, top + 0.08, w * 0.95, d * 0.9, 0.24)
    m.loft_z("Knit", (top + 0.8, 0, yc - 0.1, w * 0.9, d * 0.85), (top + 1.3, 0, yc - 0.25, w * 0.45, d * 0.4))
    m.block("KnitStripe", 0, yc - 0.3, top + 1.55, 0.6, 0.6, 0.55)
    m.head_centre = (0, front + 0.3, zc - 0.2)
    return m


# ---------------------------------------------------------------------- fierce


def sabertooth():
    """Fierce: a striped saber-toothed cat with two huge sabers, a snarl and frost-blue glowing eyes."""
    m = Model("dino_Sabertooth", {"Body": "#d2a86a", "Accent": "#4e3628", "Belly": "#f1e4c6", "Claw": "#2a221c", "Nose": "#2a1c1a",
                                   "Teeth": "#fff3dc", **FROST_EYES})
    m.joint("Spine", (0, 0, 2.6))
    quad_legs(m, 1.0, 1.4, 1.0, -1.4, 2.15, 0.85)
    body = ((-2.2, 0, 2.55, 1.7, 1.6), (1.4, 0, 2.95, 2.15, 2.1))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-1.8, 0, 1.85, 1.4, 0.4), (1.2, 0, 2.0, 1.8, 0.5))
    for y in (-1.8, -1.1, -0.4, 0.3, 1.0):
        r = ring_at(*body, y)
        for side in (-1, 1):
            beam(m, "Accent", (side * (r[3] / 2 + 0.02), y + 0.15, r[2] + r[4] * 0.45), (side * (r[3] / 2 + 0.02), y - 0.1, r[2] - r[4] * 0.05), 0.06, 0.26)
        m.block("Accent", 0, y, top_of(body, y) + 0.02, r[3] * 0.55, 0.26, 0.06)
    tail(m, (-2.15, 2.8, 0.55, 0.55), (-4.6, 3.3, 0.3, 0.3), 3)
    m.bone = "Tail3"
    m.block("Accent", 0, -4.45, 3.27, 0.36, 0.4, 0.36)
    m.use("Neck", (0, 1.4, 3.15))
    m.loft_y("Body", (1.3, 0, 3.05, 1.6, 1.6), (2.1, 0, 3.3, 1.4, 1.4))
    m.stretch("Body", "Spine")
    w, d, h = 1.8, 1.5, 1.4
    yc, zc = 2.65, 3.45
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    mouth_z, gap, up_h = zc - 0.38, 0.48, 0.38
    snout = classic_mouth(m, front, mouth_z, w, 0.8, 1.3, up_h, 0.28, gap, upper="Body", lower="Belly", tooth=0.15, per_side=3,
                          lower_teeth=True, tongue=False, grin=0.3, skull_d=d)
    edge = mouth_z + gap / 2 + 0.02
    for side in (-1, 1):  # the sabers
        x, y = side * 0.74, front + 0.42
        m.loft_z("Teeth", (edge - 1.55, x, y + 0.06, 0.06, 0.06), (edge + 0.1, x, y, 0.3, 0.38))
    ember_eyes(m, w / 2, front, zc + 0.35, 0.5, slant=0.9, squint=0.12, brow_role="Accent", wide=1.2)
    tip = snout["tip"]
    m.block("Nose", 0, tip - 0.2, snout["top"](tip - 0.2) + 0.06, 0.5, 0.4, 0.18)
    for side in (-1, 1):  # ears
        prism(m, "Body", side * 0.6, yc - 0.3, zc + h / 2 - 0.1, zc + h / 2 + 0.55, 0.32, 0.04, 4, math.pi / 4, (side * 0.08, -0.06))
        m.block("Accent", side * 0.65, yc - 0.32, zc + h / 2 + 0.38, 0.14, 0.14, 0.2)
        for k in range(3):  # whisker-pad stripes on the cheeks
            m.block("Accent", side * (w / 2 + 0.01), yc + 0.1 - k * 0.25, zc - 0.05 + k * 0.08, 0.04, 0.1, 0.4)
    m.head_centre = (0, front + 0.2, zc)
    return m


def frost_raptor():
    """Fierce: a raptor of living ice. Glowing crystals down its back and tail, an icicle crest, ice claws,
    a mouthful of icicle teeth and eyes glowing frost blue."""
    m = Model("dino_FrostRaptor", {"Body": "#6fb6e6", "Accent": "#24547f", "Belly": "#dff4ff", "Claw": "#e3fbff",
                                    "Teeth": "#eafcff", "IceGlow": "#45d6ff", **FROST_EYES})
    m.joint("Spine", (0, -0.55, 2.7))
    biped_legs(m, 0.55, -0.55, 2.2, 0.88, 1.0, 0.34, 1.05, 0.26)
    for side in (-1, 1):
        m.bone = "ShinL" if side < 0 else "ShinR"
        m.loft_y("Claw", (-0.2, side * 0.55, 0.55, 0.18, 0.26), (0.14, side * 0.55, 0.95, 0.04, 0.04))
    m.bone = "Spine"
    body = ((-1.6, 0, 2.55, 1.0, 1.0), (0.85, 0, 2.95, 1.45, 1.55))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-0.8, 0, 2.2, 0.95, 0.5), (0.9, 0, 2.48, 1.2, 0.75))
    tail(m, (-1.55, 2.58, 0.85, 0.8), (-4.8, 3.0, 0.14, 0.14), 3)
    for y, height in ((0.55, 0.9), (-0.15, 1.15), (-0.85, 1.0), (-1.45, 0.75)):
        crystal(m, "IceGlow", 0, y, top_of(body, y) - 0.05, height, 0.2, (0, -0.25 * height))
    for bone, y, z, height in (("Tail1", -2.4, 3.05, 0.6), ("Tail2", -3.4, 3.15, 0.45), ("Tail3", -4.3, 3.15, 0.3)):
        m.bone = bone
        crystal(m, "IceGlow", 0, y, z, height, 0.14, (0, -0.2 * height))
    m.bone = "Spine"
    for side in (-1, 1):
        x = side * 0.78
        m.use("ArmL" if side < 0 else "ArmR", (x, 0.6, 2.85))
        m.loft_y("Body", (0.6, x, 2.85, 0.26, 0.3), (1.35, x, 2.42, 0.18, 0.2))
        for offset in (-0.06, 0.06):
            m.loft_y("Claw", (1.32, x + offset, 2.4, 0.08, 0.11), (1.62, x + offset, 2.22, 0.03, 0.03))
    m.use("Neck", (0, 1.0, 3.35))
    m.loft_z("Body", (3.35, 0, 1.0, 1.0, 1.05), (4.2, 0, 1.35, 0.78, 0.82))
    m.stretch("Body", "Spine")
    w, d, h = 1.5, 1.55, 1.25
    yc, zc = 1.6, 4.58
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = classic_mouth(m, front, zc - 0.42, w, 1.15, 1.02, 0.4, 0.24, 0.36, tooth=0.2, per_side=4, lower_teeth=True,
                          tongue=False, grin=0.32, skull_d=d)
    ember_eyes(m, w / 2, front, zc + 0.3, 0.56, slant=0.95, squint=0.1, brow_role="Accent")
    top_nostrils(m, snout, 0.24, 0.1, role="Accent")
    for k, (y, height) in enumerate(((yc + 0.3, 0.75), (yc - 0.2, 1.0), (yc - 0.7, 0.8))):  # the icicle crest
        crystal(m, "IceGlow", 0, y, zc + h / 2 - 0.05, height, 0.18, (0, -0.45 * height))
    m.head_centre = (0, front + 0.3, zc)
    return m


def blizzard_rex():
    """Frozen Peaks' boss: a huge shaggy white rex wearing armour of glowing ice, a crown of ice crystals,
    icicles hanging off its jaw, eyes burning frost blue and frost breath pouring out of its open mouth."""
    m = Model("dino_BlizzardRex", {"Body": "#eef4fa", "Accent": "#5f86aa", "Belly": "#c9dbe8", "Claw": "#1f2a36",
                                    "Ice": "#9fdcff", "IceGlow": "#45d6ff", "Teeth": "#eafcff", "Breath": "#a9defa", "Fur": "#cbdae7", **FROST_EYES})
    rng = random.Random(9)
    m.joint("Spine", (0, -0.8, 4.4))
    biped_legs(m, 0.95, -0.8, 3.9, 1.6, 1.8, 0.75, 1.95, 0.42)
    torso = ((-2.4, 0, 4.2, 1.9, 2.0), (1.4, 0, 5.0, 2.9, 3.1))
    m.loft_y("Body", *torso)
    m.loft_y("Belly", (-1.1, 0, 3.55, 1.85, 0.85), (1.45, 0, 4.1, 2.4, 1.5))
    fringe(m, "Fur", torso, [-1.9, -1.2, -0.5, 0.2, 0.9], rng, length=(0.6, 1.1), width=0.6)
    for leg in ("LegL", "LegR"):  # shaggy thighs
        m.bone = leg
        side = -1 if leg == "LegL" else 1
        for y in (-1.2, -0.75, -0.3):
            m.block("Fur", side * (0.95 + 0.85), y, 2.6, 0.24, 0.42, rng.uniform(0.7, 1.0))
    m.bone = "Spine"
    tail(m, (-2.3, 4.25, 1.7, 1.7), (-7.2, 4.8, 0.2, 0.2), 3)
    # Ice armour: plates on the shoulders and back with glowing crystals growing out of them.
    for y, height in ((1.0, 1.5), (0.1, 1.9), (-0.8, 1.7), (-1.7, 1.3)):
        top = top_of(torso, y)
        m.block("Ice", 0, y, top + 0.05, ring_at(*torso, y)[3] * 0.62, 0.75, 0.32)
        crystal(m, "IceGlow", 0, y, top + 0.15, height, 0.36, (0, -0.3 * height))
        for side in (-1, 1):
            crystal(m, "Ice", side * 0.55, y + 0.15, top - 0.05, height * 0.55, 0.22, (side * 0.2, -0.15))
    for bone, y, z, height in (("Tail1", -3.0, 5.15, 1.0), ("Tail2", -4.3, 5.2, 0.75), ("Tail3", -5.6, 5.1, 0.5)):
        m.bone = bone
        crystal(m, "IceGlow", 0, y, z, height, 0.28, (0, -0.25 * height))
    m.bone = "Spine"
    for side in (-1, 1):
        m.use("ArmL" if side < 0 else "ArmR", (side * 1.42, 1.2, 4.85))
        m.loft_y("Body", (1, side * 1.42, 4.85, 0.36, 0.38), (1.8, side * 1.42, 4.45, 0.26, 0.26))
        m.block("Fur", side * 1.42, 1.3, 4.45, 0.42, 0.5, 0.6)
        m.block("Ice", side * 1.42, 1.55, 4.85, 0.46, 0.5, 0.34)
        for offset in (-0.08, 0.08):
            m.loft_y("Claw", (1.76, side * 1.42 + offset, 4.42, 0.09, 0.11), (2.06, side * 1.42 + offset, 4.3, 0.03, 0.03))
    m.use("Neck", (0, 1.5, 5.9))
    m.loft_z("Body", (5.9, 0, 1.5, 2.1, 2.2), (6.65, 0, 1.95, 1.85, 1.85))
    m.stretch("Body", "Spine")
    for k in range(7):  # a shaggy mane round the neck
        a = -math.pi * 0.85 + k * math.pi * 1.7 / 6
        m.block("Fur", math.cos(a) * 1.15, 1.55 + math.sin(a) * 0.2 - 0.3, 6.3 + rng.uniform(-0.2, 0.2), 0.5, 0.5, 1.1)
    w, d, h = 2.7, 2.6, 1.95
    yc, zc = 2.9, 7.3
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)

    def frost_breath(m, front, mouth_z, gap, lower_length):
        # icicles hanging off the chin, and frost breath rolling out over the lower teeth
        for x in (-0.75, -0.25, 0.3, 0.8):
            icicle(m, "Ice", x, front + lower_length * 0.55, mouth_z - gap / 2 - 0.5, rng.uniform(0.5, 0.9), 0.24)
        base = mouth_z - gap / 2 + 0.25
        for dx, dy, dz, s in ((0.0, 0.55, 0.0, 0.6), (0.15, 1.15, 0.3, 0.8), (-0.1, 1.75, 0.75, 0.65), (0.1, 2.2, 1.2, 0.45)):
            m.block("Breath", dx, front + lower_length + dy, base + dz, s, s, s * 0.85)

    mouth_z = zc - 0.62
    snout = classic_mouth(m, front, mouth_z, w, 2.0, 2.15, 0.62, 0.5, 0.75, tooth=0.36, per_side=5, lower_teeth=True,
                          tongue=False, grin=0.42, skull_d=d, on_jaw=frost_breath)
    ember_eyes(m, w / 2, front, zc + 0.5, 0.82, slant=1.0, squint=0.15, brow_role="Accent")
    top_nostrils(m, snout, 0.55, 0.2, role="Accent")
    # The crown of ice.
    top = zc + h / 2
    for x, y, height in ((0, yc - 0.8, 2.0), (0.9, yc - 0.45, 1.5), (-0.9, yc - 0.45, 1.5), (1.15, yc + 0.5, 1.0), (-1.15, yc + 0.5, 1.0)):
        lean = (0.22 * height * (1 if x > 0 else -1 if x < 0 else 0), -0.15 * height)
        crystal(m, "IceGlow" if x == 0 or abs(x) > 1 else "Ice", x, y, top - 0.15, height, 0.32, lean)
    for x in (-0.95, -0.4, 0.4, 0.95):  # frost on the brow
        m.block("Ice", x, front - 0.55, top + 0.08, 0.38, 0.6, 0.18)
    m.head_centre = (0, front + 0.6, zc)
    return m


def main():
    models = [brain_freeze(), woolly_rhino(), chilly_mammoth(), sabertooth(), frost_raptor(), blizzard_rex()]
    build_and_render(models, RENDERS, HERE / "frozen_peaks_monsters.blend", "frozen_peaks_animation_preview.mp4",
                     sky="#bcd9f2", ground="#d3e1ec", glow_roles=GLOW_ROLES, spacing=18)


if __name__ == "__main__":
    main()
