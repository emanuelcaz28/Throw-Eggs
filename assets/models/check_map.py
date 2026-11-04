"""Checks a map's Blender script against the game's configs, so the two can't drift apart. Run it after any change
to a map's props, MOTION or DECOR, or to its configs (docs/MAP_RECIPE.md, step 6):

    Blender -b --python check_map.py -- build_eclipse_temple EclipseTemple

It builds the models in memory (no renders) and reads the game's Luau configs with lune (installed by rokit).
Checks: MOTION = Config/PropMotion, DECOR = Config/Decor, glowing roles are in shared/Roles.luau, moving roles exist
on their prop, props that need a Front marker have one, flat floor props are flat, overhead props stay above the
rim and reach both rims, and the world is in Biomes, Map, Lighting and export_fbx.py. Exits 1 on a problem.
On a monster script (build_<map>_monsters.py, no MOTION or DECOR) it checks the roles, the glow and the export line.
"""
import importlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

DUMP = """
local fs = require("@lune/fs")
local luau = require("@lune/luau")
local serde = require("@lune/serde")
local process = require("@lune/process")
local env = {
	Vector3 = { new = function(x, y, z) return { x, y, z } end },
	Color3 = { fromRGB = function(r, g, b) return { r, g, b } end, new = function(r, g, b) return { r, g, b } end },
}
setmetatable(env, { __index = function(_, key) return ({ math = math, string = string, table = table })[key] end })
local function load(path) return luau.load(fs.readFile(path), { environment = env })() end
local world = process.args[1]
local root = process.args[2]
local motion = load(root .. "/src/shared/Config/PropMotion.luau")
local decor = load(root .. "/src/shared/Config/Decor.luau")
local map = load(root .. "/src/shared/Config/Map.luau")
local lighting = load(root .. "/src/shared/Config/Lighting.luau")
local biomes = load(root .. "/src/shared/Config/Biomes.luau")
local roles = fs.readFile(root .. "/src/shared/Roles.luau")
local glowing = {}
for name in string.gmatch(string.match(roles, "Roles.glowing = (%b{})"), "([%w]+) = true") do
	glowing[name] = true
end
local ids = {}
for _, biome in biomes do table.insert(ids, biome.id) end
print(serde.encode("json", {
	motion = motion.props, decor = decor.corridor[world] or false, colors = map.biomeColors[world] or false,
	light = lighting.worlds[world] or false, biomes = ids, glowing = glowing,
	overheadBuiltFor = map.corridor.overheadBuiltFor,
}))
"""


def lune_path():
    found = sorted((Path.home() / ".rokit" / "tool-storage" / "lune-org" / "lune").glob("*/lune"))
    if not found:
        sys.exit("lune not found: install it with rokit")
    return str(found[-1])


def game_configs(world):
    with tempfile.NamedTemporaryFile("w", suffix=".luau", delete=False) as f:
        f.write(DUMP)
    out = subprocess.run([lune_path(), "run", f.name, world, str(ROOT)], capture_output=True, text=True)
    if out.returncode:
        sys.exit("lune failed:\n" + out.stderr)
    return json.loads(out.stdout)


def same(a, b):
    """Compares numbers loosely (Luau has no int/float split)."""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) < 1e-9
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def bounds(model):
    vs = [v for verts, _ in model.parts.values() for v in verts]
    return [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 2:
        sys.exit("usage: Blender -b --python check_map.py -- <build module> <world id>")
    module, world = args
    m = importlib.import_module(module)
    models = {model.name: model for model in (make() for make in m.ALL)}
    game = game_configs(world)
    problems = []

    def problem(text):
        problems.append(text)

    # Names: the game reads a part's role as the last word after "_".
    for name, model in models.items():
        for role in model.parts:
            if "_" in role:
                problem(f"{name}: role {role} has an underscore")

    # Motion.
    motion = getattr(m, "MOTION", {})
    for prop, moves in motion.items():
        if prop not in models:
            problem(f"MOTION: {prop} isn't one of the map's props")
            continue
        for role in moves:
            if role != "*" and role not in models[prop].parts:
                problem(f"MOTION: {prop} has no {role} role to move")
        if not same(moves, game["motion"].get(prop)):
            problem(f"MOTION and Config/PropMotion differ for {prop}:\n    blender {moves}\n    game    {game['motion'].get(prop)}")

    # Glow.
    glow = getattr(m, "GLOW_ROLES", set())
    for role in sorted(glow - set(game["glowing"])):
        problem(f"glowing role {role} is missing from Roles.glowing in shared/Roles.luau")
    for name, model in models.items():
        for role in model.parts:
            if role in game["glowing"] and role not in glow:
                problem(f"{name}: role {role} glows in the game (Roles.glowing) but isn't in GLOW_ROLES; rename it if it shouldn't")

    # Placement.
    decor = getattr(m, "DECOR", None)
    if decor is not None:
        lua = game["decor"]
        if not lua:
            problem(f"Config/Decor has no corridor.{world}")
        else:
            def table(rows):
                return [(r["name"], r["weight"], list(r["scale"])) for r in rows]

            f, d = lua["floor"], decor["floor"]
            pairs = [
                ("floor props", [[n, w, list(s)] for n, w, s in d["props"]], table(f["props"])),
                ("floor extras", [[n, w, list(s)] for n, w, s in d["extras"]["props"]], table(f["extras"]["props"])),
                ("floor numbers", [d["first"], list(d["gap"]), list(d["side"]), d["extras"]["chance"], d["extras"]["spread"]],
                 [f["firstDistance"], f["gap"], f["side"], f["extras"]["chance"], f["extras"]["spread"]]),
                ("rim props", [[n, w, list(s)] for n, w, s in decor["rim"]["props"]], table(lua["rim"]["props"])),
                ("rim numbers", [decor["rim"]["first"], list(decor["rim"]["gap"]), decor["rim"]["chance"], list(decor["rim"]["side"])],
                 [lua["rim"]["firstDistance"], lua["rim"]["gap"], lua["rim"]["chance"], lua["rim"]["side"]]),
                ("overhead", [list(o) for o in decor.get("overhead", [])],
                 [[o["name"], o["distance"], o["yaw"], o["scale"]] for o in lua.get("overhead", [])]),
                ("walls", [list(o) for o in decor.get("walls", [])], [[o["name"], o["distance"], o["side"]] for o in lua.get("walls", [])]),
                ("spots", [list(o) + ([None] if len(o) == 6 else []) for o in decor.get("spots", [])],
                 [[o["name"], o["distance"], o["x"], o["on"], o["yaw"], o["scale"], o.get("face")] for o in lua.get("spots", [])]),
            ]
            for what, a, b in pairs:
                if not same(a, b):
                    problem(f"DECOR and Config/Decor differ in {what}:\n    blender {a}\n    game    {b}")
        used = {row[0] for key in ("overhead", "walls", "spots") for row in decor.get(key, [])}
        used |= {row[0] for row in decor["floor"]["props"] + decor["floor"]["extras"]["props"] + decor["rim"]["props"]}
        for name in sorted(used - models.keys()):
            problem(f"DECOR places {name}, which the script doesn't build")
        for name in sorted(models.keys() - used):
            problem(f"{name} is built but never placed (DECOR)")
        facing = {row[0] for row in decor.get("overhead", []) + decor.get("walls", [])}
        facing |= {row[0] for row in decor.get("spots", []) if len(row) > 6 and row[6]}
        for name in sorted(facing & models.keys()):
            if "Front" not in models[name].parts:
                problem(f"{name} has to face a way (walls, overhead or a spot's face) but has no Front marker")
        for name in {row[0] for row in decor.get("spots", []) if row[3] == "floor"} & models.keys():
            low, high = bounds(models[name])
            if high[2] > 0.5:
                problem(f"{name} lies in the middle of the floor but is {high[2]:.2f} tall (keep it under 0.5)")
        for name in {row[0] for row in decor.get("overhead", [])} & models.keys():
            model = models[name]
            parts = {role: shape for role, shape in model.parts.items() if role != "Front"}
            low = min(v[2] for verts, _ in parts.values() for v in verts)
            if low < 0:
                problem(f"{name} dips {-low:.1f} below the rim, into the flight camera's way")
            reach = max(abs(v[0]) for verts, _ in parts.values() for v in verts)
            if reach < game["overheadBuiltFor"] / 2:
                problem(f"{name} reaches {reach:.0f} from the middle; its feet must be beyond {game['overheadBuiltFor'] / 2:.0f}")

    # The world itself.
    if world not in game["biomes"]:
        problem(f"Config/Biomes has no {world}")
    if not game["colors"]:
        problem(f"Config/Map biomeColors has no {world}")
    if not game["light"]:
        problem(f"Config/Lighting worlds has no {world} (it will use the Forest's light)")
    elif game["light"].get("lighting", {}).get("ClockTime", 0) > 6:
        problem(f"Config/Lighting {world} ClockTime is past 6: the blend from the night worlds tweens through daylight")
    export = (HERE / "export_fbx.py").read_text()
    blend = getattr(m, "BLEND", module.replace("build_", "") + "_models")
    if f'"{blend}"' not in export:
        problem(f"export_fbx.py MAP_OF_FILE has no line for {blend}")

    print(f"{module}: {len(models)} models, {len(motion)} with moving parts")
    for text in problems:
        print("  PROBLEM", text)
    print("all good" if not problems else f"{len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


main()
