"""Builds The Weeping Dark's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_weeping_dark_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_weeping_dark_monsters_7_8.py    (stills only)

Saves weeping_dark_monsters_7_8.blend and renders to design/world/monsters_weeping_dark_7_8/. What this batch shares is in rare_kit.py.

The owner's words for maps 13 to 15 (2026-11-06): "very very aggressive", "the most aggressive", with "unique" animations. Bare bodies as on
maps 10 to 12, nothing glowing, floating or thrown; each monster has its own attack in MARKED (rare_kit.py and DinoLifeController).

  Inconsolable  a hunched colossus, arms like tree trunks, a mouth open in one long scream: hammers the ground with both fists and never stops (Pummel)
  Last Breath   the last monster of all: a starved thing on stilts, a neck that shouldn't stretch and does (Reach1 to 12)

The map's rule: no colour. Black, ash and bone; red only for eyes.

Skin roles Body, Accent, Belly and Claw take the colour mutations. Built at the first map's size. 1 Blender unit = 1 stud, models face
+Y, feet on Z = 0.
"""
import math
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402  (first: it turns the stud preview off)
from build_clockwork_citadel_monsters_7_8 import limb, talons  # noqa: E402
from build_forest import Model  # noqa: E402
from build_spore_hollow_monsters import egg  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from fierce_kit import eye, fierce_head, horn, knob  # noqa: E402
from rare_kit import curve, jointed, on_the_floor, sabre, sweep, sweep_fine  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_weeping_dark_7_8"
BLEND = "weeping_dark_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = set()

FACE = {"EyeColour": "#ff1a1a", "Pupil": "#050505", "Slit": "#050505", "Highlight": "#ffffff", "Socket": "#030303", "Mouth": "#070708", "Tongue": "#55555c", "Teeth": "#e8e4d8"}
SKY, FLOOR = "#25252a", "#46464c"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- Inconsolable


def inconsolable():
    """Shoulders higher than its head, short bent legs, fists on the ground in front of it."""
    m = monster("dino_Inconsolable", Body="#3e3e46", Accent="#17171a", Belly="#aaa8a0", Claw="#e8e4d8")
    m.joint("Spine", (0, -5.0, 9.0))
    m.joint("Pummel", (0, 0.0, 14.0), "Spine")
    m.joint("Neck", (0, 5.0, 16.0), "Pummel")
    rings = [((0, -8.6, 7.0), 3.0, 3.0), ((0, -7.6, 8.0), 9.0, 8.0), ((0, -5.0, 10.4), 12.0, 10.0), ((0, -2.0, 14.0), 15.0, 12.0), ((0, 1.0, 17.6), 21.0, 14.0), ((0, 4.0, 18.0), 19.0, 11.0), ((0, 6.4, 16.8), 11.0, 8.0), ((0, 8.2, 15.8), 8.4, 6.6)]
    sweep_fine(m, "Body", rings, ["Spine", "Spine", "Spine", "Pummel", "Pummel", "Pummel", "Neck", "Neck"], up=(0, -0.5, 1), sides=22, per=4, under="Belly", under_faces=7)
    for k, (y, z, tall) in enumerate(((-7.0, 13.2, 3.4), (-4.4, 16.6, 4.4), (-1.6, 20.6, 5.4), (1.0, 24.6, 6.4), (3.8, 23.8, 5.2))):  # the knobs of its spine
        m.bone = "Spine" if k < 2 else "Pummel"
        point(m, "Claw", (0, y + 0.4, z - 1.2), (0, y - 1.4, z + tall), 2.0)
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee = Vector((side * 4.6, -6.0, 8.4)), Vector((side * 6.6, -2.8, 5.0))
        foot = Vector((side * 6.8, -5.0, 0.9))
        m.use(f"Leg{letter}", tuple(hip))
        limb(m, "Accent", [hip, hip.lerp(knee, 0.5), knee], (5.4, 4.6, 3.6), sides=14)
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        limb(m, "Accent", [knee, knee.lerp(foot, 0.5), foot, foot + Vector((0, 2.4, -0.1))], (3.4, 2.8, 2.6, 2.6), sides=14)
        talons(m, foot + Vector((0, 2.6, 0)), (0, 1, -0.1), 3, 1.0, 1.8, 0.7)
        shoulder, elbow, wrist = Vector((side * 10.6, 1.4, 18.0)), Vector((side * 15.0, 3.4, 11.0)), Vector((side * 12.0, 11.0, 3.4))
        m.use(f"Arm{letter}", tuple(shoulder), "Pummel")
        knob(m, "Body", shoulder, 5.4)
        for dx, dy, dz, tall in ((3.0, -1.4, 3.8, 4.4), (4.6, 0.4, 1.6, 3.4), (1.0, -2.6, 4.6, 3.6)):  # spikes through the shoulder
            base = shoulder + Vector((side * dx, dy, dz))
            point(m, "Claw", tuple(base - Vector((side * 0.6, 0, 0.8))), tuple(base + Vector((side * tall * 0.7, -tall * 0.4, tall * 0.8))), 2.0)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5), elbow], (8.0, 7.0, 5.0), sides=18)
        m.joint(f"Fore{letter}", tuple(elbow), f"Arm{letter}")
        m.bone = f"Fore{letter}"
        limb(m, "Accent", [elbow, elbow.lerp(wrist, 0.3), elbow.lerp(wrist, 0.7), wrist], (5.0, 6.8, 7.0, 4.8), sides=18)
        for u, tall in ((0.3, 2.6), (0.56, 3.0)):  # bone through the back of the forearm
            base = elbow.lerp(wrist, u) + Vector((side * 2.4, -1.4, 1.0))
            point(m, "Claw", tuple(base), tuple(base + Vector((side * tall * 0.7, -tall * 0.5, tall * 0.5))), 1.5)
        egg(m, "Accent", tuple(wrist + Vector((0, 0.8, -0.4))), 4.0, 4.0, 3.0, 16, 8)  # a fist
        talons(m, wrist + Vector((0, 3.8, -0.2)), (0, 1, -0.45), 4, 1.5, 2.2, 0.9)
    m.use("Head", (0, 7.8, 14.6), "Neck")
    skull = [(0, 0.82, 0.0, 1.0), (0.25, 1.0, 0.0, 1.24), (0.5, 0.92, 0.0, 1.2), (0.72, 0.78, 0.0, 0.74), (0.92, 0.7, 0.0, 0.5), (1.0, 0.4, 0.06, 0.3)]
    jaw = [(0, 0.86, -0.7, 0.0), (0.4, 0.92, -0.66, 0.0), (0.75, 0.84, -0.56, 0.0), (0.96, 0.62, -0.42, 0.0), (1.0, 0.3, -0.26, -0.02)]
    at = fierce_head(m, 7.6, 14.0, 8.8, 13.0, 5.6, skull, jaw, gape=-0.86, teeth=(9, 8), tall=1.9, base=0.76, fangs=((0.58, 1.8),), low_fangs=((0.74, 2.6),), seed=31, jaw_length=1.1, throat=1.05, t0=0.32)
    for side in (-1, 1):
        a_ = 0.84 if side > 0 else math.pi - 0.84
        eye(m, at(0.7, a_), 0.62, (side * 0.14, 0.96, -0.16), side, socket=2.0, tilt=0.6, ridge=None, sink=0.7)
        for t0, drop in ((0.72, 0.22), (0.74, 0.42)):  # the lines its crying has worn down its face, lying in the skin
            line = [at(t0 + 0.06 * k, (a_ - side * (drop + 0.16 * k))) for k in range(4)]
            sweep_fine(m, "Belly", [(tuple(p), w, w) for p, w in zip(line, (0.34, 0.42, 0.34, 0.12))], sides=6, per=2)
        egg(m, "Socket", tuple(at(0.93, 1.32 if side > 0 else math.pi - 1.32)), 0.34, 0.3, 0.2, 8, 4)
    # One shelf of brow, right across, sagging at both ends.
    sweep_fine(m, "Accent", [((-6.4, 11.8, 19.2), 0.8, 0.8), ((-4.8, 13.0, 20.5), 2.8, 2.2), ((-2.0, 13.7, 19.8), 3.0, 2.2), ((0, 14.1, 18.7), 2.6, 1.8), ((2.0, 13.7, 19.8), 3.0, 2.2), ((4.8, 13.0, 20.5), 2.8, 2.2), ((6.4, 11.8, 19.2), 0.8, 0.8)], sides=10, per=3)
    m.head_centre = (0, 24.0, 16.0)
    on_the_floor(m)
    return m


# ---------------------------------------------------------------------- Last Breath


def last_breath():
    """Ribs and stilts, its neck in one high arch, and at the end of it a thin skull held low, looking straight at you."""
    m = monster("dino_LastBreath", Body="#26262c", Accent="#0e0e10", Belly="#d6d1c2", Claw="#ece8dc")
    m.joint("Spine", (0, -5.0, 19.0))
    m.joint("Neck", (0, 2.6, 21.0), "Spine")
    route = curve([(0, 3.0, 21.0), (0, 5.0, 25.6), (0, 8.0, 28.4), (0, 11.4, 28.0), (0, 13.6, 24.8), (0, 14.4, 21.0), (0, 14.8, 18.6)], 13)
    names = ["Neck"] + [f"Reach{n}" for n in range(1, 13)]
    for k in range(1, 13):  # a bone for each ring, so it pulls out smooth as a rope
        m.joint(names[k], route[k], names[k - 1])
    rings = [((0, -13.0, 18.4), 2.0, 2.0), ((0, -11.0, 18.8), 7.0, 6.0), ((0, -6.0, 19.6), 8.4, 7.4), ((0, -2.0, 19.4), 6.2, 7.0), ((0, 1.0, 20.0), 9.4, 8.6), ((0, 3.2, 21.0), 7.0, 6.0)]
    sweep_fine(m, "Body", rings, ["Spine", "Spine", "Spine", "Spine", "Spine", "Neck"], sides=14)
    for y in (-8.4, -6.0, -3.6, -1.2, 1.0):  # ribs, standing out of it
        m.bone = "Spine"
        w = 4.6 if -4 < y else 4.8
        for side in (-1, 1):
            sabre(m, "Belly", [(0, y, 23.4), (side * w, y, 21.0), (side * (w + 0.4), y + 0.2, 18.2), (side * (w - 1.2), y + 0.4, 15.8)], 1.1, 10)
    sweep(m, "Body", [(p, 5.6 - 2.6 * i / 12, 5.6 - 2.6 * i / 12) for i, p in enumerate(route)], names, sides=14, caps=(False, True))
    for k, (y, z) in zip((2, 5, 8, 11), ((5.0, 27.2), (8.0, 30.0), (11.6, 29.6), (14.6, 25.4))):  # the knobs of its neck
        m.bone = names[k]
        point(m, "Claw", (0, y - 0.6, z - 1.0), (0, y - 1.2, z + 1.6), 1.0)
    for name, x, y, front in (("FrontL", -3.6, 0.6, True), ("FrontR", 3.6, 0.6, True), ("BackL", -3.2, -9.6, False), ("BackR", 3.2, -9.6, False)):
        side = 1 if x > 0 else -1
        m.use(name, (x, y, 20.0))
        knee = Vector((x + side * 7.0, y + (2.6 if front else -3.6), 25.0))
        ankle = Vector((x + side * 10.0, y + (6.4 if front else -2.0), 8.0))
        foot = Vector((x + side * 9.6, y + (7.8 if front else -0.8), 0.5))
        knob(m, "Accent", (x, y, 20.0), 2.2)
        limb(m, "Accent", [Vector((x, y, 20.0)), Vector((x, y, 20.0)).lerp(knee, 0.5), knee, knee.lerp(ankle, 0.5), ankle, foot], (3.6, 2.4, 2.6, 1.3, 1.7, 1.2))
        talons(m, foot + Vector((0, 0.6, 0)), (0, 1, -0.2), 3, 0.7, 2.4, 0.6)
    m.bone = "Spine"
    path = [(p, w, w) for p, w in zip(curve([(0, -11.6, 18.8), (0, -15.0, 17.2), (0, -18.6, 13.6), (0, -21.0, 8.4)], 8), (3.6, 2.8, 2.2, 1.7, 1.3, 0.9, 0.6, 0.15))]
    jointed(m, "Accent", ["Tail1", "Tail2", "Tail3"], path, sides=8)
    m.joint("Head", (0, 14.8, 18.6), "Reach12")
    m.bone = "Head"
    # Nothing left on it but bone: a long, thin animal's skull, no skin, no gums.
    skull = [(0, 0.7, 0.0, 1.0), (0.18, 1.0, 0.0, 1.4), (0.38, 0.92, 0.0, 1.5), (0.56, 0.5, 0.0, 1.0), (0.78, 0.36, 0.0, 0.7), (0.95, 0.34, 0.0, 0.46), (1.0, 0.16, 0.04, 0.26)]
    jaw = [(0, 0.66, -0.5, 0.0), (0.3, 0.56, -0.36, 0.0), (0.62, 0.36, -0.28, 0.0), (0.9, 0.3, -0.24, 0.0), (1.0, 0.14, -0.16, -0.02)]
    at = fierce_head(m, 13.6, 16.6, 11.4, 7.0, 3.2, skull, jaw, gape=-0.76, upper="Belly", gums=None, teeth=(11, 10), tall=1.45, base=0.42, fangs=((0.7, 1.8),), tongue=False, seed=6)
    for side in (-1, 1):  # holes far too big for the eyes in them
        spot = at(0.42, 0.8 if side > 0 else math.pi - 0.8)
        eye(m, spot, 0.42, (side * 0.26, 0.95, -0.1), side, socket=2.7, lid="Belly", top=0.3, tilt=0.7, low=0.16, slit=0.34, sink=1.2, ridge="Belly", ridge_size=1.5, proud=0.15)
        horn(m, "Belly", tuple(at(0.2, 1.0 if side > 0 else math.pi - 1.0)), (side * 6.6, 7.2, 25.6), 2.0, droop=-1.6, count=9)  # horns, swept back
        slit = [at(0.64, 1.36 if side > 0 else math.pi - 1.36), at(0.74, 1.1 if side > 0 else math.pi - 1.1), at(0.86, 0.84 if side > 0 else math.pi - 0.84)]  # the slits where a nose was
        sweep_fine(m, "Socket", [(tuple(p), w, w) for p, w in zip(slit, (0.14, 0.62, 0.2))], sides=6, per=2)
    m.head_centre = (0, 26.0, 18.0)
    on_the_floor(m)
    return m


ALL = [inconsolable, last_breath]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "weeping_dark_7_8", SKY, FLOOR, GLOW_ROLES, glow=0.0, spacing=56)


if __name__ == "__main__":
    main()
