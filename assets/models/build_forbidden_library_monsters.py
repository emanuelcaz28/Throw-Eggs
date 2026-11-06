"""Builds Forbidden Library's 6 monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_forbidden_library_monsters.py
    QUICK=1 Blender -b -P build_forbidden_library_monsters.py    (stills only, into QUICK_OUT, for trying faces)
    ONLY=inkling,hex_owl QUICK=1 ...                              (just those)

Saves forbidden_library_monsters.blend and renders to design/world/monsters_forbidden_library/. The map's props
are in build_forbidden_library.py.

Map 10, a library whose books are alive. The owner asked for monsters that suit the biome and are aggressive in a
good way: every one of them glares and bares its teeth, the common ones with a bit of mischief, the rare ones
truly fierce, ending in a boss. They share the ink eye: a glowing violet iris with a black slit pupil, like a
drop of the living ink, under a brow that slants down to the nose. The common ones have it in a white eye; the
fierce ones have no white at all, just the violet glow in a black socket. Teeth are page-white, and the ink glows
violet in their mouths and drips off them. The map's colours: violet ink, old leather, parchment, walnut, candle
wax and gilt.

  Inkling        a gremlin of living ink: a pot belly, a head that's mostly grin, a glowing ink tongue, a quill
                 stuck in its head like a crest, claws up, ink dripping off it, and a gold pen nib on its tail
  Hermit Tome    a crab that lives under an open book like a roof: big pincers up and open, angry eyes on stalks,
                 mandibles full of teeth, a ribbon bookmark trailing behind
  Wax Hound      a hunched dog of candle wax, melting as it goes: candles burning on its back, a wick flame on its
                 forehead and a flame on its tail, droopy melted ears and a snarl of wax-dripping fangs
  Quillback      a raptor with a crest of giant quills down its back and head, their tips dipped in glowing ink,
                 quills on its arms and tail, and gold pen-nib sickle claws
  Hex Owl        a huge horned owl, the library's keeper: gold spectacles over glowing violet eyes, a hooked gold
                 beak, flight feathers like pages, and its chest a page covered in glowing writing
  Tome Tyrant    the boss: a hulking beast whose head is a giant grimoire. Its covers are its jaws, pages of fangs
                 in them and violet ink glowing inside, a ribbon tongue; violet eyes glare from under its brow, a
                 crown of candles burns on top, a glowing sigil on its chest, broken shackles and chains on its
                 wrists, candles on its shoulders and a bookmark ribbon for a tail

All have a Jaw bone (they snap as they walk and roar once per idle in the game, DinoLifeController); the crab's
eye stalks and the owl's wings ride the Wing bones. Glowing parts are EyeGlow, InkGlow, Flame and FlameCore (Neon
in the game, shared/Roles.luau, all there already). Skin roles Body, Accent, Belly and Claw take the colour
mutations; gilt, pages, quills, candles, chains and ribbons keep their colour. Built at the first map's size; the
game scales them by Config/Biomes standardScale. 1 Blender unit = 1 stud, models face +Y, feet on Z = 0.

Like the map's props, no stud texture in this file (kit.PREVIEW_STUDS off): plain colours, and the studs come
only from Studio's shared "Studs" material.
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
from build_eclipse_temple_monsters import at, face_box, feather, flank, grow, round_slab  # noqa: E402
from build_forbidden_library import Frame, candle, turn  # noqa: E402
from build_forest import Model, biped_legs, tail  # noqa: E402
from build_starfall_crater import ball, hoop  # noqa: E402
from build_volcano import prism, top_of  # noqa: E402
from face_kit import classic_mouth, icicle, top_nostrils  # noqa: E402
from map_kit import limb, plate  # noqa: E402
from monster_stage import build_and_render, light_up, set_sky  # noqa: E402

kit.PREVIEW_STUDS = False  # plain colours: studs come from Studio's "Studs" material, never from this file

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_forbidden_library"
BLEND = "forbidden_library_monsters"  # for check_map.py and export_fbx.py

GLOW_ROLES = {"EyeGlow", "InkGlow", "Flame", "FlameCore"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket"})
GLOW = 1.6  # render glow strength

# The map's colours (build_forbidden_library.py) and the ink face.
INK = "#8a5cff"
GILT = "#f2c24e"
PAGE, PAGE_DARK = "#efe2bd", "#b89a68"
RIBBON = "#c42a45"
QUILL = "#f3eee4"
FACE = {"Pupil": "#0c0a12", "Socket": "#0c0a12", "EyeGlow": "#a77bff", "EyeWhite": "#f6f1e2", "Mouth": "#2a1430", "Teeth": "#f4ecd6",
        "Tongue": RIBBON, "InkGlow": INK, "Gilt": GILT, "Page": PAGE, "Flame": "#ffb347", "FlameCore": "#fff3c4"}
SKY, FLOOR = "#17142b", "#483874"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- the ink face


def ink_iris(m, centre, normal, size, inner=1):
    """The ink eye's middle: a glowing violet iris, a black slit pupil, and a glint towards the top outer corner."""
    nv = {"y": Vector((0, 1, 0)), "+x": Vector((1, 0, 0)), "-x": Vector((-1, 0, 0))}[normal]
    c = Vector(centre)
    round_slab(m, "EyeGlow", tuple(c + nv * 0.02), normal, size * 0.38, 0.04)
    face_box(m, "Pupil", tuple(c), normal, 0, 0, 0.05, size * 0.1, size * 0.5, 0.05)
    g = size * 0.08
    gx, gy, gz = at(tuple(c), normal, -inner * size * 0.13, size * 0.13, 0.08)
    m.block("Highlight", gx, gy, gz, g, g, g)


def ink_eye(m, origin, normal, size, inner=1, white=True, look=(0.0, 0.0), lid=0.0, slant=0.0, brow=None,
            lid_role="Body", brow_role="Accent"):
    """One eye on a face at origin (its middle, on the surface); inner (+1/-1) is the way to the nose along u.
    white: a white eye, or a black socket, which reads far fiercer. lid covers that share of the eye from the top;
    slant tips the lid and the brow down towards the nose (angry). brow: how high a brow ridge sits, or None."""
    w, h = size * 1.0, size * 0.95
    face_box(m, "EyeWhite" if white else "Socket", origin, normal, 0, 0, 0.03, w, h, 0.08)
    ink_iris(m, at(origin, normal, look[0] * w * 0.28, look[1] * h * 0.28, 0.07), normal, size, inner)
    top = h / 2 + size * 0.04
    dz = slant * size * 0.3

    def tilted(role, bottom, thick_top, depth, n):
        outer = at(origin, normal, -inner * (w / 2 + size * 0.05), 0, n)
        inner_p = at(origin, normal, inner * (w / 2 + size * 0.05), 0, n)
        bo, bi = bottom + dz, bottom - dz
        to, ti = thick_top + dz * 0.5, thick_top - dz * 0.5
        if normal == "y":
            m.loft_x(role, (outer[0], outer[1], outer[2] + (bo + to) / 2, depth, to - bo),
                     (inner_p[0], inner_p[1], inner_p[2] + (bi + ti) / 2, depth, ti - bi))
        else:
            m.loft_y(role, (outer[1], outer[0], outer[2] + (bo + to) / 2, depth, to - bo),
                     (inner_p[1], inner_p[0], inner_p[2] + (bi + ti) / 2, depth, ti - bi))

    if lid > 0:
        tilted(lid_role, top - h * lid - size * 0.04, top + size * 0.02, 0.16, 0.08)
    if brow is not None:
        tilted(brow_role, top + brow * size, top + brow * size + size * 0.24, size * 0.3, 0.12)


def stalk_eye(m, x, y, z, r, side, brow_role="Accent"):
    """A round eye on the end of a stalk, looking forward, under a brow slanting down towards the middle."""
    ball(m, "EyeWhite", x, y, z, r, 8, 5)
    ink_iris(m, (x, y + r * 0.92, z), "y", r * 1.5, -side)
    beam(m, brow_role, (x + side * r * 1.0, y + r * 0.5, z + r * 0.95), (x - side * r * 1.0, y + r * 0.5, z + r * 0.5), 0.2, 0.18)


def drips(m, spots, role="InkGlow", width=0.14):
    """Drops hanging off something: (x, y, top, length) each."""
    for x, y, top, length in spots:
        icicle(m, role, x, y, top, length, width)


def ink_sigil(m, cx, y, cz, s, role="InkGlow", thick=0.1):
    """A glowing eye drawn in ink, standing on a face that looks +Y: two lids meeting at its corners, and its iris."""
    for side in (-1, 1):
        for p, q in (((-1.1, 0), (-0.45, side * 0.48)), ((-0.45, side * 0.48), (0.45, side * 0.48)), ((0.45, side * 0.48), (1.1, 0))):
            beam(m, role, (cx + p[0] * s, y, cz + p[1] * s), (cx + q[0] * s, y, cz + q[1] * s), 0.16 * s, thick)
    round_slab(m, role, (cx, y, cz), "y", 0.3 * s, thick)


# ---------------------------------------------------------------------- the common ones


def inkling():
    """A gremlin of living ink that crawled out of a spilt inkwell: a pot belly, a head that's mostly grin with
    crooked page-white teeth and a glowing ink tongue, a quill stuck in its head like a crest, claws up ready to
    scratch, ink dripping off its chin and arms, and a gold pen nib on the end of its tail."""
    m = monster("dino_Inkling", Body="#2c2456", Accent="#1a1538", Belly="#6a56b8", Claw="#120e26", Quill=QUILL, QuillTip="#3a2470",
                Nib=GILT)
    m.joint("Spine", (0, 0, 1.2))
    biped_legs(m, 0.42, 0.0, 1.1, 0.55, 0.65, 0.36, 0.8, 0.22)
    m.loft_z("Body", (0.95, 0, 0, 1.25, 1.05), (1.8, 0, 0.06, 1.5, 1.25))
    m.loft_z("Body", (1.8, 0, 0.06, 1.5, 1.25), (2.45, 0, 0.1, 1.05, 0.9))
    m.loft_z("Belly", (1.1, 0, 0.6, 0.85, 0.1), (1.9, 0, 0.7, 0.95, 0.1))
    drips(m, ((-0.62, 0.3, 1.45, 0.5), (0.66, 0.1, 1.6, 0.4), (0.2, 0.6, 1.0, 0.35)))
    for side in (-1, 1):  # arms out, claws raised to scratch
        sx = side * 0.7
        m.use("ArmL" if side < 0 else "ArmR", (sx, 0.1, 2.2))
        beam(m, "Body", (sx, 0.1, 2.25), (side * 1.25, 0.45, 1.75), 0.34, None, 0.28)
        m.block("Body", side * 1.25, 0.45, 1.75, 0.3, 0.3, 0.3)
        beam(m, "Body", (side * 1.25, 0.45, 1.75), (side * 1.35, 0.85, 2.45), 0.28, None, 0.24)
        m.block("Body", side * 1.35, 0.9, 2.55, 0.36, 0.34, 0.3)
        for off in (-0.11, 0.0, 0.11):
            m.loft_z("Claw", (2.68, side * 1.35 + off, 0.95, 0.1, 0.1), (3.05, side * 1.35 + off * 1.5, 1.02, 0.02, 0.02))
        icicle(m, "InkGlow", side * 1.27, 0.45, 1.66, 0.5, 0.13)
    m.bone = "Spine"
    tail(m, (-0.45, 1.35, 0.42, 0.42), (-1.7, 0.75, 0.14, 0.14), 3)
    m.bone = "Tail3"
    plate(m, "Nib", (0, -1.62, 0.76), (0, -2.3, 0.5), (1, 0, 0), 0.42, 0.04, 0.08)
    m.bone = "Spine"

    m.use("Neck", (0, 0.1, 2.4))
    m.block("Body", 0, 0.12, 2.45, 0.8, 0.7, 0.3)
    w, d, h = 1.95, 1.45, 1.5
    yc, zc = 0.3, 3.15
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)

    def ink_tongue(m, front, mouth_z, gap, lower_length):  # a glowing tongue of ink, and ink dripping off the chin
        m.block("InkGlow", 0, front + lower_length * 0.45, mouth_z - gap / 2 + 0.07, 0.8, lower_length * 0.75, 0.1)
        drips(m, ((-0.45, front + lower_length * 0.7, mouth_z - gap / 2 - 0.26, 0.5), (0.35, front + lower_length * 0.85, mouth_z - gap / 2 - 0.26, 0.38)))
        for x in (-0.6, -0.3, 0.0, 0.3, 0.6):  # a row of fangs across the front of the jaw
            m.loft_z("Teeth", (mouth_z - gap / 2 - 0.02, x, front + lower_length - 0.12, 0.17, 0.17),
                     (mouth_z - gap / 2 + 0.2, x, front + lower_length - 0.12, 0.03, 0.03))

    classic_mouth(m, front, zc - 0.35, w, 0.5, 1.75, 0.22, 0.26, 0.3, upper="Body", lower="Belly", tooth=0.21, per_side=5,
                  lower_teeth=True, tongue=False, grin=0.25, skull_d=d, on_jaw=ink_tongue)
    for x in (-0.75, -0.45, -0.15, 0.15, 0.45, 0.75):  # and across the front of the upper jaw, between them
        m.loft_z("Teeth", (zc - 0.35 + 0.17 - 0.26, x, front + 0.4, 0.03, 0.03), (zc - 0.35 + 0.17, x, front + 0.4, 0.19, 0.19))
    for side in (-1, 1):
        ink_eye(m, (side * 0.47, front, zc + 0.42), "y", 0.52, -side, white=True, look=(side * -0.15, 0.0), lid=0.18, slant=1.0,
                brow=0.02, lid_role="Body", brow_role="Accent")
        prism(m, "Accent", side * 0.62, yc - 0.15, zc + h / 2 - 0.05, zc + h / 2 + 0.55, 0.22, 0.03, 4, 0, (side * 0.14, -0.1))  # ink horns
    feather(m, (0.3, yc - 0.15, zc + h / 2 - 0.25), (0.75, yc - 1.3, zc + h / 2 + 1.9), 0.62, (1, 0, 0), "Quill", "QuillTip", 0.25)
    m.head_centre = (0, front + 0.2, zc)
    return m


def hermit_tome():
    """A crab that moved into an old book: it carries it open over its back like a roof, pages down. Big pincers
    up and open with teeth inside them, angry eyes on stalks, mandibles crowded with teeth, feelers, and a ribbon
    bookmark trailing out behind."""
    m = monster("dino_HermitTome", Body="#c2563c", Accent="#8a3526", Belly="#f0c8a0", Claw="#3a1a14", Cover="#2f7a5e",
                CoverDark="#1f5a44", Ribbon=RIBBON)
    m.joint("Spine", (0, 0, 1.15))
    for end, y in (("Front", 0.45), ("Back", -0.55)):  # four splayed crab legs
        for side in (-1, 1):
            sx = side * 0.8
            m.use(end + ("L" if side < 0 else "R"), (sx, y, 1.05))
            fy = 0.35 if end == "Front" else -0.35
            knee = (side * 1.9, y + fy, 1.7)
            foot = (side * 2.3, y + fy * 1.6, 0.04)
            beam(m, "Body", (sx, y, 1.05), knee, 0.38, None, 0.3)
            m.block("Accent", *knee, 0.36, 0.36, 0.36)
            beam(m, "Accent", knee, foot, 0.3, None, 0.07)
    m.bone = "Spine"
    carapace = ((-0.95, 0, 1.15, 1.75, 0.8), (0.85, 0, 1.25, 1.95, 0.9))
    m.loft_y("Body", *carapace)
    m.loft_y("Belly", (-0.8, 0, 0.8, 1.4, 0.12), (0.75, 0, 0.86, 1.6, 0.12))
    for x, y in ((-0.45, 0.4), (0.4, 0.1), (-0.1, -0.5), (0.55, -0.6)):
        m.block("Accent", x, y, top_of(carapace, y) + 0.02, 0.3, 0.3, 0.1)
    # The book, open over its back like a roof: two covers and their pages, gilt corners, the spine along the top.
    ridge = Vector((0, -0.6, 2.83))
    for s in (-1, 1):
        f = Frame(m, ridge, turn(y=s * 0.95))
        f.box("Cover", s * 0.95, 0, 0.0, 1.9, 2.8, 0.2)
        f.box("Page", s * 0.9, 0, -0.22, 1.7, 2.55, 0.36)
        for dy in (-1.22, 1.22):
            f.box("Gilt", s * 1.78, dy, 0.0, 0.36, 0.36, 0.26)
    m.block("CoverDark", 0, ridge.y, ridge.z + 0.08, 0.5, 2.9, 0.45)
    for dy in (-0.9, 0.9):
        m.block("Gilt", 0, ridge.y + dy, ridge.z + 0.08, 0.56, 0.16, 0.5)
    limb(m, "Ribbon", [(0.15, -1.9, 2.7), (0.3, -2.35, 2.1), (0.2, -2.55, 1.3)], 0.32, 0.28)
    # Pincers, up and open, teeth along their inner edges.
    for side in (-1, 1):
        m.use("ArmL" if side < 0 else "ArmR", (side * 0.75, 0.75, 1.3))
        beam(m, "Body", (side * 0.75, 0.75, 1.3), (side * 1.35, 1.35, 1.75), 0.42, None, 0.36)
        m.block("Accent", side * 1.35, 1.35, 1.75, 0.4, 0.4, 0.4)
        beam(m, "Body", (side * 1.35, 1.35, 1.75), (side * 1.15, 1.95, 2.25), 0.38, None, 0.34)
        px, py, pz = side * 1.1, 2.25, 2.35
        m.loft_y("Body", (py - 0.35, px, pz, 0.6, 0.65), (py + 0.35, px, pz + 0.05, 0.85, 0.85))
        top_a, top_b = Vector((px, py + 0.3, pz + 0.25)), Vector((px - side * 0.05, py + 1.15, pz + 0.55))
        low_a, low_b = Vector((px, py + 0.3, pz - 0.2)), Vector((px, py + 1.0, pz - 0.45))
        beam(m, "Claw", tuple(top_a), tuple(top_b), 0.42, 0.34, 0.12)
        beam(m, "Claw", tuple(low_a), tuple(low_b), 0.36, 0.3, 0.1)
        for t in (0.3, 0.55, 0.8):
            p = top_a.lerp(top_b, t)
            m.loft_z("Teeth", (p.z - 0.32, p.x, p.y, 0.02, 0.02), (p.z - 0.1, p.x, p.y, 0.12, 0.12))
            q = low_a.lerp(low_b, t)
            m.loft_z("Teeth", (q.z + 0.08, q.x, q.y, 0.11, 0.11), (q.z + 0.3, q.x, q.y, 0.02, 0.02))
    m.bone = "Spine"
    # Eyes on stalks, on the Wing bones so they sway.
    for side in (-1, 1):
        s = "L" if side < 0 else "R"
        base = (side * 0.35, 0.95, 1.55)
        m.use("Wing" + s, base)
        top = (side * 0.55, 1.15, 2.75)
        beam(m, "Accent", base, top, 0.18, None, 0.14)
        stalk_eye(m, top[0], top[1], top[2] + 0.2, 0.34, side)
    m.bone = "Spine"
    # Its face: mandibles full of teeth, and feelers.
    w, d, h = 1.3, 0.5, 0.65
    yc, zc = 0.95, 1.3
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    classic_mouth(m, front, zc - 0.12, w, 0.22, 1.1, 0.2, 0.2, 0.1, upper="Body", lower="Belly", tooth=0.1, per_side=4,
                  lower_teeth=True, tongue=False, skull_d=d)
    for side in (-1, 1):
        beam(m, "Accent", (side * 0.3, front, zc + 0.2), (side * 0.85, front + 1.1, zc + 0.95), 0.09, None, 0.04)
    m.head_centre = (0, front + 0.3, 2.0)
    return m


def wax_hound():
    """A hunched dog of candle wax, melting as it goes: three candles burning on its back, a wick flame on its
    forehead and a candle flame on the tip of its tail, droopy melted ears, wax running down its flanks, and a
    snarl of fangs dripping wax. Violet ink eyes glare from black sockets."""
    m = monster("dino_WaxHound", Body="#e6d2a4", Accent="#c4a26a", Belly="#f3e6c6", Claw="#5a4632", Candle="#fbf6ea", Wick="#2a2220")
    rng = random.Random(3)
    m.joint("Spine", (0, 0, 1.9))
    quad_legs(m, 0.62, 1.15, 0.62, -1.3, 1.75, 0.5)
    body = ((-1.65, 0, 2.0, 1.15, 1.05), (1.3, 0, 2.25, 1.4, 1.35))
    m.loft_y("Body", *body)
    m.block("Body", 0, 0.9, 2.55, 1.45, 1.0, 0.8)  # hunched shoulders
    m.loft_y("Belly", (-1.3, 0, 1.5, 0.85, 0.2), (1.1, 0, 1.6, 1.05, 0.25))
    for side in (-1, 1):  # wax running down its flanks
        for y in (-1.2, -0.5, 0.25):
            p = flank(body, y, -0.45, side, 0.0)
            icicle(m, "Accent", p[0], p[1], p[2] + 0.3, rng.uniform(0.6, 0.9), 0.22)
    for y in (-0.9, 0.0, 0.8):
        icicle(m, "Accent", rng.uniform(-0.3, 0.3), y, 1.45, rng.uniform(0.3, 0.5), 0.2)
    for x, y, height, r in ((0.22, 0.75, 1.3, 0.24), (-0.25, -0.2, 1.0, 0.22), (0.15, -1.0, 0.75, 0.2)):  # candles on its back
        z = 2.95 if y > 0.4 else top_of(body, y)
        m.block("Accent", x, y, z + 0.02, r * 3, r * 3, 0.14)
        candle(m, x, y, z - 0.05, height, r, wax="Candle", flame="Flame", core="FlameCore", rng=rng, drips=2)
    tail(m, (-1.6, 2.15, 0.34, 0.34), (-3.1, 2.95, 0.22, 0.22), 3)
    m.bone = "Tail3"
    prism(m, "Flame", 0, -3.12, 2.98, 3.8, 0.2, 0.02, 6, 0.3)
    prism(m, "FlameCore", 0, -3.12, 2.95, 3.25, 0.24, 0.1, 6, 0.0)
    m.bone = "Spine"

    m.use("Neck", (0, 1.15, 2.5))
    m.loft_y("Body", (1.0, 0, 2.5, 0.95, 0.9), (1.85, 0, 2.85, 0.85, 0.8))
    m.stretch("Body", "Spine")
    w, d, h = 1.15, 1.2, 0.95
    yc, zc = 2.05, 3.05
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)

    def wax_drool(m, front, mouth_z, gap, lower_length):
        drips(m, ((-0.22, front + lower_length * 0.6, mouth_z - gap / 2 - 0.22, 0.45), (0.25, front + lower_length * 0.8, mouth_z - gap / 2 - 0.22, 0.32)),
              "Accent", 0.15)

    snout = classic_mouth(m, front, zc - 0.22, w, 0.75, 0.82, 0.22, 0.24, 0.16, tooth=0.14, per_side=4, lower_teeth=True, tongue=True,
                          skull_d=d, on_jaw=wax_drool)
    for side in (-1, 1):  # long fangs
        y = snout["tip"] - 0.12
        m.loft_z("Teeth", (zc - 0.22 - 0.42, side * 0.27, y, 0.03, 0.03), (zc - 0.22 + 0.08, side * 0.27, y, 0.15, 0.15))
    m.block("Accent", 0, snout["tip"] - 0.1, snout["top"](snout["tip"] - 0.1) + 0.03, 0.34, 0.18, 0.12)  # nose
    for side in (-1, 1):
        ink_eye(m, (side * 0.3, front, zc + 0.27), "y", 0.34, -side, white=False, lid=0.3, slant=1.0, brow=-0.02, lid_role="Body",
                brow_role="Accent")
        beam(m, "Accent", (side * 0.48, yc - 0.2, zc + h / 2 - 0.1), (side * 0.85, yc - 0.3, zc - 0.25), 0.34, 0.14, 0.2)  # melted ears
        icicle(m, "Accent", side * 0.85, yc - 0.3, zc - 0.2, 0.35, 0.16)
    m.block("Wick", 0, yc + 0.1, zc + h / 2 + 0.12, 0.08, 0.08, 0.28)  # a wick on its forehead, burning
    prism(m, "Flame", 0, yc + 0.1, zc + h / 2 + 0.2, zc + h / 2 + 1.0, 0.22, 0.02, 6, 0.3)
    prism(m, "FlameCore", 0, yc + 0.1, zc + h / 2 + 0.17, zc + h / 2 + 0.5, 0.26, 0.1, 6, 0.0)
    m.head_centre = (0, front + 0.35, zc)
    return grow(m, 1.12)


# ---------------------------------------------------------------------- the rare ones


def quillback():
    """A raptor bristling with giant quills: a crest of them down its back and over its head, more on its arms
    and tail, every tip dipped in glowing ink. Gold pen-nib sickle claws, a long snout full of teeth with ink
    drooling from it, and violet eyes glaring from black sockets."""
    m = monster("dino_Quillback", Body="#2c3a6e", Accent="#18204a", Belly="#e6d6ae", Claw="#1a1630", Quill=QUILL, Nib=GILT)
    m.joint("Spine", (0, 0, 2.7))
    biped_legs(m, 0.6, -0.15, 2.5, 0.72, 1.1, 0.42, 1.25, 0.26)
    for side in (-1, 1):  # a gold nib for a sickle claw on each foot
        m.bone = "ShinL" if side < 0 else "ShinR"
        sx = side * 0.6
        beam(m, "Nib", (sx, 0.45, 0.25), (sx, 0.75, 0.85), 0.18, 0.2)
        beam(m, "Nib", (sx, 0.75, 0.85), (sx, 1.05, 0.6), 0.18, 0.2, 0.04)
    m.bone = "Spine"
    body = ((-1.1, 0, 2.7, 1.1, 1.15), (1.05, 0, 3.0, 1.3, 1.4))
    m.loft_y("Body", *body)
    m.loft_y("Belly", (-0.9, 0, 2.18, 0.85, 0.16), (0.95, 0, 2.35, 1.05, 0.2))
    for k, y in enumerate((0.85, 0.5, 0.15, -0.2, -0.55, -0.9)):  # the crest of quills down its back
        z = top_of(body, y)
        height = 1.9 - 0.18 * k
        feather(m, (0, y, z - 0.08), ((-1) ** k * 0.15, y - 1.1, z + height), 0.42, (0, 1, 0), "Quill", "InkGlow", 0.3)
    tail(m, (-1.05, 2.75, 0.85, 0.85), (-4.0, 2.55, 0.16, 0.16), 3)
    for bone, y, z, rise in (("Tail1", -1.6, 2.95, 1.2), ("Tail2", -2.6, 2.85, 1.0), ("Tail3", -3.6, 2.65, 0.8)):
        m.bone = bone
        feather(m, (0, y, z - 0.05), (0, y - 1.0, z + rise), 0.36, (0, 1, 0), "Quill", "InkGlow", 0.3)
    m.bone = "Tail3"
    for side in (-1, 1):
        feather(m, (0, -3.9, 2.55), (side * 0.6, -5.0, 2.8), 0.34, (1, 0, 0), "Quill", "InkGlow", 0.3)
    m.bone = "Spine"
    for side in (-1, 1):  # small arms, quills along them, nib claws
        m.use("ArmL" if side < 0 else "ArmR", (side * 0.55, 0.85, 2.85))
        beam(m, "Body", (side * 0.55, 0.85, 2.85), (side * 0.75, 1.3, 2.2), 0.3, None, 0.24)
        beam(m, "Body", (side * 0.75, 1.3, 2.2), (side * 0.7, 1.85, 2.0), 0.24, None, 0.2)
        feather(m, (side * 0.8, 1.2, 2.3), (side * 1.0, 0.3, 1.7), 0.3, (0, 0, 1), "Quill", "InkGlow", 0.3)
        for off in (-0.08, 0.08):
            beam(m, "Nib", (side * 0.7 + off, 1.9, 2.0), (side * 0.7 + off, 2.2, 1.7), 0.1, 0.12, 0.02)
    m.bone = "Spine"

    m.use("Neck", (0, 0.95, 3.2))
    beam(m, "Body", (0, 0.95, 3.15), (0, 1.55, 4.0), 0.75, None, 0.62)
    m.stretch("Body", "Spine")
    w, d, h = 0.85, 1.05, 0.8
    yc, zc = 1.85, 4.25
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)

    def ink_drool(m, front, mouth_z, gap, lower_length):
        drips(m, ((-0.15, front + lower_length * 0.5, mouth_z - gap / 2 - 0.18, 0.45), (0.17, front + lower_length * 0.75, mouth_z - gap / 2 - 0.16, 0.3)),
              "InkGlow", 0.11)

    snout = classic_mouth(m, front, zc - 0.18, w, 1.15, 0.6, 0.24, 0.2, 0.12, tooth=0.11, per_side=6, lower_teeth=True, tongue=True,
                          skull_d=d, on_jaw=ink_drool)
    top_nostrils(m, snout, 0.15, 0.09)
    for side in (-1, 1):
        ink_eye(m, (side * (w / 2), yc + 0.2, zc + 0.12), "+x" if side > 0 else "-x", 0.42, 1, white=False, lid=0.32, slant=1.0,
                brow=0.0, brow_role="Accent")
    for dx, rise, length in ((-0.2, 1.0, 1.5), (0.2, 1.0, 1.5), (0.0, 1.45, 1.8), (-0.32, 0.6, 1.2), (0.32, 0.6, 1.2)):
        feather(m, (dx, yc - 0.1, zc + h / 2 - 0.05), (dx * 2.4, yc - length, zc + h / 2 + rise), 0.3, (0, 1, 0), "Quill", "InkGlow", 0.3)
    m.head_centre = (0, front + 0.4, zc)
    return grow(m, 1.25)


def hex_owl():
    """The library's keeper: a huge horned owl. Gold spectacles over glowing violet eyes in black sockets under a
    furious V of a brow, a hooked gold beak, horn tufts, flight feathers like pages, talons, and its chest a page
    covered in glowing writing."""
    m = monster("dino_HexOwl", Body="#5b4256", Accent="#38283a", Belly="#e8d8b0", Claw="#2a1f2a", Beak=GILT)
    rng = random.Random(5)
    m.joint("Spine", (0, 0, 2.3))
    biped_legs(m, 0.62, 0.15, 2.2, 0.95, 1.05, 0.48, 0.9, 0.28, claw=False)
    for side in (-1, 1):  # talons
        m.bone = "ShinL" if side < 0 else "ShinR"
        for off in (-0.22, 0.0, 0.22):
            x = side * 0.62 + off
            beam(m, "Claw", (x, 0.7, 0.3), (x * 1.0 + off * 0.3, 1.05, 0.06), 0.2, 0.22, 0.04)
    m.bone = "Spine"
    m.loft_z("Body", (1.8, 0, 0, 2.3, 1.9), (4.1, 0, 0.1, 2.75, 2.15))
    m.loft_z("Body", (4.1, 0, 0.1, 2.75, 2.15), (5.3, 0, 0.1, 2.25, 1.85))
    m.loft_z("Belly", (2.1, 0, 1.0, 1.75, 0.16), (4.3, 0, 1.2, 1.95, 0.16))
    for row in range(6):  # glowing writing on the page of its chest
        z = 2.4 + row * 0.32
        y = 1.0 + (z - 2.1) / 2.2 * 0.2 + 0.1
        x = -0.72 + rng.uniform(0, 0.2)
        while True:
            word = rng.uniform(0.18, 0.42)
            if x + word > 0.74:
                break
            m.block("InkGlow", x + word / 2, y, z, word, 0.06, 0.1)
            x += word + rng.uniform(0.08, 0.14)
    for side in (-1, 1):  # wings half spread, inner feathers dark, flight feathers like pages
        s = "L" if side < 0 else "R"
        root = Vector((side * 1.25, -0.1, 4.7))
        m.use("Wing" + s, tuple(root))
        elbow = Vector((side * 2.3, -0.4, 4.4))
        beam(m, "Body", tuple(root), tuple(elbow), 0.55, 0.4, 0.42)
        for k in range(4):
            p = root + (elbow - root) * (0.2 + 0.25 * k)
            feather(m, tuple(p), tuple(p + Vector((side * 0.15, -0.35, -1.9 - 0.15 * k))), 0.5, tuple(elbow - root), "Accent", "Page", 0.3)
        m.use("WingTip" + s, tuple(elbow), "Wing" + s)
        tip = Vector((side * 3.6, -0.6, 4.9))
        beam(m, "Body", tuple(elbow), tuple(tip), 0.42, 0.32, 0.2)
        for k in range(5):
            p = elbow + (tip - elbow) * (0.05 + 0.22 * k)
            feather(m, tuple(p), tuple(p + Vector((side * (0.3 + 0.15 * k), -0.4, -2.2 + 0.2 * k))), 0.55, tuple(tip - elbow), "Page", "Accent", 0.25)
    m.bone = "Spine"

    m.use("Neck", (0, 0.1, 5.2))
    m.block("Body", 0, 0.1, 5.35, 1.9, 1.6, 0.4)
    w, d, h = 2.5, 1.8, 1.85
    yc, zc = 0.25, 6.4
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    for side in (-1, 1):  # the facial disc, the eyes, the spectacles
        round_slab(m, "Belly", (side * 0.58, front + 0.02, zc + 0.05), "y", 0.66, 0.06, 12)
        ink_eye(m, (side * 0.58, front + 0.05, zc + 0.12), "y", 0.72, -side, white=False, lid=0.3, slant=1.15, brow=0.0, lid_role="Body",
                brow_role="Accent")
        hoop(m, "Gilt", side * 0.58, front + 0.32, zc + 0.1, 0.5, 0.07, "xz", 14)
        beam(m, "Gilt", (side * 1.08, front + 0.32, zc + 0.12), (side * 1.27, front - 0.5, zc + 0.15), 0.07, 0.07)
        feather(m, (side * 0.85, yc + 0.2, zc + h / 2 - 0.15), (side * 1.55, yc - 0.1, zc + h / 2 + 1.45), 0.55, (1, 0, 0), "Accent", "Body", 0.3)
    m.block("Gilt", 0, front + 0.32, zc + 0.2, 0.28, 0.07, 0.07)
    # The hooked beak, its lower half on the Jaw bone.
    m.loft_y("Beak", (front - 0.05, 0, zc - 0.25, 0.5, 0.55), (front + 0.45, 0, zc - 0.45, 0.32, 0.3))
    m.loft_z("Beak", (zc - 0.85, 0, front + 0.5, 0.06, 0.06), (zc - 0.4, 0, front + 0.48, 0.3, 0.26))
    m.use("Jaw", (0, front - 0.05, zc - 0.55), "Head")
    m.loft_y("Beak", (front - 0.05, 0, zc - 0.68, 0.42, 0.22), (front + 0.3, 0, zc - 0.72, 0.24, 0.14))
    m.block("Mouth", 0, front + 0.1, zc - 0.57, 0.3, 0.3, 0.06)
    m.block("InkGlow", 0, front + 0.05, zc - 0.56, 0.2, 0.16, 0.05)
    m.bone = "Head"
    m.head_centre = (0, front + 0.3, zc)
    return grow(m, 1.3)


def tome_tyrant():
    """The boss: a hulking beast whose head is a giant grimoire. Its covers are its jaws, pages of fangs in them and
    violet ink glowing inside, its ribbon bookmark for a tongue; violet eyes glare from under a heavy brow, a crown
    of candles burns on top and a glowing sigil on its cover. Broken shackles and chains on its wrists, gilt corners
    for armour, candles on its shoulders, a glowing eye sigil on its chest, quills down its back and a bookmark
    ribbon for a tail."""
    m = monster("dino_TomeTyrant", Body="#5a1f2e", Accent="#3a1420", Belly="#d9c49a", Claw="#efe2c4", Iron="#3a3540", Chain="#5a5366",
                Candle="#fbf6ea", Ribbon=RIBBON, Quill=QUILL)
    rng = random.Random(6)
    m.joint("Spine", (0, 0, 4.5))
    biped_legs(m, 1.15, 0.0, 4.3, 1.55, 1.95, 1.1, 1.9, 0.48)
    for side in (-1, 1):
        m.bone = "ShinL" if side < 0 else "ShinR"
        m.block("Gilt", side * 1.15, 0.05, 1.7, 1.35, 1.4, 0.3)
    m.bone = "Spine"
    m.loft_z("Body", (3.9, 0, 0.0, 3.3, 2.3), (8.2, 0, 0.35, 5.2, 3.0))
    m.loft_z("Belly", (4.1, 0, 1.22, 2.4, 0.14), (7.4, 0, 1.76, 3.0, 0.14))
    m.block("Gilt", 0, 0, 4.1, 3.45, 2.45, 0.4)  # a gilt belt
    ink_sigil(m, 0, 1.62, 6.0, 0.75)  # the glowing eye on its chest, ink cracks running from it
    for a in (0.4, 1.2, 2.0, 2.9, 3.5, 5.9):
        p = (math.cos(a) * 1.0, 1.6, 6.0 + math.sin(a) * 0.75)
        q = (math.cos(a + 0.15) * 1.45, 1.66, 6.0 + math.sin(a + 0.15) * 1.15)
        beam(m, "InkGlow", p, q, 0.08, 0.08)
    for side in (-1, 1):  # gilt corners for pauldrons, two candles burning on each
        m.block("Gilt", side * 2.4, 0.3, 8.3, 1.5, 3.1, 0.45)
        for dy, height in ((-0.6, 1.1), (0.6, 0.8)):
            candle(m, side * 2.5, 0.3 + dy, 8.52, height, 0.24, wax="Candle", flame="Flame", core="FlameCore", rng=rng, drips=2)
    for k, z in enumerate((7.7, 6.9, 6.1, 5.3)):  # quills down its back
        feather(m, (0, -1.1, z), ((-1) ** k * 0.2, -2.4, z + 1.3), 0.45, (0, 1, 0), "Quill", "InkGlow", 0.3)
    for x, y in ((-0.7, -0.5), (0.0, -0.75), (0.7, -0.5)):  # candles on its back
        candle(m, x, y, 8.15, rng.uniform(0.8, 1.3), 0.26, wax="Candle", flame="Flame", core="FlameCore", rng=rng, drips=2)
    # Arms reaching low, broken shackles on the wrists, chains hanging off them.
    for side in (-1, 1):
        m.use("ArmL" if side < 0 else "ArmR", (side * 2.6, 0.3, 7.7))
        beam(m, "Body", (side * 2.6, 0.3, 7.8), (side * 3.1, 0.8, 5.6), 1.15, None, 1.0)
        m.block("Body", side * 3.1, 0.8, 5.6, 1.0, 1.0, 1.0)
        beam(m, "Body", (side * 3.1, 0.8, 5.6), (side * 3.25, 1.4, 3.9), 1.0, None, 0.9)
        m.block("Iron", side * 3.22, 1.28, 4.35, 1.25, 1.25, 0.55)
        x, y = side * 3.5, 1.55
        for i in range(5):
            z = 4.05 - i * 0.5
            beam(m, "Chain", (x + side * 0.04 * i, y + 0.06 * i, z), (x + side * 0.04 * (i + 1), y + 0.06 * (i + 1), z - 0.5),
                 *((0.34, 0.12) if i % 2 else (0.12, 0.34)))
        hand = (side * 3.3, 1.65, 3.25)
        m.block("Body", *hand, 1.1, 1.2, 1.0)
        for off in (-0.35, 0.0, 0.35):
            m.loft_y("Claw", (hand[1] + 0.55, hand[0] + off, hand[2] - 0.2, 0.26, 0.28), (hand[1] + 1.1, hand[0] + off, hand[2] - 0.65, 0.04, 0.04))
    m.bone = "Spine"
    tail(m, (-1.0, 4.4, 1.1, 0.3), (-5.6, 0.9, 0.85, 0.14), 3, role="Ribbon")
    m.bone = "Tail3"
    for s in (-1, 1):  # its swallowtail end
        plate(m, "Ribbon", (s * 0.2, -5.5, 0.92), (s * 0.45, -6.3, 0.5), (1, 0, 0), 0.42, 0.3, 0.1)
    m.bone = "Spine"

    m.use("Neck", (0, 0.5, 8.1))
    m.loft_z("Body", (7.9, 0, 0.5, 2.4, 2.0), (8.85, 0, 0.75, 2.2, 1.8))
    m.stretch("Body", "Spine")
    # The head, a giant grimoire: the upper half on the Head bone, the lower on the Jaw.
    w, d, h = 3.4, 2.9, 2.5
    yc, zc = 1.4, 9.9
    m.head_joint(yc, d, zc, h)
    m.block("Accent", 0, yc - 1.45, zc + 0.35, 3.55, 0.6, 1.35)  # its spine, with gilt bands
    for dz in (0.0, 0.7):
        m.block("Gilt", 0, yc - 1.47, zc + dz, 3.6, 0.62, 0.16)
    m.block("Page", 0, yc + 0.1, zc + 0.45, 3.1, 2.5, 0.8)
    m.block("Body", 0, yc + 0.05, zc + 1.03, 3.45, 2.95, 0.36)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.block("Gilt", sx * 1.55, yc + 0.05 + sy * 1.3, zc + 1.03, 0.55, 0.45, 0.42)
    m.block("Gilt", 0, yc + 1.56, zc + 1.03, 0.7, 0.12, 0.42)  # the clasp
    for k in range(9):  # fangs along the upper pages
        x = -1.36 + k * 0.34
        length = 0.8 if k in (1, 7) else 0.45
        m.loft_z("Teeth", (zc + 0.08 - length - 0.1, x, yc + 1.22, 0.03, 0.03), (zc + 0.12, x, yc + 1.22, 0.28, 0.28))
    m.block("Body", 0, yc + 0.95, zc + 1.55, 3.0, 1.0, 0.75)  # the heavy brow over its eyes
    for side in (-1, 1):
        ink_eye(m, (side * 0.75, yc + 1.45, zc + 1.55), "y", 0.62, -side, white=False, lid=0.3, slant=1.15, brow=-0.02, lid_role="Body",
                brow_role="Accent")
    # The sigil on its cover, and a crown of candles.
    for side in (-1, 1):
        for p, q in (((-0.9, 0), (-0.35, side * 0.4)), ((-0.35, side * 0.4), (0.35, side * 0.4)), ((0.35, side * 0.4), (0.9, 0))):
            beam(m, "InkGlow", (p[0], yc - 0.35 + p[1], zc + 1.24), (q[0], yc - 0.35 + q[1], zc + 1.24), 0.12, 0.06)
    round_slab(m, "InkGlow", (0, yc - 0.35, zc + 1.24), "z", 0.22, 0.06)
    for x, height in ((-1.3, 1.0), (-0.65, 1.3), (0.0, 1.6), (0.65, 1.3), (1.3, 1.0)):
        candle(m, x, yc - 1.0, zc + 1.2, height, 0.24, wax="Candle", flame="Flame", core="FlameCore", rng=rng, drips=2)
    # The lower half, on the Jaw bone, hanging a little open so the ink glowing in its throat shows.
    hinge = Vector((0, yc - 1.15, zc - 0.05))
    m.use("Jaw", tuple(hinge), "Head")
    jaw = Frame(m, hinge, turn(x=-0.22))

    def j(x, y, z):  # a point given as on the closed book, in the jaw's frame
        return (x, y - hinge.y, z - hinge.z)

    jaw.box("Accent", *j(0, yc - 1.45, zc - 0.75), 3.55, 0.6, 0.95)
    jaw.box("Page", *j(0, yc + 0.1, zc - 0.5), 3.1, 2.5, 0.7)
    jaw.box("Body", *j(0, yc + 0.05, zc - 1.03), 3.45, 2.95, 0.36)
    for sx in (-1, 1):
        jaw.box("Gilt", *j(sx * 1.55, yc + 1.35, zc - 1.03), 0.55, 0.45, 0.42)
    for k in range(8):  # fangs along the lower pages, between the upper ones
        x = -1.19 + k * 0.34
        length = 0.65 if k in (0, 7) else 0.45
        jaw.beam("Teeth", j(x, yc + 1.22, zc - 0.25), j(x, yc + 1.22, zc - 0.2 + length), 0.26, 0.26, 0.03)
    jaw.box("InkGlow", *j(0, yc - 0.1, zc - 0.13), 2.6, 1.8, 0.06)  # ink glowing in its throat
    lip = Vector(jaw.at(*j(0.5, yc + 1.4, zc - 0.1)))
    limb(m, "Tongue", [jaw.at(*j(0.4, yc + 0.2, zc - 0.1)), tuple(lip), tuple(lip + Vector((0.1, 0.6, -0.85))), tuple(lip + Vector((0.2, 0.7, -2.0)))],
         0.55, 0.45)
    for x, length in ((-0.9, 0.8), (1.0, 0.55)):
        top = jaw.at(*j(x, yc + 1.45, zc - 1.19))
        icicle(m, "InkGlow", top[0], top[1], top[2], length, 0.18)
    m.bone = "Head"
    m.head_centre = (0, yc + 1.6, zc + 0.5)
    return m


ALL = [inkling, hermit_tome, wax_hound, quillback, hex_owl, tome_tyrant]


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
    build_and_render(models, RENDERS, HERE / f"{BLEND}.blend", "forbidden_library_animation_preview.mp4", sky=SKY, ground=FLOOR,
                     glow_roles=GLOW_ROLES, spacing=16, glow=GLOW)


if __name__ == "__main__":
    main()
