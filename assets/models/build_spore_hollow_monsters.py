"""Builds Spore Hollow's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_spore_hollow_monsters.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_spore_hollow_monsters.py    (stills only, for trying faces)
    ONLY=toad_rage,sporantula QUICK=1 ...                                      (just those)

Saves spore_hollow_monsters.blend and renders to design/world/monsters_spore_hollow/: stills of each, the lineup, and
two videos, spore_hollow_animation_preview.mp4 (all six walking and roaring, as on every map) and
spore_hollow_pounce_preview.mp4 (each in turn close up, through its pounce). The map's props are in build_spore_hollow.py.

Map 14, a hollow at the bottom of the world where no sun ever reached and the fungus grew as big as castles. The
owner asked for monsters that suit it, "very aggressive and nice, more aggressive than the 13th map", built and
animated in Blender. So down here the fungus is the predator: it has grown through everything that lives in the
hollow and made it worse. All six are hostile, the commons too (their jokes stay in the names and one thing each),
and none of them is ever still: on top of map 13's thrashing they pounce at you, and spores pour out of them.

Two ideas run through all six. The infected eye: a glowing chartreuse iris with a black bar of a pupil lying across
it, a goat's or a toad's, and threads of glowing mycelium creeping in over the white from its rim (on the fierce
ones there is no white at all, just a glowing orb sunk in a black socket, the threads spreading out of it over the
face, under a brow with little mushrooms growing out of it). And the gill maw: a jaw hanging open on crooked teeth,
the roof of the mouth the underside of a mushroom, gills glowing all the way back to a glowing throat, and threads
of glowing mycelium stretched between the jaws. Fungus grows out of all of them: caps, shelf fungi and stalks.

  Toad Rage       a squat, furious toad with a toadstool for a hat, jammed down over its eyes into a scowl, the gills
                  under the brim glowing down on them. A mouth as wide as it is, a sticky tongue whipping about,
                  warts all over its back and two of them torn open, puffing spores
  Morel Panic     a gaunt ghoul bent double, with no head of its own, only a morel: a tall honeycomb hood glowing
                  amber out of every pit and an eye in a dozen of them, each rolling its own way. Under it a long jaw
                  hangs open on two rows of teeth; its claws drag on the ground; spores rise off the tip of its head
  Antagonist      a giant ant the fungus got to first: rust-red armour, mandibles like shears that never stop
                  clacking, two glowing orbs for eyes, and tall pale stalks with glowing clubs bursting out of its
                  head and back, whipping about as if looking for the next one
  Sporantula      a spider whose back is a mushroom cap freckled with glowing specks, on eight long stalks of legs;
                  eight infected eyes under the brim, fangs that never stop chattering, a glowing drop on each, and a
                  puffball for an abdomen, torn open in two places and pouring spores
  Gillotine       a towering mantis under a chocolate cap, its forelegs two serrated blades held up and ready, side
                  jaws round a mouth of teeth, its wings stood up behind it in a threat display, a glowing eye on
                  each and lilac light in their veins
  Shroomageddon   the boss: the hollow's own god, a colossal titan on its knuckles that is more fungus than beast. A
                  forest of glowing mushrooms on its back round a geyser of spores, the mycelium heart glowing in its
                  open chest, whips of mycelium, a cap pulled down over its face like a hood with a crown of glowing
                  morels, five eyes, and a mouth that opens four ways

What moves. The usual walk, idle and roar, map 13's thrashing (Lash and Snap bones: THRASH in DinoLifeController,
thrash_of in build_thorn_kingdom_monsters.py), and two things new on this map, in DinoLifeController (VENT, POUNCE)
and here (vent_rise, pounce_of), the same numbers in both:
  - Vent<n> bones: a column of spore clouds over a vent in the hide, lifted one VENT_GAP every VENT_PERIOD and
    dropped back, so spores pour out for ever (each cloud only goes as far as where the one above it began). The
    clouds are added after grow(), so the gap is the same on every monster.
  - A monster with Vent bones pounces once every 4 seconds: it rears back, front legs up and side jaws spread, then
    lunges, neck down, jaw flung open, arms raking, side jaws slamming shut, and slowly draws back. The side jaws
    (MandL, MandR) gnash the rest of the time and open wide in the roar.
Everything repeats every 4 seconds, so the preview's 4-stride walk and 8-second idle loop seamlessly.

Rules the game adds: Jaw sits in front of Tail1 (or the Spine), since that's how the game tells which way a monster
faces. Only the main eyes use the Pupil role, which the reveal aims at; spare eyes use Slit.

Glowing parts are EyeGlow, GillGlow, Vein, Spore, Speck, Glow, Pit, HeartGlow and Lilac (Neon in the game,
shared/Roles.luau; Lilac is new). Skin roles Body, Accent, Belly and Claw take the colour mutations; caps, shelves,
stalks, spore clouds and the face keep their colour. Built at the first map's size; the game scales them by
Config/Biomes standardScale. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0. No five- or six-pointed stars
or crosses anywhere (the owner ruled them out on map 10).

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
from build_forest import Model, biped_legs  # noqa: E402
from build_spore_hollow import (BELL, CAP, CAP_B, CAP_B_DARK, CAP_DARK, CLOUD, CLOUD_SPORES, GILL, GLOW, HEART, MYCEL, PIT,  # noqa: E402
                                PUFF, PUFF_B, RIDGE, SHELF, SHELF_DARK, SPECK, SPORE, STALK, STALK_SHADE, VEIN, WART, bracket, cap,
                                share, specks)
from build_starfall_crater import ball  # noqa: E402
from build_thorn_kingdom_monsters import (W, WALK_PREVIEW, aim, along, clawed_leg, crooked_teeth, point, ridge, slab, thorn,  # noqa: E402
                                          thrash_of, wander, yloft, zloft)
from build_volcano import idle_pose as volcano_idle, prism, ring_at, roar, top_of, walk_pose as volcano_walk  # noqa: E402
from map_kit import limb, plate  # noqa: E402
from monster_stage import build_and_render, light_up, set_sky  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_spore_hollow"
BLEND = "spore_hollow_monsters"  # for check_map.py and export_fbx.py

GLOW_ROLES = {"EyeGlow", "GillGlow", "Vein", "Spore", "Speck", "Glow", "Pit", "HeartGlow", "Lilac"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket", "Slit"})
GLOW_STRENGTH = 1.0  # the glowing roles' strength in the renders

FACE = {"Pupil": "#120d08", "Slit": "#120d08", "Socket": "#0b0806", "EyeGlow": "#d6ff3c", "EyeWhite": "#eee8cc", "Highlight": "#ffffff",
        "Mouth": "#1a100b", "Teeth": "#ece0be", "Tongue": "#b8455e", "GillGlow": GILL, "Vein": VEIN, "Spore": SPORE, "Speck": SPECK,
        "Glow": GLOW, "Puff": PUFF, "PuffB": PUFF_B, "Puffskin": "#e2d7b0", "Cap": CAP, "CapDark": CAP_DARK, "Stalk": STALK,
        "StalkShade": STALK_SHADE, "Mycel": MYCEL, "Shelf": SHELF, "ShelfDark": SHELF_DARK}
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


def sprout(m, base, direction, h, r, cap_r, cap_h, rng, cap_role="Cap", crown="CapDark", under="GillGlow", n_specks=0, shape="dome",
           stalk="Stalk", sides=8):
    """A mushroom growing out of the monster at base, along direction: a stalk h long and a cap on it, gills glowing
    under it and n_specks glowing specks on it. Returns the cap's frame."""
    d = Vector(direction).normalized()
    top = Vector(base) + d * h
    tube(m, stalk, tuple(base), tuple(top + d * cap_h * 0.3), r, r * 0.8, 6 if r < 0.2 else 8)
    # A rim at least 0.045 deep, so the glowing gills under even a tiny cap sit clear of its edge (no flicker).
    f = cap(m, cap_role, tuple(top), cap_r, cap_h, shape, up_along(d), sides, crown, under, max(0.045, cap_h * 0.16))
    if n_specks:
        specks(m, "Speck", f, cap_r, cap_h, shape, n_specks, cap_r * 0.17, rng)
    return f


def jointed_leg(m, points, w, role="Belly", ring="StalkShade", tip="Claw", taper=0.5):
    """A long thin leg through points (hip, joints, foot): segments tapering from w, a knob at each joint and a dark
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
    tendril, a tongue, a thread of silk. beads: a glowing role for knots along it; tip: a role for a bulb on its end.
    Leaves m.bone on its last bone, so more can go on the end; returns the end point."""
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


# ---------------------------------------------------------------------- the infected eye and the gill maw


def spore_eye(m, centre, look, r, rng, pupil="Pupil", iris=0.56, veins=5, off=(0.0, 0.0), sprouts=0, role="EyeWhite"):
    """The infected eye: a bulging ball, a glowing chartreuse iris with a black bar of a pupil lying across it,
    threads of glowing mycelium creeping in over the white from its rim, and with sprouts, tiny mushrooms growing out
    of its lid. off slides the iris across the eye: rolling, not looking at you."""
    f = Frame(m, centre, aim(look))
    ball(m, role, *centre, r, 8, 5)
    n = r * 0.96
    u, v = off[0] * r, off[1] * r
    slab(f, "EyeGlow", u, v, n, r * iris, r * 0.1, 10)
    f.box(pupil, u, n + r * 0.065, v, r * iris * 1.3, r * 0.05, r * iris * 0.36)
    f.box("Highlight", u - r * iris * 0.46, n + r * 0.1, v + r * iris * 0.52, r * 0.16, r * 0.03, r * 0.16)
    edge = math.asin(min(iris * 1.1, 0.95))
    for _ in range(veins):
        a = rng.uniform(0, math.tau)
        mid_t = (1.4 + edge) / 2
        pts = [on_ball(f, r * 1.02, 1.4, a), on_ball(f, r * 1.02, mid_t, a + rng.uniform(-0.35, 0.35)), on_ball(f, r * 1.02, edge, a + rng.uniform(-0.2, 0.2))]
        for p, q in zip(pts, pts[1:]):
            beam(m, "Vein", p, q, r * 0.085, None, r * 0.055)
        beam(m, "Vein", pts[1], on_ball(f, r * 1.02, mid_t - 0.2, a + rng.choice((-1, 1)) * 0.5), r * 0.06, None, r * 0.04)
    for k in range(sprouts):
        a = math.pi / 2 + (k - (sprouts - 1) / 2) * 0.7  # along the top of the eye
        base = Vector(on_ball(f, r * 0.94, 0.95, a))
        out = (base - Vector(centre)).normalized() + Vector((0, 0, 0.7))
        sprout(m, base, out, r * 0.5, r * 0.07, r * 0.26, r * 0.18, rng, crown=None, sides=6)


def spore_glare(m, centre, look, size, inner, slant=0.55, pupil="Pupil", brow="Accent", sprouts=2, veins=4, rng=None, lid=True):
    """The infected eye on the fierce ones: no white, one glowing orb sunk in a black socket with a black bar across it,
    glowing threads of mycelium spreading out of the socket over the face, under a slab of brow slanting hard down to
    the nose (inner is +1 if the nose lies at +X) with little mushrooms growing out of it."""
    rng = rng or random.Random(int(size * 1000) + int(inner))
    f = Frame(m, centre, aim(look) @ turn(y=inner * slant * 0.5))
    slab(f, "Socket", 0, 0, 0.03, size * 0.52, 0.08, 10, 1.4)
    slab(f, "EyeGlow", 0, -size * 0.02, 0.09, size * 0.42, 0.05, 10, 1.15)
    f.box(pupil, 0, 0.125, -size * 0.03, size * 0.66, 0.03, size * 0.14)
    f.box("Highlight", -size * 0.2, 0.15, size * 0.15, size * 0.1, 0.02, size * 0.1)
    b = Frame(m, centre, aim(look))
    for k in range(veins):  # threads out of the socket, down and out over the cheek
        a = math.radians(-150 + 120 * k / max(veins - 1, 1) + rng.uniform(-12, 12))
        p = Vector((math.cos(a) * size * 0.68, 0.035, math.sin(a) * size * 0.5))
        pts = [p]
        for _ in range(2):
            a += rng.uniform(-0.45, 0.45)
            p = p + Vector((math.cos(a) * size * 0.42, 0.0, math.sin(a) * size * 0.42))
            pts.append(p)
        for p, q in zip(pts, pts[1:]):
            beam(m, "Vein", b.at(*p), b.at(*q), size * 0.075, None, size * 0.05)
    out, nose = -inner * size * 1.0, inner * size * 0.82
    drop = slant * size
    b.beam(brow, (out, 0.1, size * 0.5 + drop * 0.5), (nose, 0.2, size * 0.42 - drop * 0.6), size * 0.42, size * 0.5, size * 0.34)
    if lid:
        b.beam(brow, (out * 0.9, 0.1, -size * 0.5), (nose * 0.9, 0.12, -size * 0.58), size * 0.26, size * 0.18, size * 0.2)
    for k in range(sprouts):  # little mushrooms growing out of the brow
        t = 0.12 + 0.36 * k
        p = Vector((out + (nose - out) * t, 0.05, size * 0.72 + drop * 0.5 * (1 - t) - drop * 0.1))
        sprout(m, b.at(*p), b.r @ Vector((-inner * 0.35, -0.35, 1)), size * 0.5, size * 0.07, size * 0.3, size * 0.21, rng, crown=None, sides=6)


def bead_eye(m, centre, look, r, pupil="Slit", off=(0.0, 0.0)):
    """A spider's eye gone over: a glossy black bead, a glowing ring of an iris and a black bar across it, no white."""
    f = Frame(m, centre, aim(look))
    ball(m, "Socket", *centre, r, 8, 4)
    u, v = off[0] * r, off[1] * r
    slab(f, "EyeGlow", u, v, r * 0.93, r * 0.64, r * 0.12, 10)
    f.box(pupil, u, r * 1.0, v, r * 0.86, r * 0.05, r * 0.24)
    f.box("Highlight", u - r * 0.32, r * 1.02, v + r * 0.34, r * 0.17, r * 0.03, r * 0.17)


def orb_eye(m, centre, look, r, inner, pupil="Pupil", brow="Accent", slant=0.6):
    """A mantis's great eye gone over: a bulging glowing orb with a black bar across it, set in a black rim, under a
    brow slanting down to the middle (inner is +1 if the middle lies at +X)."""
    f = Frame(m, centre, aim(look))
    ball(m, "Socket", *f.at(0, -r * 0.3, 0), r * 1.04, 8, 4)
    ball(m, "EyeGlow", *centre, r, 8, 5)
    f.box(pupil, 0, r * 0.97, -r * 0.05, r * 1.15, r * 0.07, r * 0.27)
    f.box("Highlight", -r * 0.36, r * 0.95, r * 0.36, r * 0.2, r * 0.07, r * 0.2)
    f.beam(brow, (-inner * r * 1.2, r * 0.15, r * (0.8 + 0.3 * slant)), (inner * r * 0.8, r * 0.7, r * (0.62 - 0.45 * slant)), r * 0.5, r * 0.46, r * 0.36)


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
        size = width * rng.uniform(0.75, 1.15) * (1.4 if k == teeth // 2 else 1)
        base = p + Vector((-side * width * 0.3, 0, 0))
        point(m, "Teeth", f.at(*base), f.at(*(base + inward * size)), width * 0.42)
    m.bone = parent


def gill_maw(m, f, skull_w, length, snout_w, upper_h, lower_h, rng, gape=0.16, drop=0.34, upper="Body", lower="Accent", tooth=0.3,
             per_side=5, head="Head", jaw="Jaw", tongue=True, gills=5, strands=2, rows=1, lift=0.1, mandibles=None, across=3):
    """The gill maw, built in frame f, whose origin is the middle of the mouth's back and whose +Y is out of the mouth:
    an upper jaw on the head bone, its roof the underside of a mushroom with gills glowing all the way back to a
    glowing throat; a lower jaw on the jaw bone hanging open by drop (radians) at rest; crooked teeth, two rows of
    them with rows=2; threads of glowing mycelium stretched between the jaws. mandibles (a dict of mandible()'s
    arguments) adds side jaws. Returns the lower jaw's frame and length, for a tongue."""
    m.bone = head
    yloft(f, upper, (-0.05, 0, gape / 2 + upper_h * 0.5, skull_w * 0.96, upper_h), (length, 0, gape / 2 + upper_h / 2 + lift, snout_w, upper_h))
    yloft(f, "Mouth", (0, 0, gape / 2 - 0.03, skull_w * 0.84, 0.06), (length * 0.95, 0, gape / 2 + lift * 0.95 - 0.03, snout_w * 0.86, 0.06))
    open_h = gape + drop * length * 0.8 + 0.2
    f.box("Mouth", 0, 0.03, gape / 2 - open_h / 2, skull_w * 0.88, 0.12, open_h)
    f.box("GillGlow", 0, 0.11, gape / 2 - open_h * 0.5, skull_w * 0.5, 0.06, open_h * 0.64)
    for k in range(gills):  # the roof of the mouth: gills fanning forward from the throat
        x = (k - (gills - 1) / 2) / max(gills - 1, 1) * skull_w * 0.62
        xb = x * snout_w / skull_w * 0.92
        beam(m, "GillGlow", f.at(x, length * 0.06, gape / 2 - 0.08), f.at(xb, length * 0.86, gape / 2 + lift * 0.86 - 0.08), 0.06, 0.12, 0.05)

    def width(y):
        return skull_w * 0.96 + (snout_w - skull_w * 0.96) * y / length

    def roof(y):
        return gape / 2 + lift * y / length

    crooked_teeth(m, f, width, roof, length, tooth, per_side, rng, False, across=across)
    if rows > 1:
        crooked_teeth(m, f, lambda y: width(y) * 0.62, roof, length * 0.8, tooth * 0.72, max(per_side - 2, 2), rng, False, across=0)

    hinge = f.at(0, -0.05, -gape / 2)
    m.use(jaw, hinge, head)
    lf = Frame(m, hinge, f.r @ turn(x=-drop))
    ll = length * 0.95
    yloft(lf, lower, (0, 0, -lower_h * 0.55, skull_w * 0.86, lower_h * 1.1), (ll, 0, -lower_h * 0.5, snout_w * 0.92, lower_h))
    yloft(lf, "Mouth", (0, 0, 0.0, skull_w * 0.72, 0.06), (ll * 0.95, 0, 0.0, snout_w * 0.76, 0.06))

    def low_width(y):
        return skull_w * 0.86 + (snout_w * 0.92 - skull_w * 0.86) * y / ll

    crooked_teeth(m, lf, low_width, lambda y: 0.0, ll, tooth * 0.85, per_side, rng, True, across=max(across - 1, 0))
    if rows > 1:
        crooked_teeth(m, lf, lambda y: low_width(y) * 0.6, lambda y: 0.0, ll * 0.8, tooth * 0.62, max(per_side - 2, 2), rng, True, across=0)
    if tongue:
        lf.beam("Tongue", (0, ll * 0.1, 0.06), (0, ll * 0.8, 0.08), snout_w * 0.42, 0.1, snout_w * 0.3)
    for k in range(strands):  # threads of mycelium stretched between the jaws
        x = (k - (strands - 1) / 2) * skull_w * 0.5 / max(strands - 1, 1) + (0.2 * skull_w if strands == 1 else 0)
        y = length * (0.22 + 0.12 * (k % 2))
        beam(m, "Vein", f.at(x, y, roof(y) - 0.02), lf.at(x * 0.95, y * 0.95, 0.03), 0.06, None, 0.04)
        m.stretch("Vein", head)
    if mandibles:
        for side in (-1, 1):
            mandible(m, f, side, rng=rng, parent=head, **mandibles)
    m.bone = head
    return lf, ll


# ---------------------------------------------------------------------- the common ones


def toad_rage():
    """A squat, furious toad with a toadstool for a hat, cocked over one eye, and brows slammed down over both. A mouth as
    wide as it is, hanging open on crooked teeth with glowing gills for a roof, a sticky tongue whipping about, warts
    all over its back, a few of them glowing, and two of them torn open, puffing spores."""
    rng = random.Random(1401)
    m = monster("dino_ToadRage", Body="#7f7d3c", Accent="#525526", Belly="#d9cc8f", Claw="#2a2216", Wart="#a59d58")
    m.joint("Spine", (0, -0.3, 1.3))
    bc, brx, bry, brz = Vector((0, -0.45, 1.25)), 1.45, 1.62, 1.05
    egg(m, "Body", bc, brx, bry, brz, 12, 7)
    m.loft_y("Belly", (-1.5, 0, 0.32, 1.7, 0.2), (0.75, 0, 0.5, 2.2, 0.22))

    def top(x, y):
        return bc.z + brz * math.sqrt(max(0.0, 1 - (x / brx) ** 2 - ((y - bc.y) / bry) ** 2))

    for _ in range(26):  # warts all over its back, a few of them glowing
        a, e = rng.uniform(0, math.tau), rng.uniform(0.12, 1.25)
        p = bc + Vector((brx * math.cos(e) * math.cos(a), bry * math.cos(e) * math.sin(a), brz * math.sin(e)))
        if p.y > 0.55:
            continue
        r_ = rng.uniform(0.11, 0.2)
        ball(m, "Wart", *p, r_, 6, 3)
        if rng.random() < 0.3:
            m.block("Speck", p.x, p.y, p.z + r_ * 0.85, r_ * 0.7, r_ * 0.7, r_ * 0.4)
    for x, y in ((0.45, -0.3), (-0.7, -1.4), (0.9, -1.05)):  # little mushrooms come up through its skin
        sprout(m, (x, y, top(x, y) - 0.1), (rng.uniform(-0.35, 0.35), rng.uniform(-0.3, 0.1), 1), 0.4, 0.06, 0.25, 0.18, rng, crown=None)
    for n, x, y in ((1, -0.55, -0.6), (2, 0.5, -1.25)):  # two warts torn open, puffing spores
        z = top(x, y)
        ball(m, "Puffskin", x, y, z - 0.06, 0.36, 8, 4)
        vent(m, n, (x, y, z + 0.22), "Spine", 0.32, 4)

    for side, bone in ((-1, "FrontL"), (1, "FrontR")):  # stubby arms, fingers splayed, claws out
        sh = (side * 1.05, 0.55, 1.15)
        m.use(bone, sh)
        elbow = (side * 1.6, 0.85, 0.7)
        wrist = (side * 1.5, 1.35, 0.24)
        beam(m, "Body", sh, elbow, 0.64, None, 0.52)
        ball(m, "Body", *elbow, 0.3, 6, 3)
        beam(m, "Accent", elbow, wrist, 0.5, None, 0.42)
        m.block("Belly", wrist[0], wrist[1] + 0.12, 0.13, 0.62, 0.52, 0.24)
        for k in range(4):
            a = side * (-0.5 + k * 0.42)
            d = Vector((math.sin(a), math.cos(a), 0))
            base = Vector((wrist[0], wrist[1] + 0.2, 0.12))
            tip = base + d * 0.6
            beam(m, "Belly", tuple(base), tuple(tip), 0.17, 0.14, 0.13)
            thorn(m, "Claw", tuple(tip), tuple(tip + d * 0.34 + Vector((0, 0, -0.08))), 0.12)
    for side, bone in ((-1, "BackL"), (1, "BackR")):  # big folded thighs, long toes splayed forward
        m.use(bone, (side * 1.0, -1.0, 1.05))
        x = side * 1.32
        egg(m, "Body", (x, -1.05, 0.88), 0.5, 0.95, 0.62, 8, 5)
        m.loft_y("Accent", (-1.75, x * 1.08, 0.3, 0.55, 0.5), (-0.35, x * 1.12, 0.28, 0.48, 0.42))
        ankle = Vector((x * 1.12, -0.3, 0.14))
        for k in range(4):
            a = side * (0.15 + k * 0.32)
            d = Vector((math.sin(a), math.cos(a), 0))
            tip = ankle + d * (0.95 - 0.1 * abs(k - 1.5))
            beam(m, "Belly", tuple(ankle), tuple(tip), 0.18, 0.12, 0.14)
            thorn(m, "Claw", tuple(tip), tuple(tip + d * 0.3 + Vector((0, 0, -0.06))), 0.12)
    m.bone = "Spine"

    m.use("Neck", (0, 0.3, 1.7))
    yc, zc, w, d, h = 1.0, 1.95, 2.5, 1.3, 1.05
    m.head_joint(yc, d, zc, h)
    hf = Frame(m, (0, yc, zc), turn(x=-0.05, y=0.06))
    hf.box("Body", 0, 0, 0.05, w, d, h)
    mf = Frame(m, hf.at(0, d / 2 - 0.2, -0.32), hf.r)
    lf, ll = gill_maw(m, mf, w * 0.95, 0.72, w * 0.8, 0.46, 0.42, rng, gape=0.12, drop=0.32, upper="Body", lower="Belly", tooth=0.24,
                      per_side=7, tongue=False, gills=6, strands=2, lift=0.04)
    # The tongue: a whip of its own, lolling out of the mouth and lashing about.
    tendril(m, 1, [lf.at(0.15, ll * 0.25, 0.08), lf.at(0.3, ll * 0.95, 0.14), lf.at(0.6, ll * 1.6, 0.06), lf.at(0.95, ll * 2.1, -0.18),
                   lf.at(1.25, ll * 2.4, -0.48), lf.at(1.5, ll * 2.4, -0.7), lf.at(1.78, ll * 2.2, -0.72)],
            0.44, 0.26, "Jaw", "Tongue", beads=None, tip="Tongue", tip_size=0.3)
    m.bone = "Head"
    for side, r, off in ((-1, 0.54, (0.12, -0.1)), (1, 0.47, (-0.15, 0.04))):  # bulging up off the front corners, mismatched
        spore_eye(m, hf.at(side * 0.8, 0.3, 0.6), hf.r @ Vector((side * 0.22, 1, 0.08)), r, rng, off=off, veins=5)
        hf.beam("Accent", (side * 1.32, 0.12, 1.12), (side * 0.22, 0.86, 0.72), 0.34, 0.3, 0.26)  # brows slammed down to the nose
    hat = cap(m, "Cap", hf.at(0.1, -0.5, 0.88), 1.0, 0.85, "dome", hf.r @ turn(x=-0.22, y=0.3), 12, crown="CapDark", under="GillGlow")
    specks(m, "Speck", hat, 1.0, 0.85, "dome", 7, 0.2, rng)
    m.head_centre = tuple(hf.at(0, d / 2 + 0.35, 0.3))
    return finish(m, 0.95)


def morel_hood(m, f, r, h, rng, cols=8, rows=5, ridge_role="Ridge", pit="Pit"):
    """A morel for a head, in frame f, its base at f's origin and rising up f's Z: a glowing core and over it a
    honeycomb of ridges, amber light glowing out of every pit. Returns the pits as (centre, outward, size)."""
    prof = ((0, 1.0), (0.18, 1.06), (0.45, 0.95), (0.7, 0.72), (0.88, 0.42), (1.0, 0.14))

    def rad(t):
        return r * share(prof, t)

    for (t0, s0), (t1, s1) in zip(prof, prof[1:]):
        f.prism(pit, 0, 0, h * t0, h * t1, r * s0 * 0.9, r * s1 * 0.9, cols * 2)
    rings = [0.03 + 0.9 * k / rows for k in range(rows + 1)]
    w = r * 0.15
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


def morel_panic():
    """A gaunt ghoul bent double, with no head of its own, only a morel: a tall honeycomb hood glowing amber out of
    every pit, and an eye in a dozen of the pits, each rolling its own way. Under it a long jaw hangs open on two rows
    of teeth, two mismatched eyes glare from under the hood's rim, its claws drag on the ground, whips of mycelium
    lash from its shoulders and spores rise off the tip of its head."""
    rng = random.Random(1402)
    m = monster("dino_MorelPanic", Body="#a99d86", Accent="#6c604e", Belly="#d7ccb0", Claw="#211912", Ridge=RIDGE, Pit=PIT)
    m.joint("Spine", (0, -0.2, 2.6))
    biped_legs(m, 0.55, -0.2, 2.6, 0.55, 1.3, 0.38, 1.0, 0.26)
    t = Frame(m, (0, -0.2, 2.5), turn(x=-0.62, y=0.1))  # bent nearly double, and over to one side
    zloft(t, "Accent", (-0.15, 0, 0, 0.95, 0.75), (0.35, 0, 0, 1.0, 0.8))
    zloft(t, "Body", (0.3, 0, 0, 0.92, 0.72), (1.4, 0, 0.05, 1.15, 0.82))
    zloft(t, "Body", (1.35, 0, 0.05, 1.15, 0.82), (2.3, 0, 0.12, 1.6, 1.05))
    for k in range(4):  # ribs showing
        z = 1.5 + k * 0.2
        for side in (-1, 1):
            t.beam("Belly", (side * 0.66, 0.3, z), (side * 0.16, 0.5, z - 0.1), 0.1, 0.1, 0.08)
    ridge(m, "Accent", [t.at(0, -0.42, z) for z in (0.5, 0.85, 1.2, 1.55, 1.9, 2.2)], rng, 0.38, 0.24, 0.3)
    bracket(m, *t.at(0.42, -0.4, 1.25), 0.42)
    bracket(m, *t.at(-0.48, -0.44, 1.75), 0.34)
    bracket(m, *t.at(0.5, -0.35, 2.0), 0.26)

    for side, letter in ((-1, "L"), (1, "R")):  # arms down to the ground, three long claws on each
        sh = Vector(t.at(side * 0.82, 0.05, 2.1))
        m.use(f"Arm{letter}", tuple(sh))
        elbow = sh + Vector((side * 0.45, 0.3, -1.6))
        wrist = elbow + Vector((-side * 0.05, 0.7, -1.55))
        beam(m, "Body", tuple(sh), tuple(elbow), 0.42, None, 0.32)
        ball(m, "Accent", *elbow, 0.22, 6, 3)
        beam(m, "Body", tuple(elbow), tuple(wrist), 0.32, None, 0.26)
        m.block("Accent", *wrist, 0.36, 0.42, 0.3)
        for k in (-1, 0, 1):
            base = wrist + Vector((k * 0.13, 0.15, -0.05))
            thorn(m, "Claw", tuple(base), tuple(base + Vector((k * 0.18, 0.72, -0.5))), 0.13, (0, 0.1, 0.16))
    m.bone = "Spine"
    for n, side in ((1, -1), (2, 1)):  # whips of mycelium out of its shoulders
        start = Vector(t.at(side * 0.55, -0.3, 2.05))
        tendril(m, n, wander(tuple(start), tuple(start + Vector((side * 1.6, -1.4, 1.4))), rng, 7, (side * 0.3, 0, 0.45), 0.14), 0.2, 0.06, "Spine",
                "Mycel", beads="Glow", tip="Glow", tip_size=0.13)
    m.bone = "Spine"

    neck = Vector(t.at(0, 0.15, 2.3))
    m.use("Neck", tuple(neck))
    head = neck + Vector((0.05, 0.85, 0.12))
    beam(m, "Body", tuple(neck - Vector((0, 0.15, 0.1))), tuple(head), 0.62, 0.62, 0.5)
    m.stretch("Body", "Spine")
    m.use("Head", tuple(head - Vector((0, 0.25, 0.1))), "Neck")
    hf = Frame(m, tuple(head), turn(x=0.05, z=-0.08))
    hf.box("Body", 0, 0, 0, 1.0, 0.95, 0.8)
    mf = Frame(m, hf.at(0, 0.32, -0.3), hf.r)
    gill_maw(m, mf, 0.95, 1.15, 0.62, 0.3, 0.3, rng, gape=0.12, drop=0.48, upper="Body", lower="Accent", tooth=0.24, per_side=6, rows=2,
             gills=4, strands=2)
    for side, r, off in ((-1, 0.32, (0.1, -0.12)), (1, 0.25, (-0.16, 0.1))):
        spore_eye(m, hf.at(side * 0.28, 0.42, 0.1), hf.r @ Vector((side * 0.12, 1, -0.05)), r, rng, off=off, veins=4)
        hf.beam("Accent", (side * 0.6, 0.42, 0.44), (side * 0.06, 0.68, 0.2), 0.18, 0.16, 0.13)
    mo = Frame(m, hf.at(0, -0.05, 0.34), hf.r @ turn(x=0.2, y=0.12))
    pits, tip = morel_hood(m, mo, 0.76, 1.95, rng)
    rng.shuffle(pits)
    eyes = 0
    for centre, out, size in pits:  # an eye in a dozen of the pits, every one rolling its own way
        if eyes == 12 or centre.z < head.z + 0.55:
            continue
        look = out + Vector((rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), rng.uniform(-0.3, 0.4)))
        spore_eye(m, tuple(centre), tuple(look), size * 0.42, rng, pupil="Slit", off=(rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3)), veins=2)
        eyes += 1
    vent(m, 1, tuple(tip + Vector((0, 0, 0.08))), "Head", 0.26, 4, lips=None)
    m.head_centre = tuple(hf.at(0, 0.8, 0.25))
    return finish(m, 0.92)


def antagonist():
    """A giant ant the fungus got to first: rust-red armour, mandibles like shears that never stop clacking, two
    glowing orbs for eyes under a jutting brow, and out of its head and back the fungus has burst in tall pale stalks
    with glowing clubs on the end, whipping about as if looking for the next one. Shelf fungi step up its abdomen and
    spores pour out of a split in it."""
    rng = random.Random(1403)
    m = monster("dino_Antagonist", Body="#9c4024", Accent="#5c2414", Belly="#c87a40", Claw="#1c120c")
    m.joint("Spine", (0, 0, 2.1))
    m.loft_y("Body", (-0.75, 0, 2.0, 0.85, 0.8), (0.1, 0, 2.2, 1.05, 1.0))
    m.loft_y("Body", (0.1, 0, 2.2, 1.05, 1.0), (0.85, 0, 2.45, 1.0, 1.05))
    m.loft_y("Accent", (-0.55, 0, 2.48, 0.6, 0.2), (0.7, 0, 2.95, 0.66, 0.24))
    ball(m, "Accent", 0, -0.95, 2.05, 0.32, 6, 3)
    for y in (-0.4, 0.35):
        point(m, "Accent", (0, y, 2.5), (0, y - 0.35, 3.05), 0.28)

    m.use("Tail1", (0, -1.1, 2.15))
    gc, grx, gry, grz = Vector((0, -2.35, 2.55)), 1.18, 1.38, 1.02
    m.loft_y("Body", (-0.95, 0, 2.15, 0.5, 0.5), (-1.15, 0, 2.3, 0.8, 0.8))
    egg(m, "Body", gc, grx, gry, grz, 12, 7)
    for y in (-1.75, -2.45, -3.1):  # bands round it
        k = math.sqrt(max(0.0, 1 - ((y - gc.y) / gry) ** 2)) * 1.04
        egg(m, "Accent", (0, y, gc.z), grx * k, 0.09, grz * k, 12, 3)
    m.use("Tail2", (0, -3.55, 2.45), "Tail1")
    point(m, "Claw", (0, -3.6, 2.42), (0, -4.3, 2.1), 0.36)
    m.bone = "Tail1"
    for side, y, z, r_ in ((-1, -2.25, 2.8, 0.46), (-1, -2.9, 2.25, 0.34), (1, -2.05, 2.3, 0.4), (1, -2.8, 2.85, 0.32)):
        k = math.sqrt(max(0.0, 1 - ((y - gc.y) / gry) ** 2 - ((z - gc.z) / grz) ** 2))
        bracket(m, side * grx * k * 0.98, y, z, r_)
    vent(m, 1, (0.25, -2.3, gc.z + grz - 0.04), "Tail1", 0.38, 4, lips="Accent")
    sprout(m, (-0.5, -2.75, gc.z + grz * 0.82), (-0.3, -0.2, 1), 0.7, 0.09, 0.42, 0.3, rng, n_specks=3)
    m.bone = "Spine"

    legs = (("Arm", 0.55, 1.9, (1.35, 1.25, 2.6), (1.6, 2.35, 0.05)),
            ("Front", 0.1, 1.85, (1.7, 0.35, 2.55), (2.4, 0.6, 0.05)),
            ("Back", -0.45, 1.85, (1.6, -1.25, 2.5), (2.2, -2.35, 0.05)))
    for prefix, hy, hz, knee, foot in legs:  # six legs; the front pair on the Arm bones, so they rake when it pounces
        for side, letter in ((-1, "L"), (1, "R")):
            hip = Vector((side * 0.42, hy, hz))
            m.use(f"{prefix}{letter}", tuple(hip))
            k = Vector((side * knee[0], knee[1], knee[2]))
            f_ = Vector((side * foot[0], foot[1], foot[2]))
            ankle = k.lerp(f_, 0.7) + Vector((side * 0.15, 0, 0.15))
            jointed_leg(m, [hip, k, ankle, f_], 0.3, role="Accent", ring="Body", tip="Claw")
            thorn(m, "Accent", tuple(k), tuple(k + Vector((side * 0.15, -0.2, 0.45))), 0.14)
    m.bone = "Spine"
    tendril(m, 4, wander((0.25, 0.35, 2.85), (1.1, -1.0, 5.6), rng, 7, (0.4, 0, 0.3), 0.1), 0.24, 0.16, "Spine", "Stalk", beads=None)
    tube(m, "Glow", (1.1, -1.0, 5.55), (1.25, -1.2, 6.25), 0.22, 0.12, 6)

    m.use("Neck", (0, 0.85, 2.45))
    beam(m, "Accent", (0, 0.7, 2.4), (0, 1.3, 2.62), 0.52)
    m.use("Head", (0, 1.35, 2.62), "Neck")
    hf = Frame(m, (0, 1.95, 2.75), turn(x=-0.14, y=0.06))
    zloft(hf, "Body", (-0.62, 0, 0.02, 1.05, 1.0), (0.1, 0, 0, 1.75, 1.35))
    zloft(hf, "Body", (0.1, 0, 0, 1.75, 1.35), (0.62, 0, -0.1, 1.5, 1.05))
    hf.box("Accent", 0, -0.05, 0.64, 0.12, 0.9, 0.08)
    mf = Frame(m, hf.at(0, 0.5, -0.42), hf.r)
    gill_maw(m, mf, 0.95, 0.5, 0.6, 0.26, 0.24, rng, gape=0.1, drop=0.32, upper="Accent", lower="Accent", tooth=0.17, per_side=4,
             tongue=False, gills=3, strands=1, rows=2,
             mandibles=dict(x0=0.52, y0=0.1, z0=0.02, length=1.65, width=0.36, teeth=6))
    for side in (-1, 1):
        spore_glare(m, hf.at(side * 0.7, 0.5, 0.18), hf.r @ Vector((side * 0.45, 1, 0.05)), 0.5, -side, 0.6, sprouts=1, rng=rng)
    for n, side in ((1, -1), (2, 1)):  # elbowed feelers, twitching
        pts = [hf.at(side * x, y, z) for x, y, z in ((0.28, 0.5, 0.5), (0.42, 0.68, 1.15), (0.58, 0.8, 1.7), (1.0, 1.4, 1.95), (1.4, 2.0, 1.85),
                                                     (1.65, 2.45, 1.6), (1.8, 2.75, 1.3))]
        tendril(m, n, pts, 0.13, 0.07, "Head", "Accent", beads=None, tip="Glow", tip_size=0.12)
    m.bone = "Head"
    start = Vector(hf.at(0.18, -0.38, 0.52))
    tendril(m, 3, wander(tuple(start), tuple(start + Vector((0.5, -1.4, 3.3))), rng, 7, (0.35, 0, 0.2), 0.1), 0.26, 0.16, "Head", "Stalk", beads=None)
    tube(m, "Glow", tuple(start + Vector((0.5, -1.4, 3.25))), tuple(start + Vector((0.6, -1.6, 4.0))), 0.24, 0.12, 6)
    m.bone = "Head"
    sprout(m, hf.at(-0.45, -0.3, 0.58), hf.r @ Vector((-0.5, -0.2, 1)), 0.5, 0.08, 0.34, 0.24, rng, n_specks=2)
    m.head_centre = tuple(hf.at(0, 0.85, 0.05))
    return finish(m, 1.0)


# ---------------------------------------------------------------------- the fierce ones


def sporantula():
    """A spider whose back is a mushroom cap: a broad rust-red cap freckled with glowing specks, glowing gills under
    it, on eight long jointed stalks of legs. Eight infected eyes crowd its face under the brim, two big and six small,
    its fangs never stop chattering, a drop of glowing venom on each, and its abdomen is a fat puffball, torn open in
    two places and pouring spores, glowing threads of mycelium trailing from its spinnerets."""
    rng = random.Random(1404)
    m = monster("dino_Sporantula", Body=CAP, Accent=CAP_DARK, Belly="#e2d5b8", Claw="#24160f", Wart=WART, Face="#3a1d14")
    m.joint("Spine", (0, 0, 2.35))
    m.loft_y("Belly", (-0.75, 0, 2.15, 1.35, 0.85), (0.85, 0, 2.3, 1.2, 0.9))
    carapace = cap(m, "Body", (0, 0.05, 2.8), 2.1, 1.25, "dome", turn(x=0.1), 14, crown="Accent", under="GillGlow")  # brim up at the front
    specks(m, "Speck", carapace, 2.1, 1.25, "dome", 14, 0.32, rng)

    # Eight legs, out from under the brim, up over it and down: 1 and 3 on Front, 2 and 4 on Back, so the
    # diagonal pairs step together like a spider's.
    hips = (0.75, 0.3, -0.15, -0.55)
    feet = (2.7, 1.0, -0.8, -2.45)
    for side, letter in ((-1, "L"), (1, "R")):
        for k, (hy, fy) in enumerate(zip(hips, feet)):
            bone = f"{'Front' if k % 2 == 0 else 'Back'}{letter}"
            if bone not in m.joints:
                m.use(bone, (side * 0.55, 0.4 if k % 2 == 0 else -0.2, 2.3))
            m.bone = bone
            spread = 1.0 - 0.1 * abs(k - 1.5)
            hip = Vector((side * 0.5, hy, 2.3))
            under = Vector((side * 2.3 * spread, hy + (fy - hy) * 0.3, 2.4))
            knee = Vector((side * 2.95 * spread, hy + (fy - hy) * 0.55, 3.75 - 0.1 * k))
            ankle = Vector((side * 3.5 * spread, hy + (fy - hy) * 0.9, 1.3))
            foot = Vector((side * 3.62 * spread, fy, 0.03))
            jointed_leg(m, [hip, under, knee, ankle, foot], 0.32, role="Belly", ring="StalkShade", tip="Claw", taper=0.45)
            for p in (knee, ankle):  # bristles at the joints
                thorn(m, "Claw", tuple(p), tuple(p + Vector((side * 0.2, rng.uniform(-0.2, 0.2), 0.35))), 0.09)
    m.bone = "Spine"

    m.use("Tail1", (0, -0.8, 2.45))
    ac, arx, ary, arz = Vector((0, -2.35, 2.8)), 1.22, 1.5, 1.08
    egg(m, "Belly", ac, arx, ary, arz, 12, 7)

    def on_top(x, y):
        return ac.z + arz * math.sqrt(max(0.0, 1 - (x / arx) ** 2 - ((y - ac.y) / ary) ** 2))

    for k in range(4):  # chevrons down its back
        y = ac.y + 0.75 - k * 0.5
        for side in (-1, 1):
            a_, b_ = (0, y), (side * 0.62, y - 0.32)
            beam(m, "Accent", (*a_, on_top(*a_) + 0.02), (*b_, on_top(*b_) + 0.02), 0.18, 0.08, 0.12)
    for _ in range(14):
        a, e = rng.uniform(0, math.tau), rng.uniform(0.1, 1.2)
        p = ac + Vector((arx * math.cos(e) * math.cos(a), ary * math.cos(e) * math.sin(a), arz * math.sin(e)))
        ball(m, "Wart", *p, rng.uniform(0.09, 0.16), 6, 3)
    for n, x, y in ((1, -0.42, -1.85), (2, 0.48, -2.6)):
        vent(m, n, (x, y, on_top(x, y) - 0.02), "Tail1", 0.3, 4)
    for side in (-1, 1):  # spinnerets, and glowing threads trailing from them
        tube(m, "Accent", (side * 0.16, -3.8, 2.65), (side * 0.2, -4.15, 2.5), 0.14, 0.08, 6)
    tendril(m, 1, wander((-0.18, -4.1, 2.5), (-1.0, -6.2, 0.6), rng, 7, (-0.3, 0, 0.4), 0.12), 0.09, 0.05, "Tail1", "Vein", beads=None)
    tendril(m, 2, wander((0.18, -4.1, 2.5), (1.2, -5.8, 0.35), rng, 7, (0.3, 0, 0.5), 0.12), 0.09, 0.05, "Tail1", "Vein", beads=None)
    m.bone = "Spine"

    m.use("Head", (0, 0.9, 2.2))
    hf = Frame(m, (0, 1.45, 2.18), turn(x=0.08))  # tipped up at you a little
    hf.box("Face", 0, 0, 0, 1.25, 0.72, 0.92)
    mf = Frame(m, hf.at(0, 0.28, -0.3), hf.r)
    gill_maw(m, mf, 0.72, 0.32, 0.46, 0.16, 0.18, rng, gape=0.08, drop=0.36, upper="Face", lower="Face", tooth=0.14, per_side=3,
             tongue=False, gills=3, strands=1, across=2)
    for side in (-1, 1):  # eight eyes, glossy black beads glowing in the middle, the big pair glaring under heavy brows
        bead_eye(m, hf.at(side * 0.3, 0.3, 0.1), hf.r @ Vector((side * 0.12, 1, 0.05)), 0.29, pupil="Pupil", off=(-side * 0.08, -0.05))
        hf.beam("Accent", (side * 0.66, 0.36, 0.5), (side * 0.06, 0.62, 0.26), 0.22, 0.2, 0.16)
        for x, z, r in ((0.6, 0.3, 0.15), (0.2, 0.47, 0.12), (0.5, 0.56, 0.11)):
            bead_eye(m, hf.at(side * x, 0.3, z), hf.r @ Vector((side * x * 0.8, 1, 0.2)), r, off=(rng.uniform(-0.15, 0.15), rng.uniform(-0.1, 0.1)))
    for n, side in ((1, -1), (2, 1)):  # the fangs, chattering for ever on Snap bones
        base = hf.at(side * 0.28, 0.42, -0.3)
        m.use(f"Snap{n}", base, "Head")
        knuckle = hf.at(side * 0.32, 0.74, -0.6)
        beam(m, "Accent", base, knuckle, 0.3, 0.34, 0.22)
        for k in range(3):  # bristles on the base
            p = Vector(hf.at(side * 0.42, 0.55 + 0.08 * k, -0.4 - 0.08 * k))
            thorn(m, "Claw", tuple(p), tuple(p + hf.r @ Vector((side * 0.2, 0.15, 0.05))), 0.06)
        tip = hf.at(side * 0.08, 0.9, -1.3)
        thorn(m, "Claw", knuckle, tip, 0.22, hf.r @ Vector((side * 0.1, 0.22, 0)))
        ball(m, "Glow", *hf.at(side * 0.07, 0.9, -1.38), 0.08, 6, 3)
    m.bone = "Head"
    for side, letter in ((-1, "L"), (1, "R")):  # feelers either side of the fangs, that grab when it pounces
        root = Vector(hf.at(side * 0.58, 0.2, -0.32))
        m.use(f"Arm{letter}", tuple(root))
        jointed_leg(m, [root, root + Vector((side * 0.3, 0.6, 0.35)), root + Vector((side * 0.22, 1.15, -0.25))], 0.2, role="Belly",
                    ring="StalkShade", tip="Claw", taper=0.6)
    m.bone = "Head"
    m.head_centre = tuple(hf.at(0, 0.7, 0.1))
    return finish(m, 1.05)


def mantis_wing(m, side, root, rng):
    """One of the Gillotine's wings, stood up behind it: ribs fanning from the root up and back, a dusky membrane
    between them, lilac light along the ribs and a glowing eye on the outer half, which is on its own WingTip bone."""
    letter = "L" if side < 0 else "R"
    root = Vector(root)
    m.use(f"Wing{letter}", tuple(root))
    u = Vector((side * 0.32, -0.5, 0.8)).normalized()  # up the wing
    v = Vector((side * 0.62, -0.72, -0.25)).normalized()  # across it, out and back
    ribs = []
    for k in range(5):
        a = 0.08 + k * 0.3
        d = u * math.cos(a) + v * math.sin(a)
        ribs.append((d, 3.3 - 0.32 * k))
    normal = u.cross(v).normalized()
    split = 0.5
    for bone, t0, t1 in ((f"Wing{letter}", 0.0, split), (f"WingTip{letter}", split, 1.0)):
        if bone.startswith("WingTip"):
            m.use(bone, tuple(root + ribs[2][0] * ribs[2][1] * split), f"Wing{letter}")
        for k, (d, length) in enumerate(ribs):
            a, b = root + d * length * t0, root + d * length * t1
            if t0 == 0:  # dark and stiff near the root, then only lilac light
                beam(m, "Accent", tuple(a), tuple(root + d * length * 0.22), 0.16, None, 0.1)
            beam(m, "Lilac", tuple(a), tuple(b), 0.1 * (1 - 0.4 * t0), None, 0.1 * (1 - 0.4 * t1))
            if k < len(ribs) - 1:
                d2, length2 = ribs[k + 1]
                mid = (d + d2).normalized()
                across_ = (d2 - d).normalized()
                lm = (length + length2) / 2
                lift = normal * (0.014 * k - 0.03)  # each panel a hair off the last, so where they overlap they don't flicker
                plate(m, "Membrane", tuple(root + mid * lm * t0 + lift), tuple(root + mid * lm * t1 * 0.98 + lift), tuple(across_),
                      max(0.05, lm * t0 * 0.3 * 1.2), lm * t1 * 0.3 * 1.15, 0.04)
    # The eyespot, on the outer half: a glowing ring round a black eye, a bar across it.
    d = (ribs[1][0] + ribs[2][0]).normalized()
    c = root + d * 2.35
    normal = normal * side
    f = Frame(m, tuple(c + normal * 0.06), aim(normal))
    slab(f, "EyeGlow", 0, 0, 0.0, 0.42, 0.05, 12)
    slab(f, "Socket", 0, 0, 0.03, 0.27, 0.04, 10)
    f.box("Slit", 0, 0.06, 0, 0.36, 0.02, 0.09)
    f2 = Frame(m, tuple(c - normal * 0.06), aim(-normal))
    slab(f2, "EyeGlow", 0, 0, 0.0, 0.42, 0.05, 12)
    slab(f2, "Socket", 0, 0, 0.03, 0.27, 0.04, 10)
    f2.box("Slit", 0, 0.06, 0, 0.36, 0.02, 0.09)
    m.bone = "Spine"


def gillotine():
    """A towering mantis, aubergine and bone, under a chocolate cap whose gills glow down over its eyes. Its forelegs
    are two serrated blades held up and ready to come down, side jaws open round a mouth of teeth, its wings stand up
    behind it in a threat display, a glowing eye on each and lilac light in their veins, feelers twitch and spores
    pour out of the vents along its abdomen."""
    rng = random.Random(1405)
    m = monster("dino_Gillotine", Body="#5d3d66", Accent="#35223c", Belly="#a06fa4", Claw="#ece0c4", Cap=CAP_B, CapDark=CAP_B_DARK,
                Membrane="#5a4a6e", Lilac=BELL)
    m.joint("Spine", (0, -0.3, 3.1))
    m.loft_y("Body", (-0.85, 0, 3.15, 0.95, 0.95), (0.3, 0, 3.35, 0.8, 0.85))
    for side, letter in ((-1, "L"), (1, "R")):  # four walking legs, long and thin
        hip = Vector((side * 0.35, 0.0, 3.0))
        m.use(f"Front{letter}", tuple(hip))
        jointed_leg(m, [hip, Vector((side * 1.75, 0.65, 3.95)), Vector((side * 2.45, 1.05, 1.6)), Vector((side * 2.55, 1.15, 0.03))], 0.26,
                    role="Body", ring="Accent", tip="Claw")
        hip = Vector((side * 0.35, -0.6, 3.0))
        m.use(f"Back{letter}", tuple(hip))
        jointed_leg(m, [hip, Vector((side * 1.85, -1.6, 3.85)), Vector((side * 2.55, -2.6, 1.5)), Vector((side * 2.65, -2.85, 0.03))], 0.26,
                    role="Body", ring="Accent", tip="Claw")
    m.bone = "Spine"

    # The abdomen, long and curling up at its end, banded, two vents along its top.
    m.use("Tail1", (0, -0.75, 3.2))
    pts = [(-0.75, 3.2, 1.0), (-1.9, 3.12, 1.4), (-3.0, 3.18, 1.32), (-3.9, 3.45, 1.08), (-4.6, 3.95, 0.8), (-5.0, 4.6, 0.46)]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        if i == 2:
            m.use("Tail2", (0, a[0], a[1]), "Tail1")
        if i == 4:
            m.use("Tail3", (0, a[0], a[1]), "Tail2")
        m.loft_y("Body", (a[0], 0, a[1], a[2], a[2] * 0.92), (b[0], 0, b[1], b[2], b[2] * 0.92))
        if i in (2, 4):
            m.stretch("Body", "Tail1" if i == 2 else "Tail2")
        m.loft_y("Accent", (a[0] - 0.07, 0, a[1], a[2] + 0.06, a[2] * 0.92 + 0.06), (a[0] + 0.07, 0, a[1], a[2] + 0.06, a[2] * 0.92 + 0.06))
        m.loft_y("Belly", (b[0] + 0.1, 0, b[1] - b[2] * 0.42, b[2] * 0.7, 0.12), (a[0] - 0.1, 0, a[1] - a[2] * 0.42, a[2] * 0.7, 0.12))
    m.bone = "Tail1"
    vent(m, 1, (0, -1.85, 3.12 + 0.68), "Tail1", 0.32, 4)
    m.bone = "Tail2"
    vent(m, 2, (0, -3.2, 3.2 + 0.62), "Tail2", 0.28, 4)
    m.bone = "Tail3"
    tendril(m, 3, wander((0, -5.0, 4.75), (0.4, -5.4, 6.6), rng, 6, (0.3, -0.3, 0), 0.1), 0.2, 0.06, "Tail3", "Mycel", beads="Glow", tip="Glow",
            tip_size=0.14)
    m.bone = "Spine"
    for side in (-1, 1):
        mantis_wing(m, side, (side * 0.3, -0.45, 3.65), rng)

    # The long neck of a thorax, up to the head.
    m.loft_z("Body", (3.0, 0, 0.0, 0.85, 0.85), (3.6, 0, 0.25, 0.75, 0.75))
    beam(m, "Body", (0, 0.2, 3.5), (0, 1.25, 6.05), 0.62, 0.66, 0.5)
    beam(m, "Belly", (0, 0.42, 3.55), (0, 1.48, 5.9), 0.36, 0.2, 0.28)
    for side, letter in ((-1, "L"), (1, "R")):  # the blades, held up either side of its face
        sh = Vector((side * 0.45, 1.12, 5.72))
        m.use(f"Arm{letter}", tuple(sh))
        coxa = sh + Vector((side * 0.55, 0.65, -0.95))
        femur = coxa + Vector((side * 0.3, 0.3, 1.95))
        blade_end = femur + Vector((-side * 0.2, 1.45, -1.3))
        beam(m, "Body", tuple(sh), tuple(coxa), 0.44, None, 0.36)
        ball(m, "Accent", *coxa, 0.24, 6, 3)
        beam(m, "Body", tuple(coxa), tuple(femur), 0.42, 0.62, 0.34)
        for k in range(5):  # spines along the inside of the femur
            p = coxa.lerp(femur, 0.2 + 0.16 * k) + Vector((-side * 0.12, 0.22, 0))
            point(m, "Claw", tuple(p), tuple(p + Vector((-side * 0.1, 0.32 + 0.06 * (k % 2), 0.05))), 0.12)
        ball(m, "Accent", *femur, 0.24, 6, 3)
        beam(m, "Claw", tuple(femur), tuple(blade_end), 0.18, 0.55, 0.08)
        down = (blade_end - femur).normalized().cross(Vector((side, 0, 0))).normalized()
        if down.z > 0:
            down = -down
        for k in range(7):  # the serrated edge underneath
            p = femur.lerp(blade_end, 0.12 + 0.12 * k) + down * 0.2
            point(m, "Claw", tuple(p), tuple(p + down * 0.22 - (blade_end - femur).normalized() * 0.1), 0.1)
        thorn(m, "Claw", tuple(blade_end), tuple(blade_end + Vector((0, 0.1, -0.6))), 0.16, (0, 0.18, 0))
    m.bone = "Spine"

    m.use("Neck", (0, 1.3, 6.2))
    beam(m, "Body", (0, 1.18, 6.0), (0, 1.6, 6.55), 0.44)
    m.use("Head", (0, 1.6, 6.55), "Neck")
    hf = Frame(m, (0, 1.95, 6.9), turn(x=-0.16, y=0.08))
    zloft(hf, "Body", (-0.7, 0, 0.0, 0.7, 0.66), (0.3, 0, 0.0, 1.95, 0.86))  # a mantis's triangle of a head
    zloft(hf, "Body", (0.3, 0, 0.0, 1.95, 0.86), (0.58, 0, -0.06, 1.7, 0.66))
    mf = Frame(m, hf.at(0, 0.24, -0.58), hf.r)
    gill_maw(m, mf, 0.66, 0.55, 0.44, 0.22, 0.22, rng, gape=0.08, drop=0.38, upper="Body", lower="Accent", tooth=0.17, per_side=4, rows=2,
             tongue=False, gills=3, strands=1, across=2, mandibles=dict(x0=0.36, y0=0.06, z0=0.0, length=1.05, width=0.22, teeth=4, role="Accent"))
    for side in (-1, 1):  # great glowing eyes on the corners of its head
        orb_eye(m, hf.at(side * 0.86, 0.12, 0.3), hf.r @ Vector((side * 0.55, 1, 0.08)), 0.4, -side)
    hood = cap(m, "Cap", hf.at(0, -0.35, 0.78), 0.95, 0.62, "dome", hf.r @ turn(x=-0.18, y=0.1), 12, crown="CapDark", under="GillGlow")
    specks(m, "Speck", hood, 0.95, 0.62, "dome", 6, 0.18, rng)
    for n, side in ((1, -1), (2, 1)):  # long feelers, twitching
        start = Vector(hf.at(side * 0.22, 0.42, 0.42))
        tendril(m, n, wander(tuple(start), tuple(start + hf.r @ Vector((side * 1.4, 1.2, 2.1))), rng, 7, (side * 0.3, 0.4, 0.2), 0.08), 0.09, 0.05,
                "Head", "Accent", beads=None, tip="Glow", tip_size=0.1)
    m.bone = "Head"
    m.head_centre = tuple(hf.at(0, 0.8, 0.05))
    return finish(m, 1.08)


def shroomageddon():
    """The boss: the hollow's own god, a colossal titan hunched on its knuckles that is more fungus than beast now.
    A forest of glowing mushrooms on its back round a geyser of spores, shelf fungi stepping up its arms, the mycelium
    heart glowing in its open chest behind ribs of bone and glowing threads running out of it all over its hide, whips
    of mycelium thrashing from its back, a club of puffballs on its tail, and a great cap pulled down over its face like
    a hood with a crown of glowing morels round it. Five eyes, and a mouth that opens four ways."""
    rng = random.Random(1406)
    m = monster("dino_Shroomageddon", Body="#4a2e45", Accent="#28182a", Belly="#7d4466", Claw="#e8dbbd", Heart=HEART, HeartGlow="#c8ff4c",
                CapB=CAP_B, CapBDark=CAP_B_DARK, Ridge=RIDGE, Pit=PIT)
    m.joint("Spine", (0, 0, 6.0))
    for side, letter in ((-1, "L"), (1, "R")):  # arms like tree trunks, walking on their knuckles
        sh = Vector((side * 2.2, 2.0, 7.6))
        m.use(f"Front{letter}", tuple(sh))
        elbow = Vector((side * 3.15, 2.45, 4.4))
        fist = Vector((side * 3.0, 3.1, 1.25))
        beam(m, "Body", tuple(sh + Vector((0, 0, 0.4))), tuple(elbow), 2.0, None, 1.5)
        ball(m, "Body", *elbow, 0.85, 8, 4)
        beam(m, "Body", tuple(elbow), tuple(fist), 1.5, None, 1.25)
        m.loft_z("Accent", (0.0, fist.x, fist.y + 0.15, 1.55, 1.45), (1.6, fist.x, fist.y, 1.4, 1.3))
        for k in range(4):  # knuckle claws, curled forward into the ground
            x = fist.x + (k - 1.5) * 0.36
            thorn(m, "Claw", (x, fist.y + 0.6, 0.55), (x + (k - 1.5) * 0.08, fist.y + 1.45, 0.05), 0.34, (0, 0.1, 0.22))
        for k in range(3):  # bone spikes out of its elbow
            p = elbow + Vector((side * 0.55, -0.3 + 0.3 * k, 0.2 - 0.15 * k))
            thorn(m, "Claw", tuple(p), tuple(p + Vector((side * 0.75, -0.35, 0.55 - 0.2 * k))), 0.36)
        for k, (t, r_) in enumerate(((0.3, 0.55), (0.55, 0.45), (0.72, 0.36))):  # shelf fungi stepping up the forearm
            p = fist.lerp(elbow, t) + Vector((side * 0.62, -0.1, 0))
            bracket(m, *p, r_)
        for k in range(3):  # glowing threads down the arm
            a = elbow + Vector((side * 0.4 * (k - 1), 0.62, 0.3 * k))
            b = fist + Vector((side * 0.3 * (k - 1), 0.66, 0.6 + 0.2 * k))
            limb(m, "Vein", [tuple(a), tuple(a.lerp(b, 0.5) + Vector((side * 0.15 * (k - 1), 0.08, 0))), tuple(b)], 0.11, 0.07, joints=False)
    for bone, x in (("BackL", -1.85), ("BackR", 1.85)):
        clawed_leg(m, bone, x, -2.6, 5.3, 1.75, rng, reach=0.7)
        m.bone = bone
        bracket(m, x * 1.32, -2.6, 3.6, 0.42)
    m.bone = "Spine"

    body = ((-3.4, 0, 5.7, 2.8, 2.8), (2.6, 0, 7.4, 4.3, 4.4))
    m.loft_y("Body", *body)
    m.loft_y("Body", (-0.6, 0, 8.4, 3.0, 1.4), (2.2, 0, 9.3, 3.5, 1.6))  # the hunch of its shoulders
    m.loft_y("Belly", (-2.9, 0, 4.45, 2.0, 0.2), (2.2, 0, 5.3, 3.0, 0.25))

    # Its chest is open on the mycelium heart: a black hollow, the heart glowing in it and ribs of bone across it.
    cf = Frame(m, (0, 2.62, 7.0))
    slab(cf, "Socket", 0, 0, 0.0, 1.4, 0.1, 12, 0.85)
    egg(m, "Heart", (0, 2.62, 6.95), 0.85, 0.55, 1.05, 10, 6)
    for k in range(6):  # glowing seams down the heart
        a = math.pi * (0.1 + 0.8 * k / 5)
        pts = [(math.cos(a) * 0.88 * math.cos(lat), 2.62 + 0.57 * math.sin(a) * math.cos(lat), 6.95 + 1.07 * math.sin(lat)) for lat in (-1.1, -0.5, 0.1, 0.7, 1.2)]
        limb(m, "HeartGlow", pts, 0.1, 0.08, joints=False)
    for k in range(4):
        z = 6.1 + k * 0.55
        pts = [(-1.15, 2.62, z + 0.05), (-0.6, 3.12, z + 0.12), (0.0, 3.24, z + 0.15), (0.6, 3.12, z + 0.12), (1.15, 2.62, z + 0.05)]
        limb(m, "Claw", pts, 0.24, 0.2)
    for k in range(9):  # glowing threads running out of it all over its hide
        a = k * math.tau / 9 + 0.2
        p = Vector((math.cos(a) * 1.35, 2.6, 7.0 + math.sin(a) * 1.25))
        pts = [tuple(p)]
        on_side = 1.02 / max(abs(math.cos(a)), abs(math.sin(a)))  # out to the body's square sides
        for j in range(3):
            y = 2.3 - 1.1 * (j + 1)
            _, cx, cz, w0, h0 = ring_at(*body, max(y, -3.3))
            q = Vector((math.cos(a) * on_side * w0 / 2, y, cz + math.sin(a) * on_side * h0 / 2))
            pts.append(tuple(q))
        limb(m, "Vein", pts, 0.14, 0.08, joints=False)

    # The forest on its back, leaning out round the geyser in the middle.
    def back_top(x, y):
        _, cx, cz, w0, h0 = ring_at(*body, y)
        top = cz + h0 / 2 * math.sqrt(max(0.05, 1 - (2 * x / w0) ** 2))
        if -0.6 <= y <= 2.2 and abs(x) < 1.5:
            _, _, hz, _, hh = ring_at((-0.6, 0, 8.4, 3.0, 1.4), (2.2, 0, 9.3, 3.5, 1.6), y)
            top = max(top, hz + hh / 2)
        return top

    shrooms = ((-1.45, -0.4, (-0.55, 0.15, 1), 2.6, 0.36, 1.6, 1.15, "Cap", "CapDark", 7),
               (1.55, 0.6, (0.5, 0.2, 1), 3.0, 0.4, 1.75, 1.25, "Cap", "CapDark", 8),
               (-1.25, -2.6, (-0.45, -0.4, 1), 2.0, 0.3, 1.25, 0.9, "CapB", "CapBDark", 5),
               (1.25, -2.5, (0.5, -0.35, 1), 1.7, 0.26, 1.05, 0.75, "Cap", "CapDark", 4),
               (0.45, 1.8, (0.25, 0.45, 1), 1.1, 0.2, 0.75, 0.55, "CapB", "CapBDark", 3),
               (-0.6, 1.5, (-0.4, 0.3, 1), 0.8, 0.15, 0.55, 0.42, "Cap", "CapDark", 2))
    for x, y, d, h, r_, cr, ch, role, crown, n in shrooms:
        sprout(m, (x, y, back_top(x, y) - 0.25), d, h, r_, cr, ch, rng, cap_role=role, crown=crown, n_specks=n, sides=12 if cr > 1 else 8)
    for _ in range(9):  # and little ones everywhere
        x, y = rng.uniform(-1.6, 1.6), rng.uniform(-3.0, 2.0)
        if abs(x) < 0.7 and -2.2 < y < -0.6:
            continue
        sprout(m, (x, y, back_top(x, y) - 0.08), (rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), 1), rng.uniform(0.3, 0.6), 0.07, rng.uniform(0.2, 0.32),
               0.18, rng, crown=None, sides=6)
    gx, gy = 0.0, -1.45
    gz = back_top(gx, gy)
    prism(m, "Accent", gx, gy, gz - 0.3, gz + 0.35, 1.05, 0.85, 10, math.pi / 10)  # the geyser's crater
    vent(m, 1, (gx, gy, gz + 0.4), "Spine", 0.8, 6)
    vent(m, 2, (-1.75, 1.6, back_top(-1.75, 1.6) - 0.1), "Spine", 0.36, 4)

    # Tail: short and thick, a club of puffballs on its end.
    pts = [(0, -3.3, 5.9), (0.2, -4.6, 5.4), (-0.15, -5.7, 4.8), (0.1, -6.5, 4.5)]
    widths = (2.2, 1.6, 1.15, 0.9)
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        m.use(f"Tail{i + 1}", a, f"Tail{i}" if i else "Spine")
        beam(m, "Body", a, b, widths[i], None, widths[i + 1])
        if i:
            m.stretch("Body", f"Tail{i}")
        bracket(m, a[0] + widths[i] * 0.48, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2 - 0.1, 0.36 - 0.06 * i)
    club = Vector((0.1, -6.9, 4.5))
    for k, (dx, dy, dz, r_) in enumerate(((0, 0, 0, 0.85), (0.6, -0.3, 0.4, 0.55), (-0.55, -0.4, 0.35, 0.5), (0.1, -0.7, -0.35, 0.48), (-0.2, 0.2, 0.75, 0.42))):
        c = club + Vector((dx, dy, dz))
        ball(m, "Puffskin", *c, r_, 8, 4)
        ball(m, "Glow", *(c + Vector((0, 0, r_ * 0.8))), r_ * 0.3, 6, 3)
    m.bone = "Spine"

    for n, start, end, bow in ((1, (1.75, 1.3, 9.0), (4.6, 0.6, 11.6), (0.4, 0, 0.4)), (2, (-1.75, 1.0, 9.0), (-4.4, 0.2, 12.0), (-0.3, 0, 0.5)),
                               (3, (1.5, -2.6, 7.9), (3.9, -4.8, 9.8), (0.5, 0, 0.5)), (4, (-1.5, -2.7, 7.8), (-3.7, -5.0, 10.3), (-0.4, 0, 0.6))):
        tendril(m, n, wander(start, end, rng, 7, bow, 0.22), 0.5, 0.14, "Spine", "Mycel", beads="Glow", tip="Glow", tip_size=0.3)
        m.bone = f"Lash{n}c"
        sprout(m, end, Vector(end) - Vector(start), 0.3, 0.12, 0.45, 0.32, rng, crown=None, sides=8)
    m.bone = "Spine"

    m.use("Neck", (0, 2.4, 8.3))
    beam(m, "Body", (0, 1.9, 8.0), (0, 3.6, 8.85), 2.3, 2.1, 1.75)
    m.stretch("Body", "Spine")
    m.use("Head", (0, 3.75, 8.7), "Neck")
    hf = Frame(m, (0, 4.7, 8.95), turn(x=-0.12, y=-0.06))
    hf.box("Body", 0, 0, 0, 2.5, 2.1, 2.1)
    for side in (-1, 1):
        hf.box("Accent", side * 1.12, -0.25, -0.35, 0.42, 1.4, 1.25)
    mf = Frame(m, hf.at(0, 0.85, -0.55), hf.r)
    gill_maw(m, mf, 2.2, 1.55, 1.35, 0.6, 0.55, rng, gape=0.2, drop=0.46, upper="Body", lower="Accent", tooth=0.46, per_side=7, rows=2,
             tongue=False, gills=7, strands=3, lift=0.1,
             mandibles=dict(x0=1.12, y0=0.12, z0=-0.08, length=1.45, width=0.42, height=0.8, teeth=7, curl=0.75, role="Accent"))
    spore_glare(m, hf.at(-0.6, 1.06, 0.36), hf.r @ Vector((-0.1, 1, 0)), 0.95, 1, 0.6, sprouts=2, rng=rng, lid=False)
    spore_glare(m, hf.at(0.64, 1.06, 0.42), hf.r @ Vector((0.1, 1, 0)), 0.8, -1, 0.6, sprouts=2, rng=rng, lid=False)
    for x, y, z, r, look in ((0.0, 1.08, 0.7, 0.17, (0, 1, 0.15)), (-1.2, 0.8, 0.52, 0.17, (-1, 0.7, 0.1)), (1.2, 0.85, 0.55, 0.15, (1, 0.7, 0.05))):
        spore_eye(m, hf.at(x, y, z), hf.r @ Vector(look), r, rng, pupil="Slit", veins=2, off=(rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2)))
    hood = cap(m, "Cap", hf.at(0, -0.55, 1.55), 2.45, 1.75, "dome", hf.r @ turn(x=-0.16, y=0.07), 14, crown="CapDark", under="GillGlow", lip=0.3)
    specks(m, "Speck", hood, 2.45, 1.75, "dome", 11, 0.42, rng, (0.22, 0.75))
    for k in range(5):  # a crown of glowing morels round the top of the cap
        a = math.pi / 2 + (k - 2) * 0.62
        t = 0.62
        rr = 2.45 * share(((0, 1.0), (0.35, 0.94), (0.65, 0.76), (0.88, 0.48), (1, 0.16)), t)
        base = hood.at(math.cos(a) * rr * 0.92, math.sin(a) * rr * 0.92, 1.75 * t - 0.05)
        out = hood.r @ Vector((math.cos(a) * 0.35, math.sin(a) * 0.35, 1))
        mo = Frame(m, base, up_along(out))
        morel_hood(m, mo, 0.3, 1.05 - 0.15 * abs(k - 2), rng, cols=6, rows=3)
    m.head_centre = tuple(hf.at(0, 1.6, 0.1))
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
