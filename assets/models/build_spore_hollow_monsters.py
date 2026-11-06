"""Builds Spore Hollow's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_spore_hollow_monsters.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_spore_hollow_monsters.py    (stills only, for trying faces)
    ONLY=toad_rage,sporantula QUICK=1 ...                                      (just those)

Saves spore_hollow_monsters.blend and renders to design/world/monsters_spore_hollow/: stills of each, the lineup, and
two videos, spore_hollow_animation_preview.mp4 (all six walking and roaring, as on every map) and
spore_hollow_pounce_preview.mp4 (each in turn close up, through its pounce). The map's props are in build_spore_hollow.py.

Map 14, a hollow at the bottom of the world where no sun ever reached and the fungus grew as big as castles. The owner
first asked for monsters "very aggressive and nice, more aggressive than the 13th map". The first six came out toy-like
(round eyes with a flat bar of a pupil that read sleepy, red caps with yellow spots that read like a game's power-up,
small mouths, upright poses), and on 2026-11-06 the owner said they didn't like them at all and wanted them **more scary
and aggressive**. So these are the same six, by name and by rig, rebuilt from scratch to frighten.

The idea: down here the rot is the predator. It has eaten into everything that lives in the hollow and is wearing it.
Every one of them is dark and rotten, with bone-pale teeth, claws and spikes, crusts of pale mycelium bursting out of
the hide (as the real fungus does on the ants it takes), black caps with gills glowing chartreuse under them, and none
of them stands up straight: they crouch, hunch and reach, heads low and thrust at you. They share two things:

  The rot glare. No white in any eye. A burning chartreuse iris with a thin upright slit, sunk in a black socket under a
  slab of brow slanting hard down to the nose, glowing threads of mycelium creeping out of it over the face; and spare
  eyes burst up through the hide round the main ones, little black beads with the same burning slit.
  The rot maw. The mouth is most of the face: a jaw hanging wide open, two rows of long needle teeth leaning inwards,
  the roof of the mouth a mushroom's underside with gills glowing back to a glowing throat, and glowing strings of
  mycelium stretched between the jaws like drool.

  Toad Rage       a bloated black cave toad crouched to spring, its head nearly all mouth. Two burning eyes on bumps
                  under warty brows and more bursting up beside them, a row of bone spikes down its back, black ink caps
                  and shelf fungi growing out of it, two warts torn open and pouring spores, and mycelium whips lashing
                  from its rump. Splayed hands of long hooked claws
  Morel Panic     a gaunt, ash-pale crawler on four long limbs, its knees and elbows higher than its back, ribs showing,
                  long black-clawed fingers reaching. Its head is under a black morel pulled down like a hood, every
                  pit glowing ember-orange and something looking out of a few of them; under the brim two burning eyes
                  and a long jaw hanging open in a scream
  Antagonist      a black ant reared up on four legs, its front pair raised to grab. Huge serrated mandibles spread wide
                  round a mouth of needles, burning compound eyes under ridged brows, white mycelium bursting out of every
                  joint, a sting curled over its back, and out of the back of its head the fungus that took it: a pale
                  stalk arching over it to dangle a glowing club in front of its face
  Sporantula      a black spider, its front legs raised high over its head to strike, bone knuckles on every joint, two
                  burning eyes and six more in a cluster, huge bone fangs dripping glowing venom that never stop working,
                  and a swollen abdomen marked with glowing chevrons, black caps bursting out of it and spores pouring out
  Gillotine       a towering ash-pale mantis in a black executioner's hood of a cap, its gills glowing down over its
                  burning eyes. Two great serrated blades raised high, side jaws round a mouth of needles, and behind it
                  its wings stood up in a threat display, each with a huge glaring eye
  Shroomageddon   the boss: a colossal black titan on its knuckles, more rot than beast. A ragged black cap pulled down
                  over its head like a hood, seven burning eyes under it, bone horns and glowing morels for a crown, and
                  a mouth that opens four ways, wide enough to swallow a house. Its chest is torn open on a glowing heart
                  behind ribs of bone, a forest of black and deathly pale mushrooms grows on its back round a geyser of
                  spores, mycelium whips thrash from its shoulders, and its tail ends in a club of bone spikes

What moves is unchanged from the first six, so the game needs no new code. The usual walk, idle and roar, map 13's
thrashing (Lash and Snap bones: THRASH in DinoLifeController, thrash_of in build_thorn_kingdom_monsters.py), and two
things of this map's, in DinoLifeController (VENT, POUNCE) and here (vent_rise, pounce_of), the same numbers in both:
  - Vent<n> bones: a column of spore clouds over a vent in the hide, lifted one VENT_GAP every VENT_PERIOD and
    dropped back, so spores pour out for ever (each cloud only goes as far as where the one above it began). The
    clouds are added after grow(), so the gap is the same on every monster.
  - A monster with Vent bones pounces once every 4 seconds: it rears back, front legs up and side jaws spread, then
    lunges, neck down, jaw flung open, arms raking, side jaws slamming shut, and slowly draws back. The side jaws
    (MandL, MandR) gnash the rest of the time and open wide in the roar.
Everything repeats every 4 seconds, so the preview's 4-stride walk and 8-second idle loop seamlessly.

Rules the game adds: Jaw sits in front of Tail1 (or the Spine), since that's how the game tells which way a monster
faces. Only the main eyes use the Pupil role, which the reveal aims at; spare eyes use Slit. A bone the game looks for
must carry a mesh (the importer drops empty bones).

Glowing parts are EyeGlow, GillGlow, Vein, Spore, Glow, Pit and HeartGlow (Neon in the game, shared/Roles.luau, all there
already). Skin roles Body, Accent, Belly and Claw take the colour mutations; caps, stalks, mycelium, spore clouds and the
face keep their colour. Built at the first map's size; the game scales them by Config/Biomes standardScale. 1 Blender
unit = 1 stud, models face +Y, feet on Z = 0. No five- or six-pointed stars or crosses anywhere (ruled out on map 10),
and no gore: it's a kids' game, so nothing bleeds and the insides you see are bone and fungus.

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
from build_clockwork_citadel_monsters import fcurves_of  # noqa: E402,F401
from build_desert import beam  # noqa: E402
from build_eclipse_temple_monsters import grow  # noqa: E402
from build_forest import Model  # noqa: E402
from build_spore_hollow import CLOUD, CLOUD_SPORES, GILL, SPORE, VEIN, bracket, cap, share  # noqa: E402
from build_starfall_crater import ball  # noqa: E402
from build_thorn_kingdom_monsters import (W, WALK_PREVIEW, aim, along, point, ridge, slab, thorn, thrash_of, wander,  # noqa: E402
                                          yloft, zloft)
from build_volcano import idle_pose as volcano_idle, prism, ring_at, roar, walk_pose as volcano_walk  # noqa: E402
from map_kit import limb, plate  # noqa: E402
from monster_stage import build_and_render, light_up, set_sky  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_spore_hollow"
BLEND = "spore_hollow_monsters"  # for check_map.py and export_fbx.py

GLOW_ROLES = {"EyeGlow", "GillGlow", "Vein", "Spore", "Glow", "Pit", "HeartGlow"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket", "Slit"})
GLOW_STRENGTH = 1.0  # the glowing roles' strength in the renders

ROT_CAP, ROT_CAP_DARK = "#3c2a32", "#241920"  # black caps, bruised
PALE_CAP, PALE_CAP_DARK = "#d9d0b9", "#b0a58a"  # deathly pale caps
FACE = {"Pupil": "#0b0806", "Slit": "#0b0806", "Socket": "#060403", "EyeGlow": "#d2ff2c", "EyeWhite": "#e6e0c6", "Highlight": "#ffffff",
        "Mouth": "#110a08", "Teeth": "#efe6cc", "Tongue": "#3a1c22", "GillGlow": GILL, "Vein": VEIN, "Spore": SPORE, "Glow": "#b8ff3a",
        "Puff": "#9da17b", "PuffB": "#747b58", "Puffskin": "#4a4236", "Cap": ROT_CAP, "CapDark": ROT_CAP_DARK, "CapB": PALE_CAP,
        "CapBDark": PALE_CAP_DARK, "Stalk": "#d4c9ad", "Mycel": "#ddd5bf", "Shelf": "#4b3a30", "ShelfDark": "#30241d"}
SKY, FLOOR = "#14120e", "#4a3830"


def monster(name, **colours):
    m = Model(name, {**FACE, **colours})
    m.vents = []  # asked for while building, made by finish()
    return m


# ---------------------------------------------------------------------- how they pounce and puff

VENT_GAP, VENT_PERIOD = 0.6, 0.8  # studs at the model's own size and seconds: DinoLifeController VENT


def smooth(u):
    return u * u * (3 - 2 * u)


def pulse(s, start, rise, hold, fall):
    """0, easing up to 1 over rise seconds from start, held for hold, easing back to 0 over fall; once every 4 seconds."""
    t = (s - start) % 4
    if t < rise:
        return smooth(t / rise)
    t -= rise
    if t < hold:
        return 1.0
    t -= hold
    if t < fall:
        return 1 - smooth(t / fall)
    return 0.0


def rearing(s):
    """Rearing back, before the lunge."""
    return pulse(s, 0.15, 0.5, 0.15, 0.12)


def lunging(s):
    """The lunge, and drawing slowly back."""
    return pulse(s, 0.8, 0.12, 0.22, 0.6)


def pounce_of(name, s):
    """What a bone adds for the pounce, s seconds in; the same as POUNCE in DinoLifeController."""
    c, h = rearing(s), lunging(s)
    if name == "Spine":
        return 0.06 * c - 0.08 * h, 0, 0
    if name == "Neck":
        return 0.2 * c - 0.4 * h, 0, 0
    if name == "Head":
        return 0.14 * c + 0.2 * h, 0, 0
    if name == "Jaw":
        return -0.12 * c - 0.7 * h, 0, 0
    if name in ("MandL", "MandR"):
        side = 1 if name == "MandL" else -1
        return 0, 0, side * ((0.1 + 0.08 * math.sin(8 * W * s)) * (1 - h) + 0.5 * c)
    if name in ("ArmL", "ArmR"):
        return -0.3 * c + 0.9 * h, 0, 0
    if name in ("FrontL", "FrontR"):
        return 0.3 * c - 0.06 * h, 0, 0
    if name in ("WingL", "WingR"):
        return 0, (0.35 if name == "WingL" else -0.35) * c, 0
    if name == "Tail1":
        return 0.14 * c - 0.06 * h, 0, 0
    return None


def vent_rise(s):
    return VENT_GAP * ((s / VENT_PERIOD) % 1)


# Bones the walk and the idle pose first, so the thrashing and the pounce add to them; any other bone takes them whole.
POSED = {"Spine", "Neck", "Head", "Jaw", "ArmL", "ArmR", "FrontL", "FrontR", "BackL", "BackR", "Tail1", "Tail2", "Tail3",
         "WingL", "WingR", "WingTipL", "WingTipR", "MandL", "MandR"}


def feral(a, f):
    """Adds the thrashing and the pounce to the pose just set, and lifts the vents."""
    s = f / 30
    for bone in a.pose.bones:
        name = bone.name
        if name.startswith("Vent"):
            kit.pose_bone(a, name, (0, 0, 0), (0, 0, vent_rise(s)), f)
            continue
        parts = [p for p in (thrash_of(name, s), pounce_of(name, s)) if p]
        if not parts:
            continue
        extra = [sum(p[i] for p in parts) for i in range(3)]
        if name in POSED:
            extra = [bone.rotation_euler[i] + extra[i] for i in range(3)]
        kit.pose_bone(a, name, tuple(extra), None, f)


def walk_pose(a, f):
    volcano_walk(a, f)
    for name in ("MandL", "MandR"):
        kit.pose_bone(a, name, (0, 0, 0), None, f)
    feral(a, f)


def idle_pose(a, f):
    volcano_idle(a, f)
    t = 2 * math.pi * f / kit.IDLE_FRAMES
    for letter, side in (("L", -1), ("R", 1)):  # the wings' idle, which the Volcano's has no need of
        kit.pose_bone(a, f"Wing{letter}", (0, side * 0.07 * math.sin(4 * t), 0), None, f)
        kit.pose_bone(a, f"WingTip{letter}", (0, side * 0.06 * math.sin(4 * t - 0.8), 0), None, f)
    for name, side in (("MandL", 1), ("MandR", -1)):  # side jaws flung open in the roar (DinoLifeController ROAR)
        kit.pose_bone(a, name, (0, 0, side * 0.6 * roar(t)), None, f)
    feral(a, f)


def animate(armature):
    """The Volcano's walk and idle (jaw snap and roar), with map 13's thrashing and this map's pounce on top, and the
    vents lifting their clouds."""
    walk = kit.add_action(armature, "Walk", WALK_PREVIEW, walk_pose, 2)
    idle = kit.add_action(armature, "Idle", kit.IDLE_FRAMES, idle_pose, 2)
    return walk, idle


# ---------------------------------------------------------------------- shapes


def up_along(direction):
    """A frame's turn that points its +Z along direction."""
    return Vector(direction).normalized().to_track_quat("Z", "Y").to_matrix()


def on_ball(f, r, theta, azim):
    """A point on a ball of radius r round frame f's origin: theta from its +Y (where it looks), azim round that."""
    return f.at(r * math.sin(theta) * math.cos(azim), r * math.cos(theta), r * math.sin(theta) * math.sin(azim))


def egg(m, role, centre, rx, ry, rz, sides=10, rings=6):
    """A chunky ellipsoid round centre, rx across, ry along and rz up."""
    c = Vector(centre)
    verts = [tuple(c - Vector((0, 0, rz)))]
    for k in range(1, rings):
        lat = -math.pi / 2 + k * math.pi / rings
        for i in range(sides):
            a = i * math.tau / sides
            verts.append(tuple(c + Vector((rx * math.cos(lat) * math.cos(a), ry * math.cos(lat) * math.sin(a), rz * math.sin(lat)))))
    verts.append(tuple(c + Vector((0, 0, rz))))
    top = len(verts) - 1
    faces = [[0, 1 + (i + 1) % sides, 1 + i] for i in range(sides)]
    for k in range(rings - 2):
        a0, a1 = 1 + k * sides, 1 + (k + 1) * sides
        faces += [[a0 + i, a0 + (i + 1) % sides, a1 + (i + 1) % sides, a1 + i] for i in range(sides)]
    last = 1 + (rings - 2) * sides
    faces += [[last + i, last + (i + 1) % sides, top] for i in range(sides)]
    m._add(role, verts, faces)


def on_egg(centre, rx, ry, rz, x, y):
    """The height of an egg()'s top at (x, y), or None off its edge."""
    k = 1 - (x / rx) ** 2 - ((y - centre[1]) / ry) ** 2
    return centre[2] + rz * math.sqrt(k) if k > 0 else None


def sprout(m, base, direction, h, r, cap_r, cap_h, rng, cap_role="Cap", crown="CapDark", under="GillGlow", shape="bell", stalk="Stalk",
           sides=8):
    """A mushroom bursting out of the monster at base, along direction: a stalk h long and a cap on it, gills glowing
    under it. Returns the cap's frame."""
    d = Vector(direction).normalized()
    top = Vector(base) + d * h
    tube(m, stalk, tuple(base), tuple(top + d * cap_h * 0.42), r, r * 0.8, 6 if r < 0.2 else 8)  # ending clear of the cap's slices (no flicker)
    # A rim at least 0.045 deep, so the glowing gills under even a tiny cap sit clear of its edge (no flicker).
    return cap(m, cap_role, tuple(top), cap_r, cap_h, shape, up_along(d), sides, crown, under, max(0.045, cap_h * 0.16))


def jointed_leg(m, points, w, role="Belly", ring="Claw", tip="Claw", taper=0.5):
    """A long thin leg through points (hip, joints, foot): segments tapering from w, a bony knob at each joint and a
    pointed tip for a foot."""
    n = len(points) - 1
    for i, (a, b) in enumerate(zip(points, points[1:])):
        wa = w * (1 - (1 - taper) * i / n)
        wb = w * (1 - (1 - taper) * (i + 1) / n)
        a, b = Vector(a), Vector(b)
        if i == n - 1:
            mid = a.lerp(b, 0.55)
            beam(m, role, tuple(a), tuple(mid), wa, None, wb * 1.1)
            point(m, tip, tuple(mid - (b - a).normalized() * 0.05), tuple(b), wb * 1.25)
        else:
            beam(m, role, tuple(a), tuple(b), wa, None, wb)
            ball(m, ring, *b, wb * 0.72, 6, 3)


def tendril(m, n, points, w0, w1=0.06, parent="Spine", role="Mycel", beads="Glow", every=2, tip=None, tip_size=None):
    """A whip through points on three bones, Lash<n>a, b and c, which never stop thrashing (thrash_of): a mycelium
    tendril, a fungal stalk, a thread of silk. beads: a glowing role for knots along it; tip: a role for a bulb on its
    end. Leaves m.bone on its last bone, so more can go on the end; returns the end point."""
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
        beam(m, role, a, b, wa, None, wb)
        if first and before != parent:
            m.stretch(role, before)
        if beads and i % every == every - 1 and i < segments - 1:
            obox(m, beads, b, (wb * 1.7, wb * 1.7, wb * 1.7), turn(0.5 * i, 0.8 * i, 0.3 * i))
    if tip:
        ball(m, tip, *points[-1], tip_size or w1 * 2.4, 6, 4)
    return Vector(points[-1])


def crust(m, centre, normal, size, rng, count=5, role="Mycel"):
    """A crust of pale mycelium bursting out of the hide at centre, facing normal: a clump of little turned blocks, as the
    fungus does at the joints of the ants it takes."""
    c, n = Vector(centre), Vector(normal).normalized()
    for _ in range(count):
        off = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))
        off -= n * off.dot(n)
        p = c + off * size * 0.55 + n * size * rng.uniform(0.0, 0.22)
        s = size * rng.uniform(0.35, 0.6)
        obox(m, role, tuple(p), (s, s * 0.8, s * 0.8), aim(n) @ turn(rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), rng.uniform(0, 3)))


def ragged_cap(m, role, centre, r, h, rot, rng, crown=None, under="GillGlow", shape="bell", tatters=12, length=0.35, sides=14):
    """A cap pulled down like a hood, its rim torn into ragged points hanging down all round. Returns its frame."""
    f = cap(m, role, centre, r, h, shape, rot, sides, crown, under, max(0.06, h * 0.12))
    for k in range(tatters):
        a = (k + rng.uniform(-0.25, 0.25)) * math.tau / tatters
        base = f.at(math.cos(a) * r * 0.97, math.sin(a) * r * 0.97, -h * 0.05)
        tip = f.at(math.cos(a) * r * 1.02, math.sin(a) * r * 1.02, -length * r * rng.uniform(0.6, 1.3))
        plate(m, role, base, tip, f.r @ Vector((-math.sin(a), math.cos(a), 0)), r * math.tau / tatters * 0.9, 0.04, 0.08)
    return f


def claw_hand(m, wrist, ahead, size, side, role="Body", claw="Claw", fingers=4, splay=0.9, lift=0.25):
    """A long-fingered hand from the wrist, the fingers spread ahead with their knuckles up and curling down to the
    ground, a long hooked claw on each."""
    w = Vector(wrist)
    a = Vector(ahead).normalized()
    s = a.cross(Vector((0, 0, 1))).normalized()
    palm = w + a * size * 0.6
    beam(m, role, tuple(w), tuple(palm), size * 0.55, size * 0.25, size * 0.75)
    for k in range(fingers):
        t = k / (fingers - 1) - 0.5
        d = (a + s * t * splay).normalized()
        base = palm + s * t * size * 0.6
        knuckle = base + d * size * 0.7 + Vector((0, 0, size * lift))
        tip = knuckle + d * size * 0.5 + Vector((0, 0, -size * 0.42))
        limb(m, role, [tuple(base), tuple(knuckle), tuple(tip)], size * 0.17, size * 0.11)
        hook = tip + d * size * 0.5 + Vector((0, 0, -size * 0.18))
        thorn(m, claw, tuple(tip), tuple(hook), size * 0.14, tuple(Vector((0, 0, size * 0.08))))
    return palm


# ---------------------------------------------------------------------- the spore vents


def vent(m, n, base, parent="Spine", size=0.4, count=4, lips="Puffskin"):
    """Asks for spore vent n at base, on bone parent: finish() makes it, after grow(). lips: the role of the torn lips
    round its glowing hole, or None for spores rising straight off a tip."""
    m.vents.append((n, Vector(base), parent, size, count, lips))


def build_vent(m, k, n, base, parent, size, count, lips):
    """A torn vent (on the parent bone, still) and over it, on bone Vent<n>, a column of spore clouds VENT_GAP apart,
    each a little smaller than the one below, glowing spores caught in them. DinoLifeController lifts the bone one gap
    every VENT_PERIOD and drops it back, so the clouds pour out for ever."""
    rng = random.Random(1400 + n)
    b, s = base * k, size * k
    m.bone = parent
    if lips:
        hole = s * 0.6
        prism(m, "Glow", b.x, b.y, b.z - hole * 0.8, b.z + 0.01, hole, hole * 0.86, 8, math.pi / 8)
        for j in range(7):
            a = j * math.tau / 7 + rng.uniform(-0.2, 0.2)
            d = Vector((math.cos(a), math.sin(a), 0))
            foot = b + d * hole * 1.02 - Vector((0, 0, hole * 0.65))
            tip = foot + d * hole * 0.45 + Vector((0, 0, hole * rng.uniform(0.8, 1.15)))
            plate(m, lips, tuple(foot), tuple(tip), (-d.y, d.x, 0), hole * 0.95, hole * 0.3, hole * 0.2)
    m.use(f"Vent{n}", tuple(b), parent)
    for i in range(count):
        c = s * (1 - 0.12 * i)
        z = b.z + VENT_GAP * (i + 0.45)
        co, si = math.cos(1.3 * i + n), math.sin(1.3 * i + n)
        for j, (dx, dy, dz, f) in enumerate(CLOUD):
            rx, ry = dx * co - dy * si, dx * si + dy * co
            m.block("PuffB" if j == 3 else "Puff", b.x + rx * c, b.y + ry * c, z + dz * c, c * f, c * f, c * f * 0.85)
        for dx, dy, dz in CLOUD_SPORES:
            rx, ry = dx * co - dy * si, dx * si + dy * co
            g = max(0.07, c * 0.18)
            m.block("Spore", b.x + rx * c, b.y + ry * c, z + dz * c, g, g, g)
    m.bone = parent


def finish(m, k=1.0):
    """Grows the monster by k (the rarer ones stand bigger), then makes its vents, whose clouds keep VENT_GAP apart."""
    if k != 1.0:
        grow(m, k)
    for spec in m.vents:
        build_vent(m, k, *spec)
    m.bone = "Spine"
    return m


# ---------------------------------------------------------------------- the rot glare and the rot maw


def rot_eye(m, centre, look, size, inner, slant=0.6, pupil="Pupil", brow="Accent", rng=None, veins=3, lid=True, horns=0, horn_role="Claw"):
    """The rot glare: no white at all, a burning chartreuse iris with a thin upright slit sunk in a black socket, under a
    slab of brow slanting hard down to the nose (inner is +1 if the nose lies at +X), a lid squeezing it from below and
    glowing threads of mycelium creeping out of the socket over the face. horns: bone spikes out of the brow's far end."""
    rng = rng or random.Random(int(size * 1000) + int(inner * 7))
    f = Frame(m, centre, aim(look) @ turn(y=inner * slant * 0.5))
    slab(f, "Socket", 0, 0, 0.03, size * 0.56, 0.08, 10, 1.45)
    slab(f, "EyeGlow", 0, -size * 0.05, 0.09, size * 0.4, 0.05, 10, 1.1)
    slab(f, pupil, 0, -size * 0.05, 0.125, size * 0.35, 0.03, 8, 0.16)
    f.box("Highlight", -size * 0.17, 0.15, size * 0.1, size * 0.09, 0.02, size * 0.09)
    b = Frame(m, centre, aim(look))
    for k in range(veins):  # threads out of the socket, down and out over the cheek
        a = math.radians(-150 + 120 * k / max(veins - 1, 1) + rng.uniform(-12, 12))
        if inner > 0:
            a = math.pi - a
        p = Vector((math.cos(a) * size * 0.7, 0.035, math.sin(a) * size * 0.5))
        pts = [p]
        for _ in range(2):
            a += rng.uniform(-0.45, 0.45)
            p = p + Vector((math.cos(a) * size * 0.4, 0.0, math.sin(a) * size * 0.4))
            pts.append(p)
        for p, q in zip(pts, pts[1:]):
            beam(m, "Vein", b.at(*p), b.at(*q), size * 0.07, None, size * 0.045)
    out, nose = -inner * size * 1.0, inner * size * 0.85
    drop = slant * size
    b.beam(brow, (out, 0.1, size * 0.5 + drop * 0.5), (nose, 0.22, size * 0.4 - drop * 0.65), size * 0.46, size * 0.52, size * 0.34)
    if lid:
        b.beam(brow, (out * 0.9, 0.1, -size * 0.52), (nose * 0.9, 0.12, -size * 0.58), size * 0.26, size * 0.18, size * 0.2)
    for k in range(horns):
        t = 0.06 + 0.3 * k
        p = Vector((out + (nose - out) * t, 0.08, size * 0.72 + drop * 0.45 * (1 - t)))
        tip = p + Vector((-inner * size * 0.5, -size * 0.4, size * (0.9 - 0.25 * k)))
        thorn(m, horn_role, b.at(*p), b.at(*tip), size * 0.26)


def bead(m, centre, look, r, pupil="Slit"):
    """A spare eye burst up through the hide: a black bead, a burning iris and a thin upright slit."""
    f = Frame(m, centre, aim(look))
    ball(m, "Socket", *centre, r, 8, 4)
    slab(f, "EyeGlow", 0, 0, r * 0.92, r * 0.68, r * 0.12, 10)
    slab(f, pupil, 0, 0, r * 0.99, r * 0.58, r * 0.06, 8, 0.2)
    f.box("Highlight", -r * 0.3, r * 1.02, r * 0.3, r * 0.16, r * 0.03, r * 0.16)


def orb(m, centre, look, r, inner, pupil="Pupil", brow="Accent", slant=0.65):
    """A great bulging eye (an ant's, a mantis's): a glossy black ball, a burning iris and a thick upright slit, under a
    ridge of brow slanting down to the middle (inner is +1 if the middle lies at +X)."""
    f = Frame(m, centre, aim(look))
    ball(m, "Socket", *centre, r, 8, 5)
    slab(f, "EyeGlow", 0, -r * 0.05, r * 0.9, r * 0.6, r * 0.14, 12)
    slab(f, pupil, 0, -r * 0.05, r * 0.98, r * 0.52, r * 0.06, 8, 0.2)
    f.box("Highlight", -r * 0.32, r * 1.0, r * 0.3, r * 0.15, r * 0.03, r * 0.15)
    f.beam(brow, (-inner * r * 1.15, r * 0.3, r * (0.75 + 0.3 * slant)), (inner * r * 0.8, r * 0.85, r * (0.55 - 0.45 * slant)), r * 0.5, r * 0.42,
           r * 0.34)


def needles(m, lf, width_at, edge_at, length, tooth, per_side, rng, up, across=3, thin=0.36, fang=-2):
    """Long thin teeth along a jaw in frame lf, none the same, leaning in towards the throat, with one fang much longer
    near the front of each side. width_at(y) and edge_at(y) give the jaw there; up points them up."""
    sign = 1 if up else -1
    for side in (-1, 1):
        for i in range(per_side):
            y = length * (0.08 + 0.86 * i / max(per_side - 1, 1))
            big = i == per_side + fang
            size = tooth * rng.uniform(0.7, 1.2) * (1.8 if big else 1)
            x = side * (width_at(y) / 2 - tooth * 0.2)
            edge = edge_at(y)
            point(m, "Teeth", lf.at(x, y, edge - sign * 0.04),
                  lf.at(x - side * rng.uniform(0.0, 0.25) * size, y + rng.uniform(-0.2, 0.3) * size, edge + sign * size * rng.uniform(1.15, 1.6)),
                  tooth * thin * (1.35 if big else 1))
    for k in range(across):
        x = (k + 0.5 - across / 2) * width_at(length) / max(across, 1) * 0.85
        size = tooth * rng.uniform(0.75, 1.15)
        point(m, "Teeth", lf.at(x, length * 0.97, edge_at(length) - sign * 0.04),
              lf.at(x + rng.uniform(-0.15, 0.15) * size, length + rng.uniform(0.0, 0.3) * size, edge_at(length) + sign * size * rng.uniform(1.0, 1.4)),
              tooth * thin)


def mandible(m, f, side, x0, y0, z0, length, width, rng, teeth=5, height=None, curl=1.0, role="Claw", parent="Head"):
    """A side jaw on bone Mand<L/R>, hinged at (side * x0, y0, z0) in frame f: a blade bowing out and curling in to a
    point in front of the mouth, teeth along its inner edge. height makes it a deep plate (a jaw) rather than a
    pincer. DinoLifeController swings it open round the upright."""
    m.use(f"Mand{'L' if side < 0 else 'R'}", f.at(side * x0, y0, z0), parent)
    height = height or width
    tip_x = 0.08 + width * 0.2 + (1 - curl) * x0

    def at(t):
        x = (x0 + length * 0.3 * math.sin(math.pi * t)) * (1 - curl * t * t) + tip_x * curl * t * t
        return Vector((side * x, y0 + length * t, z0 - length * 0.06 * t))

    pts = [at(i / 6) for i in range(7)]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        wa = width * (1 - 0.55 * i / 6)
        wb = width * (1 - 0.55 * (i + 1) / 6)
        beam(m, role, f.at(*a), f.at(*b), wa, height * (1 - 0.6 * i / 6), wb)
    point(m, role, f.at(*pts[-1]), f.at(*(pts[-1] + (pts[-1] - pts[-2]).normalized() * width * 1.4)), width * 0.45)
    for k in range(teeth):  # along the inner edge, pointing in
        t = 0.28 + 0.62 * k / max(teeth - 1, 1)
        p = at(t)
        inward = Vector((-side, 0.25, -0.15)).normalized()
        size = width * rng.uniform(0.8, 1.25) * (1.5 if k == teeth // 2 else 1)
        base = p + Vector((-side * width * 0.3, 0, 0))
        point(m, "Teeth", f.at(*base), f.at(*(base + inward * size)), width * 0.36)
    m.bone = parent


def rot_maw(m, f, skull_w, length, snout_w, upper_h, lower_h, rng, gape=0.18, drop=0.55, upper="Body", lower="Accent", tooth=0.3,
            per_side=7, head="Head", jaw="Jaw", gills=5, strands=3, rows=2, lift=0.1, mandibles=None, across=4, thin=0.36, tip_h=None,
            nostrils=False):
    """The rot maw, built in frame f, whose origin is the middle of the mouth's back and whose +Y is out of the mouth: an
    upper jaw on the head bone (upper_h deep at the back, tip_h at the snout, so its top slopes down), its roof the
    underside of a mushroom with gills glowing back to a glowing throat; a lower jaw on the jaw bone hanging wide open by
    drop (radians) at rest; two rows of long needle teeth in each; glowing strings of mycelium stretched between the
    jaws. mandibles (a dict of mandible()'s arguments) adds side jaws, so it opens four ways. nostrils: two flared slits on
    the snout. Returns the lower jaw's frame and length."""
    m.bone = head
    tip_h = tip_h or upper_h
    yloft(f, upper, (-0.05, 0, gape / 2 + upper_h * 0.5, skull_w * 0.96, upper_h), (length, 0, gape / 2 + tip_h / 2 + lift, snout_w, tip_h))
    if nostrils:
        y = length * 0.82
        top = gape / 2 + upper_h + (tip_h + lift - upper_h) * (y + 0.05) / (length + 0.05)
        for side in (-1, 1):
            f.box("Mouth", side * snout_w * 0.2, y, top, snout_w * 0.13, length * 0.1, 0.06, turn(z=side * 0.5))
    yloft(f, "Mouth", (0, 0, gape / 2 - 0.03, skull_w * 0.84, 0.06), (length * 0.95, 0, gape / 2 + lift * 0.95 - 0.03, snout_w * 0.86, 0.06))
    open_h = gape + drop * length * 0.8 + 0.2
    f.box("Mouth", 0, 0.03, gape / 2 - open_h / 2, skull_w * 0.88, 0.12, open_h)
    f.box("GillGlow", 0, 0.11, gape / 2 - open_h * 0.5, skull_w * 0.46, 0.06, open_h * 0.6)
    for k in range(gills):  # the roof of the mouth: gills fanning forward from the throat
        x = (k - (gills - 1) / 2) / max(gills - 1, 1) * skull_w * 0.62
        xb = x * snout_w / skull_w * 0.92
        beam(m, "GillGlow", f.at(x, length * 0.06, gape / 2 - 0.08), f.at(xb, length * 0.86, gape / 2 + lift * 0.86 - 0.08), 0.06, 0.12, 0.05)

    def width(y):
        return skull_w * 0.96 + (snout_w - skull_w * 0.96) * y / length

    def roof(y):
        return gape / 2 + lift * y / length

    needles(m, f, width, roof, length, tooth, per_side, rng, False, across=across, thin=thin)
    if rows > 1:
        needles(m, f, lambda y: width(y) * 0.64, roof, length * 0.82, tooth * 0.62, max(per_side - 2, 2), rng, False, across=0, thin=thin, fang=-99)

    hinge = f.at(0, -0.05, -gape / 2)
    m.use(jaw, hinge, head)
    lf = Frame(m, hinge, f.r @ turn(x=-drop))
    ll = length * 0.95
    yloft(lf, lower, (0, 0, -lower_h * 0.55, skull_w * 0.86, lower_h * 1.1), (ll, 0, -lower_h * 0.5, snout_w * 0.92, lower_h))
    yloft(lf, "Mouth", (0, 0, 0.0, skull_w * 0.72, 0.06), (ll * 0.95, 0, 0.0, snout_w * 0.76, 0.06))

    def low_width(y):
        return skull_w * 0.86 + (snout_w * 0.92 - skull_w * 0.86) * y / ll

    needles(m, lf, low_width, lambda y: 0.0, ll, tooth * 0.88, per_side, rng, True, across=max(across - 1, 0), thin=thin)
    if rows > 1:
        needles(m, lf, lambda y: low_width(y) * 0.6, lambda y: 0.0, ll * 0.8, tooth * 0.58, max(per_side - 2, 2), rng, True, across=0, thin=thin,
                fang=-99)
    for k in range(strands):  # glowing strings of mycelium stretched between the jaws, like drool
        u = (k + 0.5) / strands - 0.5
        x = u * skull_w * 0.7 + rng.uniform(-0.05, 0.05) * skull_w
        y = length * (0.18 + 0.22 * ((k * 7) % 3) / 2)
        beam(m, "Vein", f.at(x, y, roof(y) - 0.02), lf.at(x * 0.95 + rng.uniform(-0.1, 0.1) * skull_w, y * 0.95, 0.03), 0.055, None, 0.035)
        m.stretch("Vein", head)
    if mandibles:
        for side in (-1, 1):
            mandible(m, f, side, rng=rng, parent=head, **mandibles)
    m.bone = head
    return lf, ll


def morel_hood(m, f, r, h, rng, cols=8, rows=5, ridge_role="Ridge", pit="Pit", ridge_w=0.17):
    """A morel, in frame f, its base at f's origin and rising up f's Z: a glowing core and over it a honeycomb of ridges
    ridge_w * r thick, light glowing out of every pit. Returns the pits as (centre, outward, size), and its tip."""
    prof = ((0, 1.0), (0.18, 1.06), (0.45, 0.95), (0.7, 0.72), (0.88, 0.42), (1.0, 0.14))

    def rad(t):
        return r * share(prof, t)

    for (t0, s0), (t1, s1) in zip(prof, prof[1:]):
        f.prism(pit, 0, 0, h * t0, h * t1, r * s0 * 0.9, r * s1 * 0.9, cols * 2)
    rings = [0.03 + 0.9 * k / rows for k in range(rows + 1)]
    w = r * ridge_w
    for k, t in enumerate(rings):  # rings round it
        pts = [f.at(math.cos(a) * rad(t), math.sin(a) * rad(t), h * t) for a in [i * math.tau / cols for i in range(cols + 1)]]
        for p, q in zip(pts, pts[1:]):
            beam(m, ridge_role, p, q, w * (1 - 0.4 * t))
    pits = []
    for k, (t0, t1) in enumerate(zip(rings, rings[1:])):  # and ridges between them, staggered: the honeycomb
        for i in range(cols):
            a = (i + 0.5 * (k % 2)) * math.tau / cols + rng.uniform(-0.06, 0.06)
            beam(m, ridge_role, f.at(math.cos(a) * rad(t0), math.sin(a) * rad(t0), h * t0), f.at(math.cos(a) * rad(t1), math.sin(a) * rad(t1), h * t1),
                 w * (1 - 0.4 * t1))
            ac, tc = a + math.pi / cols, (t0 + t1) / 2
            out = f.r @ Vector((math.cos(ac), math.sin(ac), 0.25))
            pits.append((Vector(f.at(math.cos(ac) * rad(tc) * 0.93, math.sin(ac) * rad(tc) * 0.93, h * tc)), out.normalized(), min(h * (t1 - t0), rad(tc) * 0.78)))
    tip = f.at(0, 0, h)
    f.prism(ridge_role, 0, 0, h * 0.97, h * 1.06, r * 0.16, r * 0.04, 6)
    return pits, Vector(tip)


# ---------------------------------------------------------------------- the common ones


def toad_rage():
    """A bloated black cave toad crouched to spring, its head nearly all mouth: a jaw hanging wide on two rows of needles,
    glowing gills for a roof and strings of glowing mycelium stretched across it. Two burning eyes on bumps under warty
    brows slammed down to the nose, more bursting up through the hide beside them. A row of bone spikes down its back,
    black ink caps and shelf fungi growing out of it, two warts torn open and pouring spores, mycelium whips lashing from
    its rump, and splayed hands of long hooked claws."""
    rng = random.Random(1401)
    m = monster("dino_ToadRage", Body="#3c3727", Accent="#23201a", Belly="#776e53", Claw="#e8dec2", Wart="#555038")
    m.joint("Spine", (0, -0.4, 1.35))
    lumps = (((0, -0.95, 1.12), 1.6, 1.55, 1.05), ((0, 0.25, 1.55), 1.5, 1.15, 1.02))  # a heavy rump, shoulders hunched up
    for c, rx, ry, rz in lumps:
        egg(m, "Body", c, rx, ry, rz, 12, 7)
    m.loft_y("Belly", (-2.05, 0, 0.3, 1.8, 0.26), (0.9, 0, 0.7, 2.3, 0.3))

    def top(x, y):
        heights = [h for h in (on_egg(c, rx, ry, rz, x, y) for c, rx, ry, rz in lumps) if h is not None]
        return max(heights) if heights else 0.6

    for _ in range(30):  # warts all over its back
        x, y = rng.uniform(-1.35, 1.35), rng.uniform(-2.3, 0.5)
        z = top(x, y)
        if z < 0.8:
            continue
        r_ = rng.uniform(0.1, 0.2)
        ball(m, "Wart", x, y, z - r_ * 0.35, r_, 6, 3)
    ridge(m, "Claw", [(rng.uniform(-0.1, 0.1), y, top(0, y) - 0.1) for y in (0.5, 0.1, -0.3, -0.7, -1.1, -1.5, -1.9)], rng, 0.7, 0.24, 0.75)
    for side in (-1, 1):  # and smaller ones down its flanks
        ridge(m, "Claw", [(side * 0.85, y, top(side * 0.85, y) - 0.08) for y in (0.25, -0.5, -1.25, -1.9)], rng, 0.38, 0.16, 0.6)
    for x, y in ((1.0, -0.15), (-1.1, -1.45), (0.55, -2.1), (1.2, -1.6), (-0.95, 0.05)):  # pale mycelium bursting out of it
        crust(m, (x, y, top(x, y) - 0.05), (x * 0.6, 0, 1), 0.4, rng, 6)
    for x, y, d, h, r_, cr, ch in ((-0.7, -0.55, (-0.55, -0.15, 1), 1.0, 0.12, 0.52, 0.66), (0.75, -1.3, (0.6, -0.35, 1), 0.8, 0.1, 0.44, 0.55),
                                   (-0.3, -1.95, (-0.25, -0.8, 1), 0.55, 0.08, 0.32, 0.42)):  # black ink caps growing out of it
        sprout(m, (x, y, top(x, y) - 0.15), d, h, r_, cr, ch, rng)
    for side, y, z, r_ in ((-1, -0.75, 1.25, 0.44), (-1, -1.4, 0.92, 0.32), (1, -0.95, 1.5, 0.38), (1, 0.15, 1.1, 0.3)):  # shelf fungi
        k = 1 - ((y + 0.95) / 1.55) ** 2 - ((z - 1.12) / 1.05) ** 2
        bracket(m, side * 1.6 * math.sqrt(max(k, 0.05)) * 0.98, y, z, r_)
    for n, x, y in ((1, 0.32, -0.55), (2, -0.62, -1.35)):  # two warts torn open, pouring spores
        z = top(x, y)
        ball(m, "Puffskin", x, y, z - 0.1, 0.34, 8, 4)
        vent(m, n, (x, y, z + 0.16), "Spine", 0.3, 4)
    for n, side in ((1, -1), (2, 1)):  # mycelium whips lashing from its rump
        start = Vector((side * 0.5, -1.85, top(side * 0.5, -1.85) - 0.1))
        tendril(m, n, wander(tuple(start), tuple(start + Vector((side * 1.2, -1.4, 1.7))), rng, 7, (side * 0.3, 0, 0.5), 0.15), 0.22, 0.06, "Spine",
                "Mycel", beads="Glow", tip="Glow", tip_size=0.13)
        m.bone = "Spine"

    for side, bone in ((-1, "FrontL"), (1, "FrontR")):  # thick arms planted wide, hands of long hooked claws
        sh = Vector((side * 1.15, 0.65, 1.4))
        m.use(bone, tuple(sh))
        elbow = Vector((side * 1.9, 0.95, 0.85))
        wrist = Vector((side * 1.75, 1.6, 0.26))
        beam(m, "Body", tuple(sh), tuple(elbow), 0.72, None, 0.56)
        ball(m, "Body", *elbow, 0.33, 6, 3)
        thorn(m, "Claw", tuple(elbow + Vector((side * 0.2, -0.1, 0.1))), tuple(elbow + Vector((side * 0.7, -0.5, 0.45))), 0.22)
        beam(m, "Accent", tuple(elbow), tuple(wrist), 0.54, None, 0.46)
        m.block("Accent", wrist.x, wrist.y + 0.12, 0.17, 0.72, 0.62, 0.32)
        for k in range(4):
            a = side * (-0.5 + k * 0.38)
            d = Vector((math.sin(a), math.cos(a), 0))
            base = Vector((wrist.x, wrist.y + 0.3, 0.18)) + d * 0.15
            thorn(m, "Claw", tuple(base), tuple(base + d * 0.95 + Vector((0, 0, -0.14))), 0.17, (0, 0, 0.16))
    for side, bone in ((-1, "BackL"), (1, "BackR")):  # big folded thighs, toes splayed forward, clawed
        m.use(bone, (side * 1.05, -1.15, 1.05))
        x = side * 1.38
        egg(m, "Body", (x, -1.2, 0.85), 0.52, 1.0, 0.64, 8, 5)
        m.loft_y("Accent", (-1.95, x * 1.06, 0.3, 0.55, 0.5), (-0.5, x * 1.1, 0.28, 0.48, 0.42))
        ankle = Vector((x * 1.1, -0.45, 0.15))
        for k in range(4):
            a = side * (0.15 + k * 0.32)
            d = Vector((math.sin(a), math.cos(a), 0))
            tip = ankle + d * (0.9 - 0.1 * abs(k - 1.5))
            beam(m, "Accent", tuple(ankle), tuple(tip), 0.18, 0.12, 0.14)
            thorn(m, "Claw", tuple(tip), tuple(tip + d * 0.4 + Vector((0, 0, -0.08))), 0.13)
    m.bone = "Spine"

    m.use("Neck", (0, 0.85, 1.85))
    m.block("Body", 0, 0.95, 1.7, 1.7, 0.5, 0.75)  # a thick fold of neck (a bone the game moves must carry something)
    m.use("Head", (0, 1.05, 1.85), "Neck")
    hf = Frame(m, (0, 1.4, 1.95), turn(x=-0.06))
    hf.box("Body", 0, -0.4, 0.12, 2.3, 1.0, 0.75)  # the back of the skull, behind the eyes
    mf = Frame(m, hf.at(0, -0.2, -0.1), hf.r @ turn(x=0.08))
    lf, ll = rot_maw(m, mf, 2.5, 1.45, 1.8, 0.44, 0.4, rng, gape=0.18, drop=0.62, upper="Body", lower="Accent", tooth=0.38, per_side=8, rows=2,
                     gills=7, strands=5, lift=0.0, across=5, tip_h=0.22, nostrils=True)
    egg(m, "Body", mf.at(0, 0.62, 0.36), 1.0, 0.82, 0.3, 10, 4)  # a low dome over the snout, so the head isn't a box
    for side in (-1, 1):
        ball(m, "Body", *mf.at(side * 1.18, 0.1, 0.12), 0.4, 8, 4)  # cheeks bulging at the hinge
    m.bone = "Jaw"
    egg(m, "Belly", lf.at(0, ll * 0.42, -0.42), 0.95, 0.62, 0.32, 10, 5)  # the throat pouch under it
    m.bone = "Head"
    for _ in range(9):  # warts on the snout
        y = rng.uniform(0.15, 1.1)
        top = 0.18 / 2 + 0.44 + (0.22 - 0.44) * (y + 0.05) / 1.5
        ball(m, "Wart", *mf.at(rng.uniform(-0.9, 0.9), y, top - 0.03), rng.uniform(0.08, 0.14), 6, 3)
    for side in (-1, 1):  # two burning eyes on bumps, under warty brows slammed down to the nose
        ball(m, "Body", *hf.at(side * 0.82, 0.12, 0.55), 0.42, 8, 4)
        rot_eye(m, hf.at(side * 0.86, 0.5, 0.62), hf.r @ Vector((side * 0.2, 1, 0.04)), 0.5, -side, 0.72, rng=rng, veins=3, horns=1)
        for k in range(3):  # warts along the brow
            ball(m, "Wart", *hf.at(side * (1.22 - 0.22 * k), 0.3 + 0.08 * k, 0.98 - 0.1 * k), 0.12, 6, 3)
    for x, y, z, r in ((-1.25, 0.1, 0.62, 0.13), (-1.08, -0.22, 0.9, 0.1), (1.26, 0.12, 0.66, 0.14), (1.04, -0.24, 0.92, 0.11),
                       (1.32, -0.2, 0.4, 0.09)):  # spare eyes bursting up beside them
        bead(m, hf.at(x, y, z), hf.r @ Vector((x * 0.9, 0.7, 0.35)), r)
    m.head_centre = tuple(hf.at(0, 0.9, 0.35))
    return finish(m, 1.0)


def morel_panic():
    """A gaunt, ash-pale crawler on four long limbs, its knees and elbows up higher than its back, ribs and spine showing,
    long black-clawed fingers reaching. Its head is under a black morel pulled down like a hood, every pit glowing
    ember-orange and eyes looking out of a few of them; under the brim, two burning eyes and a long jaw hanging open in
    a scream. Mycelium whips lash from its shoulders and spores rise off the tip of the hood."""
    rng = random.Random(1402)
    m = monster("dino_MorelPanic", Body="#a19b85", Accent="#5c574a", Belly="#d6cfb8", Claw="#1a1411", Ridge="#221a15", Pit="#e8651c")
    hips, waist, chest = Vector((0, -1.0, 2.65)), Vector((0, -0.2, 2.45)), Vector((0, 0.75, 2.15))
    m.joint("Spine", tuple(hips))
    beam(m, "Accent", tuple(hips + Vector((0, -0.4, 0.05))), tuple(waist), 0.85, 0.62, 0.48)  # the pelvis, to a thin waist
    beam(m, "Body", tuple(waist), tuple(chest), 0.5, 0.5, 1.0)  # and out to a deep chest
    for k in range(5):  # ribs showing down its sides
        t = 0.2 + 0.17 * k
        c = waist.lerp(chest, t)
        half = 0.25 + 0.26 * t
        for side in (-1, 1):
            beam(m, "Belly", (side * half * 0.5, c.y, c.z - half * 0.95), (side * (half + 0.06), c.y + 0.05, c.z - 0.02), 0.1, 0.1, 0.08)
    spine = [hips.lerp(chest, k / 6) + Vector((0, 0, 0.3 + 0.28 * math.sin(math.pi * k / 6))) for k in range(7)]
    for k, p in enumerate(spine):  # the knobs of its spine, arched, bone spikes out of every other one
        ball(m, "Belly", *p, 0.15, 6, 3)
        if k % 2:
            thorn(m, "Belly", tuple(p), tuple(p + Vector((rng.uniform(-0.1, 0.1), -0.35, 0.6))), 0.14)
    for k, side in ((0, -1), (1, 1), (2, -1)):  # mycelium bursting out of its back
        p = hips.lerp(chest, 0.2 + 0.3 * k) + Vector((side * 0.28, 0, 0.3))
        crust(m, tuple(p), (side * 0.6, 0, 1), 0.28, rng, 5)

    for side, letter in ((-1, "L"), (1, "R")):  # arms: elbows up and out like a spider's, long hands reaching ahead
        sh = Vector((side * 0.5, 0.85, 2.25))
        m.use(f"Front{letter}", tuple(sh))
        elbow = Vector((side * 1.6, 0.85, 2.85))
        wrist = Vector((side * 1.6, 3.2, 0.6))
        limb(m, "Body", [tuple(sh), tuple(elbow)], 0.26, 0.2)
        ball(m, "Belly", *elbow, 0.19, 6, 3)
        thorn(m, "Belly", tuple(elbow), tuple(elbow + Vector((side * 0.3, -0.45, 0.6))), 0.14)
        limb(m, "Body", [tuple(elbow), tuple(wrist)], 0.2, 0.15)
        ball(m, "Belly", *wrist, 0.14, 6, 3)
        claw_hand(m, wrist, (side * 0.18, 1, -0.4), 0.5, side, role="Body", claw="Claw")
    for side, letter in ((-1, "L"), (1, "R")):  # legs folded up like a cricket's, knees above its back
        hip = Vector((side * 0.42, -1.1, 2.55))
        m.use(f"Back{letter}", tuple(hip))
        knee = Vector((side * 1.45, -0.55, 3.3))
        ankle = Vector((side * 1.35, -1.8, 0.7))
        foot = Vector((side * 1.4, -1.35, 0.1))
        limb(m, "Body", [tuple(hip), tuple(knee)], 0.3, 0.22)
        ball(m, "Belly", *knee, 0.2, 6, 3)
        thorn(m, "Belly", tuple(knee), tuple(knee + Vector((side * 0.2, -0.5, 0.5))), 0.13)
        limb(m, "Body", [tuple(knee), tuple(ankle)], 0.22, 0.15)
        ball(m, "Belly", *ankle, 0.13, 6, 3)
        limb(m, "Accent", [tuple(ankle), tuple(foot)], 0.15, 0.14)
        for k in (-1, 0, 1):
            d = Vector((k * 0.35, 1, 0)).normalized()
            thorn(m, "Claw", tuple(foot + d * 0.05), tuple(foot + d * 0.55 + Vector((0, 0, -0.08))), 0.1, (0, 0, 0.08))
    m.bone = "Spine"
    for n, side in ((1, -1), (2, 1)):  # whips of mycelium out of its shoulder blades
        start = Vector((side * 0.35, 0.4, 2.65))
        tendril(m, n, wander(tuple(start), tuple(start + Vector((side * 1.5, -1.6, 1.7))), rng, 7, (side * 0.3, 0, 0.45), 0.14), 0.19, 0.06, "Spine",
                "Mycel", beads="Glow", tip="Glow", tip_size=0.12)
        m.bone = "Spine"

    neck = chest + Vector((0, 0.15, 0.25))
    m.use("Neck", tuple(neck))
    beam(m, "Body", tuple(neck - Vector((0, 0.15, 0.1))), (0, 1.45, 2.7), 0.42, 0.42, 0.36)
    m.stretch("Body", "Spine")
    m.use("Head", (0, 1.4, 2.65), "Neck")
    hf = Frame(m, (0, 1.78, 2.72), turn(x=-0.04))  # thrust out low, at the height of its shoulders
    hf.box("Body", 0, -0.18, 0.1, 1.0, 0.85, 0.74)
    for side in (-1, 1):
        hf.box("Accent", side * 0.44, 0.12, -0.1, 0.2, 0.6, 0.32)  # sunken cheeks
    for k in range(3):  # glowing threads running down its neck from under the hood
        a = Vector(hf.at(-0.15 + 0.15 * k, -0.45, 0.35))
        limb(m, "Vein", [tuple(a), tuple(a + Vector((0.1 * (k - 1), -0.45, -0.2))), tuple(a + Vector((0.15 * (k - 1), -0.9, -0.3)))], 0.07, 0.05,
             joints=False)
    mf = Frame(m, hf.at(0, 0.2, -0.3), hf.r)
    rot_maw(m, mf, 0.95, 1.25, 0.62, 0.28, 0.26, rng, gape=0.1, drop=0.72, upper="Body", lower="Accent", tooth=0.3, per_side=8, rows=2, gills=4,
            strands=3, lift=0.0, across=3, tip_h=0.2)
    for side in (-1, 1):
        rot_eye(m, hf.at(side * 0.27, 0.32, 0.27), hf.r @ Vector((side * 0.1, 1, -0.04)), 0.36, -side, 0.78, rng=rng, veins=3)
    mo = Frame(m, hf.at(0, -0.32, 0.42), hf.r @ turn(x=0.32, y=0.1))  # a black morel for a hood, swept back off its skull
    pits, tip = morel_hood(m, mo, 0.6, 1.35, rng, cols=10, rows=6, pit="Socket", ridge_w=0.26)
    rng.shuffle(pits)
    for centre, out, size in pits[:7]:  # embers glowing deep in a few of the pits
        obox(m, "Pit", tuple(centre + out * size * 0.05), (size * 0.5, size * 0.5, size * 0.5), aim(out))
    vent(m, 1, tuple(tip + Vector((0, 0, 0.08))), "Head", 0.26, 4, lips=None)
    m.head_centre = tuple(hf.at(0, 0.8, 0.15))
    return finish(m, 1.0)


def antagonist():
    """A black ant the fungus got to, reared up on four legs with its front pair raised to grab. Huge serrated mandibles
    spread wide round a mouth of needles, burning compound eyes under ridged brows, white mycelium bursting out of every
    joint, a sting curled up over its back, and out of the back of its head the fungus that took it: a pale stalk arching
    up and over to dangle a glowing club in front of its face, whipping about as if looking for the next one."""
    rng = random.Random(1403)
    m = monster("dino_Antagonist", Body="#241c1b", Accent="#4a1b16", Belly="#6b2c20", Claw="#ddd1b4")
    m.joint("Spine", (0, 0, 2.05))
    m.loft_y("Body", (-0.8, 0, 2.1, 0.85, 0.85), (0.1, 0, 2.3, 1.1, 1.05))
    m.loft_y("Body", (0.1, 0, 2.3, 1.1, 1.05), (0.85, 0, 2.2, 1.0, 0.95))
    m.loft_y("Accent", (-0.6, 0, 2.62, 0.62, 0.22), (0.7, 0, 2.8, 0.66, 0.24))
    ridge(m, "Claw", along((0, -0.65, 2.7), (0, 0.65, 2.88), 4), rng, 0.65, 0.22, 0.65)
    crust(m, (0, -0.85, 2.15), (0, -1, 0.3), 0.32, rng, 5)  # white mycelium bursting from the waist

    m.use("Tail1", (0, -1.05, 2.25))
    m.loft_y("Accent", (-1.45, 0, 2.55, 0.5, 0.5), (-0.85, 0, 2.2, 0.42, 0.42))  # the waist, rising to the gaster
    gc, grx, gry, grz = Vector((0, -2.5, 3.0)), 1.2, 1.4, 1.1
    egg(m, "Body", gc, grx, gry, grz, 12, 7)
    for y in (-1.95, -2.55, -3.15):  # bands round it, white mycelium bursting from between them
        k = math.sqrt(max(0.0, 1 - ((y - gc.y) / gry) ** 2)) * 1.04
        egg(m, "Accent", (0, y, gc.z), grx * k, 0.09, grz * k, 12, 3)
        for side in (-1, 1):
            crust(m, (side * grx * k * 0.85, y, gc.z + grz * k * 0.45), (side, 0, 0.6), 0.24, rng, 4)
    for side in (-1, 1):  # glowing cracks where the fungus is splitting it
        pts = [(side * 0.3, -1.6, 3.6), (side * 0.65, -2.1, 3.85), (side * 0.55, -2.7, 3.95), (side * 0.85, -3.2, 3.55)]
        limb(m, "Vein", pts, 0.09, 0.06, joints=False)
    vent(m, 1, (0.3, -2.45, gc.z + grz - 0.05), "Tail1", 0.36, 4, lips="Accent")
    m.use("Tail2", (0, -3.75, 3.2), "Tail1")
    sting = [(0, -3.75, 3.25), (0, -4.2, 3.95), (0, -4.05, 4.7), (0, -3.5, 5.15)]  # the sting, curled up over its back, aimed ahead
    limb(m, "Accent", sting, 0.48, 0.26)
    point(m, "Claw", sting[-1], (0, -2.6, 5.3), 0.28)
    m.bone = "Spine"

    legs = (("Front", 0.15, 1.95, (1.8, 0.5, 3.05), (2.5, 1.05, 0.05)), ("Back", -0.45, 1.95, (1.7, -1.2, 3.0), (2.35, -2.3, 0.05)))
    for prefix, hy, hz, knee, foot in legs:  # four legs on the ground
        for side, letter in ((-1, "L"), (1, "R")):
            hip = Vector((side * 0.42, hy, hz))
            m.use(f"{prefix}{letter}", tuple(hip))
            k = Vector((side * knee[0], knee[1], knee[2]))
            f_ = Vector((side * foot[0], foot[1], foot[2]))
            ankle = k.lerp(f_, 0.7) + Vector((side * 0.15, 0, 0.15))
            jointed_leg(m, [hip, k, ankle, f_], 0.3, role="Body", ring="Accent", tip="Claw")
            thorn(m, "Claw", tuple(k), tuple(k + Vector((side * 0.15, -0.25, 0.5))), 0.15)
            crust(m, tuple(k), (side, 0, 0.4), 0.22, rng, 4)
    for side, letter in ((-1, "L"), (1, "R")):  # the front pair raised to grab, on the Arm bones so they rake when it pounces
        hip = Vector((side * 0.42, 0.6, 2.0))
        m.use(f"Arm{letter}", tuple(hip))
        knee = Vector((side * 1.4, 1.3, 3.35))
        wrist = Vector((side * 1.15, 2.6, 2.4))
        tip = Vector((side * 0.8, 3.1, 1.55))
        jointed_leg(m, [hip, knee, wrist, tip], 0.3, role="Body", ring="Accent", tip="Claw")
        for k in range(4):  # hooked spines along the forearm
            p = knee.lerp(wrist, 0.2 + 0.2 * k) + Vector((-side * 0.1, 0, -0.12))
            point(m, "Claw", tuple(p), tuple(p + Vector((-side * 0.15, 0.12, -0.38))), 0.1)
        crust(m, tuple(knee), (side, 0, 0.5), 0.24, rng, 4)
    m.bone = "Spine"
    for n, x, y, end in ((2, 0.3, -0.35, (1.3, -1.6, 5.1)), (3, -0.3, 0.2, (-1.4, -0.9, 4.6))):  # more of the fungus out of its back
        start = (x, y, 2.75)
        tendril(m, n, wander(start, end, rng, 6, (0.2 * x, 0, 0.3), 0.1), 0.2, 0.12, "Spine", "Stalk", beads=None)
        tube(m, "Glow", end, tuple(Vector(end) + (Vector(end) - Vector(start)).normalized() * 0.6), 0.18, 0.08, 6)
        m.bone = "Spine"

    m.use("Neck", (0, 0.85, 2.3))
    beam(m, "Accent", (0, 0.7, 2.3), (0, 1.3, 2.4), 0.55)
    crust(m, (0, 1.0, 2.62), (0, 0.2, 1), 0.26, rng, 4)
    m.use("Head", (0, 1.35, 2.4), "Neck")
    hf = Frame(m, (0, 2.0, 2.4), turn(x=-0.24, y=0.05))  # big and heavy, thrust down at you
    zloft(hf, "Body", (-0.7, 0, 0.0, 1.15, 1.05), (0.1, 0, 0, 1.95, 1.45))
    zloft(hf, "Body", (0.1, 0, 0, 1.95, 1.45), (0.66, 0, -0.12, 1.6, 1.1))
    hf.box("Accent", 0, -0.05, 0.68, 0.14, 0.95, 0.1)  # the seam down its crown
    mf = Frame(m, hf.at(0, 0.55, -0.48), hf.r @ turn(x=0.15))
    rot_maw(m, mf, 1.0, 0.55, 0.7, 0.28, 0.26, rng, gape=0.14, drop=0.5, upper="Accent", lower="Accent", tooth=0.22, per_side=5, rows=2, gills=3,
            strands=2, across=3, mandibles=dict(x0=0.62, y0=0.1, z0=0.05, length=2.1, width=0.44, teeth=7, curl=0.5, role="Accent"))
    for side in (-1, 1):  # burning compound eyes on the corners of its head, three more on its crown
        orb(m, hf.at(side * 0.88, 0.38, 0.28), hf.r @ Vector((side * 0.55, 1, 0.05)), 0.4, -side)
    for x, z, r in ((0, 0.62, 0.11), (-0.22, 0.52, 0.09), (0.22, 0.52, 0.09)):
        bead(m, hf.at(x, 0.5, z), hf.r @ Vector((x, 1, 0.6)), r)
    for side in (-1, 1):  # elbowed feelers, held stiff
        limb(m, "Accent", [hf.at(side * 0.32, 0.45, 0.5), hf.at(side * 0.55, 0.65, 1.35), hf.at(side * 1.15, 1.45, 1.55), hf.at(side * 1.45, 2.05, 1.25)],
             0.12, 0.07)
    start = Vector(hf.at(0.1, -0.5, 0.55))  # the stalk out of the back of its head, arching over to dangle its club ahead
    pts = [tuple(start), tuple(start + Vector((0.1, -0.35, 1.1))), tuple(start + Vector((0.2, -0.2, 2.2))), tuple(start + Vector((0.25, 0.5, 3.0))),
           tuple(start + Vector((0.2, 1.5, 3.25))), tuple(start + Vector((0.12, 2.35, 2.85))), tuple(start + Vector((0.05, 2.75, 2.15)))]
    end = tendril(m, 1, pts, 0.32, 0.18, "Head", "Stalk", beads=None)
    m.bone = "Lash1c"
    tube(m, "Glow", tuple(end), tuple(end + Vector((0, 0.1, -0.8))), 0.28, 0.14, 8)
    for k in range(4):  # dark knots on the club
        ball(m, "Accent", *(end + Vector((0.2 * math.cos(2 * k), 0.2 * math.sin(2 * k) + 0.05, -0.15 - 0.15 * k))), 0.09, 6, 3)
    m.bone = "Head"
    m.head_centre = tuple(hf.at(0, 0.9, 0.05))
    return finish(m, 1.0)


# ---------------------------------------------------------------------- the fierce ones


def sporantula():
    """A black spider, its front legs raised high over its head to strike, bone knuckles on every joint and bristles on
    every leg. Two burning eyes under heavy brows and six more in a cluster, huge bone fangs dripping glowing venom that
    never stop working, and a swollen abdomen marked with glowing chevrons, black caps and pale mycelium bursting out of
    it, spores pouring from two vents and glowing threads trailing from its spinnerets."""
    rng = random.Random(1404)
    m = monster("dino_Sporantula", Body="#211b19", Accent="#3a2f29", Belly="#55463b", Claw="#e4d9be", Face="#16110e")
    m.joint("Spine", (0, 0, 2.4))
    egg(m, "Body", (0, 0.1, 2.42), 1.25, 1.3, 0.72, 12, 6)  # a low, wide, armoured front body
    m.loft_y("Accent", (-0.95, 0, 2.95, 0.5, 0.2), (0.95, 0, 3.05, 0.42, 0.2))
    for _ in range(12):  # bristling
        x, y = rng.uniform(-0.9, 0.9), rng.uniform(-0.8, 0.9)
        z = on_egg((0, 0.1, 2.42), 1.25, 1.3, 0.72, x, y)
        if z:
            thorn(m, "Claw", (x, y, z - 0.05), (x * 1.4, y - 0.3, z + rng.uniform(0.25, 0.45)), 0.09)

    hips, feet = (0.3, -0.15, -0.55), (1.2, -0.7, -2.4)  # three pairs walking: diagonal pairs step together
    for side, letter in ((-1, "L"), (1, "R")):
        for k, (hy, fy) in enumerate(zip(hips, feet)):
            bone = f"{'Front' if k == 1 else 'Back'}{letter}"
            if bone not in m.joints:
                m.use(bone, (side * 0.55, 0.3 if k == 1 else -0.2, 2.3))
            m.bone = bone
            spread = 1.0 - 0.08 * k
            hip = Vector((side * 0.6, hy, 2.3))
            under = Vector((side * 2.3 * spread, hy + (fy - hy) * 0.3, 2.5))
            knee = Vector((side * 3.0 * spread, hy + (fy - hy) * 0.55, 4.15 - 0.15 * k))
            ankle = Vector((side * 3.55 * spread, hy + (fy - hy) * 0.9, 1.3))
            foot = Vector((side * 3.65 * spread, fy, 0.03))
            jointed_leg(m, [hip, under, knee, ankle, foot], 0.36, role="Body", ring="Claw", tip="Claw", taper=0.45)
            for a, b in ((under, knee), (knee, ankle)):  # bristles down the leg
                for t in (0.3, 0.6):
                    p = a.lerp(b, t)
                    thorn(m, "Accent", tuple(p), tuple(p + Vector((side * 0.28, rng.uniform(-0.2, 0.2), 0.22))), 0.08)
    for side, letter in ((-1, "L"), (1, "R")):  # the front pair raised high over its head, hooked down to strike
        hip = Vector((side * 0.55, 0.8, 2.4))
        m.use(f"Arm{letter}", tuple(hip))
        knee = Vector((side * 1.75, 1.35, 4.9))
        fore = Vector((side * 1.4, 2.7, 4.35))
        tip = Vector((side * 0.95, 3.35, 3.2))
        jointed_leg(m, [hip, knee, fore, tip], 0.36, role="Body", ring="Claw", tip="Claw", taper=0.5)
        for t in (0.25, 0.55, 0.8):
            p = knee.lerp(fore, t)
            thorn(m, "Accent", tuple(p), tuple(p + Vector((side * 0.15, 0.1, 0.35))), 0.09)
    m.bone = "Spine"

    m.use("Tail1", (0, -0.85, 2.5))
    ac, arx, ary, arz = (0, -2.55, 3.0), 1.5, 1.8, 1.35
    m.loft_y("Accent", (-1.2, 0, 2.6, 0.5, 0.45), (-0.8, 0, 2.5, 0.45, 0.4))
    egg(m, "Body", ac, arx, ary, arz, 12, 7)

    def on_top(x, y):
        return on_egg(ac, arx, ary, arz, x, y) or ac[2]

    for k in range(4):  # glowing chevrons down its back
        y = ac[1] + 1.0 - k * 0.55
        for side in (-1, 1):
            a_, b_ = (0, y), (side * (0.75 - 0.08 * k), y - 0.38)
            beam(m, "Glow", (*a_, on_top(*a_) + 0.01), (*b_, on_top(*b_) + 0.01), 0.17, 0.08, 0.12)
    for x, y in ((0.95, -2.0), (-1.0, -2.9), (0.6, -3.6), (-0.7, -1.6)):  # pale mycelium bursting out of it
        crust(m, (x, y, on_top(x, y) - 0.05), (x, 0, 1), 0.38, rng, 6)
    for x, y, d, h, r_, cr, ch in ((-0.75, -2.3, (-0.6, -0.1, 1), 0.85, 0.11, 0.5, 0.6), (0.85, -2.85, (0.6, -0.4, 1), 0.65, 0.09, 0.4, 0.48),
                                   (0.2, -3.55, (0.1, -0.8, 1), 0.5, 0.08, 0.3, 0.38)):
        sprout(m, (x, y, on_top(x, y) - 0.15), d, h, r_, cr, ch, rng)
    for n, x, y in ((1, -0.35, -1.75), (2, 0.4, -3.05)):
        vent(m, n, (x, y, on_top(x, y) - 0.02), "Tail1", 0.32, 4)
    for side in (-1, 1):  # spinnerets, and glowing threads trailing from them
        tube(m, "Accent", (side * 0.16, -4.25, 2.7), (side * 0.2, -4.6, 2.55), 0.15, 0.08, 6)
    tendril(m, 1, wander((-0.18, -4.55, 2.55), (-1.1, -6.6, 0.6), rng, 7, (-0.3, 0, 0.4), 0.12), 0.09, 0.05, "Tail1", "Vein", beads=None)
    tendril(m, 2, wander((0.18, -4.55, 2.55), (1.3, -6.2, 0.35), rng, 7, (0.3, 0, 0.5), 0.12), 0.09, 0.05, "Tail1", "Vein", beads=None)
    m.bone = "Spine"

    m.use("Head", (0, 0.95, 2.25))
    hf = Frame(m, (0, 1.42, 2.28), turn(x=0.06))
    hf.box("Face", 0, 0, 0, 1.4, 0.72, 1.05)
    mf = Frame(m, hf.at(0, 0.3, -0.34), hf.r)
    rot_maw(m, mf, 0.92, 0.42, 0.6, 0.16, 0.18, rng, gape=0.08, drop=0.6, upper="Face", lower="Face", tooth=0.2, per_side=5, rows=2, gills=3,
            strands=2, across=3)
    for side in (-1, 1):  # eight eyes: the big pair under heavy brows, six round them
        rot_eye(m, hf.at(side * 0.3, 0.37, 0.12), hf.r @ Vector((side * 0.12, 1, 0.05)), 0.36, -side, 0.78, rng=rng, veins=2)
        for x, z, r in ((0.64, 0.28, 0.15), (0.2, 0.47, 0.12), (0.5, 0.54, 0.11)):
            bead(m, hf.at(side * x, 0.34, z), hf.r @ Vector((side * x * 0.8, 1, 0.25)), r)
    for n, side in ((1, -1), (2, 1)):  # the fangs, working for ever on Snap bones
        base = hf.at(side * 0.3, 0.4, -0.32)
        m.use(f"Snap{n}", base, "Head")
        knuckle = hf.at(side * 0.38, 0.8, -0.66)
        beam(m, "Accent", base, knuckle, 0.38, 0.42, 0.3)
        for k in range(3):
            p = Vector(hf.at(side * 0.46, 0.55 + 0.09 * k, -0.42 - 0.09 * k))
            thorn(m, "Claw", tuple(p), tuple(p + hf.r @ Vector((side * 0.22, 0.15, 0.05))), 0.06)
        tip = hf.at(side * 0.08, 1.0, -1.55)
        thorn(m, "Claw", knuckle, tip, 0.27, tuple(hf.r @ Vector((side * 0.12, 0.28, 0))))
        for k, dz in enumerate((0.06, 0.3)):  # glowing venom dripping off it
            ball(m, "Glow", *hf.at(side * 0.07, 1.0, -1.6 - dz), 0.06 - 0.015 * k, 6, 3)
    m.bone = "Head"
    m.head_centre = tuple(hf.at(0, 0.7, 0.0))
    return finish(m, 1.05)


def mantis_wing(m, side, root, rng):
    """One of the Gillotine's wings, stood up behind it in a threat display: ribs fanning from the root up and back, a
    dark membrane between them, glowing veins along the ribs and a huge glaring eye on the outer half, which is on its
    own WingTip bone."""
    letter = "L" if side < 0 else "R"
    root = Vector(root)
    m.use(f"Wing{letter}", tuple(root))
    u = Vector((side * 0.32, -0.45, 0.85)).normalized()  # up the wing
    v = Vector((side * 0.65, -0.7, -0.2)).normalized()  # across it, out and back
    ribs = []
    for k in range(5):
        a = 0.06 + k * 0.3
        d = u * math.cos(a) + v * math.sin(a)
        ribs.append((d, 3.6 - 0.34 * k))
    normal = u.cross(v).normalized()
    split = 0.5
    for bone, t0, t1 in ((f"Wing{letter}", 0.0, split), (f"WingTip{letter}", split, 1.0)):
        if bone.startswith("WingTip"):
            m.use(bone, tuple(root + ribs[2][0] * ribs[2][1] * split), f"Wing{letter}")
        for k, (d, length) in enumerate(ribs):
            a, b = root + d * length * t0, root + d * length * t1
            if t0 == 0:
                beam(m, "Accent", tuple(a), tuple(root + d * length * 0.25), 0.17, None, 0.11)
            beam(m, "Vein", tuple(a), tuple(b), 0.09 * (1 - 0.4 * t0), None, 0.09 * (1 - 0.4 * t1))
            if t1 == 1.0:  # a hooked spine on the end of each rib
                thorn(m, "Claw", tuple(b), tuple(b + d * 0.45 + normal * 0.05), 0.1)
            if k < len(ribs) - 1:
                d2, length2 = ribs[k + 1]
                mid = (d + d2).normalized()
                across_ = (d2 - d).normalized()
                lm = (length + length2) / 2
                lift = normal * (0.014 * k - 0.03)  # each panel a hair off the last, so where they overlap they don't flicker
                plate(m, "Membrane", tuple(root + mid * lm * t0 + lift), tuple(root + mid * lm * t1 * 0.98 + lift), tuple(across_),
                      max(0.05, lm * t0 * 0.3 * 1.2), lm * t1 * 0.3 * 1.15, 0.04)
    # The glaring eye, on the outer half, on both faces: a black socket, a burning iris, an upright slit, a brow.
    d = (ribs[1][0] + ribs[2][0]).normalized()
    c = root + d * 2.5
    normal = normal * side
    for face in (1, -1):
        f = Frame(m, tuple(c + normal * face * 0.06), aim(normal * face) @ turn(y=0.35 * side * face))
        slab(f, "Socket", 0, 0, 0.0, 0.62, 0.05, 12, 1.4)
        slab(f, "EyeGlow", 0, -0.04, 0.03, 0.44, 0.04, 12, 1.1)
        slab(f, "Slit", 0, -0.04, 0.06, 0.38, 0.03, 8, 0.16)
        f.box("Accent", 0, 0.06, 0.44, 1.3, 0.04, 0.22, turn(y=0.3))
    m.bone = "Spine"


def gillotine():
    """A towering ash-pale mantis in a black executioner's hood of a cap, its gills glowing down over its burning eyes.
    Two great serrated blades raised high and ready to come down, side jaws round a mouth of needles, and behind it its
    wings stood up in a threat display, each with a huge glaring eye. Spores pour from vents along its abdomen."""
    rng = random.Random(1405)
    m = monster("dino_Gillotine", Body="#a39b84", Accent="#3a332c", Belly="#d2cab2", Claw="#eee5ce", Cap="#1c1618", CapDark="#100c0d",
                Membrane="#2a2326")
    m.joint("Spine", (0, -0.3, 3.1))
    m.loft_y("Body", (-0.85, 0, 3.15, 0.95, 0.95), (0.3, 0, 3.35, 0.8, 0.85))
    for side, letter in ((-1, "L"), (1, "R")):  # four walking legs, long, thin and spined
        for bone, hy, knee, ankle, foot in ((f"Front{letter}", 0.0, (1.8, 0.7, 4.0), (2.5, 1.1, 1.6), (2.6, 1.2, 0.03)),
                                            (f"Back{letter}", -0.6, (1.9, -1.6, 3.9), (2.6, -2.6, 1.5), (2.7, -2.85, 0.03))):
            hip = Vector((side * 0.35, hy, 3.0))
            m.use(bone, tuple(hip))
            pts = [hip] + [Vector((side * p[0], p[1], p[2])) for p in (knee, ankle, foot)]
            jointed_leg(m, pts, 0.26, role="Body", ring="Accent", tip="Accent")
            for t in (0.3, 0.6):
                p = pts[1].lerp(pts[2], t)
                thorn(m, "Accent", tuple(p), tuple(p + Vector((side * 0.25, 0.1, 0.12))), 0.08)
    m.bone = "Spine"

    m.use("Tail1", (0, -0.75, 3.2))  # the abdomen, long and curling up at its end, banded dark
    pts = [(-0.75, 3.2, 1.0), (-1.9, 3.12, 1.4), (-3.0, 3.18, 1.32), (-3.9, 3.45, 1.08), (-4.6, 3.95, 0.8), (-5.0, 4.6, 0.46)]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        if i == 2:
            m.use("Tail2", (0, a[0], a[1]), "Tail1")
        if i == 4:
            m.use("Tail3", (0, a[0], a[1]), "Tail2")
        m.loft_y("Body", (a[0], 0, a[1], a[2], a[2] * 0.92), (b[0], 0, b[1], b[2], b[2] * 0.92))
        if i in (2, 4):
            m.stretch("Body", "Tail1" if i == 2 else "Tail2")
        m.loft_y("Accent", (a[0] - 0.08, 0, a[1], a[2] + 0.06, a[2] * 0.92 + 0.06), (a[0] + 0.08, 0, a[1], a[2] + 0.06, a[2] * 0.92 + 0.06))
        m.loft_y("Belly", (b[0] + 0.1, 0, b[1] - b[2] * 0.42, b[2] * 0.7, 0.12), (a[0] - 0.1, 0, a[1] - a[2] * 0.42, a[2] * 0.7, 0.12))
    m.bone = "Tail1"
    vent(m, 1, (0, -1.85, 3.12 + 0.68), "Tail1", 0.32, 4)
    crust(m, (0.55, -2.4, 3.55), (1, 0, 0.5), 0.3, rng, 5)
    m.bone = "Tail2"
    vent(m, 2, (0, -3.2, 3.2 + 0.62), "Tail2", 0.28, 4)
    crust(m, (-0.5, -3.6, 3.6), (-1, 0, 0.5), 0.26, rng, 4)
    m.bone = "Tail3"
    tendril(m, 3, wander((0, -5.0, 4.75), (0.4, -5.5, 6.6), rng, 6, (0.3, -0.3, 0), 0.1), 0.2, 0.06, "Tail3", "Mycel", beads="Glow", tip="Glow",
            tip_size=0.14)
    m.bone = "Spine"
    for side in (-1, 1):
        mantis_wing(m, side, (side * 0.3, -0.45, 3.65), rng)

    m.loft_z("Body", (3.0, 0, 0.0, 0.85, 0.85), (3.6, 0, 0.25, 0.75, 0.75))  # the long neck of a thorax, rearing up
    beam(m, "Body", (0, 0.2, 3.5), (0, 1.15, 6.15), 0.64, 0.68, 0.5)
    beam(m, "Belly", (0, 0.42, 3.55), (0, 1.38, 6.0), 0.36, 0.2, 0.28)
    ridge(m, "Accent", along((0, 0.05, 4.0), (0, 0.85, 5.9), 4), rng, 0.5, 0.16, 0.7)
    for side, letter in ((-1, "L"), (1, "R")):  # the blades, raised high and spread wide in a threat, hooked down to come down on you
        sh = Vector((side * 0.45, 1.05, 5.75))
        m.use(f"Arm{letter}", tuple(sh))
        coxa = sh + Vector((side * 0.6, 0.55, -0.55))
        femur = coxa + Vector((side * 1.1, 0.45, 1.75))
        blade_end = femur + Vector((side * 0.45, 1.6, -1.45))
        beam(m, "Body", tuple(sh), tuple(coxa), 0.46, None, 0.38)
        ball(m, "Accent", *coxa, 0.26, 6, 3)
        beam(m, "Body", tuple(coxa), tuple(femur), 0.44, 0.66, 0.36)
        for k in range(6):  # black spines along the inside of the femur
            p = coxa.lerp(femur, 0.15 + 0.14 * k) + Vector((-side * 0.12, 0.24, 0))
            point(m, "Accent", tuple(p), tuple(p + Vector((-side * 0.1, 0.36 + 0.08 * (k % 2), 0.05))), 0.12)
        ball(m, "Accent", *femur, 0.26, 6, 3)
        run = (blade_end - femur).normalized()
        down = run.cross(Vector((side, 0, 0))).normalized()
        if down.z > 0:
            down = -down
        plate(m, "Claw", tuple(femur), tuple(blade_end), tuple(down), 0.6, 0.14, 0.12)  # a broad blade, bone pale
        for k in range(8):  # its serrated edge, black
            p = femur.lerp(blade_end, 0.1 + 0.11 * k) + down * 0.26
            point(m, "Accent", tuple(p), tuple(p + down * 0.26 - run * 0.12), 0.11)
        thorn(m, "Claw", tuple(blade_end), tuple(blade_end + Vector((0, 0.15, -0.75))), 0.18, (0, 0.2, 0))
    m.bone = "Spine"

    m.use("Neck", (0, 1.25, 6.25))
    beam(m, "Body", (0, 1.12, 6.05), (0, 1.55, 6.6), 0.46)
    m.use("Head", (0, 1.55, 6.6), "Neck")
    hf = Frame(m, (0, 1.95, 6.85), turn(x=-0.22, y=0.08))  # glaring down at you
    zloft(hf, "Body", (-0.75, 0, 0.0, 0.7, 0.66), (0.3, 0, 0.0, 2.0, 0.86))  # a mantis's triangle of a head
    zloft(hf, "Body", (0.3, 0, 0.0, 2.0, 0.86), (0.58, 0, -0.06, 1.75, 0.66))
    mf = Frame(m, hf.at(0, 0.26, -0.6), hf.r)
    rot_maw(m, mf, 0.7, 0.6, 0.46, 0.22, 0.22, rng, gape=0.08, drop=0.45, upper="Body", lower="Accent", tooth=0.19, per_side=5, rows=2, gills=3,
            strands=2, across=3, mandibles=dict(x0=0.38, y0=0.06, z0=0.0, length=1.15, width=0.24, teeth=5, role="Accent"))
    for side in (-1, 1):  # burning eyes on the corners of its head, under brows slanting hard to the middle
        rot_eye(m, hf.at(side * 0.66, 0.3, 0.2), hf.r @ Vector((side * 0.35, 1, 0.0)), 0.5, -side, 0.85, rng=rng, veins=2, horns=1)
    for x, z in ((-0.2, 0.42), (0.2, 0.42), (0, 0.55)):
        bead(m, hf.at(x, 0.36, z), hf.r @ Vector((x, 1, 0.3)), 0.1)
    for side in (-1, 1):  # horns of bone swept back off its head
        thorn(m, "Claw", hf.at(side * 0.5, -0.2, 0.55), hf.at(side * 1.0, -1.4, 1.9), 0.28, tuple(hf.r @ Vector((side * 0.15, 0.2, 0.3))))
    for x, d, h, cr, ch in ((-0.25, (-0.35, -0.6, 1), 1.0, 0.34, 0.62), (0.3, (0.4, -0.5, 1), 1.25, 0.4, 0.72), (0.0, (0.05, -0.9, 0.7), 0.7, 0.26, 0.48)):
        sprout(m, hf.at(x, -0.45, 0.4), hf.r @ Vector(d), h, 0.09, cr, ch, rng)  # black ink caps bursting out of the back of its head
    for n, side in ((1, -1), (2, 1)):  # long feelers, twitching
        start = Vector(hf.at(side * 0.25, 0.45, 0.32))
        tendril(m, n, wander(tuple(start), tuple(start + hf.r @ Vector((side * 1.5, 1.4, 1.9))), rng, 7, (side * 0.3, 0.4, 0.2), 0.08), 0.09, 0.05,
                "Head", "Accent", beads=None)
    m.bone = "Head"
    m.head_centre = tuple(hf.at(0, 0.8, 0.0))
    return finish(m, 1.1)


def shroomageddon():
    """The boss: a colossal black titan on its knuckles that is more rot than beast. A ragged black cap pulled down over
    its head like a hood, seven burning eyes under it, bone horns and glowing morels for a crown, and a mouth that opens
    four ways, wide enough to swallow a house. Its chest is torn open on a glowing heart behind ribs of bone, a forest
    of black and deathly pale mushrooms grows on its back round a geyser of spores, mycelium whips thrash from its
    shoulders, and its tail ends in a club of bone spikes."""
    rng = random.Random(1406)
    m = monster("dino_Shroomageddon", Body="#2e2229", Accent="#191116", Belly="#553845", Claw="#e9dcbd", Heart="#2a1520",
                HeartGlow="#c8ff4c", Ridge="#221a1e", Pit="#b8ff3a")
    m.joint("Spine", (0, 0, 6.0))
    for side, letter in ((-1, "L"), (1, "R")):  # arms like tree trunks, walking on their knuckles
        sh = Vector((side * 2.25, 2.0, 7.6))
        m.use(f"Front{letter}", tuple(sh))
        elbow = Vector((side * 3.3, 2.55, 4.4))
        fist = Vector((side * 3.1, 3.25, 1.25))
        beam(m, "Body", tuple(sh + Vector((0, 0, 0.4))), tuple(elbow), 2.1, None, 1.55)
        ball(m, "Body", *elbow, 0.9, 8, 4)
        beam(m, "Body", tuple(elbow), tuple(fist), 1.55, None, 1.3)
        m.loft_z("Accent", (0.0, fist.x, fist.y + 0.15, 1.6, 1.5), (1.6, fist.x, fist.y, 1.45, 1.35))
        for k in range(4):  # long knuckle claws, hooked into the ground
            x = fist.x + (k - 1.5) * 0.38
            thorn(m, "Claw", (x, fist.y + 0.6, 0.6), (x + (k - 1.5) * 0.1, fist.y + 1.75, 0.05), 0.36, (0, 0.15, 0.3))
        for k in range(4):  # bone spikes out of its elbow and forearm
            p = elbow + Vector((side * 0.6, -0.35 + 0.35 * k, 0.25 - 0.45 * k))
            thorn(m, "Claw", tuple(p), tuple(p + Vector((side * 0.85, -0.45, 0.6 - 0.15 * k))), 0.4)
        for t, r_ in ((0.3, 0.55), (0.55, 0.45)):  # shelf fungi stepping up the forearm
            bracket(m, *(fist.lerp(elbow, t) + Vector((side * 0.66, -0.1, 0))), r_)
        crust(m, tuple(sh + Vector((side * 0.9, 0, 0.6))), (side, 0, 1), 0.8, rng, 7)
        crust(m, tuple(elbow + Vector((side * 0.5, 0.5, -0.4))), (side, 1, 0), 0.5, rng, 5)
        a, b = elbow + Vector((side * 0.3, 0.7, 0.1)), fist + Vector((-side * 0.1, 0.72, 0.7))  # a glowing thread, forking down the arm
        mid = a.lerp(b, 0.45) + Vector((side * 0.2, 0.05, 0))
        limb(m, "Vein", [tuple(a), tuple(mid), tuple(b)], 0.12, 0.07, joints=False)
        limb(m, "Vein", [tuple(mid), tuple(mid + Vector((side * 0.55, 0.1, -0.9)))], 0.09, 0.06, joints=False)
    for side, letter in ((-1, "L"), (1, "R")):  # hunched hind legs, clawed
        x = side * 1.9
        m.use(f"Back{letter}", (x, -2.6, 5.3))
        m.loft_z("Body", (2.2, x, -2.6, 1.15, 1.25), (5.45, x, -2.6, 1.8, 2.1))
        m.loft_z("Accent", (0.25, x, -2.55, 0.9, 0.95), (2.4, x, -2.6, 1.15, 1.25))
        m.loft_z("Body", (0, x, -2.25, 1.65, 1.9), (0.6, x, -2.35, 1.2, 1.35))
        for k in range(3):
            cx = x + (k - 1) * 0.55
            thorn(m, "Claw", (cx, -1.4, 0.3), (cx, -0.55, 0.03), 0.38, (0, 0, 0.2))
        bracket(m, x * 1.32, -2.6, 3.6, 0.42)
    m.bone = "Spine"

    body = ((-3.4, 0, 5.7, 2.8, 2.8), (2.6, 0, 7.4, 4.3, 4.4))
    m.loft_y("Body", *body)
    m.loft_y("Body", (-0.6, 0, 8.4, 3.0, 1.4), (2.2, 0, 9.3, 3.5, 1.6))  # the hunch of its shoulders
    m.loft_y("Belly", (-2.9, 0, 4.45, 2.0, 0.2), (2.2, 0, 5.3, 3.0, 0.25))
    ridge(m, "Claw", along((0, 1.9, 10.0), (0, -3.2, 7.3), 7), rng, 1.1, 0.42, 0.55)  # bone spikes down its spine
    for x, y, z, n in ((1.9, 0.6, 8.6, (1, 0, 0.6)), (-2.0, -1.4, 7.6, (-1, 0, 0.5)), (1.7, -2.4, 7.1, (1, 0, 0.6))):
        crust(m, (x, y, z), n, 0.7, rng, 7)

    # Its chest is torn open on the heart: a black hollow, the heart glowing in it and ribs of bone across it.
    cf = Frame(m, (0, 2.62, 7.0))
    slab(cf, "Socket", 0, 0, 0.0, 1.45, 0.1, 12, 0.85)
    egg(m, "Heart", (0, 2.62, 6.95), 0.85, 0.55, 1.05, 10, 6)
    for k in range(6):  # glowing seams down the heart
        a = math.pi * (0.1 + 0.8 * k / 5)
        pts = [(math.cos(a) * 0.88 * math.cos(lat), 2.62 + 0.57 * math.sin(a) * math.cos(lat), 6.95 + 1.07 * math.sin(lat)) for lat in (-1.1, -0.5, 0.1, 0.7, 1.2)]
        limb(m, "HeartGlow", pts, 0.1, 0.08, joints=False)
    for k in range(4):
        z = 6.1 + k * 0.55
        pts = [(-1.2, 2.62, z + 0.05), (-0.62, 3.14, z + 0.12), (0.0, 3.26, z + 0.15), (0.62, 3.14, z + 0.12), (1.2, 2.62, z + 0.05)]
        limb(m, "Claw", pts, 0.26, 0.2)
    for k in range(9):  # glowing threads running out of it all over its hide
        a = k * math.tau / 9 + 0.2
        p = Vector((math.cos(a) * 1.35, 2.6, 7.0 + math.sin(a) * 1.25))
        pts = [tuple(p)]
        on_side = 1.02 / max(abs(math.cos(a)), abs(math.sin(a)))
        for j in range(3):
            y = 2.3 - 1.1 * (j + 1)
            _, cx, cz, w0, h0 = ring_at(*body, max(y, -3.3))
            pts.append((math.cos(a) * on_side * w0 / 2, y, cz + math.sin(a) * on_side * h0 / 2))
        limb(m, "Vein", pts, 0.14, 0.08, joints=False)

    def back_top(x, y):
        _, cx, cz, w0, h0 = ring_at(*body, y)
        top = cz + h0 / 2 * math.sqrt(max(0.05, 1 - (2 * x / w0) ** 2))
        if -0.6 <= y <= 2.2 and abs(x) < 1.5:
            _, _, hz, _, hh = ring_at((-0.6, 0, 8.4, 3.0, 1.4), (2.2, 0, 9.3, 3.5, 1.6), y)
            top = max(top, hz + hh / 2)
        return top

    shrooms = ((-1.45, -0.4, (-0.55, 0.15, 1), 2.7, 0.36, 1.5, 1.6, "Cap", "CapDark", "bell"),
               (1.55, 0.6, (0.5, 0.2, 1), 3.1, 0.4, 1.65, 1.75, "Cap", "CapDark", "bell"),
               (-1.25, -2.6, (-0.45, -0.4, 1), 2.1, 0.3, 1.2, 1.3, "CapB", "CapBDark", "bell"),
               (1.25, -2.5, (0.5, -0.35, 1), 1.8, 0.26, 1.0, 1.1, "Cap", "CapDark", "cone"),
               (0.45, 1.8, (0.25, 0.45, 1), 1.1, 0.2, 0.7, 0.75, "CapB", "CapBDark", "bell"),
               (-0.6, 1.5, (-0.4, 0.3, 1), 0.8, 0.15, 0.5, 0.55, "Cap", "CapDark", "cone"))
    for x, y, d, h, r_, cr, ch, role, crown, shape in shrooms:  # a forest of black and deathly pale caps on its back
        sprout(m, (x, y, back_top(x, y) - 0.25), d, h, r_, cr, ch, rng, cap_role=role, crown=crown, shape=shape, sides=12 if cr > 1 else 8)
    gx, gy = 0.0, -1.45
    gz = back_top(gx, gy)
    prism(m, "Accent", gx, gy, gz - 0.3, gz + 0.35, 1.05, 0.85, 10, math.pi / 10)  # the geyser's crater
    vent(m, 1, (gx, gy, gz + 0.4), "Spine", 0.8, 6)
    vent(m, 2, (-1.75, 1.6, back_top(-1.75, 1.6) - 0.1), "Spine", 0.36, 4)

    pts = [(0, -3.3, 5.9), (0.2, -4.6, 5.4), (-0.15, -5.7, 4.8), (0.1, -6.5, 4.5)]  # tail: short and thick, a club of bone spikes
    widths = (2.2, 1.6, 1.15, 0.9)
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        m.use(f"Tail{i + 1}", a, f"Tail{i}" if i else "Spine")
        beam(m, "Body", a, b, widths[i], None, widths[i + 1])
        if i:
            m.stretch("Body", f"Tail{i}")
        thorn(m, "Claw", (a[0], (a[1] + b[1]) / 2, (a[2] + b[2]) / 2 + widths[i] * 0.4),
              (a[0], (a[1] + b[1]) / 2 - 0.4, (a[2] + b[2]) / 2 + widths[i] * 0.4 + 0.8), 0.32)
    club = Vector((0.1, -6.9, 4.5))
    ball(m, "Accent", *club, 0.9, 8, 4)
    for k in range(10):
        z = 1 - 2 * (k + 0.5) / 10
        a = k * 2.4
        d = Vector((math.sqrt(1 - z * z) * math.cos(a), math.sqrt(1 - z * z) * math.sin(a), z))
        if d.y > 0.6:
            continue
        thorn(m, "Claw", tuple(club + d * 0.7), tuple(club + d * 1.7), 0.32)
    m.bone = "Spine"

    for n, start, end, bow in ((1, (1.75, 1.3, 9.0), (4.6, 0.6, 11.6), (0.4, 0, 0.4)), (2, (-1.75, 1.0, 9.0), (-4.4, 0.2, 12.0), (-0.3, 0, 0.5)),
                               (3, (1.5, -2.6, 7.9), (3.9, -4.8, 9.8), (0.5, 0, 0.5)), (4, (-1.5, -2.7, 7.8), (-3.7, -5.0, 10.3), (-0.4, 0, 0.6))):
        tendril(m, n, wander(start, end, rng, 7, bow, 0.22), 0.5, 0.14, "Spine", "Mycel", beads="Glow", tip="Glow", tip_size=0.3)
        m.bone = "Spine"

    m.use("Neck", (0, 2.4, 8.2))
    beam(m, "Body", (0, 1.9, 7.95), (0, 3.6, 8.3), 2.4, 2.1, 1.8)
    m.stretch("Body", "Spine")
    m.use("Head", (0, 3.75, 8.15), "Neck")
    hf = Frame(m, (0, 4.75, 8.1), turn(x=-0.16, y=-0.05))  # low, thrust out at you
    hf.box("Body", 0, -0.1, 0.25, 2.6, 2.1, 2.0)
    mf = Frame(m, hf.at(0, 0.6, -0.65), hf.r @ turn(x=0.08))
    rot_maw(m, mf, 2.5, 1.75, 1.6, 0.62, 0.58, rng, gape=0.24, drop=0.6, upper="Body", lower="Accent", tooth=0.6, per_side=9, rows=2, gills=7,
            strands=5, lift=0.0, across=5, tip_h=0.32, nostrils=True,
            mandibles=dict(x0=1.3, y0=0.05, z0=-0.15, length=2.2, width=0.55, height=1.25, teeth=9, curl=0.7, role="Accent"))
    for side in (-1, 1):  # seven burning eyes under the hood: two great ones, five round them
        rot_eye(m, hf.at(side * 0.62, 0.98, 0.55), hf.r @ Vector((side * 0.1, 1, 0)), 1.0, -side, 0.7, rng=rng, veins=4, horns=1)
    for x, y, z, r in ((0.0, 1.0, 0.95, 0.2), (-1.2, 0.8, 0.9, 0.2), (1.22, 0.82, 0.85, 0.18), (-1.25, 0.86, 0.15, 0.14), (1.28, 0.88, 0.2, 0.15)):
        bead(m, hf.at(x, y, z), hf.r @ Vector((x * 0.7, 1, 0.1)), r)
    hood = ragged_cap(m, "Cap", hf.at(0, -0.45, 1.35), 2.4, 1.9, hf.r @ turn(x=-0.1), rng, crown="CapDark", under="GillGlow", shape="bell",
                      tatters=16, length=0.25)
    for k in range(7):  # a crown of bone horns bursting up through the cap, curving forward
        a = math.pi / 2 + (k - 3) * 0.5
        t = 0.5 if k % 2 else 0.36
        rr = 2.4 * share(((0, 1.0), (0.3, 0.9), (0.6, 0.72), (0.85, 0.46), (1, 0.14)), t)
        base = hood.at(math.cos(a) * rr * 0.92, math.sin(a) * rr * 0.92, 1.9 * t - 0.05)
        out = (hood.r @ Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 1))).normalized()
        length = (2.3 if k % 2 == 0 else 1.5) * (1.15 if k == 3 else 1)
        thorn(m, "Claw", base, tuple(Vector(base) + out * length + hood.r @ Vector((0, 0.55, 0))), 0.5 if k % 2 == 0 else 0.38,
              tuple(hood.r @ Vector((0, 0.4, 0))))
    m.head_centre = tuple(hf.at(0, 1.6, 0.2))
    return finish(m, 1.0)


ALL = [toad_rage, morel_panic, antagonist, sporantula, gillotine, shroomageddon]


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
    light_up(roots, GLOW_ROLES, GLOW_STRENGTH)
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
              f"biggest {max((sum(len(x) - 2 for x in f), r) for r, (_, f) in model.parts.items())}, "
              f"box {[round(min(v[i] for vs, _ in model.parts.values() for v in vs), 1) for i in range(3)]} to "
              f"{[round(max(v[i] for vs, _ in model.parts.values() for v in vs), 1) for i in range(3)]}")


def pounce_video(models, renders, name):
    """A close look at each monster in turn through four seconds of its walk, the camera drifting round it: its
    thrashing, one pounce and the spores pouring out of it, which the lineup video is too far away to show."""
    import subprocess

    import bpy
    scene = bpy.context.scene
    roots = [bpy.data.objects[model.name] for model in models]
    player = bpy.data.objects.get("Player")
    if player:
        kit.set_visible([player], [])
    frames = renders / "pounce_frames"
    frames.mkdir(exist_ok=True)
    data = bpy.data.cameras.new("Close")
    data.lens = 40
    camera = bpy.data.objects.new("Cam_Close", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = 960, 720
    number = 0
    for model, root in zip(models, roots):
        kit.set_visible(roots, [root])
        root.animation_data.action = bpy.data.actions[f"{model.name}_Walk"]
        scene.frame_set(0)
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 3)
        for f in range(0, WALK_PREVIEW, 2):
            scene.frame_set(f)
            a = math.radians(30 + 35 * f / WALK_PREVIEW)
            camera.location = centre + Vector((math.sin(a), math.cos(a), 0.32)) * reach * 0.9
            camera.rotation_euler = (centre - camera.location).to_track_quat("-Z", "Y").to_euler()
            scene.render.filepath = str(frames / f"f{number:04d}.png")
            bpy.ops.render.render(write_still=True)
            number += 1
        root.animation_data.action = None
    bpy.data.objects.remove(camera)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "15", "-i", str(frames / "f%04d.png"), "-pix_fmt", "yuv420p",
                    str(renders / name)], check=True)
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
    build_and_render(models, RENDERS, HERE / f"{BLEND}.blend", "spore_hollow_animation_preview.mp4", sky=SKY, ground=FLOOR,
                     glow_roles=GLOW_ROLES, spacing=20, animate_fn=animate, walk_frames=WALK_PREVIEW, glow=GLOW_STRENGTH)
    import bpy
    light_up([bpy.data.objects[model.name] for model in models], GLOW_ROLES, GLOW_STRENGTH)  # build_and_render put it out to save
    pounce_video(models, RENDERS, "spore_hollow_pounce_preview.mp4")


if __name__ == "__main__":
    main()
