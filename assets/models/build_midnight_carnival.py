"""Builds Midnight Carnival's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_midnight_carnival.py              (stills and videos)
    Blender -b -P build_midnight_carnival.py -- stills    (stills only, quicker while modelling)

Saves midnight_carnival_models.blend and renders to design/world/models_midnight_carnival/: one still per prop, the
props together, the landmarks, a stretch of corridor, and two videos of what moves (carnival_motion.mp4 close up,
carnival_flight.mp4 down the corridor at the flight camera's height).

Midnight Carnival, map 11, carries on the run of mysterious, dark maps: a travelling fair that set up at midnight
and never left. Nobody runs it, yet every ride still turns and every bulb still burns. A deep teal midway on the
floor, crimson walls like the curtain of a big top with gold fringe hanging over them, gold straw on the rims, and
a light of its own: warm carnival bulbs, a little pink neon, and the pale glow of the ghosts who ride the rides.
Warm crimson and gold over cold teal, so it reads at a glance after the maps before it.

Its signature is the striped tent: crimson and cream, a pennant waving on top, a glowing doorway, bulbs round its
eaves. On the floor: jack-in-the-boxes whose clown bobs and wobbles on its spring, popcorn carts popping for ever,
a fortune teller whose head turns over a glowing crystal ball, strength testers whose puck rings the bell, balloon
carts (one balloon grins), lamp posts with a crow that looks round and a sign that swings, now and then a carousel,
and flat circus rings with chasing bulbs where the eggs land. On the rims: big tents, swing rides with ghosts in
the chairs, hot-air balloons straining at their ropes, helter-skelters. Landmarks: Ferris wheels turning, big tops
whose searchlights sweep the sky, clown-faced fun houses with hypnotic spiral eyes, and a sleeping crescent moon
hung in the sky on a rope like a stage prop, swaying. Giant popcorn boxes tip over the wall tops and pour popcorn
down into the corridor, and roller-coaster loops cross over it with ghost riders going round and round.

What moves is MOTION below, the same numbers as shared/Config/PropMotion.luau (keep the two in step).
Glowing roles (GLOW_ROLES) must also be in shared/Roles.luau, which makes them Neon in the game.
Props that must face a certain way carry a small Front part on their +Y side; MapDecor turns them, then removes it.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import map_kit as mk  # noqa: E402
from map_kit import ball, beam, disc, dome, flat_ring, gem, hoop, kit, plate, prism, star_prism  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "models_midnight_carnival"

# Roles lit from inside. The game makes them Neon (shared/Roles.luau), so add new ones there too. Lamp, Window,
# Flame, Gaze and LampStar glow in the game already (older maps); the rest are new.
GLOW_ROLES = {"Bulb", "Lamp", "Neon", "Seer", "Trance", "Crescent", "LampStar", "Ghost", "Searchbeam", "Window", "Flame", "Gaze"}
kit.NO_STUDS.update(GLOW_ROLES)
mk.GLOW_STRENGTH = 2.2

# Shared colours, so every prop's canvas, trim and light match.
CRIMSON, CRIMSON_DARK, CREAM = "#b3263a", "#7e1a2a", "#f2e6cc"
GOLD, GOLD_DARK = "#e9b23a", "#a9761f"
TEAL, TEAL_DARK = "#2f9a94", "#1e6461"
PLUM, PLUM_DARK = "#4b2b5f", "#2e1a3c"
IRON = "#2f2a3a"
WOOD, WOOD_DARK = "#8a5a36", "#5e3b23"
SHADOW = "#1a1222"
ROPE = "#d9c9a3"
POPCORN, BUTTER = "#fff2c8", "#f4cf5a"
BULB = "#ffe7a3"
LAMP = "#ffc96b"
NEON = "#ff4f9a"
GHOST = "#d8fff4"
HAIR = "#7a3fc0"
PURPLE = "#6b3a9a"

# The corridor's Midnight Carnival colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#2b6c72", "FloorB": "#245f65", "Dirt": "#7a2335", "DirtB": "#6a1c2d", "Grass": "#be8a2a"}
SKY = "#161230"

# Every part of a moving group gets the same move, so they turn round the same point and stay together.
JACK = ("Spring", "ClownFace", "Hair", "Nose", "Grin", "Teeth", "EyeWhite", "Pupil", "Ruffle", "RuffleB")
TELLER = ("TellerFace", "Turban", "Jewel", "Moustache")
CAROUSEL = ("Deck", "Column", "Mirror", "Poles", "Canopy", "CanopyLight", "Valance", "Finial")
SWINGS = ("Canopy", "CanopyLight", "Valance", "Finial", "Chains", "Seats", "SeatBack", "Ghost", "GhostEye")
BALLOON = ("Envelope", "EnvelopeB", "Band", "Rope", "Burner", "Basket", "BasketRim", "Sandbag")
WHEEL = ("Wheel", "Spokes", "Hub", "CabinA", "CabinB", "CabinTrim", "Window", "LampStar")
MOON = ("MoonFace", "Blush", "Rope")
RIDERS = ("Cart", "CartTrim", "Ghost", "GhostEye")

# What moves. The game reads the same numbers from shared/Config/PropMotion.luau. Kinds of move:
#   spin  degrees a second; swing  degrees each way, over period seconds; bob  studs up and down over period
#   (negative: the other way round, so two groups take turns); pulse  the glow dims to this share and back over
#   period; fall  drops this far over period, then starts again (negative rises).
# spin and swing turn round axis "up" (default), "across" (the model's X) or "ahead" (its Y), through the part's
# own middle (about="self") or a point `height` studs straight above the prop's origin (the default).
MOTION = {
    "prop_StripedTent": {"Flag": dict(swing=25, period=3.2), "Bulb": dict(pulse=0.4, period=1.6),
                         "Lamp": dict(pulse=0.7, period=2.3)},
    "prop_JackBox": {**{role: dict(swing=10, period=2.4, axis="ahead", height=4.6, bob=0.4) for role in JACK},
                     "Crank": dict(spin=90, axis="across", about="self")},
    "prop_PopcornCart": {"Kernels": dict(fall=-1.2, period=0.6), "Bulb": dict(pulse=0.5, period=1.3)},
    "prop_FortuneBooth": {**{role: dict(swing=18, period=6) for role in TELLER},
                          "Trance": dict(swing=18, period=6, pulse=0.5),
                          "Seer": dict(pulse=0.35, period=2.6), "Bulb": dict(pulse=0.4, period=1.1)},
    "prop_HighStriker": {"Puck": dict(bob=4.4, period=1.8), "Bell": dict(swing=10, period=1.8, axis="ahead", height=13.6),
                         "Bulb": dict(pulse=0.3, period=0.9)},
    "prop_BalloonCart": {"BalloonA": dict(swing=8, period=3.4, axis="across", height=4.2),
                         "SmileA": dict(swing=8, period=3.4, axis="across", height=4.2),
                         "StringA": dict(swing=8, period=3.4, axis="across", height=4.2),
                         "BalloonB": dict(swing=7, period=4.2, axis="ahead", height=4.2),
                         "StringB": dict(swing=7, period=4.2, axis="ahead", height=4.2),
                         "BalloonC": dict(swing=9, period=2.9, axis="across", height=4.2),
                         "StringC": dict(swing=9, period=2.9, axis="across", height=4.2),
                         "BalloonD": dict(swing=8, period=3.7, axis="ahead", height=4.2),
                         "StringD": dict(swing=8, period=3.7, axis="ahead", height=4.2)},
    "prop_Carousel": {**{role: dict(spin=25) for role in CAROUSEL},
                      "Bulb": dict(spin=25, pulse=0.45, period=1.2),
                      "SteedA": dict(spin=25, bob=0.5, period=2), "SaddleA": dict(spin=25, bob=0.5, period=2),
                      "SteedB": dict(spin=25, bob=-0.5, period=2), "SaddleB": dict(spin=25, bob=-0.5, period=2)},
    "prop_BulbPost": {"Placard": dict(swing=14, period=2.8, axis="across", height=7.9),
                      "PlacardTrim": dict(swing=14, period=2.8, axis="across", height=7.9),
                      "Neon": dict(swing=14, period=2.8, axis="across", height=7.9, pulse=0.5),
                      "CrowHead": dict(swing=40, period=7), "Beak": dict(swing=40, period=7), "Gaze": dict(swing=40, period=7),
                      "Lamp": dict(pulse=0.75, period=3)},
    "prop_CircusRing": {"Bulb": dict(spin=14, pulse=0.5, period=1.2), "StarRing": dict(spin=-10), "Star": dict(spin=6)},
    "prop_SwingRide": {**{role: dict(spin=45) for role in SWINGS}, "Bulb": dict(spin=45, pulse=0.5, period=1)},
    "prop_HotAirBalloon": {**{role: dict(swing=3, period=6, axis="across") for role in BALLOON},
                           "Flame": dict(swing=3, period=6, axis="across", pulse=0.4),
                           "Bulb": dict(swing=3, period=6, axis="across", pulse=0.5)},
    "prop_HelterSkelter": {"Flag": dict(swing=25, period=3), "Bulb": dict(pulse=0.4, period=1.4)},
    "prop_FerrisWheel": {**{role: dict(spin=8, axis="ahead", height=17) for role in WHEEL},
                         "Bulb": dict(spin=8, axis="ahead", height=17, pulse=0.5, period=1.5)},
    "prop_BigTop": {"Flag": dict(swing=25, period=3.4), "Searchbeam": dict(spin=18), "Bulb": dict(pulse=0.4, period=1.5),
                    "Neon": dict(pulse=0.5, period=2), "Lamp": dict(pulse=0.75, period=2.6)},
    "prop_FunHouse": {"SpiralL": dict(spin=90, axis="ahead", about="self"), "SpiralR": dict(spin=-90, axis="ahead", about="self"),
                      "Neon": dict(pulse=0.4, period=1.8), "Bulb": dict(pulse=0.4, period=1.1)},
    "prop_StageMoon": {**{role: dict(swing=4, period=7, axis="ahead", height=110) for role in MOON},
                       "Crescent": dict(swing=4, period=7, axis="ahead", height=110, pulse=0.8),
                       "LampStar": dict(swing=4, period=7, axis="ahead", height=110, pulse=0.4)},
    "prop_PopcornFall": {"Kernels": dict(fall=4, period=0.9), "Bulb": dict(pulse=0.4, period=1.2)},
    "prop_CoasterLoop": {**{role: dict(spin=60, axis="ahead", height=23.4) for role in RIDERS},
                         "Bulb": dict(pulse=0.4, period=1)},
}


def prop(name, **colours):
    return mk.prop(name, **colours)


# ---------------------------------------------------------------------- shape helpers


def obox(m, role, centre, axes, size):
    """A box round centre with its edges along three directions (unit vectors), size (w, d, h) along them."""
    c = Vector(centre)
    u, v, w = (Vector(a) for a in axes)
    sx, sy, sz = (s / 2 for s in size)
    verts = []
    for dz in (-sz, sz):
        for dx, dy in ((-sx, -sy), (sx, -sy), (sx, sy), (-sx, sy)):
            verts.append(tuple(c + u * dx + v * dy + w * dz))
    faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    m._add(role, verts, faces)


def box(m, role, x, y, z, w, d, h, yaw=0.0):
    """A block turned yaw radians round its upright."""
    c, s = math.cos(yaw), math.sin(yaw)
    obox(m, role, (x, y, z), ((c, s, 0), (-s, c, 0), (0, 0, 1)), (w, d, h))


class Frame:
    """Local directions for something turned or tipped: a horse going round, a cart in a loop."""

    def __init__(self, origin, u, v, w):
        self.o, self.u, self.v, self.w = Vector(origin), Vector(u), Vector(v), Vector(w)

    def p(self, a, b, c):
        return tuple(self.o + self.u * a + self.v * b + self.w * c)

    def box(self, m, role, a, b, c, size):
        obox(m, role, self.p(a, b, c), (self.u, self.v, self.w), size)


def wedge(m, role, x, y, z0, z1, r0, r1, a0, a1, base=(0, 0), top=(0, 0)):
    """A solid slice of a round column between angles a0 and a1: one stripe of a tent's wall or roof. base and
    top shift the bottom and top rings sideways (a leaning hat)."""
    def ring(r, z, shift):
        cx, cy = x + shift[0], y + shift[1]
        return [(cx, cy, z), (cx + r * math.cos(a0), cy + r * math.sin(a0), z), (cx + r * math.cos(a1), cy + r * math.sin(a1), z)]

    verts = ring(r0, z0, base) + ring(r1, z1, top)
    faces = [[0, 2, 1], [3, 4, 5], [0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5]]
    m._add(role, verts, faces)


def lathe(m, roles, x, y, profile, n, turn=0.0, lean=(0, 0)):
    """A round shape from a profile of (z, radius), cut into n stripes that take turns through roles: tents,
    canopies, balloons. lean moves the top sideways by that much, the rest in proportion."""
    z_lo, z_hi = profile[0][0], profile[-1][0]

    def shift(z):
        t = (z - z_lo) / (z_hi - z_lo) if z_hi != z_lo else 0
        return (lean[0] * t, lean[1] * t)

    for k in range(n):
        a0 = turn + k * math.tau / n
        role = roles[k % len(roles)]
        for (z0, r0), (z1, r1) in zip(profile, profile[1:]):
            wedge(m, role, x, y, z0, z1, max(r0, 0.05), max(r1, 0.05), a0, a0 + math.tau / n, shift(z0), shift(z1))


def scallops(m, role, x, y, z, r, n, depth, turn=0.0):
    """A valance of hanging points round an eave of n sides (the eave of a lathe with the same n and turn)."""
    chord = 2 * r * math.sin(math.pi / n)
    face = r * math.cos(math.pi / n) + 0.06
    for k in range(n):
        a = turn + (k + 0.5) * math.tau / n
        px, py = x + math.cos(a) * face, y + math.sin(a) * face
        plate(m, role, (px, py, z), (px, py, z - depth), (-math.sin(a), math.cos(a), 0), chord * 0.92, 0.08, 0.12)


def bulb(m, role, x, y, z, s=0.24):
    """One carnival bulb: a little six-sided gem, cheap enough to string hundreds."""
    gem(m, role, x, y, z, s, s * 1.15, s * 1.15, 6)


def bulb_ring(m, role, x, y, z, r, n, s=0.24, turn=0.0):
    for k in range(n):
        a = turn + k * math.tau / n
        bulb(m, role, x + math.cos(a) * r, y + math.sin(a) * r, z, s)


def bulb_line(m, role, a, b, n, s=0.24):
    for k in range(n):
        t = k / max(n - 1, 1)
        bulb(m, role, *(a[i] + (b[i] - a[i]) * t for i in range(3)), s)


def balloon(m, role, x, y, z, r, sides=8, rings=6):
    """A balloon: a ball a little taller than wide, and its knot."""
    for k in range(rings):
        a0 = -math.pi / 2 + k * math.pi / rings
        a1 = a0 + math.pi / rings
        prism(m, role, x, y, z + 1.2 * r * math.sin(a0), z + 1.2 * r * math.sin(a1), max(r * math.cos(a0), 0.05),
              max(r * math.cos(a1), 0.05), sides, math.pi / sides)
    m.loft_z(role, (z - 1.2 * r - 0.3, x, y, 0.32, 0.32), (z - 1.2 * r + 0.05, x, y, 0.1, 0.1))


def pennants(m, rope, roles, a, b, sag, n, size):
    """A sagging rope from a to b with n triangular flags hanging off it, taking turns through roles."""
    def at(t):
        return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))[:2] + (a[2] + (b[2] - a[2]) * t - sag * 4 * t * (1 - t),)

    for k in range(8):
        beam(m, rope, at(k / 8), at((k + 1) / 8), 0.1)
    along = Vector(b) - Vector(a)
    along.z = 0
    side = along.normalized() if along.length > 1e-6 else Vector((1, 0, 0))
    for k in range(n):
        p = at((k + 0.5) / n)
        p = (p[0], p[1], p[2] - 0.02)
        plate(m, roles[k % len(roles)], p, (p[0], p[1], p[2] - size * 1.3), tuple(side), size, 0.06, 0.08)


def popcorn(m, rng, x, y, z, s, roles=("Popcorn", "Popcorn", "Butter")):
    """One fluffy piece of popcorn: three tilted cubes, chunky and cheap (a waterfall of it stays well under
    Studio's triangle limit per part)."""
    role = rng.choice(roles)
    for k in range(3):
        turn = Euler((rng.uniform(0, 3), rng.uniform(0, 3), rng.uniform(0, 3))).to_matrix()
        axes = [tuple(turn.col[i]) for i in range(3)]
        c = (x + rng.uniform(-0.45, 0.45) * s, y + rng.uniform(-0.45, 0.45) * s, z + rng.uniform(-0.3, 0.45) * s)
        size = s * (1.15 if k == 0 else 0.85)
        obox(m, role, c, axes, (size, size, size))


def crate(m, x, y, z, s, yaw=0.0, body="Crate", edge="CrateDark"):
    """A wooden crate standing on z, its frame darker, with a brace across its front."""
    box(m, body, x, y, z + s / 2, s, s, s, yaw)
    c, sn = math.cos(yaw), math.sin(yaw)
    for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        px, py = x + (dx * c - dy * sn) * s * 0.47, y + (dx * sn + dy * c) * s * 0.47
        box(m, edge, px, py, z + s / 2, s * 0.12, s * 0.12, s * 1.01, yaw)
    for dz in (0.06, 0.94):
        box(m, edge, x, y, z + s * dz, s * 1.02, s * 1.02, s * 0.1, yaw)


def spiral_eye(m, role, cx, y, cz, r, arms=4):
    """A hypnotic spiral of `arms` black arms, flat in the XZ plane facing +Y. Turned about its own middle it
    seems to wind in for ever. Four arms keep its middle in the middle, so it turns on the spot in the game."""
    for k in range(arms):
        off = k * math.tau / arms
        steps = 7
        pts = []
        for i in range(steps + 1):
            t = i / steps
            a = off + t * 1.5 * math.pi
            rr = r * (0.08 + 0.92 * t)
            pts.append((cx + math.cos(a) * rr, y, cz + math.sin(a) * rr))
        for i in range(steps):
            a, b = pts[i], pts[i + 1]
            along = (b[0] - a[0], b[2] - a[2])
            side = (-along[1], 0, along[0])
            w0, w1 = r * (0.06 + 0.2 * i / steps), r * (0.06 + 0.2 * (i + 1) / steps)
            plate(m, role, a, b, side, w0, w1, 0.12)


# ---------------------------------------------------------------------- floor props


def striped_tent(seed=1):
    """The map's signature: a round crimson-and-cream tent, a gold valance and bulbs round its eaves, its door
    glowing warm between curtains tied back, and a teal pennant on top that waves round its pole."""
    m = prop("StripedTent", Canvas=CRIMSON, CanvasLight=CREAM, Trim=GOLD, Pole=IRON, Flag=TEAL, Bulb=BULB, Doorway=SHADOW,
             Lamp=LAMP, Curtain=CRIMSON_DARK, Rope=ROPE, Peg=WOOD_DARK)
    n = 12
    turn = math.pi / 2 - math.pi / n  # a cream panel straight ahead, for the door
    lathe(m, ("CanvasLight", "Canvas"), 0, 0, [(0, 4.2), (4.4, 4.0)], n, turn)
    lathe(m, ("CanvasLight", "Canvas"), 0, 0, [(4.4, 4.9), (6.4, 3.5), (8.8, 1.5), (10.4, 0.2)], n, turn)
    scallops(m, "Trim", 0, 0, 4.4, 4.9, n, 0.9, turn)
    bulb_ring(m, "Bulb", 0, 0, 4.32, 4.98, n, 0.26, turn)
    ball(m, "Trim", 0, 0, 10.4, 0.45, 8, 4)
    beam(m, "Pole", (0, 0, 10.4), (0, 0, 13.3), 0.18)
    ball(m, "Trim", 0, 0, 13.35, 0.22, 6, 3)
    plate(m, "Flag", (0.1, 0, 12.9), (2.7, 0, 12.45), (0, 0, 1), 1.3, 0.1, 0.08)
    # The door on the front panel, lit from inside, curtains tied back.
    m.block("Doorway", 0, 3.95, 1.6, 2.0, 0.3, 3.2)
    m.block("Lamp", 0, 4.08, 1.45, 1.4, 0.1, 2.6)
    for side in (-1, 1):
        plate(m, "Curtain", (side * 0.75, 4.18, 3.25), (side * 1.25, 4.18, 0.3), (1, 0, 0), 1.1, 0.45, 0.12)
        m.block("Trim", side * 1.2, 4.26, 1.5, 0.5, 0.12, 0.25)
    m.block("Trim", 0, 4.05, 3.65, 2.4, 0.2, 0.35)
    for a in (math.radians(40), math.radians(140), math.radians(220), math.radians(320)):  # guy ropes and pegs
        c, s = math.cos(a), math.sin(a)
        beam(m, "Rope", (c * 4.85, s * 4.85, 4.3), (c * 6.7, s * 6.7, 0.25), 0.1)
        m.block("Peg", c * 6.75, s * 6.75, 0.25, 0.3, 0.3, 0.5)
    return m


def jack_box(seed=2):
    """A giant jack-in-the-box: a crimson toy box with gold edges, its lid thrown back, and a clown on a spring
    that bobs and wobbles from side to side for ever: chalk-white face, cross-eyed stare, red nose, a grin far
    too wide, purple curls, a ruff and a little striped hat. The crank on its side keeps turning by itself."""
    m = prop("JackBox", Box=CRIMSON, BoxPanel=CREAM, Trim=GOLD, Diamond=TEAL, Lid=CRIMSON_DARK, Spring="#c9ccd6",
             ClownFace="#f6f1ea", Hair=HAIR, Nose="#e23a3a", Grin=SHADOW, Teeth="#fffaf0", EyeWhite="#ffffff", Pupil="#17141f",
             Ruffle=CRIMSON, RuffleB=CREAM, Crank=GOLD)
    s = 4.4
    m.block("Box", 0, 0, s / 2, s, s, s)
    for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        m.block("Trim", dx * s / 2, dy * s / 2, s / 2, 0.36, 0.36, s + 0.05)
    for z in (0.15, s):
        for dy in (-1, 1):
            m.block("Trim", 0, dy * s / 2, z, s + 0.1, 0.32, 0.32)
        for dx in (-1, 1):
            m.block("Trim", dx * s / 2, 0, z, 0.32, s + 0.1, 0.32)
    for face in (-1, 1):  # a cream panel with a teal diamond on each side
        y = face * (s / 2 + 0.03)
        m.block("BoxPanel", 0, y, s / 2, 3.0, 0.1, 3.0)
        plate(m, "Diamond", (0, y + face * 0.06, 1.0), (0, y + face * 0.06, s / 2), (1, 0, 0), 0.1, 1.9, 0.08)
        plate(m, "Diamond", (0, y + face * 0.06, s / 2), (0, y + face * 0.06, 3.4), (1, 0, 0), 1.9, 0.1, 0.08)
        x = face * (s / 2 + 0.03)
        m.block("BoxPanel", x, 0, s / 2, 0.1, 3.0, 3.0)
        plate(m, "Diamond", (x + face * 0.06, 0, 1.0), (x + face * 0.06, 0, s / 2), (0, 1, 0), 0.1, 1.9, 0.08)
        plate(m, "Diamond", (x + face * 0.06, 0, s / 2), (x + face * 0.06, 0, 3.4), (0, 1, 0), 1.9, 0.1, 0.08)
    # The lid, thrown back on its hinge, its cream lining towards us.
    plate(m, "Lid", (0, -2.35, 4.5), (0, -3.6, 8.7), (1, 0, 0), 4.6, 4.6, 0.4)
    plate(m, "BoxPanel", (0, -2.05, 5.0), (0, -3.15, 8.3), (1, 0, 0), 3.4, 3.4, 0.1)
    # The crank: two arms, so it turns on its own middle.
    beam(m, "Crank", (2.2, 0, 2.6), (2.95, 0, 2.6), 0.32)
    beam(m, "Crank", (2.9, 0, 1.4), (2.9, 0, 3.8), 0.3)
    for z in (1.4, 3.8):
        beam(m, "Crank", (2.9, 0, z), (3.6, 0, z), 0.36)
    # The spring, from inside the box (so its foot never shows when it bobs) up to the ruff.
    turns, steps = 4.5, 54
    for i in range(steps):
        a0, a1 = i / steps * turns * math.tau, (i + 1) / steps * turns * math.tau
        z0, z1 = 3.8 + 3.8 * i / steps, 3.8 + 3.8 * (i + 1) / steps
        beam(m, "Spring", (math.cos(a0), math.sin(a0), z0), (math.cos(a1), math.sin(a1), z1), 0.3)
    for k in range(14):  # the ruff
        a = k * math.tau / 14
        role = "Ruffle" if k % 2 else "RuffleB"
        plate(m, role, (math.cos(a) * 0.5, math.sin(a) * 0.5, 7.75), (math.cos(a) * 2.5, math.sin(a) * 2.5, 7.45),
              (-math.sin(a), math.cos(a), 0), 0.5, 1.25, 0.22)
    # The head.
    hz, r = 9.55, 1.9
    ball(m, "ClownFace", 0, 0, hz, r, 10, 7)

    def front(x, dz, out=0.0):  # y on the face's front at x, dz above the head's middle
        return math.sqrt(max(r * r * 0.9 - x * x - dz * dz, 0.05)) + out

    for side, look in ((-1, (0.18, 0.12)), (1, (-0.2, 0.16))):  # cross-eyed: both looking in and up
        ex, ez = side * 0.66, 0.38
        disc(m, "EyeWhite", ex, front(ex, ez, 0.06), hz + ez, 0.58, 0.3, 12, "xz")
        disc(m, "Pupil", ex + look[0], front(ex, ez, 0.24), hz + ez + look[1], 0.25, 0.1, 10, "xz")
        b0, b1, b2 = (side * 0.3, 1.05), (side * 0.7, 1.35), (side * 1.1, 1.08)  # high arched brows: a mad stare
        for (x0, z0), (x1, z1) in ((b0, b1), (b1, b2)):
            beam(m, "Grin", (x0, front(x0, z0, 0.05), hz + z0), (x1, front(x1, z1, 0.05), hz + z1), 0.18)
        disc(m, "Nose", side * 1.15, front(side * 1.15, -0.35, 0.02), hz - 0.35, 0.36, 0.1, 10, "xz")  # cheeks
    ball(m, "Nose", 0, front(0, -0.1, 0.25), hz - 0.1, 0.5, 8, 5)
    for i in range(11):  # the grin: a dark crescent, corners up to the cheeks, a row of teeth along its top
        x = -1.25 + i * 0.25
        k = (x / 1.25) ** 2
        top, bottom = -0.55 + 0.35 * k, -1.1 + 0.75 * k
        m.block("Grin", x, front(x, (top + bottom) / 2, 0.02), hz + (top + bottom) / 2, 0.27, 0.3, max(top - bottom, 0.12))
        if i % 2 == 0 and 0 < i < 10:
            m.block("Teeth", x, front(x, top - 0.12, 0.12), hz + top - 0.12, 0.22, 0.2, 0.22)
    for side in (-1, 1):  # purple curls
        for x, y, z, rr in ((1.9, -0.2, 9.9, 0.8), (1.6, -0.7, 10.75, 0.72), (2.15, 0.2, 9.1, 0.62), (1.0, -1.3, 11.1, 0.6)):
            ball(m, "Hair", side * x, y, z, rr, 8, 4)
    lathe(m, ("Ruffle", "RuffleB"), 0.1, -0.2, [(11.15, 0.75), (13.0, 0.06)], 8, 0.0, (0.55, -0.15))
    ball(m, "RuffleB", 0.65, -0.35, 13.05, 0.3, 6, 3)
    return m


def popcorn_cart(seed=3):
    """A popcorn cart on two big wheels under a striped canopy, its kettle popping for ever: kernels fly up out of
    it and vanish into the canopy. A bulb glows on top."""
    m = prop("PopcornCart", CartBody=CRIMSON, Panel=CREAM, Trim=GOLD, Wheel=CRIMSON_DARK, Spokes=GOLD, Handle=WOOD, Kettle="#c9ccd6",
             Popcorn=POPCORN, Butter=BUTTER, Kernels=POPCORN, Canvas=CRIMSON, CanvasLight=CREAM, Bulb=BULB, Post=GOLD)
    rng = random.Random(seed)
    for x in (-2.1, 2.1):  # wheels
        hoop(m, "Wheel", x, 0, 1.5, 1.4, 0.28, "yz", 14)
        for k in range(8):
            a = k * math.tau / 8
            beam(m, "Spokes", (x, 0, 1.5), (x, math.cos(a) * 1.35, 1.5 + math.sin(a) * 1.35), 0.14)
        m.block("Trim", x, 0, 1.5, 0.4, 0.45, 0.45)
    beam(m, "Trim", (-2.1, 0, 1.5), (2.1, 0, 1.5), 0.2)
    m.block("CartBody", 0, 0, 3.0, 3.6, 2.4, 2.0)
    for z in (2.05, 3.95):
        m.block("Trim", 0, 0, z, 3.75, 2.55, 0.2)
    for face in (-1, 1):
        m.block("Panel", 0, face * 1.23, 3.0, 2.8, 0.08, 1.3)
        star_prism(m, "Trim", (0, face * 1.3, 3.0), 0.55, 0.24, 0.08)
    for x in (-1.2, 1.2):  # the handle at the back
        beam(m, "Handle", (x, -1.2, 3.5), (x, -3.0, 3.9), 0.18)
    beam(m, "Handle", (-1.25, -3.0, 3.9), (1.25, -3.0, 3.9), 0.2)
    beam(m, "Handle", (0, 1.0, 2.0), (0, 1.4, 0.1), 0.25)  # its leg at the front
    # Corner posts, the heap of popcorn, and the kettle.
    for dx, dy in ((-1.65, -1.05), (1.65, -1.05), (1.65, 1.05), (-1.65, 1.05)):
        m.block("Post", dx, dy, 6.9, 0.18, 0.18, 5.8)
    for _ in range(26):
        popcorn(m, rng, rng.uniform(-1.4, 1.4), rng.uniform(-0.85, 0.85), rng.uniform(4.1, 4.9), rng.uniform(0.28, 0.4))
    beam(m, "Kettle", (0, 0, 9.8), (0, 0, 6.6), 0.12)
    prism(m, "Kettle", 0, 0, 5.8, 6.6, 0.55, 0.85, 8, math.pi / 8)
    for k in range(6):
        a = k * math.tau / 6
        ball(m, "Popcorn" if k % 2 else "Butter", math.cos(a) * 0.55, math.sin(a) * 0.55, 6.65, 0.26, 6, 3)
    # Kernels flying up, rows 1.2 apart: the game raises them 1.2 and starts over, so new ones come out of the
    # kettle (the lowest row is inside it) as the top ones vanish into the canopy.
    for k, z in enumerate((6.3, 7.5, 8.7)):
        for j in range(5):
            a = j * math.tau / 5 + k * 0.9
            rr = 0.35 + 0.25 * k + (j % 2) * 0.15
            m.block("Kernels", math.cos(a) * rr, math.sin(a) * rr, z + (j % 3) * 0.25, 0.3, 0.3, 0.3)
    n = 8
    lathe(m, ("Canvas", "CanvasLight"), 0, 0, [(9.8, 2.9), (11.3, 0.12)], n, math.pi / 8)
    scallops(m, "Trim", 0, 0, 9.8, 2.9, n, 0.6, math.pi / 8)
    bulb(m, "Bulb", 0, 0, 11.6, 0.4)
    bulb_ring(m, "Bulb", 0, 0, 9.72, 2.95, n, 0.2, math.pi / 8)
    return m


def fortune_booth(seed=4):
    """A fortune teller's cabinet: plum and gold with an onion dome, a bulb-lit sign, and inside it a porcelain
    seer in a teal turban, eyes half shut and glowing, hands round a crystal ball that slowly brightens and dims.
    The seer's head turns slowly from side to side. It sits straight above the prop's origin, so it turns on
    the spot in the game."""
    m = prop("FortuneBooth", Cabinet=PLUM, Trim=GOLD, Velvet=PLUM_DARK, Stars=GOLD, Dome=TEAL, DomeB=GOLD, Robe=CRIMSON_DARK,
             TellerHands="#efe3d0", TellerFace="#efe3d0", Turban=TEAL, Jewel=GOLD, Moustache="#2a1f2e", Trance="#e9d8ff",
             Seer="#b9a2ff", Sign=CRIMSON, Bulb=BULB)
    m.block("Cabinet", 0, 0, 2.0, 3.6, 2.8, 4.0)
    for z in (0.2, 3.9):
        m.block("Trim", 0, 0, z, 3.8, 3.0, 0.3)
    m.block("Velvet", 0, 1.43, 2.0, 2.6, 0.08, 2.6)
    for x, z, s in ((-0.7, 2.6, 0.45), (0.5, 1.6, 0.6), (0.8, 2.9, 0.3), (-0.5, 1.2, 0.3), (0.0, 2.2, 0.25)):
        star_prism(m, "Stars", (x, 1.5, z), s, s * 0.42, 0.08)
    # The glass case (no glass): gold posts, velvet back and sides, a cap and the dome.
    for dx, dy in ((-1.65, -1.25), (1.65, -1.25), (1.65, 1.25), (-1.65, 1.25)):
        m.block("Trim", dx, dy, 6.3, 0.3, 0.3, 4.6)
    m.block("Velvet", 0, -1.28, 6.3, 3.2, 0.2, 4.6)
    for side in (-1, 1):
        m.block("Velvet", side * 1.7, -0.6, 6.3, 0.15, 1.2, 4.6)
    m.block("Cabinet", 0, 0, 8.8, 3.8, 3.0, 0.4)
    m.block("Trim", 0, 0, 9.05, 3.4, 2.6, 0.2)
    lathe(m, ("Dome", "DomeB"), 0, 0, [(9.1, 1.3), (9.8, 1.6), (10.6, 1.25), (11.4, 0.45), (12.2, 0.05)], 8, math.pi / 8)
    ball(m, "Trim", 0, 0, 12.3, 0.25, 6, 3)
    # The sign over the case, bulbs round it.
    m.block("Sign", 0, 1.55, 9.7, 3.0, 0.2, 0.9)
    gem(m, "Trim", 0, 1.68, 9.7, 0.32, 0.3, 0.3, 4, math.pi / 4)
    for k in range(10):
        t = k / 10
        x = -1.5 + 3.0 * t
        bulb(m, "Bulb", x, 1.7, 10.2, 0.16)
        bulb(m, "Bulb", x + 0.3, 1.7, 9.2, 0.16)
    # The table and crystal ball.
    m.block("Velvet", 0, 0.75, 4.3, 2.6, 1.0, 0.6)
    prism(m, "Trim", 0, 0.75, 4.6, 4.85, 0.35, 0.25, 6)
    ball(m, "Seer", 0, 0.75, 5.35, 0.55, 10, 6)
    # The seer: robe, arms round the ball, hands hovering.
    m.loft_z("Robe", (4.0, 0, -0.35, 1.7, 1.0), (6.3, 0, -0.25, 1.9, 0.9))
    for side in (-1, 1):
        beam(m, "Robe", (side * 0.95, -0.2, 6.1), (side * 1.05, 0.35, 5.2), 0.42)
        beam(m, "Robe", (side * 1.05, 0.35, 5.2), (side * 0.62, 0.72, 5.4), 0.36)
        m.block("TellerHands", side * 0.55, 0.75, 5.5, 0.3, 0.35, 0.4)
        for f in range(3):
            beam(m, "TellerHands", (side * 0.55, 0.75 + (f - 1) * 0.1, 5.68), (side * 0.48, 0.75 + (f - 1) * 0.14, 6.0), 0.08)
    m.block("TellerHands", 0, -0.15, 6.45, 0.4, 0.4, 0.4)  # neck
    # The head: face, level half-shut eyes, curled moustache, turban with a gold jewel and plume.
    hz = 7.05
    m.loft_z("TellerFace", (hz - 0.65, 0, 0, 0.9, 0.95), (hz - 0.1, 0, 0, 1.15, 1.2))
    m.loft_z("TellerFace", (hz - 0.1, 0, 0, 1.15, 1.2), (hz + 0.45, 0, 0, 1.1, 1.1))
    m.block("TellerFace", 0, 0.62, hz - 0.15, 0.24, 0.3, 0.45)  # nose
    for side in (-1, 1):
        m.block("Trance", side * 0.28, 0.6, hz + 0.08, 0.32, 0.06, 0.08)
        m.block("TellerFace", side * 0.28, 0.61, hz + 0.17, 0.38, 0.08, 0.1)  # a level lid: calm, far away
        beam(m, "Moustache", (side * 0.05, 0.64, hz - 0.36), (side * 0.42, 0.62, hz - 0.42), 0.12)
        beam(m, "Moustache", (side * 0.42, 0.62, hz - 0.42), (side * 0.58, 0.56, hz - 0.22), 0.1)
    m.block("Moustache", 0, 0.56, hz - 0.62, 0.18, 0.12, 0.25)
    dome(m, "Turban", 0, -0.05, hz + 0.3, 0.62)
    flat_ring(m, "Turban", 0, -0.02, hz + 0.45, 0.62, 0.32, 0.3, 10)
    gem(m, "Jewel", 0, 0.66, hz + 0.65, 0.18, 0.22, 0.22, 4, math.pi / 4)
    plate(m, "Jewel", (0, 0.58, hz + 0.8), (0.18, 0.3, hz + 1.7), (1, 0, 0), 0.24, 0.08, 0.06)
    return m


def high_striker(seed=5):
    """A strength tester: hit the pad with the mallet and the puck flies up the board to ring the bell. Here it
    rings by itself, over and over: the puck rises to the bell and drops back, the bell rocks each time it's hit.
    A gold star with bulbs crowns it, more bulbs run down both sides of the board."""
    m = prop("HighStriker", Base=WOOD_DARK, Pad=CRIMSON, Post=WOOD, Board=CREAM, BoardRed=CRIMSON, Trim=GOLD, Puck=TEAL, Bell=GOLD,
             Mallet=WOOD, MalletHead=CRIMSON, Star=GOLD, Bulb=BULB)
    m.block("Base", 0, 0, 0.3, 4.2, 3.2, 0.6)
    m.block("Pad", 0, 1.0, 0.75, 1.2, 1.1, 0.3)
    m.block("Trim", 0, 1.0, 0.95, 0.5, 0.5, 0.15)
    m.block("Post", 0, -0.65, 6.9, 1.7, 0.6, 13.2)
    for k in range(8):  # the scale, crimson at the bottom up to cream at the bell
        z = 1.5 + k * 1.3
        m.block("BoardRed" if k % 2 == 0 else "Board", 0, -0.27, z + 0.65, 1.5, 0.22, 1.3)
        m.block("Trim", 0, -0.14, z + 1.3, 1.5, 0.1, 0.12)
    for x in (-0.3, 0.3):  # the guide the puck runs up
        m.block("Trim", x, -0.08, 6.9, 0.1, 0.12, 11.0)
    m.block("Puck", 0, 0.1, 6.8, 0.9, 0.45, 0.65)
    m.block("Trim", 0, 0.34, 6.8, 0.5, 0.06, 0.25)
    # The bell: hinge at z 13.6 on a bracket off the post's top, straight above the prop's origin.
    beam(m, "Trim", (0, -0.65, 13.6), (0, 0.05, 13.6), 0.3)
    m.block("Bell", 0, 0, 13.35, 0.2, 0.2, 0.5)
    prism(m, "Bell", 0, 0, 12.25, 13.15, 0.95, 0.55, 10, 0.0)
    prism(m, "Bell", 0, 0, 12.15, 12.35, 1.05, 1.05, 10, 0.0)
    star_prism(m, "Star", (0, -0.65, 15.4), 1.5, 0.65, 0.45)
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        rr = 1.75 if k % 2 == 0 else 0.85
        bulb(m, "Bulb", math.cos(a) * rr, -0.35, 15.4 + math.sin(a) * rr, 0.17)
    for x in (-0.9, 0.9):
        for k in range(9):
            bulb(m, "Bulb", x, -0.3, 1.7 + k * 1.3, 0.17)
    # The mallet, its head on the ground and its handle leaning on the post.
    beam(m, "MalletHead", (1.05, 1.5, 0.95), (2.4, 0.55, 0.95), 0.95)
    for t in (0.18, 0.82):
        a, b = (1.05, 1.5, 0.95), (2.4, 0.55, 0.95)
        p = tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
        beam(m, "Trim", tuple(p[i] - (b[i] - a[i]) * 0.04 for i in range(3)), tuple(p[i] + (b[i] - a[i]) * 0.04 for i in range(3)), 1.0)
    beam(m, "Mallet", (1.72, 1.03, 1.3), (0.95, -0.2, 4.9), 0.24)
    return m


def balloon_cart(seed=6):
    """A balloon seller's little cart, nobody at it, its bunch of balloons tied to the pole swaying in the night
    air. One of them has a grin drawn on it. The strings meet at a knot straight above the prop's origin, and
    each colour sways round that knot in its own time."""
    m = prop("BalloonCart", CartBody=TEAL, Trim=GOLD, Wheel=CRIMSON_DARK, Pole=GOLD, Canvas=CRIMSON, CanvasLight=CREAM,
             BalloonA="#e8394a", SmileA=SHADOW, StringA="#ece4d4", BalloonB="#3fc4c0", StringB="#ece4d4",
             BalloonC="#f5c242", StringC="#ece4d4", BalloonD="#9a5ad8", StringD="#ece4d4")
    for x in (-1.3, 1.3):
        hoop(m, "Wheel", x, 0, 0.75, 0.7, 0.22, "yz", 10)
    beam(m, "Trim", (-1.3, 0, 0.75), (1.3, 0, 0.75), 0.16)
    m.block("CartBody", 0, 0, 1.75, 2.3, 1.7, 1.3)
    for z in (1.15, 2.35):
        m.block("Trim", 0, 0, z, 2.4, 1.8, 0.14)
    lathe(m, ("Canvas", "CanvasLight"), 0, 0, [(2.4, 1.5), (2.9, 1.2)], 8, math.pi / 8)
    beam(m, "Pole", (0, 0, 2.9), (0, 0, 4.35), 0.16)
    ball(m, "Trim", 0, 0, 4.25, 0.2, 6, 3)
    knot = (0, 0, 4.2)
    bunch = [("A", 0.0, 0.5, 10.4, 1.25), ("A", -2.2, -0.5, 8.4, 0.9), ("B", 2.0, -0.3, 9.0, 0.95), ("B", -0.7, -1.7, 9.9, 0.9),
             ("B", 1.0, 1.5, 7.7, 0.85), ("C", -2.0, 1.3, 9.6, 0.9), ("C", 2.6, 1.2, 11.0, 0.85), ("C", -0.3, -1.0, 12.4, 0.95),
             ("D", 1.4, -1.9, 11.6, 0.85), ("D", -2.9, -0.6, 11.4, 0.85)]
    for group, x, y, z, r in bunch:
        balloon(m, f"Balloon{group}", x, y, z, r)
        beam(m, f"String{group}", knot, (x, y, z - 1.2 * r - 0.3), 0.06)
    # The grin on the big red balloon, facing +Y.
    gx, gz, gr = 0.0, 10.4, 1.25
    for side in (-1, 1):
        m.block("SmileA", side * 0.38, 0.5 + gr * 0.92, gz + 0.35, 0.18, 0.12, 0.38)
    for i in range(7):
        x = -0.6 + i * 0.2
        z = gz - 0.35 + 0.35 * (x / 0.6) ** 2
        m.block("SmileA", x, 0.5 + math.sqrt(max(gr * gr * 0.85 - x * x - 0.3, 0.1)), z, 0.22, 0.12, 0.14)
    return m


def steed(m, body, saddle, cx, cy, cz, heading):
    """A chunky carousel horse at a gallop, its centre at (cx, cy, cz), facing heading (radians)."""
    f = Frame((cx, cy, cz), (math.cos(heading), math.sin(heading), 0), (-math.sin(heading), math.cos(heading), 0), (0, 0, 1))
    f.box(m, body, 0, 0, 0, (2.0, 0.8, 0.95))
    f.box(m, body, 0.85, 0, 0.08, (0.6, 0.72, 0.85))
    beam(m, body, f.p(0.8, 0, 0.3), f.p(1.25, 0, 1.25), 0.6, 0.55)
    f.box(m, body, 1.45, 0, 1.28, (0.85, 0.5, 0.55))
    beam(m, body, f.p(1.7, 0, 1.18), f.p(2.1, 0, 0.98), 0.45, 0.4)
    for side in (-1, 1):
        f.box(m, body, 1.25, side * 0.16, 1.62, (0.16, 0.12, 0.35))
        beam(m, body, f.p(0.7, side * 0.24, -0.35), f.p(1.15, side * 0.24, -0.75), 0.28)  # front legs tucked up
        beam(m, body, f.p(1.15, side * 0.24, -0.75), f.p(0.95, side * 0.24, -1.2), 0.24)
        beam(m, body, f.p(-0.75, side * 0.24, -0.35), f.p(-1.05, side * 0.24, -1.0), 0.3)  # back legs stretched
        beam(m, body, f.p(-1.05, side * 0.24, -1.0), f.p(-1.45, side * 0.24, -1.42), 0.25)
        f.box(m, saddle, -0.05, side * 0.43, 0.2, (0.75, 0.08, 0.55))
    beam(m, saddle, f.p(0.72, 0, 0.62), f.p(1.28, 0, 1.6), 0.26, 0.3)  # mane
    beam(m, saddle, f.p(-1.0, 0, 0.3), f.p(-1.55, 0, -0.65), 0.32, 0.32, 0.12)  # tail
    f.box(m, saddle, -0.05, 0, 0.55, (0.8, 0.95, 0.2))


def carousel(seed=7):
    """A rare treat on the floor: a carousel still turning, gold poles and galloping horses rising and falling in
    turn under a striped canopy ringed with bulbs, mirrors round its middle."""
    m = prop("Carousel", Plinth=PLUM_DARK, Step=PLUM, Deck=TEAL, Trim=GOLD, Column=CRIMSON, Mirror="#bfe3ef", Poles=GOLD,
             Canopy=CRIMSON, CanopyLight=CREAM, Valance=GOLD, Finial=GOLD, Bulb=BULB, SteedA="#f3ead8", SaddleA=CRIMSON,
             SteedB="#3a2f4a", SaddleB=GOLD)
    prism(m, "Plinth", 0, 0, 0, 0.5, 6.4, 6.2, 16, math.pi / 16)
    prism(m, "Step", 0, 0, 0, 0.25, 6.9, 6.9, 16, math.pi / 16)
    prism(m, "Trim", 0, 0, 0.45, 0.55, 6.25, 6.25, 16, math.pi / 16)
    prism(m, "Deck", 0, 0, 0.5, 1.0, 5.8, 5.8, 16, math.pi / 16)
    prism(m, "Column", 0, 0, 1.0, 8.0, 1.2, 1.2, 8, math.pi / 8)
    for k in range(8):
        a = math.pi / 8 + k * math.tau / 8 + math.pi / 8
        box(m, "Mirror", math.cos(a) * 1.13, math.sin(a) * 1.13, 4.5, 0.75, 0.1, 4.2, a + math.pi / 2)
    for z in (1.4, 7.6):
        prism(m, "Deck", 0, 0, z - 0.2, z + 0.2, 1.35, 1.35, 8, math.pi / 8)
    for k in range(8):  # poles and horses, every other one dark, taking turns to rise
        a = math.pi / 8 + k * math.tau / 8
        x, y = math.cos(a) * 4.1, math.sin(a) * 4.1
        beam(m, "Poles", (x, y, 1.0), (x, y, 7.8), 0.16)
        steed(m, "SteedA" if k % 2 else "SteedB", "SaddleA" if k % 2 else "SaddleB", x, y, 3.6, a + math.pi / 2)
    n = 16
    lathe(m, ("Canopy", "CanopyLight"), 0, 0, [(7.6, 6.2), (8.4, 6.2)], n)
    lathe(m, ("Canopy", "CanopyLight"), 0, 0, [(8.4, 6.4), (9.6, 4.7), (11.0, 2.3), (12.0, 0.6), (12.2, 0.05)], n)
    scallops(m, "Valance", 0, 0, 7.6, 6.2, n, 0.9)
    bulb_ring(m, "Bulb", 0, 0, 8.0, 6.3, 32, 0.22)
    bulb_ring(m, "Bulb", 0, 0, 8.4, 6.5, n, 0.2)
    beam(m, "Finial", (0, 0, 12.1), (0, 0, 13.8), 0.16)
    ball(m, "Finial", 0, 0, 12.3, 0.4, 8, 4)
    plate(m, "Finial", (0.08, 0, 13.6), (1.4, 0, 13.35), (0, 0, 1), 0.7, 0.08, 0.06)
    return m


def crate_stack(seed=8):
    """Filler round the stalls and on the rims: crates, one stencilled with a gold star, a barrel, and a popcorn
    box knocked over and spilling."""
    m = prop("CrateStack", Crate=WOOD, CrateDark=WOOD_DARK, Barrel=CRIMSON_DARK, Hoop=IRON, Star=GOLD, BoxRed=CRIMSON,
             BoxCream=CREAM, Popcorn=POPCORN, Butter=BUTTER)
    rng = random.Random(seed)
    crate(m, 0, 0, 0, 3.0)
    crate(m, 2.75, 0.5, 0, 2.3, 0.3)
    crate(m, 0.2, -0.15, 3.0, 2.2, 0.35)
    star_prism(m, "Star", (0, 1.53, 1.5), 0.85, 0.37, 0.06)
    prism(m, "Barrel", -2.5, 1.0, 0, 1.3, 1.0, 1.15, 10)
    prism(m, "Barrel", -2.5, 1.0, 1.3, 2.6, 1.15, 1.0, 10)
    for z, r in ((0.35, 1.07), (1.3, 1.19), (2.25, 1.07)):
        prism(m, "Hoop", -2.5, 1.0, z - 0.1, z + 0.1, r, r, 10)
    # The popcorn box lying on its side, striped, its spill across the ground.
    for k in range(4):
        x = 1.2 + k * 0.4
        m.loft_y("BoxRed" if k % 2 == 0 else "BoxCream", (2.0, x, 0.6, 0.4, 1.1), (3.6, x + 0.15, 0.75, 0.4, 1.4))
    for _ in range(9):
        popcorn(m, rng, rng.uniform(0.6, 3.4), rng.uniform(3.7, 5.2), 0.2, rng.uniform(0.25, 0.38))
    return m


def bulb_post(seed=9):
    """An iron lamp post with a warm glass globe, a sign swinging on its arm with a pink neon arrow, and a crow
    on top that turns its head to watch what goes by, its eyes glinting. Its head sits straight above the prop's
    origin, so it turns on the spot."""
    m = prop("BulbPost", Post=IRON, Trim=GOLD, Lamp="#ffd98a", Placard=CRIMSON, PlacardTrim=GOLD, Neon=NEON, Crow="#1c1822",
             CrowHead="#1c1822", Beak="#e0a030", Gaze="#ffd23a")
    m.loft_z("Post", (0, 0, 0, 1.4, 1.4), (0.6, 0, 0, 1.0, 1.0))
    prism(m, "Post", 0, 0, 0.6, 9.7, 0.24, 0.2, 8)
    for z in (0.7, 2.6, 6.2, 9.6):
        prism(m, "Trim", 0, 0, z - 0.12, z + 0.12, 0.34, 0.34, 8)
    prism(m, "Post", 0, 0, 9.7, 9.95, 0.4, 0.55, 8)
    ball(m, "Lamp", 0, 0, 10.55, 0.75, 10, 6)
    prism(m, "Post", 0, 0, 11.25, 11.55, 0.6, 0.2, 8)
    # The arm and its scroll.
    beam(m, "Post", (0.15, 0, 8.25), (2.75, 0, 8.25), 0.18)
    beam(m, "Post", (0.15, 0, 7.2), (1.0, 0, 8.2), 0.14)
    beam(m, "Trim", (2.75, 0, 8.25), (2.95, 0, 8.25), 0.3)
    # The sign, hung at z 7.9: hooks, board, gold frame and a neon arrow on both faces.
    for x in (1.0, 2.4):
        beam(m, "PlacardTrim", (x, 0, 8.18), (x, 0, 7.55), 0.08)
    m.block("Placard", 1.7, 0, 6.6, 2.3, 0.2, 1.9)
    for dz in (-0.95, 0.95):
        m.block("PlacardTrim", 1.7, 0, 6.6 + dz, 2.45, 0.26, 0.14)
    for dx in (-1.15, 1.15):
        m.block("PlacardTrim", 1.7 + dx, 0, 6.6, 0.14, 0.26, 2.0)
    for face in (-1, 1):
        y = face * 0.13
        plate(m, "Neon", (1.0, y, 6.6), (2.0, y, 6.6), (0, 0, 1), 0.3, 0.3, 0.06)
        plate(m, "Neon", (1.95, y, 6.6), (2.55, y, 6.6), (0, 0, 1), 1.0, 0.08, 0.06)
    # The crow: body behind the middle, head straight above the origin.
    m.loft_y("Crow", (-0.75, 0, 11.85, 0.5, 0.45), (0.15, 0, 11.95, 0.75, 0.7))
    beam(m, "Crow", (0, -0.75, 11.95), (0, -1.45, 11.75), 0.5, 0.12, 0.6)  # tail
    for side in (-1, 1):
        beam(m, "Crow", (side * 0.33, 0.05, 12.1), (side * 0.36, -0.75, 11.8), 0.12, 0.5, 0.06)
        beam(m, "Beak", (side * 0.12, -0.05, 11.55), (side * 0.12, -0.05, 11.35), 0.08)
    m.block("CrowHead", 0, 0, 12.35, 0.48, 0.5, 0.48)
    beam(m, "Beak", (0, 0.24, 12.33), (0, 0.66, 12.25), 0.18, 0.16, 0.04)
    for side in (-1, 1):
        m.block("Gaze", side * 0.22, 0.12, 12.42, 0.08, 0.12, 0.1)
    return m


def circus_ring(seed=10):
    """A circus ring painted on the ground: crimson edge, a cream band of bulbs chasing round, a teal middle with
    a gold star that slowly turns and smaller stars turning the other way. Flat (under half a stud), so it can
    lie where the eggs land."""
    m = prop("CircusRing", RingRed=CRIMSON, RingCream=CREAM, RingTeal=TEAL_DARK, Trim=GOLD, Star=GOLD, StarRing="#f6d36b", Bulb=BULB)
    disc(m, "RingRed", 0, 0, 0.08, 7.0, 0.16, 32)
    disc(m, "RingCream", 0, 0, 0.13, 6.2, 0.12, 32)
    disc(m, "RingTeal", 0, 0, 0.16, 5.4, 0.12, 32)
    flat_ring(m, "Trim", 0, 0, 0.23, 5.4, 0.3, 0.08, 32)
    flat_ring(m, "Trim", 0, 0, 0.21, 6.95, 0.25, 0.08, 32)
    star_prism(m, "Star", (0, 0, 0.27), 3.2, 1.35, 0.12, (math.pi / 2, 0, 0))
    for k in range(8):
        a = k * math.tau / 8 + math.pi / 8
        star_prism(m, "StarRing", (math.cos(a) * 4.3, math.sin(a) * 4.3, 0.25), 0.6, 0.26, 0.08, (math.pi / 2, 0, a))
    for k in range(28):
        a = k * math.tau / 28
        disc(m, "Bulb", math.cos(a) * 6.6, math.sin(a) * 6.6, 0.22, 0.24, 0.14, 8)
    return m


# ---------------------------------------------------------------------- rim props and landmarks


def swing_ride(seed=11):
    """For the rims: a swing ride flinging its chairs out round a striped tower under a turning canopy ringed with
    bulbs. Some of the chairs have ghosts in them, arms up."""
    m = prop("SwingRide", Plinth=PLUM_DARK, Trim=GOLD, Canvas=TEAL, CanvasLight=CREAM, Canopy=PURPLE, CanopyLight=GOLD,
             Valance=GOLD, Finial=GOLD, Bulb=BULB, Chains="#9aa0ad", Seats=TEAL, SeatBack=GOLD, Ghost=GHOST, GhostEye=SHADOW)
    prism(m, "Plinth", 0, 0, 0, 0.6, 7.6, 7.4, 16, math.pi / 16)
    prism(m, "Trim", 0, 0, 0.3, 0.5, 7.7, 7.6, 16, math.pi / 16)
    prism(m, "Plinth", 0, 0, 0.6, 1.2, 2.6, 2.4, 8, math.pi / 8)
    lathe(m, ("Canvas", "CanvasLight"), 0, 0, [(1.2, 1.5), (12.45, 1.1)], 8)
    for z in (4.0, 8.0, 12.0):
        prism(m, "Trim", 0, 0, z - 0.2, z + 0.2, 1.45 - z * 0.03, 1.45 - z * 0.03, 8)
    n = 16
    lathe(m, ("Canopy", "CanopyLight"), 0, 0, [(12.5, 6.4), (13.5, 6.4)], n)
    lathe(m, ("Canopy", "CanopyLight"), 0, 0, [(13.5, 6.6), (15.0, 4.0), (16.6, 1.2), (17.2, 0.1)], n)
    scallops(m, "Valance", 0, 0, 12.5, 6.4, n, 0.9)
    bulb_ring(m, "Bulb", 0, 0, 13.0, 6.5, 32, 0.22)
    beam(m, "Finial", (0, 0, 17.0), (0, 0, 19.0), 0.2)
    ball(m, "Finial", 0, 0, 19.1, 0.45, 8, 4)
    for k in range(12):
        a = k * math.tau / 12 + 0.13
        out = Vector((math.cos(a), math.sin(a), 0))
        along = Vector((-math.sin(a), math.cos(a), 0))
        top = Vector((0, 0, 12.5)) + out * 6.0
        seat = Vector((0, 0, 6.2)) + out * 8.8
        for s in (-0.4, 0.4):
            beam(m, "Chains", tuple(top + along * s), tuple(seat + along * s + Vector((0, 0, 0.1))), 0.07)
        down = (top - seat).normalized()
        f = Frame(seat, along, out, down)
        f.box(m, "Seats", 0, 0, 0, (1.2, 1.0, 0.25))
        f.box(m, "SeatBack", 0, 0.5, 0.5, (1.2, 0.18, 1.0))
        if k % 3 == 0:  # a ghost rider, arms up
            f.box(m, "Ghost", 0, 0.05, 0.75, (0.8, 0.7, 1.1))
            ball(m, "Ghost", *f.p(0, 0.05, 1.6), 0.45, 8, 4)
            for side in (-1, 1):
                beam(m, "Ghost", f.p(side * 0.35, 0.05, 1.05), f.p(side * 0.65, -0.05, 2.0), 0.22, 0.22, 0.12)
                f.box(m, "GhostEye", side * 0.16, -0.38, 1.65, (0.12, 0.06, 0.2))
            f.box(m, "GhostEye", 0, -0.4, 1.38, (0.18, 0.06, 0.16))
    return m


def hot_air_balloon(seed=12):
    """For the rims: a striped hot-air balloon tethered to the ground, straining at its ropes and swaying, its
    burner flickering and a ring of bulbs round its middle. Sways round the ground under it, so its ropes stay
    on their sandbags."""
    m = prop("HotAirBalloon", Envelope=PURPLE, EnvelopeB=GOLD, Band=CRIMSON, Bulb=BULB, Rope=ROPE, Burner=IRON, Flame="#ffb347",
             Basket="#a0703e", BasketRim=WOOD_DARK, Sandbag="#cbb48a", Deck=WOOD, Weight="#b59c70")
    lathe(m, ("Envelope", "EnvelopeB"), 0, 0, [(12.0, 1.0), (13.2, 2.8), (15.2, 4.6), (18.0, 5.7), (21.0, 5.9), (23.6, 5.1),
                                               (25.8, 3.4), (27.0, 1.6), (27.5, 0.1)], 12)
    prism(m, "Band", 0, 0, 20.4, 21.4, 5.97, 5.95, 24)
    bulb_ring(m, "Bulb", 0, 0, 20.9, 6.08, 20, 0.24)
    prism(m, "Band", 0, 0, 11.6, 12.1, 1.15, 1.1, 12)
    for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        beam(m, "Rope", (dx * 0.72, dy * 0.72, 12.0), (dx * 0.95, dy * 0.95, 9.7), 0.09)
        beam(m, "Rope", (dx * 0.85, dy * 0.85, 7.7), (dx * 4.2, dy * 4.2, 0.6), 0.12)
    m.block("Burner", 0, 0, 10.7, 0.8, 0.8, 0.5)
    prism(m, "Flame", 0, 0, 10.95, 12.4, 0.45, 0.05, 6)
    m.loft_z("Basket", (7.6, 0, 0, 2.0, 2.0), (9.6, 0, 0, 2.4, 2.4))
    m.block("BasketRim", 0, 0, 9.65, 2.55, 2.55, 0.25)
    for dx, dy in ((0, 1.25), (0, -1.25), (1.25, 0), (-1.25, 0)):
        ball(m, "Sandbag", dx, dy, 8.6, 0.35, 6, 3)
        beam(m, "Rope", (dx, dy, 9.6), (dx, dy, 8.9), 0.05)
    m.block("Deck", 0, 0, 0.2, 5.0, 5.0, 0.4)
    for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        for k, (ox, oy, s) in enumerate(((0, 0, 1.0), (0.45, 0.3, 0.8), (-0.35, 0.4, 0.7))):
            m.block("Weight", dx * 4.25 + ox * dx, dy * 4.25 + oy * dy, s * 0.4 + (0.55 if k == 2 else 0), s, s * 0.8, s * 0.8)
    return m


def helter_skelter(seed=13):
    """For the rims: a striped helter-skelter tower with a spiral slide winding down round it, bulbs along the
    slide's edge, a pointed roof and a waving pennant."""
    m = prop("HelterSkelter", Canvas=TEAL, CanvasLight=CREAM, Trim=GOLD, Deck=PLUM, Slide=CRIMSON, SlideRim=GOLD, Post=WOOD,
             Mat=CRIMSON_DARK, Pole=IRON, Flag=CRIMSON, Bulb=BULB)
    lathe(m, ("Canvas", "CanvasLight"), 0, 0, [(0, 2.8), (17.0, 2.4)], 8)
    prism(m, "Deck", 0, 0, 17.0, 17.5, 3.5, 3.5, 12)
    for k in range(10):
        a = k * math.tau / 10
        m.block("Trim", math.cos(a) * 3.3, math.sin(a) * 3.3, 18.0, 0.15, 0.15, 1.0)
    flat_ring(m, "Trim", 0, 0, 18.5, 3.3, 0.15, 0.15, 12)
    lathe(m, ("Canvas", "CanvasLight"), 0, 0, [(17.5, 2.0), (19.8, 2.0)], 8)
    lathe(m, ("Canvas", "CanvasLight"), 0, 0, [(19.8, 3.4), (23.5, 0.1)], 8)
    scallops(m, "Trim", 0, 0, 19.8, 3.4, 8, 0.6)
    beam(m, "Pole", (0, 0, 23.4), (0, 0, 25.6), 0.14)
    plate(m, "Flag", (0.08, 0, 25.3), (2.0, 0, 24.9), (0, 0, 1), 0.9, 0.08, 0.06)
    # The slide: 2.25 turns down from the gallery, its outer rail lined with bulbs, wooden posts under it.
    steps, rmid = 36, 4.6
    start = math.pi / 2

    def at(t, r, lift=0.0):
        a = start + t * 2.25 * math.tau
        return (math.cos(a) * r, math.sin(a) * r, 17.0 - 15.8 * t + lift)

    for i in range(steps):
        t0, t1 = i / steps, (i + 1) / steps
        tm = (t0 + t1) / 2
        a = start + tm * 2.25 * math.tau
        radial = (math.cos(a), math.sin(a), 0)
        plate(m, "Slide", at(t0, rmid), at(t1, rmid), radial, 3.2, 3.2, 0.35)
        beam(m, "SlideRim", at(t0, 6.15, 0.4), at(t1, 6.15, 0.4), 0.28)
        beam(m, "SlideRim", at(t0, 3.05, 0.3), at(t1, 3.05, 0.3), 0.2)
        if i % 2 == 0:
            bulb(m, "Bulb", *at(t0, 6.15, 0.75), 0.2)
        if i % 4 == 2 and i < 16:  # one post per spot, up to the top turn (lower turns pass over the same spots)
            p = at(tm, 5.6, -0.2)
            m.block("Post", p[0], p[1], p[2] / 2, 0.3, 0.3, p[2])
    end = at(1.0, rmid)
    a = start + 2.25 * math.tau
    ahead = (-math.sin(a), math.cos(a), 0)
    plate(m, "Slide", end, (end[0] + ahead[0] * 3, end[1] + ahead[1] * 3, 0.5), (math.cos(a), math.sin(a), 0), 3.2, 3.2, 0.35)
    m.block("Mat", end[0] + ahead[0] * 4.5, end[1] + ahead[1] * 4.5, 0.1, 3.4, 3.4, 0.2)
    return m


def ferris_wheel(seed=14):
    """A landmark for the rims: a great Ferris wheel slowly turning, round cabins with glowing portholes, bulbs
    all along its rims and spokes, a gold hub with a glowing star. Turns round its axle, 17 studs straight above
    the prop's origin; its front (the side with the star) turns to the corridor."""
    m = prop("FerrisWheel", Frame="#3a3048", Plinth=PLUM_DARK, Deck=WOOD, Trim=GOLD, Wheel=TEAL, Spokes=CREAM, Hub=GOLD,
             LampStar="#ffe08a", CabinA=CRIMSON, CabinB=TEAL_DARK, CabinTrim=GOLD, Window="#ffd58a", Bulb=BULB, Booth=CRIMSON,
             Canvas=CRIMSON, CanvasLight=CREAM, Lamp=LAMP, Front="#ff00ff")
    H, R = 17.0, 13.0
    for y in (-0.9, 0.9):
        hoop(m, "Wheel", 0, y, H, R, 0.55, "xz", 40)
        hoop(m, "Wheel", 0, y, H, R * 0.5, 0.4, "xz", 24)
        for k in range(16):
            a = k * math.tau / 16
            beam(m, "Spokes", (math.cos(a) * 1.2, y, H + math.sin(a) * 1.2), (math.cos(a) * R, y, H + math.sin(a) * R), 0.26)
    for k in range(16):
        a = k * math.tau / 16
        beam(m, "Wheel", (math.cos(a) * R, -0.9, H + math.sin(a) * R), (math.cos(a) * R, 0.9, H + math.sin(a) * R), 0.3)
    disc(m, "Hub", 0, 0, H, 1.7, 2.6, 16, "xz")
    star_prism(m, "LampStar", (0, 1.4, H), 1.5, 0.65, 0.3)
    for y in (-1.25, 1.25):  # bulbs on both rims, and on the front spokes
        for k in range(36):
            a = (k + 0.5) * math.tau / 36
            bulb(m, "Bulb", math.cos(a) * R, y, H + math.sin(a) * R, 0.24)
    for k in range(16):
        a = k * math.tau / 16
        for t in (0.35, 0.6, 0.85):
            bulb(m, "Bulb", math.cos(a) * R * t, 1.15, H + math.sin(a) * R * t, 0.2)
    for k in range(10):  # round cabins: they look the same whichever way up the wheel turns them
        a = k * math.tau / 10 + math.tau / 20
        cx, cz = math.cos(a) * R, H + math.sin(a) * R
        ball(m, "CabinA" if k % 2 else "CabinB", cx, 0, cz, 1.55, 10, 6)
        for y in (-1.38, 1.38):
            disc(m, "Window", cx, y, cz, 0.72, 0.2, 10, "xz")
            hoop(m, "CabinTrim", cx, y * 1.05, cz, 0.82, 0.16, "xz", 10)
    # The A-frames each side, the axle, the base and the boarding platform.
    for y in (-2.5, 2.5):
        for side in (-1, 1):
            beam(m, "Frame", (side * 8.5, y, 0.4), (0, y, H), 0.9)
        beam(m, "Frame", (-5.6, y, 6.0), (5.6, y, 6.0), 0.6)
        beam(m, "Frame", (-3.0, y, 11.4), (3.0, y, 11.4), 0.5)
        beam(m, "Frame", (-5.6, y, 6.0), (3.0, y, 11.4), 0.35)
        beam(m, "Frame", (5.6, y, 6.0), (-3.0, y, 11.4), 0.35)
    beam(m, "Frame", (0, -2.9, H), (0, 2.9, H), 0.8)
    for y in (-2.9, 2.9):
        disc(m, "Trim", 0, y, H, 0.7, 0.2, 10, "xz")
    m.block("Plinth", 0, 0, 0.2, 21, 7.5, 0.4)
    m.block("Deck", 0, 2.6, 1.0, 6.0, 3.0, 1.6)
    for k in range(3):
        m.block("Deck", 0, 4.5 + k * 0.6, 0.27 * (3 - k), 4.0, 0.6, 0.54 * (3 - k))
    for x in (-2.9, 2.9):
        m.block("Trim", x, 2.6, 2.2, 0.12, 3.0, 0.12)
    # A ticket booth by the platform.
    m.block("Booth", 6.6, 3.0, 1.9, 2.2, 2.2, 3.0)
    m.block("Lamp", 6.6, 4.13, 2.2, 1.4, 0.1, 1.0)
    lathe(m, ("Canvas", "CanvasLight"), 6.6, 3.0, [(3.4, 1.9), (5.2, 0.1)], 8, math.pi / 8)
    bulb(m, "Bulb", 6.6, 3.0, 5.4, 0.3)
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


def big_top(seed=15):
    """A landmark for the rims: the big top. A huge crimson-and-cream tent with a gold valance and bulbs round the
    eaves and up its seams, a lit entrance under a marquee with a pink neon star, bunting out to flagpoles, a
    waving pennant on its king pole, and two searchlights from its peak sweeping round the sky."""
    m = prop("BigTop", Canvas=CRIMSON, CanvasLight=CREAM, Trim=GOLD, Pole=IRON, Flag=TEAL, FlagB=GOLD, Bulb=BULB, Doorway=SHADOW,
             Lamp=LAMP, Curtain=CRIMSON_DARK, Sign=CRIMSON_DARK, Neon=NEON, Searchbeam="#cdb8ff", Rope=ROPE, Pennant=TEAL,
             PennantB=CREAM, Front="#ff00ff")
    n = 24
    turn = math.pi / 2 - math.pi / n
    roof = [(7.0, 15.0), (10.0, 11.5), (14.0, 7.6), (18.5, 3.6), (21.5, 1.0), (22.2, 0.1)]
    lathe(m, ("CanvasLight", "Canvas"), 0, 0, [(0, 14.0), (7.0, 13.6)], n, turn)
    lathe(m, ("CanvasLight", "Canvas"), 0, 0, roof, n, turn)
    scallops(m, "Trim", 0, 0, 7.0, 15.0, n, 1.4, turn)
    bulb_ring(m, "Bulb", 0, 0, 6.9, 15.1, 48, 0.3, turn)
    for k in range(0, n, 4):  # strings of bulbs up the roof's seams
        a = turn + k * math.tau / n
        for (z0, r0), (z1, r1) in zip(roof[:-2], roof[1:-1]):
            for t in (0.0, 0.33, 0.66):
                z, r = z0 + (z1 - z0) * t, r0 + (r1 - r0) * t
                bulb(m, "Bulb", math.cos(a) * (r + 0.25), math.sin(a) * (r + 0.25), z + 0.2, 0.26)
    ball(m, "Trim", 0, 0, 22.2, 0.8, 8, 4)
    beam(m, "Pole", (0, 0, 22.0), (0, 0, 27.4), 0.35)
    ball(m, "Trim", 0, 0, 27.5, 0.4, 6, 3)
    plate(m, "Flag", (0.15, 0, 27.0), (4.2, 0, 26.3), (0, 0, 1), 2.0, 0.15, 0.1)
    # The entrance porch, its doorway lit, a marquee over it.
    for side in (-1, 1):
        m.block("Canvas", side * 3.5, 15.1, 3.6, 1.2, 3.6, 7.2)
        m.block("Trim", side * 3.5, 15.1, 7.25, 1.3, 3.7, 0.3)
    m.block("CanvasLight", 0, 15.1, 7.9, 8.4, 4.0, 1.2)
    for x in (-3.0, -1.5, 0.0, 1.5, 3.0):
        plate(m, "Trim", (x, 17.12, 7.3), (x, 17.12, 6.6), (1, 0, 0), 1.4, 0.08, 0.1)
    m.block("Doorway", 0, 16.5, 3.4, 5.8, 0.5, 6.8)
    m.block("Lamp", 0, 16.78, 3.1, 4.2, 0.1, 5.8)
    for side in (-1, 1):
        plate(m, "Curtain", (side * 1.7, 16.9, 6.6), (side * 2.4, 16.9, 0.3), (1, 0, 0), 1.6, 0.6, 0.15)
        m.block("Trim", side * 2.4, 17.0, 3.0, 0.7, 0.15, 0.3)
    m.block("Sign", 0, 16.6, 10.4, 9.0, 0.5, 3.2)
    for dz in (-1.65, 1.65):
        m.block("Trim", 0, 16.6, 10.4 + dz, 9.3, 0.6, 0.25)
    for dx in (-4.6, 4.6):
        m.block("Trim", dx, 16.6, 10.4, 0.25, 0.6, 3.5)
    star_prism(m, "Neon", (0, 16.95, 10.4), 1.25, 0.52, 0.2)
    for k in range(12):
        x = -4.1 + k * (8.2 / 11)
        bulb(m, "Bulb", x, 16.95, 11.75, 0.2)
        bulb(m, "Bulb", x, 16.95, 9.05, 0.2)
    for x in (-3.4, -2.2, 2.2, 3.4):
        star_prism(m, "Trim", (x, 16.9, 10.4), 0.45, 0.2, 0.1)
    # Bunting from the king pole out to four flagpoles.
    for a in (math.radians(45), math.radians(135), math.radians(225), math.radians(315)):
        c, s = math.cos(a), math.sin(a)
        fx, fy = c * 19.5, s * 19.5
        beam(m, "Pole", (fx, fy, 0), (fx, fy, 12.5), 0.3)
        plate(m, "FlagB", (fx, fy, 12.2), (fx + c * 2.2, fy + s * 2.2, 11.8), (0, 0, 1), 1.1, 0.1, 0.08)
        pennants(m, "Rope", ("Pennant", "PennantB"), (c * 0.3, s * 0.3, 26.0), (fx, fy, 12.4), 2.0, 9, 0.9)
    # The searchlights, sweeping round the sky from the peak.
    for side in (-1, 1):
        a = math.radians(30)
        tip = (side * math.sin(a) * 36, 0, 22.8 + math.cos(a) * 36)
        beam(m, "Searchbeam", (0, 0, 22.8), tip, 0.45, 0.45, 1.8)
    m.block("Front", 0, 20, 1, 0.2, 0.2, 0.2)
    return m


def fun_house(seed=16):
    """A landmark for the rims: a fun house behind the face of a giant clown. Its eyes are hypnotic spirals,
    turning; its glowing red nose pulses; you walk in through its grin, up its tongue, under its teeth. Purple
    curls, a tall striped hat with a gold pompom, and bulbs all the way round its face."""
    m = prop("FunHouse", Wall=TEAL_DARK, WallStripe=PLUM, Trim=GOLD, ClownFace="#f6f1ea", Hair=HAIR, HatA=CRIMSON, HatB=CREAM,
             Pompom=GOLD, EyeWhite="#ffffff", SpiralL="#17141f", SpiralR="#17141f", Brow=SHADOW, Neon="#ff3355", Cheek="#f08aa0",
             Doorway=SHADOW, Lamp="#ff8ad8", Lips=CRIMSON, Teeth="#fffaf0", Tongue="#f0627f", Base=PLUM_DARK, Bulb=BULB,
             Front="#ff00ff")
    # The house behind the face.
    m.block("Wall", 0, -3.5, 5.95, 20, 13, 11.9)
    for x in range(-9, 10, 3):
        m.block("WallStripe", x, -3.5, 5.96, 1.3, 13.1, 11.92)
    m.block("Trim", 0, -3.5, 12.2, 20.6, 13.6, 0.5)
    m.block("Base", 0, 4.6, 0.9, 17, 4.6, 1.8)
    # The face, a round board standing in front of the house.
    hz = 12.6
    disc(m, "ClownFace", 0, 3.6, hz, 10.4, 1.6, 32, "xz")
    bulb_ring_xz = 34
    for k in range(bulb_ring_xz):
        a = k * math.tau / bulb_ring_xz
        bulb(m, "Bulb", math.cos(a) * 10.7, 4.0, hz + math.sin(a) * 10.7, 0.32)
    front = 4.4
    for side, role in ((-1, "SpiralL"), (1, "SpiralR")):
        ex, ez = side * 4.2, hz + 2.6
        disc(m, "EyeWhite", ex, front + 0.15, ez, 2.9, 0.3, 24, "xz")
        spiral_eye(m, role, ex, front + 0.4, ez, 2.6)
        b0, b1, b2 = (side * 1.5, ez + 3.4), (side * 4.2, ez + 4.6), (side * 6.8, ez + 3.6)  # high arched brows
        beam(m, "Brow", (b0[0], front + 0.3, b0[1]), (b1[0], front + 0.3, b1[1]), 0.8)
        beam(m, "Brow", (b1[0], front + 0.3, b1[1]), (b2[0], front + 0.3, b2[1]), 0.8, 0.8, 0.5)
        disc(m, "Cheek", side * 6.6, front + 0.12, hz - 2.6, 1.4, 0.2, 14, "xz")
    ball(m, "Neon", 0, front + 1.3, hz - 1.2, 2.0, 12, 7)
    # The grin: a dark mouth from cheek to cheek, lit inside, red lips, teeth along the top, a tongue for a ramp.
    half = 6.6

    def top(x):
        return 6.9 + 1.4 * (x / half) ** 2

    def bottom(x):
        return 2.2 + 4.3 * (x / half) ** 2

    slabs = 14
    for i in range(slabs):
        x = -half + (i + 0.5) * 2 * half / slabs
        lo, hi = bottom(x), top(x)
        if hi - lo > 0.2:
            m.block("Doorway", x, front + 0.05, (lo + hi) / 2, 2 * half / slabs, 0.3, hi - lo)
    m.block("Lamp", 0, front + 0.2, 4.3, 3.4, 0.1, 3.6)
    for curve, z_off in ((top, 0.3), (bottom, -0.3)):
        for i in range(slabs):
            x0 = -half - 0.3 + i * (2 * half + 0.6) / slabs
            x1 = x0 + (2 * half + 0.6) / slabs
            beam(m, "Lips", (x0, front + 0.3, curve(max(min(x0, half), -half)) + z_off), (x1, front + 0.3, curve(max(min(x1, half), -half)) + z_off), 0.75)
    for i in range(9):
        x = -4.4 + i * 1.1
        m.block("Teeth", x, front + 0.32, top(x) - 0.55, 0.85, 0.3, 0.85)
    plate(m, "Tongue", (0, front + 0.2, 2.5), (0, front + 4.4, 0.2), (1, 0, 0), 3.6, 4.4, 0.4)
    # Purple curls, and a tall striped hat with a gold pompom.
    for side in (-1, 1):
        for x, y, z, r in ((10.6, 2.6, 15.0, 2.6), (10.0, 2.2, 19.2, 2.2), (11.4, 2.0, 11.0, 2.0), (8.0, 2.0, 22.0, 2.0),
                           (12.2, 1.4, 17.4, 1.8)):
            ball(m, "Hair", side * x, y, z, r, 10, 6)
    lathe(m, ("HatA", "HatB"), 0, 2.4, [(21.6, 4.0), (31.0, 0.1)], 12, 0.0, (2.2, 0))
    prism(m, "Trim", 0, 2.4, 21.4, 22.2, 4.15, 4.0, 12)
    ball(m, "Pompom", 2.2, 2.4, 31.3, 1.0, 8, 5)
    m.block("Front", 0, 9, 1, 0.2, 0.2, 0.2)
    return m


def stage_moon(seed=17):
    """In the sky beyond the rims: a crescent moon asleep, hung from a rope like a stage prop, stars dangling on
    strings beside it, all swaying gently round the rope's hook far above. Starts high above the ground (its
    middle 42 up at size 1) and faces down the corridor."""
    m = prop("StageMoon", Crescent="#ffe9a8", MoonFace="#6a4a2a", Blush="#f2a0a0", Rope=ROPE, LampStar="#ffd86b", Front="#ff00ff")
    zc, R = 42.0, 10.0
    a0, a1 = math.radians(40), math.radians(320)
    steps = 28

    def edge(i):
        a = a0 + (a1 - a0) * i / steps
        k = math.sin(math.pi * i / steps)
        t = max(6.4 * k, 0.35)
        d = 1.0 + 2.4 * k
        out = (math.cos(a) * R, zc + math.sin(a) * R)
        inner = (math.cos(a) * (R - t), zc + math.sin(a) * (R - t))
        return out, inner, d

    for i in range(steps):
        (o0, n0, d0), (o1, n1, d1) = edge(i), edge(i + 1)
        verts = []
        for (x, z), d in ((o0, d0), (n0, d0), (n1, d1), (o1, d1)):
            verts.append((x, -d / 2, z))
        for (x, z), d in ((o0, d0), (n0, d0), (n1, d1), (o1, d1)):
            verts.append((x, d / 2, z))
        m._add("Crescent", verts, [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]])
    # The sleeping face, looking right into its own curve.
    fy = 1.75
    m.loft_x("Crescent", (-3.7, 0, zc - 0.3, 2.2, 2.4), (-1.6, 0, zc - 1.0, 0.7, 0.6))  # nose
    for i in range(6):  # a closed eye, lashes down
        t0, t1 = i / 6, (i + 1) / 6
        x0, x1 = -6.4 + 2.4 * t0, -6.4 + 2.4 * t1
        z0 = zc + 2.4 - 0.55 * math.sin(math.pi * t0)
        z1 = zc + 2.4 - 0.55 * math.sin(math.pi * t1)
        beam(m, "MoonFace", (x0, fy, z0), (x1, fy, z1), 0.2, 0.55)
    for t in (0.25, 0.5, 0.75):
        x = -6.4 + 2.4 * t
        z = zc + 2.4 - 0.55 * math.sin(math.pi * t)
        beam(m, "MoonFace", (x, fy, z - 0.2), (x - 0.2, fy, z - 0.85), 0.2, 0.22)
    for i in range(5):  # a small content smile
        t0, t1 = i / 5, (i + 1) / 5
        x0, x1 = -5.7 + 1.8 * t0, -5.7 + 1.8 * t1
        beam(m, "MoonFace", (x0, fy, zc - 3.0 - 0.5 * math.sin(math.pi * t0)), (x1, fy, zc - 3.0 - 0.5 * math.sin(math.pi * t1)), 0.2, 0.45)
    disc(m, "Blush", -6.0, fy - 0.05, zc - 1.4, 0.85, 0.12, 12, "xz")
    # The hook, the rope up into the sky, a bar with stars hanging off it.
    hoop(m, "Rope", 0, 0, zc + R + 0.75, 0.75, 0.22, "xz", 12)
    beam(m, "Rope", (0, 0, zc + R + 1.5), (0, 0, 110.0), 0.28)
    bar = zc + 19.0
    beam(m, "Rope", (-12.5, 0, bar), (11.5, 0, bar), 0.35)
    for x, z, s, y in ((-12.0, zc + 8.0, 1.7, 0), (-11.0, zc - 3.5, 1.2, 0), (3.6, zc + 0.8, 1.4, 1.9), (11.0, zc - 1.0, 1.6, 0)):
        beam(m, "Rope", (x, y, bar), (x, y, z + s), 0.08)
        star_prism(m, "LampStar", (x, y, z), s, s * 0.45, 0.5)
    m.block("Front", 0, 6, zc, 0.2, 0.2, 0.2)
    return m


def popcorn_fall(seed=18):
    """A giant popcorn box tipped over the top of the corridor wall, bulbs round its mouth, pouring popcorn down
    the wall into a heap on the floor, kernels tumbling for ever. Origin on the wall's top inner edge: rim z 0,
    floor z -44, +Y out into the corridor. The Front part tells the game which way it faces, then it goes."""
    m = prop("PopcornFall", Canvas=CRIMSON, CanvasLight=CREAM, Trim=GOLD, Bulb=BULB, Popcorn=POPCORN, Butter=BUTTER, Kernels=POPCORN,
             Front="#ff00ff")
    rng = random.Random(seed)
    # The box lies on the rim, its mouth over the edge, cut into crimson and cream stripes along its length.
    y0, y1 = -11.0, 1.6
    w0, h0, w1, h1 = 7.0, 6.0, 9.6, 8.2
    strips = 6
    for i in range(strips):
        role = "Canvas" if i % 2 == 0 else "CanvasLight"
        xa = -w0 / 2 + (i + 0.5) * w0 / strips
        xb = -w1 / 2 + (i + 0.5) * w1 / strips
        m.loft_y(role, (y0, xa, h0 / 2, w0 / strips, h0), (y1, xb, h1 / 2 + 0.2, w1 / strips, h1))
    m.loft_y("Trim", (y0 - 0.3, 0, h0 / 2, w0 + 0.2, h0 + 0.2), (y0 + 0.4, 0, h0 / 2, w0 + 0.25, h0 + 0.25))
    for (xa, za), (xb, zb) in (((-w1 / 2, 0.3), (w1 / 2, 0.3)), ((w1 / 2, 0.3), (w1 / 2, h1 + 0.2)),
                               ((w1 / 2, h1 + 0.2), (-w1 / 2, h1 + 0.2)), ((-w1 / 2, h1 + 0.2), (-w1 / 2, 0.3))):
        beam(m, "Trim", (xa, y1 + 0.1, za), (xb, y1 + 0.1, zb), 0.5)
    for k in range(9):
        t = k / 8
        bulb(m, "Bulb", -w1 / 2 + w1 * t, y1 + 0.45, h1 + 0.45, 0.3)
        if 0 < k < 8:
            bulb(m, "Bulb", -w1 / 2 - 0.1, y1 + 0.45, 0.3 + (h1 - 0.1) * t, 0.3)
            bulb(m, "Bulb", w1 / 2 + 0.1, y1 + 0.45, 0.3 + (h1 - 0.1) * t, 0.3)
    star_prism(m, "Trim", (0, -4.6, h0 / 2 + 3.65), 1.8, 0.8, 0.3, (math.pi / 2 - 0.1, 0, 0))
    # Popcorn heaped in the mouth and spilling over the edge.
    for _ in range(26):
        popcorn(m, rng, rng.uniform(-4.2, 4.2), rng.uniform(1.4, 3.6), rng.uniform(0.4, 4.0), rng.uniform(0.6, 0.95))
    # The cascade down the wall, widening as it falls.
    z = -0.5
    while z > -42:
        t = -z / 44
        width = 7.0 + 4.0 * t
        for _ in range(6):
            popcorn(m, rng, rng.uniform(-width / 2, width / 2), rng.uniform(2.4, 5.2) + t * 1.5, z + rng.uniform(-0.6, 0.6),
                    rng.uniform(0.8, 1.15))
        z -= 1.4
    # The heap on the corridor floor.
    for _ in range(60):
        a = rng.uniform(0, math.pi)
        rr = rng.uniform(0, 1) ** 0.6
        x = math.cos(a) * rr * 9.0
        y = 3.0 + math.sin(a) * rr * 10.0
        top = (1 - rr) * 6.5
        popcorn(m, rng, x, y, -44 + rng.uniform(0.3, max(top, 0.4)), rng.uniform(0.8, 1.2))
    # Kernels tumbling down in front: rows four studs apart, so dropping four and starting over loops seamlessly.
    for k, zz in enumerate(range(-3, -44, -4)):
        for x in (-2.8, -0.9, 1.0, 2.9):
            jitter = ((k * 7 + int(x * 10)) % 5 - 2) * 0.25
            m.block("Kernels", x + jitter, 5.6 + (k % 2) * 0.6, zz - (1.4 if x > 0 else 0), 0.55, 0.5, 0.55)
    m.block("Front", 0, 6, -20, 0.2, 0.2, 0.2)
    return m


def coaster_loop(seed=19):
    """A roller-coaster crossing over the corridor from rim to rim on two white trestle towers, with a loop in
    the middle and two cars of ghost riders going round and round it, arms up. Bulbs along the rails, bunting
    under the track. Modelled for the 72-wide corridor (feet beyond 36 from the middle); MapDecor stretches it to
    the real width. All of it stays above the rim (z 0), clear of the flight camera."""
    m = prop("CoasterLoop", Trestle="#d9cdb8", TrestleDark="#a89a82", Rail=CRIMSON, Ties=WOOD_DARK, Bulb=BULB, Rope=ROPE,
             Pennant=TEAL, PennantB=GOLD, Cart=CRIMSON, CartTrim=GOLD, Ghost=GHOST, GhostEye=SHADOW, Front="#ff00ff")
    track = 14.4
    for side in (-1, 1):  # the trestle towers
        cx = side * 40
        for dx in (-2.5, 2.5):
            for dy in (-2.5, 2.5):
                m.block("Trestle", cx + dx, dy, track / 2 - 0.2, 0.6, 0.6, track - 0.4)
        for k, z in enumerate((3.5, 7.0, 10.5, 13.4)):  # braces end inside the legs, never flush with them
            for dy in (-2.5, 2.5):
                m.block("TrestleDark", cx, dy, z, 5.4, 0.4, 0.4)
            for dx in (-2.5, 2.5):
                m.block("TrestleDark", cx + dx, 0, z + 0.05, 0.36, 5.2, 0.36)
        for z0, z1 in ((0.2, 3.5), (3.5, 7.0), (7.0, 10.5), (10.5, 13.4)):
            for dy in (-2.55, 2.55):
                beam(m, "TrestleDark", (cx - 2.5, dy, z0), (cx + 2.5, dy, z1), 0.25)
            for dx in (-2.55, 2.55):
                beam(m, "TrestleDark", (cx + dx, -2.5, z1), (cx + dx, 2.5, z0), 0.25)
    # The straight track across.
    for y in (-0.9, 0.9):
        beam(m, "Rail", (-44, y, track), (44, y, track), 0.4)
    x = -43.5
    while x <= 43.5:
        m.block("Ties", x, 0, track - 0.35, 0.45, 2.6, 0.3)
        x += 1.6
    beam(m, "TrestleDark", (-44, 0, track - 1.05), (44, 0, track - 1.05), 0.5)
    # The loop, sitting on the track at x 0, its middle 23.4 up.
    R = 9.0
    C = track + R
    for y in (-0.9, 0.9):  # the loop's rails, all but the bottom, where the straight rails already run
        for k in range(36):
            a0, a1 = math.tau / 72 + k * math.tau / 36, math.tau / 72 + (k + 1) * math.tau / 36
            if math.sin((a0 + a1) / 2) < -0.97:
                continue
            beam(m, "Rail", (math.cos(a0) * R, y, C + math.sin(a0) * R), (math.cos(a1) * R, y, C + math.sin(a1) * R), 0.4)
    for k in range(36):
        a = (k + 0.5) * math.tau / 36
        if math.sin(a) < -0.95:
            continue
        p = (math.cos(a) * (R + 0.4), 0, C + math.sin(a) * (R + 0.4))
        obox(m, "Ties", p, ((-math.sin(a), 0, math.cos(a)), (0, 1, 0), (math.cos(a), 0, math.sin(a))), (0.45, 2.6, 0.3))
    for side in (-1, 1):
        beam(m, "TrestleDark", (side * (R + 0.6), 0, C), (side * (R + 0.6), 0, track - 0.6), 0.5)
        beam(m, "TrestleDark", (side * (R + 0.6), 0, C), (side * (R * 0.7 + 0.6), 0, C + R * 0.7), 0.4)
    for k in range(28):  # bulbs along the outside of the loop and the front of the track
        a = k * math.tau / 28
        bulb(m, "Bulb", math.cos(a) * (R + 0.75), 1.2, C + math.sin(a) * (R + 0.75), 0.24)
    for x in range(-42, 43, 3):
        if abs(x) > 1:
            bulb(m, "Bulb", x, 1.25, track + 0.35, 0.24)
    for a, b in (((-36, 1.35, track - 0.6), (-13, 1.35, track - 0.6)), ((13, 1.35, track - 0.6), (36, 1.35, track - 0.6))):
        pennants(m, "Rope", ("Pennant", "PennantB"), a, b, 1.2, 12, 1.0)
    # Two cars going round the inside of the loop, ghost riders aboard.
    for a in (-math.pi / 2, math.pi / 2):
        out = Vector((math.cos(a), 0, math.sin(a)))
        ahead = Vector((-math.sin(a), 0, math.cos(a)))
        f = Frame(Vector((0, 0, C)) + out * (R - 0.85), ahead, Vector((0, 1, 0)), -out)
        f.box(m, "Cart", 0, 0, 0, (3.6, 2.0, 1.1))
        f.box(m, "CartTrim", 0, 0, 0.6, (3.7, 2.1, 0.2))
        f.box(m, "CartTrim", 1.85, 0, 0.1, (0.3, 2.1, 1.0))
        for lx in (-0.85, 0.85):
            f.box(m, "Ghost", lx, 0, 1.25, (0.8, 0.8, 1.2))
            ball(m, "Ghost", *f.p(lx, 0, 2.1), 0.45, 8, 4)
            for side in (-1, 1):
                beam(m, "Ghost", f.p(lx, side * 0.35, 1.5), f.p(lx - 0.2, side * 0.6, 2.6), 0.22, 0.22, 0.12)
                f.box(m, "GhostEye", lx + 0.38, side * 0.16, 2.15, (0.06, 0.12, 0.2))
    m.block("Front", 0, 6, 34, 0.2, 0.2, 0.2)
    return m


ALL = [striped_tent, jack_box, popcorn_cart, fortune_booth, high_striker, balloon_cart, carousel, crate_stack, bulb_post, circus_ring,
       swing_ride, hot_air_balloon, helter_skelter, ferris_wheel, big_top, fun_house, stage_moon, popcorn_fall, coaster_loop]

# Where the props go: the same rules as Config/Decor's MidnightCarnival (keep the two in step). The map is 1400 long.
DECOR = dict(
    floor=dict(first=12, gap=(12, 22), side=(24, 34),
               props=[("prop_StripedTent", 14, (1.2, 1.6)), ("prop_JackBox", 10, (1.2, 1.5)), ("prop_PopcornCart", 9, (1.2, 1.5)),
                      ("prop_BalloonCart", 9, (1.3, 1.6)), ("prop_FortuneBooth", 8, (1.2, 1.4)), ("prop_HighStriker", 8, (1.2, 1.4)),
                      ("prop_BulbPost", 8, (1.2, 1.5)), ("prop_Carousel", 4, (1.0, 1.2))],
               extras=dict(chance=0.7, spread=8, props=[("prop_CrateStack", 5, (0.8, 1.1)), ("prop_BulbPost", 2, (0.8, 1.0)),
                                                         ("prop_BalloonCart", 2, (0.8, 1.0))])),
    rim=dict(first=6, gap=(14, 24), chance=0.9, side=(64, 102),
             props=[("prop_StripedTent", 6, (2.0, 2.6)), ("prop_SwingRide", 3, (1.6, 2.0)), ("prop_HotAirBalloon", 3, (1.6, 2.0)),
                    ("prop_HelterSkelter", 2, (1.6, 2.0)), ("prop_CrateStack", 2, (2.0, 2.6)), ("prop_JackBox", 2, (2.0, 2.4)),
                    ("prop_BulbPost", 2, (1.8, 2.2))]),
    overhead=[("prop_CoasterLoop", 240, 0, 1), ("prop_CoasterLoop", 720, 0, 1.05), ("prop_CoasterLoop", 1180, 0, 1)],
    walls=[("prop_PopcornFall", 80, 1), ("prop_PopcornFall", 250, -1), ("prop_PopcornFall", 440, 1), ("prop_PopcornFall", 620, -1),
           ("prop_PopcornFall", 800, 1), ("prop_PopcornFall", 980, -1), ("prop_PopcornFall", 1160, 1), ("prop_PopcornFall", 1340, -1)],
    spots=[("prop_BigTop", 90, -88, "rim", 0, 1.5, "middle"), ("prop_BigTop", 560, 88, "rim", 0, 1.6, "middle"),
           ("prop_BigTop", 1040, -88, "rim", 0, 1.5, "middle"),
           ("prop_FerrisWheel", 180, 84, "rim", 0, 1.5, "middle"), ("prop_FerrisWheel", 700, -84, "rim", 0, 1.6, "middle"),
           ("prop_FerrisWheel", 1220, 84, "rim", 0, 1.5, "middle"),
           ("prop_FunHouse", 380, -84, "rim", 0, 1.4, "middle"), ("prop_FunHouse", 860, 84, "rim", 0, 1.5, "middle"),
           ("prop_FunHouse", 1300, -84, "rim", 0, 1.4, "middle"),
           ("prop_StageMoon", 320, 180, "rim", 0, 2.4, "along"), ("prop_StageMoon", 1000, -170, "rim", 0, 2.6, "along")]
          + [("prop_CircusRing", d, x, "floor", yaw, 1.2) for d, x, yaw in ((40, -3, 20), (150, 4, 140), (270, -4, 70), (380, 3, 200),
                                                                             (500, -2, 300), (610, 4, 40), (740, -3, 110), (850, 2, 250),
                                                                             (960, -4, 330), (1090, 3, 80), (1210, -2, 160), (1330, 4, 10))],
)


# ---------------------------------------------------------------------- light


def carnival_light(scene):
    """Midnight for the renders: cool moonlight from high up and a deep violet fill, close to the game's
    Config/Lighting look for this world, so the bulbs and the ghosts glow."""
    sun = bpy.data.objects["Sun"]
    sun.data.energy = 1.5
    sun.data.color = (0.78, 0.78, 1.0)
    sun.rotation_euler = (math.radians(-62), math.radians(24), math.radians(30))
    ambient = scene.world.node_tree.nodes["Background"]
    ambient.inputs["Color"].default_value = (0.62, 0.52, 0.85, 1)
    ambient.inputs["Strength"].default_value = 0.65


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
    big = {"prop_FerrisWheel": (-80, -120, 0), "prop_BigTop": (-25, -125, 0), "prop_FunHouse": (30, -118, 0),
           "prop_SwingRide": (75, -115, 0), "prop_HelterSkelter": (105, -115, 0), "prop_HotAirBalloon": (130, -115, 0),
           "prop_StageMoon": (40, -230, 0), "prop_PopcornFall": (190, -110, 44), "prop_CoasterLoop": (270, -170, 0)}
    x = 40
    for model in models:
        root = model.build(props)
        if model.name in big:
            root.location = big[model.name]
        else:
            root.location = (x, -40, 0)
            x += 16
        built[model.name] = root
        roots.append(root)
    mk.light_up(roots, GLOW_ROLES)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-400, -500, -0.01), (500, -500, -0.01), (500, 200, -0.01), (-400, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", CORRIDOR["FloorA"], False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = mk.player_block(stage)
    stars = mk.star_dome(stage, count=220, colours=("#ffffff", "#ffe6f4"))
    bpy.context.view_layer.update()
    mk.set_sky(scene, SKY)
    carnival_light(scene)

    everything = roots + [player]
    if stills:
        for model, root in zip(models, roots):
            name = model.name
            if name == "prop_CoasterLoop":
                mk.shoot_prop(scene, name, root, player, everything, (-0.15, 1.0, 0.25), 0.95, (1400, 700), 32)
            elif name == "prop_PopcornFall":
                mk.shoot_prop(scene, name, root, player, everything, (0.6, 1.0, 0.1), 0.9, (700, 900), 40)
            elif name == "prop_StageMoon":
                mk.shoot_prop(scene, name, root, player, everything, (0.15, 1.0, 0.0), 1.1, (700, 900), 50)
            elif name in ("prop_FerrisWheel", "prop_BigTop", "prop_FunHouse"):
                mk.shoot_prop(scene, name, root, player, everything, (0.45, 0.95, 0.3), 1.15, (800, 700), 50)
            else:
                mk.shoot_prop(scene, name, root, player, everything)
        player.location = (30, -40, 0)
        bpy.context.view_layer.update()
        small = [r for r in roots if mk.prop_of(r) not in big]
        mk.set_visible(everything, small + [player])
        kit.shoot(scene, "props", (120, 34, 26), (120, -40, 5), (1800, 700), 18)
        landmarks = [built[n] for n in ("prop_FerrisWheel", "prop_BigTop", "prop_FunHouse", "prop_SwingRide", "prop_HelterSkelter",
                                        "prop_HotAirBalloon")]
        mk.set_visible(everything, landmarks + [player])
        player.location = (0, -95, 0)
        bpy.context.view_layer.update()
        kit.shoot(scene, "landmarks", (25, 40, 46), (25, -118, 16), (1800, 800), 20)

    if videos:  # close up on what moves
        names = ("prop_JackBox", "prop_PopcornCart", "prop_FortuneBooth", "prop_HighStriker", "prop_BalloonCart", "prop_BulbPost",
                 "prop_Carousel", "prop_SwingRide", "prop_FerrisWheel", "prop_HotAirBalloon", "prop_StageMoon")
        movers = [built[n] for n in names]
        mk.set_visible(everything, movers)
        saved = [(r, r.location.copy()) for r in movers]
        for k, root in enumerate(movers[:6]):
            root.location = (k * 13 - 32, 0, 0)
        for k, root in enumerate(movers[6:10]):
            root.location = ((k - 1.5) * 36, -45, 0)
        movers[10].location = (0, -170, 0)
        bpy.context.view_layer.update()
        entries = mk.motion_entries(movers, MOTION)
        mk.render_video(scene, RENDERS, "carnival_motion", 120, 15,
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

        mk.render_video(scene, RENDERS, "carnival_flight", frames, 15, fly, (1600, 900))
        mk.reset_motion(entries)

    mk.clear([corridor, stars] + copies)
    mk.light_up(roots, GLOW_ROLES, 0)
    ground.hide_render = False
    for root in roots:
        for child in root.children:
            child.hide_render = False
    player.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "midnight_carnival_models.blend"))
    print("saved", HERE / "midnight_carnival_models.blend")
    for model in models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    # After "--": "stills" renders only the stills, "videos" only the videos; nothing, both.
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(stills=not args or "stills" in args, videos=not args or "videos" in args)
