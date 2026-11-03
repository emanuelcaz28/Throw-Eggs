"""Builds the map's layout blockout and renders it (run with Blender in background mode).

    Blender -b -P build_world_layout.py

Saves world_layout.blend and renders to design/world/. This is shapes and sizes only: the checker
materials are a preview of the Studio look, and no studs are modelled (those are applied in Studio).
The target is docs/GAME_SPEC.md sections 3 to 5 and the screenshots in docs/reference/.

1 Blender unit = 1 Roblox stud. Positions below are written in Roblox coordinates (X, Y up, Z);
at() turns them into Blender's. The corridor runs along Roblox -Z, which is Blender +Y. The arena
floor is Y = 0 and the throw line (where worlds start counting distance) is Z = 0.

The collections under "Stand-ins" show what the game places at runtime, for checking scale. They
never get exported. Everything under "Layout" is what later becomes real models.
"""
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path("/Users/emanuel/Documents/throw-eggs/assets/models")
RENDERS = HERE.parent.parent / "design" / "world"

TILE = 8  # studs per checker square

# Arena: the sunken field with the bases in it.
ARENA_HALF_WIDTH = 144
ARENA_FRONT_Z = 16  # the platform's arena-side edge
ARENA_BACK_Z = 176
RIM_Y = 32  # top of the walls, all round
RIM_WIDTH = 56
ISLAND_BOTTOM_Y = -60  # how far the outer dirt faces drop

# Bases: one row across the back of the arena, gates facing the platform.
BASE_WIDTH = 48
BASE_DEPTH = 48
BASE_GAP = 4
BASE_FRONT_Z = 96
BASE_COUNT = 5
GATE_WIDTH = 12
FENCE_HEIGHT = 4
FENCE_POST_SPACING = 8

# Platform and corridor.
LANE_WIDTH = 72
PLATFORM_HEIGHT = 0.5
CORRIDOR_Y = -12  # the corridor floor sits this far below the arena
CORRIDOR_RIM_WIDTH = 72
WORLD_LENGTH = 400  # Forest: distance 0 to 400 from the throw line (Config/Biomes)
NEXT_WORLD_STUB = 72  # a short piece of world 2, to show the join

# Grass hanging over the wall tops: a flat band with columns of different lengths under it.
DRIP_WIDTH = 8
DRIP_DEPTH = 1.5
DRIP_BAND = 4
DRIP_LENGTHS = (0, 4, 4, 8, 8, 12, 16)

ARENA_GRASS = ("#4cc425", "#2fae1c")
CORRIDOR_GRASS = ("#93ea5d", "#6fd84a")
RIM_GRASS = ("#a9ec3e", "#80d636")
DIRT = ("#a8653b", "#874c2d")
PLATFORM = ("#ffb13c", "#f07a22")
SAND = ("#f6e2a2", "#e7cb80")
SAND_WALL = ("#d9bd77", "#c2a262")
WOOD = "#b5793f"
DARK_WOOD = "#7d4e2a"
LEAF = ("#7fd63c", "#63bf30")


def srgb_to_linear(hex_colour):
    h = hex_colour.lstrip("#")
    out = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return out


_materials = {}


def checker(colours, tile=TILE):
    """A world-space checker, so squares line up across neighbouring blocks. It's offset half a
    square in X so a lane centred on X = 0 has one whole square down its middle."""
    key = (*colours, tile)
    if key in _materials:
        return _materials[key]
    mat = bpy.data.materials.new(f"Checker {colours[0]}")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.9
    geometry = nodes.new("ShaderNodeNewGeometry")
    tex = nodes.new("ShaderNodeTexChecker")
    tex.inputs["Color1"].default_value = (*srgb_to_linear(colours[0]), 1)
    tex.inputs["Color2"].default_value = (*srgb_to_linear(colours[1]), 1)
    tex.inputs["Scale"].default_value = 1 / tile
    offset = nodes.new("ShaderNodeVectorMath")
    offset.operation = "ADD"
    offset.inputs[1].default_value = (tile / 2 + 0.01, 0.01, 0.01)
    links.new(geometry.outputs["Position"], offset.inputs[0])
    links.new(offset.outputs["Vector"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    mat.diffuse_color = (*srgb_to_linear(colours[0]), 1)
    _materials[key] = mat
    return mat


def plain(hex_colour):
    if hex_colour in _materials:
        return _materials[hex_colour]
    mat = bpy.data.materials.new(f"Plain {hex_colour}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*srgb_to_linear(hex_colour), 1)
    bsdf.inputs["Roughness"].default_value = 0.8
    mat.diffuse_color = (*srgb_to_linear(hex_colour), 1)
    _materials[hex_colour] = mat
    return mat


def at(x, y, z):
    return (x, -z, y)


def collection(name, parent):
    col = bpy.data.collections.new(name)
    parent.children.link(col)
    return col


def box(col, name, x1, x2, y1, y2, z1, z2, material):
    """A block between two corners, in Roblox coordinates."""
    xa, xb = sorted((x1, x2))
    ya, yb = sorted((y1, y2))
    za, zb = sorted((z1, z2))
    verts = [(x, -z, y) for x in (xa, xb) for z in (zb, za) for y in (ya, yb)]
    faces = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return obj


def disc(col, name, x, z, radius, y1, y2, material, sides=20):
    """A flat round pad."""
    verts = []
    for y in (y1, y2):
        for i in range(sides):
            angle = 2 * math.pi * i / sides
            verts.append((x + math.cos(angle) * radius, -z + math.sin(angle) * radius, y))
    faces = [list(range(sides - 1, -1, -1)), list(range(sides, sides * 2))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides + j, sides + i])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return obj


def dashed_circle(col, name, x, z, radius, material, dashes=12):
    for i in range(dashes):
        angle = 2 * math.pi * i / dashes
        cx, cz = x + math.cos(angle) * radius, z + math.sin(angle) * radius
        box(col, name, cx - 0.5, cx + 0.5, 0, 0.1, cz - 0.5, cz + 0.5, material)


def drips_along_z(col, name, x, face, z_start, z_end, top_y, rng, colours=RIM_GRASS):
    """Grass hanging down a wall that runs along Z. face is the way the wall faces in X (+1 or -1)."""
    mat = checker(colours)
    z_low, z_high = sorted((z_start, z_end))
    box(col, f"{name}Band", x, x + face * DRIP_DEPTH, top_y - DRIP_BAND, top_y, z_low, z_high, mat)
    z = z_low
    while z < z_high:
        length = rng.choice(DRIP_LENGTHS)
        if length:
            end = min(z + DRIP_WIDTH, z_high)
            box(col, name, x, x + face * DRIP_DEPTH, top_y - DRIP_BAND - length, top_y - DRIP_BAND, z, end, mat)
        z += DRIP_WIDTH


def drips_along_x(col, name, z, face, x_start, x_end, top_y, rng, colours=RIM_GRASS):
    """The same, for a wall running along X. face is the way the wall faces in Z."""
    mat = checker(colours)
    box(col, f"{name}Band", x_start, x_end, top_y - DRIP_BAND, top_y, z, z + face * DRIP_DEPTH, mat)
    x = x_start
    while x < x_end:
        length = rng.choice(DRIP_LENGTHS)
        if length:
            end = min(x + DRIP_WIDTH, x_end)
            box(col, name, x, end, top_y - DRIP_BAND - length, top_y - DRIP_BAND, z, z + face * DRIP_DEPTH, mat)
        x += DRIP_WIDTH


def cliff(col, name, x1, x2, z1, z2, dirt=DIRT, grass=RIM_GRASS, bottom=ISLAND_BOTTOM_Y):
    """A dirt block from far below up to the rim, with a grass top."""
    box(col, f"{name}Dirt", x1, x2, bottom, RIM_Y - 2, z1, z2, checker(dirt))
    box(col, f"{name}Grass", x1, x2, RIM_Y - 2, RIM_Y, z1, z2, checker(grass))


def tree(col, x, y, z, height, spread, rng):
    trunk = plain(DARK_WOOD)
    leaf = checker(LEAF, 4)
    box(col, "TreeTrunk", x - 1.5, x + 1.5, y, y + height, z - 1.5, z + 1.5, trunk)
    box(col, "TreeLeaves", x - spread, x + spread, y + height - 1, y + height + spread, z - spread, z + spread, leaf)
    side = rng.choice((-1, 1))
    box(
        col,
        "TreeLeaves",
        x + side * spread * 0.6,
        x + side * spread * 1.7,
        y + height - 4,
        y + height + spread * 0.4,
        z - spread * 0.5,
        z + spread * 0.5,
        leaf,
    )


def mound(col, x, y, z, rng):
    grass = checker(CORRIDOR_GRASS, 4)
    width = rng.choice((6, 8, 10))
    depth = rng.choice((8, 10, 12))
    box(col, "Mound", x - width, x + width, y, y + 2, z - depth, z + depth, grass)
    box(col, "Mound", x - width * 0.6, x + width * 0.6, y + 2, y + 4, z - depth * 0.6, z + depth * 0.6, grass)


def stump(col, x, y, z):
    box(col, "Stump", x - 2, x + 2, y, y + 2.5, z - 2, z + 2, plain("#8d3a2a"))


def rock(col, x, y, z, rng):
    size = rng.uniform(1.5, 3)
    box(col, "Rock", x - size, x + size, y, y + size * 1.4, z - size, z + size, plain("#9a9aa2"))


def build_arena(root):
    col = collection("Arena", root)
    rng = random.Random(23)
    half = ARENA_HALF_WIDTH
    outer = half + RIM_WIDTH
    lane = LANE_WIDTH / 2

    box(col, "ArenaFloor", -half, half, -4, 0, ARENA_FRONT_Z, ARENA_BACK_Z, checker(ARENA_GRASS))

    # The ring of raised ground around the field. The front side is split by the platform.
    back = ARENA_BACK_Z + RIM_WIDTH
    cliff(col, "RimBack", -outer, outer, ARENA_BACK_Z, back)
    cliff(col, "RimWest", -outer, -half, ARENA_FRONT_Z, ARENA_BACK_Z)
    cliff(col, "RimEast", half, outer, ARENA_FRONT_Z, ARENA_BACK_Z)
    cliff(col, "RimFrontWest", -outer, -lane, ARENA_FRONT_Z - RIM_WIDTH, ARENA_FRONT_Z)
    cliff(col, "RimFrontEast", lane, outer, ARENA_FRONT_Z - RIM_WIDTH, ARENA_FRONT_Z)

    drips_along_x(col, "DripBack", ARENA_BACK_Z, -1, -half, half, RIM_Y, rng)
    drips_along_x(col, "DripFrontWest", ARENA_FRONT_Z, 1, -half, -lane, RIM_Y, rng)
    drips_along_x(col, "DripFrontEast", ARENA_FRONT_Z, 1, lane, half, RIM_Y, rng)
    drips_along_z(col, "DripWest", -half, 1, ARENA_FRONT_Z, ARENA_BACK_Z, RIM_Y, rng)
    drips_along_z(col, "DripEast", half, -1, ARENA_FRONT_Z, ARENA_BACK_Z, RIM_Y, rng)

    # Decoration markers along the rim's inner edge. The reference uses pumpkins; ours are eggs.
    marker = plain("#f4ead2")
    spot = -half + 18
    while spot < half:
        box(col, "RimEgg", spot - 2, spot + 2, RIM_Y, RIM_Y + 5, ARENA_BACK_Z + 6, ARENA_BACK_Z + 10, marker)
        if abs(spot) > lane + 6:
            box(col, "RimEgg", spot - 2, spot + 2, RIM_Y, RIM_Y + 5, ARENA_FRONT_Z - 10, ARENA_FRONT_Z - 6, marker)
        spot += 36
    spot = ARENA_FRONT_Z + 22
    while spot < ARENA_BACK_Z:
        for x in (-half - 8, half + 8):
            box(col, "RimEgg", x - 2, x + 2, RIM_Y, RIM_Y + 5, spot - 2, spot + 2, marker)
        spot += 36

    # A few small things in the strip behind the bases.
    for x, z in ((-120, 160), (-58, 166), (10, 158), (70, 166), (126, 160)):
        rock(col, x, 0, z, rng)


def build_platform(root):
    col = collection("ThrowPlatform", root)
    lane = LANE_WIDTH / 2
    # Level with the arena, on top of a dirt face that drops to the corridor floor.
    box(col, "PlatformDirt", -lane, lane, CORRIDOR_Y, 0, 0, ARENA_FRONT_Z, checker(DIRT))
    box(col, "Platform", -lane, lane, 0, PLATFORM_HEIGHT, 0, ARENA_FRONT_Z, checker(PLATFORM))
    # The white dashes run along the arena side.
    x = -lane
    while x < lane:
        box(col, "LipDash", x + 1, min(x + 5, lane), 0, PLATFORM_HEIGHT + 0.08, ARENA_FRONT_Z - 0.2, ARENA_FRONT_Z + 1, plain("#ffffff"))
        x += 7


def build_world_one(root):
    """The reusable piece: floor, two walls with their rims, and floor props."""
    col = collection("World1_Forest", root)
    rng = random.Random(7)
    lane = LANE_WIDTH / 2
    outer = lane + CORRIDOR_RIM_WIDTH
    near, far = ARENA_FRONT_Z - RIM_WIDTH, -WORLD_LENGTH

    box(col, "Floor", -lane, lane, CORRIDOR_Y - 4, CORRIDOR_Y, 0, far, checker(CORRIDOR_GRASS))
    cliff(col, "WallWest", -outer, -lane, near, far)
    cliff(col, "WallEast", lane, outer, near, far)
    drips_along_z(col, "DripWest", -lane, 1, 0, far, RIM_Y, rng)
    drips_along_z(col, "DripEast", lane, -1, 0, far, RIM_Y, rng)

    # Thin pale lines across the floor.
    line = plain("#d9d3a8")
    for z in range(-64, far, -64):
        box(col, "FloorLine", -lane, lane, CORRIDOR_Y, CORRIDOR_Y + 0.1, z - 0.5, z + 0.5, line)

    # Props stay off the middle, where eggs land.
    z = -24
    while z > far + 16:
        side = rng.choice((-1, 1))
        x = side * rng.uniform(16, 28)
        kind = rng.random()
        if kind < 0.45:
            tree(col, x, CORRIDOR_Y, z, rng.uniform(10, 18), rng.uniform(4, 6), rng)
        elif kind < 0.7:
            mound(col, x, CORRIDOR_Y, z, rng)
        elif kind < 0.85:
            stump(col, x, CORRIDOR_Y, z)
        else:
            rock(col, x, CORRIDOR_Y, z, rng)
        z -= rng.uniform(14, 30)

    # Big trees on the rim.
    z = near + 10
    while z > far + 10:
        for side in (-1, 1):
            if rng.random() < 0.6:
                tree(col, side * rng.uniform(lane + 14, outer - 12), RIM_Y, z, rng.uniform(12, 22), rng.uniform(6, 10), rng)
        z -= rng.uniform(26, 44)


def build_join(root):
    """A short piece of world 2 after the end of world 1, to show how the worlds connect."""
    col = collection("Join_World2Stub", root)
    rng = random.Random(31)
    lane = LANE_WIDTH / 2
    outer = lane + CORRIDOR_RIM_WIDTH
    start, end = -WORLD_LENGTH, -WORLD_LENGTH - NEXT_WORLD_STUB
    box(col, "Floor", -lane, lane, CORRIDOR_Y - 4, CORRIDOR_Y, start, end, checker(SAND))
    cliff(col, "WallWest", -outer, -lane, start, end, SAND_WALL, SAND)
    cliff(col, "WallEast", lane, outer, start, end, SAND_WALL, SAND)
    drips_along_z(col, "DripWest", -lane, 1, start, end, RIM_Y, rng, SAND)
    drips_along_z(col, "DripEast", lane, -1, start, end, RIM_Y, rng, SAND)


def stand_in_stall(col, x, z, stripe, name):
    """A stall facing the platform (-Z), with its pad in front."""
    wood = plain(WOOD)
    half, depth = 6, 4
    for px in (x - half, x + half - 1):
        for pz in (z - depth, z + depth - 1):
            box(col, f"{name}Post", px, px + 1, 0, 8, pz, pz + 1, wood)
    box(col, f"{name}Back", x - half, x + half, 0, 5, z + depth - 1, z + depth, wood)
    box(col, f"{name}Counter", x - half, x + half, 0, 3, z - depth, z - depth + 1.5, wood)
    for i in range(7):
        colour = plain(stripe if i % 2 == 0 else "#f4f0ea")
        left = x - half - 1 + i * 2
        box(col, f"{name}Awning", left, left + 2, 8, 9, z - depth - 1, z + depth + 1, colour)


def stand_in_rack(col, x, z, colour):
    wood = plain(colour)
    box(col, "RackPillar", x - 5, x - 3.5, 0, 9, z - 0.75, z + 0.75, wood)
    box(col, "RackPillar", x + 3.5, x + 5, 0, 9, z - 0.75, z + 0.75, wood)
    box(col, "RackBar", x - 6, x + 6, 7.5, 8, z - 0.25, z + 0.25, plain("#d9e04a"))
    dashed_circle(col, "RackDash", x, z - 2, 6.5, plain("#f3c3a0"))
    disc(col, "XpPadEdge", x, z - 11, 3, 0, 0.3, plain("#8f8f96"))
    disc(col, "XpPad", x, z - 11, 2.6, 0, 0.6, plain("#f7a71c"))


def fence(col, x1, z1, x2, z2):
    """Posts with two rails, along X or along Z."""
    wood = plain(WOOD)
    along_x = abs(x2 - x1) > abs(z2 - z1)
    length = abs(x2 - x1) if along_x else abs(z2 - z1)
    if along_x:
        box(col, "FenceRail", x1, x2, 2.6, 3.2, z1 - 0.15, z1 + 0.15, wood)
        box(col, "FenceRail", x1, x2, 1.2, 1.8, z1 - 0.15, z1 + 0.15, wood)
    else:
        box(col, "FenceRail", x1 - 0.15, x1 + 0.15, 2.6, 3.2, z1, z2, wood)
        box(col, "FenceRail", x1 - 0.15, x1 + 0.15, 1.2, 1.8, z1, z2, wood)
    count = int(length // FENCE_POST_SPACING)
    for i in range(count + 1):
        t = i / max(count, 1)
        px, pz = x1 + (x2 - x1) * t, z1 + (z2 - z1) * t
        box(col, "FencePost", px - 0.4, px + 0.4, 0, FENCE_HEIGHT, pz - 0.4, pz + 0.4, plain(DARK_WOOD))


def stand_in_dino(col, x, z, height, colour):
    """A blocky long-necked animal about this tall, to judge scale."""
    mat = plain(colour)
    leg_height = height * 0.42
    body_length = height * 0.62
    body_width = height * 0.3
    leg = height * 0.09
    for lx in (-1, 1):
        for lz in (-1, 1):
            cx, cz = x + lx * body_width * 0.45, z + lz * body_length * 0.36
            box(col, "DinoLeg", cx - leg, cx + leg, 0, leg_height, cz - leg, cz + leg, mat)
    box(col, "DinoBody", x - body_width / 2, x + body_width / 2, leg_height, height * 0.72, z - body_length / 2, z + body_length / 2, mat)
    neck = height * 0.08
    neck_z = z - body_length * 0.42
    box(col, "DinoNeck", x - neck, x + neck, height * 0.68, height * 0.94, neck_z - neck, neck_z + neck, mat)
    head = height * 0.1
    box(col, "DinoHead", x - head, x + head, height * 0.86, height, neck_z - head * 2.2, neck_z + head * 0.6, mat)


def base_centres():
    step = BASE_WIDTH + BASE_GAP
    first = -step * (BASE_COUNT - 1) / 2
    return [first + step * i for i in range(BASE_COUNT)]


def build_stand_ins(root):
    col_bases = collection("Bases", root)
    col_dinos = collection("Dinos", root)
    col_hub = collection("Shared", root)

    half_w, depth = BASE_WIDTH / 2, BASE_DEPTH
    front, back = BASE_FRONT_Z, BASE_FRONT_Z + depth
    gate = GATE_WIDTH / 2
    # The owner's base is the middle one: only it shows an egg shop, as that player would see it.
    # The rack's colour hints that racks may show progress (GAME_SPEC section 15).
    racks = {0: "#e8b52a", 1: "#3fa8d8", 2: "#c8c8c8", 3: "#c8c8c8", 4: "#c8c8c8"}
    order = [2, 3, 1, 4, 0]
    for index, centre in enumerate(base_centres()):
        ground = checker(ARENA_GRASS)
        box(col_bases, "BaseGround", centre - half_w, centre + half_w, 0, 0.3, front, back, ground)
        fence(col_bases, centre - half_w, back, centre + half_w, back)
        fence(col_bases, centre - half_w, front, centre - half_w, back)
        fence(col_bases, centre + half_w, front, centre + half_w, back)
        fence(col_bases, centre - half_w, front, centre - gate, front)
        fence(col_bases, centre + gate, front, centre + half_w, front)

        # Upgrade sign at the gate, owner's plate overhead.
        box(col_bases, "UpgradeSign", centre - gate - 5, centre - gate - 0.5, 1, 5, front - 0.6, front - 0.2, plain("#3a7fb0"))
        box(col_bases, "OwnerPlate", centre - 3, centre + 3, 44, 50, front + depth / 2 - 0.2, front + depth / 2 + 0.2, plain("#20202a"))
        box(col_bases, "OwnerPlateMoney", centre - 5, centre + 5, 41.5, 43.5, front + depth / 2 - 0.2, front + depth / 2 + 0.2, plain("#59e05a"))

        # Seen from the platform, the shop is left of the gate and the rack right of it (right is -X).
        stand_in_rack(col_bases, centre - 15, front - 8, racks[order[index]])
        if index == 2:
            stand_in_stall(col_bases, centre + 15, front - 8, "#3f8fd2", "EggShop")
            disc(col_bases, "EggShopPad", centre + 15, front - 18, 4, 0, 0.3, plain("#46d8e6"))

    # Animals far too big for their bases: that's the point. Base 1 is an empty base.
    centres = base_centres()
    herd = [
        (centres[1], 118, 30, "#7a6a5a"),
        (centres[2] - 8, 112, 66, "#8d8f78"),
        (centres[2] + 10, 126, 44, "#d9b43a"),
        (centres[2] - 2, 132, 28, "#c04a3a"),
        (centres[3], 122, 88, "#e0bd2e"),
        (centres[3] + 14, 110, 36, "#6ab0d8"),
        (centres[4], 120, 20, "#5f9d4c"),
    ]
    for x, z, height, colour in herd:
        stand_in_dino(col_dinos, x, z, height, colour)

    # SELL stall by the arena's front wall, left of the platform as you face the bases (left is +X).
    stand_in_stall(col_hub, 70, 30, "#d83a3a", "SellStall")
    dashed_circle(col_hub, "SellDash", 70, 44, 6, plain("#d83a3a"))

    # Leaderboards: the screenshots don't show where they go, so this spot is a placeholder.
    for x in (-56, -76, -96):
        box(col_hub, "LeaderboardPlaceholder", x - 8, x + 8, 0, 18, 22, 23, plain("#30405f"))

    # The throw pad and a 5.5 stud player for scale.
    disc(col_hub, "ThrowPad", 0, 8, 5, PLATFORM_HEIGHT, PLATFORM_HEIGHT + 0.2, plain("#46aadc"))
    box(col_hub, "PlayerOnPad", -1, 1, PLATFORM_HEIGHT, PLATFORM_HEIGHT + 5.5, 7, 9, plain("#2b2b33"))
    box(col_hub, "PlayerInArena", 19, 21, 0, 5.5, 66, 68, plain("#2b2b33"))


def light_scene():
    world = bpy.data.worlds.new("Sky")
    world.use_nodes = True
    # Blue only to the camera; a blue ambient light would turn the brown dirt grey.
    nodes, links = world.node_tree.nodes, world.node_tree.links
    ambient = nodes["Background"]
    ambient.inputs["Color"].default_value = (1, 1, 1, 1)
    ambient.inputs["Strength"].default_value = 0.75
    sky = nodes.new("ShaderNodeBackground")
    sky.inputs["Color"].default_value = (0.16, 0.5, 1.0, 1)
    mix = nodes.new("ShaderNodeMixShader")
    light_path = nodes.new("ShaderNodeLightPath")
    links.new(light_path.outputs["Is Camera Ray"], mix.inputs[0])
    links.new(ambient.outputs[0], mix.inputs[1])
    links.new(sky.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], nodes["World Output"].inputs["Surface"])
    bpy.context.scene.world = world
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 2.2
    sun.data.angle = math.radians(8)
    sun.rotation_euler = (math.radians(-40), math.radians(15), 0)
    bpy.context.scene.collection.objects.link(sun)


def render(scene, name, position, target, lens=24, ortho=None, size=(1600, 1000)):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.clip_end = 5000
    if ortho:
        data.type = "ORTHO"
        data.ortho_scale = ortho
    camera = bpy.data.objects.new(f"Cam_{name}", data)
    camera.location = Vector(position)
    scene.collection.objects.link(camera)
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.filepath = str(RENDERS / f"layout_{name}.png")
    bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "NONE"
    for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.eevee.taa_render_samples = 32
    scene.view_settings.view_transform = "Standard"

    layout = bpy.data.collections.new("Layout")
    scene.collection.children.link(layout)
    build_arena(layout)
    build_platform(layout)
    build_world_one(layout)
    build_join(layout)
    stand_ins = bpy.data.collections.new("Stand-ins")
    scene.collection.children.link(stand_ins)
    build_stand_ins(stand_ins)
    light_scene()

    RENDERS.mkdir(parents=True, exist_ok=True)
    for old in RENDERS.glob("layout_*.png"):
        old.unlink()
    # Each view copies a reference shot, so the two can be compared side by side.
    render(scene, "1_from_above_platform", at(0, 120, -28), at(0, 0, 120), lens=22)  # arena-top-view-bases-circled
    render(scene, "2_from_over_corridor", at(0, 95, -70), at(0, 0, 90), lens=22)  # arena-from-corridor-side
    render(scene, "3_at_my_base", at(2, 10, 50), at(0, 10, 100), lens=22)  # shop-rack-sign-circled
    render(scene, "4_running_to_platform", at(0, 9, 46), at(0, 3, -60), lens=20)  # video: player running to the platform
    render(scene, "5_aiming", at(-3, 8, 17), at(3, 8, -60), lens=20)  # video: aiming with the meter
    render(scene, "6_map_top", at(0, 1000, -130), at(0, 0, -130.001), lens=35, ortho=720, size=(1100, 1500))

    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "world_layout.blend"))
    print("saved", HERE / "world_layout.blend", "objects:", len(bpy.data.objects))


main()
