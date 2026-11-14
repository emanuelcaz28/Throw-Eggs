"""Builds The Weeping Dark's 9th to 12th monsters, animates them and saves them (Blender, background mode).

    Blender -b -P build_weeping_dark_apex.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_weeping_dark_apex.py    (stills only, nothing saved)
    ONLY=grim_weeper QUICK=1 ...                                           (just those)

Saves weeping_dark_apex.blend. What they share with Spore Hollow's four (the attacks, the turning bones, the three actions) is in
apex_kit.py; the dread look (bare skulls, ribs, long claws) is build_weeping_dark_dread.py's.

The owner, 2026-11-13: four more for this map, rarer than its 8, "even more aggressive than the rarest", each with a unique animation and
an effect or an object animated on it, from the map's theme. No rarity or chances yet: they are not in Config/Dinos.

The map's rule holds: no colour at all, black, ash and bone, and red is only ever eyes. So here the effects are eyes and bone.

  Grim Weeper     a reaper with no legs, its forearms two scythes of bone, and behind its shoulders a wheel of red eyes that never
                  stops turning (Wheel). It cuts right across, cuts back, then brings both down from over its head (Reap)
  Cage Rage       a beast whose ribs are a second mouth: ten fangs of bone closed round a black heart full of eyes. It rears, the
                  ribs fling open, it falls on you and chews (RibL1-5, RibR1-5)
  Mourning Star   a low tank of bone plates with a tail arched over it, and on the tail a star of spikes with eyes between them,
                  turning (Halo). The tail whirls three times round and the star comes down ahead of it (Flail1-5)
  Nevermore       the rarest: a raven the size of a house with a bare skull, and a ring of black feathers circling over its head
                  (Halo). Wings beaten down, a hop, four pecks, a caw, and the feathers burst outward each time (Plume1-8)

Glowing role: EyeGlow only. Skin roles Body, Accent, Belly and Claw take the colour mutations. 1 Blender unit = 1 stud, models face +Y,
feet on Z = 0. Plain colours, no stud image.
"""
import math
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402,F401  (first: it turns the stud preview off)
import apex_kit  # noqa: E402
from apex_kit import PLUMES, hoop  # noqa: E402
from build_clockwork_citadel_monsters_7_8 import limb, talons  # noqa: E402
from build_spore_hollow_monsters import egg  # noqa: E402
from build_spore_hollow_toxic import grounded, leg, skin_at, tox_eye, unit  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from build_weeping_dark_dread import BONE, FLOOR, GLOW_ROLES, SKY, claws, eyes, monster, ribs, spines  # noqa: E402
from fierce_kit import band, fierce_head, horn, knob  # noqa: E402
from rare_kit import chain, curve, jointed, leaf, ring_round, sabre, sweep, sweep_fine  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_weeping_dark_apex"
BLEND = "weeping_dark_apex"  # for export_fbx.py


def loose_eye(m, at, r, look, side=1):
    """A red eye with no face round it: a black pit and the eye in it. Never the Pupil role (the reveal aims at those)."""
    tox_eye(m, Vector(at), r, look, side, socket=1.7, lid="Claw", pupil="Slit", ridge=None, top=0.3, low=0.2)


# ---------------------------------------------------------------------- Grim Weeper


def grim_weeper():
    """It hangs in the air, a cage of ribs under a hood, its own spine trailing on the ground; two scythes for arms, and the eyes behind it."""
    m = monster("dino_GrimWeeper", Body="#0b0b0e", Accent="#2a2a30", Belly="#cfcbc0", Claw="#ece8dc")
    m.joint("Spine", (0, 0, 13.0))
    m.joint("Reap", (0, 0, 14.0), "Spine")
    egg(m, "Belly", (0, 0, 13.0), 3.6, 2.8, 2.4, 12, 6)  # the hips
    # Its spine, hanging to the ground and dragging behind (Tail1 to 3).
    drop = curve([(0, 0, 12.4), (0, -0.6, 9.0), (0, -1.6, 5.6), (0, -3.6, 2.6), (0, -7.0, 1.0), (0, -10.6, 0.6)], 13)
    widths = [2.2, 2.1, 2.0, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.2, 1.0, 0.8, 0.4]
    tail_bones = jointed(m, "Belly", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(drop, widths)], sides=8)
    for i in range(1, 12, 2):  # the knobs of it
        p = Vector(drop[i])
        m.bone = tail_bones[i]
        back = unit(Vector(drop[i + 1]) - Vector(drop[i - 1])).cross(Vector((1, 0, 0)))
        point(m, "Claw", tuple(p), tuple(p - back * (1.6 + widths[i] * 0.6) + Vector((0, 0, -0.4))), 1.0)
        band(m, "Claw", tuple(p), widths[i] * 1.24, widths[i] * 1.24, length=0.5, tilt=tuple(Vector(drop[i + 1]) - Vector(drop[i - 1])))
    for n, a in enumerate((0.5, 1.3, 2.1, 3.6, 4.4, 5.2), start=1):  # what is left of its robe, in strips, swaying
        root = Vector((math.cos(a) * 3.0, math.sin(a) * 2.2, 13.2))
        out = Vector((math.cos(a), math.sin(a), 0))
        pts = curve([root, root + out * 1.6 + Vector((0, 0, -3.0)), root + out * 2.4 + Vector((0, -0.6, -6.4)), root + out * 2.6 + Vector((0, -1.4, -9.8))], 7)
        chain(m, "Sway", n, pts, 0.26, 0.16, parent="Spine", role="Body" if n % 2 else "Accent", flat="side" if abs(out.y) > 0.6 else "normal", breadth=3.0)
    m.bone = "Reap"
    torso = [((0, 0, 13.4), 2.6, 2.6), ((0, 0, 16.0), 3.4, 3.2), ((0, 0.6, 19.0), 8.6, 6.0), ((0, 1.2, 22.0), 12.0, 6.8), ((0, 1.8, 24.2), 6.6, 5.0)]
    sweep_fine(m, "Body", torso, ["Reap"] * 5, up=(0, -1, 0.1), sides=18, per=4)
    for z, w, d, yy in ((17.4, 6.5, 5.1, 0.3), (18.8, 8.8, 6.0, 0.55), (20.2, 10.9, 6.6, 0.85), (21.6, 12.6, 7.3, 1.1)):  # ribs
        sweep(m, "Claw", [((0, yy, z - 0.24), w, d), ((0, yy, z + 0.24), w, d)], sides=14, up=(0, -1, 0.05))
    for letter, side in (("L", -1), ("R", 1)):
        shoulder, elbow = Vector((side * 6.2, 1.6, 23.0)), Vector((side * 11.4, 0.4, 17.6))
        m.use(f"Arm{letter}", tuple(shoulder), "Reap")
        knob(m, "Belly", shoulder, 2.0)
        point(m, "Claw", tuple(shoulder), tuple(shoulder + Vector((side * 2.4, -1.6, 3.6))), 1.6)
        limb(m, "Belly", [shoulder, shoulder.lerp(elbow, 0.5) + Vector((side * 0.4, -0.3, 0.2)), elbow], (2.4, 1.8, 1.6), sides=10)
        # The scythe: the forearm is the blade, edge down, curving forward and in to a point.
        m.use(f"Reap{letter}", tuple(elbow), f"Arm{letter}")
        knob(m, "Claw", elbow, 1.7)
        point(m, "Claw", tuple(elbow), tuple(elbow + Vector((side * 1.4, -3.4, 1.0))), 1.5)
        blade = [elbow, elbow + Vector((side * 0.6, 5.0, -2.0)), elbow + Vector((-side * 1.6, 11.0, -2.6)), elbow + Vector((-side * 5.4, 16.0, -0.6)), elbow + Vector((-side * 8.6, 18.4, 3.0))]
        sabre(m, "Claw", [tuple(p) for p in blade], 4.2, 14, flat=0.2, sides=6, power=1.2)
        sabre(m, "Belly", [tuple(p + Vector((0, 0, 1.1))) for p in blade[:4]], 1.5, 10, flat=0.9, sides=6, power=2.5)  # its spine, thick along the back of it
    m.use("Neck", (0, 2.0, 24.0), "Reap")
    sweep_fine(m, "Belly", [((0, 1.8, 23.8), 2.6, 2.6), ((0, 2.8, 25.6), 2.2, 2.2), ((0, 3.6, 26.8), 2.6, 2.6)], sides=10, up=(0, -1, 0.1))
    m.use("Head", (0, 3.6, 26.6), "Neck")
    skull = [(0, 0.8, 0.0, 1.0), (0.22, 1.0, 0.0, 1.3), (0.46, 0.9, 0.0, 1.2), (0.7, 0.62, 0.0, 0.8), (0.92, 0.42, 0.0, 0.46), (1.0, 0.2, 0.05, 0.24)]
    jaw = [(0, 0.74, -0.42, 0.0), (0.36, 0.68, -0.38, 0.0), (0.7, 0.46, -0.28, 0.0), (0.94, 0.28, -0.2, 0.0), (1.0, 0.12, -0.12, -0.02)]
    y, zm, length, width, height = 3.2, 25.8, 8.4, 6.6, 3.8
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.9, upper="Belly", lower="Belly", teeth=(11, 10), tall=1.3, base=0.32, fangs=((0.88, 2.2), (0.6, 1.5)), seed=71, t0=0.24,
                     jaw_length=1.08)
    eyes(m, at, [(0.5, 0.8, 0.68, (0.3, 0.94, -0.12), True), (0.32, 0.46, 0.36, (0.85, 0.5, 0.0), False)], lid="Belly", ridge="Belly")
    # The hood: black, deep, torn at the edge.
    top = at(0.2, math.pi / 2)
    egg(m, "Body", (0, top.y - 1.9, top.z - 1.5), width * 0.76, 4.0, height * 1.14, 14, 7)
    for k in range(7):
        a = -0.5 + k * (math.pi + 1.0) / 6
        base = Vector((math.cos(a) * width * 0.7, top.y - 2.0, top.z - 1.6 + math.sin(a) * height))
        leaf(m, "Accent" if k % 2 else "Body", tuple(base), tuple(base + Vector((math.cos(a) * 1.6, -3.6, math.sin(a) * 1.2 - 1.6))), (-math.sin(a), 0, math.cos(a)), 2.6, thick=0.3)
    # The wheel: a ring of bone behind its shoulders with eight eyes in it, all looking where it looks. It never stops turning (Wheel).
    c = Vector((0, -3.6, 24.0))
    m.use("Wheel", tuple(c), "Reap")
    where = hoop(m, "Claw", c, 8.6, (0, 1, 0), 1.0, count=28, spikes=8, spike=3.0, spike_role="Claw", spike_w=1.2)
    for k in range(8):
        spot, out = where((k + 0.5) * math.tau / 8)
        egg(m, "Claw", tuple(spot), 2.0, 1.1, 2.0, 10, 6)
        loose_eye(m, spot + Vector((0, 0.8, 0)), 0.9, (0, 1, 0), 1 if k % 2 else -1)
    m.head_centre = (0, 9.0, 26.4)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Cage Rage


def cage_rage():
    """All legs and spine, and where its body should be, a cage: five ribs a side meeting under it like teeth, something watching from inside."""
    m = monster("dino_CageRage", Body="#101014", Accent="#2e2e35", Belly="#3a3a42", Claw=BONE)
    m.joint("Spine", (0, -9.0, 12.4))
    m.joint("Neck", (0, 10.0, 12.6), "Spine")
    rings = [((0, -14.0, 11.0), 2.0, 2.0), ((0, -11.0, 12.2), 6.0, 5.4), ((0, -4.0, 13.2), 4.4, 4.4), ((0, 4.0, 13.6), 4.8, 4.8), ((0, 9.0, 13.2), 7.6, 6.4), ((0, 12.4, 12.4), 5.0, 5.0)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Spine", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=14, per=4)
    spines(m, rings, (1.1, 1.7, 2.3, 2.9, 3.5, 4.1), 4.0, bones, w=1.4, back=0.5)
    # The heart: black, hanging under the spine on a stalk, and eyes all over it looking out between the ribs.
    m.bone = "Spine"
    heart = Vector((0, 0.0, 8.2))
    sweep(m, "Mouth", [((0, 0, 12.0), 2.4, 2.4), ((0, 0, 9.6), 3.0, 3.0)], sides=8, up=(0, 1, 0))
    egg(m, "Mouth", tuple(heart), 3.6, 6.4, 2.9, 16, 8)
    for side in (-1, 1):
        for y_, z_, r in ((-4.4, 0.2, 0.7), (-2.2, -0.5, 0.86), (0.2, 0.3, 1.0), (2.4, -0.5, 0.86), (4.4, 0.3, 0.7)):
            k = math.sqrt(max(0.0, 1 - (y_ / 6.4) ** 2 - (z_ / 2.9) ** 2))
            loose_eye(m, heart + Vector((side * 3.6 * k, y_, z_)), r, (side, 0.25, -0.1), side)
    loose_eye(m, heart + Vector((0, 6.2, 0.2)), 0.9, (0, 1, -0.1), 1)
    # The ribs (RibL1 to 5, RibR1 to 5): each hinged on the spine, curving out, down and in to a point under the heart.
    for n, y_ in enumerate((-6.4, -3.2, 0.0, 3.2, 6.4), start=1):
        top = 13.3 + 2.3 + 0.05 * y_
        swell = 1.0 - 0.012 * y_ * y_
        for letter, side in (("L", -1), ("R", 1)):
            hinge = Vector((side * 1.2, y_, top - 0.6))
            m.use(f"Rib{letter}{n}", tuple(hinge), "Spine")
            knob(m, "Claw", hinge, 1.2)
            pts = [hinge, Vector((side * 6.6 * swell, y_, top - 1.0)), Vector((side * 8.6 * swell, y_ + 0.1, 8.6)), Vector((side * 6.0 * swell, y_ + 0.3, 4.2)), Vector((side * 1.3, y_ + 0.5 - side * 0.9, 2.2))]
            sabre(m, "Claw", [tuple(p) for p in pts], 2.1, 14, flat=0.85, sides=6, power=2.2)
            barb = pts[2]
            point(m, "Claw", tuple(barb), tuple(barb + Vector((side * 2.6, -1.2, 1.0))), 1.2)
    for letter, side in (("L", -1), ("R", 1)):
        leg(m, f"Front{letter}", "Spine", [(side * 3.6, 10.0, 12.6), (side * 9.0, 11.6, 9.0), (side * 9.6, 10.0, 4.6), (side * 9.8, 11.6, 1.0)], (3.4, 2.4, 1.7, 1.8), role="Body", toes=0)
        knob(m, "Claw", Vector((side * 9.0, 11.6, 9.0)), 1.6)
        point(m, "Claw", (side * 9.0, 11.6, 9.0), (side * 11.0, 9.6, 12.0), 1.4)
        claws(m, (side * 9.8, 11.7, 1.3), (0, 1, 0), 4, 0.8, 4.8, 0.7, droop=0.16)
        leg(m, f"Back{letter}", "Spine", [(side * 3.4, -10.6, 12.0), (side * 8.6, -8.0, 8.6), (side * 9.0, -11.8, 4.2), (side * 9.2, -10.2, 1.0)], (4.0, 2.6, 1.8, 1.9), role="Body", toes=0)
        knob(m, "Claw", Vector((side * 8.6, -8.0, 8.6)), 1.7)
        point(m, "Claw", (side * 8.6, -8.0, 8.6), (side * 10.4, -10.6, 11.6), 1.4)
        claws(m, (side * 9.2, -9.6, 1.4), (0, 1, 0), 3, 0.9, 3.6, 0.7, droop=0.16)
    m.bone = "Spine"
    tail = curve([(0, -13.4, 11.2), (0, -17.0, 11.6), (0, -21.6, 9.6), (0, -26.0, 5.6)], 8)
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(tail, (2.6, 2.2, 1.9, 1.6, 1.3, 1.0, 0.7, 0.3))], sides=8)
    m.bone = "Tail3"
    sabre(m, "Claw", [(0, -25.6, 6.0), (0, -28.0, 4.6), (0, -29.6, 6.4), (0, -29.0, 9.0)], 1.5, 9, flat=0.5)  # a hook on the end of it
    m.use("Head", (0, 12.0, 11.8), "Neck")
    skull = [(0, 0.84, 0.0, 0.96), (0.2, 1.0, 0.0, 1.2), (0.44, 0.9, 0.0, 1.06), (0.68, 0.62, 0.0, 0.7), (0.9, 0.46, 0.0, 0.46), (1.0, 0.24, 0.05, 0.24)]
    jaw = [(0, 0.8, -0.5, 0.0), (0.32, 0.8, -0.48, 0.0), (0.66, 0.56, -0.36, 0.0), (0.92, 0.36, -0.26, 0.0), (1.0, 0.16, -0.14, -0.02)]
    y, zm, length, width, height = 11.4, 10.6, 11.6, 8.4, 4.8
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.7, upper="Claw", lower="Claw", teeth=(13, 12), tall=1.6, base=0.42, fangs=((0.86, 2.3), (0.62, 1.5), (0.4, 1.4)), rows=2, seed=73,
                     t0=0.2, throat=1.1, jaw_length=1.04)
    eyes(m, at, [(0.46, 0.8, 0.8, (0.3, 0.94, -0.1), True), (0.3, 0.44, 0.46, (0.85, 0.5, 0.0), False), (0.66, 1.15, 0.4, (0.1, 0.9, 0.4), False)], lid="Claw", ridge="Claw")
    for side in (-1, 1):
        spot = at(0.18, 0.75 if side > 0 else math.pi - 0.75)
        horn(m, "Claw", tuple(spot - Vector((0, 0, 0.5))), tuple(spot + Vector((side * 4.6, -6.4, 3.6))), 2.0, droop=-1.4, count=9)
        egg(m, "Socket", tuple(at(0.94, 1.15 if side > 0 else math.pi - 1.15)), 0.44, 0.36, 0.5, 8, 4)
    m.head_centre = (0, 20.0, 10.6)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Mourning Star


def mourning_star():
    """Low, wide, plated in bone; a bull's skull with the horns forward; and the tail, with its star."""
    m = monster("dino_MourningStar", Body="#2b2b31", Accent="#0e0e11", Belly="#55545c", Claw=BONE)
    m.joint("Spine", (0, -6.0, 8.6))
    m.joint("Neck", (0, 7.6, 8.8), "Spine")
    m.joint("Head", (0, 8.8, 8.2), "Neck")
    rings = [((0, -14.0, 7.6), 3.0, 3.0), ((0, -11.6, 8.2), 10.0, 7.4), ((0, -6.0, 9.0), 15.0, 9.6), ((0, 0.0, 9.4), 16.0, 10.0), ((0, 5.0, 9.2), 13.0, 8.6), ((0, 8.6, 8.8), 8.6, 6.6)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Spine", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=20, under="Belly", under_faces=7, per=4)
    ribs(m, rings, (1.4, 1.9, 2.4, 2.9, 3.4, 3.9), bones, grow=1.09, length=1.3)  # plates of bone across its back
    for side in (-1, 1):  # a row of spikes down each side of its back
        for k, u in enumerate((1.4, 1.9, 2.4, 2.9, 3.4, 3.9, 4.4)):
            at_, n = skin_at(rings, u, 0.9 if side > 0 else math.pi - 0.9)
            m.bone = bones[round(u)]
            horn(m, "Claw", tuple(at_ - n * 0.4), tuple(at_ + n * (3.4 - 0.2 * k) + Vector((0, -1.0, 0.6))), 1.7)
    for letter, side in (("L", -1), ("R", 1)):
        leg(m, f"Front{letter}", "Spine", [(side * 6.0, 4.6, 8.0), (side * 9.6, 5.6, 5.2), (side * 9.2, 4.6, 2.6), (side * 9.4, 6.0, 1.0)], (5.4, 4.0, 3.2, 3.4), toes=0, pad=2.2)
        knob(m, "Claw", Vector((side * 9.6, 5.6, 5.2)), 2.3)
        point(m, "Claw", (side * 9.6, 5.6, 5.2), (side * 12.6, 4.0, 7.6), 1.8)
        claws(m, (side * 9.4, 7.4, 1.3), (0, 1, 0), 3, 1.1, 3.4, 1.0, droop=0.2)
        leg(m, f"Back{letter}", "Spine", [(side * 6.0, -10.0, 8.0), (side * 9.6, -8.6, 5.4), (side * 9.2, -11.0, 2.8), (side * 9.4, -9.6, 1.0)], (6.2, 4.4, 3.4, 3.6), toes=0, pad=2.4)
        knob(m, "Claw", Vector((side * 9.6, -8.6, 5.4)), 2.5)
        point(m, "Claw", (side * 9.6, -8.6, 5.4), (side * 12.6, -10.6, 7.8), 1.8)
        claws(m, (side * 9.4, -8.2, 1.3), (0, 1, 0), 3, 1.1, 3.2, 1.0, droop=0.2)
    m.bone = "Head"
    skull = [(0, 0.9, 0.0, 0.96), (0.22, 1.0, 0.0, 1.16), (0.46, 0.92, 0.0, 1.0), (0.7, 0.72, 0.0, 0.7), (0.9, 0.56, 0.0, 0.48), (1.0, 0.3, 0.05, 0.26)]
    jaw = [(0, 0.86, -0.56, 0.0), (0.3, 0.94, -0.6, 0.0), (0.62, 0.8, -0.5, 0.0), (0.88, 0.58, -0.36, 0.0), (1.0, 0.28, -0.2, -0.02)]
    y, zm, length, width, height = 8.0, 7.0, 11.0, 10.8, 5.6
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.5, upper="Claw", lower="Claw", teeth=(14, 12), tall=1.7, base=0.48, fangs=((0.86, 2.0), (0.6, 1.5)), rows=2, seed=75, t0=0.2,
                     throat=1.1)
    eyes(m, at, [(0.5, 0.82, 0.86, (0.3, 0.94, -0.1), True), (0.34, 0.46, 0.5, (0.85, 0.5, 0.0), False), (0.68, 1.16, 0.44, (0.1, 0.9, 0.4), False)], lid="Claw", ridge="Claw")
    for side in (-1, 1):
        spot = at(0.2, 0.6 if side > 0 else math.pi - 0.6)  # a bull's horns, out and forward
        horn(m, "Claw", tuple(spot - Vector((side * 0.6, 0, 0))), tuple(spot + Vector((side * 6.6, 8.0, 3.6))), 2.8, droop=2.0, count=10)
        spot = at(0.1, 1.05 if side > 0 else math.pi - 1.05)
        horn(m, "Claw", tuple(spot - Vector((0, 0, 0.5))), tuple(spot + Vector((side * 3.0, -4.6, 3.6))), 1.9, droop=-1.0, count=7)
        egg(m, "Socket", tuple(at(0.93, 1.15 if side > 0 else math.pi - 1.15)), 0.5, 0.4, 0.6, 8, 4)
    # The tail: five joints of it arched up and over its back (Flail1 to 5), a knuckle of bone at each.
    route = curve([(0, -12.6, 9.6), (0, -21.0, 17.0), (0, -22.6, 28.0), (0, -15.6, 37.0), (0, -4.6, 40.0)], 21)
    names = [f"Flail{n}" for n in range(1, 6)]
    m.bone = "Spine"
    knob(m, "Body", Vector((0, -12.4, 9.4)), 3.4)
    flail = jointed(m, "Body", names, [(p, 4.4 - 0.11 * i, 4.4 - 0.11 * i) for i, p in enumerate(route)], sides=10)
    for i in range(3, 20, 2):
        p = Vector(route[i])
        along = Vector(route[i + 1]) - Vector(route[i - 1])
        band(m, "Claw", tuple(p), (4.4 - 0.11 * i) * 1.16, (4.4 - 0.11 * i) * 1.16, length=0.8, bone=flail[i], tilt=tuple(along))
        if i % 4 == 1:
            out = unit(along).cross(Vector((1, 0, 0)))
            point(m, "Claw", tuple(p), tuple(p - out * 3.6), 1.5)
    # The star: a ball of bone, spikes all round it, a red eye between every few. It turns for ever on the end of the tail (Halo).
    c = Vector((0, 1.6, 37.4))
    m.bone = "Flail5"
    sweep(m, "Body", [(route[-1], 2.2, 2.2), (tuple(c), 1.8, 1.8)], sides=8)
    m.use("Halo", tuple(c), "Flail5")
    r = 4.0
    egg(m, "Claw", tuple(c), r, r, r, 16, 9)
    golden = math.pi * (3 - math.sqrt(5))
    for k in range(18):
        z = 1 - 2 * (k + 0.5) / 18
        ring = math.sqrt(1 - z * z)
        d = Vector((math.cos(k * golden) * ring, math.sin(k * golden) * ring, z))
        if k % 3 == 1 and abs(d.z) < 0.8:
            loose_eye(m, c + d * r * 0.96, 0.9, tuple(d), 1 if d.x >= 0 else -1)
        else:
            point(m, "Claw", tuple(c + d * r * 0.8), tuple(c + d * (r + 4.4)), 2.2)
    m.head_centre = (0, 20.0, 7.6)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Nevermore


def feathers(m, role, root, tips, across, w, step=(0, 0, 0), edge="Accent"):
    """A row of blade feathers from one root line out to tips, each a little off the last so no two lie in the same plane."""
    for k, (base, tip) in enumerate(zip(root, tips)):
        o = Vector(step) * k
        leaf(m, edge if k % 3 == 2 else role, tuple(Vector(base) + o), tuple(Vector(tip) + o), across, w, thick=0.26)


def nevermore():
    """A raven taller than the gates, black to the last feather, its head a bare skull with a beak like a pick."""
    m = monster("dino_Nevermore", Body="#09090c", Accent="#24242b", Belly="#3a3a42", Claw=BONE)
    m.joint("Spine", (0, -2.0, 13.0))
    m.joint("Neck", (0, 4.4, 17.4), "Spine")
    rings = [((0, -12.0, 10.0), 3.0, 3.0), ((0, -9.0, 11.0), 8.0, 7.0), ((0, -4.0, 12.6), 11.0, 10.0), ((0, 1.0, 14.5), 11.6, 10.6), ((0, 4.4, 17.2), 8.6, 8.0), ((0, 6.2, 20.2), 5.8, 5.8), ((0, 7.6, 23.2), 4.6, 4.6)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Neck", "Neck", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=18, under="Belly", under_faces=5, per=4)
    for k, (u, a) in enumerate(((3.2, 0.5), (3.6, 1.0), (4.2, 0.4), (4.6, 0.9), (5.2, 0.5), (5.6, 1.0))):  # a ruff of blade feathers up its throat and neck
        for side in (-1, 1):
            at_, n = skin_at(rings, u, a if side > 0 else math.pi - a)
            m.bone = bones[round(u)]
            leaf(m, "Accent" if k % 2 else "Body", tuple(at_ - n * 0.4), tuple(at_ + n * 2.4 + Vector((0, -3.0, -1.6))), (0, 0.5, 1), 2.2, thick=0.3)
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee, ankle, foot = Vector((side * 3.8, -3.0, 11.6)), Vector((side * 5.6, 1.6, 7.2)), Vector((side * 5.2, -2.6, 3.0)), Vector((side * 5.4, -0.6, 0.9))
        m.use(f"Leg{letter}", tuple(hip))
        knob(m, "Body", hip, 3.0)
        limb(m, "Body", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.5, 0.3, 0.3)), knee], (5.4, 4.4, 2.0), sides=12)
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        knob(m, "Claw", knee, 1.3)
        limb(m, "Claw", [knee, knee.lerp(ankle, 0.5) + Vector((0, -0.4, 0)), ankle, foot, foot + Vector((0, 2.0, -0.1))], (1.7, 1.3, 1.2, 1.4, 1.6), sides=8)
        talons(m, foot + Vector((0, 1.7, 0)), (0, 1, -0.12), 3, 1.3, 4.8, 1.0)
        sabre(m, "Claw", [tuple(foot), tuple(foot + Vector((0, -2.4, 0.1))), tuple(foot + Vector((0, -4.0, -0.6)))], 0.9, 6)  # the back claw
        # The wing, half open and held up: an arm of bone under black blades. Wing carries the long feathers of the forearm, WingTip the hand's.
        shoulder, elbow, wrist = Vector((side * 5.0, 2.0, 16.6)), Vector((side * 11.6, -1.0, 21.4)), Vector((side * 18.0, -3.6, 18.6))
        m.use(f"Wing{letter}", tuple(shoulder), "Spine")
        knob(m, "Body", shoulder, 2.4)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5) + Vector((0, 0, 0.4)), elbow, elbow.lerp(wrist, 0.5), wrist], (3.6, 3.0, 2.4, 2.0, 1.7), sides=10)
        point(m, "Claw", tuple(elbow), tuple(elbow + Vector((side * 0.6, -1.0, 3.6))), 1.4)
        across = (0, 1, 0.25)
        base = [shoulder.lerp(elbow, t) for t in (0.2, 0.45, 0.7, 0.95)] + [elbow.lerp(wrist, t) for t in (0.25, 0.5, 0.75)]
        tips = [b + Vector((side * (0.6 + 0.5 * k), -5.0 - 0.8 * k, -9.0 - 0.9 * k)) for k, b in enumerate(base)]
        feathers(m, "Body", base, tips, across, 3.6, step=(0, -0.16, 0))
        m.use(f"WingTip{letter}", tuple(wrist), f"Wing{letter}")
        knob(m, "Claw", wrist, 1.3)
        point(m, "Claw", tuple(wrist), tuple(wrist + Vector((side * 1.0, 2.6, 1.6))), 1.2)  # a claw on the wrist
        tips = [wrist + Vector((side * (1.0 + 1.2 * k), -7.0 - 1.5 * k, -10.0 + 1.3 * k)) for k in range(6)]
        feathers(m, "Body", [wrist + Vector((side * 0.3 * k, -0.2 * k, 0)) for k in range(6)], tips, across, 3.4, step=(0, -0.18, 0))
    m.use("Tail1", (0, -11.0, 10.4), "Spine")  # a fan of a tail
    for k in range(7):
        a = (k - 3) * 0.2
        base = Vector((math.sin(a) * 1.6, -11.0, 10.2 + 0.3 * abs(k - 3)))
        leaf(m, "Accent" if k % 2 else "Body", tuple(base), tuple(base + Vector((math.sin(a) * 11.0, -math.cos(a) * 11.0, -3.4 + 0.5 * abs(k - 3)))), (1, 0, 0), 3.2, thick=0.26)
    m.use("Head", (0, 7.8, 23.4), "Neck")
    skull = [(0, 0.82, 0.0, 1.0), (0.18, 1.0, 0.0, 1.36), (0.36, 0.86, 0.0, 1.26), (0.56, 0.52, 0.0, 0.9), (0.8, 0.34, 0.0, 0.6), (0.95, 0.22, 0.0, 0.36), (1.0, 0.08, 0.04, 0.2)]
    jaw = [(0, 0.74, -0.42, 0.0), (0.34, 0.6, -0.34, 0.0), (0.68, 0.36, -0.24, 0.0), (0.93, 0.2, -0.16, 0.0), (1.0, 0.07, -0.1, -0.02)]
    y, zm, length, width, height = 7.4, 22.4, 14.0, 6.2, 3.6
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.5, upper="Claw", lower="Claw", gums=None, teeth=(13, 12), tall=0.9, base=0.3, fangs=((0.6, 1.5),), tongue=False, seed=77, t0=0.3)
    sabre(m, "Claw", [tuple(at(0.97, math.pi / 2) + Vector((0, -1.0, 0.1))), tuple(at(1.0, math.pi / 2) + Vector((0, 0.8, -0.2))), tuple(at(1.0, math.pi / 2) + Vector((0, 0.9, -2.4)))], 1.0, 8, flat=0.6)  # the hook of the beak
    for side in (-1, 1):
        spot = at(0.34, 0.8 if side > 0 else math.pi - 0.8)
        tox_eye(m, spot, 0.6, (side * 0.3, 0.94, -0.1), side, socket=2.4, lid="Claw", top=0.34, tilt=0.8, low=0.2, sink=1.0, ridge="Claw", ridge_size=1.5, proud=0.15)
        slit = [at(0.6, 1.3 if side > 0 else math.pi - 1.3), at(0.7, 1.1 if side > 0 else math.pi - 1.1), at(0.8, 0.9 if side > 0 else math.pi - 0.9)]  # where a nostril was
        sweep_fine(m, "Socket", [(tuple(p), w, w) for p, w in zip(slit, (0.14, 0.5, 0.18))], sides=6, per=2)
    for k in range(5):  # a crest of blades swept back off the skull
        spot = at(0.08 + 0.07 * k, math.pi / 2)
        leaf(m, "Accent" if k % 2 else "Body", tuple(spot - Vector((0, 0, 0.5))), tuple(spot + Vector((0, -6.4 + 0.7 * k, 3.4 - 0.3 * k))), (1, 0, 0), 1.9, thick=0.3)
    # The feathers over it: a thin ring of ash turning for ever (Halo), and eight blades riding it nose to tail (Plume1 to 8), which
    # burst outward in the attack.
    c = Vector((0, 4.0, 33.0))
    m.use("Halo", tuple(c), "Spine")
    where = hoop(m, "Accent", c, 8.0, (0, 0, 1), 0.5, count=32)
    for n in range(1, PLUMES + 1):
        a = (n - 1) * math.tau / PLUMES
        spot = c + Vector((math.cos(a), math.sin(a), 0)) * 8.0
        tangent = Vector((-math.sin(a), math.cos(a), 0))
        out = Vector((math.cos(a), math.sin(a), 0))
        m.use(f"Plume{n}", tuple(spot), "Halo")
        leaf(m, "Body", tuple(spot - tangent * 2.6), tuple(spot + tangent * 4.4 + out * 1.6 + Vector((0, 0, 0.8))), (0, 0, 1), 2.8, thick=0.3)
        sweep(m, "Claw", [(tuple(spot - tangent * 3.4), 0.5, 0.5), (tuple(spot - tangent * 2.0), 0.36, 0.36)], sides=5)  # the quill
    m.head_centre = (0, 21.0, 23.0)
    grounded(m)
    return m


ALL = [grim_weeper, cage_rage, mourning_star, nevermore]


def main():
    apex_kit.run(ALL, RENDERS, BLEND, SKY, FLOOR, GLOW_ROLES, glow=1.2, spacing=70)


if __name__ == "__main__":
    main()
