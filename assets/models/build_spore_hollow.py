"""Builds Spore Hollow's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_spore_hollow.py              (stills and videos)
    Blender -b -P build_spore_hollow.py -- stills    (stills only, quicker while modelling)

Saves spore_hollow_models.blend and renders to design/world/models_spore_hollow/: one still per prop, the props
together, the landmarks, a stretch of corridor, and two videos of what moves (spore_motion.mp4 close up,
spore_flight.mp4 down the corridor at the flight camera's height).

Spore Hollow, map 14, the sixth of the mysterious, dark maps: a hollow at the bottom of the world where no sun
has ever reached, and the fungus grew as big as castles instead. It glows by itself: chartreuse light from under
every cap, spores sifting down from the gills and puffing up out of puffballs, moths circling the brightest
caps, and a few windows lit warm amber where somebody small moved into a mushroom. Night under a hazy olive-gold
spore mist. A floor of dark umber loam, walls of peat, and pale cream mycelium on the rims, hanging over the walls
like felt. Brown, cream and chartreuse after Thorn Kingdom's moss, black-violet and crimson; its chartreuse glow
is a first. Its signature is the glowcap: a giant rust-red mushroom on a ringed stalk, its gills glowing, glowing
specks on its cap and spores sifting down from it for ever. Around it: puffball clusters puffing clouds of glowing
spores; lamp mushrooms whose stalk curls over like a lamp post with a glowing bulb swinging from its tip; wavecaps,
three tall thin stalks with glowing bells, each swaying its own way; rotten stumps stepped with glowing shelf
fungi, moths circling; orange coral fungus with glowing tips; now and then a mushroom hut (a door, lit windows,
smoke from the chimney, a lantern swinging) or the mycelium heart, a great bulb beating in the ground with glowing
veins running out from it; spore tufts as filler, and glowing mycelium webs lying flat across the middle. On the
rims: parasol mushrooms with glowing gills and moths circling, and morel spires glowing amber through their
honeycomb, spores rising off their tips; landmarks: elder shrooms (a colossal mushroom with a door, windows and a
stair of shelf fungi winding up its stalk), shroom towers (three caps stacked into a house, lanterns swinging under
them, smoke at the top) and spore geysers (a crater blowing a column of glowing spore clouds into the sky); giant
spores drift across the sky beyond the island trailing glowing threads. Shelf fungi and mycelium cords climb down
the walls dripping glowing drops, and two giant mushrooms lean across the corridor from either rim, their caps
almost touching over the middle, glowing bulbs swinging under them.

No stud texture in this file: kit.PREVIEW_STUDS is off, so every material is a plain colour and the renders show
the models as they leave Blender. The studs come only in Studio, from the shared "Studs" MaterialVariant that
studio_tidy puts on every part except the glowing ones (docs/MAP_RECIPE.md step 8). The meshes still get the
usual box-projected UVs.

What moves is MOTION below, the same numbers as shared/Config/PropMotion.luau (keep the two in step).
Glowing roles (GLOW_ROLES) must also be in shared/Roles.luau, which makes them Neon in the game.
Props that must face a certain way carry a small Front part on their +Y side; MapDecor turns them, then removes it.
Learned on the maps before (docs/MAP_RECIPE.md): drift only on the sky piece, since drift overrides every other
move; no turn tied to a bob; pieces that turn together share one centre (hooks on the X line at a height for
axis="across", stalks swaying round their foot on the line of their axis).
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
from build_clockwork_citadel import Frame, obox, puffs, tube, turn  # noqa: E402
from map_kit import ball, beam, kit, limb, prism, puddle  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "models_spore_hollow"

# Roles lit from inside. The game makes them Neon (shared/Roles.luau), so add new ones there too.
GLOW_ROLES = {"GillGlow", "Speck", "Spore", "Glow", "Bulb", "BulbB", "Moths", "Motes", "Window", "LampA", "LampB",
              "Lamp", "Pit", "Vein", "VeinB", "HeartGlow", "BellA", "BellB", "BellC", "TipGlow", "Falling", "SporeCore", "Filament",
              "Drifter"}
kit.NO_STUDS.update(GLOW_ROLES)
mk.GLOW_STRENGTH = 1.35

# Shared colours, so every prop's stalks, caps, soil and light match.
STALK, STALK_SHADE = "#e4d9c0", "#c4b396"
CAP, CAP_DARK = "#b8532c", "#86381e"
CAP_B, CAP_B_DARK = "#6e4632", "#4c2f22"
CAP_C = "#c9944e"
SCALE = "#5e3a24"
LOAM, LOAM_DARK = "#4a3830", "#33261f"
MYCEL = "#dcd3bd"
MOSS = "#5f6c38"
BARK, BARK_DARK = "#4b3628", "#33241b"
SHELF, SHELF_DARK = "#c8955a", "#9a6a3c"
CORAL, CORAL_DARK = "#e07a3e", "#b8572e"
WOOD, WOOD_DARK = "#7a5236", "#4d3322"
STONE = "#8a8578"
IRON = "#3a3630"
CHIMNEY = "#9a6448"
HEART, HEART_RIB = "#5a2f45", "#76405c"
RIDGE = "#b89466"
WART = "#b9a684"
GILL = "#a8ff38"  # the chartreuse glow under every cap
SPECK = "#d2ff52"
SPORE = "#c8ff60"
PUFF, PUFF_B = "#d4d8b4", "#aab48c"  # spore clouds: soft, not lit, with glowing spores in them
BULB = "#c4ff48"
GLOW = "#9aff58"
MOTHS = "#f4ffd2"
WINDOW, LAMP = "#ffc46a", "#ffd27a"
PIT = "#ff9a30"  # the morels glow amber
VEIN, VEIN_B = "#a4ff3c", "#d2ff6c"
BELL = "#d8a8ff"  # the wavecaps' bells, lilac: the one cool light among the green
TIP = "#ffe07a"

# The corridor's Spore Hollow colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#523c34", "FloorB": "#4a362f", "Dirt": "#3c2c28", "DirtB": "#352723", "Grass": "#ccc4ac"}
SKY = "#12140e"


def prop(name, **colours):
    return mk.prop(name, **colours)


# ---------------------------------------------------------------------- shape helpers

# Cap shapes: (height share, radius share) from the rim (0) up to the crown (1).
PROFILES = {
    "dome": ((0, 1.0), (0.35, 0.94), (0.65, 0.76), (0.88, 0.48), (1, 0.16)),
    "flat": ((0, 1.0), (0.45, 0.8), (0.8, 0.44), (1, 0.2)),
    "bell": ((0, 1.0), (0.3, 0.9), (0.6, 0.72), (0.85, 0.46), (1, 0.14)),
    "cone": ((0, 1.0), (0.5, 0.58), (1, 0.06)),
}


def share(profile, t):
    for (t0, s0), (t1, s1) in zip(profile, profile[1:]):
        if t <= t1:
            return s0 + (s1 - s0) * (t - t0) / (t1 - t0)
    return profile[-1][1]


def cap(m, role, centre, r, h, shape="dome", rot=None, sides=12, crown=None, under=None, lip=None):
    """A mushroom cap round centre (the middle of its rim), built up its frame's Z: slices from the rim to the crown
    (the top half in `crown` if given) and a lip under the rim. under: a glowing gill disc showing below the lip,
    with radial gills hanging from it, in that role. Returns its frame."""
    f = Frame(m, centre, rot)
    prof = PROFILES[shape]
    for (t0, s0), (t1, s1) in zip(prof, prof[1:]):
        f.prism(crown if crown and t0 >= 0.5 else role, 0, 0, h * t0, h * t1, r * s0, r * s1, sides)
    lip = h * 0.16 if lip is None else lip
    f.prism(role, 0, 0, -lip, 0, r * 0.9, r, sides)
    if under:
        f.prism(under, 0, 0, -lip * 1.25, -lip * 0.4, r * 0.78, r * 0.78, sides)
        if r > 0.9:
            n = 16 if r > 3 else 10
            g = max(0.12, lip * 0.4)
            for k in range(n):
                a = (k + 0.5) * math.tau / n
                f.box(under, math.cos(a) * r * 0.46, math.sin(a) * r * 0.46, -lip * 1.25 - g * 0.35, r * 0.56, max(0.1, r * 0.035), g,
                      turn(z=a))
    return f


def specks(m, role, f, r, h, shape, count, size, rng, t_range=(0.1, 0.7)):
    """Glowing spots scattered over a cap built by cap() in frame f, each lying on the cap's slope."""
    prof = PROFILES[shape]
    for k in range(count):
        t = rng.uniform(*t_range)
        a = (k + rng.uniform(-0.3, 0.3)) * math.tau / count
        rr = r * share(prof, t)
        dr = r * (share(prof, min(t + 0.04, 1)) - share(prof, max(t - 0.04, 0))) / 0.08
        tilt = math.atan2(h, -dr)
        f.box(role, math.cos(a) * rr * 0.97, math.sin(a) * rr * 0.97, h * t, size, size, size * 0.3, turn(y=tilt, z=a))


def shroom(m, x, y, h, r, cap_r, cap_h, lean=(0.0, 0.0), z0=0.0, cap_role="Cap", crown=None, under="GillGlow", n_specks=0, rng=None,
           shape="dome", stalk="Stalk", skirt=None, bulb=None, sides=12, speck="Speck", speck_size=None):
    """One mushroom standing at (x, y, z0): a stalk h tall (radius r at the foot, a fifth less at the top) leaning
    by `lean` at the top, a cap of radius cap_r and height cap_h on it tilted with the lean, gills glowing under it
    (`under`) and n_specks glowing spots on it. skirt: the role of a ring round the stalk at three quarters of its
    height; bulb: the role of a swollen foot. Returns the cap's frame."""
    lx, ly = lean
    top = h + cap_h * 0.3
    k = top / h
    prism(m, stalk, x, y, z0, z0 + top, r, r * 0.8, 8, math.pi / 8, (lx * k, ly * k))
    if bulb:
        ball(m, bulb, x, y, z0 + r * 0.5, r * 1.45, 8, 4)
    if skirt:
        zs = h * 0.72
        cx, cy = x + lx * zs / h, y + ly * zs / h
        rs = r - r * 0.2 * zs / top
        drop = max(0.2, h * 0.05)
        prism(m, skirt, cx, cy, z0 + zs - drop, z0 + zs, rs + r * 0.6, rs + r * 0.12, 10)
    rot = turn(x=-math.atan2(ly, h) * 0.8, y=math.atan2(lx, h) * 0.8)
    f = cap(m, cap_role, (x + lx, y + ly, z0 + h), cap_r, cap_h, shape, rot, sides, crown, under)
    if n_specks:
        specks(m, speck, f, cap_r, cap_h, shape, n_specks, speck_size or cap_r * 0.16, rng or random.Random(1))
    return f


def mound(m, role, x, y, r, h, sides=10, z0=0.0):
    """A low round mound of soil or moss."""
    prism(m, role, x, y, z0, z0 + h * 0.55, r, r * 0.82, sides, math.pi / sides)
    prism(m, role, x, y, z0 + h * 0.55, z0 + h, r * 0.82, r * 0.42, sides, math.pi / sides)


def patches(m, role, rng, count, r0, r1, size=(0.8, 1.6), cx=0.0, cy=0.0, z0=0.0):
    """Flat patches of mycelium or moss on the ground round (cx, cy), each a little thicker or thinner than the
    next, so no two tops lie in one plane; moss is always thinner than mycelium, so theirs never do either."""
    lo, hi = (0.04, 0.085) if role == "Moss" else (0.095, 0.15)
    for _ in range(count):
        a, rr = rng.uniform(0, math.tau), rng.uniform(r0, r1)
        s = rng.uniform(*size)
        thick = rng.uniform(lo, hi)
        obox(m, role, (cx + math.cos(a) * rr, cy + math.sin(a) * rr, z0 + thick / 2), (s, s * rng.uniform(0.5, 0.9), thick), turn(z=rng.uniform(0, math.tau)))


def stem_path(m, role, pts, r0, r1, sides=8):
    """A round stalk bending through pts, tapering from r0 to r1, with a ball at each bend so it has no gaps."""
    n = len(pts) - 1
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        ra, rb = r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n
        tube(m, role, a, b, ra, rb, sides)
        if i < n - 1:
            ball(m, role, *b, rb, sides, 4)


def spore_column(m, role, x, y, z0, z1, gap, size, rng):
    """Spores in a column exactly `gap` apart from z1 down to z0, each turned its own way, so falling `gap` over a
    period (or rising: fall = -gap) loops seamlessly: each only goes as far as where the next began."""
    z = z1
    while z > z0:
        obox(m, role, (x + rng.uniform(-0.15, 0.15), y + rng.uniform(-0.15, 0.15), z), (size, size, size),
             turn(rng.uniform(0, 1.5), rng.uniform(0, 1.5), rng.uniform(0, math.tau)))
        z -= gap


def moths(m, rng, count, r0, r1, z0, z1, role="Moths", size=0.55):
    """Glowing moths scattered round the origin, each facing round it, so they fly in a ring when the role spins."""
    for _ in range(count):
        a, rr = rng.uniform(0, math.tau), rng.uniform(r0, r1)
        f = Frame(m, (math.cos(a) * rr, math.sin(a) * rr, rng.uniform(z0, z1)), turn(z=a))
        f.box(role, 0, 0, 0, size * 0.18, size * 0.55, size * 0.18)
        for s in (-1, 1):
            f.box(role, s * size * 0.42, -size * 0.05, size * 0.1, size * 0.75, size * 0.55, size * 0.05, turn(y=-s * 0.45))


CLOUD = ((0, 0, 0, 1.0), (0.4, -0.22, 0.2, 0.66), (-0.36, 0.26, 0.1, 0.6), (0.05, 0.32, -0.28, 0.55))
CLOUD_SPORES = ((0.72, 0.15, 0.3), (-0.62, -0.42, -0.1), (0.12, -0.7, 0.42), (-0.2, 0.62, -0.38))


def cloud_column(m, x, y, z0, count, gap, size, grow=0.15, role="Puff", shade="PuffB", spore="Spore", turn_by=0.0):
    """A column of spore clouds `gap` apart, each a lumpy cluster a little bigger than the one below, glowing spores
    caught in each. Every cloud has the same shape, so rising `gap` over a period (fall = -gap) loops with barely a
    jump: each cloud only goes as far as where the next began."""
    c, s_ = math.cos(turn_by), math.sin(turn_by)
    for k in range(count):
        s = size * (1 + grow * k)
        z = z0 + gap * k
        for i, (dx, dy, dz, f) in enumerate(CLOUD):
            rx, ry = dx * c - dy * s_, dx * s_ + dy * c
            m.block(shade if i == 3 else role, x + rx * s, y + ry * s, z + dz * s, s * f, s * f, s * f * 0.85)
        if spore:
            for dx, dy, dz in CLOUD_SPORES:
                rx, ry = dx * c - dy * s_, dx * s_ + dy * c
                m.block(spore, x + rx * s, y + ry * s, z + dz * s, max(0.18, s * 0.16), max(0.18, s * 0.16), max(0.18, s * 0.16))


def motes(m, rng, count, r0, r1, z0, z1, role="Motes", size=0.24):
    for _ in range(count):
        a, rr = rng.uniform(0, math.tau), rng.uniform(r0, r1)
        m.block(role, math.cos(a) * rr, math.sin(a) * rr, rng.uniform(z0, z1), size, size, size)


def bracket(m, x, y, z, r, role="Shelf", top="ShelfDark", under="GillGlow", sides=12):
    """A shelf fungus: a flat round shelf centred on a trunk's or wall's face (so half of it sinks in), its top
    domed, its underside glowing."""
    prism(m, role, x, y, z, z + r * 0.28, r, r * 0.88, sides)
    prism(m, top, x, y, z + r * 0.28, z + r * 0.4, r * 0.88, r * 0.55, sides)
    if under:
        prism(m, under, x, y, z - r * 0.1, z + 0.02, r * 0.84, r * 0.84, sides)


def puffball(m, role, x, y, r, squash=0.85, sides=10, rings=5, z=None):
    """A round puffball sitting on the ground, a little squashed. Returns the height of its top."""
    rz = r * squash
    zc = rz * 0.82 if z is None else z
    for k in range(rings):
        a0 = -math.pi / 2 + k * math.pi / rings
        a1 = a0 + math.pi / rings
        prism(m, role, x, y, zc + rz * math.sin(a0), zc + rz * math.sin(a1), max(r * math.cos(a0), 0.03), max(r * math.cos(a1), 0.03),
              sides, math.pi / sides)
    return zc + rz


def torn_top(m, x, y, top, r, rng, skin="Puffskin", glow="Glow"):
    """A puffball's torn opening: a ring of ragged lips round a glowing hole."""
    prism(m, glow, x, y, top - r * 0.5, top - r * 0.05, r * 0.7, r * 0.62, 8)
    for k in range(7):
        a = k * math.tau / 7 + rng.uniform(-0.2, 0.2)
        d = Vector((math.cos(a), math.sin(a), 0))
        base = Vector((x, y, top - r * 0.3)) + d * r * 0.72
        tip = base + d * r * 0.25 + Vector((0, 0, r * rng.uniform(0.35, 0.6)))
        mk.plate(m, skin, tuple(base), tuple(tip), (-d.y, d.x, 0), r * 0.55, r * 0.15, r * 0.1)


def warts(m, role, x, y, zc, r, rz, count, rng, size):
    """Little bumps over a puffball's upper half."""
    for _ in range(count):
        a, e = rng.uniform(0, math.tau), rng.uniform(0.25, 1.1)
        p = (x + math.cos(a) * math.cos(e) * r, y + math.sin(a) * math.cos(e) * r, zc + math.sin(e) * rz)
        obox(m, role, p, (size, size, size * 0.6), turn(y=math.pi / 2 - e, z=a))


# ---------------------------------------------------------------------- floor props


def glowcap(seed=1):
    """The map's signature: a giant rust-red mushroom on a ringed stalk rising from a swollen foot, its cap
    freckled with glowing specks, its gills glowing chartreuse and glowing spores sifting down from them for ever;
    two smaller ones and a tiny glowing one at its foot, in a patch of loam and mycelium."""
    m = prop("Glowcap", Stalk=STALK, StalkShade=STALK_SHADE, Cap=CAP, CapDark=CAP_DARK, CapB=CAP_B, GillGlow=GILL, Speck=SPECK, Spore=SPORE,
             Loam=LOAM, Mycel=MYCEL, Moss=MOSS, Glow=GLOW)
    rng = random.Random(seed)
    mound(m, "Loam", 0, 0, 2.4, 0.7)
    patches(m, "Mycel", rng, 6, 1.6, 3.2)
    patches(m, "Moss", rng, 3, 2.0, 3.0, (0.6, 1.1))
    shroom(m, 0, 0, 7.6, 0.74, 3.5, 2.4, (0.5, 0.3), crown="CapDark", n_specks=10, rng=rng, skirt="StalkShade", bulb="Stalk",
           speck_size=0.55, sides=14)
    shroom(m, 1.9, -1.3, 3.1, 0.34, 1.45, 1.0, (0.25, -0.15), cap_role="CapB", n_specks=4, rng=rng, skirt="StalkShade")
    shroom(m, -1.8, 1.1, 2.1, 0.26, 1.0, 0.75, (-0.15, 0.1), n_specks=3, rng=rng)
    shroom(m, -1.0, -1.7, 0.9, 0.14, 0.45, 0.4, (0.05, -0.05), cap_role="Glow", under=None)
    shroom(m, 0.9, 1.9, 0.6, 0.12, 0.35, 0.3, cap_role="Glow", under=None)
    for k in range(5):  # spores sifting down from the big cap's gills, 2.5 apart
        a = k * math.tau / 5 + 0.4
        spore_column(m, "Spore", 0.5 + math.cos(a) * 2.3, 0.3 + math.sin(a) * 2.3, 0.4, 6.9, 2.5, 0.2, rng)
    return m


def puffballs(seed=2):
    """A cluster of fat cream puffballs, warty on top, the two biggest torn open and puffing clouds of glowing
    spores up out of their tops for ever; glowing specks round the holes."""
    m = prop("Puffballs", Puffskin="#e9e0c8", Wart=WART, Glow=GLOW, Puff=PUFF, PuffB=PUFF_B, Spore=SPORE, Loam=LOAM, Moss=MOSS, Mycel=MYCEL,
             Speck=SPECK)
    rng = random.Random(seed)
    mound(m, "Loam", 0.3, 0, 3.4, 0.5)
    patches(m, "Moss", rng, 5, 1.5, 3.6, (0.8, 1.4))
    patches(m, "Mycel", rng, 4, 2.5, 3.8)
    for x, y, r, opened in ((0, 0, 2.2, True), (2.7, 1.0, 1.3, True), (-2.3, 1.4, 1.0, False), (1.3, -2.4, 0.85, False), (-1.7, -1.7, 0.6, False),
                            (3.1, -1.3, 0.45, False)):
        top = puffball(m, "Puffskin", x, y, r, z=0.3 + r * 0.85 * 0.82)
        warts(m, "Wart", x, y, top - r * 0.85, r, r * 0.85, int(4 + r * 4), rng, max(0.16, r * 0.14))
        if opened:
            torn_top(m, x, y, top, r * 0.5, rng)
    cloud_column(m, 0, 0, 4.4, 4, 2.0, 0.85, grow=0.22)
    cloud_column(m, 2.7, 1.0, 3.4, 3, 2.0, 0.5, grow=0.22, turn_by=1.3)
    for k in range(6):
        a = k * math.tau / 6
        m.block("Speck", math.cos(a) * 1.25, math.sin(a) * 1.25, 3.55, 0.2, 0.2, 0.2)
    return m


def lamp_shroom(seed=3):
    """A lamp mushroom: a tall stalk curling over at the top like a lamp post, a little cap on its tip and a
    glowing bulb hanging from it on a thread, swinging; three small mushrooms with glowing caps at its foot and moths
    circling the light. The bulb's hook is on the X line at its height, so the game swings it round there."""
    m = prop("LampShroom", Stalk=STALK, StalkShade=STALK_SHADE, CapB=CAP_B, CapBDark=CAP_B_DARK, BulbStem="#8a7a5a", Bulb=BULB, Glow=GLOW,
             GillGlow=GILL, Loam=LOAM, Moss=MOSS, Mycel=MYCEL, Moths=MOTHS)
    rng = random.Random(seed)
    mound(m, "Loam", 0, 0, 1.9, 0.6)
    patches(m, "Moss", rng, 4, 1.0, 2.4, (0.6, 1.2))
    patches(m, "Mycel", rng, 3, 1.4, 2.6)
    ball(m, "Stalk", 0, 0, 0.5, 0.75, 8, 4)
    hook = 8.1
    pts = [(0, 0, 0.3), (0.25, 0, 2.6), (0.05, 0, 5.0), (0.45, 0, 7.4), (1.4, 0, 8.75), (2.6, 0, 9.0), (3.35, 0, hook + 0.35)]
    stem_path(m, "Stalk", pts, 0.5, 0.24)
    for z in (1.6, 3.4, 5.6):  # rings up the stalk
        x = 0.25 * min(z / 2.6, 1) if z < 5 else 0.1
        prism(m, "StalkShade", x, 0, z - 0.1, z + 0.1, 0.5, 0.5, 8, math.pi / 8)
    cap(m, "CapB", (3.3, 0, hook + 0.55), 0.85, 0.65, "dome", turn(y=0.5), 10, "CapBDark", "GillGlow")
    # The bulb on its thread: everything that swings hangs from the hook.
    beam(m, "BulbStem", (3.35, 0, hook + 0.1), (3.35, 0, hook - 1.0), 0.1)
    cap(m, "BulbStem", (3.35, 0, hook - 1.15), 0.42, 0.3, "dome", None, 8)
    ball(m, "Bulb", 3.35, 0, hook - 1.75, 0.66, 10, 5)
    m.block("Bulb", 3.35, 0, hook - 2.55, 0.18, 0.18, 0.35)
    for x, y, h, r in ((-1.3, 0.9, 3.4, 0.85), (1.0, -1.2, 2.0, 0.6), (-0.6, -1.4, 1.2, 0.42)):
        shroom(m, x, y, h, r * 0.3, r, r * 0.85, (rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2)), cap_role="Glow", under=None, shape="bell")
    moths(m, rng, 8, 2.0, 4.2, 5.0, 9.5)
    return m


def wavecaps(seed=4):
    """Three tall thin stalks with glowing lilac bells on top, each swaying its own way in air that doesn't move. Each
    stalk sways round its own foot: A and C stand on the X line and sway across it, B on the Y line and sways along."""
    m = prop("Wavecaps", WandA=STALK, WandB=STALK, WandC=STALK, BellA=BELL, BellB=BELL, BellC=BELL, Loam=LOAM, Moss=MOSS, Mycel=MYCEL,
             Glow=GLOW, Stalk=STALK)
    rng = random.Random(seed)
    for (fx, fy), h, wand, bell, bend in (((-1.1, 0), 8.2, "WandA", "BellA", (-0.5, 0.6)), ((0, 0.95), 9.8, "WandB", "BellB", (0.7, 0.2)),
                                          ((1.2, 0), 6.6, "WandC", "BellC", (0.5, -0.5))):
        bx, by = bend
        pts = [(fx, fy, 0), (fx + bx * 0.3, fy + by * 0.2, h * 0.35), (fx + bx * 0.1, fy + by * 0.7, h * 0.7), (fx + bx, fy + by, h)]
        stem_path(m, wand, pts, 0.3, 0.18, 6)
        cap(m, bell, (fx + bx, fy + by, h - 0.3), 0.85, 1.9, "bell", None, 10)
        prism(m, bell, fx + bx, fy + by, h + 1.5, h + 1.85, 0.2, 0.05, 6)  # its little point
    mound(m, "Loam", 0, 0.3, 2.2, 0.8)
    patches(m, "Moss", rng, 4, 1.2, 2.6, (0.6, 1.2))
    patches(m, "Mycel", rng, 4, 1.8, 3.0)
    for k in range(4):
        a = k * math.tau / 4 + 0.7
        shroom(m, math.cos(a) * 1.9, 0.3 + math.sin(a) * 1.9, rng.uniform(0.5, 1.0), 0.1, 0.32, 0.3, cap_role="Glow", under=None)
    return m


def shelf_stump(seed=5):
    """A rotten tree stump, hollow and jagged at the top, roots clawing the ground, shelf fungi stepping up its
    sides with their undersides glowing, little glowing mushrooms on its rim and moths circling it."""
    m = prop("ShelfStump", Bark=BARK, BarkDark=BARK_DARK, Shelf=SHELF, ShelfDark=SHELF_DARK, GillGlow=GILL, Glow=GLOW, Stalk=STALK, Loam=LOAM,
             Mycel=MYCEL, Moss=MOSS, Moths=MOTHS)
    rng = random.Random(seed)
    prism(m, "Bark", 0, 0, 0, 3.8, 1.75, 1.45, 9, 0.2)
    for k in range(9):  # bark strips
        a = 0.2 + (k + 0.5) * math.tau / 9
        r = 1.62
        obox(m, "BarkDark", (math.cos(a) * r, math.sin(a) * r, 1.8), (0.35, 0.3, 3.4 - (k % 3) * 0.5), turn(y=0.04, z=a))
    for k, hgt in enumerate((1.6, 0.7, 1.2, 0.5, 1.9, 0.9)):  # the jagged broken top
        a = k * math.tau / 6 + 0.3
        prism(m, "Bark" if k % 2 else "BarkDark", math.cos(a) * 1.15, math.sin(a) * 1.15, 3.7, 3.8 + hgt, 0.42, 0.06, 4, a)
    prism(m, "BarkDark", 0, 0, 3.6, 3.86, 1.2, 1.2, 9, 0.2)  # the rotten hollow
    for k in range(5):  # roots
        a = k * math.tau / 5 + 0.5
        limb(m, "BarkDark", [(math.cos(a) * 1.2, math.sin(a) * 1.2, 1.0), (math.cos(a) * 2.2, math.sin(a) * 2.2, 0.5),
                             (math.cos(a) * 3.1, math.sin(a) * 3.1, 0.06)], 0.6, 0.25)
    for a, z, r in ((0.3, 1.0, 1.25), (0.95, 1.95, 1.0), (0.25, 2.9, 0.85), (2.6, 1.45, 1.15), (3.25, 2.55, 0.8), (4.6, 0.8, 0.95), (5.2, 2.2, 0.7)):
        rr = 1.75 - 0.3 * z / 3.8
        bracket(m, math.cos(a) * rr, math.sin(a) * rr, z, r)
    for x, y, h in ((0.5, 0.4, 0.9), (-0.4, -0.3, 0.6), (0.1, -0.6, 0.4)):
        shroom(m, x, y, h, 0.1, 0.3, 0.26, z0=3.86, cap_role="Glow", under=None)
    patches(m, "Mycel", rng, 5, 1.8, 3.2)
    patches(m, "Moss", rng, 3, 2.0, 3.0, (0.6, 1.1))
    moths(m, rng, 8, 2.2, 3.8, 2.0, 6.0)
    return m


def coral_shroom(seed=6):
    """Orange coral fungus branching up out of a mound, every tip glowing gold, motes drifting round it."""
    m = prop("CoralShroom", Coral=CORAL, CoralDark=CORAL_DARK, TipGlow=TIP, Loam=LOAM, Moss=MOSS, Mycel=MYCEL, Motes=SPECK)
    rng = random.Random(seed)
    mound(m, "Loam", 0, 0, 1.8, 0.6)
    patches(m, "Moss", rng, 3, 1.0, 2.2, (0.6, 1.0))

    def branch(p, d, length, width, depth):
        end = p + d * length
        beam(m, "Coral" if depth % 2 else "CoralDark", tuple(p), tuple(end), width, None, width * 0.8)
        if depth == 0:
            ball(m, "TipGlow", *end, max(0.18, width * 0.9), 6, 3)
            return
        m.block("Coral" if depth % 2 else "CoralDark", *end, width * 0.8, width * 0.8, width * 0.8)
        for j in range(rng.choice((2, 3))):  # forks that keep reaching up, like antlers
            side = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)).normalized() * rng.uniform(0.25, 0.5)
            nd = (Vector((0, 0, 1)) + side + d * 0.3).normalized()
            branch(end, nd, length * 0.7, width * 0.75, depth - 1)

    prism(m, "CoralDark", 0, 0, 0, 1.0, 1.3, 1.0, 9)  # the fleshy base the prongs rise from
    for k in range(9):
        a = k * math.tau / 9 + rng.uniform(-0.2, 0.2)
        rr = 0.35 + 0.55 * (k % 3) / 2
        out = Vector((math.cos(a), math.sin(a), 0))
        branch(out * rr + Vector((0, 0, 0.8)), (out * 0.25 + Vector((0, 0, 1))).normalized(), rng.uniform(1.6, 2.3), 0.42, 2)
    motes(m, rng, 8, 1.6, 3.0, 2.0, 5.5)
    return m


def mycelium_heart(seed=7):
    """A rare find: the mycelium heart. A great ribbed aubergine bulb half sunk in a heap of soil, glowing veins over
    it, beating (it rises and sinks a little, its veins flaring with each beat); glowing veins run out from it
    across the ground through felted mycelium, and spores rise from the opening on its top."""
    m = prop("MyceliumHeart", Heart=HEART, HeartRib=HEART_RIB, HeartGlow="#d6ff6a", Vein=VEIN, VeinB=VEIN_B, Spore=SPORE, Mycel=MYCEL,
             Loam=LOAM, LoamDark=LOAM_DARK, Glow=GLOW, Stalk=STALK)
    rng = random.Random(seed)
    zc, rx, rz = 2.0, 2.9, 3.2
    rings = 7
    prof = []
    for k in range(rings + 1):  # an egg-shaped bulb, from under the ground up to its opening
        a = -math.pi / 2 + k * math.pi / rings
        prof.append((zc + rz * math.sin(a), max(rx * math.cos(a) * (1 - 0.12 * math.sin(a)), 0.5)))
    for (z0, r0), (z1, r1) in zip(prof, prof[1:]):
        prism(m, "Heart", 0, 0, z0, z1, r0, r1, 12, 0)
    for k in range(6):  # ribs, at every other corner
        a = k * math.tau / 6
        pts = [(math.cos(a) * r * 1.04, math.sin(a) * r * 1.04, z) for z, r in prof[1:-1]]
        limb(m, "HeartRib", pts, 0.42, 0.3)
    for k in range(6):  # glowing veins between the ribs, branching up
        a = (k + 0.5) * math.tau / 6
        pts = []
        for z, r in prof[2:-1]:
            wob = rng.uniform(-0.18, 0.18)
            pts.append((math.cos(a + wob) * r * 1.0, math.sin(a + wob) * r * 1.0, z))
        limb(m, "HeartGlow", pts, 0.2, 0.14)
    top = prof[-1][0]
    prism(m, "HeartGlow", 0, 0, top - 0.5, top + 0.12, 0.62, 0.62, 8)  # the opening, glowing
    for k in range(5):  # flaps round the opening
        a = k * math.tau / 5
        d = Vector((math.cos(a), math.sin(a), 0))
        mk.plate(m, "Heart", tuple(d * 0.45 + Vector((0, 0, top - 0.2))), tuple(d * 1.0 + Vector((0, 0, top + 0.5))), (-d.y, d.x, 0), 0.7, 0.2, 0.14)
    prism(m, "LoamDark", 0, 0, 0, 0.55, rx * 1.2, rx * 1.02, 12, 0)  # the soil heaped round its foot
    prism(m, "Loam", 0, 0, 0, 0.3, rx * 1.55, rx * 1.2, 12, 0.26)
    patches(m, "Mycel", rng, 7, rx * 1.4, rx * 2.4, (0.9, 1.6))
    # Veins over the ground, running out from it and branching.
    for k in range(8):
        a = k * math.tau / 8 + rng.uniform(-0.2, 0.2)
        role, z = ("Vein", 0.05) if k % 2 else ("VeinB", 0.07)
        p = Vector((math.cos(a) * rx * 1.15, math.sin(a) * rx * 1.15, z))
        d = Vector((math.cos(a), math.sin(a), 0))
        for j in range(3):
            q = p + (d + Vector((-d.y, d.x, 0)) * rng.uniform(-0.5, 0.5)).normalized() * rng.uniform(1.2, 1.8)
            beam(m, role, tuple(p), tuple(q), 0.26 - j * 0.05, 0.08 + (0.02 if role == "VeinB" else 0))
            if j == 1:
                side = (d + Vector((-d.y, d.x, 0)) * rng.choice((-1, 1)) * 1.2).normalized()
                beam(m, role, tuple(q), tuple(q + side * 1.2), 0.14, 0.08 + (0.02 if role == "VeinB" else 0))
            p = q
        if k % 3 == 0:
            shroom(m, p.x, p.y, 0.7, 0.09, 0.3, 0.26, cap_role="Glow", under=None)
    for k in range(3):  # spores rising from its top, 2 apart
        a = k * math.tau / 3
        spore_column(m, "Spore", math.cos(a) * 0.3, math.sin(a) * 0.3, top + 0.6, top + 7.0, 2.0, 0.2, rng)
    return m


def mushroom_hut(seed=8):
    """A rare treat: a mushroom someone moved into. Its fat stalk is the house, with a round door, lit windows and
    a stone step; its cap is the roof, chocolate freckled with glowing specks; a crooked chimney pokes through it smoking,
    and a lantern hangs by the wall on a bracket and swings (its hook is on the X line at its height)."""
    m = prop("MushroomHut", Stalk=STALK, StalkShade=STALK_SHADE, CapB=CAP_B, CapBDark=CAP_B_DARK, Speck=SPECK, GillGlow=GILL, Door=WOOD,
             Wood=WOOD_DARK, Window=WINDOW, Stone=STONE, Chimney=CHIMNEY, Smoke="#8c8a78", SmokeLight="#aaa894", Iron=IRON, Lantern=IRON,
             Lamp=LAMP, Glow=GLOW, Moss=MOSS, Mycel=MYCEL)
    rng = random.Random(seed)
    prism(m, "Stone", 0, 0, 0, 0.4, 2.95, 2.85, 12, math.pi / 12)
    wall = ((0.4, 2.55), (1.8, 2.7), (3.6, 2.6), (5.3, 2.25))
    for (z0, r0), (z1, r1) in zip(wall, wall[1:]):
        prism(m, "Stalk", 0, 0, z0, z1, r0, r1, 12, math.pi / 12)  # a face looks straight down +Y
    prism(m, "StalkShade", 0, 0, 0.45, 0.8, 2.64, 2.64, 12, math.pi / 12)

    def on_wall(a, z):
        r = next(r0 + (r1 - r0) * (z - z0) / (z1 - z0) for (z0, r0), (z1, r1) in zip(wall, wall[1:]) if z0 <= z <= z1)
        d = r * math.cos(math.pi / 12)
        return Frame(m, (math.cos(a) * d, math.sin(a) * d, z), turn(z=a - math.pi / 2))

    # The door, round-topped, with a frame and a knob.
    f = on_wall(math.pi / 2, 1.6)
    f.box("Door", 0, 0.08, 0, 1.3, 0.2, 2.2)
    f.box("Wood", 0, 0.12, 1.1, 1.6, 0.2, 0.22)
    for s in (-1, 1):
        f.box("Wood", s * 0.74, 0.12, 0, 0.2, 0.22, 2.4)
    f.box("Iron", 0.4, 0.22, 0, 0.14, 0.12, 0.14)
    for a, z in ((math.pi / 2 - math.pi / 3, 2.9), (math.pi / 2 + math.pi / 3, 2.6), (-math.pi / 2, 3.1)):  # round-ish lit windows
        f = on_wall(a, z)
        f.box("Window", 0, 0.05, 0, 0.9, 0.12, 0.6)
        f.box("Window", 0, 0.05, 0, 0.6, 0.12, 0.9)
        f.box("Wood", 0, 0.12, 0, 0.1, 0.1, 0.92)
        f.box("Wood", 0, 0.12, 0, 0.92, 0.1, 0.1)
        f.box("Wood", 0, 0.1, -0.55, 1.1, 0.25, 0.14)
    m.block("Stone", 0, 3.35, 0.12, 1.6, 0.9, 0.24)  # stepping stones
    m.block("Stone", 0.3, 4.5, 0.08, 1.2, 0.8, 0.16)
    # The roof: a big spotted cap, glowing underneath.
    f = cap(m, "CapB", (0, 0, 5.1), 4.6, 3.2, "dome", None, 14, "CapBDark", "GillGlow")
    specks(m, "Speck", f, 4.6, 3.2, "dome", 12, 0.7, rng)
    # A crooked chimney through the roof, smoking.
    beam(m, "Chimney", (1.6, -1.2, 6.0), (1.85, -1.45, 9.2), 0.75)
    m.block("Chimney", 1.87, -1.47, 9.35, 1.0, 1.0, 0.4)
    puffs(m, "Smoke", 1.9, -1.5, 10.2, 4, 1.5, 0.8, grow=0.15, shade="SmokeLight")
    # The lantern on its bracket, on the X line at the hook's height.
    hook = 4.0
    beam(m, "Iron", (2.45, 0, hook + 0.15), (3.6, 0, hook + 0.15), 0.16)
    beam(m, "Iron", (2.5, 0, hook - 0.6), (3.1, 0, hook + 0.15), 0.12)
    for i in range(2):
        z = hook - i * 0.35
        beam(m, "Lantern", (3.6, 0, z), (3.6, 0, z - 0.35), *((0.22, 0.08) if i % 2 else (0.08, 0.22)))
    zl = hook - 0.8
    m.block("Lantern", 3.6, 0, zl, 0.75, 0.75, 0.12)
    m.loft_z("Lantern", (zl, 3.6, 0, 0.65, 0.65), (zl + 0.3, 3.6, 0, 0.18, 0.18))
    m.block("Lamp", 3.6, 0, zl - 0.5, 0.5, 0.5, 0.85)
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        m.block("Lantern", 3.6 + sx * 0.3, sy * 0.3, zl - 0.5, 0.08, 0.08, 0.95)
    m.block("Lantern", 3.6, 0, zl - 0.98, 0.65, 0.65, 0.12)
    for x, y, h in ((-1.3, 3.2, 0.9), (1.4, 3.1, 0.6), (-2.6, 2.4, 0.5), (2.9, -1.8, 0.7)):
        shroom(m, x, y, h, 0.1, 0.32, 0.28, cap_role="Glow", under=None)
    patches(m, "Moss", rng, 5, 2.9, 4.0, (0.8, 1.3))
    patches(m, "Mycel", rng, 4, 3.0, 4.2)
    return m


def spore_tuft(seed=9):
    """Filler: a mossy hummock with a little cluster of glowing mushrooms."""
    m = prop("SporeTuft", Moss=MOSS, Loam=LOAM, Stalk=STALK, Glow=GLOW, Mycel=MYCEL)
    rng = random.Random(seed)
    mound(m, "Moss", 0, 0, 1.0, 0.55)
    patches(m, "Mycel", rng, 2, 0.8, 1.3, (0.4, 0.7))
    for k, (h, r) in enumerate(((1.6, 0.5), (1.1, 0.38), (0.8, 0.3), (1.3, 0.42), (0.6, 0.26))):
        a = k * math.tau / 5 + rng.uniform(-0.3, 0.3)
        d = 0.25 + 0.45 * (k % 3) / 2
        shroom(m, math.cos(a) * d, math.sin(a) * d, h, r * 0.26, r, r * 0.8, (math.cos(a) * 0.2, math.sin(a) * 0.2), z0=0.2, cap_role="Glow",
               under=None, shape="bell" if k % 2 else "dome")
    return m


def mycelium_web(seed=10):
    """A web of glowing mycelium lying flat on the floor, branching out from a felted middle, a few button
    mushrooms on it, its threads flaring in two rhythms. Flat (under half a stud), so it can lie in the middle
    where the eggs land."""
    m = prop("MyceliumWeb", Mycel=MYCEL, Vein=VEIN, VeinB=VEIN_B, Cap=CAP, Glow=GLOW)
    rng = random.Random(seed)
    prism(m, "Mycel", 0, 0, 0, 0.12, 1.5, 1.3, 10)

    def thread(p, a, length, width, depth):
        role, z, thick = ("Vein", 0.05, 0.08) if depth % 2 else ("VeinB", 0.06, 0.11)
        q = p + Vector((math.cos(a), math.sin(a), 0)) * length
        beam(m, role, (p.x, p.y, z), (q.x, q.y, z), width, thick, width * 0.7)
        if depth == 0:
            if rng.random() < 0.4:
                prism(m, "Cap", q.x, q.y, 0, 0.2, 0.42, 0.36, 8)
                prism(m, "Glow", q.x, q.y, 0.2, 0.36, 0.36, 0.2, 8)
            return
        for da in (-0.5, 0.45):
            thread(q, a + da + rng.uniform(-0.2, 0.2), length * 0.7, width * 0.72, depth - 1)

    for k in range(7):
        a = k * math.tau / 7 + rng.uniform(-0.2, 0.2)
        thread(Vector((math.cos(a) * 1.0, math.sin(a) * 1.0, 0)), a, rng.uniform(2.2, 2.9), 0.32, 2)
    return m


# ---------------------------------------------------------------------- rim props and landmarks


def parasol(seed=11):
    """A rim prop: a parasol mushroom as tall as a tree, its slender stalk banded like snakeskin with a double
    ring under the cap, its wide flat cap scaled brown and glowing underneath; spores sift down from it and moths
    circle round it."""
    m = prop("Parasol", Stalk=STALK, StalkShade=STALK_SHADE, CapC=CAP_C, CapDark=CAP_DARK, Scale=SCALE, GillGlow=GILL, Spore=SPORE, Loam=LOAM,
             Mycel=MYCEL, Moss=MOSS, Moths=MOTHS)
    rng = random.Random(seed)
    mound(m, "Loam", 0, 0, 2.0, 0.6)
    patches(m, "Mycel", rng, 5, 1.4, 3.0)
    h, lean = 12.2, (0.6, 0.2)
    f = shroom(m, 0, 0, h, 0.6, 5.4, 1.6, lean, cap_role="CapC", crown="CapDark", shape="flat", skirt="StalkShade", bulb="Stalk", sides=14)
    specks(m, "Scale", f, 5.4, 1.6, "flat", 22, 0.7, rng, (0.08, 0.6))
    f.prism("CapDark", 0, 0, 1.5, 1.9, 1.3, 0.7, 10)  # the bump on top
    for z in [1.4 + k * 1.05 for k in range(7)]:  # snakeskin bands
        t = z / h
        prism(m, "StalkShade", lean[0] * t, lean[1] * t, z - 0.12, z + 0.12, 0.6 - 0.12 * t + 0.05, 0.6 - 0.12 * t + 0.05, 8, math.pi / 8)
    zs = h * 0.72 - 0.9  # a second, lower ring under the skirt
    prism(m, "StalkShade", lean[0] * zs / h, lean[1] * zs / h, zs - 0.25, zs, 0.95, 0.6, 10)
    for k in range(6):  # spores sifting down from the gills, 3 apart
        a = k * math.tau / 6 + 0.2
        rr = 2.4 + (k % 2) * 1.6
        spore_column(m, "Spore", lean[0] + math.cos(a) * rr, lean[1] + math.sin(a) * rr, 0.6, h - 1.0, 3.0, 0.24, rng)
    moths(m, rng, 10, 3.5, 7.0, 7.5, 13.5)
    return m


def morel(m, x, y, s, rng, pit="Pit", ridge="Ridge", stalk="Stalk"):
    """A morel at size s: a short stalk and a tall honeycomb cone, glowing in its pits between the ridges."""
    prism(m, stalk, x, y, 0, 2.6 * s, 1.3 * s, 1.1 * s, 10, math.pi / 10)
    prof = [(2.2, 1.75), (3.6, 2.2), (6.2, 1.95), (8.8, 1.4), (11.0, 0.7), (12.4, 0.22)]
    prof = [(z * s, r * s) for z, r in prof]
    for (z0, r0), (z1, r1) in zip(prof, prof[1:]):
        prism(m, pit, x, y, z0, z1, r0, r1, 10, 0)
    n = 10
    for i in range(n):  # ridges up the cone, at its corners
        a = i * math.tau / n
        pts = [(x + math.cos(a) * r * 1.07, y + math.sin(a) * r * 1.07, z) for z, r in prof[:-1]]
        limb(m, ridge, pts, 0.42 * s, 0.3 * s)
    for k, z in enumerate((3.6, 5.3, 7.0, 8.7, 10.3)):  # rings round it, and zigzags between them for the honeycomb
        z *= s
        r = next(r0 + (r1 - r0) * (z - z0) / (z1 - z0) for (z0, r0), (z1, r1) in zip(prof, prof[1:]) if z0 <= z <= z1) * 1.07
        for i in range(n):
            a0, a1 = i * math.tau / n, (i + 1) * math.tau / n
            if (i + k) % 2:
                beam(m, ridge, (x + math.cos(a0) * r, y + math.sin(a0) * r, z), (x + math.cos(a1) * r, y + math.sin(a1) * r, z), 0.36 * s)
            else:
                beam(m, ridge, (x + math.cos(a0) * r, y + math.sin(a0) * r, z), (x + math.cos(a1) * r * 0.97, y + math.sin(a1) * r * 0.97,
                                                                                    z + 0.8 * s), 0.32 * s)
    prism(m, ridge, x, y, prof[-1][0] - 0.1 * s, prof[-1][0] + 0.4 * s, 0.42 * s, 0.1 * s, 6)
    return prof[-1][0] + 0.4 * s


def morel_spire(seed=12):
    """A rim prop: a morel as tall as a house, its honeycomb glowing amber deep in every pit, two small ones at its
    foot, and glowing spores rising off its tip for ever."""
    m = prop("MorelSpire", Stalk=STALK, StalkShade=STALK_SHADE, Pit=PIT, Ridge=RIDGE, Spore="#ffd08a", Loam=LOAM, Mycel=MYCEL, Moss=MOSS)
    rng = random.Random(seed)
    mound(m, "Loam", 0, 0, 2.4, 0.6)
    patches(m, "Mycel", rng, 5, 1.6, 3.4)
    patches(m, "Moss", rng, 3, 2.2, 3.4, (0.6, 1.0))
    top = morel(m, 0, 0, 1.0, rng)
    prism(m, "StalkShade", 0, 0, 1.0, 1.3, 1.3, 1.3, 10, math.pi / 10)
    morel(m, 2.6, 1.1, 0.34, rng)
    morel(m, -2.3, -1.5, 0.26, rng)
    for k in range(3):  # spores rising off its tip, 2.4 apart
        a = k * math.tau / 3
        spore_column(m, "Spore", math.cos(a) * 0.5, math.sin(a) * 0.5, top + 0.4, top + 10.0, 2.4, 0.26, rng)
    return m


def elder_shroom(seed=13):
    """A landmark for the rims: the elder shroom, a colossal rust-red mushroom that somebody lives in. A round
    door at its foot with steps, lit windows up its stalk, a stair of glowing shelf fungi winding up round it, a
    skirt under the cap; its cap is freckled with glowing specks and glows underneath, spores sift down from it and
    moths circle under it. Its door looks out of its Front."""
    m = prop("ElderShroom", Stalk=STALK, StalkShade=STALK_SHADE, Cap=CAP, CapDark=CAP_DARK, GillGlow=GILL, Speck=SPECK, Spore=SPORE,
             Shelf=SHELF, ShelfDark=SHELF_DARK, Door=WOOD, Wood=WOOD_DARK, Window=WINDOW, Stone=STONE, Glow=GLOW, Loam=LOAM, Mycel=MYCEL,
             Moss=MOSS, Moths=MOTHS, Front="#ff00ff")
    rng = random.Random(seed)
    h, lean, r0, r1 = 21.0, 1.0, 3.6, 2.7

    def radius(z):
        return r0 + (r1 - r0) * z / (h + 2.1)

    def off(z):
        return lean * z / h

    mound(m, "Loam", 0, 0, 6.5, 0.8, 14)
    patches(m, "Mycel", rng, 9, 4.0, 8.0, (1.2, 2.4))
    patches(m, "Moss", rng, 5, 5.0, 8.0, (1.0, 1.8))
    prism(m, "Stalk", 0, 0, 0, h + 2.1, r0, r1, 12, math.pi / 12, (lean * (h + 2.1) / h, 0))
    for k in range(7):  # roots flaring out round its foot, leaving the door clear
        a = k * math.tau / 7 + 2.3
        d = Vector((math.cos(a), math.sin(a), 0))
        limb(m, "Stalk", [tuple(d * 2.8 + Vector((0, 0, 2.6))), tuple(d * 4.4 + Vector((0, 0, 0.9))), tuple(d * 6.0 + Vector((0, 0, 0.1)))], 1.7, 0.7)
    for z in (5.0, 10.5):  # faint bands
        prism(m, "StalkShade", off(z), 0, z - 0.2, z + 0.2, radius(z) + 0.08, radius(z) + 0.08, 12, math.pi / 12)
    zs = 16.0
    prism(m, "StalkShade", off(zs), 0, zs - 0.9, zs, radius(zs) + 1.7, radius(zs) + 0.3, 12, math.pi / 12)

    def on_face(a, z):
        d = radius(z) * math.cos(math.pi / 12)
        return Frame(m, (off(z) + math.cos(a) * d, math.sin(a) * d, z), turn(z=a - math.pi / 2))

    f = on_face(math.pi / 2, 2.4)  # the door
    f.box("Door", 0, 0.12, 0, 1.9, 0.3, 3.6)
    f.box("Wood", 0, 0.2, 1.95, 2.4, 0.3, 0.35)
    for s in (-1, 1):
        f.box("Wood", s * 1.1, 0.2, 0, 0.3, 0.32, 4.2)
    f.box("Wood", 0.55, 0.32, 0, 0.18, 0.12, 0.18)
    m.block("Stone", 0, 4.4, 0.2, 2.6, 1.2, 0.4)
    m.block("Stone", 0.1, 5.6, 0.12, 2.0, 1.0, 0.24)
    for a, z in ((math.pi / 2, 8.3), (math.pi / 3, 14.0), (7 * math.pi / 6, 9.8), (-math.pi / 2, 9.0)):  # clear of the stair
        f = on_face(a, z)
        f.box("Window", 0, 0.05, 0, 1.1, 0.16, 1.4)
        f.box("Wood", 0, 0.14, 0, 0.14, 0.12, 1.42)
        f.box("Wood", 0, 0.14, 0, 1.12, 0.12, 0.14)
        f.box("Wood", 0, 0.14, -0.8, 1.4, 0.3, 0.18)
    for k in range(11):  # a stair of shelf fungi winding up round the stalk
        a = math.pi / 2 + 1.25 + k * 0.62
        z = 1.6 + k * 1.3
        rr = radius(z) * 0.94
        bracket(m, off(z) + math.cos(a) * rr, math.sin(a) * rr, z, 1.75)
    f = cap(m, "Cap", (lean, 0, h), 12.5, 7.0, "dome", turn(y=math.atan2(lean, h) * 0.8), 16, "CapDark", "GillGlow")
    specks(m, "Speck", f, 12.5, 7.0, "dome", 18, 1.2, rng)
    for k in range(9):  # spores sifting down from the gills, 4 apart
        a = k * math.tau / 9 + 0.15
        rr = 6.0 + (k % 3) * 2.0
        spore_column(m, "Spore", lean + math.cos(a) * rr, math.sin(a) * rr, 1.0, h - 1.6, 4.0, 0.34, rng)
    for k in range(6):
        a = k * math.tau / 6 + 0.9
        rr = rng.uniform(6.2, 7.6)
        shroom(m, math.cos(a) * rr, math.sin(a) * rr, rng.uniform(0.8, 1.8), 0.16, 0.5, 0.42, z0=0.3, cap_role="Glow", under=None)
    moths(m, rng, 14, 7.0, 14.0, 9.0, 18.0, size=0.8)
    m.block("Front", 0, 9, 1, 0.2, 0.2, 0.2)
    return m


def spore_geyser(seed=14):
    """A landmark for the rims: a crater of loam with glowing cracks down its sides, blowing a column of glowing
    spore clouds high into the mist for ever, motes spiralling up round it; puffballs and glowing mushrooms crowd
    round its foot."""
    m = prop("SporeGeyser", Loam=LOAM, LoamDark=LOAM_DARK, Vein=VEIN, Glow=GLOW, Puff=PUFF, PuffB=PUFF_B, Spore=SPORE, Motes=SPECK, Puffskin="#e9e0c8",
             Wart=WART, Stalk=STALK, Mycel=MYCEL, Moss=MOSS)
    rng = random.Random(seed)
    tiers = ((0.0, 9.5), (1.5, 8.0), (3.2, 5.9), (4.6, 4.3))
    for k, ((z0, r0), (z1, r1)) in enumerate(zip(tiers, tiers[1:])):
        prism(m, "Loam" if k % 2 == 0 else "LoamDark", 0, 0, z0, z1, r0, r1, 14, 0)
    for k in range(14):  # the crater's ragged lip
        a = (k + 0.5) * math.tau / 14
        obox(m, "LoamDark", (math.cos(a) * 3.9, math.sin(a) * 3.9, 4.95 + (k % 3) * 0.12), (2.0, 1.1, 0.9 + (k % 3) * 0.24), turn(z=a + math.pi / 2))
    prism(m, "Glow", 0, 0, 4.6, 4.78, 3.4, 3.4, 14)  # the glowing throat
    for k in range(7):  # glowing cracks down its sides
        a = k * math.tau / 7 + rng.uniform(-0.2, 0.2)
        pts = []
        for z, r in ((4.5, 4.45), (3.2, 6.0), (1.5, 8.05), (0.25, 9.35)):
            w = rng.uniform(-0.12, 0.12)
            pts.append((math.cos(a + w) * (r + 0.06), math.sin(a + w) * (r + 0.06), z))
        limb(m, "Vein", pts, 0.34, 0.2)
    cloud_column(m, 0, 0, 6.8, 6, 5.0, 2.1, grow=0.24)
    motes(m, rng, 14, 2.6, 5.5, 6.0, 26.0)
    for k in range(7):  # puffballs and glowing mushrooms round its foot
        a = k * math.tau / 7 + 0.4
        rr = rng.uniform(9.6, 11.0)
        x, y = math.cos(a) * rr, math.sin(a) * rr
        if k % 2:
            r = rng.uniform(0.8, 1.4)
            top = puffball(m, "Puffskin", x, y, r)
            warts(m, "Wart", x, y, top - r * 0.85, r, r * 0.85, 6, rng, 0.2)
        else:
            shroom(m, x, y, rng.uniform(1.0, 2.2), 0.2, 0.6, 0.5, cap_role="Glow", under=None)
    patches(m, "Mycel", rng, 8, 9.0, 12.0, (1.0, 2.0))
    patches(m, "Moss", rng, 5, 9.5, 12.0, (1.0, 1.6))
    return m


def shroom_tower(seed=15):
    """A landmark for the rims: three mushroom caps stacked up one fat stalk into a house. A door at its foot, lit
    windows between the caps, a railing round the first cap like a terrace and a ladder up to the second; glowing
    gills under every cap, glowing specks on the top one, smoke from a chimney at the top, and lanterns hanging under
    the two lower caps' rims, swinging (each pair on the X line at its hook's height). Its door looks out of its
    Front."""
    m = prop("ShroomTower", Stalk=STALK, StalkShade=STALK_SHADE, Cap=CAP, CapDark=CAP_DARK, CapC=CAP_C, GillGlow=GILL, Speck=SPECK, Door=WOOD,
             Wood=WOOD_DARK, Window=WINDOW, Stone=STONE, Chimney=CHIMNEY, Smoke="#8c8a78", SmokeLight="#aaa894", LanternA=IRON, LampA=LAMP,
             LanternB=IRON, LampB=LAMP, Glow=GLOW, Loam=LOAM, Mycel=MYCEL, Moss=MOSS, Front="#ff00ff")
    rng = random.Random(seed)
    h, r0, r1 = 25.0, 3.0, 2.3

    def radius(z):
        return r0 + (r1 - r0) * z / h

    mound(m, "Loam", 0, 0, 5.0, 0.6, 12)
    patches(m, "Mycel", rng, 7, 3.6, 6.0, (1.0, 2.0))
    patches(m, "Moss", rng, 4, 4.0, 6.0, (0.8, 1.4))
    prism(m, "Stone", 0, 0, 0, 0.8, 3.5, 3.3, 12, math.pi / 12)
    prism(m, "Stalk", 0, 0, 0.8, h, radius(0.8), r1, 12, math.pi / 12)

    def on_face(a, z):
        d = radius(z) * math.cos(math.pi / 12)
        return Frame(m, (math.cos(a) * d, math.sin(a) * d, z), turn(z=a - math.pi / 2))

    f = on_face(math.pi / 2, 2.6)  # the door
    f.box("Door", 0, 0.1, 0, 1.6, 0.26, 3.2)
    f.box("Wood", 0, 0.18, 1.75, 2.1, 0.28, 0.3)
    for s in (-1, 1):
        f.box("Wood", s * 0.95, 0.18, 0, 0.26, 0.3, 3.7)
    m.block("Stone", 0, 3.9, 0.2, 2.2, 1.0, 0.4)
    for a, z in ((math.pi / 2 - math.pi / 3, 5.4), (math.pi / 2 + math.pi / 3, 5.8), (math.pi / 2, 11.9), (math.pi / 2 + 2 * math.pi / 3, 12.2),
                 (math.pi / 2 - 2 * math.pi / 3, 11.6), (math.pi / 2, 19.4), (-math.pi / 2, 19.0)):
        f = on_face(a, z)
        f.box("Window", 0, 0.05, 0, 1.0, 0.14, 1.2)
        f.box("Wood", 0, 0.12, 0, 0.12, 0.1, 1.22)
        f.box("Wood", 0, 0.12, -0.7, 1.3, 0.28, 0.16)
    # The caps: a wide terrace, a tan one, and the spotted roof.
    cap(m, "Cap", (0, 0, 8.2), 6.8, 1.6, "flat", None, 16, "CapDark", "GillGlow")
    cap(m, "CapC", (0, 0, 15.4), 5.6, 1.5, "flat", None, 16, "CapDark", "GillGlow")
    f = cap(m, "Cap", (0, 0, 23.0), 5.0, 3.8, "dome", None, 14, "CapDark", "GillGlow")
    specks(m, "Speck", f, 5.0, 3.8, "dome", 10, 0.7, rng)
    for k in range(16):  # the terrace railing
        a = (k + 0.5) * math.tau / 16
        m.block("Wood", math.cos(a) * 5.9, math.sin(a) * 5.9, 9.05, 0.2, 0.2, 1.2)
        a1 = (k + 1.5) * math.tau / 16
        beam(m, "Wood", (math.cos(a) * 5.9, math.sin(a) * 5.9, 9.55), (math.cos(a1) * 5.9, math.sin(a1) * 5.9, 9.55), 0.16)
    lx, ly = math.cos(-0.7) * 4.3, math.sin(-0.7) * 4.3  # a ladder from the terrace to the second cap
    for s in (-1, 1):
        beam(m, "Wood", (lx - ly / 4.3 * 0.4 * s, ly + lx / 4.3 * 0.4 * s, 9.0), (lx - ly / 4.3 * 0.4 * s, ly + lx / 4.3 * 0.4 * s, 15.0), 0.16)
    for z in [9.6 + k * 0.6 for k in range(9)]:
        beam(m, "Wood", (lx + ly / 4.3 * 0.4, ly - lx / 4.3 * 0.4, z), (lx - ly / 4.3 * 0.4, ly + lx / 4.3 * 0.4, z), 0.1)
    # The chimney and its smoke.
    beam(m, "Chimney", (1.7, -1.1, 25.0), (2.0, -1.3, 28.3), 0.8)
    m.block("Chimney", 2.02, -1.32, 28.45, 1.05, 1.05, 0.4)
    puffs(m, "Smoke", 2.05, -1.35, 29.3, 4, 1.6, 0.9, grow=0.15, shade="SmokeLight")

    def lantern(x, hook, frame, lamp):
        for i in range(2):
            z = hook - i * 0.35
            beam(m, frame, (x, 0, z), (x, 0, z - 0.35), *((0.24, 0.08) if i % 2 else (0.08, 0.24)))
        zl = hook - 0.85
        m.block(frame, x, 0, zl, 0.8, 0.8, 0.12)
        m.loft_z(frame, (zl, x, 0, 0.7, 0.7), (zl + 0.3, x, 0, 0.18, 0.18))
        m.block(lamp, x, 0, zl - 0.5, 0.55, 0.55, 0.85)
        for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            m.block(frame, x + sx * 0.33, sy * 0.33, zl - 0.5, 0.08, 0.08, 0.95)
        m.block(frame, x, 0, zl - 0.98, 0.7, 0.7, 0.12)

    for s in (-1, 1):
        lantern(s * 6.0, 7.95, "LanternA", "LampA")
        lantern(s * 4.9, 15.15, "LanternB", "LampB")
    for k in range(5):
        a = k * math.tau / 5 + 0.5
        rr = rng.uniform(4.2, 5.4)
        shroom(m, math.cos(a) * rr, math.sin(a) * rr, rng.uniform(0.7, 1.5), 0.14, 0.45, 0.38, z0=0.2, cap_role="Glow", under=None)
    m.block("Front", 0, 8, 1, 0.2, 0.2, 0.2)
    return m


def spore_drifter(seed=16):
    """The sky piece: a giant spore drifting across the sky beyond the island, head first, its glowing core
    bristling with glowing filaments and long threads strung with glowing beads trailing behind it. It starts high
    above the ground. The game drifts it from its threads' middle towards its core (its head), so the threads trail
    behind (-Y)."""
    m = prop("SporeDrifter", SporeCore="#e8ff8a", Filament="#c6f070", Drifter="#f4ffd0")
    rng = random.Random(seed)
    zc = 56.0
    c = Vector((0, 0, zc))
    ball(m, "SporeCore", 0, 0, zc, 2.4, 12, 7)
    n = 34
    for i in range(n):  # filaments all round it, evenly spread (a Fibonacci sphere)
        y = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - y * y)
        a = i * math.pi * (3 - math.sqrt(5))
        d = Vector((math.cos(a) * r, y, math.sin(a) * r))
        if d.y > 0.55:
            continue  # the front stays bare: it leads
        length = rng.uniform(4.0, 6.0) * (1.3 if d.y < -0.3 else 1.0)
        beam(m, "Filament", tuple(c + d * 2.2), tuple(c + d * (2.2 + length)), 0.24, None, 0.1)
        ball(m, "Drifter", *(c + d * (2.4 + length)), 0.36, 6, 3)
    for k in range(7):  # long threads trailing behind, strung with beads
        a = k * math.tau / 7
        d = Vector((math.cos(a) * 0.22, -1, math.sin(a) * 0.22)).normalized()
        length = rng.uniform(13, 19)
        start = c + d * 2.0
        beam(m, "Filament", tuple(start), tuple(start + d * length), 0.2, None, 0.08)
        t = 3.0
        while t < length:
            ball(m, "Drifter", *(start + d * t), 0.3, 6, 3)
            t += 3.0
    return m


def shelf_fall(seed=17):
    """Two white mycelium cords as thick as an arm spilling over the wall's top edge from a felted mat on the rim and
    twisting round each other all the way down the wall to the floor, clusters of shelf fungi growing out of the
    wall beside them with their undersides glowing, glowing drops falling from each cluster for ever into a glowing
    pool at the foot. Origin on the wall's top inner edge: rim z 0, floor z -44, +Y out into the corridor. The Front
    part tells the game which way it faces, then it goes."""
    m = prop("ShelfFall", Mycel=MYCEL, Shelf=SHELF, ShelfDark=SHELF_DARK, GillGlow=GILL, Falling="#c4ff5a", Glow=GLOW, Stalk=STALK, Loam=LOAM,
             Moss=MOSS, Front="#ff00ff")
    rng = random.Random(seed)
    for x, y, w, d, h in ((0, -2.5, 8.0, 5.0, 0.4), (-3.5, -4.5, 3.5, 3.0, 0.5), (3.2, -4.0, 3.0, 3.5, 0.56)):  # the mat on the rim
        m.block("Mycel", x, y, h / 2, w, d, h)
    m.block("Mycel", 0, 0.7, 0.31, 8.4, 1.6, 0.62)
    for k in range(2):  # the cords, twisting round each other
        s = 1 if k else -1
        pts = [(s * 1.6, -3.2, 0.6), (s * 1.2, -0.6, 1.1), (s * 1.0, 2.0, 0.1)]
        z = 0.0
        while z > -43.0:
            z -= 3.2
            ph = -z * 0.15 + k * math.pi
            pts.append((2.0 * math.cos(ph), 2.1 + 0.4 * math.sin(ph), max(z, -43.6)))
        limb(m, "Mycel", pts, 0.66 - 0.14 * k, 0.42 - 0.08 * k)
        for p in pts[4:-1:3]:
            shroom(m, p[0], p[1] + 0.3, 0.7, 0.12, 0.42, 0.34, z0=p[2] + 0.2, cap_role="Glow", under=None)
    # Clusters of shelf fungi, each a few shelves stepping down, glowing drops falling from the lowest, 4 apart.
    for z, x, count in ((-5.0, 3.0, 3), (-13.0, -3.2, 2), (-20.5, 2.6, 3), (-28.0, -2.8, 3), (-35.5, 3.4, 2)):
        side = -1 if x > 0 else 1
        for j in range(count):
            bracket(m, x + side * j * 1.35 + rng.uniform(-0.3, 0.3), 1.3, z - j * 1.25, rng.uniform(1.9, 2.5) * (1 - 0.17 * j))
        dx = x + side * (count - 1) * 1.35
        zz = z - (count - 1) * 1.25 - 0.8
        while zz > -43.4:
            m.block("Falling", dx, 3.9, zz, 0.26, 0.26, 0.55)  # in front of the shelves below
            zz -= 4.0
    puddle(m, "Glow", ((0.8, 3.8, 6.0, 3.6), (-1.0, 4.6, 3.0, 2.4), (2.6, 4.4, 2.6, 2.2)), z=-43.9, thick=0.12)
    mound(m, "Loam", -2.8, 3.0, 1.2, 0.6, 8, -44.0)
    for x, y, h in ((-3.2, 4.0, 1.4), (4.4, 3.2, 1.0), (-1.8, 5.6, 0.7)):
        shroom(m, x, y, h, 0.14, 0.45, 0.38, z0=-44.0, cap_role="Glow", under=None)
    m.block("Front", 0, 6, -20, 0.2, 0.2, 0.2)
    return m


GATE_X, GATE_Z, GATE_TILT, GATE_R, GATE_H = 15.5, 31.0, 0.2, 15.5, 5.5  # each cap: its middle, lean, size
GATE_U_A, GATE_U_B = 7.0, -12.0  # where the two pairs of bulbs hang, along the gills from a cap's middle


def cap_gate(seed=18):
    """Two giant mushrooms rooted on either rim and leaning in over the corridor until their caps almost touch over
    its middle: chocolate caps freckled with glowing specks, their gills glowing down on everything below, glowing
    bulbs hanging from the gills on threads and swinging along the corridor, moths circling under them. Modelled
    for the 72-wide corridor (feet beyond 36 from the middle); MapDecor stretches it to the real width. All of it
    stays above the rim (z 0), clear of the flight camera. Each pair of bulbs hangs from the X line at its height,
    so they swing round it."""
    m = prop("CapGate", Stalk=STALK, StalkShade=STALK_SHADE, CapB=CAP_B, CapBDark=CAP_B_DARK, GillGlow=GILL, Speck=SPECK, BulbStem="#8a7a5a",
             BulbStemB="#8a7a5a", Bulb=BULB, BulbB=BULB, Glow=GLOW, Loam=LOAM, Mycel=MYCEL, Moss=MOSS, Moths=MOTHS, Front="#ff00ff")
    rng = random.Random(seed)
    lip = GATE_H * 0.16
    for s in (-1, 1):
        pts = [(s * 40, 0, 2.0), (s * 38.0, 0, 8.0), (s * 34.5, 0, 16.0), (s * 29.0, 0, 23.0), (s * 22.5, 0, 28.2), (s * 17.0, 0, 30.6),
               (s * GATE_X, 0, GATE_Z + 1.2)]
        prism(m, "Stalk", s * 40, 0, 0, 3.6, 4.2, 2.9, 10)  # the swollen foot
        stem_path(m, "Stalk", pts, 2.9, 2.0, 10)
        for k in range(6):  # roots on the rim
            a = k * math.tau / 6 + 0.3
            d = Vector((math.cos(a), math.sin(a), 0))
            base = Vector((s * 40, 0, 0))
            limb(m, "Stalk", [tuple(base + d * 3.0 + Vector((0, 0, 2.0))), tuple(base + d * 4.8 + Vector((0, 0, 0.7))),
                              tuple(base + d * 6.4 + Vector((0, 0, 0.4)))], 1.4, 0.55)
        mound(m, "Loam", s * 40, 0, 6.6, 0.8, 12)
        patches(m, "Mycel", rng, 6, 4.5, 8.0, (1.2, 2.2), cx=s * 40)
        patches(m, "Moss", rng, 4, 5.0, 8.0, (1.0, 1.6), cx=s * 40)
        for k in range(5):
            a = k * math.tau / 5 + 0.2
            rr = rng.uniform(6.0, 7.6)
            shroom(m, s * 40 + math.cos(a) * rr, math.sin(a) * rr, rng.uniform(0.8, 1.8), 0.15, 0.5, 0.42, z0=0.3, cap_role="Glow", under=None)
        # The skirt, a ring round the stalk under the cap.
        p, q = Vector(pts[3]), Vector(pts[4])
        mid = p.lerp(q, 0.5)
        along = (q - p).normalized()
        tube(m, "StalkShade", tuple(mid - along * 0.6), tuple(mid + along * 0.25), 3.8, 2.5, 12)
        rot = turn(y=-s * GATE_TILT)  # leaning in over the middle
        f = cap(m, "CapB", (s * GATE_X, 0, GATE_Z), GATE_R, GATE_H, "dome", rot, 18, "CapBDark", "GillGlow")
        specks(m, "Speck", f, GATE_R, GATE_H, "dome", 18, 1.3, rng)
        # Mycelium threads hanging from the gills, glowing beads on them (off the X line, so they stay still).
        for u, v in ((-4.0, 6.0), (3.0, -7.0), (9.0, 4.5), (-8.5, -4.0), (1.0, 9.5)):
            top = Vector(f.at(u, v, -lip * 1.4))
            length = rng.uniform(2.0, 3.5)
            beam(m, "BulbStem", tuple(top), tuple(top - Vector((0, 0, length))), 0.08)
            ball(m, "Glow", *(top - Vector((0, 0, length + 0.2))), 0.3, 6, 3)
    # The bulbs, hanging from the gills on the X line: a pair towards the middle (u > 0) and a pair further out.
    # gate_hook works out the same height.
    for role, u in (("Bulb", GATE_U_A), ("BulbB", GATE_U_B)):
        for s in (-1, 1):
            f = Frame(m, (s * GATE_X, 0, GATE_Z), turn(y=-s * GATE_TILT))
            hook = Vector(f.at(-s * u, 0, -lip * 1.35))
            stem = "BulbStem" if role == "Bulb" else "BulbStemB"
            beam(m, stem, tuple(hook + Vector((0, 0, 0.4))), tuple(hook - Vector((0, 0, 2.4))), 0.12)
            cap(m, stem, tuple(hook - Vector((0, 0, 2.42))), 0.55, 0.35, "dome", None, 8)
            ball(m, role, hook.x, 0, hook.z - 3.3, 0.85, 10, 5)
            m.block(role, hook.x, 0, hook.z - 4.3, 0.22, 0.22, 0.4)
    moths(m, rng, 14, 3.0, 13.0, 14.0, 23.0, size=0.8)
    m.block("Front", 0, 6, 20, 0.2, 0.2, 0.2)
    return m


def gate_hook(u):
    """The height of cap_gate's hook u studs along a cap's gills from its middle (towards the corridor's middle
    when u > 0), worked out the same way cap_gate places it (for MOTION)."""
    lip = GATE_H * 0.16
    return round(GATE_Z - u * math.sin(GATE_TILT) - lip * 1.35 * math.cos(GATE_TILT), 2)


GATE_HOOK_A, GATE_HOOK_B = gate_hook(GATE_U_A), gate_hook(GATE_U_B)


ALL = [glowcap, puffballs, lamp_shroom, wavecaps, shelf_stump, coral_shroom, mycelium_heart, mushroom_hut, spore_tuft, mycelium_web, parasol,
       morel_spire, elder_shroom, spore_geyser, shroom_tower, spore_drifter, shelf_fall, cap_gate]

# What moves. The game reads the same numbers from shared/Config/PropMotion.luau. Kinds of move:
#   spin  degrees a second; swing  degrees each way, over period seconds; bob  studs up and down over period;
#   pulse  the glow dims to this share and back over period; fall  drops this far over period, then starts again
#   (negative rises); "*" drift  the whole prop glides head first.
# spin and swing turn round axis "up" (default), "across" (the model's X) or "ahead" (its Y), through the part's
# own middle (about="self") or a point `height` studs straight above the prop's origin (the default).
_GILL = dict(pulse=0.55, period=3.6)
_GLOW = dict(pulse=0.5, period=2.6)
_LAMP = dict(swing=12, period=2.6, axis="across", height=8.1)
_HUT = dict(swing=10, period=2.8, axis="across", height=4.0)
_SMOKE = dict(fall=-1.5, period=1.8)
_BEAT = dict(bob=0.18, period=1.1)
_WAND_A = dict(swing=9, period=3.6, axis="across")
_WAND_B = dict(swing=7, period=4.4, axis="ahead")
_WAND_C = dict(swing=11, period=3.0, axis="across")
_TOWER_A = dict(swing=10, period=2.8, axis="across", height=7.95)
_TOWER_B = dict(swing=9, period=3.3, axis="across", height=15.15)
_GATE_A = dict(swing=8, period=3.0, axis="across", height=GATE_HOOK_A)
_GATE_B = dict(swing=8, period=3.6, axis="across", height=GATE_HOOK_B)
MOTION = {
    "prop_Glowcap": {"Spore": dict(fall=2.5, period=3.2), "GillGlow": dict(_GILL), "Speck": dict(pulse=0.35, period=2.2), "Glow": dict(_GLOW)},
    "prop_Puffballs": {"Puff": dict(fall=-2, period=2.2), "PuffB": dict(fall=-2, period=2.2), "Spore": dict(fall=-2, period=2.2),
                       "Glow": dict(pulse=0.45, period=2.2),
                       "Speck": dict(pulse=0.4, period=2.2)},
    "prop_LampShroom": {"BulbStem": dict(_LAMP), "Bulb": dict(_LAMP, pulse=0.65), "Glow": dict(_GLOW), "Moths": dict(spin=28, bob=0.3, period=3),
                        "GillGlow": dict(_GILL)},
    "prop_Wavecaps": {"WandA": dict(_WAND_A), "BellA": dict(_WAND_A, pulse=0.6), "WandB": dict(_WAND_B), "BellB": dict(_WAND_B, pulse=0.6),
                      "WandC": dict(_WAND_C), "BellC": dict(_WAND_C, pulse=0.6), "Glow": dict(_GLOW)},
    "prop_ShelfStump": {"GillGlow": dict(pulse=0.5, period=3.2), "Glow": dict(pulse=0.45, period=2.4), "Moths": dict(spin=-24, bob=0.3, period=3.4)},
    "prop_CoralShroom": {"TipGlow": dict(pulse=0.45, period=2.6), "Motes": dict(spin=20, bob=0.4, period=3.6)},
    "prop_MyceliumHeart": {"Heart": dict(_BEAT), "HeartRib": dict(_BEAT), "HeartGlow": dict(_BEAT, pulse=0.35), "Vein": dict(pulse=0.4, period=2.2),
                           "VeinB": dict(pulse=0.4, period=2.9), "Spore": dict(fall=-2.0, period=2.6), "Glow": dict(_GLOW)},
    "prop_MushroomHut": {"Smoke": dict(_SMOKE), "SmokeLight": dict(_SMOKE), "Window": dict(pulse=0.8, period=2.6), "Lantern": dict(_HUT),
                         "Lamp": dict(_HUT, pulse=0.7), "GillGlow": dict(pulse=0.6, period=3.8), "Speck": dict(pulse=0.4, period=2.4),
                         "Glow": dict(_GLOW)},
    "prop_SporeTuft": {"Glow": dict(pulse=0.45, period=2.4)},
    "prop_MyceliumWeb": {"Vein": dict(pulse=0.35, period=2.6), "VeinB": dict(pulse=0.35, period=3.4), "Glow": dict(pulse=0.5, period=2)},
    "prop_Parasol": {"GillGlow": dict(pulse=0.55, period=3.8), "Spore": dict(fall=3, period=3.4), "Moths": dict(spin=16, bob=0.4, period=4)},
    "prop_MorelSpire": {"Pit": dict(pulse=0.5, period=3), "Spore": dict(fall=-2.4, period=2.6)},
    "prop_ElderShroom": {"GillGlow": dict(pulse=0.6, period=4.2), "Speck": dict(pulse=0.4, period=2.6), "Spore": dict(fall=4, period=3.6),
                         "Moths": dict(spin=10, bob=0.6, period=5), "Window": dict(pulse=0.8, period=3), "Glow": dict(_GLOW)},
    "prop_SporeGeyser": {"Puff": dict(fall=-5, period=2.8), "PuffB": dict(fall=-5, period=2.8), "Spore": dict(fall=-5, period=2.8),
                         "Glow": dict(pulse=0.5, period=2.6),
                         "Vein": dict(pulse=0.4, period=2.6), "Motes": dict(spin=30, bob=1, period=4)},
    "prop_ShroomTower": {"LanternA": dict(_TOWER_A), "LampA": dict(_TOWER_A, pulse=0.7), "LanternB": dict(_TOWER_B), "LampB": dict(_TOWER_B, pulse=0.7),
                         "Window": dict(pulse=0.8, period=3.2), "Smoke": dict(_SMOKE), "SmokeLight": dict(_SMOKE), "GillGlow": dict(pulse=0.6, period=4),
                         "Speck": dict(pulse=0.4, period=2.4), "Glow": dict(_GLOW)},
    "prop_SporeDrifter": {"*": dict(drift=420, period=44, fade=0.12, head="SporeCore")},
    "prop_ShelfFall": {"Falling": dict(fall=4, period=1.3), "GillGlow": dict(pulse=0.55, period=3), "Glow": dict(pulse=0.5, period=2.4)},
    "prop_CapGate": {"BulbStem": dict(_GATE_A), "Bulb": dict(_GATE_A, pulse=0.6), "BulbStemB": dict(_GATE_B), "BulbB": dict(_GATE_B, pulse=0.6),
                     "GillGlow": dict(pulse=0.55, period=4), "Speck": dict(pulse=0.4, period=2.4), "Glow": dict(_GLOW),
                     "Moths": dict(spin=14, bob=0.5, period=4.5)},
}

# Where the props go: the same rules as Config/Decor's SporeHollow (keep the two in step). The map is 1700 long.
DECOR = dict(
    floor=dict(first=10, gap=(9, 16), side=(23, 34),
               props=[("prop_Glowcap", 14, (1.5, 1.9)), ("prop_Puffballs", 10, (1.3, 1.6)), ("prop_LampShroom", 9, (1.4, 1.7)),
                      ("prop_Wavecaps", 9, (1.4, 1.7)), ("prop_ShelfStump", 8, (1.4, 1.7)), ("prop_CoralShroom", 7, (1.4, 1.8)),
                      ("prop_MushroomHut", 4, (1.3, 1.5)), ("prop_MyceliumHeart", 3, (1.3, 1.5))],
               extras=dict(chance=0.85, spread=8, props=[("prop_SporeTuft", 5, (0.9, 1.3)), ("prop_Puffballs", 2, (0.5, 0.7)),
                                                         ("prop_CoralShroom", 2, (0.6, 0.8))])),
    rim=dict(first=6, gap=(10, 17), chance=0.95, side=(60, 104),
             props=[("prop_Parasol", 6, (2.0, 2.6)), ("prop_MorelSpire", 4, (1.8, 2.3)), ("prop_Glowcap", 4, (2.2, 2.8)),
                    ("prop_CoralShroom", 2, (2.2, 2.8)), ("prop_SporeTuft", 2, (2.2, 2.8))]),
    overhead=[("prop_CapGate", 280, 0, 1), ("prop_CapGate", 860, 0, 1.05), ("prop_CapGate", 1440, 0, 1)],
    walls=[("prop_ShelfFall", d, side) for d, side in ((80, 1), (270, -1), (460, 1), (650, -1), (840, 1), (1030, -1), (1220, 1),
                                                       (1410, -1), (1600, 1))],
    spots=[("prop_ElderShroom", 110, -88, "rim", 0, 1.3, "middle"), ("prop_ElderShroom", 690, 88, "rim", 0, 1.4, "middle"),
           ("prop_ElderShroom", 1270, -88, "rim", 0, 1.3, "middle"),
           ("prop_ShroomTower", 230, 86, "rim", 0, 1.2, "middle"), ("prop_ShroomTower", 810, -86, "rim", 0, 1.3, "middle"),
           ("prop_ShroomTower", 1390, 86, "rim", 0, 1.2, "middle"),
           ("prop_SporeGeyser", 430, -84, "rim", 0, 1.2), ("prop_SporeGeyser", 1010, 84, "rim", 40, 1.3),
           ("prop_SporeGeyser", 1590, -84, "rim", 80, 1.2),
           ("prop_SporeDrifter", 360, -170, "rim", 100, 2.2), ("prop_SporeDrifter", 1150, 175, "rim", 290, 2.4)]
          + [("prop_MyceliumWeb", d, x, "floor", yaw, 1.2) for d, x, yaw in ((40, -3, 20), (155, 4, 140), (270, -4, 70), (385, 3, 200),
                                                                               (500, -2, 300), (615, 4, 40), (735, -3, 110), (850, 2, 250),
                                                                               (965, -4, 330), (1085, 3, 80), (1205, -2, 160),
                                                                               (1325, 4, 10), (1445, -3, 230), (1560, 2, 120), (1670, -4, 290))],
)


# ---------------------------------------------------------------------- light


def hollow_light(scene):
    """Night in the hollow for the renders: dim greenish moonlight through the spore mist and an olive fill, close
    to the game's Config/Lighting look for this world."""
    sun = bpy.data.objects["Sun"]
    sun.data.energy = 1.4
    sun.data.color = (0.86, 0.94, 0.82)
    sun.rotation_euler = (math.radians(-58), math.radians(25), math.radians(30))
    ambient = scene.world.node_tree.nodes["Background"]
    ambient.inputs["Color"].default_value = (0.64, 0.66, 0.54, 1)
    ambient.inputs["Strength"].default_value = 0.72


# ---------------------------------------------------------------------- scene and renders

BIG = {"prop_ElderShroom": (-100, -125, 0), "prop_ShroomTower": (-62, -120, 0), "prop_SporeGeyser": (-30, -120, 0),
       "prop_Parasol": (-2, -112, 0), "prop_MorelSpire": (18, -112, 0), "prop_SporeDrifter": (40, -230, 0), "prop_ShelfFall": (110, -110, 44),
       "prop_CapGate": (200, -170, 0)}


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
    stars = mk.star_dome(stage, count=120, colours=("#ffffff", "#eaffc8"))
    bpy.context.view_layer.update()
    mk.set_sky(scene, SKY)
    hollow_light(scene)

    everything = roots + [player]
    if stills:
        for model, root in zip(models, roots):
            name = model.name
            if name == "prop_CapGate":
                mk.shoot_prop(scene, name, root, player, everything, (-0.15, 1.0, 0.25), 0.95, (1400, 700), 32)
            elif name == "prop_ShelfFall":
                mk.shoot_prop(scene, name, root, player, everything, (0.6, 1.0, 0.1), 0.9, (700, 900), 40)
            elif name == "prop_SporeDrifter":
                mk.shoot_prop(scene, name, root, player, everything, (0.8, 0.6, -0.05), 0.9, (800, 800), 50)
            elif name in ("prop_ElderShroom", "prop_ShroomTower", "prop_SporeGeyser"):
                mk.shoot_prop(scene, name, root, player, everything, (0.5, 0.95, 0.35), 1.15, (800, 800), 50)
            else:
                mk.shoot_prop(scene, name, root, player, everything)
        player.location = (30, -40, 0)
        bpy.context.view_layer.update()
        small = [r for r in roots if mk.prop_of(r) not in BIG]
        mk.set_visible(everything, small + [player])
        kit.shoot(scene, "props", (row_middle, 40, 30), (row_middle, -40, 5), (1800, 700), 18)
        landmarks = [built[n] for n in ("prop_ElderShroom", "prop_ShroomTower", "prop_SporeGeyser", "prop_Parasol", "prop_MorelSpire")]
        mk.set_visible(everything, landmarks + [player])
        player.location = (-35, -96, 0)
        bpy.context.view_layer.update()
        kit.shoot(scene, "landmarks", (-40, -8, 36), (-40, -120, 16), (1800, 800), 20)

    if videos:  # close up on what moves
        names = ("prop_Glowcap", "prop_Puffballs", "prop_LampShroom", "prop_Wavecaps", "prop_ShelfStump", "prop_MyceliumHeart", "prop_MushroomHut",
                 "prop_CoralShroom", "prop_Parasol", "prop_MorelSpire", "prop_ShroomTower", "prop_SporeGeyser", "prop_SporeDrifter")
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
        mk.render_video(scene, RENDERS, "spore_motion", 120, 15,
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

        mk.render_video(scene, RENDERS, "spore_flight", frames, 15, fly, (1600, 900))
        mk.reset_motion(entries)

    mk.clear([corridor, stars] + copies)
    mk.light_up(roots, GLOW_ROLES, 0)
    ground.hide_render = False
    for root in roots:
        for child in root.children:
            child.hide_render = False
    player.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "spore_hollow_models.blend"))
    print("saved", HERE / "spore_hollow_models.blend")
    for model in models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    # After "--": "stills" renders only the stills, "videos" only the videos; nothing, both.
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(stills=not args or "stills" in args, videos=not args or "videos" in args)
