"""Builds the pieces that stand at every base and renders them (run with Blender in background mode).

    Blender -b -P build_base_kit.py

Saves base_kit.blend and renders to design/world/models_base/. The target is docs/GAME_SPEC.md section 5
and docs/reference/shop-rack-sign-circled.webp: a chunky wooden stall with a striped awning, a squat rack
with thick ringed pillars and a dashed training circle, a round orange XP button, wooden fences and the
upgrade sign. Same rules as the other models: plain blocks, one mesh per colour role, no studs modelled
(the stud texture goes on in Studio), and every piece faces +Y here (Roblox -Z).

All pieces go under one root, kit_Base, so Studio imports them as one model. Each piece's origin is its
own floor centre, so the game can place it by its pivot.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_forest as kit  # noqa: E402
from build_forest import Model  # noqa: E402

RENDERS = HERE.parent.parent / "design" / "world" / "models_base"
kit.NO_STUDS.update({"Dash", "Bar", "Plate", "Hook", "Board"})

WOOD = "#b5793f"
DARK_WOOD = "#7d4e2a"
RAIL = "#c58848"
POST = "#9c6534"

# Sizes the game expects (Config/Hub, Config/Training, Config/Plot).
STALL_WIDTH, STALL_DEPTH, STALL_HEIGHT = 12, 8, 9
RACK_PAD_RADIUS = 5
XP_PAD_RADIUS = 3
FENCE_SECTION = 6  # rails between two posts; a 48-stud base side is 8 sections, a gate side 3
FENCE_HEIGHT = 4.6


def piece(name, **colours):
    return Model(f"base_{name}", colours)


def prism(m, role, cx, cy, z0, z1, r0, r1=None, sides=16):
    """A round post or disc standing on z0, made of `sides` flat faces."""
    r1 = r0 if r1 is None else r1
    ring = lambda z, r: [(cx + r * math.cos(a), cy + r * math.sin(a), z) for a in (2 * math.pi * i / sides for i in range(sides))]
    verts = ring(z0, r0) + ring(z1, r1)
    faces = [list(range(sides - 1, -1, -1)), list(range(sides, 2 * sides))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides + j, sides + i])
    m._add(role, verts, faces)


def disc_x(m, role, cx, cz, x0, x1, r, sides=16):
    """A round plate whose axis runs along X (barbell plates)."""
    ring = lambda x: [(x, r * math.cos(a), cz + r * math.sin(a)) for a in (2 * math.pi * i / sides for i in range(sides))]
    verts = ring(x0) + ring(x1)
    faces = [list(range(sides - 1, -1, -1)), list(range(sides, 2 * sides))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides + j, sides + i])
    m._add(role, verts, faces)


def tile(m, role, cx, cy, angle, length, width, z0, z1):
    """A flat block turned by angle around Z (the dashes of a circle)."""
    ca, sa = math.cos(angle), math.sin(angle)
    corners = [(-length / 2, -width / 2), (length / 2, -width / 2), (length / 2, width / 2), (-length / 2, width / 2)]
    ring = lambda z: [(cx + x * ca - y * sa, cy + x * sa + y * ca, z) for x, y in corners]
    verts = ring(z0) + ring(z1)
    faces = [[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    m._add(role, verts, faces)


def stall():
    """A wooden market stall: thick corner posts, low walls, a counter at the front and a striped awning.
    The game recolours the stripes (StripeA, StripeB) per stall: blue for the Egg Shop, red for SELL."""
    m = piece("Stall", Wood=WOOD, Post=DARK_WOOD, StripeA="#3c8cdc", StripeB="#f0f0f0",
              Shirt="#3c6ec8", Skin="#ffcd46")
    hw, hd = STALL_WIDTH / 2, STALL_DEPTH / 2
    post = 1.4
    for x in (-1, 1):
        for y in (-1, 1):
            m.block("Post", x * (hw - post / 2), y * (hd - post / 2), STALL_HEIGHT / 2, post, post, STALL_HEIGHT)
    m.block("Wood", 0, -hd + 0.5, 3.2, STALL_WIDTH - 2 * post, 1.0, 6.4)  # back wall
    for x in (-1, 1):
        m.block("Wood", x * (hw - 0.5), 0, 1.7, 1.0, STALL_DEPTH - 2 * post, 3.4)  # low side walls
    m.block("Wood", 0, hd - 0.7, 1.7, STALL_WIDTH - 2 * post, 1.4, 3.4)  # counter
    m.block("Post", 0, hd - 0.7, 3.65, STALL_WIDTH + 0.4, 2.2, 0.5)  # counter top

    # Shopkeeper behind the counter: a blocky figure with a friendly face.
    m.block("Shirt", 0, -0.8, 3.3, 2.4, 1.4, 2.6)
    m.block("Skin", 0, -0.8, 5.5, 2.0, 1.8, 1.8)
    for x in (-0.45, 0.45):
        m.block("Pupil", x, 0.12, 5.75, 0.32, 0.12, 0.5)
    m.block("Mouth", 0, 0.12, 5.05, 0.8, 0.12, 0.16)

    # Awning: stripes running front to back, high at the back and low at the front, overhanging both.
    stripes = 8
    width = (STALL_WIDTH + 1) / stripes
    back, front = (-hd - 1, STALL_HEIGHT + 1.6), (hd + 1, STALL_HEIGHT - 0.2)
    for i in range(stripes):
        x = -(STALL_WIDTH + 1) / 2 + width * (i + 0.5)
        role = "StripeA" if i % 2 == 0 else "StripeB"
        m.loft_y(role, (back[0], x, back[1], width, 0.6), (front[0], x, front[1], width, 0.6))
        m.block(role, x, front[0] - 0.3, front[1] - 0.9, width, 0.6, 1.4)  # the hanging front edge
    return m


def squat_rack():
    """Two thick pillars with coloured rings, a crossbar on top, J-hooks and a loaded bar, on a dashed
    circle that marks where you stand to train. The bar and plates are their own meshes (Bar, Plate),
    so the game can hide them while someone has the bar on their shoulders."""
    m = piece("SquatRack", Frame="#f5b731", Ring="#d9822b", Base="#5cbb33", Hook="#454a55",
              Bar="#c8ccd4", Plate="#2a2c33", Dash="#ffc7b8")
    gap, pillar, height = 3.8, 1.4, 8.6
    for side in (-1, 1):
        x = side * gap
        prism(m, "Base", x, 0, 0, 0.45, 1.5)
        m.block("Frame", x, 0, 0.45 + height / 2, pillar, pillar, height)
        for z in (1.4, 4.2, 7.4):
            m.block("Ring", x, 0, z, pillar + 0.3, pillar + 0.3, 0.55)
        m.block("Hook", x - side * 0.95, 0.35, 5.0, 0.55, 0.9, 0.35)
        m.block("Hook", x - side * 1.15, 0.35, 5.3, 0.15, 0.9, 0.5)
    m.block("Frame", 0, 0, 0.45 + height - 0.35, 2 * gap, 0.9, 0.7)  # crossbar

    bar_z = 5.45
    m.loft_x("Bar", (-6.4, 0.35, bar_z, 0.36, 0.36), (6.4, 0.35, bar_z, 0.36, 0.36))
    for x in (5.0, 5.55):
        for side in (-1, 1):
            disc_x(m, "Plate", 0, bar_z, side * x - 0.22, side * x + 0.22, 1.45)
    # Plates were built around y = 0; the bar sits at y = 0.35, so move them onto it.
    verts, _ = m.parts["Plate"]
    m.parts["Plate"] = ([(x, y + 0.35, z) for x, y, z in verts], m.parts["Plate"][1])

    dashes = 14
    for i in range(dashes):
        angle = 2 * math.pi * i / dashes
        tile(m, "Dash", RACK_PAD_RADIUS * math.cos(angle), RACK_PAD_RADIUS * math.sin(angle),
             angle + math.pi / 2, 1.4, 0.55, 0, 0.08)
    return m


def xp_button():
    """The round orange button in front of the rack: step on it to buy more XP per rep."""
    m = piece("XpButton", Edge="#8c8f99", Button="#ff9a1f")
    prism(m, "Edge", 0, 0, 0, 0.45, XP_PAD_RADIUS, sides=24)
    prism(m, "Button", 0, 0, 0.45, 0.85, XP_PAD_RADIUS - 0.4, XP_PAD_RADIUS - 0.55, sides=24)
    return m


def fence_post():
    m = piece("FencePost", Post=POST)
    m.block("Post", 0, 0, FENCE_HEIGHT / 2, 1.2, 1.2, FENCE_HEIGHT)
    m.block("Post", 0, 0, FENCE_HEIGHT + 0.15, 0.8, 0.8, 0.3)
    return m


def fence_rails():
    """Two planks between neighbouring posts, centred on the origin and running along X."""
    m = piece("FenceRails", Rail=RAIL)
    for z in (1.75, 3.35):
        m.block("Rail", 0, 0, z, FENCE_SECTION, 0.5, 0.9)
    return m


def upgrade_sign():
    """A small blue board on two legs, standing on the front fence by the gate. Its face (the numbers and
    the price) is a SurfaceGui the game draws on the Board's front."""
    m = piece("UpgradeSign", Post=POST, Board="#2f8ce6", Frame="#1d2340")
    for x in (-1.9, 1.9):
        m.block("Post", x, -0.1, 2.5, 0.6, 0.6, 5.0)
    m.block("Frame", 0, -0.15, 6.75, 6.0, 0.5, 4.5)
    m.block("Board", 0, 0.2, 6.75, 5.6, 0.2, 4.1)
    return m


def main():
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS  # kit.shoot saves there
    RENDERS.mkdir(parents=True, exist_ok=True)
    base = bpy.data.collections.new("Base")
    stage = bpy.data.collections.new("Preview stage")
    for col in (base, stage):
        scene.collection.children.link(col)

    models = [stall(), squat_rack(), xp_button(), fence_post(), fence_rails(), upgrade_sign()]
    root = bpy.data.objects.new("kit_Base", None)
    base.objects.link(root)
    roots = []
    x = 0
    for model in models:
        piece_root = model.build(base)
        piece_root.parent = root
        piece_root.location = (x, 0, 0)
        roots.append(piece_root)
        x += 18
    bpy.context.view_layer.update()

    # A ground and a 5.5 stud player, both only for the renders.
    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-60, -60, -0.01), (160, -60, -0.01), (160, 60, -0.01), (-60, 60, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(kit.material("Ground", "#4cc425", False))
    stage.objects.link(bpy.data.objects.new("Ground", ground_mesh))
    player = Model("Player", {"Skin": "#3f4553"})
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    player_root = player.build(stage)

    everything = roots + [player_root]
    for model, piece_root in zip(models, roots):
        player_root.location = piece_root.location + Vector((-8, 3, 0))
        bpy.context.view_layer.update()
        kit.set_visible(everything, [piece_root, player_root])
        low, high = kit.bounds(piece_root)
        centre = (low + high) / 2
        reach = max((high - low).length, 8)
        kit.shoot(scene, model.name, centre + Vector((0.55, 1.0, 0.5)) * reach * 1.2, centre, (700, 700), 50)

    # A base's front as the game lays it out: stall left of the gate, rack and button right of it.
    stage_pieces = bpy.data.collections.new("Preview: base front")
    scene.collection.children.link(stage_pieces)
    kit.set_visible(everything, [player_root])
    player_root.location = (0, 8, 0)

    def copy(model, location, rotation=0):
        obj_root = model.build(stage_pieces)
        obj_root.location = location
        obj_root.rotation_euler = (0, 0, rotation)
        return obj_root

    # Blender +Y is out of the base; Roblox +X (left as you walk up) is Blender +X.
    for x in [-24 + i * FENCE_SECTION for i in range(9)]:
        copy(fence_post(), (x, 0, 0))
    for i in range(8):
        x = -24 + FENCE_SECTION * (i + 0.5)
        if abs(x) > 6:
            copy(fence_rails(), (x, 0, 0))
    for y in [-i * FENCE_SECTION for i in range(1, 9)]:
        copy(fence_post(), (-24, y, 0))
        copy(fence_post(), (24, y, 0))
    copy(stall(), (15, 5, 0))
    copy(squat_rack(), (-15, 6, 0))
    copy(xp_button(), (-15, 16, 0))
    copy(upgrade_sign(), (-9.5, 0.9, 0))
    bpy.context.view_layer.update()
    kit.shoot(scene, "base_front", (8, 44, 22), (0, 4, 3), (1400, 800), 30)

    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "base_kit.blend"))
    print("saved", HERE / "base_kit.blend")
    for model in models:
        print(f"  {model.name}: roles {sorted(model.parts)}")


if __name__ == "__main__":
    main()
