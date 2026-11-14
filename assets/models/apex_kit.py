"""Shared by the 9th to 12th monsters of Spore Hollow and The Weeping Dark (build_spore_hollow_apex.py, build_weeping_dark_apex.py).

The owner, 2026-11-13: four more monsters on maps 14 and 15, rarer than the 8 each has, "even more aggressive than the rarest", with
"unique animations with unique vfx ... or just objects that look good and can be animated on the monsters using the map's themes", clean
geometry and clean animations, "including the idle animations". No rarity and no chances yet, so they are not in Config/Dinos.

What is new here:

  - An attack each, nothing else has it. A marker bone picks the table, as MARKED does in rare_kit.py; the tables are the same as the
    APEX block in DinoLifeController, number for number. Each is 4 seconds long and, in the game, plays once every DinoLife.attackCycle.
  - Effects that never stop, on bones the game turns steadily whatever the monster is doing (SPIN in DinoLifeController):
        Halo    round the upright, a quarter turn a second      Wheel   round the forward axis, the same speed
        Hoop    round the sideways axis, the same speed         Saw     round the sideways axis, a whole turn a second
    Everything stays on the monster: nothing is thrown, dripped or puffed out (owner, 2026-11-10).
  - Three actions per monster instead of two: Walk and Idle are the monster at peace (breathing, looking round, the roar, what sways,
    what spins) and Attack is the idle with the attack on top, twice through. Every one loops without a jump. The game takes no
    animation from the FBX (it poses the bones itself), so these are for looking at in Blender.
  - Bones are posed in the game's order (pitch outermost, then roll, then yaw: Euler ZYX), so a whirl with a lean in it previews as it plays.

1 Blender unit = 1 stud, models face +Y, feet on Z = 0. Plain colours, no stud image.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rare_kit  # noqa: E402  (first: it turns the stud preview off)
import build_forest as kit  # noqa: E402
from build_clockwork_citadel_monsters import fcurves_of  # noqa: E402
from build_thorn_kingdom_monsters import point  # noqa: E402
from monster_stage import light_up, set_sky  # noqa: E402
from rare_kit import ACROSS, AHEAD, PITCH, RISE, ROLL, W, WALK_PREVIEW, YAW, beat, keys, ring_round, stacked, wave  # noqa: E402

PI = math.pi

# ---------------------------------------------------------------------- what turns for ever (SPIN in DinoLifeController)

SPIN = {"Halo": (PI / 2, 2), "Wheel": (PI / 2, 1), "Hoop": (PI / 2, 0), "Saw": (2 * PI, 0)}  # radians a second, axis (0 X, 1 Y, 2 Z)


def spin_pose(a, f):
    for name, (speed, axis) in SPIN.items():
        rotation = [0.0, 0.0, 0.0]
        rotation[axis] = speed * f / 30
        kit.pose_bone(a, name, tuple(rotation), None, f)


# ---------------------------------------------------------------------- the attacks (APEX in DinoLifeController)


def shaken(points, speed, reach, slot=PITCH, phase=0.0):
    """A wave that only runs while its envelope (points, over the 4 seconds) is up."""
    def move(s):
        out = [0.0] * 6
        out[slot] = reach * keys((s / 4) % 1, points) * math.sin(speed * W * s - phase)
        return tuple(out)
    return move


def pulsed(points, seconds, envelope, slot=PITCH, scale=1.0, start=0.0):
    """A short run of keys (points, `seconds` long) repeated from `start` on, only while its envelope is up: pecks, chews."""
    def move(s):
        out = [0.0] * 6
        out[slot] = scale * keys(((s - start) / seconds) % 1, points) * keys((s / 4) % 1, envelope)
        return tuple(out)
    return move


# Rot Weiler (Triad, its chest): three heads. It sinks back, the left head strikes, then the right, then the middle; then all three rear
# and it throws itself forward on them, shaking what they caught.
SNAP = [(0, 0), (0.06, 0.4), (0.1, -0.55), (0.16, -0.55), (0.26, 0), (1, 0)]
SNAP_JAW = [(0, 0), (0.06, -0.5), (0.094, -0.5), (0.11, 0.42), (0.17, 0.42), (0.26, 0), (1, 0)]
SNAP_OUT = [(0, 0), (0.06, 0.3), (0.1, 0.45), (0.16, 0.45), (0.26, 0), (1, 0)]
TRI_ALL = [(0, 0), (0.64, 0), (0.7, 0.35), (0.735, -0.4), (0.86, -0.4), (0.95, 0), (1, 0)]
TRI_ALL_JAW = [(0, 0), (0.64, 0), (0.7, -0.6), (0.73, -0.6), (0.745, 0.42), (0.86, 0.42), (0.95, 0), (1, 0)]
TRI_SURGE = [(0, 0), (0.08, -1.5), (0.64, -1.5), (0.7, -2.6), (0.735, 6), (0.86, 6), (0.96, 0), (1, 0)]
TRI_LEAN = [(0, 0), (0.08, 0.08), (0.64, 0.08), (0.7, 0.2), (0.735, -0.14), (0.86, -0.14), (0.96, 0), (1, 0)]
TRI_SHAKE = [(0, 0), (0.735, 0), (0.76, 1), (0.84, 1), (0.88, 0), (1, 0)]
TRI_LEGS = [(0, 0), (0.08, -0.1), (0.64, -0.1), (0.7, -0.18), (0.735, 0.5), (0.86, 0.3), (0.96, 0), (1, 0)]
TRI_WAG = [(0, 0), (0.08, 1), (0.9, 1), (1, 0)]
TRIAD = {
    "Spine": stacked(beat(TRI_SURGE, 4, AHEAD), shaken(TRI_WAG, 20, 0.01)),
    "Triad": beat(TRI_LEAN, 4),
    "NeckL": stacked(beat(SNAP, 4, PITCH, 1.0, 0.1), beat(SNAP_OUT, 4, YAW, 1.0, 0.1), beat(TRI_ALL, 4), shaken(TRI_SHAKE, 24, 0.12, YAW)),
    "NeckR": stacked(beat(SNAP, 4, PITCH, 1.0, 0.24), beat(SNAP_OUT, 4, YAW, -1.0, 0.24), beat(TRI_ALL, 4), shaken(TRI_SHAKE, 24, -0.12, YAW)),
    "Neck": stacked(beat(SNAP, 4, PITCH, 1.0, 0.38), beat(TRI_ALL, 4), shaken(TRI_SHAKE, 24, 0.16, YAW, 1.0)),
    "JawL": stacked(beat(SNAP_JAW, 4, PITCH, 1.0, 0.1), beat(TRI_ALL_JAW, 4)),
    "JawR": stacked(beat(SNAP_JAW, 4, PITCH, 1.0, 0.24), beat(TRI_ALL_JAW, 4)),
    "Jaw": stacked(beat(SNAP_JAW, 4, PITCH, 1.0, 0.38), beat(TRI_ALL_JAW, 4)),
    "FrontL": beat(TRI_LEGS, 4), "FrontR": beat(TRI_LEGS, 4), "BackL": beat(TRI_LEGS, 4, PITCH, -1.0), "BackR": beat(TRI_LEGS, 4, PITCH, -1.0),
    "Tail1": shaken(TRI_WAG, 16, 0.3, YAW),
}

# Acid Reign (Crown, the crown over its head): it draws itself up to its full height, hood flung wide, and sways; the crown tips down
# over its face like a saw and it throws its whole length at the ground, once ahead and once to the side.
REIGN_RISE = [(0, 0), (0.16, 1), (0.44, 1), (0.5, 0), (0.62, 0.7), (0.68, 0.7), (0.73, 0), (1, 0)]
REIGN_HIT = [(0, 0), (0.44, 0), (0.5, 1), (0.58, 1), (0.64, 0), (0.68, 0), (0.73, 1), (0.84, 1), (0.94, 0), (1, 0)]
REIGN_SWAY = [(0, 0), (0.14, 0), (0.2, 1), (0.4, 1), (0.45, 0), (1, 0)]
REIGN_SIDE = [(0, 0), (0.6, 0), (0.68, 0.5), (0.84, 0.5), (0.96, 0), (1, 0)]
REIGN_FLARE = [(0, 0), (0.14, 1), (0.86, 1), (1, 0)]
REIGN_JAW = [(0, 0), (0.16, -0.3), (0.46, -0.4), (0.505, 0.4), (0.58, 0.4), (0.64, -0.35), (0.69, -0.4), (0.735, 0.4), (0.84, 0.4), (1, 0)]
REIGN_VISOR = [(0, 0), (0.16, 0), (0.44, 0.15), (0.5, 1), (0.58, 1), (0.64, 0.25), (0.68, 0.25), (0.73, 1), (0.84, 1), (0.95, 0), (1, 0)]
REIGN = {
    "Rear1": stacked(beat(REIGN_RISE, 4, PITCH, 0.16), beat(REIGN_HIT, 4, PITCH, -0.5), shaken(REIGN_SWAY, 4, 0.22, YAW), beat(REIGN_SIDE, 4, YAW)),
    "Rear2": stacked(beat(REIGN_RISE, 4, PITCH, 0.1), beat(REIGN_HIT, 4, PITCH, -0.45), shaken(REIGN_SWAY, 4, -0.12, YAW)),
    "Rear3": stacked(beat(REIGN_RISE, 4, PITCH, -0.2), beat(REIGN_HIT, 4, PITCH, -0.3)),
    "Neck": beat(REIGN_HIT, 4, PITCH, 0.3),
    "Head": beat(REIGN_HIT, 4, PITCH, 0.2),
    "Jaw": beat(REIGN_JAW, 4),
    "FrillL": stacked(beat(REIGN_FLARE, 4, YAW, -0.85), shaken(REIGN_FLARE, 24, 0.05, YAW)),
    "FrillR": stacked(beat(REIGN_FLARE, 4, YAW, 0.85), shaken(REIGN_FLARE, 24, -0.05, YAW)),
    "Crown": stacked(beat(REIGN_RISE, 4, RISE, 1.5), beat(REIGN_VISOR, 4, PITCH, -1.45), beat(REIGN_VISOR, 4, AHEAD, 8.5), beat(REIGN_VISOR, 4, RISE, -7.5)),
}

# Cap Punishment (SawArm1, the arm out of its back): the saw is cocked back, brought down on the ground ahead and dragged across, left to
# right, the whole beast shaking with it; up again and down again.
SAW_ARM = [(0, 0), (0.16, -0.3), (0.24, -0.34), (0.29, 1), (0.52, 1), (0.6, -0.2), (0.66, -0.24), (0.71, 1), (0.82, 1), (0.94, 0), (1, 0)]  # 1: down on the ground
SAW_DRAG = [(0, 0), (0.24, 0), (0.29, -1), (0.52, 1), (0.6, 0), (1, 0)]
SAW_ON = [(0, 0), (0.27, 0), (0.3, 1), (0.52, 1), (0.56, 0), (0.7, 0), (0.72, 1), (0.82, 1), (0.86, 0), (1, 0)]
SAW_LEAN = [(0, 0), (0.16, 0.14), (0.24, 0.16), (0.29, -0.2), (0.52, -0.2), (0.6, 0.1), (0.66, 0.12), (0.71, -0.24), (0.82, -0.24), (0.94, 0), (1, 0)]
SAW_JAW = [(0, 0), (0.16, -0.2), (0.29, -0.55), (0.52, -0.55), (0.6, 0), (0.71, -0.55), (0.82, -0.55), (0.94, 0), (1, 0)]
SAW_RAKE = [(0, 0), (0.24, 0.9), (0.29, -0.2), (0.52, -0.2), (0.66, 0.9), (0.71, -0.2), (0.82, -0.2), (0.94, 0), (1, 0)]
SAW_REACH = (-0.9, 0.05, 0.35)  # how far each joint of the arm turns to put the saw on the ground
SAWYER = {
    "Spine": stacked(beat(SAW_LEAN, 4), shaken(SAW_ON, 28, 0.012, ROLL)),
    "LegL": beat(SAW_LEAN, 4, PITCH, -1.0), "LegR": beat(SAW_LEAN, 4, PITCH, -1.0),
    "Neck": beat(SAW_LEAN, 4, PITCH, 0.6),
    "Head": shaken(SAW_ON, 28, 0.05, YAW),
    "Jaw": beat(SAW_JAW, 4),
    "ArmL": beat(SAW_RAKE, 4), "ArmR": beat(SAW_RAKE, 4, PITCH, 1.0, 0.02),
    "Tail1": shaken(SAW_ON, 12, 0.2, YAW),
    "SawArm1": stacked(beat(SAW_ARM, 4, PITCH, SAW_REACH[0]), beat(SAW_DRAG, 4, YAW, 0.3)),
    "SawArm2": beat(SAW_ARM, 4, PITCH, SAW_REACH[1]),
    "SawArm3": stacked(beat(SAW_ARM, 4, PITCH, SAW_REACH[2]), shaken(SAW_ON, 32, 0.025)),
}

# Sporeactor (Core, the light over its back): it sinks, the core climbs and whirls three times round, the rods in its back rising one
# after the other; it rears, and the core comes down as its front feet do. Everything shakes.
MELT_CHARGE = [(0, 0), (0.14, 0.3), (0.46, 1), (0.5, 1), (0.53, -0.2), (0.6, -0.2), (0.8, 0.1), (1, 0)]
MELT_SPIN = [(0, 0), (0.1, 0), (0.5, 6 * PI), (1, 6 * PI)]
MELT_ROD = [(0, 0), (0.1, 0), (0.42, 1), (0.48, 1), (0.52, -0.1), (0.62, 0), (1, 0)]
MELT_SINK = [(0, 0), (0.14, -1), (0.4, -1), (0.5, 0.6), (0.53, -1.2), (0.62, -1.2), (0.8, 0), (1, 0)]
MELT_REAR = [(0, 0), (0.4, 0), (0.5, 0.3), (0.53, -0.06), (0.62, -0.06), (0.8, 0), (1, 0)]
MELT_PAW = [(0, 0), (0.4, 0), (0.5, 0.6), (0.53, -0.06), (0.62, -0.06), (0.8, 0), (1, 0)]
MELT_ROAR = [(0, 0), (0.14, 0.2), (0.46, 0.34), (0.53, -0.3), (0.62, -0.3), (0.8, 0), (1, 0)]
MELT_JAW = [(0, 0), (0.14, -0.25), (0.46, -0.5), (0.7, -0.5), (0.8, 0), (1, 0)]
MELT_QUAKE = [(0, 0), (0.52, 0), (0.54, 1), (0.7, 0.4), (0.8, 0), (1, 0)]
MELTER = {
    "Spine": stacked(beat(MELT_SINK, 4, RISE), beat(MELT_REAR, 4), shaken(MELT_QUAKE, 28, 0.03, ROLL)),
    "Neck": beat(MELT_ROAR, 4),
    "Jaw": stacked(beat(MELT_JAW, 4), shaken(MELT_QUAKE, 24, 0.08)),
    "FrontL": beat(MELT_PAW, 4), "FrontR": beat(MELT_PAW, 4, PITCH, 1.0, 0.01),
    "BackL": beat(MELT_REAR, 4, PITCH, -1.0), "BackR": beat(MELT_REAR, 4, PITCH, -1.0),
    "Tail1": shaken(MELT_QUAKE, 16, 0.3, YAW),
    "Core": stacked(beat(MELT_CHARGE, 4, RISE, 6.0), beat(MELT_SPIN, 4, YAW)),
}
for n in range(1, 7):
    MELTER[f"Rod{n}"] = beat(MELT_ROD, 4, RISE, 4.2, 0.012 * n)

# Grim Weeper (Reap, its waist): both blades wound back to the right, one cut right across to the left and one back; then both up over
# its head, and down, falling forward on them.
REAP_TURN = [(0, 0), (0.16, -1), (0.2, -1), (0.27, 1), (0.36, 1), (0.43, -1), (0.5, -0.6), (0.58, 0), (1, 0)]
REAP_LIFT = [(0, 0), (0.5, 0), (0.6, 1), (0.64, 1), (0.68, -0.16), (0.82, -0.16), (0.94, 0), (1, 0)]
REAP_SPREAD = [(0, 0), (0.16, 1), (0.46, 1), (0.56, 0.2), (0.66, 0.2), (0.7, 0), (1, 0)]
REAP_LEAN = [(0, 0), (0.16, 0.1), (0.5, 0.1), (0.6, 0.3), (0.64, 0.32), (0.68, -0.45), (0.82, -0.45), (0.94, 0), (1, 0)]
REAP_AHEAD = [(0, 0), (0.2, 0), (0.27, 2.5), (0.36, 2.5), (0.43, 4), (0.6, 3), (0.64, 3), (0.68, 7), (0.82, 7), (0.95, 0), (1, 0)]
REAP_JAW = [(0, 0), (0.16, -0.3), (0.2, -0.45), (0.27, 0.3), (0.36, -0.4), (0.43, 0.3), (0.6, -0.5), (0.66, -0.5), (0.69, 0.4), (0.82, 0.4), (1, 0)]
REAP_TRAIL = [(0, 0), (0.2, 0), (0.27, -1), (0.36, 0), (0.43, 1), (0.52, 0), (0.64, 0), (0.68, 1.2), (0.82, 0.6), (0.94, 0), (1, 0)]
REAPER = {
    "Spine": beat(REAP_AHEAD, 4, AHEAD),
    "Reap": stacked(beat(REAP_TURN, 4, YAW, 1.0), beat(REAP_LEAN, 4)),
    "Neck": beat(REAP_TURN, 4, YAW, -0.7),
    "Jaw": beat(REAP_JAW, 4),
    "ArmL": stacked(beat(REAP_SPREAD, 4, ROLL, 0.8), beat(REAP_LIFT, 4, PITCH, 2.2)),
    "ArmR": stacked(beat(REAP_SPREAD, 4, ROLL, -0.8), beat(REAP_LIFT, 4, PITCH, 2.2)),
    "ReapL": beat(REAP_SPREAD, 4, YAW, 0.45), "ReapR": beat(REAP_SPREAD, 4, YAW, -0.45),
    "Tail1": stacked(beat(REAP_TRAIL, 4, YAW, 0.5), beat(REAP_TRAIL, 4, PITCH, 0.2)),
    "Tail2": beat(REAP_TRAIL, 4, YAW, 0.4, 0.03),
}

# Cage Rage (RibL1, its ribs): it rears right up and its ribs fling open one pair after the other, like a second mouth; it falls on you,
# they clamp shut, and it chews three times.
CAGE_REAR = [(0, 0), (0.14, 0.75), (0.3, 0.8), (0.36, -0.08), (0.8, -0.08), (0.92, 0), (1, 0)]
CAGE_OPEN = [(0, 0), (0.1, 1), (0.3, 1), (0.36, 0), (0.44, 0.8), (0.5, 0), (0.56, 0.8), (0.62, 0), (0.68, 0.8), (0.74, 0), (1, 0)]
CAGE_AHEAD = [(0, 0), (0.14, -1), (0.3, -1), (0.36, 7), (0.8, 7), (0.94, 0), (1, 0)]
CAGE_JAW = [(0, 0), (0.1, -0.5), (0.3, -0.55), (0.36, 0.4), (0.44, -0.3), (0.5, 0.4), (0.56, -0.3), (0.62, 0.4), (0.68, -0.3), (0.74, 0.4), (0.9, 0), (1, 0)]
CAGE_REACH = [(0, 0), (0.14, 1), (0.3, 1), (0.36, 0), (1, 0)]
CAGER = {
    "Spine": stacked(beat(CAGE_REAR, 4), beat(CAGE_AHEAD, 4, AHEAD)),
    "BackL": beat(CAGE_REAR, 4, PITCH, -1.0), "BackR": beat(CAGE_REAR, 4, PITCH, -1.0),
    "FrontL": stacked(beat(CAGE_REACH, 4, PITCH, 0.5), beat(CAGE_REACH, 4, ROLL, 0.5)),
    "FrontR": stacked(beat(CAGE_REACH, 4, PITCH, 0.5), beat(CAGE_REACH, 4, ROLL, -0.5)),
    "Neck": beat(CAGE_REAR, 4, PITCH, -0.6),
    "Jaw": beat(CAGE_JAW, 4),
    "Tail1": beat(CAGE_REAR, 4, PITCH, -0.5),
}
for n in range(1, 6):
    CAGER[f"RibL{n}"] = beat(CAGE_OPEN, 4, ROLL, 1.2, 0.012 * n)
    CAGER[f"RibR{n}"] = beat(CAGE_OPEN, 4, ROLL, -1.2, 0.012 * n)

# Mourning Star (Flail1, the root of its tail): the tail winds back and whirls three times round over it, flung out straight; then the
# star comes over its head and down on the ground in front of it, and bounces.
MOURN_WHIRL = [(0, 0), (0.1, -0.5), (0.16, -0.5), (0.6, 6 * PI), (1, 6 * PI)]
MOURN_OUT = [(0, 0), (0.14, 0.3), (0.24, 1), (0.56, 1), (0.62, 0), (1, 0)]
MOURN_SMASH = [(0, 0), (0.6, 0), (0.66, -0.3), (0.7, 1), (0.76, 1), (0.8, 0.8), (0.83, 1), (0.88, 1), (0.96, 0), (1, 0)]
MOURN_BRACE = [(0, 0), (0.16, -0.6), (0.6, -0.6), (0.66, 0.4), (0.7, -1.2), (0.88, -1.2), (0.96, 0), (1, 0)]
MOURN_HEAD = [(0, 0), (0.16, -0.25), (0.6, -0.25), (0.66, 0.3), (0.7, -0.2), (0.88, -0.2), (0.96, 0), (1, 0)]
MOURN_JAW = [(0, 0), (0.16, -0.3), (0.6, -0.4), (0.7, -0.55), (0.88, -0.55), (0.96, 0), (1, 0)]
MOURN_QUAKE = [(0, 0), (0.69, 0), (0.71, 1), (0.84, 0.4), (0.9, 0), (1, 0)]
MOURN_UNROLL = (0.0, -0.7, 0.0, 0.1, 0.4)  # how far each joint opens to fling the star out level
MOURN_REACH = (-1.4, 0.0, 0.0, 0.2, 0.4)  # and turns to put it on the ground ahead
MOURNER = {
    "Spine": stacked(beat(MOURN_BRACE, 4, RISE), shaken(MOURN_QUAKE, 28, 0.03, ROLL)),
    "Neck": beat(MOURN_HEAD, 4),
    "Jaw": beat(MOURN_JAW, 4),
    "Flail1": stacked(beat(MOURN_WHIRL, 4, YAW), beat(MOURN_SMASH, 4, PITCH, MOURN_REACH[0])),
}
for n in range(2, 6):
    MOURNER[f"Flail{n}"] = stacked(beat(MOURN_OUT, 4, PITCH, MOURN_UNROLL[n - 1]), beat(MOURN_SMASH, 4, PITCH, MOURN_REACH[n - 1]))

# Nevermore (Plume1, the feathers circling over it): wings up, beaten down, and it hops at you as the feathers burst outward; four pecks,
# fast; then wings flung wide, one long caw, and the feathers burst again.
PLUMES = 8
MURDER_WING = [(0, 0), (0.12, 1), (0.16, 1), (0.2, -0.35), (0.28, 0.3), (0.7, 0.3), (0.76, 1), (0.8, 1), (0.84, 0.5), (0.94, 0), (1, 0)]
MURDER_HOP = [(0, 0), (0.16, -0.8), (0.22, 5), (0.3, 0), (1, 0)]
MURDER_AHEAD = [(0, 0), (0.16, -1), (0.3, 5), (0.72, 5), (0.94, 0), (1, 0)]
MURDER_LEAN = [(0, 0), (0.16, 0.2), (0.3, -0.25), (0.7, -0.25), (0.78, 0.15), (0.94, 0), (1, 0)]
MURDER_PECKING = [(0, 0), (0.3, 0), (0.33, 1), (0.68, 1), (0.71, 0), (1, 0)]
MURDER_PECK = [(0, 0), (0.35, 0.45), (0.55, -1), (0.75, -1), (1, 0)]
MURDER_PECK_JAW = [(0, 0), (0.35, -0.5), (0.55, -0.5), (0.62, 0.35), (0.8, 0.35), (1, 0)]
MURDER_CAW = [(0, 0), (0.72, 0), (0.78, -0.7), (0.9, -0.7), (0.96, 0), (1, 0)]
MURDER_BURST = [(0, 0), (0.16, 0), (0.21, 1), (0.28, 1), (0.4, 0), (0.74, 0), (0.79, 1), (0.86, 1), (0.96, 0), (1, 0)]
MURDER_TREMBLE = [(0, 0), (0.28, 0), (0.32, 1), (0.9, 1), (0.96, 0), (1, 0)]
MURDERER = {
    "Spine": stacked(beat(MURDER_HOP, 4, RISE), beat(MURDER_AHEAD, 4, AHEAD), beat(MURDER_LEAN, 4)),
    "LegL": beat(MURDER_LEAN, 4, PITCH, -1.0), "LegR": beat(MURDER_LEAN, 4, PITCH, -1.0),
    "Neck": stacked(pulsed(MURDER_PECK, 0.38, MURDER_PECKING, PITCH, 0.6, 1.2), beat(MURDER_CAW, 4, PITCH, -0.3)),
    "Head": pulsed(MURDER_PECK, 0.38, MURDER_PECKING, PITCH, 0.35, 1.2),
    "Jaw": stacked(pulsed(MURDER_PECK_JAW, 0.38, MURDER_PECKING, PITCH, 1.0, 1.2), beat(MURDER_CAW, 4)),
    "WingL": stacked(beat(MURDER_WING, 4, ROLL, 0.9), shaken(MURDER_TREMBLE, 24, 0.05, ROLL)),
    "WingR": stacked(beat(MURDER_WING, 4, ROLL, -0.9), shaken(MURDER_TREMBLE, 24, -0.05, ROLL)),
    "WingTipL": beat(MURDER_WING, 4, ROLL, 0.5, 0.02), "WingTipR": beat(MURDER_WING, 4, ROLL, -0.5, 0.02),
    "Tail1": beat(MURDER_WING, 4, PITCH, 0.4),
}
for n in range(1, PLUMES + 1):
    angle = (n - 1) * math.tau / PLUMES
    MURDERER[f"Plume{n}"] = stacked(beat(MURDER_BURST, 4, ACROSS, 7 * math.cos(angle), 0.004 * n), beat(MURDER_BURST, 4, AHEAD, 7 * math.sin(angle), 0.004 * n))

# A monster with one of these bones has the rest of its body moved by that bone's table. The same eight lines as in DinoLifeController.
APEX_MOVES = {"Triad": TRIAD, "Crown": REIGN, "SawArm1": SAWYER, "Core": MELTER, "Reap": REAPER, "RibL1": CAGER, "Flail1": MOURNER, "Plume1": MURDERER}
rare_kit.MARKED.update(APEX_MOVES)


# ---------------------------------------------------------------------- the three actions

ZERO = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


def _pose(a, f, idle, attacking):
    table = rare_kit.marked_of(a)
    real = rare_kit.marked_of
    if not attacking:  # at peace: the attack's bones are keyed still, so nothing is left over from another action
        table = {name: (lambda s: ZERO) for name in table}
    rare_kit.marked_of = lambda _a: table
    try:
        (rare_kit.idle_pose if idle else rare_kit.walk_pose)(a, f)
    finally:
        rare_kit.marked_of = real
    spin_pose(a, f)


def animate(armature):
    """Walk (4 strides), Idle (8 seconds) and Attack (the idle with the attack on it, twice through). Returns walk, idle, attack."""
    walk = kit.add_action(armature, "Walk", WALK_PREVIEW, lambda a, f: _pose(a, f, False, False), 2)
    idle = kit.add_action(armature, "Idle", kit.IDLE_FRAMES, lambda a, f: _pose(a, f, True, False), 2)
    attack = kit.add_action(armature, "Attack", kit.IDLE_FRAMES, lambda a, f: _pose(a, f, True, True), 1)
    for action in (walk, idle, attack):  # a steady turn, not eased between keys
        for fcurve in fcurves_of(action):
            if any(f'"{name}"' in fcurve.data_path for name in SPIN):
                for key in fcurve.keyframe_points:
                    key.interpolation = "LINEAR"
    for bone in armature.pose.bones:  # the game's order: pitch outermost, yaw innermost
        bone.rotation_mode = "ZYX"
    armature.animation_data.action = idle
    return walk, idle, attack


def check_loops(armature, actions):
    """Every curve of every action ends where it starts (whole turns apart for what spins)."""
    bad = []
    for action in actions:
        last = action.frame_range[1]
        for fcurve in fcurves_of(action):
            a, b = fcurve.evaluate(0), fcurve.evaluate(last)
            gap = abs(b - a)
            if "rotation" in fcurve.data_path:
                gap = abs((gap + PI) % math.tau - PI)
            if gap > 1e-3:
                bad.append(f"{action.name} {fcurve.data_path}[{fcurve.array_index}] {a:.3f} -> {b:.3f}")
    print(f"LOOPS {armature.name}: " + ("clean" if not bad else f"{len(bad)} do not close"))
    for line in bad[:12]:
        print("LOOPS    " + line)


# ---------------------------------------------------------------------- shapes


def rename_bones(m, names):
    """Gives bones other names (a second head built with fierce_head, which only knows Head and Jaw)."""
    for groups in m.groups.values():
        groups[:] = [names.get(b, b) for b in groups]
    m.joints = {names.get(n, n): (pivot, names.get(parent, parent)) for n, (pivot, parent) in m.joints.items()}
    m.bone = names.get(m.bone, m.bone)


def shift(m, bones, offset):
    """Moves everything on these bones, the bones with it."""
    o = Vector(offset)
    for role, (verts, _) in m.parts.items():
        for i, bone in enumerate(m.groups[role]):
            if bone in bones:
                verts[i] = tuple(Vector(verts[i]) + o)
    for name in bones:
        at, parent = m.joints[name]
        m.joints[name] = (tuple(Vector(at) + o), parent)


def hoop(m, role, centre, radius, normal, tube, count=20, spikes=0, spike=1.5, spike_role="Claw", spike_w=None, start=0.0, lean=0.0):
    """A ring round centre, flat to normal, with spikes standing out of it all round (lean tips them along the normal).
    Returns where(angle): a point on the ring and the way out of it there."""
    n = Vector(normal).normalized()
    u = n.cross(Vector((0, 0, 1)))
    if u.length < 1e-3:
        u = Vector((1, 0, 0))
    u.normalize()
    v = u.cross(n)
    c = Vector(centre)
    ring_round(m, role, tuple(c), radius, tuple(n), tube, count)

    def where(angle):
        out = u * math.cos(angle) + v * math.sin(angle)
        return c + out * radius, out

    for k in range(spikes):
        at, out = where(start + k * math.tau / spikes)
        point(m, spike_role, tuple(at + out * tube * 0.2), tuple(at + out * (tube * 0.4 + spike) + n * lean * spike), spike_w or tube * 1.5)
    return where


# ---------------------------------------------------------------------- building, saving, looking


def run(builders, renders, blend, sky, ground, glow_roles=(), glow=1.0, spacing=60, attack_frames=(20, 36, 60, 84, 100)):
    """Everything: builds the monsters, makes their three actions, checks they loop and saves <blend>.blend.
    QUICK=1 renders stills into QUICK_OUT instead of saving (rest poses, and the attack at attack_frames); ONLY=a,b builds just those."""
    only = os.environ.get("ONLY")
    if only:
        builders = [b for b in builders if b.__name__ in only.split(",")]
    models = [b() for b in builders]
    quick = os.environ.get("QUICK")
    out = Path(os.environ.get("QUICK_OUT", str(renders / "quick")))
    scene = kit.setup_scene()
    kit.RENDERS = out if quick else renders
    kit.RENDERS.mkdir(parents=True, exist_ok=True)
    kit.NO_STUDS.update(glow_roles)
    animals = bpy.data.collections.new("Animals")
    scene.collection.children.link(animals)
    roots = []
    for i, model in enumerate(models):
        root = model.build(animals)
        root.location = (i * spacing, 0, 0)
        roots.append(root)
    light_up(roots, set(glow_roles), glow)
    stage = bpy.data.collections.new("Preview stage")
    scene.collection.children.link(stage)
    mesh = bpy.data.meshes.new("Ground")
    mesh.from_pydata([(-300, -300, -0.01), (600, -300, -0.01), (600, 300, -0.01), (-300, 300, -0.01)], [], [(0, 1, 2, 3)])
    mesh.materials.append(kit.material("Ground", ground, False))
    stage.objects.link(bpy.data.objects.new("Ground", mesh))
    set_sky(scene, sky)
    bpy.context.view_layer.update()
    for model in models:
        tris = sum(len(f) - 2 for _, faces in model.parts.values() for f in faces)
        lo = [round(min(v[i] for vs, _ in model.parts.values() for v in vs), 1) for i in range(3)]
        hi = [round(max(v[i] for vs, _ in model.parts.values() for v in vs), 1) for i in range(3)]
        print(f"BUILT {model.name}: {tris} triangles, {len(model.joints)} bones, box {lo} to {hi}")
    made = [animate(root) for root in roots]
    for root, actions in zip(roots, made):
        check_loops(root, actions)
    scene.frame_start, scene.frame_end = 0, kit.IDLE_FRAMES
    scene.render.fps = 30
    if not quick:
        scene.frame_set(0)
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE / f"{blend}.blend"))
        print("SAVED", blend)
        return
    size = (480, 480)
    for model, root, (walk, idle, attack) in zip(models, roots, made):
        kit.set_visible(roots, [root])
        root.animation_data.action = None
        for bone in root.pose.bones:
            bone.location, bone.rotation_euler = (0, 0, 0), (0, 0, 0)
        scene.frame_set(0)
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 3)
        names = []
        for tag, way in (("full", (0.62, 0.85, 0.32)), ("side", (1.15, 0.02, 0.14)), ("back", (-0.6, -0.9, 0.4))):
            kit.shoot(scene, f"{model.name}_{tag}", centre + Vector(way) * reach * 0.95, centre, size, 50)
            names.append(f"{model.name}_{tag}")
        head = root.location + Vector(model.head_centre)
        span = max(3.2, model.head_centre[2] * 0.5)
        kit.shoot(scene, f"{model.name}_face", head + Vector((0.55, 1.0, 0.14)) * span * 1.3, head, size, 50)
        kit.shoot(scene, f"{model.name}_front", head + Vector((0, 1, 0.1)) * span * 1.5, head, size, 50)
        names += [f"{model.name}_face", f"{model.name}_front"]
        root.animation_data.action = attack
        for frame in attack_frames:
            scene.frame_set(frame)
            kit.shoot(scene, f"{model.name}_attack{frame:03d}", centre + Vector((0.9, 0.55, 0.3)) * reach * 1.25 + Vector((0, 4, 0)), centre + Vector((0, 4, 0)), size, 50)
            names.append(f"{model.name}_attack{frame:03d}")
        root.animation_data.action = idle
        inputs = []
        for name in names:
            inputs += ["-i", str(out / f"{name}.png")]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", f"concat=n={len(names)}:v=1:a=0,tile=5x2", "-frames:v", "1", "-q:v", "4",
                        str(out / f"{model.name}_sheet.jpg")], check=False)
        for name in names:
            (out / f"{name}.png").unlink(missing_ok=True)
