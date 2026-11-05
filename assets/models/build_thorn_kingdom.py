"""Builds Thorn Kingdom's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_thorn_kingdom.py              (stills and videos)
    Blender -b -P build_thorn_kingdom.py -- stills    (stills only, quicker while modelling)

Saves thorn_kingdom_models.blend and renders to design/world/models_thorn_kingdom/: one still per prop, the props
together, the landmarks, a stretch of corridor, and two videos of what moves (thorn_motion.mp4 close up,
thorn_flight.mp4 down the corridor at the flight camera's height).

Thorn Kingdom, map 13, the fifth of the mysterious, dark maps: a fairy-tale kingdom put to sleep by a curse a
thousand years ago and swallowed by briars as big as trees. Nothing in it has woken since; only the roses are
alive, glowing crimson in the dark, and the fireflies keep watch. Night under a pale silver-mauve mist and a huge
moon, and two lights of its own: crimson rose-glow and the warm gold of fireflies and lit windows. A floor of dark
moss, walls of black-violet thorn bark, and silvery moss on the rims, hanging over the walls. Dark green, black
and silver after Clockwork Citadel's bronze, iron and copper, and its crimson glow is a first. Its signature is the
briar rose: a giant rose on a thorny stem, its heart glowing, petals falling off it for ever. Around it: thorn
thickets with fireflies, kneeling stone knights holding a swinging lantern, their visors glowing, spinning wheels
turning with glowing gold thread, briar-wrapped lamp posts with a lantern swinging, fairy rings of glowing
toadstools, enchanted fountains dripping glowing water, now and then a magic mirror whose eyes watch you or a
crown floating and turning over its cushion; briar tufts as filler, and fallen rose windows of glowing glass
lying flat across the middle. On the rims: black thorn trees dropping glowing petals, and turrets with a banner
waving; landmarks: sleeping castles with banners and lit windows, rose towers crowned by a colossal glowing rose
with petals circling it, and crooked cottages smoking with a weather vane turning; a huge moon wrapped in thorns
hangs beyond the island with ravens circling it. Briars spill over the wall tops down into the corridor dropping
glowing petals, and stone bridges span it with banners and a lantern swinging under them.

No stud texture in this file: kit.PREVIEW_STUDS is off, so every material is a plain colour and the renders show
the models as they leave Blender. The studs come only in Studio, from the shared "Studs" MaterialVariant that
studio_tidy puts on every part except the glowing ones (docs/MAP_RECIPE.md step 8). The meshes still get the
usual box-projected UVs.

What moves is MOTION below, the same numbers as shared/Config/PropMotion.luau (keep the two in step).
Glowing roles (GLOW_ROLES) must also be in shared/Roles.luau, which makes them Neon in the game.
Props that must face a certain way carry a small Front part on their +Y side; MapDecor turns them, then removes it.
Learned on the maps before (docs/MAP_RECIPE.md): nothing that drifts, since drift overrides every other move; no
turn tied to a bob; parts turning on their own middle (about="self") are point-symmetric; pieces that turn
together share one centre (hooks straight above the origin, or on the X line at a height for axis="across").
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import map_kit as mk  # noqa: E402
from build_clockwork_citadel import SIDEWAYS, UPRIGHT, Frame, obox, puffs, tube, turn, wheel  # noqa: E402
from build_shadow_bog import dome  # noqa: E402
from map_kit import ball, beam, disc, flat_ring, gem, kit, limb, plate, prism, puddle  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "models_thorn_kingdom"

# Roles lit from inside. The game makes them Neon (shared/Roles.luau), so add new ones there too.
GLOW_ROLES = {"RoseGlow", "PetalGlow", "Bud", "Motes", "Glow", "Lamp", "Window", "Stream", "Falling", "Gaze", "Thread", "MirrorGlow",
              "CrownGem", "Pane", "PaneB", "Lunar"}
kit.NO_STUDS.update(GLOW_ROLES)
mk.GLOW_STRENGTH = 1.8

# Shared colours, so every prop's stone, thorns, roses and light match.
STONE, STONE_DARK, STONE_LIGHT = "#8b8996", "#666472", "#aba9b5"
MOSS, MOSS_DARK = "#62805a", "#40593c"
BARK, BARK_DARK = "#2e2430", "#1f1922"
PETAL, PETAL_DARK = "#c8243f", "#8c1430"
LEAF, LEAF_DARK = "#3e6c3c", "#2a4d2c"
GOLD, GOLD_DARK = "#e0b44a", "#a0782a"
IRON, IRON_DARK = "#3b3742", "#26232b"
WOOD, WOOD_DARK = "#6b4a34", "#46301f"
SLATE = "#4a3f5e"
VELVET = "#7a1830"
ROSE, BUD, FIREFLY = "#ff4466", "#ff6f8c", "#ffe28a"
LAMP, WINDOW = "#ffcf7a", "#ffc36a"
MIRROR, LUNAR = "#c3ccff", "#f2edd8"
WATER, DROP = "#ff9db3", "#ffd2dc"

# The corridor's Thorn Kingdom colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#344e3c", "FloorB": "#2e4535", "Dirt": "#342630", "DirtB": "#2d212a", "Grass": "#7c8c74"}
SKY = "#15121c"


def prop(name, **colours):
    return mk.prop(name, **colours)


# ---------------------------------------------------------------------- shape helpers


def rose(m, centre, r, rot=None, petal="Petal", dark="PetalDark", heart="RoseGlow", sepal="Leaf"):
    """A chunky open rose: a glowing heart, three rings of petals cupping up and opening outwards, and green
    sepals under it. Built facing up in frame rot (a 3x3 turn) round centre."""
    f = Frame(m, centre, rot)
    ball(m, heart, *centre, r * 0.34, 8, 5)
    for k in range(3):
        n = 5 + 2 * k
        ring = r * (0.22 + 0.32 * k)
        for i in range(n):
            a = (i + 0.5 * k) * math.tau / n
            d = Vector((math.cos(a), math.sin(a), 0))
            t = Vector((-math.sin(a), math.cos(a), 0))
            base = d * ring * 0.45 + Vector((0, 0, -r * 0.18))
            tip = d * (ring + r * 0.3) + Vector((0, 0, r * (0.42 - 0.17 * k)))
            plate(m, dark if (i + k) % 2 else petal, f.at(*base), f.at(*tip), tuple(f.r @ t), r * (0.32 + 0.1 * k), r * (0.5 + 0.12 * k), r * 0.07)
    for i in range(5):
        a = (i + 0.3) * math.tau / 5
        d = Vector((math.cos(a), math.sin(a), 0))
        plate(m, sepal, f.at(*(d * r * 0.2 + Vector((0, 0, -r * 0.25)))), f.at(*(d * r * 0.85 + Vector((0, 0, -r * 0.5)))),
              tuple(f.r @ Vector((-math.sin(a), math.cos(a), 0))), r * 0.25, r * 0.08, r * 0.05)


def leaf(m, role, base, tip, side, w):
    """A pointed leaf from base to tip, broad along side."""
    b, t = Vector(base), Vector(tip)
    mid = b.lerp(t, 0.45)
    plate(m, role, tuple(b), tuple(mid), side, w * 0.2, w, 0.06)
    plate(m, role, tuple(mid), tuple(t), side, w, 0.05, 0.06)


def thorn_vine(m, role, points, w0, w1, rng, every=0.8, size=0.4):
    """A twisting briar through points, tapering from w0 to w1, with thorns sticking out of it every so often."""
    limb(m, role, points, w0, w1)
    count = len(points) - 1
    for i, (p, q) in enumerate(zip(points, points[1:])):
        p, q = Vector(p), Vector(q)
        along = q - p
        steps = max(1, int(along.length / every))
        width = w0 + (w1 - w0) * (i + 0.5) / count
        for k in range(steps):
            c = p + along * ((k + 0.5) / steps)
            out = along.cross(Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))).normalized()
            beam(m, role, tuple(c + out * width * 0.3), tuple(c + out * (width * 0.5 + size)), width * 0.45, None, 0.03)


def petal_column(m, role, x, y, z0, z1, gap, size, rng):
    """Glowing petals falling: one column of petals exactly `gap` apart from z1 down to z0, each tipped its own way,
    so falling `gap` over a period and starting over loops seamlessly (each only goes as far as the next began)."""
    z = z1
    while z > z0:
        obox(m, role, (x, y, z), (size, size * 0.8, size * 0.12), turn(rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8), rng.uniform(0, math.tau)))
        z -= gap


def fireflies(m, rng, count, r0, r1, z0, z1, role="Motes", size=0.22):
    """Glowing fireflies scattered round the origin (they circle it when the role spins)."""
    for _ in range(count):
        a, r = rng.uniform(0, math.tau), rng.uniform(r0, r1)
        m.block(role, math.cos(a) * r, math.sin(a) * r, rng.uniform(z0, z1), size, size, size)


def banner(m, role, x, y, top, w, h, along="x", trim=None):
    """A hanging banner, top edge at `top`, w wide along x (or y), with a swallowtail cut at the bottom."""
    if along == "x":
        m.block(role, x, y, top - h * 0.4, w, 0.1, h * 0.8)
        for s in (-1, 1):
            m.loft_z(role, (top - h, x + s * w * 0.3, y, 0.04, 0.1), (top - h * 0.8, x + s * w * 0.25, y, w * 0.5, 0.1))
        if trim:
            m.block(trim, x, y, top - 0.08, w + 0.1, 0.14, 0.16)
    else:
        m.block(role, x, y, top - h * 0.4, 0.1, w, h * 0.8)
        for s in (-1, 1):
            m.loft_z(role, (top - h, x, y + s * w * 0.3, 0.1, 0.04), (top - h * 0.8, x, y + s * w * 0.25, 0.1, w * 0.5))
        if trim:
            m.block(trim, x, y, top - 0.08, 0.14, w + 0.1, 0.16)


def crenels(m, role, x0, x1, y, z, w=0.9, h=0.8, d=0.8, along="x"):
    """Battlements along a wall top."""
    n = max(2, int(abs(x1 - x0) / (w * 1.8)))
    for k in range(n + 1):
        t = x0 + (x1 - x0) * k / n
        if along == "x":
            m.block(role, t, y, z + h / 2, w, d, h)
        else:
            m.block(role, y, t, z + h / 2, d, w, h)


def cone_roof(m, role, x, y, z, r, h, sides=10):
    prism(m, role, x, y, z, z + h, r, 0.05, sides)


# ---------------------------------------------------------------------- floor props


def briar_rose(seed=1):
    """The map's signature: a giant rose on a thorny stem curling up out of a mossy mound, its great bloom glowing
    at the heart, two smaller roses and glowing buds on side shoots, leaves, and glowing petals drifting down off it
    for ever."""
    m = prop("BriarRose", Moss=MOSS, MossDark=MOSS_DARK, Bark=LEAF_DARK, Leaf=LEAF, Petal=PETAL, PetalDark=PETAL_DARK, RoseGlow=ROSE,
             Bud=BUD, PetalGlow=ROSE, StoneDark=STONE_DARK)
    rng = random.Random(seed)
    dome(m, "Moss", 0, 0, 0, 1.6)
    dome(m, "MossDark", 1.4, -0.8, 0, 0.9)
    m.block("StoneDark", -1.6, 1.0, 0.35, 1.4, 1.1, 0.7)
    stem = [(0, 0, 1.6), (0.6, 0.2, 3.5), (-0.2, 0.4, 5.6), (0.3, 0.1, 7.6), (0.1, 0.5, 8.8)]
    thorn_vine(m, "Bark", stem, 0.5, 0.32, rng, 0.7, 0.35)
    rose(m, (0.1, 0.6, 9.4), 2.2, turn(x=-0.35))
    for (p, q, s) in (((0.6, 0.2, 3.5), (2.3, 0.6, 5.2), 1.1), ((-0.2, 0.4, 5.6), (-2.2, -0.4, 6.6), 1.2)):
        thorn_vine(m, "Bark", [p, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, q[2] - 0.6), q], 0.28, 0.18, rng, 0.6, 0.25)
        rose(m, (q[0], q[1], q[2] + 0.35), s, turn(y=0.4 if q[0] > 0 else -0.4))
    for p in ((0.4, -0.3, 4.6), (-0.6, 0.3, 7.0), (1.2, 0.0, 2.6)):  # glowing buds on short shoots
        beam(m, "Bark", (p[0] * 0.3, p[1] * 0.3, p[2] - 0.4), p, 0.12)
        ball(m, "Bud", *p, 0.26, 6, 4)
        for k in range(3):
            a = k * math.tau / 3
            plate(m, "Leaf", (p[0], p[1], p[2] - 0.2), (p[0] + math.cos(a) * 0.3, p[1] + math.sin(a) * 0.3, p[2] + 0.15), (-math.sin(a), math.cos(a), 0),
                  0.14, 0.05, 0.04)
    for z, a in ((2.4, 0.4), (4.2, 2.5), (6.3, 4.4), (8.0, 1.2)):
        d = Vector((math.cos(a), math.sin(a), 0.2))
        base = Vector((0.2, 0.25, z))
        leaf(m, "Leaf", tuple(base), tuple(base + d * 1.8), (-math.sin(a), math.cos(a), 0.3), 0.9)
    for x, y in ((1.9, 1.6), (-1.7, 1.9), (2.4, -1.2)):  # petals falling off it, 3 apart
        petal_column(m, "PetalGlow", x, y, 0.4, 8.8, 3.0, 0.5, rng)
    return m


def thorn_thicket(seed=2):
    """A tangle of black briars arching out of the ground and back into it, little roses glowing among them and
    fireflies drifting round it."""
    m = prop("ThornThicket", Bark=BARK, BarkDark=BARK_DARK, Leaf=LEAF_DARK, Petal=PETAL, PetalDark=PETAL_DARK, RoseGlow=ROSE, Motes=FIREFLY,
             Moss=MOSS_DARK)
    rng = random.Random(seed)
    dome(m, "Moss", 0, 0, 0, 1.4)
    for k in range(7):
        a = k * math.tau / 7 + rng.uniform(-0.3, 0.3)
        reach, height = rng.uniform(2.6, 4.2), rng.uniform(3.5, 6.5)
        d = Vector((math.cos(a), math.sin(a), 0))
        side = Vector((-d.y, d.x, 0)) * rng.uniform(-1.2, 1.2)
        pts = [tuple(d * 0.4 + Vector((0, 0, 0.6))), tuple(d * reach * 0.35 + side * 0.4 + Vector((0, 0, height * 0.7))),
               tuple(d * reach * 0.7 + side + Vector((0, 0, height))), tuple(d * reach * 1.0 + side * 1.3 + Vector((0, 0, height * 0.72)))]
        thorn_vine(m, "Bark" if k % 2 else "BarkDark", pts, 0.42, 0.2, rng, 0.75, 0.4)
        if k % 2 == 0:
            p = Vector(pts[1])
            rose(m, tuple(p + Vector((0, 0, 0.45))), 0.8, turn(x=rng.uniform(-0.4, 0.4), y=rng.uniform(-0.4, 0.4)))
        for j in (1, 2, 3):
            q = Vector(pts[j])
            out = (d * 0.8 + Vector((0, 0, 0.5 if j < 3 else -0.4))).normalized()
            leaf(m, "Leaf", tuple(q), tuple(q + out * 1.3), (-d.y, d.x, 0.3), 0.65)
    fireflies(m, rng, 12, 2.0, 5.0, 2.0, 7.5)
    return m


def stone_knight(seed=3):
    """A stone knight kneeling on its plinth, its hands on the pommel of its sword, a thorny briar wound round it and
    moss on its shoulders. Its visor glows faintly, and its left hand holds out a lantern that swings on a short
    chain. The hand is on the X line at the hook's height, so the game swings the lantern round it."""
    m = prop("StoneKnight", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Moss=MOSS, Bark=BARK, Petal=PETAL, PetalDark=PETAL_DARK,
             RoseGlow=ROSE, Leaf=LEAF_DARK, Gaze="#ffb3c0", Chain=IRON, Lantern=IRON_DARK, Lamp=LAMP)
    rng = random.Random(seed)
    m.loft_z("StoneDark", (0, 0, 0, 5.2, 5.2), (0.8, 0, 0, 4.6, 4.6))
    m.block("Stone", 0, 0, 1.05, 4.2, 4.2, 0.5)
    # Kneeling: the right knee down, the left leg up.
    m.block("Stone", -0.7, -0.6, 1.9, 1.0, 2.2, 1.0)  # right shin on the plinth
    m.block("Stone", -0.7, 0.4, 2.6, 1.0, 1.2, 1.6)
    m.block("Stone", 0.7, 0.6, 2.0, 1.0, 1.0, 1.3)  # left shin, standing
    m.block("Stone", 0.7, 0.3, 3.0, 1.05, 1.9, 0.9)  # left thigh
    m.block("StoneDark", 0.7, 0.95, 2.75, 1.0, 0.3, 0.45)  # knee guard
    m.loft_z("Stone", (3.0, 0, -0.1, 2.0, 1.3), (5.6, 0, 0, 2.5, 1.5))  # torso
    m.block("StoneLight", 0, 0.5, 4.4, 1.6, 0.6, 1.4)  # breastplate
    for s in (-1, 1):
        m.block("StoneDark", s * 1.45, 0, 5.55, 0.9, 1.6, 0.7)  # pauldrons
    m.block("StoneDark", 0, -0.95, 4.4, 2.2, 0.5, 2.6)  # a shield on its back
    m.block("Stone", 0, -1.25, 4.4, 1.2, 0.12, 1.4)
    # The head: a helmet with a glowing visor slit and a crest.
    m.block("Stone", 0, 0.1, 6.35, 1.2, 1.25, 1.3)
    m.block("StoneDark", 0, 0.75, 6.45, 0.95, 0.06, 0.18)
    m.block("Gaze", 0, 0.77, 6.45, 0.75, 0.05, 0.1)
    m.loft_y("StoneLight", (-0.55, 0, 7.15, 0.24, 0.3), (0.55, 0, 7.15, 0.24, 0.5))
    # The sword planted in front, both of the right hand's on its pommel.
    m.block("StoneLight", -0.15, 1.5, 2.5, 0.3, 0.12, 3.3)
    m.block("StoneDark", -0.15, 1.5, 4.25, 1.3, 0.3, 0.25)
    ball(m, "StoneDark", -0.15, 1.5, 4.65, 0.22, 6, 3)
    beam(m, "Stone", (-1.2, 0.0, 5.3), (-0.4, 1.3, 4.4), 0.5)
    m.block("StoneDark", -0.25, 1.45, 4.5, 0.55, 0.45, 0.4)
    # The left arm held out with the lantern; the hand is at y = 0, z = hook.
    hook = 5.25
    beam(m, "Stone", (1.2, 0.0, 5.4), (2.0, 0.0, hook + 0.15), 0.5)
    m.block("StoneDark", 2.15, 0.0, hook + 0.1, 0.45, 0.45, 0.4)
    for i in range(3):
        z = hook - i * 0.35
        beam(m, "Chain", (2.15, 0, z), (2.15, 0, z - 0.35), *((0.24, 0.08) if i % 2 else (0.08, 0.24)))
    zl = hook - 1.05
    m.block("Lantern", 2.15, 0, zl, 0.8, 0.8, 0.12)
    m.loft_z("Lantern", (zl, 2.15, 0, 0.7, 0.7), (zl + 0.35, 2.15, 0, 0.2, 0.2))
    m.block("Lamp", 2.15, 0, zl - 0.55, 0.55, 0.55, 0.9)
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        m.block("Lantern", 2.15 + sx * 0.32, sy * 0.32, zl - 0.55, 0.08, 0.08, 1.0)
    m.block("Lantern", 2.15, 0, zl - 1.05, 0.7, 0.7, 0.12)
    # Moss on its shoulders, and a briar wound round it with a rose.
    for s in (-1, 1):
        m.block("Moss", s * 1.45, 0.1, 5.95, 0.8, 1.2, 0.14)
    pts = [(-2.0, -1.6, 0.9), (-1.4, 1.3, 1.8), (1.4, 1.2, 2.6), (1.5, -1.2, 3.5), (-1.2, -1.0, 4.1)]
    thorn_vine(m, "Bark", pts, 0.22, 0.14, rng, 0.6, 0.22)
    rose(m, (-1.5, 1.4, 2.25), 0.7, turn(y=-0.6))
    leaf(m, "Leaf", (1.4, 1.2, 2.6), (2.2, 1.9, 2.9), (0, 1, 0.3), 0.5)
    return m


def spinning_wheel(seed=4):
    """An old spinning wheel left mid-spin when the kingdom fell asleep: its big wheel still turning on its own,
    glowing gold thread wound on the spindle and trailing from the distaff, a stool beside it."""
    m = prop("SpinningWheel", Wood=WOOD, WoodDark=WOOD_DARK, Wheel=WOOD, Iron=IRON, Thread="#ffd36a", Petal=PETAL, Bark=BARK)
    rng = random.Random(seed)
    for sx in (-1, 1):  # the bench on splayed legs
        for sy in (-1, 1):
            beam(m, "WoodDark", (sx * 2.2, sy * 0.9, 0), (sx * 1.8, sy * 0.6, 2.2), 0.3)
    m.block("Wood", 0, 0, 2.35, 4.6, 1.6, 0.35)
    # The wheel's uprights and axle; the wheel itself stands in the YZ plane and turns on its own middle.
    zc, xc = 4.6, -0.9
    for y in (-0.55, 0.55):
        beam(m, "WoodDark", (xc, y, 2.5), (xc, y, zc + 0.2), 0.26)
    tube(m, "Iron", (xc, -0.75, zc), (xc, 0.75, zc), 0.12)
    wheel(m, "Wheel", (xc, 0, zc), 2.3, 0.22, UPRIGHT, spokes=8, rim=0.34)
    # The flyer and spindle at the other end, the gold thread wound on it.
    for y in (-0.35, 0.35):
        beam(m, "WoodDark", (1.6, y, 2.5), (1.6, y, 3.7), 0.2)
    tube(m, "Wood", (1.0, 0, 3.6), (2.5, 0, 3.6), 0.1)
    tube(m, "Thread", (1.35, 0, 3.6), (2.05, 0, 3.6), 0.28, 0.24, 10)
    beam(m, "Thread", (1.35, 0, 3.75), (xc + 0.2, 0, zc + 2.2), 0.04)  # the thread running up to the wheel
    # The distaff, wrapped in glowing fibre.
    beam(m, "WoodDark", (2.0, 0.4, 2.5), (2.6, 0.6, 6.0), 0.12)
    prism(m, "Thread", 2.45, 0.56, 4.6, 5.8, 0.36, 0.12, 8, 0, (0.08, 0.02))
    m.block("WoodDark", 1.2, 0.95, 0.15, 1.6, 0.6, 0.12)  # the treadle
    beam(m, "WoodDark", (1.2, 0.95, 0.2), (xc + 0.3, 0.6, zc - 0.4), 0.08)
    # A stool, with a rose left on it.
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        beam(m, "WoodDark", (4.2 + sx * 0.5, 1.6 + sy * 0.5, 0), (4.2 + sx * 0.38, 1.6 + sy * 0.38, 1.6), 0.18)
    m.block("Wood", 4.2, 1.6, 1.7, 1.2, 1.2, 0.22)
    beam(m, "Bark", (3.9, 1.3, 1.85), (4.6, 1.9, 1.85), 0.07)
    ball(m, "Petal", 4.65, 1.95, 1.9, 0.18, 6, 3)
    return m


def briar_lantern(seed=5):
    """A twisted iron lamp post strangled by a briar, a lantern hanging from its curled arm and swinging, a rose at
    its foot and fireflies circling it. The hook is on the X line at its height, so the game swings the lantern."""
    m = prop("BriarLantern", Iron=IRON, IronDark=IRON_DARK, Bark=BARK, Leaf=LEAF_DARK, Petal=PETAL, PetalDark=PETAL_DARK, RoseGlow=ROSE,
             Chain=IRON, Lantern=IRON_DARK, Lamp=LAMP, Motes=FIREFLY, Moss=MOSS_DARK)
    rng = random.Random(seed)
    dome(m, "Moss", 0, 0, 0, 0.9)
    prism(m, "IronDark", 0, 0, 0, 0.6, 0.7, 0.55, 8)
    prism(m, "Iron", 0, 0, 0.6, 8.6, 0.24, 0.2, 6)
    for z in (1.0, 3.5, 6.0, 8.4):
        prism(m, "IronDark", 0, 0, z - 0.12, z + 0.12, 0.32, 0.32, 6)
    hook = 8.1
    limb(m, "Iron", [(0, 0, 8.5), (0.6, 0, 9.3), (1.5, 0, 9.4), (2.2, 0, 8.9), (2.3, 0, hook + 0.1)], 0.16, 0.12)
    ball(m, "IronDark", 0, 0, 8.85, 0.25, 6, 3)
    for i in range(3):
        z = hook - i * 0.35
        beam(m, "Chain", (2.3, 0, z), (2.3, 0, z - 0.35), *((0.24, 0.08) if i % 2 else (0.08, 0.24)))
    zl = hook - 1.05
    m.block("Lantern", 2.3, 0, zl, 0.9, 0.9, 0.12)
    m.loft_z("Lantern", (zl, 2.3, 0, 0.8, 0.8), (zl + 0.4, 2.3, 0, 0.2, 0.2))
    m.block("Lamp", 2.3, 0, zl - 0.6, 0.6, 0.6, 1.0)
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        m.block("Lantern", 2.3 + sx * 0.36, sy * 0.36, zl - 0.6, 0.09, 0.09, 1.1)
    m.loft_z("Lantern", (zl - 1.3, 2.3, 0, 0.1, 0.1), (zl - 1.1, 2.3, 0, 0.8, 0.8))
    pts = [(0.3 * math.cos(k * 1.3), 0.3 * math.sin(k * 1.3), 0.5 + k * 0.62) for k in range(13)]
    thorn_vine(m, "Bark", pts, 0.14, 0.1, rng, 0.5, 0.2)
    rose(m, (0.75, 0.6, 0.9), 0.75, turn(y=0.3))
    rose(m, (-0.5, 0.3, 6.2), 0.55, turn(x=0.7))
    leaf(m, "Leaf", (0.2, 0.2, 4.0), (0.9, 1.0, 4.4), (1, -1, 0.2), 0.5)
    fireflies(m, rng, 9, 1.4, 3.2, 3.0, 9.0)
    return m


def toadstools(seed=6):
    """A fairy ring of red-capped toadstools, white spots on their caps and their gills glowing underneath, the
    biggest with a little door and a lit window in its stalk, and fireflies dancing round the ring."""
    m = prop("Toadstools", Stalk="#e8dcc6", StalkShade="#c4b59c", Cap="#b8283c", CapDark="#8a1c2e", Spot="#f6efe2", Glow="#ffb0c0",
             Moss=MOSS_DARK, WoodDark=WOOD_DARK, Window=WINDOW, Motes=FIREFLY)
    rng = random.Random(seed)
    puddle(m, "Moss", ((0, 0, 5.4, 5.0), (1.2, 0.6, 3.0, 3.0), (-1.4, -0.8, 2.8, 2.6)), z=0.05, thick=0.1)
    shrooms = [(0.0, 0.0, 5.2, 0.75, 2.4), (2.0, 1.2, 2.6, 0.4, 1.3), (-1.9, 1.0, 3.2, 0.45, 1.5), (1.4, -1.8, 2.0, 0.32, 1.0),
               (-1.2, -1.7, 1.5, 0.26, 0.8), (2.6, -0.5, 1.2, 0.22, 0.65)]
    for k, (x, y, h, r, cap) in enumerate(shrooms):
        prism(m, "Stalk", x, y, 0, h, r * 1.15, r, 8)
        prism(m, "StalkShade", x, y, h * 0.55, h * 0.62, r * 1.2, r * 1.2, 8)
        prism(m, "Glow", x, y, h - 0.02, h + 0.12, cap * 0.92, cap * 0.92, 12)  # glowing gills
        prism(m, "Cap", x, y, h + 0.12, h + cap * 0.45, cap, cap * 0.7, 12)
        prism(m, "CapDark" if k % 2 else "Cap", x, y, h + cap * 0.45, h + cap * 0.7, cap * 0.7, cap * 0.25, 12)
        for j in range(5 if k == 0 else 3):
            a = j * math.tau / (5 if k == 0 else 3) + k
            rr = cap * 0.62
            obox(m, "Spot", (x + math.cos(a) * rr, y + math.sin(a) * rr, h + cap * 0.48), (cap * 0.24, cap * 0.24, 0.1), turn(z=a))
    m.block("WoodDark", 0, 0.78, 0.75, 0.6, 0.08, 1.1)  # the big one's door and window
    m.block("Window", 0, 0.79, 2.8, 0.4, 0.06, 0.45)
    m.block("WoodDark", 0, 0.83, 2.8, 0.06, 0.04, 0.45)
    fireflies(m, rng, 10, 1.0, 3.6, 1.5, 6.5)
    return m


def rose_fountain(seed=7):
    """An enchanted fountain of cracked stone: glowing rose-pink water in its basin and its bowl, drops falling from
    the bowl's lip into the basin for ever, a stone rose on top and petals floating."""
    m = prop("RoseFountain", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Moss=MOSS, Stream=WATER, Falling=DROP, Petal=PETAL,
             PetalDark=PETAL_DARK, Bark=BARK)
    rng = random.Random(seed)
    prism(m, "StoneDark", 0, 0, 0, 0.35, 4.4, 4.4, 16)
    for k in range(16):  # the basin's wall, in blocks
        a = (k + 0.5) * math.tau / 16
        obox(m, "Stone" if k % 3 else "StoneLight", (math.cos(a) * 3.9, math.sin(a) * 3.9, 0.95), (1.6, 0.7, 1.2), turn(z=a + math.pi / 2))
    disc(m, "Stream", 0, 0, 1.2, 3.6, 0.12, 16)
    prism(m, "Stone", 0, 0, 0.3, 4.2, 0.7, 0.55, 8)
    for z in (1.6, 3.8):
        prism(m, "StoneLight", 0, 0, z - 0.15, z + 0.15, 0.8, 0.8, 8)
    prism(m, "StoneDark", 0, 0, 4.2, 4.9, 0.7, 2.1, 12)  # the bowl
    prism(m, "Stone", 0, 0, 4.9, 5.25, 2.2, 2.2, 12)
    disc(m, "Stream", 0, 0, 5.3, 1.95, 0.1, 12)  # just over the bowl, so its top shows
    prism(m, "Stone", 0, 0, 5.2, 6.6, 0.32, 0.26, 8)
    rose(m, (0, 0, 7.05), 0.8, None, petal="StoneLight", dark="Stone", heart="Stream", sepal="StoneDark")
    # Drops falling from the bowl's lip: columns of drops 1.2 apart, falling 1.2 and starting over.
    for k in range(6):
        a = k * math.tau / 6 + 0.3
        x, y = math.cos(a) * 2.25, math.sin(a) * 2.25
        z = 4.8
        while z > 1.3:
            m.block("Falling", x, y, z, 0.18, 0.18, 0.32)
            z -= 1.2
    for k in range(7):  # petals floating in the basin
        a, r = rng.uniform(0, math.tau), rng.uniform(1.0, 3.3)
        obox(m, "Petal" if k % 2 else "PetalDark", (math.cos(a) * r, math.sin(a) * r, 1.3), (0.45, 0.35, 0.06), turn(z=rng.uniform(0, math.tau)))
    for a in (0.6, 2.9, 4.6):  # moss on its rim, and a crack
        m.block("Moss", math.cos(a) * 3.9, math.sin(a) * 3.9, 1.6, 1.1, 1.0, 0.12)
    m.block("StoneDark", 3.9 * math.cos(1.8), 3.9 * math.sin(1.8), 0.95, 0.12, 0.74, 1.0)
    thorn_vine(m, "Bark", [(-4.2, -1.0, 0.1), (-3.9, 0.2, 1.8), (-3.6, 1.6, 1.2), (-4.4, 2.4, 0.1)], 0.18, 0.12, rng, 0.5, 0.2)
    return m


def magic_mirror(seed=8):
    """A rare find: a tall magic mirror in an ornate gold frame on clawed feet, its glass glowing silver-violet,
    two eyes in it that open and close as you pass, sparkles circling it and a gem in its crest."""
    m = prop("MagicMirror", Gold=GOLD, GoldDark=GOLD_DARK, MirrorGlow="#8a86e6", Gaze="#ff6b8a", CrownGem=ROSE, Motes="#e9e4ff", WoodDark=WOOD_DARK,
             Bark=BARK, Petal=PETAL)
    rng = random.Random(seed)
    zc, a_, b_ = 5.2, 1.9, 3.4  # the oval's middle and half sizes
    for sx in (-1, 1):  # clawed feet and the stand
        m.loft_z("GoldDark", (0, sx * 1.6, 0, 0.9, 1.4), (0.5, sx * 1.4, 0, 0.6, 0.9))
        beam(m, "Gold", (sx * 1.4, 0, 0.5), (sx * 1.2, 0, zc - b_ + 0.6), 0.36)
    m.block("GoldDark", 0, 0, 0.55, 3.4, 0.7, 0.3)
    rows = 14  # the glass, an oval in steps
    for k in range(rows):
        z = zc - b_ + (k + 0.5) * 2 * b_ / rows
        w = 2 * a_ * math.sqrt(max(0.0, 1 - ((z - zc) / b_) ** 2))
        m.block("MirrorGlow", 0, 0.02, z, max(w, 0.3), 0.1, 2 * b_ / rows + 0.01)
    n = 28  # the frame round it
    pts = [(math.sin(i * math.tau / n) * (a_ + 0.3), math.cos(i * math.tau / n) * (b_ + 0.3)) for i in range(n)]
    for i in range(n):
        (x0, z0), (x1, z1) = pts[i], pts[(i + 1) % n]
        beam(m, "Gold", (x0, 0, zc + z0), (x1, 0, zc + z1), 0.5, 0.5)
    for i in range(0, n, 4):
        x, z = pts[i]
        ball(m, "GoldDark", x * 1.06, 0.15, zc + z * 1.04, 0.24, 6, 3)
    m.block("WoodDark", 0, -0.2, zc, 2 * a_ + 0.4, 0.2, 2 * b_ + 0.3)  # its back
    for s in (-1, 1):  # the eyes in the glass
        m.block("Gaze", s * 0.62, 0.1, zc + 0.6, 0.85, 0.06, 0.28)
        m.block("Gaze", s * 0.62, 0.1, zc + 0.6, 0.4, 0.07, 0.5)
    # The crest: gold scrolls and a gem.
    for s in (-1, 1):
        limb(m, "Gold", [(s * 0.2, 0, zc + b_ + 0.3), (s * 0.9, 0, zc + b_ + 0.9), (s * 0.5, 0, zc + b_ + 1.4)], 0.22, 0.16)
    gem(m, "CrownGem", 0, 0.05, zc + b_ + 1.0, 0.38, 0.55, 0.45, 6)
    fireflies(m, rng, 10, 2.6, 3.6, 1.5, 9.5, "Motes", 0.18)
    thorn_vine(m, "Bark", [(-1.8, 0.5, 0.2), (-2.1, 0.2, 2.5), (-1.9, 0.1, 4.6)], 0.16, 0.1, rng, 0.5, 0.18)
    ball(m, "Petal", -1.9, 0.2, 4.7, 0.3, 6, 4)
    return m


def floating_crown(seed=9):
    """A rare treat: the sleeping kingdom's crown, floating over a velvet cushion on a stone pedestal, slowly turning
    and bobbing, its gems glowing; briars creep up the pedestal. The crown is straight above the origin."""
    m = prop("FloatingCrown", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Cushion=VELVET, Gold=GOLD, Crown=GOLD, CrownGem=ROSE,
             Bark=BARK, Leaf=LEAF_DARK, Motes=FIREFLY)
    rng = random.Random(seed)
    m.loft_z("StoneDark", (0, 0, 0, 3.4, 3.4), (0.6, 0, 0, 2.8, 2.8))
    m.loft_z("Stone", (0.6, 0, 0, 1.6, 1.6), (3.6, 0, 0, 1.3, 1.3))
    m.block("StoneLight", 0, 0, 3.75, 2.4, 2.4, 0.3)
    m.loft_z("Cushion", (3.9, 0, 0, 2.2, 2.2), (4.4, 0, 0, 1.9, 1.9))
    m.loft_z("Cushion", (4.4, 0, 0, 1.9, 1.9), (4.6, 0, 0, 1.3, 1.3))
    for sx in (-1, 1):
        for sy in (-1, 1):  # gold tassels
            m.block("Gold", sx * 1.05, sy * 1.05, 4.0, 0.16, 0.16, 0.5)
    zc = 6.0  # the crown
    for k in range(16):
        a = (k + 0.5) * math.tau / 16
        obox(m, "Crown", (math.cos(a) * 1.0, math.sin(a) * 1.0, zc), (0.45, 0.2, 0.55), turn(z=a + math.pi / 2))
    for k in range(8):
        a = k * math.tau / 8
        prism(m, "Crown", math.cos(a) * 1.0, math.sin(a) * 1.0, zc + 0.25, zc + 1.1, 0.22, 0.04, 4, a + math.pi / 4)
        ball(m, "CrownGem" if k % 2 == 0 else "Crown", math.cos(a) * 1.0, math.sin(a) * 1.0, zc + 1.15, 0.12, 6, 3)
        gem(m, "CrownGem", math.cos(a + math.pi / 8) * 1.1, math.sin(a + math.pi / 8) * 1.1, zc, 0.14, 0.16, 0.16, 4, a)
    fireflies(m, rng, 8, 1.6, 2.8, 4.5, 8.0)
    thorn_vine(m, "Bark", [(1.6, 1.0, 0.1), (0.8, 0.9, 1.4), (0.85, -0.6, 2.4), (0.75, -0.7, 3.4)], 0.16, 0.1, rng, 0.45, 0.18)
    leaf(m, "Leaf", (0.8, 0.9, 1.4), (1.5, 1.6, 1.9), (1, -1, 0.3), 0.45)
    return m


def briar_tuft(seed=10):
    """Filler: a little thorny shrub with a glowing bud or two."""
    m = prop("BriarTuft", Bark=BARK, Leaf=LEAF, LeafDark=LEAF_DARK, Bud=BUD, Moss=MOSS_DARK)
    rng = random.Random(seed)
    dome(m, "Moss", 0, 0, 0, 0.7)
    for k in range(5):
        a = k * math.tau / 5 + rng.uniform(-0.3, 0.3)
        d = Vector((math.cos(a), math.sin(a), 0))
        top = d * rng.uniform(0.8, 1.4) + Vector((0, 0, rng.uniform(1.6, 2.6)))
        thorn_vine(m, "Bark", [(0, 0, 0.6), tuple(d * 0.5 + Vector((0, 0, 1.3))), tuple(top)], 0.18, 0.1, rng, 0.45, 0.18)
        leaf(m, "Leaf" if k % 2 else "LeafDark", tuple(d * 0.5 + Vector((0, 0, 1.3))), tuple(d * 1.7 + Vector((0, 0, 1.5))), (-d.y, d.x, 0.3), 0.8)
        if k % 2 == 0:
            ball(m, "Bud", *top, 0.15, 6, 4)
    return m


def rose_window(seed=11):
    """A fallen rose window lying flat on the floor, its glass still glowing crimson and gold in its stone tracery:
    twelve petal panes round a round middle, a ring of small round panes round them. Flat (under half a stud), so it
    can lie in the middle where the eggs land."""
    m = prop("RoseWindow", StoneLight=STONE_LIGHT, Stone=STONE, Pane=ROSE, PaneB="#e89a34", Moss=MOSS_DARK)
    rng = random.Random(seed)
    prism(m, "Stone", 0, 0, 0, 0.14, 5.6, 5.6, 24)
    prism(m, "StoneLight", 0, 0, 0.14, 0.26, 5.6, 5.6, 24)
    disc(m, "Stone", 0, 0, 0.25, 5.2, 0.1, 24)  # the bed the glass sits in
    disc(m, "PaneB", 0, 0, 0.3, 1.1, 0.06, 16)
    flat_ring(m, "StoneLight", 0, 0, 0.32, 1.25, 0.3, 0.1, 16)
    for k in range(12):  # petal panes, each a teardrop of glass with stone between
        a = k * math.tau / 12
        d, t = Vector((math.cos(a), math.sin(a), 0)), Vector((-math.sin(a), math.cos(a), 0))
        plate(m, "Pane" if k % 2 else "PaneB", tuple(d * 1.5 + Vector((0, 0, 0.3))), tuple(d * 3.6 + Vector((0, 0, 0.3))), tuple(t), 0.5, 1.3, 0.06)
        beam(m, "StoneLight", tuple(d * 1.3 + Vector((0, 0, 0.33))), tuple(Vector((math.cos(a + math.pi / 12), math.sin(a + math.pi / 12), 0)) * 3.9 + Vector((0, 0, 0.33))),
             0.18, 0.1)
        c = Vector((math.cos(a + math.pi / 12), math.sin(a + math.pi / 12), 0)) * 4.5
        disc(m, "Pane" if k % 2 == 0 else "PaneB", c.x, c.y, 0.3, 0.42, 0.06, 10)
        flat_ring(m, "StoneLight", c.x, c.y, 0.32, 0.5, 0.12, 0.1, 10)
    flat_ring(m, "StoneLight", 0, 0, 0.32, 3.95, 0.28, 0.1, 24)
    flat_ring(m, "StoneLight", 0, 0, 0.32, 5.25, 0.3, 0.1, 24)
    for k in range(5):  # moss creeping over its edge
        a = rng.uniform(0, math.tau)
        obox(m, "Moss", (math.cos(a) * 5.3, math.sin(a) * 5.3, 0.3), (1.3, 0.7, 0.08), turn(z=a + math.pi / 2))
    return m


# ---------------------------------------------------------------------- rim props and landmarks


def thorn_tree(seed=12):
    """A rim prop: a black thorn tree, twisted and spiked, crimson blossoms glowing in clusters along its branches,
    glowing petals falling off it for ever and fireflies circling its crown."""
    m = prop("ThornTree", Bark=BARK, BarkDark=BARK_DARK, Petal=PETAL, PetalDark=PETAL_DARK, RoseGlow=ROSE, PetalGlow=ROSE, Motes=FIREFLY,
             Moss=MOSS_DARK, Leaf=LEAF_DARK)
    rng = random.Random(seed)
    trunk = [(0, 0, 0), (0.6, 0.2, 3.0), (-0.3, -0.1, 6.0), (0.4, 0.2, 9.0), (0.0, 0.0, 11.0)]
    thorn_vine(m, "Bark", trunk, 1.6, 0.6, rng, 1.0, 0.6)
    dome(m, "Moss", 0, 0, 0, 1.3)
    for k in range(5):
        a = k * math.tau / 5 + 0.4
        limb(m, "BarkDark", [(math.cos(a) * 0.5, math.sin(a) * 0.5, 1.6), (math.cos(a) * 1.7, math.sin(a) * 1.7, 0.7), (math.cos(a) * 2.7, math.sin(a) * 2.7, 0.05)],
             0.7, 0.3)

    def on_trunk(z):
        for p, q in zip(trunk, trunk[1:]):
            if p[2] <= z <= q[2]:
                t = (z - p[2]) / (q[2] - p[2])
                return tuple(a + (b - a) * t for a, b in zip(p, q))
        return trunk[-1]

    ends = []
    for k in range(7):
        a = k * math.tau / 7 + rng.uniform(-0.3, 0.3)
        z0, r = rng.uniform(5.0, 10.0), rng.uniform(3.8, 5.4)
        end = (math.cos(a) * r, math.sin(a) * r, z0 + rng.uniform(1.0, 3.0))
        thorn_vine(m, "Bark", [on_trunk(z0), (math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, z0 + 1.6), end], 0.5, 0.16, rng, 0.8, 0.4)
        ends.append(end)
    ends.append((0.0, 0.0, 11.4))
    for k, (x, y, z) in enumerate(ends):  # clusters of blossom
        for j in range(3):
            rose(m, (x + rng.uniform(-0.9, 0.9), y + rng.uniform(-0.9, 0.9), z + rng.uniform(-0.4, 0.8)), rng.uniform(0.5, 0.8),
                 turn(rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), 0))
        if k % 2 == 0:
            petal_column(m, "PetalGlow", x * 0.9, y * 0.9, 0.6, z - 0.8, 3.0, 0.45, rng)
    fireflies(m, rng, 14, 3.0, 6.5, 6.0, 13.5)
    return m


def turret(seed=13):
    """A rim prop: a round stone turret of the sleeping castle, briars climbing it, lit windows and arrow slits, a
    slate cone roof and a banner waving on the pole at its tip (the pole is straight above the origin)."""
    m = prop("Turret", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Roof=SLATE, Window=WINDOW, Bark=BARK, Petal=PETAL,
             PetalDark=PETAL_DARK, RoseGlow=ROSE, Leaf=LEAF_DARK, Iron=IRON, Banner=PETAL, Gold=GOLD, Moss=MOSS)
    rng = random.Random(seed)
    prism(m, "StoneDark", 0, 0, 0, 1.2, 2.9, 2.6, 12)
    prism(m, "Stone", 0, 0, 1.2, 9.6, 2.4, 2.25, 12)
    for z in (3.6, 6.6):
        prism(m, "StoneLight", 0, 0, z - 0.15, z + 0.15, 2.5, 2.5, 12)
    prism(m, "StoneLight", 0, 0, 9.6, 10.2, 2.7, 2.7, 12)
    for k in range(12):  # crenels
        a = (k + 0.5) * math.tau / 12
        if k % 2 == 0:
            obox(m, "Stone", (math.cos(a) * 2.5, math.sin(a) * 2.5, 10.55), (1.1, 0.5, 0.7), turn(z=a + math.pi / 2))
    cone_roof(m, "Roof", 0, 0, 10.2, 2.3, 4.8, 12)
    m.block("Iron", 0, 0, 15.6, 0.12, 0.12, 2.4)
    banner(m, "Banner", 0, 0.75, 16.7, 1.3, 1.0, along="y")
    ball(m, "Gold", 0, 0, 16.85, 0.16, 6, 3)
    for k, z in ((0, 5.1), (3, 8.0), (6, 5.4), (9, 2.6)):  # lit windows and arrow slits
        a = (k + 0.5) * math.tau / 12 + math.pi / 2
        r = 2.3 * math.cos(math.pi / 12) + 0.03
        obox(m, "Window", (math.cos(a) * r, math.sin(a) * r, z), (0.08, 0.7 if k % 2 == 0 else 0.25, 1.2), turn(z=a))
        obox(m, "StoneLight", (math.cos(a) * (r + 0.04), math.sin(a) * (r + 0.04), z + 0.7), (0.12, 0.9, 0.2), turn(z=a))
    pts = [(2.5 * math.cos(k * 0.75), 2.5 * math.sin(k * 0.75), 0.4 + k * 0.62) for k in range(13)]
    thorn_vine(m, "Bark", pts, 0.3, 0.16, rng, 0.7, 0.3)
    for k in (3, 7, 11):
        rose(m, tuple(Vector(pts[k]) * 1.08), 0.7, turn(y=0.5))
    m.block("Moss", 0, 2.3, 1.25, 1.6, 0.4, 0.14)
    return m


def sleeping_castle(seed=14):
    """A landmark for the rims: the sleeping castle. A keep with a tall middle tower, four round corner towers
    with slate cones, battlements, lit windows, a shut gate, and briars as thick as trees climbing it with roses
    glowing on them; a banner waves on three of its towers (each on its own middle)."""
    m = prop("SleepingCastle", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Roof=SLATE, Window=WINDOW, WoodDark=WOOD_DARK,
             Iron=IRON, Bark=BARK, BarkDark=BARK_DARK, Petal=PETAL, PetalDark=PETAL_DARK, RoseGlow=ROSE, Leaf=LEAF_DARK, Gold=GOLD,
             BannerA=PETAL, BannerB=PETAL, BannerC=PETAL, Moss=MOSS, Front="#ff00ff")
    rng = random.Random(seed)
    w, d, h = 14.0, 10.0, 11.0
    m.block("StoneDark", 0, 0, 0.6, w + 1.2, d + 1.2, 1.2)
    m.block("Stone", 0, 0, (1.2 + h) / 2, w, d, h - 1.2)
    m.block("StoneLight", 0, 0, h + 0.15, w + 0.4, d + 0.4, 0.3)
    crenels(m, "Stone", -w / 2, w / 2, d / 2, h + 0.3)
    crenels(m, "Stone", -w / 2, w / 2, -d / 2, h + 0.3)
    crenels(m, "Stone", -d / 2, d / 2, w / 2, h + 0.3, along="y")
    crenels(m, "Stone", -d / 2, d / 2, -w / 2, h + 0.3, along="y")
    # The gate, shut, and rows of lit windows.
    m.block("StoneLight", 0, d / 2 + 0.1, 3.4, 4.2, 0.3, 4.8)
    m.block("WoodDark", 0, d / 2 + 0.2, 3.0, 3.2, 0.2, 3.8)
    for x in (-0.8, 0.0, 0.8):
        m.block("Iron", x, d / 2 + 0.33, 3.0, 0.12, 0.08, 3.8)
    for x in (-5.0, -3.0, 3.0, 5.0):
        for z in (4.5, 8.0):
            m.block("Window", x, d / 2 + 0.05, z, 0.9, 0.1, 1.6)
            m.block("StoneLight", x, d / 2 + 0.1, z + 1.0, 1.2, 0.2, 0.25)
    # The towers: four round ones on the corners, a tall square one in the middle.
    banners = iter(("BannerA", "BannerB", "BannerC"))
    for k, (sx, sy) in enumerate(((1, 1), (-1, 1), (1, -1), (-1, -1))):
        x, y = sx * w / 2, sy * d / 2
        th = h + 4.0 + (1.0 if k % 2 else 0)
        prism(m, "Stone", x, y, 0, th, 2.3, 2.1, 12)
        prism(m, "StoneLight", x, y, th, th + 0.5, 2.5, 2.5, 12)
        cone_roof(m, "Roof", x, y, th + 0.5, 2.3, 4.6, 12)
        m.block("Window", x, y + 2.1, th - 2.0, 0.7, 0.1, 1.2)
        if k < 3:
            role = next(banners)
            m.block("Iron", x, y, th + 5.8, 0.12, 0.12, 2.6)
            banner(m, role, x, y + 0.7, th + 6.9, 1.2, 1.0, along="y")
    mh = h + 9.0
    m.block("Stone", 0, -1.0, (h + 0.3 + mh) / 2, 5.0, 5.0, mh - h - 0.3)
    m.block("StoneLight", 0, -1.0, mh + 0.2, 5.6, 5.6, 0.4)
    m.loft_z("Roof", (mh + 0.4, 0, -1.0, 5.2, 5.2), (mh + 6.5, 0, -1.0, 0.2, 0.2))
    for z in (h + 2.5, h + 6.0):
        m.block("Window", 0, 1.55, z, 1.0, 0.1, 1.8)
    # Briars as thick as trees, climbing it, roses glowing on them.
    for side in (-1, 1):
        pts = [(side * 9.5, 6.5, 0), (side * 7.6, 5.6, 4.0), (side * 5.5, 5.4, 7.5), (side * 3.0, 5.3, 10.2), (side * 1.5, 4.0, 13.5),
               (side * 0.6, 1.5, 15.5)]
        thorn_vine(m, "Bark" if side > 0 else "BarkDark", pts, 1.1, 0.4, rng, 1.2, 0.7)
        for k in (1, 3, 4):
            rose(m, tuple(Vector(pts[k]) + Vector((0, 0.6, 0.5))), 1.3, turn(x=-0.5))
    thorn_vine(m, "Bark", [(-8.5, -6.0, 0), (-7.2, -4.0, 6.0), (-6.8, -1.0, 12.0), (-7.0, 0.5, 15.5)], 0.9, 0.4, rng, 1.2, 0.6)
    m.block("Moss", 0, 0, h + 0.36, w - 1.0, d - 1.0, 0.1)
    m.block("Front", 0, 9, 1, 0.2, 0.2, 0.2)
    return m


def rose_tower(seed=15):
    """A landmark for the rims: a slender stone tower strangled by briars, crowned by a colossal rose in full bloom
    glowing at its heart, petals circling it slowly in the air and glowing buds along the briars."""
    m = prop("RoseTower", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Window=WINDOW, Bark=BARK, BarkDark=BARK_DARK, Leaf=LEAF,
             LeafDark=LEAF_DARK, Petal=PETAL, PetalDark=PETAL_DARK, RoseGlow=ROSE, Bud=BUD, PetalOrbit=PETAL, Front="#ff00ff")
    rng = random.Random(seed)
    prism(m, "StoneDark", 0, 0, 0, 1.4, 3.6, 3.2, 10)
    prism(m, "Stone", 0, 0, 1.4, 22.0, 2.2, 1.7, 10)
    for z in (6.0, 12.0, 18.0):
        prism(m, "StoneLight", 0, 0, z - 0.2, z + 0.2, 2.25 - z * 0.022, 2.25 - z * 0.022, 10)
    prism(m, "StoneLight", 0, 0, 22.0, 22.8, 2.4, 2.6, 10)
    for z in (9.0, 15.0):
        m.block("Window", 0, 2.0 - z * 0.02, z, 0.7, 0.1, 1.4)
    for k in range(3):  # briars spiralling up it
        pts = [(2.3 * math.cos(k * 2.1 + j * 0.55), 2.3 * math.sin(k * 2.1 + j * 0.55), j * 1.0) for j in range(23)]
        thorn_vine(m, "Bark" if k % 2 else "BarkDark", pts, 0.55, 0.3, rng, 0.9, 0.45)
        for j in (6, 12, 18):
            ball(m, "Bud", *(Vector(pts[j]) * 1.15), 0.32, 6, 4)
            p = Vector(pts[j])
            out = Vector((p.x, p.y, 0)).normalized()
            leaf(m, "Leaf" if j % 2 else "LeafDark", tuple(p), tuple(p + out * 1.5 + Vector((0, 0, -0.5))), (-out.y, out.x, 0.2), 0.8)
    rose(m, (0, 0.6, 25.0), 4.6, turn(x=-0.5))  # turned to face the corridor (its Front)
    for k in range(10):  # petals circling the bloom
        a = k * math.tau / 10
        r = 7.0 + (k % 3) * 0.8
        obox(m, "PetalOrbit", (math.cos(a) * r, math.sin(a) * r, 24.0 + (k % 4) * 1.1), (1.0, 0.8, 0.12), turn(0.4, 0.3, a))
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


def crooked_cottage(seed=16):
    """A landmark for the rims: a crooked half-timbered cottage leaning on its own chimney, a deep thatched roof,
    lit windows and a round door, smoke rising from the chimney, a weather vane turning on the ridge (straight
    above the origin) and roses round the door."""
    m = prop("CrookedCottage", Plaster="#d8ccb4", Beam=WOOD_DARK, Wood=WOOD, Thatch="#7a6640", ThatchDark="#5a4a2c", Stone=STONE, StoneDark=STONE_DARK,
             Window=WINDOW, Iron=IRON, Vane=IRON, Smoke="#8a8494", SmokeLight="#aaa4b2", Bark=BARK, Petal=PETAL, PetalDark=PETAL_DARK,
             RoseGlow=ROSE, Leaf=LEAF_DARK, Front="#ff00ff")
    rng = random.Random(seed)
    lean = turn(y=0.06)
    f = Frame(m, (0, 0, 0), lean)
    w, d, h = 8.0, 6.0, 5.5
    f.box("StoneDark", 0, 0, 0.4, w + 0.6, d + 0.6, 0.8)
    f.box("Plaster", 0, 0, 0.8 + h / 2, w, d, h)
    for x in (-w / 2, -1.3, 1.3, w / 2):  # timbers
        f.box("Beam", x, d / 2 + 0.06, 0.8 + h / 2, 0.3, 0.14, h)
    f.box("Beam", 0, d / 2 + 0.06, 0.8 + h * 0.55, w, 0.14, 0.3)
    for sx in (-1, 1):
        f.box("Window", sx * 2.6, d / 2 + 0.05, 0.8 + h * 0.62, 1.2, 0.1, 1.2)
        f.box("Beam", sx * 2.6, d / 2 + 0.12, 0.8 + h * 0.62, 0.1, 0.06, 1.2)
        f.box("Beam", sx * 2.6, d / 2 + 0.12, 0.8 + h * 0.62, 1.2, 0.06, 0.1)
    f.box("Wood", 0, d / 2 + 0.06, 0.8 + 1.4, 1.5, 0.12, 2.8)  # the door
    m.block("Iron", 0.5, d / 2 + 0.2, 2.2, 0.14, 0.1, 0.14)
    # The thatched roof, deep and sagging, with an eyebrow over the windows.
    top = 0.8 + h
    m.loft_y("Thatch", (-d / 2 - 1.0, 0.3, top + 0.5, w + 1.8, 1.2), (0, 0.3, top + 3.8, w + 1.8, 0.8))
    m.loft_y("Thatch", (0, 0.3, top + 3.8, w + 1.8, 0.8), (d / 2 + 1.0, 0.3, top + 0.5, w + 1.8, 1.2))
    m.loft_y("ThatchDark", (-d / 2 - 1.05, 0.3, top + 0.1, w + 1.9, 0.4), (d / 2 + 1.05, 0.3, top + 0.1, w + 1.9, 0.4))
    # The chimney, leaning the other way, and its smoke.
    m.loft_z("Stone", (0, -w / 2 - 0.6, -1.0, 1.8, 1.8), (top + 4.5, -w / 2 - 0.2, -1.0, 1.3, 1.3))
    m.block("StoneDark", -w / 2 - 0.2, -1.0, top + 4.7, 1.6, 1.6, 0.4)
    puffs(m, "Smoke", -w / 2 - 0.2, -1.0, top + 5.8, 4, 1.6, 1.0, grow=0.15, shade="SmokeLight")
    # The weather vane on the ridge, turning round its rod.
    m.block("Iron", 0, 0, top + 4.6, 0.12, 0.12, 1.8)
    m.block("Vane", 0, -0.3, top + 5.3, 0.1, 2.0, 0.14)
    m.loft_y("Vane", (0.6, 0, top + 5.3, 0.1, 0.6), (1.1, 0, top + 5.3, 0.1, 0.04))
    plate(m, "Vane", (0, -0.9, top + 5.3), (0, -1.5, top + 5.6), (0, 0, 1), 0.8, 0.5, 0.06)
    # Roses round the door.
    for sx in (-1, 1):
        thorn_vine(m, "Bark", [(sx * 1.2, d / 2 + 0.4, 0.8), (sx * 1.0, d / 2 + 0.45, 2.6), (sx * 0.4, d / 2 + 0.45, 3.9)], 0.18, 0.12, rng, 0.5, 0.2)
        rose(m, (sx * 1.05, d / 2 + 0.6, 2.7), 0.55, turn(x=-1.0))
    m.block("Front", 0, 7, 1, 0.2, 0.2, 0.2)
    return m


MOON_ROLES = ("Lunar", "Crater", "Bark", "Leaf", "Petal", "PetalDark", "RoseGlow")


def thorn_moon(seed=17):
    """The sky piece: a huge pale moon hanging beyond the island, a briar wound round it with roses glowing on it,
    and ravens circling it; the whole of it rises and sinks slowly. It starts high above the ground and faces +Y,
    so it only has to face along the corridor. The ravens circle the origin's upright."""
    m = prop("ThornMoon", Lunar="#d6cdae", Crater="#a89f86", Bark=BARK, Leaf=LEAF_DARK, Petal=PETAL, PetalDark=PETAL_DARK, RoseGlow=ROSE,
             Raven="#141118", Front="#ff00ff")
    rng = random.Random(seed)
    zc, r = 52.0, 7.0
    ball(m, "Lunar", 0, 0, zc, r, 14, 9)
    for x, z, cr in ((-2.5, 2.0, 1.5), (2.6, -1.2, 1.1), (0.4, -3.6, 0.9), (-3.4, -2.6, 0.8), (3.0, 3.4, 0.7), (0.0, 0.6, 0.6)):
        y = math.sqrt(max(0.0, r * r - x * x - z * z))
        disc(m, "Crater", x, y - 0.05, zc + z, cr, 0.25, 10, "xz")
    tilt = turn(x=1.2, y=0.35)
    pts = [tuple(Vector((0, 0, zc)) + tilt @ Vector((math.cos(a) * (r + 0.6), math.sin(a) * (r + 0.6), 0)))
           for a in (k * math.tau / 18 for k in range(19))]
    thorn_vine(m, "Bark", pts, 0.6, 0.6, rng, 1.2, 0.5)
    for k in (2, 7, 12, 16):
        rose(m, pts[k], 1.2, tilt)
        leaf(m, "Leaf", pts[k + 1], tuple(Vector(pts[k + 1]) * 1.0 + tilt @ Vector((0, 0, 1.6))), tuple(tilt @ Vector((1, 0, 0))), 0.9)
    for k in range(5):  # ravens circling it
        a = k * math.tau / 5 + 2.2 + rng.uniform(-0.2, 0.2)  # none starts right in front of the moon
        rr = rng.uniform(10.5, 12.5)
        f = Frame(m, (math.cos(a) * rr, math.sin(a) * rr, zc + rng.uniform(-3.5, 3.5)), turn(z=a + math.pi / 2))
        f.box("Raven", 0, 0, 0, 0.5, 1.3, 0.5)
        f.box("Raven", 0, 0.8, 0.15, 0.35, 0.4, 0.35)
        f.beam("Raven", (0, 1.0, 0.15), (0, 1.35, 0.05), 0.12, None, 0.02)
        for s in (-1, 1):
            f.box("Raven", s * 0.9, 0.1, 0.25, 1.5, 0.6, 0.08, turn(y=s * 0.35))
        f.box("Raven", 0, -0.85, 0, 0.5, 0.6, 0.08)
    m.block("Front", 0, 12, zc, 0.2, 0.2, 0.2)
    return m


def briar_curtain(seed=18):
    """Briars as thick as an arm spilling over the wall's top edge from a tangle on the rim and hanging down the
    wall to the floor, roses glowing along them and glowing petals falling past them for ever. Origin on the wall's
    top inner edge: rim z 0, floor z -44, +Y out into the corridor. The Front part tells the game which way it
    faces, then it goes."""
    m = prop("BriarCurtain", Bark=BARK, BarkDark=BARK_DARK, Leaf=LEAF, LeafDark=LEAF_DARK, Petal=PETAL, PetalDark=PETAL_DARK, RoseGlow=ROSE,
             PetalGlow=ROSE, Moss=MOSS, Front="#ff00ff")
    rng = random.Random(seed)
    dome(m, "Moss", 0, -3.5, 0, 1.8)
    for k, x0 in enumerate((-2.2, 0.2, 2.4)):
        pts = [(x0 * 0.6, -4.0, 1.2), (x0 * 0.8, -1.5, 2.4), (x0, 1.2, 1.0), (x0 + 0.3, 2.2, -2.0)]
        z = -2.0
        while z > -42.0:
            z -= rng.uniform(4.5, 6.5)
            pts.append((x0 + rng.uniform(-0.9, 0.9), rng.uniform(2.0, 2.6), max(z, -43.6)))
        thorn_vine(m, "Bark" if k % 2 else "BarkDark", pts, 0.55, 0.3, rng, 1.0, 0.45)
        for j, p in enumerate(pts[3:]):
            if j % 2 == 0:
                rose(m, (p[0] + 0.3, p[1] + 0.6, p[2]), 0.9, turn(x=-1.2))
            else:
                leaf(m, "Leaf" if j % 4 == 1 else "LeafDark", p, (p[0] + 1.2, p[1] + 0.8, p[2] - 0.4), (0, 0, 1), 0.7)
    for x in (-1.2, 1.0, 3.2):  # petals falling past it, 4 apart
        petal_column(m, "PetalGlow", x, 3.4, -43.0, -2.0, 4.0, 0.5, rng)
    for k in range(9):  # fallen petals at its foot
        a, rr = rng.uniform(0, math.pi), rng.uniform(1.0, 5.0)
        obox(m, "Petal" if k % 2 else "PetalDark", (math.cos(a) * rr, 2.5 + math.sin(a) * rr, -43.95), (0.6, 0.45, 0.06), turn(z=rng.uniform(0, math.tau)))
    dome(m, "Moss", 0.0, 3.0, -44.0, 1.2)
    m.block("Front", 0, 6, -20, 0.2, 0.2, 0.2)
    return m


def stone_bridge(seed=19):
    """Two stone towers on the rims and a stone bridge across the corridor on a great arch, battlements along its
    deck, crimson banners hanging from both its faces and swinging slowly along the corridor, lamps lit on the
    towers and briars climbing them. Modelled for the 72-wide corridor (feet beyond 36 from the middle); MapDecor
    stretches it to the real width. All of it stays above the rim (z 0), clear of the flight camera; the banners
    hang from the X line at the deck's underside, so they swing round it."""
    m = prop("StoneBridge", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Banner=PETAL, Window=WINDOW, Lamp=LAMP, Iron=IRON,
             Bark=BARK, Petal=PETAL, PetalDark=PETAL_DARK, RoseGlow=ROSE, Leaf=LEAF_DARK, Moss=MOSS, Front="#ff00ff")
    rng = random.Random(seed)
    deck = 17.0
    for sx in (-1, 1):
        x = sx * 40
        m.block("StoneDark", x, 0, 0.75, 6.6, 6.0, 1.5)
        m.loft_z("Stone", (1.5, x, 0, 5.0, 4.6), (deck + 3.0, x, 0, 4.2, 4.0))
        for z in (6.0, 12.0):
            m.block("StoneLight", x, 0, z, 4.9 - z * 0.04, 4.5 - z * 0.03, 0.4)
        m.block("StoneLight", x, 0, deck + 3.2, 4.8, 4.6, 0.4)
        crenels(m, "Stone", x - 2.0, x + 2.0, 2.0, deck + 3.4, 0.8, 0.8, 0.6)
        crenels(m, "Stone", x - 2.0, x + 2.0, -2.0, deck + 3.4, 0.8, 0.8, 0.6)
        for y in (2.12, -2.12):
            m.block("Window", x, y, 9.0, 0.8, 0.1, 1.5)
        for y in (2.5, -2.5):  # lamps on brackets
            m.block("Iron", x - sx * 1.6, y * 1.02, deck + 1.0, 0.5, 0.5, 0.12)
            m.block("Lamp", x - sx * 1.6, y * 1.02, deck + 0.6, 0.4, 0.4, 0.7)
        pts = [(x + sx * 2.2, 2.6, 0.2), (x + sx * 1.5, 2.6, 5.0), (x - sx * 1.6, 2.5, 9.0), (x - sx * 1.2, 2.5, 14.0)]
        thorn_vine(m, "Bark", pts, 0.5, 0.25, rng, 0.9, 0.4)
        rose(m, (x - sx * 1.6, 3.0, 9.6), 1.0, turn(x=-1.0))
    # The deck and its battlements.
    m.block("Stone", 0, 0, deck + 0.8, 76.0, 4.4, 1.6)
    m.block("StoneLight", 0, 0, deck + 1.7, 76.4, 4.6, 0.2)
    for y in (2.0, -2.0):
        crenels(m, "Stone", -37.0, 37.0, y, deck + 1.8, 0.9, 0.8, 0.5)
    # The arch under it: stones along a half-ellipse from the towers' sides up to the deck.
    a_, b_, z0 = 38.0, 8.5, 8.0
    n = 36
    for i in range(n):
        t0, t1 = math.pi * i / n, math.pi * (i + 1) / n
        p = Vector((a_ * math.cos(t0), 0, z0 + b_ * math.sin(t0)))
        q = Vector((a_ * math.cos(t1), 0, z0 + b_ * math.sin(t1)))
        mid, along = (p + q) / 2, q - p
        obox(m, "StoneLight" if i % 2 else "Stone", tuple(mid), (along.length + 0.25, 3.2, 1.5), turn(y=-math.atan2(along.z, along.x)))
    for sx in (-1, 1):  # spandrels filling in near the towers
        for k, (x, h) in enumerate(((36.0, 9.0), (32.0, 5.5), (28.0, 3.2))):
            m.block("Stone", sx * x, 0, deck - h / 2, 4.0, 3.0, h)
    # Banners from both faces of the deck.
    for x in (-24.0, -8.0, 8.0, 24.0):
        for y in (2.4, -2.4):
            banner(m, "Banner", x, y, deck, 2.2, 4.6)
    m.block("Moss", 0, 0, deck + 1.83, 70.0, 3.6, 0.06)
    m.block("Front", 0, 6, deck + 4, 0.2, 0.2, 0.2)
    return m


ALL = [briar_rose, thorn_thicket, stone_knight, spinning_wheel, briar_lantern, toadstools, rose_fountain, magic_mirror, floating_crown,
       briar_tuft, rose_window, thorn_tree, turret, sleeping_castle, rose_tower, crooked_cottage, thorn_moon, briar_curtain, stone_bridge]

# What moves. The game reads the same numbers from shared/Config/PropMotion.luau. Kinds of move:
#   spin  degrees a second; swing  degrees each way, over period seconds; bob  studs up and down over period;
#   pulse  the glow dims to this share and back over period; fall  drops this far over period, then starts again
#   (negative rises).
# spin and swing turn round axis "up" (default), "across" (the model's X) or "ahead" (its Y), through the part's
# own middle (about="self") or a point `height` studs straight above the prop's origin (the default).
_ROSE = dict(pulse=0.6, period=3.2)
_KNIGHT = dict(swing=12, period=2.4, axis="across", height=5.25)
_POST = dict(swing=10, period=2.8, axis="across", height=8.1)
_CROWN = dict(spin=20, bob=0.3, period=3)
_SMOKE = dict(fall=-1.6, period=1.6)
_FLOAT = dict(bob=1.0, period=9)
_BRIDGE = dict(swing=7, period=3.2, axis="across", height=17)
MOTION = {
    "prop_BriarRose": {"PetalGlow": dict(fall=3, period=2.6), "RoseGlow": dict(_ROSE), "Bud": dict(pulse=0.4, period=2.2)},
    "prop_ThornThicket": {"Motes": dict(spin=18, bob=0.4, period=3.5), "RoseGlow": dict(pulse=0.55, period=2.8)},
    "prop_StoneKnight": {"Chain": dict(_KNIGHT), "Lantern": dict(_KNIGHT), "Lamp": dict(_KNIGHT, pulse=0.7), "Gaze": dict(pulse=0.3, period=4),
                         "RoseGlow": dict(_ROSE)},
    "prop_SpinningWheel": {"Wheel": dict(spin=40, axis="ahead", about="self"), "Thread": dict(pulse=0.6, period=2.6)},
    "prop_BriarLantern": {"Chain": dict(_POST), "Lantern": dict(_POST), "Lamp": dict(_POST, pulse=0.7), "Motes": dict(spin=20, bob=0.5, period=4),
                          "RoseGlow": dict(_ROSE)},
    "prop_Toadstools": {"Glow": dict(pulse=0.5, period=3), "Motes": dict(spin=24, bob=0.4, period=3), "Window": dict(pulse=0.8, period=2.5)},
    "prop_RoseFountain": {"Falling": dict(fall=1.2, period=0.5), "Stream": dict(pulse=0.75, period=3)},
    "prop_MagicMirror": {"MirrorGlow": dict(pulse=0.55, period=3.6), "Gaze": dict(pulse=0.05, period=5), "Motes": dict(spin=30, bob=0.3, period=3),
                         "CrownGem": dict(pulse=0.5, period=2)},
    "prop_FloatingCrown": {"Crown": dict(_CROWN), "CrownGem": dict(_CROWN), "Motes": dict(spin=-20, bob=0.3, period=3)},
    "prop_BriarTuft": {"Bud": dict(pulse=0.4, period=2.4)},
    "prop_RoseWindow": {"Pane": dict(pulse=0.55, period=3.4), "PaneB": dict(pulse=0.6, period=4.4)},
    "prop_ThornTree": {"PetalGlow": dict(fall=3, period=2.8), "RoseGlow": dict(_ROSE), "Motes": dict(spin=14, bob=0.5, period=4)},
    "prop_Turret": {"Banner": dict(swing=25, period=3), "Window": dict(pulse=0.8, period=3.2), "RoseGlow": dict(_ROSE)},
    "prop_SleepingCastle": {"BannerA": dict(swing=10, period=3, about="self"), "BannerB": dict(swing=10, period=3.4, about="self"),
                            "BannerC": dict(swing=10, period=2.7, about="self"), "Window": dict(pulse=0.8, period=3.5), "RoseGlow": dict(_ROSE)},
    "prop_RoseTower": {"PetalOrbit": dict(spin=10, bob=0.6, period=5), "RoseGlow": dict(pulse=0.65, period=3.6), "Bud": dict(pulse=0.4, period=2.4),
                       "Window": dict(pulse=0.8, period=3)},
    "prop_CrookedCottage": {"Smoke": dict(_SMOKE), "SmokeLight": dict(_SMOKE), "Vane": dict(swing=35, period=7), "Window": dict(pulse=0.8, period=2.6),
                            "RoseGlow": dict(_ROSE)},
    "prop_ThornMoon": {**{role: dict(_FLOAT) for role in MOON_ROLES}, "Raven": dict(spin=12, **_FLOAT)},
    "prop_BriarCurtain": {"PetalGlow": dict(fall=4, period=1.4), "RoseGlow": dict(pulse=0.6, period=3)},
    "prop_StoneBridge": {"Banner": dict(_BRIDGE), "Lamp": dict(pulse=0.7, period=2.6), "Window": dict(pulse=0.8, period=3.4)},
}

# Where the props go: the same rules as Config/Decor's ThornKingdom (keep the two in step). The map is 1600 long.
DECOR = dict(
    floor=dict(first=12, gap=(12, 22), side=(24, 34),
               props=[("prop_BriarRose", 14, (1.3, 1.7)), ("prop_ThornThicket", 10, (1.1, 1.4)), ("prop_BriarLantern", 9, (1.2, 1.5)),
                      ("prop_Toadstools", 9, (1.2, 1.6)), ("prop_StoneKnight", 8, (1.2, 1.5)), ("prop_SpinningWheel", 7, (1.2, 1.5)),
                      ("prop_RoseFountain", 7, (1.1, 1.4)), ("prop_FloatingCrown", 5, (1.2, 1.4)), ("prop_MagicMirror", 4, (1.2, 1.4))],
               extras=dict(chance=0.7, spread=8, props=[("prop_BriarTuft", 5, (0.9, 1.3)), ("prop_Toadstools", 2, (0.6, 0.8)),
                                                         ("prop_ThornThicket", 2, (0.5, 0.7))])),
    rim=dict(first=6, gap=(14, 24), chance=0.9, side=(64, 102),
             props=[("prop_ThornTree", 6, (1.8, 2.4)), ("prop_Turret", 3, (1.6, 2.0)), ("prop_BriarRose", 4, (2.0, 2.6)),
                    ("prop_ThornThicket", 3, (2.0, 2.5)), ("prop_BriarTuft", 2, (2.2, 2.8))]),
    overhead=[("prop_StoneBridge", 270, 0, 1), ("prop_StoneBridge", 830, 0, 1.05), ("prop_StoneBridge", 1390, 0, 1)],
    walls=[("prop_BriarCurtain", d, side) for d, side in ((80, 1), (260, -1), (450, 1), (640, -1), (820, 1), (1000, -1), (1180, 1),
                                                          (1370, -1), (1540, 1))],
    spots=[("prop_SleepingCastle", 100, -88, "rim", 0, 1.4, "middle"), ("prop_SleepingCastle", 660, 88, "rim", 0, 1.5, "middle"),
           ("prop_SleepingCastle", 1220, -88, "rim", 0, 1.4, "middle"),
           ("prop_RoseTower", 230, 86, "rim", 0, 1.3, "middle"), ("prop_RoseTower", 790, -86, "rim", 0, 1.4, "middle"),
           ("prop_RoseTower", 1350, 86, "rim", 0, 1.3, "middle"),
           ("prop_CrookedCottage", 420, -84, "rim", 0, 1.4, "middle"), ("prop_CrookedCottage", 960, 84, "rim", 0, 1.5, "middle"),
           ("prop_CrookedCottage", 1520, -84, "rim", 0, 1.4, "middle"),
           ("prop_ThornMoon", 340, -180, "rim", 0, 2.2, "along"), ("prop_ThornMoon", 1100, 185, "rim", 0, 2.4, "along")]
          + [("prop_RoseWindow", d, x, "floor", yaw, 1.2) for d, x, yaw in ((40, -3, 20), (155, 4, 140), (270, -4, 70), (385, 3, 200),
                                                                              (500, -2, 300), (615, 4, 40), (735, -3, 110), (850, 2, 250),
                                                                              (965, -4, 330), (1085, 3, 80), (1205, -2, 160),
                                                                              (1325, 4, 10), (1445, -3, 230), (1560, 2, 120))],
)


# ---------------------------------------------------------------------- light


def kingdom_light(scene):
    """Night in the sleeping kingdom for the renders: cool moonlight and a mauve fill, close to the game's
    Config/Lighting look for this world."""
    sun = bpy.data.objects["Sun"]
    sun.data.energy = 1.5
    sun.data.color = (0.86, 0.84, 1.0)
    sun.rotation_euler = (math.radians(-58), math.radians(25), math.radians(30))
    ambient = scene.world.node_tree.nodes["Background"]
    ambient.inputs["Color"].default_value = (0.66, 0.62, 0.76, 1)
    ambient.inputs["Strength"].default_value = 0.72


# ---------------------------------------------------------------------- scene and renders

BIG = {"prop_SleepingCastle": (-95, -125, 0), "prop_RoseTower": (-55, -120, 0), "prop_CrookedCottage": (-20, -118, 0),
       "prop_ThornTree": (14, -112, 0), "prop_Turret": (36, -112, 0), "prop_ThornMoon": (40, -230, 0), "prop_BriarCurtain": (110, -110, 44),
       "prop_StoneBridge": (200, -170, 0)}


def main(stills=True, videos=True):
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    props = bpy.data.collections.new("Props")
    stage = bpy.data.collections.new("Preview stage")
    for col in (props, stage):
        scene.collection.children.link(col)

    models = [make() for make in ALL]
    built, roots = {}, []
    x = 40
    for model in models:
        root = model.build(props)
        if model.name in BIG:
            root.location = BIG[model.name]
        else:
            root.location = (x, -40, 0)
            x += 15
        built[model.name] = root
        roots.append(root)
    row_middle = (40 + x - 15) / 2
    mk.light_up(roots, GLOW_ROLES)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-400, -500, -0.01), (500, -500, -0.01), (500, 200, -0.01), (-400, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", CORRIDOR["FloorA"], False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = mk.player_block(stage)
    stars = mk.star_dome(stage, count=150, colours=("#ffffff", "#ffe0ea"))
    bpy.context.view_layer.update()
    mk.set_sky(scene, SKY)
    kingdom_light(scene)

    everything = roots + [player]
    if stills:
        for model, root in zip(models, roots):
            name = model.name
            if name == "prop_StoneBridge":
                mk.shoot_prop(scene, name, root, player, everything, (-0.15, 1.0, 0.25), 0.95, (1400, 700), 32)
            elif name == "prop_BriarCurtain":
                mk.shoot_prop(scene, name, root, player, everything, (0.6, 1.0, 0.1), 0.9, (700, 900), 40)
            elif name == "prop_ThornMoon":
                mk.shoot_prop(scene, name, root, player, everything, (0.3, 1.0, -0.05), 0.9, (800, 800), 50)
            elif name in ("prop_SleepingCastle", "prop_RoseTower", "prop_CrookedCottage"):
                mk.shoot_prop(scene, name, root, player, everything, (0.5, 0.95, 0.35), 1.15, (800, 800), 50)
            else:
                mk.shoot_prop(scene, name, root, player, everything)
        player.location = (30, -40, 0)
        bpy.context.view_layer.update()
        small = [r for r in roots if mk.prop_of(r) not in BIG]
        mk.set_visible(everything, small + [player])
        kit.shoot(scene, "props", (row_middle, 40, 30), (row_middle, -40, 5), (1800, 700), 18)
        landmarks = [built[n] for n in ("prop_SleepingCastle", "prop_RoseTower", "prop_CrookedCottage", "prop_ThornTree", "prop_Turret")]
        mk.set_visible(everything, landmarks + [player])
        player.location = (-25, -96, 0)
        bpy.context.view_layer.update()
        kit.shoot(scene, "landmarks", (-25, -8, 36), (-25, -120, 16), (1800, 800), 20)

    if videos:  # close up on what moves
        names = ("prop_BriarRose", "prop_StoneKnight", "prop_SpinningWheel", "prop_BriarLantern", "prop_Toadstools", "prop_RoseFountain",
                 "prop_MagicMirror", "prop_FloatingCrown", "prop_ThornTree", "prop_Turret", "prop_RoseTower", "prop_CrookedCottage", "prop_ThornMoon")
        movers = [built[n] for n in names]
        mk.set_visible(everything, movers)
        saved = [(r, r.location.copy()) for r in movers]
        for k, root in enumerate(movers[:8]):
            root.location = (k * 12.5 - 44, 0, 0)
        for k, root in enumerate(movers[8:12]):
            root.location = ((k - 1.5) * 38, -50, 0)
        movers[12].location = (0, -160, -14)
        bpy.context.view_layer.update()
        entries = mk.motion_entries(movers, MOTION)
        mk.render_video(scene, RENDERS, "thorn_motion", 120, 15,
                        lambda f: ((0, 66, 32), (0, -22, 11), 26, lambda t: mk.apply_motion(entries, t)), (1600, 800))
        mk.reset_motion(entries)
        for root, loc in saved:
            root.location = loc

    ground.hide_render = True
    mk.set_visible(everything, [])
    corridor = mk.corridor_stage(stage, CORRIDOR, length=600)
    copies = mk.decorate_stage(stage, built, DECOR, length=600)
    if stills:
        kit.shoot(scene, "corridor_flight", (0, 30, 30), (0, -160, 10), (1600, 900), 22)
        kit.shoot(scene, "corridor_high", (0, 40, 80), (0, -170, 20), (1600, 900), 22)
        kit.shoot(scene, "corridor_floor", (-16, -50, 10), (8, -170, 9), (1600, 900), 22)
        kit.shoot(scene, "corridor_rim", (-40, 20, 90), (50, -160, 44), (1600, 900), 24)
    if videos:  # down the corridor at the flight camera's height (14 over an egg that flies up to 18 high)
        entries = mk.motion_entries(copies, MOTION)
        frames = 150

        def fly(f):
            t = f / (frames - 1)
            y = 30 - 360 * t
            return (0, y, 28 + 4 * math.sin(t * math.pi)), (0, y - 70, 15), 22, lambda s: mk.apply_motion(entries, s)

        mk.render_video(scene, RENDERS, "thorn_flight", frames, 15, fly, (1600, 900))
        mk.reset_motion(entries)

    mk.clear([corridor, stars] + copies)
    mk.light_up(roots, GLOW_ROLES, 0)
    ground.hide_render = False
    for root in roots:
        for child in root.children:
            child.hide_render = False
    player.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "thorn_kingdom_models.blend"))
    print("saved", HERE / "thorn_kingdom_models.blend")
    for model in models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    # After "--": "stills" renders only the stills, "videos" only the videos; nothing, both.
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(stills=not args or "stills" in args, videos=not args or "videos" in args)
