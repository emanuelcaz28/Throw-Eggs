"""Builds Spore Hollow's 8 monsters, the toxic set, animates them and renders them (Blender, background mode).

    Blender -b -P build_spore_hollow_toxic.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_spore_hollow_toxic.py    (stills only)
    ONLY=toad_rage,sporantula QUICK=1 ...                                    (just those)

Saves spore_hollow_toxic.blend and renders to design/world/monsters_spore_hollow_toxic/.

The owner, 2026-11-10: redesign every Spore Hollow monster in Blender so they look different, "aggressive" and "toxic themed",
each with a suitable animation, the two rarest the best looking. This file replaces the six of build_spore_hollow_monsters.py
("the rot": black bodies, pale crusts) and the two of build_spore_hollow_monsters_7_8.py. Names and ids are the same, so
Config/Dinos doesn't change; those two scripts stay only for the helpers other files import from them.

The idea: everything in the hollow is poisonous and wants you to know. Loud warning colours instead of black (acid green,
poison violet, hazard yellow, venom magenta), smooth swollen bodies, and three things they all share:

  Toxin sacs    glowing blisters swollen out of the hide in a dark collar, in clusters, biggest where the venom is made
  The glare     a glowing slit eye sunk in a black pit under a hard ridge; the throat glows too, so an open mouth lights up
  Venom         glowing strings of it hanging off the longest teeth

Each has its own attack, picked from what DinoLifeController already plays. In the game the attack comes once every 10 seconds and the
monster roams like any other in between (owner, 2026-11-10: DinoLife.attackCycle); the preview videos here play it nonstop. Nothing comes
out of them: the owner had the falling venom drops and the rising spore clouds taken off (2026-11-10, "blocky dots"), so the Vent and
Drip bones the game needs carry only small hidden pieces.

  Toad Rage       a squat poison toad, acid green with black blotches and violet glands, three chimneys on its back. It pounces (Vent1-3,
                  POUNCE)
  Morel Panic     a gaunt violet stalker under a tall honeycombed morel whose pits glow. It can't keep still: four venom whips thrash
                  from its back (Lash1-4, THRASH), and it pounces (Vent)
  Antagonist      a hazard-striped soldier ant reared up over a swollen glowing acid sac. It rears and spits six globs of acid
                  (Strike, Spit1-6), side jaws snapping (MandL, MandR)
  Sporantula      a tarantula in warning bands, front legs raised to strike. It lunges, bites and claws (DripB, RAGE)
  Gillotine       a tall pale mantis with two glowing blades. It heaves both over its head and brings them down like its name, toxic
                  sludge bursting off the ground (Shard1-6, the smash)
  Shroomageddon   the boss: a colossal black-violet titan on its knuckles, cracked open on a glowing core, venom whips on its
                  shoulders (Lash, THRASH); it lunges and bites (DripB, RAGE)
  Mouth Breather  nothing but a mouth lit from inside, on four claws, a crown of sacs and barbels round it: leaps skull flung back
                  and lands jaws first (Gulp)
  Spore Loser     the rarest: a venom-violet hopper in acid plates, hooks and feelers, that ricochets left, right and ahead, biting
                  each time it lands (Bounce)

Glowing roles: Glow, Vein, EyeGlow, Spore, Pit (all in shared/Roles.luau already). Skin roles Body, Accent, Belly and Claw take
the colour mutations. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0. No gore: nothing bleeds, the insides are light.
Plain colours, no stud image.
"""
import math
import random
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402  (first: it turns the stud preview off)
import build_forest as kit  # noqa: E402
from build_clockwork_citadel_monsters import fcurves_of  # noqa: E402
from build_clockwork_citadel_monsters_7_8 import limb, talons  # noqa: E402
from build_forest import Model  # noqa: E402
from build_eclipse_temple_monsters import grow  # noqa: E402
from build_spore_hollow_monsters import egg, pounce_of, vent, vent_rise  # noqa: E402
from build_thorn_kingdom_monsters import point, thrash_of  # noqa: E402
from build_volcano import idle_pose as volcano_idle, walk_pose as volcano_walk  # noqa: E402
from build_weeping_dark_monsters import DRIP, rage_of  # noqa: E402
from fierce_kit import band, fierce_head, horn, knob  # noqa: E402
from rare_kit import (WALK_PREVIEW, chain, curve, fine, jointed, leaf, marked_of, on_the_floor, ring_round, sabre, slit_eye, sway, sway_of,  # noqa: E402
                      sweep, sweep_fine)

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_spore_hollow_toxic"
BLEND = "spore_hollow_toxic"  # for check_map.py and export_fbx.py
GLOW_ROLES = {"Glow", "Vein", "EyeGlow", "Spore", "Pit"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket", "Slit"})

ACID, VENOM = "#b4ff2a", "#e04dff"  # the two lights of the set: acid green and venom magenta
FACE = {"Pupil": "#0a0610", "Slit": "#0a0610", "Socket": "#07040c", "Highlight": "#ffffff", "EyeGlow": "#d8ff3a", "Mouth": "#1c0a26", "Tongue": "#6a1f8a",
        "Teeth": "#eef4c0", "Glow": ACID, "Vein": VENOM, "Spore": "#dcff70", "Pit": ACID, "Puff": "#a9cf4a", "PuffB": "#74982c", "Puffskin": "#1a1024"}
SKY, FLOOR = "#17140f", "#4a3c30"


def finish(m, k=1.0):
    """Grows the monster by k, then puts in its Vent bones. The game needs them to turn POUNCE on, but the owner had the spore clouds
    that rose out of them taken off, 2026-11-10 (blocky dots coming out of the monster). Each carries only a small piece hidden in its
    chimney or body, VENT_GAP plus a little below where the clouds began, so the game's steady lift never brings it out."""
    if k != 1.0:
        grow(m, k)
    for n, base, parent, *_ in m.vents:
        b = base * k
        m.use(f"Vent{n}", tuple(b), parent)
        egg(m, "Body", tuple(b - Vector((0, 0, 1.05))), 0.2, 0.2, 0.2, 6, 4)
    m.bone = "Spine"
    return m


def monster(name, **colours):
    m = Model(name, {**FACE, **colours})
    m.vents = []  # asked for while building, made by finish()
    return m


# ---------------------------------------------------------------------- what moves

POSED = {"Swim", "Spine", "Neck", "Head", "Jaw", "ArmL", "ArmR", "LegL", "LegR", "ShinL", "ShinR", "FrontL", "FrontR", "BackL", "BackR", "Tail1", "Tail2", "Tail3",
         "WingL", "WingR", "WingTipL", "WingTipR", "MandL", "MandR"}
LEGS = ("FrontL", "FrontR", "BackL", "BackR", "LegL", "LegR", "ShinL", "ShinR")


def extras(a, f, idle):
    """On top of the walk or idle and rare_kit's markers: the thrashing (Lash), the pounce and its gas (Vent), the rage and its
    venom (Drip), as DinoLifeController stacks them."""
    s = f / 30
    names = {bone.name for bone in a.pose.bones}
    thrashes = any(n.startswith("Lash") for n in names)
    vents = any(n.startswith("Vent") for n in names)
    rages = any(n in DRIP for n in names)
    moved = set(marked_of(a))
    for bone in a.pose.bones:
        name = bone.name
        if name.startswith("Vent"):
            kit.pose_bone(a, name, (0, 0, 0), (0, 0, vent_rise(s)), f)
            continue
        if name in DRIP:
            gap, period = DRIP[name]
            kit.pose_bone(a, name, (0, 0, 0), (0, 0, -gap * ((s / period) % 1)), f)
            continue
        parts = []
        if thrashes and thrash_of(name, s):
            parts.append(thrash_of(name, s))
        if vents and pounce_of(name, s):
            parts.append(pounce_of(name, s))
        rage = rage_of(name, s) if rages else None
        if not parts and not rage:
            continue
        has_pose = name in POSED or name in moved or sway_of(name, s) is not None
        rotation = list(bone.rotation_euler) if has_pose else [0.0, 0.0, 0.0]
        location = list(bone.location) if has_pose else [0.0, 0.0, 0.0]
        for p in parts:
            rotation = [rotation[i] + p[i] for i in range(3)]
        if rage:
            rotation = [rotation[i] + rage[i] for i in range(3)]
            location = [location[0], location[1] + rage[4], location[2] + rage[3]]
        kit.pose_bone(a, name, tuple(rotation), tuple(location), f)


def walk_pose(a, f):
    volcano_walk(a, f)
    for name in ("MandL", "MandR"):
        kit.pose_bone(a, name, (0, 0, 0), None, f)
    sway(a, f, False)
    extras(a, f, False)


def idle_pose(a, f):
    volcano_idle(a, f)
    moved = set(marked_of(a))
    for name in LEGS:  # no idle of their own: what's added goes on the rest pose, not on the last frame
        if name not in moved:
            kit.pose_bone(a, name, (0, 0, 0), None, f)
    sway(a, f, True)
    extras(a, f, True)


def animate(armature):
    walk = kit.add_action(armature, "Walk", WALK_PREVIEW, walk_pose, 2)
    idle = kit.add_action(armature, "Idle", kit.IDLE_FRAMES, idle_pose, 2)
    for action in (walk, idle):  # gas and venom move steadily, not eased between keys
        for fcurve in fcurves_of(action):
            if '"Vent' in fcurve.data_path or any(f'"{name}"' in fcurve.data_path for name in DRIP):
                for key in fcurve.keyframe_points:
                    key.interpolation = "LINEAR"
    return walk, idle


# ---------------------------------------------------------------------- shapes


def unit(v):
    return Vector(v).normalized()


def grounded(m):
    """Nothing reaches under the ground at rest: the game stands a model on its lowest point."""
    for verts, _ in m.parts.values():
        verts[:] = [(x, y, max(z, 0.03)) for x, y, z in verts]


def skin_at(rings, u, angle, out=0.0):
    """A point on a sweep_fine body and the way out of it there. u: 0 to len(rings) - 1 along it; angle round it, 0 to the
    right (+X), pi / 2 on top. For bodies running mostly along +Y."""
    path, _ = fine(rings, None, 6)
    k = u * 6
    i = min(int(k), len(path) - 2)
    t = k - i
    (p0, w0, h0), (p1, w1, h1) = path[i], path[i + 1]
    c = Vector(p0).lerp(Vector(p1), t)
    w, h = w0 + (w1 - w0) * t, h0 + (h1 - h0) * t
    ahead = unit(Vector(p1) - Vector(p0))
    side = unit(ahead.cross(Vector((0, 0, 1))))
    normal = side.cross(ahead)
    off = side * math.cos(angle) * w / 2 + normal * math.sin(angle) * h / 2
    n = unit(side * math.cos(angle) / max(w, 0.01) + normal * math.sin(angle) / max(h, 0.01))
    return c + off + n * out, n


def sac(m, at, normal, r, role="Glow", rim="Accent", sink=0.35, squash=0.9):
    """A toxin sac: a glowing blister swollen out of the hide at `at`, in a dark collar."""
    at, n = Vector(at), unit(normal)
    c = at - n * r * sink
    egg(m, role, tuple(c), r, r, r * squash if abs(n.z) > 0.6 else r, 10, 6)
    if rim:
        ring_round(m, rim, tuple(at + n * r * 0.02), r * 0.98, tuple(n), r * 0.42, 12)


def cluster(m, rings, spots, role="Glow", rim="Accent", bones=None):
    """Sacs over a body: spots are (u, angle, radius), mirrored when the angle isn't straight up."""
    for u, angle, r in spots:
        for a in ((angle,) if abs(angle - math.pi / 2) < 0.02 else (angle, math.pi - angle)):
            at, n = skin_at(rings, u, a)
            if bones:
                m.bone = bones[min(round(u), len(bones) - 1)]
            sac(m, at, n, r, role, rim)


def blotch(m, rings, spots, role="Accent", bones=None, lift=0.16):
    """Flat dark blotches lying on the top of a body: (u, angle, across, along)."""
    for u, angle, rx, ry in spots:
        for a in ((angle,) if abs(angle - math.pi / 2) < 0.02 else (angle, math.pi - angle)):
            at, n = skin_at(rings, u, a)
            if bones:
                m.bone = bones[min(round(u), len(bones) - 1)]
            egg(m, role, tuple(at - n * (0.5 - lift)), rx, ry, 0.5, 10, 4)


def tox_eye(m, at, r, look, side, socket=1.9, lid="Body", pupil="Pupil", top=0.5, tilt=0.9, low=0.36, slit=0.22, sink=0.5, ridge="Accent", ridge_size=1.0,
            proud=0.3, iris="EyeGlow"):
    """The glare: a glowing slit eye sunk in a black pit under a hard ridge driving down to the nose (fierce_kit's eye, lit)."""
    at, look = Vector(at), unit(look)
    egg(m, "Socket", tuple(at - look * r * sink), r * socket, r * (sink + 0.3), r * socket * 0.72, 12, 6)
    slit_eye(m, tuple(at + look * r * proud), r, look, side, iris=iris, lid_role=lid, top=top, tilt=tilt, low=low, slit=slit, pupil=pupil, layer=max(0.04, r * 0.1))
    if ridge:
        c = at + look * r * 0.6 - Vector((0, 0, r * ridge_size * 0.26))
        k = r * ridge_size
        sweep_fine(m, ridge, [(tuple(c + Vector((side * k * 1.9, -k * 1.0, k * 1.3))), k * 0.5, k * 0.4), (tuple(c + Vector((side * k * 0.9, -k * 0.3, k * 1.0))), k * 1.3, k * 1.0),
                              (tuple(c + Vector((-side * k * 0.4, k * 0.4, k * 0.56))), k * 1.1, k * 0.9), (tuple(c + Vector((-side * k * 1.9, k * 1.1, -k * 0.75))), k * 0.24, k * 0.24)], sides=8, per=3)


def venom(m, at, length, w, role="Glow", sway_=0.0):
    """A string of venom hanging from `at`, with a drop on its end."""
    a = Vector(at)
    b = a + Vector((sway_, 0, -length))
    sweep(m, role, [(tuple(a), w, w), (tuple(a.lerp(b, 0.5)), w * 0.5, w * 0.5), (tuple(b + Vector((0, 0, w * 0.9))), w * 0.45, w * 0.45)], sides=5)
    egg(m, role, tuple(b), w * 0.8, w * 0.8, w * 1.1, 6, 4)


def throat_glow(m, y, zm, width, height, role="Glow"):
    """Light at the back of the mouth, behind the teeth: an open mouth shows it."""
    egg(m, role, (0, y, zm - height * 0.06), width * 0.2, width * 0.1, height * 0.2, 10, 5)


def chimney(m, n, at, normal, h, w, parent, size=1.0, count=4, role="Accent", lean=(0, 0, 0.6)):
    """A vent grown out of the hide: a crooked tube with a swollen mouth, gas pouring out of it for ever (Vent<n>; n None: no gas)."""
    at = Vector(at)
    d = unit(unit(normal) + Vector(lean))
    top = at + d * h
    m.bone = parent
    sweep_fine(m, role, [(tuple(at - d * w * 0.4), w * 1.5, w * 1.5), (tuple(at + d * h * 0.35), w * 0.95, w * 0.95), (tuple(at + d * h * 0.75), w * 0.9, w * 0.9),
                         (tuple(top), w * 1.25, w * 1.25)], sides=10, per=2, up=(0, 1, 0))
    ring_round(m, "Glow", tuple(top - d * 0.02), w * 0.52, (0, 0, 1), w * 0.24, 10)
    if n is None:
        egg(m, "Glow", tuple(top), w * 0.44, w * 0.44, w * 0.36, 8, 4)
    else:
        vent(m, n, tuple(top + Vector((0, 0, 0.04))), parent, size, count, None)


def whip(m, n, points, w0, w1=0.12, parent="Spine", role="Accent", tip="Glow", tip_size=None, count=10):
    """A venom whip on Lash<n>a, b and c, which never stop thrashing: a smooth tube with a glowing bulb on its end."""
    pts = curve(points, count)
    names = chain(m, "Lash", n, pts, w0, w1, parent=parent, role=role, sides=8)
    if tip:
        r = tip_size or w0 * 0.7
        egg(m, tip, tuple(pts[-1]), r, r, r, 8, 5)
        point(m, "Claw", tuple(pts[-1]), tuple(Vector(pts[-1]) + unit(Vector(pts[-1]) - Vector(pts[-2])) * r * 2.6), r * 0.9)
    return names


def leg(m, bone, parent, pts, widths, role="Body", toes=3, toe=(1.0, 2.2, 0.8), ahead=(0, 1, -0.25), pad=None, shoulder=0.62, spur=None):
    """A leg or an arm on one bone, through pts (the first is its joint), ending in claws."""
    pts = [Vector(p) for p in pts]
    m.use(bone, tuple(pts[0]), parent)
    if shoulder:
        knob(m, role, pts[0], widths[0] * shoulder)
    limb(m, role, pts, widths, sides=12)
    foot = pts[-1]
    if pad:
        egg(m, role, tuple(foot + Vector((0, pad * 0.3, 0))), pad, pad * 1.1, pad * 0.45, 10, 5)
    if toes:
        talons(m, foot + unit(ahead) * toe[1] * 0.3, ahead, toes, toe[0], toe[1], toe[2])
    if spur:
        k, length, w = spur
        p = pts[k]
        side = 1 if p.x > 0 else -1
        point(m, "Claw", tuple(p), tuple(p + Vector((side * length * 0.6, -length * 0.6, length * 0.6))), w)


def stripes(m, rings, us, role="Accent", bones=None, grow=1.03, length=0.9):
    """Warning bands round a body at each u."""
    path, _ = fine(rings, None, 6)
    for u in us:
        i = min(round(u * 6), len(path) - 1)
        p, w, h = path[i]
        ahead = unit(Vector(path[min(i + 1, len(path) - 1)][0]) - Vector(path[max(i - 1, 0)][0]))
        band(m, role, p, w * grow, h * grow, length=length, bone=bones[min(round(u), len(bones) - 1)] if bones else None, tilt=tuple(ahead))


# ---------------------------------------------------------------------- Toad Rage


def toad_rage():
    """A squat poison toad, its head nearly all mouth, glands swollen behind its eyes and three chimneys of gas on its back."""
    m = monster("dino_ToadRage", Body="#86cf1c", Accent="#1b1230", Belly="#e6e88c", Claw="#2d1446")
    m.joint("Spine", (0, -5.0, 6.0))
    m.joint("Neck", (0, 1.6, 6.6), "Spine")
    m.joint("Head", (0, 3.0, 6.6), "Neck")
    rings = [((0, -11.4, 4.6), 3.0, 2.6), ((0, -9.6, 5.4), 10.4, 7.2), ((0, -6.0, 6.8), 15.6, 10.8), ((0, -2.0, 7.4), 16.4, 11.4), ((0, 1.4, 7.0), 15.2, 9.0), ((0, 4.2, 6.9), 14.2, 6.0)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Neck", "Head"]
    sweep_fine(m, "Body", rings, bones, sides=22, under="Belly", under_faces=7, per=4)
    blotch(m, rings, [(1.5, math.pi / 2, 2.6, 1.6), (2.0, 1.0, 2.0, 2.6), (2.9, 0.75, 1.7, 2.2), (3.4, math.pi / 2, 2.2, 1.3), (1.3, 0.6, 1.5, 1.9), (2.5, 0.3, 1.4, 2.4), (3.6, 0.35, 1.2, 1.6)], bones=bones)
    cluster(m, rings, [(3.75, 0.95, 1.9), (3.2, 1.2, 1.0), (2.45, 0.66, 0.9), (1.75, 0.95, 1.1), (1.2, 1.25, 0.8), (2.2, 0.2, 0.8)], role="Vein", bones=bones)  # the glands: violet
    for n, (u, a, h, w) in enumerate(((2.6, math.pi / 2, 3.2, 1.9), (1.7, 1.15, 2.4, 1.5), (1.9, math.pi - 1.3, 2.0, 1.3)), start=1):
        at, normal = skin_at(rings, u, a)
        chimney(m, n, at, normal, h, w, "Spine", 1.5 - 0.15 * n, count=4)
    m.bone = "Spine"
    for letter, side in (("L", -1), ("R", 1)):
        leg(m, f"Front{letter}", "Spine", [(side * 6.2, 1.6, 5.2), (side * 9.6, 2.2, 5.6), (side * 11.4, 2.6, 4.2), (side * 10.8, 4.4, 2.0), (side * 10.2, 5.6, 0.8)], (5.2, 4.6, 3.6, 2.8, 2.4),
            toes=4, toe=(1.0, 2.6, 0.8), pad=2.0, spur=(2, 2.6, 1.5))
        leg(m, f"Back{letter}", "Spine", [(side * 6.0, -7.0, 5.4), (side * 10.0, -5.0, 7.4), (side * 12.6, -3.2, 6.8), (side * 12.4, -6.4, 3.4), (side * 11.6, -8.6, 1.6), (side * 12.2, -6.0, 0.8)],
            (6.6, 6.4, 5.0, 3.6, 2.8, 2.6), toes=4, toe=(1.1, 2.8, 0.85), pad=2.4, spur=(2, 3.0, 1.7))
        stripe_at = Vector((side * 11.0, 2.5, 4.6))
        band(m, "Accent", tuple(stripe_at), 4.7, 4.7, length=0.9, bone=f"Front{letter}", tilt=(side * 0.5, 0.2, -0.8))
    m.bone = "Spine"
    for u, tall in ((0.9, 1.6), (1.35, 2.2), (2.25, 2.0), (3.1, 2.4), (3.55, 1.8)):  # hooks down its back
        at, _ = skin_at(rings, u, math.pi / 2)
        horn(m, "Claw", tuple(at - Vector((0, 0, 0.4))), tuple(at + Vector((0, -tall * 0.7, tall))), 1.3)
    m.bone = "Head"
    skull = [(0, 0.92, 0.0, 0.74), (0.25, 1.0, 0.0, 0.86), (0.52, 0.97, 0.0, 0.66), (0.78, 0.84, 0.0, 0.44), (0.94, 0.6, 0.0, 0.28), (1.0, 0.32, 0.03, 0.15)]
    jaw = [(0, 0.92, -0.62, 0.0), (0.3, 1.0, -0.7, 0.0), (0.6, 0.95, -0.58, 0.0), (0.85, 0.78, -0.42, 0.0), (0.97, 0.52, -0.3, 0.0), (1.0, 0.28, -0.2, -0.02)]
    y, zm, length, width, height = 2.6, 6.2, 10.0, 15.6, 6.4
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.4, lower="Belly", teeth=(15, 13), tall=1.25, base=0.52, fangs=((0.84, 1.9), (0.5, 1.4)), rows=2, seed=7,
                     t0=0.3, throat=1.1, tongue_long=0.86)
    throat_glow(m, y + length * 0.16, zm, width, height)
    for side in (-1, 1):
        spot = at(0.4, 1.0 if side > 0 else math.pi - 1.0)
        egg(m, "Body", tuple(spot + Vector((0, -0.6, -0.3))), 2.6, 2.8, 2.0, 12, 6)  # eyes up on bumps
        tox_eye(m, spot + Vector((side * 0.1, 1.3, 0.7)), 0.95, (side * 0.26, 0.95, -0.12), side, socket=1.8, ridge_size=1.5)
        for t, a_, r in ((0.2, 0.55, 0.8), (0.62, 0.7, 0.6), (0.78, 1.05, 0.5)):  # warts along the lip
            sac(m, at(t, a_ if side > 0 else math.pi - a_), (side * 0.5, 0.2, 0.8), r, "Vein")
        egg(m, "Socket", tuple(at(0.93, 1.2 if side > 0 else math.pi - 1.2)), 0.5, 0.4, 0.2, 8, 4)  # nostrils
        venom(m, (side * width * 0.3, y + length * 0.78, zm - 0.6), 2.6, 0.34)
    m.head_centre = (0, 12.0, 6.0)
    grounded(m)
    return finish(m, 0.42)


# ---------------------------------------------------------------------- Morel Panic


def morel(m, base, tip, r, rng, rows=6, role="Cap", pits="Pit", bone="Head"):
    """A tall honeycombed morel from base to tip: a swollen cone, every pit glowing in a dark collar."""
    b, t = Vector(base), Vector(tip)
    axis = t - b
    d = unit(axis)
    u = unit(d.cross(Vector((1, 0, 0))))
    v = d.cross(u)
    profile = [(0.0, 0.62), (0.12, 0.95), (0.3, 1.0), (0.55, 0.84), (0.78, 0.56), (0.93, 0.3), (1.0, 0.08)]
    m.bone = bone
    sweep_fine(m, role, [(tuple(b + axis * s), 2 * r * k, 2 * r * k) for s, k in profile], sides=16, per=3, up=tuple(u))

    def radius(s):
        for (s0, k0), (s1, k1) in zip(profile, profile[1:]):
            if s <= s1:
                return r * (k0 + (k1 - k0) * (s - s0) / (s1 - s0))
        return r * profile[-1][1]

    for row in range(rows):
        s = 0.1 + 0.76 * row / (rows - 1)
        count = max(4, round(9 * radius(s) / r))
        for k in range(count):
            a = (k + 0.5 * (row % 2) + rng.uniform(-0.12, 0.12)) * math.tau / count
            out = unit(math.cos(a) * u + math.sin(a) * v)
            at = b + axis * s + out * radius(s) * 0.97
            size = radius(s) * math.tau / count * rng.uniform(0.3, 0.4)
            egg(m, pits, tuple(at - out * size * 0.5), size, size, size * 1.25, 8, 4)
            ring_round(m, "CapDark", tuple(at + out * size * 0.2), size * 1.02, tuple(out), size * 0.5, 8, squash=1.25)


def morel_panic():
    """Gaunt, hunched, all elbows and knees, its head lost under a morel taller than its body."""
    m = monster("dino_MorelPanic", Body="#5a2a94", Accent="#170d26", Belly="#b05ad6", Claw="#d8f06a", Cap="#2a1640", CapDark="#120a1e")
    rng = random.Random(142)
    m.joint("Spine", (0, -2.0, 11.0))
    m.joint("Neck", (0, 3.6, 15.4), "Spine")
    m.joint("Head", (0, 5.2, 16.0), "Neck")
    rings = [((0, -4.0, 9.2), 3.6, 3.2), ((0, -3.0, 10.4), 6.2, 5.0), ((0, -1.4, 12.2), 5.0, 4.4), ((0, 0.6, 14.0), 7.4, 5.6), ((0, 2.6, 15.4), 8.4, 5.6), ((0, 4.6, 16.0), 5.0, 4.4)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Spine", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=16, under="Belly", under_faces=5, per=4)
    stripes(m, rings, (1.6, 2.1, 2.6, 3.1), "Accent", bones, grow=1.04, length=0.5)  # ribs
    cluster(m, rings, [(3.6, 0.9, 1.0), (4.1, 1.15, 0.8), (3.0, 1.2, 0.7), (2.3, math.pi / 2, 0.8), (1.2, 1.0, 0.7)], bones=bones)
    for k, u in enumerate((1.3, 2.0, 2.8, 3.5, 4.2)):  # spines
        at, n = skin_at(rings, u, math.pi / 2)
        horn(m, "Claw", tuple(at - n * 0.3), tuple(at + n * (2.6 - 0.2 * k) + Vector((0, -1.2, 0.6))), 1.0)
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee, ankle, foot = Vector((side * 2.6, -3.0, 10.0)), Vector((side * 5.6, 0.6, 6.6)), Vector((side * 5.0, -3.2, 2.6)), Vector((side * 5.2, -1.4, 0.7))
        m.use(f"Leg{letter}", tuple(hip))
        knob(m, "Body", hip, 2.2)
        limb(m, "Body", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.4, 0.3, 0.3)), knee], (3.6, 3.0, 2.0), sides=12)
        point(m, "Claw", tuple(knee), tuple(knee + Vector((side * 0.8, 2.0, 1.4))), 1.3)
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        knob(m, "Accent", knee, 1.25)
        limb(m, "Accent", [knee, knee.lerp(ankle, 0.5) + Vector((0, -0.4, 0)), ankle, foot, foot + Vector((0, 2.2, -0.1))], (1.9, 1.5, 1.2, 1.3, 1.7), sides=10)
        talons(m, foot + Vector((0, 2.4, 0)), (0, 1, -0.15), 3, 0.8, 2.4, 0.7)
        shoulder, elbow, wrist = Vector((side * 4.2, 2.4, 15.2)), Vector((side * 8.6, -0.6, 11.0)), Vector((side * 7.4, 6.4, 6.0))
        m.use(f"Arm{letter}", tuple(shoulder))
        knob(m, "Body", shoulder, 1.9)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5) + Vector((side * 0.5, -0.4, 0.4)), elbow, elbow.lerp(wrist, 0.5) + Vector((side * 0.6, 0, -0.6)), wrist], (3.0, 2.4, 1.8, 1.5, 1.7), sides=10)
        point(m, "Claw", tuple(elbow), tuple(elbow + Vector((side * 1.2, -2.6, 1.6))), 1.3)
        sac(m, shoulder + Vector((side * 0.9, -0.2, 1.3)), (side * 0.5, -0.1, 0.9), 1.0)
        for k in range(4):  # long fingers, hooked
            o = Vector((side * (k - 1.5) * 0.62, 0, 0))
            sabre(m, "Claw", [tuple(wrist + o), tuple(wrist + o * 1.5 + Vector((0, 2.2, -0.6))), tuple(wrist + o * 1.9 + Vector((0, 3.6, -2.6))), tuple(wrist + o * 1.9 + Vector((0, 3.2, -4.6)))], 0.72, 8)
    m.bone = "Spine"
    for n, (side, x, z, up) in enumerate(((-1, 2.8, 14.6, 5.0), (1, 2.8, 14.6, 5.0), (-1, 1.6, 12.4, 1.5), (1, 1.6, 12.4, 1.5)), start=1):  # venom whips out of its back
        root = Vector((side * x, -0.4 if up > 2 else -2.4, z))
        whip(m, n, [root, root + Vector((side * 3.0, -3.0, up * 0.6)), root + Vector((side * 6.6, -4.0, up)), root + Vector((side * 9.6, -1.4, up * 0.7 - 1.0)), root + Vector((side * 11.4, 2.2, up * 0.3 - 1.6))],
             1.3, 0.3, role="Accent", tip_size=0.75)
    m.bone = "Head"
    skull = [(0, 0.8, 0.0, 0.9), (0.24, 1.0, 0.0, 1.0), (0.5, 0.86, 0.0, 0.8), (0.74, 0.62, 0.0, 0.56), (0.92, 0.4, 0.0, 0.36), (1.0, 0.2, 0.04, 0.2)]
    jaw = [(0, 0.8, -0.56, 0.0), (0.32, 0.9, -0.6, 0.0), (0.64, 0.7, -0.46, 0.0), (0.9, 0.42, -0.32, 0.0), (1.0, 0.2, -0.2, -0.02)]
    y, zm, length, width, height = 4.6, 14.4, 8.4, 7.6, 4.0
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.72, lower="Belly", teeth=(10, 9), tall=1.15, base=0.36, fangs=((0.86, 2.2),), low_fangs=((0.7, 1.7),), seed=9, t0=0.3, jaw_length=1.04)
    throat_glow(m, y + length * 0.18, zm, width, height)
    for side in (-1, 1):
        tox_eye(m, at(0.6, 0.8 if side > 0 else math.pi - 0.8), 0.6, (side * 0.3, 0.94, -0.1), side, socket=1.8, ridge_size=1.2)
        venom(m, (side * width * 0.2, y + length * 0.84, zm - 0.5), 2.2, 0.26)
    morel(m, (0, 5.6, 17.4), (0, 1.0, 29.0), 4.4, rng)
    vent(m, 1, (0, 0.9, 29.3), "Head", 1.5, 4, None)
    m.bone = "Spine"
    for n, side in ((2, -1), (3, 1)):
        at_, normal = skin_at(rings, 3.9, 0.7 if side > 0 else math.pi - 0.7)
        chimney(m, n, at_, normal, 2.0, 1.2, "Spine", 1.0, count=3)
    m.head_centre = (0, 12.0, 16.0)
    grounded(m)
    return finish(m, 0.42)


# ---------------------------------------------------------------------- Antagonist


def banded(m, rings, roles=("Body", "Accent"), bones=None, per=6, chunk=3, swell=(1.0, 1.06), sides=14):
    """A body in warning bands: the sweep_fine tube through rings, cut into rings of colour, every other one a little proud."""
    path, ring_bones = fine(rings, bones, per)
    i = k = 0
    while i < len(path) - 1:
        j = min(i + chunk, len(path) - 1)
        s = swell[k % len(swell)]
        sweep(m, roles[k % len(roles)], [(p, w * s, h * s) for p, w, h in path[i:j + 1]], ring_bones[i:j + 1] if ring_bones else None, sides=sides)
        i, k = j, k + 1


def side_jaw(m, side, pivot, points, w, parent="Head", role="Claw", root="Body", flat=0.7, teeth=0):
    """A side jaw on MandL or MandR, hinged at pivot: a great curved hook. They gnash, and fling open in the roar."""
    m.use(f"Mand{'L' if side < 0 else 'R'}", tuple(pivot), parent)
    knob(m, root, Vector(pivot), w * 0.8)
    pts = [Vector(p) for p in points]
    sabre(m, role, [tuple(p) for p in pts], w, 10, flat=flat)
    path = curve(pts, 12)
    for k in range(teeth):  # along its inner edge
        p = Vector(path[3 + k * (7 // max(teeth, 1))])
        point(m, role, tuple(p), tuple(p + Vector((-side * w * 1.3, w * 0.3, 0))), w * 0.5)
    m.bone = parent


def acid(m, n, at, size, parent="Head"):
    """One Spit bone's glob of acid, a teardrop trailing back along Y, parked out of sight at `at` until it's spat."""
    m.use(f"Spit{n}", at, parent)
    x, y, z = at
    sweep(m, "Glow", [((x, y - size * 1.5, z), 0.06, 0.06), ((x, y - size * 0.7, z), size * 0.9, size * 0.9), ((x, y, z), size * 1.4, size * 1.4), ((x, y + size * 0.55, z), size, size),
                      ((x, y + size * 0.8, z), 0.1, 0.1)], sides=6)


def antagonist():
    """A soldier ant reared up to spit, its abdomen a tank of acid glowing between black bands."""
    m = monster("dino_Antagonist", Body="#1a1524", Accent="#f4d01c", Belly="#7d3cc4", Claw="#f1f58a")
    m.joint("Spine", (0, -3.0, 7.4))
    m.joint("Strike", (0, 0.0, 8.8), "Spine")
    m.joint("Neck", (0, 3.4, 11.8), "Strike")
    m.joint("Head", (0, 4.6, 12.4), "Neck")
    gaster = [((0, -4.6, 7.2), 2.4, 2.4), ((0, -6.6, 7.8), 8.4, 7.8), ((0, -10.4, 8.6), 11.6, 10.6), ((0, -14.4, 8.0), 10.2, 9.2), ((0, -17.4, 6.6), 5.4, 5.0), ((0, -19.0, 5.6), 1.6, 1.6)]
    banded(m, gaster, ("Body", "Glow"), chunk=3, swell=(1.05, 1.0), sides=18)
    m.use("Sting", (0, -18.6, 5.8), "Spine")
    horn(m, "Claw", (0, -18.2, 5.9), (0, -23.0, 2.6), 1.7, droop=-1.0)
    egg(m, "Glow", (0, -23.0, 2.5), 0.5, 0.5, 0.7, 8, 4)
    m.bone = "Spine"
    thorax = [((0, -5.2, 7.2), 2.8, 2.8), ((0, -3.4, 7.6), 6.0, 5.6), ((0, -1.0, 8.4), 7.0, 6.4), ((0, 1.4, 10.0), 6.0, 5.6), ((0, 3.2, 11.6), 4.4, 4.2), ((0, 4.8, 12.4), 3.8, 3.8)]
    bones = ["Spine", "Spine", "Spine", "Strike", "Neck", "Neck"]
    sweep_fine(m, "Body", thorax, bones, sides=16, under="Belly", under_faces=5, per=4)
    stripes(m, thorax, (1.5, 2.6), "Accent", bones, grow=1.05, length=1.1)
    cluster(m, thorax, [(2.0, 0.5, 0.9), (3.2, 0.6, 0.7)], bones=bones)
    for k, u in enumerate((1.1, 2.1, 3.0, 3.8)):
        at, n = skin_at(thorax, u, math.pi / 2)
        m.bone = bones[round(u)]
        horn(m, "Accent", tuple(at - n * 0.3), tuple(at + n * 2.4 + Vector((0, -1.4, 0.4))), 1.1)
    for letter, side in (("L", -1), ("R", 1)):
        for name, hip, knee, foot in ((f"Front{letter}", (side * 2.8, -0.6, 8.2), (side * 9.4, 2.0, 12.6), (side * 12.4, 3.6, 0.5)),
                                      (f"Back{letter}", (side * 2.8, -3.4, 7.6), (side * 10.0, -6.6, 12.2), (side * 13.4, -10.4, 0.5))):
            hip, knee, foot = Vector(hip), Vector(knee), Vector(foot)
            leg(m, name, "Spine", [hip, hip.lerp(knee, 0.5) + Vector((0, 0, 0.6)), knee, knee.lerp(foot, 0.5) + Vector((side * 0.8, 0, 0)), foot], (2.4, 1.9, 1.5, 1.1, 0.7),
                toes=2, toe=(0.7, 1.6, 0.6), shoulder=0.7)
            knob(m, "Accent", knee, 1.25)
            point(m, "Claw", tuple(knee), tuple(knee + Vector((side * 1.0, -0.6, 2.4))), 1.1)
        shoulder, elbow, wrist = Vector((side * 2.6, 2.0, 10.6)), Vector((side * 7.0, 4.6, 15.2)), Vector((side * 5.4, 9.4, 13.0))
        leg(m, f"Arm{letter}", "Strike", [shoulder, shoulder.lerp(elbow, 0.5), elbow, elbow.lerp(wrist, 0.5) + Vector((0, 0.4, 0.6)), wrist], (2.2, 1.8, 1.4, 1.2, 1.0), toes=0, shoulder=0.7)
        knob(m, "Accent", elbow, 1.15)
        for o in (-0.5, 0.5):  # two hooks
            sabre(m, "Claw", [tuple(wrist + Vector((o, 0, 0))), tuple(wrist + Vector((o * 1.6, 2.4, -0.4))), tuple(wrist + Vector((o * 1.8, 3.2, -3.2)))], 0.9, 8)
    m.bone = "Head"
    skull = [(0, 0.86, 0.0, 0.9), (0.2, 1.0, 0.0, 1.04), (0.46, 0.94, 0.0, 0.94), (0.72, 0.7, 0.0, 0.66), (0.92, 0.46, 0.0, 0.4), (1.0, 0.24, 0.04, 0.22)]
    jaw = [(0, 0.8, -0.5, 0.0), (0.32, 0.86, -0.52, 0.0), (0.64, 0.66, -0.42, 0.0), (0.9, 0.42, -0.3, 0.0), (1.0, 0.2, -0.2, -0.02)]
    y, zm, length, width, height = 4.2, 11.6, 8.0, 9.4, 5.4
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.62, lower="Belly", teeth=(10, 9), tall=1.1, base=0.4, fangs=((0.88, 1.7),), seed=11, t0=0.3)
    throat_glow(m, y + length * 0.18, zm, width, height)
    for side in (-1, 1):
        tox_eye(m, at(0.56, 0.72 if side > 0 else math.pi - 0.72), 0.8, (side * 0.34, 0.93, -0.08), side, socket=1.8, ridge="Body", ridge_size=1.3)
        tox_eye(m, at(0.3, 0.5 if side > 0 else math.pi - 0.5), 0.4, (side * 0.86, 0.5, 0.0), side, socket=1.6, pupil="Slit", ridge=None)
        pivot = Vector((side * width * 0.4, y + length * 0.5, zm - 0.4))
        side_jaw(m, side, pivot, [pivot, pivot + Vector((side * 3.4, 3.0, -0.8)), pivot + Vector((side * 2.8, 7.4, -1.4)), pivot + Vector((-side * 2.2, 9.4, -1.8))], 1.7, teeth=3)
        root = at(0.5, 1.28 if side > 0 else math.pi - 1.28)
        pts = curve([root, root + Vector((side * 1.4, 1.0, 3.0)), root + Vector((side * 3.2, 4.4, 5.0)), root + Vector((side * 4.0, 8.4, 3.4))], 7)
        chain(m, "Sway", 1 if side < 0 else 2, pts, 0.6, 0.16, parent="Head", role="Accent")
        egg(m, "Glow", pts[-1], 0.4, 0.4, 0.4, 6, 4)
        m.bone = "Head"
        band(m, "Accent", tuple(at(0.16, math.pi / 2) - Vector((0, 0, height * 0.5))), width * 0.9, height * 1.06, length=0.8, bone="Head")
    for n, size in enumerate((1.2, 1.0, 0.9, 1.1, 0.9, 0.8), start=1):  # acid, hidden in its head until it spits
        acid(m, n, (0, y + length * 0.36, zm + 1.6), size)
    m.bone = "Head"
    m.head_centre = (0, 10.0, 12.2)
    grounded(m)
    return finish(m)


# ---------------------------------------------------------------------- Sporantula


def ooze(m, centre, bone="DripB", parent="Spine"):
    """The Drip bone the game needs to turn RAGE on, carrying only a small piece hidden in the middle of the body (a bone with no
    mesh is dropped by the importer). The owner had the venom drops that fell from it taken off, 2026-11-10: they read as stray
    dots. DRIP still slides it down DRIP[bone] gap studs, so keep it that far inside."""
    m.use(bone, tuple(centre), parent)
    egg(m, "Body", tuple(centre), 0.3, 0.3, 0.3, 6, 4)
    m.bone = parent


def sporantula():
    """A tarantula in warning bands, front legs up over its head, venom pouring off its fangs."""
    m = monster("dino_Sporantula", Body="#127068", Accent="#08161c", Belly="#d8388c", Claw="#f2f7b4")
    m.joint("Spine", (0, -1.0, 7.4))
    m.joint("Neck", (0, 3.2, 7.2), "Spine")
    m.joint("Head", (0, 4.4, 7.2), "Neck")
    carapace = [((0, -3.2, 7.0), 4.0, 3.0), ((0, -1.4, 7.6), 9.6, 5.8), ((0, 1.6, 7.8), 10.6, 6.2), ((0, 4.2, 7.5), 9.0, 5.4), ((0, 6.0, 7.2), 7.0, 4.2)]
    bones = ["Spine", "Spine", "Spine", "Neck", "Head"]
    sweep_fine(m, "Body", carapace, bones, sides=18, under="Belly", under_faces=5, per=4)
    abdomen = [((0, -2.4, 7.4), 3.0, 3.0), ((0, -4.4, 8.8), 9.6, 8.4), ((0, -8.6, 10.8), 13.6, 12.0), ((0, -12.8, 11.0), 13.0, 11.4), ((0, -16.0, 9.4), 8.0, 7.4), ((0, -17.6, 8.0), 2.0, 2.0)]
    sweep_fine(m, "Body", abdomen, None, sides=20, under="Belly", under_faces=5, per=4)
    for u in (1.5, 2.2, 2.9, 3.5):  # glowing chevrons down its back
        apex, _ = skin_at(abdomen, u - 0.28, math.pi / 2, 0.1)
        for a in (0.72, math.pi - 0.72):
            end, _ = skin_at(abdomen, u + 0.1, a, 0.1)
            mid, _ = skin_at(abdomen, u - 0.1, (a + math.pi / 2) / 2, 0.1)
            sweep(m, "Vein", [(tuple(apex), 0.8, 0.5), (tuple(mid), 0.9, 0.5), (tuple(end), 0.3, 0.3)], sides=6)
    cluster(m, abdomen, [(1.6, 0.25, 1.1), (2.4, 0.1, 1.5), (3.2, 0.2, 1.2), (3.9, 0.5, 0.9), (2.0, -0.35, 0.9), (3.0, -0.3, 1.0)])
    for a in (0.9, math.pi / 2, math.pi - 0.9):  # spinnerets, hooked
        at, n = skin_at(abdomen, 4.4, a)
        horn(m, "Claw", tuple(at - n * 0.3), tuple(at + n * 1.6 + Vector((0, -2.4, 0.4))), 1.1)
    for k, u in enumerate((1.4, 2.0, 2.6, 3.2, 3.8)):
        at, n = skin_at(abdomen, u, math.pi / 2)
        horn(m, "Claw", tuple(at - n * 0.3), tuple(at + n * 2.6 + Vector((0, -1.6, 0))), 1.2)
    legs = (("Arm", (4.0, 3.8, 7.6), (9.4, 6.8, 15.0), (8.6, 11.6, 18.6), (5.6, 16.4, 14.4)),
            ("Front", (4.8, 2.0, 7.6), (11.6, 6.0, 14.0), (15.6, 9.6, 7.0), (16.8, 11.4, 0.3)),
            ("Back", (5.0, 0.0, 7.6), (13.2, -0.4, 14.6), (17.8, -1.6, 7.2), (19.4, -2.0, 0.3)),
            ("Leg", (4.6, -1.8, 7.6), (11.4, -6.8, 14.0), (15.6, -11.4, 7.0), (16.8, -13.6, 0.3)))
    for letter, side in (("L", -1), ("R", 1)):
        for name, *pts in legs:
            pts = [Vector((side * x, y_, z)) for x, y_, z in pts]
            m.use(f"{name}{letter}", tuple(pts[0]))
            knob(m, "Body", pts[0], 1.7)
            path = [pts[0], pts[0].lerp(pts[1], 0.5) + Vector((0, 0, 0.5)), pts[1], pts[1].lerp(pts[2], 0.5) + Vector((side * 0.7, 0, 0.5)), pts[2], pts[2].lerp(pts[3], 0.6), pts[3]]
            banded(m, [(tuple(p), w, w) for p, w in zip(path, (2.6, 2.4, 2.0, 1.8, 1.5, 1.1, 0.5))], ("Body", "Accent"), chunk=3, swell=(1.0, 1.12), sides=10)
            for joint in pts[1:3]:
                egg(m, "Vein", tuple(joint), 1.55, 1.55, 1.55, 8, 5)
            point(m, "Claw", tuple(pts[2].lerp(pts[3], 0.8)), tuple(pts[3] + (pts[3] - pts[2]).normalized() * 0.9), 1.5)
    m.bone = "Head"
    skull = [(0, 0.9, 0.0, 0.8), (0.3, 1.0, 0.0, 0.86), (0.6, 0.9, 0.0, 0.66), (0.86, 0.66, 0.0, 0.42), (1.0, 0.36, 0.04, 0.2)]
    jaw = [(0, 0.86, -0.5, 0.0), (0.4, 0.9, -0.52, 0.0), (0.76, 0.66, -0.4, 0.0), (1.0, 0.3, -0.22, -0.02)]
    y, zm, length, width, height = 4.6, 6.4, 5.6, 9.0, 3.8
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.5, lower="Belly", teeth=(8, 7), tall=1.0, base=0.42, fangs=(), seed=13, t0=0.3)
    throat_glow(m, y + length * 0.2, zm, width, height)
    for side in (-1, 1):
        tox_eye(m, at(0.62, 0.9 if side > 0 else math.pi - 0.9), 0.78, (side * 0.3, 0.94, -0.06), side, socket=1.7, ridge_size=1.3)
        for t, a_, r, look in ((0.82, 1.3, 0.34, (side * 0.1, 1, 0.2)), (0.4, 1.05, 0.44, (side * 0.4, 0.7, 0.6)), (0.3, 0.5, 0.4, (side * 0.9, 0.3, 0.3))):  # six more
            tox_eye(m, at(t, a_ if side > 0 else math.pi - a_), r, look, side, socket=1.5, pupil="Slit", ridge=None, top=0.3, low=0.2)
        pivot = Vector((side * 2.3, y + length * 0.9, zm + 0.5))
        tip = pivot + Vector((-side * 0.9, 1.9, -5.0))
        side_jaw(m, side, pivot, [pivot, pivot + Vector((side * 0.5, 1.6, -1.6)), pivot + Vector((0, 2.4, -3.6)), tip], 1.9, flat=0.9)
    ooze(m, (0, 1.6, 8.2))
    m.bone = "Head"
    m.head_centre = (0, 9.4, 6.8)
    grounded(m)
    return finish(m)


# ---------------------------------------------------------------------- Gillotine


def sludge(m, n, at, size, role="Glow"):
    """A lump of toxic sludge on a Shard bone, parked out of sight inside the body until the blades land (FLING in rare_kit.py)."""
    m.use(f"Shard{n}", at, "Root")
    x, y, z = at
    sweep(m, role, [((x, y, z - size), 0.04, 0.04), ((x + size * 0.1, y, z - size * 0.15), size * 1.1, size * 0.9), ((x - size * 0.1, y, z + size * 0.25), size * 0.8, size * 0.8), ((x, y, z + size), 0.04, 0.04)], sides=6)


def crack(m, body, spots, w=0.5, role="Glow", out=0.08):
    """A glowing crack running over a body through (u, angle) spots."""
    pts = [skin_at(body, u, a, out)[0] for u, a in spots]
    widths = [w * (0.4 + 0.6 * math.sin(math.pi * (k + 0.5) / len(pts))) for k in range(len(pts))]
    sweep(m, role, [(tuple(p), wd, wd * 0.6) for p, wd in zip(pts, widths)], sides=5)


def gillotine():
    """A tall pale mantis leaning on two blades as long as itself, a frill of gills stood up behind its head."""
    m = monster("dino_Gillotine", Body="#d3e2a4", Accent="#3d1c66", Belly="#8fbf2a", Claw="#241038")
    m.joint("Spine", (0, -1.6, 9.6))
    m.joint("Neck", (0, 3.4, 17.4), "Spine")
    m.joint("Head", (0, 4.2, 18.0), "Neck")
    trunk = [((0, -3.0, 8.4), 4.4, 4.0), ((0, -1.8, 10.0), 6.8, 6.2), ((0, -0.2, 12.4), 5.4, 4.8), ((0, 1.6, 14.8), 8.0, 5.8), ((0, 2.8, 16.6), 7.4, 5.2), ((0, 3.8, 18.0), 3.8, 3.6)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Spine", "Neck"]
    sweep_fine(m, "Body", trunk, bones, sides=16, under="Belly", under_faces=5, per=4)
    stripes(m, trunk, (1.5, 2.0, 2.5), "Accent", bones, grow=1.05, length=0.5)
    cluster(m, trunk, [(3.2, 0.9, 1.0), (3.9, 1.2, 0.8), (1.2, 0.9, 0.9)], role="Vein", bones=bones)
    for k, u in enumerate((1.2, 2.0, 2.8, 3.5, 4.2)):
        at, n = skin_at(trunk, u, math.pi / 2)
        horn(m, "Claw", tuple(at - n * 0.3), tuple(at + n * 2.4 + Vector((0, -0.4, 1.4))), 1.0)
    # The abdomen, a long striped tail behind it.
    tail = curve([(0, -2.6, 9.0), (0, -6.0, 9.6), (0, -10.5, 8.6), (0, -15.0, 6.6), (0, -18.6, 4.6)], 13)
    widths = (3.6, 5.6, 6.8, 7.4, 7.6, 7.4, 7.0, 6.2, 5.2, 4.2, 3.0, 1.8, 0.4)
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w * 0.86) for p, w in zip(tail, widths)], sides=14, under="Belly", under_faces=5)
    for k in (3, 5, 7, 9):
        band(m, "Accent", tail[k], widths[k] * 1.05, widths[k] * 0.9, length=0.7, bone=["Tail1", "Tail2", "Tail3"][min((k - 1) * 3 // 12, 2)], tilt=tuple(Vector(tail[k]) - Vector(tail[k - 1])))
    m.bone = "Spine"
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee, ankle, foot = Vector((side * 3.0, -1.6, 9.4)), Vector((side * 5.4, 2.4, 6.0)), Vector((side * 4.8, -2.2, 2.6)), Vector((side * 5.0, -0.2, 0.7))
        m.use(f"Leg{letter}", tuple(hip))
        knob(m, "Body", hip, 2.3)
        limb(m, "Body", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.5, 0.2, 0.5)), knee], (3.8, 3.2, 2.2), sides=12)
        point(m, "Claw", tuple(knee), tuple(knee + Vector((side * 0.8, 2.2, 1.2))), 1.3)
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        knob(m, "Accent", knee, 1.35)
        limb(m, "Accent", [knee, knee.lerp(ankle, 0.5) + Vector((0, -0.5, 0)), ankle, foot, foot + Vector((0, 2.4, -0.1))], (2.1, 1.6, 1.3, 1.4, 1.8), sides=10)
        talons(m, foot + Vector((0, 2.6, 0)), (0, 1, -0.15), 3, 0.9, 2.6, 0.8)
        # The blade: an upper arm up to a high elbow, then one long edge down to the ground.
        shoulder, elbow, tip = Vector((side * 4.6, 2.4, 15.8)), Vector((side * 8.0, 0.4, 20.6)), Vector((side * 8.3, 7.2, 0.3))
        m.use(f"Arm{letter}", tuple(shoulder))
        knob(m, "Body", shoulder, 2.0)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5) + Vector((side * 0.4, -0.3, 0)), elbow], (3.2, 2.6, 2.2), sides=10)
        knob(m, "Accent", elbow, 1.7)
        bow = elbow.lerp(tip, 0.45) + Vector((side * 0.6, 3.4, 1.0))
        sabre(m, "Claw", [tuple(elbow), tuple(bow), tuple(tip)], 4.4, 12, flat=0.22, sides=6, power=1.9)
        edge = [Vector(p) + Vector((0, 1.0, -0.5)) for p in curve([elbow, bow, tip], 12)]
        sweep(m, "Vein", [(tuple(p), 0.5, 0.9 * (1 - k / 11) + 0.1) for k, p in enumerate(edge)], sides=5)
        for k in range(2, 10):  # saw teeth down the cutting edge
            p = edge[k]
            point(m, "Claw", tuple(p - Vector((0, 0.3, 0))), tuple(p + Vector((0, 1.5, -1.2))), 0.9)
        # Wings: stood up behind it in a threat, veined with venom.
        root = Vector((side * 2.2, 0.8, 15.4))
        m.use(f"Wing{letter}", tuple(root))
        for j, (dx, dy, dz, w) in enumerate(((6.5, -6.0, 9.0, 4.4), (9.5, -7.0, 3.0, 3.8))):
            tip_ = root + Vector((side * dx, dy, dz))
            across = unit(Vector((side * dz, 0, -dx)))
            leaf(m, "Accent", tuple(root), tuple(tip_), tuple(across), w, thick=0.2)
            normal = unit((tip_ - root).cross(across)) * 0.24
            for sign in (-1, 1):  # veins on both faces
                for f0, f1, o in ((0.1, 0.94, 0.0), (0.2, 0.7, 0.3), (0.2, 0.7, -0.3)):
                    sweep(m, "Vein", [(tuple(root.lerp(tip_, f0) + normal * sign), 0.34, 0.2), (tuple(root.lerp(tip_, f1) + across * o * w + normal * sign), 0.14, 0.14)], sides=4)
    m.bone = "Head"
    skull = [(0, 0.9, 0.0, 0.8), (0.22, 1.0, 0.0, 0.96), (0.5, 0.74, 0.0, 0.8), (0.76, 0.46, 0.0, 0.52), (0.94, 0.28, 0.0, 0.3), (1.0, 0.14, 0.04, 0.16)]
    jaw = [(0, 0.8, -0.5, 0.0), (0.34, 0.74, -0.46, 0.0), (0.7, 0.44, -0.34, 0.0), (0.94, 0.24, -0.22, 0.0), (1.0, 0.1, -0.14, -0.02)]
    y, zm, length, width, height = 3.8, 16.6, 7.6, 7.6, 4.0
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.66, lower="Belly", teeth=(9, 8), tall=1.05, base=0.34, fangs=((0.86, 2.0),), seed=15, t0=0.3)
    throat_glow(m, y + length * 0.18, zm, width, height)
    for side in (-1, 1):
        tox_eye(m, at(0.34, 0.5 if side > 0 else math.pi - 0.5), 1.0, (side * 0.6, 0.8, -0.04), side, socket=1.6, ridge_size=1.15, top=0.44)
        pivot = Vector((side * width * 0.3, y + length * 0.6, zm - 0.3))
        side_jaw(m, side, pivot, [pivot, pivot + Vector((side * 1.8, 1.8, -0.6)), pivot + Vector((side * 1.4, 4.2, -1.0)), pivot + Vector((-side * 1.0, 5.4, -1.2))], 0.95)
        root = at(0.4, 1.3 if side > 0 else math.pi - 1.3)
        pts = curve([root, root + Vector((side * 0.8, 1.0, 3.0)), root + Vector((side * 1.6, 4.0, 5.2)), root + Vector((side * 1.8, 8.0, 5.0))], 7)
        chain(m, "Sway", 1 if side < 0 else 2, pts, 0.42, 0.12, parent="Head", role="Accent")
        m.bone = "Head"
    for k in range(7):  # the gills: a frill stood up behind its head
        a = math.radians(-78 + 26 * k)
        base = Vector((math.sin(a) * 2.4, 3.9, 18.4 + math.cos(a) * 1.4))
        tip_ = base + Vector((math.sin(a) * 4.6, -2.6, math.cos(a) * 4.6 + 1.0)) * (1.25 - 0.1 * abs(k - 3))
        across = Vector((math.cos(a), 0, -math.sin(a)))
        leaf(m, "Accent", tuple(base), tuple(tip_), tuple(across), 2.3, thick=0.26)
        normal = unit((tip_ - base).cross(across))
        normal *= 0.3 if normal.y > 0 else -0.3  # on the face that looks ahead
        sweep(m, "Vein", [(tuple(base.lerp(tip_, 0.15) + normal), 0.4, 0.26), (tuple(base.lerp(tip_, 0.86) + normal), 0.14, 0.14)], sides=4)
    for n, size in enumerate((1.3, 1.1, 1.0, 1.3, 1.1, 1.0), start=1):  # sludge it knocks off the ground
        sludge(m, n, (0, -1.4, 10.2), size, "Glow" if n % 2 else "Puff")
    m.bone = "Head"
    m.head_centre = (0, 9.0, 16.8)
    grounded(m)
    return finish(m)


# ---------------------------------------------------------------------- Shroomageddon


def shroomageddon():
    """The boss: a titan on its knuckles, cracked open on a glowing core, stacks and sacs all over its back."""
    m = monster("dino_Shroomageddon", Body="#2c1c44", Accent="#0f0a18", Belly="#6f9c1e", Claw="#dcf070")
    m.joint("Spine", (0, -7.0, 10.0))
    m.joint("Neck", (0, 6.6, 14.0), "Spine")
    m.joint("Head", (0, 8.4, 13.6), "Neck")
    trunk = [((0, -13.0, 7.4), 4.0, 4.0), ((0, -10.4, 8.8), 12.0, 9.6), ((0, -5.4, 11.4), 16.0, 13.4), ((0, 0.0, 14.0), 20.0, 15.4), ((0, 4.6, 15.2), 21.0, 13.6), ((0, 8.4, 14.4), 13.6, 9.6)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Spine", "Neck"]
    sweep_fine(m, "Body", trunk, bones, sides=22, under="Belly", under_faces=7, per=4)
    core, n = skin_at(trunk, 3.9, -math.pi / 2)  # the core, in its chest
    sac(m, core, n, 3.4, "Glow", "Accent", sink=0.5)
    for k in range(7):  # cracks running out of it and over its sides
        a0 = -math.pi / 2 + (k - 3) * 0.3
        sign = 1 if k >= 3 else -1
        crack(m, trunk, [(3.9 - 0.2 * j + 0.05 * (j % 2), a0 + sign * (0.12 + 0.26 * j) + 0.06 * (-1) ** j) for j in range(1, 7)], w=0.9)
    for side in (-1, 1):
        crack(m, trunk, [(1.3 + 0.35 * j, (math.pi / 2 - side * (0.5 + 0.1 * (-1) ** j))) for j in range(7)], w=0.8)
    cluster(m, trunk, [(3.5, 1.0, 2.2), (2.8, 0.75, 1.7), (2.1, 1.05, 1.9), (1.4, 0.8, 1.3), (4.3, 0.7, 1.4), (3.1, 0.3, 1.5), (2.2, 0.25, 1.2), (4.0, 1.3, 1.0)], role="Vein", bones=bones)
    for u, a, h, w in ((3.2, math.pi / 2, 7.0, 3.4), (2.3, math.pi / 2, 5.2, 2.8), (3.9, 1.05, 4.6, 2.4), (3.9, math.pi - 1.05, 5.4, 2.6), (1.5, math.pi / 2, 3.6, 2.2), (2.7, 1.2, 3.2, 1.8), (2.7, math.pi - 1.2, 3.8, 2.0)):
        at, normal = skin_at(trunk, u, a)
        chimney(m, None, at, normal, h, w, "Spine", lean=(0, -0.2, 0.9))
    for letter, side in (("L", -1), ("R", 1)):
        shoulder, elbow, wrist, fist = Vector((side * 9.6, 4.4, 14.4)), Vector((side * 15.4, 6.0, 9.0)), Vector((side * 14.0, 10.0, 4.6)), Vector((side * 13.6, 11.4, 2.6))
        m.use(f"Front{letter}", tuple(shoulder))
        knob(m, "Body", shoulder + Vector((side * 0.8, 0, 1.0)), 5.6)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5) + Vector((side * 0.8, 0, 0.6)), elbow, elbow.lerp(wrist, 0.5) + Vector((side * 0.8, 0, 0)), wrist], (9.0, 8.4, 7.4, 7.0, 6.4), sides=14)
        egg(m, "Accent", tuple(fist), 4.0, 4.2, 2.8, 12, 6)
        for dx in (-2.4, -0.8, 0.8, 2.4):
            sabre(m, "Claw", [(fist.x + dx, fist.y + 2.6, 2.8), (fist.x + dx * 1.1, fist.y + 5.0, 2.2), (fist.x + dx * 1.2, fist.y + 6.0, 0.1)], 1.5, 7)
        point(m, "Claw", tuple(elbow), tuple(elbow + Vector((side * 3.0, -4.0, 3.0))), 3.0)
        sac(m, shoulder + Vector((side * 2.6, 0.4, 5.6)), (side * 0.5, 0, 1), 1.9, "Vein")
        band(m, "Accent", tuple(elbow.lerp(wrist, 0.5) + Vector((side * 0.6, 0, 0))), 8.2, 8.2, length=1.4, tilt=tuple(wrist - elbow))
        hip, knee, foot = Vector((side * 6.6, -8.4, 8.6)), Vector((side * 10.0, -5.6, 5.4)), Vector((side * 9.4, -8.6, 1.2))
        m.use(f"Back{letter}", tuple(hip))
        knob(m, "Body", hip, 4.6)
        limb(m, "Body", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.6, 0.4, 0.4)), knee, knee.lerp(foot, 0.5) + Vector((0, -0.6, 0)), foot], (7.6, 7.0, 5.6, 4.8, 4.6), sides=12)
        egg(m, "Accent", tuple(foot + Vector((0, 1.4, -0.2))), 3.2, 3.8, 1.4, 12, 5)
        talons(m, foot + Vector((0, 4.4, -0.2)), (0, 1, -0.3), 3, 1.7, 3.0, 1.2)
    m.bone = "Spine"
    tail = curve([(0, -12.4, 8.0), (0, -16.0, 7.4), (0, -20.0, 5.4), (0, -23.6, 3.6)], 7)
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(tail, (5.6, 4.8, 4.0, 3.4, 3.0, 3.0, 3.2))], sides=10)
    m.bone = "Tail3"
    egg(m, "Vein", (0, -25.0, 3.6), 2.6, 2.8, 2.4, 10, 6)  # a club of venom on the end of it
    for k in range(6):
        a = k * math.tau / 6
        d = Vector((math.cos(a), -0.3, math.sin(a)))
        point(m, "Claw", tuple(Vector((0, -25.0, 3.6)) + d * 1.6), tuple(Vector((0, -25.0, 3.6)) + d * 4.4), 1.5)
    m.bone = "Spine"
    for n, (side, back, up) in enumerate(((-1, 0, 1), (1, 0, 1), (-1, 1, 0.5), (1, 1, 0.5)), start=1):  # venom whips off its shoulders
        root, _ = skin_at(trunk, 3.6 - 1.2 * back, 0.8 if side > 0 else math.pi - 0.8)
        whip(m, n, [root, root + Vector((side * 5.0, -2.0, 6.0 * up)), root + Vector((side * 11.0, 0.0, 9.0 * up)), root + Vector((side * 16.0, 5.0, 6.0 * up)), root + Vector((side * 18.0, 11.0, 2.0 * up))],
             2.4, 0.5, role="Accent", tip_size=1.5, count=12)
    m.bone = "Head"
    skull = [(0, 0.84, 0.0, 0.96), (0.22, 1.0, 0.0, 1.08), (0.48, 0.96, 0.0, 0.88), (0.72, 0.8, 0.0, 0.6), (0.92, 0.56, 0.0, 0.38), (1.0, 0.3, 0.04, 0.2)]
    jaw = [(0, 0.84, -0.66, 0.0), (0.3, 0.98, -0.72, 0.0), (0.6, 0.9, -0.6, 0.0), (0.85, 0.7, -0.44, 0.0), (0.97, 0.46, -0.3, 0.0), (1.0, 0.24, -0.2, -0.02)]
    y, zm, length, width, height = 7.6, 11.6, 12.4, 14.0, 8.0
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.5, lower="Accent", teeth=(15, 13), tall=1.8, base=0.72, fangs=((0.84, 1.9), (0.5, 1.5)), rows=2, seed=17, t0=0.3, throat=1.1)
    throat_glow(m, y + length * 0.16, zm, width, height)
    for side in (-1, 1):
        tox_eye(m, at(0.56, 0.86 if side > 0 else math.pi - 0.86), 1.05, (side * 0.3, 0.94, -0.12), side, socket=1.9, ridge_size=1.5)
        tox_eye(m, at(0.4, 0.5 if side > 0 else math.pi - 0.5), 0.6, (side * 0.7, 0.7, 0.0), side, socket=1.6, pupil="Slit", ridge=None)
        tox_eye(m, at(0.7, 1.2 if side > 0 else math.pi - 1.2), 0.5, (side * 0.1, 0.9, 0.3), side, socket=1.6, pupil="Slit", ridge=None)
        spot = at(0.26, 0.9 if side > 0 else math.pi - 0.9)  # a crown of horns
        horn(m, "Claw", tuple(spot - Vector((0, 0, 0.6))), tuple(spot + Vector((side * 7.0, -3.0, 7.0))), 3.0, droop=-2.0, count=9)
        spot = at(0.12, 0.45 if side > 0 else math.pi - 0.45)
        horn(m, "Claw", tuple(spot - Vector((side * 0.5, 0, 0))), tuple(spot + Vector((side * 6.0, 2.0, -1.0))), 2.2, droop=1.4, count=8)
        for t, a_, r in ((0.84, 0.9, 0.7), (0.2, 1.25, 1.0)):
            sac(m, at(t, a_ if side > 0 else math.pi - a_), (side * 0.3, 0.2, 0.9), r, "Vein")
    for t, tall in ((0.14, 4.0), (0.3, 3.4), (0.46, 2.8), (0.62, 2.0)):
        spot = at(t, math.pi / 2)
        horn(m, "Claw", tuple(spot - Vector((0, 0, 0.4))), tuple(spot + Vector((0, -tall * 0.5, tall))), 1.6)
    ooze(m, (0, 0.0, 16.0))
    m.bone = "Head"
    m.head_centre = (0, 19.0, 11.6)
    grounded(m)
    return finish(m)


# ---------------------------------------------------------------------- Mouth Breather


def mouth_breather():
    """One huge head lit from inside and a small rump behind it: a lure over the mouth, whiskers of venom streaming off its cheeks."""
    m = monster("dino_MouthBreather", Body="#d6c81c", Accent="#3d1664", Belly="#f1eaa4", Claw="#2a0f42", Tongue="#8fe01a", Mouth="#2c0a3e")
    m.joint("Spine", (0, -6.0, 8.0))
    m.joint("Gulp", (0, -3.0, 10.0), "Spine")
    m.joint("Neck", (0, -1.0, 10.4), "Gulp")
    m.joint("Head", (0, 1.0, 10.4), "Neck")
    rings = [((0, -13.4, 8.4), 3.0, 3.0), ((0, -12.0, 9.0), 10.0, 9.0), ((0, -8.0, 10.0), 15.0, 12.4), ((0, -4.0, 11.0), 17.0, 13.4), ((0, -1.0, 12.4), 18.6, 14.0), ((0, 2.6, 13.6), 19.0, 12.0), ((0, 5.0, 14.2), 16.0, 8.0)]
    bones = ["Spine", "Spine", "Spine", "Gulp", "Gulp", "Head", "Head"]
    sweep_fine(m, "Body", rings, bones, sides=24, under="Belly", under_faces=7, per=4)
    for u, w in ((1.45, 1.6), (2.2, 1.9), (2.95, 2.0), (3.7, 1.8)):  # tiger stripes over its back, down to points on its sides
        pts = [skin_at(rings, u + 0.1 * math.cos(2.4 * a), a, -0.25)[0] for a in (0.15 + 0.31 * k for k in range(10))]
        m.bone = bones[round(u)]
        sweep(m, "Accent", [(tuple(p), w * math.sin(math.pi * (k + 0.6) / 10.2) + 0.2, 1.1) for k, p in enumerate(pts)], sides=8)
    cluster(m, rings, [(1.8, 0.8, 1.5), (2.6, 1.1, 1.9), (3.3, 0.7, 1.6), (1.2, 1.15, 1.0), (2.6, 0.35, 1.2), (3.4, 0.2, 1.0), (1.8, 0.25, 0.9), (4.0, 1.25, 1.1)], role="Vein", bones=bones)
    for u, a, h, w in ((2.2, math.pi / 2, 3.6, 2.0), (3.0, 1.35, 2.6, 1.5), (3.0, math.pi - 1.35, 3.0, 1.6)):
        at_, normal = skin_at(rings, u, a)
        chimney(m, None, at_, normal, h, w, bones[round(u)], lean=(0, -0.3, 0.8))
    for name, x, y, front in (("FrontL", -8.0, 1.0, True), ("FrontR", 8.0, 1.0, True), ("BackL", -7.4, -9.6, False), ("BackR", 7.4, -9.6, False)):
        side = 1 if x > 0 else -1
        m.use(name, (x, y, 7.6), "Gulp" if front else "Spine")
        knee = Vector((x + side * (4.4 if front else 5.2), y + (0.0 if front else 2.4), 7.0 if front else 8.4))
        foot = Vector((x + side * 3.6, y + (2.0 if front else -1.0), 0.8))
        start = Vector((x, y, 7.6))
        knob(m, "Body", start + Vector((0, 0, 1.6)), 4.1)
        limb(m, "Body", [start, start.lerp(knee, 0.5), knee, knee.lerp(foot, 0.4), knee.lerp(foot, 0.8), foot], (6.0, 6.2, 4.4, 4.0, 2.8, 2.6), sides=14)
        band(m, "Accent", tuple(knee.lerp(foot, 0.3)), 4.5, 4.5, length=1.0, tilt=tuple(foot - knee))
        band(m, "Accent", tuple(knee.lerp(foot, 0.68)), 3.5, 3.5, length=0.9, tilt=tuple(foot - knee))
        sac(m, knee + Vector((side * 1.6, 0, 1.4)), (side * 0.8, 0, 0.6), 1.2, "Vein")
        point(m, "Claw", tuple(knee), tuple(knee + Vector((side * 2.4, -2.0, 1.6))), 1.8)
        egg(m, "Accent", tuple(foot + Vector((0, 0.8, -0.2))), 2.2, 2.4, 0.8, 10, 5)
        talons(m, foot + Vector((0, 2.4, -0.2)), (0, 1, -0.3), 3, 1.3, 2.4, 0.8)
    m.bone = "Spine"
    path = [(p, w, w) for p, w in zip(curve([(0, -12.6, 9.0), (0, -15.0, 8.0), (0, -17.0, 6.0), (0, -18.6, 3.6)], 7), (5.0, 3.8, 2.8, 2.0, 1.6, 1.4, 1.2))]
    jointed(m, "Accent", ["Tail1", "Tail2", "Tail3"], path, sides=10)
    m.bone = "Tail3"
    egg(m, "Glow", (0, -19.2, 2.8), 1.5, 1.5, 1.5, 10, 6)
    ring_round(m, "Accent", (0, -19.2, 2.8), 1.4, (0.0, -0.6, -0.8), 0.6, 12)
    m.bone = "Head"
    skull = [(0, 0.8, 0.0, 0.84), (0.24, 1.0, 0.0, 0.92), (0.5, 1.0, 0.0, 0.7), (0.74, 0.9, 0.0, 0.46), (0.92, 0.68, 0.0, 0.3), (1.0, 0.34, 0.04, 0.18)]
    jaw = [(0, 0.8, -0.8, 0.0), (0.3, 0.98, -0.86, 0.0), (0.6, 0.92, -0.74, 0.0), (0.84, 0.72, -0.56, 0.0), (0.97, 0.46, -0.4, 0.0), (1.0, 0.24, -0.26, -0.02)]
    y, zm, length, width, height = 0.8, 10.0, 15.0, 20.0, 7.6
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.41, lower="Belly", teeth=(19, 17), tall=2.4, base=0.72, fangs=((0.82, 1.7), (0.48, 1.45)), rows=2, seed=3, jaw_length=1.06, t0=0.32,
                     throat=1.1, tongue_long=0.8)
    egg(m, "Glow", (0, y + length * 0.2, zm - height * 0.1), width * 0.26, width * 0.12, height * 0.36, 12, 6)  # lit from inside
    for k in range(5):  # and ribs of light down the roof of its mouth
        yy = y + length * (0.3 + 0.11 * k)
        hw = width / 2 * 0.62 * (1 - 0.1 * k)
        sweep(m, "Glow", [((-hw, yy, zm - 0.5), 0.3, 0.3), ((-hw * 0.5, yy, zm - 0.8), 0.7, 0.5), ((0, yy, zm - 0.9), 0.8, 0.5), ((hw * 0.5, yy, zm - 0.8), 0.7, 0.5), ((hw, yy, zm - 0.5), 0.3, 0.3)], sides=5)
    for side in (-1, 1):  # eyes up on the roof of the head
        spot = at(0.5, 0.92 if side > 0 else math.pi - 0.92)
        egg(m, "Body", tuple(spot + Vector((0, -0.8, 0.0))), 2.8, 3.0, 1.9, 12, 6)
        c = spot + Vector((side * 0.1, 1.2, 0.5))
        tox_eye(m, c, 1.05, (side * 0.24, 0.95, -0.16), side, socket=1.8, ridge_size=1.4)
        tox_eye(m, at(0.3, 0.6 if side > 0 else math.pi - 0.6), 0.6, (side * 0.8, 0.5, 0.3), side, socket=1.6, pupil="Slit", ridge=None)
        tox_eye(m, at(0.72, 1.0 if side > 0 else math.pi - 1.0), 0.5, (side * 0.3, 0.8, 0.5), side, socket=1.6, pupil="Slit", ridge=None)
        horn(m, "Claw", tuple(c + Vector((side * 1.6, -1.8, 0.6))), tuple(c + Vector((side * 3.8, -6.0, 2.6))), 1.3, droop=-0.3)
        for t, a_, r in ((0.84, 0.75, 0.8), (0.66, 0.5, 0.9), (0.44, 0.34, 1.0), (0.2, 0.4, 1.1), (0.9, 1.15, 0.6)):  # a crown of sacs round its lips
            sac(m, at(t, a_ if side > 0 else math.pi - a_), (side * 0.6, 0.2, 0.7), r, "Vein")
        for n, (t, a_, reach, up) in enumerate(((0.3, 0.16, 9.0, 1.0), (0.18, 0.3, 11.0, 4.0), (0.1, 0.55, 9.0, 7.0)), start=1):  # whiskers of venom, streaming back
            root = at(t, a_ if side > 0 else math.pi - a_)
            pts = curve([root, root + Vector((side * reach * 0.4, -reach * 0.1, up * 0.2)), root + Vector((side * reach * 0.8, -reach * 0.5, up * 0.7)), root + Vector((side * reach, -reach * 1.1, up))], 8)
            chain(m, "Sway", n if side < 0 else n + 3, pts, 0.9, 0.2, parent="Head", role="Accent")
            egg(m, "Glow", pts[-1], 0.6, 0.6, 0.6, 8, 5)
            m.bone = "Head"
        venom(m, (side * width * 0.36, y + length * 0.62, zm - 1.0), 4.2, 0.5)
        venom(m, (side * width * 0.2, y + length * 0.9, zm - 1.0), 3.0, 0.4)
        egg(m, "Socket", tuple(at(0.9, 1.25 if side > 0 else math.pi - 1.25)), 0.82, 0.6, 0.26, 8, 4)
    for t, tall in ((0.12, 4.4), (0.24, 3.8), (0.36, 3.0)):  # a sail of hooks down the middle of the skull
        spot = at(t, math.pi / 2)
        horn(m, "Claw", tuple(spot - Vector((0, 0, 0.3))), tuple(spot + Vector((0, -tall * 0.6, tall))), 1.6)
    # The lure: a stalk off its forehead, bent over the mouth, a lantern of venom wriggling on the end of it.
    root = at(0.5, math.pi / 2)
    pts = curve([root - Vector((0, 0, 0.3)), root + Vector((0, 1.0, 4.6)), root + Vector((0, 5.0, 7.6)), root + Vector((0, 9.6, 6.4)), root + Vector((0, 11.4, 3.0))], 10)
    chain(m, "Wriggle", 1, pts, 1.1, 0.3, parent="Head", role="Accent", sides=8)
    egg(m, "Glow", tuple(Vector(pts[-1]) + Vector((0, 0.2, -1.1))), 1.5, 1.5, 1.7, 10, 6)
    ring_round(m, "Accent", tuple(Vector(pts[-1]) + Vector((0, 0.1, -0.2))), 1.0, (0, 0.2, 1), 0.5, 10)
    for k in range(4):
        a = k * math.tau / 4 + 0.4
        tip = Vector(pts[-1]) + Vector((0, 0.2, -1.1))
        point(m, "Claw", tuple(tip + Vector((math.cos(a), math.sin(a), -0.6)) * 1.0), tuple(tip + Vector((math.cos(a) * 1.4, math.sin(a) * 1.4, -3.0))), 0.6)
    m.bone = "Head"
    m.head_centre = (0, 30.0, 13.0)
    grounded(m)
    return finish(m)


# ---------------------------------------------------------------------- Spore Loser


def spore_loser():
    """The rarest: thin as a flea in plates of acid over venom-violet, hopper's legs folded high, four wings of poisoned glass, a lantern for a tail."""
    m = monster("dino_SporeLoser", Body="#7a1fb0", Accent="#c6f02a", Belly="#e77ad6", Claw="#f4f8c4", Wing="#3a1458")
    m.joint("Spine", (0, -4.0, 9.0))
    m.joint("Bounce", (0, 1.6, 10.6), "Spine")
    m.joint("Neck", (0, 5.0, 12.0), "Bounce")
    rings = [((0, -11.0, 8.0), 2.0, 2.0), ((0, -9.0, 8.4), 6.6, 6.0), ((0, -5.0, 9.2), 8.4, 7.4), ((0, -1.0, 10.0), 6.6, 6.0), ((0, 2.0, 11.0), 5.0, 4.8), ((0, 4.6, 12.0), 3.8, 3.6), ((0, 6.8, 13.0), 3.4, 3.4), ((0, 8.4, 13.6), 4.2, 3.6)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Bounce", "Bounce", "Neck", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=16, under="Belly", under_faces=5)
    for y, z, w, h, bone in ((-8.2, 8.5, 8.0, 7.3, "Spine"), (-6.4, 8.9, 9.0, 8.1, "Spine"), (-4.4, 9.3, 9.4, 8.4, "Spine"), (-2.4, 9.7, 8.5, 7.7, "Spine"), (-0.2, 10.3, 7.1, 6.6, "Bounce"), (2.0, 11.0, 5.6, 5.4, "Bounce"),
                             (4.0, 11.8, 4.6, 4.4, "Bounce")):  # plates of acid down its back
        band(m, "Accent", (0, y, z), w, h, length=1.1, bone=bone, tilt=(0, 1, 0.18))
    for y, z, x in ((-7.3, 8.7, 4.2), (-5.4, 9.1, 4.6), (-3.4, 9.5, 4.4), (-1.3, 10.0, 3.8)):  # sacs swollen out between the plates
        for side in (-1, 1):
            m.bone = "Spine"
            sac(m, (side * x * 0.94, y, z + 0.6), (side, 0, 0.25), 0.8, "Glow", None)
    for k, (y, z, tall) in enumerate(((-8.0, 11.0, 2.6), (-5.4, 12.4, 3.4), (-2.6, 12.6, 3.0), (0.2, 12.8, 2.4), (2.8, 13.2, 2.0))):  # hooks down its back
        m.bone = "Spine" if k < 3 else "Bounce"
        point(m, "Claw", (0, y + 0.3, z - 0.8), (0, y - 1.6, z + tall), 1.5)
    # A lantern on its tail: venom glowing between bands, and a sting.
    m.bone = "Spine"
    lantern = [((0, -10.4, 8.0), 2.4, 2.4), ((0, -12.4, 8.4), 5.2, 5.0), ((0, -15.0, 9.4), 6.4, 6.2), ((0, -17.4, 11.0), 5.0, 4.8), ((0, -19.0, 12.8), 2.2, 2.2)]
    banded(m, lantern, ("Body", "Glow", "Accent", "Glow"), chunk=2, swell=(1.06, 1.0, 1.06, 1.0), sides=14)
    m.use("Sting", (0, -18.8, 12.6), "Spine")
    sabre(m, "Claw", [(0, -18.6, 12.4), (0, -20.6, 15.6), (0, -19.0, 18.8), (0, -15.8, 19.6)], 1.6, 10)
    egg(m, "Glow", (0, -15.6, 19.6), 0.5, 0.6, 0.5, 8, 4)
    m.bone = "Spine"
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee = Vector((side * 3.6, -5.0, 10.2)), Vector((side * 7.6, -11.0, 18.6))
        hock, foot = Vector((side * 8.6, -3.4, 5.4)), Vector((side * 8.8, -0.4, 0.8))
        m.use(f"Back{letter}", tuple(hip))
        knob(m, "Body", hip, 2.6)
        limb(m, "Body", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.3, 0, 0.5)), knee], (4.6, 4.4, 1.6))
        band(m, "Accent", tuple(hip.lerp(knee, 0.34)), 4.9, 4.9, length=1.0, tilt=tuple(knee - hip))
        band(m, "Accent", tuple(hip.lerp(knee, 0.62)), 3.9, 3.9, length=0.9, tilt=tuple(knee - hip))
        m.joint(f"Hock{letter}", tuple(knee), f"Back{letter}")
        m.bone = f"Hock{letter}"
        egg(m, "Glow", tuple(knee), 1.3, 1.3, 1.3, 8, 5)
        limb(m, "Accent", [knee, knee.lerp(hock, 0.5), hock, foot, foot + Vector((0, 2.2, -0.1))], (2.0, 1.3, 1.1, 1.0, 1.4))
        talons(m, foot + Vector((0, 2.2, 0)), (0, 1, -0.1), 3, 0.7, 1.8, 0.6)
        point(m, "Claw", tuple(knee), tuple(knee + Vector((side * 0.6, -2.2, 2.6))), 1.3)
        for k in range(4):  # barbs down the shin
            p = knee.lerp(hock, 0.2 + 0.2 * k)
            point(m, "Claw", tuple(p), tuple(p + Vector((side * 0.5, -1.6, -0.6))), 0.7)
        shoulder, elbow, wrist = Vector((side * 2.4, 2.2, 10.6)), Vector((side * 6.2, 5.4, 7.4)), Vector((side * 5.2, 9.6, 2.4))
        m.use(f"Front{letter}", tuple(shoulder), "Bounce")
        knob(m, "Body", shoulder, 1.5)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5), elbow], (2.4, 1.9, 1.5))
        limb(m, "Accent", [elbow, elbow.lerp(wrist, 0.5), wrist], (1.5, 1.2, 1.1))
        egg(m, "Glow", tuple(elbow), 0.95, 0.95, 0.95, 8, 5)
        talons(m, wrist, (0, 0.7, -0.6), 2, 0.8, 2.8, 0.7)
        # Wings: two a side, dark glass veined with venom.
        root = Vector((side * 1.8, -1.0, 12.6))
        m.use(f"Wing{letter}", tuple(root), "Spine")
        for dx, dy, dz, w in ((11.0, -9.0, 9.0, 5.0), (12.0, -12.0, 2.0, 4.0)):
            tip = root + Vector((side * dx, dy, dz))
            across = unit((tip - root).cross(Vector((0, 1, 0.6))))
            leaf(m, "Wing", tuple(root), tuple(tip), tuple(across), w, thick=0.2)
            normal = unit((tip - root).cross(across)) * 0.24
            for sign in (-1, 1):  # veins on both faces
                for j, (f0, f1, o) in enumerate(((0.1, 0.94, 0.0), (0.2, 0.7, 0.3), (0.2, 0.7, -0.3))):
                    a_, b_ = root.lerp(tip, f0), root.lerp(tip, f1) + across * o * w
                    sweep(m, "Vein", [(tuple(a_ + normal * sign), 0.3, 0.16), (tuple(b_ + normal * sign), 0.12, 0.12)], sides=4)
    m.use("Head", (0, 8.0, 13.0), "Neck")
    skull = [(0, 0.76, 0.0, 1.0), (0.22, 1.0, 0.0, 1.36), (0.44, 0.9, 0.0, 1.46), (0.66, 0.56, 0.0, 1.12), (0.88, 0.34, 0.0, 0.76), (1.0, 0.14, 0.06, 0.36)]
    jaw = [(0, 0.76, -0.5, 0.0), (0.34, 0.68, -0.42, 0.0), (0.66, 0.42, -0.32, 0.0), (0.92, 0.24, -0.22, 0.0), (1.0, 0.1, -0.14, -0.02)]
    at = fierce_head(m, 7.8, 12.6, 8.6, 7.6, 3.4, skull, jaw, gape=-0.8, lower="Belly", teeth=(9, 8), tall=1.2, base=0.34, fangs=((0.88, 2.5),), low_fangs=((0.7, 1.8),), seed=21, lower_inset=0.62, t0=0.32, gum_lift=0.18)
    throat_glow(m, 7.8 + 8.6 * 0.18, 12.6, 7.6, 3.4)
    for side in (-1, 1):
        a_ = 0.86 if side > 0 else math.pi - 0.86
        tox_eye(m, at(0.56, a_), 0.7, (side * 0.3, 0.93, -0.1), side, socket=1.8, ridge_size=1.1, ridge="Body")
        tox_eye(m, at(0.24, 0.6 if side > 0 else math.pi - 0.6), 0.4, (side * 0.8, 0.6, 0), side, socket=1.6, pupil="Slit", ridge=None)  # spare eyes, further back
        tox_eye(m, at(0.72, 1.15 if side > 0 else math.pi - 1.15), 0.3, (side * 0.2, 0.9, 0.3), side, socket=1.6, pupil="Slit", ridge=None)
        feeler = at(0.62, 1.1 if side > 0 else math.pi - 1.1)  # feelers, thin as whips, swept back over it
        pts = curve([feeler, feeler + Vector((side * 1.4, 0.4, 3.4)), feeler + Vector((side * 4.0, -3.4, 6.0)), feeler + Vector((side * 6.4, -9.0, 5.6))], 8)
        chain(m, "Sway", 1 if side < 0 else 2, pts, 0.5, 0.14, parent="Head", role="Claw")
        egg(m, "Glow", pts[-1], 0.5, 0.5, 0.5, 8, 5)
        m.bone = "Head"
        venom(m, (side * 1.5, 7.8 + 8.6 * 0.86, 12.2), 2.4, 0.26)
    beak = at(0.98, math.pi / 2)
    sabre(m, "Claw", [tuple(beak + Vector((0, -1.2, 0.2))), tuple(beak + Vector((0, 0.7, -0.1))), tuple(beak + Vector((0, 0.7, -1.9)))], 1.0, 8, flat=0.6)  # a hook over the mouth
    m.head_centre = (0, 19.0, 14.0)
    grounded(m)
    return finish(m)


ALL = [toad_rage, morel_panic, antagonist, sporantula, gillotine, shroomageddon, mouth_breather, spore_loser]


def main():
    rare_kit.animate = animate  # run() films with it: these stack more than rare_kit's own monsters do
    rare_kit.run(ALL, RENDERS, BLEND, "spore_hollow_toxic", SKY, FLOOR, GLOW_ROLES, glow=0.55, spacing=34)


if __name__ == "__main__":
    main()
