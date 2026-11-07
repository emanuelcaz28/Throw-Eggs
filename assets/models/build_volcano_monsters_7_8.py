"""Builds the Volcano's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_volcano_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_volcano_monsters_7_8.py    (stills only)
    ONLY=magmapede QUICK=1 ...                                                (just that one)

Saves volcano_monsters_7_8.blend and renders to design/world/monsters_volcano_7_8/. The Volcano's first six are in
build_volcano.py; what this batch shares is in rare_kit.py.

The owner asked for 8 monsters a map (2026-11-06): two more each, nicer than the ones before, more aggressive map by map.
The Swamp's pair lunge at what's in front of them. These two reach further: they rear back, lunge and spit fire.

  Magmapede    a centipede as long as a street, plated in black glass with lava showing between the plates, its front third
               reared up over the rest. Sickle fangs bigger than its head, legs rippling down both sides
  Cinderdrake  a black dragon cracked with lava, wings raised, horns swept back. Its throat glows like a furnace and when it
               lunges it breathes a stream of fireballs that burst on the ground

What moves: the usual walk, idle and roar, and from rare_kit.py (SWAY in DinoLifeController): Spit1 to 6 (the fire), Strike,
Slither1 to 8 and Step1 to 8 (Magmapede's legs), Sway and Wriggle bones.

Skin roles Body, Accent, Belly and Claw take the colour mutations; wing skin, lava and the face keep theirs. EyeGlow, Furnace, Lava,
Ember and Flame glow (all already in shared/Roles.luau). Built at the first map's size. 1 Blender unit = 1 stud, models face +Y,
feet on Z = 0.
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
from rare_kit import chain, curve, frames_along, jointed, poly, sabre, sheet, slit_eye, sweep, swing  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_volcano_7_8"
BLEND = "volcano_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = {"EyeGlow", "Furnace", "Lava", "Ember", "Flame"}

FACE = {"EyeGlow": "#ffb321", "Pupil": "#160c0e", "Slit": "#160c0e", "Highlight": "#fff7dc", "Furnace": "#ff5a1f", "Mouth": "#2e1013", "Tongue": "#a8301c", "Teeth": "#fff1d6",
        "Socket": "#0f0809", "Lava": "#ff6a1a", "Ember": "#ffc23a", "Flame": "#ff8a1f"}
SKY, FLOOR = "#59403d", "#3b2d2c"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


def crack(m, points, w=0.2):
    """A glowing crack in the hide, along points."""
    for a, b in zip(points, points[1:]):
        beam(m, "Lava", a, b, w, w * 0.7, w * 0.8)


def on_tube(rings, y, angle, lift=0.03):
    """A point on a body swept along Y (rings as in sweep): angle round it, 0 at the +X side and pi/2 on top."""
    for ((_, ya, za), wa, ha), ((_, yb, zb), wb, hb) in zip(rings, rings[1:]):
        if ya <= y <= yb:
            t = (y - ya) / (yb - ya)
            w, h, z = wa + (wb - wa) * t, ha + (hb - ha) * t, za + (zb - za) * t
            return (math.cos(angle) * (w / 2 + lift), y, z + math.sin(angle) * (h / 2 + lift))
    raise ValueError(y)


def hide_cracks(m, rings, spots, rng):
    """Forked cracks running along a body: each spot is (y, angle, how long, which way along), and each throws a branch."""
    for y, angle, length, way in spots:
        pts = []
        for k in range(5):
            pts.append(on_tube(rings, y + way * length * k / 4, angle + rng.uniform(-0.2, 0.2) + 0.12 * k * (1 if k % 2 else -1)))
        crack(m, pts, 0.28)
        fork = pts[2]
        fork_angle = angle + 0.6 * (1 if angle < 1.5 else -1)
        crack(m, [fork, on_tube(rings, y + way * length * 0.75, fork_angle), on_tube(rings, y + way * length * 0.95, fork_angle + 0.25)], 0.18)


def fireball(m, n, at, size, parent="Head"):
    """One Spit bone's fire, a teardrop trailing back along Y, parked out of sight at `at` until it's thrown."""
    m.use(f"Spit{n}", at, parent)
    x, y, z = at
    sweep(m, "Flame", [((x, y - size * 1.5, z), 0.06, 0.06), ((x, y - size * 0.7, z), size * 0.9, size * 0.9), ((x, y, z), size * 1.4, size * 1.4), ((x, y + size * 0.55, z), size, size),
                       ((x, y + size * 0.8, z), 0.1, 0.1)], sides=6)


# ---------------------------------------------------------------------- Magmapede


def magmapede():
    """A lava centipede with its front third reared up, sickle fangs spread."""
    m = monster("dino_Magmapede", Body="#201a1f", Accent="#35201f", Belly="#6e2c1a", Claw="#120d0e")
    rng = random.Random(40)

    # One long body from behind the head to the tail, in plates. Its bones: Neck, Strike, Spine, then Slither1 to 8.
    route = [(0, 6.2, 12.0), (0, 4.6, 11.7), (0, 3.2, 10.5), (0, 2.5, 8.7), (0, 2.3, 6.8), (0, 1.5, 4.7), (0, -0.4, 3.0), (0.3, -3.2, 2.2), (2.0, -6.3, 2.05),
             (3.4, -9.8, 2.0), (2.4, -13.4, 1.95), (-0.8, -16.0, 1.9), (-3.4, -19.0, 1.8), (-3.3, -22.6, 1.65), (-0.9, -25.4, 1.45)]
    plates = 24
    pts = curve(route, plates + 1)
    frames = frames_along(pts, (0, -1, 0))

    def width(i):
        u = i / plates
        table = [(0, 4.4), (0.12, 4.9), (0.45, 5.3), (0.75, 4.4), (0.92, 3.0), (1.0, 1.7)]
        for (a, wa), (b, wb) in zip(table, table[1:]):
            if u <= b:
                return wa + (wb - wa) * (u - a) / (b - a)
        return 1.7

    owner = ["Neck"] * 2 + ["Strike"] * 3 + ["Spine"] * 2 + [f"Slither{1 + min(7, k // 2)}" for k in range(plates - 7)]
    m.joint("Spine", pts[7], "Root")
    m.joint("Strike", pts[5], "Spine")
    m.joint("Neck", pts[2], "Strike")
    for n in range(1, 9):
        first = owner.index(f"Slither{n}")
        m.joint(f"Slither{n}", pts[first], "Spine" if n == 1 else f"Slither{n - 1}")
        m.joint(f"Step{n}", pts[first], f"Slither{n}")

    # The lava under the plates, one tube the whole way, seen in the gaps.
    tube = [(p, width(i) * 0.84, width(i) * 0.58) for i, p in enumerate(pts)]
    sweep(m, "Lava", tube, [owner[min(i, plates - 1)] for i in range(plates + 1)], sides=8, up=(0, -1, 0))

    for i in range(plates):
        a, b = Vector(pts[i]), Vector(pts[i + 1])
        mid = (a + b) / 2
        ahead, side, normal = frames[i]
        w = width(i)
        h = w * 0.66
        back = (b - a).normalized()
        m.bone = owner[i]
        gap = (b - a).length * 0.12
        sweep(m, "Body", [(tuple(a + back * gap), w * 0.8, h * 0.78), (tuple(mid - back * 0.1), w * 1.02, h * 1.04), (tuple(b - back * gap * 1.5), w * 1.06, h * 1.08), (tuple(b - back * gap), w * 0.8, h * 0.8)],
              sides=8, up=tuple(normal), under="Belly", under_faces=3)
        rim = b - back * (gap * 1.9)
        sweep(m, "Accent", [(tuple(rim - back * 0.1), w * 1.09, h * 1.11), (tuple(rim + back * 0.12), w * 1.11, h * 1.13)], sides=8, up=tuple(normal))
        top = mid + normal * h * 0.5
        tall = 1.05 if i % 2 == 0 else 0.6
        point(m, "Claw", tuple(top - normal * 0.1), tuple(top + normal * tall + back * 0.5), 0.62)
        for s in (-1, 1):
            edge = mid + side * s * w * 0.5 + normal * h * 0.12
            point(m, "Accent", tuple(edge - side * s * 0.2), tuple(edge + side * s * 0.72 + back * 0.4), 0.5)

        # Legs: out, up over the knee and down on a black claw. On the ground they walk, up in the air they grab at nothing.
        lifted = i < 7
        if not lifted:
            m.bone = f"Step{1 + min(7, (i - 7) // 2)}"
        else:
            m.joint(f"Wriggle{i + 1}a", tuple(mid), owner[i])
            m.bone = f"Wriggle{i + 1}a"
        for s in (-1, 1):
            hip = mid + side * s * w * 0.42 - normal * h * 0.22
            if lifted:
                knee = hip + side * s * 2.0 + normal * 0.4 - back * 0.5
                foot = knee + side * s * 1.0 - normal * 0.9 - back * 1.3
            else:
                knee = hip + side * s * 2.2 + Vector((0, 0, 1.2)) + back * 0.1
                foot = Vector((*(hip + side * s * 3.7 + back * 0.5)[:2], 0.03))
            sweep(m, "Body", [(tuple(hip), 0.78, 0.78), (tuple(knee), 0.7, 0.7), (tuple(knee.lerp(foot, 0.55)), 0.46, 0.46)], sides=6)
            sabre(m, "Claw", [tuple(knee.lerp(foot, 0.5)), tuple(knee.lerp(foot, 0.8)), tuple(foot)], 0.5, 4, sides=5)
    m.bone = owner[-1]

    # The tail end: two long spines, curved like the fangs.
    end, (_, side, normal) = Vector(pts[-1]), frames[-1]
    for s in (-1, 1):
        sabre(m, "Claw", [tuple(end + side * s * 0.5), tuple(end + side * s * 1.5 + Vector((0, -2.2, 0.5))), tuple(end + side * s * 0.9 + Vector((0, -5.0, 1.4)))], 0.8, 6)

    # The head: a flat armoured wedge, level, thrust forward.
    m.use("Head", (0, 5.9, 11.9), "Neck")
    zm = 11.2
    skull = [((0, 5.6, zm + 0.9), 4.2, 2.7), ((0, 7.0, zm + 1.1), 6.0, 3.0), ((0, 8.5, zm + 1.0), 5.6, 2.5), ((0, 9.9, zm + 0.75), 4.0, 1.75), ((0, 10.8, zm + 0.55), 2.2, 1.1)]
    sweep(m, "Body", skull, sides=8)
    poly(m, "Accent", [(0, 11.0, zm + 1.2), (1.6, 8.6, zm + 2.2), (1.2, 5.9, zm + 2.5), (-1.2, 5.9, zm + 2.5), (-1.6, 8.6, zm + 2.2)], (0, 0, -0.4))
    crack(m, [(0, 6.0, zm + 2.55), (0.3, 7.2, zm + 2.5), (-0.25, 8.2, zm + 2.3), (0.05, 9.6, zm + 1.75)], 0.22)
    for side in (-1, 1):
        look = (side * 0.34, 0.93, -0.06)
        egg(m, "Socket", (side * 1.62, 9.0, zm + 1.45), 0.86, 0.9, 0.62, 10, 5)
        slit_eye(m, (side * 1.72, 9.42, zm + 1.42), 0.5, look, side, iris="EyeGlow", lid_role="Accent", top=0.5, tilt=0.7, low=0.36)
        beam(m, "Accent", (side * 3.2, 8.2, zm + 2.5), (side * 0.3, 10.5, zm + 1.5), 0.84, 0.74, 0.46)
        crack(m, [(side * 0.9, 10.4, zm + 1.02), (side * 1.3, 9.9, zm + 0.62), (side * 1.9, 10.0, zm + 0.34)], 0.14)
        point(m, "Claw", (side * 2.6, 6.6, zm + 2.2), (side * 3.4, 5.4, zm + 3.6), 0.86)
        for k in range(3):  # a row of spare eyes back along the head, like a spider's
            slit_eye(m, (side * (2.75 - 0.06 * k), 7.5 - 0.75 * k, zm + 1.7), 0.22, (side * 0.9, 0.4, 0.05), side, iris="EyeGlow", lid_role="Accent", top=0.3, tilt=0.5, low=0.2, pupil="Slit")

    # The roof of the mouth, glowing back to the throat, with needle teeth along the front.
    sweep(m, "Furnace", [((0, 6.0, zm + 0.02), 3.8, 0.2), ((0, 9.8, zm + 0.0), 3.0, 0.16), ((0, 10.8, zm + 0.1), 1.6, 0.12)], sides=8)
    egg(m, "Furnace", (0, 6.4, zm - 0.7), 1.5, 0.5, 1.0, 8, 5)
    for side in (-1, 1):
        for k in range(6):
            t = k / 5
            y, x = 7.0 + 3.7 * t, side * (2.0 - 1.15 * t * t)
            point(m, "Teeth", (x, y, zm + 0.06), (x, y + 0.04, zm - 0.5 - 0.22 * (k % 2)), 0.32)

    m.use("Jaw", (0, 5.9, zm - 0.04), "Head")
    z = zm - 0.5
    sweep(m, "Accent", [((0, 6.0, z), 4.0, 0.9), ((0, 8.6, z), 3.6, 0.8), ((0, 10.2, z + 0.05), 2.0, 0.6)], sides=8)
    sweep(m, "Furnace", [((0, 6.2, z + 0.42), 3.0, 0.1), ((0, 10.0, z + 0.34), 1.4, 0.1)], sides=8)
    for side in (-1, 1):
        for k in range(5):
            t = k / 4
            y, x = 7.0 + 3.0 * t, side * (1.65 - 0.85 * t * t)
            point(m, "Teeth", (x, y, z + 0.36), (x, y + 0.03, z + 0.82 + 0.16 * (k % 2)), 0.28)
    swing(m, ["Jaw"], (0, 5.9, zm - 0.04), -0.5)

    # The sickle fangs, each as long as the head, opened round the upright.
    for side, letter in ((-1, "L"), (1, "R")):
        pivot = (side * 2.5, 7.2, zm - 0.1)
        m.use(f"Mand{letter}", pivot, "Head")
        egg(m, "Claw", pivot, 1.1, 1.1, 0.9, 8, 4)
        sabre(m, "Body", [pivot, (side * 5.0, 8.7, zm + 0.1), (side * 6.2, 11.6, zm), (side * 5.1, 14.3, zm - 0.1)], 2.1, 8, flat=0.9, power=1.2)
        sabre(m, "Lava", [(side * 6.05, 10.4, zm + 0.02), (side * 6.05, 12.9, zm - 0.06), (side * 4.7, 14.9, zm - 0.14), (side * 2.4, 16.4, zm - 0.22)], 1.45, 8, flat=0.9, power=1.2)
        sabre(m, "Ember", [(side * 5.1, 14.1, zm - 0.1), (side * 4.1, 15.4, zm - 0.18), (side * 2.4, 16.4, zm - 0.22), (side * 0.9, 16.9, zm - 0.26)], 0.8, 6, flat=0.9, power=1.2)
        for t, tall in ((0.15, 0.6), (0.4, 0.8), (0.65, 0.7)):  # barbs on the inside edge
            y = 9.4 + 4.0 * t
            x = side * (5.0 - 1.0 * t * t)
            point(m, "Claw", (x, y, zm), (x - side * tall, y + 0.3, zm - 0.05), 0.5)

    # Feelers, whipping about.
    for n, side in ((1, -1), (2, 1)):
        pts2 = curve([(side * 1.4, 9.4, zm + 1.75), (side * 3.0, 11.0, zm + 3.4), (side * 5.5, 11.2, zm + 5.0), (side * 8.2, 9.2, zm + 5.4), (side * 10.0, 6.5, zm + 4.6)], 9)
        chain(m, "Sway", n, pts2, 0.38, 0.1, parent="Head", role="Accent")

    # Lava globs parked in its head until it spits them.
    for n, size in ((1, 1.5), (2, 1.2), (3, 0.9)):
        fireball(m, n, (0, 7.4, zm + 1.2), size)
    m.bone = "Head"
    m.head_centre = (0, 9.0, zm + 0.8)
    return m


# ---------------------------------------------------------------------- Cinderdrake


def wing(m, s, letter):
    """A dragon's wing, raised: an arm to the wrist, four long fingers, and skin stretched between them down to the body."""
    shoulder, elbow, wrist = Vector((s * 3.0, 3.0, 10.0)), Vector((s * 8.2, 0.4, 15.2)), Vector((s * 11.8, 2.6, 19.0))
    tips = [Vector((s * 19.6, 0.4, 12.0)), Vector((s * 17.6, -5.6, 7.6)), Vector((s * 12.6, -9.4, 6.4)), Vector((s * 7.4, -9.6, 7.2))]
    root = Vector((s * 2.8, -4.8, 9.2))
    m.use(f"Wing{letter}", tuple(shoulder))
    sweep(m, "Body", [(tuple(shoulder), 1.9, 1.9), (tuple(shoulder.lerp(elbow, 0.5)), 1.4, 1.4), (tuple(elbow), 1.3, 1.3)], sides=6)
    m.use(f"WingTip{letter}", tuple(elbow), f"Wing{letter}")
    sweep(m, "Body", [(tuple(elbow), 1.3, 1.3), (tuple(elbow.lerp(wrist, 0.5)), 1.0, 1.0), (tuple(wrist), 1.1, 1.1)], sides=6)
    sabre(m, "Claw", [tuple(wrist), tuple(wrist + Vector((s * 0.8, 1.2, 1.1))), tuple(wrist + Vector((s * 0.5, 2.4, 1.1)))], 0.8, 5)  # the claw on its wrist

    def rib(tip, bend, count=5):
        mid = wrist.lerp(tip, 0.5) + bend
        return [wrist.lerp(mid, 2 * t) if t < 0.5 else mid.lerp(tip, 2 * t - 1) for t in (i / (count - 1) for i in range(count))]

    fingers = [rib(tip, Vector((s * 1.4, 1.2 - 0.9 * i, 0.7 - 0.2 * i))) for i, tip in enumerate(tips)]
    for fingers_row in fingers:
        rings = [(tuple(p), 0.62 - 0.11 * k, 0.62 - 0.11 * k) for k, p in enumerate(fingers_row)]
        sweep(m, "Body", rings, sides=5)
        crack(m, [tuple(p + Vector((0, 0.05, 0.28 - 0.05 * k))) for k, p in enumerate(fingers_row[:4])], 0.14)

    # The skin: rows from the wrist out, each scalloped in between the fingers, then the part back to the body.
    rows, bones = [], []
    for a, b in zip(fingers, fingers[1:]):
        rows.append(a)
        bones.append([f"WingTip{letter}"] * 5)
        # Half way between two fingers, pulled in: the scallop.
        rows.append([p.lerp(q, 0.5).lerp(wrist, 0.26 * k / 4) for k, (p, q) in enumerate(zip(a, b))])
        bones.append([f"WingTip{letter}"] * 5)
    rows.append(fingers[-1])
    bones.append([f"WingTip{letter}"] * 5)
    edge = elbow.lerp(wrist, 0.05)
    inner_tip = fingers[-1][-1].lerp(root, 0.5).lerp(elbow, 0.2)
    rows.append([edge.lerp(inner_tip, k / 4) for k in range(5)])
    bones.append([f"WingTip{letter}", f"WingTip{letter}", f"Wing{letter}", f"Wing{letter}", f"Wing{letter}"])
    rows.append([shoulder.lerp(root, k / 4) for k in range(5)])
    bones.append(["Spine"] * 5)
    sheet(m, "Membrane", [[tuple(p) for p in row] for row in rows], bones, 0.16)
    m.bone = "Spine"


def dragon_leg(m, bone, side, y, hip_z, knee, hock, thick):
    """A heavy leg down to a clawed foot: thigh, shin and foot in one bend."""
    x = side * 3.4
    m.use(bone, (x, y, hip_z))
    top = Vector((x, y, hip_z))
    k = top + Vector((side * 0.9, knee[0], knee[1] - hip_z))
    h = Vector((x + side * 1.0, y + hock[0], hock[1]))
    foot = Vector((x + side * 1.0, y + 0.9, 0.5))
    sweep(m, "Body", [(tuple(top), thick * 1.3, thick * 1.5), (tuple(top.lerp(k, 0.6)), thick * 1.2, thick * 1.3), (tuple(k), thick, thick), (tuple(h), thick * 0.72, thick * 0.72), (tuple(foot), thick * 0.92, thick * 0.74)], sides=8)
    crack(m, [tuple(top + Vector((side * thick * 0.6, 0, -0.3))), tuple(top.lerp(k, 0.4) + Vector((side * thick * 0.62, 0.2, 0))), tuple(k + Vector((side * thick * 0.5, 0.1, 0.1)))], 0.2)
    point(m, "Claw", tuple(k + Vector((0, 0.3, 0.2))), tuple(k + Vector((side * 0.3, 1.4, 0.9))), 0.8)
    for dx in (-0.9, 0, 0.9):
        base = (foot.x + dx, foot.y + 0.4, 0.5)
        sabre(m, "Claw", [base, (base[0] + dx * 0.2, base[1] + 1.1, 0.5), (base[0] + dx * 0.3, base[1] + 1.8, 0.03)], 0.62, 5)
    m.bone = "Spine"


def cinderdrake():
    """A black dragon cracked with lava, wings raised, its throat a furnace."""
    m = monster("dino_Cinderdrake", Body="#1f1a20", Accent="#3f2b2a", Belly="#8c3a1c", Claw="#0f0b0d", Membrane="#7c1c12", Horn="#2a2226")
    m.joint("Spine", (0, -3.0, 6.6))

    # The body: deep at the chest, belly plates underneath.
    body = [((0, -7.2, 7.0), 3.6, 3.8), ((0, -4.8, 6.9), 6.2, 6.0), ((0, -1.2, 7.0), 7.0, 6.6), ((0, 2.2, 7.3), 7.0, 6.8), ((0, 4.6, 7.8), 5.4, 5.6)]
    sweep(m, "Body", body, sides=10, under="Belly", under_faces=3)
    rng = random.Random(9)
    hide_cracks(m, body, [(3.8, 0.5, 5.6, -1), (-1.0, 0.95, 4.6, -1), (2.6, 1.2, 3.6, -1)], rng)  # lava showing through the hide, each side
    mirrored = len(m.parts["Lava"][0])
    verts = m.parts["Lava"][0]
    m._add("Lava", [(-x, y, z) for x, y, z in verts], [[i for i in f[::-1]] for f in m.parts["Lava"][1]])
    for y, tall in ((4.0, 1.5), (2.2, 1.9), (0.3, 2.1), (-1.6, 2.1), (-3.5, 1.9), (-5.4, 1.5)):  # a ridge of black glass
        base = (0, y, 10.2 - 0.03 * (y + 1) ** 2 * 0.5)
        point(m, "Accent", base, (0, y - 0.9, base[2] + tall), 1.3)

    dragon_leg(m, "FrontL", -1, 3.0, 6.4, (0.5, 3.6), (-0.2, 1.5), 1.9)
    dragon_leg(m, "FrontR", 1, 3.0, 6.4, (0.5, 3.6), (-0.2, 1.5), 1.9)
    dragon_leg(m, "BackL", -1, -4.2, 6.8, (1.5, 3.8), (-0.8, 1.9), 2.4)
    dragon_leg(m, "BackR", 1, -4.2, 6.8, (1.5, 3.8), (-0.8, 1.9), 2.4)
    wing(m, -1, "L")
    wing(m, 1, "R")

    # The tail, long and tapering, spined, with a blade of black glass on the end.
    path = [(p, w, w * 0.92) for p, w in zip(curve([(0, -7.0, 6.9), (0, -10.0, 5.9), (0, -13.4, 4.6), (1.4, -16.8, 3.5), (2.2, -20.0, 2.8), (1.4, -23.0, 2.4)], 10),
                                             (3.4, 3.0, 2.6, 2.2, 1.9, 1.6, 1.3, 1.0, 0.7, 0.3))]
    bones = jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], path, under="Belly", under_faces=3)
    for i, (p, w, _) in enumerate(path[:-1]):
        m.bone = bones[i]
        base = (p[0], p[1], p[2] + w * 0.42)
        point(m, "Accent", base, (p[0], p[1] - 0.8, base[2] + 1.3 * (1 - i / 11)), 0.9 * (1 - i / 14))
    m.bone = "Tail3"
    tip = Vector(path[-1][0])
    poly(m, "Accent", [tuple(tip + Vector((0, 0.7, 0))), tuple(tip + Vector((1.5, -0.6, 0.0))), tuple(tip + Vector((0.3, -3.4, -0.1))), tuple(tip + Vector((-1.5, -0.6, 0.0)))], (0, 0, 0.3))
    crack(m, [tuple(tip + Vector((0, 0.3, 0.36))), tuple(tip + Vector((0, -2.6, 0.26)))], 0.16)
    m.bone = "Spine"

    # The neck: an S up from the chest, on Strike so it lunges.
    m.joint("Strike", (0, 4.2, 8.6), "Spine")
    m.joint("Neck", (0, 6.4, 10.9), "Strike")
    rings = [((0, 3.8, 8.0), 5.0, 5.0), ((0, 5.4, 9.2), 4.1, 4.3), ((0, 6.2, 10.8), 3.4, 3.5), ((0, 6.6, 12.4), 3.0, 3.0), ((0, 7.5, 13.7), 2.9, 2.9), ((0, 8.8, 14.3), 3.0, 2.9), ((0, 9.8, 14.4), 3.0, 2.9)]
    sweep(m, "Body", rings, ["Spine", "Strike", "Strike", "Neck", "Neck", "Neck", "Neck"], sides=8, under="Belly", under_faces=3, up=(0, -0.3, 1))
    # A burning line down its throat to the chest: the fire on its way up.
    throat = [(Vector(p) + Vector(d) * (h / 2 + 0.03), 0.5, 0.16) for (p, _, h), d in zip(rings[1:], ((0.0, 0.75, -0.66), (0.0, 0.95, -0.3), (0.0, 0.92, 0.38), (0.0, 0.5, -0.86), (0.0, 0.15, -0.99), (0.0, 0.0, -1.0)))]
    sweep(m, "Lava", [(tuple(p), w, h) for p, w, h in throat], ["Strike", "Strike", "Neck", "Neck", "Neck", "Neck"], sides=4, up=(0, 0.3, 1))
    for y, z, dy, dz, bone in ((3.6, 10.9, -0.9, 1.2, "Spine"), (4.3, 11.5, -1.1, 1.0, "Strike"), (4.5, 12.6, -1.3, 0.7, "Neck"), (4.9, 13.8, -1.2, 0.9, "Neck"), (6.0, 15.0, -0.8, 1.2, "Neck"), (7.4, 15.6, -0.5, 1.2, "Neck")):
        m.bone = bone
        point(m, "Accent", (0, y + 0.4, z - 0.4), (0, y + dy, z + dz), 1.0)

    # The head: a long wedge under a hard brow.
    m.use("Head", (0, 9.2, 14.2), "Neck")
    zm = 13.5
    skull = [((0, 8.9, zm + 1.1), 3.0, 2.7), ((0, 10.2, zm + 1.25), 4.6, 3.0), ((0, 11.7, zm + 1.1), 4.4, 2.5), ((0, 13.1, zm + 0.78), 3.0, 1.75), ((0, 14.6, zm + 0.62), 2.5, 1.35), ((0, 15.7, zm + 0.58), 2.5, 1.16), ((0, 16.5, zm + 0.42), 1.4, 0.7)]
    sweep(m, "Body", skull, sides=8)
    point(m, "Accent", (0, 15.2, zm + 1.05), (0, 15.8, zm + 2.1), 0.8)  # a horn on its nose
    point(m, "Accent", (0, 14.0, zm + 1.32), (0, 14.1, zm + 2.1), 0.6)
    for side in (-1, 1):
        look = (side * 0.5, 0.86, -0.06)
        egg(m, "Accent", (side * 1.65, 11.6, zm + 1.38), 0.74, 0.8, 0.56, 10, 5)
        slit_eye(m, (side * 1.86, 11.92, zm + 1.34), 0.48, look, side, iris="EyeGlow", lid_role="Accent", top=0.5, tilt=0.66, low=0.34)
        beam(m, "Accent", (side * 2.75, 10.7, zm + 2.3), (side * 0.42, 13.1, zm + 1.5), 0.76, 0.66, 0.42)
        egg(m, "Furnace", (side * 0.72, 16.0, zm + 0.85), 0.2, 0.16, 0.12, 6, 3)  # smoking nostrils
        # Horns swept back, a pair and a pair behind it.
        sabre(m, "Horn", [(side * 1.75, 10.0, zm + 2.2), (side * 2.6, 8.0, zm + 3.3), (side * 3.0, 5.4, zm + 4.0), (side * 2.7, 2.8, zm + 5.2)], 1.3, 9, power=1.2)
        sabre(m, "Horn", [(side * 2.3, 9.5, zm + 1.1), (side * 3.5, 7.9, zm + 1.4), (side * 4.3, 6.4, zm + 2.2)], 0.9, 6)
        for k, (y, z) in enumerate(((9.5, zm + 0.1), (10.7, zm + 0.0), (11.9, zm + 0.1))):  # cheek spikes
            point(m, "Accent", (side * 2.0, y, z + 0.4), (side * (3.2 - 0.15 * k), y - 0.9, z + 0.2), 0.62)
        crack(m, [(side * 1.95, 9.0, zm + 2.18), (side * 2.05, 9.9, zm + 1.9), (side * 2.18, 10.7, zm + 1.4)], 0.14)
    # The roof of its mouth, a furnace from front to back, and teeth.
    sweep(m, "Furnace", [((0, 9.2, zm + 0.02), 3.6, 0.2), ((0, 13.4, zm + 0.02), 2.3, 0.16), ((0, 16.2, zm + 0.1), 1.4, 0.12)], sides=8)
    egg(m, "Furnace", (0, 9.6, zm - 0.72), 1.5, 0.5, 1.05, 8, 5)
    for side in (-1, 1):
        for k in range(8):
            t = k / 7
            y, x = 10.2 + 6.0 * t, side * (1.85 - 0.75 * t * t)
            point(m, "Teeth", (x, y, zm + 0.08), (x, y + 0.04, zm - 0.5 - 0.3 * (k % 2)), 0.34)

    m.use("Jaw", (0, 9.2, zm - 0.04), "Head")
    z = zm - 0.46
    sweep(m, "Accent", [((0, 9.2, z), 3.5, 0.92), ((0, 12.2, z), 3.0, 0.82), ((0, 14.6, z + 0.02), 2.2, 0.66), ((0, 15.9, z + 0.08), 1.3, 0.46)], sides=8)
    sweep(m, "Belly", [((0, 9.2, z - 0.2), 2.7, 0.7), ((0, 13.8, z - 0.14), 1.7, 0.56)], sides=8)
    sweep(m, "Furnace", [((0, 9.4, z + 0.42), 2.7, 0.1), ((0, 15.6, z + 0.36), 1.0, 0.1)], sides=8)
    sweep(m, "Tongue", [((0, 10.2, z + 0.5), 1.5, 0.22), ((0, 13.6, z + 0.46), 1.0, 0.18), ((0, 14.8, z + 0.44), 0.4, 0.1)], sides=6)
    for side in (-1, 1):
        for k in range(7):
            t = k / 6
            y, x = 10.4 + 5.1 * t, side * (1.5 - 0.6 * t * t)
            point(m, "Teeth", (x, y, z + 0.36), (x, y + 0.03, z + 0.84 + 0.2 * (k % 2)), 0.3)
        point(m, "Accent", (side * 1.5, 11.0, z - 0.2), (side * 2.1, 10.3, z - 0.95), 0.6)
    swing(m, ["Jaw"], (0, 9.2, zm - 0.04), -0.56)

    # The fire, parked in its head until it breathes.
    for n, size in enumerate((1.5, 1.4, 1.25, 1.1, 0.95, 0.8), start=1):
        fireball(m, n, (0, 11.2, zm + 1.2), size)
    m.bone = "Head"
    m.head_centre = (0, 13.0, zm + 0.6)
    return m


ALL = [magmapede, cinderdrake]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "volcano_7_8", SKY, FLOOR, GLOW_ROLES, glow=1.0, spacing=44)


if __name__ == "__main__":
    main()
