"""Exports the Blender models to assets/models/fbx/<map>/<kind>/ for Roblox Studio's 3D importer.

    Blender -b forest_models.blend -P export_fbx.py
    Blender -b world_kit.blend -P export_fbx.py

One FBX per model: its Empty or armature and everything under it (kit_Arena holds the arena's pieces), in the rest pose, without
animation (the game moves the bones itself). Models face Roblox -Z.
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(bpy.data.filepath).parent))
import flicker_fix  # noqa: E402

OUT = Path(bpy.data.filepath).parent / "fbx"
# One folder per map, in throw order (GAME_SPEC section 8a), so the owner imports map by map.
MAPS = ("01_Forest", "02_Desert", "03_Swamp", "04_Volcano", "05_FrozenPeaks", "06_ShadowBog", "07_Abyss", "08_StarfallCrater", "09_EclipseTemple",
        "10_ForbiddenLibrary", "11_MidnightCarnival", "12_ClockworkCitadel", "13_ThornKingdom", "14_SporeHollow",
        "15_WeepingDark", "16_Specials", "17_DeepEnd", "00_Eggs")
# Which map each .blend belongs to. A new map's .blend gets a line here.
MAP_OF_FILE = {"forest_models": "01_Forest", "world_kit": "01_Forest", "desert_models": "02_Desert", "base_kit": "01_Forest", "leaderboards": "01_Forest", "best_catch": "01_Forest", "racks": "01_Forest", "swamp_models": "03_Swamp",
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
               "spore_hollow_models": "14_SporeHollow",
               "weeping_dark_models": "15_WeepingDark",
               "deep_end_models": "17_DeepEnd",
               "swamp_monsters": "03_Swamp", "frozen_peaks_monsters": "05_FrozenPeaks", "shadow_bog_monsters": "06_ShadowBog",
               "abyss_monsters": "07_Abyss", "starfall_crater_monsters": "08_StarfallCrater",
               "eclipse_temple_monsters": "09_EclipseTemple", "forbidden_library_monsters": "10_ForbiddenLibrary",
               "midnight_carnival_monsters": "11_MidnightCarnival",  # the original six, polished 2026-11-12 (the fright set, midnight_carnival_fright, was turned down)
               "clockwork_citadel_monsters": "12_ClockworkCitadel",
               "thorn_kingdom_monsters": "13_ThornKingdom",
               "spore_hollow_toxic": "14_SporeHollow",  # all 8, the toxic set (2026-11-10); spore_hollow_monsters and _7_8 are the old looks, not exported any more
               "weeping_dark_dread": "15_WeepingDark",  # the first 7, the dread set (2026-11-10); weeping_dark_monsters is the old looks, not exported any more
               "forest_monsters_7_8": "01_Forest", "desert_monsters_7_8": "02_Desert", "swamp_monsters_7_8": "03_Swamp",
               "volcano_monsters_7_8": "04_Volcano", "frozen_peaks_monsters_7_8": "05_FrozenPeaks", "shadow_bog_monsters_7_8": "06_ShadowBog",
               "abyss_monsters_7_8": "07_Abyss", "starfall_crater_monsters_7_8": "08_StarfallCrater", "eclipse_temple_monsters_7_8": "09_EclipseTemple",
               "forbidden_library_monsters_7_8": "10_ForbiddenLibrary", "midnight_carnival_monsters_7_8": "11_MidnightCarnival", "clockwork_citadel_monsters_7_8": "12_ClockworkCitadel",
               "thorn_kingdom_monsters_7_8": "13_ThornKingdom", "weeping_dark_monsters_7_8": "15_WeepingDark",
               "special_monsters": "16_Specials",
               "eggs": "00_Eggs"}  # the Egg Shop's eggs, all in one folder (build_eggs.py)
# Models a .blend still holds but must not export: another file makes them now.
SKIP = {"weeping_dark_monsters_7_8": {"dino_Inconsolable"}}  # redesigned in weeping_dark_dread; Last Breath still comes from this file
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
            if root.name in SKIP.get(Path(bpy.data.filepath).stem, ()):
                continue
            if root.type == "ARMATURE":
                if root.name.startswith("dino_"):
                    print("flicker lifted", root.name, flicker_fix.lift(root))  # in memory only; the .blend isn't saved
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
