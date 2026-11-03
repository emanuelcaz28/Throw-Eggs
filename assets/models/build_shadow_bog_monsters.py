"""Builds the Shadow Bog's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_shadow_bog_monsters.py

Saves shadow_bog_monsters.blend and renders to design/world/monsters_shadow_bog/. Shadow Bog's props are in
build_shadow_bog.py.

The owner asked for a step more aggressive and interesting than the Frozen Peaks, and for creatures that look
weird in a good way: they don't need to make sense. So even the common ones are hostile here, and none of them
is quite an animal. The bog face: glowing magenta eyes with a slit pupil, never just two (spare eyes crowd
round the main pair, or one is far too big), and a maw that glows violet inside like the wisps, crammed with
crooked bone-white teeth, tar dripping off the jaw. Tar-black skin, bone, grey-green moss and violet glow,
the map's colours, so they belong to it on sight.

  Sticky Steve   a dollop of tar that wants a hug: a grin too wide for it, one huge eye and one tiny one,
                 arms up to grab, tar stretching from its arms, things it caught stuck in it
  Slow Bob       a slug wearing a dead monster's skull as a shell, with a lamprey mouth ringed with teeth
                 and three eyes on stalks (two wave about, one droops)
  Terror Bird    a plucked black bird with a hooked beak full of teeth, five eyes, a ruff of quills and
                 skeleton wings with bone fingers
  Pitch Raptor   a raptor of wet pitch whose face splits four ways: jaws top and bottom and a pincer on each
                 side, six spider eyes, mantis scythes for arms and a bone blade on its tail
  Tar Titan      a hunched giant with no neck: its whole front is one mouth of gravestone teeth, seven eyes
                 in a row over it, ribs bursting out of its back round a trapped wisp
  Bog Rex        the boss: three heads (a bare skull in the middle, a cyclops and a three-eyed one on necks
                 from its shoulders), its rib cage open with a wisp glowing inside, a crown of roots
                 hung with glowing pods

All have the Jaw bone, so they snap and roar in the game. Spare parts ride the bones the game already moves:
Slow Bob's eye stalks, Pitch Raptor's pincers, Terror Bird's wings and Bog Rex's side heads are on the Wing
bones, which roll as they walk. Glowing parts are EyeGlow, Glow and Wisp (Neon in the game, shared/Roles.luau).
Built at the first map's size; the game makes them 5.2x (Config/Biomes standardScale).
1 Blender unit = 1 stud, models face +Y, feet on Z = 0.
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_desert import beam, quad_legs  # noqa: E402
from build_forest import Model, biped_legs, tail  # noqa: E402
from build_shadow_bog import limb, moss_beard  # noqa: E402
from build_volcano import prism, ring_at, top_of  # noqa: E402
from face_kit import icicle  # noqa: E402
from monster_stage import build_and_render  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_shadow_bog"

GLOW_ROLES = {"EyeGlow", "Glow", "Wisp"}

# The bog face, and the map's colours (build_shadow_bog.py).
FACE = {"EyeGlow": "#ff4fd2", "Pupil": "#1a0f1f", "Highlight": "#fff0fb", "Glow": "#a865ff", "Wisp": "#f6e2ff",
        "Mouth": "#1a0f22", "Teeth": "#efe6d2"}
BONE, BONE_SHADE, SOCKET = "#ece4d0", "#c8bca0", "#151119"
GLOSS = "#9284bf"  # the violet sky caught in wet tar
MOSS, MOSS_DARK = "#8a9b7c", "#5d6e58"
SKY, FLOOR = "#8d80b6", "#6a5a8e"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- the bog face


def glow_eye(m, x, y, z, size, side, facing="front", slant=0.8, brow=True, brow_role="Accent", wide=1.2):
    """One glowing eye with an upright slit pupil glaring towards the nose, under a brow that slants down
    towards it. facing "front": y is the front face of the head; "side": x is the side face it sits on, and
    the brow slants down towards the front. side is which side of the face the eye is on (-1 left, 1 right).
    brow can be "v" for one eye in the middle (a cyclops): both halves slant down to the middle."""
    w, d, h = size * wide, size * 0.9, size * 0.8
    bh = size * 0.36
    top = z + h / 2
    if facing == "front":
        cy = y - size * 0.32
        fy = cy + d / 2
        m.block("EyeGlow", x, cy, z, w, d, h)
        px = x - side * w * 0.1
        m.block("Pupil", px, fy + size * 0.02, z - h * 0.03, size * 0.2, size * 0.08, h * 0.84)
        m.block("Highlight", px + side * size * 0.09, fy + size * 0.07, z + h * 0.25, size * 0.16, size * 0.05, size * 0.16)
        if not brow:
            return
        brow_y, brow_d = cy + size * 0.12, d + size * 0.3
        low = top - slant * size * 0.3 + bh * 0.2
        high = top + bh * 0.25
        if brow == "v":
            for s in (-1, 1):
                m.loft_x(brow_role, (x, brow_y, low, brow_d, bh), (x + s * (w / 2 + size * 0.1), brow_y, high, brow_d, bh))
        else:
            m.loft_x(brow_role, (x - side * (w / 2 + size * 0.1), brow_y, low, brow_d, bh),
                     (x + side * (w / 2 + size * 0.1), brow_y, high, brow_d, bh))
    else:
        cx = x - side * size * 0.32
        fx = cx + side * d / 2
        m.block("EyeGlow", cx, y, z, d, w, h)
        py = y + w * 0.1
        m.block("Pupil", fx + side * size * 0.02, py, z - h * 0.03, size * 0.08, size * 0.2, h * 0.84)
        m.block("Highlight", fx + side * size * 0.07, py + size * 0.09, z + h * 0.25, size * 0.05, size * 0.16, size * 0.16)
        if brow:
            brow_x = cx + side * size * 0.12
            m.loft_y(brow_role, (y - w / 2 - size * 0.1, brow_x, top + bh * 0.25, d + size * 0.3, bh),
                     (y + w / 2 + size * 0.1, brow_x, top - slant * size * 0.3 + bh * 0.2, d + size * 0.3, bh))


def maw(m, front, mouth_z, skull_w, length, snout_w, upper_h, lower_h, gap, rng, cx=0.0, upper="Body", lower="Belly",
        tooth=0.24, per_side=4, front_row=2, crooked=0.35, gravestones=False, ring=False, grin=0.0, skull_d=1.0, jaw=True,
        drips=(), drip_role="Accent", on_jaw=None):
    """The bog maw: open, glowing violet inside, crooked teeth along both jaws and front_row more across the
    front of the upper one (one fewer on the lower), so it reads head-on (gravestones: flat-topped slabs);
    ring: more teeth on the side walls, like a lamprey. The lower jaw goes on a Jaw bone hinged at the back of
    the mouth unless jaw is False (the side heads, which can't move theirs). drips are (x share of the jaw's
    half width, length): tar hanging off the jaw. Call it on the head's bone; cx moves the whole mouth sideways.
    Returns the snout's tip and its top height along it."""
    head_bone = m.bone
    upper_z = mouth_z + gap / 2 + upper_h / 2
    lower_z = mouth_z - gap / 2 - lower_h / 2
    back = (front - 0.05, cx, upper_z + upper_h * 0.1, skull_w * 0.94, upper_h * 1.2)
    tip = (front + length, cx, upper_z, snout_w, upper_h)
    m.loft_y(upper, back, tip)
    # The glow stops short of the lips, so the front teeth stand out against it.
    m.block("Glow", cx, front + length * 0.36, mouth_z + gap * 0.05, snout_w * 0.84, length * 0.72, gap + 0.04)
    m.block("Mouth", cx, front + 0.05, mouth_z - lower_h * 0.45, snout_w * 0.78, 0.12, gap + lower_h * 0.9)

    def at_lip(lip, size):
        return lip - (size * 0.25 if gravestones else size * 0.5)

    def fang(x, y, z, size, down):
        if gravestones:
            tall = size * 1.15
            m.block("Teeth", x, y, z - tall / 2 if down else z + tall / 2, size * 0.8, size * 0.5, tall)
            return
        lean = (rng.uniform(-1, 1) * crooked * size * 0.6, rng.uniform(-1, 1) * crooked * size * 0.4)
        point = (x + lean[0], y + lean[1])
        if down:
            m.loft_z("Teeth", (z - size, *point, size * 0.15, size * 0.15), (z, x, y, size, size))
        else:
            m.loft_z("Teeth", (z, x, y, size, size), (z + size, *point, size * 0.15, size * 0.15))

    def size_of(i, scale=1.0):
        return tooth * scale * (1.0 if i % 2 == 0 else 0.68) * rng.uniform(1 - crooked * 0.5, 1 + crooked * 0.4)

    edge = mouth_z + gap / 2 + 0.02
    for side in (-1, 1):
        for i in range(per_side):
            y = front + length * (0.14 + 0.72 * i / max(per_side - 1, 1))
            size = size_of(i)
            fang(cx + side * (ring_at(back, tip, y)[3] / 2 - size * 0.5), y, edge, size, True)
        if ring:
            wall = cx + side * snout_w * 0.42
            for k in range(3):
                z = mouth_z + gap * (-0.3 + 0.3 * k)
                y = front + length * 0.8
                s = tooth * 0.7
                m.loft_x("Teeth", (wall, y, z, s, s), (wall - side * s, y + 0.02, z, 0.03, 0.03))
    span = snout_w * 0.78
    for k in range(front_row):
        size = size_of(k) * 0.95
        fang(cx - span / 2 + span * (k + 0.5) / front_row, at_lip(front + length, size), edge, size, True)

    if jaw:
        m.use("Jaw", (cx, front - 0.05, mouth_z), head_bone)
    lower_length = length * 0.92
    jaw_back = (front - 0.05, cx, lower_z, skull_w * 0.85, lower_h)
    jaw_tip = (front + lower_length, cx, lower_z, snout_w * 0.9, lower_h)
    m.loft_y(lower, jaw_back, jaw_tip)
    m.block("Glow", cx, front + lower_length * 0.38, mouth_z - gap / 2 + 0.02, snout_w * 0.62, lower_length * 0.7, 0.06)
    floor = mouth_z - gap / 2 - 0.02
    count = max(per_side - 1, 1)
    for side in (-1, 1):
        for i in range(count):
            y = front + lower_length * (0.22 + 0.6 * i / max(count - 1, 1))
            size = size_of(i, 0.78)
            fang(cx + side * (ring_at(jaw_back, jaw_tip, y)[3] / 2 - size * 0.5), y, floor, size, False)
    lower_row = front_row - 1
    span = snout_w * 0.66
    for k in range(lower_row):
        size = size_of(k + 1, 0.8)
        fang(cx - span / 2 + span * (k + 0.5) / lower_row, at_lip(front + lower_length, size), floor, size, False)
    for share, hang in drips:
        x = cx + share * snout_w * 0.45
        y = front + lower_length * rng.uniform(0.45, 0.8)
        icicle(m, drip_role, x, y, lower_z - lower_h / 2 + 0.06, hang, max(tooth * 0.9, 0.14))
    if on_jaw:
        on_jaw(m, front, mouth_z, gap, lower_length)
    m.bone = head_bone

    if grin:
        line_h = max(gap, 0.06) * 0.8
        for side in (-1, 1):
            x = cx + side * (skull_w / 2 + 0.005)
            m.loft_y("Glow", (front - skull_d * 0.38, x, mouth_z + grin, 0.04, line_h * 0.7), (front + 0.02, x, mouth_z, 0.04, line_h))
    return {"tip": front + length, "top": lambda y: top_of((back, tip), y), "lower_z": lower_z}


def strand(m, role, a, b, width, bone_a, bone_b):
    """A strand of tar stretched between two bones: it pulls longer and shorter as they move."""
    beam(m, role, a, b, width)
    m.groups[role][-8:-4] = [bone_a] * 4
    m.groups[role][-4:] = [bone_b] * 4


def stub_leg(m, x, y, top, width):
    """One more of quad_legs' legs, on the current bone."""
    m.loft_z("Body", (0.3, x, y, width * 0.8, width * 0.8), (top + 0.2, x, y, width, width * 1.1))
    m.block("Belly", x, y + width * 0.12, width * 0.16, width * 1.02, width * 1.15, width * 0.32)
    for offset in (-0.3, 0, 0.3):
        claw = width * 0.18
        m.block("Claw", x + offset * width, y + width * 0.68, claw * 0.7, claw, claw, claw * 1.3)


def pod(m, x, y, top, length, stalk="RootsDark"):
    """A glowing pod hanging on a stalk, like the gloom trees grow."""
    m.block(stalk, x, y, top - length / 2, 0.14, 0.14, length)
    m.loft_z("Glow", (top - length - 0.42, x, y, 0.42, 0.42), (top - length + 0.04, x, y, 0.7, 0.7))
    m.loft_z("Glow", (top - length - 0.95, x, y, 0.22, 0.22), (top - length - 0.42, x, y, 0.42, 0.42))


def wisp(m, x, y, z, s):
    """A trapped will-o'-wisp: a glowing blob with a white-hot heart."""
    m.loft_z("Glow", (z - s * 0.7, x, y, s * 0.8, s * 0.8), (z, x, y, s * 1.4, s * 1.4))
    m.loft_z("Glow", (z, x, y, s * 1.4, s * 1.4), (z + s * 0.9, x, y, s * 0.9, s * 0.9))
    m.loft_z("Glow", (z + s * 0.9, x, y, s * 0.9, s * 0.9), (z + s * 1.6, x - s * 0.15, y, 0.05, 0.05))
    m.block("Wisp", x, y, z + s * 0.1, s * 0.7, s * 0.7, s * 0.8)


# ---------------------------------------------------------------------- the common ones (still hostile)


def sticky_steve():
    """Silly, but it wants a hug and it won't let go: a dollop of tar on stubby legs with a grin far too wide
    for its face, one huge eye glaring and one tiny one popping, arms up to grab you with tar stretching off
    them, and the things it already caught stuck in it: a bone through its head, a little skull in its side."""
    m = monster("dino_StickySteve", Body="#3d2f58", Accent="#231a35", Belly="#55457a", Claw="#171021", Gloss=GLOSS,
                Bone=BONE, BoneShade=BONE_SHADE, Socket=SOCKET)
    rng = random.Random(1)
    m.joint("Spine", (0, 0, 1.5))
    biped_legs(m, 0.62, 0.0, 1.05, 0.8, 0.95, 0.55, 0.85, 0.26)
    m.loft_z("Body", (0.75, 0, 0, 1.9, 1.7), (1.75, 0, 0.05, 2.35, 2.0))
    m.loft_z("Body", (1.75, 0, 0.05, 2.35, 2.0), (2.4, 0, 0.05, 2.2, 1.9))
    m.loft_z("Belly", (0.9, 0, 0.78, 1.2, 0.4), (2.0, 0, 0.95, 1.5, 0.35))
    for x, y, length in ((-0.8, 0.6, 0.45), (0.9, 0.4, 0.35), (0.2, 0.85, 0.55), (-1.0, -0.5, 0.4)):
        icicle(m, "Accent", x, y, 0.95, length, 0.22)
    # The little skull it caught, stuck in its side.
    sx, sy, sz = 1.12, 0.25, 1.55
    m.block("Bone", sx, sy, sz, 0.42, 0.62, 0.5)
    m.block("Bone", sx + 0.02, sy + 0.12, sz - 0.33, 0.34, 0.4, 0.18)
    for dy in (-0.14, 0.14):
        m.block("Socket", sx + 0.2, sy + dy, sz + 0.06, 0.06, 0.16, 0.16)
    m.block("Socket", sx + 0.2, sy, sz - 0.16, 0.05, 0.08, 0.1)

    # Arms up, claws out, ready to grab; tar strands stretch from them to its sides.
    for side in (-1, 1):
        arm = "ArmL" if side < 0 else "ArmR"
        x = side * 1.1
        m.use(arm, (x, 0.2, 2.0))
        beam(m, "Body", (x, 0.2, 2.0), (side * 1.55, 0.85, 2.9), 0.5, None, 0.42)
        hand = (side * 1.6, 0.95, 3.05)
        m.block("Body", *hand, 0.62, 0.55, 0.55)
        for offset in (-0.18, 0, 0.18):
            m.loft_y("Claw", (hand[1] + 0.2, hand[0] + offset, hand[2] + 0.05, 0.13, 0.15), (hand[1] + 0.55, hand[0] + offset * 1.3, hand[2] + 0.3, 0.03, 0.03))
        icicle(m, "Accent", hand[0], hand[1] - 0.05, hand[2] - 0.25, 0.55, 0.18)
        m.bone = "Spine"
        strand(m, "Accent", (side * 1.45, 0.65, 2.65), (side * 1.12, 0.35, 1.4), 0.12, arm, "Spine")
        strand(m, "Accent", (side * 1.6, 0.9, 2.8), (side * 1.12, 0.6, 2.05), 0.09, arm, "Spine")

    w, d, h = 2.25, 1.95, 1.6
    yc, zc = 0.1, 3.05
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    # The dollop on top, flopping over backwards.
    top = zc + h / 2
    m.loft_z("Body", (top, 0, 0.05, 2.05, 1.8), (top + 0.65, 0, -0.15, 1.2, 1.05))
    m.loft_z("Body", (top + 0.65, 0, -0.15, 1.2, 1.05), (top + 1.2, 0, -0.55, 0.22, 0.22))
    maw(m, front, zc - 0.55, w, 0.5, 2.2, 0.34, 0.36, 0.46, rng, tooth=0.27, per_side=3, front_row=6, crooked=0.6, grin=0.34,
        skull_d=d, drips=((-0.7, 0.5), (0.15, 0.8), (0.75, 0.42)))
    glow_eye(m, -0.5, front, zc + 0.42, 0.72, -1, slant=1.1)  # the big angry one
    glow_eye(m, 0.62, front, zc + 0.55, 0.34, 1, slant=-0.6)  # the tiny one, popping
    glow_eye(m, 0.12, 0.72, top + 0.3, 0.24, 1, brow=False)  # a spare one, up in the dollop
    # The bone stuck right through its head, and wet shine on the tar.
    beam(m, "Bone", (-1.45, -0.25, top + 0.75), (1.35, 0.1, top + 0.05), 0.2)
    for end in ((-1.45, -0.25, top + 0.75), (1.35, 0.1, top + 0.05)):
        for dz in (-0.12, 0.12):
            m.block("Bone", end[0], end[1], end[2] + dz, 0.3, 0.3, 0.26)
    for side, y, z in ((-1, 0.4, zc - 0.1), (1, -0.3, zc + 0.2)):  # wet shine on its cheeks
        m.block("Gloss", side * (w / 2 + 0.01), y, z, 0.06, 0.45, 0.18)
    m.head_centre = (0, front + 0.2, zc + 0.1)
    return m


def slow_bob():
    """Slow, and it doesn't need to be fast: a fat slug with six stubby legs, wearing the skull of something
    huge that sank in the tar as its shell, the skull's teeth biting into its back. Its face is a lamprey's,
    a round mouth ringed with teeth, and it looks round on three eye stalks: two wave about, one droops."""
    m = monster("dino_SlowBob", Body="#6b5480", Accent="#3e304f", Belly="#9a82a8", Claw="#2a2030", Bone=BONE,
                BoneShade=BONE_SHADE, Socket=SOCKET, Moss=MOSS, Slime="#c3b0e3")
    rng = random.Random(2)
    m.joint("Spine", (0, -0.5, 1.2))
    quad_legs(m, 0.85, 0.9, 0.85, -1.7, 0.85, 0.5)
    for leg, side in (("FrontL", -1), ("FrontR", 1)):  # the middle pair steps with the front
        m.bone = leg
        stub_leg(m, side * 0.9, -0.4, 0.85, 0.48)
    m.bone = "Spine"
    body = ((-1.9, 0, 1.15, 1.9, 1.35), (0.4, 0, 1.25, 2.1, 1.55))
    m.loft_y("Body", *body)
    m.loft_y("Body", (0.4, 0, 1.25, 2.1, 1.55), (1.45, 0, 1.2, 1.8, 1.3))
    m.loft_y("Belly", (-1.9, 0, 0.6, 1.6, 0.35), (1.35, 0, 0.62, 1.7, 0.35))
    for y in (-1.6, 0.6, 1.1):
        m.block("Accent", 0, y, top_of(body, min(y, 0.4)) + 0.02, 1.7, 0.24, 0.12)
    tail(m, (-1.85, 1.1, 1.8, 1.25), (-4.4, 0.45, 0.35, 0.3), 3)
    for bone, y, z, width in (("Tail1", -2.4, 1.48, 1.45), ("Tail2", -3.25, 1.1, 1.0), ("Tail3", -4.0, 0.78, 0.58)):
        m.bone = bone
        m.block("Accent", 0, y, z, width, 0.22, 0.12)
    m.bone = "Spine"
    for x, y in ((-0.95, -1.0), (0.98, -0.2), (-0.92, 0.7)):
        icicle(m, "Slime", x, y, 0.75, 0.45, 0.18)

    # The skull shell: a horned skull looking forward over its head, its teeth biting into the slug's back.
    base = top_of(body, -0.2)
    low = base + 0.25  # the skull's bottom edge, a little above the slug
    face = 0.6
    m.block("Bone", 0, -0.35, low + 0.7, 2.0, 1.9, 1.4)
    m.loft_y("Bone", (-1.3, 0, low + 0.75, 1.9, 1.3), (-2.3, 0, low + 0.6, 1.3, 0.8))  # the back of the skull
    m.block("Bone", 0, face - 0.1, low + 1.15, 2.1, 0.32, 0.36)  # brow ridge
    for side in (-1, 1):
        m.block("Socket", side * 0.5, face + 0.02, low + 0.75, 0.75, 0.08, 0.62)
        m.block("Glow", side * 0.5, face + 0.05, low + 0.72, 0.36, 0.06, 0.32)
        limb(m, "Bone", [(side * 0.78, -0.55, low + 1.3), (side * 1.3, -1.15, low + 1.8), (side * 1.3, -1.85, low + 1.7),
                         (side * 0.95, -2.3, low + 1.25)], 0.46, 0.12)
        moss_beard(m, side * 1.02, -0.3, low + 1.35, 1.1, 0.3)
    m.block("Socket", 0, face + 0.02, low + 0.32, 0.3, 0.08, 0.3)  # the nose hole
    for k in range(6):  # its teeth, biting down into the slug
        x = -0.75 + k * 0.3
        s = 0.2 if k % 2 else 0.25
        m.loft_z("Bone", (base - 0.15, x, face - 0.12, 0.04, 0.04), (low + 0.02, x, face - 0.12, s, s))
    for p, q in (((0.55, face - 0.3, low + 1.42), (0.15, -0.3, low + 1.42)), ((0.15, -0.3, low + 1.42), (0.4, -0.85, low + 1.42))):
        beam(m, "BoneShade", p, q, 0.12, 0.05)

    m.use("Neck", (0, 1.35, 1.25))
    m.loft_y("Body", (1.2, 0, 1.2, 1.75, 1.25), (1.8, 0, 1.25, 1.6, 1.2))
    m.stretch("Body", "Spine")
    w, d, h = 1.6, 1.1, 1.35
    yc, zc = 2.25, 1.3
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    maw(m, front, 1.22, w, 0.42, 1.5, 0.3, 0.3, 0.56, rng, tooth=0.2, per_side=4, front_row=5, crooked=0.3, ring=True,
        skull_d=d, drips=((-0.5, 0.35), (0.45, 0.5)), drip_role="Slime")
    # Three eye stalks: two wave about on the Wing bones, the third droops over the mouth.
    for side, height in ((-1, 3.05), (1, 3.35)):
        m.use("WingL" if side < 0 else "WingR", (side * 0.45, 2.1, 1.9), "Head")
        tip = (side * 0.85, 2.3, height)
        beam(m, "Body", (side * 0.45, 2.1, 1.85), tip, 0.26, None, 0.2)
        m.block("EyeGlow", tip[0], tip[1] + 0.02, tip[2] + 0.22, 0.5, 0.5, 0.48)
        m.block("Pupil", tip[0] - side * 0.04, tip[1] + 0.28, tip[2] + 0.2, 0.11, 0.06, 0.38)
        m.block("Highlight", tip[0] + side * 0.05, tip[1] + 0.31, tip[2] + 0.33, 0.08, 0.04, 0.08)
        m.loft_x("Accent", (tip[0] - side * 0.34, tip[1] + 0.05, tip[2] + 0.4, 0.62, 0.16),
                 (tip[0] + side * 0.34, tip[1] + 0.05, tip[2] + 0.56, 0.62, 0.16))
    m.bone = "Head"
    limb(m, "Body", [(0.05, 2.1, 1.95), (0.12, 2.75, 2.5), (0.2, 3.3, 2.25)], 0.22, 0.16)
    m.block("EyeGlow", 0.22, 3.42, 2.02, 0.34, 0.34, 0.32)
    m.block("Pupil", 0.22, 3.6, 1.97, 0.08, 0.05, 0.26)
    m.block("Accent", 0.22, 3.42, 2.2, 0.4, 0.4, 0.12)  # its lid, half shut
    m.head_centre = (0, front + 0.3, 1.9)
    return m


def terror_bird():
    """A tall plucked black bird that never learned to be a bird: a hooked beak that gapes open on rows of
    teeth, five glowing eyes, a ruff of black quills, ragged quills down its back, skeleton wings ending in
    bone fingers, and moss hanging off its beak like a beard."""
    m = monster("dino_TerrorBird", Body="#3a3147", Accent="#17131f", Belly="#5e5070", Claw="#14101a", Beak="#d9cba8",
                BeakDark="#8f7f62", Bone=BONE, Moss=MOSS)
    rng = random.Random(3)
    m.joint("Spine", (0, -0.3, 3.1))
    biped_legs(m, 0.45, -0.3, 2.65, 0.7, 1.05, 0.24, 1.25, 0.24)
    for side in (-1, 1):  # a hooked killing claw on each foot
        m.bone = "ShinL" if side < 0 else "ShinR"
        m.loft_y("Claw", (-0.05, side * 0.45, 0.35, 0.16, 0.24), (0.35, side * 0.45, 0.85, 0.04, 0.04))
    m.bone = "Spine"
    torso = ((-1.25, 0, 3.05, 1.15, 1.1), (0.85, 0, 3.45, 1.55, 1.7))
    m.loft_y("Body", *torso)
    m.loft_y("Belly", (-0.7, 0, 2.65, 1.0, 0.5), (0.85, 0, 2.85, 1.3, 0.75))
    for y in (-1.0, -0.5, 0.0, 0.5):
        t = top_of(torso, y)
        for x in (-0.32, 0.32):
            beam(m, "Accent", (x, y, t - 0.1), (x * 1.8 + rng.uniform(-0.1, 0.1), y - 0.75, t + rng.uniform(0.7, 1.1)), 0.2, 0.08, 0.04)
    tail(m, (-1.2, 3.25, 0.7, 0.65), (-2.3, 3.6, 0.25, 0.25), 2)
    m.bone = "Tail2"
    for x in (-0.3, 0, 0.3):
        beam(m, "Accent", (x * 0.5, -2.0, 3.5), (x * 2.2, -3.4, 4.3 - abs(x)), 0.22, 0.08, 0.04)
    m.bone = "Spine"
    # Skeleton wings on the Wing bones, so they twitch as it runs.
    for side in (-1, 1):
        m.use("WingL" if side < 0 else "WingR", (side * 0.72, 0.35, 3.85))
        elbow, wrist = (side * 1.6, 0.1, 4.2), (side * 1.95, 0.4, 3.5)
        beam(m, "Body", (side * 0.6, 0.35, 3.85), elbow, 0.34, None, 0.24)
        m.block("Body", *elbow, 0.28, 0.28, 0.28)
        beam(m, "Body", elbow, wrist, 0.24, None, 0.18)
        for k, off in enumerate((-0.25, 0.05, 0.35)):
            limb(m, "Bone", [wrist, (wrist[0] + side * 0.2, wrist[1] + off, wrist[2] - 0.55), (wrist[0] + side * 0.15, wrist[1] + off * 1.4 + 0.15, wrist[2] - 1.0 - k * 0.15)], 0.1, 0.03)
        for t in (0.2, 0.5, 0.8):
            p = [elbow[i] + (wrist[i] - elbow[i]) * t for i in range(3)]
            beam(m, "Accent", p, (p[0] + side * 0.1, p[1] - 0.2, p[2] - 0.75 - t * 0.3), 0.18, 0.06, 0.03)
    m.use("Neck", (0, 0.75, 3.95))
    m.loft_z("Body", (3.75, 0, 0.75, 0.85, 0.9), (4.6, 0, 1.0, 0.7, 0.75))
    m.stretch("Body", "Spine")
    m.loft_z("Body", (4.6, 0, 1.0, 0.7, 0.75), (5.4, 0, 1.2, 0.66, 0.7))
    for k in range(9):  # the ruff of quills round the bottom of its neck
        a = -math.pi * 0.95 + k * math.pi * 1.9 / 8
        base = (math.cos(a) * 0.38, 0.8 + math.sin(a) * 0.35, 4.05)
        beam(m, "Accent", base, (math.cos(a) * 1.05, 0.8 + math.sin(a) * 0.95 - 0.25, 4.4 + rng.uniform(-0.1, 0.25)), 0.2, 0.07, 0.03)
    w, d, h = 1.1, 1.2, 1.05
    yc, zc = 1.5, 5.85
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)

    def beard(m, front, mouth_z, gap, lower_length):
        for x, y, length in ((-0.15, front + 0.4, 0.9), (0.12, front + 0.75, 0.7), (0.0, front + 1.05, 0.55)):
            moss_beard(m, x, y, mouth_z - gap / 2 - 0.2, length, 0.26)

    mouth_z, gap, upper_h = zc - 0.2, 0.42, 0.5
    snout = maw(m, front, mouth_z, 0.8, 1.8, 0.46, upper_h, 0.26, gap, rng, upper="Beak", lower="Beak", tooth=0.15, per_side=5,
                front_row=0, crooked=0.3, skull_d=d, on_jaw=beard)
    tip = snout["tip"]
    upper_z = mouth_z + gap / 2 + upper_h / 2
    beam(m, "Beak", (0, tip - 0.2, upper_z), (0, tip + 0.3, mouth_z - gap / 2 - 0.45), 0.4, 0.5, 0.06)  # the hook
    m.block("BeakDark", 0, front + 0.65, snout["top"](front + 0.65) + 0.02, 0.36, 1.0, 0.06)
    for side in (-1, 1):  # five eyes: a big pair, a smaller pair behind, and a tiny one on the right
        glow_eye(m, side * w / 2, yc + 0.32, zc + 0.12, 0.44, side, facing="side", slant=1.0)
        glow_eye(m, side * w / 2, yc - 0.28, zc + 0.3, 0.28, side, facing="side", brow=False)
    glow_eye(m, w / 2, yc + 0.05, zc - 0.25, 0.2, 1, facing="side", brow=False)
    for x in (-0.25, 0, 0.25):  # a crest of quills sweeping back
        beam(m, "Accent", (x, yc + 0.2, zc + h / 2 - 0.05), (x * 1.6, yc - 1.1, zc + h / 2 + 0.85 - abs(x)), 0.22, 0.08, 0.03)
    m.head_centre = (0, front + 0.4, zc)
    return m


# ---------------------------------------------------------------------- the fierce ones


def pitch_raptor():
    """A raptor of wet black pitch whose face splits four ways: jaws top and bottom and a pincer on each side,
    all glowing inside. Six spider eyes, bone spikes down its back, mantis scythes of bone instead of hands
    and a bone blade on the end of its tail."""
    m = monster("dino_PitchRaptor", Body="#1c1727", Accent="#463a5e", Belly="#2f2740", Claw="#ece4d0", Bone=BONE, Gloss=GLOSS)
    rng = random.Random(4)
    m.joint("Spine", (0, -0.55, 2.7))
    biped_legs(m, 0.55, -0.55, 2.2, 0.88, 1.0, 0.34, 1.05, 0.26)
    for side in (-1, 1):
        m.bone = "ShinL" if side < 0 else "ShinR"
        m.loft_y("Claw", (-0.2, side * 0.55, 0.5, 0.18, 0.28), (0.2, side * 0.55, 1.1, 0.04, 0.04))
    m.bone = "Spine"
    body = ((-1.6, 0, 2.55, 1.0, 1.0), (0.85, 0, 2.95, 1.45, 1.55))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-0.8, 0, 2.2, 0.95, 0.5), (0.9, 0, 2.48, 1.2, 0.75))
    for y in (-1.2, -0.6, 0.0, 0.6):  # wet shine down its flanks
        r = ring_at(*body, y)
        for side in (-1, 1):
            beam(m, "Gloss", (side * (r[3] / 2 + 0.02), y + 0.12, r[2] + r[4] * 0.42), (side * (r[3] / 2 + 0.02), y - 0.1, r[2] - r[4] * 0.1), 0.05, 0.14)
    for y, height in ((0.55, 0.85), (-0.15, 1.05), (-0.85, 0.95), (-1.45, 0.7)):
        prism(m, "Bone", 0, y, top_of(body, y) - 0.1, top_of(body, y) + height, 0.22, 0.03, 4, math.pi / 4, (0, -0.4 * height))
    tail(m, (-1.55, 2.58, 0.85, 0.8), (-4.8, 3.0, 0.14, 0.14), 3)
    for bone, y, z, height in (("Tail1", -2.4, 2.95, 0.55), ("Tail2", -3.4, 3.05, 0.4)):
        m.bone = bone
        prism(m, "Bone", 0, y, z - 0.05, z + height, 0.15, 0.03, 4, math.pi / 4, (0, -0.35 * height))
    m.bone = "Tail3"  # the blade
    m.loft_y("Bone", (-4.6, 0, 3.0, 0.14, 0.5), (-5.7, 0, 3.65, 0.04, 0.12))
    m.loft_y("Bone", (-4.7, 0, 2.9, 0.12, 0.3), (-5.3, 0, 2.45, 0.03, 0.05))
    m.bone = "Spine"
    for side in (-1, 1):  # mantis scythes
        x = side * 0.78
        m.use("ArmL" if side < 0 else "ArmR", (x, 0.6, 2.85))
        m.loft_y("Body", (0.6, x, 2.85, 0.28, 0.32), (1.3, x, 2.45, 0.22, 0.24))
        limb(m, "Bone", [(x, 1.3, 2.45), (x + side * 0.05, 1.75, 2.95), (x + side * 0.05, 1.85, 3.5), (x, 1.55, 3.75)], 0.16, 0.03)
        for k in range(3):
            y, z = 1.42 + k * 0.14, 2.6 + k * 0.28
            m.loft_y("Bone", (y, x, z, 0.06, 0.08), (y + 0.16, x, z - 0.1, 0.02, 0.02))
    m.use("Neck", (0, 1.0, 3.35))
    m.loft_z("Body", (3.35, 0, 1.0, 1.0, 1.05), (4.2, 0, 1.35, 0.78, 0.82))
    m.stretch("Body", "Spine")
    w, d, h = 1.45, 1.5, 1.4
    yc, zc = 1.6, 4.68
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    mouth_z = zc - 0.45
    maw(m, front, mouth_z, w, 1.15, 1.0, 0.38, 0.26, 0.44, rng, tooth=0.21, per_side=4, front_row=3, crooked=0.4, grin=0.3,
        skull_d=d, drips=((-0.4, 0.45), (0.5, 0.3)))
    # The pincers either side of the mouth, on the Wing bones: they flex open as it runs.
    for side in (-1, 1):
        m.use("WingL" if side < 0 else "WingR", (side * 0.62, front, mouth_z + 0.25), "Head")
        x0, x1, reach = side * 0.68, side * 1.05, 1.25
        m.loft_y("Accent", (front - 0.15, x0, mouth_z - 0.08, 0.2, 0.82), (front + reach, x1, mouth_z - 0.15, 0.12, 0.42))
        m.loft_y("Glow", (front, x0 - side * 0.1, mouth_z - 0.08, 0.03, 0.56), (front + reach - 0.1, x1 - side * 0.065, mouth_z - 0.15, 0.03, 0.26))
        m.loft_x("Bone", (x1, front + reach - 0.05, mouth_z - 0.15, 0.2, 0.28), (x1 - side * 0.55, front + reach + 0.25, mouth_z - 0.25, 0.03, 0.03))
        for t in (0.12, 0.36, 0.6, 0.82):
            y = front + t * reach
            x = x0 + (x1 - x0) * t - side * 0.08
            m.loft_x("Teeth", (x, y, mouth_z - 0.12, 0.13, 0.17), (x - side * 0.26, y + 0.04, mouth_z - 0.15, 0.02, 0.02))
    m.bone = "Head"
    for side in (-1, 1):  # six spider eyes
        glow_eye(m, side * 0.4, front, zc + 0.42, 0.34, side, slant=1.2)
        glow_eye(m, side * 0.13, front, zc + 0.58, 0.18, side, brow=False)
        glow_eye(m, side * w / 2, yc + 0.35, zc + 0.3, 0.24, side, facing="side", brow=False)
    m.head_centre = (0, front + 0.35, zc)
    return m


def tar_titan():
    """A hunched giant with no neck at all: its whole front is one mouth, a cave of gravestone teeth glowing
    violet inside, with a row of seven eyes glaring over it. Ribs burst out of its back like the skeletons
    sinking in the bog, curled round a wisp it caught; long arms drag bone claws along the ground, and moss
    and tar hang off everything."""
    m = monster("dino_TarTitan", Body="#2a2236", Accent="#120e18", Belly="#443855", Claw="#ece4d0", Bone=BONE,
                BoneShade=BONE_SHADE, Moss=MOSS, MossDark=MOSS_DARK, Gloss=GLOSS)
    rng = random.Random(5)
    m.joint("Spine", (0, -0.3, 3.2))
    biped_legs(m, 1.15, -0.3, 2.9, 1.55, 1.7, 0.95, 1.7, 0.42)
    m.loft_y("Body", (-1.5, 0, 3.6, 3.0, 2.6), (1.2, 0, 3.75, 3.4, 2.8))
    m.loft_y("Belly", (-0.8, 0, 3.1, 2.6, 1.0), (1.35, 0, 3.3, 3.0, 1.4))
    for x, length in ((-1.2, 0.6), (-0.3, 0.85), (0.7, 0.55), (1.35, 0.7)):
        icicle(m, "Accent", x, 1.0, 2.55, length, 0.32)
    tail(m, (-1.4, 3.4, 1.4, 1.2), (-3.4, 2.2, 0.5, 0.4), 2)

    # The head is the whole upper body: no neck, one mouth across its front.
    w, d, h = 3.9, 3.1, 2.7
    yc, zc = 0.25, 6.2
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    m.loft_y("Body", (-1.55, 0, 6.5, 3.5, 2.3), (-0.4, 0, 7.15, 3.7, 2.4))  # the hunch

    def beard(m, front, mouth_z, gap, lower_length):
        for x, y, length in ((-1.3, front + 0.3, 1.2), (-0.5, front + 0.6, 1.5), (0.45, front + 0.45, 1.1), (1.25, front + 0.25, 1.35)):
            moss_beard(m, x, y, mouth_z - gap / 2 - 0.75, length, 0.38, "Moss" if x < 0 else "MossDark")

    mouth_z = 5.55
    maw(m, front, mouth_z, w, 0.9, 3.6, 0.8, 0.75, 0.95, rng, tooth=0.5, per_side=3, front_row=6, crooked=0.35, gravestones=True,
        grin=0.55, skull_d=d, drips=((-0.85, 0.9), (-0.2, 1.3), (0.55, 0.8), (0.95, 1.1)), on_jaw=beard)
    # Seven eyes in a row over the mouth, the middle pair biggest.
    for x, size, dz in ((-1.58, 0.32, 0.02), (-1.08, 0.4, 0.06), (-0.5, 0.5, 0.0), (0.5, 0.5, 0.0), (1.08, 0.38, 0.08), (1.58, 0.3, -0.02)):
        glow_eye(m, x, front, 7.18 + dz, size, -1 if x < 0 else 1, slant=1.1, wide=1.1)
    glow_eye(m, 0, front, 7.42, 0.22, 1, brow=False)
    # Ribs bursting out of its back, curled round a wisp it caught.
    for y in (0.4, -0.35, -1.1):
        for side in (-1, 1):
            limb(m, "Bone", [(side * 1.15, y, 7.4), (side * 1.85, y - 0.35, 8.5), (side * 1.55, y - 0.8, 9.45), (side * 0.75, y - 0.9, 9.9)], 0.36, 0.1)
    for y in (0.7, -0.05, -0.8, -1.5):
        prism(m, "Bone", 0, y, 7.45, 8.0, 0.24, 0.04, 4, math.pi / 4, (0, -0.25))
    wisp(m, 0, -0.35, 8.55, 0.55)
    for side in (-1, 1):  # moss draped over its shoulders
        for y, length in ((0.9, 1.2), (-0.1, 1.5)):
            moss_beard(m, side * (w / 2 + 0.05), y, zc + 0.9, length, 0.42)
    m.block("Gloss", -0.9, -0.2, zc + h / 2 + 0.02, 0.9, 0.3, 0.06)

    # Long arms on the head (it is the shoulders), dragging bone claws.
    for side in (-1, 1):
        sx = side * 2.15
        m.use("ArmL" if side < 0 else "ArmR", (sx, 0.3, 6.4), "Head")
        m.block("Body", sx, 0.25, 6.45, 1.3, 1.45, 1.35)
        beam(m, "Body", (sx, 0.3, 6.4), (sx + side * 0.35, 1.0, 2.9), 1.0, None, 1.15)
        hand = (sx + side * 0.35, 1.15, 2.25)
        m.block("Body", *hand, 1.35, 1.45, 1.15)
        for offset in (-0.45, 0, 0.45):
            m.loft_z("Claw", (0.2, hand[0] + offset, hand[1] + 0.95, 0.05, 0.05), (hand[2] - 0.2, hand[0] + offset, hand[1] + 0.45, 0.34, 0.4))
        moss_beard(m, sx + side * 0.6, 0.6, 5.1, 1.3, 0.36)
        icicle(m, "Accent", hand[0] - side * 0.3, hand[1] - 0.3, hand[2] - 0.5, 0.7, 0.26)
    m.bone = "Head"
    m.head_centre = (0, front + 0.6, 6.4)
    return m


def bog_rex():
    """Shadow Bog's boss: a tar rex with three heads. The middle one is a bare skull, its third eye open on
    the brow; a cyclops head and a three-eyed head snarl on necks from its shoulders. Its rib cage stands open
    with a wisp glowing inside, its tail is a row of bone, moss hangs off its shoulders, tar off all three
    jaws, and it wears a crown of roots hung with glowing pods."""
    m = monster("dino_BogRex", Body="#211b2e", Accent="#ece4d0", Belly="#3a3050", Claw="#141019", BoneShade=BONE_SHADE,
                Socket=SOCKET, Moss=MOSS, MossDark=MOSS_DARK, Roots="#4a3e52", RootsDark="#30283a", Gloss=GLOSS)
    rng = random.Random(6)
    m.joint("Spine", (0, -0.8, 4.4))
    biped_legs(m, 0.95, -0.8, 3.9, 1.6, 1.8, 0.75, 1.95, 0.42)
    torso = ((-2.4, 0, 4.2, 1.9, 2.0), (1.4, 0, 5.0, 2.9, 3.1))
    m.loft_y("Body", *torso)
    m.loft_y("Belly", (-1.1, 0, 3.55, 1.85, 0.85), (1.2, 0, 4.0, 2.2, 1.2))
    # The open rib cage on its chest, a wisp glowing inside it.
    chest = torso[1][0]
    m.block("Socket", 0, chest + 0.02, 5.0, 1.7, 0.1, 2.0)
    m.block("Glow", 0, chest + 0.05, 5.0, 1.0, 0.06, 1.2)
    m.block("Wisp", 0, chest + 0.08, 5.05, 0.42, 0.04, 0.5)
    for z in (4.25, 4.7, 5.15, 5.6):
        m.block("Accent", 0, chest + 0.12, z, 2.0, 0.18, 0.2)
    m.block("Accent", 0, chest + 0.14, 4.95, 0.24, 0.2, 1.9)
    for side in (-1, 1):  # ribs showing through the tar on its flanks
        for y in (-1.6, -0.9, -0.2, 0.5):
            r = ring_at(*torso, y)
            x = side * (r[3] / 2 + 0.02)
            beam(m, "Accent", (side * r[3] * 0.3, y, r[2] + r[4] / 2 + 0.02), (x, y + 0.1, r[2] + r[4] * 0.15), 0.16, 0.22)
            beam(m, "Accent", (x, y + 0.1, r[2] + r[4] * 0.15), (side * r[3] * 0.38, y + 0.3, r[2] - r[4] / 2 + 0.05), 0.16, 0.22, 0.12)
        moss_beard(m, side * 1.25, 1.0, 6.3, 1.6, 0.45, "Moss")
        moss_beard(m, side * 1.05, -0.4, 5.9, 1.2, 0.4, "MossDark")
    for y, height in ((0.9, 1.1), (0.0, 1.45), (-0.9, 1.3), (-1.8, 1.0)):  # vertebrae down the back
        prism(m, "Accent", 0, y, top_of(torso, y) - 0.2, top_of(torso, y) + height, 0.34, 0.04, 4, math.pi / 4, (0, -0.3 * height))
    tail(m, (-2.3, 4.25, 1.7, 1.7), (-7.2, 4.8, 0.2, 0.2), 3)
    for bone, y, z, height in (("Tail1", -3.0, 5.1, 1.0), ("Tail2", -4.3, 5.1, 0.8), ("Tail3", -5.6, 5.0, 0.55)):
        m.bone = bone
        prism(m, "Accent", 0, y, z - 0.25, z + height, 0.28, 0.03, 4, math.pi / 4, (0, -0.3 * height))
        for side in (-1, 1):
            beam(m, "Accent", (0, y, z - 0.35), (side * (0.3 + 0.35 * height), y + 0.15, z - 0.9), 0.14, 0.18, 0.06)
    m.bone = "Spine"
    for side in (-1, 1):
        m.use("ArmL" if side < 0 else "ArmR", (side * 1.4, 1.2, 4.6))
        m.loft_y("Body", (1, side * 1.4, 4.6, 0.36, 0.38), (1.8, side * 1.4, 4.2, 0.26, 0.26))
        for offset in (-0.08, 0.08):
            m.loft_y("Claw", (1.76, side * 1.4 + offset, 4.17, 0.09, 0.11), (2.1, side * 1.4 + offset, 4.0, 0.03, 0.03))

    # The side heads, on necks from its shoulders (the Wing bones, so they sway as it walks).
    for side in (-1, 1):
        m.use("WingL" if side < 0 else "WingR", (side * 1.25, 1.0, 5.9))
        cx = side * 3.5
        limb(m, "Body", [(side * 1.25, 1.0, 5.9), (side * 2.4, 1.5, 6.95), (cx, 2.4, 7.4)], 1.05, 0.8)
        hw, hd, hh = 1.45, 1.45, 1.25
        hy, hz = 2.95, 7.55
        m.block("Body", cx, hy, hz, hw, hd, hh)
        hfront = hy + hd / 2
        maw(m, hfront, hz - 0.35, hw, 1.05, 1.15, 0.34, 0.3, 0.55, rng, cx=cx, tooth=0.24, per_side=3, front_row=3, crooked=0.45,
            jaw=False, skull_d=hd, drips=((-0.3, 0.7), (0.4, 0.45)), drip_role="Body")
        if side < 0:  # the cyclops
            glow_eye(m, cx, hfront, hz + 0.3, 0.72, 1, slant=1.2, brow="v", wide=1.05)
        else:  # three eyes in a triangle
            glow_eye(m, cx - 0.36, hfront, hz + 0.22, 0.36, -1, slant=1.0)
            glow_eye(m, cx + 0.36, hfront, hz + 0.22, 0.36, 1, slant=1.0)
            glow_eye(m, cx, hfront, hz + 0.5, 0.26, 1, brow=False)
        for dx, height in ((-0.35, 0.65), (0.3, 0.85)):
            prism(m, "Accent", cx + dx, hy - 0.1, hz + hh / 2 - 0.1, hz + hh / 2 + height, 0.2, 0.03, 4, math.pi / 4, (side * 0.2, -0.25))

    m.bone = "Spine"
    m.use("Neck", (0, 1.5, 5.9))
    m.loft_z("Body", (5.9, 0, 1.5, 2.1, 2.2), (6.65, 0, 1.95, 1.85, 1.85))
    m.stretch("Body", "Spine")
    w, d, h = 2.6, 2.6, 1.9
    yc, zc = 2.9, 7.3
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    # The middle head's bare skull over the tar: a bone mask with deep sockets.
    m.block("Accent", 0, yc + 0.45, zc + 0.35, w + 0.1, d * 0.72, h * 0.72)
    for side in (-1, 1):
        m.block("Socket", side * 0.72, front + 0.06, zc + 0.66, 1.05, 0.1, 0.78)
        glow_eye(m, side * 0.72, front + 0.12, zc + 0.66, 0.7, side, slant=1.1, brow_role="BoneShade", wide=1.15)
    m.block("Socket", 0, front + 0.06, zc + 0.9, 0.36, 0.1, 0.32)
    glow_eye(m, 0, front + 0.12, zc + 0.9, 0.26, 1, brow=False)  # the third eye

    def beard(m, front, mouth_z, gap, lower_length):
        for x, y, length in ((-0.7, front + 0.5, 1.3), (0.1, front + 0.9, 1.6), (0.75, front + 0.6, 1.1)):
            moss_beard(m, x, y, mouth_z - gap / 2 - 0.45, length, 0.36, "Moss" if x < 0.5 else "MossDark")

    mouth_z = zc - 0.62
    snout = maw(m, front, mouth_z, w, 2.0, 2.1, 0.6, 0.48, 0.66, rng, upper="Accent", lower="Accent", tooth=0.36, per_side=5,
                front_row=4, crooked=0.3, grin=0.42, skull_d=d, drips=((-0.75, 0.8), (-0.1, 1.2), (0.6, 0.9)), drip_role="Body",
                on_jaw=beard)
    for y in (front + 0.5, front + 1.2):  # nostril holes in the bone
        for side in (-1, 1):
            m.block("Socket", side * 0.38, y, snout["top"](y) + 0.02, 0.24, 0.3, 0.06)
    for p, q in (((0.9, front - 0.2, zc + 1.03), (0.35, front - 0.9, zc + 1.03)), ((0.35, front - 0.9, zc + 1.03), (0.6, front - 1.5, zc + 1.03))):
        beam(m, "BoneShade", p, q, 0.12, 0.05)
    # The crown of roots, hung with glowing pods.
    top = zc + h / 2
    for side in (-1, 1):
        base = (side * 0.65, yc - 0.4, top)
        knee = (side * 1.35, yc - 0.7, top + 1.0)
        limb(m, "Roots", [base, knee, (side * 1.5, yc - 1.3, top + 1.95), (side * 2.15, yc - 1.55, top + 2.45)], 0.42, 0.1)
        limb(m, "Roots", [knee, (side * 2.15, yc - 0.3, top + 1.5), (side * 2.6, yc + 0.1, top + 1.55)], 0.26, 0.08)
        limb(m, "RootsDark", [(side * 0.3, yc - 0.9, top), (side * 0.45, yc - 1.4, top + 0.95), (side * 0.25, yc - 1.9, top + 1.5)], 0.3, 0.08)
        pod(m, side * 2.45, yc + 0.05, top + 1.5, 0.45)
        pod(m, side * 1.7, yc - 1.35, top + 2.1, 0.6)
    m.head_centre = (0, front + 0.6, zc)
    return m


def main():
    models = [sticky_steve(), slow_bob(), terror_bird(), pitch_raptor(), tar_titan(), bog_rex()]
    build_and_render(models, RENDERS, HERE / "shadow_bog_monsters.blend", "shadow_bog_animation_preview.mp4",
                     sky=SKY, ground=FLOOR, glow_roles=GLOW_ROLES, spacing=18)


if __name__ == "__main__":
    main()
