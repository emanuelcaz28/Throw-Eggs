"""Builds Starfall Crater's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_starfall_crater.py

Saves starfall_crater_models.blend and renders to design/world/models_starfall_crater/, with a stretch of
corridor and two videos of the moving props (starfall_flight.mp4 down the corridor, starfall_motion.mp4 close up).

Starfall Crater, map 8 and the last, is where the stars came down: a field of craters under a night sky, and
the owner asked for it nicer and more decorative than any map before, with things that move where moving
makes sense. Midnight-blue crater rock, pale moon-dust rims, and light from what fell: cyan crystals, gold
star-stuff and magenta nebula glow, so it reads at a glance as the end of the road and nothing like Shadow
Bog's violet tar. Landmarks: a fallen star plunged point-first into its crater, crystal spires with a halo
turning round them, a little observatory whose dome turns, ringed planets and comets in the sky, stardust
pouring down the corridor walls and crystal arches across it.

What moves, and how, is MOTION below; the game moves the same parts the same way (shared/Config/PropMotion.luau,
PropMotionController), so keep the two in step. A moving part is its own colour role, because each role is one
mesh and one part in Studio. Kinds of motion: spin (degrees a second round the upright axis, through the
prop's origin or the part's own middle), bob (studs up and down over period seconds), pulse (the glow dims to
`pulse` of its brightness and back), fall (drops `fall` studs over period, then starts again: sparkles spaced
that far apart pour down for ever) and drift (the whole prop glides `drift` studs head first, then starts over).

Glowing parts get the Neon material in the game (shared/Roles.luau). Props that must face a certain way
(StardustFall, CrystalArch) carry a small Front part that MapDecor uses to turn them, then removes.
1 Blender unit = 1 stud, props stand on Z = 0 at their origin.
"""
import math
import random
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_desert import beam  # noqa: E402
from build_forest import Model  # noqa: E402
from build_shadow_bog import dome, limb, puddle  # noqa: E402
from build_swamp import place_copy  # noqa: E402
from build_volcano import prism, set_sky, set_visible  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "models_starfall_crater"

GLOW_ROLES = {"CrystalGlow", "NebulaGlow", "StarGlow", "Sparkle", "Motes", "Shard", "Core", "Bloom", "Bud", "Beacon",
              "Halo", "Gyro", "Orb", "Stream", "Falling", "CometHead", "CometTail", "LampStar", "Window"}
kit.NO_STUDS.update(GLOW_ROLES)

# Shared colours, so every prop's rock, dust and light match.
ROCK, ROCK_DARK, ROCK_LIGHT = "#4b5688", "#353e68", "#6f7bab"
DUST, DUST_DARK = "#c3cbee", "#959fcc"
SCORCH = "#232846"
CRYSTAL, CRYSTAL_GLOW = "#8ff0ff", "#3fdcff"
PINK, NEBULA_GLOW = "#ffa3ec", "#ff58d6"
STAR, STAR_DARK, STAR_GLOW, SPARKLE = "#ffc93f", "#e09a2a", "#ffe066", "#fff4cf"
METAL, METAL_DARK = "#d3d8e8", "#7d859e"

# The corridor's Starfall Crater colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#303a72", "FloorB": "#29326a", "Dirt": "#232b54", "DirtB": "#1d2449", "Grass": "#aab4e2"}
SKY = "#141a40"
GLOW_STRENGTH = 3.0

# What moves (see the top). The game reads the same numbers from shared/Config/PropMotion.luau.
MOTION = {
    "prop_StarCrystals": {"Shard": dict(bob=0.5, period=3.2, spin=50, about="self"),
                          "Motes": dict(spin=30, about="pivot", bob=0.3, period=4.5)},
    "prop_Meteorite": {"Core": dict(pulse=0.4, period=2.2)},
    "prop_StarBloom": {"Bloom": dict(spin=35, about="self", bob=0.15, period=3)},
    "prop_CrashedProbe": {"Dish": dict(spin=60, about="self"), "Beacon": dict(pulse=0.1, period=1.1)},
    "prop_FloatingRocks": {"RockA": dict(bob=0.6, period=4.2, spin=6, about="self"),
                           "RockB": dict(bob=0.8, period=5.3, spin=-9, about="self"),
                           "RockC": dict(bob=0.5, period=3.7, spin=12, about="self")},
    "prop_CrystalSpire": {"Halo": dict(spin=18, about="pivot", bob=0.6, period=5)},
    "prop_Observatory": {"Dome": dict(spin=8, about="pivot"), "Slit": dict(spin=8, about="pivot"),
                         "Scope": dict(spin=8, about="pivot")},
    "prop_StarLamp": {"LampStar": dict(spin=45, about="self")},
    "prop_FallenStar": {"Motes": dict(spin=22, about="pivot", bob=0.8, period=4), "StarGlow": dict(pulse=0.55, period=3)},
    "prop_RingedPlanet": {"PlanetA": dict(spin=10, about="pivot"), "PlanetB": dict(spin=10, about="pivot"),
                          "Moons": dict(spin=-16, about="pivot")},
    "prop_Comet": {"*": dict(drift=420, period=36, fade=0.12, head="CometHead")},
    "prop_StardustFall": {"Falling": dict(fall=4, period=0.9)},
    "prop_CrystalArch": {"Gyro": dict(spin=40, about="self")},
}


def prop(name, **colours):
    return Model(f"prop_{name}", colours)


# ---------------------------------------------------------------------- shape helpers


def star_prism(m, role, centre, outer, inner, depth, tilt=(0, 0, 0), points=5):
    """A chunky star with `points` points, `depth` thick, standing in the XZ plane facing +Y, then turned by
    tilt (Euler XYZ, radians). The faces are fans from the middle, so the importer can't fold the points."""
    turn = Euler(tilt, "XYZ").to_matrix()
    c = Vector(centre)
    ring = []
    for i in range(points * 2):
        a = math.pi / 2 + i * math.pi / points
        r = outer if i % 2 == 0 else inner
        ring.append((math.cos(a) * r, math.sin(a) * r))
    verts = []
    for y in (-depth / 2, depth / 2):
        verts.append(tuple(c + turn @ Vector((0, y, 0))))
        for u, v in ring:
            verts.append(tuple(c + turn @ Vector((u, y, v))))
    n = len(ring)
    faces = []
    for start in (0, n + 1):
        for i in range(n):
            faces.append([start, start + 1 + i, start + 1 + (i + 1) % n])
    for i in range(n):
        faces.append([1 + i, 1 + (i + 1) % n, n + 2 + (i + 1) % n, n + 2 + i])
    m._add(role, verts, faces)


def gem(m, role, x, y, z, r, up, down, sides=4, turn=0.0):
    """A double-pointed crystal: a ring at z, a point `up` above it and `down` below."""
    ring = [(x + r * math.cos(turn + i * math.tau / sides), y + r * math.sin(turn + i * math.tau / sides), z) for i in range(sides)]
    verts = ring + [(x, y, z + up), (x, y, z - down)]
    faces = []
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides])
        faces.append([j, i, sides + 1])
    m._add(role, verts, faces)


def ball(m, role, x, y, z, r, sides=8, rings=5):
    """A chunky ball: stacked n-sided slices."""
    for k in range(rings):
        a0 = -math.pi / 2 + k * math.pi / rings
        a1 = a0 + math.pi / rings
        prism(m, role, x, y, z + r * math.sin(a0), z + r * math.sin(a1), max(r * math.cos(a0), 0.03), max(r * math.cos(a1), 0.03),
              sides, math.pi / sides)


def flat_ring(m, role, x, y, z, radius, width, thick, n=16):
    pts = [(x + radius * math.cos(i * math.tau / n), y + radius * math.sin(i * math.tau / n), z) for i in range(n)]
    for i in range(n):
        beam(m, role, pts[i], pts[(i + 1) % n], width, thick)


def hoop(m, role, x, y, z, radius, thick, plane="xz", n=16):
    """An upright ring, standing in the XZ plane (facing Y) or the YZ plane (facing X)."""
    pts = []
    for i in range(n):
        a = math.tau / (2 * n) + i * math.tau / n
        u, v = radius * math.cos(a), radius * math.sin(a)
        pts.append((x + u, y, z + v) if plane == "xz" else (x, y + u, z + v))
    for i in range(n):
        beam(m, role, pts[i], pts[(i + 1) % n], thick, thick)


def crystal(m, body, glow, x, y, z, h, r, lean=(0, 0), turn=0.0, sides=6):
    """A crystal column growing from z: its body, then a glowing point."""
    mid = h * 0.68
    lx, ly = lean
    prism(m, body, x, y, z - 0.3, z + mid, r, r * 0.88, sides, turn, (lx * 0.68, ly * 0.68))
    prism(m, glow, x + lx * 0.68, y + ly * 0.68, z + mid, z + h, r * 0.88, 0.04, sides, turn, (lx * 0.32, ly * 0.32))


def sparkle(m, role, x, y, z, s):
    """A four-pointed twinkle: two thin crossed diamonds."""
    m.loft_z(role, (z - s, x, y, 0.04, 0.04), (z, x, y, s * 0.35, s * 0.35))
    m.loft_z(role, (z, x, y, s * 0.35, s * 0.35), (z + s, x, y, 0.04, 0.04))
    m.loft_x(role, (x - s, y, z, 0.04, 0.04), (x, y, z, s * 0.35, s * 0.35))
    m.loft_x(role, (x, y, z, s * 0.35, s * 0.35), (x + s, y, z, 0.04, 0.04))


def crater_rim(m, rng, rx, ry, count, size, roles=("Dust", "DustDark"), z=0.0):
    """A ring of mounds thrown up round an impact."""
    for i in range(count):
        a = i * math.tau / count + rng.uniform(-0.12, 0.12)
        s = rng.uniform(*size)
        m.block(roles[i % len(roles)], math.cos(a) * rx, math.sin(a) * ry, z + s * 0.22, s, s * rng.uniform(0.8, 1.2), s * 0.44)


def boulder(m, role, x, y, w, d, h, top_role=None):
    """A chunky rock: a wide base and a smaller lump on it."""
    m.loft_z(role, (0, x, y, w, d), (h * 0.6, x + 0.05 * w, y, w * 0.95, d * 0.92))
    m.loft_z(top_role or role, (h * 0.6, x + 0.05 * w, y, w * 0.95, d * 0.92), (h, x + 0.1 * w, y + 0.05 * d, w * 0.6, d * 0.55))


# ---------------------------------------------------------------------- floor props


def star_crystals(seed=1):
    """The map's signature: a cluster of cyan and pink crystals bursting out of the rock, glowing at their
    points. A crystal shard floats above it, turning, and little motes of light circle round it."""
    m = prop("StarCrystals", Rock=ROCK, RockDark=ROCK_DARK, Dust=DUST, Crystal=CRYSTAL, CrystalGlow=CRYSTAL_GLOW,
             Pink=PINK, NebulaGlow=NEBULA_GLOW, Shard=CRYSTAL_GLOW, Motes=SPARKLE)
    rng = random.Random(seed)
    puddle(m, "Dust", ((0, 0, 7, 6), (1.5, -1, 5, 5), (-1.8, 1.2, 4, 4)), z=0.1, thick=0.2)
    for k in range(6):
        a = k * math.tau / 6 + rng.uniform(-0.2, 0.2)
        r = rng.uniform(2.4, 3.1)
        boulder(m, "RockDark" if k % 2 else "Rock", math.cos(a) * r, math.sin(a) * r, rng.uniform(1.4, 2.2), rng.uniform(1.3, 2.0),
                rng.uniform(0.9, 1.6))
    for i, (x, y, h, r, lean) in enumerate(((0, 0, 8.0, 1.25, (0.1, -0.15)), (1.9, 0.8, 5.2, 0.85, (0.6, 0.3)),
                                            (-1.8, 0.6, 5.8, 0.9, (-0.6, 0.2)), (0.6, -1.9, 4.2, 0.75, (0.2, -0.6)),
                                            (-1.0, -1.5, 3.2, 0.6, (-0.4, -0.5)), (2.4, -1.4, 2.6, 0.55, (0.5, -0.3)))):
        body, glow = ("Pink", "NebulaGlow") if i in (2, 5) else ("Crystal", "CrystalGlow")
        crystal(m, body, glow, x, y, 0, h, r, lean, turn=rng.uniform(0, 1))
    gem(m, "Shard", 0, 0, 10.6, 0.7, 1.3, 1.3)
    for k in range(5):
        a = k * math.tau / 5
        m.block("Motes", math.cos(a) * 3.6, math.sin(a) * 3.6, 4.5 + (k % 3) * 1.2, 0.34, 0.34, 0.34)
    return m


def meteorite(seed=2):
    """A charred meteorite that skidded in and stopped in its own crater, still glowing hot through its cracks,
    with the furrow it ploughed behind it and bits of it scattered round."""
    m = prop("Meteorite", Char="#2c2738", CharDark="#1e1a28", Core="#ffab3a", Scorch=SCORCH, Dust=DUST, DustDark=DUST_DARK)
    rng = random.Random(seed)
    puddle(m, "Scorch", ((0, 0, 9, 8), (0, -5, 3.6, 7), (1.5, 1.5, 5, 5)), z=0.08, thick=0.16)
    crater_rim(m, rng, 5.0, 4.4, 16, (1.0, 1.9))
    for side in (-1, 1):  # banks along the furrow
        for y in (-4.6, -6.6, -8.4):
            m.block("Dust", side * 2.1, y, 0.3, 1.2, 1.8, 0.6)
    m.loft_z("Char", (0, 0, 0, 3.4, 3.0), (1.1, 0, 0, 4.0, 3.6))
    m.loft_z("Char", (1.1, 0, 0, 4.0, 3.6), (2.2, 0.3, -0.2, 3.4, 3.0))
    m.loft_z("Char", (2.2, 0.3, -0.2, 3.4, 3.0), (3.3, 0.5, -0.2, 1.9, 1.7))
    m.block("CharDark", -1.4, 0.6, 1.0, 2.0, 2.2, 1.8)
    m.block("CharDark", 1.45, 0.9, 1.2, 1.6, 1.4, 2.0)
    m.block("Char", 0.2, 1.45, 0.9, 2.4, 1.2, 1.6)
    m.block("CharDark", -0.4, -1.6, 0.7, 1.8, 1.2, 1.4)
    # Glowing cracks over its top and front, and glow in the seams between its lumps.
    for pts in (((-0.3, -0.9, 3.32), (0.3, -0.3, 3.32), (0.7, -0.6, 3.32), (1.3, 0.4, 3.32)),
                ((0.5, 0.0, 3.32), (0.0, 0.5, 3.32))):
        for a, b in zip(pts, pts[1:]):
            beam(m, "Core", a, b, 0.24, 0.08)
    for a, b in (((-0.8, 2.07, 1.6), (0.2, 2.07, 1.0)), ((0.2, 2.07, 1.0), (1.0, 2.07, 1.5)), ((1.0, 2.07, 1.5), (1.3, 2.07, 0.4))):
        beam(m, "Core", a, b, 0.08, 0.24)
    m.block("Core", -0.3, 0.6, 0.35, 0.5, 2.6, 0.5)
    m.block("Core", 0.75, -0.2, 2.0, 0.3, 2.2, 0.3)
    for x, y, s in ((3.2, 1.8, 0.6), (-3.0, -1.6, 0.5), (2.2, -3.2, 0.45), (-2.4, 2.8, 0.4)):
        m.block("Char", x, y, s / 2, s, s, s)
        m.block("Core", x, y + s * 0.5, s * 0.5, s * 0.35, 0.06, s * 0.35)
    return m


def star_bloom(seed=3):
    """An alien flower: curling purple stalks and broad teal leaves, the tallest stalk crowned with a glowing gold
    star that slowly turns, and round magenta buds on the others."""
    m = prop("StarBloom", Stem="#6a4fc0", Leaf="#4cc7b2", LeafDark="#2f8f87", Bloom=STAR_GLOW, Bud=NEBULA_GLOW, Dust=DUST_DARK)
    rng = random.Random(seed)
    m.loft_z("Dust", (0, 0, 0, 3.2, 3.0), (0.4, 0, 0, 2.2, 2.0))
    for k in range(5):
        a = k * math.tau / 5 + rng.uniform(-0.2, 0.2)
        tip = (math.cos(a) * 2.8, math.sin(a) * 2.8, 1.3)
        beam(m, "Leaf", (math.cos(a) * 0.3, math.sin(a) * 0.3, 0.4), tip, 1.5, 0.18, 0.55)
        beam(m, "LeafDark", (math.cos(a) * 0.5, math.sin(a) * 0.5, 0.55), (tip[0] * 0.9, tip[1] * 0.9, tip[2] + 0.06), 0.18, 0.12, 0.06)
    top = (0.25, 0.1, 6.6)
    limb(m, "Stem", [(0, 0, 0.3), (0.6, 0.3, 2.5), (-0.2, 0.6, 4.6), top], 0.5, 0.3)
    star_prism(m, "Bloom", (top[0], top[1], top[2] + 1.1), 1.5, 0.65, 0.5)
    star_prism(m, "Bloom", (top[0], top[1], top[2] + 1.1), 0.8, 0.36, 0.8)
    for start, bend, end in (((0.2, 0, 1.5), (1.6, -0.4, 3.2), (2.0, -0.2, 4.2)), ((-0.1, 0.2, 1.8), (-1.5, 0.3, 2.9), (-1.9, -0.2, 3.6))):
        limb(m, "Stem", [start, bend, end], 0.34, 0.22)
        ball(m, "Bud", end[0], end[1], end[2] + 0.45, 0.55, 6, 4)
    for a in (0.8, 2.6, 4.4):  # little curled tendrils
        beam(m, "Stem", (math.cos(a) * 0.3, math.sin(a) * 0.3, 2.0), (math.cos(a) * 1.1, math.sin(a) * 1.1, 2.7), 0.14)
    return m


def moon_rock(seed=4):
    """A pitted boulder of moon rock with craters on top and glowing crystal stubs poking out of its side."""
    m = prop("MoonRock", Rock=ROCK, RockDark=ROCK_DARK, RockLight=ROCK_LIGHT, CrystalGlow=CRYSTAL_GLOW)
    m.loft_z("Rock", (0, 0, 0, 4.2, 3.6), (1.3, 0.1, 0.1, 5.0, 4.4))
    m.loft_z("Rock", (1.3, 0.1, 0.1, 5.0, 4.4), (2.6, 0.3, 0.2, 3.8, 3.3))
    m.loft_z("Rock", (2.6, 0.3, 0.2, 3.8, 3.3), (3.3, 0.4, 0.3, 2.4, 2.1))
    m.loft_z("RockLight", (0, -2.2, -1.0, 2.4, 2.2), (1.0, -2.3, -1.1, 2.6, 2.3))
    m.loft_z("RockLight", (1.0, -2.3, -1.1, 2.6, 2.3), (1.9, -2.1, -1.0, 1.4, 1.3))
    m.loft_z("RockDark", (0, 2.3, 1.2, 1.8, 1.6), (1.2, 2.2, 1.1, 1.2, 1.1))
    for x, y, z, r in ((0.4, 0.3, 3.3, 0.6), (-0.6, -0.9, 2.62, 0.45), (1.7, 0.9, 2.62, 0.4)):  # craters on top
        m.block("RockDark", x, y, z + 0.02, r * 1.4, r * 1.4, 0.06)
        for dx, dy, w, d in ((0, r, 2 * r + 0.3, 0.3), (0, -r, 2 * r + 0.3, 0.3), (r, 0, 0.3, 2 * r), (-r, 0, 0.3, 2 * r)):
            m.block("RockLight", x + dx, y + dy, z + 0.1, w, d, 0.2)
    for x, y, z, h, lean in ((2.3, 0.4, 0.9, 1.8, (0.8, 0.1)), (-2.4, 0.9, 0.6, 1.4, (-0.7, 0.3)), (0.6, 2.1, 1.2, 1.3, (0.1, 0.7)),
                             (0.9, 2.3, 0.6, 0.9, (0.4, 0.5))):
        prism(m, "CrystalGlow", x, y, z, z + h, 0.34, 0.04, 6, 0, lean)
    return m


def glow_tufts(seed=5):
    """Clumps of stiff blue blades tipped with glowing beads: the filler between everything else."""
    m = prop("GlowTufts", Blade="#5468c8", BladeDark="#3a4796", NebulaGlow=NEBULA_GLOW, CrystalGlow=CRYSTAL_GLOW, Dust=DUST_DARK)
    rng = random.Random(seed)
    for cx, cy, count in ((0, 0, 8), (1.6, 1.2, 6), (-1.4, 1.0, 5)):
        m.block("Dust", cx, cy, 0.1, 1.6, 1.4, 0.2)
        for k in range(count):
            a = rng.uniform(0, math.tau)
            lean = rng.uniform(0.3, 1.0)
            h = rng.uniform(1.2, 2.6)
            tip = (cx + math.cos(a) * lean, cy + math.sin(a) * lean, h)
            beam(m, "Blade" if k % 2 else "BladeDark", (cx + math.cos(a) * 0.2, cy + math.sin(a) * 0.2, 0.1), tip, 0.24, None, 0.06)
            if k % 2 == 0:
                m.block("NebulaGlow" if k % 4 == 0 else "CrystalGlow", *tip, 0.26, 0.26, 0.26)
    return m


def crashed_probe(seed=6):
    """A space probe that came down with the stars: gold-foiled, half buried and leaning, one solar panel flat
    on the ground and the other snapped up out of the dust. Its radar dish still turns on its mast, and a red
    light on top still blinks."""
    m = prop("CrashedProbe", Metal=METAL, MetalDark=METAL_DARK, Foil="#e8b84a", Panel="#2d5bd1", PanelLine="#9fc0ff",
             Dish=METAL, Beacon="#ff4d6a", Dust=DUST, DustDark=DUST_DARK, Scorch=SCORCH)
    rng = random.Random(seed)
    puddle(m, "Scorch", ((0, -3, 3, 6), (0, 0, 5, 5)), z=0.06, thick=0.12)
    crater_rim(m, rng, 2.4, 2.4, 10, (0.9, 1.5))
    lean = (0.8, 0.3)
    z0, z1 = 0.2, 3.4

    def at(z):  # the body's middle at height z
        t = (z - z0) / (z1 - z0)
        return lean[0] * t, lean[1] * t

    prism(m, "Foil", 0, 0, z0, z1, 1.4, 1.3, 8, math.pi / 8, lean)
    for z in (1.2, 2.5):
        x, y = at(z)
        prism(m, "MetalDark", x, y, z - 0.12, z + 0.12, 1.48, 1.47, 8, math.pi / 8)
    x, y = at(z1)
    prism(m, "Metal", x, y, z1, z1 + 0.5, 1.3, 0.9, 8, math.pi / 8, (lean[0] * 0.15, lean[1] * 0.15))
    mx, my = x + lean[0] * 0.15, y + lean[1] * 0.15
    beam(m, "MetalDark", (mx, my, z1 + 0.5), (mx, my, 6.0), 0.2)
    # The dish, centred on the mast so it turns on the spot: dish, feed spike and counterweight.
    m.loft_x("Dish", (mx - 0.2, my, 6.0, 0.4, 0.4), (mx + 0.25, my, 6.0, 2.0, 2.0))
    beam(m, "Dish", (mx + 0.2, my, 6.0), (mx + 1.0, my, 6.0), 0.1)
    m.block("Dish", mx - 0.55, my, 6.0, 0.5, 0.6, 0.6)
    m.block("Beacon", mx, my, 6.45, 0.36, 0.36, 0.36)
    # Solar panels: one flat on the ground, one snapped and sticking up.
    m.block("Panel", -4.0, 0.5, 0.35, 4.4, 2.4, 0.16)
    for k in range(1, 4):
        m.block("PanelLine", -6.2 + k * 1.1, 0.5, 0.45, 0.08, 2.4, 0.04)
    m.block("PanelLine", -4.0, 0.5, 0.45, 4.4, 0.08, 0.04)
    beam(m, "MetalDark", (-1.3, 0.4, 1.1), (-1.9, 0.5, 0.45), 0.2)
    beam(m, "Panel", (2.6, -1.2, 0.1), (3.8, -1.9, 3.2), 2.2, 0.16)
    beam(m, "MetalDark", (1.3, -0.4, 1.4), (2.6, -1.2, 0.6), 0.2)
    for y in (-3.4, -5.4, -7.2):  # the skid it left
        m.block("DustDark", rng.uniform(-0.4, 0.4), y, 0.2, 1.8, 1.4, 0.3)
    return m


def star_crater(seed=16):
    """A shallow scorched crater where a small star landed: cracks of gold light radiating from a star-shaped
    glow, specks of star dust and a low rim. Flat (under half a stud), so it can lie where the eggs land."""
    m = prop("StarCrater", Scorch=SCORCH, ScorchDark="#1a1e38", Dust=DUST, DustDark=DUST_DARK, StarGlow=STAR_GLOW, Sparkle=SPARKLE)
    rng = random.Random(seed)
    puddle(m, "Scorch", ((0, 0, 11, 10), (2, 1.5, 7, 7), (-2.5, -1.5, 6, 6)), z=0.06, thick=0.12)
    puddle(m, "ScorchDark", ((0, 0, 5, 5),), z=0.09, thick=0.12)
    for i in range(22):
        a = i * math.tau / 22
        s = rng.uniform(1.0, 1.7)
        m.block("Dust" if i % 3 else "DustDark", math.cos(a) * 6.2, math.sin(a) * 5.8, 0.18, s, s, 0.36)
    for k in range(7):
        a = k * math.tau / 7 + rng.uniform(-0.2, 0.2)
        pts = [(math.cos(a) * 1.2, math.sin(a) * 1.2, 0.17)]
        for r in (2.4, 3.6, 4.9):
            b = a + rng.uniform(-0.25, 0.25)
            pts.append((math.cos(b) * r, math.sin(b) * r, 0.17))
        for p, q in zip(pts, pts[1:]):
            beam(m, "StarGlow", p, q, 0.28, 0.08)
    star_prism(m, "StarGlow", (0, 0, 0.18), 1.7, 0.75, 0.1, (math.pi / 2, 0, 0))
    for _ in range(9):
        a, r = rng.uniform(0, math.tau), rng.uniform(1.5, 5.0)
        m.block("Sparkle", math.cos(a) * r, math.sin(a) * r, 0.2, 0.22, 0.22, 0.08)
    return m


# ---------------------------------------------------------------------- rim props and landmarks


def floating_rocks(seed=7):
    """Three chunks of rock floating over a glowing crater, as if the ground forgot to keep hold of them. They
    rise and fall, each in its own time, and slowly turn."""
    m = prop("FloatingRocks", Dust=DUST, DustDark=DUST_DARK, NebulaGlow=NEBULA_GLOW, RockA=ROCK, RockB=ROCK_LIGHT, RockC=PINK,
             Rock=ROCK_DARK)
    rng = random.Random(seed)
    crater_rim(m, rng, 3.6, 3.3, 12, (0.9, 1.5))
    puddle(m, "NebulaGlow", ((0, 0, 4.4, 3.6), (0, 0, 3.4, 4.8), (0.8, -0.6, 3, 3), (-0.9, 0.7, 2.6, 2.6)), z=0.1, thick=0.14)
    for x, y, w in ((2.6, 2.4, 0.6), (-2.9, -1.6, 0.5)):  # pebbles left behind
        m.block("Rock", x, y, w / 2, w, w, w)

    def rock(role, x, y, z, w):
        m.loft_z(role, (z - w * 0.95, x, y, w * 0.22, w * 0.22), (z, x, y, w, w * 0.9))
        m.loft_z(role, (z, x, y, w, w * 0.9), (z + w * 0.3, x + 0.08 * w, y, w * 0.82, w * 0.72))
        m.block(role, x - 0.15 * w, y + 0.1 * w, z + w * 0.42, w * 0.5, w * 0.45, w * 0.3)

    rock("RockA", 0.5, 0.3, 4.4, 2.6)
    rock("RockB", -2.4, -0.8, 7.0, 1.8)
    rock("RockC", 1.9, -1.6, 9.2, 1.3)
    return m


def crystal_spire(seed=8):
    """A landmark for the rims: a great crystal tower rising out of the rock with smaller crystals round its
    foot, and a glowing gold halo set with gems turning round it, rising and falling."""
    m = prop("CrystalSpire", Rock=ROCK, RockDark=ROCK_DARK, Dust=DUST, Crystal=CRYSTAL, CrystalGlow=CRYSTAL_GLOW, Pink=PINK,
             NebulaGlow=NEBULA_GLOW, Halo=STAR_GLOW, Sparkle=SPARKLE)
    rng = random.Random(seed)
    puddle(m, "Dust", ((0, 0, 10, 9),), z=0.1, thick=0.2)
    m.loft_z("Rock", (0, 0, 0, 7.5, 7.0), (1.6, 0, 0, 6.0, 5.6))
    m.loft_z("RockDark", (1.6, 0, 0, 6.0, 5.6), (2.4, 0.2, 0, 4.2, 4.0))
    for k in range(7):
        a = k * math.tau / 7
        boulder(m, "RockDark" if k % 2 else "Rock", math.cos(a) * 4.0, math.sin(a) * 3.8, 1.6, 1.4, rng.uniform(0.8, 1.4))
    lean = (0.3, -0.2)
    crystal(m, "Crystal", "CrystalGlow", 0, 0, 2.0, 18, 1.8, lean)
    # A glowing seam up two of its edges.
    for k in (0, 3):
        a = k * math.tau / 6
        foot = (1.8 * math.cos(a) + 0.02, 1.8 * math.sin(a), 1.8)
        mid = (lean[0] * 0.68 + 1.58 * math.cos(a), lean[1] * 0.68 + 1.58 * math.sin(a), 2.0 + 18 * 0.68)
        beam(m, "CrystalGlow", foot, mid, 0.26)
    for k, (h, r) in enumerate(((6.0, 0.9), (4.5, 0.7), (7.0, 0.95), (3.6, 0.6))):
        a = k * math.tau / 4 + 0.4
        body, glow = ("Pink", "NebulaGlow") if k % 2 else ("Crystal", "CrystalGlow")
        crystal(m, body, glow, math.cos(a) * 2.6, math.sin(a) * 2.4, 1.4, h, r, (math.cos(a) * 1.5, math.sin(a) * 1.5))
    flat_ring(m, "Halo", 0, 0, 13.5, 4.4, 0.4, 0.32, 20)
    for k in range(4):
        a = k * math.tau / 4
        gem(m, "Halo", math.cos(a) * 4.4, math.sin(a) * 4.4, 13.5, 0.5, 0.8, 0.8)
    for x, y, z, s in ((2.4, 1.0, 19.5, 0.6), (-1.8, -1.6, 17.0, 0.5), (1.2, -2.2, 21.5, 0.45)):
        sparkle(m, "Sparkle", x, y, z, s)
    return m


def observatory(seed=9):
    """A little observatory on the crater's rim: a round white tower with lit windows and a door, and a domed
    roof that slowly turns, its slit open and the telescope poking out at the stars."""
    m = prop("Observatory", Wall="#e9e7f4", WallDark="#c4c2dc", Trim=METAL_DARK, Dome="#8c98c4", Slit="#1d2142", Scope=METAL,
             Door="#3b3560", Window="#ffd45a", Rock=ROCK, Dust=DUST)
    puddle(m, "Dust", ((0, 0, 13, 13),), z=0.08, thick=0.16)
    prism(m, "Rock", 0, 0, 0, 0.8, 5.6, 5.4, 8, math.pi / 8)
    for k, (w, d) in enumerate(((3.0, 1.0), (2.4, 1.0))):  # steps up to the door
        m.block("Rock", 0, 5.4 + d * (k + 0.5), 0.2 + 0.2 * (1 - k), w, d, 0.4 + 0.4 * (1 - k))
    r = 3.8
    prism(m, "Wall", 0, 0, 0.8, 6.5, r, r, 8, math.pi / 8)
    prism(m, "WallDark", 0, 0, 0.8, 1.4, r + 0.15, r + 0.15, 8, math.pi / 8)
    prism(m, "Trim", 0, 0, 6.5, 7.0, r + 0.25, r + 0.2, 8, math.pi / 8)
    face = r * math.cos(math.pi / 8)
    m.block("Door", 0, face + 0.06, 2.55, 1.5, 0.12, 2.5)
    m.block("WallDark", 0, face + 0.08, 3.95, 1.9, 0.12, 0.3)
    for side in (-1, 1):  # windows on the side faces and the back
        m.block("Window", side * (face + 0.04), 0, 4.6, 0.12, 0.9, 1.2)
    m.block("Window", 0, -(face + 0.04), 4.6, 0.9, 0.12, 1.2)
    for side in (-1, 1):  # lamps by the door
        m.block("Window", side * 1.25, face + 0.25, 3.6, 0.3, 0.3, 0.4)
    # The dome: stacked rings, with the slit (and the telescope in it) facing the door at the start.
    profile = [(7.0, 3.75), (8.1, 3.55), (9.1, 3.0), (9.9, 2.1), (10.4, 1.0), (10.6, 0.2)]
    for (za, ra), (zb, rb) in zip(profile, profile[1:]):
        prism(m, "Dome", 0, 0, za, zb, ra, rb, 8, math.pi / 8)
    for (za, ra), (zb, rb) in zip(profile, profile[1:]):
        fa, fb = ra * math.cos(math.pi / 8), rb * math.cos(math.pi / 8)
        beam(m, "Slit", (0, fa + 0.04, za), (0, fb + 0.04, zb), 1.1, 0.12)
    beam(m, "Scope", (0, 1.0, 8.6), (0, 4.6, 11.4), 0.85, None, 1.1)
    m.block("Scope", 0, 4.75, 11.5, 1.3, 0.3, 1.3)
    beam(m, "Scope", (0, 1.0, 8.6), (0, 0.4, 8.1), 0.5)
    return m


def star_lamp(seed=10):
    """A lamp post for the rims: a dark post with a curled arm, and a glowing gold star hanging from it, slowly
    turning."""
    m = prop("StarLamp", Post=METAL_DARK, PostLight=METAL, LampStar=STAR_GLOW, Rock=ROCK, Dust=DUST)
    m.block("Dust", 0, 0, 0.08, 2.6, 2.6, 0.16)
    m.loft_z("Rock", (0, 0, 0, 1.6, 1.6), (0.7, 0, 0, 1.2, 1.2))
    prism(m, "Post", 0, 0, 0.7, 6.0, 0.28, 0.22, 6)
    for z in (1.1, 3.6):
        prism(m, "PostLight", 0, 0, z - 0.12, z + 0.12, 0.38, 0.38, 6)
    gem(m, "PostLight", 0, 0, 6.15, 0.3, 0.6, 0.15)
    limb(m, "Post", [(0, 0, 5.6), (0.8, 0, 6.3), (1.6, 0, 6.2), (1.85, 0, 5.75)], 0.18, 0.12)
    m.block("PostLight", 1.85, 0, 5.4, 0.08, 0.08, 0.7)
    star_prism(m, "LampStar", (1.85, 0, 4.45), 0.8, 0.35, 0.36)
    star_prism(m, "LampStar", (1.85, 0, 4.45), 0.45, 0.2, 0.56)
    return m


def fallen_star(seed=11):
    """The crater's namesake: a great gold star that fell point first and stuck, tilted in its crater, its glowing
    heart pulsing. The crater floor is cracked with its light, rocks it threw up ring the rim, and sparkles
    still circle round it."""
    m = prop("FallenStar", Star=STAR, StarDark=STAR_DARK, StarGlow=STAR_GLOW, Motes=SPARKLE, Rock=ROCK, RockDark=ROCK_DARK,
             Dust=DUST, DustDark=DUST_DARK, Scorch=SCORCH)
    rng = random.Random(seed)
    puddle(m, "Scorch", ((0, 0, 19, 17), (3, 2, 12, 12), (-4, -3, 11, 10)), z=0.08, thick=0.16)
    crater_rim(m, rng, 10.0, 9.0, 26, (1.6, 2.8))
    for k in range(9):
        a = k * math.tau / 9 + rng.uniform(-0.2, 0.2)
        r = rng.uniform(11.5, 13.5)
        boulder(m, "RockDark" if k % 2 else "Rock", math.cos(a) * r, math.sin(a) * r, rng.uniform(1.4, 2.4), rng.uniform(1.2, 2.2),
                rng.uniform(1.0, 2.2))
    tilt = (math.radians(-22), math.radians(10), math.radians(16))
    centre = (0, 0.5, 5.4)
    star_prism(m, "StarDark", centre, 7.3, 3.2, 2.2, tilt)
    star_prism(m, "Star", centre, 7.0, 3.05, 2.7, tilt)
    star_prism(m, "StarGlow", centre, 4.0, 1.75, 3.0, tilt)
    for k in range(8):  # cracks of light across the crater floor
        a = k * math.tau / 8 + 0.2
        pts = [(math.cos(a) * 2.5, math.sin(a) * 2.5, 0.18)]
        for r in (4.5, 6.5, 8.6):
            b = a + rng.uniform(-0.2, 0.2)
            pts.append((math.cos(b) * r, math.sin(b) * r, 0.18))
        for p, q in zip(pts, pts[1:]):
            beam(m, "StarGlow", p, q, 0.4, 0.1)
    for _ in range(6):  # bits of star broken off
        a, r = rng.uniform(0, math.tau), rng.uniform(4, 8)
        gem(m, "StarGlow", math.cos(a) * r, math.sin(a) * r, 0.4, 0.4, 0.6, 0.3, 4, rng.uniform(0, 1))
    for k in range(8):
        a = k * math.tau / 8
        r = 8.0 + (k % 2) * 1.2
        sparkle(m, "Motes", math.cos(a) * r, math.sin(a) * r, 3.5 + (k % 4) * 2.2, 0.7)
    return m


def ringed_planet(seed=12):
    """A small ringed planet hanging in the sky over the rim, slowly turning, with two moons going round it."""
    m = prop("RingedPlanet", PlanetA="#ffad6b", PlanetB="#d9694a", Ring="#d8ccff", RingDark="#9d8fd8", Moons="#cdd4f2")
    rng = random.Random(seed)
    zc, r = 26.0, 6.0
    ball(m, "PlanetA", 0, 0, zc, r, 10, 7)
    for _ in range(9):  # patches on its surface, so the turning shows
        lat, lon = rng.uniform(-1.0, 1.0), rng.uniform(0, math.tau)
        x, y, z = math.cos(lat) * math.cos(lon) * r * 0.92, math.cos(lat) * math.sin(lon) * r * 0.92, math.sin(lat) * r * 0.92
        s = rng.uniform(1.6, 2.8)
        m.block("PlanetB", x, y, zc + z, s, s, s * 0.8)
    flat_ring(m, "Ring", 0, 0, zc, 9.6, 2.6, 0.26, 24)
    flat_ring(m, "RingDark", 0, 0, zc, 12.0, 0.8, 0.2, 28)
    ball(m, "Moons", 14.5, 0, zc + 1.8, 1.1, 8, 5)
    ball(m, "Moons", -11.5, 6.5, zc - 2.0, 0.8, 8, 5)
    return m


def comet(seed=13):
    """A comet crossing the sky, head first: a white-hot head and a long glowing tail spreading behind it, with
    sparks trailing off. It glides along, fades out, and comes round again."""
    m = prop("Comet", CometHead="#dafbff", CometTail="#5fd9ff", Sparkle=SPARKLE)
    rng = random.Random(seed)
    zc = 40.0
    ball(m, "CometHead", 0, 0, zc, 1.8, 8, 5)
    for k in range(5):
        a = k * math.tau / 5
        gem(m, "CometHead", math.cos(a) * 1.4, -0.4 + math.sin(a) * 0.3, zc + math.sin(a) * 1.3, 0.5, 0.6, 0.6)
    for (x0, z0), (x1, y1, z1), w0, w1 in (((0, 0), (0, -26, 1.5), 2.8, 0.2), ((0.8, 0.3), (2.6, -20, 2.0), 1.6, 0.15),
                                           ((-0.9, -0.3), (-2.4, -18, -1.0), 1.4, 0.1)):
        beam(m, "CometTail", (x0, -1.0, zc + z0), (x1, y1, zc + z1), w0, None, w1)
    for _ in range(12):
        y = rng.uniform(-24, -3)
        spread = (-y) * 0.12
        m.block("Sparkle", rng.uniform(-spread, spread), y, zc + rng.uniform(-spread, spread) + (-y) * 0.04, 0.4, 0.4, 0.4)
    return m


def stardust_fall(seed=14):
    """Stardust pouring off the rim and down the corridor wall like a waterfall of light, from a crystal outcrop
    on the rim into a glowing pool on the floor, with sparkles tumbling down it all the time. Origin on the wall's
    top inner edge: rim z 0, floor z -44, +Y out into the corridor. The Front part tells the game which way it
    faces, then it's removed."""
    m = prop("StardustFall", Rock=ROCK, RockDark=ROCK_DARK, Crystal=CRYSTAL, CrystalGlow=CRYSTAL_GLOW, Stream="#7286ff",
             StreamDark="#3f4fc4", Falling=SPARKLE, NebulaGlow=NEBULA_GLOW, Dust=DUST, Front="#ff00ff")
    rng = random.Random(seed)
    # The source on the rim: a crystal outcrop with a glowing pool spilling over the lip.
    for x, y, w in ((-4.2, -5.5, 3.0), (3.8, -6.5, 3.4), (0.5, -9.0, 3.8), (-2.0, -10.5, 2.4)):
        boulder(m, "RockDark" if x < 0 else "Rock", x, y, w, w * 0.9, w * 0.6)
    for x, y, h, r, lean in ((-3.6, -6.8, 6.0, 0.9, (-0.4, -0.6)), (3.0, -7.4, 4.6, 0.8, (0.5, -0.4)), (0.4, -10.2, 7.4, 1.0, (0, -0.8))):
        crystal(m, "Crystal", "CrystalGlow", x, y, 0.6, h, r, lean)
    puddle(m, "Stream", ((0, -3.4, 8.5, 6.0), (1.0, -6.0, 4.6, 3.0)), z=0.2, thick=0.3)
    m.block("Stream", 0, 0.9, -0.2, 8.6, 2.2, 1.0)  # bulging over the lip
    m.block("Stream", 0, 2.2, -1.6, 9.2, 2.0, 2.8)
    # The curtain, clear of the hanging grass (1.5 out), in lumps with darker edges.
    z = -2.8
    while z > -43.5:
        length = min(rng.uniform(5, 8), z + 43.5)
        width = rng.uniform(7.0, 8.6)
        x = rng.uniform(-0.4, 0.4)
        m.block("Stream", x, 2.8, z - length / 2, width, 1.6, length)
        for side in (-1, 1):
            m.block("StreamDark", x + side * (width / 2 + 0.25), 2.6, z - length / 2, 0.6, 1.4, length * 0.9)
        z -= length
    # The sparkles that fall: rows four studs apart, so moving them down four studs and back loops seamlessly.
    for k, zz in enumerate(range(-2, -44, -4)):
        for x in (-2.6, -0.6, 1.4, 3.0):
            jitter = ((k * 7 + int(x * 10)) % 5 - 2) * 0.25
            m.block("Falling", x + jitter, 3.85, zz - (1.3 if x > 0 else 0), 0.55, 0.3, 0.55)
    # The pool at its foot, against the wall, splashing.
    puddle(m, "Stream", ((0, 4.6, 13, 8), (0, 8.4, 8, 3.6), (-4.5, 6.8, 4.5, 5.5), (4.5, 6.6, 4.5, 5)), z=-43.75, thick=0.5)
    puddle(m, "NebulaGlow", ((0, 5.4, 6, 4),), z=-43.45, thick=0.1)
    for x, y, s in ((-7.6, 2.8, 1.8), (-7.2, 8.0, 1.6), (-3.2, 10.8, 1.4), (2.6, 10.8, 1.6), (6.6, 8.4, 1.8), (7.6, 3.2, 1.5)):
        m.block("Dust", x, y, -44 + s * 0.3, s, s, s * 0.6)
    for x, y, h in ((-1.6, 4.0, 1.6), (1.4, 4.4, 2.2), (0.0, 5.6, 1.2)):
        m.loft_z("Stream", (-43.5, x, y, 0.9, 0.9), (-43.5 + h, x, y, 0.2, 0.2))
    m.block("Front", 0, 6, -20, 0.2, 0.2, 0.2)
    return m


def crystal_arch(seed=15):
    """An arch of crystal across the corridor, rim to rim, glowing along its seams, with crystals bristling from
    it and hanging under it, and a gold gyroscope turning round a glowing orb under its top. It spans X; its
    feet stand on the rims beyond 36 studs from the middle, and all of it stays above the rim's height (z 0),
    clear of the flight camera."""
    m = prop("CrystalArch", Crystal=CRYSTAL, CrystalGlow=CRYSTAL_GLOW, Pink=PINK, NebulaGlow=NEBULA_GLOW, Rock=ROCK,
             RockDark=ROCK_DARK, Dust=DUST, Gyro=STAR_GLOW, Orb=SPARKLE, Chain=METAL_DARK, Front="#ff00ff")
    rng = random.Random(seed)
    span = 52

    def height(x):
        return 2 + 24 * (1 - (x / span) ** 2)

    def width(x):
        return 4.0 - 1.4 * (1 - (abs(x) / span) ** 2)

    xs = list(range(-span, span + 1, 4))
    for a, b in zip(xs, xs[1:]):
        wa, wb = width(a), width(b)
        beam(m, "Crystal" if (a // 4) % 3 else "Pink", (a, 0, height(a)), (b, 0, height(b)), wa, wa * 0.9, wb)
        for side in (-1, 1):  # the glowing seams along its faces
            beam(m, "CrystalGlow", (a, side * wa * 0.46, height(a)), (b, side * wb * 0.46, height(b)), 0.3, 0.3)
    for x in range(-span + 6, span - 5, 7):  # crystals bristling from its top
        if abs(x) < 3:
            continue
        top = height(x) + width(x) * 0.4
        lean = (x / span * 1.2, rng.uniform(-0.4, 0.4))
        body, glow = ("Pink", "NebulaGlow") if (x // 7) % 2 else ("Crystal", "CrystalGlow")
        crystal(m, body, glow, x, rng.uniform(-0.3, 0.3), top - 0.3, rng.uniform(2.8, 4.6), 0.7, lean)
    for x in (-30, -22, -12, 12, 22, 30):  # and hanging under it
        gem(m, "CrystalGlow" if abs(x) != 22 else "NebulaGlow", x, 0, height(x) - width(x) * 0.4 - 0.9, 0.45, 0.9, 1.6)
    for side in (-1, 1):  # feet: rock outcrops with crystal clusters on the rims
        fx = side * (span + 2)
        m.loft_z("Rock", (0, fx, 0, 9, 8), (2.6, fx, 0, 6.5, 6))
        m.loft_z("RockDark", (2.6, fx, 0, 6.5, 6), (3.6, fx - side * 0.4, 0, 4.4, 4.2))
        m.block("Dust", fx, 0, 0.1, 13, 11, 0.2)
        for k, (dx, dy, h) in enumerate(((2.8, 2.6, 5.2), (-2.4, -2.8, 4.0), (3.4, -2.2, 3.2), (-3.0, 2.4, 2.6))):
            body, glow = ("Pink", "NebulaGlow") if k % 2 else ("Crystal", "CrystalGlow")
            crystal(m, body, glow, fx + dx, dy, 0.4, h, 0.7, (side * 0.8, dy * 0.2))
    # The gyroscope under its top: two hoops round a glowing orb, hung on a chain.
    top = height(0) - width(0) * 0.45
    gz = top - 5.2
    m.block("Chain", 0, 0, (top + gz + 1.2) / 2, 0.16, 0.16, top - gz - 1.2)
    hoop(m, "Gyro", 0, 0, gz, 3.4, 0.34, "xz")
    hoop(m, "Gyro", 0, 0, gz, 2.6, 0.3, "yz")
    ball(m, "Orb", 0, 0, gz, 1.2, 8, 5)
    m.block("Front", 0, 6, 3, 0.2, 0.2, 0.2)
    return m


ALL = [star_crystals, meteorite, star_bloom, moon_rock, glow_tufts, crashed_probe, star_crater, floating_rocks, crystal_spire,
       observatory, star_lamp, fallen_star, ringed_planet, comet, stardust_fall, crystal_arch]


# ---------------------------------------------------------------------- preview stage


def corridor_stage(stage, length=360, seed=7):
    """A stretch of corridor in Starfall Crater's colours (floor z 0, walls 44 high, inner faces 36 from the middle)."""
    m = Model("StarfallCorridor", dict(CORRIDOR))
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


def star_sky(stage, seed=3):
    """For the renders only: stars on a far dome, like the game's night sky over this world."""
    m = Model("StarSky", {"Star": "#ffffff", "StarBlue": "#bcd0ff"})
    m.bone = "Root"
    rng = random.Random(seed)
    for k in range(420):
        a = rng.uniform(0, math.tau)
        e = rng.uniform(0.04, 1.3)
        r = 1400
        s = rng.uniform(2.5, 7)
        m.block("Star" if k % 3 else "StarBlue", math.cos(e) * math.cos(a) * r, math.cos(e) * math.sin(a) * r - 150, math.sin(e) * r, s, s, s)
    root = m.build(stage)
    light_up([root], {"Star", "StarBlue"}, 6)
    return root


# The mix Config/Decor uses for StarfallCrater, so the corridor render shows the real thing.
FLOOR = [("prop_StarCrystals", 16, (1.2, 1.6)), ("prop_StarBloom", 14, (1.2, 1.6)), ("prop_MoonRock", 12, (1.2, 1.6)),
         ("prop_Meteorite", 10, (1.1, 1.4)), ("prop_GlowTufts", 10, (1.3, 1.7)), ("prop_CrashedProbe", 5, (1.1, 1.3))]
EXTRAS = [("prop_GlowTufts", 5, (0.8, 1.1)), ("prop_MoonRock", 3, (0.5, 0.7)), ("prop_StarBloom", 2, (0.6, 0.8))]
RIM = [("prop_StarCrystals", 6, (2.0, 2.6)), ("prop_FloatingRocks", 4, (2.0, 2.6)), ("prop_StarLamp", 4, (1.8, 2.2)),
       ("prop_MoonRock", 3, (2.0, 2.6)), ("prop_StarBloom", 3, (2.0, 2.4))]


def decorate_stage(stage, built, length=360, seed=61):
    """The corridor's props laid out like Config/Decor's StarfallCrater rules."""
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
        for child in copy.children:  # copies are named ..._Front.001, so hide_markers misses them
            if role_of(child) == "Front":
                child.hide_render = True
        copies.append(copy)

    def put_random(table, x, z, y):
        name, (low, high) = pick(table)
        put(name, (x, -y, z), rng.uniform(0, math.tau), rng.uniform(low, high))

    y = 12
    while y < length - 14:
        side = rng.choice((-1, 1))
        x = side * rng.uniform(20, 27)
        put_random(FLOOR, x, 0, y)
        if rng.random() < 0.65:
            put_random(EXTRAS, side * min(max(abs(x) + rng.uniform(-8, 8), 16), 33), 0, y + rng.uniform(-8, 8))
        y += rng.uniform(13, 24)
    y = 8
    while y < length:
        for side in (-1, 1):
            if rng.random() < 0.85:
                put_random(RIM, side * rng.uniform(56, 94), 44, y)
        y += rng.uniform(16, 28)
    put("prop_FallenStar", (76, -120, 44), math.radians(200), 1.6)
    put("prop_CrystalSpire", (-70, -60, 44), math.radians(20), 1.6)
    put("prop_CrystalSpire", (72, -300, 44), math.radians(140), 1.5)
    put("prop_Observatory", (-80, -230, 44), math.radians(-60), 1.5)
    put("prop_RingedPlanet", (-120, -170, 44), math.radians(15), 2.4)
    put("prop_Comet", (110, -60, 44), math.radians(120), 2.0)
    for y, side in ((40, 1), (150, -1), (270, 1)):
        put("prop_StardustFall", (side * 36, -y, 44), side * math.pi / 2, 1)
    put("prop_CrystalArch", (0, -200, 44), 0, 1)
    for y, x, yaw in ((30, -3, 20), (95, 4, 140), (180, -4, 70), (250, 3, 200), (330, -2, 300)):
        put("prop_StarCrater", (x, -y, 0), math.radians(yaw), 1.2)
    return copies


# ---------------------------------------------------------------------- light and motion in Blender


def light_up(roots, roles, strength=GLOW_STRENGTH):
    """Glowing roles shine in the renders. Undone before saving, so the export stays plain colours."""
    for root in roots:
        for child in root.children:
            if child.type == "MESH" and role_of(child) in roles:
                for mat in child.data.materials:
                    nodes = mat.node_tree.nodes
                    bsdf = nodes.get("Principled BSDF")
                    bsdf.inputs["Emission Color"].default_value = nodes["Colour"].outputs[0].default_value
                    bsdf.inputs["Emission Strength"].default_value = strength


def night(scene):
    """Moonlight for the renders, close to the game's Starfall Crater look."""
    sun = bpy.data.objects["Sun"]
    sun.data.energy = 1.5
    sun.data.color = (0.78, 0.84, 1.0)
    ambient = scene.world.node_tree.nodes["Background"]
    ambient.inputs["Color"].default_value = (0.6, 0.66, 1.0, 1)
    ambient.inputs["Strength"].default_value = 0.75


def role_of(obj):
    return obj.name.split(".")[0].rsplit("_", 1)[-1]


def prop_of(root):
    return root.name.split(".")[0].replace("_copy", "")


def bounds_centre(obj):
    vs = [v.co for v in obj.data.vertices]
    return Vector([(min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(3)])


def centre_origins(roots):
    """Parts that turn on the spot get their origin moved to their middle, as Studio puts a part's pivot."""
    moved = []
    for root in roots:
        for child in root.children:
            motion = MOTION.get(prop_of(root), {}).get(role_of(child))
            if motion and motion.get("about") == "self":
                c = bounds_centre(child)
                child.data.transform(Matrix.Translation(-c))
                child.location = c
                moved.append((child, c))
    return moved


def restore_origins(moved):
    for child, c in moved:
        child.data.transform(Matrix.Translation(c))
        child.location = (0, 0, 0)
        child.rotation_euler = (0, 0, 0)


def motion_entries(roots):
    """Everything that moves, with where it starts: (object, motion, start location, phase, root, root start)."""
    entries = []
    for root in roots:
        moves = MOTION.get(prop_of(root), {})
        phase = (sum(ord(ch) * (i + 1) for i, ch in enumerate(root.name)) % 997) / 997
        if "*" in moves:
            entries.append((None, moves["*"], None, phase, root, root.location.copy()))
        for child in root.children:
            motion = moves.get(role_of(child))
            if motion:
                entries.append((child, motion, child.location.copy(), phase, root, None))
    return entries


def apply_motion(entries, t):
    """The same moves PropMotionController makes in the game, at time t seconds."""
    for obj, mo, start, phase, root, root_start in entries:
        if obj is None:  # drift: the whole prop glides head first (+Y in the model) and starts over
            ahead = (root.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
            along = mo["drift"] * (((t / mo["period"]) + phase) % 1 - 0.5)
            root.location = root_start + ahead * along
            continue
        loc = start.copy()
        if "bob" in mo:
            loc.z += mo["bob"] * math.sin(math.tau * (t / mo["period"] + phase))
        if "fall" in mo:
            loc.z -= mo["fall"] * ((t / mo["period"] + phase) % 1)
        obj.location = loc
        obj.rotation_euler = (0, 0, math.radians(mo.get("spin", 0)) * t)
        if "pulse" in mo:
            k = mo["pulse"] + (1 - mo["pulse"]) * (0.5 + 0.5 * math.sin(math.tau * (t / mo["period"] + phase)))
            for mat in obj.data.materials:
                mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = GLOW_STRENGTH * k


def reset_motion(entries):
    for obj, mo, start, phase, root, root_start in entries:
        if obj is None:
            root.location = root_start
        else:
            obj.location = start
            obj.rotation_euler = (0, 0, 0)
            if "pulse" in mo:
                for mat in obj.data.materials:
                    mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = GLOW_STRENGTH


def render_video(scene, name, frames, fps, camera_at, size):
    """Renders frames (camera_at(frame) gives position and target) into an mp4 in RENDERS."""
    folder = RENDERS / f"{name}_frames"
    folder.mkdir(exist_ok=True)
    data = bpy.data.cameras.new(name)
    data.clip_end = 3000
    camera = bpy.data.objects.new(f"Cam_{name}", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = size
    for f in range(frames):
        position, target, lens, update = camera_at(f)
        update(f / fps)
        data.lens = lens
        camera.location = Vector(position)
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(folder / f"f{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(folder / "f%04d.png"),
                    "-pix_fmt", "yuv420p", "-vf", f"scale={size[0]}:-2", str(RENDERS / f"{name}.mp4")], check=True)
    for frame in folder.glob("*.png"):
        frame.unlink()
    folder.rmdir()


# ---------------------------------------------------------------------- scene and renders


def main(stills=True, videos=True):
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    props = bpy.data.collections.new("Props")
    stage = bpy.data.collections.new("Preview stage")
    for col in (props, stage):
        scene.collection.children.link(col)

    prop_models = [make() for make in ALL]
    built = {}
    prop_roots = []
    spots = {"prop_FallenStar": (0, -90, 0), "prop_StardustFall": (40, -170, 44), "prop_CrystalArch": (160, -170, 0),
             "prop_CrystalSpire": (-60, -90, 0), "prop_RingedPlanet": (-60, -170, 0), "prop_Comet": (0, -200, 0),
             "prop_Observatory": (40, -100, 0)}
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
    light_up(prop_roots, GLOW_ROLES)
    moved = centre_origins(prop_roots)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-400, -500, -0.01), (500, -500, -0.01), (500, 200, -0.01), (-400, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", CORRIDOR["FloorA"], False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = Model("Player", {"Skin": "#d8d2c4"})
    player.bone = "Root"
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    player_root = player.build(stage)
    sky = star_sky(stage)
    bpy.context.view_layer.update()
    set_sky(scene, SKY)
    night(scene)

    everything = prop_roots + [player_root]
    if stills:
        for model, root in zip(prop_models, prop_roots):
            low, high = kit.bounds(root)
            player_root.location = Vector((low.x - 3, (low.y + high.y) / 2 + 2, 0))
            bpy.context.view_layer.update()
            set_visible(everything, [root, player_root])
            centre = (low + high) / 2
            reach = max((high - low).length, 7)
            if model.name == "prop_CrystalArch":
                kit.shoot(scene, model.name, centre + Vector((-25, 125, 10)), centre, (1400, 700), 32)
            elif model.name == "prop_StardustFall":
                kit.shoot(scene, model.name, centre + Vector((40, 55, 6)), centre, (700, 900), 40)
            elif model.name in ("prop_RingedPlanet", "prop_Comet"):
                kit.shoot(scene, model.name, centre + Vector((0.5, 1.0, 0.1)) * reach * 1.1, centre, (700, 700), 50)
            else:
                kit.shoot(scene, model.name, centre + Vector((0.5, 0.9, 0.42)) * reach * 1.25, centre, (600, 600), 50)
        player_root.location = (30, -40, 0)
        bpy.context.view_layer.update()
        small = [r for r in prop_roots if prop_of(r) not in spots]
        set_visible(everything, small + [player_root])
        kit.shoot(scene, "props", (150, 55, 40), (150, -45, 5), (1800, 700), 20)
        set_visible(everything, [built[n] for n in ("prop_FallenStar", "prop_CrystalSpire", "prop_Observatory", "prop_RingedPlanet")] + [player_root])
        player_root.location = (-20, -80, 0)
        bpy.context.view_layer.update()
        kit.shoot(scene, "landmarks", (-10, 40, 40), (-10, -110, 14), (1800, 800), 24)

    if videos:  # close up on the props that move
        movers = [built[n] for n in ("prop_StarCrystals", "prop_StarBloom", "prop_CrashedProbe", "prop_FloatingRocks", "prop_StarLamp",
                                     "prop_Meteorite", "prop_Observatory", "prop_CrystalSpire", "prop_FallenStar", "prop_RingedPlanet")]
        set_visible(everything, movers)
        saved = [(r, r.location.copy()) for r in movers]
        for k, root in enumerate(movers[:6]):
            root.location = (k * 13 - 32, 0, 0)
        for k, root in enumerate(movers[6:]):
            root.location = ((k - 1.5) * 34, -40, 0)
        bpy.context.view_layer.update()
        entries = motion_entries(movers)
        render_video(scene, "starfall_motion", 90, 15,
                     lambda f: ((0, 62, 34), (0, -18, 8), 28, lambda t: apply_motion(entries, t)), (1600, 800))
        reset_motion(entries)
        for root, loc in saved:
            root.location = loc

    ground.hide_render = True
    set_visible(everything, [])
    corridor = corridor_stage(stage)
    copies = decorate_stage(stage, built)
    if stills:
        kit.shoot(scene, "corridor_flight", (0, 40, 72), (0, -160, 10), (1600, 900), 24)
        kit.shoot(scene, "corridor_floor", (-14, -60, 12), (6, -170, 8), (1600, 900), 22)
        kit.shoot(scene, "corridor_rim", (-30, 30, 95), (40, -150, 40), (1600, 900), 24)
    if videos:  # down the corridor like the flight camera, everything moving
        entries = motion_entries(copies)
        frames = 120

        def fly(f):
            t = f / (frames - 1)
            y = 40 - 300 * t
            return (0, y, 66 - 20 * t), (0, y - 160, 12), 24, lambda s: apply_motion(entries, s)

        render_video(scene, "starfall_flight", frames, 15, fly, (1600, 900))
        reset_motion(entries)

    for root in [corridor, sky] + copies:
        for child in list(root.children):
            bpy.data.objects.remove(child)
        bpy.data.objects.remove(root)
    restore_origins(moved)
    light_up(prop_roots, GLOW_ROLES, 0)
    ground.hide_render = False
    for root in prop_roots:
        for child in root.children:
            child.hide_render = False
    player_root.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "starfall_crater_models.blend"))
    print("saved", HERE / "starfall_crater_models.blend")
    for model in prop_models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    # After "--": "stills" renders only the stills, "videos" only the videos; nothing, both.
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(stills=not args or "stills" in args, videos=not args or "videos" in args)
