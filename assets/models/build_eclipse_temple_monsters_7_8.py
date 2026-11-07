"""Builds Eclipse Temple's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_eclipse_temple_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_eclipse_temple_monsters_7_8.py    (stills only)
    ONLY=praying_menace QUICK=1 ...                                                  (just that one)

Saves eclipse_temple_monsters_7_8.blend and renders to design/world/monsters_eclipse_temple_7_8/. The first six are in
build_eclipse_temple_monsters.py; what this batch shares is in rare_kit.py.

The owner asked for 8 monsters a map (2026-11-06): two more each, nicer than the ones before, more aggressive map by map. After
Starfall Crater's calm the run picks up again, fiercer than The Abyss. They share the eclipse eye (build_eclipse_temple_monsters.py): a
black iris ringed with glowing jade, under a gold mask. The map's colours: obsidian, old gold, jade, red laterite, jungle green.

  Praying Menace  a temple mantis as tall as a doorway, in a gold mask, its obsidian scythes folded as if it's praying. It isn't.
                  It flings them open and two crescents of jade fly out, spinning, and come back to its hands
  Batastrophe     a giant bat, the shadow that eats the light: gold mask, huge ears, a mouth that's most of its face, wings wider than a
                  temple. It climbs, screams rings of jade at you, then folds its wings and drops

They're the first that come at you through the air. What moves: the usual walk, idle and swim (Batastrophe has a Swim bone: it flies),
and from rare_kit.py (SWAY in DinoLifeController): ArmL, ArmR, ScytheL, ScytheR and Crescent1 and 2, Ring1 to 4, and Sway bones.

Skin roles Body, Accent, Belly and Claw take the colour mutations; gold, jade and the face keep theirs. EyeGlow, Jade and EclipseRing glow
(all already in shared/Roles.luau). Built at the first map's size. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0.
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
from rare_kit import cap, chain, curve, fine, jointed, leaf, lid, poly, ring_round, sabre, scallop, sheet, skin, sweep, sweep_fine, swing  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_eclipse_temple_7_8"
BLEND = "eclipse_temple_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = {"EyeGlow", "Jade", "EclipseRing"}
rare_kit.kit.NO_STUDS.update({"Trim", "TrimDark"})

JADE, GOLD, GOLD_DARK = "#47ff9c", "#f0b93a", "#b8801f"
FACE = {"Pupil": "#0c0a12", "Slit": "#0c0a12", "Socket": "#0c0a12", "EyeGlow": JADE, "Highlight": "#ffffff", "Mouth": "#3a1420", "Teeth": "#f4ecd6", "Tongue": "#e0607e", "Trim": GOLD, "TrimDark": GOLD_DARK,
        "Jade": JADE, "EclipseRing": JADE}
SKY, FLOOR = "#1b2b2e", "#804642"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


def eclipse_ball(m, centre, r, look, side, lid_role="Trim", top=0.5, tilt=0.8, low=0.32, pupil="Pupil"):
    """The eclipse eye as a real eyeball: black, a ring of burning jade, a black middle, under hard lids. No white at all."""
    egg(m, "Socket", centre, r, r, r, 10, 6)
    forward = Vector(look).normalized()
    cap(m, "EyeGlow", centre, r * 1.01, forward, 0.74, rings=4, sides=12)
    cap(m, pupil, centre, r * 1.022, forward, 0.5, rings=3, sides=12)
    u = forward.cross(Vector((0, 0, 1))).normalized()
    v = u.cross(forward)
    cap(m, "Highlight", centre, r * 1.03, forward - u * side * 0.3 + v * 0.3, 0.1, sides=6, rings=2)
    lid(m, lid_role, centre, r, forward, top, tilt, side)
    lid(m, lid_role, centre, r, forward, low, 0.0, side, lower=True)


# ---------------------------------------------------------------------- Praying Menace


def crescent(m, n, at, span, parent="Root"):
    """A flat crescent of jade on its own bone, parked out of sight in the abdomen until it's thrown."""
    m.use(f"Crescent{n}", at, parent)
    x, y, z = at
    count = 8
    outer = [(x + math.sin(-1.25 + 2.5 * i / count) * span / 2, y + math.cos(-1.25 + 2.5 * i / count) * span / 2, z) for i in range(count + 1)]
    inner = [(x + math.sin(-1.25 + 2.5 * i / count) * span * 0.4, y + math.cos(-1.25 + 2.5 * i / count) * span * 0.26 - span * 0.05, z) for i in range(count + 1)]
    sheet(m, "Jade", [outer, inner], [[f"Crescent{n}"] * (count + 1)] * 2, 0.5)


def scythe_arm(m, letter, side):
    """A raptor's arm, folded: a spiked upper arm reaching forward and a blade hanging back from it, like hands in prayer."""
    shoulder, elbow, wrist = Vector((side * 1.9, 3.6, 14.2)), Vector((side * 2.6, 9.0, 13.6)), Vector((side * 1.2, 6.8, 9.2))
    m.use(f"Arm{letter}", tuple(shoulder))
    m.joint(f"Arm{letter}", tuple(shoulder), "Neck")
    sweep_fine(m, "Body", [(tuple(shoulder), 1.6, 2.0), (tuple(shoulder.lerp(elbow, 0.4)), 1.8, 3.4), (tuple(shoulder.lerp(elbow, 0.85)), 1.4, 2.2), (tuple(elbow), 1.3, 1.6)], sides=10)
    sabre(m, "Trim", [tuple(shoulder + Vector((0, 0.3, 1.0))), tuple(shoulder.lerp(elbow, 0.4) + Vector((0, 0, 1.72))), tuple(shoulder.lerp(elbow, 0.8) + Vector((0, 0, 1.1))), tuple(elbow + Vector((0, 0.3, 0.8)))], 0.42, 8, power=4)
    for t, tall in ((0.25, 1.0), (0.45, 1.4), (0.65, 1.2), (0.82, 0.8)):  # spikes along its underside, to hold what it catches
        p = shoulder.lerp(elbow, t)
        point(m, "Claw", tuple(p + Vector((0, 0, -0.9))), tuple(p + Vector((-side * 0.2, 0.4, -0.9 - tall))), 0.6)
    m.use(f"Scythe{letter}", tuple(elbow), f"Arm{letter}")
    # The forearm and its blade: obsidian, gold along the back, jade in the edge.
    sweep_fine(m, "Accent", [(tuple(elbow), 1.4, 1.5), (tuple(elbow.lerp(wrist, 0.5)), 1.4, 1.7), (tuple(wrist), 1.0, 1.1)], sides=8, per=2)
    tip = wrist + Vector((-side * 0.2, -3.6, -1.2))
    sabre(m, "Claw", [tuple(wrist), tuple(wrist + Vector((-side * 0.1, -1.2, -1.8))), tuple(wrist + Vector((-side * 0.2, -2.7, -2.1))), tuple(tip)], 1.5, 12, flat=0.5, power=1.1)
    sabre(m, "Jade", [tuple(wrist + Vector((-side * 0.05, 0.25, -0.5))), tuple(wrist + Vector((-side * 0.1, -1.0, -2.2))), tuple(wrist + Vector((-side * 0.2, -2.7, -2.45))), tuple(tip + Vector((0, -0.1, -0.1)))], 0.5, 7, flat=0.9, power=1.1)
    for t in (0.2, 0.42, 0.64, 0.84):
        p = elbow.lerp(wrist, t)
        point(m, "Teeth", tuple(p + Vector((0, 0.5, 0))), tuple(p + Vector((0, 1.3, -0.2))), 0.42)
    sweep(m, "Trim", [(tuple(elbow.lerp(wrist, 0.95)), 1.5, 1.5), (tuple(wrist + Vector((-side * 0.02, -0.08, -0.2))), 1.5, 1.5)], sides=6)
    m.bone = "Spine"


def mantis_leg(m, bone, side, hip, knee, foot):
    """A long jointed leg: a thick thigh up to a high knee, a thin shin bowed down, and a little foot lying along the ground."""
    m.use(bone, tuple(hip))
    h, k, f = Vector(hip), Vector(knee), Vector(foot)
    ankle = k.lerp(f, 0.9) + Vector((0, 0, 0.3))
    bow = Vector((side * 0.5, 0, 0.5))
    sweep_fine(m, "Body", [(tuple(h), 1.1, 1.2), (tuple(h.lerp(k, 0.4) + Vector((0, 0, 0.3))), 1.5, 1.8), (tuple(h.lerp(k, 0.85)), 1.0, 1.1), (tuple(k), 0.8, 0.86)], sides=8, per=2)
    ring_round(m, "Trim", tuple(k), 0.56, k - h, 0.34, count=10)
    sweep_fine(m, "Accent", [(tuple(k), 0.76, 0.76), (tuple(k.lerp(ankle, 0.5) + bow), 0.6, 0.6), (tuple(ankle), 0.44, 0.44)], sides=6, per=3)
    for t in (0.2, 0.42, 0.64):  # thorns down the shin
        p = k.lerp(ankle, t) + bow * (1 - abs(2 * t - 1))
        point(m, "Claw", tuple(p), tuple(p + Vector((side * 0.5, 0.15, 0.5))), 0.3)
    point(m, "Trim", tuple(k + Vector((0, 0, 0.2))), tuple(k + Vector((side * 0.3, -0.5, 1.5))), 0.6)
    ahead = Vector((side * 0.4, 1, 0)).normalized()
    sweep_fine(m, "Accent", [(tuple(ankle), 0.44, 0.44), (tuple(f + Vector((0, 0, 0.3))), 0.4, 0.36), (tuple(f + ahead * 1.6 + Vector((0, 0, 0.16))), 0.3, 0.24)], sides=6, per=2)
    for d in (-0.5, 0.5):
        sabre(m, "Claw", [tuple(f + ahead * 1.5 + Vector((0, 0, 0.14))), tuple(f + ahead * 2.1 + Vector((d * 0.4, 0, 0.14))), tuple(f + ahead * 2.6 + Vector((d * 0.8, 0, 0.02)))], 0.28, 4)
    m.bone = "Spine"


def praying_menace():
    """A temple mantis in a gold mask, scythes folded."""
    m = monster("dino_PrayingMenace", Body="#1b1722", Accent="#2d2130", Belly="#7a2a28", Claw="#0e0b10", Wingcase="#1f7a4d", WingcaseDark="#14573a")
    m.joint("Spine", (0, -1.4, 8.0))

    # The abdomen: long, tapering back, under two folded wings, leaf green, veined with gold.
    route = [(0, -1.0, 8.2), (0, -3.6, 8.1), (0, -6.8, 7.8), (0, -10.0, 7.2), (0, -13.0, 6.5), (0, -15.6, 5.8)]
    path = [(p, w, w * 0.8) for p, w in zip(curve(route, 9), (3.4, 4.6, 5.6, 6.2, 6.2, 5.6, 4.4, 2.8, 0.5))]
    bones = jointed(m, "Belly", ["Tail1", "Tail2", "Tail3"], path, sides=12)
    for i, (p2, w, _) in enumerate(path[1:-1], start=1):  # the rings of its belly
        m.bone = bones[i]
        ring_round(m, "Accent", p2, w * 0.5, (0, -1, -0.1), 0.26, count=12, squash=0.8)
    # Two long folded wings, leaf green, a curved blade each, past the end of the body and veined with gold.
    for s2, role in ((-1, "Wingcase"), (1, "WingcaseDark")):
        rows = []
        ts = [i / 13 for i in range(14)]
        for t in ts:
            y = -0.4 - 19.0 * t
            top = 8.4 + 2.9 * math.sin(math.pi * min(t * 0.9 + 0.1, 1)) - 2.6 * t
            half = 3.9 * math.sin(math.pi * (t * 0.9 + 0.1)) ** 0.7 + 0.05
            rows.append([(0.0, y, top + 0.3), (s2 * half * 0.4, y, top + 0.2), (s2 * half * 0.75, y, top - 0.7), (s2 * half, y, top - 2.2 * math.sin(math.pi * (t * 0.9 + 0.1)))])
        grid_bones = [[bones[min(int(k * 0.72), len(bones) - 1)]] * 4 for k in range(14)]
        sheet(m, role, rows, grid_bones, 0.16)
        # Gold veins: one down its length, and the side veins running off it.
        for i in range(13):
            m.bone = grid_bones[i][0]
            beam(m, "Trim", tuple(Vector(rows[i][1]) + Vector((0, 0, 0.14))), tuple(Vector(rows[i + 1][1]) + Vector((0, 0, 0.14))), 0.2, 0.18, 0.1)
            if i % 2 == 0 and i < 12:
                beam(m, "Trim", tuple(Vector(rows[i][1]) + Vector((0, 0, 0.14))), tuple(Vector(rows[i + 2][3]) + Vector((0, 0, 0.14))), 0.12, 0.1, 0.08)
    m.bone = "Spine"

    # Four long thin legs out to the sides.
    mantis_leg(m, "FrontL", -1, (-1.5, 0.8, 8.2), (-7.4, 3.6, 11.2), (-10.0, 6.4, 0.03))
    mantis_leg(m, "FrontR", 1, (1.5, 0.8, 8.2), (7.4, 3.6, 11.2), (10.0, 6.4, 0.03))
    mantis_leg(m, "BackL", -1, (-1.6, -1.8, 8.0), (-8.4, -6.2, 12.2), (-11.4, -11.2, 0.03))
    mantis_leg(m, "BackR", 1, (1.6, -1.8, 8.0), (8.4, -6.2, 12.2), (11.4, -11.2, 0.03))

    # The long neck, rearing up from the body, banded with gold.
    m.joint("Neck", (0, 0.8, 9.2), "Spine")
    m.bone = "Neck"
    neck = [((0, -0.6, 8.2), 3.8, 3.6), ((0, 0.8, 9.6), 3.2, 3.2), ((0, 2.2, 12.0), 2.6, 2.7), ((0, 3.2, 14.4), 3.0, 3.1), ((0, 4.0, 16.2), 2.4, 2.4)]
    sweep_fine(m, "Body", neck, ["Spine", "Neck", "Neck", "Neck", "Neck"], sides=12, up=(0, -0.7, 0.7))
    for p, r in (((0, 1.2, 10.3), 1.72), ((0, 1.9, 11.4), 1.48), ((0, 2.5, 12.6), 1.46), ((0, 3.0, 13.8), 1.62)):
        ring_round(m, "Trim", p, r, (0, 0.4, 0.92), 0.36, count=14)
    for z, y in ((10.8, 0.1), (13.2, 1.5), (15.0, 2.5)):  # spines down its back
        point(m, "Claw", (0, y + 0.3, z), (0, y - 1.3, z + 0.9), 0.8)
    scythe_arm(m, "L", -1)
    scythe_arm(m, "R", 1)

    # The head: a wide triangle, an eye at each top corner, narrowing down to the mouth.
    m.use("Head", (0, 4.4, 16.4), "Neck")
    sweep_fine(m, "Body", [((0, 4.2, 17.0), 3.4, 3.0), ((0, 5.4, 17.2), 7.2, 3.2), ((0, 6.2, 16.6), 5.0, 3.0), ((0, 6.9, 15.6), 3.0, 2.2)], sides=12, per=2)
    # The gold mask, its point down the face.
    poly(m, "Trim", [(-2.9, 6.9, 18.5), (0, 7.5, 18.9), (2.9, 6.9, 18.5), (1.7, 7.5, 16.6), (0, 7.8, 15.7), (-1.7, 7.5, 16.6)], (0, -0.7, 0))
    poly(m, "TrimDark", [(-2.1, 7.0, 18.2), (0, 7.58, 18.5), (2.1, 7.0, 18.2), (1.2, 7.58, 16.8), (0, 7.86, 16.1), (-1.2, 7.58, 16.8)], (0, -0.3, 0))
    egg(m, "Jade", (0, 7.72, 17.3), 0.5, 0.24, 0.5, 8, 4)  # a third eye of jade
    for side in (-1, 1):
        beam(m, "Trim", (side * 3.4, 6.6, 19.0), (side * 0.3, 7.9, 17.9), 0.56, 0.5, 0.34)  # a hard gold brow
    for side in (-1, 1):
        at = (side * 3.5, 5.6, 17.3)
        egg(m, "Body", at, 1.3, 1.0, 1.15, 12, 6)
        eclipse_ball(m, (side * 3.56, 5.9, 17.25), 1.0, (side * 0.46, 0.88, -0.12), side, lid_role="Trim", top=0.6, tilt=0.9, low=0.42)
        sabre(m, "Trim", [(side * 3.6, 5.0, 18.5), (side * 4.1, 3.8, 20.0), (side * 3.9, 2.4, 21.6)], 1.0, 8)  # swept-back gold horns
    # Feelers.
    for n, side in ((1, -1), (2, 1)):
        pts = curve([(side * 0.8, 6.0, 18.2), (side * 2.4, 7.6, 20.6), (side * 5.0, 7.0, 22.4), (side * 8.0, 4.2, 23.0)], 7)
        chain(m, "Sway", n, pts, 0.3, 0.08, parent="Head", role="Accent")
    m.bone = "Head"

    # The mouth: a lower jaw and two side jaws that open round it, all needles.
    zm = 15.1
    egg(m, "Mouth", (0, 6.7, zm - 0.1), 1.6, 0.8, 0.9, 8, 4)
    for side, letter in ((-1, "L"), (1, "R")):
        pivot = (side * 1.3, 6.4, zm - 0.1)
        m.use(f"Mand{letter}", pivot, "Head")
        sabre(m, "Accent", [pivot, (side * 2.3, 7.6, zm - 0.5), (side * 1.9, 9.0, zm - 1.0), (side * 0.5, 9.8, zm - 1.5)], 1.3, 7, flat=0.8, power=1.2)
        for t in (0.3, 0.5, 0.7):
            x, y = side * (2.3 - 1.4 * t), 7.4 + 2.2 * t
            point(m, "Teeth", (x, y, zm - 0.7), (x - side * 0.8, y + 0.2, zm - 0.8), 0.32)
    m.use("Jaw", (0, 5.9, zm - 0.2), "Head")
    sweep(m, "Accent", [((0, 6.0, zm - 0.7), 2.4, 0.7), ((0, 7.6, zm - 0.8), 1.8, 0.6), ((0, 8.4, zm - 0.7), 0.8, 0.4)], sides=6)
    for k in (-1, 0, 1):
        point(m, "Teeth", (k * 0.5, 7.6 - abs(k) * 0.3, zm - 0.5), (k * 0.5, 7.7 - abs(k) * 0.3, zm + 0.3), 0.3)
    swing(m, ["Jaw"], (0, 5.9, zm - 0.2), -0.3)

    # The crescents, parked in the abdomen until they're thrown.
    for n in (1, 2):
        crescent(m, n, (0, -7.0, 7.8), 4.8)
    m.bone = "Head"
    m.head_centre = (0, 7.0, 16.6)
    return m


# ---------------------------------------------------------------------- Batastrophe


def bat_wing(m, s, letter):
    """A vast wing: arm, wrist, four long curved fingers, and skin stretched between them down to the body."""
    shoulder, elbow, wrist = Vector((s * 3.4, 0.6, 14.0)), Vector((s * 9.4, 1.8, 18.6)), Vector((s * 14.6, 3.8, 20.8))
    tips = [Vector((s * 29.0, 3.6, 16.2)), Vector((s * 26.4, -0.6, 8.4)), Vector((s * 19.4, -1.4, 4.2)), Vector((s * 11.6, -1.2, 3.6))]
    root = Vector((s * 2.6, -1.0, 6.8))
    m.use(f"Wing{letter}", tuple(shoulder), "Swim")
    sweep_fine(m, "Body", [(tuple(shoulder), 2.6, 2.6), (tuple(shoulder.lerp(elbow, 0.45)), 2.2, 2.3), (tuple(elbow), 1.5, 1.5)], sides=8)
    m.use(f"WingTip{letter}", tuple(elbow), f"Wing{letter}")
    sweep_fine(m, "Body", [(tuple(elbow), 1.5, 1.5), (tuple(elbow.lerp(wrist, 0.5)), 1.3, 1.3), (tuple(wrist), 1.2, 1.2)], sides=8)
    ring_round(m, "Trim", tuple(wrist), 0.86, wrist - elbow, 0.42, count=10)
    sabre(m, "Trim", [tuple(wrist), tuple(wrist + Vector((s * 0.6, 1.3, 1.5))), tuple(wrist + Vector((s * 0.2, 2.6, 1.7)))], 1.0, 7)

    def rib(tip, bend, count=9):
        mid = wrist.lerp(tip, 0.5) + bend
        out = []
        for i in range(count):  # a smooth bow from the wrist to the tip
            t = i / (count - 1)
            out.append(wrist * (1 - t) ** 2 + mid * (2 * t * (1 - t)) + tip * t * t)
        return out

    fingers = [rib(tip, Vector((s * 2.4, 0.6 - 0.5 * i, 1.8 - 0.3 * i))) for i, tip in enumerate(tips)]
    n = len(fingers[0])
    for row in fingers:
        sweep(m, "Accent", [(tuple(p), 0.8 - 0.07 * k, 0.8 - 0.07 * k) for k, p in enumerate(row)], sides=6)
        sabre(m, "Trim", [tuple(row[-2].lerp(row[-1], 0.6)), tuple(row[-1]), tuple(row[-1] + (row[-1] - row[-2]).normalized() * 1.8)], 0.5, 5)
    rows, bones = [], []
    for a, b in zip(fingers, fingers[1:]):
        for share in (0.0, 0.25, 0.5, 0.75):  # the skin between two fingers, sagging into a smooth scallop
            sag = math.sin(math.pi * share) * 0.34
            rows.append([p.lerp(q, share).lerp(wrist, sag * (k / (n - 1)) ** 2) for k, (p, q) in enumerate(zip(a, b))])
            bones.append([f"WingTip{letter}"] * n)
    rows.append(fingers[-1])
    bones.append([f"WingTip{letter}"] * n)
    edge = elbow.lerp(wrist, 0.05)
    inner_tip = fingers[-1][-1].lerp(root, 0.5).lerp(elbow, 0.26)
    rows.append([edge.lerp(inner_tip, k / (n - 1)) for k in range(n)])
    bones.append([f"WingTip{letter}"] * 3 + [f"Wing{letter}"] * (n - 3))
    rows.append([shoulder.lerp(root, k / (n - 1)) for k in range(n)])
    bones.append(["Swim"] * n)
    sheet(m, "Membrane", [[tuple(p) for p in row] for row in rows], bones, 0.18)
    # Veins of jade running out through the skin between the fingers.
    m.bone = f"WingTip{letter}"
    for r in (2, 6, 10):
        for k in range(2, 6):
            beam(m, "Jade", tuple(rows[r][k] + Vector((0, 0.12, 0))), tuple(rows[r][k + 1] + Vector((0, 0.12, 0))), 0.22 - 0.02 * k, 0.2 - 0.02 * k, 0.1)
    m.bone = "Swim"


def batastrophe():
    """A giant bat: gold mask, huge ears, a mouth that's most of its face, wings wider than a temple."""
    m = monster("dino_Batastrophe", Body="#1a1520", Accent="#0f0c14", Belly="#35202f", Claw="#0b090e", Membrane="#4a1630", Fur="#2b2030")
    rng = random.Random(6)
    m.use("Swim", (0, 0, 11.0), "Root")

    # A deep furred chest down to a narrow waist.
    sweep_fine(m, "Body", [((0, -1.6, 5.2), 3.6, 3.0), ((0, -1.2, 7.4), 5.4, 4.6), ((0, -0.4, 10.0), 7.6, 6.4), ((0, 0.4, 12.6), 9.0, 7.2), ((0, 1.0, 14.4), 7.4, 5.8), ((0, 1.2, 15.6), 4.6, 4.0)], sides=14, up=(0, 1, 0.1))
    # Fur in soft overlapping tiers down from the shoulders, one colour a tier.
    for k, (y, rx, ry, top, tip, role, count) in enumerate(((0.8, 3.9, 3.0, 16.0, 13.8, "Fur", 15), (0.5, 4.8, 3.7, 14.8, 12.2, "Belly", 18), (0.1, 4.7, 3.7, 13.0, 10.4, "Fur", 18), (-0.4, 4.0, 3.2, 11.2, 8.6, "Belly", 16), (-0.9, 3.1, 2.6, 9.4, 6.8, "Fur", 14), (-1.3, 2.4, 2.1, 7.6, 5.0, "Belly", 12))):
        scallop(m, (role,), (0, y), (rx, ry), top, tip, count, 0.16, thick=0.5, offset=0.16 * k)
    # On its chest a black sun in a gold ring: the eclipse it's named for.
    c = Vector((0, 4.9, 11.6))
    ring_round(m, "Trim", tuple(c), 2.0, (0, 1, 0.1), 0.56, count=18)
    egg(m, "Socket", tuple(c + Vector((0, -0.14, 0))), 1.9, 0.3, 1.9, 14, 5)
    for k in range(12):
        a = k * math.tau / 12
        d = Vector((math.cos(a), 0, math.sin(a)))
        point(m, "Jade" if k % 2 else "Trim", tuple(c + d * 2.1), tuple(c + d * (3.3 + 0.5 * (k % 2)) + Vector((0, -0.2, 0))), 0.54)

    # Legs hanging, talons open, and a stump of a tail.
    for side, n in ((-1, 3), (1, 4)):
        hip = Vector((side * 1.8, -1.2, 6.2))
        pts = [tuple(hip), tuple(hip + Vector((side * 0.5, -0.5, -2.0))), tuple(hip + Vector((side * 0.9, 0.0, -3.6)))]
        names = chain(m, "Sway", n, curve(pts, 5), 1.5, 0.8, parent="Swim", role="Belly", sides=8)
        foot = Vector(pts[-1])
        for dx in (-0.7, 0, 0.7):
            sabre(m, "Trim", [tuple(foot), tuple(foot + Vector((dx, 1.0, -0.5))), tuple(foot + Vector((dx * 1.2, 1.3, -1.3)))], 0.5, 4)
    m.bone = "Swim"
    m.joint("Tail1", (0, -2.2, 6.4), "Swim")
    m.bone = "Tail1"
    sabre(m, "Accent", [(0, -1.8, 6.6), (0, -3.6, 5.8), (0, -5.0, 4.6)], 1.6, 5)
    m.bone = "Swim"

    bat_wing(m, -1, "L")
    bat_wing(m, 1, "R")

    # The head, thrust forward over its chest.
    m.use("Head", (0, 1.8, 15.8), "Swim")
    zm = 14.9
    sweep_fine(m, "Body", [((0, 1.4, 16.6), 5.8, 5.2), ((0, 3.0, 16.9), 6.8, 5.0), ((0, 4.4, 16.5), 5.8, 3.6), ((0, 5.6, 16.0), 3.6, 2.2), ((0, 6.3, 15.8), 2.4, 1.3)], sides=12, per=2)
    scallop(m, ("Fur",), (0, 1.4), (4.0, 3.2), 19.0, 16.4, 15, 0.22, thick=0.5)  # a ruff of fur behind it
    # The gold mask: one smooth plate from the brow down the nose.
    sweep_fine(m, "Trim", [((0, 2.8, 18.5), 5.6, 1.0), ((0, 4.3, 17.85), 5.0, 1.0), ((0, 5.5, 17.0), 2.6, 0.8), ((0, 6.5, 16.3), 1.5, 0.5)], sides=8, per=2)
    for side in (-1, 1):
        sabre(m, "Trim", [(side * 3.3, 3.0, 18.2), (side * 2.6, 4.6, 17.7), (side * 0.3, 5.7, 17.4)], 0.8, 7, flat=1.2, power=2.5)  # a brow slanting hard to the nose
        at = Vector((side * 2.05, 4.62, 16.75))
        egg(m, "Socket", tuple(at), 1.1, 0.55, 0.72, 10, 5)
        eclipse_ball(m, tuple(at + Vector((side * 0.02, 0.25, 0))), 0.56, (side * 0.3, 0.92, -0.2), side, lid_role="Trim", top=0.54, tilt=0.88, low=0.36)
        # Ears: huge, ribbed, jade inside.
        base = Vector((side * 2.3, 1.8, 18.6))
        tip = base + Vector((side * 3.6, 0.5, 8.6))
        for role, grow, push in (("Accent", 1.0, 0.0), ("Membrane", 0.76, 0.2), ("Jade", 0.22, 0.34)):
            rows = []  # a cupped ear, wide at the base, curving to a point
            for t in (0.0, 0.2, 0.4, 0.6, 0.8, 0.92, 1.0):
                c0 = base.lerp(base.lerp(tip, 0.5 + 0.5 * grow), t)
                half = (2.6 * grow) * math.sin(math.pi * min(t * 0.86 + 0.14, 1)) ** 0.7 + 0.03
                rows.append([tuple(c0 + Vector((-side * half, push - 0.5, 0))), tuple(c0 + Vector((0, push + 0.2, 0))), tuple(c0 + Vector((side * half, push - 0.5, 0)))])
            sheet(m, role, rows, [["Head"] * 3] * 7, 0.26)
    # A leaf of a nose, standing up off the end of its mask.
    leaf(m, "Trim", (0, 6.5, 16.2), (0, 6.9, 18.0), (1, 0, 0), 1.5, 0.2)
    for side in (-1, 1):
        egg(m, "Socket", (side * 0.5, 6.7, 15.85), 0.22, 0.14, 0.18, 6, 3)
    # The mouth: a glowing throat and needles, and two fangs as long as its head.
    sweep(m, "Mouth", [((0, 1.8, zm + 0.04), 5.2, 0.2), ((0, 5.2, zm + 0.1), 3.6, 0.16), ((0, 6.3, zm + 0.2), 2.0, 0.12)], sides=8)
    egg(m, "Mouth", (0, 2.2, zm - 1.6), 2.6, 0.7, 2.0, 10, 5)
    egg(m, "Jade", (0, 2.76, zm - 1.5), 1.1, 0.3, 0.9, 8, 4)
    for side in (-1, 1):
        for k in range(8):
            t = k / 7
            y, x = 2.6 + 3.6 * t, side * (2.5 - 1.5 * t * t)
            point(m, "Teeth", (x, y, zm + 0.16), (x, y + 0.04, zm - 0.7 - 0.34 * (k % 2)), 0.36)
        sabre(m, "Teeth", [(side * 1.5, 5.4, zm + 0.2), (side * 1.56, 5.6, zm - 1.2), (side * 1.3, 5.3, zm - 2.8)], 0.86, 7, power=1.2)
    m.use("Jaw", (0, 2.0, zm - 0.02), "Head")
    z = zm - 0.42
    sweep(m, "Accent", [((0, 2.0, z), 5.0, 0.9), ((0, 4.6, z), 3.8, 0.8), ((0, 5.9, z + 0.1), 1.9, 0.6)], sides=8)
    sweep(m, "Mouth", [((0, 2.2, z + 0.42), 4.0, 0.1), ((0, 5.6, z + 0.36), 1.5, 0.1)], sides=8)
    sweep(m, "Tongue", [((0, 2.8, z + 0.5), 1.8, 0.22), ((0, 5.0, z + 0.46), 0.9, 0.16)], sides=6)
    for side in (-1, 1):
        for k in range(6):
            t = k / 5
            y, x = 2.8 + 2.8 * t, side * (2.1 - 1.2 * t * t)
            point(m, "Teeth", (x, y, z + 0.36), (x, y + 0.03, z + 1.0 + 0.24 * (k % 2)), 0.32)
    swing(m, ["Jaw"], (0, 2.0, zm - 0.02), -0.72)

    # Rings of sound, parked in its chest until it screams.
    for n, radius in enumerate((1.5, 2.2, 3.0, 3.8), start=1):
        at = (0, 0.4, 11.4)
        m.use(f"Ring{n}", at, "Swim")  # with the body, or they'd hang in the air when it dives
        pts = [tuple(Vector(at) + Vector((math.cos(a) * radius, 0, math.sin(a) * radius))) for a in (i * math.tau / 14 for i in range(15))]
        sweep(m, "EclipseRing", [(p, 0.42, 0.42) for p in pts], sides=5, caps=(False, False), up=(0, 1, 0))
    m.bone = "Head"
    m.head_centre = (0, 5.4, 15.6)
    return m


ALL = [praying_menace, batastrophe]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "eclipse_temple_7_8", SKY, FLOOR, GLOW_ROLES, glow=1.2, spacing=64)


if __name__ == "__main__":
    main()
