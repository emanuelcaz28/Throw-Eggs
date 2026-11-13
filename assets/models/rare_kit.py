"""Shared by every map's 7th and 8th monsters (owner, 2026-11-06: 8 monsters a map like the reference, so 2 more on each,
made in Blender and animated, nicer than the ones before, more aggressive map by map; 6 at a time, a prompt each).

The new pair are each map's two rarest, its new top prizes. Each map has its own script, build_<map>_monsters_7_8.py,
which saves its own .blend (export_fbx.py sends it to that map's Animals folder). This file holds what they share:

  - sweep(): a tube along a curved path, ring by ring, each ring on its own bone. Necks, tails, bodies and a snake bend
    smoothly when their bones turn, with no gaps opening between pieces.
  - Faces: real eyeballs. round_eye (a white ball, a curved iris, pupil and shines, skin lids that set the mood) and
    slit_eye (a dark ball, a burning iris and a thin upright slit under a hard lid). cap() lays a patch on any ball or
    egg: an iris, a blush, a mask, a spot.
  - Shapes: scallop (a ring of overlapping feathers or scales), leaf (one feather), sabre (a curved claw, tooth or horn),
    swing (hangs a jaw open at rest).
  - What moves, on top of every monster's walk, idle and roar (build_volcano.py), the same as SWAY in
    DinoLifeController, number for number:
      Sway<n>a, b, c     slow waves down a chain of up to three bones: feathers, crests, sails, moss. n (1 to 8) moves
                         each chain's wave along, so a row of them ripples
      Wriggle<n>a, b, c  the same, three times as fast and a little wider: a worm lure
      PinchL, PinchR     a pincer's moving finger: eases open, snaps shut, every 2 seconds, the right half a beat after
                         the left; wide open in the roar
      Flick              a forked tongue: darts out twice and back every 2 seconds
      Sting              a scorpion's stinger: draws back, then stabs, every 4 seconds
      Slither<n>         a snake's body, one bone after the next: a wave runs down it, gently at rest, wide as it moves
      Strike             sits under the Neck: every 4 seconds the neck rears back and lunges, and the Jaw flings open and
                         bites shut. The Swamp's pair, so the motion gets fiercer map by map as the looks do
      Spit1 to 6         the Volcano's pair: fire parked in the head, thrown out one after the other as the Strike lunges, the
                         jaw held wide, side jaws snapping and wings beating. Each sinks into the ground and snaps back
      Step<n>            a centipede's legs, one set after the next: a ripple down its sides, wide as it moves
      Kick1 to 4         the Frozen Peaks' charge: snow flung off the hooves. With these it paws the ground and throws its whole body
                         forward, head down, every 4 seconds
      Shard1 to 6        the Frozen Peaks' smash: ice flung off the ground. With these it heaves both arms overhead and smashes them down
      Stab, BuzzL, BuzzR Shadow Bog's mosquito: a needle that stabs twice every 4 seconds as the body dips, wings that blur
      Curl1 to 4, Thumb  Shadow Bog's hand: drums its fingers one after the other, then rears up and grabs
      Punch, Club L and R, Shock1 and 2, Bubble1 to 4
                         The Abyss's shrimp: arms that snap out one after the other, a ring of shock flying off each
      SeizeL1 to 5, SeizeR1 to 5
                         The Abyss's Kraken: long arms that unroll straight, strike and drag back. Its jaw snaps on what they bring
      Spout1 to 6        Starfall's whale: a fountain of stars. Orbit (DinoLifeController SPIN): its moon, going round it
      Fall1 to 6         Starfall's lion: lifts its head and sings, and meteors fall round it
      Arm, Scythe L and R, Crescent1 and 2
                         Eclipse Temple's mantis: scythes flung open, crescents flying out, spinning, and back to its hands
      Ring1 to 4         Eclipse Temple's bat: climbs, screams rings of sound, folds its wings and drops
      Maul               maps 10 to 12: between the Spine and the Neck. Bare monsters, no effects: every 2 seconds, twice as often as
                         anything before, it throws its whole front forward, bites three times and shakes what it caught
      Whirl, Gore, Gulp, Bounce, Pummel, Reach1
                         maps 13 to 15: bare too, the most aggressive of all, each with its own attack (see the tables): spins on its waist, rams and
                         hooks upward, leaps jaws first, ricochets, hammers both fists, stretches its neck. Quill<n>, Hock L and R, Fore L and R, Reach2 to 12 go with them
    A monster with one of these marker bones (Strike, Spit1, Kick1, Shard1, Stab, Curl1, Shock1, SeizeL1, Spout1, Fall1, Crescent1, Ring1, Maul, Whirl, Gore, Gulp, Bounce, Pummel, Reach1) also has the rest of its body taken
    over by that bone's table in MARKED. A bone's a marker only if the monster's built for it.
    Everything moves at whole multiples of a quarter turn a second, so it repeats every 4 seconds; the preview's walk is
    4 strides and its idle 8 seconds, so both loop.

Models face +Y, feet on Z = 0, 1 Blender unit = 1 stud at the first map's size. Plain colours (no stud image): the studs
come only from Studio's shared "Studs" material.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_desert import beam  # noqa: E402
from build_forest import Model  # noqa: E402
from build_spore_hollow_monsters import egg  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from build_volcano import idle_pose as volcano_idle, walk_pose as volcano_walk  # noqa: E402
from monster_stage import build_and_render, light_up, set_sky  # noqa: E402

kit.PREVIEW_STUDS = False
kit.NO_STUDS.update({"EyeColour", "Socket", "Lash", "Blush", "Slit"})  # the face stays clean, as the older faces' roles do

W = math.pi / 2  # a quarter turn a second: everything moves at whole multiples of it
WALK_PREVIEW = 4 * kit.WALK_FRAMES  # four strides, so the 4-second sway loops in the preview


# ---------------------------------------------------------------------- what moves (SWAY in DinoLifeController)


def smooth(u):
    return u * u * (3 - 2 * u)


def pinch_open(u):
    """0 to 1 over a cycle (u from 0 to 1): eases open, holds, snaps shut, rests."""
    u %= 1
    if u < 0.55:
        return smooth(u / 0.55)
    if u < 0.62:
        return 1.0
    if u < 0.68:
        return 1 - smooth((u - 0.62) / 0.06)
    return 0.0


def bump(u, start, length):
    """A quick rise to 1 and back between start and start + length, 0 elsewhere."""
    u = (u - start) % 1
    return math.sin(math.pi * u / length) if u < length else 0.0


def keys(u, points):
    """A smooth run through points, (u, value) pairs from u = 0 to 1."""
    for (u0, v0), (u1, v1) in zip(points, points[1:]):
        if u <= u1:
            return v0 + (v1 - v0) * smooth((u - u0) / (u1 - u0))
    return points[-1][1]


STING = [(0, 0), (0.3, 0.4), (0.35, -0.8), (0.44, -0.8), (0.7, 0), (1, 0)]
STRIKE = [(0, 0), (0.3, 1), (0.345, -1), (0.42, -1), (0.7, 0), (1, 0)]  # 1 reared back, -1 lunged
STRIKE_JAW = [(0, 0), (0.3, -0.3), (0.38, -0.3), (0.43, 0.42), (0.6, 0.42), (0.75, 0), (1, 0)]

METEOR = (0.22, 0.5, -1)  # which way Constellion's meteors fall; their tails point back up it

# Bits thrown out for a moment: when (seconds into the 4), how long, from and to (across, ahead, up from where they're
# parked, studs at the first map's size) and how high the arc. They jump to `from`, fly to `to`, and snap back out of sight.
FLING = {f"Spit{n}": (1.38 + 0.07 * (n - 1), 0.62, (0, 2, -1.4), (0, 19, -16), 1) for n in range(1, 7)}
FLING.update({
    "Kick1": (1.2, 0.7, (-3.1, -5, -7.6), (-5.5, -13, -9), 3.2),
    "Kick2": (1.2, 0.7, (3.1, -5, -7.6), (5.5, -13, -9), 3.2),
    "Kick3": (1.28, 0.6, (-3, 4.6, -7.6), (-6.5, -3, -9), 2.4),
    "Kick4": (1.28, 0.6, (3, 4.6, -7.6), (6.5, -3, -9), 2.4),
    "Shard1": (1.34, 0.75, (-8.3, 8.4, -9.5), (-13.5, 15, -11.5), 6),
    "Shard2": (1.34, 0.65, (-8.3, 8.4, -9.5), (-16, 7, -11.5), 4.5),
    "Shard3": (1.38, 0.7, (-8.3, 8.4, -9.5), (-5, 17, -11.5), 5),
    "Shard4": (1.34, 0.75, (8.3, 8.4, -9.5), (13.5, 15, -11.5), 6),
    "Shard5": (1.34, 0.65, (8.3, 8.4, -9.5), (16, 7, -11.5), 4.5),
    "Shard6": (1.38, 0.7, (8.3, 8.4, -9.5), (5, 17, -11.5), 5),
    "Shock1": (1.26, 0.5, (-3.2, 14, -3.7), (-3.2, 44, -3.7), 0),
    "Shock2": (2.26, 0.5, (3.2, 14, -3.7), (3.2, 44, -3.7), 0),
    "Bubble1": (1.26, 0.9, (-3.2, 13, -3.7), (-5, 21, 2), 1.5),
    "Bubble2": (1.32, 0.8, (-3.2, 13, -3.7), (-1.5, 19, 4), 1),
    "Bubble3": (2.26, 0.9, (3.2, 13, -3.7), (5, 21, 2), 1.5),
    "Bubble4": (2.32, 0.8, (3.2, 13, -3.7), (1.5, 19, 4), 1),
    "Crescent1": (1.3, 1.3, (-3, 17, 6.2), (-3, 17, 6.2), (-9, 26, -2), 25),
    "Crescent2": (1.4, 1.3, (3, 17, 6.2), (3, 17, 6.2), (9, 26, -2), -25),
})
FLING.update({f"Spout{n}": (0.6 + 0.18 * (n - 1), 1.4, (0, 0.4, 2.6), (x, y, -12), 12, 3) for n, (x, y) in enumerate(((-7, 3), (6, 8), (-3, -6), (9, -2), (-10, -3), (3, 5)), start=1)})


def meteor(n, x, y):
    """A meteor landing at x, y from its parked spot: it comes down the METEOR line from high above."""
    d = Vector(METEOR).normalized() * 42
    return (0.9 + 0.28 * (n - 1), 0.55, (x - d.x, y - d.y, -11 - d.z), (x, y, -11), 0)


FLING.update({f"Fall{n}": meteor(n, x, y) for n, (x, y) in enumerate(((-12, 16), (10, 20), (-4, 26), (14, 8), (-16, 6), (3, 14)), start=1)})
FLING.update({f"Ring{n}": (0.72 + 0.08 * (4 - n), 0.46, (0, 5.6, 3.4), (0, 46, -2), 0) for n in range(1, 5)})  # on the Swim bone: parked on Root they'd be left in mid air when it dives


def fling_of(spec, s):
    """Where a thrown bit is, s seconds in: pitch, roll, yaw, ahead, up and across."""
    start, seconds, source, target, arc = spec[:5]
    spin = spec[5] if len(spec) > 5 else 0
    t = ((s - start) % 4) / seconds
    if t >= 1:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    lift = (0, 0, arc) if isinstance(arc, (int, float)) else arc
    at = [a + (b - a) * t + 4 * t * (1 - t) * c for a, b, c in zip(source, target, lift)]
    return 0.0, 0.0, spin * t, at[1], at[2], at[0]


def track(points, pitch=1.0, delay=0.0):
    """A bone that pitches along points, over the 4 seconds, delay (a share of them) late."""
    return lambda s: (pitch * keys((s / 4 - delay) % 1, points), 0.0, 0.0, 0.0, 0.0, 0.0)


def plus_pitch(move, points, sign=1.0):
    """move, with points' pitch added: a leg turned against the body's lean, so its foot stays down."""
    return lambda s: (move(s)[0] + sign * keys((s / 4) % 1, points), *move(s)[1:])


# The fire: wide jaws, side jaws thrown open then shut, wings up as it rears and beating down on the lunge.
SPIT_JAW = [(0, 0), (0.3, -0.3), (0.345, -0.5), (0.55, -0.5), (0.75, 0), (1, 0)]
SPIT_MAND = [(0, 0), (0.3, 0.42), (0.345, 0.42), (0.4, -0.12), (0.55, -0.12), (0.75, 0), (1, 0)]
SPIT_WING = [(0, 0), (0.3, 0.36), (0.345, -0.12), (0.42, -0.12), (0.7, 0), (1, 0)]
SPIT_TIP = [(0, 0), (0.32, 0.26), (0.38, -0.2), (0.46, -0.2), (0.72, 0), (1, 0)]


def rolled(points, sign):
    return lambda s: (0.0, sign * keys((s / 4) % 1, points), 0.0, 0.0, 0.0, 0.0)


def yawed(points, sign):
    return lambda s: (0.0, 0.0, sign * keys((s / 4) % 1, points), 0.0, 0.0, 0.0)


SPITTER = {"Jaw": track(SPIT_JAW), "MandL": yawed(SPIT_MAND, 1), "MandR": yawed(SPIT_MAND, -1), "WingL": rolled(SPIT_WING, 1), "WingR": rolled(SPIT_WING, -1),
           "WingTipL": rolled(SPIT_TIP, 1), "WingTipR": rolled(SPIT_TIP, -1)}

# The charge: paw twice, sink back, throw the whole body forward head down, toss the head on impact, walk back.
CHARGE_AHEAD = [(0, 0), (0.2, 0), (0.29, -1.2), (0.345, 4.2), (0.42, 4.2), (0.78, 0), (1, 0)]
CHARGE_LEAN = [(0, 0), (0.2, 0), (0.29, -0.06), (0.345, -0.13), (0.385, 0.08), (0.46, 0.08), (0.72, 0), (1, 0)]
CHARGE_NECK = [(0, 0), (0.12, -0.12), (0.29, -0.42), (0.345, -0.42), (0.385, 0.2), (0.46, 0.2), (0.72, 0), (1, 0)]
CHARGE_HEAD = [(0, 0), (0.29, -0.2), (0.345, -0.2), (0.385, 0.24), (0.46, 0.24), (0.72, 0), (1, 0)]
CHARGE_JAW = [(0, 0), (0.29, 0.05), (0.345, -0.1), (0.385, -0.5), (0.5, -0.5), (0.72, 0), (1, 0)]
CHARGE_FRONT = [(0, 0), (0.29, -0.2), (0.345, 0.55), (0.42, 0.3), (0.7, 0), (1, 0)]
CHARGE_BACK = [(0, 0), (0.29, 0.25), (0.345, -0.55), (0.42, -0.2), (0.7, 0), (1, 0)]
CHARGE_TAIL = [(0, 0), (0.29, -0.2), (0.345, 0.4), (0.5, 0.2), (0.7, 0), (1, 0)]


def charge_spine(s):
    u = (s / 4) % 1
    return keys(u, CHARGE_LEAN), 0.0, 0.0, keys(u, CHARGE_AHEAD), 0.0, 0.0


def paw(s):
    u = (s / 4) % 1
    return 0.55 * (bump(u, 0.02, 0.09) + bump(u, 0.12, 0.09)), 0.0, 0.0, 0.0, 0.0, 0.0


CHARGER = {"Spine": charge_spine, "Neck": track(CHARGE_NECK), "Head": track(CHARGE_HEAD), "Jaw": track(CHARGE_JAW), "Tail1": track(CHARGE_TAIL),
           "FrontL": plus_pitch(track(CHARGE_FRONT), CHARGE_LEAN, -1), "FrontR": plus_pitch(plus_pitch(paw, CHARGE_FRONT), CHARGE_LEAN, -1),
           "BackL": plus_pitch(track(CHARGE_BACK), CHARGE_LEAN, -1), "BackR": plus_pitch(track(CHARGE_BACK), CHARGE_LEAN, -1)}

# The smash: both arms up over the head, leaning back, then down with everything it has.
SLAM_ARM = [(0, 0), (0.19, 2.35), (0.285, 2.55), (0.335, 0.4), (0.44, 0.4), (0.72, 0), (1, 0)]
SLAM_LEAN = [(0, 0), (0.19, 0.2), (0.285, 0.24), (0.335, -0.36), (0.44, -0.36), (0.72, 0), (1, 0)]
SLAM_NECK = [(0, 0), (0.19, 0.18), (0.285, 0.22), (0.335, -0.05), (0.44, -0.05), (0.72, 0), (1, 0)]
SLAM_HEAD = [(0, 0), (0.19, 0.3), (0.285, 0.34), (0.335, 0.24), (0.44, 0.24), (0.72, 0), (1, 0)]
SLAM_JAW = [(0, 0), (0.19, -0.22), (0.285, -0.22), (0.335, 0.3), (0.44, 0.3), (0.72, 0), (1, 0)]

SLAMMER = {"Spine": track(SLAM_LEAN), "Neck": track(SLAM_NECK), "Head": track(SLAM_HEAD), "Jaw": track(SLAM_JAW), "ArmL": track(SLAM_ARM), "ArmR": track(SLAM_ARM),
           "LegL": track(SLAM_LEAN, -1), "LegR": track(SLAM_LEAN, -1)}

# The needle: rise, stab, draw back, stab again, the front legs reaching in to hold on.
STAB_NEEDLE = [(0, 0), (0.2, -1), (0.26, 3.4), (0.3, 3.4), (0.38, -0.4), (0.44, 3.4), (0.48, 3.4), (0.7, 0), (1, 0)]
STAB_HEAD = [(0, 0), (0.2, 0.12), (0.26, -0.22), (0.3, -0.22), (0.38, 0.06), (0.44, -0.22), (0.48, -0.22), (0.7, 0), (1, 0)]
STAB_LEAN = [(0, 0), (0.2, 0.06), (0.26, -0.12), (0.48, -0.12), (0.7, 0), (1, 0)]
STAB_RISE = [(0, 0), (0.2, 0.6), (0.26, -0.7), (0.48, -0.7), (0.7, 0), (1, 0)]
STAB_LEGS = [(0, 0), (0.2, 0.3), (0.26, -0.25), (0.48, -0.25), (0.7, 0), (1, 0)]


def stab_spine(s):
    u = (s / 4) % 1
    return keys(u, STAB_LEAN), 0.0, 0.0, 0.0, keys(u, STAB_RISE), 0.0


STABBER = {"Spine": stab_spine, "Head": track(STAB_HEAD), "FrontL": track(STAB_LEGS), "FrontR": track(STAB_LEGS)}

# The hand: taps out its fingers twice, one after the other, rears up, then grabs.
GRAB_LEAN = [(0, 0), (0.42, 0), (0.52, 0.42), (0.57, -0.4), (0.64, -0.4), (0.9, 0), (1, 0)]
GRAB_AHEAD = [(0, 0), (0.42, 0), (0.52, -1), (0.57, 3.6), (0.64, 3.6), (0.9, 0), (1, 0)]
GRAB_RISE = [(0, 0), (0.42, 0), (0.52, -1), (0.57, 0.4), (0.64, 0.4), (0.9, 0), (1, 0)]
GRAB_JAW = [(0, 0), (0.42, 0), (0.52, -0.5), (0.565, -0.5), (0.58, 0.14), (0.64, 0.14), (0.9, 0), (1, 0)]
GRAB_THUMB = [(0, 0), (0.42, 0), (0.52, -0.5), (0.57, 0.75), (0.64, 0.75), (0.9, 0), (1, 0)]
GRAB_CURL = [(0, 0), (0.42, 0), (0.52, 0.5), (0.57, -0.75), (0.64, -0.75), (0.9, 0), (1, 0)]


def grab_spine(s):
    u = (s / 4) % 1
    return keys(u, GRAB_LEAN), 0.0, 0.0, keys(u, GRAB_AHEAD), keys(u, GRAB_RISE), 0.0


def curl(n):
    def move(s):
        u = (s / 4) % 1
        tap = bump(u, 0.02 + 0.045 * n, 0.07) + bump(u, 0.22 + 0.045 * n, 0.07)
        return 0.5 * tap + keys(u, GRAB_CURL), 0.0, 0.0, 0.0, 0.0, 0.0
    return move


GRABBER = {"Spine": grab_spine, "Jaw": track(GRAB_JAW), "Thumb": yawed(GRAB_THUMB, 1), "Tail1": track(GRAB_LEAN, -1), "FrontL": track(GRAB_LEAN, -1), "FrontR": track(GRAB_LEAN, -1),
           "BackL": track(GRAB_LEAN, -1), "BackR": track(GRAB_LEAN, -1), "Curl1": curl(0), "Curl2": curl(1), "Curl3": curl(2), "Curl4": curl(3)}

# The punch: cocked, then out in an instant, one fist and a quarter of the way round the clock the other.
PUNCH_CLUB = [(0, 0), (0.27, -0.22), (0.3, -0.22), (0.315, 2.9), (0.36, 2.9), (0.5, 0), (1, 0)]
PUNCH_ARM = [(0, 0), (0.27, 0.15), (0.3, 0.15), (0.315, -0.2), (0.36, -0.2), (0.5, 0), (1, 0)]
PUNCH_JAW = [(0, 0), (0.27, -0.2), (0.6, -0.2), (0.75, 0), (1, 0)]
PUNCHER = {"ClubL": track(PUNCH_CLUB), "PunchL": track(PUNCH_ARM), "ClubR": track(PUNCH_CLUB, 1.0, 0.25), "PunchR": track(PUNCH_ARM, 1.0, 0.25), "Jaw": track(PUNCH_JAW)}

# The hunting arms: drawn back, unrolled straight in an instant, held, then dragged home, where the jaw snaps. 1 is straight.
SEIZE_REACH = [(0, 0), (0.25, -0.12), (0.32, -0.12), (0.365, 1), (0.43, 1), (0.62, 0.55), (0.72, 0), (1, 0)]
SEIZE_AHEAD = [(0, 0), (0.32, 0), (0.365, 6), (0.43, 6), (0.62, 2), (0.72, 0), (1, 0)]
SEIZE_TURN = (-1.527, 0.48, 0.611, 0.703, 0.735)  # how far each joint turns to lay the arm out straight
SEIZE_JAW = [(0, 0), (0.36, -0.1), (0.45, -0.35), (0.68, -0.35), (0.72, 0.1), (0.78, 0.1), (0.9, 0), (1, 0)]


def seize(k, delay):
    def move(s):
        u = (s / 4 - delay) % 1
        return SEIZE_TURN[k] * keys(u, SEIZE_REACH), 0.0, 0.0, keys(u, SEIZE_AHEAD) if k == 0 else 0.0, 0.0, 0.0
    return move


SEIZER = {"Jaw": track(SEIZE_JAW)}
for k in range(5):
    SEIZER[f"SeizeL{k + 1}"] = seize(k, 0.0)
    SEIZER[f"SeizeR{k + 1}"] = seize(k, 0.06)

# The whale breathes out: its head lifts a little and its mouth parts.
SPOUT_HEAD = [(0, 0), (0.12, 0.06), (0.5, 0.06), (0.7, 0), (1, 0)]
SPOUT_JAW = [(0, 0), (0.12, -0.06), (0.5, -0.06), (0.7, 0), (1, 0)]
SPOUTER = {"Head": track(SPOUT_HEAD), "Jaw": track(SPOUT_JAW)}

# The lion lifts its head and sings.
FALL_NECK = [(0, 0), (0.16, 0.24), (0.62, 0.24), (0.8, 0), (1, 0)]
FALL_HEAD = [(0, 0), (0.16, 0.14), (0.62, 0.14), (0.8, 0), (1, 0)]
FALL_JAW = [(0, 0), (0.2, -0.2), (0.6, -0.2), (0.75, 0), (1, 0)]
CALLER = {"Neck": track(FALL_NECK), "Head": track(FALL_HEAD), "Jaw": track(FALL_JAW)}

# The mantis: scythes up and open, flung down as the crescents fly, up again to catch them.
THROW_ARM = [(0, 0), (0.2, 0.7), (0.3, 0.8), (0.335, -0.1), (0.4, -0.1), (0.66, 0.5), (0.72, 0.3), (0.85, 0), (1, 0)]
THROW_SCYTHE = [(0, 0), (0.2, 1.7), (0.3, 2.0), (0.335, 0.5), (0.4, 0.4), (0.66, 1.4), (0.72, 1.0), (0.85, 0), (1, 0)]
THROW_NECK = [(0, 0), (0.2, 0.1), (0.3, 0.12), (0.335, -0.2), (0.4, -0.2), (0.8, 0), (1, 0)]
THROW_MAND = [(0, 0), (0.2, 0.4), (0.3, 0.4), (0.335, -0.1), (0.4, -0.1), (0.8, 0), (1, 0)]
THROW_JAW = [(0, 0), (0.2, -0.35), (0.34, -0.35), (0.42, 0), (1, 0)]
THROWER = {"ArmL": track(THROW_ARM), "ArmR": track(THROW_ARM), "ScytheL": track(THROW_SCYTHE), "ScytheR": track(THROW_SCYTHE), "Neck": track(THROW_NECK), "Jaw": track(THROW_JAW),
           "MandL": yawed(THROW_MAND, 1), "MandR": yawed(THROW_MAND, -1)}

# The bat: beats its wings, climbs, screams, folds them and drops on you, and climbs back.
DIVE_UP = [(0, 0), (0.16, 6), (0.3, 6.4), (0.36, 6.4), (0.44, -2.5), (0.5, -2.5), (0.8, 0), (1, 0)]
DIVE_AHEAD = [(0, 0), (0.3, -2), (0.36, -2), (0.44, 11), (0.5, 11), (0.8, 0), (1, 0)]
DIVE_LEAN = [(0, 0), (0.3, 0.2), (0.36, 0.25), (0.44, -0.5), (0.5, -0.5), (0.72, 0), (1, 0)]
DIVE_FOLD = [(0, 0), (0.36, 0), (0.4, 1), (0.5, 1), (0.6, 0), (1, 0)]
DIVE_HEAD = [(0, 0), (0.2, 0.1), (0.3, 0.15), (0.36, 0.15), (0.44, 0.3), (0.5, 0.3), (0.72, 0), (1, 0)]
DIVE_JAW = [(0, 0), (0.2, -0.35), (0.34, -0.35), (0.44, -0.1), (0.5, -0.2), (0.7, 0), (1, 0)]


def dive_swim(s):
    u = (s / 4) % 1
    return keys(u, DIVE_LEAN), 0.0, 0.0, keys(u, DIVE_AHEAD), keys(u, DIVE_UP), 0.0


def dive_wing(side, beat, lag, fold):
    def move(s):
        f = keys((s / 4) % 1, DIVE_FOLD)
        return 0.0, side * ((1 - f) * beat * math.sin(8 * W * s - lag) - fold * f), 0.0, 0.0, 0.0, 0.0
    return move


DIVER = {"Swim": dive_swim, "Head": track(DIVE_HEAD), "Jaw": track(DIVE_JAW), "WingL": dive_wing(1, 0.3, 0, 0.9), "WingR": dive_wing(-1, 0.3, 0, 0.9), "WingTipL": dive_wing(1, 0.22, 0.8, 1.0),
         "WingTipR": dive_wing(-1, 0.22, 0.8, 1.0)}

# Maps 10 to 12: nothing but the body. Every 2 seconds it sinks back, throws itself forward, bites three times, shakes what it
# caught and drags itself back to go again, its arms raking one after the other, trembling all the time.
MAUL_AHEAD = [(0, 0), (0.26, -1.2), (0.33, 3), (0.5, 3), (0.8, 0), (1, 0)]
MAUL_LEAN = [(0, 0), (0.26, 0.18), (0.33, -0.18), (0.5, -0.18), (0.8, 0), (1, 0)]
MAUL_SURGE = [(0, 0), (0.26, -0.5), (0.33, 1.6), (0.5, 1.6), (0.8, 0), (1, 0)]
MAUL_NECK = [(0, 0), (0.26, 0.2), (0.33, -0.3), (0.5, -0.2), (0.8, 0), (1, 0)]
MAUL_HEAD = [(0, 0), (0.26, 0.1), (0.33, 0.22), (0.5, 0.12), (0.8, 0), (1, 0)]
MAUL_JAW = [(0, 0), (0.26, -0.5), (0.32, -0.5), (0.345, 0.4), (0.39, -0.2), (0.42, 0.4), (0.46, -0.2), (0.49, 0.4), (0.8, 0), (1, 0)]
MAUL_ARM = [(0, 0), (0.22, 1.5), (0.33, -0.3), (0.5, -0.3), (0.8, 0), (1, 0)]
MAUL_FRONT = [(0, 0), (0.26, -0.2), (0.33, 0.45), (0.5, 0.3), (0.8, 0), (1, 0)]
MAUL_BACK = [(0, 0), (0.26, 0.2), (0.33, -0.4), (0.5, -0.2), (0.8, 0), (1, 0)]


def fast(points, pitch=1.0, delay=0.0):
    """A bone that pitches along points, over 2 seconds."""
    return lambda s: (pitch * keys((s / 2 - delay) % 1, points), 0.0, 0.0, 0.0, 0.0, 0.0)


def maul_body(s):
    u = (s / 2) % 1
    return 0.012 * math.sin(20 * W * s), 0.0, 0.0, keys(u, MAUL_SURGE), 0.0, 0.0


def maul_chest(s):
    u = (s / 2) % 1
    return keys(u, MAUL_LEAN), 0.0, 0.0, keys(u, MAUL_AHEAD), 0.0, 0.0


def maul_shake(points, reach, roll=False):
    """Pitches along points and shakes from side to side while it has hold."""
    def move(s):
        u = (s / 2) % 1
        shake = reach * math.sin(32 * W * s) * bump(u, 0.34, 0.2)
        return keys(u, points), shake if roll else 0.0, 0.0 if roll else shake, 0.0, 0.0, 0.0
    return move


def maul_tail(s):
    return 0.0, 0.0, 0.34 * math.sin(8 * W * s), 0.0, 0.0, 0.0


def maul_slither(n):
    return lambda s: (0.0, 0.0, 0.16 * math.sin(8 * W * s - 0.8 * n), 0.0, 0.0, 0.0)


MAULER = {"Spine": maul_body, "Maul": maul_chest, "Neck": maul_shake(MAUL_NECK, 0.3), "Head": maul_shake(MAUL_HEAD, 0.16, True), "Jaw": fast(MAUL_JAW), "ArmL": fast(MAUL_ARM), "ArmR": fast(MAUL_ARM, 1.0, 0.5),
          "FrontL": fast(MAUL_FRONT), "FrontR": fast(MAUL_FRONT), "BackL": fast(MAUL_BACK), "BackR": fast(MAUL_BACK), "Tail1": maul_tail}
for n in range(1, 9):
    MAULER[f"Slither{n}"] = maul_slither(n)

# Maps 13 to 15, the last and worst: each has its own attack, all of them at least twice as often as the Maul. They're written with four small
# pieces, so the two files can stay line for line: beat (a run of keys over some seconds), wave, hop (a bounce) and stacked (moves added up).
PITCH, ROLL, YAW, AHEAD, RISE, ACROSS = 0, 1, 2, 3, 4, 5


def beat(points, seconds=2, slot=PITCH, scale=1.0, delay=0.0):
    def move(s):
        out = [0.0] * 6
        out[slot] = scale * keys((s / seconds - delay) % 1, points)
        return tuple(out)
    return move


def wave(speed, reach, slot=PITCH, phase=0.0):
    def move(s):
        out = [0.0] * 6
        out[slot] = reach * math.sin(speed * W * s - phase)
        return tuple(out)
    return move


def hop(speed, reach, slot=RISE):
    def move(s):
        out = [0.0] * 6
        out[slot] = reach * abs(math.sin(speed * W * s))
        return tuple(out)
    return move


def stacked(*moves):
    return lambda s: tuple(sum(values) for values in zip(*(move(s) for move in moves)))


# Thornado (Whirl, its waist): winds up, spins twice on its own hips with its four arms flung out, then falls forward biting. Every 2 seconds.
WHIRL_TURN = [(0, 0), (0.16, -0.8), (0.24, -0.8), (0.6, 4 * math.pi), (1, 4 * math.pi)]
WHIRL_LEAN = [(0, 0), (0.24, 0.16), (0.62, 0.16), (0.68, -0.34), (0.8, -0.34), (1, 0)]
WHIRL_FLING = [(0, 0), (0.16, -0.3), (0.24, -0.3), (0.34, 1.35), (0.52, 1.35), (0.62, 0), (1, 0)]
WHIRL_RAKE = [(0, 0), (0.6, 0), (0.64, 1.2), (0.7, -0.3), (0.8, -0.3), (1, 0)]
WHIRL_NECK = [(0, 0), (0.24, 0.25), (0.62, 0.25), (0.68, -0.3), (0.8, -0.3), (1, 0)]
WHIRL_JAW = [(0, 0), (0.24, -0.4), (0.66, -0.4), (0.69, 0.45), (0.73, -0.2), (0.76, 0.45), (0.85, 0.1), (1, 0)]
WHIRLER = {"Spine": wave(20, 0.012), "Whirl": stacked(beat(WHIRL_TURN, 2, YAW), beat(WHIRL_LEAN)), "Neck": beat(WHIRL_NECK), "Jaw": beat(WHIRL_JAW),
           "ArmL": stacked(beat(WHIRL_FLING, 2, ROLL), beat(WHIRL_RAKE)), "ArmR": stacked(beat(WHIRL_FLING, 2, ROLL, -1.0), beat(WHIRL_RAKE, 2, PITCH, 1.0, 0.03)),
           "WingL": beat(WHIRL_FLING, 2, ROLL, 0.8, 0.02), "WingR": beat(WHIRL_FLING, 2, ROLL, -0.8, 0.02)}

# Thorn to Bits (Gore, its chest): head down, every thorn on its back standing up, it rams and hooks upward three times, left, right and through.
GORE_SURGE = [(0, 0), (0.2, -2), (0.3, 6), (0.72, 6), (0.92, 0), (1, 0)]
GORE_CHEST = [(0, 0), (0.2, 0.1), (0.3, -0.16), (0.36, -0.16), (0.42, 0.2), (0.5, -0.16), (0.58, 0.2), (0.66, -0.16), (0.72, 0.26), (0.92, 0), (1, 0)]
GORE_NECK = [(0, 0), (0.2, -0.3), (0.3, -0.55), (0.36, -0.55), (0.42, 0.55), (0.5, -0.55), (0.58, 0.55), (0.66, -0.55), (0.72, 0.65), (0.92, 0), (1, 0)]
GORE_HOOK = [(0, 0), (0.36, 0), (0.42, 0.4), (0.5, 0), (0.58, -0.4), (0.66, 0), (1, 0)]
GORE_JAW = [(0, 0), (0.2, -0.1), (0.3, 0.2), (0.36, -0.3), (0.42, 0.3), (0.5, -0.3), (0.58, 0.3), (0.66, -0.3), (0.72, 0.35), (0.92, 0), (1, 0)]
GORE_FRONT = [(0, 0), (0.2, -0.2), (0.3, 0.6), (0.72, 0.3), (0.92, 0), (1, 0)]
GORE_BACK = [(0, 0), (0.2, 0.25), (0.3, -0.6), (0.72, -0.3), (0.92, 0), (1, 0)]
GORE_QUILL = [(0, 0), (0.18, -0.9), (0.72, -0.9), (0.9, 0), (1, 0)]
GORER = {"Spine": beat(GORE_SURGE, 2, AHEAD), "Gore": beat(GORE_CHEST), "Neck": stacked(beat(GORE_NECK), beat(GORE_HOOK, 2, YAW)), "Jaw": beat(GORE_JAW), "FrontL": beat(GORE_FRONT), "FrontR": beat(GORE_FRONT),
         "BackL": beat(GORE_BACK), "BackR": beat(GORE_BACK), "Tail1": wave(8, 0.4, YAW)}
for n in range(1, 9):
    GORER[f"Quill{n}"] = stacked(beat(GORE_QUILL, 2, PITCH, 1.0, 0.012 * n), wave(20, 0.1, PITCH, 0.7 * n))

# Mouth Breather (Gulp, what little neck it has): all mouth on legs. Every second it leaps with its skull flung right back and comes down jaws first.
GULP_HEAD = [(0, 0), (0.32, 0.72), (0.4, 0.72), (0.47, -0.16), (0.6, -0.16), (1, 0)]
GULP_JAW = [(0, 0), (0.32, -0.7), (0.4, -0.7), (0.47, 0.55), (0.6, 0.55), (1, 0)]
GULP_THROAT = [(0, 0), (0.32, 0.2), (0.47, -0.12), (0.6, -0.12), (1, 0)]
GULP_RISE = [(0, 0), (0.3, 4), (0.47, 0), (1, 0)]
GULP_AHEAD = [(0, 0), (0.3, 2), (0.47, 5), (0.6, 5), (1, 0)]
GULP_TUCK = [(0, 0), (0.3, 0.5), (0.47, -0.2), (0.6, 0), (1, 0)]
GULPER = {"Spine": stacked(beat(GULP_RISE, 1, RISE), beat(GULP_AHEAD, 1, AHEAD)), "Gulp": beat(GULP_THROAT, 1), "Head": beat(GULP_HEAD, 1), "Jaw": beat(GULP_JAW, 1), "FrontL": beat(GULP_TUCK, 1), "FrontR": beat(GULP_TUCK, 1),
          "BackL": beat(GULP_TUCK, 1, PITCH, -1.0), "BackR": beat(GULP_TUCK, 1, PITCH, -1.0), "Tail1": wave(8, 0.3, YAW)}

# Spore Loser (Bounce, its chest): never touches the ground for long. Twice a second it springs, left, right, ahead and home, biting as it lands.
BOUNCE_ACROSS = [(0, 0), (0.25, -7), (0.5, 7), (0.75, 0), (1, 0)]
BOUNCE_AHEAD = [(0, 0), (0.25, 3), (0.5, 3), (0.75, 9), (1, 0)]
BOUNCE_TURN = [(0, 0), (0.25, 0.5), (0.5, -0.5), (0.75, 0), (1, 0)]
BOUNCE_HOCK = [(0, -0.5), (0.12, 0.8), (0.3, 0.8), (1, -0.5)]
BOUNCE_THIGH = [(0, 0.3), (0.12, -0.7), (0.3, -0.7), (1, 0.3)]
BOUNCE_CLAW = [(0, -0.3), (0.3, 0.9), (0.6, 0.9), (1, -0.3)]
BOUNCE_JAW = [(0, 0.35), (0.2, -0.5), (0.86, -0.5), (1, 0.35)]
BOUNCE_NECK = [(0, -0.2), (0.5, 0.3), (1, -0.2)]
BOUNCER = {"Spine": stacked(beat(BOUNCE_ACROSS, 2, ACROSS), beat(BOUNCE_AHEAD, 2, AHEAD), beat(BOUNCE_TURN, 2, YAW), hop(4, 6)), "Bounce": wave(8, 0.12, PITCH, 1.0), "Neck": beat(BOUNCE_NECK, 0.5), "Jaw": beat(BOUNCE_JAW, 0.5),
           "FrontL": beat(BOUNCE_CLAW, 0.5), "FrontR": beat(BOUNCE_CLAW, 0.5, PITCH, 1.0, 0.1), "BackL": beat(BOUNCE_THIGH, 0.5), "BackR": beat(BOUNCE_THIGH, 0.5), "HockL": beat(BOUNCE_HOCK, 0.5), "HockR": beat(BOUNCE_HOCK, 0.5)}

# Inconsolable (Pummel, its chest): never stops. Both fists hammer the ground in turn, four blows a second, its mouth wide in one long scream.
PUMMEL_ARM = [(0, 0), (0.45, 1.8), (0.58, 1.85), (0.72, -0.05), (0.85, -0.05), (1, 0)]
PUMMEL_FORE = [(0, 0), (0.45, 0.7), (0.58, 0.7), (0.72, 0), (1, 0)]
PUMMELER = {"Spine": hop(8, 0.9), "Pummel": stacked(wave(8, 0.16, ROLL), wave(16, 0.05)), "Neck": stacked(wave(16, 0.1), wave(8, 0.12, ROLL, 1.0)), "Head": wave(32, 0.06, YAW), "Jaw": stacked(wave(24, 0.1), beat([(0, -0.3), (1, -0.3)])),
            "ArmL": beat(PUMMEL_ARM, 0.5), "ArmR": beat(PUMMEL_ARM, 0.5, PITCH, 1.0, 0.5), "ForeL": beat(PUMMEL_FORE, 0.5), "ForeR": beat(PUMMEL_FORE, 0.5, PITCH, 1.0, 0.5), "LegL": wave(8, 0.08), "LegR": wave(8, -0.08)}

# Last Breath (Reach1 to 12, its neck): the end of it all. Every second its neck stretches far past what a neck can, left, ahead, right, ahead, and snaps shut.
REACH = [(0, 0), (0.3, -0.12), (0.42, 1), (0.62, 1), (1, 0)]
REACH_FAN = [(0, 0), (0.25, 0.6), (0.5, 0), (0.75, -0.6), (1, 0)]
REACH_JAW = [(0, 0), (0.3, -0.45), (0.42, -0.5), (0.47, 0.4), (0.62, 0.4), (1, 0)]
REACH_HEAD = [(0, 0), (0.3, 0.2), (0.42, -0.1), (0.62, -0.1), (1, 0)]
REACH_RAKE = [(0, 0), (0.3, 0.5), (0.42, -0.3), (0.62, -0.3), (1, 0)]
REACHER = {"Spine": wave(20, 0.012), "Reach1": stacked(beat(REACH, 1, AHEAD, 1.7), beat(REACH, 1, RISE, -0.35), beat(REACH_FAN, 4, YAW)), "Head": beat(REACH_HEAD, 1), "Jaw": beat(REACH_JAW, 1),
           "FrontL": beat(REACH_RAKE, 1), "FrontR": beat(REACH_RAKE, 1, PITCH, 1.0, 0.5)}
for n in range(2, 13):
    REACHER[f"Reach{n}"] = stacked(beat(REACH, 1, AHEAD, 1.7), beat(REACH, 1, RISE, -0.35))

# A monster with one of these bones has the rest of its body moved by that bone's table. The same as MARKED in DinoLifeController.
MARKED = {"Spit1": SPITTER, "Kick1": CHARGER, "Shard1": SLAMMER, "Stab": STABBER, "Curl1": GRABBER, "Shock1": PUNCHER, "SeizeL1": SEIZER, "Spout1": SPOUTER, "Fall1": CALLER,
          "Crescent1": THROWER, "Ring1": DIVER, "Maul": MAULER, "Whirl": WHIRLER, "Gore": GORER, "Gulp": GULPER, "Bounce": BOUNCER, "Pummel": PUMMELER, "Reach1": REACHER}


def sway_of(name, s, walking=0.0):
    """What a bone adds, s seconds in: pitch, roll, yaw and how far it slides ahead (studs at the first map's size), or
    None for a bone this doesn't move. walking: 0 at rest, 1 on the move. The same as SWAY in DinoLifeController."""
    sin = math.sin
    w = W * s
    u4 = (s / 4) % 1
    if name in FLING:
        return fling_of(FLING[name], s)
    if name == "Orbit":
        return 0.0, 0.0, s * math.pi / 4, 0.0  # the game's SPIN turns it
    if name.startswith("Step") and name[4:].isdigit():
        return (0.06 + 0.42 * walking) * sin(8 * w - 1.2 * int(name[4:])), 0.0, 0.0, 0.0
    if name == "BuzzL" or name == "BuzzR":
        side = 1 if name == "BuzzL" else -1
        return 0.0, side * (0.1 + 0.26 * sin(32 * w)), 0.0, 0.0
    if name == "Stab":
        return 0.0, 0.0, 0.0, keys(u4, STAB_NEEDLE)
    if name == "Sting":
        return keys(u4, STING), 0.0, 0.0, 0.0
    if name == "Strike":
        e = keys(u4, STRIKE)
        return 0.2 * e, 0.0, 0.0, -1.4 * e
    if name.startswith("Slither") and name[7:].isdigit():
        return 0.0, 0.0, (0.05 + 0.2 * walking) * sin(2 * w - 0.8 * int(name[7:])), 0.0
    for family, speed, reach0, step in (("Sway", 1, 0.1, 0.05), ("Wriggle", 3, 0.16, 0.08)):
        if name.startswith(family) and name[-1] in "abc" and name[len(family):-1].isdigit():
            n, k = int(name[len(family):-1]), "abc".index(name[-1])
            phase = 0.8 * n - 0.9 * k
            reach = reach0 + step * k
            v = speed * w
            return (reach * (sin(2 * v + phase) + 0.35 * sin(5 * v + 1.3 * phase)),
                    0.6 * reach * sin(3 * v + 2 * phase),
                    0.7 * reach * sin(2 * v + 0.7 * phase + 1), 0.0)
    if name in ("PinchL", "PinchR"):
        side, offset = (1, 0.0) if name == "PinchL" else (-1, math.pi)
        return 0.0, 0.0, side * 0.5 * pinch_open((2 * w + offset) / math.tau), 0.0
    if name == "Flick":
        u = (w / math.pi) % 1  # a 2-second cycle
        e = bump(u, 0.0, 0.12) + bump(u, 0.2, 0.12)
        return 0.22 * e * sin(12 * w), 0.0, 0.0, 0.55 * e
    return None


def roar_of(name, t):
    """What the roar adds to the idle for this batch's own bones (t: the idle loop, 0 to 2 pi): the pincers fling open.
    The same as ROAR.PinchL and PinchR in DinoLifeController."""
    r = ((1 - math.cos(t)) / 2) ** 10
    if name == "PinchL":
        return 0.0, 0.0, 0.55 * r
    if name == "PinchR":
        return 0.0, 0.0, -0.55 * r
    if name == "MandL":
        return 0.0, 0.0, 0.6 * r
    if name == "MandR":
        return 0.0, 0.0, -0.6 * r
    return None


# Which bones the walk and the idle pose first. A marker's move goes on top of these; any other bone takes it whole.
POSED_WALK = {"Swim", "Spine", "Neck", "Head", "Jaw", "ArmL", "ArmR", "LegL", "LegR", "ShinL", "ShinR", "FrontL", "FrontR", "BackL", "BackR", "Tail1", "Tail2", "Tail3",
              "WingL", "WingR", "WingTipL", "WingTipR"}
POSED_IDLE = {"Swim", "Spine", "Neck", "Head", "Jaw", "ArmL", "ArmR", "Tail1", "Tail2", "Tail3", "WingL", "WingR", "WingTipL", "WingTipR"}


def marked_of(a):
    """The table of bones a monster's marker bone takes over."""
    for marker, moves in MARKED.items():
        if marker in a.pose.bones:
            return moves
    return {"Jaw": track(STRIKE_JAW)} if "Strike" in a.pose.bones else {}


def sway(a, f, idle):
    """Adds the swaying to the pose just set. These bones have no other pose, so theirs is the whole pose; the bones a marker
    takes over may have one, so theirs goes on top."""
    s = f / 30
    t = 2 * math.pi * f / kit.IDLE_FRAMES
    posed = POSED_IDLE if idle else POSED_WALK
    if "Swim" in a.pose.bones:  # The Abyss's swim and hover don't pose wings, so a flyer's wings have nothing to add to
        posed = posed - {"WingL", "WingR", "WingTipL", "WingTipR"}
    moves = marked_of(a)
    for name, move in moves.items():
        bone = a.pose.bones.get(name)
        if not bone:
            continue
        pitch, roll, yaw, ahead, rise, across = move(s)
        r = roar_of(name, t) if idle else None
        if r:
            pitch, roll, yaw = pitch + r[0], roll + r[1], yaw + r[2]
        base = bone.rotation_euler if name in posed else (0, 0, 0)
        at = bone.location if name in ("Spine", "Swim") else (0, 0, 0)
        kit.pose_bone(a, name, (base[0] + pitch, base[1] + roll, base[2] + yaw), (at[0] + across, at[1] + ahead, at[2] + rise), f)
    for bone in a.pose.bones:
        if bone.name in moves:
            continue
        extra = sway_of(bone.name, s, 0.0 if idle else 1.0)
        if extra is None:
            if idle and roar_of(bone.name, t):  # side jaws have no sway, only the roar
                kit.pose_bone(a, bone.name, roar_of(bone.name, t), None, f)
            continue
        pitch, roll, yaw, ahead = extra[:4]
        rise, across = extra[4:] if len(extra) > 4 else (0.0, 0.0)
        if idle:
            r = roar_of(bone.name, t)
            if r:
                pitch, roll, yaw = pitch + r[0], roll + r[1], yaw + r[2]
        kit.pose_bone(a, bone.name, (pitch, roll, yaw), (across, ahead, rise), f)


def walk_pose(a, f):
    volcano_walk(a, f)
    sway(a, f, False)


def idle_pose(a, f):
    volcano_idle(a, f)
    t = 2 * math.pi * f / kit.IDLE_FRAMES
    for letter, side in (("L", -1), ("R", 1)):  # the wings' idle, which the Volcano's has no need of
        kit.pose_bone(a, f"Wing{letter}", (0, side * 0.07 * math.sin(4 * t), 0), None, f)
        kit.pose_bone(a, f"WingTip{letter}", (0, side * 0.06 * math.sin(4 * t - 0.8), 0), None, f)
    sway(a, f, True)


def swim_preview(a, f):
    from build_abyss_monsters import swim_pose
    swim_pose(a, f)
    sway(a, f, False)


def hover_preview(a, f):
    from build_abyss_monsters import hover_pose
    hover_pose(a, f)
    sway(a, f, True)


def animate(armature):
    """The Volcano's walk and idle (jaw snap and roar), or The Abyss's swim and hover, with this batch's swaying on top."""
    swims = "Swim" in armature.pose.bones
    walk = kit.add_action(armature, "Walk", WALK_PREVIEW, swim_preview if swims else walk_pose, 2)
    idle = kit.add_action(armature, "Idle", kit.IDLE_FRAMES, hover_preview if swims else idle_pose, 2)
    return walk, idle


# ---------------------------------------------------------------------- shapes


def frames_along(points, up=(0, 0, 1)):
    """A frame (ahead, side, normal) at each point of a path, turned as little as possible from one to the next. For a
    path running +Y, side is +X and normal +Z."""
    pts = [Vector(p) for p in points]
    ahead = []
    for i in range(len(pts)):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        ahead.append((b - a).normalized())
    side = ahead[0].cross(Vector(up))
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    frames = []
    for t in ahead:
        side = (side - t * side.dot(t))
        if side.length < 1e-4:
            side = Vector((1, 0, 0))
        side.normalize()
        frames.append((t, side, side.cross(t)))
    return frames


def sweep(m, role, path, bones=None, sides=8, caps=(True, True), up=(0, 0, 1), turn=None, under=None, under_faces=3):
    """A tube along path, a list of (point, width, height): width along the path's side, height along its normal. Each
    ring rides its own bone (bones, one per point; m.bone when None), so the tube bends where they turn instead of
    opening a gap. sides 4 makes a box section, 8 a chunky round one. under: another role for the faces along the
    tube's underside (-normal), under_faces of them: a belly, a throat, a snake's belly plates."""
    pts = [p for p, _, _ in path]
    frames = frames_along(pts, up)
    turn = math.pi / sides if turn is None else turn
    rings = []
    for i, ((p, w, h), (_, side, normal)) in enumerate(zip(path, frames)):
        rings.append([tuple(Vector(p) + side * math.cos(turn + j * math.tau / sides) * w / 2 + normal * math.sin(turn + j * math.tau / sides) * h / 2)
                      for j in range(sides)])
    step = math.tau / sides

    def is_under(j):
        mid = (turn + (j + 0.5) * step) % math.tau
        gap = abs((mid - 1.5 * math.pi + math.pi) % math.tau - math.pi)
        return under is not None and gap < under_faces * step / 2 - 1e-6

    for target in ([role, under] if under else [role]):
        verts, groups, faces = [], [], []
        for i, ring in enumerate(rings):
            verts.extend(ring)
            groups.extend([bones[i] if bones else m.bone] * sides)
        for i in range(len(path) - 1):
            for j in range(sides):
                if (target == under) != is_under(j):
                    continue
                a0, a1 = i * sides + j, i * sides + (j + 1) % sides
                faces.append([a0, a1, a1 + sides, a0 + sides])
        if target == role:
            if caps[0]:
                faces.append(list(range(sides))[::-1])
            if caps[1]:
                faces.append([(len(path) - 1) * sides + j for j in range(sides)])
        part_verts, part_faces = m.parts.setdefault(target, ([], []))
        start = len(part_verts)
        part_verts.extend(verts)
        part_faces.extend([[start + k for k in f] for f in faces])
        m.groups.setdefault(target, []).extend(groups)


def fine(path, bones=None, per=3):
    """A sweep path with per times as many rings, on a smooth curve through the old ones, widths easing between them. Fewer
    hard corners: it's what turns a stack of boxes into a body. Returns the path and its bones, one each per ring."""
    count = (len(path) - 1) * per + 1
    points = curve([p for p, _, _ in path], count)

    def ease(values, u):
        k = min(int(u), len(values) - 2)
        t = u - k
        a, b, c, d = values[max(k - 1, 0)], values[k], values[k + 1], values[min(k + 2, len(values) - 1)]
        value = 0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (3 * b - a - 3 * c + d) * t ** 3)
        return max(min(value, max(b, c) * 1.08), min(b, c) * 0.92, 0.02)

    widths, heights = [w for _, w, _ in path], [h for _, _, h in path]
    out, ring_bones = [], []
    for i, p in enumerate(points):
        u = i / per
        out.append((p, ease(widths, u), ease(heights, u)))
        if bones:
            ring_bones.append(bones[min(round(u), len(bones) - 1)])
    return out, (ring_bones if bones else None)


def sweep_fine(m, role, path, bones=None, per=3, sides=12, **options):
    """sweep(), smoothed by fine()."""
    rings, ring_bones = fine(path, bones, per)
    sweep(m, role, rings, ring_bones, sides=sides, **options)


def ring_round(m, role, centre, radius, normal, tube, count=14, squash=1.0):
    """A hoop round centre, flat to normal: the rim of an eye, a collar, a crater."""
    n = Vector(normal).normalized()
    u = n.cross(Vector((0, 0, 1)))
    if u.length < 1e-3:
        u = Vector((1, 0, 0))
    u.normalize()
    v = u.cross(n)
    c = Vector(centre)
    points = [tuple(c + u * math.cos(a) * radius + v * math.sin(a) * radius * squash) for a in (i * math.tau / count for i in range(count + 1))]
    sweep(m, role, [(p, tube, tube) for p in points], sides=6, caps=(False, False), up=tuple(n))


def jointed(m, role, names, path, parent="Spine", sides=8, under=None, under_faces=3, caps=(True, True)):
    """A swept tube (path as in sweep) bending on a run of bones: a tail on Tail1-3, a neck. The first ring stays on
    parent; the rest are shared out between names in order, each bone pivoting on the ring before its first."""
    count = len(path)
    bones = [parent]
    for i in range(1, count):
        bones.append(names[min((i - 1) * len(names) // (count - 1), len(names) - 1)])
    for k, name in enumerate(names):
        first = bones.index(name) if name in bones else None
        if first is None:
            continue
        m.joint(name, tuple(path[first - 1][0]), parent if k == 0 else names[k - 1])
    sweep(m, role, path, bones, sides=sides, under=under, under_faces=under_faces, caps=caps)
    return bones


def skin(m, role, verts, faces, bones):
    """A mesh with its own bone on each vertex, so it stretches between them."""
    part_verts, part_faces = m.parts.setdefault(role, ([], []))
    start = len(part_verts)
    part_verts.extend(verts)
    part_faces.extend([[start + i for i in f] for f in faces])
    m.groups.setdefault(role, []).extend(bones)


def sheet(m, role, grid, bones, thick=0.14):
    """A skin stretched over a grid of points, rows of equal length, with a bone for each point, closed all round so it shows
    from both sides: a wing's membrane. Studio draws only the outside of a mesh, so a single layer would vanish from behind."""
    rows, cols = len(grid), len(grid[0])
    pts = [[Vector(p) for p in row] for row in grid]

    def normal(i, j):
        along = pts[min(i + 1, rows - 1)][j] - pts[max(i - 1, 0)][j]
        across = pts[i][min(j + 1, cols - 1)] - pts[i][max(j - 1, 0)]
        n = along.cross(across)
        return n.normalized() if n.length > 1e-6 else Vector((0, 0, 1))

    def at(layer, i, j):
        return layer * rows * cols + i * cols + j

    verts, groups, faces = [], [], []
    for sign in (1, -1):
        for i in range(rows):
            for j in range(cols):
                verts.append(tuple(pts[i][j] + normal(i, j) * sign * thick / 2))
                groups.append(bones[i][j])
    for i in range(rows - 1):
        for j in range(cols - 1):
            faces.append([at(0, i, j), at(0, i + 1, j), at(0, i + 1, j + 1), at(0, i, j + 1)])
            faces.append([at(1, i, j + 1), at(1, i + 1, j + 1), at(1, i + 1, j), at(1, i, j)])
    edge = [(i, 0) for i in range(rows - 1)] + [(rows - 1, j) for j in range(cols - 1)]
    edge += [(i, cols - 1) for i in range(rows - 1, 0, -1)] + [(0, j) for j in range(cols - 1, 0, -1)]
    for (a, b), (c, d) in zip(edge, edge[1:] + edge[:1]):
        faces.append([at(0, a, b), at(1, a, b), at(1, c, d), at(0, c, d)])
    skin(m, role, verts, faces, groups)


def beast_head(m, y, zm, length, width, height, gape=-0.7, upper="Body", lower=None, brow="Accent", eye=0.5, teeth=8, fang=1.0, socket=1.8, throat=1.0, tooth=1.0, layer=0.04):
    """A bare head that is mostly mouth, for the Maul monsters: a wedge of skull, small slit eyes in black sockets under a brow
    slanting hard to the nose, rows of long teeth and a lower jaw hanging wide. y and zm: the back of the jaw hinge. Call it on the
    Head bone; it makes the Jaw."""
    lower = lower or upper
    table = [(0, 0.62, 0.86, 1.0), (0.28, 0.66, 1.0, 1.06), (0.55, 0.5, 0.84, 0.76), (0.8, 0.36, 0.6, 0.5), (1.0, 0.26, 0.38, 0.28)]
    sweep_fine(m, upper, [((0, y + length * t, zm + height * c), width * w, height * h) for t, c, w, h in table], sides=12)
    ey, ez, ew, eh = y + length * 0.5, zm + height * 0.53, width * 0.87, height * 0.82
    for side in (-1, 1):
        look = Vector((side * 0.34, 0.93, -0.1))
        at = Vector((side * math.cos(0.72) * ew / 2 * 0.92, ey, ez + math.sin(0.72) * eh / 2 * 0.92))
        egg(m, "Socket", tuple(at), eye * socket, eye * 0.9, eye * socket * 0.7, 10, 5)
        slit_eye(m, tuple(at + look * eye * 0.5), eye, look, side, iris="EyeColour", lid_role=upper, top=0.56, tilt=0.88, low=0.44, slit=0.2, layer=layer)
        sweep_fine(m, brow, [((side * width * 0.46, y + length * 0.36, ez + eh * 0.5), height * 0.06, height * 0.06), ((side * width * 0.34, y + length * 0.46, ez + eh * 0.6), height * 0.3, height * 0.24), ((side * width * 0.14, y + length * 0.6, ez + eh * 0.42), height * 0.24, height * 0.2), ((side * width * 0.02, y + length * 0.72, ez + eh * 0.18), height * 0.05, height * 0.05)], sides=6, per=2)
        egg(m, "Mouth", (side * width * 0.09, y + length * 0.985, zm + height * 0.3), width * 0.04, width * 0.05, height * 0.06, 10, 5)
    sweep(m, "Mouth", [((0, y + length * 0.02, zm + 0.04), width * 0.62, 0.3), ((0, y + length * 0.7, zm + 0.04), width * 0.42, 0.26), ((0, y + length * 0.96, zm + 0.1), width * 0.16, 0.2)], sides=8)
    egg(m, "Mouth", (0, y + length * 0.05, zm + height * 0.02), width * 0.33 * throat, height * 0.2 * throat, height * 0.22 * throat, 10, 5)

    def rim(t, narrow):
        return width / 2 * (narrow - 0.5 * t * t)

    for side in (-1, 1):
        for k in range(teeth):
            t = 0.3 + 0.68 * k / (teeth - 1)  # none further back: the corners of the mouth cover them
            tall = tooth * height * (0.34 + 0.16 * (k % 2)) * (1.7 * fang if k == teeth - 2 else 1.0)
            x, yy = side * rim(t, 0.78), y + length * t
            sabre(m, "Teeth", [(x, yy, zm + 0.1), (x, yy + 0.04, zm - tall * 0.5), (x, yy + 0.2 * height * 0.2, zm - tall)], height * 0.17 * (1.4 if k == teeth - 2 else 1.0), 4, sides=5)
    m.use("Jaw", (0, y + length * 0.04, zm - 0.02), "Head")
    z = zm - height * 0.14
    sweep_fine(m, lower, [((0, y + length * 0.04, z), width * 0.84, height * 0.32), ((0, y + length * 0.5, z), width * 0.72, height * 0.3), ((0, y + length * 0.85, z + height * 0.02), width * 0.46, height * 0.24), ((0, y + length * 0.99, z + height * 0.06), width * 0.26, height * 0.14)], sides=10, per=2)
    sweep(m, "Mouth", [((0, y + length * 0.08, z + height * 0.16), width * 0.5, 0.14), ((0, y + length * 0.86, z + height * 0.14), width * 0.14, 0.12)], sides=8)
    sweep_fine(m, "Tongue", [((0, y + length * 0.16, z + height * 0.2), width * 0.3, height * 0.1), ((0, y + length * 0.55, z + height * 0.2), width * 0.24, height * 0.08), ((0, y + length * 0.74, z + height * 0.19), width * 0.08, height * 0.04)], sides=6, per=2)
    for side in (-1, 1):
        for k in range(teeth - 1):
            t = 0.32 + 0.62 * k / (teeth - 2)
            tall = tooth * height * (0.3 + 0.14 * (k % 2)) * (1.6 * fang if k == teeth - 3 else 1.0)
            x, yy = side * rim(t, 0.66), y + length * t
            sabre(m, "Teeth", [(x, yy, z + height * 0.13), (x, yy + 0.03, z + height * 0.13 + tall * 0.5), (x, yy - 0.05, z + height * 0.13 + tall)], height * 0.15, 4, sides=5)
    swing(m, ["Jaw"], (0, y + length * 0.04, zm - 0.02), gape)
    # Skin stretched across the corners of the mouth, from the skull to the hanging jaw: it stretches as the jaw moves.
    hinge = Vector((0, y + length * 0.04, zm - 0.02))
    turn = Matrix.Rotation(gape, 3, Vector((1, 0, 0)))
    for side in (-1, 1):
        rows, ring_bones = [], []
        for t in (0.04, 0.12, 0.2, 0.28, 0.34):
            high = Vector((side * rim(t, 0.9), y + length * t, zm + height * 0.1))
            low = hinge + turn @ (Vector((side * rim(t, 0.82), y + length * t, z + height * 0.04)) - hinge)
            sag = high.lerp(low, 0.5) - Vector((side * width * 0.03 * (t / 0.34), length * 0.05 * (t / 0.34), 0))
            rows.append([tuple(high), tuple(sag), tuple(low)])
            ring_bones.append(["Head", "Head", "Jaw"])
        sheet(m, upper, rows, ring_bones, 0.22)
    m.bone = "Head"


def on_the_floor(m):
    """Claws that hook below the ground stop at it."""
    verts = m.parts["Claw"][0]
    verts[:] = [(x, y, max(z, 0.04)) for x, y, z in verts]


def panel(m, role, corners, thick=0.08):
    """A flat four-cornered panel with a little thickness: a sail between two spines, a fin."""
    c = [Vector(p) for p in corners]
    normal = (c[1] - c[0]).cross(c[3] - c[0]).normalized() * thick / 2
    verts = [tuple(p - normal) for p in c] + [tuple(p + normal) for p in c]
    m._add(role, verts, [[0, 1, 2, 3], [7, 6, 5, 4]] + [[i, i + 4, (i + 1) % 4 + 4, (i + 1) % 4] for i in range(4)])


def curve(points, count):
    """count points along a smooth curve through points (Catmull-Rom), for sweep paths."""
    pts = [Vector(p) for p in points]
    out = []
    segments = len(pts) - 1
    for i in range(count):
        u = i / (count - 1) * segments
        k = min(int(u), segments - 1)
        t = u - k
        p0, p1, p2, p3 = pts[max(k - 1, 0)], pts[k], pts[k + 1], pts[min(k + 2, segments)]
        t2, t3 = t * t, t * t * t
        out.append(tuple(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)))
    return out


def chain(m, family, n, points, w0, w1=0.06, parent="Spine", role="Body", flat=None, breadth=None, sides=6):
    """A chain on up to three bones, <family><n>a, b and c, which sway for ever (sway_of): a feather, a crest, a strand
    of moss, a worm lure. The points are split between the bones, the first bone pivoting at points[0]. A swept tube
    that bends where the bones turn. flat makes it a flat strip, breadth wide (tapering to a third) and w thick, broad
    along the path's "side" or its "normal". Leaves m.bone on the last bone, so a tip can be added; returns the names."""
    count = len(points)
    per = max(1, math.ceil((count - 1) / 3))
    names, bones = [], []
    for i, p in enumerate(points):
        k = min(i // per, 2) if i < count - 1 else min((count - 2) // per, 2)
        name = f"{family}{n}{'abc'[k]}"
        if name not in names:
            m.joint(name, tuple(points[i]), names[-1] if names else parent)
            names.append(name)
        bones.append(name)
    widths = [w0 + (w1 - w0) * i / (count - 1) for i in range(count)]
    if flat:
        broad = [breadth * (1 - 0.66 * i / (count - 1)) for i in range(count)]
        if flat == "side":
            path = [(p, b, w) for p, w, b in zip(points, widths, broad)]
        else:
            path = [(p, w, b) for p, w, b in zip(points, widths, broad)]
        sweep(m, role, path, bones, sides=4)
    else:
        sweep(m, role, [(p, w, w) for p, w in zip(points, widths)], bones, sides=sides)
    m.bone = names[-1]
    return names


def poly(m, role, points, push):
    """A flat shape with thickness: points, and the same points moved by push (a vector, or one per point)."""
    n = len(points)
    pushes = push if isinstance(push, list) else [push] * n
    front = [Vector(p) for p in points]
    back = [p + Vector(q) for p, q in zip(front, pushes)]
    faces = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
    faces += [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    m._add(role, [tuple(p) for p in front + back], faces)


def leaf(m, role, base, tip, across, w, thick=0.12):
    """One feather or leaf: a rounded blade from base to tip, w wide along across."""
    a, b = Vector(base), Vector(tip)
    d = Vector(across).normalized() * w / 2
    length = b - a
    normal = length.cross(d).normalized() * thick
    pts = [a - d * 0.45, a + length * 0.5 - d, a + length * 0.84 - d * 0.62, b, a + length * 0.84 + d * 0.62, a + length * 0.5 + d, a + d * 0.45]
    poly(m, role, pts, normal)


def scallop(m, roles, xy, radii, z_top, z_tip, count, flare=0.2, thick=0.16, offset=0.0, front=None, front_half=0.6, arc=None):
    """A ring of overlapping feathers or scales round a body: each flap hangs from an ellipse (centre xy, radii) at
    z_top down to a point at z_tip, flaring out by flare (a share of the radius), so a ring reads as one soft tier with
    a pointed hem. roles are taken in turn; front: another role for the flaps within front_half radians of the front.
    arc (from, to): only that part of the ring."""
    cx, cy = xy
    rx, ry = radii
    half = math.pi / count * 1.2
    from_a, span = (arc[0], arc[1] - arc[0]) if arc else (offset, math.tau)
    for k in range(count):
        angle = from_a + (k + 0.5) * span / count if arc else from_a + k * span / count

        def at(a, grow, z):
            return Vector((cx + math.cos(a) * rx * grow, cy + math.sin(a) * ry * grow, z))

        z_mid = z_top + (z_tip - z_top) * 0.62
        pts = [at(angle - half, 1, z_top), at(angle + half, 1, z_top), at(angle + half * 0.95, 1 + flare * 0.6, z_mid), at(angle, 1 + flare, z_tip),
               at(angle - half * 0.95, 1 + flare * 0.6, z_mid)]
        centre = Vector((cx, cy, (z_top + z_tip) / 2))
        inward = [(centre - p).normalized() * thick for p in pts]
        gap = abs((angle - math.pi / 2 + math.pi) % math.tau - math.pi)
        role = front if front and gap < front_half else roles[k % len(roles)]
        poly(m, role, pts, inward)


def sabre(m, role, points, w0, count=7, flat=1.0, sides=6, power=1.5):
    """A curved claw, tooth or horn through points, w0 thick at its base and running to a point. flat: its width across
    the curve, as a share of its depth."""
    path = curve(points, count)
    rings = []
    for i, p in enumerate(path):
        w = w0 * (1 - (i / (count - 1)) ** power) + 0.015
        rings.append((p, w * flat, w))
    sweep(m, role, rings, sides=sides)


def swing(m, bones, pivot, angle, axis=(1, 0, 0)):
    """Turns everything on these bones round pivot, the bones with it: a lower jaw built shut hangs open at rest."""
    turn = Matrix.Rotation(angle, 3, Vector(axis))
    p = Vector(pivot)
    for role, (verts, _) in m.parts.items():
        for i, bone in enumerate(m.groups[role]):
            if bone in bones:
                verts[i] = tuple(p + turn @ (Vector(verts[i]) - p))
    for name in bones:
        at, parent = m.joints[name]
        m.joints[name] = (tuple(p + turn @ (Vector(at) - p)), parent)


def bandage(m, path, bones, rng, step=0.6, tilt=0.3, roles=("Body", "Body", "Accent", "Belly")):
    """Wraps a tube (path as in sweep, bones one per point) in overlapping bands, each a slanted ring a little bigger than the
    last or smaller, so a mummy reads as wound with cloth. The tube under it shows through where a band is left out."""
    pts = [Vector(p) for p, _, _ in path]
    lengths = [0.0]
    for a, b in zip(pts, pts[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    frames = frames_along(pts)

    def at(d):
        d = max(0.0, min(d, lengths[-1] - 1e-5))
        i = max(k for k in range(len(pts) - 1) if lengths[k] <= d)
        t = (d - lengths[i]) / (lengths[i + 1] - lengths[i])
        (_, wa, ha), (_, wb, hb) = path[i], path[i + 1]
        side = frames[i][1].lerp(frames[i + 1][1], t).normalized()
        normal = frames[i][2].lerp(frames[i + 1][2], t).normalized()
        ahead = (pts[i + 1] - pts[i]).normalized()
        return pts[i].lerp(pts[i + 1], t), wa + (wb - wa) * t, ha + (hb - ha) * t, side, normal, ahead, bones[i + 1 if t > 0.5 else i]

    count = max(2, round(lengths[-1] / step))
    sides = 8
    for k in range(count):
        if rng.random() < 0.05:  # a gap: the shadow under the wraps shows
            continue
        d0, d1 = k * lengths[-1] / count, (k + 1.14) * lengths[-1] / count
        slant = tilt * (1 if (k // 2) % 2 else -1) * rng.uniform(0.6, 1.1)
        puff = 1.0 + rng.uniform(0.0, 0.06)
        spin = rng.uniform(0, math.tau)
        verts, groups = [], []
        for d in (d0, d1):
            p, w, h, side, normal, ahead, bone = at(d)
            for j in range(sides):
                a = math.pi / sides + j * math.tau / sides
                verts.append(tuple(p + side * math.cos(a) * w / 2 * puff + normal * math.sin(a) * h / 2 * puff + ahead * slant * math.sin(a + spin) * min(w, h) * 0.3))
                groups.append(bone)
        faces = [[j, (j + 1) % sides, sides + (j + 1) % sides, sides + j] for j in range(sides)]
        faces += [list(range(sides))[::-1], [sides + j for j in range(sides)]]
        role = rng.choice(roles)
        part_verts, part_faces = m.parts.setdefault(role, ([], []))
        start = len(part_verts)
        part_verts.extend(verts)
        part_faces.extend([[start + i for i in f] for f in faces])
        m.groups.setdefault(role, []).extend(groups)


def stripes(m, roles, points, w, grow=0.0):
    """A rod along points, one colour after the other: a crook, a beard. grow: each stripe a little thinner than the last."""
    for i, (a, b) in enumerate(zip(points, points[1:])):
        wa, wb = max(w - grow * i, 0.05), max(w - grow * (i + 1), 0.04)
        sweep(m, roles[i % len(roles)], [(tuple(a), wa, wa), (tuple(b), wb, wb)], sides=6)


def cap(m, role, centre, radii, axis, angle, squash=(1.0, 1.0), spin=0.0, rings=3, sides=10):
    """A patch lying on a ball or an egg (radii: one number, or across, along, up): round axis, angle radians wide,
    squash its width and height. Irises, pupils, shines, blushes, masks and spots."""
    c = Vector(centre)
    r = Vector((radii, radii, radii)) if isinstance(radii, (int, float)) else Vector(radii)
    a = Vector(axis).normalized()
    u = a.cross(Vector((0, 0, 1)))
    if u.length < 1e-3:
        u = Vector((1, 0, 0))
    u.normalize()
    v = u.cross(a)
    if spin:
        q = Quaternion(a, spin)
        u, v = q @ u, q @ v
    su, sv = squash

    def on(direction):
        return tuple(c + direction * r)

    verts = [on(a)]
    for i in range(1, rings + 1):
        th = angle * i / rings
        for j in range(sides):
            ph = math.tau * j / sides
            verts.append(on((a * math.cos(th) + (u * math.cos(ph) * su + v * math.sin(ph) * sv) * math.sin(th)).normalized()))
    verts.append(tuple(c + a * r * (math.cos(angle) * 0.86)))
    last = len(verts) - 1
    faces = [[0, 1 + j, 1 + (j + 1) % sides] for j in range(sides)]
    for i in range(rings - 1):
        p, q = 1 + i * sides, 1 + (i + 1) * sides
        faces += [[p + j, q + j, q + (j + 1) % sides, p + (j + 1) % sides] for j in range(sides)]
    rim = 1 + (rings - 1) * sides
    faces += [[rim + (j + 1) % sides, rim + j, last] for j in range(sides)]
    m._add(role, verts, faces)


def lid(m, role, centre, r, look, share, tilt, side, lower=False):
    """A skin lid on an eyeball. share: 0 barely there, 1 nearly shut. tilt: its inner end lower (positive, fierce) or
    higher (negative, soft); side: +1 for the eye at +X. lower: the bottom lid."""
    forward = Vector(look).normalized()
    up = Vector((0, -1, 0)) if abs(forward.z) > 0.95 else Vector((0, 0, 1))
    up = (up - forward * up.dot(forward)).normalized()
    if lower:
        up = -up
    up = Quaternion(forward, side * tilt * (1 if lower else -1)) @ up
    edge = math.radians((70 - 60 * share) if lower else (62 - 84 * share))
    cap(m, role, centre, r * 1.09, up, math.pi / 2 - edge, rings=4, sides=12)


def round_eye(m, centre, r, look, side, iris="EyeColour", iris_size=0.66, pupil_size=0.44, lid_role="Body", top=0.0, tilt=0.0, low=0.0):
    """A big bright eye: a white ball with a curved coloured iris, a big pupil and two shines, under skin lids."""
    egg(m, "EyeWhite", centre, r, r, r, 10, 6)
    forward = Vector(look).normalized()
    cap(m, iris, centre, r * 1.008, forward, iris_size)
    cap(m, "Pupil", centre, r * 1.016, forward, pupil_size)
    u = forward.cross(Vector((0, 0, 1))).normalized()
    v = u.cross(forward)
    cap(m, "Highlight", centre, r * 1.024, forward - u * side * 0.3 + v * 0.34, 0.2, sides=8, rings=2)
    cap(m, "Highlight", centre, r * 1.024, forward + u * side * 0.26 - v * 0.3, 0.09, sides=6, rings=2)
    if top or tilt:
        lid(m, lid_role, centre, r, forward, top, tilt, side)
    if low:
        lid(m, lid_role, centre, r, forward, low, 0.0, side, lower=True)


def slit_eye(m, centre, r, look, side, iris="EyeColour", lid_role="Body", top=0.42, tilt=0.5, low=0.3, slit=0.2, pupil="Pupil", layer=0.04):
    """A fierce eye: a dark ball, a burning iris with a thin upright slit and a glint, half shut under hard lids. pupil: the
    role of its slit. A spare eye takes "Slit": the reveal aims at the middle of the Pupil parts. layer: the gap between ball, iris,
    slit and lids, in studs; closer than this and they shimmer from far away."""
    egg(m, "Socket", centre, r, r, r, 10, 6)
    forward = Vector(look).normalized()
    cap(m, iris, centre, r + layer, forward, 0.98, rings=5, sides=12)
    cap(m, pupil, centre, r + 2 * layer, forward, 0.86, squash=(slit, 1.0), rings=6, sides=12)  # finely cut and raised, or the iris pokes through it
    u = forward.cross(Vector((0, 0, 1))).normalized()
    v = u.cross(forward)
    cap(m, "Highlight", centre, r + 3 * layer, forward - u * side * 0.34 + v * 0.3, 0.12, sides=6, rings=2)
    lid(m, lid_role, centre, (r + 5 * layer) / 1.09, forward, top, tilt, side)
    lid(m, lid_role, centre, (r + 5 * layer) / 1.09, forward, low, 0.0, side, lower=True)


# ---------------------------------------------------------------------- previews


def quick_preview(models, out, sky, ground, glow_roles, glow):
    """Stills only, for trying shapes and faces: each model whole, from the side, its face, and the lineup."""
    scene = kit.setup_scene()
    kit.RENDERS = out
    out.mkdir(parents=True, exist_ok=True)
    kit.NO_STUDS.update(glow_roles)
    animals = bpy.data.collections.new("Animals")
    scene.collection.children.link(animals)
    roots = []
    for i, model in enumerate(models):
        root = model.build(animals)
        root.location = (i * 30, 0, 0)
        roots.append(root)
    light_up(roots, glow_roles, glow)
    mesh = bpy.data.meshes.new("Ground")
    mesh.from_pydata([(-300, -300, -0.01), (400, -300, -0.01), (400, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    mesh.materials.append(kit.material("Ground", ground, False))
    scene.collection.objects.link(bpy.data.objects.new("Ground", mesh))
    set_sky(scene, sky)
    bpy.context.view_layer.update()
    for model, root in zip(models, roots):
        kit.set_visible(roots, [root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 3)
        kit.shoot(scene, f"{model.name}_full", centre + Vector((0.62, 0.85, 0.32)) * reach * 0.95, centre, (720, 720), 50)
        kit.shoot(scene, f"{model.name}_side", centre + Vector((1.15, 0.02, 0.14)) * reach * 0.95, centre, (720, 720), 50)
        kit.shoot(scene, f"{model.name}_back", centre + Vector((-0.6, -0.9, 0.4)) * reach * 0.95, centre, (720, 720), 50)
        head = root.location + Vector(model.head_centre)
        size = max(3.2, model.head_centre[2] * 0.5)
        kit.shoot(scene, f"{model.name}_face", head + Vector((0.55, 1.0, 0.14)) * size * 1.2, head, (720, 720), 50)
        kit.shoot(scene, f"{model.name}_front", head + Vector((0, 1, 0.1)) * size * 1.3, head, (720, 720), 50)
    for model in models:
        tris = sum(len(f) - 2 for _, faces in model.parts.values() for f in faces)
        lo = [round(min(v[i] for vs, _ in model.parts.values() for v in vs), 1) for i in range(3)]
        hi = [round(max(v[i] for vs, _ in model.parts.values() for v in vs), 1) for i in range(3)]
        print(f"  {model.name}: {tris} triangles, {len(model.joints)} bones {sorted(model.joints)}, box {lo} to {hi}")


def closeups(models, renders, video, glow_roles, glow):
    """A close look at each monster through its idle, round the roar: its sways, pinches and flicks up close. Runs after
    the .blend is saved, so nothing here reaches the model."""
    scene = bpy.context.scene
    roots = [bpy.data.objects[model.name] for model in models]
    light_up(roots, glow_roles, glow)
    for obj in bpy.data.objects:
        if obj.name.startswith("Player"):
            obj.hide_render = True
    frames = renders / "closeup_frames"
    frames.mkdir(exist_ok=True)
    data = bpy.data.cameras.new("Closeup")
    data.lens = 38
    camera = bpy.data.objects.new("Cam_Closeup", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = 960, 720
    number = 0
    for model, root in zip(models, roots):
        kit.set_visible(roots, [root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        target = centre.lerp(root.location + Vector(model.head_centre), 0.5)
        camera.location = target + Vector((0.55, 1.0, 0.15)).normalized() * (high - low).length * 0.85
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        root.animation_data.action = bpy.data.actions[f"{root.name}_Idle"]
        for frame in range(60, 180, 2):
            scene.frame_set(frame)
            scene.render.filepath = str(frames / f"f{number:04d}.png")
            bpy.ops.render.render(write_still=True)
            number += 1
        root.animation_data.action = None
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "15", "-i", str(frames / "f%04d.png"), "-pix_fmt", "yuv420p",
                    str(renders / video)], check=True)
    for frame in frames.glob("*.png"):
        frame.unlink()
    frames.rmdir()


def run(builders, renders, blend, slug, sky, ground, glow_roles=(), glow=1.2, spacing=24):
    """QUICK=1 (stills into QUICK_OUT), ONLY=a,b (just those builders), or everything: renders, both videos and the .blend."""
    only = os.environ.get("ONLY")
    if only:
        builders = [b for b in builders if b.__name__ in only.split(",")]
    models = [b() for b in builders]
    if os.environ.get("QUICK"):
        quick_preview(models, Path(os.environ.get("QUICK_OUT", str(renders / "quick"))), sky, ground, set(glow_roles), glow)
        return
    kit.NO_STUDS.update(glow_roles)
    build_and_render(models, renders, HERE / f"{blend}.blend", f"{slug}_animation_preview.mp4", sky=sky, ground=ground,
                     glow_roles=set(glow_roles), spacing=spacing, animate_fn=animate, walk_frames=WALK_PREVIEW, glow=glow)
    if not only:
        closeups(models, renders, f"{slug}_closeups.mp4", set(glow_roles), glow)
