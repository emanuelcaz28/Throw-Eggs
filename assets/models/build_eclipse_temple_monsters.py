"""Builds Eclipse Temple's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_eclipse_temple_monsters.py
    QUICK=1 Blender -b -P build_eclipse_temple_monsters.py    (stills only, into QUICK_OUT, for trying faces)
    ONLY=idol_ollie,jade_jaguar QUICK=1 ...                     (just those)

Saves eclipse_temple_monsters.blend and renders to design/world/monsters_eclipse_temple/. The map's props are in
build_eclipse_temple.py.

Map 9 opens the mysterious, dark maps. After Starfall Crater's calm faces the run picks up again (GAME_SPEC
8a): the common ones are silly, temple thieves and squatters, and the rare ones are the temple's fierce
guardians, ending in a boss. They share the eclipse eye: a black iris ringed with glowing jade, like the
eclipsed sun over the map. The silly ones have it in a white eye; the fierce ones have no white at all, just
the black eye and its jade ring under a gold mask, which is what makes them unsettling. The map's colours:
jungle green, red laterite, temple stone, obsidian, old gold and jade.

  Idol Ollie         a derpy toad that stole a temple idol and wears it as a helmet; the idol's stern face
                     peers over its bulging, cross-eyed eyes, and its tongue hangs out
  Mossy Mo           a sleepy sloth carrying a little temple ruin on its back, a jungle growing on it; one eye
                     shut, the other barely open, and its roar is a huge yawn
  Lantern Larry      a lanky temple monkey with a lantern, a gold mask pushed up on its head and a gold tooth
                     in a sneaky grin, eyes sliding sideways, tail curled into a spiral
  Jade Jaguar        an obsidian guardian cat with glowing jade rosettes, a gold mask over its black eclipse
                     eyes, gold collar and bands, fangs bared
  Plumed Wyrm        a feathered serpent-dragon: emerald scales, a golden belly, feathered wings, a huge crest
                     and ruff of green, gold and red plumes round a toothy snout
  Eclipse Devourer   the boss: a four-armed obsidian god-beast that swallowed the sun. A black sun with a
                     burning corona behind its head, the eaten sun still glowing in its chest, a black sun in
                     each raised hand, a gold mask, a third eye, great horns, and jade fire in its throat

All have a Jaw bone (they snap as they walk and roar once per idle in the game, DinoLifeController); extra arms
and wings ride the Wing bones. Glowing parts are EyeGlow, Jade, Pod, Lamp, EclipseRing and Corona (Neon in the
game, shared/Roles.luau, all there already). Skin roles Body, Accent, Belly and Claw take the colour mutations;
gold (Trim, TrimDark, Gold), plumes and jade keep their colour. Built at the first map's size; the game scales
them by Config/Biomes standardScale. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0.
"""
import math
import os
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_desert import beam, quad_legs  # noqa: E402
from build_forest import Model, biped_legs, tail  # noqa: E402
from build_starfall_crater import ball, gem  # noqa: E402
from build_volcano import prism, ring_at, top_of  # noqa: E402
from face_kit import classic_mouth, top_nostrils  # noqa: E402
from map_kit import plate  # noqa: E402
from monster_stage import build_and_render, light_up, set_sky  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_eclipse_temple"
BLEND = "eclipse_temple_monsters"  # for check_map.py and export_fbx.py

GLOW_ROLES = {"EyeGlow", "Jade", "Pod", "Lamp", "EclipseRing", "Corona"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket", "Void"})
GLOW = 1.3  # render glow strength; stronger clips the jade to cyan

# The map's colours (build_eclipse_temple.py) and the eclipse face.
JADE = "#47ff9c"
GOLD, GOLD_DARK = "#f0b93a", "#b8801f"
STONE, STONE_DARK = "#9c9d86", "#6e705e"
MOSS, LEAF, LEAF_DARK, BARK = "#5aa04e", "#2f7a45", "#215c35", "#5e4636"
FACE = {"Pupil": "#0c0a12", "Socket": "#0c0a12", "EyeGlow": JADE, "EyeWhite": "#f6f1e2", "Mouth": "#3a1420", "Teeth": "#f4ecd6",
        "Tongue": "#e0607e", "Trim": GOLD, "TrimDark": GOLD_DARK, "Gold": GOLD, "Jade": JADE}
SKY, FLOOR = "#1b2b2e", "#804642"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- the eclipse face


def at(origin, normal, u, v, n):
    """A point on a face: u across it, v up, n out of it. normal "y" is a front face (u = x), "+x" or "-x" a
    side face (u = y, forwards)."""
    x0, y0, z0 = origin
    if normal == "y":
        return (x0 + u, y0 + n, z0 + v)
    s = 1 if normal == "+x" else -1
    return (x0 + s * n, y0 + u, z0 + v)


def face_box(m, role, origin, normal, u, v, n, wu, wv, wn):
    x, y, z = at(origin, normal, u, v, n)
    if normal == "y":
        m.block(role, x, y, z, wu, wn, wv)
    else:
        m.block(role, x, y, z, wn, wu, wv)


def round_slab(m, role, centre, normal, r, depth, sides=10):
    """A round slab lying flat on a face that looks along normal ("y", "+x", "-x" or "z")."""
    cx, cy, cz = centre
    verts = []
    for k in (-depth / 2, depth / 2):
        for i in range(sides):
            a = math.pi / sides + i * math.tau / sides
            u, v = r * math.cos(a), r * math.sin(a)
            if normal == "y":
                verts.append((cx + u, cy + k, cz + v))
            elif normal == "z":
                verts.append((cx + u, cy + v, cz + k))
            else:
                verts.append((cx + k, cy + u, cz + v))
    faces = [list(range(sides))[::-1], list(range(sides, 2 * sides))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides + j, sides + i])
    m._add(role, verts, faces)


def iris(m, centre, normal, size, inner=1):
    """The eclipse: a black iris ringed with glowing jade, and a glint."""
    nv = {"y": Vector((0, 1, 0)), "+x": Vector((1, 0, 0)), "-x": Vector((-1, 0, 0))}[normal]
    c = Vector(centre)
    round_slab(m, "EyeGlow", tuple(c + nv * 0.02), normal, size * 0.36, 0.04)
    round_slab(m, "Pupil", tuple(c + nv * 0.045), normal, size * 0.25, 0.05)
    g = size * 0.09
    gx, gy, gz = at(tuple(c), normal, -inner * size * 0.1, size * 0.1, 0.075)
    m.block("Highlight", gx, gy, gz, g, g, g)


def eclipse_eye(m, origin, normal, size, inner=1, white=True, look=(0.0, 0.0), lid=0.0, slant=0.0, brow=None,
                lid_role="Body", brow_role="Accent", lash=False):
    """One eye on a face at origin (its middle, on the surface). inner (+1/-1) is the way to the nose along u.
    white: a white eye; otherwise a black socket, which reads far fiercer. look moves the iris (shares of the
    eye). lid covers that share of the eye from the top; slant tips the lid and the brow down towards the
    nose (angry) or up (sad, sleepy when negative). brow: how high a brow ridge sits over the eye, or None.
    lash: a dark line along the lid's edge, which makes a shut eye read as shut."""
    w, h = size * 1.0, size * 0.95
    face_box(m, "EyeWhite" if white else "Socket", origin, normal, 0, 0, 0.03, w, h, 0.08)
    iris(m, at(origin, normal, look[0] * w * 0.28, look[1] * h * 0.28, 0.07), normal, size, inner)
    top = h / 2 + size * 0.04
    dz = slant * size * 0.3

    def tilted(role, bottom, thick_top, depth, n):
        """A strip across the eye from its outer corner to its inner one, its bottom edge tilted by slant."""
        outer = at(origin, normal, -inner * (w / 2 + size * 0.05), 0, n)
        inner_p = at(origin, normal, inner * (w / 2 + size * 0.05), 0, n)
        bo, bi = bottom + dz, bottom - dz
        to, ti = thick_top + dz * 0.5, thick_top - dz * 0.5
        if normal == "y":
            m.loft_x(role, (outer[0], outer[1], outer[2] + (bo + to) / 2, depth, to - bo),
                     (inner_p[0], inner_p[1], inner_p[2] + (bi + ti) / 2, depth, ti - bi))
        else:
            m.loft_y(role, (outer[1], outer[0], outer[2] + (bo + to) / 2, depth, to - bo),
                     (inner_p[1], inner_p[0], inner_p[2] + (bi + ti) / 2, depth, ti - bi))

    if lid > 0:
        bottom = top - h * lid - size * 0.04
        tilted(lid_role, bottom, top + size * 0.02, 0.16, 0.08)
        if lash:
            tilted("Pupil", bottom - size * 0.03, bottom + size * 0.05, 0.18, 0.09)
    if brow is not None:
        tilted(brow_role, top + brow * size, top + brow * size + size * 0.24, size * 0.3, 0.12)


def rosette(m, c, normal, s, role="Jade"):
    """A jaguar's rosette: a broken ring of three bars, lying on a face looking along normal ("+x", "-x", "z")."""
    x, y, z = c
    t = 0.05
    if normal == "z":
        m.block(role, x - s, y, z, t * 1.6, 2 * s, t)
        m.block(role, x, y + s, z, 2 * s, t * 1.6, t)
        m.block(role, x + s, y - s * 0.2, z, t * 1.6, 1.4 * s, t)
    else:
        m.block(role, x, y - s, z, t, t * 1.6, 2 * s)
        m.block(role, x, y, z + s, t, 2 * s, t * 1.6)
        m.block(role, x, y + s, z - s * 0.2, t, t * 1.6, 1.4 * s)


def grow(m, k):
    """Scales a whole monster, bones and all, so the rarer ones stand bigger than the common ones."""
    for verts, _ in m.parts.values():
        verts[:] = [(x * k, y * k, z * k) for x, y, z in verts]
    m.joints = {name: (tuple(c * k for c in pivot), parent) for name, (pivot, parent) in m.joints.items()}
    m.head_centre = tuple(c * k for c in m.head_centre)
    return m


def flank(pair, y, share, side, out=0.0):
    """A point on the side of a loft_y body: share -1 is its bottom edge, 1 its top."""
    r = ring_at(*pair, y)
    return (side * (r[3] / 2 + out), y, r[2] + share * r[4] / 2)


def feather(m, base, tip, width, side_dir, role="Plume", tip_role="PlumeTip", tip_share=0.28):
    """A long flat feather from base to tip, broad along side_dir, its end in another colour."""
    b, t = Vector(base), Vector(tip)
    cut = b + (t - b) * (1 - tip_share)
    plate(m, role, tuple(b), tuple(cut), side_dir, width * 0.5, width, 0.07)
    plate(m, tip_role, tuple(cut), tuple(t), side_dir, width, width * 0.25, 0.08)


def sun_disc(m, centre, r, rays, ray_len, normal="y"):
    """A black eclipsed sun: a dark disc, a glowing ring and a corona of rays round it, facing normal ("y")."""
    cx, cy, cz = centre
    round_slab(m, "Void", centre, normal, r, 0.16, 16)
    pts = []
    n = 20
    for i in range(n):
        a = i * math.tau / n
        pts.append((cx + math.cos(a) * r * 1.06, cy, cz + math.sin(a) * r * 1.06))
    for i in range(n):
        beam(m, "EclipseRing", pts[i], pts[(i + 1) % n], r * 0.12, r * 0.12)
    for k in range(rays):
        a = k * math.tau / rays
        r2 = r * (1.12 + ray_len * (1.0 if k % 2 == 0 else 0.6))
        plate(m, "Corona", (cx + math.cos(a) * r * 1.1, cy, cz + math.sin(a) * r * 1.1), (cx + math.cos(a) * r2, cy, cz + math.sin(a) * r2),
              (-math.sin(a), 0, math.cos(a)), r * 0.32, r * 0.04, 0.1)


# ---------------------------------------------------------------------- the common ones


def idol_ollie():
    """A squat toad that stole a temple idol and wears it as a helmet, crooked. The idol's stern gold face, its eye
    slits glowing jade, peers over the toad's own bulging, cross-eyed eyes; its tongue hangs out of a wide grin."""
    m = monster("dino_IdolOllie", Body="#73b04c", Accent="#3f7a35", Belly="#efe2a8", Claw="#2e5a28")
    m.joint("Spine", (0, 0, 1.0))
    quad_legs(m, 1.0, 0.75, 1.0, -0.55, 0.85, 0.6)
    for side in (-1, 1):  # big folded back legs, flat feet
        m.bone = "BackL" if side < 0 else "BackR"
        m.loft_y("Body", (-1.35, side * 1.2, 0.6, 0.8, 0.75), (0.0, side * 1.15, 0.85, 0.9, 1.05))
        m.block("Belly", side * 1.3, 0.35, 0.12, 0.75, 1.0, 0.24)
    m.bone = "Spine"
    body = ((-1.3, 0, 1.15, 2.1, 1.25), (0.9, 0, 1.35, 2.5, 1.55))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-1.1, 0, 0.62, 1.7, 0.3), (0.85, 0, 0.7, 2.1, 0.45))
    for x, y in ((-0.6, -0.6), (0.55, -0.2), (-0.2, 0.25), (0.75, 0.55), (-0.8, 0.45), (0.15, -0.95), (-0.95, -0.2)):
        m.block("Accent", x, y, top_of(body, y) + 0.04, 0.32, 0.32, 0.12)
    m.block("Body", 0, -1.35, 1.1, 0.7, 0.3, 0.5)  # a stub of a rump

    w, d, h = 2.4, 1.5, 1.15
    yc, zc = 1.55, 1.55
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)

    def tongue_out(m, front, mouth_z, gap, lower_length):  # lolling out of one side, over the lip
        beam(m, "Tongue", (0.35, front + 0.05, mouth_z - gap / 2 + 0.03), (0.55, front + lower_length + 0.3, mouth_z - 0.38), 0.42, 0.12, 0.36)
        m.block("Tongue", 0.56, front + lower_length + 0.32, mouth_z - 0.47, 0.38, 0.14, 0.26)

    classic_mouth(m, front, zc - 0.28, w, 0.32, 2.2, 0.34, 0.3, 0.16, tongue=True, grin=0.14, skull_d=d, on_jaw=tongue_out)
    # Bulging eyes on top of its head, cross-eyed.
    for side, dx, dz in ((-1, 0.14, 0.08), (1, -0.06, -0.12)):  # one looks in and up, the other in and down
        ex, ey, ez = side * 0.74, front - 0.3, zc + h / 2 + 0.3
        m.loft_z("Body", (zc + h / 2 - 0.05, ex, ey - 0.1, 0.95, 0.85), (ez + 0.05, ex, ey - 0.05, 0.85, 0.75))
        ball(m, "EyeWhite", ex, ey, ez + 0.15, 0.5, 8, 5)
        iris(m, (ex + dx, ey + 0.44, ez + 0.15 + dz), "y", 0.62, -side)
    # The idol helmet, a little crooked, its face looking over the toad's eyes.
    hx, hy, base = 0.15, yc - 0.45, zc + h / 2 - 0.05
    m.loft_z("Trim", (base, hx, hy, 1.9, 1.45), (base + 1.75, hx + 0.22, hy, 1.7, 1.3))
    fy = hy + 0.68  # its face
    fx = hx + 0.15
    m.block("TrimDark", fx, fy + 0.06, base + 1.42, 1.5, 0.16, 0.2)  # brow
    for side in (-1, 1):
        m.block("TrimDark", fx + side * 0.36, fy + 0.04, base + 1.2, 0.42, 0.1, 0.22)
        m.block("Jade", fx + side * 0.36, fy + 0.09, base + 1.2, 0.3, 0.06, 0.08)
    m.loft_y("TrimDark", (fy, fx, base + 0.98, 0.28, 0.42), (fy + 0.2, fx, base + 0.92, 0.32, 0.22))  # nose
    m.block("TrimDark", fx, fy + 0.04, base + 0.62, 0.7, 0.1, 0.12)  # a stern mouth
    m.block("Trim", hx + 0.25, hy, base + 1.92, 1.4, 1.15, 0.36)  # crown tiers and a jade gem
    m.block("TrimDark", hx + 0.27, hy, base + 2.2, 1.0, 0.85, 0.24)
    gem(m, "Jade", hx + 0.3, fy - 0.12, base + 2.05, 0.18, 0.24, 0.24, 4, math.pi / 4)
    for side in (-1, 1):  # earplugs
        m.block("TrimDark", hx + side * 0.95, hy + 0.1, base + 1.0, 0.16, 0.45, 0.45)
    m.head_centre = (0, front, zc + 0.6)
    return m


def mossy_mo():
    """A big, slow, shaggy sloth that's been asleep in the temple so long a ruin has settled on its back: a
    stone slab, a broken column, a little tree with a glowing pod and a gold idol it hasn't noticed. One eye is
    shut, the other barely open, and when it roars it just yawns."""
    m = monster("dino_MossyMo", Body="#8d7b5a", Accent="#5e503a", Belly="#d6c596", Claw="#2c2620", Stone=STONE,
                StoneDark=STONE_DARK, Moss=MOSS, Leaf=LEAF, LeafDark=LEAF_DARK, Bark=BARK, Pod="#b9ff5c")
    rng = random.Random(2)
    m.joint("Spine", (0, 0, 1.9))
    quad_legs(m, 1.15, 1.3, 1.15, -1.25, 1.55, 0.8)
    for end, y in (("Front", 1.3), ("Back", -1.25)):  # long hooked claws
        for side in (-1, 1):
            m.bone = end + ("L" if side < 0 else "R")
            for off in (-0.28, 0.0, 0.28):
                x = side * 1.15 + off
                beam(m, "Claw", (x, y + 0.45, 0.32), (x, y + 0.95, 0.12), 0.13, None, 0.05)
    m.bone = "Spine"
    body = ((-1.9, 0, 2.0, 2.5, 1.6), (1.7, 0, 2.1, 2.6, 1.75))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-1.5, 0, 1.25, 2.0, 0.3), (1.5, 0, 1.3, 2.2, 0.35))
    for side in (-1, 1):  # a shaggy fringe hanging off its sides
        for k in range(8):
            y = -1.7 + k * 0.46
            r = ring_at(*body, y)
            length = rng.uniform(0.4, 0.75)
            m.block("Accent", side * (r[3] / 2 + 0.04), y, r[2] - r[4] / 2 + 0.2 - length / 2, 0.16, 0.42, length)
    m.block("Body", 0, -2.05, 1.95, 0.8, 0.5, 0.7)  # a stub of a tail
    # The ruin on its back.
    top = top_of(body, -0.2)
    m.block("Stone", 0, -0.2, top + 0.12, 2.2, 2.6, 0.26)
    m.block("StoneDark", 0, -0.2, top - 0.02, 2.35, 2.75, 0.06)
    prism(m, "Stone", -0.55, -0.75, top + 0.2, top + 2.0, 0.36, 0.33, 8, math.pi / 8)
    prism(m, "StoneDark", -0.55, -0.75, top + 0.75, top + 0.9, 0.39, 0.39, 8, math.pi / 8)
    for k in range(3):
        a = k * math.tau / 3 + 0.4
        m.block("Stone", -0.55 + math.cos(a) * 0.17, -0.75 + math.sin(a) * 0.17, top + 2.1 + 0.12 * k, 0.3, 0.3, 0.3 + 0.18 * k)
    m.block("Moss", -0.55, -0.75, top + 2.38, 0.55, 0.5, 0.08)
    m.block("Moss", -0.3, -0.75, top + 1.6, 0.1, 0.4, 0.7)
    prism(m, "Bark", 0.45, 0.25, top + 0.2, top + 2.3, 0.22, 0.15, 6)
    m.block("Leaf", 0.45, 0.25, top + 2.5, 2.0, 1.8, 0.45)
    m.block("LeafDark", 0.55, 0.15, top + 2.9, 1.3, 1.2, 0.4)
    m.block("Leaf", 0.4, 0.3, top + 3.2, 0.7, 0.65, 0.3)
    for px, py, length in ((-0.15, 0.85, 0.45), (1.2, -0.25, 0.3)):
        m.block("Bark", px, py, top + 2.27 - length / 2, 0.06, 0.06, length)
        ball(m, "Pod", px, py, top + 2.27 - length - 0.16, 0.17, 6, 4)
    for k in range(5):  # ferns round the slab
        a = k * math.tau / 5 + 0.3
        bx, by = math.cos(a) * 0.7, -0.2 + math.sin(a) * 0.9
        beam(m, "Leaf" if k % 2 else "LeafDark", (bx, by, top + 0.25), (bx + math.cos(a) * 0.7, by + math.sin(a) * 0.7, top + 0.75), 0.32, 0.06, 0.1)
    m.block("Trim", 0.75, -1.1, top + 0.45, 0.32, 0.32, 0.42)  # the idol it hasn't noticed
    m.block("Trim", 0.75, -1.1, top + 0.72, 0.24, 0.24, 0.14)
    m.block("Jade", 0.75, -0.93, top + 0.5, 0.18, 0.04, 0.06)
    for x, y in ((-0.9, 0.6), (0.9, -0.3), (-0.7, -1.3)):
        m.block("Moss", x, y, top + 0.28, 0.6, 0.5, 0.08)
        m.block("Moss", x + 0.25 * (1 if x > 0 else -1), y, top + 0.05, 0.08, 0.5, 0.5)

    m.use("Neck", (0, 1.6, 2.0))
    m.loft_y("Body", (1.5, 0, 2.05, 1.5, 1.25), (2.2, 0, 1.95, 1.25, 1.1))
    m.stretch("Body", "Spine")
    w, d, h = 1.85, 1.45, 1.5
    yc, zc = 2.75, 2.05
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    m.block("Belly", 0, front + 0.02, zc - 0.05, w * 0.86, 0.06, h * 0.78)  # its pale face
    for side in (-1, 1):  # dark patches round the eyes, running back like a sloth's
        m.block("Accent", side * 0.45, front + 0.06, zc + 0.12, 0.72, 0.06, 0.6)
        m.loft_y("Accent", (front - 0.9, side * (w / 2 + 0.01), zc + 0.2, 0.04, 0.2), (front - 0.05, side * (w / 2 + 0.01), zc + 0.12, 0.04, 0.42))
    classic_mouth(m, front, zc - 0.45, w, 0.38, 1.0, 0.3, 0.26, 0.05, upper="Belly", lower="Belly", tongue=True, grin=0.08, skull_d=d)
    m.block("Mouth", 0, front + 0.36, zc - 0.12, 0.42, 0.14, 0.22)  # a little dark nose
    eclipse_eye(m, (-0.45, front + 0.09, zc + 0.12), "y", 0.46, 1, white=True, look=(0.15, -0.35), lid=0.58, slant=-0.4, lash=True)
    eclipse_eye(m, (0.45, front + 0.09, zc + 0.12), "y", 0.46, -1, white=True, lid=1.0, slant=-0.3, lash=True)  # shut
    m.block("Moss", 0, yc - 0.1, zc + h / 2 + 0.05, w * 0.7, d * 0.7, 0.1)  # moss on its head, and a sprout
    beam(m, "Bark", (0.1, yc, zc + h / 2 + 0.08), (0.15, yc + 0.05, zc + h / 2 + 0.55), 0.06)
    for s in (-1, 1):
        beam(m, "Leaf", (0.15, yc + 0.05, zc + h / 2 + 0.55), (0.15 + s * 0.35, yc + 0.1, zc + h / 2 + 0.68), 0.22, 0.05, 0.08)
    m.head_centre = (0, front, zc)
    return m


def lantern_larry():
    """A lanky temple monkey up to no good: knuckles on the ground, a lantern held out in front, a gold mask
    pushed up on its head like goggles, a sneaky grin with one gold tooth, eyes sliding sideways, one brow up."""
    m = monster("dino_LanternLarry", Body="#4c5a3a", Accent="#2d3624", Belly="#dcbc8c", Claw="#2a2620", Lamp="#ffcf6a",
                Lantern="#7c4a28")
    m.joint("Spine", (0, -0.1, 2.3))
    biped_legs(m, 0.52, -0.1, 2.1, 0.55, 0.95, 0.38, 0.95, 0.25)
    m.loft_z("Body", (1.9, 0, -0.1, 1.3, 1.0), (3.5, 0, 0.25, 1.65, 1.15))
    m.loft_z("Belly", (2.05, 0, 0.42, 0.85, 0.1), (3.3, 0, 0.8, 1.0, 0.1))
    m.block("Body", 0, 0.2, 3.55, 1.9, 1.05, 0.4)  # shoulders
    for side in (-1, 1):
        arm = "ArmL" if side < 0 else "ArmR"
        sx = side * 0.95
        m.use(arm, (sx, 0.2, 3.4))
        beam(m, "Body", (sx, 0.2, 3.45), (side * 1.25, 0.45, 2.25), 0.46, None, 0.38)
        m.block("Body", side * 1.25, 0.45, 2.25, 0.4, 0.4, 0.4)
        if side < 0:  # knuckles on the ground
            beam(m, "Body", (side * 1.25, 0.45, 2.25), (side * 1.35, 0.75, 0.75), 0.38, None, 0.34)
            m.block("Belly", side * 1.35, 0.8, 0.55, 0.5, 0.55, 0.45)
            for off in (-0.15, 0.0, 0.15):
                m.block("Claw", side * 1.35 + off, 1.08, 0.38, 0.1, 0.12, 0.12)
        else:  # holding a lantern out in front
            beam(m, "Body", (side * 1.25, 0.45, 2.25), (side * 1.2, 1.3, 2.65), 0.38, None, 0.34)
            hx, hy, hz = side * 1.2, 1.45, 2.65
            m.block("Belly", hx, hy, hz, 0.45, 0.45, 0.42)
            m.block("Lantern", hx, hy + 0.1, hz - 0.45, 0.06, 0.06, 0.5)
            m.loft_z("Lantern", (hz - 0.95, hx, hy + 0.1, 0.62, 0.62), (hz - 0.72, hx, hy + 0.1, 0.22, 0.22))
            for dx, dy in ((-0.22, -0.22), (0.22, -0.22), (0.22, 0.22), (-0.22, 0.22)):
                m.block("Lantern", hx + dx, hy + 0.1 + dy, hz - 1.3, 0.07, 0.07, 0.62)
            m.block("Lantern", hx, hy + 0.1, hz - 1.64, 0.55, 0.55, 0.1)
            m.block("Lamp", hx, hy + 0.1, hz - 1.3, 0.38, 0.38, 0.56)
    m.bone = "Spine"
    tail(m, (-0.5, 2.4, 0.28, 0.28), (-1.5, 3.7, 0.13, 0.13), 3)
    m.bone = "Tail3"
    for p, q in (((0, -1.5, 3.7), (0, -1.68, 4.1)), ((0, -1.68, 4.1), (0, -1.45, 4.38)), ((0, -1.45, 4.38), (0, -1.25, 4.15)),
                 ((0, -1.25, 4.15), (0, -1.4, 3.98))):
        beam(m, "Body", p, q, 0.12)
    m.bone = "Spine"
    for k in range(5):  # a string of stolen gold coins round its neck
        a = math.pi * (0.15 + 0.7 * k / 4)
        m.block("Trim", math.cos(a) * 0.6, 0.35 + math.sin(a) * 0.45, 3.35 - math.sin(a) * 0.2, 0.2, 0.06, 0.2)

    m.use("Neck", (0, 0.35, 3.6))
    m.block("Body", 0, 0.45, 3.75, 0.6, 0.55, 0.5)
    m.stretch("Body", "Spine")
    w, d, h = 1.35, 1.15, 1.2
    yc, zc = 0.75, 4.35
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    m.block("Belly", 0, front + 0.02, zc - 0.12, w * 0.84, 0.06, h * 0.72)  # its pale face
    for side in (-1, 1):  # big round ears
        round_slab(m, "Body", (side * (w / 2 + 0.06), yc - 0.05, zc + 0.15), "+x" if side > 0 else "-x", 0.42, 0.12, 10)
        round_slab(m, "Belly", (side * (w / 2 + 0.13), yc - 0.05, zc + 0.15), "+x" if side > 0 else "-x", 0.27, 0.04, 10)
    classic_mouth(m, front, zc - 0.36, w, 0.4, 1.0, 0.26, 0.24, 0.1, upper="Belly", lower="Belly", tooth=0.11, per_side=3,
                  grin=0.26, skull_d=d, gold=(1, 1))
    m.block("Accent", 0, front + 0.4, zc - 0.06, 0.32, 0.12, 0.14)  # nose
    eclipse_eye(m, (-0.3, front + 0.06, zc + 0.16), "y", 0.4, 1, white=True, look=(0.85, 0.0), brow=0.2, slant=-0.5)
    eclipse_eye(m, (0.3, front + 0.06, zc + 0.16), "y", 0.4, -1, white=True, look=(0.85, 0.0), lid=0.3, brow=0.05, slant=0.5)
    # The gold mask pushed up on its head, its jade eye slits staring at the sky.
    a, b = (0, front - 0.05, zc + 0.55), (0, front - 0.6, zc + 1.0)
    beam(m, "Trim", a, b, 1.2, 0.1, 1.05)
    along = (Vector(b) - Vector(a)).normalized()
    up = Vector((1, 0, 0)).cross(along)
    for side in (-1, 1):
        p = Vector(a) + along * 0.4 + up * 0.07 + Vector((side * 0.27, 0, 0))
        m.block("Jade", p.x, p.y, p.z, 0.28, 0.08, 0.08)
    m.block("Body", 0, front - 0.45, zc + h / 2 + 0.05, 1.2, 0.18, 0.12)  # its strap
    m.head_centre = (0, front, zc)
    return m


# ---------------------------------------------------------------------- the rare ones


def jade_jaguar():
    """The temple's guardian cat: an obsidian coat with glowing jade rosettes, a gold mask over black eclipse eyes
    with jade rings, slanted down in a glare, a gold collar with a jade pendant, gold bands, and its fangs bared."""
    m = monster("dino_JadeJaguar", Body="#2a2633", Accent="#16141c", Belly="#4c4658", Claw="#e6dcc0")
    m.joint("Spine", (0, 0, 2.0))
    quad_legs(m, 0.62, 1.4, 0.62, -1.45, 1.8, 0.52)
    for side in (-1, 1):  # gold bands on the forelegs
        m.bone = "FrontL" if side < 0 else "FrontR"
        m.block("Trim", side * 0.62, 1.4, 1.0, 0.58, 0.62, 0.16)
        m.block("Jade", side * 0.62, 1.73, 1.0, 0.18, 0.04, 0.1)
    m.bone = "Spine"
    body = ((-1.95, 0, 2.15, 1.25, 1.1), (1.5, 0, 2.3, 1.45, 1.35))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-1.5, 0, 1.62, 0.95, 0.2), (1.3, 0, 1.68, 1.15, 0.25))
    for side in (-1, 1):
        for y, share in ((1.05, 0.35), (0.45, -0.15), (-0.15, 0.45), (-0.75, 0.0), (-1.35, 0.4), (0.75, 0.75), (-0.45, 0.8),
                         (-1.65, -0.1)):
            rosette(m, flank(body, y, share, side, 0.02), "+x" if side > 0 else "-x", 0.13)
    for x, y in ((0.25, 0.9), (-0.3, 0.2), (0.2, -0.6), (-0.25, -1.3)):
        rosette(m, (x, y, top_of(body, y) + 0.02), "z", 0.12)
    tail(m, (-1.9, 2.35, 0.36, 0.34), (-4.3, 3.25, 0.15, 0.15), 3)
    for i, t in ((1, 0.2), (2, 0.55), (3, 0.85)):
        m.bone = f"Tail{i}"
        y = -1.9 - 2.4 * t
        z = 2.35 + 0.9 * t
        s = 0.36 - 0.21 * t
        m.block("Jade" if i < 3 else "Trim", 0, y, z, s + 0.05, 0.1, s + 0.05)
    m.bone = "Spine"

    m.use("Neck", (0, 1.25, 2.4))
    m.loft_y("Body", (1.2, 0, 2.45, 1.15, 1.05), (2.0, 0, 2.75, 0.95, 0.92))
    m.stretch("Body", "Spine")
    m.block("Trim", 0, 1.62, 2.6, 1.2, 0.3, 1.14)  # the collar and its jade pendant
    m.block("Trim", 0, 1.8, 2.0, 0.36, 0.1, 0.44)
    gem(m, "Jade", 0, 1.86, 1.98, 0.13, 0.17, 0.17, 4, math.pi / 4)
    w, d, h = 1.3, 1.25, 1.05
    yc, zc = 2.45, 2.95
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = classic_mouth(m, front, zc - 0.3, w, 0.55, 0.85, 0.3, 0.24, 0.12, tooth=0.14, per_side=3, lower_teeth=True,
                          tongue=True, skull_d=d)
    for side in (-1, 1):  # long fangs
        y = snout["tip"] - 0.12
        m.loft_z("Teeth", (zc - 0.3 - 0.36, side * 0.3, y, 0.03, 0.03), (zc - 0.3 + 0.1, side * 0.3, y, 0.15, 0.15))
    m.block("Accent", 0, snout["tip"] - 0.1, snout["top"](snout["tip"] - 0.1) + 0.02, 0.36, 0.18, 0.1)  # nose
    # The gold mask over the upper face, swept back at the sides, with the eyes in it.
    m.block("Trim", 0, front + 0.04, zc + 0.2, 1.38, 0.08, 0.6)
    for side in (-1, 1):
        beam(m, "Trim", (side * 0.66, front + 0.02, zc + 0.3), (side * 0.85, front - 0.65, zc + 0.75), 0.3, 0.1, 0.12)
        eclipse_eye(m, (side * 0.32, front + 0.08, zc + 0.16), "y", 0.36, -side, white=False, lid=0.32, slant=0.9, brow=-0.02,
                    lid_role="Trim", brow_role="TrimDark")
        beam(m, "Jade", (side * (w / 2 + 0.01), front - 0.15, zc - 0.05), (side * (w / 2 + 0.01), front - 0.7, zc - 0.25), 0.05, 0.07)
        beam(m, "Jade", (side * (w / 2 + 0.01), front - 0.1, zc - 0.25), (side * (w / 2 + 0.01), front - 0.55, zc - 0.45), 0.05, 0.07)
        prism(m, "Body", side * 0.42, yc - 0.3, zc + h / 2 - 0.05, zc + h / 2 + 0.5, 0.26, 0.03, 3, side * 0.5, (side * 0.06, -0.08))
        m.block("Trim", side * 0.55, yc - 0.3, zc + h / 2 - 0.02, 0.12, 0.3, 0.2)
    gem(m, "Jade", 0, front + 0.1, zc + 0.56, 0.12, 0.18, 0.18, 4, math.pi / 4)
    m.head_centre = (0, front + 0.3, zc)
    return grow(m, 1.35)


def plumed_wyrm():
    """A feathered serpent-dragon: a long emerald body on short legs, a golden belly, feathered wings raised off
    its back, a long serpent tail ending in a fan of plumes, and a toothy snout framed by a huge crest and ruff of
    green, gold and red feathers. Black eclipse eyes on the sides of its head, glaring under heavy brows."""
    m = monster("dino_PlumedWyrm", Body="#2e8a5a", Accent="#1b5a3a", Belly="#e8c35e", Claw="#efe7cc", Plume="#3cc47c",
                PlumeTip="#e8452c", PlumeGold=GOLD)
    m.joint("Spine", (0, 0, 1.9))
    quad_legs(m, 0.72, 1.3, 0.72, -1.3, 1.45, 0.48)
    body = ((-2.2, 0, 1.95, 1.35, 1.2), (1.55, 0, 2.05, 1.5, 1.35))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-2.0, 0, 1.38, 1.05, 0.2), (1.45, 0, 1.42, 1.2, 0.25))
    for y in (-1.8, -1.2, -0.6, 0.0, 0.6, 1.2):  # dark bands across its back, with a gold feather spike each
        z = top_of(body, y)
        m.block("Accent", 0, y, z + 0.02, ring_at(*body, y)[3] * 0.92, 0.22, 0.06)
        feather(m, (0, y, z), (0, y - 0.35, z + 0.6), 0.2, (0, 1, 0), "PlumeGold", "PlumeTip", 0.35)
    tail(m, (-2.15, 1.95, 1.05, 0.95), (-6.2, 1.0, 0.18, 0.18), 3)
    m.bone = "Tail3"
    for dx in (-0.5, -0.25, 0.0, 0.25, 0.5):  # the fan of plumes at its end
        feather(m, (0, -5.9, 1.08), (dx * 2.0, -7.3, 1.35 + (0.5 - abs(dx)) * 0.6), 0.32, (1, 0, 0))
    m.bone = "Spine"
    for side in (-1, 1):  # feathered wings, half spread
        s = "L" if side < 0 else "R"
        m.use("Wing" + s, (side * 0.65, 0.9, 2.55))
        root, elbow = Vector((side * 0.65, 0.9, 2.55)), Vector((side * 1.7, 0.3, 3.9))
        beam(m, "Accent", tuple(root), tuple(elbow), 0.3, None, 0.24)
        for k in range(4):
            p = root + (elbow - root) * (0.15 + 0.25 * k)
            feather(m, tuple(p), tuple(p + Vector((side * 0.15, -0.9 - 0.15 * k, -1.2 - 0.1 * k))), 0.42, tuple(elbow - root))
        m.use("WingTip" + s, tuple(elbow), "Wing" + s)
        tip = Vector((side * 3.0, -0.7, 4.2))
        beam(m, "Accent", tuple(elbow), tuple(tip), 0.24, None, 0.12)
        for k in range(4):
            p = elbow + (tip - elbow) * (0.1 + 0.28 * k)
            feather(m, tuple(p), tuple(p + Vector((side * 0.35, -1.3 - 0.2 * k, -1.1 + 0.15 * k))), 0.46, tuple(tip - elbow))
    m.bone = "Spine"

    m.use("Neck", (0, 1.35, 2.15))
    beam(m, "Body", (0, 1.3, 2.1), (0, 2.0, 2.95), 0.9, None, 0.78)
    m.stretch("Body", "Spine")
    m.block("Body", 0, 2.0, 2.95, 0.78, 0.78, 0.78)
    beam(m, "Body", (0, 2.0, 2.95), (0, 2.55, 3.55), 0.78, None, 0.7)
    beam(m, "Belly", (0, 1.62, 2.25), (0, 2.38, 3.05), 0.6, 0.6, 0.5)
    w, d, h = 0.98, 1.15, 0.88
    yc, zc = 2.85, 3.75
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    snout = classic_mouth(m, front, zc - 0.22, w, 1.15, 0.64, 0.3, 0.22, 0.12, tooth=0.11, per_side=5, lower_teeth=True,
                          tongue=True, skull_d=d)
    top_nostrils(m, snout, 0.18, 0.1)
    for side in (-1, 1):
        eclipse_eye(m, (side * (w / 2), yc + 0.2, zc + 0.14), "+x" if side > 0 else "-x", 0.44, 1, white=False, lid=0.3, slant=0.8,
                    brow=0.0, brow_role="Accent")
        prism(m, "Trim", side * 0.3, yc - 0.2, zc + h / 2 - 0.05, zc + h / 2 + 0.45, 0.12, 0.02, 4, 0, (side * 0.12, -0.25))
        m.block("Trim", side * (w / 2 + 0.03), yc - 0.25, zc - 0.15, 0.06, 0.4, 0.4)  # gold cheek plates with jade
        m.block("Jade", side * (w / 2 + 0.07), yc - 0.25, zc - 0.15, 0.04, 0.16, 0.16)
    # The crest, sweeping back, and a ruff of plumes round the back of the head.
    m.block("Trim", 0, yc - 0.15, zc + h / 2 + 0.06, 0.7, 0.5, 0.14)
    gem(m, "Jade", 0, yc + 0.12, zc + h / 2 + 0.12, 0.1, 0.15, 0.12, 4, math.pi / 4)
    for dx, rise, length in ((-0.24, 1.3, 2.0), (0.0, 1.75, 2.3), (0.24, 1.3, 2.0), (-0.42, 0.9, 1.6), (0.42, 0.9, 1.6)):
        base = (dx, yc - 0.1, zc + h / 2 + 0.05)
        feather(m, base, (dx * 2.2, yc - length, zc + h / 2 + rise), 0.3, (1, 0, 0), "Plume", "PlumeTip")
    for k in range(9):
        a = math.pi * (k / 8)  # from one side round over the top to the other
        u, v = math.cos(a), math.sin(a)
        base = (u * 0.42, yc - 0.45, zc + v * 0.38)
        tipp = (u * 1.5, yc - 0.85, zc + v * 1.25 - 0.1)
        feather(m, base, tipp, 0.36, (-v, 0, u), "PlumeGold" if k % 2 else "Plume", "PlumeTip")
    m.head_centre = (0, front + 0.35, zc)
    return grow(m, 1.3)


def eclipse_devourer():
    """The boss: a towering four-armed god-beast of obsidian with jade fire in its cracks, that swallowed the sun.
    A black sun with a burning corona stands behind its head; the eaten sun still glows in its chest; its raised
    upper hands each hold a little black sun. A gold mask with a glare, black eclipse eyes and a third eye on its
    brow, great horns, gold-capped fangs, and jade fire deep in its throat."""
    m = monster("dino_EclipseDevourer", Body="#24212d", Accent="#3b2b40", Belly="#d9cfb3", Claw="#ece3c8", Void="#07060b",
                EclipseRing="#fff3cf", Corona="#ffd36b")
    m.joint("Spine", (0, 0, 4.6))
    biped_legs(m, 1.0, 0.0, 4.3, 1.4, 1.9, 1.0, 1.7, 0.45)
    for side in (-1, 1):  # jade cracks down the thighs, gold greaves
        m.bone = "LegL" if side < 0 else "LegR"
        x = side * (1.0 + 0.72)
        for p, q in (((x, 0.0, 4.3), (x + side * 0.02, 0.2, 3.6)), ((x + side * 0.02, 0.2, 3.6), (x, -0.1, 2.9))):
            beam(m, "Jade", p, q, 0.06, 0.12)
        m.bone = "ShinL" if side < 0 else "ShinR"
        m.block("Trim", side * 1.0, 0.0, 1.55, 1.2, 1.25, 0.3)
    m.bone = "Spine"
    m.loft_z("Body", (3.9, 0, 0.0, 3.0, 2.0), (8.3, 0, 0.15, 4.8, 2.7))
    m.loft_z("Accent", (2.2, 0, 1.02, 1.5, 0.12), (4.1, 0, 1.02, 1.3, 0.12))  # loincloth
    m.block("Trim", 0, 0, 4.05, 3.15, 2.15, 0.4)  # belt
    m.block("Jade", 0, 1.1, 4.05, 0.4, 0.06, 0.25)
    # The sun it swallowed, still glowing in its chest, with jade cracks spreading from it.
    sun_disc(m, (0, 1.36, 6.6), 0.78, 10, 0.55)
    for a in (0.5, 1.4, 2.5, 3.6, 4.6, 5.6):
        p = (math.cos(a) * 1.25, 1.33, 6.6 + math.sin(a) * 1.15)
        q = (math.cos(a + 0.2) * 1.85, 1.3, 6.6 + math.sin(a + 0.2) * 1.65)
        beam(m, "Jade", p, q, 0.08, 0.06)
    for side in (-1, 1):  # gold pauldrons with jade, and spikes
        m.block("Trim", side * 2.35, 0.0, 8.3, 1.4, 2.2, 0.6)
        m.block("TrimDark", side * 2.35, 0.0, 7.95, 1.45, 2.25, 0.14)
        gem(m, "Jade", side * 2.35, 1.12, 8.3, 0.18, 0.25, 0.25, 4, math.pi / 4)
        for dy in (-0.6, 0.3):
            prism(m, "Accent", side * 2.6, dy, 8.55, 9.4, 0.22, 0.03, 4, math.pi / 4, (side * 0.3, -0.15))
    # Lower arms, hanging heavy, clawed.
    for side in (-1, 1):
        sx = side * 2.55
        m.use("ArmL" if side < 0 else "ArmR", (sx, 0.0, 7.7))
        beam(m, "Body", (sx, 0.0, 7.8), (side * 2.9, 0.5, 5.6), 1.0, None, 0.9)
        m.block("Body", side * 2.9, 0.5, 5.6, 0.9, 0.9, 0.9)
        beam(m, "Body", (side * 2.9, 0.5, 5.6), (side * 3.0, 1.0, 3.9), 0.9, None, 0.85)
        m.block("Trim", side * 3.0, 0.95, 4.2, 1.0, 1.0, 0.3)
        beam(m, "Jade", (side * 3.42, 0.55, 5.4), (side * 3.45, 0.85, 4.5), 0.06, 0.1)
        hand = (side * 3.05, 1.15, 3.4)
        m.block("Body", *hand, 0.95, 1.0, 0.85)
        for off in (-0.3, 0.0, 0.3):
            m.loft_y("Claw", (hand[1] + 0.45, hand[0] + off, hand[2] - 0.15, 0.22, 0.24), (hand[1] + 0.95, hand[0] + off, hand[2] - 0.55, 0.04, 0.04))
    # Upper arms on the Wing bones, raised, each holding a little black sun.
    for side in (-1, 1):
        s = "L" if side < 0 else "R"
        m.use("Wing" + s, (side * 2.2, -0.3, 8.3))
        beam(m, "Body", (side * 2.2, -0.3, 8.3), (side * 3.5, -0.2, 9.4), 0.8, None, 0.72)
        m.block("Body", side * 3.5, -0.2, 9.4, 0.72, 0.72, 0.72)
        beam(m, "Body", (side * 3.5, -0.2, 9.4), (side * 3.9, 0.1, 10.7), 0.72, None, 0.66)
        m.block("Trim", side * 3.85, 0.05, 10.4, 0.8, 0.8, 0.24)
        m.block("Body", side * 3.95, 0.15, 11.0, 0.75, 0.75, 0.6)
        for off in (-0.25, 0.25):
            beam(m, "Claw", (side * 3.95 + off, 0.15, 11.3), (side * 3.95 + off * 1.4, 0.2, 11.75), 0.16, None, 0.04)
        sun_disc(m, (side * 3.95, 0.15, 12.25), 0.42, 8, 0.6)
    m.bone = "Spine"
    tail(m, (-0.9, 4.6, 1.3, 1.1), (-4.6, 2.2, 0.3, 0.3), 3)
    for bone, y, z, height in (("Tail1", -1.6, 4.65, 0.55), ("Tail2", -2.8, 3.9, 0.45), ("Tail3", -3.9, 3.0, 0.35)):
        m.bone = bone
        gem(m, "Jade", 0, y, z + height * 0.6, 0.14, height, 0.1, 4, math.pi / 4)
    m.bone = "Spine"

    m.use("Neck", (0, 0.1, 8.3))
    m.loft_z("Body", (8.1, 0, 0.1, 1.9, 1.7), (8.85, 0, 0.25, 1.8, 1.6))
    m.stretch("Body", "Spine")
    w, d, h = 2.1, 1.9, 1.7
    yc, zc = 0.55, 9.55
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2

    def throat_fire(m, front, mouth_z, gap, lower_length):
        m.block("Jade", 0, front + 0.15, mouth_z - gap / 2 + 0.05, 0.9, 0.2, 0.12)

    m.block("Belly", 0, yc, zc, w, d, h)  # a pale skull of a head, so it stands out against the black sun
    snout = classic_mouth(m, front, zc - 0.5, w, 0.8, 1.65, 0.45, 0.4, 0.22, upper="Belly", lower="Belly", tooth=0.22, per_side=4,
                          lower_teeth=True, tongue=False, skull_d=d, on_jaw=throat_fire)
    m.block("Jade", 0, front + 0.12, zc - 0.5, 1.0, 0.12, 0.18)  # jade fire at the back of the mouth
    for side in (-1, 1):  # gold-capped fangs
        y = snout["tip"] - 0.2
        m.loft_z("Teeth", (zc - 0.5 - 0.55, side * 0.55, y, 0.04, 0.04), (zc - 0.5 + 0.05, side * 0.55, y, 0.24, 0.24))
        m.block("Trim", side * 0.55, y, zc - 0.5 + 0.02, 0.27, 0.27, 0.12)
    m.block("Body", 0, snout["tip"] - 0.15, snout["top"](snout["tip"] - 0.15) + 0.03, 0.6, 0.25, 0.14)  # nose holes
    for side in (-1, 1):  # dark cracks across the skull's cheeks
        beam(m, "Body", (side * (w / 2 + 0.01), front - 0.2, zc - 0.1), (side * (w / 2 + 0.01), front - 0.9, zc + 0.3), 0.05, 0.1)
    # The gold mask, two black eclipse eyes glaring, and the third eye on its brow.
    m.block("Trim", 0, front + 0.04, zc + 0.25, w * 0.98, 0.08, 0.75)
    for side in (-1, 1):
        eclipse_eye(m, (side * 0.48, front + 0.08, zc + 0.15), "y", 0.5, -side, white=False, lid=0.34, slant=1.0, brow=-0.02,
                    lid_role="Trim", brow_role="TrimDark")
        beam(m, "Trim", (side * 1.0, front + 0.02, zc + 0.35), (side * 1.3, front - 0.8, zc + 0.85), 0.36, 0.12, 0.14)
    m.block("Trim", 0, front + 0.04, zc + 0.78, 0.6, 0.08, 0.55)
    eclipse_eye(m, (0, front + 0.1, zc + 0.8), "y", 0.42, 1, white=False)
    # Great horns.
    for side in (-1, 1):
        pts = [(side * 0.8, yc - 0.2, zc + 0.75), (side * 1.6, yc - 0.45, zc + 1.25), (side * 2.05, yc - 0.3, zc + 2.15),
               (side * 1.9, yc + 0.15, zc + 2.85)]
        for (p, q), (w0, w1) in zip(zip(pts, pts[1:]), ((0.6, 0.45), (0.45, 0.28), (0.28, 0.12))):
            beam(m, "Accent", p, q, w0, None, w1)
            m.block("Accent", *q, w1, w1, w1)
        m.block("Trim", *pts[1], 0.52, 0.52, 0.2)
        gem(m, "Trim", *pts[3], 0.08, 0.3, 0.05)
    # The black sun behind its head.
    sun_disc(m, (0, yc - 1.25, zc + 0.75), 1.85, 16, 0.75)
    m.head_centre = (0, front + 0.45, zc)
    return m


# ---------------------------------------------------------------------- previews


def quick_preview(models, out):
    """Stills only, for trying faces: each model whole, its face up close, and the lineup."""
    scene = kit.setup_scene()
    kit.RENDERS = out
    out.mkdir(parents=True, exist_ok=True)
    kit.NO_STUDS.update(GLOW_ROLES)
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


ALL = [idol_ollie, mossy_mo, lantern_larry, jade_jaguar, plumed_wyrm, eclipse_devourer]


def main():
    builders = ALL
    only = os.environ.get("ONLY")
    if only:
        builders = [b for b in builders if b.__name__ in only.split(",")]
    models = [b() for b in builders]
    if os.environ.get("QUICK"):
        quick_preview(models, Path(os.environ.get("QUICK_OUT", str(RENDERS / "quick"))))
        return
    build_and_render(models, RENDERS, HERE / f"{BLEND}.blend", "eclipse_temple_animation_preview.mp4", sky=SKY, ground=FLOOR,
                     glow_roles=GLOW_ROLES, spacing=16, glow=GLOW)


if __name__ == "__main__":
    main()
