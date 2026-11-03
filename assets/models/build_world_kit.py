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
LANE_WIDTH = 72
WALL_HEIGHT = 44  # corridor floor to rim
RIM_WIDTH = 72
PLATFORM_DEPTH = 16
TILE_SQUARES = 2  # the image holds 2 x 2 checker squares
SQUARE = 8  # studs per checker square
STUDS_PER_SQUARE = 4
DRIP_WIDTH = 8
DRIP_DEPTH = 1.5
DRIP_LENGTHS = (0, 4, 4, 8, 8, 12, 16)

FERN_VALLEY = {
    "Floor": "#8fe85a",
    "Dirt": "#ad6a3e",
    "Grass": "#a4ea3e",
    "Platform": "#ffa030",
    "Dash": "#ffffff",
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
    p.box("Dirt", inner, outer, 0, SECTION, -48, WALL_HEIGHT - 2)
    p.box("Grass", inner, outer, 0, SECTION, WALL_HEIGHT - 2, WALL_HEIGHT)
    face = inner - side * DRIP_DEPTH
    p.box("Grass", inner, face, 0, SECTION, WALL_HEIGHT - 4, WALL_HEIGHT)
    for y in range(0, SECTION, DRIP_WIDTH):
        length = rng.choice(DRIP_LENGTHS)
        if length:
            p.box("Grass", inner, face, y, y + DRIP_WIDTH, WALL_HEIGHT - 4 - length, WALL_HEIGHT - 4)
    return p


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

    # Eight sections end to end show the seams, which should not be visible.
    for i in range(8):
        offset = (0, i * SECTION, 0)
        floor().build(joined, FERN_VALLEY, image, offset)
        wall(-1, 10 + i).build(joined, FERN_VALLEY, image, offset)
        wall(1, 30 + i).build(joined, FERN_VALLEY, image, offset)
    platform().build(joined, FERN_VALLEY, image, (0, 0, 0))

    RENDERS.mkdir(parents=True, exist_ok=True)
    shoot(scene, "kit_corridor", (0, -30, 20), (0, 200, 14))
    shoot(scene, "kit_from_above", (0, -95, 105), (0, 70, 0))

    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "world_kit.blend"))
    print("saved", HERE / "world_kit.blend")


main()
