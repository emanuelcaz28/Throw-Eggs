"""Builds Forbidden Library's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_forbidden_library.py              (stills and videos)
    Blender -b -P build_forbidden_library.py -- stills    (stills only, quicker while modelling)

Saves forbidden_library_models.blend and renders to design/world/models_forbidden_library/: one still per prop,
the props together, a stretch of corridor, and two videos of what moves (library_motion.mp4 close up,
library_flight.mp4 down the corridor at the flight camera's height).

Forbidden Library, map 10, the second of the mysterious, dark maps: a library so old it became a world of its
own, locked up for ever because its books are alive. Night, a dusty indigo haze, and two lights of its own: warm
candlelight and the violet glow of living ink. A deep violet carpet on the floor, dark walnut walls like
bookcases, and parchment on the rims, hanging over the walls like loose pages. Cold violet and parchment after
Eclipse Temple's red and jade, and nothing like Midnight Carnival's teal and crimson. Its signature is the open
tome on its lectern, a page turning back and forth by itself, writing glowing on its pages and letters of light
rising out of it under a floating sigil. Around it: towers of books with a candle on top, bookcases with eyes
peering out from between the books, candelabras, candles floating in the air, an inkwell whose quill nods as if
it writes, an hourglass of glowing sand, and now and then a mimic book chomping its pages. On the rims: trees
that grew pages instead of leaves with glowing moths circling them, stacked bookcases dropping pages for ever,
forbidden tomes chained to their pedestals and rattling; landmarks: clock towers whose minute hand runs
backwards over a swinging pendulum, giant pop-up books with a paper castle and a paper moon on a stick, spiral
stairs climbing to a glowing door to nowhere with books circling them, and huge books flapping like birds in the
sky. Ink pours down the walls from giant tipped inkwells, book arches span the corridor with a chandelier
swinging under them, and spell pages lie flat across the floor.

No stud texture in this file: kit.PREVIEW_STUDS is off, so every material is a plain colour and the renders show
the models as they leave Blender. The studs come only in Studio, from the shared "Studs" MaterialVariant that
studio_tidy puts on every part except the glowing ones (docs/MAP_RECIPE.md step 8). The meshes still get the
usual box-projected UVs.

What moves is MOTION below, the same numbers as shared/Config/PropMotion.luau (keep the two in step).
Glowing roles (GLOW_ROLES) must also be in shared/Roles.luau, which makes them Neon in the game.
Props that must face a certain way carry a small Front part on their +Y side; MapDecor turns them, then removes it.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import map_kit as mk  # noqa: E402
from map_kit import ball, beam, disc, flat_ring, gem, hoop, kit, limb, plate, prism, puddle  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "models_forbidden_library"

# Roles lit from inside. The game makes them Neon (shared/Roles.luau), so add new ones there too.
GLOW_ROLES = {"InkGlow", "Spell", "Letters", "FlipGlow", "Flame", "FlameCore", "FlameA", "FlameB", "TimeSand", "Grain", "Peeper",
              "Gaze", "Moths", "Lamp", "TomeGlow", "ClockGlow", "Window", "Orb", "Crescent", "DoorGlow", "InkL", "InkR", "SpellRing",
              "Stream", "Falling"}
kit.NO_STUDS.update(GLOW_ROLES)
mk.GLOW_STRENGTH = 1.8

# Shared colours, so every prop's wood, books and light match.
WOOD, WOOD_DARK, WOOD_LIGHT, WOOD_DEEP = "#7a4e34", "#523224", "#9a6842", "#2f1d16"
COVER_A, COVER_B, COVER_C, COVER_D, COVER_E = "#9a2f3c", "#2f7a5e", "#3a4c8f", "#c4922f", "#7a3f86"
PAGE, PAGE_DARK = "#efe2bd", "#b89a68"
GILT, BRASS, BRASS_DARK = "#f2c24e", "#cf9a42", "#8d6427"
IRON, IRON_LIGHT = "#37323f", "#5a5366"
STONE, STONE_DARK, STONE_LIGHT = "#8a83a0", "#625b78", "#aea7c2"
LEATHER, LEATHER_DARK = "#6b2236", "#4a1726"
WAX, WAX_WARM = "#f4ecd4", "#f0dcb4"
FLAME, FLAME_CORE = "#ffb347", "#fff3c4"
INK, INK_DARK = "#8a5cff", "#251a42"
SPELL = "#cdb6ff"
BOTTLE, BOTTLE_LIGHT = "#33295e", "#5a4c99"
RIBBON = "#c42a45"
SHADOW = "#1b1426"
WINDOW = "#ffc46b"

# The corridor's Forbidden Library colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#483874", "FloorB": "#40316a", "Dirt": "#56392a", "DirtB": "#4c3225", "Grass": "#d5c193"}
SKY = "#17142b"

# What moves. The game reads the same numbers from shared/Config/PropMotion.luau. Kinds of move:
#   spin  degrees a second; swing  degrees each way, over period seconds; bob  studs up and down over period;
#   pulse  the glow dims to this share and back over period; fall  drops this far over period, then starts again
#   (negative rises).
# spin and swing turn round axis "up" (default), "across" (the model's X) or "ahead" (its Y), through the part's
# own middle (about="self") or a point `height` studs straight above the prop's origin (the default).
_FLICKER = {"Flame": dict(pulse=0.55, period=0.8, bob=0.06), "FlameCore": dict(pulse=0.6, period=0.5)}
_MIMIC = dict(swing=14, period=1.5, axis="across", height=1.6)
_QUILL = dict(swing=9, period=2.2, axis="across", height=4.65)
_TOME = dict(swing=4, period=0.5, axis="ahead", height=4.25)
_CHANDELIER = dict(swing=7, period=3.6, axis="across", height=34.5)
_FLAP = dict(period=3, axis="ahead", height=46, bob=1.2)
MOTION = {
    "prop_OpenTome": {"FlipPage": dict(swing=75, period=3.2, axis="ahead", height=6.24),
                      "FlipGlow": dict(swing=75, period=3.2, axis="ahead", height=6.24),
                      "Spell": dict(spin=30, about="self", bob=0.3, period=3),
                      "Letters": dict(fall=-1.5, period=1.6),
                      "InkGlow": dict(pulse=0.5, period=3.5)},
    "prop_BookStack": dict(_FLICKER),
    "prop_Bookcase": {**_FLICKER, "Peeper": dict(pulse=0.1, period=4.5)},
    "prop_Candelabra": dict(_FLICKER),
    "prop_FloatingCandles": {"CandleA": dict(bob=0.5, period=3.4), "FlameA": dict(bob=0.5, period=3.4, pulse=0.6),
                             "CandleB": dict(bob=0.7, period=4.4), "FlameB": dict(bob=0.7, period=4.4, pulse=0.6)},
    "prop_InkWell": {"Quill": dict(_QUILL), "QuillBarb": dict(_QUILL), "QuillBand": dict(_QUILL),
                     "InkGlow": dict(pulse=0.5, period=3)},
    "prop_Hourglass": {"Grain": dict(fall=0.45, period=0.3), "TimeSand": dict(pulse=0.7, period=4)},
    "prop_MimicBook": {"MimicLid": dict(_MIMIC), "MimicPages": dict(_MIMIC), "Fangs": dict(_MIMIC), "MimicBrow": dict(_MIMIC),
                       "Pupil": dict(_MIMIC), "Gaze": dict(_MIMIC, pulse=0.5), "InkGlow": dict(pulse=0.4, period=1.5)},
    "prop_ScrollPile": dict(_FLICKER),
    "prop_SpellPage": {"SpellRing": dict(spin=-10), "InkGlow": dict(pulse=0.4, period=3.2)},
    "prop_PageTree": {"Moths": dict(spin=22, bob=0.5, period=3)},
    "prop_LeaningShelves": {"Flutter": dict(fall=3, period=2.6), "Lamp": dict(pulse=0.7, period=2.4)},
    "prop_ChainedTome": {"Tome": dict(_TOME), "TomePage": dict(_TOME), "TomeGilt": dict(_TOME), "Lock": dict(_TOME),
                         "TomeGlow": dict(_TOME, pulse=0.3), "InkGlow": dict(pulse=0.5, period=3)},
    "prop_ClockTower": {"MinuteHand": dict(spin=-36, axis="ahead", height=18.8), "HourHand": dict(spin=3, axis="ahead", height=18.8),
                        "Pendulum": dict(swing=16, period=2, axis="ahead", height=16.1), "ClockGlow": dict(pulse=0.75, period=4),
                        "Orb": dict(pulse=0.5, period=3), "InkGlow": dict(pulse=0.5, period=3.6)},
    "prop_PopupBook": {"MoonStick": dict(swing=12, period=3.2, axis="ahead", height=1.8),
                       "Crescent": dict(swing=12, period=3.2, axis="ahead", height=1.8),
                       "Bats": dict(spin=18, bob=0.6, period=3.6), "Window": dict(pulse=0.6, period=2.8)},
    "prop_SpiralStair": {"OrbitA": dict(spin=12, bob=0.8, period=5), "OrbitB": dict(spin=12, bob=0.8, period=5),
                         "OrbitPage": dict(spin=12, bob=0.8, period=5), "DoorGlow": dict(pulse=0.5, period=3),
                         "InkGlow": dict(pulse=0.4, period=4)},
    "prop_SkyTome": {"CoverL": dict(_FLAP, swing=14), "PageL": dict(_FLAP, swing=14), "InkL": dict(_FLAP, swing=14),
                     "CoverR": dict(_FLAP, swing=-14), "PageR": dict(_FLAP, swing=-14), "InkR": dict(_FLAP, swing=-14),
                     "SkySpine": dict(bob=1.2, period=3), "Headband": dict(bob=1.2, period=3), "Ribbon": dict(bob=1.2, period=3)},
    "prop_InkFall": {"Falling": dict(fall=4, period=0.8), "InkGlow": dict(pulse=0.5, period=3)},
    "prop_BookArch": {"Chain": dict(_CHANDELIER), "Chandelier": dict(_CHANDELIER), "Taper": dict(_CHANDELIER),
                      "Flame": dict(_CHANDELIER, pulse=0.6)},
}


def prop(name, **colours):
    return mk.prop(name, **colours)


# ---------------------------------------------------------------------- shape helpers


def turn(x=0.0, y=0.0, z=0.0):
    """A rotation (radians round X, then Y, then Z) as a 3x3 matrix."""
    return Euler((x, y, z), "XYZ").to_matrix()


def obox(m, role, centre, size, rot=None):
    """A box of size (w, d, h) round centre, turned by rot (a 3x3 matrix)."""
    rot = rot if rot is not None else Matrix.Identity(3)
    c = Vector(centre)
    w, d, h = size
    verts = [tuple(c + rot @ Vector((sx * w / 2, sy * d / 2, sz * h / 2)))
             for sy in (-1, 1) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    m._add(role, verts, [[0, 1, 2, 3], [7, 6, 5, 4]] + [[i, i + 4, (i + 1) % 4 + 4, (i + 1) % 4] for i in range(4)])


class Frame:
    """A turned frame to build in: at() is a point of the frame in the model, box() a box turned with it."""

    def __init__(self, m, origin, rot=None):
        self.m, self.o = m, Vector(origin)
        self.r = rot if rot is not None else Matrix.Identity(3)

    def at(self, x, y, z):
        return tuple(self.o + self.r @ Vector((x, y, z)))

    def box(self, role, x, y, z, w, d, h, extra=None):
        obox(self.m, role, self.at(x, y, z), (w, d, h), self.r @ extra if extra is not None else self.r)

    def beam(self, role, a, b, width, height=None, end_width=None):
        beam(self.m, role, self.at(*a), self.at(*b), width, height, end_width)


def tube(m, role, a, b, r0, r1=None, sides=8):
    """A round rod from a to b, radius r0 to r1: scrolls, a bottle on its side, a cork. Flat side down."""
    r1 = r0 if r1 is None else r1
    a, b = Vector(a), Vector(b)
    along = (b - a).normalized()
    side = along.cross(Vector((0, 0, 1)))
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    up = side.cross(along)
    verts = []
    for p, r in ((a, r0), (b, r1)):
        for i in range(sides):
            t = math.pi / sides + i * math.tau / sides
            verts.append(tuple(p + (side * math.cos(t) + up * math.sin(t)) * r))
    faces = [list(range(sides))[::-1], list(range(sides, 2 * sides))]
    faces += [[i, (i + 1) % sides, sides + (i + 1) % sides, sides + i] for i in range(sides)]
    m._add(role, verts, faces)


def book(m, cover, centre, size, rot=None, page="Page", band=None):
    """A closed book. size is (thick, wide, tall) in its own frame: the boards are its -X and +X sides, the spine
    its -Y side, and the pages show at +Y, +Z and -Z, set in from the boards. rot turns it: standing on a shelf
    with its spine out, turn(z=pi); lying flat, see flat_book. band adds two gilt bands round the spine."""
    f = Frame(m, centre, rot)
    t, w, h = size
    board = max(0.08, min(0.3, t * 0.15))
    inset = min(0.16, h * 0.06 + 0.04)
    for s in (-1, 1):
        f.box(cover, s * (t / 2 - board / 2), 0, 0, board, w, h)
    f.box(cover, 0, -w / 2 + board / 2 - 0.02, 0, t + 0.06, board + 0.04, h + 0.06)
    y0, y1 = -w / 2 + board - 0.04, w / 2 - inset
    f.box(page, 0, (y0 + y1) / 2, 0, t - 2 * board + 0.02, y1 - y0, h - 2 * inset)
    if band:
        for z in (-h * 0.3, h * 0.3):
            f.box(band, 0, -w / 2 - 0.05, z, t + 0.1, 0.08, max(0.1, h * 0.05))


def flat_book(m, cover, x, y, z, length, depth, thick, yaw=0.0, page="Page", band=None):
    """A closed book lying flat on z, `length` along X and `depth` along Y before the yaw, its spine to -Y."""
    book(m, cover, (x, y, z + thick / 2), (thick, depth, length), turn(y=math.pi / 2, z=yaw), page, band)


def open_book(m, cover, centre, half, depth, pages, rot=None, rise=0.08, board=0.25, page="Page"):
    """An open book on its back, its spine along Y through centre: a flat cover, and a block of pages each side
    rising `rise` radians towards its outer edge. Returns the two halves' frames (left, right), whose origin is the
    cover's top at the spine, and the height of the page tops in them."""
    base = rot if rot is not None else Matrix.Identity(3)
    Frame(m, centre, base).box(cover, 0, 0, board / 2, half * 2, depth, board)
    halves = []
    sink = half * math.sin(rise) + 0.05  # the pages reach down into the cover all the way along
    for s in (-1, 1):
        f = Frame(m, Vector(centre) + base @ Vector((0, 0, board)), base @ turn(y=-s * rise))
        f.box(page, s * (half - 0.2) / 2, 0, (pages - sink) / 2, half - 0.2, depth - 0.45, pages + sink)
        halves.append(f)
    return halves, pages


def ink_lines(f, role, x0, x1, y0, y1, z, rng, rows=6, thick=0.07, height=0.16):
    """Rows of glowing writing on a page of frame f: words along X from x0 towards x1, rows from y0 to y1, at z."""
    step = 1 if x1 > x0 else -1
    for k in range(rows):
        y = y0 + (y1 - y0) * (k + 0.5) / rows
        x = x0 + step * rng.uniform(0, 0.4)
        while True:
            word = rng.uniform(0.3, 0.9)
            end = x + step * word
            if (end - x1) * step > 0:
                break
            f.box(role, (x + end) / 2, y, z + thick / 2 - 0.02, word, height, thick)
            x = end + step * rng.uniform(0.15, 0.3)


def frame_ring(f, role, cx, cy, z, r, width, thick, n=16):
    """A flat ring lying in frame f."""
    for i in range(n):
        a = (i + 0.5) * math.tau / n
        seg = 2 * r * math.sin(math.pi / n) + width * 0.4
        f.box(role, cx + math.cos(a) * r, cy + math.sin(a) * r, z, seg, width, thick, turn(z=a + math.pi / 2))


def star4(cx, cy, outer, inner, turn_by=0.0):
    """The outline of a four-pointed star (a compass rose), as 2D points round (cx, cy): the magic circles' design.
    Deliberately not a five- or six-pointed star, which read as religious or occult symbols."""
    pts = []
    for k in range(8):
        a = turn_by + k * math.pi / 4
        r = outer if k % 2 == 0 else inner
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return list(zip(pts, pts[1:] + pts[:1]))


def candle(m, x, y, z, h, r=0.32, wax="Wax", flame="Flame", core="FlameCore", rng=None, drips=2):
    """A candle standing on z: wax drips down its sides and lumps round its rim, a flame, and a bright heart at
    the foot of the flame."""
    rng = rng or random.Random(int(x * 31 + y * 17 + z * 7))
    prism(m, wax, x, y, z, z + h, r, r * 0.94, 8, math.pi / 8)
    top = z + h
    for _ in range(drips):
        a = rng.uniform(0, math.tau)
        length = rng.uniform(0.25, 0.6) * h
        m.block(wax, x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9, top - length / 2 + 0.04, r * 0.55, r * 0.55, length)
    prism(m, flame, x, y, top + 0.05, top + 0.6 + r * 1.6, r * 0.8, 0.03, 6, 0.3)
    if core:
        prism(m, core, x, y, top + 0.02, top + 0.38, r * 0.95, r * 0.4, 6, 0.0)


def chain(m, role, a, b, sag=0.4, link=0.5):
    """A hanging chain from a to b: links turned flat and upright in turn, sagging in the middle."""
    a, b = Vector(a), Vector(b)
    n = max(2, int((b - a).length / link))
    pts = []
    for i in range(n + 1):
        t = i / n
        p = a.lerp(b, t)
        p.z -= sag * 4 * t * (1 - t)
        pts.append(p)
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        w, h = (0.34, 0.12) if i % 2 else (0.12, 0.34)
        beam(m, role, tuple(p), tuple(q), w, h)


def crescent(m, role, cx, cy, cz, r, thick, width=1.1, n=14):
    """A crescent moon standing in the XZ plane facing Y, open towards +X: fat in the middle, pointed at its tips."""
    a0, a1 = 0.75, math.tau - 0.75
    for i in range(n):
        t = (i + 0.5) / n
        a = a0 + (a1 - a0) * t
        seg = r * (a1 - a0) / n + 0.12
        w = 0.15 + width * math.sin(math.pi * t)
        rr = r - w / 2
        obox(m, role, (cx + math.cos(a) * rr, cy, cz + math.sin(a) * rr), (seg, thick, w), turn(y=-(a + math.pi / 2)))


def loose_pages(m, rng, cx, cy, radius, count, roles=("Page",), z=0.04):
    """Torn pages lying on the floor round a point."""
    for k in range(count):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(radius * 0.6, radius)
        obox(m, roles[k % len(roles)], (cx + math.cos(a) * r, cy + math.sin(a) * r, z), (1.3, 1.7, 0.06), turn(z=rng.uniform(0, math.tau)))


def shelf_case(m, rng, origin, yaw, w, h, d, shelves, covers, peep=False):
    """A double-sided bookcase standing on origin, w wide, h tall to its crown and d deep, with `shelves` rows of
    books on both faces (spines out, gilt bands, now and then a gap), so it looks full whichever way it's turned.
    peep puts a pair of glowing eyes in the dark between the books of its second row, on its +Y face (before the
    yaw). Returns its frame; its crown's top is at z h + 0.5."""
    f = Frame(m, origin, turn(z=yaw))
    f.box("WoodDark", 0, 0, 0.3, w + 0.4, d + 0.3, 0.6)
    for s in (-1, 1):
        f.box("Wood", s * (w / 2 - 0.25), 0, (0.6 + h) / 2, 0.5, d, h - 0.6)
    f.box("WoodDeep", 0, 0, (0.6 + h) / 2, w - 0.4, 0.3, h - 0.6)
    f.box("WoodLight", 0, 0.05, h + 0.25, w + 0.5, d + 0.4, 0.5)
    rows = [0.6 + k * (h - 0.6) / shelves for k in range(shelves + 1)]
    for k, z in enumerate(rows[1:-1]):
        f.box("Wood", 0, 0.05, z, w - 0.9, d - 0.2, 0.3)
    for face in (1, -1):
        for k in range(shelves):
            bottom = rows[k] + (0.15 if k else 0)
            top = rows[k + 1] - (0.15 if k < shelves - 1 else 0)
            room = top - bottom - 0.12
            x, end = -w / 2 + 0.58, w / 2 - 0.58
            if peep and k == 1 and face > 0:
                f.box("Peeper", x + 0.3, 0.18, bottom + room * 0.55, 0.2, 0.06, 0.12)
                f.box("Peeper", x + 0.66, 0.18, bottom + room * 0.55, 0.2, 0.06, 0.12)
                x += 1.05
            while True:
                t = rng.uniform(0.32, 0.62)
                if x + t > end:
                    break
                if rng.random() < 0.07:
                    x += rng.uniform(0.4, 0.7)
                    continue
                bh = rng.uniform(0.62, 0.95) * room
                bd = rng.uniform(0.8, 0.95) * (d / 2 - 0.4)
                front = d / 2 - 0.2 - rng.uniform(0, 0.1)
                book(m, rng.choice(covers), f.at(x + t / 2, face * (front - bd / 2), bottom + bh / 2), (t, bd, bh),
                     f.r @ turn(z=math.pi if face > 0 else 0.0), band="Gilt")
                x += t + 0.02
    return f


# ---------------------------------------------------------------------- floor props


def open_tome(seed=1):
    """The map's signature: a great grimoire lying open on a carved lectern. A page stands up in the middle and
    turns back and forth by itself, writing glows on both sides, letters of light rise out of the book for ever,
    and over it all a violet sigil floats and turns. The page's hinge is the spine, straight above the origin."""
    m = prop("OpenTome", Wood=WOOD, WoodDark=WOOD_DARK, WoodLight=WOOD_LIGHT, Gilt=GILT, Leather=LEATHER, Page=PAGE, InkGlow=INK,
             FlipPage=PAGE, FlipGlow=INK, Ribbon=RIBBON, Spell=SPELL, Letters=SPELL)
    rng = random.Random(seed)
    m.loft_z("WoodDark", (0, 0, 0, 4.2, 3.6), (0.5, 0, 0, 3.6, 3.0))
    for sx in (-1, 1):  # carved feet
        m.block("WoodDark", sx * 1.9, 0, 0.3, 0.9, 3.2, 0.6)
    m.block("Wood", 0, 0, 0.75, 2.8, 2.3, 0.5)
    prism(m, "Wood", 0, 0, 1.0, 4.4, 0.62, 0.5, 8, math.pi / 8)
    for z, r in ((1.5, 0.7), (3.9, 0.6)):
        prism(m, "Gilt", 0, 0, z - 0.12, z + 0.12, r, r, 8, math.pi / 8)
    m.loft_z("Wood", (4.4, 0, 0, 1.1, 1.1), (5.0, 0, 0, 3.4, 2.8))
    for sx in (-1, 1):  # brackets under the board
        limb(m, "WoodLight", [(sx * 0.45, 0, 3.8), (sx * 1.7, 0, 4.25), (sx * 3.3, 0, 4.98)], 0.4, 0.28)
    m.block("WoodDark", 0, 0, 5.2, 8.2, 5.8, 0.4)
    m.block("Gilt", 0, 2.93, 5.2, 8.3, 0.1, 0.2)
    # The book, open on the board: cover, pages, gilt corners, writing.
    halves, top = open_book(m, "Leather", (0, 0, 5.4), 3.7, 5.2, 0.6, rise=0.08, board=0.24)
    base = Frame(m, (0, 0, 5.4))
    for sx in (-1, 1):
        for sy in (-1, 1):
            base.box("Gilt", sx * 3.45, sy * 2.35, 0.12, 0.6, 0.6, 0.3)
    ink_lines(halves[1], "InkGlow", 0.45, 3.25, -2.2, 2.2, top, rng, rows=8)
    left = halves[0]
    frame_ring(left, "InkGlow", -1.85, 0.5, top + 0.015, 1.05, 0.14, 0.07, 14)
    for p, q in star4(-1.85, 0.5, 0.95, 0.32):
        left.beam("InkGlow", (p[0], p[1], top + 0.015), (q[0], q[1], top + 0.015), 0.12, 0.07)
    ink_lines(left, "InkGlow", -0.45, -3.25, -2.25, -1.0, top, rng, rows=3)
    # The page turning by itself: standing straight up on the spine, writing on both faces.
    hinge = 5.4 + 0.24 + top
    m.block("FlipPage", 0, 0, hinge + 1.65, 0.08, 4.6, 3.3)
    for s in (-1, 1):
        for k in range(6):
            z = hinge + 0.55 + k * 0.42
            y = -1.9 + rng.uniform(0, 0.3)
            while True:
                word = rng.uniform(0.35, 0.9)
                if y + word > 1.95:
                    break
                m.block("FlipGlow", s * 0.06, y + word / 2, z, 0.05, word, 0.14)
                y += word + rng.uniform(0.15, 0.3)
    limb(m, "Ribbon", [(0.5, 1.4, hinge - 0.02), (0.6, 2.8, hinge - 0.1), (0.7, 3.15, 5.3), (0.75, 3.18, 4.1)], 0.32, 0.3)
    # The sigil floating over it, turning on its own middle.
    zc = 9.6
    flat_ring(m, "Spell", 0, 0, zc, 1.8, 0.2, 0.1, 20)
    flat_ring(m, "Spell", 0, 0, zc, 0.6, 0.14, 0.08, 10)
    for p, q in star4(0, 0, 1.7, 0.55, math.pi / 4):
        beam(m, "Spell", (p[0], p[1], zc), (q[0], q[1], zc), 0.14, 0.08)
    for k in range(8):
        a = k * math.tau / 8 + math.pi / 8
        gem(m, "Spell", math.cos(a) * 2.25, math.sin(a) * 2.25, zc, 0.18, 0.2, 0.2, 4, a)
    # Letters of light rising out of the pages: three columns, rows 1.5 apart, so rising 1.5 and starting over loops.
    # Each column keeps one shape, so nothing changes as they start over.
    for c, (x, y) in enumerate(((-2.7, -1.0), (2.5, 1.4), (0.4, -2.3))):
        for k in range(5):
            z = 6.9 + 0.5 * c + 1.5 * k
            if c == 0:
                gem(m, "Letters", x, y, z, 0.22, 0.28, 0.28, 4, math.pi / 4)
            elif c == 1:
                m.block("Letters", x, y, z, 0.12, 0.12, 0.46)
                m.block("Letters", x + 0.14, y, z - 0.17, 0.3, 0.12, 0.12)
            else:
                m.block("Letters", x, y, z - 0.08, 0.12, 0.12, 0.34)
                m.block("Letters", x, y, z + 0.24, 0.12, 0.12, 0.12)
    return m


def book_stack(seed=2):
    """A crooked tower of giant books with a candle burning on top, a book leaning on it and another fallen at
    its foot. Also the filler round the other props."""
    m = prop("BookStack", CoverA=COVER_A, CoverB=COVER_B, CoverC=COVER_C, CoverD=COVER_D, Page=PAGE, Gilt=GILT, Wax=WAX, Flame=FLAME,
             FlameCore=FLAME_CORE, Brass=BRASS)
    rng = random.Random(seed)
    covers = ("CoverA", "CoverB", "CoverC", "CoverD")
    z, x = 0.0, 0.0
    for k, (length, depth, thick) in enumerate(((6.4, 4.8, 1.3), (5.8, 4.4, 1.0), (6.0, 4.2, 1.5), (5.2, 4.0, 0.9), (4.8, 3.6, 1.3),
                                                 (4.4, 3.4, 0.8), (3.8, 3.0, 1.1))):
        x += rng.uniform(-0.25, 0.25)
        flat_book(m, covers[k % 4], x, rng.uniform(-0.2, 0.2), z, length, depth, thick, rng.uniform(-0.4, 0.4), band="Gilt")
        z += thick
    disc(m, "Brass", x, 0, z + 0.08, 0.9, 0.16, 12)
    candle(m, x, 0, z + 0.16, 2.0, 0.42, rng=rng, drips=3)
    book(m, "CoverB", (4.2, 0.4, 1.84), (0.8, 2.8, 3.6), turn(y=-0.36, z=0.2), band="Gilt")
    flat_book(m, "CoverC", -1.0, 3.6, 0, 3.4, 2.6, 0.7, 0.5, band="Gilt")
    return m


def bookcase(seed=3):
    """A tall bookcase crammed with books, a library ladder hooked to its brass rail, a candle and two books on
    top and two fallen at its foot. In the dark behind the books of one shelf, two eyes peer out, blinking."""
    m = prop("Bookcase", Wood=WOOD, WoodDark=WOOD_DARK, WoodLight=WOOD_LIGHT, WoodDeep=WOOD_DEEP, CoverA=COVER_A, CoverB=COVER_B,
             CoverC=COVER_C, CoverD=COVER_D, CoverE=COVER_E, Page=PAGE, Gilt=GILT, Ladder=WOOD_LIGHT, Brass=BRASS, Wax=WAX, Flame=FLAME,
             FlameCore=FLAME_CORE, Peeper="#fff06a")
    rng = random.Random(seed)
    covers = ("CoverA", "CoverB", "CoverC", "CoverD", "CoverE")
    shelf_case(m, rng, (0, 0, 0), 0.0, 7.0, 11.0, 2.4, 4, covers, peep=True)
    beam(m, "Brass", (-3.3, 1.35, 10.4), (3.3, 1.35, 10.4), 0.16)
    for x in (1.0, 2.3):
        beam(m, "Ladder", (x, 3.7, 0), (x, 1.5, 10.5), 0.26)
        m.block("Brass", x, 1.42, 10.62, 0.2, 0.3, 0.3)
    for k in range(9):
        z = 0.9 + k * 1.1
        y = 3.7 - (3.7 - 1.5) * z / 10.5
        beam(m, "Ladder", (1.0, y, z), (2.3, y, z), 0.16)
    candle(m, -2.3, 0.2, 11.5, 1.6, 0.36, rng=rng)
    flat_book(m, "CoverD", 1.4, 0.1, 11.5, 2.6, 1.8, 0.6, 0.3, band="Gilt")
    flat_book(m, "CoverA", 1.3, 0.0, 12.1, 2.2, 1.6, 0.5, -0.2, band="Gilt")
    flat_book(m, "CoverA", -1.8, 2.9, 0, 3.0, 2.2, 0.7, 0.6, band="Gilt")
    flat_book(m, "CoverC", -3.1, 5.0, 0, 2.6, 2.0, 0.6, -0.3, band="Gilt")
    return m


def candelabra(seed=4):
    """A tall iron candelabra on three feet, four curling arms and a fifth candle in the middle, every flame
    flickering."""
    m = prop("Candelabra", Iron=IRON, IronLight=IRON_LIGHT, Brass=BRASS, Wax=WAX, Flame=FLAME, FlameCore=FLAME_CORE)
    rng = random.Random(seed)
    for k in range(3):
        a = k * math.tau / 3 + 0.5
        beam(m, "Iron", (math.cos(a) * 1.9, math.sin(a) * 1.9, 0.25), (math.cos(a) * 0.3, math.sin(a) * 0.3, 1.5), 0.32)
        ball(m, "IronLight", math.cos(a) * 1.95, math.sin(a) * 1.95, 0.32, 0.38, 6, 4)
    prism(m, "Iron", 0, 0, 1.2, 6.2, 0.3, 0.24, 8)
    for z, r in ((1.5, 0.55), (3.6, 0.45), (5.4, 0.4)):
        ball(m, "IronLight", 0, 0, z, r, 8, 4)
    prism(m, "Brass", 0, 0, 6.1, 6.4, 0.5, 0.7, 8)
    for k in range(4):
        a = k * math.tau / 4 + math.pi / 4
        c, s = math.cos(a), math.sin(a)
        limb(m, "Iron", [(c * 0.2, s * 0.2, 5.6), (c * 1.1, s * 1.1, 5.2), (c * 2.0, s * 2.0, 5.6), (c * 2.3, s * 2.3, 6.35)], 0.24, 0.2)
        limb(m, "Iron", [(c * 0.25, s * 0.25, 4.4), (c * 0.9, s * 0.9, 4.7), (c * 1.0, s * 1.0, 5.25)], 0.16, 0.12)
        disc(m, "Brass", c * 2.3, s * 2.3, 6.5, 0.55, 0.2, 10)
        candle(m, c * 2.3, s * 2.3, 6.6, rng.uniform(1.3, 1.9), 0.3, rng=rng)
    candle(m, 0, 0, 6.4, 2.4, 0.36, rng=rng, drips=3)
    return m


def floating_candles(seed=5):
    """Candles floating in the air over a pool of spilt wax, in two groups bobbing at their own pace, wax
    dripping off their feet."""
    m = prop("FloatingCandles", Wax=WAX, CandleA=WAX, CandleB=WAX_WARM, FlameA=FLAME, FlameB=FLAME)
    rng = random.Random(seed)
    puddle(m, "Wax", ((0, 0, 3.4, 2.8), (1.0, 0.8, 2.0, 1.6), (-1.1, -0.6, 1.8, 1.4)), z=0.06, thick=0.12)
    for x, y, h in ((0.5, -0.3, 0.7), (-0.7, 0.4, 0.45), (0.2, 0.9, 0.3)):  # melted stubs
        prism(m, "Wax", x, y, 0.1, 0.1 + h, 0.32, 0.3, 8, math.pi / 8)
    spots = [(0.0, 0.0, 6.8, 1.8), (1.9, 0.6, 5.2, 1.4), (-1.6, 1.3, 7.6, 1.6), (-1.2, -1.8, 4.8, 1.2), (1.4, -1.6, 8.4, 1.5),
             (2.4, 2.0, 7.0, 1.1), (-2.5, -0.2, 6.0, 1.3), (0.4, 2.4, 9.2, 1.0), (-0.3, -2.6, 9.6, 1.2)]
    for k, (x, y, z, h) in enumerate(spots):
        g = "A" if k % 2 == 0 else "B"
        candle(m, x, y, z, h, 0.32, wax=f"Candle{g}", flame=f"Flame{g}", core=None, rng=rng, drips=2)
        m.loft_z(f"Candle{g}", (z - 0.35, x + 0.12, y, 0.06, 0.06), (z + 0.05, x + 0.12, y, 0.22, 0.22))  # a drip under it
    return m


def ink_well(seed=6):
    """A giant inkwell of dark glass, ink glowing at its mouth and running down its shoulders, a label with a
    warning rune, ink spilt round its foot, and a huge quill stuck in it, nodding as if it writes. The quill
    turns round the bottle's mouth, straight above the origin."""
    m = prop("InkWell", InkBottle=BOTTLE, BottleLight=BOTTLE_LIGHT, Brass=BRASS, InkGlow=INK, Ink=INK_DARK, Page=PAGE,
             Quill="#f3eee4", QuillBarb="#bdb3c9", QuillBand=GILT, CoverC=COVER_C, Gilt=GILT)
    rng = random.Random(seed)
    puddle(m, "Ink", ((1.6, 1.8, 4.2, 3.0), (2.8, 2.8, 2.4, 2.2), (0.6, 2.6, 2.0, 1.6)), z=0.05, thick=0.1)
    for x, y, w, d in ((2.2, 2.4, 1.6, 0.2), (1.0, 2.6, 0.24, 1.2), (3.1, 3.2, 0.9, 0.18)):
        m.block("InkGlow", x, y, 0.1, w, d, 0.06)
    prism(m, "BottleLight", 0, 0, 0, 0.4, 2.55, 2.45, 8, math.pi / 8)
    prism(m, "InkBottle", 0, 0, 0.4, 3.2, 2.3, 2.35, 8, math.pi / 8)
    prism(m, "InkBottle", 0, 0, 3.2, 4.0, 2.35, 1.1, 8, math.pi / 8)
    prism(m, "InkBottle", 0, 0, 4.0, 4.55, 1.0, 1.0, 8, math.pi / 8)
    disc(m, "InkGlow", 0, 0, 4.58, 0.98, 0.06, 12)
    flat_ring(m, "Brass", 0, 0, 4.65, 1.12, 0.36, 0.34, 12)
    m.block("BottleLight", -0.62, 2.16, 1.9, 0.24, 0.1, 2.0)  # a shine on the glass
    m.block("Page", 0.25, 2.15, 1.9, 1.1, 0.1, 1.6)
    for s in (-1, 1):
        obox(m, "InkGlow", (0.25, 2.215, 1.9), (0.9, 0.05, 0.14), turn(y=s * 0.9))
    for a in (0.0, math.pi, math.pi * 1.5):  # ink running down the shoulders
        c, s = math.cos(a), math.sin(a)
        beam(m, "InkGlow", (c * 1.1, s * 1.1, 4.0), (c * 2.23, s * 2.23, 3.2), 0.24, 0.1)
        beam(m, "InkGlow", (c * 2.23, s * 2.23, 3.2), (c * 2.23, s * 2.23, 2.2 + 0.3 * (a > 3)), 0.24, 0.1, 0.16)
    # The quill: its shaft passes through the middle of the mouth, so it nods round it.
    base, tip = Vector((0, 0.42, 3.4)), Vector((0, -2.6, 12.4))
    along = tip - base
    unit = along.normalized()
    side = Vector((1, 0, 0))
    normal = unit.cross(side).normalized()
    beam(m, "Quill", tuple(base), tuple(tip + unit * 0.4), 0.24, None, 0.08)
    plate(m, "Quill", base + along * 0.3, base + along * 0.62, side, 1.0, 2.1, 0.12)
    plate(m, "Quill", base + along * 0.62, tip + unit * 0.4, side, 2.1, 0.25, 0.12)
    for k in range(6):
        t = 0.42 + k * 0.09
        half = (0.5 + 0.55 * (t - 0.3) / 0.32) if t < 0.62 else 1.05 - 0.92 * (t - 0.62) / 0.42
        p = base + along * t
        for sx in (-1, 1):
            for n in (-1, 1):
                a = p + side * sx * 0.2 + normal * n * 0.08
                b = p + side * sx * (half - 0.12) + unit * 0.35 + normal * n * 0.08
                plate(m, "QuillBarb", a, b, unit, 0.14, 0.1, 0.05)
    beam(m, "QuillBand", tuple(base + along * 0.2), tuple(base + along * 0.25), 0.36)
    # A sheet it was writing on, and a book.
    obox(m, "Page", (-3.7, 1.0, 0.06), (3.0, 3.8, 0.12), turn(z=0.35))
    ink_lines(Frame(m, (-3.7, 1.0, 0.12), turn(z=0.35)), "InkGlow", -1.2, 1.2, -1.5, 1.5, 0, rng, rows=6)
    flat_book(m, "CoverC", -2.6, -2.8, 0, 3.2, 2.4, 0.8, -0.4, band="Gilt")
    return m


def hourglass(seed=7):
    """A big hourglass in a turned wooden frame, its bulbs a cage of brass, the sand inside glowing like embers,
    grains of it falling through the neck for ever."""
    m = prop("Hourglass", Wood=WOOD, WoodDark=WOOD_DARK, WoodLight=WOOD_LIGHT, Brass=BRASS, TimeSand="#ffcf6a", Grain="#ffe39a")
    for k in range(3):
        a = k * math.tau / 3 + math.pi / 2
        ball(m, "Brass", math.cos(a) * 1.9, math.sin(a) * 1.9, 0.3, 0.42, 6, 4)
    prism(m, "WoodDark", 0, 0, 0.5, 0.85, 2.7, 2.7, 8, math.pi / 8)
    prism(m, "Wood", 0, 0, 0.85, 1.35, 2.45, 2.45, 8, math.pi / 8)
    prism(m, "Wood", 0, 0, 8.65, 9.15, 2.45, 2.45, 8, math.pi / 8)
    prism(m, "WoodDark", 0, 0, 9.15, 9.5, 2.7, 2.7, 8, math.pi / 8)
    ball(m, "Brass", 0, 0, 9.92, 0.5, 8, 4)
    gem(m, "Brass", 0, 0, 10.37, 0.22, 0.7, 0.1, 4)
    for k in range(3):  # turned posts
        a = k * math.tau / 3 + math.pi / 6
        x, y = math.cos(a) * 2.05, math.sin(a) * 2.05
        prism(m, "Wood", x, y, 1.35, 8.65, 0.26, 0.26, 6)
        for z in (2.6, 5.0, 7.4):
            ball(m, "WoodLight", x, y, z, 0.42, 6, 4)
    for prof in (((1.35, 1.55), (2.6, 1.8), (4.0, 1.15), (4.85, 0.24)), ((8.65, 1.55), (7.4, 1.8), (6.0, 1.15), (5.15, 0.24))):
        for k in range(8):
            a = k * math.tau / 8
            pts = [(math.cos(a) * r, math.sin(a) * r, z) for z, r in prof]
            for p, q in zip(pts, pts[1:]):
                beam(m, "Brass", p, q, 0.1)
        flat_ring(m, "Brass", 0, 0, prof[1][0], 1.8, 0.14, 0.14, 16)
    prism(m, "Brass", 0, 0, 4.8, 5.2, 0.42, 0.42, 8)
    prism(m, "TimeSand", 0, 0, 5.2, 6.4, 0.2, 1.3, 8)
    prism(m, "TimeSand", 0, 0, 1.35, 2.3, 1.5, 1.2, 8)
    prism(m, "TimeSand", 0, 0, 2.3, 3.3, 1.2, 0.12, 8)
    for z in (4.55, 4.1, 3.65):  # grains half a stud apart, falling half a stud and starting over
        m.block("Grain", 0, 0, z, 0.16, 0.16, 0.16)
    return m


def mimic_book(seed=8):
    """A rare find: a huge book that's really a monster. Its cover lifts and slams like a jaw, fangs along the
    pages, angry yellow eyes on the cover, a ribbon for a tongue, glowing violet inside, and torn pages all round
    it. The cover hinges on its spine, straight above the origin, so the game snaps it round that line."""
    m = prop("MimicBook", Leather="#2f6a5a", LeatherDark="#1f4a3f", Page=PAGE, Gilt=GILT, Teeth="#f4ecd6", InkGlow=INK,
             Tongue=RIBBON, MimicLid="#2f6a5a", MimicPages=PAGE, Fangs="#f4ecd6", Gaze="#ffd84a", Pupil="#1a1020",
             MimicBrow="#1f4a3f", PageDark=PAGE_DARK)
    rng = random.Random(seed)
    hinge = 1.6
    m.block("Leather", 0, 2.6, 0.18, 7.4, 5.6, 0.36)
    m.block("LeatherDark", 0, -0.2, 1.0, 7.6, 0.6, 2.0)
    m.block("Page", 0, 2.6, 0.95, 7.0, 5.1, 1.2)
    for sx in (-1, 1):
        for sy in (0.16, 5.04):
            m.block("Gilt", sx * 3.38, sy, 0.18, 0.8, 0.8, 0.42)
    m.block("Gilt", 0, 5.45, 0.9, 1.2, 0.2, 1.0)
    for k in range(9):
        x = -3.0 + k * 0.75
        beam(m, "Teeth", (x, 4.75, 1.45), (x, 4.85, 2.15), 0.5, 0.42, 0.06)
    for sx in (-1, 1):
        for y in (1.6, 2.6, 3.6):
            beam(m, "Teeth", (sx * 3.2, y, 1.45), (sx * 3.25, y, 2.05), 0.42, 0.42, 0.06)
    m.block("InkGlow", 0, 2.6, 1.56, 6.0, 4.0, 0.06)
    limb(m, "Tongue", [(0.9, 3.0, 1.62), (1.0, 4.6, 1.75), (1.1, 5.7, 1.3), (1.3, 6.5, 0.3)], 0.75, 0.6)
    # The lid, open 29 degrees round the hinge; the game swings it 14 degrees either way.
    lid = Frame(m, (0, 0, hinge), turn(x=0.5))
    lid.box("MimicPages", 0, 2.6, 0.6, 7.0, 5.1, 1.2)
    lid.box("MimicLid", 0, 2.6, 1.38, 7.4, 5.6, 0.36)
    lid.box("MimicLid", 0, -0.2, 0.7, 7.5, 0.6, 1.5)
    for k in range(8):
        x = -2.62 + k * 0.75
        lid.beam("Fangs", (x, 4.75, 0.1), (x, 4.85, -0.62), 0.5, 0.42, 0.06)
    for sx in (-1, 1):  # bulging eyes on the cover's front edge, under heavy angry brows
        lid.box("MimicLid", sx * 1.6, 4.4, 1.9, 1.5, 1.2, 0.8)
        lid.box("Gaze", sx * 1.6, 5.03, 1.95, 1.1, 0.08, 0.6)
        lid.box("Pupil", sx * 1.6, 5.08, 1.95, 0.2, 0.06, 0.5)
        lid.box("MimicBrow", sx * 1.6, 5.0, 2.42, 1.7, 0.45, 0.32, turn(y=-sx * 0.32))
    loose_pages(m, rng, 2.6, 2.4, 6.5, 6, ("Page", "PageDark"))
    return m


def scroll_pile(seed=9):
    """Filler: a pile of rolled scrolls, one tied with a ribbon, one leaning up, one unrolled with writing, a
    small book and a candle stub on it."""
    m = prop("ScrollPile", Scroll=PAGE, Knob=WOOD_DARK, Ribbon=RIBBON, CoverB=COVER_B, Page=PAGE, Gilt=GILT, Wax=WAX, Flame=FLAME,
             FlameCore=FLAME_CORE, InkGlow=INK)
    rng = random.Random(seed)

    def scroll(a, b, r):
        a, b = Vector(a), Vector(b)
        unit = (b - a).normalized()
        tube(m, "Scroll", a, b, r)
        tube(m, "Knob", a - unit * 0.35, a + unit * 0.05, r * 0.45)
        tube(m, "Knob", b - unit * 0.05, b + unit * 0.35, r * 0.45)

    for y, z, x0, length in ((-0.47, 0.42, -1.5, 3.2), (0.47, 0.42, -1.2, 3.0), (0.0, 1.2, -1.4, 3.1)):
        scroll((x0, y, z), (x0 + length, y, z), 0.45)
    tube(m, "Ribbon", (0.0, 0.0, 1.2), (0.3, 0.0, 1.2), 0.5)
    scroll((1.9, 1.4, 0.36), (2.5, 1.2, 3.3), 0.4)
    obox(m, "Scroll", (-0.4, 2.3, 0.04), (3.0, 2.2, 0.08))
    tube(m, "Scroll", (-1.9, 3.5, 0.3), (1.1, 3.5, 0.3), 0.3)
    ink_lines(Frame(m, (-0.4, 2.3, 0.08)), "InkGlow", -1.2, 1.2, -0.9, 0.8, 0, rng, rows=4)
    flat_book(m, "CoverB", 3.2, -0.6, 0, 2.6, 1.9, 0.6, 0.4, band="Gilt")
    candle(m, 3.2, -0.6, 0.6, 0.6, 0.3, rng=rng)
    return m


def spell_page(seed=10):
    """A giant loose page lying flat on the floor, scorched round its edges, a corner curling up, with a glowing
    spell circle whose ring of runes slowly turns, lines of writing and a wax seal. Flat (under half a stud), so
    it can lie where the eggs land."""
    m = prop("SpellPage", Page=PAGE, PageDark=PAGE_DARK, InkGlow=INK, SpellRing=SPELL, Seal="#a8202f")
    rng = random.Random(seed)
    m.block("Page", 0, 0, 0.05, 10, 13, 0.1)
    for k in range(24):  # a ragged, scorched edge
        along = rng.uniform(0.6, 1.4)
        if k % 2:
            x, y = rng.uniform(-4.6, 4.6), rng.choice((-1, 1)) * (6.5 + rng.uniform(0.05, 0.3))
            m.block("PageDark", x, y, 0.04, along, 0.7, 0.08)
        else:
            x, y = rng.choice((-1, 1)) * (5.0 + rng.uniform(0.05, 0.3)), rng.uniform(-6.1, 6.1)
            m.block("PageDark", x, y, 0.04, 0.7, along, 0.08)
    obox(m, "Page", (4.55, 6.15, 0.14), (1.6, 1.4, 0.08), turn(x=-0.18, y=0.14, z=0.78))
    flat_ring(m, "SpellRing", 0, 0, 0.13, 3.4, 0.28, 0.07, 24)
    for k in range(12):
        a = k * math.tau / 12
        p = Vector((math.cos(a) * 4.1, math.sin(a) * 4.1, 0.13))
        u, v = Vector((-math.sin(a), math.cos(a), 0)), Vector((math.cos(a), math.sin(a), 0))
        if k % 3 == 0:  # runes: a bar with a branch, a bar and a dot, two bars
            beam(m, "SpellRing", tuple(p - v * 0.4), tuple(p + v * 0.4), 0.16, 0.07)
            beam(m, "SpellRing", tuple(p + v * 0.4), tuple(p + v * 0.05 + u * 0.35), 0.14, 0.07)
        elif k % 3 == 1:
            beam(m, "SpellRing", tuple(p - v * 0.4), tuple(p + v * 0.15), 0.16, 0.07)
            m.block("SpellRing", *(p + v * 0.38), 0.18, 0.18, 0.07)
        else:
            for side in (-1, 1):
                beam(m, "SpellRing", tuple(p - v * 0.35 + u * side * 0.17), tuple(p + v * 0.35 + u * side * 0.17), 0.13, 0.07)
    for p, q in star4(0, 0, 3.0, 1.0, math.pi / 2):
        beam(m, "InkGlow", (p[0], p[1], 0.12), (q[0], q[1], 0.12), 0.18, 0.06)
    flat_ring(m, "InkGlow", 0, 0, 0.12, 1.1, 0.18, 0.06, 14)
    page = Frame(m, (0, 0, 0.1))
    ink_lines(page, "InkGlow", -4.0, 4.0, 4.7, 6.0, 0, rng, rows=3, height=0.2)
    ink_lines(page, "InkGlow", -4.0, 2.2, -6.0, -4.7, 0, rng, rows=3, height=0.2)
    disc(m, "Seal", 3.4, -5.3, 0.15, 0.75, 0.14, 12)
    return m


# ---------------------------------------------------------------------- rim props and landmarks


def page_tree(seed=11):
    """A crooked black tree that grew pages instead of leaves, little open books perched on its branches like
    roosting birds, and glowing moths circling it."""
    m = prop("PageTree", Bark="#2a2230", BarkDark="#1d1722", Page=PAGE, PageDark=PAGE_DARK, CoverA=COVER_A, CoverD=COVER_D, Moths="#efe2ff")
    rng = random.Random(seed)
    trunk = [(0, 0, 0), (0.5, 0.2, 3.5), (-0.3, 0.1, 7.0), (0.4, -0.3, 10.0), (0.1, 0.0, 12.0)]
    limb(m, "Bark", trunk, 1.7, 0.7)
    for k in range(5):
        a = k * math.tau / 5 + 0.3
        limb(m, "BarkDark", [(math.cos(a) * 0.5, math.sin(a) * 0.5, 2.0), (math.cos(a) * 1.6, math.sin(a) * 1.6, 0.8),
                             (math.cos(a) * 2.8, math.sin(a) * 2.8, 0.1)], 0.8, 0.35)

    def on_trunk(z):
        for p, q in zip(trunk, trunk[1:]):
            if p[2] <= z <= q[2]:
                t = (z - p[2]) / (q[2] - p[2])
                return tuple(a + (b - a) * t for a, b in zip(p, q))
        return trunk[-1]

    ends = []
    for k in range(6):
        a = k * math.tau / 6 + rng.uniform(-0.3, 0.3)
        z0 = rng.uniform(7.5, 11.5)
        r = rng.uniform(4.0, 5.6)
        end = (math.cos(a) * r, math.sin(a) * r, z0 + rng.uniform(1.5, 3.2))
        limb(m, "Bark", [on_trunk(z0), (math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, z0 + 1.4), end], 0.55, 0.2)
        ends.append((a, end))
    ends.append((0, (0.1, 0.0, 12.6)))
    for k, (a, (x, y, z)) in enumerate(ends):
        for j in range(14):  # a clump of pages for leaves
            px, py, pz = x + rng.uniform(-2.0, 2.0), y + rng.uniform(-2.0, 2.0), z + rng.uniform(-0.9, 1.6)
            obox(m, "Page" if j % 3 else "PageDark", (px, py, pz), (1.7, 1.25, 0.08),
                 turn(rng.uniform(-0.9, 0.9), rng.uniform(-0.9, 0.9), rng.uniform(0, math.tau)))
        if k % 2 == 0 and k < 6:  # a book perched on the branch end, open like wings
            open_book(m, "CoverA" if k % 4 else "CoverD", (x, y, z + 0.1), 1.3, 1.8, 0.3, turn(z=a), rise=0.5, board=0.12)
    for k in range(10):  # moths circling the crown
        a = k * math.tau / 10 + rng.uniform(-0.2, 0.2)
        r = rng.uniform(3.5, 6.5)
        f = Frame(m, (math.cos(a) * r, math.sin(a) * r, rng.uniform(8.0, 15.0)), turn(z=a + math.pi / 2))
        f.box("Moths", 0, 0, 0, 0.5, 0.14, 0.14)
        for s in (-1, 1):
            f.box("Moths", 0, s * 0.3, 0.08, 0.45, 0.5, 0.06, turn(x=s * 0.45))
    return m


def leaning_shelves(seed=12):
    """Three bookcases stacked on each other, each turned and shoved off-centre on the one below, an oil lamp
    on top, and loose pages falling past them for ever."""
    m = prop("LeaningShelves", Wood=WOOD, WoodDark=WOOD_DARK, WoodLight=WOOD_LIGHT, WoodDeep=WOOD_DEEP, CoverA=COVER_A, CoverB=COVER_B,
             CoverC=COVER_C, CoverD=COVER_D, CoverE=COVER_E, Page=PAGE, Gilt=GILT, Brass=BRASS, Lamp="#ffc86e", Flutter=PAGE)
    rng = random.Random(seed)
    covers = ("CoverA", "CoverB", "CoverC", "CoverD", "CoverE")
    shelf_case(m, rng, (0, 0, 0), 0.0, 7.0, 7.0, 2.6, 2, covers)
    shelf_case(m, rng, (0.7, 0.2, 7.5), 0.22, 6.2, 6.2, 2.4, 2, covers)
    shelf_case(m, rng, (1.5, 0.1, 14.2), -0.15, 5.2, 5.2, 2.2, 2, covers)
    top = 14.2 + 5.2 + 0.5
    prism(m, "Brass", 1.6, 0.1, top, top + 0.4, 0.75, 0.6, 8)
    prism(m, "Lamp", 1.6, 0.1, top + 0.4, top + 1.5, 0.55, 0.7, 8)
    prism(m, "Brass", 1.6, 0.1, top + 1.5, top + 1.75, 0.75, 0.75, 8)
    prism(m, "Brass", 1.6, 0.1, top + 1.75, top + 2.6, 0.3, 0.22, 8)
    # Pages falling beside it: two columns, pages exactly 3 apart in each, so falling 3 and starting over loops.
    for (x, y, z0), rot in (((5.1, 0.9, 1.0), turn(0.5, -0.3, 0.4)), ((4.4, -1.4, 2.5), turn(-0.4, 0.35, 1.9))):
        for k in range(7):
            obox(m, "Flutter", (x, y, z0 + 3 * k), (1.3, 1.0, 0.06), rot)
    return m


def chained_tome(seed=13):
    """A forbidden book chained down on a stone pedestal, padlocked, an eye-like sigil on its cover and violet
    light leaking from between its pages. It rattles against its chains, trying to get away."""
    m = prop("ChainedTome", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Iron=IRON, IronLight=IRON_LIGHT, Chain=IRON_LIGHT,
             Tome="#3b1f5e", TomePage=PAGE, TomeGilt=GILT, Lock=GILT, TomeGlow=INK, InkGlow=INK)
    m.loft_z("StoneDark", (0, 0, 0, 6.4, 6.4), (0.7, 0, 0, 5.8, 5.8))
    m.block("StoneLight", 0, 0, 0.9, 5.0, 5.0, 0.4)
    m.block("Stone", 0, 0, 1.9, 4.6, 4.6, 2.2)
    m.block("StoneLight", 0, 0, 3.2, 5.4, 5.4, 0.4)
    for sx, sy in ((0, 1), (0, -1), (1, 0), (-1, 0)):  # a glowing rune on each face of the pedestal: a diamond over a bar
        x, y = sx * 2.33, sy * 2.33
        obox(m, "InkGlow", (x, y, 2.25), (0.08, 0.62, 0.62) if sx else (0.62, 0.08, 0.62), turn(x=math.pi / 4) if sx else turn(y=math.pi / 4))
        m.block("InkGlow", x, y, 1.45, 0.08 if sx else 1.2, 1.2 if sx else 0.08, 0.16)
    posts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            prism(m, "Iron", sx * 3.5, sy * 3.5, 0, 5.2, 0.28, 0.24, 6)
            ball(m, "IronLight", sx * 3.5, sy * 3.5, 5.35, 0.45, 6, 4)
            posts.append((sx, sy))
    flat_book(m, "Tome", 0, 0, 3.4, 4.8, 3.6, 1.7, 0.0, page="TomePage")
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.block("TomeGilt", sx * 2.15, sy * 1.55, 5.1, 0.6, 0.6, 0.12)
            m.block("TomeGilt", sx * 2.15, sy * 1.55, 3.5, 0.6, 0.6, 0.12)
    m.block("Lock", 0, 1.98, 4.25, 0.9, 0.4, 0.9)
    hoop(m, "Lock", 0, 1.98, 4.95, 0.35, 0.14, "xz", 8)
    m.block("Lock", 0, 1.3, 5.13, 0.6, 1.2, 0.08)
    m.block("TomeGlow", 0, 1.65, 4.25, 4.0, 0.06, 0.3)  # light leaking from the pages
    for sx in (-1, 1):
        m.block("TomeGlow", sx * 2.25, 0.1, 4.25, 0.06, 2.6, 0.3)
    for side in (-1, 1):  # an eye on the cover: two lids meeting at its corners, and its iris
        for p, q in (((-1.1, 0), (-0.45, side * 0.48)), ((-0.45, side * 0.48), (0.45, side * 0.48)), ((0.45, side * 0.48), (1.1, 0))):
            beam(m, "TomeGlow", (p[0], p[1] - 0.2, 5.14), (q[0], q[1] - 0.2, 5.14), 0.14, 0.06)
    disc(m, "TomeGlow", 0, -0.2, 5.14, 0.3, 0.06, 10)
    for sx, sy in posts:
        chain(m, "Chain", (sx * 3.5, sy * 3.5, 5.0), (sx * 2.0, sy * 1.2, 4.4), 0.5)
    return m


def clock_tower(seed=14):
    """A landmark for the rims: the library's clock tower. A big glowing clock whose minute hand runs backwards,
    a pendulum swinging in front of a lit window, lanterns by the door, violet light in the belfry and a glowing
    orb on its spire. The clock and the pendulum are centred over the origin, so the game turns them in place."""
    m = prop("ClockTower", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Shadow=SHADOW, Roof="#3d3557", WoodDark=WOOD_DARK,
             Gilt=GILT, Brass=BRASS, Iron=IRON, Window=WINDOW, InkGlow=INK, Orb=SPELL, ClockGlow="#fff1c9", HourHand=IRON, MinuteHand=IRON,
             Pendulum=BRASS, Lamp="#ffc86e", CoverA=COVER_A, CoverC=COVER_C, Page=PAGE, Front="#ff00ff")
    m.loft_z("StoneDark", (0, 0, 0, 10, 10), (1.2, 0, 0, 9.2, 9.2))
    m.block("Stone", 0, 0, 11.8, 7.4, 7.4, 21.2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.block("StoneLight", sx * 3.7, sy * 3.7, 11.875, 1.3, 1.3, 21.25)
    for z in (8.0, 15.4):
        m.block("StoneLight", 0, 0, z, 8.0, 8.0, 0.5)
    m.block("StoneLight", 0, 0, 22.75, 9.0, 9.0, 0.7)
    # The door, its frame and two lanterns.
    m.block("WoodDark", 0, 3.78, 3.3, 2.8, 0.2, 4.2)
    m.block("StoneLight", 0, 3.85, 5.75, 3.7, 0.3, 0.7)
    for sx in (-1, 1):
        m.block("StoneLight", sx * 1.65, 3.85, 3.3, 0.4, 0.3, 4.2)
        beam(m, "Iron", (sx * 2.4, 3.7, 5.7), (sx * 2.4, 4.6, 5.7), 0.14)
        m.block("Iron", sx * 2.4, 4.6, 5.5, 0.8, 0.8, 0.15)
        m.block("Lamp", sx * 2.4, 4.6, 5.0, 0.6, 0.6, 0.85)
        m.block("Iron", sx * 2.4, 4.6, 4.55, 0.7, 0.7, 0.12)
    ball(m, "Gilt", 0.9, 3.95, 3.2, 0.18, 6, 4)  # the door's handle
    # The big window, lit, with the pendulum swinging in front of it.
    m.block("Window", 0, 3.75, 11.6, 2.6, 0.12, 4.4)
    m.block("Iron", 0, 3.86, 11.6, 0.2, 0.12, 4.4)
    m.block("Iron", 0, 3.86, 11.6, 2.6, 0.12, 0.2)
    m.block("StoneLight", 0, 3.82, 14.05, 3.2, 0.3, 0.5)
    m.block("Window", 3.75, 0, 11.6, 0.12, 2.2, 3.6)
    m.block("Window", -3.75, 0, 11.6, 0.12, 2.2, 3.6)
    m.block("Window", 0, -3.75, 11.6, 2.2, 0.12, 3.6)
    m.block("Iron", 0, 4.05, 16.1, 0.5, 0.7, 0.5)
    m.block("Pendulum", 0, 4.5, 13.1, 0.2, 0.2, 6.0)
    disc(m, "Pendulum", 0, 4.5, 9.9, 1.0, 0.3, 14, "xz")
    # The clock.
    zc = 18.8
    disc(m, "ClockGlow", 0, 3.85, zc, 2.6, 0.2, 24, "xz")
    hoop(m, "Brass", 0, 3.98, zc, 2.72, 0.32, "xz", 24)
    for k in range(12):
        a = k * math.tau / 12
        s = 0.42 if k % 3 == 0 else 0.22
        m.block("Iron", math.sin(a) * 2.15, 4.02, zc + math.cos(a) * 2.15, s, 0.1, s)
    m.block("MinuteHand", 0, 4.15, zc + 1.0, 0.24, 0.1, 2.3)
    hour = turn(y=2.1)
    obox(m, "HourHand", tuple(Vector((0, 4.28, zc)) + hour @ Vector((0, 0, 0.6))), (0.32, 0.1, 1.5), hour)
    disc(m, "Gilt", 0, 4.4, zc, 0.3, 0.12, 10, "xz")
    # The belfry with violet light in its openings, the roof and its glowing orb.
    m.block("Stone", 0, 0, 25.2, 6.2, 6.2, 4.2)
    for sx, sy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        w, d = (0.12, 2.0) if sx else (2.0, 0.12)
        m.block("InkGlow", sx * 3.12, sy * 3.12, 25.0, w, d, 2.8)
        m.block("StoneLight", sx * 3.2, sy * 3.2, 26.65, 0.3 if sx else 2.6, 2.6 if sx else 0.3, 0.4)
    m.block("Roof", 0, 0, 27.5, 7.2, 7.2, 0.4)
    m.loft_z("Roof", (27.7, 0, 0, 6.4, 6.4), (34.5, 0, 0, 0.3, 0.3))
    m.block("Iron", 0, 0, 35.2, 0.18, 0.18, 1.6)
    ball(m, "Orb", 0, 0, 35.9, 0.55, 8, 5)
    flat_book(m, "CoverA", 3.0, 5.4, 0, 2.8, 2.0, 0.7, 0.3, band="Gilt")
    flat_book(m, "CoverC", 3.1, 5.3, 0.7, 2.4, 1.8, 0.6, -0.2, band="Gilt")
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


def popup_book(seed=15):
    """A landmark for the rims: a giant pop-up book lying open, a paper castle standing up out of its pages with
    lit windows, paper trees and hills, a paper moon on a stick rocking over it like a stage prop, and paper bats
    circling the towers."""
    m = prop("PopupBook", Leather=LEATHER, Page=PAGE, Gilt=GILT, Paper="#f6ecd2", PaperShade="#d9c8a0", PaperTree="#7d9a72",
             PaperRoof="#8a68b8", Window=WINDOW, Shadow=SHADOW, InkGlow=INK, MoonStick=IRON, Crescent="#fff0b0", Bats="#231c2e",
             Ribbon=RIBBON, Front="#ff00ff")
    rng = random.Random(seed)
    halves, top = open_book(m, "Leather", (0, 0, 0), 12, 16, 1.2, rise=0.05, board=0.6)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.block("Gilt", sx * 11.5, sy * 7.5, 0.3, 1.4, 1.4, 0.7)
    for s, f in zip((-1, 1), halves):
        ink_lines(f, "InkGlow", s * 2.0, s * 10.5, 5.0, 7.2, top, rng, rows=3, height=0.3, thick=0.08)
    # The castle: a keep, two towers and a spire, cut out of paper, standing on a line across the gutter.
    m.block("Paper", 0, -2.0, 7.0, 9.0, 0.3, 10.4)
    for x in (-4.0, -2.0, 0.0, 2.0, 4.0):
        m.block("Paper", x, -2.0, 12.6, 1.0, 0.3, 0.8)
    m.loft_z("PaperRoof", (12.15, 0, -2.0, 3.2, 0.36), (18.6, 0, -2.0, 0.1, 0.36))
    for sx in (-1, 1):
        m.block("PaperShade", sx * 5.6, -2.0, 9.475, 3.0, 0.4, 15.45)
        m.loft_z("PaperRoof", (17.2, sx * 5.6, -2.0, 3.8, 0.4), (21.8, sx * 5.6, -2.0, 0.1, 0.4))
        for z in (12.5, 15.0):
            m.block("Window", sx * 5.6, -1.75, z, 0.8, 0.1, 1.2)
        for x in (2.5, 0.0):
            beam(m, "PaperShade", (sx * (x + 1.2), -2.3, 3.6), (sx * (x + 1.2), -5.2, 1.8), 1.0, 0.15)
    for x, z in ((-2.5, 8.0), (2.5, 8.0), (0.0, 9.6), (-2.5, 10.8), (2.5, 10.8)):
        m.block("Window", x, -1.8, z, 0.8, 0.1, 1.2)
    m.block("Shadow", 0, -1.8, 3.6, 2.4, 0.1, 3.6)
    # Paper trees and hills on the pages in front.
    for x, y in ((-8.5, 3.0), (-6.5, 5.5), (8.0, 4.0), (9.5, 1.5)):
        m.block("PaperShade", x, y, 3.0, 0.5, 0.2, 2.6)
        for k, (z, w) in enumerate(((3.6, 3.4), (5.2, 2.8), (6.6, 2.0))):
            m.loft_z("PaperTree", (z, x, y + 0.05 * k, w, 0.25), (z + 2.2, x, y + 0.05 * k, 0.1, 0.25))
    for x, w in ((-5.0, 7.0), (4.5, 8.0)):
        m.loft_z("PaperShade", (1.8, x, 6.6, w, 0.3), (4.0, x, 6.6, w * 0.3, 0.3))
    # The moon on its stick, rocking round the gutter.
    m.block("MoonStick", 0, -6.5, 11.2, 0.2, 0.2, 18.8)
    crescent(m, "Crescent", 0, -6.5, 22.2, 2.4, 0.4)
    # Paper bats circling the towers.
    for k in range(6):
        a = k * math.tau / 6 + rng.uniform(-0.2, 0.2)
        r = rng.uniform(9.0, 11.0)
        f = Frame(m, (math.cos(a) * r, math.sin(a) * r, rng.uniform(12.0, 19.0)), turn(z=a + math.pi / 2))
        f.box("Bats", 0, 0, 0, 0.5, 0.35, 0.6)
        for s in (-1, 1):
            f.box("Bats", 0, s * 0.18, 0.4, 0.14, 0.14, 0.3)
            f.box("Bats", 0, s * 0.75, 0.15, 0.7, 1.1, 0.08, turn(x=s * 0.35))
            f.box("Bats", 0, s * 1.5, 0.42, 0.5, 0.6, 0.08, turn(x=s * 0.75))
    limb(m, "Ribbon", [(0.6, 7.0, 1.85), (0.8, 8.4, 1.7), (1.0, 8.9, 0.25)], 0.6, 0.5)
    m.block("Front", 0, 10, 1, 0.2, 0.2, 0.2)
    return m


def spiral_stair(seed=16):
    """A landmark for the rims: a spiral stair climbing round a stone column to a landing with a glowing door
    that leads nowhere, violet glyphs winding up the column and books circling it all, rising and falling."""
    m = prop("SpiralStair", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Iron=IRON, Wood=WOOD, WoodDark=WOOD_DARK,
             DoorGlow="#b38cff", InkGlow=INK, OrbitA=COVER_A, OrbitB=COVER_C, OrbitPage=PAGE, Front="#ff00ff")
    rng = random.Random(seed)
    prism(m, "StoneDark", 0, 0, 0, 0.7, 5.6, 5.3, 12)
    prism(m, "Stone", 0, 0, 0.7, 1.0, 4.8, 4.8, 12)
    prism(m, "Stone", 0, 0, 1.0, 26.4, 0.95, 0.85, 8)
    posts = []
    for k in range(42):
        a = k * 0.42
        top = 1.0 + 0.6 * (k + 1)
        obox(m, "StoneLight" if k % 2 else "Stone", (math.cos(a) * 2.45, math.sin(a) * 2.45, top - 0.2), (3.3, 1.3, 0.4), turn(z=a))
        if k % 2 == 0:
            px, py = math.cos(a) * 3.95, math.sin(a) * 3.95
            m.block("Iron", px, py, top + 0.75, 0.16, 0.16, 1.5)
            posts.append((px, py, top + 1.5))
    for p, q in zip(posts, posts[1:]):
        beam(m, "Iron", p, q, 0.16)
    prism(m, "StoneLight", 0, 0, 26.2, 26.7, 3.2, 3.2, 12)
    for k in range(14):  # glyphs winding up the column
        a = math.pi / 8 + (k * 3 % 8) * math.pi / 4
        r = (0.95 - 0.1 * (1.5 + k * 1.6) / 25.4) * math.cos(math.pi / 8) + 0.07
        obox(m, "InkGlow", (math.cos(a) * r, math.sin(a) * r, 2.5 + k * 1.6), (0.32, 0.08, 0.55), turn(z=a + math.pi / 2))
    # The door to nowhere.
    for sx in (-1, 1):
        m.block("Wood", sx * 1.45, 0, 29.48, 0.5, 0.5, 5.6)
    m.block("WoodDark", 0, 0, 32.6, 3.6, 0.7, 0.6)
    m.block("DoorGlow", 0, 0, 29.5, 2.5, 0.2, 5.64)
    m.block("StoneDark", 0, 0, 26.73, 3.4, 1.2, 0.14)
    # Books circling it all.
    for k in range(6):
        a = k * math.tau / 6 + 0.4
        r = 6.6 + (k % 2) * 0.8
        book(m, "OrbitA" if k % 2 else "OrbitB", (math.cos(a) * r, math.sin(a) * r, 7 + k * 3.6), (0.9, 2.6, 3.4),
             turn(rng.uniform(-0.5, 0.5), rng.uniform(-0.6, 0.6), a + rng.uniform(-0.6, 0.6)), page="OrbitPage")
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


def sky_tome(seed=17):
    """A huge open book flying in the sky beyond the rims, its covers beating slowly like wings as it rises and
    sinks, glowing writing on the pages underneath and its ribbon trailing behind. The model starts high above
    the ground; its spine runs along Y, so it only has to face along the corridor."""
    m = prop("SkyTome", SkySpine=LEATHER_DARK, Headband=GILT, CoverL=LEATHER, CoverR=LEATHER, PageL=PAGE, PageR=PAGE, InkL=INK, InkR=INK,
             Ribbon=RIBBON, Front="#ff00ff")
    rng = random.Random(seed)
    zc = 46.0
    m.block("SkySpine", 0, 0, zc, 1.6, 14.4, 1.6)
    m.block("Headband", 0, 7.3, zc, 1.9, 0.4, 1.9)
    for s, side in ((-1, "L"), (1, "R")):
        f = Frame(m, (0, 0, zc), turn(y=-s * 0.3))
        f.box(f"Cover{side}", s * 7.6, 0, 0.4, 15.2, 14.0 if s < 0 else 13.9, 0.5)
        f.box(f"Page{side}", s * 7.3, 0, -0.35, 14.2, 13.0, 1.0)
        for k in range(7):
            y = -5.2 + k * 1.75
            x = s * rng.uniform(1.2, 2.0)
            while True:
                word = rng.uniform(0.8, 2.0)
                if abs(x) + word > 13.8:
                    break
                f.box(f"Ink{side}", x + s * word / 2, y, -0.86, word, 0.36, 0.08)
                x += s * (word + rng.uniform(0.4, 0.8))
    limb(m, "Ribbon", [(0.3, -7.0, zc - 0.6), (0.8, -9.5, zc - 2.5), (0.2, -12.0, zc - 3.5), (0.9, -14.5, zc - 5.5)], 0.7, 0.5)
    m.block("Front", 0, 10, zc, 0.2, 0.2, 0.2)
    return m


def ink_fall(seed=18):
    """A giant inkwell tipped over on the rim, its neck out over the corridor, pouring glowing ink down the wall
    into a pool on the floor, drops tumbling down it for ever, a cork and books beside it. Origin on the wall's
    top inner edge: rim z 0, floor z -44, +Y out into the corridor. The Front part tells the game which way it
    faces, then it goes."""
    m = prop("InkFall", InkBottle=BOTTLE, BottleLight=BOTTLE_LIGHT, Brass=BRASS, Page=PAGE, InkGlow=INK, Stream="#8a5cff",
             StreamDark="#4b2f99", Falling="#e2d4ff", WoodLight=WOOD_LIGHT, CoverA=COVER_A, CoverD=COVER_D, Gilt=GILT, Front="#ff00ff")
    rng = random.Random(seed)
    cz = 3.1
    tube(m, "BottleLight", (0, -10.7, cz), (0, -10.0, cz), 3.55)
    tube(m, "InkBottle", (0, -10.0, cz), (0, -2.5, cz), 3.4)
    tube(m, "InkBottle", (0, -2.5, cz), (0, 0.4, cz), 3.4, 1.6)
    tube(m, "InkBottle", (0, 0.4, cz), (0, 2.4, cz), 1.5)
    tube(m, "Brass", (0, 1.9, cz), (0, 2.7, cz), 1.8)
    tube(m, "Stream", (0, 2.68, cz), (0, 2.78, cz), 1.3)
    top = cz + 3.4 * math.cos(math.pi / 8)
    m.block("Page", 0, -6.0, top + 0.03, 2.4, 3.6, 0.1)
    for s in (-1, 1):
        obox(m, "InkGlow", (0, -6.0, top + 0.1), (2.6, 0.24, 0.06), turn(z=s * 0.9))
    # The ink: out of the mouth, over the edge, and down the wall in a curtain.
    m.block("Stream", 0, 3.5, 2.4, 2.2, 1.6, 1.6)
    m.block("Stream", 0, 4.4, 0.6, 2.6, 1.4, 2.6)
    z = -0.7
    while z > -43.5:
        length = min(rng.uniform(5, 8), z + 43.5)
        width = rng.uniform(2.6, 3.2)
        x = rng.uniform(-0.2, 0.2)
        m.block("Stream", x, 4.6, z - length / 2, width, 1.2, length)
        for side in (-1, 1):
            m.block("StreamDark", x + side * (width / 2 + 0.15), 4.45, z - length / 2, 0.45, 1.0, length * 0.9)
        z -= length
    # Drops that fall: rows four studs apart, so moving them down four studs and back loops seamlessly.
    for k, zz in enumerate(range(-2, -44, -4)):
        for x in (-0.8, 0.1, 0.9):
            jitter = ((k * 7 + int(x * 10)) % 3 - 1) * 0.12
            m.block("Falling", x + jitter, 5.35, zz - (1.3 if x > 0.5 else 0), 0.45, 0.3, 0.45)
    puddle(m, "Stream", ((0, 7.5, 10, 6), (0, 10.4, 6, 3.0), (-3.8, 8.6, 3.6, 4.4), (3.6, 8.4, 3.6, 4.0)), z=-43.75, thick=0.5)
    puddle(m, "StreamDark", ((0, 7.6, 11, 7.0),), z=-43.8, thick=0.36)
    for x, y, h in ((-1.2, 6.6, 1.6), (1.1, 7.0, 2.0), (0.0, 8.4, 1.2)):
        m.loft_z("Stream", (-43.5, x, y, 0.8, 0.8), (-43.5 + h, x, y, 0.2, 0.2))
    # A cork and a pile of books beside it.
    tube(m, "WoodLight", (4.2, -1.8, 0.7), (5.8, -2.9, 0.7), 0.75, 0.68)
    flat_book(m, "CoverA", -5.8, -4.0, 0, 4.4, 3.0, 1.1, 0.4, band="Gilt")
    flat_book(m, "CoverD", -5.6, -4.2, 1.1, 3.6, 2.6, 0.9, 0.1, band="Gilt")
    m.block("Front", 0, 6, -20, 0.2, 0.2, 0.2)
    return m


def book_arch(seed=19):
    """Books stacked into pillars on both rims and an arch of books across the corridor, rim to rim, ribbons
    hanging from it and an iron chandelier swinging slowly along the corridor under its crown. Modelled for the
    72-wide corridor (feet beyond 36 from the middle); MapDecor stretches it to the real width. All of it stays
    above the rim (z 0), clear of the flight camera."""
    m = prop("BookArch", CoverA=COVER_A, CoverB=COVER_B, CoverC=COVER_C, CoverD=COVER_D, CoverE=COVER_E, Page=PAGE, Gilt=GILT,
             Ribbon=RIBBON, Chain=IRON_LIGHT, Chandelier=IRON, Taper=WAX, Flame=FLAME, Front="#ff00ff")
    rng = random.Random(seed)
    covers = ("CoverA", "CoverB", "CoverC", "CoverD", "CoverE")
    for side in (-1, 1):
        z, k = 0.06, 0  # the spines and bands reach 0.05 below a book, so the stack starts just above the rim
        while z < 20.5:
            thick = rng.uniform(1.4, 2.2)
            flat_book(m, covers[(k + side) % 5], side * 41 + rng.uniform(-0.4, 0.4), rng.uniform(-0.3, 0.3), z, rng.uniform(8.4, 9.4),
                      rng.uniform(6.4, 7.2), thick, rng.uniform(-0.25, 0.25), band="Gilt")
            z += thick
            k += 1
    a_, b_, z0 = 40.0, 14.0, 20.5
    theta, k = 0.05, 0
    while True:
        speed = math.sqrt((a_ * math.sin(theta)) ** 2 + (b_ * math.cos(theta)) ** 2)
        t = rng.uniform(2.0, 3.0)
        mid = theta + t / 2 / speed
        if mid > math.pi - 0.05:
            break
        p = Vector((a_ * math.cos(mid), 0, z0 + b_ * math.sin(mid)))
        n = Vector((b_ * math.cos(mid), 0, a_ * math.sin(mid))).normalized()
        xd = Vector((n.z, 0, -n.x))
        rot = Matrix((xd, (0, 1, 0), n)).transposed()
        if k % 2:
            rot = rot @ turn(z=math.pi)
        h = rng.uniform(4.0, 5.4)
        book(m, covers[k % 5], tuple(p + n * (h / 2 - 0.2)), (t, rng.uniform(5.6, 6.6), h), rot, band="Gilt")
        if k % 6 == 3:  # a ribbon hanging from it
            limb(m, "Ribbon", [tuple(p + Vector((0, 1.2, 0))), tuple(p + Vector((0.3, 1.3, -2.0))), tuple(p + Vector((-0.2, 1.2, -4.2)))], 0.45, 0.35)
        theta += (t + 0.05) / speed
        k += 1
    # The chandelier, hung from the crown.
    hinge = z0 + b_
    for i in range(9):
        z = hinge - i * 0.6
        beam(m, "Chain", (0, 0, z), (0, 0, z - 0.6), *((0.34, 0.12) if i % 2 else (0.12, 0.34)))
    ring = hinge - 7.0
    ball(m, "Chandelier", 0, 0, hinge - 5.6, 0.6, 8, 4)
    prism(m, "Chandelier", 0, 0, ring - 1.6, hinge - 5.6, 0.15, 0.3, 6)
    ball(m, "Chandelier", 0, 0, ring - 1.8, 0.4, 6, 4)
    flat_ring(m, "Chandelier", 0, 0, ring, 3.2, 0.4, 0.35, 16)
    for k in range(4):
        a = k * math.tau / 4 + math.pi / 4
        beam(m, "Chandelier", (0, 0, hinge - 5.6), (math.cos(a) * 3.1, math.sin(a) * 3.1, ring + 0.1), 0.18)
    for k in range(8):
        a = k * math.tau / 8
        x, y = math.cos(a) * 3.2, math.sin(a) * 3.2
        disc(m, "Chandelier", x, y, ring + 0.25, 0.45, 0.15, 8)
        candle(m, x, y, ring + 0.32, rng.uniform(0.9, 1.4), 0.26, wax="Taper", flame="Flame", core=None, rng=rng, drips=1)
    m.block("Front", 0, 6, 34, 0.2, 0.2, 0.2)
    return m


ALL = [open_tome, book_stack, bookcase, candelabra, floating_candles, ink_well, hourglass, mimic_book, scroll_pile, spell_page,
       page_tree, leaning_shelves, chained_tome, clock_tower, popup_book, spiral_stair, sky_tome, ink_fall, book_arch]

# Where the props go: the same rules as Config/Decor's ForbiddenLibrary (keep the two in step). The map is 1300 long.
DECOR = dict(
    floor=dict(first=12, gap=(12, 22), side=(24, 34),
               props=[("prop_OpenTome", 14, (1.4, 1.8)), ("prop_BookStack", 12, (1.2, 1.6)), ("prop_Bookcase", 10, (1.1, 1.4)),
                      ("prop_Candelabra", 9, (1.2, 1.5)), ("prop_InkWell", 8, (1.2, 1.5)), ("prop_FloatingCandles", 8, (1.2, 1.5)),
                      ("prop_Hourglass", 6, (1.2, 1.4)), ("prop_MimicBook", 4, (1.2, 1.4))],
               extras=dict(chance=0.7, spread=8, props=[("prop_ScrollPile", 5, (0.9, 1.2)), ("prop_BookStack", 2, (0.6, 0.8)),
                                                         ("prop_FloatingCandles", 2, (0.7, 0.9))])),
    rim=dict(first=6, gap=(14, 24), chance=0.9, side=(64, 102),
             props=[("prop_PageTree", 6, (1.9, 2.5)), ("prop_BookStack", 3, (2.2, 2.8)), ("prop_LeaningShelves", 3, (1.6, 2.0)),
                    ("prop_ChainedTome", 3, (1.8, 2.2)), ("prop_FloatingCandles", 2, (2.0, 2.4)), ("prop_ScrollPile", 2, (2.2, 2.8))]),
    overhead=[("prop_BookArch", 250, 0, 1), ("prop_BookArch", 760, 0, 1.05), ("prop_BookArch", 1180, 0, 1)],
    walls=[("prop_InkFall", 80, 1), ("prop_InkFall", 240, -1), ("prop_InkFall", 420, 1), ("prop_InkFall", 600, -1),
           ("prop_InkFall", 780, 1), ("prop_InkFall", 960, -1), ("prop_InkFall", 1140, 1), ("prop_InkFall", 1270, -1)],
    spots=[("prop_ClockTower", 90, -86, "rim", 0, 1.4, "middle"), ("prop_ClockTower", 560, 86, "rim", 0, 1.5, "middle"),
           ("prop_ClockTower", 1040, -86, "rim", 0, 1.4, "middle"),
           ("prop_PopupBook", 200, 84, "rim", 0, 1.3, "middle"), ("prop_PopupBook", 690, -84, "rim", 0, 1.35, "middle"),
           ("prop_PopupBook", 1180, 84, "rim", 0, 1.3, "middle"),
           ("prop_SpiralStair", 370, -84, "rim", 0, 1.4, "middle"), ("prop_SpiralStair", 860, 84, "rim", 0, 1.5, "middle"),
           ("prop_SpiralStair", 1280, -84, "rim", 0, 1.4, "middle"),
           ("prop_SkyTome", 310, -165, "rim", 0, 2.2, "along"), ("prop_SkyTome", 970, 175, "rim", 0, 2.4, "along")]
          + [("prop_SpellPage", d, x, "floor", yaw, 1.2) for d, x, yaw in ((40, -3, 20), (150, 4, 140), (270, -4, 70), (380, 3, 200),
                                                                             (500, -2, 300), (610, 4, 40), (740, -3, 110), (850, 2, 250),
                                                                             (960, -4, 330), (1090, 3, 80), (1210, -2, 160))],
)


# ---------------------------------------------------------------------- light


def library_light(scene):
    """Night in the library for the renders: cool moonlight and a dusty violet fill, close to the game's
    Config/Lighting look for this world."""
    sun = bpy.data.objects["Sun"]
    sun.data.energy = 1.6
    sun.data.color = (0.82, 0.8, 1.0)
    sun.rotation_euler = (math.radians(-62), math.radians(25), math.radians(30))
    ambient = scene.world.node_tree.nodes["Background"]
    ambient.inputs["Color"].default_value = (0.62, 0.58, 0.85, 1)
    ambient.inputs["Strength"].default_value = 0.7


# ---------------------------------------------------------------------- scene and renders


def main(stills=True, videos=True):
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    props = bpy.data.collections.new("Props")
    stage = bpy.data.collections.new("Preview stage")
    for col in (props, stage):
        scene.collection.children.link(col)

    models = [make() for make in ALL]
    built = {}
    roots = []
    big = {"prop_ClockTower": (-75, -110, 0), "prop_PopupBook": (-42, -110, 0), "prop_SpiralStair": (-6, -110, 0),
           "prop_PageTree": (22, -110, 0), "prop_LeaningShelves": (44, -110, 0), "prop_SkyTome": (40, -200, 0),
           "prop_InkFall": (70, -110, 44), "prop_BookArch": (180, -170, 0)}
    x = 40
    for model in models:
        root = model.build(props)
        if model.name in big:
            root.location = big[model.name]
        else:
            root.location = (x, -40, 0)
            x += 13
        built[model.name] = root
        roots.append(root)
    row_middle = (40 + x - 13) / 2
    mk.light_up(roots, GLOW_ROLES)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-400, -500, -0.01), (500, -500, -0.01), (500, 200, -0.01), (-400, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", CORRIDOR["FloorA"], False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = mk.player_block(stage)
    stars = mk.star_dome(stage, count=160, colours=("#ffffff", "#e2d8ff"))
    bpy.context.view_layer.update()
    mk.set_sky(scene, SKY)
    library_light(scene)

    everything = roots + [player]
    if stills:
        for model, root in zip(models, roots):
            name = model.name
            if name == "prop_BookArch":
                mk.shoot_prop(scene, name, root, player, everything, (-0.15, 1.0, 0.25), 0.95, (1400, 700), 32)
            elif name == "prop_InkFall":
                mk.shoot_prop(scene, name, root, player, everything, (0.6, 1.0, 0.1), 0.9, (700, 900), 40)
            elif name == "prop_SkyTome":
                mk.shoot_prop(scene, name, root, player, everything, (0.5, 0.9, -0.15), 0.9, (700, 700), 50)
            elif name in ("prop_ClockTower", "prop_PopupBook", "prop_SpiralStair"):
                mk.shoot_prop(scene, name, root, player, everything, (0.55, 0.9, 0.35), 1.2, (700, 700), 50)
            else:
                mk.shoot_prop(scene, name, root, player, everything)
        player.location = (30, -40, 0)
        bpy.context.view_layer.update()
        small = [r for r in roots if mk.prop_of(r) not in big]
        mk.set_visible(everything, small + [player])
        kit.shoot(scene, "props", (row_middle, 34, 26), (row_middle, -40, 5), (1800, 700), 18)
        landmarks = [built[n] for n in ("prop_ClockTower", "prop_PopupBook", "prop_SpiralStair", "prop_PageTree", "prop_LeaningShelves")]
        mk.set_visible(everything, landmarks + [player])
        player.location = (-20, -96, 0)
        bpy.context.view_layer.update()
        kit.shoot(scene, "landmarks", (-16, -18, 30), (-16, -115, 14), (1800, 800), 22)

    if videos:  # close up on what moves
        names = ("prop_OpenTome", "prop_MimicBook", "prop_InkWell", "prop_Candelabra", "prop_FloatingCandles", "prop_Hourglass",
                 "prop_PageTree", "prop_ChainedTome", "prop_LeaningShelves", "prop_ClockTower", "prop_SkyTome")
        movers = [built[n] for n in names]
        mk.set_visible(everything, movers)
        saved = [(r, r.location.copy()) for r in movers]
        for k, root in enumerate(movers[:6]):
            root.location = (k * 13 - 32, 0, 0)
        for k, root in enumerate(movers[6:10]):
            root.location = ((k - 1.5) * 36, -45, 0)
        movers[10].location = (0, -150, -10)
        bpy.context.view_layer.update()
        entries = mk.motion_entries(movers, MOTION)
        mk.render_video(scene, RENDERS, "library_motion", 120, 15,
                        lambda f: ((0, 62, 30), (0, -20, 11), 28, lambda t: mk.apply_motion(entries, t)), (1600, 800))
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

        mk.render_video(scene, RENDERS, "library_flight", frames, 15, fly, (1600, 900))
        mk.reset_motion(entries)

    mk.clear([corridor, stars] + copies)
    mk.light_up(roots, GLOW_ROLES, 0)
    ground.hide_render = False
    for root in roots:
        for child in root.children:
            child.hide_render = False
    player.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "forbidden_library_models.blend"))
    print("saved", HERE / "forbidden_library_models.blend")
    for model in models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    # After "--": "stills" renders only the stills, "videos" only the videos; nothing, both.
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(stills=not args or "stills" in args, videos=not args or "videos" in args)
