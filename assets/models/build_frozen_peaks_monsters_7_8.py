"""Builds the Frozen Peaks' 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_frozen_peaks_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_frozen_peaks_monsters_7_8.py    (stills only)
    ONLY=ramvalanche QUICK=1 ...                                                   (just that one)

Saves frozen_peaks_monsters_7_8.blend and renders to design/world/monsters_frozen_peaks_7_8/. The first six are in
build_frozen_peaks_monsters.py; what this batch shares is in rare_kit.py.

The owner asked for 8 monsters a map (2026-11-06): two more each, nicer than the ones before, more aggressive map by map.
The Volcano's pair lunge and spit from where they stand. These two throw their whole bodies at you.

  Ramvalanche  a mountain ram gone wrong: a shaggy fleece frozen into icicles, crystals growing out of its back, two great curled
               horns of blue ice, and a fanged mouth a ram should never have. It paws the ground, then charges
  Abominator   the thing on top of the mountain: a yeti, huge and hunched, with a bare dark face that's mostly mouth, ice
               tusks and crystals growing out of its shoulders. It heaves both fists over its head and smashes the ground

The frost face (build_frozen_peaks_monsters.py) gone harder: small icy eyes with a thin slit in a black socket, no white.

What moves: the usual walk, idle and roar, and from rare_kit.py (SWAY in DinoLifeController): Kick1 to 4 (a charge, with snow flying
off its hooves), Shard1 to 6 (a smash, with ice bursting off the ground) and Sway bones.

Skin roles Body, Accent, Belly and Claw take the colour mutations; horns, ice and the face keep theirs. EyeGlow and IceGlow
glow (both already in shared/Roles.luau). Built at the first map's size. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0.
"""
import math
import random
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402  (first: it turns the stud preview off)
from build_desert import beam  # noqa: E402
from build_forest import Model  # noqa: E402
from build_spore_hollow_monsters import egg  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from rare_kit import curve, jointed, sabre, scallop, slit_eye, sweep, swing  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_frozen_peaks_7_8"
BLEND = "frozen_peaks_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = {"EyeGlow", "IceGlow"}

FACE = {"EyeGlow": "#2ec4ff", "Pupil": "#0a1826", "Highlight": "#ffffff", "Mouth": "#16233a", "Tongue": "#3e6f9c", "Teeth": "#eafcff", "Socket": "#070d16",
        "Ice": "#9fdcff", "IceGlow": "#45d6ff"}
SKY, FLOOR = "#a6c6e4", "#7c9cbd"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


def crystal(m, role, base, tip, width):
    """A six-sided crystal: straight sides and a sharp point."""
    a, b = Vector(base), Vector(tip)
    sweep(m, role, [(tuple(a), width * 0.7, width * 0.7), (tuple(a.lerp(b, 0.62)), width, width), (tuple(b), 0.02, 0.02)], sides=6)


def cluster(m, spots):
    """A clump of crystals growing out of the hide: (base, lean, height, width) each, the tallest glowing."""
    for i, (base, lean, tall, width) in enumerate(spots):
        b = Vector(base)
        crystal(m, "IceGlow" if i % 3 != 2 else "Ice", tuple(b - Vector(lean) * 0.4), tuple(b + Vector(lean) * tall), width)


def chunk(m, name, n, at, size, parent="Spine", role="Ice"):
    """A lump of ice on its own bone, parked out of sight inside the body until it's thrown (FLING in rare_kit.py)."""
    m.use(f"{name}{n}", at, parent)
    x, y, z = at
    sweep(m, role, [((x, y, z - size), 0.04, 0.04), ((x + size * 0.1, y, z - size * 0.15), size * 1.1, size * 0.9), ((x - size * 0.1, y, z + size * 0.25), size * 0.8, size * 0.8), ((x, y, z + size), 0.04, 0.04)], sides=5)


def shag(m, role, points, widths, rng, length=1.4, per_ring=7, thick=0.7, hang=0.7):
    """Rough fur round a limb: spikes all round each of the points, hanging down and back."""
    roles = (role,) if isinstance(role, str) else role
    for i, (p, w) in enumerate(zip(points, widths)):
        for k in range(per_ring):
            a = (k + rng.uniform(0, 0.8)) * math.tau / per_ring
            out = Vector((math.cos(a), math.sin(a) * 0.9, 0.0))
            base = Vector(p) + out * w * 0.42
            tip = base + out * length * 0.5 + Vector((0, -0.25, -hang)) * length * rng.uniform(0.8, 1.2)
            point(m, roles[i % len(roles)], tuple(base), tuple(tip), thick)


def pelt(m, centre, radii, lats, rng, density=20, tuft=2.6, width=2.4, roles=("Body", "Belly"), keep=None):
    """Chunky fleece over a dome: rings of tufts from the crown down, each lying down the slope. One colour a ring: tufts
    overlap, so alternating them round a ring would only stripe it."""
    c = Vector(centre)
    for k, lat in enumerate(lats):
        count = max(6, round(density * math.cos(lat)))
        for j in range(count):
            a = (j + 0.5 * (k % 2) + rng.uniform(-0.15, 0.15)) * math.tau / count
            out = Vector((math.cos(a) * math.cos(lat), math.sin(a) * math.cos(lat), math.sin(lat)))
            down = Vector((math.cos(a) * math.sin(lat), math.sin(a) * math.sin(lat), -math.cos(lat)))
            spot = c + Vector((out.x * radii[0], out.y * radii[1], out.z * radii[2]))
            if keep and not keep(spot):
                continue
            tip = spot + (down + out * 0.42) * tuft * rng.uniform(0.85, 1.2)
            point(m, roles[k % len(roles)], tuple(spot - out * 0.5), tuple(tip), width)


# ---------------------------------------------------------------------- Ramvalanche


def spiral_horn(m, side):
    """A great curled ram's horn: up from the brow, back over, down and forward round the cheek, ridged all along. The tip
    turns to burning ice."""
    centre, r0, a0 = Vector((side * 2.0, 7.2, 11.2)), 3.9, 0.5
    count = 46
    path, tip = [], []
    for i in range(count):
        t = i / (count - 1)
        a = a0 + t * math.tau * 1.32
        r = r0 * (1 - 0.6 * t)
        p = centre + Vector((side * (0.1 + 4.6 * t ** 1.4), math.cos(a) * r, math.sin(a) * r))
        w = (2.5 * (1 - t) ** 0.8 + 0.06) * (1.1 if i % 2 else 0.94)
        (path if t < 0.66 else tip).append((tuple(p), w, w))
    sweep(m, "Horn", path + tip[:1], sides=6)
    sweep(m, "IceGlow", path[-1:] + tip, sides=6)


def ram_leg(m, bone, x, y, top, rng):
    """A bare dark leg out of the fleece, on a heavy split hoof."""
    m.use(bone, (x, y, top))
    side = 1 if x > 0 else -1
    knee = (x + side * 0.1, y + 0.2, top * 0.55)
    ankle = (x + side * 0.1, y - 0.1, 1.5)
    sweep(m, "Accent", [((x, y, top), 2.6, 3.0), (knee, 1.8, 2.0), (ankle, 1.2, 1.3), ((x + side * 0.1, y + 0.1, 0.9), 1.7, 1.8)], sides=8)
    for dx in (-0.5, 0.5):  # the two halves of the hoof, and an ice spike off each
        sweep(m, "Claw", [((x + dx, y + 0.1, 1.0), 1.0, 1.7), ((x + dx, y + 0.5, 0.02), 1.15, 2.4)], sides=6)
        point(m, "Claw", (x + dx, y + 1.3, 0.3), (x + dx, y + 2.1, 0.03), 0.6)
    shag(m, "Belly", [(x, y, top * 0.8), (x, y, top * 0.62)], [2.6, 2.3], rng, length=1.5, per_ring=6, thick=0.9, hang=0.9)
    m.bone = "Spine"


def ramvalanche():
    """A monstrous mountain ram, head down, horns first."""
    m = monster("dino_Ramvalanche", Body="#c9d9e8", Accent="#27354c", Belly="#94b2ce", Claw="#0f1826", Horn="#6b90b8")
    rng = random.Random(55)
    m.joint("Spine", (0, -2.6, 6.8))

    # The body under the fleece.

    ram_leg(m, "FrontL", -3.0, 3.6, 6.0, rng)
    ram_leg(m, "FrontR", 3.0, 3.6, 6.0, rng)
    ram_leg(m, "BackL", -3.1, -6.0, 6.2, rng)
    ram_leg(m, "BackR", 3.1, -6.0, 6.2, rng)

    # The fleece: tiers hanging one over the other, pale and shadow by turns, a hem of icicles along the bottom.
    egg(m, "Body", (0, -1.2, 7.9), 5.3, 8.9, 4.9, 12, 7)
    pelt(m, (0, -1.2, 7.9), (5.4, 9.0, 5.0), (1.32, 1.08, 0.82, 0.56, 0.3, 0.06), rng, density=22, tuft=2.7, width=2.5)
    for k in range(18):
        a = k * math.tau / 18 + 0.1
        x, y = math.cos(a) * 6.1, -1.2 + math.sin(a) * 10.0
        z = 6.3 + 0.3 * (k % 3)
        crystal(m, "Ice", (x, y, z + 0.6), (x * 1.02, y, z - 1.0 - 0.45 * (k % 2)), 0.62)

    # Crystals breaking out along its back.
    cluster(m, [((0, 3.2, 12.0), (0.0, 0.1, 1), 2.4, 1.1), ((0.9, 2.5, 12.0), (0.3, -0.1, 1), 1.5, 0.8), ((-0.9, 2.4, 11.9), (-0.3, 0.0, 1), 1.7, 0.8),
                ((0, 0.4, 12.5), (0.0, -0.2, 1), 3.2, 1.3), ((1.1, -0.4, 12.2), (0.35, -0.2, 1), 2.1, 0.9), ((-1.1, -0.2, 12.2), (-0.35, -0.2, 1), 1.9, 0.9),
                ((0, -2.8, 12.4), (0.0, -0.3, 1), 2.8, 1.2), ((0.9, -3.6, 12.1), (0.3, -0.3, 1), 1.6, 0.8), ((-1.0, -3.4, 12.0), (-0.3, -0.3, 1), 1.8, 0.8),
                ((0, -5.5, 11.7), (0.0, -0.4, 1), 2.0, 1.0)])

    # A stump of a tail, frozen stiff.
    path = [(p, w, w) for p, w in zip(curve([(0, -9.8, 9.4), (0, -11.0, 9.3), (0, -12.0, 8.6), (0, -12.4, 7.5)], 5), (2.2, 2.0, 1.7, 1.1, 0.2))]
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], path)
    m.bone = "Tail2"
    for dx in (-0.5, 0, 0.5):
        crystal(m, "Ice", (dx, -12.0, 8.4), (dx * 1.3, -12.2, 6.2), 0.5)
    m.bone = "Spine"

    # The neck, thick, low and thrust forward, under a mane of frozen wool.
    m.joint("Neck", (0, 5.2, 9.2), "Spine")
    rings = [((0, 4.0, 9.4), 6.4, 6.0), ((0, 5.8, 9.5), 5.6, 5.2), ((0, 7.4, 9.5), 4.6, 4.3), ((0, 8.6, 9.6), 4.0, 3.9)]
    sweep(m, "Body", rings, ["Spine", "Neck", "Neck", "Neck"], sides=10)
    m.bone = "Neck"
    for k, (y, r, length) in enumerate(((7.6, 3.1, 3.1), (6.2, 3.9, 3.7), (4.8, 4.7, 4.3))):
        for j in range(13):
            a = j * math.tau / 13 + 0.2 * k
            base = Vector((math.cos(a) * r * 0.8, y, 9.6 + math.sin(a) * r * 0.8))
            tip = base + Vector((math.cos(a) * 0.9, -1.6, math.sin(a) * 0.8 - 1.4)) * (length / 3)
            point(m, "Body" if k % 2 else "Belly", tuple(base), tuple(tip), 1.5)

    # The head: long, dark, low. Its bony brow is what it hits you with.
    m.use("Head", (0, 8.4, 9.8), "Neck")
    zm = 7.7
    skull = [((0, 8.0, 9.9), 4.4, 4.2), ((0, 9.5, 9.85), 5.0, 4.1), ((0, 11.0, 9.3), 4.4, 3.2), ((0, 12.4, 8.65), 3.1, 2.3), ((0, 13.6, 8.25), 2.6, 1.6), ((0, 14.3, 8.05), 1.7, 1.0)]
    sweep(m, "Accent", skull, sides=8)
    sweep(m, "Horn", [((0, 9.0, 11.5), 4.4, 1.1), ((0, 10.2, 11.4), 3.7, 1.1), ((0, 11.2, 10.7), 1.6, 0.8)], sides=6)  # the battering plate
    for side in (-1, 1):
        spiral_horn(m, side)
        look = (side * 0.42, 0.9, -0.14)
        egg(m, "Socket", (side * 1.86, 11.0, 9.75), 0.92, 0.5, 0.66, 10, 5)
        slit_eye(m, (side * 1.94, 11.4, 9.7), 0.5, look, side, iris="EyeGlow", lid_role="Accent", top=0.56, tilt=0.8, low=0.4)
        for a, b in (((side * 0.15, 12.0, 9.85), (side * 0.75, 12.9, 9.2)), ((side * 0.75, 12.9, 9.2), (side * 0.5, 13.7, 8.8)), ((side * 0.75, 12.9, 9.2), (side * 1.4, 13.3, 8.4))):
            beam(m, "IceGlow", a, b, 0.14, 0.12, 0.1)
        beam(m, "Horn", (side * 3.1, 10.4, 11.1), (side * 0.3, 12.2, 9.75), 0.86, 0.74, 0.42)
        egg(m, "Mouth", (side * 0.55, 14.05, 8.32), 0.2, 0.12, 0.14, 6, 3)  # nostrils
        # An ear flat back, torn, as an angry ram's would be.
        sabre(m, "Accent", [(side * 2.4, 8.2, 8.9), (side * 3.5, 7.2, 8.2), (side * 4.1, 6.2, 7.6)], 1.2, 5, flat=0.5)
    sweep(m, "Mouth", [((0, 8.4, zm + 0.04), 4.0, 0.16), ((0, 12.6, zm + 0.0), 2.6, 0.14), ((0, 14.1, zm + 0.1), 1.3, 0.12)], sides=8)
    egg(m, "Mouth", (0, 8.8, zm - 0.7), 1.6, 0.5, 1.1, 8, 5)
    for side in (-1, 1):
        for k in range(7):
            t = k / 6
            y, x = 9.4 + 4.6 * t, side * (1.95 - 1.0 * t * t)
            point(m, "Teeth", (x, y, zm + 0.08), (x, y + 0.04, zm - 0.5 - 0.28 * (k % 2)), 0.34)
        sabre(m, "Teeth", [(side * 1.5, 12.5, zm + 0.1), (side * 1.56, 12.6, zm - 0.6), (side * 1.45, 12.4, zm - 1.5)], 0.56, 5, power=1.2)  # fangs no ram should have

    m.use("Jaw", (0, 8.5, zm - 0.02), "Head")
    z = zm - 0.42
    sweep(m, "Accent", [((0, 8.5, z), 3.9, 0.9), ((0, 11.4, z), 3.0, 0.8), ((0, 13.4, z + 0.05), 1.9, 0.6)], sides=8)
    sweep(m, "Mouth", [((0, 8.6, z + 0.4), 3.2, 0.1), ((0, 13.2, z + 0.34), 1.3, 0.1)], sides=8)
    sweep(m, "Tongue", [((0, 9.4, z + 0.48), 1.6, 0.2), ((0, 12.1, z + 0.44), 0.8, 0.16)], sides=6)
    for side in (-1, 1):
        for k in range(6):
            t = k / 5
            y, x = 9.6 + 3.6 * t, side * (1.6 - 0.8 * t * t)
            point(m, "Teeth", (x, y, z + 0.34), (x, y + 0.03, z + 0.8 + 0.18 * (k % 2)), 0.3)
    # A beard of icicles.
    for dx, y, drop in ((0, 12.9, 2.6), (-0.6, 12.2, 2.0), (0.6, 12.2, 2.0), (-1.1, 11.3, 1.5), (1.1, 11.3, 1.5)):
        crystal(m, "Ice", (dx, y, z - 0.3), (dx * 1.05, y - 0.15, z - 0.3 - drop), 0.62)
    swing(m, ["Jaw"], (0, 8.5, zm - 0.02), -0.48)

    # Snow it kicks up as it charges, hidden in its belly until then.
    for n, size in ((1, 1.5), (2, 1.3), (3, 1.3), (4, 1.1)):
        chunk(m, "Kick", n, (0, -1.0, 8.0), size, parent="Root")
    m.bone = "Head"
    m.head_centre = (0, 12.0, 9.0)
    return m


# ---------------------------------------------------------------------- Abominator


def abominator():
    """A huge hunched yeti, fists down, its head low in front of its shoulders and its face mostly mouth."""
    m = monster("dino_Abominator", Body="#c9d9e8", Accent="#1d2a40", Belly="#94b2ce", Claw="#0c1420", Tusk="#d9f3ff")
    rng = random.Random(12)
    m.joint("Spine", (0, -1.4, 7.0))

    # The trunk: hips to huge shoulders, leaning forward.
    trunk = [((0, -2.6, 5.6), 6.4, 4.8), ((0, -2.0, 7.0), 8.0, 6.2), ((0, -0.9, 9.0), 9.6, 7.4), ((0, 0.6, 11.0), 11.6, 8.0), ((0, 2.0, 12.6), 11.4, 7.0), ((0, 3.0, 13.6), 7.4, 4.6)]
    sweep(m, "Belly", trunk, sides=10, up=(0, 1, 0.2))

    # Fur in hanging tiers from the shoulders down, one colour a tier.
    tiers = [((2.2, 1.0), (4.2, 3.2), 15.0, 13.0, "Body", 13), ((1.7, 0.9), (6.0, 4.2), 14.2, 11.6, "Belly", 16), ((1.0, 0.8), (6.6, 4.9), 12.6, 9.7, "Body", 18), ((0.2, 0.7), (6.0, 4.9), 10.6, 7.8, "Belly", 18),
             ((-0.8, 0.6), (5.2, 4.5), 8.8, 5.9, "Body", 17), ((-1.6, 0.5), (4.7, 4.0), 6.9, 4.0, "Belly", 16)]
    for k, ((y, _), radii, top, tip, role, count) in enumerate(tiers):
        scallop(m, (role,), (0, y), radii, top, tip, count, 0.18, thick=0.55, offset=0.17 * k)
    egg(m, "Body", (0, 2.2, 14.3), 4.6, 3.4, 1.7, 10, 5)

    # Crystals growing out of its shoulders and back: the mountain has started to grow on it.
    for side in (-1, 1):
        cluster(m, [((side * 4.2, 1.6, 14.6), (side * 0.35, -0.1, 1), 3.4, 1.4), ((side * 3.1, 0.7, 14.9), (side * 0.1, -0.3, 1), 2.5, 1.1), ((side * 5.2, 2.2, 14.0), (side * 0.7, 0.1, 1), 2.4, 1.1),
                    ((side * 4.6, 0.4, 13.8), (side * 0.6, -0.4, 1), 1.9, 0.9), ((side * 2.0, -0.6, 14.0), (side * 0.2, -0.6, 1), 2.0, 0.9)])
    cluster(m, [((0, -1.0, 13.8), (0, -0.5, 1), 2.4, 1.1), ((0, -3.0, 11.6), (0, -0.8, 0.8), 2.0, 1.0), ((1.4, -3.5, 10.2), (0.25, -0.9, 0.6), 1.6, 0.8), ((-1.4, -3.6, 9.8), (-0.25, -0.9, 0.6), 1.5, 0.8)])

    # Legs: short and huge, on big dark feet.
    for letter, side in (("L", -1), ("R", 1)):
        hip = (side * 3.2, -1.8, 6.4)
        knee = (side * 3.9, -1.0, 3.7)
        ankle = (side * 4.0, -1.4, 1.5)
        m.use(f"Leg{letter}", hip)
        sweep(m, "Body", [(hip, 4.6, 4.6), ((side * 3.7, -1.3, 4.9), 4.7, 4.8), (knee, 3.9, 4.0)], sides=8)
        shag(m, "Body", [(side * 3.5, -1.5, 5.8), (side * 3.8, -1.2, 4.6)], [4.2, 4.2], rng, length=1.7, per_ring=8, thick=1.0, hang=0.9)
        m.use(f"Shin{letter}", knee, f"Leg{letter}")
        sweep(m, "Belly", [(knee, 3.9, 4.0), ((side * 4.0, -1.2, 2.4), 3.3, 3.5), (ankle, 3.0, 3.2)], sides=8)
        shag(m, "Belly", [(side * 3.9, -1.1, 3.3), (side * 4.0, -1.2, 2.2)], [3.6, 3.2], rng, length=1.6, per_ring=8, thick=0.9, hang=1.0)
        sweep(m, "Accent", [((side * 4.0, -2.6, 0.75), 3.0, 1.5), ((side * 4.1, -0.6, 0.85), 3.6, 1.7), ((side * 4.2, 1.6, 0.6), 3.4, 1.15)], sides=8)
        for dx in (-1.15, -0.4, 0.4, 1.15):
            base = (side * 4.2 + dx, 1.8, 0.5)
            sabre(m, "Claw", [base, (base[0], base[1] + 0.7, 0.5), (base[0], base[1] + 1.2, 0.03)], 0.62, 4)

    # Arms: longer than its legs, hanging to fists like boulders.
    for letter, side in (("L", -1), ("R", 1)):
        shoulder = (side * 6.0, 2.0, 12.6)
        elbow = (side * 8.5, 3.2, 8.2)
        wrist = (side * 8.3, 5.4, 4.2)
        m.use(f"Arm{letter}", shoulder)
        arm = curve([shoulder, elbow, wrist], 7)
        widths = (4.9, 5.3, 5.0, 4.4, 4.0, 3.8, 3.6)
        sweep(m, "Body", [(p, w, w) for p, w in zip(arm, widths)], sides=8)
        shag(m, ("Body", "Belly"), arm[:6], widths, rng, length=2.0, per_ring=9, thick=1.2, hang=1.0)
        fist = (side * 8.3, 6.2, 2.6)
        sweep(m, "Accent", [(wrist, 3.1, 3.2), ((side * 8.3, 5.9, 3.2), 4.3, 4.2), (fist, 4.8, 4.4), ((side * 8.3, 6.9, 1.6), 4.2, 3.0)], sides=8)
        for dx in (-1.5, -0.5, 0.5, 1.5):
            knuckle = (side * 8.3 + dx, 7.7, 2.8)
            egg(m, "Accent", knuckle, 0.72, 0.74, 0.84, 6, 4)
            sabre(m, "Claw", [(knuckle[0], 8.0, 2.4), (knuckle[0], 8.9, 1.5), (knuckle[0], 8.9, 0.22)], 0.74, 5)
        crystal(m, "IceGlow", (side * 9.0, 4.6, 7.0), (side * 11.2, 3.9, 8.2), 1.1)
        crystal(m, "Ice", (side * 9.2, 5.3, 5.3), (side * 11.0, 5.0, 5.9), 0.8)
    m.bone = "Spine"

    # The neck: there isn't one. The head hangs in front of its chest.
    m.joint("Neck", (0, 3.2, 12.0), "Spine")
    m.bone = "Neck"
    sweep(m, "Body", [((0, 2.6, 12.4), 7.2, 6.2), ((0, 4.2, 12.1), 6.8, 5.8)], sides=8)

    # The head: a dark bare face in a ruff of fur.
    m.use("Head", (0, 4.2, 12.0), "Neck")
    zm = 11.5
    sweep(m, "Accent", [((0, 4.2, 13.0), 5.6, 4.2), ((0, 6.0, 13.3), 6.4, 3.8), ((0, 7.4, 13.15), 5.8, 3.0), ((0, 8.4, 12.75), 4.6, 2.0), ((0, 8.9, 12.45), 3.2, 1.1)], sides=8)
    sweep(m, "Accent", [((0, 4.6, 12.0), 6.2, 1.0), ((0, 6.6, 12.0), 6.0, 1.0), ((0, 8.0, 12.0), 4.8, 0.9), ((0, 9.0, 12.05), 3.0, 0.7)], sides=8)  # the upper lip, thin and drawn back off the teeth
    sweep(m, "Accent", [((0, 8.2, 12.9), 2.0, 1.2), ((0, 9.4, 12.6), 1.9, 0.9), ((0, 9.85, 12.3), 2.3, 0.8)], sides=6)  # the bridge of the nose
    pelt(m, (0, 5.2, 13.2), (3.9, 3.7, 2.7), (1.3, 1.0, 0.65, 0.3), rng, density=15, tuft=2.1, width=2.0, roles=("Body", "Belly"), keep=lambda spot: spot.y < 6.9)  # fur over its skull, down to the bare face
    for k, (y, r, length) in enumerate(((6.6, 3.6, 2.2), (5.3, 4.0, 3.0))):  # the ruff, round the bare face
        for j in range(15):
            a = j * math.tau / 15 + 0.2 * k
            if math.sin(a) < 0 and abs(math.cos(a)) < 0.85:
                continue  # that's where its mouth opens
            base = Vector((math.cos(a) * r, y, 12.5 + math.sin(a) * r * 0.9))
            tip = base + Vector((math.cos(a) * 1.0, -0.5, math.sin(a) * 0.9 - 0.4)) * length
            point(m, "Body" if k else "Belly", tuple(base), tuple(tip), 1.7)
    for side in (-1, 1):
        look = (side * 0.3, 0.94, -0.14)
        egg(m, "Socket", (side * 1.6, 8.3, 13.0), 0.95, 0.5, 0.62, 10, 5)
        slit_eye(m, (side * 1.62, 8.6, 12.98), 0.37, look, side, iris="EyeGlow", lid_role="Accent", top=0.58, tilt=0.86, low=0.46)
        beam(m, "Accent", (side * 2.9, 7.8, 14.4), (side * 0.15, 9.3, 13.2), 1.3, 1.0, 0.7)
        crystal(m, "IceGlow", (side * 2.5, 6.0, 14.8), (side * 3.1, 5.1, 16.4), 0.9)
        egg(m, "Mouth", (side * 0.6, 9.86, 12.34), 0.26, 0.12, 0.18, 6, 3)  # a wide flat nose
    sweep(m, "Mouth", [((0, 4.6, zm + 0.04), 5.8, 0.2), ((0, 8.0, zm + 0.0), 4.4, 0.16), ((0, 9.0, zm + 0.1), 2.6, 0.12)], sides=8)
    egg(m, "Mouth", (0, 5.3, zm - 2.0), 3.2, 0.8, 2.6, 10, 6)  # the dark of its throat, behind the teeth
    egg(m, "IceGlow", (0, 5.9, zm - 2.2), 1.1, 0.4, 0.9, 8, 5)
    for side in (-1, 1):
        for k in range(8):
            t = k / 7
            y, x = 5.4 + 3.9 * t, side * (2.7 - 1.7 * t ** 3 - 0.2 * t)
            crystal(m, "Teeth", (x, y, zm + 0.12), (x, y + 0.05, zm - 1.1 - 0.6 * (k % 2) - (0.8 if k == 6 else 0)), 0.46)

    m.use("Jaw", (0, 4.6, zm - 0.04), "Head")
    z = zm - 0.5
    sweep(m, "Accent", [((0, 4.6, z), 5.2, 1.1), ((0, 7.4, z), 4.8, 1.0), ((0, 8.8, z + 0.05), 3.0, 0.8)], sides=8)
    sweep(m, "Mouth", [((0, 4.8, z + 0.5), 4.4, 0.1), ((0, 8.5, z + 0.44), 2.4, 0.1)], sides=8)
    sweep(m, "Tongue", [((0, 5.4, z + 0.6), 2.6, 0.26), ((0, 7.6, z + 0.56), 1.5, 0.2)], sides=6)
    for side in (-1, 1):
        for k in range(6):
            t = k / 5
            y, x = 5.6 + 2.8 * t, side * (2.15 - 1.0 * t ** 3 - 0.2 * t)
            point(m, "Teeth", (x, y, z + 0.4), (x, y + 0.03, z + 1.7 + 0.4 * (k % 2)), 0.56)
        # Two great tusks of ice, up from the jaw.
        sabre(m, "Tusk", [(side * 1.85, 8.3, z + 0.3), (side * 2.2, 8.9, z + 1.4), (side * 2.1, 8.8, z + 2.7), (side * 1.6, 8.3, z + 3.7)], 1.0, 7, power=1.2)
    for k in range(9):  # the fur under its chin
        x = (k - 4) * 0.72
        point(m, "Body", (x, 7.0 - abs(x) * 0.3, z - 0.3), (x * 1.1, 6.6 - abs(x) * 0.3, z - 1.9 + abs(x) * 0.15), 1.1)
    swing(m, ["Jaw"], (0, 4.6, zm - 0.04), -0.72)

    # Ice it knocks off the ground, hidden in its chest until the fists land.
    for n, size in enumerate((1.9, 1.6, 1.4, 1.9, 1.6, 1.4), start=1):
        chunk(m, "Shard", n, (0, 0.6, 10.0), size, parent="Root", role="Ice" if n % 2 else "IceGlow")
    m.bone = "Head"
    m.head_centre = (0, 8.6, 11.8)
    return m


ALL = [ramvalanche, abominator]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "frozen_peaks_7_8", SKY, FLOOR, GLOW_ROLES, glow=0.9, spacing=36)


if __name__ == "__main__":
    main()
