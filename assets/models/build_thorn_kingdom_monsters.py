"""Builds Thorn Kingdom's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_thorn_kingdom_monsters.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_thorn_kingdom_monsters.py    (stills only, for trying faces)
    ONLY=bramble_brat,sir_skewer QUICK=1 ...                                    (just those)

Saves thorn_kingdom_monsters.blend and renders to design/world/monsters_thorn_kingdom/. The map's props are in
build_thorn_kingdom.py.

Map 13, a fairy-tale kingdom cursed to sleep for a thousand years. The owner asked for monsters that fit the biome,
animated, "aggressive and chaotic looking", built in Blender. So these are the ones that woke up: everything in the
kingdom that tore itself out of the curse, furious and half mad, with the briars still growing through it. All six
are aggressive, the commons too (their jokes stay in the names and one silly thing each); nothing here is mirror
symmetric, nothing stands straight, and thorns stick out of everything at every angle.

They share two ideas. The sleepless eye: wide open and bloodshot, a crimson iris with a pinprick slit, never the
same size twice (white and bulging on the feral ones, sunk in a black socket under a slab of brow on the fierce
ones). And the rose maw: a jaw hanging open at rest, crooked teeth of every length, a rose glowing in the throat.

  Bramble Brat    a ball of briars that is nearly all mouth on two stumpy legs: one huge eye, one tiny one, its long
                  tongue whipping about, an eye on a stalk and long thorny arms
  Grandma Gnash   the wolf that ate her and kept the clothes: a hunched silver wolf in a shredded nightcap, shawl
                  and bent spectacles, its wild eyes rolling, the cap's tassel flailing behind it
  Sir Skewer      a suit of armour with nobody in it, only briars: they burst out of a hole in its chest round a
                  glowing rose. A hound-snout visor of steel fangs, a giant spindle for a lance and for a shield a
                  spinning wheel with thorns round its rim that never stops turning
  Hart Attack     a stag with a bare skull for a face and open ribs, a rose burning inside them. Vast crooked antlers
                  of black briar with roses in them, spare eyes up its antlers, snapped arrows still in its flank
  Hydrangry       a heap of violet roots and crimson blooms with five heads on writhing necks, each with its own
                  mouth and its own opinion, all snapping at once
  Wrathorn        the boss: the sleeping king, a dragon now. A black thorn-bark tyrant on its knuckles, wings of
                  crimson blades, rose fire veining its hide, a rusted crown jammed on crooked horns, five eyes, and
                  in its chest a second mouth, a ring of teeth grinding for ever round a burning rose

What moves. The usual walk, idle and roar, and two things new on this map, in DinoLifeController (THRASH) and here
(thrash_of below), the same numbers in both:
  - Lash bones: Lash<n>a, b and c, three bones along a briar whip, thrash for ever whatever the monster is doing,
    each with its own rhythm, swelling, dying down and cracking now and then.
  - Monsters with Lash bones never settle: their heads snap round in sudden jerks, jaws gnash in bursts, bodies
    shudder, arms and tails twitch. Snap<n> bones are the jaws of Hydrangry's spare heads.
  - The spinning bones from map 12 are reused (DinoLifeController SPIN): Cog turns Sir Skewer's wheel, Drill Wrathorn's
    chest maw and Key the ring of glowing petals over its crown.
Everything thrashes at whole multiples of a quarter turn a second, so the pattern repeats every 4 seconds and the
preview's 4-stride walk and 8-second idle both loop seamlessly.

Rules the game adds: Jaw sits in front of Tail1 (or the Spine), since that's how the game tells which way a monster
faces. Only the main eyes use the Pupil role, which the reveal aims at; spare eyes use Slit.

Glowing parts are EyeGlow, RoseGlow, PetalGlow, Thread and CrownGem (Neon in the game, shared/Roles.luau, all there
already). Skin roles Body, Accent, Belly and Claw take the colour mutations; briars, petals, cloth and the face keep
their colour. Built at the first map's size; the game scales them by Config/Biomes standardScale. 1 Blender unit =
1 stud, models face +Y, feet on Z = 0. No crosses or stars anywhere (memory: the owner ruled them out on map 10), so
Sir Skewer carries no sword and nobody carries a cross-shaped anything.

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
from build_clockwork_citadel import SIDEWAYS, Frame, gear, obox, tube, turn  # noqa: E402
from build_clockwork_citadel_monsters import SPIN, fcurves_of, spin_pose  # noqa: E402
from build_desert import beam  # noqa: E402
from build_eclipse_temple_monsters import grow  # noqa: E402
from build_forest import Model, biped_legs  # noqa: E402
from build_starfall_crater import ball, hoop  # noqa: E402
from build_thorn_kingdom import (BARK, BARK_DARK, GOLD, GOLD_DARK, LEAF, LEAF_DARK, PETAL, PETAL_DARK, ROSE, WOOD, WOOD_DARK,  # noqa: E402
                                 rose)
from build_volcano import idle_pose as volcano_idle, prism, ring_at, top_of, walk_pose as volcano_walk  # noqa: E402
from map_kit import limb, plate  # noqa: E402
from monster_stage import build_and_render, light_up, set_sky  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_thorn_kingdom"
BLEND = "thorn_kingdom_monsters"  # for check_map.py and export_fbx.py

GLOW_ROLES = {"EyeGlow", "RoseGlow", "PetalGlow", "Thread", "CrownGem"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket", "Slit", "Vein", "Sinew"})
GLOW = 1.1

FACE = {"Pupil": "#120a10", "Slit": "#120a10", "Socket": "#0b070c", "EyeGlow": ROSE, "EyeWhite": "#f4ecd9", "Highlight": "#ffffff",
        "Mouth": "#1f0b14", "Teeth": "#efe4c8", "Tongue": "#b02445", "RoseGlow": ROSE, "PetalGlow": "#ff5c7c", "Vein": "#c8243f",
        "Sinew": "#6e1428", "Briar": BARK, "Petal": PETAL, "PetalDark": PETAL_DARK, "Leaf": LEAF, "LeafDark": LEAF_DARK}
SKY, FLOOR = "#15121c", "#344e3c"

WALK_PREVIEW = 4 * kit.WALK_FRAMES  # four strides: the thrashing repeats every 4 seconds
W = math.pi / 2  # everything thrashes at whole multiples of this, in radians a second


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- how they thrash


def crack(x):
    """0 nearly all the time, jolting up to 1 and back once every full turn of x."""
    return ((1 + math.cos(x)) / 2) ** 14


def burst(x):
    """Quiet about half the time, then swelling to 1 and dying away."""
    return ((1 + math.sin(x)) / 2) ** 3


def lash_turn(n, k, s):
    """Pitch, roll and yaw of bone k (0 to 2) of whip n, s seconds in: a fast wave running down it, swelling and
    dying, and once every 4 seconds a crack. Each bone bends further than the one before it."""
    sin = math.sin
    phase = 1.9 * n - 0.85 * k
    size = (0.3 + 0.16 * k) * (0.55 + 0.45 * sin(W * s + 2.1 * n))
    snap = (0.5 + 0.3 * k) * crack(W * s + 2.4 * n - 0.5 * k)
    pitch = size * (sin(6 * W * s + phase) + 0.4 * sin(11 * W * s + 1.3 * phase)) + snap
    roll = size * sin(5 * W * s + 2 * phase)
    yaw = size * (sin(7 * W * s + 0.7 * phase) + 0.4 * sin(13 * W * s + phase)) - 0.6 * snap
    return pitch, roll, yaw


def thrash_of(name, s):
    """What a bone adds to the walk and idle, s seconds in; the same as THRASH in DinoLifeController."""
    sin, cos = math.sin, math.cos
    if name.startswith("Lash"):
        return lash_turn(int(name[4:-1]), "abc".index(name[-1]), s)
    if name.startswith("Snap"):
        n = int(name[4:])
        return -0.14 - 0.14 * sin(10 * W * s + 1.7 * n) - 0.3 * crack(2 * W * s + 1.3 * n), 0, 0
    if name == "Head":
        a, b = crack(2 * W * s + 0.7), crack(3 * W * s + 2.2)
        return 0.16 * b - 0.12 * a, 0.2 * a * cos(W * s), 0.34 * a * sin(W * s + 1) - 0.26 * b * cos(W * s)
    if name == "Neck":
        shiver = 0.05 * sin(16 * W * s) * burst(W * s + 2)
        return shiver, 0, shiver
    if name == "Jaw":
        return -0.2 * (0.5 + 0.5 * sin(12 * W * s)) * burst(2 * W * s), 0, 0
    if name == "Spine":
        b = burst(W * s + 4)
        return 0.02 * sin(16 * W * s) * b, 0.03 * sin(12 * W * s) * b, 0
    if name in ("ArmL", "ArmR"):
        return -0.35 * crack(3 * W * s + (0 if name == "ArmL" else 2.5)), 0, 0
    if name in ("Tail1", "Tail2", "Tail3"):
        i = int(name[4])
        return 0, 0, 0.22 * sin(6 * W * s - 0.9 * i) * burst(W * s + i)
    return None


def thrash(a, f):
    """Adds the thrashing to the pose just set. Lash and Snap bones have no other pose, so theirs is the whole pose."""
    s = f / 30
    for bone in a.pose.bones:
        extra = thrash_of(bone.name, s)
        if extra is None:
            continue
        if not bone.name.startswith(("Lash", "Snap")):
            extra = tuple(bone.rotation_euler[i] + extra[i] for i in range(3))
        kit.pose_bone(a, bone.name, extra, None, f)


def walk_pose(a, f):
    volcano_walk(a, f)
    thrash(a, f)
    spin_pose(a, f)


def idle_pose(a, f):
    volcano_idle(a, f)
    t = 2 * math.pi * f / kit.IDLE_FRAMES
    for letter, side in (("L", -1), ("R", 1)):  # the wings' idle, which the Volcano's has no need of
        kit.pose_bone(a, f"Wing{letter}", (0, side * 0.07 * math.sin(4 * t), 0), None, f)
        kit.pose_bone(a, f"WingTip{letter}", (0, side * 0.06 * math.sin(4 * t - 0.8), 0), None, f)
    thrash(a, f)
    spin_pose(a, f)


def animate(armature):
    """The Volcano's walk and idle (jaw snap and roar) with the thrashing on top and the spinning bones turning."""
    walk = kit.add_action(armature, "Walk", WALK_PREVIEW, walk_pose, 2)
    idle = kit.add_action(armature, "Idle", kit.IDLE_FRAMES, idle_pose, 2)
    for action in (walk, idle):  # a steady turn, not eased between keys
        for curve in fcurves_of(action):
            if any(f'"{name}"' in curve.data_path for name in SPIN):
                for point in curve.keyframe_points:
                    point.interpolation = "LINEAR"
    return walk, idle


# ---------------------------------------------------------------------- shapes


def aim(direction):
    """A frame's turn that points its +Y along direction, keeping its +Z as near up as it can."""
    return Vector(direction).normalized().to_track_quat("Y", "Z").to_matrix()


def yloft(f, role, a, b):
    """loft_y in a turned frame: a and b are (y, centre x, centre z, width, height)."""
    def ring(y, cx, cz, w, h):
        return [f.at(cx - w / 2, y, cz - h / 2), f.at(cx + w / 2, y, cz - h / 2), f.at(cx + w / 2, y, cz + h / 2), f.at(cx - w / 2, y, cz + h / 2)]
    f.m._ring_shape(role, ring(*a), ring(*b))


def zloft(f, role, a, b):
    """loft_z in a turned frame: a and b are (z, centre x, centre y, width, depth)."""
    def ring(z, cx, cy, w, d):
        return [f.at(cx - w / 2, cy - d / 2, z), f.at(cx + w / 2, cy - d / 2, z), f.at(cx + w / 2, cy + d / 2, z), f.at(cx - w / 2, cy + d / 2, z)]
    f.m._ring_shape(role, ring(*a), ring(*b))


def slab(f, role, u, v, n, r, depth, sides=12, squash=1.0):
    """A round slab on a frame's XZ plane at n along its +Y; squash narrows it across (slit pupils)."""
    verts = []
    for k in (-depth / 2, depth / 2):
        for i in range(sides):
            a = math.pi / sides + i * math.tau / sides
            verts.append(f.at(u + r * squash * math.cos(a), n + k, v + r * math.sin(a)))
    faces = [list(range(sides))[::-1], list(range(sides, 2 * sides))]
    faces += [[i, (i + 1) % sides, sides + (i + 1) % sides, sides + i] for i in range(sides)]
    f.m._add(role, verts, faces)


def half_ball(f, role, x, y, r, up=1, sides=10, rings=3, squash=1.0):
    """The top (up=1) or bottom (up=-1) half of a chunky ball, flat side on the frame's Z = 0."""
    for k in range(rings):
        a0, a1 = k * math.pi / 2 / rings, (k + 1) * math.pi / 2 / rings
        f.prism(role, x, y, up * r * squash * math.sin(a0), up * r * squash * math.sin(a1), max(r * math.cos(a0), 0.03),
                max(r * math.cos(a1), 0.03), sides)


def point(m, role, base, tip, width):
    """A four-sided spike: six triangles, where a beam tapering to nothing costs twelve. A monster has hundreds."""
    base, tip = Vector(base), Vector(tip)
    along_ = (tip - base).normalized()
    side = along_.cross(Vector((0, 0, 1)))
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    lift = side.cross(along_)
    verts = [tuple(base + side * sx * width / 2 + lift * sz * width / 2) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    m._add(role, verts + [tuple(tip)], [[3, 2, 1, 0], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]])


def thorn(m, role, base, tip, width, hook=0.0):
    """A thorn from base to tip, its last half bent by hook (a direction) if given."""
    base, tip = Vector(base), Vector(tip)
    if not hook:
        point(m, role, base, tip, width)
        return
    mid = base.lerp(tip, 0.55) + Vector(hook)
    beam(m, role, tuple(base), tuple(mid), width, None, width * 0.55)
    point(m, role, mid, tip, width * 0.55)


def blade(m, role, base, tip, side, w, thick=0.1):
    """A pointed leaf, petal or wing blade: a flat diamond from base to tip, broadest along side. Eight triangles."""
    base, tip = Vector(base), Vector(tip)
    run = tip - base
    side = Vector(side)
    side = (side - run.normalized() * side.dot(run.normalized())).normalized()
    normal = run.normalized().cross(side)
    mid = base.lerp(tip, 0.45)
    verts = [tuple(base), tuple(tip), tuple(mid + side * w / 2), tuple(mid - side * w / 2), tuple(mid + normal * thick / 2), tuple(mid - normal * thick / 2)]
    m._add(role, verts, [[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4], [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5]])


def vine(m, role, points, w0, w1, rng, every=0.8, size=0.4):
    """A twisting briar through points, tapering from w0 to w1, with thorns sticking out of it every so often."""
    limb(m, role, points, w0, w1, joints=False)
    count = len(points) - 1
    for i, (p, q) in enumerate(zip(points, points[1:])):
        p, q = Vector(p), Vector(q)
        run = q - p
        steps = max(1, int(run.length / every))
        width = w0 + (w1 - w0) * (i + 0.5) / count
        for k in range(steps):
            c = p + run * ((k + 0.5) / steps)
            out = run.cross(Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))).normalized()
            thorn(m, role, c + out * width * 0.3, c + out * (width * 0.5 + size), width * 0.45)


def bristle(m, role, pair, rng, count, length, width, back=0.5, sides=(0, 0, 1, 2)):
    """Thorns out of a loft_y body at odd angles, swept back: 0 on top, 1 on its left, 2 on its right."""
    y0, y1 = sorted((pair[0][0], pair[1][0]))
    for _ in range(count):
        y = rng.uniform(y0, y1)
        _, cx, cz, w, h = ring_at(*pair, y)
        side = rng.choice(sides)
        if side == 0:
            p, n = Vector((cx + rng.uniform(-0.42, 0.42) * w, y, cz + h / 2)), Vector((0, 0, 1))
        else:
            s = -1 if side == 1 else 1
            p, n = Vector((cx + s * w / 2, y, cz + rng.uniform(-0.3, 0.45) * h)), Vector((s, 0, 0))
        d = (n + Vector((rng.uniform(-0.5, 0.5), -back + rng.uniform(-0.4, 0.4), rng.uniform(-0.2, 0.4)))).normalized()
        thorn(m, role, p - d * 0.05, p + d * length * rng.uniform(0.6, 1.3), width * rng.uniform(0.8, 1.2))


def ridge(m, role, points, rng, length, width, back=0.5):
    """Shards along a line (a spine, a mane), every one its own length and lean."""
    for p in points:
        p = Vector(p)
        tip = p + Vector((rng.uniform(-0.35, 0.35) * length, -back * length * rng.uniform(0.5, 1.4), length * rng.uniform(0.6, 1.3)))
        thorn(m, role, p, tip, width * rng.uniform(0.8, 1.25))


def along(a, b, count):
    """count points spaced along the line from a to b, for ridge()."""
    a, b = Vector(a), Vector(b)
    return [tuple(a.lerp(b, (i + 0.5) / count)) for i in range(count)]


def wrap(m, role, a, b, r, turns, rng, w=0.13, size=0.2):
    """A thorny vine coiling round the line from a to b, r from it: briars strangling a limb."""
    a, b = Vector(a), Vector(b)
    axis = (b - a).normalized()
    u = axis.cross(Vector((0.3, 0.2, 1))).normalized()
    v = axis.cross(u)
    start = rng.uniform(0, math.tau)
    steps = max(6, int(turns * 7))
    points = []
    for i in range(steps + 1):
        t = i / steps
        ang = start + t * turns * math.tau
        points.append(tuple(a.lerp(b, t) + (u * math.cos(ang) + v * math.sin(ang)) * r))
    vine(m, role, points, w, w * 0.7, rng, every=0.7, size=size)


def wander(start, end, rng, count=7, bow=(0, 0, 0), jitter=0.25):
    """A crooked line from start to end, bowed by bow: the points of a whip."""
    a, b = Vector(start), Vector(end)
    bow = Vector(bow)
    points = []
    for i in range(count):
        t = i / (count - 1)
        p = a.lerp(b, t) + bow * (4 * t * (1 - t))
        if 0 < i < count - 1:
            p += Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * jitter
        points.append(tuple(p))
    return points


def lash(m, n, points, w0, w1=0.06, parent="Spine", role="Briar", rng=None, size=0.22, every=0.45, flat=None):
    """A whip through points on three bones, Lash<n>a, b and c, which never stop thrashing (thrash_of). Thorns stick
    out of it if rng is given; flat (a direction) makes it a strip of cloth, wide that way. Leaves m.bone on its last bone,
    so a tip can be added; returns the tip."""
    segments = len(points) - 1
    per = math.ceil(segments / 3)
    bone = parent
    for i, (a, b) in enumerate(zip(points, points[1:])):
        wa = w0 + (w1 - w0) * i / segments
        wb = w0 + (w1 - w0) * (i + 1) / segments
        first = i % per == 0
        if first:
            before = bone
            bone = f"Lash{n}{'abc'[i // per]}"
            m.use(bone, tuple(a), before)
        if flat:
            plate(m, role, a, b, flat, wa, wb, 0.1)
        else:
            beam(m, role, a, b, wa, None, wb)
        if first and before != parent:
            m.stretch(role, before)
        if rng:
            p, q = Vector(a), Vector(b)
            for k in range(max(1, int((q - p).length / every))):
                c = p.lerp(q, (k + 0.5) / max(1, int((q - p).length / every)))
                out = (q - p).cross(Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))).normalized()
                thorn(m, role, c, c + out * (wa * 0.5 + size * rng.uniform(0.7, 1.2)), wa * 0.5)
    return Vector(points[-1])


def puff(m, centre, r, rng, roles=("Floret", "FloretB"), count=16):
    """A hydrangea bloom: a round heap of little four-petalled flowers."""
    c = Vector(centre)
    ball(m, "Accent", *c, r * 0.72, 6, 3)
    for i in range(count):
        z = 1 - 2 * (i + 0.5) / count
        a = i * 2.4
        d = Vector((math.sqrt(1 - z * z) * math.cos(a), math.sqrt(1 - z * z) * math.sin(a), z))
        role = roles[0] if rng.random() < 0.6 else roles[1]
        obox(m, role, c + d * r * rng.uniform(0.78, 0.95), (r * 0.56, r * 0.56, r * 0.24), aim(d) @ turn(x=math.pi / 2, z=rng.uniform(0, 1.5)))


# ---------------------------------------------------------------------- the sleepless eye and the rose maw


def wild_eye(m, centre, look, r, rng, pupil="Pupil", iris=0.5, veins=4, off=(0.0, 0.0), lashes=0, role="EyeWhite"):
    """A bulging, bloodshot eye: a white ball, a crimson iris, a pinprick slit, red veins running in from its rim and
    thorns for lashes round it. off slides the iris across the eye: rolling, not looking at you."""
    f = Frame(m, centre, aim(look))
    ball(m, role, *centre, r, 8, 5)
    n = r * 0.96
    u, v = off[0] * r, off[1] * r
    slab(f, "EyeGlow", u, v, n, r * iris, r * 0.1, 10)
    slab(f, pupil, u, v, n + r * 0.05, r * iris * 0.62, r * 0.06, 8, 0.3)
    f.box("Highlight", u - r * iris * 0.45, n + r * 0.09, v + r * iris * 0.45, r * 0.16, r * 0.03, r * 0.16)
    for k in range(veins):
        a = rng.uniform(0, math.tau)
        beam(m, "Vein", f.at(u + math.cos(a) * r * iris, n * 0.97, v + math.sin(a) * r * iris),
             f.at(u + math.cos(a + 0.3) * r * 0.92, n * 0.45, v + math.sin(a + 0.3) * r * 0.92), r * 0.09, None, r * 0.03)
    for k in range(lashes):
        a = math.pi * (0.1 + 0.8 * k / max(lashes - 1, 1))
        thorn(m, "Briar", f.at(math.cos(a) * r * 0.9, n * 0.2, math.sin(a) * r * 0.9),
              f.at(math.cos(a) * r * 1.5, n * 0.7, math.sin(a) * r * 1.5), r * 0.2)


def glare(m, centre, look, size, inner, slant=0.55, pupil="Pupil", brow="Accent", spikes=2, rng=None):
    """A fierce eye: a black socket, a burning iris and a slit pupil under a heavy brow slanting hard down to the nose
    (inner is +1 if the nose lies at +X), a lid squeezing it from below and thorns growing out of the brow's far end."""
    f = Frame(m, centre, aim(look) @ turn(y=inner * slant * 0.5))
    slab(f, "Socket", 0, 0, 0.03, size * 0.5, 0.08, 10, 1.45)
    slab(f, "EyeGlow", 0, -size * 0.02, 0.09, size * 0.38, 0.05, 10, 1.1)
    slab(f, pupil, 0, -size * 0.02, 0.125, size * 0.3, 0.03, 8, 0.24)
    f.box("Highlight", -size * 0.16, 0.15, size * 0.14, size * 0.1, 0.02, size * 0.1)
    b = Frame(m, centre, aim(look))
    out, nose = -inner * size * 1.0, inner * size * 0.82
    drop = slant * size
    b.beam(brow, (out, 0.1, size * 0.5 + drop * 0.5), (nose, 0.2, size * 0.42 - drop * 0.6), size * 0.42, size * 0.5, size * 0.34)
    b.beam(brow, (out * 0.9, 0.1, -size * 0.5), (nose * 0.9, 0.12, -size * 0.58), size * 0.26, size * 0.18, size * 0.2)
    for k in range(spikes):
        t = 0.12 + 0.3 * k
        p = Vector((out + (nose - out) * t, 0.1, size * 0.72 + drop * 0.45 * (1 - t)))
        tip = p + Vector((-inner * size * 0.55, -size * 0.3, size * (0.9 - 0.2 * k)))
        thorn(m, "Briar", b.at(*p), b.at(*tip), size * 0.28)


def crooked_teeth(m, lf, width_at, edge_at, length, tooth, per_side, rng, up, across=3, fang=-2):
    """Teeth along a jaw in frame lf, none the same: along both edges and across the tip, leaning all ways, a few
    missing, the one at index fang much bigger. width_at(y) and edge_at(y) give the jaw there; up points them up."""
    sign = 1 if up else -1
    for side in (-1, 1):
        for i in range(per_side):
            if rng.random() < 0.1 and i != per_side + fang:
                continue
            y = length * (0.1 + 0.84 * i / max(per_side - 1, 1))
            size = tooth * rng.uniform(0.65, 1.15) * (1.75 if i == per_side + fang else 1)
            x = side * (width_at(y) / 2 - tooth * 0.22)
            edge = edge_at(y)
            point(m, "Teeth", lf.at(x, y, edge - sign * 0.04),
                  lf.at(x + rng.uniform(-0.25, 0.3) * size * side, y + rng.uniform(-0.4, 0.3) * size, edge + sign * size * rng.uniform(0.9, 1.45)),
                  tooth * 0.55 * (1.3 if i == per_side + fang else 1))
    for k in range(across):
        x = (k + 0.5 - across / 2) * width_at(length) / max(across, 1) * 0.85
        size = tooth * rng.uniform(0.7, 1.2)
        point(m, "Teeth", lf.at(x, length * 0.98, edge_at(length) - sign * 0.04),
              lf.at(x + rng.uniform(-0.2, 0.2) * size, length + rng.uniform(-0.1, 0.25) * size, edge_at(length) + sign * size * rng.uniform(0.9, 1.3)),
              tooth * 0.5)


def maw(m, f, skull_w, length, snout_w, upper_h, lower_h, rng, gape=0.16, drop=0.3, upper="Body", lower="Accent", tooth=0.3, per_side=5,
        head="Head", jaw="Jaw", tongue=True, ruff=0, on_jaw=None, lift=0.1, sinew=True, ruff_len=1.0):
    """The rose maw, built in frame f, whose origin is the middle of the mouth's back and whose +Y is out of the
    mouth: an upper jaw on the head bone, a lower jaw on the jaw bone hanging open by drop (radians) at rest, crooked
    teeth, a rose glowing in the throat, strands of sinew stretched between the jaws and, with ruff, petals peeling
    back from the corners of the mouth. on_jaw(m, lf, length) adds to the lower jaw. Returns the snout's tip point in
    f's terms and a function for its top height."""
    m.bone = head
    back = (-0.05, 0, gape / 2 + upper_h * 0.5, skull_w * 0.96, upper_h)
    tip = (length, 0, gape / 2 + upper_h / 2 + lift, snout_w, upper_h)
    yloft(f, upper, back, tip)
    yloft(f, "Mouth", (0, 0, gape / 2 - 0.03, skull_w * 0.84, 0.06), (length * 0.95, 0, gape / 2 + lift * 0.95 - 0.03, snout_w * 0.86, 0.06))
    open_h = gape + drop * length * 0.8 + 0.2
    f.box("Mouth", 0, 0.03, gape / 2 - open_h / 2, skull_w * 0.88, 0.12, open_h)
    f.box("RoseGlow", 0, 0.11, gape / 2 - open_h * 0.5, skull_w * 0.5, 0.06, open_h * 0.62)

    def width(y):
        return skull_w * 0.96 + (snout_w - skull_w * 0.96) * y / length

    crooked_teeth(m, f, width, lambda y: gape / 2 + lift * y / length, length, tooth, per_side, rng, False, across=3)
    if ruff:
        for side in (-1, 1):
            for k in range(ruff):
                a = math.radians(-20 + 130 * k / max(ruff - 1, 1))
                d = Vector((side * math.cos(a), -0.35, math.sin(a)))
                base = (side * skull_w * 0.4, -0.2, gape / 2 + upper_h * 0.3)
                tip_p = Vector(base) + d * ruff_len * rng.uniform(0.8, 1.2)
                blade(m, "Petal" if k % 2 else "PetalDark", f.at(*base), f.at(*tip_p), tuple(f.r @ Vector((-math.sin(a) * side, 0, math.cos(a)))),
                     ruff_len * 0.55)

    hinge = f.at(0, -0.05, -gape / 2)
    m.use(jaw, hinge, head)
    lf = Frame(m, hinge, f.r @ turn(x=-drop))
    ll = length * 0.95
    yloft(lf, lower, (0, 0, -lower_h * 0.55, skull_w * 0.86, lower_h * 1.1), (ll, 0, -lower_h * 0.5, snout_w * 0.92, lower_h))
    yloft(lf, "Mouth", (0, 0, 0.0, skull_w * 0.72, 0.06), (ll * 0.95, 0, 0.0, snout_w * 0.76, 0.06))

    def low_width(y):
        return skull_w * 0.86 + (snout_w * 0.92 - skull_w * 0.86) * y / ll

    crooked_teeth(m, lf, low_width, lambda y: 0.0, ll, tooth * 0.85, per_side, rng, True, across=2)
    if tongue:
        lf.beam("Tongue", (0, ll * 0.1, 0.06), (0, ll * 0.8, 0.08), snout_w * 0.42, 0.1, snout_w * 0.3)
    if sinew:
        for side in (-1, 1):
            beam(m, "Sinew", f.at(side * skull_w * 0.38, length * 0.2, gape / 2 + 0.02), lf.at(side * skull_w * 0.34, length * 0.24, 0.02), 0.08, None, 0.05)
            m.stretch("Sinew", head)
    if ruff:
        for side in (-1, 1):
            for k in range(max(ruff - 1, 1)):
                a = math.radians(-35 - 30 * k)
                d = Vector((side * math.cos(a), -0.2, math.sin(a)))
                base = (side * skull_w * 0.36, 0.05, -lower_h * 0.5)
                blade(m, "PetalDark" if k % 2 else "Petal", lf.at(*base), lf.at(*(Vector(base) + d * ruff_len * rng.uniform(0.7, 1.05))),
                     tuple(lf.r @ Vector((-math.sin(a) * side, 0, math.cos(a)))), ruff_len * 0.5)
    if on_jaw:
        on_jaw(m, lf, ll)
    m.bone = head
    return {"tip": length, "top": lambda y: gape / 2 + upper_h / 2 + lift * y / length + upper_h / 2}


def clawed_leg(m, bone, x, y, top, w, rng, role="Body", low="Accent", toe="Claw", toes=3, reach=0.7):
    """A hunched beast's leg on one bone: a thick thigh, a thin shin, a paw and long hooked claws."""
    m.use(bone, (x, y, top))
    m.loft_z(role, (top * 0.42, x, y, w * 0.62, w * 0.72), (top + 0.15, x, y, w, w * 1.2))
    m.loft_z(low, (0.2, x, y + 0.03, w * 0.5, w * 0.55), (top * 0.46, x, y, w * 0.66, w * 0.76))
    m.loft_z(role, (0, x, y + w * 0.2, w * 0.95, w * 1.1), (w * 0.34, x, y + w * 0.1, w * 0.68, w * 0.78))
    for k in range(toes):
        cx = x + (k - (toes - 1) / 2) * w * 0.34
        thorn(m, toe, (cx, y + w * 0.62, w * 0.18), (cx + rng.uniform(-0.05, 0.05), y + w * 0.62 + reach * w, 0.03), w * 0.22, (0, 0, w * 0.12))
    m.bone = "Spine"


# ---------------------------------------------------------------------- the feral ones


def bramble_brat():
    """A ball of briars that is nearly all mouth, on two stumpy legs. One huge bloodshot eye, one tiny furious one and
    a third on a stalk, a rose growing crooked out of its head, long thorny arms, and a long tongue whipping about."""
    rng = random.Random(1301)
    m = monster("dino_BrambleBrat", Body="#4f7d3c", Accent="#2f5230", Belly="#8fa24e", Claw=BARK_DARK)
    m.joint("Spine", (0, -0.1, 1.1))
    biped_legs(m, 0.62, -0.1, 1.05, 0.62, 0.72, 0.44, 1.05, 0.24)
    m.block("Accent", 0, -0.1, 1.2, 1.5, 1.05, 0.7)
    m.use("Tail1", (0, -1.0, 1.5))
    limb(m, "Briar", [(0, -1.0, 1.5), (0.1, -1.55, 1.2)], 0.3, 0.22)
    m.use("Tail2", (0.1, -1.55, 1.2), "Tail1")
    limb(m, "Briar", [(0.1, -1.55, 1.2), (-0.1, -2.0, 1.25)], 0.22, 0.14)
    m.use("Tail3", (-0.1, -2.0, 1.25), "Tail2")
    limb(m, "Briar", [(-0.1, -2.0, 1.25), (0.05, -2.45, 1.6)], 0.14, 0.05)
    for p, q in (((0.1, -1.55, 1.2), (0.4, -1.8, 1.55)), ((-0.1, -2.0, 1.25), (-0.45, -2.2, 1.6))):
        thorn(m, "Briar", p, q, 0.12)
    m.bone = "Spine"

    r = 1.65
    hinge = (0, -0.75, 2.2)
    top = Frame(m, hinge, turn(x=0.24, y=0.12))  # its skull thrown back and to one side
    low = Frame(m, hinge, turn(x=-0.34, y=-0.08))
    cy = 0.95  # the ball's middle, along the frames' Y
    m.use("Head", (0, -0.4, 1.9))
    half_ball(top, "Body", 0, cy, r)
    top.prism("Mouth", 0, cy, -0.05, 0.02, r * 0.93, r * 0.93, 10)
    ball(m, "Mouth", *top.at(0, 0.75, -0.3), 0.95, 8, 4)
    ball(m, "RoseGlow", *top.at(0, 1.25, -0.5), 0.55, 8, 4)
    for k in range(12):  # teeth round the rim, every one its own
        a = math.radians(-22 + k * 224 / 11)
        px, py = math.cos(a) * r * 0.87, cy + math.sin(a) * r * 0.87
        size = rng.uniform(0.34, 0.62) * (1.5 if k in (3, 8) else 1)
        point(m, "Teeth", top.at(px, py, 0.02), top.at(px * rng.uniform(0.84, 1.06), py + rng.uniform(-0.1, 0.16), -size), 0.3)

    for _ in range(6):  # briars strangling it
        u = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)).normalized()
        v = Vector((-u.y, u.x, 0)) * rng.uniform(-0.5, 0.5) + Vector((0, 0, 1))
        points = [top.at(*(Vector((0, cy, 0)) + (u * math.cos(t) + v.normalized() * math.sin(t)) * r * 1.04)) for t in [math.pi * i / 8 for i in range(9)]]
        vine(m, "Briar", points, 0.2, 0.14, rng, every=0.75, size=0.34)
    for _ in range(26):  # and thorns all over
        d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 0.6), rng.uniform(0.15, 1))).normalized()
        base = Vector((0, cy, 0)) + d * r * 0.95
        thorn(m, "Briar", top.at(*base), top.at(*(base + (d + Vector((rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), rng.uniform(-0.3, 0.5)))).normalized() * rng.uniform(0.35, 0.8))), 0.17)

    big = (Vector((-0.4, 0.8, 0.42))).normalized()
    wild_eye(m, top.at(*(Vector((0, cy, 0)) + big * r * 0.9)), top.r @ Vector((-0.22, 1, -0.02)), 0.74, rng, off=(0.08, -0.06), veins=5, lashes=4)
    small = (Vector((0.46, 0.84, 0.3))).normalized()
    wild_eye(m, top.at(*(Vector((0, cy, 0)) + small * r * 0.98)), top.r @ Vector((0.2, 1, 0.05)), 0.3, rng, off=(-0.2, 0.05), veins=2)
    brow = Vector((0, cy, 0)) + small * r * 1.02
    top.beam("Accent", tuple(brow + Vector((0.3, -0.16, 0.34))), tuple(brow + Vector((-0.34, 0.04, 0.2))), 0.2, 0.2, 0.15)
    rose(m, top.at(0.62, cy - 0.15, r * 0.92), 0.66, top.r @ turn(x=-0.75, y=0.45))

    tip = lash(m, 1, wander(top.at(-0.3, cy - 0.7, r * 0.8), top.at(-1.1, cy - 1.3, r * 2.05), rng, 7, (-0.3, 0.2, 0.1), 0.1), 0.2, 0.09, "Head", "Briar", rng, 0.14)
    wild_eye(m, tuple(tip + Vector((0, 0.05, 0.1))), (0.1, 1, -0.1), 0.3, rng, pupil="Slit", off=(0, 0.1), veins=2)
    lash(m, 2, wander(top.at(0.9, cy - 1.0, r * 0.62), top.at(2.2, cy - 2.0, 1.8), rng, 7, (0.2, 0, 0.5), 0.14), 0.22, 0.05, "Head", "Briar", rng, 0.2)
    lash(m, 3, wander(top.at(-0.9, cy - 0.95, r * 0.5), top.at(-2.4, cy - 1.7, 1.1), rng, 7, (0, 0, 0.5), 0.14), 0.22, 0.05, "Head", "Briar", rng, 0.2)

    m.use("Jaw", hinge, "Head")
    half_ball(low, "Belly", 0, cy, r * 0.96, -1, 10, 3, 0.8)
    low.prism("Mouth", 0, cy, -0.02, 0.05, r * 0.86, r * 0.86, 10)
    for k in range(10):
        a = math.radians(-14 + k * 208 / 9)
        px, py = math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.8
        size = rng.uniform(0.3, 0.55) * (1.45 if k in (1, 7) else 1)
        point(m, "Teeth", low.at(px, py, -0.02), low.at(px * rng.uniform(0.86, 1.05), py + rng.uniform(-0.12, 0.14), size), 0.28)
    for side in (-1, 1):
        beam(m, "Sinew", top.at(side * 1.25, 0.3, 0.02), low.at(side * 1.2, 0.3, 0.02), 0.09, None, 0.06)
        m.stretch("Sinew", "Head")
    for _ in range(9):
        d = Vector((rng.uniform(-1, 1), rng.uniform(-0.6, 1), rng.uniform(-1, -0.25))).normalized()
        base = Vector((0, cy, 0)) + Vector((d.x, d.y, d.z * 0.8)) * r * 0.92
        thorn(m, "Briar", low.at(*base), low.at(*(base + d * rng.uniform(0.3, 0.6))), 0.16)
    # The tongue, a whip of its own, lolling out of one side of the mouth.
    start = low.at(0.1, 0.9, 0.08)
    lash(m, 4, [start, low.at(0.2, 1.6, 0.16), low.at(0.5, 2.25, 0.05), low.at(0.8, 2.75, -0.2), low.at(0.95, 3.05, -0.55), low.at(1.15, 3.1, -0.85), low.at(1.45, 3.0, -0.95)],
         0.38, 0.14, "Jaw", "Tongue")
    m.bone = "Spine"

    for side in (-1, 1):  # long thorny arms, reaching for you
        letter = "L" if side < 0 else "R"
        shoulder = (side * 1.5, 0.15, 1.95)
        m.use(f"Arm{letter}", shoulder)
        elbow = (side * 2.1, 0.5, 1.5)
        wrist = (side * 2.05, 1.5, 1.45 + 0.35 * side)
        vine(m, "Accent", [shoulder, elbow, wrist], 0.34, 0.2, rng, every=0.6, size=0.22)
        for k in (-1, 0, 1):
            thorn(m, "Claw", wrist, (wrist[0] + k * 0.32, wrist[1] + 0.75 - abs(k) * 0.15, wrist[2] + k * 0.1 - 0.12), 0.16, (0, 0, 0.12))
    m.bone = "Spine"
    m.head_centre = (0, 1.1, 2.75)
    return grow(m, 0.92)


def grandma_gnash():
    """The wolf that ate her and kept the clothes: a hunched silver wolf, its back all ragged fur, in a shredded nightcap,
    a torn shawl and bent spectacles. Wild mismatched eyes rolling behind the glasses, a jaw far too wide, briars
    round its legs and the cap's tassel flailing."""
    rng = random.Random(1302)
    m = monster("dino_GrandmaGnash", Body="#8d8aa3", Accent="#54516b", Belly="#c9c6d6", Claw="#201a24", Cap="#cfc5cf", CapTrim="#d9708f",
                Shawl="#a0506e", ShawlDark="#6e2f4a", Rim=GOLD)
    m.joint("Spine", (0, 0, 2.3))
    clawed_leg(m, "FrontL", -0.82, 0.85, 2.6, 0.8, rng)
    clawed_leg(m, "FrontR", 0.82, 0.85, 2.6, 0.8, rng)
    clawed_leg(m, "BackL", -0.66, -1.5, 1.95, 0.72, rng)
    clawed_leg(m, "BackR", 0.66, -1.5, 1.95, 0.72, rng)
    body = ((-1.9, 0, 2.05, 1.15, 1.15), (1.05, 0, 2.75, 1.85, 2.0))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-1.5, 0, 1.45, 0.8, 0.14), (1.05, 0, 1.75, 1.3, 0.2))
    ridge(m, "Accent", along((0, -1.8, top_of(body, -1.8)), (0, 0.9, top_of(body, 0.9)), 15), rng, 0.85, 0.42)
    bristle(m, "Accent", body, rng, 16, 0.6, 0.3, 0.8, (1, 2))
    wrap(m, "Briar", (-0.82, 0.9, 2.2), (-0.82, 0.9, 0.3), 0.36, 2.5, rng)
    wrap(m, "Briar", (0, -1.7, 2.1), (0, 0.1, 2.5), 0.86, 2.5, rng, 0.16, 0.28)
    m.bone = "Spine"
    # The shawl over its shoulders, torn along the bottom.
    a_, b_ = ring_at(*body, -0.35), ring_at(*body, 1.12)
    m.loft_y("Shawl", (-0.35, 0, a_[2] + a_[4] * 0.26, a_[3] + 0.14, a_[4] * 0.6), (1.12, 0, b_[2] + b_[4] * 0.26, b_[3] + 0.14, b_[4] * 0.6))
    for side in (-1, 1):  # its edge in rags, longer at the shoulder
        for k in range(8):
            y = -0.3 + k * 0.2
            r_ = ring_at(*body, y)
            edge = r_[2] + r_[4] * -0.04
            h = rng.uniform(0.35, 0.8) * (0.7 + 0.1 * k)
            m.loft_z("ShawlDark" if k % 3 == 1 else "Shawl", (edge - h, side * (r_[3] / 2 + 0.08), y, 0.04, 0.05), (edge + 0.1, side * (r_[3] / 2 + 0.08), y, 0.06, 0.24))

    m.use("Tail1", (0, -1.85, 2.3))
    pts = [(0, -1.85, 2.3), (0.15, -2.6, 2.1), (-0.1, -3.2, 2.35), (0.1, -3.8, 2.85)]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        if i:
            m.use(f"Tail{i + 1}", a, f"Tail{i}")
        beam(m, "Body", a, b, 0.55 - i * 0.14, None, 0.4 - i * 0.14)
        for _ in range(4):
            c = Vector(a).lerp(Vector(b), rng.random())
            thorn(m, "Accent", c, c + Vector((rng.uniform(-0.4, 0.4), -0.35, rng.uniform(-0.1, 0.5))), 0.2)
    m.bone = "Spine"
    lash(m, 2, wander((0.6, 0.1, 3.5), (2.3, -1.3, 4.5), rng, 7, (0.2, 0, 0.5), 0.15), 0.2, 0.05, "Spine", "Briar", rng, 0.2)
    lash(m, 3, wander((-0.6, -0.5, 3.3), (-2.0, -2.0, 4.1), rng, 7, (-0.2, 0, 0.6), 0.15), 0.2, 0.05, "Spine", "Briar", rng, 0.2)

    m.use("Neck", (0, 1.05, 3.15))
    beam(m, "Body", (0, 0.9, 3.2), (0, 1.75, 3.2), 1.45, 1.45, 1.2)
    m.stretch("Body", "Spine")
    ridge(m, "Accent", along((0, 1.0, 3.9), (0, 1.75, 3.8), 4), rng, 0.6, 0.36)
    w, d, h = 1.6, 1.35, 1.45
    yc, zc = 2.2, 3.2
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    for side in (-1, 1):  # ragged cheek fur
        for k in range(4):
            p = Vector((side * w / 2, yc + 0.1 - k * 0.14, zc - 0.5 + k * 0.28))
            thorn(m, "Accent", p, p + Vector((side * rng.uniform(0.45, 0.8), -0.45, rng.uniform(-0.45, 0.1))), 0.34)

    f = Frame(m, (0, front, zc - 0.48), turn(z=0.08))
    maw(m, f, w, 1.5, 0.95, 0.42, 0.34, rng, gape=0.14, drop=0.36, upper="Body", lower="Accent", tooth=0.3, per_side=6)
    nose = f.at(0, 1.36, 0.6)
    obox(m, "Socket", nose, (0.34, 0.26, 0.2), f.r)

    wild_eye(m, (-0.42, front + 0.04, zc + 0.26), (-0.14, 1, 0.0), 0.4, rng, off=(0.14, -0.08), veins=4)
    wild_eye(m, (0.46, front + 0.04, zc + 0.3), (0.16, 1, 0.05), 0.27, rng, off=(-0.1, 0.16), veins=3)
    for side in (-1, 1):  # brows slamming down to the nose
        beam(m, "Accent", (side * 0.86, front + 0.02, zc + 0.68), (side * 0.06, front + 0.3, zc + 0.3), 0.26, 0.26, 0.2)
    # Her spectacles, bent: one rim round each eye, a bridge, an arm back to the ear.
    hoop(m, "Rim", -0.42, front + 0.46, zc + 0.2, 0.52, 0.08, "xz", 14)
    hoop(m, "Rim", 0.5, front + 0.46, zc + 0.36, 0.4, 0.08, "xz", 14)
    beam(m, "Rim", (0.0, front + 0.46, zc + 0.3), (0.12, front + 0.46, zc + 0.38), 0.08)
    beam(m, "Rim", (-0.93, front + 0.46, zc + 0.22), (-0.84, yc - 0.3, zc + 0.46), 0.07)
    beam(m, "Rim", (0.89, front + 0.46, zc + 0.38), (0.84, yc - 0.2, zc + 0.46), 0.07)

    for side in (-1, 1):  # torn ears through the cap
        base = (side * 0.58, yc - 0.2, zc + h / 2 - 0.05)
        tip = (side * 1.05, yc - 0.65, zc + h / 2 + 1.05)
        plate(m, "Accent", base, tip, (1, 0.8, 0), 0.6, 0.06, 0.14)
        plate(m, "Belly", (side * 0.6, yc - 0.13, zc + h / 2 + 0.05), (side * 0.93, yc - 0.46, zc + h / 2 + 0.72), (1, 0.8, 0), 0.32, 0.04, 0.06)

    # The nightcap: a frilled band, a bag flopping over one side and a tassel flailing on a lash.
    band_z = zc + h / 2 + 0.02
    for k in range(16):
        a = k * math.tau / 16
        px, py = math.cos(a) * 0.9, yc + math.sin(a) * 0.8
        obox(m, "CapTrim", (px, py, band_z), (0.36, 0.1, 0.34), turn(z=a + math.pi / 2, x=rng.uniform(-0.35, 0.35)))
    prism(m, "Cap", 0, yc, band_z - 0.06, band_z + 0.34, 0.86, 0.72, 10)
    x, y, z = 0.0, yc, band_z + 0.32
    for lean, rise, r0, r1 in (((0.04, -0.14), 0.42, 0.72, 0.56), ((-0.1, -0.24), 0.36, 0.56, 0.4), ((-0.24, -0.24), 0.24, 0.4, 0.27)):
        prism(m, "Cap", x, y, z, z + rise, r0, r1, 10, 0, lean)
        x, y, z = x + lean[0], y + lean[1], z + rise
    bag = [(x, y, z)]
    for _ in range(4):  # thorns come through it
        p = Vector((rng.uniform(-0.35, 0.35), yc + rng.uniform(-0.4, 0.3), band_z + rng.uniform(0.3, 0.7)))
        thorn(m, "Briar", p, p + Vector((rng.uniform(-0.8, 0.8), rng.uniform(-0.2, 0.7), rng.uniform(0.2, 0.7))), 0.17)
    tip = lash(m, 1, [bag[-1], (x - 0.32, y - 0.2, z - 0.02), (x - 0.62, y - 0.36, z - 0.28), (x - 0.82, y - 0.48, z - 0.7)], 0.5, 0.14, "Head", "Cap")
    ball(m, "CapTrim", *(tip + Vector((0, 0, -0.14))), 0.26, 6, 4)
    for k in range(5):
        thorn(m, "CapTrim", tip, tip + Vector((rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), -0.55)), 0.12)
    m.bone = "Head"
    m.head_centre = (0, front + 0.3, zc + 0.05)
    return m


def sir_skewer():
    """A suit of armour with nobody in it, only briars, bursting from a hole torn in its chest round a glowing rose. A
    hound-snout visor of steel fangs with two mismatched lights deep inside, one pauldron and no other, a spindle
    as big as a lance, and on its other arm a spinning wheel with thorns round the rim, never stopping."""
    rng = random.Random(1303)
    m = monster("dino_SirSkewer", Body="#a3a9b6", Accent="#5c6172", Belly="#7c8192", Claw="#2c2a34", Cloth="#8c1430", ClothDark="#5e0e22",
                Wheel=WOOD, WheelDark=WOOD_DARK, Spindle="#c9a86a", Trim=GOLD, TrimDark=GOLD_DARK, Thread="#ffb84a")
    m.joint("Spine", (0, 0, 2.7))
    biped_legs(m, 0.6, -0.05, 2.6, 0.66, 1.4, 0.5, 1.25, 0.32, claw=False)
    for side, letter in ((-1, "L"), (1, "R")):  # knee cops with a spike, and steel toes
        x = side * 0.6
        m.bone = f"Leg{letter}"
        m.block("Accent", x, 0.34, 1.68, 0.56, 0.2, 0.56)
        thorn(m, "Accent", (x, 0.42, 1.68), (x + side * 0.1, 1.05, 1.82), 0.34)
        m.bone = f"Shin{letter}"
        for off in (-0.2, 0.0, 0.2):
            thorn(m, "Claw", (x + off, 0.8, 0.16), (x + off * 1.3, 1.25, 0.04), 0.14)
    m.bone = "LegR"
    wrap(m, "Briar", (0.6, 0, 2.6), (0.6, 0, 1.25), 0.42, 2, rng)
    m.bone = "ShinR"
    wrap(m, "Briar", (0.6, -0.05, 1.2), (0.6, 0.05, 0.3), 0.32, 1.5, rng, 0.11, 0.16)
    m.bone = "Spine"

    t = Frame(m, (0, 0, 2.6), turn(x=-0.24, y=0.14))  # the whole torso lurches forward and over
    zloft(t, "Accent", (-0.1, 0, 0, 1.25, 0.95), (0.4, 0, 0, 1.3, 1.0))
    zloft(t, "Body", (0.3, 0, 0, 1.3, 1.0), (1.75, 0, 0.06, 2.1, 1.4))
    zloft(t, "Accent", (1.7, 0, 0.06, 1.7, 1.15), (1.95, 0, 0.06, 1.1, 0.8))
    for k in range(4):  # the skirt of plates at the waist, one hanging off
        x = -0.55 + k * 0.37
        t.box("Belly", x, 0.5, 0.08 - (0.14 if k == 2 else 0), 0.34, 0.08, 0.62)
        t.box("Belly", x, -0.5, 0.08, 0.34, 0.08, 0.62)
    for k, (x, h) in enumerate(((-0.4, 1.0), (0.3, 1.2))):  # the tabard, in rags
        t.box("Cloth", x, 0.58, -0.45, 0.5, 0.06, h)
        for j in (-1, 1):
            zloft(t, "ClothDark" if k else "Cloth", (-1.1 - k * 0.3, x + j * 0.13, 0.58, 0.03, 0.05), (-0.92, x + j * 0.13, 0.58, 0.24, 0.05))

    # The hole torn in its chest: black inside, the steel curling back round it, a rose glowing where a heart was.
    cz, cy = 1.15, 0.76
    slab(t, "Socket", 0.08, cz, cy, 0.68, 0.06, 10)
    for k in range(9):
        a = k * math.tau / 9 + rng.uniform(-0.12, 0.12)
        p = Vector((0.08 + math.cos(a) * 0.62, cy, cz + math.sin(a) * 0.62))
        q = p + Vector((math.cos(a) * rng.uniform(0.2, 0.46), rng.uniform(0.25, 0.5), math.sin(a) * rng.uniform(0.2, 0.46)))
        plate(m, "Body", t.at(*p), t.at(*q), tuple(t.r @ Vector((-math.sin(a), 0, math.cos(a)))), 0.46, 0.05, 0.07)
    rose(m, t.at(0.08, cy + 0.14, cz), 0.5, t.r @ turn(x=-1.4))
    centre = t.at(0.08, cy + 0.02, cz)
    lash(m, 1, wander(t.at(0.5, cy, cz + 0.3), t.at(2.0, cy + 1.6, cz + 1.2), rng, 7, (0.2, 0, 0.5), 0.14), 0.22, 0.05, "Spine", "Briar", rng, 0.2)
    lash(m, 2, wander(t.at(-0.4, cy, cz - 0.4), t.at(-1.7, cy + 1.7, cz - 1.0), rng, 7, (0, 0, -0.3), 0.14), 0.22, 0.05, "Spine", "Briar", rng, 0.2)
    m.bone = "Spine"
    for _ in range(5):  # thick briars out of the hole, straight through the armour
        d = Vector((rng.uniform(-1, 1), rng.uniform(0.3, 1), rng.uniform(-0.9, 0.9))).normalized()
        c = Vector(centre)
        vine(m, "Briar", [tuple(c), tuple(c + d * 0.7 + Vector((0, 0, 0.1))), tuple(c + d * 1.25 + Vector((rng.uniform(-0.2, 0.2), 0, -0.15)))], 0.22, 0.07, rng, every=0.4, size=0.2)
    for _ in range(4):  # and out of every gap
        side = rng.choice((-1, 1))
        p = t.at(side * 0.62, rng.uniform(-0.3, 0.3), 0.2)
        vine(m, "Briar", [p, t.at(side * 1.0, rng.uniform(-0.5, 0.5), rng.uniform(-0.2, 0.3)), t.at(side * 1.35, rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.0))], 0.14, 0.05, rng, every=0.4, size=0.16)

    # A cape on a lash, ripped to one rag.
    tip = lash(m, 4, [t.at(0.1, -0.72, 1.75), t.at(0.05, -0.9, 1.1), t.at(0.15, -1.05, 0.4), t.at(-0.05, -1.25, -0.2), t.at(0.1, -1.4, -0.7), t.at(-0.05, -1.55, -1.1), t.at(0.05, -1.7, -1.4)],
               1.5, 0.75, "Spine", "Cloth", flat=(1, 0, 0))
    for k, (x, length) in enumerate(((-0.28, 0.75), (-0.05, 0.4), (0.15, 0.95), (0.32, 0.55))):  # its torn end
        plate(m, "Cloth" if k % 2 else "ClothDark", tuple(tip + Vector((x, 0, 0.1))), tuple(tip + Vector((x + 0.06, -0.12, -length))), (1, 0, 0), 0.24, 0.02, 0.08)
    m.bone = "Spine"

    # Left: the great pauldron, and the arm carrying the wheel.
    shoulder = t.at(-1.05, 0, 1.55)
    m.use("ArmL", shoulder)
    p = Frame(m, shoulder, t.r @ turn(y=-0.35))
    half_ball(p, "Accent", 0, 0, 0.72, 1, 8, 2, 0.85)
    p.prism("Belly", 0, 0, -0.12, 0.02, 0.8, 0.8, 8)
    for k in range(6):
        a = k * math.tau / 6 + 0.3
        thorn(m, "Claw", p.at(math.cos(a) * 0.48, math.sin(a) * 0.48, 0.45), p.at(math.cos(a) * 0.86, math.sin(a) * 0.86, 1.15 + 0.2 * (k % 2)), 0.26)
    elbow = (shoulder[0] - 0.42, shoulder[1] + 0.15, shoulder[2] - 1.0)
    hand = (elbow[0] - 0.14, elbow[1] + 0.85, elbow[2] + 0.08)
    beam(m, "Body", shoulder, elbow, 0.5, None, 0.42)
    m.block("Accent", *elbow, 0.56, 0.56, 0.56)
    beam(m, "Body", elbow, hand, 0.44, None, 0.5)
    tube(m, "Accent", (hand[0], hand[1], hand[2]), (hand[0] - 0.55, hand[1], hand[2]), 0.14)
    hub = (hand[0] - 0.62, hand[1], hand[2])
    m.use("Cog", hub, "ArmL")
    gear(m, "Wheel", hub, 1.3, 16, 0.2, SIDEWAYS, spokes=8, tooth=0.3)
    wf = Frame(m, hub, SIDEWAYS)
    wf.prism("TrimDark", 0, 0, -0.18, 0.18, 0.26, 0.26, 8)
    wf.prism("Trim", 0, 0, -0.26, -0.16, 0.16, 0.16, 8)
    for k in range(12):  # thorns jammed all round the rim, all raking the same way
        a = k * math.tau / 12
        c = Vector((math.cos(a), math.sin(a), 0))
        tan = Vector((-math.sin(a), math.cos(a), 0))
        thorn(m, "Briar", wf.at(*(c * 1.32)), wf.at(*(c * 1.95 + tan * 0.42)), 0.3)
    m.bone = "Spine"

    # Right: no pauldron, a bundle of briars for a shoulder, and the spindle.
    shoulder = t.at(1.05, 0, 1.5)
    m.use("ArmR", shoulder)
    elbow = (shoulder[0] + 0.45, shoulder[1] - 0.2, shoulder[2] - 0.75)
    hand = (elbow[0] + 0.02, elbow[1] + 0.75, elbow[2] + 0.1)
    for k in range(4):
        off = Vector((rng.uniform(-0.14, 0.14), rng.uniform(-0.14, 0.14), rng.uniform(-0.14, 0.14)))
        vine(m, "Briar", [tuple(Vector(shoulder) + off), tuple(Vector(elbow) + off), tuple(Vector(hand) + off * 0.5)], 0.17, 0.11, rng, every=0.5, size=0.2)
    m.block("Accent", *hand, 0.52, 0.56, 0.44)  # the gauntlet, on nothing but thorns
    for off in (-0.16, 0.0, 0.16):
        m.block("Belly", hand[0] + off, hand[1] + 0.22, hand[2] + 0.2, 0.13, 0.2, 0.14)
    butt = Vector((hand[0] + 0.02, hand[1] - 1.35, hand[2] - 0.5))
    point = Vector((hand[0] + 0.15, hand[1] + 3.8, hand[2] + 1.55))
    d = (point - butt).normalized()
    whorl = butt + d * 1.55
    tube(m, "Spindle", tuple(butt), tuple(whorl), 0.09, 0.22, 6)
    tube(m, "Spindle", tuple(whorl), tuple(whorl + d * 1.2), 0.22, 0.17, 6)
    tube(m, "Spindle", tuple(whorl + d * 1.2), tuple(point), 0.17, 0.015, 6)
    tube(m, "TrimDark", tuple(butt + d * 0.5), tuple(butt + d * 0.66), 0.34, 0.34, 8)
    for k in range(5):  # glowing thread wound round its waist
        c = whorl + d * (0.1 + k * 0.17)
        tube(m, "Thread", tuple(c), tuple(c + d * 0.12), 0.3 - 0.04 * abs(k - 2), 0.3 - 0.04 * abs(k - 2), 8)
    m.bone = "Spine"

    # The helm: a steel bucket, a hound-snout visor that snaps and briars through the top of it.
    neck = t.at(0, 0.04, 1.9)
    m.use("Neck", neck)
    prism(m, "Socket", neck[0], neck[1], neck[2] - 0.1, neck[2] + 0.5, 0.42, 0.4, 8)
    w, d_, h = 1.3, 1.25, 1.2
    yc, zc = neck[1] + 0.42, neck[2] + 0.92
    x0 = neck[0]
    m.head_joint(yc, d_, zc, h)
    m.joints["Head"] = ((x0, yc - d_ * 0.2, zc - h * 0.4), "Neck")
    hf = Frame(m, (x0, yc, zc), turn(y=-0.2, z=0.1))  # head cocked over, looking at you sideways
    hf.box("Body", 0, 0, 0.1, w, d_, h)
    hf.box("Accent", 0, 0, 0.72, w * 0.7, d_ * 0.8, 0.14)
    hf.box("Belly", 0, 0, -0.5, w + 0.08, d_ + 0.08, 0.14)
    # The eye slit, and in it two lights that don't match.
    hf.box("Socket", 0, d_ / 2 + 0.01, 0.4, w * 0.86, 0.04, 0.36)
    eye = Frame(m, hf.at(-0.3, d_ / 2 + 0.03, 0.4), hf.r)
    slab(eye, "EyeGlow", 0, 0, 0.0, 0.17, 0.04, 8)
    slab(eye, "Pupil", 0, 0, 0.03, 0.1, 0.02, 6, 0.3)
    eye = Frame(m, hf.at(0.3, d_ / 2 + 0.03, 0.42), hf.r)
    slab(eye, "EyeGlow", 0, 0, 0.0, 0.11, 0.04, 8)
    slab(eye, "Pupil", 0, 0, 0.03, 0.07, 0.02, 6, 0.3)
    hf.beam("Accent", (-0.68, d_ / 2 + 0.05, 0.72), (0.06, d_ / 2 + 0.12, 0.5), 0.2, 0.18, 0.15)
    hf.beam("Accent", (0.68, d_ / 2 + 0.05, 0.68), (0.1, d_ / 2 + 0.12, 0.5), 0.2, 0.18, 0.15)
    mf = Frame(m, hf.at(0, d_ / 2, -0.26), hf.r)
    maw(m, mf, w * 0.96, 1.2, 0.5, 0.3, 0.26, rng, gape=0.12, drop=0.38, upper="Body", lower="Accent", tooth=0.24, per_side=5, tongue=False)
    for k in range(5):  # breathing holes down the snout
        y = 0.25 + k * 0.17
        mf.box("Socket", -0.3 + 0.3 * (k % 3), y, 0.42 - 0.03 * k, 0.1, 0.1, 0.03)
    for _ in range(4):  # briars through the crown of the helm
        p = hf.at(rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), 0.75)
        q = hf.at(rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 0.2), rng.uniform(1.4, 2.0))
        vine(m, "Briar", [p, tuple(Vector(p).lerp(Vector(q), 0.5) + Vector((0, 0, 0.2))), q], 0.16, 0.03, rng, every=0.4, size=0.14)
    lash(m, 3, wander(hf.at(0.2, -0.3, 0.75), hf.at(1.4, -1.7, 2.3), rng, 7, (0.2, 0, 0.4), 0.12), 0.18, 0.05, "Head", "Briar", rng, 0.17)
    m.bone = "Head"
    head = hf.at(0, d_ / 2 + 0.5, 0.05)
    m.head_centre = tuple(head)
    return grow(m, 0.98)


# ---------------------------------------------------------------------- the fierce ones


def deer_leg(m, bone, x, y, top, w, rng):
    """A long thin leg on one bone: a lean thigh, a bony shank wound with thorns, a split black hoof."""
    m.use(bone, (x, y, top))
    knee = top * 0.5
    m.loft_z("Body", (knee, x, y, w * 0.5, w * 0.62), (top + 0.2, x, y, w, w * 1.3))
    m.loft_z("Accent", (0.42, x, y + 0.08, w * 0.3, w * 0.34), (knee + 0.1, x, y, w * 0.52, w * 0.66))
    m.block("Accent", x, y + 0.03, knee, w * 0.62, w * 0.78, w * 0.5)
    for off in (-1, 1):
        m.loft_z("Claw", (0.0, x + off * w * 0.2, y + 0.18, w * 0.3, w * 0.62), (0.46, x + off * w * 0.06, y + 0.08, w * 0.2, w * 0.3))
    thorn(m, "Briar", (x, y + 0.1, knee), (x + rng.uniform(-0.2, 0.2), y + 0.8, knee + 0.3), 0.2)
    m.bone = "Spine"


def hart_attack():
    """A stag with a bare skull for a face and nothing behind its ribs but a burning rose. Vast crooked antlers of black
    briar hung with roses and spare eyes, a mane of shards down its neck, snapped arrows still in its flank."""
    rng = random.Random(1304)
    m = monster("dino_HartAttack", Body="#5e1f36", Accent="#2a1220", Belly="#e6dcc4", Claw="#1a1418", Shaft=WOOD, Fletch="#d8d2c8")
    m.joint("Spine", (0, 0, 3.4))
    deer_leg(m, "FrontL", -0.66, 1.25, 3.5, 0.72, rng)
    deer_leg(m, "FrontR", 0.66, 1.25, 3.5, 0.72, rng)
    deer_leg(m, "BackL", -0.6, -1.75, 3.4, 0.8, rng)
    deer_leg(m, "BackR", 0.6, -1.75, 3.4, 0.8, rng)
    rump = ((-2.3, 0, 3.75, 1.1, 1.35), (-0.55, 0, 3.8, 1.35, 1.6))
    chest = ((0.95, 0, 3.95, 1.45, 1.85), (1.75, 0, 4.1, 1.25, 1.75))
    m.loft_y("Body", *rump)
    m.loft_y("Body", *chest)
    m.loft_y("Socket", (-0.7, 0, 4.25, 0.4, 0.4), (1.05, 0, 4.35, 0.44, 0.44))
    ball(m, "RoseGlow", 0, 0.2, 3.8, 0.66, 8, 5)
    rose(m, (0, 0.2, 3.72), 0.7, turn(x=-0.3))
    # The open ribs round it: bare bone, an empty cage either side.
    y = -0.45
    while y < 0.95:
        for side in (-1, 1):
            z_top, z_low = 4.68, 3.0
            limb(m, "Belly", [(side * 0.15, y, z_top), (side * 0.78, y + 0.04, z_top - 0.3), (side * 0.98, y + 0.12, 3.85), (side * 0.74, y + 0.2, z_low + 0.3), (side * 0.2, y + 0.26, z_low + 0.05)],
                 0.15, 0.07)
        y += 0.46
    m.loft_y("Belly", (-0.7, 0, 4.72, 0.3, 0.2), (1.1, 0, 4.76, 0.34, 0.2))  # the backbone
    ridge(m, "Briar", along((0, -2.2, 4.42), (0, -0.5, 4.6), 7), rng, 0.8, 0.26)
    bristle(m, "Briar", rump, rng, 8, 0.6, 0.2, 0.7, (1, 2))
    wrap(m, "Briar", (-0.3, -0.5, 3.8), (0.3, 1.0, 3.9), 0.96, 2, rng, 0.14, 0.22)
    # Snapped arrows.
    for p, d in (((0.68, -1.5, 4.05), (0.8, 0.25, 0.55)), ((0.7, -1.1, 3.55), (0.9, -0.2, 0.25)), ((-0.72, 1.3, 4.4), (-0.75, -0.2, 0.7))):
        p, d = Vector(p), Vector(d).normalized()
        beam(m, "Shaft", tuple(p - d * 0.1), tuple(p + d * 1.15), 0.08)
        for k in (0.7, 0.86):
            q = p + d * k
            plate(m, "Fletch", tuple(q), tuple(q + d * 0.16), (0, 1, 0), 0.34, 0.2, 0.03)
    tail = [(0, -2.25, 4.1), (0.05, -2.65, 4.3), (-0.08, -2.95, 4.2), (0.03, -3.2, 4.45)]
    for i, (a, b) in enumerate(zip(tail, tail[1:])):
        m.use(f"Tail{i + 1}", a, f"Tail{i}" if i else "Spine")
        beam(m, "Briar", a, b, 0.32 - i * 0.08, None, 0.22 - i * 0.08)
        thorn(m, "Briar", b, Vector(b) + Vector((rng.uniform(-0.3, 0.3), -0.3, 0.35)), 0.14)
    m.bone = "Spine"

    m.use("Neck", (0, 1.6, 4.5))
    beam(m, "Body", (0, 1.45, 4.3), (0, 2.75, 5.55), 1.25, 1.35, 0.72)
    m.stretch("Body", "Spine")
    ridge(m, "Accent", along((0, 1.55, 5.1), (0, 2.5, 6.0), 8), rng, 1.0, 0.34, 0.8)
    ridge(m, "Briar", along((0.2, 1.7, 5.0), (0.15, 2.5, 5.75), 4), rng, 0.8, 0.2, 0.8)
    for side in (-1, 1):
        thorn(m, "Accent", (side * 0.5, 2.1, 4.75), (side * 1.0, 1.7, 4.3), 0.34)
        thorn(m, "Accent", (side * 0.42, 2.4, 5.05), (side * 0.95, 2.05, 4.7), 0.3)

    w, d, h = 1.25, 1.2, 1.15
    yc, zc = 3.0, 5.85
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    hf = Frame(m, (0, yc, zc), turn(x=-0.18, y=-0.1))  # head low and crooked, coming at you
    zloft(hf, "Belly", (-h / 2, 0, 0, w * 0.86, d), (h / 2, 0, -0.04, w, d * 0.94))
    mf = Frame(m, hf.at(0, d / 2, -0.36), hf.r)
    maw(m, mf, w * 0.82, 1.55, 0.56, 0.42, 0.28, rng, gape=0.12, drop=0.34, upper="Belly", lower="Belly", tooth=0.3, per_side=6, tongue=False)
    for side in (-1, 1):  # the nose holes of a skull
        beam(m, "Socket", mf.at(side * 0.09, 1.0, 0.62), mf.at(side * 0.16, 1.48, 0.55), 0.14, 0.05, 0.09)
    cracks = [hf.at(-0.5, d / 2 + 0.01, 0.56), hf.at(-0.22, d / 2 + 0.03, 0.42), hf.at(-0.3, d / 2 + 0.03, 0.22)]
    limb(m, "Socket", cracks, 0.05, 0.03)
    size = 0.4
    glare(m, hf.at(-0.34, d / 2 - 0.02, 0.2), hf.r @ Vector((-0.12, 1, 0)), size, 1, 0.55, brow="Accent", spikes=1)
    glare(m, hf.at(0.34, d / 2 - 0.02, 0.22), hf.r @ Vector((0.12, 1, 0)), size * 0.8, -1, 0.55, brow="Accent", spikes=1)
    # Spare eyes crowding up its brow.
    for x, z, r_ in ((-0.1, 0.5, 0.12), (0.16, 0.5, 0.09)):
        wild_eye(m, hf.at(x, d / 2 + 0.0, z), hf.r @ Vector((x, 1, 0.1)), r_, rng, pupil="Slit", role="Socket", veins=0, iris=0.74)

    # The antlers: a great crooked tree of briar each side, never matching.
    def antler(side, points, tines, w0):
        p0 = hf.at(*points[0])
        pts = [hf.at(*p) for p in points]
        limb(m, "Briar", pts, w0, 0.09)
        for i, length, dx, dy, dz in tines:
            a, b = Vector(pts[i]), Vector(pts[i + 1])
            base = a.lerp(b, 0.6)
            t_ = base + hf.r @ Vector((side * dx, dy, dz)) * length
            mid = base.lerp(t_, 0.55) + hf.r @ Vector((side * 0.1, 0.1, 0.1)) * length
            limb(m, "Briar", [tuple(base), tuple(mid), tuple(t_)], w0 * 0.62, 0.05)
            thorn(m, "Briar", tuple(mid), tuple(mid + hf.r @ Vector((side * 0.4, -0.3, 0.4))), 0.18)
            thorn(m, "Briar", tuple(base), tuple(base + hf.r @ Vector((-side * 0.35, 0.3, 0.45))), 0.2)
        return p0

    m.bone = "Head"
    left = [(-0.4, -0.2, 0.52), (-0.95, -0.5, 1.25), (-1.6, -0.45, 2.1), (-1.85, -0.9, 3.0), (-2.75, -1.0, 3.75), (-3.0, -1.5, 4.6)]
    antler(-1, left, [(0, 1.3, 0.5, 1.0, 0.3), (1, 1.5, 0.8, 0.5, 0.45), (2, 1.45, -0.2, 1.0, 0.6), (3, 1.2, 0.9, 0.2, 0.2), (4, 1.0, -0.6, 0.6, 0.5), (1, 1.1, -0.5, -0.8, 0.4)], 0.6)
    right = [(0.4, -0.2, 0.52), (0.85, -0.55, 1.1), (1.5, -0.6, 1.75), (1.75, -1.15, 2.6), (2.35, -1.15, 3.05)]
    antler(1, right, [(0, 1.2, 0.6, 0.9, 0.2), (1, 1.3, 0.9, 0.3, 0.6), (2, 1.35, -0.5, 0.9, 0.7), (3, 1.1, 0.7, -0.5, 0.5)], 0.54)
    rose(m, hf.at(-1.6, -0.45, 2.1), 0.62, hf.r @ turn(x=-1.0, y=-0.4))
    rose(m, hf.at(1.5, -0.6, 1.75), 0.5, hf.r @ turn(x=-1.1, y=0.6))
    wild_eye(m, hf.at(-0.95, -0.2, 1.3), hf.r @ Vector((-0.3, 1, 0.1)), 0.24, rng, pupil="Slit", role="Socket", veins=0, iris=0.7)
    wild_eye(m, hf.at(1.75, -0.95, 2.6), hf.r @ Vector((0.3, 1, 0.1)), 0.22, rng, pupil="Slit", role="Socket", veins=0, iris=0.7)
    lash(m, 1, wander(hf.at(2.35, -1.15, 3.05), hf.at(3.6, -1.2, 2.0), rng, 7, (0.3, 0, 0.5), 0.12), 0.14, 0.04, "Head", "Briar", rng, 0.16)
    lash(m, 2, wander(hf.at(-1.85, -0.9, 3.0), hf.at(-3.5, -0.7, 2.0), rng, 7, (-0.2, 0, 0.3), 0.12), 0.15, 0.04, "Head", "Briar", rng, 0.16)
    lash(m, 3, wander(hf.at(0.2, -0.5, 0.5), hf.at(0.9, -2.2, 1.5), rng, 7, (0, 0, 0.4), 0.12), 0.16, 0.05, "Head", "Briar", rng, 0.17)
    m.bone = "Head"
    m.head_centre = tuple(hf.at(0, d / 2 + 0.4, 0))
    return grow(m, 0.92)


def snapper(m, n, at_point, look, s, rng, eyes=1):
    """One of Hydrangry's spare heads, on the end of whip n: a bud of a skull with a jaw on its own Snap bone, a ruff of
    petals peeling back from its mouth, one or two eyes. Its bone is whatever m.bone is."""
    head = m.bone
    f = Frame(m, at_point, aim(look))
    d = s * 1.0
    f.box("Body", 0, 0, 0.08 * s, s * 1.1, d, s * 1.05)
    mf = Frame(m, f.at(0, d / 2, -0.3 * s), f.r)
    maw(m, mf, s * 1.05, s * 1.05, s * 0.6, s * 0.3, s * 0.24, rng, gape=0.1 * s, drop=0.4, upper="Body", lower="Accent", tooth=0.22 * s, per_side=4, head=head,
        jaw=f"Snap{n}", tongue=True, ruff=4, ruff_len=s * 1.05, sinew=False)
    m.bone = head
    if eyes == 1:
        glare(m, f.at(0.05 * s, d / 2 - 0.02, 0.3 * s), f.r @ Vector((0, 1, 0.05)), 0.44 * s, 1, 0.35, pupil="Slit", brow="Accent", spikes=1)
    else:
        wild_eye(m, f.at(-0.3 * s, d / 2 - 0.04, 0.3 * s), f.r @ Vector((-0.2, 1, 0.1)), 0.3 * s, rng, pupil="Slit", veins=2, off=(0.1, -0.1))
        wild_eye(m, f.at(0.3 * s, d / 2 - 0.04, 0.34 * s), f.r @ Vector((0.2, 1, 0.1)), 0.2 * s, rng, pupil="Slit", veins=1, off=(-0.2, 0.1))
    for k in range(3):
        a = 0.6 + k * 0.9
        p = f.at(math.cos(a) * s * 0.4, -d * 0.2, s * 0.56)
        thorn(m, "Briar", p, f.at(math.cos(a) * s * 0.75, -d * 0.45, s * (1.05 + 0.12 * k)), 0.2 * s)


def hydrangry():
    """A heap of violet roots and crimson blooms with five heads on writhing necks, all snapping at once: the big one in
    the middle on the Neck, Head and Jaw bones, the four others each on the end of a whip with a jaw of its own."""
    rng = random.Random(1305)
    m = monster("dino_Hydrangry", Body="#6a4aa0", Accent="#35235c", Belly="#9a6fc4", Claw="#1f1626", Floret="#e04a78", FloretB="#a02a5e")
    m.joint("Spine", (0, 0, 2.2))
    for bone, x, y, top in (("FrontL", -1.45, 1.1, 2.0), ("FrontR", 1.45, 1.1, 2.0), ("BackL", -1.4, -1.3, 2.0), ("BackR", 1.4, -1.3, 2.0)):
        m.use(bone, (x, y, top))
        s = 1 if x > 0 else -1
        limb(m, "Accent", [(x * 0.8, y * 0.8, top + 0.3), (x * 1.05, y * 1.1, top * 0.6), (x * 1.3, y * 1.35, 0.32)], 0.95, 0.5)
        for k in range(4):  # roots clawing out of each foot
            a = math.atan2(y, x) + (k - 1.5) * 0.55
            d = Vector((math.cos(a), math.sin(a), 0))
            base = Vector((x * 1.3, y * 1.35, 0.3))
            limb(m, "Claw", [tuple(base), tuple(base + d * 0.55 + Vector((0, 0, -0.1))), tuple(base + d * 1.05 + Vector((0, 0, -0.28)))], 0.3, 0.05)
    m.bone = "Spine"
    body = Frame(m, (0, 0, 2.8))
    ball(m, "Body", 0, 0, 2.8, 2.3, 10, 6)
    ball(m, "Belly", 0, 1.3, 2.25, 1.15, 8, 5)
    for _ in range(26):
        d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.3, 1))).normalized()
        thorn(m, "Briar", body.at(*(d * 2.15)), body.at(*(d * rng.uniform(2.7, 3.2) + Vector((rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), 0.1)))), 0.26)
    for k in range(7):  # veins of briar over the heap
        a = k * math.tau / 7 + rng.uniform(-0.2, 0.2)
        pts = []
        for i in range(6):
            lat = -0.35 + i * 0.3
            aa = a + i * 0.28
            pts.append(body.at(math.cos(aa) * math.cos(lat) * 2.34, math.sin(aa) * math.cos(lat) * 2.34, math.sin(lat) * 2.34))
        vine(m, "Briar", pts, 0.2, 0.12, rng, every=0.9, size=0.28)
    for p, r_ in (((-1.75, 0.55, 3.9), 1.1), ((1.85, 0.15, 3.65), 1.2), ((0.5, -1.8, 4.0), 1.05), ((-1.3, -1.5, 3.0), 0.95), ((1.5, 1.6, 2.2), 0.86), ((-1.8, 1.55, 2.3), 0.8)):
        puff(m, p, r_, rng)
    for k in range(9):  # big ragged leaves round its base
        a = k * math.tau / 9 + rng.uniform(-0.15, 0.15)
        d = Vector((math.cos(a), math.sin(a), 0))
        base = d * 1.9 + Vector((0, 0, 1.3))
        blade(m, "Leaf" if k % 2 else "LeafDark", tuple(base), tuple(base + d * 1.6 + Vector((0, 0, -0.75))), (-d.y, d.x, 0), 1.0)

    # The big head, in the middle.
    m.use("Neck", (0, 0.9, 4.4))
    limb(m, "Body", [(0, 0.5, 4.2), (0.25, 1.05, 5.3), (-0.2, 0.95, 6.4), (0, 1.55, 7.3)], 1.25, 0.9)
    ridge(m, "Briar", [(0.3, 0.6, 5.2), (-0.1, 0.45, 6.0), (-0.3, 0.6, 6.8), (0.1, 0.8, 7.3)], rng, 0.8, 0.26, 0.8)
    w, d, h = 1.7, 1.5, 1.5
    yc, zc = 2.0, 7.55
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    hf = Frame(m, (0, yc, zc), turn(x=-0.2, y=0.12))
    hf.box("Body", 0, 0, 0, w, d, h)
    mf = Frame(m, hf.at(0, d / 2, -0.52), hf.r)
    maw(m, mf, w, 1.5, 0.95, 0.42, 0.36, rng, gape=0.14, drop=0.4, upper="Body", lower="Accent", tooth=0.34, per_side=6, ruff=6, ruff_len=1.5)
    glare(m, hf.at(-0.42, d / 2 - 0.02, 0.3), hf.r @ Vector((-0.1, 1, 0)), 0.5, 1, 0.6, spikes=2)
    glare(m, hf.at(0.44, d / 2 - 0.02, 0.34), hf.r @ Vector((0.1, 1, 0)), 0.4, -1, 0.6, spikes=2)
    m.bone = "Head"
    for k in range(8):  # thorns along its crown
        p = hf.at(rng.uniform(-0.65, 0.65), rng.uniform(-0.6, 0.5), h / 2)
        thorn(m, "Briar", p, Vector(p) + Vector((rng.uniform(-0.45, 0.45), rng.uniform(-0.7, 0.0), rng.uniform(0.6, 1.2))), 0.26)
    rose(m, hf.at(-0.1, -0.5, h / 2 + 0.15), 0.6, hf.r @ turn(x=-0.5, y=-0.5))
    m.head_centre = tuple(hf.at(0, d / 2 + 0.5, -0.05))

    # The four others, on whips, each looking a bit its own way.
    spare = (
        (1, (-1.0, 0.85, 4.5), (-3.3, 2.0, 5.9), (-0.8, 0.4, 1.0), (-0.3, 1, 0.1), 1.0, 1),
        (2, (1.0, 0.85, 4.4), (3.3, 2.1, 5.3), (0.9, 0.2, 1.0), (0.3, 1, 0.0), 1.05, 2),
        (3, (-0.55, -0.25, 4.8), (-1.9, 1.3, 8.2), (-0.7, -0.5, 0.5), (-0.2, 1, 0.3), 0.85, 2),
        (4, (0.7, -0.15, 4.8), (2.0, 1.2, 7.6), (0.8, -0.5, 0.3), (0.25, 1, 0.25), 0.92, 1),
    )
    for n, start, end, bow, look, s, eyes in spare:
        tip = lash(m, n, wander(start, end, rng, 7, bow, 0.16), 0.62 * s, 0.42 * s, "Spine", "Body", rng, 0.24, 0.6)
        snapper(m, n, tuple(tip + Vector(look).normalized() * 0.35 * s), look, s, rng, eyes)
    m.bone = "Spine"
    return grow(m, 1.08)


def wrathorn():
    """The boss: the sleeping king, a dragon now. A black thorn-bark tyrant up on its knuckles, wings of crimson blades,
    rose fire veining its hide, a rusted crown jammed down on crooked horns, five eyes, a mace of thorns on its tail, a
    ring of petals burning round its crown, and in its chest a second mouth: a ring of teeth grinding for ever round a
    burning rose."""
    rng = random.Random(1306)
    m = monster("dino_Wrathorn", Body="#43334f", Accent="#221829", Belly="#8c1f3c", Claw="#e2dacb", Crown=GOLD, CrownDark=GOLD_DARK, CrownGem=ROSE,
                Blade=PETAL, BladeDark=PETAL_DARK)
    m.joint("Spine", (0, 0, 5.8))
    for bone, x, y, top, w_ in (("FrontL", -2.2, 2.0, 6.6, 1.5), ("FrontR", 2.2, 2.0, 6.6, 1.5), ("BackL", -1.85, -2.3, 5.5, 1.75), ("BackR", 1.85, -2.3, 5.5, 1.75)):
        s = 1 if x > 0 else -1
        clawed_leg(m, bone, x, y, top, w_, rng, reach=0.75)
        m.bone = bone
        for k in range(3):
            z = top * (0.82 - 0.2 * k)
            p = Vector((x + s * w_ * 0.42, y - 0.1, z))
            thorn(m, "Accent", p, p + Vector((s * 0.9, -0.55, 0.65)), 0.5)
        m.bone = "Spine"
    body = ((-3.3, 0, 5.6, 2.6, 2.7), (2.7, 0, 6.5, 3.7, 4.1))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-2.9, 0, 4.25, 1.9, 0.16), (2.65, 0, 4.48, 2.7, 0.2))
    m.loft_z("Belly", (4.5, 0, 2.72, 2.9, 0.1), (8.4, 0, 2.72, 2.6, 0.1))
    # The chest maw: a rose at its heart, a ring of teeth on its own Drill bone, and thorns round the mouth of it.
    c = (0, 2.86, 6.45)
    cf = Frame(m, c, turn())
    slab(cf, "Socket", 0, 0, -0.08, 1.62, 0.08, 14)
    rose(m, (0, 3.0, 6.45), 0.85, turn(x=-math.pi / 2))
    for k in range(14):
        a = k * math.tau / 14
        p = Vector((math.cos(a) * 1.62, 0, math.sin(a) * 1.62))
        thorn(m, "Briar", cf.at(*p), cf.at(*(p * 1.5 + Vector((0, 0.8, 0)))), 0.46)
    m.use("Drill", c)
    for r_, count, length in ((1.45, 14, 0.75), (1.1, 12, 0.55)):
        for k in range(count):
            a = k * math.tau / count + r_
            p = Vector((math.cos(a) * r_, 0.0, math.sin(a) * r_))
            inward = Vector((-math.cos(a) * 0.6, 0.65, -math.sin(a) * 0.6)).normalized()
            point(m, "Teeth", cf.at(*p), cf.at(*(p + inward * length * (1.15 if k % 2 else 0.85))), 0.34)
    hoop_points = [cf.at(math.cos(k * math.tau / 14) * 1.5, -0.03, math.sin(k * math.tau / 14) * 1.5) for k in range(15)]
    for a, b in zip(hoop_points, hoop_points[1:]):
        beam(m, "Accent", a, b, 0.3)
    m.bone = "Spine"

    # Rose fire veining its hide.
    def veins(side):
        x = side * 1.82
        for start in ((1.5, 7.8), (0.3, 7.4), (-1.0, 6.9), (-2.1, 6.3)):
            y, z = start
            pts = []
            for i in range(5):
                half = ring_at(*body, y)[3] / 2
                pts.append((side * (half + 0.03), y, z))
                y += rng.uniform(-0.55, 0.15)
                z -= rng.uniform(0.3, 0.55)
            for a, b in zip(pts, pts[1:]):
                beam(m, "RoseGlow", a, b, 0.11)
            k = pts[2]
            beam(m, "RoseGlow", k, (k[0], k[1] + 0.5, k[2] - 0.35), 0.08)

    veins(-1)
    veins(1)
    ridge(m, "Briar", along((0, -3.1, top_of(body, -3.1)), (0, 2.4, top_of(body, 2.4)), 15), rng, 1.9, 0.72, 0.6)
    bristle(m, "Accent", body, rng, 26, 1.1, 0.42, 0.7)
    wrap(m, "Briar", (0, -3.1, 5.6), (0, 2.4, 6.4), 2.0, 3, rng, 0.22, 0.42)
    m.bone = "Spine"

    # Tail: a long ridge of shards and a mace of thorns round a burning rose.
    pts = [(0, -3.2, 5.8), (0.3, -5.2, 5.6), (-0.3, -7.2, 5.0), (0.15, -8.8, 5.3)]
    widths = (2.1, 1.35, 0.8, 0.5)
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        m.use(f"Tail{i + 1}", a, f"Tail{i}" if i else "Spine")
        beam(m, "Body", a, b, widths[i], None, widths[i + 1])
        if i:
            m.stretch("Body", f"Tail{i}")
        ridge(m, "Briar", along((a[0], a[1], a[2] + widths[i] * 0.45), (b[0], b[1], b[2] + widths[i + 1] * 0.45), 4), rng, 1.3 - 0.25 * i, 0.5 - 0.1 * i, 0.5)
    mace = Vector((0.15, -9.2, 5.4))
    ball(m, "Accent", *mace, 0.8, 8, 5)
    ball(m, "RoseGlow", *(mace + Vector((0, -0.45, 0.42))), 0.4, 6, 4)
    for k in range(16):
        z = 1 - 2 * (k + 0.5) / 16
        a = k * 2.4
        d = Vector((math.sqrt(1 - z * z) * math.cos(a), math.sqrt(1 - z * z) * math.sin(a), z))
        thorn(m, "Claw", tuple(mace + d * 0.7), tuple(mace + d * rng.uniform(1.4, 1.9)), 0.34)
    m.bone = "Spine"

    # Wings: a briar arm, and a fan of crimson blades, ragged and uneven, some gone.
    for letter, side in (("L", -1), ("R", 1)):
        shoulder = (side * 1.6, 1.0, 8.2)
        m.use(f"Wing{letter}", shoulder)
        elbow = (side * 5.2, 0.1, 11.0 + (0.5 if side > 0 else 0))
        limb(m, "Accent", [shoulder, (side * 3.2, 0.9, 10.2), elbow], 0.8, 0.45)
        thorn(m, "Claw", elbow, (side * 5.5, 0.5, 12.3), 0.42)
        m.use(f"WingTip{letter}", elbow, f"Wing{letter}")
        fingers = [(side * 8.6, -0.8, 9.6), (side * 8.0, -1.3, 7.2), (side * 6.8, -1.6, 5.0), (side * 4.9, -1.5, 3.8)]
        for tip_ in fingers:
            limb(m, "Accent", [elbow, tuple(Vector(elbow).lerp(Vector(tip_), 0.55) + Vector((0, 0, 0.25))), tip_], 0.34, 0.06)
        e = Vector(elbow)
        for k in range(9):
            if rng.random() < 0.14:
                continue  # a blade torn away
            t = k / 8
            a = fingers[min(int(t * 3), 2)]
            b = fingers[min(int(t * 3) + 1, 3)]
            tip_ = Vector(a).lerp(Vector(b), (t * 3) % 1 if t < 1 else 1) * rng.uniform(0.8, 1.02) + Vector((0, 0, 0.3))
            tip_ = e + (tip_ - e) * rng.uniform(0.82, 1.03)
            tip_.y = e.y - 1.2  # every blade leaning back the same way, so the fan's blades lie parallel and never cross
            # Each behind the last by more than a blade is thick, so no two cut through each other (they flickered at 0.07).
            base = e + Vector((0, 0.18 * k, 0))
            blade(m, "BladeDark" if k % 2 else "Blade", tuple(base), tuple(tip_ + Vector((0, 0.18 * k, 0))), (0, 0.15, 1) if abs(tip_.z - e.z) < 2 else (1, 0.1, 0), 1.35, 0.1 + 0.06 * (k % 2))
    m.bone = "Spine"

    lash(m, 1, wander((1.2, 1.3, 8.4), (3.2, 1.8, 12.4), rng, 7, (0.4, 0, 0.3), 0.2), 0.42, 0.08, "Spine", "Briar", rng, 0.42, 0.75)
    lash(m, 2, wander((-1.2, 1.2, 8.4), (-3.4, 2.4, 11.6), rng, 7, (-0.4, 0, 0.4), 0.2), 0.42, 0.08, "Spine", "Briar", rng, 0.42, 0.75)
    lash(m, 3, wander((1.0, -2.0, 7.2), (3.4, -4.2, 9.6), rng, 7, (0.4, 0, 0.5), 0.2), 0.38, 0.08, "Spine", "Briar", rng, 0.4, 0.75)
    lash(m, 4, wander((-1.0, -2.0, 7.2), (-3.3, -4.6, 8.9), rng, 7, (-0.3, 0, 0.6), 0.2), 0.38, 0.08, "Spine", "Briar", rng, 0.4, 0.75)
    m.bone = "Spine"

    # The neck, up and over, thick with thorns.
    m.use("Neck", (0, 2.2, 8.0))
    neck = [(0, 1.8, 7.6), (0.05, 2.5, 9.3), (0.25, 2.75, 10.6), (-0.05, 3.7, 11.4)]
    widths = (2.3, 1.7, 1.4, 1.3)
    for i, (a, b) in enumerate(zip(neck, neck[1:])):
        beam(m, "Body", a, b, widths[i], None, widths[i + 1])
    for a, b, w0, w1 in (((0.02, 3.2, 8.0), (0.08, 3.28, 9.4), 1.1, 0.8), ((0.08, 3.28, 9.4), (0.2, 3.5, 10.5), 0.8, 0.65)):
        beam(m, "Belly", a, b, w0, 0.14, w1)  # the crimson plates down its throat
    ridge(m, "Briar", [(0, 1.7, 9.3), (0.2, 1.95, 10.0), (-0.1, 2.05, 10.8), (0.1, 2.5, 11.5), (-0.1, 3.0, 11.9)], rng, 1.5, 0.6, 0.8)
    for side in (-1, 1):
        beam(m, "RoseGlow", (side * 0.84, 2.35, 9.0), (side * 0.72, 2.6, 10.1), 0.1)
        beam(m, "RoseGlow", (side * 0.72, 2.6, 10.1), (side * 0.66, 3.1, 10.9), 0.09)

    w, d, h = 2.4, 2.3, 2.1
    yc, zc = 4.6, 11.7
    m.head_joint(yc, d, zc, h)
    hf = Frame(m, (0, yc, zc), turn(x=-0.14, y=-0.1))  # jammed down and to one side, under the crown
    hf.box("Body", 0, 0, 0, w, d, h)
    hf.box("Accent", 0, -0.1, h / 2 + 0.05, w * 0.8, d * 0.8, 0.14)
    mf = Frame(m, hf.at(0, d / 2, -0.8), hf.r)
    maw(m, mf, w, 2.4, 1.4, 0.68, 0.54, rng, gape=0.24, drop=0.4, upper="Body", lower="Accent", tooth=0.55, per_side=7, tongue=False, lift=0.16, ruff=0)
    for side in (-1, 1):  # smouldering nostrils
        beam(m, "RoseGlow", mf.at(side * 0.38, 2.12, 0.98), mf.at(side * 0.44, 2.38, 0.94), 0.2, 0.12, 0.16)
    glare(m, hf.at(-0.66, d / 2 - 0.02, 0.5), hf.r @ Vector((-0.12, 1, 0)), 0.62, 1, 0.65, spikes=2)
    glare(m, hf.at(0.68, d / 2 - 0.02, 0.56), hf.r @ Vector((0.12, 1, 0)), 0.48, -1, 0.65, spikes=2)
    wild_eye(m, hf.at(-w / 2 + 0.05, 0.75, 0.32), hf.r @ Vector((-1, 0.5, 0)), 0.24, rng, pupil="Slit", role="Socket", veins=0, iris=0.74)
    wild_eye(m, hf.at(w / 2 - 0.05, 0.8, 0.42), hf.r @ Vector((1, 0.5, 0)), 0.2, rng, pupil="Slit", role="Socket", veins=0, iris=0.74)
    wild_eye(m, hf.at(0.02, d / 2, 0.9), hf.r @ Vector((0, 1, 0.3)), 0.15, rng, pupil="Slit", role="Socket", veins=0, iris=0.74)
    # Crooked horns, the crown jammed down over them.
    m.bone = "Head"
    for side, top_, lean in ((-1, (-2.3, -2.0, 3.6), (-1.6, -0.6, 2.4)), (1, (1.9, -2.5, 2.7), (1.45, -1.1, 1.7))):
        base = hf.at(side * 0.75, -0.5, h / 2 - 0.1)
        mid = hf.at(*lean)
        tip = hf.at(*top_)
        limb(m, "Briar", [base, mid, tip], 0.68, 0.05)
        thorn(m, "Briar", mid, Vector(mid) + hf.r @ Vector((side * 0.7, 0.7, 0.5)), 0.3)
    for k in range(6):
        p = hf.at(side * rng.uniform(0.2, 1.0), -d / 2 + 0.1, rng.uniform(-0.3, 0.8))
        q = hf.at(rng.uniform(-1.4, 1.4), -d / 2 - 1.4, rng.uniform(-0.1, 1.2))
        thorn(m, "Briar", p, q, 0.34)
    ring = Frame(m, hf.at(0.1, -0.1, h / 2 + 0.14), hf.r @ turn(y=0.22, x=0.1))
    spikes = 8
    for k in range(spikes):
        a = k * math.tau / spikes
        b = (k + 1) * math.tau / spikes
        r_ = 1.08
        pa = (math.cos(a) * r_, math.sin(a) * r_)
        pb = (math.cos(b) * r_, math.sin(b) * r_)
        ring.beam("Crown", (pa[0], pa[1], 0.15), (pb[0], pb[1], 0.15), 0.34, 0.42)
        if k == 5:
            continue  # one point snapped off
        h_ = 0.8 + 0.3 * (k % 2)
        ring.beam("CrownDark" if k % 2 else "Crown", (pa[0], pa[1], 0.2), (pa[0] * 1.1, pa[1] * 1.1, 0.2 + h_), 0.32, 0.32, 0.03)
    ball(m, "CrownGem", *ring.at(0.2, 1.1, 0.22), 0.2, 6, 4)
    ball(m, "CrownGem", *ring.at(-0.9, 0.55, 0.22), 0.16, 6, 4)
    # Glowing petals circling the crown, for ever, on the Key bone.
    m.use("Key", hf.at(0, -0.1, h / 2 + 1.0), "Head")
    o = Vector(hf.at(0, -0.1, h / 2 + 1.0))
    for k in range(10):
        a = k * math.tau / 10
        d_ = Vector((math.cos(a), math.sin(a), 0))
        t_ = Vector((-d_.y, d_.x, 0.25 * (-1) ** k))
        p = o + d_ * 2.4 + Vector((0, 0, 0.45 if k % 2 else -0.35))
        blade(m, "PetalGlow", tuple(p - t_ * 0.5), tuple(p + t_ * 0.7), (0, 0, 1), 0.62)
    m.bone = "Head"
    m.head_centre = tuple(hf.at(0, d / 2 + 0.9, -0.1))
    return grow(m, 0.92)


ALL = [bramble_brat, grandma_gnash, sir_skewer, hart_attack, hydrangry, wrathorn]


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
        root.location = (i * 26, 0, 0)
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
        kit.shoot(scene, f"{model.name}_back", centre + Vector((-0.75, -0.7, 0.4)) * reach * 0.95, centre, (640, 640), 50)
        head = root.location + Vector(model.head_centre)
        size = max(3.2, model.head_centre[2] * 0.6)
        kit.shoot(scene, f"{model.name}_face", head + Vector((0.55, 1.0, 0.14)) * size * 1.5, head, (640, 640), 50)
        kit.shoot(scene, f"{model.name}_front", head + Vector((0, 1, 0.1)) * size * 1.6, head, (640, 640), 50)
    kit.set_visible(roots, roots)
    for model in models:
        print(f"  {model.name}: {sum(len(x) - 2 for _, f in model.parts.values() for x in f)} triangles, {len(model.joints)} bones, "
              f"biggest {max((len(f), r) for r, (_, f) in model.parts.items())}, "
              f"box {[round(min(v[i] for vs, _ in model.parts.values() for v in vs), 1) for i in range(3)]} to "
              f"{[round(max(v[i] for vs, _ in model.parts.values() for v in vs), 1) for i in range(3)]}")


def main():
    builders = ALL
    only = os.environ.get("ONLY")
    if only:
        builders = [b for b in builders if b.__name__ in only.split(",")]
    models = [b() for b in builders]
    if os.environ.get("QUICK"):
        quick_preview(models, Path(os.environ.get("QUICK_OUT", str(RENDERS / "quick"))))
        return
    build_and_render(models, RENDERS, HERE / f"{BLEND}.blend", "thorn_kingdom_animation_preview.mp4", sky=SKY, ground=FLOOR,
                     glow_roles=GLOW_ROLES, spacing=18, animate_fn=animate, walk_frames=WALK_PREVIEW, glow=GLOW)


if __name__ == "__main__":
    main()
