"""Builds Clockwork Citadel's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_clockwork_citadel_monsters.py
    QUICK=1 Blender -b -P build_clockwork_citadel_monsters.py    (stills only, into QUICK_OUT, for trying faces)
    ONLY=wind_up_wally,sprocket QUICK=1 ...                       (just those)

Saves clockwork_citadel_monsters.blend and renders to design/world/monsters_clockwork_citadel/. The map's props
are in build_clockwork_citadel.py.

Map 12, a citadel that is one enormous machine, still running in the dark. The owner asked for monsters that suit
the biome, animated, and nice: the citadel's machines built in the shape of beasts, wound up and let loose, silly
at the common end and fierce at the rare end, then a boss. They share the lens eye: a riveted brass bezel round a
glass lens with a glowing iris, white glass and an electric-blue iris on the silly ones, dark glass and a
furnace-orange glare under slanted iron brows on the fierce ones. And every one has a wind-up key in its back that
never stops turning. The map's colours: bronze, brass, copper, soot iron, electric blue and furnace orange.

  Wind-Up Wally   a tin wind-up toy rex: red tin painted with yellow stripes, big flat feet, stubby arms, two
                  mismatched googly lenses, chattering tin teeth and a huge brass key in its back
  Sprocket        a clockwork pup of copper plate: big puppy lenses, flying goggles pushed up on its head, floppy
                  metal ears that flap as it trots, its tongue out, a gear tag on its collar and a coil-spring tail
  Kettle Belly    a grumpy walking boiler: a riveted iron drum on stubby legs, its furnace door glowing in its
                  belly, a gauge on its chest, a lid and a chimney for a hat, a whistle spout, gritted teeth and
                  heavy iron brows, its arms pipes ending in wrench claws
  Gearjaw         a steel raptor: a buzz saw spinning in a slot along its skull, dark lenses glaring orange under
                  slanted brows, a long jaw of steel fangs with a furnace in its throat, pistons on its thighs
  Drillhorn       an iron triceratops: a great brass gear for a frill, steel brow horns, a drill for a nose horn
                  that never stops boring, furnace grilles glowing in its flanks and exhaust stacks on its back
  Chrono Rex      the boss: a towering iron tyrant with a giant brass gear turning on its back like a sail,
                  smokestacks glowing on its shoulders, a furnace heart burning behind brass ribs, a crest of gear
                  teeth, glaring furnace eyes under heavy brows and a jaw of steel fangs with fire in its throat

All have a Jaw bone (they snap as they walk and roar once per idle in the game, DinoLifeController), always in front
of the Spine, since the game tells which way a monster faces from it. Sprocket's ears ride the Wing bones. Parts
that turn for ever sit on their own bone, which DinoLifeController's SPIN turns at a steady speed whatever the
monster is doing, and the preview turns the same (SPIN below): Key (the wind-up key, round the upright), Drill
(Drillhorn's nose, round its forward axis) and Cog (Gearjaw's saw, the boss's gear sail, round the sideways axis).
Their speeds are whole half turns a second, so the 1-second walk and the 8-second idle loop seamlessly in Blender
(keys, saws and gears look the same turned half way round).

Glowing parts are EyeGlow, Furnace, Dial and Volt (Neon in the game, shared/Roles.luau, all there already). Skin
roles Body, Accent, Belly and Claw take the colour mutations; brass trim, keys, rivets, steel, glass and paint keep
their colour. Built at the first map's size; the game scales them by Config/Biomes standardScale. 1 Blender unit =
1 stud, models face +Y, feet on Z = 0.

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
from build_clockwork_citadel import (BRASS, BRASS_DARK, BRASS_LIGHT, COPPER, COPPER_DARK, FURNACE, IRON, IRON_DARK,  # noqa: E402
                                     IRON_LIGHT, RIVET, SIDEWAYS, SOOT, STEAM, STEEL, UPRIGHT, VOLT, gear, tube)
from build_desert import beam, quad_legs  # noqa: E402
from build_eclipse_temple_monsters import at, face_box, grow, round_slab  # noqa: E402
from build_forest import Model, biped_legs, tail  # noqa: E402
from build_starfall_crater import ball, flat_ring  # noqa: E402
from build_volcano import idle_pose as volcano_idle, prism, top_of, walk_pose as volcano_walk  # noqa: E402
from face_kit import classic_mouth  # noqa: E402
from map_kit import limb, plate  # noqa: E402
from monster_stage import build_and_render, light_up, set_sky  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_clockwork_citadel"
BLEND = "clockwork_citadel_monsters"  # for check_map.py and export_fbx.py

GLOW_ROLES = {"EyeGlow", "Furnace", "Dial", "Volt"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket", "Glass", "Paint"})
GLOW = 1.8

FACE = {"Pupil": "#101218", "Socket": "#0d0f14", "EyeGlow": VOLT, "EyeWhite": "#f4f1e8", "Highlight": "#ffffff", "Mouth": "#1c1a22",
        "Teeth": "#e2e8ef", "Tongue": "#d8455a", "Trim": BRASS, "TrimDark": BRASS_DARK, "Rivet": RIVET, "Key": BRASS, "Glass": "#9fb3c8",
        "Steel": STEEL, "Furnace": FURNACE}
SKY, FLOOR = "#121825", "#8a6436"

# Parts that turn for ever on their own bone: radians a second and the axis (0 X: sideways, 1 Y: forwards, 2 Z: up),
# the same as SPIN in DinoLifeController (keep the two in step).
SPIN = {"Key": (math.pi, 2), "Drill": (4 * math.pi, 1), "Cog": (math.pi, 0)}


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


def spin_pose(a, f):
    for name, (speed, axis) in SPIN.items():
        rotation = [0.0, 0.0, 0.0]
        rotation[axis] = speed * f / 30
        kit.pose_bone(a, name, tuple(rotation), None, f)


def walk_pose(a, f):
    volcano_walk(a, f)
    spin_pose(a, f)


def idle_pose(a, f):
    volcano_idle(a, f)
    spin_pose(a, f)


def fcurves_of(action):
    """An action's curves, in the old (action.fcurves) and the layered (Blender 4.4+) actions alike."""
    curves = list(getattr(action, "fcurves", None) or [])
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []):
                curves.extend(bag.fcurves)
    return curves


def animate(armature):
    """The Volcano's walk and idle (jaw snap and roar), with the spinning bones turning steadily through both."""
    walk = kit.add_action(armature, "Walk", kit.WALK_FRAMES, walk_pose, 2)
    idle = kit.add_action(armature, "Idle", kit.IDLE_FRAMES, idle_pose, 2)
    for action in (walk, idle):  # a steady turn, not eased between keys
        for curve in fcurves_of(action):
            if any(f'"{name}"' in curve.data_path for name in SPIN):
                for point in curve.keyframe_points:
                    point.interpolation = "LINEAR"
    return walk, idle


# ---------------------------------------------------------------------- the lens eye, keys and teeth


def lens_eye(m, origin, normal, size, inner=1, white=True, look=(0.0, 0.0), lid=0.0, slant=0.0, brow=None, lid_role="Accent",
             brow_role="Accent"):
    """One clockwork eye on a face at origin (its middle, on the surface; normal "y", "+x" or "-x"), inner (+1/-1)
    the way to the nose along the face: a brass bezel with four rivets, a glass lens (white, or a dark socket on the
    fierce ones), a glowing iris with a pupil and a highlight, an iron lid over its top and a brow plate, both
    slanting down to the nose by slant (angry) or level (sleepy, grumpy)."""
    def p(u, v, n):
        return at(origin, normal, u, v, n)

    round_slab(m, "Trim", p(0, 0, 0.05), normal, size * 0.62, 0.1, 16)
    r, bolt = size * 0.57, max(0.05, size * 0.1)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        face_box(m, "TrimDark", origin, normal, math.cos(a) * r, math.sin(a) * r, 0.11, bolt, bolt, 0.05)
    round_slab(m, "EyeWhite" if white else "Socket", p(0, 0, 0.12), normal, size * 0.5, 0.06, 16)
    du, dv = look[0] * size * 0.18, look[1] * size * 0.18
    round_slab(m, "EyeGlow", p(du, dv, 0.165), normal, size * 0.3, 0.04, 12)
    round_slab(m, "Pupil", p(du, dv, 0.195), normal, size * 0.13, 0.03, 10)
    face_box(m, "Highlight", origin, normal, du - size * 0.1, dv + size * 0.12, 0.215, size * 0.09, size * 0.09, 0.02)
    w, top = size * 1.15, size * 0.52
    dz = slant * size * 0.3

    def tilted(role, bottom, thick_top, depth, n):
        o = at(origin, normal, -inner * w / 2, 0, n)
        i = at(origin, normal, inner * w / 2, 0, n)
        bo, bi = bottom + dz, bottom - dz
        to, ti = thick_top + dz * 0.5, thick_top - dz * 0.5
        if normal == "y":
            m.loft_x(role, (o[0], o[1], o[2] + (bo + to) / 2, depth, to - bo), (i[0], i[1], i[2] + (bi + ti) / 2, depth, ti - bi))
        else:
            m.loft_y(role, (o[1], o[0], o[2] + (bo + to) / 2, depth, to - bo), (i[1], i[0], i[2] + (bi + ti) / 2, depth, ti - bi))

    if lid > 0:
        tilted(lid_role, top - 2 * top * lid, top + size * 0.04, 0.2, 0.2)
    if brow is not None:
        tilted(brow_role, top + brow * size, top + brow * size + size * 0.3, size * 0.36, 0.22)


def wind_key(m, y, z, size, parent="Spine"):
    """The wind-up key in the back: a brass collar on the body, and on its own Key bone a stem and a bow of two
    round lobes with holes, which the game turns for ever round the upright (SPIN)."""
    m.bone = parent
    prism(m, "TrimDark", 0, y, z - 0.15, z + 0.12, size * 0.34, size * 0.34, 8)
    m.use("Key", (0, y, z), parent)
    prism(m, "Key", 0, y, z - 0.05, z + size * 0.95, size * 0.12, size * 0.12, 8)
    zt = z + size * 1.25
    m.block("Key", 0, y, zt, size * 0.55, size * 0.2, size * 0.32)
    for side in (-1, 1):
        round_slab(m, "Key", (side * size * 0.52, y, zt), "y", size * 0.42, size * 0.16, 12)
        round_slab(m, "Socket", (side * size * 0.56, y, zt), "y", size * 0.15, size * 0.2, 8)
    m.bone = parent


def fang_row(m, xs, y, edge, length, width, down):
    """A row of pointed steel teeth across the front of a jaw, from its edge at z = edge, pointing down or up."""
    for x in xs:
        if down:
            m.loft_z("Teeth", (edge - length, x, y, 0.03, 0.03), (edge, x, y, width, width))
        else:
            m.loft_z("Teeth", (edge, x, y, width, width), (edge + length, x, y, 0.03, 0.03))


def tin_teeth(m, xs, y, edge, h, w, down=True):
    """Square tin teeth across a jaw, hanging from its edge (or standing up from it)."""
    for x in xs:
        m.block("Teeth", x, y, edge - h / 2 if down else edge + h / 2, w, w * 0.6, h)


def rivets(m, points, size=0.08, role="Rivet"):
    for p in points:
        m.block(role, *p, size, size, size)


def side_rivets(m, ys, z, half_width, size=0.08):
    """Rivets in a row along both flanks of a body, at height z."""
    rivets(m, [(s * (half_width + 0.02), y, z) for y in ys for s in (-1, 1)], size)


# ---------------------------------------------------------------------- the common ones


def wind_up_wally():
    """A tin wind-up toy rex out for a walk: red tin painted with yellow stripes and riveted at its seams, big flat
    feet, stubby arms, a huge brass key turning in its back. Its two lenses don't match, one big and one small,
    looking two ways at once, and its square tin teeth chatter."""
    m = monster("dino_WindUpWally", Body="#c94b3c", Accent="#8e2f27", Belly="#f1e2b9", Claw="#3a3d47", Paint="#f2c24e")
    m.joint("Spine", (0, 0, 1.3))
    biped_legs(m, 0.5, -0.1, 1.25, 0.55, 0.75, 0.42, 1.15, 0.3)
    body = ((-0.9, 0, 1.78, 1.25, 1.2), (0.8, 0, 1.98, 1.45, 1.5))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-0.6, 0, 1.3, 0.95, 0.26), (0.78, 0, 1.42, 1.15, 0.36))
    for y in (-0.45, 0.3):  # painted stripes round the tin
        top = top_of(body, y)
        half = (1.25 + (1.45 - 1.25) * (y + 0.9) / 1.7) / 2
        m.block("Paint", 0, y, top + 0.01, half * 2 - 0.2, 0.16, 0.04)
        for s in (-1, 1):
            m.block("Paint", s * (half + 0.01), y, top - 0.55, 0.04, 0.16, 1.0)
    side_rivets(m, (-0.7, -0.2, 0.55), 1.95, 0.7)
    tail(m, (-0.85, 1.85, 0.75, 0.75), (-2.0, 1.3, 0.22, 0.22), 3)
    for side in (-1, 1):  # stubby arms
        m.use("ArmL" if side < 0 else "ArmR", (side * 0.62, 0.55, 2.05))
        beam(m, "Body", (side * 0.62, 0.55, 2.05), (side * 0.75, 0.95, 1.7), 0.26, None, 0.22)
        for off in (-0.07, 0.07):
            m.loft_y("Claw", (0.92, side * 0.75 + off, 1.68, 0.08, 0.08), (1.15, side * 0.76 + off, 1.6, 0.02, 0.02))
    m.bone = "Spine"
    wind_key(m, -0.35, top_of(body, -0.35), 0.8)

    m.use("Neck", (0, 0.7, 2.35))
    m.block("Body", 0, 0.85, 2.45, 0.85, 0.6, 0.6)
    w, d, h = 1.3, 1.3, 1.25
    yc, zc = 1.25, 2.95
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    m.block("Paint", 0, yc - 0.1, zc + h / 2 + 0.01, 0.24, d - 0.3, 0.04)  # a stripe over its head
    mouth_z, gap = zc - 0.42, 0.2

    def bottom_teeth(m, front, mouth_z, gap, lower_length):
        tin_teeth(m, (-0.3, -0.1, 0.1, 0.3), front + lower_length - 0.08, mouth_z - gap / 2, 0.16, 0.15, False)

    classic_mouth(m, front, mouth_z, w, 0.55, 1.1, 0.3, 0.28, gap, upper="Body", lower="Belly", tongue=True, skull_d=d,
                  on_jaw=bottom_teeth)
    tin_teeth(m, (-0.36, -0.12, 0.12, 0.36), front + 0.47, mouth_z + gap / 2, 0.18, 0.16, True)
    lens_eye(m, (-0.32, front, zc + 0.36), "y", 0.66, 1, white=True, look=(0.35, -0.25))
    lens_eye(m, (0.38, front, zc + 0.3), "y", 0.44, -1, white=True, look=(-0.5, 0.4), brow=0.06, slant=-0.6)
    rivets(m, [(s * (w / 2 + 0.02), yc + dy, zc + dz) for s in (-1, 1) for dy, dz in ((-0.4, 0.4), (0.2, 0.4), (-0.4, -0.3))])
    m.head_centre = (0, front + 0.25, zc + 0.15)
    return m


def sprocket():
    """A clockwork pup of copper plate: big round puppy lenses looking up at you, flying goggles pushed up on its
    head, floppy metal ears that flap as it trots, its tongue hanging out over two bolt teeth, a brass collar with
    a gear for a tag, and a coil spring for a tail."""
    m = monster("dino_Sprocket", Body=COPPER, Accent=COPPER_DARK, Belly=BRASS_LIGHT, Claw="#3a3d47", Strap="#5a3a28", Nose="#1b1c22")
    m.joint("Spine", (0, 0, 1.55))
    quad_legs(m, 0.55, 0.75, 0.55, -0.75, 1.45, 0.5)
    for end, y in (("Front", 0.75), ("Back", -0.75)):  # brass knee bolts
        for side in (-1, 1):
            m.bone = end + ("L" if side < 0 else "R")
            m.block("Trim", side * (0.55 + 0.27), y, 1.2, 0.08, 0.2, 0.2)
    m.bone = "Spine"
    body = ((-1.05, 0, 1.78, 1.15, 1.05), (0.95, 0, 1.88, 1.3, 1.2))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-0.8, 0, 1.3, 0.85, 0.2), (0.85, 0, 1.33, 1.0, 0.24))
    for y in (-0.55, 0.25):  # riveted bands round the copper
        top = top_of(body, y)
        half = (1.15 + 0.15 * (y + 1.05) / 2.0) / 2
        m.block("Accent", 0, y, top + 0.02, half * 2 + 0.06, 0.18, 0.06)
        for s in (-1, 1):
            m.block("Accent", s * (half + 0.03), y, top - 0.5, 0.06, 0.18, 1.0)
    side_rivets(m, (-0.85, -0.25, 0.45), 1.95, 0.62)
    # A coil spring for a tail, curling up behind it.
    m.use("Tail1", (0, -1.0, 2.0))
    pts = []
    for k in range(25):
        t = k / 24
        a = t * math.tau * 4
        centre = Vector((0, -1.0 - 0.55 * t, 2.0 + 1.0 * t * (1.4 - 0.4 * t)))
        pts.append(centre + Vector((math.cos(a) * 0.2, math.sin(a) * 0.12, math.sin(a) * 0.16)))
    for k, (p, q) in enumerate(zip(pts, pts[1:])):
        m.bone = "Tail1" if k < 8 else ("Tail2" if k < 16 else "Tail3")
        if k == 8:
            m.use("Tail2", tuple(pts[8] * 1.0), "Tail1")
        if k == 16:
            m.use("Tail3", tuple(pts[16] * 1.0), "Tail2")
        beam(m, "Steel", tuple(p), tuple(q), 0.1)
    ball(m, "Trim", *pts[-1], 0.16, 6, 4)
    m.bone = "Spine"
    wind_key(m, -0.45, top_of(body, -0.45), 0.7)

    m.use("Neck", (0, 0.95, 2.05))
    m.block("Body", 0, 1.05, 2.15, 0.85, 0.55, 0.7)
    prism(m, "Trim", 0, 1.1, 1.92, 2.08, 0.5, 0.5, 12)  # the collar
    gear(m, "Trim", (0, 1.52, 1.72), 0.2, 8, 0.06, UPRIGHT, spokes=4, tooth=0.08)  # its tag
    w, d, h = 1.25, 1.15, 1.05
    yc, zc = 1.45, 2.6
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    mouth_z, gap = zc - 0.36, 0.14

    def tongue_and_bolts(m, front, mouth_z, gap, lower_length):
        limb(m, "Tongue", [(0.12, front + lower_length * 0.5, mouth_z - gap / 2 + 0.04), (0.16, front + lower_length + 0.08, mouth_z - 0.06),
                           (0.18, front + lower_length + 0.16, mouth_z - 0.4)], 0.2, 0.18)
        fang_row(m, (-0.2, 0.2), front + lower_length - 0.06, mouth_z - gap / 2, 0.14, 0.1, False)

    snout = classic_mouth(m, front, mouth_z, w, 0.5, 0.78, 0.26, 0.22, gap, upper="Belly", lower="Belly", tongue=False, skull_d=d,
                          on_jaw=tongue_and_bolts)
    y = snout["tip"] - 0.1
    ball(m, "Nose", 0, y, snout["top"](y) + 0.06, 0.15, 8, 4)
    for side in (-1, 1):
        lens_eye(m, (side * 0.32, front, zc + 0.27), "y", 0.5, -side, white=True, look=(0.0, 0.45))
        m.use("WingL" if side < 0 else "WingR", (side * w / 2, yc, zc + 0.3), "Head")  # floppy ears
        plate(m, "Accent", (side * (w / 2 + 0.06), yc - 0.05, zc + 0.36), (side * (w / 2 + 0.32), yc - 0.2, zc - 0.42), (0, 1, 0), 0.4, 0.5, 0.08)
        m.bone = "Head"
    # The flying goggles pushed up on its head, on their strap.
    m.block("Strap", 0, yc - 0.05, zc + h / 2 + 0.03, w + 0.08, 0.3, 0.08)
    for side in (-1, 1):
        m.block("Strap", side * (w / 2 + 0.03), yc - 0.05, zc + 0.3, 0.08, 0.3, 0.5)
        c = (side * 0.3, yc + 0.12, zc + h / 2 + 0.2)
        prism(m, "Trim", c[0], c[1], c[2] - 0.15, c[2] + 0.12, 0.26, 0.24, 10)
        prism(m, "Glass", c[0], c[1], c[2] + 0.12, c[2] + 0.16, 0.18, 0.18, 10)
    m.block("Trim", 0, yc + 0.12, zc + h / 2 + 0.12, 0.2, 0.12, 0.1)
    m.head_centre = (0, front + 0.2, zc + 0.05)
    return grow(m, 1.15)


def kettle_belly():
    """A grumpy walking boiler: a riveted iron drum on stubby legs, its furnace door glowing in its belly and a
    pressure gauge on its chest, a domed lid and a little chimney for a hat, a whistle spout on its cheek, gritted
    square teeth under heavy level brows and half-shut lids, and pipes for arms ending in wrench claws."""
    m = monster("dino_KettleBelly", Body="#4a5163", Accent="#2c313d", Belly=COPPER, Claw=STEEL, Dial="#fff0c6", Needle="#b8262a",
                Soot=SOOT, Steam=STEAM)
    m.joint("Spine", (0, 0, 1.0))
    biped_legs(m, 0.55, 0.0, 0.95, 0.6, 0.62, 0.46, 0.95, 0.26)
    prism(m, "Body", 0, 0, 0.85, 2.9, 1.15, 1.15, 12, math.pi / 12)
    prism(m, "Accent", 0, 0, 0.78, 0.95, 1.1, 1.2, 12, math.pi / 12)
    for z in (1.25, 2.55):
        prism(m, "Belly", 0, 0, z - 0.1, z + 0.1, 1.2, 1.2, 12, math.pi / 12)
        for k in range(12):
            a = k * math.tau / 12
            m.block("Rivet", math.cos(a) * 1.22, math.sin(a) * 1.22, z, 0.1, 0.1, 0.1)
    fy = 1.15 * math.cos(math.pi / 12)  # the drum's front face
    m.block("Soot", 0, fy + 0.03, 1.8, 0.95, 0.08, 0.75)  # the furnace door
    m.block("Furnace", 0, fy + 0.06, 1.8, 0.75, 0.06, 0.55)
    for x in (-0.24, 0.0, 0.24):
        m.block("Accent", x, fy + 0.1, 1.8, 0.07, 0.06, 0.6)
    m.block("Accent", 0, fy + 0.1, 2.17, 1.0, 0.08, 0.1)
    round_slab(m, "Trim", (0.62, fy - 0.1, 2.28), "y", 0.22, 0.2, 12)  # a gauge on its chest
    round_slab(m, "Dial", (0.62, fy + 0.01, 2.28), "y", 0.17, 0.06, 12)
    m.block("Needle", 0.66, fy + 0.05, 2.32, 0.04, 0.03, 0.14)
    for side in (-1, 1):  # pipes for arms, wrench claws for hands
        m.use("ArmL" if side < 0 else "ArmR", (side * 1.1, 0.1, 2.35))
        beam(m, "Accent", (side * 1.1, 0.1, 2.35), (side * 1.45, 0.45, 1.75), 0.26)
        m.block("Trim", side * 1.45, 0.45, 1.75, 0.34, 0.34, 0.34)
        beam(m, "Accent", (side * 1.45, 0.45, 1.75), (side * 1.5, 0.95, 1.55), 0.24)
        for off in (-0.13, 0.13):
            beam(m, "Claw", (side * 1.5 + off, 0.95, 1.55), (side * 1.5 + off * 1.2, 1.35, 1.6), 0.14, 0.18, 0.1)
    m.bone = "Spine"
    wind_key(m, -0.75, 2.9, 0.7)

    w, d, h = 1.9, 1.6, 1.2
    yc, zc = 0.4, 3.5
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    m.block("Belly", 0, yc, zc - h / 2 + 0.1, w + 0.08, d + 0.08, 0.16)
    prism(m, "Body", 0, yc, zc + h / 2, zc + h / 2 + 0.3, 0.95, 0.7, 12)  # the lid and its knob
    prism(m, "Accent", 0, yc, zc + h / 2 + 0.3, zc + h / 2 + 0.42, 0.32, 0.32, 8)
    ball(m, "Trim", 0, yc, zc + h / 2 + 0.55, 0.16, 6, 4)
    prism(m, "Accent", 0.62, yc - 0.45, zc + h / 2 - 0.05, zc + h / 2 + 0.85, 0.2, 0.2, 8)  # its chimney, and a puff
    prism(m, "Accent", 0.62, yc - 0.45, zc + h / 2 + 0.85, zc + h / 2 + 1.0, 0.28, 0.28, 8)
    for k, (x, z, r) in enumerate(((0.66, 1.25, 0.18), (0.52, 1.5, 0.22), (0.72, 1.78, 0.26))):
        m.block("Steam", x, yc - 0.45, zc + h / 2 + z, r * 2, r * 2, r * 1.6)
    tube(m, "Trim", (-w / 2 + 0.05, yc + 0.3, zc - 0.05), (-w / 2 - 0.55, yc + 0.75, zc + 0.3), 0.17, 0.11)  # a whistle spout
    mouth_z, gap = zc - 0.34, 0.16

    def lower_teeth(m, front, mouth_z, gap, lower_length):
        tin_teeth(m, (-0.55, -0.33, -0.11, 0.11, 0.33, 0.55), front + lower_length - 0.07, mouth_z - gap / 2, 0.13, 0.17, False)

    classic_mouth(m, front, mouth_z, w, 0.28, 1.65, 0.2, 0.28, gap, upper="Body", lower="Accent", tongue=False, skull_d=d,
                  underbite=1.2, on_jaw=lower_teeth)
    tin_teeth(m, (-0.6, -0.36, -0.12, 0.12, 0.36, 0.6), front + 0.22, mouth_z + gap / 2, 0.14, 0.18, True)
    for side in (-1, 1):
        lens_eye(m, (side * 0.47, front, zc + 0.27), "y", 0.52, -side, white=True, look=(0.0, -0.2), lid=0.35, slant=0.7, brow=0.0,
                 lid_role="Body", brow_role="Accent")
    rivets(m, [(s * (w / 2 + 0.02), yc + dy, zc + 0.35) for s in (-1, 1) for dy in (-0.5, 0.0, 0.5)])
    m.head_centre = (0, front + 0.2, zc + 0.1)
    return m


# ---------------------------------------------------------------------- the rare ones


def gearjaw():
    """A steel clockwork raptor: a buzz saw spinning in a slot along its skull, dark lenses glaring furnace orange
    under brows slanting to its snout, a long jaw of steel fangs with a furnace glowing in its throat, brass
    bands down its tail and pistons along its thighs."""
    m = monster("dino_Gearjaw", Body="#5d6577", Accent="#3d4352", Belly=BRASS, Claw="#dfe6ee", EyeGlow=FURNACE, Saw="#c9d2dd")
    m.joint("Spine", (0, 0, 2.3))
    biped_legs(m, 0.5, -0.1, 2.25, 0.62, 1.3, 0.38, 1.25, 0.26)
    for side in (-1, 1):  # pistons along its thighs
        m.bone = "LegL" if side < 0 else "LegR"
        x = side * 0.84
        m.block("Trim", x, -0.1, 2.0, 0.12, 0.3, 0.3)
        beam(m, "Steel", (x, -0.05, 1.95), (x, 0.0, 1.05), 0.1)
        m.block("Trim", x, 0.0, 1.0, 0.14, 0.24, 0.24)
    m.bone = "Spine"
    body = ((-1.2, 0, 2.45, 1.0, 1.0), (1.0, 0, 2.75, 1.15, 1.3))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-0.9, 0, 1.98, 0.7, 0.14), (0.95, 0, 2.15, 0.85, 0.2))
    for y in (-0.8, -0.25, 0.3, 0.8):  # armour plates down its back
        m.block("Accent", 0, y, top_of(body, y) + 0.05, 0.75, 0.45, 0.12)
    side_rivets(m, (-0.8, -0.2, 0.4), 2.6, 0.55)
    tail(m, (-1.15, 2.55, 0.7, 0.7), (-3.5, 2.85, 0.14, 0.14), 3)
    for i, y in ((1, -1.6), (2, -2.35), (3, -3.0)):
        m.bone = f"Tail{i}"
        t = (y + 1.15) / (-3.5 + 1.15)
        r = 0.7 + (0.14 - 0.7) * t
        z = 2.55 + (2.85 - 2.55) * t
        m.block("Trim", 0, y, z, r + 0.08, 0.16, r + 0.08)
    m.bone = "Spine"
    for side in (-1, 1):  # small clawed arms
        m.use("ArmL" if side < 0 else "ArmR", (side * 0.5, 0.75, 2.4))
        beam(m, "Body", (side * 0.5, 0.75, 2.4), (side * 0.62, 1.15, 1.95), 0.22, None, 0.18)
        for off in (-0.07, 0.07):
            beam(m, "Claw", (side * 0.62 + off, 1.15, 1.95), (side * 0.64 + off, 1.4, 1.78), 0.07, None, 0.02)
    m.bone = "Spine"
    wind_key(m, -0.45, top_of(body, -0.45) + 0.1, 0.6)

    m.use("Neck", (0, 0.9, 2.95))
    beam(m, "Body", (0, 0.85, 2.85), (0, 1.45, 3.7), 0.62, 0.7, 0.55)
    m.stretch("Body", "Spine")
    w, d, h = 0.95, 1.2, 1.1
    yc, zc = 1.75, 4.0
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    mouth_z, gap = zc - 0.3, 0.18

    def throat(m, front, mouth_z, gap, lower_length):  # a furnace glowing down its throat, fangs at the front
        m.block("Furnace", 0, front + lower_length * 0.35, mouth_z - gap / 2 + 0.06, 0.4, lower_length * 0.6, 0.04)
        fang_row(m, (-0.18, 0.18), front + lower_length - 0.08, mouth_z - gap / 2, 0.22, 0.1, False)

    snout = classic_mouth(m, front, mouth_z, w, 1.15, 0.62, 0.28, 0.22, gap, upper="Body", lower="Accent", tooth=0.15, per_side=6,
                          lower_teeth=True, tongue=False, skull_d=d, on_jaw=throat)
    fang_row(m, (-0.2, 0.2), snout["tip"] - 0.1, mouth_z + gap / 2, 0.26, 0.11, True)
    for side in (-1, 1):
        lens_eye(m, (side * 0.25, front, zc + 0.33), "y", 0.4, -side, white=False, lid=0.22, slant=1.0, brow=-0.06, lid_role="Accent",
                 brow_role="Accent")
    # The buzz saw in a slot along its skull, on its own Cog bone, turning for ever.
    m.block("Accent", 0, yc - 0.05, zc + h / 2 + 0.06, 0.34, d - 0.1, 0.12)
    m.use("Cog", (0, yc - 0.05, zc + h / 2 + 0.15), "Head")
    gear(m, "Saw", (0, yc - 0.05, zc + h / 2 + 0.15), 0.62, 14, 0.08, SIDEWAYS, spokes=4, tooth=0.2)
    m.bone = "Head"
    m.head_centre = (0, front + 0.4, zc)
    return grow(m, 1.22)


def drillhorn():
    """An iron clockwork triceratops: a great brass gear standing behind its head for a frill, two steel brow
    horns, and for a nose horn a drill that never stops boring (its own Drill bone). Dark lenses glare orange under
    heavy slanted brows, a beak of steel teeth hides a furnace, furnace light glows through grilles in its flanks,
    and two exhaust stacks lean back from its shoulders."""
    m = monster("dino_Drillhorn", Body=IRON, Accent=IRON_DARK, Belly=COPPER, Claw=STEEL, EyeGlow=FURNACE, Frill=BRASS, Bit="#c9d2dd",
                Soot=SOOT)
    m.joint("Spine", (0, 0, 2.6))
    quad_legs(m, 0.85, 1.1, 0.85, -1.2, 2.5, 0.8)
    for end, y in (("Front", 1.1), ("Back", -1.2)):  # brass knee plates
        for side in (-1, 1):
            m.bone = end + ("L" if side < 0 else "R")
            m.block("Trim", side * 0.85, y + 0.48, 1.6, 0.6, 0.1, 0.5)
            rivets(m, [(side * 0.85 + dx, y + 0.54, 1.6) for dx in (-0.18, 0.18)])
    m.bone = "Spine"
    body = ((-1.9, 0, 2.9, 2.0, 1.9), (1.4, 0, 3.1, 2.3, 2.2))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-1.6, 0, 1.98, 1.6, 0.2), (1.3, 0, 2.02, 1.9, 0.24))
    for k, y in enumerate((-1.45, -0.75, -0.05, 0.65)):  # overlapping armour plates down its back
        top = top_of(body, y)
        m.loft_y("Accent", (y - 0.4, 0, top - 0.05, 1.5, 0.3), (y + 0.4, 0, top + 0.12, 1.3, 0.3))
    for side in (-1, 1):  # furnace grilles in its flanks
        half = 1.0 + 0.15 * (0.4 + 1.9) / 3.3
        x = side * (half + 0.01)
        m.block("Soot", x, -0.2, 2.95, 0.06, 1.3, 0.75)
        m.block("Furnace", side * (half + 0.03), -0.2, 2.95, 0.04, 1.1, 0.58)
        for y in (-0.62, -0.34, -0.06, 0.22):
            m.block("Accent", side * (half + 0.06), y, 2.95, 0.06, 0.08, 0.7)
        side_rivets(m, (-1.5, -0.95, 0.55, 1.1), 3.45, half - 0.02)
        beam(m, "Steel", (side * 0.55, 0.7, top_of(body, 0.7) - 0.1), (side * 0.75, -0.2, top_of(body, 0.7) + 1.3), 0.32, None, 0.3)  # stacks
        prism(m, "Soot", side * 0.75, -0.2, top_of(body, 0.7) + 1.25, top_of(body, 0.7) + 1.45, 0.2, 0.2, 8)
    tail(m, (-1.85, 3.0, 0.9, 0.9), (-3.3, 2.4, 0.28, 0.28), 3)
    wind_key(m, -1.1, top_of(body, -1.1) + 0.15, 0.75)

    m.use("Neck", (0, 1.3, 3.3))
    m.block("Body", 0, 1.55, 3.35, 1.4, 0.8, 1.3)
    w, d, h = 1.75, 1.6, 1.5
    yc, zc = 2.2, 3.55
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    gear(m, "Frill", (0, yc - d / 2 - 0.22, zc + 0.55), 2.0, 16, 0.24, UPRIGHT, spokes=6, tooth=0.42)  # its gear frill
    mouth_z, gap = zc - 0.42, 0.2

    def throat(m, front, mouth_z, gap, lower_length):
        m.block("Furnace", 0, front + lower_length * 0.35, mouth_z - gap / 2 + 0.06, 0.7, lower_length * 0.6, 0.04)

    snout = classic_mouth(m, front, mouth_z, w, 0.95, 1.0, 0.36, 0.3, gap, upper="Body", lower="Accent", tooth=0.16, per_side=5,
                          lower_teeth=True, tongue=False, skull_d=d, on_jaw=throat)
    fang_row(m, (-0.3, 0.3), snout["tip"] - 0.1, mouth_z + gap / 2, 0.28, 0.13, True)
    for side in (-1, 1):
        lens_eye(m, (side * 0.43, front, zc + 0.42), "y", 0.48, -side, white=False, lid=0.25, slant=1.0, brow=-0.06, lid_role="Accent",
                 brow_role="Accent")
        prism(m, "Steel", side * 0.5, yc + 0.2, zc + h / 2 - 0.1, zc + h / 2 + 1.25, 0.2, 0.03, 6, 0, (side * 0.1, 0.75))  # brow horns
        prism(m, "Trim", side * 0.5, yc + 0.2, zc + h / 2 - 0.12, zc + h / 2 + 0.06, 0.26, 0.26, 6)
    # The drill on its nose, on its own Drill bone: pointing straight ahead, so it turns true.
    tip_y = snout["tip"]
    dz = mouth_z + gap / 2 + 0.36 * 0.5
    tube(m, "TrimDark", (0, tip_y - 0.15, dz), (0, tip_y + 0.12, dz), 0.36, 0.36, 10)
    m.use("Drill", (0, tip_y + 0.1, dz), "Head")
    tube(m, "Bit", (0, tip_y + 0.1, dz), (0, tip_y + 0.3, dz), 0.3, 0.3, 10)
    for k in range(4):  # the bit tapers in four steps, with a spiral flute winding round it
        y0 = tip_y + 0.3 + k * 0.3
        tube(m, "Bit", (0, y0, dz), (0, y0 + 0.3, dz), 0.3 - k * 0.07, 0.3 - (k + 1) * 0.07, 10)
    tube(m, "Bit", (0, tip_y + 1.5, dz), (0, tip_y + 1.75, dz), 0.04, 0.01, 6)
    for k in range(16):
        t = k / 15
        a = t * math.tau * 2.5
        r = 0.32 - t * 0.27
        y = tip_y + 0.32 + t * 1.25
        for flute in (0, math.pi):
            m.block("Steel", math.cos(a + flute) * r, y, dz + math.sin(a + flute) * r, 0.1, 0.12, 0.1)
    m.bone = "Head"
    m.head_centre = (0, front + 0.4, zc + 0.15)
    return grow(m, 1.12)


def chrono_rex():
    """The boss: a towering iron tyrant. A giant brass gear turns on its back like a sail (its own Cog bone),
    smokestacks glow on its shoulders, a furnace heart burns behind a riveted porthole in its chest, brass ribs
    run down its flanks and bands round its tail, and the wind-up key at the root of its tail never stops. Its
    skull carries a crest of gear teeth, its dark lenses glare furnace orange under heavy brows slanting to the
    snout, its nostrils smoulder and its jaw is full of steel fangs with fire in its throat."""
    m = monster("dino_ChronoRex", Body="#363b48", Accent="#1f232b", Belly=BRASS, Claw="#dfe6ee", EyeGlow=FURNACE, Sail=BRASS,
                Crown=BRASS_LIGHT, Soot=SOOT)
    m.joint("Spine", (0, 0, 5.0))
    biped_legs(m, 1.25, -0.4, 5.0, 1.55, 2.9, 1.0, 2.7, 0.55)
    for side in (-1, 1):  # brass knee caps and rivets up the thighs
        m.bone = "LegL" if side < 0 else "LegR"
        x = side * 1.25
        m.block("Trim", x, 0.42, 3.15, 1.0, 0.24, 0.8)
        rivets(m, [(x + side * 0.8, -0.4 + dy, z) for dy in (-0.3, 0.3) for z in (3.4, 4.2)], 0.14)
    m.bone = "Spine"
    body = ((-2.6, 0, 5.7, 2.6, 2.6), (1.8, 0, 6.7, 3.0, 3.3))
    m.loft_y("Body", *body)
    for y in (-1.9, -1.1, -0.3, 0.5, 1.2):  # armour plates down its back
        m.block("Accent", 0, y, top_of(body, y) + 0.05, 1.9, 0.6, 0.16)
    for side in (-1, 1):  # brass ribs down its flanks
        for y in (-1.6, -0.9, -0.2, 0.5, 1.15):
            t = (y + 2.6) / 4.4
            half = (2.6 + 0.4 * t) / 2
            zc_ = 5.7 + 1.0 * t
            hh = (2.6 + 0.7 * t) / 2
            beam(m, "Belly", (side * (half + 0.04), y, zc_ + hh * 0.55), (side * (half + 0.04), y + 0.25, zc_ - hh * 0.75), 0.24, 0.12)
    # The furnace heart behind a riveted porthole in its chest.
    zf, yf = 6.1, 1.8
    round_slab(m, "Trim", (0, yf + 0.06, zf), "y", 1.0, 0.12, 16)
    round_slab(m, "Furnace", (0, yf + 0.14, zf), "y", 0.78, 0.06, 16)
    for x in (-0.4, 0.0, 0.4):
        m.block("Accent", x, yf + 0.2, zf, 0.1, 0.08, 1.4 - abs(x) * 0.9)
    m.block("Accent", 0, yf + 0.2, zf, 1.5, 0.08, 0.1)
    rivets(m, [(math.cos(k * math.tau / 10) * 0.9, yf + 0.14, zf + math.sin(k * math.tau / 10) * 0.9) for k in range(10)], 0.12)
    # The gear sail on its back, on its own Cog bone, between two brackets holding its axle.
    ys = -1.2  # far enough back that the turning sail clears the head, its crest and the key
    back = top_of(body, ys)
    zs = back + 2.3
    for x in (-0.38, 0.38):
        m.block("Accent", x, ys, (back + zs) / 2, 0.16, 1.1, zs - back + 0.4)
    tube(m, "Steel", (-0.55, ys, zs), (0.55, ys, zs), 0.32)
    m.use("Cog", (0, ys, zs))
    gear(m, "Sail", (0, ys, zs), 2.6, 16, 0.3, SIDEWAYS, spokes=6, tooth=0.55)
    m.bone = "Spine"
    for side in (-1, 1):  # smokestacks on its shoulders, glowing at the mouth
        base = (side * 1.0, 1.0, top_of(body, 1.0) - 0.2)
        top = (side * 1.25, 0.25, top_of(body, 1.0) + 1.9)
        beam(m, "Steel", base, top, 0.55, None, 0.5)
        prism(m, "Soot", top[0], top[1], top[2] - 0.05, top[2] + 0.25, 0.36, 0.36, 8)
        prism(m, "Furnace", top[0], top[1], top[2] + 0.12, top[2] + 0.27, 0.24, 0.24, 8)
    tail(m, (-2.55, 5.8, 1.6, 1.6), (-7.0, 4.7, 0.3, 0.3), 3)
    for i, y in ((1, -3.6), (2, -5.0), (3, -6.3)):  # brass bands and spikes down its tail
        m.bone = f"Tail{i}"
        t = (y + 2.55) / (-7.0 + 2.55)
        r = 1.6 + (0.3 - 1.6) * t
        z = 5.8 + (4.7 - 5.8) * t
        m.block("Belly", 0, y, z, r + 0.12, 0.3, r + 0.12)
        prism(m, "Steel", 0, y + 0.45, z + r / 2 - 0.05, z + r / 2 + 0.55 * r, 0.2 * r + 0.05, 0.02, 4, math.pi / 4, (0, -0.15))
    m.bone = "Spine"
    wind_key(m, -3.6, 6.18, 0.9, parent="Tail1")
    for side in (-1, 1):  # small clawed arms
        m.use("ArmL" if side < 0 else "ArmR", (side * 1.3, 1.4, 5.9))
        beam(m, "Body", (side * 1.3, 1.4, 5.9), (side * 1.55, 2.25, 5.15), 0.55, None, 0.45)
        for off in (-0.16, 0.0, 0.16):
            beam(m, "Claw", (side * 1.55 + off, 2.3, 5.1), (side * 1.58 + off, 2.75, 4.8), 0.14, None, 0.03)
    m.bone = "Spine"

    m.use("Neck", (0, 1.55, 7.2))
    beam(m, "Body", (0, 1.4, 7.0), (0, 2.4, 8.2), 2.0, 2.1, 1.8)
    m.stretch("Body", "Spine")
    w, d, h = 2.3, 2.6, 2.3
    yc, zc = 3.1, 8.6
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    mouth_z, gap = zc - 0.55, 0.42

    def throat(m, front, mouth_z, gap, lower_length):  # fire in its throat, fangs up from its jaw
        m.block("Furnace", 0, front + lower_length * 0.35, mouth_z - gap / 2 + 0.075, 1.1, lower_length * 0.6, 0.05)
        fang_row(m, (-0.55, -0.18, 0.18, 0.55), front + lower_length - 0.15, mouth_z - gap / 2, 0.42, 0.22, False)

    snout = classic_mouth(m, front, mouth_z, w, 1.6, 1.9, 0.6, 0.55, gap, upper="Body", lower="Accent", tooth=0.3, per_side=6,
                          lower_teeth=True, tongue=False, skull_d=d, on_jaw=throat)
    fang_row(m, (-0.62, -0.22, 0.22, 0.62), snout["tip"] - 0.18, mouth_z + gap / 2, 0.55, 0.26, True)
    y = snout["tip"] - 0.3
    for side in (-1, 1):  # smouldering nostrils
        m.block("Furnace", side * 0.4, y, snout["top"](y) + 0.03, 0.26, 0.3, 0.08)
        lens_eye(m, (side * 0.6, front, zc + 0.72), "y", 0.62, -side, white=False, lid=0.25, slant=1.0, brow=-0.05, lid_role="Accent",
                 brow_role="Accent")
        rivets(m, [(side * (w / 2 + 0.02), yc + dy, zc + dz) for dy in (-0.8, 0.0, 0.8) for dz in (-0.3, 0.5)], 0.12)
    gear(m, "Crown", (0, yc, zc + h / 2 + 0.05), 1.0, 12, 0.28, SIDEWAYS, spokes=4, tooth=0.36)  # its crest of gear teeth
    m.head_centre = (0, front + 0.6, zc + 0.3)
    return m


ALL = [wind_up_wally, sprocket, kettle_belly, gearjaw, drillhorn, chrono_rex]


def quick_preview(models, out):
    """Stills only, for trying faces: each model whole, its face up close and straight on, and the lineup."""
    import bpy
    scene = kit.setup_scene()
    kit.RENDERS = out
    out.mkdir(parents=True, exist_ok=True)
    animals = bpy.data.collections.new("Animals")
    scene.collection.children.link(animals)
    roots = []
    for i, model in enumerate(models):
        root = model.build(animals)
        root.location = (i * 16, 0, 0)
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
        kit.shoot(scene, f"{model.name}_full", centre + Vector((0.62, 0.85, 0.32)) * reach * 1.15, centre, (640, 640), 50)
        head = root.location + Vector(model.head_centre)
        size = max(3.2, model.head_centre[2] * 0.75)
        kit.shoot(scene, f"{model.name}_face", head + Vector((0.55, 1.0, 0.14)) * size * 1.5, head, (560, 560), 50)
        kit.shoot(scene, f"{model.name}_front", head + Vector((0, 1, 0.1)) * size * 1.6, head, (560, 560), 50)
    kit.set_visible(roots, roots)
    middle = (len(models) - 1) * 16 / 2
    kit.shoot(scene, "lineup", (middle, 84, 20), (middle, 0, 5.5), (1800, 700), 26)


def main():
    builders = ALL
    only = os.environ.get("ONLY")
    if only:
        builders = [b for b in builders if b.__name__ in only.split(",")]
    models = [b() for b in builders]
    if os.environ.get("QUICK"):
        quick_preview(models, Path(os.environ.get("QUICK_OUT", str(RENDERS / "quick"))))
        return
    build_and_render(models, RENDERS, HERE / f"{BLEND}.blend", "clockwork_citadel_animation_preview.mp4", sky=SKY, ground=FLOOR,
                     glow_roles=GLOW_ROLES, spacing=16, animate_fn=animate, glow=GLOW)


if __name__ == "__main__":
    main()
