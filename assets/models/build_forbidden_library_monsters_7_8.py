"""Builds the Forbidden Library's 7th and 8th monsters, animates them and renders them (Blender, background mode).

    Blender -b -P build_forbidden_library_monsters_7_8.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_forbidden_library_monsters_7_8.py    (stills only)

Saves forbidden_library_monsters_7_8.blend and renders to design/world/monsters_forbidden_library_7_8/. What this batch shares is in rare_kit.py.

The owner's words for maps 10 to 12 (2026-11-06): "simple yet very very aggressive", with no accessories on them and no auras. So bare
bodies in two or three colours, nothing glowing, nothing floating, nothing thrown: big plain shapes, mouths, teeth, claws and small
furious eyes. The aggression is in the Maul bone (SWAY in DinoLifeController): every 2 seconds it throws itself forward, bites three
times and shakes what it caught.

  Bookworm  a giant worm, ink black, reared up: no face, just a round hole lined with rows of needles, and two small eyes over it
  Papercut  a gaunt thing the colour of old paper, all ribs and long thin limbs, hunched low, with razor claws and a mouth too wide

Skin roles Body, Accent, Belly and Claw take the colour mutations. Built at the first map's size. 1 Blender unit = 1 stud, models face
+Y, feet on Z = 0.
"""
import math
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402  (first: it turns the stud preview off)
from build_forest import Model  # noqa: E402
from build_spore_hollow_monsters import egg  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from rare_kit import beast_head, curve, jointed, ring_round, sabre, slit_eye, sweep, sweep_fine, swing  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_forbidden_library_7_8"
BLEND = "forbidden_library_monsters_7_8"  # for check_map.py and export_fbx.py
GLOW_ROLES = set()

FACE = {"EyeColour": "#ffd21f", "Pupil": "#0c0808", "Highlight": "#ffffff", "Socket": "#080506", "Mouth": "#2a0a12", "Tongue": "#8a2238", "Teeth": "#f2ead6"}
SKY, FLOOR = "#2a2240", "#57496e"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


def limb(m, role, points, widths, sides=10):
    """A leg or an arm through points, thick to thin, smoothed."""
    sweep_fine(m, role, [(tuple(p), w, w) for p, w in zip(points, widths)], sides=sides, per=3)


def talons(m, at, ahead, count, spread, length, width):
    """Long curved claws out of a hand or foot at `at`, hooking down."""
    c, d = Vector(at), Vector(ahead).normalized()
    for k in range(count):
        o = Vector((spread * (k - (count - 1) / 2), 0, 0))
        base = c + o
        sabre(m, "Claw", [tuple(base), tuple(base + d * length * 0.6 + o * 0.15 + Vector((0, 0, 0.1))), tuple(base + d * length + o * 0.25 - Vector((0, 0, length * 0.5)))], width, 6)


# ---------------------------------------------------------------------- Bookworm


def bookworm():
    """A giant worm reared up, its front a round hole lined with needles."""
    m = monster("dino_Bookworm", Body="#2a2036", Accent="#171220", Belly="#6a4a7a", Claw="#120d18")
    route = [(0, 8.2, 11.8), (0, 5.8, 11.8), (0, 3.4, 10.7), (0, 2.1, 8.6), (0, 1.9, 6.4), (0, 0.8, 4.8), (0, -2.0, 4.0), (2.6, -6.0, 3.9), (4.2, -10.0, 3.7), (2.4, -14.0, 3.5), (-1.6, -16.6, 3.2), (-4.2, -20.0, 2.8),
             (-3.2, -24.0, 2.3), (-0.4, -26.6, 1.6)]
    count = 66
    pts = curve(route, count)
    knots = [i * (count - 1) / (len(route) - 1) for i in range(len(route))]

    def width(i):
        u = i / (count - 1)
        base = 9.2 if u < 0.1 else 9.2 - 1.6 * (u - 0.1) / 0.3 if u < 0.4 else 7.6 - 6.4 * ((u - 0.4) / 0.6) ** 1.6
        return base * (1.08 if i % 3 == 0 else 0.95)  # the fat rings of a worm

    head_end, neck_end, maul_end, spine_end = knots[1], knots[2], knots[5], knots[6]
    bones = []
    for i in range(count):
        if i <= head_end:
            bones.append("Head")
        elif i <= neck_end:
            bones.append("Neck")
        elif i <= maul_end:
            bones.append("Maul")
        elif i <= spine_end:
            bones.append("Spine")
        else:
            bones.append(f"Slither{1 + min(7, int((i - spine_end) / (count - spine_end) * 8))}")
    m.joint("Spine", pts[int(spine_end)], "Root")
    m.joint("Maul", pts[int(maul_end)], "Spine")
    m.joint("Neck", pts[int(neck_end)], "Maul")
    m.joint("Head", pts[int(head_end)], "Neck")
    for n in range(1, 9):
        first = bones.index(f"Slither{n}")
        m.joint(f"Slither{n}", pts[first - 1], "Spine" if n == 1 else f"Slither{n - 1}")
    sweep(m, "Body", [(p, width(i), width(i)) for i, p in enumerate(pts)], bones, sides=16, under="Belly", under_faces=5, up=(0, -1, 0.1), caps=(False, True))

    # The hole: a thick lip, dark inside, needles in three rings all pointing in. The lower half is on the Jaw, so it gapes and bites.
    m.bone = "Head"
    mid = Vector((0, 8.4, 11.8))
    rx, rz = 4.5, 4.5
    m.joint("Jaw", (0, 5.2, 11.0), "Head")
    ring = [tuple(mid + Vector((math.cos(a) * rx, 0, math.sin(a) * rz))) for a in (i * math.tau / 20 for i in range(21))]
    lows = ["Jaw" if math.sin(i * math.tau / 20) < -0.02 else "Head" for i in range(21)]
    sweep(m, "Accent", [(p, 1.5, 1.5) for p in ring], lows, sides=8, caps=(False, False), up=(0, 1, 0))
    egg(m, "Mouth", tuple(mid + Vector((0, -1.5, 0))), rx * 0.96, 1.5, rz * 0.96, 14, 7)
    for row, (radius, depth, tall, count2) in enumerate(((4.3, 0.5, 2.3, 18), (3.2, -0.05, 1.9, 15), (2.1, -0.4, 1.4, 11))):
        for k in range(count2):
            a = (k + 0.5 * (row % 2)) * math.tau / count2
            d = Vector((math.cos(a), 0, math.sin(a)))
            m.bone = "Jaw" if d.z < 0 else "Head"
            base = mid + d * radius + Vector((0, depth, 0))
            sabre(m, "Teeth", [tuple(base), tuple(base - d * tall * 0.55 + Vector((0, 0.7, 0))), tuple(base - d * tall + Vector((0, 0.5, 0)))], 0.72 - 0.1 * row, 4, sides=5)
    swing(m, ["Jaw"], (0, 5.2, 11.0), -0.1)
    m.bone = "Head"
    # Two small burning eyes over the hole, under one hard fold of skin.
    for side in (-1, 1):
        at = Vector((side * 2.5, 7.0, 15.4))
        look = Vector((side * 0.3, 0.92, -0.2))
        egg(m, "Socket", tuple(at), 0.9, 0.5, 0.62, 10, 5)
        slit_eye(m, tuple(at + look * 0.2), 0.46, look, side, iris="EyeColour", lid_role="Body", top=0.56, tilt=0.9, low=0.44)
        sabre(m, "Accent", [(side * 4.0, 6.0, 16.2), (side * 2.4, 7.2, 16.1), (side * 0.2, 7.9, 15.6)], 1.0, 8, flat=1.4, power=2.0)
    m.head_centre = (0, 10.5, 11.8)
    return m


# ---------------------------------------------------------------------- Papercut


def papercut():
    """A gaunt pale thing on long thin legs, hunched low, its long arms reaching, razor claws and a mouth too wide."""
    m = monster("dino_Papercut", Body="#e6dabc", Accent="#a8977a", Belly="#c8b896", Claw="#17121a")
    m.joint("Spine", (0, -1.4, 10.0))
    m.joint("Maul", (0, 1.6, 13.8), "Spine")
    m.joint("Neck", (0, 4.2, 14.5), "Maul")
    # One body from the hips to the base of the skull, so it bends instead of stepping: pinched waist, wide shoulders, thin neck.
    rings = [((0, -2.0, 9.0), 3.4, 3.0), ((0, -1.0, 11.0), 2.2, 2.0), ((0, 0.6, 12.8), 3.8, 3.0), ((0, 2.2, 14.0), 5.8, 3.8), ((0, 3.4, 14.6), 6.0, 3.4), ((0, 4.6, 14.7), 3.0, 2.4), ((0, 5.8, 14.5), 1.9, 1.8), ((0, 7.0, 14.6), 2.6, 2.4)]
    sweep_fine(m, "Body", rings, ["Spine", "Spine", "Spine", "Maul", "Maul", "Neck", "Neck", "Neck"], sides=12, up=(0, -0.4, 1))
    for k, (y, z) in enumerate(((-1.5, 11.3), (-0.5, 12.6), (0.6, 13.9), (1.7, 15.3), (2.9, 16.0))):  # the knobs of its spine, showing through
        m.bone = "Spine" if k < 3 else "Maul"
        egg(m, "Accent", (0, y, z), 0.42, 0.5, 0.42, 8, 4)
    for letter, side in (("L", -1), ("R", 1)):
        hip = Vector((side * 1.8, -1.8, 9.6))
        knee = Vector((side * 2.8, 1.2, 6.2))
        hock = Vector((side * 2.8, -2.4, 3.2))
        m.use(f"Leg{letter}", tuple(hip))
        limb(m, "Body", [hip, hip.lerp(knee, 0.5), knee], (1.9, 1.5, 1.0))
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        foot = Vector((side * 2.9, -0.6, 0.5))
        limb(m, "Body", [knee, hock, foot, foot + Vector((0, 2.2, -0.1))], (1.0, 0.76, 0.8, 1.1))
        talons(m, foot + Vector((0, 2.2, 0)), (0, 1, -0.1), 3, 0.62, 1.6, 0.5)
    for letter, side in (("L", -1), ("R", 1)):
        shoulder, elbow, wrist = Vector((side * 3.5, 3.0, 14.4)), Vector((side * 6.4, 3.4, 9.2)), Vector((side * 5.6, 8.8, 5.6))
        m.use(f"Arm{letter}", tuple(shoulder), "Maul")
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5), elbow, elbow.lerp(wrist, 0.5), wrist], (1.5, 1.1, 0.85, 0.8, 0.74))
        hand = wrist + Vector((0, 1.0, -0.4))
        egg(m, "Body", tuple(hand), 1.0, 1.2, 0.6, 10, 5)
        talons(m, hand + Vector((0, 0.8, -0.1)), (0, 1, -0.45), 4, 0.72, 4.2, 0.62)
    m.use("Head", (0, 6.6, 13.6), "Neck")
    beast_head(m, 6.4, 13.2, 8.8, 5.8, 3.0, gape=-0.8, brow="Accent", eye=0.34, teeth=11, fang=1.2, socket=3.4)
    m.head_centre = (0, 12.0, 13.6)
    return m


ALL = [bookworm, papercut]


def main():
    rare_kit.run(ALL, RENDERS, BLEND, "forbidden_library_7_8", SKY, FLOOR, GLOW_ROLES, glow=0.0, spacing=48)


if __name__ == "__main__":
    main()
