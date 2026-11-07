"""Builds Clockwork Citadel's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_clockwork_citadel_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_clockwork_citadel_monsters_7_8.py    (stills only)

Saves clockwork_citadel_monsters_7_8.blend and renders to design/world/monsters_clockwork_citadel_7_8/. What this batch shares is in rare_kit.py.

The owner's words for maps 10 to 12 (2026-11-06): "simple yet very very aggressive", with no accessories on them and no auras. So bare
bodies in two or three colours, nothing glowing, nothing floating, nothing thrown: big plain shapes, mouths, teeth, claws and small
furious eyes. The aggression is in the Maul bone (SWAY in DinoLifeController): every 2 seconds it throws itself forward, bites three
times and shakes what it caught.

  Tick-Tock   a tick the size of a car, a bloated bronze body on eight hooked legs and a small head that is nothing but jaws
  Clockodile  a crocodile, long, low and heavy, plated in dark iron, a third of it jaw

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
from build_forest import Model  # noqa: E402
from build_spore_hollow_monsters import egg  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from rare_kit import beast_head, curve, jointed, ring_round, sabre, slit_eye, sweep, sweep_fine, swing  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_clockwork_citadel_7_8"
BLEND = "clockwork_citadel_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = set()

FACE = {"EyeColour": "#ffb020", "Pupil": "#0c0808", "Highlight": "#ffffff", "Socket": "#080506", "Mouth": "#2a0a12", "Tongue": "#8a2238", "Teeth": "#f2ead6"}
SKY, FLOOR = "#3a2a20", "#6a5444"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


def limb(m, role, points, widths, sides=10):
    """A leg or an arm through points, thick to thin, smoothed."""
    sweep_fine(m, role, [(tuple(p), w, w) for p, w in zip(points, widths)], sides=sides, per=3)


def talons(m, at, ahead, count, spread, length, width):
    """Long curved claws out of a hand or foot at `at`, hooking down."""
    c, d = Vector(at), Vector(ahead).normalized()
    for k in range(count):
        o = Vector((spread * (k - (count - 1) / 2), 0, 0))
        base = c + o
        sabre(m, "Claw", [tuple(base), tuple(base + d * length * 0.6 + o * 0.15 + Vector((0, 0, 0.1))), tuple(base + d * length + o * 0.25 - Vector((0, 0, length * 0.5)))], width, 6)


# ---------------------------------------------------------------------- Tick-Tock


def tick_leg(m, bone, side, y, spread, foot_y):
    hip = Vector((side * 5.4, y, 5.4))
    knee = Vector((side * spread, y + (foot_y - y) * 0.45, 8.6))
    foot = Vector((side * (spread + 3.0), foot_y, 0.1))
    m.use(bone, tuple(hip))
    limb(m, "Accent", [hip, hip.lerp(knee, 0.5) + Vector((0, 0, 0.5)), knee, knee.lerp(foot, 0.5), knee.lerp(foot, 0.82)], (2.2, 2.0, 1.6, 1.2, 0.9))
    sabre(m, "Claw", [tuple(knee.lerp(foot, 0.72)), tuple(knee.lerp(foot, 0.9)), tuple(foot + Vector((0, 0.6, 0)))], 1.5, 6)
    m.bone = "Spine"


def tick_tock():
    """A bloated giant tick on eight hooked legs, its small head all jaws."""
    m = monster("dino_TickTock", Body="#7a4a24", Accent="#2a1c14", Belly="#b07a3a", Claw="#120c08")
    m.joint("Spine", (0, -2.0, 6.0))
    sweep_fine(m, "Body", [((0, -12.0, 7.0), 3.0, 2.4), ((0, -9.6, 7.0), 11.0, 9.4), ((0, -5.0, 7.2), 16.0, 12.4), ((0, 0.0, 7.0), 16.4, 11.6), ((0, 3.4, 6.6), 11.0, 8.2), ((0, 5.0, 6.4), 4.0, 3.4)], sides=16, under="Belly", under_faces=5, per=3)
    for name, y, spread, foot_y in (("Front", 3.0, 12.0, 8.6), ("Arm", 0.6, 13.6, 3.2), ("Wing", -2.6, 13.6, -3.6), ("Back", -5.6, 12.0, -10.0)):
        for letter, side in (("L", -1), ("R", 1)):
            tick_leg(m, name + letter, side, y, spread, foot_y)
    m.joint("Maul", (0, 3.6, 6.8), "Spine")
    m.joint("Neck", (0, 6.6, 6.7), "Maul")
    sweep_fine(m, "Accent", [((0, 2.0, 7.0), 8.0, 6.4), ((0, 3.8, 7.1), 9.6, 7.0), ((0, 5.6, 7.1), 8.2, 6.0), ((0, 7.0, 7.3), 6.2, 4.8), ((0, 8.2, 7.6), 5.6, 4.2)], ["Maul", "Maul", "Maul", "Neck", "Neck"], sides=14)
    m.use("Head", (0, 7.8, 6.6), "Neck")
    beast_head(m, 7.6, 5.8, 7.0, 6.8, 3.4, gape=-0.76, upper="Accent", lower="Accent", brow="Body", eye=0.44, teeth=8, fang=1.25)
    m.head_centre = (0, 11.0, 6.6)
    return m


# ---------------------------------------------------------------------- Clockodile


def clockodile():
    """A long low crocodile in dark iron, its jaws a third of it, hanging wide."""
    m = monster("dino_Clockodile", Body="#3c4650", Accent="#1c2228", Belly="#b08a3e", Claw="#0e1014")
    m.joint("Spine", (0, -5.0, 4.6))
    m.joint("Maul", (0, 2.4, 4.8), "Spine")
    m.joint("Neck", (0, 4.8, 4.9), "Maul")
    # One long low body from the tail to the skull, rising a little to the head.
    sweep_fine(m, "Body", [((0, -10.0, 4.4), 7.0, 4.4), ((0, -6.0, 4.8), 10.4, 5.6), ((0, -1.0, 4.9), 11.0, 5.8), ((0, 2.4, 5.0), 9.8, 5.4), ((0, 4.8, 5.4), 8.8, 5.0), ((0, 6.8, 6.1), 8.2, 4.4), ((0, 8.0, 6.7), 8.0, 3.8)],
               ["Spine", "Spine", "Spine", "Maul", "Maul", "Neck", "Neck"], sides=16, under="Belly", under_faces=5)
    for row, y in enumerate((-8.6, -6.2, -3.8, -1.4, 1.0)):  # two low rows of scutes: the crocodile's own hide
        for side in (-1, 1):
            top = 7.1 - 0.02 * y * y
            point(m, "Accent", (side * 1.7, y + 0.5, top), (side * 1.8, y - 0.3, top + 1.0), 1.7)
    for name, side, y, front in (("FrontL", -1, 1.0, True), ("FrontR", 1, 1.0, True), ("BackL", -1, -7.6, False), ("BackR", 1, -7.6, False)):
        x = side * 4.8
        m.use(name, (x, y, 4.0))
        knee = Vector((x + side * 2.8, y + 0.4, 3.4))
        foot = Vector((x + side * 4.0, y + 1.4, 0.7))
        limb(m, "Body", [Vector((x, y, 4.0)), knee, foot], (3.6, 2.8, 2.4))
        egg(m, "Body", tuple(foot + Vector((0, 0.6, -0.2))), 1.7, 2.0, 0.7, 10, 5)
        talons(m, foot + Vector((0, 1.8, -0.2)), (0, 1, -0.3), 4, 0.8, 1.7, 0.6)
    m.bone = "Spine"
    path = [(p, w, w * 0.66) for p, w in zip(curve([(0, -9.6, 4.4), (0, -13.2, 3.9), (0, -17.0, 3.3), (1.6, -21.0, 2.6), (3.2, -25.0, 1.9), (2.8, -28.6, 1.2)], 12), (7.4, 6.8, 6.0, 5.2, 4.4, 3.7, 3.0, 2.4, 1.8, 1.3, 0.8, 0.2))]
    bones = jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], path, sides=12, under="Belly", under_faces=5)
    for i, (p, w, _) in enumerate(path[:-2]):  # the ridge down its tail
        m.bone = bones[i]
        base = Vector(p) + Vector((0, 0, w * 0.3))
        point(m, "Accent", tuple(base), tuple(base + Vector((0, -0.8, 0.9 * (1 - i / 12) + 0.2))), 1.3 * (1 - i / 14))
    m.use("Head", (0, 6.6, 5.8), "Neck")
    beast_head(m, 6.4, 5.8, 15.0, 8.6, 2.8, gape=-0.36, upper="Body", lower="Body", brow="Accent", eye=0.46, teeth=13, fang=1.3)
    m.head_centre = (0, 15.0, 6.2)
    return m


ALL = [tick_tock, clockodile]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "clockwork_citadel_7_8", SKY, FLOOR, GLOW_ROLES, glow=0.0, spacing=48)


if __name__ == "__main__":
    main()
