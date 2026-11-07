"""Builds The Abyss's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_abyss_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_abyss_monsters_7_8.py    (stills only)
    ONLY=kraken QUICK=1 ...                                                 (just that one)

Saves abyss_monsters_7_8.blend and renders to design/world/monsters_abyss_7_8/. The first six are in build_abyss_monsters.py;
what this batch shares is in rare_kit.py.

The owner asked for 8 monsters a map (2026-11-06): two more each, nicer than the ones before, more aggressive map by map, and for
The Abyss, monsters that are actually nice and very aggressive. Shadow Bog's pair grab what's in front of them. These two hit
you from across the base.

  Shrimpact  a mantis shrimp, the fastest punch in the sea, in neon plates. Two club fists folded under its chin, cocked like
             hammers: they snap out one after the other so fast the water cracks, and a ring of shock flies off each
  Kraken     the thing the sailors drew: a huge dark mantle ringed with glowing spots, a ring of eight hooked arms round a beak,
             and two long hunting arms held up over its head like cobras. They shoot out straight, then drag what they hit home

They swim like The Abyss's other monsters (a Swim bone). What moves: their swim and hover, and from rare_kit.py (SWAY in
DinoLifeController): PunchL, PunchR, ClubL, ClubR, Shock1 and 2 and Bubble1 to 4 (the punch), Seize L and R 1 to 5 (the arms) and Sway
and Wriggle bones.

Skin roles Body, Accent, Belly and Claw take the colour mutations; the face keeps its colours. EyeGlow, Glow and Shine glow (all
already in shared/Roles.luau). Built at the first map's size. 1 Blender unit = 1 stud, models face +Y, ground at Z = 0.
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
from build_thorn_kingdom_monsters import point  # noqa: E402
from rare_kit import cap, chain, curve, fine, frames_along, jointed, leaf, lid, poly, ring_round, sabre, sheet, slit_eye, sweep, sweep_fine, swing  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_abyss_7_8"
BLEND = "abyss_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = {"EyeGlow", "Glow", "Shine"}

FACE = {"EyeGlow": "#3ff2ff", "Pupil": "#03121a", "Highlight": "#ffffff", "Mouth": "#14060a", "Tongue": "#a3213b", "Teeth": "#f4f0e4", "Socket": "#050b12",
        "Glow": "#5cf4ff", "Shine": "#ff62d6"}
SKY, FLOOR = "#2f6fa8", "#3b78a0"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- Shrimpact


def shock_ring(m, n, at, radius, parent="Root"):
    """A ring of cracked water on its own bone, parked out of sight inside the body, flat to the front."""
    m.use(f"Shock{n}", at, parent)
    pts = [tuple(Vector(at) + Vector((math.cos(a) * radius, 0, math.sin(a) * radius))) for a in (i * math.tau / 14 for i in range(15))]
    sweep(m, "Shine", [(p, 0.5, 0.5) for p in pts], sides=5, caps=(False, False), up=(0, 1, 0))


def shrimp_eye(m, base, top, side):
    """A mantis shrimp's eye on its stalk: a tall bright ball split by a band, a burning iris and a thin slit under a hard lid."""
    sweep_fine(m, "Stalk", [(tuple(base), 1.3, 1.3), (tuple(base.lerp(top, 0.55)), 0.82, 0.82), (tuple(top), 1.05, 1.05)], sides=8, per=2)
    c = top + Vector((0, 0.1, 0.55))
    egg(m, "EyeShell", tuple(c), 0.98, 0.98, 1.2, 12, 7)
    look = Vector((side * 0.28, 0.95, -0.1))
    cap(m, "EyeGlow", tuple(c), (1.0, 1.0, 1.22), look, 0.72, squash=(0.9, 1.0), rings=4, sides=12)
    cap(m, "Pupil", tuple(c), (1.02, 1.02, 1.24), look, 0.6, squash=(0.2, 1.0), rings=5, sides=12)
    ring_round(m, "Claw", tuple(c), 0.99, (0, 0, 1), 0.2, count=14)  # the band round its middle
    lid(m, "Accent", tuple(c), 1.16, look, 0.56, 0.8, side)


def punch_arm(m, letter, side):
    """A folded arm: forward to the elbow, then back on itself to a club like a boulder."""
    shoulder = Vector((side * 2.5, 8.6, 5.6))
    elbow = Vector((side * 3.1, 12.6, 3.9))
    wrist = Vector((side * 3.3, 9.6, 2.9))
    m.use(f"Punch{letter}", tuple(shoulder), "Head")
    sweep_fine(m, "Accent", [(tuple(shoulder), 1.7, 1.9), (tuple(shoulder.lerp(elbow, 0.5)), 2.1, 2.5), (tuple(elbow), 1.7, 1.9)], sides=10)
    for t in (0.3, 0.55, 0.8):  # plates down the arm
        ring_round(m, "Claw", tuple(shoulder.lerp(elbow, t)), 1.04 - 0.1 * abs(t - 0.5), elbow - shoulder, 0.26, count=10)
    m.use(f"Club{letter}", tuple(elbow), f"Punch{letter}")
    sweep_fine(m, "Belly", [(tuple(elbow), 1.6, 1.8), (tuple(elbow.lerp(wrist, 0.55)), 2.0, 2.2), (tuple(wrist), 2.5, 2.6)], sides=10)
    hit = wrist + Vector((0, -0.8, 0))
    egg(m, "Claw", tuple(hit), 2.0, 2.1, 2.0, 12, 7)
    ring_round(m, "Accent", tuple(hit), 2.02, (0, 1, 0), 0.34, count=14)
    for a, b in (((0.0, -2.4, 0.0), (0.0, -3.6, 0.0)), ((-1.2, -1.8, 0.8), (-2.0, -2.5, 1.4)), ((1.2, -1.8, 0.8), (2.0, -2.5, 1.4)), ((-1.2, -1.8, -0.8), (-2.0, -2.5, -1.4)), ((1.2, -1.8, -0.8), (2.0, -2.5, -1.4))):
        point(m, "Teeth", tuple(wrist + Vector(a)), tuple(wrist + Vector(b)), 0.9)
    m.bone = "Head"


def shrimpact():
    """A neon mantis shrimp, its club fists cocked under its chin."""
    m = monster("dino_Shrimpact", Body="#17a58b", Accent="#e8432c", Belly="#2d5bd8", Claw="#ffd83a", Fan="#ff8a2a", Stalk="#c9e04a", Slit="#03121a", EyeShell="#ff5a8a")
    m.use("Swim", (0, 2.0, 7.4), "Root")

    # The shell: a big armoured back over the front half, then plates down a tail that curls under.
    route = [(0, 8.6, 7.1), (0, 5.8, 7.8), (0, 3.0, 8.0), (0, 0.2, 7.9), (0, -3.0, 7.5), (0, -6.2, 6.8), (0, -9.2, 5.8), (0, -11.9, 4.7), (0, -14.2, 3.7), (0, -16.0, 3.0)]
    widths = (6.0, 7.4, 8.0, 8.2, 7.8, 7.2, 6.5, 5.6, 4.6, 3.4)
    owner = ["Head", "Swim", "Swim", "Swim", "Tail1", "Tail1", "Tail2", "Tail3", "Tail4", "Tail4"]
    m.joint("Tail1", route[3], "Swim")
    m.joint("Tail2", route[5], "Tail1")
    m.joint("Tail3", route[6], "Tail2")
    m.joint("Tail4", route[7], "Tail3")
    frames = frames_along(route, (0, 0, 1))
    m.joint("Head", (0, 7.0, 7.1), "Swim")
    sweep(m, "Claw", [(p, w * 0.8, w * 0.56) for p, w in zip(route, widths)], owner, sides=8)  # under the shell, showing in the gaps
    for i in range(len(route) - 1):
        a, b = Vector(route[i]), Vector(route[i + 1])
        ahead, side, normal = frames[i]
        back = (b - a).normalized()
        w, h = widths[i], widths[i] * 0.74
        gap = (b - a).length * 0.06
        m.bone = owner[i]
        mid = (a + b) / 2
        sweep_fine(m, "Body", [(tuple(a + back * gap), w * 0.86, h * 0.84), (tuple(mid), w * 1.02, h * 1.04), (tuple(b - back * gap * 2.4), w * 1.06, h * 1.08), (tuple(b - back * gap), w * 0.84, h * 0.82)],
                   per=2, sides=14, up=tuple(normal), under="Belly", under_faces=5)
        for s2 in (-1, 1):  # a dark stripe either side of its spine, bright down the middle of each plate
            d = mid + normal * h * 0.47 + side * s2 * w * 0.2
            poly(m, "Accent", [tuple(d - back * 0.7 + normal * 0.06), tuple(d + side * s2 * 0.5 - normal * 0.1), tuple(d + back * 0.7 + normal * 0.06), tuple(d - side * s2 * 0.5 + normal * 0.1)], tuple(-normal * 0.16))
        rim = b - back * (gap * 3.2)
        sweep(m, "Accent", [(tuple(rim - back * 0.14), w * 1.09, h * 1.12), (tuple(rim + back * 0.16), w * 1.1, h * 1.13)], sides=14, up=tuple(normal))
        top = mid + normal * h * 0.5
        point(m, "Claw", tuple(top - normal * 0.2), tuple(top + normal * (1.0 if i % 2 else 1.5) + back * 0.8), 0.9)
        for s in (-1, 1):  # glowing spots down each side, and a spike on each plate's edge
            spot = mid + side * s * w * 0.47 + normal * h * 0.18
            egg(m, "Glow", tuple(spot), 0.3, 0.42, 0.3, 6, 3)
            edge = b - back * gap * 3 + side * s * w * 0.52 - normal * h * 0.12
            point(m, "Accent", tuple(edge), tuple(edge + side * s * 0.8 + back * 0.5 - normal * 0.4), 0.7)

    # Paddles under the tail, each pair a beat after the next.
    for n, (i, t) in enumerate(((4, 0.2), (4, 0.8), (5, 0.5), (6, 0.2), (6, 0.8)), start=3):
        p = Vector(route[i]).lerp(Vector(route[i + 1]), t)
        name = f"Wriggle{n}a"
        m.joint(name, tuple(p), owner[i])
        m.bone = name
        for s in (-1, 1):
            base = p + Vector((s * 1.6, 0, -1.6))
            leaf(m, "Fan", tuple(base), tuple(base + Vector((s * 1.2, -1.2, -2.8))), (0, 1, 0), 1.9, 0.16)

    # Three pairs of thin walking legs under its chest, curled up as it swims.
    for n, y in ((1, 6.2), (2, 3.8), (8, 1.4)):
        m.joint(f"Wriggle{n}a", (0, y, 5.0), "Swim")
        m.bone = f"Wriggle{n}a"
        for s2 in (-1, 1):
            hip, knee, foot = Vector((s2 * 2.4, y, 4.8)), Vector((s2 * 5.2, y + 0.5, 3.6)), Vector((s2 * 5.4, y + 1.6, 1.1))
            sweep_fine(m, "Accent", [(tuple(hip), 0.9, 0.9), (tuple(knee), 0.8, 0.8), (tuple(knee.lerp(foot, 0.6)), 0.5, 0.5)], sides=6, per=2)
            sabre(m, "Claw", [tuple(knee.lerp(foot, 0.55)), tuple(foot), tuple(foot + Vector((-s2 * 0.5, 0.7, -0.2)))], 0.46, 4)

    # The tail fan: a spread of blades on the Fin bones and a spined middle.
    end = Vector(route[-1])
    m.bone = "Tail4"
    sweep(m, "Accent", [(tuple(end + Vector((0, 0.2, 0))), 3.0, 1.4), (tuple(end + Vector((0, -3.2, -0.5))), 0.6, 0.4)], sides=6)
    for s, letter in ((-1, "L"), (1, "R")):
        m.use(f"Fin{letter}", tuple(end + Vector((s * 1.1, 0, 0))), "Tail4")
        for k, (dx, dy) in enumerate(((1.2, -3.9), (3.1, -3.3), (4.3, -1.9))):
            base = end + Vector((s * 1.1, 0, 0))
            leaf(m, "Fan" if k % 2 else "Accent", tuple(base), tuple(base + Vector((s * dx, dy, -0.6))), (dy, -s * dx, 0), 2.1, 0.2)
            beam(m, "Glow", tuple(base), tuple(base + Vector((s * dx, dy, -0.5)) * 0.8), 0.14, 0.14, 0.08)
    m.bone = "Swim"

    # The head: a low armoured wedge, a spike of a nose, and a mouth that's most of its front.
    m.bone = "Head"
    zm = 5.6
    sweep_fine(m, "Body", [((0, 7.2, 7.0), 6.0, 4.2), ((0, 9.2, 6.9), 6.2, 3.4), ((0, 11.0, 6.65), 5.0, 2.4), ((0, 12.2, 6.45), 3.2, 1.5)], sides=12)
    # A shield over its head, ending in a blade of a nose.
    sweep_fine(m, "Accent", [((0, 8.0, 8.5), 4.6, 0.7), ((0, 10.2, 7.9), 3.6, 0.6), ((0, 12.4, 7.2), 1.8, 0.5), ((0, 14.6, 7.1), 0.5, 0.3)], sides=8, per=2)
    for s2 in (-1, 1):
        sabre(m, "Claw", [(s2 * 2.5, 8.2, 8.3), (s2 * 1.6, 10.2, 7.95), (s2 * 0.5, 12.4, 7.42)], 0.5, 6, flat=1.2)  # hard lines down it to the nose
    # Eyes on short stalks: the mantis shrimp's, but slit and burning.
    for side in (-1, 1):
        base = Vector((side * 1.5, 11.0, 7.3))
        shrimp_eye(m, base, base + Vector((side * 1.1, 0.5, 1.9)), side)
        # The paddles beside its mouth, out of the way of its face.
        p0 = Vector((side * 2.5, 10.2, 6.2))
        leaf(m, "Fan", tuple(p0), tuple(p0 + Vector((side * 5.0, 2.4, 0.8))), (0, 0.4, 1), 2.0, 0.2)
        beam(m, "Glow", tuple(p0 + Vector((side * 0.8, 0.3, 0.26))), tuple(p0 + Vector((side * 4.0, 1.9, 0.86))), 0.16, 0.16, 0.08)
    # Feelers.
    for n, side in ((1, -1), (2, 1)):
        pts = curve([(side * 1.3, 12.0, 6.8), (side * 3.2, 15.4, 8.4), (side * 6.2, 16.2, 10.8), (side * 9.6, 13.6, 12.0), (side * 12.0, 9.4, 11.6)], 9)
        chain(m, "Sway", n, pts, 0.42, 0.1, parent="Head", role="Accent")
    m.bone = "Head"
    sweep(m, "Mouth", [((0, 7.4, zm + 0.04), 5.0, 0.2), ((0, 11.2, zm + 0.1), 3.6, 0.16), ((0, 12.1, zm + 0.2), 1.8, 0.12)], sides=8)
    egg(m, "Mouth", (0, 7.8, zm - 1.0), 2.0, 0.6, 1.4, 8, 5)
    for side in (-1, 1):
        for k in range(8):
            t = k / 7
            y, x = 8.0 + 4.2 * t, side * (2.3 - 1.4 * t * t)
            point(m, "Teeth", (x, y, zm + 0.16 + 0.12 * t), (x, y + 0.04, zm - 0.6 - 0.3 * (k % 2) + 0.1 * t), 0.36)
    m.use("Jaw", (0, 7.4, zm - 0.02), "Head")
    z = zm - 0.46
    sweep(m, "Belly", [((0, 7.4, z), 4.8, 0.9), ((0, 10.4, z), 3.8, 0.8), ((0, 12.0, z + 0.1), 2.0, 0.6)], sides=8)
    sweep(m, "Mouth", [((0, 7.6, z + 0.42), 3.8, 0.1), ((0, 11.8, z + 0.36), 1.5, 0.1)], sides=8)
    for side in (-1, 1):
        for k in range(7):
            t = k / 6
            y, x = 8.0 + 3.7 * t, side * (1.9 - 1.1 * t * t)
            point(m, "Teeth", (x, y, z + 0.36), (x, y + 0.03, z + 0.92 + 0.2 * (k % 2)), 0.32)
    swing(m, ["Jaw"], (0, 7.4, zm - 0.02), -0.5)

    punch_arm(m, "L", -1)
    punch_arm(m, "R", 1)

    # Cracks in the water and bubbles, parked in its body until it hits.
    parked = (0, 3.0, 7.6)
    for n in (1, 2):
        shock_ring(m, n, parked, 2.5)
    for n, size in ((1, 0.9), (2, 0.7), (3, 0.8), (4, 0.6)):
        m.use(f"Bubble{n}", parked, "Root")
        egg(m, "Glow", parked, size, size, size, 6, 4)
    m.bone = "Head"
    m.head_centre = (0, 11.0, 7.0)
    return m


# ---------------------------------------------------------------------- Kraken


SEIZE_PATH = [(0, 4.2, 8.6), (0, 4.8, 12.6), (0, 7.2, 15.9), (0, 11.0, 17.2), (0, 14.6, 15.8), (0, 16.2, 12.6)]


def hunting_arm(m, letter, side):
    """A long arm held up over the head, on five bones, ending in a hooked club. It unrolls straight when it strikes."""
    pts = [Vector(p) + Vector((side * 5.0, 0, 0)) for p in SEIZE_PATH]
    names = [f"Seize{letter}{k}" for k in range(1, 6)]
    for k, name in enumerate(names):
        m.joint(name, tuple(pts[k]), "Head" if k == 0 else names[k - 1])
    rings = curve([tuple(p) for p in pts], 26)
    bones = [names[min(int(i / 25 * 5), 4)] for i in range(26)]
    path = [(p, 2.1 - 0.05 * i, 2.1 - 0.05 * i) for i, p in enumerate(rings)]
    sweep(m, "Body", path, bones, sides=10, up=(1, 0, 0), under="Belly", under_faces=3)
    # Suckers along the inside, each a pink pad in a pale rim.
    for i in range(1, 25, 2):
        p = Vector(rings[i])
        m.bone = bones[i]
        along = (Vector(rings[i + 1]) - p).normalized()
        inside = along.cross(Vector((1, 0, 0))).normalized()
        egg(m, "Claw", tuple(p + inside * (0.9 - 0.02 * i)), 0.4, 0.4, 0.4, 6, 3)
        egg(m, "Shine", tuple(p + inside * (1.04 - 0.02 * i)), 0.27, 0.27, 0.27, 6, 3)
    # The club: a broad leaf, rimmed with hooks.
    tip = pts[-1]
    m.bone = names[-1]
    sweep_fine(m, "Body", [(tuple(tip + Vector((0, 0.2, 0.8))), 1.0, 1.0), (tuple(tip + Vector((0, 0.2, -1.2))), 3.4, 2.4), (tuple(tip + Vector((0, 0.1, -3.4))), 2.8, 2.0), (tuple(tip + Vector((0, 0, -5.4))), 0.3, 0.3)], sides=10, up=(1, 0, 0))
    for k, (dz, reach) in enumerate(((-0.8, 1.7), (-1.9, 2.0), (-3.0, 1.6))):
        for dx in (-1.1, 0, 1.1):
            base = tip + Vector((dx, 0.8, dz))
            sabre(m, "Claw", [tuple(base), tuple(base + Vector((0, reach * 0.7, 0.1))), tuple(base + Vector((0, reach, -0.7)))], 0.46, 5)
    egg(m, "Glow", tuple(tip + Vector((0, -1.15, -1.8))), 0.9, 0.5, 1.4, 8, 5)
    m.bone = "Head"


def kraken():
    """A huge dark squid: mantle, a ring of arms round its beak, and two long hunting arms."""
    m = monster("dino_Kraken", Body="#17304e", Accent="#0b1a2c", Belly="#8a2240", Claw="#efe2c6", Beak="#14100f", Slit="#03121a")
    m.use("Swim", (0, -1.0, 8.4), "Root")

    # The mantle, back and up from the head, on the tail bones so it sways: a long smooth torpedo.
    route = curve([(0, -0.5, 8.6), (0, -4.0, 10.2), (0, -8.2, 12.6), (0, -12.4, 15.0), (0, -16.4, 17.2), (0, -19.6, 19.0)], 10)
    widths = (8.8, 10.6, 12.0, 12.6, 12.4, 11.4, 9.8, 7.6, 4.8, 0.8)
    mantle = [(p, w, w * 0.96) for p, w in zip(route, widths)]
    bones = ["Swim"] + [("Tail1", "Tail2", "Tail3")[min((i - 1) * 3 // 9, 2)] for i in range(1, 10)]
    for k, name in enumerate(("Tail1", "Tail2", "Tail3")):
        m.joint(name, mantle[bones.index(name) - 1][0], "Swim" if k == 0 else ("Tail1", "Tail2")[k - 1])
    fine_rings, fine_bones = fine(mantle, bones, 3)
    sweep(m, "Body", fine_rings, fine_bones, sides=16, under="Accent", under_faces=5)

    # Dark bands round it, broken into patches like a squid's skin, and rings of light between them.
    for i, (p, w, _) in enumerate(mantle[1:-1], start=1):
        m.bone = bones[i]
        centre, radii = Vector(p), (w * 0.5, 2.0, w * 0.48)
        for k in range(9):
            a = 0.1 + k * 0.37 + (0.18 if i % 2 else 0)
            spot = Vector((math.cos(a), 0.0, math.sin(a)))
            if (k + i) % 2:
                cap(m, "Accent", tuple(centre), (w * 0.505, 2.1, w * 0.485), spot, 0.3, squash=(0.8, 1.0), rings=2, sides=8)
            else:
                cap(m, "Glow", tuple(centre), (w * 0.51, 2.1, w * 0.49), spot, 0.12, rings=2, sides=6)
        if i % 2:  # a low keel of spines, and a scar of pink glow down each flank
            top = centre + Vector((0, 0, w * 0.47))
            sabre(m, "Accent", [tuple(top), tuple(top + Vector((0, -0.8, 1.0))), tuple(top + Vector((0, -2.0, 1.5)))], 1.5, 5, flat=0.5)
        if i in (3, 4, 5):
            for s2 in (-1, 1):
                a0 = centre + Vector((s2 * w * 0.5, 0, -w * 0.05))
                beam(m, "Shine", tuple(a0), tuple(a0 + Vector((0, -1.8, 0.6))), 0.2, 0.2, 0.12)

    # A rounded fin down each side of the mantle's tip, on the Fin bones, ribbed with light.
    for side, letter in ((-1, "L"), (1, "R")):
        root = Vector(mantle[6][0])
        m.use(f"Fin{letter}", tuple(root), "Tail2")
        rows = []
        for t in (0.0, 0.25, 0.5, 0.75, 0.92, 1.0):
            reach = side * (3.4 + 11.0 * math.sin(t * math.pi / 2))
            chord = 1 - t ** 2.6
            rows.append([tuple(root + Vector((reach, 5.0 * chord - 1.4 * t, -1.4 + 2.6 * t))), tuple(root + Vector((reach, -0.6 * chord - 1.2 * t, -0.1 + 1.6 * t))), tuple(root + Vector((reach, -7.0 * chord - 1.0 * t, 3.2 - 0.6 * t)))])
        sheet(m, "Accent", rows, [[f"Fin{letter}"] * 3] * len(rows), 0.3)
        for k in (0.0, 0.5, 1.0):
            a0 = Vector(rows[0][1]) + Vector((0, 3.0 * (0.5 - k), 0.2))
            b0 = Vector(rows[-2][0]).lerp(Vector(rows[-2][2]), k) + Vector((0, 0, 0.2))
            beam(m, "Glow", tuple(a0), tuple(b0), 0.22, 0.22, 0.12)
    m.bone = "Swim"

    # A collar where the mantle meets the head, its edge scalloped.
    ring_round(m, "Accent", (0, -0.4, 8.7), 4.9, (0, 1, -0.3), 0.9, count=18, squash=0.96)
    for k in range(14):
        a = k * math.tau / 14
        base = Vector((math.cos(a) * 4.9, -0.1, 8.7 + math.sin(a) * 4.6))
        point(m, "Accent", tuple(base), tuple(base + Vector((math.cos(a) * 0.5, 1.5, math.sin(a) * 0.5))), 1.5)

    # The head: wide, low, under a heavy ridge.
    m.use("Head", (0, 0.4, 8.2), "Swim")
    sweep_fine(m, "Body", [((0, -0.6, 8.6), 9.0, 8.4), ((0, 1.4, 8.6), 10.2, 8.2), ((0, 3.2, 8.1), 9.0, 7.0), ((0, 4.8, 7.6), 6.8, 5.4), ((0, 5.8, 7.4), 4.6, 3.8)], sides=14)
    for side in (-1, 1):
        look = Vector((side * 0.5, 0.86, -0.1))
        at = Vector((side * 3.75, 2.75, 9.55))
        ring_round(m, "Glow", tuple(at), 1.62, look, 0.2, count=16)
        egg(m, "Socket", tuple(at), 1.5, 0.8, 1.4, 12, 6)
        slit_eye(m, tuple(at + look * 0.4), 1.12, look, side, iris="EyeGlow", lid_role="Accent", top=0.5, tilt=0.86, low=0.4)
        sabre(m, "Accent", [(side * 5.6, 1.0, 11.5), (side * 4.0, 2.8, 11.5), (side * 1.4, 4.8, 9.8)], 1.5, 7, flat=1.5, power=2.0)
        for k in range(3):  # smaller eyes crowding behind it
            p = Vector((side * (4.7 - 0.1 * k), 0.8 - 1.0 * k, 11.1 - 0.15 * k))
            egg(m, "Socket", tuple(p), 0.5, 0.42, 0.42, 8, 4)
            slit_eye(m, tuple(p + Vector((side * 0.1, 0.1, 0.1))), 0.27, (side * 0.8, 0.5, 0.3), side, iris="EyeGlow", lid_role="Accent", top=0.3, tilt=0.5, low=0.2, pupil="Slit")

    # The mouth at the middle of the arms: a crimson ring, teeth all round and a black hooked beak.
    mouth = Vector((0, 5.9, 7.2))
    egg(m, "Mouth", tuple(mouth), 2.9, 0.6, 2.7, 12, 6)
    ring_round(m, "Belly", tuple(mouth + Vector((0, 0.2, 0))), 3.0, (0, 1, 0), 1.0, count=18, squash=0.94)
    for k in range(14):
        a = (k + 0.5) * math.tau / 14
        base = mouth + Vector((math.cos(a) * 2.7, 0.3, math.sin(a) * 2.5))
        tip = mouth + Vector((math.cos(a) * (1.3 - 0.3 * (k % 2)), 1.0, math.sin(a) * (1.2 - 0.3 * (k % 2))))
        point(m, "Teeth", tuple(base), tuple(tip), 0.76)
    sabre(m, "Beak", [(0, 6.0, 9.0), (0, 7.6, 8.5), (0, 8.5, 7.2), (0, 8.3, 6.0)], 2.2, 9, flat=1.3, power=1.2)
    m.use("Jaw", (0, 5.0, 6.8), "Head")
    sabre(m, "Beak", [(0, 6.0, 5.5), (0, 7.2, 5.7), (0, 7.8, 6.6)], 1.9, 8, flat=1.2, power=1.2)
    swing(m, ["Jaw"], (0, 5.0, 6.8), -0.3)

    # Eight arms in a ring round the mouth, curling out at the tips, webbed at the base, hooks and suckers on their inner sides.
    centre = Vector((0, 5.2, 7.2))
    arms = []
    for n in range(1, 9):
        a = (n - 1) * math.tau / 8 + math.pi / 8
        radial = Vector((math.cos(a), 0, math.sin(a)))
        root = centre + radial * 3.3
        pts = []
        for i in range(24):
            t = i / 23
            p = root + Vector((0, 15.0 * t - 4.6 * t ** 4, 0)) + radial * (3.4 * t ** 1.2 + 5.0 * t ** 4)
            p.z = max(p.z, 0.9)
            pts.append(tuple(p))
        name, tip = f"Tentacle{n}", f"Tentacle{n}b"
        m.joint(name, tuple(root), "Head")
        m.joint(tip, pts[11], name)
        bones2 = ["Head"] + [name] * 11 + [tip] * 12
        widths = [2.7 * (1 - i / 23) ** 0.8 + 0.1 for i in range(24)]
        sweep(m, "Body", [(p, w, w) for p, w in zip(pts, widths)], bones2, sides=8, up=tuple(radial))
        arms.append((pts, bones2))
        for i in range(2, 20, 2):
            p = Vector(pts[i])
            m.bone = bones2[i]
            along = (Vector(pts[i + 1]) - p).normalized()
            out = (radial - along * radial.dot(along)).normalized()
            size = 0.16 * widths[i] + 0.12
            cap(m, "Claw", tuple(p - out * widths[i] * 0.4), size * 1.3, -out, 1.1, rings=1, sides=6)
            cap(m, "Shine", tuple(p - out * widths[i] * 0.42), size * 1.3, -out, 0.6, rings=1, sides=6)
            if i % 6 == 0:
                point(m, "Claw", tuple(p + out * widths[i] * 0.4), tuple(p + out * (widths[i] * 0.5 + 0.9) - along * 0.5), 0.5)
    # Webbing between the arms' roots, pulled in at its edge.
    for k in range(8):
        (pa, ba), (pb, bb) = arms[k], arms[(k + 1) % 8]
        rows, ring_bones = [], []
        for i in (0, 2, 4, 6):
            a0, b0 = Vector(pa[i]), Vector(pb[i])
            mid = a0.lerp(b0, 0.5)
            mid = mid.lerp(Vector((0, mid.y, 7.2)), 0.1 + 0.03 * i) - Vector((0, 0.16 * i, 0))
            rows.append([tuple(a0), tuple(mid), tuple(b0)])
            ring_bones.append([ba[i], ba[i], bb[i]])
        sheet(m, "Belly", rows, ring_bones, 0.2)
    m.bone = "Head"

    hunting_arm(m, "L", -1)
    hunting_arm(m, "R", 1)
    m.bone = "Head"
    m.head_centre = (0, 7.0, 8.4)
    return m


ALL = [shrimpact, kraken]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "abyss_7_8", SKY, FLOOR, GLOW_ROLES, glow=1.0, spacing=50)


if __name__ == "__main__":
    main()
