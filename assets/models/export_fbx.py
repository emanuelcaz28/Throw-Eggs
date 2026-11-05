"""Exports the Blender models to assets/models/fbx/<map>/<kind>/ for Roblox Studio's 3D importer.

    Blender -b forest_models.blend -P export_fbx.py
    Blender -b world_kit.blend -P export_fbx.py

One FBX per model: its Empty or armature and everything under it (kit_Arena holds the arena's pieces), in the rest pose, without
animation (the game moves the bones itself). Models face Roblox -Z.
"""
from pathlib import Path

import bpy

OUT = Path(bpy.data.filepath).parent / "fbx"
# One folder per map, in throw order (GAME_SPEC section 8a), so the owner imports map by map.
MAPS = ("01_Forest", "02_Desert", "03_Swamp", "04_Volcano", "05_FrozenPeaks", "06_ShadowBog", "07_Abyss", "08_StarfallCrater", "09_EclipseTemple",
        "10_ForbiddenLibrary", "11_MidnightCarnival", "12_ClockworkCitadel", "13_ThornKingdom")
# Which map each .blend belongs to. A new map's .blend gets a line here.
MAP_OF_FILE = {"forest_models": "01_Forest", "world_kit": "01_Forest", "desert_models": "02_Desert", "base_kit": "01_Forest", "leaderboards": "01_Forest", "swamp_models": "03_Swamp",
               "volcano_models": "04_Volcano",
               "frozen_peaks_models": "05_FrozenPeaks",
               "shadow_bog_models": "06_ShadowBog",
               "abyss_models": "07_Abyss",
               "starfall_crater_models": "08_StarfallCrater",
               "eclipse_temple_models": "09_EclipseTemple",
               "forbidden_library_models": "10_ForbiddenLibrary",
               "midnight_carnival_models": "11_MidnightCarnival",
               "clockwork_citadel_models": "12_ClockworkCitadel",
               "thorn_kingdom_models": "13_ThornKingdom",
               "swamp_monsters": "03_Swamp", "frozen_peaks_monsters": "05_FrozenPeaks", "shadow_bog_monsters": "06_ShadowBog",
               "abyss_monsters": "07_Abyss", "starfall_crater_monsters": "08_StarfallCrater",
               "eclipse_temple_monsters": "09_EclipseTemple", "clockwork_citadel_monsters": "12_ClockworkCitadel"}
# Blender collection -> folder inside the map's folder.
EXPORT_COLLECTIONS = {"Animals": "Animals", "Props": "Props", "Kit": "Corridor", "Arena": "Arena", "Base": "Base"}


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
            for child in root.children_recursive:
                child.hide_render = False
            bpy.context.view_layer.update()
            bpy.ops.object.select_all(action="DESELECT")
            root.select_set(True)
            for child in root.children_recursive:
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
