"""Builds Thorn Kingdom's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_thorn_kingdom_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_thorn_kingdom_monsters_7_8.py    (stills only)

Saves thorn_kingdom_monsters_7_8.blend and renders to design/world/monsters_thorn_kingdom_7_8/. What this batch shares is in rare_kit.py.

The owner's words for maps 13 to 15 (2026-11-06): "very very aggressive", "the most aggressive", with "unique" animations. Bare bodies as on
maps 10 to 12, nothing glowing, floating or thrown; each monster has its own attack in MARKED (rare_kit.py and DinoLifeController).

  Thornado       a lean black thing with four thorned arms and a waist that turns right round: it spins on its own hips (Whirl)
  Thorn to Bits  a boar-backed brute, shoulders like a hill, a back of thorns that stand on end, tusks: rams and hooks upward (Gore)

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

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_thorn_kingdom_7_8"
BLEND = "thorn_kingdom_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = set()

FACE = {"EyeColour": "#ff3040", "Pupil": "#0c0808", "Slit": "#0c0808", "Highlight": "#ffffff", "Socket": "#060406", "Mouth": "#2a0612", "Tongue": "#a81e3e", "Teeth": "#efe6d2"}
SKY, FLOOR = "#2a1a30", "#4a3a44"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- Thornado


def thorned_arm(m, bone, parent, shoulder, elbow, wrist, widths, claw):
    """An arm with thorns up the outside of it and long hooked claws. All on one bone, so it's flung out whole."""
    s, e, w = Vector(shoulder), Vector(elbow), Vector(wrist)
    m.use(bone, tuple(s), parent)
    knob(m, "Body", s, widths[0] * 0.56)
    limb(m, "Body", [s, s.lerp(e, 0.3), s.lerp(e, 0.72), e], widths[:4], sides=12)
    knob(m, "Accent", e, widths[3] * 0.62)
    limb(m, "Accent", [e, e.lerp(w, 0.34), e.lerp(w, 0.72), w], widths[3:], sides=12)  # the arm darkens to crimson from the elbow
    side = 1 if s.x > 0 else -1
    for a, b, t in ((s, e, 0.5), (e, w, 0.15), (e, w, 0.6)):
        base = a.lerp(b, t)
        point(m, "Claw", tuple(base), tuple(base + Vector((side * 2.0, -1.0, 0.8))), 1.0)
    d = (w - e).normalized()
    egg(m, "Accent", tuple(w + d * 0.6), widths[-1] * 0.8, widths[-1] * 0.9, widths[-1] * 0.6, 10, 5)
    talons(m, w + d * 1.2, d, 3, widths[-1] * 0.6, claw, widths[-1] * 0.5)


def thornado():
    """Pinched at the waist, wide at the shoulders. The top half is its own piece turning in the hips, so it can spin for ever."""
    m = monster("dino_Thornado", Body="#2c1a3c", Accent="#86142e", Belly="#c02a42", Claw="#e8dcc0")
    m.joint("Spine", (0, 0, 10.0))
    m.joint("Whirl", (0, 0, 11.0), "Spine")
    # The hips: a bowl the waist turns in.
    sweep_fine(m, "Accent", [((0, -0.4, 8.2), 1.6, 1.4), ((0, -0.2, 9.2), 6.0, 5.0), ((0, 0, 10.6), 6.6, 5.8), ((0, 0, 11.8), 4.8, 4.6)], ["Spine"] * 4, up=(0, -1, 0.05), sides=14)
    m.bone = "Whirl"
    rings = [((0, 0, 10.4), 2.6, 2.6), ((0, 0, 12.4), 3.8, 3.8), ((0, 0.3, 14.6), 6.4, 4.6), ((0, 0.9, 17.0), 10.6, 6.0), ((0, 1.6, 19.2), 13.0, 6.4), ((0, 2.6, 20.6), 8.0, 5.0)]
    sweep_fine(m, "Body", rings, ["Whirl"] * 6, up=(0, -1, 0.1), sides=20, per=4, under="Belly", under_faces=3)
    for k, (y, z, s) in enumerate(((-1.6, 13.4, 0), (-2.2, 15.4, 1.4), (-2.2, 15.2, -1.4), (-2.2, 17.8, 2.4), (-2.2, 17.8, -2.4), (-1.8, 19.8, 3.6), (-1.8, 19.8, -3.6), (-1.0, 21.0, 1.4), (-1.0, 21.0, -1.4))):
        base = Vector((s, y + 0.8, z))
        point(m, "Claw", tuple(base), tuple(base + Vector((s * 0.5, -3.0, 1.2 + 0.1 * k))), 1.5)
    for letter, side in (("L", -1), ("R", 1)):
        thorned_arm(m, f"Arm{letter}", "Whirl", (side * 6.2, 1.6, 19.2), (side * 11.2, 1.0, 13.4), (side * 9.8, 7.4, 7.6), (3.4, 3.6, 2.2, 2.0, 2.3, 1.7, 1.3), 5.2)
        thorned_arm(m, f"Wing{letter}", "Whirl", (side * 4.0, 1.4, 15.6), (side * 8.2, 2.4, 13.0), (side * 7.0, 7.6, 12.6), (2.1, 2.2, 1.4, 1.3, 1.5, 1.1, 0.9), 3.6)
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee, hock = Vector((side * 2.6, 0, 9.6)), Vector((side * 3.8, 3.0, 6.2)), Vector((side * 4.0, -1.2, 3.0))
        foot = Vector((side * 4.2, 0.6, 0.6))
        m.use(f"Leg{letter}", tuple(hip))
        limb(m, "Accent", [hip, hip.lerp(knee, 0.5), knee], (3.2, 2.6, 1.9))
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        limb(m, "Accent", [knee, hock, foot, foot + Vector((0, 2.0, -0.1))], (1.8, 1.3, 1.3, 1.6))
        talons(m, foot + Vector((0, 2.0, 0)), (0, 1, -0.1), 3, 0.8, 1.8, 0.62)
    m.use("Neck", (0, 2.6, 20.2), "Whirl")
    sweep_fine(m, "Body", [((0, 2.0, 20.4), 6.0, 4.6), ((0, 3.6, 20.2), 4.4, 3.6), ((0, 5.0, 19.9), 4.0, 3.2)], ["Whirl", "Neck", "Neck"], sides=12)
    m.use("Head", (0, 4.8, 19.4), "Neck")
    skull = [(0, 0.72, 0.0, 0.9), (0.18, 1.0, 0.0, 1.2), (0.4, 0.84, 0.0, 1.3), (0.62, 0.52, 0.0, 0.84), (0.86, 0.36, 0.0, 0.54), (1.0, 0.16, 0.04, 0.24)]
    jaw = [(0, 0.74, -0.5, 0.0), (0.3, 0.72, -0.44, 0.0), (0.62, 0.46, -0.36, 0.0), (0.9, 0.3, -0.28, 0.0), (1.0, 0.14, -0.18, -0.02)]
    at = fierce_head(m, 4.6, 18.9, 8.8, 7.6, 3.2, skull, jaw, gape=-0.82, teeth=(10, 9), tall=1.15, base=0.36, fangs=((0.76, 2.3),), low_fangs=((0.8, 1.7),), seed=11, lower_inset=0.58)
    for side in (-1, 1):
        a_ = 0.8 if side > 0 else math.pi - 0.8
        eye(m, at(0.47, a_), 0.56, (side * 0.3, 0.93, -0.1), side, socket=1.8)
        eye(m, at(0.27, a_ - side * 0.1), 0.3, (side * 0.72, 0.68, 0), side, socket=1.7, pupil="Slit", ridge=None)  # a spare, further back
    # A crown of thorns, thrown back from the skull, not quite even. They fan out wider than the head, so it reads from far off.
    for side, x, y, tip in ((1, 0.6, 7.0, (1.4, 1.0, 26.6)), (-1, -0.6, 7.2, (-1.2, 2.2, 27.8)), (1, 1.8, 6.6, (4.6, 1.4, 25.8)), (-1, -1.9, 6.4, (-5.2, 0.4, 25.2)), (1, 2.9, 6.0, (7.4, 1.8, 23.4)), (-1, -3.0, 6.0, (-7.0, 2.4, 22.8)), (1, 0.0, 5.6, (0.2, -1.4, 26.0))):
        horn(m, "Claw", (x, y, 21.6), tip, 1.1, droop=-0.3)
    m.head_centre = (0, 12.5, 19.6)
    on_the_floor(m)
    return m


# ---------------------------------------------------------------------- Thorn to Bits


def thorn_to_bits():
    """All shoulder, its head hung low in front of it, tusks hooked up, thorns laid flat along its back until it charges."""
    m = monster("dino_ThornToBits", Body="#641628", Accent="#1a0e16", Belly="#a83a48", Claw="#ece0c4")
    m.joint("Spine", (0, -6.0, 8.6))
    m.joint("Gore", (0, 3.0, 11.0), "Spine")
    m.joint("Neck", (0, 8.0, 10.6), "Gore")
    rings = [((0, -13.0, 8.6), 3.0, 3.0), ((0, -11.6, 9.4), 9.4, 8.0), ((0, -7.0, 10.0), 12.0, 9.6), ((0, -1.0, 11.4), 14.0, 12.0), ((0, 3.4, 12.6), 16.0, 14.0), ((0, 7.0, 11.8), 13.0, 11.0), ((0, 9.8, 10.2), 10.0, 7.8), ((0, 11.6, 9.4), 8.6, 6.0)]
    sweep_fine(m, "Body", rings, ["Spine", "Spine", "Spine", "Spine", "Gore", "Gore", "Neck", "Neck"], sides=22, under="Belly", under_faces=7, per=4)
    # The thorns, on a bone each so they can stand up: laid back along the spine at rest.
    for n, (y, z, side) in enumerate(((7.6, 17.0, 0), (5.0, 19.0, 0), (2.2, 19.0, 0), (-0.8, 17.4, 0), (-3.6, 15.8, 0), (-6.2, 14.6, 0), (-8.6, 14.0, 0), (-10.8, 13.0, 0)), 1):
        m.joint(f"Quill{n}", (0, y, z - 1.2), "Gore" if n <= 3 else "Spine")
        m.bone = f"Quill{n}"
        for x, long in ((0, 11.0), (-3.2, 8.0), (3.2, 8.0), (-6.0, 5.4), (6.0, 5.4)):
            base = Vector((x, y, z - 2.2 - x * x * 0.1))
            sabre(m, "Claw", [tuple(base), tuple(base + Vector((x * 0.5, -long * 0.4, long * 0.42))), tuple(base + Vector((x * 1.0, -long, long * 0.62)))], 1.9, 7)
    for name, x, y, z, front in (("FrontL", -6.4, 5.4, 9.0, True), ("FrontR", 6.4, 5.4, 9.0, True), ("BackL", -5.4, -8.4, 8.0, False), ("BackR", 5.4, -8.4, 8.0, False)):
        side = 1 if x > 0 else -1
        m.use(name, (x, y, z), "Gore" if front else "Spine")
        knob(m, "Body", (x * 0.92, y, z + 2.4), 4.0 if front else 3.8)  # shoulders and haunches, under the skin
        limb(m, "Body", [Vector((x, y, z + 2.0)), Vector((x, y + 0.2, z - 1.0)), Vector((x + side * 0.6, y + 0.6, z - 2.8))], (7.4, 6.2, 4.6), sides=14)
        knee = Vector((x + side * 1.2, y + (1.4 if front else -2.2), z - 4.0))
        foot = Vector((x + side * 1.4, y + (1.0 if front else -0.8), 0.9))
        limb(m, "Accent", [Vector((x, y, z - 1.6)), knee, knee.lerp(foot, 0.6), foot], (4.6, 3.6, 2.5, 2.9), sides=14)
        egg(m, "Accent", tuple(foot + Vector((0, 0.6, -0.2))), 2.0, 2.2, 0.8, 10, 5)
        talons(m, foot + Vector((0, 2.0, -0.2)), (0, 1, -0.3), 3, 1.2, 2.0, 0.8)
    m.bone = "Spine"
    path = [(p, w, w) for p, w in zip(curve([(0, -12.0, 9.4), (0, -15.0, 9.8), (0, -18.0, 11.0), (1.0, -20.4, 12.6)], 8), (5.0, 4.0, 3.2, 2.6, 2.0, 1.4, 0.9, 0.2))]
    jointed(m, "Accent", ["Tail1", "Tail2", "Tail3"], path, sides=10)
    m.use("Head", (0, 10.8, 8.8), "Neck")
    skull = [(0, 0.86, 0.0, 1.1), (0.22, 1.0, 0.0, 1.4), (0.46, 0.86, 0.0, 1.2), (0.7, 0.62, 0.0, 0.84), (0.9, 0.56, 0.0, 0.74), (0.97, 0.58, 0.0, 0.76), (1.0, 0.4, 0.1, 0.52)]
    jaw = [(0, 0.84, -0.7, 0.0), (0.34, 0.8, -0.62, 0.0), (0.66, 0.58, -0.5, 0.0), (0.92, 0.48, -0.36, 0.0), (1.0, 0.24, -0.24, -0.02)]
    at = fierce_head(m, 10.6, 8.2, 9.6, 10.4, 4.4, skull, jaw, gape=-0.5, teeth=(9, 8), tall=1.5, base=0.56, fangs=((0.6, 1.9),), seed=12)
    egg(m, "Accent", (0, 20.0, 8.2 + 4.4 * 0.4), 3.3, 0.8, 1.9, 14, 6)  # the flat end of a boar's snout
    for side in (-1, 1):
        egg(m, "Socket", (side * 1.25, 20.62, 8.2 + 4.4 * 0.36), 0.36, 0.24, 0.72, 10, 5)
        a_ = 0.74 if side > 0 else math.pi - 0.74
        eye(m, at(0.5, a_), 0.6, (side * 0.26, 0.95, -0.12), side, socket=1.8, ridge_size=1.15)
        ear = at(0.12, 0.95 if side > 0 else math.pi - 0.95)
        horn(m, "Body", tuple(ear), tuple(ear + Vector((side * 3.2, -2.6, 2.6))), 2.2, droop=0.3)
    m.bone = "Head"
    for side in (-1, 1):  # short tusks over the lip, as well as the big pair
        horn(m, "Claw", (side * 2.6, 18.6, 9.0), (side * 4.6, 19.6, 11.6), 0.9, droop=0.3)
    m.head_centre = (0, 27.0, 10.2)
    on_the_floor(m)
    return m


ALL = [thornado, thorn_to_bits]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "thorn_kingdom_7_8", SKY, FLOOR, GLOW_ROLES, glow=0.0, spacing=56)


if __name__ == "__main__":
    main()
