"""Builds Spore Hollow's 9th to 12th monsters, animates them and saves them (Blender, background mode).

    Blender -b -P build_spore_hollow_apex.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_spore_hollow_apex.py    (stills only, nothing saved)
    ONLY=rot_weiler,sporeactor QUICK=1 ...                                 (just those)

Saves spore_hollow_apex.blend. What they share with The Weeping Dark's four (the attacks, the turning bones, the three actions) is in
apex_kit.py; the toxic look (sacs, the glare, venom) is build_spore_hollow_toxic.py's.

The owner, 2026-11-13: four more for this map, rarer than its 8, "even more aggressive than the rarest", each with a unique animation and
an effect or an object animated on it, from the map's theme. No rarity or chances yet: they are not in Config/Dinos.

  Rot Weiler      a three-headed hound of rot, a mane of acid burning down its back (Wriggle, never still). Its heads strike one after
                  the other, left, right, middle, then all three together (Triad)
  Acid Reign      a king cobra in hazard bands, reared taller than anything on the map, a crown of acid thorns turning in the air over
                  its head (Halo). It draws up, spreads its hood, the crown tips down over its face like a saw, and it strikes (Crown)
  Cap Punishment  a tyrant with an arm growing out of its back and, on the end of it, a death cap spinning as a saw (Saw). It brings
                  the saw down on the ground ahead and drags it across (SawArm1 to 3)
  Sporeactor      the rarest: a walking reactor, a core of light floating over its back inside two rings that tumble round it like a
                  gyroscope (Halo, Hoop). The core climbs and whirls, the rods in its back rise, and it all comes down at once (Core, Rod1-6)

Glowing roles: Glow, Vein, EyeGlow, Spore, Pit (all in shared/Roles.luau already). Skin roles Body, Accent, Belly and Claw take the colour
mutations. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0. Plain colours, no stud image.
"""
import math
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402,F401  (first: it turns the stud preview off)
import apex_kit  # noqa: E402
from apex_kit import hoop, rename_bones, shift  # noqa: E402
from build_clockwork_citadel_monsters_7_8 import limb, talons  # noqa: E402
from build_spore_hollow_monsters import egg  # noqa: E402
from build_spore_hollow_toxic import (FLOOR, GLOW_ROLES, SKY, blotch, cluster, grounded, leg, monster, sac, skin_at, stripes, throat_glow, tox_eye, unit,  # noqa: E402
                                      venom)
from build_thorn_kingdom_monsters import point  # noqa: E402
from fierce_kit import band, fierce_head, horn, knob  # noqa: E402
from rare_kit import chain, curve, jointed, leaf, ring_round, sabre, sweep, sweep_fine  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_spore_hollow_apex"
BLEND = "spore_hollow_apex"  # for export_fbx.py


def back_spikes(m, rings, us, tall, bones, w=1.3, role="Claw", lean=0.6):
    for k, u in enumerate(us):
        at, n = skin_at(rings, u, math.pi / 2)
        m.bone = bones[min(round(u), len(bones) - 1)]
        h = tall * (1 - 0.07 * k)
        horn(m, role, tuple(at - n * 0.3), tuple(at + n * h + Vector((0, -h * lean, 0))), w)


# ---------------------------------------------------------------------- Rot Weiler


def hound_head(m, neck_bone, base, y, zm, size, seed):
    """One of its heads, built on the middle line: a neck from base to a long wolf's skull. Leaves it on the bones Head and Jaw."""
    length, width, height = 10.5 * size, 6.6 * size, 4.2 * size
    m.use("Head", (0, y + 0.4, zm + 0.8), neck_bone)
    b = Vector(base)
    sweep_fine(m, "Body", [(tuple(b), 6.4 * size, 6.4 * size), (tuple(b.lerp(Vector((0, y, zm + 0.9)), 0.55) + Vector((0, 0, 0.5))), 5.2 * size, 5.4 * size), ((0, y + 1.6, zm + 0.9), 5.6 * size, 4.6 * size)],
               [neck_bone, neck_bone, "Head"], sides=14, per=4)
    m.bone = "Head"
    skull = [(0, 0.84, 0.0, 0.92), (0.2, 1.0, 0.0, 1.14), (0.42, 0.88, 0.0, 1.0), (0.66, 0.6, 0.0, 0.66), (0.9, 0.44, 0.0, 0.46), (1.0, 0.24, 0.05, 0.24)]
    jaw = [(0, 0.8, -0.5, 0.0), (0.34, 0.76, -0.46, 0.0), (0.68, 0.5, -0.34, 0.0), (0.92, 0.32, -0.24, 0.0), (1.0, 0.16, -0.14, -0.02)]
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.6, lower="Belly", teeth=(12, 11), tall=1.3 * size, base=0.36 * size, fangs=((0.86, 2.5), (0.6, 1.5)), low_fangs=((0.8, 2.0),),
                     seed=seed, t0=0.22, throat=1.1)
    throat_glow(m, y + length * 0.18, zm, width, height)
    for side in (-1, 1):
        tox_eye(m, at(0.4, 0.74 if side > 0 else math.pi - 0.74), 0.66 * size, (side * 0.34, 0.93, -0.08), side, socket=1.9, ridge_size=1.4)
        tox_eye(m, at(0.24, 0.42 if side > 0 else math.pi - 0.42), 0.34 * size, (side * 0.9, 0.4, 0.0), side, socket=1.6, pupil="Slit", ridge=None)
        ear = at(0.12, 1.05 if side > 0 else math.pi - 1.05)
        horn(m, "Claw", tuple(ear - Vector((0, 0, 0.4))), tuple(ear + Vector((side * 1.8, -4.0, 3.6)) * size), 1.3 * size, droop=-0.5)
        sac(m, at(0.3, 1.2 if side > 0 else math.pi - 1.2), (side * 0.3, 0, 1), 0.6 * size, "Vein")
        venom(m, (side * width * 0.2, y + length * 0.84, zm - 0.4), 2.2 * size, 0.26 * size)
        egg(m, "Socket", tuple(at(0.95, 1.2 if side > 0 else math.pi - 1.2)), 0.34 * size, 0.3 * size, 0.2 * size, 8, 4)
    for t, tall in ((0.14, 2.4), (0.3, 1.8)):
        spot = at(t, math.pi / 2)
        horn(m, "Claw", tuple(spot - Vector((0, 0, 0.3))), tuple(spot + Vector((0, -tall * 0.7, tall)) * size), 1.0 * size)


def rot_weiler():
    """Three heads on one starved body the colour of a bruise, and where a hound has hackles, acid burning."""
    m = monster("dino_RotWeiler", Body="#3d1670", Accent="#100818", Belly="#cfe83a", Claw="#f1f5c4")
    m.joint("Spine", (0, -8.0, 12.0))
    m.joint("Triad", (0, 2.0, 13.0), "Spine")
    rings = [((0, -15.0, 11.0), 2.6, 2.6), ((0, -13.0, 11.6), 7.0, 7.4), ((0, -8.0, 12.0), 7.6, 7.6), ((0, -3.0, 12.4), 8.6, 9.0), ((0, 2.0, 13.2), 13.0, 11.6), ((0, 6.0, 13.6), 16.0, 10.6),
             ((0, 8.4, 13.4), 15.0, 8.0)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Triad", "Triad", "Triad"]
    sweep_fine(m, "Body", rings, bones, sides=18, under="Belly", under_faces=5, per=4)
    stripes(m, rings, (2.5, 2.9, 3.3, 3.7), "Accent", bones, grow=1.04, length=0.5)  # ribs
    cluster(m, rings, [(4.4, 0.75, 1.3), (5.2, 1.0, 1.1), (3.6, 1.0, 0.9), (1.6, 0.9, 0.9), (4.8, 0.2, 0.9)], role="Vein", bones=bones)
    # The mane: tongues of acid down its back, never still (Wriggle).
    for n, (u, tall, lean) in enumerate(((5.4, 5.0, 0.2), (4.6, 6.4, 0.5), (3.8, 5.6, 0.7), (3.0, 4.6, 0.8), (2.2, 3.8, 0.9), (1.4, 3.0, 1.0)), start=1):
        at, normal = skin_at(rings, u, math.pi / 2)
        root = at - normal * 0.5
        pts = curve([root, root + Vector((0, -tall * lean * 0.3, tall * 0.4)), root + Vector((0, -tall * lean * 0.8, tall * 0.8)), root + Vector((0, -tall * lean * 1.5, tall))], 7)
        chain(m, "Wriggle", n, pts, 2.2, 0.2, parent=bones[round(u)], role="Glow", sides=6)
        m.bone = bones[round(u)]
        ring_round(m, "Accent", tuple(at + normal * 0.05), 1.25, tuple(normal), 0.6, 10)
    for letter, side in (("L", -1), ("R", 1)):
        leg(m, f"Front{letter}", "Spine", [(side * 5.4, 4.0, 11.4), (side * 7.0, 5.4, 7.0), (side * 6.6, 3.6, 3.2), (side * 6.8, 5.0, 0.9)], (4.8, 3.0, 2.0, 2.2), toes=3, toe=(0.9, 2.8, 0.8), pad=1.5,
            spur=(1, 2.2, 1.2))
        leg(m, f"Back{letter}", "Spine", [(side * 3.8, -11.0, 11.2), (side * 5.6, -8.4, 6.6), (side * 5.4, -12.2, 3.4), (side * 5.6, -10.4, 0.9)], (5.6, 3.2, 2.0, 2.2), toes=3, toe=(0.9, 2.6, 0.8), pad=1.5,
            spur=(2, 2.4, 1.2))
    m.bone = "Spine"
    path = [(p, w, w) for p, w in zip(curve([(0, -14.4, 11.2), (0, -18.0, 12.6), (0, -22.0, 12.0), (0, -25.4, 9.4)], 8), (2.6, 2.2, 1.8, 1.5, 1.2, 1.0, 0.9, 0.9))]
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], path, sides=8)
    m.bone = "Tail3"  # a lantern of venom on the end of it, in thorns
    egg(m, "Glow", (0, -26.2, 8.6), 1.7, 1.7, 1.7, 10, 6)
    ring_round(m, "Accent", (0, -25.7, 9.1), 1.5, (0, -0.5, -0.8), 0.6, 10)
    for k in range(5):
        a = k * math.tau / 5
        d = Vector((math.cos(a), -0.5, math.sin(a) - 0.5)).normalized()
        point(m, "Claw", tuple(Vector((0, -26.2, 8.6)) + d * 1.2), tuple(Vector((0, -26.2, 8.6)) + d * 3.4), 0.9)
    # The side heads first (fierce_head only knows the names Head and Jaw), then the middle one. Each side head rides a Sway bone, so
    # it weaves on its own between attacks.
    for letter, side, n, seed in (("L", -1, 7, 51), ("R", 1, 8, 52)):
        m.joint(f"Neck{letter}", (0, 7.6, 12.8), "Triad")
        hound_head(m, f"Neck{letter}", (0, 6.8, 12.8), 10.6, 11.2, 0.86, seed)
        shift(m, [f"Neck{letter}", "Head", "Jaw"], (side * 7.6, 0, 0))
        rename_bones(m, {"Head": f"Sway{n}a", "Jaw": f"Jaw{letter}"})
    m.joint("Neck", (0, 8.6, 14.6), "Triad")
    hound_head(m, "Neck", (0, 7.6, 14.4), 12.4, 14.6, 1.0, 53)
    m.head_centre = (0, 19.0, 15.0)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Acid Reign


def acid_reign():
    """A king cobra, black in hazard bands, standing on its own coils, its hood two fans of spines; and its crown, which touches nothing."""
    m = monster("dino_AcidReign", Body="#17111f", Accent="#f4d01c", Belly="#9bd61e", Claw="#f6f9d0")
    m.joint("Spine", (0, -2.0, 2.6))
    route = [(0, -2.0, 2.6), (0, 1.6, 6.0), (0, 0.8, 10.0), (0, -1.4, 14.0), (0, -1.2, 18.0), (0, 1.2, 22.0), (0, 4.2, 25.4), (0, 6.6, 27.4)]
    widths = [8.0, 7.8, 7.0, 6.4, 6.6, 7.4, 6.0, 5.0]
    bones = ["Spine", "Rear1", "Rear1", "Rear2", "Rear2", "Rear3", "Neck", "Neck"]
    m.joint("Rear1", (0, 0.6, 4.6), "Spine")
    m.joint("Rear2", (0, -0.6, 12.0), "Rear1")
    m.joint("Rear3", (0, 0.0, 20.0), "Rear2")
    m.joint("Neck", (0, 2.8, 24.0), "Rear3")
    rings = [(p, w, w * 0.9) for p, w in zip(route, widths)]
    sweep_fine(m, "Body", rings, bones, sides=18, under="Belly", under_faces=5, per=5, up=(0, -1, 0.2))
    path, ring_bones = rare_kit.fine(rings, bones, 5)
    for i in range(3, len(path) - 3, 5):  # hazard bands
        p, w, h = path[i]
        ahead = unit(Vector(path[i + 1][0]) - Vector(path[i - 1][0]))
        band(m, "Accent", p, w * 1.04, h * 1.04, length=1.0, bone=ring_bones[i], tilt=tuple(ahead))
    # The coils it stands on: its tail, lying behind it in an S, slithering (Slither1 to 6).
    tail = curve([(0, -2.0, 2.6), (3.4, -7.0, 2.3), (0, -12.0, 2.0), (-3.4, -17.0, 1.6), (0, -22.0, 1.2), (2.6, -26.0, 0.8), (1.0, -29.6, 0.5)], 19)
    m.bone = "Spine"
    egg(m, "Body", (0, -2.0, 2.8), 4.4, 4.4, 2.8, 14, 6)
    jointed(m, "Body", [f"Slither{n}" for n in range(1, 7)], [(p, 7.6 - 0.39 * i, (7.6 - 0.39 * i) * 0.7) for i, p in enumerate(tail)], sides=12, under="Belly", under_faces=3)
    m.bone = "Slither6"
    egg(m, "Glow", (1.0, -30.0, 0.9), 0.8, 1.2, 0.8, 8, 5)  # a rattle of venom
    # The hood: a fan of spines each side of the neck, a glowing eye painted on each. They lie back along it, and fling wide.
    for letter, side in (("L", -1), ("R", 1)):
        root = Vector((side * 2.6, 0.2, 22.4))
        m.use(f"Frill{letter}", tuple(root), "Rear3")
        knob(m, "Body", root, 1.6)
        for k, (dy, dz, long_) in enumerate(((-3.0, 6.4, 8.6), (-5.6, 3.6, 9.8), (-6.6, 0.4, 10.2), (-5.8, -2.8, 9.2), (-3.6, -5.6, 7.6))):
            tip = root + Vector((side * 2.4, dy, dz)).normalized() * long_
            horn(m, "Claw", tuple(root), tuple(tip), 1.0, count=5)
            if k < 4:
                dy2, dz2, long2 = ((-5.6, 3.6, 9.8), (-6.6, 0.4, 10.2), (-5.8, -2.8, 9.2), (-3.6, -5.6, 7.6))[k]
                tip2 = root + Vector((side * 2.4, dy2, dz2)).normalized() * long2
                web = [root, root.lerp(tip, 0.86), root.lerp(tip2, 0.86)]
                normal = unit((web[1] - web[0]).cross(web[2] - web[0])) * 0.14
                rare_kit.poly(m, "Accent" if k % 2 == 0 else "Body", [tuple(q - normal) for q in web], tuple(normal * 2))
        spot = root + Vector((side * 1.9, -4.6, 0.6))
        egg(m, "Vein", tuple(spot), 0.7, 1.5, 1.5, 10, 6)
    m.use("Head", (0, 6.6, 27.6), "Neck")
    skull = [(0, 0.8, 0.0, 0.8), (0.2, 1.0, 0.0, 0.96), (0.44, 0.94, 0.0, 0.8), (0.7, 0.66, 0.0, 0.54), (0.9, 0.44, 0.0, 0.36), (1.0, 0.22, 0.04, 0.2)]
    jaw = [(0, 0.78, -0.44, 0.0), (0.34, 0.8, -0.44, 0.0), (0.68, 0.56, -0.32, 0.0), (0.92, 0.34, -0.22, 0.0), (1.0, 0.16, -0.14, -0.02)]
    y, zm, length, width, height = 6.0, 26.6, 11.0, 8.4, 4.4
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.7, lower="Belly", teeth=(11, 10), tall=1.2, base=0.38, fangs=((0.84, 3.4),), low_fangs=((0.7, 1.6),), seed=61, t0=0.26,
                     jaw_length=1.04, throat=1.1)
    throat_glow(m, y + length * 0.18, zm, width, height)
    for side in (-1, 1):
        tox_eye(m, at(0.5, 0.8 if side > 0 else math.pi - 0.8), 0.72, (side * 0.3, 0.94, -0.1), side, socket=1.9, ridge_size=1.4, ridge="Accent")
        tox_eye(m, at(0.3, 0.46 if side > 0 else math.pi - 0.46), 0.4, (side * 0.86, 0.5, 0.0), side, socket=1.6, pupil="Slit", ridge=None)
        tox_eye(m, at(0.7, 1.1 if side > 0 else math.pi - 1.1), 0.34, (side * 0.2, 0.9, 0.36), side, socket=1.6, pupil="Slit", ridge=None)
        venom(m, (side * width * 0.19, y + length * 0.8, zm - 0.4), 3.0, 0.3)
        egg(m, "Socket", tuple(at(0.95, 1.2 if side > 0 else math.pi - 1.2)), 0.36, 0.3, 0.2, 8, 4)
        spot = at(0.16, 0.9 if side > 0 else math.pi - 0.9)
        horn(m, "Claw", tuple(spot - Vector((0, 0, 0.4))), tuple(spot + Vector((side * 2.6, -4.6, 2.8))), 1.3, droop=-0.6)
    # The crown: a hoop of thorns in the air over its head, a light in the middle of it. The hoop turns for ever (Halo); the light is
    # the bone the attack moves (Crown), so the whole crown tips over its face.
    c = Vector((0, 9.6, 36.2))
    m.use("Crown", tuple(c), "Head")
    egg(m, "Glow", tuple(c), 1.2, 1.2, 1.2, 10, 6)
    m.use("Halo", tuple(c), "Crown")
    where = hoop(m, "Accent", c, 4.6, (0, 0, 1), 1.0, count=20, spikes=8, spike=3.4, spike_role="Claw", spike_w=1.3, lean=0.9)
    for k in range(8):
        spot, out = where((k + 0.5) * math.tau / 8)
        egg(m, "Vein" if k % 2 else "Glow", tuple(spot + out * 0.3), 0.62, 0.62, 0.62, 8, 5)
        horn(m, "Claw", tuple(spot), tuple(spot + out * 0.6 + Vector((0, 0, 1.9))), 0.8, count=4)
    for k in range(4):  # four spokes of light, thin, holding the hoop to its heart
        spot, out = where(k * math.tau / 4)
        sweep(m, "Glow", [(tuple(c + out * 0.9), 0.3, 0.3), (tuple(spot - out * 0.4), 0.16, 0.16)], sides=5)
    m.head_centre = (0, 14.0, 27.0)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Cap Punishment


def saw_cap(m, centre, r):
    """A death cap turned on its side for a saw: a dark disc, a rim of light and hooked teeth of it all round. Spins on the Saw bone."""
    c = Vector(centre)
    sweep(m, "Cap", [(tuple(c + Vector((-0.75, 0, 0))), r * 1.5, r * 1.5), (tuple(c + Vector((-0.45, 0, 0))), r * 2, r * 2), (tuple(c + Vector((0.45, 0, 0))), r * 2, r * 2),
                     (tuple(c + Vector((0.75, 0, 0))), r * 1.5, r * 1.5)], sides=20, up=(0, 0, 1))
    for sx in (-1, 1):
        knob(m, "CapDark", c + Vector((sx * 0.7, 0, 0)), 1.5)
        ring_round(m, "Glow", tuple(c + Vector((sx * 0.72, 0, 0))), r * 0.62, (1, 0, 0), 0.4, 20)
    teeth = 10
    for k in range(teeth):
        a = k * math.tau / teeth
        out = Vector((0, math.cos(a), math.sin(a)))
        rake = Vector((0, math.cos(a + 0.5), math.sin(a + 0.5)))
        point(m, "Glow", tuple(c + out * r * 0.9), tuple(c + out * r * 0.9 + rake * 2.6), 1.8)


def cap_punishment():
    """A tyrant in wasp orange and black, small arms, a head that is mostly teeth; and out of its back an arm with a saw on it."""
    m = monster("dino_CapPunishment", Body="#f08a12", Accent="#15101c", Belly="#f5e9a0", Claw="#2a1040", Cap="#2a1640", CapDark="#120a1e")
    m.joint("Spine", (0, -3.0, 13.0))
    m.joint("Neck", (0, 5.0, 17.6), "Spine")
    m.joint("Head", (0, 7.4, 17.4), "Neck")
    rings = [((0, -9.0, 11.0), 4.0, 4.0), ((0, -6.0, 13.0), 10.0, 9.0), ((0, -2.0, 15.0), 13.0, 11.0), ((0, 2.0, 17.0), 13.0, 10.6), ((0, 5.4, 18.0), 9.4, 8.4), ((0, 8.0, 18.2), 7.4, 6.6)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Neck", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=20, under="Belly", under_faces=7, per=4)
    blotch(m, rings, [(1.5, 1.0, 2.0, 1.6), (2.2, 0.6, 1.8, 2.4), (3.0, 0.9, 1.8, 1.8), (3.8, 0.7, 1.3, 1.5), (1.2, 0.4, 1.4, 1.8), (2.8, 0.25, 1.4, 2.0)], bones=bones)
    cluster(m, rings, [(3.4, 0.5, 1.1), (2.4, 0.9, 1.0), (1.6, 0.6, 0.9), (4.2, 1.0, 0.8)], role="Vein", bones=bones)
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee, ankle, foot = Vector((side * 4.6, -3.2, 12.0)), Vector((side * 6.8, 1.6, 7.2)), Vector((side * 6.2, -3.4, 3.0)), Vector((side * 6.4, -1.2, 0.9))
        m.use(f"Leg{letter}", tuple(hip))
        knob(m, "Body", hip, 3.6)
        limb(m, "Body", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.6, 0.4, 0.4)), knee], (6.6, 5.6, 3.6), sides=14)
        band(m, "Accent", tuple(hip.lerp(knee, 0.5) + Vector((side * 0.4, 0.3, 0.3))), 6.5, 6.5, length=1.2, tilt=tuple(knee - hip))
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        knob(m, "Accent", knee, 2.1)
        point(m, "Claw", tuple(knee), tuple(knee + Vector((side * 0.8, 2.6, 1.8))), 1.5)
        limb(m, "Body", [knee, knee.lerp(ankle, 0.5) + Vector((0, -0.6, 0)), ankle, foot, foot + Vector((0, 3.0, -0.1))], (3.4, 2.6, 2.2, 2.4, 2.8), sides=10)
        band(m, "Accent", tuple(knee.lerp(ankle, 0.6) + Vector((0, -0.5, 0))), 2.9, 2.9, length=0.9, tilt=tuple(ankle - knee))
        talons(m, foot + Vector((0, 2.6, 0)), (0, 1, -0.15), 3, 1.2, 3.8, 1.0)
        shoulder, elbow, wrist = Vector((side * 5.6, 4.6, 15.8)), Vector((side * 7.6, 6.0, 12.6)), Vector((side * 6.6, 9.4, 11.4))
        m.use(f"Arm{letter}", tuple(shoulder))
        knob(m, "Body", shoulder, 1.7)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5), elbow, elbow.lerp(wrist, 0.5), wrist], (2.6, 2.2, 1.7, 1.5, 1.5), sides=10)
        for o in (-0.5, 0.5):
            sabre(m, "Claw", [tuple(wrist + Vector((o, 0, 0))), tuple(wrist + Vector((o * 1.5, 2.2, -0.3))), tuple(wrist + Vector((o * 1.7, 3.0, -2.8)))], 0.9, 8)
    m.bone = "Spine"
    tail = curve([(0, -8.4, 11.6), (0, -13.0, 11.0), (0, -18.0, 9.4), (0, -24.0, 7.4)], 8)
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(tail, (6.0, 5.0, 4.0, 3.2, 2.5, 1.9, 1.3, 0.4))], sides=10, under="Belly", under_faces=3)
    for k in (2, 4, 6):
        p = Vector(tail[k])
        m.bone = "Tail1" if k < 3 else "Tail2" if k < 6 else "Tail3"
        band(m, "Accent", tuple(p), 4.3 - 0.45 * k, 4.3 - 0.45 * k, length=0.9, tilt=tuple(Vector(tail[k + 1]) - Vector(tail[k - 1])))
    m.bone = "Head"
    skull = [(0, 0.86, 0.0, 0.96), (0.22, 1.0, 0.0, 1.14), (0.46, 0.96, 0.0, 1.0), (0.7, 0.8, 0.0, 0.76), (0.9, 0.64, 0.0, 0.56), (1.0, 0.36, 0.05, 0.3)]
    jaw = [(0, 0.84, -0.6, 0.0), (0.3, 0.96, -0.64, 0.0), (0.62, 0.86, -0.54, 0.0), (0.88, 0.64, -0.4, 0.0), (1.0, 0.32, -0.24, -0.02)]
    y, zm, length, width, height = 7.0, 15.6, 12.6, 9.8, 6.0
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.5, lower="Belly", teeth=(15, 13), tall=1.8, base=0.5, fangs=((0.86, 1.8), (0.6, 1.5), (0.4, 1.4)), rows=2, seed=63, t0=0.2,
                     throat=1.1)
    throat_glow(m, y + length * 0.16, zm, width, height)
    for side in (-1, 1):
        tox_eye(m, at(0.5, 0.84 if side > 0 else math.pi - 0.84), 0.86, (side * 0.3, 0.94, -0.12), side, socket=1.9, ridge_size=1.5)
        tox_eye(m, at(0.34, 0.5 if side > 0 else math.pi - 0.5), 0.46, (side * 0.85, 0.5, 0.0), side, socket=1.6, pupil="Slit", ridge=None)
        venom(m, (side * width * 0.32, y + length * 0.7, zm - 0.7), 3.0, 0.36)
        egg(m, "Socket", tuple(at(0.94, 1.15 if side > 0 else math.pi - 1.15)), 0.5, 0.4, 0.3, 8, 4)
        for t, a_, r in ((0.2, 0.9, 0.9), (0.66, 0.5, 0.7), (0.8, 1.0, 0.6)):
            sac(m, at(t, a_ if side > 0 else math.pi - a_), (side * 0.5, 0.1, 0.8), r, "Vein")
    # The arm: out of its back between the shoulders, up, over its head and down to the saw, in three joints.
    arm = curve([(0, -3.6, 19.4), (0, -9.0, 27.0), (0, -7.0, 36.0), (0, 2.0, 42.0), (0, 12.0, 42.0), (0, 18.0, 38.0)], 16)
    widths = [4.6, 4.2, 3.9, 3.6, 3.4, 3.2, 3.0, 2.9, 2.8, 2.7, 2.6, 2.5, 2.4, 2.3, 2.2, 2.2]
    m.bone = "Spine"
    knob(m, "Body", Vector((0, -3.4, 19.0)), 3.2)
    arm_bones = jointed(m, "Body", ["SawArm1", "SawArm2", "SawArm3"], [(p, w, w) for p, w in zip(arm, widths)], sides=10)
    for i in (2, 4, 7, 9, 12, 14):
        p = Vector(arm[i])
        band(m, "Accent", tuple(p), widths[i] * 1.14, widths[i] * 1.14, length=0.9, bone=arm_bones[i], tilt=tuple(Vector(arm[i + 1]) - Vector(arm[i - 1])))
    for i in (5, 10):  # elbows, with a hook each
        p = Vector(arm[i])
        m.bone = arm_bones[i]
        knob(m, "Accent", p, widths[i] * 0.8)
        back = unit(p - Vector((0, 4, 30)))
        point(m, "Claw", tuple(p), tuple(p + back * 3.4), 1.5)
    centre = Vector((0, 20.0, 34.0))
    m.bone = "SawArm3"
    sweep(m, "Accent", [(tuple(arm[-1]), 2.3, 2.3), (tuple(centre), 1.6, 1.6)], sides=8)  # the wrist the saw turns on
    m.use("Saw", tuple(centre), "SawArm3")
    saw_cap(m, centre, 5.6)
    m.head_centre = (0, 21.0, 15.0)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Sporeactor


def sporeactor():
    """A reactor that walks: a black hull in hazard stripes on four pillars, light in every seam, and over the crater in its back the core."""
    m = monster("dino_Sporeactor", Body="#1b1626", Accent="#f4d01c", Belly="#5b2a8a", Claw="#e9f59a")
    m.joint("Spine", (0, -9.0, 10.0))
    m.joint("Neck", (0, 8.0, 11.0), "Spine")
    m.joint("Head", (0, 10.0, 10.6), "Neck")
    rings = [((0, -16.0, 9.0), 4.0, 4.0), ((0, -13.0, 10.0), 14.0, 10.0), ((0, -7.0, 11.5), 20.0, 13.0), ((0, 0.0, 12.0), 22.0, 14.0), ((0, 6.0, 11.5), 19.0, 12.0), ((0, 10.0, 11.0), 12.0, 9.0)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Spine", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=24, under="Belly", under_faces=7, per=4)
    stripes(m, rings, (1.5, 3.9), "Accent", bones, grow=1.06, length=1.6)  # hazard stripes fore and aft
    stripes(m, rings, (1.9, 3.5), "Glow", bones, grow=1.03, length=0.5)  # and a seam of light inside each
    cluster(m, rings, [(2.2, 0.25, 1.5), (3.0, 0.2, 1.7), (3.8, 0.3, 1.3), (1.3, 0.5, 1.1), (4.4, 0.7, 1.0)], role="Vein", bones=bones)
    for u in (1.3, 4.4, 4.9):  # spikes fore and aft of the crater
        at, n = skin_at(rings, u, math.pi / 2)
        m.bone = bones[round(u)]
        horn(m, "Claw", tuple(at - n * 0.4), tuple(at + n * 4.0 + Vector((0, -1.6 if u < 2 else 1.6, 0))), 2.0)
    for letter, side in (("L", -1), ("R", 1)):
        leg(m, f"Front{letter}", "Spine", [(side * 8.5, 5.0, 10.0), (side * 11.8, 6.0, 6.6), (side * 11.2, 5.0, 3.2), (side * 11.4, 6.4, 1.2)], (7.4, 5.8, 4.8, 5.0), toes=3, toe=(1.5, 3.0, 1.2),
            pad=3.0, spur=(1, 3.0, 1.8))
        band(m, "Accent", (side * 11.4, 5.4, 4.6), 6.0, 6.0, length=1.1, bone=f"Front{letter}", tilt=(0, 0.2, -1))
        leg(m, f"Back{letter}", "Spine", [(side * 8.0, -11.0, 10.0), (side * 11.8, -9.4, 6.8), (side * 11.2, -12.0, 3.4), (side * 11.4, -10.4, 1.2)], (8.2, 6.2, 5.0, 5.2), toes=3, toe=(1.5, 3.0, 1.2),
            pad=3.2, spur=(1, 3.2, 1.8))
        band(m, "Accent", (side * 11.4, -11.4, 4.8), 6.3, 6.3, length=1.1, bone=f"Back{letter}", tilt=(0, -0.2, -1))
        for u in (2.0, 2.6, 3.2, 3.8):  # a row of hooks down each flank
            at, n = skin_at(rings, u, 0.5 if side > 0 else math.pi - 0.5)
            m.bone = "Spine"
            horn(m, "Claw", tuple(at - n * 0.4), tuple(at + n * 3.2 + Vector((0, -1.0, 1.0))), 1.6)
    m.bone = "Spine"
    tail = curve([(0, -15.4, 9.4), (0, -19.0, 9.0), (0, -22.6, 7.8), (0, -25.6, 6.4)], 7)
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(tail, (6.0, 5.0, 4.2, 3.6, 3.2, 3.0, 3.0))], sides=10)
    m.bone = "Tail3"
    egg(m, "Glow", (0, -26.6, 6.0), 2.4, 2.4, 2.4, 10, 6)
    band(m, "Accent", (0, -26.6, 6.0), 5.0, 5.0, length=1.0, tilt=(0, 1, 0.4))
    for k in range(6):
        a = k * math.tau / 6
        d = Vector((math.cos(a), -0.3, math.sin(a))).normalized()
        point(m, "Claw", tuple(Vector((0, -26.6, 6.0)) + d * 2.0), tuple(Vector((0, -26.6, 6.0)) + d * 4.6), 1.3)
    # The crater in its back, light down inside it, and six rods round it that rise as the core charges (Rod1 to 6).
    pit = Vector((0, -2.0, 18.5))
    m.bone = "Spine"
    ring_round(m, "Accent", tuple(pit), 5.4, (0, 0, 1), 2.0, 18)
    egg(m, "Glow", tuple(pit + Vector((0, 0, 0.2))), 4.6, 4.6, 1.5, 14, 5)
    for n, (sx, dy) in enumerate(((-1, -6.5), (-1, 0.0), (-1, 6.5), (1, -6.5), (1, 0.0), (1, 6.5)), start=1):
        at, normal = skin_at(rings, 2.72 + dy / 6.5 * 0.95, 1.02 if sx > 0 else math.pi - 1.02)
        m.bone = "Spine"
        ring_round(m, "Accent", tuple(at + Vector((0, 0, 0.1))), 1.5, (0, 0, 1), 0.8, 10)
        m.use(f"Rod{n}", tuple(at), "Spine")
        sweep(m, "Glow", [(tuple(at + Vector((0, 0, -6.0))), 2.0, 2.0), (tuple(at + Vector((0, 0, 1.3))), 2.0, 2.0), (tuple(at + Vector((0, 0, 1.9))), 1.0, 1.0)], sides=6, up=(0, 1, 0))
        sweep(m, "Accent", [(tuple(at + Vector((0, 0, 0.75))), 2.3, 2.3), (tuple(at + Vector((0, 0, 1.2))), 2.3, 2.3)], sides=6, up=(0, 1, 0))
    # The core: a ball of light in a dark cage, and two rings round it, one upright and one level, each turning on an axis that lies in
    # its own plane (Halo, Hoop), so together they tumble like a gyroscope.
    c = Vector((0, -2.0, 30.5))
    m.use("Core", tuple(c), "Spine")
    egg(m, "Spore", tuple(c), 3.3, 3.3, 3.3, 14, 8)
    for normal in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        ring_round(m, "Body", tuple(c), 3.3, normal, 0.7, 16)
    for sz in (-1, 1):
        point(m, "Claw", tuple(c + Vector((0, 0, sz * 3.0))), tuple(c + Vector((0, 0, sz * 5.4))), 1.3)
    m.use("Halo", tuple(c), "Core")
    where = hoop(m, "Vein", c, 5.9, (0, 1, 0), 0.9, count=24, spikes=6, spike=1.8, spike_role="Claw", spike_w=1.1)
    for k in range(6):
        spot, out = where((k + 0.5) * math.tau / 6)
        egg(m, "Accent", tuple(spot), 0.8, 0.8, 0.8, 8, 5)
    m.use("Hoop", tuple(c), "Core")
    where = hoop(m, "Glow", c, 7.6, (0, 0, 1), 0.9, count=28, spikes=8, spike=2.0, spike_role="Claw", spike_w=1.1)
    for k in range(8):
        spot, out = where((k + 0.5) * math.tau / 8)
        egg(m, "Accent", tuple(spot), 0.8, 0.8, 0.8, 8, 5)
    m.bone = "Head"
    skull = [(0, 0.9, 0.0, 0.9), (0.24, 1.0, 0.0, 1.0), (0.5, 0.96, 0.0, 0.82), (0.74, 0.8, 0.0, 0.58), (0.92, 0.6, 0.0, 0.4), (1.0, 0.32, 0.04, 0.2)]
    jaw = [(0, 0.9, -0.62, 0.0), (0.3, 1.0, -0.68, 0.0), (0.62, 0.9, -0.56, 0.0), (0.88, 0.66, -0.4, 0.0), (1.0, 0.3, -0.24, -0.02)]
    y, zm, length, width, height = 9.0, 9.4, 13.0, 14.4, 6.6
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.52, lower="Belly", teeth=(17, 15), tall=1.9, base=0.6, fangs=((0.86, 1.9), (0.6, 1.5), (0.36, 1.4)), rows=2, seed=65, t0=0.2,
                     throat=1.15)
    egg(m, "Glow", (0, y + length * 0.2, zm - height * 0.1), width * 0.24, width * 0.1, height * 0.32, 12, 6)  # lit from inside
    for side in (-1, 1):
        tox_eye(m, at(0.52, 0.86 if side > 0 else math.pi - 0.86), 1.0, (side * 0.3, 0.94, -0.12), side, socket=1.9, ridge_size=1.5, ridge="Accent")
        tox_eye(m, at(0.36, 0.5 if side > 0 else math.pi - 0.5), 0.56, (side * 0.8, 0.6, 0.0), side, socket=1.6, pupil="Slit", ridge=None)
        tox_eye(m, at(0.7, 1.15 if side > 0 else math.pi - 1.15), 0.48, (side * 0.15, 0.9, 0.4), side, socket=1.6, pupil="Slit", ridge=None)
        tox_eye(m, at(0.22, 0.95 if side > 0 else math.pi - 0.95), 0.44, (side * 0.5, 0.5, 0.7), side, socket=1.6, pupil="Slit", ridge=None)
        spot = at(0.2, 0.5 if side > 0 else math.pi - 0.5)  # horns: a pair swept forward like a bull's, a pair back
        horn(m, "Claw", tuple(spot - Vector((side * 0.5, 0, 0))), tuple(spot + Vector((side * 6.0, 7.0, 3.0))), 2.6, droop=1.6, count=9)
        spot = at(0.1, 1.0 if side > 0 else math.pi - 1.0)
        horn(m, "Claw", tuple(spot - Vector((0, 0, 0.5))), tuple(spot + Vector((side * 4.0, -5.0, 5.0))), 2.2, droop=-1.4, count=8)
        venom(m, (side * width * 0.34, y + length * 0.66, zm - 0.8), 3.6, 0.44)
        egg(m, "Socket", tuple(at(0.93, 1.2 if side > 0 else math.pi - 1.2)), 0.7, 0.5, 0.3, 8, 4)
        for t, a_, r in ((0.84, 0.8, 0.7), (0.62, 0.45, 0.9), (0.42, 0.3, 0.9)):
            sac(m, at(t, a_ if side > 0 else math.pi - a_), (side * 0.6, 0.2, 0.7), r, "Vein")
    m.head_centre = (0, 25.0, 10.0)
    grounded(m)
    return m


ALL = [rot_weiler, acid_reign, cap_punishment, sporeactor]


def main():
    apex_kit.run(ALL, RENDERS, BLEND, SKY, FLOOR, GLOW_ROLES, glow=0.55, spacing=70)


if __name__ == "__main__":
    main()
