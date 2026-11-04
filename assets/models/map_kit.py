"""Shared tools for a map's props in Blender (background mode), so a new map's script only models its props and
says where they go. The whole recipe for a new map is docs/MAP_RECIPE.md; build_eclipse_temple.py is the
example to copy.

What's here:
- Shape helpers every map uses, gathered from the older maps' scripts (Model, beam, prism, limb, ball, ...).
- The preview stage: a stretch of corridor at the game's real size (Config/Map: 88 wide, walls 44 tall, rims
  out to 116), in the map's colours, decorated the way MapDecor places props from Config/Decor.
- Glow and motion: light_up makes glowing roles shine in renders, apply_motion makes the same moves
  PropMotionController makes in the game (spin, swing, bob, pulse, fall, drift), so the videos show the game.
- Stills and videos (render_video needs ffmpeg).

1 Blender unit = 1 stud. Props stand on Z = 0 at their origin and face +Y. In the preview stage the corridor
floor is Z = 0, the rims Z = 44, and the corridor runs along -Y (a game distance d is Y = -d).
"""
import math
import random
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402,F401  (re-exported: kit.setup_scene, kit.shoot, kit.bounds, kit.NO_STUDS)
from build_desert import beam  # noqa: E402,F401
from build_forest import Model  # noqa: E402,F401
from build_shadow_bog import bezier, dome, limb, moss_beard, puddle  # noqa: E402,F401
from build_starfall_crater import ball, boulder, crystal, flat_ring, gem, hoop, sparkle, star_prism  # noqa: E402,F401
from build_swamp import place_copy  # noqa: E402,F401
from build_volcano import hide_markers, prism, set_sky  # noqa: E402,F401

# The corridor's real size (Config/Map, Config/Decor). Change them here if the game's change.
HALF_WIDTH = 44  # the corridor walls' inner faces, from the middle (Config/Map platform.width / 2)
WALL = 44  # corridor floor to rim
ISLAND_EDGE = 116  # the rims run out to here
OVERHEAD_BUILT_FOR = 72  # overhead props are modelled for this width; MapDecor stretches them to 88
GLOW_STRENGTH = 3.0


def prop(name, **colours):
    return kit.Model(f"prop_{name}", colours)


def role_of(obj):
    """The colour role of a part: the last word of its name, as shared/Roles.luau reads it in the game."""
    return obj.name.split(".")[0].rsplit("_", 1)[-1]


def prop_of(root):
    return root.name.split(".")[0].replace("_copy", "")


def set_visible(roots, shown):
    kit.set_visible(roots, shown)
    hide_markers(roots)


# ---------------------------------------------------------------------- shapes not in the older kits


def disc(m, role, x, y, z, r, thick, sides=16, plane="xy"):
    """A flat round slab: lying down (plane "xy") or standing up facing Y ("xz")."""
    if plane == "xy":
        prism(m, role, x, y, z - thick / 2, z + thick / 2, r, r, sides, math.pi / sides)
        return
    verts = []
    for dy in (-thick / 2, thick / 2):
        for i in range(sides):
            a = math.pi / sides + i * math.tau / sides
            verts.append((x + r * math.cos(a), y + dy, z + r * math.sin(a)))
    faces = [list(range(sides))[::-1], list(range(sides, 2 * sides))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides + j, sides + i])
    m._add(role, verts, faces)


def plate(m, role, a, b, side, w0, w1, thick):
    """A flat plate from a to b, w0 wide at a and w1 at b, its width along `side` (a direction) and `thick`
    across both. beam() picks the width direction itself, which lays rays and feathers flat; this doesn't."""
    a, b = Vector(a), Vector(b)
    along = (b - a).normalized()
    side = Vector(side)
    side = (side - along * side.dot(along)).normalized()
    normal = along.cross(side).normalized()
    verts = []
    for point, w in ((a, w0), (b, w1)):
        for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            verts.append(tuple(point + side * sx * w / 2 + normal * sz * thick / 2))
    faces = [[0, 1, 2, 3], [7, 6, 5, 4]] + [[i, i + 4, (i + 1) % 4 + 4, (i + 1) % 4] for i in range(4)]
    m._add(role, verts, faces)


def hanging_vine(m, role, x, y, top, length, width=0.35, rng=None, leaf_role=None):
    """A vine hanging straight down from (x, y, top), with a few leaf blocks along it."""
    m.block(role, x, y, top - length / 2, width, width, length)
    if leaf_role:
        rng = rng or random.Random(int(x * 13 + y * 7))
        z = top - rng.uniform(0.6, 1.4)
        while z > top - length + 0.4:
            side = rng.choice((-1, 1))
            m.block(leaf_role, x + side * width * 0.9, y, z, width * 1.6, width * 1.2, width * 0.9)
            z -= rng.uniform(1.0, 2.0)


# ---------------------------------------------------------------------- preview stage


def corridor_stage(stage, colours, length=360, seed=7):
    """A stretch of corridor in the map's colours at the game's size. colours: FloorA, FloorB, Dirt, DirtB, Grass
    (the game makes the two-tone checker from one colour; the preview fakes it with two)."""
    m = Model("PreviewCorridor", dict(colours))
    m.bone = "Root"
    across = int(HALF_WIDTH * 2 / 8)
    for ix in range(across):
        for iy in range(length // 8):
            m.block("FloorA" if (ix + iy) % 2 == 0 else "FloorB", -HALF_WIDTH + 4 + ix * 8, -iy * 8 - 4, -0.5, 8, 8, 1)
    rng = random.Random(seed)
    thick = ISLAND_EDGE - HALF_WIDTH
    # Like the game's wall kit (build_world_kit.py): dirt up to 2 below the rim, 2 of grass on top (so props on
    # the rim stand at WALL), and grass hanging 1.5 out from the wall's face. Nothing may lie flush on the wall's
    # face: two surfaces in one place flicker (z-fighting).
    rows = 6
    row = (WALL - 2) / rows
    for side in (-1, 1):
        for iz in range(rows):
            for iy in range(length // 8):
                m.block("Dirt" if (iz + iy) % 2 == 0 else "DirtB", side * (HALF_WIDTH + thick / 2), -iy * 8 - 4, (iz + 0.5) * row,
                        thick, 8, row)
        m.block("Grass", side * (HALF_WIDTH + thick / 2), -length / 2, WALL - 1, thick, length, 2)
        m.block("Grass", side * (HALF_WIDTH - 0.75), -length / 2, WALL - 2, 1.5, length, 4)
        y = 0
        while y < length:
            drip = rng.choice((0, 4, 4, 8, 8, 12, 16))
            if drip:
                m.block("Grass", side * (HALF_WIDTH - 0.75), -y - 4, WALL - 4 - drip / 2, 1.5, 8, drip)
            y += 8
    return m.build(stage)


def star_dome(stage, count=300, seed=3, colours=("#ffffff", "#d8e6ff"), radius=1400, glow=5):
    """For night and dusk renders: specks of light on a far dome."""
    m = Model("PreviewStars", {"Star": colours[0], "StarB": colours[1]})
    m.bone = "Root"
    rng = random.Random(seed)
    for k in range(count):
        a = rng.uniform(0, math.tau)
        e = rng.uniform(0.15, 1.3)
        s = rng.uniform(2.5, 6)
        m.block("Star" if k % 3 else "StarB", math.cos(e) * math.cos(a) * radius, math.cos(e) * math.sin(a) * radius - 150,
                math.sin(e) * radius, s, s, s)
    root = m.build(stage)
    light_up([root], {"Star", "StarB"}, glow)
    return root


def decorate_stage(stage, built, rules, length=360, seed=61):
    """Lays the built props out like MapDecor does with Config/Decor. rules mirrors a biome's Decor table:
        floor:    dict(first, gap=(lo, hi), side=(lo, hi), props=[(name, weight, (lo, hi))],
                       extras=dict(chance, spread, props=[...]))
        rim:      dict(first, gap, chance, side, props)
        overhead: [(name, distance, yaw, scale)]       across the corridor, stretched like the game does
        walls:    [(name, distance, side)]             on a wall's top edge, facing the middle
        spots:    [(name, distance, x, on, yaw, scale, face)] on = "rim" or "floor"; face (optional) "middle"
                  turns its Front towards the corridor's middle, "along" down the corridor, then yaw is added
    Returns the copies, so motion_entries can move them."""
    rng = random.Random(seed)
    copies = []

    def pick(table):
        total = sum(w for _, w, _ in table)
        roll = rng.uniform(0, total)
        for name, weight, scale in table:
            roll -= weight
            if roll <= 0:
                return name, scale
        return table[-1][0], table[-1][2]

    def put(name, location, yaw, scale):
        if name not in built:
            return
        copy = place_copy(built[name], stage, location, yaw, scale)
        for child in copy.children:  # copies are named ..._Front.001, so hide_markers misses them
            if role_of(child) == "Front":
                child.hide_render = True
        copies.append(copy)

    def put_random(table, x, z, distance):
        name, (low, high) = pick(table)
        put(name, (x, -distance, z), rng.uniform(0, math.tau), rng.uniform(low, high))

    floor = rules.get("floor")
    if floor:
        d = floor["first"]
        while d < length - floor["gap"][0]:
            side = rng.choice((-1, 1))
            x = side * rng.uniform(*floor["side"])
            put_random(floor["props"], x, 0, d)
            extras = floor.get("extras")
            if extras and rng.random() < extras["chance"]:
                spread = extras["spread"]
                ex = side * min(max(abs(x) + rng.uniform(-spread, spread), floor["side"][0] - 4), HALF_WIDTH - 3)
                put_random(extras["props"], ex, 0, d + rng.uniform(-spread, spread))
            d += rng.uniform(*floor["gap"])
    rim = rules.get("rim")
    if rim:
        d = rim["first"]
        while d < length:
            for side in (-1, 1):
                if rng.random() < rim["chance"]:
                    put_random(rim["props"], side * rng.uniform(*rim["side"]), WALL, d)
            d += rng.uniform(*rim["gap"])
    stretch = HALF_WIDTH * 2 / OVERHEAD_BUILT_FOR
    for name, d, yaw, scale in rules.get("overhead", ()):
        if d < length:
            put(name, (0, -d, WALL), math.pi + math.radians(yaw), scale * stretch)
    for name, d, side in rules.get("walls", ()):
        if d < length:
            put(name, (side * HALF_WIDTH, -d, WALL), side * math.pi / 2, 1)
    for spot in rules.get("spots", ()):
        name, d, x, on, yaw, scale = spot[:6]
        face = spot[6] if len(spot) > 6 else None
        turn = math.radians(yaw)
        if face == "middle":  # the model's front is +Y; turn it towards X = 0
            turn += math.pi / 2 if x > 0 else -math.pi / 2
        elif face == "along":
            turn += math.pi
        if d < length:
            put(name, (x, -d, 0 if on == "floor" else WALL), turn, scale)
    return copies


def clear(roots):
    for root in roots:
        for child in list(root.children):
            bpy.data.objects.remove(child)
        bpy.data.objects.remove(root)


# ---------------------------------------------------------------------- glow and motion


def light_up(roots, roles, strength=None):
    """Glowing roles shine in the renders (the game makes them Neon). Call again with 0 before saving, so the
    export stays plain colours. Too strong and a colour clips to white or cyan, so a map can lower
    map_kit.GLOW_STRENGTH."""
    strength = GLOW_STRENGTH if strength is None else strength
    for root in roots:
        for child in root.children:
            if child.type == "MESH" and role_of(child) in roles:
                for mat in child.data.materials:
                    nodes = mat.node_tree.nodes
                    bsdf = nodes.get("Principled BSDF")
                    bsdf.inputs["Emission Color"].default_value = nodes["Colour"].outputs[0].default_value
                    bsdf.inputs["Emission Strength"].default_value = strength


AXES = {"up": Vector((0, 0, 1)), "across": Vector((1, 0, 0)), "ahead": Vector((0, 1, 0))}


def mesh_centre(obj):
    vs = [v.co for v in obj.data.vertices]
    return Vector([(min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(3)])


def motion_entries(roots, motion):
    """Everything that moves: (part or None, its motion, the centre it turns round, phase, root, root's start).
    motion is the map's MOTION table, {prop name: {role: moves}}, the same as Config/PropMotion."""
    entries = []
    for root in roots:
        moves = motion.get(prop_of(root), {})
        phase = (sum(ord(ch) * (i + 1) for i, ch in enumerate(root.name)) % 997) / 997
        if "*" in moves:
            entries.append((None, moves["*"], None, phase, root, root.location.copy()))
        for child in root.children:
            mo = moves.get(role_of(child))
            if mo:
                centre = mesh_centre(child) if mo.get("about") == "self" else Vector((0, 0, mo.get("height", 0)))
                entries.append((child, mo, centre, phase, root, None))
    return entries


def _turned(centre, axis, angle):
    return Matrix.Translation(centre) @ Matrix.Rotation(angle, 4, axis) @ Matrix.Translation(-centre)


def apply_motion(entries, t):
    """The moves PropMotionController makes in the game, at time t seconds (see Config/PropMotion)."""
    for obj, mo, centre, phase, root, root_start in entries:
        if obj is None:  # drift: the whole prop glides head first (+Y in the model) and starts over
            ahead = (root.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
            along = mo["drift"] * (((t / mo["period"]) + phase) % 1 - 0.5)
            root.location = root_start + ahead * along
            continue
        cycle = t / mo["period"] + phase if "period" in mo else 0
        axis = AXES[mo.get("axis", "up")]
        m = Matrix.Identity(4)
        if "swing" in mo:
            m = _turned(centre, axis, math.radians(mo["swing"]) * math.sin(math.tau * cycle)) @ m
        if "spin" in mo:
            m = _turned(centre, axis, math.radians(mo["spin"]) * t) @ m
        lift = 0.0
        if "bob" in mo:
            lift += mo["bob"] * math.sin(math.tau * cycle)
        if "fall" in mo:
            lift -= mo["fall"] * (cycle % 1)
        obj.matrix_basis = Matrix.Translation((0, 0, lift)) @ m
        if "pulse" in mo:
            k = mo["pulse"] + (1 - mo["pulse"]) * (0.5 + 0.5 * math.sin(math.tau * cycle))
            for mat in obj.data.materials:
                mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = GLOW_STRENGTH * k


def reset_motion(entries):
    for obj, mo, centre, phase, root, root_start in entries:
        if obj is None:
            root.location = root_start
        else:
            obj.matrix_basis = Matrix.Identity(4)
            if "pulse" in mo:
                for mat in obj.data.materials:
                    mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = GLOW_STRENGTH


# ---------------------------------------------------------------------- renders


def render_video(scene, folder, name, frames, fps, camera_at, size):
    """Renders frames into folder/name.mp4. camera_at(frame) gives (position, target, lens, update), and
    update(seconds) is called first, to move the props."""
    tmp = folder / f"{name}_frames"
    tmp.mkdir(parents=True, exist_ok=True)
    data = bpy.data.cameras.new(name)
    data.clip_end = 3000
    camera = bpy.data.objects.new(f"Cam_{name}", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = size
    for f in range(frames):
        position, target, lens, update = camera_at(f)
        update(f / fps)
        data.lens = lens
        camera.location = Vector(position)
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(tmp / f"f{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(tmp / "f%04d.png"),
                    "-pix_fmt", "yuv420p", "-vf", f"scale={size[0]}:-2", str(folder / f"{name}.mp4")], check=True)
    for frame in tmp.glob("*.png"):
        frame.unlink()
    tmp.rmdir()


def shoot_prop(scene, name, root, player_root, everything, view=(0.5, 0.9, 0.42), distance=1.25, size=(600, 600), lens=50):
    """A still of one prop, with a player-sized block beside it for scale."""
    low, high = kit.bounds(root)
    player_root.location = Vector((low.x - 3, (low.y + high.y) / 2 + 2, root.location.z))
    bpy.context.view_layer.update()
    set_visible(everything, [root, player_root])
    centre = (low + high) / 2
    reach = max((high - low).length, 7)
    kit.shoot(scene, name, centre + Vector(view) * reach * distance, centre, size, lens)


def player_block(stage):
    player = Model("Player", {"Skin": "#d8d2c4"})
    player.bone = "Root"
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    return player.build(stage)
