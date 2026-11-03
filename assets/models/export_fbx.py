"""Exports the Blender models to assets/models/fbx/<map>/<kind>/ for Roblox Studio's 3D importer.

    Blender -b fern_valley_models.blend -P export_fbx.py
    Blender -b world_kit.blend -P export_fbx.py

One FBX per model: its Empty or armature and the meshes under it, in the rest pose, without
animation (the game moves the bones itself). Models face Roblox -Z.
"""
from pathlib import Path

import bpy

OUT = Path(bpy.data.filepath).parent / "fbx"
# One folder per map, in throw order (GAME_SPEC section 8a), so the owner imports map by map.
MAPS = ("01_FernValley", "02_DryPlains", "03_Swamp", "04_VolcanoFoothills", "05_IceAgeTundra", "06_TarPits", "07_DeepSeaTrench", "08_MeteorCrater")
# Which map each .blend belongs to. A new map's .blend gets a line here.
MAP_OF_FILE = {"fern_valley_models": "01_FernValley", "world_kit": "01_FernValley", "dry_plains_models": "02_DryPlains"}
# Blender collection -> folder inside the map's folder.
EXPORT_COLLECTIONS = {"Animals": "Animals", "Props": "Props", "Kit": "Corridor"}


def main():
    for map_name in MAPS:
        for kind in EXPORT_COLLECTIONS.values():
            (OUT / map_name / kind).mkdir(parents=True, exist_ok=True)
    map_name = MAP_OF_FILE[Path(bpy.data.filepath).stem]
    for collection_name, kind in EXPORT_COLLECTIONS.items():
        collection = bpy.data.collections.get(collection_name)
        if not collection:
            continue
        for root in [obj for obj in collection.objects if obj.parent is None]:
            if root.type == "ARMATURE":
                root.animation_data_clear()
                for bone in root.pose.bones:
                    bone.location = (0, 0, 0)
                    bone.rotation_euler = (0, 0, 0)
            location = root.location.copy()
            root.location = (0, 0, 0)
            for child in root.children:
                child.hide_render = False
            bpy.context.view_layer.update()
            bpy.ops.object.select_all(action="DESELECT")
            root.select_set(True)
            for child in root.children:
                child.select_set(True)
            bpy.ops.export_scene.fbx(
                filepath=str(OUT / map_name / kind / f"{root.name}.fbx"),
                use_selection=True,
                object_types={"EMPTY", "ARMATURE", "MESH"},
                global_scale=0.01,  # Studio reads 1 FBX unit as 1 stud only at this scale; it came in 100x too big
                axis_forward="Z",  # Studio ignored this: models still import facing +Z, so the game code turns them
                axis_up="Y",
                add_leaf_bones=False,
                bake_anim=False,
                mesh_smooth_type="FACE",
            )
            root.location = location
            print("exported", root.name)


main()
