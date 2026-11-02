"""Renders every model built by build_blueprints.py to a transparent PNG (run inside Blender).

Orthographic 3/4 camera (top, front and the +y flank showing), soft key/fill/rim suns and the
Standard view transform so the colours stay as bright as the blueprints. Each model is framed
on its own; images land in RAW_DIR at twice their final size for post-processing.
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

BLEND = "/Users/emanuel/Documents/throw-eggs/assets/models/dino_blueprints.blend"
RAW_DIR = Path("/private/tmp/claude-501/-Users-emanuel-Documents-throw-eggs/9a6fdfb2-81f7-48b8-81da-0a32044a09ae/scratchpad/blender/raw")
YAW, PITCH = math.radians(34), math.radians(24)
MARGIN = 0.06
SIZES = {"dino_": (360, 300), "egg_": (260, 300), "biome_": (320, 340), "cash_": (240, 200), "bolts_": (240, 200), "clover": (220, 220), "gift": (200, 200)}


def size_for(name):
    return next(v for k, v in SIZES.items() if name.startswith(k))


def setup(scene):
    for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = 48
    except AttributeError:
        pass

    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.85, 0.9, 1.0, 1)
    bg.inputs["Strength"].default_value = 0.45

    old = bpy.data.objects.get("Light")
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    for name, direction, strength in (("Key", (0.35, 1.0, 1.5), 4.2), ("Fill", (1.0, -0.4, 0.5), 0.8), ("Rim", (-1.0, -0.8, 0.7), 1.8)):
        light = bpy.data.objects.get(name)
        if not light:
            light = bpy.data.objects.new(name, bpy.data.lights.new(name, "SUN"))
            scene.collection.objects.link(light)
        light.data.energy = strength
        light.data.angle = math.radians(12)
        light.rotation_euler = (-Vector(direction)).normalized().to_track_quat("-Z", "Y").to_euler()

    cam = bpy.data.objects.get("Camera")
    cam.data.type = "ORTHO"
    scene.camera = cam
    return cam


def frame(cam, obj, width, height):
    view = Vector((math.sin(YAW) * math.cos(PITCH), math.cos(YAW) * math.cos(PITCH), math.sin(PITCH)))
    forward = -view
    right = forward.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(forward).normalized()
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [c.dot(right) for c in corners]
    ys = [c.dot(up) for c in corners]
    depth = max(c.dot(view) for c in corners)
    mid_x, mid_y = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    # ortho_scale is the longer side of the view, so fit both sides into it.
    aspect = width / height
    fit = max(w, h * aspect) if aspect >= 1 else max(h, w / aspect)
    cam.data.ortho_scale = fit * (1 + 2 * MARGIN)
    cam.location = right * mid_x + up * mid_y + view * (depth + 40)
    cam.rotation_euler = forward.to_track_quat("-Z", "Y").to_euler()
    cam.data.clip_end = 200


def main():
    scene = bpy.context.scene
    cam = setup(scene)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    models = [o for o in scene.objects if o.type == "MESH" and any(o.name.startswith(k) for k in SIZES)]
    done = []
    for obj in models:
        for other in models:
            other.hide_render = other is not obj
        width, height = size_for(obj.name)
        scene.render.resolution_x, scene.render.resolution_y = width * 2, height * 2
        frame(cam, obj, width * 2, height * 2)
        scene.render.filepath = str(RAW_DIR / f"{obj.name}.png")
        bpy.ops.render.render(write_still=True)
        done.append(obj.name)
    for other in models:
        other.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print(len(done), "rendered;", "saved", BLEND)


main()
