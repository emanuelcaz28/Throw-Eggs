"""Builds The Abyss's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_abyss_monsters.py

Saves abyss_monsters.blend and renders to design/world/monsters_abyss/. The Abyss's props are in build_abyss.py.

The owner asked for monsters that are actually nice and very aggressive, so every one of them is a predator,
the common ones included. The abyss face: eyes glowing cyan with a slit pupil under a heavy brow slanting down
to the snout, a crimson mouth gaping open and crammed with teeth, and glowing cyan spots and stripes along the
flanks like deep-sea photophores (pink on lures and suckers). Dark navy, slate and teal skin with pale bellies,
the map's colours, so they belong to it on sight.

  Spiral Gary    an ammonite gone bad: a spiked spiral shell, two huge glaring eyes, a hooked beak full of
                 teeth, eight tentacles with glowing suckers and hooks, two of them long with spiked clubs
  Derpichthys    an anglerfish all mouth: an underbite jutting past its face, crossed needle fangs a third of
                 its height, furious little eyes and a glowing pink lure dangling in front of it all
  Dunkleosteus   an armoured fish: a helmet of bone plates with glowing seams, blade jaws with fangs at the
                 front, deep-set eyes in armoured sockets, spikes on its helmet
  Plesiosaur     a long-necked hunter rearing to strike, needle teeth splayed out of its narrow jaws, four big
                 flippers, spines down its neck and glowing spots down its back
  Megalodon      the giant shark: a gaping mouth with two rows of triangle teeth, claw scars down one flank, a
                 harpoon still stuck in its back with its rope trailing
  Mosasaurus     the boss: a sea dragon with croc jaws and two rows of hooked teeth, a crown of swept-back
                 horns, a crest of glowing spines from its head to its fluke, glowing stripes, scars and barnacles

They swim instead of walking: every one has a Swim bone, which tells DinoLifeController to play the swim and
hover moves below (their tail beats, fins and flippers paddle, Spiral Gary's tentacles pulse and the lure
bobs) and, once per idle loop, an attack: it rears up and lunges with its jaw wide, shaking its head and
thrashing its tail. They float just above the ground, so on a base they hover. Glowing parts are EyeGlow,
Glow and Shine (Neon in the game, shared/Roles.luau). Built at the first map's size; the game makes them
7.2x (Config/Biomes standardScale). 1 Blender unit = 1 stud, models face +Y, ground at Z = 0.
"""
import math
import random
import sys
from pathlib import Path

from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_desert import beam  # noqa: E402
from build_forest import Model  # noqa: E402
from build_shadow_bog import limb  # noqa: E402
from build_shadow_bog_monsters import glow_eye  # noqa: E402
from build_volcano import prism, roar  # noqa: E402
from monster_stage import build_and_render  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_abyss"

GLOW_ROLES = {"EyeGlow", "Glow", "Shine"}

# The abyss face, and the map's glow (build_abyss.py).
FACE = {"EyeGlow": "#3ff2ff", "Pupil": "#03121a", "Highlight": "#ffffff", "Mouth": "#14060a", "Tongue": "#a3213b",
        "Teeth": "#f4f0e4", "Glow": "#5cf4ff", "Shine": "#ff62d6"}
SKY, FLOOR = "#2f6fa8", "#3b78a0"


def monster(name, **colours):
    return Model(f"dino_{name}", {**FACE, **colours})


# ---------------------------------------------------------------------- shape helpers


def snapshot(m):
    """How far each role's vertices have got, so the parts built after it can be turned on their own."""
    return {role: len(verts) for role, (verts, _) in m.parts.items()}


def turn_since(m, since, pivot, angle, axis=(1, 0, 0)):
    """Turns everything built after snapshot `since` round pivot: a jaw modelled shut, then dropped open."""
    turn = Matrix.Rotation(angle, 3, Vector(axis))
    centre = Vector(pivot)
    for role, (verts, _) in m.parts.items():
        start = since.get(role, 0)
        verts[start:] = [tuple(turn @ (Vector(v) - centre) + centre) for v in verts[start:]]


def at(a, b, y):
    """A body ring (y, z, width, height) between rings a and b, at y: its centre height, half width and height."""
    t = (y - a[0]) / (b[0] - a[0])
    z, w, h = (a[k] + (b[k] - a[k]) * t for k in (1, 2, 3))
    return z, w / 2, h


def chain(m, rings, bones, role="Body", belly="Belly", decorate=None):
    """A body lofted front to back through rings (y, z, width, height), with a pale belly band along its
    underside. bones: {segment: (bone, parent)}: that segment and the ones after it go on a new bone pivoted at
    its front ring, bending smoothly from the last one. decorate(i, a, b) runs while each segment's bone is
    current, for the fins, spines and spots on it."""
    for i, (a, b) in enumerate(zip(rings, rings[1:])):
        spec = bones.get(i)
        if spec:
            m.use(spec[0], (0, a[0], a[1]), spec[1])
        m.loft_y(role, (a[0], 0, a[1], a[2], a[3]), (b[0], 0, b[1], b[2], b[3]))
        if spec:
            m.stretch(role, spec[1])
        if belly:
            m.loft_y(belly, (a[0], 0, a[1] - a[3] * 0.31, a[2] * 1.02, a[3] * 0.42),
                     (b[0], 0, b[1] - b[3] * 0.31, b[2] * 1.02, b[3] * 0.42))
            if spec:
                m.stretch(belly, spec[1])
        if decorate:
            decorate(i, a, b)


def flank_dots(m, a, b, step=0.42, share=0.0, size=0.13, role="Glow", offset=0.0):
    """A row of glowing spots down both flanks of a body segment, at share of its height above its middle."""
    y = a[0] - offset
    while y > b[0] + 0.05:
        z, half, h = at(a, b, y)
        for side in (-1, 1):
            m.block(role, side * (half + 0.012), y, z + share * h, 0.06, size * 1.3, size)
        y -= step


def back_spine(m, a, b, y, height, role="Claw", tip=None, lean=0.3):
    """A spine on the middle of a segment's back, leaning back; tip: a role for its glowing point."""
    z, _, h = at(a, b, y)
    top = z + h / 2
    if tip:
        prism(m, role, 0, y, top - 0.12, top + height * 0.65, height * 0.3, height * 0.15, 4, math.pi / 4, (0, -lean * height * 0.65))
        prism(m, tip, 0, y - lean * height * 0.65, top + height * 0.65, top + height, height * 0.15, 0.02, 4, math.pi / 4, (0, -lean * height * 0.35))
    else:
        prism(m, role, 0, y, top - 0.12, top + height, height * 0.3, 0.02, 4, math.pi / 4, (0, -lean * height))


def fang(m, x, y, z, length, base, down, lean=(0, 0), flat=None, role="Teeth"):
    """A tooth from z, pointing down (an upper tooth) or up (a lower one). flat "x": thin across, for the side
    teeth of a shark; "y": thin front to back, for its front teeth."""
    wx = base * (0.38 if flat == "x" else 1)
    wy = base * (0.38 if flat == "y" else 1)
    tip = z - length if down else z + length
    m.loft_z(role, (z, x, y, wx, wy), (tip, x + lean[0], y + lean[1], 0.03, 0.03))


def jaws(m, head_bone, front, length, mouth_z, skull_w, snout_w, upper_h, lower_h, gap, drop, rng, style="cone",
         per_side=5, front_row=2, tooth=0.26, rows=1, front_scale=1.25, upper="Body", lower="Body", chin="Belly",
         lower_len=0.95, hinge_back=0.0):
    """Long jaws gaping open: an upper jaw from `front` forward, and a lower one on a Jaw bone hinged at its back,
    modelled shut and dropped open by `drop` radians. Crimson inside with a dark throat, teeth along both jaws
    and across their fronts. style: "cone" (hooked back), "triangle" (a shark's flat blades), "needle" (long and
    splayed outwards). rows 2 adds a smaller inner row. Call it on the head's bone. Returns the snout tip's y."""
    upper_z = mouth_z + gap / 2 + upper_h / 2
    lower_z = mouth_z - gap / 2 - lower_h / 2
    back = (front, 0, upper_z + upper_h * 0.1, skull_w * 0.94, upper_h * 1.2)
    tip = (front + length, 0, upper_z, snout_w, upper_h)
    m.loft_y(upper, back, tip)
    edge = mouth_z + gap / 2
    m.loft_y("Tongue", (front + 0.04, 0, edge - 0.02, skull_w * 0.72, 0.04), (front + length * 0.9, 0, edge - 0.02, snout_w * 0.6, 0.04))
    m.block("Mouth", 0, front + 0.06, mouth_z - lower_h * 0.25, skull_w * 0.76, 0.1, gap + lower_h * 1.3)

    def half(ra, rb, y):
        t = (y - ra[0]) / (rb[0] - ra[0])
        return (ra[3] + (rb[3] - ra[3]) * t) / 2

    def tooth_at(x, y, z, size, down, side, is_front):
        if style == "triangle":
            fang(m, x, y, z, size * 1.15, size, down, (0, -size * 0.12), "y" if is_front else "x")
        elif style == "needle":
            out = 0 if is_front else side
            fang(m, x, y, z, size * 2.5, size * 0.5, down, (out * size * 0.8 + (x * 0.25 if is_front else 0), size * 0.55))
        else:
            fang(m, x, y, z, size * 1.35, size * 0.78, down, (side * size * 0.12, -size * 0.3))

    def row(ra, rb, start, span, count, z, down, scale=1.0, inset=0.0):
        for side in (-1, 1):
            for i in range(count):
                y = start + span * i / max(count - 1, 1)
                size = tooth * scale * (1.0 if i % 2 == 0 else 0.72) * rng.uniform(0.9, 1.1)
                x = side * (half(ra, rb, y) - size * 0.35 - inset)
                tooth_at(x, y, z, size, down, side, False)

    def across(y, width, count, z, down, scale):
        for k in range(count):
            size = tooth * scale * rng.uniform(0.92, 1.08)
            x = -width / 2 + width * (k + 0.5) / count
            tooth_at(x, y, z, size, down, 1 if x > 0 else -1, True)

    row(back, tip, front + length * 0.1, length * 0.78, per_side, edge + 0.02, True)
    if rows == 2:
        row(back, tip, front + length * 0.18, length * 0.66, per_side - 1, edge + 0.02, True, 0.62, tooth * 0.75)
    across(front + length - tooth * 0.35, snout_w * 0.7, front_row, edge + 0.02, True, front_scale)

    mark = snapshot(m)
    pivot = (0, front - hinge_back, mouth_z)
    m.use("Jaw", pivot, head_bone)
    jaw_len = length * lower_len + hinge_back
    jb = (front - hinge_back, 0, lower_z, skull_w * 0.86, lower_h)
    jt = (front - hinge_back + jaw_len, 0, lower_z, snout_w * 0.9, lower_h)
    m.loft_y(lower, jb, jt)
    m.loft_y(chin, (jb[0], 0, lower_z - lower_h * 0.32, jb[3] * 1.02, lower_h * 0.42), (jt[0], 0, lower_z - lower_h * 0.32, jt[3] * 1.02, lower_h * 0.42))
    floor = mouth_z - gap / 2
    m.loft_y("Tongue", (front + 0.04, 0, floor + 0.02, skull_w * 0.64, 0.04), (jt[0] - length * 0.1, 0, floor + 0.02, snout_w * 0.56, 0.04))
    row(jb, jt, front + length * 0.16, jaw_len - hinge_back - length * 0.3, max(per_side - 1, 2), floor - 0.02, False, 0.85)
    if rows == 2:
        row(jb, jt, front + length * 0.24, jaw_len - hinge_back - length * 0.42, max(per_side - 2, 2), floor - 0.02, False, 0.55, tooth * 0.75)
    across(jt[0] - tooth * 0.35, snout_w * 0.6, max(front_row - 1, 1), floor - 0.02, False, front_scale * 0.85)
    turn_since(m, mark, pivot, -drop)
    m.bone = head_bone
    return front + length


def eyes(m, half_w, y, z, size, slant=1.1, brow="Accent", wide=1.1):
    for side in (-1, 1):
        glow_eye(m, side * half_w, y, z, size, side, facing="side", slant=slant, brow_role=brow, wide=wide)


def scars(m, side, x, marks, role="Scar"):
    """Claw marks on a flank: marks are ((y, z), (y, z)) slashes at x."""
    for (y0, z0), (y1, z1) in marks:
        beam(m, role, (side * x, y0, z0), (side * x, y1, z1), 0.05, 0.11, 0.04)


def fin_x(m, role, side, root, tip):
    """A fin standing out sideways: root and tip are (x, y, z, depth, thickness)."""
    m.loft_x(role, (side * root[0], root[1], root[2], root[3], root[4]), (side * tip[0], tip[1], tip[2], tip[3], tip[4]))


def flippers(m, role, edge, front, back, parent="Swim"):
    """Four paddle flippers on Flipper bones: front and back are lists of (x, y, z, depth, thickness) from root
    to tip, mirrored for the left side; edge is the role of the glowing spots along them."""
    for name, points in (("F", front), ("B", back)):
        for side, letter in ((-1, "L"), (1, "R")):
            m.use(f"Flipper{name}{letter}", (side * points[0][0], points[0][1], points[0][2]), parent)
            for k, (a, b) in enumerate(zip(points, points[1:])):
                fin_x(m, role, side, a, b)
                if k == 0:
                    m.stretch(role, parent)
            for a, b in zip(points, points[1:]):
                mid = [(a[k] + b[k]) / 2 for k in range(5)]
                m.block(edge, side * mid[0], mid[1] - mid[3] * 0.25, mid[2] + mid[4] / 2 + 0.01, 0.16, 0.16, 0.04)
    m.bone = parent


# ---------------------------------------------------------------------- the monsters


def spiral_gary():
    """An ammonite gone bad: a spiralled shell with spikes down its keel and glowing spots along its whorls,
    and out of its mouth a head with two huge glaring eyes, a hooked beak full of teeth and eight tentacles
    with glowing suckers and hooked tips, two of them long hunting arms with spiked clubs."""
    m = monster("SpiralGary", Body="#c4622d", Accent="#6b2316", Belly="#9a3f86", Claw="#efe2c6", Beak="#2b1d1c")
    rng = random.Random(1)
    m.use("Swim", (0, -0.6, 3.0), "Root")
    a, b = 0.17, 0.2
    y0, z0 = -0.6, 3.6
    points = []
    t = 0.6
    while t <= 3.5 * math.pi + 1e-6:
        r = a * math.exp(b * t)
        points.append((t, Vector((0, y0 + r * math.cos(t), z0 + r * math.sin(t))), r))
        t += 0.2
    for i, ((ta, p, r), (tb, q, rq)) in enumerate(zip(points, points[1:])):
        beam(m, "Body", tuple(p - (q - p) * 0.08), tuple(q + (q - p) * 0.08), r * 0.8, r * 0.95, rq * 0.8)
        along = (q - p).normalized()
        if i % 2 == 0:
            beam(m, "Accent", tuple(q - along * 0.1 * rq), tuple(q + along * 0.1 * rq), rq * 0.88, rq * 1.04)
        out = Vector((0, math.cos(tb), math.sin(tb)))
        if tb > 2.1 * math.pi and i % 2 == 1:  # spikes down the keel of the outer whorl
            base = q + out * rq * 0.45
            beam(m, "Claw", tuple(base), tuple(base + out * (0.25 + 0.3 * rq)), 0.22 * rq + 0.08, None, 0.03)
        if tb > 1.6 * math.pi and i % 3 == 0:  # glowing spots along both sides
            for side in (-1, 1):
                m.block("Glow", side * (rq * 0.4 + 0.012), q.y, q.z, 0.05, 0.14 + 0.06 * rq, 0.14 + 0.06 * rq)
        if tb > 2.6 * math.pi and i % 4 == 2:  # side spikes
            for side in (-1, 1):
                beam(m, "Claw", (side * rq * 0.38, q.y, q.z), (side * (rq * 0.38 + 0.3), q.y - 0.05, q.z + 0.12), 0.16, None, 0.02)
    _, end, r_end = points[-1]
    m.loft_y("Accent", (end.y - 0.15, 0, end.z, r_end * 0.9, r_end * 1.08), (end.y + 0.12, 0, end.z, r_end * 0.92, r_end * 1.1))  # the lip

    # The head coming out of the shell's mouth.
    m.use("Head", (0, -0.45, end.z), "Swim")
    hz = end.z
    m.loft_y("Belly", (-0.5, 0, hz, 1.2, 1.4), (0.75, 0, hz + 0.02, 1.45, 1.3))
    m.stretch("Belly", "Swim")
    m.loft_y("Accent", (-0.4, 0, hz + 0.78, 1.3, 0.3), (0.62, 0, hz + 0.72, 1.38, 0.24))  # a dark hood over the eyes
    for side in (-1, 1):
        glow_eye(m, side * 0.38, 0.75, hz + 0.26, 0.48, side, slant=1.25, brow_role="Accent", wide=1.0)
    # The beak, hooked down, with teeth inside it.
    m.loft_y("Beak", (0.7, 0, hz - 0.34, 0.6, 0.48), (1.32, 0, hz - 0.55, 0.18, 0.22))
    m.loft_y("Beak", (1.32, 0, hz - 0.55, 0.18, 0.22), (1.42, 0, hz - 0.78, 0.07, 0.08))
    m.block("Mouth", 0, 0.78, hz - 0.62, 0.48, 0.08, 0.3)
    for side in (-1, 1):
        for k in range(2):
            fang(m, side * 0.17, 0.92 + k * 0.17, hz - 0.58, 0.16, 0.08, True)
    mark = snapshot(m)
    m.use("Jaw", (0, 0.72, hz - 0.68), "Head")
    m.loft_y("Beak", (0.7, 0, hz - 0.78, 0.5, 0.3), (1.16, 0, hz - 0.7, 0.14, 0.14))
    m.loft_y("Tongue", (0.75, 0, hz - 0.62, 0.32, 0.03), (1.0, 0, hz - 0.62, 0.16, 0.03))
    for side in (-1, 1):
        fang(m, side * 0.14, 0.88, hz - 0.64, 0.14, 0.07, False)
    turn_since(m, mark, (0, 0.72, hz - 0.68), -0.32)

    # Eight tentacles in a ring round the beak, on two bones each (DinoLifeController knows their angles).
    cz = hz - 0.5
    for n in range(1, 9):
        th = tentacle_angle(n)
        u = Vector((math.cos(th), 0, math.sin(th)))
        base = Vector((0.6 * u.x, 0.62, cz + 0.4 * u.z))
        mid = base + u * 0.35 + Vector((0, 1.0, -0.26))
        tip = mid + u * 0.28 + Vector((0, 0.85, -0.4))
        hunter = n in (4, 7)
        if hunter:
            tip += Vector((0, 0.15, 0.05))
        end_point = tip + u * 0.15 + Vector((0, 1.2, 0.1)) if hunter else None
        for p in (mid, tip) + ((end_point,) if hunter else ()):
            p.z = max(p.z, 0.3)
        m.use(f"Tentacle{n}", tuple(base), "Head")
        beam(m, "Belly", tuple(base - Vector((0, 0.15, 0))), tuple(mid), 0.3, None, 0.22)
        m.stretch("Belly", "Head")
        m.use(f"Tentacle{n}b", tuple(mid), f"Tentacle{n}")
        m.block("Belly", *mid, 0.22, 0.22, 0.22)
        beam(m, "Belly", tuple(mid), tuple(tip), 0.22, None, 0.12 if not hunter else 0.16)
        m.stretch("Belly", f"Tentacle{n}")
        for p, q in ((base, mid), (mid, tip)):  # glowing suckers on the inner side
            for s in (0.35, 0.75):
                spot = p.lerp(q, s) - u * 0.12
                m.block("Shine", *spot, 0.09, 0.09, 0.09)
        if hunter:  # a long arm ending in a spiked club
            m.block("Belly", *tip, 0.17, 0.17, 0.17)
            beam(m, "Belly", tuple(tip), tuple(end_point), 0.15, None, 0.12)
            m.loft_y("Accent", (end_point.y - 0.1, end_point.x, end_point.z, 0.36, 0.36), (end_point.y + 0.45, end_point.x, end_point.z, 0.22, 0.22))
            for k in range(6):
                a2 = k * math.tau / 6
                d = Vector((math.cos(a2), 0.2, math.sin(a2))).normalized()
                c = end_point + Vector((0, 0.18, 0))
                beam(m, "Claw", tuple(c + d * 0.12), tuple(c + d * 0.36), 0.1, None, 0.02)
        else:  # a hooked claw at the tip
            beam(m, "Claw", tuple(tip), tuple(tip + Vector((0, 0.18, -0.12)) + u * 0.05), 0.11, None, 0.02)
    m.head_centre = (0, 0.8, hz)
    return m


def derpichthys():
    """An anglerfish that is all mouth: a huge underbite jutting past its face, crossed needle fangs a third of
    its height, furious little eyes under a heavy brow, spines down its back and a glowing pink lure dangling in
    front of the whole thing."""
    m = monster("Derpichthys", Body="#2e3448", Accent="#181c29", Belly="#4c5370", Claw="#6b4a8a")
    rng = random.Random(2)
    m.use("Swim", (0, 0, 1.95), "Root")
    rings = [(1.55, 2.15, 2.5, 2.45), (0.45, 2.05, 2.85, 2.8), (-0.75, 2.0, 2.45, 2.35), (-1.7, 2.05, 1.45, 1.45),
             (-2.4, 2.1, 0.8, 0.85), (-2.95, 2.1, 0.45, 0.55)]

    def decorate(i, a, b):
        if i < 4:
            flank_dots(m, a, b, 0.4, -0.12, 0.13)
            flank_dots(m, a, b, 0.55, 0.22, 0.1, offset=0.2)
        if i in (0, 1):  # a ridge of spines down its back, with a fin between them
            for y in ((1.1, 0.6) if i == 0 else (0.1, -0.4)):
                back_spine(m, a, b, y, 0.75, "Accent", lean=0.35)
            z, _, h = at(a, b, a[0] - 0.3)
            m.loft_z("Claw", (z + h / 2 - 0.05, 0, (a[0] + b[0]) / 2, 0.08, (a[0] - b[0]) * 0.9),
                     (z + h / 2 + 0.45, 0, (a[0] + b[0]) / 2 - 0.25, 0.05, (a[0] - b[0]) * 0.6))
        if i == 4:  # a fan of a tail
            m.loft_z("Claw", (2.25, 0, -2.92, 0.12, 0.6), (3.3, 0, -3.6, 0.05, 0.45))
            m.loft_z("Claw", (1.95, 0, -2.92, 0.12, 0.6), (0.95, 0, -3.5, 0.05, 0.4))
            m.loft_y("Claw", (-2.9, 0, 2.1, 0.1, 0.6), (-3.75, 0, 2.1, 0.06, 1.5))

    chain(m, rings, {2: ("Tail1", "Swim"), 3: ("Tail2", "Tail1"), 4: ("Tail3", "Tail2")}, decorate=decorate)
    m.bone = "Swim"
    for side, letter in ((-1, "L"), (1, "R")):
        m.use(f"Fin{letter}", (side * 1.38, 0.15, 1.6), "Swim")
        fin_x(m, "Claw", side, (1.36, 0.15, 1.6, 0.7, 0.12), (2.25, -0.4, 1.45, 1.0, 0.05))
        m.block("Glow", side * 2.15, -0.4, 1.48, 0.12, 0.12, 0.08)
    m.bone = "Swim"
    # The mouth: a wide upper head over a lower jaw jutting out past it.
    jaws(m, "Swim", 1.55, 1.1, 1.85, 2.5, 2.15, 1.15, 0.8, 0.3, 0.26, rng, style="needle", per_side=4, front_row=7,
         tooth=0.3, front_scale=1.3, upper="Body", lower="Body", chin="Belly", lower_len=1.3, hinge_back=0.25)
    m.block("Mouth", 0, 1.57, 1.45, 2.2, 0.06, 0.95)
    for side in (-1, 1):
        m.block("Accent", side * 0.62, 2.66, 2.84, 0.5, 0.06, 0.4)  # dark sockets
        glow_eye(m, side * 0.62, 2.71, 2.82, 0.36, side, slant=1.45, brow_role="Accent", wide=1.1)
    for side in (-1, 1):  # spikes over its cheeks and brow
        beam(m, "Accent", (side * 1.15, 1.6, 2.55), (side * 1.65, 1.2, 2.75), 0.22, None, 0.02)
        beam(m, "Accent", (side * 1.1, 1.0, 2.2), (side * 1.6, 0.6, 2.3), 0.2, None, 0.02)
        for y in (1.75, 2.15, 2.45):
            m.block("Glow", side * 1.06, y, 1.62, 0.06, 0.12, 0.1)
    # The lure: a stalk off its brow on two bones, and a glowing bulb dangling in front of its face.
    m.use("Lure", (0, 1.0, 3.32), "Swim")
    limb(m, "Accent", [(0, 0.95, 3.25), (0, 1.6, 4.15), (0, 2.3, 4.55)], 0.17, 0.13)
    m.stretch("Accent", "Swim")
    m.use("LureTip", (0, 2.3, 4.55), "Lure")
    limb(m, "Accent", [(0, 2.3, 4.55), (0, 2.95, 4.52), (0, 3.25, 4.2)], 0.13, 0.09)
    m.loft_z("Shine", (3.55, 0, 3.3, 0.32, 0.32), (3.85, 0, 3.3, 0.62, 0.62))
    m.loft_z("Shine", (3.85, 0, 3.3, 0.62, 0.62), (4.15, 0, 3.3, 0.3, 0.3))
    for d in ((0.3, 0.1, 3.6), (-0.3, -0.05, 3.7), (0.05, 0.32, 3.95)):
        m.block("Glow", d[0], 3.3 + d[1], d[2], 0.07, 0.07, 0.07)
    m.head_centre = (0, 2.2, 2.4)
    return m


def dunkleosteus():
    """An armoured fish: a helmet of bone plates with glowing seams, blade jaws with two great fangs at the
    front of each, deep-set eyes in armoured sockets, spikes along its helmet, and a shark's tail."""
    m = monster("Dunkleosteus", Body="#3e495b", Accent="#252d3a", Belly="#9ea8b4", Claw="#b0a690")
    rng = random.Random(3)
    m.use("Swim", (0, 0.4, 2.0), "Root")
    rings = [(1.45, 2.05, 2.45, 2.45), (0.2, 2.0, 2.35, 2.3), (-1.1, 2.0, 1.85, 1.85), (-2.3, 2.05, 1.25, 1.25),
             (-3.3, 2.1, 0.72, 0.72), (-4.1, 2.15, 0.42, 0.46)]

    def decorate(i, a, b):
        if i < 4:
            flank_dots(m, a, b, 0.42, 0.0, 0.12)
            flank_dots(m, a, b, 0.42, -0.24, 0.1, offset=0.21)
        if i == 0:  # armour over its shoulders and a dorsal fin
            for y in (1.2, 0.75):
                z, half, h = at(a, b, y)
                m.block("Claw", 0, y, z + h / 2 + 0.06, half * 1.5, 0.42, 0.16)
            m.loft_z("Accent", (3.05, 0, 0.55, 0.25, 1.4), (4.45, 0, -0.38, 0.06, 0.25))
        if i == 4:
            m.loft_z("Accent", (2.25, 0, -4.05, 0.2, 0.7), (3.95, 0, -5.35, 0.06, 0.28))
            m.loft_z("Accent", (2.0, 0, -4.05, 0.18, 0.6), (0.95, 0, -4.85, 0.05, 0.22))

    chain(m, rings, {1: ("Tail1", "Swim"), 2: ("Tail2", "Tail1"), 3: ("Tail3", "Tail2"), 4: ("Tail4", "Tail3")},
          decorate=decorate)
    for side, letter in ((-1, "L"), (1, "R")):
        m.use(f"Fin{letter}", (side * 1.15, 0.95, 1.35), "Swim")
        fin_x(m, "Accent", side, (1.1, 0.95, 1.3, 1.1, 0.2), (2.6, -0.25, 0.75, 0.3, 0.1))
    m.use("Head", (0, 1.45, 2.1), "Swim")
    skull = ((1.45, 2.25, 2.65, 2.6), (2.75, 2.42, 2.5, 2.2))
    m.loft_y("Claw", (skull[0][0], 0, skull[0][1], skull[0][2], skull[0][3]), (skull[1][0], 0, skull[1][1], skull[1][2], skull[1][3]))
    m.stretch("Claw", "Swim")
    tip = jaws(m, "Head", 2.75, 0.75, 1.62, 2.3, 1.6, 1.1, 0.5, 0.12, 0.34, rng, style="triangle", per_side=4, front_row=2,
               tooth=0.2, front_scale=2.6, upper="Claw", lower="Claw", chin="Accent", lower_len=1.0, hinge_back=1.0)
    # Glowing seams between the plates, rivets and spikes.
    top = skull[1][1] + skull[1][3] / 2
    m.block("Glow", 0, 2.76, top - 0.02, 2.3, 0.06, 0.06)
    for side in (-1, 1):
        m.block("Glow", side * 1.255, 2.76, 2.2, 0.06, 0.06, 1.5)
        m.block("Glow", side * 1.29, 2.1, 1.75, 0.06, 1.3, 0.06)
    m.block("Glow", 0, 2.1, top + 0.03, 0.06, 1.25, 0.06)
    for y in (1.75, 2.35):
        for side in (-1, 1):
            m.block("Accent", side * 0.55, y, top + 0.04, 0.16, 0.16, 0.08)
    for y, height in ((1.65, 0.75), (2.15, 0.6), (2.6, 0.45)):
        prism(m, "Claw", 0, y, top - 0.1, top + height, 0.24, 0.02, 4, math.pi / 4, (0, -0.25 * height))
    for side in (-1, 1):
        beam(m, "Claw", (side * 1.2, 1.7, 2.9), (side * 1.75, 1.25, 3.25), 0.26, None, 0.02)
        beam(m, "Claw", (side * 1.25, 1.9, 1.6), (side * 1.8, 1.5, 1.4), 0.22, None, 0.02)
        m.block("Accent", side * 0.62, 2.755, 3.22, 0.52, 0.06, 0.38)  # the eye sockets in the helmet's front
        glow_eye(m, side * 0.62, 2.8, 3.22, 0.34, side, slant=1.4, brow_role="Accent", wide=1.05)
        m.block("Mouth", side * 0.3, tip + 0.01, 2.75, 0.16, 0.06, 0.12)  # nostril pits
    m.block("Glow", 0, tip + 0.012, 2.35, 0.06, 0.04, 0.9)  # a seam down the front of its snout
    m.head_centre = (0, 2.7, 2.3)
    return m


def plesiosaur():
    """A long-necked hunter rearing to strike: its neck coiled up and over, needle teeth splayed out of its
    narrow jaws, four big flippers, bone spines down its neck and glowing spots down its back."""
    m = monster("Plesiosaur", Body="#36588a", Accent="#203a63", Belly="#cbd9e8", Claw="#ece4cf")
    rng = random.Random(4)
    m.use("Swim", (0, 0, 1.9), "Root")
    rings = [(1.35, 2.0, 1.45, 1.35), (0.45, 1.9, 2.3, 1.75), (-0.8, 1.85, 2.4, 1.8), (-1.9, 1.85, 1.75, 1.4),
             (-2.8, 1.9, 0.95, 0.85), (-3.6, 1.95, 0.4, 0.4)]

    def decorate(i, a, b):
        if i < 4:
            flank_dots(m, a, b, 0.45, 0.05, 0.12)
            z, half, h = at(a, b, (a[0] + b[0]) / 2)
            for k in range(4):  # spots across its back
                x = rng.uniform(-0.55, 0.55) * half
                y = rng.uniform(b[0] + 0.1, a[0] - 0.1)
                zz, hh, h2 = at(a, b, y)
                m.block("Glow", x, y, zz + h2 / 2 + 0.01, 0.16, 0.16, 0.04)
        if i in (1, 2, 3):
            back_spine(m, a, b, (a[0] + b[0]) / 2, 0.42, "Claw", lean=0.4)
        if i == 4:
            m.loft_z("Accent", (2.25, 0, -3.0, 0.1, 0.7), (2.85, 0, -3.6, 0.04, 0.2))
            m.loft_z("Accent", (1.65, 0, -3.0, 0.1, 0.6), (1.2, 0, -3.5, 0.04, 0.18))

    chain(m, rings, {3: ("Tail1", "Swim"), 4: ("Tail2", "Tail1")}, decorate=decorate)
    m.bone = "Swim"
    flippers(m, "Accent", "Glow", [(1.1, 0.6, 1.55, 0.9, 0.2), (2.4, 0.1, 1.2, 0.85, 0.16), (3.4, -0.7, 0.85, 0.3, 0.1)],
             [(1.1, -1.3, 1.5, 0.8, 0.18), (2.1, -1.9, 1.1, 0.7, 0.15), (2.9, -2.6, 0.85, 0.25, 0.08)])
    # The neck, coiled up and forward, on three bones.
    points = [Vector(p) for p in ((0, 1.2, 2.15), (0, 1.85, 2.9), (0, 2.2, 3.75), (0, 2.45, 4.55), (0, 2.85, 5.1))]
    widths = [1.15, 1.0, 0.9, 0.82, 0.76]
    heights = [1.05, 0.95, 0.86, 0.78, 0.72]
    bones = {0: ("Neck1", "Swim"), 1: ("Neck2", "Neck1"), 2: ("Neck3", "Neck2")}
    for i, (p, q) in enumerate(zip(points, points[1:])):
        spec = bones.get(i)
        if spec:
            m.use(spec[0], tuple(p), spec[1])
        beam(m, "Body", tuple(p), tuple(q), widths[i], heights[i], widths[i + 1])
        if spec:
            m.stretch("Body", spec[1])
        along = (q - p).normalized()
        throat = Vector((0, along.z, -along.y))  # the underside of the neck, in its plane
        beam(m, "Belly", tuple(p + throat * heights[i] * 0.3), tuple(q + throat * heights[i + 1] * 0.3), widths[i] * 1.02,
             heights[i] * 0.45, widths[i + 1] * 1.02)
        if spec:
            m.stretch("Belly", spec[1])
        m.block("Body", *q, widths[i + 1] * 0.88, widths[i + 1] * 0.88, heights[i + 1] * 0.88)
        mid = p.lerp(q, 0.5)
        nape = -throat
        beam(m, "Claw", tuple(mid + nape * heights[i] * 0.42), tuple(mid + nape * (heights[i] * 0.42 + 0.42) - along * 0.12),
             0.2, None, 0.02)
        for side in (-1, 1):
            m.block("Glow", side * (widths[i] * 0.47 + 0.02), *mid.yz, 0.05, 0.14, 0.14)
    m.use("Head", tuple(points[-1]), "Neck3")
    m.loft_y("Body", (2.75, 0, 5.15, 1.0, 0.95), (3.45, 0, 5.12, 0.95, 0.8))
    m.stretch("Body", "Neck3")
    jaws(m, "Head", 3.45, 1.35, 4.86, 0.95, 0.42, 0.44, 0.3, 0.08, 0.42, rng, style="needle", per_side=6, front_row=2,
         tooth=0.2, front_scale=1.2, lower_len=0.96, hinge_back=0.35)
    eyes(m, 0.49, 3.3, 5.34, 0.36, slant=1.25)
    for y, height in ((2.9, 0.42), (3.2, 0.32)):
        prism(m, "Claw", 0, y, 5.5, 5.55 + height, 0.15, 0.02, 4, math.pi / 4, (0, -0.2))
    m.head_centre = (0, 3.7, 5.0)
    return m


def megalodon():
    """The giant shark: a gaping mouth with two rows of triangle teeth under a long snout, cold glowing eyes,
    claw scars down one flank and a bite out of the other, a harpoon still stuck in its back with its rope
    trailing, and a glowing line down both flanks."""
    m = monster("Megalodon", Body="#56687e", Accent="#34435a", Belly="#dfe7ec", Claw="#3d4c62", Scar="#aebbc8",
                Iron="#5d636b", Rust="#9a4e2c", Rope="#cdb88c")
    rng = random.Random(5)
    m.use("Swim", (0, 0.4, 2.0), "Root")
    rings = [(1.7, 2.05, 2.15, 2.2), (0.3, 2.0, 2.35, 2.4), (-1.0, 2.05, 2.05, 2.1), (-2.2, 2.1, 1.45, 1.5),
             (-3.2, 2.15, 0.9, 0.95), (-4.0, 2.2, 0.52, 0.58), (-4.55, 2.2, 0.34, 0.5)]

    def decorate(i, a, b):
        if i < 5:
            flank_dots(m, a, b, 0.34, -0.05, 0.11)
        if i == 0:  # gill slits
            for y in (1.55, 1.3, 1.05, 0.8):
                z, half, h = at(a, b, y)
                for side in (-1, 1):
                    m.block("Accent", side * (half + 0.012), y, z + 0.05, 0.05, 0.09, h * 0.42)
        if i == 1:
            m.loft_z("Body", (3.1, 0, 0.35, 0.3, 2.0), (4.95, 0, -0.95, 0.07, 0.22))  # the dorsal fin
            m.loft_z("Accent", (4.35, 0, -0.62, 0.14, 0.6), (4.97, 0, -0.96, 0.08, 0.2))
            for side in (-1, 1):  # pelvic fins
                fin_x(m, "Accent", side, (0.7, -0.65, 1.05, 0.55, 0.12), (1.3, -1.1, 0.72, 0.15, 0.06))
        if i == 3:
            m.loft_z("Body", (2.55, 0, -2.9, 0.15, 0.5), (3.08, 0, -3.16, 0.04, 0.12))
            m.loft_z("Body", (1.72, 0, -2.95, 0.12, 0.45), (1.25, 0, -3.2, 0.04, 0.1))
        if i == 5:  # the crescent tail
            m.loft_z("Body", (2.35, 0, -4.45, 0.22, 0.75), (4.2, 0, -5.7, 0.06, 0.28))
            m.loft_z("Body", (2.05, 0, -4.45, 0.2, 0.6), (0.9, 0, -5.25, 0.05, 0.22))
            m.loft_z("Accent", (3.6, 0, -5.3, 0.1, 0.4), (4.22, 0, -5.72, 0.06, 0.2))

    chain(m, rings, {2: ("Tail1", "Swim"), 3: ("Tail2", "Tail1"), 4: ("Tail3", "Tail2"), 5: ("Tail4", "Tail3")},
          decorate=decorate)
    m.bone = "Swim"
    scars(m, 1, 1.15, [((0.95, 2.85), (0.05, 1.55)), ((0.6, 2.95), (-0.3, 1.65)), ((0.25, 3.0), (-0.65, 1.75))])
    for k in range(7):  # a bite out of its left flank: a curve of tooth marks
        a2 = math.pi * (0.15 + 0.7 * k / 6)
        m.block("Scar", -1.17, -0.25 + 0.75 * math.cos(a2), 1.75 + 0.6 * math.sin(a2) - 0.3, 0.05, 0.16, 0.22)
    beam(m, "Iron", (0.3, -0.55, 2.9), (1.25, -1.5, 4.55), 0.12)  # the harpoon
    beam(m, "Rust", (1.1, -1.35, 4.3), (1.32, -1.57, 4.67), 0.2)
    limb(m, "Rope", [(1.28, -1.55, 4.6), (1.65, -2.25, 4.15), (1.9, -2.95, 3.45), (1.95, -3.65, 2.95), (1.8, -4.15, 2.65)],
         0.09, 0.07, joints=False)
    beam(m, "Iron", (-0.6, -1.9, 2.6), (-1.45, -2.25, 3.3), 0.1)  # a broken one
    beam(m, "Rust", (-1.35, -2.2, 3.2), (-1.5, -2.28, 3.38), 0.16)
    for side, letter in ((-1, "L"), (1, "R")):
        m.use(f"Fin{letter}", (side * 1.05, 1.0, 1.35), "Swim")
        fin_x(m, "Body", side, (1.0, 0.95, 1.3, 1.15, 0.22), (2.75, -0.35, 0.72, 0.3, 0.1))
        fin_x(m, "Accent", side, (2.35, -0.05, 0.86, 0.5, 0.15), (2.76, -0.36, 0.71, 0.28, 0.1))
    # The head: a cap over the upper jaw, the jaws, and a long snout overhanging the teeth.
    m.use("Head", (0, 1.7, 2.05), "Swim")
    m.loft_y("Body", (1.7, 0, 2.6, 2.1, 1.1), (3.4, 0, 2.55, 1.35, 0.85))
    m.stretch("Body", "Swim")
    jaws(m, "Head", 1.7, 1.9, 1.35, 2.15, 1.1, 0.9, 0.42, 0.1, 0.34, rng, style="triangle", per_side=7, front_row=4,
         tooth=0.3, rows=2, front_scale=1.1, lower_len=0.92)
    m.loft_y("Body", (3.3, 0, 2.3, 1.3, 1.05), (4.4, 0, 2.38, 0.6, 0.55))  # the snout
    m.loft_y("Belly", (3.3, 0, 1.95, 1.32, 0.3), (4.4, 0, 2.18, 0.62, 0.15))
    for side in (-1, 1):
        m.block("Mouth", side * 0.24, 4.1, 2.12, 0.14, 0.2, 0.05)  # nostrils
    eyes(m, 0.84, 2.85, 2.45, 0.38, slant=1.15)
    beam(m, "Scar", (0.35, 3.0, 3.0), (0.1, 2.2, 3.08), 0.12, 0.04)  # a scar across the top of its head
    m.head_centre = (0, 3.2, 2.2)
    return m


def mosasaurus():
    """The boss: a sea dragon with croc jaws and two rows of hooked teeth, eyes glowing under armoured brows, a
    crown of swept-back horns, a crest of glowing spines from its head to its fluke, glowing stripes down its
    flanks, four flippers, scars and barnacles."""
    m = monster("Mosasaurus", Body="#26505f", Accent="#14303b", Belly="#bcd3c8", Claw="#e8dfc6", Scar="#86a8ad",
                Barnacle="#a6aea9")
    rng = random.Random(6)
    m.use("Swim", (0, 0.4, 2.2), "Root")
    rings = [(1.9, 2.3, 2.0, 1.9), (0.6, 2.2, 2.55, 2.4), (-0.9, 2.2, 2.5, 2.35), (-2.3, 2.25, 2.0, 1.85),
             (-3.6, 2.3, 1.4, 1.3), (-4.7, 2.35, 0.9, 0.85), (-5.6, 2.4, 0.5, 0.52), (-6.0, 2.4, 0.34, 0.45)]

    def decorate(i, a, b):
        if i < 6:  # glowing stripes slanting down its flanks
            y = a[0] - 0.3
            while y > b[0] + 0.1:
                z, half, h = at(a, b, y)
                for side in (-1, 1):
                    beam(m, "Glow", (side * (half + 0.012), y + 0.2, z + h * 0.32), (side * (half + 0.012), y - 0.28, z - h * 0.08), 0.05, 0.1)
                y -= 0.75
            spine_y = a[0] - 0.2
            k = 0
            while spine_y > b[0]:
                z, half, h = at(a, b, spine_y)
                height = (0.95 if k % 2 == 0 else 0.6) * (h / 2.35) ** 0.6
                back_spine(m, a, b, spine_y, height, "Claw", tip="Glow", lean=0.45)
                spine_y -= 0.55
                k += 1
        if i == 1:  # barnacles and scars
            for k in range(9):
                y = rng.uniform(-0.6, 1.4)
                z, half, h = at(a, b, max(min(y, a[0]), b[0]))
                x = rng.uniform(-0.6, 0.6) * half
                s = rng.uniform(0.1, 0.2)
                m.block("Barnacle", x + 0.25, y, z + h / 2 + s * 0.3, s, s, s * 0.8)
            scars(m, -1, 1.27, [((1.2, 2.9), (0.3, 1.7)), ((0.85, 3.0), (-0.05, 1.8)), ((0.5, 3.05), (-0.4, 1.9))])
        if i == 6:  # the fluke
            m.loft_z("Accent", (2.5, 0, -5.75, 0.22, 0.8), (4.15, 0, -7.0, 0.06, 0.3))
            m.loft_z("Accent", (2.3, 0, -5.75, 0.2, 0.7), (1.05, 0, -6.6, 0.05, 0.25))
            m.block("Glow", 0, -6.85, 3.85, 0.1, 0.22, 0.22)
            m.block("Glow", 0, -6.45, 1.3, 0.1, 0.2, 0.2)

    chain(m, rings, {2: ("Tail1", "Swim"), 3: ("Tail2", "Tail1"), 4: ("Tail3", "Tail2"), 5: ("Tail4", "Tail3")},
          decorate=decorate)
    m.bone = "Swim"
    flippers(m, "Accent", "Glow", [(1.15, 1.0, 1.55, 1.2, 0.28), (2.4, 0.4, 1.0, 0.9, 0.2), (3.3, -0.3, 0.7, 0.35, 0.12)],
             [(1.05, -1.7, 1.5, 0.9, 0.24), (2.0, -2.3, 1.05, 0.7, 0.18), (2.7, -2.9, 0.8, 0.28, 0.1)])
    m.use("Neck1", (0, 1.9, 2.3), "Swim")
    a, b = (1.9, 2.3, 2.0, 1.9), (3.05, 2.45, 1.8, 1.65)
    m.loft_y("Body", (a[0], 0, a[1], a[2], a[3]), (b[0], 0, b[1], b[2], b[3]))
    m.stretch("Body", "Swim")
    m.loft_y("Belly", (a[0], 0, a[1] - a[3] * 0.31, a[2] * 1.02, a[3] * 0.42), (b[0], 0, b[1] - b[3] * 0.31, b[2] * 1.02, b[3] * 0.42))
    m.stretch("Belly", "Swim")
    back_spine(m, a, b, 2.5, 0.8, "Claw", tip="Glow", lean=0.45)
    m.use("Head", (0, 3.05, 2.45), "Neck1")
    m.loft_y("Body", (3.0, 0, 2.62, 1.8, 1.4), (3.95, 0, 2.75, 1.62, 1.1))  # the skull, behind and above the jaws
    m.stretch("Body", "Neck1")
    jaws(m, "Head", 3.2, 2.5, 2.0, 1.72, 0.78, 0.65, 0.5, 0.12, 0.36, rng, style="cone", per_side=7, front_row=2,
         tooth=0.25, rows=2, front_scale=1.5, lower_len=0.95, hinge_back=0.05)
    eyes(m, 0.83, 3.62, 2.95, 0.54, slant=1.3)
    for side in (-1, 1):
        m.loft_y("Claw", (3.1, side * 0.82, 3.33, 0.28, 0.2), (3.95, side * 0.78, 3.22, 0.22, 0.14))  # armoured brows
        limb(m, "Claw", [(side * 0.55, 3.3, 3.25), (side * 0.95, 2.85, 3.85), (side * 1.12, 2.15, 4.3), (side * 1.05, 1.5, 4.45)],
             0.42, 0.05)  # the horn crown
        limb(m, "Claw", [(side * 0.72, 3.05, 2.85), (side * 1.25, 2.45, 2.95), (side * 1.6, 1.9, 3.05)], 0.26, 0.04)
        for y in (3.7, 4.3, 4.85, 5.3):
            m.block("Glow", side * (0.8 - (y - 3.2) * 0.17 + 0.03), y, 2.2, 0.05, 0.1, 0.07)  # spots along the jaw line
    for y, height in ((3.35, 0.5), (3.75, 0.36)):
        prism(m, "Claw", 0, y, 3.25, 3.3 + height, 0.17, 0.02, 4, math.pi / 4, (0, -0.25))
    for k in range(5):
        m.block("Barnacle", rng.uniform(-0.25, 0.25), rng.uniform(4.4, 5.3), 2.73, 0.13, 0.13, 0.1)
    m.head_centre = (0, 4.4, 2.5)
    return m


# ---------------------------------------------------------------------- the moves


SWIM_FRAMES = 36  # one tail beat, at 30 frames a second (Config/DinoLife swim.strideSeconds = 1.2)
SIDE = {"L": -1, "R": 1}


def tentacle_angle(n):
    """Where tentacle n (1 to 8) sits round Spiral Gary's beak: radians round the front, 0 is its right side."""
    return (n - 1) * math.tau / 8 + math.pi / 8


def tentacle(name, spread, wriggle):
    """A tentacle's pitch and yaw: spread opens it out from the beak, wriggle waves it round the beak."""
    n = int(name[8:].rstrip("b"))
    th = tentacle_angle(n)
    return spread * math.sin(th) + wriggle * math.cos(th), -spread * math.cos(th) + wriggle * math.sin(th)


def swim_motion(name, p):
    """While swimming: p runs through one tail beat. Returns pitch, roll, yaw, rise and surge, or None for a
    bone that doesn't move. DinoLifeController's SWIM copies this."""
    sin, cos = math.sin, math.cos
    if name == "Swim":
        return 0.03 * sin(2 * p), 0.05 * sin(p), -0.05 * sin(p), 0.06 * sin(2 * p), 0
    if name == "Head":
        return 0.02 * sin(2 * p), 0, -0.06 * sin(p), 0, 0
    if name.startswith("Neck"):
        i = int(name[4:])
        return 0.03 * sin(2 * p - 0.4 * i), 0, -0.05 * sin(p - 0.4 * i), 0, 0
    if name.startswith("Tail"):
        i = int(name[4:])
        return 0.02 * sin(2 * p - i), 0, (0.14 + 0.05 * i) * sin(p - 0.75 * i), 0, 0
    if name in ("FinL", "FinR"):
        return 0.08 * sin(p + 1), SIDE[name[-1]] * 0.18 * sin(p), 0, 0, 0
    if name.startswith("Flipper"):
        phase = 0 if name[7] == "F" else math.pi
        return 0.25 * cos(p + phase), SIDE[name[-1]] * 0.45 * sin(p + phase), 0, 0, 0
    if name == "Jaw":
        return -0.1 * (0.5 + 0.5 * sin(2 * p)), 0, 0, 0, 0
    if name == "Lure":
        return 0.15 * sin(2 * p), 0, 0.1 * sin(p), 0, 0
    if name == "LureTip":
        return 0.2 * sin(2 * p - 1), 0, 0, 0, 0
    if name.startswith("Tentacle"):
        n = int(name[8:].rstrip("b"))
        if name.endswith("b"):
            pitch, yaw = tentacle(name, 0.18 * sin(p - 1.2), 0.18 * sin(2 * p - 0.8 * n - 1))
        else:
            pitch, yaw = tentacle(name, 0.08 + 0.16 * (0.5 + 0.5 * sin(p)), 0.12 * sin(2 * p - 0.8 * n))
        return pitch, 0, yaw, 0, 0
    return None


def hover_motion(name, t):
    """Hovering: t runs through one idle loop. Bobbing, the head looking round, tail and fins swaying, and once
    a loop the attack (roar() of the Volcano): it rears up and lunges, jaw wide, shaking its head and
    thrashing its tail. DinoLifeController's HOVER copies this."""
    sin, cos = math.sin, math.cos
    r = roar(t)
    shake = sin(14 * t) * r
    if name == "Swim":
        return 0.02 * sin(2 * t) + 0.12 * r, 0.03 * sin(t) + 0.05 * shake, 0, 0.12 * sin(2 * t), 0.6 * r
    if name == "Head":
        return 0.06 * sin(3 * t) + 0.22 * r, 0, 0.15 * sin(t) + 0.05 * sin(3 * t) + 0.12 * shake, 0, 0
    if name.startswith("Neck"):
        i = int(name[4:])
        return 0.05 * sin(2 * t + i) + 0.1 * r, 0, 0.12 * sin(t - 0.3 * i), 0, 0
    if name.startswith("Tail"):
        i = int(name[4:])
        return 0, 0, (0.06 + 0.03 * i) * sin(4 * t - 0.75 * i) + 0.22 * sin(10 * t - i) * r, 0, 0
    if name in ("FinL", "FinR"):
        return 0, SIDE[name[-1]] * (0.1 * sin(4 * t) + 0.4 * r), 0, 0, 0
    if name.startswith("Flipper"):
        phase = 0 if name[7] == "F" else math.pi
        return 0.1 * cos(4 * t + phase), SIDE[name[-1]] * (0.18 * sin(4 * t + phase) - 0.45 * r), 0, 0, 0
    if name == "Jaw":
        return -0.04 * (0.5 + 0.5 * sin(4 * t)) - 0.7 * r, 0, 0, 0, 0
    if name == "Lure":
        return 0.1 * sin(3 * t) - 0.3 * r, 0, 0.25 * sin(t), 0, 0
    if name == "LureTip":
        return 0.15 * sin(3 * t - 1) - 0.25 * r, 0, 0, 0, 0
    if name.startswith("Tentacle"):
        n = int(name[8:].rstrip("b"))
        if name.endswith("b"):
            pitch, yaw = tentacle(name, 0.1 * sin(2 * t - 1) + 0.35 * r, 0.16 * sin(4 * t - 0.8 * n - 1) + 0.1 * shake)
        else:
            pitch, yaw = tentacle(name, 0.1 + 0.06 * sin(2 * t) + 0.5 * r, 0.14 * sin(4 * t - 0.8 * n))
        return pitch, 0, yaw, 0, 0
    return None


def pose_all(armature, frame, motion, phase):
    for bone in armature.pose.bones:
        values = motion(bone.name, phase)
        if values is None:
            continue
        pitch, roll, yaw, rise, surge = values
        kit.pose_bone(armature, bone.name, (pitch, roll, yaw), (0, surge, rise) if bone.name == "Swim" else None, frame)


def swim_pose(armature, f):
    pose_all(armature, f, swim_motion, math.tau * f / SWIM_FRAMES)


def hover_pose(armature, f):
    pose_all(armature, f, hover_motion, math.tau * f / kit.IDLE_FRAMES)


def animate(armature):
    swim = kit.add_action(armature, "Swim", SWIM_FRAMES, swim_pose, 2)
    idle = kit.add_action(armature, "Idle", kit.IDLE_FRAMES, hover_pose, 2)
    return swim, idle


def main():
    models = [spiral_gary(), derpichthys(), dunkleosteus(), plesiosaur(), megalodon(), mosasaurus()]
    build_and_render(models, RENDERS, HERE / "abyss_monsters.blend", "abyss_animation_preview.mp4", sky=SKY, ground=FLOOR,
                     glow_roles=GLOW_ROLES, spacing=18, animate_fn=animate, walk_frames=SWIM_FRAMES)


if __name__ == "__main__":
    main()
