"""Builds Midnight Carnival's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_midnight_carnival_monsters.py
    QUICK=1 Blender -b -P build_midnight_carnival_monsters.py    (stills only, into QUICK_OUT, for trying faces)
    ONLY=jack_snap,grinmaster QUICK=1 ...                         (just those)

Saves midnight_carnival_monsters.blend and renders to design/world/monsters_midnight_carnival/. The map's props
are in build_midnight_carnival.py.

Map 11, a haunted fair at midnight. The owner asked for monsters that suit the biome and are scary and aggressive
at the same time: the fair's own attractions come alive, all teeth. They share the carnival face: chalk-white
greasepaint, black harlequin diamonds over glowing neon-pink eyes with pinprick pupils, and a crimson painted grin
stretching the real mouth, full of needle teeth, far up the cheeks. The common ones have it in a white eye; the
fierce ones have no white at all, just the neon glow in a black socket. The map's colours: crimson and cream
stripes, teal, gold, plum, warm bulbs and pink neon.

  Jack Snap        a jack-in-the-box out walking on stubby legs: its clown head bounces on a spring neck, needle
                   teeth, a red nose, purple hair and a little cone hat with a bulb on top
  Popcorn Fiend    a striped popcorn box whose whole top half is a jaw: jagged kernel teeth, warm light inside,
                   popcorn heaped on its head like hair, butter running down, grabby little arms
  Twisty           a balloon-animal dog gone wrong: twisted pink balloons, devil-horn ears, glowing eyes and a
                   mouth far too full of teeth, its string trailing from the knot of its tail
  Nightmare Mare   a carousel horse that came off its ride, the brass pole still through its back: cracked white
                   paint, a gilded saddle, a mane and tail of pink neon, painted diamonds round its eyes, and fangs
  Grinmaster       the ringmaster: a towering thing in a crimson tailcoat and top hat, a long chalk face split by a
                   huge grin, a curled moustache, one clawed glove reaching for you and a whip cracking overhead
  Big Top Terror   the boss: an elephant-legged beast carrying the whole big top on its back, bulbs round its
                   valance and a pennant on top, a ruff round its neck, a giant clown head with a crown of bulbs
                   and a mouth of fangs, and long arms reaching out from under the ruff

All have a Jaw bone (they snap as they walk and roar once per idle in the game, DinoLifeController), always in front
of the Spine, since the game tells which way a monster faces from it; Jack Snap's head bounces on its Neck spring
and the boss's arms ride the Wing bones. Glowing parts are EyeGlow, Bulb, Neon and Lamp (Neon in the game,
shared/Roles.luau, all there already). Skin roles Body, Accent, Belly and Claw take the colour mutations; the face
paint, gold, stripes, hats and coats keep their colour. Built at the first map's size; the game scales them by
Config/Biomes standardScale. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0.

Polished 2026-11-12 (the owner turned down a full redesign, build_midnight_carnival_fright.py: "i want their old designs ... all i
wanted was an improvement for their flaws"): round eyes with a shine instead of square ones, the scowl eased a little, the painted grin
kept on the face, rounder balls and balloons, Grinmaster's whip over and behind its head instead of through its face.

No stud texture in this file (kit.PREVIEW_STUDS off): plain colours, and the studs come only from Studio's shared
"Studs" material.
"""
import math
import os
import random
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_desert import beam, quad_legs  # noqa: E402
from build_eclipse_temple_monsters import at, face_box, feather, grow, round_slab  # noqa: E402
from build_forbidden_library import tube  # noqa: E402
from build_forest import Model, biped_legs, tail  # noqa: E402
from build_starfall_crater import ball as chunky_ball, flat_ring, gem  # noqa: E402
from build_volcano import prism, top_of  # noqa: E402
from face_kit import classic_mouth, icicle, top_nostrils  # noqa: E402
from map_kit import limb, plate  # noqa: E402
from monster_stage import build_and_render, light_up, set_sky  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_midnight_carnival"
BLEND = "midnight_carnival_monsters"  # for check_map.py and export_fbx.py

GLOW_ROLES = {"EyeGlow", "Bulb", "Neon", "Lamp"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket", "Makeup", "Paint"})
GLOW = 1.8

# The map's colours (build_midnight_carnival.py) and the carnival face.
CRIMSON, CRIMSON_DARK, CREAM = "#b3263a", "#7e1a2a", "#f2e6cc"
GOLD, GOLD_DARK = "#e9b23a", "#a9761f"
TEAL, PLUM = "#2f9a94", "#4b2b5f"
NEON, BULB, LAMP = "#ff4f9a", "#ffe7a3", "#ffc96b"
HAIR = "#7a3fc0"
POPCORN, BUTTER = "#fff2c8", "#f4cf5a"
ROPE = "#d9c9a3"
FACE = {"Pupil": "#0c0a12", "Socket": "#0c0a12", "EyeGlow": NEON, "EyeWhite": "#fbf6ec", "Mouth": "#2a0c18", "Teeth": "#fffaf0",
        "Tongue": "#e0465f", "Trim": GOLD, "TrimDark": GOLD_DARK, "Makeup": "#160c1e", "Paint": "#d01f3c", "Face": "#f4ede0",
        "Nose": "#e8213c", "Bulb": BULB, "Neon": NEON, "Hair": HAIR, "Glove": "#f6f2ea"}
SKY, FLOOR = "#161230", "#2b6c72"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


def ball(m, role, x, y, z, r, sides=8, rings=5):
    """starfall's chunky ball, rounder (2026-11-12 polish: the 6-sided balls read as rough lumps)."""
    chunky_ball(m, role, x, y, z, r, max(sides * 2, 12), max(rings * 2, 8))


# ---------------------------------------------------------------------- the carnival face


def rhombus(m, role, centre, normal, w, h, depth):
    """A diamond lying flat on a face that looks along normal ("y", "+x" or "-x"): w across, h tall."""
    cx, cy, cz = centre
    verts = []
    for k in (-depth / 2, depth / 2):
        for u, v in ((w / 2, 0), (0, h / 2), (-w / 2, 0), (0, -h / 2)):
            verts.append((cx + u, cy + k, cz + v) if normal == "y" else (cx + k, cy + u, cz + v))
    m._add(role, verts, [[3, 2, 1, 0], [4, 5, 6, 7]] + [[i, (i + 1) % 4, 4 + (i + 1) % 4, 4 + i] for i in range(4)])


def neon_eye(m, origin, normal, size, inner=1, white=True, look=(0.0, 0.0), lid=0.0, slant=0.0, brow=None, lid_role="Face",
             brow_role="Makeup", diamond=True):
    """One carnival eye on a face at origin (its middle, on the surface); inner (+1/-1) is the way to the nose along u.
    A black harlequin diamond painted round it (diamond), a white eye or a black socket (far fiercer), a glowing
    neon-pink iris with a pinprick pupil, and a lid and brow slanting down towards the nose (slant: angry)."""
    if diamond:
        rhombus(m, "Makeup", at(origin, normal, 0, 0, -0.005), normal, size * 1.55, size * 1.9, 0.09)
    w, h = size * 1.0, size * 0.95
    # 2026-11-12 polish: round eyes (the square whites and square pupils looked odd), a shine, the scowl eased a little.
    # Every layer's front 0.04 in front of the one under it (diamond 0.04, white 0.09, iris 0.13, pupil 0.17, shine 0.21, lid 0.25,
    # brow 0.29), and every layer's back sunk into the head at its own depth, so no two faces ever lie flat against each other:
    # export_fbx's flicker lift pushes such pairs apart, one after another up the stack, and scattered the eye in game (2026-11-12).
    round_slab(m, "EyeWhite" if white else "Socket", at(origin, normal, 0, 0, 0.02), normal, size * 0.5, 0.14, 18)
    c = at(origin, normal, look[0] * w * 0.28, look[1] * h * 0.28, 0.0)
    round_slab(m, "EyeGlow", at(c, normal, 0, 0, 0.035), normal, size * 0.33, 0.19, 16)
    round_slab(m, "Pupil", at(c, normal, 0, 0, 0.05), normal, size * 0.13, 0.24, 12)
    round_slab(m, "EyeWhite", at(c, normal, inner * -size * 0.12, size * 0.12, 0.065), normal, size * 0.07, 0.29, 8)
    top = h / 2 + size * 0.04
    dz = slant * 0.7 * size * 0.3

    def tilted(role, bottom, thick_top, depth, n):
        outer = at(origin, normal, -inner * (w / 2 + size * 0.14), 0, n)  # well past the eye's edge, not flush with it
        inner_p = at(origin, normal, inner * (w / 2 + size * 0.14), 0, n)
        bo, bi = bottom + dz, bottom - dz
        to, ti = thick_top + dz * 0.5, thick_top - dz * 0.5
        if normal == "y":
            m.loft_x(role, (outer[0], outer[1], outer[2] + (bo + to) / 2, depth, to - bo),
                     (inner_p[0], inner_p[1], inner_p[2] + (bi + ti) / 2, depth, ti - bi))
        else:
            m.loft_y(role, (outer[1], outer[0], outer[2] + (bo + to) / 2, depth, to - bo),
                     (inner_p[1], inner_p[0], inner_p[2] + (bi + ti) / 2, depth, ti - bi))

    if lid > 0:
        tilted(lid_role, top - h * lid - size * 0.04, top + size * 0.02, 0.35, 0.075)
    if brow is not None:
        tilted(brow_role, top + brow * size, top + brow * size + size * 0.24, 0.4, 0.09)


def painted_grin(m, front, mouth_z, half, rise, reach=0.25, stroke=0.11, edge=None, start=0.0):
    """Crimson greasepaint carrying the mouth's corners up the cheeks, on a face looking +Y at y = front. edge: half the face's
    width; the stroke stops inside it (2026-11-12 polish: it stuck out into the air past the cheek)."""
    if edge:
        half = min(half, edge - stroke * 1.6)
        reach = max(0.0, min(reach, edge - stroke * 0.8 - half))
    for side in (-1, 1):
        a = (side * half, front + 0.02, mouth_z + start)  # start: above the lips, clear of the side teeth
        b = (side * (half + reach), front + 0.02, mouth_z + rise)
        beam(m, "Paint", a, b, 0.06, stroke)
        m.block("Paint", *b, stroke * 1.2, 0.06, stroke * 1.2)


def fang_row(m, xs, y, edge, length, width, down):
    """A row of needle teeth across the front of a jaw, from its edge at z = edge, pointing down or up."""
    for x in xs:  # each root sunk 0.08 into the jaw: a root lying flat on it was pushed off at export (2026-11-12)
        if down:
            m.loft_z("Teeth", (edge - length, x, y, 0.03, 0.03), (edge + 0.08, x, y, width * (1 + 0.08 / length), width * (1 + 0.08 / length)))
        else:
            m.loft_z("Teeth", (edge - 0.08, x, y, width * (1 + 0.08 / length), width * (1 + 0.08 / length)), (edge + length, x, y, 0.03, 0.03))


def ankles(m, legs, width, role="Belly"):
    """quad_legs leaves thin legs (width under ~1) standing 0.17 above their foot pads: a short ankle joins them (2026-11-12)."""
    for name, x, y in legs:
        m.bone = name
        m.block(role, x, y, 0.22, width * 0.66, width * 0.66, 0.26)
    m.bone = "Spine"


def coil(m, role, x, y, z0, z1, r, wire, turns):
    """A steel spring from z0 up to z1, one wire wound round (x, y), joined end to end (2026-11-12: the old stack of loose rings
    left the head floating over the box)."""
    n = int(turns * 16)
    pts = [(x + r * math.cos(k / 16 * math.tau), y + r * math.sin(k / 16 * math.tau), z0 + (z1 - z0) * k / n) for k in range(n + 1)]
    for a, b in zip(pts, pts[1:]):
        tube(m, role, a, b, wire, wire, 8)
    for p in pts[::4]:
        ball(m, role, *p, wire, 6, 3)


def sausage(m, role, a, b, r, sides=16):
    """A twisted balloon: a round tube with rounded ends."""
    tube(m, role, a, b, r, r, sides)
    ball(m, role, *a, r, sides, 4)
    ball(m, role, *b, r, sides, 4)


# ---------------------------------------------------------------------- the common ones


def jack_snap():
    """A jack-in-the-box out walking on four stubby legs, its lid hanging open behind, the crank on its side. Its
    clown head bounces on a coiled spring for a neck: chalk-white, glowing pink eyes in black diamonds, a grin of
    needle teeth painted further up its cheeks, a red nose, tufts of purple hair and a little cone hat with a bulb."""
    m = monster("dino_JackSnap", Body=CRIMSON, Accent=CRIMSON_DARK, Belly=CREAM, Claw="#2a1a22", Teal=TEAL, Spring="#c9c2d6")
    m.joint("Spine", (0, 0, 1.2))
    quad_legs(m, 0.72, 0.62, 0.72, -0.62, 1.05, 0.42)
    ankles(m, [("FrontL", -0.72, 0.62), ("FrontR", 0.72, 0.62), ("BackL", -0.72, -0.62), ("BackR", 0.72, -0.62)], 0.42)
    m.block("Body", 0, 0, 2.05, 2.1, 2.1, 1.9)
    for z in (1.12, 2.98):
        m.block("Trim", 0, 0, z, 2.22, 2.22, 0.16)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.block("Trim", sx * 1.02, sy * 1.02, 2.05, 0.2, 0.2, 1.8)
    for c, normal in (((0, 1.06, 2.05), "y"), ((0, -1.06, 2.05), "y"), ((1.06, 0, 2.05), "+x"), ((-1.06, 0, 2.05), "-x")):
        rhombus(m, "Teal", c, normal, 1.0, 1.3, 0.04)
    lid = Vector((0, -1.05, 3.06))
    rot = Vector((0, math.cos(-1.9), math.sin(-1.9)))  # the lid's far edge, hanging back and down
    beam(m, "Body", tuple(lid + Vector((0, 0, 0.04))), tuple(lid + rot * 2.1), 2.1, 0.16)
    beam(m, "Trim", (1.1, 0.2, 2.1), (1.5, 0.2, 2.1), 0.16)  # the crank
    beam(m, "Trim", (1.5, 0.2, 2.1), (1.5, 0.2, 1.55), 0.14)
    ball(m, "Belly", 1.62, 0.2, 1.5, 0.16, 6, 4)

    m.use("Neck", (0, 0.1, 3.0))
    coil(m, "Spring", 0, 0.1, 3.0, 4.2, 0.42, 0.07, 4.5)  # the spring, from the lid's rim up into the ruff
    w, d, h = 1.7, 1.45, 1.5
    yc, zc = 0.3, 5.0
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Face", 0, yc, zc, w, d, h)
    for k, (r, role) in enumerate(((1.15, "Teal"), (1.0, "Belly"))):  # a ruff under its chin
        prism(m, role, 0, yc - 0.05, zc - h / 2 - 0.2 + k * 0.12, zc - h / 2 + 0.02 + k * 0.12, r, r * 1.05, 12, k * 0.26)
    mouth_z, gap = zc - 0.33, 0.28

    def lower_fangs(m, front, mouth_z, gap, lower_length):
        fang_row(m, (-0.44, -0.22, 0.0, 0.22, 0.44), front + 0.9 * 0.38 + 0.05, mouth_z - gap / 2 - 0.02, 0.22, 0.15, False)

    classic_mouth(m, front, mouth_z, w, 0.38, 1.4, 0.22, 0.24, gap, upper="Face", lower="Face", tooth=0.17, per_side=4, lower_teeth=True,
                  tongue=True, skull_d=d, on_jaw=lower_fangs)
    fang_row(m, (-0.5, -0.3, -0.1, 0.1, 0.3, 0.5), front + 0.9 * 0.38 + 0.05, mouth_z + gap / 2 + 0.02, 0.24, 0.16, True)  # just past the dark mouth block, clear of the paint (2026-11-12)
    painted_grin(m, front, mouth_z, 0.72, 0.42, edge=w / 2)
    for side in (-1, 1):
        neon_eye(m, (side * 0.42, front, zc + 0.3), "y", 0.46, -side, white=True, lid=0.2, slant=1.0, brow=0.06)
        ball(m, "Hair", side * (w / 2 + 0.12), yc - 0.15, zc + 0.3, 0.42, 8, 5)
        ball(m, "Hair", side * (w / 2 + 0.05), yc - 0.35, zc - 0.1, 0.32, 8, 5)
    ball(m, "Nose", 0, front + 0.36, zc + 0.12, 0.22, 8, 5)
    prism(m, "Teal", 0.15, yc - 0.1, zc + h / 2 - 0.05, zc + h / 2 + 1.1, 0.5, 0.05, 16, 0, (0.35, -0.2))  # its cone hat
    ball(m, "Bulb", 0.5, yc - 0.3, zc + h / 2 + 1.15, 0.16, 6, 4)
    m.head_centre = (0, front + 0.2, zc + 0.1)
    return m


def popcorn_fiend():
    """A popcorn box that bites. Red and cream stripes; its whole top half is a jaw that lifts to show jagged
    kernel teeth and a warm light inside; angry eyes, popcorn heaped on its head like hair, butter running down
    its sides, stubby legs and grabby little arms."""
    m = monster("dino_PopcornFiend", Body=CRIMSON, Accent=CRIMSON_DARK, Belly=CREAM, Claw="#3a1a14", Popcorn=POPCORN, Butter=BUTTER,
                Teeth=POPCORN, Lamp=LAMP)
    rng = random.Random(2)
    m.joint("Spine", (0, 0, 1.0))
    biped_legs(m, 0.45, 0.0, 0.95, 0.5, 0.6, 0.34, 0.8, 0.22)

    def striped_box(z0, z1, w0, w1, d0, d1, front_stripes):
        """A tapering box of cream with red stripes up its faces."""
        m.loft_z("Belly", (z0, 0, 0, w0, d0), (z1, 0, 0, w1, d1))
        for s in (-1, 1):
            for u in ((-0.38, 0.38) if s > 0 and not front_stripes else (-0.38, 0.0, 0.38)):
                m.loft_z("Body", (z0 + 0.05, u * w0, s * (d0 / 2 + 0.03), 0.2 * w0, 0.06), (z1 - 0.05, u * w1, s * (d1 / 2 + 0.03), 0.2 * w1, 0.06))
            for u in (-0.38, 0.0, 0.38):  # (0.06 proud of the box and short of its ends: flush, and the flicker lift moved the box and everything on it)
                m.loft_z("Body", (z0 + 0.05, s * (w0 / 2 + 0.03), u * d0, 0.06, 0.2 * d0), (z1 - 0.05, s * (w1 / 2 + 0.03), u * d1, 0.06, 0.2 * d1))

    striped_box(0.85, 1.72, 1.6, 1.8, 1.4, 1.55, False)
    m.block("Mouth", 0, 0, 1.75, 1.6, 1.1, 0.08)  # front at 0.55, so the teeth fit between it and the box front
    m.block("Lamp", 0, -0.1, 1.78, 1.0, 0.8, 0.04)  # the warm light in its throat
    for side in (-1, 1):  # grabby arms
        m.use("ArmL" if side < 0 else "ArmR", (side * 0.85, 0.2, 1.5))
        beam(m, "Body", (side * 0.85, 0.2, 1.5), (side * 1.3, 0.75, 1.25), 0.28, None, 0.24)
        m.block("Belly", side * 1.35, 0.85, 1.25, 0.32, 0.32, 0.3)
        for off in (-0.09, 0.09):
            m.loft_y("Claw", (1.0, side * 1.35 + off, 1.25, 0.09, 0.09), (1.3, side * 1.38 + off, 1.18, 0.02, 0.02))
    m.bone = "Spine"
    m.use("Jaw", (0, 0.3, 1.72), "Spine")  # in front of the Spine: the game tells which way it faces from the Jaw
    fang_row(m, (-0.6, -0.3, 0.0, 0.3, 0.6), 0.62, 1.7, 0.3, 0.2, False)  # just inside the box's front, not flush with it
    fang_row(m, (-0.55, 0.55), 0.25, 1.7, 0.26, 0.18, False)
    m.bone = "Spine"
    m.use("Head", (0, 0.0, 1.85), "Spine")
    striped_box(1.85, 3.2, 1.82, 2.1, 1.57, 1.8, True)
    m.block("Trim", 0, 0, 3.17, 2.3, 2.0, 0.14)
    fang_row(m, (-0.75, -0.45, -0.15, 0.15, 0.45, 0.75), 0.62, 1.88, 0.34, 0.22, True)
    for x in (-0.75, 0.75):  # inside the box's sides, not flush with them
        fang_row(m, (x,), 0.2, 1.88, 0.3, 0.2, True)
    for side in (-1, 1):
        neon_eye(m, (side * 0.42, 0.93, 2.62), "y", 0.5, -side, white=True, lid=0.22, slant=1.1, brow=0.04, lid_role="Belly", diamond=False)  # on the stripes, not flush
    m.loft_z("Popcorn", (3.15, 0, 0, 2.0, 1.7), (3.55, 0, 0, 1.4, 1.1))
    heap = []
    for i in range(30):  # the heap of popcorn on its head
        for _ in range(60):  # a buttered kernel sits well into its neighbours or clear of them, never just touching (that flickers)
            x, y = rng.uniform(-0.95, 0.95), rng.uniform(-0.8, 0.8)
            z = 3.3 + rng.uniform(0.0, 0.5) * (1.2 - abs(x) * 0.5 - abs(y) * 0.5)
            r = rng.uniform(0.2, 0.3)
            if i % 5 or all((Vector((x, y, z)) - c).length < 0.7 * (r + q) or (Vector((x, y, z)) - c).length > r + q + 0.06 for c, q in heap):
                break
        heap.append((Vector((x, y, z)), r))
        ball(m, "Butter" if i % 5 == 0 else "Popcorn", x, y, z, r, 6, 4)
    for x, y, length in ((-1.0, 0.5, 0.6), (1.03, -0.3, 0.8), (0.4, 0.9, 0.5)):  # butter running down
        icicle(m, "Butter", x, y, 3.15, length, 0.18)
    m.head_centre = (0, 0.9, 2.5)
    return m


def twisty():
    """A balloon-animal dog gone wrong: twisted pink balloons, devil-horn ears, glowing eyes in black sockets and a
    mouth far too full of teeth, knots for feet and nose, and its string trailing from the knot of its tail."""
    m = monster("dino_Twisty", Body="#ff5fa8", Accent="#c2347a", Belly="#ff9cc9", Claw="#5a1238", Rope=ROPE)
    m.joint("Spine", (0, 0, 1.95))
    for end, y in (("Front", 0.85), ("Back", -0.85)):
        for side in (-1, 1):
            x = side * 0.45
            m.use(end + ("L" if side < 0 else "R"), (x, y, 1.9))
            sausage(m, "Body", (x, y, 1.75), (x, y + 0.05, 0.42), 0.3)
            ball(m, "Accent", x, y + 0.08, 0.16, 0.2, 6, 4)
            for off in (-0.12, 0.12):
                m.loft_y("Claw", (y + 0.2, x + off, 0.12, 0.08, 0.08), (y + 0.48, x + off, 0.06, 0.02, 0.02))
    m.bone = "Spine"
    sausage(m, "Body", (0, -0.95, 2.0), (0, 0.95, 2.1), 0.55)
    for y in (-0.95, 0.95):
        ball(m, "Accent", 0, y, 2.05 + 0.05 * (y > 0), 0.24, 6, 4)  # the twists
    m.use("Tail1", (0, -1.35, 2.15))
    sausage(m, "Body", (0, -1.4, 2.25), (0, -1.75, 2.9), 0.24)
    m.use("Tail2", (0, -1.75, 2.9), "Tail1")
    sausage(m, "Body", (0, -1.75, 2.9), (0, -1.8, 3.5), 0.2)
    m.use("Tail3", (0, -1.8, 3.5), "Tail2")
    ball(m, "Accent", 0, -1.82, 3.72, 0.2, 6, 4)
    limb(m, "Rope", [(0, -1.85, 3.6), (0.15, -2.2, 2.9), (-0.05, -2.45, 2.0), (0.1, -2.6, 1.0)], 0.06, 0.05)
    m.bone = "Spine"
    m.use("Neck", (0, 0.95, 2.2))
    sausage(m, "Body", (0, 1.05, 2.3), (0, 1.55, 3.1), 0.34)
    w, d, h = 1.1, 1.1, 1.0
    yc, zc = 1.85, 3.4
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    ball(m, "Body", 0, yc - 0.1, zc + 0.1, 0.72, 10, 6)
    mouth_z, gap = zc - 0.25, 0.2

    def lower_fangs(m, front, mouth_z, gap, lower_length):
        fang_row(m, (-0.24, -0.08, 0.08, 0.24), front + 0.9 * 0.7 + 0.05, mouth_z - gap / 2 - 0.02, 0.18, 0.12, False)

    classic_mouth(m, front, mouth_z, w, 0.7, 0.75, 0.24, 0.22, gap, upper="Body", lower="Belly", tooth=0.13, per_side=5, lower_teeth=True,
                  tongue=True, grin=0.22, skull_d=d, on_jaw=lower_fangs)
    fang_row(m, (-0.25, -0.12, 0.0, 0.12, 0.25), front + 0.9 * 0.7 + 0.05, mouth_z + gap / 2 + 0.02, 0.2, 0.11, True)  # just past the dark mouth block (2026-11-12)
    ball(m, "Accent", 0, front + 0.75, mouth_z + gap / 2 + 0.3, 0.15, 6, 4)  # a knot for a nose
    for side in (-1, 1):
        neon_eye(m, (side * 0.3, 2.37, zc + 0.3), "y", 0.34, -side, white=False, lid=0.3, slant=1.0, brow=0.0, lid_role="Body",
                 brow_role="Accent", diamond=False)
        sausage(m, "Body", (side * 0.35, yc - 0.3, zc + 0.6), (side * 0.65, yc - 0.6, zc + 1.45), 0.2)  # devil-horn ears
        ball(m, "Accent", side * 0.68, yc - 0.63, zc + 1.62, 0.13, 6, 4)
    m.head_centre = (0, front + 0.3, zc)
    return grow(m, 1.12)


# ---------------------------------------------------------------------- the rare ones


def nightmare_mare():
    """A carousel horse that came off its ride, the brass pole still through its back: cracked white paint, a
    crimson and gold saddle with a neon jewel, a mane and tail of pink neon, harlequin diamonds painted round its
    glowing eyes, a crimson plume, and a snarl of fangs."""
    m = monster("dino_NightmareMare", Body="#efe8dc", Accent="#a99abb", Belly="#f8f2e8", Claw="#1a1222", Saddle=CRIMSON, Pole=GOLD)
    m.joint("Spine", (0, 0, 2.7))
    quad_legs(m, 0.5, 1.2, 0.5, -1.35, 2.5, 0.42)
    ankles(m, [("FrontL", -0.5, 1.2), ("FrontR", 0.5, 1.2), ("BackL", -0.5, -1.35), ("BackR", 0.5, -1.35)], 0.42)
    for end, y in (("Front", 1.2), ("Back", -1.35)):  # gilded hooves
        for side in (-1, 1):
            m.bone = end + ("L" if side < 0 else "R")
            m.block("Trim", side * 0.5, y, 0.62, 0.5, 0.55, 0.18)
    m.bone = "Spine"
    body = ((-1.6, 0, 2.85, 1.05, 1.15), (1.35, 0, 3.05, 1.2, 1.35))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-1.3, 0, 2.3, 0.8, 0.16), (1.2, 0, 2.42, 0.95, 0.2))
    for side in (-1, 1):  # cracks in its paint
        x = side * 0.62
        for p, q in (((x, -0.9, 3.2), (x, -0.5, 2.9)), ((x, -0.5, 2.9), (x, -0.1, 3.1)), ((x, 0.7, 3.3), (x, 1.0, 2.8))):
            beam(m, "Accent", p, q, 0.06, 0.08)
    top = top_of(body, 0)
    m.block("Saddle", 0, 0, top + 0.08, 1.3, 1.2, 0.3)
    for side in (-1, 1):
        m.block("Saddle", side * 0.63, 0, top - 0.4, 0.08, 1.15, 0.85)
        m.block("Trim", side * 0.66, 0, top - 0.82, 0.06, 1.2, 0.1)
        gem(m, "Neon", side * 0.69, 0, top - 0.35, 0.14, 0.22, 0.22, 4, math.pi / 4)
    m.block("Trim", 0, 0, top + 0.25, 1.36, 1.26, 0.06)
    m.block("Pole", 0, 0.05, 5.3, 0.22, 0.22, 4.6)  # the carousel's brass pole, still through its back
    for z in range(6):
        m.block("TrimDark", 0, 0.05, 3.6 + z * 0.6, 0.32, 0.32, 0.12)
    ball(m, "Pole", 0, 0.05, 7.7, 0.3, 8, 5)
    tail(m, (-1.55, 3.0, 0.3, 0.3), (-2.6, 2.2, 0.15, 0.15), 3)
    m.bone = "Tail3"
    for dx in (-0.2, 0.0, 0.2):  # a neon tail
        feather(m, (0, -2.5, 2.3), (dx * 2, -3.4, 1.0), 0.32, (1, 0, 0), "Neon", "Neon", 0.3)
    m.bone = "Spine"

    m.use("Neck", (0, 1.1, 3.3))
    beam(m, "Body", (0, 1.05, 3.2), (0, 1.75, 4.5), 0.85, 0.95, 0.7)
    m.stretch("Body", "Spine")
    for k in range(5):  # a mane of pink neon
        p = Vector((0, 1.0, 3.75)).lerp(Vector((0, 1.6, 4.95)), k / 4)
        feather(m, tuple(p), tuple(p + Vector((0, -0.9, 0.55))), 0.4, (0, 1, 0), "Neon", "Neon", 0.3)
    w, d, h = 0.78, 0.95, 0.95
    yc, zc = 2.05, 4.75
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    mouth_z, gap = zc - 0.25, 0.14
    snout = classic_mouth(m, front, mouth_z, w, 1.0, 0.66, 0.26, 0.22, gap, tooth=0.12, per_side=5, lower_teeth=True, tongue=True, skull_d=d)
    for side in (-1, 1):  # fangs at the front of its mouth
        m.loft_z("Teeth", (mouth_z - 0.3, side * 0.2, snout["tip"] - 0.12, 0.03, 0.03), (mouth_z + 0.08, side * 0.2, snout["tip"] - 0.12, 0.12, 0.12))
    top_nostrils(m, snout, 0.16, 0.1)
    y = front + 0.45  # a crimson noseband
    m.block("Saddle", 0, y, mouth_z + gap / 2 + 0.13, snout["width"](y) + 0.06, 0.14, 0.32)
    for side in (-1, 1):
        neon_eye(m, (side * (w / 2), yc + 0.1, zc + 0.15), "+x" if side > 0 else "-x", 0.38, 1, white=False, lid=0.3, slant=1.1, brow=0.0,
                 lid_role="Body", brow_role="Accent")
        round_slab(m, "Trim", (side * (w / 2 + 0.02), yc - 0.25, zc - 0.25), "+x" if side > 0 else "-x", 0.14, 0.04)
        prism(m, "Body", side * 0.25, yc - 0.25, zc + h / 2 - 0.05, zc + h / 2 + 0.55, 0.16, 0.03, 4, 0, (side * 0.08, -0.12))
    feather(m, (0, yc - 0.1, zc + h / 2), (0, yc - 0.7, zc + h / 2 + 1.1), 0.45, (0, 1, 0), "Saddle", "Trim", 0.3)
    m.head_centre = (0, front + 0.4, zc)
    return grow(m, 1.22)


def grinmaster():
    """The ringmaster: a towering thing in a crimson tailcoat with gold buttons and epaulettes and a tall black top
    hat with a neon plume. Its long chalk face is split by a huge grin of needle teeth under a curled black
    moustache, its eyes glow in black diamonds; one clawed glove reaches for you, the other cracks a whip overhead."""
    m = monster("dino_Grinmaster", Body="#2a2033", Accent="#120c18", Belly="#f2ece0", Claw="#120c18", Coat=CRIMSON, CoatDark=CRIMSON_DARK,
                Hat="#16101c", Whip="#4a2e1c")
    m.joint("Spine", (0, 0, 3.4))
    biped_legs(m, 0.45, 0.0, 3.25, 0.55, 1.7, 0.36, 1.05, 0.26)
    for side in (-1, 1):  # black boots over its feet
        m.bone = "ShinL" if side < 0 else "ShinR"
        m.block("Accent", side * 0.45, 1.05 * 0.22, 0.17, 0.36 * 1.5 + 0.12, 1.05 + 0.12, 0.34)
    m.bone = "Spine"
    m.loft_z("Coat", (3.0, 0, 0, 1.5, 0.95), (5.7, 0, 0.05, 2.1, 1.2))
    m.loft_z("Belly", (3.9, 0, 0.55, 0.5, 0.08), (5.6, 0, 0.66, 0.7, 0.08))
    for side in (-1, 1):
        beam(m, "Trim", (side * 0.27, 0.6, 3.85), (side * 0.38, 0.71, 5.6), 0.07, 0.08)  # gold edges to the lapels
        for z in (4.0, 4.5, 5.0):
            m.block("Trim", side * 0.52, 0.56 + (z - 3.0) / 2.7 * 0.18, z, 0.14, 0.08, 0.14)
        m.loft_z("Coat", (1.6, side * 0.38, -0.55, 0.55, 0.12), (3.2, side * 0.42, -0.5, 0.7, 0.14))  # coat tails
        m.block("Trim", side * 1.0, 0.0, 5.72, 0.6, 1.0, 0.18)  # epaulettes with a fringe
        for k in range(4):
            m.block("Trim", side * (1.22 + 0.02 * k), -0.35 + k * 0.24, 5.5, 0.06, 0.08, 0.32)
    for side in (-1, 1):  # its bow tie
        gem(m, "CoatDark", side * 0.18, 0.73, 5.5, 0.14, 0.14, 0.14, 4, 0)
    m.block("CoatDark", 0, 0.75, 5.5, 0.12, 0.1, 0.12)
    for side in (-1, 1):
        m.use("ArmL" if side < 0 else "ArmR", (side * 1.05, 0.0, 5.45))
        beam(m, "Coat", (side * 1.05, 0.0, 5.5), (side * 1.4, 0.3, 4.3), 0.42, None, 0.36)
        m.block("Coat", side * 1.4, 0.3, 4.3, 0.36, 0.36, 0.36)
        if side > 0:  # cracking a whip
            beam(m, "Coat", (1.4, 0.3, 4.3), (1.45, 1.0, 4.4), 0.34, None, 0.3)
            m.block("Belly", 1.45, 1.1, 4.4, 0.36, 0.14, 0.36)
            m.block("Glove", 1.45, 1.35, 4.45, 0.36, 0.38, 0.36)
            beam(m, "Whip", (1.45, 1.35, 4.35), (1.5, 1.55, 5.0), 0.12)
            limb(m, "Whip", [(1.5, 1.55, 5.0), (1.75, 1.3, 6.4), (1.3, -0.3, 7.7), (0.0, -1.5, 8.1), (-1.2, -1.3, 7.5), (-1.8, -0.6, 6.7)], 0.09, 0.04)  # over and behind its head (2026-11-12: it ran through its face)
        else:  # reaching for you with long clawed fingers
            beam(m, "Coat", (-1.4, 0.3, 4.3), (-1.3, 1.1, 4.6), 0.34, None, 0.3)
            m.block("Belly", -1.3, 1.2, 4.6, 0.36, 0.14, 0.36)
            m.block("Glove", -1.3, 1.45, 4.6, 0.42, 0.4, 0.36)
            for off in (-0.13, 0.0, 0.13):
                beam(m, "Glove", (-1.3 + off, 1.6, 4.65), (-1.3 + off * 1.5, 2.05, 4.75), 0.1, None, 0.08)
                beam(m, "Claw", (-1.3 + off * 1.5, 2.05, 4.75), (-1.3 + off * 1.6, 2.3, 4.6), 0.08, None, 0.02)
    m.bone = "Spine"

    m.use("Neck", (0, 0.05, 5.7))
    m.block("Belly", 0, 0.05, 5.85, 0.8, 0.75, 0.35)
    w, d, h = 1.25, 1.2, 1.7
    yc, zc = 0.15, 6.75
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Face", 0, yc, zc, w, d, h)
    mouth_z, gap = zc - 0.45, 0.3

    def lower_fangs(m, front, mouth_z, gap, lower_length):
        fang_row(m, (-0.36, -0.18, 0.0, 0.18, 0.36), front + 0.9 * 0.35 + 0.05, mouth_z - gap / 2 - 0.02, 0.24, 0.14, False)

    classic_mouth(m, front, mouth_z, w, 0.35, 1.15, 0.22, 0.3, gap, upper="Face", lower="Face", tooth=0.15, per_side=4, lower_teeth=True,
                  tongue=True, grin=0.3, skull_d=d, on_jaw=lower_fangs)
    fang_row(m, (-0.42, -0.25, -0.08, 0.08, 0.25, 0.42), front + 0.9 * 0.35 + 0.05, mouth_z + gap / 2 + 0.02, 0.26, 0.14, True)  # just past the dark mouth block (2026-11-12)
    painted_grin(m, front, mouth_z, 0.6, 0.45, 0.15, edge=w / 2, start=gap / 2 + 0.08)
    for side in (-1, 1):  # a curled moustache
        beam(m, "Accent", (0, front + 0.37, mouth_z + 0.32), (side * 0.5, front + 0.3, mouth_z + 0.3), 0.18, 0.14, 0.12)
        beam(m, "Accent", (side * 0.5, front + 0.3, mouth_z + 0.3), (side * 0.66, front + 0.25, mouth_z + 0.56), 0.12, 0.1, 0.05)
        neon_eye(m, (side * 0.3, front, zc + 0.38), "y", 0.36, -side, white=False, lid=0.3, slant=1.2, brow=0.0, brow_role="Accent")
        m.block("Accent", side * (w / 2 + 0.03), yc - 0.1, zc + 0.15, 0.08, 0.5, 0.9)  # sideburns
    m.loft_y("Face", (front, 0, zc + 0.1, 0.22, 0.3), (front + 0.35, 0, zc - 0.02, 0.06, 0.08))  # a sharp nose
    m.block("Hat", 0, yc - 0.05, zc + h / 2 + 0.06, 1.7, 1.55, 0.12)  # its top hat
    m.loft_z("Hat", (zc + h / 2 + 0.1, 0, yc - 0.05, 1.1, 1.0), (zc + h / 2 + 1.7, 0, yc - 0.1, 1.25, 1.15))
    m.loft_z("Coat", (zc + h / 2 + 0.12, 0, yc - 0.05, 1.2, 1.1), (zc + h / 2 + 0.45, 0, yc - 0.06, 1.23, 1.13))
    m.block("Trim", 0, yc + 0.48, zc + h / 2 + 0.29, 0.3, 0.06, 0.24)
    feather(m, (0.45, yc - 0.1, zc + h / 2 + 0.4), (0.8, yc - 0.6, zc + h / 2 + 1.9), 0.32, (1, 0, 0), "Neon", "Neon", 0.3)
    m.head_centre = (0, front + 0.3, zc + 0.1)
    return m


def big_top_terror():
    """The boss: an elephant-legged beast carrying the whole big top on its back, cream and crimson stripes, a gold
    scalloped valance hung with bulbs and a pennant on its pole. A ruff round its neck, and out of it a giant clown
    head: chalk-white, eyes glowing in black diamonds, a red nose, purple hair, a crown of bulbs and a mouth of fangs
    with its grin painted up its cheeks; long arms reach out from under the ruff, gloved and clawed."""
    m = monster("dino_BigTopTerror", Body="#5b4f6b", Accent="#3a3046", Belly="#8a7d9a", Claw="#efe2c4", Tent=CREAM, TentStripe=CRIMSON,
                Ruff=TEAL)
    m.joint("Spine", (0, 0, 4.3))
    quad_legs(m, 1.5, 1.7, 1.5, -1.9, 4.1, 1.3)
    for end, y in (("Front", 1.7), ("Back", -1.9)):
        for side in (-1, 1):
            m.bone = end + ("L" if side < 0 else "R")
            for z in (1.5, 3.1):
                m.block("Trim", side * 1.5, y, z, 1.42, 1.58, 0.32)
    m.bone = "Spine"
    body = ((-2.6, 0, 4.6, 3.6, 2.9), (2.3, 0, 4.9, 4.0, 3.3))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-2.2, 0, 3.2, 2.8, 0.2), (2.0, 0, 3.3, 3.2, 0.25))
    # The big top on its back.
    base = top_of(body, -0.1) - 0.35
    prism(m, "Tent", 0, -0.1, base, base + 0.9, 2.9, 2.9, 12, 0)
    prism(m, "Tent", 0, -0.1, base + 0.9, base + 4.6, 3.1, 0.25, 12, 0)
    c15 = math.cos(math.pi / 12)
    for k in range(12):
        a = (k + 0.5) * math.tau / 12
        u, t = Vector((math.cos(a), math.sin(a), 0)), Vector((-math.sin(a), math.cos(a), 0))
        centre = Vector((0, -0.1, 0))
        if k % 2 == 0:
            plate(m, "TentStripe", tuple(centre + u * (3.1 * c15 + 0.09) + Vector((0, 0, base + 0.95))),
                  tuple(centre + u * (0.25 * c15 + 0.09) + Vector((0, 0, base + 4.5))), tuple(t), 1.45, 0.08, 0.06)
            plate(m, "TentStripe", tuple(centre + u * (2.9 * c15 + 0.04) + Vector((0, 0, base + 0.05))),
                  tuple(centre + u * (2.9 * c15 + 0.04) + Vector((0, 0, base + 0.85))), tuple(t), 1.35, 1.35, 0.06)
        edge = centre + u * (3.1 * c15 + 0.06) + Vector((0, 0, base + 0.9))
        plate(m, "Trim", tuple(edge), tuple(edge + Vector((0, 0, -0.5))), tuple(t), 1.5, 0.12, 0.08)  # the scalloped valance
        ball(m, "Bulb", edge.x, edge.y, edge.z - 0.58, 0.14, 6, 4)
    m.block("Trim", 0, -0.1, base + 5.2, 0.16, 0.16, 1.4)
    plate(m, "TentStripe", (0, -0.1, base + 5.75), (0, -1.5, base + 5.5), (0, 0, 1), 0.65, 0.04, 0.05)
    ball(m, "Bulb", 0, -0.1, base + 5.98, 0.2, 6, 4)
    tail(m, (-2.55, 4.9, 0.6, 0.6), (-4.6, 3.6, 0.3, 0.3), 3)
    m.bone = "Tail3"
    ball(m, "Hair", 0, -4.75, 3.55, 0.5, 8, 5)
    m.bone = "Spine"
    for side in (-1, 1):  # long arms out from under the ruff
        s = "L" if side < 0 else "R"
        m.use("Wing" + s, (side * 1.6, 1.9, 5.3))
        beam(m, "Body", (side * 1.6, 1.9, 5.3), (side * 2.6, 3.2, 4.4), 0.8, None, 0.7)
        m.block("Body", side * 2.6, 3.2, 4.4, 0.7, 0.7, 0.7)
        beam(m, "Body", (side * 2.6, 3.2, 4.4), (side * 2.4, 4.5, 3.5), 0.7, None, 0.6)
        m.block("Glove", side * 2.4, 4.85, 3.35, 0.95, 0.9, 0.85)
        for off in (-0.3, 0.0, 0.3):
            m.loft_y("Claw", (5.25, side * 2.4 + off, 3.2, 0.24, 0.26), (5.85, side * 2.4 + off * 1.2, 2.75, 0.04, 0.04))
    m.bone = "Spine"

    m.use("Neck", (0, 2.0, 5.0))
    for k, (r, role) in enumerate(((2.3, "Ruff"), (2.0, "Belly"), (1.7, "Ruff"))):
        round_slab(m, role, (0, 2.35 + 0.16 * k, 5.4), "y", r, 0.18, 16)
    w, d, h = 3.0, 2.5, 2.7
    yc, zc = 3.65, 6.0
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Face", 0, yc, zc, w, d, h)
    mouth_z, gap = zc - 0.55, 0.7

    def lower_fangs(m, front, mouth_z, gap, lower_length):  # fangs, and pink neon glowing in its throat
        m.block("Neon", 0, front + lower_length * 0.4, mouth_z - gap / 2 + 0.06, 1.5, lower_length * 0.6, 0.06)
        fang_row(m, (-0.9, -0.54, -0.18, 0.18, 0.54, 0.9), front + 0.9 * 0.6 + 0.05, mouth_z - gap / 2 - 0.02, 0.5, 0.3, False)

    classic_mouth(m, front, mouth_z, w, 0.6, 2.5, 0.36, 0.42, gap, upper="Face", lower="Face", tooth=0.34, per_side=5, lower_teeth=True,
                  tongue=False, skull_d=d, on_jaw=lower_fangs)
    fang_row(m, (-1.0, -0.66, -0.33, 0.0, 0.33, 0.66, 1.0), front + 0.9 * 0.6 + 0.05, mouth_z + gap / 2 + 0.02, 0.56, 0.32, True)  # just past the dark mouth block, clear of the paint (2026-11-12)
    painted_grin(m, front, mouth_z, 1.27, 0.8, 0.2, 0.18, edge=w / 2, start=gap / 2 + 0.1)
    for side in (-1, 1):
        neon_eye(m, (side * 0.75, front, zc + 0.6), "y", 0.72, -side, white=False, lid=0.3, slant=1.15, brow=0.0)
        ball(m, "Hair", side * 1.7, yc - 0.2, zc + 0.6, 0.85, 8, 5)
        ball(m, "Hair", side * 1.6, yc - 0.6, zc - 0.2, 0.65, 8, 5)
    ball(m, "Nose", 0, front + 0.62, zc + 0.15, 0.48, 10, 6)
    m.block("Trim", 0, yc - 0.2, zc + h / 2 + 0.15, 2.4, 1.8, 0.3)  # a crown of bulbs
    for x in (-0.9, -0.3, 0.3, 0.9):
        prism(m, "Trim", x, yc - 0.2, zc + h / 2 + 0.3, zc + h / 2 + 1.0, 0.22, 0.05, 4, math.pi / 4)
        ball(m, "Bulb", x, yc - 0.2, zc + h / 2 + 1.06, 0.17, 6, 4)
    m.head_centre = (0, front + 0.5, zc + 0.3)
    return m


ALL = [jack_snap, popcorn_fiend, twisty, nightmare_mare, grinmaster, big_top_terror]


def quick_preview(models, out):
    """Stills only, for trying faces: each model whole, its face up close, and the lineup."""
    import bpy
    scene = kit.setup_scene()
    kit.RENDERS = out
    out.mkdir(parents=True, exist_ok=True)
    animals = bpy.data.collections.new("Animals")
    scene.collection.children.link(animals)
    roots = []
    for i, model in enumerate(models):
        root = model.build(animals)
        root.location = (i * 16, 0, 0)
        roots.append(root)
    light_up(roots, GLOW_ROLES, GLOW)
    ground = bpy.data.meshes.new("Ground")
    ground.from_pydata([(-300, -300, -0.01), (400, -300, -0.01), (400, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground.materials.append(kit.material("Ground", FLOOR, False))
    scene.collection.objects.link(bpy.data.objects.new("Ground", ground))
    set_sky(scene, SKY)
    bpy.context.view_layer.update()
    for model, root in zip(models, roots):
        kit.set_visible(roots, [root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 3)
        kit.shoot(scene, f"{model.name}_full", centre + Vector((0.62, 0.85, 0.32)) * reach * 1.15, centre, (640, 640), 50)
        head = root.location + Vector(model.head_centre)
        size = max(3.2, model.head_centre[2] * 0.75)
        kit.shoot(scene, f"{model.name}_face", head + Vector((0.55, 1.0, 0.14)) * size * 1.5, head, (560, 560), 50)
    kit.set_visible(roots, roots)
    middle = (len(models) - 1) * 16 / 2
    kit.shoot(scene, "lineup", (middle, 84, 20), (middle, 0, 5.5), (1800, 700), 26)


def main():
    builders = ALL
    only = os.environ.get("ONLY")
    if only:
        builders = [b for b in builders if b.__name__ in only.split(",")]
    models = [b() for b in builders]
    if os.environ.get("QUICK"):
        quick_preview(models, Path(os.environ.get("QUICK_OUT", str(RENDERS / "quick"))))
        return
    build_and_render(models, RENDERS, HERE / f"{BLEND}.blend", "midnight_carnival_animation_preview.mp4", sky=SKY, ground=FLOOR,
                     glow_roles=GLOW_ROLES, spacing=16, glow=GLOW)


if __name__ == "__main__":
    main()
