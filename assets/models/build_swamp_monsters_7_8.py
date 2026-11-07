"""Builds the Swamp's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_swamp_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_swamp_monsters_7_8.py    (stills only)
    ONLY=mossmaw QUICK=1 ...                                                (just that one)

Saves swamp_monsters_7_8.blend and renders to design/world/monsters_swamp_7_8/. The Swamp's first six are in
build_swamp_monsters.py; what this batch shares is in rare_kit.py.

The owner asked for 8 monsters a map (2026-11-06): two more each, nicer than the ones before, more aggressive map by map.
These two are the Swamp's new rarest and the fiercest of the first three maps: no more jokes in the face. Small yellow
slit eyes under hard brows, mouths hanging wide open, and they don't just stand there: they strike.

  Mossmaw     a giant snapping turtle, a whole bog on its back: a serrated shell with three rows of ridges, moss hanging off
              its rim, mushrooms and cattails growing on it, and a hooked saw-edged beak hanging open round a pink worm
              lure that never stops wriggling. Then the neck shoots out and the beak slams shut
  Titanoboa   a hooded giant snake reared up over its own coils, poison-marked, fangs out and tongue flicking. It rears back
              and lunges every 4 seconds, and a wave runs down its body as it slithers

What moves: the usual walk, idle and roar, and from rare_kit.py (SWAY in DinoLifeController): moss on Sway bones, the lure on
Wriggle1a to c, the tongue on Flick, the body on Slither1 to 8, the neck on Strike (with the Jaw biting along with it).

Skin roles Body, Accent, Belly and Claw take the colour mutations; moss, the worm and the face keep theirs. Glow is the
Swamp's own glowing role (already in shared/Roles.luau). Built at the first map's size. 1 Blender unit = 1 stud, models
face +Y, feet on Z = 0.
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
from rare_kit import cap, chain, curve, frames_along, leaf, poly, sabre, scallop, slit_eye, sweep, swing  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_swamp_7_8"
BLEND = "swamp_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = {"Glow"}

FACE = {"Pupil": "#0d0b08", "EyeWhite": "#fff8e8", "Highlight": "#fffbe0", "Mouth": "#4a1320", "Tongue": "#a83a55", "Teeth": "#f4ecd2",
        "Socket": "#0c0a08"}
SKY, FLOOR = "#b9d4a6", "#4e8466"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- Mossmaw


def on_shell(x, y, centre, radii):
    """The height of the shell's dome over x, y, or None off its edge."""
    u = ((x - centre[0]) / radii[0]) ** 2 + ((y - centre[1]) / radii[1]) ** 2
    return centre[2] + radii[2] * math.sqrt(1 - u) if u < 1 else None


def mossmaw():
    """A giant snapping turtle with a bog on its back, its hooked beak hanging open round a wriggling pink lure."""
    m = monster("dino_Mossmaw", Body="#4d5b33", Accent="#2d3a27", Belly="#c8b67e", Claw="#191510", Moss="#5c8e33", MossTip="#8ab446", Worm="#ff6f91", WormBand="#ffc2cf",
                EyeColour="#ffd21f", Stalk="#d8cfa6", Glow="#b8ff4a", Cattail="#6a3f24", Reed="#5f8f3a")
    rng = random.Random(77)
    m.joint("Spine", (0, -0.5, 3.8))

    # Legs: short, bowed and scaly, splayed out from under the shell, with long black claws.
    for x, y, end in ((3.6, 3.5, "Front"), (3.6, -4.6, "Back")):
        for side in (-1, 1):
            bone = end + ("L" if side < 0 else "R")
            px = side * x
            m.use(bone, (px, y, 3.2))
            sweep(m, "Body", [((px, y, 3.2), 2.4, 2.5), ((px + side * 1.15, y + 0.1, 2.15), 2.75, 2.9), ((px + side * 1.5, y + 0.2, 1.05), 2.55, 2.7), ((px + side * 1.6, y + 0.3, 0.42), 2.9, 3.1)], sides=10)
            sweep(m, "Accent", [((px + side * 1.6, y + 0.3, 0.5), 2.95, 3.15), ((px + side * 1.62, y + 0.34, 0.02), 3.05, 3.3)], sides=10)
            for k in range(4):  # scaly knobs down the leg
                point(m, "Accent", (px + side * (1.5 + 0.2 * k), y + 0.5 - 0.42 * k, 2.1 - 0.36 * k), (px + side * (2.3 + 0.2 * k), y + 0.2 - 0.42 * k, 2.35 - 0.36 * k), 0.6)
            for dx in (-1.0, -0.33, 0.33, 1.0):
                base = (px + side * 1.62 + dx, y + 1.6, 0.48)
                sabre(m, "Claw", [base, (base[0] + dx * 0.1, base[1] + 0.8, 0.48), (base[0] + dx * 0.18, base[1] + 1.3, 0.04)], 0.62, 5)
    m.bone = "Spine"

    # The shell: a low dark dome with a saw-toothed rim.
    centre, radii = (0, -0.8, 3.6), (6.1, 7.7, 4.1)
    first = len(m.parts.get("Accent", ([], []))[0])
    egg(m, "Accent", centre, *radii, 14, 8)
    shell = m.parts["Accent"][0]
    for i in range(first, len(shell)):  # the dome's underside, cut flat above the ground
        shell[i] = (shell[i][0], shell[i][1], max(shell[i][2], 2.0))
    sweep(m, "Belly", [((0, -7.2, 2.5), 7.0, 1.6), ((0, -3.0, 2.3), 11.2, 2.0), ((0, 2.0, 2.3), 11.0, 2.0), ((0, 6.0, 2.6), 7.0, 1.6)], sides=8)
    scallop(m, ("Accent",), (0, -0.8), (5.95, 7.55), 4.2, 2.35, 22, 0.12, thick=0.5)
    scallop(m, ("Body",), (0, -0.8), (6.0, 7.6), 3.5, 2.55, 22, 0.05, thick=0.4, offset=0.14)

    # Three rows of ridges down the shell, the middle one tallest.
    for row, x0, count, tall, wide in ((0, 0.0, 7, 1.9, 1.9), (-1, -3.3, 6, 1.35, 1.6), (1, 3.3, 6, 1.35, 1.6)):
        for k in range(count):
            y = 5.3 - k * (11.4 / (count - 1))
            x = x0 * (1 - abs(y + 0.8) / 11)
            z = on_shell(x, y, centre, radii)
            if z is None:
                continue
            ridge = tall * (0.75 + 0.35 * math.cos((y + 0.8) / 7))
            lean = Vector((x * 0.1, -0.45, 1)).normalized() * ridge
            base = Vector((x, y, z - 0.25))
            point(m, "Body", tuple(base), tuple(base + lean), wide)

    # Moss lying over it in soft patches.
    for k in range(20):
        a, b = rng.uniform(0, math.tau), rng.uniform(0.25, 1.2)
        direction = Vector((math.cos(a) * math.sin(b), math.sin(a) * math.sin(b), math.cos(b)))
        cap(m, "Moss" if k % 3 else "MossTip", centre, (radii[0] * 1.02, radii[1] * 1.02, radii[2] * 1.02), direction, rng.uniform(0.2, 0.36), rings=2, sides=8)

    # Moss hanging off the rim in long strands, each swaying a beat after the next.
    for n, a in enumerate((0.55, 1.2, 1.95, 2.6, 3.65, 4.3, 5.1, 5.8), start=1):
        x, y = math.cos(a) * 6.5, -0.8 + math.sin(a) * 8.05
        drop = 1.9 + 0.35 * (n % 3)
        pts = [(x, y, 3.3), (x * 1.05, y, 3.3 - drop * 0.4), (x * 1.08, y + 0.1, 3.3 - drop * 0.75), (x * 1.08, y, 3.3 - drop)]
        chain(m, "Sway", n, pts, 0.42, 0.2, role="Moss", flat="side", breadth=1.5)
        leaf(m, "MossTip", pts[-1], (pts[-1][0], pts[-1][1], pts[-1][2] - 0.6), (math.sin(a), -math.cos(a), 0), 0.62, 0.12)
    m.bone = "Spine"

    # A bog growing on its back: glowing toadstools and cattails.
    for x, y, r in ((-1.8, -3.6, 0.72), (-2.5, -2.65, 0.5), (2.4, 1.3, 0.62), (2.2, -5.0, 0.56)):
        z = on_shell(x, y, centre, radii)
        sweep(m, "Stalk", [((x, y, z - 0.2), r * 0.55, r * 0.55), ((x, y, z + r * 1.0), r * 0.42, r * 0.42)], sides=6)
        egg(m, "Glow", (x, y, z + r * 1.05), r * 1.1, r * 1.1, r * 0.62, 8, 4)
    for x, y, tall in ((-3.2, 0.9, 3.0), (-2.6, 1.55, 2.3), (3.4, -2.2, 2.6)):
        z = on_shell(x, y, centre, radii)
        sweep(m, "Reed", [((x, y, z - 0.2), 0.16, 0.16), ((x + 0.14, y, z + tall), 0.11, 0.11)], sides=6)
        egg(m, "Cattail", (x + 0.15, y, z + tall + 0.15), 0.24, 0.24, 0.58, 8, 4)
        leaf(m, "Reed", (x, y, z), (x + 0.75, y + 0.2, z + tall * 0.7), (0, 1, 0), 0.36, 0.06)
        leaf(m, "Reed", (x, y, z), (x - 0.6, y - 0.1, z + tall * 0.55), (0, 1, 0), 0.3, 0.06)

    # A thick tail with a saw down its back.
    path = [(p, w, w * 0.96) for p, w in zip(curve([(0, -7.8, 3.3), (0, -10.0, 2.7), (0, -12.2, 1.9), (0, -14.2, 1.2), (0, -15.8, 0.8)], 9),
                                             (3.3, 2.9, 2.5, 2.1, 1.75, 1.4, 1.1, 0.75, 0.3))]
    bones = rare_kit.jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], path, under="Belly", under_faces=3)
    for i, (p, w, _) in enumerate(path[:-1]):
        m.bone = bones[i]
        for dx, tall in ((0.0, 0.95), (-0.32, 0.5), (0.32, 0.5)):
            base = (p[0] + dx * w, p[1], p[2] + w * 0.42 - abs(dx) * w * 0.3)
            point(m, "Accent", base, (base[0] + dx * 0.4, base[1] - 0.4, base[2] + tall * (1 - i / 11)), 0.72 * (1 - i / 14))
    m.bone = "Spine"

    # The neck, heavy and folded. It sits on the Strike bone, so it shoots out of the shell.
    m.joint("Strike", (0, 5.2, 3.9), "Spine")
    m.joint("Neck", (0, 6.0, 4.0), "Strike")
    rings = [((0, 5.2, 3.9), 4.8, 4.4), ((0, 6.0, 4.05), 4.3, 3.95), ((0, 6.5, 4.2), 4.75, 4.3), ((0, 7.1, 4.3), 4.15, 3.75), ((0, 7.6, 4.4), 4.5, 4.05), ((0, 8.3, 4.55), 4.1, 3.65)]
    sweep(m, "Body", rings, ["Strike", "Strike", "Neck", "Neck", "Neck", "Neck"], sides=10, under="Belly", under_faces=3)
    m.bone = "Neck"
    for k in range(9):  # knobbly skin
        a = rng.uniform(0.15, math.pi - 0.15)
        y = rng.uniform(6.2, 8.1)
        base = Vector((math.cos(a) * 2.1, y, 4.35 + math.sin(a) * 1.95))
        point(m, "Accent", tuple(base), tuple(base + Vector((math.cos(a) * 0.5, -0.2, math.sin(a) * 0.5))), 0.5)

    # The head: a huge wedge ending in a hooked beak, its top bony and ridged.
    m.use("Head", (0, 8.2, 4.4), "Neck")
    zm = 3.95  # the mouth line at the back of the jaw
    skull = [((0, 8.0, 5.45), 4.6, 3.1), ((0, 9.4, 5.6), 5.4, 3.35), ((0, 10.9, 5.4), 4.9, 2.85), ((0, 12.1, 5.05), 3.75, 2.2), ((0, 12.95, 4.75), 2.55, 1.75)]
    sweep(m, "Body", skull, sides=10)
    sweep(m, "Accent", [((0, 12.7, 4.85), 2.95, 1.95), ((0, 13.5, 4.5), 2.1, 1.55), ((0, 14.0, 3.95), 1.3, 1.3), ((0, 14.1, 3.2), 0.5, 0.7), ((0, 13.95, 2.75), 0.12, 0.2)], sides=8)
    for k, (y, tall) in enumerate(((8.6, 1.0), (9.9, 1.2), (11.1, 0.95))):  # bony ridges down the middle of its head
        z = 6.95 - 0.28 * k * k * 0.5
        point(m, "Accent", (0, y, z - 0.25), (0, y - 0.5, z + tall), 1.05)
    for side in (-1, 1):
        for y, x, tall in ((8.4, 2.05, 0.9), (9.6, 2.45, 0.8)):  # knobs behind the eyes
            point(m, "Accent", (side * x, y, 6.5), (side * (x + 0.45), y - 0.5, 6.5 + tall), 0.8)
        egg(m, "Mouth", (side * 0.46, 13.6, 4.95), 0.15, 0.13, 0.1, 6, 3)  # nostrils
        look = (side * 0.62, 0.78, -0.02)
        egg(m, "Accent", (side * 1.95, 10.6, 5.72), 0.86, 0.95, 0.72, 10, 5)
        slit_eye(m, (side * 2.18, 10.92, 5.68), 0.58, look, side, lid_role="Accent", top=0.5, tilt=0.62, low=0.34)
        beam(m, "Accent", (side * 2.9, 9.75, 6.65), (side * 0.5, 11.95, 5.75), 0.82, 0.74, 0.5)
    # The roof of the mouth, a saw edge all round and a dark throat.
    sweep(m, "Mouth", [((0, 8.2, zm + 0.1), 4.6, 0.24), ((0, 12.2, zm + 0.0), 3.5, 0.2), ((0, 13.8, zm - 0.1), 1.3, 0.16)], sides=8)
    egg(m, "Mouth", (0, 8.5, zm - 1.05), 2.0, 0.7, 1.55, 8, 5)
    for side in (-1, 1):
        for k in range(7):
            t = k / 6
            y = 9.0 + 4.7 * t
            x = side * (2.3 - 1.65 * t * t)
            point(m, "Teeth", (x, y, zm + 0.08 - 0.15 * t), (x, y + 0.08, zm - 0.5 - 0.22 * (k % 2) - 0.15 * t), 0.56)

    # The lower jaw, built shut, then hung wide open round the lure.
    m.use("Jaw", (0, 8.3, zm), "Head")
    z = zm - 0.62
    sweep(m, "Accent", [((0, 8.3, z), 4.6, 1.2), ((0, 10.4, z - 0.02), 4.45, 1.1), ((0, 12.1, z + 0.02), 3.2, 0.95), ((0, 13.3, z + 0.14), 1.7, 0.72), ((0, 13.7, z + 0.42), 0.5, 0.42)], sides=8)
    sweep(m, "Belly", [((0, 8.3, z - 0.18), 3.6, 0.95), ((0, 12.0, z - 0.12), 2.3, 0.82)], sides=8)
    sweep(m, "Mouth", [((0, 8.4, z + 0.6), 3.8, 0.14), ((0, 12.2, z + 0.5), 2.5, 0.14), ((0, 13.2, z + 0.6), 1.1, 0.12)], sides=8)
    sweep(m, "Tongue", [((0, 8.7, z + 0.68), 2.3, 0.28), ((0, 11.1, z + 0.64), 1.7, 0.26), ((0, 11.9, z + 0.62), 0.9, 0.16)], sides=6)
    for side in (-1, 1):
        for k in range(6):
            t = k / 5
            y = 9.4 + 3.7 * t
            x = side * (2.0 - 1.35 * t * t)
            point(m, "Teeth", (x, y, z + 0.55), (x, y + 0.06, z + 1.05 + 0.2 * (k % 2)), 0.5)
    lure = [(0, 11.3, z + 0.74), (0.18, 11.6, z + 1.45), (-0.2, 11.9, z + 2.1), (0.2, 12.2, z + 2.7), (-0.1, 12.5, z + 3.2), (0.04, 12.72, z + 3.55)]
    names = chain(m, "Wriggle", 1, lure, 0.62, 0.42, parent="Jaw", role="Worm", sides=8)
    bone_for = [names[min(i * len(names) // len(lure), len(names) - 1)] for i in range(len(lure))]
    for p, bone in zip(lure[1:-1], bone_for[1:-1]):
        m.bone = bone
        sweep(m, "WormBand", [((p[0], p[1] - 0.04, p[2] - 0.06), 0.72, 0.72), ((p[0], p[1] + 0.04, p[2] + 0.06), 0.72, 0.72)], sides=8)
    swing(m, ["Jaw"] + names, (0, 8.3, zm), -0.58)
    m.bone = "Head"
    m.head_centre = (0, 14.5, 4.6)  # the tip of the beak, so the face renders stand clear of that huge head
    return m


# ---------------------------------------------------------------------- Titanoboa


def titanoboa():
    """A hooded giant snake reared up over its own coils, fangs out, tongue flicking, ready to strike."""
    m = monster("dino_Titanoboa", Body="#25392c", Accent="#c6d33f", Belly="#e6dca2", Claw="#14110d", Glow="#b8ff3a", EyeColour="#ffc81f", Hood="#16241c")

    # One long body from behind the head down to the tail tip. Its bones: Neck, Strike, Spine, then Slither1 to 8 to the tail.
    route = [(0, 6.3, 10.75), (0, 5.05, 10.45), (0, 3.9, 9.35), (0, 3.45, 7.75), (0, 3.85, 6.1), (0, 4.2, 4.5), (0, 3.65, 2.95), (0.1, 2.3, 1.85), (1.0, 0.5, 1.5),
             (3.4, -1.3, 1.45), (4.3, -4.2, 1.4), (1.4, -6.5, 1.3), (-3.1, -6.9, 1.2), (-5.0, -9.6, 1.05), (-3.1, -12.5, 0.92), (0.8, -13.0, 0.78), (3.4, -14.8, 0.6),
             (2.4, -17.0, 0.4), (0.5, -17.6, 0.22)]
    count = 56
    pts = curve(route, count)
    knots = [i * (count - 1) / (len(route) - 1) for i in range(len(route))]

    def width(i):
        """Thick behind the neck and through the coils, thin at the neck, running to a point."""
        u = i / (count - 1)
        table = [(0, 2.15), (0.08, 1.95), (0.22, 2.3), (0.36, 2.9), (0.55, 3.0), (0.75, 2.3), (0.9, 1.25), (1.0, 0.2)]
        for (a, wa), (b, wb) in zip(table, table[1:]):
            if u <= b:
                return wa + (wb - wa) * (u - a) / (b - a)
        return 0.2

    pts = [(p[0], p[1], max(p[2], width(i) * 0.47 + 0.02)) for i, p in enumerate(pts)]  # lying on the ground, not sunk into it
    neck_end, strike_end, spine_end = knots[3], knots[6], knots[8]
    tail_start = spine_end
    bones = []
    for i in range(count):
        if i <= neck_end:
            bones.append("Neck")
        elif i <= strike_end:
            bones.append("Strike")
        elif i <= spine_end:
            bones.append("Spine")
        else:
            n = 1 + min(7, int((i - tail_start) / (count - tail_start) * 8))
            bones.append(f"Slither{n}")
    m.joint("Spine", pts[int(spine_end)], "Root")
    m.joint("Strike", pts[int(strike_end)], "Spine")
    m.joint("Neck", pts[int(neck_end)], "Strike")
    for n in range(1, 9):
        first = bones.index(f"Slither{n}")
        m.joint(f"Slither{n}", pts[first - 1], "Spine" if n == 1 else f"Slither{n - 1}")
    path = [(p, width(i), width(i)) for i, p in enumerate(pts)]
    sweep(m, "Body", path, bones, sides=8, under="Belly", under_faces=3, up=(0, -1, 0))

    # Diamonds down its back, pale edged in poison yellow, and a low ridge of spines.
    frames = frames_along(pts, (0, -1, 0))
    for i in range(3, count - 3, 2):
        p, (ahead, side, normal) = Vector(pts[i]), frames[i]
        w = width(i)
        c = p + normal * w * 0.47
        m.bone = bones[i]
        big, small = w * 0.5, w * 0.34
        poly(m, "Accent", [c + ahead * big, c + side * small, c - ahead * big, c - side * small], -normal * 0.14)
        inner = c + normal * 0.02
        poly(m, "Hood", [inner + ahead * big * 0.5, inner + side * small * 0.5, inner - ahead * big * 0.5, inner - side * small * 0.5], -normal * 0.1)
        if i % 4 == 1 and i < count - 12:
            for s in (-1, 1):
                d = c - normal * w * 0.24 + side * s * w * 0.44
                poly(m, "Accent", [d + ahead * small * 0.5 + normal * 0.1, d + normal * small * 0.26, d - ahead * small * 0.5, d - normal * small * 0.26], -side * s * 0.1)

    # The hood, flared either side of the neck, dark ribs and a glowing eye-spot on each side to scare things off.
    m.bone = "Neck"
    for side in (-1, 1):
        outline = [(side * 0.72, 4.75, 10.55), (side * 2.15, 4.35, 10.55), (side * 3.5, 3.85, 9.8), (side * 3.95, 3.5, 8.55), (side * 3.2, 3.35, 7.3), (side * 0.85, 3.5, 6.75)]
        poly(m, "Hood", outline, (0, -0.2, 0))
        hem = [(side * 0.9, 4.85, 10.75), (side * 2.25, 4.42, 10.8), (side * 3.75, 3.85, 9.95), (side * 4.25, 3.5, 8.55), (side * 3.4, 3.3, 7.1), (side * 0.9, 3.42, 6.5)]
        for a, b in zip(hem, hem[1:]):
            beam(m, "Accent", a, b, 0.3, 0.3, 0.26)
        for tip, z in (((side * 3.2, 3.95, 10.15), 9.7), ((side * 3.8, 3.55, 8.6), 8.8), ((side * 3.05, 3.42, 7.3), 7.9)):
            beam(m, "Body", (side * 0.8, 4.0, z), tip, 0.24, 0.24, 0.12)
            point(m, "Claw", tip, (tip[0] + side * 0.75, tip[1] - 0.1, tip[2] + (tip[2] - 8.6) * 0.3), 0.3)
        spot = (side * 2.25, 4.1, 8.85)
        egg(m, "Accent", spot, 0.72, 0.12, 0.92, 10, 4)
        egg(m, "Glow", (spot[0], spot[1] + 0.07, spot[2]), 0.42, 0.1, 0.62, 10, 4)
        egg(m, "Socket", (spot[0], spot[1] + 0.13, spot[2]), 0.12, 0.08, 0.5, 8, 3)

    # The head: a wide viper's wedge, carried level, its jaw hanging open.
    m.use("Head", (0, 6.0, 10.5), "Neck")
    zm = 10.15
    skull = [((0, 5.5, zm + 0.95), 2.2, 1.95), ((0, 6.55, zm + 1.05), 3.9, 2.15), ((0, 7.75, zm + 0.98), 3.65, 1.95), ((0, 8.95, zm + 0.76), 2.75, 1.45), ((0, 9.95, zm + 0.52), 1.85, 1.0), ((0, 10.45, zm + 0.38), 1.15, 0.68)]
    sweep(m, "Body", skull, sides=8)
    poly(m, "Accent", [(0, 9.3, zm + 1.5), (0.95, 7.35, zm + 2.0), (0.4, 6.1, zm + 2.0), (-0.4, 6.1, zm + 2.0), (-0.95, 7.35, zm + 2.0)], (0, 0, -0.16))  # the arrow on its head
    for side in (-1, 1):
        look = (side * 0.6, 0.8, -0.04)
        egg(m, "Hood", (side * 1.3, 8.0, zm + 1.26), 0.62, 0.66, 0.46, 10, 5)
        slit_eye(m, (side * 1.48, 8.26, zm + 1.26), 0.46, look, side, lid_role="Body", top=0.48, tilt=0.66, low=0.32, slit=0.18)
        beam(m, "Body", (side * 2.1, 7.1, zm + 2.1), (side * 0.32, 8.95, zm + 1.32), 0.56, 0.5, 0.3)
        sabre(m, "Claw", [(side * 1.85, 7.25, zm + 1.92), (side * 2.1, 6.7, zm + 2.5), (side * 2.15, 5.9, zm + 2.85)], 0.5, 5)
        egg(m, "Mouth", (side * 0.38, 10.25, zm + 0.62), 0.13, 0.11, 0.08, 6, 3)
        cap(m, "Mouth", (0, 7.7, zm + 0.98), (1.87, 2.6, 1.0), (side * 0.75, 0.75, -0.2), 0.12, rings=2, sides=6)  # a heat pit
    sweep(m, "Mouth", [((0, 5.9, zm + 0.04), 3.3, 0.14), ((0, 8.9, zm + 0.04), 2.5, 0.12), ((0, 10.3, zm + 0.1), 1.05, 0.1)], sides=8)
    egg(m, "Mouth", (0, 6.2, zm - 0.72), 1.45, 0.5, 1.05, 8, 5)
    for side in (-1, 1):
        sabre(m, "Teeth", [(side * 0.72, 9.55, zm + 0.06), (side * 0.78, 9.72, zm - 0.7), (side * 0.72, 9.42, zm - 1.5), (side * 0.62, 8.92, zm - 2.0)], 0.56, 7, power=1.2)
        egg(m, "Tongue", (side * 0.72, 9.55, zm + 0.02), 0.42, 0.42, 0.14, 8, 3)
        egg(m, "Glow", (side * 0.62, 8.86, zm - 2.14), 0.09, 0.09, 0.16, 6, 3)  # a bead of venom on the fang's tip
        for k in range(7):  # needle teeth along the edge
            y = 6.3 + k * 0.46
            x = side * (1.6 - 0.09 * k - 0.012 * k * k)
            point(m, "Teeth", (x, y, zm + 0.04), (x, y + 0.03, zm - 0.3 - 0.1 * (k % 2)), 0.2)

    # The jaw, hung wide open, with two lower fangs and a long forked tongue on the Flick bone.
    m.use("Jaw", (0, 6.0, zm - 0.02), "Head")
    z = zm - 0.42
    sweep(m, "Belly", [((0, 6.0, z), 3.25, 0.82), ((0, 7.7, z), 3.0, 0.74), ((0, 9.0, z + 0.03), 2.1, 0.56), ((0, 9.95, z + 0.1), 1.3, 0.38)], sides=8)
    sweep(m, "Body", [((0, 6.0, z - 0.14), 3.4, 0.68), ((0, 7.7, z - 0.14), 3.15, 0.6), ((0, 9.0, z - 0.1), 2.2, 0.4)], sides=8)
    sweep(m, "Mouth", [((0, 6.1, z + 0.36), 2.7, 0.08), ((0, 9.8, z + 0.28), 1.1, 0.08)], sides=8)
    for side in (-1, 1):
        sabre(m, "Teeth", [(side * 0.62, 9.3, z + 0.28), (side * 0.66, 9.32, z + 0.72), (side * 0.6, 9.12, z + 1.08)], 0.32, 5, power=1.2)
        for k in range(6):
            y = 6.5 + k * 0.42
            x = side * (1.32 - 0.1 * k)
            point(m, "Teeth", (x, y, z + 0.3), (x, y + 0.02, z + 0.6), 0.16)
    m.use("Flick", (0, 7.4, z + 0.44), "Jaw")
    sweep(m, "Tongue", [((0, 7.2, z + 0.44), 0.36, 0.14), ((0, 9.1, z + 0.46), 0.3, 0.12), ((0, 10.3, z + 0.5), 0.24, 0.1)], sides=6)
    for side in (-1, 1):
        sabre(m, "Tongue", [(0, 10.25, z + 0.5), (side * 0.2, 10.75, z + 0.54), (side * 0.48, 11.25, z + 0.72)], 0.17, 4, power=1.0)
    swing(m, ["Jaw", "Flick"], (0, 6.0, zm - 0.02), -0.62)
    m.bone = "Head"
    m.head_centre = (0, 8.0, 10.7)
    return m


ALL = [mossmaw, titanoboa]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "swamp_7_8", SKY, FLOOR, GLOW_ROLES, glow=0.6, spacing=34)


if __name__ == "__main__":
    main()
