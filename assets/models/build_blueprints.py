"""Builds every blueprint in blueprints.json as a Blender mesh (run inside Blender).

Each model becomes one object: only the outside faces of its blocks, flat same-coloured areas
merged, a small bevel, one plain material per colour (no studs; those are applied in Roblox
Studio). Origins sit at the bottom centre. Models are laid out in a grid per collection.
"""
import json
from pathlib import Path

import bmesh
import bpy

HERE = Path("/Users/emanuel/Documents/throw-eggs/assets/models")
VOXEL = 0.25  # metres per block
GROUPS = {"dino_": "Dinos", "egg_": "Eggs", "biome_": "Biomes"}

FACES = [
    ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
    ((0, 0, -1), [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]),
    ((1, 0, 0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
    ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
    ((0, 1, 0), [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),
    ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
]


def srgb_to_linear(hex_colour):
    h = hex_colour.lstrip("#")
    out = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return out


_materials = {}


def material(hex_colour):
    if hex_colour in _materials:
        return _materials[hex_colour]
    name = f"Block {hex_colour}"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    rgb = srgb_to_linear(hex_colour)
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = 0.5
    mat.diffuse_color = (*rgb, 1)
    _materials[hex_colour] = mat
    return mat


def collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def build(name, blocks):
    cells = {(x, y, z): c for x, y, z, c in blocks}
    colours = sorted(set(cells.values()))
    index_of = {c: i for i, c in enumerate(colours)}
    min_x = min(k[0] for k in cells); max_x = max(k[0] for k in cells) + 1
    min_y = min(k[1] for k in cells); max_y = max(k[1] for k in cells) + 1
    min_z = min(k[2] for k in cells)
    cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2

    verts, vert_index, faces, face_mats = [], {}, [], []
    for (x, y, z), colour in cells.items():
        for (nx, ny, nz), corners in FACES:
            if (x + nx, y + ny, z + nz) in cells:
                continue
            face = []
            for dx, dy, dz in corners:
                key = (x + dx, y + dy, z + dz)
                if key not in vert_index:
                    vert_index[key] = len(verts)
                    verts.append(((key[0] - cx) * VOXEL, (key[1] - cy) * VOXEL, (key[2] - min_z) * VOXEL))
                face.append(vert_index[key])
            faces.append(face)
            face_mats.append(index_of[colour])

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    for colour in colours:
        mesh.materials.append(material(colour))
    for poly, mat_index in zip(mesh.polygons, face_mats):
        poly.material_index = mat_index

    # Merge flat runs of same-coloured faces so the mesh stays light and bevels only real edges.
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.dissolve_limit(bm, angle_limit=0.01, verts=bm.verts, edges=bm.edges, delimit={"MATERIAL"})
    bm.to_mesh(mesh)
    bm.free()

    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    obj = bpy.data.objects.new(name, mesh)
    group = next((g for prefix, g in GROUPS.items() if name.startswith(prefix)), "Shop")
    collection(group).objects.link(obj)
    bevel = obj.modifiers.new("Bevel", "BEVEL")
    bevel.width = VOXEL * 0.08
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    return obj, group, len(faces), len(mesh.polygons)


def main():
    for leftover in ("Cube",):
        obj = bpy.data.objects.get(leftover)
        if obj and obj.type == "MESH" and not obj.data.materials or (obj and obj.name == "Cube"):
            bpy.data.objects.remove(obj, do_unlink=True)
    data = json.loads((HERE / "blueprints.json").read_text())
    stats = {}
    slots = {}
    for name, blocks in data.items():
        obj, group, quads, polys = build(name, blocks)
        row = list(GROUPS.values()).index(group) if group in GROUPS.values() else 3
        slots[group] = slots.get(group, -1) + 1
        obj.location = (slots[group] * 10, row * 12, 0)
        stats[name] = polys
    return stats


result = main()
