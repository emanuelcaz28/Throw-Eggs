"""Builds the Forest's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_forest_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_forest_monsters_7_8.py    (stills only)
    ONLY=therizinosaurus QUICK=1 ...                                          (just that one)

Saves forest_monsters_7_8.blend and renders to design/world/monsters_forest_7_8/. The Forest's first six are in
build_forest.py; what this batch shares is in rare_kit.py.

The owner asked for 8 monsters a map (2026-11-06): two more each, nicer than the ones before, more aggressive map by map.
These two are the Forest's new rarest. Map 1 is the cute map (GAME_SPEC 8a: friendly faces, real dinosaur names), so
they're the least aggressive of all the new ones: gentle giants, the Forest's prize catches, with big round eyes.

  Therizinosaurus   a big soft violet fluffball in tiers of feathers, a small kind face with a soft muzzle, and enormous
                    golden scythe claws, which it uses to hold one small daisy very carefully
  Amargasaurus      the Forest's gentle giant: a long-necked royal blue sauropod with a double sail of sunset-coloured
                    spines down its neck. Each pair of spines sways a beat after the one before, so the sail ripples

What moves: the usual walk, idle and roar, and the swaying (rare_kit.py, SWAY in DinoLifeController): the crest feathers on
Sway1a to Sway5a, Amargasaurus's six sail segments on Sway1a to Sway6a. Nothing here lunges or snaps: that's for later maps.

Skin roles Body, Accent, Belly and Claw take the colour mutations; the beak, crest, sail, daisy and the face keep theirs.
Built at the first map's size. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0.
"""
import math
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402  (first: it turns the stud preview off)
from build_desert import beam  # noqa: E402
from build_forest import Model  # noqa: E402
from build_spore_hollow_monsters import egg  # noqa: E402
from build_starfall_crater import ball  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from rare_kit import cap, chain, curve, jointed, leaf, panel, round_eye, sabre, scallop, sweep  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_forest_7_8"
BLEND = "forest_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = set()

FACE = {"Pupil": "#1d1828", "EyeWhite": "#ffffff", "Highlight": "#ffffff", "Mouth": "#5c2434", "Tongue": "#f27b96",
        "Teeth": "#fffaf0", "Lash": "#2b2433", "Blush": "#ff9ab6"}
SKY, FLOOR = "#8fd0ff", "#6ccf4a"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


def daisy(m, centre, facing, r):
    """A little daisy: white petals round a yellow heart, facing along facing."""
    c, f = Vector(centre), Vector(facing).normalized()
    side = f.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(f)
    for k in range(9):
        a = k * math.tau / 9
        d = side * math.cos(a) + up * math.sin(a)
        leaf(m, "Daisy", tuple(c + d * r * 0.2), tuple(c + d * r * 1.2 - f * r * 0.12), tuple(side * -math.sin(a) + up * math.cos(a)), r * 0.62, 0.06)
    egg(m, "DaisyHeart", tuple(c + f * r * 0.1), r * 0.4, r * 0.4, r * 0.4, 8, 4)


def smile(m, x, y, z, reach, lift):
    """A curl of a smile running back from the corner of the mouth, along a cheek."""
    side = 1 if x > 0 else -1
    beam(m, "Mouth", (x, y, z), (x + side * 0.05, y - reach, z + lift), 0.09, 0.09, 0.05)


# ---------------------------------------------------------------------- Therizinosaurus


def therizinosaurus():
    """A big soft fluffball with enormous golden scythe claws, holding one small daisy very carefully."""
    m = monster("dino_Therizino", Body="#a48cf0", Accent="#6a4fd0", Belly="#fff0d4", Claw="#ffcf4d", Beak="#ff8f6b", Crest="#e0459b",
                CrestTip="#37c6b4", EyeColour="#3fb8a8", Stem="#3f9a3a", Daisy="#ffffff", DaisyHeart="#ffc933")
    m.joint("Spine", (0, -0.3, 4.6))

    # Legs: fluffy thighs, then stout scaly shins and big soft feet. No thin yellow shanks, or it's a goose.
    for side, letter in ((-1, "L"), (1, "R")):
        x = side * 1.3
        m.use(f"Leg{letter}", (x, -0.25, 4.4))
        sweep(m, "Body", [((x, -0.25, 4.9), 2.2, 2.3), ((x, -0.15, 3.6), 2.35, 2.5), ((x, -0.05, 2.5), 1.45, 1.55)], sides=8)
        scallop(m, ("Accent",), (x, -0.1), (1.0, 1.05), 3.05, 1.95, 8, 0.1, offset=0.2)
        m.use(f"Shin{letter}", (x, 0.0, 2.6), f"Leg{letter}")
        sweep(m, "Accent", [((x, 0.0, 2.7), 1.05, 1.1), ((x, 0.1, 0.55), 1.0, 1.05)], sides=8)
        sweep(m, "Accent", [((x, -0.55, 0.3), 1.2, 0.6), ((x, 0.25, 0.32), 1.5, 0.66), ((x, 1.05, 0.26), 1.45, 0.5)], sides=8)
        for dx, reach in ((-0.5, 1.1), (0.0, 1.32), (0.5, 1.1)):
            sabre(m, "Claw", [(x + dx, reach, 0.3), (x + dx * 1.08, reach + 0.42, 0.3), (x + dx * 1.12, reach + 0.72, 0.06)], 0.34, 4)
    m.bone = "Spine"

    # The body: a big round pear, in tiers of soft feathers with a cream bib down the front.
    sweep(m, "Body", [((0, -0.65, 2.9), 2.5, 2.3), ((0, -0.45, 3.9), 4.2, 3.9), ((0, -0.1, 5.1), 4.5, 4.15), ((0, 0.35, 6.2), 3.7, 3.45),
                      ((0, 0.75, 7.15), 2.5, 2.4)], sides=10)
    scallop(m, ("Accent",), (0, -0.42), (2.3, 2.12), 4.3, 2.65, 12, 0.08, offset=0.1, front="Belly", front_half=0.62)
    scallop(m, ("Body",), (0, -0.1), (2.46, 2.26), 5.45, 3.75, 12, 0.12, offset=0.36, front="Belly", front_half=0.66)
    scallop(m, ("Accent",), (0, 0.3), (2.04, 1.9), 6.6, 4.9, 11, 0.24, offset=0.1, front="Belly", front_half=0.72)
    scallop(m, ("Belly",), (0, 0.72), (1.46, 1.36), 7.5, 6.05, 10, 0.4, offset=0.28)

    # Arms: held up in front, feathered sleeves, hands of three huge golden scythes, curved to be gentle.
    for side, letter in ((-1, "L"), (1, "R")):
        sh, el, wr = Vector((side * 2.05, 0.8, 6.55)), Vector((side * 3.1, 1.35, 5.35)), Vector((side * 2.35, 3.0, 5.65))
        m.use(f"Arm{letter}", tuple(sh))
        sweep(m, "Body", [(tuple(sh), 1.2, 1.2), (tuple(el), 1.0, 1.0), (tuple(wr), 0.86, 0.86)], sides=8)
        for k in range(5):  # a little cape of feathers over the shoulder
            a = math.radians(-70 + k * 35)
            base = sh + Vector((side * 0.42 * math.cos(a), 0.62 * math.sin(a), 0.55))
            leaf(m, "Accent", tuple(base), tuple(base + Vector((side * 0.6, 0.52 * math.sin(a), -1.45))), (math.sin(a) * side, math.cos(a), 0), 1.05, 0.14)
        for a, b in ((sh, el), (el, wr)):
            for k in range(4):
                base = a.lerp(b, (k + 0.3) / 4) + Vector((0, 0, -0.22))
                leaf(m, "Body", tuple(base), tuple(base + Vector((side * 0.2, -0.22, -1.2))), tuple((b - a).normalized()), 1.0, 0.12)
        egg(m, "Body", tuple(wr + Vector((0, 0.32, 0))), 0.82, 0.78, 0.74, 8, 5)
        for k, dx in enumerate((-0.42, 0.0, 0.42)):
            x = wr.x + dx
            reach = 1.0 if k == 1 else 0.88
            y0, z0 = wr.y + 0.75, wr.z + 0.1
            sabre(m, "Claw", [(x, y0, z0), (x, y0 + 1.15 * reach, z0 + 0.25), (x - side * 0.1, y0 + 2.05 * reach, z0 - 0.3),
                              (x - side * 0.22, y0 + 2.35 * reach, z0 - 1.35), (x - side * 0.3, y0 + 2.0 * reach, z0 - 2.3)], 0.62, 8, flat=0.72)
        if side > 0:  # the daisy, its stem pinched between two claws, up in front of its face
            stem = [(wr.x - 0.2, wr.y + 2.2, wr.z + 0.1), (wr.x - 0.45, wr.y + 2.1, wr.z + 1.0), (wr.x - 0.9, wr.y + 1.9, wr.z + 1.95)]
            sabre(m, "Stem", stem, 0.2, 5, power=4)
            leaf(m, "Stem", (wr.x - 0.42, wr.y + 2.1, wr.z + 0.9), (wr.x + 0.3, wr.y + 2.25, wr.z + 1.3), (0, 1, 0.2), 0.34, 0.05)
            daisy(m, (wr.x - 0.92, wr.y + 1.85, wr.z + 2.1), (-0.3, -0.75, 0.6), 0.62)
    m.bone = "Spine"

    # A short fluffy tail ending in a fan.
    path = [(p, w, w * 0.95) for p, w in zip(curve([(0, -1.5, 3.9), (0, -2.6, 3.65), (0, -3.5, 3.75), (0, -4.2, 4.1)], 6), (2.1, 1.75, 1.4, 1.1, 0.85, 0.62))]
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], path)
    m.bone = "Tail3"
    base = Vector((0, -4.1, 4.15))
    for k in range(7):
        a = math.radians(-66 + k * 22)
        tip = base + Vector((math.sin(a) * 1.75, -math.cos(a) * 2.0, 0.75 + 0.5 * math.cos(a)))
        leaf(m, ("Crest", "Accent", "Body", "Accent")[abs(k - 3)], tuple(base), tuple(tip), (math.cos(a), math.sin(a), 0), 1.0, 0.14)
    m.bone = "Spine"

    # The neck: short and thick, buried in the ruff.
    m.joint("Neck", (0, 0.75, 7.1), "Spine")
    sweep(m, "Body", [((0, 0.6, 6.9), 2.65, 2.55), ((0, 1.0, 7.6), 2.2, 2.15), ((0, 1.55, 8.3), 1.95, 1.9), ((0, 2.0, 8.85), 1.8, 1.8)],
          ["Spine", "Neck", "Neck", "Neck"], sides=8)
    m.bone = "Neck"
    scallop(m, ("Belly",), (0, 1.32), (1.04, 1.0), 8.4, 7.3, 9, 0.34, offset=0.15)

    # The head: round and soft, a cream mask, big kind eyes, feathers swept back over the neck. An upright crest is a rooster's.
    yc, zc = 2.4, 9.2
    head = (1.42, 1.32, 1.2)
    m.use("Head", (0, yc - 0.5, zc - 0.95), "Neck")
    egg(m, "Body", (0, yc, zc), *head, 12, 7)
    cap(m, "Belly", (0, yc, zc), (head[0] * 1.012, head[1] * 1.012, head[2] * 1.012), (0, 1, -0.42), 1.02, squash=(1.0, 0.86), rings=4, sides=12)
    look = (0.22, 1.0, -0.02)
    for side in (-1, 1):
        round_eye(m, (side * 0.7, yc + 0.8, zc + 0.3), 0.54, (look[0] + side * 0.3, 1.0, look[2]), side, top=0.3, tilt=-0.3, low=0.12)
        cap(m, "Blush", (0, yc, zc), (head[0] * 1.03, head[1] * 1.03, head[2] * 1.03), (side * 0.72, 0.6, -0.34), 0.25, squash=(1.0, 0.62), rings=2)
    # A soft dinosaur muzzle, tipped with a little beak, and two small front teeth. Not a bill: bills made it a bird.
    z = zc - 0.46
    muzzle = (0.92, 0.9, 0.46)
    centre = (0, yc + 1.05, z + 0.26)
    egg(m, "Belly", centre, *muzzle, 10, 5)
    cap(m, "Beak", centre, (muzzle[0] * 1.02, muzzle[1] * 1.02, muzzle[2] * 1.02), (0, 1, 0.3), 0.42, squash=(1.0, 0.8), rings=3)
    for side in (-1, 1):
        egg(m, "Mouth", (side * 0.17, yc + 1.86, z + 0.48), 0.07, 0.07, 0.05, 6, 3)
        m.block("Teeth", side * 0.14, yc + 1.8, z - 0.08, 0.2, 0.08, 0.24)
    egg(m, "Mouth", (0, yc + 1.02, z + 0.0), 0.84, 0.84, 0.16, 10, 4)
    m.use("Jaw", (0, yc + 0.5, z - 0.05), "Head")
    egg(m, "Belly", (0, yc + 1.0, z - 0.18), 0.8, 0.8, 0.3, 10, 5)
    egg(m, "Tongue", (0, yc + 1.08, z - 0.0), 0.4, 0.46, 0.06, 8, 3)
    m.bone = "Head"
    for side in (-1, 1):
        smile(m, side * 0.8, yc + 1.0, z - 0.0, 0.3, 0.2)
    top = zc + head[2]
    for n, (dx, y0, lean, length) in enumerate(((0.0, 0.75, 1.02, 2.1), (-0.42, 0.4, 1.2, 2.3), (0.42, 0.4, 1.2, 2.3), (-0.62, -0.1, 1.42, 2.0),
                                                (0.62, -0.1, 1.42, 2.0)), start=1):
        base = Vector((dx, yc + y0, top - 0.16 - 0.22 * abs(dx)))
        reach = Vector((dx * 0.6, -length * math.sin(lean), length * math.cos(lean)))
        m.joint(f"Sway{n}a", tuple(base), "Head")
        m.bone = f"Sway{n}a"
        across = Vector((0.75 if dx else 0.0, reach.z * 0.2, -reach.y * 0.2)).normalized() if dx else Vector((0, reach.z, -reach.y)).normalized()
        leaf(m, "Crest" if n in (1, 4, 5) else "CrestTip", tuple(base), tuple(base + reach), tuple(across), 0.72, 0.18)
    m.bone = "Head"
    m.head_centre = (0, yc + 0.7, zc)
    return m


# ---------------------------------------------------------------------- Amargasaurus


def amargasaurus():
    """The Forest's gentle giant: a long-necked sauropod, heavy and sweet, with a double sail of sunset spines down its neck."""
    m = monster("dino_Amarga", Body="#3f62d8", Accent="#8fb0ff", Belly="#ffeccb", Claw="#2e2a50", Quill="#fff3dc", Sail="#ff8a3d", SailTip="#ff4f7a",
                EyeColour="#2f9aa0")
    m.joint("Spine", (0, 0, 5.3))

    # Legs: four short, thick pillars, wider at the foot, with pads and toenails. It's heavy, not on stilts.
    for x, y, end in ((1.72, 2.55, "Front"), (1.8, -2.75, "Back")):
        for side in (-1, 1):
            bone = end + ("L" if side < 0 else "R")
            px = side * x
            m.use(bone, (px, y, 4.6))
            sweep(m, "Body", [((px, y, 5.6), 2.2, 2.5), ((px, y + 0.02, 3.3), 2.15, 2.25), ((px, y + 0.06, 1.3), 2.1, 2.2), ((px, y + 0.1, 0.5), 2.55, 2.65)], sides=8)
            sweep(m, "Belly", [((px, y + 0.1, 0.62), 2.5, 2.6), ((px, y + 0.12, 0.02), 2.75, 2.85)], sides=8)
            for dx, dy in ((-0.72, 1.12), (0.0, 1.38), (0.72, 1.12)):
                egg(m, "Claw", (px + dx, y + dy, 0.32), 0.34, 0.26, 0.32, 8, 4)
    m.bone = "Spine"

    # The body: a big soft barrel, cream underneath, a pale saddle of spots along its back.
    body = [((0, -4.9, 5.9), 2.6, 2.9), ((0, -3.3, 6.25), 4.9, 4.9), ((0, -0.5, 6.5), 5.9, 5.8), ((0, 2.0, 6.4), 5.5, 5.4), ((0, 3.7, 6.3), 4.0, 4.0)]
    sweep(m, "Body", body, under="Belly", under_faces=3, sides=10)
    barrel = (2.95, 5.2, 2.92)
    for k, (y, a, size) in enumerate(((-3.1, 0.35, 0.2), (-1.9, -0.35, 0.26), (-0.8, 0.42, 0.3), (0.2, -0.3, 0.27), (1.4, 0.38, 0.24), (2.4, -0.3, 0.2),
                                      (-2.5, 0.0, 0.15), (-0.2, 0.05, 0.17), (1.8, 0.02, 0.14), (-1.2, 0.86, 0.2), (0.9, 0.9, 0.2), (-1.4, -0.86, 0.2), (0.7, -0.9, 0.2))):
        direction = Vector((math.sin(a), y / 5.2, math.cos(a))).normalized()
        cap(m, "Accent", (0, -0.4, 6.42), (barrel[0], barrel[1], barrel[2]), direction, size, squash=(1.0, 0.82), rings=2, sides=8)

    # A long whip of a tail, the sail's spines running down it.
    tail_pts = curve([(0, -4.4, 6.1), (0, -6.3, 5.9), (0, -8.2, 5.15), (0, -10.0, 4.2), (0, -11.8, 3.5)], 10)
    widths = [2.9, 2.45, 2.0, 1.62, 1.3, 1.0, 0.76, 0.54, 0.36, 0.18]
    bones = jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w * 1.05) for p, w in zip(tail_pts, widths)], under="Belly", under_faces=3)
    for i, (p, w) in enumerate(zip(tail_pts, widths)):
        if 0 < i < 8:
            m.bone = bones[i]
            h = 0.72 - 0.06 * i
            point(m, "SailTip" if i % 2 else "Sail", (p[0], p[1], p[2] + w * 0.46), (p[0], p[1] - 0.35, p[2] + w * 0.5 + h), 0.42)
    m.bone = "Spine"
    for k, y in enumerate((-3.5, -2.5, -1.5, -0.5, 0.5)):  # the same spines along its back, growing towards the neck
        z = 6.42 + 2.82 * math.sqrt(max(0.05, 1 - ((y + 0.4) / 5.2) ** 2))
        point(m, "Sail" if k % 2 else "SailTip", (0, y, z - 0.1), (0, y - 0.35, z + 0.8 + 0.1 * k), 0.5)

    # The neck, rising in a long curve, the sail along its top.
    neck = curve([(0, 2.9, 7.2), (0, 4.1, 8.25), (0, 4.95, 9.6), (0, 5.6, 10.9), (0, 6.3, 11.75)], 9)
    widths = [3.4, 2.85, 2.4, 2.1, 1.85, 1.7, 1.58, 1.5, 1.45]
    m.joint("Neck", (0, 3.0, 7.0), "Spine")
    sweep(m, "Body", [(p, w, w * 1.05) for p, w in zip(neck, widths)], ["Spine"] + ["Neck"] * 8, under="Belly", under_faces=3, sides=8)
    frames = rare_kit.frames_along(neck)
    heights = [1.55, 2.2, 2.75, 2.9, 2.55, 1.9]
    spots = []
    for n, (i, h) in enumerate(zip(range(1, 7), heights), start=1):
        p, (ahead, side, normal) = Vector(neck[i]), frames[i]
        top = p + normal * widths[i] * 1.05 / 2 * 0.86
        up = (normal * 0.75 - ahead * 0.2 + Vector((0, 0, 0.35))).normalized()
        spots.append((n, top, up, h, side))
    for idx, (n, top, up, h, side) in enumerate(spots):
        bone = f"Sway{n}a"
        m.joint(bone, tuple(top), "Neck")
        m.bone = bone
        nxt = spots[idx + 1] if idx + 1 < len(spots) else None
        for s in (-1, 1):
            base = top + side * s * 0.34
            tip = base + up * h + side * s * h * 0.2
            point(m, "Quill", tuple(base), tuple(tip + up * 0.15), 0.24)
            if nxt:
                nbase = nxt[1] + nxt[4] * s * 0.32
                ntip = nbase + nxt[2] * nxt[3] + nxt[4] * s * nxt[3] * 0.2
                inset = side * s * -0.03
                mid_a, mid_b = base.lerp(tip, 0.6), nbase.lerp(ntip, 0.6)
                panel(m, "Sail", [tuple(base + up * 0.1 + inset), tuple(nbase + nxt[2] * 0.1 + inset), tuple(mid_b + inset), tuple(mid_a + inset)], 0.07)
                panel(m, "SailTip", [tuple(mid_a + inset), tuple(mid_b + inset), tuple(nbase.lerp(ntip, 0.9) + inset), tuple(base.lerp(tip, 0.9) + inset)], 0.07)
    m.bone = "Neck"

    # The head: small and sweet on all that neck. A round skull, big lashed eyes, a soft muzzle and a happy smile.
    yc, zc = 7.15, 12.1
    head = (1.28, 1.3, 1.12)
    m.use("Head", (0, yc - 0.6, zc - 0.8), "Neck")
    egg(m, "Body", (0, yc, zc), *head, 12, 7)
    z = zc - 0.42
    egg(m, "Body", (0, yc + 1.2, z + 0.3), 1.08, 1.02, 0.56, 10, 5)
    for side in (-1, 1):
        egg(m, "Mouth", (side * 0.34, yc + 1.82, z + 0.68), 0.14, 0.12, 0.07, 6, 3)
    egg(m, "Mouth", (0, yc + 1.16, z - 0.03), 0.98, 0.96, 0.2, 10, 4)
    m.use("Jaw", (0, yc + 0.45, z - 0.05), "Head")
    egg(m, "Belly", (0, yc + 1.12, z - 0.22), 0.96, 0.92, 0.34, 10, 5)
    egg(m, "Tongue", (0, yc + 1.2, z - 0.03), 0.52, 0.56, 0.07, 8, 3)
    m.bone = "Head"
    for side in (-1, 1):
        round_eye(m, (side * 0.82, yc + 0.62, zc + 0.36), 0.62, (side * 0.46, 1.0, 0.04), side, top=0.1, tilt=-0.2)
        cap(m, "Blush", (0, yc, zc), (head[0] * 1.02, head[1] * 1.02, head[2] * 1.02), (side * 0.95, 0.2, -0.22), 0.27, squash=(1.0, 0.62), rings=2)
        smile(m, side * 0.94, yc + 1.05, z - 0.03, 0.34, 0.24)
        for k in range(3):  # lashes flicking up off the outer corner
            a = 0.12 + 0.34 * k
            base = Vector((side * (0.82 + 0.5 * math.cos(a + 0.5)), yc + 0.76 - 0.14 * k, zc + 0.36 + 0.5 * math.sin(a + 0.5)))
            beam(m, "Lash", tuple(base), tuple(base + Vector((side * 0.3, -0.06, 0.25 - 0.06 * k))), 0.09, 0.08, 0.04)
    m.head_centre = (0, yc + 0.6, zc)
    return m


ALL = [therizinosaurus, amargasaurus]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "forest_7_8", SKY, FLOOR, GLOW_ROLES, spacing=26)


if __name__ == "__main__":
    main()
