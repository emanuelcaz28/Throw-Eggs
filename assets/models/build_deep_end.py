"""Builds The Deep End's props and renders them (Blender, background mode). It has no monsters of its own.

    Blender -b -P build_deep_end.py              (stills and videos)
    Blender -b -P build_deep_end.py -- stills    (stills only, quicker while modelling)

Saves deep_end_models.blend and renders to design/world/models_deep_end/.

The Deep End, world 16, the game's endgame (docs/RETENTION_PLAN.md step 3): what's behind the Last Door. Every egg strong
enough bursts through the door at the end of The Weeping Dark and comes out at the bottom of a colossal shaft. After the
blackest world in the game it's a shock of colour: mint light seeping out of the rock, on teal stone and old bone.

Something giant fell down here long ago, and its ribs and teeth are still lying on the floor. Whoever came after it
measured how far down it goes: Depth Gauges, the world's signature, stand all over the floor, each with a marker that
never stops sinking and rising. Chains as thick as a player hang from somewhere too high to see. At the very end of
the corridor the shaft's bottom stares back: the Bottom Face, a wall of angry stone with mint eyes and a jaw that slowly
works. Throws past a certain depth all land in front of it, so it's what the best players see the most.

Floor: Depth Gauges, giant ribs, stone fangs with glowing tips, fallen blocks split by light, hanging chains and now and
then a titan's tooth; glow moss as filler, and seep pools lying flat across the middle. Rims: rock spires. Landmarks: carved
shaft columns and titan skulls. Mint seeps run down the walls and chain spans cross overhead.

No pentagrams, hexagrams or crosses (kids' game). No stud texture in this file, as for every map from 10 on: studs come
only in Studio. What moves is MOTION below, the same numbers as shared/Config/PropMotion.luau. Glowing roles must also
be in shared/Roles.luau. LIGHTS is Config/Decor's propLights.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import map_kit as mk  # noqa: E402
from build_weeping_dark import drops, link_chain, pool  # noqa: E402
from map_kit import ball, beam, flat_ring, gem, kit, limb, prism  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "models_deep_end"

# Roles lit from inside. The game makes them Neon (shared/Roles.luau), so add new ones there too.
GLOW_ROLES = {"GaugeTick", "GaugeMark", "FangTip", "SeamGlow", "DeepSpore", "SeepRing", "ColumnRing", "DeepEye", "SeepFall", "SeepDrop"}
kit.NO_STUDS.update(GLOW_ROLES)
mk.GLOW_STRENGTH = 2.4

ROCK, ROCK_DARK, ROCK_LIGHT = "#3a5a5c", "#22383c", "#5f8280"
CUT, CUT_DARK = "#7c8f86", "#556a64"
BONE, BONE_DARK = "#ddd6bd", "#a59e86"
IRON, IRON_DARK = "#3a4448", "#23292c"
MOSS = "#1f6a58"
HOLE = "#0a1416"
WATER = "#0f3f42"
MINT, MINT_SOFT, MINT_DIM = "#8ff8e0", "#c8fff2", "#3fae9c"

# The corridor's colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#2c5654", "FloorB": "#274e4c", "Dirt": "#2e4e50", "DirtB": "#284648", "Grass": "#a8ae96"}
SKY = "#0d2226"

FACE_FRONT = 26  # the Bottom Face's front, from its origin
FACE_AT = 1526  # where that front stands, from the world's start: 26 short of the end wall, like the Last Door's
JAW_REST = -30  # the middle of the Bottom Face's jaw, on its Z


def prop(name, **colours):
    return mk.prop(name, **colours)


# ---------------------------------------------------------------------- floor props


def depth_gauge(seed=1):
    """The map's signature: a tall cut-stone post marked off like a ruler, with a glowing marker that sinks and rises for
    ever. Someone measured this place, and never found the bottom."""
    m = prop("DepthGauge", Cut=CUT, CutDark=CUT_DARK, Rubble=ROCK_DARK, GaugeTick=MINT_DIM, GaugeMark=MINT_SOFT, Band=IRON)
    rng = random.Random(seed)
    m.loft_z("Rubble", (0, 0, 0, 7, 7), (0.8, 0, 0, 5.2, 5.2))
    m.block("CutDark", 0, 0, 1.2, 4.2, 4.2, 1.0)
    m.loft_z("Cut", (1.6, 0, 0, 2.6, 2.6), (15.4, 0, 0, 2.0, 2.0))
    m.block("CutDark", 0, 0, 16.0, 3.0, 3.0, 1.2)
    gem(m, "Cut", 0, 0, 17.2, 1.3, 1.6, 0.6, 4, math.pi / 4)
    for k in range(13):
        z = 2.6 + k
        wide = 1.9 if k % 4 == 0 else 1.1
        for y in (1.3, -1.3):
            m.block("GaugeTick", 0, y - 0.05 * (k / 12) * (1 if y > 0 else -1), z, wide, 0.16, 0.2)
    for z in (5.0, 10.0, 15.0):
        m.block("Band", 0, 0, z, 2.9 - z * 0.04, 2.9 - z * 0.04, 0.3)
    m.block("GaugeMark", 0, 1.65, 8.6, 3.2, 0.5, 0.6)
    m.block("GaugeMark", 0, -1.65, 8.6, 3.2, 0.5, 0.6)
    for _ in range(5):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(3.2, 4.4)
        m.block("Rubble", math.cos(a) * d, math.sin(a) * d, 0.35, rng.uniform(0.6, 1.3), rng.uniform(0.6, 1.3), 0.7)
    return m


def giant_rib(seed=2):
    """Three pairs of ribs from something that fell here, curving up out of the floor and nearly meeting overhead."""
    m = prop("GiantRib", Bone=BONE, BoneDark=BONE_DARK, Moss=MOSS, Rubble=ROCK_DARK)
    rng = random.Random(seed)
    for k, y in enumerate((-7, 0, 7)):
        h = 13.5 - abs(k - 1) * 1.8
        for s in (-1, 1):
            limb(m, "Bone", [(s * 8.2, y, 0), (s * 9.2, y, h * 0.35), (s * 7.4, y + 0.3, h * 0.75), (s * 2.4, y + 0.6, h)], 1.6, 0.55)
            m.loft_z("BoneDark", (0, s * 8.2, y, 2.6, 2.6), (1.0, s * 8.4, y, 1.9, 1.9))
            m.block("Moss", s * 8.4, y, 0.12, rng.uniform(3, 4.4), rng.uniform(2.4, 3.6), 0.24)
    beam(m, "BoneDark", (0, -10, 0.8), (0, 10, 1.1), 1.4, 1.2, 1.0)
    for y in (-3.5, 3.5):
        m.block("Rubble", rng.uniform(-3, 3), y, 0.4, 1.6, 1.3, 0.8)
    return m


def stone_fang(seed=3):
    """A cluster of stone teeth growing out of the floor, each with a glowing tip."""
    m = prop("StoneFang", Rock=ROCK, RockDark=ROCK_DARK, FangTip=MINT)
    rng = random.Random(seed)
    m.loft_z("RockDark", (0, 0, 0, 8, 7), (1, 0, 0, 6, 5.4))
    for x, y, h, r in ((0, 0, 11, 2.0), (2.7, 1.1, 7.4, 1.4), (-2.5, 0.8, 8.4, 1.5), (0.9, -2.3, 6, 1.2), (-1.4, -2.0, 4.6, 1.0)):
        lean = (rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8))
        prism(m, "Rock", x, y, 0.4, h, r, 0.34, 6, rng.uniform(0, 1), lean=lean)
        gem(m, "FangTip", x + lean[0], y + lean[1], h + 0.1, 0.42, 1.1, 0.6, 5)
    return m


def fallen_block(seed=4):
    """A huge cut block that came down from above and split on landing, with light coming out of the crack."""
    m = prop("FallenBlock", Cut=CUT, CutDark=CUT_DARK, SeamGlow=MINT, Rubble=ROCK_DARK, Moss=MOSS)
    rng = random.Random(seed)
    m.block("Cut", -3.2, 0, 3.0, 6.0, 8.6, 6.0)
    m.block("CutDark", 3.3, 0.4, 2.5, 6.0, 8.0, 5.0)
    m.block("SeamGlow", 0.05, 0.2, 2.6, 0.7, 7.6, 5.0)
    m.block("CutDark", -3.2, 0, 6.2, 6.3, 8.9, 0.5)
    m.block("Moss", -3.4, 0.4, 6.56, 4.6, 5.6, 0.2)
    for k in range(4):
        m.block("SeamGlow", -6.26, -3 + k * 2, 3.4, 0.08, 1.0, 0.24)
    for _ in range(6):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(6.4, 8.6)
        m.block("Rubble", math.cos(a) * d, math.sin(a) * d, 0.5, rng.uniform(0.8, 1.8), rng.uniform(0.8, 1.8), 1.0)
    return m


def hanging_chain(seed=5):
    """A chain as thick as a player, coming down from too high to see and ending in a great broken shackle. It swings
    very slowly. Nothing pulls it, which is the worrying part."""
    m = prop("HangingChain", Links=IRON, Shackle=IRON_DARK, Rubble=ROCK_DARK)
    link_chain(m, "Links", (0, 0, 40), (0, 0, 5.0), 11, 1.5)
    m.block("Shackle", 0, 0, 4.2, 4.2, 2.2, 0.9)
    for s in (-1, 1):
        m.block("Shackle", s * 1.75, 0, 2.7, 0.8, 2.2, 3.0)
    m.block("Rubble", 0, 0, 0.2, 7, 7, 0.4)
    return m


def titan_tooth(seed=6):
    """A rare treat: one tooth of the thing that fell, bigger than a house door."""
    m = prop("TitanTooth", Bone=BONE, BoneDark=BONE_DARK, Rubble=ROCK_DARK, Moss=MOSS)
    prism(m, "Bone", 0, 0, 0.3, 12, 3.0, 0.3, 8, 0.2, lean=(1.8, 0))
    prism(m, "BoneDark", 0, 0, 0, 2.2, 3.5, 3.1, 8, 0.2)
    m.block("Rubble", 0.6, 0.3, 0.2, 9, 8, 0.4)
    m.block("Moss", -1.6, 2.0, 0.42, 4, 3, 0.16)
    return m


def glow_moss(seed=7):
    """Filler: low mounds of moss with glowing specks."""
    m = prop("GlowMoss", Moss=MOSS, RockDark=ROCK_DARK, DeepSpore=MINT)
    rng = random.Random(seed)
    for _ in range(5):
        x, y = rng.uniform(-2.4, 2.4), rng.uniform(-2.4, 2.4)
        r = rng.uniform(0.9, 1.6)
        ball(m, "Moss", x, y, 0.1, r, 7, 3)
        for _ in range(3):
            a = rng.uniform(0, math.tau)
            ball(m, "DeepSpore", x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.6, 0.1 + r * 0.72, 0.14, 5, 2)
    m.block("RockDark", 0, 0, 0.1, 5.2, 5.2, 0.2)
    return m


def seep_pool(seed=8):
    """Flat, for the middle of the floor where eggs land: a dark pool with a glowing ring spreading on it."""
    m = prop("SeepPool", SeepWater=WATER, SeepRing=MINT_DIM, RockDark=ROCK_DARK, Front=ROCK_DARK)
    m.block("Front", 0, 7, 0.1, 0.2, 0.2, 0.2)
    pool(m, "RockDark", [(0, 0, 13, 10), (1.4, 0.8, 9, 11)], 0.06, 0.1)
    pool(m, "SeepWater", [(0, 0, 11.4, 8.6), (1.4, 0.8, 7.6, 9.6)], 0.14, 0.1)
    flat_ring(m, "SeepRing", 0.4, 0.3, 0.24, 3.0, 0.16, 0.04, 14)
    flat_ring(m, "SeepRing", 0.4, 0.3, 0.24, 1.5, 0.12, 0.04, 12)
    return m


# ---------------------------------------------------------------------- rims, landmarks, walls, overhead


def rock_spire(seed=9):
    """Rims: the shaft's walls go on up in broken towers of teal rock, so the world feels like the bottom of something."""
    m = prop("RockSpire", Rock=ROCK, RockDark=ROCK_DARK, RockLight=ROCK_LIGHT, Moss=MOSS)
    rng = random.Random(seed)
    z = 0
    r = 6.5
    x = y = 0.0
    for k in range(5):
        h = rng.uniform(5.5, 8.5)
        dx, dy = rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8)
        prism(m, "Rock" if k % 2 == 0 else "RockLight", x, y, z, z + h, r, r * 0.8, 7, rng.uniform(0, 1), lean=(dx, dy))
        m.block("RockDark", x, y, z + h, r * 1.2, r * 1.2, 0.6)
        x, y, z, r = x + dx, y + dy, z + h, r * 0.8
    m.block("Moss", 0, 0, 0.3, 15, 15, 0.6)
    return m


def shaft_column(seed=10):
    """Landmark: a carved column as old as the shaft, its rings of light pulsing one after another up its length."""
    m = prop("ShaftColumn", Cut=CUT, CutDark=CUT_DARK, Rock=ROCK_DARK, ColumnRing=MINT, Front=CUT_DARK)
    m.block("Front", 0, 7, 2, 0.2, 0.2, 0.2)
    m.loft_z("Rock", (0, 0, 0, 16, 16), (2.2, 0, 0, 12, 12))
    prism(m, "Cut", 0, 0, 2, 32, 4.4, 3.4, 8, math.pi / 8)
    prism(m, "CutDark", 0, 0, 32, 35, 4.8, 5.8, 8, math.pi / 8)
    for k in range(5):
        z = 6 + k * 5.4
        r = 4.4 - (z / 32) * 1.0
        prism(m, "ColumnRing", 0, 0, z, z + 0.7, r + 0.22, r + 0.22, 8, math.pi / 8)
    return m


def titan_skull(seed=11):
    """Landmark: the skull of what fell, on the rim, staring into the corridor with eyes still lit, its jaw slowly
    opening and closing. Faces +Y. The jaw turns round the X line at SKULL_HINGE."""
    m = prop("TitanSkull", Bone=BONE, BoneDark=BONE_DARK, Sockets=HOLE, DeepEye=MINT, Mandible=BONE_DARK, Fangs=BONE, Rock=ROCK_DARK, Front=BONE_DARK)
    m.block("Front", 0, 19, 8, 0.2, 0.2, 0.2)
    m.loft_z("Rock", (0, 0, -2, 40, 40), (3, 0, 0, 30, 30))
    m.loft_y("Bone", (-14, 0, 17, 25, 21), (4, 0, 16.5, 25, 19))  # the cranium: its flat front holds the eyes
    m.loft_y("Bone", (4, 0, 11, 15, 8), (16, 0, 9.5, 10, 6))  # the snout, low on it
    m.block("BoneDark", 0, -5, 27, 19, 14, 1.4)
    for s in (-1, 1):
        m.block("Sockets", s * 6.4, 4.2, 19.4, 8.6, 0.6, 7.2)
        ball(m, "DeepEye", s * 6.4, 4.7, 19.4, 2.1, 8, 4)
        beam(m, "BoneDark", (s * 1.2, 5.2, 21.6), (s * 12.4, 5.2, 25.4), 3.4, 2.4, 2.0)  # a heavy slanted brow: angry
        beam(m, "Bone", (s * 11.5, -3, 24), (s * 21, 1, 37), 4.2, None, 0.5)  # horns
        m.block("Sockets", s * 2.0, 16.2, 10.6, 1.8, 0.6, 2.4)  # nostrils
    for k in range(6):
        x = -5.0 + k * 2.0
        gem(m, "Fangs", x, 15.6 - abs(x) * 0.25, 6.6, 0.8, 0.3, 2.4, 4)
    m.loft_y("Mandible", (-4, 0, 3.4, 15, 3.6), (15, 0, 2.6, 10, 2.6))
    for k in range(5):
        x = -3.8 + k * 1.9
        gem(m, "Mandible", x, 14.2 - abs(x) * 0.25, 4.0, 0.7, 1.8, 0.3, 4)
    return m


SKULL_HINGE = 6.0


def deep_seep(seed=12):
    """Wall prop: mint light seeping out of a crack at the top of the wall and running down it in falling drops. Origin
    on the wall's top inner edge: rim Z 0, floor Z -44, +Y out into the corridor."""
    m = prop("DeepSeep", RockDark=ROCK_DARK, SeepFall=MINT_DIM, SeepDrop=MINT_SOFT, SeepWater=WATER, Front=ROCK_DARK)
    m.block("RockDark", 0, 2.0, -2.4, 12, 1.6, 5)
    for x, top in ((-2.6, -3), (0.4, -4), (3.0, -3.4)):
        m.block("SeepFall", x, 2.9, (top - 43.4) / 2, 0.8, 0.3, abs(top + 43.4))
        drops(m, "SeepDrop", x, 3.2, top - 1, -42.6, 6.0, 0.3)
    m.block("RockDark", 0.2, 5, -43.7, 15, 9, 0.6)
    m.block("SeepWater", 0.2, 5, -43.34, 12.6, 7, 0.14)
    m.block("Front", 0, 6.4, -2, 0.2, 0.2, 0.2)
    return m


def chain_span(seed=13):
    """Overhead: a great chain sagging from rim to rim between two stone blocks, with a weight hanging from its middle.
    All of it above Z 0, so the flight camera never hits it."""
    m = prop("ChainSpan", Cut=CUT, CutDark=CUT_DARK, Links=IRON, Shackle=IRON_DARK, Front=CUT_DARK)
    m.block("Front", 0, 6, 8, 0.2, 0.2, 0.2)
    for s in (-1, 1):
        m.block("Cut", s * 42, 0, 8, 8, 8, 16)
        m.block("CutDark", s * 42, 0, 16.6, 9, 9, 1.2)
    last = (-38, 0, 13.0)
    for k in range(1, 9):
        x = -38 + k * 9.5
        z = 13.0 - 8.5 * math.sin(k / 8 * math.pi)
        link_chain(m, "Links", last, (x, 0, z), 3, 1.0)
        last = (x, 0, z)
    m.block("Shackle", 0, 0, 3.0, 3.2, 3.2, 2.4)
    return m


def bottom_face(seed=14):
    """The end of the shaft, and the end of the game's corridor: a wall of angry stone filling it from the floor to high
    above the rims, mint eyes looking back up the corridor and a jaw that slowly grinds. Rim at Z 0, corridor floor
    at Z -44. +Y faces the thrower, and the origin stands FACE_FRONT behind the front."""
    m = prop("BottomFace", Rock=ROCK, RockDark=ROCK_DARK, RockLight=ROCK_LIGHT, Brow=ROCK_LIGHT, Sockets=HOLE, DeepEye=MINT, Maw=HOLE,
             Fangs=BONE, Mandible=ROCK, Moss=MOSS, Front=ROCK_DARK)
    F = FACE_FRONT
    m.block("Front", 0, F + 12, 0, 0.2, 0.2, 0.2)
    m.block("RockDark", 0, F - 8, 30, 240, 16, 150)
    m.loft_y("Rock", (F - 8, 0, 34, 150, 96), (F, 0, 34, 120, 84))
    for s in (-1, 1):
        beam(m, "Brow", (s * 3, F + 2, 26), (s * 44, F + 2, 50), 16, 10, 9)  # slanted down to the middle: furious
        m.block("Sockets", s * 22, F + 0.4, 24, 26, 1.0, 13)
        ball(m, "DeepEye", s * 21, F + 1.4, 24, 5.6, 8, 5)
        ball(m, "Sockets", s * 19, F + 6.2, 23, 1.9, 6, 3)  # pupils, turned in: it's looking at you
        beam(m, "RockLight", (s * 40, F, 12), (s * 26, F + 2, -2), 8, 6, 5)  # cheeks
        limb(m, "RockDark", [(s * 60, F - 6, 60), (s * 72, F - 2, 84), (s * 62, F, 104)], 11, 2)  # horns
    m.loft_y("RockLight", (F, 0, 8, 12, 24), (F + 8, 0, 7, 8, 10))  # the nose
    m.block("Maw", 0, F + 0.4, -18, 72, 1.0, 26)
    for k in range(9):
        x = -32 + k * 8
        gem(m, "Fangs", x, F + 2.2, -6.5, 2.8, 0.8, 8.5 - abs(k - 4) * 0.7, 4)
    m.block("Mandible", 0, F + 3, JAW_REST - 6, 80, 7, 12)
    for k in range(8):
        x = -28 + k * 8
        gem(m, "Mandible", x, F + 4, JAW_REST + 1, 2.4, 6.5, 0.6, 4)
    for x, z in ((-52, 44), (56, 36), (-48, -30), (52, -32)):
        m.block("Moss", x, F + 0.4, z, 16, 0.5, 8)
    return m


ALL = [depth_gauge, giant_rib, stone_fang, fallen_block, hanging_chain, titan_tooth, glow_moss, seep_pool, rock_spire, shaft_column, titan_skull,
       deep_seep, chain_span, bottom_face]

# What moves. Same numbers as shared/Config/PropMotion.luau.
MOTION = {
    "prop_DepthGauge": {"GaugeMark": dict(bob=3.2, period=9), "GaugeTick": dict(pulse=0.55, period=3)},
    "prop_StoneFang": {"FangTip": dict(pulse=0.6, period=2.6)},
    "prop_FallenBlock": {"SeamGlow": dict(pulse=0.5, period=2.2)},
    "prop_HangingChain": {"Links": dict(swing=3, period=9, axis="across", height=40), "Shackle": dict(swing=3, period=9, axis="across", height=40)},
    "prop_GlowMoss": {"DeepSpore": dict(pulse=0.5, period=2.9)},
    "prop_SeepPool": {"SeepRing": dict(pulse=0.45, period=2.4)},
    "prop_ShaftColumn": {"ColumnRing": dict(pulse=0.45, period=3.2)},
    "prop_TitanSkull": {"DeepEye": dict(pulse=0.6, period=3.6), "Mandible": dict(swing=7, period=6, axis="across", height=SKULL_HINGE)},
    "prop_DeepSeep": {"SeepDrop": dict(fall=6, period=1.8), "SeepFall": dict(pulse=0.6, period=3.1)},
    "prop_ChainSpan": {"Shackle": dict(bob=0.5, period=7)},
    "prop_BottomFace": {"DeepEye": dict(pulse=0.65, period=4.2), "Mandible": dict(bob=2.4, period=6.5)},
}

LIGHTS = {
    "prop_FallenBlock": ("SeamGlow", MINT, 24, 1.0),
    "prop_ShaftColumn": ("ColumnRing", MINT, 40, 1.1),
    "prop_TitanSkull": ("DeepEye", MINT, 40, 1.4),
    "prop_BottomFace": ("DeepEye", MINT, 90, 2.6),
}

# Where the props go: the same rules as Config/Decor's DeepEnd (keep the two in step). The map is 1500 long, and the Last
# Door stands at its first 52 studs, so nothing starts before 70. The Bottom Face is past the end, like the Last Door.
DECOR = dict(
    floor=dict(first=70, gap=(12, 20), side=(23, 34),
               props=[("prop_DepthGauge", 13, (1.3, 1.7)), ("prop_GiantRib", 8, (1.1, 1.4)), ("prop_StoneFang", 10, (1.2, 1.7)), ("prop_FallenBlock", 7, (1.0, 1.3)),
                      ("prop_HangingChain", 7, (1.2, 1.5)), ("prop_TitanTooth", 3, (1.2, 1.5))],
               extras=dict(chance=0.7, spread=8, props=[("prop_GlowMoss", 5, (0.9, 1.4))])),
    rim=dict(first=70, gap=(9, 15), chance=0.95, side=(60, 104),
             props=[("prop_RockSpire", 9, (1.6, 2.6)), ("prop_StoneFang", 3, (2.0, 2.8)), ("prop_DepthGauge", 2, (2.0, 2.4)), ("prop_GlowMoss", 2, (2.2, 2.8))]),
    overhead=[("prop_ChainSpan", 340, 0, 1), ("prop_ChainSpan", 800, 0, 1), ("prop_ChainSpan", 1260, 0, 1)],
    walls=[("prop_DeepSeep", d, side) for d, side in ((120, 1), (290, -1), (460, 1), (630, -1), (800, 1), (970, -1), (1140, 1), (1310, -1), (1470, 1))],
    spots=[("prop_ShaftColumn", 210, -84, "rim", 0, 1.6, "middle"), ("prop_ShaftColumn", 560, 84, "rim", 0, 1.7, "middle"), ("prop_ShaftColumn", 920, -84, "rim", 0, 1.6, "middle"),
           ("prop_ShaftColumn", 1290, 84, "rim", 0, 1.7, "middle"),
           ("prop_TitanSkull", 400, 84, "rim", 0, 1.5, "middle"), ("prop_TitanSkull", 760, -84, "rim", 0, 1.6, "middle"), ("prop_TitanSkull", 1130, 84, "rim", 0, 1.5, "middle"),
           ("prop_BottomFace", FACE_AT + FACE_FRONT, 0, "rim", 180, 1, "along")]
          + [("prop_SeepPool", d, x, "floor", yaw, 1.3, "along") for d, x, yaw in ((130, -3, 10), (300, 4, 350), (470, -4, 20), (640, 3, 340), (810, -2, 5), (980, 4, 15),
                                                                         (1150, 2, 10), (1320, -4, 355), (1450, 3, 25))],
)

BIG = {"prop_ShaftColumn": (-110, -150, 0), "prop_TitanSkull": (-40, -150, 0), "prop_RockSpire": (20, -150, 0), "prop_DeepSeep": (140, -110, 44), "prop_ChainSpan": (240, -170, 0),
       "prop_BottomFace": (90, -520, 44)}


def set_light(scene, sun_energy, ambient):
    world = scene.world
    world.node_tree.nodes["Background"].inputs[1].default_value = ambient
    for obj in scene.objects:
        if obj.type == "LIGHT" and obj.data.type == "SUN":
            obj.data.energy = sun_energy


def main(stills=True, videos=True, only=None):
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
            x += 22
        built[model.name] = root
        roots.append(root)
    row_middle = (40 + x - 22) / 2
    mk.light_up(roots, GLOW_ROLES)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-500, -800, -0.01), (800, -800, -0.01), (800, 200, -0.01), (-500, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", CORRIDOR["FloorA"], False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = mk.player_block(stage)
    bpy.context.view_layer.update()
    mk.set_sky(scene, SKY)

    everything = roots + [player]
    if stills:
        for model, root in zip(models, roots):
            name = model.name
            if only and name not in only:
                continue
            if name == "prop_BottomFace":
                mk.set_visible(everything, [root])
                c = Vector(root.location) + Vector((0, 40, 10))
                kit.shoot(scene, name, c + Vector((30, 230, 26)), c + Vector((0, 0, 14)), (1300, 1000), 34)
            elif name == "prop_DeepSeep":
                mk.shoot_prop(scene, name, root, player, everything, (0.3, 1.0, 0.0), 1.0, (800, 900), 40)
            elif name == "prop_ChainSpan":
                mk.shoot_prop(scene, name, root, player, everything, (0.1, 1.0, 0.22), 0.9, (1400, 700), 32)
            elif name == "prop_SeepPool":
                mk.shoot_prop(scene, name, root, player, everything, (0.05, 0.25, 1.0), 1.1, (700, 700), 50)
            elif name in ("prop_ShaftColumn", "prop_TitanSkull", "prop_RockSpire"):
                mk.shoot_prop(scene, name, root, player, everything, (0.5, 0.95, 0.3), 1.1, (800, 800), 50)
            else:
                mk.shoot_prop(scene, name, root, player, everything)
        if not only:
            player.location = (30, -40, 0)
            bpy.context.view_layer.update()
            small = [r for r in roots if mk.prop_of(r) not in BIG]
            mk.set_visible(everything, small + [player])
            kit.shoot(scene, "props", (row_middle, 60, 40), (row_middle, -40, 6), (2000, 700), 18)

    if only:
        return
    ground.hide_render = True
    mk.set_visible(everything, [])
    corridor = mk.corridor_stage(stage, CORRIDOR, length=600)
    copies = mk.decorate_stage(stage, built, {k: v for k, v in DECOR.items() if k != "spots"} | {"spots": [s for s in DECOR["spots"] if s[1] < 600]}, length=600)
    if stills:
        kit.shoot(scene, "corridor_flight", (0, -40, 30), (0, -240, 16), (1600, 900), 22)
        kit.shoot(scene, "corridor_high", (0, -30, 80), (0, -240, 30), (1600, 900), 22)
        kit.shoot(scene, "corridor_floor", (-16, -120, 10), (8, -240, 12), (1600, 900), 22)
        kit.shoot(scene, "corridor_rim", (-40, -50, 90), (50, -230, 54), (1600, 900), 24)
    if videos:
        entries = mk.motion_entries(copies, MOTION)
        frames = 165

        def fly(f):
            t = f / (frames - 1)
            y = -40 - 400 * t
            return (0, y, 28 + 4 * math.sin(t * math.pi)), (0, y - 70, 17), 22, lambda s: mk.apply_motion(entries, s)

        mk.render_video(scene, RENDERS, "deep_end_flight", frames, 15, fly, (1600, 900))
        mk.reset_motion(entries)

    # The end of it all: the Bottom Face at the end of a stretch of corridor.
    mk.clear(copies)
    face = mk.place_copy(built["prop_BottomFace"], stage, (0, -(520 + FACE_FRONT), mk.WALL), 0, 1)
    if stills:
        kit.shoot(scene, "bottom_of_the_world", (0, -310, 24), (0, -520, 40), (1600, 900), 26)
        kit.shoot(scene, "egg_view", (10, -400, 9), (-2, -520, 22), (1600, 900), 26)
    mk.clear([face, corridor])
    mk.light_up(roots, GLOW_ROLES, 0)
    ground.hide_render = False
    for root in roots:
        for child in root.children:
            child.hide_render = False
    player.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "deep_end_models.blend"))
    print("saved", HERE / "deep_end_models.blend")
    for model in models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "only" in args:
        main(stills=True, videos=False, only=set(args[args.index("only") + 1:]))
    else:
        main(stills=not args or "stills" in args, videos=not args or "videos" in args)
