"""Builds Volcano' monsters and props, animates the monsters and renders it all (Blender, background mode).

    Blender -b -P build_volcano.py

Saves volcano_models.blend and renders to design/world/models_volcano/, with an animation preview
(volcano_animation_preview.mp4). The monsters have every map's bones, so the game's walk and idle work
unchanged, plus a new Jaw bone: DinoLifeController snaps it as they walk and opens it wide in a roar once
per idle. walk_pose and idle_pose here are the same movements, keep the two in step.

The owner asked for meaner monsters with a different face on this map. The Volcano face: eyes that glow
like embers, with a slit pupil, under a heavy brow that slants down to the nose; and a snarl that glows
inside like a furnace, jagged teeth top and bottom and often tusks. The silly ones keep their jokes (a
raptor still smoking from the lava, an ankylo whose tail is on fire, a trike that ate the hot sauce), the
rare ones are lava and obsidian, and Volcano King is the map's boss: a hulking lava monster with a crown
of burning horns and a volcano erupting on its back.

Glowing parts (Lava, Ember, Flame, Furnace, EyeGlow) get the Neon material in the game (shared/Roles.luau)
and are left without the stud texture. Monsters are built at the first map's size; the game makes them
2.7x (Config/Biomes standardScale). 1 Blender unit = 1 stud, models face +Y, feet on Z = 0.
"""
import math
import random
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_desert import beam, quad_legs  # noqa: E402
from build_forest import Model, biped_legs, tail  # noqa: E402
from build_swamp import place_copy  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "models_volcano"

GLOW_ROLES = {"EyeGlow", "Furnace", "Lava", "Ember", "Flame"}  # lit from inside: Neon in the game
kit.NO_STUDS.update(GLOW_ROLES)

# The Volcano face's colours. Pupil, Highlight, Mouth and Teeth keep their roles from the first maps, so
# mutations leave them alone as before.
FACE = {"EyeGlow": "#ffb321", "Pupil": "#1c1015", "Highlight": "#fff7dc", "Furnace": "#ff5a1f", "Mouth": "#2e1013", "Teeth": "#fff1d6"}

# The corridor's Volcano colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#5d4b45", "FloorB": "#514039", "Dirt": "#3d302e", "DirtB": "#342927", "Grass": "#74402e"}
SKY = "#e6a47f"

GAME_SCALE = 2.7  # Config/Biomes standardScale for this map


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


def prop(name, **colours):
    return Model(f"prop_{name}", colours)


# ---------------------------------------------------------------------- shape helpers


def ring_at(a, b, y):
    """A loft_y's rectangle at y, between its two ends a and b: (y, centre x, centre z, width, height)."""
    t = (y - a[0]) / (b[0] - a[0])
    return [a[k] + (b[k] - a[k]) * t for k in range(5)]


def top_of(pair, y):
    r = ring_at(*pair, y)
    return r[2] + r[4] / 2


def flank_vein(m, pair, side, spots, role="Lava", wide=0.16, thick=0.1):
    """A glowing crack across one side of a body loft. spots are (y, height share: -1 bottom, 1 top)."""
    points = []
    for y, f in spots:
        r = ring_at(*pair, y)
        points.append((side * (r[3] / 2 + 0.015), y, r[2] + f * r[4] / 2))
    for p, q in zip(points, points[1:]):
        beam(m, role, p, q, thick, wide)


def crack(m, points, flat=False, role="Lava", wide=0.18, thick=0.08):
    """A zigzag crack along points on a flat face. flat: the face is level (a top), else upright."""
    for p, q in zip(points, points[1:]):
        if flat:
            beam(m, role, p, q, wide, thick)
        else:
            beam(m, role, p, q, thick, wide)


def prism(m, role, x, y, z0, z1, r0, r1=None, sides=6, turn=0.0, lean=(0, 0)):
    """An upright n-sided column from z0 to z1, radius r0 at the foot and r1 at the top; lean moves the top."""
    r1 = r0 if r1 is None else r1
    verts = []
    for z, r, (dx, dy) in ((z0, r0, (0, 0)), (z1, r1, lean)):
        for i in range(sides):
            a = turn + i * math.tau / sides
            verts.append((x + dx + r * math.cos(a), y + dy + r * math.sin(a), z))
    faces = [list(range(sides))[::-1], list(range(sides, 2 * sides))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides + j, sides + i])
    m._add(role, verts, faces)


def thigh_crack(m, side, x, hip_y, hip_z, thigh_w, thigh_h, heights, wide=0.18):
    """A glowing crack down the outside of a biped_legs thigh, through the given heights."""
    points = []
    for i, z in enumerate(heights):
        t = (z - (hip_z - thigh_h)) / (1.2 * thigh_h)
        points.append((side * (x + thigh_w * (0.36 + 0.14 * t) + 0.02), hip_y + thigh_w * 0.1 * t + (0.18 if i % 2 else -0.18), z))
    crack(m, points, wide=wide)


def strand(m, role, x, y, top, length, width=0.5):
    m.block(role, x, y, top - length / 2, width, width, length)


def pick_side(value, side):
    return value[0 if side < 0 else 1] if isinstance(value, tuple) else value


# ---------------------------------------------------------------------- the Volcano face


def ember_eyes(m, half_width, front_y, z, size, slant=0.6, squint=0.0, look=(0, 0), brow_role="Accent", wrap=0.14,
               wide=1.25, horn=0.0, horn_role="Accent", cheek_role="Body"):
    """Eyes that glow like embers, wider than tall, with an upright slit pupil and a heavy brow that slants
    down towards the nose, so the look is narrowed and angry from the front.

    slant: how far the brow drops at its inner end. squint pushes the cheek up over the bottom of the eye.
    horn puts a spike on the brow's outer end. slant, squint and look can be a pair, one per eye (left
    first), for a twitchy, lopsided rage. Returns each eye's centre x, front face y and top and bottom z.
    """
    found = []
    for side in (-1, 1):
        outer = side * (half_width + size * wrap)
        w, d, h = size * wide, size * 0.9, size * 0.8
        cx = outer - side * w / 2
        cy = front_y - size * 0.32
        front = cy + d / 2
        m.block("EyeGlow", cx, cy, z, w, d, h)

        look_pair = look[0 if side < 0 else 1] if isinstance(look[0], tuple) else look
        px, pz = look_pair
        pw, ph = size * 0.2, h * 0.84
        pupil_x = cx - side * w * 0.1 + side * px * size  # a little towards the nose: a glare, not a stare
        pupil_z = z + pz * size - h * 0.03
        m.block("Pupil", pupil_x, front + size * 0.02, pupil_z, pw, size * 0.08, ph)
        glint = size * 0.16
        m.block("Highlight", pupil_x + side * pw * 0.45, front + size * 0.07, pupil_z + ph * 0.3, glint, size * 0.05, glint)

        top = z + h / 2
        bh = size * 0.36
        x_in = cx - side * (w / 2 + size * 0.1)
        x_out = outer + side * size * 0.1
        z_in = top - pick_side(slant, side) * size * 0.3 + bh * 0.2
        z_out = top + bh * 0.25
        brow_y = cy + size * 0.12
        brow_d = d + size * 0.3
        m.loft_x(brow_role, (x_in, brow_y, z_in, brow_d, bh), (x_out, brow_y, z_out, brow_d, bh))

        lid = pick_side(squint, side)
        if lid:
            m.block(cheek_role, cx, cy + size * 0.06, z - h / 2 + lid * h / 2 - size * 0.02, w + size * 0.08, d + size * 0.14, lid * h + size * 0.04)
        if horn:
            hx = x_out - side * size * 0.28
            hz = z_out + bh * 0.4
            m.loft_z(horn_role, (hz - bh * 0.5, hx, brow_y - size * 0.1, size * 0.36, size * 0.44),
                     (hz + horn * size, hx + side * horn * size * 0.3, brow_y - size * 0.5, size * 0.04, size * 0.04))
        found.append({"x": cx, "front": front, "top": top, "bottom": z - h / 2})
    return found


def snarl(m, front, mouth_z, skull_w, length, snout_w, upper_h, lower_h, gap, upper="Body", lower="Belly",
          tooth=0.22, per_side=4, tusk=0.0, grin=0.0, skull_d=1.0, underbite=1.0, on_jaw=None):
    """The Volcano mouth: open in a snarl and glowing inside like a furnace, jagged teeth top and bottom,
    and with tusk, two lower fangs jutting up past the upper lip. The lower jaw is on its own Jaw bone, so
    the game can snap it as the monster walks and drop it wide in a roar; a dark throat behind the glow
    fills the mouth when it opens. on_jaw(m, front, mouth_z, gap, lower_length) adds more to the jaw.

    Call it on the Head bone. Returns the snout's tip and its top height along it, for nostrils and horns.
    """
    upper_z = mouth_z + gap / 2 + upper_h / 2
    lower_z = mouth_z - gap / 2 - lower_h / 2
    back = (front - 0.05, 0, upper_z + upper_h * 0.1, skull_w * 0.94, upper_h * 1.2)
    tip = (front + length, 0, upper_z, snout_w, upper_h)
    m.loft_y(upper, back, tip)
    m.block("Furnace", 0, front + length * 0.45, mouth_z + gap * 0.05, snout_w * 0.84, length * 0.9, gap + 0.04)
    m.block("Mouth", 0, front + 0.05, mouth_z - lower_h * 0.45, snout_w * 0.78, 0.12, gap + lower_h * 0.9)
    edge = mouth_z + gap / 2 + 0.02
    for side in (-1, 1):
        for i in range(per_side):
            y = front + length * (0.14 + 0.72 * i / max(per_side - 1, 1))
            size = tooth * (1.0 if i % 2 == 0 else 0.66)
            x = side * (ring_at(back, tip, y)[3] / 2 - size * 0.5)
            m.loft_z("Teeth", (edge - size, x, y, size * 0.15, size * 0.15), (edge, x, y, size, size))
        x = side * snout_w * 0.17
        y = front + length - tooth * 0.5
        m.loft_z("Teeth", (edge - tooth * 0.8, x, y, tooth * 0.12, tooth * 0.12), (edge, x, y, tooth * 0.8, tooth * 0.8))

    m.use("Jaw", (0, front - 0.05, mouth_z), "Head")
    lower_length = length * 0.92 * underbite
    jaw_back = (front - 0.05, 0, lower_z, skull_w * 0.85, lower_h)
    jaw_tip = (front + lower_length, 0, lower_z, snout_w * (0.9 + (underbite - 1) * 0.3), lower_h)
    m.loft_y(lower, jaw_back, jaw_tip)
    m.block("Furnace", 0, front + lower_length * 0.45, mouth_z - gap / 2 + 0.02, snout_w * 0.62, lower_length * 0.8, 0.06)
    floor = mouth_z - gap / 2 - 0.02
    for side in (-1, 1):
        count = max(per_side - 1, 1)
        for i in range(count):
            y = front + lower_length * (0.22 + 0.6 * i / max(count - 1, 1))
            size = tooth * (0.78 if i % 2 == 0 else 0.55)
            x = side * (ring_at(jaw_back, jaw_tip, y)[3] / 2 - size * 0.5)
            m.loft_z("Teeth", (floor, x, y, size, size), (floor + size, x, y, size * 0.15, size * 0.15))
        if tusk:
            y = min(front + lower_length * 0.86, front + length * 0.9)
            x = side * (ring_at(back, tip, y)[3] / 2 + tusk * 0.1)
            m.loft_z("Teeth", (lower_z, x, y, tusk * 0.36, tusk * 0.36),
                     (mouth_z + gap / 2 + upper_h * 0.55, x + side * tusk * 0.06, y - tusk * 0.04, tusk * 0.06, tusk * 0.06))
    if on_jaw:
        on_jaw(m, front, mouth_z, gap, lower_length)
    m.bone = "Head"

    if grin:
        line_h = max(gap, 0.06) * 0.8
        for side in (-1, 1):
            x = side * (skull_w / 2 + 0.005)
            m.loft_y("Furnace", (front - skull_d * 0.38, x, mouth_z + grin, 0.04, line_h * 0.7), (front + 0.02, x, mouth_z, 0.04, line_h))
    return {"tip": front + length, "top": lambda y: top_of((back, tip), y), "width": lambda y: ring_at(back, tip, y)[3]}


def ember_nostrils(m, snout, spread, size=0.14):
    """Nostrils glowing on top of the snout. (No smoke out of them: it always drifted over the eyes.)"""
    y = snout["tip"] - size * 1.8
    z = snout["top"](y)
    for side in (-1, 1):
        m.block("Furnace", side * spread, y, z + size * 0.2, size, size * 1.2, size * 0.5)


# ---------------------------------------------------------------------- monsters


def toasty_raptor():
    """Silly: a raptor that got too close to the lava. Singed black on top, smoke still coming off its head,
    and absolutely furious about it: one eye squeezed shut, one twitching wide, every tooth on show."""
    m = monster("dino_ToastyRaptor", Body="#ef8a3a", Accent="#2c2226", Belly="#ffd9a2", Claw="#2a1c1e", Smoke="#8e8a92", Ember="#ffb02a")
    m.joint("Spine", (0, -0.5, 2.5))
    biped_legs(m, 0.52, -0.5, 2.05, 0.84, 0.95, 0.33, 1.0, 0.25)
    for side in (-1, 1):  # the sickle claw, held up off the ground
        m.bone = "ShinL" if side < 0 else "ShinR"
        m.loft_y("Claw", (-0.2, side * 0.52, 0.52, 0.16, 0.24), (0.14, side * 0.52, 0.9, 0.04, 0.04))
    m.bone = "Spine"
    body = ((-1.5, 0, 2.4, 0.95, 0.95), (0.8, 0, 2.8, 1.4, 1.5))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-0.75, 0, 2.06, 0.9, 0.48), (0.85, 0, 2.33, 1.15, 0.72))
    tail(m, (-1.45, 2.42, 0.82, 0.78), (-4.5, 2.85, 0.14, 0.14), 3)
    # Scorched: charred patches over the back and the tail, still smouldering in spots.
    for y, w, d in ((0.15, 0.95, 0.9), (-0.85, 0.72, 0.7)):
        m.block("Accent", 0.05, y, top_of(body, y) + 0.03, w, d, 0.12)
    m.block("Ember", 0.25, 0.32, top_of(body, 0.32) + 0.11, 0.14, 0.14, 0.06)
    m.block("Ember", -0.18, -0.95, top_of(body, -0.95) + 0.11, 0.12, 0.12, 0.06)
    m.bone = "Tail1"
    m.block("Accent", 0, -2.0, 2.86, 0.6, 0.7, 0.12)
    m.bone = "Spine"
    for side in (-1, 1):
        x = side * 0.76
        m.use("ArmL" if side < 0 else "ArmR", (x, 0.55, 2.78))
        m.loft_y("Body", (0.55, x, 2.78, 0.26, 0.3), (1.3, x, 2.4, 0.2, 0.22))
        for offset in (-0.06, 0.06):
            m.loft_y("Claw", (1.27, x + offset, 2.38, 0.07, 0.1), (1.56, x + offset, 2.2, 0.03, 0.03))
    m.use("Neck", (0, 0.95, 3.2))
    m.loft_z("Body", (3.2, 0, 0.95, 0.95, 1.0), (4.0, 0, 1.3, 0.75, 0.8))
    m.stretch("Body", "Spine")

    w, d, h = 1.45, 1.5, 1.3
    yc, zc = 1.55, 4.42
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = snarl(m, front, zc - 0.52, w, 1.1, 1.0, 0.34, 0.24, 0.3, tooth=0.2, per_side=4, grin=0.3, skull_d=d)
    ember_eyes(m, w / 2, front, zc + 0.33, 0.6, slant=(0.9, 0.7), squint=(0.45, 0.0), look=((0.04, -0.03), (-0.06, 0.03)))
    ember_nostrils(m, snout, 0.26, 0.13)
    # The singed top of its head: charred, a frizzled crest, smouldering, and still smoking.
    top = zc + h / 2
    m.block("Accent", 0, yc - 0.15, top + 0.04, w * 0.92, d * 0.75, 0.14)
    for x, y in ((0.32, yc + 0.08), (-0.36, yc - 0.42)):
        m.block("Ember", x, y, top + 0.13, 0.14, 0.14, 0.06)
    for z, length_f in ((top - 0.1, 0.75), (top - 0.4, 0.95), (top - 0.7, 0.65)):
        m.loft_y("Accent", (yc - d / 2 - length_f, 0, z + 0.42, 0.08, 0.08), (yc - d / 2 + 0.25, 0, z, 0.44, 0.24))
    for x, y, z, s in ((0.12, yc - 0.45, top + 0.55, 0.5), (-0.12, yc - 0.85, top + 1.12, 0.66), (0.18, yc - 1.25, top + 1.82, 0.52)):
        m.block("Smoke", x, y, z, s, s, s * 0.9)
    m.head_centre = (0, front + 0.3, zc + 0.15)
    return m


def burnt_ankylo():
    """Silly: a low tank of charred armour with lava glowing up between the plates, and a tail club that
    is on fire, which it has decided is your fault. Tiny eyes under one huge brow, an underbite and tusks."""
    m = monster("dino_BurntAnkylo", Body="#5e4a42", Accent="#262022", Belly="#c48a5c", Claw="#1a1416",
                Lava="#ff6a1a", Flame="#ffcf3a", Smoke="#8e8a92")
    m.joint("Spine", (0, 0, 1.75))
    quad_legs(m, 1.15, 1.3, 1.2, -1.5, 1.5, 0.82)
    back = ((-2.6, 0, 1.7, 2.2, 1.6), (0, 0, 2.05, 3.2, 2.2))
    fore = ((0, 0, 2.05, 3.2, 2.2), (2.2, 0, 1.6, 2.3, 1.5))
    m.loft_y("Body", *back)
    m.loft_y("Body", *fore)
    m.loft_y("Belly", (-2.2, 0, 0.98, 2, 0.3), (2, 0, 0.92, 2.1, 0.3))
    # A hot layer over the back, then the armour on it: lava shows in every gap.
    for pair, (y0, y1) in ((back, (-2.45, 0)), (fore, (0, 2.05))):
        rings = [ring_at(*pair, y) for y in (y0, y1)]
        m.loft_y("Lava", *[(r[0], 0, r[2] + r[4] / 2 - 0.03, r[3] * 0.86, 0.12) for r in rings])
    for y in (-1.85, -0.75, 0.35, 1.4):
        pair = back if y < 0 else fore
        r = ring_at(*pair, y)
        top = r[2] + r[4] / 2
        size = 0.7 if abs(y) > 1.5 else 0.82
        for share in (-0.34, 0, 0.34):
            x = share * r[3]
            m.loft_z("Accent", (top - 0.05, x, y, size, size * 0.9), (top + 0.28, x, y, size * 0.8, size * 0.72))
            m.loft_z("Accent", (top + 0.28, x, y, size * 0.8, size * 0.72), (top + 0.66, x, y - 0.05, size * 0.12, size * 0.1))
    # Obsidian spikes along the flanks, each with a hot tip.
    for y in (-1.6, -0.5, 0.6, 1.6):
        r = ring_at(*(back if y < 0 else fore), y)
        for side in (-1, 1):
            start = side * (r[3] / 2 - 0.1)
            z = r[2] + r[4] * 0.12
            m.loft_x("Accent", (start, y, z, 0.5, 0.5), (start + side * 0.95, y, z - 0.1, 0.06, 0.06))
            m.block("Lava", start + side * 0.9, y, z - 0.09, 0.11, 0.11, 0.11)
    tail(m, (-2.5, 1.65, 1.1, 0.9), (-5.3, 1.7, 0.42, 0.36), 3)
    m.bone = "Tail3"
    # The club: a lump of charcoal with lava in its cracks, on fire.
    m.block("Accent", 0, -5.6, 1.7, 1.5, 1.1, 1.0)
    m.block("Lava", 0.76, -5.55, 1.72, 0.05, 0.14, 0.72)
    m.block("Lava", -0.76, -5.7, 1.6, 0.05, 0.14, 0.6)
    m.block("Lava", 0.1, -6.16, 1.75, 0.9, 0.05, 0.14)
    m.loft_z("Lava", (2.15, 0, -5.6, 0.95, 0.75), (3.55, 0.08, -5.78, 0.08, 0.08))
    for side in (-1, 1):
        m.loft_z("Lava", (2.15, side * 0.42, -5.62, 0.42, 0.4), (2.9, side * 0.66, -5.7, 0.05, 0.05))
    m.loft_z("Flame", (2.15, 0.04, -5.32, 0.5, 0.36), (2.95, 0.08, -5.42, 0.06, 0.06))
    m.block("Smoke", 0.22, -5.95, 4.05, 0.46, 0.46, 0.42)
    m.block("Smoke", 0.05, -6.2, 4.65, 0.62, 0.62, 0.56)
    m.bone = "Spine"
    m.use("Neck", (0, 2.1, 1.65))
    m.loft_y("Body", (2.1, 0, 1.65, 1.8, 1.3), (2.6, 0, 1.55, 1.5, 1.1))
    m.stretch("Body", "Spine")

    w, d, h = 1.7, 1.2, 1.0
    yc, zc = 2.95, 1.55
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = snarl(m, front, zc - 0.3, w, 0.5, 1.3, 0.3, 0.3, 0.14, tooth=0.15, per_side=3, tusk=0.7, grin=-0.16, skull_d=d, underbite=1.35)
    ember_eyes(m, w / 2, front, zc + 0.27, 0.46, slant=1.0, squint=0.22, wide=1.15)
    ember_nostrils(m, snout, 0.3, 0.13)
    m.block("Accent", 0, yc + 0.1, zc + h / 2 + 0.08, w * 1.04, d * 0.9, 0.18)  # an armoured forehead
    m.head_centre = (0, front, zc)
    return m


def hot_sauce_trike():
    """Silly: a triceratops that ate the hot sauce. Red hot, horns turned to chili peppers, the frill on
    fire, steam blasting out of its nose, sweating, its tongue hanging out and on fire, and furious."""
    m = monster("dino_HotSauceTrike", Body="#e63b2c", Accent="#ffb21e", Belly="#ffe1a3", Claw="#5c1c14", Tongue="#ff3d3d",
                Chili="#b5121b", Stem="#3d9b35", Steam="#f2efea", Sweat="#8fd9ff", Flame="#ffcf3a", Lava="#ff6a1a")
    m.joint("Spine", (0, 0, 2.5))
    quad_legs(m, 1.2, 1.6, 1.25, -1.9, 2.1, 0.95)
    rear = ((-3, 0, 2.5, 2.3, 2.1), (-0.2, 0, 3.05, 3.2, 3))
    fore = ((-0.2, 0, 3.05, 3.2, 3), (2.5, 0, 2.7, 2.5, 2.3))
    m.loft_y("Body", *rear)
    m.loft_y("Body", *fore)
    m.loft_y("Belly", (-2.5, 0, 1.55, 2, 0.4), (2.3, 0, 1.6, 2.1, 0.4))
    for y in (-1.8, -0.4, 1.0):
        m.block("Accent", 0, y, top_of(rear if y < -0.2 else fore, y) + 0.03, 2.0, 0.5, 0.14)
    tail(m, (-2.9, 2.4, 1.6, 1.4), (-6, 2.4, 0.2, 0.2), 3)

    w, d, h = 2.1, 1.7, 1.6
    yc, zc = 3.3, 2.5
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)

    def burning_tongue(m, front, mouth_z, gap, lower_length):
        z = mouth_z - gap / 2 + 0.07
        x = -0.34
        tip_y = front + lower_length + 0.36
        m.block("Tongue", x, front + lower_length * 0.5, z, 0.42, lower_length * 0.92, 0.12)
        m.loft_y("Tongue", (front + lower_length * 0.92, x, z, 0.42, 0.12), (tip_y, x - 0.06, z - 0.5, 0.36, 0.12))
        m.loft_z("Lava", (z - 0.62, x - 0.06, tip_y + 0.02, 0.44, 0.34), (z + 0.45, x - 0.02, tip_y + 0.12, 0.05, 0.05))
        m.loft_z("Flame", (z - 0.6, x - 0.06, tip_y + 0.14, 0.26, 0.2), (z + 0.08, x - 0.03, tip_y + 0.2, 0.04, 0.04))

    snout = snarl(m, front, zc - 0.5, w, 0.95, 1.1, 0.46, 0.26, 0.5, tooth=0.17, per_side=3, grin=0.24, skull_d=d, on_jaw=burning_tongue)
    ember_eyes(m, w / 2, front, zc + 0.5, 0.66, slant=1.0, squint=0.38, wide=1.2, brow_role="Claw")
    ember_nostrils(m, snout, 0.3, 0.15)
    ny = snout["tip"] - 0.27
    nz = snout["top"](ny)
    for side in (-1, 1):  # steam blasting out sideways
        for dx, dy, dz, s in ((0.55, 0.0, 0.1, 0.32), (1.05, -0.15, 0.35, 0.44)):
            m.block("Steam", side * (0.3 + dx), ny + dy, nz + dz, s, s, s * 0.9)
    # Chili pepper horns, swept up and out above the eyes, green stalks and all.
    for side in (-1, 1):
        x = side * 0.85
        base = (front - 0.25, x, zc + 1.05, 0.38, 0.38)
        mid = (front + 0.75, x * 1.25, zc + 1.95, 0.32, 0.32)
        m.loft_y("Chili", base, mid)
        m.loft_y("Chili", mid, (front + 1.3, x * 1.4, zc + 2.15, 0.04, 0.04))
        m.block("Stem", x, front - 0.22, zc + 1.05, 0.5, 0.2, 0.5)
        m.loft_y("Stem", (front - 0.35, x, zc + 1.2, 0.14, 0.14), (front - 0.7, x, zc + 1.5, 0.09, 0.09))
    ny = front + 0.62
    nz = snout["top"](ny)
    m.loft_z("Chili", (nz - 0.05, 0, ny, 0.34, 0.4), (nz + 0.62, 0, ny + 0.14, 0.04, 0.04))
    m.block("Stem", 0, ny, nz + 0.03, 0.42, 0.48, 0.12)
    # The frill, with flames licking along its top edge.
    frill_low = (zc - 0.6, 0, yc - 0.9, 2.2, 0.3)
    frill_high = (zc + 2, 0, yc - 1.55, 4, 0.24)
    m.loft_z("Accent", frill_low, frill_high)
    m.loft_z("Body", (zc - 0.4, 0, yc - 1.02, 1.9, 0.32), (zc + 1.7, 0, yc - 1.62, 3.4, 0.28))
    for x in (-1.6, -0.8, 0, 0.8, 1.6):
        tall = 0.75 - abs(x) * 0.12
        m.loft_z("Flame", (zc + 1.9, x, yc - 1.55, 0.46, 0.2), (zc + 1.95 + tall, x * 1.04, yc - 1.62, 0.04, 0.04))
    # Sweating with the heat: drops on the frill.
    for x, z in ((0.95, zc + 1.2), (-1.15, zc + 0.85), (0.3, zc + 1.55)):
        t = (z - frill_low[0]) / (frill_high[0] - frill_low[0])
        y = frill_low[2] + (frill_high[2] - frill_low[2]) * t + 0.16
        m.block("Sweat", x, y, z, 0.22, 0.12, 0.3)
        m.block("Sweat", x, y, z - 0.22, 0.14, 0.1, 0.14)
    m.head_centre = (0, front + 0.3, zc + 0.3)
    return m


def magma_stego():
    """Fierce: a basalt stegosaurus whose plates are obsidian with molten cores, lava cracks down its sides,
    white-hot tail spikes and a mean, horned little head."""
    m = monster("dino_MagmaStego", Body="#3e3537", Accent="#1f1a1f", Belly="#6e5a52", Claw="#141012", Lava="#ff6a1a", Ember="#ffc23a")
    m.joint("Spine", (0, 0, 2.8))
    rear = ((-3.2, 0, 2.55, 1.9, 2.0), (-0.4, 0, 3.05, 3.1, 3.1))
    fore = ((-0.42, 0, 3.05, 3.1, 3.1), (2.6, 0, 2.3, 2.1, 1.9))
    m.loft_y("Body", *rear)
    m.loft_y("Body", *fore)
    m.loft_y("Belly", (-2.8, 0, 1.45, 1.6, 0.5), (2.4, 0, 1.42, 1.8, 0.45))
    for side in (-1, 1):
        flank_vein(m, rear, side, ((-2.9, 0.1), (-2.3, -0.25), (-1.7, 0.2), (-1.0, -0.3), (-0.5, 0.05)))
        flank_vein(m, fore, side, ((0.1, 0.35), (0.7, -0.05), (1.3, 0.3), (1.9, -0.1)))
    tail(m, (-3.1, 2.55, 1.45, 1.4), (-6.5, 3.05, 0.26, 0.26), 3)
    for x, y in ((-1.1, 1.65), (1.1, 1.65), (-1.15, -1.75), (1.15, -1.75)):
        big = y < 0
        m.use(("Back" if big else "Front") + ("L" if x < 0 else "R"), (x, y, 2.0))
        top, size = (2.15, 1.25) if big else (1.85, 1.05)
        m.loft_z("Body", (0.32, x, y, 0.85, 0.85), (top, x, y, size, size * 1.05))
        m.block("Belly", x, y + 0.12, 0.16, 1.05, 1.15, 0.32)
        half = 0.425 + (size / 2 - 0.425) * (1.1 - 0.32) / (top - 0.32)
        m.block("Lava", x + (1 if x > 0 else -1) * (half + 0.02), y + 0.1, 1.1, 0.06, 0.14, 0.9)
        for offset in (-0.3, 0, 0.3):
            m.loft_y("Claw", (y + 0.45, x + offset, 0.14, 0.2, 0.22), (y + 0.82, x + offset, 0.07, 0.04, 0.04))
    # Plates: obsidian with a molten core showing on both faces, biggest over the hips.
    plates = [(1.9, 3.1, 0.75), (0.95, 3.85, 1.1), (-0.1, 4.45, 1.45), (-1.2, 4.3, 1.55), (-2.3, 3.5, 1.25), (-3.3, 3.25, 0.9), (-4.2, 3.1, 0.65)]
    for y, z, size in plates:
        m.bone = "Tail1" if y < -3.1 else "Spine"
        m.loft_z("Accent", (z - 0.3, 0, y, 0.34, size * 0.85), (z + size * 0.45, 0, y, 0.3, size * 0.95))
        m.loft_z("Accent", (z + size * 0.45, 0, y, 0.3, size * 0.95), (z + size * 1.1, 0, y - size * 0.06, 0.12, size * 0.16))
        m.loft_z("Lava", (z + size * 0.02, 0, y, 0.38, size * 0.42), (z + size * 0.5, 0, y, 0.36, size * 0.52))
        m.loft_z("Lava", (z + size * 0.5, 0, y, 0.36, size * 0.52), (z + size * 0.86, 0, y - size * 0.04, 0.3, size * 0.1))
    m.bone = "Tail3"
    for side in (-1, 1):
        for y, z in ((-6.1, 2.98), (-5.3, 2.85)):
            m.loft_x("Accent", (side * 0.2, y, z, 0.32, 0.32), (side * 1.35, y - 0.15, z + 0.56, 0.06, 0.06))
            m.block("Ember", side * 1.28, y - 0.14, z + 0.52, 0.13, 0.13, 0.13)
    m.bone = "Spine"
    m.use("Neck", (0, 2.5, 2.2))
    m.loft_y("Body", (2.5, 0, 2.2, 1.45, 1.35), (3.6, 0, 1.95, 1.05, 1.05))
    m.stretch("Body", "Spine")

    w, d, h = 1.4, 1.2, 1.15
    yc, zc = 4.05, 1.95
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = snarl(m, front, zc - 0.34, w, 0.62, 1.05, 0.32, 0.22, 0.2, tooth=0.15, per_side=3, tusk=0.42, grin=0.18, skull_d=d)
    ember_eyes(m, w / 2, front, zc + 0.3, 0.5, slant=0.95, squint=0.12, horn=0.8)
    ember_nostrils(m, snout, 0.24, 0.11)
    for y, size in ((yc - 0.15, 0.32), (yc - 0.55, 0.26)):  # little obsidian ridges on the head
        m.loft_z("Accent", (zc + h / 2 - 0.05, 0, y, 0.16, size), (zc + h / 2 + size * 0.9, 0, y - 0.08, 0.06, 0.08))
    m.head_centre = (0, front + 0.1, zc + 0.1)
    return m


def obsidian_rex():
    """Fierce: a T-rex of black volcanic glass. Purple obsidian shards down its back, lava veins glowing
    through its hide, a furnace of a mouth crammed with teeth, tusks, horns and burning eyes."""
    m = monster("dino_ObsidianRex", Body="#26222d", Accent="#6a4fa3", Belly="#40374b", Claw="#0f0c13", Lava="#ff5f1a", Ember="#ffc23a", Smoke="#8a8590")
    m.joint("Spine", (0, -0.8, 4.4))
    biped_legs(m, 0.95, -0.8, 3.9, 1.5, 1.7, 0.7, 1.9, 0.4)
    torso = ((-2.4, 0, 4.2, 1.8, 1.9), (1.4, 0, 5, 2.7, 3))
    m.loft_y("Body", *torso)
    m.loft_y("Belly", (-1.1, 0, 3.55, 1.75, 0.8), (1.45, 0, 4.1, 2.3, 1.45))
    for side in (-1, 1):
        flank_vein(m, torso, side, ((-2.1, 0.3), (-1.5, -0.1), (-0.9, 0.35), (-0.2, -0.15), (0.5, 0.3), (1.2, -0.2)))
    for leg in ("LegL", "LegR"):
        m.bone = leg
        thigh_crack(m, -1 if leg == "LegL" else 1, 0.95, -0.8, 3.9, 1.5, 1.7, (4.05, 3.55, 3.05, 2.55))
    m.bone = "Spine"
    tail(m, (-2.3, 4.25, 1.6, 1.6), (-7.2, 4.8, 0.2, 0.2), 3)
    # Obsidian shards down the back, leaning back like they were swept by the heat.
    turn = math.pi / 4
    for y, height in ((1.1, 1.3), (0.2, 1.65), (-0.7, 1.5), (-1.6, 1.15)):
        top = top_of(torso, y)
        prism(m, "Accent", 0, y, top - 0.25, top + height, 0.42, 0.04, 4, turn, (0, -0.35 * height))
    for bone, y, z, height in (("Tail1", -3.0, 5.0, 0.95), ("Tail2", -4.3, 5.05, 0.7), ("Tail3", -5.6, 5.0, 0.45)):
        m.bone = bone
        prism(m, "Accent", 0, y, z - 0.3, z + height, 0.3, 0.03, 4, turn, (0, -0.3 * height))
    m.bone = "Spine"
    for side in (-1, 1):
        m.use("ArmL" if side < 0 else "ArmR", (side * 1.38, 1.2, 4.85))
        m.loft_y("Body", (1, side * 1.38, 4.85, 0.3, 0.32), (1.75, side * 1.38, 4.45, 0.2, 0.2))
        for offset in (-0.07, 0.07):
            m.loft_y("Claw", (1.72, side * 1.38 + offset, 4.42, 0.08, 0.1), (2.02, side * 1.38 + offset, 4.28, 0.03, 0.03))
    m.use("Neck", (0, 1.5, 5.9))
    m.loft_z("Body", (5.9, 0, 1.5, 2, 2.1), (6.65, 0, 1.95, 1.75, 1.75))
    m.stretch("Body", "Spine")

    w, d, h = 2.6, 2.6, 1.9
    yc, zc = 2.9, 7.3
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = snarl(m, front, zc - 0.6, w, 2.0, 2.1, 0.6, 0.48, 0.62, tooth=0.36, per_side=5, tusk=0.8, grin=0.4, skull_d=d)
    ember_eyes(m, w / 2, front, zc + 0.62, 0.78, slant=1.0, squint=0.1, horn=1.1)
    ember_nostrils(m, snout, 0.55, 0.2)
    # A glowing scar across the snout, and shards down the back of the skull.
    scar_a, scar_b = front + 0.45, front + 1.35
    crack(m, [(0.55, scar_a, snout["top"](scar_a) + 0.02), (0.05, (scar_a + scar_b) / 2, snout["top"]((scar_a + scar_b) / 2) + 0.03),
              (-0.35, scar_b, snout["top"](scar_b) + 0.02)], flat=True, wide=0.2)
    for y, height in ((yc + 0.4, 0.55), (yc - 0.5, 0.7), (yc - 1.2, 0.5)):
        prism(m, "Accent", 0, y, zc + h / 2 - 0.2, zc + h / 2 + height, 0.34, 0.03, 4, turn, (0, -0.4 * height))
    m.head_centre = (0, front + 0.6, zc)
    return m


def volcano_king():
    """The map's boss: a hulking lava monster that walks on its knuckles, a volcano erupting on its back,
    a crown of burning horns, molten cracks across its chest and a jaw like a furnace door."""
    m = monster("dino_VolcanoKing", Body="#4a2f2b", Accent="#1d1718", Belly="#7a4636", Claw="#141012",
                Lava="#ff6a1a", Ember="#ffc23a", Smoke="#8a8488")
    m.joint("Spine", (0, -0.6, 5.6))
    biped_legs(m, 1.45, -0.6, 4.6, 2.0, 2.2, 1.2, 2.3, 0.5)
    torso = ((-2.4, 0, 5.5, 3.0, 3.0), (1.5, 0, 6.6, 4.3, 4.4))
    m.loft_y("Body", *torso)
    belly = ((-1.0, 0, 4.85, 2.6, 1.0), (1.6, 0, 5.6, 3.6, 2.3))
    m.loft_y("Belly", *belly)
    # Molten cracks across the belly, and down both flanks.
    front = belly[1][0] + 0.03
    crack(m, [(-1.3, front, 6.5), (-0.7, front, 5.9), (-1.0, front, 5.3), (-0.4, front, 4.7)], wide=0.24, thick=0.1)
    crack(m, [(1.2, front, 6.55), (0.6, front, 6.0), (0.95, front, 5.4), (0.35, front, 4.8)], wide=0.24, thick=0.1)
    crack(m, [(-0.7, front, 5.9), (0.6, front, 6.0)], wide=0.2, thick=0.1)
    for side in (-1, 1):
        flank_vein(m, torso, side, ((-2.1, 0.4), (-1.4, -0.05), (-0.8, 0.45), (0.0, 0.0), (0.8, 0.5), (1.3, 0.1)), wide=0.22, thick=0.12)
    for leg in ("LegL", "LegR"):
        m.bone = leg
        thigh_crack(m, -1 if leg == "LegL" else 1, 1.45, -0.6, 4.6, 2.0, 2.2, (4.85, 4.15, 3.45, 2.75), wide=0.24)
    m.bone = "Spine"
    tail(m, (-2.3, 5.0, 1.9, 1.9), (-6.6, 1.6, 0.6, 0.5), 3)
    for bone, y, z, height in (("Tail1", -3.0, 5.25, 0.9), ("Tail2", -4.4, 4.2, 0.7), ("Tail3", -5.6, 3.0, 0.5)):
        m.bone = bone
        prism(m, "Accent", 0, y, z - 0.3, z + height, 0.36, 0.03, 4, math.pi / 4, (0, -0.3 * height))
    m.bone = "Spine"
    # The volcano on its back, erupting.
    vy = -0.95
    vz = top_of(torso, vy)
    m.loft_z("Body", (vz - 0.6, 0, vy, 3.4, 3.0), (vz + 1.3, 0, vy - 0.1, 2.3, 2.0))
    m.loft_z("Accent", (vz + 1.3, 0, vy - 0.1, 2.3, 2.0), (vz + 2.15, 0, vy - 0.15, 1.6, 1.4))
    m.block("Lava", 0, vy - 0.15, vz + 2.15, 1.25, 1.05, 0.14)
    for dx, dy in ((0.55, 0.45), (-0.6, 0.3), (0.2, -0.6)):
        crack(m, [(dx * 1.05, vy - 0.15 + dy * 1.0, vz + 2.1), (dx * 1.45, vy - 0.1 + dy * 1.35, vz + 1.3), (dx * 1.95, vy + dy * 1.75, vz + 0.2)],
              flat=True, wide=0.3, thick=0.14)
    for x, y, z, s in ((0.1, vy - 0.25, vz + 2.8, 0.8), (-0.2, vy - 0.6, vz + 3.6, 1.05), (0.25, vy - 1.0, vz + 4.5, 1.25)):
        m.block("Smoke", x, y, z, s, s, s * 0.85)
    m.block("Ember", 0.15, vy - 0.1, vz + 2.45, 0.24, 0.24, 0.24)  # a lava bomb flying out
    # Shoulder spikes.
    for side in (-1, 1):
        for dx, dy, height in ((1.35, 0.6, 1.2), (1.65, -0.3, 0.9)):
            x = side * dx
            z = top_of(torso, dy) - 0.2
            prism(m, "Accent", x, dy, z, z + height, 0.34, 0.03, 4, math.pi / 4, (side * 0.35 * height, -0.25 * height))
    # Arms: long and heavy, knuckles almost on the ground.
    for side in (-1, 1):
        sx = side * 2.35
        m.use("ArmL" if side < 0 else "ArmR", (sx, 1.0, 7.3))
        beam(m, "Body", (sx, 1.0, 7.5), (sx + side * 0.35, 1.9, 3.2), 1.35, None, 1.6)
        fist = (sx + side * 0.35, 2.05, 2.5)
        m.block("Body", *fist, 1.75, 1.85, 1.55)
        m.block("Accent", fist[0], fist[1] + 0.1, fist[2] + 0.85, 1.6, 1.5, 0.22)  # knuckle plate
        for offset in (-0.55, 0, 0.55):
            m.loft_y("Claw", (fist[1] + 0.9, fist[0] + offset, fist[2] - 0.35, 0.36, 0.4), (fist[1] + 1.5, fist[0] + offset, fist[2] - 0.75, 0.05, 0.05))
        trunk_crack(m, (sx, 1.0, 7.5), (sx + side * 0.35, 1.9, 3.2), 1.35, 1.6, side, zig=0.3, steps=4, role="Lava")
    m.use("Neck", (0, 1.7, 7.9))
    m.loft_y("Body", (1.3, 0, 7.6, 2.8, 2.6), (2.4, 0, 7.9, 2.3, 2.1))
    m.stretch("Body", "Spine")

    w, d, h = 2.9, 2.6, 2.1
    yc, zc = 3.3, 8.2
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = snarl(m, front, zc - 0.7, w, 1.6, 2.5, 0.6, 0.6, 0.7, tooth=0.4, per_side=5, tusk=1.15, grin=0.45, skull_d=d)
    ember_eyes(m, w / 2, front, zc + 0.62, 0.95, slant=1.0, squint=0.2)
    ember_nostrils(m, snout, 0.6, 0.22)
    # The crown: a ring of horns, burning at the tips.
    top = zc + h / 2
    for x, y, height in ((0, yc - 0.95, 1.9), (1.0, yc - 0.55, 1.55), (-1.0, yc - 0.55, 1.55), (1.25, yc + 0.55, 1.1), (-1.25, yc + 0.55, 1.1)):
        lean = (0.25 * height * (1 if x > 0 else -1 if x < 0 else 0), -0.15 * height)
        mid = height * 0.55
        prism(m, "Accent", x, y, top - 0.2, top + mid, 0.36, 0.22, 4, math.pi / 4, (lean[0] * 0.55, lean[1] * 0.55))
        prism(m, "Lava", x + lean[0] * 0.55, y + lean[1] * 0.55, top + mid, top + height, 0.22, 0.03, 4, math.pi / 4, (lean[0] * 0.45, lean[1] * 0.45))
    m.head_centre = (0, front + 0.5, zc)
    return m


# ---------------------------------------------------------------------- animation


def roar(t):
    """0 most of the idle loop, rising to 1 halfway through it and back: the roar."""
    return ((1 - math.cos(t)) / 2) ** 10


def walk_pose(a, f):
    """Every map's walk, with the jaw snapping in time with the steps."""
    kit.walk_pose(a, f)
    p = 2 * math.pi * f / kit.WALK_FRAMES
    kit.pose_bone(a, "Jaw", (-0.08 * (0.5 + 0.5 * math.sin(2 * p)), 0, 0), None, f)


def idle_pose(a, f):
    """Every map's idle (breathing, looking round, tail swaying), plus a roar once per loop: head thrown up,
    jaw dropped wide, arms out and a shake of the head. DinoLifeController adds the same roar."""
    t = 2 * math.pi * f / kit.IDLE_FRAMES
    r = roar(t)
    sin = math.sin
    kit.pose_bone(a, "Spine", (0.025 * sin(4 * t) + 0.03 * r, 0, 0), (0, 0, 0.03 * sin(4 * t)), f)
    for letter in "LR":
        kit.pose_bone(a, f"Arm{letter}", (0.08 * sin(4 * t + 0.5) + 0.45 * r, 0, 0), None, f)
    for i in (1, 2, 3):
        lift = 0.08 * r if i == 1 else 0
        kit.pose_bone(a, f"Tail{i}", (0.02 * sin(4 * t - i * 0.5) + lift, 0, 0.14 * sin(2 * t - i * 0.6)), None, f)
    kit.pose_bone(a, "Neck", (0.05 * sin(2 * t + 1) + 0.12 * r, 0, 0.14 * sin(t)), None, f)
    kit.pose_bone(a, "Head", (0.09 * sin(3 * t) + 0.3 * r, 0, 0.36 * sin(t) + 0.08 * sin(3 * t) + 0.08 * sin(14 * t) * r), None, f)
    kit.pose_bone(a, "Jaw", (-0.03 * (0.5 + 0.5 * sin(4 * t)) - 0.55 * r, 0, 0), None, f)


def animate(armature):
    walk = kit.add_action(armature, "Walk", kit.WALK_FRAMES, walk_pose, 2)
    idle = kit.add_action(armature, "Idle", kit.IDLE_FRAMES, idle_pose, 2)
    return walk, idle


ROAR_FRAME = kit.IDLE_FRAMES // 2  # the top of the roar


# ---------------------------------------------------------------------- props
# Dark rock, black glass and lava: the reference's far worlds go dark with lava and black spires (GAME_SPEC
# section 9). Lots of glow so it reads in a second from the flight camera.


def volcano(seed=5):
    """The map's signature, for the rims: a stepped cone with a crater of lava, lava running down three
    sides and smoke rolling off the top."""
    m = prop("Volcano", Rock="#4b3e3c", RockDark="#352c2c", Crust="#5c2f26", Lava="#ff6a1a", Ember="#ffc23a", Smoke="#8f8a8e", SmokeLight="#b8b3b5")
    rng = random.Random(seed)
    tiers = [(0, 4, 13, 12), (4, 8.5, 10.6, 9.4), (8.5, 12.5, 8.0, 6.8), (12.5, 15.5, 5.6, 4.8)]
    eighth = math.pi / 8
    for i, (z0, z1, r0, r1) in enumerate(tiers):
        prism(m, "Rock" if i % 2 == 0 else "RockDark", 0, 0, z0, z1, r0, r1, 8, eighth)
    prism(m, "Lava", 0, 0, 15.5, 15.95, 3.7, 3.7, 8, eighth)
    for i in range(8):
        a = i * math.tau / 8
        height = rng.uniform(0.8, 1.7)
        m.block("RockDark", math.cos(a) * 4.25, math.sin(a) * 4.25, 15.5 + height / 2, 2.3, 2.3, height)
    # Lava running down three faces, over every ledge, pooling at the foot.
    apothem = math.cos(eighth)
    for k in (0, 3, 5):
        a = k * math.pi / 4
        ca, sa = math.cos(a), math.sin(a)
        steps = [(3.3, 15.9)]
        for z0, z1, r0, r1 in reversed(tiers):
            steps += [(r1 * apothem + 0.12, z1), (r0 * apothem + 0.12, z0)]
        for i, ((r_a, z_a), (r_b, z_b)) in enumerate(zip(steps, steps[1:])):
            wiggle = 0.35 * (1 if i % 2 else -1)
            p = (ca * r_a - sa * wiggle, sa * r_a + ca * wiggle, z_a)
            q = (ca * r_b - sa * wiggle, sa * r_b + ca * wiggle, z_b)
            beam(m, "Lava", p, q, 1.4, 0.32)
        m.block("Lava", ca * 14, sa * 14, 0.15, 3.2, 3.2, 0.3)
        m.block("Ember", ca * 9.8, sa * 9.8, 8.55, 0.7, 0.7, 0.2)
    for a, z, s in ((1.2, 2.0, 2.6), (2.0, 6.5, 2.0), (4.0, 10.5, 1.8), (5.2, 3.0, 2.4)):  # cooled lava crust
        r = 11.4 if z < 4 else 9.4 if z < 8.5 else 7.0
        m.block("Crust", math.cos(a) * r, math.sin(a) * r, z, s, s, s * 0.6)
    for k, (dx, dy, z, s) in enumerate(((0, 0, 17.6, 4.2), (1.2, 0.4, 20.6, 5.6), (2.9, 0.8, 24.0, 6.8), (5.2, 1.0, 27.6, 7.6))):
        m.block("SmokeLight" if k % 2 else "Smoke", dx, dy, z, s, s * 0.9, s * 0.75)
    return m


def obsidian_spire(seed=8):
    """A cluster of black glass shards, some with a purple sheen, standing in a ring of glowing lava."""
    m = prop("ObsidianSpire", Obsidian="#1f1a25", Sheen="#4e3f70", Rock="#3d3536", Lava="#ff6a1a")
    rng = random.Random(seed)
    prism(m, "Lava", 0, 0, 0, 0.25, 3.7, 3.7, 6, 0.2)
    prism(m, "Rock", 0, 0, 0, 0.9, 3.4, 2.8, 6, 0.2)
    shards = [(0, 0, 11, 1.25, (0.4, 0.3), "Obsidian"), (1.7, 0.9, 7.2, 0.85, (1.0, 0.5), "Sheen"),
              (-1.5, 0.7, 6.0, 0.8, (-0.9, 0.3), "Obsidian"), (0.5, -1.6, 4.6, 0.7, (0.3, -0.8), "Sheen"),
              (-0.9, -1.1, 3.2, 0.55, (-0.4, -0.5), "Obsidian")]
    for x, y, height, r, (lx, ly), role in shards:
        turn = rng.uniform(0, 1.5)
        mid = height * 0.68
        prism(m, role, x, y, 0.4, mid, r, r * 0.72, 4, turn, (lx * 0.68, ly * 0.68))
        prism(m, role, x + lx * 0.68, y + ly * 0.68, mid, height, r * 0.72, 0.03, 4, turn, (lx * 0.32, ly * 0.32))
    return m


def lava_pool(seed=3):
    """A pool of lava in a ring of dark rock, crust floating on it and bubbles coming up."""
    m = prop("LavaPool", Lava="#ff6a1a", Ember="#ffc23a", Crust="#2f2526", CrustRed="#5c2f26", Rock="#4b3e3c")
    rng = random.Random(seed)
    m.block("Lava", 0, 0, 0.2, 10, 7, 0.4)
    m.block("Lava", 0.6, 0.4, 0.2, 7, 9.6, 0.4)
    for x, y, s in ((-2.2, -1.0, 1.6), (1.8, 1.6, 1.2), (0.6, -2.6, 0.9)):
        m.block("Ember", x, y, 0.42, s, s * 0.8, 0.06)
    for x, y, w, d in ((-3.2, 1.6, 2.2, 1.6), (2.6, -1.4, 1.8, 2.2), (0.4, 3.4, 1.4, 1.2), (-0.8, -0.2, 1.2, 1.0)):
        m.block("CrustRed", x, y, 0.45, w, d, 0.22)
    for i in range(16):
        a = i * math.tau / 16
        s = rng.uniform(1.3, 2.4)
        m.block("Rock" if i % 3 else "Crust", math.cos(a) * 5.4, math.sin(a) * 4.9, s * 0.28, s, s, s * 0.56)
    for x, y, s in ((-1.0, 1.2, 0.9), (2.4, 0.4, 0.6), (-2.6, -2.2, 0.5)):
        m.block("Lava", x, y, 0.45 + s * 0.2, s, s, s * 0.8)
        m.block("Ember", x, y, 0.45 + s * 0.62, s * 0.4, s * 0.4, 0.06)
    return m


def trunk_crack(m, a, b, w0, w1, face, zig=0.25, steps=5, role="Ember"):
    """A glowing crack up one face of a beam() trunk from a to b (widths w0 to w1). face: +1 or -1, which side."""
    a, b = Vector(a), Vector(b)
    along = (b - a).normalized()
    side = along.cross(Vector((0, 0, 1))).normalized()
    lift = side.cross(along)
    points = []
    for i in range(steps + 1):
        t = 0.12 + 0.76 * i / steps
        centre = a + (b - a) * t
        half = (w0 + (w1 - w0) * t) / 2
        points.append(centre + side * face * (half + 0.02) + lift * zig * half * (1 if i % 2 else -1))
    for p, q in zip(points, points[1:]):
        beam(m, role, tuple(p), tuple(q), 0.1, 0.16)


def charred_tree(seed=6):
    """A burnt black tree, embers still glowing in its cracks and at the tips of its branches."""
    m = prop("CharredTree", Char="#2c2325", CharLight="#433638", Ember="#ff7a24", Ash="#8b827d")
    rng = random.Random(seed)
    m.loft_z("CharLight", (0, 0, 0, 3.6, 3.6), (0.8, 0, 0, 2.4, 2.4))
    m.block("Ash", 1.6, -1.2, 0.2, 1.6, 1.4, 0.4)
    m.block("Ash", -1.4, 1.5, 0.15, 1.2, 1.0, 0.3)
    trunk = [((0, 0, 0), (0.7, 0.3, 5), 2.3, 1.7), ((0.7, 0.3, 5), (0.0, -0.2, 9.5), 1.7, 1.0)]
    for a, b, w0, w1 in trunk:
        beam(m, "Char", a, b, w0, None, w1)
    trunk_crack(m, *trunk[0], 1)
    trunk_crack(m, *trunk[1], -1)
    for start, angle, length, rise in (((0.6, 0.25, 4.6), 0.4, 3.9, 2.4), ((0.4, 0.05, 6.8), 2.9, 3.4, 2.4), ((0.1, -0.15, 9.1), 4.7, 2.6, 2.2)):
        sx, sy, sz = start
        end = (sx + math.cos(angle) * length, sy + math.sin(angle) * length, sz + rise)
        beam(m, "Char", start, end, 0.95, None, 0.5)
        for turn in (-0.6, 0.7):
            twig = angle + turn + rng.uniform(-0.2, 0.2)
            tip = (end[0] + math.cos(twig) * 1.6, end[1] + math.sin(twig) * 1.6, end[2] + rng.uniform(0.6, 1.4))
            beam(m, "CharLight", end, tip, 0.45, None, 0.22)
            m.block("Ember", *tip, 0.28, 0.28, 0.28)
    return m


def steam_vent():
    """A rocky vent crusted with yellow sulfur, a column of steam pouring out of it."""
    m = prop("SteamVent", Rock="#4b3e3c", RockDark="#352c2c", Sulfur="#e8cf3f", Vent="#1a1414", Steam="#ece8e4", SteamShade="#cdc8c5")
    prism(m, "Rock", 0, 0, 0, 2.2, 4.4, 3.4, 7)
    prism(m, "RockDark", 0, 0, 2.2, 3.4, 3.2, 1.9, 7, 0.3)
    prism(m, "Vent", 0, 0, 3.4, 3.46, 1.15, 1.15, 7, 0.3)
    for x, y, z, w, d, h in ((1.5, 0.3, 3.1, 1.2, 0.9, 0.5), (-1.2, 1.0, 3.05, 1.0, 1.0, 0.45), (0.2, -1.6, 3.0, 1.1, 0.8, 0.45),
                             (2.9, 0.2, 1.6, 0.9, 1.4, 1.2), (-2.4, -1.6, 1.2, 1.3, 1.0, 0.8)):
        m.block("Sulfur", x, y, z, w, d, h)
    for k in range(6):
        s = 1.0 + k * 0.34
        m.block("Steam" if k % 2 == 0 else "SteamShade", 0.26 * k, 0.1 * k, 3.9 + k * 1.3, s, s, s * 0.8)
    return m


def basalt_columns(seed=4):
    """Hexagonal basalt columns packed together at different heights, lighter on top."""
    m = prop("BasaltColumns", Basalt="#3b3536", BasaltLight="#4f4647", Top="#675c59")
    rng = random.Random(seed)
    r = 1.0
    cells = [(0, 0), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (2, -1), (-2, 1), (1, 1), (-1, 2), (2, 0)]
    for q, s in cells:
        x, y = r * math.sqrt(3) * (q + s / 2), r * 1.5 * s
        height = 8.5 if (q, s) == (0, 0) else rng.choice((1.8, 2.8, 3.8, 4.8, 6.0, 7.2))
        role = "Basalt" if (q + s) % 2 == 0 else "BasaltLight"
        prism(m, role, x, y, 0, height, r * 0.97, r * 0.97, 6, math.pi / 6)
        prism(m, "Top", x, y, height, height + 0.15, r * 0.84, r * 0.84, 6, math.pi / 6)
    return m


def lava_rock():
    """A dark boulder split by glowing cracks, with a smaller one beside it."""
    m = prop("LavaRock", Rock="#3d3436", RockDark="#2c2527", Lava="#ff6a1a")
    m.block("Rock", 0, 0, 1.5, 5.2, 4.4, 3.0)
    m.block("RockDark", 0.3, -0.2, 3.35, 3.8, 3.2, 0.7)
    m.block("RockDark", -3.4, 1.6, 0.7, 1.8, 1.6, 1.4)
    crack(m, [(2.62, -1.6, 0.4), (2.62, -0.8, 1.2), (2.62, -1.1, 2.0), (2.62, -0.2, 2.95)])
    crack(m, [(-1.9, -2.22, 0.5), (-1.1, -2.22, 1.4), (-1.5, -2.22, 2.1), (-0.6, -2.22, 2.95)])
    crack(m, [(-1.2, 0.8, 3.72), (-0.2, 0.2, 3.72), (0.4, 0.7, 3.72), (1.6, 0.1, 3.72)], flat=True)
    crack(m, [(-2.5, 1.4, 0.3), (-2.5, 1.8, 0.9), (-2.5, 1.5, 1.35)], wide=0.14)
    return m


def fire_flowers(seed=9):
    """Volcanic flowers in ash, their petals shaped like flames, glowing at the heart."""
    m = prop("FireFlower", Stem="#3a3a28", Leaf="#56662c", Petal="#ff4a26", PetalTip="#ffb32a", Ember="#ffd84a", Ash="#5a4e4a")
    rng = random.Random(seed)
    m.loft_z("Ash", (0, 0, 0, 2.8, 2.8), (0.3, 0, 0, 2.1, 2.1))
    for x, y, height in ((0, 0, 2.6), (1.0, 0.6, 1.9), (-0.9, 0.5, 1.6)):
        beam(m, "Stem", (x, y, 0.2), (x, y, height), 0.2)
        for turn in (0.6, 3.4):
            angle = turn + rng.uniform(-0.3, 0.3)
            dx, dy = math.cos(angle), math.sin(angle)
            beam(m, "Leaf", (x + dx * 0.05, y + dy * 0.05, height * 0.35), (x + dx * 0.9, y + dy * 0.9, height * 0.5), 0.3, 0.06, 0.08)
        for i in range(5):
            a = i * math.tau / 5 + rng.uniform(-0.1, 0.1)
            dx, dy = math.cos(a), math.sin(a)
            beam(m, "Petal", (x + dx * 0.12, y + dy * 0.12, height), (x + dx * 0.6, y + dy * 0.6, height + 0.95), 0.44, 0.16, 0.06)
            beam(m, "PetalTip", (x + dx * 0.08, y + dy * 0.08, height + 0.1), (x + dx * 0.32, y + dy * 0.32, height + 1.25), 0.24, 0.1, 0.04)
        m.block("Ember", x, y, height + 0.12, 0.3, 0.3, 0.25)
    return m


def lava_cracks(seed=21):
    """Cracks in the corridor floor with lava glowing through. Flat (under a quarter of a stud), so they can
    lie in the middle of the floor where the eggs land."""
    m = prop("LavaCracks", Crust="#3e3330", CrustDark="#33292a", Lava="#ff6a1a", Ember="#ffc23a")
    rng = random.Random(seed)
    m.block("Crust", 0, 0, 0.05, 14, 8, 0.1)
    m.block("Crust", 2.5, 1.5, 0.05, 9, 9, 0.1)
    m.block("CrustDark", -4, -1, 0.07, 6, 5, 0.14)
    main = [(-8, -1.5), (-5, 0.5), (-2, -0.8), (1, 1.0), (4, -0.4), (7.5, 1.6)]
    crack(m, [(x, y, 0.17) for x, y in main], flat=True, wide=0.5, thick=0.1)
    for i in (1, 2, 3, 4):
        x, y = main[i]
        angle = (1 if i % 2 else -1) * rng.uniform(1.0, 2.1)
        length = rng.uniform(2.4, 4)
        bx, by = x + math.cos(angle) * length, y + math.sin(angle) * length
        crack(m, [(x, y, 0.17), (bx, by, 0.17), (bx + math.cos(angle + 0.7) * 1.6, by + math.sin(angle + 0.7) * 1.6, 0.17)], flat=True, wide=0.3, thick=0.1)
        m.block("Ember", x, y, 0.19, 0.75, 0.75, 0.1)
    return m


def lava_fall(seed=4):
    """Lava pouring off the rim and down the corridor wall into a pool on the floor. Its origin is the
    wall's top inner edge: the rim is z 0, the corridor floor z -44, and +Y points out into the corridor.
    The small Front part tells the game which way it faces once imported (MapDecor), then it's removed."""
    m = prop("LavaFall", Lava="#ff6a1a", Ember="#ffc23a", Rock="#4b3e3c", Crust="#2f2526", Steam="#ece8e4", Front="#ff00ff")
    rng = random.Random(seed)
    m.block("Lava", 0, -6.5, 0.15, 5, 13, 0.3)  # a channel across the rim
    for side in (-1, 1):
        for y, s in ((-11, 2.6), (-7.5, 2.2), (-4, 2.4), (-0.9, 2.0)):
            m.block("Rock", side * 3.6, y, s * 0.35, s, s * 1.1, s * 0.7)
    m.block("Lava", 0, 0.9, -0.15, 5, 2.0, 0.7)  # curling over the lip
    m.block("Lava", 0, 2.0, -1.2, 5.2, 1.4, 2.0)
    # The curtain, standing clear of the wall's hanging grass (1.5 out), in chunks of different widths.
    z = -1.5
    while z > -43.5:
        length = min(rng.uniform(4, 7), z + 43.5)
        m.block("Lava", rng.uniform(-0.4, 0.4), 2.4, z - length / 2, rng.uniform(4.6, 6.2), 1.2, length)
        z -= length
    for x, z0, z1 in ((-1.2, -3, -16), (0.9, -8, -27), (-0.3, -20, -38), (1.6, -30, -42)):
        m.block("Ember", x, 3.03, (z0 + z1) / 2, 0.45, 0.08, z0 - z1)
    # The pool at its foot, against the wall.
    m.block("Lava", 0, 3.5, -43.75, 11, 7, 0.5)
    m.block("Lava", 0, 7.2, -43.75, 7, 2.4, 0.5)
    for x, y, s in ((-6.2, 2.5, 1.8), (-4.8, 6.6, 1.6), (-1.6, 8.8, 1.4), (2.2, 8.6, 1.6), (5.0, 6.4, 1.8), (6.3, 2.8, 1.5)):
        m.block("Crust", x, y, -44 + s * 0.3, s, s, s * 0.6)
    for x, y, s in ((-2.1, 4.6, 0.7), (2.4, 4.0, 0.6), (0.4, 6.0, 0.5)):
        m.block("Lava", x, y, -43.2 + s, s, s, s)
    for x, y, z, s in ((-1.5, 5.5, -40.5, 2.2), (1.8, 6.5, -38.6, 2.8), (-0.6, 7.6, -36.2, 3.4)):
        m.block("Steam", x, y, z, s, s, s * 0.8)
    m.block("Front", 0, 6, -20, 0.2, 0.2, 0.2)
    return m


def rock_arch(seed=12):
    """A natural basalt arch over the corridor, rim to rim, with lava running along its top and dripping
    off its underside. It spans X; its feet stand on the rims beyond 36 studs from the middle, and all of
    it stays above the rim's height (z 0), clear of the flight camera."""
    m = prop("RockArch", Rock="#4b3e3c", RockDark="#352c2c", Crust="#5c2f26", Lava="#ff6a1a", Ember="#ffc23a", Obsidian="#1f1a25", Front="#ff00ff")
    rng = random.Random(seed)

    def underside(x):
        return 5 + 7 * (1 - (x / 46) ** 2)

    for side in (-1, 1):
        m.block("Rock", side * 49, 0, 3, 20, 13, 6)
        m.block("RockDark", side * 46.5, 0.5, 8, 15, 11, 4)
        m.block("Rock", side * 43.5, -0.3, 11.2, 11, 10, 2.6)
    for i in range(-5, 6):
        x = i * 8
        bottom = underside(x)
        m.block("Rock" if i % 2 == 0 else "RockDark", x, rng.uniform(-0.5, 0.5), bottom + 3, 8.4, rng.uniform(8.6, 10), 6)
        m.block("Crust", x, 0, bottom + 6.05, 8.4, 4.2, 0.2)
        m.block("Lava", x, 0, bottom + 6.2, 8.5, 2.8, 0.3)
    for k in range(10):
        x = -30 + k * 6.6 + rng.uniform(-1.5, 1.5)
        y = rng.uniform(-3, 3)
        under = underside(x)
        length = rng.uniform(1.8, min(4.5, under - 3))
        m.loft_z("Lava", (under - length, x, y, 0.22, 0.22), (under + 0.3, x, y, 0.95, 0.95))
        m.block("Ember", x, y, under - length - 0.2, 0.32, 0.32, 0.32)
    for x, y, height in ((-24, 2.6, 2.6), (-6, -3.2, 3.4), (14, 3.0, 2.2), (28, -2.8, 2.8)):
        base = underside(x) + 6
        prism(m, "Obsidian", x, y, base - 0.2, base + height, 0.8, 0.04, 4, 0.5, (0.3, -0.3))
    m.block("Front", 0, 6, 3, 0.2, 0.2, 0.2)
    return m


# ---------------------------------------------------------------------- preview stage


def corridor_stage(stage, length=300, seed=7):
    """A stretch of corridor in the Volcano's colours (floor z 0, walls 44 high, inner faces 36 from the middle)."""
    m = Model("VolcanoCorridor", dict(CORRIDOR))
    m.bone = "Root"
    for ix in range(9):
        for iy in range(length // 8):
            m.block("FloorA" if (ix + iy) % 2 == 0 else "FloorB", -32 + ix * 8, -iy * 8 - 4, -0.5, 8, 8, 1)
    rng = random.Random(seed)
    for side in (-1, 1):
        for iz in range(6):
            for iy in range(length // 8):
                m.block("Dirt" if (iz + iy) % 2 == 0 else "DirtB", side * 72, -iy * 8 - 4, iz * 7 + 3.5, 72, 8, 7)
        m.block("Grass", side * 72, -length / 2, 45, 72, length, 2)
        m.block("Grass", side * 35.25, -length / 2, 42, 1.5, length, 4)
        y = 0
        while y < length:
            drip = rng.choice((0, 4, 4, 8, 8, 12, 16))
            if drip:
                m.block("Grass", side * 35.25, -y - 4, 40 - drip / 2, 1.5, 8, drip)
            y += 8
    return m.build(stage)


def hide_markers(roots):
    for root in roots:
        for child in root.children:
            if child.name.endswith("_Front"):
                child.hide_render = True


def set_visible(roots, shown):
    kit.set_visible(roots, shown)
    hide_markers(roots)


def decorate_stage(stage, built, length=300, seed=31):
    """The corridor's props laid out like Config/Decor's Volcano rules, so the render shows the real mix."""
    rng = random.Random(seed)

    def pick(table):
        total = sum(w for _, w, _ in table)
        roll = rng.uniform(0, total)
        for name, weight, scale in table:
            roll -= weight
            if roll <= 0:
                return name, scale
        return table[-1][0], table[-1][2]

    floor = [("prop_LavaPool", 16, (1.2, 1.6)), ("prop_ObsidianSpire", 14, (1.2, 1.6)), ("prop_CharredTree", 14, (1.3, 1.7)),
             ("prop_BasaltColumns", 12, (1.2, 1.6)), ("prop_LavaRock", 12, (1.2, 1.7)), ("prop_SteamVent", 10, (1.2, 1.5)),
             ("prop_FireFlower", 8, (1.3, 1.8))]
    extras = [("prop_FireFlower", 4, (0.8, 1.2)), ("prop_LavaRock", 3, (0.5, 0.8)), ("prop_BasaltColumns", 2, (0.5, 0.7))]
    rim = [("prop_ObsidianSpire", 4, (2, 2.8)), ("prop_CharredTree", 4, (2, 2.6)), ("prop_BasaltColumns", 3, (2, 2.6)),
           ("prop_SteamVent", 2, (2, 2.4)), ("prop_LavaPool", 2, (2, 2.6))]
    copies = []

    def put(name, location, yaw, scale):
        copy = place_copy(built[name], stage, location, yaw, scale)
        hide_markers([copy])
        copies.append(copy)

    def put_random(table, x, z, y):
        name, (low, high) = pick(table)
        put(name, (x, -y, z), rng.uniform(0, math.tau), rng.uniform(low, high))

    y = 12
    while y < length - 14:
        side = rng.choice((-1, 1))
        x = side * rng.uniform(20, 27)
        put_random(floor, x, 0, y)
        if rng.random() < 0.55:
            put_random(extras, side * min(max(abs(x) + rng.uniform(-8, 8), 16), 33), 0, y + rng.uniform(-8, 8))
        y += rng.uniform(14, 26)
    y = 10
    while y < length:
        for side in (-1, 1):
            if rng.random() < 0.8:
                put_random(rim, side * rng.uniform(56, 94), 44, y)
        y += rng.uniform(22, 34)
    # The set pieces: volcanoes on the rims, lava falls down the walls, an arch across.
    for y, x, yaw, scale in ((60, 74, 20, 1.7), (230, -72, 200, 1.9)):
        put("prop_Volcano", (x, -y, 44), math.radians(yaw), scale)
    for y, side in ((40, 1), (150, -1), (255, 1)):
        put("prop_LavaFall", (side * 36, -y, 44), side * math.pi / 2, 1)
    put("prop_RockArch", (0, -120, 44), 0, 1)
    for y, x, yaw in ((30, -4, 15), (95, 6, 160), (175, -2, 80), (250, 3, 220)):
        put("prop_LavaCracks", (x, -y, 0), math.radians(yaw), 1.3)
    return copies


def light_up(roots, strength=2.4):
    """Glowing roles shine in the renders. Undone before saving, so the export stays plain colours."""
    for root in roots:
        for child in root.children:
            if child.type == "MESH" and child.name.rsplit("_", 1)[-1] in GLOW_ROLES:
                for mat in child.data.materials:
                    nodes = mat.node_tree.nodes
                    bsdf = nodes.get("Principled BSDF")
                    bsdf.inputs["Emission Color"].default_value = nodes["Colour"].outputs[0].default_value
                    bsdf.inputs["Emission Strength"].default_value = strength


def set_sky(scene, hex_colour):
    sky = [n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND" and n.name != "Background"][0]
    sky.inputs["Color"].default_value = (*kit.srgb_to_linear(hex_colour), 1)


def camera_shot(scene, name, position, target, size, lens):
    kit.shoot(scene, name, position, target, size, lens)


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

    models = [toasty_raptor(), burnt_ankylo(), hot_sauce_trike(), magma_stego(), obsidian_rex(), volcano_king()]
    prop_models = [volcano(), obsidian_spire(), lava_pool(), charred_tree(), steam_vent(), basalt_columns(), lava_rock(),
                   fire_flowers(), lava_cracks(), lava_fall(), rock_arch()]
    roots = []
    x = 0
    for model in models:
        root = model.build(animals)
        root.location = (x, 0, 0)
        roots.append(root)
        x += 18
    built = {}
    prop_roots = []
    spots = {"prop_Volcano": (0, -60, 0), "prop_LavaFall": (40, -150, 44), "prop_RockArch": (130, -150, 0)}
    x = 40
    for model in prop_models:
        root = model.build(props)
        if model.name in spots:
            root.location = spots[model.name]
        else:
            root.location = (x, -40, 0)
            x += 22
        built[model.name] = root
        prop_roots.append(root)
    light_up(roots + prop_roots)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-300, -400, -0.01), (400, -400, -0.01), (400, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", CORRIDOR["FloorA"], False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = Model("Player", {"Skin": "#3f4553"})
    player.bone = "Root"
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    player_root = player.build(stage)
    player_root.location = (-9, 0, 0)
    bpy.context.view_layer.update()
    set_sky(scene, SKY)

    everything = roots + prop_roots + [player_root]
    # Each monster at rest: whole, face, straight on.
    for model, root in zip(models, roots):
        set_visible(everything, [root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 3)
        kit.shoot(scene, f"{model.name}_full", centre + Vector((0.62, 0.85, 0.32)) * reach * 1.15, centre, (800, 800), 50)
        head = root.location + Vector(model.head_centre)
        size = max(3.2, model.head_centre[2] * 0.75)
        kit.shoot(scene, f"{model.name}_face", head + Vector((0.55, 1.0, 0.14)) * size * 1.5, head, (700, 700), 50)
        kit.shoot(scene, f"{model.name}_front", head + Vector((0, 1, 0.1)) * size * 1.6, head, (700, 700), 50)
    set_visible(everything, roots + [player_root])
    lineup = ((45, 84, 20), (45, 0, 4.5), (1800, 700), 26)
    kit.shoot(scene, "lineup", *lineup)
    saved = kit.tint_mutation(models, "#ffc628")
    kit.shoot(scene, "lineup_Gold", *lineup)
    for node, value in saved:
        node.outputs[0].default_value = value

    # Props, one by one with the player for scale, then all together.
    for model, root in zip(prop_models, prop_roots):
        low, high = kit.bounds(root)
        player_root.location = Vector((low.x - 3, (low.y + high.y) / 2 + 2, root.location.z if model.name != "prop_LavaFall" else 0))
        bpy.context.view_layer.update()
        set_visible(everything, [root, player_root])
        centre = (low + high) / 2
        reach = max((high - low).length, 7)
        if model.name == "prop_RockArch":
            kit.shoot(scene, model.name, centre + Vector((-25, 125, 10)), centre, (1400, 700), 32)
        elif model.name == "prop_LavaFall":
            kit.shoot(scene, model.name, centre + Vector((40, 55, 6)), centre, (700, 900), 40)
        else:
            kit.shoot(scene, model.name, centre + Vector((0.5, 0.9, 0.42)) * reach * 1.25, centre, (600, 600), 50)
    player_root.location = (30, -40, 0)
    bpy.context.view_layer.update()
    set_visible(everything, [r for r in prop_roots if r.name not in ("prop_LavaFall", "prop_RockArch")] + [player_root])
    kit.shoot(scene, "props", (106, 45, 38), (106, -45, 5), (1800, 700), 20)

    # The animation: each monster's walk twice, then the idle through its roar, turned so the strides show.
    set_visible(everything, roots)
    actions = [animate(root) for root in roots]
    for model, root, pair in zip(models, roots, actions):
        root.animation_data.action = pair[1]
    scene.frame_set(ROAR_FRAME)
    for model, root in zip(models, roots):
        set_visible(everything, [root])
        head = root.location + Vector(model.head_centre)
        size = max(3.2, model.head_centre[2] * 0.75)
        kit.shoot(scene, f"{model.name}_roar", head + Vector((0.55, 1.0, 0.3)) * size * 1.7, head + Vector((0, 0.3, 0.6)), (700, 700), 50)
    set_visible(everything, roots)
    frames_dir = RENDERS / "anim_frames"
    frames_dir.mkdir(exist_ok=True)
    for root in roots:
        root.rotation_euler = (0, 0, math.radians(-55))
    data = bpy.data.cameras.new("Preview")
    data.lens = 26
    camera = bpy.data.objects.new("Cam_Preview", data)
    camera.location = (46, 76, 15)
    scene.collection.objects.link(camera)
    camera.rotation_euler = (Vector((46, 0, 4.5)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = 1800, 640
    shots = [(0, f % kit.WALK_FRAMES) for f in range(0, kit.WALK_FRAMES * 2, 2)]
    shots += [(1, f) for f in range(ROAR_FRAME - 50, ROAR_FRAME + 50, 2)]
    for number, (which, frame) in enumerate(shots):
        for root, pair in zip(roots, actions):
            root.animation_data.action = pair[which]
        scene.frame_set(frame)
        scene.render.filepath = str(frames_dir / f"f{number:04d}.png")
        bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera)
    video = RENDERS / "volcano_animation_preview.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "15", "-i", str(frames_dir / "f%04d.png"),
                    "-pix_fmt", "yuv420p", "-vf", "scale=1800:-2", str(video)], check=True)
    for frame in frames_dir.glob("*.png"):
        frame.unlink()
    frames_dir.rmdir()
    print("video", video)
    for root, pair in zip(roots, actions):
        root.rotation_euler = (0, 0, 0)
        root.animation_data.action = None
    scene.frame_set(0)
    for root in roots:
        for bone in root.pose.bones:
            bone.location = (0, 0, 0)
            bone.rotation_euler = (0, 0, 0)

    # The whole look: a stretch of Volcano corridor with its props, then its monsters at their game size.
    ground.hide_render = True
    set_visible(everything, [])
    corridor = corridor_stage(stage)
    copies = decorate_stage(stage, built)
    set_sky(scene, SKY)
    kit.shoot(scene, "corridor_flight", (0, 40, 72), (0, -160, 10), (1600, 900), 24)
    kit.shoot(scene, "corridor_floor", (-14, -60, 12), (6, -170, 8), (1600, 900), 22)
    homes = [root.location.copy() for root in roots]
    for root, (x, y, yaw) in zip(roots, ((-20, -78, -15), (-1, -80, 8), (18, -78, 20), (-21, -112, -10), (1, -114, 5), (22, -112, 15))):
        root.location = (x, y, 0)
        root.rotation_euler = (0, 0, math.radians(yaw))
        root.scale = (GAME_SCALE,) * 3
    set_visible(everything, roots)
    kit.shoot(scene, "corridor_monsters", (0, -18, 26), (0, -100, 16), (1600, 900), 24)
    for root, home in zip(roots, homes):
        root.location = home
        root.rotation_euler = (0, 0, 0)
        root.scale = (1, 1, 1)

    # Tidy the .blend: the stage goes, glow goes back to plain colour for the export.
    for root in [corridor] + copies:
        for child in list(root.children):
            bpy.data.objects.remove(child)
        bpy.data.objects.remove(root)
    light_up(roots + prop_roots, 0)
    ground.hide_render = False
    set_visible(everything, everything)
    for root in prop_roots:
        for child in root.children:
            child.hide_render = False
    player_root.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "volcano_models.blend"))
    print("saved", HERE / "volcano_models.blend")
    for model in models + prop_models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    main()
