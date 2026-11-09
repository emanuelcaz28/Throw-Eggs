"""Builds The Weeping Dark's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_weeping_dark_monsters.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_weeping_dark_monsters.py    (stills only, for trying faces)
    ONLY=teddy_wrecks,good_boy QUICK=1 ...                                     (just those)

Saves weeping_dark_monsters.blend and renders to design/world/monsters_weeping_dark/. The map's props are in
build_weeping_dark.py.

Map 15, the end of the corridor. The owner asked for monsters that suit the map, "very aggressive, the most aggressive
out of all the animals we did", built in Blender and animated nicely. Everybody here walked into the dark to look for
the sun. These are what came back: grief gone bad, every one of them something from the map turned to rage. So there
are no silly ones at all. The jokes are only in the names, and the names are sad as well as funny.

They keep the map's rule: no colour. Black, ash and bone, and red only ever for eyes, so a lot of pale in them, which
also keeps them readable in the map's very dark light. They share two ideas. The weeping glare: burning eyes in black
sockets under brows slanting hard to the nose, with tears running from them, because they haven't stopped crying.
And the throat eye: in every mouth, right at the back, another red eye looks out at you.

  Teddy Wrecks    the Lost Bear: a worn teddy whose whole face has torn open into a mouth of nails, a button hanging by a
                  thread where its eye was, stuffing bursting from its belly, loose threads whipping about
  Good Boy        the dog that waited too long: a gaunt hound, its ribs showing, hackles up, snarling, its collar still on
                  and the chain it snapped lashing behind it
  Casket Case     a coffin for a head: a huge snapping box, lid and all, full of nails, on four long pale arms that gallop on
                  their hands, its shroud streaming behind it, two more arms reaching ahead of it to grab you
  Wailing Widow   a tall black veiled thing, a bone mask, a jaw hanging open to its chest in one long scream, its veil torn
                  into strips that lash about its head, and pale arms as long as it is tall, claws spread
  Death Knell     a hulking brute on its knuckles with a great black bell for a head. The bell is the mouth, its rim a ring
                  of teeth, and the clapper is a tongue on a chain with a red eye on the end of it
  Endless Grief   the boss, and what's behind the Last Door: the same pale eye with the same red iris and slit, in a colossal
                  hooded head, its huge pale hands clawing at its own face. Shackles from the door still on its wrists, and
                  out of its back reach the arms of everyone it ever took, thrashing

What moves. The usual walk, idle and roar, the thrashing from map 13 (thrash_of in build_thorn_kingdom_monsters.py and
THRASH in DinoLifeController: Lash and Snap bones, head jerks, gnashing) and, new here, in DinoLifeController (RAGE, DRIP)
and in this file (rage_of, DRIP), the same numbers in both:
  - Rage. A monster with a Drip or DripB bone doesn't just thrash, it attacks. Every 4 seconds it loads up and lunges: its body
    heaves back, slams forward, its head drives in, its jaw drops and bites shut, and its tail cracks. Its arms claw one
    after the other, 2 seconds apart, and it snaps at the air between lunges. All the time it pants and shakes.
  - Charge. It walks a third faster than anything else (a stride takes 2/3 of a second, DinoLife rageStrideSeconds).
  - Drip and DripB bones fall for ever, the same as the props' `fall`: tears `gap` apart, so each only goes as far as
    where the next began, and they loop seamlessly. Their tears run from the eyes whatever the head is doing.
  - Palm bones: Endless Grief's hands pull away from its face in the roar and the lunge.
Everything moves at whole multiples of a quarter turn a second, so the pattern repeats every 4 seconds and the preview's
walk (6 strides) and 8-second idle both loop seamlessly.

Rules the game adds: Jaw sits in front of Tail1 (or the Spine), since that's how the game tells which way a monster
faces. Only the main eyes use the Pupil role, which the reveal aims at; spare eyes use Slit.

Glowing parts are EyeGlow, Tears and Stream (Neon in the game, shared/Roles.luau, all there already). Skin roles Body,
Accent, Belly and Claw take the colour mutations; the face, the iron and the cloth keep their colour. Built at the first
map's size; the game scales them by Config/Biomes standardScale. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0.

No gore and nothing showing how anyone died: it's a kids' game. Nothing here bleeds, and the stuffing and bones are
all the insides you see. No crosses or stars anywhere (memory: ruled out on map 10), so the coffin has iron straps
and nothing else on its lid.

No stud texture in this file (kit.PREVIEW_STUDS off): plain colours, and the studs come only from Studio's shared
"Studs" material.
"""
import math
import os
import random
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_clockwork_citadel import Frame, obox, tube, turn  # noqa: E402
from build_desert import beam  # noqa: E402
from build_eclipse_temple_monsters import grow  # noqa: E402
from build_forest import Model, biped_legs  # noqa: E402
from build_starfall_crater import ball, gem  # noqa: E402
from build_thorn_kingdom_monsters import (W, along, blade, bristle, clawed_leg, crooked_teeth, fcurves_of, glare, half_ball, idle_pose as thorn_idle,  # noqa: E402
                                          lash, point, ridge, slab, thorn, walk_pose as thorn_walk, wander, wild_eye, yloft)
from build_volcano import prism, top_of  # noqa: E402
from build_weeping_dark import BONE_DARK, CORRIDOR, IRON, IRON_DARK, STREAM, TEAR, flat_outline, hand, outline  # noqa: E402
from map_kit import limb, plate  # noqa: E402
from monster_stage import build_and_render, light_up, set_sky  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_weeping_dark"
BLEND = "weeping_dark_monsters"  # for check_map.py and export_fbx.py

GLOW_ROLES = {"EyeGlow", "Tears", "Stream"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket", "Slit", "Sinew"})
GLOW = 1.5

RED = "#ff1a1a"
FACE = {"Pupil": "#0a0506", "Slit": "#0a0506", "Socket": "#08070a", "EyeGlow": RED, "EyeWhite": "#d9d6cc", "Highlight": "#ffffff", "Mouth": "#0a090c",
        "Teeth": "#ece8dc", "Tongue": "#4c4749", "Sinew": "#8c8a86", "Stream": STREAM, "Tears": TEAR, "Chain": "#6c6c72", "Iron": IRON, "IronDark": IRON_DARK,
        "Briar": "#232327"}
SKY, FLOOR = "#16171d", CORRIDOR["FloorA"]

WALK_PREVIEW = 120  # four seconds: six strides, and the rage repeats every 4 seconds
CHARGE_FRAMES = 20  # a stride at 30 frames a second: 2/3 of a second, DinoLife rageStrideSeconds

# Bones whose tears fall for ever: how far apart the tears are and how long one takes to reach the next, as in the game.
DRIP = {"Drip": (0.6, 0.8), "DripB": (1.6, 1.0)}


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- how they rage


def smooth(t):
    return t * t * (3 - 2 * t)


def strike(x):
    """0 most of the time. Once every full turn of x: a slam up to 1, held a moment, then a slower recovery."""
    u = (x / math.tau) % 1
    if u < 0.05:
        return smooth(u / 0.05)
    if u < 0.12:
        return 1.0
    if u < 0.34:
        return 1 - smooth((u - 0.12) / 0.22)
    return 0.0


def windup(x):
    """The moment before strike: rising to 1 over the end of the turn, gone as strike lands."""
    u = (x / math.tau) % 1
    if u > 0.9:
        return smooth((u - 0.9) / 0.1)
    if u < 0.05:
        return 1 - smooth(u / 0.05)
    return 0.0


def rage_of(name, s):
    """What a bone adds to the walk, the idle and the thrashing, s seconds in: pitch, roll, yaw, rise and surge. The same
    as RAGE in DinoLifeController."""
    sin = math.sin
    w = W * s
    hit, load = strike(w), windup(w)  # the great lunge, every 4 seconds
    nip, nip_load = strike(2 * w + math.pi), windup(2 * w + math.pi)  # a snap at the air between lunges
    if name == "Spine":
        return -0.1 * hit + 0.09 * load + 0.014 * sin(8 * w), 0, 0, 0.05 * sin(8 * w) - 0.1 * hit, 0.55 * hit - 0.3 * load
    if name == "Neck":
        return -0.2 * hit + 0.14 * load - 0.08 * nip, 0, 0, 0, 0
    if name == "Head":
        return 0.16 * hit - 0.1 * load + 0.1 * nip, 0.03 * sin(20 * w) * (0.3 + hit), 0.1 * sin(14 * w) * hit, 0, 0
    if name == "Jaw":
        return -0.5 * load + 0.2 * hit - 0.3 * nip_load + 0.12 * nip, 0, 0, 0, 0
    if name in ("ArmL", "ArmR"):
        x = w if name == "ArmL" else w + math.pi  # one claw, then the other
        return 1.2 * windup(x) - 0.6 * strike(x), 0, 0, 0, 0
    if name in ("FrontL", "FrontR"):
        return 0.42 * hit - 0.24 * load, 0, 0, 0, 0
    if name in ("BackL", "BackR"):
        return -0.2 * hit + 0.1 * load, 0, 0, 0, 0
    if name in ("LegL", "LegR"):
        side = 1 if name == "LegL" else -1
        return side * (0.3 * hit - 0.1 * load), 0, 0, 0, 0
    if name in ("ShinL", "ShinR"):
        return (-0.2 if name == "ShinL" else -0.5) * hit, 0, 0, 0, 0
    if name in ("Tail1", "Tail2", "Tail3"):
        i = int(name[4])
        return 0.1 * strike(w - 0.3 * i), 0, 0.42 * strike(w - 0.3 * i), 0, 0
    if name in ("PalmL", "PalmR"):
        side = 1 if name == "PalmL" else -1
        return 0, 0, side * (0.5 * hit + 0.24 * load), 0, 0
    return None


def rage(a, f):
    """Adds the rage and the falling tears to the pose just set."""
    s = f / 30
    for bone in a.pose.bones:
        extra = rage_of(bone.name, s)
        if extra:
            rotation = tuple(bone.rotation_euler[i] + extra[i] for i in range(3))
            kit.pose_bone(a, bone.name, rotation, (bone.location[0], bone.location[1] + extra[4], bone.location[2] + extra[3]), f)
        if bone.name in DRIP:
            gap, period = DRIP[bone.name]
            kit.pose_bone(a, bone.name, (0, 0, 0), (0, 0, -gap * ((s / period) % 1)), f)


def roar_palms(a, f):
    """Endless Grief's hands pull away from its face in the roar: ROAR.PalmL and PalmR in DinoLifeController."""
    t = 2 * math.pi * f / kit.IDLE_FRAMES
    r = ((1 - math.cos(t)) / 2) ** 10
    for name, side in (("PalmL", 1), ("PalmR", -1)):
        kit.pose_bone(a, name, (0, 0, side * 0.8 * r), None, f)


def walk_pose(a, f):
    stride = kit.WALK_FRAMES
    kit.WALK_FRAMES = CHARGE_FRAMES  # the usual walk, a third faster
    thorn_walk(a, f)
    kit.WALK_FRAMES = stride
    for name in ("PalmL", "PalmR"):
        kit.pose_bone(a, name, (0, 0, 0), None, f)
    rage(a, f)


def idle_pose(a, f):
    thorn_idle(a, f)
    roar_palms(a, f)
    for name in ("FrontL", "FrontR", "BackL", "BackR", "LegL", "LegR", "ShinL", "ShinR"):  # no idle of their own: rage adds to rest, not to the last frame
        kit.pose_bone(a, name, (0, 0, 0), None, f)
    rage(a, f)


def animate(armature):
    """The Volcano's walk and idle (jaw snap and roar) with the thrashing and the rage on top."""
    walk = kit.add_action(armature, "Walk", WALK_PREVIEW, walk_pose, 2)
    idle = kit.add_action(armature, "Idle", kit.IDLE_FRAMES, idle_pose, 2)
    for action in (walk, idle):  # tears fall steadily, not eased between keys
        for curve in fcurves_of(action):
            if any(f'"{name}"' in curve.data_path for name in DRIP):
                for key in curve.keyframe_points:
                    key.interpolation = "LINEAR"
    return walk, idle


# ---------------------------------------------------------------------- shapes


def rage_maw(m, f, skull_w, length, snout_w, upper_h, lower_h, rng, gape=0.2, drop=0.42, upper="Body", lower="Accent", tooth=0.4, per_side=6, head="Head",
             jaw="Jaw", tongue=True, lift=0.12, on_jaw=None, eye=0.28, jaw_long=1.0, back_h=None):
    """The mouth they share, built in frame f, whose origin is the middle of the mouth's back and whose +Y is out of the
    mouth: an upper jaw on the head bone, a lower jaw on the jaw bone hanging open by drop (radians), two rows of crooked
    teeth in each, strands stretched between the jaws, and at the back of the throat, the throat eye. back_h shortens the
    throat's back wall, for a head whose cheeks close the mouth's sides (it hangs below the jaw otherwise). Returns the
    snout's top height along it."""
    m.bone = head
    back = (-0.05, 0, gape / 2 + upper_h * 0.5, skull_w * 0.96, upper_h)
    tip = (length, 0, gape / 2 + upper_h / 2 + lift, snout_w, upper_h)
    yloft(f, upper, back, tip)
    yloft(f, "Mouth", (0, 0, gape / 2 - 0.03, skull_w * 0.84, 0.06), (length * 0.95, 0, gape / 2 + lift * 0.95 - 0.03, snout_w * 0.86, 0.06))
    open_h = back_h if back_h is not None else gape + drop * length * 0.8 + 0.2
    f.box("Mouth", 0, 0.03, gape / 2 - open_h / 2, skull_w * 0.88, 0.12, open_h)
    if eye:
        z = gape / 2 - open_h * 0.5
        slab(f, "EyeGlow", 0, z, 0.12, eye, 0.05, 10)
        slab(f, "Slit", 0, z, 0.155, eye * 0.82, 0.03, 8, 0.24)

    def width(y):
        return skull_w * 0.96 + (snout_w - skull_w * 0.96) * y / length

    def roof(y):
        return gape / 2 + lift * y / length

    crooked_teeth(m, f, width, roof, length, tooth, per_side, rng, False, across=3)
    crooked_teeth(m, f, lambda y: width(y) * 0.66, roof, length * 0.9, tooth * 0.6, per_side - 1, rng, False, across=2, fang=-99)

    hinge = f.at(0, -0.05, -gape / 2)
    m.use(jaw, hinge, head)
    lf = Frame(m, hinge, f.r @ turn(x=-drop))
    ll = length * 0.95 * jaw_long
    yloft(lf, lower, (0, 0, -lower_h * 0.55, skull_w * 0.86, lower_h * 1.1), (ll, 0, -lower_h * 0.5, snout_w * 0.92, lower_h))
    yloft(lf, "Mouth", (0, 0, 0.0, skull_w * 0.72, 0.06), (ll * 0.95, 0, 0.0, snout_w * 0.76, 0.06))

    def low_width(y):
        return skull_w * 0.86 + (snout_w * 0.92 - skull_w * 0.86) * y / ll

    crooked_teeth(m, lf, low_width, lambda y: 0.0, ll, tooth * 0.9, per_side, rng, True, across=2)
    crooked_teeth(m, lf, lambda y: low_width(y) * 0.62, lambda y: 0.0, ll * 0.88, tooth * 0.55, per_side - 1, rng, True, across=2, fang=-99)
    if tongue:
        lf.beam("Tongue", (0, ll * 0.1, 0.06), (0, ll * 0.74, 0.08), snout_w * 0.34, 0.1, snout_w * 0.22)
    for side in (-1, 1):
        beam(m, "Sinew", f.at(side * skull_w * 0.38, length * 0.2, gape / 2 + 0.02), lf.at(side * skull_w * 0.34, length * 0.24, 0.02), 0.07, None, 0.04)
        m.stretch("Sinew", head)
    if on_jaw:
        on_jaw(m, lf, ll)
    m.bone = head
    return lambda y: gape / 2 + upper_h + lift * y / length


def weeping(m, spots, ground, parent="Head", bone="Drip", size=0.08, grown=1.0):
    """Tears falling for ever from each spot, on a Drip bone: each spot a (x, y, z), `gap` apart down to ground (see
    DRIP). grown is what the monster will be grow()n by afterwards, so the gap comes out right."""
    # 2026-11-09: the owner had the falling tears taken off (they read as stray dots). The Drip bone stays, with nothing
    # on it, because the game turns RAGE on for any monster that has one.
    m.use(bone, spots[0], parent)
    m.bone = parent


def track(m, a, b, width=0.08):
    """A tear's shining track down a face."""
    beam(m, "Stream", a, b, width, 0.04, width * 0.7)


def chain(m, n, points, link, parent="Spine", role="Chain"):
    """A broken chain through points on three bones, Lash<n>a, b and c, which never stop lashing. Links turned a quarter
    from each other. Leaves m.bone on its last bone; returns the tip."""
    segments = len(points) - 1
    per = math.ceil(segments / 3)
    bone = parent
    turned = False
    for i, (a, b) in enumerate(zip(points, points[1:])):
        if i % per == 0:
            before = bone
            bone = f"Lash{n}{'abc'[i // per]}"
            m.use(bone, tuple(a), before)
        p, q = Vector(a), Vector(b)
        count = max(1, round((q - p).length / (link * 1.5)))
        run = (q - p) / count
        for k in range(count):
            c = p + run * (k + 0.5)
            half = run * 0.62
            turned = not turned
            beam(m, role, tuple(c - half), tuple(c + half), link * (1 if turned else 0.42), link * (0.42 if turned else 1))
    return Vector(points[-1])


def arm_leg(m, bone, hip, elbow, wrist, w0, w1, side, size=1.0, role="Belly"):
    """A long arm for a leg, its elbow high and its hand flat on the ground, on one bone from the hip."""
    m.use(bone, hip)
    limb(m, role, [hip, elbow, wrist], w0, w1)
    ball(m, role, *elbow, w0 * 0.62, 6, 4)
    hand(m, role, wrist, (side * 0.16, 1, -0.12), (0, 0.12, 1), size=size, spread=0.9, curl=0.16, long=1.2, thumb=-side)
    m.bone = "Spine"


def rag(m, role, top, length, width, rng, lean=(0, -0.3)):
    """A torn strip of cloth hanging from top."""
    p = Vector(top)
    q = p + Vector((rng.uniform(-0.3, 0.3) + lean[0], rng.uniform(-0.3, 0.3) + lean[1], -length))
    plate(m, role, tuple(p), tuple(q), (1, 0.2, 0), width, width * 0.15, 0.08)


# ---------------------------------------------------------------------- the common ones


def teddy_wrecks():
    """The Lost Bear, gone bad. A worn teddy hunched forward on stubby legs, its whole face torn open into a mouth of
    nails, one red eye glaring from under a stitched brow and a button hanging by a thread over the other. Stuffing
    bursts out of its belly and its shoulder, its paws end in long nails, and loose threads whip about it."""
    rng = random.Random(1501)
    m = monster("dino_TeddyWrecks", Body="#8f8a80", Accent="#5f5b55", Belly="#bbb5a8", Claw="#d7d2c5", Stuffing="#d4d0c6", Seam="#26262a", Button=IRON_DARK)
    m.joint("Spine", (0, -0.15, 1.3))
    biped_legs(m, 0.72, -0.15, 1.05, 0.74, 0.74, 0.56, 1.1, 0.28)
    ball(m, "Body", 0, 0.0, 1.85, 1.32, 10, 6)
    ball(m, "Belly", 0, 0.62, 1.7, 0.96, 8, 4)
    # The rip down its belly, stitched once, and the stuffing coming out.
    f = Frame(m, (0, 1.48, 1.72), turn())
    slab(f, "Socket", 0, 0, 0.0, 0.7, 0.1, 10, 0.5)
    for x, z, r in ((0.05, 0.0, 0.34), (-0.16, 0.34, 0.24), (0.2, -0.32, 0.26), (0.32, 0.18, 0.18)):
        ball(m, "Stuffing", x, 1.56, 1.72 + z, r, 6, 4)
    for z in (0.52, 0.2, -0.14, -0.44):
        beam(m, "Seam", (-0.5, 1.47, 1.72 + z), (0.5, 1.47, 1.72 + z - 0.06), 0.05, 0.05)
    for x, y, z, r in ((1.12, 0.3, 2.65, 0.4), (1.3, 0.1, 2.35, 0.3), (0.95, 0.55, 2.8, 0.26)):  # the torn shoulder
        ball(m, "Stuffing", x, y, z, r, 6, 4)
    lash(m, 1, wander((0.15, 1.5, 1.45), (0.5, 3.0, 0.4), rng, 7, (0.2, 0, -0.1), 0.08), 0.13, 0.04, "Spine", "Seam")
    lash(m, 2, wander((-0.6, -1.0, 2.2), (-1.4, -2.7, 2.6), rng, 7, (0, 0, 0.4), 0.12), 0.12, 0.04, "Spine", "Seam")
    m.bone = "Spine"

    for side in (-1, 1):  # paws out, nails first
        letter = "L" if side < 0 else "R"
        shoulder = (side * 1.28, 0.25, 2.4)
        m.use(f"Arm{letter}", shoulder)
        elbow = (side * 1.9, 0.6, 1.75)
        paw = (side * 1.75, 1.75, 1.75 + 0.3 * side)
        limb(m, "Body", [shoulder, elbow, paw], 0.86, 0.72)
        ball(m, "Accent", *paw, 0.52, 6, 4)
        for k in (-1.5, -0.5, 0.5, 1.5):
            base = Vector(paw) + Vector((k * 0.2, 0.3, 0))
            thorn(m, "Claw", base, base + Vector((k * 0.22, 0.95, -0.25 + rng.uniform(-0.1, 0.1))), 0.13, (0, 0, 0.1))
    m.bone = "Spine"

    r = 1.62
    hinge = (0, 0.15, 2.75)
    top = Frame(m, hinge, turn(x=0.3, y=0.1))  # its skull wrenched back
    low = Frame(m, hinge, turn(x=-0.5, y=-0.07))
    cy = 1.0
    m.use("Head", (0, 0.1, 2.55))
    half_ball(top, "Body", 0, cy, r, 1, 12, 4)
    top.prism("Mouth", 0, cy, -0.05, 0.02, r * 0.94, r * 0.94, 12)
    ball(m, "Mouth", *top.at(0, 0.85, -0.25), 1.05, 8, 4)
    eye = top.at(0, 1.72, -0.5)  # at the back of the dark, just out of it
    ball(m, "EyeGlow", *eye, 0.36, 8, 4)
    slab(Frame(m, eye, top.r @ turn(x=0.22)), "Slit", 0, 0, 0.34, 0.3, 0.05, 8, 0.24)
    for k in range(14):  # nails round the rip, every one bent its own way
        a = math.radians(-20 + k * 220 / 13)
        px, py = math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9
        size = rng.uniform(0.42, 0.72) * (1.5 if k in (3, 7, 10) else 1)
        point(m, "Teeth", top.at(px, py, 0.02), top.at(px * rng.uniform(0.82, 1.04), py + rng.uniform(-0.1, 0.16), -size), 0.24)
    # Ears, one torn half off, and the seams.
    ball(m, "Accent", *top.at(-1.2, cy - 0.5, r * 0.82), 0.62, 8, 4)
    ball(m, "Accent", *top.at(1.34, cy - 0.45, r * 0.68), 0.42, 6, 3)
    ball(m, "Stuffing", *top.at(1.46, cy - 0.36, r * 0.88), 0.2, 6, 3)
    seam = [top.at(0.25 * math.sin(t * 3), cy - 0.2 - r * 0.95 * math.cos(t), r * 0.98 * math.sin(t)) for t in [i * math.pi / 8 for i in range(2, 8)]]
    for p, q in zip(seam, seam[1:]):
        beam(m, "Seam", p, q, 0.06, 0.06)
    for p in seam[1:-1]:
        beam(m, "Seam", tuple(Vector(p) + Vector((-0.2, 0, 0))), tuple(Vector(p) + Vector((0.2, 0, 0))), 0.05, 0.05)
    # The eyes: one glaring, and a button dangling over the other's socket.
    right = Vector((0.46, 0.84, 0.36)).normalized()
    glare(m, top.at(*(Vector((0, cy, 0)) + right * r * 0.98)), top.r @ Vector((0.22, 1, -0.1)), 0.46, -1, 0.75, brow="Accent", spikes=0)
    left = Vector((-0.46, 0.84, 0.36)).normalized()
    socket = Vector((0, cy, 0)) + left * r * 0.98
    glare(m, top.at(*socket), top.r @ Vector((-0.22, 1, -0.1)), 0.36, 1, 0.75, brow="Accent", spikes=0)
    tip = lash(m, 3, [top.at(*(socket + Vector((-0.34, 0.1, 0.1)))), top.at(*(socket + Vector((-0.46, 0.22, -0.12)))), top.at(*(socket + Vector((-0.5, 0.26, -0.42)))),
                      top.at(*(socket + Vector((-0.52, 0.26, -0.72))))], 0.05, 0.04, "Head", "Seam")
    disc_f = Frame(m, tuple(tip + Vector((0, 0, -0.26))), top.r)
    slab(disc_f, "Button", 0, 0, 0, 0.3, 0.1, 10)
    for dx in (-0.08, 0.08):
        slab(disc_f, "Socket", dx, 0, 0.055, 0.05, 0.02, 6)
    # Tears from both eyes, running off its cheeks.
    m.bone = "Head"
    pr, pl = top.at(*(Vector((0, cy, 0)) + right * r * 1.02)), top.at(*socket)
    track(m, (pr[0] + 0.1, pr[1] + 0.05, pr[2] - 0.2), (pr[0] + 0.22, pr[1] + 0.14, pr[2] - 0.72))
    weeping(m, [(pr[0] + 0.14, pr[1] + 0.2, pr[2] - 0.34), (pl[0] + 0.06, pl[1] + 0.14, pl[2] - 0.3)], 0.5)

    m.use("Jaw", hinge, "Head")
    half_ball(low, "Belly", 0, cy, r * 0.95, -1, 12, 3, 0.74)
    low.prism("Mouth", 0, cy, -0.02, 0.05, r * 0.86, r * 0.86, 12)
    for k in range(12):
        a = math.radians(-12 + k * 204 / 11)
        px, py = math.cos(a) * r * 0.82, cy + math.sin(a) * r * 0.82
        size = rng.uniform(0.4, 0.68) * (1.5 if k in (2, 6, 9) else 1)
        point(m, "Teeth", low.at(px, py, -0.02), low.at(px * rng.uniform(0.84, 1.04), py + rng.uniform(-0.12, 0.14), size), 0.22)
    for side in (-1, 1):  # the last of the stitches, stretched across the rip
        for k in range(2):
            beam(m, "Seam", top.at(side * (1.28 - 0.4 * k), 0.45 + 0.5 * k, 0.02), low.at(side * (1.2 - 0.4 * k), 0.45 + 0.5 * k, 0.02), 0.05, None, 0.04)
            m.stretch("Seam", "Head")
    m.bone = "Spine"
    m.head_centre = tuple(top.at(0, cy + 0.4, 0.1))
    return m


def good_boy():
    """The dog that waited too long. A gaunt ash-grey hound, its ribs showing, head low and hackles up, every tooth bared,
    its collar still on and the chain it snapped lashing behind it, and a tail like a whip."""
    rng = random.Random(1502)
    m = monster("dino_GoodBoy", Body="#a39f96", Accent="#54524f", Belly="#d2cdc0", Claw="#26262a", Collar=IRON, Tag=BONE_DARK)
    m.joint("Spine", (0, -0.3, 3.1))
    for bone, x, y, top_, w_ in (("FrontL", -0.66, 2.0, 3.1, 0.58), ("FrontR", 0.66, 2.0, 3.1, 0.58), ("BackL", -0.56, -2.5, 2.9, 0.66), ("BackR", 0.56, -2.5, 2.9, 0.66)):
        clawed_leg(m, bone, x, y, top_, w_, rng, reach=1.0)
    rump = ((-3.1, 0, 3.25, 0.95, 1.0), (-1.0, 0, 3.4, 0.72, 0.72))  # a waist you could close a hand round
    chest = ((-1.0, 0, 3.4, 0.72, 0.72), (2.3, 0, 3.0, 1.36, 2.2))
    m.loft_y("Body", *rump)
    m.loft_y("Body", *chest)
    # Its ribs, standing out of its sides, and its spine.
    for k in range(6):
        y = -0.6 + k * 0.52
        half = 0.42 + 0.09 * k
        low_z = 3.0 - 0.17 * k
        for side in (-1, 1):
            limb(m, "Belly", [(side * half * 0.5, y, 3.78), (side * (half + 0.14), y - 0.05, (3.78 + low_z) / 2), (side * half * 0.8, y + 0.04, low_z)], 0.17, 0.11, False)
    ridge(m, "Belly", along((0, -2.8, 3.72), (0, 1.7, 4.08), 11), rng, 0.45, 0.2, 0.4)
    ridge(m, "Accent", along((0, -1.6, 3.8), (0, 2.1, 4.14), 12), rng, 1.05, 0.34, 0.7)  # hackles
    bristle(m, "Accent", chest, rng, 12, 0.5, 0.2, 0.8)
    m.bone = "Spine"

    pts = [(0, -3.05, 3.3), (0.1, -4.0, 3.9), (-0.15, -4.9, 4.35), (0.1, -5.8, 4.9)]
    widths = (0.42, 0.3, 0.18, 0.05)
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        m.use(f"Tail{i + 1}", a, f"Tail{i}" if i else "Spine")
        beam(m, "Accent", a, b, widths[i], None, widths[i + 1])
        if i:
            m.stretch("Accent", f"Tail{i}")
    m.bone = "Spine"

    m.use("Neck", (0, 2.0, 3.5))
    neck = [(0, 1.7, 3.4), (0, 2.9, 3.6), (0, 3.8, 3.75)]
    limb(m, "Body", neck, 1.5, 1.05)
    ridge(m, "Accent", along((0, 2.1, 4.25), (0, 3.7, 4.4), 7), rng, 0.95, 0.32, 0.8)
    # The collar, spiked, its tag, and the chain it broke.
    collar = [(math.cos(k * math.tau / 10) * 0.86, 3.05 + 0.1 * math.sin(k * math.tau / 10), 3.6 + math.sin(k * math.tau / 10) * 0.86) for k in range(11)]
    for a, b in zip(collar, collar[1:]):
        beam(m, "Collar", a, b, 0.24, 0.34)
    for p in collar[:-1:2]:
        d = Vector((p[0], 0, p[2] - 3.6)).normalized()
        point(m, "Claw", p, tuple(Vector(p) + d * 0.42), 0.16)
    m.block("Tag", 0, 3.1, 2.56, 0.42, 0.08, 0.42)
    chain(m, 1, wander((0.1, 2.9, 4.5), (1.2, -1.4, 5.7), rng, 7, (0.6, 0, 1.0), 0.14), 0.22, "Neck")
    m.bone = "Neck"
    chain(m, 2, wander((-0.7, 3.1, 3.2), (-1.6, 3.9, 0.9), rng, 7, (-0.2, 0.2, 0), 0.1), 0.16, "Neck")
    m.bone = "Neck"

    w, d, h = 1.34, 1.2, 1.12
    yc, zc = 4.45, 3.6
    m.head_joint(yc, d, zc, h)
    hf = Frame(m, (0, yc, zc), turn(x=-0.14, y=0.05))
    hf.box("Body", 0, 0, 0, w, d, h)
    hf.box("Accent", 0, -0.1, h / 2 + 0.03, w * 0.8, d * 0.8, 0.12)
    mf = Frame(m, hf.at(0, d / 2, -0.3), hf.r)
    top_at = rage_maw(m, mf, w, 2.05, 0.62, 0.44, 0.34, rng, gape=0.2, drop=0.56, upper="Body", lower="Accent", tooth=0.4, per_side=6, lift=0.12, eye=0.26)
    for side in (-1, 1):  # a snarl: lips pulled up, the snout creased
        for k in range(3):
            y = 0.5 + 0.34 * k
            mf.beam("Accent", (side * 0.08, y, top_at(y) + 0.02), (side * (0.46 - 0.07 * k), y + 0.12, top_at(y) - 0.26), 0.09, 0.06)
    ball(m, "Socket", *mf.at(0, 2.02, top_at(2.0) - 0.06), 0.15, 6, 3)  # its nose
    glare(m, hf.at(-0.38, d / 2 - 0.02, 0.26), hf.r @ Vector((-0.2, 1, 0.14)), 0.4, 1, 0.8, brow="Accent", spikes=0)
    glare(m, hf.at(0.38, d / 2 - 0.02, 0.26), hf.r @ Vector((0.2, 1, 0.14)), 0.4, -1, 0.8, brow="Accent", spikes=0)
    for side, length in ((-1, 1.5), (1, 0.95)):  # ears pinned back, one torn
        base = hf.at(side * 0.5, -0.2, h / 2 - 0.05)
        plate(m, "Accent", base, hf.at(side * 0.95, -0.25 - length, h / 2 + 0.62), (1, 0, 0.2), 0.68, 0.08, 0.12)
    p = hf.at(-0.42, d / 2 + 0.06, 0.02)
    q = hf.at(0.42, d / 2 + 0.06, 0.02)
    track(m, p, hf.at(-0.5, d / 2 + 0.55, -0.32))
    track(m, q, hf.at(0.5, d / 2 + 0.55, -0.32))
    weeping(m, [hf.at(-0.56, d / 2 + 0.3, -0.05), hf.at(0.56, d / 2 + 0.3, -0.05)], 1.0)
    m.bone = "Spine"
    m.head_centre = tuple(hf.at(0, d / 2 + 0.6, -0.1))
    return m


LID_DROP = 0.5


def casket_case():
    """A coffin for a head. Its lid is the upper jaw and its box the lower, both edges full of nails, carried low and nose
    down on a pale neck, red eyes glaring out of the lid and another from the dark inside it. It gallops on four long
    arms, elbows high, on its hands, with two more reaching out ahead of it, and its shroud streams out behind."""
    rng = random.Random(1503)
    m = monster("dino_CasketCase", Body="#5b5752", Accent="#23232a", Belly="#c7c3b8", Claw="#26262a", Inside="#17161a", Strap=IRON, Nail="#8a8a90", Shroud="#b4b1a8")
    m.joint("Spine", (0, -0.9, 5.0))
    for bone, side, y, ahead in (("FrontL", -1, 0.4, 1), ("FrontR", 1, 0.4, 1), ("BackL", -1, -2.0, -1), ("BackR", 1, -2.0, -1)):
        hip = (side * 0.9, y, 5.0)
        arm_leg(m, bone, hip, (side * 3.0, y + ahead * 0.5, 6.4), (side * 3.0, y + ahead * 1.0, 0.72), 0.74, 0.42, side, 1.1)
    # The body: a knot of black shroud and ribs.
    ball(m, "Accent", 0, -0.8, 5.0, 1.75, 8, 5)
    ball(m, "Accent", 0, 0.4, 5.25, 1.5, 8, 4)
    for k in range(5):
        a = -0.9 + k * 0.45
        for side in (-1, 1):
            limb(m, "Belly", [(side * 0.3, a, 6.5), (side * 1.55, a, 5.5), (side * 1.4, a + 0.1, 4.3)], 0.2, 0.12, False)
    for k, (x, y, z) in enumerate(((-1.2, -1.6, 4.3), (0.9, -1.9, 4.4), (-0.4, -2.2, 4.8), (1.4, -0.8, 4.2), (-1.5, -0.4, 4.1), (0.3, 0.8, 3.9))):
        rag(m, "Accent", (x, y, z), rng.uniform(1.0, 2.2), 0.8, rng)
    # The shroud, streaming out behind: pale strips, each on its own bones.
    lash(m, 1, wander((-0.6, -2.3, 5.8), (-2.2, -6.0, 7.2), rng, 7, (0, 0, 0.6), 0.16), 1.0, 0.2, "Spine", "Shroud", None, 0.2, 0.5, (1, 0, 0.2))
    lash(m, 2, wander((0.7, -2.4, 5.4), (2.0, -6.2, 5.8), rng, 7, (0, 0, 0.7), 0.16), 0.95, 0.18, "Spine", "Shroud", None, 0.2, 0.5, (1, 0, 0.2))
    lash(m, 3, wander((0, -2.5, 6.4), (0.2, -5.6, 8.6), rng, 7, (0, 0, 0.3), 0.16), 0.9, 0.16, "Spine", "Shroud", None, 0.2, 0.5, (1, 0, 0))
    m.bone = "Spine"
    for letter, side in (("L", -1), ("R", 1)):  # the two that grab
        shoulder = (side * 1.1, 1.0, 4.4)
        m.use(f"Arm{letter}", shoulder)
        elbow = (side * 1.9, 2.2, 3.1)
        wrist = (side * 1.5, 4.3, 3.0 + side * 0.4)
        limb(m, "Belly", [shoulder, elbow, wrist], 0.56, 0.36)
        hand(m, "Belly", wrist, (side * -0.1, 1, 0.1), (0, 0, 1), size=1.05, spread=1.0, curl=0.34, long=1.35, thumb=-side)
    m.bone = "Spine"

    m.use("Neck", (0, 0.8, 5.5))
    limb(m, "Belly", [(0, 0.3, 5.2), (0, 1.5, 6.3), (0, 2.3, 7.2)], 1.05, 0.8)
    for k in range(3):
        y = 1.0 + 0.5 * k
        beam(m, "Accent", (-0.55, y, 5.9 + 0.5 * k), (0.55, y, 5.9 + 0.5 * k), 0.16, 0.3)

    # The head: lid on Head, box on Jaw, hinged at its foot. Nose down, so the lid faces whatever it's looking at.
    hinge = (0, 2.0, 7.5)
    m.head_joint(hinge[1] + 0.3, 0.6, hinge[2] + 0.1, 0.4)
    pitch = -0.62
    lid = Frame(m, hinge, turn(x=pitch + 0.18))
    box = Frame(m, hinge, turn(x=pitch - LID_DROP))
    shape = [(-0.95, 0), (0.95, 0), (1.72, 3.9), (1.25, 5.8), (-1.25, 5.8), (-1.72, 3.9)]
    flat_outline(m, "Body", lid, shape, 0.0, 0.46)
    flat_outline(m, "Accent", lid, [(x * 0.72, 0.5 + y * 0.84) for x, y in shape], 0.46, 0.62)
    flat_outline(m, "Inside", lid, [(x * 0.84, 0.3 + y * 0.9) for x, y in shape], -0.04, 0.02)
    for y in (0.7, 2.3, 4.9):  # iron straps
        wide = 1.04 + 0.7 * min(y / 3.9, 1) if y < 4 else 1.54
        lid.box("Strap", 0, y, 0.25, wide * 2 + 0.12, 0.38, 0.6)
    for k in range(9):  # its upper teeth: coffin nails, along the edge
        t = k / 8
        for side in (-1, 1):
            y = 0.5 + 5.1 * t
            half = 0.95 + 0.77 * min(y / 3.9, 1) - (0.47 * max(y - 3.9, 0) / 1.9)
            size = rng.uniform(0.5, 0.95)
            point(m, "Teeth", lid.at(side * (half - 0.14), y, 0.0), lid.at(side * (half - 0.16 + rng.uniform(-0.12, 0.06)), y + rng.uniform(-0.1, 0.14), -size), 0.2)
    for k in range(5):
        x = -1.0 + 0.5 * k
        point(m, "Teeth", lid.at(x, 5.72, 0.0), lid.at(x + rng.uniform(-0.1, 0.1), 5.78, -rng.uniform(0.6, 1.05)), 0.2)
    # Its eyes, on the lid, under brows of iron.
    glare(m, lid.at(-0.72, 3.65, 0.64), lid.r @ Vector((-0.14, 0.42, 1)), 0.62, 1, 0.8, brow="Strap", spikes=0)
    glare(m, lid.at(0.72, 3.65, 0.64), lid.r @ Vector((0.14, 0.42, 1)), 0.62, -1, 0.8, brow="Strap", spikes=0)
    m.bone = "Head"
    for x in (-0.72, 0.72):
        track(m, lid.at(x, 3.6, 0.66), lid.at(x * 1.08, 5.7, 0.5), 0.1)
    # A chain round it, snapped, and the lid's edge bristling.
    lash_at = lid.at(1.3, 2.6, 0.3)
    chain(m, 4, wander(lash_at, (lash_at[0] + 1.6, lash_at[1] + 0.4, lash_at[2] - 2.4), rng, 7, (0.5, 0, 0), 0.1), 0.2, "Head")
    m.bone = "Head"
    weeping(m, [lid.at(-0.8, 5.76, 0.5), lid.at(0.8, 5.76, 0.5)], 1.0)

    m.use("Jaw", hinge, "Head")
    flat_outline(m, "Body", box, shape, -1.3, 0.0)
    flat_outline(m, "Inside", box, [(x * 0.86, 0.3 + y * 0.9) for x, y in shape], 0.0, 0.05)
    flat_outline(m, "Strap", box, [(x * 1.03, y * 1.012 - 0.04) for x, y in shape], -1.3, -1.08)
    for k in range(9):
        t = k / 8
        for side in (-1, 1):
            y = 0.5 + 5.1 * t
            half = 0.95 + 0.77 * min(y / 3.9, 1) - (0.47 * max(y - 3.9, 0) / 1.9)
            size = rng.uniform(0.5, 0.95)
            point(m, "Teeth", box.at(side * (half - 0.16), y, 0.02), box.at(side * (half - 0.2 + rng.uniform(-0.1, 0.06)), y + rng.uniform(-0.1, 0.14), size), 0.2)
    for k in range(5):
        x = -1.0 + 0.5 * k
        point(m, "Teeth", box.at(x, 5.7, 0.02), box.at(x + rng.uniform(-0.1, 0.1), 5.74, rng.uniform(0.6, 1.05)), 0.2)
    # The throat eye, at the coffin's foot, and the dark.
    e = Frame(m, box.at(0, 1.5, 0.08), box.r @ turn(x=math.pi / 2 + LID_DROP * 0.5))
    slab(e, "Socket", 0, 0, 0.0, 0.72, 0.06, 10)
    slab(e, "EyeGlow", 0, 0, 0.05, 0.5, 0.05, 10)
    slab(e, "Slit", 0, 0, 0.09, 0.42, 0.03, 8, 0.22)
    m.bone = "Spine"
    m.head_centre = tuple(lid.at(0, 4.4, 0.0))
    return m


# ---------------------------------------------------------------------- the fierce ones


def wailing_widow():
    """A tall black veiled thing, leaning right out over you. A bone mask with burning eyes, a jaw hanging to its chest in
    one long scream, its veil torn into strips that lash about its head, and pale arms as long as it is tall, every
    finger a claw."""
    rng = random.Random(1504)
    m = monster("dino_WailingWidow", Body="#2a2a30", Accent="#101014", Belly="#d6d2c7", Claw="#f0ece0", Lace="#55555c", Veil="#17171b")
    m.joint("Spine", (0, -0.2, 4.0))
    biped_legs(m, 0.55, -0.2, 3.7, 0.62, 2.6, 0.32, 1.35, 0.22)
    # Its skirt, torn off at different lengths.
    prism(m, "Body", 0, -0.2, 2.1, 4.3, 1.75, 0.92, 8, math.pi / 8)
    for k in range(10):
        a = k * math.tau / 10 + rng.uniform(-0.15, 0.15)
        p = Vector((math.cos(a) * 1.6, -0.2 + math.sin(a) * 1.6, 2.5))
        q = Vector((math.cos(a) * 2.05, -0.2 + math.sin(a) * 2.05, rng.uniform(0.55, 1.5)))
        plate(m, "Accent" if k % 2 else "Body", tuple(p), tuple(q), (-math.sin(a), math.cos(a), 0), 1.05, 0.14, 0.08)
    # A thin body bent right forward, ribs of lace.
    f = Frame(m, (0, -0.2, 4.2), turn(x=-0.42))
    f.prism("Body", 0, 0, 0, 2.7, 0.9, 1.15, 8)
    f.prism("Body", 0, 0, 2.7, 3.2, 1.15, 0.5, 8)
    for k in range(5):
        z = 0.55 + 0.46 * k
        half = 0.9 + 0.06 * k
        f.beam("Lace", (-half, 0.68, z), (half, 0.68, z + 0.08), 0.1, 0.1)
    m.bone = "Spine"
    for letter, side in (("L", -1), ("R", 1)):  # arms as long as it is tall, up and out
        shoulder = f.at(side * 1.05, 0, 2.75)
        m.use(f"Arm{letter}", shoulder)
        elbow = (side * 3.0, shoulder[1] + 0.3, shoulder[2] + 0.6)
        wrist = (side * 3.1, shoulder[1] + 3.5, shoulder[2] - 0.3 + side * 0.5)
        limb(m, "Belly", [shoulder, elbow, wrist], 0.5, 0.3)
        ball(m, "Belly", *elbow, 0.36, 6, 4)
        for k in range(4):
            rag(m, "Accent", Vector(shoulder).lerp(Vector(elbow), 0.2 + 0.2 * k), rng.uniform(1.0, 2.2), 0.46, rng, (0, 0))
        hand(m, "Belly", wrist, (side * -0.25, 1, 0.1), (side * 0.2, 0, 1), size=1.45, spread=1.15, curl=0.34, long=1.6, thumb=-side)
    m.bone = "Spine"
    lash(m, 5, wander((-0.9, -1.6, 2.8), (-2.4, -4.0, 1.2), rng, 7, (0, 0, 0.5), 0.14), 1.3, 0.2, "Spine", "Veil", None, 0.2, 0.5, (1, 0, 0.2))
    lash(m, 6, wander((1.0, -1.5, 3.0), (2.3, -4.4, 1.6), rng, 7, (0, 0, 0.5), 0.14), 1.25, 0.2, "Spine", "Veil", None, 0.2, 0.5, (1, 0, 0.2))
    m.bone = "Spine"

    neck_top = f.at(0, 0.1, 3.1)
    m.use("Neck", neck_top)
    limb(m, "Belly", [neck_top, (0, neck_top[1] + 0.7, neck_top[2] + 0.6), (0, neck_top[1] + 1.2, neck_top[2] + 0.8)], 0.56, 0.42)
    yc, zc = neck_top[1] + 1.8, neck_top[2] + 0.9
    w, d, h = 2.0, 1.8, 2.6
    m.head_joint(yc, d, zc, h)
    hf = Frame(m, (0, yc, zc), turn(x=-0.1, y=-0.08))
    # A long mask of bone in a black veil.
    hf.prism("Veil", 0, -0.35, -h * 0.5, h * 0.74, 1.5, 0.6, 8)
    ball(m, "Veil", *hf.at(0, -0.4, h * 0.24), 1.52, 8, 5)
    yloft(hf, "Belly", (0.0, 0, 0.4, w, h * 0.8), (d / 2 + 0.14, 0, 0.4, w * 0.86, h * 0.76))
    # Eyes, sunk and burning, the brows dragged down to the nose.
    glare(m, hf.at(-0.5, d / 2 + 0.14, 0.72), hf.r @ Vector((-0.12, 1, 0)), 0.62, 1, 0.85, brow="Accent", spikes=0)
    glare(m, hf.at(0.5, d / 2 + 0.14, 0.72), hf.r @ Vector((0.12, 1, 0)), 0.62, -1, 0.85, brow="Accent", spikes=0)
    yloft(hf, "Accent", (d / 2 + 0.12, 0, 0.22, 0.34, 0.6), (d / 2 + 0.34, 0, 0.12, 0.2, 0.5))
    # The mouth: a short snout, and a jaw like a drawer pulled right out, hanging to its chest in one long scream.
    mf = Frame(m, hf.at(0, d / 2 - 0.14, -0.42), hf.r)
    rage_maw(m, mf, 1.54, 0.95, 1.14, 0.3, 0.34, rng, gape=0.3, drop=1.12, upper="Belly", lower="Belly", tooth=0.46, per_side=5, tongue=False, lift=0.02, eye=0.34, jaw_long=2.5)
    for x in (-0.56, 0.56):
        track(m, hf.at(x, d / 2 + 0.22, 0.4), hf.at(x * 1.15, d / 2 + 0.2, -0.3), 0.1)
    # Its veil, in strips, streaming and lashing all round its head.
    for n, (a, b, bow) in enumerate((((-0.7, -0.1, 1.2), (-3.4, -2.6, 2.6), (-0.3, 0, 0.8)), ((0.7, -0.1, 1.25), (3.5, -2.2, 2.9), (0.3, 0, 0.8)),
                                     ((-1.1, -0.6, 0.2), (-3.9, -3.2, -0.7), (0, 0, 0.8)), ((1.1, -0.6, 0.2), (3.9, -3.5, -1.0), (0, 0, 0.9))), 1):
        lash(m, n, wander(hf.at(*a), hf.at(*b), rng, 7, bow, 0.16), 1.15, 0.16, "Head", "Veil", None, 0.2, 0.5, (0.45, 0.25, 0.85))
    m.bone = "Head"
    weeping(m, [hf.at(-0.62, d / 2 + 0.3, -0.05), hf.at(0.62, d / 2 + 0.3, -0.05)], 2.0)
    m.bone = "Spine"
    m.head_centre = tuple(hf.at(0, d / 2 + 0.2, 0.1))
    return m


def half_bell(m, role, f, steps, up=1, sides=10, end_role=None):
    """Half a bell lying along its frame's Y: steps are (y, radius); up=1 the top half, -1 the bottom."""
    rings = []
    for y, r in steps:
        rings.append([f.at(r * math.cos(math.pi * i / sides), y, up * r * math.sin(math.pi * i / sides)) for i in range(sides + 1)])
    n = sides + 1
    verts = [p for ring in rings for p in ring]
    faces = []
    for k in range(len(rings) - 1):
        for i in range(sides):
            faces.append([k * n + i, k * n + i + 1, (k + 1) * n + i + 1, (k + 1) * n + i])
        faces.append([k * n, (k + 1) * n, (k + 1) * n + sides, k * n + sides])  # the flat side
    faces.append(list(range(n)))
    m._add(role, verts, faces)


def death_knell():
    """A hulking brute on its knuckles with a great black bell for a head, the bell lying on its side with its mouth
    towards you and split so its lower half is a jaw. Its rim is a ring of teeth. Two small eyes glare from under iron
    brows, and from the dark inside swings the clapper, a tongue on a chain, with a red eye on the end of it."""
    rng = random.Random(1505)
    m = monster("dino_DeathKnell", Body="#9b978e", Accent="#4d4b4a", Belly="#c7c2b5", Claw="#1f1f23", Bell="#1d1d21", BellRim="#77777c", Rope="#6e6a63", Yoke="#35322f")
    m.joint("Spine", (0, -0.6, 5.6))
    for bone, x, y, top_, w_ in (("BackL", -1.7, -2.5, 4.6, 1.6), ("BackR", 1.7, -2.5, 4.6, 1.6)):
        clawed_leg(m, bone, x, y, top_, w_, rng, reach=0.6)
    for bone, side in (("FrontL", -1), ("FrontR", 1)):  # arms like trunks, on the knuckles
        x = side * 3.1
        m.use(bone, (side * 2.7, 1.8, 7.6))
        m.loft_z("Body", (4.3, x + side * 0.4, 2.0, 2.0, 2.2), (8.3, side * 2.8, 1.7, 2.6, 2.7))
        m.loft_z("Belly", (0.9, x + side * 0.5, 2.4, 2.6, 2.7), (4.5, x + side * 0.4, 2.0, 1.9, 2.0))
        m.loft_z("Accent", (0, x + side * 0.5, 2.6, 2.3, 2.3), (1.0, x + side * 0.5, 2.45, 2.8, 2.9))
        for k in (-1, 0, 1):
            cx = x + side * 0.5 + k * 0.82
            thorn(m, "Claw", (cx, 3.5, 0.7), (cx, 4.7, 0.04), 0.52, (0, 0, 0.3))
        for z in (5.0, 5.7, 6.4):  # rope bound round it
            m.loft_z("Rope", (z, x + side * 0.15, 1.95, 2.42, 2.54), (z + 0.32, x + side * 0.1, 1.9, 2.52, 2.62))
        chain(m, 2 if side < 0 else 3, wander((x + side * 1.2, 2.0, 4.9), (x + side * 2.2, 1.0, 1.1), rng, 7, (side * 0.3, 0, 0), 0.14), 0.3, bone)
        m.bone = "Spine"
    body = ((-3.4, 0, 5.3, 3.2, 3.1), (2.2, 0, 7.4, 5.0, 4.9))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-2.6, 0, 3.9, 2.4, 0.3), (2.0, 0, 5.1, 3.6, 0.4))
    m.loft_z("Belly", (5.0, 0, 2.3, 3.4, 0.14), (9.2, 0, 2.3, 3.6, 0.14))
    bristle(m, "Accent", body, rng, 22, 1.1, 0.4, 0.7)
    ridge(m, "Accent", along((0, -3.2, top_of(body, -3.2)), (0, 1.8, top_of(body, 1.8)), 11), rng, 1.5, 0.56, 0.6)
    for k in range(3):  # rope over its shoulders
        y = -0.8 + k * 1.1
        limb(m, "Rope", [(-2.4, y, 6.0 + k * 0.3), (-1.3, y + 0.2, 8.0 + k * 0.2), (1.3, y + 0.2, 8.1 + k * 0.2), (2.4, y, 6.0 + k * 0.3)], 0.26, 0.26, False)
    chain(m, 4, wander((1.6, -2.0, 7.6), (3.8, -4.6, 8.6), rng, 7, (0.4, 0, 0.8), 0.14), 0.3, "Spine")
    m.bone = "Spine"
    pts = [(0, -3.3, 5.3), (0.2, -4.6, 5.5), (-0.2, -5.7, 6.0), (0, -6.5, 6.7)]
    widths = (1.1, 0.8, 0.5, 0.15)
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        m.use(f"Tail{i + 1}", a, f"Tail{i}" if i else "Spine")
        beam(m, "Accent", a, b, widths[i], None, widths[i + 1])
        if i:
            m.stretch("Accent", f"Tail{i}")
    m.bone = "Spine"

    m.use("Neck", (0, 2.0, 7.7))
    limb(m, "Body", [(0, 1.4, 7.4), (0, 2.7, 7.9), (0, 3.3, 7.9)], 3.0, 2.3)
    ridge(m, "Accent", along((0, 1.6, 9.0), (0, 3.2, 9.1), 6), rng, 1.3, 0.5, 0.8)

    # The bell, lying on its side: crown at the back, mouth at the front. Its top half is the head, its bottom the jaw.
    yc, zc = 4.0, 8.1
    m.head_joint(yc, 3.4, zc, 3.2)
    drop = 0.5
    hf = Frame(m, (0, yc, zc), turn(x=0.08, y=-0.06))
    steps = ((-0.9, 1.1), (-0.5, 1.75), (0.7, 2.0), (2.0, 2.25), (3.0, 2.95), (3.5, 3.5))
    half_bell(m, "Bell", hf, steps, 1, 10)
    rim = [hf.at(3.5 * math.cos(math.pi * i / 12), 3.46, 3.5 * math.sin(math.pi * i / 12)) for i in range(13)]
    for a, b in zip(rim, rim[1:]):
        beam(m, "BellRim", a, b, 0.5, 0.5)
    band = [hf.at(2.06 * math.cos(math.pi * i / 10), 1.1, 2.06 * math.sin(math.pi * i / 10)) for i in range(11)]
    for a, b in zip(band, band[1:]):
        beam(m, "BellRim", a, b, 0.24, 0.3)
    # A crack down the bell, and the yoke it hung from.
    crack_pts = [hf.at(1.0, 3.3, 3.1), hf.at(0.72, 2.5, 2.42), hf.at(1.05, 1.7, 2.02), hf.at(0.8, 0.8, 1.98)]
    limb(m, "Socket", crack_pts, 0.18, 0.05, False)
    hf.box("Yoke", 0, -0.75, 1.7, 3.8, 0.8, 0.6)
    for side in (-1, 1):
        thorn(m, "Claw", hf.at(side * 1.9, -0.75, 1.9), hf.at(side * 3.1, -1.6, 3.0), 0.5, (0, 0, 0.2))
    # Teeth round the rim, pointing in.
    for k in range(13):
        a = math.pi * (0.03 + 0.94 * k / 12)
        p = Vector((3.25 * math.cos(a), 3.5, 3.25 * math.sin(a)))
        d = Vector((-math.cos(a), 0.34, -math.sin(a)))
        point(m, "Teeth", hf.at(*p), hf.at(*(p + d * rng.uniform(1.0, 1.7))), 0.5)
    slab(Frame(m, hf.at(0, 0.28, 0), hf.r), "Mouth", 0, 0, 0, 2.2, 0.1, 14)  # the back of the bell, shutting off the neck
    half_bell(m, "Mouth", hf, ((-0.05, 1.5), (2.8, 2.5), (3.44, 3.2)), 1, 8)
    # A slab of forehead over the bell's mouth, the eyes small and burning in it under brows of iron.
    yloft(hf, "Accent", (2.2, 0, 3.0, 3.4, 0.5), (3.95, 0, 3.92, 5.0, 1.5))
    yloft(hf, "Bell", (3.2, 0, 4.42, 3.6, 0.5), (4.0, 0, 4.42, 3.8, 0.4))
    for side in (-1, 1):
        glare(m, hf.at(side * 1.32, 3.96, 3.86), hf.r @ Vector((side * 0.14, 1, -0.12)), 0.78, -side, 0.95, brow="BellRim", spikes=0)
        track(m, hf.at(side * 1.32, 4.02, 3.36), hf.at(side * 1.4, 4.0, 3.2), 0.12)
    # The throat eye, and the clapper: a tongue on a chain, with an eye on the end of it.
    e = Frame(m, hf.at(0, 0.36, 0.1), hf.r)
    slab(e, "EyeGlow", 0, 0, 0.04, 0.86, 0.05, 12)
    slab(e, "Slit", 0, 0, 0.08, 0.74, 0.03, 8, 0.24)
    tip = chain(m, 1, [hf.at(1.0, 0.4, 1.4), hf.at(1.1, 1.3, 1.1), hf.at(0.9, 2.2, 0.7), hf.at(0.6, 3.0, 0.4), hf.at(0.3, 3.6, 0.2), hf.at(0.15, 4.1, -0.2), hf.at(0.1, 4.5, -0.7)], 0.3, "Head")
    ball(m, "Bell", *(tip + Vector((0, 0.1, -0.5))), 0.78, 8, 5)
    c = Frame(m, tuple(tip + Vector((0, 0.1, -0.5))), hf.r)
    slab(c, "EyeGlow", 0, 0, 0.7, 0.42, 0.14, 10)
    slab(c, "Slit", 0, 0, 0.78, 0.36, 0.05, 8, 0.24)
    m.bone = "Head"
    weeping(m, [hf.at(-1.32, 4.1, 3.2), hf.at(1.32, 4.1, 3.2)], 6.0, "Head", "Drip", 0.14)

    m.use("Jaw", hf.at(0, -0.4, 0), "Head")
    lf = Frame(m, hf.at(0, -0.4, 0), hf.r @ turn(x=-drop))
    steps_low = tuple((y + 0.4, r) for y, r in steps)
    half_bell(m, "Bell", lf, steps_low, -1, 10)
    half_bell(m, "Mouth", lf, ((0.35, 1.5), (3.2, 2.5), (3.84, 3.2)), -1, 8)
    rim = [lf.at(3.5 * math.cos(math.pi * i / 12), 3.86, -3.5 * math.sin(math.pi * i / 12)) for i in range(13)]
    for a, b in zip(rim, rim[1:]):
        beam(m, "BellRim", a, b, 0.5, 0.5)
    for k in range(13):
        a = math.pi * (0.03 + 0.94 * k / 12)
        p = Vector((3.25 * math.cos(a), 3.9, -3.25 * math.sin(a)))
        d = Vector((-math.cos(a), 0.34, math.sin(a)))
        point(m, "Teeth", lf.at(*p), lf.at(*(p + d * rng.uniform(1.0, 1.7))), 0.5)
    m.bone = "Spine"
    m.head_centre = tuple(hf.at(0, 3.0, 0.6))
    return m


def endless_grief():
    """The boss, and what's behind the Last Door. A colossal hooded thing crawling on its knuckles, its face the eye
    from the door: pale, with a red iris and a black slit, looking out over a mouth too wide for anything. Its huge pale
    hands claw at its own face, and pull away when it roars. The door's shackles are on its wrists, its chains
    still lashing, and out of its back reach the arms of everyone it ever took, thrashing, trying to get out."""
    rng = random.Random(1506)
    m = monster("dino_EndlessGrief", Body="#26262c", Accent="#0f0f13", Belly="#d6d2c8", Claw="#f2eee3", Hood="#1a1a1f", HoodDark="#050507", Sclera="#c9c5ba", Shackle=IRON, ShackleDark=IRON_DARK)
    m.joint("Spine", (0, -1.2, 7.4))
    for bone, x, y, top_, w_ in (("BackL", -2.3, -3.9, 6.2, 2.0), ("BackR", 2.3, -3.9, 6.2, 2.0)):
        clawed_leg(m, bone, x, y, top_, w_, rng, low="Accent", toe="Claw", reach=0.7)
    for bone, side in (("FrontL", -1), ("FrontR", 1)):  # long arms up and over, on the knuckles
        shoulder = (side * 3.0, 2.4, 9.6)
        elbow = (side * 6.0, 2.2, 10.6)
        wrist = (side * 5.2, 3.6, 2.5)
        m.use(bone, shoulder)
        limb(m, "Body", [shoulder, elbow], 2.6, 1.9)
        limb(m, "Belly", [elbow, (side * 5.6, 3.0, 5.6), wrist], 1.7, 1.15)
        ball(m, "Accent", *elbow, 1.4, 8, 5)
        hand(m, "Belly", wrist, (side * -0.1, 1, -0.2), (0, 0.2, 1), size=2.6, spread=0.85, curl=0.12, long=1.2, thumb=-side)
        # The shackle from the door, and its chain.
        sh = Vector(wrist) + Vector((side * 0.05, -0.1, 1.5))
        for z, r in ((0.0, 1.14), (0.42, 1.1)):
            prism(m, "Shackle", sh.x, sh.y, sh.z + z, sh.z + z + 0.34, r, r, 10, 0.3, lean=(0, -0.05))
        chain(m, 5 if side < 0 else 6, wander(tuple(sh + Vector((side * 1.0, -0.2, 0.2))), tuple(sh + Vector((side * 3.2, -2.4, -1.3))), rng, 7, (side * 0.3, 0, 0.5), 0.14), 0.42, bone)
        m.bone = "Spine"
    body = ((-5.0, 0, 7.0, 4.2, 4.0), (3.0, 0, 9.0, 6.6, 6.6))
    m.loft_y("Body", *body)
    prism(m, "Accent", 0, -1, 4.6, 8.0, 3.7, 3.4, 8, 0.3)
    for k in range(14):  # its robe, hanging in rags
        a = k * math.tau / 14
        p = Vector((math.cos(a) * 3.4, -1 + math.sin(a) * 3.9, 5.5))
        q = Vector((math.cos(a) * 4.2, -1 + math.sin(a) * 4.7, rng.uniform(1.8, 3.8)))
        plate(m, "Body" if k % 2 else "Accent", tuple(p), tuple(q), (-math.sin(a), math.cos(a), 0), 2.1, 0.24, 0.14)
    # The arms of everyone it took, thrashing out of its back, each ending in a hand.
    for n, (a, b, bow, w0) in enumerate((((-1.6, -2.4, 10.2), (-4.4, -4.6, 15.2), (-0.8, 0, 0.4), 0.72), ((1.5, -2.8, 10.2), (4.6, -4.2, 14.6), (0.9, 0, 0.5), 0.72),
                                         ((-0.4, -0.6, 11.4), (-1.8, -2.4, 16.6), (-0.3, 0.2, 0.3), 0.66), ((0.6, -0.4, 11.5), (2.2, -1.6, 16.2), (0.4, 0.2, 0.3), 0.66)), 1):
        tip = lash(m, n, wander(a, b, rng, 7, bow, 0.2), w0, 0.42, "Spine", "Belly")
        back = tip - Vector(wander(a, b, random.Random(n), 7, bow, 0.0)[-2])
        hand(m, "Belly", tuple(tip), tuple(back), (rng.uniform(-1, 1), 1, 0.2), size=1.25, spread=1.1, curl=0.32, long=1.4, thumb=1 if a[0] > 0 else -1)
        m.bone = "Spine"
    m.bone = "Spine"
    pts = [(0, -5.0, 6.6), (0.3, -7.0, 5.6), (-0.3, -9.0, 4.2), (0.2, -10.8, 2.8)]
    widths = (3.4, 2.8, 2.0, 0.8)
    for i, (a, b) in enumerate(zip(pts, pts[1:])):  # its robe's train, dragging
        m.use(f"Tail{i + 1}", a, f"Tail{i}" if i else "Spine")
        plate(m, "Accent", a, b, (1, 0, 0.2), widths[i], widths[i + 1], 0.3)
        if i:
            m.stretch("Accent", f"Tail{i}")
    m.bone = "Spine"

    m.use("Neck", (0, 3.0, 10.2))
    limb(m, "Body", [(0, 2.4, 10.0), (0, 3.8, 10.9), (0, 5.0, 11.0)], 4.6, 3.6)

    # The head: a vast hood, and in it a pale face with one eye.
    yc, zc = 6.4, 11.1
    d, h = 4.0, 4.2
    m.head_joint(yc, d, zc, h)
    hf = Frame(m, (0, yc, zc), turn(x=-0.1))
    ball(m, "Hood", *hf.at(0, -1.1, 0.5), 3.5, 10, 6)
    beam(m, "Hood", hf.at(0, -2.2, 2.6), hf.at(0, -5.6, 6.0), 3.4, None, 0.2)
    ball(m, "HoodDark", *hf.at(0, 0.4, 0.2), 2.9, 10, 5)
    # The hood's edge, ragged, hanging round the face.
    for k in range(9):
        a = math.pi * (-0.1 + 1.2 * k / 8)
        p = hf.at(math.cos(a) * 3.1, 1.6, 0.6 + math.sin(a) * 3.1)
        q = hf.at(math.cos(a) * 3.3, 2.6, 0.6 + math.sin(a) * 3.3 - rng.uniform(0.3, 1.1))
        blade(m, "Hood", p, q, (-math.sin(a), 0, math.cos(a)), 1.6, 0.3)
    fy = 3.0  # the face's front
    # The eye: the door's. A pale eye, its red iris and slit, under heavy lids.
    ec = hf.at(0, fy, 1.0)
    e = Frame(m, ec, hf.r)
    slab(e, "Socket", 0, 0, -0.04, 2.3, 0.1, 16, 1.25)
    slab(e, "Sclera", 0, 0, 0.04, 1.86, 0.1, 16, 1.32)
    slab(e, "EyeGlow", 0, 0, 0.12, 1.2, 0.08, 14)
    slab(e, "Pupil", 0, 0, 0.18, 1.04, 0.05, 10, 0.24)
    e.box("Highlight", -0.44, 0.21, 0.46, 0.22, 0.03, 0.22)
    outline_lid = ((-3.0, 2.6), (3.0, 2.6), (3.0, 0.9), (1.5, 1.32), (0, 1.08), (-1.5, 1.32), (-3.0, 0.9))
    outline(m, "Accent", e, outline_lid, 0.2, 0.46)
    outline(m, "Accent", e, ((-3.0, -2.2), (3.0, -2.2), (3.0, -1.1), (1.5, -1.42), (0, -1.5), (-1.5, -1.42), (-3.0, -1.1)), 0.2, 0.4)
    for x in (-1.9, 1.9):
        track(m, hf.at(x, fy + 0.5, -0.2), hf.at(x * 1.1, fy + 0.8, -2.2), 0.18)

    mf = Frame(m, hf.at(0, fy - 1.2, -1.15), hf.r)
    rage_maw(m, mf, 4.8, 2.5, 3.6, 0.5, 0.74, rng, gape=0.34, drop=0.56, upper="Belly", lower="Belly", tooth=0.92, per_side=8, tongue=False, lift=0.04, eye=0.7)

    # Its huge hands, clawing at its own face. Each on a Palm bone from the head, so they pull away when it roars.
    for letter, side in (("PalmL", -1), ("PalmR", 1)):
        wrist = hf.at(side * 4.3, fy - 0.9, -1.4)
        m.use(letter, hf.at(side * 4.7, fy - 3.0, -1.6), "Head")
        limb(m, "Belly", [hf.at(side * 4.9, fy - 3.2, -2.4), wrist], 1.3, 1.0)
        # Up the sides of its head, the fingertips digging in over its brow, clear of the eye.
        hand(m, "Belly", wrist, hf.r @ Vector((-side * 0.2, 0.2, 1)), hf.r @ Vector((side * 1, 0.5, 0.05)), size=2.5, spread=0.5, curl=0.26, long=1.45, thumb=side)
    m.bone = "Head"
    weeping(m, [hf.at(-1.9, fy + 0.7, -0.4), hf.at(1.9, fy + 0.7, -0.4), hf.at(-0.9, fy + 0.5, -0.8), hf.at(0.9, fy + 0.5, -0.8)], 5.0, "Head", "DripB", 0.22, 0.8)
    m.bone = "Spine"
    m.head_centre = tuple(hf.at(0, fy, 0.2))
    return grow(m, 0.8)


ALL = [teddy_wrecks, good_boy, casket_case, wailing_widow, death_knell, endless_grief]


def quick_preview(models, out):
    """Stills only, for trying faces: each model whole from the front and from behind, its face and the lineup."""
    import bpy
    scene = kit.setup_scene()
    kit.RENDERS = out
    out.mkdir(parents=True, exist_ok=True)
    animals = bpy.data.collections.new("Animals")
    scene.collection.children.link(animals)
    roots = []
    for i, model in enumerate(models):
        root = model.build(animals)
        root.location = (i * 34, 0, 0)
        roots.append(root)
    light_up(roots, GLOW_ROLES, GLOW)
    ground = bpy.data.meshes.new("Ground")
    ground.from_pydata([(-300, -300, -0.01), (400, -300, -0.01), (400, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground.materials.append(kit.material("Ground", FLOOR, False))
    scene.collection.objects.link(bpy.data.objects.new("Ground", ground))
    set_sky(scene, SKY)
    bpy.context.view_layer.update()
    for model, root in zip(models, roots):
        kit.set_visible(roots, [root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 3)
        kit.shoot(scene, f"{model.name}_full", centre + Vector((0.62, 0.85, 0.32)) * reach * 0.95, centre, (640, 640), 50)
        kit.shoot(scene, f"{model.name}_side", centre + Vector((1.15, 0.02, 0.14)) * reach * 0.95, centre, (640, 640), 50)
        head = root.location + Vector(model.head_centre)
        size = max(3.2, model.head_centre[2] * 0.6)
        kit.shoot(scene, f"{model.name}_front", head + Vector((0, 1, 0.1)) * size * 1.6, head, (640, 640), 50)
    kit.set_visible(roots, roots)
    for model in models:
        print(f"  {model.name}: {sum(len(x) - 2 for _, f in model.parts.values() for x in f)} triangles, {len(model.joints)} bones, "
              f"biggest {max((len(f), r) for r, (_, f) in model.parts.items())}, "
              f"box {[round(min(v[i] for vs, _ in model.parts.values() for v in vs), 1) for i in range(3)]} to "
              f"{[round(max(v[i] for vs, _ in model.parts.values() for v in vs), 1) for i in range(3)]}")


def closeups(models):
    """A close look at each monster raging, one after another: four seconds of its idle round the roar and the lunge,
    in weeping_dark_attacks.mp4. Runs after the .blend is saved, so nothing here reaches the model."""
    import subprocess

    import bpy
    scene = bpy.context.scene
    roots = [bpy.data.objects[model.name] for model in models]
    light_up(roots, GLOW_ROLES, GLOW)
    for obj in bpy.data.objects:
        if obj.name.startswith("Player"):
            obj.hide_render = True
    bpy.data.objects["Sun"].data.energy = 1.2
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
    frames = RENDERS / "attack_frames"
    frames.mkdir(exist_ok=True)
    data = bpy.data.cameras.new("Closeup")
    data.lens = 38
    camera = bpy.data.objects.new("Cam_Closeup", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = 960, 720
    number = 0
    for model, root in zip(models, roots):
        kit.set_visible(roots, [root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        target = centre.lerp(root.location + Vector(model.head_centre), 0.5)
        camera.location = target + Vector((0.5, 1.0, 0.1)).normalized() * (high - low).length * 0.82
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        root.animation_data.action = bpy.data.actions[f"{root.name}_Idle"]
        for frame in range(60, 180, 2):
            scene.frame_set(frame)
            scene.render.filepath = str(frames / f"f{number:04d}.png")
            bpy.ops.render.render(write_still=True)
            number += 1
        root.animation_data.action = None
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "15", "-i", str(frames / "f%04d.png"), "-pix_fmt", "yuv420p", str(RENDERS / "weeping_dark_attacks.mp4")], check=True)
    for frame in frames.glob("*.png"):
        frame.unlink()
    frames.rmdir()


def main():
    builders = ALL
    only = os.environ.get("ONLY")
    if only:
        builders = [b for b in builders if b.__name__ in only.split(",")]
    models = [b() for b in builders]
    if os.environ.get("QUICK"):
        quick_preview(models, Path(os.environ.get("QUICK_OUT", str(RENDERS / "quick"))))
        return
    build_and_render(models, RENDERS, HERE / f"{BLEND}.blend", "weeping_dark_animation_preview.mp4", sky=SKY, ground=FLOOR,
                     glow_roles=GLOW_ROLES, spacing=18, animate_fn=animate, walk_frames=WALK_PREVIEW, glow=GLOW)
    if not only:
        closeups(models)


if __name__ == "__main__":
    main()
