"""Builds the Swamp's props and renders them (run with Blender in background mode).

    Blender -b -P build_swamp.py

Saves swamp_models.blend and renders to design/world/models_swamp/. Same parts and UVs as
build_forest.py, so the stud image sits on them the same way in Studio. The Swamp's animals
come later, in their own step.

The Swamp swaps Desert' sand and bones for murky green: big mossy trees with roots standing in
the water, reeds, lily pads and bubbling bog, with a few warm and glowing things (lanterns, a hut's
window, giant toadstools) so it doesn't read as one flat green from the flight camera. A fallen giant
tree lies across the corridor from rim to rim, the swamp's thing overhead (GAME_SPEC section 9).

1 Blender unit = 1 stud. Props stand on Z = 0 at their origin.
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
from build_forest import Model, add_frond_segment  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "models_swamp"

# The corridor's Swamp colours, from Config/Map biomeColors, for the preview stage only.
FLOOR = "#4e8466"
DIRT = "#5c4a34"
GRASS = "#6e9646"


def prop(name, **colours):
    return Model(f"prop_{name}", colours)


def strand(m, role, x, y, top, length, width=0.5):
    """Something hanging straight down from `top`: moss, vines, willow leaves."""
    m.block(role, x, y, top - length / 2, width, width, length)


def round_slab(m, role, x, y, z, size, thick):
    """A chunky disc: two crossed blocks, so it reads round from above without any curves."""
    m.block(role, x, y, z, size, size * 0.64, thick)
    m.block(role, x, y, z, size * 0.64, size, thick)


# ---------------------------------------------------------------------- trees


def swamp_tree(seed=3):
    """The map's signature: a bald cypress up on stilt roots, a flat dark crown and grey moss
    hanging off every edge."""
    m = prop("SwampTree", Bark="#5e4a3a", BarkDark="#44352a", Leaf="#4f9a3f", LeafDark="#3a7a34", Moss="#a9bd86")
    rng = random.Random(seed)
    # A trunk that swells out at the foot, as cypresses do in water.
    m.loft_z("Bark", (1.6, 0, 0, 3.4, 3.4), (4.5, 0, 0, 2.2, 2.2))
    m.loft_z("Bark", (4.5, 0, 0, 2.2, 2.2), (13.5, 0, 0, 1.6, 1.6))
    # The roots it stands on, arching out and down into the mud.
    for i in range(6):
        angle = i * math.tau / 6 + rng.uniform(-0.2, 0.2)
        dx, dy = math.cos(angle), math.sin(angle)
        knee = (dx * 2.6, dy * 2.6, 2.4)
        beam(m, "BarkDark", (dx * 0.6, dy * 0.6, 3.6), knee, 1.1, None, 0.9)
        beam(m, "BarkDark", knee, (dx * 4.2, dy * 4.2, 0), 0.9, None, 0.8)
        m.block("BarkDark", knee[0], knee[1], knee[2], 1.1, 1.1, 1.1)  # fills the elbow
    # Cypress knees: stubby points poking out of the water round about.
    for angle, reach, height in ((0.5, 5.4, 1.4), (2.3, 5, 1), (4.1, 5.8, 1.2)):
        x, y = math.cos(angle) * reach, math.sin(angle) * reach
        m.loft_z("Bark", (0, x, y, 0.8, 0.8), (height, x, y, 0.3, 0.3))
    # Branches up to the crown.
    for angle, length in ((0.4, 4.2), (2.6, 3.8), (4.4, 4)):
        start = (0, 0, 10.5)
        end = (math.cos(angle) * length, math.sin(angle) * length, 13.6)
        beam(m, "Bark", start, end, 0.8, None, 0.5)
    # A flat, layered crown, wider than tall.
    m.block("LeafDark", 0, 0, 14, 12, 11, 1.6)
    m.block("Leaf", 0.4, -0.3, 15.5, 10.5, 9.5, 1.8)
    m.block("Leaf", -0.6, 0.5, 17.1, 6.5, 6, 1.6)
    m.block("LeafDark", 4.6, 3.2, 14.9, 4.6, 4.4, 1.6)
    m.block("Leaf", -4.8, -2.8, 15.2, 4.4, 4.6, 1.8)
    # Moss hanging off the crown's edge, longer on the shady side.
    for i in range(16):
        angle = i * math.tau / 16 + rng.uniform(-0.08, 0.08)
        reach = rng.uniform(4.4, 5.4)
        x, y = math.cos(angle) * reach, math.sin(angle) * reach * 0.92
        strand(m, "Moss", x, y, 13.3, rng.uniform(1.8, 4.6), rng.uniform(0.45, 0.7))
    return m


def willow(seed=8):
    """A weeping willow: a leaning trunk and a dome of leaves that hangs nearly to the ground
    all round, like a curtain."""
    m = prop("Willow", Bark="#6b5340", Leaf="#7fb54a", LeafDark="#5f9a3c", LeafLight="#a0cc5c")
    rng = random.Random(seed)
    beam(m, "Bark", (0, 0, 0), (0.8, 0.3, 6), 2.8, None, 2)
    beam(m, "Bark", (0.8, 0.3, 6), (0.4, 0, 11), 2, None, 1.4)
    m.loft_z("Bark", (0, 0, 0, 4, 4), (0.8, 0, 0, 2.8, 2.8))
    # The dome.
    m.block("LeafDark", 0.4, 0, 11.2, 12, 12, 1.4)
    m.block("Leaf", 0.4, 0, 12.6, 11, 11, 1.6)
    m.block("Leaf", 0.4, 0, 14.1, 8, 8, 1.6)
    m.block("LeafLight", 0.4, 0, 15.4, 4.5, 4.5, 1.2)
    # The curtain: strips of leaves hanging from the dome's edge, every one a different length.
    for i in range(28):
        angle = i * math.tau / 28
        dx, dy = math.cos(angle), math.sin(angle)
        x, y = 0.4 + dx * 5.7, dy * 5.7
        role = ("Leaf", "LeafDark", "LeafLight")[i % 3]
        length = rng.uniform(4, 8.5)
        wide, thin = 1.3, 0.6  # wide along the dome's edge, thin across it
        m.block(role, x, y, 10.6 - length / 2, wide if abs(dy) > 0.7 else thin, wide if abs(dx) > 0.7 else thin, length)
    return m


# ---------------------------------------------------------------------- water and plants


def lilypads(seed=5):
    """A patch of dark water with lily pads and one big pink flower: the pop of colour on the floor."""
    m = prop("Lilypads", Water="#355f57", WaterLight="#4b7a6c", Pad="#7cc24a", PadDark="#5aa23a",
             Petal="#ff8fc8", PetalLight="#ffd1ea", Centre="#ffd84a")
    rng = random.Random(seed)
    m.block("Water", 0, 0, 0.1, 11, 7.5, 0.2)
    m.block("Water", 1.2, 0.4, 0.1, 7, 10, 0.2)
    m.block("WaterLight", -2.5, -1.6, 0.21, 2.4, 0.3, 0.04)  # glints
    m.block("WaterLight", 3.2, 2.8, 0.21, 1.8, 0.3, 0.04)
    for x, y, size in ((-3.2, 1.2, 2.8), (0.4, -1.8, 3.2), (2.8, 1.9, 2.4), (-1.0, 2.6, 1.8), (3.9, -1.9, 1.7)):
        round_slab(m, "Pad", x, y, 0.32, size, 0.18)
        # A notch, the lily pad's tell, made by a sliver of water cutting in.
        m.block("Water", x + size * 0.28, y, 0.36, size * 0.44, 0.22, 0.2)
        m.block("PadDark", x, y, 0.43, size * 0.18, size * 0.18, 0.06)
    # The flower, on the biggest pad: two rings of petals opening outwards.
    fx, fy, fz = 0.2, -1.8, 0.4
    for i in range(8):
        angle = i * math.tau / 8 + rng.uniform(-0.05, 0.05)
        dx, dy = math.cos(angle), math.sin(angle)
        beam(m, "Petal", (fx + dx * 0.3, fy + dy * 0.3, fz + 0.1), (fx + dx * 1.4, fy + dy * 1.4, fz + 1.1), 0.75, 0.2, 0.45)
        angle += math.tau / 16
        dx, dy = math.cos(angle), math.sin(angle)
        beam(m, "PetalLight", (fx + dx * 0.2, fy + dy * 0.2, fz + 0.2), (fx + dx * 0.75, fy + dy * 0.75, fz + 1.5), 0.6, 0.18, 0.35)
    m.block("Centre", fx, fy, fz + 0.45, 0.7, 0.7, 0.5)
    return m


def cattails(seed=11):
    """A clump of reeds with brown sausage heads, the swamp's grass."""
    m = prop("Cattails", Stalk="#6aa03c", Blade="#86b84a", Head="#6b3f22", Mud="#4e3e2c")
    rng = random.Random(seed)
    m.loft_z("Mud", (0, 0, 0, 3, 3), (0.4, 0, 0, 2.4, 2.4))
    for i in range(7):
        angle = i * math.tau / 7 + rng.uniform(-0.3, 0.3)
        base = (math.cos(angle) * 0.7, math.sin(angle) * 0.7, 0.2)
        lean = rng.uniform(0.3, 1.1)
        height = rng.uniform(5.5, 8)
        top = (math.cos(angle) * lean, math.sin(angle) * lean, height)
        beam(m, "Stalk", base, top, 0.28)
        # The head sits a little under the tip, and the tip carries on as a spike.
        t = 0.82
        hx, hy, hz = (base[0] + (top[0] - base[0]) * t, base[1] + (top[1] - base[1]) * t, base[2] + (top[2] - base[2]) * t)
        m.block("Head", hx, hy, hz, 0.75, 0.75, 1.9)
    # Long flat blades bending out.
    for i in range(9):
        angle = i * math.tau / 9 + rng.uniform(-0.2, 0.2)
        dx, dy = math.cos(angle), math.sin(angle)
        length = rng.uniform(2.6, 3.8)
        rise = rng.uniform(3.4, 5)
        add_frond_segment(m, "Blade", dx, dy, 0.3, 0.3, 0.12, 0.6, length * 0.6, rise, 0.1, 0.5)
        add_frond_segment(m, "Blade", dx, dy, length * 0.6, rise, 0.1, 0.5, length, rise * 0.75, 0.08, 0.1)
    return m


def mossy_log():
    """A fallen hollow log, moss on its back and orange toadstools growing out of it."""
    m = prop("MossyLog", Bark="#6b4f38", BarkDark="#4f3a29", Hollow="#2a1f17", Rings="#c9a46a",
             Moss="#78b048", Cap="#ff8a3a", Stem="#f2e6c8")
    m.loft_x("Bark", (-5, 0, 1.5, 3, 3), (5, 0, 1.45, 2.8, 2.8))
    for x in (-3.2, 0.4, 3.4):  # rough bark bands
        m.block("BarkDark", x, 0, 1.5, 0.5, 3.1, 3.1)
    # One end cut, the other end hollow.
    m.block("Rings", 5.03, 0, 1.45, 0.1, 2.3, 2.3)
    m.block("BarkDark", 5.1, 0, 1.45, 0.1, 0.6, 0.6)
    m.block("Hollow", -5.03, 0, 1.5, 0.1, 2.1, 2.1)
    # Moss along the top and spilling down one side.
    m.block("Moss", -0.6, 0, 3.05, 8.2, 2.4, 0.3)
    m.block("Moss", -2.5, 1.45, 2.4, 3.2, 0.3, 1.2)
    m.block("Moss", 1.8, -1.45, 2.6, 2.4, 0.3, 0.8)
    # A broken branch.
    beam(m, "Bark", (1.2, 0.6, 2.6), (2.2, 2.2, 4.8), 0.9, None, 0.6)
    for x, y, height, cap in ((-3, -0.4, 3.9, 1.6), (-2, 0.5, 3.6, 1.1), (3.6, 0.2, 3.7, 1.3)):
        m.loft_z("Stem", (3.1, x, y, cap * 0.3, cap * 0.3), (height, x, y, cap * 0.25, cap * 0.25))
        m.loft_z("Cap", (height - 0.05, x, y, cap, cap), (height + cap * 0.38, x, y, cap * 0.5, cap * 0.5))
    return m


def glow_shrooms():
    """Giant toadstools in purple and teal: bright enough to read in the murk."""
    m = prop("GlowShrooms", Stem="#e6ecd2", Gill="#d6c6f2", CapPurple="#a35cff", CapTeal="#36d6b4", Spot="#f2fff8")
    for x, y, height, cap, role in ((0, 0, 5.2, 5.6, "CapPurple"), (3.6, 1.6, 3.2, 3.6, "CapTeal"), (-2.6, 2.4, 2, 2.4, "CapPurple"), (1.6, -2.8, 1.4, 1.8, "CapTeal")):
        m.loft_z("Stem", (0, x, y, cap * 0.3, cap * 0.3), (height, x, y, cap * 0.22, cap * 0.22))
        m.block("Gill", x, y, height + 0.05, cap * 0.86, cap * 0.86, 0.1)
        m.loft_z(role, (height + 0.1, x, y, cap, cap), (height + cap * 0.22, x, y, cap * 0.92, cap * 0.92))
        m.loft_z(role, (height + cap * 0.22, x, y, cap * 0.92, cap * 0.92), (height + cap * 0.45, x, y, cap * 0.45, cap * 0.45))
        for dx, dy, s in ((0.2, -0.15, 0.16), (-0.22, 0.18, 0.12), (0.05, 0.3, 0.1)):
            m.block("Spot", x + cap * dx, y + cap * dy, height + cap * 0.36, cap * s, cap * s, cap * 0.08)
        # Spots on the cap's sides too, so it reads from the corridor floor.
        m.block("Spot", x + cap * 0.48, y, height + cap * 0.16, cap * 0.04, cap * 0.18, cap * 0.12)
        m.block("Spot", x, y - cap * 0.48, height + cap * 0.18, cap * 0.14, cap * 0.04, cap * 0.1)
    return m


def bog_pool(seed=13):
    """A pool of green ooze in a ring of mud, bubbles coming up through it."""
    m = prop("BogPool", Mud="#5b4632", MudDark="#46362a", Ooze="#7d9a34", Bubble="#b4d652")
    rng = random.Random(seed)
    m.block("Ooze", 0, 0, 0.2, 9, 6.5, 0.4)
    m.block("Ooze", 0.5, 0.3, 0.2, 6.5, 8.4, 0.4)
    # Mud banks round the edge, in uneven lumps.
    for i in range(14):
        angle = i * math.tau / 14
        x, y = math.cos(angle) * 5, math.sin(angle) * 4.5
        size = rng.uniform(1.4, 2.4)
        m.block("Mud" if i % 3 else "MudDark", x, y, size * 0.25, size, size, size * 0.5)
    # Bubbles: cubes half sunk in the ooze, and one just bursting as a ring.
    for x, y, size in ((-1.6, -0.8, 1.4), (1.2, 1.4, 1.0), (0.4, -2.2, 0.7), (2.6, -0.6, 0.5), (-2.8, 1.6, 0.6)):
        m.block("Bubble", x, y, 0.4 + size * 0.2, size, size, size * 0.9)
        m.block("Ooze", x, y, 0.4 + size * 0.66, size * 0.4, size * 0.4, 0.06)  # highlight
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        m.block("Bubble", -0.4 + dx * 0.8, 2.6 + dy * 0.8, 0.5, 0.5 if dx else 1.1, 1.1 if dx else 0.5, 0.25)
    # Bubbles in the air above, rising.
    m.block("Bubble", -1.4, -0.6, 2.2, 0.5, 0.5, 0.5)
    m.block("Bubble", -1.1, -0.9, 3.3, 0.32, 0.32, 0.32)
    return m


# ---------------------------------------------------------------------- built things


def stilt_hut():
    """A ramshackle hut up on stilts, with a porch, a ladder and a warm window. Big enough to
    read from the rim."""
    m = prop("StiltHut", Wood="#8a6a44", WoodDark="#5e4630", Plank="#a88456", Thatch="#c9a75a",
             ThatchDark="#a88a44", Window="#ffd45a", Door="#3a2a1e")
    deck = 6
    for x, y in ((-4, -4), (4, -4), (-4, 4), (4, 4), (-4, 7.5), (4, 7.5)):
        m.block("WoodDark", x, y, deck / 2, 0.8, 0.8, deck)
    m.block("Plank", 0, 1.75, deck + 0.3, 10, 12.5, 0.6)  # the deck, porch to the front (+Y)
    for y in range(-4, 8, 2):
        m.block("WoodDark", 0, y + 0.5, deck + 0.62, 10, 0.12, 0.05)
    # The hut itself, with plank lines across it.
    m.block("Wood", 0, -0.5, deck + 2.9, 7, 6.5, 4.6)
    for z in (deck + 1.4, deck + 2.6, deck + 3.8):
        m.block("WoodDark", 0, -0.5, z, 7.1, 6.6, 0.15)
    m.block("Door", -1.3, 2.78, deck + 2.3, 1.8, 0.1, 3.4)
    m.block("Window", 1.9, 2.78, deck + 3, 1.6, 0.1, 1.4)
    m.block("WoodDark", 1.9, 2.82, deck + 3, 0.16, 0.06, 1.4)
    m.block("WoodDark", 1.9, 2.82, deck + 3, 1.6, 0.06, 0.16)
    m.block("Window", -3.53, -0.8, deck + 3, 0.1, 1.4, 1.2)
    # A shaggy thatched roof, overhanging, slightly crooked.
    m.loft_z("Thatch", (deck + 5.2, 0.2, -0.5, 9.6, 9), (deck + 7.6, 0, -0.5, 4.4, 4))
    m.loft_z("ThatchDark", (deck + 7.6, 0, -0.5, 4.4, 4), (deck + 9, -0.2, -0.6, 1, 1))
    for i in range(10):
        x = -4.3 + i * 0.95
        m.block("ThatchDark", x, 4.05, deck + 4.9 - (i % 3) * 0.25, 0.7, 0.4, 0.8 + (i % 3) * 0.4)
    # Porch rail and posts.
    for x in (-4.6, 4.6):
        m.block("WoodDark", x, 5.5, deck + 1.2, 0.3, 4, 0.25)
    m.block("WoodDark", 2.3, 7.8, deck + 1.2, 4.6, 0.3, 0.25)
    for x, y in ((-4.6, 7.8), (4.6, 7.8), (-4.6, 3.6), (4.6, 3.6)):
        m.block("WoodDark", x, y, deck + 0.75, 0.35, 0.35, 1.5)
    # A ladder down from the porch's open corner.
    for x in (-3.9, -2.3):
        beam(m, "Wood", (x, 8.6, 0), (x, 7.9, deck + 0.6), 0.3)
    for i in range(5):
        t = (i + 0.6) / 5.6
        m.block("Plank", -3.1, 8.6 - 0.7 * t, deck * t, 1.8, 0.25, 0.22)
    # A lantern hanging off the roof's corner.
    m.block("WoodDark", 4.6, 4.2, deck + 4.6, 0.12, 0.12, 0.9)
    m.block("Window", 4.6, 4.2, deck + 3.8, 0.55, 0.55, 0.7)
    m.block("WoodDark", 4.6, 4.2, deck + 4.2, 0.75, 0.75, 0.15)
    return m


def swamp_lantern():
    """A crooked post with a lantern hanging off it, a warm light down in the murk."""
    m = prop("SwampLantern", Wood="#6b5340", Metal="#3b3530", Glow="#ffd34d", Mud="#4e3e2c")
    m.loft_z("Mud", (0, 0, 0, 1.8, 1.8), (0.3, 0, 0, 1.3, 1.3))
    beam(m, "Wood", (0, 0, 0), (0.4, 0.1, 4), 0.7, None, 0.6)
    beam(m, "Wood", (0.4, 0.1, 4), (0.1, 0, 7.4), 0.6, None, 0.5)
    beam(m, "Wood", (0.1, 0, 7.2), (2.2, 0, 7.6), 0.4)
    m.block("Metal", 2.0, 0, 7.05, 0.1, 0.1, 0.9)
    # The lantern: a cap, glass that glows, a base.
    m.block("Metal", 2.0, 0, 6.5, 0.95, 0.95, 0.2)
    m.block("Glow", 2.0, 0, 5.85, 0.75, 0.75, 1.1)
    for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        m.block("Metal", 2.0 + dx * 0.38, dy * 0.38, 5.85, 0.12, 0.12, 1.1)
    m.block("Metal", 2.0, 0, 5.22, 0.85, 0.85, 0.16)
    return m


def log_bridge(seed=17):
    """A giant tree that fell across the corridor, rim to rim, with vines and moss hanging under it.
    The trunk runs along X, centred on the origin, its underside on Z = 0 (the rim's grass)."""
    m = prop("LogBridge", Bark="#5e4a3a", BarkDark="#44352a", Rings="#c9a46a", Moss="#78b048",
             Vine="#4f8f34", Leaf="#6fbf44", HangMoss="#a9bd86")
    rng = random.Random(seed)
    # The trunk, thick at the roots (-X) and tapering to a broken top (+X), bottom kept flat.
    spans = [(-56, 7.2), (-20, 6.4), (20, 5.6), (56, 4.8)]
    for (x0, d0), (x1, d1) in zip(spans, spans[1:]):
        m.loft_x("Bark", (x0, 0, d0 / 2, d0, d0), (x1, 0, d1 / 2, d1, d1))
    for x in range(-50, 56, 9):  # bark bands
        d = 7.2 - (x + 56) / 112 * 2.4
        m.block("BarkDark", x, 0, d / 2, 0.8, d + 0.12, d + 0.12)
    # The root plate at the fallen end, roots splayed out.
    m.block("BarkDark", -57, 0, 4.2, 2.2, 10, 8.4)
    for i in range(7):
        angle = i * math.tau / 7 + rng.uniform(-0.15, 0.15)
        dy, dz = math.cos(angle), math.sin(angle)
        beam(m, "BarkDark", (-57, dy * 2.5, 4.2 + dz * 2.5), (-60 - rng.uniform(0, 2), dy * 6.5, max(4.2 + dz * 6.5, 0.4)), 1.2, None, 0.5)
    # The snapped top: jagged splinters and a stub of a branch.
    m.block("Rings", 56.05, 0, 2.4, 0.1, 3.8, 3.8)
    for dy, dz, length in ((-1.4, 1.2, 2.4), (0.6, 3.6, 1.6), (1.6, 1.6, 3)):
        m.loft_x("Bark", (56, dy, dz, 1.4, 1.4), (56 + length, dy, dz + 0.3, 0.2, 0.2))
    beam(m, "Bark", (34, 1.2, 4.2), (40, 6, 9), 1.4, None, 0.7)
    m.block("Leaf", 40, 6, 9.8, 4, 4, 2)
    # Moss on top and draped over the sides.
    for x in range(-48, 50, 7):
        d = 7.2 - (x + 56) / 112 * 2.4
        m.block("Moss", x + rng.uniform(-1, 1), 0, d + 0.2, rng.uniform(4, 6.5), d * 0.85, 0.5)
        side = rng.choice((-1, 1))
        m.block("Moss", x + rng.uniform(-1, 1), side * d / 2, d * 0.72, rng.uniform(2, 3.5), 0.4, d * 0.5)
    # Vines hanging into the corridor (its walls are 36 studs either side of the middle), with leaves.
    for i in range(18):
        x = -32 + i * 64 / 17 + rng.uniform(-1, 1)
        y = rng.choice((-1, 1)) * rng.uniform(1.2, 2.6)
        length = rng.uniform(4, 14)
        strand(m, "Vine", x, y, 0.4, length, 0.4)
        for k in range(int(length // 3)):
            z = -1.6 - k * 3 + rng.uniform(-0.5, 0.5)
            side = 1 if k % 2 else -1
            m.block("Leaf", x + side * 0.45, y, z, 0.9, 0.3, 0.6)
        m.block("Leaf", x, y, 0.4 - length - 0.3, 0.9, 0.9, 0.6)
    # Grey moss in clumps between the vines, like the cypress's.
    for i in range(12):
        x = -30 + i * 60 / 11 + rng.uniform(-1.5, 1.5)
        for k in range(3):
            strand(m, "HangMoss", x + k * 0.6 - 0.6, rng.uniform(-2.4, 2.4), 0.4, rng.uniform(2, 5.5), 0.55)
    return m


# ---------------------------------------------------------------------- preview stage


def corridor_stage(stage, length=300):
    """A stretch of corridor in the Swamp's colours, to see the props where they'll stand. Not
    exported. Floor top Z = 0, walls 44 high with their inner faces 36 from the middle (Config/Map)."""
    m = Model("SwampCorridor", {"FloorA": FLOOR, "FloorB": "#45765b", "Dirt": DIRT, "DirtB": "#51412e", "Grass": GRASS})
    m.bone = "Root"
    for ix in range(9):
        for iy in range(length // 8):
            role = "FloorA" if (ix + iy) % 2 == 0 else "FloorB"
            m.block(role, -32 + ix * 8, -iy * 8 - 4, -0.5, 8, 8, 1)
    rng = random.Random(7)
    for side in (-1, 1):
        for iz in range(6):
            for iy in range(length // 8):
                role = "Dirt" if (iz + iy) % 2 == 0 else "DirtB"
                m.block(role, side * 36.5 + side * 35.5, -iy * 8 - 4, iz * 7 + 3.5, 72, 8, 7)
        m.block("Grass", side * 72, -length / 2, 45, 72, length, 2)
        m.block("Grass", side * 35.25, -length / 2, 42, 1.5, length, 4)
        y = 0
        while y < length:
            drip = rng.choice((0, 4, 4, 8, 8, 12, 16))
            if drip:
                m.block("Grass", side * 35.25, -y - 4, 40 - drip / 2, 1.5, 8, drip)
            y += 8
    return m.build(stage)


def place_copy(source, collection, location, yaw, scale):
    """A linked copy of a built prop: shares its meshes, so the stage stays light."""
    root = bpy.data.objects.new(source.name + "_copy", None)
    collection.objects.link(root)
    for child in source.children:
        copy = child.copy()
        copy.hide_render = False
        collection.objects.link(copy)
        copy.parent = root
    root.location = location
    root.rotation_euler = (0, 0, yaw)
    root.scale = (scale, scale, scale)
    return root


def decorate_stage(stage, built, length=300, seed=21):
    """The corridor's props laid out like Config/Decor's Swamp rules, so the render shows the real mix."""
    rng = random.Random(seed)

    def pick(table):
        total = sum(w for _, w, _ in table)
        roll = rng.uniform(0, total)
        for name, weight, scale in table:
            roll -= weight
            if roll <= 0:
                return name, scale
        return table[-1][0], table[-1][2]

    floor = [("prop_SwampTree", 18, (1.4, 1.8)), ("prop_Cattails", 16, (1.3, 1.8)), ("prop_Lilypads", 14, (1.2, 1.6)),
             ("prop_MossyLog", 12, (1.3, 1.7)), ("prop_GlowShrooms", 10, (1.2, 1.6)), ("prop_BogPool", 10, (1.2, 1.5)),
             ("prop_Willow", 10, (1.3, 1.6)), ("prop_SwampLantern", 8, (1.4, 1.7))]
    extras = [("prop_Cattails", 4, (0.8, 1.2)), ("prop_Lilypads", 3, (0.7, 1)), ("prop_GlowShrooms", 2, (0.6, 0.9))]
    rim = [("prop_SwampTree", 5, (2, 2.6)), ("prop_Willow", 4, (2, 2.5)), ("prop_StiltHut", 2, (1.6, 2)), ("prop_GlowShrooms", 2, (2.2, 2.8)),
           ("prop_Cattails", 2, (2.2, 2.8)), ("prop_BogPool", 1, (2, 2.6))]
    copies = []

    def put(table, x, z, y):
        name, (low, high) = pick(table)
        copies.append(place_copy(built[name], stage, (x, -y, z), rng.uniform(0, math.tau), rng.uniform(low, high)))

    y = 10
    while y < length - 14:
        side = rng.choice((-1, 1))
        x = side * rng.uniform(20, 27)
        put(floor, x, 0, y)
        if rng.random() < 0.6:
            put(extras, side * min(max(abs(x) + rng.uniform(-8, 8), 16), 33), 0, y + rng.uniform(-8, 8))
        y += rng.uniform(12, 24)
    y = 6
    while y < length:
        for side in (-1, 1):
            if rng.random() < 0.85:
                put(rim, side * rng.uniform(52, 94), 44, y)
        y += rng.uniform(18, 30)
    bridge = place_copy(built["prop_LogBridge"], stage, (0, -170, 44), math.radians(6), 1)
    return copies + [bridge]


def swamp_sky(scene, hex_colour):
    sky = [n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND" and n.name != "Background"][0]
    sky.inputs["Color"].default_value = (*kit.srgb_to_linear(hex_colour), 1)


# ---------------------------------------------------------------------- scene and renders


def main():
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    props = bpy.data.collections.new("Props")
    stage = bpy.data.collections.new("Preview stage")
    for col in (props, stage):
        scene.collection.children.link(col)

    prop_models = [swamp_tree(), willow(), lilypads(), cattails(), mossy_log(), glow_shrooms(), bog_pool(),
                   stilt_hut(), swamp_lantern(), log_bridge()]
    built = {}
    prop_roots = []
    x = 0
    for model in prop_models:
        root = model.build(props)
        root.location = (x, -40, 0)
        built[model.name] = root
        prop_roots.append(root)
        x += 24
    built["prop_LogBridge"].location = (100, -110, 0)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-300, -400, -0.01), (400, -400, -0.01), (400, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", FLOOR, False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = Model("Player", {"Skin": "#3f4553"})
    player.bone = "Root"
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    player_root = player.build(stage)
    bpy.context.view_layer.update()

    everything = prop_roots + [player_root]
    swamp_sky(scene, "#b9d4a6")
    for model, root in zip(prop_models, prop_roots):
        low, high = kit.bounds(root)
        player_root.location = Vector((low.x - 3, (low.y + high.y) / 2 + 2, 0))
        bpy.context.view_layer.update()
        kit.set_visible(everything, [root, player_root])
        centre = (low + high) / 2
        reach = max((high - low).length, 7)
        if model.name == "prop_LogBridge":
            # Lifted to rim height, as in the game, so the vines hang free.
            root.location.z = 44
            bpy.context.view_layer.update()
            low, high = kit.bounds(root)
            centre = (low + high) / 2
            kit.shoot(scene, model.name, centre + Vector((-30, 90, -14)), centre, (1400, 700), 32)
            root.location.z = 0
        else:
            kit.shoot(scene, model.name, centre + Vector((0.5, 0.9, 0.42)) * reach * 1.25, centre, (600, 600), 50)
    player_root.location = (-9, -40, 0)
    bpy.context.view_layer.update()
    lineup = prop_roots[:-1] + [player_root]
    kit.set_visible(everything, lineup)
    kit.shoot(scene, "props", (100, 40, 34), (100, -40, 5), (1800, 700), 22)

    # The whole look: a stretch of Swamp corridor with its props, from about where the flight camera rides.
    ground.hide_render = True
    kit.set_visible(everything, [])
    corridor = corridor_stage(stage)
    copies = decorate_stage(stage, built)
    stage_parts = [corridor] + copies
    kit.shoot(scene, "corridor_flight", (0, 40, 70), (0, -160, 10), (1600, 900), 24)
    kit.shoot(scene, "corridor_floor", (-14, -60, 12), (6, -170, 8), (1600, 900), 22)

    # Keep the .blend tidy: the stage goes, the props stay where they were lined up.
    for root in stage_parts:
        for child in list(root.children):
            bpy.data.objects.remove(child)
        bpy.data.objects.remove(root)
    ground.hide_render = False
    kit.set_visible(everything, everything)
    player_root.location = (-9, -40, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "swamp_models.blend"))
    print("saved", HERE / "swamp_models.blend")
    for model in prop_models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    main()
