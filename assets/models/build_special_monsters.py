"""Builds the shop's special monsters, the ones bought with Robux that earn a share of your best monster's income
(Blender, background mode). They belong to no map.

    Blender -b -P build_special_monsters.py

Saves special_monsters.blend and renders to design/world/monsters_special/.

  Gloomfin   the Game Pass shark, the most aggressive of them (owner, 2026-11-06): hunched and scarred, a mouth that is
             most of its face hanging open on crooked teeth, slit eyes under bone horns, a torn bone-edged dorsal fin,
             burning gills and slashes, foam dripping from its jaws. It floats well clear of the ground, and its Drip
             bone gives it The Weeping Dark's RAGE: it lunges and bites every 4 seconds.

The Prism Egg's three (Config/Specials), the same dark family and the same red, each with a shape of its own:

  Duskeel    150%: a serpent rearing out of a slow S, a spined red sail down its back, long barbels.
  Umbray     300%: a ray with a bat's wings on bone spars, burning veins, hook horns, a bone-tipped whip of a tail.
  Dreadlure  900%: a hulking anglerfish that is mostly mouth, rows of fangs, an eye in its throat, a lure in a cage of bone.

They have a Swim bone, so they move with The Abyss's swim and hover (DinoLifeController SWIM and HOVER): tail beats, fins
sway, and once per idle loop it rears up and lunges, jaw wide. 1 Blender unit = 1 stud, models face +Y, ground at Z = 0.
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
from build_abyss_monsters import SWIM_FRAMES, at, fin_x, jaws, monster, swim_pose, hover_pose  # noqa: E402
from build_clockwork_citadel import Frame  # noqa: E402
from build_desert import beam  # noqa: E402
from build_eclipse_temple_monsters import grow  # noqa: E402
from build_shadow_bog import limb  # noqa: E402
from build_starfall_crater import ball, gem  # noqa: E402
from build_thorn_kingdom_monsters import aim, blade, fcurves_of, glare, lash, point, thrash  # noqa: E402
from build_weeping_dark_monsters import DRIP, rage, rage_maw  # noqa: E402
from monster_stage import build_and_render, light_up, set_sky  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_special"
GLOW_ROLES = {"EyeGlow", "Glow", "Shine"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket", "Slit", "Sinew", "Drool"})
FLOAT = 3.5  # the body's middle above the ground, before the final size: well clear of it


def rounded(m, role, a, b, parent=None):
    """A body segment with its corners cut, from a wide loft and a tall one: rings are (y, z, width, height)."""
    for wide, tall in ((1, 0.68), (0.72, 1)):
        m.loft_y(role, (a[0], 0, a[1], a[2] * wide, a[3] * tall), (b[0], 0, b[1], b[2] * wide, b[3] * tall))
        if parent:
            m.stretch(role, parent)


def fin_z(m, role, points):
    """A fin rising through points (z, y, thickness, depth), curving back as it goes."""
    for a, b in zip(points, points[1:]):
        m.loft_z(role, (a[0], 0, a[1], a[2], a[3]), (b[0], 0, b[1], b[2], b[3]))


GLOOMFIN_GROW = 0.75  # "not too big" (owner): about 9 studs nose to tail


def gloomfin():
    """The Game Pass shark, the most aggressive of the family (owner, 2026-11-06): a hunched, scarred torpedo dipping its
    head at you, a mouth that is most of its face hanging open on rows of crooked teeth with a red eye burning in its
    throat, slit eyes in black sockets under hard brows and bone horns, a torn dorsal fin edged in bone, bone spikes down
    its back and tail, burning gills, slashes and claw scars, and foam dripping from the corners of its mouth. That
    Drip bone turns on The Weeping Dark's RAGE in DinoLifeController: every 4 seconds it loads up, lunges and bites,
    snaps at the air between, and its tail cracks; on top of the swim and hover with their lunge."""
    m = monster("Gloomfin", **COLOURS, Drool="#dfe4ea")
    rng = random.Random(9)
    z = FLOAT
    rings = [(0, 2.5, z + 0.1, 2.25, 2.15), (0, 1.3, z + 0.42, 2.75, 2.6), (0, 0.0, z + 0.5, 2.6, 2.5), (0, -1.3, z + 0.38, 2.1, 2.0),
             (0, -2.5, z + 0.24, 1.5, 1.45), (0, -3.5, z + 0.16, 0.95, 0.95), (0, -4.3, z + 0.14, 0.52, 0.56), (0, -4.9, z + 0.16, 0.28, 0.34)]
    bones = ["Swim", "Swim", "Swim", "Tail1", "Tail2", "Tail3", "Tail4", "Tail4"]
    m.joint("Swim", (0, 0, z), "Root")
    m.joint("Tail1", rings[2][:3], "Swim")
    m.joint("Tail2", rings[3][:3], "Tail1")
    m.joint("Tail3", rings[4][:3], "Tail2")
    m.joint("Tail4", rings[5][:3], "Tail3")
    m.bone = "Swim"
    hull(m, rings, bones, sides=(8, 6))
    embers(m, rings, bones, 1.7, 5.6, 0.55, 0.45, 0.11)
    belly_line(m, rings, bones, 0.0, 7.0)

    # Five burning gill slits a side, raked back like slashes.
    for k in range(5):
        t = 0.12 + 0.16 * k
        for side in (-1, 1):
            top, _ = on_skin(rings, t + 0.14, 34 if side > 0 else 146, 0.015)
            low, _ = on_skin(rings, t, -6 if side > 0 else 186, 0.015)
            m.bone = "Swim"
            beam(m, "Glow", tuple(low), tuple(top), 0.1, 0.05, 0.07)
    # Claw scars, pale and raked across the flanks: three on the right, two on the left.
    for side, count in ((1, 3), (-1, 2)):
        for k in range(count):
            a_, _ = on_skin(rings, 1.5 + 0.2 * k, 68 if side > 0 else 112, 0.02)
            b_, _ = on_skin(rings, 2.2 + 0.2 * k, 8 if side > 0 else 172, 0.02)
            strut(m, "Claw", a_, b_, 0.09, 0.05, bone_at(bones, 1.5 + 0.2 * k), bone_at(bones, 2.2 + 0.2 * k))

    # The dorsal fin: tall and swept back, a bone spine down its leading edge and its trailing edge torn to tatters.
    m.bone = "Swim"
    top = rings[1][2] + rings[1][4] / 2 - 0.2
    fin = [(top, -0.4, 0.3, 2.6), (top + 1.0, -1.0, 0.2, 1.5), (top + 1.9, -1.7, 0.11, 0.65), (top + 2.5, -2.3, 0.05, 0.12)]
    fin_z(m, "Body", fin)
    lead = [Vector((0, y + d / 2, h)) for h, y, _, d in fin]
    for p_, q_ in zip(lead, lead[1:]):
        strut(m, "Claw", p_ + Vector((0, 0.06, 0)), q_ + Vector((0, 0.06, 0)), 0.2, 0.12, "Swim", "Swim")
    point(m, "Claw", tuple(lead[-1]), tuple(lead[-1] + Vector((0, -0.8, 0.2))), 0.14)
    for h, y, _, d in fin[:3]:
        edge = Vector((0, y - d / 2 + 0.15, h + 0.15))
        blade(m, "Body", tuple(edge), tuple(edge + Vector((0, -0.75, -0.3))), (0, 0, 1), 0.42, 0.08)
    # Bone spikes up the back to the fin, and down the tail behind it.
    spines(m, rings, bones, [(0.25, 0.42), (0.6, 0.55)], sail=False, width=0.26)
    spines(m, rings, bones, [(3.0, 0.62), (3.6, 0.55), (4.2, 0.48), (4.8, 0.38), (5.4, 0.3), (6.0, 0.24)], sail=False, width=0.24)

    # Long pectoral fins like sickles, a bone edge in front and tatters behind, on the Fin bones.
    for side, letter in ((-1, "L"), (1, "R")):
        root, _ = on_skin(rings, 0.8, -24 if side > 0 else 204, -0.1)
        m.use(f"Fin{letter}", tuple(root), "Swim")
        elbow = root + Vector((side * 1.6, -0.45, -0.55))
        tip = root + Vector((side * 3.0, -1.9, -1.15))
        back = root + Vector((0, -1.15, 0.05))
        mid = root + Vector((side * 1.45, -1.7, -0.55))
        panel(m, "Body", [root, elbow, mid, back], 0.12)
        panel(m, "Body", [elbow, tip, tip.lerp(mid, 0.02), mid], 0.1)
        strut(m, "Claw", root, elbow, 0.22, 0.16, f"Fin{letter}", f"Fin{letter}")
        strut(m, "Claw", elbow, tip, 0.16, 0.05, f"Fin{letter}", f"Fin{letter}")
        point(m, "Claw", tuple(tip), tuple(tip + Vector((side * 0.3, -0.6, -0.1))), 0.1)
        for q in (0.35, 0.7):
            edge = back.lerp(mid, q) if q < 0.5 else mid.lerp(tip, q - 0.3)
            blade(m, "Body", tuple(edge), tuple(edge + Vector((side * 0.1, -0.6, -0.12))), (side, 0, 0), 0.36, 0.06)

    # The tail: a crescent, its top lobe longer and edged in bone.
    m.bone = "Tail4"
    end = Vector(rings[-1][:3])
    upper = end + Vector((0, -1.6, 2.3))
    blade(m, "Body", tuple(end + Vector((0, 0.7, 0.05))), tuple(upper), (0, 1, 0), 1.0, 0.16)
    blade(m, "Body", tuple(end + Vector((0, 0.5, -0.05))), tuple(end + Vector((0, -1.0, -1.45))), (0, 1, 0), 0.75, 0.14)
    strut(m, "Claw", end + Vector((0, 0.35, 0.45)), upper + Vector((0, 0.08, 0.02)), 0.16, 0.05, "Tail4", "Tail4")

    # The head, dipped at you: the mouth hanging open, a snout over it, slit eyes under bone horns.
    m.use("Head", rings[0][:3], "Swim")
    f = Frame(m, (0, 2.75, z - 0.15), aim((0, 1, -0.16)))

    def cheeks_and_throat(m_, lf, ll):
        """Skin from the upper jaw to the lower at each corner of the mouth, and from the chin back to the belly, on both
        bones so they stretch as the jaw drops: from the side the open mouth reads as a mouth, not a box hanging out."""
        for side in (-1, 1):
            panel(m_, "Accent", [f.at(side * 1.0, -0.05, 0.08), f.at(side * 0.98, 0.75, 0.1), lf.at(side * 0.9, 0.7, 0.0), lf.at(side * 0.9, -0.05, 0.0)],
                  0.06, ["Head", "Head", "Jaw", "Jaw"])
        right, _ = on_skin(rings, 0.3, -55, -0.05)
        left, _ = on_skin(rings, 0.3, 235, -0.05)
        panel(m_, "Belly", [lf.at(-0.85, 0.1, -0.4), lf.at(0.85, 0.1, -0.4), right, left], 0.08, ["Jaw", "Jaw", "Swim", "Swim"])

    rage_maw(m, f, 2.15, 2.2, 1.25, 0.28, 0.34, rng, gape=0.16, drop=0.45, upper="Accent", lower="Belly", tooth=0.42, per_side=7, eye=0.24,
             on_jaw=cheeks_and_throat, back_h=0.62)
    m.bone = "Head"
    shell(m, "Body", [(0, 2.75, 0.42, 0.5, 0.3), (0, 2.3, 0.5, 1.15, 0.62), (0, 1.5, 0.62, 1.85, 1.05), (0, 0.7, 0.72, 2.25, 1.45),
                      (0, -0.1, 0.78, 2.35, 1.8), (0, -0.5, 0.7, 2.3, 1.9)], -40, 220, 8, f=f)
    for side in (-1, 1):
        # Turned well forward, so its glare meets you from the front as well as the side.
        glare(m, f.at(side * 0.9, 1.35, 0.88), f.r @ Vector((side * 0.62, 0.7, 0.3)), 0.5, -side, slant=0.8, spikes=0)
        for k, (y0, length) in enumerate(((0.45, 1.0), (0.0, 0.7))):  # bone horns swept back off the brow
            base = Vector(f.at(side * (0.8 - 0.1 * k), y0, 1.3))
            point(m, "Claw", tuple(base), tuple(base + Vector((side * 0.3, -length, 0.45 * length))), 0.22 - 0.05 * k)
        point(m, "Claw", f.at(side * 0.22, 2.25, 0.62), f.at(side * 0.3, 2.05, 0.95), 0.13)  # knobs down the snout
    # The Drip bone, with nothing on it: the dripping foam was taken off (2026-11-09), but the bone keeps RAGE on.
    m.use("Drip", f.at(-1.0, 0.3, -0.08), "Head")
    m.bone = "Head"
    m.head_centre = tuple(f.at(0, 1.2, 0.4))
    return grow(m, GLOOMFIN_GROW)


# The Prism Egg's three. Same family as Gloomfin: near-black backs and the same red, but built the way the best monsters of
# the maps are: rounded bodies with a pale belly, the glare and the open rage_maw, bone spikes for contrast and a shape
# of their own that reads from across the arena. Their barbels are lashes, so they thrash for ever on top of the swim.
BONE, BONE_DARK, ASH = "#ddd5c2", "#9b9384", "#8b90a4"
COLOURS = dict(Body="#1c1e2b", Accent="#0e0f18", Belly=ASH, Claw=BONE, Sail="#4a1420", EyeGlow="#ff1a2e", Pupil="#16000a", Slit="#16000a",
               Socket="#07060b", Highlight="#ffd6d6", Glow="#ff2438", Shine="#ffb0a0", Mouth="#16060c", Tongue="#8c1a2c", Teeth="#f2ecdd",
               Sinew="#5e0f1c")
SPLIT = -22  # where the dark back meets the pale belly, in degrees round the body


def ring_axes(rings, k):
    """A ring's centre, and its side and lift directions, from the path through the rings' centres (x, y, z, w, h)."""
    n = len(rings)
    centre = lambda i: Vector(rings[i][:3])
    d = (centre(min(k + 1, n - 1)) - centre(max(k - 1, 0))).normalized()
    s = Vector((0, 0, 1)).cross(d)
    s = Vector((1, 0, 0)) if s.length < 1e-3 else s.normalized()
    return centre(k), s, d.cross(s)


def curve(a, sq=0.85):
    """A point round a squared-off ring."""
    c, t = math.cos(a), math.sin(a)
    return math.copysign(abs(c) ** sq, c), math.copysign(abs(t) ** sq, t)


def shell(m, role, rings, lo=0.0, hi=360.0, sides=10, bones=None, f=None):
    """A solid lofted through rings (x, y, z, width, height), front to back, following their path: the whole way round, or
    the arc from lo to hi (degrees: 0 is the right side, 90 the top), closed off flat. bones gives each ring its bone, so
    a body bends; f builds it in a turned frame."""
    whole = hi - lo >= 360
    count = sides if whole else sides + 1
    verts = []
    for k, r in enumerate(rings):
        c, s, l = ring_axes(rings, k)
        for i in range(count):
            u, v = curve(math.radians(lo + (hi - lo) * i / sides))
            p = c + s * (r[3] / 2 * u) + l * (r[4] / 2 * v)
            verts.append(f.at(*p) if f else tuple(p))
    faces = [list(range(count))[::-1], [(len(rings) - 1) * count + i for i in range(count)]]
    for k in range(len(rings) - 1):
        for i in range(count):
            j = (i + 1) % count
            faces.append([k * count + i, k * count + j, (k + 1) * count + j, (k + 1) * count + i])
    m._add(role, verts, faces)
    if bones:
        groups = m.groups[role]
        start = len(groups) - len(verts)
        for k, bone in enumerate(bones):
            groups[start + k * count:start + (k + 1) * count] = [bone] * count


def hull(m, rings, bones=None, top="Body", under="Belly", sides=(7, 5)):
    """A body: dark above, pale below."""
    shell(m, top, rings, SPLIT, 180 - SPLIT, sides[0], bones)
    shell(m, under, rings, 180 - SPLIT, 360 + SPLIT, sides[1], bones)


def on_skin(rings, t, angle, out=0.0):
    """A point on a body at ring t (a fraction is between rings), `angle` degrees round, and the way out of the skin there."""
    k = min(int(t), len(rings) - 2)
    q = t - k
    a, sa, la = ring_axes(rings, k)
    b, sb, lb = ring_axes(rings, k + 1)
    w = rings[k][3] + (rings[k + 1][3] - rings[k][3]) * q
    h = rings[k][4] + (rings[k + 1][4] - rings[k][4]) * q
    u, v = curve(math.radians(angle))
    s, l = sa.lerp(sb, q).normalized(), la.lerp(lb, q).normalized()
    normal = (s * u * h + l * v * w).normalized()
    return a.lerp(b, q) + s * (w / 2 * u) + l * (h / 2 * v) + normal * out, normal


def bone_at(bones, t):
    return bones[min(int(t + 0.5), len(bones) - 1)]


def panel(m, role, corners, thick=0.1, bones=None):
    """A thin plate through four corners, whichever way round they come. bones gives each corner its bone."""
    p = [Vector(c) for c in corners]
    n = (p[1] - p[0]).cross(p[3] - p[0])
    if n.length < 1e-6:
        n = (p[2] - p[1]).cross(p[0] - p[1])
    n.normalize()
    verts = [tuple(c - n * thick / 2) for c in p] + [tuple(c + n * thick / 2) for c in p]
    faces = [[3, 2, 1, 0], [4, 5, 6, 7]] + [[i, (i + 1) % 4, (i + 1) % 4 + 4, i + 4] for i in range(4)]
    m._add(role, verts, faces)
    if bones:
        groups = m.groups[role]
        start = len(groups) - 8
        for i, bone in enumerate(bones):
            groups[start + i] = groups[start + i + 4] = bone


def strut(m, role, a, b, w0, w1, bone_a, bone_b):
    """A beam from a to b that stays joined when its two ends are on different bones."""
    m.bone = bone_b
    beam(m, role, tuple(a), tuple(b), w0, None, w1)
    if bone_a != bone_b:
        m.stretch(role, bone_a)


def embers(m, rings, bones, t0, t1, step, reach=0.5, width=0.1):
    """The family's mark: glowing red slashes raking back along both flanks, like ribs burning through the skin."""
    t = t0
    while t < t1:
        for flip in (0, 1):
            low, high = (SPLIT + 12, 52) if not flip else (168 - SPLIT, 128)
            a, _ = on_skin(rings, t, low, 0.015)
            b, _ = on_skin(rings, t + reach, high, 0.015)
            m.bone = bone_at(bones, t + reach / 2)
            beam(m, "Glow", tuple(a), tuple(b), width, width * 0.5, width * 0.55)
        t += step


def belly_line(m, rings, bones, t0, t1, step=0.5, width=0.1):
    """A thin red line where the dark back meets the pale belly."""
    for angle in (SPLIT, 180 - SPLIT):
        t = t0
        while t < t1:
            a, _ = on_skin(rings, t, angle, 0.012)
            b, _ = on_skin(rings, min(t + step, t1), angle, 0.012)
            strut(m, "Glow", a, b, width, width, bone_at(bones, t), bone_at(bones, t + step))
            t += step


def spines(m, rings, bones, spots, sail=True, lean=0.45, width=0.3):
    """Bone spikes up the back: spots are (ring, length). A dark red sail stretches between them, and each has a glowing tip."""
    tips = []
    for t, length in spots:
        base, out = on_skin(rings, t, 90, -0.06)
        back = (Vector(rings[min(int(t) + 1, len(rings) - 1)][:3]) - Vector(rings[int(t)][:3])).normalized()
        tip = base + (out + back * lean).normalized() * length
        m.bone = bone_at(bones, t)
        point(m, "Claw", tuple(base), tuple(tip), width * (0.7 + 0.3 * min(length, 2)))
        tips.append((base, tip, m.bone))
    if sail:
        for (a, ta, ba), (b, tb, bb) in zip(tips, tips[1:]):
            mid = a.lerp(ta, 0.7), b.lerp(tb, 0.7)
            panel(m, "Sail", [a, mid[0], mid[1], b], 0.06, [ba, ba, bb, bb])


def barbel(m, n, start, points, w0, parent, bead=0.2):
    """A long whisker on three Lash bones that never stops thrashing, with a glowing bead at its tip."""
    tip = lash(m, n, [start, *points], w0, 0.05, parent=parent, role="Accent")
    ball(m, "Glow", tip.x, tip.y, tip.z, bead, 6, 4)


def duskeel():
    """A serpent rearing out of a slow S: a long ash-bellied body, a bone-spined red sail down its whole back, burning ribs,
    a thrown-open needle mouth, and long barbels trailing from its lip."""
    m = monster("Duskeel", **COLOURS)
    rng = random.Random(21)
    rings = [(0.0, 3.0, 6.0, 1.55, 1.5), (0.1, 2.1, 5.6, 1.6, 1.6), (0.35, 1.1, 5.0, 1.68, 1.68), (0.6, 0.1, 4.4, 1.72, 1.72),
             (0.75, -1.1, 3.9, 1.72, 1.72), (0.45, -2.4, 3.6, 1.66, 1.66), (-0.3, -3.6, 3.5, 1.55, 1.55), (-0.95, -4.8, 3.55, 1.38, 1.38),
             (-1.1, -6.0, 3.65, 1.18, 1.18), (-0.65, -7.2, 3.75, 0.98, 0.98), (0.1, -8.3, 3.85, 0.76, 0.76), (0.8, -9.3, 3.95, 0.52, 0.52),
             (1.05, -10.3, 4.0, 0.3, 0.3), (0.9, -11.2, 4.05, 0.1, 0.1)]
    bones = ["Neck3", "Neck2", "Neck1", "Swim", "Swim", "Swim", "Tail1", "Tail1", "Tail2", "Tail2", "Tail3", "Tail4", "Tail4", "Tail4"]
    m.joint("Swim", rings[4][:3], "Root")
    m.joint("Neck1", rings[3][:3], "Swim")
    m.joint("Neck2", rings[2][:3], "Neck1")
    m.joint("Neck3", rings[1][:3], "Neck2")
    m.joint("Tail1", rings[5][:3], "Swim")
    m.joint("Tail2", rings[7][:3], "Tail1")
    m.joint("Tail3", rings[9][:3], "Tail2")
    m.joint("Tail4", rings[10][:3], "Tail3")
    hull(m, rings, bones)
    embers(m, rings, bones, 1.2, 10.0, 0.62, 0.55, 0.13)
    belly_line(m, rings, bones, 0.0, 12.0)
    spines(m, rings, bones, [(0.4 + i * 0.74, 1.75 - abs(i - 3) * 0.1 - max(i - 6, 0) * 0.16) for i in range(15)], width=0.3)
    # The tail ends in a bone blade with a red edge.
    m.bone = "Tail4"
    tail = Vector(rings[-1][:3])
    blade(m, "Claw", tuple(tail - Vector((0, -0.6, 0))), tuple(tail + Vector((-0.1, -2.0, 0.25))), (0, 0, 1), 1.0, 0.14)
    # Small fans behind the head, on the Fin bones.
    for side, letter in ((-1, "L"), (1, "R")):
        root, _ = on_skin(rings, 1.5, 0 if side > 0 else 180, -0.1)
        m.use(f"Fin{letter}", tuple(root), "Neck2")
        for k, spread in enumerate((-0.5, -0.1, 0.32)):
            tip = root + Vector((side * (1.6 - k * 0.12), -0.55 - k * 0.3, spread * 1.5))
            blade(m, "Sail" if k != 1 else "Accent", tuple(root), tuple(tip), (0, 0.3, 1), 0.72, 0.08)
            point(m, "Claw", tuple(root), tuple(tip + (tip - root) * 0.08), 0.14)
    # The head, looking down its nose at you.
    origin = Vector((0, 3.0, 5.72))
    m.use("Head", tuple(rings[0][:3]), "Neck3")
    f = Frame(m, origin, aim((0, 1, -0.2)))
    rage_maw(m, f, 1.75, 2.45, 0.95, 0.24, 0.32, rng, gape=0.14, drop=0.56, upper="Accent", lower="Belly", tooth=0.46, per_side=6, eye=0.2)
    m.bone = "Head"
    shell(m, "Body", [(0, 2.55, 0.34, 0.62, 0.36), (0, 1.9, 0.5, 1.12, 0.74), (0, 1.0, 0.62, 1.62, 1.14), (0, 0.1, 0.68, 1.82, 1.46),
                      (0, -0.7, 0.62, 1.66, 1.6)], -42, 222, 8, f=f)
    for side in (-1, 1):
        m.bone = "Head"  # barbel() leaves m.bone on the whisker's last bone: without this the second eye and horn rode the whisker
        glare(m, f.at(side * 0.66, 1.15, 0.88), f.r @ Vector((side * 0.72, 0.62, 0.22)), 0.44, -side, slant=0.72, spikes=0)
        # Horns swept back off the skull, and a row of knobs down the snout.
        a = Vector(f.at(side * 0.55, 0.2, 1.2))
        limb(m, "Claw", [tuple(a), tuple(a + Vector((side * 0.5, -0.9, 0.5))), tuple(a + Vector((side * 0.72, -2.0, 0.72))), tuple(a + Vector((side * 0.6, -3.0, 0.5)))], 0.34, 0.05)
        point(m, "Claw", f.at(side * 0.28, 1.95, 0.72), f.at(side * 0.34, 1.75, 1.15), 0.2)
        barbel(m, 1 if side < 0 else 2, Vector(f.at(side * 0.42, 2.1, 0.12)),
               [Vector(f.at(side * 1.1, 2.3, -0.5)), Vector(f.at(side * 1.9, 1.7, -1.4)), Vector(f.at(side * 2.1, 0.8, -2.3)), Vector(f.at(side * 1.7, 0.2, -3.0))],
               0.15, "Head", 0.17)
    m.bone = "Head"
    for y in (0.55, 0.95, 1.35):  # gills, burning behind the jaw
        for side in (-1, 1):
            a, _ = on_skin(rings, 0.6 + y * 0.5, 0 if side > 0 else 180, 0.02)
            m.bone = "Neck2"
            beam(m, "Glow", tuple(a + Vector((0, -0.22, 0.42))), tuple(a - Vector((0, -0.12, 0.3))), 0.11, 0.05, 0.08)  # raked back, like slashes
    m.head_centre = tuple(f.at(0, 1.4, 0.5))
    return grow(m, 0.8)


def umbray():
    """A ray with a bat's wings: a crescent span on bone spars with a scalloped back edge and burning veins, pale beneath,
    bull-hook horns either side of a wide open mouth, a spiked spine and a long bone-tipped tail."""
    m = monster("Umbray", **COLOURS)
    rng = random.Random(33)
    z = 4.6
    rings = [(0, 3.1, z, 2.5, 0.7), (0, 2.1, z + 0.05, 3.5, 1.3), (0, 0.6, z + 0.1, 4.1, 1.7), (0, -1.0, z + 0.1, 3.5, 1.5), (0, -2.5, z + 0.05, 2.2, 1.0),
             (0, -3.6, z, 1.05, 0.56), (0, -4.3, z, 0.5, 0.3)]
    bones = ["Swim"] * 7
    m.joint("Swim", (0, 0, z), "Root")
    hull(m, rings, bones)
    spines(m, rings, bones, [(0.9 + i * 0.62, 1.5 - abs(i - 3) * 0.22) for i in range(8)], sail=False, width=0.34)
    belly_line(m, rings, bones, 0.5, 5.5)

    # The tail: a long tapering whip on the Tail bones, rising a little, barbs near the end.
    tail = [(0, -4.1, z, 0.56, 0.36), (0, -5.8, z + 0.1, 0.42, 0.3), (0, -7.6, z + 0.3, 0.32, 0.24), (0, -9.4, z + 0.6, 0.24, 0.18),
            (0, -11.0, z + 0.95, 0.16, 0.13), (0, -12.4, z + 1.3, 0.08, 0.08)]
    tail_bones = ["Swim", "Tail1", "Tail2", "Tail3", "Tail4", "Tail4"]
    for k, name in enumerate(("Tail1", "Tail2", "Tail3", "Tail4")):
        m.joint(name, tail[k][:3], "Swim" if k == 0 else f"Tail{k}")
    shell(m, "Accent", tail, sides=6, bones=tail_bones)
    m.bone = "Tail4"
    end = Vector(tail[-1][:3])
    blade(m, "Claw", tuple(end + Vector((0, 0.5, -0.1))), tuple(end + Vector((0, -2.0, 0.55))), (1, 0, 0), 0.95, 0.14)
    for k, y in enumerate((-8.2, -9.2, -10.1)):
        c = Vector((0, y, z + 0.42 + 0.17 * k * 2))
        for side in (-1, 1):
            m.bone = "Tail2" if k == 0 else "Tail3"
            point(m, "Claw", tuple(c), tuple(c + Vector((side * 0.72, -0.42, 0.14))), 0.16)
            point(m, "Glow", tuple(c + Vector((side * 0.5, -0.3, 0.1))), tuple(c + Vector((side * 0.76, -0.45, 0.15))), 0.08)

    # The wings: stations out along the span, a scallop between each pair, on two bones so they flap from the elbow.
    lead = [(1.6, 2.2, z + 0.1), (3.6, 1.9, z + 0.5), (5.6, 0.6, z + 1.1), (7.5, -1.3, z + 1.9), (9.0, -3.5, z + 2.5)]
    trail = [(1.6, -2.7, z), (3.6, -3.4, z + 0.28), (5.6, -3.9, z + 0.85), (7.5, -4.3, z + 1.65), (9.0, -3.7, z + 2.45)]
    for side, letter in ((-1, "L"), (1, "R")):
        inner, outer = f"Fin{letter}", f"FlipperF{letter}"
        mirror = lambda p: Vector((side * p[0], p[1], p[2]))
        m.joint(inner, tuple(mirror((1.6, 0.2, z))), "Swim")
        m.joint(outer, tuple(mirror((5.6, -1.6, z + 1.0))), inner)
        wing_bone = [inner, inner, inner, outer, outer]
        L, T = [mirror(p) for p in lead], [mirror(p) for p in trail]
        for i in range(4):
            top = L[i].lerp(L[i + 1], 0.5)
            scallop = T[i].lerp(T[i + 1], 0.5).lerp(top, 0.3)
            ba, bb = wing_bone[i], wing_bone[i + 1]
            for role, drop, thick in (("Body", 0.0, 0.2), ("Belly", -0.16, 0.05)):
                d = Vector((0, 0, drop))
                panel(m, role, [L[i] + d, T[i] + d, scallop + d, top + d], thick, [ba, ba, bb, bb])
                panel(m, role, [top + d, scallop + d, T[i + 1] + d, L[i + 1] + d], thick, [bb, bb, bb, bb])
            # The spar along the front, a bone rib to each back point, and veins burning between them.
            strut(m, "Claw", L[i] + Vector((0, 0.05, 0.1)), L[i + 1] + Vector((0, 0.05, 0.1)), 0.42 - i * 0.08, 0.34 - i * 0.08, ba, bb)
            strut(m, "Accent", L[i + 1].lerp(T[i + 1], 0.04) + Vector((0, 0, 0.14)), T[i + 1] + Vector((0, 0, 0.13)), 0.2, 0.08, bb, bb)
            root = L[i].lerp(T[i], 0.32) + Vector((0, 0, 0.13))
            strut(m, "Glow", root, scallop.lerp(root, 0.08) + Vector((0, 0, 0.12)), 0.12, 0.05, ba, bb)
            mid = root.lerp(T[i], 0.5).lerp(top, 0.2)
            strut(m, "Glow", mid, mid.lerp(T[i], 0.6), 0.09, 0.04, ba, ba)
            m.bone = bb
            point(m, "Claw", tuple(L[i + 1] + Vector((0, 0.1, 0.1))), tuple(L[i + 1] + Vector((side * 0.3, 0.75, 0.42))), 0.24)
        m.bone = outer
        point(m, "Claw", tuple(L[4]), tuple(L[4] + Vector((side * 1.0, -1.1, 0.5))), 0.32)

    # The head: a wide mouth, a brow of bone, and the great hooks of horn.
    m.use("Head", (0, 2.3, z), "Swim")
    f = Frame(m, (0, 2.9, z - 0.14), aim((0, 1, -0.08)))
    rage_maw(m, f, 2.7, 1.45, 2.1, 0.2, 0.3, rng, gape=0.12, drop=0.42, upper="Accent", lower="Belly", tooth=0.4, per_side=7, eye=0.2)
    m.bone = "Head"
    shell(m, "Body", [(0, 1.55, 0.3, 1.9, 0.26), (0, 0.9, 0.4, 2.55, 0.56), (0, 0.1, 0.46, 3.0, 0.82), (0, -0.8, 0.46, 3.3, 0.96)], -30, 210, 8, f=f)
    for side in (-1, 1):
        m.bone = "Head"  # barbel() leaves m.bone on the whisker's last bone: without this the second eye and horn rode the whisker
        glare(m, f.at(side * 1.05, 0.25, 0.78), f.r @ Vector((side * 0.55, 0.72, 0.42)), 0.46, -side, slant=0.72, spikes=0)
        horn = Vector(f.at(side * 1.15, 0.95, 0.3))
        limb(m, "Accent", [tuple(horn), tuple(horn + Vector((side * 0.6, 0.9, 0.05))), tuple(horn + Vector((side * 0.52, 2.0, 0.2)))], 0.62, 0.42)
        limb(m, "Claw", [tuple(horn + Vector((side * 0.52, 2.0, 0.2))), tuple(horn + Vector((side * 0.1, 2.8, 0.5))), tuple(horn + Vector((-side * 0.5, 3.05, 0.9)))], 0.42, 0.04)
        barbel(m, 1 if side < 0 else 2, Vector(f.at(side * 0.95, 1.0, -0.1)),
               [Vector(f.at(side * 1.25, 1.1, -0.9)), Vector(f.at(side * 1.45, 0.5, -1.7)), Vector(f.at(side * 1.3, -0.3, -2.3))], 0.13, "Head", 0.15)
    for y in (0.0, 0.4, 0.8, 1.2):  # the gill slits behind the mouth, under the pale belly's edge
        for side in (-1, 1):
            m.bone = "Swim"
            a = Vector((side * (1.2 + y * 0.22), 1.9 - y * 0.75, z - 0.42))
            beam(m, "Glow", tuple(a + Vector((-side * 0.28, 0, 0))), tuple(a + Vector((side * 0.32, 0.05, 0.14))), 0.1, 0.04, 0.06)
    m.head_centre = tuple(f.at(0, 0.7, 0.3))
    return grow(m, 0.95)


def dreadlure():
    """The prize. A hulking anglerfish that is mostly mouth: a jaw that drops open on rows of fangs as long as a player's arm
    with an eye burning in its throat, a pale belly, a spined sail, torn fins and a lure hung in a cage of bone, right
    where you'd look. Bigger than anything else you can buy."""
    m = monster("Dreadlure", **COLOURS)
    rng = random.Random(47)
    z = 6.4
    rings = [(0, 3.2, z, 7.2, 7.0), (0, 1.4, z + 0.1, 8.6, 8.4), (0, -0.8, z + 0.1, 8.5, 8.3), (0, -3.0, z + 0.05, 6.6, 6.6), (0, -4.8, z, 4.2, 4.4),
             (0, -6.2, z, 2.3, 2.6), (0, -7.3, z, 1.15, 1.45), (0, -7.9, z, 0.55, 0.8)]
    bones = ["Swim", "Swim", "Swim", "Tail1", "Tail2", "Tail3", "Tail4", "Tail4"]
    m.joint("Swim", (0, 0, z), "Root")
    m.joint("Tail1", rings[2][:3], "Swim")
    m.joint("Tail2", rings[3][:3], "Tail1")
    m.joint("Tail3", rings[4][:3], "Tail2")
    m.joint("Tail4", rings[5][:3], "Tail3")
    hull(m, rings, bones, sides=(9, 6))
    embers(m, rings, bones, 0.5, 5.6, 0.52, 0.42, 0.26)
    belly_line(m, rings, bones, 0.0, 6.5, 0.5, 0.2)
    spines(m, rings, bones, [(0.7 + i * 0.62, 4.2 - abs(i - 2) * 0.5 - max(i - 4, 0) * 0.3) for i in range(9)], width=0.72, lean=0.55)
    # Scars across its flanks.
    for t, angle, side in ((1.4, 52, 1), (2.3, 38, 1), (1.9, 128, -1), (3.0, 140, -1)):
        a, out = on_skin(rings, t, angle, 0.02)
        m.bone = "Swim"
        beam(m, "Belly", tuple(a + Vector((0, 1.0, 0.7))), tuple(a + Vector((0, -1.0, -0.7))), 0.16, 0.05, 0.05)
    # The tail: a fan of bone rays with torn skin between.
    base = Vector(rings[-1][:3])
    fan = [(0.95, 0.5), (0.62, 0.95), (0.25, 1.15), (-0.2, 1.1), (-0.6, 0.9), (-0.95, 0.5)]
    tips = []
    for up, reach in fan:
        tip = base + Vector((0, -reach * 4.2, up * 3.6))
        strut(m, "Claw", base, tip, 0.3, 0.05, "Tail4", "Tail4")
        tips.append(tip)
    for a, b in zip(tips, tips[1:]):
        panel(m, "Sail", [base, a.lerp(base, 0.12), a.lerp(b, 0.5).lerp(base, 0.3), b.lerp(base, 0.12)], 0.1)
    # The great fins, ragged fans on the Fin bones.
    for side, letter in ((-1, "L"), (1, "R")):
        root, _ = on_skin(rings, 2.0, 0 if side > 0 else 180, -0.2)
        root = root + Vector((0, 0, -1.3))
        m.use(f"Fin{letter}", tuple(root), "Swim")
        rays = [root + Vector((side * (4.3 - k * 0.35), -0.4 - k * 1.0, 1.5 - k * 1.1)) for k in range(5)]
        for k, tip in enumerate(rays):
            strut(m, "Claw", root, tip, 0.34, 0.06, f"Fin{letter}", f"Fin{letter}")
        for a, b in zip(rays, rays[1:]):
            panel(m, "Sail", [root, a.lerp(root, 0.1), a.lerp(b, 0.5).lerp(root, 0.34), b.lerp(root, 0.1)], 0.1)
    # The mouth.
    m.use("Head", (0, 2.6, z + 0.5), "Swim")
    f = Frame(m, (0, 3.0, z - 0.9), aim((0, 1, 0.14)))

    def chin(m_, lf, ll):
        shell(m_, "Belly", [(0, ll + 0.05, -0.55, 3.4, 0.9), (0, ll * 0.72, -0.8, 5.3, 1.9), (0, ll * 0.36, -1.05, 6.5, 2.6), (0, -0.2, -1.1, 6.9, 3.0)],
              175, 365, 8, f=lf)
        for k in range(7):  # the lip of the jaw, burning red under the teeth
            y0, y1 = ll * k / 7, ll * (k + 1) / 7
            for side in (-1, 1):
                wa = (6.1 + (3.9 - 6.1) * y0 / ll) / 2
                wb = (6.1 + (3.9 - 6.1) * y1 / ll) / 2
                lf.beam("Glow", (side * wa, y0, -0.34), (side * wb, y1, -0.34), 0.16, 0.12, 0.16)
        for k, x in enumerate((-1.5, -0.5, 0.5, 1.5)):  # bone hooks jutting from the chin
            point(m_, "Claw", lf.at(x, ll * 0.92, -0.9), lf.at(x * 1.15, ll * 1.06, -2.0 - (k % 2) * 0.4), 0.42)

    rage_maw(m, f, 7.3, 4.3, 4.6, 0.5, 0.9, rng, gape=0.5, drop=0.62, upper="Accent", lower="Accent", tooth=1.5, per_side=7, eye=0.85, jaw_long=1.14, on_jaw=chin)
    m.bone = "Head"
    shell(m, "Body", [(0, 4.45, 0.72, 3.8, 0.75), (0, 3.7, 1.15, 5.2, 1.8), (0, 2.5, 1.65, 6.4, 3.1), (0, 1.1, 2.05, 7.2, 4.3), (0, -0.3, 2.3, 7.5, 5.2)], -50, 230, 10, f=f)
    for side in (-1, 1):
        m.bone = "Head"  # barbel() leaves m.bone on the whisker's last bone: without this the second eye and horn rode the whisker
        # On the skin (the dome is 2.6 out at this height), looking out, forward and a little up.
        glare(m, f.at(side * 2.78, 2.45, 2.7), f.r @ Vector((side * 0.66, 0.58, 0.48)), 1.3, -side, slant=0.78, spikes=0)
        for t, h in ((0.8, 1.2), (1.9, 0.95)):  # bone knobs along the lip
            point(m, "Claw", f.at(side * (2.5 - t * 0.28), 2.2 + t, 2.9 - t * 0.55), f.at(side * (2.7 - t * 0.28), 2.0 + t, 2.9 - t * 0.55 + h), 0.42)
        barbel(m, 1 if side < 0 else 2, Vector(f.at(side * 3.0, 2.6, 0.5)),
               [Vector(f.at(side * 3.9, 2.8, -0.6)), Vector(f.at(side * 4.5, 2.3, -2.0)), Vector(f.at(side * 4.5, 1.5, -3.3)), Vector(f.at(side * 4.0, 1.0, -4.3))], 0.26, "Head", 0.34)
    # The lure: a jointed stalk off its brow, and a burning bulb held in a cage of bone, hanging in front of the teeth.
    brow = Vector(f.at(0, 1.8, 4.1))
    m.use("Lure", tuple(brow), "Head")
    mid = Vector(f.at(0, 4.2, 6.2))
    limb(m, "Accent", [tuple(brow - Vector((0, 0.1, 0.5))), tuple(Vector(f.at(0, 2.9, 5.6))), tuple(mid)], 0.6, 0.34)
    m.stretch("Accent", "Head")
    for q in (0.25, 0.55, 0.85):
        c = brow.lerp(mid, q)
        ball(m, "Claw", c.x, c.y, c.z + 0.2 * math.sin(q * 3), 0.36 - q * 0.1, 6, 3)
    m.use("LureTip", tuple(mid), "Lure")
    end = Vector(f.at(0, 6.7, 5.3))
    limb(m, "Accent", [tuple(mid), tuple(Vector(f.at(0, 5.8, 6.3))), tuple(end)], 0.34, 0.16)
    bulb = end - Vector((0, 0, 1.25))
    ball(m, "Glow", bulb.x, bulb.y, bulb.z, 0.72, 8, 5)
    ball(m, "Shine", bulb.x, bulb.y, bulb.z, 0.38, 6, 4)
    for k in range(5):
        a = k * math.tau / 5
        top = end + Vector((0.28 * math.cos(a), 0.28 * math.sin(a), -0.1))
        wide = bulb + Vector((1.0 * math.cos(a), 1.0 * math.sin(a), 0.1))
        limb(m, "Claw", [tuple(top), tuple(wide), tuple(bulb + Vector((0.42 * math.cos(a), 0.42 * math.sin(a), -1.05)))], 0.17, 0.03)
    m.head_centre = tuple(f.at(0, 3.0, 1.2))
    return m


ALL = [gloomfin, duskeel, umbray, dreadlure]  # studio_tidy.py reads the colours from here


def swim_and_thrash(a, f):
    swim_pose(a, f)
    extras(a, f)


def hover_and_thrash(a, f):
    hover_pose(a, f)
    extras(a, f)


def extras(a, f):
    """On top of the swim or hover, as DinoLifeController adds them: barbels (Lash bones) thrash, and a Drip bone (Gloomfin's
    foam) turns on The Weeping Dark's rage and the dripping."""
    names = {bone.name for bone in a.pose.bones}
    if any(name.startswith("Lash") for name in names):
        thrash(a, f)
    if names & DRIP.keys():
        rage(a, f)


def animate(armature):
    """The Abyss's swim and hover, with the barbels' thrashing and Gloomfin's rage on top as DinoLifeController plays them."""
    actions = kit.add_action(armature, "Swim", SWIM_FRAMES, swim_and_thrash, 2), kit.add_action(armature, "Idle", kit.IDLE_FRAMES, hover_and_thrash, 2)
    for action in actions:  # foam falls steadily, not eased between keys
        for curve in fcurves_of(action):
            if any(f'"{name}"' in curve.data_path for name in DRIP):
                for key in curve.keyframe_points:
                    key.interpolation = "LINEAR"
    return actions


def quick_preview(models, out):
    """Stills only: each model whole, side on, face on and from behind, for trying shapes. QUICK=1 QUICK_OUT=<folder>, ONLY=<name>."""
    import bpy
    scene = kit.setup_scene()
    kit.RENDERS = out
    out.mkdir(parents=True, exist_ok=True)
    animals = bpy.data.collections.new("Animals")
    scene.collection.children.link(animals)
    roots = []
    for i, model in enumerate(models):
        root = model.build(animals)
        root.location = (i * 40, 0, 0)
        roots.append(root)
    light_up(roots, GLOW_ROLES, 1.4)
    ground = bpy.data.meshes.new("Ground")
    ground.from_pydata([(-300, -300, -0.01), (400, -300, -0.01), (400, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground.materials.append(kit.material("Ground", "#3f5a4a", False))
    scene.collection.objects.link(bpy.data.objects.new("Ground", ground))
    set_sky(scene, "#2c3a52")
    bpy.context.view_layer.update()
    for model, root in zip(models, roots):
        kit.set_visible(roots, [root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 3)
        kit.shoot(scene, f"{model.name}_full", centre + Vector((0.62, 0.85, 0.32)) * reach * 0.95, centre, (760, 760), 50)
        kit.shoot(scene, f"{model.name}_side", centre + Vector((1.15, 0.02, 0.14)) * reach * 0.95, centre, (760, 760), 50)
        kit.shoot(scene, f"{model.name}_top", centre + Vector((0.02, -0.25, 1.1)) * reach * 0.95, centre, (760, 760), 50)
        head = root.location + Vector(model.head_centre)
        size = max(3.2, (high.z - low.z) * 0.5)
        kit.shoot(scene, f"{model.name}_front", head + Vector((0, 1, 0.08)) * size * 2.2, head, (760, 760), 50)
    kit.set_visible(roots, roots)
    for model in models:
        boxes = [v for vs, _ in model.parts.values() for v in vs]
        print(f"  {model.name}: {sum(len(x) - 2 for _, f in model.parts.values() for x in f)} triangles, {len(model.joints)} bones, "
              f"box {[round(min(v[i] for v in boxes), 1) for i in range(3)]} to {[round(max(v[i] for v in boxes), 1) for i in range(3)]}")


def main():
    kit.PREVIEW_STUDS = False
    only = os.environ.get("ONLY")
    makers = [make for make in ALL if not only or make.__name__ == only]
    if os.environ.get("QUICK"):
        quick_preview([make() for make in makers], Path(os.environ["QUICK_OUT"]))
        return
    build_and_render([make() for make in makers], RENDERS, HERE / "special_monsters.blend", "special_animation_preview.mp4", sky="#2c3a52",
                     ground="#3f5a4a", glow_roles=GLOW_ROLES, spacing=30, animate_fn=animate, walk_frames=SWIM_FRAMES)


if __name__ == "__main__":
    main()
