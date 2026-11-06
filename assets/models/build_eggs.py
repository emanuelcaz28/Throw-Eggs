"""Builds the Egg Shop's 15 eggs in Blender and renders them, whole and cut in half (Blender, background mode).

    Blender -b -P build_eggs.py                 (models, stills, the lineups and the slice video; saves eggs.blend)
    Blender -b -P build_eggs.py -- stills       (stills only, quicker while modelling)
    ONLY=lava_egg,weeping_egg Blender -b -P build_eggs.py -- stills

Renders go to design/eggs/; FBX files (export_fbx.py) to assets/models/fbx/00_Eggs/Props/. The owner imports them;
studio_tidy.py then puts them in ReplicatedStorage.Assets.Eggs, where the game finds them (src/shared/EggModel.luau).

The owner asked (2026-11-06) for the shop's eggs to be made in Blender, "nothing special but more attractive as they
ramp up in price", and for an animation when the egg lands: it's cut in half and the white and the yolk show. One egg
per map, in Config/Eggs order and price, each following its map (as the block eggs did): the first three are plain
patterns, then glow comes in, then extra pieces (a lure, a planet's ring, a corona), then gold, gems and machinery,
and the last three wear a crown, a mushroom and a halo. From the Cosmic Egg on the yolk glows too.

  Dirty      a plain beige egg, smudged with dirt, dirtiest at the bottom
  Spotted    mint green with darker green spots
  Golden     gold, a darker zigzag round its middle and a pale band under it
  Lava       black basalt cracked all over, lava glowing through the cracks and pooling at its foot
  Frost      ice blue, a cap of snow dripping icicles, ice crystals growing out of its side
  Shadow     dark violet swirls and two pale eyes glowing out of the dark
  Abyss      deep-sea blue, glowing lure dots, a wave band, and an angler's lure bobbing over its top
  Cosmic     the night sky, a nebula band, twinkling stars and a gold planet's ring round it (glowing yolk from here)
  Eclipse    black over dark violet, a glowing gold corona round its waist with rays, a jade gem on top
  Forbidden  a leather-bound book: oxblood, gilt bands, a strip of page edges and a glowing violet gem clasp
  Carnival   red and cream candy stripes, gold bands, a ring of warm bulbs and a gold pompom
  Clockwork  brass and riveted steel bands, a gear on its side, a gauge glowing blue and a wind-up key on top
  Thorn      dark moss wrapped in violet briars, thorns, a glowing crimson rose and a gold crown on top
  Spore      lilac with chartreuse spots glowing, a black mushroom cap on top with glowing gills, two little ones
  Weeping    ash black under silver filigree, a red eye (red only ever for eyes) weeping pale light, a silver halo

The shape. Every egg is the same shell, exactly the thrown egg's size (ThrowController EGG_SIZE: 2.4 wide, 3 tall),
its foot at the origin: two half-ellipses meeting at the widest point, 0.42 of the way up, so the top is the pointier
end. The shell is a skin of facets (16 round, 17 up), each a thin closed tile so it's solid from every side, and each
painted by its egg's own rule, which is how the stripes, spots, cracks and bands are made with plain colours. Pieces
stuck on (crowns, gems, the ring) are ordinary closed shapes.

The cut. The egg is two halves cut across at its widest point: the bottom, and the top, whose every role ends in "Lid"
(ShellLid, WhiteLid, YolkLid...), which is how the game tells the two apart. Each half is closed by a disc of white with
a domed yolk in the middle, so whichever way a half lies, the cut shows white and yolk. Whole, the two halves' insides
meet and nothing of them shows.

The slice (split_pose here, EggModel.luau in the game, the same numbers as Config/Throw landing.split): the egg lands
upright; a white streak sweeps across its middle; the top slides a little way along the cut, tips over sideways and
lands upside down beside the bottom half, its white and yolk facing up, and rocks to a stop. The bottom half stays
where the egg landed, so the reveal (which keeps the egg where it lands) is unchanged.

Glowing roles are EggGlow, EggGlowB and YolkGlow, with their Lid twins (Neon in the game, shared/Roles.luau). The white
and yolk never get studs. No five- or six-pointed stars (owner, map 10): the Cosmic Egg's stars are four-point twinkles.
No stud texture in this file (kit.PREVIEW_STUDS off): plain colours, studs come from Studio's shared "Studs" material.
"""
import math
import os
import random
import subprocess
import sys
from pathlib import Path

from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_clockwork_citadel import Frame, gear, obox, tube, turn  # noqa: E402
from build_desert import beam  # noqa: E402
from build_forest import Model  # noqa: E402
from build_starfall_crater import ball, gem, sparkle  # noqa: E402
from build_thorn_kingdom_monsters import aim, blade, point, slab, thorn  # noqa: E402
from build_volcano import prism  # noqa: E402
from map_kit import limb, plate  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "eggs"
BLEND = "eggs"  # for export_fbx.py (MAP_OF_FILE) and check_map.py

LID = "Lid"  # every role of the top half ends in this
GLOW = {"EggGlow", "EggGlowB", "YolkGlow"}
GLOW_ROLES = GLOW | {g + LID for g in GLOW}
CLEAN = {"White", "Yolk"}  # the inside: never studded
kit.NO_STUDS.update(GLOW_ROLES | CLEAN | {c + LID for c in CLEAN})
GLOW_STRENGTH = 1.6  # the glowing roles' strength in the renders

# ---------------------------------------------------------------------- the shell

HEIGHT, RADIUS = 3.0, 1.2  # the thrown egg's size, ThrowController EGG_SIZE (Config/Throw landing.split.height)
WAIST = 0.42  # the widest point, as a share of the height up from the foot: where the egg is cut (landing.split.cut)
RINGS = (0.0, 0.035, 0.08, 0.14, 0.21, 0.28, 0.35, WAIST, 0.49, 0.56, 0.63, 0.70, 0.77, 0.84, 0.90, 0.95, 0.985, 1.0)
CUT = RINGS.index(WAIST)
SIDES = 16
SKIN = 0.07  # the shell's thickness
CUT_Z = WAIST * HEIGHT


def radius_at(t):
    """The egg's radius t of the way up: two half-ellipses meeting at the waist, the top one taller (the pointy end)."""
    u = (WAIST - t) / WAIST if t < WAIST else (t - WAIST) / (1 - WAIST)
    return RADIUS * math.sqrt(max(0.0, 1 - u * u))


def surface(t, a, out=0.0):
    """The point on the shell t of the way up, at angle a round it (0 is +X, pi/2 is +Y, the egg's front), lifted out
    from it by out, and the way out there."""
    r = radius_at(t)
    dz = 0.004
    dr = (radius_at(min(t + dz, 1)) - radius_at(max(t - dz, 0))) / (2 * dz * HEIGHT)
    n = Vector((math.cos(a), math.sin(a), -dr)).normalized() if r > 1e-6 else Vector((0, 0, 1 if t > 0.5 else -1))
    if t == WAIST:
        n = Vector((math.cos(a), math.sin(a), 0))
    p = Vector((r * math.cos(a), r * math.sin(a), t * HEIGHT))
    return p + n * out, n


class Facet:
    """One facet of the shell, for an egg's paint rule: ring k (up from the foot), side i (round from +X), t how far up
    its middle is (0 to 1), a its angle (0 is +X, pi/2 the egg's front, +Y), and lid, whether it's on the top half."""

    def __init__(self, k, i):
        self.k, self.i = k, i
        self.t = (RINGS[k] + RINGS[k + 1]) / 2
        self.a = (i + 0.5) * math.tau / SIDES
        self.lid = k >= CUT


def noise(*xs):
    """A repeatable 0..1 number for a facet, so patterns stay put between runs."""
    v = math.sin(sum(x * w for x, w in zip(xs, (12.9898, 78.233, 37.719, 19.19)))) * 43758.5453
    return v - math.floor(v)


def ring_vertex(k, i, inner=False):
    t = RINGS[k]
    a = i * math.tau / SIDES
    p, n = surface(t, a)
    if t in (0.0, 1.0):
        p = Vector((0, 0, t * HEIGHT))
    return p - n * SKIN if inner else p


def shell(m, paint):
    """The egg's skin: one thin closed tile per facet, coloured by paint(facet) -> role, its Lid twin above the cut."""
    last = len(RINGS) - 1
    for k in range(last):
        for i in range(SIDES):
            f = Facet(k, i)
            role = paint(f) + (LID if f.lid else "")
            if k == 0 or k + 1 == last:  # a wedge at either tip
                pole = 0 if k == 0 else last
                ring = k + 1 if k == 0 else k
                corners = [(pole, 0), (ring, i), (ring, i + 1)]
                outer = [ring_vertex(kk, ii) for kk, ii in corners]
                inner = [ring_vertex(kk, ii, True) for kk, ii in corners]
                m._add(role, [tuple(v) for v in outer + inner],
                       [[0, 1, 2], [5, 4, 3], [0, 3, 4, 1], [1, 4, 5, 2], [2, 5, 3, 0]])
                continue
            corners = [(k, i), (k, i + 1), (k + 1, i + 1), (k + 1, i)]
            outer = [tuple(ring_vertex(kk, ii)) for kk, ii in corners]
            inner = [tuple(ring_vertex(kk, ii, True)) for kk, ii in corners]
            m._ring_shape(role, outer, inner)


def inside(m, yolk="Yolk"):
    """What the cut shows on both halves: a disc of white closing each half, a domed yolk in its middle. Whole, the two
    meet inside the shell and none of it shows."""
    turn_by = 0.0  # line the white's corners up with the shell's, so its flat sides stay inside the facets
    white_r, yolk_r = RADIUS * 0.955, RADIUS * 0.44
    c = CUT_Z
    for up, suffix in ((1, ""), (-1, LID)):
        z0, z1 = c - up * 0.06, c + up * 0.025
        prism(m, "White" + suffix, 0, 0, min(z0, z1), max(z0, z1), white_r, white_r, SIDES, turn_by)
        steps = ((0.025, 0.06, 1.0, 1.0), (0.06, 0.095, 1.0, 0.8), (0.095, 0.12, 0.8, 0.5))
        for h0, h1, s0, s1 in steps:
            a, b = c + up * h0, c + up * h1
            if up > 0:
                prism(m, yolk + suffix, 0, 0, a, b, yolk_r * s0, yolk_r * s1, 12, 0)
            else:
                prism(m, yolk + suffix, 0, 0, b, a, yolk_r * s1, yolk_r * s0, 12, 0)


def on(role, z):
    """A stuck-on piece's role: its Lid twin when it sits above the cut."""
    return role + LID if z > CUT_Z else role


def egg(name, paint, yolk="Yolk", **colours):
    """An egg: its shell painted by paint(facet), its inside, and every colour also given to its Lid twin."""
    base = {"White": "#f7f3e8", "Yolk": "#ffbf1f", "YolkGlow": "#ffd23a", "Gold": "#f2c14e", **colours}
    m = Model(f"egg_{name}", {**base, **{k + LID: v for k, v in base.items()}})
    shell(m, paint)
    inside(m, yolk)
    return m


# ---------------------------------------------------------------------- the slice

# The same numbers as Config/Throw landing.split (EggModel.luau plays them), in seconds and studs at the egg's own size.
SPLIT = {"delay": 0.05, "slice": 0.14, "slide": 0.12, "fall": 0.42, "push": 0.42, "lift": 0.15, "gap": 0.3, "hop": 0.6, "rock": 0.16,
         "rockTime": 0.7, "sink": 0.04}


def smooth(u):
    return u * u * (3 - 2 * u)


def split_pose(s):
    """Where the top half is s seconds after the egg touches down: (across, up, tip), its cut's middle across from and up
    from the egg's foot, in studs at size 1, and how far it has tipped over (radians, towards +across). The same as
    EggModel.lidPose in the game."""
    c = CUT_Z
    flipped = HEIGHT - c - SPLIT["sink"]  # upside down, its tip on the ground, its cut this high
    beside = 2 * RADIUS + SPLIT["gap"]
    push = SPLIT["push"] * RADIUS
    t = s - SPLIT["delay"] - SPLIT["slice"]
    if t <= 0:
        return 0.0, c, 0.0
    lifted = c + SPLIT["lift"]  # lifted clear of the bottom half's yolk as it slides
    if t < SPLIT["slide"]:  # slides off along the cut
        u = smooth(t / SPLIT["slide"])
        return push * u, c + SPLIT["lift"] * u, 0.0
    t -= SPLIT["slide"]
    if t < SPLIT["fall"]:  # tips over and drops beside it, upside down
        v = t / SPLIT["fall"]
        return push + (beside - push) * v, lifted + (flipped - lifted) * v + SPLIT["hop"] * 4 * v * (1 - v), math.pi * smooth(v)
    t -= SPLIT["fall"]
    rock = SPLIT["rock"] * math.sin(t / SPLIT["rockTime"] * 3 * math.pi) * max(0.0, 1 - t / SPLIT["rockTime"]) ** 2
    return beside, flipped, math.pi + rock


def slice_streak(s):
    """The white streak across the egg's middle: (how far across, from -1 to 1, how see-through) or None."""
    t = s - SPLIT["delay"]
    if t < 0 or t > SPLIT["slice"] * 1.6:
        return None
    u = min(t / SPLIT["slice"], 1)
    return -1 + 2 * smooth(u), max(0.0, (t - SPLIT["slice"]) / (SPLIT["slice"] * 0.6))


# ---------------------------------------------------------------------- the eggs, cheapest first


def dirty_egg():
    def paint(f):
        n = noise(f.k, f.i, 1)
        if n < 0.12 or (f.t < 0.2 and n < 0.5):
            return "ShellB"  # dirt, dirtiest at the bottom
        return "ShellC" if n < 0.24 else "Shell"
    return egg("DirtyEgg", paint, Shell="#d6c6a1", ShellB="#94764f", ShellC="#bfa982")


SPOTS = ((0.3, 0.6, 0.55), (0.62, 1.9, 0.5), (0.2, 3.3, 0.45), (0.75, 4.2, 0.42), (0.48, 5.3, 0.5), (0.85, 0.9, 0.35),
         (0.12, 4.9, 0.4), (0.55, 3.0, 0.38), (0.38, 2.4, 0.3), (0.7, 5.9, 0.3))


def spotted_egg():
    def paint(f):
        for t, a, size in SPOTS:  # round-ish spots: how far the facet is from each spot's middle over the shell
            da = math.atan2(math.sin(f.a - a), math.cos(f.a - a)) * radius_at(f.t) / RADIUS
            if math.hypot(da, (f.t - t) * HEIGHT / RADIUS) < size:
                return "ShellB"
        return "ShellC" if noise(f.k, f.i, 2) < 0.08 else "Shell"
    return egg("SpottedEgg", paint, Shell="#a6dbb6", ShellB="#4b9867", ShellC="#d2f1dc")


def golden_egg():
    def paint(f):
        zig = 0.6 + 0.04 * (1 if f.i % 2 else -1)
        if abs(f.t - zig) < 0.045:
            return "ShellC"
        if 0.24 < f.t < 0.32:
            return "ShellB"
        return "Shell"
    m = egg("GoldenEgg", paint, Shell="#f0b832", ShellB="#ffe08a", ShellC="#b9801a")
    for t, a in ((0.78, 1.2), (0.5, 2.1)):  # a glint or two
        p, n = surface(t, a, 0.02)
        sparkle(m, on("ShellB", p.z), p.x, p.y, p.z, 0.22)
    return m


def lava_egg():
    def paint(f):
        if f.t < 0.09:
            return "EggGlow"  # lava pooling at its foot
        crack = math.sin(3 * f.a + 9 * f.t + 2.5 * noise(f.k // 2, f.i // 2, 3))
        if abs(crack) < 0.2 or (abs(math.sin(5 * f.a - 6 * f.t)) < 0.1 and f.t < 0.8):
            return "EggGlow"
        return "ShellB" if noise(f.k, f.i, 4) < 0.3 else "Shell"
    return egg("LavaEgg", paint, Shell="#3d2c28", ShellB="#2a1d1a", EggGlow="#ff6a14")


def frost_egg():
    def drip(i):
        return 0.74 + 0.05 * noise(i, 5) - (0.06 if i % 3 == 0 else 0)

    def paint(f):
        if f.t > drip(f.i):
            return "ShellB"  # the snow cap
        if f.t < 0.2:
            return "ShellC"
        return "Shell"
    m = egg("FrostEgg", paint, Shell="#a3d8f7", ShellB="#f2fbff", ShellC="#6db2e3", Ice="#d4f2ff")
    for i in range(0, SIDES, 2):  # icicles hanging from the cap's edge
        a = (i + 0.5) * math.tau / SIDES
        t = drip(i) - 0.01
        p, n = surface(t, a, -0.02)
        point(m, on("Ice", p.z), tuple(p + n * 0.05), tuple(p + n * 0.12 + Vector((0, 0, -0.32 - 0.12 * noise(i, 6)))), 0.12)
    for t, a, size in ((0.3, 1.3, 0.34), (0.22, 2.0, 0.24), (0.34, 0.6, 0.2)):  # ice crystals growing out of its side
        p, n = surface(t, a, -0.04)
        tip = p + (n + Vector((0, 0, 0.6))).normalized() * size * 2.2
        gem(m, on("Ice", p.z), *p.lerp(tip, 0.45), size * 0.4, size * 1.1, size * 0.9, 4, a)
    return m


def shadow_egg():
    def paint(f):
        wave = math.sin(2 * f.a + 10 * f.t)
        return "ShellB" if wave > 0.45 else "Shell"
    m = egg("ShadowEgg", paint, Shell="#36205a", ShellB="#6a3bb8", EggGlow="#dcbcff")
    for side in (-1, 1):  # two pale eyes glowing out of the dark: narrow, slanting down to the middle
        a = math.pi / 2 - side * 0.3
        p, n = surface(0.62, a, 0.01)
        f = Frame(m, tuple(p), aim(n) @ turn(y=-side * 0.45))
        slab(f, on("EggGlow", p.z), 0, 0, 0.0, 0.08, 0.06, 8, 3.2)
    return m


def abyss_egg():
    def paint(f):
        if noise(f.k, f.i, 7) < 0.1 and 0.12 < f.t < 0.9:
            return "EggGlow"  # glowing like the deep's lures
        if f.t < 0.25:
            return "ShellB"
        if abs(f.t - (0.62 + 0.05 * math.sin(4 * f.a))) < 0.04:
            return "ShellC"
        return "Shell"
    m = egg("AbyssEgg", paint, Shell="#0f3d5a", ShellB="#0a2438", ShellC="#2a7aa0", EggGlow="#4ff0e0")
    top = Vector((0, 0, HEIGHT - 0.02))  # an angler's lure bobbing over its top
    pts = [top, top + Vector((0, -0.1, 0.45)), top + Vector((0, 0.15, 0.85)), top + Vector((0, 0.6, 0.95)), top + Vector((0, 0.85, 0.75))]
    limb(m, "ShellC" + LID, [tuple(p) for p in pts], 0.12, 0.07)
    ball(m, "EggGlow" + LID, *(pts[-1] + Vector((0, 0.03, -0.18))), 0.17, 8, 4)
    return m


def cosmic_egg():
    def paint(f):
        if abs(f.t - (0.55 + 0.08 * math.sin(2 * f.a + 1))) < 0.06:
            return "ShellB"  # a band of nebula
        return "Shell"
    m = egg("CosmicEgg", paint, "YolkGlow", Shell="#1c1742", ShellB="#4a2f7a", EggGlow="#fff1b8")
    rng = random.Random(8)
    for _ in range(11):  # twinkling stars, four-pointed
        t, a = rng.uniform(0.12, 0.9), rng.uniform(0, math.tau)
        p, n = surface(t, a, 0.03)
        sparkle(m, on("EggGlow", p.z), p.x, p.y, p.z, rng.uniform(0.1, 0.17))
    ring = Frame(m, (0, 0, 1.0), turn(x=0.28, y=-0.12))  # a gold planet's ring round it, on the bottom half
    for i in range(24):
        a0, a1 = i * math.tau / 24, (i + 1) * math.tau / 24
        beam(m, "Gold", ring.at(1.78 * math.cos(a0), 1.78 * math.sin(a0), 0), ring.at(1.78 * math.cos(a1), 1.78 * math.sin(a1), 0), 0.32, 0.06)
    return m


def eclipse_egg():
    def paint(f):
        return "Shell" if f.lid else "ShellB"
    m = egg("EclipseEgg", paint, "YolkGlow", Shell="#16112b", ShellB="#2c2050", EggGlow="#ffc83c", EggGlowB="#3fe0a0")
    c = CUT_Z - 0.06  # the corona: a glowing gold band round its waist, on the bottom half, rays fanning up and out
    for i in range(SIDES):
        a0, a1 = i * math.tau / SIDES, (i + 1) * math.tau / SIDES
        r = RADIUS + 0.05
        beam(m, "EggGlow", (r * math.cos(a0), r * math.sin(a0), c), (r * math.cos(a1), r * math.sin(a1), c), 0.14, 0.12)
    for i in range(8):
        a = (i + 0.5) * math.tau / 8
        base = Vector((RADIUS * math.cos(a), RADIUS * math.sin(a), c - 0.05))
        out = Vector((math.cos(a), math.sin(a), 0))
        blade(m, "EggGlow", tuple(base), tuple(base + out * 0.42 + Vector((0, 0, -0.12))), (0, 0, 1), 0.16, 0.04)
    top = Vector((0, 0, HEIGHT))
    gem(m, "EggGlowB" + LID, *(top + Vector((0, 0, 0.12))), 0.17, 0.3, 0.12, 6)  # a jade gem
    return m


def forbidden_egg():
    def paint(f):
        if 0.12 < f.t < 0.18 or 0.8 < f.t < 0.86:
            return "Gold"  # gilt bands, like an old book's
        if 0.28 < f.t < 0.35:
            return "ShellC"  # the page edges
        return "ShellB" if noise(f.k, f.i, 9) < 0.12 else "Shell"
    m = egg("ForbiddenEgg", paint, "YolkGlow", Shell="#6d302a", ShellB="#57231f", ShellC="#f2e4c0", EggGlow="#b673ff")
    p, n = surface(0.6, math.pi / 2, 0.02)  # the clasp: a glowing violet gem in a gold setting
    f = Frame(m, tuple(p), aim(n))
    slab(f, "Gold" + LID, 0, 0, 0.0, 0.32, 0.08, 8)
    gem(m, "EggGlow" + LID, *(p + n * 0.1), 0.2, 0.16, 0.05, 8)
    for a in (0.3, 1.7, 3.1, 4.5, 5.9):  # gold corner studs
        for t in (0.15, 0.83):
            q, nq = surface(t, a, 0.03)
            obox(m, on("Gold", q.z), tuple(q), (0.18, 0.18, 0.18), aim(nq))
    return m


def carnival_egg():
    def paint(f):
        if 0.16 < f.t < 0.22 or 0.74 < f.t < 0.8:
            return "Gold"
        return "Shell" if ((f.i + f.k // 2) // 2) % 2 == 0 else "ShellB"  # candy stripes, twisting
    m = egg("CarnivalEgg", paint, "YolkGlow", Shell="#e8304a", ShellB="#fff3e0", EggGlow="#ffd27a")
    for i in range(10):  # a ring of warm bulbs round its waist
        a = (i + 0.25) * math.tau / 10
        p, n = surface(0.33, a, 0.05)
        ball(m, "EggGlow", *p, 0.11, 6, 3)
    ball(m, "Gold" + LID, 0, 0, HEIGHT + 0.12, 0.2, 8, 4)  # a gold pompom
    return m


def clockwork_egg():
    def paint(f):
        if 0.3 < f.t < 0.36 or 0.56 < f.t < 0.63:
            return "ShellB"  # riveted steel bands
        return "Shell"
    m = egg("ClockworkEgg", paint, "YolkGlow", Shell="#c98a2e", ShellB="#8a8f9c", EggGlow="#6fd6ff", Steel="#5f6470")
    for t in (0.33, 0.595):
        for i in range(12):
            p, n = surface(t, i * math.tau / 12 + 0.13, 0.02)
            obox(m, on("Gold", p.z), tuple(p), (0.09, 0.09, 0.09), aim(n))
    p, n = surface(0.7, 0.35, 0.03)  # a gear on its side
    gear(m, "Steel" + LID, tuple(p), 0.36, 10, 0.08, aim(n) @ turn(x=math.pi / 2), spokes=4)
    p, n = surface(0.2, math.pi / 2, 0.02)  # a gauge glowing blue
    f = Frame(m, tuple(p), aim(n))
    slab(f, "Gold", 0, 0, 0.0, 0.26, 0.06, 10)
    slab(f, "EggGlow", 0, 0, 0.03, 0.19, 0.05, 10)
    top = HEIGHT  # the wind-up key on top
    tube(m, "Steel" + LID, (0, 0, top - 0.1), (0, 0, top + 0.32), 0.07, 0.07, 6)
    for side in (-1, 1):
        f = Frame(m, (side * 0.2, 0, top + 0.42), turn(x=math.pi / 2))
        f.prism("Gold" + LID, 0, 0, -0.04, 0.04, 0.2, 0.2, 8)
    return m


def thorn_egg():
    def paint(f):
        wrap = (f.a / math.tau * 2 + f.t * 2.5) % 1  # violet briars spiralling round it
        return "ShellB" if wrap < 0.16 else "Shell"
    m = egg("ThornEgg", paint, "YolkGlow", Shell="#3a2342", ShellB="#6a2a44", Briar="#1c1016", EggGlow="#ff3355", EggGlowB="#ff9ab0")
    for k in range(14):  # thorns along the briars
        t = 0.12 + 0.055 * k
        a = ((0.08 - t * 2.5) / 2) * math.tau + 0.4
        p, n = surface(t, a, -0.02)
        thorn(m, on("Briar", p.z), tuple(p), tuple(p + (n + Vector((0, 0, 0.3))).normalized() * 0.34), 0.11)
    for t, a, size in ((0.3, math.pi / 2 + 0.3, 1.0), (0.2, math.pi / 2 - 0.9, 0.6), (0.62, math.pi / 2 - 0.6, 0.55)):  # glowing roses
        p, n = surface(t, a, 0.02)
        f = Frame(m, tuple(p), aim(n))
        for k in range(7):
            b = k * math.tau / 7
            f.beam(on("EggGlow", p.z), (0, 0.02, 0), (math.cos(b) * 0.36 * size, 0.07, math.sin(b) * 0.36 * size), 0.3 * size, 0.07, 0.2 * size)
        ball(m, on("EggGlowB", p.z), *(p + n * 0.1), 0.15 * size, 6, 3)
    t0 = 0.86  # a gold crown on its top, set with gems, sitting just proud of the shell
    z0 = t0 * HEIGHT
    r0 = radius_at(t0) + 0.05
    prism(m, "Gold" + LID, 0, 0, z0 - 0.08, z0 + 0.16, r0, r0 - 0.04, SIDES)
    for k in range(8):
        a = (k + 0.5) * math.tau / 8
        base = Vector(((r0 - 0.03) * math.cos(a), (r0 - 0.03) * math.sin(a), z0 + 0.1))
        point(m, "Gold" + LID, tuple(base), tuple(base + Vector((0.1 * math.cos(a), 0.1 * math.sin(a), 0.5 + 0.18 * (k % 2)))), 0.22)
        if k % 2:
            ball(m, "EggGlowB" + LID, (r0 + 0.02) * math.cos(a), (r0 + 0.02) * math.sin(a), z0 + 0.04, 0.08, 6, 3)
    return m


def spore_egg():
    def paint(f):
        if noise(f.k, f.i, 11) < 0.1 and 0.08 < f.t < 0.8:
            return "EggGlow"  # glowing spots
        return "ShellB" if f.t < 0.22 else "Shell"
    m = egg("SporeEgg", paint, "YolkGlow", Shell="#7a54a8", ShellB="#4a3166", EggGlow="#b8ff3a", Cap="#3c2a32", Stalk="#e2d8bd")
    # Mushrooms growing out of it, gills glowing under their black caps: a cluster on its top, two little ones lower down.
    for t, a, lean, h, r in ((1.0, 0.0, 0.0, 0.62, 0.42), (0.9, 0.9, 0.55, 0.42, 0.3), (0.88, 3.6, 0.6, 0.34, 0.25),
                             (0.3, 2.2, 1.0, 0.32, 0.18), (0.24, 2.75, 1.0, 0.22, 0.13)):
        p, n = surface(t, a, -0.04)
        up = (Vector((0, 0, 1)) + n * lean).normalized()
        tube(m, on("Stalk", p.z), tuple(p), tuple(p + up * h), 0.07 * r / 0.25, 0.06 * r / 0.25, 6)
        f = Frame(m, tuple(p + up * h), up.to_track_quat("Z", "Y").to_matrix())
        role = "EggGlow" + LID if p.z > CUT_Z else "EggGlow"
        cap_role = "Cap" + LID if p.z > CUT_Z else "Cap"
        f.prism(role, 0, 0, -0.05, 0.0, r * 0.82, r * 0.82, 10)
        f.prism(cap_role, 0, 0, 0.0, r * 0.35, r, r * 0.82, 10)
        f.prism(cap_role, 0, 0, r * 0.35, r * 0.6, r * 0.82, r * 0.3, 10)
    return m


def weeping_egg():
    def paint(f):
        lattice = (f.i + f.k) % 8 == 0 or (f.i - f.k) % 8 == 0  # fine silver filigree over ash black
        if lattice and 0.1 < f.t < 0.9:
            return "ShellB"
        return "Shell"
    m = egg("WeepingEgg", paint, "YolkGlow", Shell="#26262b", ShellB="#8e8e99", EggGlow="#ff2a2a", EggGlowB="#e6edf7", Silver="#dcdce4")
    p, n = surface(0.64, math.pi / 2, 0.02)  # a red eye (the only red: eyes) weeping pale light
    f = Frame(m, tuple(p), aim(n))
    slab(f, "Silver" + LID, 0, 0, 0.0, 0.3, 0.06, 10, 1.4)
    slab(f, "EggGlow" + LID, 0, 0, 0.03, 0.19, 0.05, 10, 1.3)
    for k, (a, t0, t1) in enumerate(((math.pi / 2 - 0.12, 0.6, 0.47), (math.pi / 2 + 0.12, 0.6, 0.5))):
        prev = None
        for j in range(6):  # tears running down, onto the bottom half
            t = t0 + (0.12 - t0) * j / 5
            q, _ = surface(t, a + 0.03 * math.sin(j * 1.7 + k), 0.025)
            if prev is not None:
                beam(m, on("EggGlowB", (prev.z + q.z) / 2), tuple(prev), tuple(q), 0.07, 0.04)
            prev = q
    halo = HEIGHT + 0.3  # a glowing halo floating over its tip
    for i in range(20):
        a0, a1 = i * math.tau / 20, (i + 1) * math.tau / 20
        beam(m, "EggGlowB" + LID, (0.72 * math.cos(a0), 0.72 * math.sin(a0), halo), (0.72 * math.cos(a1), 0.72 * math.sin(a1), halo), 0.13, 0.1)
    for side in (-1, 1):  # silver wings of filigree at its waist, on the bottom half
        for k in range(3):
            base = Vector((side * (RADIUS - 0.04), -0.1 * k, CUT_Z - 0.12 - 0.12 * k))
            blade(m, "Silver", tuple(base), tuple(base + Vector((side * (0.55 - 0.1 * k), -0.15, 0.32 - 0.08 * k))), (0, 0, 1), 0.2, 0.05)
    return m


# In Config/Eggs order (cheapest first): the ids are the models' names after "egg_".
ALL = [dirty_egg, spotted_egg, golden_egg, lava_egg, frost_egg, shadow_egg, abyss_egg, cosmic_egg, eclipse_egg, forbidden_egg,
       carnival_egg, clockwork_egg, thorn_egg, spore_egg, weeping_egg]


# ---------------------------------------------------------------------- renders


def pose_lid(root, pose):
    """Puts the top half's meshes where split_pose says: (across, up, tip) in the egg's own frame."""
    across, up, tip = pose
    m = Matrix.Translation((across, 0, up)) @ Matrix.Rotation(tip, 4, "Y") @ Matrix.Translation((0, 0, -CUT_Z))
    for child in root.children:
        if child.name.endswith(LID):
            child.matrix_basis = m  # relative to the egg (Model.build parents with no inverse)


def stage(models):
    import bpy
    from monster_stage import light_up, set_sky
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    eggs = bpy.data.collections.new("Props")  # export_fbx.py sends this collection to fbx/00_Eggs/Props
    scene.collection.children.link(eggs)
    roots = []
    for i, model in enumerate(models):
        root = model.build(eggs)
        root.location = (i * 5.0, 0, 0)
        roots.append(root)
    light_up(roots, GLOW_ROLES, GLOW_STRENGTH)
    ground = bpy.data.meshes.new("Ground")
    ground.from_pydata([(-200, -200, -0.005), (300, -200, -0.005), (300, 200, -0.005), (-200, 200, -0.005)], [], [(0, 1, 2, 3)])
    ground.materials.append(kit.material("Ground", "#5a7a4a", False))
    scene.collection.objects.link(bpy.data.objects.new("Ground", ground))
    set_sky(scene, "#1f2430")
    bpy.context.view_layer.update()
    return scene, roots


def stills(scene, models, roots):
    for model, root in zip(models, roots):
        kit.set_visible(roots, [root])
        c = root.location + Vector((0, 0, 1.75))
        kit.shoot(scene, model.name, c + Vector((2.2, 6.2, 1.6)), c, (500, 500), 50)
        pose_lid(root, split_pose(10))
        c = root.location + Vector((1.35, 0, 0.8))
        kit.shoot(scene, f"{model.name}_split", c + Vector((1.4, 6.0, 4.4)), c, (500, 500), 50)
        pose_lid(root, (0, CUT_Z, 0))
    kit.set_visible(roots, roots)
    if len(models) == len(ALL):  # the lineups: every still in price order, five to a row
        for suffix in ("", "_split"):
            inputs = []
            for model in models:
                inputs += ["-i", str(RENDERS / f"{model.name}{suffix}.png")]
            rows = ";".join(f"{''.join(f'[{5 * r + c}]' for c in range(5))}hstack=5[r{r}]" for r in range(3))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", f"{rows};[r0][r1][r2]vstack=3",
                            str(RENDERS / f"lineup{suffix}.png")], check=True)


def slice_video(scene, models, roots, picks):
    """Each picked egg in turn, close up, landing and being cut in half, at 30 frames a second: the same moves and
    numbers as the game."""
    import bpy
    frames = RENDERS / "slice_frames"
    frames.mkdir(exist_ok=True)
    streak = Model("Streak", {"Streak": "#ffffff"})
    streak.block("Streak", 0, 0, 0, 1.0, 0.16, 0.16)  # EggModel.luau STREAK_THICK
    streak_root = streak.build(scene.collection)
    from monster_stage import light_up
    light_up([streak_root], {"Streak"}, 4.0)
    data = bpy.data.cameras.new("Slice")
    data.lens = 45
    camera = bpy.data.objects.new("Cam_Slice", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = 960, 640
    number = 0
    for name in picks:
        index = next(i for i, m in enumerate(models) if m.name == f"egg_{name}")
        root = roots[index]
        kit.set_visible(roots, [root])
        foot = root.location.copy()
        drop = 0.35  # it comes down out of the sky, tumbling, for this long before touching down
        for f in range(int((drop + 1.7) * 30)):
            s = f / 30 - drop
            if s < 0:  # falling in
                u = -s / drop
                root.location = foot + Vector((0, -u * 6, u * 5))
                root.rotation_euler = (u * 7, 0, 0)
                pose_lid(root, (0, CUT_Z, 0))
            else:
                root.location = foot
                root.rotation_euler = (0, 0, 0)
                bpy.context.view_layer.update()
                pose_lid(root, split_pose(s))
            sweep = slice_streak(s) if s >= 0 else None
            for child in streak_root.children:
                child.hide_render = sweep is None
            if sweep:
                streak_root.location = foot + Vector((sweep[0] * RADIUS * 1.6, 0, CUT_Z))
                streak_root.scale = (RADIUS * 1.4 * (1 - sweep[1]), 1, 1)
            target = foot + Vector((1.35, 0, 1.0))
            camera.location = target + Vector((2.0, 7.6, 3.6))
            camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
            bpy.context.view_layer.update()
            scene.render.filepath = str(frames / f"f{number:04d}.png")
            bpy.ops.render.render(write_still=True)
            number += 1
        root.location = foot
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", str(frames / "f%04d.png"), "-pix_fmt", "yuv420p",
                    str(RENDERS / "egg_slice.mp4")], check=True)
    for frame in frames.glob("*.png"):
        frame.unlink()
    frames.rmdir()
    bpy.data.objects.remove(camera)
    for child in list(streak_root.children):
        bpy.data.objects.remove(child)
    bpy.data.objects.remove(streak_root)


def main():
    import bpy
    builders = ALL
    only = os.environ.get("ONLY")
    if only:
        builders = [b for b in builders if b.__name__ in only.split(",")]
    models = [b() for b in builders]
    for model in models:
        print(f"  {model.name}: {sum(len(x) - 2 for _, f in model.parts.values() for x in f)} triangles, roles {sorted(model.parts)}")
    scene, roots = stage(models)
    if not only:
        for root in roots:  # saved standing at the origin, whole, ready for export_fbx.py
            root.location = (0, 0, 0)
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE / f"{BLEND}.blend"))
        for i, root in enumerate(roots):
            root.location = (i * 5.0, 0, 0)
        bpy.context.view_layer.update()
    stills(scene, models, roots)
    if "stills" not in sys.argv:
        picks = [n for n in ("DirtyEgg", "LavaEgg", "CosmicEgg", "ClockworkEgg", "WeepingEgg") if any(m.name == f"egg_{n}" for m in models)]
        slice_video(scene, models, roots, picks)


if __name__ == "__main__":
    main()
