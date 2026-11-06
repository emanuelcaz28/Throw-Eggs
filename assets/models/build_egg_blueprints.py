"""Adds the eggs that have no block model yet to blueprints.json: Frost, Shadow and Abyss, and one for each of
maps 9 to 15. Every egg is the Dirty Egg's shape painted by its own rule, some with blocks stuck on (thorns, gear
teeth). Run it, then export_luau.py. Running it again replaces these eggs, so tweak and re-run freely.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).parent
BLUEPRINTS = HERE / "blueprints.json"
EYE_ROWS = (9, 10)  # the egg is 16 blocks tall
EYE_COLUMNS = (2, 3)


def noise(x, y, z, seed):
    """A repeatable 0..1 number for a block, so speckles stay put between runs."""
    v = math.sin(x * 12.9898 + y * 78.233 + z * 37.719 + seed * 19.19) * 43758.5453
    return v - math.floor(v)


def angle(x, y):
    return math.atan2(y, x) % (2 * math.pi)


def frost(x, y, z, top):
    if z >= top - 2:
        return "#ffffff"
    if z >= top - 3 and noise(x, y, 0, 1) < 0.5:
        return "#ffffff"
    if noise(x, y, z, 2) < 0.14:
        return "#e8fbff"
    return "#5fb8ea" if z <= 2 else "#a8e4ff"


def shadow(x, y, z, top):
    if x > 0 and z in EYE_ROWS and abs(y) in EYE_COLUMNS:
        return "#d9b8ff"  # two pale eyes looking out of the dark
    wave = math.sin(angle(x, y) * 2 + z * 0.9)
    return "#6e3cbf" if wave > 0.45 else "#3a2160"


def abyss(x, y, z, top):
    if noise(x, y, z, 3) < 0.13:
        return "#4ff0e0"  # glowing like the deep sea's lures
    return "#0a2438" if z <= 3 else "#0e3a56"


def eclipse(x, y, z, top):
    middle = top // 2
    if z == middle:
        return "#ffc83c"
    if z == middle + 1 and noise(x, y, 0, 4) < 0.3:
        return "#fff0b0"
    return "#15102a" if z > middle else "#2a1f4a"


def forbidden(x, y, z, top):
    if z in (2, top - 2):
        return "#e0b040"  # gilt bands, like an old book's spine
    if z == top // 2:
        return "#f2e4c0"  # a strip of pages
    return "#6b2f2a" if noise(x, y, z, 5) > 0.12 else "#57231f"


def carnival(x, y, z, top):
    if z >= top - 1:
        return "#ffc83c"
    return "#e8304a" if int(angle(x, y) / (math.pi / 4)) % 2 == 0 else "#fff3e0"


def clockwork(x, y, z, top):
    middle = top // 2
    if abs(z - middle) <= 1:
        return "#8a8f9c"
    if noise(x, y, z, 6) < 0.08:
        return "#ffe08a"  # rivets
    return "#c98a2e"


def thorn(x, y, z, top):
    if noise(x, y, z, 7) < 0.1:
        return "#d82a5c"  # rosebuds
    return "#24502f" if int(angle(x, y) * 2 + z * 0.5) % 2 == 0 else "#2f6b3e"


def spore(x, y, z, top):
    if z <= top // 2 - 1:
        return "#efe0bd"  # the stalk end
    return "#d6ff7a" if noise(x, y, z, 8) < 0.16 else "#8a5cc8"


def weeping(x, y, z, top):
    """No colour at all, red only for the eyes (map 15's rule)."""
    if x > 0 and z in EYE_ROWS and abs(y) in EYE_COLUMNS:
        return "#e01020"
    if x > 0 and z < min(EYE_ROWS) and abs(y) in EYE_COLUMNS:
        return "#2c2c30"  # what runs down from them
    return "#8d8d92" if noise(x, y, z, 9) > 0.2 else "#6a6a70"


def add_thorns(cells):
    """Short brown spikes standing out of the shell."""
    extra = {}
    for (x, y, z) in cells:
        if noise(x, y, z, 10) < 0.09 and math.hypot(x, y) >= 2:
            step = (int(math.copysign(1, x)) if abs(x) >= abs(y) else 0, int(math.copysign(1, y)) if abs(y) > abs(x) else 0)
            for reach in (1, 2):
                spot = (x + step[0] * reach, y + step[1] * reach, z)
                if spot not in cells:
                    extra[spot] = "#5a3b1e"
    return extra


def add_teeth(cells):
    """Gear teeth round the steel band."""
    middle = max(z for _, _, z in cells) // 2
    extra = {}
    ring = [(x, y) for (x, y, z) in cells if z == middle]
    reach = max(math.hypot(x, y) for x, y in ring)
    for index in range(8):
        a = index * math.pi / 4
        spot = (round(math.cos(a) * (reach + 1)), round(math.sin(a) * (reach + 1)))
        for z in (middle - 1, middle, middle + 1):
            extra[(spot[0], spot[1], z)] = "#8a8f9c"
    return {k: v for k, v in extra.items() if k not in cells}


EGGS = {
    "egg_FrostEgg": (frost, None),
    "egg_ShadowEgg": (shadow, None),
    "egg_AbyssEgg": (abyss, None),
    "egg_EclipseEgg": (eclipse, None),
    "egg_ForbiddenEgg": (forbidden, None),
    "egg_CarnivalEgg": (carnival, None),
    "egg_ClockworkEgg": (clockwork, add_teeth),
    "egg_ThornEgg": (thorn, add_thorns),
    "egg_SporeEgg": (spore, None),
    "egg_WeepingEgg": (weeping, None),
}


def main():
    data = json.loads(BLUEPRINTS.read_text())
    shape = {(x, y, z) for x, y, z, _ in data["egg_DirtyEgg"]}
    top = max(z for _, _, z in shape)
    for name, (paint, extras) in EGGS.items():
        cells = {cell: paint(*cell, top) for cell in shape}
        if extras:
            cells.update(extras(shape))
        data[name] = [[x, y, z, colour] for (x, y, z), colour in sorted(cells.items())]
    BLUEPRINTS.write_text(json.dumps(data, separators=(",", ":")))
    print(f"{len(EGGS)} eggs written; shape is {len(shape)} blocks, {top + 1} tall")


if __name__ == "__main__":
    main()
