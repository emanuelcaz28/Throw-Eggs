"""Builds Midnight Carnival's 8 monsters, the fright set, animates them and renders them (Blender, background mode).

    Blender -b -P build_midnight_carnival_fright.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_midnight_carnival_fright.py    (stills only)
    ONLY=jack_snap,twisty QUICK=1 ...                                            (just those)

Saves midnight_carnival_fright.blend and renders to design/world/monsters_midnight_carnival_fright/.

The owner, 2026-11-12: redesign map 11's monsters in Blender, the old ones "have poor geometry and weird faces". This file replaces the six
of build_midnight_carnival_monsters.py (blocky bodies, painted clown faces) and the two of build_midnight_carnival_monsters_7_8.py. Names and
ids are the same, so Config/Dinos doesn't change; the old scripts stay for the helpers other files import.

The idea stays: the fair's own attractions came alive at midnight, a little spooky and mischievous, not monstrous. The owner wanted
them better made, not scarier (2026-11-12: "they look too scary and aggressive, i just wanted them to look better and be more
polished"). So the characters are the old ones, made again: smooth swept bodies instead of boxes, clean round eyes with a neon-pink
iris and a shine, wide open under arched brows, a smile only just parted with a few short rounded teeth (no needle teeth,
no fangs, short claws), and their carnival things kept (the cone hat and red nose, the top hat and
moustache, the carousel pole, the big top and its bulbs). Colours: crimson and cream stripes, gold trim, a plum night, pink neon,
warm bulbs. Nothing drips, puffs or flies off them. They move as the old ones did: no new attacks (Last Laugh and Unbearable keep their
Maul, as before):

  Jack Snap       a striped jack-in-the-box on four crooked legs: a clown's head on a steel spring (Neck), red nose, purple hair,
                  a little cone hat with a bulb
  Popcorn Fiend   a striped popcorn carton whose top half is a jaw, popcorn heaped on its lid, butter running down, grabby arms
  Twisty          a balloon dog twisted wrong, folded up on hopper's legs, horn-shaped balloon ears, a curly balloon tail
  Nightmare Mare  the carousel horse, brass pole still through its back, white paint cracking, a mane and tail of pink neon
  Grinmaster      the ringmaster: a tall thing in a crimson tailcoat and top hat, a long chalk face with a curled moustache and a big
                  grin, one white glove reaching, a whip in the other
  Big Top Terror  the boss: a hunched brute carrying the big top on its back, bulbs round the valance, a ruff, a clown head with a
                  red nose and a crown of bulbs, long arms
  Last Laugh      the second rarest: a spotted hyena with high shoulders, a studded collar it slipped, a grin round its head (Maul)
  Unbearable      the rarest: the dancing bear that got out, reared up, its show collar and a shackle on each wrist (Maul)

Glowing roles: EyeGlow, Neon, Bulb (all in shared/Roles.luau already). Skin roles Body, Accent, Belly and Claw take the colour mutations.
1 Blender unit = 1 stud, models face +Y, feet on Z = 0. Plain colours, no stud image.
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
from build_spore_hollow_toxic import animate, blotch, grounded, leg, skin_at, unit  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from build_weeping_dark_dread import claws  # noqa: E402
from fierce_kit import band, fierce_head, horn, knob  # noqa: E402
from rare_kit import curve, jointed, leaf, ring_round, round_eye, sabre, skin, sweep, sweep_fine  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_midnight_carnival_fright"
BLEND = "midnight_carnival_fright"  # for check_map.py and export_fbx.py
GLOW_ROLES = {"EyeGlow", "Neon", "Bulb"}
kit.NO_STUDS.update(GLOW_ROLES | {"Socket", "EyeWhite"})

CRIMSON, CREAM, GOLD, PLUM, NIGHT = "#b8142f", "#f2e6cc", "#e2a92c", "#4a1a4f", "#1a0f1e"
FACE = {"Pupil": "#0a0508", "Slit": "#0a0508", "Socket": "#060307", "Highlight": "#ffffff", "EyeWhite": "#fbf6ec", "EyeGlow": "#ff2fa6", "Mouth": "#22060e", "Tongue": "#8a1a3a",
        "Teeth": "#f6eedc", "Neon": "#ff3fb4", "Bulb": "#ffd27a", "Gold": GOLD}
SKY, FLOOR = "#2a1630", "#5a3048"
ROOT2 = math.sqrt(2)


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- shapes


def fair_eyes(m, at, t, angle, r, look, lid="Body", top=0.26, tilt=0.18, brow=None):
    """The fair's eyes: a pair of big round eyes, a glowing neon-pink iris, a big pupil and a shine, wide open (2026-11-12, second
    softening: lowered lids and slanted brows read as angry). brow: a role for a soft brow arching up over each."""
    top, tilt = top * 0.3, 0.0
    for side in (-1, 1):
        spot = at(t, angle if side > 0 else math.pi - angle)
        round_eye(m, tuple(spot), r, (side * look[0], look[1], look[2]), side, iris="EyeGlow", iris_size=0.62, pupil_size=0.36, lid_role=lid, top=top, tilt=tilt)
        if brow:
            c = Vector(spot) + Vector((0, -r * 0.1, r * 1.5))
            sweep_fine(m, brow, [(tuple(c + Vector((side * r * 0.95, -r * 0.2, -r * 0.3))), r * 0.28, r * 0.2), (tuple(c), r * 0.38, r * 0.28),
                                 (tuple(c + Vector((-side * r * 0.95, r * 0.1, -r * 0.3))), r * 0.28, r * 0.2)], sides=6, per=3)


def blunt_teeth(m, at, z, count, tall, base, fangs, direction, rng, rake=0.12, start=0.02):
    """Stands in for fierce_kit.row_of_teeth inside grin(): short rounded cartoon teeth instead of sabres."""
    for side in (-1, 1):
        for k in range(count):
            s = start + (0.985 - start) * (k + 0.5) / count
            x, yy = at(s)
            egg(m, "Teeth", (side * x * 0.97, yy, z + direction * tall * 0.45), base, base * 0.55, tall * 0.55, 8, 4)


def grin(m, y, zm, length, width, height, skull, jaw, seed, upper="Body", lower=None, teeth=(10, 8), fang=1.3, gape=-0.3, **options):
    """fierce_head made friendly (2026-11-12, second softening: the open maw of needle teeth was still too aggressive): a smile only just
    parted, a few short rounded teeth on top, none below, no fangs. teeth, fang and gape are kept in the calls but scaled down here."""
    import fierce_kit
    sabres, fierce_kit.row_of_teeth = fierce_kit.row_of_teeth, blunt_teeth
    try:
        return fierce_head(m, y, zm, length, width, height, skull, jaw, gape=gape * 0.3, upper=upper, lower=lower, teeth=(max(4, teeth[0] // 2), 0),
                           tall=0.8, base=0.62, fangs=(), low_fangs=(), rows=1, seed=seed, **options)
    finally:
        fierce_kit.row_of_teeth = sabres


def box(m, role, base, w0, d0, h, w1=None, d1=None, bone=None):
    """A box standing on `base` (its bottom middle): w across, d deep, h tall, w1 and d1 at the top for a taper."""
    c = Vector(base)
    w1, d1 = w1 or w0, d1 or d0
    sweep(m, role, [(tuple(c), w0 * ROOT2, d0 * ROOT2), (tuple(c + Vector((0, 0, h))), w1 * ROOT2, d1 * ROOT2)], [bone or m.bone] * 2, sides=4, up=(0, 1, 0))


def slab(m, role, a, b, w, thick, out):
    """A flat board from a to b, w wide, thick through along out."""
    sweep(m, role, [(tuple(a), w * ROOT2, thick * ROOT2), (tuple(b), w * ROOT2, thick * ROOT2)], sides=4, up=tuple(unit(out)))


def diamond(m, role, centre, normal, w, h, depth=0.4):
    """A harlequin diamond standing proud of a flat face."""
    c, n = Vector(centre), unit(normal)
    sweep(m, role, [(tuple(c - n * depth), w, h), (tuple(c + n * depth * 0.4), w, h)], sides=4, turn=0, up=(0, 0, 1) if abs(n.z) < 0.9 else (0, 1, 0))


def ruff(m, centre, r, count, roles, out=1.0, rise=0.4, w=3.0, start=0.0, arc=math.tau, tilt=0.0):
    """A clown's ruff: blades fanned out round a neck at centre, roles taking turns. tilt leans the whole ring forward."""
    c = Vector(centre)
    for k in range(count):
        a = start + arc * (k + 0.5) / count
        d = Vector((math.cos(a), math.sin(a), tilt * math.sin(a))).normalized()
        lift = Vector((0, 0, 0.5 if k % 2 else 0.0))  # every other blade a little higher, so neighbours cross instead of lying in one plane
        base = c + d * r * 0.5 + lift
        tip = c + d * (r + out * r) + Vector((0, 0, rise * r)) + lift * 1.6
        leaf(m, roles[k % len(roles)], tuple(base), tuple(tip), (-d.y, d.x, 0), w, thick=0.4)


def glove(m, wrist, ahead, r=1.2, role="Glove"):
    """A white showman's glove: a round palm and four short fat fingers, curled a little."""
    w, d = Vector(wrist), unit(ahead)
    side = unit(d.cross(Vector((0, 0, 1)))) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    down = side.cross(d)
    palm = w + d * r * 0.8
    egg(m, role, tuple(palm), r, r * 1.1, r * 0.8, 10, 6)
    for k in range(4):
        base = palm + side * r * 0.55 * (k - 1.5) + d * r * 0.8
        tip = base + d * r * (1.1 - 0.12 * abs(k - 1.5)) + down * r * 0.4
        sweep_fine(m, role, [(tuple(base), r * 0.5, r * 0.5), (tuple(base.lerp(tip, 0.6) - down * r * 0.05), r * 0.46, r * 0.46), (tuple(tip), r * 0.36, r * 0.36)], sides=8, per=2)


def sausage(m, role, a, b, r, pinch=0.3, bone=None):
    """One balloon: a long round bulb from a to b, pinched at both ends where it's twisted."""
    a, b = Vector(a), Vector(b)
    rings = [(tuple(a), r * pinch * 2, r * pinch * 2), (tuple(a.lerp(b, 0.14)), r * 1.7, r * 1.7), (tuple(a.lerp(b, 0.5)), r * 2, r * 2),
             (tuple(a.lerp(b, 0.86)), r * 1.7, r * 1.7), (tuple(b), r * pinch * 2, r * pinch * 2)]
    sweep_fine(m, role, rings, [bone or m.bone] * 5, sides=14, per=3)


def twist(m, at, r, role="Accent"):
    """The knot where two balloons are twisted together."""
    egg(m, role, tuple(at), r, r, r, 10, 6)


def crack_line(m, rings, spots, w=0.32, role="Crack"):
    """A crack in old paint running over a body through (u, angle) spots."""
    pts = [skin_at(rings, u, a, -0.05)[0] for u, a in spots]
    sweep(m, role, [(tuple(p), w * (0.5 + 0.5 * math.sin(math.pi * (k + 0.5) / len(pts))), 0.36) for k, p in enumerate(pts)], sides=4)


def striped_tent(m, centre, rx, ry, top, sectors=16, roles=("Accent", "Belly"), bone="Spine", levels=6, bulge=0.12):
    """The big top: a cone of canvas in alternating gores, from an oval base round centre up to a point `top` above it."""
    c = Vector(centre)
    for j in range(sectors):
        verts, faces = [], []
        for side in (0, 1):
            a = (j + side) * math.tau / sectors
            for i in range(levels + 1):
                t = i / levels
                swell = 1 + bulge * math.sin(math.pi * t)
                k = (1 - t) ** 0.85 * swell
                verts.append(tuple(c + Vector((math.cos(a) * rx * k, math.sin(a) * ry * k, top * t))))
        n = levels + 1
        for i in range(levels):
            faces.append([i, n + i, n + i + 1, i + 1])
        skin(m, roles[j % len(roles)], verts, faces, [bone] * len(verts))


def coil(m, role, base, r, turns, height, w, bone=None):
    """A steel spring standing on base."""
    b = Vector(base)
    count = int(turns * 16)
    pts = [tuple(b + Vector((math.cos(k / 16 * math.tau) * r, math.sin(k / 16 * math.tau) * r, height * k / count))) for k in range(count + 1)]
    sweep(m, role, [(p, w, w) for p in pts], [bone or m.bone] * len(pts), sides=8)


# ---------------------------------------------------------------------- Jack Snap


def jack_snap():
    """A jack-in-the-box walking on four crooked legs. Out of it, on a steel spring, a clown's head with a sly grin and a cone hat."""
    m = monster("dino_JackSnap", Body=CRIMSON, Accent=NIGHT, Belly=CREAM, Claw="#efe6d6", Hair="#6a1fa0", Nose="#ff2244", Steel="#b9b4c4", Hat="#1c8c86", Glove="#f6f1e6")
    m.joint("Spine", (0, -5.0, 6.0))
    m.bone = "Spine"
    cy = -3.0
    box(m, "Body", (0, cy, 3.4), 10.0, 9.4, 7.8, 11.4, 10.6)
    box(m, "Gold", (0, cy, 3.1), 10.5, 9.9, 0.9, 10.6, 10.0)
    box(m, "Gold", (0, cy, 10.6), 11.8, 11.0, 0.9)
    for side in (-1, 1):
        diamond(m, "Belly", (side * 5.45, cy, 7.2), (side, 0, 0), 6.2, 5.6)
        diamond(m, "Accent", (side * 5.6, cy, 7.2), (side, 0, 0), 2.6, 2.4, 0.3)
    for side in (-1, 1):
        diamond(m, "Belly", (0, cy + side * 5.1, 7.2), (0, side, 0), 6.6, 5.6)
        diamond(m, "Accent", (0, cy + side * 5.25, 7.2), (0, side, 0), 2.8, 2.4, 0.3)
    # The lid, thrown open behind it.
    hinge = Vector((0, cy - 5.3, 11.5))
    lid_top = hinge + Vector((0, -2.8, 9.6))
    slab(m, "Body", hinge, lid_top, 11.4, 0.8, (0, 0.96, 0.28))
    slab(m, "Gold", hinge + Vector((0, -0.25, 0.0)), hinge + Vector((0, -0.4, 0.0)) + (lid_top - hinge) * 0.12, 11.8, 0.9, (0, 0.96, 0.28))
    diamond(m, "Belly", hinge.lerp(lid_top, 0.55) + Vector((0, 0.5, 0)), (0, 0.96, 0.28), 6.0, 5.4)
    for letter, side in (("L", -1), ("R", 1)):
        for name, y_, reach in ((f"Front{letter}", cy + 3.6, 3.0), (f"Back{letter}", cy - 3.6, -2.4)):
            hip = Vector((side * 4.6, y_, 4.4))
            knee = Vector((side * 8.6, y_ + reach * 0.4, 5.6))
            foot = Vector((side * 9.4, y_ + reach, 0.8))
            leg(m, name, "Spine", [hip, hip.lerp(knee, 0.5) + Vector((0, 0, 0.6)), knee, knee.lerp(foot, 0.5), foot], (2.8, 2.4, 2.0, 1.7, 1.6), role="Accent", toes=3, toe=(0.8, 1.2, 0.7),
                ahead=(0, 1 if reach > 0 else 0.6, -0.25))
            knob(m, "Gold", knee, 1.25)
    # The spring: its Neck, which bounces.
    m.joint("Neck", (0, cy, 11.6), "Spine")
    coil(m, "Steel", (0, cy, 11.4), 2.2, 4.5, 6.6, 0.9, "Neck")
    egg(m, "Steel", (0, cy, 11.6), 2.6, 2.6, 0.5, 12, 4)
    ruff(m, (0, cy + 0.4, 18.4), 3.6, 14, ("Belly", "Body"), out=0.9, rise=0.12, w=2.8, tilt=0.15)
    for letter, side in (("L", -1), ("R", 1)):  # thin arms out of the ruff, gloved in claws
        shoulder, elbow, wrist = Vector((side * 3.0, cy + 0.6, 18.0)), Vector((side * 7.2, cy + 2.4, 15.4)), Vector((side * 6.4, cy + 7.6, 15.6))
        m.use(f"Arm{letter}", tuple(shoulder), "Neck")
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5), elbow, elbow.lerp(wrist, 0.5), wrist], (1.8, 1.6, 1.5, 1.4, 1.5), sides=10)
        band(m, "Belly", tuple(elbow.lerp(wrist, 0.82)), 2.1, 2.1, length=0.7, tilt=tuple(wrist - elbow))
        glove(m, wrist, (0, 1, -0.15), 1.0)
    m.joint("Head", (0, cy + 1.6, 20.4), "Neck")
    m.bone = "Head"
    skull = [(0, 0.82, 0.0, 1.0), (0.2, 1.0, 0.0, 1.42), (0.44, 0.96, 0.0, 1.36), (0.68, 0.8, 0.0, 0.92), (0.9, 0.62, 0.0, 0.54), (1.0, 0.4, 0.03, 0.3)]
    jaw = [(0, 0.8, -0.55, 0.0), (0.3, 0.92, -0.62, 0.0), (0.62, 0.82, -0.5, 0.0), (0.88, 0.6, -0.36, 0.0), (1.0, 0.36, -0.22, -0.02)]
    y, zm, length, width, height = cy - 0.6, 20.8, 10.0, 10.0, 5.0
    at = grin(m, y, zm, length, width, height, skull, jaw, 51, upper="Belly", lower="Belly", teeth=(12, 10), gape=-0.42, t0=0.16)
    fair_eyes(m, at, 0.56, 0.86, 1.15, (0.28, 0.95, -0.05), lid="Belly", brow="Accent")
    egg(m, "Nose", tuple(at(0.94, math.pi / 2) + Vector((0, 0.9, 0.5))), 1.25, 1.2, 1.15, 12, 6)
    crown = at(0.36, math.pi / 2)  # its little cone hat, cocked to one side, a bulb on the tip
    tip = crown + Vector((1.6, -0.6, 6.0))
    sweep_fine(m, "Hat", [(tuple(crown - Vector((0, 0, 0.3))), 4.4, 4.4), (tuple(crown.lerp(tip, 0.5)), 2.4, 2.4), (tuple(tip), 0.4, 0.4)], sides=14, per=3)
    ring_round(m, "Gold", tuple(crown + Vector((0, 0, 0.1))), 2.1, tuple(unit(tip - crown)), 0.4, 14)
    egg(m, "Bulb", tuple(tip + Vector((0.1, 0, 0.5))), 0.7, 0.7, 0.7, 10, 6)
    for side in (-1, 1):  # tufts of hair, swept back like flames
        for k, (t, a, out, up) in enumerate(((0.16, 0.25, 5.2, 1.0), (0.3, 0.35, 4.6, 2.4), (0.12, 0.6, 3.8, 3.6), (0.4, 0.15, 4.2, -0.6))):
            spot = at(t, a if side > 0 else math.pi - a)
            horn(m, "Hair", tuple(spot - Vector((side * 0.6, 0, 0))), tuple(spot + Vector((side * out, -2.6 - 0.4 * k, up))), 2.0 - 0.2 * k, droop=-0.8)
    m.head_centre = (0, 12.0, 21.0)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Popcorn Fiend


def popcorn_fiend():
    """A popcorn carton whose whole top is a jaw, popcorn heaped on it like a lid of hair, on four short legs, little gloved arms."""
    m = monster("dino_PopcornFiend", Body=CREAM, Accent=CRIMSON, Belly="#2a1424", Claw="#efe6d6", Kernel="#fff3d6", Butter="#f2c53d", Glove="#f6f1e6")
    rng = random.Random(61)
    m.joint("Spine", (0, -6.6, 5.0))
    m.joint("Head", (0, -5.0, 9.0), "Spine")
    m.bone = "Spine"
    # The carton: narrow at the foot, wide at the rim, crimson stripes up every side, a gold rim.
    box(m, "Body", (0, 0, 1.8), 9.0, 7.6, 7.0, 12.8, 10.8)
    box(m, "Gold", (0, 0, 8.4), 13.2, 11.2, 0.6)
    for k in range(-2, 3):
        f = k / 2.5
        for side in (-1, 1):
            strip_ = (Vector((f * 4.5, side * 3.86, 1.9)), Vector((f * 6.3, side * 5.38, 8.2)))
            slab(m, "Accent", *strip_, 1.5, 0.3, (0, side, 0))
        if abs(k) < 2:
            for side in (-1, 1):  # (the stripes on its sides)
                slab(m, "Accent", Vector((side * 4.56, f * 3.8, 1.9)), Vector((side * 6.38, f * 5.3, 8.2)), 1.5, 0.3, (side, 0, 0))
    for letter, side in (("L", -1), ("R", 1)):
        for name, y_ in ((f"Front{letter}", 2.6), (f"Back{letter}", -2.6)):
            hip = Vector((side * 3.4, y_, 2.4))
            foot = Vector((side * 6.4, y_ + (1.6 if y_ > 0 else -0.6), 0.7))
            leg(m, name, "Spine", [hip, hip.lerp(foot, 0.5) + Vector((side * 0.8, 0, 0.8)), foot], (2.6, 2.2, 1.8), role="Belly", toes=3, toe=(0.8, 1.2, 0.7))
        shoulder, elbow, wrist = Vector((side * 6.0, 1.2, 6.6)), Vector((side * 8.8, 2.4, 4.6)), Vector((side * 7.6, 6.0, 5.2))
        m.use(f"Arm{letter}", tuple(shoulder), "Spine")
        limb(m, "Belly", [shoulder, shoulder.lerp(elbow, 0.5), elbow, elbow.lerp(wrist, 0.5), wrist], (1.8, 1.6, 1.5, 1.3, 1.5), sides=10)
        glove(m, wrist, (0, 1, -0.1), 1.0)
    m.bone = "Head"
    # The top half: the lid of the carton is the skull, the rim of the carton its lower jaw.
    skull = [(0, 0.92, 0.0, 0.8), (0.1, 1.0, 0.0, 1.0), (0.5, 1.0, 0.0, 1.06), (0.88, 0.98, 0.0, 0.92), (1.0, 0.9, 0.0, 0.62)]
    jaw = [(0, 0.88, -0.3, 0.0), (0.5, 0.94, -0.34, 0.0), (0.9, 0.9, -0.3, 0.0), (1.0, 0.82, -0.22, 0.0)]
    y, zm, length, width, height = -5.2, 9.4, 10.6, 12.6, 5.4
    at = grin(m, y, zm, length, width, height, skull, jaw, 63, upper="Body", lower="Accent", teeth=(14, 12), fang=1.5, gape=-0.3, t0=0.08)
    fair_eyes(m, at, 0.84, 0.66, 1.3, (0.25, 0.96, 0.0), brow="Accent")
    for k in range(46):  # the popcorn, heaped in the middle
        t = rng.uniform(0.08, 0.8)
        a = rng.uniform(0.55, math.pi - 0.55)
        spot = at(t, a)
        heap = math.sin(a) * (1 - abs(t - 0.42) * 1.4)
        c = spot + Vector((0, 0, heap * 2.6 + rng.uniform(0.0, 0.8)))
        r = rng.uniform(0.9, 1.4)
        for j in range(3):
            o = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.4, 0.6))).normalized() * r * 0.55
            egg(m, "Kernel" if j else "Butter" if k % 5 == 0 else "Kernel", tuple(c + o), r * 0.7, r * 0.7, r * 0.6, 8, 4)
    for t, a, length_ in ((0.3, 0.3, 2.6), (0.6, 0.25, 2.0), (0.46, math.pi - 0.28, 2.8), (0.2, math.pi - 0.3, 1.8)):  # butter running down the lid
        top = at(t, a)
        bottom = at(t, (0.02 if a < math.pi / 2 else math.pi - 0.02))
        sweep(m, "Butter", [(tuple(top + Vector((0, 0, 0.2))), 1.0, 0.4), (tuple(bottom.lerp(top, 0.3)), 0.8, 0.4), (tuple(bottom + Vector((0, 0, -0.2 - length_ * 0.2))), 0.5, 0.4)], sides=4)
    m.head_centre = (0, 12.0, 9.6)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Twisty


def twisty():
    """A balloon dog twisted wrong: hot pink bulbs folded up like a flea, horn-shaped ears, a sly grin with a few teeth."""
    m = monster("dino_Twisty", Body="#ff4f9a", Accent="#6a0f40", Belly="#ffc2dc", Claw="#f6eedc")
    m.joint("Spine", (0, -4.0, 9.0))
    m.joint("Neck", (0, 4.6, 11.6), "Spine")
    m.bone = "Spine"
    sausage(m, "Body", (0, -11.2, 8.6), (0, -3.4, 10.2), 3.4)
    twist(m, Vector((0, -3.2, 10.2)), 1.3)
    sausage(m, "Body", (0, -3.0, 10.2), (0, 4.6, 11.8), 3.0)
    twist(m, Vector((0, 4.8, 11.8)), 1.2)
    m.use("Tail1", (0, -11.4, 9.2))  # its tail: two more balloons, curled up over its back, and the knot
    sausage(m, "Body", (0, -11.4, 9.2), (0, -14.2, 15.0), 1.6)
    m.use("Tail2", (0, -14.3, 15.2), "Tail1")
    twist(m, Vector((0, -14.3, 15.2)), 0.9)
    sausage(m, "Body", (0, -14.3, 15.4), (0, -12.0, 19.0), 1.2)
    m.use("Tail3", (0, -11.9, 19.2), "Tail2")
    twist(m, Vector((0, -11.9, 19.2)), 0.7)
    m.bone = "Spine"
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee = Vector((side * 3.4, -6.0, 9.8)), Vector((side * 7.6, -11.6, 17.6))
        hock, foot = Vector((side * 8.6, -4.4, 5.0)), Vector((side * 8.8, -1.4, 0.9))
        m.use(f"Back{letter}", tuple(hip))
        twist(m, hip, 1.4)
        sausage(m, "Body", hip, knee, 1.9, bone=f"Back{letter}")
        m.joint(f"Hock{letter}", tuple(knee), f"Back{letter}")
        m.bone = f"Hock{letter}"
        twist(m, knee, 1.1)
        sausage(m, "Body", knee, hock, 1.3, bone=f"Hock{letter}")
        twist(m, hock, 0.9)
        sausage(m, "Body", hock, foot, 1.1, bone=f"Hock{letter}")
        egg(m, "Body", tuple(foot + Vector((0, 1.0, 0))), 1.5, 2.2, 1.0, 12, 6)
        shoulder, elbow, wrist = Vector((side * 2.4, 3.0, 10.4)), Vector((side * 6.0, 6.0, 7.0)), Vector((side * 5.0, 9.4, 1.6))
        m.use(f"Front{letter}", tuple(shoulder), "Spine")
        twist(m, shoulder, 1.1)
        sausage(m, "Body", shoulder, elbow, 1.3, bone=f"Front{letter}")
        twist(m, elbow, 0.9)
        sausage(m, "Body", elbow, wrist, 1.1, bone=f"Front{letter}")
        egg(m, "Body", tuple(wrist + Vector((0, 0.9, -0.4))), 1.3, 1.9, 0.9, 12, 6)
    m.bone = "Neck"
    sausage(m, "Body", (0, 4.8, 12.0), (0, 7.0, 14.4), 1.8)
    m.use("Head", (0, 7.4, 14.0), "Neck")
    skull = [(0, 0.78, 0.0, 1.0), (0.22, 1.0, 0.0, 1.3), (0.46, 0.94, 0.0, 1.2), (0.7, 0.72, 0.0, 0.84), (0.9, 0.5, 0.0, 0.54), (1.0, 0.3, 0.04, 0.3)]
    jaw = [(0, 0.76, -0.5, 0.0), (0.34, 0.8, -0.5, 0.0), (0.66, 0.6, -0.38, 0.0), (0.92, 0.4, -0.26, 0.0), (1.0, 0.2, -0.16, -0.02)]
    y, zm, length, width, height = 6.4, 14.2, 9.4, 7.6, 3.8
    at = grin(m, y, zm, length, width, height, skull, jaw, 71, lower="Body", teeth=(11, 9), fang=1.2, gape=-0.36, t0=0.2)
    fair_eyes(m, at, 0.5, 0.84, 1.0, (0.3, 0.94, -0.05))
    twist(m, at(0.985, math.pi / 2) + Vector((0, 0.3, -0.1)), 0.55)  # the knot at the end of its nose
    for side in (-1, 1):  # devil-horn ears: two balloons twisted up and back
        root = at(0.2, 0.9 if side > 0 else math.pi - 0.9)
        mid = root + Vector((side * 2.2, -1.4, 3.6))
        tip = mid + Vector((side * 0.4, -2.6, 2.8))
        twist(m, root, 0.9)
        sausage(m, "Body", root, mid, 1.0)
        twist(m, mid, 0.6)
        sausage(m, "Body", mid, tip, 0.7)
        twist(m, tip, 0.45)
    m.head_centre = (0, 17.0, 14.6)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Nightmare Mare


def nightmare_mare():
    """The carousel horse that came off its ride: white paint cracking, gold trim, the brass pole still through its back, a mane of pink neon."""
    m = monster("dino_NightmareMare", Body="#efe8dc", Accent=CRIMSON, Belly="#cfc4b2", Claw="#22161c", Crack="#3a2430")
    m.joint("Spine", (0, -6.0, 11.0))
    m.joint("Neck", (0, 6.4, 14.6), "Spine")
    rings = [((0, -11.6, 11.4), 2.6, 2.6), ((0, -10.2, 11.8), 7.2, 7.4), ((0, -5.6, 12.2), 8.2, 8.4), ((0, -0.6, 12.4), 8.4, 8.8), ((0, 3.6, 12.8), 8.6, 9.4), ((0, 6.4, 14.4), 6.4, 7.2)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Spine", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=18, under="Belly", under_faces=5, per=4)
    crack_line(m, rings, [(1.6, 0.4), (1.9, 0.6), (2.1, 0.45), (2.4, 0.7)])
    crack_line(m, rings, [(3.2, math.pi - 0.3), (3.5, math.pi - 0.55), (3.8, math.pi - 0.4)])
    crack_line(m, rings, [(1.2, math.pi - 0.9), (1.5, math.pi - 0.7), (1.7, math.pi - 0.95)])
    m.bone = "Neck"
    sweep_fine(m, "Body", [((0, 5.6, 13.6), 6.0, 7.0), ((0, 7.6, 17.0), 5.0, 5.6), ((0, 9.0, 20.0), 4.2, 4.6), ((0, 9.8, 21.4), 3.6, 3.8)], ["Neck"] * 4, sides=14, per=3)
    # The saddle and its cloth, and the pole it was riding on.
    m.bone = "Spine"
    egg(m, "Accent", (0, -2.4, 15.9), 5.0, 5.6, 1.4, 14, 5)
    egg(m, "Gold", (0, -2.4, 16.7), 3.4, 4.0, 1.0, 12, 5)
    for side in (-1, 1):
        egg(m, "Gold", (side * 4.4, -2.4, 14.6), 0.6, 4.6, 0.6, 8, 4)
    sweep(m, "Gold", [((0, -2.4, 8.0), 1.4, 1.4), ((0, -2.4, 32.0), 1.4, 1.4)], sides=12)
    for z in (17.8, 24.0, 30.0):
        ring_round(m, "Gold", (0, -2.4, z), 0.9, (0, 0, 1), 0.36, 12)
    egg(m, "Gold", (0, -2.4, 32.6), 1.6, 1.6, 1.4, 12, 6)
    for n, (y, z) in enumerate(((9.6, 22.4), (8.8, 21.0), (8.0, 19.6), (7.0, 18.2), (5.8, 16.8), (4.2, 15.8), (2.4, 15.4), (0.6, 15.4)), start=1):  # the neon mane, in locks
        m.bone = "Neck" if n <= 5 else "Spine"
        tall = 5.0 - 0.3 * n
        sabre(m, "Neon", [(0, y, z - 1.2), (0, y - tall * 0.5, z + tall * 0.4), (0, y - tall * 1.05, z + tall * 0.1)], 1.6, 7, flat=0.6, power=1.0)
    for name, x, y_, front in (("FrontL", -3.2, 4.4, True), ("FrontR", 3.2, 4.4, True), ("BackL", -3.0, -8.4, False), ("BackR", 3.0, -8.4, False)):
        side = 1 if x > 0 else -1
        top = Vector((x, y_, 12.0))
        knee = Vector((x + side * 0.6, y_ + (1.6 if front else -2.4), 6.4))
        foot = Vector((x + side * 0.4, y_ + (0.8 if front else -0.6), 1.4))
        m.use(name, tuple(top), "Spine")
        knob(m, "Body", top + Vector((0, 0, 0.6)), 3.4 if front else 3.8)
        limb(m, "Body", [top, top.lerp(knee, 0.5) + Vector((0, 0.2 if front else -0.4, 0)), knee, knee.lerp(foot, 0.5), foot], (4.4 if front else 5.0, 3.2, 2.2, 1.8, 2.0), sides=12)
        knob(m, "Belly", knee, 1.5)
        ring_round(m, "Gold", tuple(foot + Vector((0, 0, 0.6))), 1.2, (0, 0, 1), 0.44, 12)
        egg(m, "Claw", tuple(foot + Vector((0, 0.4, -0.6))), 1.7, 2.0, 1.0, 12, 5)  # the hoof
    m.bone = "Spine"
    tail = curve([(0, -11.4, 11.6), (0, -14.6, 12.6), (0, -17.4, 10.0), (0, -18.6, 5.6)], 8)
    jointed(m, "Neon", ["Tail1", "Tail2", "Tail3"], [(p, w, w * 0.7) for p, w in zip(tail, (1.6, 2.4, 2.6, 2.4, 2.0, 1.6, 1.1, 0.4))], sides=8)
    m.use("Head", (0, 10.0, 20.8), "Neck")
    skull = [(0, 0.9, 0.0, 1.1), (0.24, 1.0, 0.0, 1.12), (0.5, 0.84, 0.0, 0.8), (0.78, 0.74, 0.0, 0.64), (0.94, 0.7, 0.0, 0.56), (1.0, 0.6, 0.02, 0.44)]
    jaw = [(0, 0.84, -0.52, 0.0), (0.34, 0.78, -0.46, 0.0), (0.7, 0.68, -0.4, 0.0), (0.94, 0.62, -0.34, 0.0), (1.0, 0.5, -0.26, -0.02)]
    y, zm, length, width, height = 8.8, 20.0, 11.6, 5.8, 4.4
    at = grin(m, y, zm, length, width, height, skull, jaw, 81, lower="Body", teeth=(12, 10), fang=1.3, gape=-0.26, t0=0.2, jaw_length=1.02)
    fair_eyes(m, at, 0.36, 0.78, 1.0, (0.45, 0.88, -0.05), top=0.3, tilt=0.1)
    band(m, "Accent", (0, y + length * 0.66, zm + height * 0.22), width * 0.98, height * 1.1, length=0.8, bone="Head")  # the bridle
    for side in (-1, 1):
        ear = at(0.1, 1.0 if side > 0 else math.pi - 1.0)
        leaf(m, "Body", tuple(ear - Vector((0, 0, 0.4))), tuple(ear + Vector((side * 1.2, -3.0, 2.4))), (1, 0.2, 0), 1.6, thick=0.3)  # laid back
        egg(m, "Socket", tuple(at(0.985, 0.55 if side > 0 else math.pi - 0.55)), 0.42, 0.34, 0.5, 8, 4)  # nostrils, flared at the front
    m.head_centre = (0, 16.0, 20.6)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Grinmaster


def grinmaster():
    """The ringmaster: tall, hunched, a crimson tailcoat with gold on its shoulders, a top hat, a long chalk face, a moustache and a grin."""
    m = monster("dino_Grinmaster", Body=CRIMSON, Accent="#140b16", Belly=CREAM, Claw="#efe6d6", Glove="#f6f1e6", Whip="#2a1416", Shoe="#0e080f")
    m.joint("Spine", (0, -1.0, 11.0))
    m.bone = "Spine"
    torso = [((0, -1.4, 9.6), 5.2, 4.4), ((0, -1.0, 12.4), 6.4, 5.0), ((0, -0.2, 15.4), 8.6, 5.8), ((0, 0.8, 18.0), 10.4, 6.2), ((0, 1.6, 19.8), 7.4, 5.2)]
    sweep_fine(m, "Body", torso, ["Spine"] * 5, up=(0, -1, 0.1), sides=18, per=4)
    egg(m, "Belly", (0, 2.6, 16.6), 2.4, 1.4, 3.6, 12, 6)  # shirt front
    for side in (-1, 1):
        for z in (13.4, 15.2, 17.0):
            knob(m, "Gold", Vector((side * 2.6, 2.4 - 0.1 * (17.0 - z), z)), 0.55)
        leaf(m, "Body", (side * 1.6, -3.2, 11.6), (side * 2.8, -5.4, 2.6), (1, 0, 0), 3.6, thick=0.4)  # the tails of its coat
        leaf(m, "Body", (side * 1.6, -2.4, 18.6), (side * 3.4, -2.0, 23.6), (1, 0, 0), 4.4, thick=0.4)  # a collar standing up behind its head
        egg(m, "Gold", (side * 5.4, 0.8, 19.6), 2.0, 2.0, 0.9, 12, 5)  # epaulettes
        for k in range(5):
            p = Vector((side * (4.2 + 0.6 * k), 0.8 + 0.5 * (k - 2), 19.0))
            point(m, "Gold", tuple(p), tuple(p + Vector((side * 0.5, 0, -1.8))), 0.5)
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee, ankle, foot = Vector((side * 2.6, -1.0, 10.0)), Vector((side * 3.8, 2.2, 6.0)), Vector((side * 3.6, -1.8, 2.4)), Vector((side * 3.8, 0.0, 0.9))
        m.use(f"Leg{letter}", tuple(hip))
        knob(m, "Accent", hip, 2.4)
        limb(m, "Accent", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.3, 0, 0)), knee], (3.6, 3.0, 2.2), sides=12)
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        knob(m, "Accent", knee, 1.4)
        limb(m, "Accent", [knee, knee.lerp(ankle, 0.5), ankle, foot], (2.0, 1.7, 1.5, 1.7), sides=10)
        egg(m, "Shoe", tuple(foot + Vector((0, 1.4, -0.1))), 1.4, 2.8, 0.9, 12, 6)  # pointed show shoes
        egg(m, "Gold", tuple(foot + Vector((0, 0.6, 0.7))), 0.6, 0.4, 0.4, 8, 4)
    # One arm reaching out, presenting the show.
    shoulder, elbow, wrist = Vector((-5.2, 1.0, 18.6)), Vector((-8.6, 4.4, 14.0)), Vector((-6.2, 10.2, 14.4))
    m.use("ArmL", tuple(shoulder))
    limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5), elbow, elbow.lerp(wrist, 0.5), wrist], (2.6, 2.2, 1.9, 1.7, 1.7), sides=10)
    band(m, "Gold", tuple(elbow.lerp(wrist, 0.86)), 2.4, 2.4, length=0.7, tilt=tuple(wrist - elbow))
    glove(m, wrist, (0, 1, -0.1), 1.3)
    # The other raised, a whip curling from it.
    shoulder, elbow, wrist = Vector((5.2, 1.0, 18.6)), Vector((9.4, 2.2, 15.0)), Vector((9.6, 5.8, 18.6))
    m.use("ArmR", tuple(shoulder))
    limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5), elbow, elbow.lerp(wrist, 0.5), wrist], (2.6, 2.2, 1.9, 1.7, 1.7), sides=10)
    band(m, "Gold", tuple(elbow.lerp(wrist, 0.86)), 2.4, 2.4, length=0.7, tilt=tuple(wrist - elbow))
    egg(m, "Glove", tuple(wrist + Vector((0, 0.3, 0.6))), 1.4, 1.4, 1.3, 10, 5)
    sweep(m, "Accent", [(tuple(wrist + Vector((0, 0.2, 0.4))), 0.9, 0.9), (tuple(wrist + Vector((0.2, 0.6, 4.0))), 0.8, 0.8)], sides=8)  # the handle
    lash = curve([wrist + Vector((0.2, 0.6, 4.0)), wrist + Vector((0.6, -1.0, 8.0)), wrist + Vector((-0.6, -5.0, 9.0)), wrist + Vector((-1.6, -7.6, 5.0)), wrist + Vector((-1.0, -6.0, 1.0))], 16)
    sweep(m, "Whip", [(p_, 0.7 - 0.034 * i, 0.7 - 0.034 * i) for i, p_ in enumerate(lash)], sides=8)
    egg(m, "Neon", tuple(lash[-1]), 0.4, 0.4, 0.4, 8, 5)
    m.use("Neck", (0, 1.8, 19.6), "Spine")
    sweep_fine(m, "Belly", [((0, 1.4, 19.2), 2.6, 2.6), ((0, 2.4, 21.0), 2.2, 2.2), ((0, 3.0, 22.0), 2.4, 2.4)], sides=10, up=(0, -1, 0.1))
    m.use("Head", (0, 2.8, 22.2), "Neck")
    skull = [(0, 0.8, 0.0, 1.0), (0.2, 1.0, 0.0, 1.5), (0.44, 0.92, 0.0, 1.42), (0.68, 0.7, 0.0, 0.9), (0.9, 0.5, 0.0, 0.5), (1.0, 0.28, 0.04, 0.28)]
    jaw = [(0, 0.74, -0.46, 0.0), (0.36, 0.7, -0.44, 0.0), (0.7, 0.5, -0.36, 0.0), (0.94, 0.34, -0.3, 0.0), (1.0, 0.18, -0.2, -0.02)]
    y, zm, length, width, height = 1.8, 21.8, 8.8, 6.8, 4.2
    at = grin(m, y, zm, length, width, height, skull, jaw, 91, upper="Belly", lower="Belly", teeth=(14, 12), fang=1.0, gape=-0.34, t0=0.22, jaw_length=1.1)
    fair_eyes(m, at, 0.5, 0.84, 0.95, (0.3, 0.94, -0.06), lid="Belly", brow="Accent")
    for side in (-1, 1):  # a waxed moustache, curling up at both ends
        a = Vector((side * 0.3, y + length * 0.93, zm + height * 0.3))
        pts = curve([a, a + Vector((side * 1.8, -0.6, -0.4)), a + Vector((side * 3.6, -1.6, 0.2)), a + Vector((side * 4.0, -1.8, 1.6)), a + Vector((side * 3.4, -1.4, 2.2))], 10)
        sweep(m, "Accent", [(p_, 1.0 * math.sin(math.pi * (0.3 + 0.7 * i / 9)) + 0.15, 0.7 * math.sin(math.pi * (0.3 + 0.7 * i / 9)) + 0.12) for i, p_ in enumerate(pts)], sides=8)
    # The top hat, tipped back a little: brim, crown, a crimson band.
    hat = at(0.3, math.pi / 2) + Vector((0, -0.4, 0.4))
    up = unit((0, -0.22, 1))
    sweep_fine(m, "Accent", [(tuple(hat - up * 0.3), 9.2, 8.6), (tuple(hat + up * 0.3), 9.2, 8.6)], sides=20, per=1, up=(0, 1, 0))
    sweep(m, "Accent", [(tuple(hat), 5.6, 5.4), (tuple(hat + up * 6.4), 6.0, 5.8)], sides=20, up=(0, 1, 0))
    sweep(m, "Body", [(tuple(hat + up * 0.5), 5.84, 5.64), (tuple(hat + up * 1.6), 5.88, 5.68)], sides=20, caps=(False, False), up=(0, 1, 0))
    m.head_centre = (0, 8.4, 22.0)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Big Top Terror


def big_top_terror():
    """The boss: a hunched brute carrying the big top on its back. Bulbs round the valance, a ruff, a clown head with a crown of bulbs."""
    m = monster("dino_BigTopTerror", Body="#2e1834", Accent=CRIMSON, Belly=CREAM, Claw="#efe6d6", Glove="#f6f1e6")
    m.joint("Spine", (0, -2.0, 11.0))
    m.joint("Neck", (0, 4.0, 15.0), "Spine")
    m.joint("Head", (0, 5.4, 14.6), "Neck")
    trunk = [((0, -6.0, 8.4), 5.6, 5.0), ((0, -4.4, 10.4), 11.0, 9.0), ((0, -1.6, 13.0), 14.0, 10.6), ((0, 1.4, 15.0), 16.0, 10.4), ((0, 4.0, 15.4), 11.6, 8.4)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Neck"]
    sweep_fine(m, "Body", trunk, bones, sides=18, under="Belly", under_faces=5, per=4)
    # The big top on its back: gores of crimson and cream, a gold rim, a valance of scallops and bulbs, a pennant on its peak.
    m.bone = "Spine"
    tent = Vector((0, -2.0, 17.4))
    striped_tent(m, tent, 10.6, 9.4, 14.0, sectors=16)
    ring_round(m, "Gold", tuple(tent + Vector((0, 0, 0.2))), 10.0, (0, 0, 1), 0.6, 32, squash=0.89)
    for k in range(16):
        a = (k + 0.5) * math.tau / 16
        d = Vector((math.cos(a), math.sin(a) * 0.89, 0))
        base = tent + d * 10.4 + Vector((0, 0, 0.2))
        leaf(m, "Belly" if k % 2 else "Accent", tuple(base), tuple(base + d * 0.6 + Vector((0, 0, -2.6))), (-d.y, d.x, 0), 3.8, thick=0.3)
        b = tent + Vector((math.cos(a + math.pi / 16), math.sin(a + math.pi / 16) * 0.89, 0)) * 10.7
        egg(m, "Bulb", tuple(b + Vector((0, 0, 0.3))), 0.6, 0.6, 0.7, 8, 5)
    peak = tent + Vector((0, 0, 14.0))
    sweep(m, "Gold", [(tuple(peak - Vector((0, 0, 1.0))), 0.6, 0.6), (tuple(peak + Vector((0, 0, 4.4))), 0.5, 0.5)], sides=8)
    egg(m, "Bulb", tuple(peak + Vector((0, 0, 4.8))), 0.8, 0.8, 0.8, 8, 5)
    leaf(m, "Accent", tuple(peak + Vector((0, -0.1, 4.0))), tuple(peak + Vector((0, -4.6, 3.0))), (0, 0, 1), 2.4, thick=0.2)
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee, ankle, foot = Vector((side * 4.0, -4.2, 9.4)), Vector((side * 6.0, -0.6, 5.6)), Vector((side * 5.6, -4.4, 2.4)), Vector((side * 5.8, -2.6, 1.0))
        m.use(f"Leg{letter}", tuple(hip))
        knob(m, "Body", hip, 3.2)
        limb(m, "Body", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.5, 0.3, 0.4)), knee], (6.0, 5.2, 3.8), sides=12)
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        knob(m, "Body", knee, 2.2)
        limb(m, "Body", [knee, knee.lerp(ankle, 0.5) + Vector((0, -0.5, 0)), ankle, foot, foot + Vector((0, 2.8, -0.1))], (3.6, 3.0, 2.6, 2.8, 3.0), sides=10)
        for k in range(3):  # round toenails
            egg(m, "Claw", tuple(foot + Vector(((k - 1) * 1.3, 3.0, 0.1))), 0.7, 0.6, 0.5, 8, 4)
        shoulder, elbow, wrist = Vector((side * 7.6, 2.4, 14.6)), Vector((side * 12.0, 4.0, 8.8)), Vector((side * 10.0, 9.6, 4.4))
        m.use(f"Arm{letter}", tuple(shoulder))
        knob(m, "Body", shoulder + Vector((side * 0.4, 0, 0.4)), 3.8)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5) + Vector((side * 0.6, 0, 0.3)), elbow, elbow.lerp(wrist, 0.5), wrist], (6.0, 5.4, 4.2, 3.8, 3.6), sides=12)
        band(m, "Gold", tuple(elbow.lerp(wrist, 0.7)), 4.4, 4.4, length=1.2, tilt=tuple(wrist - elbow))
        glove(m, wrist + Vector((0, 0.2, -0.4)), (0, 1, -0.5), 2.2)
    m.bone = "Neck"
    ruff(m, (0, 4.6, 15.4), 4.8, 18, ("Accent", "Belly"), out=1.0, rise=0.1, w=3.6, tilt=0.35)
    m.bone = "Head"
    skull = [(0, 0.84, 0.0, 0.96), (0.22, 1.0, 0.0, 1.14), (0.48, 0.96, 0.0, 0.96), (0.72, 0.8, 0.0, 0.66), (0.92, 0.58, 0.0, 0.42), (1.0, 0.34, 0.04, 0.24)]
    jaw = [(0, 0.84, -0.66, 0.0), (0.3, 0.98, -0.72, 0.0), (0.6, 0.9, -0.6, 0.0), (0.85, 0.7, -0.44, 0.0), (0.97, 0.46, -0.3, 0.0), (1.0, 0.24, -0.2, -0.02)]
    y, zm, length, width, height = 4.6, 13.4, 12.6, 13.0, 6.4
    at = grin(m, y, zm, length, width, height, skull, jaw, 101, upper="Belly", lower="Body", teeth=(14, 12), fang=1.8, gape=-0.36, t0=0.26)
    fair_eyes(m, at, 0.56, 0.84, 1.6, (0.3, 0.94, -0.06), lid="Belly", brow="Accent")
    egg(m, "Accent", tuple(at(0.92, math.pi / 2) + Vector((0, 0.6, 0.4))), 1.9, 1.7, 1.6, 12, 6)  # its nose, a red bulb
    for k in range(5):  # a crown of bulbs on gold stalks
        a = math.pi / 2 + (k - 2) * 0.42
        spot = at(0.3, a)
        tip = spot + Vector((math.cos(a) * 1.4, -0.4, 2.4 + 0.5 * (2 - abs(k - 2))))
        sweep(m, "Gold", [(tuple(spot - Vector((0, 0, 0.4))), 0.6, 0.6), (tuple(tip), 0.5, 0.5)], sides=8)
        egg(m, "Bulb", tuple(tip + Vector((0, 0, 0.6))), 0.9, 0.9, 1.0, 10, 6)
    m.head_centre = (0, 15.0, 13.4)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Last Laugh


def last_laugh():
    """A hyena gone wrong: shoulders high, back sloping away, spotted, a studded collar it slipped, a grin right round its head."""
    m = monster("dino_LastLaugh", Body="#5b3a5e", Accent="#160b18", Belly="#cdb08e", Claw="#efe6d6", Collar=CRIMSON)
    m.joint("Spine", (0, -5.0, 8.4))
    m.joint("Maul", (0, 1.0, 11.0), "Spine")
    m.joint("Neck", (0, 5.0, 12.6), "Maul")
    rings = [((0, -11.6, 7.4), 2.6, 2.6), ((0, -9.6, 8.2), 7.4, 7.0), ((0, -5.2, 9.4), 8.6, 8.2), ((0, -0.8, 11.4), 10.4, 10.2), ((0, 3.0, 12.8), 10.8, 10.8), ((0, 6.0, 13.0), 7.6, 7.6)]
    bones = ["Spine", "Spine", "Spine", "Maul", "Maul", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=20, under="Belly", under_faces=6, per=4)
    blotch(m, rings, [(1.4, 1.0, 1.4, 1.8), (2.0, 0.55, 1.6, 2.0), (2.6, 1.15, 1.8, 2.0), (3.0, 0.5, 1.6, 1.8), (3.6, 1.0, 1.4, 1.6), (1.7, 0.2, 1.1, 1.4), (2.6, 0.15, 1.2, 1.4)], bones=bones)
    mane = [skin_at(rings, u, math.pi / 2, 0.6 + 0.5 * math.sin(math.pi * (u - 2.2) / 2.8))[0] for u in (2.2, 2.7, 3.2, 3.7, 4.2, 4.7, 5.0)]
    sweep_fine(m, "Accent", [(tuple(p_), 1.4, 1.2 + 1.2 * math.sin(math.pi * (k + 0.5) / 7)) for k, p_ in enumerate(mane)], ["Spine", "Maul", "Maul", "Maul", "Maul", "Neck", "Neck"], sides=8, per=3)  # a short mane
    m.bone = "Neck"
    band(m, "Collar", (0, 5.6, 13.0), 9.2, 9.2, length=1.6, bone="Neck", tilt=(0, 1, -0.3))
    for k in range(10):  # gold studs on it
        a = k * math.tau / 10
        d = Vector((math.cos(a), 0.3 * math.sin(a), math.sin(a))).normalized()
        knob(m, "Gold", Vector((0, 5.6, 13.0)) + d * 4.65, 0.55)
    for letter, side in (("L", -1), ("R", 1)):
        leg(m, f"Front{letter}", "Maul", [(side * 4.4, 2.8, 11.4), (side * 6.2, 4.2, 7.0), (side * 6.0, 3.6, 3.4), (side * 6.0, 5.0, 0.9)], (4.6, 3.6, 2.6, 2.6), toes=3, toe=(0.9, 1.3, 0.8))
        leg(m, f"Back{letter}", "Spine", [(side * 3.8, -7.6, 8.0), (side * 5.4, -5.2, 5.0), (side * 5.2, -7.8, 2.4), (side * 5.2, -6.4, 0.9)], (5.0, 3.6, 2.4, 2.4), toes=3, toe=(0.9, 1.2, 0.8))
    m.bone = "Spine"
    tail = curve([(0, -11.2, 7.8), (0, -13.6, 8.6), (0, -15.6, 7.4), (0, -16.8, 5.0)], 7)
    jointed(m, "Accent", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(tail, (1.4, 1.8, 2.4, 2.8, 2.6, 2.0, 0.8))], sides=8)
    m.use("Head", (0, 7.0, 12.0), "Neck")
    skull = [(0, 0.88, 0.0, 1.0), (0.24, 1.0, 0.0, 1.08), (0.5, 0.88, 0.0, 0.84), (0.74, 0.66, 0.0, 0.56), (0.92, 0.5, 0.0, 0.4), (1.0, 0.3, 0.04, 0.24)]
    jaw = [(0, 0.86, -0.6, 0.0), (0.3, 0.94, -0.62, 0.0), (0.62, 0.78, -0.5, 0.0), (0.88, 0.56, -0.36, 0.0), (1.0, 0.28, -0.22, -0.02)]
    y, zm, length, width, height = 5.8, 11.0, 10.4, 9.4, 5.0
    at = grin(m, y, zm, length, width, height, skull, jaw, 111, lower="Body", teeth=(14, 12), fang=1.5, gape=-0.4, t0=0.12, jaw_length=1.04)
    fair_eyes(m, at, 0.5, 0.84, 1.0, (0.3, 0.94, -0.06), brow="Accent")
    egg(m, "Accent", tuple(at(0.96, math.pi / 2) + Vector((0, 0.4, 0.2))), 1.1, 0.9, 0.8, 10, 5)  # its nose
    for side in (-1, 1):  # round ears, pricked
        ear = at(0.14, 1.0 if side > 0 else math.pi - 1.0)
        egg(m, "Body", tuple(ear + Vector((side * 0.8, -0.4, 1.4))), 0.6, 1.3, 1.6, 12, 6)
        egg(m, "Accent", tuple(ear + Vector((side * 0.8, 0.2, 1.4))), 0.3, 0.8, 1.1, 10, 5)
    m.head_centre = (0, 13.0, 11.6)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Unbearable


def unbearable():
    """The rarest: the dancing bear that got out. Reared up, its studded show collar, shackles on its wrists, paws like anvils."""
    m = monster("dino_Unbearable", Body="#2e1e1a", Accent=CRIMSON, Belly="#7c5a46", Claw="#f1e8d6")
    m.joint("Spine", (0, -5.0, 9.0))
    m.joint("Maul", (0, 0.0, 14.0), "Spine")
    m.joint("Neck", (0, 5.0, 16.0), "Maul")
    trunk = [((0, -8.6, 6.6), 6.4, 5.6), ((0, -6.4, 9.0), 13.0, 10.6), ((0, -3.0, 12.4), 16.4, 12.6), ((0, 0.6, 16.0), 19.6, 13.6), ((0, 3.6, 18.0), 18.6, 11.6), ((0, 6.0, 17.2), 11.0, 8.6)]
    bones = ["Spine", "Spine", "Spine", "Maul", "Maul", "Neck"]
    sweep_fine(m, "Body", trunk, bones, sides=22, under="Belly", under_faces=7, per=4)
    band(m, "Accent", (0, 5.8, 16.4), 11.4, 9.0, length=1.8, bone="Neck", tilt=(0, 1, -0.5))  # what's left of its show collar
    n = unit((0, 1, -0.5))
    v = unit(Vector((1, 0, 0)).cross(n))
    for k in range(9):  # gold studs round it
        a = math.pi * (0.1 + 0.8 * k / 8)
        d = Vector((math.cos(a), 0, 0)) * 5.7 + v * math.sin(a) * 4.5
        knob(m, "Gold", Vector((0, 5.8, 16.4)) + d * 1.02, 0.7)
    for letter, side in (("L", -1), ("R", 1)):
        hip, knee, ankle, foot = Vector((side * 5.0, -5.6, 8.4)), Vector((side * 7.4, -2.6, 5.0)), Vector((side * 7.0, -6.0, 2.2)), Vector((side * 7.2, -4.4, 0.9))
        m.use(f"Leg{letter}", tuple(hip))
        knob(m, "Body", hip, 3.8)
        limb(m, "Body", [hip, hip.lerp(knee, 0.5) + Vector((side * 0.6, 0.3, 0.3)), knee], (7.0, 6.0, 4.4), sides=12)
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        knob(m, "Body", knee, 2.6)
        limb(m, "Body", [knee, knee.lerp(ankle, 0.5) + Vector((0, -0.4, 0)), ankle, foot, foot + Vector((0, 2.6, -0.1))], (4.2, 3.6, 3.0, 3.2, 3.6), sides=10)
        egg(m, "Belly", tuple(foot + Vector((0, 1.6, -0.4))), 2.2, 2.6, 0.7, 10, 4)
        talons(m, foot + Vector((0, 3.6, 0)), (0, 1, -0.15), 4, 1.0, 0.9, 0.9)
        shoulder, elbow, wrist = Vector((side * 10.6, 1.4, 18.0)), Vector((side * 15.0, 3.4, 11.0)), Vector((side * 12.0, 11.0, 3.4))
        m.use(f"Arm{letter}", tuple(shoulder), "Maul")
        knob(m, "Body", shoulder, 5.8)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5), elbow], (8.6, 7.6, 5.8), sides=16)
        knob(m, "Body", elbow, 3.4)
        limb(m, "Body", [elbow, elbow.lerp(wrist, 0.5) + Vector((side * 0.6, 0, 0)), wrist], (5.8, 6.2, 6.0), sides=14)
        band(m, "Gold", tuple(elbow.lerp(wrist, 0.66) + Vector((side * 0.3, 0, 0))), 7.0, 7.0, length=1.8, tilt=tuple(wrist - elbow))  # the shackle
        c = elbow.lerp(wrist, 0.66) + Vector((side * 3.2, 0, -1.0))
        ring_round(m, "Gold", tuple(c), 1.2, (0, 1, 0), 0.4, 10)  # the broken chain
        ring_round(m, "Gold", tuple(c + Vector((side * 0.8, 0, -1.8))), 1.2, (1, 0, 0), 0.4, 10)
        paw = wrist + Vector((0, 0.8, -0.6))
        egg(m, "Body", tuple(paw), 4.6, 4.8, 3.0, 16, 8)
        egg(m, "Belly", tuple(paw + Vector((0, 0.6, -1.8))), 3.6, 3.8, 1.4, 12, 5)
        claws(m, paw + Vector((0, 3.4, 0.4)), (0, 1, -0.5), 5, 1.4, 1.4, 1.0, droop=0.3)
    m.use("Head", (0, 8.0, 15.4), "Neck")
    skull = [(0, 0.9, 0.0, 1.0), (0.24, 1.0, 0.0, 1.16), (0.46, 0.86, 0.0, 0.92), (0.68, 0.62, 0.0, 0.62), (0.9, 0.52, 0.0, 0.5), (1.0, 0.4, 0.04, 0.36)]
    jaw = [(0, 0.86, -0.56, 0.0), (0.3, 0.86, -0.56, 0.0), (0.62, 0.62, -0.44, 0.0), (0.88, 0.5, -0.34, 0.0), (1.0, 0.34, -0.24, -0.02)]
    y, zm, length, width, height = 6.8, 13.4, 10.6, 11.0, 5.8
    at = grin(m, y, zm, length, width, height, skull, jaw, 121, lower="Body", teeth=(12, 10), fang=1.9, gape=-0.42, t0=0.2, jaw_length=1.04)
    sweep_fine(m, "Belly", [(tuple(at(0.5, math.pi / 2) - Vector((0, 0, 0.4))), 3.4, 1.0), (tuple(at(0.8, math.pi / 2) - Vector((0, 0, 0.5))), 3.6, 1.0),
                            (tuple(at(0.98, math.pi / 2) - Vector((0, 0, 0.6))), 2.6, 0.9)], sides=8)  # the paler muzzle
    egg(m, "Socket", tuple(at(0.98, math.pi / 2) + Vector((0, 0.5, 0.2))), 1.6, 1.0, 0.9, 10, 5)  # its nose
    fair_eyes(m, at, 0.42, 0.86, 1.0, (0.3, 0.94, -0.08), top=0.3, tilt=0.12)
    for side in (-1, 1):  # round ears, one torn
        ear = at(0.12, 1.1 if side > 0 else math.pi - 1.1)
        egg(m, "Body", tuple(ear + Vector((side * 1.0, -0.6, 1.8))), 2.2, 1.2, 2.2 if side > 0 else 1.5, 12, 6)
        egg(m, "Belly", tuple(ear + Vector((side * 1.0, 0.1, 1.8))), 1.3, 0.7, 1.3 if side > 0 else 0.9, 10, 5)
    m.head_centre = (0, 16.0, 14.0)
    grounded(m)
    return m


ALL = [jack_snap, popcorn_fiend, twisty, nightmare_mare, grinmaster, big_top_terror, last_laugh, unbearable]


def main():
    rare_kit.animate = animate  # run() films with it: build_spore_hollow_toxic's, which stacks the thrash and the rage on rare_kit's markers
    rare_kit.run(ALL, RENDERS, BLEND, "midnight_carnival_fright", SKY, FLOOR, GLOW_ROLES, glow=1.0, spacing=40)


if __name__ == "__main__":
    main()
