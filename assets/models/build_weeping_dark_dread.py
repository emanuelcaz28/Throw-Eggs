"""Builds The Weeping Dark's first 7 monsters, the dread set, animates them and renders them (Blender, background mode).

    Blender -b -P build_weeping_dark_dread.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_weeping_dark_dread.py    (stills only)
    ONLY=good_boy QUICK=1 ...                                               (just those)

Saves weeping_dark_dread.blend and renders to design/world/monsters_weeping_dark_dread/.

The owner, 2026-11-10: recreate the map's 7 monsters (all but Last Breath, which stays as it is in build_weeping_dark_monsters_7_8.py)
with "another design, extremely scary and aggressive with nice animations". This file replaces the six of build_weeping_dark_monsters.py
and Inconsolable. Names and ids are the same, so Config/Dinos doesn't change; the old scripts stay for the helpers other files import.

The map's rule holds: no colour at all, black, ash and bone, and red is only ever eyes. What scares is shape: bare skulls on black
bodies, mouths torn far too wide, needle teeth, too many eyes, ribs showing through, claws as long as arms. Nothing drips, puffs or
flies off them (owner, 2026-11-10). Each has its own attack, from what DinoLifeController already plays; in the game it comes once
every 10 seconds (DinoLife.attackCycle) and the monster roams in between:

  Teddy Wrecks    a rotten stitched bear on all fours, stuffing bursting from its seams, its head split ear to ear: it throws itself
                  forward, bites three times and shakes what it caught (Maul)
  Good Boy        a starved black hound with a bare skull, ribs showing, bone hackles that stand up as it rams and hooks (Gore, Quill1-8)
  Casket Case     a coffin that is a mouth, on four bone arms, eyes under the lid: leaps and comes down jaws first (Gulp)
  Wailing Widow   a tall veiled thing with four long arms that winds up and spins on its waist, claws flung out, then falls on you (Whirl)
  Death Knell     a hunched brute whose head is a bell lying on its side, the bell's mouth its mouth: lunges, bites and claws (hidden Drip, RAGE)
  Endless Grief   the thing behind the Last Door: a crawling horror with two arms held high over it that unroll, seize and drag back (Seize)
  Inconsolable    the second rarest: a giant all ribs and skull that hammers the ground with fists of bone, four blows a second (Pummel)

Glowing role: EyeGlow only. Skin roles Body, Accent, Belly and Claw take the colour mutations. 1 Blender unit = 1 stud, models face +Y,
feet on Z = 0. Plain colours, no stud image.
"""
import math
import random
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402  (first: it turns the stud preview off)
import build_forest as kit  # noqa: E402
from build_clockwork_citadel_monsters_7_8 import limb, talons  # noqa: E402
from build_forest import Model  # noqa: E402
from build_spore_hollow_monsters import egg  # noqa: E402
from build_spore_hollow_toxic import animate, grounded, leg, ooze, skin_at, stripes, tox_eye, unit  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from fierce_kit import band, fierce_head, horn, knob  # noqa: E402
from rare_kit import chain, curve, jointed, leaf, ring_round, sabre, sweep, sweep_fine  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_weeping_dark_dread"
BLEND = "weeping_dark_dread"  # for check_map.py and export_fbx.py
GLOW_ROLES = {"EyeGlow"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket", "Slit"})

BONE = "#e6e2d6"
FACE = {"Pupil": "#0a0506", "Slit": "#0a0506", "Socket": "#050506", "Highlight": "#ffffff", "EyeGlow": "#ff1616", "Mouth": "#060608", "Tongue": "#3a3638", "Teeth": "#ece8dc"}
SKY, FLOOR = "#16171d", "#3a3a40"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


def eyes(m, at, spots, lid="Body", ridge="Accent"):
    """Red eyes on a skull: spots are (t, angle, size, look, main). Both sides. Only the main pair use Pupil (the reveal aims at them)."""
    for side in (-1, 1):
        for t, a, r, look, main in spots:
            spot = at(t, a if side > 0 else math.pi - a)
            tox_eye(m, spot, r, (side * look[0], look[1], look[2]), side, socket=1.9 if main else 1.6, lid=lid, pupil="Pupil" if main else "Slit",
                    ridge=ridge if main else None, ridge_size=1.4, top=0.5 if main else 0.3, low=0.36 if main else 0.2)


def ribs(m, rings, us, bones=None, role="Claw", grow=1.05, length=0.55):
    """Ribs showing through: thin bone hoops round a body."""
    stripes(m, rings, us, role, bones, grow=grow, length=length)


def spines(m, rings, us, tall, bones=None, role="Claw", w=1.2, back=0.6):
    for k, u in enumerate(us):
        at, n = skin_at(rings, u, math.pi / 2)
        if bones:
            m.bone = bones[min(round(u), len(bones) - 1)]
        h = tall * (1 - 0.08 * k)
        horn(m, role, tuple(at - n * 0.3), tuple(at + n * h + Vector((0, -h * back, 0))), w)


def claws(m, at, ahead, count, spread, length, w, droop=0.5, role="Claw"):
    """Long claws fanned out of a hand at `at`."""
    c, d = Vector(at), unit(ahead)
    side = unit(d.cross(Vector((0, 0, 1)))) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    for k in range(count):
        o = side * spread * (k - (count - 1) / 2)
        sabre(m, role, [tuple(c + o), tuple(c + o * 1.4 + d * length * 0.55 + Vector((0, 0, length * 0.12))), tuple(c + o * 1.7 + d * length - Vector((0, 0, length * droop)))], w, 8)


# ---------------------------------------------------------------------- Teddy Wrecks


def teddy_wrecks():
    """What's left of a bear: grey cloth, black seams, stuffing coming out, and a mouth that goes right round its head."""
    m = monster("dino_TeddyWrecks", Body="#6f6c68", Accent="#141317", Belly="#a9a59c", Claw=BONE, Stuffing="#d9d6cc")
    m.joint("Spine", (0, -5.0, 8.0))
    m.joint("Maul", (0, 1.0, 9.6), "Spine")
    m.joint("Neck", (0, 4.6, 10.6), "Maul")
    m.joint("Head", (0, 6.0, 10.6), "Neck")
    rings = [((0, -11.0, 6.4), 3.0, 3.0), ((0, -9.0, 7.4), 9.6, 8.4), ((0, -5.0, 8.6), 12.6, 10.6), ((0, -1.0, 9.4), 11.6, 10.0), ((0, 2.6, 10.2), 11.0, 9.0), ((0, 5.6, 10.6), 8.0, 7.0)]
    bones = ["Spine", "Spine", "Spine", "Maul", "Maul", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=20, under="Belly", under_faces=7, per=4)
    stripes(m, rings, (1.5, 2.5, 3.5), "Accent", bones, grow=1.02, length=0.3)  # seams
    for u, a, r in ((1.5, 1.0, 1.3), (2.5, 2.3, 1.5), (3.5, 0.7, 1.2), (2.5, 0.4, 1.1), (1.5, 2.5, 1.0)):  # stuffing bursting out of them
        at, n = skin_at(rings, u, a)
        m.bone = bones[round(u)]
        for k in range(3):
            egg(m, "Stuffing", tuple(at + n * r * 0.2 + Vector((0.5 * (k - 1) * r, 0.3 * (k % 2) * r, 0))), r * 0.7, r * 0.7, r * 0.6, 8, 4)
    spines(m, rings, (1.2, 2.0, 2.9, 3.7), 2.6, bones)
    for letter, side in (("L", -1), ("R", 1)):
        leg(m, f"Front{letter}", "Maul", [(side * 5.0, 2.4, 8.4), (side * 7.6, 3.2, 5.6), (side * 7.4, 4.6, 2.6), (side * 7.2, 5.6, 1.0)], (5.2, 4.4, 3.6, 3.4), toes=0, pad=2.4)
        claws(m, (side * 7.2, 7.4, 1.4), (0, 1, -0.1), 4, 0.9, 4.6, 0.8)
        band(m, "Accent", (side * 7.5, 3.9, 4.0), 4.3, 4.3, length=0.3, bone=f"Front{letter}", tilt=(0, 0.3, -1))
        leg(m, f"Back{letter}", "Spine", [(side * 4.6, -7.6, 7.4), (side * 7.4, -6.0, 5.4), (side * 7.0, -8.0, 2.6), (side * 7.0, -6.6, 1.0)], (6.0, 5.0, 3.8, 3.6), toes=0, pad=2.6)
        claws(m, (side * 7.0, -4.6, 1.2), (0, 1, -0.1), 3, 1.0, 3.0, 0.8)
    m.bone = "Head"
    skull = [(0, 0.9, 0.0, 1.0), (0.25, 1.0, 0.0, 1.1), (0.55, 0.92, 0.0, 0.9), (0.8, 0.7, 0.0, 0.6), (1.0, 0.4, 0.04, 0.34)]
    jaw = [(0, 0.9, -0.6, 0.0), (0.3, 1.0, -0.66, 0.0), (0.65, 0.84, -0.52, 0.0), (0.9, 0.56, -0.36, 0.0), (1.0, 0.3, -0.22, -0.02)]
    y, zm, length, width, height = 5.4, 9.4, 9.0, 11.0, 5.6
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.62, lower="Body", teeth=(14, 12), tall=1.5, base=0.44, fangs=((0.86, 1.8), (0.5, 1.5)), rows=2, seed=31, t0=0.14, throat=1.1)
    eyes(m, at, [(0.52, 0.9, 0.85, (0.28, 0.95, -0.1), True), (0.34, 0.5, 0.42, (0.8, 0.5, 0.1), False)])
    for side in (-1, 1):  # ears, one torn
        c = at(0.2, 0.95 if side > 0 else math.pi - 0.95)
        egg(m, "Body", tuple(c + Vector((side * 0.8, 0, 1.2))), 2.0, 0.9, 2.0 if side > 0 else 1.2, 10, 5)
        egg(m, "Accent", tuple(c + Vector((side * 0.8, 0.5, 1.2))), 1.2, 0.6, 1.2 if side > 0 else 0.7, 8, 4)
    band(m, "Accent", (0, y + length * 0.3, zm + height * 0.52), width * 1.0, height * 1.12, length=0.3, bone="Head")  # a seam over its skull
    m.head_centre = (0, 12.0, 9.6)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Good Boy


def good_boy():
    """A starved hound: black hide over a rack of ribs, a bare skull for a head, hackles of bone."""
    m = monster("dino_GoodBoy", Body="#131317", Accent=BONE, Belly="#34343a", Claw="#d9d5c8")
    m.joint("Spine", (0, -6.0, 8.6))
    m.joint("Gore", (0, 3.0, 11.0), "Spine")
    m.joint("Neck", (0, 8.0, 10.6), "Gore")
    rings = [((0, -11.0, 8.4), 2.6, 2.6), ((0, -9.0, 9.0), 6.0, 6.6), ((0, -5.0, 9.2), 5.6, 5.6), ((0, -1.0, 10.0), 8.0, 8.4), ((0, 3.0, 11.0), 9.4, 10.0), ((0, 7.0, 11.0), 6.4, 6.6), ((0, 10.4, 9.6), 4.8, 4.8)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Gore", "Gore", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=16, under="Belly", under_faces=5, per=4)
    ribs(m, rings, (2.6, 3.0, 3.4, 3.8, 4.2, 4.6), bones)
    for n, (y, z) in enumerate(((7.4, 14.0), (5.2, 15.4), (3.0, 15.8), (0.6, 15.0), (-1.8, 13.8), (-4.2, 12.4), (-6.6, 12.2), (-8.8, 12.2)), start=1):  # hackles, lying back until it rams
        m.joint(f"Quill{n}", (0, y, z - 1.2), "Gore" if n <= 3 else "Spine")
        m.bone = f"Quill{n}"
        tall = 5.4 - 0.36 * n
        sabre(m, "Claw", [(0, y, z - 1.4), (0, y - tall * 0.55, z + tall * 0.3), (0, y - tall, z + tall * 0.36)], 1.3, 7, flat=0.6)
    for name, x, y_, front in (("FrontL", -3.6, 3.6, True), ("FrontR", 3.6, 3.6, True), ("BackL", -3.2, -8.0, False), ("BackR", 3.2, -8.0, False)):
        side = 1 if x > 0 else -1
        z = 10.0 if front else 9.0
        knee = (x + side * 1.6, y_ + (1.6 if front else 2.6), 5.6)
        hock = (x + side * 1.4, y_ + (0.0 if front else -2.4), 2.6)
        leg(m, name, "Gore" if front else "Spine", [(x, y_, z), knee, hock, (x + side * 1.4, y_ + 1.4, 0.8)], (3.6 if front else 4.4, 2.2, 1.5, 1.6), toes=3, toe=(0.7, 2.4, 0.6))
        knob(m, "Accent", Vector(knee), 1.3)
    m.bone = "Spine"
    path = [(p, w, w) for p, w in zip(curve([(0, -10.6, 8.8), (0, -14.0, 9.6), (0, -17.6, 8.0), (0, -20.4, 4.6)], 8), (2.2, 1.8, 1.5, 1.2, 1.0, 0.8, 0.6, 0.3))]
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], path, sides=8)
    m.use("Head", (0, 10.8, 8.8), "Neck")
    skull = [(0, 0.8, 0.0, 0.9), (0.2, 1.0, 0.0, 1.1), (0.42, 0.84, 0.0, 0.96), (0.66, 0.54, 0.0, 0.6), (0.9, 0.4, 0.0, 0.44), (1.0, 0.22, 0.05, 0.24)]
    jaw = [(0, 0.76, -0.44, 0.0), (0.34, 0.7, -0.4, 0.0), (0.68, 0.44, -0.3, 0.0), (0.92, 0.3, -0.22, 0.0), (1.0, 0.14, -0.14, -0.02)]
    y, zm, length, width, height = 10.4, 7.6, 10.0, 6.4, 3.8
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.6, upper="Accent", lower="Accent", teeth=(11, 10), tall=1.2, base=0.34, fangs=((0.86, 2.6), (0.6, 1.5)), low_fangs=((0.8, 2.0),), seed=33, t0=0.22)
    eyes(m, at, [(0.36, 0.72, 0.62, (0.36, 0.92, -0.06), True), (0.22, 0.4, 0.3, (0.9, 0.4, 0.0), False)], lid="Accent", ridge="Accent")
    for side in (-1, 1):
        ear = at(0.12, 1.1 if side > 0 else math.pi - 1.1)
        leaf(m, "Body", tuple(ear - Vector((0, 0, 0.4))), tuple(ear + Vector((side * 1.6, -3.4, 4.4))), (1, 0.2, 0), 2.2, thick=0.3)
        egg(m, "Socket", tuple(at(0.95, 1.2 if side > 0 else math.pi - 1.2)), 0.36, 0.3, 0.2, 8, 4)
    m.head_centre = (0, 17.0, 8.0)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Casket Case


def casket_case():
    """A coffin, lid for a skull and box for a jaw, carried at a run on four bone arms."""
    m = monster("dino_CasketCase", Body="#242328", Accent="#77757b", Belly="#b9b4aa", Claw=BONE)
    m.joint("Spine", (0, -6.0, 9.0))
    m.joint("Gulp", (0, -3.0, 10.0), "Spine")
    m.joint("Neck", (0, -1.6, 10.2), "Gulp")
    m.joint("Head", (0, -0.6, 10.2), "Neck")
    rump = [((0, -9.6, 9.0), 2.0, 2.0), ((0, -8.0, 9.6), 6.0, 5.0), ((0, -4.0, 10.2), 8.6, 6.4), ((0, -0.4, 10.4), 9.6, 6.6)]
    sweep_fine(m, "Body", rump, ["Spine", "Spine", "Gulp", "Gulp"], sides=14, per=3)
    for name, x, y_, front in (("FrontL", -5.0, 2.0, True), ("FrontR", 5.0, 2.0, True), ("BackL", -4.0, -6.6, False), ("BackR", 4.0, -6.6, False)):
        side = 1 if x > 0 else -1
        hip = Vector((x, y_, 9.4))
        knee = hip + Vector((side * 5.4, 1.0 if front else -1.6, 5.0))
        foot = Vector((x + side * 5.6, y_ + (3.0 if front else 0.0), 0.5))
        leg(m, name, "Gulp" if front else "Spine", [hip, hip.lerp(knee, 0.5), knee, knee.lerp(foot, 0.5) + Vector((side * 0.6, 0, 0)), foot], (2.6, 2.0, 1.6, 1.3, 1.0), role="Claw", toes=0)
        knob(m, "Claw", knee, 1.4)
        claws(m, foot + Vector((0, 0.4, 0.5)), (0, 1, 0), 4, 0.7, 3.4, 0.6, droop=0.12)
    m.bone = "Spine"
    links = curve([(0, -9.4, 9.0), (0, -12.0, 7.4), (0, -15.0, 4.0), (0, -18.0, 1.2)], 7)
    jointed(m, "Accent", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(links, (1.6, 1.4, 1.3, 1.2, 1.1, 1.0, 1.4))], sides=6)
    m.bone = "Head"
    # A coffin seen from above: narrow at the head end, widest at the shoulders, tapering to the foot. Flat lid, flat floor.
    skull = [(0, 0.62, 0.0, 0.5), (0.06, 0.66, 0.0, 0.62), (0.26, 1.0, 0.0, 0.66), (0.6, 0.8, 0.0, 0.62), (0.94, 0.58, 0.0, 0.56), (1.0, 0.54, 0.0, 0.4)]
    jaw = [(0, 0.62, -0.8, 0.0), (0.06, 0.66, -0.9, 0.0), (0.26, 1.0, -0.94, 0.0), (0.6, 0.8, -0.9, 0.0), (0.94, 0.58, -0.84, 0.0), (1.0, 0.54, -0.7, 0.0)]
    y, zm, length, width, height = -1.0, 10.6, 20.0, 12.0, 5.6
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.36, lower="Body", inside="Belly", teeth=(20, 18), tall=2.0, base=0.5, fangs=((0.9, 1.6), (0.55, 1.4), (0.3, 1.3)), rows=2, seed=35,
                     t0=0.1, throat=0.9, tongue_long=0.9, jaw_length=1.0)
    egg(m, "Mouth", (0, y + length * 0.16, zm - 0.6), width * 0.3, 2.4, height * 0.5, 12, 6)
    for t in (0.2, 0.5, 0.8):  # iron straps over the lid
        hw = width / 2 * (1.0 if t == 0.2 else 0.86 if t == 0.5 else 0.68)
        band(m, "Accent", (0, y + length * t, zm + height * 0.33), hw * 2.04, height * 0.72, length=0.9, bone="Head")
    for side in (-1, 1):
        for t in (0.36, 0.66):  # handles
            c = at(t, 0.12 if side > 0 else math.pi - 0.12) + Vector((side * 0.5, 0, 0))
            ring_round(m, "Accent", tuple(c), 1.1, (side, 0, 0), 0.36, 10)
    eyes(m, at, [(0.9, 0.5, 0.8, (0.3, 0.95, 0.0), True), (0.97, 1.1, 0.5, (0.1, 1, 0.1), False), (0.72, 0.3, 0.5, (0.9, 0.4, 0.0), False), (0.5, 0.3, 0.42, (1, 0.1, 0.0), False)], ridge="Accent")
    m.head_centre = (0, 20.0, 10.0)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Wailing Widow


def widow_arm(m, bone, shoulder, elbow, wrist, widths, claw):
    s, e, w_ = Vector(shoulder), Vector(elbow), Vector(wrist)
    m.use(bone, tuple(s), "Whirl")
    knob(m, "Belly", s, widths[0] * 0.62)
    limb(m, "Belly", [s, s.lerp(e, 0.5), e, e.lerp(w_, 0.5), w_], widths, sides=10)
    knob(m, "Claw", e, widths[2] * 0.75)
    claws(m, w_, (0, 1, -0.5), 4, widths[4] * 0.42, claw, widths[4] * 0.42, droop=0.6)


def wailing_widow():
    """Tall, veiled, no feet to be seen: a ragged black skirt, a waist like a wrist, four arms, and a skull screaming under the veil."""
    m = monster("dino_WailingWidow", Body="#0d0d11", Accent="#34333a", Belly="#cfcbc0", Claw="#e9e5da")
    rng = random.Random(154)
    m.joint("Spine", (0, 0, 10.0))
    m.joint("Whirl", (0, 0, 11.0), "Spine")
    # The skirt: a bell of rags down to the ground, and the bowl of hips the waist turns in.
    sweep_fine(m, "Body", [((0, 0, 1.2), 12.6, 11.6), ((0, 0, 4.0), 10.4, 9.6), ((0, 0, 8.0), 7.4, 6.6), ((0, 0, 10.6), 6.4, 5.6), ((0, 0, 11.8), 4.6, 4.4)], ["Spine"] * 5, up=(0, -1, 0.05), sides=18)
    for k in range(16):  # the hem, in tatters
        a = k * math.tau / 16 + rng.uniform(-0.1, 0.1)
        base = Vector((math.cos(a) * 5.9, math.sin(a) * 5.4, 2.4))
        leaf(m, "Accent" if k % 3 == 0 else "Body", tuple(base), tuple(base + Vector((math.cos(a) * 1.6, math.sin(a) * 1.6, -2.3))), (-math.sin(a), math.cos(a), 0), 2.6, thick=0.3)
    m.bone = "Whirl"
    torso = [((0, 0, 10.4), 2.4, 2.4), ((0, 0, 12.6), 3.0, 3.0), ((0, 0.3, 15.0), 5.0, 3.8), ((0, 0.9, 17.6), 8.6, 5.0), ((0, 1.6, 19.6), 10.4, 5.4), ((0, 2.4, 21.0), 5.6, 4.2)]
    sweep_fine(m, "Body", torso, ["Whirl"] * 6, up=(0, -1, 0.1), sides=18, per=4)
    for z, w, d, yy in ((14.4, 4.9, 3.9, 0.2), (15.6, 6.0, 4.3, 0.45), (16.8, 7.6, 4.8, 0.7), (18.0, 9.2, 5.3, 1.0)):  # ribs
        sweep(m, "Claw", [((0, yy, z - 0.22), w, d), ((0, yy, z + 0.22), w, d)], sides=14, up=(0, -1, 0.05))
    for k, z in enumerate((13.0, 15.0, 17.0, 19.0)):  # its spine standing out of its back
        point(m, "Claw", (0, -1.2 - 0.3 * k, z), (0, -4.4 - 0.4 * k, z + 1.4), 1.3)
    for letter, side in (("L", -1), ("R", 1)):
        widow_arm(m, f"Arm{letter}", (side * 5.0, 1.6, 19.6), (side * 10.4, 0.6, 14.0), (side * 9.0, 7.0, 8.0), (2.2, 1.8, 1.5, 1.3, 1.5), 5.6)
        widow_arm(m, f"Wing{letter}", (side * 3.4, 1.2, 16.4), (side * 7.6, 2.6, 13.6), (side * 6.4, 8.0, 13.0), (1.7, 1.4, 1.2, 1.0, 1.2), 4.4)
    m.use("Neck", (0, 2.4, 20.6), "Whirl")
    sweep_fine(m, "Belly", [((0, 2.2, 20.4), 2.4, 2.4), ((0, 3.2, 22.0), 2.0, 2.0), ((0, 4.0, 23.0), 2.4, 2.4)], sides=10, up=(0, -1, 0.1))
    m.use("Head", (0, 3.8, 22.8), "Neck")
    skull = [(0, 0.8, 0.0, 1.0), (0.22, 1.0, 0.0, 1.3), (0.46, 0.9, 0.0, 1.2), (0.7, 0.6, 0.0, 0.8), (0.92, 0.4, 0.0, 0.46), (1.0, 0.2, 0.05, 0.24)]
    jaw = [(0, 0.72, -0.4, 0.0), (0.36, 0.66, -0.36, 0.0), (0.7, 0.44, -0.28, 0.0), (0.94, 0.28, -0.2, 0.0), (1.0, 0.12, -0.12, -0.02)]
    y, zm, length, width, height = 3.4, 22.0, 7.4, 5.8, 3.4
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.95, upper="Belly", lower="Belly", teeth=(10, 9), tall=1.2, base=0.3, fangs=((0.88, 2.0),), seed=37, t0=0.24, jaw_length=1.08)
    eyes(m, at, [(0.5, 0.8, 0.6, (0.3, 0.94, -0.12), True)], lid="Belly", ridge="Body")
    # The veil: a hood over the back of its skull, and strips of it hanging and swaying.
    hood = at(0.2, math.pi / 2)
    egg(m, "Accent", (0, hood.y - 0.9, hood.z - 1.2), width * 0.66, 3.4, height * 0.98, 14, 7)
    for n, (side, back) in enumerate(((-1, 0), (1, 0), (-1, 1), (1, 1), (0, 2)), start=1):
        root = Vector((side * (2.9 - 0.6 * back), hood.y - 1.0 - 1.2 * back, hood.z - 1.4))
        pts = curve([root, root + Vector((side * 1.2, -1.0, -3.0)), root + Vector((side * 1.8, -1.6, -6.4)), root + Vector((side * 1.6, -1.2, -9.6))], 7)
        chain(m, "Sway", n, pts, 0.24, 0.16, parent="Head", role="Accent", flat="side", breadth=2.6)
        m.bone = "Head"
    m.head_centre = (0, 8.6, 22.6)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Death Knell


def death_knell():
    """A hunched brute whose head is a great bell lying on its side: the bell's mouth is its mouth, its clapper the tongue."""
    m = monster("dino_DeathKnell", Body="#2b2b31", Accent="#5c5b63", Belly="#8b8880", Claw=BONE)
    m.joint("Spine", (0, -2.0, 11.0))
    m.joint("Neck", (0, 3.8, 15.4), "Spine")
    m.joint("Head", (0, 5.0, 15.0), "Neck")
    trunk = [((0, -5.6, 8.6), 5.0, 4.6), ((0, -4.0, 10.4), 9.6, 8.0), ((0, -1.6, 13.0), 12.6, 9.6), ((0, 1.4, 15.6), 15.0, 10.0), ((0, 4.0, 16.0), 11.0, 8.0)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Neck"]
    sweep_fine(m, "Body", trunk, bones, sides=18, under="Belly", under_faces=5, per=4)
    ribs(m, trunk, (1.4, 1.8, 2.2, 2.6), bones)
    spines(m, trunk, (1.2, 2.0, 2.8, 3.5), 3.4, bones, w=1.6, back=0.2)
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee, ankle, foot = Vector((side * 3.6, -4.2, 9.4)), Vector((side * 5.6, -0.6, 5.6)), Vector((side * 5.2, -4.4, 2.4)), Vector((side * 5.4, -2.6, 0.9))
        m.use(f"Leg{letter}", tuple(hip))
        knob(m, "Body", hip, 3.0)
        limb(m, "Body", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.5, 0.3, 0.4)), knee], (5.4, 4.6, 3.2), sides=12)
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        knob(m, "Accent", knee, 1.9)
        limb(m, "Body", [knee, knee.lerp(ankle, 0.5) + Vector((0, -0.5, 0)), ankle, foot, foot + Vector((0, 2.8, -0.1))], (3.0, 2.4, 2.0, 2.2, 2.6), sides=10)
        talons(m, foot + Vector((0, 3.2, 0)), (0, 1, -0.15), 3, 1.1, 3.0, 1.0)
        shoulder, elbow, wrist = Vector((side * 7.4, 1.6, 15.6)), Vector((side * 11.6, 2.6, 9.4)), Vector((side * 10.2, 7.6, 4.4))
        m.use(f"Arm{letter}", tuple(shoulder))
        knob(m, "Body", shoulder + Vector((side * 0.4, 0, 0.6)), 3.8)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5) + Vector((side * 0.6, 0, 0.3)), elbow, elbow.lerp(wrist, 0.5), wrist], (6.0, 5.4, 4.2, 3.8, 3.6), sides=12)
        band(m, "Accent", tuple(elbow.lerp(wrist, 0.7)), 4.4, 4.4, length=1.3, tilt=tuple(wrist - elbow))  # a shackle
        point(m, "Claw", tuple(elbow), tuple(elbow + Vector((side * 2.0, -3.0, 2.0))), 2.0)
        claws(m, wrist + Vector((0, 0.6, -0.4)), (0, 1, -0.45), 4, 1.0, 6.4, 1.0, droop=0.4)
    m.bone = "Head"
    # The bell: narrow crown at the back, flaring to the lip at the front.
    skull = [(0, 0.36, 0.0, 0.5), (0.12, 0.56, 0.0, 0.8), (0.4, 0.68, 0.0, 0.94), (0.72, 0.78, 0.0, 1.0), (0.9, 0.94, 0.0, 1.12), (1.0, 1.0, 0.0, 1.16)]
    jaw = [(0, 0.36, -0.4, 0.0), (0.12, 0.56, -0.62, 0.0), (0.4, 0.68, -0.74, 0.0), (0.72, 0.78, -0.8, 0.0), (0.9, 0.94, -0.9, 0.0), (1.0, 1.0, -0.94, 0.0)]
    y, zm, length, width, height = 4.6, 13.6, 11.0, 11.6, 5.4
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.4, upper="Accent", lower="Accent", teeth=(16, 14), tall=1.9, base=0.5, fangs=((0.9, 1.5), (0.6, 1.4)), rows=2, seed=39, t0=0.3,
                     tongue=False, throat=0.9)
    for t in (0.34, 0.86):  # the bands cast round a bell
        hw = width / 2 * (0.66 if t < 0.5 else 0.9)
        band(m, "Body", (0, y + length * t, zm + height * (0.47 if t < 0.5 else 0.54)), hw * 2.08, height * (0.98 if t < 0.5 else 1.14), length=0.7, bone="Head")
    m.bone = "Jaw"
    sweep(m, "Tongue", [((0, y + 1.0, zm - 2.4), 1.0, 1.0), ((0, y + 6.0, zm - 2.6), 0.8, 0.8)], sides=8)  # the clapper
    egg(m, "Tongue", (0, y + 7.0, zm - 2.6), 1.6, 1.8, 1.6, 10, 6)
    m.bone = "Head"
    eyes(m, at, [(0.6, 0.86, 0.8, (0.3, 0.94, -0.1), True), (0.44, 0.5, 0.5, (0.8, 0.5, 0.0), False), (0.3, 1.0, 0.44, (0.3, 0.6, 0.6), False), (0.76, 1.25, 0.4, (0.1, 0.8, 0.5), False)], lid="Accent", ridge="Body")
    ooze(m, (0, -1.0, 14.0))  # RAGE needs a Drip bone; nothing shows
    m.bone = "Head"
    m.head_centre = (0, 14.0, 13.4)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Endless Grief

SEIZE_PATH = [(0, 4.2, 8.6), (0, 4.8, 12.6), (0, 7.2, 15.9), (0, 11.0, 17.2), (0, 14.6, 15.8), (0, 16.2, 12.6)]  # as build_abyss_monsters_7_8.py: SEIZE_TURN in rare_kit.py straightens exactly this


def seizing_arm(m, letter, side, parent="Spine"):
    """A long arm held up over the head on five bones (SeizeL1-5, SeizeR1-5), ending in a hand of hooks. It unrolls straight to strike."""
    pts = [Vector(p) + Vector((side * 5.0, 0, 0)) for p in SEIZE_PATH]
    names = [f"Seize{letter}{k}" for k in range(1, 6)]
    for k, name in enumerate(names):
        m.joint(name, tuple(pts[k]), parent if k == 0 else names[k - 1])
    rings = curve([tuple(p) for p in pts], 26)
    bones = [names[min(int(i / 25 * 5), 4)] for i in range(26)]
    sweep(m, "Body", [(p, 2.3 - 0.05 * i, 2.3 - 0.05 * i) for i, p in enumerate(rings)], bones, sides=10, up=(1, 0, 0))
    for i in range(2, 25, 3):  # bone knuckles down the back of it
        p = Vector(rings[i])
        m.bone = bones[i]
        along = (Vector(rings[i + 1]) - p).normalized()
        out = -along.cross(Vector((1, 0, 0))).normalized()
        point(m, "Claw", tuple(p + out * 0.6), tuple(p + out * 2.6 - along * 0.8), 1.0)
    tip = pts[-1]
    m.bone = names[-1]
    egg(m, "Body", tuple(tip + Vector((0, 0.2, -0.8))), 2.2, 1.6, 2.0, 12, 6)
    for dx in (-1.5, -0.5, 0.5, 1.5):  # the fingers: long hooks
        base = tip + Vector((dx, 0.4, -1.6))
        sabre(m, "Claw", [tuple(base), tuple(base + Vector((dx * 0.3, 1.4, -3.0))), tuple(base + Vector((dx * 0.4, 0.4, -6.6)))], 0.9, 9)
    base = tip + Vector((-side * 1.6, -0.6, -0.6))
    sabre(m, "Claw", [tuple(base), tuple(base + Vector((-side * 1.6, 0.6, -2.0))), tuple(base + Vector((-side * 1.2, 1.2, -4.4)))], 0.9, 8)
    m.bone = parent


def endless_grief():
    """The thing behind the Last Door: it crawls, low and black, a skull for a face, and two arms taller than itself wait over it."""
    m = monster("dino_EndlessGrief", Body="#0b0b0e", Accent=BONE, Belly="#2b2b32", Claw="#dcd8cc")
    m.joint("Spine", (0, -4.0, 7.6))
    m.joint("Neck", (0, 6.0, 8.0), "Spine")
    m.joint("Head", (0, 7.4, 7.6), "Neck")
    rings = [((0, -16.0, 5.0), 2.4, 2.4), ((0, -13.0, 6.4), 8.0, 6.6), ((0, -8.0, 7.6), 11.0, 8.6), ((0, -3.0, 8.2), 12.0, 9.0), ((0, 2.0, 8.6), 12.6, 9.0), ((0, 6.4, 8.0), 8.6, 6.6)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Spine", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=20, under="Belly", under_faces=5, per=4)
    ribs(m, rings, (1.5, 1.9, 2.3, 2.7, 3.1, 3.5), bones, role="Accent")
    spines(m, rings, (1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0), 4.4, bones, role="Accent", w=1.5, back=0.5)
    for letter, side in (("L", -1), ("R", 1)):
        for name, y_, reach in ((f"Front{letter}", 2.0, 3.4), (f"Back{letter}", -9.0, -1.0)):
            hip = Vector((side * 5.0, y_, 7.4))
            knee = hip + Vector((side * 6.4, 0.6, 3.4))
            foot = Vector((side * 12.4, y_ + reach, 0.6))
            leg(m, name, "Spine", [hip, hip.lerp(knee, 0.5) + Vector((0, 0, 0.5)), knee, knee.lerp(foot, 0.5) + Vector((side * 0.8, 0, 0)), foot], (4.6, 3.6, 2.6, 2.0, 1.8), toes=0)
            knob(m, "Accent", knee, 1.9)
            point(m, "Accent", tuple(knee), tuple(knee + Vector((side * 1.2, -1.6, 3.0))), 1.6)
            claws(m, foot + Vector((0, 0.6, 0.6)), (0, 1, 0), 4, 0.9, 4.4, 0.8, droop=0.14)
        seizing_arm(m, letter, side)
        knob(m, "Body", Vector((side * 5.0, 4.0, 8.8)), 3.0)
    m.bone = "Spine"
    tail = curve([(0, -15.4, 5.4), (0, -19.0, 5.0), (0, -23.0, 3.4), (0, -27.0, 1.4)], 8)
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(tail, (3.6, 3.0, 2.5, 2.0, 1.6, 1.2, 0.8, 0.3))], sides=8)
    for n, (side, y_) in enumerate(((-1, 3.0), (1, 3.0), (-1, -1.0), (1, -1.0), (-1, -5.0), (1, -5.0)), start=1):  # a shroud in strips, dragging off its sides
        root = Vector((side * 5.6, y_, 9.4))
        pts = curve([root, root + Vector((side * 2.6, -2.0, -1.6)), root + Vector((side * 4.4, -5.0, -4.6)), root + Vector((side * 5.0, -8.6, -7.6))], 7)
        chain(m, "Sway", n, pts, 0.26, 0.16, parent="Spine", role="Belly", flat="normal", breadth=3.0)
    m.bone = "Head"
    skull = [(0, 0.84, 0.0, 0.96), (0.22, 1.0, 0.0, 1.1), (0.46, 0.94, 0.0, 0.92), (0.7, 0.72, 0.0, 0.62), (0.9, 0.52, 0.0, 0.42), (1.0, 0.28, 0.05, 0.22)]
    jaw = [(0, 0.8, -0.56, 0.0), (0.3, 0.92, -0.6, 0.0), (0.62, 0.8, -0.5, 0.0), (0.88, 0.56, -0.36, 0.0), (1.0, 0.26, -0.2, -0.02)]
    y, zm, length, width, height = 6.8, 6.0, 12.0, 11.0, 6.0
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.42, upper="Accent", lower="Accent", teeth=(15, 13), tall=1.9, base=0.5, fangs=((0.86, 2.0), (0.6, 1.5), (0.4, 1.4)), rows=2, seed=41, t0=0.2,
                     throat=1.1)
    eyes(m, at, [(0.52, 0.8, 0.9, (0.3, 0.94, -0.1), True), (0.36, 0.44, 0.5, (0.85, 0.5, 0.0), False), (0.7, 1.15, 0.44, (0.1, 0.9, 0.4), False), (0.24, 1.0, 0.5, (0.4, 0.4, 0.7), False)],
         lid="Accent", ridge="Accent")
    for side in (-1, 1):  # horns swept back off its brow
        spot = at(0.2, 0.8 if side > 0 else math.pi - 0.8)
        horn(m, "Claw", tuple(spot - Vector((0, 0, 0.5))), tuple(spot + Vector((side * 4.0, -7.0, 4.0))), 2.2, droop=-1.4, count=9)
        egg(m, "Socket", tuple(at(0.94, 1.15 if side > 0 else math.pi - 1.15)), 0.5, 0.4, 0.5, 8, 4)
    m.head_centre = (0, 16.0, 6.6)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Inconsolable


def inconsolable():
    """Shoulders higher than its head, a cage of ribs for a chest, a skull hung low between its arms, and two fists of bone it can't stop using."""
    m = monster("dino_Inconsolable", Body="#38373d", Accent="#0f0f12", Belly="#1c1c21", Claw=BONE)
    m.joint("Spine", (0, -5.0, 9.0))
    m.joint("Pummel", (0, 0.0, 14.0), "Spine")
    m.joint("Neck", (0, 5.0, 16.0), "Pummel")
    trunk = [((0, -8.0, 6.6), 5.0, 4.6), ((0, -6.0, 8.6), 10.0, 8.0), ((0, -3.0, 12.0), 13.6, 10.0), ((0, 0.6, 16.0), 19.0, 11.6), ((0, 3.6, 18.0), 20.0, 10.0), ((0, 6.0, 17.0), 10.0, 7.0)]
    bones = ["Spine", "Spine", "Spine", "Pummel", "Pummel", "Neck"]
    sweep_fine(m, "Body", trunk, bones, sides=22, under="Belly", under_faces=7, per=4)
    ribs(m, trunk, (1.5, 1.85, 2.2, 2.55, 2.9, 3.25), bones, grow=1.04, length=0.7)
    spines(m, trunk, (1.2, 1.8, 2.4, 3.0, 3.6, 4.2), 4.6, bones, w=1.8, back=0.15)
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee, ankle, foot = Vector((side * 4.6, -5.6, 8.4)), Vector((side * 7.0, -2.6, 5.0)), Vector((side * 6.6, -6.0, 2.2)), Vector((side * 6.8, -4.4, 0.9))
        m.use(f"Leg{letter}", tuple(hip))
        knob(m, "Body", hip, 3.4)
        limb(m, "Body", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.5, 0.3, 0.3)), knee], (6.0, 5.0, 3.6), sides=12)
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        knob(m, "Claw", knee, 2.0)
        limb(m, "Body", [knee, knee.lerp(ankle, 0.5) + Vector((0, -0.4, 0)), ankle, foot, foot + Vector((0, 2.6, -0.1))], (3.2, 2.6, 2.2, 2.4, 2.8), sides=10)
        talons(m, foot + Vector((0, 3.0, 0)), (0, 1, -0.15), 3, 1.2, 3.0, 1.1)
        shoulder, elbow, wrist = Vector((side * 10.6, 1.4, 18.0)), Vector((side * 15.0, 3.4, 11.0)), Vector((side * 12.0, 11.0, 3.4))
        m.use(f"Arm{letter}", tuple(shoulder), "Pummel")
        knob(m, "Body", shoulder, 5.4)
        for dx, dy, dz, tall in ((3.0, -1.4, 3.8, 5.0), (4.6, 0.4, 1.6, 3.8), (1.0, -2.6, 4.6, 4.2)):  # spikes through the shoulder
            base = shoulder + Vector((side * dx, dy, dz))
            horn(m, "Claw", tuple(base - Vector((side * 0.4, 0, 0.8))), tuple(base + Vector((side * tall * 0.5, -tall * 0.3, tall))), 1.9)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5), elbow], (8.0, 7.0, 5.0), sides=16)
        m.joint(f"Fore{letter}", tuple(elbow), f"Arm{letter}")
        m.bone = f"Fore{letter}"
        knob(m, "Claw", elbow, 3.0)
        point(m, "Claw", tuple(elbow), tuple(elbow + Vector((side * 3.0, -4.6, 2.4))), 2.6)
        limb(m, "Body", [elbow, elbow.lerp(wrist, 0.5) + Vector((side * 0.6, 0, 0)), wrist], (5.0, 5.6, 5.4), sides=14)
        band(m, "Accent", tuple(elbow.lerp(wrist, 0.6) + Vector((side * 0.3, 0, 0))), 6.3, 6.3, length=1.6, tilt=tuple(wrist - elbow))
        fist = wrist + Vector((0, 0.8, -0.4))
        egg(m, "Claw", tuple(fist), 4.2, 4.2, 3.2, 16, 8)  # a fist of bone
        for k in range(7):  # studded all round
            a = k * math.tau / 7
            d = Vector((math.cos(a), 0.5 + 0.5 * math.sin(a), 0.5 * math.sin(a) + 0.1)).normalized()
            point(m, "Claw", tuple(fist + d * 3.0), tuple(fist + d * 6.0), 1.7)
    m.use("Head", (0, 7.8, 14.6), "Neck")
    skull = [(0, 0.86, 0.0, 1.0), (0.2, 1.0, 0.0, 1.2), (0.44, 0.96, 0.0, 1.1), (0.68, 0.74, 0.0, 0.74), (0.9, 0.56, 0.0, 0.5), (1.0, 0.3, 0.05, 0.26)]
    jaw = [(0, 0.8, -0.5, 0.0), (0.3, 0.9, -0.54, 0.0), (0.62, 0.78, -0.46, 0.0), (0.88, 0.56, -0.34, 0.0), (1.0, 0.26, -0.2, -0.02)]
    y, zm, length, width, height = 7.0, 12.6, 9.6, 9.6, 5.2
    at = fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.86, upper="Claw", lower="Claw", teeth=(13, 11), tall=1.7, base=0.46, fangs=((0.86, 2.0), (0.6, 1.5)), rows=2, seed=43, t0=0.2,
                     throat=1.1, jaw_length=1.04)
    eyes(m, at, [(0.5, 0.82, 0.86, (0.3, 0.94, -0.1), True), (0.34, 0.46, 0.5, (0.85, 0.5, 0.0), False), (0.68, 1.16, 0.44, (0.1, 0.9, 0.4), False)], lid="Claw", ridge="Claw")
    for side in (-1, 1):
        spot = at(0.22, 0.7 if side > 0 else math.pi - 0.7)
        horn(m, "Claw", tuple(spot - Vector((0, 0, 0.5))), tuple(spot + Vector((side * 5.4, 1.0, 4.4))), 2.2, droop=-1.6, count=9)
        egg(m, "Socket", tuple(at(0.93, 1.15 if side > 0 else math.pi - 1.15)), 0.5, 0.4, 0.6, 8, 4)
    m.head_centre = (0, 15.0, 13.4)
    grounded(m)
    return m


ALL = [teddy_wrecks, good_boy, casket_case, wailing_widow, death_knell, endless_grief, inconsolable]


def main():
    rare_kit.animate = animate  # run() films with it: build_spore_hollow_toxic's, which stacks the rage on rare_kit's markers
    rare_kit.run(ALL, RENDERS, BLEND, "weeping_dark_dread", SKY, FLOOR, GLOW_ROLES, glow=1.2, spacing=46)


if __name__ == "__main__":
    main()
