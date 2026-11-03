"""Builds the Shadow Bog's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_shadow_bog.py

Saves shadow_bog_models.blend and renders to design/world/models_shadow_bog/, with a stretch of corridor.

Shadow Bog, map 6, is a tar pit at dusk: the world of Sticky Steve, Tar Titan and Bog Rex. It has to read
differently from the Swamp's green and the Volcano's orange from the flight camera, so it is slate violet and
black: pools and falls of glossy black tar, crooked black trees with hanging grey moss, bone-white skeletons
of huge things that sank in the tar, and glowing violet will-o'-wisps for the colour. Landmarks on the rims
(a giant long-necked skeleton rising out of the tar), tar oozing down the corridor walls, an arch of giant
twisted roots over it, flat tar pits across the floor.

Glowing parts (Glow, Wisp) get the Neon material in the game (shared/Roles.luau). Props that must face a
certain way (TarFall, RootArch) carry a small Front part that MapDecor uses to turn them, then removes.
1 Blender unit = 1 stud, props stand on Z = 0 at their origin.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_desert import beam  # noqa: E402
from build_forest import Model  # noqa: E402
from build_swamp import place_copy, strand  # noqa: E402
from build_volcano import hide_markers, prism, set_sky, set_visible  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "models_shadow_bog"

GLOW_ROLES = {"Glow", "Wisp"}
kit.NO_STUDS.update(GLOW_ROLES)

# Shared colours, so every prop's tar, wood and bone match.
TAR, TAR_SHINE, TAR_GLOSS = "#28213a", "#4a3e62", "#9284bf"  # gloss: the violet sky caught in the wet tar
BARK, BARK_DARK = "#4a3e52", "#30283a"
BONE, BONE_SHADE = "#ece4d0", "#c8bca0"
GLOW, WISP = "#a865ff", "#f6e2ff"
MUD = "#3b3344"
MOSS = "#8a9b7c"
ROCK, ROCK_DARK = "#5d5670", "#46405a"

# The corridor's Shadow Bog colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#6a5a8e", "FloorB": "#5e4f80", "Dirt": "#45364f", "DirtB": "#3d3047", "Grass": "#4d7d68"}
SKY = "#8d80b6"


def prop(name, **colours):
    return Model(f"prop_{name}", colours)


def limb(m, role, points, w0, w1, joints=True):
    """A crooked branch or root through points, tapering from w0 to w1, with the bends filled."""
    count = len(points) - 1
    for i, (a, b) in enumerate(zip(points, points[1:])):
        wa = w0 + (w1 - w0) * i / count
        wb = w0 + (w1 - w0) * (i + 1) / count
        beam(m, role, a, b, wa, None, wb)
        if joints and i < count - 1:
            m.block(role, *b, wb * 0.95, wb * 0.95, wb * 0.95)


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def puddle(m, role, blobs, z=0.08, thick=0.16):
    """A flat, uneven pool made of overlapping slabs: (x, y, width, depth) each."""
    for x, y, w, d in blobs:
        m.block(role, x, y, z, w, d, thick)


def bubble_ring(m, role, x, y, z, r, thick=0.05):
    """A flat ring where a bubble just popped: four thin bars round a square."""
    for dx, dy, w, d in ((0, r, 2 * r, 0.22), (0, -r, 2 * r, 0.22), (r, 0, 0.22, 2 * r), (-r, 0, 0.22, 2 * r)):
        m.block(role, x + dx, y + dy, z, w, d, thick)


def dome(m, role, x, y, z, r):
    """A chunky bubble or blob: three stacked lofts, wide at the middle."""
    m.loft_z(role, (z, x, y, r * 1.5, r * 1.5), (z + r * 0.55, x, y, r * 2, r * 2))
    m.loft_z(role, (z + r * 0.55, x, y, r * 2, r * 2), (z + r * 1.25, x, y, r * 1.45, r * 1.45))
    m.loft_z(role, (z + r * 1.25, x, y, r * 1.45, r * 1.45), (z + r * 1.6, x, y, r * 0.6, r * 0.6))


def mud_rim(m, rng, rx, ry, count, size=(0.9, 1.6), role="Mud"):
    for i in range(count):
        a = i * math.tau / count + rng.uniform(-0.15, 0.15)
        s = rng.uniform(*size)
        m.block(role, math.cos(a) * rx, math.sin(a) * ry, s * 0.18, s, s * rng.uniform(0.8, 1.2), s * 0.36)


def moss_beard(m, x, y, top, length, width, role="Moss"):
    """A beard of moss hanging off a branch, tapering to a point."""
    m.loft_z(role, (top - length * 0.55, x, y, width * 0.75, width * 0.75), (top, x, y, width, width))
    m.loft_z(role, (top - length, x, y, 0.1, 0.1), (top - length * 0.55, x, y, width * 0.75, width * 0.75))


def hanging_pod(m, x, y, top, length):
    """A glowing pod dangling on a thin stalk, like a lantern the bog grew."""
    m.block("BarkDark", x, y, top - length / 2, 0.16, 0.16, length)
    m.loft_z("Glow", (top - length - 0.5, x, y, 0.5, 0.5), (top - length + 0.05, x, y, 0.85, 0.85))
    m.loft_z("Glow", (top - length - 1.15, x, y, 0.3, 0.3), (top - length - 0.5, x, y, 0.5, 0.5))


# ---------------------------------------------------------------------- props


def gloom_tree(seed=3):
    """The map's signature tree: a crooked black trunk splitting into bent branches, grey moss hanging off
    them and a few glowing pods dangling like lanterns."""
    m = prop("GloomTree", Bark=BARK, BarkDark=BARK_DARK, Moss=MOSS, Glow=GLOW, Tar=TAR)
    rng = random.Random(seed)
    puddle(m, "Tar", ((0, 0, 6.6, 5.4), (1.3, -1.0, 4.2, 5.2), (-1.6, 1.2, 3.6, 3.6)))
    for k in range(5):
        a = k * math.tau / 5 + rng.uniform(-0.3, 0.3)
        reach = rng.uniform(2.8, 3.8)
        limb(m, "BarkDark", [(math.cos(a) * 0.6, math.sin(a) * 0.6, 1.8), (math.cos(a) * 1.9, math.sin(a) * 1.9, 0.6),
                             (math.cos(a) * reach, math.sin(a) * reach, 0.15)], 1.1, 0.35)
    trunk = [(0, 0, 0), (0.7, 0.3, 3.0), (-0.5, 0.5, 5.8), (0.6, -0.3, 8.4), (0.1, 0, 10.6)]
    limb(m, "Bark", trunk, 2.5, 1.15)
    m.block("BarkDark", 0.45, 1.05, 3.6, 0.9, 0.3, 1.6)  # a knot hole
    branches = [  # start on the trunk, then the bends
        ((-0.5, 0.5, 5.8), [(-2.8, 1.2, 7.4), (-5.0, 0.6, 7.6), (-6.4, 1.2, 6.6)]),
        ((0.6, -0.3, 8.4), [(2.8, -1.4, 9.8), (5.0, -1.0, 10.0), (6.2, -2.0, 9.0)]),
        ((0.1, 0, 10.6), [(-1.4, -1.8, 12.4), (-2.2, -3.6, 12.8), (-3.4, -4.4, 12.0)]),
        ((0.1, 0, 10.6), [(1.2, 1.8, 12.6), (2.6, 3.2, 13.6), (2.8, 4.6, 13.0)]),
        ((0.7, 0.3, 3.0), [(2.6, 1.6, 4.6), (4.0, 2.8, 5.0)]),
    ]
    for start, bends in branches:
        points = [start] + bends
        limb(m, "Bark", points, 1.0, 0.35)
        tip = Vector(bends[-1])
        before = Vector(bends[-2]) if len(bends) > 1 else Vector(start)
        out = (tip - before).normalized()
        for turn in (-0.7, 0.7):  # a twiggy fork at the end
            d = Vector((out.x * math.cos(turn) - out.y * math.sin(turn), out.x * math.sin(turn) + out.y * math.cos(turn), 0.8))
            beam(m, "BarkDark", tuple(tip), tuple(tip + d.normalized() * 1.5), 0.32, None, 0.08)
        for a, b in zip(points, points[1:]):  # beards of moss hanging off the branches
            for k in range(3):
                if rng.random() < 0.7:
                    at = Vector(a).lerp(Vector(b), 0.2 + 0.3 * k)
                    moss_beard(m, at.x + rng.uniform(-0.3, 0.3), at.y + rng.uniform(-0.3, 0.3), at.z - 0.15,
                               rng.uniform(1.4, 3.4), rng.uniform(0.45, 0.7))
    for x, y, top, length in ((-6.0, 1.0, 6.9, 1.6), (5.8, -1.8, 9.3, 2.0), (2.7, 4.2, 13.1, 1.4)):
        hanging_pod(m, x, y, top, length)
    return m


def tar_pit(seed=5):
    """A pool of glossy black tar with popped bubbles and an old bone in it. Flat (under half a stud), so
    it can lie in the middle of the floor where the eggs land."""
    m = prop("TarPit", Tar=TAR, TarShine=TAR_SHINE, TarGloss=TAR_GLOSS, Mud=MUD, Bone=BONE)
    rng = random.Random(seed)
    puddle(m, "Tar", ((0, 0, 14, 8.5), (2, 2.4, 9, 7), (-3.2, -1.6, 7.5, 6.5), (4.6, -2.0, 6, 5)))
    for i in range(20):
        a = i * math.tau / 20
        s = rng.uniform(1.0, 1.7)
        m.block("Mud", math.cos(a) * 7.0, math.sin(a) * 5.0 + 0.4, 0.12, s, s, 0.24)
    for x, y, w in ((-3.6, 1.6, 3.2), (2.0, -1.4, 2.6), (4.4, 2.6, 1.8)):
        m.block("TarShine", x, y, 0.18, w, 0.3, 0.04)
        m.block("TarGloss", x - w * 0.3, y, 0.2, w * 0.3, 0.3, 0.04)
    for x, y, r in ((-1.0, -2.4, 0.8), (3.4, 0.6, 0.55), (-4.8, -0.6, 0.45)):
        bubble_ring(m, "TarShine", x, y, 0.19, r)
        m.block("TarGloss", x, y, 0.19, 0.3, 0.3, 0.05)
    m.block("Bone", 1.2, 3.2, 0.24, 3.2, 0.55, 0.3)  # a bone lying in the tar
    for dx in (-1.7, 1.7):
        for dy in (-0.3, 0.3):
            m.block("Bone", 1.2 + dx, 3.2 + dy, 0.26, 0.6, 0.55, 0.34)
    return m


def tar_bubbles(seed=6):
    """A mound of tar heaving with fat bubbles, one of them popping."""
    m = prop("TarBubbles", Tar=TAR, TarShine=TAR_SHINE, TarGloss=TAR_GLOSS, Mud=MUD)
    rng = random.Random(seed)
    puddle(m, "Tar", ((0, 0, 8.4, 7.0), (1.2, 1.4, 5, 5)))
    mud_rim(m, rng, 4.2, 3.6, 12)
    m.loft_z("Tar", (0, 0, 0, 7, 6), (1.0, 0.2, 0, 5.6, 4.6))
    m.loft_z("Tar", (1.0, 0.2, 0, 5.6, 4.6), (1.6, 0.3, 0.1, 3.6, 3.0))
    for x, y, z, r in ((0.4, 0.2, 1.2, 1.3), (-1.9, 0.9, 0.8, 0.8), (1.9, -1.0, 0.8, 0.9), (-0.6, -1.8, 0.7, 0.55)):
        dome(m, "Tar", x, y, z, r)
        m.block("TarGloss", x - r * 0.35, y - r * 0.55, z + r * 1.05, r * 0.5, r * 0.25, r * 0.35)
        m.block("TarShine", x + r * 0.2, y - r * 0.7, z + r * 0.7, r * 0.8, r * 0.2, r * 0.3)
    # The popping one: a crown of splashes and drops flying up.
    px, py, pz = 1.5, 1.6, 1.0
    bubble_ring(m, "TarShine", px, py, pz + 0.05, 0.8, 0.15)
    for i in range(6):
        a = i * math.tau / 6 + 0.3
        h = rng.uniform(0.6, 1.1)
        beam(m, "Tar", (px + math.cos(a) * 0.7, py + math.sin(a) * 0.7, pz), (px + math.cos(a) * 1.1, py + math.sin(a) * 1.1, pz + h), 0.4, None, 0.15)
    for dx, dy, dz, s in ((0.3, 0.2, 2.6, 0.4), (-0.4, 0.5, 3.3, 0.3), (0.5, -0.4, 3.9, 0.22)):
        m.block("Tar", px + dx, py + dy, pz + dz, s, s, s)
    return m


def wisps(seed=7):
    """Will-o'-wisps: little violet flames with sleepy faces, floating over a tuft of dead reeds. Bright, so
    they read from far away."""
    m = prop("Wisps", Glow=GLOW, Wisp=WISP, Mud=MUD, Reed="#7a7085", ReedDark="#564d61", Socket="#2a1640")
    rng = random.Random(seed)
    m.loft_z("Mud", (0, 0, 0, 4.4, 3.6), (0.5, 0, 0, 3.2, 2.6))
    for k in range(11):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0.2, 1.3)
        x, y = math.cos(a) * r, math.sin(a) * r
        lean = rng.uniform(0.3, 1.2)
        beam(m, "Reed" if k % 2 else "ReedDark", (x, y, 0.3), (x + math.cos(a) * lean, y + math.sin(a) * lean, rng.uniform(1.6, 3.2)), 0.22, None, 0.06)
    for x, y, z, s, lean in ((0.2, 0.1, 5.6, 1.0, 0.35), (2.4, 1.3, 4.0, 0.72, -0.3), (-2.0, 1.6, 7.4, 0.62, 0.4),
                             (1.2, -1.9, 8.6, 0.5, -0.25)):
        # A teardrop flame: round at the bottom, licking up to a point that leans a little.
        m.loft_z("Glow", (z - s * 0.8, x, y, s * 0.9, s * 0.9), (z - s * 0.2, x, y, s * 1.6, s * 1.6))
        m.loft_z("Glow", (z - s * 0.2, x, y, s * 1.6, s * 1.6), (z + s * 0.6, x + lean * s * 0.3, y, s * 1.3, s * 1.3))
        m.loft_z("Glow", (z + s * 0.6, x + lean * s * 0.3, y, s * 1.3, s * 1.3), (z + s * 1.4, x + lean * s * 0.9, y, s * 0.6, s * 0.6))
        m.loft_z("Glow", (z + s * 1.4, x + lean * s * 0.9, y, s * 0.6, s * 0.6), (z + s * 2.1, x + lean * s * 1.7, y, 0.05, 0.05))
        m.block("Wisp", x, y, z - s * 0.1, s * 0.95, s * 1.62, s * 0.55)  # the white-hot heart, a face on each side
        for side in (-1, 1):  # sleepy eyes on the -Y face
            m.block("Socket", x + side * s * 0.22, y - s * 0.82, z - s * 0.02, s * 0.2, s * 0.04, s * 0.13)
        for k, (dz, t) in enumerate(((1.15, 0.45), (1.7, 0.32), (2.2, 0.2))):  # a trail of sparks below
            m.block("Glow", x - lean * s * 0.6 * (k + 1), y + s * 0.15 * k, z - s * dz, s * t, s * t, s * t)
    return m


def sunken_skeleton(seed=8):
    """A landmark for the rims: the skeleton of a huge long-necked monster that sank in the tar, its neck
    arching out of the pool and its skull hanging down, two violet lights deep in its eye sockets. A few rib
    tips and the end of its tail poke out of the tar too."""
    m = prop("SunkenSkeleton", Bone=BONE, BoneShade=BONE_SHADE, Socket="#151119", Glow=GLOW,
             Tar=TAR, TarShine=TAR_SHINE, TarGloss=TAR_GLOSS, Mud=MUD)
    rng = random.Random(seed)
    puddle(m, "Tar", ((0, 0, 24, 14), (-3, 3, 14, 12), (5, -3, 12, 10), (-8, -2, 8, 8)), z=0.15, thick=0.3)
    for i in range(26):
        a = i * math.tau / 26
        s = rng.uniform(1.4, 2.4)
        m.block("Mud", math.cos(a) * 12.0, math.sin(a) * 7.6, s * 0.2, s, s, s * 0.4)
    for x, y, r in ((3, 4, 0.9), (-5, -3.5, 0.7), (8, 1.5, 0.6)):
        bubble_ring(m, "TarShine", x, y, 0.34, r)
    for x, y, w in ((-6, 3.8, 4), (6, -4.5, 3), (1, 5.4, 2.4)):
        m.block("TarGloss", x, y, 0.33, w, 0.4, 0.05)

    # The neck: vertebrae along a curve, each with a fin on its outer side.
    p0, p1, p2, p3 = (-7.0, 0, -0.5), (-8.5, 0, 17), (2.5, 0, 27), (7.5, 0, 18.5)
    steps = 16
    points = [Vector(bezier(p0, p1, p2, p3, i / steps)) for i in range(steps + 1)]
    for i, p in enumerate(points[:-1]):
        w = 2.8 - 1.3 * i / steps
        q = points[i + 1]
        beam(m, "BoneShade", tuple(p), tuple(q), w * 0.55)
        m.block("Bone", p.x, p.y, p.z, w, w * 1.05, w)
        along = (q - p).normalized()
        outward = Vector((-along.z, 0, along.x))
        if outward.z < 0:
            outward = -outward
        beam(m, "Bone", tuple(p + outward * w * 0.4), tuple(p + outward * w * 1.15), w * 0.45, w * 0.3, w * 0.15)
        for side in (-1, 1):  # little side knobs
            m.block("BoneShade", p.x, p.y + side * w * 0.62, p.z, w * 0.45, w * 0.35, w * 0.45)

    # The skull, hanging down and looking along +X.
    hx, hy, hz = 8.6, 0, 17.0
    m.block("Bone", hx, hy, hz, 4.4, 3.6, 3.2)  # cranium
    m.block("BoneShade", hx - 0.6, hy, hz + 1.75, 3.2, 2.8, 0.5)
    m.loft_x("Bone", (hx + 2.2, hy, hz - 0.4, 3.0, 2.2), (hx + 5.4, hy, hz - 0.9, 2.2, 1.5))  # snout
    m.loft_x("BoneShade", (hx + 1.6, hy, hz - 2.2, 2.6, 0.7), (hx + 5.0, hy, hz - 2.9, 1.9, 0.5))  # jaw, hanging open
    m.block("BoneShade", hx + 0.6, hy, hz - 1.6, 1.6, 2.6, 1.6)  # jaw hinge
    for side in (-1, 1):
        m.block("Socket", hx + 0.6, hy + side * 1.78, hz + 0.3, 1.5, 0.1, 1.3)
        m.block("Glow", hx + 0.75, hy + side * 1.84, hz + 0.25, 0.5, 0.1, 0.5)
        m.block("Socket", hx + 5.0, hy + side * 0.8, hz - 0.35, 0.5, 0.5, 0.3)  # nostril holes, on top of the snout
        for k in range(4):
            tx = hx + 2.6 + k * 0.75
            m.block("Bone", tx, hy + side * (1.1 - k * 0.08), hz - 1.75 - k * 0.12, 0.3, 0.3, 0.75)  # upper teeth
            m.block("Bone", tx + 0.3, hy + side * (0.95 - k * 0.08), hz - 2.2 - k * 0.15, 0.28, 0.28, 0.6)  # lower teeth

    # Rib tips and a tail curling out of the tar.
    for x in (-2.5, 0.0, 2.5):
        for side in (-1, 1):
            h = rng.uniform(3.2, 4.6)
            limb(m, "Bone", [(x, side * 4.2, 0), (x + 0.3, side * 4.4, h * 0.55), (x + 0.5, side * 3.4, h)], 0.85, 0.4)
    tail = [(9.5, -4.0, 0), (10.6, -4.4, 1.6), (11.4, -4.2, 3.0), (11.2, -3.2, 4.0), (10.4, -2.7, 4.2)]
    for i, p in enumerate(tail):
        s = 1.1 - i * 0.16
        m.block("Bone", *p, s, s, s)
        if i < len(tail) - 1:
            beam(m, "BoneShade", p, tail[i + 1], s * 0.5)
    return m


def thorn_bush(seed=9):
    """A dark bramble bristling with pale thorns, with a few magenta berries."""
    m = prop("ThornBush", Bramble="#3c3047", BrambleLight="#54456a", Thorn="#a8979f", Berry="#d93a7e")
    rng = random.Random(seed)
    clumps = [(0, 0, 1.3, 3.8, 3.2, 2.6, "Bramble"), (1.5, 0.8, 1.9, 2.4, 2.2, 2.0, "BrambleLight"),
              (-1.4, -0.6, 1.6, 2.4, 2.4, 2.0, "Bramble"), (0.2, -0.2, 3.0, 2.2, 2.0, 1.4, "BrambleLight"),
              (-0.4, 1.4, 1.0, 2.0, 1.6, 1.6, "BrambleLight")]
    for x, y, z, w, d, h, role in clumps:
        m.block(role, x, y, z, w, d, h)
    for i in range(26):
        x, y, z, w, d, h, _ = clumps[i % len(clumps)]
        a = rng.uniform(0, math.tau)
        lift = rng.uniform(-0.3, 0.7)
        start = Vector((x + math.cos(a) * w * 0.45, y + math.sin(a) * d * 0.45, z + lift * h * 0.5))
        out = Vector((math.cos(a), math.sin(a), lift * 0.8)).normalized()
        beam(m, "Thorn", tuple(start), tuple(start + out * rng.uniform(0.6, 1.0)), 0.26, None, 0.03)
    for i in range(7):
        x, y, z, w, d, h, _ = clumps[(i * 2) % len(clumps)]
        a = rng.uniform(0, math.tau)
        m.block("Berry", x + math.cos(a) * w * 0.52, y + math.sin(a) * d * 0.52, z + rng.uniform(-0.2, 0.6), 0.42, 0.42, 0.42)
    for k in range(3):  # a few long stems curling out
        a = k * math.tau / 3 + 0.5
        limb(m, "Bramble", [(math.cos(a) * 1.2, math.sin(a) * 1.2, 2.2), (math.cos(a) * 2.6, math.sin(a) * 2.6, 3.2),
                            (math.cos(a) * 3.0, math.sin(a) * 3.0, 4.2)], 0.4, 0.18)
    return m


def jaw(m, hinge, angle, length, width, thick, inner_role="Maw", outer_role="Leaf", teeth=4):
    """One half of a snapping plant's head: an outer leaf, its coloured inside and teeth along its edges.
    angle: radians up from +X (negative opens downward)."""
    h = Vector(hinge)
    along = Vector((math.cos(angle), 0, math.sin(angle)))
    inward = Vector((math.sin(angle), 0, -math.cos(angle))) * (1 if angle > 0 else -1)
    tip = h + along * length
    beam(m, outer_role, tuple(h), tuple(tip), width, thick, width * 0.7)
    beam(m, inner_role, tuple(h + inward * thick * 0.5), tuple(tip + inward * thick * 0.5), width * 0.82, thick * 0.4, width * 0.56)
    for k in range(teeth):
        t = 0.3 + 0.65 * k / max(teeth - 1, 1)
        w = width * (1 - 0.3 * t)
        for side in (-1, 1):
            base = h + along * length * t + Vector((0, side * w * 0.45, 0)) + inward * thick * 0.5
            beam(m, "Teeth", tuple(base), tuple(base + inward * 0.75), 0.3, None, 0.04)
    base = tip + inward * thick * 0.5
    beam(m, "Teeth", tuple(base), tuple(base + inward * 0.6 + along * 0.2), 0.32, None, 0.04)


def bog_snapper(seed=10):
    """A carnivorous bog plant: a tall stalk with a big snapping head wide open, magenta inside and ringed
    with teeth, and two closed buds on shorter stalks."""
    m = prop("BogSnapper", Leaf="#3f6c5a", LeafDark="#2f5446", Maw="#df4a95", Teeth="#f3ecd8", Mud=MUD)
    rng = random.Random(seed)
    m.loft_z("Mud", (0, 0, 0, 4.0, 3.6), (0.4, 0, 0, 3.0, 2.6))
    for k in range(7):
        a = k * math.tau / 7 + rng.uniform(-0.2, 0.2)
        limb(m, "LeafDark" if k % 2 else "Leaf", [(0, 0, 0.4), (math.cos(a) * 1.8, math.sin(a) * 1.8, 0.5),
                                                  (math.cos(a) * 3.0, math.sin(a) * 3.0, 1.1)], 0.9, 0.25, joints=False)
    stalk = [(0, 0, 0.3), (0.5, 0.1, 2.4), (0.1, 0, 4.4), (-0.5, 0, 6.0)]
    limb(m, "Leaf", stalk, 0.95, 0.65)
    head = Vector((-0.6, 0, 6.4))
    m.block("LeafDark", *head, 1.4, 1.6, 1.4)
    jaw(m, head, math.radians(38), 3.6, 3.0, 0.7)
    jaw(m, head, math.radians(-14), 3.4, 2.8, 0.7)
    beam(m, "Maw", tuple(head + Vector((0.4, 0, 0))), tuple(head + Vector((2.6, 0.3, -0.5))), 0.7, 0.25, 0.35)  # a tongue
    for side, height, lean in ((-1, 3.2, 0.9), (1, 2.4, 1.1)):
        top = Vector((-0.4 + lean * 0.3, side * (1.4 + lean), height))
        limb(m, "LeafDark", [(0, side * 0.4, 0.3), (0, side * 1.0, height * 0.6), tuple(top)], 0.5, 0.35)
        m.loft_z("Leaf", (top.z, top.x, top.y, 0.9, 0.9), (top.z + 0.7, top.x, top.y, 1.3, 1.1))
        m.loft_z("Leaf", (top.z + 0.7, top.x, top.y, 1.3, 1.1), (top.z + 1.6, top.x, top.y, 0.35, 0.3))
        m.block("Maw", top.x, top.y, top.z + 0.95, 1.36, 0.14, 0.6)  # the closed lips
    return m


def hollow_stump(seed=11):
    """A huge rotten stump with a jagged broken top, shelf fungus on its side and two eyes glowing in the
    dark of its hollow: something lives in there."""
    m = prop("HollowStump", Bark=BARK, BarkDark=BARK_DARK, Hollow="#120e16", Glow=GLOW, Moss=MOSS,
             Fungus="#d9c8a6", FungusDark="#b39e78", Tar=TAR)
    rng = random.Random(seed)
    puddle(m, "Tar", ((0, 1.0, 9, 8.5), (2.5, -1.5, 5, 5)))
    prism(m, "Bark", 0, 0, 0, 6.2, 4.6, 4.0, 8, math.pi / 8)
    m.block("Hollow", 0, 0, 6.15, 4.4, 4.4, 0.2)  # rotten out at the top
    for i in range(8):  # splintered top edge
        a = math.pi / 8 + i * math.tau / 8
        h = rng.uniform(0.6, 3.0)
        r = 3.75
        prism(m, "Bark" if i % 2 else "BarkDark", math.cos(a) * r, math.sin(a) * r, 6.0, 6.0 + h, 1.25, 0.15, 4,
              a, (rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3)))
    for k in range(7):  # roots
        a = k * math.tau / 7 + 0.4
        limb(m, "BarkDark", [(math.cos(a) * 3.6, math.sin(a) * 3.6, 1.8), (math.cos(a) * 5.0, math.sin(a) * 5.0, 0.7),
                             (math.cos(a) * 6.0, math.sin(a) * 6.0, 0.15)], 1.6, 0.5)
    for k in range(5):  # bark grooves
        a = k * math.tau / 5 + 1.0
        m.block("BarkDark", math.cos(a) * 4.35, math.sin(a) * 4.35, 3.2, 0.5, 0.5, rng.uniform(3, 4.8))
    # The hollow, on the +Y side, with a frame of torn bark and two eyes in the dark.
    m.block("Hollow", 0, 4.05, 2.5, 3.0, 0.7, 3.6)
    m.loft_z("Hollow", (4.3, 0, 4.05, 3.0, 0.7), (5.0, 0, 4.05, 1.6, 0.7))
    m.block("BarkDark", -1.75, 4.15, 2.6, 0.6, 0.6, 4.0)
    m.block("BarkDark", 1.75, 4.15, 2.4, 0.6, 0.6, 3.6)
    m.block("BarkDark", 0, 4.2, 0.45, 3.8, 0.6, 0.9)
    for side in (-1, 1):
        m.block("Glow", side * 0.65, 4.42, 3.05, 0.75, 0.1, 0.45)
        m.block("Hollow", side * 0.65 + side * 0.15, 4.45, 3.32, 0.7, 0.1, 0.2)  # a heavy lid, so they glare
    # Shelf fungus and moss.
    for a, z, w in ((2.4, 3.6, 2.2), (2.4, 2.6, 1.6), (3.4, 4.6, 1.8), (-0.9, 3.0, 2.0), (-1.2, 1.9, 1.4)):
        x, y = math.cos(a) * 4.4, math.sin(a) * 4.4
        m.block("Fungus", x, y, z, w, w, 0.35)
        m.block("FungusDark", x, y, z - 0.25, w * 0.8, w * 0.8, 0.15)
    for x, y, w, d in ((1.4, -1.6, 2.6, 2.0), (-2.0, 0.8, 1.8, 2.4)):
        m.block("Moss", x, y, 6.25, w, d, 0.2)
    for k in range(5):
        a = rng.uniform(math.pi * 0.9, math.pi * 1.9)
        strand(m, "Moss", math.cos(a) * 4.45, math.sin(a) * 4.45, 6.4, rng.uniform(1.2, 2.8), 0.5)
    return m


def gloom_rock(seed=12):
    """Crooked shards of dark slate leaning out of a tar puddle, pale lichen on their tops and tar oozing down
    the biggest one, with an old bone at their foot."""
    m = prop("GloomRock", Rock=ROCK, RockDark=ROCK_DARK, Tar=TAR, TarGloss=TAR_GLOSS, Lichen="#a9b896", Bone=BONE, Mud=MUD)
    rng = random.Random(seed)
    puddle(m, "Tar", ((0.4, 0.2, 8.0, 6.4), (2.8, -1.8, 4.4, 3.8), (-2.6, 1.6, 3.6, 3.6)))
    mud_rim(m, rng, 4.4, 3.6, 10, (0.8, 1.3))
    shards = [(0, 0, 7.2, 1.7, 1.2, (0.6, 0.3), "Rock"), (2.0, 1.0, 4.6, 1.2, 0.8, (1.2, 0.6), "RockDark"),
              (-1.8, 0.8, 5.4, 1.3, 0.9, (-1.1, 0.4), "Rock"), (0.8, -1.8, 3.4, 1.1, 0.8, (0.5, -1.0), "RockDark"),
              (-1.2, -1.4, 2.2, 0.9, 0.7, (-0.4, -0.6), "Rock")]
    for i, (x, y, height, r0, r1, (lx, ly), role) in enumerate(shards):
        turn = math.pi / 4 if i == 0 else rng.uniform(0, 1)  # the big one square to the axes, so its tar sits on a face
        prism(m, role, x, y, 0, height, r0, r1, 4, turn, (lx, ly))
        prism(m, role, x + lx, y + ly, height, height + r1 * 0.9, r1, 0.08, 4, turn, (lx * 0.1, ly * 0.1))  # a broken point
        if height > 3:
            m.block("Lichen", x + lx * 0.7 + r1 * 0.3, y + ly * 0.7, height * 0.72, r1 * 1.1, r1 * 1.1, 0.5)
    for z_top, length, dx in ((5.6, 3.6, 0.2), (4.2, 3.0, -0.5)):  # tar running down the big shard
        t = z_top / 7.2
        x, y = 0.6 * t + dx, 0.3 * t - (1.7 + (1.2 - 1.7) * t) * 0.7 - 0.1
        m.block("Tar", x, y, z_top - length / 2, 0.55, 0.5, length)
        m.loft_z("Tar", (z_top - length - 0.7, x, y - 0.05, 0.3, 0.3), (z_top - length, x, y - 0.05, 0.8, 0.7))
    for x, y, w in ((-2.2, -1.0, 2.0), (2.6, 2.0, 1.6)):
        m.block("TarGloss", x, y, 0.18, w, 0.35, 0.05)
    beam(m, "Bone", (2.4, -2.8, 0.35), (4.4, -1.4, 0.55), 0.5)
    for p in ((2.4, -2.8, 0.35), (4.4, -1.4, 0.55)):
        m.block("Bone", *p, 0.85, 0.85, 0.7)
    return m


def shadow_reeds(seed=13):
    """A clump of tall dead reeds, grey-violet with dark seed heads; small filler for the floor."""
    m = prop("ShadowReeds", Reed="#7a7085", ReedDark="#564d61", Head="#2b2433", Mud=MUD)
    rng = random.Random(seed)
    m.loft_z("Mud", (0, 0, 0, 3.6, 3.0), (0.4, 0, 0, 2.6, 2.2))
    for k in range(14):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0.1, 1.2)
        x, y = math.cos(a) * r, math.sin(a) * r
        h = rng.uniform(3.0, 6.0)
        lean = rng.uniform(0.2, 1.4)
        top = (x + math.cos(a) * lean, y + math.sin(a) * lean, h)
        beam(m, "Reed" if k % 3 else "ReedDark", (x, y, 0.3), top, 0.26, None, 0.14)
        if k % 2 == 0:
            m.loft_z("Head", (h - 0.2, top[0], top[1], 0.42, 0.42), (h + 1.0, top[0], top[1], 0.42, 0.42))
            m.block("ReedDark", top[0], top[1], h + 1.3, 0.12, 0.12, 0.6)
        if k % 4 == 1:  # a broken one, folded over
            fold = (top[0] + math.cos(a) * 1.4, top[1] + math.sin(a) * 1.4, h - 1.6)
            beam(m, "ReedDark", top, fold, 0.2, None, 0.08)
    return m


def root_arch(seed=14):
    """An arch of giant roots braided round each other over the corridor, rim to rim, with moss on top,
    dead shoots sticking up, and moss, vines and glowing pods hanging under it. It spans X; its feet spread
    out on the rims beyond 36 studs from the middle, and all of it stays above the rim's height (z 0),
    clear of the flight camera."""
    m = prop("RootArch", Bark=BARK, BarkDark=BARK_DARK, BarkLight="#5e4f68", Moss=MOSS, Vine="#5d6e58", Glow=GLOW,
             Front="#ff00ff")
    rng = random.Random(seed)
    span = 54

    def centre(x):
        return 10 + 9 * (1 - (x / 58) ** 2)  # the braid's middle line

    def thick(x, at_feet, at_top):
        t = min(abs(x) / span, 1)
        return at_top + (at_feet - at_top) * t * t

    def strand_at(x, phase, radius):
        a = x / 7 + phase
        return Vector((x, radius * math.sin(a), centre(x) + radius * math.cos(a)))

    roots = (("Bark", 0, 2.4, 6.0, 4.2), ("BarkDark", math.tau / 3, 2.4, 5.0, 3.4), ("BarkLight", 2 * math.tau / 3, 2.4, 4.4, 2.8))
    lowest = {}
    for role, phase, radius, feet, top in roots:
        xs = [x * 0.5 for x in range(-span * 2, span * 2 + 1, 5)]
        points = [strand_at(x, phase, radius) for x in xs]
        for a, b in zip(points, points[1:]):
            wa, wb = thick(a.x, feet, top), thick(b.x, feet, top)
            beam(m, role, tuple(a), tuple(b), wa, None, wb)
            m.block(role, *b, wb * 0.92, wb * 0.92, wb * 0.92)
            low = b.z - wb / 2
            key = round(b.x)
            lowest[key] = min(lowest.get(key, 99), low)
        for k in range(4):  # knots
            x = rng.uniform(-40, 40)
            p = strand_at(x, phase, radius)
            w = thick(x, feet, top)
            m.block(role, p.x, p.y + rng.choice((-1, 1)) * w * 0.3, p.z + w * 0.3, w * 0.7, w * 0.7, w * 0.6)

    def underside(x):
        near = [v for k, v in lowest.items() if abs(k - x) <= 3]
        return min(near) if near else centre(x) - 5

    def top_at(x):
        return centre(x) + 2.4 + thick(x, 6.0, 4.2) / 2

    for side in (-1, 1):  # feet: roots plunging into the rim and spreading out
        foot = Vector((side * span, 0, centre(span)))
        for k in range(6):
            a = (k - 2.5) * 0.5
            end = Vector((side * (span + 4 + 6 * math.cos(a)), 10 * math.sin(a), 0.2))
            mid = foot.lerp(end, 0.5) + Vector((0, 0, 2.0))
            limb(m, ("Bark", "BarkDark", "BarkLight")[k % 3], [tuple(foot), tuple(mid), tuple(end)], 3.6, 1.0)
        m.loft_z("BarkDark", (0, side * (span + 2), 0, 10, 9), (3.5, side * (span + 1), 0, 6, 5.5))
        m.block("Moss", side * (span + 4), 0, 0.3, 14, 12, 0.6)
    for x in range(-44, 45, 5):  # moss along the top, with beards hanging over its sides
        z = top_at(x)
        y = rng.uniform(-1, 1)
        m.block("Moss", x + rng.uniform(-1, 1), y, z, rng.uniform(3, 4.5), rng.uniform(3.2, 4.4), 0.7)
        for face in (-1, 1):
            if rng.random() < 0.55:
                moss_beard(m, x + rng.uniform(-1.5, 1.5), y + face * 2.6, z - 0.4, rng.uniform(2.5, 5.0), rng.uniform(0.6, 0.9))
    for x, lean in ((-30, -1), (-12, 1), (8, -1), (26, 1), (40, -1)):  # dead shoots sticking up, forking
        base = Vector((x, rng.uniform(-1, 1), top_at(x) - 0.4))
        bend = base + Vector((lean * 1.6, rng.uniform(-1, 1), rng.uniform(3, 4.5)))
        tip = bend + Vector((lean * 1.8, rng.uniform(-1.2, 1.2), rng.uniform(1.6, 2.6)))
        limb(m, "BarkDark", [tuple(base), tuple(bend), tuple(tip)], 1.1, 0.4)
        for turn in (-1, 1):
            beam(m, "BarkDark", tuple(tip), tuple(tip + Vector((lean * 0.5, turn * 1.0, 1.2))), 0.35, None, 0.08)
    for k in range(20):  # vines and moss underneath, some with a glowing pod at the end
        x = -36 + k * 3.8 + rng.uniform(-1, 1)
        y = rng.uniform(-2.2, 2.2)
        under = underside(x) + 0.4
        length = rng.uniform(2.5, min(8.0, under - 4.0))
        if k % 2:
            moss_beard(m, x, y, under, length, rng.uniform(0.6, 0.9))
        else:
            strand(m, "Vine", x, y, under, length, rng.uniform(0.3, 0.45))
            if k % 4 == 0:
                hang = under - length
                m.loft_z("Glow", (hang - 0.6, x, y, 0.6, 0.6), (hang + 0.1, x, y, 1.0, 1.0))
                m.loft_z("Glow", (hang - 1.3, x, y, 0.3, 0.3), (hang - 0.6, x, y, 0.6, 0.6))
    m.block("Front", 0, 6, 3, 0.2, 0.2, 0.2)
    return m


def tar_fall(seed=15):
    """Thick black tar oozing off the rim and down the corridor wall in sagging lumps, dripping as it goes,
    with an old skull stuck in it halfway down, into a sticky pool on the floor. Origin on the wall's top
    inner edge: rim z 0, floor z -44, +Y out into the corridor. The Front part tells the game which way it
    faces, then it's removed."""
    m = prop("TarFall", Tar=TAR, TarShine=TAR_SHINE, TarGloss=TAR_GLOSS, Mud=MUD, Bone=BONE, BoneShade=BONE_SHADE,
             Socket="#151119", Front="#ff00ff")
    rng = random.Random(seed)
    m.block("Tar", 0, -7, 0.18, 9, 14, 0.36)  # a sticky stream across the rim
    m.block("Tar", 1.5, -12, 0.18, 6, 5, 0.36)
    for y in (-4, -9):
        dome(m, "Tar", rng.uniform(-2, 2), y, 0.2, 0.7)
    m.block("TarGloss", -1.8, -7.5, 0.4, 0.7, 8, 0.05)
    m.block("TarGloss", 2.2, -4, 0.4, 0.5, 4, 0.05)
    for side in (-1, 1):
        for y, s in ((-12.5, 2.6), (-9, 2.2), (-5.5, 2.6), (-1.6, 2.2)):
            m.block("Mud", side * 5.6, y, s * 0.3, s, s * 1.1, s * 0.6)
    m.block("Tar", 0, 0.9, -0.2, 9.4, 2.2, 1.0)  # bulging over the lip
    m.block("Tar", 0, 2.2, -1.6, 10.0, 2.0, 2.8)
    # The curtain stands clear of the hanging grass (1.5 out): lumps of different widths, each sagging at
    # its foot, with drips hanging off the sags.
    z = -2.8
    while z > -43.5:
        length = min(rng.uniform(4, 7.5), z + 43.5)
        width = rng.uniform(7.2, 9.4)
        x = rng.uniform(-0.5, 0.5)
        m.block("Tar", x, 2.8, z - length / 2, width, 1.8, length)
        if length > 3 and rng.random() < 0.75:
            sag = z - length * 0.78
            m.block("Tar", x + rng.uniform(-0.6, 0.6), 3.5, sag, width + 1.2, 1.6, length * 0.4)
            for k in range(rng.randint(1, 2)):
                dx = rng.choice((-1, 1)) * rng.uniform(1.5, width / 2)
                drop = rng.uniform(1.2, 2.4)
                m.loft_z("Tar", (sag - length * 0.2 - drop, x + dx, 3.6, 0.35, 0.35), (sag - length * 0.2, x + dx, 3.6, 1.1, 1.1))
        z -= length
    for x, z0, z1, w in ((-2.6, -3, -17, 0.6), (1.6, -8, -21, 0.45), (2.8, -27, -41, 0.6), (-1.4, -31, -42, 0.45)):  # wet streaks
        m.block("TarGloss", x, 3.75, (z0 + z1) / 2, w, 0.08, z0 - z1)
    for x, z_end in ((-5.6, -11), (5.4, -17), (-5.2, -26), (5.8, -33)):  # separate drips beside it
        m.block("Tar", x, 2.4, (-1.6 + z_end) / 2, 0.6, 0.8, -1.6 - z_end)
        m.loft_z("Tar", (z_end - 1.2, x, 2.4, 0.4, 0.4), (z_end, x, 2.4, 1.1, 1.2))
    # A skull stuck in the tar halfway down, gazing out of the gloop.
    sx, sy, sz = -0.6, 4.1, -23.5
    m.block("Bone", sx, sy, sz, 3.2, 1.6, 2.6)
    m.block("Bone", sx + 0.1, sy + 0.4, sz - 1.4, 2.0, 1.2, 1.0)  # muzzle
    for side in (-1, 1):
        m.block("Socket", sx + side * 0.75, sy + 0.82, sz + 0.25, 0.9, 0.06, 0.8)
        m.block("BoneShade", sx + side * 0.4, sy + 1.02, sz - 1.75, 0.3, 0.06, 0.35)  # teeth
        beam(m, "Bone", (sx + side * 1.4, sy, sz + 1.0), (sx + side * 2.6, sy + 0.6, sz + 2.4), 0.6, None, 0.15)  # horns
    m.block("Tar", sx, sy + 0.3, sz + 1.5, 3.8, 1.6, 0.9)  # tar pouring over its head
    m.block("Tar", sx - 0.9, sy + 0.9, sz + 0.6, 0.6, 0.4, 1.4)
    # The pool at its foot, against the wall, with bubbles and a bone sticking out.
    puddle(m, "Tar", ((0, 4.6, 15, 8.5), (0, 9.0, 10, 3.6), (-5, 7.2, 5, 6), (5, 7.0, 4.5, 5.5)), z=-43.75, thick=0.5)
    for x, y, s in ((-8.4, 2.8, 1.8), (-8.0, 8.0, 1.6), (-3.6, 11.2, 1.4), (2.4, 11.2, 1.6), (6.8, 8.8, 1.8), (8.4, 3.2, 1.5)):
        m.block("Mud", x, y, -44 + s * 0.3, s, s, s * 0.6)
    for x, y, r in ((-3.0, 6.4, 0.7), (3.0, 5.6, 0.9), (0.2, 8.0, 0.5)):
        dome(m, "Tar", x, y, -43.6, r)
        m.block("TarGloss", x - r * 0.3, y - r * 0.6, -43.6 + r * 1.05, r * 0.5, r * 0.2, r * 0.3)
    bubble_ring(m, "TarShine", -1.0, 9.6, -43.47, 0.7)
    m.block("TarGloss", 4.0, 3.6, -43.47, 3, 0.4, 0.05)
    beam(m, "Bone", (4.6, 8.0, -43.6), (5.8, 9.4, -40.8), 0.55)
    m.block("Bone", 5.8, 9.4, -40.8, 1.0, 1.0, 0.9)
    m.block("Front", 0, 6, -20, 0.2, 0.2, 0.2)
    return m


# ---------------------------------------------------------------------- preview stage


def corridor_stage(stage, length=300, seed=7):
    """A stretch of corridor in Shadow Bog's colours (floor z 0, walls 44 high, inner faces 36 from the middle)."""
    m = Model("ShadowBogCorridor", dict(CORRIDOR))
    m.bone = "Root"
    for ix in range(9):
        for iy in range(length // 8):
            m.block("FloorA" if (ix + iy) % 2 == 0 else "FloorB", -32 + ix * 8, -iy * 8 - 4, -0.5, 8, 8, 1)
    rng = random.Random(seed)
    for side in (-1, 1):
        for iz in range(6):
            for iy in range(length // 8):
                m.block("Dirt" if (iz + iy) % 2 == 0 else "DirtB", side * 72, -iy * 8 - 4, iz * 7 + 3.5, 72, 8, 7)
        m.block("Grass", side * 72, -length / 2, 45, 72, length, 2)
        m.block("Grass", side * 35.25, -length / 2, 42, 1.5, length, 4)
        y = 0
        while y < length:
            drip = rng.choice((0, 4, 4, 8, 8, 12, 16))
            if drip:
                m.block("Grass", side * 35.25, -y - 4, 40 - drip / 2, 1.5, 8, drip)
            y += 8
    return m.build(stage)


# The mix Config/Decor uses for ShadowBog, so the corridor render shows the real thing.
FLOOR = [("prop_GloomTree", 18, (1.3, 1.7)), ("prop_ThornBush", 14, (1.3, 1.7)), ("prop_GloomRock", 12, (1.2, 1.6)),
         ("prop_TarBubbles", 12, (1.2, 1.6)), ("prop_ShadowReeds", 12, (1.2, 1.6)), ("prop_BogSnapper", 10, (1.2, 1.5)),
         ("prop_Wisps", 8, (1.2, 1.5)), ("prop_HollowStump", 6, (1.0, 1.2))]
EXTRAS = [("prop_ShadowReeds", 4, (0.7, 1.0)), ("prop_ThornBush", 3, (0.6, 0.9)), ("prop_GloomRock", 2, (0.5, 0.7))]
RIM = [("prop_GloomTree", 6, (2, 2.6)), ("prop_HollowStump", 2, (1.6, 2)), ("prop_BogSnapper", 2, (2, 2.4)),
       ("prop_ThornBush", 2, (2, 2.6)), ("prop_Wisps", 2, (2, 2.4))]


def decorate_stage(stage, built, length=300, seed=51):
    """The corridor's props laid out like Config/Decor's ShadowBog rules."""
    rng = random.Random(seed)

    def pick(table):
        total = sum(w for _, w, _ in table)
        roll = rng.uniform(0, total)
        for name, weight, scale in table:
            roll -= weight
            if roll <= 0:
                return name, scale
        return table[-1][0], table[-1][2]

    copies = []

    def put(name, location, yaw, scale):
        copy = place_copy(built[name], stage, location, yaw, scale)
        hide_markers([copy])
        copies.append(copy)

    def put_random(table, x, z, y):
        name, (low, high) = pick(table)
        put(name, (x, -y, z), rng.uniform(0, math.tau), rng.uniform(low, high))

    y = 12
    while y < length - 14:
        side = rng.choice((-1, 1))
        x = side * rng.uniform(20, 27)
        put_random(FLOOR, x, 0, y)
        if rng.random() < 0.6:
            put_random(EXTRAS, side * min(max(abs(x) + rng.uniform(-8, 8), 16), 33), 0, y + rng.uniform(-8, 8))
        y += rng.uniform(14, 26)
    y = 8
    while y < length:
        for side in (-1, 1):
            if rng.random() < 0.85:
                put_random(RIM, side * rng.uniform(56, 94), 44, y)
        y += rng.uniform(18, 30)
    put("prop_SunkenSkeleton", (74, -80, 44), math.radians(200), 1.5)
    put("prop_SunkenSkeleton", (-72, -230, 44), math.radians(20), 1.4)
    for y, side in ((50, -1), (175, 1), (270, -1)):
        put("prop_TarFall", (side * 36, -y, 44), side * math.pi / 2, 1)
    put("prop_RootArch", (0, -130, 44), 0, 1)
    for y, x, yaw in ((30, -3, 20), (100, 5, 140), (200, -4, 70), (260, 3, 200)):
        put("prop_TarPit", (x, -y, 0), math.radians(yaw), 1.2)
    return copies


def light_up(roots, strength=2.4):
    """Glowing roles shine in the renders. Undone before saving, so the export stays plain colours."""
    for root in roots:
        for child in root.children:
            if child.type == "MESH" and child.name.rsplit("_", 1)[-1] in GLOW_ROLES:
                for mat in child.data.materials:
                    nodes = mat.node_tree.nodes
                    bsdf = nodes.get("Principled BSDF")
                    bsdf.inputs["Emission Color"].default_value = nodes["Colour"].outputs[0].default_value
                    bsdf.inputs["Emission Strength"].default_value = strength


def dusk(scene):
    """A dimmer, cooler sun for the renders, closer to the game's Shadow Bog light."""
    sun = bpy.data.objects["Sun"]
    sun.data.energy = 2.0
    sun.data.color = (0.86, 0.82, 1.0)
    ambient = scene.world.node_tree.nodes["Background"]
    ambient.inputs["Color"].default_value = (0.8, 0.74, 1.0, 1)
    ambient.inputs["Strength"].default_value = 0.8


# ---------------------------------------------------------------------- scene and renders


def main():
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    props = bpy.data.collections.new("Props")
    stage = bpy.data.collections.new("Preview stage")
    for col in (props, stage):
        scene.collection.children.link(col)

    prop_models = [gloom_tree(), tar_pit(), tar_bubbles(), wisps(), sunken_skeleton(), thorn_bush(), bog_snapper(),
                   hollow_stump(), gloom_rock(), shadow_reeds(), root_arch(), tar_fall()]
    built = {}
    prop_roots = []
    spots = {"prop_SunkenSkeleton": (0, -80, 0), "prop_TarFall": (40, -160, 44), "prop_RootArch": (140, -160, 0)}
    x = 40
    for model in prop_models:
        root = model.build(props)
        if model.name in spots:
            root.location = spots[model.name]
        else:
            root.location = (x, -40, 0)
            x += 22
        built[model.name] = root
        prop_roots.append(root)
    light_up(prop_roots)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-300, -400, -0.01), (400, -400, -0.01), (400, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", CORRIDOR["FloorA"], False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = Model("Player", {"Skin": "#d8d2c4"})
    player.bone = "Root"
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    player_root = player.build(stage)
    bpy.context.view_layer.update()
    set_sky(scene, SKY)
    dusk(scene)

    everything = prop_roots + [player_root]
    for model, root in zip(prop_models, prop_roots):
        low, high = kit.bounds(root)
        player_root.location = Vector((low.x - 3, (low.y + high.y) / 2 + 2, 0))
        bpy.context.view_layer.update()
        set_visible(everything, [root, player_root])
        centre = (low + high) / 2
        reach = max((high - low).length, 7)
        if model.name == "prop_RootArch":
            kit.shoot(scene, model.name, centre + Vector((-25, 125, 10)), centre, (1400, 700), 32)
        elif model.name == "prop_TarFall":
            kit.shoot(scene, model.name, centre + Vector((40, 55, 6)), centre, (700, 900), 40)
        else:
            kit.shoot(scene, model.name, centre + Vector((0.5, 0.9, 0.42)) * reach * 1.25, centre, (600, 600), 50)
    player_root.location = (30, -40, 0)
    bpy.context.view_layer.update()
    set_visible(everything, [r for r in prop_roots if r.name not in ("prop_TarFall", "prop_RootArch", "prop_SunkenSkeleton")] + [player_root])
    kit.shoot(scene, "props", (150, 55, 40), (150, -45, 5), (1800, 700), 20)

    ground.hide_render = True
    set_visible(everything, [])
    corridor = corridor_stage(stage)
    copies = decorate_stage(stage, built)
    kit.shoot(scene, "corridor_flight", (0, 40, 72), (0, -160, 10), (1600, 900), 24)
    kit.shoot(scene, "corridor_floor", (-14, -60, 12), (6, -170, 8), (1600, 900), 22)
    kit.shoot(scene, "corridor_rim", (-30, 30, 95), (40, -150, 40), (1600, 900), 24)

    for root in [corridor] + copies:
        for child in list(root.children):
            bpy.data.objects.remove(child)
        bpy.data.objects.remove(root)
    light_up(prop_roots, 0)
    ground.hide_render = False
    for root in prop_roots:
        for child in root.children:
            child.hide_render = False
    player_root.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "shadow_bog_models.blend"))
    print("saved", HERE / "shadow_bog_models.blend")
    for model in prop_models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    main()
