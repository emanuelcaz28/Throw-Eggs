"""Builds The Abyss's props and renders them (Blender, background mode). The monsters come later.

    Blender -b -P build_abyss.py

Saves abyss_models.blend and renders to design/world/models_abyss/, with a stretch of corridor.

The Abyss, map 7, is the bottom of the ocean: the world of Spiral Gary, Derpichthys, Megalodon and Mosasaurus.
It is the most decorated world so far, on the owner's request: deep blue sand and dark abyssal rock, packed
with reef life in warm colours (branching coral, brain coral, tube sponges, anemones, giant clams, tube worms,
urchins and starfish, kelp forests and sea grass) and bioluminescent glow for the dark (jellyfish floating
overhead, glowing anemone tips, pearls and sea glass, hydrothermal vents). Set pieces: sunken shipwrecks and
giant ammonite shells on the rims, reefs tumbling down the corridor walls, coral arches over it, an anchor
and a treasure chest on the floor, flat shell patches across the middle where the eggs land.

Glowing parts (Glow, Shine, Ember) get the Neon material in the game (shared/Roles.luau). Props that must
face a certain way (WallReef, CoralArch) carry a small Front part that MapDecor uses to turn them, then removes.
1 Blender unit = 1 stud, props stand on Z = 0 at their origin.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_desert import beam  # noqa: E402
from build_forest import Model  # noqa: E402
from build_shadow_bog import dome, limb, moss_beard  # noqa: E402
from build_swamp import place_copy, strand  # noqa: E402
from build_volcano import hide_markers, prism, set_sky, set_visible  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "models_abyss"

GLOW_ROLES = {"Glow", "Shine", "Ember"}
kit.NO_STUDS.update(GLOW_ROLES)

# Shared colours, so every prop's sand, rock and reef match.
SAND, SAND_LIGHT = "#4a89b3", "#6aa6cb"  # a little lighter than the corridor floor
ROCK, ROCK_DARK = "#3f5675", "#2f4160"
CORAL_PINK, CORAL_PINK_TIP = "#ff6f91", "#ffb3c6"
CORAL_ORANGE, CORAL_ORANGE_TIP = "#ff8f3c", "#ffc27a"
CORAL_YELLOW, CORAL_PURPLE = "#ffd447", "#a06bff"
KELP, KELP_LEAF, KELP_DARK, BLADDER = "#6f7a2c", "#b3a441", "#525c22", "#e0be4c"
SEAGRASS, SEAGRASS_DARK = "#3fbf9f", "#2a907a"
SHELL, SHELL_SHADE, SHELL_STRIPE = "#f4dfc4", "#dcb991", "#b9764a"
GLOW_CYAN, SHINE_PINK = "#5cf4ff", "#ff62d6"

# The corridor's Abyss colours (Config/Map biomeColors), for the preview stage only.
CORRIDOR = {"FloorA": "#3b78a0", "FloorB": "#336c92", "Dirt": "#1d3557", "DirtB": "#192e4c", "Grass": "#33a3a0"}
SKY = "#2f6fa8"


def prop(name, **colours):
    return Model(f"prop_{name}", colours)


def transform(m, matrix, offset=(0, 0, 0)):
    """Turns and moves everything built so far, for props that lie tilted (a sunken ship, a buried anchor)."""
    shift = Vector(offset)
    for verts, _ in m.parts.values():
        verts[:] = [tuple(matrix @ Vector(v) + shift) for v in verts]


def coral_branch(m, role, tip_role, start, direction, length, width, depth, rng, children=(2, 3)):
    """A branching coral limb: it forks again and again, every tip a fat rounded nub."""
    start, direction = Vector(start), Vector(direction).normalized()
    end = start + direction * length
    beam(m, role, tuple(start), tuple(end), width, None, width * 0.8)
    if depth == 0:
        m.block(tip_role, *end, width * 1.15, width * 1.15, width * 1.15)
        return
    m.block(role, *end, width * 0.8, width * 0.8, width * 0.8)
    for _ in range(rng.randint(*children)):
        side = direction.cross(Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.2, 0.2))))
        if side.length < 1e-3:
            side = Vector((1, 0, 0))
        turned = Matrix.Rotation(math.radians(rng.uniform(24, 42)), 3, side.normalized()) @ direction
        turned = (turned + Vector((0, 0, 0.35))).normalized()
        coral_branch(m, role, tip_role, end, turned, length * rng.uniform(0.65, 0.82), width * 0.74, depth - 1, rng, children)


def rock_base(m, rng, w, d, h, role="Rock", dark="RockDark"):
    m.loft_z(role, (0, 0, 0, w, d), (h, rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), w * 0.7, d * 0.7))
    m.block(dark, w * 0.3, -d * 0.25, h * 0.35, w * 0.35, d * 0.35, h * 0.7)


def sand_patch(m, w, d, role="Sand"):
    m.loft_z(role, (0, 0, 0, w, d), (0.35, 0, 0, w * 0.8, d * 0.8))


def brain_dome(m, x, y, z, a, b, height, ridge="Brain", groove="Groove", seed=1):
    """A brain coral: rows of rounded ridges winding over a dark core, so the grooves show between them."""
    rng = random.Random(seed)
    m.loft_z(groove, (z, x, y, a * 1.7, b * 1.7), (z + height * 0.85, x, y, a * 0.6, b * 0.6))
    rows = max(3, int(b * 2 / 0.85))
    for i in range(rows):
        yy = -b + (i + 0.5) * 2 * b / rows
        phase = rng.uniform(0, math.tau)
        steps = max(2, int(a * 2 / 0.8))
        for k in range(steps):
            xx = -a + (k + 0.5) * 2 * a / steps
            share = 1 - (xx / a) ** 2 - (yy / b) ** 2
            if share <= 0.02:
                continue
            h = height * math.sqrt(share)
            wobble = 0.22 * math.sin(xx * 1.8 + phase)
            m.block(ridge, x + xx, y + yy + wobble, z + h / 2, 2 * a / steps + 0.06, 2 * b / rows * 0.78, h)


def anemone(m, x, y, s, rng, column="Column", tentacle="Tentacle", tip="Shine", z=0.0):
    """A sea anemone: a squat column crowned with curling tentacles whose tips glow."""
    prism(m, column, x, y, z, z + 1.6 * s, 0.85 * s, 1.1 * s, 10, rng.uniform(0, 1))
    m.loft_z(column, (z + 1.6 * s, x, y, 1.7 * s, 1.7 * s), (z + 1.75 * s, x, y, 1.2 * s, 1.2 * s))
    for ring, count, reach, lift in ((1.0, 14, 1.25, 0.9), (0.55, 8, 0.8, 1.2)):
        for k in range(count):
            a = k * math.tau / count + rng.uniform(-0.12, 0.12) + ring
            base = Vector((x + math.cos(a) * 0.85 * s * ring, y + math.sin(a) * 0.85 * s * ring, z + 1.65 * s))
            mid = base + Vector((math.cos(a) * reach * s * 0.6, math.sin(a) * reach * s * 0.6, lift * s * 0.7))
            end = mid + Vector((math.cos(a) * reach * s * 0.45, math.sin(a) * reach * s * 0.45, lift * s * 0.35))
            limb(m, tentacle, [tuple(base), tuple(mid), tuple(end)], 0.34 * s, 0.2 * s, joints=False)
            m.block(tip, *end, 0.3 * s, 0.3 * s, 0.3 * s)


def worms(m, spots, tube="Tube", plume="Plume"):
    """Giant tube worms: white tubes topped with red feathery plumes. spots: (x, y, height, radius, lean)."""
    for x, y, h, r, (lx, ly) in spots:
        prism(m, tube, x, y, 0, h, r, r * 0.9, 6, 0.2, (lx, ly))
        m.loft_z(plume, (h, x + lx, y + ly, r * 1.3, r * 1.3), (h + 0.9, x + lx * 1.1, y + ly * 1.1, r * 2.6, r * 2.6))
        m.loft_z(plume, (h + 0.9, x + lx * 1.1, y + ly * 1.1, r * 2.6, r * 2.6), (h + 1.3, x + lx * 1.15, y + ly * 1.15, r * 1.4, r * 1.4))


def urchin(m, x, y, z, r, core="Urchin", spike="Spike"):
    """A sea urchin: a dark ball bristling with long spines (golden-spiral directions, so they spread evenly)."""
    m.block(core, x, y, z, r * 1.5, r * 1.5, r * 1.3)
    centre = Vector((x, y, z))
    count = 18
    for i in range(count):
        t = (i + 0.5) / count
        up = 1 - 2 * t
        if up < -0.4:
            continue  # none pointing into the ground
        ring = math.sqrt(1 - up * up)
        a = i * math.pi * (3 - math.sqrt(5))
        d = Vector((ring * math.cos(a), ring * math.sin(a), up))
        beam(m, spike, tuple(centre + d * r * 0.6), tuple(centre + d * r * 2.1), 0.24, None, 0.03)


def starfish(m, x, y, z, s, turn, role="Starfish", dot="StarDot"):
    """A starfish lying flat: five tapering arms and a few dots."""
    m.block(role, x, y, z + 0.15 * s, 0.9 * s, 0.9 * s, 0.3 * s)
    for k in range(5):
        a = turn + k * math.tau / 5
        end = (x + math.cos(a) * 1.5 * s, y + math.sin(a) * 1.5 * s, z + 0.12 * s)
        beam(m, role, (x, y, z + 0.15 * s), end, 0.7 * s, 0.3 * s, 0.2 * s)
        m.block(dot, x + math.cos(a) * 0.7 * s, y + math.sin(a) * 0.7 * s, z + 0.3 * s, 0.18 * s, 0.18 * s, 0.06 * s)


def kelp_stalk(m, x, y, height, phase, rng, stalk="Kelp", leaf="KelpLeaf", bladder="Bladder", width=0.5):
    """One tall kelp stalk swaying as it rises, a leaf blade and an air bladder at every joint."""
    points = []
    z = 0.0
    while z < height:
        points.append((x + 0.9 * math.sin(z / 4 + phase), y + 0.6 * math.cos(z / 5 + phase), z))
        z += 2.0
    points.append((x + 0.9 * math.sin(height / 4 + phase), y + 0.6 * math.cos(height / 5 + phase), height))
    limb(m, stalk, points, width, width * 0.6)
    for i, p in enumerate(points[1:-1], start=1):
        a = phase + i * 2.4
        out = Vector((math.cos(a), math.sin(a), 0)).normalized()
        start = Vector(p) + out * 0.35
        m.block(bladder, *start, 0.5, 0.5, 0.55)
        # A long ribbon blade floating up and out: narrow at the stalk, widest past the middle, then a point.
        length = rng.uniform(3.0, 4.4)
        mid = start + out * length * 0.45 + Vector((0, 0, length * 0.35))
        tip = mid + out * length * 0.3 + Vector((0, 0, length * 0.55))
        beam(m, leaf, tuple(start), tuple(mid), 0.45, 0.14, 1.25)
        beam(m, leaf, tuple(mid), tuple(tip), 1.25, 0.14, 0.12)
    top = Vector(points[-1])
    beam(m, leaf, tuple(top), tuple(top + Vector((0.6, 0.3, 1.6))), 0.4, 0.14, 1.1)
    beam(m, leaf, tuple(top + Vector((0.6, 0.3, 1.6))), tuple(top + Vector((1.4, 0.5, 3.4))), 1.1, 0.14, 0.12)


def jelly(m, x, y, z, s, rng, bell="Bell", rim="Glow", arm="Arm", tentacle="Tentacle"):
    """A jellyfish drifting at height z: a domed bell with a glowing rim and spots, frilly arms and long
    swaying tentacles."""
    m.loft_z(bell, (z, x, y, 2.4 * s, 2.4 * s), (z + 0.6 * s, x, y, 2.7 * s, 2.7 * s))
    m.loft_z(bell, (z + 0.6 * s, x, y, 2.7 * s, 2.7 * s), (z + 1.4 * s, x, y, 2.1 * s, 2.1 * s))
    m.loft_z(bell, (z + 1.4 * s, x, y, 2.1 * s, 2.1 * s), (z + 1.9 * s, x, y, 1.0 * s, 1.0 * s))
    m.block(rim, x, y, z - 0.05 * s, 1.9 * s, 1.9 * s, 0.25 * s)  # the glow inside, seen from below
    for k in range(8):
        a = k * math.tau / 8
        m.block(rim, x + math.cos(a) * 1.25 * s, y + math.sin(a) * 1.25 * s, z + 0.08 * s, 0.5 * s, 0.5 * s, 0.3 * s)
    for k in range(4):
        a = k * math.tau / 4 + 0.4
        m.block(rim, x + math.cos(a) * 1.08 * s, y + math.sin(a) * 1.08 * s, z + 1.15 * s, 0.32 * s, 0.32 * s, 0.32 * s)
    for k in range(4):  # frilly arms from the middle
        a = k * math.tau / 4
        points = [(x + math.cos(a) * 0.3 * s, y + math.sin(a) * 0.3 * s, z)]
        for j in range(1, 5):
            wig = 0.35 * s * (1 if j % 2 else -1)
            points.append((x + math.cos(a) * (0.3 * s + wig), y + math.sin(a) * (0.3 * s - wig), z - j * 0.75 * s))
        limb(m, arm, points, 0.5 * s, 0.25 * s)
    for k in range(10):  # long tentacles from the rim
        a = k * math.tau / 10 + 0.2
        length = rng.uniform(4.5, 7.5) * s
        bx, by = x + math.cos(a) * 1.15 * s, y + math.sin(a) * 1.15 * s
        points = []
        steps = 6
        for j in range(steps + 1):
            t = j / steps
            sway = 0.4 * s * math.sin(t * 4 + k)
            points.append((bx + math.cos(a + 1.5) * sway, by + math.sin(a + 1.5) * sway, z - length * t))
        limb(m, tentacle, points, 0.16 * s, 0.08 * s, joints=False)


# ---------------------------------------------------------------------- reef props


def branch_coral(seed=3):
    """The map's signature coral: a pink coral tree forking again and again into fat rounded tips, with a
    smaller orange one at its foot."""
    m = prop("BranchCoral", Coral=CORAL_PINK, CoralTip=CORAL_PINK_TIP, Coral2=CORAL_ORANGE, Coral2Tip=CORAL_ORANGE_TIP,
             Rock=ROCK, RockDark=ROCK_DARK, Sand=SAND)
    rng = random.Random(seed)
    sand_patch(m, 7, 6)
    rock_base(m, rng, 4.2, 3.6, 1.4)
    for k in range(4):
        a = k * math.tau / 4 + 0.3
        d = Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 1))
        coral_branch(m, "Coral", "CoralTip", (math.cos(a) * 0.5, math.sin(a) * 0.5, 1.2), d, 2.6, 1.05, 3, rng)
    for k in range(2):
        a = k * math.pi + 1.2
        coral_branch(m, "Coral2", "Coral2Tip", (math.cos(a) * 2.4, math.sin(a) * 2.0, 0.3),
                     (math.cos(a) * 0.5, math.sin(a) * 0.5, 1), 1.4, 0.6, 2, rng)
    return m


def brain_coral(seed=4):
    """A big round brain coral, its ridges winding over the top, with a little purple one beside it."""
    m = prop("BrainCoral", Brain="#d6e04f", Groove="#7f8f25", Brain2=CORAL_PURPLE, Groove2="#5e3aa8", Sand=SAND)
    sand_patch(m, 8, 7)
    brain_dome(m, 0, 0, 0.2, 3.0, 2.7, 3.6, seed=seed)
    brain_dome(m, 3.2, -2.0, 0.2, 1.3, 1.2, 1.6, "Brain2", "Groove2", seed=seed + 1)
    return m


def tube_sponges(seed=5):
    """A cluster of tall tube sponges, purple and orange, dark inside their open tops."""
    m = prop("TubeSponges", Sponge=CORAL_PURPLE, Sponge2=CORAL_ORANGE, Inside="#2a1840", Pore="#7a48d6", Rock=ROCK,
             RockDark=ROCK_DARK, Sand=SAND)
    rng = random.Random(seed)
    sand_patch(m, 6.5, 6)
    rock_base(m, rng, 4.2, 3.8, 0.9)
    tubes = [(0, 0, 7.2, 0.95, "Sponge"), (1.4, 0.9, 5.2, 0.8, "Sponge2"), (-1.3, 0.7, 6.0, 0.75, "Sponge"),
             (0.6, -1.4, 4.2, 0.7, "Sponge"), (-1.0, -1.2, 3.0, 0.6, "Sponge2"), (2.2, -0.6, 2.4, 0.55, "Sponge")]
    for x, y, h, r, role in tubes:
        turn = rng.uniform(0, 1)
        prism(m, role, x, y, 0.5, h, r, r * 1.2, 8, turn)
        prism(m, "Inside", x, y, h - 0.6, h + 0.03, r * 0.9, r * 0.98, 8, turn)
        for k in range(int(h // 1.6)):  # pores
            a = rng.uniform(0, math.tau)
            z = 1.2 + k * 1.5 + rng.uniform(-0.2, 0.2)
            rr = r + (r * 0.2) * (z / h)
            m.block("Pore", x + math.cos(a) * rr, y + math.sin(a) * rr, z, 0.3, 0.3, 0.3)
    return m


def kelp(seed=6):
    """A stand of tall kelp swaying up from a tangle of holdfasts, olive with golden air bladders."""
    m = prop("Kelp", Kelp=KELP, KelpLeaf=KELP_LEAF, Bladder=BLADDER, KelpDark=KELP_DARK, Rock=ROCK, Sand=SAND)
    rng = random.Random(seed)
    sand_patch(m, 6, 5)
    m.loft_z("Rock", (0, 0, 0, 3.0, 2.6), (0.8, 0, 0, 2.2, 1.8))
    for x, y, h, ph in ((0, 0, 21, 0.0), (1.4, 0.8, 16, 1.7), (-1.2, 0.9, 18, 3.1), (0.6, -1.3, 13, 4.4), (-1.0, -1.0, 10, 5.5)):
        kelp_stalk(m, x, y, h, ph, rng)
        for k in range(4):  # holdfast roots gripping the rock
            a = k * math.tau / 4 + ph
            beam(m, "KelpDark", (x, y, 0.8), (x + math.cos(a) * 1.0, y + math.sin(a) * 1.0, 0.1), 0.35, None, 0.15)
    return m


def anemones(seed=7):
    """Three sea anemones on a rock, magenta with glowing pink tips."""
    m = prop("Anemones", Column="#d9466f", Tentacle="#ff8fb8", Shine=SHINE_PINK, Rock=ROCK, RockDark=ROCK_DARK, Sand=SAND)
    rng = random.Random(seed)
    sand_patch(m, 7, 6)
    rock_base(m, rng, 4.6, 4.0, 0.8)
    anemone(m, 0, 0, 1.3, rng, z=0.6)
    anemone(m, 2.4, 1.3, 0.8, rng, z=0.3)
    anemone(m, -2.0, 1.6, 0.65, rng, z=0.2)
    return m


def giant_clam(seed=8):
    """A giant clam gaping open, its blue mantle inside and a big glowing pearl, a few bubbles rising."""
    m = prop("GiantClam", Shell=SHELL, ShellRidge=SHELL_SHADE, Mantle="#3fb6d4", Spot="#8ef0ff", Glow="#effcff",
             Bubble="#cdf6ff", Sand=SAND)
    rng = random.Random(seed)
    sand_patch(m, 9, 7.5)
    m.loft_z("Shell", (0.1, 0, 0, 5.4, 4.6), (1.5, 0, 0, 7.0, 5.8))
    for k in range(7):  # ridges down the lower shell's front
        y = -2.4 + k * 0.8
        m.block("ShellRidge", 3.45, y, 0.85, 0.3, 0.42, 1.5)
        m.block("ShellRidge", 3.5, y, 1.65 + 0.15 * (k % 2), 0.55, 0.6, 0.35)  # the wavy lip
    m.block("Mantle", 0.2, 0, 1.55, 6.2, 5.0, 0.3)
    for x, y in ((-1.5, 1.4), (1.6, -1.6), (2.2, 1.2), (-1.8, -1.3)):
        m.block("Spot", x, y, 1.72, 0.6, 0.6, 0.06)
    dome(m, "Glow", 0.4, 0, 1.6, 0.85)  # the pearl
    hinge = Vector((-3.4, 0, 1.4))
    angle = math.radians(55)
    along = Vector((math.cos(angle), 0, math.sin(angle)))
    outward = Vector((-math.sin(angle), 0, math.cos(angle)))
    beam(m, "Shell", tuple(hinge), tuple(hinge + along * 7.0), 5.8, 0.9, 7.0)
    beam(m, "Mantle", tuple(hinge + along * 0.5 - outward * 0.55), tuple(hinge + along * 6.6 - outward * 0.55), 5.0, 0.2, 6.0)
    for k in range(-3, 4):  # ridges fanning out over the top shell
        a = hinge + outward * 0.55 + Vector((0, k * 0.5, 0))
        b = hinge + along * 7.0 + outward * 0.6 + Vector((0, k * 1.0, 0))
        beam(m, "ShellRidge", tuple(a), tuple(b), 0.45, 0.3, 0.6)
    for dx, dy, z, s in ((1.0, 0.4, 3.4, 0.45), (1.4, -0.2, 4.6, 0.35), (0.8, 0.5, 5.7, 0.28), (1.3, 0.1, 6.6, 0.2)):
        m.block("Bubble", dx, dy, z, s, s, s)
    return m


def tube_worms(seed=9):
    """A cluster of giant tube worms on a dark mound: white tubes with red plumes."""
    m = prop("TubeWorms", Tube="#f2efe6", Plume="#e8303f", Rock="#2e3a4c", RockDark="#232d3c", Sand=SAND)
    rng = random.Random(seed)
    sand_patch(m, 6, 5.5)
    rock_base(m, rng, 3.8, 3.4, 0.8)
    spots = []
    for k in range(11):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0, 1.6)
        spots.append((math.cos(a) * r, math.sin(a) * r, rng.uniform(2.4, 6.0), rng.uniform(0.3, 0.45),
                      (math.cos(a) * rng.uniform(0.2, 0.8), math.sin(a) * rng.uniform(0.2, 0.8))))
    worms(m, spots)
    return m


def sea_urchins(seed=10):
    """A rock with purple urchins bristling on it and orange starfish clinging to it and the sand."""
    m = prop("SeaUrchins", Urchin="#4a2468", Spike="#8a52c8", Starfish="#ff7a3d", StarDot="#ffd0a0", Rock=ROCK,
             RockDark=ROCK_DARK, Sand=SAND)
    rng = random.Random(seed)
    sand_patch(m, 7, 6)
    m.loft_z("Rock", (0, 0, 0, 4.6, 3.8), (1.6, 0.2, 0, 4.0, 3.2))
    m.loft_z("Rock", (1.6, 0.2, 0, 4.0, 3.2), (2.4, 0.3, 0.1, 2.6, 2.0))
    m.block("RockDark", 2.0, -1.4, 0.6, 1.6, 1.4, 1.2)
    urchin(m, 0.2, 0.1, 3.0, 0.75)
    urchin(m, -1.6, 1.0, 2.0, 0.55)
    urchin(m, 2.8, 1.4, 0.55, 0.5)
    starfish(m, 1.0, -0.8, 2.4, 0.7, 0.4)
    starfish(m, -2.8, -1.6, 0.05, 0.9, 1.1)
    return m


def sea_grass(seed=11):
    """A tuft of sea grass, small filler tucked around the bigger props."""
    m = prop("SeaGrass", Grass=SEAGRASS, GrassDark=SEAGRASS_DARK, Sand=SAND)
    rng = random.Random(seed)
    sand_patch(m, 3.4, 3.0)
    for k in range(14):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0, 1.1)
        x, y = math.cos(a) * r, math.sin(a) * r
        h = rng.uniform(2.0, 4.6)
        lean = rng.uniform(0.3, 1.0)
        mid = (x + math.cos(a) * lean * 0.4, y + math.sin(a) * lean * 0.4, h * 0.55)
        top = (x + math.cos(a + 0.6) * lean, y + math.sin(a + 0.6) * lean, h)
        limb(m, "Grass" if k % 3 else "GrassDark", [(x, y, 0.2), mid, top], 0.4, 0.1)
    return m


def jellyfish(seed=12):
    """Three jellyfish drifting high over the sea floor, lavender and pink, their rims and spots glowing.
    Nothing touches the ground: the origin is the spot on the floor they float over."""
    m = prop("Jellyfish", Bell="#c48cff", Bell2="#ff9fd6", Glow=GLOW_CYAN, Arm="#f3d4ff", Tentacle="#e6c4ff")
    rng = random.Random(seed)
    jelly(m, 0, 0, 13, 1.25, rng)
    jelly(m, 2.8, 1.6, 9.0, 0.8, rng, bell="Bell2")
    jelly(m, -2.4, -1.8, 16.5, 0.7, rng)
    return m


def ammonite(seed=13):
    """A landmark: a giant spiral ammonite shell half sunk in the sand, cream with brown bands, starfish
    and urchins around it."""
    m = prop("Ammonite", Shell=SHELL, ShellStripe=SHELL_STRIPE, ShellShade=SHELL_SHADE,
             Sand=SAND, SandLight=SAND_LIGHT, Starfish="#ff7a3d", StarDot="#ffd0a0", Urchin="#4a2468", Spike="#8a52c8")
    rng = random.Random(seed)
    a, b = 0.7, 0.21
    theta_end = 3.5 * math.pi  # the last whorl dives into the sand, so the shell looks half sunk
    centre_z = 6.2
    points = []
    t = 0.6
    while t <= theta_end + 1e-6:
        r = a * math.exp(b * t)
        points.append((Vector((r * math.cos(t), 0, centre_z + r * math.sin(t))), r))
        t += 0.2
    for i, ((p, r), (q, rq)) in enumerate(zip(points, points[1:])):
        beam(m, "Shell", tuple(p - (q - p) * 0.08), tuple(q + (q - p) * 0.08), r * 0.8, r * 0.95, rq * 0.8)
        if i % 2 == 0:  # ribs round the tube, turned with it
            along = (q - p).normalized()
            beam(m, "ShellStripe" if i % 4 == 0 else "ShellShade", tuple(q - along * 0.12 * rq), tuple(q + along * 0.12 * rq),
                 rq * 0.88, rq * 1.05)
    m.loft_z("Sand", (0, 0, 0, 20, 10), (1.2, 0, 0, 15, 7))
    m.loft_z("SandLight", (1.2, 0, 0, 15, 7), (1.9, 0.5, 0, 9, 4.6))
    starfish(m, -5.5, -3.2, 1.2, 0.9, 0.3)
    starfish(m, 6.2, 3.0, 0.9, 0.8, 1.4)
    urchin(m, 5.6, -3.0, 1.4, 0.55)
    urchin(m, -6.2, 2.6, 1.3, 0.45)
    return m


def thermal_vent(seed=14):
    """A hydrothermal vent: a lumpy black chimney with glowing cracks, dark smoke billowing from its top,
    bubbles streaming up its side and tube worms crowding its foot."""
    m = prop("ThermalVent", Chimney="#2e3440", ChimneyDark="#20252e", Ember="#ff7a2a", Smoke="#384556",
             SmokeLight="#4d5c70", Bubble="#cdf6ff", Tube="#f2efe6", Plume="#e8303f", Sand=SAND)
    rng = random.Random(seed)
    sand_patch(m, 7, 6.5)
    segments = [(0, 3.0, 2.3, 1.9, (0, 0)), (3.0, 6.0, 1.9, 1.6, (0.3, 0.1)), (6.0, 9.0, 1.6, 1.35, (0.1, 0.35)),
                (9.0, 11.6, 1.35, 1.05, (0.35, 0.2))]
    for i, (z0, z1, r0, r1, (cx, cy)) in enumerate(segments):
        prism(m, "Chimney" if i % 2 == 0 else "ChimneyDark", cx, cy, z0, z1 + 0.2, r0, r1, 6, 0)
        for k in range(3):  # lumps
            a = rng.uniform(0, math.tau)
            z = rng.uniform(z0 + 0.5, z1 - 0.5)
            m.block("ChimneyDark", cx + math.cos(a) * r0 * 0.85, cy + math.sin(a) * r0 * 0.85, z, 0.9, 0.9, 0.9)
        face = math.radians(30 + 60 * rng.randint(0, 5))
        apothem = (r0 + r1) / 2 * 0.866 + 0.06
        crack = [Vector((cx + math.cos(face) * apothem, cy + math.sin(face) * apothem, z0 + 0.4))]
        for j in range(3):
            crack.append(crack[-1] + Vector((-math.sin(face) * rng.uniform(-0.4, 0.4), math.cos(face) * rng.uniform(-0.4, 0.4), (z1 - z0) / 3.4)))
        for p, q in zip(crack, crack[1:]):
            beam(m, "Ember", tuple(p), tuple(q), 0.1, 0.22)
    top = Vector((0.35, 0.2, 11.8))
    m.block("ChimneyDark", *top, 2.4, 2.4, 0.5)
    m.block("Ember", top.x, top.y, top.z + 0.15, 1.2, 1.2, 0.3)
    for k, (dz, s, dx) in enumerate(((1.0, 1.0, 0.0), (2.2, 1.3, 0.4), (3.6, 1.6, 0.9), (5.2, 1.9, 1.5), (7.0, 2.1, 2.2))):
        role = "Smoke" if k % 2 == 0 else "SmokeLight"
        m.block(role, top.x + dx, top.y + 0.25 * k, top.z + dz, s, s * 0.9, s * 0.8)
        if k >= 2:
            m.block(role, top.x + dx + s * 0.45, top.y - 0.2, top.z + dz + s * 0.35, s * 0.55, s * 0.55, s * 0.55)
    for k in range(7):
        s = 0.5 - k * 0.04
        m.block("Bubble", 2.2 + 0.25 * math.sin(k), -0.8, 1.0 + k * 1.7, s, s, s)
    worms(m, [(-2.4, 0.6, 3.2, 0.32, (-0.3, 0.2)), (-2.0, -1.2, 2.4, 0.3, (-0.2, -0.3)), (-2.9, -0.4, 1.8, 0.28, (-0.4, 0)),
              (1.6, 2.2, 2.8, 0.3, (0.1, 0.4)), (0.6, 2.5, 2.0, 0.28, (0, 0.3))])
    return m


def anchor(seed=15):
    """A giant rusty anchor stuck in the sand at a slant, kelp hanging off its stock and its chain trailing
    across the sea floor."""
    m = prop("Anchor", Iron="#55606e", IronDark="#3e4752", Rust="#a0532c", Chain="#4a535f", Kelp=KELP, Sand=SAND,
             SandLight=SAND_LIGHT)
    rng = random.Random(seed)
    beam(m, "Iron", (0, 0, 0), (0, 0, 10), 1.0)
    for z, h in ((3.2, 1.4), (6.4, 0.9)):
        m.block("Rust", 0.52, 0.1, z, 0.1, 0.7, h)
    for x0, z0, x1, z1 in ((-0.7, 10.3, 0.7, 10.3), (-0.7, 11.7, 0.7, 11.7), (-0.75, 10.3, -0.75, 11.7), (0.75, 10.3, 0.75, 11.7)):
        beam(m, "IronDark", (x0, 0, z0), (x1, 0, z1), 0.4)
    m.block("IronDark", 0, 0, 9.0, 0.6, 6.4, 0.6)  # the stock, across
    for side in (-1, 1):
        m.block("IronDark", 0, side * 3.3, 9.0, 0.8, 0.5, 0.8)
        limb(m, "Iron", [(0, 0, 0.5), (side * 1.8, 0, 0.25), (side * 3.0, 0, 1.4), (side * 3.3, 0, 2.8)], 1.0, 0.65)
        beam(m, "Iron", (side * 2.9, 0, 1.4), (side * 3.7, 0, 3.6), 1.7, 0.35, 0.25)  # the fluke
        m.block("Rust", side * 2.2, 0.1, 0.55, 0.8, 0.9, 0.5)
    for k in range(5):
        y = -2.6 + k * 1.3
        moss_beard(m, 0.1, y, 8.6, rng.uniform(1.4, 3.0), 0.45, role="Kelp")
    turn = Matrix.Rotation(math.radians(24), 3, Vector((0, 1, 0)))
    transform(m, turn, (0, 0, -1.6))
    ring = turn @ Vector((0, 0, 10.3)) + Vector((0, 0, -1.6))
    path = [ring, Vector((ring.x + 2.4, 0.5, 0.4)), Vector((ring.x + 5.0, 1.8, 0.3)), Vector((ring.x + 7.6, 1.2, 0.3)),
            Vector((ring.x + 9.4, 3.0, 0.3))]
    flat = True
    for a, b in zip(path, path[1:]):
        steps = max(1, int((b - a).length / 0.9))
        for j in range(steps):
            p, q = a.lerp(b, j / steps), a.lerp(b, (j + 1) / steps)
            beam(m, "Chain", tuple(p), tuple(q), 0.55 if flat else 0.18, 0.18 if flat else 0.55)
            flat = not flat
    m.loft_z("Sand", (0, -1.2, 0, 9, 7), (0.9, -1.2, 0, 6, 4.4))
    m.loft_z("SandLight", (0.9, -1.2, 0, 6, 4.4), (1.4, -1.2, 0, 3.6, 2.6))
    return m


def treasure_chest(seed=16):
    """A treasure chest burst open on the sea floor: gold banded wood, coins heaped inside and spilling onto
    the sand, a goblet and a few glowing gems."""
    m = prop("TreasureChest", Wood="#7a4a2c", WoodDark="#5a3420", Gold="#ffc93c", GoldDark="#d99a1e", Iron="#4a4f58",
             Shine=SHINE_PINK, Glow=GLOW_CYAN, Sand=SAND)
    rng = random.Random(seed)
    sand_patch(m, 8, 7)
    m.block("Wood", 0, 0, 1.3, 4.2, 2.8, 2.2)
    m.block("WoodDark", 0, 0, 0.35, 4.4, 3.0, 0.5)
    for x in (-1.5, 1.5):
        m.block("Gold", x, 0, 1.35, 0.35, 2.95, 2.3)
    m.block("Gold", 0, -1.45, 2.3, 4.3, 0.15, 0.3)
    m.block("Iron", 0, -1.5, 1.7, 0.7, 0.2, 0.8)
    hinge = Vector((0, 1.35, 2.4))
    along = Vector((0, 0.45, 0.89)).normalized()
    beam(m, "Wood", tuple(hinge), tuple(hinge + along * 2.7), 4.2, 0.6)
    beam(m, "WoodDark", tuple(hinge + Vector((0, 0.35, 0.1))), tuple(hinge + along * 2.7 + Vector((0, 0.35, 0.1))), 4.0, 0.4)
    for x in (-1.5, 1.5):
        beam(m, "Gold", tuple(hinge + Vector((x, -0.02, 0))), tuple(hinge + along * 2.75 + Vector((x, -0.02, 0))), 0.36, 0.66)
    for k in range(40):  # coins heaped inside
        x, y = rng.uniform(-1.8, 1.8), rng.uniform(-1.1, 1.1)
        z = 2.4 + 0.7 * (1 - (x / 2) ** 2) * (1 - (y / 1.3) ** 2) + rng.uniform(-0.1, 0.1)
        m.block("Gold" if k % 3 else "GoldDark", x, y, z, 0.55, 0.55, 0.14)
    for k in range(26):  # and spilling out over the front
        x = rng.uniform(-2.0, 2.0)
        y = -1.6 - rng.uniform(0, 2.6)
        z = 0.42 + max(0, 0.9 - (abs(y) - 1.6) * 0.6) * rng.uniform(0.2, 1.0)
        m.block("Gold" if k % 3 else "GoldDark", x, y, z, 0.55, 0.55, 0.14)
    for x, y, z, role in ((-0.8, -0.2, 3.1, "Shine"), (0.9, 0.3, 3.0, "Glow"), (1.6, -2.6, 0.6, "Shine"), (-1.4, -3.1, 0.55, "Glow")):
        m.loft_z(role, (z - 0.25, x, y, 0.3, 0.3), (z, x, y, 0.6, 0.6))
        m.loft_z(role, (z, x, y, 0.6, 0.6), (z + 0.3, x, y, 0.1, 0.1))
    gx, gy = 2.7, -1.0  # a goblet tipped beside it
    prism(m, "Gold", gx, gy, 0.35, 0.6, 0.5, 0.45, 8)
    prism(m, "Gold", gx, gy, 0.6, 1.4, 0.15, 0.15, 6)
    prism(m, "GoldDark", gx, gy, 1.4, 2.2, 0.25, 0.6, 8)
    return m


def shell_patch(seed=17):
    """A patch of rippled sand with starfish, scallop shells, pebbles and bits of glowing sea glass. Flat
    (under half a stud), so it can lie in the middle of the floor where the eggs land."""
    m = prop("ShellPatch", Sand=SAND, SandLight=SAND_LIGHT, Shell=SHELL, ShellRidge=SHELL_SHADE, Starfish="#ff7a3d",
             StarDot="#ffd0a0", Pebble="#8fa3b8", Glow=GLOW_CYAN)
    rng = random.Random(seed)
    for x, y, w, d in ((0, 0, 14, 8), (2, 2.4, 9, 6), (-3.4, -1.6, 7, 6)):
        m.block("Sand", x, y, 0.06, w, d, 0.12)
    for k in range(6):  # ripples
        y = -3.2 + k * 1.3
        m.block("SandLight", rng.uniform(-1, 1), y + 0.4 * math.sin(k), 0.15, rng.uniform(6, 10), 0.35, 0.06)
    starfish(m, -3.0, 1.4, 0.12, 0.8, 0.5)
    starfish(m, 3.6, -1.6, 0.12, 0.6, 1.6)
    for x, y, turn in ((1.0, 2.2, 0.4), (-4.6, -2.0, 2.0), (4.8, 2.4, 3.3)):  # scallops: a fan of ribs
        for k in range(5):
            a = turn + (k - 2) * 0.32
            beam(m, "Shell" if k % 2 else "ShellRidge", (x, y, 0.2), (x + math.cos(a) * 1.3, y + math.sin(a) * 1.3, 0.2), 0.3, 0.12, 0.42)
        m.block("ShellRidge", x - math.cos(turn) * 0.15, y - math.sin(turn) * 0.15, 0.2, 0.5, 0.5, 0.14)
    for k in range(9):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(2, 6)
        s = rng.uniform(0.4, 0.8)
        m.block("Pebble", math.cos(a) * r, math.sin(a) * r * 0.6, 0.2, s, s * 0.8, 0.22)
    for x, y in ((-0.6, -2.4), (2.2, 0.6), (-5.4, 0.8), (5.6, -0.4)):
        m.block("Glow", x, y, 0.18, 0.45, 0.35, 0.12)
    return m


# ---------------------------------------------------------------------- set pieces


def shipwreck(seed=18):
    """A landmark for the rims: an old sailing ship sunk to the bottom, heeled over and half buried, its main
    mast snapped with a rag of sail, an eerie light in its stern windows, a hole stove in its side, coral and
    kelp growing over it and barrels tumbled out into the sand."""
    m = prop("Shipwreck", Hull="#6b4a35", HullDark="#4a3324", Deck="#8a6a4a", Trim="#3a2a1e", Hole="#120c0a",
             Sail="#d8cfb6", Glow="#7ff6ff", Barrel="#7a5536", Iron="#4a4f58", Coral=CORAL_ORANGE, CoralTip=CORAL_ORANGE_TIP,
             Coral2=CORAL_PINK, Coral2Tip=CORAL_PINK_TIP, Kelp=KELP, KelpLeaf=KELP_LEAF, Bladder=BLADDER, Sand=SAND,
             SandLight=SAND_LIGHT)
    rng = random.Random(seed)
    sections = [(-17, 0.6, 8.4), (-12, 0.0, 10.4), (-4, 0.0, 11.2), (6, 0.2, 10.6), (12, 0.8, 8.6), (16, 1.6, 5.2), (19.5, 2.8, 1.0)]
    for (xa, la, wa), (xb, lb, wb) in zip(sections, sections[1:]):
        m.loft_x("Hull", (xa, 0, 4.6 + la, wa, 4.4), (xb, 0, 4.6 + lb, wb, 4.4))
        m.loft_x("HullDark", (xa, 0, 1.6 + la, wa * 0.62, 1.8), (xb, 0, 1.6 + lb, wb * 0.62, 1.8))
        m.loft_x("Trim", (xa, 0, 6.6 + la, wa + 0.25, 0.6), (xb, 0, 6.6 + lb, wb + 0.25, 0.6))
        m.loft_x("Deck", (xa, 0, 6.85 + la, wa - 0.8, 0.12), (xb, 0, 6.85 + lb, max(wb - 0.8, 0.2), 0.12))
        for z in (3.4, 5.1):  # plank lines
            m.loft_x("HullDark", (xa, 0, z + la, wa + 0.12, 0.22), (xb, 0, z + lb, wb + 0.12, 0.22))
    m.loft_x("Trim", (-17.5, 0, 1.2, 1.0, 1.0), (19.8, 0, 3.6, 0.6, 0.8))  # the keel
    m.block("Hull", -14.2, 0, 8.6, 6.0, 9.0, 3.6)  # the stern castle
    m.block("Trim", -14.2, 0, 10.5, 6.4, 9.4, 0.4)
    for y in (-2.6, 0, 2.6):
        m.block("Glow", -17.25, y, 8.8, 0.12, 1.3, 1.2)
    for side in (-1, 1):  # rails and portholes
        for k in range(11):
            x = -9 + k * 2.2
            if rng.random() < 0.8:
                lift = 0.2 if x < 12 else 1.0
                m.block("Trim", x, side * 4.7, 7.5 + lift, 0.3, 0.3, 1.2)
        m.block("Trim", 2, side * 4.7, 8.15, 22, 0.3, 0.3)
        for x in (-8, -3, 2, 7):
            m.block("Trim", x, side * 5.62, 4.6, 0.9, 0.1, 0.9)
    m.block("Hole", 1.5, 5.62, 3.6, 4.2, 0.12, 2.8)  # stove in on the side it heels to
    for k in range(4):
        beam(m, "Trim", (-0.4 + k * 1.2, 5.7, 2.2), (0.2 + k * 1.2, 5.7, 5.0), 0.35, 0.2)
    beam(m, "HullDark", (0, 0, 6.9), (0, 0, 22), 1.0, None, 0.8)  # main mast, snapped at the top
    prism(m, "HullDark", 0, 0, 22, 23.2, 0.4, 0.05, 4, 0.3, (0.3, 0))
    m.block("Trim", 0, 0, 18.5, 0.6, 11, 0.5)  # its yard
    m.block("Sail", 0.15, -2.6, 16.0, 0.12, 4.6, 4.6)  # a torn rag of sail
    m.block("Sail", 0.15, 2.9, 16.8, 0.12, 3.2, 3.0)
    m.block("Sail", 0.15, -1.2, 13.4, 0.12, 2.0, 1.4)
    beam(m, "HullDark", (10, 0, 7.0), (10, 0, 11.6), 0.8)  # fore mast, broken off
    beam(m, "HullDark", (10.4, 0.6, 7.2), (4.8, 3.6, 7.4), 0.7)  # its top, lying across the deck
    beam(m, "HullDark", (19.0, 0, 6.4), (25, 0, 10.0), 0.6, None, 0.35)  # bowsprit
    for x, y, h in ((-6, -2.5, 1.6), (-4.8, 2.4, 1.4)):  # barrels on deck
        prism(m, "Barrel", x, y, 6.9, 6.9 + h, 0.75, 0.75, 8)
        prism(m, "Iron", x, y, 6.9 + h * 0.2, 6.9 + h * 0.3, 0.8, 0.8, 8)
        prism(m, "Iron", x, y, 6.9 + h * 0.7, 6.9 + h * 0.8, 0.8, 0.8, 8)
    for x, y in ((-10, 1.8), (6, -2.2), (14, 1.0)):  # coral growing on the deck
        for k in range(3):
            a = k * math.tau / 3 + x
            coral_branch(m, "Coral" if x < 0 else "Coral2", "CoralTip" if x < 0 else "Coral2Tip", (x, y, 7.0),
                         (math.cos(a) * 0.4, math.sin(a) * 0.4, 1), 1.3, 0.5, 2, rng)
    heel = Matrix.Rotation(math.radians(17), 3, Vector((1, 0, 0))) @ Matrix.Rotation(math.radians(-4), 3, Vector((0, 1, 0)))
    transform(m, heel, (0, 0, -2.6))
    # Added after the tilt: the sand it sank into, kelp growing up beside it and barrels tumbled out.
    m.loft_z("Sand", (0, 3, 0.5, 46, 18), (1.6, 3, 0.5, 39, 14))
    m.loft_z("SandLight", (1.6, 3, 0.5, 34, 9), (2.6, 3, 0.5, 25, 6))
    for x, y in ((-12, -8.5), (-2, -8.8), (8, -8.0), (16, 6.0)):
        kelp_stalk(m, x, y, rng.uniform(10, 15), rng.uniform(0, 6), rng, stalk="Kelp", leaf="KelpLeaf", bladder="Bladder", width=0.45)
    for x, y, lying in ((5, 10.5, True), (-8, 10.0, False), (20, -6, True)):
        if lying:
            m.loft_x("Barrel", (x - 0.8, y, 1.75 + 0.75, 1.5, 1.5), (x + 0.8, y, 1.75 + 0.75, 1.5, 1.5))
            m.loft_x("Iron", (x - 0.5, y, 2.5, 1.6, 1.6), (x - 0.35, y, 2.5, 1.6, 1.6))
        else:
            prism(m, "Barrel", x, y, 1.6, 3.2, 0.75, 0.75, 8)
            prism(m, "Iron", x, y, 2.7, 2.85, 0.8, 0.8, 8)
    return m


def coral_arch(seed=19):
    """An arch of rock over the corridor, rim to rim, overgrown with coral, sponges and anemones on top,
    sea grass and glowing strands hanging under it. It spans X; its feet stand on the rims beyond 36 studs
    from the middle, and all of it stays above the rim's height (z 0), clear of the flight camera."""
    m = prop("CoralArch", Rock=ROCK, RockDark=ROCK_DARK, Coral=CORAL_PINK, CoralTip=CORAL_PINK_TIP, Coral2=CORAL_ORANGE,
             Coral2Tip=CORAL_ORANGE_TIP, Brain="#d6e04f", Groove="#7f8f25", Sponge=CORAL_PURPLE, Inside="#2a1840",
             Column="#d9466f", Tentacle="#ff8fb8", Shine=SHINE_PINK, Grass=SEAGRASS, Glow=GLOW_CYAN, Front="#ff00ff")
    rng = random.Random(seed)

    def underside(x):
        return 6 + 9 * (1 - (x / 48) ** 2)

    for side in (-1, 1):
        m.block("Rock", side * 49, 0, 3.2, 20, 13, 6.4)
        m.block("RockDark", side * 46.5, 0.4, 8.4, 15, 11, 4.4)
        m.block("Rock", side * 43.8, -0.3, 11.6, 11, 10, 2.8)
    for i in range(-5, 6):
        x = i * 8
        bottom = underside(x)
        m.block("Rock" if i % 2 == 0 else "RockDark", x, rng.uniform(-0.5, 0.5), bottom + 3, 8.4, rng.uniform(8.6, 10), 6)
    def top_at(x):
        if abs(x) > 42:
            return 12.8 if abs(x) > 44 else underside(40) + 6
        return underside(round(x / 8) * 8) + 6  # the top of the rock block it stands on

    for i in range(-14, 15):  # a reef growing all along the top, in both rows
        x = i * 3 + rng.uniform(-0.6, 0.6)
        top = top_at(x)
        y = (2.4 if i % 2 else -2.4) + rng.uniform(-0.6, 0.6)
        kind = (i * 7) % 6
        if kind in (0, 3):
            role, tip = ("Coral", "CoralTip") if kind == 0 else ("Coral2", "Coral2Tip")
            for k in range(3):
                a = k * math.tau / 3 + i
                coral_branch(m, role, tip, (x, y, top - 0.1), (math.cos(a) * 0.4, math.sin(a) * 0.4, 1), 2.3, 0.9, 2, rng, (2, 2))
        elif kind == 1:
            brain_dome(m, x, y, top - 0.2, 2.0, 1.8, 2.5, seed=i + 40)
        elif kind == 2:
            for dx, dy, h in ((0, 0, 4.6), (0.9, 0.6, 3.0), (-0.8, 0.5, 3.6)):
                prism(m, "Sponge", x + dx, y + dy, top - 0.2, top + h, 0.6, 0.72, 8)
                prism(m, "Inside", x + dx, y + dy, top + h - 0.4, top + h + 0.03, 0.55, 0.66, 8)
        elif kind == 4 and i % 3 == 0:
            anemone(m, x, y, 0.95, rng, z=top - 0.1)
        else:
            for k in range(6):  # a tuft of sea grass
                a = k * math.tau / 6 + i
                beam(m, "Grass", (x, y, top - 0.1), (x + math.cos(a) * 0.9, y + math.sin(a) * 0.9, top + rng.uniform(2.0, 3.4)), 0.4, None, 0.1)
    for i in range(-5, 6):  # crusts of coral and glowing polyps over both faces of every block
        x = i * 8
        bottom = underside(x)
        for side in (-1, 1):
            for k in range(3):
                role = ("Coral", "Coral2", "Brain", "Sponge")[(i + k + side) % 4]
                m.block(role, x + rng.uniform(-3, 3), side * 4.75, bottom + rng.uniform(1.2, 4.8), rng.uniform(1.4, 3.0), 0.5, rng.uniform(1.0, 2.0))
            m.block("Glow" if i % 2 else "Shine", x + rng.uniform(-3, 3), side * 4.85, bottom + rng.uniform(1, 5), 0.45, 0.25, 0.45)
    for k in range(24):  # sea grass and glowing strands hanging underneath
        x = -38 + k * 3.3 + rng.uniform(-1, 1)
        y = rng.uniform(-3.4, 3.4)
        under = underside(x)
        length = rng.uniform(1.6, min(6.0, under - 3.0))
        if k % 3 == 0:
            strand(m, "Glow", x, y, under + 0.2, length * 0.8, 0.22)
            m.block("Glow", x, y, under - length * 0.8, 0.5, 0.5, 0.5)
        else:
            m.loft_z("Grass", (under - length, x, y, 0.1, 0.1), (under + 0.2, x, y, 0.6, 0.6))
    m.block("Front", 0, 6, 3, 0.2, 0.2, 0.2)
    return m


def wall_reef(seed=20):
    """A reef spilling over the rim and down the corridor wall: table corals jutting out from the wall at
    every height with coral and anemones on them, glowing polyps, and kelp rising from a reef heap on the
    floor. Origin on the wall's top inner edge: rim z 0, floor z -44, +Y out into the corridor. The Front
    part tells the game which way it faces, then it's removed."""
    m = prop("WallReef", Table=CORAL_ORANGE, Table2=CORAL_YELLOW, Coral=CORAL_PINK, CoralTip=CORAL_PINK_TIP,
             Brain="#d6e04f", Groove="#7f8f25", Sponge=CORAL_PURPLE, Inside="#2a1840", Column="#d9466f", Tentacle="#ff8fb8",
             Shine=SHINE_PINK, Glow=GLOW_CYAN, Kelp=KELP, KelpLeaf=KELP_LEAF, Bladder=BLADDER, Rock=ROCK,
             RockDark=ROCK_DARK, Grass=SEAGRASS, Front="#ff00ff")
    rng = random.Random(seed)
    # Up on the rim, at the edge.
    brain_dome(m, -3.0, -3.5, 0, 2.4, 2.2, 2.6, seed=seed)
    for k in range(3):
        a = k * math.tau / 3
        coral_branch(m, "Coral", "CoralTip", (3.2, -3.0, 0), (math.cos(a) * 0.4, math.sin(a) * 0.4, 1), 2.0, 0.8, 2, rng)
    anemone(m, 0.4, -6.4, 0.9, rng)
    # Table corals sticking out of the wall, each on a stalk, with things growing on it.
    plates = [(-1.5, -5.5, 7.5, 4.6), (2.5, -12.0, 6.5, 4.0), (-2.5, -18.5, 8.0, 5.0), (1.5, -25.0, 6.0, 3.8),
              (-1.0, -31.5, 7.0, 4.4), (2.8, -37.5, 5.5, 3.6)]
    for i, (x, z, w, d) in enumerate(plates):
        y = 1.6 + d / 2
        role = "Table" if i % 2 == 0 else "Table2"
        beam(m, "RockDark", (x, 0.4, z - 2.4), (x, y - 0.4, z - 0.3), 1.2)
        m.block(role, x, y, z, w, d, 0.6)
        m.block(role, x, y + 0.3, z + 0.35, w * 0.7, d * 0.7, 0.3)
        for k in range(int(w // 1.2)):  # the plate's frilly rim
            m.block(role, x - w / 2 + 0.6 + k * 1.2, y + d / 2, z - 0.15 * (k % 2), 0.7, 0.5, 0.5)
        top = z + 0.5
        pick = i % 3
        if pick == 0:
            for k in range(2):
                a = k * math.pi + i
                coral_branch(m, "Coral", "CoralTip", (x + 1.2 * (k - 0.5), y, top), (math.cos(a) * 0.3, math.sin(a) * 0.3, 1), 1.3, 0.55, 2, rng)
        elif pick == 1:
            anemone(m, x - 1.0, y, 0.7, rng, z=top)
            anemone(m, x + 1.4, y + 0.6, 0.5, rng, z=top)
        else:
            for dx, h in ((-0.8, 2.6), (0.4, 1.8), (1.3, 2.2)):
                prism(m, "Sponge", x + dx, y, top, top + h, 0.45, 0.55, 8)
                prism(m, "Inside", x + dx, y, top + h - 0.35, top + h + 0.03, 0.42, 0.5, 8)
    for k in range(22):  # glowing polyps dotted over the wall
        x = rng.uniform(-5, 5)
        z = rng.uniform(-42, -4)
        m.block("Glow" if k % 2 else "Shine", x, 1.62, z, 0.4, 0.2, 0.4)
    for k in range(10):  # crusts of coral on the wall face
        x = rng.uniform(-5, 5)
        z = rng.uniform(-40, -6)
        m.block("Table2" if k % 2 else "Coral", x, 1.75, z, rng.uniform(1.0, 2.0), 0.5, rng.uniform(0.8, 1.6))
    # The reef heap on the floor, against the wall, with kelp rising from it.
    m.loft_z("Rock", (-44, 0, 4.0, 14, 8), (-42.6, 0, 3.6, 10, 5.6))
    m.loft_z("RockDark", (-42.6, 0, 3.6, 10, 5.6), (-41.8, 0.5, 3.4, 6, 3.6))
    brain_dome(m, -3.6, 6.2, -44, 1.8, 1.6, 2.2, seed=seed + 3)
    anemone(m, 3.4, 6.4, 0.8, rng, z=-44)
    for x, y, h, ph in ((-5.2, 3.4, 26, 0.5), (4.8, 3.0, 22, 2.2), (0.4, 5.0, 17, 4.0)):
        start = len(m.parts.get("Kelp", ([], []))[0]), len(m.parts.get("KelpLeaf", ([], []))[0]), len(m.parts.get("Bladder", ([], []))[0])
        kelp_stalk(m, x, y, h, ph, rng, width=0.55)
        for role, first in zip(("Kelp", "KelpLeaf", "Bladder"), start):  # lift the stalk onto the floor
            verts = m.parts[role][0]
            verts[first:] = [(v[0], v[1], v[2] - 41.6) for v in verts[first:]]
    for k in range(6):
        a = rng.uniform(-0.6, 0.6)
        x = rng.uniform(-6.5, 6.5)
        top = (x + math.sin(a) * 0.5, 3.2 + rng.uniform(0, 3), -44 + rng.uniform(2.5, 4.0))
        beam(m, "Grass", (x, top[1] - 0.5, -43.8), top, 0.35, None, 0.08)
    m.block("Front", 0, 6, -20, 0.2, 0.2, 0.2)
    return m


# ---------------------------------------------------------------------- preview stage


def corridor_stage(stage, length=300, seed=7):
    """A stretch of corridor in The Abyss's colours (floor z 0, walls 44 high, inner faces 36 from the middle)."""
    m = Model("AbyssCorridor", dict(CORRIDOR))
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


# The mix Config/Decor uses for Abyss, so the corridor render shows the real thing.
FLOOR = [("prop_BranchCoral", 16, (1.3, 1.7)), ("prop_Kelp", 14, (1.2, 1.6)), ("prop_BrainCoral", 10, (1.2, 1.6)),
         ("prop_TubeSponges", 10, (1.2, 1.6)), ("prop_Anemones", 10, (1.2, 1.6)), ("prop_SeaUrchins", 8, (1.2, 1.6)),
         ("prop_Jellyfish", 8, (1.1, 1.4)), ("prop_TubeWorms", 7, (1.2, 1.6)), ("prop_GiantClam", 6, (1.1, 1.4)),
         ("prop_ThermalVent", 4, (1.1, 1.4)), ("prop_Anchor", 3, (1.1, 1.3)), ("prop_TreasureChest", 2, (1.2, 1.4))]
EXTRAS = [("prop_SeaGrass", 5, (0.8, 1.2)), ("prop_BrainCoral", 2, (0.5, 0.7)), ("prop_SeaUrchins", 2, (0.5, 0.8)),
          ("prop_Anemones", 2, (0.5, 0.8))]
RIM = [("prop_Kelp", 5, (2, 2.6)), ("prop_BranchCoral", 5, (2, 2.6)), ("prop_BrainCoral", 2, (2, 2.6)),
       ("prop_TubeSponges", 2, (2, 2.4)), ("prop_Jellyfish", 3, (1.8, 2.2)), ("prop_SeaGrass", 2, (2.2, 2.8))]


def decorate_stage(stage, built, length=300, seed=61):
    """The corridor's props laid out like Config/Decor's Abyss rules."""
    rng = random.Random(seed)

    def pick(table):
        total = sum(w for _, w, _ in table)
        roll = rng.uniform(0, total)
        for name, weight, scale in table:
            roll -= weight
            if roll <= 0:
                return name, scale
        return table[-1][0], table[-1][2]

    copies = []

    def put(name, location, yaw, scale):
        copy = place_copy(built[name], stage, location, yaw, scale)
        hide_markers([copy])
        copies.append(copy)

    def put_random(table, x, z, y):
        name, (low, high) = pick(table)
        put(name, (x, -y, z), rng.uniform(0, math.tau), rng.uniform(low, high))

    y = 10
    while y < length - 12:
        side = rng.choice((-1, 1))
        x = side * rng.uniform(19, 27)
        put_random(FLOOR, x, 0, y)
        if rng.random() < 0.75:
            put_random(EXTRAS, side * min(max(abs(x) + rng.uniform(-8, 8), 16), 33), 0, y + rng.uniform(-8, 8))
        y += rng.uniform(10, 20)
    y = 6
    while y < length:
        for side in (-1, 1):
            if rng.random() < 0.9:
                put_random(RIM, side * rng.uniform(54, 96), 44, y)
        y += rng.uniform(14, 24)
    put("prop_Shipwreck", (-74, -110, 44), math.radians(20), 1.3)
    put("prop_Ammonite", (72, -230, 44), math.radians(90), 1.6)
    for y, side in ((40, 1), (150, -1), (255, 1)):
        put("prop_WallReef", (side * 36, -y, 44), side * math.pi / 2, 1)
    put("prop_CoralArch", (0, -200, 44), 0, 1)
    for y, x, yaw in ((25, -3, 20), (90, 5, 140), (170, -4, 70), (280, 3, 200)):
        put("prop_ShellPatch", (x, -y, 0), math.radians(yaw), 1.2)
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


def deep_light(scene):
    """A cooler, bluer light for the renders, closer to the game's Abyss light."""
    sun = bpy.data.objects["Sun"]
    sun.data.energy = 2.0
    sun.data.color = (0.8, 0.92, 1.0)
    ambient = scene.world.node_tree.nodes["Background"]
    ambient.inputs["Color"].default_value = (0.72, 0.86, 1.0, 1)
    ambient.inputs["Strength"].default_value = 0.8


# ---------------------------------------------------------------------- scene and renders


SET_PIECES = ("prop_Shipwreck", "prop_Ammonite", "prop_WallReef", "prop_CoralArch")


def main():
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    props = bpy.data.collections.new("Props")
    stage = bpy.data.collections.new("Preview stage")
    for col in (props, stage):
        scene.collection.children.link(col)

    prop_models = [branch_coral(), brain_coral(), tube_sponges(), kelp(), anemones(), giant_clam(), tube_worms(),
                   sea_urchins(), sea_grass(), jellyfish(), ammonite(), thermal_vent(), anchor(), treasure_chest(),
                   shell_patch(), shipwreck(), coral_arch(), wall_reef()]
    built = {}
    prop_roots = []
    spots = {"prop_Shipwreck": (0, -100, 0), "prop_Ammonite": (-60, -100, 0), "prop_WallReef": (40, -170, 44),
             "prop_CoralArch": (160, -170, 0)}
    x = 40
    for model in prop_models:
        root = model.build(props)
        if model.name in spots:
            root.location = spots[model.name]
        else:
            root.location = (x, -40, 0)
            x += 20
        built[model.name] = root
        prop_roots.append(root)
    light_up(prop_roots)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-300, -400, -0.01), (500, -400, -0.01), (500, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", CORRIDOR["FloorA"], False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = Model("Player", {"Skin": "#e8e2d4"})
    player.bone = "Root"
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    player_root = player.build(stage)
    bpy.context.view_layer.update()
    set_sky(scene, SKY)
    deep_light(scene)

    everything = prop_roots + [player_root]
    for model, root in zip(prop_models, prop_roots):
        low, high = kit.bounds(root)
        player_root.location = Vector((low.x - 3, (low.y + high.y) / 2 + 2, 0))
        bpy.context.view_layer.update()
        set_visible(everything, [root, player_root])
        centre = (low + high) / 2
        reach = max((high - low).length, 7)
        if model.name == "prop_CoralArch":
            kit.shoot(scene, model.name, centre + Vector((-25, 125, 10)), centre, (1400, 700), 32)
        elif model.name == "prop_WallReef":
            kit.shoot(scene, model.name, centre + Vector((40, 55, 6)), centre, (700, 900), 40)
        else:
            kit.shoot(scene, model.name, centre + Vector((0.5, 0.9, 0.42)) * reach * 1.25, centre, (600, 600), 50)
    player_root.location = (30, -40, 0)
    bpy.context.view_layer.update()
    set_visible(everything, [r for r in prop_roots if r.name not in SET_PIECES] + [player_root])
    kit.shoot(scene, "props", (190, 70, 46), (190, -45, 5), (1800, 700), 18)

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
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "abyss_models.blend"))
    print("saved", HERE / "abyss_models.blend")
    for model in prop_models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    main()
