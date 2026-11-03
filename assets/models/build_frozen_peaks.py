"""Builds the Frozen Peaks's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_frozen_peaks.py

Saves frozen_peaks_models.blend and renders to design/world/models_frozen_peaks/, with a stretch of corridor.

Frozen Peaks after the Volcano's dark rock and lava: white snow and pale blue ice, cut with dark green pines
so it doesn't read as one white blur from the flight camera, and a few warm spots (an igloo's lit doorway,
a campfire, red berries). Big landmarks on the rims (a glacier, giant mammoth tusks arching out of the
snow), frozen waterfalls down the corridor walls, an ice arch over it, flat frozen ponds across the floor.

Glowing parts (Flame, Ember, Glow) get the Neon material in the game (shared/Roles.luau). Props that must
face a certain way (Icefall, IceArch) carry a small Front part that MapDecor uses to turn them, then removes.
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
from build_swamp import place_copy  # noqa: E402
from build_volcano import crack, hide_markers, prism, set_sky, set_visible  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "models_frozen_peaks"

GLOW_ROLES = {"Flame", "Ember", "Glow"}
kit.NO_STUDS.update(GLOW_ROLES)

# Shared colours, so every prop's snow and ice match.
SNOW, SNOW_SHADE = "#f4f8fc", "#d9e6f0"
ICE, ICE_DEEP, ICE_DARK, ICE_LIGHT = "#a9e4fb", "#5fbde6", "#3d8fbf", "#e3f7ff"
ROCK, ROCK_DARK = "#7b8794", "#5c6672"

# The corridor's Frozen Peaks colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#d3e1ec", "FloorB": "#c1d2df", "Dirt": "#7f9fb8", "DirtB": "#7393ad", "Grass": "#f2f7fb"}
SKY = "#bcd9f2"


def prop(name, **colours):
    return Model(f"prop_{name}", colours)


def icicle(m, role, x, y, top, length, width=0.5):
    """An icicle hanging from `top`, tapering to a point."""
    m.loft_z(role, (top - length, x, y, 0.04, 0.04), (top, x, y, width, width))


# ---------------------------------------------------------------------- props


def snow_pine(seed=3):
    """The map's signature tree: a dark pine of stacked tiers, every tier capped with snow."""
    m = prop("SnowPine", Trunk="#6b4a33", Pine="#2f6b4f", PineDark="#25543f", Snow=SNOW)
    rng = random.Random(seed)
    m.loft_z("Trunk", (0, 0, 0, 1.7, 1.7), (3.2, 0, 0, 1.3, 1.3))
    m.loft_z("Snow", (0, 0, 0, 3.4, 3.4), (0.45, 0, 0, 2.3, 2.3))
    tiers = [(2.4, 6.4, 5.6), (5.4, 9.0, 4.5), (8.0, 11.4, 3.3), (10.4, 13.6, 2.1)]  # bottom, top, radius
    for i, (z0, z1, r) in enumerate(tiers):
        turn = (math.pi / 4) * (i % 2)
        top = r * 0.16
        prism(m, "Pine" if i % 2 == 0 else "PineDark", 0, 0, z0, z1, r, top, 4, turn)
        zm, rm = z0 + (z1 - z0) * 0.5, r + (top - r) * 0.5
        prism(m, "Snow", 0, 0, zm, z1 + 0.1, rm + 0.12, top + 0.12, 4, turn)
        for k in range(4):
            if rng.random() < 0.8:
                a = turn + k * math.pi / 2
                m.block("Snow", math.cos(a) * r * 0.82, math.sin(a) * r * 0.82, z0 + 0.3, 0.75, 0.75, 0.42)
    m.block("Snow", 0, 0, 13.85, 0.5, 0.5, 0.5)
    return m


def ice_spikes(seed=8):
    """A cluster of ice crystals growing out of a snow mound, pale to deep blue."""
    m = prop("IceSpikes", Ice=ICE, IceDeep=ICE_DEEP, IceLight=ICE_LIGHT, Snow=SNOW, SnowShade=SNOW_SHADE)
    rng = random.Random(seed)
    m.loft_z("Snow", (0, 0, 0, 6.2, 5.2), (0.7, 0, 0, 4.6, 3.8))
    m.block("SnowShade", 1.9, -1.3, 0.25, 2.2, 1.8, 0.5)
    spikes = [(0, 0, 10.5, 1.15, (0.3, 0.2), "Ice"), (1.6, 0.8, 6.8, 0.8, (0.9, 0.5), "IceDeep"),
              (-1.5, 0.6, 7.6, 0.85, (-0.8, 0.3), "Ice"), (0.4, -1.5, 5.0, 0.65, (0.3, -0.8), "IceDeep"),
              (-1.0, -1.1, 3.6, 0.55, (-0.5, -0.5), "IceLight"), (2.2, -0.6, 3.0, 0.5, (0.6, -0.2), "IceLight")]
    for x, y, height, r, (lx, ly), role in spikes:
        turn = rng.uniform(0, 1)
        mid = height * 0.72
        prism(m, role, x, y, 0.3, mid, r, r * 0.85, 6, turn, (lx * 0.72, ly * 0.72))
        prism(m, role, x + lx * 0.72, y + ly * 0.72, mid, height, r * 0.85, 0.03, 6, turn, (lx * 0.28, ly * 0.28))
    return m


def giant_tusks():
    """A landmark for the rims: two huge mammoth tusks curving out of the snow and crossing overhead."""
    m = prop("GiantTusks", Tusk="#f3e6c8", TuskShade="#d8c59c", Snow=SNOW, SnowShade=SNOW_SHADE)
    radius, steps = 9.0, 12
    for side in (-1, 1):
        y = side * 0.7
        cx = -side * 3.0
        points = []
        for i in range(steps + 1):
            t = math.radians(100) * i / steps
            points.append((cx + side * radius * math.cos(t), y, 0.3 + radius * math.sin(t)))
        for i, (a, b) in enumerate(zip(points, points[1:])):
            w0 = 1.7 - 1.4 * i / steps
            w1 = 1.7 - 1.4 * (i + 1) / steps
            beam(m, "Tusk" if i % 4 else "TuskShade", a, b, w0, None, w1)
            if 0 < i:
                m.block("Tusk", *a, w0 * 0.92, w0 * 0.92, w0 * 0.92)  # fills the bend between pieces
        sx = cx + side * radius
        m.loft_z("Snow", (0, sx, y, 4.6, 4.0), (1.4, sx, y, 2.8, 2.6))
        m.block("SnowShade", sx + side * 1.6, y - 1.2, 0.35, 2.0, 1.8, 0.7)
    m.block("Snow", -2.5, 2.2, 0.3, 3.0, 2.2, 0.6)
    return m


def igloo():
    """A snow-block igloo with warm light glowing out of its doorway."""
    m = prop("Igloo", Snow=SNOW, SnowShade=SNOW_SHADE, Glow="#ffb860", Ice=ICE)
    rows = [(0, 1.1, 4.8, 4.75), (1.1, 2.2, 4.65, 4.35), (2.2, 3.25, 4.25, 3.7), (3.25, 4.15, 3.6, 2.8), (4.15, 4.85, 2.7, 1.6), (4.85, 5.25, 1.6, 0.5)]
    for i, (z0, z1, r0, r1) in enumerate(rows):
        prism(m, "Snow" if i % 2 == 0 else "SnowShade", 0, 0, z0, z1, r0, r1, 12, (math.pi / 12) * (i % 2))
    m.block("Snow", 0, 4.9, 1.15, 2.8, 2.6, 2.3)  # the entrance tunnel
    m.block("SnowShade", 0, 4.9, 2.45, 3.0, 2.8, 0.35)
    m.block("Glow", 0, 6.21, 0.95, 1.5, 0.06, 1.7)
    m.block("Ice", 0, 3.65, 4.0, 1.2, 0.3, 0.9)  # an ice window over the door
    for x, y, s in ((-3.8, 4.0, 1.6), (3.4, 4.6, 1.3), (-4.6, -2.0, 1.4), (4.4, -2.6, 1.8)):
        m.block("Snow", x, y, s * 0.25, s, s, s * 0.5)
    return m


def ice_boulder():
    """A grey boulder with a thick cap of snow, and a smaller one beside it."""
    m = prop("IceBoulder", Rock=ROCK, RockDark=ROCK_DARK, Snow=SNOW, SnowShade=SNOW_SHADE)
    m.loft_z("Rock", (0, 0, 0, 5.6, 4.6), (2.6, 0.2, 0.1, 5.0, 4.2))
    m.loft_z("Rock", (2.6, 0.2, 0.1, 5.0, 4.2), (3.6, 0.3, 0.2, 3.4, 2.8))
    m.loft_z("Snow", (3.3, 0.3, 0.2, 4.0, 3.4), (4.0, 0.3, 0.2, 3.0, 2.4))
    m.block("Snow", 1.9, 0.4, 3.0, 1.2, 1.8, 0.6)
    m.block("Snow", -1.6, -0.6, 2.9, 1.0, 1.4, 0.5)
    m.loft_z("RockDark", (0, -3.4, 1.6, 2.6, 2.4), (1.5, -3.3, 1.5, 1.9, 1.7))
    m.loft_z("Snow", (1.35, -3.3, 1.5, 2.1, 1.9), (1.8, -3.3, 1.5, 1.4, 1.2))
    m.block("SnowShade", 2.2, -2.6, 0.25, 2.4, 1.6, 0.5)
    return m


def snow_drift(seed=2):
    """Low drifts of snow with rocks and tundra grass poking through."""
    m = prop("SnowDrift", Snow=SNOW, SnowShade=SNOW_SHADE, Rock=ROCK, Grass="#b9a56a")
    rng = random.Random(seed)
    m.loft_z("Snow", (0, 0, 0, 8, 5), (1.0, 0.3, 0, 6, 3.6))
    m.loft_z("SnowShade", (1.0, 0.3, 0, 6, 3.6), (1.7, 0.6, 0, 3.6, 2.2))
    m.loft_z("Snow", (0, 4.2, 2.0, 4.4, 3.6), (0.9, 4.4, 2.1, 2.8, 2.2))
    m.block("Rock", -2.8, 1.6, 0.5, 1.4, 1.2, 1.0)
    m.block("Rock", 3.4, -1.4, 0.4, 1.0, 1.0, 0.8)
    for x, y in ((-3.6, -1.2), (2.4, 2.6), (-1.0, 2.2), (5.6, 2.8)):
        for k in range(4):
            a = k * math.pi / 2 + rng.uniform(-0.4, 0.4)
            beam(m, "Grass", (x, y, 0.2), (x + math.cos(a) * 0.5, y + math.sin(a) * 0.5, rng.uniform(1.0, 1.6)), 0.2, None, 0.05)
    return m


def frozen_pond(seed=5):
    """A frozen pond with cracks and a fishing hole. Flat (under half a stud), so it can lie in the middle
    of the floor where the eggs land."""
    m = prop("FrozenPond", Ice=ICE, IceLight=ICE_LIGHT, IceDark=ICE_DARK, Water="#1f4f6b", Snow=SNOW)
    rng = random.Random(seed)
    m.block("Ice", 0, 0, 0.06, 14, 9, 0.12)
    m.block("Ice", 1.5, 1.0, 0.06, 9, 12, 0.12)
    for x, y, w in ((-3, -2, 4), (2.5, 3, 3), (4, -1.5, 2.5)):
        m.block("IceLight", x, y, 0.13, w, 0.35, 0.03)
    crack(m, [(-6, 1, 0.15), (-3, -0.5, 0.15), (0, 0.8, 0.15), (3, -0.6, 0.15), (5.5, 1.2, 0.15)], flat=True, role="IceDark", wide=0.18, thick=0.05)
    crack(m, [(0, 0.8, 0.15), (0.8, 3.2, 0.15), (2.2, 4.6, 0.15)], flat=True, role="IceDark", wide=0.14, thick=0.05)
    m.block("Water", -3.2, 2.0, 0.13, 1.8, 1.8, 0.04)
    for dx, dy in ((1.2, 0), (-1.2, 0.2), (0.1, 1.2), (-0.2, -1.2)):
        m.block("IceLight", -3.2 + dx, 2.0 + dy, 0.2, 0.6, 0.5, 0.18)
    for i in range(18):
        a = i * math.tau / 18
        s = rng.uniform(1.0, 1.8)
        m.block("Snow", math.cos(a) * 7.2, math.sin(a) * 5.6, 0.14, s, s, 0.28)
    return m


def glacier(seed=7):
    """A landmark for the rims: a stepped cliff of blue ice with snow on every ledge, crevasses and icicles."""
    m = prop("Glacier", Ice=ICE, IceDeep=ICE_DEEP, IceDark=ICE_DARK, IceLight=ICE_LIGHT, Snow=SNOW)
    rng = random.Random(seed)
    steps = [(0, 0, 0, 26, 16, 6, "IceDeep"), (1, -0.5, 6, 21, 13, 5, "Ice"), (-1.5, 0.5, 11, 15, 10, 4.5, "IceDeep"), (0.5, -0.5, 15.5, 9, 7, 3.5, "Ice")]
    for x, y, z, w, d, h, role in steps:
        m.block(role, x, y, z + h / 2, w, d, h)
        m.block("Snow", x, y, z + h + 0.18, w + 0.3, d + 0.3, 0.36)
        for face in (1, -1):
            for k in range(int(w // 3)):
                xi = x - w / 2 + 1.5 + k * 3 + rng.uniform(-0.6, 0.6)
                if rng.random() < 0.7:
                    icicle(m, "IceLight", xi, y + face * (d / 2 + 0.2), z + h, rng.uniform(1.0, 2.6), 0.6)
                if rng.random() < 0.35:
                    m.block("IceDark", xi + 1.2, y + face * (d / 2 + 0.03), z + h * 0.45, 0.5, 0.12, h * 0.7)
            for k in range(int(d // 3)):
                yi = y - d / 2 + 1.5 + k * 3 + rng.uniform(-0.5, 0.5)
                if rng.random() < 0.6:
                    icicle(m, "IceLight", x + face * (w / 2 + 0.2), yi, z + h, rng.uniform(1.0, 2.2), 0.55)
    for x, y, height in ((-2, 1, 4.5), (2.5, -1.5, 3.2), (-0.5, -2.2, 2.4)):
        prism(m, "IceLight", x, y, 19.2, 19.2 + height, 0.9, 0.04, 5, rng.uniform(0, 1), (0.2, -0.2))
    return m


def campfire(seed=4):
    """A campfire in a ring of stones, with log benches either side: a warm spot in the snow."""
    m = prop("Campfire", Stone="#8e959e", StoneDark="#6b737c", Wood="#7a5232", WoodDark="#5a3b24",
             Flame="#ffc23a", Ember="#ff6a1a", Ash="#4b4b50", Snow=SNOW)
    rng = random.Random(seed)
    m.block("Ash", 0, 0, 0.05, 3.4, 3.4, 0.1)
    for i in range(10):
        a = i * math.tau / 10
        s = rng.uniform(0.7, 1.0)
        m.block("Stone" if i % 2 else "StoneDark", math.cos(a) * 2.0, math.sin(a) * 2.0, s * 0.3, s, s, s * 0.6)
    for k in range(4):
        a = k * math.pi / 2 + 0.4
        beam(m, "Wood" if k % 2 else "WoodDark", (math.cos(a) * 1.3, math.sin(a) * 1.3, 0.2), (0, 0, 1.7), 0.42)
    m.block("Ember", 0, 0, 0.25, 1.4, 1.4, 0.3)
    for (x, y, height, w, role) in ((0, 0, 2.9, 1.2, "Ember"), (0.45, 0.3, 2.0, 0.7, "Flame"), (-0.45, -0.2, 2.2, 0.7, "Flame"),
                                      (0.35, -0.45, 1.6, 0.6, "Ember"), (-0.3, 0.45, 1.5, 0.55, "Flame")):
        m.loft_z(role, (0.3, x, y, w, w), (0.3 + height, x * 0.6, y * 0.6, 0.06, 0.06))
    for side in (-1, 1):
        y = side * 3.6
        m.loft_x("Wood", (-1.8, y, 0.45, 0.9, 0.9), (1.8, y, 0.45, 0.85, 0.85))
        m.block("WoodDark", 1.82, y, 0.45, 0.06, 0.6, 0.6)
        m.block("Snow", 0.3, y, 0.95, 2.6, 0.7, 0.12)
    return m


def frost_bush(seed=6):
    """A frosted blue-green bush with red berries, a spot of colour in the white."""
    m = prop("FrostBush", Leaf="#5f8f8a", LeafLight="#8fbcb6", Frost="#eef7fb", Berry="#e0334a")
    rng = random.Random(seed)
    clumps = [(0, 0, 1.1, 3.4, 3.0, 2.2, "Leaf"), (1.2, 0.6, 1.6, 2.2, 2.0, 1.8, "LeafLight"),
              (-1.1, -0.5, 1.4, 2.0, 2.2, 1.6, "Leaf"), (0.2, -0.1, 2.6, 2.0, 1.8, 1.0, "LeafLight")]
    for x, y, z, w, d, h, role in clumps:
        m.block(role, x, y, z, w, d, h)
        m.block("Frost", x, y, z + h / 2 + 0.06, w * 0.86, d * 0.86, 0.12)
    for i in range(10):
        x, y, z, w, d, h, _ = clumps[i % 3]
        a = rng.uniform(0, math.tau)
        m.block("Berry", x + math.cos(a) * w * 0.5, y + math.sin(a) * d * 0.5, z + rng.uniform(-0.3, 0.4), 0.3, 0.3, 0.3)
    return m


def ice_arch(seed=12):
    """An arch of ice over the corridor, rim to rim, snow on top and icicles hanging under it. It spans X
    and every part stays above the rim's height (z 0), clear of the flight camera."""
    m = prop("IceArch", Ice=ICE, IceDeep=ICE_DEEP, IceLight=ICE_LIGHT, Snow=SNOW, SnowShade=SNOW_SHADE, Front="#ff00ff")
    rng = random.Random(seed)

    def underside(x):
        return 6 + 8 * (1 - (x / 46) ** 2)

    for side in (-1, 1):
        m.block("IceDeep", side * 49, 0, 3.5, 20, 12, 7)
        m.block("Snow", side * 49, 0, 7.2, 20.4, 12.4, 0.4)
        m.block("Ice", side * 46, 0.5, 9.5, 14, 10, 4.6)
        m.block("Snow", side * 46, 0.5, 11.95, 14.4, 10.4, 0.4)
    for i in range(-5, 6):
        x = i * 8
        bottom = underside(x)
        m.block("Ice" if i % 2 == 0 else "IceDeep", x, rng.uniform(-0.4, 0.4), bottom + 2.6, 8.4, rng.uniform(7.6, 8.8), 5.2)
        m.block("Snow", x, 0, bottom + 5.45, 8.6, 9.2, 0.5)
        for face in (1, -1):
            if rng.random() < 0.6:
                m.block("SnowShade", x + rng.uniform(-2, 2), face * 4.5, bottom + 4.6, 2.0, 0.5, 1.4)
    for k in range(14):
        x = -32 + k * 4.9 + rng.uniform(-1.2, 1.2)
        under = underside(x)
        icicle(m, "IceLight", x, rng.uniform(-3.4, 3.4), under + 0.2, rng.uniform(1.6, min(4.5, under - 2)), rng.uniform(0.6, 1.0))
    m.block("Front", 0, 6, 3, 0.2, 0.2, 0.2)
    return m


def icefall(seed=4):
    """A frozen waterfall down the corridor wall: a stream frozen on the rim, ice spilling over the edge and
    columns of ice down to an ice mound on the floor. Origin on the wall's top inner edge: rim z 0, floor
    z -44, +Y out into the corridor. The Front part tells the game which way it faces, then it's removed."""
    m = prop("Icefall", Ice=ICE, IceDeep=ICE_DEEP, IceLight=ICE_LIGHT, Snow=SNOW, SnowShade=SNOW_SHADE, Front="#ff00ff")
    rng = random.Random(seed)
    m.block("Ice", 0, -6.5, 0.15, 7.5, 13, 0.3)
    for side in (-1, 1):
        for y, s in ((-11, 2.6), (-7.5, 2.2), (-4, 2.4), (-0.9, 2.0)):
            m.block("Snow", side * 4.8, y, s * 0.3, s, s * 1.1, s * 0.6)
    m.block("Ice", 0, 0.9, -0.1, 8.0, 2.0, 0.7)
    m.block("IceLight", 0, 2.0, -1.3, 9.0, 1.8, 2.2)
    roles = ("Ice", "IceDeep", "IceLight")
    for k in range(12):
        x = -4.8 + k * 0.87 + rng.uniform(-0.15, 0.15)
        r = rng.uniform(0.6, 1.1)
        y = 1.7 + r + rng.uniform(0, 0.5)
        role = roles[k % 3]
        if k in (3, 4, 6, 7, 9):  # these reach the floor
            prism(m, role, x, y, -43.6, -1.6, r * 1.2, r, 6, rng.uniform(0, 1))
        else:
            end = rng.uniform(-32, -10)
            prism(m, role, x, y, end, -1.6, r, r, 6, 0.3)
            prism(m, role, x, y, end - rng.uniform(2.5, 4.5), end, 0.04, r, 6, 0.3)
    for z in (-11, -24, -35):
        m.block("IceLight", rng.uniform(-1, 1), 2.9, z, 8.5, 1.8, 1.4)  # bulges where it froze in layers
    m.loft_z("IceDeep", (-44, 0, 3.8, 13, 9), (-42.2, 0, 3.2, 8, 5.4))
    m.loft_z("Ice", (-42.2, 0, 3.2, 8, 5.4), (-41.2, 0, 2.9, 4.5, 3))
    for x, y, s in ((-7.2, 3.0, 2.0), (-5.0, 7.6, 1.6), (0.4, 8.8, 1.8), (5.0, 7.4, 1.6), (7.4, 2.8, 2.1)):
        m.block("Snow", x, y, -44 + s * 0.3, s, s, s * 0.6)
    m.block("Front", 0, 6, -20, 0.2, 0.2, 0.2)
    return m


# ---------------------------------------------------------------------- preview stage


def corridor_stage(stage, length=300, seed=7):
    """A stretch of corridor in Frozen Peaks' colours (floor z 0, walls 44 high, inner faces 36 from the middle)."""
    m = Model("FrozenPeaksCorridor", dict(CORRIDOR))
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


def decorate_stage(stage, built, length=300, seed=41):
    """The corridor's props laid out like Config/Decor's FrozenPeaks rules, so the render shows the real mix."""
    rng = random.Random(seed)

    def pick(table):
        total = sum(w for _, w, _ in table)
        roll = rng.uniform(0, total)
        for name, weight, scale in table:
            roll -= weight
            if roll <= 0:
                return name, scale
        return table[-1][0], table[-1][2]

    floor = [("prop_SnowPine", 20, (1.3, 1.7)), ("prop_IceSpikes", 14, (1.2, 1.6)), ("prop_IceBoulder", 12, (1.2, 1.6)),
             ("prop_SnowDrift", 12, (1.2, 1.6)), ("prop_FrostBush", 10, (1.3, 1.7)), ("prop_Igloo", 6, (1.2, 1.4)),
             ("prop_Campfire", 5, (1.3, 1.6))]
    extras = [("prop_SnowDrift", 4, (0.6, 0.9)), ("prop_FrostBush", 3, (0.7, 1.0)), ("prop_IceSpikes", 2, (0.5, 0.7))]
    rim = [("prop_SnowPine", 6, (2, 2.6)), ("prop_IceSpikes", 3, (2, 2.6)), ("prop_IceBoulder", 2, (2, 2.6)), ("prop_Igloo", 1, (1.8, 2.2))]
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
        put_random(floor, x, 0, y)
        if rng.random() < 0.55:
            put_random(extras, side * min(max(abs(x) + rng.uniform(-8, 8), 16), 33), 0, y + rng.uniform(-8, 8))
        y += rng.uniform(14, 26)
    y = 8
    while y < length:
        for side in (-1, 1):
            if rng.random() < 0.85:
                put_random(rim, side * rng.uniform(56, 94), 44, y)
        y += rng.uniform(18, 30)
    put("prop_Glacier", (72, -70, 44), math.radians(10), 1.3)
    put("prop_GiantTusks", (-70, -200, 44), math.radians(80), 1.6)
    for y, side in ((45, -1), (165, 1), (265, -1)):
        put("prop_Icefall", (side * 36, -y, 44), side * math.pi / 2, 1)
    put("prop_IceArch", (0, -125, 44), 0, 1)
    for y, x, yaw in ((30, -3, 20), (105, 5, 140), (190, -4, 70), (255, 2, 200)):
        put("prop_FrozenPond", (x, -y, 0), math.radians(yaw), 1.2)
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


# ---------------------------------------------------------------------- scene and renders


def main():
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    props = bpy.data.collections.new("Props")
    stage = bpy.data.collections.new("Preview stage")
    for col in (props, stage):
        scene.collection.children.link(col)

    prop_models = [snow_pine(), ice_spikes(), giant_tusks(), igloo(), ice_boulder(), snow_drift(), frozen_pond(),
                   glacier(), campfire(), frost_bush(), ice_arch(), icefall()]
    built = {}
    prop_roots = []
    spots = {"prop_Glacier": (0, -70, 0), "prop_Icefall": (40, -150, 44), "prop_IceArch": (130, -150, 0), "prop_GiantTusks": (-40, -70, 0)}
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
    player = Model("Player", {"Skin": "#3f4553"})
    player.bone = "Root"
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    player_root = player.build(stage)
    bpy.context.view_layer.update()
    set_sky(scene, SKY)

    everything = prop_roots + [player_root]
    for model, root in zip(prop_models, prop_roots):
        low, high = kit.bounds(root)
        player_root.location = Vector((low.x - 3, (low.y + high.y) / 2 + 2, 0))
        bpy.context.view_layer.update()
        set_visible(everything, [root, player_root])
        centre = (low + high) / 2
        reach = max((high - low).length, 7)
        if model.name == "prop_IceArch":
            kit.shoot(scene, model.name, centre + Vector((-25, 125, 10)), centre, (1400, 700), 32)
        elif model.name == "prop_Icefall":
            kit.shoot(scene, model.name, centre + Vector((40, 55, 6)), centre, (700, 900), 40)
        else:
            kit.shoot(scene, model.name, centre + Vector((0.5, 0.9, 0.42)) * reach * 1.25, centre, (600, 600), 50)
    player_root.location = (30, -40, 0)
    bpy.context.view_layer.update()
    set_visible(everything, [r for r in prop_roots if r.name not in ("prop_Icefall", "prop_IceArch", "prop_Glacier", "prop_GiantTusks")] + [player_root])
    kit.shoot(scene, "props", (128, 50, 40), (128, -45, 5), (1800, 700), 20)

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
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "frozen_peaks_models.blend"))
    print("saved", HERE / "frozen_peaks_models.blend")
    for model in prop_models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    main()
