"""Builds the Desert's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_desert_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_desert_monsters_7_8.py    (stills only)
    ONLY=scorchion QUICK=1 ...                                               (just that one)

Saves desert_monsters_7_8.blend and renders to design/world/monsters_desert_7_8/. The Desert's first six are in
build_desert.py; what this batch shares is in rare_kit.py.

The owner asked for 8 monsters a map (2026-11-06): two more each, nicer than the ones before, more aggressive map by map.
These two are the Desert's new rarest, a step fiercer than the Forest's: angry faces and real weapons, but still a joke.

  Scorchion   a sunburnt scorpion the size of a truck: plated in scorched red with ember edges, eight legs, two huge pincers
              that snap one after the other, and a tail arched over its back that stabs with a glowing sting
  Rexhotep    a mummified T-Rex, risen and furious. Bandaged all over with a gold death mask for a snout, a striped royal
              headcloth, a pharaoh's false beard on its jaw and eyes burning jade. Its tiny arms clutch a tiny crook and flail

What moves: the usual walk, idle and roar, and from rare_kit.py (SWAY in DinoLifeController): Scorchion's pincers on PinchL
and PinchR, its stinger on Sting; Rexhotep's headcloth, loose bandages and flail on Sway bones.

Skin roles Body, Accent, Belly and Claw take the colour mutations; gold, lapis and the face keep theirs. Ember and Jade glow
(both already in shared/Roles.luau). Built at the first map's size. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0.
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
from rare_kit import bandage, cap, chain, curve, panel, round_eye, sabre, slit_eye, stripes, sweep, swing  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_desert_7_8"
BLEND = "desert_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = {"Ember", "Jade"}

FACE = {"Pupil": "#14100f", "EyeWhite": "#fff8e8", "Highlight": "#ffffff", "Mouth": "#3e1414", "Tongue": "#c9485a", "Teeth": "#fff4d8",
        "Socket": "#120c0a"}
SKY, FLOOR = "#ffd9a8", "#e8c283"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- Scorchion


def scorpion_leg(m, side, y, foot_y, reach, role="Body"):
    """One leg: out and up to a high knee, down to a pointed black foot, with a pale band at each joint."""
    hip = Vector((side * 2.1, y, 2.5))
    knee = Vector((side * (3.6 + reach * 0.4), y + (foot_y - y) * 0.35, 3.75))
    ankle = Vector((side * (5.0 + reach * 0.7), y + (foot_y - y) * 0.75, 2.2))
    foot = Vector((side * (5.7 + reach), foot_y, 0.02))
    sweep(m, role, [(tuple(hip), 1.05, 1.05), (tuple(knee), 0.95, 0.95)], sides=6)
    sweep(m, role, [(tuple(knee), 0.95, 0.95), (tuple(ankle), 0.72, 0.72)], sides=6)
    sweep(m, "Claw", [(tuple(ankle), 0.72, 0.72), (tuple(foot.lerp(ankle, 0.45)), 0.46, 0.46), (tuple(foot), 0.08, 0.08)], sides=6)
    for p, r in ((knee, 0.58), (ankle, 0.46)):
        egg(m, "Accent", tuple(p), r, r, r, 8, 5)


def pincer(m, side, letter):
    """A huge pincer on a thick arm: a fat palm, a fixed inner finger and a moving outer one on Pinch<letter>, both toothed."""
    sh, el, wr = Vector((side * 2.1, 3.1, 2.75)), Vector((side * 5.6, 4.2, 3.3)), Vector((side * 5.9, 6.9, 3.5))
    m.use(f"Arm{letter}", tuple(sh))
    sweep(m, "Body", [(tuple(sh), 1.55, 1.45), (tuple(el), 1.35, 1.3)], sides=8)
    sweep(m, "Body", [(tuple(el), 1.35, 1.3), (tuple(wr), 1.3, 1.25)], sides=8)
    egg(m, "Accent", tuple(el), 0.92, 0.92, 0.88, 8, 5)
    palm = wr + Vector((-side * 0.1, 1.15, 0.12))
    egg(m, "Accent", tuple(wr), 0.86, 0.86, 0.82, 8, 5)
    egg(m, "Body", tuple(palm), 1.62, 1.72, 1.2, 10, 6)
    egg(m, "Accent", tuple(palm + Vector((side * 0.55, -0.1, 0.72))), 0.72, 0.9, 0.5, 8, 4)
    for k in range(3):  # studs of armour along the palm
        egg(m, "Claw", tuple(palm + Vector((side * (1.2 - 0.05 * k), -0.7 + 0.72 * k, 0.32))), 0.2, 0.2, 0.2, 6, 3)
    # The fixed finger, on the inside, curving out.
    y0 = palm.y + 1.15
    inner = [(palm.x - side * 0.72, y0, palm.z), (palm.x - side * 0.92, y0 + 1.25, palm.z + 0.02), (palm.x - side * 0.62, y0 + 2.3, palm.z + 0.06),
             (palm.x - side * 0.02, y0 + 2.95, palm.z + 0.08)]
    sabre(m, "Claw", inner, 1.1, 8, flat=1.1, power=2.0)
    for t, y in ((0.0, 0.5), (0.0, 1.1), (0.0, 1.7)):  # teeth facing the other finger
        x = palm.x - side * (0.64 - 0.12 * y)
        point(m, "Teeth", (x, y0 + y, palm.z), (x + side * 0.4, y0 + y + 0.16, palm.z), 0.26)
    # The moving finger, on the outside, curving in.
    m.use(f"Pinch{letter}", (palm.x + side * 0.72, palm.y + 0.75, palm.z), f"Arm{letter}")
    outer = [(palm.x + side * 0.78, y0 - 0.2, palm.z), (palm.x + side * 1.12, y0 + 1.1, palm.z + 0.02), (palm.x + side * 0.82, y0 + 2.25, palm.z + 0.06),
             (palm.x + side * 0.12, y0 + 3.0, palm.z + 0.08)]
    sabre(m, "Claw", outer, 1.22, 8, flat=1.1, power=2.0)
    for y in (0.5, 1.2, 1.85):
        x = palm.x + side * (0.72 - 0.08 * y)
        point(m, "Teeth", (x, y0 + y, palm.z), (x - side * 0.42, y0 + y + 0.16, palm.z), 0.26)
    m.bone = "Spine"


def scorchion():
    """A sunburnt scorpion the size of a truck, pincers up, tail arched to stab."""
    m = monster("dino_Scorchion", Body="#b93a22", Accent="#ff8c2b", Belly="#f1d091", Claw="#2d1c18", Ember="#ffb31f", EyeColour="#ffb31f")
    m.joint("Spine", (0, 0, 2.6))

    # The body: overlapping armoured plates, each with a burning hem, narrowing to the tail.
    plates = [(3.9, 1.3, 5.3, 2.5), (1.55, 0.0, 5.7, 3.0), (0.25, -1.2, 5.4, 2.95), (-0.95, -2.35, 4.9, 2.75), (-2.1, -3.45, 4.2, 2.5), (-3.2, -4.45, 3.3, 2.2)]
    for y0, y1, w, h in plates:
        sweep(m, "Body", [((0, y0, 2.62), w * 0.86, h * 0.8), ((0, (y0 + y1) / 2, 2.75), w, h), ((0, y1, 2.68), w * 0.94, h * 0.9)], sides=10)
        sweep(m, "Accent", [((0, y1 + 0.2, 2.7), w * 0.985, h * 0.93), ((0, y1 - 0.05, 2.68), w * 0.985, h * 0.93)], sides=10)
    sweep(m, "Belly", [((0, 3.2, 1.95), 3.2, 1.0), ((0, 0, 1.85), 4.4, 1.0), ((0, -4.0, 2.05), 2.4, 0.9)], sides=8)
    for k, y in enumerate((0.75, -0.45, -1.6, -2.75)):  # a row of spines down the back
        point(m, "Claw", (0, y, 4.0 - 0.1 * k), (0, y - 0.45, 4.95 - 0.12 * k), 0.54)

    # Eight legs in four pairs, turn about on the Front and Back bones so they step like a real one.
    for side, letter in ((-1, "L"), (1, "R")):
        m.use(f"Front{letter}", (side * 0.6, 0.9, 2.6))
        scorpion_leg(m, side, 2.0, 3.2, 0.0)
        scorpion_leg(m, side, -1.0, -1.2, 0.7)
        m.use(f"Back{letter}", (side * 0.6, -0.8, 2.6))
        scorpion_leg(m, side, 0.5, 1.0, 0.55)
        scorpion_leg(m, side, -2.4, -3.3, 0.3)
    m.bone = "Spine"
    for side, letter in ((-1, "L"), (1, "R")):
        pincer(m, side, letter)

    # The tail: beads of armour arching up and over, ending in a glowing sting aimed past its head.
    spine = curve([(0, -4.3, 2.9), (0, -5.75, 3.6), (0, -6.5, 5.3), (0, -5.95, 7.2), (0, -4.4, 8.55), (0, -2.45, 8.95), (0, -0.85, 8.45)], 9)
    widths = [2.75, 2.5, 2.3, 2.15, 2.0, 1.85, 1.7, 1.55]
    names = ["Tail1", "Tail1", "Tail2", "Tail2", "Tail3", "Tail3", "Sting", "Sting"]
    parents = {"Tail1": "Spine", "Tail2": "Tail1", "Tail3": "Tail2", "Sting": "Tail3"}
    for i, (w, name) in enumerate(zip(widths, names)):
        a, b = Vector(spine[i]), Vector(spine[i + 1])
        if name not in m.joints:
            m.joint(name, tuple(a), parents[name])
        m.bone = name
        sweep(m, "Body", [(tuple(a.lerp(b, -0.05)), w * 0.78, w * 0.76), (tuple(a.lerp(b, 0.45)), w, w * 0.96), (tuple(a.lerp(b, 1.02)), w * 0.8, w * 0.78)], sides=8)
        sweep(m, "Accent", [(tuple(a.lerp(b, 0.78)), w * 0.94, w * 0.9), (tuple(a.lerp(b, 0.92)), w * 0.9, w * 0.86)], sides=8)
        if i < 7:  # a spike on each bead, along the top of the arch
            frame = rare_kit.frames_along([a, b])[0]
            top = a.lerp(b, 0.45) + frame[2] * w * 0.44
            point(m, "Claw", tuple(top), tuple(top + frame[2] * 0.62 - frame[0] * 0.3), 0.44)
    tip = Vector(spine[-1])
    egg(m, "Body", tuple(tip + Vector((0, 0.7, -0.22))), 1.05, 1.28, 1.0, 10, 6)
    for k, a in enumerate((0.0, 2.1, 4.2)):  # glowing bands round the venom bulb
        cap(m, "Ember", tuple(tip + Vector((0, 0.7, -0.22))), (1.07, 1.3, 1.02), (math.cos(a) * 0.9, 0.25, math.sin(a) * 0.9), 0.5, squash=(0.8, 1.2), rings=2)
    sabre(m, "Ember", [tuple(tip + Vector((0, 1.65, -0.35))), tuple(tip + Vector((0, 2.5, -0.5))), tuple(tip + Vector((0, 2.95, -1.3))), tuple(tip + Vector((0, 2.75, -2.25)))], 0.78, 8)
    m.bone = "Spine"

    # The head: low and wide under the front plate, two angry eyes under a burning brow, a jaw of teeth, two stub mandibles.
    m.use("Head", (0, 3.1, 2.6), "Spine")
    sweep(m, "Body", [((0, 3.4, 2.9), 3.9, 2.0), ((0, 4.3, 2.85), 3.6, 1.8), ((0, 5.1, 2.7), 3.0, 1.35), ((0, 5.45, 2.6), 2.4, 0.95)], sides=8)
    yf, zf = 4.72, 3.42
    for side in (-1, 1):
        round_eye(m, (side * 0.92, yf, zf), 0.68, (side * 0.3, 1.0, -0.1), side, iris_size=0.5, pupil_size=0.3, top=0.5, tilt=0.5, low=0.22)
        beam(m, "Accent", (side * 1.95, yf - 0.25, zf + 0.82), (side * 0.12, yf + 0.5, zf + 0.22), 0.5, 0.42, 0.36)
        point(m, "Claw", (side * 1.55, yf - 0.35, zf + 0.72), (side * 2.05, yf - 1.1, zf + 1.45), 0.42)
        for k, (x, z) in enumerate(((1.75, 0.05), (1.9, -0.32))):  # small spare eyes on the side of the plate
            egg(m, "Socket", (side * x, yf - 0.6 - 0.1 * k, zf - 0.2 + z), 0.17, 0.17, 0.17, 6, 3)
            cap(m, "Ember", (side * x, yf - 0.6 - 0.1 * k, zf - 0.2 + z), 0.175, (side * 0.8, 0.6, 0.1), 0.55, sides=6, rings=2)
    z = 2.22
    sweep(m, "Mouth", [((0, 3.9, z + 0.12), 3.1, 0.28), ((0, 5.3, z + 0.14), 2.2, 0.2)], sides=8)
    for k in range(7):  # upper teeth round the front of the mouth
        t = (k - 3) / 3
        x, y = t * 1.15, 5.34 - 0.5 * t * t
        size = 0.46 if k % 2 else 0.34
        point(m, "Teeth", (x, y, z + 0.16), (x, y + 0.06, z - size), 0.24)
    m.use("Jaw", (0, 3.95, z), "Head")
    sweep(m, "Belly", [((0, 3.95, z - 0.35), 2.9, 0.6), ((0, 4.9, z - 0.34), 2.5, 0.55), ((0, 5.5, z - 0.3), 1.9, 0.42)], sides=8)
    sweep(m, "Mouth", [((0, 4.0, z - 0.02), 2.4, 0.1), ((0, 5.35, z - 0.03), 1.7, 0.08)], sides=8)
    for k in range(6):
        t = (k - 2.5) / 2.5
        x, y = t * 0.95, 5.36 - 0.42 * t * t
        point(m, "Teeth", (x, y, z - 0.06), (x, y + 0.04, z + 0.32), 0.2)
    swing(m, ["Jaw"], (0, 3.95, z), -0.14)
    for side, letter in ((-1, "L"), (1, "R")):  # stub mandibles either side of the mouth, thrown wide in the roar
        m.use(f"Mand{letter}", (side * 1.3, 4.9, 2.3), "Head")
        sabre(m, "Claw", [(side * 1.3, 4.7, 2.3), (side * 1.55, 5.55, 2.3), (side * 1.15, 6.3, 2.2), (side * 0.55, 6.5, 2.05)], 0.68, 6, flat=1.0)
    m.bone = "Head"
    m.head_centre = (0, 5.0, 3.1)
    return m


# ---------------------------------------------------------------------- Rexhotep


def rexhotep():
    """A mummified T-Rex, risen and furious: bandages, a gold death mask, a royal headcloth and a pharaoh's beard."""
    m = monster("dino_Rexhotep", Body="#e9dcbc", Accent="#c7b48c", Belly="#f6edd6", Claw="#2c2320", Under="#8a7556", Gold="#f2b632", Lapis="#2342a8", Jade="#3effb6",
                EyeColour="#3effb6", Kohl="#14161f")
    rng = random.Random(708)
    m.joint("Spine", (0, -0.6, 6.6))

    # Legs: huge bandaged thighs, gold anklets, clawed feet.
    for side, letter in ((-1, "L"), (1, "R")):
        x = side * 1.75
        m.use(f"Leg{letter}", (x, -0.6, 6.3))
        sweep(m, "Under", [((x, -0.6, 6.9), 2.4, 2.9), ((x, -0.5, 5.0), 2.55, 3.1), ((x, -0.75, 3.55), 1.5, 1.75)], sides=8)
        bandage(m, [((x, -0.6, 7.2), 2.5, 3.0), ((x, -0.5, 5.0), 2.65, 3.2), ((x, -0.75, 3.5), 1.6, 1.85)], [f"Leg{letter}"] * 3, rng, step=0.55)
        m.use(f"Shin{letter}", (x, -0.75, 3.7), f"Leg{letter}")
        sweep(m, "Under", [((x, -0.75, 3.8), 1.35, 1.5), ((x, -0.3, 0.9), 1.1, 1.2)], sides=8)
        bandage(m, [((x, -0.75, 3.8), 1.45, 1.6), ((x, -0.35, 1.25), 1.2, 1.3)], [f"Shin{letter}"] * 2, rng, step=0.5)
        sweep(m, "Gold", [((x, -0.32, 1.32), 1.45, 1.55), ((x, -0.28, 0.82), 1.45, 1.55)], sides=8)
        sweep(m, "Accent", [((x, -1.0, 0.36), 1.3, 0.66), ((x, 0.0, 0.42), 1.9, 0.8), ((x, 1.2, 0.3), 2.0, 0.55)], sides=8)
        for dx, reach in ((-0.72, 1.2), (0.0, 1.5), (0.72, 1.2)):
            sabre(m, "Claw", [(x + dx, reach, 0.34), (x + dx * 1.05, reach + 0.6, 0.34), (x + dx * 1.1, reach + 1.05, 0.05)], 0.46, 5)
    m.bone = "Spine"

    # The body, leaning forward, bandaged all over, loose ends trailing.
    torso = [((0, -3.1, 6.9), 3.2, 3.5), ((0, -1.3, 7.2), 4.4, 4.7), ((0, 0.9, 7.8), 4.5, 4.7), ((0, 2.7, 8.5), 3.6, 3.7), ((0, 3.8, 9.1), 2.9, 3.0)]
    sweep(m, "Under", [(p, w * 0.95, h * 0.95) for p, w, h in torso], sides=10)
    bandage(m, torso, ["Spine"] * 5, rng, step=0.6)

    # The tail: long and tapering, the last wrap coming loose.
    tail_pts = curve([(0, -2.8, 7.0), (0, -5.0, 6.8), (0, -7.3, 6.1), (0, -9.5, 5.3), (0, -11.6, 4.9)], 9)
    widths = [3.2, 2.8, 2.35, 1.95, 1.6, 1.28, 1.0, 0.72, 0.42]
    bones = ["Spine"] + ["Tail1"] * 3 + ["Tail2"] * 3 + ["Tail3"] * 2
    m.joint("Tail1", tail_pts[0], "Spine")
    m.joint("Tail2", tail_pts[3], "Tail1")
    m.joint("Tail3", tail_pts[6], "Tail2")
    path = [(p, w, w * 1.04) for p, w in zip(tail_pts, widths)]
    sweep(m, "Under", [(p, w * 0.95, h * 0.95) for p, w, h in path], bones, sides=8)
    bandage(m, path, bones, rng, step=0.6)
    for k, y in ((3, 0), (6, 1)):  # gold rings on the tail
        p = tail_pts[k]
        w = widths[k]
        frame = rare_kit.frames_along(tail_pts)[k]
        a, b = Vector(p) - frame[0] * 0.2, Vector(p) + frame[0] * 0.2
        m.bone = bones[k]
        sweep(m, "Gold", [(tuple(a), w * 1.1, w * 1.14), (tuple(b), w * 1.1, w * 1.14)], sides=8)

    # Loose bandages trailing off it, swaying for ever.
    tip = Vector(tail_pts[-1])
    ends = [("Tail3", tip, Vector((0.25, -1.1, -0.9)), 1), ("Spine", Vector((-1.9, -1.8, 5.6)), Vector((-0.3, -0.5, -1.5)), 2), ("Spine", Vector((2.0, -0.2, 5.8)), Vector((0.3, -0.4, -1.5)), 3)]
    for bone, start, way, n in ends:
        pts = [start + way * t + Vector((0.12 * math.sin(t * 2), 0, -0.1 * t * t)) for t in (0, 0.7, 1.4, 2.1)]
        chain(m, "Sway", n, [tuple(p) for p in pts], 0.14, 0.1, parent=bone, role="Accent", flat="normal", breadth=0.95)
    m.bone = "Spine"

    # Tiny arms, of course: bandaged, gold cuffs, one hand gripping a tiny crook, the other a tiny flail.
    for side, letter in ((-1, "L"), (1, "R")):
        sh, el, wr = Vector((side * 2.05, 2.75, 7.5)), Vector((side * 2.3, 3.95, 6.55)), Vector((side * 1.5, 5.0, 6.8))
        m.use(f"Arm{letter}", tuple(sh))
        sweep(m, "Under", [(tuple(sh), 0.82, 0.82), (tuple(el), 0.72, 0.72), (tuple(wr), 0.6, 0.6)], sides=6)
        bandage(m, [(tuple(sh), 0.92, 0.92), (tuple(el), 0.84, 0.84), (tuple(wr), 0.7, 0.7)], [f"Arm{letter}"] * 3, rng, step=0.36, tilt=0.2)
        sweep(m, "Gold", [(tuple(wr.lerp(el, 0.12)), 0.86, 0.86), (tuple(wr), 0.86, 0.86)], sides=6)
        for dx in (-0.2, 0.2):
            sabre(m, "Claw", [tuple(wr + Vector((dx, 0.2, 0))), tuple(wr + Vector((dx, 0.56, -0.05))), tuple(wr + Vector((dx, 0.64, -0.42)))], 0.24, 4)
        if side > 0:  # the crook: gold and lapis, its hook over its shoulder
            shaft = [wr + Vector((0.45, 0.4, -1.0)), wr + Vector((-0.2, 0.3, 0.3)), wr + Vector((-0.75, 0.2, 1.5))]
            stripes(m, ("Gold", "Lapis"), [tuple(p) for p in curve(shaft, 7)], 0.26)
            hook = curve([tuple(shaft[-1]), tuple(shaft[-1] + Vector((-0.2, 0.0, 0.5))), tuple(shaft[-1] + Vector((0.35, 0.0, 0.85))), tuple(shaft[-1] + Vector((0.72, 0.0, 0.42)))], 5)
            stripes(m, ("Gold", "Lapis"), hook, 0.26)
        else:  # the flail: a short handle and three beaded strands that swing
            shaft = [wr + Vector((-0.35, 0.4, -0.9)), wr + Vector((0.1, 0.3, 0.4)), wr + Vector((0.5, 0.2, 1.3))]
            stripes(m, ("Gold", "Lapis"), [tuple(p) for p in curve(shaft, 6)], 0.26)
            top = shaft[-1]
            for n, dx in ((4, -0.3), (5, 0.08), (6, 0.42)):
                pts = [top, top + Vector((dx * 0.8, -0.1, 0.1)), top + Vector((dx * 1.6, -0.1, -0.55)), top + Vector((dx * 1.9, -0.1, -1.25))]
                chain(m, "Sway", n, [tuple(p) for p in pts], 0.14, 0.11, parent=f"Arm{letter}", role="Gold")
                egg(m, "Lapis", tuple(pts[-1]), 0.16, 0.16, 0.2, 6, 3)
    m.bone = "Spine"

    # The neck, wrapped, with a gold and lapis collar.
    m.joint("Neck", (0, 3.6, 8.9), "Spine")
    neck = [((0, 3.5, 9.0), 3.0, 3.1), ((0, 4.4, 9.8), 2.65, 2.75), ((0, 5.1, 10.45), 2.5, 2.6)]
    sweep(m, "Under", [(p, w * 0.95, h * 0.95) for p, w, h in neck], ["Spine", "Neck", "Neck"], sides=8)
    bandage(m, neck, ["Spine", "Neck", "Neck"], rng, step=0.55)
    m.bone = "Neck"
    for k, (role, grow) in enumerate((("Lapis", 0.0), ("Gold", 0.28), ("Lapis", 0.56))):
        y, z = 3.6 - grow * 0.2, 8.8 - grow * 0.6
        sweep(m, role, [((0, y + 0.16, z + 0.2), 3.3 + grow, 3.4 + grow), ((0, y - 0.1, z - 0.14), 3.45 + grow, 3.55 + grow)], sides=10)

    # The head: a gold death mask of a snout striped in lapis, burning jade eyes in black kohl under a hard gold brow.
    m.use("Head", (0, 5.35, 10.0), "Neck")
    mouth = 9.75
    snout = [((0, 5.2, 11.15), 2.9, 2.75), ((0, 6.2, 11.3), 3.5, 3.0), ((0, 7.3, 11.05), 3.3, 2.4), ((0, 8.6, 10.6), 2.75, 1.65), ((0, 9.85, 10.4), 2.5, 1.32), ((0, 10.55, 10.32), 1.9, 0.92)]
    sweep(m, "Gold", snout, sides=8)
    for y, w, h, z in ((7.95, 3.12, 2.1, 10.82), (8.85, 2.78, 1.62, 10.56), (9.7, 2.6, 1.42, 10.44)):
        sweep(m, "Lapis", [((0, y - 0.17, z), w, h), ((0, y + 0.17, z), w * 0.97, h * 0.97)], sides=8)
    sweep(m, "Mouth", [((0, 5.9, mouth + 0.02), 3.1, 0.16), ((0, 10.3, mouth + 0.02), 2.1, 0.14)], sides=8)
    egg(m, "Mouth", (0, 6.05, mouth - 0.65), 1.45, 0.5, 1.1, 8, 5)
    rngt = random.Random(5)
    for side in (-1, 1):
        for k in range(7):  # long upper teeth, biggest at the front of the cheek
            y = 6.5 + k * 0.6
            half = 1.5 - 0.09 * k
            size = (0.82 if k in (1, 2, 4) else 0.56) * (1 - 0.03 * k) + rngt.uniform(-0.04, 0.04)
            point(m, "Teeth", (side * half, y, mouth + 0.04), (side * (half - 0.06), y + 0.05, mouth - size), 0.32)
        look = (side * 0.5, 0.86, -0.05)
        egg(m, "Kohl", (side * 1.18, 7.86, 11.42), 0.7, 0.74, 0.46, 10, 5)
        slit_eye(m, (side * 1.34, 8.1, 11.4), 0.42, look, side, iris="Jade", lid_role="Kohl", top=0.42, tilt=0.55, low=0.26, slit=0.2)
        beam(m, "Gold", (side * 1.68, 7.15, 12.28), (side * 0.3, 8.55, 11.8), 0.6, 0.52, 0.34)
        beam(m, "Kohl", (side * 1.62, 7.1, 11.42), (side * 1.9, 6.15, 11.3), 0.26, 0.2, 0.12)  # the long painted line behind the eye
    for side in (-1, 1):
        egg(m, "Kohl", (side * 0.46, 10.28, 10.82), 0.2, 0.17, 0.1, 6, 3)
    egg(m, "Lapis", (0, 7.15, 12.5), 0.36, 0.32, 0.34, 8, 4)  # the jewel on its brow
    cap(m, "Jade", (0, 7.15, 12.5), 0.37, (0, 0.8, 0.5), 0.62, rings=2)

    # The royal headcloth: striped back over its skull and down either side of its neck.
    cloth = [(5.0, 3.5, 3.5, 11.3), (5.95, 3.95, 3.4, 11.4), (6.4, 3.75, 3.15, 11.5)]
    for k in range(5):
        y0, y1 = 3.9 + k * 0.5, 4.42 + k * 0.5
        w = 3.1 + 0.2 * k
        sweep(m, "Gold" if k % 2 else "Lapis", [((0, y0, 11.1), w, 3.0), ((0, y1, 11.2), w + 0.2, 3.25)], sides=10)
    for side in (-1, 1):
        top = Vector((side * 1.9, 5.5, 12.0))
        pts = [top, Vector((side * 2.8, 5.2, 11.0)), Vector((side * 2.6, 5.0, 10.1)), Vector((side * 2.05, 4.8, 9.3)), Vector((side * 1.85, 4.7, 8.65))]
        n = 7 if side < 0 else 8
        names = [f"Sway{n}a", f"Sway{n}a", f"Sway{n}b", f"Sway{n}b"]
        m.joint(f"Sway{n}a", tuple(pts[0]), "Head")
        m.joint(f"Sway{n}b", tuple(pts[2]), f"Sway{n}a")
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            m.bone = names[i]
            wa, wb = (1.7, 1.75, 1.6, 1.25)[i], (1.75, 1.6, 1.25, 0.9)[i]
            for j in range(4):
                t0, t1 = j / 4, (j + 1) / 4
                c0, c1 = a.lerp(b, t0), a.lerp(b, t1)
                w0, w1 = wa + (wb - wa) * t0, wa + (wb - wa) * t1
                d = Vector((0, 1, 0.1)).normalized()
                panel(m, "Gold" if j % 2 else "Lapis", [tuple(c0 - d * w0 / 2), tuple(c0 + d * w0 / 2), tuple(c1 + d * w1 / 2), tuple(c1 - d * w1 / 2)], 0.2)
    m.bone = "Head"

    # The jaw: bandaged, huge teeth, and on its chin a pharaoh's false beard.
    m.use("Jaw", (0, 5.9, mouth - 0.1), "Head")
    z = mouth - 0.42
    jaw = [((0, 5.9, z), 2.75, 1.0), ((0, 7.5, z - 0.02), 2.75, 0.9), ((0, 9.2, z + 0.02), 2.25, 0.74), ((0, 10.05, z + 0.08), 1.7, 0.52)]
    sweep(m, "Under", [(p, w * 0.95, h * 0.95) for p, w, h in jaw], sides=8)
    bandage(m, jaw, ["Jaw"] * 4, rng, step=0.5, tilt=0.16)
    sweep(m, "Mouth", [((0, 6.0, z + 0.48), 2.3, 0.1), ((0, 9.9, z + 0.32), 1.45, 0.1)], sides=8)
    sweep(m, "Tongue", [((0, 6.3, z + 0.56), 1.3, 0.2), ((0, 8.7, z + 0.46), 0.9, 0.16)], sides=6)
    for side in (-1, 1):
        for k in range(6):
            y = 6.9 + k * 0.56
            half = 1.26 - 0.08 * k
            size = 0.56 if k % 2 == 0 else 0.42
            point(m, "Teeth", (side * half, y, z + 0.42), (side * (half + 0.04), y + 0.03, z + 0.42 + size), 0.28)
    beard = [(0, 8.7, z - 0.36), (0, 8.8, z - 1.05), (0, 8.95, z - 1.75), (0, 9.2, z - 2.35)]
    stripes(m, ("Gold", "Lapis"), curve(beard, 8), 0.62, grow=0.05)
    swing(m, ["Jaw"], (0, 5.9, mouth - 0.1), -0.42)
    m.bone = "Head"
    m.head_centre = (0, 8.2, 10.4)
    return m


ALL = [scorchion, rexhotep]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "desert_7_8", SKY, FLOOR, GLOW_ROLES, spacing=30)


if __name__ == "__main__":
    main()
