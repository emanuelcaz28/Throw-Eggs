"""Builds the Midnight Carnival's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_midnight_carnival_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_midnight_carnival_monsters_7_8.py    (stills only)

Saves midnight_carnival_monsters_7_8.blend and renders to design/world/monsters_midnight_carnival_7_8/. What this batch shares is in rare_kit.py.

The owner's words for maps 10 to 12 (2026-11-06): "simple yet very very aggressive", with no accessories on them and no auras. So bare
bodies in two or three colours, nothing glowing, nothing floating, nothing thrown: big plain shapes, mouths, teeth, claws and small
furious eyes. The aggression is in the Maul bone (SWAY in DinoLifeController): every 2 seconds it throws itself forward, bites three
times and shakes what it caught.

  Last Laugh  a hyena gone wrong: high shoulders, a low back, a neck like a tree and a grin that goes round its head
  Unbearable  the bear that got out: huge, reared up, arms wide, a head as big as a barrel, roaring

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

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_midnight_carnival_7_8"
BLEND = "midnight_carnival_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = set()

FACE = {"EyeColour": "#ff3a22", "Pupil": "#0c0808", "Highlight": "#ffffff", "Socket": "#080506", "Mouth": "#2a0a12", "Tongue": "#8a2238", "Teeth": "#f2ead6"}
SKY, FLOOR = "#2a1630", "#5a3048"


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


# ---------------------------------------------------------------------- Last Laugh


def last_laugh():
    """A hyena, shoulders high and back sloping, thrusting a huge grinning head low in front of it."""
    m = monster("dino_LastLaugh", Body="#6a2038", Accent="#2c0f1e", Belly="#b08a6a", Claw="#120a0e")
    m.joint("Spine", (0, -4.0, 8.0))
    m.joint("Maul", (0, 2.6, 10.8), "Spine")
    m.joint("Neck", (0, 5.0, 10.6), "Maul")
    # One body from the rump to the skull, sloping up to the shoulders and down the thick neck.
    rings = [((0, -9.0, 7.6), 4.6, 4.6), ((0, -6.6, 8.0), 6.8, 6.4), ((0, -2.6, 9.0), 6.2, 6.4), ((0, 1.2, 10.2), 7.8, 8.4), ((0, 3.8, 10.6), 8.0, 8.2), ((0, 6.0, 10.5), 7.2, 7.0), ((0, 7.8, 10.5), 6.6, 6.0), ((0, 9.0, 10.8), 6.4, 5.2)]
    sweep_fine(m, "Body", rings, ["Spine", "Spine", "Spine", "Spine", "Maul", "Neck", "Neck", "Neck"], sides=16, under="Belly", under_faces=5)
    # A ridge of dark mane down its back, a low keel standing clear of the hide.
    sweep_fine(m, "Accent", [((0, -6.6, 11.1), 0.8, 0.9), ((0, -2.6, 12.4), 1.1, 1.2), ((0, 1.2, 14.7), 1.3, 1.4)], sides=6)
    m.bone = "Maul"
    sweep_fine(m, "Accent", [((0, 1.2, 14.7), 1.3, 1.4), ((0, 3.8, 15.0), 1.2, 1.3)], sides=6, per=2)
    m.bone = "Neck"
    sweep_fine(m, "Accent", [((0, 3.8, 15.0), 1.2, 1.3), ((0, 6.0, 14.3), 1.0, 1.1), ((0, 7.8, 13.7), 0.5, 0.5)], sides=6, per=2)
    m.bone = "Spine"
    for name, side, y, top, hind in (("FrontL", -1, 2.6, 8.4, False), ("FrontR", 1, 2.6, 8.4, False), ("BackL", -1, -6.4, 7.0, True), ("BackR", 1, -6.4, 7.0, True)):
        x = side * 3.2
        m.use(name, (x, y, top))
        knee = Vector((x + side * 0.3, y + (1.0 if hind else -0.8), top * 0.6))
        ankle = Vector((x + side * 0.3, y + (-1.2 if hind else 0.5), top * 0.28))
        foot = Vector((x + side * 0.3, y + 0.8, 0.5))
        egg(m, "Body", (x * 0.92, y, top + 0.7), 1.9, 3.0, 3.0, 12, 7)
        limb(m, "Body", [Vector((x, y, top)), knee, ankle, foot], (3.0, 2.1, 1.5, 1.8))
        talons(m, foot + Vector((0, 0.9, -0.1)), (0, 1, -0.3), 4, 0.6, 1.5, 0.5)
    m.bone = "Spine"
    tail = [(p, w, w) for p, w in zip(curve([(0, -8.8, 8.8), (0, -11.0, 8.0), (0, -12.6, 6.6), (0, -13.4, 5.0)], 8), (2.0, 1.9, 1.8, 1.8, 1.9, 1.9, 1.4, 0.3))]
    jointed(m, "Accent", ["Tail1", "Tail2", "Tail3"], tail)
    m.use("Head", (0, 7.8, 9.8), "Neck")
    beast_head(m, 7.6, 9.2, 8.8, 7.6, 3.8, gape=-0.72, upper="Body", lower="Accent", brow="Accent", eye=0.5, teeth=9, fang=1.1)
    for side in (-1, 1):  # round ears, flat back
        egg(m, "Accent", (side * 3.2, 8.4, 13.2), 1.1, 0.5, 1.5, 8, 5)
    m.head_centre = (0, 13.0, 9.8)
    return m


# ---------------------------------------------------------------------- Unbearable


def unbearable():
    """A huge bear reared up on its hind legs, arms wide, head low and roaring."""
    m = monster("dino_Unbearable", Body="#3a1c30", Accent="#1c0e1a", Belly="#c09a78", Claw="#0e080c")
    m.joint("Spine", (0, -2.0, 7.6))
    m.joint("Maul", (0, -0.4, 11.0), "Spine")
    m.joint("Neck", (0, 3.0, 14.2), "Maul")
    # One huge body from the hips up over the shoulders and forward into the neck.
    rings = [((0, -3.0, 5.4), 7.6, 6.6), ((0, -2.2, 7.6), 10.8, 8.8), ((0, -0.8, 10.4), 12.4, 9.4), ((0, 0.6, 12.8), 14.8, 9.8), ((0, 2.0, 14.6), 12.6, 8.6), ((0, 3.4, 15.6), 9.8, 7.4), ((0, 4.5, 15.7), 9.0, 6.8)]
    sweep_fine(m, "Body", rings, ["Spine", "Spine", "Spine", "Maul", "Maul", "Neck", "Neck"], sides=18, up=(0, -0.3, 1))
    m.bone = "Spine"
    for letter, side in (("L", -1), ("R", 1)):
        hip = Vector((side * 3.8, -2.2, 6.6))
        knee = Vector((side * 4.6, -0.4, 3.8))
        m.use(f"Leg{letter}", tuple(hip))
        limb(m, "Body", [hip, hip.lerp(knee, 0.6), knee], (6.0, 5.4, 4.2))
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        ankle = Vector((side * 4.8, -1.0, 1.2))
        limb(m, "Body", [knee, ankle], (4.2, 3.6))
        foot = Vector((side * 4.8, 0.4, 0.8))
        sweep_fine(m, "Accent", [(tuple(foot + Vector((0, -2.2, 0))), 3.6, 1.8), (tuple(foot), 4.2, 1.6), (tuple(foot + Vector((0, 2.0, -0.2))), 4.0, 1.1)], sides=10, per=2)
        talons(m, foot + Vector((0, 2.4, -0.2)), (0, 1, -0.3), 4, 0.95, 1.9, 0.7)
    for letter, side in (("L", -1), ("R", 1)):
        shoulder, elbow, wrist = Vector((side * 6.6, 1.6, 14.0)), Vector((side * 10.4, 3.4, 11.0)), Vector((side * 10.0, 8.0, 10.4))
        m.use(f"Arm{letter}", tuple(shoulder), "Maul")
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5), elbow, elbow.lerp(wrist, 0.6), wrist], (5.4, 5.0, 4.2, 3.8, 3.4), sides=12)
        hand = wrist + Vector((0, 1.0, 0))
        egg(m, "Accent", tuple(hand), 2.5, 2.0, 1.5, 10, 6)
        talons(m, hand + Vector((0, 1.4, 0)), (0, 1, -0.2), 5, 0.98, 3.4, 0.86)
    m.use("Head", (0, 4.4, 13.8), "Neck")
    beast_head(m, 4.0, 12.6, 6.8, 9.6, 5.0, gape=-0.78, upper="Body", lower="Accent", brow="Accent", eye=0.5, teeth=8, fang=1.25, throat=0.7)
    for side in (-1, 1):  # small round ears
        egg(m, "Accent", (side * 4.0, 4.4, 18.0), 1.4, 0.7, 1.4, 10, 5)
    m.head_centre = (0, 9.0, 13.8)
    return m


ALL = [last_laugh, unbearable]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "midnight_carnival_7_8", SKY, FLOOR, GLOW_ROLES, glow=0.0, spacing=48)


if __name__ == "__main__":
    main()
