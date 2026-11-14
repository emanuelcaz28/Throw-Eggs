"""Builds The Weeping Dark's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_weeping_dark.py              (stills and videos)
    Blender -b -P build_weeping_dark.py -- stills    (stills only, quicker while modelling)

Saves weeping_dark_models.blend and renders to design/world/models_weeping_dark/: one still per prop, the props
together, the landmarks, a stretch of corridor, the end of the world, and two videos of what moves
(weeping_motion.mp4 close up, weeping_flight.mp4 down the corridor at the flight camera's height).

The Weeping Dark, map 15, the last map: the darkest, saddest and most frightening place in the game, and the end
of the corridor. There was a town here once, and a sun. The sun went out, everybody walked into the dark to look
for it, and nobody came back. What they left behind is still waiting: a candle in the window, swings still
swinging, a rocking chair still rocking, a lost bear sitting on its suitcase, a lighthouse sweeping for a ship
that isn't coming, a bell tolling for no one. Stone mourners kneel in the ash with their faces in their hands.

It's the only map with no colour at all: black, ash and bone, lit by pale tear-light and candles. The one colour
left in the world is red, and red is only ever eyes. Everywhere you see red, something is looking at you: the
mourner peeking through its fingers, the thing lifting its coffin lid, the bear's empty socket as its head turns
after you, the faces under the tear pools. And out past the walls, where you thought there was only sky, the
Watchers stand in the void with their long hands on the edge of the island, weeping, their eyes following you.

Its signature is the Mourner: a hooded stone figure kneeling with its hands over its face, shoulders heaving, tears
of light running through its fingers, and one red eye that opens between them. Around it: black willows dripping
tears, empty swings, rocking chairs, a house's last wall with a candle in the window and its door swinging, plots of
blank headstones with souls rising, coffins whose lids lift by themselves, pale hands reaching out of the ash, dying
street lamps with moths, hooded bearers carrying a lantern, and now and then the lost bear; ash reeds and candle stubs
as filler, and tear pools lying flat across the middle with a drowned face looking up. On the rims: claw trees,
hollow houses where a shape rises in the lit window, and a funeral procession gliding along the edge of the wall;
landmarks: the last lighthouse, its beam still sweeping, the tolling bell tower, and colossal wailing heads. The
Watchers fill the sky. Faces push out of the walls crying long streams, and a Long Arm reaches from one rim right
over the corridor to grip the other.

At the very end of the corridor, where every other map has only ever had a wall, stands the Last Door: a colossal
black door with a sea of candles left in front of it, chained, and not quite shut. Something is holding it from the
other side. Its fingers are round the edge, and its eye moves in the gap.

No pentagrams, hexagrams or crosses (kids' game): headstones are plain and round-topped, windows have upright bars
only. Nothing to do with how anyone died: the sadness here is who's missing, and the fear is what's watching.

No stud texture in this file: kit.PREVIEW_STUDS is off, so every material is a plain colour and the renders show
the models as they leave Blender. The studs come only in Studio, from the shared "Studs" MaterialVariant that
studio_tidy puts on every part except the glowing ones (docs/MAP_RECIPE.md step 8). The meshes still get the
usual box-projected UVs.

What moves is MOTION below, the same numbers as shared/Config/PropMotion.luau (keep the two in step). Glowing roles
(GLOW_ROLES) must also be in shared/Roles.luau, which makes them Neon in the game. LIGHTS is Config/Decor's
propLights: this map is so dark that Neon alone lights nothing, so its candles and lamps cast real light, which
flickers with the part's pulse. Props that must face a certain way carry a small Front part on their +Y side;
MapDecor turns them, then removes it. Learned on the maps before (docs/MAP_RECIPE.md): drift overrides every other
move, so the procession has no other move; no turn tied to a bob; pieces that turn together share one centre (hinges
and hooks on the X line at a height for axis="across", or straight above the origin).
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
from build_clockwork_citadel import Frame, obox, tube, turn  # noqa: E402
from build_shadow_bog import dome  # noqa: E402
from map_kit import ball, beam, disc, flat_ring, gem, kit, limb, plate, prism  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "models_weeping_dark"

# Roles lit from inside. The game makes them Neon (shared/Roles.luau), so add new ones there too.
GLOW_ROLES = {"Tears", "Stream", "Stare", "Flame", "FlameA", "FlameB", "Lamp", "LampA", "Window", "Soul", "Ripple", "RippleB", "Beacon",
              "Sweep", "Leader", "Motes"}
kit.NO_STUDS.update(GLOW_ROLES)
mk.GLOW_STRENGTH = 2.4

# Shared colours. No colour on purpose: everything is grey, the one exception being RED, which is only ever eyes.
STONE, STONE_DARK, STONE_LIGHT = "#74747a", "#4e4e54", "#9a9a9e"
ASH, ASH_DARK, ASH_LIGHT = "#3c3c42", "#28282c", "#66666c"
BARK, BARK_DARK = "#1d1d21", "#131316"
WOOD, WOOD_DARK = "#403e3c", "#2a2927"
IRON, IRON_DARK = "#2c2c30", "#1b1b1e"
CLOTH, CLOTH_DARK = "#222226", "#151518"
BONE, BONE_DARK = "#c2c0ba", "#8e8c86"
PLUSH, PLUSH_DARK, PLUSH_LIGHT = "#5f5c58", "#403e3b", "#86837e"
BLACK = "#08080a"
POOL = "#0c0d12"
WAX = "#cdc9bc"
TEAR, FLAME, LAMP, WINDOW = "#e6e6e6", "#f4ecd6", "#dfe2d8", "#e2dcc4"
STREAM, RIPPLE = "#777777", "#8c8c8c"  # the long lines of light, kept dim so the drops on them stand out. Pure grey: Neon turns any hint of blue into blue
RED = "#ff1a1a"

# The corridor's colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#26262a", "FloorB": "#212125", "Dirt": "#18181c", "DirtB": "#141418", "Grass": "#4a4a50"}
SKY = "#16171d"  # a little lighter than the things standing in it, so the Watchers are shapes against it


def prop(name, **colours):
    return mk.prop(name, **colours)


# ---------------------------------------------------------------------- shape helpers


def outline(m, role, f, pts, y0, y1):
    """A slab with this outline: pts are (x, z) in frame f's XZ plane, thick from y0 to y1 along its Y."""
    n = len(pts)
    verts = [f.at(x, y0, z) for x, z in pts] + [f.at(x, y1, z) for x, z in pts]
    faces = [list(range(n)), list(range(n, 2 * n))[::-1]] + [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    m._add(role, verts, faces)


def flat_outline(m, role, f, pts, z0, z1):
    """A slab with this outline lying flat: pts are (x, y) in frame f's XY plane, from z0 to z1."""
    n = len(pts)
    verts = [f.at(x, y, z0) for x, y in pts] + [f.at(x, y, z1) for x, y in pts]
    faces = [list(range(n)), list(range(n, 2 * n))[::-1]] + [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    m._add(role, verts, faces)


def pool(m, role, blobs, z=0.08, thick=0.16):
    """puddle(), with each slab a hair higher than the last, so their tops never share a plane and shimmer."""
    for k, (x, y, w, d) in enumerate(blobs):
        m.block(role, x, y, z + k * 0.004, w, d, thick)


def oval(rx, ry, sides=14, cx=0.0, cy=0.0):
    return [(cx + rx * math.cos(i * math.tau / sides), cy + ry * math.sin(i * math.tau / sides)) for i in range(sides)]


def drops(m, role, x, y, z_top, z_bottom, gap, size=0.2):
    """A column of tears exactly `gap` apart from z_top down to z_bottom. Falling `gap` over a period and starting
    over loops seamlessly: each only goes as far as where the next began."""
    z = z_top
    while z > z_bottom:
        gem(m, role, x, y, z, size, size * 2.4, size * 1.1, 5)
        z -= gap


def souls(m, role, x, y, z0, count, gap, size=0.2):
    """Pale specks rising: `gap` apart, so rising `gap` over a period (fall = -gap) loops for ever."""
    for k in range(count):
        gem(m, role, x + 0.1 * math.sin(k * 2.1), y + 0.1 * math.cos(k * 1.7), z0 + k * gap, size, size * 1.6, size * 1.6, 4)


def candle(m, x, y, z, h, r=0.18, flame="Flame", wax="Wax"):
    prism(m, wax, x, y, z, z + h, r, r * 0.92, 6)
    gem(m, flame, x, y, z + h + r * 0.9, r * 0.75, r * 2.3, r * 0.8, 5)


def hand(m, role, wrist, ahead, back, size=1.0, spread=0.6, curl=0.3, long=1.0, thumb=1):
    """A long thin hand from the wrist: its fingers point `ahead`, the back of it faces `back`, the fingers curl away
    from that, and thumb says which side the thumb is on."""
    w = Vector(wrist)
    a = Vector(ahead).normalized()
    u = Vector(back)
    u = (u - a * u.dot(a)).normalized()
    s = a.cross(u)
    palm = 1.15 * size
    plate(m, role, tuple(w), tuple(w + a * palm), tuple(s), 0.72 * size, 1.05 * size, 0.34 * size)
    for off, length in ((-0.39, 1.0), (-0.13, 1.18), (0.13, 1.22), (0.39, 1.05)):
        base = w + a * palm + s * off * size
        d = (a + s * off * spread).normalized()
        k = length * long * size
        p1 = base + d * k * 0.5
        d = (d - u * curl).normalized()
        p2 = p1 + d * k * 0.4
        d = (d - u * curl).normalized()
        p3 = p2 + d * k * 0.34
        limb(m, role, [tuple(base), tuple(p1), tuple(p2), tuple(p3)], 0.23 * size, 0.08 * size)
    base = w + a * palm * 0.35 + s * thumb * 0.34 * size
    t = (a * 0.7 + s * thumb * 0.8).normalized()
    p1 = base + t * 0.55 * size
    p2 = p1 + (t + a - u * 0.3).normalized() * 0.5 * size
    limb(m, role, [tuple(base), tuple(p1), tuple(p2)], 0.24 * size, 0.1 * size)


def hooded(m, x, y, z, h, robe="Robe", hood="Hood", dark="HoodDark", rng=None, sides=8):
    """A tall hooded figure h high from z, its robe hanging in tatters and no feet under it. Looks towards +Y."""
    rng = rng or random.Random(int(abs(x) * 7 + abs(y) * 3 + 1))
    prism(m, robe, x, y, z + h * 0.1, z + h * 0.72, h * 0.19, h * 0.125, sides, math.pi / sides)
    prism(m, robe, x, y, z + h * 0.72, z + h * 0.8, h * 0.135, h * 0.07, sides, math.pi / sides)
    for k in range(9):  # the hem: tatters of different lengths
        a = k * math.tau / 9 + rng.uniform(-0.15, 0.15)
        p = Vector((x + math.cos(a) * h * 0.165, y + math.sin(a) * h * 0.165, z + h * 0.16))
        q = Vector((x + math.cos(a) * h * 0.2, y + math.sin(a) * h * 0.2, z + rng.uniform(0.0, 0.06) * h))
        plate(m, robe, tuple(p), tuple(q), (-math.sin(a), math.cos(a), 0), h * 0.13, h * 0.03, h * 0.012)
    hy = y + h * 0.035
    ball(m, hood, x, hy, z + h * 0.86, h * 0.1, 8, 5)
    beam(m, hood, (x, hy - h * 0.02, z + h * 0.92), (x, hy - h * 0.1, z + h * 1.0), h * 0.1, None, h * 0.01)
    ball(m, dark, x, hy + h * 0.042, z + h * 0.85, h * 0.068, 8, 4)
    return hy + h * 0.042 + h * 0.068  # the front of the dark inside the hood, where eyes go


def headstone(m, role, x, y, w, h, t, tilt=(0.0, 0.0, 0.0), plaque=None):
    """A plain round-topped headstone, h tall, turned by tilt (radians round X, Y, Z)."""
    f = Frame(m, (x, y, 0), turn(*tilt))
    pts = [(-w / 2, -0.5), (w / 2, -0.5)]
    pts += [(w / 2 * math.cos(i * math.pi / 8), h - w / 2 + w / 2 * math.sin(i * math.pi / 8)) for i in range(9)]
    outline(m, role, f, pts, -t / 2, t / 2)
    if plaque:
        f.box(plaque, 0, t / 2 + 0.02, h * 0.56, w * 0.56, 0.08, h * 0.28)


def link_chain(m, role, a, b, count, size):
    """Chain links from a to b, each turned a quarter from the last."""
    a, b = Vector(a), Vector(b)
    along = (b - a) / count
    for k in range(count):
        c = a + along * (k + 0.5)
        half = along * 0.62
        if k % 2:
            beam(m, role, tuple(c - half), tuple(c + half), size, size * 0.45)
        else:
            beam(m, role, tuple(c - half), tuple(c + half), size * 0.45, size)


# ---------------------------------------------------------------------- floor props


def mourner(seed=1):
    """The map's signature: a hooded stone figure kneeling in the ash with its hands over its face, its shoulders
    rising and falling with each sob, tears of light running from under its hands into a pool at its knees. Between
    its fingers, as its shoulders rise, one red eye opens: it's been watching you all along."""
    m = prop("Mourner", Stone=STONE, StoneDark=STONE_DARK, Ash=ASH, Mantle=STONE, Hood=STONE_DARK, HoodDark=BLACK, Palms=STONE_LIGHT, Stare=RED,
             Tears=TEAR, Pool=POOL, Ripple=TEAR)
    m.loft_z("Ash", (0, 0, 0.5, 9.2, 8.8), (0.35, 0, 0.5, 7.8, 7.4))
    prism(m, "Stone", 0, -0.2, 0.2, 1.9, 3.15, 2.25, 8, math.pi / 8)
    for k in range(8):  # the robe's folds, pooling on the ground
        a = (k + 0.5) * math.tau / 8
        c, s = math.cos(a), math.sin(a)
        beam(m, "StoneDark", (c * 2.3, s * 2.3 - 0.2, 1.75), (c * 3.25, s * 3.25 - 0.2, 0.32), 0.55, None, 0.8)
    m.loft_y("Stone", (-0.8, 0, 1.0, 3.6, 1.8), (2.7, 0, 0.95, 3.0, 1.3))  # the lap, knees towards +Y
    prism(m, "Mantle", 0, -0.1, 1.4, 5.0, 2.2, 1.85, 8, math.pi / 8, lean=(0, 0.75))
    prism(m, "Mantle", 0, 0.65, 5.0, 6.1, 1.85, 0.95, 8, math.pi / 8, lean=(0, 0.35))
    prism(m, "Hood", 0, 0.85, 5.2, 6.4, 1.75, 1.5, 8, math.pi / 8)
    ball(m, "Hood", 0, 1.25, 6.55, 1.6, 8, 5)
    beam(m, "Hood", (0, 0.9, 7.4), (0, -0.5, 8.7), 1.7, None, 0.15)
    ball(m, "HoodDark", 0, 2.0, 6.35, 1.14, 8, 4)
    ball(m, "Stare", 0.26, 3.08, 6.62, 0.19, 6, 3)
    for s in (-1, 1):
        limb(m, "Mantle", [(s * 1.8, 0.6, 5.4), (s * 2.2, 1.9, 4.3), (s * 0.98, 3.05, 5.05)], 0.95, 0.62)
        hand(m, "Palms", (s * 0.95, 3.15, 5.1), (-s * 0.2, 0.02, 1), (0, 1, 0), size=0.92, spread=0.45, curl=0.14, thumb=s)
        drops(m, "Tears", s * 1.0, 3.45, 4.9, 0.5, 1.5, 0.13)
    pool(m, "Pool", [(0, 3.7, 3.6, 2.2), (1.1, 4.0, 1.8, 1.6), (-1.1, 3.9, 1.7, 1.8)], 0.41, 0.12)
    for s in (-1, 1):
        flat_ring(m, "Ripple", s * 1.0, 3.5, 0.5, 0.55, 0.07, 0.03, 10)
    return m


def empty_swing(seed=2):
    """A rusted swing set with nobody on it. One seat swings high and steadily, as if somebody had just jumped off;
    the other only stirs. A small pair of shoes waits under the first."""
    m = prop("EmptySwing", Iron=IRON, IronDark=IRON_DARK, ChainA=ASH_LIGHT, SeatA=WOOD, ChainB=ASH_LIGHT, SeatB=WOOD_DARK, Ash=ASH, AshLight=ASH_LIGHT,
             Shoe=BONE_DARK)
    top = 8.6
    m.loft_z("Ash", (0, 0, 0, 13.0, 7.4), (0.2, 0, 0, 12.2, 6.6))
    for x, y, w, d in ((-2.4, 0, 3.4, 4.6), (2.4, 0, 3.4, 3.2)):  # the ground worn bare under each seat
        m.block("AshLight", x, y, 0.23, w, d, 0.06)
    for x in (-5.0, 5.0):
        for y in (-2.5, 2.5):
            beam(m, "Iron", (x, y, 0), (x * 0.97, 0, top + 0.3), 0.42)
        beam(m, "IronDark", (x * 0.985, -1.3, 4.2), (x * 0.985, 1.3, 4.2), 0.24)
    tube(m, "Iron", (-5.5, 0, top), (5.5, 0, top), 0.24)
    for x, chain, seat in ((-2.4, "ChainA", "SeatA"), (2.4, "ChainB", "SeatB")):
        for dx in (-0.8, 0.8):
            m.block(chain, x + dx, 0, (top + 1.5) / 2, 0.11, 0.11, top - 1.5)
            m.block(chain, x + dx, 0, top - 0.02, 0.2, 0.34, 0.42)
        m.block(seat, x, 0, 1.45, 2.1, 0.85, 0.18)
    for dx, yaw in ((-0.32, 0.12), (0.3, -0.22)):  # the shoes
        f = Frame(m, (-2.4 + dx, 1.6, 0.26), turn(z=yaw))
        f.box("Shoe", 0, 0, 0.14, 0.42, 0.95, 0.28)
        f.box("Shoe", 0, -0.22, 0.34, 0.4, 0.46, 0.2)
    return m


CHAIR_RADIUS = 6.0
CHAIR_HEIGHT = 0.3 + 0.1 + CHAIR_RADIUS  # the middle of the rockers' curve


def rocking_chair(seed=3):
    """A rocking chair on what's left of a floor, rocking by itself with a shawl still on its back, and a candle
    burning on the little table beside it, for somebody who's late home. The rockers are a true curve round the
    point the game rocks it on, so it rolls on them."""
    m = prop("RockingChair", Plank=WOOD_DARK, PlankLight=WOOD, Chair=WOOD, Shawl=PLUSH_LIGHT, Table=WOOD_DARK, Wax=WAX, Flame=FLAME)
    rng = random.Random(seed)
    for i in range(7):
        m.block("Plank" if i % 2 else "PlankLight", -4.2 + i * 1.4, rng.uniform(-0.3, 0.3), 0.15, 1.35, rng.uniform(7.6, 9.2), 0.3)
    for x in (-1.25, 1.25):
        pts = []
        for k in range(7):
            a = -0.42 + 0.84 * k / 6
            pts.append((x, CHAIR_RADIUS * math.sin(a), CHAIR_HEIGHT - CHAIR_RADIUS * math.cos(a)))
        limb(m, "Chair", pts, 0.26, 0.26)
        beam(m, "Chair", (x, 1.25, 0.55), (x, 1.2, 2.05), 0.26)
        beam(m, "Chair", (x, -1.2, 0.55), (x, -1.2, 2.05), 0.26)
        beam(m, "Chair", (x, -1.2, 1.95), (x, -2.1, 5.9), 0.28)
        beam(m, "Chair", (x * 1.08, -1.5, 3.3), (x * 1.08, 1.2, 3.1), 0.3)  # arm rest
        beam(m, "Chair", (x * 1.08, 1.15, 2.05), (x * 1.08, 1.15, 3.15), 0.2)
    m.block("Chair", 0, 0.05, 2.05, 2.9, 2.8, 0.3)
    m.block("Chair", 0, -2.12, 5.95, 3.1, 0.34, 0.5)
    for x in (-0.65, 0, 0.65):
        beam(m, "Chair", (x, -1.3, 2.2), (x, -2.05, 5.7), 0.2)
    m.loft_z("Shawl", (3.4, 0.35, -2.06, 1.7, 0.14), (6.28, 0.35, -2.14, 2.1, 0.2))  # over the back
    m.loft_z("Shawl", (4.5, 0.35, -2.45, 1.7, 0.14), (6.28, 0.35, -2.34, 2.0, 0.22))
    m.block("Shawl", 0.35, -2.24, 6.3, 2.1, 0.56, 0.1)
    prism(m, "Table", 3.2, 0.8, 0.3, 2.3, 0.35, 0.18, 6)
    prism(m, "Table", 3.2, 0.8, 0.3, 0.55, 0.8, 0.45, 6)
    disc(m, "Table", 3.2, 0.8, 2.35, 1.1, 0.16, 10)
    candle(m, 3.2, 0.8, 2.43, 0.9, 0.17)
    return m


DOOR_OPEN = math.radians(30)


def waiting_window(seed=4):
    """All that's left of a house: its front wall, standing alone, with a candle on the sill for whoever's still out
    there and the door swinging on its hinge. The hinge stands on the origin, so the game swings the door round it.
    The window has upright bars only."""
    m = prop("WaitingWindow", Wall=WOOD_DARK, WallLight=WOOD, Trim=ASH_LIGHT, Door=WOOD, Window=WINDOW, Wax=WAX, Flame=FLAME, Stone=STONE_DARK, Mat=ASH_LIGHT,
             Ash=ASH, Curtain=PLUSH_DARK)
    rng = random.Random(seed)
    m.loft_z("Ash", (0, -0.8, 0, 14.0, 6.0), (0.2, -0.8, 0, 13.0, 5.2))
    tops = {-5.0: 10.6, -3.6: 11.4, -2.2: 10.4, -0.8: 11.8, 0.7: 10.0, 2.2: 10.9, 3.4: 10.2}
    y0, d = 0, 0.7
    m.block("Wall", -5.0, y0, 5.0, 1.15, d, 10)  # left of the window
    m.block("Wall", -0.8, y0, 2.8, 1.5, d, 5.6)  # between the window and the door
    m.block("Wall", -0.9, y0, 7.6, 7.0, d, 4.0)  # all along above them
    m.block("Wall", 3.4, y0, 4.2, 1.6, d, 8.4)  # right of the door
    m.block("Wall", -3.0, y0, 1.4, 2.8, d, 2.8)  # under the window
    for x, top in tops.items():  # the broken top of the wall
        m.block("WallLight", x, y0, top - 1.4, 1.4, d * 0.9, 2.8)
    for z in (2.2, 4.4, 8.0):  # boards
        m.block("WallLight", -5.0, y0 + 0.37, z, 1.15, 0.05, 0.14)
        m.block("WallLight", 3.4, y0 + 0.37, z, 1.6, 0.05, 0.14)
    m.block("Window", -3.0, -0.28, 4.2, 2.8, 0.06, 2.8)
    m.block("Curtain", -4.05, -0.14, 4.3, 0.7, 0.1, 2.5)
    m.loft_z("Curtain", (3.0, -2.0, -0.14, 0.4, 0.1), (5.55, -2.05, -0.14, 0.8, 0.1))
    for x in (-3.7, -2.3):
        m.block("Trim", x, 0.06, 4.2, 0.12, 0.14, 2.8)
    m.block("Trim", -3.0, 0.42, 2.76, 3.4, 0.6, 0.18)  # the sill
    m.block("Trim", -3.0, 0.38, 5.68, 3.2, 0.1, 0.2)
    candle(m, -3.0, 0.45, 2.85, 0.75, 0.15)
    for x in (0.12, 2.54):  # the door frame
        m.block("Trim", x, 0.38, 2.8, 0.2, 0.1, 5.6)
    obox(m, "Door", (1.2 * math.cos(DOOR_OPEN), 1.2 * math.sin(DOOR_OPEN), 2.82), (2.36, 0.16, 5.44), turn(z=DOOR_OPEN))
    f = Frame(m, (0, 0, 0), turn(z=DOOR_OPEN))
    for z in (1.4, 4.2):
        f.box("Trim", 1.2, 0.1, z, 1.7, 0.06, 1.8)
    f.box("Stone", 2.05, 0.14, 2.8, 0.16, 0.14, 0.16)
    m.block("Stone", 1.3, 1.1, 0.34, 3.1, 1.5, 0.3)  # the step
    m.block("Mat", 1.3, 2.75, 0.24, 2.3, 1.5, 0.1)
    for k in range(9):  # rubble behind, where the house was
        m.block("Wall" if k % 2 else "WallLight", rng.uniform(-6, 4), rng.uniform(-4.5, -1), 0.4 + k * 0.014, rng.uniform(0.8, 2.4), rng.uniform(0.3, 1.2), 0.3)
    return m


def headstones(seed=5):
    """A plot of plain round-topped headstones leaning in the ash, a broken iron fence round them, two candles still
    burning, and pale souls rising slowly out of the ground."""
    m = prop("Headstones", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Ash=ASH, AshDark=ASH_DARK, Iron=IRON, Wax=WAX, Flame=FLAME, Soul=TEAR)
    rng = random.Random(seed)
    m.loft_z("Ash", (0, 0, 0, 12.6, 10.4), (0.3, 0, 0, 11.6, 9.4))
    stones = ((-3.6, 1.2, 2.0, 3.8, -0.1, 0.12), (-0.6, 2.2, 2.3, 4.6, 0.04, -0.07), (2.7, 1.3, 2.0, 3.5, 0.07, 0.17), (-2.2, -2.2, 1.8, 3.1, -0.14, -0.1),
              (1.2, -2.0, 2.2, 4.1, 0.1, 0.08), (4.0, -2.4, 1.6, 2.5, -0.05, 0.28))
    for k, (x, y, w, h, tx, ty) in enumerate(stones):
        headstone(m, "Stone" if k % 3 else "StoneDark", x, y, w, h, 0.5, (tx, ty, rng.uniform(-0.2, 0.2)), "StoneLight" if k % 2 == 0 else None)
        m.loft_z("AshDark", (0.3, x, y + 1.1, 1.7, 2.6), (0.46, x, y + 1.0, 1.3, 2.2))  # the mound
    candle(m, -0.6, 3.1, 0.3, 0.8, 0.17)
    candle(m, 1.25, -0.9, 0.3, 0.55, 0.16)
    for x, y, top in ((-3.6, 2.2, 0.3), (2.7, 2.2, 0.3), (-2.2, -1.0, 0.3)):
        souls(m, "Soul", x, y, 1.0, 4, 2.0, 0.15)
    for i in range(12):  # the fence round the front and sides, with gaps where it fell
        if i in (4, 5, 9):
            continue
        a = -0.9 + i * 0.42
        x, y = 6.0 * math.cos(a), 4.9 * math.sin(a)
        lean = rng.uniform(-0.25, 0.25)
        beam(m, "Iron", (x, y, 0), (x + lean, y, 2.2), 0.15)
        gem(m, "Iron", x + lean, y, 2.2, 0.14, 0.38, 0.1, 4)
    for a, b in ((-0.9, 0.4), (1.3, 2.4), (3.1, 3.5)):
        pts = [(6.0 * math.cos(a + (b - a) * t / 4), 4.9 * math.sin(a + (b - a) * t / 4), 1.6) for t in range(5)]
        limb(m, "Iron", pts, 0.1, 0.1)
    return m


def black_willow(seed=6):
    """A dead weeping willow, black, its long strands hanging almost to the ground and stirring in air that doesn't
    move, tears of light dropping off the ends of them."""
    m = prop("BlackWillow", Bark=BARK, BarkDark=BARK_DARK, Strands=ASH_DARK, StrandsDark=BARK, Tears=TEAR, Ash=ASH)
    rng = random.Random(seed)
    dome(m, "Ash", 0, 0, 0, 2.2)
    limb(m, "Bark", [(0, 0, -0.3), (0.5, 0.1, 3), (0.15, -0.2, 6), (0.5, 0.1, 8.6)], 2.0, 1.0)
    for k in range(5):
        a = k * math.tau / 5 + 0.4
        c, s = math.cos(a), math.sin(a)
        limb(m, "BarkDark", [(c * 0.6, s * 0.6, 1.8), (c * 1.8, s * 1.8, 0.9), (c * 3.0, s * 3.0, 0.25)], 0.9, 0.3)
    tips = []
    for k in range(9):
        a = k * math.tau / 9 + rng.uniform(-0.2, 0.2)
        c, s = math.cos(a), math.sin(a)
        r = rng.uniform(5.0, 7.4)
        z0 = rng.uniform(6.4, 8.6)
        top = rng.uniform(12.2, 13.8)
        # A long bough rising from the trunk and arching over in one curve, drooping at the end.
        pts = [(0.4 + c * r * t, s * r * t, z0 + (top - z0) * math.sin(min(t, 0.82) / 0.82 * math.pi / 2) - max(0, t - 0.82) * 9) for t in (0, 0.18, 0.36, 0.54, 0.7, 0.84, 0.96, 1.08)]
        limb(m, "Bark", pts, 0.62, 0.07)
        for q in (2, 3, 4, 5, 6, 7):
            p = Vector(pts[q])
            for j in range(2 if q > 3 else 1):
                off = Vector((rng.uniform(-0.45, 0.45), rng.uniform(-0.45, 0.45), 0))
                length = rng.uniform(5.5, 10.5) * (0.65 + 0.07 * q)
                tip = p + off * 1.8 + Vector((0, 0, -length))
                tip.z = max(tip.z, 0.8)
                limb(m, "Strands" if j else "StrandsDark", [tuple(p), tuple(p + off + Vector((0, 0, -length * 0.55))), tuple(tip)], 0.15, 0.04, False)
                tips.append(tip)
    rng.shuffle(tips)
    for tip in tips[:7]:
        drops(m, "Tears", tip.x, tip.y, tip.z - 0.5, 0.4, 2.2, 0.11)
    return m


LID_HINGE = 2.95
LID_REST = math.radians(7)


def coffin(seed=7):
    """A black coffin on a stone bier, its lid lifting by itself and sinking back. Whatever's inside has pale fingers
    round the edge of the lid and red eyes in the gap. The lid hinges at the foot, which stands on the origin's X line,
    and it's modelled half open, so swinging it either way goes from shut to wide. Candles burn at its foot."""
    m = prop("Coffin", Stone=STONE_DARK, StoneLight=STONE, Box=WOOD_DARK, Trim=IRON, Inner=BLACK, Lid=WOOD, LidHand=BONE, Stare=RED, Wax=WAX, Flame=FLAME, Ash=ASH)
    m.block("Ash", 0, 4.2, 0.1, 7.2, 12.8, 0.2)
    m.block("Stone", 0, 4.2, 0.5, 5.8, 11.6, 0.6)
    m.block("StoneLight", 0, 4.2, 1.05, 4.8, 10.6, 0.5)
    shape = [(-0.8, 0), (0.8, 0), (1.5, 5.8), (1.05, 8.4), (-1.05, 8.4), (-1.5, 5.8)]
    root = Frame(m, (0, 0, 0))
    flat_outline(m, "Box", root, shape, 1.26, 2.92)
    flat_outline(m, "Trim", root, [(x * 1.06, y * 1.012 - 0.05) for x, y in shape], 1.3, 1.5)
    inner = [(x * 0.82, 0.4 + y * 0.9) for x, y in shape]
    flat_outline(m, "Inner", root, inner, 2.9, 2.96)
    for s in (-1, 1):
        ball(m, "Stare", s * 0.32, 7.75, 3.04, 0.15, 6, 3)
    lid = Frame(m, (0, 0, LID_HINGE), turn(x=LID_REST))
    flat_outline(m, "Lid", lid, [(x * 1.06, y) for x, y in shape], 0.02, 0.36)
    flat_outline(m, "Lid", lid, [(x * 0.7, 0.8 + y * 0.8) for x, y in shape], 0.36, 0.5)
    for y in (7.05, 7.45, 7.85, 6.65):  # fingers over the lid's edge at its right shoulder
        lid.beam("LidHand", (1.42, y, -0.45), (1.55, y, 0.42), 0.17)
        lid.beam("LidHand", (1.55, y, 0.42), (1.02, y, 0.5), 0.16, None, 0.09)
    for y in (6.95, 7.4):  # and two at its left
        lid.beam("LidHand", (-1.42, y, -0.45), (-1.55, y, 0.42), 0.17)
        lid.beam("LidHand", (-1.55, y, 0.42), (-1.04, y, 0.5), 0.16, None, 0.09)
    for x in (-2.0, 2.0):
        candle(m, x, -0.5, 1.3 - 0.5, 1.2, 0.17)
    return m


def reaching_hands(seed=8):
    """Long pale arms reaching up out of the ash, sliding slowly up and sinking back, their fingers spread. They go on
    well below the ground, so they never come loose from it."""
    m = prop("ReachingHands", HandA=BONE, HandB=BONE_DARK, Ash=ASH, AshDark=ASH_DARK)
    rng = random.Random(seed)
    m.loft_z("Ash", (0, 0, 0, 9.6, 8.8), (0.3, 0, 0, 8.4, 7.6))
    m.loft_z("AshDark", (0.3, 0.3, -0.2, 6.2, 5.6), (0.42, 0.3, -0.2, 5.6, 5.0))
    arms = (("HandA", (-2.0, 0.6), (-0.9, 0.4), 6.6, 1.35), ("HandB", (0.9, -1.2), (0.7, -0.5), 5.2, 1.15), ("HandA", (2.3, 1.2), (0.6, 0.5), 4.2, 1.2),
            ("HandB", (-0.6, 2.2), (-0.4, 0.8), 3.6, 1.0))
    for role, (x, y), (lx, ly), h, size in arms:
        wrist = (x + lx, y + ly, h)
        mid = (x + lx * 0.3, y + ly * 0.3, h * 0.45)
        limb(m, role, [(x, y, -3.0), mid, wrist], 0.95 * size, 0.55 * size)
        m.block(role, *wrist, 0.62 * size, 0.62 * size, 0.62 * size)
        ahead = (lx * 0.5, ly * 0.5, 1)
        hand(m, role, wrist, ahead, (rng.uniform(-1, 1), 1, 0.2), size=size * 1.2, spread=1.0, curl=0.3, long=1.45, thumb=1 if x > 0 else -1)
    return m


def lost_bear(seed=9):
    """A big worn teddy bear, left behind sitting on the ground against its owner's little suitcase, one button eye and
    one torn shoulder. Its head turns slowly after you, and the empty socket glows. Its head stands straight above
    the origin, so the game turns it round the upright."""
    m = prop("LostBear", Plush=PLUSH, PlushDark=PLUSH_DARK, Patch=PLUSH_LIGHT, BearHead=PLUSH, BearSnout=PLUSH_LIGHT, BearEar=PLUSH_DARK, BearEye=BLACK, Stare=RED,
             Stuffing=BONE, Case=WOOD, CaseDark=WOOD_DARK, Tag=BONE_DARK, Ash=ASH)
    m.loft_z("Ash", (0, 0, 0.1, 10.2, 11.2), (0.2, 0, 0.1, 9.4, 10.4))
    # The suitcase behind it.
    m.block("Case", 0, -3.5, 2.2, 6.2, 1.9, 4.0)
    m.block("CaseDark", 0, -3.5, 2.2, 6.3, 2.0, 0.3)
    for x in (-2.0, 2.0):
        m.block("CaseDark", x, -3.5, 2.2, 0.5, 2.05, 4.1)
    m.block("CaseDark", 0, -3.5, 4.45, 1.6, 0.34, 0.14)
    beam(m, "Tag", (1.1, -2.46, 3.6), (1.5, -2.46, 2.7), 0.5, 0.06)
    # The body.
    ball(m, "Plush", 0, -0.3, 2.2, 2.25, 10, 6)
    ball(m, "Patch", 0, 0.75, 2.0, 1.5, 8, 4)
    for s in (-1, 1):
        tube(m, "Plush", (s * 1.35, 0.7, 0.98), (s * 2.1, 3.5, 0.92), 0.95, 0.88, 8)
        disc(m, "Patch", s * 2.14, 3.62, 0.92, 0.68, 0.14, 10, "xz")
    limb(m, "Plush", [(-2.0, -0.1, 3.3), (-2.8, 0.3, 2.3), (-3.0, 1.2, 1.2)], 1.0, 0.8)
    ball(m, "PlushDark", -3.0, 1.3, 1.05, 0.56, 6, 4)
    limb(m, "Plush", [(2.2, 0.2, 2.6), (2.9, 0.8, 1.6), (3.1, 1.6, 0.8)], 0.95, 0.8)  # hanging by a thread
    ball(m, "PlushDark", 3.15, 1.7, 0.72, 0.54, 6, 4)
    for x, y, z, r in ((2.0, -0.2, 3.3, 0.62), (2.5, 0.2, 3.0, 0.46), (1.7, 0.4, 3.75, 0.4)):
        ball(m, "Stuffing", x, y, z, r, 6, 4)
    # The head, on the upright through the origin.
    ball(m, "BearHead", 0, 0, 5.21, 2.0, 10, 6)
    for s in (-1, 1):
        ball(m, "BearEar", s * 1.55, -0.1, 6.75, 0.78, 8, 4)
    ball(m, "BearSnout", 0, 1.68, 4.71, 0.86, 8, 4)
    m.block("BearEye", 0, 2.42, 5.05, 0.56, 0.3, 0.4)
    m.block("BearEye", 0, 2.42, 4.45, 0.09, 0.2, 0.7)
    disc(m, "BearEye", -0.78, 1.82, 5.6, 0.33, 0.14, 10, "xz")
    ball(m, "Stare", 0.78, 1.8, 5.6, 0.22, 6, 3)
    return m


def dying_lamp(seed=10):
    """A bent iron street lamp, the last on its road, its light sputtering, with moths going round it. The lamp hangs
    straight above the origin, so the moths circle it."""
    m = prop("DyingLamp", Iron=IRON, IronDark=IRON_DARK, Lamp=LAMP, LampA="#ffffff", Motes=BONE, Ash=ASH)
    rng = random.Random(seed)
    dome(m, "Ash", 1.6, 0, 0, 1.0)
    prism(m, "IronDark", 1.7, 0, 0, 1.3, 0.62, 0.36, 8)
    limb(m, "Iron", [(1.7, 0, 1.0), (1.65, 0.05, 5.0), (1.2, 0.1, 8.5), (1.5, 0, 10.8), (1.1, 0, 11.9), (0.3, 0, 12.2), (0, 0, 11.7)], 0.34, 0.17)
    prism(m, "IronDark", 0, 0, 11.2, 11.75, 0.75, 0.16, 6)  # the cap
    for k in range(4):
        a = k * math.tau / 4 + math.pi / 4
        beam(m, "IronDark", (math.cos(a) * 0.6, math.sin(a) * 0.6, 11.25), (math.cos(a) * 0.36, math.sin(a) * 0.36, 9.9), 0.07)
    prism(m, "IronDark", 0, 0, 9.76, 9.9, 0.46, 0.46, 6)
    prism(m, "Lamp", 0, 0, 9.9, 11.2, 0.3, 0.46, 6)
    ball(m, "LampA", 0, 0, 10.5, 0.22, 6, 4)
    for _ in range(7):
        a, r = rng.uniform(0, math.tau), rng.uniform(0.9, 1.9)
        m.block("Motes", math.cos(a) * r, math.sin(a) * r, rng.uniform(9.6, 11.5), 0.16, 0.05, 0.1)
    return m


def bearer(seed=11):
    """One of the bearers: a tall hooded shape with no feet, hanging just above the ground, holding out a lantern on a
    pole. Two red points in the dark of its hood. The hook's on the X line, so the lantern swings round it."""
    m = prop("Bearer", Robe=CLOTH, Hood=CLOTH_DARK, HoodDark=BLACK, Stare=RED, Pole=WOOD_DARK, Cage=IRON, Lamp=LAMP, Sleeve=CLOTH, Palms=BONE_DARK)
    rng = random.Random(seed)
    front = hooded(m, 0, 0, 0.6, 11.6, rng=rng)
    z_eye = 0.6 + 11.6 * 0.855
    for s in (-1, 1):
        ball(m, "Stare", s * 0.29, front - 0.05, z_eye, 0.11, 6, 3)
    limb(m, "Sleeve", [(1.3, 0.2, 8.8), (2.1, 0.5, 7.5), (2.5, 0.1, 7.1)], 0.95, 0.72)
    ball(m, "Palms", 2.6, 0, 7.05, 0.34, 6, 4)
    beam(m, "Pole", (2.6, 0, 1.8), (2.6, 0, 12.6), 0.17)
    beam(m, "Pole", (2.6, 0, 12.4), (5.0, 0, 12.2), 0.14)
    # The lantern hangs on the X line, so it swings round the hook.
    m.block("Cage", 4.8, 0, 11.8, 0.06, 0.06, 0.8)
    for k in range(4):
        a = k * math.tau / 4 + math.pi / 4
        beam(m, "Cage", (4.8 + math.cos(a) * 0.42, math.sin(a) * 0.42, 11.4), (4.8 + math.cos(a) * 0.42, math.sin(a) * 0.42, 10.3), 0.07)
    prism(m, "Cage", 4.8, 0, 11.4, 11.65, 0.6, 0.12, 6)
    prism(m, "Cage", 4.8, 0, 10.15, 10.3, 0.56, 0.56, 6)
    ball(m, "Lamp", 4.8, 0, 10.85, 0.4, 6, 4)
    return m


def ash_tuft(seed=12):
    """Filler: dead reeds in a heap of ash, bent by a wind nobody can feel."""
    m = prop("AshTuft", Ash=ASH, AshDark=ASH_DARK, Reeds=ASH_LIGHT, ReedsDark=STONE_DARK)
    rng = random.Random(seed)
    dome(m, "Ash", 0, 0, 0, 0.8)
    m.loft_z("AshDark", (0, 0.9, 0.5, 2.0, 1.8), (0.34, 0.9, 0.5, 1.2, 1.0))
    for k in range(13):
        a, r = rng.uniform(0, math.tau), rng.uniform(0.1, 1.2)
        x, y = math.cos(a) * r, math.sin(a) * r
        h = rng.uniform(1.8, 3.8)
        lean = rng.uniform(0.2, 0.9)
        beam(m, "Reeds" if k % 2 else "ReedsDark", (x, y, 0.2), (x + math.cos(a) * lean, y + math.sin(a) * lean, h), 0.17, None, 0.03)
    return m


def candle_stubs(seed=13):
    """Filler: burnt-down candles somebody left here, stuck in their own wax."""
    m = prop("CandleStubs", Wax=WAX, WaxDark=BONE_DARK, FlameA=FLAME, FlameB=FLAME, Ash=ASH)
    m.loft_z("Ash", (0, 0, 0, 3.8, 3.4), (0.14, 0, 0, 3.4, 3.0))
    pool(m, "WaxDark", [(0, 0, 2.6, 1.8), (0.5, 0.5, 1.5, 1.4), (-0.7, -0.3, 1.2, 1.2)], 0.17, 0.08)
    for k, (x, y, h, r) in enumerate(((0, 0.2, 1.2, 0.24), (-0.8, -0.3, 0.75, 0.22), (0.75, -0.4, 0.5, 0.2), (0.45, 0.8, 0.9, 0.2), (-0.5, 0.75, 0.42, 0.2),
                                      (-1.25, 0.35, 0.3, 0.18))):
        candle(m, x, y, 0.2, h, r, "FlameB" if k % 2 else "FlameA")
    return m


def tear_pool(seed=14):
    """Flat, so it can lie in the middle of the corridor where the eggs land: a black pool of tears, rings spreading
    on it, and a huge pale face under the surface looking up at whatever flies over, its hair drifting out round it.
    Sad brows, its mouth open, tears still running from its eyes, which open red. Its forehead is its Front: it lies
    with its chin towards the thrower, so it's the right way up from the flight. Under 0.5 tall."""
    m = prop("TearPool", Shore=ASH, Pool=POOL, Pale=BONE_DARK, PaleDark="#55544f", Socket=BLACK, Stream=STREAM, Stare=RED, Ripple=RIPPLE, RippleB=RIPPLE, Front=ASH)
    f = Frame(m, (0, 0, 0))
    rng = random.Random(seed)
    pool(m, "Shore", [(0, 0, 15.5, 13.0), (-4.2, 2.0, 8.0, 10.5), (4.0, -2.2, 8.5, 10.5), (0, 5.2, 8.0, 6.0), (0.5, -5.5, 7.0, 5.0)], 0.05, 0.1)
    pool(m, "Pool", [(0, 0, 14.0, 11.6), (-4.0, 2.0, 7.0, 9.4), (3.8, -2.2, 7.5, 9.4), (0, 5.0, 7.0, 5.0), (0.4, -5.2, 6.2, 4.2)], 0.11, 0.1)
    for k in range(17):  # its hair, drifting out from the top of its head
        a = math.radians(-20 + k * 220 / 16)
        c, s = math.cos(a), math.sin(a)
        wob = rng.uniform(-0.6, 0.6)
        p0, p1, p2 = (c * 2.9, s * 3.8), (c * 3.9 - s * wob, s * 4.8 + c * wob), (c * 4.8 + s * wob, s * 5.6 - c * wob)
        for (ax, ay), (bx, by), w0, w1 in ((p0, p1, 0.34, 0.22), (p1, p2, 0.22, 0.06)):
            plate(m, "PaleDark", (ax, ay, 0.2), (bx, by, 0.2), (-(by - ay), bx - ax, 0), w0, w1, 0.03)
    flat_outline(m, "Pale", f, oval(3.1, 4.1), 0.1, 0.24)
    for s in (-1, 1):  # raised at the middle: sad
        flat_outline(m, "PaleDark", f, [(s * 0.5, 2.05), (s * 2.3, 1.25), (s * 2.3, 0.95), (s * 0.5, 1.7)], 0.21, 0.27)
        flat_outline(m, "Socket", f, oval(0.86, 0.68, 10, s * 1.3, 0.55), 0.23, 0.28)
        flat_outline(m, "Stare", f, oval(0.3, 0.3, 8, s * 1.3, 0.55), 0.27, 0.31)
        flat_outline(m, "Stream", f, [(s * 1.24, 0.0), (s * 1.38, 0.0), (s * 1.71, -3.55), (s * 1.57, -3.55)], 0.23, 0.27)
    flat_outline(m, "PaleDark", f, [(-0.28, 0.1), (0.28, 0.1), (0.5, -0.85), (-0.5, -0.85)], 0.21, 0.26)
    flat_outline(m, "Socket", f, oval(0.95, 1.3, 12, 0, -2.2), 0.23, 0.28)
    flat_ring(m, "Ripple", 0, 0, 0.33, 4.7, 0.12, 0.05, 20)
    flat_ring(m, "RippleB", 0, 0, 0.35, 6.2, 0.1, 0.05, 20)
    m.block("Front", 0, 6, 0.2, 0.1, 0.1, 0.1)
    return m


# ---------------------------------------------------------------------- rim props


def claw_tree(seed=15):
    """A bare black tree whose branches grow like the fingers of a hand clawing up out of the ground. Its top sways."""
    m = prop("ClawTree", Bark=BARK, BarkDark=BARK_DARK, Claws=BARK, Ash=ASH)
    rng = random.Random(seed)
    dome(m, "Ash", 0, 0, 0, 1.5)
    limb(m, "Bark", [(0, 0, -0.3), (0.4, 0.2, 2.6), (-0.2, 0, 5.2)], 1.9, 1.3)
    for k in range(4):
        a = k * math.tau / 4 + 0.7
        c, s = math.cos(a), math.sin(a)
        limb(m, "BarkDark", [(c * 0.5, s * 0.5, 1.5), (c * 1.5, s * 1.5, 0.7), (c * 2.4, s * 2.4, 0.2)], 0.8, 0.26)
    for k, (a, reach, h) in enumerate(((0.3, 3.8, 11.6), (1.6, 3.2, 13.6), (2.9, 3.6, 12.6), (4.2, 3.4, 11.8), (5.3, 3.0, 9.8))):
        c, s = math.cos(a), math.sin(a)
        pts = [(-0.2, 0, 5.0), (c * reach * 0.7, s * reach * 0.7, 6.9), (c * reach, s * reach, h * 0.8), (c * reach * 0.82, s * reach * 0.82, h),
               (c * reach * 0.45, s * reach * 0.45, h + 1.1)]
        limb(m, "Claws", pts, 0.72, 0.07)
        p = Vector(pts[2])
        for j in range(2):
            q = p + Vector((rng.uniform(-1.3, 1.3), rng.uniform(-1.3, 1.3), rng.uniform(0.6, 1.8)))
            beam(m, "Claws", tuple(p), tuple(q), 0.2, None, 0.03)
    return m


def hollow_house(seed=16):
    """A tall crooked house, black and empty, with one lit window. Every so often something dark rises in the window,
    stands there, and sinks away again. It bobs behind the sill, so most of the time it's hidden. A loose shutter
    bangs on the floor above."""
    m = prop("HollowHouse", Wall=WOOD_DARK, WallLight=WOOD, Trim=ASH_LIGHT, Roof=IRON_DARK, RoofLight=IRON, Stone=STONE_DARK, Window=WINDOW, Shade=BLACK, Shutter=WOOD,
             Hole=BLACK, Door=WOOD)
    yf = 5.0  # the front wall's face
    d = 0.8
    m.block("Stone", 0, 0, 0.5, 11.2, 11.2, 1.0)
    m.loft_z("Wall", (1.0, 0, -0.45, 10.2, 9.1), (10.0, 0.4, -0.45, 10.0, 9.1))  # the house behind the front wall
    x0, x1, z0, z1 = -1.4, 1.4, 4.0, 7.2
    m.block("WallLight", -3.45, yf - d / 2, 5.5, 4.1, d, 9.0)
    m.block("WallLight", 3.45, yf - d / 2, 5.5, 4.1, d, 9.0)
    m.block("WallLight", 0, yf - d / 2, 2.5, 2.8, d, 3.0)
    m.block("WallLight", 0, yf - d / 2, 8.6, 2.8, d, 2.8)
    m.block("Window", 0, yf - d - 0.06, 5.6, 3.0, 0.1, 3.4)
    for x in (-0.48, 0.48):
        m.block("Trim", x, yf - 0.1, 5.6, 0.12, 0.14, 3.2)
    m.block("Trim", 0, yf + 0.14, 3.92, 3.4, 0.5, 0.18)
    m.block("Trim", 0, yf + 0.04, 7.3, 3.2, 0.14, 0.2)
    # What stands in the window: built low, so it's below the sill unless it rises.
    sy = yf - d + 0.2
    ball(m, "Shade", 0, sy, 3.3, 0.72, 6, 4)
    m.loft_z("Shade", (0.8, 0, sy, 2.6, 0.2), (2.7, 0, sy, 1.5, 0.2))
    # The upper floor leans out, crooked.
    m.loft_z("Wall", (10.0, 0.4, 0, 11.0, 10.2), (15.8, 1.2, 0.2, 10.4, 9.8))
    m.block("Hole", 1.4, 5.32, 13.0, 2.4, 0.1, 3.0)
    m.block("Trim", 1.4, 5.34, 11.4, 2.8, 0.26, 0.16)
    m.block("Shutter", 3.3, 5.56, 13.0, 1.2, 0.12, 2.9)  # turns round its own middle
    # The roof, sagging, and a broken chimney.
    m.loft_z("Roof", (15.8, 1.2, 0.2, 12.4, 11.6), (18.6, 1.5, 0.3, 8.6, 8.0))
    m.loft_z("RoofLight", (18.6, 1.5, 0.3, 8.6, 8.0), (21.8, 2.2, 0.5, 0.8, 0.8))
    m.loft_z("Stone", (17.4, -2.6, -1.8, 1.8, 1.8), (22.6, -2.9, -1.8, 1.5, 1.5))
    # The door, shut, under a little porch roof.
    m.block("Door", -3.3, yf + 0.04, 2.6, 2.1, 0.14, 3.2)
    m.block("Trim", -3.3, yf + 0.08, 4.34, 2.6, 0.2, 0.2)
    m.block("Stone", -3.3, yf + 0.9, 0.7, 2.8, 1.8, 0.6)
    return m


# ---------------------------------------------------------------------- landmarks


def last_lighthouse(seed=17):
    """The last lighthouse, leaning on its rock at the edge of everything, its beam still sweeping out over the dark
    for a ship that isn't coming. The light stands straight above the origin, so the beam turns round the tower.
    The beam's see-through in the game (Roles.sheer)."""
    m = prop("LastLighthouse", Rock=STONE_DARK, RockDark=ASH, Tower=STONE_LIGHT, Band=IRON, Iron=IRON_DARK, Roof=IRON, Beacon="#ffffff", Sweep=TEAR, Hole=BLACK, Window=WINDOW,
             Front=STONE)
    rng = random.Random(seed)
    for x, y, w, d, h in ((0, 0, 17, 16, 5), (-5, -2, 8, 8, 7), (5, 3, 7, 6, 4), (-4, 5, 6, 5, 3.4), (4.8, -4.6, 6.4, 5.6, 5.6)):
        m.loft_z("Rock", (0, x - 1.4, y, w, d), (h * 0.6, x - 1.4, y, w * 0.86, d * 0.84))
        m.loft_z("RockDark", (h * 0.6, x - 1.4, y, w * 0.86, d * 0.84), (h, x - 1.2, y, w * 0.55, d * 0.5))
    bands = 6
    z0, z1 = 4.0, 27.0
    r0, r1 = 4.6, 2.9
    for i in range(bands):  # leaning: its foot off to one side, its top over the origin
        t0, t1 = i / bands, (i + 1) / bands
        x0, x1 = -1.6 * (1 - t0), -1.6 * (1 - t1)
        prism(m, "Tower" if i % 2 == 0 else "Band", x0, 0, z0 + (z1 - z0) * t0, z0 + (z1 - z0) * t1, r0 + (r1 - r0) * t0, r0 + (r1 - r0) * t1, 10, 0.31, lean=(x1 - x0, 0))
    m.block("Hole", -1.15, 4.34, 6.3, 1.9, 0.5, 3.4)  # the door
    m.block("Hole", -0.42, 3.6, 13.7, 1.0, 0.5, 1.6)
    m.block("Window", -0.05, 3.26, 21.0, 0.9, 0.5, 1.5)
    disc(m, "Iron", 0, 0, 27.2, 4.2, 0.4, 12)
    for k in range(10):  # the rail, broken away on one side
        if k in (3, 4):
            continue
        a = k * math.tau / 10
        x, y = 3.95 * math.cos(a), 3.95 * math.sin(a)
        beam(m, "Iron", (x, y, 27.3), (x, y, 28.7), 0.13)
        if k not in (2, 5):
            a2 = (k + 1) * math.tau / 10
            beam(m, "Iron", (x, y, 28.6), (3.95 * math.cos(a2), 3.95 * math.sin(a2), 28.6), 0.1)
    prism(m, "Iron", 0, 0, 27.4, 28.1, 2.4, 2.4, 10, 0.31)
    for k in range(6):
        a = k * math.tau / 6
        beam(m, "Iron", (2.1 * math.cos(a), 2.1 * math.sin(a), 28.1), (2.0 * math.cos(a), 2.0 * math.sin(a), 31.4), 0.18)
    ball(m, "Beacon", 0, 0, 29.8, 1.3, 8, 5)
    prism(m, "Roof", 0, 0, 31.4, 33.8, 2.9, 0.24, 10, 0.31)
    ball(m, "Roof", 0, 0, 34.0, 0.34, 6, 4)
    for s in (-1, 1):  # two beams, opposite each other, tipping down into the corridor
        tube(m, "Sweep", (s * 1.4, 0, 29.8), (s * 74, 0, 22), 0.4, 3.2, 8)
    m.block("Front", 0, 9, 1, 0.2, 0.2, 0.2)
    return m


BELL_HOOK = 19.4


def bell_tower(seed=18):
    """A plain stone bell tower, open on all four sides, its great black bell tolling slowly with nobody at the rope.
    The bell and its clapper hang on the X line at the hook's height, so they swing together. No cross on top."""
    m = prop("BellTower", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Roof=IRON, RoofDark=IRON_DARK, Beam=WOOD_DARK, Bell=BARK, BellRim=ASH_LIGHT, Clapper=IRON_DARK, Rope=ASH_LIGHT,
             Ash=ASH, Front=STONE)
    rng = random.Random(seed)
    m.loft_z("Ash", (0, 0, 0, 19, 19), (0.6, 0, 0, 17.4, 17.4))
    m.block("StoneDark", 0, 0, 1.1, 15.4, 15.4, 1.0)
    m.block("Stone", 0, 0, 2.1, 13.6, 13.6, 1.0)
    for x in (-5, 5):
        for y in (-5, 5):
            m.block("Stone", x, y, 12.2, 2.6, 2.6, 18.4)
            m.block("StoneDark", x, y, 3.4, 3.2, 3.2, 1.6)
            m.block("StoneLight", x, y, 21.6, 3.2, 3.2, 0.8)
    for z in (11.8,):  # a ring of stone halfway up, left open
        for s in (-1, 1):
            m.block("StoneDark", s * 5, 0, z, 1.4, 7.6, 1.0)
    for s in (-1, 1):  # arches over the openings, front and back and at the sides
        for a, b in (((-3.8, s * 5, 19.4), (0, s * 5, 21.3)), ((3.8, s * 5, 19.4), (0, s * 5, 21.3))):
            beam(m, "StoneDark", a, b, 1.4, 1.2)
        for a, b in (((s * 5, -3.8, 19.4), (s * 5, 0, 21.3)), ((s * 5, 3.8, 19.4), (s * 5, 0, 21.3))):
            beam(m, "StoneDark", a, b, 1.4, 1.2)
    m.block("StoneLight", 0, 0, 22.4, 15.0, 15.0, 0.9)
    m.loft_z("Roof", (22.85, 0, 0, 16.2, 16.2), (28.0, 0.6, 0.3, 7.4, 7.4))
    m.loft_z("RoofDark", (28.0, 0.6, 0.3, 7.4, 7.4), (33.0, 1.4, 0.8, 0.5, 0.5))  # crooked
    tube(m, "Beam", (-6.2, 0, BELL_HOOK + 0.5), (6.2, 0, BELL_HOOK + 0.5), 0.55, None, 8)
    # The bell, hanging from the hook.
    steps = ((BELL_HOOK - 0.2, 0.6), (BELL_HOOK - 1.0, 1.15), (BELL_HOOK - 2.6, 1.45), (BELL_HOOK - 5.4, 1.85), (BELL_HOOK - 7.2, 2.7), (BELL_HOOK - 7.9, 3.3))
    for (za, ra), (zb, rb) in zip(steps, steps[1:]):
        prism(m, "Bell", 0, 0, zb, za, rb, ra, 12, 0.26)
    prism(m, "BellRim", 0, 0, BELL_HOOK - 8.15, BELL_HOOK - 7.7, 3.42, 3.2, 12, 0.26)
    m.block("Bell", 0, 0, BELL_HOOK + 0.1, 0.7, 1.1, 0.9)
    m.block("Clapper", 0, 0, BELL_HOOK - 4.9, 0.3, 0.3, 8.0)
    ball(m, "Clapper", 0, 0, BELL_HOOK - 9.0, 0.72, 8, 4)
    # The rope, frayed, hanging to the ground.
    beam(m, "Rope", (2.6, 0, BELL_HOOK - 2.8), (2.6, 0.2, 3.4), 0.2)
    beam(m, "Rope", (0.9, 0, BELL_HOOK - 2.6), (2.6, 0, BELL_HOOK - 2.8), 0.2)
    for k in range(4):
        a = k * math.tau / 4
        beam(m, "Rope", (2.6, 0.2, 3.5), (2.6 + 0.4 * math.cos(a), 0.2 + 0.4 * math.sin(a), 2.9), 0.1, None, 0.03)
    m.block("Front", 0, 10, 1, 0.2, 0.2, 0.2)
    return m


def wailing_head(seed=19):
    """A colossal hooded head sunk in the ash to its shoulders, its stone mouth open in a silent wail and rivers of
    tears running down its cheeks. Its brows rise at the middle, which reads as grief. Its stone eyelids lift slowly,
    and the eyes under them are red."""
    m = prop("WailingHead", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Hood=STONE_DARK, HoodDark=ASH_DARK, Ash=ASH, Socket=BLACK, Maw=BLACK, Stare=RED, Eyelid=STONE_LIGHT,
             Stream=STREAM, Tears=TEAR, Front=STONE)
    rng = random.Random(seed)
    m.loft_z("Ash", (0, 0, 2, 42, 34), (2.4, 0, 2, 32, 26))
    m.loft_z("Hood", (0, 0, -2, 36, 28), (9, 0, -3, 28, 22))  # shoulders
    prism(m, "Hood", 0, -7, 6, 24, 15.5, 13.5, 10, 0.31)
    prism(m, "Hood", 0, -7, 24, 33, 13.5, 4.5, 10, 0.31, lean=(0, -3))
    # The face, wider at the brow than at the chin.
    m.loft_z("Stone", (1.5, 0, 5, 10, 9), (21, 0, 5, 16.4, 9))
    m.loft_z("Stone", (21, 0, 5, 16.4, 9), (27, 0, 3.5, 12, 7))
    # The cowl round the face.
    arch = [(-10.8, 8.4, 2.5), (-11.2, 8.8, 12), (-10.4, 8.4, 21), (-6.8, 7.6, 28), (0, 7.0, 30.4), (6.8, 7.6, 28), (10.4, 8.4, 21), (11.2, 8.8, 12), (10.8, 8.4, 2.5)]
    limb(m, "Hood", arch, 5.0, 5.0)
    face = 9.55
    for s in (-1, 1):
        rot = turn(y=s * 0.26)
        obox(m, "Socket", (s * 3.9, face + 0.02, 15.2), (5.0, 0.3, 3.2), rot)
        disc(m, "Stare", s * 3.9, face + 0.28, 15.2, 1.18, 0.2, 12, "xz")
        obox(m, "Eyelid", (s * 3.9, face + 0.62, 15.7), (5.2, 0.34, 2.5), rot)
        beam(m, "StoneLight", (s * 0.9, face + 0.75, 19.4), (s * 7.6, face + 0.35, 16.4), 1.5, 1.1)  # brows up at the middle: grief
        beam(m, "StoneDark", (s * 2.0, face + 0.1, 11.4), (s * 7.0, face + 0.02, 9.0), 0.5, 0.3)  # the fold under the cheek
        m.block("Stream", s * 3.9, face + 0.32, 7.7, 0.6, 0.1, 13.0)
        for dx in (-0.25, 0.25):
            drops(m, "Tears", s * 3.9 + dx, face + 0.6, 13.6, 0.6, 3.0, 0.3)
    m.loft_z("Stone", (10, 0, face + 0.4, 3.4, 2.0), (15.6, 0, face, 1.6, 0.9))  # the nose
    outline(m, "Maw", Frame(m, (0, 0, 0)), [(-3.2, 6.4), (-2.4, 8.0), (0, 8.5), (2.4, 8.0), (3.2, 6.4), (2.5, 3.0), (0, 2.2), (-2.5, 3.0)], face - 0.2, face + 0.2)
    limbs = [(-3.3, 6.2), (-2.5, 8.2), (0, 8.8), (2.5, 8.2), (3.3, 6.2), (2.6, 2.9), (0, 2.0), (-2.6, 2.9), (-3.3, 6.2)]
    limb(m, "StoneLight", [(x, face + 0.28, z) for x, z in limbs], 0.5, 0.5)
    for k in range(5):  # cracks across the brow and the hood
        p = Vector((rng.uniform(-5, 5), face + 0.05, rng.uniform(21, 26)))
        q = p + Vector((rng.uniform(-2.5, 2.5), 0, rng.uniform(-3, 2)))
        beam(m, "StoneDark", tuple(p), tuple(q), 0.26, 0.2)
    m.block("Front", 0, 14, 1, 0.2, 0.2, 0.2)
    return m


# ---------------------------------------------------------------------- sky, walls, overhead


def watcher(seed=20):
    """Beyond the walls, where you thought there was only sky: something colossal standing in the void. A black hooded
    shape as tall as the world, its long arms folded out from high elbows and its long pale fingers resting on the
    island's edge. It doesn't do anything. Its head turns slowly, following you, its two red eyes open and close, and
    tears fall from them a long way down. Its origin is at rim height, and it hangs far below that. At size 3 and
    266 out from the middle, its fingers rest on the rim's outer edge."""
    m = prop("Watcher", Shroud=CLOTH_DARK, ShroudDark=BLACK, Hood=CLOTH_DARK, HoodDark=BLACK, Stare=RED, Tears=TEAR, Sleeve=CLOTH_DARK, Fingers=BONE_DARK, Front=CLOTH_DARK)
    rng = random.Random(seed)
    rows = ((-170, 7), (-90, 15), (-10, 21), (40, 24), (66, 22.5), (80, 12))
    for k, ((za, ra), (zb, rb)) in enumerate(zip(rows, rows[1:])):
        prism(m, "Shroud", 0, 0, za, zb, ra, rb, 10, 0.31, lean=(0, 2))
    for k in range(10):  # long folds
        a = (k + 0.5) * math.tau / 10
        c, s = math.cos(a), math.sin(a)
        beam(m, "ShroudDark", (c * 15, s * 15, -90), (c * 24.4, s * 24.4 + 3, 44), 2.2, None, 1.6)
    ball(m, "Hood", 0, 6, 92, 15, 10, 6)
    prism(m, "Hood", 0, 4, 76, 90, 14, 14.5, 10, 0.31)
    beam(m, "Hood", (0, 2, 100), (0, -8, 116), 15, None, 1.0)
    ball(m, "HoodDark", 0, 13, 90.5, 10.2, 10, 5)
    for s, z in ((-1, 91.6), (1, 90.6)):
        ball(m, "Stare", s * 4.2, 22.4, z, 2.3, 8, 4)
        drops(m, "Tears", s * 4.2, 24.2, z - 6, 34, 20, 0.5)
    for s in (-1, 1):
        shoulder = (s * 21, 6, 64)
        elbow = (s * 47, 18, 98)
        wrist = (s * 26, 47, 6)
        limb(m, "Sleeve", [shoulder, ((shoulder[0] + elbow[0]) / 2, 12, 86), elbow], 11, 6.5)
        limb(m, "Sleeve", [elbow, (s * 38, 33, 54), (s * 28, 44, 16)], 6.5, 3.6)
        for k in range(5):  # rags hanging off the arm
            t = 0.15 + 0.17 * k
            p = Vector(shoulder).lerp(Vector(elbow), t)
            plate(m, "ShroudDark", tuple(p), tuple(p + Vector((rng.uniform(-3, 3), rng.uniform(-2, 2), -rng.uniform(16, 34)))), (1, 0.3, 0), 7, 0.6, 0.5)
        # The hand, its long fingers curled on the rim. z stays above the rim's top.
        beam(m, "Fingers", (s * 28, 44, 16), wrist, 3.4)
        hand(m, "Fingers", wrist, (-s * 0.1, 1, -0.08), (0, 0.2, 1), size=4.6, spread=0.7, curl=0.1, long=1.3, thumb=-s)
    m.block("Front", 0, 30, 0, 0.3, 0.3, 0.3)
    return m


def weeping_wall(seed=21):
    """Hangs down a corridor wall: heads pushing out of the stone as if through a sheet, mouths stretched open, hollow
    eyes crying long lines of light that run to the floor. Pale hands are pressed against the wall beside them, trying
    to get out. The smallest has opened its eyes. Rim at Z 0, floor at Z -44, +Y into the corridor."""
    m = prop("WeepingWall", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Socket=BLACK, Maw=BLACK, Stream=STREAM, Tears=TEAR, Stare=RED, Palms=BONE_DARK, Front=STONE)
    root = Frame(m, (0, 0, 0))

    def tilted(pts, cx, cz, by):
        c, s = math.cos(by), math.sin(by)
        return [(cx + (x - cx) * c - (z - cz) * s, cz + (x - cx) * s + (z - cz) * c) for x, z in pts]

    def face(cx, cz, w, h, open_eyes=False):
        y = 1.8
        # The head swelling out of the wall: ovals, each smaller and further out, long at the chin.
        for scale, step, role in ((1.2, 0.5, "StoneDark"), (1.06, 0.9, "StoneDark"), (0.95, 0.9, "Stone"), (0.84, 0.7, "Stone")):
            outline(m, role, root, oval(w / 2 * scale, h / 2 * scale, 14, cx, cz), y, y + step)
            y += step
        front = y
        for s in (-1, 1):
            ex, ez = cx + s * w * 0.19, cz + h * 0.1
            sad = s * 0.42  # the outer ends droop
            outline(m, "Socket", root, tilted(oval(w * 0.14, h * 0.082, 10, ex, ez), ex, ez, sad), front - 0.1, front + 0.1)
            if open_eyes:
                disc(m, "Stare", ex, front + 0.12, ez, w * 0.05, 0.12, 8, "xz")
            beam(m, "StoneLight", (cx + s * w * 0.05, front + 0.15, cz + h * 0.25), (cx + s * w * 0.38, front + 0.1, cz + h * 0.14), w * 0.05, w * 0.04)
            m.block("Stream", ex, front + 0.12, (ez - 44) / 2, 0.22, 0.08, ez + 44)
            drops(m, "Tears", ex, front + 0.32, ez - 1.0, -43, 4, 0.2)
        m.loft_z("Stone", (cz - h * 0.08, cx, front + 0.25, w * 0.14, 0.6), (cz + h * 0.1, cx, front + 0.1, w * 0.07, 0.25))
        outline(m, "Maw", root, oval(w * 0.13, h * 0.17, 12, cx, cz - h * 0.25), front - 0.1, front + 0.1)

    face(-4, -19, 14, 21)
    face(11, -30, 8.5, 13, True)
    face(-15, -33, 7.5, 11.5)
    hand(m, "Palms", (8, 2.3, -17), (0.15, 0, 1), (0, 1, 0), size=2.3, spread=0.75, curl=0.03, long=1.25, thumb=-1)
    hand(m, "Palms", (17, 2.3, -15), (-0.1, 0, 1), (0, 1, 0), size=2.0, spread=0.75, curl=0.03, long=1.25, thumb=1)
    hand(m, "Palms", (-17, 2.3, -20), (-0.2, 0, 1), (0, 1, 0), size=1.8, spread=0.75, curl=0.03, long=1.25, thumb=-1)
    m.block("Front", 0, 7, -22, 0.2, 0.2, 0.2)
    return m


def long_arm(seed=22):
    """One long arm reaching from behind one rim right over the corridor, its fingers gripping the other rim. Rags of
    black sleeve hang off the top of it. Nothing's attached that you can see. Its fingers tap slowly on the stone. Built
    for a 72-wide corridor (feet beyond 36), all of it above the rim."""
    m = prop("LongArm", Arm=BONE_DARK, ArmDark="#6c6a65", Sleeve=CLOTH_DARK, Rags=CLOTH, Fingers=BONE, Ash=ASH, Front=BONE_DARK)
    rng = random.Random(seed)
    shoulder = (-60, 0, 3.4)
    elbow = (-20, 1, 46)
    wrist = (17, 0, 22)
    m.loft_z("Ash", (0, -60, 0, 18, 18), (2.2, -60, 0, 10, 10))
    limb(m, "Sleeve", [shoulder, (-46, 0.5, 18), (-33, 1, 34), elbow], 7.6, 5.4)
    limb(m, "Arm", [elbow, (-4, 1, 40), (8, 0.5, 31), wrist], 4.6, 2.8)
    ball(m, "ArmDark", *elbow, 3.4, 8, 5)
    for k in range(7):
        t = 0.1 + 0.13 * k
        p = Vector(shoulder).lerp(Vector(elbow), t)
        tip = p + Vector((rng.uniform(-1.4, 1.4), rng.uniform(-2, 2), -rng.uniform(5, 13)))
        tip.z = max(tip.z, 0.6)  # the whole arm stays above the rim
        plate(m, "Rags", tuple(p), tuple(tip), (0, 1, 0), 5, 0.4, 0.3)
    # A huge hand, as wide as a monster's foot, coming down on the far rim.
    hand(m, "Fingers", wrist, (1, 0, -0.68), (0.7, 0, 1), size=11, spread=0.62, curl=0.22, long=1.0, thumb=-1)
    m.block("Front", 0, 6, 12, 0.2, 0.2, 0.2)
    return m


def procession(seed=23):
    """A funeral going along the edge of the wall in the dark for ever: hooded bearers in single file, a long coffin on
    the shoulders of the middle four, a lantern at the head and one at the tail. It glides head first (its Leader) and
    fades out and back. Drift overrides every other move, so nothing on it moves by itself."""
    m = prop("Procession", Robe=CLOTH, Hood=CLOTH_DARK, HoodDark=BLACK, Coffin=WOOD_DARK, CoffinLid=WOOD, Pole=WOOD_DARK, Lamp=LAMP, Leader=LAMP, Cage=IRON, Front=CLOTH)
    rng = random.Random(seed)
    h = 9.0
    spots = (24, 13, 5.5, -2, -9.5, -20)
    for y in spots:
        hooded(m, 0, y, 0.3, h, rng=rng)
    for y in spots[1:-1]:  # the bearers' second column, side by side under the coffin
        hooded(m, 3.4, y, 0.3, h, rng=rng)
    # Shift: the middle four walk in pairs, the coffin between their shoulders.
    root = Frame(m, (1.7, 0, 0))
    flat_outline(m, "Coffin", root, [(-0.9, -13), (0.9, -13), (1.6, 5), (1.1, 9), (-1.1, 9), (-1.6, 5)], 8.2, 9.3)
    flat_outline(m, "CoffinLid", root, [(-0.95, -13.1), (0.95, -13.1), (1.66, 5), (1.16, 9.1), (-1.16, 9.1), (-1.66, 5)], 9.3, 9.55)
    for y, role, x in ((24, "Leader", 0), (-20, "Lamp", 0)):
        beam(m, "Pole", (x + 1.1, y + 1.1, 3.4), (x + 1.1, y + 1.1, 10.6), 0.14)
        beam(m, "Pole", (x + 1.1, y + 1.1, 10.6), (x + 1.1, y + 2.5, 10.8), 0.12)
        prism(m, "Cage", x + 1.1, y + 2.5, 9.95, 10.2, 0.5, 0.1, 6)
        ball(m, role, x + 1.1, y + 2.5, 9.6, 0.38, 6, 4)
    m.block("Front", 0, 30, 1, 0.2, 0.2, 0.2)
    return m


DOOR_FRONT = 26  # the door's face, from the origin: far enough that the eye moves a good way as it turns round the origin
DOOR_AT = 3726  # where the door's face stands, from this world's start: the corridor's end, past Shattered Mirror (1900 long) since
# 2026-11-13; it was 1826 when this was the last map. The end wall is 10 behind it: the eye behind the door must clear it


def last_door(seed=24):
    """The end of the world, and the end of the corridor: where every other map only ever had a wall. A colossal black
    door filling the corridor from the floor to high above the rims, chains across it and two great mourners carved
    into it, crying down its face. It isn't quite shut. Pale fingers as long as a player is tall hold the edge of it from
    the other side, and in the gap an eye moves from side to side. In front of it, across the whole floor, a sea of
    candles: everyone who ever came this far left one.

    Rim at Z 0, corridor floor at Z -44. +Y faces back up the corridor, towards the thrower. The eye turns round the
    origin, which stands DOOR_FRONT behind the door's face."""
    m = prop("LastDoor", Stone=STONE_DARK, StoneDark=ASH, StoneLight=STONE, Leaf=BARK, LeafEdge=IRON, Band=IRON_DARK, Rivet=ASH_LIGHT, Relief=ASH_LIGHT, ReliefDark=STONE_DARK, Stream=STREAM, Tears=TEAR, Void=BLACK,
             Sclera=BONE_DARK, Stare=RED, EyeSlit=BLACK, Fingers=BONE, FingersB=BONE_DARK, Chain=ASH_LIGHT, Lock=IRON, Wax=WAX, WaxDark=BONE_DARK, FlameA=FLAME, FlameB=FLAME, Lamp=LAMP, Cage=IRON, Front=STONE)
    rng = random.Random(seed)
    F = DOOR_FRONT
    floor, top = -44, 74
    gap = 6.5  # half the gap between the leaves
    root = Frame(m, (0, 0, 0))
    # The frame: two towers on the rims and a lintel across them.
    for s in (-1, 1):
        m.block("Stone", s * 62, F - 7, 42, 36, 18, 84)
        m.block("StoneLight", s * 49, F + 2.6, top / 2, 10, 1.2, top + 2)
        m.block("StoneDark", s * 62, F - 7, 2.5, 40, 22, 5)
        m.block("StoneLight", s * 62, F - 7, 85, 39, 21, 2.5)
    m.block("Stone", 0, F - 7, top + 8, 88, 18, 16)
    m.block("StoneLight", 0, F + 2.6, top + 1.4, 88, 1.4, 3)
    m.loft_z("StoneDark", (top + 16, 0, F - 7, 120, 19), (top + 34, 0, F - 7, 30, 12))
    # A closed eye carved over the door, weeping.
    arc = [(-14 + 28 * t / 8, F + 2.3, top + 9.4 - 5.5 * math.sin(math.pi * t / 8)) for t in range(9)]
    limb(m, "Relief", arc, 1.3, 1.3)
    gem(m, "Relief", 0, F + 2.2, top + 1.0 + 3.0, 0.9, 1.8, 1.0, 6)
    # The leaves.
    for s, leaf_top in ((-1, top), (1, top)):
        x0, x1 = s * gap, s * 44
        m.block("Leaf", (x0 + x1) / 2, F - 2, (floor + leaf_top) / 2, abs(x1 - x0), 4, leaf_top - floor)
        m.block("LeafEdge", s * (gap + 0.7), F - 2, (floor + leaf_top) / 2, 1.8, 4.3, leaf_top - floor + 0.6)
        for z in (-30, 34, 54):  # iron bands, with rivets
            m.block("Band", (x0 + x1) / 2 + s * 0.8, F + 0.15, z, abs(x1 - x0) - 2.0, 0.5, 3.4)
            for i in range(8):
                ball(m, "Rivet", s * (gap + 2.6 + i * 5.1), F + 0.4, z, 0.5, 6, 3)
        # The great mourner on each leaf, kneeling towards the gap.
        shape = ((0.03, 0.0), (1.0, 0.0), (0.98, 0.2), (0.9, 0.4), (0.8, 0.5), (0.74, 0.62), (0.82, 0.76), (0.74, 0.9), (0.6, 1.0), (0.42, 0.98), (0.25, 0.8), (0.12, 0.55), (0.02, 0.25))
        pts = [(s * (42 - u * 32), floor + 1 + v * 72) for u, v in shape]
        if s > 0:
            pts = pts[::-1]
        outline(m, "Relief", root, pts, F, F + 1.1)
        inner = [(s * (42 - (0.2 + u * 0.55) * 32), floor + 40 + v * 28) for u, v in ((0.3, 0.1), (0.8, 0.26), (0.92, 0.7), (0.72, 0.92), (0.42, 0.8))]
        if s > 0:
            inner = inner[::-1]
        outline(m, "ReliefDark", root, inner, F + 1.0, F + 1.3)
        # Its hands over its face, and its tears running down the door.
        ex = s * 19
        hand(m, "Relief", (ex, F + 1.4, floor + 37), (-s * 0.05, 0, 1), (0, 1, 0), size=7, spread=0.42, curl=0.03, long=1.0, thumb=-s)
        m.block("Stream", ex, F + 1.2, floor + 19, 0.5, 0.1, 37)
        drops(m, "Tears", ex, F + 1.5, floor + 36, floor + 1, 6, 0.42)
    # The gap, and what's looking through it: a pale eye, its red iris sliding from side to side, under a heavy lid.
    m.block("Void", 0, F - 7.2, (floor + top) / 2, 2 * gap + 8, 1, top - floor)
    disc(m, "Sclera", 0, F - 6.6, 16, 13.5, 0.5, 18, "xz")
    disc(m, "Stare", 0, F - 6.1, 16, 6.4, 0.5, 16, "xz")
    m.block("EyeSlit", 0, F - 5.7, 15.6, 1.5, 0.3, 7.6)
    outline(m, "Void", root, [(-10, 34), (10, 34), (10, 18.6), (5, 21.8), (0, 23), (-5, 21.8), (-10, 18.6)], F - 5.4, F - 4.6)  # the upper lid
    outline(m, "Void", root, [(-10, 2), (10, 2), (10, 11), (5, 9), (0, 8.4), (-5, 9), (-10, 11)], F - 5.4, F - 4.6)  # the lower
    # The fingers round the edge of the right leaf, and lower down the left.

    def finger(role, side, z, reach, width):
        x = side * gap
        pts = [(x - side * 2.5, F - 6.5, z + 1.5), (x + side * 0.4, F + 0.9, z + 2.2), (x + side * reach * 0.5, F + 2.6, z), (x + side * reach * 0.82, F + 2.3, z - reach * 0.45),
               (x + side * reach, F + 1.3, z - reach * 0.85)]
        limb(m, role, pts, width, width * 0.4)
        ball(m, role, *pts[1], width * 0.66, 6, 4)
        ball(m, role, *pts[2], width * 0.6, 6, 4)

    for z, reach in ((52, 14), (44, 15.5), (36, 15), (28.5, 12.5)):
        finger("Fingers", 1, z, reach, 3.3)
    for z, reach in ((-5, 11), (-12, 12), (-19, 10.5)):
        finger("FingersB", -1, z, reach, 2.9)
    # The chains across it, snapped, and the broken lock.
    link_chain(m, "Chain", (-43, F + 1.5, 16), (-8, F + 1.5, 7), 14, 2.0)
    link_chain(m, "Chain", (43, F + 1.5, 11), (11, F + 1.5, 0), 13, 2.0)
    link_chain(m, "Chain", (-8, F + 1.5, 7), (-9, F + 1.5, -6), 6, 2.0)
    link_chain(m, "Chain", (11, F + 1.5, 0), (13, F + 1.5, -14), 6, 2.0)
    m.block("Lock", -9.3, F + 1.6, -10, 5, 1.6, 6)
    hoop_top = [(-11.2 + 3.8 * t / 6, F + 1.6, -7 + 3.6 * math.sin(math.pi * t / 6)) for t in range(7)]
    limb(m, "Lock", hoop_top, 0.8, 0.8)
    # Lamps hanging on the towers, the last light before the door.
    for s in (-1, 1):
        x = s * 49
        m.block("Cage", x, F + 5, 56, 0.5, 8, 0.5)
        m.block("Cage", x, F + 8.6, 53.8, 0.3, 0.3, 4)
        prism(m, "Cage", x, F + 8.6, 51.2, 52.0, 2.2, 0.4, 6)
        for k in range(4):
            a = k * math.tau / 4 + math.pi / 4
            beam(m, "Cage", (x + math.cos(a) * 1.6, F + 8.6 + math.sin(a) * 1.6, 51.2), (x + math.cos(a) * 1.6, F + 8.6 + math.sin(a) * 1.6, 47.6), 0.26)
        prism(m, "Cage", x, F + 8.6, 47.2, 47.6, 2, 2, 6)
        ball(m, "Lamp", x, F + 8.6, 49.4, 1.4, 6, 4)
    # The sea of candles: thickest at the door, thinning away from it.
    pool(m, "WaxDark", [(rng.uniform(-38, 38), F + rng.uniform(4, 38), rng.uniform(2, 5), rng.uniform(2, 4.5)) for _ in range(40)], floor + 0.1, 0.16)
    for k in range(270):
        along = rng.random() ** 1.6 * 44
        x = rng.uniform(-41, 41)
        if along < 3 and abs(x) < 4:
            continue
        candle(m, x, F + 3 + along, floor + 0.14, rng.uniform(0.6, 2.6), rng.uniform(0.24, 0.42), "FlameB" if k % 2 else "FlameA")
    m.block("Front", 0, F + 8, 0, 0.3, 0.3, 0.3)
    return m


ALL = [mourner, empty_swing, rocking_chair, waiting_window, headstones, black_willow, coffin, reaching_hands, lost_bear, dying_lamp, bearer, ash_tuft, candle_stubs,
       tear_pool, claw_tree, hollow_house, last_lighthouse, bell_tower, wailing_head, watcher, weeping_wall, long_arm, procession, last_door]

# What moves. Same numbers as shared/Config/PropMotion.luau.
_SOB = dict(bob=0.16, period=6.4)
_ROCK = dict(swing=8, period=3.4, axis="across", height=CHAIR_HEIGHT)
_SWING_A = dict(swing=20, period=3.8, axis="across", height=8.6)
_SWING_B = dict(swing=5, period=4.6, axis="across", height=8.6)
_LID = dict(swing=7, period=7, axis="across", height=LID_HINGE)
_BEAR = dict(swing=40, period=12)
_DRIFT = dict(bob=0.35, period=5)
_SWAY = dict(swing=3, period=6.5, axis="ahead", height=12)
_CANDLE = dict(pulse=0.6, period=0.9)
_CANDLE_B = dict(pulse=0.55, period=1.3)
_HEAD = dict(swing=11, period=19)
_BELL = dict(swing=15, period=6.5, axis="across", height=BELL_HOOK)
_SOUL = dict(fall=-2.0, period=3.2)
MOTION = {
    "prop_Mourner": {"Mantle": dict(_SOB), "Hood": dict(_SOB), "HoodDark": dict(_SOB), "Palms": dict(_SOB), "Stare": dict(_SOB, pulse=0.02),
                     "Tears": dict(fall=1.5, period=1.1), "Ripple": dict(pulse=0.3, period=1.1)},
    "prop_EmptySwing": {"ChainA": dict(_SWING_A), "SeatA": dict(_SWING_A), "ChainB": dict(_SWING_B), "SeatB": dict(_SWING_B)},
    "prop_RockingChair": {"Chair": dict(_ROCK), "Shawl": dict(_ROCK), "Flame": dict(_CANDLE)},
    "prop_WaitingWindow": {"Door": dict(swing=17, period=5.6), "Trim": dict(), "Window": dict(pulse=0.7, period=1.7), "Flame": dict(_CANDLE)},
    "prop_Headstones": {"Soul": dict(_SOUL), "Flame": dict(_CANDLE)},
    "prop_BlackWillow": {"Strands": dict(_SWAY), "StrandsDark": dict(_SWAY), "Tears": dict(fall=2.2, period=1.5)},
    "prop_Coffin": {"Lid": dict(_LID), "LidHand": dict(_LID), "Stare": dict(pulse=0.05, period=7), "Flame": dict(_CANDLE)},
    "prop_ReachingHands": {"HandA": dict(bob=0.9, period=5.2), "HandB": dict(bob=0.7, period=6.9)},
    "prop_LostBear": {"BearHead": dict(_BEAR), "BearSnout": dict(_BEAR), "BearEar": dict(_BEAR), "BearEye": dict(_BEAR), "Stare": dict(_BEAR, pulse=0.2)},
    "prop_DyingLamp": {"Lamp": dict(pulse=0.12, period=1.7), "LampA": dict(pulse=0.04, period=0.53), "Motes": dict(spin=46, bob=0.3, period=2.4)},
    "prop_Bearer": {**{role: dict(_DRIFT) for role in ("Robe", "Hood", "HoodDark", "Sleeve", "Palms", "Pole")}, "Stare": dict(_DRIFT, pulse=0.1),
                    "Cage": dict(_DRIFT, swing=8, axis="across", height=12.2), "Lamp": dict(_DRIFT, swing=8, axis="across", height=12.2, pulse=0.6)},
    "prop_AshTuft": {"Reeds": dict(swing=4, period=3.6, axis="ahead"), "ReedsDark": dict(swing=5, period=4.4, axis="ahead")},
    "prop_CandleStubs": {"FlameA": dict(_CANDLE), "FlameB": dict(_CANDLE_B)},
    "prop_TearPool": {"Ripple": dict(pulse=0.15, period=3.6), "RippleB": dict(pulse=0.15, period=4.8), "Stare": dict(pulse=0.03, period=9), "Stream": dict(pulse=0.5, period=4)},
    "prop_ClawTree": {"Claws": dict(swing=2.5, period=7, axis="ahead", height=5)},
    "prop_HollowHouse": {"Shade": dict(bob=1.9, period=11), "Window": dict(pulse=0.7, period=1.9), "Shutter": dict(swing=22, period=4.2, about="self")},
    "prop_LastLighthouse": {"Sweep": dict(spin=14), "Beacon": dict(pulse=0.75, period=3.4), "Window": dict(pulse=0.6, period=2.6)},
    "prop_BellTower": {"Bell": dict(_BELL), "BellRim": dict(_BELL), "Clapper": dict(swing=23, period=6.5, axis="across", height=BELL_HOOK)},
    "prop_WailingHead": {"Eyelid": dict(bob=1.1, period=10), "Tears": dict(fall=3.0, period=2.0), "Stream": dict(pulse=0.6, period=2.8), "Stare": dict(pulse=0.5, period=10)},
    "prop_Watcher": {"Hood": dict(_HEAD), "HoodDark": dict(_HEAD), "Stare": dict(_HEAD, pulse=0.12), "Tears": dict(fall=20, period=3.8), "Fingers": dict(bob=0.5, period=8)},
    "prop_WeepingWall": {"Tears": dict(fall=4, period=1.5), "Stream": dict(pulse=0.55, period=3.4), "Stare": dict(pulse=0.1, period=6), "Palms": dict(bob=0.25, period=4.4)},
    "prop_LongArm": {"Fingers": dict(bob=0.5, period=5.2), "Rags": dict(swing=3, period=5.8, axis="ahead", height=30)},
    "prop_Procession": {"*": dict(drift=320, period=84, fade=0.12, head="Leader"), },
    "prop_LastDoor": {"Stare": dict(swing=15, period=9), "EyeSlit": dict(swing=15, period=9), "Fingers": dict(bob=0.8, period=6), "FingersB": dict(bob=0.6, period=7.6),
                      "Tears": dict(fall=6, period=2.4), "Stream": dict(pulse=0.55, period=3.6), "FlameA": dict(_CANDLE), "FlameB": dict(_CANDLE_B), "Lamp": dict(pulse=0.7, period=2.1)},
}
del MOTION["prop_WaitingWindow"]["Trim"]

# Real light (Config/Decor propLights). Neon lights nothing round it, and this map has no other light, so what's lit
# here comes from these. Each prop: the role it shines from, colour, range and brightness at size 1. The light dims with
# the role's pulse.
LIGHTS = {
    "prop_Mourner": ("Ripple", TEAR, 12, 0.6),
    "prop_RockingChair": ("Flame", FLAME, 20, 1.1),
    "prop_WaitingWindow": ("Window", WINDOW, 22, 1.1),
    "prop_Headstones": ("Flame", FLAME, 18, 1),
    "prop_Coffin": ("Flame", FLAME, 18, 1),
    "prop_DyingLamp": ("Lamp", LAMP, 32, 1.5),
    "prop_Bearer": ("Lamp", LAMP, 22, 1.1),
    "prop_CandleStubs": ("FlameA", FLAME, 14, 0.9),
    "prop_HollowHouse": ("Window", WINDOW, 18, 0.9),
    "prop_LastLighthouse": ("Beacon", TEAR, 40, 1.1),
    "prop_LastDoor": ("Stare", RED, 60, 2.4),
}

# Where the props go: the same rules as Config/Decor's WeepingDark (keep the two in step). The map is 1800 long. It's
# sparser than any other map on purpose: emptiness is the point. The Last Door stands past the end of the map, in the
# 36 studs of corridor beyond it, just in front of the end wall. Its origin is DOOR_FRONT behind its face.
DECOR = dict(
    floor=dict(first=10, gap=(13, 22), side=(23, 34),
               props=[("prop_Mourner", 14, (1.4, 1.8)), ("prop_BlackWillow", 9, (1.2, 1.5)), ("prop_DyingLamp", 9, (1.3, 1.5)), ("prop_Headstones", 9, (1.2, 1.5)),
                      ("prop_EmptySwing", 7, (1.3, 1.5)), ("prop_RockingChair", 6, (1.3, 1.6)), ("prop_WaitingWindow", 6, (1.2, 1.5)), ("prop_Bearer", 7, (1.1, 1.4)),
                      ("prop_Coffin", 6, (1.2, 1.5)), ("prop_ReachingHands", 7, (1.2, 1.6)), ("prop_LostBear", 3, (1.3, 1.6))],
               extras=dict(chance=0.7, spread=8, props=[("prop_AshTuft", 5, (0.9, 1.3)), ("prop_CandleStubs", 4, (0.9, 1.3)), ("prop_ReachingHands", 1, (0.5, 0.7))])),
    rim=dict(first=6, gap=(11, 18), chance=0.9, side=(60, 104),
             props=[("prop_ClawTree", 6, (2.0, 2.6)), ("prop_BlackWillow", 5, (1.8, 2.3)), ("prop_HollowHouse", 3, (1.3, 1.7)), ("prop_Mourner", 3, (2.2, 2.8)),
                    ("prop_Headstones", 3, (1.8, 2.3)), ("prop_DyingLamp", 2, (1.8, 2.2)), ("prop_AshTuft", 2, (2.2, 2.8))]),
    overhead=[("prop_LongArm", 300, 0, 1), ("prop_LongArm", 900, 180, 1.05), ("prop_LongArm", 1500, 0, 1)],
    walls=[("prop_WeepingWall", d, side) for d, side in ((90, 1), (280, -1), (470, 1), (660, -1), (850, 1), (1040, -1), (1230, 1), (1420, -1), (1610, 1))],
    spots=[("prop_WailingHead", 110, -84, "rim", 0, 1.4, "middle"), ("prop_WailingHead", 720, 84, "rim", 0, 1.5, "middle"), ("prop_WailingHead", 1330, -84, "rim", 0, 1.4, "middle"),
           ("prop_LastLighthouse", 240, 86, "rim", 0, 1.5, "middle"), ("prop_LastLighthouse", 980, -86, "rim", 0, 1.6, "middle"), ("prop_LastLighthouse", 1640, 86, "rim", 0, 1.5, "middle"),
           ("prop_BellTower", 420, -84, "rim", 0, 1.4, "middle"), ("prop_BellTower", 1140, 84, "rim", 0, 1.5, "middle"),
           ("prop_Watcher", 170, 266, "rim", 0, 3, "middle"), ("prop_Watcher", 520, -266, "rim", 0, 3, "middle"), ("prop_Watcher", 870, 266, "rim", 0, 3, "middle"),
           ("prop_Watcher", 1220, -266, "rim", 0, 3, "middle"), ("prop_Watcher", 1570, 266, "rim", 0, 3, "middle"),
           ("prop_Procession", 330, 52, "rim", 0, 1.2, "along"), ("prop_Procession", 1050, -52, "rim", 0, 1.2, "along"),
           ("prop_LastDoor", DOOR_AT + DOOR_FRONT, 0, "rim", 180, 1, "along")]
          + [("prop_TearPool", d, x, "floor", yaw, 1.3, "along") for d, x, yaw in ((45, -3, 10), (170, 4, 350), (295, -4, 20), (420, 3, 340), (545, -2, 5), (670, 4, 15), (795, -3, 345),
                                                                         (920, 2, 10), (1045, -4, 355), (1170, 3, 25), (1295, -2, 335), (1420, 4, 0), (1545, -3, 20), (1670, 2, 350))],
)


# ---------------------------------------------------------------------- light

SHEER = {"Sweep": 0.72}  # shared/Roles.luau sheer
HAZE_DENSITY = 0.0035


def set_light(scene, sun_energy, ambient):
    sun = bpy.data.objects["Sun"]
    sun.data.energy = sun_energy
    sun.data.color = (0.82, 0.86, 1.0)
    sun.rotation_euler = (math.radians(-62), math.radians(25), math.radians(30))
    node = scene.world.node_tree.nodes["Background"]
    node.inputs["Color"].default_value = (0.72, 0.74, 0.82, 1)
    node.inputs["Strength"].default_value = ambient


def show_light(scene):
    """Enough light to read a model by, for the stills of each prop."""
    set_light(scene, 1.3, 0.62)


def game_light(scene):
    """As near as Blender gets to the game's Config/Lighting look for this world: almost none."""
    set_light(scene, 0.16, 0.13)


def sheer(roots, on=True):
    """The game makes these roles see-through (Roles.sheer). Off again before saving, so the export stays plain."""
    for root in roots:
        for child in root.children:
            if child.type == "MESH" and mk.role_of(child) in SHEER:
                for mat in child.data.materials:
                    mat.node_tree.nodes.get("Principled BSDF").inputs["Alpha"].default_value = 1 - SHEER[mk.role_of(child)] if on else 1
                    mat.surface_render_method = "BLENDED" if on else "DITHERED"


def haze(scene, on=True):
    """A dark fog over the corridor renders, for the game's atmosphere. The prop lights stay out of it, as they do in
    the game: only the distance fades, nothing glows in the fog."""
    nodes, links = scene.world.node_tree.nodes, scene.world.node_tree.links
    out = nodes["World Output"].inputs["Volume"]
    if not on:
        for link in list(out.links):
            links.remove(link)
        return
    volume = nodes.new("ShaderNodeVolumePrincipled")
    volume.inputs["Color"].default_value = (0, 0, 0, 1)
    volume.inputs["Density"].default_value = HAZE_DENSITY
    volume.inputs["Emission Strength"].default_value = HAZE_DENSITY * 0.022  # what things fade towards with distance
    volume.inputs["Emission Color"].default_value = (0.82, 0.84, 1.0, 1)
    links.new(volume.outputs[0], out)
    scene.eevee.volumetric_end = 1400
    scene.eevee.volumetric_tile_size = "8"


def real_lights(stage, copies):
    """The game's propLights as Blender lights, so the corridor renders show the pools of light."""
    bpy.context.view_layer.update()
    made = []
    for root in copies:
        spec = LIGHTS.get(mk.prop_of(root))
        if not spec:
            continue
        role, colour, reach, brightness = spec
        for child in root.children:
            if child.type == "MESH" and mk.role_of(child) == role:
                data = bpy.data.lights.new("PropLight", "POINT")
                data.energy = brightness * reach * reach * 2.2
                data.color = kit.srgb_to_linear(colour)
                data.shadow_soft_size = 0.5
                data.use_shadow = False
                data.volume_factor = 0
                light = bpy.data.objects.new("PropLight", data)
                light.location = root.matrix_world @ mk.mesh_centre(child)
                stage.objects.link(light)
                made.append(light)
    return made


# ---------------------------------------------------------------------- scene and renders

BIG = {"prop_LastLighthouse": (-110, -150, 0), "prop_BellTower": (-68, -130, 0), "prop_WailingHead": (-22, -140, 0), "prop_HollowHouse": (16, -122, 0), "prop_ClawTree": (36, -118, 0),
       "prop_Watcher": (90, -520, 0), "prop_WeepingWall": (140, -110, 44), "prop_LongArm": (240, -170, 0), "prop_Procession": (-180, -150, 0), "prop_LastDoor": (420, -500, 44)}


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
            x += 15
        built[model.name] = root
        roots.append(root)
    row_middle = (40 + x - 15) / 2
    mk.light_up(roots, GLOW_ROLES)
    sheer(roots)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-500, -800, -0.01), (800, -800, -0.01), (800, 200, -0.01), (-500, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", CORRIDOR["FloorA"], False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = mk.player_block(stage)
    bpy.context.view_layer.update()
    mk.set_sky(scene, SKY)
    show_light(scene)

    everything = roots + [player]
    if stills:
        for model, root in zip(models, roots):
            name = model.name
            if only and name not in only:
                continue
            low, high = kit.bounds(root)
            if name == "prop_LastLighthouse":
                c = Vector(root.location) + Vector((0, 0, 16))
                mk.set_visible(everything, [root])
                kit.shoot(scene, name, c + Vector((26, 62, 16)), c, (800, 900), 40)
            elif name == "prop_LongArm":
                mk.shoot_prop(scene, name, root, player, everything, (0.1, 1.0, 0.22), 0.9, (1400, 700), 32)
            elif name == "prop_WeepingWall":
                mk.shoot_prop(scene, name, root, player, everything, (0.3, 1.0, 0.0), 1.0, (800, 900), 40)
            elif name == "prop_Watcher":
                mk.set_visible(everything, [root])
                c = Vector(root.location) + Vector((0, 20, 40))
                kit.shoot(scene, name, c + Vector((130, 240, -10)), c, (900, 1000), 40)
            elif name == "prop_LastDoor":
                mk.set_visible(everything, [root])
                c = Vector(root.location) + Vector((0, 40, 10))
                kit.shoot(scene, name, c + Vector((30, 230, 26)), c + Vector((0, 0, 14)), (1300, 1000), 34)
            elif name == "prop_Procession":
                mk.shoot_prop(scene, name, root, player, everything, (1.0, 0.25, 0.3), 0.95, (1300, 600), 32)
            elif name == "prop_WailingHead":
                mk.shoot_prop(scene, name, root, player, everything, (0.28, 1.0, 0.12), 1.15, (800, 800), 50)
            elif name in ("prop_BellTower", "prop_HollowHouse"):
                mk.shoot_prop(scene, name, root, player, everything, (0.5, 0.95, 0.3), 1.1, (800, 800), 50)
            elif name == "prop_TearPool":
                mk.shoot_prop(scene, name, root, player, everything, (0.05, 0.25, 1.0), 1.1, (700, 700), 50)
            else:
                mk.shoot_prop(scene, name, root, player, everything)
        if not only:
            player.location = (30, -40, 0)
            bpy.context.view_layer.update()
            small = [r for r in roots if mk.prop_of(r) not in BIG]
            mk.set_visible(everything, small + [player])
            kit.shoot(scene, "props", (row_middle, 50, 34), (row_middle, -40, 5), (2000, 700), 18)
            landmarks = [built[n] for n in ("prop_BellTower", "prop_WailingHead", "prop_HollowHouse", "prop_ClawTree", "prop_LastLighthouse")]
            mk.set_visible(everything, landmarks + [player])
            player.location = (-30, -96, 0)
            bpy.context.view_layer.update()
            kit.shoot(scene, "landmarks", (-45, -8, 44), (-45, -130, 18), (1800, 800), 20)

    if videos:  # close up on what moves
        names = ("prop_Mourner", "prop_EmptySwing", "prop_RockingChair", "prop_WaitingWindow", "prop_Coffin", "prop_ReachingHands", "prop_LostBear", "prop_Bearer", "prop_BellTower",
                 "prop_HollowHouse", "prop_WailingHead", "prop_LastLighthouse")
        movers = [built[n] for n in names]
        mk.set_visible(everything, movers)
        saved = [(r, r.location.copy()) for r in movers]
        for k, root in enumerate(movers[:8]):
            root.location = (k * 14 - 49, 0, 0)
        for k, root in enumerate(movers[8:]):
            root.location = ((k - 1.5) * 40, -60, 0)
        bpy.context.view_layer.update()
        entries = mk.motion_entries(movers, MOTION)
        mk.render_video(scene, RENDERS, "weeping_motion", 150, 15, lambda f: ((0, 70, 34), (0, -22, 12), 26, lambda t: mk.apply_motion(entries, t)), (1600, 800))
        mk.reset_motion(entries)
        for root, loc in saved:
            root.location = loc

    if only:
        return
    ground.hide_render = True
    mk.set_visible(everything, [])
    corridor = mk.corridor_stage(stage, CORRIDOR, length=600)
    copies = mk.decorate_stage(stage, built, DECOR, length=600)
    lights = real_lights(stage, copies)
    game_light(scene)
    haze(scene)
    if stills:
        kit.shoot(scene, "corridor_flight", (0, 30, 30), (0, -160, 16), (1600, 900), 22)
        kit.shoot(scene, "corridor_high", (0, 40, 80), (0, -170, 30), (1600, 900), 22)
        kit.shoot(scene, "corridor_floor", (-16, -50, 10), (8, -170, 12), (1600, 900), 22)
        kit.shoot(scene, "corridor_rim", (-40, 20, 90), (50, -160, 54), (1600, 900), 24)
        kit.shoot(scene, "watcher_over_the_wall", (-30, -60, 12), (120, -170, 150), (1600, 900), 20)
        show_light(scene)
        kit.shoot(scene, "corridor_flight_lit", (0, 30, 30), (0, -160, 16), (1600, 900), 22)
        game_light(scene)
    if videos:  # down the corridor at the flight camera's height (14 over an egg that flies up to 18 high)
        entries = mk.motion_entries(copies, MOTION)
        frames = 165

        def fly(f):
            t = f / (frames - 1)
            y = 30 - 400 * t
            return (0, y, 28 + 4 * math.sin(t * math.pi)), (0, y - 70, 17), 22, lambda s: mk.apply_motion(entries, s)

        mk.render_video(scene, RENDERS, "weeping_flight", frames, 15, fly, (1600, 900))
        mk.reset_motion(entries)

    # The end of the world: the Last Door at the end of a stretch of corridor.
    mk.clear(copies)
    for light in lights:
        bpy.data.lights.remove(light.data)
    door = mk.place_copy(built["prop_LastDoor"], stage, (0, -(520 + DOOR_FRONT), mk.WALL), 0, 1)
    for child in door.children:
        if mk.role_of(child) == "Front":
            child.hide_render = True
    door_lights = real_lights(stage, [door])
    extra = mk.decorate_stage(stage, built, {"walls": [("prop_WeepingWall", 330, 1), ("prop_WeepingWall", 400, -1)],
                                              "spots": [("prop_Watcher", 440, 266, "rim", 0, 3, "middle"), ("prop_Watcher", 460, -266, "rim", 0, 3, "middle")]}, length=600)
    if stills:
        kit.shoot(scene, "end_of_the_world", (0, -310, 24), (0, -520, 46), (1600, 900), 24)
        kit.shoot(scene, "end_of_the_world_close", (-18, -448, 10), (2, -520, 26), (1600, 900), 24)
    mk.clear([door, corridor] + extra)
    for light in door_lights:
        bpy.data.lights.remove(light.data)
    mk.light_up(roots, GLOW_ROLES, 0)
    sheer(roots, False)
    haze(scene, False)
    ground.hide_render = False
    for root in roots:
        for child in root.children:
            child.hide_render = False
    player.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "weeping_dark_models.blend"))
    print("saved", HERE / "weeping_dark_models.blend")
    for model in models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    # After "--": "stills" renders only the stills, "videos" only the videos; nothing, both. "only prop_A prop_B" is
    # just those props' stills, without saving (quick while modelling).
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "only" in args:
        main(stills=True, videos=False, only=set(args[args.index("only") + 1:]))
    else:
        main(stills=not args or "stills" in args, videos=not args or "videos" in args)
