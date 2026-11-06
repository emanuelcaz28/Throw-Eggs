"""Builds the squat racks a player earns with rack upgrades and renders them (run with Blender in background mode).

    Blender -b -P build_racks.py

Saves racks.blend and renders to design/world/models_racks/. Rack 1 is base_SquatRack in build_base_kit.py; these are
racks 2 to 6, and Config/Training rackModels says how many upgrades each one needs. Everyone sees them, so each should
read as a step up from across the arena: Iron, Bone, Crystal, Magma, Titan.

What the game needs from every rack (TrainingService):
- The lifter stands at the origin, so the floor stays flat and clear between the pillars (|x| under 2) and in front.
- The loaded bar is its own Bar and Plate parts, at the same height as rack 1: they're hidden while it's being lifted.
- The dashed circle is the Dash part, radius 5, the pad the game reads. The game turns its collisions off.
- Nothing stands in front of y = 4.5: the XP button is at y = 7 and STOP puts the lifter down at y = 6.
- Nothing tall behind the lifter between the pillars, or it gets between them and the camera.

Plain colours, no studs here (the "Studs" material goes on in Studio). Glowing roles must be in shared/Roles.luau.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import map_kit as mk  # noqa: E402
from map_kit import Model, ball, beam, crystal, disc, flat_ring, gem, kit, limb, plate, prism  # noqa: E402
from build_base_kit import RACK_PAD_RADIUS, squat_rack, tile  # noqa: E402

kit.PREVIEW_STUDS = False
RENDERS = HERE.parent.parent / "design" / "world" / "models_racks"

GLOW_ROLES = {"Lava", "Flame", "Ember", "EyeGlow", "CrystalGlow", "Shine"}
kit.NO_STUDS.update(GLOW_ROLES | {"Dash", "Bar", "Plate", "Hook", "Chain", "Bolt", "Socket"})
mk.GLOW_STRENGTH = 1.0  # stronger clips the crystals to white in the renders

GAP = 3.8  # pillars stand this far either side of the lifter, like rack 1
BAR_Y, BAR_Z = 0.35, 5.45  # where rack 1's bar rests


def rack(name, **colours):
    m = Model(f"base_SquatRack_{name}", {"Dash": "#ffc7b8", **colours})
    m.bone = "Root"
    return m


def plate_x(m, x0, x1, r, sides=16):
    """A barbell plate on the bar."""
    ring = lambda x: [(x, BAR_Y + r * math.cos(a), BAR_Z + r * math.sin(a)) for a in (math.tau * i / sides for i in range(sides))]
    faces = [list(range(sides - 1, -1, -1)), list(range(sides, 2 * sides))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append([i, j, sides + j, sides + i])
    m._add("Plate", ring(x0) + ring(x1), faces)


def loaded_bar(m, plates=(1.45, 1.45), length=6.4):
    """The bar and its plates, biggest innermost. More and bigger plates on the better racks."""
    m.loft_x("Bar", (-length, BAR_Y, BAR_Z, 0.36, 0.36), (length, BAR_Y, BAR_Z, 0.36, 0.36))
    for i, r in enumerate(plates):
        x = 5.0 + i * 0.5
        for side in (-1, 1):
            plate_x(m, side * x - 0.22, side * x + 0.22, r)


def dashed_circle(m):
    dashes = 14
    for i in range(dashes):
        angle = math.tau * i / dashes
        tile(m, "Dash", RACK_PAD_RADIUS * math.cos(angle), RACK_PAD_RADIUS * math.sin(angle), angle + math.pi / 2, 1.4, 0.55, 0, 0.08)


def hooks(m, role="Hook"):
    """The J-hooks the bar rests on."""
    for side in (-1, 1):
        x = side * GAP
        m.block(role, x - side * 1.0, BAR_Y, 5.0, 0.6, 0.9, 0.35)
        m.block(role, x - side * 1.2, BAR_Y, 5.3, 0.16, 0.9, 0.5)


def iron():
    """Rack 2: serious gym steel. Square pillars braced from behind on long feet, bolts, blue bands, chains
    swinging from the crossbar and a kettlebell left beside each foot."""
    m = rack("Iron", Frame="#566274", Brace="#3d4655", Foot="#2c323c", Ring="#2f8ce6", Bolt="#d4d8e0", Hook="#2c323c",
             Chain="#98a0ae", Weight="#25282f", Bar="#c8ccd4", Plate="#1f2127")
    height = 9.8
    top = 0.6 + height
    for side in (-1, 1):
        x = side * GAP
        m.block("Foot", x, -0.8, 0.3, 3.0, 5.4, 0.6)
        m.block("Frame", x, 0, 0.6 + height / 2, 1.7, 1.7, height)
        beam(m, "Brace", (x, -3.0, 0.6), (x, -0.5, 6.8), 0.8)
        for z in (2.3, 7.4):
            m.block("Ring", x, 0, z, 2.0, 2.0, 0.55)
        for z in (1.2, 3.4, 6.3, 8.6):  # bolts down the front
            m.block("Bolt", x, 0.92, z, 0.42, 0.2, 0.42)
        for dx in (-1, 1):  # and on the foot
            for y in (-2.8, 1.0):
                m.block("Bolt", x + dx * 1.05, y, 0.65, 0.42, 0.42, 0.14)
        # A kettlebell on the floor outside the pillar.
        kx = side * 6.4
        ball(m, "Weight", kx, -2.2, 0.8, 0.85)
        m.block("Weight", kx, -2.2, 1.95, 0.3, 1.1, 0.3)
        for dy in (-0.45, 0.45):
            m.block("Weight", kx, -2.2 + dy, 1.6, 0.3, 0.26, 0.7)
    m.block("Frame", 0, 0, top - 0.6, 2 * GAP + 1.7, 1.3, 1.2)
    m.block("Ring", 0, 0, top - 0.6, 2.2, 1.5, 1.4)
    for x in (-2.2, 2.2):  # the chains, link by link
        for i in range(5):
            wide = i % 2 == 0
            m.block("Chain", x, 0, top - 1.45 - i * 0.42, 0.34 if wide else 0.14, 0.14 if wide else 0.34, 0.5)
        m.block("Weight", x, 0, top - 3.6, 0.8, 0.8, 0.5)
    hooks(m)
    loaded_bar(m, (1.45, 1.2))
    dashed_circle(m)
    return m


def bone():
    """Rack 3: built from something that died. Two great thigh bones for pillars with ribs curling out of them, a
    spine for a crossbar, tusks holding the bar, and a horned skull on top with green fire in its sockets."""
    m = rack("Bone", Bone="#e9e0c6", BoneDark="#b9a985", Socket="#2a2020", EyeGlow="#7dff5a", Rock="#5b5147",
             Teeth="#fff6dc", Bar="#ddd3b6", Plate="#4d4036")
    for side in (-1, 1):
        x = side * GAP
        prism(m, "Rock", x, -0.2, 0, 0.7, 2.1, 1.5, sides=7)
        prism(m, "Bone", x, 0, 0.5, 9.3, 0.85, 0.72, sides=8)
        for dx in (-0.5, 0.5):  # the knobbly ends of a thigh bone
            ball(m, "Bone", x + dx, 0, 1.0, 0.95)
            ball(m, "Bone", x + dx, 0, 9.0, 0.95)
        for z in (3.3, 7.0):  # lashed with dark sinew
            prism(m, "BoneDark", x, 0, z, z + 0.45, 0.95, 0.95, sides=8)
        for i, z in enumerate((7.6, 5.9, 4.2, 2.5)):  # ribs curling out and back
            reach = 2.3 - i * 0.15
            limb(m, "Bone", [(x + side * 0.6, -0.3, z), (x + side * reach * 0.75, -1.3, z + 0.45), (x + side * reach, -2.9, z - 0.2),
                             (x + side * reach * 0.8, -3.9, z - 0.9)], 0.5, 0.16)
        # A tusk curling up in front to hold the bar.
        limb(m, "Bone", [(x, 0.3, 4.3), (x - side * 0.85, BAR_Y + 0.15, 4.6), (x - side * 1.15, BAR_Y, 5.2), (x - side * 1.2, BAR_Y, 6.1)], 0.46, 0.14)

    # The spine, with a spike on every bone.
    x = -GAP + 0.3
    while x <= GAP - 0.2:
        m.block("Bone", x, 0, 9.7, 0.62, 1.15, 1.15)
        m.block("BoneDark", x + 0.36, 0, 9.7, 0.14, 0.8, 0.8)
        plate(m, "Bone", (x, 0, 10.2), (x, -0.25, 11.0 - abs(x) * 0.08), (1, 0, 0), 0.42, 0.08, 0.2)
        x += 0.74

    # The skull, looking out over the lifter.
    sz = 11.5
    ball(m, "Bone", 0, 0, sz, 1.7, sides=10, rings=6)
    m.loft_y("Bone", (0.8, 0, sz - 0.6, 2.5, 1.9), (2.9, 0, sz - 0.9, 1.5, 1.0))  # snout
    m.block("Bone", 0, 1.1, sz - 1.95, 2.0, 2.0, 0.42)  # lower jaw
    for side in (-1, 1):
        m.block("Socket", side * 0.72, 1.32, sz + 0.2, 0.92, 0.62, 0.92)
        m.block("EyeGlow", side * 0.72, 1.56, sz + 0.2, 0.46, 0.22, 0.46)
        m.block("Socket", side * 0.3, 2.86, sz - 0.72, 0.22, 0.14, 0.3)  # nostrils
        limb(m, "BoneDark", [(side * 1.3, 0, sz + 1.0), (side * 2.6, 0.1, sz + 1.4), (side * 3.2, 0.4, sz + 2.5), (side * 2.9, 0.7, sz + 3.6)], 0.7, 0.1)
    for i in range(5):
        x = -0.72 + i * 0.36
        m.loft_z("Teeth", (sz - 1.4, x, 2.45, 0.28, 0.26), (sz - 1.9, x, 2.45, 0.06, 0.06))
    loaded_bar(m, (1.5, 1.2))
    dashed_circle(m)
    return m


def crystal_rack():
    """Rack 4: nobody built this one, it grew. Amethyst columns rising in clusters from dark rock, glowing bands, two
    shards leaning in to make the crossbar, and a gem floating over it all, with smaller ones drifting round it."""
    m = rack("Crystal", Crystal="#7a55e0", CrystalDark="#4a2fa8", CrystalGlow="#c7a2ff", Shine="#6ff0ff", Rock="#2d2a3e",
             Hook="#c7a2ff", Bar="#eaf6ff", Plate="#3fc4ea")
    for side in (-1, 1):
        x = side * GAP
        prism(m, "Rock", x, -0.1, 0, 1.0, 2.2, 1.5, sides=7, turn=0.3)
        crystal(m, "Crystal", "CrystalGlow", x, 0, 0.7, 10.2, 1.0, sides=6)
        crystal(m, "CrystalDark", "CrystalGlow", x + side * 1.15, -0.5, 0.6, 6.2, 0.62, lean=(side * 0.9, -0.4), turn=0.4)
        crystal(m, "CrystalDark", "CrystalGlow", x + side * 0.5, -1.1, 0.6, 4.2, 0.5, lean=(side * 0.3, -0.7), turn=0.9)
        crystal(m, "Crystal", "CrystalGlow", x + side * 1.3, 0.8, 0.5, 3.4, 0.46, lean=(side * 0.7, 0.3), turn=0.2)
        for z in (2.6, 7.2):
            flat_ring(m, "Shine", x, 0, z, 1.25, 0.22, 0.22)
        # Shards reaching for the middle, not quite touching.
        beam(m, "CrystalDark", (x, 0, 7.9), (0, 0, 10.3), 1.5, 1.5, 0.6)
        gem(m, "Shine", side * 2.5, 0.2, 13.2, 0.42, 0.75, 0.75, sides=4)
        gem(m, "CrystalGlow", side * 5.6, -0.6, 11.4, 0.34, 0.6, 0.6, sides=4)
    gem(m, "CrystalGlow", 0, 0, 10.2, 0.75, 0.9, 0.9, sides=6)  # where the shards meet
    gem(m, "Shine", 0, 0, 13.0, 1.15, 2.1, 1.6, sides=6)
    flat_ring(m, "CrystalGlow", 0, 0, 13.0, 1.95, 0.18, 0.18)
    hooks(m)
    loaded_bar(m, (1.55, 1.3))
    dashed_circle(m)
    return m


def magma():
    """Rack 5: pulled up out of a volcano. Stacked basalt pillars split by lava, standing in pools of it, a fire in a
    brazier on each, black horns sweeping up from a crossbar that drips, and a burning heart held in the middle."""
    m = rack("Magma", Basalt="#3a3438", BasaltDark="#262226", Trim="#6b3a2a", Lava="#ff6a1a", Flame="#ffb52e", Ember="#ff3d1f",
             Horn="#1a171a", Hook="#262226", Bar="#d6c8bc", Plate="#1c181a")
    for side in (-1, 1):
        x = side * GAP
        disc(m, "Lava", x, -0.3, 0.03, 2.5, 0.06, sides=12)
        prism(m, "BasaltDark", x, -0.2, 0, 1.1, 2.0, 1.75, sides=6, turn=0.2)
        # Stacked drums, each turned and set a little off, so the pillar looks broken and rebuilt.
        z = 1.1
        for i, (h, r) in enumerate(((2.2, 1.5), (1.9, 1.32), (2.3, 1.42), (1.8, 1.22))):
            prism(m, "Basalt", x + side * (0.06 if i % 2 else -0.06), 0, z, z + h, r, r - 0.08, sides=6, turn=i * 0.5)
            m.block("Lava", x, 0, z + h, 2 * r - 0.5, 2 * r - 0.5, 0.16)  # the glowing seam between drums
            z += h
        limb(m, "Lava", [(x + side * 0.3, 1.27, 8.8), (x - side * 0.2, 1.3, 7.2), (x + side * 0.35, 1.32, 5.9), (x - side * 0.1, 1.34, 4.4),
                         (x + side * 0.25, 1.36, 3.0), (x, 1.4, 1.4)], 0.34, 0.16)
        prism(m, "Trim", x, 0, 9.3, 10.1, 1.05, 1.7, sides=8)  # the brazier
        prism(m, "BasaltDark", x, 0, 10.1, 10.3, 1.7, 1.7, sides=8)
        prism(m, "Lava", x, 0, 10.3, 10.42, 1.4, 1.4, sides=8)
        gem(m, "Ember", x, 0, 10.5, 1.1, 2.0, 0.1, sides=6)
        gem(m, "Flame", x, 0, 10.5, 0.75, 3.2, 0.1, sides=6, turn=0.5)
        limb(m, "Horn", [(side * 2.1, 0, 9.5), (side * 2.0, 0.2, 11.2), (side * 1.5, 0.4, 12.6), (side * 0.6, 0.6, 13.8)], 0.95, 0.1)
    m.block("BasaltDark", 0, 0, 9.0, 2 * GAP, 1.5, 1.1)
    m.block("Lava", 0, 0.78, 9.0, 5.4, 0.1, 0.22)
    for x, length in ((-2.2, 1.0), (-0.9, 1.5), (0.9, 1.3), (2.3, 0.8)):  # drips, high enough to clear the lifter's head
        m.loft_z("Lava", (8.5, x, 0.3, 0.34, 0.34), (8.5 - length, x, 0.3, 0.1, 0.1))
    gem(m, "Ember", 0, 0, 10.9, 0.95, 1.4, 1.4, sides=6)  # the heart
    gem(m, "Flame", 0, 0.1, 10.9, 0.55, 1.0, 1.0, sides=6, turn=0.5)
    hooks(m)
    loaded_bar(m, (1.65, 1.4, 1.1))
    dashed_circle(m)
    return m


def titan():
    """Rack 6, the last: a throne for a squat. Gold columns on marble steps, red banners, gems set in rings, and over
    the arch a crowned monster's head spreading golden wings. It should be obvious from across the arena."""
    m = rack("Titan", Frame="#ffc72e", FrameDark="#d1921a", Marble="#f1ecf5", MarbleDark="#c6bdd2", Banner="#c81f3a", BannerTrim="#ffe27a",
             Wing="#ffd95a", WingDark="#e8a92a", Crown="#fff0a0", Shine="#ff3fa8", EyeGlow="#ff2a2a", Socket="#40101c", Teeth="#fffbe8",
             Hook="#d1921a", Bar="#fff0b8", Plate="#ffc72e")
    top = 11.8
    for side in (-1, 1):
        x = side * GAP
        m.block("MarbleDark", x, -0.1, 0.4, 3.6, 4.6, 0.8)
        m.block("Marble", x, -0.1, 1.05, 2.9, 3.8, 0.5)
        prism(m, "FrameDark", x, 0, 1.3, 1.9, 1.3, 1.1, sides=12)
        prism(m, "Frame", x, 0, 1.9, top - 0.8, 0.98, 0.86, sides=12)
        prism(m, "FrameDark", x, 0, top - 0.8, top - 0.1, 0.9, 1.35, sides=12)
        for z in (4.0, 8.0):  # gem rings
            prism(m, "FrameDark", x, 0, z - 0.2, z + 0.2, 1.08, 1.08, sides=12)
            for i in range(6):
                a = i * math.tau / 6 + 0.26
                gem(m, "Shine", x + 1.1 * math.cos(a), 1.1 * math.sin(a), z, 0.2, 0.26, 0.26, sides=4)
        # A banner down the outside of each column.
        bx = x + side * 1.08
        m.block("BannerTrim", bx, 0, top - 2.0, 0.14, 2.0, 0.3)
        m.block("Banner", bx, 0, top - 4.2, 0.1, 1.7, 4.2)
        m.loft_z("Banner", (top - 6.3, bx, 0, 0.1, 1.7), (top - 7.2, bx, 0, 0.1, 0.1))
        m.block("BannerTrim", bx + side * 0.04, 0, top - 4.0, 0.08, 0.6, 0.6)
    m.block("MarbleDark", 0, 0, top + 0.1, 2 * GAP + 3.0, 1.9, 0.5)
    m.block("Frame", 0, 0, top + 0.6, 2 * GAP + 2.4, 1.5, 0.7)
    for i in range(-3, 4):
        gem(m, "Shine", i * 1.3, 0.8, top + 0.6, 0.2, 0.26, 0.26, sides=4)

    # The crest: a golden monster's head.
    hz = top + 2.9
    ball(m, "Frame", 0, 0, hz, 1.75, sides=10, rings=6)
    m.loft_y("Frame", (0.8, 0, hz - 0.5, 2.7, 2.0), (3.0, 0, hz - 0.8, 1.7, 1.1))
    m.loft_y("FrameDark", (0.7, 0, hz - 1.6, 2.5, 0.6), (2.6, 0, hz - 1.75, 1.5, 0.3))
    for side in (-1, 1):
        m.block("Socket", side * 0.78, 1.42, hz + 0.25, 0.9, 0.5, 0.62)
        m.block("EyeGlow", side * 0.78, 1.66, hz + 0.25, 0.54, 0.16, 0.36)
        m.block("Socket", side * 0.34, 2.98, hz - 0.62, 0.24, 0.14, 0.28)
        limb(m, "FrameDark", [(side * 1.2, 0, hz + 1.0), (side * 2.3, -0.2, hz + 1.9), (side * 2.5, -0.1, hz + 3.1)], 0.6, 0.08)
    for i in range(5):
        x = -0.78 + i * 0.39
        m.loft_z("Teeth", (hz - 1.3, x, 2.6, 0.3, 0.26), (hz - 1.85, x, 2.6, 0.06, 0.06))
    prism(m, "Crown", 0, 0, hz + 1.45, hz + 2.1, 1.25, 1.4, sides=10)  # the crown
    for i in range(5):
        a = math.pi * (0.1 + 0.2 * i)
        cx, cy = 1.3 * math.cos(a), 1.3 * math.sin(a)
        m.loft_z("Crown", (hz + 2.1, cx, cy, 0.62, 0.62), (hz + 3.0, cx, cy, 0.06, 0.06))
    gem(m, "Shine", 0, 1.42, hz + 1.78, 0.28, 0.34, 0.34, sides=4)

    # The wings, one long feather at a time, fanning out from behind the head.
    for side in (-1, 1):
        root = (side * 1.3, -0.5, hz - 0.2)
        for i in range(6):
            angle = math.radians(8 + i * 13)
            length = 7.4 - i * 0.6
            tip = (root[0] + side * length * math.cos(angle), -0.5 - i * 0.05, root[2] + length * math.sin(angle))
            across = (-side * math.sin(angle), 0, math.cos(angle))  # feathers are broad in the wing's plane, and taper
            plate(m, "Wing" if i % 2 == 0 else "WingDark", root, tip, across, 1.5, 0.45, 0.32)
    hooks(m)
    loaded_bar(m, (1.8, 1.55, 1.25))
    dashed_circle(m)
    return m


ALL = [iron, bone, crystal_rack, magma, titan]  # studio_tidy.py reads this


def main():
    scene = kit.setup_scene()
    kit.RENDERS = RENDERS
    RENDERS.mkdir(parents=True, exist_ok=True)
    base = bpy.data.collections.new("Base")  # export_fbx.py makes one file per model in here
    stage = bpy.data.collections.new("Preview stage")
    for col in (base, stage):
        scene.collection.children.link(col)

    models = [make() for make in ALL]
    roots = [model.build(base) for model in models]

    ground = bpy.data.meshes.new("Ground")
    ground.from_pydata([(-90, -60, -0.01), (90, -60, -0.01), (90, 60, -0.01), (-90, 60, -0.01)], [], [(0, 1, 2, 3)])
    ground.materials.append(kit.material("Ground", "#4cc425", False))
    stage.objects.link(bpy.data.objects.new("Ground", ground))
    player_root = mk.player_block(stage)
    first = squat_rack().build(stage)  # rack 1, to compare in the renders; not exported

    everything = [first, player_root, *roots]
    mk.light_up(roots, GLOW_ROLES)
    for model, root in zip(models, roots):
        player_root.location = (0, 0, 0)
        bpy.context.view_layer.update()
        mk.set_visible(everything, [root, player_root])
        low, high = kit.bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 8)
        kit.shoot(scene, model.name, centre + Vector((0.6, 1.0, 0.32)) * reach * 1.25, centre, (760, 760), 50)
        kit.shoot(scene, f"{model.name}_lifter_view", (0, -13, 7.5), (0, 8, 5.5), (760, 480), 35)

    # All six in a row, in the order players earn them.
    mk.set_visible(everything, [first, *roots])
    row = [first, *roots]
    for i, root in enumerate(row):
        root.location = ((2.5 - i) * 17, 0, 0)  # the camera looks back along -Y, so this reads left to right
    bpy.context.view_layer.update()
    kit.shoot(scene, "all_racks", (0, 135, 34), (0, 0, 8), (1500, 560), 40)
    for root in row:
        root.location = (0, 0, 0)

    mk.light_up(roots, GLOW_ROLES, 0)
    mk.set_visible(everything, everything)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "racks.blend"))
    print("saved", HERE / "racks.blend")
    for model, root in zip(models, roots):
        low, high = kit.bounds(root)
        print(f"  {model.name}: x {low.x:.1f}..{high.x:.1f} y {low.y:.1f}..{high.y:.1f} top {high.z:.1f} roles {sorted(model.parts)}")


if __name__ == "__main__":
    main()
