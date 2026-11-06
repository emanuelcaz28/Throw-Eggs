"""Builds the pedestal for the server's best catch, in the middle of the arena, and renders it (Blender, background mode).

    Blender -b -P build_best_catch.py

Saves best_catch.blend and renders to design/world/best_catch/.

An eight-sided stone plinth on a wide step, a gold band round its top with a purple cushion the monster stands on,
a ring of marquee bulbs round its middle and a gold plaque with a crown on its front. The game puts the server's
rarest catch on the cushion at its map's standard size.

In front of it stands a sign on two posts: a dark Screen in a gold frame, where the game writes the catch's name,
mutation, size, odds, income, world and who caught it (Figma "Throw Eggs - Pop-up Text", "Best catch sign face").

The game finds the parts by role: Glow (the bulbs) gets the Neon material (shared/Roles.luau), Screen carries the
text, Top is the cushion the monster stands on, and the small Front part tells it which way the pedestal faces, then it's removed.
1 Blender unit = 1 stud, the pedestal faces +Y and stands on Z = 0 at its origin.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_desert import beam  # noqa: E402
from build_forest import Model  # noqa: E402
from build_leaderboards import disc  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "best_catch"
kit.NO_STUDS.update({"Glow", "Top", "Screen"})

COLOURS = {"Wood": "#a0663a", "WoodDark": "#6e4224", "Screen": "#1f1a33", "Stone": "#8f97ab", "StoneDark": "#6f778c", "Trim": "#ffc93c", "TrimDark": "#d99a1e", "Top": "#6a2fa3",
           "TopDark": "#4a1f78", "Glow": "#fff1a8", "Badge": "#6a2fa3", "Icon": "#ffe066", "IconDark": "#d99a1e",
           "Gem": "#ff5fa8", "Front": "#ff00ff"}

SIDES = 8
TOP_Z = 4.6  # the cushion's top, where the monster's feet go (Config/BestCatch standHeight)
SIGN_Y = 12.0  # the sign's screen, in front of the pedestal
SIGN_W, SIGN_H, SIGN_Z = 8.0, 4.0, 2.7  # its width, height and the height of its middle (2:1, like its Figma face)


def prism(m, role, r, z0, z1, sides=SIDES, turn=math.pi / SIDES):
    """An n-sided column standing on Z, centred on the origin, a flat side facing +Y."""
    verts = []
    for z in (z0, z1):
        for i in range(sides):
            a = turn + i * math.tau / sides
            verts.append((r * math.cos(a), r * math.sin(a), z))
    faces = [list(range(sides))[::-1], list(range(sides, 2 * sides))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides + j, sides + i])
    m._add(role, verts, faces)


def pedestal():
    m = Model("prop_BestCatchPedestal", COLOURS)
    prism(m, "StoneDark", 9.4, 0, 0.7)  # the wide step
    prism(m, "Stone", 8.6, 0.7, 1.1)
    prism(m, "Stone", 7.4, 1.1, 3.7)  # the drum
    prism(m, "TrimDark", 7.7, 1.1, 1.5)  # gold collar at its foot
    prism(m, "Trim", 7.9, 3.7, 4.2)  # gold band
    prism(m, "TopDark", 7.5, 4.2, 4.35)
    prism(m, "Top", 7.2, 4.35, TOP_Z)  # the cushion

    # Marquee bulbs round the drum, two on each side.
    apothem = 7.4 * math.cos(math.pi / SIDES)
    for i in range(SIDES):
        a = math.pi / 2 + i * math.tau / SIDES  # the middle of each flat side
        out, side = Vector((math.cos(a), math.sin(a), 0)), Vector((-math.sin(a), math.cos(a), 0))
        for k in (-1, 1):
            if i == 0:
                continue  # the plaque covers the front side
            c = out * (apothem + 0.05) + side * k * 1.4
            m.block("Glow", c.x, c.y, 2.45, 0.45 if abs(out.x) > 0.5 else 0.5, 0.45 if abs(out.y) > 0.5 else 0.5, 0.45)

    # The plaque on the front: gold frame, purple face, a crown with gems.
    y = apothem
    m.block("TrimDark", 0, y + 0.15, 2.4, 5.2, 0.4, 2.3)
    m.block("Trim", 0, y + 0.35, 2.4, 4.8, 0.3, 1.9)
    m.block("Badge", 0, y + 0.55, 2.4, 4.0, 0.2, 1.4)
    face = y + 0.68
    m.block("Icon", 0, face, 1.9, 2.4, 0.16, 0.38)  # the crown's band
    for x, h in ((-0.95, 0.5), (0, 0.65), (0.95, 0.5)):  # its three points, clear of the frame
        beam(m, "Icon", (x * 0.85, face, 2.05), (x, face, 2.05 + h), 0.42, 0.14, 0.12)
        disc(m, "IconDark", x, 2.05 + h + 0.12, 0.16, face - 0.08, face + 0.1, 8)
    for x in (-0.7, 0, 0.7):
        disc(m, "Gem", x, 1.9, 0.13, face + 0.06, face + 0.12, 8)
    m.block("Front", 0, 18, 1, 0.2, 0.2, 0.2)  # no sign any more: the owner asked for it gone (2026-11-05)
    return m


def sign(m):
    """The sign in front of the pedestal: a dark screen in a gold frame on two posts, as tall as the cushion so it
    doesn't hide the monster. The game writes the catch on the screen (Figma "Best catch sign face", 2:1)."""
    y = SIGN_Y
    for x in (-3.6, 3.6):  # posts, with a foot each
        m.block("Wood", x, y - 0.5, 1.4, 0.7, 0.7, 2.8)
        m.block("StoneDark", x, y - 0.5, 0.2, 1.4, 1.4, 0.4)
    m.block("WoodDark", 0, y - 0.3, SIGN_Z, SIGN_W + 0.6, 0.5, SIGN_H + 0.6)  # back panel
    m.block("Screen", 0, y, SIGN_Z, SIGN_W, 0.3, SIGN_H)
    for side in (-1, 1):  # the gold frame
        m.block("Trim", side * (SIGN_W / 2 + 0.25), y + 0.05, SIGN_Z, 0.5, 0.5, SIGN_H + 1.0)
        m.block("Trim", 0, y + 0.05, SIGN_Z + side * (SIGN_H / 2 + 0.25), SIGN_W + 1.0, 0.5, 0.5)
    for x in (-1, 1):
        for z in (-1, 1):
            m.block("TrimDark", x * (SIGN_W / 2 + 0.25), y + 0.1, SIGN_Z + z * (SIGN_H / 2 + 0.25), 0.7, 0.55, 0.7)
    for x in (-1, 1):  # a gold ball on each top corner
        m.loft_z("Trim", (SIGN_Z + SIGN_H / 2 + 0.6, x * (SIGN_W / 2 + 0.25), y + 0.05, 0.6, 0.6), (SIGN_Z + SIGN_H / 2 + 1.0, x * (SIGN_W / 2 + 0.25), y + 0.05, 0.3, 0.3))


ALL = [pedestal]  # for studio_tidy.py


def main():
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    arena = bpy.data.collections.new("Arena")
    stage = bpy.data.collections.new("Preview stage")
    for col in (arena, stage):
        scene.collection.children.link(col)

    model = pedestal()
    root = model.build(arena)
    for child in root.children:
        if child.name.endswith("_Glow"):
            bsdf = child.data.materials[0].node_tree.nodes.get("Principled BSDF")
            bsdf.inputs["Emission Color"].default_value = (1, 0.9, 0.5, 1)
            bsdf.inputs["Emission Strength"].default_value = 2
        if child.name.endswith("_Front"):
            child.hide_render = True

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-200, -200, -0.01), (200, -200, -0.01), (200, 200, -0.01), (-200, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", "#4cc425", False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage.objects.link(ground)
    player = Model("Player", {"Skin": "#3f4553"})
    player.bone = "Root"
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    player_root = player.build(stage)
    player_root.location = (-11, 8, 0)
    bpy.context.view_layer.update()

    kit.shoot(scene, "pedestal", (14, 40, 14), (0, 4, 2.5), (1200, 900), 40)
    kit.shoot(scene, "pedestal_plaque", (2, 10, 3), (0, 6.5, 2.4), (800, 600), 45)

    for child in root.children:
        child.hide_render = False
        if child.name.endswith("_Glow"):
            child.data.materials[0].node_tree.nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = 0
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "best_catch.blend"))
    print("saved", HERE / "best_catch.blend")
    print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    main()
