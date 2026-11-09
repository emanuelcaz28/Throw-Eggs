"""Runs check_flicker_monsters.py's check on the monsters saved in a .blend (every dino_ armature), so it covers the monsters
whose build scripts have no ALL list too (the first six of the early maps).

    Blender -b <file>.blend --python check_flicker_blend.py
    GAP=0.03 ...     how close counts, in studs at the model's built size
    FIXED=1 ...      lift the layers first, as export_fbx.py does (flicker_fix.py), to check what reaches Studio

Prints one FLICKER line per monster and per fighting pair, like check_flicker_monsters.py.
"""
import os
import sys
from pathlib import Path

import bpy

import types

# check_flicker_monsters.py without its last line (main(), which builds from scripts and exits).
_source = (Path(bpy.data.filepath).parent / "check_flicker_monsters.py").read_text().rsplit("main()", 1)[0]
cfm = types.ModuleType("check_flicker_monsters")
cfm.__file__ = str(Path(bpy.data.filepath).parent / "check_flicker_monsters.py")
exec(compile(_source, "check_flicker_monsters.py", "exec"), cfm.__dict__)


class Seen:
    """The parts of one saved monster, shaped like a build script's Model: parts[role] = (verts, faces), groups[role][i] = bone."""

    def __init__(self, armature):
        self.name = armature.name
        self.parts, self.groups = {}, {}
        for mesh in armature.children:
            if mesh.type != "MESH":
                continue
            role = mesh.name[len(armature.name) + 1:] or mesh.name
            m = mesh.matrix_world
            data = mesh.data
            names = {g.index: g.name for g in mesh.vertex_groups}
            bones = []
            for v in data.vertices:
                best = max(v.groups, key=lambda g: g.weight, default=None)
                bones.append(names.get(best.group, "?") if best else "?")
            self.parts[role] = ([tuple(m @ v.co) for v in data.vertices], [tuple(p.vertices) for p in data.polygons])
            self.groups[role] = bones


sys.path.insert(0, str(Path(bpy.data.filepath).parent))
import flicker_fix  # noqa: E402

for obj in bpy.data.objects:
    if obj.type == "ARMATURE" and obj.name.startswith("dino_"):
        if os.environ.get("FIXED"):
            flicker_fix.lift(obj)
        hits, worst = cfm.check(Seen(obj))
        shown = {k: v for k, v in hits.items() if v > cfm.LIMIT}
        print(f"FLICKER {Path(bpy.data.filepath).stem} {obj.name}: " + ("clear" if not shown else f"{len(shown)} pairs"))
        for pair, area in sorted(shown.items(), key=lambda kv: -kv[1]):
            print(f"FLICKER    {pair[0]} / {pair[1]}: {area:.2f} sq studs, worst at {worst[pair][1]} on {worst[pair][2]}")
