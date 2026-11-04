"""Builds the reusable corridor pieces and renders them joined up (run with Blender in background mode).

    Blender -b -P build_world_kit.py

Saves world_kit.blend and assets/textures/checker_studs.png, and renders to design/world/models/.

Every world is these same pieces with different colours: each piece has one mesh per colour role,
and the grey checker image tints to any colour. Pieces are one section long and sit end to end along
+Y (Roblox -Z). Sizes match build_world_layout.py. 1 Blender unit = 1 stud.
"""
import math
import random
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path("/Users/emanuel/Documents/throw-eggs/assets/models")
TEXTURES = HERE.parent / "textures"
RENDERS = HERE.parent.parent / "design" / "world" / "models"

SECTION = 64  # a whole number of checker repeats, so sections line up
LANE_WIDTH = 88  # the corridor and platform; widened from 72 at the owner's request (2026-11-04). 11 checker squares
WALL_HEIGHT = 44  # corridor floor to rim
RIM_WIDTH = 72
PLATFORM_DEPTH = 16
TILE_SQUARES = 2  # the image holds 2 x 2 checker squares
SQUARE = 8  # studs per checker square
STUDS_PER_SQUARE = 4
DRIP_WIDTH = 8
DRIP_DEPTH = 1.5
DRIP_LENGTHS = (0, 4, 4, 8, 8, 12, 16)
WALL_BOTTOM = -48  # the island's outer dirt faces drop this far below the corridor floor

# The sunken arena the bases stand in (GAME_SPEC section 3, build_world_layout.py). In these pieces'
# coordinates, like the corridor's, the corridor floor is z = 0 and the throw line is y = 0, so the
# arena floor is 12 up and the arena lies towards -y (Roblox +Z).
ARENA_HALF_WIDTH = 144
ARENA_FRONT = 16  # the platform's arena-side edge
ARENA_BACK = 176
ARENA_FLOOR = 12
ARENA_RIM_WIDTH = 56
CORRIDOR_WALL_START = 40  # the arena's front walls end here and the corridor's walls carry on

FERN_VALLEY = {
    "Floor": "#8fe85a",
    "Dirt": "#ad6a3e",
    "Grass": "#a4ea3e",
    "Platform": "#ffa030",
    "Dash": "#ffffff",
    "ArenaFloor": "#4cc425",
}


def srgb_to_linear(hex_colour):
    h = hex_colour.lstrip("#")
    out = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return out


def checker_image():
    """One grey tile of two-tone checker with studs on it. Tinting it gives any world's colours."""
    size = 512
    image = bpy.data.images.new("checker_studs", size, size)
    stud = size / (TILE_SQUARES * STUDS_PER_SQUARE)
    pixels = []
    for py in range(size):
        for px in range(size):
            dark = (px // (size // 2) + py // (size // 2)) % 2 == 1
            value = 0.8 if dark else 1.0
            dx, dy = (px % stud) / stud - 0.5, (py % stud) / stud - 0.5
            dist = math.hypot(dx, dy)
            if dist < 0.33:
                value *= 1.05
                if dist > 0.26:
                    value *= 0.84 if dx - dy > 0 else 1.1
            if max(abs(dx), abs(dy)) > 0.48:
                value *= 0.94
            value = min(value, 1.0)
            pixels.extend((value, value, value, 1))
    image.pixels = pixels
    TEXTURES.mkdir(parents=True, exist_ok=True)
    image.filepath_raw = str(TEXTURES / "checker_studs.png")
    image.file_format = "PNG"
    image.save()
    return image


class Piece:
    def __init__(self, name):
        self.name = name
        self.parts = {}

    def box(self, role, x1, x2, y1, y2, z1, z2):
        verts, faces = self.parts.setdefault(role, ([], []))
        start = len(verts)
        verts.extend((x, y, z) for x in (x1, x2) for y in (y1, y2) for z in (z1, z2))
        for face in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
            faces.append([start + i for i in face])

    def build(self, collection, colours, image, offset):
        root = bpy.data.objects.new(self.name, None)
        collection.objects.link(root)
        root.location = offset
        for role, (verts, faces) in self.parts.items():
            mesh = bpy.data.meshes.new(f"{self.name}_{role}")
            mesh.from_pydata(verts, [], faces)
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(mesh)
            bm.free()
            mesh.update()
            lay_out_uvs(mesh, offset)
            mesh.materials.append(material(role, colours[role], image))
            obj = bpy.data.objects.new(f"{self.name}_{role}", mesh)
            collection.objects.link(obj)
            obj.parent = root
        return root


def lay_out_uvs(mesh, offset):
    """Box projection in map space, half a square off in X so the lane has one square down its middle."""
    layer = mesh.uv_layers.new(name="UVMap")
    repeat = TILE_SQUARES * SQUARE
    for poly in mesh.polygons:
        axis = max(range(3), key=lambda i: abs(poly.normal[i]))
        u_axis, v_axis = [(1, 2), (0, 2), (0, 1)][axis]
        for loop_index in poly.loop_indices:
            co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            shifted = (co[0] + SQUARE / 2, co[1], co[2])
            layer.data[loop_index].uv = (shifted[u_axis] / repeat, shifted[v_axis] / repeat)


_materials = {}


def material(role, hex_colour, image):
    if role in _materials:
        return _materials[role]
    mat = bpy.data.materials.new(f"Kit_{role}")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.85
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 1
    multiply.inputs[1].default_value = (*srgb_to_linear(hex_colour), 1)
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    links.new(tex.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs[0], bsdf.inputs["Base Color"])
    _materials[role] = mat
    return mat


def floor():
    p = Piece("kit_Floor")
    half = LANE_WIDTH / 2
    p.box("Floor", -half, half, 0, SECTION, -4, 0)
    return p


def wall(side, seed):
    """One side of the corridor: dirt face, rim on top and grass hanging over the edge."""
    p = Piece("kit_WallWest" if side < 0 else "kit_WallEast")
    rng = random.Random(seed)
    half = LANE_WIDTH / 2
    inner, outer = side * half, side * (half + RIM_WIDTH)
    p.box("Dirt", inner, outer, 0, SECTION, WALL_BOTTOM, WALL_HEIGHT - 2)
    p.box("Grass", inner, outer, 0, SECTION, WALL_HEIGHT - 2, WALL_HEIGHT)
    face = inner - side * DRIP_DEPTH
    p.box("Grass", inner, face, 0, SECTION, WALL_HEIGHT - 4, WALL_HEIGHT)
    for y in range(0, SECTION, DRIP_WIDTH):
        length = rng.choice(DRIP_LENGTHS)
        if length:
            p.box("Grass", inner, face, y, y + DRIP_WIDTH, WALL_HEIGHT - 4 - length, WALL_HEIGHT - 4)
    return p


def drips(p, rng, along, start, end, face_at, depth):
    """Grass hanging over a wall's inner face: a band along the top with columns of random length.

    along is "x" or "y", the axis the face runs along, from start to end. face_at is the face's
    position on the other axis and depth is signed: where the grass sticks out to.
    """
    a, b = sorted((face_at, face_at + depth))
    lo, hi = sorted((start, end))

    def box(u1, u2, z1, z2):
        if along == "x":
            p.box("Grass", u1, u2, a, b, z1, z2)
        else:
            p.box("Grass", a, b, u1, u2, z1, z2)

    box(lo, hi, WALL_HEIGHT - 4, WALL_HEIGHT)
    u = lo
    while u < hi:
        length = rng.choice(DRIP_LENGTHS)
        if length:
            box(u, min(u + DRIP_WIDTH, hi), WALL_HEIGHT - 4 - length, WALL_HEIGHT - 4)
        u += DRIP_WIDTH


def block(p, x1, x2, y1, y2):
    """Dirt from the island's bottom up to the rim, with the rim's grass on top."""
    p.box("Dirt", x1, x2, y1, y2, WALL_BOTTOM, WALL_HEIGHT - 2)
    p.box("Grass", x1, x2, y1, y2, WALL_HEIGHT - 2, WALL_HEIGHT)


def arena_floor():
    p = Piece("kit_ArenaFloor")
    p.box("ArenaFloor", -ARENA_HALF_WIDTH, ARENA_HALF_WIDTH, -ARENA_BACK, -ARENA_FRONT, 0, ARENA_FLOOR)
    return p


def arena_back_wall():
    """Behind the bases, wide enough to cover both back corners."""
    p = Piece("kit_ArenaWallBack")
    rng = random.Random(41)
    outer = ARENA_HALF_WIDTH + ARENA_RIM_WIDTH
    block(p, -outer, outer, -ARENA_BACK - ARENA_RIM_WIDTH, -ARENA_BACK)
    drips(p, rng, "x", -ARENA_HALF_WIDTH, ARENA_HALF_WIDTH, -ARENA_BACK, DRIP_DEPTH)
    return p


def arena_side_wall(side):
    """Left or right of the arena, between the front and back walls."""
    p = Piece("kit_ArenaWallWest" if side < 0 else "kit_ArenaWallEast")
    rng = random.Random(42 + side)
    inner = side * ARENA_HALF_WIDTH
    block(p, inner, inner + side * ARENA_RIM_WIDTH, -ARENA_BACK, -ARENA_FRONT)
    # Stops short of the corners, where the front and back walls' grass already hangs.
    drips(p, rng, "y", -ARENA_BACK + DRIP_DEPTH, -ARENA_FRONT - DRIP_DEPTH, inner, -side * DRIP_DEPTH)
    return p


def arena_front_wall(side):
    """Beside the platform, covering a front corner. Its end faces the corridor, so grass hangs there too."""
    p = Piece("kit_ArenaFrontWest" if side < 0 else "kit_ArenaFrontEast")
    rng = random.Random(45 + side)
    inner = side * LANE_WIDTH / 2
    outer = side * (ARENA_HALF_WIDTH + ARENA_RIM_WIDTH)
    block(p, inner, outer, -ARENA_FRONT, CORRIDOR_WALL_START)
    drips(p, rng, "x", inner, side * ARENA_HALF_WIDTH, -ARENA_FRONT, -DRIP_DEPTH)
    drips(p, rng, "y", -ARENA_FRONT, CORRIDOR_WALL_START, inner, -side * DRIP_DEPTH)
    return p


def arena_pieces():
    return [arena_floor(), arena_back_wall(), arena_side_wall(-1), arena_side_wall(1), arena_front_wall(-1), arena_front_wall(1)]


def platform():
    """Sits at the arena end, above the corridor floor, with the dashes on the arena side."""
    p = Piece("kit_Platform")
    half = LANE_WIDTH / 2
    top = 12
    p.box("Dirt", -half, half, -PLATFORM_DEPTH, 0, 0, top)
    p.box("Platform", -half, half, -PLATFORM_DEPTH, 0, top, top + 0.5)
    x = -half
    while x < half:
        p.box("Dash", x + 1, min(x + 5, half), -PLATFORM_DEPTH - 0.8, -PLATFORM_DEPTH + 0.2, top, top + 0.58)
        x += 7
    return p


def shoot(scene, name, position, target, lens=22):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.clip_end = 3000
    camera = bpy.data.objects.new(name, data)
    camera.location = Vector(position)
    scene.collection.objects.link(camera)
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = 1500, 900
    scene.render.filepath = str(RENDERS / f"{name}.png")
    bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "NONE"
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 32
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("Sky")
    world.use_nodes = True
    nodes, links = world.node_tree.nodes, world.node_tree.links
    ambient = nodes["Background"]
    ambient.inputs["Color"].default_value = (1, 1, 1, 1)
    ambient.inputs["Strength"].default_value = 0.8
    sky = nodes.new("ShaderNodeBackground")
    sky.inputs["Color"].default_value = (0.16, 0.5, 1.0, 1)
    mix = nodes.new("ShaderNodeMixShader")
    path = nodes.new("ShaderNodeLightPath")
    links.new(path.outputs["Is Camera Ray"], mix.inputs[0])
    links.new(ambient.outputs[0], mix.inputs[1])
    links.new(sky.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], nodes["World Output"].inputs["Surface"])
    scene.world = world
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 2.0
    sun.rotation_euler = (math.radians(-40), math.radians(25), 0)
    scene.collection.objects.link(sun)

    image = checker_image()
    kit = bpy.data.collections.new("Kit")
    scene.collection.children.link(kit)
    joined = bpy.data.collections.new("Preview: pieces joined")
    scene.collection.children.link(joined)

    # The originals sit at the origin, ready to export.
    for piece in (floor(), wall(-1, 1), wall(1, 2), platform()):
        piece.build(kit, FERN_VALLEY, image, (0, 0, 0))
    kit.hide_render = True
    bpy.context.view_layer.layer_collection.children["Kit"].exclude = True
    bpy.context.view_layer.layer_collection.children["Kit"].exclude = False
    for obj in kit.objects:
        obj.hide_render = True

    # The arena is one of a kind, so its pieces are built where they stand and exported from there.
    # They go under one root, kit_Arena, so Studio imports them as one model.
    arena = bpy.data.collections.new("Arena")
    scene.collection.children.link(arena)
    arena_root = bpy.data.objects.new("kit_Arena", None)
    arena.objects.link(arena_root)
    for piece in arena_pieces():
        piece.build(arena, FERN_VALLEY, image, (0, 0, 0)).parent = arena_root

    # Eight sections end to end show the seams, which should not be visible. The walls start where
    # the arena's front walls end, as in the game (Config/Map corridor.wallStartZ).
    for i in range(8):
        floor().build(joined, FERN_VALLEY, image, (0, i * SECTION, 0))
        wall(-1, 1).build(joined, FERN_VALLEY, image, (0, CORRIDOR_WALL_START + i * SECTION, 0))
        wall(1, 2).build(joined, FERN_VALLEY, image, (0, CORRIDOR_WALL_START + i * SECTION, 0))
    platform().build(joined, FERN_VALLEY, image, (0, 0, 0))

    RENDERS.mkdir(parents=True, exist_ok=True)
    shoot(scene, "kit_corridor", (0, -30, 20), (0, 200, 14))
    shoot(scene, "kit_from_above", (0, -95, 105), (0, 70, 0))
    shoot(scene, "arena_from_corridor", (0, 150, 150), (0, -90, 0), lens=18)
    shoot(scene, "arena_from_back", (0, -330, 170), (0, -20, 0), lens=18)

    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "world_kit.blend"))
    print("saved", HERE / "world_kit.blend")


main()
