"""Builds Shattered Mirror's monsters (map 16), animates them and renders them (Blender, background mode).

    Blender -b -P build_shattered_mirror_monsters.py
    QUICK=1 QUICK_OUT=<folder> Blender -b -P build_shattered_mirror_monsters.py    (stills only)
    ONLY=mane_event QUICK=1 ...                                                    (just those)

Saves shattered_mirror_monsters.blend and renders to design/world/monsters_shattered_mirror/.

The owner, 2026-11-13: twelve monsters for this map, "aggressive, but at the same time magnificent", not too aggressive, the
map's theme, each with an animation of its own and an aggression that looks like nothing else in the game. Their own example:
a monster whose skin is covered in shards that slide out of it and back in, in waves, like a stadium wave ("not float, but get
out of him and then go back in"), on one monster, not all. Built six at a time, a prompt each (owner's choice to leave to us).

The world on the other side of the glass: pearl dawn, chrome, gilt, smoked violet glass, porcelain, velvet, rainbow light, and
the reflections are wrong. The face they share: cold cyan slit eyes (the map's Gleam) under brows of chrome, fangs of glass.
They are beautiful first and dangerous second: smooth bodies, chrome and gilt, crests and manes of mirror shards, poised, never
drooling or rotting. Chrome and gilt are real metal in the game (METAL, as the world's props: studio_tidy gives those parts the
HoloChrome and PolishedGold MaterialVariants and no studs). Skin roles Body, Accent, Belly and Claw take the colour mutations.

The first six, most common first, each with its attack (4 seconds, once every DinoLife.attackCycle; the preview plays it nonstop):

  Paw de Deux       a smoked-glass panther with a crest of mirror shards. It circles you, sidestepping right round with its eyes
                    on you the whole way, crouches, wriggles and springs, raking with one paw and then the other (Prowl)
  Frill Seeker      a porcelain and velvet lizard with a kaleidoscope for a frill, chrome and rainbow glass petals that never stop
                    turning. It rears onto its hind legs, the frill whirls, and it runs at you on two legs hissing (Frill, Rosette)
  Dressed to Kill   a porcelain mannequin whose head is a gilt hand mirror with a face in it. It turns its head right round to look
                    behind it, holds, snaps it the rest of the way round, then lunges like a broken doll, in jerks (Twist)
  Wrecking Ballroom an armoured beast tiled in mirrors with a mirror ball for a tail club, always turning. It swings the tail like
                    a pendulum, higher each time, heaves it over its back and slams it down (Swing, Club)
  Swanquish         a swan and its reflection: one body, two necks, white on one side and black on the other, a gilt line where
                    they meet. Whatever one neck does the other does mirrored, always. It flares its wings, both necks coil, and
                    they strike together like shears (Reflect)
  Mane Event        a lion with a mane of mirror shards. A wave runs round the mane and down its back for ever, each shard sliding
                    out of the skin and back in (the owner's stadium wave). It rears up rampant, every shard bursts out at once
                    and rattles, it roars, slams down, and the shards ripple back in (Rampant, Sliver1 to 20)

The next six (a later prompt; the plan, not built): Out of Line (a wolf of glass slices that slide out of line like a broken
reflection and snap back as it lunges), a mirror-winged moth whose wings clap shut, Rose Windowmaker (a beetle whose stained-glass
shell opens like cathedral doors), Vainglory (a peacock-like beast whose train of mirror eyes fans open before it charges), and the
two rarest, ending with the thing that stands in the mirrors stepping out of its broken frame.

What moves is in the tables at the bottom, the same as the map-16 block in DinoLifeController, number for number. New there: a
marker table can hold "@always", moves that run all the time on top of everything (the mane's wave, the frill's and the mirror
ball's turning, the swan's mirrored necks), as Sway does, while the rest waits for the attack. 1 Blender unit = 1 stud, models
face +Y, feet on Z = 0. Plain colours, no stud image.
"""
import math
import os
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402  (first: it turns the stud preview off)
import build_forest as kit  # noqa: E402
import build_shattered_mirror as world  # noqa: E402  (the chrome in the renders)
import monster_stage  # noqa: E402
from build_clockwork_citadel_monsters_7_8 import limb  # noqa: E402
from build_forest import Model  # noqa: E402
from build_special_monsters import shell  # noqa: E402
from build_spore_hollow_monsters import egg  # noqa: E402
from build_spore_hollow_toxic import grounded, leg, skin_at, stripes, tox_eye, unit  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from build_volcano import idle_pose as volcano_idle, walk_pose as volcano_walk  # noqa: E402
from build_weeping_dark_dread import claws  # noqa: E402
from fierce_kit import band, fierce_head, horn, knob  # noqa: E402
from rare_kit import (AHEAD, PITCH, RISE, ROLL, W, WALK_PREVIEW, YAW, beat, curve, jointed, keys, leaf, marked_of, ring_round, sabre,  # noqa: E402
                      stacked, sway, sweep, sweep_fine, wave)

RENDERS = HERE.parent.parent / "design" / "world" / "monsters_shattered_mirror"
BLEND = "shattered_mirror_monsters"  # for check_map.py and export_fbx.py
SPECTRUM = ("SpecA", "SpecB", "SpecC", "SpecD", "SpecE")  # the world's rainbow glass, glowing (shared/Roles.luau)
GLOW_ROLES = {"EyeGlow", *SPECTRUM}
METAL = {"Chrome": "HoloChrome", "ChromeDark": "HoloChrome", "Gilt": "PolishedGold"}  # studio_tidy reads this
kit.NO_STUDS.update(GLOW_ROLES | set(METAL) | {"Socket", "Slit"})

GLEAM = "#7ff3ff"  # the world's cold eyes
FACE = {"Pupil": "#04121a", "Slit": "#04121a", "Socket": "#07060f", "Highlight": "#ffffff", "EyeGlow": GLEAM, "Mouth": "#1a1030", "Tongue": "#3d1d4f",
        "Teeth": "#e9f7ff", "Chrome": "#eef2f8", "ChromeDark": "#8d8fa3", "Gilt": "#f4ca68",
        "SpecA": "#ff5c8a", "SpecB": "#ffb547", "SpecC": "#5cf5a8", "SpecD": "#56c8ff", "SpecE": "#a77bff"}
SKY, FLOOR = "#efd9e6", "#a7abbd"


def monster(name, **colours):
    return Model(name, {**FACE, **colours})


# ---------------------------------------------------------------------- shapes


def shard(m, role, base, tip, w, sides=4, belly=0.3, turn=None):
    """A crystal: a faceted spike from base to tip, widest a third of the way up, cut sharp at the tip."""
    a, b = Vector(base), Vector(tip)
    sweep(m, role, [(tuple(a), w * 0.55, w * 0.55), (tuple(a.lerp(b, belly)), w, w), (tuple(a.lerp(b, 0.78)), w * 0.5, w * 0.5), (tuple(b), 0.03, 0.03)],
          sides=sides, turn=turn)


def glare(m, at, spots, lid="Body", ridge="Chrome"):
    """The set's face: cold cyan slit eyes sunk under brows of chrome. spots are (t, angle, size, look), both sides; the first pair
    are the main eyes (Pupil, which the reveal aims at), the rest spare (Slit)."""
    for side in (-1, 1):
        for k, (t, a, r, look) in enumerate(spots):
            spot = at(t, a if side > 0 else math.pi - a)
            tox_eye(m, spot, r, (side * look[0], look[1], look[2]), side, socket=1.8 if k == 0 else 1.5, lid=lid, pupil="Pupil" if k == 0 else "Slit",
                    ridge=ridge if k == 0 else None, ridge_size=1.3, top=0.42, low=0.3, slit=0.2)


def mark(m):
    """How much of each role is built so far, for grown() to find what came after."""
    return {role: len(verts) for role, (verts, _) in m.parts.items()}, set(m.joints)


def grown(m, since, pivot, k):
    """Everything built since mark() made k times bigger round pivot, its new joints too: a head made at one size and wanted bigger."""
    counts, joints = since
    c = Vector(pivot)
    for role, (verts, _) in m.parts.items():
        for i in range(counts.get(role, 0), len(verts)):
            verts[i] = tuple(c + (Vector(verts[i]) - c) * k)
    for name, (at, parent) in list(m.joints.items()):
        if name not in joints:
            m.joints[name] = (tuple(c + (Vector(at) - c) * k), parent)


def plate(m, role, corners, thick=0.12):
    """A flat facet through corners, lifted off what it lies on: a mirror tile, a chrome mask."""
    rare_kit.panel(m, role, [tuple(c) for c in corners], thick)


def mask(m, at, t0, t1, spread, lift=0.1, role="Chrome", count=10):
    """A kite of chrome down the brow and the bridge of the nose, from t0 to t1 along the skull, following its curve the same height
    above it all the way (a flat plate on a round skull sinks into it in the middle and shimmers). spread: its widest, in studs."""
    path = []
    for i in range(count + 1):
        t = t0 + (t1 - t0) * i / count
        p = at(t, math.pi / 2)
        side = at(t, math.pi / 2 - 0.12) - at(t, math.pi / 2 + 0.12)
        ahead = at(min(t + 0.02, 1.0), math.pi / 2) - at(max(t - 0.02, 0.0), math.pi / 2)
        q = i / count
        width = spread * max(0.06, math.sin(math.pi * min(q / 0.84, 1.0) ** 0.8)) if q < 0.84 else spread * 0.06 + spread * 0.3 * (1 - q)
        path.append((tuple(p + unit(side.cross(ahead)) * lift), width, 0.1))
    sweep(m, role, path, sides=4)


def crest(m, rings, bones, spots, role="Chrome", lean=0.5, w=0.42):
    """Mirror shards standing up out of a body's back: spots are (u, height)."""
    for u, h in spots:
        at, n = skin_at(rings, u, math.pi / 2)
        m.bone = bones[min(round(u), len(bones) - 1)]
        shard(m, role, tuple(at - n * 0.4), tuple(at + n * h + Vector((0, -h * lean, 0))), w + h * 0.12)


# ---------------------------------------------------------------------- Paw de Deux


def paw_de_deux():
    """A panther of smoked glass, long and low, a crest of mirror shards down its back and a mirror kite down its brow."""
    m = monster("dino_PawDeDeux", Body="#2c2850", Accent="#121026", Belly="#8e86c4", Claw="#eef6ff")
    m.joint("Spine", (0, -4.5, 6.4))
    m.joint("Prowl", (0, 1.8, 7.0), "Spine")
    m.joint("Neck", (0, 4.8, 7.8), "Prowl")
    rings = [((0, -8.4, 6.4), 2.4, 2.4), ((0, -6.8, 6.9), 4.8, 4.8), ((0, -3.6, 6.7), 4.0, 4.0), ((0, -0.2, 7.0), 4.8, 5.1), ((0, 2.6, 7.4), 5.4, 5.8),
             ((0, 5.0, 8.0), 3.5, 3.8), ((0, 6.8, 8.2), 3.0, 3.0)]
    bones = ["Spine", "Spine", "Spine", "Prowl", "Prowl", "Neck", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=16, under="Belly", under_faces=5, per=4)
    crest(m, rings, bones, [(0.9, 1.2), (1.5, 1.6), (2.1, 1.9), (2.7, 2.3), (3.3, 2.7), (3.9, 2.4), (4.5, 1.8)])
    for side in (-1, 1):  # shards off the shoulders, swept back
        for k, (u, a, h) in enumerate(((3.5, 0.75, 1.9), (3.9, 0.45, 1.3))):
            at, n = skin_at(rings, u, a if side > 0 else math.pi - a)
            m.bone = "Prowl"
            shard(m, "Chrome" if k == 0 else "ChromeDark", tuple(at - n * 0.3), tuple(at + n * h + Vector((0, -h * 0.8, 0))), 0.5)
    for letter, side in (("L", -1), ("R", 1)):
        leg(m, f"Front{letter}", "Prowl", [(side * 2.3, 2.6, 6.6), (side * 2.7, 3.5, 3.8), (side * 2.5, 2.7, 1.4), (side * 2.5, 3.4, 0.55)], (2.6, 1.9, 1.35, 1.4),
            toes=0, pad=1.2)
        claws(m, (side * 2.5, 4.4, 0.6), (0, 1, -0.1), 4, 0.42, 1.2, 0.34, droop=0.4)
        leg(m, f"Back{letter}", "Spine", [(side * 2.3, -6.4, 6.4), (side * 2.7, -4.8, 3.9), (side * 2.5, -7.5, 1.8), (side * 2.5, -6.7, 0.55)], (3.2, 2.2, 1.4, 1.4),
            toes=0, pad=1.2)
        claws(m, (side * 2.5, -5.8, 0.6), (0, 1, -0.1), 4, 0.42, 1.0, 0.32, droop=0.4)
    tail = curve([(0, -8.0, 6.4), (0, -10.6, 7.4), (0, -12.9, 9.2), (0, -14.3, 11.4), (0, -14.1, 13.2)], 10)
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(tail, (1.5, 1.35, 1.2, 1.1, 1.0, 0.95, 0.9, 0.85, 0.8, 0.7))], sides=8)
    m.bone = "Tail3"
    tip = Vector(tail[-1])
    for k, d in enumerate(((0, -0.3, 1), (0.6, -0.5, 0.7), (-0.6, -0.5, 0.7))):  # a tuft of shards on the tip
        shard(m, "Chrome", tuple(tip - unit(d) * 0.3), tuple(tip + unit(d) * (1.7 - 0.4 * (k > 0))), 0.45)
    m.use("Head", (0, 6.9, 8.1), "Neck")
    # A cat's head: a round skull, a short broad muzzle, cheeks wider than the jaw, small round ears set wide.
    skull = [(0, 0.95, 0.0, 1.15), (0.25, 1.0, 0.0, 1.25), (0.5, 0.92, 0.0, 1.0), (0.72, 0.74, 0.0, 0.72), (0.9, 0.62, 0.02, 0.5), (1.0, 0.5, 0.05, 0.34)]
    jaw = [(0, 0.88, -0.52, 0.0), (0.35, 0.84, -0.48, 0.0), (0.7, 0.66, -0.38, 0.0), (0.92, 0.52, -0.28, 0.0), (1.0, 0.4, -0.2, -0.02)]
    at = fierce_head(m, 6.4, 7.9, 3.9, 4.2, 2.9, skull, jaw, gape=-0.3, teeth=(9, 8), tall=0.55, base=0.22, fangs=((0.84, 1.45),), low_fangs=((0.8, 1.0),),
                     seed=61, t0=0.2)
    glare(m, at, [(0.48, 1.08, 0.42, (0.3, 0.95, -0.04))])
    mask(m, at, 0.14, 0.86, 2.0)
    for side in (-1, 1):
        cheek = at(0.32, 0.25 if side > 0 else math.pi - 0.25)
        egg(m, "Body", tuple(cheek + Vector((side * 0.15, -0.2, -0.1))), 0.9, 1.3, 0.95, 10, 5)
        ear = at(0.1, 1.05 if side > 0 else math.pi - 1.05)
        egg(m, "Body", tuple(ear + Vector((side * 0.35, -0.3, 0.55))), 0.62, 0.3, 0.72, 10, 5)
        egg(m, "Accent", tuple(ear + Vector((side * 0.35, -0.08, 0.55))), 0.36, 0.14, 0.44, 8, 4)
        for k, (dx, dz, h) in enumerate(((0.35, 0.0, 2.2), (0.9, -0.3, 1.5))):  # chrome swept back off the brow, into the crest
            base = at(0.2, 1.25 if side > 0 else math.pi - 1.25) + Vector((side * dx, -0.2, dz))
            shard(m, "Chrome" if k == 0 else "ChromeDark", tuple(base), tuple(base + Vector((side * 0.35 * h, -h, 0.45 * h))), 0.38)
    egg(m, "Accent", tuple(at(0.97, math.pi / 2) + Vector((0, 0.05, -0.05))), 0.62, 0.34, 0.3, 8, 4)  # the nose
    m.head_centre = (0, 8.8, 8.2)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Frill Seeker

FRILL_AT = (0, 4.0, 5.0)  # the frill's hub: Frill and Rosette turn round it, on the forward axis


def frill_seeker():
    """A porcelain lizard banded in velvet, sprawled low, and round its neck a kaleidoscope: chrome petals and rainbow glass."""
    m = monster("dino_FrillSeeker", Body="#efe7de", Accent="#7a2c52", Belly="#d8d2e6", Claw="#2a2440", Mouth="#8a2350")
    m.joint("Spine", (0, -3.2, 3.6))
    m.joint("Neck", (0, 2.6, 4.3), "Spine")
    rings = [((0, -6.2, 3.4), 2.2, 2.0), ((0, -4.2, 3.7), 4.0, 3.2), ((0, -1.0, 3.9), 4.6, 3.4), ((0, 1.8, 4.1), 3.8, 3.0), ((0, 3.6, 4.6), 2.4, 2.3),
             ((0, 4.8, 5.0), 2.0, 2.0)]
    bones = ["Spine", "Spine", "Spine", "Spine", "Neck", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=14, under="Belly", under_faces=5, per=4)
    stripes(m, rings, (0.8, 1.5, 2.2, 2.9), "Accent", bones, grow=1.09, length=0.55)  # velvet bands, standing clear of the belly so they don't shimmer
    crest(m, rings, bones, [(0.5, 0.7), (1.0, 0.9), (1.5, 1.1), (2.0, 1.1), (2.5, 1.0), (3.0, 0.8)], lean=0.6, w=0.3)
    for letter, side in (("L", -1), ("R", 1)):  # sprawled legs, long toes
        leg(m, f"Front{letter}", "Spine", [(side * 1.8, 1.6, 3.8), (side * 3.5, 2.1, 3.1), (side * 3.8, 2.8, 1.1), (side * 4.0, 3.5, 0.45)], (1.6, 1.2, 0.9, 0.8),
            toes=4, toe=(0.42, 1.4, 0.22))
        leg(m, f"Back{letter}", "Spine", [(side * 1.9, -4.6, 3.6), (side * 3.9, -4.0, 3.2), (side * 4.2, -5.5, 1.1), (side * 4.4, -4.8, 0.45)], (2.0, 1.5, 1.0, 0.85),
            toes=4, toe=(0.45, 1.6, 0.24))
    tail = curve([(0, -6.0, 3.4), (0, -9.0, 2.8), (0, -12.5, 1.8), (0, -16.0, 1.1), (0, -19.0, 0.9)], 11)
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w * 0.9) for p, w in zip(tail, (2.0, 1.8, 1.6, 1.4, 1.2, 1.0, 0.85, 0.7, 0.55, 0.4, 0.22))], sides=8)
    for k, i in enumerate((2, 4, 6, 8)):  # velvet rings down the tail
        p = Vector(tail[i])
        band(m, "Accent", tuple(p), (2.0 - 0.18 * i) * 1.16, (2.0 - 0.18 * i) * 1.06, length=0.4, bone=["Tail1", "Tail2", "Tail2", "Tail3"][k],
             tilt=tuple(Vector(tail[i + 1]) - Vector(tail[i - 1])))
    m.use("Head", (0, 4.6, 5.0), "Neck")
    skull = [(0, 0.9, 0.0, 1.0), (0.3, 0.95, 0.0, 0.95), (0.6, 0.75, 0.0, 0.7), (0.85, 0.55, 0.02, 0.45), (1.0, 0.32, 0.05, 0.25)]
    jaw = [(0, 0.85, -0.5, 0.0), (0.4, 0.8, -0.45, 0.0), (0.75, 0.58, -0.32, 0.0), (1.0, 0.3, -0.18, -0.02)]
    at = fierce_head(m, 4.3, 4.9, 4.4, 2.7, 2.0, skull, jaw, gape=-0.5, teeth=(12, 10), tall=0.32, base=0.14, fangs=((0.9, 0.7),), seed=62, t0=0.18)
    glare(m, at, [(0.4, 0.78, 0.34, (0.7, 0.68, 0.06))])
    mask(m, at, 0.3, 0.92, 1.1, lift=0.08)
    for side in (-1, 1):  # chrome horns over the eyes
        spot = at(0.3, 1.15 if side > 0 else math.pi - 1.15)
        shard(m, "Chrome", tuple(spot - Vector((0, 0, 0.2))), tuple(spot + Vector((side * 0.5, -1.0, 0.9))), 0.3)
    # The frill: a hub on Frill (its marker, which whirls it in the attack), and on Rosette, turning for ever, ten petals: chrome
    # in front and rainbow glass a little behind, alternating, on a velvet back and inside a gilt rim.
    c = Vector(FRILL_AT)
    m.use("Frill", tuple(c), "Neck")
    ring_round(m, "Gilt", tuple(c + Vector((0, 0.15, 0))), 1.45, (0, 1, 0), 0.26, 18)
    m.use("Rosette", tuple(c), "Frill")
    egg(m, "Accent", tuple(c + Vector((0, -0.42, 0))), 4.1, 0.14, 4.1, 24, 4)
    for k in range(10):
        a = k * math.tau / 10 + math.pi / 10
        out = Vector((math.cos(a), 0, math.sin(a)))
        across = Vector((-math.sin(a), 0, math.cos(a)))
        if k % 2 == 0:
            leaf(m, "Chrome", tuple(c + out * 1.4), tuple(c + out * 5.1), tuple(across), 2.0, thick=0.12)
            shard(m, "Chrome", tuple(c + out * 4.6 + Vector((0, 0.06, 0))), tuple(c + out * 5.9 + Vector((0, 0.06, 0))), 0.3)
        else:
            body = c + Vector((0, -0.16, 0))
            leaf(m, SPECTRUM[k // 2], tuple(body + out * 1.4), tuple(body + out * 4.7), tuple(across), 2.2, thick=0.1)
    ring_round(m, "Gilt", tuple(c + Vector((0, -0.08, 0))), 4.25, (0, 1, 0), 0.16, 40)
    m.bone = "Head"
    m.head_centre = (0, 6.6, 5.2)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Dressed to Kill


def dressed_to_kill():
    """A porcelain mannequin, dark ball joints, long chrome fingers, and for a head a gilt hand mirror with a face looking out of it."""
    m = monster("dino_DressedToKill", Body="#f2ece5", Accent="#2a2540", Belly="#d9cfc3", Claw="#2a2540")
    m.joint("Spine", (0, 0, 7.8))
    m.joint("Twist", (0, 0.15, 10.2), "Spine")
    m.joint("Neck", (0, 0.3, 13.4), "Twist")
    torso = [((0, 0, 6.9), 3.0, 2.2), ((0, 0.05, 7.9), 3.8, 2.5), ((0, 0.1, 9.0), 3.4, 2.3), ((0, 0.15, 9.9), 2.5, 1.9), ((0, 0.2, 11.2), 3.8, 2.4),
             ((0, 0.25, 12.4), 4.6, 2.6), ((0, 0.3, 13.1), 3.4, 2.2), ((0, 0.3, 13.5), 1.5, 1.3)]
    sweep_fine(m, "Body", torso, ["Spine", "Spine", "Spine", "Twist", "Twist", "Twist", "Twist", "Twist"], sides=16, per=3, up=(0, 1, 0))
    m.bone = "Twist"
    ring_round(m, "Accent", (0, 0.15, 9.95), 1.35, (0, 0, 1), 0.34, 16, squash=0.76)  # the swivel at the waist
    ring_round(m, "Gilt", (0, 0.3, 13.55), 0.72, (0, 0, 1), 0.26, 16, squash=0.9)  # a gilt collar round the base of the neck
    for k, (x, z) in enumerate(((-0.9, 11.6), (0.5, 12.3), (1.2, 11.2))):  # a crack across the chest, cold light in it
        a, b = Vector((x, 1.36, z)), Vector((x + (0.7 if k != 1 else 0.6), 1.3, z - 0.55))
        sweep(m, "EyeGlow", [(tuple(a), 0.09, 0.09), (tuple(b), 0.05, 0.05)], sides=4)
    for letter, side in (("L", -1), ("R", 1)):
        shoulder, elbow, wrist = Vector((side * 2.5, 0.3, 12.6)), Vector((side * 3.2, 0.2, 9.9)), Vector((side * 3.3, 1.1, 7.5))
        m.use(f"Arm{letter}", tuple(shoulder), "Twist")
        knob(m, "Accent", shoulder, 0.95)
        limb(m, "Body", [shoulder, shoulder.lerp(elbow, 0.5), elbow], (1.15, 1.0, 0.85), sides=10)
        m.use(f"Fore{letter}", tuple(elbow), f"Arm{letter}")
        knob(m, "Accent", elbow, 0.7)
        limb(m, "Body", [elbow, elbow.lerp(wrist, 0.5), wrist], (0.82, 0.72, 0.6), sides=10)
        egg(m, "Body", tuple(wrist + Vector((0, 0.25, -0.4))), 0.5, 0.6, 0.75, 10, 5)  # the hand
        for f in range(4):  # long chrome fingers, curled like claws
            base = wrist + Vector((side * (f - 1.5) * 0.12 + side * 0.0, 0.45, -0.7 - 0.05 * abs(f - 1.5)))
            spread = (f - 1.5) * 0.25
            sabre(m, "Chrome", [tuple(base), tuple(base + Vector((side * spread, 0.9, -0.9))), tuple(base + Vector((side * spread * 1.4, 1.5, -2.4)))], 0.22, 7)
        hip, knee, ankle = Vector((side * 1.15, 0, 7.3)), Vector((side * 1.25, 0.4, 4.2)), Vector((side * 1.25, -0.1, 1.05))
        m.use(f"Leg{letter}", tuple(hip), "Spine")
        knob(m, "Accent", hip + Vector((0, 0, -0.1)), 0.9)
        limb(m, "Body", [hip, hip.lerp(knee, 0.5), knee], (1.5, 1.3, 1.05), sides=10)
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        knob(m, "Accent", knee, 0.68)
        limb(m, "Body", [knee, knee.lerp(ankle, 0.5), ankle], (0.98, 0.82, 0.68), sides=10)
        sweep_fine(m, "Body", [((side * 1.25, -0.5, 0.7), 0.8, 0.9), ((side * 1.25, 0.4, 0.55), 0.85, 0.7), ((side * 1.25, 1.5, 0.3), 0.45, 0.3)], sides=8, per=2)
    # The head: a hand mirror. Porcelain behind, a gilt frame, a chrome glass with two cold eyes in it, and its lower third the jaw,
    # which splits from the rest along a crack and opens on teeth of glass.
    # Dressed: a peplum of mirror shards hanging from the hips, and shards fanned off the shoulders.
    m.bone = "Spine"
    for k in range(16):
        a = k * math.tau / 16 + 0.1
        out = Vector((math.cos(a) * 1.0, math.sin(a) * 0.72, 0))
        base = Vector((0, 0.05, 8.1)) + out * 1.75
        length = 2.6 + 0.5 * (k % 2) - 0.6 * max(math.sin(a), 0) ** 2  # shorter at the front, longest at the back and sides
        shard(m, "Chrome" if k % 2 == 0 else "ChromeDark", tuple(base), tuple(base + out * 0.75 + Vector((0, 0, -length))), 0.62, belly=0.22)
    ring_round(m, "Gilt", (0, 0.05, 8.25), 1.86, (0, 0, 1), 0.2, 20, squash=0.74)
    for letter, side in (("L", -1), ("R", 1)):
        m.bone = "Twist"
        for k, (dy, h, tilt) in enumerate(((0.0, 2.2, 0.3), (-0.5, 1.6, 0.55), (0.5, 1.5, 0.05))):
            base = Vector((side * 2.2, 0.3 + dy, 13.0))
            shard(m, "Chrome" if k == 0 else "ChromeDark", tuple(base), tuple(base + Vector((side * h * 0.8, dy * 0.6, h * (0.45 + tilt)))), 0.42)
    m.use("Head", (0, 0.4, 14.3), "Neck")
    head = mark(m)
    sweep_fine(m, "Belly", [((0, 0.3, 13.3), 1.1, 1.1), ((0, 0.35, 14.2), 0.9, 0.9), ((0, 0.4, 14.6), 1.2, 1.2)], sides=10, per=2)
    egg(m, "Body", (0, 0.35, 15.4), 1.5, 1.15, 1.95, 14, 8)  # stops well short of the glass's front, or the two fight
    egg(m, "Chrome", (0, 1.25, 15.85), 1.32, 0.62, 1.18, 16, 8)
    egg(m, "Mouth", (0, 1.15, 14.62), 0.95, 0.5, 0.36, 12, 6)
    for k in range(7):  # upper teeth, hanging from the crack
        x = (k - 3) * 0.24
        sabre(m, "Teeth", [(x, 1.48 - 0.12 * abs(k - 3) ** 1.3, 14.86), (x * 1.02, 1.55 - 0.12 * abs(k - 3) ** 1.3, 14.6),
                           (x * 1.04, 1.58 - 0.12 * abs(k - 3) ** 1.3, 14.38 + 0.05 * abs(k - 3))], 0.17, 5)
    m.use("Jaw", (0, 0.55, 14.55), "Head")
    egg(m, "Chrome", (0, 1.15, 14.08), 1.0, 0.56, 0.62, 14, 6)
    for k in range(6):
        x = (k - 2.5) * 0.24
        sabre(m, "Teeth", [(x, 1.42 - 0.12 * abs(k - 2.5) ** 1.3, 14.46), (x, 1.47 - 0.12 * abs(k - 2.5) ** 1.3, 14.62), (x, 1.5 - 0.12 * abs(k - 2.5) ** 1.3, 14.78)], 0.14, 5)
    rare_kit.swing(m, ["Jaw"], (0, 0.55, 14.55), -0.2)
    m.bone = "Head"
    ring_round(m, "Gilt", (0, 1.05, 15.3), 1.5, (0, 1, 0), 0.24, 28, squash=1.32)
    for z, r in ((17.3, 0.36), (13.3, 0.3)):  # the frame's ornaments, top and bottom
        egg(m, "Gilt", (0, 1.1, z), r, r, r, 10, 5)
    for k, (dx, h) in enumerate(((0, 1.9), (-0.55, 1.4), (0.55, 1.4), (-1.05, 0.9), (1.05, 0.9))):  # a broken tiara of shards
        base = Vector((dx, 0.85, 17.05 - abs(dx) * 0.35))
        shard(m, "Chrome" if k % 2 == 0 else "ChromeDark", tuple(base), tuple(base + Vector((dx * 0.4, -0.25, h))), 0.34)
    for side in (-1, 1):
        tox_eye(m, (side * 0.46, 1.8, 16.0), 0.24, (side * 0.18, 1, 0.02), side, socket=1.7, lid="Chrome", ridge="ChromeDark", ridge_size=1.2, top=0.4, low=0.3)
    for a, b in (((0.62, 1.86, 16.65), (0.95, 1.7, 16.2)), ((0.62, 1.86, 16.65), (0.2, 1.84, 16.9)), ((0.95, 1.7, 16.2), (1.12, 1.45, 15.6)),
                 ((0.2, 1.84, 16.9), (-0.35, 1.78, 16.95))):  # a crack in the glass, cold light in it
        sweep(m, "EyeGlow", [(a, 0.08, 0.08), (b, 0.06, 0.06)], sides=4)
    grown(m, head, (0, 0.4, 13.9), 1.3)
    m.head_centre = (0, 2.0, 15.8)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Wrecking Ballroom

CLUB_AT = (0, -19.0, 3.4)  # the mirror ball: Club turns it round the tail's own axis


def wrecking_ballroom():
    """A low armoured beast tiled in mirrors like a ballroom's ball, gilt spikes down its flanks, and a mirror ball for a club."""
    m = monster("dino_WreckingBallroom", Body="#3f3a72", Accent="#1c1838", Belly="#cfc8e2", Claw="#efe7de")
    m.joint("Spine", (0, -3.0, 5.2))
    m.joint("Swing", (0, 1.6, 5.6), "Spine")
    m.joint("Neck", (0, 5.0, 5.0), "Swing")
    rings = [((0, -7.8, 4.9), 3.0, 2.6), ((0, -6.0, 5.5), 7.6, 5.2), ((0, -2.6, 6.1), 10.0, 6.4), ((0, 1.0, 6.1), 9.6, 6.2), ((0, 3.8, 5.6), 6.6, 4.6),
             ((0, 5.6, 5.0), 3.8, 3.2)]
    bones = ["Spine", "Spine", "Spine", "Swing", "Swing", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=20, under="Belly", under_faces=7, per=4)
    for u in (1.0, 1.6, 2.2, 2.8, 3.4, 4.0):  # mirror tiles over the back, in rows
        for j in range(7):
            a = math.pi / 2 + (j - 3) * 0.27
            at, n = skin_at(rings, u, a)
            m.bone = bones[min(round(u), len(bones) - 1)]
            side = unit(n.cross(Vector((0, 1, 0))))
            ahead = unit(side.cross(n))
            s = 0.55 if 1.3 < u < 3.7 else 0.45
            c = at + n * 0.1
            plate(m, "Chrome" if (j + round(u * 10 / 6)) % 3 else "ChromeDark", [c - side * s - ahead * s, c + side * s - ahead * s, c + side * s + ahead * s, c - side * s + ahead * s], 0.12)
    for side in (-1, 1):
        for k, u in enumerate((1.2, 1.9, 2.6, 3.3, 4.0)):  # gilt spikes down the flanks
            at, n = skin_at(rings, u, 0.18 if side > 0 else math.pi - 0.18)
            m.bone = bones[min(round(u), len(bones) - 1)]
            h = 1.5 + 0.4 * (k in (1, 2))
            horn(m, "Gilt", tuple(at - n * 0.3), tuple(at + n * h + Vector((0, -h * 0.5, 0.2))), 0.7)
        at, n = skin_at(rings, 3.7, 0.7 if side > 0 else math.pi - 0.7)
        m.bone = "Swing"
        horn(m, "Claw", tuple(at - n * 0.4), tuple(at + n * 2.4 + Vector((0, -0.8, 0.8))), 1.0)
    for letter, side in (("L", -1), ("R", 1)):
        leg(m, f"Front{letter}", "Swing", [(side * 3.6, 2.8, 4.6), (side * 4.3, 3.2, 2.5), (side * 4.3, 3.6, 0.6)], (3.0, 2.5, 2.5), toes=0, pad=1.5)
        leg(m, f"Back{letter}", "Spine", [(side * 3.8, -4.4, 4.8), (side * 4.5, -4.0, 2.6), (side * 4.5, -4.3, 0.6)], (3.4, 2.7, 2.6), toes=0, pad=1.6)
        for y in (3.6 + 1.6, -4.3 + 1.6):
            m.bone = f"Front{letter}" if y > 0 else f"Back{letter}"
            for k in range(3):  # porcelain toenails
                egg(m, "Claw", (side * 4.3 + (k - 1) * 0.6, y, 0.4), 0.3, 0.36, 0.32, 8, 4)
    tail = curve([(0, -7.6, 5.0), (0, -10.6, 4.6), (0, -13.8, 4.0), (0, -17.2, 3.5)], 9)
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w * 0.8) for p, w in zip(tail, (2.8, 2.5, 2.2, 1.9, 1.65, 1.45, 1.3, 1.15, 1.05))], sides=10)
    for i in (2, 4, 6, 8):  # gilt spikes in pairs down the tail
        p = Vector(tail[i])
        m.bone = ["Tail1", "Tail1", "Tail1", "Tail2", "Tail2", "Tail2", "Tail3", "Tail3", "Tail3"][i]
        w = 2.8 - 0.22 * i
        for side in (-1, 1):
            horn(m, "Gilt", tuple(p + Vector((side * w * 0.3, 0, 0.1))), tuple(p + Vector((side * (w * 0.5 + 0.9), -0.6, 0.4))), 0.5)
    # The mirror ball on Club, turning for ever round the tail; symmetric round that axis, so it turns without wobbling.
    c = Vector(CLUB_AT)
    m.use("Club", tuple(c), "Tail3")
    sweep(m, "Accent", [(tuple(Vector(tail[-1]) + Vector((0, 0.3, 0))), 1.0, 1.0), (tuple(c), 1.1, 1.1)], sides=8)
    egg(m, "Chrome", tuple(c), 2.6, 2.6, 2.6, 12, 8)
    ring_round(m, "Gilt", tuple(c), 2.62, (0, 1, 0), 0.24, 24)
    for k in range(6):
        a = k * math.tau / 6
        d = Vector((math.cos(a), 0, math.sin(a)))
        horn(m, "Gilt", tuple(c + d * 2.3), tuple(c + d * 3.9), 0.7)
    horn(m, "Gilt", tuple(c - Vector((0, 2.3, 0))), tuple(c - Vector((0, 3.8, 0))), 0.8)
    m.use("Head", (0, 6.2, 4.6), "Neck")
    skull = [(0, 0.95, 0.0, 1.0), (0.3, 1.0, 0.0, 1.0), (0.6, 0.86, 0.0, 0.78), (0.85, 0.66, 0.02, 0.5), (1.0, 0.5, 0.05, 0.3)]
    jaw = [(0, 0.9, -0.5, 0.0), (0.4, 0.86, -0.46, 0.0), (0.75, 0.66, -0.34, 0.0), (1.0, 0.46, -0.2, -0.02)]
    at = fierce_head(m, 5.0, 4.2, 4.6, 4.6, 2.6, skull, jaw, gape=-0.32, teeth=(13, 11), tall=0.42, base=0.2, fangs=((0.9, 0.9),), seed=64, t0=0.18)
    glare(m, at, [(0.42, 0.62, 0.32, (0.72, 0.68, 0.0))])
    for t in (0.3, 0.55):  # mirror tiles on the skull
        p = at(t, math.pi / 2) + Vector((0, 0, 0.1))
        plate(m, "Chrome", [p + Vector((-0.5, -0.45, 0)), p + Vector((0.5, -0.45, 0)), p + Vector((0.5, 0.45, 0)), p + Vector((-0.5, 0.45, 0))], 0.12)
    for side in (-1, 1):
        for k, (t, a, d, h) in enumerate(((0.08, 0.5, (1.2, -1.6, 0.6), 2.1), (0.12, 1.0, (0.6, -1.5, 1.2), 1.6))):  # porcelain horns at the back of the skull
            spot = at(t, a if side > 0 else math.pi - a)
            horn(m, "Claw", tuple(spot), tuple(spot + Vector((side * d[0], d[1], d[2])) * (h / 2)), 0.8 - 0.15 * k)
    m.head_centre = (0, 8.0, 4.6)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Swanquish


def swan_neck(m, letter, side, role, wing_role, chrome):
    """One neck, its head and its bill. side -1 is the white one, +1 its black reflection."""
    pts = [Vector((side * x, y, z)) for x, y, z in ((0.9, 3.8, 8.4), (1.5, 5.0, 10.8), (1.9, 4.1, 13.2), (1.7, 4.7, 15.4), (1.5, 6.0, 16.2))]
    path = curve([tuple(p) for p in pts], 13)
    widths = [1.65 - 0.07 * i for i in range(13)]
    jointed(m, role, [f"Neck{letter}1", f"Neck{letter}2", f"Neck{letter}3"], [(p, w, w) for p, w in zip(path, widths)], parent="Reflect", sides=10)
    end = Vector(path[-1])
    m.use(f"Head{letter}", tuple(end), f"Neck{letter}3")
    head = mark(m)
    # A swan's head, fierce: a long wedge of a skull, black skin from the bill back round the eye (the eye glares out of it), a long
    # gilt bill with a black knob, a hooked nail on its tip and a few glass teeth along its edge.
    h = end + Vector((0, 0.35, 0.1))
    sweep_fine(m, role, [(tuple(h + Vector((0, -0.45, -0.1))), 0.95, 1.0), (tuple(h + Vector((0, 0.3, 0.05))), 1.25, 1.15), (tuple(h + Vector((0, 1.0, -0.05))), 0.95, 0.85)],
               sides=10, per=3)
    for s in (-1, 1):  # the black lores
        sweep_fine(m, "Socket", [(tuple(h + Vector((s * 0.42, 0.25, 0.16))), 0.12, 0.5), (tuple(h + Vector((s * 0.4, 0.75, 0.0))), 0.12, 0.62),
                                 (tuple(h + Vector((s * 0.3, 1.2, -0.12))), 0.12, 0.5)], sides=4, per=2, up=(1, 0, 0))
    sweep_fine(m, "Gilt", [(tuple(h + Vector((0, 1.1, -0.05))), 0.8, 0.62), (tuple(h + Vector((0, 2.0, -0.18))), 0.62, 0.42), (tuple(h + Vector((0, 2.9, -0.36))), 0.36, 0.24)],
               sides=8, per=2)
    egg(m, "Socket", tuple(h + Vector((0, 1.2, 0.32))), 0.36, 0.4, 0.34, 8, 4)  # the knob on the bill
    point(m, "Socket", tuple(h + Vector((0, 2.75, -0.26))), tuple(h + Vector((0, 3.2, -0.62))), 0.24)  # the nail, hooked down
    for k in range(3):  # glass teeth along the edge of the bill
        for s in (-1, 1):
            base = h + Vector((s * (0.27 - 0.04 * k), 1.55 + 0.42 * k, -0.24 - 0.06 * k))
            sabre(m, "Teeth", [tuple(base), tuple(base + Vector((0, 0.06, -0.2))), tuple(base + Vector((0, 0.14, -0.4)))], 0.14, 4)
    m.use(f"Bill{letter}", tuple(h + Vector((0, 1.0, -0.28))), f"Head{letter}")
    sweep_fine(m, "Gilt", [(tuple(h + Vector((0, 1.1, -0.36))), 0.66, 0.26), (tuple(h + Vector((0, 2.0, -0.5))), 0.48, 0.2), (tuple(h + Vector((0, 2.7, -0.58))), 0.24, 0.12)],
               sides=8, per=2)
    rare_kit.swing(m, [f"Bill{letter}"], tuple(h + Vector((0, 1.0, -0.28))), -0.14)
    m.bone = f"Head{letter}"
    tox_eye(m, tuple(h + Vector((side * 0.5, 0.45, 0.2))), 0.21, (side * 0.7, 0.68, 0.06), side, socket=1.6, lid="Socket", ridge="Chrome", ridge_size=1.3, top=0.48, low=0.3)
    grown(m, head, end, 1.3)


def swan_wing(m, letter, side, role, chrome):
    """A wing held up and arched like a sail: coverts on WingL/R, the long chrome flight feathers on WingTipL/R."""
    shoulder, elbow, tip = Vector((side * 2.4, 1.2, 8.4)), Vector((side * 4.0, -1.6, 12.2)), Vector((side * 3.3, -6.6, 12.0))
    m.use(f"Wing{letter}", tuple(shoulder), "Spine")
    limb(m, role, [shoulder, shoulder.lerp(elbow, 0.5) + Vector((side * 0.3, 0, 0.3)), elbow], (1.6, 1.3, 1.0), sides=8)
    trail = unit(Vector((-side * 0.3, -0.3, -0.9)))
    for k in range(6):  # coverts down from the arm to the body, each a little further out so none lie in the same plane
        t = k / 5
        base = shoulder.lerp(elbow, 0.1 + 0.85 * t) + Vector((side * 0.07 * k, 0, 0))
        leaf(m, role, tuple(base), tuple(base + trail * (2.0 + 2.0 * t) + Vector((0, -0.6, 0))), (0, 1, 0), 1.9, thick=0.16)
    m.use(f"WingTip{letter}", tuple(elbow), f"Wing{letter}")
    limb(m, role, [elbow, elbow.lerp(tip, 0.5) + Vector((0, 0, 0.3)), tip], (1.0, 0.8, 0.5), sides=8)
    for k in range(6):  # secondaries
        base = elbow.lerp(tip, 0.05 + 0.17 * k) + Vector((side * 0.06 * k, 0, 0))
        leaf(m, role, tuple(base), tuple(base + trail * (4.0 - 0.3 * k) + Vector((0, -1.0, 0))), (0, 1, 0), 1.6, thick=0.14)
    for k in range(5):  # primaries, long and chrome, swept back and up like a sail's end
        base = tip + Vector((side * 0.08 * k, 0.7 * k, -0.25 * k))
        leaf(m, chrome, tuple(base), tuple(base + Vector((side * (0.3 - 0.1 * k), -3.8 + 0.25 * k, 0.4 - 0.55 * k))), (0, 0, 1), 1.05, thick=0.12)


def swanquish():
    """A swan and its reflection: white on its left, black on its right, a gilt line down the middle where they meet, two necks."""
    m = monster("dino_Swanquish", Body="#f7f3fa", Accent="#16132a", Belly="#bdb5d3", Claw="#2a2540")
    m.joint("Spine", (0, -0.6, 6.6))
    m.joint("Reflect", (0, 2.8, 7.6), "Spine")
    rings = [(0, 4.4, 8.0, 2.6, 2.4), (0, 3.0, 7.2, 4.8, 4.0), (0, 0.6, 6.6, 6.0, 4.3), (0, -2.6, 6.6, 5.8, 3.9), (0, -5.2, 7.3, 3.8, 2.6), (0, -6.8, 8.1, 1.0, 0.9)]
    bones = ["Reflect", "Reflect", "Spine", "Spine", "Spine", "Spine"]
    shell(m, "Accent", rings, -80, 80, 8, bones)
    shell(m, "Body", rings, 100, 260, 8, bones)
    shell(m, "Belly", rings, 260, 280, 2, bones)
    shell(m, "Gilt", [(x, y, z + 0.06, w, h) for x, y, z, w, h in rings], 82, 98, 2, bones)  # the mirror line
    m.bone = "Spine"
    tail = Vector((0, -5.6, 8.0))
    m.use("Tail1", tuple(tail), "Spine")
    for k in range(5):  # a short upturned tail, each feather a layer above the one before so none lie in the same place
        a = (k - 2) * 0.35
        base = tail + Vector((math.sin(a) * 0.3, 0.4, 0.14 * k))
        leaf(m, "Body" if k < 2 else "Accent" if k > 2 else "Gilt", tuple(base), tuple(base + Vector((math.sin(a) * 1.4, -2.2, 0.9))), (1, 0, 0), 0.8, thick=0.1)
    for letter, side, role, chrome in (("L", -1, "Body", "Chrome"), ("R", 1, "Accent", "ChromeDark")):
        swan_neck(m, letter, side, role, role, chrome)
        swan_wing(m, letter, side, role, chrome)
        hip, knee, ankle = Vector((side * 1.6, -0.4, 5.4)), Vector((side * 1.8, 0.4, 3.0)), Vector((side * 1.8, -0.2, 0.5))
        m.use(f"Leg{letter}", tuple(hip), "Spine")
        limb(m, "Claw", [hip, knee], (1.3, 0.8), sides=8)
        m.use(f"Shin{letter}", tuple(knee), f"Leg{letter}")
        limb(m, "Claw", [knee, ankle], (0.7, 0.55), sides=8)
        foot = ankle + Vector((0, 0.1, -0.1))
        for k in range(3):  # a webbed foot: three toes and the web between
            a = (k - 1) * 0.5
            toe = foot + Vector((math.sin(a) * 1.5 + side * 0.0, math.cos(a) * 1.5, -0.2))
            sweep(m, "Claw", [(tuple(foot), 0.4, 0.3), (tuple(toe), 0.2, 0.18)], sides=6)
            point(m, "Gilt", tuple(toe), tuple(toe + unit(toe - foot) * 0.5 - Vector((0, 0, 0.1))), 0.16)
        leaf(m, "Claw", tuple(foot), tuple(foot + Vector((0, 1.5, -0.25))), (1, 0, 0), 2.0, thick=0.1)
    m.use("Jaw", (0, 4.2, 7.9), "Reflect")  # the game reads which way it faces from its Jaw; nothing of it shows
    egg(m, "Belly", (0, 3.8, 7.6), 0.3, 0.3, 0.3, 6, 4)
    m.bone = "Spine"
    m.head_centre = (0, 7.0, 16.3)
    grounded(m)
    return m


# ---------------------------------------------------------------------- Mane Event

MANE_AT = (0, 4.3, 10.3)  # the middle of the mane, round the back of the skull so it frames the face
MANE_AXIS = (0, 0.72, 0.69)  # the neck's line, which the mane rings
MANE_ANGLES = [-0.8 + k * (math.pi + 1.6) / 11 for k in range(12)]  # round the neck from the right, over the top, to the left; none under the chin
MANE_BACK = (0, -0.4, 1)  # the shards down its back stand this way
MANE_SUNK = 0.5  # of each shard's length sunk in the skin at rest; the wave and the burst together never slide out more than that
MANE_WAVE, MANE_BURST = 0.25, 0.22  # shares of a shard's length: how far the wave and the burst slide it out


def mane_way(a):
    """The way a mane shard at angle a (0 to the right, pi / 2 on top) points: out from the neck and swept back along it."""
    axis = unit(MANE_AXIS)
    up = unit(Vector((1, 0, 0)).cross(axis))
    return unit(Vector((1, 0, 0)) * math.cos(a) + up * math.sin(a) - axis * 0.42)


def mane_slivers():
    """Every moving shard, in the order the burst lets go of them: (where: mane, back or tail; way; length; the spot it comes out of the
    skin, or how far along the body; the wave's phase)."""
    out = []
    centre, axis = Vector(MANE_AT), unit(MANE_AXIS)
    up = unit(Vector((1, 0, 0)).cross(axis))
    for a in MANE_ANGLES:
        radial = Vector((1, 0, 0)) * math.cos(a) + up * math.sin(a)
        out.append(("mane", mane_way(a), 5.0 + 1.0 * math.sin(a), centre + radial * 3.4, a))
    for k in range(6):
        out.append(("back", unit(MANE_BACK), 3.6 - 0.25 * k, 3.4 - 0.55 * k, 4.4 + 0.5 * k))
    for s in (-1, 1):
        out.append(("tail", unit(Vector((s * 0.4, -0.8, 0.45))), 2.4, None, 7.8 + 0.4 * (s > 0)))
    return out


def mane_event():
    """A lion of smoked violet glass with a pale muzzle and a mane of mirror shards, shards down its back and on its tail's tip."""
    m = monster("dino_ManeEvent", Body="#3a3266", Accent="#17142e", Belly="#cbc2e4", Claw="#eef6ff")
    m.joint("Spine", (0, -5.0, 7.4))
    m.joint("Rampant", (0, 1.2, 8.2), "Spine")
    m.joint("Neck", (0, 3.0, 9.2), "Rampant")
    rings = [((0, -9.0, 7.2), 3.0, 3.0), ((0, -7.6, 7.8), 6.4, 6.2), ((0, -4.4, 7.6), 5.8, 5.6), ((0, -1.0, 8.1), 6.6, 6.6), ((0, 2.0, 8.8), 7.4, 7.4),
             ((0, 4.4, 9.8), 5.0, 5.0)]
    bones = ["Spine", "Spine", "Spine", "Rampant", "Rampant", "Neck"]
    sweep_fine(m, "Body", rings, bones, sides=18, under="Belly", under_faces=5, per=4)
    for letter, side in (("L", -1), ("R", 1)):
        leg(m, f"Front{letter}", "Rampant", [(side * 2.8, 2.4, 8.0), (side * 3.2, 3.1, 4.6), (side * 3.0, 2.5, 1.8), (side * 3.0, 3.4, 0.7)], (3.4, 2.4, 1.9, 2.0),
            toes=0, pad=1.6)
        claws(m, (side * 3.0, 4.6, 0.75), (0, 1, -0.1), 4, 0.55, 1.5, 0.42, droop=0.4)
        leg(m, f"Back{letter}", "Spine", [(side * 2.8, -7.4, 7.6), (side * 3.3, -5.8, 4.8), (side * 3.0, -8.6, 2.2), (side * 3.0, -7.4, 0.7)], (3.8, 2.6, 1.8, 1.9),
            toes=0, pad=1.6)
        claws(m, (side * 3.0, -6.2, 0.75), (0, 1, -0.1), 4, 0.55, 1.3, 0.4, droop=0.4)
    tail = curve([(0, -8.8, 7.4), (0, -11.8, 6.6), (0, -14.8, 5.2), (0, -17.4, 5.6)], 9)
    jointed(m, "Body", ["Tail1", "Tail2", "Tail3"], [(p, w, w) for p, w in zip(tail, (1.4, 1.2, 1.05, 0.95, 0.85, 0.8, 0.75, 0.7, 0.7))], sides=8)
    m.bone = "Tail3"
    tuft = Vector(tail[-1]) + Vector((0, -0.6, 0.1))
    egg(m, "Accent", tuple(tuft), 1.1, 1.2, 1.1, 12, 6)
    for d in ((0, -1, 0.15), (0, -0.7, -0.6), (0, -0.6, 0.8)):  # fixed shards in the tuft, round the two that move
        shard(m, "ChromeDark", tuple(tuft), tuple(tuft + unit(d) * 2.1), 0.5)

    # The mane: a dark ruff round the neck; behind, two rings of shards that stay put, dark chrome and gilt, the back one flowing onto the
    # shoulders, with a beard under the chin; in front of them the twelve that move, bright chrome.
    centre, axis = Vector(MANE_AT), unit(MANE_AXIS)
    up = unit(Vector((1, 0, 0)).cross(axis))
    m.bone = "Neck"
    sweep_fine(m, "Accent", [(tuple(centre - axis * 1.9), 5.2, 5.2), (tuple(centre - axis * 0.7), 7.0, 7.0), (tuple(centre + axis * 0.5), 6.8, 6.8),
                             (tuple(centre + axis * 1.3), 4.8, 4.8)], sides=18, per=3, up=(0, 0, 1))
    for ring, (count, back, reach, sweep_back, size, out) in enumerate(((16, 0.2, 3.0, 0.65, 0.95, 4.2), (14, 1.5, 2.7, 1.25, 0.9, 3.8))):
        for k in range(count):
            a = -math.pi / 2 + (k + 0.5 * ring) * math.tau / count
            radial = Vector((1, 0, 0)) * math.cos(a) + up * math.sin(a)
            way = unit(radial - axis * sweep_back + Vector((0, 0, 0.4 * ring)))  # the back ring tips up a little, off the shoulders
            base = centre - axis * back + radial * reach
            length = out + 0.8 * max(math.sin(a), 0) - (1.2 if math.sin(a) < -0.6 else 0)  # longest on top, short under the chin
            m.bone = "Neck" if ring == 0 else "Rampant"
            shard(m, "Gilt" if (k + ring) % 3 == 0 else "ChromeDark", tuple(base), tuple(base + way * length), size, belly=0.25)
    for n, (where, way, length, sits, _) in enumerate(mane_slivers(), 1):
        if where == "mane":
            bone, root = "Neck", sits - way * (MANE_SUNK * length)
        elif where == "tail":
            bone, root = "Tail3", tuft - way * (MANE_SUNK * length - 1.0)
        else:
            at, _n = skin_at(rings, sits, math.pi / 2)
            bone, root = bones[min(round(sits), len(bones) - 1)], at - way * (MANE_SUNK * length)
        m.use(f"Sliver{n}", tuple(root), bone)
        shard(m, "Chrome", tuple(root), tuple(root + way * length), (0.3 if where == "mane" else 0.36) * length, belly=0.55)
    m.use("Head", (0, 5.0, 10.0), "Neck")
    skull = [(0, 0.95, 0.0, 1.15), (0.25, 1.0, 0.0, 1.25), (0.5, 0.9, 0.0, 1.0), (0.72, 0.7, 0.0, 0.72), (0.9, 0.58, 0.02, 0.5), (1.0, 0.46, 0.05, 0.34)]
    jaw = [(0, 0.9, -0.55, 0.0), (0.35, 0.86, -0.5, 0.0), (0.7, 0.66, -0.4, 0.0), (0.92, 0.5, -0.3, 0.0), (1.0, 0.4, -0.22, -0.02)]
    at = fierce_head(m, 4.7, 9.6, 4.8, 4.6, 3.2, skull, jaw, gape=-0.42, teeth=(10, 9), tall=0.6, base=0.26, fangs=((0.85, 1.7),), low_fangs=((0.8, 1.2),),
                     seed=66, t0=0.2)
    glare(m, at, [(0.5, 1.05, 0.46, (0.32, 0.94, -0.04))])
    mask(m, at, 0.12, 0.84, 2.4)
    for side in (-1, 1):
        egg(m, "Belly", tuple(at(0.84, math.pi / 2 - side * 0.62) + Vector((0, -0.1, -0.25))), 0.62, 0.7, 0.4, 10, 5)  # the pale muzzle
    egg(m, "Accent", tuple(at(0.98, math.pi / 2) + Vector((0, 0.05, -0.02))), 0.66, 0.36, 0.32, 8, 4)  # the nose
    m.head_centre = (0, 7.8, 10.0)
    grounded(m)
    return m


ALL = [paw_de_deux, frill_seeker, dressed_to_kill, wrecking_ballroom, swanquish, mane_event]


# ---------------------------------------------------------------------- what moves
#
# Each has an attack nothing else in the game has, 4 seconds, played once every DinoLife.attackCycle; a marker bone picks the table,
# as rare_kit's MARKED. "@always" in a table: moves played all the time, on top of everything, attack or not. These are the same as
# the map-16 block in DinoLifeController, number for number. Nothing leaves the body: the shards slide but never come out.

ALWAYS = "@always"


def shaken(points, speed, reach, slot=PITCH, phase=0.0):
    """A wave that only runs while its envelope (keys over the 4 seconds) is up."""
    def move(s):
        out = [0.0] * 6
        out[slot] = reach * keys((s / 4) % 1, points) * math.sin(speed * W * s - phase)
        return tuple(out)
    return move


def along(way, amount):
    """Slides along a way in the model's own axes (x across, y ahead, z up), amount(s) studs."""
    x, y, z = way

    def move(s):
        v = amount(s)
        return 0.0, 0.0, 0.0, y * v, z * v, x * v
    return move


def stepped(move, fps=8):
    """The move in jerks, fps poses a second, like a broken doll."""
    return lambda s: move(math.floor(s * fps) / fps)


def spun(turns=1, slot=ROLL):
    """Turns for ever: turns whole turns every 4 seconds."""
    def move(s):
        out = [0.0] * 6
        out[slot] = turns * W * s
        return tuple(out)
    return move


def mirrored(move):
    """The same move seen in a mirror across the middle: roll, yaw and sideways slide the other way."""
    def move_(s):
        p, r, y, a, u, x = move(s)
        return p, -r, -y, a, u, -x
    return move_


def right_of(name):
    i = name.rindex("L")
    return name[:i] + "R" + name[i + 1:]


# Paw de Deux (Prowl, its chest): it sidesteps a whole circle round a spot in front of it, always facing it, crouches, wriggles, springs
# and rakes with one paw and then the other.
PROWL_R = 6.0  # the circle's radius, studs at the first map's size
PROWL_TURN = [(0, 0), (0.12, 0), (0.62, 2 * math.pi), (1, 2 * math.pi)]
PROWL_LOW = [(0, 0), (0.1, -0.7), (0.62, -0.7), (0.68, -1.1), (0.72, -1.1), (0.76, 0.3), (0.84, 0), (1, 0)]
PROWL_LUNGE = [(0, 0), (0.7, 0), (0.75, 4.5), (0.86, 4.5), (1, 0)]
PROWL_LEAN = [(0, 0), (0.1, -0.06), (0.62, -0.06), (0.7, 0.12), (0.75, -0.1), (0.86, -0.1), (1, 0)]
PROWL_PACING = [(0, 0), (0.12, 0), (0.16, 1), (0.58, 1), (0.62, 0), (1, 0)]
PROWL_WIGGLE = [(0, 0), (0.63, 0), (0.65, 1), (0.71, 1), (0.73, 0), (1, 0)]
PROWL_SWIPE = [(0, 0), (0.7, 0), (0.74, 1.3), (0.77, -0.35), (0.84, -0.35), (0.94, 0), (1, 0)]
PROWL_NECK = [(0, 0), (0.1, -0.18), (0.62, -0.18), (0.7, -0.3), (0.75, 0.08), (0.86, 0.08), (1, 0)]
PROWL_HEAD = [(0, 0), (0.1, 0.1), (0.62, 0.1), (0.75, 0.22), (0.86, 0.22), (1, 0)]
PROWL_JAW = [(0, 0), (0.1, -0.15), (0.62, -0.15), (0.7, -0.55), (0.76, -0.55), (0.78, 0.1), (0.8, -0.5), (0.86, -0.5), (1, 0)]
PROWL_LASH = [(0, 0), (0.08, 1), (0.9, 1), (1, 0)]


def prowl_circle(s):
    """Round a circle PROWL_R in front of it, turning as it goes, so it faces the circle's middle all the way round."""
    a = keys((s / 4) % 1, PROWL_TURN)
    return 0.0, 0.0, a, PROWL_R * (1 - math.cos(a)), 0.0, PROWL_R * math.sin(a)


PROWLER = {
    "Spine": stacked(prowl_circle, beat(PROWL_LOW, 4, RISE), beat(PROWL_LUNGE, 4, AHEAD), beat(PROWL_LEAN, 4), shaken(PROWL_WIGGLE, 12, 0.1, YAW)),
    "Prowl": shaken(PROWL_PACING, 8, 0.05, ROLL),
    "Neck": beat(PROWL_NECK, 4),
    "Head": beat(PROWL_HEAD, 4),
    "Jaw": beat(PROWL_JAW, 4),
    "FrontL": stacked(shaken(PROWL_PACING, 8, 0.38), beat(PROWL_SWIPE, 4)),
    "FrontR": stacked(shaken(PROWL_PACING, 8, 0.38, PITCH, math.pi), beat(PROWL_SWIPE, 4, PITCH, 1.0, 0.08)),
    "BackL": shaken(PROWL_PACING, 8, 0.3, PITCH, math.pi),
    "BackR": shaken(PROWL_PACING, 8, 0.3),
}
for i in range(1, 4):
    PROWLER[f"Tail{i}"] = shaken(PROWL_LASH, 6, 0.18 + 0.06 * i, YAW, 0.7 * i)

# Frill Seeker (Frill, its frill's hub): it rears onto its hind legs, its kaleidoscope whirls a whole turn on top of its own turning, and it
# runs at you on two legs, hissing, then backs off and drops. Rosette, the petals, turns for ever.
FRILL_REAR = [(0, 0), (0.12, 1), (0.84, 1), (0.95, 0), (1, 0)]
FRILL_DASH = [(0, 0), (0.24, 0), (0.48, 1), (0.6, 1), (0.84, 0), (1, 0)]
FRILL_RUN = [(0, 0), (0.18, 0), (0.24, 1), (0.82, 1), (0.88, 0), (1, 0)]
FRILL_SPIN = [(0, 0), (0.1, 0), (0.6, 2 * math.pi), (1, 2 * math.pi)]
FRILL_HISS = [(0, 0), (0.1, -0.62), (0.84, -0.62), (0.95, 0), (1, 0)]
FRILL_SHIVER = [(0, 0), (0.08, 0), (0.12, 1), (0.84, 1), (0.9, 0), (1, 0)]
DASHER = {
    "Spine": stacked(beat(FRILL_REAR, 4, PITCH, 0.62), beat(FRILL_REAR, 4, RISE, 1.0), beat(FRILL_DASH, 4, AHEAD, 7.0), shaken(FRILL_RUN, 12, 0.05, ROLL)),
    "BackL": stacked(beat(FRILL_REAR, 4, PITCH, -0.62), shaken(FRILL_RUN, 12, 0.7)),
    "BackR": stacked(beat(FRILL_REAR, 4, PITCH, -0.62), shaken(FRILL_RUN, 12, 0.7, PITCH, math.pi)),
    "FrontL": stacked(beat(FRILL_REAR, 4, PITCH, 0.5), shaken(FRILL_RUN, 12, 0.3, PITCH, math.pi)),
    "FrontR": stacked(beat(FRILL_REAR, 4, PITCH, 0.5), shaken(FRILL_RUN, 12, 0.3)),
    "Neck": beat(FRILL_REAR, 4, PITCH, -0.45),
    "Head": beat(FRILL_REAR, 4, PITCH, -0.1),
    "Jaw": stacked(beat(FRILL_HISS, 4), shaken(FRILL_SHIVER, 20, 0.05)),
    "Frill": stacked(beat(FRILL_SPIN, 4, ROLL), shaken(FRILL_SHIVER, 24, 0.035)),
    "Tail1": beat(FRILL_REAR, 4, PITCH, -0.5),
    "Tail2": beat(FRILL_REAR, 4, PITCH, 0.2),
    "Tail3": shaken(FRILL_RUN, 6, 0.25, YAW),
    ALWAYS: {"Rosette": spun(1)},
}

# Dressed to Kill (Twist, its chest): its head turns slowly right round to look behind it, tilts, then snaps the rest of the way round, and
# it lunges: arms thrown out, its mirror of a face split open. The lunge comes in jerks, eight poses a second.
TWIST_TURN = [(0, 0), (0.08, 0), (0.4, math.pi), (0.55, math.pi), (0.585, 2 * math.pi), (1, 2 * math.pi)]
TWIST_TILT = [(0, 0), (0.32, 0), (0.42, 0.42), (0.54, 0.42), (0.58, 0), (1, 0)]
TWIST_LUNGE = [(0, 0), (0.58, 0), (0.64, 1), (0.76, 1), (0.9, 0), (1, 0)]
TWIST_REACH = [(0, 0), (0.56, 0), (0.6, -0.25), (0.64, 1), (0.76, 1), (0.9, 0), (1, 0)]
TWIST_JAW = [(0, 0), (0.08, 0), (0.4, -0.12), (0.55, -0.12), (0.6, -0.75), (0.76, -0.75), (0.9, 0), (1, 0)]
TWIST_JITTER = [(0, 0), (0.58, 0), (0.6, 1), (0.76, 1), (0.8, 0), (1, 0)]
TWISTER = {
    "Spine": stepped(stacked(beat(TWIST_LUNGE, 4, AHEAD, 3.6), beat(TWIST_LUNGE, 4, RISE, -0.5))),
    "Twist": stepped(stacked(beat(TWIST_LUNGE, 4, PITCH, -0.38), shaken(TWIST_JITTER, 14, 0.05, ROLL))),
    "Neck": stepped(beat(TWIST_LUNGE, 4, PITCH, -0.12)),
    "Head": stacked(beat(TWIST_TURN, 4, YAW), beat(TWIST_TILT, 4, ROLL), stepped(beat(TWIST_LUNGE, 4, PITCH, 0.3))),
    "Jaw": stepped(stacked(beat(TWIST_JAW, 4), shaken(TWIST_JITTER, 20, 0.08))),
    "ArmL": stepped(beat(TWIST_REACH, 4, PITCH, 1.45)),
    "ArmR": stepped(beat(TWIST_REACH, 4, PITCH, 1.45, 0.02)),
    "ForeL": stepped(beat(TWIST_REACH, 4, PITCH, 0.5)),
    "ForeR": stepped(beat(TWIST_REACH, 4, PITCH, 0.5, 0.02)),
    "LegL": stepped(beat(TWIST_LUNGE, 4, PITCH, 0.45)),
    "ShinL": stepped(beat(TWIST_LUNGE, 4, PITCH, -0.5)),
    "LegR": stepped(beat(TWIST_LUNGE, 4, PITCH, -0.3)),
}

# Wrecking Ballroom (Swing, its chest): the tail swings like a pendulum, higher each time, the body leaning against it; then it heaves
# the mirror ball up over its back and slams it down, hopping on its front feet, roaring. Club, the ball, turns for ever and faster in it.
PEND = [(0, 0), (0.06, 0.25), (0.56, 1), (0.6, 0), (1, 0)]
PEND_LIFT = [(0, 0), (0.56, 0), (0.66, 1), (0.71, 1), (0.75, -0.12), (0.84, -0.12), (1, 0)]
PEND_HOP = [(0, 0), (0.72, 0), (0.755, 1), (0.8, 0), (1, 0)]
PEND_DIP = [(0, 0), (0.56, 0), (0.66, -1), (0.71, -1), (0.75, 1), (0.84, 0.6), (1, 0)]
PEND_JAW = [(0, 0), (0.6, 0), (0.7, -0.55), (0.88, -0.55), (1, 0)]
PEND_SPIN = [(0, 0), (0.06, 0), (0.75, 4 * math.pi), (1, 4 * math.pi)]
SWINGER = {
    "Spine": stacked(shaken(PEND, 4, -0.08, YAW), beat(PEND_DIP, 4, PITCH, 0.1), beat(PEND_HOP, 4, RISE, 0.9)),
    "Swing": shaken(PEND, 4, -0.06, YAW, 0.4),
    "Neck": stacked(beat(PEND_DIP, 4, PITCH, 0.12), shaken(PEND, 4, -0.1, YAW, 0.6)),
    "Head": beat(PEND_DIP, 4, PITCH, 0.1),
    "Jaw": beat(PEND_JAW, 4),
    "FrontL": beat(PEND_HOP, 4, PITCH, 0.35),
    "FrontR": beat(PEND_HOP, 4, PITCH, 0.35),
    "Tail1": stacked(shaken(PEND, 4, 0.5, YAW), beat(PEND_LIFT, 4, PITCH, -0.8)),
    "Tail2": stacked(shaken(PEND, 4, 0.32, YAW, 0.6), beat(PEND_LIFT, 4, PITCH, -0.5)),
    "Tail3": stacked(shaken(PEND, 4, 0.26, YAW, 1.2), beat(PEND_LIFT, 4, PITCH, -0.35)),
    "Club": beat(PEND_SPIN, 4, ROLL),
    ALWAYS: {"Club": spun(1)},
}

# Swanquish (Reflect, its breast): the wings flare up and forward, both necks coil back hissing and weave, mirror images of each other,
# then strike together, closing like shears, twice. The right neck always does what the left does, seen in a mirror.
SWAN_FLARE = [(0, 0), (0.12, 1), (0.84, 1), (1, 0)]
SWAN_COIL = [(0, 0), (0.12, 0), (0.3, 1), (0.44, 1), (0.48, -0.7), (0.56, -0.7), (0.6, 0.5), (0.64, -0.7), (0.72, -0.7), (0.86, 0), (1, 0)]
SWAN_PINCH = [(0, 0), (0.44, 0), (0.48, 1), (0.56, 1), (0.6, 0.2), (0.64, 1), (0.72, 1), (0.86, 0), (1, 0)]
SWAN_BILL = [(0, 0), (0.14, -0.45), (0.44, -0.45), (0.47, 0.05), (0.52, -0.4), (0.6, -0.4), (0.63, 0.05), (0.68, -0.4), (0.86, 0), (1, 0)]
SWAN_BEATS = [(0, 0), (0.42, 0), (0.46, 1), (0.74, 1), (0.8, 0), (1, 0)]
SWAN_WEAVE = [(0, 0), (0.14, 0), (0.2, 1), (0.42, 1), (0.46, 0), (1, 0)]
SWAN_LUNGE = [(0, 0), (0.44, 0), (0.48, 1), (0.72, 1), (0.86, 0), (1, 0)]
SWAN_LEFT = {
    "NeckL1": stacked(beat(SWAN_COIL, 4, PITCH, 0.45), beat(SWAN_PINCH, 4, YAW, -0.16), shaken(SWAN_WEAVE, 6, 0.22, YAW)),
    "NeckL2": stacked(beat(SWAN_COIL, 4, PITCH, -0.55), shaken(SWAN_WEAVE, 6, -0.18, YAW, 0.8)),
    "NeckL3": stacked(beat(SWAN_COIL, 4, PITCH, 0.5), shaken(SWAN_WEAVE, 6, 0.15, YAW, 1.6)),
    "HeadL": beat(SWAN_COIL, 4, PITCH, -0.35),
    "BillL": beat(SWAN_BILL, 4),
    "WingL": stacked(beat(SWAN_FLARE, 4, ROLL, -0.35), beat(SWAN_FLARE, 4, YAW, -0.3), shaken(SWAN_BEATS, 8, 0.2, ROLL)),
    "WingTipL": stacked(beat(SWAN_FLARE, 4, ROLL, -0.25), shaken(SWAN_BEATS, 8, 0.22, ROLL, 0.8)),
}
SWAN_IDLE = {  # always: the necks sway, the right the mirror of the left
    "NeckL1": wave(1, 0.1, YAW),
    "NeckL2": wave(2, 0.06, PITCH, 0.6),
    "NeckL3": wave(1, -0.09, YAW, 1.2),
    "HeadL": stacked(wave(1, 0.08, ROLL, 0.4), wave(2, 0.05, PITCH, 1.4)),
}
MIRRORER = {
    "Spine": stacked(beat(SWAN_LUNGE, 4, AHEAD, 1.6), beat(SWAN_LUNGE, 4, PITCH, -0.06)),
    "Reflect": beat(SWAN_COIL, 4, PITCH, 0.08),
    "Tail1": beat(SWAN_FLARE, 4, PITCH, -0.3),
    ALWAYS: {},
}
for name, move in SWAN_LEFT.items():
    MIRRORER[name], MIRRORER[right_of(name)] = move, mirrored(move)
for name, move in SWAN_IDLE.items():
    MIRRORER[ALWAYS][name], MIRRORER[ALWAYS][right_of(name)] = move, mirrored(move)

# Mane Event (Rampant, its chest): it rears up rampant, pawing the air, and every shard bursts out at once and rattles; it roars, slams
# down onto its front paws and the shards ripple back in, mane first. Always: a wave runs round the mane and down its back, each shard
# sliding out of the skin and back in (Sliver1 to 20, MANE_WAVE), the owner's stadium wave.
RAMP_UP = [(0, 0), (0.15, 1), (0.48, 1), (0.58, -0.25), (0.7, -0.25), (0.86, 0), (1, 0)]
RAMP_SLAM = [(0, 0), (0.48, 0), (0.58, 2.6), (0.72, 2.6), (0.9, 0), (1, 0)]
RAMP_PAW = [(0, 0), (0.1, 0), (0.16, 1), (0.46, 1), (0.5, 0), (1, 0)]
RAMP_JAW = [(0, 0), (0.12, -0.2), (0.2, -0.78), (0.5, -0.78), (0.58, 0.05), (0.66, -0.35), (0.82, 0), (1, 0)]
RAMP_ROAR = [(0, 0), (0.18, 0), (0.22, 1), (0.48, 1), (0.52, 0), (1, 0)]
RAMP_RATTLE = [(0, 0), (0.17, 0), (0.2, 1), (0.56, 1), (0.6, 0), (1, 0)]


def burst_keys(order):
    """All out together; back in one after another, order 0 first."""
    late = 0.012 * order
    return [(0, 0), (0.12, 0), (0.19, 1), (0.6 + late, 1), (0.7 + late, 0), (1, 0)]


def sliver(way, length, phase, order):
    """A mane shard's two moves: the wave, always, and the burst, in the attack."""
    def wave_(s):
        return MANE_WAVE * length * ((1 + math.cos(2 * W * s - phase)) / 2) ** 4

    points = burst_keys(order)

    def burst(s):
        u = (s / 4) % 1
        return MANE_BURST * length * keys(u, points) + 0.05 * length * keys(u, RAMP_RATTLE) * math.sin(24 * W * s)
    return along(way, wave_), along(way, burst)


RAMPANT = {
    "Spine": stacked(beat(RAMP_UP, 4, PITCH, 0.62), beat(RAMP_UP, 4, RISE, 1.6), beat(RAMP_SLAM, 4, AHEAD)),
    "Rampant": stacked(beat(RAMP_UP, 4, PITCH, 0.12), shaken(RAMP_ROAR, 20, 0.03, ROLL)),
    "BackL": beat(RAMP_UP, 4, PITCH, -0.62),
    "BackR": beat(RAMP_UP, 4, PITCH, -0.62),
    "FrontL": stacked(beat(RAMP_UP, 4, PITCH, 0.55), shaken(RAMP_PAW, 6, 0.55)),
    "FrontR": stacked(beat(RAMP_UP, 4, PITCH, 0.55), shaken(RAMP_PAW, 6, 0.55, PITCH, math.pi)),
    "Neck": beat(RAMP_UP, 4, PITCH, -0.15),
    "Head": stacked(beat(RAMP_ROAR, 4, PITCH, 0.3), shaken(RAMP_ROAR, 20, 0.04, YAW)),
    "Jaw": stacked(beat(RAMP_JAW, 4), shaken(RAMP_ROAR, 24, 0.05)),
    "Tail1": beat(RAMP_UP, 4, PITCH, -0.45),
    "Tail2": shaken(RAMP_PAW, 4, 0.3, YAW),
    "Tail3": shaken(RAMP_PAW, 4, 0.4, YAW, 1.0),
    ALWAYS: {},
}
for n, (_, way, length, _, phase) in enumerate(mane_slivers(), 1):
    RAMPANT[ALWAYS][f"Sliver{n}"], RAMPANT[f"Sliver{n}"] = sliver(tuple(way), length, phase, n - 1)

# A monster with one of these bones has the rest of its body moved by that bone's table: the same lines as in DinoLifeController.
MIRROR_MOVES = {"Prowl": PROWLER, "Frill": DASHER, "Twist": TWISTER, "Swing": SWINGER, "Reflect": MIRRORER, "Rampant": RAMPANT}
rare_kit.MARKED.update(MIRROR_MOVES)


# ---------------------------------------------------------------------- the preview's animation

LEGS = ("FrontL", "FrontR", "BackL", "BackR", "LegL", "LegR", "ShinL", "ShinR")


def always(a, f, idle):
    """The "@always" moves, on top of whatever this frame has posed (DinoLifeController adds them last)."""
    s = f / 30
    moves = marked_of(a)
    posed = rare_kit.POSED_IDLE if idle else rare_kit.POSED_WALK
    for name, move in moves.get(ALWAYS, {}).items():
        bone = a.pose.bones.get(name)
        if not bone:
            continue
        p, r, y, ahead, rise, across = move(s)
        has = name in moves or name in posed
        rot = list(bone.rotation_euler) if has else [0.0, 0.0, 0.0]
        loc = list(bone.location) if has else [0.0, 0.0, 0.0]
        kit.pose_bone(a, name, (rot[0] + p, rot[1] + r, rot[2] + y), (loc[0] + across, loc[1] + ahead, loc[2] + rise), f)


def walk_pose(a, f):
    volcano_walk(a, f)
    sway(a, f, False)
    always(a, f, False)


def idle_pose(a, f):
    volcano_idle(a, f)
    moved = set(marked_of(a))
    for name in LEGS:  # no idle of their own: what's added goes on the rest pose, not on the last frame
        if name not in moved:
            kit.pose_bone(a, name, (0, 0, 0), None, f)
    sway(a, f, True)
    always(a, f, True)


def animate(armature):
    walk = kit.add_action(armature, "Walk", WALK_PREVIEW, walk_pose, 2)
    idle = kit.add_action(armature, "Idle", kit.IDLE_FRAMES, idle_pose, 2)
    return walk, idle


def light_and_shine(roots, glow_roles, strength=2.4):
    """The glow, and the chrome and gilt as metal (the world's shine), off again when the glow is (before the .blend is saved)."""
    monster_stage_light(roots, glow_roles, strength)
    world.shine(roots, strength > 0)


monster_stage_light = monster_stage.light_up


def pose_stills(builders, out, seconds):
    """POSE="0.8 1.6 2.9" QUICK_OUT=<folder>: each monster in its idle at those seconds, attack and all, from the side and three
    quarters on, for checking the attacks without the videos."""
    import bpy
    scene = kit.setup_scene()
    kit.RENDERS = out
    out.mkdir(parents=True, exist_ok=True)
    animals = bpy.data.collections.new("Animals")
    scene.collection.children.link(animals)
    models = [make() for make in builders]
    roots = []
    for i, model in enumerate(models):
        root = model.build(animals)
        root.location = (i * 80, 0, 0)
        roots.append(root)
    light_and_shine(roots, GLOW_ROLES, 1.6)
    mesh = bpy.data.meshes.new("Ground")
    mesh.from_pydata([(-300, -300, -0.01), (600, -300, -0.01), (600, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    mesh.materials.append(kit.material("Ground", FLOOR, False))
    scene.collection.objects.link(bpy.data.objects.new("Ground", mesh))
    monster_stage.set_sky(scene, SKY)
    frames = [round(s * 30) for s in seconds]
    for root in roots:
        root.animation_data_create()
        root.animation_data.action = bpy.data.actions.new(f"{root.name}_Poses")
        for f in frames:
            idle_pose(root, f)
    for model, root in zip(models, roots):
        kit.set_visible(roots, [root])
        scene.frame_set(0)
        low, high = kit.bounds(root)
        centre = (low + high) / 2 + Vector((0, 3, 1))
        reach = max((high - low).length, 3)
        for s, f in zip(seconds, frames):
            scene.frame_set(f)
            kit.shoot(scene, f"{model.name}_pose_{s}", centre + Vector((1.15, 0.5, 0.35)) * reach * 1.15, centre, (520, 520), 50)


def main():
    monster_stage.light_up = light_and_shine
    rare_kit.light_up = light_and_shine
    if os.environ.get("POSE"):
        only = os.environ.get("ONLY")
        pose_stills([b for b in ALL if not only or b.__name__ in only.split(",")], Path(os.environ["QUICK_OUT"]), [float(s) for s in os.environ["POSE"].split()])
        return
    rare_kit.animate = animate  # run() films with it
    rare_kit.run(ALL, RENDERS, BLEND, "shattered_mirror", SKY, FLOOR, GLOW_ROLES, glow=1.6, spacing=40)


if __name__ == "__main__":
    main()
