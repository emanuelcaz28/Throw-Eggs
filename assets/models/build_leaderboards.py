"""Builds the arena's three leaderboards and renders them (Blender, background mode).

    Blender -b -P build_leaderboards.py

Saves leaderboards.blend and renders to design/world/leaderboards/.

Each board stands on a stone plinth between two wooden posts with gold caps: a dark screen in a wooden frame
(the game draws the top 10 on it), a header plaque in the board's colour with a row of marquee bulbs along
its gold bands (the game writes the title on it), and on top a gold medallion with the board's icon: a paw
for MOST DINOS, a stack of cash for TOP MONEY and a four-leaf clover for LUCKIEST CATCH.

The game finds the parts by role: Screen and Header carry the text, Glow (the bulbs) gets the Neon material
(shared/Roles.luau) and the small Front part tells it which way the board faces, then it's removed.
1 Blender unit = 1 stud, the board faces +Y and stands on Z = 0 at its origin.
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

RENDERS = HERE.parent.parent / "design" / "world" / "leaderboards"
kit.NO_STUDS.update({"Screen", "Glow"})

# The frame, shared by all three.
FRAME = {"Wood": "#a0663a", "WoodDark": "#6e4224", "Trim": "#ffc93c", "TrimDark": "#d99a1e", "Stone": "#8f97ab",
         "StoneDark": "#6f778c", "Screen": "#1f1a33", "Glow": "#fff1a8", "Front": "#ff00ff"}

# Per board: its colours and the icon on its medallion (Config/Leaderboards ids).
BOARDS = {
    "MostDinos": {"Header": "#3f8fe6", "HeaderDark": "#2a64b0", "Badge": "#2a64b0", "Icon": "#fff6e0", "IconDark": "#ffcf6a"},
    "TopMoney": {"Header": "#55b83f", "HeaderDark": "#3a8a2b", "Badge": "#2f6f24", "Icon": "#8dff5a", "IconDark": "#3fae4a",
                 "IconLight": "#fff3c4"},
    "LuckiestCatch": {"Header": "#a55ae0", "HeaderDark": "#7a3cb3", "Badge": "#6a2fa3", "Icon": "#5fe06a", "IconDark": "#2fa63a",
                      "IconLight": "#c8ffb8"},
}

MEDAL_Z = 26.0  # the medallion's centre height
FACE_Y = 1.3  # the front of the medallion's badge, where the icon sits


def disc(m, role, x, z, r, y0, y1, sides=16, turn=0.0):
    """A round slab facing the front: an n-sided column along Y from y0 to y1, centred on (x, z)."""
    verts = []
    for y in (y0, y1):
        for i in range(sides):
            a = turn + i * math.tau / sides
            verts.append((x + r * math.cos(a), y, z + r * math.sin(a)))
    faces = [list(range(sides)), list(range(sides, 2 * sides))[::-1]]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides + j, sides + i])
    m._add(role, verts, faces)


def frame(m):
    """The plinth, posts, screen, frame and header, the same on every board."""
    m.block("Stone", 0, 0, 0.6, 21.4, 5.4, 1.2)
    m.block("StoneDark", 0, 2.95, 0.3, 17.0, 0.6, 0.6)  # a step along the front
    m.block("StoneDark", 0, 0, 1.3, 20.4, 4.6, 0.2)
    for side in (-1, 1):
        x = side * 9.5
        m.block("Wood", x, 0, 12.7, 1.8, 1.8, 22.6)
        m.block("TrimDark", x, 0, 1.75, 2.3, 2.3, 0.7)  # collar
        m.block("Trim", x, 0, 24.25, 2.4, 2.4, 0.7)  # cap
        m.loft_z("Trim", (24.6, x, 0, 1.6, 1.6), (25.4, x, 0, 1.9, 1.9))  # a ball on top
        m.loft_z("Trim", (25.4, x, 0, 1.9, 1.9), (26.1, x, 0, 0.7, 0.7))
        for z in (6.0, 12.0):  # brackets holding the screen
            m.block("TrimDark", side * 8.75, 0.2, z, 0.9, 1.2, 0.5)
    m.block("WoodDark", 0, -0.25, 10.6, 17.4, 0.8, 16.8)  # back panel
    m.block("Screen", 0, 0.35, 10.6, 16.0, 0.5, 15.4)
    for side in (-1, 1):  # the frame round the screen
        m.block("Wood", side * 8.45, 0.45, 10.6, 0.9, 0.9, 16.8)
    for z in (2.45, 18.75):
        m.block("Wood", 0, 0.45, z, 17.8, 0.9, 0.9)
    for x in (-8.45, 8.45):
        for z in (2.45, 18.75):
            m.block("Trim", x, 0.5, z, 1.15, 1.1, 1.15)  # a touch deeper than the frame, so their backs don't flicker
    # The header plaque, gold bands top and bottom, with marquee bulbs along them.
    # Its front stands 0.1 proud of the posts' fronts (y 0.9): level with them, the two flickered [Owner, 2026-11-11].
    m.block("Header", 0, 0.3, 21.45, 18.6, 1.4, 4.3)
    m.block("HeaderDark", 0, -0.25, 21.45, 18.9, 1.0, 4.6)
    for z in (19.3, 23.6):
        m.block("Trim", 0, 0.25, z, 19.2, 1.7, 0.55)
        for k in range(11):
            m.block("Glow", -8.0 + k * 1.6, 1.12, z, 0.42, 0.12, 0.34)
    m.block("Front", 0, 4, 1, 0.2, 0.2, 0.2)


def medallion(m):
    """A gold rosette on top of the header, the board's badge inside it."""
    for k in range(14):  # a scalloped edge of round bumps
        a = k * math.tau / 14
        disc(m, "TrimDark", 2.75 * math.cos(a), MEDAL_Z + 2.75 * math.sin(a), 0.55, -0.1, 0.85, 10)
    disc(m, "Trim", 0, MEDAL_Z, 2.8, -0.2, 1.05, 16)
    disc(m, "Badge", 0, MEDAL_Z, 2.2, 1.05, FACE_Y - 0.05, 16)


def paw(m):
    """MOST DINOS: a monster's paw print."""
    z = MEDAL_Z
    for x in (-0.38, 0.38):  # a bean-shaped pad
        disc(m, "Icon", x, z - 0.5, 0.72, FACE_Y - 0.1, FACE_Y + 0.15, 12)
    m.block("Icon", 0, FACE_Y + 0.02, z - 0.75, 0.9, 0.25, 0.6)
    for x, dz in ((-1.15, 0.28), (-0.45, 0.98), (0.45, 0.98), (1.15, 0.28)):  # toes
        disc(m, "Icon", x, z + dz, 0.4, FACE_Y - 0.1, FACE_Y + 0.15, 10)
        m.block("IconDark", x + 0.12, FACE_Y + 0.17, z + dz + 0.14, 0.14, 0.05, 0.14)  # a claw glint


def cash(m):
    """TOP MONEY: a stack of three bills and a gold coin."""
    z = MEDAL_Z
    # Every layer's front is at least 0.04 from any other's, or they flicker [Owner, 2026-11-11].
    for i in range(3):
        x, dz = -0.35 + 0.3 * i, -0.55 + 0.42 * i
        y = FACE_Y + 0.05 + 0.2 * i
        m.block("IconDark", x, y - 0.02, z + dz, 3.0, 0.16, 1.45)  # front y + 0.06
        m.block("Icon", x, y + 0.04, z + dz, 2.8, 0.12, 1.25)  # front y + 0.10
        m.block("IconDark", x, y + 0.12, z + dz, 1.9, 0.04, 0.75)  # front y + 0.14
        disc(m, "IconLight", x, z + dz, 0.3, y + 0.12, y + 0.2, 10)  # front y + 0.20, under the next bill's y + 0.26
    disc(m, "Trim", 1.15, z - 1.0, 0.62, FACE_Y + 0.45, FACE_Y + 0.8, 12)
    disc(m, "TrimDark", 1.15, z - 1.0, 0.4, FACE_Y + 0.8, FACE_Y + 0.86, 12)


def clover(m):
    """LUCKIEST CATCH: a four-leaf clover, each leaf a pair of round lobes."""
    z = MEDAL_Z + 0.15
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        out = Vector((math.cos(a), math.sin(a)))
        side = Vector((-out.y, out.x))
        for s in (-1, 1):  # a heart: two lobes and a point towards the middle
            c = out * 1.0 + side * s * 0.34
            disc(m, "Icon", c.x, z + c.y, 0.46, FACE_Y - 0.1, FACE_Y + 0.15, 12)
        tip = out * 0.42
        disc(m, "Icon", tip.x, z + tip.y, 0.3, FACE_Y - 0.1, FACE_Y + 0.15, 8)
        vein_a, vein_b = out * 0.5, out * 1.05
        beam(m, "IconDark", (vein_a.x, FACE_Y + 0.17, z + vein_a.y), (vein_b.x, FACE_Y + 0.17, z + vein_b.y), 0.1, 0.05)
    disc(m, "IconDark", 0, z, 0.24, FACE_Y + 0.1, FACE_Y + 0.2, 10)
    # The stem, its front 0.05 proud of the leaves' (FACE_Y + 0.15): level with them, they flickered.
    beam(m, "IconDark", (0.1, FACE_Y + 0.1, z - 0.3), (0.55, FACE_Y + 0.1, z - 1.25), 0.26, 0.2, 0.2)
    beam(m, "IconDark", (0.55, FACE_Y + 0.1, z - 1.25), (1.05, FACE_Y + 0.1, z - 1.6), 0.2, 0.2, 0.16)


ICONS = {"MostDinos": paw, "TopMoney": cash, "LuckiestCatch": clover}


def board(board_id):
    m = Model(f"board_{board_id}", {**FRAME, **BOARDS[board_id]})
    frame(m)
    medallion(m)
    ICONS[board_id](m)
    return m


def main():
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    arena = bpy.data.collections.new("Arena")
    stage = bpy.data.collections.new("Preview stage")
    for col in (arena, stage):
        scene.collection.children.link(col)

    models = [board(i) for i in ("MostDinos", "TopMoney", "LuckiestCatch")]
    roots = []
    for i, model in enumerate(models):
        root = model.build(arena)
        root.location = (i * 24 - 24, 0, 0)
        roots.append(root)
    for root in roots:  # the bulbs shine in the renders only
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
    player_root.location = (-12, 6, 0)
    bpy.context.view_layer.update()

    kit.shoot(scene, "boards", (-14, 62, 22), (0, 0, 13), (1600, 900), 32)
    for model, root in zip(models, roots):
        centre = root.location + Vector((0, 0, 14))
        kit.shoot(scene, model.name, centre + Vector((9, 30, 4)), centre, (700, 900), 40)
        head = root.location + Vector((0, 0, MEDAL_Z))
        kit.shoot(scene, f"{model.name}_medal", head + Vector((1.5, 11, 1)), head, (600, 600), 45)

    for root in roots:
        pass  # keep them side by side in the .blend; the exporter moves each to the origin
        for child in root.children:
            child.hide_render = False
            if child.name.endswith("_Glow"):
                child.data.materials[0].node_tree.nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = 0
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "leaderboards.blend"))
    print("saved", HERE / "leaderboards.blend")
    for model in models:
        print(f"  {model.name}: {sum(len(f) for _, f in model.parts.values())} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    main()
