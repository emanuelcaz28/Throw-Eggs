"""Builds the Swamp's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_swamp_monsters.py

Saves swamp_monsters.blend and renders to design/world/monsters_swamp/. The Swamp's props are in build_swamp.py.

The Swamp sits between Desert and the Volcano, so its faces are the first maps' kind (white eyes, a pupil
and a highlight, a dark mouth) and its rare ones are fiercer than Desert'. They have the Volcano's Jaw
bone, so they snap and roar like it. Ids keep the old stand-ins' (Bary, Dilo, Sarco, Brachio, Spino), so
monsters players already own get the new models: Burpasaurus is dino_Dilo, Sir Chomps-a-Lot dino_Sarco,
Neckzilla dino_Brachio. Built at the first map's size; the game makes them 1.9x.
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
from build_swamp import round_slab  # noqa: E402
from build_volcano import prism, ring_at, top_of  # noqa: E402
from face_kit import classic_mouth, icicle, top_nostrils  # noqa: E402
from monster_stage import build_and_render  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_swamp"


def lerp_table(table, y):
    """Values along y from a table of (y, a, b, ...) rows sorted by y descending."""
    for top, bottom in zip(table, table[1:]):
        if bottom[0] <= y <= top[0]:
            t = (y - top[0]) / (bottom[0] - top[0])
            return [a + (b - a) * t for a, b in zip(top[1:], bottom[1:])]
    return list(table[0][1:] if y > table[0][0] else table[-1][1:])


def soggy_dimetrodon():
    """Silly: a sail-back that fell in the swamp and never dried off. Its sail flops over to one side, a lily
    pad is stuck on its head, it drips everywhere and it's miserable about all of it."""
    m = Model("dino_Dimetro", {"Body": "#6f9a7a", "Accent": "#c9734a", "Belly": "#d8d6a8", "Claw": "#3b4a3f",
                               "Rib": "#8a4a2f", "Pad": "#7cc24a", "PadDark": "#5aa23a", "Drip": "#8fd8ff"})
    m.joint("Spine", (0, 0, 1.3))
    quad_legs(m, 0.95, 1.1, 1.0, -1.2, 1.05, 0.6)
    body = ((-2.2, 0, 1.25, 1.6, 1.1), (1.8, 0, 1.35, 2.0, 1.3))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-1.8, 0, 0.82, 1.4, 0.3), (1.6, 0, 0.82, 1.7, 0.36))
    tail(m, (-2.1, 1.2, 0.9, 0.7), (-4.9, 0.75, 0.14, 0.14), 3)
    # The sail, soaked through and flopped over: a lower and an upper strip, the upper one leaning further.
    sail = [(1.5, 0.9, 0.12), (0.3, 2.6, 0.6), (-0.9, 2.5, 0.8), (-2.0, 1.0, 0.35)]  # y, height, droop
    lower, upper = [], []
    for y, h, droop in sail:
        base = top_of(body, y) - 0.1
        lower.append((y, droop * 0.3, base + h * 0.27, 0.14, h * 0.55))
        upper.append((y, droop, base + h * 0.75, 0.14, h * 0.5))
    for a, b in zip(lower, lower[1:]):
        m.loft_y("Accent", a, b)
    for a, b in zip(upper, upper[1:]):
        m.loft_y("Accent", a, b)
    for y in (1.1, 0.5, -0.1, -0.7, -1.3, -1.8):
        h, droop = lerp_table(sail, y)
        base = top_of(body, y) - 0.1
        beam(m, "Rib", (0, y, base), (droop * 0.3 + 0.1, y, base + h * 0.5), 0.12)
        beam(m, "Rib", (droop * 0.3 + 0.1, y, base + h * 0.5), (droop + 0.1, y, base + h + 0.1), 0.12)
        if y < 1:
            icicle(m, "Drip", droop + 0.12, y + 0.2, base + h * 0.55, 0.35, 0.14)

    w, d, h = 1.5, 1.3, 0.95
    yc, zc = 2.35, 1.5
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2

    def droopy_tongue(m, front, mouth_z, gap, lower_length):
        m.loft_y("Tongue", (front + lower_length * 0.55, 0.38, mouth_z - gap / 2 + 0.05, 0.36, 0.1),
                 (front + lower_length + 0.3, 0.46, mouth_z - gap / 2 - 0.5, 0.3, 0.1))

    m.block("Body", 0, yc, zc, w, d, h)
    snout = classic_mouth(m, front, zc - 0.25, w, 0.95, 1.35, 0.3, 0.24, 0.16, grin=-0.12, skull_d=d, on_jaw=droopy_tongue)
    kit.eyes(m, w / 2, front, zc + 0.38, 0.62, lid=0.5, brow=0.3, look=(0, -0.12))
    top_nostrils(m, snout, 0.3, 0.11)
    icicle(m, "Drip", 0.3, snout["tip"] + 0.06, snout["top"](snout["tip"]) - 0.2, 0.4, 0.14)
    top = zc + h / 2
    round_slab(m, "Pad", 0.15, yc - 0.15, top + 0.06, 1.35, 0.12)
    m.block("PadDark", 0.55, yc - 0.15, top + 0.13, 0.5, 0.16, 0.04)
    for x, y in ((0.85, yc - 0.1), (-0.5, yc + 0.45), (0.2, yc - 0.85)):
        icicle(m, "Drip", x, y, top + 0.02, 0.45, 0.15)
    m.head_centre = (0, front + 0.2, zc + 0.15)
    return m


def burpasaurus():
    """Silly: a pot-bellied crested dino caught mid-burp. Frill flared, cheeks puffed, a green cloud rolling out
    of its mouth, and its eyes wide with surprise at itself."""
    m = Model("dino_Dilo", {"Body": "#7fbf5a", "Accent": "#f2c94c", "Belly": "#e9f2b0", "Claw": "#3e5a2a",
                            "Crest": "#e2563a", "Burp": "#c8ecb0"})
    m.joint("Spine", (0, -0.4, 2.6))
    biped_legs(m, 0.6, -0.4, 2.2, 0.95, 1.05, 0.38, 1.05, 0.28)
    body = ((-1.6, 0, 2.55, 1.2, 1.2), (0.9, 0, 2.85, 1.8, 2.0))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-0.6, 0, 2.2, 1.35, 0.9), (1.05, 0, 2.55, 1.75, 1.5))
    tail(m, (-1.55, 2.6, 1.0, 0.95), (-4.6, 3.0, 0.14, 0.14), 3)
    for x, y in ((0.35, 0.3), (-0.3, -0.4), (0.25, -1.1), (-0.2, 0.7)):
        m.block("Crest", x, y, top_of(body, y) + 0.03, 0.32, 0.32, 0.1)
    for side in (-1, 1):
        x = side * 0.88
        m.use("ArmL" if side < 0 else "ArmR", (x, 0.6, 2.95))
        m.loft_y("Body", (0.6, x, 2.95, 0.26, 0.3), (1.25, x, 2.6, 0.2, 0.22))
        for offset in (-0.06, 0.06):
            m.loft_y("Claw", (1.22, x + offset, 2.58, 0.07, 0.1), (1.48, x + offset, 2.45, 0.03, 0.03))
    m.use("Neck", (0, 0.9, 3.5))
    m.loft_z("Body", (3.4, 0, 0.95, 1.0, 1.05), (4.3, 0, 1.25, 0.85, 0.9))
    m.stretch("Body", "Spine")
    # The frill, flared out round its neck.
    for side in (-1, 1):
        m.loft_x("Accent", (side * 0.4, 1.15, 4.0, 0.25, 0.9), (side * 1.4, 1.0, 4.35, 0.15, 1.7))
        m.block("Crest", side * 1.1, 1.0, 4.3, 0.22, 0.18, 0.3)
        m.loft_z("Accent", (4.3, side * 0.32, 1.0, 0.6, 0.2), (5.05, side * 0.75, 0.9, 0.95, 0.15))

    w, d, h = 1.35, 1.4, 1.1
    yc, zc = 1.6, 4.65
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = classic_mouth(m, front, zc - 0.38, w, 0.95, 0.95, 0.36, 0.26, 0.42, tooth=0.14, per_side=3, skull_d=d)
    for side in (-1, 1):  # puffed-out cheeks
        m.block("Body", side * (w / 2 + 0.12), front - 0.3, zc - 0.22, 0.3, 0.6, 0.55)
    kit.eyes(m, w / 2, front, zc + 0.36, 0.66, brow=0.55, look=(0, 0.12))
    top_nostrils(m, snout, 0.22, 0.1)
    for side in (-1, 1):  # two tall crests
        m.loft_y("Crest", (yc - 0.7, side * 0.28, zc + h / 2 + 0.1, 0.12, 0.2), (yc + 0.5, side * 0.28, zc + h / 2 + 0.5, 0.12, 0.85))
    # The burp, rolling out of the far corner of its mouth and up past its cheek, clear of its face.
    for x, dy, dz, s in ((-0.75, 0.75, -0.4, 0.42), (-1.15, 0.6, -0.05, 0.56), (-1.4, 0.35, 0.45, 0.46), (-1.5, 0.1, 0.9, 0.32)):
        m.block("Burp", x, front + dy, zc + dz, s, s, s * 0.9)
    m.head_centre = (0, front + 0.3, zc + 0.15)
    return m


def baryonyx():
    """A fishing dino with a long croc snout, big hooked thumb claws and a fish it has no plans to share."""
    m = Model("dino_Bary", {"Body": "#4f7f6a", "Accent": "#2f4f45", "Belly": "#d9e0b8", "Claw": "#1f2a26",
                            "Fish": "#b8c9d6", "FishFin": "#e07b54"})
    m.joint("Spine", (0, -0.6, 3.0))
    biped_legs(m, 0.62, -0.6, 2.7, 1.0, 1.15, 0.42, 1.2, 0.3)
    body = ((-1.9, 0, 3.0, 1.2, 1.2), (1.0, 0, 3.45, 1.6, 1.7))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-1.0, 0, 2.55, 1.15, 0.55), (1.05, 0, 2.9, 1.4, 0.85))
    tail(m, (-1.85, 3.0, 1.0, 0.95), (-5.6, 3.3, 0.15, 0.15), 3)
    for y in (-1.5, -0.8, -0.1, 0.6):
        m.block("Accent", 0, y, top_of(body, y) + 0.02, ring_at(*body, y)[3] * 0.9, 0.3, 0.08)
    for side in (-1, 1):
        x = side * 0.86
        m.use("ArmL" if side < 0 else "ArmR", (x, 0.8, 3.3))
        m.loft_y("Body", (0.7, x, 3.3, 0.28, 0.3), (1.55, x, 2.8, 0.2, 0.22))
        m.loft_y("Claw", (1.45, x, 2.88, 0.15, 0.22), (1.9, x, 3.12, 0.03, 0.03))  # the big hooked thumb
        m.loft_y("Claw", (1.5, x + side * 0.07, 2.72, 0.07, 0.1), (1.72, x + side * 0.07, 2.62, 0.03, 0.03))
    m.use("Neck", (0, 1.1, 4.0))
    m.loft_z("Body", (4.0, 0, 1.15, 1.05, 1.1), (4.6, 0, 1.45, 0.9, 0.9))
    m.stretch("Body", "Spine")

    w, d, h = 1.25, 1.3, 1.0
    yc, zc = 1.8, 4.9
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)

    def fish(m, front, mouth_z, gap, lower_length):
        y, z = front + lower_length * 0.55, mouth_z
        m.loft_x("Fish", (-0.95, y, z, 0.32, 0.45), (0.5, y, z + 0.05, 0.36, 0.6))
        m.loft_x("Fish", (0.5, y, z + 0.05, 0.36, 0.6), (1.0, y, z, 0.2, 0.25))
        m.loft_x("FishFin", (1.0, y, z, 0.12, 0.2), (1.45, y, z + 0.1, 0.1, 0.75))
        m.block("FishFin", 0.1, y, z + 0.38, 0.5, 0.08, 0.18)
        for side in (-1, 1):
            m.block("Pupil", -0.72, y + side * 0.17, z + 0.06, 0.1, 0.04, 0.1)

    snout = classic_mouth(m, front, zc - 0.32, w, 1.8, 0.72, 0.3, 0.22, 0.3, tooth=0.13, per_side=6, lower_teeth=True,
                          tongue=False, grin=0.2, skull_d=d, on_jaw=fish)
    kit.eyes(m, w / 2, front, zc + 0.38, 0.56, brow=-0.35, look=(0.04, 0))
    top_nostrils(m, snout, 0.18, 0.1)
    m.block("Accent", 0, front + 0.55, snout["top"](front + 0.55) + 0.06, 0.3, 0.7, 0.14)
    m.head_centre = (0, front + 0.5, zc)
    return m


def sir_chomps_a_lot():
    """A giant crocodile of great importance: a monocle, one gold tooth, a smug half-lidded look and far too
    many teeth in a grin that goes all the way back."""
    m = Model("dino_Sarco", {"Body": "#5a6b3a", "Accent": "#3a452a", "Belly": "#d6cf9a", "Claw": "#22281a", "Gold": "#ffc93a"})
    m.joint("Spine", (0, 0, 1.2))
    quad_legs(m, 1.2, 1.3, 1.25, -1.5, 1.0, 0.75)
    body = ((-2.8, 0, 1.1, 2.2, 1.1), (1.8, 0, 1.2, 2.6, 1.3))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-2.4, 0, 0.62, 2.0, 0.24), (1.6, 0, 0.62, 2.3, 0.26))
    for i in range(8):
        y = -2.5 + i * 0.6
        for x in (-0.45, 0.45):
            m.block("Accent", x, y, top_of(body, y) + 0.08, 0.6, 0.45, 0.22)
    tail(m, (-2.7, 1.1, 1.4, 0.9), (-6.8, 0.8, 0.25, 0.2), 3)
    for bone, ys in (("Tail1", (-3.1, -3.8)), ("Tail2", (-4.5, -5.1)), ("Tail3", (-5.8, -6.3))):
        m.bone = bone
        for y in ys:
            t = (y + 2.7) / -4.1
            z = 1.1 - 0.3 * t + (0.9 - 0.7 * t) / 2
            for x in (-0.25, 0.25):
                m.loft_z("Accent", (z - 0.05, x, y, 0.35, 0.35), (z + 0.3, x, y, 0.06, 0.06))
    m.bone = "Spine"

    w, d, h = 2.0, 1.5, 1.1
    yc, zc = 2.6, 1.3
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = classic_mouth(m, front, zc - 0.22, w, 2.6, 1.3, 0.34, 0.26, 0.14, tooth=0.22, per_side=7, lower_teeth=True,
                          tongue=False, grin=0.4, skull_d=d, gold=(1, 2))
    bump = snout["tip"] - 0.35
    m.block("Accent", 0, bump, snout["top"](bump) + 0.1, 0.75, 0.5, 0.22)
    top_nostrils(m, snout, 0.3, 0.12)
    eye_half, size, eye_z = w / 2 - 0.15, 0.5, zc + 0.62
    kit.eyes(m, eye_half, front, eye_z, size, lid=0.35, brow=-0.3)
    # The monocle on its right eye, chain and all.
    cx = eye_half + size * 0.22 - size * 0.45
    fy = front - size * 0.3 + size / 2 + 0.07
    for dz in (-0.36, 0.36):
        m.block("Gold", cx, fy, eye_z + dz, 0.7, 0.08, 0.08)
    for dx in (-0.33, 0.33):
        m.block("Gold", cx + dx, fy, eye_z, 0.08, 0.08, 0.8)
    beam(m, "Gold", (cx + 0.33, fy, eye_z - 0.36), (cx + 0.75, front - 0.7, zc - 0.4), 0.05)
    m.head_centre = (0, front + 0.8, zc + 0.3)
    return m


def neckzilla():
    """A swamp sauropod with a neck far too long and a temper to match: a small head with fangs and a glare,
    spines down its neck, moss and reeds growing on its back and vines hanging off its belly."""
    m = Model("dino_Brachio", {"Body": "#3f6b5a", "Accent": "#a7c957", "Belly": "#c9d4a0", "Claw": "#24352c",
                               "Spike": "#22382f", "Reed": "#6aa03c", "ReedHead": "#6b3f22", "Vine": "#4f8f34"})
    rng = random.Random(5)
    m.joint("Spine", (0, 0, 4.4))
    for x, y, top, width, name in ((-1.15, 1.4, 4.7, 1.05, "FrontL"), (1.15, 1.4, 4.7, 1.05, "FrontR"),
                                   (-1.2, -1.6, 4.1, 1.15, "BackL"), (1.2, -1.6, 4.1, 1.15, "BackR")):
        m.use(name, (x, y, top))
        m.loft_z("Body", (0.3, x, y, width * 0.85, width * 0.85), (top + 0.3, x, y, width, width * 1.1))
        m.block("Belly", x, y + 0.1, 0.16, width * 1.05, width * 1.15, 0.32)
        for offset in (-0.3, 0, 0.3):
            m.block("Claw", x + offset * width, y + width * 0.62, 0.14, 0.18, 0.2, 0.26)
    m.bone = "Spine"
    body = ((-2.4, 0, 4.3, 2.4, 2.2), (1.9, 0, 5.0, 2.9, 2.8))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-2.0, 0, 3.3, 2.1, 0.4), (1.7, 0, 3.7, 2.5, 0.5))
    # Moss on its back, reeds growing out of it, vines hanging off its sides.
    for y, w in ((-1.6, 1.6), (-0.4, 2.0), (0.9, 1.7)):
        m.block("Accent", rng.uniform(-0.2, 0.2), y, top_of(body, y) + 0.06, w, 1.0, 0.18)
    for x, y in ((0.4, -0.5), (-0.3, -0.2), (0.1, 0.9), (-0.5, -1.5)):
        z = top_of(body, y)
        for k in range(3):
            tip = (x + rng.uniform(-0.4, 0.4), y + rng.uniform(-0.3, 0.3), z + rng.uniform(1.3, 2.0))
            beam(m, "Reed", (x, y, z), tip, 0.1)
            m.block("ReedHead", *(tip[0], tip[1], tip[2] - 0.3), 0.22, 0.22, 0.55)
    for side in (-1, 1):
        for y in (-1.6, -0.6, 0.4, 1.3):
            r = ring_at(*body, y)
            icicle(m, "Vine", side * (r[3] / 2 + 0.05), y, r[2] - r[4] * 0.1, rng.uniform(0.9, 1.8), 0.16)
    tail(m, (-2.3, 4.4, 1.3, 1.2), (-6.8, 3.0, 0.2, 0.2), 3)
    m.use("Neck", (0, 1.9, 5.6))
    neck = [((0, 1.7, 5.4), (0, 2.7, 9.0), 1.7, 1.25), ((0, 2.7, 9.0), (0, 3.4, 12.0), 1.25, 0.95)]
    for a, b, w0, w1 in neck:
        beam(m, "Body", a, b, w0, None, w1)
    m.block("Body", 0, 2.7, 9.0, 1.3, 1.3, 1.3)
    for a, b, w0, w1 in neck:
        for t in (0.2, 0.5, 0.8):
            px, py, pz = (a[i] + (b[i] - a[i]) * t for i in range(3))
            half = (w0 + (w1 - w0) * t) / 2
            prism(m, "Spike", 0, py - half * 0.95, pz - 0.1, pz + 0.55, 0.26, 0.03, 4, math.pi / 4, (0, -0.3))

    w, d, h = 1.4, 1.5, 1.05
    yc, zc = 3.9, 12.5
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = classic_mouth(m, front, zc - 0.3, w, 0.9, 1.05, 0.3, 0.24, 0.28, tooth=0.17, per_side=3, lower_teeth=True,
                          tongue=False, grin=0.3, skull_d=d)
    kit.eyes(m, w / 2, front, zc + 0.38, 0.52, lid=0.15, brow=-0.6)
    top_nostrils(m, snout, 0.25, 0.11)
    m.block("Body", 0, yc + 0.05, zc + h / 2 + 0.22, 0.9, 0.9, 0.45)  # the arch over its nose
    for y in (yc - 0.4, yc + 0.15):
        prism(m, "Spike", 0, y, zc + h / 2 + 0.35, zc + h / 2 + 0.95, 0.24, 0.03, 4, math.pi / 4, (0, -0.25))
    m.head_centre = (0, front + 0.2, zc)
    return m


def spinosaurus():
    """The Swamp's boss: a huge sail-back with a blood-red sail ragged at the top, a long croc jaw full of
    fangs, hooked claws and the meanest glare in the swamp."""
    m = Model("dino_Spino", {"Body": "#2e4a3e", "Accent": "#9b2f2f", "Belly": "#c9c18f", "Claw": "#141a16",
                             "Rib": "#1d2b25", "SailStripe": "#e0a23a"})
    m.joint("Spine", (0, -0.8, 4.0))
    biped_legs(m, 0.9, -0.8, 3.6, 1.4, 1.6, 0.65, 1.8, 0.38)
    torso = ((-2.2, 0, 3.9, 1.7, 1.8), (1.4, 0, 4.6, 2.4, 2.7))
    m.loft_y("Body", *torso)
    m.loft_y("Belly", (-1.0, 0, 3.25, 1.65, 0.75), (1.45, 0, 3.75, 2.1, 1.3))
    tail(m, (-2.1, 3.95, 1.5, 1.5), (-7.2, 4.4, 0.2, 0.2), 3)
    # The sail: a red membrane, gold bands across it, ribs poking out of its ragged top.
    sail = [(1.3, 1.6), (0.4, 3.6), (-0.6, 4.6), (-1.6, 3.8), (-2.4, 1.6)]
    rings = []
    for y, h in sail:
        base = top_of(torso, min(max(y, -2.2), 1.4)) - 0.15
        rings.append((y, 0, base + h / 2, 0.2, h))
    for a, b in zip(rings, rings[1:]):
        m.loft_y("Accent", a, b)
    for band in (0.45, 0.72):
        for a, b in zip(rings, rings[1:]):
            m.loft_y("SailStripe", (a[0], 0, a[2] - a[4] / 2 + a[4] * band, 0.26, 0.18), (b[0], 0, b[2] - b[4] / 2 + b[4] * band, 0.26, 0.18))
    for i in range(9):
        y = 1.2 - i * 0.43
        h = lerp_table([(1.3, 1.6), (0.4, 3.6), (-0.6, 4.6), (-1.6, 3.8), (-2.4, 1.6)], y)[0]
        base = top_of(torso, min(max(y, -2.2), 1.4)) - 0.15
        poke = 0.25 + 0.45 * (i % 3) / 2
        m.loft_z("Rib", (base, 0, y, 0.22, 0.22), (base + h + poke, 0, y, 0.05, 0.05))
    for side in (-1, 1):
        x = side * 1.25
        m.use("ArmL" if side < 0 else "ArmR", (x, 1.1, 4.5))
        m.loft_y("Body", (0.9, x, 4.5, 0.36, 0.4), (1.9, x, 3.9, 0.26, 0.28))
        for offset in (-0.09, 0.09):
            m.loft_y("Claw", (1.85, x + offset, 3.85, 0.1, 0.14), (2.25, x + offset, 3.95, 0.03, 0.03))
    m.use("Neck", (0, 1.3, 5.4))
    m.loft_z("Body", (5.3, 0, 1.3, 1.6, 1.7), (6.1, 0, 1.75, 1.35, 1.35))
    m.stretch("Body", "Spine")

    w, d, h = 1.7, 2.0, 1.45
    yc, zc = 2.6, 6.75
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = classic_mouth(m, front, zc - 0.45, w, 2.3, 1.05, 0.42, 0.32, 0.45, tooth=0.25, per_side=6, lower_teeth=True,
                          tongue=False, grin=0.4, skull_d=d)
    kit.eyes(m, w / 2, front, zc + 0.5, 0.6, lid=0.2, brow=-0.7)
    top_nostrils(m, snout, 0.3, 0.13)
    m.loft_y("Accent", (front + 0.3, 0, snout["top"](front + 0.3) + 0.1, 0.3, 0.2), (front + 1.6, 0, snout["top"](front + 1.6) + 0.18, 0.25, 0.36))
    m.head_centre = (0, front + 0.6, zc)
    return m


def main():
    models = [soggy_dimetrodon(), burpasaurus(), baryonyx(), sir_chomps_a_lot(), neckzilla(), spinosaurus()]
    build_and_render(models, RENDERS, HERE / "swamp_monsters.blend", "swamp_animation_preview.mp4",
                     sky="#b9d4a6", ground="#4e8466", spacing=18)


if __name__ == "__main__":
    main()
