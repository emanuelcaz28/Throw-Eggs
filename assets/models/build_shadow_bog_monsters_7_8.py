"""Builds Shadow Bog's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_shadow_bog_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_shadow_bog_monsters_7_8.py    (stills only)
    ONLY=skeeterror QUICK=1 ...                                                  (just that one)

Saves shadow_bog_monsters_7_8.blend and renders to design/world/monsters_shadow_bog_7_8/. The first six are in
build_shadow_bog_monsters.py; what this batch shares is in rare_kit.py.

The owner asked for 8 monsters a map (2026-11-06): two more each, nicer than the ones before, more aggressive map by map, and
Shadow Bog's should "look weird in a good way": they don't need to make sense. So the most hostile of the first six maps, and the
strangest. The bog face (build_shadow_bog_monsters.py): burning magenta eyes, never just two, a violet glow inside the maw, bone
teeth; tar-black skin, bone, grey-green moss and violet glow.

  Skeeterror   a mosquito the size of a house on stilt legs, a bare skull for a head, a cluster of eyes in each socket and a bone needle
               longer than its body. Its wings blur, and its long swollen belly glows with what it has already drunk
  Manhandler   a giant hand of tar walking on its fingers, a mouth across the palm, eyes above it, its forearm dragging behind. It drums
               its fingers, one after the other, as if it's waiting for you. Then it rears up and grabs

What moves: the usual walk, idle and roar, and from rare_kit.py (SWAY in DinoLifeController): Stab and BuzzL, BuzzR (Skeeterror's needle
and wings), Curl1 to 4 and Thumb (Manhandler's fingers) and Sway bones.

Skin roles Body, Accent, Belly and Claw take the colour mutations; bone, wing skin, moss and the face keep theirs. EyeGlow, Glow and Wisp
glow (all already in shared/Roles.luau). Built at the first map's size. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0.
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
from rare_kit import cap, chain, curve, jointed, sabre, sheet, slit_eye, sweep, swing  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_shadow_bog_7_8"
BLEND = "shadow_bog_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = {"EyeGlow", "Glow", "Wisp"}

FACE = {"EyeGlow": "#ff4fd2", "Pupil": "#1a0f1f", "Slit": "#1a0f1f", "Highlight": "#fff0fb", "Glow": "#a865ff", "Wisp": "#f6e2ff", "Mouth": "#1a0f22", "Teeth": "#efe6d2",
        "Socket": "#0d0a12", "Tongue": "#5a2f6e", "BoneShade": "#c8bca0", "Moss": "#5d6e58", "MossLight": "#8a9b7c"}
BONE = "#ece4d0"
SKY, FLOOR = "#8d80b6", "#6a5a8e"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- Skeeterror


def stilt(m, bone, side, hip, knee, foot, width=1.0):
    """A long thin leg: up from the body to a knee over its back, then down a long way to a hooked bone claw."""
    m.use(bone, tuple(hip))
    h, k, f = Vector(hip), Vector(knee), Vector(foot)
    sweep(m, "Body", [(tuple(h), width * 1.1, width * 1.1), (tuple(h.lerp(k, 0.5)), width * 0.82, width * 0.82), (tuple(k), width * 0.9, width * 0.9), (tuple(k.lerp(f, 0.3)), width * 0.6, width * 0.6), (tuple(k.lerp(f, 0.72)), width * 0.46, width * 0.46)], sides=6)
    egg(m, "BoneKnob", tuple(k), width * 0.72, width * 0.72, width * 0.72, 6, 4)
    point(m, "BoneKnob", tuple(k + Vector((0, 0, 0.1))), tuple(k + Vector((side * 0.6, -0.3, 1.4))), width * 0.7)
    tip = k.lerp(f, 0.7)
    sabre(m, "BoneKnob", [tuple(tip), tuple(tip.lerp(f, 0.55)), tuple(f)], width * 0.5, 5)
    for t in (0.2, 0.42):  # barbs down the shin
        p = k.lerp(f, t)
        point(m, "Claw", tuple(p), tuple(p + Vector((side * 0.55, 0.1, 0.4))), width * 0.34)
    m.bone = "Spine"


def wing_blade(m, letter, side, root, tip, back):
    """A long tattered wing on one bone, which blurs (BuzzL, BuzzR): a thin skin between veins, its back edge torn."""
    m.use(f"Buzz{letter}", tuple(root), "Spine")
    r, t, b = Vector(root), Vector(tip), Vector(back)
    # The front edge, and the torn back edge with bites out of it.
    front = [r.lerp(t, k / 6) for k in range(7)]
    tears = (0.0, 1.0, 0.55, 1.0, 0.72, 0.95, 0.0)
    rear = []
    for k in range(7):
        u = k / 6
        wide = math.sin(math.pi * min(u * 1.08, 1)) ** 0.7
        rear.append(front[k] + b * wide * tears[k])
    middle = [p.lerp(q, 0.5) for p, q in zip(front, rear)]
    sheet(m, "WingSkin", [[tuple(p) for p in row] for row in (front, middle, rear)], [[f"Buzz{letter}"] * 7] * 3, 0.1)
    sweep(m, "Body", [(tuple(p), 0.4 - 0.05 * k, 0.4 - 0.05 * k) for k, p in enumerate(front)], sides=5)
    for k in (2, 3, 4, 5):  # veins
        beam(m, "Glow", tuple(front[k - 2]), tuple(rear[k] * 0.86 + front[k] * 0.14), 0.2, 0.2, 0.1)
    m.bone = "Spine"


def skeeterror():
    """A huge mosquito with a skull for a head, a needle for a mouth, and a belly full of light."""
    m = monster("dino_Skeeterror", Body="#17131c", Accent="#2d2438", Belly="#3c3050", Claw="#0b090e", BoneKnob=BONE, WingSkin="#2b2436")
    rng = random.Random(31)
    m.joint("Spine", (0, 0, 10.6))

    # The thorax: a hunched lump, tar over bone.
    sweep(m, "Body", [((0, -3.4, 10.4), 2.6, 2.6), ((0, -2.0, 10.8), 5.0, 5.0), ((0, 0.2, 11.4), 6.2, 6.0), ((0, 2.2, 11.3), 5.2, 5.0), ((0, 3.6, 10.9), 2.8, 2.8)], sides=10, under="Belly", under_faces=3)
    for k, (y, tall) in enumerate(((2.3, 1.3), (0.9, 1.9), (-0.6, 2.2), (-2.0, 1.7))):  # bone spikes along the hump
        point(m, "BoneKnob", (0, y, 13.8 - 0.14 * k * k * 0.6), (0, y - 0.8, 14.0 + tall - 0.1 * k), 1.2)
    for side in (-1, 1):
        for y, z in ((1.9, 13.0), (0.2, 13.6), (-1.5, 13.0)):
            point(m, "Accent", (side * 1.7, y, z - 0.4), (side * 2.8, y - 0.7, z + 0.6), 0.9)
        for k in range(4):  # moss hanging off it
            x, y = side * (2.8 - 0.1 * k), 2.2 - 1.3 * k
            sabre(m, "Moss" if k % 2 else "MossLight", [(x, y, 10.0), (x * 1.04, y, 9.0), (x * 1.06, y + 0.1, 8.2 - 0.3 * k)], 0.7, 4, flat=1.6)

    # Six stilt legs: the front pair reach forward to hold what it bites.
    for letter, side in (("L", -1), ("R", 1)):
        s = side
        stilt(m, f"Front{letter}", s, (s * 2.2, 2.4, 9.4), (s * 6.6, 6.4, 13.6), (s * 8.4, 13.2, 0.03), 1.1)
        stilt(m, f"Arm{letter}", s, (s * 2.7, 0.2, 9.6), (s * 10.0, 0.8, 16.2), (s * 14.6, 0.4, 0.03), 1.1)
        stilt(m, f"Back{letter}", s, (s * 2.2, -2.2, 9.8), (s * 8.4, -7.6, 17.0), (s * 11.6, -14.4, 0.03), 1.1)

    wing_blade(m, "L", -1, (-1.8, 0.8, 13.2), (-17.0, -8.6, 18.6), (3.4, -8.4, -1.4))
    wing_blade(m, "R", 1, (1.8, 0.8, 13.2), (17.0, -8.6, 18.6), (-3.4, -8.4, -1.4))

    # The belly: long, swollen, banded, sagging behind it, glowing with what it has drunk.
    route = curve([(0, -3.0, 10.4), (0, -6.2, 10.1), (0, -9.6, 9.0), (0, -13.0, 7.4), (0, -16.2, 5.9), (0, -18.6, 5.2)], 13)
    widths = (2.6, 4.2, 5.6, 6.6, 7.1, 7.3, 7.1, 6.6, 5.8, 4.8, 3.6, 2.2, 0.5)
    third = ("Spine", "Sway1a", "Sway1a", "Sway1a", "Sway1a", "Sway1b", "Sway1b", "Sway1b", "Sway1b", "Sway1c", "Sway1c", "Sway1c", "Sway1c")
    m.joint("Sway1a", route[1], "Spine")
    m.joint("Sway1b", route[5], "Sway1a")
    m.joint("Sway1c", route[9], "Sway1b")
    sweep(m, "Glow", [(p, w * 0.9, w * 0.86) for p, w in zip(route, widths)], third, sides=10, up=(0, 0.2, 1))
    for i in range(1, 12):  # dark bands over the light
        a, b = Vector(route[i]), Vector(route[i + 1])
        w = widths[i]
        m.bone = third[i]
        along = (b - a).normalized()
        sweep(m, "Body", [(tuple(a - along * 0.4), w * 0.92, w * 0.88), (tuple(a), w * 0.98, w * 0.94), (tuple(a + along * 0.4), w * 0.92, w * 0.88)], sides=10, up=(0, 0.2, 1))
        if i % 2 == 0:
            top = a + Vector((0, 0, w * 0.46))
            point(m, "BoneKnob", tuple(top), tuple(top + Vector((0, -0.8, 1.0))), 0.8)
    # Glowing veins and a wisp at the heart of it, seen through the skin where the bands leave a gap.
    m.bone = "Sway1b"
    end = Vector(route[-1])
    m.bone = "Sway1c"
    sabre(m, "BoneKnob", [tuple(end + Vector((0, 0.4, 0))), tuple(end + Vector((0, -1.0, -0.2))), tuple(end + Vector((0, -2.6, -0.1)))], 1.0, 5)
    m.bone = "Spine"

    # The neck, thin and jointed, carrying the head low and forward.
    m.joint("Neck", (0, 3.4, 10.6), "Spine")
    m.bone = "Neck"
    sweep(m, "Accent", [((0, 3.2, 10.8), 2.4, 2.4), ((0, 4.6, 10.2), 1.8, 1.8), ((0, 5.6, 9.8), 2.0, 2.0)], sides=8)

    # The head: a long bare skull, a cluster of burning eyes in each socket.
    m.use("Head", (0, 5.6, 9.8), "Neck")
    zm = 8.75
    sweep(m, "BoneKnob", [((0, 5.2, 10.3), 3.6, 3.4), ((0, 6.5, 10.7), 5.0, 3.9), ((0, 7.9, 10.5), 4.8, 3.3), ((0, 9.0, 9.9), 3.3, 2.2), ((0, 9.9, 9.45), 2.6, 1.4), ((0, 10.4, 9.25), 1.5, 0.8)], sides=8)
    sweep(m, "BoneShade", [((0, 6.3, 12.3), 2.2, 0.5), ((0, 7.8, 12.05), 1.8, 0.5), ((0, 9.0, 11.0), 0.9, 0.5)], sides=6)
    for side in (-1, 1):
        centre = (side * 1.5, 8.2, 10.4)
        egg(m, "Socket", centre, 1.32, 1.02, 1.08, 10, 5)
        # Bone brow slanting hard to the nose.
        beam(m, "BoneShade", (side * 3.0, 7.6, 12.0), (side * 0.3, 9.3, 10.75), 0.9, 0.8, 0.46)
        spots = [((side * 1.28, 8.92, 10.42), 0.42, "Pupil"), ((side * 2.05, 8.62, 10.6), 0.3, "Slit"), ((side * 1.95, 8.7, 10.0), 0.26, "Slit"), ((side * 1.2, 8.86, 9.86), 0.24, "Slit"), ((side * 0.82, 8.92, 10.2), 0.2, "Slit")]
        for at, r, pupil in spots:
            slit_eye(m, at, r, (side * 0.3, 0.94, -0.1), side, iris="EyeGlow", lid_role="Socket", top=0.3, tilt=0.5, low=0.16, pupil=pupil)
        for k in range(3):  # cracks in the skull, with the glow behind
            a = Vector((side * (0.9 + 0.5 * k), 6.0 + 0.5 * k, 12.3 - 0.1 * k))
            beam(m, "Glow", tuple(a), tuple(a + Vector((side * 0.5, 0.7, 0.04))), 0.12, 0.12, 0.08)
        # Feelers, like a dead fern, on the brow.
        names = chain(m, "Sway", 1 + (side + 3) // 2, curve([(side * 1.1, 9.4, 10.8), (side * 2.6, 10.8, 12.6), (side * 4.8, 11.0, 14.0), (side * 7.0, 9.6, 14.8)], 7), 0.34, 0.08, parent="Head", role="Accent")
        for k, name in enumerate(names):
            m.bone = name
            base = Vector(curve([(side * 1.1, 9.4, 10.8), (side * 2.6, 10.8, 12.6), (side * 4.8, 11.0, 14.0), (side * 7.0, 9.6, 14.8)], 7)[2 + 2 * k])
            for lean in (-1, 1):
                point(m, "Accent", tuple(base), tuple(base + Vector((lean * 0.4, -0.6 + lean * 0.9, 0.7))), 0.2)
        m.bone = "Head"
    sweep(m, "Mouth", [((0, 5.5, zm + 0.02), 3.3, 0.16), ((0, 9.0, zm + 0.1), 2.8, 0.14), ((0, 10.3, zm + 0.26), 1.3, 0.1)], sides=8)
    egg(m, "Glow", (0, 5.9, zm - 0.6), 1.3, 0.4, 0.9, 8, 5)
    for side in (-1, 1):
        for k in range(8):
            t = k / 7
            y, x = 6.2 + 4.0 * t, side * (1.65 - 0.9 * t * t)
            point(m, "Teeth", (x, y, zm + 0.14 + 0.2 * t), (x, y + 0.04, zm - 0.7 - 0.34 * (k % 2) + 0.2 * t), 0.3)

    m.use("Jaw", (0, 5.6, zm - 0.02), "Head")
    z = zm - 0.42
    sweep(m, "BoneKnob", [((0, 5.6, z), 3.2, 0.74), ((0, 8.2, z), 2.8, 0.66), ((0, 9.7, z + 0.1), 1.6, 0.5)], sides=8)
    sweep(m, "Mouth", [((0, 5.8, z + 0.34), 2.5, 0.08), ((0, 9.4, z + 0.32), 1.1, 0.08)], sides=8)
    for side in (-1, 1):
        for k in range(6):
            t = k / 5
            y, x = 6.3 + 3.2 * t, side * (1.3 - 0.65 * t * t)
            point(m, "Teeth", (x, y, z + 0.3), (x, y + 0.02, z + 0.86 + 0.2 * (k % 2)), 0.26)
    swing(m, ["Jaw"], (0, 5.6, zm - 0.02), -0.62)

    # The needle: out of its throat, longer than its body, with two feelers beside it. It stabs on its own bone.
    m.use("Stab", (0, 6.4, zm - 0.5), "Head")
    sabre(m, "BoneKnob", [(0, 6.4, zm - 0.5), (0, 9.8, zm - 1.5), (0, 14.0, zm - 3.6), (0, 18.2, zm - 6.4), (0, 21.4, zm - 8.5)], 0.72, 10, power=1.4)
    for k in range(4):  # barbs on the needle
        y = 11.0 + 2.2 * k
        zz = zm - 1.9 - 1.2 * k - 0.1 * k * k
        for side in (-1, 1):
            point(m, "BoneShade", (0, y, zz), (side * 0.42, y - 0.5, zz + 0.22), 0.2)
    m.bone = "Head"
    m.head_centre = (0, 9.0, 9.8)
    return m


# ---------------------------------------------------------------------- Manhandler


def finger(m, bone, curl, x, spread, length, thick, lean=0.0):
    """A long jointed finger from the bottom of the palm, out and down to a bone claw on the ground. bone turns it at the
    knuckle, curl at its middle joint. Returns the tip."""
    root = Vector((x, 1.8, 9.2))
    m.use(bone, tuple(root))
    side = 1 if x > 0 else -1
    k1 = root + Vector((spread * 0.7, 3.6 + lean, 0.1))  # out to the first knuckle, like a spider's leg
    k2 = k1 + Vector((spread * 0.5, 2.4 + lean * 0.5, -4.4))
    sweep(m, "Body", [(tuple(root), thick * 1.05, thick * 1.1), (tuple(root.lerp(k1, 0.55)), thick * 0.9, thick * 0.95), (tuple(k1), thick * 1.04, thick * 1.08)], sides=8, up=(0, -0.3, 1))
    egg(m, "Accent", tuple(k1), thick * 0.62, thick * 0.62, thick * 0.66, 8, 5)
    point(m, "BoneKnob", tuple(k1 + Vector((0, 0, thick * 0.3))), tuple(k1 + Vector((spread * 0.15, -0.6, thick * 0.6 + 1.5))), thick * 0.54)
    m.use(curl, tuple(k1), bone)
    sweep(m, "Body", [(tuple(k1), thick * 0.98, thick), (tuple(k1.lerp(k2, 0.5)), thick * 0.82, thick * 0.84), (tuple(k2), thick * 0.92, thick * 0.92)], sides=8)
    egg(m, "Accent", tuple(k2), thick * 0.54, thick * 0.54, thick * 0.56, 8, 5)
    foot = Vector((k2.x + spread * 0.12, k2.y + 0.5, 0.03))
    tip = k2.lerp(foot, 0.62)
    sweep(m, "Body", [(tuple(k2), thick * 0.84, thick * 0.84), (tuple(tip), thick * 0.62, thick * 0.62)], sides=8)
    sabre(m, "BoneKnob", [tuple(tip + Vector((0, -0.2, 0.4))), tuple(tip.lerp(foot, 0.5) + Vector((0, 0.5, 0))), tuple(foot + Vector((0, 0.7, 0)))], thick * 0.66, 5)
    m.bone = "Spine"


def manhandler():
    """A giant hand on its fingertips, palm to the front, a mouth across the palm."""
    m = monster("dino_Manhandler", Body="#1b1622", Accent="#2f2640", Belly="#463a5c", Claw="#0b090e", BoneKnob=BONE)
    rng = random.Random(3)
    m.joint("Spine", (0, 0, 13.0))

    # The palm: a thick slab standing on the fingers, leaning forward, its face to the front.
    sweep(m, "Body", [((0, 0.4, 7.8), 14.0, 4.6), ((0, 0.3, 11.0), 15.6, 5.8), ((0, -0.4, 15.4), 15.2, 5.8), ((0, -1.8, 19.0), 12.4, 5.4), ((0, -3.6, 21.4), 8.4, 5.0)], sides=10, up=(0, 1, 0.2))

    # Four fingers for legs.
    finger(m, "FrontL", "Curl1", -5.2, -2.6, 9, 2.7, 0.0)
    finger(m, "FrontR", "Curl2", -1.75, -0.8, 10, 2.8, 0.6)
    finger(m, "BackR", "Curl3", 1.75, 0.8, 10, 2.8, 0.6)
    finger(m, "BackL", "Curl4", 5.2, 2.6, 9, 2.6, 0.0)

    # The thumb, out to one side, reaching for you.
    thumb_root = Vector((7.0, 2.2, 14.2))
    m.use("Thumb", tuple(thumb_root))
    t1, t2, t3 = thumb_root + Vector((3.2, 2.4, 0.4)), thumb_root + Vector((5.0, 5.4, 0.2)), thumb_root + Vector((4.6, 8.8, -2.4))
    sweep(m, "Body", [(tuple(thumb_root), 4.2, 4.6), (tuple(t1), 3.6, 3.7), (tuple(t2), 3.1, 3.1), (tuple(t2.lerp(t3, 0.6)), 2.3, 2.3)], sides=8)
    egg(m, "Accent", tuple(t1), 2.0, 2.0, 2.0, 8, 5)
    egg(m, "Accent", tuple(t2), 1.7, 1.7, 1.7, 8, 5)
    point(m, "BoneKnob", tuple(t1 + Vector((0, 0, 1.3))), tuple(t1 + Vector((0.4, -0.6, 3.0))), 1.5)
    point(m, "BoneKnob", tuple(t2 + Vector((0.6, 0, 1.0))), tuple(t2 + Vector((1.2, -0.5, 2.6))), 1.3)
    sabre(m, "BoneKnob", [tuple(t2.lerp(t3, 0.55)), tuple(t3), tuple(t3 + Vector((-1.2, 2.0, -1.4)))], 1.9, 6)
    m.bone = "Spine"

    # The forearm, dragging behind it like a tail: a bone sticking out of the tar along its back.
    path = [(p, w, w * 0.9) for p, w in zip(curve([(0, -3.2, 18.8), (0, -6.6, 17.4), (0, -9.8, 13.6), (0, -13.4, 9.0), (0, -17.6, 5.2), (0, -22.0, 3.0), (0, -26.0, 1.9)], 12),
                                            (7.6, 7.4, 7.0, 6.6, 6.2, 5.6, 5.0, 4.4, 3.7, 3.0, 2.2, 0.5))]
    bones = jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], path, under="Belly", under_faces=3)
    for i, (p, w, _) in enumerate(path[:-1]):
        m.bone = bones[i]
        if i % 2 == 0:
            base = Vector(p) + Vector((0, 0, w * 0.4))
            point(m, "BoneKnob", tuple(base), tuple(base + Vector((0, -1.1, 1.0 + 1.5 * (1 - i / 12)))), 1.4 * (1 - i / 16))
        for side in (-1, 1):
            if i % 3 == 1:
                base = Vector(p) + Vector((side * w * 0.42, 0, 0))
                sabre(m, "Moss" if i % 2 else "MossLight", [tuple(base), tuple(base + Vector((side * 0.3, -0.1, -1.4))), tuple(base + Vector((side * 0.3, 0.1, -2.6)))], 1.0, 4, flat=1.6)
    m.bone = "Spine"

    # The mouth, right across the palm: a lipped hole, a glowing throat, long needle teeth all round. The lower half is on the Jaw.
    mid = Vector((0, 3.0, 13.4))
    rx, rz = 6.9, 3.4

    def rim(a, grow=1.0, out=0.0):
        """A point on the mouth's edge, a in radians from the right corner round the top. The palm leans back as it rises."""
        z = rz * grow * math.sin(a)
        return mid + Vector((rx * grow * math.cos(a), -0.2 * z + out, z))

    count = 18
    ring = [tuple(rim(i * math.tau / count)) for i in range(count + 1)]
    lower = [math.sin(i * math.tau / count) < -0.02 for i in range(count + 1)]
    m.joint("Jaw", (0, -0.6, 13.0), "Spine")
    sweep(m, "Accent", [(p, 1.25, 1.5) for p in ring], ["Jaw" if low else "Spine" for low in lower], sides=6, caps=(False, False), up=(0, 1, 0))
    m.bone = "Spine"
    egg(m, "Mouth", tuple(mid + Vector((0, -0.2, 0))), rx * 0.98, 0.5, rz * 0.98, 12, 6)
    egg(m, "Glow", tuple(mid + Vector((0, 0.02, -0.5))), rx * 0.52, 0.5, rz * 0.5, 10, 5)
    egg(m, "Wisp", tuple(mid + Vector((0, 0.3, -0.5))), rx * 0.22, 0.42, rz * 0.2, 8, 4)
    for i in range(24):
        a = (i + 0.5) * math.tau / 24
        low = math.sin(a) < 0
        m.bone = "Jaw" if low else "Spine"
        reach = 0.42 if i % 2 else 0.6
        base, tip = rim(a, 0.98, 0.5), rim(a, 1 - reach, 0.9)
        tip = tip.lerp(Vector((base.x, tip.y, tip.z)), 0.72)  # teeth point across the mouth, not at its middle
        point(m, "Teeth", tuple(base), tuple(tip), 1.05 if i % 2 else 1.25)
    swing(m, ["Jaw"], (0, -0.6, 13.0), -0.14)
    m.bone = "Spine"

    # Eyes over the mouth: a burning pair under a hard brow, and smaller ones crowding up the palm.
    for side in (-1, 1):
        at = (side * 2.5, 1.58, 18.1)
        look = (side * 0.2, 0.94, -0.26)
        egg(m, "Socket", at, 1.36, 0.5, 0.9, 10, 5)
        slit_eye(m, (side * 2.55, 1.58, 18.08), 0.6, look, side, iris="EyeGlow", lid_role="Accent", top=0.54, tilt=0.82, low=0.42)
        beam(m, "Accent", (side * 5.4, 0.6, 19.9), (side * 0.15, 2.0, 18.0), 1.3, 1.0, 0.7)
    for x, z, r in ((-5.9, 16.9, 0.32), (5.9, 16.8, 0.34), (-4.6, 20.0, 0.28), (4.5, 20.1, 0.26), (0.0, 20.5, 0.36), (-6.6, 14.6, 0.26), (6.6, 14.4, 0.26)):
        y = 2.5 - (z - 15) * 0.36 - 0.1
        egg(m, "Socket", (x, y, z), r * 1.7, r * 0.8, r * 1.4, 8, 4)
        slit_eye(m, (x, y + 0.14, z), r, (x * 0.04, 0.94, -0.26), 1 if x > 0 else -1, iris="EyeGlow", lid_role="Accent", top=0.36, tilt=0.6, low=0.22, pupil="Slit")

    # The lines of the palm, burning. A fortune teller wouldn't like them.
    for pts in ([(-7.4, 1.4, 11.0), (-7.9, 2.2, 9.4), (-5.8, 2.3, 8.6), (-3.4, 2.3, 8.4)], [(7.4, 1.4, 11.0), (7.9, 2.2, 9.4), (5.8, 2.3, 8.6), (3.4, 2.3, 8.4)]):
        for a, b in zip(pts, pts[1:]):
            beam(m, "Glow", a, b, 0.26, 0.22, 0.16)
    m.bone = "Spine"
    m.head_centre = (0, 3.0, 15.0)
    return m


ALL = [skeeterror, manhandler]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "shadow_bog_7_8", SKY, FLOOR, GLOW_ROLES, glow=1.0, spacing=44)


if __name__ == "__main__":
    main()
