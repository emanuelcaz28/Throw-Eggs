"""Builds Starfall Crater's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_starfall_crater_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_starfall_crater_monsters_7_8.py    (stills only)
    ONLY=moonwhale QUICK=1 ...                                                        (just that one)

Saves starfall_crater_monsters_7_8.blend and renders to design/world/monsters_starfall_crater_7_8/. The first six are in
build_starfall_crater_monsters.py; what this batch shares is in rare_kit.py.

The owner asked for 8 monsters a map (2026-11-06): two more each, nicer than the ones before, more aggressive map by map. But this
map's own rule stands (2026-11-04): nice to look at, not cute, not aggressive, above all in the face. So these two never so much as
frown, and what they do is the most dangerous thing so far. They don't attack. The sky does.

  Moonwhale   a whale as big as a hill swimming through the crater's air, midnight skin, moon-dust belly, craters and crystals on
              its back and a little moon of its own going round it. It breathes out a fountain of falling stars
  Constellion a great lion drawn in stars: a body of night sky with the lines of a constellation down its flanks, a moon-pale face
              and a mane like the sun. It lifts its head and sings, and meteors fall round it

The starfall face (build_starfall_crater_monsters.py) with real eyeballs: long half-shut eyes, dark as the sky, a star for an iris,
under a level lid; a quiet closed mouth with no teeth, and the night sky inside it.

What moves: the usual walk, idle and swim, and from rare_kit.py (SWAY in DinoLifeController): Spout1 to 6, Fall1 to 6, Orbit and Sway
bones.

Skin roles Body, Accent, Belly and Claw take the colour mutations; the stars and the face keep theirs. EyeGlow, StarGlow, CrystalGlow,
NebulaGlow, Sparkle, CometHead and CometTail glow (all already in shared/Roles.luau). Built at the first map's size. 1 Blender unit = 1
stud, models face +Y, feet on Z = 0.
"""
import math
import random
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402  (first: it turns the stud preview off)
from build_desert import beam  # noqa: E402
from build_forest import Model  # noqa: E402
from build_spore_hollow_monsters import egg  # noqa: E402
from build_starfall_crater import star_prism  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from rare_kit import cap, chain, curve, fine, jointed, leaf, lid, poly, ring_round, sabre, scallop, sheet, sweep, sweep_fine, swing  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_starfall_crater_7_8"
BLEND = "starfall_crater_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = {"EyeGlow", "StarGlow", "CrystalGlow", "NebulaGlow", "Sparkle", "CometHead", "CometTail"}

DUST, DUST_DARK = "#c3cbee", "#959fcc"
FACE = {"Pupil": "#10143a", "EyeGlow": "#ffe48a", "Mouth": "#141a42", "Sparkle": "#fff4cf", "StarLine": "#a9b4ea", "Dust": DUST, "DustDark": DUST_DARK, "Crystal": "#8ff0ff",
        "CrystalGlow": "#3fdcff", "StarGlow": "#ffe066", "Star": "#ffc93f", "StarDark": "#e09a2a", "NebulaGlow": "#ff58d6", "CometHead": "#fff4cf", "CometTail": "#8fdcff"}
SKY, FLOOR = "#141a40", "#303a72"
rare_kit.kit.NO_STUDS.update({"StarLine"})


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


def calm_eye(m, centre, r, look, side, lid_role="Body"):
    """Long, half shut, dark as the night: a star for an iris, and a level lid. A level lid reads calm, a slanted one angry."""
    forward = Vector(look).normalized()
    ring_round(m, lid_role, centre, r * 1.02, forward, r * 0.26, count=14, squash=0.74)  # a soft fold of skin round it
    egg(m, "Pupil", centre, r, r, r, 12, 7)
    cap(m, "EyeGlow", centre, r * 1.012, forward, 0.7, squash=(0.24, 1.0), rings=4, sides=10)
    cap(m, "EyeGlow", centre, r * 1.014, forward, 0.7, squash=(1.0, 0.24), rings=4, sides=10)
    cap(m, "EyeGlow", centre, r * 1.02, forward, 0.3, rings=2, sides=8)
    lid(m, lid_role, centre, r, forward, 0.46, 0.0, side)
    lid(m, lid_role, centre, r, forward, 0.2, 0.0, side, lower=True)


def star(m, at, size, role="Sparkle", tilt=(0, 0, 0)):
    star_prism(m, role, at, size, size * 0.34, size * 0.3, tilt, 4)


def drawn(m, points, sizes=None, line=0.14):
    """A constellation: thin lines joining stars."""
    for a, b in zip(points, points[1:]):
        beam(m, "StarLine", a, b, line, line, line * 0.8)
    for i, p in enumerate(points):
        star(m, p, (sizes or {}).get(i, 0.42), tilt=(math.pi / 2, 0, 0.5 * i) if False else (0, 0, math.pi / 2))


def thrown_star(m, name, n, at, size, role="StarGlow"):
    """A star on its own bone, parked out of sight in the body until it's thrown."""
    m.use(f"{name}{n}", at, "Root")
    star_prism(m, role, at, size, size * 0.36, size * 0.7, (0, 0, 0), 4)
    star_prism(m, role, at, size, size * 0.36, size * 0.7, (0, 0, math.pi / 2), 4)


def on_body(rings, y, angle, lift=0.04):
    for ((_, ya, za), wa, ha), ((_, yb, zb), wb, hb) in zip(rings, rings[1:]):
        if ya <= y <= yb:
            t = (y - ya) / (yb - ya)
            w, h, z = wa + (wb - wa) * t, ha + (hb - ha) * t, za + (zb - za) * t
            return (math.cos(angle) * (w / 2 + lift), y, z + math.sin(angle) * (h / 2 + lift))
    raise ValueError(y)


# ---------------------------------------------------------------------- Moonwhale


def moonwhale():
    """A whale of night sky, its own little moon going round it, a crater and crystals on its back."""
    m = monster("dino_Moonwhale", Body="#1f2a70", Accent="#141a4c", Belly=DUST, Claw=DUST_DARK)
    rng = random.Random(21)
    m.use("Swim", (0, 0, 9.4), "Root")

    # The body, front to back. Whales' heads are huge: a third of it.
    rings = [((0, -6.0, 9.2), 9.6, 9.0), ((0, -2.0, 9.5), 12.0, 11.2), ((0, 2.5, 9.7), 13.2, 12.2), ((0, 7.0, 9.6), 13.0, 11.8), ((0, 11.0, 9.3), 11.6, 10.4), ((0, 14.6, 8.9), 9.2, 8.2), ((0, 17.4, 8.5), 6.2, 5.4), ((0, 18.9, 8.2), 2.6, 2.4)]
    m.joint("Head", (0, 6.0, 9.3), "Swim")
    sweep_fine(m, "Body", rings, ["Swim", "Swim", "Swim", "Head", "Head", "Head", "Head", "Head"], sides=18, under="Belly", under_faces=7)

    # Throat grooves, running back from the jaw in long curves.
    for k in (-4, -3, -2, -1, 0, 1, 2, 3, 4):
        pts = [on_body(rings, y, -math.pi / 2 + 0.17 * k * (1 + 0.012 * (y - 2)), 0.05) for y in (-4.0, -1.0, 2.0, 5.0)]
        m.bone = "Swim"
        for p, q in zip(pts, pts[1:]):
            beam(m, "DustDark", p, q, 0.3, 0.2, 0.3)

    # The tail, tapering to flukes trailing light.
    path = [(p, w, w * 0.9) for p, w in zip(curve([(0, -5.6, 9.2), (0, -9.4, 9.6), (0, -13.2, 10.4), (0, -17.0, 11.6), (0, -20.2, 12.8), (0, -23.0, 13.8)], 11),
                                            (9.6, 9.2, 8.6, 7.8, 6.9, 5.9, 5.0, 4.1, 3.3, 2.5, 1.7))]
    bones = jointed(m, "Body", ["Tail1", "Tail2", "Tail3", "Tail4"], path, parent="Swim", sides=14, under="Belly", under_faces=5)
    tip = Vector(path[-1][0])
    m.bone = "Tail4"
    for s in (-1, 1):
        # A fluke: a swept curved blade, thick at the root, with a notch in the middle of the tail.
        rows = []
        for t in (0.0, 0.2, 0.42, 0.64, 0.84, 1.0):
            x = s * (0.2 + 11.0 * t)
            lead = 1.4 - 3.6 * t ** 1.6
            trail = -2.6 - 3.0 * math.sin(t * math.pi * 0.9) + 2.2 * t ** 3
            z = 0.2 + 2.6 * t ** 1.5
            rows.append([tuple(tip + Vector((x, lead, z))), tuple(tip + Vector((x, (lead + trail) / 2, z + 0.1))), tuple(tip + Vector((x, trail, z)))])
        sheet(m, "Body", rows, [["Tail4"] * 3] * 6, 0.5)
        for a0, b0 in zip(rows, rows[1:]):
            beam(m, "CrystalGlow", tuple(Vector(a0[2]) + Vector((0, 0, 0.26))), tuple(Vector(b0[2]) + Vector((0, 0, 0.26))), 0.2, 0.16, 0.12)
        # Streamers of light off each fluke.
        for n, x in ((1 if s < 0 else 2, 9.4), (3 if s < 0 else 4, 5.4)):
            start = tip + Vector((s * x, -5.0, 1.6))
            pts = curve([tuple(start), tuple(start + Vector((s * 0.6, -3.0, 0.2))), tuple(start + Vector((s * 0.2, -6.0, -0.4))), tuple(start + Vector((s * 0.8, -9.0, -0.8)))], 7)
            chain(m, "Sway", n, pts, 0.5, 0.08, parent="Tail4", role="CometTail")
            star(m, pts[-1], 0.6)
            m.bone = "Tail4"
    m.bone = "Swim"

    # Flippers, long and slow, patterned with stars.
    for side, letter in ((-1, "L"), (1, "R")):
        root = (side * 5.8, 6.2, 6.0)
        m.use(f"FlipperF{letter}", root)
        m.joint(f"FlipperF{letter}", root, "Swim")
        pts = curve([root, (side * 9.6, 4.8, 4.4), (side * 13.4, 2.4, 3.0), (side * 16.6, -0.8, 2.2)], 7)
        sweep_fine(m, "Body", [(p, w, w * 0.3) for p, w in zip(pts, (3.6, 5.0, 5.2, 4.8, 3.9, 2.6, 0.6))], sides=10, up=(0, 0, 1), under="Belly", under_faces=5, per=2)
        for p in pts[1:6:2]:
            star(m, tuple(Vector(p) + Vector((0, 0, 0.8))), 0.42)
    m.bone = "Swim"

    # A crater sunk in its back: a broken rim of moon rock, a dark floor, a star that fell in it, and crystals growing round it.
    cx, cy = 0.0, -0.8
    top = rings[1][0][2] + 5.3
    m.bone = "Swim"
    egg(m, "DustDark", (cx, cy, top - 0.1), 3.9, 4.4, 0.9, 12, 5)
    egg(m, "StarGlow", (cx, cy, top + 0.62), 1.0, 1.0, 0.5, 8, 4)
    for k in range(16):
        a = k * math.tau / 16
        r = rng.uniform(0.55, 1.05)
        at = (cx + math.cos(a) * 4.2, cy + math.sin(a) * 4.7, top + 0.05 + 0.1 * math.sin(3 * a) - 0.012 * (math.cos(a) * 4.2) ** 2)
        egg(m, "Dust" if k % 3 else "DustDark", at, r, r * 1.2, r * 0.8, 7, 4)
    for x, y, h, w in ((-5.0, 1.4, 3.8, 1.3), (-5.9, -0.2, 2.4, 0.9), (5.2, -3.4, 3.2, 1.2), (5.9, -1.8, 2.0, 0.8), (3.2, 3.8, 2.4, 0.9), (-2.8, -5.6, 2.0, 0.8)):
        z = top - 0.9 - 0.1 * abs(x)
        sweep(m, "Crystal", [((x, y, z), w * 0.8, w * 0.8), ((x * 1.08, y, z + h * 0.62), w, w)], sides=6)
        sweep(m, "CrystalGlow", [((x * 1.08, y, z + h * 0.62), w, w), ((x * 1.14, y, z + h), 0.03, 0.03)], sides=6)
    # A little galaxy turning on each flank: two arms of pink light round a bright heart.
    for side in (-1, 1):
        heart = Vector((side * 0.93, -0.05, 0.36))
        cap(m, "StarGlow", (0, -1.0, 9.6), (6.5, 7.8, 6.1), heart, 0.07, rings=2, sides=8)
        for arm in (0, math.pi):
            for k in range(1, 9):
                a = arm + 0.62 * k
                r = 0.042 * k
                d = heart + Vector((0, math.cos(a) * r * 1.4, math.sin(a) * r))
                cap(m, "NebulaGlow" if k % 3 else "Sparkle", (0, -1.0, 9.6), (6.5, 7.8, 6.1), d, 0.05 - 0.0035 * k, rings=1, sides=6)
    # A low fin far back along its spine.
    sabre(m, "Accent", [(0, -8.0, 14.0), (0, -9.6, 15.2), (0, -11.4, 15.6)], 3.0, 6, flat=0.3, power=1.1)
    # Stars all over its back, and a constellation down each side.
    for k in range(46):
        y = rng.uniform(-5.0, 16.0)
        a = rng.uniform(0.2, math.pi - 0.2)
        m.bone = "Head" if y > 6.5 else "Swim"
        egg(m, "Sparkle", on_body(rings, y, a, 0.02), 0.13, 0.13, 0.13, 5, 3)
    for side, a0 in ((0, 0.0), (1, math.pi)):
        pts = [on_body(rings, y, a0 + (1 if side == 0 else -1) * a, 0.06) for y, a in ((-4.6, 0.72), (-1.0, 0.98), (2.6, 0.62), (5.0, 0.86))]
        m.bone = "Swim"
        for p, q in zip(pts, pts[1:]):
            beam(m, "StarLine", p, q, 0.14, 0.14, 0.1)
        for p in pts:
            egg(m, "StarGlow", p, 0.26, 0.26, 0.26, 6, 3)
    m.bone = "Head"

    # The face: one calm dark eye each side, low by the corner of the mouth. No teeth. The mouth's a long quiet line.
    zm = 6.7
    for side in (-1, 1):
        # Set well forward, as no real whale's are: the reveal meets it head on, and it needs a face from the front.
        at = Vector((side * 3.7, 15.0, 10.0))
        calm_eye(m, tuple(at), 1.05, (side * 0.46, 0.88, 0.04), side, lid_role="Body")
        # The long line of its mouth, curving from the tip of its nose back and up under the eye.
        seam = [on_body(rings, y, (-0.35 if side > 0 else math.pi + 0.35) + (0.0 if side > 0 else 0), 0.06) for y in (8.4, 10.0, 11.6, 13.2, 14.8, 16.0, 17.2, 18.2)]
        for p0, q0 in zip(seam, seam[1:]):
            beam(m, "Accent", p0, q0, 0.34, 0.34, 0.24)
    # A star on its brow, and a trail of small ones running back from it: the mark of the crater's creatures.
    c0, n0, u0 = Vector((0, 16.45, 11.72)), Vector((0, 0.62, 0.78)), Vector((1, 0, 0))
    v0 = n0.cross(u0)
    poly(m, "StarGlow", [tuple(c0 + (u0 * math.cos(a) + v0 * math.sin(a)) * (1.6 if k % 2 == 0 else 0.5)) for k, a in enumerate(i * math.tau / 8 for i in range(8))], tuple(-n0 * 0.3))
    for k, (y, a0) in enumerate(((14.4, 1.57), (12.6, 1.5), (12.6, 1.64), (10.6, 1.4), (10.6, 1.74))):
        egg(m, "StarGlow", on_body(rings, y, a0, 0.04), 0.24 - 0.02 * k, 0.24 - 0.02 * k, 0.24 - 0.02 * k, 6, 3)
    m.use("Jaw", (0, 7.0, zm + 0.2), "Head")
    z = zm
    low = [((0, 7.0, z - 1.4), 11.0, 4.4), ((0, 11.0, z - 1.3), 10.0, 3.8), ((0, 15.0, z - 0.9), 7.2, 2.8), ((0, 17.8, z - 0.3), 3.8, 1.6), ((0, 18.8, z + 0.1), 1.2, 0.7)]
    sweep_fine(m, "Belly", low, sides=14)
    sweep(m, "Mouth", [((0, 7.4, z + 0.8), 9.6, 0.14), ((0, 15.2, z + 0.9), 6.0, 0.14), ((0, 18.0, z + 1.0), 2.2, 0.12)], sides=8)
    for k in range(12):  # the night sky inside it, seen when it sings
        y, x = rng.uniform(8.0, 16.0), rng.uniform(-3.0, 3.0)
        egg(m, "Sparkle", (x, y, z + 0.92), 0.14, 0.14, 0.08, 5, 3)
    for k in (-3, -2, -1, 0, 1, 2, 3):
        y0 = 16.8 - 0.2 * abs(k)
        beam(m, "DustDark", (k * 0.9, 9.0, z - 3.5 + 0.02 * k * k), (k * 0.6, y0, z - 1.1), 0.3, 0.2, 0.3)
    swing(m, ["Jaw"], (0, 7.0, zm + 0.2), -0.03)
    m.bone = "Head"

    # Its little moon, on an arm of nothing, going round it.
    m.use("Orbit", (0, 2.0, 11.6), "Swim")
    moon = Vector((21.0, 2.0, 15.0))
    egg(m, "Dust", tuple(moon), 2.6, 2.6, 2.6, 16, 10)
    ring_round(m, "CrystalGlow", tuple(moon), 3.7, (0.2, 0.1, 1), 0.18, count=20)
    for d, s in (((0.5, -0.6, 0.6), 0.34), ((-0.7, -0.1, 0.5), 0.26), ((0.1, 0.8, 0.5), 0.3), ((-0.2, -0.8, -0.5), 0.22)):
        cap(m, "DustDark", tuple(moon), 2.62, Vector(d), s, rings=2, sides=8)
    for a in (0.3, 1.5, 2.6):  # and the dust it trails
        egg(m, "Sparkle", tuple(moon + Vector((-3.5 - a, 0.8 * a, -0.2 * a))), 0.2, 0.2, 0.2, 5, 3)

    # The stars it breathes out, parked at its blowhole.
    for n, size in enumerate((2.0, 1.7, 1.5, 1.8, 1.5, 1.3), start=1):
        thrown_star(m, "Spout", n, (0, 13.0, 11.0), size, "StarGlow" if n % 2 else "Sparkle")
    m.bone = "Head"
    egg(m, "Mouth", (0, 13.4, 13.5), 0.8, 0.4, 0.26, 8, 3)  # the blowhole
    m.head_centre = (0, 14.0, 8.4)
    return m


# ---------------------------------------------------------------------- Constellion


def paw_leg(m, bone, x, y, top, thick, hind=False):
    """A big cat's leg: heavy at the top, an elbow or a hock, a slim wrist, a broad soft paw with its toes spread."""
    side = 1 if x > 0 else -1
    m.use(bone, (x, y, top))
    bend = ((0.9, top * 0.62), (-1.5, top * 0.34)) if hind else ((-0.9, top * 0.64), (0.5, top * 0.28))
    knee, ankle = (x + side * 0.3, y + bend[0][0], bend[0][1]), (x + side * 0.3, y + bend[1][0], bend[1][1])
    sweep_fine(m, "Body", [((x, y, top + 1.0), thick * 1.5, thick * 1.9), ((x + side * 0.1, y + bend[0][0] * 0.6, top * 0.82), thick * 1.45, thick * 1.8), (knee, thick * 1.0, thick * 1.2), (ankle, thick * 0.74, thick * 0.84), ((x + side * 0.3, y + 0.4, 1.7), thick * 0.8, thick * 0.86)], sides=10)
    sweep_fine(m, "Belly", [((x + side * 0.3, y + 0.4, 2.0), thick * 0.92, thick * 0.96), ((x + side * 0.3, y + 0.9, 1.0), thick * 1.3, thick * 1.5), ((x + side * 0.3, y + 1.8, 0.5), thick * 1.4, thick * 1.1)], sides=10, per=2)
    for dx in (-1.1, -0.38, 0.38, 1.1):  # toes
        egg(m, "Belly", (x + side * 0.3 + dx * thick * 0.42, y + 2.4 - 0.2 * abs(dx), 0.52), thick * 0.24, thick * 0.34, 0.5, 8, 4)
        egg(m, "DustDark", (x + side * 0.3 + dx * thick * 0.42, y + 2.8 - 0.2 * abs(dx), 0.36), thick * 0.1, thick * 0.14, 0.2, 6, 3)
    m.bone = "Spine"


def constellion():
    """A great lion of night sky and stars, with a moon-pale face and a mane like the sun."""
    m = monster("dino_Constellion", Body="#171d58", Accent="#0e1238", Belly=DUST, Claw=DUST_DARK)
    rng = random.Random(14)
    m.joint("Spine", (0, -4.2, 10.2))

    rings = [((0, -10.0, 10.6), 5.0, 5.4), ((0, -7.6, 10.5), 8.0, 8.4), ((0, -4.4, 10.7), 7.6, 7.6), ((0, -1.0, 11.0), 7.2, 7.2), ((0, 2.2, 10.9), 9.0, 10.0), ((0, 5.0, 11.2), 9.4, 10.8), ((0, 7.0, 11.8), 8.0, 9.0)]
    sweep_fine(m, "Body", rings, sides=16)
    for s2 in (-1, 1):  # shoulders and haunches
        egg(m, "Body", (s2 * 3.5, 3.8, 11.0), 2.3, 4.2, 5.0, 12, 7)
        egg(m, "Body", (s2 * 3.5, -7.4, 10.7), 2.4, 4.4, 4.8, 12, 7)

    paw_leg(m, "FrontL", -3.9, 4.2, 9.0, 2.5)
    paw_leg(m, "FrontR", 3.9, 4.2, 9.0, 2.5)
    paw_leg(m, "BackL", -3.7, -7.6, 9.2, 2.7, hind=True)
    paw_leg(m, "BackR", 3.7, -7.6, 9.2, 2.7, hind=True)

    # The lines of the constellation down its flanks, a star at each turn, and small stars scattered all over.
    for s in (-1, 1):
        for route in ([(5.4, 0.85), (2.6, 0.5), (-0.6, 0.9), (-3.6, 0.5), (-6.6, 0.95), (-9.4, 0.5)], [(2.6, 0.5), (1.4, -0.2)], [(-3.6, 0.5), (-4.8, -0.2)]):
            pts = []
            for y, a in route:
                p = on_body(rings, y, a, 0.08)
                pts.append((s * p[0], p[1], p[2]))
            for p, q in zip(pts, pts[1:]):
                beam(m, "StarLine", p, q, 0.16, 0.16, 0.1)
            for p in pts:
                star_prism(m, "StarGlow", p, 0.6, 0.2, 0.16, (0, 0, math.pi / 2), 4)
    for k in range(40):
        y = rng.uniform(-9.6, 6.6)
        a = rng.uniform(-0.3, math.pi + 0.3)
        egg(m, "Sparkle", on_body(rings, y, a, 0.02), 0.12, 0.12, 0.12, 5, 3)

    # The tail, up and over, its tuft a little comet.
    path = [(p, w, w) for p, w in zip(curve([(0, -10.0, 12.0), (0, -13.2, 11.0), (0, -16.0, 10.8), (0, -18.4, 12.4), (0, -19.6, 14.6)], 17), [2.2 - 0.08 * i for i in range(17)])]
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], path)
    m.bone = "Tail3"
    tip = Vector(path[-1][0])
    egg(m, "CometHead", tuple(tip + Vector((0, 0, 0.6))), 1.1, 1.1, 1.3, 8, 5)
    for k, (dx, dy) in enumerate(((0, -1.8), (1.2, -1.2), (-1.2, -1.2))):
        sabre(m, "CometTail", [tuple(tip + Vector((0, 0, 0.8))), tuple(tip + Vector((dx * 0.8, dy * 0.8, 1.6))), tuple(tip + Vector((dx * 1.7, dy * 2.0, 1.5)))], 0.9, 5)
    m.bone = "Spine"

    # The neck, carried high, and the head.
    m.joint("Neck", (0, 6.4, 13.0), "Spine")
    m.bone = "Neck"
    sweep(m, "Body", [((0, 5.6, 12.2), 8.4, 9.2), ((0, 7.8, 14.0), 7.4, 7.8), ((0, 9.4, 15.4), 6.6, 6.6)], ["Spine", "Neck", "Neck"], sides=10)

    m.use("Head", (0, 9.0, 15.4), "Neck")
    # The mane: rays of the sun framing the face and swept back down the neck, longest behind, burning brightest at the front.
    hc = Vector((0, 9.6, 16.0))
    for tier, (radius, length, count, role, back, wide, sweep_back) in enumerate(((3.9, 9.8, 19, "StarDark", -3.4, 2.4, 6.0), (3.7, 7.4, 19, "Star", -1.8, 2.2, 4.2), (3.5, 5.0, 19, "StarGlow", -0.2, 2.0, 2.4), (3.2, 2.8, 23, "StarGlow", 1.7, 1.5, 2.2))):
        for k in range(count):
            a = (k + 0.5 * (tier % 2)) * math.tau / count + 0.05
            out = Vector((math.cos(a), 0, math.sin(a) * 0.96))
            base = hc + out * radius + Vector((0, back, 0))
            grow = rng.uniform(0.74, 1.14)
            tip = base + out * length * grow + Vector((0, -sweep_back * grow, 0))
            # A curved ray, bending as a flame does.
            bow = Vector((-out.z, 0, out.x)) * length * 0.13 * (1 if k % 2 else -1)
            sabre(m, role, [tuple(base - out * 0.6), tuple(base.lerp(tip, 0.55) + bow), tuple(tip + bow * 0.3)], wide, 5, flat=0.62, sides=5, power=1.1)
    # Crystals standing in the outer mane.
    for a in (0.42, 1.02, 1.57, 2.12, 2.72):
        out = Vector((math.cos(a), 0, math.sin(a)))
        base = hc + out * 11.4 + Vector((0, -7.6, 0))
        tip = base + out * 3.4 + Vector((0, -1.4, 0))
        sweep(m, "Crystal", [(tuple(base), 0.9, 0.9), (tuple(base.lerp(tip, 0.6)), 1.15, 1.15)], sides=6, up=(0, 1, 0))
        sweep(m, "CrystalGlow", [(tuple(base.lerp(tip, 0.6)), 1.15, 1.15), (tuple(tip), 0.03, 0.03)], sides=6, up=(0, 1, 0))

    # The face: a dark head of night sky, level eyes looking straight at you, a broad square muzzle pale as the moon.
    sweep_fine(m, "Body", [((0, 8.6, 16.2), 6.4, 6.0), ((0, 10.4, 16.4), 7.0, 6.2), ((0, 11.8, 16.4), 6.4, 5.4), ((0, 12.7, 16.3), 5.0, 4.0)], sides=14, per=2)
    for s2 in (-1, 1):  # the muzzle: two soft pads either side of the nose, over a square chin
        egg(m, "Belly", (s2 * 1.1, 13.6, 14.55), 1.35, 1.35, 1.1, 12, 7)
        egg(m, "Body", (s2 * 3.0, 11.6, 15.0), 1.4, 1.8, 1.9, 10, 6)  # cheekbones
    egg(m, "Belly", (0, 12.7, 14.9), 1.9, 1.8, 1.3, 10, 6)
    sweep_fine(m, "Body", [((0, 12.4, 17.6), 2.2, 1.0), ((0, 13.4, 16.6), 2.0, 1.0), ((0, 14.4, 15.9), 1.8, 0.9)], sides=8, per=2)  # the bridge of the nose
    poly(m, "Accent", [(-1.2, 14.6, 16.1), (1.2, 14.6, 16.1), (0.45, 15.2, 15.3), (-0.45, 15.2, 15.3)], (0, -0.6, 0))  # the nose
    beam(m, "Accent", (0, 15.1, 15.3), (0, 15.0, 14.3), 0.2, 0.2, 0.14)
    for side in (-1, 1):  # a quiet mouth: one level line
        beam(m, "Accent", (0, 15.0, 14.3), (side * 1.6, 14.35, 14.0), 0.2, 0.16, 0.14)
        beam(m, "Accent", (side * 1.6, 14.35, 14.0), (side * 2.5, 13.2, 14.25), 0.16, 0.12, 0.1)
        for k in range(3):  # whisker spots
            egg(m, "DustDark", (side * (0.8 + 0.45 * k), 14.8 - 0.32 * k, 14.85), 0.1, 0.1, 0.1, 5, 3)
    star_prism(m, "StarGlow", (0, 12.1, 19.0), 1.0, 0.34, 0.2, (math.pi / 2 - 0.5, 0, 0), 4)  # a star on its brow
    for side in (-1, 1):
        at = (side * 1.95, 12.5, 16.85)
        calm_eye(m, at, 0.72, (side * 0.26, 0.96, -0.05), side, lid_role="Accent")
        beam(m, "Accent", (side * 3.3, 12.2, 17.7), (side * 0.9, 13.0, 17.7), 0.4, 0.34, 0.26)  # a level brow
    zm = 13.0
    egg(m, "Mouth", (0, 11.4, zm + 0.1), 2.2, 2.4, 0.8, 8, 4)
    m.use("Jaw", (0, 10.4, zm + 0.1), "Head")
    sweep_fine(m, "Belly", [((0, 10.6, zm - 0.1), 3.6, 1.8), ((0, 12.6, zm - 0.1), 3.2, 1.9), ((0, 14.0, zm), 2.0, 1.2)], sides=10, per=2)
    sweep(m, "Mouth", [((0, 10.8, zm + 0.68), 3.6, 0.12), ((0, 13.8, zm + 0.6), 1.8, 0.1)], sides=6)
    for k in range(7):
        egg(m, "Sparkle", (rng.uniform(-1.2, 1.2), rng.uniform(11.0, 13.4), zm + 0.72), 0.1, 0.1, 0.06, 5, 3)
    m.bone = "Head"

    # The meteors it calls down, parked in its chest.
    for n, size in enumerate((1.5, 1.2, 1.4, 1.1, 1.3, 1.0), start=1):
        at = (0, 2.0, 9.0)
        m.use(f"Fall{n}", at, "Root")
        d = Vector(rare_kit.METEOR).normalized()
        x, y, z = at
        c = Vector(at)
        sweep(m, "CometTail", [(tuple(c - d * size * 3.6), 0.06, 0.06), (tuple(c - d * size * 1.6), size * 0.9, size * 0.9), (tuple(c), size * 1.6, size * 1.6)], sides=6, up=(1, 0, 0))
        egg(m, "CometHead", at, size * 1.05, size * 1.05, size * 1.05, 6, 4)
    m.bone = "Head"
    m.head_centre = (0, 13.0, 15.6)
    return m


ALL = [moonwhale, constellion]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "starfall_crater_7_8", SKY, FLOOR, GLOW_ROLES, glow=1.0, spacing=56)


if __name__ == "__main__":
    main()
