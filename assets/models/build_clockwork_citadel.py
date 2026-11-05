"""Builds Clockwork Citadel's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_clockwork_citadel.py              (stills and videos)
    Blender -b -P build_clockwork_citadel.py -- stills    (stills only, quicker while modelling)

Saves clockwork_citadel_models.blend and renders to design/world/models_clockwork_citadel/: one still per prop,
the props together, the landmarks, a stretch of corridor, and two videos of what moves (clockwork_motion.mp4
close up, clockwork_flight.mp4 down the corridor at the flight camera's height).

Clockwork Citadel, map 12, the fourth of the mysterious, dark maps: a citadel that is one enormous machine, so old
its gears grew as big as houses. Whoever built it is long gone, but it never stopped: it winds itself in the dark,
every gear turning, pistons pounding, steam hissing out of its pipes and blue lightning crackling between its
coils, as if it's still building something nobody has seen. Night under a smoky steel-blue smog, and two lights
of its own: electric blue and furnace orange. A floor of bronze plates, walls of soot-black iron, and copper on
the rims, hanging over the walls like old copper roofing. Warm metal and cold smog after Midnight Carnival's teal,
crimson and gold. Its signature is the gear works: a great brass gear on an iron stand, meshing with a smaller
iron one that turns the other way, steam puffing beside them. Around it: steam hammers pounding a glowing ingot,
boilers with a furnace door and a gauge needle twitching, bundles of copper pipes with turning valve wheels,
giant brass metronomes, music boxes whose drum and key turn while a brass bird goes round on top, crackling spark
coils, and now and then a giant pocket watch lying open, its hands going round. Scrap piles as filler, and flat
floor gears turning in their plates across the middle. On the rims: smokestacks puffing, brass trees crowned with
a turning gear, wind-pump fan towers; landmarks: cog spires of stacked gears turning opposite ways under a
crackling orb, lightning towers arcing to their little coils, and engine houses with a huge flywheel and a
spinning governor. Airships hang in the smog beyond the island, their propellers turning. Crucibles tipped over
the wall tops pour glowing molten brass down into the corridor, and iron arches span it with three gears turning
along their crown.

No stud texture in this file: kit.PREVIEW_STUDS is off, so every material is a plain colour and the renders show
the models as they leave Blender. The studs come only in Studio, from the shared "Studs" MaterialVariant that
studio_tidy puts on every part except the glowing ones (docs/MAP_RECIPE.md step 8). The meshes still get the
usual box-projected UVs.

Gears that turn on their own middle (about="self") have an even number of teeth and spokes, so a part's bounding
box, whose middle the game turns it round, is centred on its axle. Meshing gears turn at the inverse ratio of
their teeth, so they stay in mesh (spins have no phase, in Blender and in the game).

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
from map_kit import ball, beam, disc, flat_ring, hoop, kit, limb, plate, prism, puddle  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "models_clockwork_citadel"

# Roles lit from inside. The game makes them Neon (shared/Roles.luau), so add new ones there too.
GLOW_ROLES = {"Volt", "Arc", "Spark", "Charge", "Furnace", "Molten", "Falling", "Dial", "Lamp", "Window", "Ember"}
kit.NO_STUDS.update(GLOW_ROLES)
mk.GLOW_STRENGTH = 1.8

# Shared colours, so every prop's metal, steam and light match.
BRASS, BRASS_DARK, BRASS_LIGHT = "#c99a3e", "#8c6528", "#e6c46c"
COPPER, COPPER_DARK = "#c26e3c", "#874726"
IRON, IRON_DARK, IRON_LIGHT = "#3d4352", "#272b36", "#5d6577"
STEEL = "#8d97a8"
RIVET = "#d9b55c"
BRICK, BRICK_DARK = "#7c4033", "#5a2c25"
SOOT = "#202329"
STEAM, STEAM_SHADE = "#e9eef3", "#c2cad5"
GLASS = "#2c3b55"
WOOD, WOOD_DARK = "#6e4b32", "#4b3222"
VOLT, ARC, SPARK = "#5cd6ff", "#c9f6ff", "#a6ecff"
FURNACE, MOLTEN, EMBER = "#ff7424", "#ffb236", "#ff9838"
DIAL, LAMP, WINDOW = "#fff0c6", "#ffc86e", "#ffb45a"

# The corridor's Clockwork Citadel colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#8a6436", "FloorB": "#7f5b31", "Dirt": "#343844", "DirtB": "#2d313c", "Grass": "#ba683c"}
SKY = "#121825"


def prop(name, **colours):
    return mk.prop(name, **colours)


# ---------------------------------------------------------------------- shape helpers


def turn(x=0.0, y=0.0, z=0.0):
    """A rotation (radians round X, then Y, then Z) as a 3x3 matrix."""
    return Euler((x, y, z), "XYZ").to_matrix()


UPRIGHT = turn(x=-math.pi / 2)  # a frame's flat XY plane stood up in the model's XZ plane, its +Z facing +Y
SIDEWAYS = turn(y=math.pi / 2)  # its flat XY plane stood up in the YZ plane, its +Z facing +X


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

    def prism(self, role, x, y, z0, z1, r0, r1=None, sides=8, turn_by=None):
        """An n-sided column along the frame's Z, from z0 to z1."""
        r1 = r0 if r1 is None else r1
        turn_by = math.pi / sides if turn_by is None else turn_by
        verts = []
        for z, r in ((z0, r0), (z1, r1)):
            for i in range(sides):
                a = turn_by + i * math.tau / sides
                verts.append(self.at(x + r * math.cos(a), y + r * math.sin(a), z))
        faces = [list(range(sides))[::-1], list(range(sides, 2 * sides))]
        faces += [[i, (i + 1) % sides, sides + (i + 1) % sides, sides + i] for i in range(sides)]
        self.m._add(role, verts, faces)


def tube(m, role, a, b, r0, r1=None, sides=8):
    """A round rod from a to b, radius r0 to r1: pipes, axles, a boiler on its side. Flat side down."""
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


def gear(m, role, centre, radius, teeth, thick, rot=None, spokes=6, hub_role=None, phase=0.0, tooth=None, rim=None):
    """A gear in the flat XY plane of rot (lying down without one; UPRIGHT stands it up facing Y): a toothed rim,
    spokes and a hub. radius is the pitch circle, the teeth reach tooth / 2 past it. With even teeth and spokes it
    is point-symmetric, so its bounding box is centred on its axle and about="self" turns it true. The teeth are a
    little thinner than the rim and the spokes thinner still, so no two faces lie in one plane. phase turns the
    teeth (a meshing gear needs a gap where the other's tooth comes in). hub_role draws the hub in another colour
    (it then doesn't turn with the gear, so only use it on gears that hold still or turn round the hub's axis)."""
    f = Frame(m, centre, rot)
    tooth = tooth or max(0.3, radius * 0.2)
    rim = rim or max(0.32, radius * 0.17)
    r_in = radius - tooth / 2
    r_mid = r_in - rim / 2
    n = max(12, teeth + teeth % 2)
    for i in range(n):
        a = phase + (i + 0.5) * math.tau / n
        seg = 2 * r_mid * math.sin(math.pi / n) + rim * 0.55
        f.box(role, math.cos(a) * r_mid, math.sin(a) * r_mid, 0, seg, rim, thick, turn(z=a + math.pi / 2))
    pitch = math.tau * radius / teeth
    for k in range(teeth):
        a = phase + k * math.tau / teeth
        r = r_in + tooth / 2 - 0.05
        f.box(role, math.cos(a) * r, math.sin(a) * r, 0, tooth + 0.1, pitch * 0.5, thick * 0.86, turn(z=a))
    hub = max(0.3, radius * 0.22)
    for j in range(spokes):
        a = phase + j * math.tau / spokes
        f.beam(role, (math.cos(a) * hub * 0.6, math.sin(a) * hub * 0.6, 0), (math.cos(a) * r_mid, math.sin(a) * r_mid, 0),
               min(rim * 0.7, thick * 0.8))
    f.prism(hub_role or role, 0, 0, -thick * 0.6, thick * 0.6, hub, hub, 8)


def bolt(m, role, a, b, kinks, width, rng, wild=0.6):
    """A lightning arc from a to b: a zigzag through `kinks` points pushed off the straight line."""
    a, b = Vector(a), Vector(b)
    along = b - a
    side = along.cross(Vector((0, 0, 1)))
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    up = side.cross(along.normalized())
    pts = [a]
    for k in range(1, kinks + 1):
        t = k / (kinks + 1)
        pts.append(a + along * t + side * rng.uniform(-wild, wild) + up * rng.uniform(-wild, wild) * 0.6)
    pts.append(b)
    for p, q in zip(pts, pts[1:]):
        beam(m, role, tuple(p), tuple(q), width)


def puffs(m, role, x, y, z0, count, gap, size, grow=0.12, shade=None):
    """A column of steam or smoke puffs, `gap` apart, each a little bigger than the one below. Moved up by `gap`
    over a period (fall = -gap) it rises for ever and loops: each puff only goes as far as where the next began.
    shade adds a darker puff tucked under each one, in that role."""
    for k in range(count):
        s = size * (1 + grow * k)
        z = z0 + gap * k
        m.block(role, x, y, z, s, s, s * 0.8)
        m.block(role, x + s * 0.28, y - s * 0.2, z + s * 0.25, s * 0.62, s * 0.62, s * 0.55)
        if shade:
            m.block(shade, x - s * 0.22, y + s * 0.18, z - s * 0.2, s * 0.7, s * 0.7, s * 0.5)


def rivet_ring(f, role, cx, cy, z, r, count, size=0.18):
    """Rivets round a circle in frame f's XY plane, at height z."""
    for k in range(count):
        a = (k + 0.5) * math.tau / count
        f.box(role, cx + math.cos(a) * r, cy + math.sin(a) * r, z, size, size, size)


def band(m, role, x, y, z, r, h, sides=12):
    """A riveted band round an upright drum or post: a ring a little proud of it."""
    prism(m, role, x, y, z - h / 2, z + h / 2, r, r, sides, math.pi / sides)


def gauge(m, x, y, z, r, face="Dial", rim="Brass", needle="Needle"):
    """A round pressure gauge on a +Y face: a brass rim, a glowing face and a needle hanging from the middle,
    standing at (x, y, z). The needle is its own role, so it can twitch round the gauge's middle."""
    disc(m, rim, x, y + 0.08, z, r, 0.16, 16, "xz")
    disc(m, face, x, y + 0.2, z, r * 0.8, 0.1, 16, "xz")
    for k in range(5):
        a = math.radians(-60 + k * 30)
        m.block("IronDark", x + math.sin(a) * r * 0.62, y + 0.27, z + math.cos(a) * r * 0.62, 0.08, 0.05, 0.16)
    m.block(needle, x, y + 0.31, z + r * 0.28, 0.08, 0.05, r * 0.62)
    disc(m, rim, x, y + 0.33, z, r * 0.14, 0.06, 8, "xz")


def handwheel(m, role, x, y, z, r, spokes=4, plane="xz"):
    """A valve's handwheel: a ring and spokes, upright facing Y (plane "xz") or lying flat ("xy"). Point-symmetric,
    so about="self" turns it true."""
    rot = UPRIGHT if plane == "xz" else None
    f = Frame(m, (x, y, z), rot)
    n = 12
    for i in range(n):
        a = (i + 0.5) * math.tau / n
        f.box(role, math.cos(a) * r, math.sin(a) * r, 0, 2 * r * math.sin(math.pi / n) + 0.1, 0.16, 0.16, turn(z=a + math.pi / 2))
    for j in range(spokes):
        a = j * math.tau / spokes
        f.beam(role, (0, 0, 0), (math.cos(a) * r, math.sin(a) * r, 0), 0.11)
    f.prism(role, 0, 0, -0.12, 0.12, 0.16, 0.16, 8)


def wheel(m, role, centre, radius, thick, rot=None, spokes=6, rim=None, hub_role=None):
    """A spoked wheel without teeth (flywheels), in the flat XY plane of rot. Point-symmetric like gear()."""
    f = Frame(m, centre, rot)
    rim = rim or max(0.4, radius * 0.16)
    r_mid = radius - rim / 2
    n = 20
    for i in range(n):
        a = (i + 0.5) * math.tau / n
        f.box(role, math.cos(a) * r_mid, math.sin(a) * r_mid, 0, 2 * r_mid * math.sin(math.pi / n) + rim * 0.5, rim, thick,
              turn(z=a + math.pi / 2))
    for j in range(spokes):
        a = j * math.tau / spokes
        f.beam(role, (0, 0, 0), (math.cos(a) * r_mid, math.sin(a) * r_mid, 0), min(rim * 0.6, thick * 0.7))
    f.prism(hub_role or role, 0, 0, -thick * 0.7, thick * 0.7, radius * 0.16, radius * 0.16, 8)


def rivet_row(m, role, a, b, count, size=0.2):
    """Rivets in a line from a to b."""
    a, b = Vector(a), Vector(b)
    for k in range(count):
        m.block(role, *(a.lerp(b, (k + 0.5) / count)), size, size, size)


# ---------------------------------------------------------------------- floor props


def gear_works(seed=1):
    """The map's signature: a great brass gear on an iron stand, meshing with a smaller iron gear on its own post
    that turns the other way twice as fast, a copper vent puffing steam beside them and a blue lamp crackling on
    the post. Both gears stand facing Y and turn on their own middles; the small one has a gap where the big one's
    tooth comes in, and 16 teeth to 8 means half the speed."""
    m = prop("GearWorks", IronDark=IRON_DARK, Iron=IRON, IronLight=IRON_LIGHT, Steel=STEEL, Rivet=RIVET, BrassDark=BRASS_DARK,
             GearA=BRASS, GearB=IRON_LIGHT, Copper=COPPER, CopperDark=COPPER_DARK, Steam=STEAM, Volt=VOLT)
    zc = 6.2
    m.block("IronDark", 1.6, 0, 0.3, 13.6, 5.2, 0.6)
    m.block("BrassDark", 1.6, 0, 0.66, 13.0, 4.6, 0.12)
    for x in (-4.6, 7.8):
        rivet_row(m, "Rivet", (x, -2.2, 0.66), (x, 2.2, 0.66), 5)
    # The big gear's stand: an A-frame each side of it, the axle through both.
    for y in (-1.15, 1.15):
        for sx in (-1, 1):
            beam(m, "Iron", (sx * 3.0, y, 0.7), (sx * 0.25, y, zc + 0.3), 0.7)
        m.block("Iron", 0, y, 2.6, 3.6, 0.5, 0.5)
        m.block("IronDark", 0, y, zc, 1.3, 0.6, 1.3)
    tube(m, "Steel", (0, -1.7, zc), (0, 1.7, zc), 0.36)
    gear(m, "GearA", (0, 0, zc), 4.0, 16, 0.9, UPRIGHT, spokes=6, tooth=0.6)
    # The small gear on its post behind it, its axle sticking out of the front.
    m.block("Iron", 6.0, -1.05, (0.66 + zc) / 2 + 1.2, 0.9, 0.7, zc + 1.8)
    m.block("IronDark", 6.0, -1.05, zc, 1.3, 0.8, 1.3)
    tube(m, "Steel", (6.0, -1.3, zc), (6.0, 0.9, zc), 0.28)
    gear(m, "GearB", (6.0, 0, zc), 2.0, 8, 0.8, UPRIGHT, spokes=4, phase=math.pi / 8, tooth=0.6)
    # The blue lamp on top of the post.
    m.block("IronDark", 6.0, -1.05, zc + 3.05, 1.2, 1.2, 0.3)
    prism(m, "Volt", 6.0, -1.05, zc + 3.2, zc + 4.3, 0.42, 0.42, 8)
    for k in range(4):
        a = k * math.tau / 4 + math.pi / 4
        m.block("IronDark", 6.0 + math.cos(a) * 0.48, -1.05 + math.sin(a) * 0.48, zc + 3.75, 0.12, 0.12, 1.1)
    prism(m, "IronDark", 6.0, -1.05, zc + 4.3, zc + 4.7, 0.6, 0.15, 8)
    # The steam vent: a copper pipe out of the plate, an elbow, a brass valve, and puffs rising off it.
    prism(m, "Copper", -4.0, 1.3, 0.5, 4.2, 0.45, 0.45, 8)
    for z in (1.4, 3.0):
        band(m, "CopperDark", -4.0, 1.3, z, 0.52, 0.22, 8)
    prism(m, "CopperDark", -4.0, 1.3, 4.2, 4.6, 0.6, 0.62, 8)
    puffs(m, "Steam", -4.0, 1.3, 5.3, 4, 1.2, 0.75)
    return m


def steam_hammer(seed=2):
    """A steam hammer in an iron gantry, pounding a glowing ingot on its anvil: the hammer head and its rod bob
    together (the rod's top stays hidden in the cylinder), a flywheel spins on the side and the cylinder puffs
    steam out of its exhaust."""
    m = prop("SteamHammer", IronDark=IRON_DARK, Iron=IRON, IronLight=IRON_LIGHT, Steel=STEEL, Rivet=RIVET, Brass=BRASS,
             BrassDark=BRASS_DARK, Copper=COPPER, Hammer=STEEL, HammerFace=IRON_DARK, Ember=EMBER, Flywheel=IRON_LIGHT, Steam=STEAM)
    m.block("IronDark", 0.8, 0, 0.25, 9.2, 5.0, 0.5)
    rivet_row(m, "Rivet", (-3.4, 2.2, 0.52), (5.0, 2.2, 0.52), 8)
    # The anvil and its ingot.
    m.loft_z("IronDark", (0.5, 0, 0, 2.2, 1.8), (1.4, 0, 0, 1.4, 1.2))
    m.block("Iron", 0, 0, 1.75, 2.6, 1.5, 0.7)
    m.loft_x("Iron", (1.3, 0, 1.85, 1.0, 0.5), (2.3, 0, 1.95, 0.2, 0.2))
    m.block("Ember", 0, 0, 2.27, 1.5, 0.8, 0.34)
    # The gantry: two posts and a beam, the cylinder on top.
    for sx in (-1, 1):
        m.block("Iron", sx * 2.7, 0, 4.85, 0.8, 1.3, 7.5)
        m.block("IronDark", sx * 2.7, 0, 0.9, 1.4, 1.9, 0.8)
        for z in (3.0, 6.0):
            m.block("Rivet", sx * 2.7, 0.7, z, 0.2, 0.12, 0.2)
    m.block("Iron", 0, 0, 9.1, 6.6, 1.5, 1.0)
    m.block("IronDark", 0, 0, 9.75, 7.0, 1.7, 0.3)
    prism(m, "Copper", 0, 0, 9.9, 12.3, 1.05, 1.05, 10)
    for z in (10.4, 11.8):
        band(m, "BrassDark", 0, 0, z, 1.12, 0.22, 10)
    prism(m, "Brass", 0, 0, 12.3, 12.7, 1.15, 0.6, 10)
    # The hammer: a rod and a heavy head with a darker striking face. Its lowest point (bob 0.6) meets the ingot.
    prism(m, "Hammer", 0, 0, 4.35, 10.9, 0.24, 0.24, 8)
    m.block("Hammer", 0, 0, 3.9, 2.0, 1.3, 1.5)
    m.block("HammerFace", 0, 0, 3.1, 1.8, 1.1, 0.2)
    m.block("Hammer", 0, 0, 4.85, 0.9, 0.9, 0.5)
    for sx in (-1, 1):  # guides the head runs in
        m.block("IronLight", sx * 2.2, 0, 3.8, 0.3, 0.6, 2.4)
    # The flywheel on its bracket, turning round its own middle.
    beam(m, "Iron", (4.3, -1.3, 0.5), (4.3, 0, 4.2), 0.5)
    beam(m, "Iron", (4.3, 1.3, 0.5), (4.3, 0, 4.2), 0.5)
    tube(m, "Steel", (3.1, 0, 4.2), (5.3, 0, 4.2), 0.25)
    wheel(m, "Flywheel", (4.9, 0, 4.2), 2.3, 0.45, SIDEWAYS, spokes=6)
    # The exhaust, puffing.
    beam(m, "Copper", (0.7, 0.5, 12.0), (1.5, 0.5, 12.9), 0.4)
    prism(m, "Copper", 1.5, 0.5, 12.8, 13.3, 0.32, 0.4, 8)
    puffs(m, "Steam", 1.5, 0.5, 14.0, 4, 1.0, 0.6)
    return m


def spark_coil(seed=3):
    """A spark coil: a copper winding on a stack of insulators, a brass ring on top and an orb of blue light
    that lightning keeps arcing out of, a ring of sparks racing round it, and a little spark gap crackling at its
    foot."""
    m = prop("SparkCoil", IronDark=IRON_DARK, Iron=IRON, Brass=BRASS, BrassDark=BRASS_DARK, Rivet=RIVET, Insulator="#e6e0d2",
             Copper=COPPER, CopperDark=COPPER_DARK, Volt=VOLT, Arc=ARC, Charge=SPARK)
    rng = random.Random(seed)
    prism(m, "IronDark", 0, 0, 0, 0.8, 2.6, 2.2, 12)
    band(m, "BrassDark", 0, 0, 0.85, 2.0, 0.1, 12)
    for k in range(4):  # the insulator stack
        prism(m, "Insulator", 0, 0, 0.9 + k * 0.42, 1.25 + k * 0.42, 0.95, 0.95, 10)
        prism(m, "Iron", 0, 0, 1.25 + k * 0.42, 1.32 + k * 0.42, 0.55, 0.55, 10)
    prism(m, "Copper", 0, 0, 2.6, 8.5, 0.85, 0.75, 12)
    z = 2.85
    while z < 8.3:
        band(m, "CopperDark", 0, 0, z, 0.86 - (z - 2.6) * 0.016, 0.12, 12)
        z += 0.32
    prism(m, "BrassDark", 0, 0, 8.5, 8.8, 0.9, 0.9, 12)
    flat_ring(m, "Brass", 0, 0, 9.05, 1.45, 0.8, 0.6, 16)
    prism(m, "Brass", 0, 0, 8.8, 9.7, 0.4, 0.4, 8)
    ball(m, "Volt", 0, 0, 10.25, 0.85, 10, 6)
    for k in range(5):  # lightning out of the orb
        a = k * math.tau / 5 + rng.uniform(-0.3, 0.3)
        r = rng.uniform(2.6, 3.6)
        bolt(m, "Arc", (math.cos(a) * 0.7, math.sin(a) * 0.7, 10.3), (math.cos(a) * r, math.sin(a) * r, rng.uniform(7.6, 11.2)), 3, 0.16, rng, 0.45)
    for k in range(8):  # the ring of sparks
        a = k * math.tau / 8
        m.block("Charge", math.cos(a) * 2.45, math.sin(a) * 2.45, 9.05 + (0.25 if k % 2 else -0.25), 0.3, 0.3, 0.3)
    # A spark gap at its foot: two brass balls on posts, a little arc between them.
    for sx in (-1, 1):
        prism(m, "Iron", sx * 1.5, 2.3, 0, 1.9, 0.16, 0.14, 6)
        ball(m, "Brass", sx * 1.5, 2.3, 2.1, 0.32, 8, 4)
    bolt(m, "Arc", (-1.2, 2.3, 2.1), (1.2, 2.3, 2.1), 3, 0.12, rng, 0.25)
    prism(m, "IronDark", 0, 2.3, 0, 0.3, 2.1, 2.1, 4, math.pi / 4)
    return m


def boiler(seed=4):
    """A riveted boiler lying on iron cradles, a firebox at one end with its furnace door glowing, a chimney
    smoking, a safety valve puffing steam, and a pressure gauge on top whose needle twitches. The gauge's middle is
    straight above the origin, so its needle swings round it."""
    m = prop("Boiler", IronDark=IRON_DARK, Iron=IRON, IronLight=IRON_LIGHT, Rivet=RIVET, Brass=BRASS, BrassDark=BRASS_DARK,
             Copper=COPPER, CopperDark=COPPER_DARK, Furnace=FURNACE, Dial=DIAL, Needle="#b8262a", Steam=STEAM, Smoke="#5a5e68",
             SmokeLight="#7c818c", Soot=SOOT)
    zc = 3.0
    for x in (-2.0, 2.0):  # cradles
        m.loft_z("IronDark", (0, x, 0, 1.0, 4.4), (1.6, x, 0, 0.8, 3.6))
    tube(m, "Copper", (-3.4, 0, zc), (3.6, 0, zc), 2.2, 2.2, 14)
    tube(m, "CopperDark", (3.6, 0, zc), (4.0, 0, zc), 2.0, 1.4, 14)
    for x in (-2.6, -0.9, 0.8, 2.5):
        tube(m, "BrassDark", (x - 0.15, 0, zc), (x + 0.15, 0, zc), 2.3, 2.3, 14)
    for x in (-1.75, 1.65):
        for k in range(10):
            a = (k + 0.5) * math.tau / 10
            m.block("Rivet", x, math.cos(a) * 2.2, zc + math.sin(a) * 2.2, 0.2, 0.2, 0.2)
    # The firebox, its door and the chimney.
    m.block("IronDark", -4.9, 0, 2.3, 2.8, 4.0, 4.6)
    m.block("Iron", -4.9, 0, 4.75, 3.1, 4.3, 0.3)
    m.block("Soot", -4.9, 2.02, 1.9, 2.0, 0.08, 1.8)
    m.block("Furnace", -4.9, 2.06, 1.9, 1.6, 0.06, 1.4)
    for x in (-5.4, -4.9, -4.4):
        m.block("Iron", x, 2.12, 1.9, 0.14, 0.1, 1.6)
    m.block("Iron", -4.9, 2.12, 2.75, 2.1, 0.12, 0.25)
    prism(m, "Iron", -4.9, -0.6, 4.9, 10.0, 0.62, 0.55, 10)
    for z in (6.4, 8.4):
        band(m, "IronDark", -4.9, -0.6, z, 0.64, 0.2, 10)
    prism(m, "IronDark", -4.9, -0.6, 10.0, 10.5, 0.62, 0.95, 10)
    puffs(m, "Smoke", -4.9, -0.6, 11.4, 4, 1.5, 1.0, shade="SmokeLight")
    # The safety valve, puffing.
    prism(m, "Brass", 2.2, 0, zc + 2.0, zc + 3.2, 0.3, 0.3, 8)
    prism(m, "BrassDark", 2.2, 0, zc + 3.2, zc + 3.5, 0.5, 0.5, 8)
    puffs(m, "Steam", 2.2, 0, zc + 4.3, 4, 1.2, 0.7)
    # The gauge on a pipe, straight above the origin.
    prism(m, "Brass", 0, 0, zc + 2.0, zc + 3.6, 0.22, 0.22, 8)
    m.block("BrassDark", 0, 0, zc + 3.8, 0.5, 0.5, 0.5)
    gauge(m, 0, 0.2, zc + 4.6, 0.95)
    return m


def steam_pipes(seed=5):
    """A bundle of copper pipes of all heights rising out of an iron manifold, banded in brass, two of them
    puffing steam, two red valve wheels turning on their own, and a gauge on the manifold twitching. The gauge's
    middle is straight above the origin."""
    m = prop("SteamPipes", IronDark=IRON_DARK, Iron=IRON, Rivet=RIVET, Copper=COPPER, CopperDark=COPPER_DARK, Brass=BRASS,
             BrassDark=BRASS_DARK, ValveA="#b8262a", ValveB="#b8262a", Dial=DIAL, Needle="#b8262a", Steam=STEAM)
    m.block("IronDark", 0, 0, 0.35, 7.6, 3.2, 0.7)
    m.block("Iron", 0, 0, 1.35, 7.0, 2.4, 1.3)
    rivet_row(m, "Rivet", (-3.3, 1.22, 1.85), (3.3, 1.22, 1.85), 12, 0.16)
    pipes = [(-2.8, 0.2, 7.0, 0.5), (-1.7, -0.35, 10.0, 0.6), (-0.55, 0.3, 8.2, 0.5), (0.6, -0.25, 11.6, 0.62),
             (1.75, 0.3, 6.6, 0.48), (2.8, -0.2, 9.2, 0.55)]
    for x, y, h, r in pipes:
        prism(m, "Copper", x, y, 1.9, h, r, r, 10)
        for z in (3.1, h - 1.4):
            band(m, "BrassDark", x, y, z, r + 0.07, 0.24, 10)
        prism(m, "CopperDark", x, y, h, h + 0.35, r * 1.25, r * 1.25, 10)
    for k in (1, 3):
        x, y, h, r = pipes[k]
        puffs(m, "Steam", x, y, h + 1.1, 4, 1.2, 0.8)
    tube(m, "Copper", (-2.8, 0.2, 5.4), (-0.55, 0.3, 5.4), 0.3)  # a cross pipe
    tube(m, "Copper", (1.75, 0.3, 4.6), (2.8, -0.2, 4.6), 0.28)
    # The valves: brass stubs out of the front, a red wheel on each.
    tube(m, "Brass", (-2.8, 0.2, 3.7), (-2.8, 1.45, 3.7), 0.22)
    handwheel(m, "ValveA", -2.8, 1.6, 3.7, 0.7)
    tube(m, "Brass", (2.8, -0.2, 4.0), (2.8, 1.45, 4.0), 0.22)
    handwheel(m, "ValveB", 2.8, 1.6, 4.0, 0.8)
    gauge(m, 0, 1.2, 1.35, 0.55)
    return m


def metronome(seed=6):
    """A giant brass-and-walnut metronome ticking away: its arm swings from a pivot low on its front, the brass
    weight riding on it, and the wind-up key in its side turns. The pivot is straight above the origin."""
    m = prop("Metronome", Wood=WOOD, WoodDark=WOOD_DARK, Brass=BRASS, BrassDark=BRASS_DARK, BrassLight=BRASS_LIGHT, Arm=STEEL,
             ArmWeight=BRASS_LIGHT, Key=BRASS)
    m.block("BrassDark", 0, 0, 0.4, 5.8, 3.9, 0.8)
    m.block("Brass", 0, 0, 0.9, 5.2, 3.4, 0.2)
    m.loft_z("Wood", (1.0, 0, 0, 4.4, 2.6), (9.2, 0, 0, 1.3, 2.0))
    m.loft_z("WoodDark", (2.0, 0, 1.2, 2.0, 0.3), (8.4, 0, 0.98, 0.6, 0.3))  # the recess the arm swings over
    for k in range(9):  # gilt ticks up the recess
        z = 3.0 + k * 0.6
        y = 1.35 - (z - 2.0) / 6.4 * 0.22 + 0.03
        m.block("BrassLight", 0, y, z, 0.9 - k * 0.05 if k % 2 else 0.5, 0.06, 0.1)
    m.block("BrassDark", 0, 0, 9.4, 1.6, 2.3, 0.4)
    m.loft_z("Brass", (9.6, 0, 0, 1.4, 2.1), (10.8, 0, 0, 0.2, 0.2))
    ball(m, "BrassLight", 0, 0, 11.0, 0.3, 8, 4)
    # The arm and its weight, in front of the recess; the pivot cap.
    zp = 1.8
    m.block("Arm", 0, 1.62, zp + 4.1, 0.22, 0.14, 8.6)
    m.block("ArmWeight", 0, 1.62, 7.0, 0.9, 0.32, 0.9)
    m.block("ArmWeight", 0, 1.62, 7.55, 0.5, 0.32, 0.2)
    disc(m, "Brass", 0, 1.78, zp, 0.36, 0.14, 10, "xz")
    # The wind-up key in its right side: a stem and a bow of two lobes, point-symmetric round the stem.
    tube(m, "Key", (1.4, 0, 4.0), (2.9, 0, 4.0), 0.18)
    for s in (-1, 1):
        m.block("Key", 3.0, 0, 4.0 + s * 0.7, 0.26, 1.1, 0.9)
    m.block("Key", 3.0, 0, 4.0, 0.3, 0.5, 0.7)
    return m


def music_box(seed=7):
    """A giant music box with its lid open and a mirror inside it: its pinned drum turns past the steel comb,
    the key in its side turns, and on a turntable over the works a little brass bird goes round and round. The
    turntable is straight above the origin."""
    m = prop("MusicBox", Wood=WOOD, WoodDark=WOOD_DARK, Brass=BRASS, BrassDark=BRASS_DARK, Velvet="#6e2438", Glass="#9fb3c8",
             Steel=STEEL, Drum=BRASS_LIGHT, Key=BRASS, Turntable=BRASS_DARK, Bird=BRASS_LIGHT, BirdEye=IRON_DARK)
    x0, x1, y0, y1, top = -5.0, 3.4, -2.7, 2.7, 3.3
    cx, w = (x0 + x1) / 2, x1 - x0
    m.block("WoodDark", cx, 0, 0.25, w + 0.3, 5.7, 0.5)
    m.block("Velvet", cx, 0, 0.55, w - 0.5, 4.9, 0.18)
    for y in (y0 + 0.15, y1 - 0.15):
        m.block("Wood", cx, y, (0.5 + top) / 2, w, 0.3, top - 0.5)
    for x in (x0 + 0.15, x1 - 0.15):
        m.block("Wood", x, 0, (0.5 + top) / 2, 0.3, y1 - y0 - 0.6, top - 0.5)
    for x in (x0, x1):
        for y in (y0, y1):
            m.block("Brass", x, y, top - 0.1, 0.62, 0.62, 0.32)
            m.block("Brass", x, y, 0.62, 0.62, 0.62, 0.32)
    m.block("Brass", cx, y1 + 0.04, 1.9, 2.6, 0.1, 0.5)  # a name plate
    # The lid, open and leaning back on its hinge, the mirror on its inside.
    f = Frame(m, (cx, y0, top), turn(x=math.radians(100)))
    f.box("Wood", 0, 2.75, 0.18, w, 5.5, 0.36)
    f.box("Glass", 0, 2.75, -0.04, w - 1.4, 4.4, 0.1)
    for dx, dy, bw, bd in ((0, 0.45, w - 1.0, 0.3), (0, 5.05, w - 1.0, 0.3), (-(w - 1.3) / 2, 2.75, 0.3, 4.6), ((w - 1.3) / 2, 2.75, 0.3, 4.6)):
        f.box("Brass", dx, dy, -0.06, bw, bd, 0.12)
    # The drum on its brackets, pins in pairs round it, and the comb.
    yd, zd = -1.1, 2.0
    for x in (-4.4, -1.0):
        m.block("BrassDark", x, yd, (0.6 + zd) / 2, 0.3, 0.6, zd - 0.6 + 0.3)
    tube(m, "Steel", (-4.5, yd, zd), (-0.9, yd, zd), 0.16)
    tube(m, "Drum", (-4.1, yd, zd), (-1.3, yd, zd), 0.8, 0.8, 12)
    rng = random.Random(seed)
    for k in range(12):
        x = -3.9 + k * 0.22
        a = rng.uniform(0, math.pi)
        for b in (a, a + math.pi):
            m.block("Drum", x, yd + math.cos(b) * 0.86, zd + math.sin(b) * 0.86, 0.1, 0.14, 0.14)
    m.block("Steel", -2.7, 0.55, 1.5, 3.2, 0.7, 0.5)
    for k in range(11):
        m.block("Steel", -4.0 + k * 0.26, 0.05, 1.95, 0.16, 0.9, 0.06)
    # The cover over the works, the pillar and the turntable with its bird.
    m.block("Brass", 1.25, 0, top - 0.3, 3.7, 4.9, 0.2)
    prism(m, "BrassDark", 0, 0, top - 0.2, 4.0, 0.3, 0.3, 8)
    disc(m, "Turntable", 0, 0, 4.08, 1.5, 0.16, 16)
    flat_ring(m, "Turntable", 0, 0, 4.2, 1.35, 0.2, 0.1, 16)
    bx, bz = 0.75, 4.75
    ball(m, "Bird", bx, 0, bz, 0.45, 8, 5)
    ball(m, "Bird", bx, 0.42, bz + 0.45, 0.3, 8, 4)
    m.loft_y("Bird", (0.66, bx, bz + 0.45, 0.2, 0.16), (0.95, bx, bz + 0.42, 0.04, 0.04))
    plate(m, "Bird", (bx, -0.3, bz + 0.05), (bx, -1.1, bz + 0.45), (1, 0, 0), 0.4, 0.7, 0.06)
    for s in (-1, 1):
        plate(m, "Bird", (bx + s * 0.3, 0.15, bz + 0.1), (bx + s * 0.55, -0.55, bz + 0.2), (0, 0, 1), 0.5, 0.25, 0.06)
        m.block("BirdEye", bx + s * 0.18, 0.62, bz + 0.52, 0.06, 0.1, 0.1)
    m.block("Bird", bx, 0, bz - 0.55, 0.12, 0.12, 0.3)  # its leg
    # The key in the right side.
    tube(m, "Key", (x1, 0, 1.8), (x1 + 1.3, 0, 1.8), 0.2)
    for s in (-1, 1):
        m.block("Key", x1 + 1.4, 0, 1.8 + s * 0.75, 0.28, 1.2, 0.95)
    m.block("Key", x1 + 1.4, 0, 1.8, 0.32, 0.55, 0.7)
    return m


def pocket_watch(seed=8):
    """A rare find: a giant pocket watch lying open on its back, its face glowing, its hands going round, a little
    gear turning in a window of its face, the lid standing open behind it and its chain trailing off across the
    floor. The face is straight above the origin, so the hands turn round its middle."""
    m = prop("PocketWatch", Brass=BRASS, BrassDark=BRASS_DARK, BrassLight=BRASS_LIGHT, IronDark=IRON_DARK, Dial="#f4e4bc",
             MinuteHand=IRON_DARK, HourHand=IRON_DARK, GearA=BRASS_LIGHT, Chain=BRASS)
    prism(m, "BrassDark", 0, 0, 0, 0.35, 4.0, 4.3, 24)
    prism(m, "Brass", 0, 0, 0.35, 1.0, 4.3, 4.3, 24)
    disc(m, "Dial", 0, 0, 0.98, 3.75, 0.1, 24)
    flat_ring(m, "BrassLight", 0, 0, 1.06, 3.95, 0.5, 0.18, 24)
    for k in range(12):
        a = k * math.tau / 12
        big = k % 3 == 0
        obox(m, "IronDark", (math.sin(a) * 3.2, math.cos(a) * 3.2, 1.05), (0.26 if big else 0.16, 0.7 if big else 0.42, 0.06), turn(z=-a))
    # A window in the face, a gear turning in it.
    disc(m, "IronDark", 1.5, -1.4, 1.04, 1.05, 0.04, 16)
    flat_ring(m, "BrassDark", 1.5, -1.4, 1.07, 1.12, 0.16, 0.08, 16)
    gear(m, "GearA", (1.5, -1.4, 1.1), 0.75, 8, 0.08, spokes=4, tooth=0.24)
    # The hands and the cap over them.
    m.block("HourHand", 0, 0.9, 1.21, 0.38, 2.2, 0.07)
    m.loft_y("HourHand", (1.95, 0, 1.21, 0.7, 0.07), (2.55, 0, 1.21, 0.05, 0.07))
    m.block("MinuteHand", 0, 1.45, 1.28, 0.24, 3.5, 0.06)
    prism(m, "Brass", 0, 0, 1.0, 1.4, 0.32, 0.32, 10)
    # The crown and bow at twelve o'clock, the chain trailing off.
    tube(m, "BrassDark", (0, 4.2, 0.6), (0, 4.95, 0.6), 0.45)
    tube(m, "Brass", (0, 4.95, 0.6), (0, 5.5, 0.6), 0.62, 0.62, 12)
    flat_ring(m, "Brass", 0, 6.5, 0.55, 1.0, 0.36, 0.36, 12)
    pts = [Vector((math.sin(t * 2.4) * 1.6 + t * 1.2, 7.5 + t * 3.0, 0.16)) for t in (i / 13 for i in range(14))]
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        beam(m, "Chain", tuple(p), tuple(q), *((0.4, 0.14) if i % 2 else (0.14, 0.32)))
    # The lid, open and leaning back on its hinge, engraved on the inside.
    tube(m, "BrassDark", (-0.9, -4.35, 0.7), (0.9, -4.35, 0.7), 0.32)
    f = Frame(m, (0, -4.35, 0.7), turn(x=math.radians(108)))
    f.prism("Brass", 0, 4.3, -0.18, 0.18, 4.3, 4.3, 24)
    f.prism("BrassLight", 0, 4.3, -0.26, -0.17, 3.3, 3.3, 24)
    gear(m, "BrassDark", f.at(0, 4.3, -0.32), 2.3, 16, 0.1, f.r, spokes=6, tooth=0.5)  # a gear engraved inside it
    return m


def scrap_pile(seed=9):
    """Filler: a heap of scrap, loose gears, nuts, bolts, a spring and an oil can, with one broken gear still
    standing on its edge on a bolt and turning, and a snapped wire spitting blue sparks."""
    m = prop("ScrapPile", IronDark=IRON_DARK, Iron=IRON, IronLight=IRON_LIGHT, Brass=BRASS, BrassDark=BRASS_DARK, Copper=COPPER,
             CopperDark=COPPER_DARK, Steel=STEEL, Spring=STEEL, GearA=BRASS, Spark=SPARK)
    rng = random.Random(seed)
    m.loft_z("IronDark", (0, 0, 0, 5.2, 4.4), (0.5, 0.1, 0, 4.4, 3.6))
    gear(m, "BrassDark", (-1.1, 0.6, 0.75), 1.6, 12, 0.3, turn(x=0.12, y=-0.1), spokes=4)
    gear(m, "Iron", (1.0, -0.9, 0.7), 1.2, 8, 0.3, turn(x=-0.2, y=0.15), spokes=4)
    gear(m, "IronLight", (-0.3, -0.2, 1.25), 1.0, 8, 0.25, turn(x=0.35, z=0.4), spokes=4)
    for x, y, z in ((1.7, 1.1, 0.5), (-2.2, -1.2, 0.5), (0.2, 1.6, 0.6), (2.3, -1.9, 0.0)):
        prism(m, "Steel", x, y, z, z + 0.35, 0.42, 0.42, 6, rng.uniform(0, 1))
        prism(m, "IronDark", x, y, z + 0.35, z + 0.37, 0.18, 0.18, 6)
    for a, b in (((-2.6, 0.9, 0.62), (-1.2, 2.0, 0.85)), ((0.8, 1.9, 0.58), (2.4, 1.2, 0.6))):
        tube(m, "Steel", a, b, 0.14)
        prism(m, "Steel", a[0], a[1], a[2] - 0.2, a[2] + 0.2, 0.3, 0.3, 6)
    for k in range(18):  # a spring lying on the heap
        t = k / 17
        a = t * math.tau * 4
        p = (-2.4 + math.cos(a) * 0.45, -0.5 + t * 1.6, 0.95 + math.sin(a) * 0.45)
        m.block("Spring", *p, 0.18, 0.2, 0.18)
    prism(m, "Copper", 2.5, 0.2, 0.4, 1.4, 0.55, 0.45, 10)  # the oil can
    prism(m, "CopperDark", 2.5, 0.2, 1.4, 1.7, 0.45, 0.15, 10)
    beam(m, "CopperDark", (2.5, 0.2, 1.55), (3.4, 0.6, 2.1), 0.14, None, 0.08)
    # The broken gear on its bolt, turning on its own middle.
    m.block("IronDark", 0.6, 0.4, 1.0, 0.5, 0.5, 1.6)
    tube(m, "Steel", (0.6, 0.15, 1.75), (0.6, 0.95, 1.75), 0.14)
    gear(m, "GearA", (0.6, 0.62, 1.75), 1.15, 8, 0.22, UPRIGHT, spokes=4)
    # The snapped wire and its sparks.
    limb(m, "Copper", [(-1.8, -1.6, 0.5), (-1.6, -1.9, 1.3), (-1.2, -1.8, 1.9)], 0.14, 0.1)
    for p in ((-1.1, -1.8, 2.05), (-0.9, -1.6, 2.2), (-1.3, -2.0, 2.3), (-0.95, -2.05, 1.85)):
        m.block("Spark", *p, 0.14, 0.14, 0.14)
    return m


def floor_gears(seed=10):
    """A flat iron plate set into the floor with two gears lying in it, meshing and turning opposite ways, blue
    light glowing in the grooves round its edge. Flat (under half a stud), so it can lie where the eggs land.
    20 teeth to 12, so the small one turns 20/12 as fast."""
    m = prop("FloorGears", IronDark=IRON_DARK, Iron=IRON, Rivet=RIVET, Brass=BRASS_DARK, GearA=BRASS, GearB=COPPER, Volt=VOLT)
    m.block("IronDark", 0, 0, 0.05, 13, 13, 0.1)
    for s in (-1, 1):
        m.block("Iron", 0, s * 6.15, 0.1, 12.8, 0.6, 0.1)
        m.block("Iron", s * 6.15, 0, 0.1, 0.6, 11.7, 0.1)
        for k in range(7):
            t = -5.4 + k * 1.8
            m.block("Rivet", t, s * 6.2, 0.18, 0.16, 0.16, 0.12)
            m.block("Rivet", s * 6.2, t, 0.18, 0.16, 0.16, 0.12)
        m.block("Volt", 0, s * 5.5, 0.11, 11.2, 0.22, 0.04)
        m.block("Volt", s * 5.5, 0, 0.11, 0.22, 10.78, 0.04)
    ax, ay = -1.2, 0.9
    bx, by = ax + 4.8 * math.cos(math.radians(-40)), ay + 4.8 * math.sin(math.radians(-40))
    for x, y in ((ax, ay), (bx, by)):
        disc(m, "Brass", x, y, 0.13, 0.7, 0.06, 10)
    gear(m, "GearA", (ax, ay, 0.22), 3.0, 20, 0.12, spokes=6, phase=math.radians(-40), tooth=0.5)
    gear(m, "GearB", (bx, by, 0.22), 1.8, 12, 0.12, spokes=4, phase=math.radians(155), tooth=0.5)
    return m


# ---------------------------------------------------------------------- rim props and landmarks


def smokestack(seed=11):
    """A rim prop: a tall banded brick chimney, its mouth glowing, smoke rolling out of it for ever, an iron
    ladder up its side and a furnace door glowing at its foot."""
    m = prop("Smokestack", Brick=BRICK, BrickDark=BRICK_DARK, IronDark=IRON_DARK, Iron=IRON, Rivet=RIVET, Furnace=FURNACE, Soot=SOOT,
             Ember=EMBER, Smoke="#4f535c", SmokeLight="#737884")
    m.block("BrickDark", 0, 0, 1.5, 5.0, 5.0, 3.0)
    m.block("IronDark", 0, 0, 3.15, 5.3, 5.3, 0.3)
    z0, z1, w0, w1 = 3.3, 14.0, 3.8, 2.8
    rows = 6
    for k in range(rows):  # courses of two bricks' colours, banded in iron
        za, zb = z0 + (z1 - z0) * k / rows, z0 + (z1 - z0) * (k + 1) / rows
        wa, wb = w0 + (w1 - w0) * k / rows, w0 + (w1 - w0) * (k + 1) / rows
        m.loft_z("Brick" if k % 2 == 0 else "BrickDark", (za, 0, 0, wa, wa), (zb, 0, 0, wb, wb))
        if k:
            m.block("IronDark", 0, 0, za, wa + 0.2, wa + 0.2, 0.3)
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):  # rivets on the bands' corners
        for k in range(1, rows):
            za = z0 + (z1 - z0) * k / rows
            wa = w0 + (w1 - w0) * k / rows
            m.block("Rivet", sx * (wa / 2 + 0.1), sy * (wa / 2 + 0.1), za, 0.22, 0.22, 0.22)
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):  # the crown: a flared iron lip round the glowing mouth
        w = 3.5 if sx == 0 else 0.45
        d = 0.45 if sx == 0 else 3.5
        m.loft_z("IronDark", (z1, sx * 1.15, sy * 1.15, w * 0.85, d * 0.85 if sx else d), (z1 + 0.9, sx * 1.5, sy * 1.5, w, d))
    m.block("Ember", 0, 0, z1 + 0.5, 2.3, 2.3, 0.2)
    puffs(m, "Smoke", 0, 0, z1 + 2.4, 5, 2.2, 1.9, grow=0.15, shade="SmokeLight")
    # The furnace door at its foot and the ladder up its side.
    m.block("Soot", 0, 2.52, 1.3, 2.0, 0.08, 1.8)
    m.block("Furnace", 0, 2.56, 1.2, 1.5, 0.06, 1.3)
    for x in (-0.45, 0.0, 0.45):
        m.block("Iron", x, 2.62, 1.2, 0.14, 0.1, 1.5)
    for y in (-0.6, 0.6):
        beam(m, "Iron", (2.65, y, 3.4), (2.15, y, 13.6), 0.14)
    for k in range(14):
        z = 3.9 + k * 0.7
        x = 2.65 - (z - 3.4) / 10.2 * 0.5
        m.block("Iron", x, 0, z, 0.12, 1.2, 0.1)
    return m


def brass_tree(seed=12):
    """A rim prop: a tree of copper and brass whose leaves are brass plates and little gears, glowing blue fruit
    hanging from its branches, and a big gear for a crown turning slowly on top of its trunk."""
    m = prop("BrassTree", Copper=COPPER, CopperDark=COPPER_DARK, Brass=BRASS, BrassDark=BRASS_DARK, BrassLight=BRASS_LIGHT, Volt=VOLT,
             Crown=BRASS_LIGHT, IronDark=IRON_DARK)
    rng = random.Random(seed)
    trunk = [(0, 0, 0), (0.5, 0.2, 3.0), (-0.3, -0.1, 6.0), (0, 0, 9.0)]
    limb(m, "Copper", trunk, 1.5, 0.7)
    for z in (1.5, 4.5, 7.4):
        x, y = (0.25, 0.1) if z < 3 else ((0.1, 0.05) if z < 6 else (-0.1, -0.03))
        m.block("BrassDark", x, y, z, 1.45 - z * 0.08, 1.45 - z * 0.08, 0.3)
    for k in range(4):
        a = k * math.tau / 4 + 0.4
        limb(m, "CopperDark", [(math.cos(a) * 0.4, math.sin(a) * 0.4, 1.2), (math.cos(a) * 1.4, math.sin(a) * 1.4, 0.5),
                               (math.cos(a) * 2.4, math.sin(a) * 2.4, 0.05)], 0.6, 0.3)

    def on_trunk(z):
        for p, q in zip(trunk, trunk[1:]):
            if p[2] <= z <= q[2]:
                t = (z - p[2]) / (q[2] - p[2])
                return tuple(a + (b - a) * t for a, b in zip(p, q))
        return trunk[-1]

    for k in range(6):
        a = k * math.tau / 6 + rng.uniform(-0.25, 0.25)
        z0 = rng.uniform(4.5, 7.8)
        r = rng.uniform(3.6, 4.8)
        x, y, z = math.cos(a) * r, math.sin(a) * r, z0 + rng.uniform(1.2, 2.6)
        limb(m, "Copper", [on_trunk(z0), (math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, z0 + 1.2), (x, y, z)], 0.45, 0.2)
        for j in range(4):  # a cluster of little gears for leaves
            p = (x + rng.uniform(-1.4, 1.4), y + rng.uniform(-1.4, 1.4), z + rng.uniform(-0.3, 1.1))
            gear(m, ("Brass", "BrassLight", "BrassDark", "Brass")[j], p, rng.uniform(0.6, 1.0), 8, 0.16,
                 turn(rng.uniform(-1.2, 1.2), rng.uniform(-1.2, 1.2), rng.uniform(0, math.tau)), spokes=4, tooth=0.24)
        for j in range(5):  # and a few brass leaves
            p = Vector((x + rng.uniform(-1.5, 1.5), y + rng.uniform(-1.5, 1.5), z + rng.uniform(-0.5, 1.0)))
            d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.3, 0.5))).normalized()
            plate(m, "BrassLight" if j % 2 else "Brass", tuple(p), tuple(p + d * 1.4), (d.y, -d.x, 0.4), 1.1, 0.3, 0.08)
        if k % 2 == 0:  # a glowing fruit hanging under the branch end
            m.block("IronDark", x * 0.85, y * 0.85, z - 1.0, 0.08, 0.08, 1.2)
            ball(m, "Volt", x * 0.85, y * 0.85, z - 1.9, 0.45, 8, 4)
    # The crown: a gear lying on top of the trunk, turning round it.
    prism(m, "IronDark", 0, 0, 8.6, 10.3, 0.22, 0.22, 8)
    gear(m, "Crown", (0, 0, 9.7), 2.6, 16, 0.32, spokes=6)
    ball(m, "BrassLight", 0, 0, 10.45, 0.32, 8, 4)
    return m


def fan_tower(seed=13):
    """A rim prop: a riveted lattice tower with a wind-pump fan at its top, the blades turning, a weather vane
    swinging over it and a lamp on its platform. The fan's hub and the vane's rod are straight above the origin."""
    m = prop("FanTower", Iron=IRON, IronDark=IRON_DARK, IronLight=IRON_LIGHT, Rivet=RIVET, Brass=BRASS, BrassDark=BRASS_DARK,
             Fan=COPPER, Vane=BRASS_LIGHT, Lamp=LAMP)
    zt = 13.0
    corners = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    feet = [(sx * 2.6, sy * 2.6, 0.0) for sx, sy in corners]
    tops = [(sx * 0.9, sy * 0.9, zt) for sx, sy in corners]
    for f, t in zip(feet, tops):
        beam(m, "Iron", f, t, 0.36)
        m.block("IronDark", f[0], f[1], 0.25, 0.9, 0.9, 0.5)
    levels = [0.5 + k * 3.1 for k in range(5)]

    def leg(i, z):
        f, t = Vector(feet[i]), Vector(tops[i])
        return tuple(f.lerp(t, z / zt))

    for i in range(4):
        j = (i + 1) % 4
        for k in range(4):
            za, zb = levels[k], levels[k + 1]
            beam(m, "IronLight", leg(i, za), leg(j, zb), 0.16)
            beam(m, "IronLight", leg(j, za), leg(i, zb), 0.16)
            beam(m, "Iron", leg(i, zb), leg(j, zb), 0.2)
    m.block("IronDark", 0, 0, zt + 0.15, 3.6, 3.6, 0.3)
    for sx, sy in corners:
        m.block("Iron", sx * 1.7, sy * 1.7, zt + 0.8, 0.14, 0.14, 1.0)
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        beam(m, "Iron", (a[0] * 1.7, a[1] * 1.7, zt + 1.25), (b[0] * 1.7, b[1] * 1.7, zt + 1.25), 0.12)
    # The head: a housing, the axle out of its front and the fan on it.
    zf = zt + 2.2
    m.block("IronDark", 0, -0.2, zt + 1.4, 1.2, 2.4, 2.2)
    tube(m, "Brass", (0, 0.8, zf), (0, 2.1, zf), 0.24)
    f = Frame(m, (0, 2.2, zf), UPRIGHT)
    for i in range(16):
        a = (i + 0.5) * math.tau / 16
        f.box("Fan", math.cos(a) * 3.5, math.sin(a) * 3.5, 0, 1.45, 0.24, 0.22, turn(z=a + math.pi / 2))
    for i in range(12):
        a = i * math.tau / 12
        d = Vector((math.cos(a), math.sin(a), 0))
        side = Vector((-math.sin(a), math.cos(a), 0.45))
        plate(m, "Fan", f.at(*(d * 0.55)), f.at(*(d * 3.4)), tuple(f.r @ side), 0.5, 1.1, 0.07)
    f.prism("Fan", 0, 0, -0.3, 0.3, 0.55, 0.55, 8)
    # The weather vane: a rod (it stays still) and an arrow that swings round it.
    prism(m, "IronDark", 0, 0, zt + 2.5, zt + 6.2, 0.08, 0.08, 6)
    ball(m, "BrassDark", 0, 0, zt + 6.3, 0.2, 6, 3)
    m.block("Vane", 0, 0, zt + 5.4, 0.2, 0.2, 0.5)
    m.block("Vane", 0, -0.4, zt + 5.4, 0.1, 3.2, 0.14)
    m.loft_y("Vane", (1.2, 0, zt + 5.4, 0.1, 0.9), (1.9, 0, zt + 5.4, 0.1, 0.05))
    plate(m, "Vane", (0, -1.4, zt + 5.4), (0, -2.4, zt + 5.6), (0, 0, 1), 1.4, 1.0, 0.08)
    # The lamp on the platform's corner.
    m.block("IronDark", 1.5, 1.5, zt + 0.45, 0.5, 0.5, 0.3)
    m.block("Lamp", 1.5, 1.5, zt + 0.95, 0.4, 0.4, 0.7)
    m.block("IronDark", 1.5, 1.5, zt + 1.4, 0.55, 0.55, 0.2)
    return m


def face_box(m, role, a, r, z, w, h, out=0.05, depth=0.1):
    """A flat panel (a window, a door) on the face of an upright prism whose faces look out at angle a, r out from
    its middle (the face's distance, not the corner's)."""
    obox(m, role, (math.cos(a) * (r + out), math.sin(a) * (r + out), z), (depth, w, h), turn(z=a))


def cog_spire(seed=14):
    """A landmark for the rims: a riveted iron spire ringed with four great gears lying flat round it, each
    turning the other way from the one below, lit windows between them, and a blue orb on its tip with lightning
    playing round it. Everything that turns is centred over the origin."""
    m = prop("CogSpire", IronDark=IRON_DARK, Iron=IRON, IronLight=IRON_LIGHT, Rivet=RIVET, Brass=BRASS, BrassDark=BRASS_DARK,
             GearA=BRASS, GearB=COPPER, GearC=BRASS, GearD=COPPER, Window=WINDOW, Volt=VOLT, Arc=ARC, Front="#ff00ff")
    rng = random.Random(seed)
    prism(m, "IronDark", 0, 0, 0, 1.2, 7.2, 6.6, 12)
    prism(m, "Iron", 0, 0, 1.2, 1.8, 6.0, 5.8, 12)
    z0, z1, r0, r1 = 1.8, 26.0, 3.4, 2.3
    prism(m, "Iron", 0, 0, z0, z1, r0, r1, 8, math.pi / 8)

    def radius(z):  # the tower's corner radius at z
        return r0 + (r1 - r0) * (z - z0) / (z1 - z0)

    for role, z, r, teeth, thick in (("GearA", 5.4, 6.6, 24, 0.9), ("GearB", 10.4, 5.8, 20, 0.8), ("GearC", 15.4, 5.0, 16, 0.8),
                                     ("GearD", 20.4, 4.1, 16, 0.7)):
        prism(m, "IronDark", 0, 0, z - 0.75, z + 0.75, radius(z) + 0.25, radius(z) + 0.2, 8, math.pi / 8)
        gear(m, role, (0, 0, z), r, teeth, thick, spokes=8, tooth=0.7)
    for z in (7.9, 12.9, 17.9, 22.9):  # lit windows between the gears, on every face
        for k in range(8):
            a = k * math.tau / 8 + math.pi / 2
            face_box(m, "Window", a, radius(z) * math.cos(math.pi / 8), z, 0.8 - z * 0.012, 1.5)
    for k in range(8):  # rivets up the corners
        a = math.pi / 8 + k * math.tau / 8
        for z in (3.0, 8.0, 13.0, 18.0, 23.0):
            r = radius(z) + 0.05
            m.block("Rivet", math.cos(a) * r, math.sin(a) * r, z, 0.24, 0.24, 0.24)
    # The door, facing the corridor.
    face_box(m, "IronDark", math.pi / 2, r0 * math.cos(math.pi / 8) - 0.05, 3.25, 1.9, 2.8, 0.05, 0.2)
    face_box(m, "Window", math.pi / 2, r0 * math.cos(math.pi / 8), 3.0, 1.4, 2.2, 0.12, 0.08)
    # The top: a brass cap, a spire, four rods and the orb, lightning jumping from it to the rods.
    prism(m, "BrassDark", 0, 0, z1, z1 + 0.6, r1 + 0.3, r1 + 0.3, 8, math.pi / 8)
    prism(m, "Brass", 0, 0, z1 + 0.6, z1 + 2.2, r1 + 0.1, 0.8, 8, math.pi / 8)
    prism(m, "BrassDark", 0, 0, z1 + 2.2, z1 + 4.4, 0.45, 0.15, 8)
    ball(m, "Volt", 0, 0, z1 + 5.2, 1.0, 10, 6)
    for k in range(4):
        a = k * math.tau / 4 + math.pi / 4
        tip = (math.cos(a) * 2.2, math.sin(a) * 2.2, z1 + 3.6)
        beam(m, "Brass", (math.cos(a) * 1.6, math.sin(a) * 1.6, z1 + 1.2), tip, 0.18)
        ball(m, "BrassDark", *tip, 0.28, 6, 3)
        bolt(m, "Arc", (math.cos(a) * 0.8, math.sin(a) * 0.8, z1 + 5.0), tip, 3, 0.16, rng, 0.4)
    m.block("Front", 0, 8, 1, 0.2, 0.2, 0.2)
    return m


def lightning_tower(seed=15):
    """A landmark for the rims: a lattice tower round a copper column, crowned with a great brass dome ringed with
    blue light and racing sparks, lightning arcing down from its rim to three little coils round its foot."""
    m = prop("LightningTower", IronDark=IRON_DARK, Iron=IRON, IronLight=IRON_LIGHT, Rivet=RIVET, Copper=COPPER, CopperDark=COPPER_DARK,
             Brass=BRASS, BrassDark=BRASS_DARK, BrassLight=BRASS_LIGHT, Insulator="#e6e0d2", Volt=VOLT, Arc=ARC, Charge=SPARK,
             Window=WINDOW, Front="#ff00ff")
    rng = random.Random(seed)
    prism(m, "IronDark", 0, 0, 0, 2.0, 4.6, 4.0, 10)
    face_box(m, "Window", math.pi / 2, 4.3 * math.cos(math.pi / 10) - 0.25, 1.0, 1.2, 1.7, 0.1)
    prism(m, "Copper", 0, 0, 2.0, 21.2, 1.0, 0.8, 12)
    z = 2.6
    while z < 20.8:
        band(m, "CopperDark", 0, 0, z, 1.03 - (z - 2) * 0.0105, 0.14, 12)
        z += 0.4
    corners = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    feet = [Vector((sx * 3.0, sy * 3.0, 2.0)) for sx, sy in corners]
    tops = [Vector((sx * 1.4, sy * 1.4, 20.4)) for sx, sy in corners]
    for f, t in zip(feet, tops):
        beam(m, "Iron", tuple(f), tuple(t), 0.34)
    for i in range(4):
        j = (i + 1) % 4
        for k in range(5):
            ta, tb = k / 5, (k + 1) / 5
            beam(m, "IronLight", tuple(feet[i].lerp(tops[i], ta)), tuple(feet[j].lerp(tops[j], tb)), 0.14)
            beam(m, "Iron", tuple(feet[i].lerp(tops[i], tb)), tuple(feet[j].lerp(tops[j], tb)), 0.18)
    # The dome.
    prism(m, "BrassDark", 0, 0, 20.4, 21.6, 1.6, 4.4, 16)
    prism(m, "BrassLight", 0, 0, 21.6, 22.2, 4.5, 4.5, 16)
    prism(m, "Brass", 0, 0, 22.2, 24.0, 4.4, 2.6, 16)
    prism(m, "Brass", 0, 0, 24.0, 25.0, 2.6, 0.8, 16)
    flat_ring(m, "Volt", 0, 0, 21.9, 4.8, 0.36, 0.3, 24)
    for k in range(16):
        a = (k + 0.5) * math.tau / 16
        m.block("Rivet", math.cos(a) * 4.52, math.sin(a) * 4.52, 22.2, 0.22, 0.22, 0.22)
    prism(m, "BrassDark", 0, 0, 25.0, 25.8, 0.3, 0.3, 8)
    ball(m, "Volt", 0, 0, 26.5, 0.75, 10, 5)
    for k in range(12):  # sparks racing round the rim
        a = k * math.tau / 12
        m.block("Charge", math.cos(a) * 5.7, math.sin(a) * 5.7, 21.9 + (0.35 if k % 2 else -0.35), 0.34, 0.34, 0.34)
    # The little coils round its foot, and the lightning down to them.
    for k in range(3):
        a = -math.pi / 2 + k * math.tau / 3 + math.pi / 3
        x, y = math.cos(a) * 9.5, math.sin(a) * 9.5
        prism(m, "IronDark", x, y, 0, 0.7, 1.4, 1.2, 8)
        for j in range(3):
            prism(m, "Insulator", x, y, 0.7 + j * 0.36, 1.0 + j * 0.36, 0.6, 0.6, 8)
        prism(m, "Copper", x, y, 1.8, 5.0, 0.48, 0.42, 10)
        for zz in (2.4, 3.2, 4.0):
            band(m, "CopperDark", x, y, zz, 0.5, 0.18, 10)
        ball(m, "Volt", x, y, 5.6, 0.62, 8, 5)
        d = Vector((math.cos(a), math.sin(a), 0))
        bolt(m, "Arc", tuple(d * 4.5 + Vector((0, 0, 21.6))), (x - d.x * 0.5, y - d.y * 0.5, 6.0), 7, 0.22, rng, 1.2)
    m.block("Front", 0, 10, 1, 0.2, 0.2, 0.2)
    return m


def engine_house(seed=16):
    """A landmark for the rims: a brick engine house with tall lit windows, a huge flywheel turning beside it, a
    flyball governor whirling on its roof and two chimneys smoking. The flywheel's axle runs along X (the game
    turns it round the X line at its height); the governor is straight above the origin."""
    m = prop("EngineHouse", Brick=BRICK, BrickDark=BRICK_DARK, IronDark=IRON_DARK, Iron=IRON, IronLight=IRON_LIGHT, Rivet=RIVET,
             Brass=BRASS, BrassDark=BRASS_DARK, Roof="#3a3f4c", Window=WINDOW, Lamp=LAMP, Flywheel=IRON_LIGHT, Governor=BRASS_LIGHT,
             Smoke="#4f535c", SmokeLight="#737884", Front="#ff00ff")
    w, d, h = 14.0, 9.0, 8.0
    m.block("BrickDark", 0, 0, 0.5, w + 0.6, d + 0.6, 1.0)
    m.block("Brick", 0, 0, (1.0 + h) / 2, w, d, h - 1.0)
    m.block("IronDark", 0, 0, h + 0.15, w + 0.4, d + 0.4, 0.3)
    m.loft_z("Roof", (h + 0.3, 0, 0, w + 0.6, d + 0.8), (h + 4.0, 0, 0, w + 0.6, 0.4))
    for x in (-w / 2, -2.25, 2.25, w / 2):  # pilasters
        m.block("BrickDark", x, d / 2 + 0.1, (1.0 + h) / 2, 0.8, 0.3, h - 1.0)
    for x in (-4.5, 0.0, 4.5):  # tall arched windows
        m.block("BrickDark", x, d / 2 + 0.06, 2.0, 2.4, 0.2, 0.4)
        m.block("Window", x, d / 2 + 0.06, 4.4, 1.8, 0.1, 4.4)
        m.block("Window", x, d / 2 + 0.06, 6.85, 1.2, 0.1, 0.5)
        m.block("IronDark", x, d / 2 + 0.13, 4.6, 0.12, 0.08, 4.9)
        for z in (3.6, 5.2):
            m.block("IronDark", x, d / 2 + 0.13, z, 1.8, 0.08, 0.12)
        m.block("BrickDark", x, d / 2 + 0.1, 7.35, 2.2, 0.2, 0.5)
    for sx in (-1, 1):  # lamps on the front corners
        beam(m, "IronDark", (sx * 6.2, d / 2 + 0.1, 6.0), (sx * 6.2, d / 2 + 1.0, 6.0), 0.12)
        m.block("IronDark", sx * 6.2, d / 2 + 1.0, 5.75, 0.6, 0.6, 0.15)
        m.block("Lamp", sx * 6.2, d / 2 + 1.0, 5.3, 0.45, 0.45, 0.75)
    # The flywheel on the +X gable, its axle out of the wall into a bearing on a pedestal.
    zc = 6.0
    tube(m, "Iron", (w / 2 - 0.2, 0, zc), (w / 2 + 3.6, 0, zc), 0.4)
    m.block("IronDark", w / 2 + 3.2, 0, zc / 2, 0.9, 1.8, zc)
    m.block("IronDark", w / 2 + 3.2, 0, zc + 0.3, 1.2, 1.4, 1.2)
    m.block("IronDark", w / 2 + 0.7, 0, zc, 1.2, 1.4, 1.4)
    wheel(m, "Flywheel", (w / 2 + 1.9, 0, zc), 6.0, 0.9, SIDEWAYS, spokes=8, rim=0.9)
    # The governor on the ridge: a spindle (still) and two flyballs on their arms, whirling round it.
    ridge = h + 4.0
    m.block("IronDark", 0, 0, ridge + 0.2, 1.4, 1.0, 0.5)
    prism(m, "IronDark", 0, 0, ridge + 0.4, ridge + 4.0, 0.12, 0.12, 6)
    prism(m, "Governor", 0, 0, ridge + 3.3, ridge + 3.7, 0.32, 0.32, 8)
    prism(m, "Governor", 0, 0, ridge + 1.6, ridge + 1.9, 0.3, 0.3, 8)
    for s in (-1, 1):
        beam(m, "Governor", (s * 0.2, 0, ridge + 3.5), (s * 1.5, 0, ridge + 2.2), 0.12)
        beam(m, "Governor", (s * 0.2, 0, ridge + 1.75), (s * 0.95, 0, ridge + 2.55), 0.1)
        ball(m, "Governor", s * 1.6, 0, ridge + 2.1, 0.5, 8, 4)
    ball(m, "BrassDark", 0, 0, ridge + 4.15, 0.22, 6, 3)
    # Two chimneys at the back, smoking.
    for sx in (-1, 1):
        x, y = sx * 5.0, -2.6
        m.block("Brick", x, y, h + 3.7, 1.6, 1.6, 6.6)
        m.block("IronDark", x, y, h + 7.1, 2.0, 2.0, 0.4)
        puffs(m, "Smoke", x, y, h + 8.6, 4, 1.8, 1.4, grow=0.15, shade="SmokeLight")
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


AIRSHIP_ROLES = ("Envelope", "EnvelopeDark", "Band", "BrassDark", "Gondola", "Wood", "Window", "Fin", "IronDark", "Lamp")


def airship(seed=17):
    """The sky piece: an airship hanging in the smog beyond the island, its envelope banded in brass, lit windows
    along its gondola and a propeller turning on each side; the whole ship rises and sinks slowly. It starts high
    above the ground, its nose to +Y, so it only has to face along the corridor."""
    m = prop("Airship", Envelope="#7c3b33", EnvelopeDark="#5e2b27", Band=BRASS, BrassDark=BRASS_DARK, Gondola=WOOD_DARK, Wood=WOOD,
             Window=WINDOW, Fin="#5e2b27", IronDark=IRON_DARK, PropL=BRASS_LIGHT, PropR=BRASS_LIGHT, Lamp=LAMP, Front="#ff00ff")
    zc = 52.0
    profile = [(-13.0, 0.7), (-12.0, 2.0), (-10.0, 3.4), (-7.0, 4.4), (-3.0, 4.9), (2.0, 4.9), (6.0, 4.5), (9.0, 3.6),
               (11.0, 2.4), (12.4, 1.0)]
    for k, ((y0, r0), (y1, r1)) in enumerate(zip(profile, profile[1:])):
        tube(m, "Envelope" if k % 2 else "EnvelopeDark", (0, y0, zc), (0, y1, zc), r0, r1, 16)
        if 0 < k < len(profile) - 2:
            tube(m, "Band", (0, y1 - 0.18, zc), (0, y1 + 0.18, zc), r1 + 0.08, r1 + 0.08, 16)
    tube(m, "BrassDark", (0, 12.4, zc), (0, 13.1, zc), 1.0, 0.3, 12)
    for s in (-1, 1):  # four tail fins
        m.loft_y("Fin", (-13.4, 0, zc + s * 3.7, 0.3, 4.6), (-8.4, 0, zc + s * 3.4, 0.3, 0.7))
        m.loft_y("Fin", (-13.4, s * 3.7, zc, 4.6, 0.3), (-8.4, s * 3.4, zc, 0.7, 0.3))
    # The gondola under it, its struts and lit windows.
    zg = zc - 6.3
    m.block("Gondola", 0, 0.6, zg, 2.6, 9.4, 1.8)
    m.loft_z("Gondola", (zg - 1.6, 0, 0.6, 1.4, 7.0), (zg - 0.9, 0, 0.6, 2.6, 9.4))
    m.block("Wood", 0, 0.6, zg + 1.05, 2.9, 9.8, 0.3)
    for y in (-3.0, 0.6, 4.2):
        for sx in (-1, 1):
            beam(m, "IronDark", (sx * 1.2, y, zg + 1.1), (sx * 1.9, y, zc - 4.4), 0.16)
    for k in range(6):
        for sx in (-1, 1):
            m.block("Window", sx * 1.32, -3.0 + k * 1.45, zg + 0.1, 0.1, 0.85, 0.7)
    m.block("Lamp", 0, 5.4, zg, 0.6, 0.2, 0.6)
    # The propellers on their outriggers, each turning on its own middle.
    for sx, role in ((-1, "PropL"), (1, "PropR")):
        beam(m, "IronDark", (sx * 1.2, -2.6, zg + 0.2), (sx * 3.2, -2.9, zg + 0.2), 0.3)
        tube(m, "IronDark", (sx * 3.2, -4.4, zg + 0.2), (sx * 3.2, -1.6, zg + 0.2), 0.55, 0.45, 10)
        f = Frame(m, (sx * 3.2, -4.75, zg + 0.2), UPRIGHT)
        for k in range(4):
            a = k * math.tau / 4 + math.pi / 4
            f.box(role, math.cos(a) * 1.05, math.sin(a) * 1.05, 0, 1.9, 0.42, 0.1, turn(z=a) @ turn(x=0.35))
        f.prism(role, 0, 0, -0.3, 0.3, 0.32, 0.32, 8)
    m.block("Front", 0, 15, zc, 0.2, 0.2, 0.2)
    return m


def brass_fall(seed=18):
    """A crucible of molten brass tipped over the wall's edge on its iron cradle, pouring glowing metal down the
    wall into a pool on the corridor floor, drops of it falling for ever and sparks flying up off the pool. Origin
    on the wall's top inner edge: rim z 0, floor z -44, +Y out into the corridor. The Front part tells the game
    which way it faces, then it goes."""
    m = prop("BrassFall", IronDark=IRON_DARK, Iron=IRON, Rivet=RIVET, Copper=COPPER, CopperDark=COPPER_DARK, BrassDark=BRASS_DARK,
             Molten=MOLTEN, Slag="#a5481f", Falling="#ffe08a", Ember=EMBER, Front="#ff00ff")
    rng = random.Random(seed)
    ya, za = -3.6, 5.2  # the cradle's axle
    for sx in (-1, 1):
        beam(m, "Iron", (sx * 3.4, ya - 2.2, 0), (sx * 3.4, ya, za + 0.4), 0.6)
        beam(m, "Iron", (sx * 3.4, ya + 2.2, 0), (sx * 3.4, ya, za + 0.4), 0.6)
        m.block("IronDark", sx * 3.4, ya, za, 0.9, 0.9, 0.9)
        m.block("IronDark", sx * 3.4, ya, 0.25, 1.0, 5.4, 0.5)
    tube(m, "Iron", (-3.8, ya, za), (3.8, ya, za), 0.3)
    f = Frame(m, (0, ya, za), turn(x=-1.05))  # tipped towards the corridor
    f.prism("Copper", 0, 0, -2.6, 2.0, 2.0, 2.6, 12)
    for z in (-1.6, 0.6):
        f.prism("CopperDark", 0, 0, z - 0.18, z + 0.18, 2.12 + 0.13 * (z + 2.6), 2.12 + 0.13 * (z + 2.6) + 0.02, 12)
    f.prism("CopperDark", 0, 0, 1.9, 2.25, 2.75, 2.75, 12)
    f.prism("Molten", 0, 0, 1.8, 2.02, 2.45, 2.45, 12)
    f.prism("CopperDark", 0, 0, -2.9, -2.6, 1.6, 1.8, 12)
    # The pour: over the lip, out past the edge, and down the wall in a curtain.
    beam(m, "Molten", (0, -0.4, 3.9), (0, 1.3, 2.3), 1.5, 1.0)
    beam(m, "Molten", (0, 1.3, 2.3), (0, 2.3, 0.3), 1.5, 1.0)
    z = 0.5
    while z > -43.5:
        length = min(rng.uniform(5, 8), z + 43.5)
        width = rng.uniform(1.8, 2.4)
        x = rng.uniform(-0.15, 0.15)
        m.block("Molten", x, 2.4, z - length / 2, width, 1.0, length)
        for side in (-1, 1):
            m.block("Slag", x + side * (width / 2 + 0.12), 2.3, z - length / 2, 0.36, 0.7, length * 0.9)
        z -= length
    # Drops that fall: rows four studs apart, so moving them down four studs and back loops seamlessly.
    for k, zz in enumerate(range(-2, -44, -4)):
        for x in (-0.55, 0.15, 0.65):
            jitter = ((k * 7 + int(x * 10)) % 3 - 1) * 0.1
            m.block("Falling", x + jitter, 3.05, zz - (1.3 if x > 0.5 else 0), 0.4, 0.3, 0.4)
    puddle(m, "Molten", ((0, 6.5, 8, 5), (0, 9.0, 5, 2.4), (-3.2, 7.4, 3.0, 3.6), (3.0, 7.2, 3.0, 3.4)), z=-43.75, thick=0.5)
    puddle(m, "Slag", ((0, 6.6, 9.9, 6.6),), z=-43.8, thick=0.36)
    for x, y, h in ((-1.0, 5.6, 1.3), (1.2, 6.2, 1.7), (0.1, 7.6, 1.0)):
        m.loft_z("Molten", (-43.5, x, y, 0.7, 0.7), (-43.5 + h, x, y, 0.2, 0.2))
    # Sparks flying up off the pool: columns 1.5 apart, rising 1.5 and starting over.
    for x, y in ((-2.2, 7.8), (2.4, 6.8), (0.6, 9.4)):
        for k in range(4):
            m.block("Ember", x + (k % 2) * 0.2, y, -42.6 + k * 1.5 + (0.5 if x > 0 else 0), 0.22, 0.22, 0.22)
    # Ingots stacked on the rim beside it.
    for k, (x, y, z) in enumerate(((5.6, -4.2, 0.3), (6.9, -4.2, 0.3), (6.25, -4.2, 0.85))):
        m.loft_z("BrassDark", (z - 0.3, x, y, 1.2, 2.4), (z + 0.3, x, y, 0.9, 2.1))
    m.block("Front", 0, 6, -20, 0.2, 0.2, 0.2)
    return m


def gear_arch(seed=19):
    """Riveted iron pylons on both rims and an iron girder arching across the corridor, three great gears turning
    on its faces (the two on its shoulders one way, the one on its crown the other) and a lamp swinging under the
    crown. Each gear is on both faces, so it reads from either way along the corridor. Modelled for the 72-wide
    corridor (feet beyond 36 from the middle); MapDecor stretches it to the real width. All of it stays above the
    rim (z 0), clear of the flight camera."""
    m = prop("GearArch", IronDark=IRON_DARK, Iron=IRON, IronLight=IRON_LIGHT, Rivet=RIVET, Brass=BRASS, BrassDark=BRASS_DARK,
             GearL=BRASS, GearTop=COPPER, GearR=BRASS, Chain=IRON_LIGHT, LampCage=IRON_DARK, Lamp=LAMP, Front="#ff00ff")
    for sx in (-1, 1):
        x = sx * 40
        m.block("IronDark", x, 0, 0.75, 6.4, 5.4, 1.5)
        m.loft_z("Iron", (1.5, x, 0, 4.4, 3.6), (17.0, x, 0, 3.2, 2.8))
        for z in (5.0, 11.0):
            w = 4.4 - (z - 1.5) / 15.5 * 1.2
            m.block("BrassDark", x, 0, z, w + 0.2, 3.6 - (z - 1.5) / 15.5 * 0.8 + 0.2, 0.4)
        m.block("BrassDark", x, 0, 17.3, 3.6, 3.2, 0.6)
    a_, b_, z0 = 40.0, 13.0, 17.6
    n = 40
    pts = [Vector((a_ * math.cos(math.pi * i / n), 0, z0 + b_ * math.sin(math.pi * i / n))) for i in range(n + 1)]
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        mid = (p + q) / 2
        along = (q - p)
        rot = turn(y=-math.atan2(along.z, along.x))
        obox(m, "Iron", tuple(mid), (along.length + 0.3, 2.4, 1.8), rot)
        normal = rot @ Vector((0, 0, 1))
        obox(m, "IronDark", tuple(mid + normal * 1.0), (along.length + 0.2, 2.9, 0.35), rot)
        obox(m, "IronDark", tuple(mid - normal * 1.0), (along.length + 0.2, 2.9, 0.35), rot)
        if i % 2 == 0:
            for y in (-1.25, 1.25):
                m.block("Rivet", mid.x, y, mid.z, 0.24, 0.12, 0.24)
    for role, t, r, teeth, thick in (("GearL", 0.78, 4.4, 16, 0.6), ("GearTop", 0.5, 5.2, 20, 0.6), ("GearR", 0.22, 4.4, 16, 0.6)):
        c = Vector((a_ * math.cos(math.pi * t), 0, z0 + b_ * math.sin(math.pi * t)))
        tube(m, "IronDark", (c.x, -2.6, c.z), (c.x, 2.6, c.z), 0.45)
        for y in (-1.95, 1.95):
            gear(m, role, (c.x, y, c.z), r, teeth, thick, UPRIGHT, spokes=6, tooth=0.7)
    # The lamp hung under the crown, swinging along the corridor.
    hinge = z0 + b_ - 0.9
    m.block("IronDark", 0, 0, hinge + 0.1, 0.6, 0.6, 0.3)
    for i in range(9):  # long enough that the lamp hangs below the crown gear
        z = hinge - i * 0.6
        beam(m, "Chain", (0, 0, z), (0, 0, z - 0.6), *((0.34, 0.12) if i % 2 else (0.12, 0.34)))
    zl = hinge - 5.4
    m.block("LampCage", 0, 0, zl + 0.15, 1.3, 1.3, 0.3)
    m.loft_z("LampCage", (zl + 0.3, 0, 0, 1.1, 1.1), (zl + 0.9, 0, 0, 0.3, 0.3))
    m.block("Lamp", 0, 0, zl - 0.75, 0.9, 0.9, 1.5)
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        m.block("LampCage", sx * 0.52, sy * 0.52, zl - 0.75, 0.12, 0.12, 1.6)
    m.block("LampCage", 0, 0, zl - 1.6, 1.2, 1.2, 0.2)
    m.block("Front", 0, 6, 30, 0.2, 0.2, 0.2)
    return m


ALL = [gear_works, steam_hammer, spark_coil, boiler, steam_pipes, metronome, music_box, pocket_watch, scrap_pile, floor_gears,
       smokestack, brass_tree, fan_tower, cog_spire, lightning_tower, engine_house, airship, brass_fall, gear_arch]

# What moves. The game reads the same numbers from shared/Config/PropMotion.luau. Kinds of move:
#   spin  degrees a second; swing  degrees each way, over period seconds; bob  studs up and down over period;
#   pulse  the glow dims to this share and back over period; fall  drops this far over period, then starts again
#   (negative rises).
# spin and swing turn round axis "up" (default), "across" (the model's X) or "ahead" (its Y), through the part's
# own middle (about="self") or a point `height` studs straight above the prop's origin (the default).
_STEAM = dict(fall=-1.2, period=0.7)
_SMOKE = dict(fall=-1.5, period=1.4)
_ARM = dict(swing=24, period=1.6, axis="ahead", height=1.8)
_BIRD = dict(spin=36)
_HAMMER = dict(bob=0.6, period=1.1)
_STACK = dict(fall=-2.2, period=1.6)
_HOUSE_SMOKE = dict(fall=-1.8, period=1.4)
_FLOAT = dict(bob=1.2, period=6)
_ARCH_LAMP = dict(swing=8, period=3.2, axis="across", height=29.7)
MOTION = {
    "prop_GearWorks": {"GearA": dict(spin=20, axis="ahead", about="self"), "GearB": dict(spin=-40, axis="ahead", about="self"),
                       "Steam": dict(_STEAM), "Volt": dict(pulse=0.5, period=1.4)},
    "prop_SteamHammer": {"Hammer": dict(_HAMMER), "HammerFace": dict(_HAMMER), "Flywheel": dict(spin=120, axis="across", about="self"),
                         "Ember": dict(pulse=0.6, period=1.1), "Steam": dict(fall=-1.0, period=0.55)},
    "prop_SparkCoil": {"Arc": dict(pulse=0.05, period=0.3), "Volt": dict(pulse=0.55, period=1.6), "Charge": dict(spin=140)},
    "prop_Boiler": {"Needle": dict(swing=22, period=0.9, axis="ahead", height=7.6), "Furnace": dict(pulse=0.55, period=1.3),
                    "Steam": dict(_STEAM), "Smoke": dict(_SMOKE), "SmokeLight": dict(_SMOKE)},
    "prop_SteamPipes": {"ValveA": dict(spin=50, axis="ahead", about="self"), "ValveB": dict(spin=-35, axis="ahead", about="self"),
                        "Needle": dict(swing=18, period=1.3, axis="ahead", height=1.35), "Steam": dict(_STEAM)},
    "prop_Metronome": {"Arm": dict(_ARM), "ArmWeight": dict(_ARM), "Key": dict(spin=40, axis="across", about="self")},
    "prop_MusicBox": {"Drum": dict(spin=30, axis="across", about="self"), "Key": dict(spin=-30, axis="across", about="self"),
                      "Turntable": dict(_BIRD), "Bird": dict(_BIRD), "BirdEye": dict(_BIRD)},
    "prop_PocketWatch": {"MinuteHand": dict(spin=-30), "HourHand": dict(spin=-2.5), "GearA": dict(spin=60, about="self")},
    "prop_ScrapPile": {"GearA": dict(spin=25, axis="ahead", about="self"), "Spark": dict(pulse=0.05, period=0.4)},
    "prop_FloorGears": {"GearA": dict(spin=12, about="self"), "GearB": dict(spin=-20, about="self"), "Volt": dict(pulse=0.4, period=3)},
    "prop_Smokestack": {"Smoke": dict(_STACK), "SmokeLight": dict(_STACK), "Ember": dict(pulse=0.6, period=2.2),
                        "Furnace": dict(pulse=0.6, period=1.7)},
    "prop_BrassTree": {"Crown": dict(spin=14), "Volt": dict(pulse=0.45, period=2.6)},
    "prop_FanTower": {"Fan": dict(spin=60, axis="ahead", height=15.2), "Vane": dict(swing=30, period=6), "Lamp": dict(pulse=0.7, period=2.4)},
    "prop_CogSpire": {"GearA": dict(spin=12), "GearB": dict(spin=-16), "GearC": dict(spin=20), "GearD": dict(spin=-26),
                      "Volt": dict(pulse=0.5, period=1.8), "Arc": dict(pulse=0.05, period=0.35)},
    "prop_LightningTower": {"Arc": dict(pulse=0.05, period=0.4), "Volt": dict(pulse=0.55, period=2), "Charge": dict(spin=90)},
    "prop_EngineHouse": {"Flywheel": dict(spin=30, axis="across", height=6), "Governor": dict(spin=150), "Smoke": dict(_HOUSE_SMOKE),
                         "SmokeLight": dict(_HOUSE_SMOKE), "Window": dict(pulse=0.8, period=3)},
    "prop_Airship": {**{role: dict(_FLOAT) for role in AIRSHIP_ROLES},
                     "PropL": dict(spin=300, axis="ahead", about="self", **_FLOAT), "PropR": dict(spin=-300, axis="ahead", about="self", **_FLOAT)},
    "prop_BrassFall": {"Falling": dict(fall=4, period=0.8), "Molten": dict(pulse=0.7, period=2.2), "Ember": dict(fall=-1.5, period=0.5)},
    "prop_GearArch": {"GearL": dict(spin=14, axis="ahead", about="self"), "GearR": dict(spin=14, axis="ahead", about="self"),
                      "GearTop": dict(spin=-11, axis="ahead", about="self"), "Chain": dict(_ARCH_LAMP), "LampCage": dict(_ARCH_LAMP),
                      "Lamp": dict(_ARCH_LAMP, pulse=0.7)},
}

# Where the props go: the same rules as Config/Decor's ClockworkCitadel (keep the two in step). The map is 1500 long.
DECOR = dict(
    floor=dict(first=12, gap=(12, 22), side=(24, 34),
               props=[("prop_GearWorks", 14, (1.3, 1.7)), ("prop_SteamHammer", 10, (1.2, 1.5)), ("prop_Boiler", 9, (1.2, 1.5)),
                      ("prop_SteamPipes", 9, (1.2, 1.5)), ("prop_Metronome", 8, (1.2, 1.5)), ("prop_MusicBox", 6, (1.1, 1.4)),
                      ("prop_SparkCoil", 6, (1.2, 1.5)), ("prop_PocketWatch", 4, (1.2, 1.4))],
               extras=dict(chance=0.7, spread=8, props=[("prop_ScrapPile", 5, (0.9, 1.2)), ("prop_SteamPipes", 2, (0.6, 0.8)),
                                                         ("prop_GearWorks", 2, (0.6, 0.8))])),
    rim=dict(first=6, gap=(14, 24), chance=0.9, side=(64, 102),
             props=[("prop_GearWorks", 6, (2.0, 2.6)), ("prop_Smokestack", 4, (1.6, 2.0)), ("prop_BrassTree", 4, (1.8, 2.3)),
                    ("prop_FanTower", 3, (1.5, 1.9)), ("prop_SteamPipes", 2, (2.0, 2.4)), ("prop_ScrapPile", 2, (2.2, 2.8))]),
    overhead=[("prop_GearArch", 260, 0, 1), ("prop_GearArch", 800, 0, 1.05), ("prop_GearArch", 1320, 0, 1)],
    walls=[("prop_BrassFall", d, side) for d, side in ((80, 1), (260, -1), (450, 1), (640, -1), (820, 1), (1000, -1), (1180, 1),
                                                       (1370, -1))],
    spots=[("prop_CogSpire", 90, -86, "rim", 0, 1.4, "middle"), ("prop_CogSpire", 620, 86, "rim", 0, 1.5, "middle"),
           ("prop_CogSpire", 1150, -86, "rim", 0, 1.4, "middle"),
           ("prop_LightningTower", 220, 86, "rim", 0, 1.3, "middle"), ("prop_LightningTower", 760, -86, "rim", 0, 1.4, "middle"),
           ("prop_LightningTower", 1290, 86, "rim", 0, 1.3, "middle"),
           ("prop_EngineHouse", 400, -84, "rim", 0, 1.3, "middle"), ("prop_EngineHouse", 940, 84, "rim", 0, 1.4, "middle"),
           ("prop_EngineHouse", 1440, -84, "rim", 0, 1.3, "middle"),
           ("prop_Airship", 330, -170, "rim", 0, 2.2, "along"), ("prop_Airship", 1060, 175, "rim", 0, 2.4, "along")]
          + [("prop_FloorGears", d, x, "floor", yaw, 1.2) for d, x, yaw in ((40, -3, 20), (150, 4, 140), (270, -4, 70), (380, 3, 200),
                                                                              (500, -2, 300), (610, 4, 40), (730, -3, 110), (850, 2, 250),
                                                                              (970, -4, 330), (1090, 3, 80), (1210, -2, 160),
                                                                              (1330, 4, 10), (1450, -3, 230))],
)


# ---------------------------------------------------------------------- light


def citadel_light(scene):
    """Night in the citadel for the renders: cold moonlight through the smog and a steel-blue fill, close to the
    game's Config/Lighting look for this world."""
    sun = bpy.data.objects["Sun"]
    sun.data.energy = 1.5
    sun.data.color = (0.8, 0.86, 1.0)
    sun.rotation_euler = (math.radians(-58), math.radians(25), math.radians(30))
    ambient = scene.world.node_tree.nodes["Background"]
    ambient.inputs["Color"].default_value = (0.64, 0.68, 0.8, 1)
    ambient.inputs["Strength"].default_value = 0.72


# ---------------------------------------------------------------------- scene and renders

BIG = {"prop_CogSpire": (-85, -120, 0), "prop_LightningTower": (-45, -120, 0), "prop_EngineHouse": (-5, -120, 0),
       "prop_Smokestack": (30, -112, 0), "prop_BrassTree": (48, -112, 0), "prop_FanTower": (66, -112, 0),
       "prop_Airship": (40, -230, 0), "prop_BrassFall": (110, -110, 44), "prop_GearArch": (200, -170, 0)}


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
    stars = mk.star_dome(stage, count=90, colours=("#dfe8ff", "#ffe2c0"), glow=3)
    bpy.context.view_layer.update()
    mk.set_sky(scene, SKY)
    citadel_light(scene)

    everything = roots + [player]
    if stills:
        for model, root in zip(models, roots):
            name = model.name
            if name == "prop_GearArch":
                mk.shoot_prop(scene, name, root, player, everything, (-0.15, 1.0, 0.25), 0.95, (1400, 700), 32)
            elif name == "prop_BrassFall":
                mk.shoot_prop(scene, name, root, player, everything, (0.6, 1.0, 0.1), 0.9, (700, 900), 40)
            elif name == "prop_Airship":
                mk.shoot_prop(scene, name, root, player, everything, (0.9, 0.6, -0.1), 0.9, (900, 700), 50)
            elif name in ("prop_CogSpire", "prop_LightningTower", "prop_EngineHouse"):
                mk.shoot_prop(scene, name, root, player, everything, (0.5, 0.95, 0.35), 1.15, (800, 800), 50)
            else:
                mk.shoot_prop(scene, name, root, player, everything)
        player.location = (30, -40, 0)
        bpy.context.view_layer.update()
        small = [r for r in roots if mk.prop_of(r) not in BIG]
        mk.set_visible(everything, small + [player])
        kit.shoot(scene, "props", (row_middle, 40, 30), (row_middle, -40, 5), (1800, 700), 18)
        landmarks = [built[n] for n in ("prop_CogSpire", "prop_LightningTower", "prop_EngineHouse", "prop_Smokestack", "prop_BrassTree",
                                        "prop_FanTower")]
        mk.set_visible(everything, landmarks + [player])
        player.location = (-20, -96, 0)
        bpy.context.view_layer.update()
        kit.shoot(scene, "landmarks", (-12, -10, 34), (-12, -118, 15), (1800, 800), 20)

    if videos:  # close up on what moves
        names = ("prop_GearWorks", "prop_SteamHammer", "prop_Boiler", "prop_SteamPipes", "prop_Metronome", "prop_MusicBox",
                 "prop_SparkCoil", "prop_PocketWatch", "prop_CogSpire", "prop_LightningTower", "prop_EngineHouse", "prop_FanTower",
                 "prop_Airship")
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
        mk.render_video(scene, RENDERS, "clockwork_motion", 120, 15,
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

        mk.render_video(scene, RENDERS, "clockwork_flight", frames, 15, fly, (1600, 900))
        mk.reset_motion(entries)

    mk.clear([corridor, stars] + copies)
    mk.light_up(roots, GLOW_ROLES, 0)
    ground.hide_render = False
    for root in roots:
        for child in root.children:
            child.hide_render = False
    player.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "clockwork_citadel_models.blend"))
    print("saved", HERE / "clockwork_citadel_models.blend")
    for model in models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    # After "--": "stills" renders only the stills, "videos" only the videos; nothing, both.
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(stills=not args or "stills" in args, videos=not args or "videos" in args)
