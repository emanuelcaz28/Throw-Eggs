"""Builds a map's monsters in Blender, animates them and renders them: one routine for every map from the
Swamp on (the first maps and the Volcano have their own, in their build scripts).

Renders, per monster: whole, face, straight on and mid-roar; a lineup, the lineup in Gold, and an animation
preview video (each walk twice, then the idle through its roar; a map can pass its own moves). The walk and idle are the Volcano's
(build_volcano.py): every map's moves plus the jaw snap and the roar, as DinoLifeController plays them.
"""
import math
import subprocess

import bpy
from mathutils import Vector

import build_forest as kit
from build_forest import Model
from build_volcano import ROAR_FRAME, animate


def light_up(roots, glow_roles, strength=2.4):
    for root in roots:
        for child in root.children:
            if child.type == "MESH" and child.name.rsplit("_", 1)[-1] in glow_roles:
                for mat in child.data.materials:
                    nodes = mat.node_tree.nodes
                    bsdf = nodes.get("Principled BSDF")
                    bsdf.inputs["Emission Color"].default_value = nodes["Colour"].outputs[0].default_value
                    bsdf.inputs["Emission Strength"].default_value = strength


def set_sky(scene, hex_colour):
    sky = [n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND" and n.name != "Background"][0]
    sky.inputs["Color"].default_value = (*kit.srgb_to_linear(hex_colour), 1)


def build_and_render(models, renders, blend_path, video_name, sky="#8fd0ff", ground="#6ccf4a", glow_roles=(), spacing=18,
                     animate_fn=animate, walk_frames=None):
    """animate_fn(armature) makes the (walk, idle) actions, the Volcano's by default; walk_frames is one walk
    cycle's length (the swimmers' tail beat is longer than a stride)."""
    walk_frames = walk_frames or kit.WALK_FRAMES
    scene = kit.setup_scene()
    kit.RENDERS = renders
    renders.mkdir(parents=True, exist_ok=True)
    kit.NO_STUDS.update(glow_roles)
    animals = bpy.data.collections.new("Animals")
    stage = bpy.data.collections.new("Preview stage")
    for col in (animals, stage):
        scene.collection.children.link(col)

    roots = []
    for i, model in enumerate(models):
        root = model.build(animals)
        root.location = (i * spacing, 0, 0)
        roots.append(root)
    light_up(roots, glow_roles)
    middle = (len(models) - 1) * spacing / 2

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-300, -300, -0.01), (400, -300, -0.01), (400, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", ground, False))
    stage.objects.link(bpy.data.objects.new("Ground", ground_mesh))
    player = Model("Player", {"Skin": "#3f4553"})
    player.bone = "Root"
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    player_root = player.build(stage)
    player_root.location = (-9, 0, 0)
    bpy.context.view_layer.update()
    set_sky(scene, sky)
    everything = roots + [player_root]

    for model, root in zip(models, roots):
        kit.set_visible(everything, [root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 3)
        kit.shoot(scene, f"{model.name}_full", centre + Vector((0.62, 0.85, 0.32)) * reach * 1.15, centre, (800, 800), 50)
        head = root.location + Vector(model.head_centre)
        size = max(3.2, model.head_centre[2] * 0.75)
        kit.shoot(scene, f"{model.name}_face", head + Vector((0.55, 1.0, 0.14)) * size * 1.5, head, (700, 700), 50)
        kit.shoot(scene, f"{model.name}_front", head + Vector((0, 1, 0.1)) * size * 1.6, head, (700, 700), 50)
    kit.set_visible(everything, roots + [player_root])
    lineup = ((middle, 84, 20), (middle, 0, 4.5), (1800, 700), 26)
    kit.shoot(scene, "lineup", *lineup)
    saved = kit.tint_mutation(models, "#ffc628")
    kit.shoot(scene, "lineup_Gold", *lineup)
    for node, value in saved:
        node.outputs[0].default_value = value

    actions = [animate_fn(root) for root in roots]
    for root, pair in zip(roots, actions):
        root.animation_data.action = pair[1]
    scene.frame_set(ROAR_FRAME)
    for model, root in zip(models, roots):
        kit.set_visible(everything, [root])
        head = root.location + Vector(model.head_centre)
        size = max(3.2, model.head_centre[2] * 0.75)
        kit.shoot(scene, f"{model.name}_roar", head + Vector((0.55, 1.0, 0.3)) * size * 1.7, head + Vector((0, 0.3, 0.6)), (700, 700), 50)

    kit.set_visible(everything, roots)
    frames = renders / "anim_frames"
    frames.mkdir(exist_ok=True)
    for root in roots:
        root.rotation_euler = (0, 0, math.radians(-55))
    data = bpy.data.cameras.new("Preview")
    data.lens = 26
    camera = bpy.data.objects.new("Cam_Preview", data)
    camera.location = (middle + 1, 80, 16)
    scene.collection.objects.link(camera)
    camera.rotation_euler = (Vector((middle, 0, 5)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = 1800, 640
    shots = [(0, f % walk_frames) for f in range(0, walk_frames * 2, 2)]
    shots += [(1, f) for f in range(ROAR_FRAME - 50, ROAR_FRAME + 50, 2)]
    for number, (which, frame) in enumerate(shots):
        for root, pair in zip(roots, actions):
            root.animation_data.action = pair[which]
        scene.frame_set(frame)
        scene.render.filepath = str(frames / f"f{number:04d}.png")
        bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "15", "-i", str(frames / "f%04d.png"),
                    "-pix_fmt", "yuv420p", "-vf", "scale=1800:-2", str(renders / video_name)], check=True)
    for frame in frames.glob("*.png"):
        frame.unlink()
    frames.rmdir()

    for root in roots:
        root.rotation_euler = (0, 0, 0)
        root.animation_data.action = None
        for bone in root.pose.bones:
            bone.location = (0, 0, 0)
            bone.rotation_euler = (0, 0, 0)
    scene.frame_set(0)
    light_up(roots, glow_roles, 0)
    kit.set_visible(everything, everything)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print("saved", blend_path)
    for model in models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")
