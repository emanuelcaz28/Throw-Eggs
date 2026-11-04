"""Builds Eclipse Temple's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_eclipse_temple.py              (stills and videos)
    Blender -b -P build_eclipse_temple.py -- stills    (stills only, quicker while modelling)

Saves eclipse_temple_models.blend and renders to design/world/models_eclipse_temple/: one still per prop, the
props together, a stretch of corridor, and two videos of what moves (eclipse_motion.mp4 close up,
eclipse_flight.mp4 down the corridor at the flight camera's height).

Eclipse Temple, map 9, opens the run of mysterious, dark maps the owner asked for after Starfall Crater: a lost
temple city swallowed by the jungle, frozen under a total eclipse. Red laterite flagstones on the floor, dark
carved walls with jungle hanging over them, grey-green temple stone, old gold and bronze, and one light of its
own: glowing jade, in the statues' eyes, the runes and the spirit fire. Warm and dark after Starfall's cold blue
night, so it reads at a glance. Its signature is the guardian head, a carved stone face half sunk in the floor
whose eyes glow. Landmarks: stepped temples with jade glyphs circling a floating orb over them, guardian
statues whose heads slowly turn to watch you pass, black eclipsed suns in the sky with their corona turning,
carved faces in the walls pouring spirit water down into the corridor, and temple gates across it with a
bronze bell and lanterns swinging under them.

What moves is MOTION below, the same numbers as shared/Config/PropMotion.luau (keep the two in step). This map
adds two kinds of move to the game: swing (rocks back and forth) and turning round a sideways axis.
Glowing roles (GLOW_ROLES) must also be in shared/Roles.luau, which makes them Neon in the game.
Props that must face a certain way carry a small Front part on their +Y side; MapDecor turns them, then removes it.
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
from map_kit import ball, beam, disc, flat_ring, gem, hanging_vine, hoop, kit, limb, plate, prism, puddle  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "models_eclipse_temple"

# Roles lit from inside. The game makes them Neon (shared/Roles.luau), so add new ones there too.
GLOW_ROLES = {"Jade", "Gaze", "Pod", "Lamp", "Flame", "FlameCore", "Ember", "Iris", "Orb", "Sigil", "RuneInner", "RuneOuter",
              "Glyph", "RuneA", "RuneB", "RuneC", "LampA", "LampB", "LampC", "Corona", "EclipseRing", "Stream", "Falling",
              "BellGlow"}
kit.NO_STUDS.update(GLOW_ROLES)
mk.GLOW_STRENGTH = 1.7  # stronger clips the jade to cyan in the renders

# Shared colours, so every prop's stone, plants and light match.
STONE, STONE_DARK, STONE_LIGHT = "#9c9d86", "#6e705e", "#c4c3a7"
SOCKET = "#1f1a20"
MOSS, MOSS_DARK = "#5aa04e", "#36703b"
VINE, LEAF, LEAF_DARK, LEAF_LIGHT = "#3f8c46", "#2f7a45", "#215c35", "#58a85a"
BARK, BARK_DARK = "#5e4636", "#46342a"
GOLD, GOLD_DARK = "#f0b93a", "#b8801f"
BRONZE, BRONZE_DARK, PATINA = "#b5743c", "#7c4a28", "#5fb79a"
LATERITE, LATERITE_DARK = "#8a4a44", "#6a3734"
JADE = "#47ff9c"
LAMP = "#ffcf6a"
POD = "#b9ff5c"

# The corridor's Eclipse Temple colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#804642", "FloorB": "#723d3a", "Dirt": "#4a2e3a", "DirtB": "#402733", "Grass": "#3a804a"}
SKY = "#1b2b2e"

# What moves. The game reads the same numbers from shared/Config/PropMotion.luau. Kinds of move:
#   spin  degrees a second; swing  degrees each way, over period seconds; bob  studs up and down over period;
#   pulse  the glow dims to this share and back over period; fall  drops this far over period, then starts again
#   (negative rises); drift  the whole prop glides head first.
# spin and swing turn round axis "up" (default), "across" (the model's X) or "ahead" (its Y), through the part's
# own middle (about="self") or a point `height` studs straight above the prop's origin (the default).
MOTION = {
    "prop_GuardianHead": {"Gaze": dict(pulse=0.35, period=3.4)},
    "prop_JungleFronds": {"Pod": dict(pulse=0.45, period=2.6)},
    "prop_JungleTree": {"Pod": dict(pulse=0.45, period=2.9)},
    "prop_HangingLantern": {"Lantern": dict(swing=12, period=2.6, axis="across", height=7.8),
                            "Lamp": dict(swing=12, period=2.6, axis="across", height=7.8)},
    "prop_SpiritBrazier": {"Flame": dict(pulse=0.55, period=0.7, bob=0.12),
                           "FlameCore": dict(pulse=0.6, period=0.45),
                           "Ember": dict(fall=-2, period=1.3)},
    "prop_WatcherBloom": {role: dict(swing=50, period=7) for role in ("EyeBall", "Iris", "Pupil", "Lid")},
    "prop_Orrery": {"Orb": dict(pulse=0.6, period=4, bob=0.3),
                    "RingA": dict(spin=35, height=8.3, bob=0.3, period=4),
                    "Planets": dict(spin=35, height=8.3, bob=0.3, period=4),
                    "RingB": dict(spin=-50, height=8.3, bob=0.3, period=4),
                    "RingC": dict(spin=22, axis="across", height=8.3, bob=0.3, period=4)},
    "prop_StoneHand": {"Orb": dict(pulse=0.5, bob=0.35, period=3.6)},
    "prop_RuneCircle": {"RuneOuter": dict(spin=-8), "RuneInner": dict(spin=14), "Sigil": dict(pulse=0.4, period=3)},
    "prop_StepTemple": {"Orb": dict(pulse=0.5, bob=0.8, period=5), "Glyph": dict(spin=20, bob=0.8, period=5),
                        "Jade": dict(pulse=0.6, period=4)},
    "prop_GuardianStatue": {"StatueHead": dict(swing=40, period=9), "Mask": dict(swing=40, period=9),
                            "Gaze": dict(swing=40, period=9, pulse=0.4)},
    "prop_FloatingMonoliths": {"MonolithA": dict(spin=10, bob=0.7, period=4.4), "RuneA": dict(spin=10, bob=0.7, period=4.4),
                               "MonolithB": dict(spin=10, bob=0.9, period=5.2), "RuneB": dict(spin=10, bob=0.9, period=5.2),
                               "MonolithC": dict(spin=10, bob=0.6, period=3.8), "RuneC": dict(spin=10, bob=0.6, period=3.8),
                               "Jade": dict(pulse=0.5, period=3)},
    "prop_SkyLanterns": {"LampA": dict(spin=6, bob=1.0, period=5), "CapA": dict(spin=6, bob=1.0, period=5),
                         "LampB": dict(spin=6, bob=1.3, period=6.2), "CapB": dict(spin=6, bob=1.3, period=6.2),
                         "LampC": dict(spin=6, bob=0.8, period=4.4), "CapC": dict(spin=6, bob=0.8, period=4.4)},
    "prop_Eclipse": {"Corona": dict(spin=5, axis="ahead", about="self"), "EclipseRing": dict(pulse=0.6, period=5)},
    "prop_FaceFall": {"Gaze": dict(pulse=0.4, period=3.5), "Falling": dict(fall=4, period=0.8)},
    "prop_TempleGate": {"Bell": dict(swing=6, period=4.2, axis="across", height=30.6),
                        "BellRim": dict(swing=6, period=4.2, axis="across", height=30.6),
                        "BellGlow": dict(swing=6, period=4.2, axis="across", height=30.6, pulse=0.6),
                        "Lantern": dict(swing=12, period=2.8, axis="across", height=30.6),
                        "Lamp": dict(swing=12, period=2.8, axis="across", height=30.6),
                        "Jade": dict(pulse=0.6, period=4)},
}


def prop(name, **colours):
    return mk.prop(name, **colours)


# ---------------------------------------------------------------------- shape helpers


def rubble(m, rng, cx, cy, radius, count, roles=("Stone", "StoneDark", "StoneLight"), size=(0.5, 1.2), z=0.0, inner=0.5):
    """Broken stones scattered round a point."""
    for i in range(count):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(radius * inner, radius)
        s = rng.uniform(*size)
        m.block(roles[i % len(roles)], cx + math.cos(a) * r, cy + math.sin(a) * r, z + s * 0.35, s, s * rng.uniform(0.7, 1.3), s * 0.7)


def moss_on(m, rng, x, y, z, w, d, drips=2, role="Moss"):
    """A cap of moss on a top face at height z, with a few drips down its sides."""
    m.block(role, x, y, z + 0.08, w * 0.9, d * 0.9, 0.18)
    for _ in range(drips):
        side = rng.choice((0, 1, 2, 3))
        length = rng.uniform(0.4, 1.2)
        if side < 2:
            px, py = x + rng.uniform(-w, w) * 0.35, y + (d / 2 if side == 0 else -d / 2) * 0.98
            m.block(role, px, py, z - length / 2, rng.uniform(0.4, 0.9), 0.14, length)
        else:
            px, py = x + (w / 2 if side == 2 else -w / 2) * 0.98, y + rng.uniform(-d, d) * 0.35
            m.block(role, px, py, z - length / 2, 0.14, rng.uniform(0.4, 0.9), length)


def big_leaf(m, role, base, angle, length, width, lift=0.8, droop=0.7, rib=None):
    """An elephant-ear leaf from base towards angle: rising, then drooping at its tip."""
    bx, by, bz = base
    mid = (bx + math.cos(angle) * length * 0.55, by + math.sin(angle) * length * 0.55, bz + lift)
    tip = (bx + math.cos(angle) * length, by + math.sin(angle) * length, bz + lift - droop)
    beam(m, role, base, mid, width * 0.45, 0.14, width)
    beam(m, role, mid, tip, width, 0.2, width * 0.2)
    if rib:
        beam(m, rib, (bx, by, bz + 0.12), (mid[0], mid[1], mid[2] + 0.12), 0.14, 0.1)
        beam(m, rib, (mid[0], mid[1], mid[2] + 0.12), (tip[0], tip[1], tip[2] + 0.06), 0.14, 0.1, 0.05)


def stone_face(m, front_y, cx, cz, w, h, eye_role="Gaze", stone="Stone", light="StoneLight", dark="StoneDark", socket="Socket",
               open_mouth=False, facing=1):
    """A carved temple face on a flat front at y = front_y, centred on (cx, cz), w wide and h tall, looking
    towards +Y (facing=1) or -Y (facing=-1): a heavy straight brow (calm and stern, never angry), deep sockets
    with a glowing slit of an eye, a broad nose and thick lips, closed or open wide."""
    def at(out):  # y, `out` studs in front of the face
        return front_y + facing * out

    m.block(light, cx, at(0.3), cz + h * 0.2, w * 0.92, 0.6, h * 0.1)  # brow
    for side in (-1, 1):
        ex = cx + side * w * 0.22
        m.block(socket, ex, at(0.04), cz + h * 0.06, w * 0.26, 0.1, h * 0.14)
        m.block(eye_role, ex, at(0.1), cz + h * 0.05, w * 0.19, 0.08, h * 0.045)
        m.block(light, cx + side * w * 0.31, at(0.15), cz - h * 0.12, w * 0.16, 0.3, h * 0.14)  # cheeks
    m.loft_y(light, (at(0), cx, cz - h * 0.08, w * 0.17, h * 0.24), (at(w * 0.12), cx, cz - h * 0.14, w * 0.2, h * 0.13))  # nose
    if open_mouth:
        m.block(socket, cx, at(0.04), cz - h * 0.33, w * 0.42, 0.1, h * 0.14)
        m.block(dark, cx, at(0.35), cz - h * 0.25, w * 0.48, 0.7, h * 0.04)
        m.block(dark, cx, at(0.35), cz - h * 0.41, w * 0.44, 0.7, h * 0.04)
    else:
        m.block(dark, cx, at(0.2), cz - h * 0.27, w * 0.44, 0.4, h * 0.05)
        m.block(socket, cx, at(0.12), cz - h * 0.305, w * 0.38, 0.1, h * 0.025)
        m.block(dark, cx, at(0.18), cz - h * 0.34, w * 0.36, 0.36, h * 0.045)


# ---------------------------------------------------------------------- floor props


def guardian_head(seed=1):
    """The map's signature: the head of a giant temple guardian, half sunk in the floor among its rubble, still
    crowned, moss on its headdress and vines down its cheeks. Its eyes glow jade, slowly brightening and dimming."""
    m = prop("GuardianHead", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Socket=SOCKET, Gaze=JADE, Gold=GOLD,
             GoldDark=GOLD_DARK, Jade=JADE, Moss=MOSS, MossDark=MOSS_DARK, Vine=VINE, Leaf=LEAF, Soil=LATERITE_DARK)
    rng = random.Random(seed)
    puddle(m, "Soil", ((0, 0.5, 9, 8), (1.5, -1.5, 6, 5)), z=0.08, thick=0.16)
    m.loft_z("StoneDark", (0, 0, 0, 6.6, 5.6), (1.0, 0, 0, 6.1, 5.1))
    m.block("Stone", 0, 0, 4.2, 6.0, 5.0, 6.4)
    stone_face(m, 2.5, 0, 4.4, 6.0, 6.0)
    for side in (-1, 1):  # ears with gold plugs, and side flaps of the headdress
        m.block("Stone", side * 3.2, 0.3, 4.3, 0.5, 1.4, 2.6)
        m.block("Gold", side * 3.5, 0.3, 4.0, 0.3, 1.0, 1.0)
        m.block("GoldDark", side * 3.6, 0.3, 4.0, 0.1, 0.5, 0.5)
        m.block("StoneDark", side * 2.9, -0.4, 6.4, 0.6, 4.2, 1.8)
    m.block("Gold", 0, 0, 7.6, 6.4, 5.4, 0.5)
    for x in (-2.2, -1.1, 0, 1.1, 2.2):
        m.block("GoldDark", x, 2.72, 7.6, 0.5, 0.06, 0.3)
    gem(m, "Jade", 0, 2.8, 7.62, 0.45, 0.55, 0.55, 4, math.pi / 4)
    m.block("Stone", 0, -0.2, 8.4, 5.6, 4.6, 1.1)
    m.block("StoneLight", 0, -0.3, 9.3, 4.4, 3.6, 0.8)
    m.block("Stone", 0, -0.4, 10.0, 3.0, 2.6, 0.7)
    m.block("StoneLight", 0, 1.9, 9.4, 2.4, 0.6, 2.6)  # crest over the brow
    m.block("Gold", 0, 2.25, 10.0, 1.0, 0.2, 1.0)
    moss_on(m, rng, 0, -0.4, 10.35, 3.0, 2.6, 3)
    moss_on(m, rng, -1.4, -0.6, 9.7, 1.8, 2.4, 2)
    moss_on(m, rng, 1.6, 0.2, 8.95, 2.0, 2.2, 2, "MossDark")
    beam(m, "StoneDark", (1.6, 2.53, 6.0), (2.2, 2.53, 4.4), 0.12, 0.06)  # a crack down the forehead
    beam(m, "StoneDark", (2.2, 2.53, 4.4), (1.9, 2.53, 3.2), 0.12, 0.06)
    for x, y, top, length in ((2.9, 2.0, 7.4, 4.0), (-3.0, 1.6, 7.4, 3.2), (-2.4, -2.6, 8.0, 5.0), (1.8, -2.6, 8.2, 3.6)):
        hanging_vine(m, "Vine", x, y, top, length, 0.3, rng, "Leaf")
    rubble(m, rng, 0, 0, 5.4, 12, inner=0.75)
    return m


def temple_ruin(seed=2):
    """What's left of a temple porch: a stepped platform, two broken columns (one with jade glyphs down it),
    drums of a fallen column, a slab leaning on them, moss and roots over everything."""
    m = prop("TempleRuin", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Jade=JADE, Moss=MOSS, MossDark=MOSS_DARK,
             Vine=VINE, Leaf=LEAF, Root=BARK)
    rng = random.Random(seed)
    m.loft_z("StoneDark", (0, 0, 0, 10, 8), (0.6, 0, 0, 9.6, 7.6))
    m.block("Stone", 0, -0.4, 0.95, 8.4, 6.2, 0.7)
    for x, top, broken in ((-2.6, 7.2, False), (2.4, 4.2, True)):
        prism(m, "Stone", x, -1.6, 1.3, top, 0.95, 0.85, 8, math.pi / 8)
        for z in (2.2, 4.0) if top > 4.5 else (2.2,):
            prism(m, "StoneLight", x, -1.6, z - 0.15, z + 0.15, 1.0, 1.0, 8, math.pi / 8)
        if broken:
            for k in range(4):  # a jagged top
                a = k * math.tau / 4 + 0.3
                m.block("Stone", x + math.cos(a) * 0.5, -1.6 + math.sin(a) * 0.5, top + 0.25 + 0.2 * (k % 2), 0.7, 0.7, 0.6 + 0.4 * (k % 2))
        else:
            m.block("StoneLight", x, -1.6, top + 0.3, 2.4, 2.4, 0.6)
            m.block("Stone", x, -1.6, top + 0.8, 2.0, 2.0, 0.4)
            moss_on(m, rng, x, -1.6, top + 1.0, 2.0, 2.0, 3)
            hanging_vine(m, "Vine", x + 0.9, -0.7, top + 0.6, 3.8, 0.26, rng, "Leaf")
    for z in (2.0, 3.0, 4.0, 5.0, 6.0):  # glyphs down the tall column's front
        m.block("Jade", -2.6 + (0.2 if z % 2 else -0.2), -0.66, z, 0.5, 0.1, 0.4)
    for k, (x, y, turn) in enumerate(((1.0, 2.6, 0.1), (2.9, 2.9, -0.15), (4.6, 2.4, 0.25))):  # the fallen column's drums
        m.loft_x("Stone" if k % 2 else "StoneLight", (x - 0.85, y + turn, 1.0, 1.8, 1.8), (x + 0.85, y - turn, 1.0, 1.8, 1.8))
    beam(m, "Stone", (-4.6, 2.2, 0.3), (-1.2, 2.6, 2.4), 2.4, 0.7)  # a slab leaning on them
    beam(m, "StoneDark", (-4.4, 2.2, 0.75), (-1.4, 2.6, 2.6), 1.6, 0.1)
    limb(m, "Root", [(-4.8, -3.6, 0.1), (-3.2, -2.8, 1.2), (-2.6, -2.3, 2.6), (-2.2, -1.9, 4.6)], 0.5, 0.25)
    limb(m, "Root", [(4.8, -2.8, 0.1), (3.6, -2.2, 1.3), (2.9, -1.9, 2.6)], 0.45, 0.25)
    moss_on(m, rng, 1.5, -0.6, 1.3, 4.0, 3.0, 3, "MossDark")
    rubble(m, rng, 0, 0, 6.0, 8, inner=0.8)
    return m


def jungle_fronds(seed=3):
    """A clump of huge dark jungle leaves with glowing seed pods among them: the filler between everything."""
    m = prop("JungleFronds", Leaf=LEAF, LeafDark=LEAF_DARK, LeafLight=LEAF_LIGHT, Stem="#2d6a3a", Pod=POD, Soil=LATERITE_DARK)
    rng = random.Random(seed)
    m.loft_z("Soil", (0, 0, 0, 3.0, 2.8), (0.4, 0, 0, 2.2, 2.0))
    for k in range(7):
        a = k * math.tau / 7 + rng.uniform(-0.2, 0.2)
        h = rng.uniform(1.6, 3.2)
        base = (math.cos(a) * 0.4, math.sin(a) * 0.4, h)
        beam(m, "Stem", (0, 0, 0.3), base, 0.22)
        big_leaf(m, "Leaf" if k % 2 else "LeafDark", base, a, rng.uniform(3.2, 4.4), rng.uniform(1.6, 2.2), rng.uniform(0.6, 1.2), 1.2,
                 "LeafLight")
    for k in range(3):
        a = k * math.tau / 3 + 0.5
        top = (math.cos(a) * 0.9, math.sin(a) * 0.9, 2.6 + k * 0.5)
        beam(m, "Stem", (0, 0, 0.3), top, 0.16)
        ball(m, "Pod", top[0], top[1], top[2] + 0.35, 0.42, 6, 4)
    return m


def jungle_tree(seed=4):
    """A tall jungle tree: buttress roots, a straight trunk, flat layers of canopy, vines hanging off it and
    glowing pods dangling underneath."""
    m = prop("JungleTree", Bark=BARK, BarkDark=BARK_DARK, Leaf=LEAF, LeafDark=LEAF_DARK, LeafLight=LEAF_LIGHT, Vine=VINE, Pod=POD,
             Moss=MOSS)
    rng = random.Random(seed)
    for k in range(5):  # buttress roots
        a = k * math.tau / 5 + rng.uniform(-0.2, 0.2)
        limb(m, "BarkDark", [(math.cos(a) * 0.9, math.sin(a) * 0.9, 4.2), (math.cos(a) * 2.3, math.sin(a) * 2.3, 1.6),
                             (math.cos(a) * 3.6, math.sin(a) * 3.6, 0.2)], 1.3, 0.55)
    prism(m, "Bark", 0, 0, 0, 14, 1.8, 1.25, 7)
    m.block("Moss", 1.5, 0.5, 3.4, 0.4, 1.4, 2.8)
    pads = [(0, 0, 14.6, 10, 9, 1.8, "Leaf"), (1.2, -0.8, 16.6, 7, 6.5, 1.8, "LeafDark"), (-0.6, 0.6, 18.3, 4.6, 4.4, 1.4, "LeafLight")]
    for k in range(4):  # branches out to side pads
        a = k * math.tau / 4 + 0.6
        end = (math.cos(a) * 5.2, math.sin(a) * 4.6, 12.4 + (k % 2) * 1.2)
        beam(m, "Bark", (0, 0, 10.5 + k * 0.6), end, 0.6, None, 0.35)
        pads.append((end[0], end[1], end[2] + 0.8, 4.4, 4.0, 1.4, "Leaf" if k % 2 else "LeafDark"))
    for x, y, z, w, d, h, role in pads:
        m.block(role, x, y, z, w, d, h)
        m.block(role, x, y, z - h / 2 - 0.3, w * 0.8, d * 0.8, 0.6)
    for _ in range(9):  # vines off the canopy's edges
        a = rng.uniform(0, math.tau)
        r = rng.uniform(3.6, 5.6)
        hanging_vine(m, "Vine", math.cos(a) * r, math.sin(a) * r, 13.4, rng.uniform(3, 7), 0.26, rng, "Leaf")
    for _ in range(5):  # glowing pods under the canopy
        a = rng.uniform(0, math.tau)
        r = rng.uniform(1.8, 3.6)
        x, y = math.cos(a) * r, math.sin(a) * r
        length = rng.uniform(0.8, 2.0)
        m.block("Vine", x, y, 13.6 - length / 2, 0.12, 0.12, length)
        ball(m, "Pod", x, y, 13.6 - length - 0.35, 0.4, 6, 4)
    return m


def hanging_lantern(seed=5):
    """A carved stone post with a bronze arm, and a lantern hanging from it, swinging gently. The lantern hangs
    straight above the prop's origin (the post stands to one side), so the game swings it round its hook."""
    m = prop("HangingLantern", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Bronze=BRONZE, Gold=GOLD,
             Lantern=BRONZE_DARK, Lamp=LAMP, Moss=MOSS, Vine=VINE, Leaf=LEAF, Jade=JADE)
    rng = random.Random(seed)
    px = -2.4
    m.loft_z("StoneDark", (0, px, 0, 2.2, 2.2), (0.8, px, 0, 1.8, 1.8))
    m.block("Stone", px, 0, 4.2, 1.0, 1.0, 6.8)
    for z in (2.0, 5.6):
        m.block("StoneLight", px, 0, z, 1.2, 1.2, 0.3)
    for z in (3.0, 3.8, 4.6):
        m.block("Jade", px + 0.51, 0, z, 0.08, 0.4, 0.35)
    m.block("StoneLight", px, 0, 7.8, 1.5, 1.5, 0.5)
    gem(m, "Gold", px, 0, 8.3, 0.35, 0.6, 0.2, 4, math.pi / 4)
    limb(m, "Bronze", [(px + 0.4, 0, 7.4), (-1.3, 0, 8.1), (-0.4, 0, 8.25), (0, 0, 7.95)], 0.22, 0.16)
    # The lantern: hook at z 7.8, chain, roof, frame and light.
    m.block("Lantern", 0, 0, 7.15, 0.12, 0.12, 1.4)
    m.loft_z("Lantern", (6.0, 0, 0, 1.9, 1.9), (6.5, 0, 0, 0.6, 0.6))
    for dx, dy in ((-0.62, -0.62), (0.62, -0.62), (0.62, 0.62), (-0.62, 0.62)):
        m.block("Lantern", dx, dy, 5.15, 0.18, 0.18, 1.7)
    m.block("Lantern", 0, 0, 4.25, 1.6, 1.6, 0.25)
    m.block("Lantern", 0, 0, 3.9, 0.35, 0.35, 0.5)
    m.block("Lamp", 0, 0, 5.2, 1.06, 1.06, 1.5)
    moss_on(m, rng, px, 0, 8.05, 1.5, 1.5, 2)
    hanging_vine(m, "Vine", px - 0.5, 0.5, 7.6, 3.6, 0.22, rng, "Leaf")
    rubble(m, rng, px, 0, 2.2, 5, size=(0.4, 0.8), inner=0.8)
    return m


def spirit_brazier(seed=6):
    """A bronze fire bowl on three legs, on a stone plinth, burning with a jade spirit fire that flickers,
    sparks rising out of it for ever."""
    m = prop("SpiritBrazier", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Bronze=BRONZE, BronzeDark=BRONZE_DARK,
             Patina=PATINA, Flame="#4dffa0", FlameCore="#e2fff0", Ember=JADE, Moss=MOSS)
    rng = random.Random(seed)
    m.loft_z("StoneDark", (0, 0, 0, 3.8, 3.8), (0.5, 0, 0, 3.4, 3.4))
    m.block("Stone", 0, 0, 0.9, 3.0, 3.0, 0.8)
    m.block("StoneLight", 0, 0, 1.4, 3.2, 3.2, 0.2)
    for k in range(3):
        a = k * math.tau / 3 + 0.4
        beam(m, "BronzeDark", (math.cos(a) * 1.25, math.sin(a) * 1.25, 1.5), (math.cos(a) * 0.7, math.sin(a) * 0.7, 2.8), 0.28)
    prism(m, "Bronze", 0, 0, 2.6, 3.4, 0.9, 1.7, 8, math.pi / 8)
    prism(m, "BronzeDark", 0, 0, 3.3, 3.55, 1.8, 1.8, 8, math.pi / 8)
    for k in range(4):
        a = k * math.tau / 4 + 0.2
        m.block("Patina", math.cos(a) * 1.3, math.sin(a) * 1.3, 3.0, 0.5, 0.5, 0.4)
    prism(m, "Flame", 0, 0, 3.4, 6.2, 1.15, 0.05, 5, 0.3, (0.15, -0.1))
    for a, h in ((0.5, 4.8), (2.6, 5.2), (4.4, 4.5)):
        prism(m, "Flame", math.cos(a) * 0.75, math.sin(a) * 0.75, 3.4, h, 0.55, 0.04, 5, a, (math.cos(a) * 0.3, math.sin(a) * 0.3))
    prism(m, "FlameCore", 0, 0, 3.4, 5.0, 0.6, 0.04, 5, 0.1)
    for k, z in enumerate((5.0, 7.0, 9.0, 11.0)):  # sparks two studs apart, so rising two and starting over loops
        for a in (0.4, 2.5, 4.4):
            jitter = ((k * 5 + int(a * 10)) % 5 - 2) * 0.18
            r = 0.5 + 0.12 * k
            m.block("Ember", math.cos(a + k) * r + jitter, math.sin(a + k) * r, z + (a - 2.4) * 0.3, 0.22, 0.22, 0.22)
    moss_on(m, rng, 1.2, -1.2, 0.5, 1.2, 1.0, 1)
    return m


def watcher_bloom(seed=7):
    """A jungle flower that watches: a tall stalk, a cup of crimson petals, and in it one big eye under a heavy
    lid that slowly looks round from side to side. Its eye sits straight above the prop's origin, so the game
    turns it on the spot."""
    m = prop("WatcherBloom", Leaf=LEAF, LeafDark=LEAF_DARK, LeafLight=LEAF_LIGHT, Stalk="#3d7a3c", Petal="#9b2d55",
             PetalDark="#5e1a36", EyeBall="#f4efe2", Iris=JADE, Pupil="#120f18", Lid="#6e1f40", Soil=LATERITE_DARK)
    rng = random.Random(seed)
    m.loft_z("Soil", (0, 0.3, 0.2, 3.2, 3.0), (0.4, 0.3, 0.2, 2.2, 2.0))
    for k in range(5):
        a = k * math.tau / 5 + 0.3
        big_leaf(m, "Leaf" if k % 2 else "LeafDark", (math.cos(a) * 0.4 + 0.3, math.sin(a) * 0.4 + 0.2, 0.5), a,
                 rng.uniform(3.0, 3.8), rng.uniform(1.5, 1.9), 0.6, 0.9, "LeafLight")
    limb(m, "Stalk", [(0.4, 0.3, 0.3), (0.9, -0.2, 2.5), (-0.4, 0.2, 4.8), (0, 0, 6.6)], 0.62, 0.42)
    zc, r = 8.2, 1.5
    prism(m, "PetalDark", 0, 0, 6.5, 7.3, 0.5, 1.2, 7)
    for k in range(7):  # an open flower round the eye, two rows of petals
        a = k * math.tau / 7
        plate(m, "Petal", (math.cos(a) * 0.8, math.sin(a) * 0.8, 7.2), (math.cos(a) * 3.0, math.sin(a) * 3.0, 7.9),
              (-math.sin(a), math.cos(a), 0), 1.0, 1.5, 0.18)
        b = a + math.tau / 14
        plate(m, "PetalDark", (math.cos(b) * 0.6, math.sin(b) * 0.6, 7.0), (math.cos(b) * 2.2, math.sin(b) * 2.2, 7.3),
              (-math.sin(b), math.cos(b), 0), 0.8, 1.1, 0.16)
    ball(m, "EyeBall", 0, 0, zc, r, 10, 7)
    disc(m, "Iris", 0, r * 0.92, zc, 0.78, 0.14, 12, "xz")
    m.block("Pupil", 0, r * 0.92 + 0.1, zc, 0.26, 0.08, 1.1)
    m.loft_z("Lid", (zc + 0.8, 0, 0.1, 3.1, 3.0), (zc + 1.3, 0, 0.06, 2.4, 2.3))  # a heavy lid over the top of the eye
    m.loft_z("Lid", (zc + 1.3, 0, 0.06, 2.4, 2.3), (zc + 1.7, 0, 0.0, 1.1, 1.1))
    return m


def orrery(seed=8):
    """A rare find: a bronze orrery left on its pedestal, a glowing jade orb floating in the middle and three
    rings turning round it, one flat with little planets on it, one on edge, one tumbling over. All of it
    floats, gently rising and falling."""
    m = prop("Orrery", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Bronze=BRONZE, BronzeDark=BRONZE_DARK, Orb=JADE,
             RingA=GOLD, Planets=PATINA, RingB=BRONZE, RingC=PATINA, Gold=GOLD, Moss=MOSS)
    rng = random.Random(seed)
    m.loft_z("StoneDark", (0, 0, 0, 3.6, 3.6), (0.5, 0, 0, 3.1, 3.1))
    prism(m, "Stone", 0, 0, 0.5, 3.2, 0.95, 0.75, 8, math.pi / 8)
    m.block("StoneLight", 0, 0, 3.4, 2.2, 2.2, 0.4)
    prism(m, "BronzeDark", 0, 0, 3.6, 4.1, 0.6, 1.1, 8, math.pi / 8)
    for k in range(4):
        a = k * math.tau / 4 + math.pi / 4
        m.block("Gold", math.cos(a) * 0.9, math.sin(a) * 0.9, 4.15, 0.3, 0.3, 0.3)
    zc = 8.3
    ball(m, "Orb", 0, 0, zc, 1.0, 8, 5)
    flat_ring(m, "RingA", 0, 0, zc, 2.0, 0.32, 0.22, 20)
    for k in range(3):
        a = k * math.tau / 3
        ball(m, "Planets", math.cos(a) * 2.0, math.sin(a) * 2.0, zc + 0.35, 0.32 + 0.08 * k, 6, 4)
    hoop(m, "RingB", 0, 0, zc, 2.8, 0.26, "xz", 20)
    flat_ring(m, "RingC", 0, 0, zc, 3.5, 0.3, 0.22, 24)
    moss_on(m, rng, 0.6, 0.6, 0.5, 1.2, 1.0, 1)
    return m


def stone_hand(seed=9):
    """A giant stone hand rising out of the floor, palm up, cupping a jade orb that floats over it, pulsing."""
    m = prop("StoneHand", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Gold=GOLD, Orb=JADE, Moss=MOSS, Vine=VINE,
             Leaf=LEAF, Soil=LATERITE_DARK)
    rng = random.Random(seed)
    puddle(m, "Soil", ((0, 0, 6, 5.5),), z=0.08, thick=0.16)
    m.loft_z("Stone", (0, 0, 0, 2.8, 2.6), (3.8, 0.1, 0.1, 2.4, 2.2))
    m.block("Gold", 0.1, 0.1, 3.3, 2.6, 2.4, 0.5)
    m.loft_z("Stone", (3.8, 0.1, 0.1, 2.4, 2.2), (4.6, 0.1, 0.3, 3.2, 3.0))
    m.block("Stone", 0.1, 0.4, 5.0, 3.2, 3.0, 0.9)
    for k, x in enumerate((-1.1, -0.37, 0.37, 1.1)):  # fingers curling up and in at the far edge
        tip = 7.6 + (0.4 if k in (1, 2) else 0)
        beam(m, "Stone", (x + 0.1, 1.6, 5.2), (x + 0.1, 2.2, 6.7), 0.68)
        m.block("StoneLight", x + 0.1, 2.2, 6.7, 0.7, 0.7, 0.7)
        beam(m, "Stone", (x + 0.1, 2.2, 6.7), (x + 0.1, 1.7, tip), 0.64, None, 0.55)
    beam(m, "Stone", (-1.4, -0.6, 5.0), (-2.2, 0.3, 6.1), 0.75)  # thumb
    m.block("StoneLight", -2.2, 0.3, 6.1, 0.75, 0.75, 0.75)
    beam(m, "Stone", (-2.2, 0.3, 6.1), (-1.6, 0.9, 6.9), 0.7, None, 0.6)
    ball(m, "Orb", 0.1, 0.6, 9.2, 1.1, 8, 5)
    for k in range(5):  # a vine winding up the forearm
        a = k * 1.4
        beam(m, "Vine", (math.cos(a) * 1.35, math.sin(a) * 1.25, 0.2 + k * 0.7), (math.cos(a + 1.4) * 1.3, math.sin(a + 1.4) * 1.2, 0.9 + k * 0.7),
             0.24)
    beam(m, "StoneDark", (1.25, -1.15, 1.0), (1.2, -1.1, 2.6), 0.1, 0.06)
    moss_on(m, rng, -0.3, -0.3, 5.45, 1.6, 1.4, 2)
    rubble(m, rng, 0, 0, 4.0, 9, inner=0.6)
    return m


def rune_circle(seed=10):
    """A round stone set into the floor, carved with two rings of glowing runes that turn opposite ways round a
    pulsing sigil. Flat (under half a stud), so it can lie where the eggs land."""
    m = prop("RuneCircle", Slab=STONE, SlabDark=STONE_DARK, Laterite=LATERITE_DARK, RuneOuter=JADE, RuneInner=JADE, Sigil="#c8ffe6")
    rng = random.Random(seed)
    disc(m, "Slab", 0, 0, 0.08, 6.6, 0.16, 24)
    disc(m, "SlabDark", 0, 0, 0.12, 4.7, 0.12, 24)
    disc(m, "Slab", 0, 0, 0.14, 2.2, 0.12, 16)
    for k in range(10):  # broken stones round the edge, back into the floor
        a = k * math.tau / 10 + rng.uniform(-0.15, 0.15)
        s = rng.uniform(0.8, 1.6)
        m.block("Laterite" if k % 2 else "SlabDark", math.cos(a) * 6.9, math.sin(a) * 6.9, 0.08, s, s * 0.8, 0.16)

    def rune(role, a, r, size, kind):
        x, y = math.cos(a) * r, math.sin(a) * r
        u, v = (-math.sin(a), math.cos(a)), (math.cos(a), math.sin(a))  # along the ring, and outwards

        def bar(du, dv, length, across):
            cx, cy = x + u[0] * du + v[0] * dv, y + u[1] * du + v[1] * dv
            if across:
                beam(m, role, (cx - u[0] * length / 2, cy - u[1] * length / 2, 0.22), (cx + u[0] * length / 2, cy + u[1] * length / 2, 0.22),
                     size * 0.22, 0.08)
            else:
                beam(m, role, (cx - v[0] * length / 2, cy - v[1] * length / 2, 0.22), (cx + v[0] * length / 2, cy + v[1] * length / 2, 0.22),
                     size * 0.22, 0.08)

        bar(0, 0, size, False)
        if kind == 0:
            bar(0, size * 0.4, size * 0.7, True)
        elif kind == 1:
            bar(size * 0.3, -size * 0.4, size * 0.6, True)
            bar(-size * 0.3, size * 0.4, size * 0.6, True)
        else:
            bar(0, 0, size * 0.8, True)

    for k in range(16):
        rune("RuneOuter", k * math.tau / 16, 5.6, 1.1, k % 3)
    flat_ring(m, "RuneInner", 0, 0, 0.22, 2.75, 0.24, 0.08, 20)
    for k in range(8):
        rune("RuneInner", k * math.tau / 8 + 0.2, 3.65, 0.9, (k + 1) % 3)
    for p, q in (((0, 1.5), (1.1, 0)), ((1.1, 0), (0, -1.5)), ((0, -1.5), (-1.1, 0)), ((-1.1, 0), (0, 1.5))):  # an eye
        beam(m, "Sigil", (p[0], p[1], 0.24), (q[0], q[1], 0.24), 0.26, 0.08)
    m.block("Sigil", 0, 0, 0.24, 0.6, 0.6, 0.08)
    return m


# ---------------------------------------------------------------------- rim props and landmarks


def step_temple(seed=11):
    """A landmark for the rims: a stepped temple of five tiers with a stair up its front, a shrine on top whose
    doorway glows, jade glyphs on its tiers, a tree's roots spilling over one corner, and over it all a jade
    orb floating with glyph-crystals circling round it, rising and falling together."""
    m = prop("StepTemple", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Socket=SOCKET, Jade=JADE, Gold=GOLD,
             Moss=MOSS, MossDark=MOSS_DARK, Vine=VINE, Leaf=LEAF, LeafDark=LEAF_DARK, Root=BARK, Orb=JADE, Glyph="#9dffc8", Front="#ff00ff")
    rng = random.Random(seed)
    tiers = [(0, 2.5, 26), (2.5, 5, 22), (5, 7.5, 18), (7.5, 10, 14), (10, 12.5, 10)]
    for k, (z0, z1, w) in enumerate(tiers):
        m.block("Stone" if k % 2 == 0 else "StoneDark", 0, 0, (z0 + z1) / 2, w, w, z1 - z0)
        m.block("StoneLight", 0, 0, z1 - 0.2, w + 0.3, w + 0.3, 0.4)
        for side in (-1, 1):  # glyphs on the front either side of the stair
            for g in range(2):
                if 3.6 + g * 1.6 + 0.6 < w / 2:
                    m.block("Jade", side * (3.6 + g * 1.6), w / 2 + 0.06, (z0 + z1) / 2, 0.8, 0.1, 0.7)
        for _ in range(2):
            a = rng.choice((0, 1, 2, 3))
            u = rng.uniform(-w / 2 + 1.5, w / 2 - 1.5)
            x, y = [(u, -w / 2), (u, w / 2), (-w / 2, u), (w / 2, u)][a]
            if a == 1 and abs(u) < 3:
                continue
            hanging_vine(m, "Vine", x * 1.01, y * 1.01, z1, rng.uniform(1.6, 3.2), 0.26, rng, "Leaf")
        moss_on(m, rng, rng.uniform(-w / 3, w / 3), -w / 2 + 1.2, z1, rng.uniform(2, 4), 1.6, 2, "Moss" if k % 2 else "MossDark")
    steps = 25
    for k in range(steps):
        y = 15.0 - 0.4 * k
        z = 0.5 * k
        m.block("StoneLight" if k % 2 else "Stone", 0, (5 + y) / 2, z + 0.25, 4, y - 5, 0.5)
    for side in (-1, 1):
        beam(m, "StoneDark", (side * 2.4, 15.2, 0.6), (side * 2.4, 5.0, 13.0), 0.8)
    # The shrine on top, its doorway glowing.
    m.block("Stone", 0, 0, 14.5, 7, 7, 4)
    m.block("Socket", 0, 3.52, 14.0, 2.4, 0.1, 3.0)
    m.block("Jade", 0, 3.56, 13.9, 1.7, 0.1, 2.4)
    m.block("StoneLight", 0, 0, 16.8, 8, 8, 0.6)
    m.block("Stone", 0, 0, 17.6, 6, 6, 1.0)
    m.block("StoneLight", 0, 0, 18.4, 4, 4, 0.6)
    m.block("Gold", 0, 0, 19.0, 2, 2, 0.6)
    for side in (-1, 1):
        m.block("Gold", side * 2.4, 3.55, 14.0, 0.5, 0.2, 3.4)
    # A tree that took root on a back ledge, its roots draped down over the steps below it.
    tx, ty = 7.6, -10.0
    prism(m, "Root", tx, ty, 5.0, 13.0, 1.1, 0.8, 7)
    for (x0, y0), (x1, y1) in (((tx - 0.9, ty - 0.4), (tx - 2.0, -11.2)), ((tx + 0.9, ty - 0.3), (tx + 2.4, -11.3)), ((tx, ty - 0.9), (tx - 0.4, -11.3))):
        limb(m, "Root", [(x0, y0, 5.6), (x1, y1, 5.1), (x1 + 0.2, y1 - 0.3, 2.6), (x1 + 0.4, -13.1, 2.4), (x1 + 0.5, -13.3, 0.2)], 0.7, 0.4)
    for k in range(3):
        a = k * math.tau / 3 + 0.5
        beam(m, "Root", (tx, ty, 11.0 + k * 0.6), (tx + math.cos(a) * 3.2, ty + math.sin(a) * 2.8, 13.2 + k * 0.4), 0.5, None, 0.3)
    m.block("Leaf", tx, ty, 14.2, 8.0, 7.0, 1.8)
    m.block("LeafDark", tx + 0.6, ty - 0.4, 15.8, 5.4, 4.8, 1.6)
    m.block("Leaf", tx - 0.3, ty + 0.2, 17.1, 3.0, 2.8, 1.2)
    for k in range(5):
        a = k * math.tau / 5 + 0.2
        hanging_vine(m, "Vine", tx + math.cos(a) * 3.4, ty + math.sin(a) * 3.0, 13.4, rng.uniform(2, 4), 0.24, rng, "Leaf")
    # The orb and the glyph-crystals round it.
    zc = 26.0
    ball(m, "Orb", 0, 0, zc, 1.8, 8, 5)
    for k in range(6):
        a = k * math.tau / 6
        gem(m, "Glyph", math.cos(a) * 4.6, math.sin(a) * 4.6, zc + (0.8 if k % 2 else -0.8), 0.55, 1.1, 1.1, 4, a)
    m.block("Front", 0, 16, 1, 0.2, 0.2, 0.2)
    return m


def guardian_statue(seed=12):
    """A landmark for the rims: a tall temple guardian in a robe, holding a staff topped with jade, a gold mask
    on its face and a crown of gold feathers. Its head slowly turns from side to side, as if it watches the
    eggs fly by. The head sits straight above the prop's origin, so the game turns it on the spot."""
    m = prop("GuardianStatue", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Gold=GOLD, GoldDark=GOLD_DARK, Jade=JADE,
             Moss=MOSS, MossDark=MOSS_DARK, Vine=VINE, Leaf=LEAF, StatueHead=STONE, Mask=GOLD, Gaze=JADE, Front="#ff00ff")
    rng = random.Random(seed)
    m.loft_z("StoneDark", (0, 0, 0, 8, 7), (1.5, 0, 0, 7.4, 6.4))
    m.block("Stone", 0, 0, 2.0, 6.6, 5.6, 1.0)
    for x in (-2.2, -0.75, 0.75, 2.2):
        m.block("Jade", x, 2.82, 2.0, 0.8, 0.1, 0.5)
    for side in (-1, 1):
        m.block("Stone", side * 1.3, 0.7, 3.0, 1.7, 3.0, 1.0)
    m.loft_z("Stone", (2.5, 0, 0, 4.6, 3.3), (11, 0, 0, 3.6, 2.6))
    m.block("StoneLight", 0, 1.38, 6.6, 1.6, 0.3, 7.8)
    for z in (4.0, 6.0, 8.0):
        m.block("Gold", 0, 1.56, z, 1.0, 0.1, 0.3)
    m.block("Gold", 0, 0, 11.2, 3.9, 2.9, 0.6)
    m.loft_z("Stone", (11, 0, 0, 3.6, 2.6), (16.5, 0, 0, 5.6, 3.2))
    m.block("Gold", 0, 1.55, 14.4, 2.6, 0.25, 2.0)
    gem(m, "Jade", 0, 1.75, 14.4, 0.45, 0.6, 0.6, 4, math.pi / 4)
    for side in (-1, 1):
        m.block("StoneLight", side * 3.1, 0, 16.0, 1.7, 2.7, 1.4)
        m.block("Gold", side * 3.1, 0, 16.75, 1.8, 2.8, 0.2)
        moss_on(m, rng, side * 3.1, -0.3, 16.85, 1.4, 2.0, 2, "Moss" if side > 0 else "MossDark")
    beam(m, "Stone", (3.1, 0, 15.5), (3.4, 0.6, 12.6), 1.1)  # the right arm holding the staff
    beam(m, "Stone", (3.4, 0.6, 12.6), (3.4, 2.2, 12.8), 1.0)
    m.block("StoneLight", 3.4, 2.4, 12.8, 1.1, 1.1, 1.1)
    m.block("StoneDark", 3.4, 2.4, 13.3, 0.5, 0.5, 21.6)
    for z in (6.0, 18.0):
        m.block("Gold", 3.4, 2.4, z, 0.7, 0.7, 0.3)
    hoop(m, "Gold", 3.4, 2.4, 25.0, 1.1, 0.22, "xz", 10)
    gem(m, "Jade", 3.4, 2.4, 25.0, 0.55, 0.9, 0.9, 4, math.pi / 4)
    limb(m, "Stone", [(-3.1, 0, 15.5), (-3.3, 0.4, 12.6), (-2.0, 1.5, 11.6)], 1.1, 1.0)  # the left hand rests on its belt
    m.block("StoneLight", -1.7, 1.6, 11.5, 1.1, 1.0, 1.0)
    m.block("StoneDark", 0, 0, 17.0, 1.6, 1.6, 1.4)
    # The head, mask and crown, all turning together.
    m.block("StatueHead", 0, 0, 18.9, 2.8, 2.6, 3.0)
    m.block("StatueHead", 0, -0.1, 20.7, 3.4, 3.0, 0.6)
    m.block("StatueHead", 0, -0.2, 21.5, 2.6, 2.2, 1.0)
    for side in (-1, 1):
        m.block("StatueHead", side * 1.5, 0, 18.6, 0.4, 1.2, 1.8)
        m.block("Mask", side * 1.72, 0, 18.4, 0.1, 0.7, 0.7)
    m.block("Mask", 0, 1.38, 19.0, 2.6, 0.3, 2.6)
    m.block("Mask", 0, 1.6, 18.8, 0.5, 0.3, 1.2)
    m.block("Mask", 0, 1.56, 17.95, 1.2, 0.12, 0.2)
    for side in (-1, 1):
        m.block("Gaze", side * 0.66, 1.56, 19.35, 0.78, 0.06, 0.24)
    m.block("Mask", 0, 1.56, 19.75, 2.4, 0.1, 0.22)
    for k in range(7):  # the crown of gold feathers
        a = math.radians(30 + k * 20)
        plate(m, "Mask", (0, -0.1, 21.9), (math.cos(a) * 2.7, -0.3, 21.9 + math.sin(a) * 2.7), (-math.sin(a), 0, math.cos(a)), 0.35, 0.8, 0.14)
    gem(m, "Gaze", 0, 1.15, 21.6, 0.3, 0.4, 0.4, 4, math.pi / 4)
    for x, y, top, length in ((2.7, 1.0, 16.4, 6), (-3.6, 0.8, 16.2, 4.5), (-3.0, -1.2, 16.6, 8), (3.4, 2.9, 22.0, 5)):
        hanging_vine(m, "Vine", x, y, top, length, 0.28, rng, "Leaf")
    m.block("Front", 0, 6, 1, 0.2, 0.2, 0.2)
    return m


def floating_monoliths(seed=13):
    """Three obelisks carved with glowing runes, hovering over a broken round platform and slowly circling it,
    each rising and falling in its own time."""
    m = prop("FloatingMonoliths", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Jade=JADE, Moss=MOSS,
             MonolithA=STONE, MonolithB=STONE_LIGHT, MonolithC=STONE_DARK, RuneA=JADE, RuneB=JADE, RuneC=JADE)
    rng = random.Random(seed)
    disc(m, "StoneDark", 0, 0, 0.3, 5.2, 0.6, 12)
    disc(m, "Stone", 0, 0, 0.75, 4.4, 0.3, 12)
    flat_ring(m, "Jade", 0, 0, 0.92, 3.1, 0.3, 0.08, 16)
    m.block("Jade", 0, 0, 0.92, 0.8, 0.8, 0.08)
    rubble(m, rng, 0, 0, 6.2, 8, inner=0.85)
    moss_on(m, rng, -2.6, 1.8, 0.9, 1.6, 1.4, 2)
    for k, (role, rune, z0) in enumerate((("MonolithA", "RuneA", 3.4), ("MonolithB", "RuneB", 5.0), ("MonolithC", "RuneC", 4.2))):
        a = k * math.tau / 3 + 0.3
        x, y = math.cos(a) * 3.3, math.sin(a) * 3.3
        m.loft_z(role, (z0 - 0.9, x, y, 0.2, 0.2), (z0, x, y, 1.4, 1.4))
        m.loft_z(role, (z0, x, y, 1.4, 1.4), (z0 + 5.0, x, y, 1.0, 1.0))
        m.loft_z(role, (z0 + 5.0, x, y, 1.0, 1.0), (z0 + 5.8, x, y, 0.08, 0.08))
        for g in range(3):  # runes down all four faces
            z = z0 + 1.0 + g * 1.4
            half = 0.72 - 0.04 * (z - z0)
            for dx, dy, w, d in ((half, 0, 0.08, 0.5), (-half, 0, 0.08, 0.5), (0, half, 0.5, 0.08), (0, -half, 0.5, 0.08)):
                m.block(rune, x + dx, y + dy, z, w, d, 0.42 if g % 2 else 0.6)
    return m


def sky_lanterns(seed=14):
    """Paper lanterns floating over a little stone shrine on the rim, slowly circling it and drifting up and
    down, warm lights over the dark jungle."""
    m = prop("SkyLanterns", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Lamp=LAMP, Moss=MOSS, LampA="#ffb347",
             LampB="#ff8c42", LampC="#ffd45a", CapA="#7a2e22", CapB="#7a2e22", CapC="#7a2e22")
    rng = random.Random(seed)
    m.loft_z("StoneDark", (0, 0, 0, 2.4, 2.4), (0.6, 0, 0, 2.0, 2.0))
    m.block("Stone", 0, 0, 1.4, 0.9, 0.9, 1.6)
    m.block("StoneLight", 0, 0, 2.4, 2.2, 2.2, 0.4)
    m.block("Lamp", 0, 0, 3.15, 1.2, 1.2, 1.1)
    m.loft_z("Stone", (3.7, 0, 0, 2.6, 2.6), (4.6, 0, 0, 0.4, 0.4))
    moss_on(m, rng, 0, 0, 0.6, 2.0, 2.0, 2)
    spots = [(3.0, 1.0, 9.0, "A"), (-2.6, 3.4, 12.5, "B"), (-3.6, -2.4, 15.0, "C"), (1.6, -4.0, 17.5, "A"), (4.4, -1.0, 20.5, "B"),
             (-0.8, 2.0, 22.5, "C"), (0.4, -0.8, 13.5, "A")]
    for x, y, z, group in spots:
        s = rng.uniform(0.85, 1.15)
        m.loft_z(f"Lamp{group}", (z - 1.0 * s, x, y, 1.0 * s, 1.0 * s), (z + 0.2 * s, x, y, 1.5 * s, 1.5 * s))
        m.loft_z(f"Lamp{group}", (z + 0.2 * s, x, y, 1.5 * s, 1.5 * s), (z + 1.0 * s, x, y, 1.1 * s, 1.1 * s))
        m.block(f"Cap{group}", x, y, z + 1.05 * s, 1.15 * s, 1.15 * s, 0.18)
        m.block(f"Cap{group}", x, y, z - 1.05 * s, 1.05 * s, 1.05 * s, 0.16)
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):  # ribs down its sides
            m.loft_z(f"Cap{group}", (z - 1.0 * s, x + dx * 0.52 * s, y + dy * 0.52 * s, 0.12 if dx else 0.2 * s, 0.2 * s if dx else 0.12),
                     (z + 0.2 * s, x + dx * 0.77 * s, y + dy * 0.77 * s, 0.12 if dx else 0.2 * s, 0.2 * s if dx else 0.12))
            m.loft_z(f"Cap{group}", (z + 0.2 * s, x + dx * 0.77 * s, y + dy * 0.77 * s, 0.12 if dx else 0.2 * s, 0.2 * s if dx else 0.12),
                     (z + 1.0 * s, x + dx * 0.57 * s, y + dy * 0.57 * s, 0.12 if dx else 0.2 * s, 0.2 * s if dx else 0.12))
    return m


def eclipse(seed=15):
    """A black eclipsed sun hanging in the sky beyond the rims, ringed with white fire, its corona of rays slowly
    turning. The model starts high above the ground, and it looks the same from in front and behind, so it only
    has to face along the corridor."""
    m = prop("Eclipse", Moon="#0d0b14", EclipseRing="#fff3cf", Corona="#ffd36b", Front="#ff00ff")
    zc = 40.0
    disc(m, "Moon", 0, 0, zc, 10, 1.2, 28, "xz")
    hoop(m, "EclipseRing", 0, 0, zc, 10.5, 1.0, "xz", 28)
    for k in range(16):
        a = k * math.tau / 16
        r1, r2 = 10.8, (19.5 if k % 2 == 0 else 15.5)
        plate(m, "Corona", (math.cos(a) * r1, 0, zc + math.sin(a) * r1), (math.cos(a) * r2, 0, zc + math.sin(a) * r2),
              (-math.sin(a), 0, math.cos(a)), 2.6, 0.25, 0.5)
    for k in range(16):
        a = (k + 0.5) * math.tau / 16
        plate(m, "Corona", (math.cos(a) * r1, 0, zc + math.sin(a) * r1), (math.cos(a) * 13.0, 0, zc + math.sin(a) * 13.0),
              (-math.sin(a), 0, math.cos(a)), 1.6, 0.2, 0.5)
    m.block("Front", 0, 6, zc, 0.2, 0.2, 0.2)
    return m


def face_fall(seed=16):
    """A giant carved face set into the top of the corridor wall, its mouth open, pouring glowing spirit water down
    the wall into a pool on the floor, drops tumbling down it for ever. Origin on the wall's top inner edge: rim
    z 0, floor z -44, +Y out into the corridor. The Front part tells the game which way it faces, then it goes."""
    m = prop("FaceFall", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Socket=SOCKET, Gaze=JADE, Gold=GOLD, Jade=JADE,
             Moss=MOSS, MossDark=MOSS_DARK, Vine=VINE, Leaf=LEAF, Stream="#3ff0a0", StreamDark="#1f8f6a", Falling="#d6fff0",
             Front="#ff00ff")
    rng = random.Random(seed)
    # The face, standing out from the wall in front of the hanging jungle (which sticks out 1.5).
    m.block("Stone", 0, 1.6, -7.5, 17, 3.2, 22)
    stone_face(m, 3.2, 0, -8.5, 16, 16, open_mouth=True)
    for side in (-1, 1):
        m.block("Stone", side * 8.9, 1.4, -8.5, 1.0, 2.2, 6)
        m.block("Gold", side * 9.45, 1.6, -9.0, 0.3, 1.8, 1.8)
    # Its headdress, rising above the rim.
    m.block("StoneDark", 0, 0.6, 4.2, 19, 5.4, 1.4)
    m.block("Stone", 0, 0.4, 5.7, 15, 4.4, 1.6)
    m.block("Gold", 0, 3.35, 4.2, 19.2, 0.2, 0.6)
    gem(m, "Jade", 0, 2.8, 5.7, 0.7, 0.9, 0.9, 4, math.pi / 4)
    m.block("StoneLight", 0, 0.2, 7.1, 8, 3.4, 1.2)
    for x in (-5.5, -2.8, 2.8, 5.5):
        m.block("StoneLight", x, 0.2, 7.9 + abs(x) * -0.12, 1.4, 2.2, 2.4 - abs(x) * 0.15)
    moss_on(m, rng, -6.0, 0.4, 6.5, 2.6, 3.0, 2)
    moss_on(m, rng, 5.8, 0.6, 6.5, 2.8, 2.4, 2, "MossDark")
    for x, top, length in ((-8.2, 3.0, 8), (8.0, 3.2, 10), (-5.6, -1.2, 5), (6.0, -1.4, 4)):
        hanging_vine(m, "Vine", x, 3.4, top, length, 0.32, rng, "Leaf")
    # The water: out of the mouth, over the lower lip, and down the wall in a curtain.
    m.block("Stream", 0, 4.0, -13.9, 6.0, 1.6, 1.8)
    m.block("Stream", 0, 4.9, -15.6, 6.4, 1.6, 2.4)
    z = -16.8
    while z > -43.5:
        length = min(rng.uniform(5, 8), z + 43.5)
        width = rng.uniform(6.2, 7.2)
        x = rng.uniform(-0.3, 0.3)
        m.block("Stream", x, 5.2, z - length / 2, width, 1.4, length)
        for side in (-1, 1):
            m.block("StreamDark", x + side * (width / 2 + 0.2), 5.0, z - length / 2, 0.5, 1.2, length * 0.9)
        z -= length
    # Drops that fall: rows four studs apart, so moving them down four studs and back loops seamlessly.
    for k, zz in enumerate(range(-17, -44, -4)):
        for x in (-2.4, -0.8, 0.8, 2.3):
            jitter = ((k * 7 + int(x * 10)) % 5 - 2) * 0.2
            m.block("Falling", x + jitter, 6.1, zz - (1.3 if x > 0 else 0), 0.5, 0.3, 0.5)
    puddle(m, "Stream", ((0, 7.5, 12, 7), (0, 10.6, 7, 3.4), (-4.4, 8.8, 4.0, 5.0), (4.2, 8.6, 4.0, 4.6)), z=-43.75, thick=0.5)
    for x, y, s in ((-6.8, 6.0, 1.8), (-6.4, 11.0, 1.4), (-2.6, 13.0, 1.2), (2.8, 13.0, 1.5), (6.4, 10.6, 1.8), (6.9, 5.8, 1.4)):
        m.block("StoneDark" if x < 0 else "Stone", x, y, -44 + s * 0.3, s, s, s * 0.6)
    for x, y, h in ((-1.4, 6.6, 1.6), (1.2, 7.0, 2.0), (0.0, 8.4, 1.2)):
        m.loft_z("Stream", (-43.5, x, y, 0.8, 0.8), (-43.5 + h, x, y, 0.2, 0.2))
    m.block("Front", 0, 6, -20, 0.2, 0.2, 0.2)
    return m


def temple_gate(seed=17):
    """A great temple gate across the corridor, rim to rim: two pillars glowing with glyphs, a lintel with a
    stepped crest and a gold sun disc, a bronze bell hanging from its middle and lanterns either side, all
    swinging slowly along the corridor. Modelled for the 72-wide corridor (feet beyond 36 from the middle);
    MapDecor stretches it to the real width. All of it stays above the rim (z 0), clear of the flight camera."""
    m = prop("TempleGate", Stone=STONE, StoneDark=STONE_DARK, StoneLight=STONE_LIGHT, Socket=SOCKET, Gold=GOLD, GoldDark=GOLD_DARK, Jade=JADE,
             Moss=MOSS, MossDark=MOSS_DARK, Vine=VINE, Leaf=LEAF, Root=BARK, Bell=BRONZE, BellRim=BRONZE_DARK, BellGlow=JADE,
             Lantern=BRONZE_DARK, Lamp=LAMP, Front="#ff00ff")
    rng = random.Random(seed)
    for side in (-1, 1):
        x = side * 41
        m.block("StoneDark", x, 0, 1.0, 8, 8, 2)
        m.block("Stone", x, 0, 16, 5.4, 5.4, 28)
        for z in (6, 12, 18, 24):
            m.block("StoneLight", x, 0, z, 5.8, 5.8, 0.5)
        for face in (-1, 1):
            for g in range(3):
                m.block("Jade", x + (0.6 if g % 2 else -0.6), face * 2.74, 4 + g * 5.0, 1.0, 0.1, 0.8)
        m.block("StoneLight", x, 0, 30.5, 7.4, 7.0, 1.4)
        for facing in (-1, 1):  # a carved face looking each way along the corridor
            stone_face(m, facing * 2.7, x, 22.0, 4.8, 7.0, eye_role="Jade", facing=facing)
        rubble(m, rng, x, 0, 6.5, 6, inner=0.8)
        limb(m, "Root", [(x - side * 2.6, 2.4, 29), (x - side * 3.0, 3.0, 20), (x - side * 2.9, 2.8, 10), (x - side * 4.2, 3.6, 0.2)], 0.7, 0.4)
    m.block("Stone", 0, 0, 32.9, 90, 6, 3.6)
    m.block("StoneLight", 0, 0, 31.0, 88, 6.4, 0.6)
    m.block("StoneDark", 0, 0, 35.3, 72, 5, 1.2)
    m.block("Stone", 0, 0, 36.7, 42, 4.4, 1.6)
    m.block("StoneLight", 0, 0, 38.9, 16, 4, 2.8)
    m.block("Gold", 0, 0, 40.5, 4, 2.4, 0.6)
    for face in (-1, 1):
        disc(m, "Gold", 0, face * 3.05, 33.2, 2.7, 0.3, 16, "xz")
        disc(m, "Jade", 0, face * 3.25, 33.2, 1.2, 0.2, 12, "xz")
        for x in range(-38, 39, 4):  # a band of glyphs along the lintel
            if abs(x) > 4:
                m.block("Jade", x, face * 3.03, 32.6 + (0.5 if (x // 4) % 2 else 0), 1.0, 0.1, 0.6)
    for x in range(-40, 41, 10):
        moss_on(m, rng, x + rng.uniform(-2, 2), rng.uniform(-1, 1), 34.7, rng.uniform(3, 6), 3.4, 3, "Moss" if x % 20 else "MossDark")
    for _ in range(12):  # vines off the lintel
        x = rng.uniform(-36, 36)
        if abs(x) < 6 or 15 < abs(x) < 21 or 27 < abs(x) < 33:
            continue
        hanging_vine(m, "Vine", x, rng.choice((-3.1, 3.1)), 31.0, rng.uniform(3, 7), 0.3, rng, "Leaf")
    # The bell: hook at z 30.6, chain, crown, body, lip and a glowing clapper.
    hinge = 30.6
    m.block("Bell", 0, 0, hinge - 1.5, 0.3, 0.3, 3.0)
    m.block("Bell", 0, 0, hinge - 3.3, 1.4, 1.4, 0.6)
    prism(m, "Bell", 0, 0, hinge - 8.4, hinge - 3.4, 2.9, 1.4, 10, 0.0)
    prism(m, "BellRim", 0, 0, hinge - 9.0, hinge - 8.2, 3.3, 3.0, 10, 0.0)
    for z in (hinge - 5.0, hinge - 6.8):
        prism(m, "BellRim", 0, 0, z - 0.15, z + 0.15, 2.45 if z > hinge - 6 else 2.75, 2.45 if z > hinge - 6 else 2.75, 10, 0.0)
    ball(m, "BellGlow", 0, 0, hinge - 9.6, 0.8, 8, 5)
    for x in (-18, 18, -30, 30):  # lanterns either side, on the same hinge line
        length = 4.0 if abs(x) < 25 else 2.6
        m.block("Lantern", x, 0, hinge - length / 2, 0.14, 0.14, length)
        top = hinge - length
        m.loft_z("Lantern", (top - 0.5, x, 0, 2.0, 2.0), (top, x, 0, 0.6, 0.6))
        for dx, dy in ((-0.65, -0.65), (0.65, -0.65), (0.65, 0.65), (-0.65, 0.65)):
            m.block("Lantern", x + dx, dy, top - 1.4, 0.2, 0.2, 1.8)
        m.block("Lantern", x, 0, top - 2.35, 1.7, 1.7, 0.25)
        m.block("Lamp", x, 0, top - 1.4, 1.12, 1.12, 1.6)
    m.block("Front", 0, 6, 34, 0.2, 0.2, 0.2)
    return m


ALL = [guardian_head, temple_ruin, jungle_fronds, jungle_tree, hanging_lantern, spirit_brazier, watcher_bloom, orrery, stone_hand,
       rune_circle, step_temple, guardian_statue, floating_monoliths, sky_lanterns, eclipse, face_fall, temple_gate]

# Where the props go: the same rules as Config/Decor's EclipseTemple (keep the two in step).
DECOR = dict(
    floor=dict(first=12, gap=(12, 22), side=(24, 34),
               props=[("prop_GuardianHead", 14, (1.5, 2.0)), ("prop_JungleTree", 10, (1.0, 1.3)), ("prop_JungleFronds", 12, (1.2, 1.6)),
                      ("prop_TempleRuin", 10, (1.2, 1.6)), ("prop_HangingLantern", 9, (1.2, 1.4)), ("prop_WatcherBloom", 8, (1.2, 1.5)),
                      ("prop_SpiritBrazier", 8, (1.2, 1.5)), ("prop_StoneHand", 6, (1.2, 1.5)), ("prop_Orrery", 4, (1.1, 1.3))],
               extras=dict(chance=0.7, spread=8, props=[("prop_JungleFronds", 5, (0.7, 1.0)), ("prop_TempleRuin", 2, (0.5, 0.7)),
                                                         ("prop_SpiritBrazier", 2, (0.7, 0.9))])),
    rim=dict(first=6, gap=(14, 24), chance=0.9, side=(64, 102),
             props=[("prop_JungleTree", 6, (1.9, 2.5)), ("prop_GuardianHead", 4, (2.0, 2.6)), ("prop_FloatingMonoliths", 3, (1.8, 2.3)),
                    ("prop_SkyLanterns", 3, (1.8, 2.2)), ("prop_TempleRuin", 2, (2.0, 2.6)), ("prop_JungleFronds", 2, (2.0, 2.6))]),
    overhead=[("prop_TempleGate", 260, 0, 1), ("prop_TempleGate", 780, 0, 1.05)],
    walls=[("prop_FaceFall", 80, 1), ("prop_FaceFall", 230, -1), ("prop_FaceFall", 400, 1), ("prop_FaceFall", 560, -1),
           ("prop_FaceFall", 720, 1), ("prop_FaceFall", 900, -1), ("prop_FaceFall", 1080, 1)],
    spots=[("prop_GuardianStatue", 60, 80, "rim", 0, 1.5, "middle"), ("prop_GuardianStatue", 480, -80, "rim", 0, 1.6, "middle"),
           ("prop_GuardianStatue", 880, 80, "rim", 0, 1.5, "middle"),
           ("prop_StepTemple", 150, -86, "rim", 0, 1.5, "middle"), ("prop_StepTemple", 620, 86, "rim", 0, 1.6, "middle"),
           ("prop_StepTemple", 1040, -86, "rim", 0, 1.5, "middle"),
           ("prop_Eclipse", 300, -170, "rim", 0, 2.4, "along"), ("prop_Eclipse", 940, 180, "rim", 0, 2.8, "along")]
          + [("prop_RuneCircle", d, x, "floor", yaw, 1.2) for d, x, yaw in ((40, -3, 20), (150, 4, 140), (270, -4, 70), (380, 3, 200),
                                                                              (500, -2, 300), (610, 4, 40), (740, -3, 110), (850, 2, 250),
                                                                              (960, -4, 330), (1090, 3, 80))],
)


# ---------------------------------------------------------------------- light


def eclipse_light(scene):
    """Dusk under an eclipse for the renders: low gold light and a deep teal-green fill, close to the game's
    Config/Lighting look for this world."""
    sun = bpy.data.objects["Sun"]
    sun.data.energy = 1.7
    sun.data.color = (1.0, 0.8, 0.6)
    sun.rotation_euler = (math.radians(-68), math.radians(30), math.radians(20))
    ambient = scene.world.node_tree.nodes["Background"]
    ambient.inputs["Color"].default_value = (0.55, 0.78, 0.7, 1)
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
    big = {"prop_StepTemple": (-60, -110, 0), "prop_GuardianStatue": (-20, -110, 0), "prop_Eclipse": (40, -200, 0),
           "prop_FaceFall": (60, -110, 44), "prop_TempleGate": (160, -170, 0), "prop_FloatingMonoliths": (10, -110, 0),
           "prop_SkyLanterns": (30, -110, 0)}
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
    mk.light_up(roots, GLOW_ROLES)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-400, -500, -0.01), (500, -500, -0.01), (500, 200, -0.01), (-400, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", CORRIDOR["FloorA"], False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = mk.player_block(stage)
    stars = mk.star_dome(stage, count=160, colours=("#ffffff", "#c8fff0"))
    bpy.context.view_layer.update()
    mk.set_sky(scene, SKY)
    eclipse_light(scene)

    everything = roots + [player]
    if stills:
        for model, root in zip(models, roots):
            name = model.name
            if name == "prop_TempleGate":
                mk.shoot_prop(scene, name, root, player, everything, (-0.15, 1.0, 0.25), 0.95, (1400, 700), 32)
            elif name == "prop_FaceFall":
                mk.shoot_prop(scene, name, root, player, everything, (0.6, 1.0, 0.1), 0.9, (700, 900), 40)
            elif name == "prop_Eclipse":
                mk.shoot_prop(scene, name, root, player, everything, (0.15, 1.0, 0.0), 1.3, (700, 700), 50)
            elif name in ("prop_StepTemple", "prop_GuardianStatue"):
                mk.shoot_prop(scene, name, root, player, everything, (0.55, 0.9, 0.35), 1.2, (700, 700), 50)
            else:
                mk.shoot_prop(scene, name, root, player, everything)
        player.location = (30, -40, 0)
        bpy.context.view_layer.update()
        small = [r for r in roots if mk.prop_of(r) not in big]
        mk.set_visible(everything, small + [player])
        kit.shoot(scene, "props", (98, 30, 24), (98, -40, 5), (1800, 700), 18)
        landmarks = [built[n] for n in ("prop_StepTemple", "prop_GuardianStatue", "prop_FloatingMonoliths", "prop_SkyLanterns")]
        mk.set_visible(everything, landmarks + [player])
        player.location = (0, -100, 0)
        bpy.context.view_layer.update()
        kit.shoot(scene, "landmarks", (-10, -30, 26), (-20, -115, 12), (1800, 800), 24)

    if videos:  # close up on what moves
        names = ("prop_HangingLantern", "prop_WatcherBloom", "prop_Orrery", "prop_SpiritBrazier", "prop_StoneHand", "prop_RuneCircle",
                 "prop_GuardianStatue", "prop_FloatingMonoliths", "prop_SkyLanterns", "prop_StepTemple", "prop_Eclipse")
        movers = [built[n] for n in names]
        mk.set_visible(everything, movers)
        saved = [(r, r.location.copy()) for r in movers]
        for k, root in enumerate(movers[:6]):
            root.location = (k * 13 - 32, 0, 0)
        for k, root in enumerate(movers[6:10]):
            root.location = ((k - 1.5) * 36, -45, 0)
        movers[10].location = (0, -150, 0)
        bpy.context.view_layer.update()
        entries = mk.motion_entries(movers, MOTION)
        mk.render_video(scene, RENDERS, "eclipse_motion", 120, 15,
                        lambda f: ((0, 62, 30), (0, -20, 9), 28, lambda t: mk.apply_motion(entries, t)), (1600, 800))
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

        mk.render_video(scene, RENDERS, "eclipse_flight", frames, 15, fly, (1600, 900))
        mk.reset_motion(entries)

    mk.clear([corridor, stars] + copies)
    mk.light_up(roots, GLOW_ROLES, 0)
    ground.hide_render = False
    for root in roots:
        for child in root.children:
            child.hide_render = False
    player.location = (-9, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "eclipse_temple_models.blend"))
    print("saved", HERE / "eclipse_temple_models.blend")
    for model in models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    # After "--": "stills" renders only the stills, "videos" only the videos; nothing, both.
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(stills=not args or "stills" in args, videos=not args or "videos" in args)
