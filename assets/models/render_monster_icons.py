# Renders every monster (dino_* armature) in a monsters .blend as a see-through 512 px PNG icon, front three-quarter
# view, for UI mock-ups in Figma (Throw Eggs - Index & Inventory used them). The game itself shows the real models
# live (UiKit.monster), so nothing here goes into Studio. Run in the background, once per .blend:
#   /Applications/Blender.app/Contents/MacOS/Blender -b assets/models/eclipse_temple_monsters.blend \
#     --python assets/models/render_monster_icons.py -- OUT_DIR
import math
import sys

import bpy
from mathutils import Vector

out_dir = sys.argv[sys.argv.index("--") + 1]
scene = bpy.context.scene
scene.render.film_transparent = True
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
try:
    scene.view_settings.view_transform = "Standard"
except Exception:
    pass

world = scene.world or bpy.data.worlds.new("IconWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (1, 1, 1, 1)
    bg.inputs[1].default_value = 1.6

roots = [o for o in bpy.data.objects if o.parent is None and o.name.startswith("dino_") and o.type == "ARMATURE"]


def family(root):
    return [root] + list(root.children_recursive)


for o in bpy.data.objects:
    if o.parent is None and not o.name.startswith("dino_") and o.type not in ("LIGHT",):
        for x in family(o):
            x.hide_render = True

sun = next((o for o in bpy.data.objects if o.type == "LIGHT"), None)
if sun is None:
    data = bpy.data.lights.new("IconSun", "SUN")
    sun = bpy.data.objects.new("IconSun", data)
    scene.collection.objects.link(sun)
sun.data.energy = 4.5
sun.hide_render = False

cam_data = bpy.data.cameras.new("IconCam")
cam_data.lens_unit = "FOV"
cam_data.angle = math.radians(26)
cam = bpy.data.objects.new("IconCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

for root in roots:
    for other in roots:
        for x in family(other):
            x.hide_render = other is not root
    depsgraph = bpy.context.evaluated_depsgraph_get()
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for x in family(root):
        if x.type == "MESH":
            ev = x.evaluated_get(depsgraph)
            for corner in ev.bound_box:
                p = ev.matrix_world @ Vector(corner)
                lo = Vector(map(min, lo, p))
                hi = Vector(map(max, hi, p))
    centre = (lo + hi) / 2
    size = hi - lo
    # Which way it faces: from its tail (or spine) to its head (or jaw).
    bones = {b.name: root.matrix_world @ b.head_local for b in root.data.bones}
    front = bones.get("Jaw") or bones.get("Head")
    back = bones.get("Tail1") or bones.get("Spine") or bones.get("Swim")
    ahead = Vector((0, -1, 0))
    if front is not None and back is not None:
        d = front - back
        d.z = 0
        if d.length > 1e-3:
            ahead = d.normalized()
    side = Vector((ahead.y, -ahead.x, 0))  # its right
    yaw = math.radians(40)
    pitch = math.radians(16)
    flat = ahead * math.cos(yaw) + side * math.sin(yaw)
    direction = flat * math.cos(pitch) + Vector((0, 0, math.sin(pitch)))
    radius = size.length / 2
    distance = radius * 0.86 / math.tan(math.radians(13))
    cam.location = centre + direction * distance
    cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    sun.rotation_euler = (-(direction + Vector((0.4, 0.2, 0.9)))).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = f"{out_dir}/{root.name}.png"
    bpy.ops.render.render(write_still=True)
    print("ICON", root.name)
