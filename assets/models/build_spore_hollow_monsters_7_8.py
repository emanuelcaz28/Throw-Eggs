"""Builds Spore Hollow's 7th and 8th monsters, animates them and renders them (Blender, background mode).

SUPERSEDED 2026-11-10: the owner had all 8 redesigned ("toxic themed"); the monsters in the game come from
build_spore_hollow_toxic.py. This file stays for the helpers other scripts import (egg, vent, finish, pounce_of) and is not exported.

    Blender -b -P build_spore_hollow_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_spore_hollow_monsters_7_8.py    (stills only)

Saves spore_hollow_monsters_7_8.blend and renders to design/world/monsters_spore_hollow_7_8/. What this batch shares is in rare_kit.py.

The owner's words for maps 13 to 15 (2026-11-06): "very very aggressive", "the most aggressive", with "unique" animations. Bare bodies as on
maps 10 to 12, nothing glowing, floating or thrown; each monster has its own attack in MARKED (rare_kit.py and DinoLifeController).

  Mouth Breather  a body that's nothing but a mouth, on four short claws: leaps with its skull flung right back and lands jaws first (Gulp)
  Spore Loser     a gaunt thing on folded hopper's legs that can't keep still: ricochets left, right and ahead, biting each time it lands (Bounce)

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
from fierce_kit import band, eye, fierce_head, horn, knob  # noqa: E402
from rare_kit import curve, jointed, on_the_floor, sabre, sweep, sweep_fine  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_spore_hollow_7_8"
BLEND = "spore_hollow_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = set()

FACE = {"EyeColour": "#c8e020", "Pupil": "#0c0808", "Slit": "#0c0808", "Highlight": "#ffffff", "Socket": "#060604", "Mouth": "#201408", "Tongue": "#7c8e1c", "Teeth": "#e6dfc0"}
SKY, FLOOR = "#2a2614", "#4a4228"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- Mouth Breather


def mouth_breather():
    """One huge head and a small rump behind it. Everything else is jaw."""
    m = monster("dino_MouthBreather", Body="#352c12", Accent="#16120a", Belly="#a39868", Claw="#ece4bc")
    m.joint("Spine", (0, -6.0, 8.0))
    m.joint("Gulp", (0, -3.0, 10.0), "Spine")
    m.joint("Neck", (0, -1.0, 10.4), "Gulp")
    m.joint("Head", (0, 1.0, 10.4), "Neck")
    rings = [((0, -13.4, 8.4), 3.0, 3.0), ((0, -12.0, 9.0), 10.0, 9.0), ((0, -8.0, 10.0), 15.0, 12.4), ((0, -4.0, 11.0), 17.0, 13.4), ((0, -1.0, 12.4), 18.6, 14.0), ((0, 2.6, 13.6), 19.0, 12.0), ((0, 5.0, 14.2), 16.0, 8.0)]
    sweep_fine(m, "Body", rings, ["Spine", "Spine", "Spine", "Gulp", "Gulp", "Head", "Head"], sides=22, under="Belly", under_faces=7, per=4)
    for x, y, z, r in ((-4.0, -9.0, 15.4, 1.4), (3.4, -7.0, 16.4, 1.7), (-1.2, -5.0, 17.4, 1.3), (5.2, -3.6, 15.8, 1.2), (-6.0, -4.6, 14.6, 1.5), (1.6, -11.0, 13.8, 1.1)):  # blisters that stand up
        m.bone = "Spine" if y < -5.5 else "Gulp"
        egg(m, "Belly", (x, y, z), r, r, r * 1.1, 10, 5)
    for name, x, y, front in (("FrontL", -8.0, 1.0, True), ("FrontR", 8.0, 1.0, True), ("BackL", -7.4, -9.6, False), ("BackR", 7.4, -9.6, False)):
        side = 1 if x > 0 else -1
        m.use(name, (x, y, 7.6), "Gulp" if front else "Spine")
        knee = Vector((x + side * (4.4 if front else 5.2), y + (0.0 if front else 2.4), 7.0 if front else 8.4))
        foot = Vector((x + side * 3.6, y + (2.0 if front else -1.0), 0.8))
        start = Vector((x, y, 7.6))
        knob(m, "Body", start + Vector((0, 0, 1.6)), 4.1)
        limb(m, "Accent", [start, start.lerp(knee, 0.5), knee, knee.lerp(foot, 0.4), knee.lerp(foot, 0.8), foot], (6.0, 6.2, 4.4, 4.0, 2.8, 2.6), sides=14)
        point(m, "Claw", tuple(knee), tuple(knee + Vector((side * 2.4, -2.0, 1.6))), 1.8)
        egg(m, "Accent", tuple(foot + Vector((0, 0.8, -0.2))), 2.2, 2.4, 0.8, 10, 5)
        talons(m, foot + Vector((0, 2.4, -0.2)), (0, 1, -0.3), 3, 1.3, 2.4, 0.8)
    m.bone = "Spine"
    path = [(p, w, w) for p, w in zip(curve([(0, -12.6, 9.0), (0, -15.0, 8.0), (0, -17.0, 6.0), (0, -18.6, 3.6)], 7), (5.0, 3.8, 2.8, 2.0, 1.4, 0.8, 0.2))]
    jointed(m, "Accent", ["Tail1", "Tail2", "Tail3"], path, sides=10)
    m.bone = "Head"
    skull = [(0, 0.8, 0.0, 0.84), (0.24, 1.0, 0.0, 0.92), (0.5, 1.0, 0.0, 0.7), (0.74, 0.9, 0.0, 0.46), (0.92, 0.68, 0.0, 0.3), (1.0, 0.34, 0.04, 0.18)]
    jaw = [(0, 0.8, -0.8, 0.0), (0.3, 0.98, -0.86, 0.0), (0.6, 0.92, -0.74, 0.0), (0.84, 0.72, -0.56, 0.0), (0.97, 0.46, -0.4, 0.0), (1.0, 0.24, -0.26, -0.02)]
    at = fierce_head(m, 0.8, 10.0, 15.0, 20.0, 7.6, skull, jaw, gape=-0.41, lower="Belly", teeth=(19, 17), tall=2.4, base=0.72, fangs=((0.82, 1.7), (0.48, 1.45)), rows=2, seed=3, jaw_length=1.06, t0=0.32, throat=1.1, tongue_long=0.8)
    for side in (-1, 1):  # eyes up on the roof of the head
        spot = at(0.5, 0.92 if side > 0 else math.pi - 0.92)
        egg(m, "Body", tuple(spot + Vector((0, -0.8, 0.0))), 2.8, 3.0, 1.9, 12, 6)
        c = spot + Vector((side * 0.1, 1.2, 0.5))
        eye(m, c, 1.0, (side * 0.24, 0.95, -0.16), side, socket=1.8, ridge_size=1.4)
        horn(m, "Claw", tuple(c + Vector((side * 1.6, -1.8, 0.6))), tuple(c + Vector((side * 3.8, -6.0, 2.6))), 1.3, droop=-0.3)
        for t, a_, tall in ((0.68, 0.8, 1.5), (0.8, 0.62, 1.2), (0.28, 0.9, 1.6)):  # bone breaking through the roof of its mouth
            spot2 = at(t, a_ if side > 0 else math.pi - a_)
            horn(m, "Claw", tuple(spot2), tuple(spot2 + Vector((side * tall * 0.5, -tall * 0.5, tall * 1.2))), 0.9)
    # Hooks down the middle of the skull, big to small, the only line on that huge dome.
    for t, tall in ((0.12, 3.6), (0.24, 3.2), (0.36, 2.6), (0.5, 2.0), (0.62, 1.5)):
        spot2 = at(t, math.pi / 2)
        horn(m, "Claw", tuple(spot2 - Vector((0, 0, 0.3))), tuple(spot2 + Vector((0, -tall * 0.6, tall))), 1.5)
    for x, t in ((-1, 0.9), (1, 0.9)):
        egg(m, "Socket", tuple(at(t, 1.25 if x > 0 else math.pi - 1.25)), 0.82, 0.6, 0.26, 8, 4)
    m.head_centre = (0, 30.0, 13.0)
    on_the_floor(m)
    return m


# ---------------------------------------------------------------------- Spore Loser


def spore_loser():
    """Thin as a flea, its back legs folded high over it, hooks held out in front."""
    m = monster("dino_SporeLoser", Body="#3e3c14", Accent="#17140a", Belly="#a0a84c", Claw="#ece4bc")
    m.joint("Spine", (0, -4.0, 9.0))
    m.joint("Bounce", (0, 1.6, 10.6), "Spine")
    m.joint("Neck", (0, 5.0, 12.0), "Bounce")
    rings = [((0, -11.0, 8.0), 2.0, 2.0), ((0, -9.0, 8.4), 6.6, 6.0), ((0, -5.0, 9.2), 8.4, 7.4), ((0, -1.0, 10.0), 6.6, 6.0), ((0, 2.0, 11.0), 5.0, 4.8), ((0, 4.6, 12.0), 3.8, 3.6), ((0, 6.8, 13.0), 3.4, 3.4), ((0, 8.4, 13.6), 4.2, 3.6)]
    sweep_fine(m, "Body", rings, ["Spine", "Spine", "Spine", "Spine", "Bounce", "Bounce", "Neck", "Neck"], sides=14, under="Belly", under_faces=5)
    for y, z, w, h, bone in ((-8.2, 8.5, 8.0, 7.3, "Spine"), (-6.4, 8.9, 9.0, 8.1, "Spine"), (-4.4, 9.3, 9.4, 8.4, "Spine"), (-2.4, 9.7, 8.5, 7.7, "Spine"), (-0.2, 10.3, 7.1, 6.6, "Bounce")):  # the plates of a flea's back
        band(m, "Accent", (0, y, z), w, h, length=1.0, bone=bone, tilt=(0, 1, 0.18))
    for k, (y, z, tall) in enumerate(((-8.0, 11.0, 2.6), (-5.4, 12.4, 3.4), (-2.6, 12.6, 3.0), (0.2, 12.8, 2.4), (2.8, 13.2, 2.0))):  # hooks down its back
        m.bone = "Spine" if k < 3 else "Bounce"
        point(m, "Claw", (0, y + 0.3, z - 0.8), (0, y - 1.6, z + tall), 1.5)
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee = Vector((side * 3.6, -5.0, 10.2)), Vector((side * 7.6, -11.0, 18.6))
        hock, foot = Vector((side * 8.6, -3.4, 5.4)), Vector((side * 8.8, -0.4, 0.8))
        m.use(f"Back{letter}", tuple(hip))
        limb(m, "Body", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.3, 0, 0.5)), knee], (4.6, 4.4, 1.0))
        m.joint(f"Hock{letter}", tuple(knee), f"Back{letter}")
        m.bone = f"Hock{letter}"
        limb(m, "Accent", [knee, knee.lerp(hock, 0.5), hock, foot, foot + Vector((0, 2.2, -0.1))], (2.0, 1.3, 1.1, 1.0, 1.4))
        talons(m, foot + Vector((0, 2.2, 0)), (0, 1, -0.1), 3, 0.7, 1.8, 0.6)
        point(m, "Claw", tuple(knee), tuple(knee + Vector((side * 0.6, -2.2, 2.6))), 1.3)
        shoulder, elbow, wrist = Vector((side * 2.4, 2.2, 10.6)), Vector((side * 6.2, 5.4, 7.4)), Vector((side * 5.2, 9.6, 2.4))
        m.use(f"Front{letter}", tuple(shoulder), "Bounce")
        limb(m, "Accent", [shoulder, shoulder.lerp(elbow, 0.5), elbow, elbow.lerp(wrist, 0.5), wrist], (2.2, 1.6, 1.3, 1.0, 1.0))
        talons(m, wrist, (0, 0.7, -0.6), 2, 0.8, 2.8, 0.7)
    m.use("Head", (0, 8.0, 13.0), "Neck")
    skull = [(0, 0.76, 0.0, 1.0), (0.22, 1.0, 0.0, 1.36), (0.44, 0.9, 0.0, 1.46), (0.66, 0.56, 0.0, 1.12), (0.88, 0.34, 0.0, 0.76), (1.0, 0.14, 0.06, 0.36)]
    jaw = [(0, 0.76, -0.5, 0.0), (0.34, 0.68, -0.42, 0.0), (0.66, 0.42, -0.32, 0.0), (0.92, 0.24, -0.22, 0.0), (1.0, 0.1, -0.14, -0.02)]
    at = fierce_head(m, 7.8, 12.6, 8.6, 7.6, 3.4, skull, jaw, gape=-0.8, lower="Belly", teeth=(9, 8), tall=1.2, base=0.34, fangs=((0.88, 2.5),), low_fangs=((0.7, 1.8),), seed=21, lower_inset=0.62, t0=0.32, gum_lift=0.18)
    for side in (-1, 1):
        a_ = 0.86 if side > 0 else math.pi - 0.86
        spot = at(0.52, a_)
        eye(m, spot, 0.66, (side * 0.3, 0.93, -0.1), side, socket=1.8, ridge_size=1.1)
        eye(m, at(0.24, 0.6 if side > 0 else math.pi - 0.6), 0.36, (side * 0.8, 0.6, 0), side, socket=1.6, pupil="Slit", ridge=None)  # spare eyes, further back
        feeler = at(0.62, 1.1 if side > 0 else math.pi - 1.1)  # feelers, thin as whips, swept back over it
        sabre(m, "Claw", [tuple(feeler), tuple(feeler + Vector((side * 1.4, 0.4, 3.4))), tuple(feeler + Vector((side * 4.0, -3.4, 6.0))), tuple(feeler + Vector((side * 6.4, -9.0, 5.6)))], 0.5, 10)
    beak = at(0.98, math.pi / 2)
    sabre(m, "Claw", [tuple(beak + Vector((0, -1.2, 0.2))), tuple(beak + Vector((0, 0.7, -0.1))), tuple(beak + Vector((0, 0.7, -1.9)))], 1.0, 8, flat=0.6)  # a hook over the mouth
    m.head_centre = (0, 19.0, 14.0)
    on_the_floor(m)
    return m


ALL = [mouth_breather, spore_loser]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "spore_hollow_7_8", SKY, FLOOR, GLOW_ROLES, glow=0.0, spacing=56)


if __name__ == "__main__":
    main()
