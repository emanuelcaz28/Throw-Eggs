"""Builds Shattered Mirror's six rarest monsters (map 16, the 7th to 12th), animates them and renders them (Blender, background mode).

    Blender -b -P build_shattered_mirror_rare.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_shattered_mirror_rare.py    (stills only)
    POSE="0.6 1.9 2.4" QUICK_OUT=<folder> ...                                  (each one's attack at those seconds)
    ONLY=royal_pane ...                                                        (just those)

Saves shattered_mirror_rare.blend and renders to design/world/monsters_shattered_mirror_rare/.

The owner, 2026-11-14, on the first six (build_shattered_mirror_monsters.py): only the swan was good; the rest shared one mouth and
one set of teeth on four legs or a human shape. For these: "something unique", "more complex, something actually wow", two feet but
"not an actual humanoid body", and "I want them shards to be floating and waving and doing stuff". "The rarest ones are the most
important", they "must look the best". So here: no shared head (bills, a prism, a mouthless moth, a hooked beak, a face behind glass,
a helmed dragon), no rows of teeth, bodies on two bird or raptor legs or in the air, and on every one shards that float free of the
body and never stop moving. Most common first:

  Stilt Life        a porcelain wader on gilt stilts, a dagger of a bill, and for wings two fans of mirror blades hanging in the air
                    beside it, rippling. It coils its neck and stabs three times, the blades flung wide (Stilt, VaneL/R1-5)
  Prism Break       a midnight raptor whose head is a prism with a visor of cold light, a sail of rainbow glass floating over its
                    back in a wave. It drops its head, the sail tips forward and fires blade after blade ahead, and it charges (Prism, Sail1-7)
  Moth-er of Pearl  a pearl moth in the air on four wings of mirror and stained glass, false eyes on the hind pair, no mouth, two
                    rings of shards circling it opposite ways. It climbs, claps its wings shut twice and dives (Flutter, LoopA, LoopB)
  Vainglory         a sapphire peacock with a hooked gilt beak, a train of thirteen mirror eyes floating behind it in a fan, a wave
                    always running through them. It throws the fan up, shivers it, struts at you screaming, and the eyes stab outward
                    from the middle (Train, Eye1-13)
  Mirror Mirror     the world's standing mirror, walking on two great bird legs: a gilt frame, cracked glass, and in the hole in the
                    middle two cold eyes. Two rings of shards wheel round it opposite ways. The glass bursts out of the frame, every
                    piece spinning, and what lives in the mirror leans out and looks round for you (Frame, Glass1-8, LoopA, LoopB)
  Royal Pane        the rarest: a white and gold wyvern, helmed in chrome, horned, a ring of shards turning over its head, and wings
                    whose skin is stained glass: panes floating between gilt fingers, rippling. It rears, spreads, and beats its
                    wings forward so the panes fly out at you and back, roaring (Royal, PaneL/R1-5, Tiara)

Chrome and gilt are metal in the game (METAL), the rainbow glass glows (SPECTRUM), eyes are the world's cold cyan. Skin roles Body,
Accent, Belly and Claw take the colour mutations. What moves is in the tables at the bottom, the same as the map-16 block in
DinoLifeController, number for number; "@always" moves run all the time, the rest once every DinoLife.attackCycle. 1 Blender unit =
1 stud, models face +Y, feet on Z = 0 (the moth hovers on a Swim bone). Plain colours, no stud image.
"""
import math
import os
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402  (first: it turns the stud preview off)
import build_forest as kit  # noqa: E402
import build_shattered_mirror_monsters as first  # noqa: E402
import monster_stage  # noqa: E402
from build_abyss_monsters import hover_pose, swim_pose  # noqa: E402
from build_clockwork_citadel_monsters_7_8 import limb  # noqa: E402
from build_shattered_mirror_monsters import (ALWAYS, GLOW_ROLES, METAL, SPECTRUM, along, grown, mark, mirrored, monster, right_of, shaken, shard,  # noqa: E402, F401
                                             spun)
from build_spore_hollow_monsters import egg  # noqa: E402
from build_spore_hollow_toxic import grounded, skin_at, stripes, tox_eye, unit  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from build_volcano import idle_pose as volcano_idle, walk_pose as volcano_walk  # noqa: E402
from fierce_kit import horn, knob  # noqa: E402
from rare_kit import (AHEAD, PITCH, RISE, ROLL, W, WALK_PREVIEW, YAW, beat, chain, curve, jointed, keys, leaf, marked_of, poly, ring_round, sabre,  # noqa: E402
                      stacked, sway, sweep, sweep_fine, wave)

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_shattered_mirror_rare"
BLEND = "shattered_mirror_rare"  # for check_map.py and export_fbx.py
SKY, FLOOR = first.SKY, first.FLOOR


# ---------------------------------------------------------------------- shapes


def blade(m, role, base, tip, w, thick=0.2, up=(1, 0, 0), belly=0.35):
    """A flat shard of mirror: broad one way (across `up` and its length), thin the other, cut to a point."""
    a, b = Vector(base), Vector(tip)
    k = 1.414  # a four-sided sweep is this much narrower than its width says
    sweep(m, role, [(tuple(a), w * 0.3 * k, thick * k), (tuple(a.lerp(b, belly)), w * k, thick * k), (tuple(a.lerp(b, 0.8)), w * 0.55 * k, thick * 0.8 * k),
                    (tuple(b), 0.04, 0.04)], sides=4, up=up)


def eye(m, at, r, look, side, lid="Body", ridge="Chrome", main=True):
    tox_eye(m, tuple(at), r, look, side, socket=1.7, lid=lid, pupil="Pupil" if main else "Slit", ridge=ridge, ridge_size=1.2, top=0.42, low=0.3)


def bird_leg(m, letter, side, hip, ankle, foot, w, role="Gilt", thigh=None, parent="Spine", toe=2.4):
    """A bird's leg on LegL/R and ShinL/R: a thigh down and back to the ankle, a long shank forward to the foot, three toes ahead and
    one behind, all chrome claws, a spur on the ankle."""
    hip, ankle, foot = Vector(hip), Vector(ankle), Vector(foot)
    m.use(f"Leg{letter}", tuple(hip), parent)
    knob(m, thigh or role, hip, w * 0.8)
    limb(m, thigh or role, [hip, hip.lerp(ankle, 0.5) + Vector((0, w * 0.4, 0)), ankle], (w * 1.4, w, w * 0.55), sides=10)
    m.use(f"Shin{letter}", tuple(ankle), f"Leg{letter}")
    knob(m, "Chrome", ankle, w * 0.42)
    shard(m, "Chrome", tuple(ankle), tuple(ankle + Vector((0, -w * 1.5, w * 0.6))), w * 0.34)
    limb(m, role, [ankle, ankle.lerp(foot, 0.5), foot], (w * 0.5, w * 0.4, w * 0.5), sides=8)
    for a in (-0.55, 0.0, 0.55, math.pi):
        d = Vector((math.sin(a), math.cos(a), 0))
        reach = toe * (0.55 if a == math.pi else 1.0)
        sabre(m, "Chrome", [tuple(foot), tuple(foot + d * reach * 0.6 + Vector((0, 0, 0.2))), tuple(Vector((foot.x, foot.y, 0.06)) + d * reach)], w * 0.38, 6)


def raptor_leg(m, letter, side, hip, knee, ankle, foot, w, role="Body", parent="Spine", toe=2.6):
    """A raptor's leg: a thick thigh forward to the knee (LegL/R), back to the ankle and down to the foot (ShinL/R), chrome talons, one
    of them the big hooked one held off the ground."""
    hip, knee, ankle, foot = Vector(hip), Vector(knee), Vector(ankle), Vector(foot)
    m.use(f"Leg{letter}", tuple(hip), parent)
    knob(m, role, hip, w * 0.85)
    limb(m, role, [hip, hip.lerp(knee, 0.5) + Vector((side * w * 0.12, 0, w * 0.1)), knee], (w * 1.6, w * 1.35, w * 0.9), sides=12)
    m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
    limb(m, role, [knee, knee.lerp(ankle, 0.5), ankle, ankle.lerp(foot, 0.6), foot], (w * 0.9, w * 0.7, w * 0.5, w * 0.46, w * 0.55), sides=10)
    shard(m, "Chrome", tuple(ankle), tuple(ankle + Vector((0, -w * 1.2, w * 0.7))), w * 0.3)
    for a in (-0.45, 0.0, 0.45):
        d = Vector((math.sin(a), math.cos(a), 0))
        sabre(m, "Chrome", [tuple(foot), tuple(foot + d * toe * 0.6 + Vector((0, 0, 0.25))), tuple(Vector((foot.x, foot.y, 0.06)) + d * toe)], w * 0.36, 6)
    inner = foot + Vector((-side * w * 0.35, 0.2, 0.5))
    sabre(m, "Chrome", [tuple(inner), tuple(inner + Vector((0, toe * 0.5, toe * 0.55))), tuple(inner + Vector((0, toe * 0.95, toe * 0.1)))], w * 0.44, 7)


def ring_of_shards(m, centre, radius, count, length, w, axis="yaw", tilt=0.0, roles=("Chrome", "ChromeDark"), start=0.0):
    """Shards hung in a circle round centre, on the bone in use, which turns for ever. axis "yaw": a level ring (tilt leans it); "roll":
    upright, facing ahead, like the hands of a clock. Each shard lies along the circle, so the ring reads as a wheel of knives."""
    c = Vector(centre)
    for k in range(count):
        a = start + k * math.tau / count
        if axis == "yaw":
            out = Vector((math.cos(a), math.sin(a), math.sin(a) * tilt))
            along_ = Vector((-math.sin(a), math.cos(a), math.cos(a) * tilt))
            up = (0, 0, 1)
        else:
            out = Vector((math.cos(a), 0, math.sin(a)))
            along_ = Vector((-math.sin(a), 0, math.cos(a)))
            up = (0, 1, 0)
        p = c + out * radius
        size = length * (1.0 if k % 2 == 0 else 0.7)
        blade(m, roles[k % len(roles)], tuple(p - along_ * size * 0.4), tuple(p + along_ * size * 0.6), w, thick=w * 0.3, up=up)


def volley(order, start, step, rise, hold_to, fall):
    """Keys for one of a row that go out one after another and come back the same way: 0, up to 1, held, back to 0."""
    late = step * order
    return [(0, 0), (start + late, 0), (start + late + rise, 1), (hold_to + late, 1), (hold_to + late + fall, 0), (1, 0)]


# ---------------------------------------------------------------------- Stilt Life

VANES = 5  # blades a side


def stilt_life():
    """A wader of white porcelain, tall on gilt stilts, a black mask and a dagger bill, a crest and two long plumes, and where its wings
    would be, five mirror blades a side hanging in the air."""
    m = monster("dino_StiltLife", Body="#f4efe9", Accent="#1a1730", Belly="#d9d3e8", Claw="#2a2540")
    m.joint("Spine", (0, -1.0, 11.4))
    m.joint("Stilt", (0, 1.6, 12.0), "Spine")
    rings = [((0, -4.6, 11.7), 1.2, 1.0), ((0, -3.0, 11.4), 3.6, 3.2), ((0, -0.5, 11.3), 4.6, 4.2), ((0, 1.8, 12.0), 3.8, 3.6), ((0, 3.2, 12.9), 2.2, 2.2)]
    bones = ["Spine", "Spine", "Spine", "Stilt", "Stilt"]
    sweep_fine(m, "Body", rings, bones, sides=14, under="Belly", under_faces=5, per=4)
    m.bone = "Spine"
    for k in range(7):  # a fan of a tail, mirror and black
        a = (k - 3) * 0.24
        base = Vector((math.sin(a) * 0.6, -4.0, 11.5 + 0.12 * k))
        leaf(m, "Chrome" if k % 2 == 0 else "Accent", tuple(base), tuple(base + Vector((math.sin(a) * 3.0, -5.2, -1.2))), (1, 0, 0), 1.1, thick=0.1)
    neck = curve([(0, 3.0, 12.8), (0, 4.8, 15.0), (0, 3.7, 17.4), (0, 4.4, 19.4), (0, 5.8, 20.2)], 13)
    jointed(m, "Body", ["Neck", "NeckB", "NeckC"], [(p, 1.55 - 0.06 * i, 1.55 - 0.06 * i) for i, p in enumerate(neck)], parent="Stilt", sides=10)
    end = Vector(neck[-1])
    m.use("Head", tuple(end), "NeckC")
    sweep_fine(m, "Body", [(tuple(end + Vector((0, -0.5, 0))), 1.2, 1.3), (tuple(end + Vector((0, 0.5, 0.15))), 1.7, 1.6), (tuple(end + Vector((0, 1.6, 0.05))), 1.15, 1.05)],
               sides=10, per=3)
    for s in (-1, 1):  # the black mask, from the bill back past the eye
        sweep_fine(m, "Socket", [(tuple(end + Vector((s * 0.6, -0.2, 0.3))), 0.14, 0.4), (tuple(end + Vector((s * 0.62, 0.7, 0.22))), 0.14, 0.8),
                                 (tuple(end + Vector((s * 0.42, 1.7, 0.1))), 0.14, 0.6)], sides=4, per=2, up=(1, 0, 0))
        eye(m, end + Vector((s * 0.72, 0.75, 0.28)), 0.27, (s * 0.72, 0.66, 0.05), s, lid="Socket")
    sweep_fine(m, "Chrome", [(tuple(end + Vector((0, 1.5, 0.12))), 1.0, 0.8), (tuple(end + Vector((0, 3.6, -0.2))), 0.6, 0.5), (tuple(end + Vector((0, 6.6, -0.9))), 0.07, 0.07)],
               sides=6, per=3)
    for k, (dx, h) in enumerate(((0, 3.4), (-0.4, 2.6), (0.4, 2.6), (-0.7, 1.8), (0.7, 1.8))):  # the crest
        base = end + Vector((dx, -0.1, 0.6))
        shard(m, "Chrome" if k % 2 == 0 else "ChromeDark", tuple(base), tuple(base + Vector((dx * 0.8, -h * 0.8, h * 0.55))), 0.34)
    for n, s in ((1, -1), (2, 1)):  # two long plumes off the back of its head, swaying
        root = end + Vector((s * 0.3, -0.5, 0.2))
        chain(m, "Sway", n, curve([root, root + Vector((s * 0.5, -2.2, -0.6)), root + Vector((s * 0.9, -4.4, -2.2)), root + Vector((s * 1.0, -5.6, -4.4))], 7),
              0.14, 0.08, parent="Head", role="Accent", flat="side", breadth=0.8)
        m.bone = "Head"
    hinge = end + Vector((0, 1.4, -0.3))
    m.use("Jaw", tuple(hinge), "Head")
    sweep_fine(m, "Gilt", [(tuple(end + Vector((0, 1.5, -0.42))), 0.82, 0.4), (tuple(end + Vector((0, 3.5, -0.62))), 0.5, 0.3), (tuple(end + Vector((0, 6.0, -1.02))), 0.06, 0.06)],
               sides=6, per=3)
    rare_kit.swing(m, ["Jaw"], tuple(hinge), -0.1)
    for letter, side in (("L", -1), ("R", 1)):
        bird_leg(m, letter, side, (side * 1.3, -0.8, 10.2), (side * 1.5, -2.6, 5.6), (side * 1.5, -0.6, 0.7), 1.5, thigh="Body")
        for k in range(1, VANES + 1):  # the blades: off the body, fanned from level to steep, longest on top
            rise = math.radians(-12 + 21 * (k - 1))
            root = Vector((side * (3.5 + 0.12 * k), -0.4 - 0.3 * k, 11.9 + 0.62 * k))
            way = unit(Vector((side * 0.32, -math.cos(rise), math.sin(rise))))
            m.use(f"Vane{letter}{k}", tuple(root), "Stilt")
            blade(m, ("Chrome", "SpecD", "Chrome", "SpecE", "Chrome")[k - 1], tuple(root), tuple(root + way * (5.4 + 0.7 * k)), 1.7, thick=0.2)
    m.bone = "Head"
    m.head_centre = (0, 8.4, 20.0)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Prism Break

SAILS = 7


def prism_break():
    """A raptor the blue of midnight, banded in chrome, whose head is a prism: three flat faces, a visor of cold light for eyes, light
    in its throat instead of teeth. A sail of rainbow glass floats over its back, and three shards trail off the end of its tail."""
    m = monster("dino_PrismBreak", Body="#1d2a5c", Accent="#0d1230", Belly="#9fb4e6", Claw="#f2f6ff")
    m.joint("Spine", (0, -2.0, 8.6))
    m.joint("Prism", (0, 2.4, 9.3), "Spine")
    m.joint("Neck", (0, 4.6, 10.4), "Prism")
    rings = [((0, -6.2, 8.5), 2.4, 2.6), ((0, -3.6, 8.7), 4.6, 5.0), ((0, -0.5, 8.9), 5.0, 5.6), ((0, 2.6, 9.5), 4.2, 4.8), ((0, 4.8, 10.8), 2.9, 3.1),
             ((0, 6.2, 12.2), 2.3, 2.3)]
    bones = ["Spine", "Spine", "Spine", "Prism", "Neck", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=16, under="Belly", under_faces=5, per=4)
    stripes(m, rings, (1.0, 1.7, 2.4, 3.1), "Chrome", bones, grow=1.06, length=0.34)
    tail = curve([(0, -6.0, 8.5), (0, -9.5, 8.9), (0, -13.5, 9.6), (0, -17.5, 10.6)], 10)
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(tail, (2.4, 2.1, 1.8, 1.55, 1.3, 1.1, 0.9, 0.7, 0.5, 0.3))], sides=8, under="Belly")
    tip = Vector(tail[-1])
    for k in range(1, 4):  # shards trailing off the tail, each further off, not touching
        root = tip + Vector((0, -0.9 - 2.3 * (k - 1), 0.25 * k))
        m.use(f"Drift{k}", tuple(root), "Tail3")
        blade(m, ("SpecA", "Chrome", "SpecC")[k - 1], tuple(root), tuple(root + Vector((0, -2.0, 0.3))), 1.3 - 0.25 * k, thick=0.18)
    for letter, side in (("L", -1), ("R", 1)):
        raptor_leg(m, letter, side, (side * 2.1, -1.6, 8.3), (side * 2.6, 1.0, 5.2), (side * 2.5, -2.3, 2.7), (side * 2.5, -0.7, 0.7), 2.0)
        shoulder = Vector((side * 1.9, 3.2, 9.0))
        m.use(f"Arm{letter}", tuple(shoulder), "Prism")
        limb(m, "Body", [shoulder, shoulder + Vector((side * 0.5, 0.4, -1.5)), shoulder + Vector((side * 0.4, 1.7, -2.0))], (1.1, 0.8, 0.6), sides=8)
        for dx in (-0.25, 0.25):
            base = shoulder + Vector((side * 0.4 + dx, 1.7, -2.0))
            sabre(m, "Chrome", [tuple(base), tuple(base + Vector((0, 0.8, -0.2))), tuple(base + Vector((0, 1.2, -0.9)))], 0.3, 5)
    # The head: a prism. The top is a three-sided wedge, a ridge along its crown; the jaw a smaller one upside down; between them, light.
    m.use("Head", (0, 6.2, 12.2), "Neck")
    h = Vector((0, 6.2, 12.3))
    sweep(m, "Chrome", [(tuple(h + Vector((0, -1.3, 0.5))), 2.0, 1.8), (tuple(h + Vector((0, 0.3, 0.7))), 3.9, 3.3), (tuple(h + Vector((0, 2.6, 0.45))), 3.0, 2.3),
                        (tuple(h + Vector((0, 5.6, -0.1))), 0.3, 0.3)], sides=3, turn=math.pi / 2)
    sweep(m, "SpecD", [(tuple(h + Vector((0, 0.2, -0.42))), 1.3, 0.4), (tuple(h + Vector((0, 2.4, -0.48))), 1.0, 0.36), (tuple(h + Vector((0, 4.4, -0.56))), 0.3, 0.2)], sides=4)
    for s in (-1, 1):  # the visor: a strip of light down each side, a dark slit in it; and a shard off each corner of the skull
        a, b = h + Vector((s * 1.18, 0.5, 0.42)), h + Vector((s * 0.52, 3.4, 0.2))
        out = Vector((s * 0.95, 0.2, 0.3)).normalized()
        sweep(m, "EyeGlow", [(tuple(a + out * 0.05), 0.12, 0.62), (tuple(a.lerp(b, 0.5) + out * 0.05), 0.12, 0.5), (tuple(b + out * 0.05), 0.12, 0.16)], sides=4, up=tuple(out))
        sweep(m, "Pupil", [(tuple(a.lerp(b, 0.12) + out * 0.13), 0.1, 0.14), (tuple(a.lerp(b, 0.62) + out * 0.13), 0.1, 0.1)], sides=4, up=tuple(out))
        shard(m, "ChromeDark", tuple(h + Vector((s * 1.0, -0.6, 0.9))), tuple(h + Vector((s * 2.6, -3.4, 2.4))), 0.6)
    shard(m, "Chrome", tuple(h + Vector((0, -0.6, 1.6))), tuple(h + Vector((0, -4.2, 3.6))), 0.7)
    hinge = h + Vector((0, -0.2, -0.5))
    m.use("Jaw", tuple(hinge), "Head")
    sweep(m, "ChromeDark", [(tuple(h + Vector((0, -0.4, -0.95))), 1.7, 1.1), (tuple(h + Vector((0, 1.6, -1.0))), 2.5, 1.5), (tuple(h + Vector((0, 4.9, -0.75))), 0.26, 0.26)],
          sides=3, turn=-math.pi / 2)
    rare_kit.swing(m, ["Jaw"], tuple(hinge), -0.14)
    for k in range(1, SAILS + 1):  # the sail: blades standing in the air over the spine, tallest in the middle
        u = 4.2 - 0.52 * (k - 1)
        at, _ = skin_at(rings, u, math.pi / 2)
        root = at + Vector((0.2 if k % 2 else -0.2, 0, 0.9))  # side by side, not in one plane: where two overlap they'd shimmer
        tall = 5.6 - 0.55 * abs(k - 3.5)
        m.use(f"Sail{k}", tuple(root), bones[min(round(u), len(bones) - 1)])
        blade(m, ("SpecA", "SpecB", "SpecC", "SpecD", "SpecE", "SpecA", "SpecB")[k - 1], tuple(root), tuple(root + Vector((0, -tall * 0.28, tall))), 1.7, thick=0.2)
    m.bone = "Head"
    m.head_centre = (0, 9.0, 12.2)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Moth-er of Pearl

MOTH_Z = 11.0  # it hovers this high


def moth_wing(m, bone, parent, side, root, rays, roles, spot=None):
    """A wing of panes: each ray (a tip) is a long leaf of mirror or glass from the root, each a little lower than the one before so
    none lie in the same place, a gilt rib along the front one. spot: a false eye on the pane of that number."""
    root = Vector(root)
    m.use(bone, tuple(root), parent)
    for k, tip in enumerate(rays):
        tip = Vector(tip)
        base = root + Vector((0, 0, -0.24 * k))
        across = (tip - root).cross(Vector((0, 0, 1)))
        leaf(m, roles[k % len(roles)], tuple(base), tuple(tip + Vector((0, 0, -0.24 * k))), tuple(across), (tip - root).length * 0.42, thick=0.1)
        if spot == k:
            c = root.lerp(tip, 0.62) + Vector((0, 0, 0.12))
            egg(m, "Socket", tuple(c), 1.5, 1.5, 0.12, 14, 4)
            egg(m, "EyeGlow", tuple(c + Vector((0, 0, 0.07))), 1.05, 1.05, 0.1, 12, 4)
            egg(m, "Slit", tuple(c + Vector((0, 0, 0.14))), 0.3, 0.9, 0.08, 8, 4)
    first_tip = Vector(rays[0])
    sweep(m, "Gilt", [(tuple(root + Vector((0, 0, 0.1))), 0.5, 0.4), (tuple(first_tip + Vector((0, 0, 0.1))), 0.12, 0.12)], sides=6)


def mother_of_pearl():
    """A great pearl moth in the air: a furred thorax, a banded tail curling under, feather feelers, a coiled gilt tongue and no mouth,
    four wings of mirror and stained glass, and two rings of shards wheeling round it opposite ways."""
    m = monster("dino_MotherOfPearl", Body="#f1ecf5", Accent="#6b2a66", Belly="#cdbfe6", Claw="#2a2540")
    z = MOTH_Z
    m.joint("Swim", (0, 0, z))
    m.joint("Flutter", (0, 0.6, z + 0.2), "Swim")
    m.bone = "Flutter"
    egg(m, "Body", (0, 0.8, z + 0.3), 2.5, 3.0, 2.5, 16, 8)
    for k in range(12):  # a ruff of fur round its neck
        a = k * math.tau / 12
        base = Vector((math.cos(a) * 1.7, 2.6, z + 0.5 + math.sin(a) * 1.7))
        leaf(m, "Belly", tuple(base), tuple(base + Vector((math.cos(a) * 1.5, -1.3, math.sin(a) * 1.5))), (-math.sin(a), 0, math.cos(a)), 1.3, thick=0.2)
    for s in (-1, 1):  # six thin gilt legs, tucked
        for k in range(3):
            hip = Vector((s * 1.2, 2.0 - 1.3 * k, z - 1.7))
            limb(m, "Gilt", [hip, hip + Vector((s * 1.6, 0.4, -1.2)), hip + Vector((s * 1.2, 1.2, -3.0))], (0.36, 0.26, 0.12), sides=6)
    belly = curve([(0, -1.4, z + 0.1), (0, -4.0, z - 0.3), (0, -6.6, z - 1.5), (0, -8.2, z - 3.4)], 9)
    jointed(m, "Body", ["AbdA", "AbdB"], [(p, w, w) for p, w in zip(belly, (3.4, 3.5, 3.3, 3.0, 2.6, 2.1, 1.6, 1.1, 0.4))], parent="Swim", sides=12, under="Belly")
    for i in (2, 4, 6):  # velvet bands
        p = Vector(belly[i])
        m.bone = "AbdA" if i < 5 else "AbdB"
        ring_round(m, "Accent", tuple(p), (3.4, 3.5, 3.3, 3.0, 2.6, 2.1, 1.6)[i] * 0.52, tuple(Vector(belly[i + 1]) - Vector(belly[i - 1])), 0.3, 14)
    m.bone = "AbdB"
    shard(m, "Chrome", tuple(Vector(belly[-1])), tuple(Vector(belly[-1]) + Vector((0, -1.6, -2.2))), 0.6)
    m.use("Head", (0, 3.4, z + 0.5), "Flutter")
    egg(m, "Body", (0, 4.0, z + 0.5), 1.5, 1.4, 1.4, 12, 6)
    for s in (-1, 1):  # great dark eyes, a cold light deep in each
        c = Vector((s * 1.0, 4.5, z + 0.75))
        egg(m, "Socket", tuple(c), 0.85, 0.8, 0.95, 12, 6)
        look = Vector((s * 0.6, 0.78, 0.1)).normalized()
        egg(m, "EyeGlow", tuple(c + look * 0.56), 0.34, 0.34, 0.2, 10, 5)  # a narrow light, slanted down to the middle: a glare, not a doll's eye
        egg(m, "Pupil", tuple(c + look * 0.8), 0.08, 0.2, 0.16, 8, 4)
        horn(m, "Chrome", tuple(c + Vector((s * 0.5, 0.2, 0.75))), tuple(c + Vector((-s * 0.75, 0.9, 0.3))), 0.5)
    coil = [(0, 5.1 + 0.55 * math.sin(a) * (1 - a / 14), z - 0.5 - 0.55 * (1 - math.cos(a)) * (1 - a / 14)) for a in [i * 0.7 for i in range(14)]]
    sweep(m, "Gilt", [(p, 0.22, 0.22) for p in coil], sides=6)  # its tongue, coiled
    for n, s in ((1, -1), (2, 1)):  # feather feelers, swaying
        root = Vector((s * 0.6, 4.4, z + 1.6))
        pts = curve([root, root + Vector((s * 1.2, 1.2, 1.6)), root + Vector((s * 2.6, 2.0, 2.6)), root + Vector((s * 4.4, 1.6, 3.0))], 7)
        names = chain(m, "Sway", n, pts, 0.2, 0.08, parent="Head", role="Gilt")
        for i in range(1, 7):
            m.bone = names[min((i - 1) // 2, 2)]
            p = Vector(pts[i])
            for d in (-1, 1):
                leaf(m, "Belly", tuple(p), tuple(p + Vector((0.2 * s, d * (1.5 - 0.15 * i), 0.3))), (1, 0, 0.4), 0.4, thick=0.08)
        m.bone = "Head"
    glass = ("Chrome", "SpecE", "Chrome", "SpecD", "Chrome")
    for letter, side in (("L", -1), ("R", 1)):
        fore = [(side * 9.0, 7.5, z + 6.4), (side * 11.8, 4.0, z + 6.6), (side * 12.4, 0.2, z + 5.6), (side * 10.6, -2.6, z + 4.2), (side * 7.4, -3.6, z + 2.8)]
        moth_wing(m, f"Wing{letter}", "Flutter", side, (side * 1.6, 1.8, z + 1.2), fore, glass)
        hind = [(side * 9.4, -5.0, z + 2.6), (side * 8.0, -9.0, z + 2.0), (side * 4.8, -11.0, z + 0.8), (side * 2.2, -9.2, z - 0.2)]
        moth_wing(m, f"Hind{letter}", "Flutter", side, (side * 1.5, -0.4, z + 0.7), hind, ("SpecA", "Chrome", "SpecB", "Chrome"), spot=1)
    m.use("LoopA", (0, 0, z), "Swim")
    ring_of_shards(m, (0, 0, z - 2.0), 8.5, 8, 4.2, 1.5)
    m.use("LoopB", (0, 0, z), "Swim")
    ring_of_shards(m, (0, 0, z + 1.0), 11.0, 10, 3.4, 1.2, tilt=0.3, roles=("SpecC", "Chrome", "SpecA", "Chrome", "SpecD"))
    m.bone = "Head"
    m.head_centre = (0, 4.6, z + 0.6)
    return m


# ---------------------------------------------------------------------- Vainglory

TRAIN_AT = (0, -3.4, 9.2)  # where the train's feathers would meet, if they touched it
TRAIN_UP = (0, -0.57, 0.82)  # the fan's middle feather points this way; the others are spread either side of it
EYES = 13


def train_way(k):
    """The way feather k (1 to 13) of the train points: the fan's own plane, 0.2 radians a feather either side of the middle one."""
    a = (k - 7) * 0.2
    return unit(Vector((1, 0, 0)) * math.sin(a) + unit(TRAIN_UP) * math.cos(a))


def vainglory():
    """A peacock of sapphire glass with a white face and a hooked gilt beak, gilt legs, mirror wings folded on its flanks, a crest
    hanging over its head, and behind it thirteen long mirror feathers in a fan, an eye of coloured light on each, none touching it."""
    m = monster("dino_Vainglory", Body="#2433a0", Accent="#141a52", Belly="#f1ecf5", Claw="#2a2540")
    m.joint("Spine", (0, -1.0, 8.0))
    m.joint("Train", TRAIN_AT, "Spine")
    rings = [((0, -4.8, 8.4), 2.0, 1.8), ((0, -3.0, 8.0), 4.6, 4.2), ((0, -0.4, 7.8), 5.4, 5.0), ((0, 1.8, 8.4), 4.4, 4.4), ((0, 3.0, 9.6), 2.5, 2.7)]
    sweep_fine(m, "Body", rings, ["Spine"] * 5, sides=14, per=4)
    m.bone = "Spine"
    for s in (-1, 1):  # folded wings: rows of mirror feathers down each flank
        for row in range(3):
            for k in range(4):
                base = Vector((s * (2.5 + 0.1 * row + 0.05 * k), 1.6 - 1.5 * k - 0.4 * row, 9.4 - 1.0 * row))
                leaf(m, ("Chrome", "Accent", "ChromeDark")[row], tuple(base), tuple(base + Vector((s * 0.3, -2.6, -1.3))), (0, 0.4, 1), 1.5, thick=0.12)
    neck = curve([(0, 2.6, 9.4), (0, 4.0, 11.6), (0, 3.6, 13.8), (0, 4.0, 15.4)], 10)
    jointed(m, "Body", ["Neck", "NeckB"], [(p, 2.3 - 0.13 * i, 2.3 - 0.13 * i) for i, p in enumerate(neck)], parent="Spine", sides=10)
    end = Vector(neck[-1])
    m.use("Head", tuple(end), "NeckB")
    sweep_fine(m, "Body", [(tuple(end + Vector((0, -0.6, 0))), 1.2, 1.3), (tuple(end + Vector((0, 0.5, 0.2))), 1.8, 1.7), (tuple(end + Vector((0, 1.5, 0.1))), 1.2, 1.1)], sides=10, per=3)
    for s in (-1, 1):  # the white face, and the eye in it
        egg(m, "Belly", tuple(end + Vector((s * 0.62, 0.75, 0.25))), 0.42, 0.78, 0.62, 10, 5)
        eye(m, end + Vector((s * 0.8, 0.85, 0.3)), 0.26, (s * 0.74, 0.64, 0.05), s, lid="Belly")
    sweep_fine(m, "Gilt", [(tuple(end + Vector((0, 1.4, 0.15))), 0.95, 0.9), (tuple(end + Vector((0, 2.4, 0.0))), 0.62, 0.62), (tuple(end + Vector((0, 3.1, -0.5))), 0.3, 0.34),
                           (tuple(end + Vector((0, 3.2, -1.05))), 0.05, 0.05)], sides=6, per=3)  # hooked
    hinge = end + Vector((0, 1.3, -0.3))
    m.use("Jaw", tuple(hinge), "Head")
    sweep_fine(m, "Gilt", [(tuple(end + Vector((0, 1.4, -0.4))), 0.7, 0.34), (tuple(end + Vector((0, 2.3, -0.52))), 0.44, 0.24), (tuple(end + Vector((0, 2.9, -0.62))), 0.06, 0.06)],
               sides=6, per=2)
    rare_kit.swing(m, ["Jaw"], tuple(hinge), -0.1)
    m.use("Crest", tuple(end + Vector((0, 0, 2.2))), "Head")  # the crest: five gems hung over its head in an arc
    for k in range(5):
        a = (k - 2) * 0.42
        c = end + Vector((math.sin(a) * 1.7, -0.2, 2.0 + math.cos(a) * 1.3))
        shard(m, SPECTRUM[k], tuple(c - Vector((0, 0, 0.5))), tuple(c + Vector((math.sin(a) * 0.4, 0, 0.9))), 0.5, belly=0.45)
    for letter, side in (("L", -1), ("R", 1)):
        bird_leg(m, letter, side, (side * 1.6, -0.6, 6.4), (side * 1.8, -2.1, 3.6), (side * 1.8, -0.4, 0.7), 1.6, thigh="Body", toe=2.2)
    # The train. Each feather on its own bone (Eye1 to 13), all carried by Train: a long mirror blade starting clear of the body, and
    # near its end an eye: a gilt ring, a disc of coloured light, a dark slit. Between them a second, shorter row, on Train itself.
    centre = Vector(TRAIN_AT)
    for k in range(1, EYES + 1):
        way = train_way(k)
        length = 12.5 - 0.5 * abs(k - 7)
        root = centre + way * 3.0
        m.use(f"Eye{k}", tuple(root), "Train")
        face = unit(Vector((0, 0.82, 0.57)))  # the fan faces ahead and up
        blade(m, "Chrome" if k % 2 else "ChromeDark", tuple(root), tuple(root + way * length), 1.5, thick=0.16, up=tuple(face), belly=0.7)
        spot = root + way * length * 0.74
        for layer, (role, r) in enumerate((("Gilt", 1.25), (SPECTRUM[k % 5], 1.0), ("Slit", 0.4))):
            for f in (-1, 1):  # on both faces
                c = spot + face * f * (0.16 + 0.06 * layer)
                poly(m, role, [tuple(c + (Vector((1, 0, 0)) * math.cos(t) + way * math.sin(t) * (1.25 if layer < 2 else 1.6)) * r) for t in
                               [i * math.tau / 10 for i in range(10)]][::f], tuple(face * f * 0.05))
    m.bone = "Train"
    for k in range(12):
        a = (k - 5.5) * 0.2
        way = unit(Vector((1, 0, 0)) * math.sin(a) + unit(TRAIN_UP) * math.cos(a) + Vector((0, -0.12, -0.1)))
        root = centre + way * 2.4
        blade(m, "Accent", tuple(root), tuple(root + way * 6.0), 1.2, thick=0.14, up=(0, 0.82, 0.57), belly=0.6)
    egg(m, "Accent", tuple(centre + Vector((0, 0.4, -0.5))), 1.5, 1.4, 1.2, 10, 5)
    m.bone = "Head"
    m.head_centre = (0, 5.6, 15.4)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Mirror Mirror

GLASS_AT = (0, 0.3, 15.0)  # the middle of the glass
PANES = 8


def glass_way(k):
    """The way pane k (1 to 8) of the glass flies when the mirror bursts: out from the middle and at you."""
    b = (k - 0.5) * math.tau / PANES
    return unit(Vector((math.cos(b), 0.9, math.sin(b))))


def mirror_mirror():
    """The standing mirror, alive: an oval gilt frame taller than a house, crowned in shards, on two bird legs of gold; the glass cracked
    into eight pieces round a hole, and in the hole the face of what lives inside, two cold eyes. Two rings of shards wheel round it."""
    m = monster("dino_MirrorMirror", Body="#141222", Accent="#5c1c44", Belly="#2a2648", Claw="#f2f6ff")
    c = Vector(GLASS_AT)
    rx, rz = 5.6, 8.4
    m.joint("Spine", (0, -1.2, 7.0))
    m.bone = "Spine"
    ring_round(m, "Gilt", tuple(c), rx, (0, 1, 0), 1.25, 36, squash=rz / rx)
    egg(m, "Accent", tuple(c + Vector((0, -0.7, 0))), rx, 0.5, rz, 28, 6)  # the velvet back
    egg(m, "Socket", tuple(c + Vector((0, -0.25, 0))), rx * 0.96, 0.3, rz * 0.97, 28, 4)  # the dark behind the glass
    for k in range(12):  # knobs round the frame
        a = k * math.tau / 12
        p = c + Vector((math.cos(a) * rx, 0.5, math.sin(a) * rz))
        egg(m, "Gilt", tuple(p), 0.7, 0.6, 0.7, 8, 4)
    for k, (dx, h) in enumerate(((0, 5.4), (-1.4, 4.0), (1.4, 4.0), (-2.7, 2.8), (2.7, 2.8), (-3.8, 1.8), (3.8, 1.8))):  # its crown
        base = c + Vector((dx, 0, rz * math.sqrt(max(1 - (dx / rx) ** 2, 0)) + 0.3))
        shard(m, "Chrome" if k % 2 == 0 else "ChromeDark", tuple(base), tuple(base + Vector((dx * 0.35, -0.3, h))), 0.9 + 0.1 * h)
    sweep_fine(m, "Gilt", [((0, -0.2, 7.2), 3.4, 2.2), ((0, -0.4, 6.0), 6.4, 3.0), ((0, -0.4, 5.0), 5.0, 2.6)], sides=12, per=3, up=(0, 1, 0))  # the hips it stands on
    for letter, side in (("L", -1), ("R", 1)):
        bird_leg(m, letter, side, (side * 2.7, -0.4, 5.8), (side * 3.3, -3.0, 3.4), (side * 3.3, 0.0, 0.8), 2.2, toe=3.4)
        for k in range(3):  # a frond of gilt up each side of the frame
            p = c + Vector((side * (rx + 0.5), 0, -4.0 + 3.0 * k))
            horn(m, "Gilt", tuple(p), tuple(p + Vector((side * 2.0, -0.4, 2.2))), 0.9, droop=0.5)
    # What lives in it, on Head: a dark mask no deeper than the mirror is thick, so nothing of it shows behind the frame until it leans out.
    m.use("Head", tuple(c + Vector((0, -0.2, 0.4))), "Spine")
    sweep_fine(m, "Body", [(tuple(c + Vector((0, -0.85, 0.4))), 3.0, 3.8), (tuple(c + Vector((0, -0.5, 0.4))), 3.4, 4.2), (tuple(c + Vector((0, -0.2, 0.5))), 3.0, 4.0),
                           (tuple(c + Vector((0, 0.5, 0.3))), 1.6, 2.6)], sides=12, per=3)
    for s in (-1, 1):
        eye(m, c + Vector((s * 0.85, 0.42, 1.1)), 0.62, (s * 0.12, 1, -0.02), s, lid="Body", ridge="Belly")
        for k in range(3):  # a crown of its own, glass thorns
            base = c + Vector((s * (0.5 + 0.55 * k), -0.3, 2.0 - 0.25 * k))
            shard(m, "ChromeDark", tuple(base), tuple(base + Vector((s * 0.5, -0.4, 1.7 - 0.3 * k))), 0.42)
    sweep(m, "EyeGlow", [(tuple(c + Vector((0, 0.72, 0.1))), 0.16, 0.16), (tuple(c + Vector((0, 0.6, -1.3))), 0.08, 0.08)], sides=4)  # a crack of light for a mouth
    # The glass: eight pieces round the hole, each on its own bone at its middle, gaps between them like cracks.
    for k in range(1, PANES + 1):
        a0, a1 = (k - 1) * math.tau / PANES + 0.035, k * math.tau / PANES - 0.035
        hole = 2.0 + 0.5 * math.sin(k * 2.3)
        def rim(a, share):
            return c + Vector((math.cos(a) * rx * share, 0.12, math.sin(a) * rz * share))
        def near(a):
            return c + Vector((math.cos(a) * hole, 0.12, math.sin(a) * hole * 1.25))
        mid = (a0 + a1) / 2
        pts = [near(a0), rim(a0, 0.93), rim(mid, 0.93), rim(a1, 0.93), near(a1)]
        middle = sum(pts, Vector()) / len(pts)
        m.use(f"Glass{k}", tuple(middle), "Spine")
        poly(m, "Chrome" if k % 2 else "ChromeDark", [tuple(p) for p in pts], (0, 0.26, 0))
    # The rings: upright, facing you, turning opposite ways for ever.
    m.use("LoopA", tuple(c), "Spine")
    ring_of_shards(m, c + Vector((0, 0.9, 0)), 11.0, 10, 3.4, 1.3, axis="roll")
    m.use("LoopB", tuple(c), "Spine")
    ring_of_shards(m, c + Vector((0, -1.3, 0)), 13.2, 14, 2.6, 1.0, axis="roll", roles=("SpecD", "Chrome", "SpecE", "ChromeDark"), start=0.2)
    m.bone = "Head"
    m.head_centre = (0, 1.0, 15.6)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Royal Pane

PANES_A_WING = 5
PANE_WAY = (-0.5, 0.8, 0.3)  # the way the left wing's panes fly in the gust: ahead, out and up (the right's is its mirror)


def pane(m, name, parent, corners, role, shrink=0.8):
    """A pane of stained glass floating in the gap between a wing's ribs: the gap's own shape, smaller, on its own bone at its middle."""
    pts = [Vector(p) for p in corners]
    middle = sum(pts, Vector()) / len(pts)
    inner = [middle + (p - middle) * shrink for p in pts]
    n = (inner[1] - inner[0]).cross(inner[2] - inner[0]).normalized()
    m.use(name, tuple(middle), parent)
    poly(m, role, [tuple(p - n * 0.09) for p in inner], tuple(n * 0.18))
    ring = inner + [inner[0]]
    for a, b in zip(ring, ring[1:]):  # leaded in gilt
        sweep(m, "Gilt", [(tuple(a), 0.4, 0.4), (tuple(b), 0.4, 0.4)], sides=6)


def royal_pane():
    """A wyvern of white porcelain and gold on two great legs: a long neck crested in mirror, a narrow head helmed in chrome with a
    hooked beak, four gilt horns, two glass tusks, a ring of shards turning over it; a whip of a tail; and wings that are windows."""
    m = monster("dino_RoyalPane", Body="#f4efe8", Accent="#6b1f47", Belly="#e6d6a6", Claw="#f2f6ff")
    m.joint("Spine", (0, -3.0, 9.2))
    m.joint("Royal", (0, 2.0, 10.2), "Spine")
    rings = [((0, -7.6, 8.7), 2.6, 2.6), ((0, -5.0, 9.1), 5.4, 5.4), ((0, -1.5, 9.5), 6.4, 6.6), ((0, 2.0, 10.3), 6.0, 6.4), ((0, 4.6, 11.4), 3.8, 4.0)]
    bones = ["Spine", "Spine", "Spine", "Royal", "Royal"]
    sweep_fine(m, "Body", rings, bones, sides=18, under="Belly", under_faces=5, per=4)
    stripes(m, rings, (1.3, 2.0, 2.7), "Gilt", bones, grow=1.05, length=0.3)
    first.crest(m, rings, bones, [(0.7, 1.3), (1.3, 1.9), (1.9, 2.4), (2.5, 2.8), (3.1, 2.6), (3.7, 2.0)], w=0.5)
    tail = curve([(0, -7.4, 8.7), (0, -11.5, 8.0), (0, -16.0, 6.6), (0, -20.5, 6.2), (0, -24.0, 7.4)], 12)
    widths = (2.6, 2.3, 2.0, 1.75, 1.5, 1.3, 1.1, 0.9, 0.75, 0.6, 0.45, 0.3)
    tail_bones = jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(tail, widths)], sides=10, under="Belly")
    for i in range(1, 11, 2):  # mirror down the tail, and a gilt spade on its end
        p = Vector(tail[i])
        m.bone = tail_bones[i]
        shard(m, "Chrome", tuple(p + Vector((0, 0, widths[i] * 0.3))), tuple(p + Vector((0, -1.0, widths[i] * 0.5 + 1.5 - 0.08 * i))), 0.42)
    m.bone = "Tail3"
    end_ = Vector(tail[-1])
    blade(m, "Gilt", tuple(end_ - Vector((0, -0.3, 0))), tuple(end_ + Vector((0, -3.4, 1.6))), 2.4, thick=0.3, up=(0, 0, 1), belly=0.45)
    for letter, side in (("L", -1), ("R", 1)):
        raptor_leg(m, letter, side, (side * 2.6, -2.6, 9.0), (side * 3.3, 0.6, 5.6), (side * 3.1, -3.2, 2.9), (side * 3.1, -1.2, 0.8), 2.5, toe=3.2)
    # The neck, crested, and the head.
    neck = curve([(0, 4.4, 11.4), (0, 6.9, 13.4), (0, 6.6, 16.0), (0, 7.4, 17.8), (0, 8.6, 18.6)], 13)
    neck_w = [3.5 - 0.13 * i for i in range(13)]
    neck_bones = jointed(m, "Body", ["Neck", "NeckB", "NeckC"], [(p, w, w) for p, w in zip(neck, neck_w)], parent="Royal", sides=12, under="Belly")
    for i in range(2, 12, 2):
        p, ahead = Vector(neck[i]), unit(Vector(neck[i + 1]) - Vector(neck[i - 1]))
        back = unit(Vector((0, -ahead.z, ahead.y)))
        m.bone = neck_bones[i]
        shard(m, "Chrome", tuple(p + back * neck_w[i] * 0.3), tuple(p + back * (neck_w[i] * 0.5 + 1.9) - ahead * 0.8), 0.46)
    e = Vector(neck[-1])
    m.use("Head", tuple(e), "NeckC")
    head = mark(m)
    sweep_fine(m, "Body", [(tuple(e + Vector((0, -0.9, 0))), 2.0, 2.0), (tuple(e + Vector((0, 0.8, 0.2))), 2.6, 2.3), (tuple(e + Vector((0, 2.8, 0.0))), 2.0, 1.5),
                           (tuple(e + Vector((0, 4.7, -0.3))), 1.35, 0.95)], sides=12, per=3)
    sweep_fine(m, "Chrome", [(tuple(e + Vector((0, 4.3, -0.26))), 1.5, 1.05), (tuple(e + Vector((0, 5.6, -0.5))), 0.95, 0.75), (tuple(e + Vector((0, 6.3, -0.95))), 0.4, 0.4),
                             (tuple(e + Vector((0, 6.35, -1.5))), 0.05, 0.05)], sides=8, per=3)  # the hooked beak
    sweep(m, "Chrome", [(tuple(e + Vector((0, -0.6, 1.18))), 1.5, 0.3), (tuple(e + Vector((0, 0.9, 1.42))), 2.6, 0.3), (tuple(e + Vector((0, 2.8, 0.92))), 1.7, 0.3),
                        (tuple(e + Vector((0, 4.4, 0.36))), 0.7, 0.3)], sides=4)  # the helm
    egg(m, "Mouth", tuple(e + Vector((0, 2.3, -0.55))), 0.85, 2.0, 0.3, 10, 4)
    for s in (-1, 1):
        eye(m, e + Vector((s * 1.12, 1.5, 0.5)), 0.36, (s * 0.62, 0.76, 0.08), s)
        horn(m, "Gilt", tuple(e + Vector((s * 0.9, -0.3, 0.9))), tuple(e + Vector((s * 2.4, -5.6, 3.4))), 0.95, droop=-0.9, count=9)
        horn(m, "Gilt", tuple(e + Vector((s * 1.2, -0.2, 0.2))), tuple(e + Vector((s * 2.8, -3.2, 0.4))), 0.7, droop=0.3)
        shard(m, "ChromeDark", tuple(e + Vector((s * 1.1, 0.5, -0.2))), tuple(e + Vector((s * 2.0, -1.6, -1.0))), 0.4)
    hinge = e + Vector((0, 0.5, -0.6))
    m.use("Jaw", tuple(hinge), "Head")
    sweep_fine(m, "Body", [(tuple(e + Vector((0, 0.3, -0.95))), 1.9, 0.8), (tuple(e + Vector((0, 2.6, -1.05))), 1.5, 0.6), (tuple(e + Vector((0, 4.9, -1.0))), 0.8, 0.4)],
               sides=10, per=3)
    for s in (-1, 1):  # two tusks of glass, and nothing else in its mouth
        base = e + Vector((s * 0.5, 3.9, -0.9))
        sabre(m, "Teeth", [tuple(base), tuple(base + Vector((s * 0.12, 0.2, 0.9))), tuple(base + Vector((s * 0.05, -0.1, 1.9)))], 0.4, 7)
    rare_kit.swing(m, ["Jaw"], tuple(hinge), -0.2)
    for n, s in ((1, -1), (2, 1)):  # barbels off its chin, swaying
        root = e + Vector((s * 0.5, 2.6, -1.4))
        chain(m, "Sway", n, curve([root, root + Vector((s * 0.5, -0.6, -1.4)), root + Vector((s * 0.7, -1.6, -2.6)), root + Vector((s * 0.5, -2.2, -3.8))], 7), 0.24, 0.06,
              parent="Jaw", role="Gilt")
    m.use("Tiara", tuple(e + Vector((0, -0.6, 4.2))), "Head")  # a ring of shards turning over its head
    ring_of_shards(m, e + Vector((0, -0.6, 4.2)), 1.9, 8, 1.5, 0.6, roles=("Chrome", "SpecB"))
    grown(m, head, e, 1.15)
    # The wings: an arm (WingL/R), then three gilt fingers from the wrist (WingTipL/R), and in each gap a pane of glass.
    for letter, side in (("L", -1), ("R", 1)):
        def v(x, y, z):
            return Vector((side * x, y, z))
        s_, elbow, wrist = v(3.0, 1.6, 12.4), v(7.5, 0.0, 18.5), v(9.5, 3.0, 22.5)
        f1, f2, f3, body = v(15.0, 5.5, 28.0), v(17.5, -2.5, 21.5), v(13.0, -8.5, 14.0), v(2.8, -5.2, 11.0)
        m.use(f"Wing{letter}", tuple(s_), "Royal")
        knob(m, "Body", s_, 1.3)
        limb(m, "Body", [s_, s_.lerp(elbow, 0.5) + Vector((0, 0, 0.4)), elbow], (2.0, 1.6, 1.2), sides=10)
        pane(m, f"Pane{letter}1", f"Wing{letter}", [s_.lerp(elbow, 0.12), elbow, f3, body], "SpecE")
        m.use(f"WingTip{letter}", tuple(elbow), f"Wing{letter}")
        knob(m, "Chrome", elbow, 0.8)
        limb(m, "Body", [elbow, wrist], (1.2, 0.9), sides=8)
        sabre(m, "Chrome", [tuple(wrist), tuple(wrist + Vector((0, 1.4, 0.8))), tuple(wrist + Vector((side * 0.4, 2.6, 0.2)))], 0.6, 6)
        for tip in (f1, f2, f3):
            sweep(m, "Gilt", [(tuple(wrist), 0.7, 0.7), (tuple(wrist.lerp(tip, 0.5)), 0.5, 0.5), (tuple(tip), 0.1, 0.1)], sides=6)
        sweep(m, "Gilt", [(tuple(elbow), 0.6, 0.6), (tuple(f3), 0.1, 0.1)], sides=6)
        low = wrist.lerp(elbow, 0.5)
        pane(m, f"Pane{letter}2", f"WingTip{letter}", [wrist, wrist.lerp(f1, 0.5), wrist.lerp(f2, 0.5)], "SpecA", shrink=0.76)
        pane(m, f"Pane{letter}3", f"WingTip{letter}", [wrist.lerp(f1, 0.5), f1, f2, wrist.lerp(f2, 0.5)], "SpecB")
        pane(m, f"Pane{letter}4", f"WingTip{letter}", [low, low.lerp(f2, 0.5), low.lerp(f3, 0.5)], "SpecC", shrink=0.76)
        pane(m, f"Pane{letter}5", f"WingTip{letter}", [low.lerp(f2, 0.5), f2, f3, low.lerp(f3, 0.5)], "SpecD")
    m.bone = "Head"
    m.head_centre = (0, 11.5, 18.8)
    grounded(m)
    return m


ALL = [stilt_life, prism_break, mother_of_pearl, vainglory, mirror_mirror, royal_pane]


# ---------------------------------------------------------------------- what moves
#
# As the first six: a marker bone picks the table, the attack is 4 seconds, "@always" runs all the time. The same as the second half of
# the map-16 block in DinoLifeController, number for number.


def bob(way, reach, speed, phase=0.0):
    """Floats back and forth along a way, for ever."""
    return along(way, lambda s: reach * math.sin(speed * W * s - phase))


def thrust(way, reach, points):
    """Slides out along a way and back, by keys over the 4 seconds."""
    return along(way, lambda s: reach * keys((s / 4) % 1, points))


def both_sides(table, left):
    """A left-hand table into `table`, with its mirror for the right."""
    for name, move in left.items():
        table[name], table[right_of(name)] = move, mirrored(move)


UPWARD = (0, 0, 1)

# Stilt Life (Stilt, its chest): the neck coils back, the bill opens, and it stabs three times, driving forward each time, its blades
# flung wide and shaking. Always: the blades hang beside it and a wave runs up each fan.
STAB_COIL = [(0, 0), (0.14, 1), (0.3, 1), (0.335, -1), (0.4, 0.5), (0.435, -1), (0.5, 0.5), (0.535, -1), (0.66, -1), (0.86, 0), (1, 0)]
STAB_LUNGE = [(0, 0), (0.3, -0.3), (0.335, 1), (0.4, 0.3), (0.435, 1), (0.5, 0.3), (0.535, 1), (0.66, 1), (0.86, 0), (1, 0)]
STAB_BILL = [(0, 0), (0.14, -0.35), (0.3, -0.35), (0.34, 0.05), (0.4, -0.3), (0.44, 0.05), (0.5, -0.3), (0.54, 0.05), (0.66, 0.05), (0.75, -0.4), (0.86, 0), (1, 0)]
STAB_FLARE = [(0, 0), (0.14, 1), (0.7, 1), (0.9, 0), (1, 0)]
STABBER = {
    "Spine": stacked(beat(STAB_LUNGE, 4, AHEAD, 2.4), beat(STAB_LUNGE, 4, PITCH, -0.08)),
    "Neck": beat(STAB_COIL, 4, PITCH, 0.3),
    "NeckB": beat(STAB_COIL, 4, PITCH, 0.35),
    "NeckC": beat(STAB_COIL, 4, PITCH, -0.45),
    "Head": beat(STAB_COIL, 4, PITCH, -0.2),
    "Jaw": beat(STAB_BILL, 4),
    "LegL": beat(STAB_LUNGE, 4, PITCH, 0.2),
    "LegR": beat(STAB_LUNGE, 4, PITCH, -0.2),
    ALWAYS: {},
}
for k in range(1, VANES + 1):
    both_sides(STABBER, {f"VaneL{k}": stacked(beat(STAB_FLARE, 4, YAW, -0.6), beat(STAB_FLARE, 4, PITCH, -0.25), shaken(STAB_FLARE, 16, 0.05, ROLL, 0.5 * k))})
    both_sides(STABBER[ALWAYS], {f"VaneL{k}": stacked(bob(UPWARD, 0.45, 2, 0.7 * k), wave(2, 0.1, PITCH, 0.7 * k))})

# Prism Break (Prism, its chest): it drops its head and its whole sail tips forward over it; blade after blade fires ahead and comes
# back, front one first; then it charges, jaw wide. Always: the sail floats in a wave, the tail's shards drift.
RAY_LOW = [(0, 0), (0.15, 1), (0.72, 1), (0.9, 0), (1, 0)]
RAY_CHARGE = [(0, 0), (0.5, 0), (0.6, 1), (0.72, 1), (0.92, 0), (1, 0)]
RAY_RUN = [(0, 0), (0.48, 0), (0.52, 1), (0.72, 1), (0.78, 0), (1, 0)]
RAY_JAW = [(0, 0), (0.15, -0.2), (0.5, -0.2), (0.58, -0.7), (0.72, -0.7), (0.78, 0.1), (0.9, 0), (1, 0)]
RAY_WAY = (0, 1, 0.15)
RAYER = {
    "Spine": stacked(beat(RAY_LOW, 4, PITCH, -0.2), beat(RAY_LOW, 4, RISE, -0.6), beat(RAY_CHARGE, 4, AHEAD, 5.5)),
    "Neck": beat(RAY_LOW, 4, PITCH, -0.35),
    "Head": beat(RAY_LOW, 4, PITCH, 0.25),
    "Jaw": beat(RAY_JAW, 4),
    "LegL": stacked(beat(RAY_LOW, 4, PITCH, 0.2), shaken(RAY_RUN, 12, 0.6)),
    "LegR": stacked(beat(RAY_LOW, 4, PITCH, 0.2), shaken(RAY_RUN, 12, 0.6, PITCH, math.pi)),
    "ArmL": beat(RAY_CHARGE, 4, PITCH, 0.8),
    "ArmR": beat(RAY_CHARGE, 4, PITCH, 0.8),
    ALWAYS: {},
}
for i in range(1, 4):
    RAYER[f"Tail{i}"] = shaken(RAY_LOW, 6, 0.12 + 0.05 * i, YAW, 0.8 * i)
    RAYER[ALWAYS][f"Drift{i}"] = stacked(bob(UPWARD, 0.5, 2, 0.9 * i), wave(2, 0.25, ROLL, 0.9 * i))
for k in range(1, SAILS + 1):
    RAYER[f"Sail{k}"] = stacked(beat(RAY_LOW, 4, PITCH, -1.0), thrust(RAY_WAY, 4.0, volley(k - 1, 0.2, 0.04, 0.05, 0.3, 0.1)))
    RAYER[ALWAYS][f"Sail{k}"] = stacked(bob(UPWARD, 0.7, 2, 0.8 * k), wave(2, 0.12, ROLL, 0.8 * k))

# Moth-er of Pearl (Flutter, its thorax): it climbs, draws its wings back, claps them shut in front of it twice, and dives through you;
# its rings spin up. Always: all four wings beat, its tail curls, the two rings turn opposite ways.
MOTH_RISE = [(0, 0), (0.2, 1), (0.4, 1), (0.5, -0.3), (0.62, -0.3), (0.85, 0), (1, 0)]
MOTH_DIVE = [(0, 0), (0.4, -0.15), (0.5, 1), (0.62, 1), (0.86, 0), (1, 0)]
MOTH_CLAP = [(0, 0), (0.2, 0.35), (0.4, 0.35), (0.47, -1), (0.52, -1), (0.57, 0.3), (0.62, -1), (0.68, -1), (0.86, 0), (1, 0)]
MOTH_SPIN = [(0, 0), (0.2, 0), (0.8, 4 * math.pi), (1, 4 * math.pi)]
MOTH_BUSY = [(0, 0), (0.18, 0), (0.24, 1), (0.8, 1), (0.86, 0), (1, 0)]
FLUTTERER = {
    "Swim": stacked(beat(MOTH_RISE, 4, RISE, 2.6), beat(MOTH_DIVE, 4, AHEAD, 6.5), beat(MOTH_RISE, 4, PITCH, 0.25)),
    "Flutter": shaken(MOTH_BUSY, 16, 0.04, ROLL),
    "Head": beat(MOTH_RISE, 4, PITCH, -0.2),
    "LoopA": beat(MOTH_SPIN, 4, YAW),
    "LoopB": stacked(beat(MOTH_SPIN, 4, YAW, -1.0), shaken(MOTH_BUSY, 4, 0.12)),
    ALWAYS: {"LoopA": spun(1, YAW), "LoopB": spun(-1, YAW), "AbdA": wave(2, 0.1), "AbdB": wave(2, 0.14, PITCH, 0.8)},
}
both_sides(FLUTTERER, {"WingL": beat(MOTH_CLAP, 4, YAW, 1.1), "HindL": beat(MOTH_CLAP, 4, YAW, 0.7, 0.02)})
both_sides(FLUTTERER[ALWAYS], {"WingL": wave(8, 0.28, ROLL), "HindL": wave(8, 0.24, ROLL, 0.9)})

# Vainglory (Train, the root of its train): the fan goes up and shivers, it struts at you with its neck pumping, screams, and the eyes
# stab outward, the middle one first, and come back. Always: a wave runs across the train, the crest bobs.
VAIN_UP = [(0, 0), (0.16, 1), (0.8, 1), (0.94, 0), (1, 0)]
VAIN_SHIVER = [(0, 0), (0.18, 0), (0.22, 1), (0.5, 1), (0.56, 0), (1, 0)]
VAIN_STRUT = [(0, 0), (0.22, 0), (0.5, 1), (0.74, 1), (0.94, 0), (1, 0)]
VAIN_STEPS = [(0, 0), (0.2, 0), (0.24, 1), (0.5, 1), (0.54, 0), (1, 0)]
VAIN_SCREAM = [(0, 0), (0.5, 0), (0.54, -0.6), (0.72, -0.6), (0.78, 0), (1, 0)]
VAIN_HEAD = [(0, 0), (0.5, 0), (0.54, 0.3), (0.72, 0.3), (0.8, 0), (1, 0)]
VAUNTER = {
    "Spine": stacked(beat(VAIN_STRUT, 4, AHEAD, 3.2), shaken(VAIN_STEPS, 8, 0.2, RISE)),
    "Train": stacked(beat(VAIN_UP, 4, PITCH, -0.5), shaken(VAIN_SHIVER, 24, 0.04, ROLL)),
    "Neck": stacked(beat(VAIN_UP, 4, PITCH, 0.15), shaken(VAIN_STEPS, 8, 0.12)),
    "NeckB": shaken(VAIN_STEPS, 8, -0.1),
    "Head": beat(VAIN_HEAD, 4),
    "Jaw": beat(VAIN_SCREAM, 4),
    "LegL": shaken(VAIN_STEPS, 8, 0.5),
    "LegR": shaken(VAIN_STEPS, 8, 0.5, PITCH, math.pi),
    "Crest": shaken(VAIN_SHIVER, 24, 0.08, ROLL),
    ALWAYS: {"Crest": bob(UPWARD, 0.25, 2), "Train": wave(1, 0.04, ROLL)},
}
for k in range(1, EYES + 1):
    VAUNTER[f"Eye{k}"] = thrust(tuple(train_way(k)), 2.6, volley(abs(k - 7), 0.5, 0.02, 0.04, 0.62, 0.12))
    VAUNTER[ALWAYS][f"Eye{k}"] = bob(tuple(train_way(k)), 0.5, 2, 0.5 * k)

# Mirror Mirror (Glass1, the first piece of its glass): the glass bursts out of the frame, each
# piece spinning in its own plane; what lives inside leans out through the hole and looks left and right for you; then it draws back and
# the glass closes over it. Always: the two rings wheel opposite ways, and the glass breathes.
GLASS_TUMBLE = [(0, 0), (0.14, 0), (0.3, 2 * math.pi), (0.66, 2 * math.pi), (0.8, 4 * math.pi), (1, 4 * math.pi)]
GLASS_EMERGE = [(0, 0), (0.24, 0), (0.36, 1), (0.62, 1), (0.72, 0), (1, 0)]
GLASS_LOOK = [(0, 0), (0.36, 0), (0.4, 1), (0.6, 1), (0.64, 0), (1, 0)]
GLASS_SPIN = [(0, 0), (0.14, 0), (0.8, 2 * math.pi), (1, 2 * math.pi)]
SHATTERER = {
    "Spine": stacked(beat(GLASS_EMERGE, 4, PITCH, -0.1), shaken(GLASS_LOOK, 8, 0.25, RISE)),
    "Head": stacked(beat(GLASS_EMERGE, 4, AHEAD, 2.6), shaken(GLASS_LOOK, 4, 0.4, YAW)),
    "LegL": shaken(GLASS_LOOK, 8, 0.3),
    "LegR": shaken(GLASS_LOOK, 8, 0.3, PITCH, math.pi),
    "LoopA": beat(GLASS_SPIN, 4, ROLL),
    "LoopB": beat(GLASS_SPIN, 4, ROLL, -1.0),
    ALWAYS: {"LoopA": spun(1), "LoopB": spun(-1)},
}
for k in range(1, PANES + 1):
    SHATTERER[f"Glass{k}"] = stacked(thrust(tuple(glass_way(k)), 3.6, volley(k - 1, 0.14, 0.012, 0.06, 0.66, 0.1)), beat(GLASS_TUMBLE, 4, ROLL, 1.0 if k % 2 else -1.0))
    SHATTERER[ALWAYS][f"Glass{k}"] = bob((0, 1, 0), 0.12, 2, 0.8 * k)

# Royal Pane (Royal, its chest): it rears, spreads its wings high, coils its neck, then beats the wings forward: the panes fly out of
# them at you, one after another, and back, as it strikes down roaring. Always: the panes ripple in their frames, the ring over its head
# turns, the neck sways.
ROYAL_REAR = [(0, 0), (0.18, 1), (0.6, 1), (0.72, -0.2), (0.82, -0.2), (1, 0)]
ROYAL_SPREAD = [(0, 0), (0.18, 1), (0.46, 1), (0.54, -0.3), (0.7, -0.3), (0.9, 0), (1, 0)]
ROYAL_GUST = [(0, 0), (0.46, 0), (0.54, 1), (0.7, 1), (0.9, 0), (1, 0)]
ROYAL_COIL = [(0, 0), (0.18, 1), (0.46, 1), (0.54, -1), (0.72, -1), (0.9, 0), (1, 0)]
ROYAL_JAW = [(0, 0), (0.18, -0.2), (0.46, -0.25), (0.54, -0.75), (0.74, -0.75), (0.86, 0), (1, 0)]
ROYAL_ROAR = [(0, 0), (0.52, 0), (0.56, 1), (0.74, 1), (0.8, 0), (1, 0)]
REGENT = {
    "Spine": stacked(beat(ROYAL_REAR, 4, PITCH, 0.4), beat(ROYAL_REAR, 4, RISE, 1.4)),
    "LegL": beat(ROYAL_REAR, 4, PITCH, -0.4),
    "LegR": beat(ROYAL_REAR, 4, PITCH, -0.4),
    "Neck": beat(ROYAL_COIL, 4, PITCH, 0.25),
    "NeckB": beat(ROYAL_COIL, 4, PITCH, 0.2),
    "NeckC": beat(ROYAL_COIL, 4, PITCH, -0.3),
    "Head": stacked(beat(ROYAL_COIL, 4, PITCH, -0.15), shaken(ROYAL_ROAR, 20, 0.04, YAW)),
    "Jaw": stacked(beat(ROYAL_JAW, 4), shaken(ROYAL_ROAR, 24, 0.05)),
    "Tail1": beat(ROYAL_REAR, 4, PITCH, -0.35),
    "Tail2": shaken(ROYAL_SPREAD, 4, 0.25, YAW),
    "Tail3": shaken(ROYAL_SPREAD, 4, 0.35, YAW, 1.0),
    ALWAYS: {"Tiara": spun(1, YAW), "NeckB": wave(1, 0.05, YAW)},
}
both_sides(REGENT, {"WingL": stacked(beat(ROYAL_SPREAD, 4, ROLL, 0.45), beat(ROYAL_GUST, 4, YAW, -0.4)),
                    "WingTipL": stacked(beat(ROYAL_SPREAD, 4, ROLL, 0.3), beat(ROYAL_GUST, 4, YAW, -0.25))})
for k in range(1, PANES_A_WING + 1):
    both_sides(REGENT, {f"PaneL{k}": thrust(PANE_WAY, 4.2, volley(k - 1, 0.5, 0.025, 0.05, 0.64, 0.12))})
    both_sides(REGENT[ALWAYS], {f"PaneL{k}": stacked(bob(UPWARD, 0.3, 2, 0.9 * k), wave(2, 0.06, ROLL, 0.9 * k))})

# A monster with one of these bones has the rest of its body moved by that bone's table: the same lines as in DinoLifeController.
RARE_MOVES = {"Stilt": STABBER, "Prism": RAYER, "Flutter": FLUTTERER, "Train": VAUNTER, "Glass1": SHATTERER, "Royal": REGENT}
rare_kit.MARKED.update(RARE_MOVES)


# ---------------------------------------------------------------------- the preview's animation


def walk_pose(a, f):
    (swim_pose if "Swim" in a.pose.bones else volcano_walk)(a, f)
    sway(a, f, False)
    first.always(a, f, False)


def idle_pose(a, f):
    (hover_pose if "Swim" in a.pose.bones else volcano_idle)(a, f)
    moved = set(marked_of(a))
    for name in first.LEGS:
        if name not in moved:
            kit.pose_bone(a, name, (0, 0, 0), None, f)
    sway(a, f, True)
    first.always(a, f, True)


def animate(armature):
    return kit.add_action(armature, "Walk", WALK_PREVIEW, walk_pose, 2), kit.add_action(armature, "Idle", kit.IDLE_FRAMES, idle_pose, 2)


def main():
    monster_stage.light_up = first.light_and_shine
    rare_kit.light_up = first.light_and_shine
    only = os.environ.get("ONLY")
    if os.environ.get("POSE"):
        first.idle_pose, first.ALL = idle_pose, ALL
        first.pose_stills([b for b in ALL if not only or b.__name__ in only.split(",")], Path(os.environ["QUICK_OUT"]), [float(s) for s in os.environ["POSE"].split()])
        return
    rare_kit.animate = animate
    rare_kit.run(ALL, RENDERS, BLEND, "shattered_mirror_rare", SKY, FLOOR, GLOW_ROLES, glow=1.6, spacing=60)


if __name__ == "__main__":
    main()
