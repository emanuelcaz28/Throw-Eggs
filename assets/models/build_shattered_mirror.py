"""Builds Shattered Mirror's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_shattered_mirror.py              (stills and videos)
    Blender -b -P build_shattered_mirror.py -- stills    (stills only, quicker while modelling)
    Blender -b -P build_shattered_mirror.py -- only prop_A prop_B   (just those stills, nothing saved)

Saves shattered_mirror_models.blend and renders to design/world/models_shattered_mirror/: one still per prop, the props
together, the landmarks, a stretch of corridor, and two videos of what moves (mirror_motion.mp4 close up,
mirror_flight.mp4 down the corridor at the flight camera's height).

Shattered Mirror, map 16, after The Weeping Dark: the world on the other side of the glass. Coming out of the
blackest map, the light comes back all at once, cold and bright: a pearl-pink dawn, silver floors, white quartz rims,
walls of smoked violet glass, and everything throwing rainbows. It looks beautiful for about a second. Then you
notice the reflections are wrong. A silhouette stands in every standing mirror with nobody in front of it, breathing,
two cold eyes in its face. Glass mannequins with mirrors for faces turn their heads after you. A statue has burst
apart and its pieces float, still holding the shape. In the giant hand mirror on the rim an eye looks round for you.

The signature is the Standing Mirror: a tall gilt mirror on claw feet, cracked from one blow, with a shape standing in
it that isn't yours. Around it: forests of mirror shards stuck in the ground with one hovering and turning above them,
glass prism obelisks spilling rainbows over the floor, glass mannequins with cracked mirror faces, kaleidoscope
flowers of mirror petals turning slowly, crashed chandeliers with their candles still lit, statues split into floating
pieces, and now and then a heap of empty frames with eyes in the biggest one; glass tufts and broken mirror bits as
filler, and cracked mirror pools lying flat across the middle, rings of rainbow in them. On the rims: glass trees with
mirror leaves, broken halls of mirrors where one panel revolves; landmarks: the Looking Glass, a hand mirror the size
of a tower stuck in the ground with an eye in it and shards orbiting it, and the Kaleidoscope Towers, a rose window
of rainbow glass turning on top. The Broken Moon hangs in the sky, its pieces circling it. Shards pour down the
corridor walls from cracks in the glass, and colossal gilt frames stand across the corridor so the flight goes
through one empty mirror after another.

The Last Door from The Weeping Dark stays the end of the corridor: it moved to the end of this map (GAME_SPEC
section 9: "if a map is ever added after this one, the door moves to the new end").

The owner asked for real chrome, "silver but with multiple colours", not something basic (2026-11-13): every silver,
glass and gold part is metal in the game. METAL below says which roles get which of two MaterialVariants,
"HoloChrome" (silver with rainbow flowing through it, almost mirror smooth) and "PolishedGold", made in MaterialService
by studio_chrome.luau from the maps assets/textures/make_chrome.py makes; studio_tidy puts them on and keeps studs off
them, and Config/Lighting turns this world's reflections up. The renders fake them with metal and a thin film. No stud
texture in this file: kit.PREVIEW_STUDS is off, so every material is a plain colour. The studs come only in Studio, from
the shared "Studs" material that studio_tidy puts on the rest, the porcelain and marble (docs/MAP_RECIPE.md step 8).

What moves is MOTION below, the same numbers as shared/Config/PropMotion.luau (keep the two in step). Glowing roles
(GLOW_ROLES) must also be in shared/Roles.luau. Props that must face a certain way carry a small Front part on their
+Y side; MapDecor turns them, then removes it. Learned on the maps before (docs/MAP_RECIPE.md): no turn tied to a bob;
pieces that turn together share one centre; `about = "self"` turns round the part's bounding box, so whatever spins
that way is built symmetric round its axle.
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
from build_clockwork_citadel import Frame, obox, turn  # noqa: E402
from build_weeping_dark import link_chain, oval, outline  # noqa: E402
from map_kit import ball, beam, disc, flat_ring, gem, hoop, kit, limb, plate, prism, sparkle  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "models_shattered_mirror"

# Roles lit from inside. The game makes them Neon (shared/Roles.luau), so add new ones there too. FlameA is already there.
SPECTRUM = ("SpecA", "SpecB", "SpecC", "SpecD", "SpecE")
GLOW_ROLES = {"Fracture", "Gleam", "Facet", "Cascade", "CascadeB", "FlameA", "Note", "Spray", "SprayB", "ChandFlame", *SPECTRUM}
# Metal in the game: studio_tidy gives these roles one of the two MaterialVariants studio_chrome.luau makes (Foil, fully
# metal, almost mirror smooth), and no studs. HoloChrome is silver with rainbow flowing through it; the part's colour tints
# it, so the near-white roles are bright holographic chrome and the dark ones dark chrome. PolishedGold is tinted by the
# gold colours. Glass, crystal and the smoked violet glass are chrome too; porcelain, marble, velvet and eyes are not.
_HOLO = ("Silvered", "Splinter", "Turner", "TurnerFrame", "Tarnish", "Chrome", "ChromeDark", "Wheel", "Prism", "Pendant", "Quartz", "QuartzDark", "Rubble",
         "RubbleLight", "MoonCore", "MoonDark", "Smoked", "SmokedDark", "Panel", "Shatter", "ShatterB", "BoxLid", "Tutu", "FlapL", "FlapR", "Thorax", "PendRod",
         "PendGlass", "PrismL", "PrismR", "IsleA", "IsleB", "IsleC", "Swinger", "ChandDrop")
_GOLD = ("Gilt", "GiltDark", "Hub", "Floater", "PendantChain", "Turntable", "WindKey", "PendRim", "SwingerFrame", "Chand", "ChandRod", "SpanBar")
METAL = {**{role: "HoloChrome" for role in _HOLO}, **{role: "PolishedGold" for role in _GOLD}}
kit.NO_STUDS.update(GLOW_ROLES | set(METAL))
mk.GLOW_STRENGTH = 2.6

# Shared colours. The chrome roles' colours are the tint on the chrome (near white = the whole rainbow), and the gold's
# are the gold. Then white quartz, smoked violet glass, porcelain and marble, and the rainbow of light through glass.
SILVERED, TARNISH = "#f2f5fa", "#8a87a8"
CHROME, CHROME_DARK = "#e2e6ee", "#8d8fa3"
GILT, GILT_DARK = "#f4ca68", "#c39a4c"
QUARTZ, QUARTZ_DARK = "#f4f7fb", "#c9cfe0"
PRISM = "#e6e0fa"
SMOKED, SMOKED_DARK = "#5a5690", "#3a3666"
PORCELAIN, PORCELAIN_DARK = "#f0e9e1", "#c8bdb0"
MARBLE, MARBLE_DARK = "#ddd9e7", "#aaa5bb"
VELVET = "#7a2c52"
VOID = "#0b0a14"
FRACTURE = "#f4f8ff"
GLEAM = "#7ff3ff"  # the cold eyes of everything on the other side of the glass
CASCADE = "#e8f6ff"
FLAME = "#ffe2a8"
SPEC = {"SpecA": "#ff5c8a", "SpecB": "#ffb547", "SpecC": "#5cf5a8", "SpecD": "#56c8ff", "SpecE": "#a77bff"}

# The corridor's colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#b4b8c9", "FloorB": "#a7abbd", "Dirt": "#3a3760", "DirtB": "#33305a", "Grass": "#e4ebf3"}
SKY = "#efd9e6"


def prop(name, **colours):
    return mk.prop(name, **colours)


# ---------------------------------------------------------------------- shape helpers

FACING = (0, 1, 0)


def band(m, role, pts, y, depth, width, z_up=True):
    """A band round a closed outline of (x, z) points standing in the XZ plane at y: a frame round a mirror."""
    n = len(pts)
    for i in range(n):
        (x0, z0), (x1, z1) = pts[i], pts[(i + 1) % n]
        plate(m, role, (x0, y, z0), (x1, y, z1), FACING, depth, depth, width)
        m.block(role, x1, y, z1, width * 0.95, depth * 0.98, width * 0.95)


def crack(m, role, a, b, y, width=0.1, depth=0.06):
    """A glowing crack line on a face standing in the XZ plane, from (x, z) a to b, at depth y."""
    plate(m, role, (a[0], y, a[1]), (b[0], y, b[1]), FACING, depth, depth, width)


def crack_web(m, role, centre, reach, y, rng, rays=7, width=0.1, depth=0.06, inside=None):
    """Cracks running out from a blow at centre, each with a kink, and a broken ring round it. inside(x, z) keeps
    them on the glass."""
    cx, cz = centre
    for k in range(rays):
        a = k * math.tau / rays + rng.uniform(-0.25, 0.25)
        length = reach * rng.uniform(0.65, 1.0)
        a2 = a + rng.uniform(-0.35, 0.35)
        for _ in range(12):  # shorter until it stays on the glass
            mid = (cx + math.cos(a) * length * 0.45, cz + math.sin(a) * length * 0.45)
            end = (mid[0] + math.cos(a2) * length * 0.55, mid[1] + math.sin(a2) * length * 0.55)
            if not inside or (inside(*mid) and inside(*end)):
                break
            length *= 0.8
        crack(m, role, (cx, cz), mid, y, width, depth)
        crack(m, role, mid, end, y, width * 0.8, depth)
    r = reach * 0.28
    for k in range(rays):
        if k % 3 == 2:
            continue  # a broken ring
        a0, a1 = k * math.tau / rays, (k + 1) * math.tau / rays
        crack(m, role, (cx + math.cos(a0) * r, cz + math.sin(a0) * r), (cx + math.cos(a1) * r, cz + math.sin(a1) * r), y, width * 0.7, depth)


def flat_crack(m, role, a, b, z, width=0.12, depth=0.06):
    """A glowing crack lying flat on the floor, from (x, y) a to b."""
    plate(m, role, (a[0], a[1], z), (b[0], b[1], z), (0, 0, 1), depth, depth, width)


def shard_slab(m, role, origin, rot, w, h, thick, rng, edge=None):
    """A convex jagged shard of glass standing in its frame's XZ plane, its foot at the origin."""
    f = Frame(m, origin, rot)
    pts = [(-w / 2, 0), (w / 2, 0), (w * rng.uniform(0.3, 0.5), h * rng.uniform(0.45, 0.65)), (w * rng.uniform(-0.1, 0.25), h),
           (-w * rng.uniform(0.35, 0.5), h * rng.uniform(0.55, 0.8))]
    outline(m, role, f, pts, -thick / 2, thick / 2)
    if edge:  # one glowing crack down its face
        side = tuple(f.r @ Vector(FACING))
        p0, p1, p2 = f.at(-w * 0.15, thick / 2 + 0.04, h * 0.1), f.at(w * 0.08, thick / 2 + 0.04, h * 0.45), f.at(-w * 0.05, thick / 2 + 0.04, h * 0.75)
        plate(m, edge, p0, p1, side, 0.06, 0.06, 0.09)
        plate(m, edge, p1, p2, side, 0.06, 0.06, 0.07)
    return f


def rainbow(m, foot, ahead, length, spread, z=0.06, w0=0.14, w1=0.75, roles=SPECTRUM, start_at=1.4):
    """Light split by glass: bands of colour fanning out across the floor from foot, towards the angle `ahead`. They start
    start_at out, where they're already apart, so no two lie on one another (that shimmers)."""
    n = len(roles)
    for k, role in enumerate(roles):
        a = ahead + (k - (n - 1) / 2) * spread
        start = (foot[0] + math.cos(a) * start_at, foot[1] + math.sin(a) * start_at, z + k * 0.02)
        end = (foot[0] + math.cos(a) * length, foot[1] + math.sin(a) * length, z + k * 0.02)
        plate(m, role, start, end, (-math.sin(a), math.cos(a), 0), w0, w1, 0.05)


def rubble(m, roles, count, rx, ry, size, rng, z=0.0):
    """A low heap of broken glass."""
    for k in range(count):
        a = rng.uniform(0, math.tau)
        r = math.sqrt(rng.random())
        s = rng.uniform(*size)
        obox(m, roles[k % len(roles)], (math.cos(a) * rx * r, math.sin(a) * ry * r, z + s * 0.2), (s, s * rng.uniform(0.6, 1.1), s * 0.4),
             turn(rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0, math.pi)))


# ---------------------------------------------------------------------- floor props

MIRROR_CZ, MIRROR_RX, MIRROR_RZ = 6.2, 2.3, 4.3


def standing_mirror(seed=1):
    """The map's signature: a tall gilt mirror on claw feet, cracked from one blow. Standing in it, where your
    reflection should be, is a shape that isn't yours: it breathes, and its eyes are open. Two splinters of the glass
    hang in the air in front of it, circling."""
    m = prop("StandingMirror", Gilt=GILT, GiltDark=GILT_DARK, Silvered=SILVERED, Tarnish=TARNISH, Fracture=FRACTURE, Reflection=SMOKED_DARK,
             Gleam=GLEAM, Splinter=SILVERED, Rubble=QUARTZ_DARK)
    rng = random.Random(seed)
    cz, rx, rz = MIRROR_CZ, MIRROR_RX, MIRROR_RZ
    f = Frame(m, (0, 0, 0))
    m.block("GiltDark", 0, 0, 0.3, 5.4, 2.2, 0.6)
    for s in (-1, 1):
        for dy in (-0.7, 0.7):
            ball(m, "GiltDark", s * 2.35, dy, 0.42, 0.42, 8, 4)  # claw feet
        beam(m, "Gilt", (s * 1.9, 0, 0.6), (s * 1.25, 0, cz - rz * 0.93), 0.55, None, 0.42)
    outline(m, "GiltDark", f, oval(rx + 0.25, rz + 0.25, 24, 0, cz), -0.34, -0.14)  # the back
    outline(m, "Silvered", f, oval(rx, rz, 24, 0, cz), -0.14, 0.12)
    band(m, "Gilt", oval(rx + 0.32, rz + 0.32, 24, 0, cz), -0.05, 0.62, 0.55)
    gem(m, "Gilt", 0, 0, cz + rz + 1.0, 0.6, 1.3, 0.5, 4)
    for s in (-1, 1):
        ball(m, "Gilt", s * 1.2, 0, cz + rz + 0.25, 0.42, 8, 4)
        ball(m, "Gilt", s * (rx + 0.35), 0, cz, 0.36, 8, 4)
    # Its reflection: a silhouette that isn't the viewer's, a little hunched, arms hanging long.
    body = [(-1.3, cz - 3.0), (1.3, cz - 3.0), (1.25, cz + 0.1), (0.95, cz + 0.5), (0.32, cz + 0.72), (-0.32, cz + 0.72), (-0.95, cz + 0.5), (-1.25, cz + 0.1)]
    outline(m, "Reflection", f, body, 0.13, 0.16)
    outline(m, "Reflection", f, oval(0.56, 0.72, 12, 0.0, cz + 1.4), 0.13, 0.16)
    for s in (-1, 1):
        m.block("Gleam", s * 0.22, 0.22, cz + 1.47, 0.22, 0.08, 0.1)
    inside = lambda x, z: (x / (rx - 0.2)) ** 2 + ((z - cz) / (rz - 0.2)) ** 2 < 1  # noqa: E731
    blow = (-1.0, cz + 2.7)  # the blow landed high on one side, clear of the face
    crack_web(m, "Fracture", blow, 3.6, 0.2, rng, 8, inside=inside)
    for k in range(3):  # pieces knocked loose at the blow
        a = k * math.tau / 3 + 0.4
        obox(m, "Tarnish", (blow[0] + math.cos(a) * 0.45, 0.24, blow[1] + math.sin(a) * 0.45), (0.5, 0.05, 0.36), turn(0.15, 0.2 * (k - 1), a))
    for s in (-1, 1):  # the splinters circling in front of it
        gem(m, "Splinter", 0.6 + s * 1.5, 1.8, cz + 0.8 + s * 0.3, 0.32, 0.9, 0.65, 3, s)
    rubble(m, ("Rubble", "Tarnish"), 9, 3.2, 2.2, (0.25, 0.6), rng)
    return m


def shard_cluster(seed=2):
    """Mirror shards as tall as a house stuck in the ground at angles, cracked down their faces. The biggest piece hangs
    in the air above them, turning slowly, and the light through them spills rainbows on the floor."""
    m = prop("ShardCluster", Silvered=SILVERED, Tarnish=TARNISH, Fracture=FRACTURE, Splinter=SILVERED, Rubble=QUARTZ_DARK, RubbleLight=QUARTZ,
             **SPEC)
    rng = random.Random(seed)
    rubble(m, ("Rubble", "RubbleLight", "Tarnish"), 14, 3.6, 3.0, (0.4, 1.0), rng)
    for x, y, yaw, tx, ty, w, h in ((0, -0.4, 0.2, 0.08, -0.12, 2.6, 9.0), (-1.9, 0.6, -0.7, -0.15, 0.25, 2.0, 6.2), (1.8, 0.4, 0.9, 0.2, 0.18, 1.9, 6.8),
                                    (0.6, 1.6, 2.1, -0.28, 0.05, 1.6, 4.4), (-1.2, -1.7, 1.2, 0.22, -0.2, 1.5, 4.0), (2.3, -1.4, -0.3, 0.1, 0.3, 1.2, 3.2)):
        shard_slab(m, "Silvered" if h > 4.2 else "Tarnish", (x, y, -0.4), turn(tx, ty, yaw), w * 1.6, h + 0.4, 0.34, rng, "Fracture" if h > 5 else None)
    gem(m, "Splinter", 0, 0, 11.6, 1.0, 2.2, 1.7, 3)
    rainbow(m, (0.3, 1.2), math.pi / 2 - 0.2, 6.0, 0.13, roles=("SpecA", "SpecC", "SpecE"))
    return m


def prism_obelisk(seed=3):
    """A three-sided pillar of glass on a silver plinth. A prism hangs turning over its point, and the light through it
    pours a rainbow across the floor."""
    m = prop("PrismObelisk", Chrome=CHROME, ChromeDark=CHROME_DARK, Quartz=PRISM, QuartzDark=QUARTZ_DARK, Prism=QUARTZ, Facet=FRACTURE, **SPEC)
    m.loft_z("ChromeDark", (0, 0, 0, 4.4, 4.4), (0.6, 0, 0, 4.0, 4.0))
    m.loft_z("Chrome", (0.6, 0, 0, 3.2, 3.2), (1.2, 0, 0, 2.8, 2.8))
    prism(m, "Quartz", 0, 0, 1.2, 9.4, 1.55, 0.95, 3, math.pi / 2)
    prism(m, "QuartzDark", 0, 0, 9.4, 10.6, 0.95, 0.05, 3, math.pi / 2)
    for k in range(3):  # the edges catch the light
        a = math.pi / 2 + k * math.tau / 3
        beam(m, "Facet", (math.cos(a) * 1.6, math.sin(a) * 1.6, 1.3), (math.cos(a) * 1.0, math.sin(a) * 1.0, 9.3), 0.12)
    gem(m, "Prism", 0, 0, 12.6, 0.95, 1.4, 1.4, 3)
    rainbow(m, (0, 1.4), math.pi / 2, 7.5, 0.11)
    return m


HEAD_Z = 6.75


def glass_gazer(seed=4):
    """A porcelain mannequin on its stand, one arm pointing at you. Its face is a cracked mirror with one cold eye in
    it, and its head turns after you."""
    m = prop("GlassGazer", Porcelain=PORCELAIN, PorcelainDark=PORCELAIN_DARK, ChromeDark=CHROME_DARK, Visage=PORCELAIN, Silvered=SILVERED,
             Fracture=FRACTURE, Gleam=GLEAM)
    disc(m, "ChromeDark", 0, 0, 0.15, 1.6, 0.3, 12)
    for s in (-1, 1):
        limb(m, "Porcelain", [(s * 0.45, 0, 3.2), (s * 0.5, 0.15, 1.8), (s * 0.48, 0, 0.5)], 0.62, 0.36)
        ball(m, "PorcelainDark", s * 0.5, 0.15, 1.8, 0.36, 8, 4)  # the knees' joints
        m.block("Porcelain", s * 0.48, 0.25, 0.42, 0.42, 0.9, 0.24)
    m.loft_z("Porcelain", (3.0, 0, 0, 1.7, 1.0), (3.7, 0, 0, 1.9, 1.1))
    m.loft_z("Porcelain", (3.7, 0, 0, 1.9, 1.1), (4.3, 0, 0, 1.3, 0.85))
    m.loft_z("Porcelain", (4.3, 0, 0, 1.3, 0.85), (5.7, 0, 0, 2.3, 1.15))
    m.loft_z("PorcelainDark", (5.7, 0, 0, 2.3, 1.15), (5.95, 0, 0, 1.4, 0.8))
    prism(m, "Porcelain", 0, 0, 5.9, 6.3, 0.26, 0.24, 8)
    for s in (-1, 1):
        ball(m, "PorcelainDark", s * 1.15, 0, 5.45, 0.34, 8, 4)
    limb(m, "Porcelain", [(-1.2, 0, 5.4), (-1.35, 0.1, 4.2), (-1.25, 0.25, 3.1)], 0.38, 0.26)  # hanging
    limb(m, "Porcelain", [(1.2, 0, 5.4), (1.35, 0.9, 4.75), (1.05, 2.2, 5.15)], 0.38, 0.24)  # pointing at you
    ball(m, "PorcelainDark", 1.35, 0.9, 4.75, 0.28, 8, 4)
    beam(m, "Porcelain", (1.05, 2.2, 5.15), (1.0, 2.75, 5.25), 0.16, 0.14)  # the pointing finger
    m.block("Porcelain", 1.05, 2.3, 5.12, 0.34, 0.4, 0.3)
    # The head turns: everything on it is built round x = 0, y = 0.
    ball(m, "Visage", 0, 0, HEAD_Z, 0.72, 10, 6)
    f = Frame(m, (0, 0, 0))
    outline(m, "Silvered", f, oval(0.52, 0.62, 14, 0, HEAD_Z + 0.02), 0.45, 0.78)
    crack(m, "Fracture", (-0.4, HEAD_Z + 0.35), (0.05, HEAD_Z - 0.05), 0.81, 0.07, 0.05)
    crack(m, "Fracture", (0.05, HEAD_Z - 0.05), (0.3, HEAD_Z - 0.5), 0.81, 0.06, 0.05)
    m.block("Gleam", 0.2, 0.83, HEAD_Z + 0.12, 0.2, 0.06, 0.12)
    return m


BLOOM_Z = 6.0


def kaleido_bloom(seed=5):
    """A flower of mirror petals on a silver stem, its head turning slowly like a kaleidoscope."""
    m = prop("KaleidoBloom", Chrome=CHROME, ChromeDark=CHROME_DARK, Silvered=SILVERED, Gilt=GILT, Facet=FRACTURE, Rubble=QUARTZ_DARK)
    rng = random.Random(seed)
    rubble(m, ("Rubble",), 6, 1.4, 1.4, (0.3, 0.6), rng)
    limb(m, "Chrome", [(0.3, 0.1, 0), (0.45, 0, 2.2), (0.1, -0.1, 4.2), (0, 0, BLOOM_Z - 0.3)], 0.42, 0.3)
    for s, z in ((-1, 1.6), (1, 2.8)):  # two pointed leaves
        root, mid, tip = (0.4, 0, z), (0.4 + s * 1.5, 0.2, z + 0.6), (0.4 + s * 2.9, 0.3, z + 1.5)
        plate(m, "ChromeDark", root, mid, (0, 1, 0.3), 0.3, 1.2, 0.1)
        plate(m, "ChromeDark", mid, tip, (0, 1, 0.3), 1.2, 0.08, 0.1)
    for k in range(6):  # six broad mirror petals, open to the sky so the flight sees into it, each ending in a point
        a = k * math.tau / 6
        c, s = math.cos(a), math.sin(a)
        plate(m, "Silvered", (c * 0.45, s * 0.45, BLOOM_Z), (c * 2.4, s * 2.4, BLOOM_Z + 0.75), (-s, c, 0), 0.6, 1.7, 0.12)
        plate(m, "Silvered", (c * 2.4, s * 2.4, BLOOM_Z + 0.75), (c * 3.6, s * 3.6, BLOOM_Z + 1.35), (-s, c, 0), 1.7, 0.1, 0.12)
        b = a + math.tau / 12
        plate(m, "Gilt", (math.cos(b) * 0.4, math.sin(b) * 0.4, BLOOM_Z + 0.15), (math.cos(b) * 1.8, math.sin(b) * 1.8, BLOOM_Z + 1.3),
              (-math.sin(b), math.cos(b), 0), 0.3, 0.8, 0.1)
    gem(m, "Facet", 0, 0, BLOOM_Z + 0.25, 0.5, 0.9, 0.4, 6)
    return m


def fallen_chandelier(seed=6):
    """A crystal chandelier come down from a ceiling nobody can see, crashed on its side with its chain coiled beside it.
    Its candles are still burning and its crystals still tremble."""
    m = prop("FallenChandelier", Gilt=GILT, GiltDark=GILT_DARK, Quartz=QUARTZ, Pendant=PRISM, FlameA=FLAME, Facet=FRACTURE, Rubble=QUARTZ_DARK)
    rng = random.Random(seed)
    tilt = turn(0.32, 0.08, 0.3)
    f = Frame(m, (0, 0, 1.3), tilt)
    rim = [f.at(math.cos(k * math.tau / 16) * 3.0, math.sin(k * math.tau / 16) * 3.0, 0) for k in range(16)]
    for k in range(16):
        beam(m, "Gilt", rim[k], rim[(k + 1) % 16], 0.36, 0.36)
    inner = [f.at(math.cos(k * math.tau / 10) * 1.5, math.sin(k * math.tau / 10) * 1.5, 1.0) for k in range(10)]
    for k in range(10):
        beam(m, "Gilt", inner[k], inner[(k + 1) % 10], 0.28, 0.28)
    for k in range(8):
        a = k * math.tau / 8
        f.beam("GiltDark", (math.cos(a) * 2.9, math.sin(a) * 2.9, 0), (0, 0, 1.7), 0.22)
    f.prism("GiltDark", 0, 0, -0.4, 2.6, 0.32, 0.22, 8)
    ball(m, "Gilt", *f.at(0, 0, 2.7), 0.4, 8, 4)
    link_chain(m, "GiltDark", f.at(0, 0, 3.0), (-1.4, -5.5, 0.35), 9, 0.4)
    for k in range(8):  # candles stand up from the ring, tilted with it
        a = (k + 0.5) * math.tau / 8
        x, y = math.cos(a) * 3.0, math.sin(a) * 3.0
        f.prism("GiltDark", x, y, 0.1, 0.35, 0.3, 0.32, 8)
        f.prism("Quartz", x, y, 0.35, 1.2, 0.17, 0.16, 6)
        gem(m, "FlameA", *f.at(x, y, 1.5), 0.13, 0.36, 0.12, 5)
    for k in range(16):  # crystals hang straight down from the high side of the ring
        p = Vector(rim[k])
        if p.z < 1.75:
            continue
        drop = rng.uniform(0.7, 1.1)
        beam(m, "Pendant", tuple(p), (p.x, p.y, p.z - drop), 0.06)
        gem(m, "Pendant", p.x, p.y, p.z - drop - 0.25, 0.18, 0.25, 0.45, 4)
    rubble(m, ("Rubble", "Quartz"), 10, 4.0, 3.4, (0.15, 0.4), rng)
    for x, y in ((2.6, 2.2), (-2.8, 1.2), (1.0, -3.3)):
        sparkle(m, "Facet", x, y, 0.5, 0.35)
    return m


def split_statue(seed=7):
    """A marble figure that burst apart and never fell: its robe stands on the plinth, and above it the chest, the head
    and an arm float apart, rising and sinking out of step, the head's eyes open."""
    m = prop("SplitStatue", Marble=MARBLE, MarbleDark=MARBLE_DARK, PieceA=MARBLE, PieceB=MARBLE, PieceC=MARBLE, Gleam=GLEAM, Facet=FRACTURE)
    m.loft_z("MarbleDark", (0, 0, 0, 3.6, 3.6), (1.0, 0, 0, 3.2, 3.2))
    m.loft_z("Marble", (1.0, 0, 0, 2.6, 2.2), (3.5, 0, 0, 1.9, 1.4))  # the robe's skirt, broken off at the waist
    for k in range(5):
        obox(m, "MarbleDark", (-0.8 + k * 0.4, 0.62, 2.1), (0.22, 0.2, 2.2), turn(0.1, 0, 0))
    obox(m, "PieceA", (0, 0, 5.2), (2.1, 1.3, 2.0), turn(0.06, -0.05, 0.08))  # the chest
    obox(m, "PieceA", (0, 0, 4.35), (1.6, 1.1, 0.5), turn(0.06, -0.05, 0.08))
    obox(m, "PieceA", (-0.35, 0.7, 5.3), (1.5, 0.45, 0.5), turn(0, 0, 0.35))  # an arm folded across it
    ball(m, "PieceB", 0, 0.05, 7.95, 0.75, 10, 6)  # the head
    obox(m, "PieceB", (0, 0.05, 7.35), (0.5, 0.5, 0.4), turn())
    for s in (-1, 1):
        m.block("Gleam", s * 0.26, 0.74, 8.02, 0.22, 0.08, 0.1)
    obox(m, "PieceC", (2.1, 0.1, 5.6), (0.55, 0.55, 2.2), turn(0, 0.5, 0))  # the other arm, drifting off
    obox(m, "PieceC", (2.55, 0.1, 4.6), (0.5, 0.6, 0.6), turn(0, 0.5, 0))
    for x, y, z in ((-1.4, 0.6, 6.6), (1.3, -0.5, 7.4), (0.8, 0.9, 3.9)):
        sparkle(m, "Facet", x, y, z, 0.3)
    return m


def empty_frames(seed=8):
    """A rare treat: a heap of empty gilt frames leant on one another. In the biggest there's no glass and no picture,
    only two eyes in the empty air. A little frame floats above the heap, turning."""
    m = prop("EmptyFrames", Gilt=GILT, GiltDark=GILT_DARK, Velvet=VELVET, Gleam=GLEAM, Floater=GILT, Rubble=QUARTZ_DARK)
    rng = random.Random(seed)

    def frame(role, origin, rot, w, h, bar):
        f = Frame(m, origin, rot)
        for x, z, bw, bh in ((0, bar / 2, w, bar), (0, h - bar / 2, w, bar), (-w / 2 + bar / 2, h / 2, bar, h), (w / 2 - bar / 2, h / 2, bar, h)):
            f.box(role, x, 0, z, bw, bar * 0.8, bh)
        return f

    frame("GiltDark", (-1.6, -0.6, 0), turn(-0.25, 0, 0.3), 3.4, 4.2, 0.45)
    back = frame("GiltDark", (1.7, -0.4, 0), turn(-0.2, 0, -0.4), 2.6, 3.0, 0.4)
    back.box("Velvet", 0, -0.12, 1.5, 1.8, 0.1, 2.2)
    big = frame("Gilt", (0, 0.6, 0), turn(-0.18, 0, 0), 4.6, 6.4, 0.6)
    big.box("Gilt", 0, 0, 6.6, 1.2, 0.5, 0.6)
    for s in (-1, 1):
        big.box("Gleam", s * 0.42, 0, 3.6, 0.42, 0.12, 0.16)
    hoop(m, "Floater", 0, 0, 9.4, 0.9, 0.22, "xz", 4)  # a little square frame, turning in the air
    rubble(m, ("Rubble",), 8, 3.2, 2.4, (0.2, 0.5), rng)
    return m


def glass_tuft(seed=9):
    """Filler: a tuft of thin glass spikes, their tips catching the light."""
    m = prop("GlassTuft", Quartz=QUARTZ, QuartzDark=QUARTZ_DARK, Facet=FRACTURE)
    rng = random.Random(seed)
    for k in range(7):
        a = k * math.tau / 7 + rng.uniform(-0.3, 0.3)
        r = rng.uniform(0.2, 0.8)
        h = rng.uniform(1.6, 3.4)
        lean = (math.cos(a) * h * 0.2, math.sin(a) * h * 0.2)
        x, y = math.cos(a) * r, math.sin(a) * r
        prism(m, "Quartz" if k % 2 else "QuartzDark", x, y, -0.2, h * 0.8, 0.18, 0.12, 4, a, (lean[0] * 0.8, lean[1] * 0.8))
        prism(m, "Facet", x + lean[0] * 0.8, y + lean[1] * 0.8, h * 0.8, h, 0.12, 0.02, 4, a, (lean[0] * 0.2, lean[1] * 0.2))
    return m


def shard_scatter(seed=10):
    """Filler: broken bits of mirror on the ground, twinkling."""
    m = prop("ShardScatter", Silvered=SILVERED, Tarnish=TARNISH, Facet=FRACTURE)
    rng = random.Random(seed)
    for k in range(9):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0.3, 2.4)
        obox(m, "Silvered" if k % 3 else "Tarnish", (math.cos(a) * r, math.sin(a) * r, 0.1), (rng.uniform(0.5, 1.1), rng.uniform(0.4, 0.8), 0.1),
             turn(rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12), rng.uniform(0, math.pi)))
    for x, y, yaw in ((0.4, -0.3, 0.4), (-0.9, 0.7, 2.0)):
        shard_slab(m, "Silvered", (x, y, -0.2), turn(0.15, -0.1, yaw), 0.9, 1.9, 0.12, rng)
    for x, y, z in ((1.1, 0.8, 0.6), (-1.4, -0.6, 0.5), (0.2, 1.6, 0.9)):
        sparkle(m, "Facet", x, y, z, 0.3)
    return m


def mirror_pool(seed=11):
    """Flat, for the middle of the floor where eggs land: a round mirror set in the floor in a gilt ring, cracked from
    one blow, with rings of rainbow shimmering out across it."""
    m = prop("MirrorPool", Silvered=SILVERED, Gilt=GILT, Fracture=FRACTURE, **SPEC)
    rng = random.Random(seed)
    disc(m, "Silvered", 0, 0, 0.1, 4.3, 0.2, 28)
    flat_ring(m, "Gilt", 0, 0, 0.16, 4.5, 0.55, 0.3, 28)
    for k, role in enumerate(SPECTRUM):
        flat_ring(m, role, 0, 0, 0.215, 1.15 + k * 0.5, 0.16, 0.04, 24)
    cx, cy = 0.9, 0.5
    for k in range(8):
        a = k * math.tau / 8 + rng.uniform(-0.2, 0.2)
        length = rng.uniform(2.6, 3.4)
        mid = (cx + math.cos(a) * length * 0.45, cy + math.sin(a) * length * 0.45)
        a2 = a + rng.uniform(-0.3, 0.3)
        end = (mid[0] + math.cos(a2) * length * 0.55, mid[1] + math.sin(a2) * length * 0.55)
        while math.hypot(*end) > 4.0:
            end = ((end[0] + mid[0]) / 2, (end[1] + mid[1]) / 2)
        flat_crack(m, "Fracture", (cx, cy), mid, 0.25)
        flat_crack(m, "Fracture", mid, end, 0.25, 0.1)
    return m


# ---------------------------------------------------------------------- rim props


def glass_tree(seed=12):
    """A silver tree whose leaves are little mirrors, its crown swaying, sparks of light in it."""
    m = prop("GlassTree", Chrome=CHROME, ChromeDark=CHROME_DARK, Silvered=SILVERED, Facet=FRACTURE, Rubble=QUARTZ_DARK)
    rng = random.Random(seed)
    rubble(m, ("Rubble",), 6, 1.8, 1.8, (0.3, 0.7), rng)
    limb(m, "ChromeDark", [(0, 0, -0.3), (0.2, 0.1, 3.0), (-0.2, 0, 6.0)], 1.3, 0.85)
    ends = []
    for k in range(5):
        a = k * math.tau / 5 + rng.uniform(-0.2, 0.2)
        r = rng.uniform(3.0, 4.2)
        tip = (math.cos(a) * r, math.sin(a) * r, rng.uniform(9.0, 11.5))
        limb(m, "Chrome", [(-0.2, 0, 5.6), (math.cos(a) * r * 0.45, math.sin(a) * r * 0.45, 8.0), tip], 0.6, 0.25)
        ends.append(tip)
    ends.append((0, 0, 12.8))
    limb(m, "Chrome", [(-0.2, 0, 5.8), (0, 0.2, 9.5), (0, 0, 12.6)], 0.6, 0.3)
    for x, y, z in ends:  # a bunch of mirror leaves round each branch's end
        for j in range(7):
            a = j * math.tau / 7 + rng.uniform(-0.3, 0.3)
            r = rng.uniform(0.6, 1.6)
            gem(m, "Silvered", x + math.cos(a) * r, y + math.sin(a) * r, z + rng.uniform(-0.8, 0.9), 0.55, 0.7, 0.7, 4, a)
    for x, y, z in ends[::2]:
        sparkle(m, "Facet", x + 0.4, y - 0.6, z + 1.4, 0.35)
    return m


def mirror_maze(seed=13):
    """What's left of a hall of mirrors: tall panels in silver frames standing in a broken row, some smashed half away.
    The one in the middle revolves slowly on its own."""
    m = prop("MirrorMaze", Chrome=CHROME, ChromeDark=CHROME_DARK, Silvered=SILVERED, Tarnish=TARNISH, Turner=SILVERED, TurnerFrame=CHROME,
             Fracture=FRACTURE, Rubble=QUARTZ_DARK)
    rng = random.Random(seed)

    def panel(origin, yaw, pane, frame_role, broken=False):
        f = Frame(m, origin, turn(0, 0, yaw))
        w, h = 3.0, 9.0
        for x, z, bw, bh in ((0, 0.25, w + 0.5, 0.5), (0, h + 0.25, w + 0.5, 0.5), (-w / 2, h / 2 + 0.25, 0.5, h), (w / 2, h / 2 + 0.25, 0.5, h)):
            if broken and z > h:
                continue
            f.box(frame_role, x, 0, z, bw, 0.6, bh)
        if broken:  # smashed: only a jagged bottom half of glass is left
            outline(m, pane, f, [(-w / 2 + 0.2, 0.5), (w / 2 - 0.2, 0.5), (w / 2 - 0.2, 4.6), (0.3, 6.2), (-w / 2 + 0.2, 3.8)], -0.15, 0.15)
            f.box(frame_role, -w / 2, 0, h * 0.35 + 0.25, 0.5, 0.6, h * 0.7)
        else:
            f.box(pane, 0, 0, h / 2 + 0.25, w - 0.4, 0.3, h - 0.4)
        return f

    for x, y, yaw, broken in ((-8.0, 0.6, 0.35, False), (-4.4, -0.6, -0.25, True), (4.4, -0.5, 0.3, False), (8.0, 0.7, -0.4, True)):
        f = panel((x, y, 0), yaw, "Silvered" if not broken else "Tarnish", "ChromeDark")
        if not broken:  # a crack down the whole panels' faces
            side = tuple(f.r @ Vector(FACING))
            p = [f.at(-0.7, 0.2, 6.8), f.at(0.2, 0.2, 5.0), f.at(-0.1, 0.2, 3.2)]
            plate(m, "Fracture", p[0], p[1], side, 0.06, 0.06, 0.09)
            plate(m, "Fracture", p[1], p[2], side, 0.06, 0.06, 0.08)
    panel((0, 0, 0), 0, "Turner", "TurnerFrame")  # revolves round its own middle: built straight and centred
    rubble(m, ("Rubble", "Tarnish"), 12, 10.0, 2.4, (0.3, 0.8), rng)
    return m


# ---------------------------------------------------------------------- landmarks and set pieces

GLASS_CZ = 21.0  # the Looking Glass's pane centre, where its eye looks round


def looking_glass(seed=14):
    """A hand mirror the size of a tower, stuck handle first in the ground and cracked across. There's an eye in the glass,
    looking round for you, and great splinters of it circle the whole thing."""
    m = prop("LookingGlass", Gilt=GILT, GiltDark=GILT_DARK, Silvered=SILVERED, Fracture=FRACTURE, Sclera=PORCELAIN, Gleam=GLEAM, Void=VOID,
             Splinter=SILVERED, Rubble=QUARTZ_DARK, Tarnish=TARNISH, Front=GILT)
    rng = random.Random(seed)
    cz, rx, rz = GLASS_CZ, 7.0, 9.0
    f = Frame(m, (0, 0, 0))
    rubble(m, ("Rubble", "Tarnish"), 16, 5.5, 4.5, (0.6, 1.6), rng)
    prism(m, "Gilt", 0, 0, -1.0, 10.5, 1.1, 1.35, 10, math.pi / 10)
    for z in (2.0, 4.5, 7.0):
        prism(m, "GiltDark", 0, 0, z - 0.35, z + 0.35, 1.45, 1.55, 10, math.pi / 10)
    m.loft_z("GiltDark", (10.5, 0, 0, 2.8, 2.2), (cz - rz + 0.2, 0, 0, 5.0, 2.2))
    outline(m, "GiltDark", f, oval(rx + 0.6, rz + 0.6, 28, 0, cz), -1.0, -0.4)
    outline(m, "Silvered", f, oval(rx, rz, 28, 0, cz), -0.4, 0.4)
    band(m, "Gilt", oval(rx + 0.75, rz + 0.75, 28, 0, cz), -0.1, 1.6, 1.4)
    gem(m, "Gilt", 0, 0, cz + rz + 2.2, 1.3, 2.6, 1.1, 4)
    for s in (-1, 1):
        ball(m, "Gilt", s * 2.6, 0, cz + rz + 0.9, 0.9, 8, 4)
    inside = lambda x, z: (x / (rx - 0.4)) ** 2 + ((z - cz) / (rz - 0.4)) ** 2 < 1  # noqa: E731
    crack_web(m, "Fracture", (-3.4, cz + 4.4), 10.0, 0.48, rng, 9, 0.22, 0.1, inside)
    # The eye: an almond of white, and the iris and pupil off its middle, turning round it to look about.
    almond = [(math.cos(k * math.tau / 20) * 3.8, cz + math.sin(k * math.tau / 20) * 2.3 * (1 - 0.25 * math.cos(k * math.tau / 20) ** 2)) for k in range(20)]
    outline(m, "Sclera", f, almond, 0.4, 0.62)
    disc(m, "Gleam", 0.95, 0.68, cz + 0.2, 1.25, 0.1, 18, "xz")
    disc(m, "Void", 0.95, 0.79, cz + 0.2, 0.6, 0.1, 14, "xz")
    for k in range(4):  # splinters circling the whole thing
        a = k * math.tau / 4 + 0.4
        gem(m, "Splinter", math.cos(a) * 12.0, math.sin(a) * 12.0, 13.0 + 3.5 * k, 1.1, 2.6, 2.0, 3, a)
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


WHEEL = (0.0, 1.4, 30.0)  # the kaleidoscope wheel's hub


def kaleido_tower(seed=15):
    """A spire of smoked violet glass with silver bands, a rose window of rainbow glass turning on top of it."""
    m = prop("KaleidoTower", Smoked=SMOKED, SmokedDark=SMOKED_DARK, Chrome=CHROME, Wheel=CHROME, Hub=GILT, Facet=FRACTURE, Rubble=QUARTZ_DARK, Front=CHROME,
             **SPEC)
    rng = random.Random(seed)
    rubble(m, ("Rubble",), 10, 5.0, 5.0, (0.6, 1.4), rng)
    m.loft_z("SmokedDark", (0, 0, 0, 8.0, 8.0), (4.0, 0, 0, 6.6, 6.6))
    prism(m, "Smoked", 0, 0, 4.0, 14.0, 3.5, 2.8, 8, math.pi / 8)
    prism(m, "Chrome", 0, 0, 13.6, 14.6, 3.0, 3.0, 8, math.pi / 8)
    prism(m, "Smoked", 0, 0, 14.6, 22.0, 2.7, 2.1, 8, math.pi / 8)
    prism(m, "Chrome", 0, 0, 21.6, 22.6, 2.4, 2.4, 8, math.pi / 8)
    prism(m, "SmokedDark", 0, 0, 22.6, 24.0, 2.2, 1.4, 8, math.pi / 8)
    for k in range(8):  # slit windows of light up the spire
        a = (k + 0.5) * math.tau / 8
        for z, r in ((9.0, 3.2), (18.3, 2.45)):
            obox(m, "Facet", (math.cos(a) * r, math.sin(a) * r, z), (0.5, 0.2, 2.4), turn(0, 0, a + math.pi / 2))
    hx, hy, hz = WHEEL
    for s in (-1, 1):  # the cradle the wheel turns in
        beam(m, "Chrome", (s * 1.6, 0, 23.6), (s * 3.2, hy - 0.6, hz - 4.0), 0.7)
        beam(m, "Chrome", (s * 3.2, hy - 0.6, hz - 4.0), (s * 1.0, hy - 0.6, hz), 0.6)
    radius = 7.0
    hoop(m, "Wheel", hx, hy, hz, radius, 0.7, "xz", 20)
    hoop(m, "Wheel", hx, hy, hz, radius * 0.45, 0.4, "xz", 12)
    f = Frame(m, (0, 0, 0))
    for k in range(10):
        a0, a1 = k * math.tau / 10, (k + 1) * math.tau / 10
        f.beam("Wheel", (hx + math.cos(a0) * 0.9, hy, hz + math.sin(a0) * 0.9), (hx + math.cos(a0) * radius, hy, hz + math.sin(a0) * radius), 0.35, 0.35)
        role = SPECTRUM[k % 5]  # each colour twice, opposite itself, so the pair turns round the hub
        pts = [(hx + math.cos(a0 + 0.06) * 1.3, hz + math.sin(a0 + 0.06) * 1.3), (hx + math.cos(a0 + 0.05) * (radius - 0.5), hz + math.sin(a0 + 0.05) * (radius - 0.5)),
               (hx + math.cos(a1 - 0.05) * (radius - 0.5), hz + math.sin(a1 - 0.05) * (radius - 0.5)), (hx + math.cos(a1 - 0.06) * 1.3, hz + math.sin(a1 - 0.06) * 1.3)]
        outline(m, role, f, pts, hy - 0.12, hy + 0.12)
    disc(m, "Hub", hx, hy, hz, 1.0, 0.9, 12, "xz")
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


MOON_Z = 120.0


def broken_moon(seed=16):
    """A sky piece: the moon, cracked like a dropped mirror, its pieces broken off and circling it."""
    m = prop("BrokenMoon", MoonCore=QUARTZ, MoonDark=QUARTZ_DARK, Fracture=FRACTURE, Splinter=SILVERED, Tarnish=TARNISH)
    rng = random.Random(seed)
    ball(m, "MoonCore", 0, 0, MOON_Z, 14.0, 12, 8)
    for k in range(7):  # craters
        a, e = rng.uniform(0, math.tau), rng.uniform(-0.8, 0.8)
        n = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
        c = n * 13.6 + Vector((0, 0, MOON_Z))
        disc(m, "MoonDark", c.x, c.y, c.z, rng.uniform(1.6, 3.0), 1.0, 10) if abs(e) > 0.6 else ball(m, "MoonDark", c.x, c.y, c.z, rng.uniform(1.6, 2.6), 8, 4)
    for k in range(9):  # bright seams across it
        a0 = k * math.tau / 9
        pts = []
        for j in range(4):
            e = -1.1 + j * 0.7 + rng.uniform(-0.15, 0.15)
            a = a0 + rng.uniform(-0.25, 0.25)
            pts.append(Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))) * 14.3 + Vector((0, 0, MOON_Z)))
        for p, q in zip(pts, pts[1:]):
            beam(m, "Fracture", tuple(p), tuple(q), 0.5, 0.5)
    for k in range(10):  # the pieces broken off, circling it
        a = k * math.tau / 10 + rng.uniform(-0.15, 0.15)
        r = rng.uniform(21.0, 27.0)
        gem(m, "Splinter" if k % 3 else "Tarnish", math.cos(a) * r, math.sin(a) * r, MOON_Z + rng.uniform(-8, 8), rng.uniform(1.6, 2.8),
            rng.uniform(2.4, 4.0), rng.uniform(2.0, 3.2), 3, a)
    return m


def shardfall(seed=17):
    """On the corridor wall: the glass of the wall broken open, and splinters pouring out of the hole all the way down
    to a heap on the floor. Its origin is the wall's top inner edge (rim Z = 0, floor Z = -44), +Y out over the corridor."""
    m = prop("Shardfall", Panel=SMOKED, Hole=VOID, Silvered=SILVERED, Tarnish=TARNISH, Fracture=FRACTURE, Cascade=CASCADE, CascadeB=CASCADE, Rubble=QUARTZ_DARK,
             RubbleLight=QUARTZ, Front=SMOKED_DARK)
    rng = random.Random(seed)
    f = Frame(m, (0, 0, 0))
    outline(m, "Panel", f, oval(8.0, 11.0, 16, 0, -11.0), 1.55, 1.8)  # a sheet of the wall's glass, 1.5 out past the hanging rims
    outline(m, "Hole", f, oval(3.4, 4.6, 12, 0, -9.0), 1.8, 1.92)
    for k in range(10):  # teeth of glass round the hole
        a = k * math.tau / 10 + rng.uniform(-0.1, 0.1)
        base = (math.cos(a) * 3.9, -9.0 + math.sin(a) * 5.1)
        tip = (math.cos(a) * 2.6, -9.0 + math.sin(a) * 3.5)
        across = (-(tip[1] - base[1]), 0, tip[0] - base[0])
        plate(m, "Silvered" if k % 2 else "Tarnish", (base[0], 2.05, base[1]), (tip[0], 2.15, tip[1]), across, rng.uniform(1.0, 1.6), 0.08, 0.22)
    for k in range(8):  # cracks running out across the glass
        a = k * math.tau / 8 + rng.uniform(-0.2, 0.2)
        p = (math.cos(a) * 3.9, -9.0 + math.sin(a) * 5.0)
        length = rng.uniform(2.5, 4.5)
        q = (p[0] + math.cos(a) * length, p[1] + math.sin(a) * length)
        while (q[0] / 7.4) ** 2 + ((q[1] + 11.0) / 10.4) ** 2 > 1:
            q = ((q[0] + p[0]) / 2, (q[1] + p[1]) / 2)
        crack(m, "Fracture", p, q, 1.86, 0.16, 0.08)
    for role, x, y, top, size in (("Cascade", -0.9, 2.8, -7.0, 0.35), ("CascadeB", 0.8, 3.6, -9.0, 0.3)):
        z = top
        while z > -44:
            gem(m, role, x + 0.3 * math.sin(z * 1.7), y + 0.3 * math.cos(z * 1.3), z, size, size * 2.2, size * 1.6, 3, z)
            z -= 4.0
    heap = random.Random(seed + 1)
    for k in range(18):
        a = heap.uniform(0, math.pi)
        r = math.sqrt(heap.random()) * 5.0
        s = heap.uniform(0.5, 1.3)
        obox(m, ("Rubble", "RubbleLight", "Silvered")[k % 3], (math.cos(a) * r, 3.4 + math.sin(a) * r * 0.8, -44 + s * 0.25),
             (s, s * 0.8, s * 0.5), turn(heap.uniform(-0.4, 0.4), heap.uniform(-0.4, 0.4), heap.uniform(0, math.pi)))
    m.block("Front", 0, 6, -2, 0.2, 0.2, 0.2)
    return m


FRAME_TOP = 30.0  # the Great Frame's top bar; its crystals hang from here


def great_frame(seed=18):
    """Spans the corridor (modelled 72 wide, stretched to 88 in the game): a colossal gilt mirror frame standing on both
    rims, its glass gone but for jagged pieces clinging to the corners, crystals swinging from its top. The flight goes
    through one empty mirror after another."""
    m = prop("GreatFrame", Gilt=GILT, GiltDark=GILT_DARK, Silvered=SILVERED, Tarnish=TARNISH, Pendant=PRISM, PendantChain=GILT_DARK, Facet=FRACTURE,
             Front=GILT)
    rng = random.Random(seed)
    f = Frame(m, (0, 0, 0))
    for s in (-1, 1):
        m.block("GiltDark", s * 40.0, 0, 0.6, 4.4, 4.0, 1.2)
        m.block("Gilt", s * 40.0, 0, FRAME_TOP / 2 + 0.6, 2.6, 2.4, FRAME_TOP - 0.2)
        m.block("GiltDark", s * 38.4, 0, FRAME_TOP / 2 + 0.6, 0.6, 1.6, FRAME_TOP - 2.0)
        for z in (8.0, 16.0, 24.0):
            m.block("GiltDark", s * 40.0, 0, z, 3.0, 2.8, 0.7)
        ball(m, "Gilt", s * 40.0, 0, FRAME_TOP + 2.2, 1.4, 8, 5)
    m.block("Gilt", 0, 0, FRAME_TOP + 1.0, 82.6, 2.4, 2.4)
    m.block("GiltDark", 0, 0, FRAME_TOP - 0.45, 76.2, 1.6, 0.6)
    for x in (-24.0, -12.0, 12.0, 24.0):
        ball(m, "GiltDark", x, 0, FRAME_TOP + 2.3, 0.9, 8, 4)
    gem(m, "Gilt", 0, 0, FRAME_TOP + 4.0, 2.0, 3.6, 1.4, 4)
    gem(m, "Facet", 0, 1.1, FRAME_TOP + 3.0, 0.7, 1.1, 0.7, 4)
    for s in (-1, 1):  # what's left of the glass, clinging in the corners and along the sides
        x0 = s * 38.0
        outline(m, "Silvered", f, [(x0, FRAME_TOP - 0.8), (x0 - s * 9.5, FRAME_TOP - 0.8), (x0 - s * 6.5, FRAME_TOP - 8.5), (x0, FRAME_TOP - 12.0)][:: s], -0.2, 0.2)
        outline(m, "Tarnish", f, [(x0, 1.0), (x0 - s * 2.6, 1.0), (x0 - s * 1.2, 9.0), (x0, 13.0)][:: s], -0.2, 0.2)
    for x in (-27.0, -18.0, -9.0, 0.0, 9.0, 18.0, 27.0):  # crystals on chains, swinging together across the corridor
        drop = 3.0 + rng.uniform(0, 3.0) if x else 5.5
        beam(m, "PendantChain", (x, 0, FRAME_TOP - 0.7), (x, 0, FRAME_TOP - drop), 0.18)
        gem(m, "Pendant", x, 0, FRAME_TOP - drop - 0.6, 0.55, 0.6, 1.4, 4)
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


# ---------------------------------------------------------------------- the way in, the Glass Garden and the Ballroom
# (second pass, 2026-11-13: the owner wanted more props and the map "organized nicely" so it feels special. The world is
# now three acts: The Shattering (broken glass, scattered), The Glass Garden (fountains of light, butterflies, flowers, in
# mirrored pairs) and The Ballroom (music boxes, chandeliers, a mirror runway, every prop twinned across the corridor).)

THRESHOLD_CZ = 34.0  # the middle of the Threshold's rings of shards: they turn round it


def threshold(seed=19):
    """Spans the corridor at the very start of the world (modelled 72 wide, stretched to 88): the way in. A colossal gilt
    arch, the mirror it held just broken, its glass still hanging in the air inside it in two rings turning opposite ways
    round a point of light, so the flight comes out of The Weeping Dark's black straight through a shattering mirror."""
    m = prop("Threshold", Gilt=GILT, GiltDark=GILT_DARK, Shatter=SILVERED, ShatterB=PRISM, Facet=FRACTURE, Gleam=GLEAM, Front=GILT)
    rng = random.Random(seed)
    cz = THRESHOLD_CZ
    for s in (-1, 1):
        m.block("GiltDark", s * 40.0, 0, 1.0, 6.0, 5.0, 2.0)
        prism(m, "Gilt", s * 40.0, 0, 2.0, cz, 2.3, 2.0, 8, math.pi / 8)
        for z in (6.0, 14.0, 22.0, 30.0):
            prism(m, "GiltDark", s * 40.0, 0, z - 0.5, z + 0.5, 2.7, 2.7, 8, math.pi / 8)
        ball(m, "Gilt", s * 40.0, 0, cz + 0.6, 2.6, 8, 5)
    for rx, rz, role, depth, width in ((40.0, 24.0, "Gilt", 3.2, 3.0), (36.6, 21.0, "GiltDark", 2.0, 1.0)):  # the arch, half an oval
        arch = [(math.cos(math.pi * k / 20) * rx, cz + math.sin(math.pi * k / 20) * rz) for k in range(21)]
        for (x0, z0), (x1, z1) in zip(arch, arch[1:]):
            plate(m, role, (x0, 0, z0), (x1, 0, z1), FACING, depth, depth, width)
            m.block(role, x1, 0, z1, width * 0.95, depth * 0.97, width * 0.95)
    top = cz + 24.0
    gem(m, "Gilt", 0, 0, top + 2.6, 2.6, 4.6, 1.2, 4)
    for s in (-1, 1):
        ball(m, "Gilt", s * 5.0, 0, top + 0.6, 1.5, 8, 4)
        ball(m, "GiltDark", s * 9.5, 0, top - 0.6, 1.1, 8, 4)
    gem(m, "Gleam", 0, 1.7, top + 2.4, 0.9, 0.9, 0.9, 6)  # one cold eye in the crest
    shard = [(-0.5, -0.6), (0.55, -0.4), (0.2, 0.9), (-0.35, 0.5)]
    for role, count, (r0, r1), (s0, s1) in (("Shatter", 20, (19.0, 26.0), (3.0, 4.4)), ("ShatterB", 14, (8.5, 15.0), (1.8, 3.0))):
        for k in range(count // 2):  # in opposite pairs, so the ring's middle is the point it turns round
            a = k * math.tau / count + rng.uniform(-0.08, 0.08)
            r, s = rng.uniform(r0, r1), rng.uniform(s0, s1)
            rot = turn(rng.uniform(-0.5, 0.5), rng.uniform(0, math.pi), rng.uniform(-0.6, 0.6))
            dy = rng.uniform(-0.6, 0.6)
            for b in (a, a + math.pi):
                f = Frame(m, (math.cos(b) * r, dy, cz + math.sin(b) * r), rot)
                outline(m, role, f, [(x * s, z * s) for x, z in shard], -0.12, 0.12)
            dy = -dy
    sparkle(m, "Facet", 0, 0, cz, 3.2)
    gem(m, "Facet", 0, 0, cz, 0.9, 1.3, 1.3, 6)
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


def music_box(seed=20):
    """A chrome music box the size of a car, its lid thrown open on a mirror, and on top a porcelain ballerina turning and
    turning on one toe, arms over her head, her cold eyes on you each time she comes round. The key in its side turns,
    and notes of light rise off it."""
    m = prop("MusicBox", Chrome=CHROME, ChromeDark=CHROME_DARK, Gilt=GILT, GiltDark=GILT_DARK, BoxLid=CHROME, Silvered=SILVERED, Turntable=GILT,
             Dancer=PORCELAIN, Tutu="#f6d6e6", Gleam=GLEAM, WindKey=GILT, Note=FRACTURE)
    m.loft_z("ChromeDark", (0.0, 0, 0, 6.8, 5.0), (0.5, 0, 0, 6.8, 5.0))
    m.loft_z("Chrome", (0.5, 0, 0, 6.4, 4.6), (2.4, 0, 0, 6.4, 4.6))
    m.block("GiltDark", 0, 0, 1.45, 6.56, 4.76, 0.3)  # a band round its middle
    m.block("GiltDark", 0, 0, 2.48, 6.7, 4.9, 0.24)  # its lip
    for sx in (-1, 1):
        for sy in (-1, 1):
            ball(m, "Gilt", sx * 3.15, sy * 2.25, 0.3, 0.42, 8, 4)
    m.block("BoxLid", 0, -2.45, 4.7, 6.4, 0.35, 4.6)  # the lid, thrown right back, a mirror inside it
    m.block("Silvered", 0, -2.25, 4.75, 5.6, 0.1, 3.8)
    m.block("GiltDark", 0, -2.45, 7.08, 6.6, 0.5, 0.3)
    # The ballerina turns on the box's vertical middle: everything of hers is built round x = 0, y = 0.
    disc(m, "Turntable", 0, 0, 2.66, 1.0, 0.24, 12)
    limb(m, "Dancer", [(0, 0, 2.78), (0, 0.04, 3.8), (0.04, 0, 4.85)], 0.16, 0.36)  # on one toe
    limb(m, "Dancer", [(0.04, -0.05, 4.8), (0.08, -1.0, 5.0), (0.08, -1.95, 5.3)], 0.34, 0.13)  # the other leg out behind
    for k in range(12):
        a = k * math.tau / 12
        c, s = math.cos(a), math.sin(a)
        plate(m, "Tutu", (c * 0.3, s * 0.3, 4.86), (c * 1.55, s * 1.55, 5.08), (-s, c, 0), 0.4, 0.85, 0.08)
    m.loft_z("Dancer", (4.85, 0, 0, 0.72, 0.5), (5.9, 0, 0, 0.86, 0.48))
    for s in (-1, 1):
        limb(m, "Dancer", [(s * 0.42, 0, 5.82), (s * 0.78, 0.04, 6.6), (s * 0.24, 0.04, 7.34)], 0.17, 0.11)
    prism(m, "Dancer", 0, 0, 5.88, 6.16, 0.12, 0.11, 6)
    ball(m, "Dancer", 0, 0, 6.46, 0.34, 8, 5)
    ball(m, "Dancer", 0, -0.24, 6.74, 0.17, 6, 4)  # her bun
    for s in (-1, 1):
        m.block("Gleam", s * 0.12, 0.32, 6.5, 0.1, 0.05, 0.06)
    # The key turns round its own axle, along X: the two loops of its bow sit either side of it.
    beam(m, "WindKey", (3.2, 0, 1.4), (4.15, 0, 1.4), 0.3)
    for dz in (-0.55, 0.55):
        hoop(m, "WindKey", 4.35, 0, 1.4 + dz, 0.5, 0.16, "yz", 10)
    for x in (-2.1, 2.1):  # notes of light rising off it, spaced to loop
        for k in range(5):
            gem(m, "Note", x, 0.9, 3.2 + k * 1.6, 0.16, 0.34, 0.2, 4, k * 0.7)
    return m


FLY_Z = 7.0  # the line the butterflies' wings beat round


def mirror_butterflies(seed=21):
    """Three butterflies with wings of mirror, hovering over a cluster of crystal stems, beating their wings."""
    m = prop("MirrorButterflies", Chrome=CHROME, Quartz=QUARTZ, QuartzDark=QUARTZ_DARK, Facet=FRACTURE, FlapL=SILVERED, FlapR=SILVERED, Thorax=SMOKED_DARK,
             Rubble=QUARTZ_DARK)
    rng = random.Random(seed)
    rubble(m, ("Rubble",), 6, 1.6, 1.6, (0.3, 0.6), rng)
    for k, (x, y, h) in enumerate(((0.9, 0.5, 4.2), (-1.0, -0.4, 3.3), (0.3, -1.1, 2.5))):
        limb(m, "Chrome", [(x * 0.3, y * 0.3, 0), (x * 0.7, y, h * 0.5), (x, y, h)], 0.22, 0.12)
        gem(m, "QuartzDark" if k % 2 else "Quartz", x, y, h + 0.3, 0.32, 0.7, 0.3, 5)
        sparkle(m, "Facet", x, y, h + 1.2, 0.25)
    for y, size in ((-2.3, 1.15), (0.2, 1.45), (2.7, 1.0)):  # all on one line, x = 0 at FLY_Z, so their wings beat round it
        beam(m, "Thorax", (0, y - 0.6 * size, FLY_Z), (0, y + 0.6 * size, FLY_Z), 0.18 * size, 0.18 * size, 0.1 * size)
        ball(m, "Thorax", 0, y + 0.7 * size, FLY_Z, 0.16 * size, 6, 3)
        for s, role in ((-1, "FlapL"), (1, "FlapR")):
            plate(m, role, (s * 0.1, y + 0.15 * size, FLY_Z), (s * 1.8 * size, y + 0.7 * size, FLY_Z + 0.25 * size), (0, 1, 0), 0.55 * size, 1.25 * size, 0.06)
            plate(m, role, (s * 0.1, y - 0.2 * size, FLY_Z - 0.02), (s * 1.35 * size, y - 1.0 * size, FLY_Z - 0.1 * size), (0, 1, 0), 0.4 * size, 0.85 * size, 0.06)
    return m


def prism_fountain(seed=22):
    """A fountain of chrome tiers with a mirror for water and a crystal turning over its top, pouring light instead of
    water: drops of it fall in a ring from the upper bowl into the pool, where rings of rainbow shimmer."""
    m = prop("PrismFountain", Chrome=CHROME, ChromeDark=CHROME_DARK, Gilt=GILT, GiltDark=GILT_DARK, Silvered=SILVERED, Prism=QUARTZ, Spray="#dff6ff",
             SprayB="#ffe4f5", SpecB=SPEC["SpecB"], SpecD=SPEC["SpecD"], SpecE=SPEC["SpecE"])
    prism(m, "ChromeDark", 0, 0, 0, 0.3, 4.6, 4.6, 8, math.pi / 8)
    prism(m, "Chrome", 0, 0, 0.3, 1.0, 4.3, 4.2, 8, math.pi / 8)  # the basin's floor
    flat_ring(m, "Chrome", 0, 0, 0.85, 4.15, 0.45, 1.1, 16)  # its wall, a ring round the pool
    flat_ring(m, "GiltDark", 0, 0, 1.44, 4.15, 0.6, 0.12, 16)
    disc(m, "Silvered", 0, 0, 1.1, 3.95, 0.2, 16)  # the pool: a mirror
    for k, role in enumerate(("SpecB", "SpecD", "SpecE")):
        flat_ring(m, role, 0, 0, 1.27, 1.6 + k * 0.7, 0.14, 0.04, 20)
    prism(m, "Chrome", 0, 0, 1.2, 5.0, 0.55, 0.45, 8)
    prism(m, "Chrome", 0, 0, 5.0, 5.7, 0.5, 2.25, 8)  # the upper bowl
    flat_ring(m, "Gilt", 0, 0, 5.8, 2.25, 0.3, 0.14, 16)
    disc(m, "Silvered", 0, 0, 5.75, 1.95, 0.06, 16)
    prism(m, "Chrome", 0, 0, 5.6, 6.8, 0.25, 0.2, 8)
    gem(m, "Prism", 0, 0, 7.9, 0.7, 1.0, 1.0, 5)
    for k in range(8):  # light pouring over the bowl's rim, spaced to loop, two speeds turn about
        a = (k + 0.5) * math.tau / 8
        x, y = math.cos(a) * 2.2, math.sin(a) * 2.2
        for j in range(5):
            gem(m, "Spray" if k % 2 else "SprayB", x, y, 5.5 - j * 0.9, 0.11, 0.3, 0.2, 4, a)
    return m


PENDULUM_HOOK = 14.0  # the pendulum swings round the X line at this height


def pendulum_mirror(seed=23):
    """A round mirror on a long rod, swinging slowly between two gilt posts like a clock's pendulum. There are eyes in it,
    and they swing with it."""
    m = prop("PendulumMirror", Gilt=GILT, GiltDark=GILT_DARK, PendRod=CHROME, PendGlass=SILVERED, PendRim=GILT, Gleam=GLEAM, Facet=FRACTURE, Rubble=QUARTZ_DARK)
    rng = random.Random(seed)
    rubble(m, ("Rubble",), 8, 4.6, 2.4, (0.3, 0.7), rng)
    for s in (-1, 1):
        m.loft_z("GiltDark", (0, s * 4.2, 0, 1.7, 1.7), (1.0, s * 4.2, 0, 1.3, 1.3))
        prism(m, "Gilt", s * 4.2, 0, 1.0, PENDULUM_HOOK + 0.6, 0.5, 0.4, 8)
        ball(m, "Gilt", s * 4.2, 0, PENDULUM_HOOK + 1.2, 0.6, 8, 4)
    m.block("Gilt", 0, 0, PENDULUM_HOOK + 0.6, 8.8, 0.7, 0.7)
    gem(m, "Gilt", 0, 0, PENDULUM_HOOK + 1.6, 0.6, 1.4, 0.4, 4)
    sparkle(m, "Facet", 0, 0.6, PENDULUM_HOOK + 0.6, 0.4)
    beam(m, "PendRod", (0, 0, PENDULUM_HOOK), (0, 0, 6.7), 0.3)
    disc(m, "PendGlass", 0, 0, 4.0, 2.7, 0.3, 20, "xz")
    hoop(m, "PendRim", 0, 0, 4.0, 2.85, 0.45, "xz", 20)
    for y in (0.2, -0.2):
        for s in (-1, 1):
            m.block("Gleam", s * 0.45, y, 4.4, 0.32, 0.06, 0.13)
    return m


def glass_cathedral(seed=24):
    """A landmark for the Ballroom: a cathedral of smoked violet glass with a rose window of rainbow that breathes in and
    out, slits of light up its walls, twin spires with a prism turning over each, and a door of nothing."""
    m = prop("GlassCathedral", Smoked=SMOKED, SmokedDark=SMOKED_DARK, Chrome=CHROME, Gilt=GILT, GiltDark=GILT_DARK, Void=VOID, Facet=FRACTURE,
             PrismL=SILVERED, PrismR=PRISM, Rubble=QUARTZ_DARK, Front=SMOKED, **SPEC)
    rng = random.Random(seed)
    f = Frame(m, (0, 0, 0))
    rubble(m, ("Rubble",), 14, 13.0, 7.0, (0.6, 1.4), rng)
    m.loft_z("SmokedDark", (0, 0, 0, 24.0, 12.0), (3.0, 0, 0, 22.5, 11.0))
    m.block("Smoked", 0, 0, 11.5, 16.0, 9.0, 17.0)
    outline(m, "Smoked", f, [(-8.0, 20.0), (8.0, 20.0), (0.0, 28.0)], -4.5, 4.5)  # the gable
    for s in (-1, 1):
        plate(m, "GiltDark", (s * 8.4, 4.65, 19.8), (0, 4.65, 28.5), FACING, 0.5, 0.5, 0.7)
    # the rose window, on the front face
    hx, hy, hz, radius = 0.0, 4.55, 13.5, 4.6
    for k in range(10):
        a0, a1 = k * math.tau / 10, (k + 1) * math.tau / 10
        pts = [(hx + math.cos(a0 + 0.06) * 1.2, hz + math.sin(a0 + 0.06) * 1.2), (hx + math.cos(a0 + 0.05) * radius, hz + math.sin(a0 + 0.05) * radius),
               (hx + math.cos(a1 - 0.05) * radius, hz + math.sin(a1 - 0.05) * radius), (hx + math.cos(a1 - 0.06) * 1.2, hz + math.sin(a1 - 0.06) * 1.2)]
        outline(m, SPECTRUM[k % 5], f, pts, hy, hy + 0.2)
        f.beam("GiltDark", (hx + math.cos(a0) * 1.0, hy + 0.2, hz + math.sin(a0) * 1.0), (hx + math.cos(a0) * radius, hy + 0.2, hz + math.sin(a0) * radius), 0.3, 0.3)
    hoop(m, "Gilt", hx, hy + 0.2, hz, radius + 0.2, 0.6, "xz", 20)
    disc(m, "Gilt", hx, hy + 0.15, hz, 1.1, 0.5, 12, "xz")
    for s in (-1, 1):  # slits of light either side, and lancets on the sides
        m.block("Facet", s * 5.6, 4.55, 11.5, 0.8, 0.2, 9.0)
        gem(m, "Facet", s * 5.6, 4.55, 16.3, 0.45, 1.0, 0.1, 4)
        for y in (-2.5, 0.5, 3.0):
            m.block("Facet", s * 8.05, y, 12.5, 0.2, 0.8, 8.0)
    outline(m, "Void", f, [(-2.0, 3.0), (2.0, 3.0), (2.0, 7.5), (0.0, 9.5), (-2.0, 7.5)], 4.5, 4.62)  # the door
    for s in (-1, 1):
        m.block("Gilt", s * 2.25, 4.6, 5.5, 0.4, 0.3, 5.2)
    for s, role in ((-1, "PrismL"), (1, "PrismR")):  # the spires, each with its own prism turning over it
        x = s * 10.0
        prism(m, "Smoked", x, 0, 3.0, 26.0, 2.3, 1.5, 8, math.pi / 8)
        for z in (10.0, 18.0, 26.0):
            prism(m, "Chrome", x, 0, z - 0.4, z + 0.4, 2.5 - z * 0.035, 2.5 - z * 0.035, 8, math.pi / 8)
        prism(m, "SmokedDark", x, 0, 26.4, 33.0, 1.5, 0.05, 8, math.pi / 8)
        gem(m, role, x, 0, 36.0, 1.2, 1.9, 1.9, 4)
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


ISLE_Z = 95.0


def mirror_isles(seed=25):
    """A sky piece for the Glass Garden: three islands of chrome rock floating high above the island, shards of mirror
    standing on them, each rising and sinking at its own pace."""
    m = prop("MirrorIsles", IsleA=SILVERED, IsleB=PRISM, IsleC=CHROME)
    rng = random.Random(seed)
    for role, (x, y, z, r) in (("IsleA", (-18.0, 4.0, ISLE_Z, 9.0)), ("IsleB", (16.0, -10.0, ISLE_Z + 22.0, 7.0)), ("IsleC", (4.0, 18.0, ISLE_Z - 14.0, 5.5))):
        spin = rng.uniform(0, 1)
        prism(m, role, x, y, z - r * 1.7, z - r * 0.5, 0.5, r * 0.8, 7, spin)  # an upside-down cone of rock
        prism(m, role, x, y, z - r * 0.5, z, r * 0.8, r, 7, spin)
        for k in range(5):
            a, d = rng.uniform(0, math.tau), rng.uniform(0, r * 0.6)
            shard_slab(m, role, (x + math.cos(a) * d, y + math.sin(a) * d, z - 0.3), turn(rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0, math.pi)),
                       rng.uniform(1.4, 2.6), rng.uniform(3.0, 6.5), 0.35, rng)
    return m


NAIL_Z = -4.0  # the nail the crooked mirror swings on, below the wall's top edge


def wall_gallery(seed=26):
    """On the corridor walls of the Ballroom: oval mirrors hung on a sheet of the wall's glass. In the biggest a shape
    stands looking out, and the one at the top hangs crooked on its nail, swinging. Its origin is the wall's top inner
    edge (rim Z = 0, floor Z = -44), +Y out over the corridor; everything stays 1.5 out past the hanging rims."""
    m = prop("WallGallery", Panel=SMOKED, Gilt=GILT, GiltDark=GILT_DARK, Silvered=SILVERED, Swinger=SILVERED, SwingerFrame=GILT, Reflection=SMOKED_DARK,
             Gleam=GLEAM, Front=GILT)
    f = Frame(m, (0, 0, 0))
    outline(m, "Panel", f, oval(13.0, 12.0, 18, 0, -15.0), 1.5, 1.6)
    for x, z, rx, rz in ((-7.0, -17.0, 3.4, 4.6), (7.2, -18.5, 2.6, 3.4)):
        outline(m, "GiltDark", f, oval(rx + 0.5, rz + 0.5, 18, x, z), 1.6, 1.8)
        outline(m, "Silvered", f, oval(rx, rz, 18, x, z), 1.8, 1.95)
        band(m, "Gilt", oval(rx + 0.35, rz + 0.35, 18, x, z), 1.98, 0.42, 0.5)
    body = [(-8.6, -21.0), (-5.4, -21.0), (-5.6, -18.0), (-6.4, -17.4), (-7.6, -17.4), (-8.4, -18.0)]  # someone in the big one
    outline(m, "Reflection", f, body, 1.95, 1.99)
    outline(m, "Reflection", f, oval(0.62, 0.8, 12, -7.0, -16.4), 1.95, 1.99)
    for s in (-1, 1):
        m.block("Gleam", -7.0 + s * 0.24, 2.02, -16.35, 0.22, 0.06, 0.1)
    # The crooked one, hung straight below the origin so it swings round its nail.
    ball(m, "Gilt", 0, 1.9, NAIL_Z, 0.32, 8, 4)
    for s in (-1, 1):
        beam(m, "SwingerFrame", (0, 1.95, NAIL_Z), (s * 1.3, 1.95, NAIL_Z - 2.0), 0.12)
    outline(m, "SwingerFrame", f, oval(2.6, 3.2, 18, 0, NAIL_Z - 5.2), 1.7, 1.9)
    outline(m, "Swinger", f, oval(2.2, 2.8, 18, 0, NAIL_Z - 5.2), 1.9, 2.02)
    m.block("Front", 0, 6, -2, 0.2, 0.2, 0.2)
    return m


SPAN_Z = 28.0  # the bar the chandeliers hang from: they swing round it


def chandelier_span(seed=27):
    """Spans the Ballroom's corridor (modelled 72 wide, stretched to 88): a gilt bar from rim to rim with three great
    chandeliers hanging from it, candles lit, crystals trembling, all swinging gently together."""
    m = prop("ChandelierSpan", Gilt=GILT, GiltDark=GILT_DARK, SpanBar=GILT, Chand=GILT, ChandRod=GILT_DARK, ChandDrop=PRISM, ChandFlame=FLAME, Facet=FRACTURE,
             Front=GILT)
    rng = random.Random(seed)
    for s in (-1, 1):
        m.block("GiltDark", s * 40.0, 0, 0.6, 3.6, 3.6, 1.2)
        prism(m, "Gilt", s * 40.0, 0, 1.2, SPAN_Z + 1.5, 1.0, 0.8, 8)
        gem(m, "Gilt", s * 40.0, 0, SPAN_Z + 2.6, 1.0, 1.8, 0.5, 4)
    m.block("SpanBar", 0, 0, SPAN_Z + 0.5, 80.0, 0.8, 0.8)
    for x in (-27.0, -11.0, 11.0, 27.0):
        sparkle(m, "Facet", x, 0.6, SPAN_Z + 1.4, 0.5)
    k = 1.45  # how big each chandelier is
    for x in (-22.0, 0.0, 22.0):
        cz = SPAN_Z - 7.5 * k
        beam(m, "ChandRod", (x, 0, SPAN_Z), (x, 0, cz + 1.6 * k), 0.35 * k)
        prism(m, "ChandRod", x, 0, cz - 1.6 * k, cz + 1.6 * k, 0.55 * k, 0.45 * k, 8)
        gem(m, "Chand", x, 0, cz - 1.6 * k, 0.6 * k, 0.2 * k, 1.4 * k, 6)
        outer = [(x + math.cos(j * math.tau / 16) * 4.0 * k, math.sin(j * math.tau / 16) * 4.0 * k) for j in range(16)]
        inner = [(x + math.cos(j * math.tau / 8) * 2.2 * k, math.sin(j * math.tau / 8) * 2.2 * k) for j in range(8)]
        for (x0, y0), (x1, y1) in zip(outer, outer[1:] + outer[:1]):
            beam(m, "Chand", (x0, y0, cz), (x1, y1, cz), 0.4 * k, 0.4 * k)
        for (x0, y0), (x1, y1) in zip(inner, inner[1:] + inner[:1]):
            beam(m, "Chand", (x0, y0, cz + 1.4 * k), (x1, y1, cz + 1.4 * k), 0.3 * k, 0.3 * k)
        for j in range(8):
            ox, oy = outer[j * 2]
            beam(m, "Chand", (x, 0, cz + 0.4 * k), (ox, oy, cz), 0.25 * k, 0.25 * k)
            prism(m, "Chand", ox, oy, cz + 0.2 * k, cz + 0.55 * k, 0.28 * k, 0.32 * k, 6)
            gem(m, "ChandFlame", ox, oy, cz + 0.85 * k, 0.14 * k, 0.4 * k, 0.12 * k, 5)
        for j in range(16):
            ox, oy = outer[j]
            drop = rng.uniform(0.8, 1.4) * k
            beam(m, "ChandDrop", (ox, oy, cz - 0.2), (ox, oy, cz - drop), 0.07)
            gem(m, "ChandDrop", ox, oy, cz - drop - 0.25 * k, 0.2 * k, 0.25 * k, 0.5 * k, 4)
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


def ballroom_inlay(seed=28):
    """Flat, for the middle of the Ballroom's floor where eggs land: a long runway of mirror tiles in a gilt border, a star
    of light at its heart and diamonds of rainbow shimmering down its length."""
    m = prop("BallroomInlay", Silvered=SILVERED, Gilt=GILT, GiltDark=GILT_DARK, Facet=FRACTURE, Front=GILT, **SPEC)
    w, length = 12.0, 30.0
    m.block("Silvered", 0, 0, 0.1, w, length, 0.2)
    for s in (-1, 1):
        m.block("Gilt", s * (w / 2 + 0.4), 0, 0.15, 0.8, length + 1.6, 0.3)
        m.block("Gilt", 0, s * (length / 2 + 0.4), 0.15, w, 0.8, 0.3)
    step = 4.0
    for sign in (-1, 1):  # a lattice of gilt lines on the two diagonals, x = c + sign * y, cut to the runway
        for k in range(-12, 13):
            c = k * step
            lo, hi = (-w / 2 - c, w / 2 - c) if sign > 0 else (c - w / 2, c + w / 2)
            lo, hi = max(lo, -length / 2), min(hi, length / 2)
            if hi - lo < 0.3:
                continue
            plate(m, "GiltDark", (c + sign * lo, lo, 0.23), (c + sign * hi, hi, 0.23), (0, 0, 1), 0.06, 0.06, 0.12)
    for i, y in enumerate(range(-12, 13, 4)):  # diamonds of rainbow down its middle and sides
        for x in (-4.0, 0.0, 4.0) if i % 2 == 0 else (-2.0, 2.0):
            if abs(x) < 1e-6 and abs(y) < 3:
                continue
            obox(m, SPECTRUM[i % 5], (x, float(y), 0.27), (0.9, 0.9, 0.06), turn(0, 0, math.pi / 4))
    mk.star_prism(m, "Facet", (0, 0, 0.3), 2.2, 0.9, 0.08, (math.pi / 2, 0, 0), 8)
    m.block("Front", 0, 6, 0.1, 0.2, 0.2, 0.2)
    return m


ALL = [standing_mirror, shard_cluster, prism_obelisk, glass_gazer, kaleido_bloom, fallen_chandelier, split_statue, empty_frames, glass_tuft, shard_scatter,
       mirror_pool, glass_tree, mirror_maze, looking_glass, kaleido_tower, broken_moon, shardfall, great_frame,
       threshold, music_box, mirror_butterflies, prism_fountain, pendulum_mirror, glass_cathedral, mirror_isles, wall_gallery, chandelier_span, ballroom_inlay]

# ---------------------------------------------------------------------- motion (Config/PropMotion)

_BREATH = dict(bob=0.22, period=5.5)
_GAZE = dict(swing=38, period=11)
_LOOK = dict(swing=50, period=9, axis="ahead", height=GLASS_CZ)
_KALEIDO = dict(spin=-20, axis="ahead", about="self")
_TINKLE = dict(bob=0.1, period=1.7)
_CHIME = dict(swing=5, period=3.6, axis="across", height=FRAME_TOP)
_FLAME = dict(pulse=0.6, period=0.9)
_GLINT = dict(pulse=0.15, period=1.6)
_PIROUETTE = dict(spin=80)
_FLAP = dict(bob=0.3, period=0.8, axis="ahead", height=FLY_Z)
_PENDULUM = dict(swing=28, period=4.4, axis="across", height=PENDULUM_HOOK)
_CROOKED = dict(swing=9, period=3.4, axis="ahead", height=NAIL_Z)
_CHANDELIER = dict(swing=6, period=3.8, axis="across", height=SPAN_Z)
MOTION = {
    "prop_StandingMirror": {"Reflection": dict(_BREATH), "Gleam": dict(_BREATH, pulse=0.2), "Splinter": dict(spin=45, about="self"), "Fracture": dict(pulse=0.55, period=3.2)},
    "prop_ShardCluster": {"Splinter": dict(spin=30, about="self", bob=0.5, period=4.0), "Fracture": dict(pulse=0.5, period=2.8), "SpecA": dict(pulse=0.35, period=2.1),
                          "SpecC": dict(pulse=0.35, period=2.5), "SpecE": dict(pulse=0.35, period=2.9)},
    "prop_PrismObelisk": {"Prism": dict(spin=35, about="self", bob=0.35, period=3.4), "Facet": dict(pulse=0.4, period=2.4), **{role: dict(pulse=0.3, period=2.0 + k * 0.35)
                                                                                                                                for k, role in enumerate(SPECTRUM)}},
    "prop_GlassGazer": {"Visage": dict(_GAZE), "Silvered": dict(_GAZE), "Fracture": dict(_GAZE), "Gleam": dict(_GAZE, pulse=0.25)},
    "prop_KaleidoBloom": {"Silvered": dict(spin=22), "Gilt": dict(spin=22), "Facet": dict(spin=22, pulse=0.4, period=2.2)},
    "prop_FallenChandelier": {"Pendant": dict(_TINKLE), "FlameA": dict(_FLAME), "Facet": dict(_GLINT)},
    "prop_SplitStatue": {"PieceA": dict(bob=0.32, period=4.2), "PieceB": dict(bob=0.45, period=5.1), "Gleam": dict(bob=0.45, period=5.1, pulse=0.3),
                         "PieceC": dict(bob=0.45, period=3.7), "Facet": dict(_GLINT)},
    "prop_EmptyFrames": {"Gleam": dict(bob=0.3, period=4.6, pulse=0.05), "Floater": dict(spin=30, about="self", bob=0.4, period=3.2)},
    "prop_GlassTuft": {"Facet": dict(pulse=0.3, period=2.2)},
    "prop_ShardScatter": {"Facet": dict(pulse=0.1, period=1.3)},
    "prop_MirrorPool": {"Fracture": dict(pulse=0.5, period=3.0), **{role: dict(pulse=0.2, period=1.8 + k * 0.3) for k, role in enumerate(SPECTRUM)}},
    "prop_GlassTree": {"Silvered": dict(swing=2.5, period=6.0, axis="ahead", height=6.0), "Facet": dict(_GLINT)},
    "prop_MirrorMaze": {"Turner": dict(spin=24, about="self"), "TurnerFrame": dict(spin=24, about="self"), "Fracture": dict(pulse=0.5, period=3.4)},
    "prop_LookingGlass": {"Gleam": dict(_LOOK), "Void": dict(_LOOK), "Splinter": dict(spin=10), "Fracture": dict(pulse=0.55, period=4.0)},
    "prop_KaleidoTower": {"Wheel": dict(_KALEIDO), "Hub": dict(_KALEIDO), **{role: dict(_KALEIDO) for role in SPECTRUM}, "Facet": dict(pulse=0.4, period=3.0)},
    "prop_BrokenMoon": {"Splinter": dict(spin=5), "Tarnish": dict(spin=5), "Fracture": dict(pulse=0.5, period=5.0)},
    "prop_Shardfall": {"Cascade": dict(fall=4, period=0.9), "CascadeB": dict(fall=4, period=1.15), "Fracture": dict(pulse=0.5, period=2.6)},
    "prop_GreatFrame": {"Pendant": dict(_CHIME), "PendantChain": dict(_CHIME), "Facet": dict(pulse=0.4, period=2.6)},
    "prop_Threshold": {"Shatter": dict(spin=7, axis="ahead", about="self"), "ShatterB": dict(spin=-11, axis="ahead", about="self"), "Facet": dict(pulse=0.35, period=2.0),
                       "Gleam": dict(pulse=0.2, period=6.0)},
    "prop_MusicBox": {**{role: dict(_PIROUETTE) for role in ("Dancer", "Tutu", "Turntable")}, "Gleam": dict(_PIROUETTE), "WindKey": dict(spin=120, axis="across", about="self"),
                      "Note": dict(fall=-1.6, pulse=0.3, period=1.4)},
    "prop_MirrorButterflies": {"FlapL": dict(_FLAP, swing=36), "FlapR": dict(_FLAP, swing=-36), "Thorax": dict(bob=0.3, period=0.8), "Facet": dict(_GLINT)},
    "prop_PrismFountain": {"Spray": dict(fall=0.9, period=0.55), "SprayB": dict(fall=0.9, period=0.7), "Prism": dict(spin=40, about="self", bob=0.3, period=3.0),
                           "SpecB": dict(pulse=0.25, period=1.6), "SpecD": dict(pulse=0.25, period=1.9), "SpecE": dict(pulse=0.25, period=2.2)},
    "prop_PendulumMirror": {"PendRod": dict(_PENDULUM), "PendGlass": dict(_PENDULUM), "PendRim": dict(_PENDULUM), "Gleam": dict(_PENDULUM, pulse=0.3),
                            "Facet": dict(_GLINT)},
    "prop_GlassCathedral": {**{role: dict(pulse=0.45, period=3.0 + k * 0.4) for k, role in enumerate(SPECTRUM)}, "Facet": dict(pulse=0.4, period=2.6),
                            "PrismL": dict(spin=35, about="self", bob=0.6, period=3.6), "PrismR": dict(spin=-35, about="self", bob=0.6, period=4.2)},
    "prop_MirrorIsles": {"IsleA": dict(bob=3.0, period=9.0), "IsleB": dict(bob=3.5, period=11.0), "IsleC": dict(bob=2.5, period=7.5)},
    "prop_WallGallery": {"Swinger": dict(_CROOKED), "SwingerFrame": dict(_CROOKED), "Gleam": dict(pulse=0.1, period=5.0)},
    "prop_ChandelierSpan": {"Chand": dict(_CHANDELIER), "ChandRod": dict(_CHANDELIER), "ChandDrop": dict(_CHANDELIER), "ChandFlame": dict(_CHANDELIER, pulse=0.6),
                            "Facet": dict(_GLINT)},
    "prop_BallroomInlay": {**{role: dict(pulse=0.2, period=1.5 + k * 0.25) for k, role in enumerate(SPECTRUM)}, "Facet": dict(pulse=0.4, period=2.0)},
}

# No real light: a bright map, Neon and the sun are enough.
LIGHTS = {}

# Where the props go: the same rules as Config/Decor's ShatteredMirror (keep the two in step). The map is 1900 long, in
# three acts. You fly in through the Threshold. The Shattering (to 680): broken glass scattered anyhow, shards pouring
# down the walls, gilt frames across the corridor. The Glass Garden (680 to 1280): fountains of light, mirror butterflies
# and kaleidoscope flowers, every one twinned across the corridor (`pairs`), Kaleidoscope Towers either side at its gates,
# islands floating in the sky. The Ballroom (1280 to the end): music boxes, mannequins and statues in mirrored pairs on
# a runway of mirror inlays, chandeliers swinging overhead, mirrors hung on both walls, twin glass cathedrals, and at the
# very end two Looking Glasses facing each other across the corridor before the Last Door.
GARDEN, BALLROOM, END = 680, 1280, 1900
DECOR = dict(
    floor=dict(first=10, gap=(11, 18), side=(23, 34),
               props=[("prop_StandingMirror", 14, (1.3, 1.7)), ("prop_ShardCluster", 14, (1.2, 1.6)), ("prop_PrismObelisk", 8, (1.2, 1.5)), ("prop_GlassGazer", 6, (1.3, 1.6)),
                      ("prop_KaleidoBloom", 3, (1.2, 1.5)), ("prop_FallenChandelier", 3, (1.2, 1.5)), ("prop_SplitStatue", 3, (1.2, 1.5)), ("prop_EmptyFrames", 3, (1.2, 1.5))],
               extras=dict(chance=0.7, spread=8, props=[("prop_GlassTuft", 5, (0.9, 1.3)), ("prop_ShardScatter", 4, (1.0, 1.4))]),
               zones=[{"from": GARDEN, "to": BALLROOM, "pairs": True, "gap": (20, 28),
                       "props": [("prop_KaleidoBloom", 10, (1.2, 1.5)), ("prop_MirrorButterflies", 9, (1.2, 1.5)), ("prop_PrismFountain", 6, (1.2, 1.4)),
                                 ("prop_PrismObelisk", 4, (1.2, 1.4))]},
                      {"from": BALLROOM, "to": END, "pairs": True, "gap": (18, 26),
                       "props": [("prop_MusicBox", 8, (1.2, 1.4)), ("prop_GlassGazer", 7, (1.3, 1.5)), ("prop_SplitStatue", 6, (1.2, 1.4)), ("prop_StandingMirror", 6, (1.3, 1.6)),
                                 ("prop_FallenChandelier", 4, (1.2, 1.4)), ("prop_EmptyFrames", 3, (1.2, 1.4))]}]),
    rim=dict(first=6, gap=(10, 16), chance=0.9, side=(60, 104),
             props=[("prop_GlassTree", 6, (1.9, 2.5)), ("prop_ShardCluster", 6, (2.0, 2.6)), ("prop_StandingMirror", 3, (2.0, 2.5)), ("prop_MirrorMaze", 3, (1.6, 2.0)),
                    ("prop_PrismObelisk", 2, (1.8, 2.2)), ("prop_GlassTuft", 2, (2.2, 2.8))],
             zones=[{"from": GARDEN, "to": BALLROOM, "pairs": True, "gap": (14, 20),
                     "props": [("prop_GlassTree", 8, (1.9, 2.5)), ("prop_KaleidoBloom", 4, (2.0, 2.6)), ("prop_MirrorButterflies", 3, (2.0, 2.5)), ("prop_PrismFountain", 2, (1.8, 2.2))]},
                    {"from": BALLROOM, "to": END, "pairs": True, "gap": (14, 20),
                     "props": [("prop_PendulumMirror", 5, (1.5, 1.8)), ("prop_MirrorMaze", 4, (1.6, 2.0)), ("prop_StandingMirror", 4, (2.0, 2.5)), ("prop_GlassTree", 2, (1.9, 2.4))]}]),
    overhead=[("prop_Threshold", 14, 0, 1), ("prop_GreatFrame", 280, 0, 1), ("prop_GreatFrame", 560, 180, 1), ("prop_GreatFrame", 900, 0, 1), ("prop_GreatFrame", 1160, 180, 1)]
             + [("prop_ChandelierSpan", d, 0, 1) for d in (1340, 1460, 1580, 1700, 1820)],
    walls=[("prop_Shardfall", d, side) for d, side in ((100, 1), (290, -1), (480, 1), (670, -1), (860, 1), (1050, -1), (1240, 1))]
          + [("prop_WallGallery", d, side) for d in (1390, 1530, 1670, 1810) for side in (-1, 1)],
    spots=[("prop_LookingGlass", 130, -84, "rim", 0, 1.5, "middle"), ("prop_LookingGlass", 520, 84, "rim", 0, 1.5, "middle"),
           ("prop_LookingGlass", 1872, -84, "rim", 0, 1.6, "middle"), ("prop_LookingGlass", 1872, 84, "rim", 0, 1.6, "middle"),
           ("prop_KaleidoTower", 400, 86, "rim", 0, 1.4, "middle"), ("prop_KaleidoTower", 700, -86, "rim", 0, 1.5, "middle"), ("prop_KaleidoTower", 700, 86, "rim", 0, 1.5, "middle"),
           ("prop_KaleidoTower", 1262, -86, "rim", 0, 1.5, "middle"), ("prop_KaleidoTower", 1262, 86, "rim", 0, 1.5, "middle"),
           ("prop_GlassCathedral", 1600, -90, "rim", 0, 1.5, "middle"), ("prop_GlassCathedral", 1600, 90, "rim", 0, 1.5, "middle"),
           ("prop_BrokenMoon", 420, -230, "rim", 0, 2.4), ("prop_BrokenMoon", 1620, 230, "rim", 0, 2.6),
           ("prop_MirrorIsles", 800, 220, "rim", 0, 2.0), ("prop_MirrorIsles", 1000, -220, "rim", 0, 2.2), ("prop_MirrorIsles", 1190, 210, "rim", 0, 2.0)]
          + [("prop_MirrorPool", d, x, "floor", yaw, 1.3) for d, x, yaw in ((50, -3, 10), (175, 4, 350), (300, -4, 20), (425, 3, 340), (550, -2, 5), (675, 4, 15),
                                                                          (800, -3, 345), (925, 2, 10), (1050, -4, 355), (1175, 3, 25))]
          + [("prop_BallroomInlay", d, 0, "floor", 0, 1.0, "along") for d in range(1320, 1900, 60)],
)


# ---------------------------------------------------------------------- light and shine


def set_light(scene, sun_energy, ambient):
    sun = bpy.data.objects["Sun"]
    sun.data.energy = sun_energy
    sun.data.color = (1.0, 0.9, 0.92)
    sun.rotation_euler = (math.radians(-55), math.radians(30), math.radians(40))
    node = scene.world.node_tree.nodes["Background"]
    node.inputs["Color"].default_value = (0.95, 0.86, 0.92, 1)
    node.inputs["Strength"].default_value = ambient


def show_light(scene):
    set_light(scene, 3.0, 0.75)


def game_light(scene):
    """As near as Blender gets to Config/Lighting ShatteredMirror: a bright pearl-pink dawn."""
    set_light(scene, 3.4, 0.85)


TEXTURES = HERE.parent / "textures"
PREVIEW_MAPS = {"HoloChrome": ("chrome_color.png", 18, 0.1), "PolishedGold": ("gold_color.png", 10, 0.18)}  # map, studs per tile, roughness
REFLECTED = ((0.0, "#4a4660"), (0.46, "#bdb6cc"), (0.5, "#ffffff"), (0.56, "#f6dbe7"), (1.0, "#e9b9d2"))  # ground, horizon, dawn sky


def shine(roots, on=True):
    """The chrome and gold in the renders, as near as Blender gets to the game's MaterialVariants (METAL): fully metal,
    smooth, coloured by the same maps (assets/textures/make_chrome.py) tinted by the part's colour. Metal shows what it
    reflects, so while it's on the light the world gives (its "Background", not what the camera sees) is a dawn sky like
    the game's: lilac ground, a white horizon, pink above. Off again before saving, so the export stays plain colours."""
    world = bpy.context.scene.world.node_tree
    background = world.nodes["Background"]
    for link in list(background.inputs["Color"].links):
        world.links.remove(link)
    if on:
        coord = world.nodes.get("ReflCoord") or world.nodes.new("ShaderNodeTexCoord")
        coord.name = "ReflCoord"
        split = world.nodes.get("ReflSplit") or world.nodes.new("ShaderNodeSeparateXYZ")
        split.name = "ReflSplit"
        span = world.nodes.get("ReflSpan") or world.nodes.new("ShaderNodeMapRange")
        span.name = "ReflSpan"
        span.inputs["From Min"].default_value = -1.0
        ramp = world.nodes.get("ReflRamp")
        if ramp is None:
            ramp = world.nodes.new("ShaderNodeValToRGB")
            ramp.name = "ReflRamp"
            stops = ramp.color_ramp.elements
            while len(stops) < len(REFLECTED):
                stops.new(0.5)
            for stop, (at, colour) in zip(stops, REFLECTED):
                stop.position = at
                stop.color = (*kit.srgb_to_linear(colour), 1)
        world.links.new(coord.outputs["Generated"], split.inputs[0])
        world.links.new(split.outputs["Z"], span.inputs["Value"])
        world.links.new(span.outputs["Result"], ramp.inputs["Fac"])
        world.links.new(ramp.outputs["Color"], background.inputs["Color"])
    for root in roots:
        for child in root.children:
            variant = METAL.get(mk.role_of(child)) if child.type == "MESH" else None
            if not variant:
                continue
            image, studs, rough = PREVIEW_MAPS[variant]
            for mat in child.data.materials:
                nodes, links = mat.node_tree.nodes, mat.node_tree.links
                bsdf, rgb = nodes["Principled BSDF"], nodes["Colour"]
                for link in list(bsdf.inputs["Base Color"].links):
                    links.remove(link)
                bsdf.inputs["Metallic"].default_value = 1.0 if on else 0.0
                bsdf.inputs["Roughness"].default_value = rough if on else 0.65
                if not on:
                    links.new(rgb.outputs[0], bsdf.inputs["Base Color"])
                    continue
                tex = nodes.get("MetalMap") or nodes.new("ShaderNodeTexImage")
                tex.name = "MetalMap"
                tex.image = bpy.data.images.load(str(TEXTURES / image), check_existing=True)
                tex.projection = "BOX"
                tex.projection_blend = 0.3
                coord = nodes.get("MetalCoord") or nodes.new("ShaderNodeTexCoord")
                coord.name = "MetalCoord"
                scale = nodes.get("MetalScale") or nodes.new("ShaderNodeMapping")
                scale.name = "MetalScale"
                scale.inputs["Scale"].default_value = (1 / studs,) * 3
                tint = nodes.get("MetalTint") or nodes.new("ShaderNodeMixRGB")
                tint.name = "MetalTint"
                tint.blend_type = "MULTIPLY"
                tint.inputs[0].default_value = 1
                links.new(coord.outputs["Object"], scale.inputs["Vector"])
                links.new(scale.outputs["Vector"], tex.inputs["Vector"])
                links.new(rgb.outputs[0], tint.inputs[1])
                links.new(tex.outputs["Color"], tint.inputs[2])
                links.new(tint.outputs[0], bsdf.inputs["Base Color"])


# ---------------------------------------------------------------------- scene and renders

BIG = {"prop_LookingGlass": (-110, -150, 0), "prop_KaleidoTower": (-60, -140, 0), "prop_MirrorMaze": (-20, -120, 0), "prop_GlassTree": (16, -118, 0),
       "prop_BrokenMoon": (100, -500, -60), "prop_Shardfall": (140, -110, 44), "prop_GreatFrame": (240, -170, 0), "prop_GlassCathedral": (-175, -150, 0),
       "prop_PendulumMirror": (50, -120, 0), "prop_WallGallery": (190, -110, 44), "prop_Threshold": (360, -200, 0), "prop_ChandelierSpan": (480, -170, 0),
       "prop_MirrorIsles": (300, -700, -60)}


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
    shine(roots)

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
            if name == "prop_GlassCathedral":
                c = Vector(root.location) + Vector((0, 0, 17))
                mk.set_visible(everything, [root])
                kit.shoot(scene, name, c + Vector((30, 82, 2)), c, (800, 900), 40)
            elif name == "prop_MirrorIsles":
                mk.set_visible(everything, [root])
                c = Vector(root.location) + Vector((0, 0, ISLE_Z))
                kit.shoot(scene, name, c + Vector((50, 130, -10)), c, (900, 900), 40)
            elif name == "prop_LookingGlass":
                c = Vector(root.location) + Vector((0, 0, 16))
                mk.set_visible(everything, [root])
                kit.shoot(scene, name, c + Vector((22, 66, 6)), c, (800, 900), 40)
            elif name == "prop_KaleidoTower":
                c = Vector(root.location) + Vector((0, 0, 18))
                mk.set_visible(everything, [root])
                kit.shoot(scene, name, c + Vector((26, 70, 4)), c, (800, 900), 40)
            elif name in ("prop_GreatFrame", "prop_Threshold", "prop_ChandelierSpan"):
                mk.shoot_prop(scene, name, root, player, everything, (0.1, 1.0, 0.1), 0.9, (1400, 700), 32)
            elif name in ("prop_Shardfall", "prop_WallGallery"):
                mk.shoot_prop(scene, name, root, player, everything, (0.3, 1.0, 0.0), 1.0, (800, 900), 40)
            elif name == "prop_BrokenMoon":
                mk.set_visible(everything, [root])
                c = Vector(root.location) + Vector((0, 0, MOON_Z))
                kit.shoot(scene, name, c + Vector((40, 120, -20)), c, (900, 900), 40)
            elif name in ("prop_MirrorPool", "prop_BallroomInlay"):
                mk.shoot_prop(scene, name, root, player, everything, (0.05, 0.25, 1.0), 1.1, (700, 700), 50)
            elif name in ("prop_MirrorMaze", "prop_GlassTree", "prop_PendulumMirror"):
                mk.shoot_prop(scene, name, root, player, everything, (0.5, 0.95, 0.3), 1.1, (800, 800), 50)
            else:
                mk.shoot_prop(scene, name, root, player, everything)
        if not only:
            player.location = (30, -40, 0)
            bpy.context.view_layer.update()
            small = [r for r in roots if mk.prop_of(r) not in BIG]
            mk.set_visible(everything, small + [player])
            kit.shoot(scene, "props", (row_middle, 50, 34), (row_middle, -40, 5), (2000, 700), 18)
            landmarks = [built[n] for n in ("prop_GlassCathedral", "prop_LookingGlass", "prop_KaleidoTower", "prop_MirrorMaze", "prop_GlassTree", "prop_PendulumMirror")]
            mk.set_visible(everything, landmarks + [player])
            player.location = (-30, -96, 0)
            bpy.context.view_layer.update()
            kit.shoot(scene, "landmarks", (-70, -8, 48), (-70, -135, 18), (1800, 800), 20)

    if videos:  # close up on what moves
        names = ("prop_StandingMirror", "prop_MusicBox", "prop_MirrorButterflies", "prop_PrismFountain", "prop_GlassGazer", "prop_KaleidoBloom", "prop_SplitStatue",
                 "prop_ShardCluster", "prop_LookingGlass", "prop_KaleidoTower", "prop_PendulumMirror", "prop_GlassCathedral")
        movers = [built[n] for n in names]
        mk.set_visible(everything, movers)
        saved = [(r, r.location.copy()) for r in movers]
        for k, root in enumerate(movers[:8]):
            root.location = (k * 14 - 49, 0, 0)
        for k, root in enumerate(movers[8:]):
            root.location = ((k - 1.5) * 40, -60, 0)
        bpy.context.view_layer.update()
        entries = mk.motion_entries(movers, MOTION)
        mk.render_video(scene, RENDERS, "mirror_motion", 150, 15, lambda f: ((0, 70, 34), (0, -22, 12), 26, lambda t: mk.apply_motion(entries, t)), (1600, 800))
        mk.reset_motion(entries)
        for root, loc in saved:
            root.location = loc

    if only:
        return
    ground.hide_render = True
    mk.set_visible(everything, [])
    corridor = mk.corridor_stage(stage, CORRIDOR, length=END)
    copies = mk.decorate_stage(stage, built, DECOR, length=END)
    game_light(scene)
    if stills:
        kit.shoot(scene, "corridor_flight", (0, 30, 30), (0, -160, 16), (1600, 900), 22)
        kit.shoot(scene, "corridor_high", (0, 40, 80), (0, -170, 30), (1600, 900), 22)
        kit.shoot(scene, "corridor_floor", (-16, -50, 10), (8, -170, 12), (1600, 900), 22)
        kit.shoot(scene, "corridor_rim", (-40, 20, 90), (50, -160, 54), (1600, 900), 24)
        kit.shoot(scene, "moon_over_the_wall", (30, -340, 14), (-190, -420, 200), (1600, 900), 22)
        kit.shoot(scene, "garden_flight", (0, -640, 30), (0, -830, 16), (1600, 900), 22)
        kit.shoot(scene, "garden_isles", (-20, -760, 20), (150, -900, 150), (1600, 900), 22)
        kit.shoot(scene, "ballroom_flight", (0, -1290, 30), (0, -1480, 16), (1600, 900), 22)
        kit.shoot(scene, "ballroom_high", (0, -1270, 90), (0, -1520, 30), (1600, 900), 22)
        kit.shoot(scene, "ballroom_floor", (-14, -1480, 9), (6, -1620, 12), (1600, 900), 22)
        kit.shoot(scene, "the_end", (0, -1700, 30), (0, -1900, 30), (1600, 900), 22)
    if videos:  # down the corridor at the flight camera's height (14 over an egg that flies up to 18 high)
        entries = mk.motion_entries(copies, MOTION)
        frames = 165

        def fly(f):
            t = f / (frames - 1)
            y = 30 - 400 * t
            return (0, y, 28 + 4 * math.sin(t * math.pi)), (0, y - 70, 17), 22, lambda s: mk.apply_motion(entries, s)

        mk.render_video(scene, RENDERS, "mirror_flight", frames, 15, fly, (1600, 900))
        mk.reset_motion(entries)

    mk.clear(copies + [corridor])
    mk.light_up(roots, GLOW_ROLES, 0)
    shine(roots, False)
    ground.hide_render = False
    for root in roots:
        for child in root.children:
            child.hide_render = False
    player.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "shattered_mirror_models.blend"))
    print("saved", HERE / "shattered_mirror_models.blend")
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
