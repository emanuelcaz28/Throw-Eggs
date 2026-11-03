"""Builds the first map's animals and props and renders them (run with Blender in background mode).

    Blender -b -P build_forest.py

Saves forest_models.blend and renders to design/world/models/.

The style is in docs/GAME_SPEC.md section 8a: chunky simple shapes, with the effort in the faces.
Each model is an Empty with one mesh per colour role under it, because a Roblox MeshPart has one
colour. A mutation can then recolour Body, Accent and Belly and leave the face alone. No studs are
modelled, but every mesh has UVs laid out so a stud image repeats evenly once it's in Studio. The
stud look in these renders is a preview only.

1 Blender unit = 1 stud at the first map's size. Models face +Y (Roblox -Z), feet at Z = 0.
"""
import math
import random
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path("/Users/emanuel/Documents/throw-eggs/assets/models")
RENDERS = HERE.parent.parent / "design" / "world" / "models"

STUDS_PER_UNIT = 2  # how many times the stud image repeats per stud of model
NO_STUDS = {"EyeWhite", "Pupil", "Highlight", "Mouth", "Tongue", "Teeth"}  # keeps faces clean

FACE_COLOURS = {
    "EyeWhite": "#ffffff",
    "Pupil": "#17141f",
    "Highlight": "#ffffff",
    "Mouth": "#4a1a26",
    "Tongue": "#f0627f",
    "Teeth": "#fffaf0",
}

# Mutations recolour these roles only.
MUTATION_ROLES = {"Body": 1.0, "Accent": 0.72, "Belly": 1.25, "Claw": 0.6}
MUTATIONS = {"Gold": "#ffc628", "Diamond": "#7fdcff"}


def srgb_to_linear(hex_colour):
    h = hex_colour.lstrip("#")
    out = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return out


class Model:
    """Collects blocks per colour role, then turns them into meshes."""

    def __init__(self, name, colours):
        self.name = name
        self.colours = {**FACE_COLOURS, **colours}
        self.parts = {}
        self.head_centre = None
        self.bone = "Spine"  # blocks added now move with this bone
        self.groups = {}  # per role, the bone of each vertex
        self.joints = {}  # bone name -> (pivot, parent name)

    def joint(self, name, pivot, parent="Root"):
        self.joints[name] = (pivot, parent)

    def use(self, name, pivot, parent="Spine"):
        """Declares a bone and puts the next blocks on it."""
        self.joint(name, pivot, parent)
        self.bone = name

    def stretch(self, role, bone):
        """The last block's first end stays with this bone, so it bends instead of opening a gap."""
        self.groups[role][-8:-4] = [bone] * 4

    def head_joint(self, yc, d, zc, h):
        self.use("Head", (0, yc - d * 0.2, zc - h * 0.4), "Neck" if "Neck" in self.joints else "Spine")

    def _add(self, role, verts, faces):
        part_verts, part_faces = self.parts.setdefault(role, ([], []))
        start = len(part_verts)
        part_verts.extend(verts)
        part_faces.extend([[start + i for i in face] for face in faces])
        self.groups.setdefault(role, []).extend([self.bone] * len(verts))

    def _ring_shape(self, role, ring_a, ring_b):
        faces = [[0, 1, 2, 3], [7, 6, 5, 4]]
        for i in range(4):
            faces.append([i, i + 4, (i + 1) % 4 + 4, (i + 1) % 4])
        self._add(role, ring_a + ring_b, faces)

    def loft_y(self, role, a, b):
        """From one rectangle to another along Y. a and b are (y, centre x, centre z, width, height)."""
        def ring(y, cx, cz, w, h):
            return [(cx - w / 2, y, cz - h / 2), (cx + w / 2, y, cz - h / 2), (cx + w / 2, y, cz + h / 2), (cx - w / 2, y, cz + h / 2)]
        self._ring_shape(role, ring(*a), ring(*b))

    def loft_z(self, role, a, b):
        """Along Z. a and b are (z, centre x, centre y, width, depth)."""
        def ring(z, cx, cy, w, d):
            return [(cx - w / 2, cy - d / 2, z), (cx + w / 2, cy - d / 2, z), (cx + w / 2, cy + d / 2, z), (cx - w / 2, cy + d / 2, z)]
        self._ring_shape(role, ring(*a), ring(*b))

    def loft_x(self, role, a, b):
        """Along X. a and b are (x, centre y, centre z, depth, height)."""
        def ring(x, cy, cz, d, h):
            return [(x, cy - d / 2, cz - h / 2), (x, cy + d / 2, cz - h / 2), (x, cy + d / 2, cz + h / 2), (x, cy - d / 2, cz + h / 2)]
        self._ring_shape(role, ring(*a), ring(*b))

    def block(self, role, x, y, z, w, d, h):
        """A plain block around a centre point."""
        self.loft_y(role, (y - d / 2, x, z, w, h), (y + d / 2, x, z, w, h))

    def build_armature(self, parent):
        armature = bpy.data.armatures.new(self.name)
        root = bpy.data.objects.new(self.name, armature)
        parent.objects.link(root)
        bpy.context.view_layer.objects.active = root
        bpy.ops.object.mode_set(mode="EDIT")
        # Every bone points along +Y, so in pose mode X is pitch, Y is roll and Z is yaw.
        bones = {}
        for name, (pivot, _) in {"Root": ((0, 0, 0), None), **self.joints}.items():
            bone = armature.edit_bones.new(name)
            bone.head = pivot
            bone.tail = (pivot[0], pivot[1] + 0.3, pivot[2])
            bones[name] = bone
        for name, (_, parent_name) in self.joints.items():
            bones[name].parent = bones[parent_name]
        bpy.ops.object.mode_set(mode="OBJECT")
        return root

    def build(self, parent):
        if self.joints:
            root = self.build_armature(parent)
        else:
            root = bpy.data.objects.new(self.name, None)
            root.empty_display_size = 0.5
            parent.objects.link(root)
        for role, (verts, faces) in self.parts.items():
            mesh = bpy.data.meshes.new(f"{self.name}_{role}")
            mesh.from_pydata(verts, [], faces)
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(mesh)
            bm.free()
            mesh.update()
            lay_out_uvs(mesh)
            mesh.materials.append(material(f"{self.name}_{role}", self.colours[role], role not in NO_STUDS))
            obj = bpy.data.objects.new(f"{self.name}_{role}", mesh)
            parent.objects.link(obj)
            obj.parent = root
            if self.joints:
                for index, bone in enumerate(self.groups[role]):
                    group = obj.vertex_groups.get(bone) or obj.vertex_groups.new(name=bone)
                    group.add([index], 1.0, "REPLACE")
                obj.modifiers.new("Armature", "ARMATURE").object = root
        return root


def lay_out_uvs(mesh):
    """Box projection: each face takes its UVs from the two axes it lies along, so studs stay square."""
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for poly in mesh.polygons:
        n = poly.normal
        axis = max(range(3), key=lambda i: abs(n[i]))
        u_axis, v_axis = [(1, 2), (0, 2), (0, 1)][axis]
        for loop_index in poly.loop_indices:
            co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            uv_layer.data[loop_index].uv = (co[u_axis] * STUDS_PER_UNIT, co[v_axis] * STUDS_PER_UNIT)


def stud_image():
    """A small stud tile, for previewing how the Studio texture will sit on the UVs."""
    size = 64
    image = bpy.data.images.new("StudPreview", size, size)
    pixels = []
    for py in range(size):
        for px in range(size):
            dx, dy = (px + 0.5) / size - 0.5, (py + 0.5) / size - 0.5
            dist = math.hypot(dx, dy)
            value = 1.0
            if dist < 0.33:
                value = 1.08
                if dist > 0.25:
                    value = 0.8 if dx - dy > 0 else 1.18
            if max(abs(dx), abs(dy)) > 0.475:
                value = 0.93
            pixels.extend((value / 1.2, value / 1.2, value / 1.2, 1))
    image.pixels = pixels
    return image


_stud = None


def material(name, hex_colour, studs):
    global _stud
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.65
    rgb = nodes.new("ShaderNodeRGB")
    rgb.name = "Colour"
    rgb.outputs[0].default_value = (*srgb_to_linear(hex_colour), 1)
    if studs:
        if _stud is None:
            _stud = stud_image()
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = _stud
        multiply = nodes.new("ShaderNodeMixRGB")
        multiply.blend_type = "MULTIPLY"
        multiply.inputs[0].default_value = 1
        boost = nodes.new("ShaderNodeMath")
        boost.operation = "MULTIPLY"
        boost.inputs[1].default_value = 1.2
        links.new(tex.outputs["Color"], boost.inputs[0])
        links.new(rgb.outputs[0], multiply.inputs[1])
        links.new(boost.outputs[0], multiply.inputs[2])
        links.new(multiply.outputs[0], bsdf.inputs["Base Color"])
    else:
        links.new(rgb.outputs[0], bsdf.inputs["Base Color"])
    mat.diffuse_color = (*srgb_to_linear(hex_colour), 1)
    return mat


# ---------------------------------------------------------------------- faces


def eyes(m, half_width, front_y, z, size, lid=0.0, brow=None, brow_role="Accent", look=(0, 0), wrap=0.22):
    """Two big eyes on the skull's front corners, so they read from the front and the side.

    lid (0 to 1) drops an eyelid over the top. brow is the slope of the eyebrow, from back to front:
    negative frowns towards the nose, positive looks friendly or surprised. look shifts the pupils,
    per eye if look is a pair of pairs, which is how a derpy stare is made.
    """
    for side in (-1, 1):
        outer = side * (half_width + size * wrap)
        white_w = size * 0.9
        white_d = size
        white_h = size * 1.15
        cy = front_y - size * 0.3
        m.block("EyeWhite", outer - side * white_w / 2, cy, z, white_w, white_d, white_h)

        look_pair = look[0 if side < 0 else 1] if isinstance(look[0], tuple) else look
        px, pz = look_pair
        pupil_w, pupil_d, pupil_h = size * 0.68, size * 0.62, size * 0.74
        # The pupil sits over the corner, standing proud of both the side and the front.
        pupil_x = outer - side * (pupil_w / 2 - size * 0.04) + side * px * size
        pupil_y = cy + white_d / 2 - pupil_d / 2 + size * 0.04
        pupil_z = z + pz * size - size * 0.08
        m.block("Pupil", pupil_x, pupil_y, pupil_z, pupil_w, pupil_d, pupil_h)
        glint = size * 0.2
        m.block(
            "Highlight",
            pupil_x + side * (pupil_w / 2 - glint / 2 + size * 0.02),
            pupil_y + pupil_d / 2 - glint / 2 + size * 0.02,
            pupil_z + pupil_h / 2 - glint / 2 - size * 0.04,
            glint,
            glint,
            glint,
        )

        if lid > 0:
            lid_h = white_h * lid
            m.block("Body", outer - side * (white_w / 2 - size * 0.05), cy, z + white_h / 2 - lid_h / 2 + size * 0.04, white_w + size * 0.12, white_d + size * 0.12, lid_h)

        if brow is not None:
            top = z + white_h / 2
            brow_w = white_w + size * 0.12
            brow_h = size * 0.34
            brow_x = outer - side * brow_w / 2 + side * size * 0.06
            m.loft_y(
                brow_role,
                (cy - white_d * 0.5, brow_x, top - brow * size * 0.32, brow_w, brow_h),
                (cy + white_d * 0.58, brow_x, top + brow * size * 0.32, brow_w, brow_h),
            )


def jaws(m, front_y, mouth_z, skull_w, length, snout_w, upper_h, lower_h, gap, upper="Body", lower="Belly", tongue=True, grin=0.0, skull_d=1.0):
    """Upper and lower jaw with a dark mouth between them. grin lifts the mouth's corners back along the cheeks."""
    upper_z = mouth_z + gap / 2 + upper_h / 2
    lower_z = mouth_z - gap / 2 - lower_h / 2
    m.loft_y(upper, (front_y - 0.05, 0, upper_z + upper_h * 0.1, skull_w * 0.94, upper_h * 1.2), (front_y + length, 0, upper_z, snout_w, upper_h))
    m.loft_y(lower, (front_y - 0.05, 0, lower_z, skull_w * 0.85, lower_h), (front_y + length * 0.92, 0, lower_z, snout_w * 0.9, lower_h))
    m.block("Mouth", 0, front_y + length * 0.42, mouth_z, snout_w * 0.84, length * 0.95, gap + lower_h * 0.3)
    if tongue and gap > 0.05:
        tongue_h = gap * 0.45
        m.block("Tongue", 0, front_y + length * 0.42, mouth_z - gap / 2 + tongue_h / 2, snout_w * 0.5, length * 0.7, tongue_h)
    if grin:
        # A dark line along each cheek, rising towards the back.
        line_h = max(gap, 0.05) * 0.8
        for side in (-1, 1):
            x = side * (skull_w / 2 + 0.005)
            m.loft_y("Mouth", (front_y - skull_d * 0.38, x, mouth_z + grin, 0.04, line_h * 0.7), (front_y + 0.02, x, mouth_z, 0.04, line_h))


def teeth(m, positions, z, size, role="Teeth"):
    """Pointed teeth hanging down. positions are (x, y) under the upper jaw's edge."""
    for x, y in positions:
        m.loft_z(role, (z - size, x, y, size * 0.15, size * 0.15), (z, x, y, size, size))


def nostrils(m, y, z, spread, size=0.12):
    for side in (-1, 1):
        m.block("Mouth", side * spread, y, z, size, size, size * 0.7)


def spikes_along_y(m, role, spots):
    """Little triangle-ish fins. spots are (y, z, height, length)."""
    for y, z, height, length in spots:
        m.loft_z(role, (z, 0, y, 0.25, length), (z + height, 0, y - length * 0.15, 0.12, length * 0.25))


def biped_legs(m, x, hip_y, hip_z, thigh_w, thigh_h, shin_w, foot_len, foot_h=0.3, claw=True):
    for side in (-1, 1):
        sx = side * x
        shin_top = hip_z - thigh_h * 0.65
        letter = "L" if side < 0 else "R"
        m.use(f"Leg{letter}", (sx, hip_y, hip_z))
        m.loft_z("Body", (hip_z - thigh_h, sx, hip_y, thigh_w * 0.72, thigh_w * 0.9), (hip_z + thigh_h * 0.2, sx, hip_y + thigh_w * 0.1, thigh_w, thigh_w * 1.25))
        m.use(f"Shin{letter}", (sx, hip_y, shin_top), f"Leg{letter}")
        m.loft_z("Body", (foot_h * 0.5, sx, hip_y - shin_w * 0.1, shin_w, shin_w), (shin_top, sx, hip_y, shin_w * 1.15, shin_w * 1.2))
        m.block("Belly", sx, hip_y + foot_len * 0.22, foot_h / 2, shin_w * 1.5, foot_len, foot_h)
        if claw:
            for offset in (-0.32, 0.32):
                c = shin_w * 0.36
                m.block("Claw", sx + offset * shin_w * 1.2, hip_y + foot_len * 0.72 + c * 0.2, foot_h * 0.4, c, c * 1.3, foot_h * 0.8)
    m.bone = "Spine"


def tail(m, start, end, segments, role="Body"):
    """A tail that thins out. start and end are (y, z, width, height)."""
    for i in range(segments):
        t0, t1 = i / segments, (i + 1) / segments
        a = [start[k] + (end[k] - start[k]) * t0 for k in range(4)]
        b = [start[k] + (end[k] - start[k]) * t1 for k in range(4)]
        m.use(f"Tail{i + 1}", (0, a[0], a[1]), f"Tail{i}" if i else "Spine")
        m.loft_y(role, (b[0], 0, b[1], b[2], b[3]), (a[0], 0, a[1], a[2], a[3]))
        if i < segments - 1:
            m.stretch(role, f"Tail{i + 2}")
    m.bone = "Spine"


# ---------------------------------------------------------------------- animals


def compy():
    """Tiny, huge-eyed and delighted to see you."""
    m = Model("dino_Compy", {"Body": "#7ed957", "Accent": "#3fa84a", "Belly": "#e7f5b5", "Claw": "#3b6b2a"})
    m.joint("Spine", (0, -0.15, 1.4))
    biped_legs(m, 0.42, -0.15, 1.0, 0.62, 0.72, 0.28, 0.75, 0.2)
    m.loft_y("Body", (-0.85, 0, 1.3, 0.85, 0.85), (0.55, 0, 1.45, 1.1, 1.2))
    m.loft_y("Belly", (-0.45, 0, 1.08, 0.75, 0.5), (0.58, 0, 1.2, 0.9, 0.72))
    tail(m, (-0.8, 1.32, 0.68, 0.62), (-2.0, 1.75, 0.14, 0.14), 2)
    for y in (-0.6, -0.1):
        m.block("Accent", 0, y, 1.82, 0.7, 0.26, 0.14)
    m.bone = "Tail1"
    m.block("Accent", 0, -1.25, 1.55, 0.4, 0.22, 0.3)
    for side in (-1, 1):
        m.use("ArmL" if side < 0 else "ArmR", (side * 0.62, 0.35, 1.28))
        m.block("Body", side * 0.62, 0.55, 1.28, 0.16, 0.5, 0.18)
        m.block("Claw", side * 0.62, 0.84, 1.28, 0.14, 0.14, 0.14)

    w, d, h = 1.55, 1.3, 1.25
    yc, zc = 0.72, 2.5
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    jaws(m, front, zc - 0.34, w, 0.62, 1.15, 0.4, 0.24, 0.2, grin=0.2, skull_d=d)
    eyes(m, w / 2, front, zc + 0.22, 0.8, brow=None, look=(0, 0.02))
    nostrils(m, front + 0.5, zc - 0.03, 0.25, 0.1)
    teeth(m, [(-0.2, front + 0.56), (0.2, front + 0.56)], zc - 0.25, 0.14)
    spikes_along_y(m, "Accent", [(yc + 0.3, zc + h / 2, 0.32, 0.42), (yc - 0.2, zc + h / 2, 0.42, 0.45), (yc - 0.62, zc + h / 2 - 0.1, 0.32, 0.38)])
    m.head_centre = (0, front + 0.1, zc)
    return m


def gallimimus():
    """All legs and neck, and never quite sure what's going on: the eyes don't agree."""
    m = Model("dino_Gallimimus", {"Body": "#ffcf4d", "Accent": "#f07f2e", "Belly": "#fff0be", "Claw": "#a85a1f"})
    m.joint("Spine", (0, -0.1, 3.4))
    biped_legs(m, 0.5, -0.1, 3.0, 0.72, 1.1, 0.26, 1.05, 0.22)
    m.loft_y("Body", (-1.15, 0, 3.4, 0.9, 0.9), (0.8, 0, 3.7, 1.3, 1.45))
    m.loft_y("Belly", (-0.5, 0, 3.05, 0.9, 0.55), (0.82, 0, 3.32, 1.05, 0.75))
    tail(m, (-1.1, 3.42, 0.75, 0.7), (-2.9, 3.85, 0.18, 0.18), 3)
    m.bone = "Tail3"
    m.loft_y("Accent", (-3.5, 0, 4.05, 0.1, 0.1), (-2.6, 0, 3.82, 0.5, 0.55))
    m.bone = "Spine"
    for side in (-1, 1):
        m.loft_x("Accent", (side * 0.65, 0.55, 3.65, 0.75, 0.55), (side * 0.9, 0.3, 3.45, 0.95, 0.2))
    m.use("Neck", (0, 0.7, 3.9))
    m.loft_z("Body", (3.9, 0, 0.7, 0.72, 0.8), (5.8, 0, 1.25, 0.38, 0.42))
    m.stretch("Body", "Spine")
    m.loft_z("Belly", (3.9, 0, 0.98, 0.42, 0.28), (5.8, 0, 1.42, 0.24, 0.14))
    m.stretch("Belly", "Spine")

    w, d, h = 1.05, 1.05, 0.9
    yc, zc = 1.4, 6.15
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    # A beak in place of teeth, slightly open.
    jaws(m, front, zc - 0.26, w, 0.95, 0.58, 0.26, 0.15, 0.09, upper="Accent", lower="Accent", tongue=False, grin=0.1, skull_d=d)
    eyes(m, w / 2, front, zc + 0.14, 0.62, brow=None, look=((0.0, 0.14), (0.0, -0.12)))
    for z, length in ((zc + 0.45, 0.5), (zc + 0.28, 0.7), (zc + 0.05, 0.55)):
        m.loft_y("Accent", (yc - d / 2 - length, 0, z + 0.14, 0.12, 0.1), (yc - d / 2 + 0.1, 0, z, 0.4, 0.22))
    nostrils(m, front + 0.6, zc - 0.1, 0.13, 0.07)
    m.head_centre = (0, front + 0.15, zc)
    return m


def parasaurolophus():
    """A big gentle sleepyhead with a smile and a great curved crest."""
    m = Model("dino_Parasaurolophus", {"Body": "#46c7b8", "Accent": "#ff9a3d", "Belly": "#d6f7e6", "Claw": "#1e7d78"})
    m.joint("Spine", (0, -0.5, 2.9))
    biped_legs(m, 0.72, -0.5, 2.4, 1.15, 1.25, 0.55, 1.4, 0.3)
    m.loft_y("Body", (-1.9, 0, 3.0, 1.35, 1.4), (1.05, 0, 3.55, 1.9, 2.1))
    m.loft_y("Belly", (-0.9, 0, 2.42, 1.3, 0.75), (1.1, 0, 2.85, 1.6, 1.0))
    tail(m, (-1.85, 3.02, 1.15, 1.15), (-5.0, 3.1, 0.2, 0.2), 3)
    for y, depth in ((-1.2, 0.5), (-0.3, 0.6), (0.6, 0.5)):
        m.block("Accent", 0, y, 4.45 if y > 0 else 4.15 if y > -1 else 3.8, 1.3, depth, 0.14)
    m.bone = "Tail1"
    m.block("Accent", 0, -2.6, 3.55, 0.7, 0.45, 0.14)
    for side in (-1, 1):
        m.use("ArmL" if side < 0 else "ArmR", (side * 0.98, 1.1, 2.9))
        m.loft_z("Body", (1.65, side * 0.98, 1.4, 0.26, 0.26), (2.9, side * 0.98, 1.1, 0.4, 0.5))
        m.block("Claw", side * 0.98, 1.5, 1.6, 0.3, 0.42, 0.14)
    m.use("Neck", (0, 1.1, 4.1))
    m.loft_z("Body", (4.1, 0, 1.1, 1.3, 1.45), (5.75, 0, 1.75, 0.82, 0.9))
    m.stretch("Body", "Spine")
    m.loft_z("Belly", (4.1, 0, 1.68, 0.8, 0.34), (5.75, 0, 2.16, 0.5, 0.14))
    m.stretch("Belly", "Spine")

    w, d, h = 1.5, 1.55, 1.25
    yc, zc = 1.95, 6.1
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    # A wide, flat duck bill.
    jaws(m, front, zc - 0.36, w, 1.05, 1.28, 0.3, 0.2, 0.09, lower="Belly", tongue=False, grin=0.28, skull_d=d)
    m.block("Belly", 0, front + 0.9, zc - 0.17, 1.3, 0.34, 0.2)
    eyes(m, w / 2, front, zc + 0.2, 0.78, lid=0.42, look=(0, -0.05))
    nostrils(m, front + 0.72, zc - 0.02, 0.28, 0.12)
    # The crest sweeps up and back from the top of the head.
    m.loft_y("Accent", (yc - 0.35, 0, zc + 0.88, 0.78, 0.65), (yc + 0.6, 0, zc + 0.5, 0.82, 0.42))
    m.loft_y("Accent", (yc - 1.35, 0, zc + 1.48, 0.62, 0.55), (yc - 0.3, 0, zc + 0.9, 0.76, 0.65))
    m.loft_y("Accent", (yc - 2.25, 0, zc + 2.1, 0.32, 0.26), (yc - 1.3, 0, zc + 1.48, 0.62, 0.55))
    m.head_centre = (0, front + 0.2, zc)
    return m


def stegosaurus():
    """A wide, low, cheerful tank with a tiny head that's nearly all eyes and smile."""
    m = Model("dino_Stegosaurus", {"Body": "#6cc24a", "Accent": "#ff7a45", "Belly": "#d9f2a8", "Claw": "#3e7d2c"})
    m.joint("Spine", (0, 0, 2.8))
    m.loft_y("Body", (-3.2, 0, 2.55, 1.9, 2.0), (-0.4, 0, 3.05, 3.1, 3.1))
    m.loft_y("Body", (-0.42, 0, 3.05, 3.1, 3.1), (2.6, 0, 2.3, 2.1, 1.9))
    m.loft_y("Belly", (-2.8, 0, 1.45, 1.6, 0.5), (2.4, 0, 1.42, 1.8, 0.45))
    tail(m, (-3.1, 2.55, 1.45, 1.4), (-6.5, 3.05, 0.26, 0.26), 3)
    for x, y in ((-1.1, 1.65), (1.1, 1.65), (-1.15, -1.75), (1.15, -1.75)):
        big = y < 0
        m.use(("Back" if big else "Front") + ("L" if x < 0 else "R"), (x, y, 2.0))
        m.loft_z("Body", (0.32, x, y, 0.8, 0.8), (1.85 if not big else 2.15, x, y, 1.0 if not big else 1.2, 1.0 if not big else 1.3))
        m.block("Belly", x, y + 0.12, 0.16, 1.02, 1.1, 0.32)
        for offset in (-0.28, 0, 0.28):
            m.block("Claw", x + offset, y + 0.68, 0.12, 0.16, 0.16, 0.2)

    # Plates down the back, biggest over the hips.
    m.bone = "Spine"
    plates = [(1.9, 3.1, 0.65), (0.95, 3.85, 1.0), (-0.1, 4.45, 1.3), (-1.2, 4.3, 1.42), (-2.3, 3.5, 1.15), (-3.3, 3.25, 0.8), (-4.2, 3.1, 0.6)]
    for y, z, size in plates:
        m.bone = "Tail1" if y < -3.1 else "Spine"
        m.loft_z("Accent", (z - 0.3, 0, y, 0.34, size * 0.85), (z + size * 0.45, 0, y, 0.3, size * 0.95))
        m.loft_z("Accent", (z + size * 0.45, 0, y, 0.3, size * 0.95), (z + size * 1.05, 0, y - size * 0.05, 0.14, size * 0.2))
    # Tail spikes.
    m.bone = "Tail3"
    for side in (-1, 1):
        for y, z in ((-6.1, 2.98), (-5.3, 2.85)):
            m.loft_x("Teeth", (side * 0.2, y, z, 0.3, 0.3), (side * 1.25, y - 0.15, z + 0.48, 0.05, 0.05))

    m.use("Neck", (0, 2.5, 2.2))
    m.loft_y("Body", (2.5, 0, 2.2, 1.45, 1.35), (3.6, 0, 1.85, 0.95, 0.95))
    m.stretch("Body", "Spine")
    w, d, h = 1.28, 1.05, 1.05
    yc, zc = 3.95, 1.82
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    jaws(m, front, zc - 0.3, w, 0.5, 0.95, 0.32, 0.2, 0.13, tongue=True, grin=0.26, skull_d=d)
    eyes(m, w / 2, front, zc + 0.2, 0.74, brow=0.25, brow_role="Accent", look=(0, 0.02))
    nostrils(m, front + 0.38, zc - 0.05, 0.2, 0.09)
    m.head_centre = (0, front + 0.1, zc)
    return m


def velociraptor():
    """The troublemaker: frowning brows, a toothy grin and that big toe claw."""
    m = Model("dino_Velociraptor", {"Body": "#ff9838", "Accent": "#8a3fa6", "Belly": "#ffe2b0", "Claw": "#2a2030"})
    m.joint("Spine", (0, -0.55, 2.7))
    biped_legs(m, 0.55, -0.55, 2.2, 0.88, 1.0, 0.34, 1.05, 0.26)
    for side in (-1, 1):
        # The sickle claw, held up off the ground.
        m.bone = "ShinL" if side < 0 else "ShinR"
        m.loft_y("Claw", (-0.2, side * 0.55, 0.55, 0.16, 0.24), (0.12, side * 0.55, 0.85, 0.04, 0.04))
    m.bone = "Spine"
    m.loft_y("Body", (-1.6, 0, 2.55, 1.0, 1.0), (0.85, 0, 2.95, 1.45, 1.55))
    m.loft_y("Belly", (-0.8, 0, 2.2, 0.95, 0.5), (0.9, 0, 2.48, 1.2, 0.75))
    tail(m, (-1.55, 2.58, 0.85, 0.8), (-4.8, 3.0, 0.14, 0.14), 3)
    m.bone = "Tail3"
    m.loft_y("Accent", (-5.5, 0, 3.08, 0.08, 0.1), (-4.5, 0, 3.0, 0.7, 0.26))
    for y, length in ((0.45, 0.42), (-0.28, 0.42), (-1.0, 0.36), (-1.9, 0.3), (-2.7, 0.26)):
        z = 2.95 + y * 0.16 + 0.42 if y > -1.5 else 2.72 + (y + 1.9) * -0.13 + 0.26
        m.bone = "Tail1" if y < -1.5 else "Spine"
        m.block("Accent", 0, y, z, 1.15 if y > -1.5 else 0.68, length, 0.14)
    for side in (-1, 1):
        x = side * 0.78
        m.use("ArmL" if side < 0 else "ArmR", (x, 0.6, 2.85))
        m.loft_y("Body", (0.6, x, 2.85, 0.26, 0.3), (1.35, x, 2.42, 0.18, 0.2))
        m.loft_y("Accent", (0.55, x + side * 0.03, 2.62, 0.08, 0.1), (1.25, x + side * 0.03, 2.22, 0.08, 0.34))
        for offset in (-0.06, 0.06):
            m.loft_y("Claw", (1.32, x + offset, 2.4, 0.07, 0.1), (1.58, x + offset, 2.24, 0.03, 0.03))
    m.use("Neck", (0, 1.0, 3.35))
    m.loft_z("Body", (3.35, 0, 1.0, 1.0, 1.05), (4.2, 0, 1.35, 0.78, 0.82))
    m.stretch("Body", "Spine")

    w, d, h = 1.5, 1.55, 1.2
    yc, zc = 1.6, 4.55
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    length, snout = 1.15, 1.02
    mouth_z = zc - 0.4
    jaws(m, front, mouth_z, w, length, snout, 0.42, 0.24, 0.32, grin=0.32, skull_d=d)
    eyes(m, w / 2, front, zc + 0.22, 0.72, brow=-0.45, look=(0, -0.04))
    upper_edge = mouth_z + 0.16
    spots = []
    for side in (-1, 1):
        for y in (0.15, 0.48, 0.8):
            spots.append((side * (snout / 2 - 0.08), front + y))
        spots.append((side * 0.17, front + length - 0.08))
    teeth(m, spots, upper_edge, 0.2)
    for side in (-1, 1):
        m.loft_z("Teeth", (mouth_z - 0.16, side * (snout * 0.9 / 2 - 0.08), front + 0.62, 0.15, 0.15), (mouth_z + 0.01, side * (snout * 0.9 / 2 - 0.08), front + 0.62, 0.03, 0.03))
    nostrils(m, front + length - 0.2, mouth_z + 0.44, 0.27, 0.12)
    # A small head crest of feathers.
    for z, length_f in ((zc + 0.45, 0.8), (zc + 0.18, 1.0), (zc - 0.1, 0.72)):
        m.loft_y("Accent", (yc - d / 2 - length_f, 0, z + 0.32, 0.1, 0.1), (yc - d / 2 + 0.25, 0, z, 0.48, 0.26))
    m.head_centre = (0, front + 0.25, zc)
    return m


def pteranodon():
    """The rarest here: wings thrown wide, a long beak and a sly sideways look."""
    m = Model("dino_Pteranodon", {"Body": "#7c6bf0", "Accent": "#ff6f91", "Belly": "#e6e0ff", "Claw": "#3d2f91"})
    m.joint("Spine", (0, 0, 1.5))
    biped_legs(m, 0.42, -0.1, 1.25, 0.52, 0.72, 0.22, 0.75, 0.2)
    m.loft_z("Body", (1.1, 0, 0, 0.95, 0.9), (2.9, 0, 0.2, 1.25, 1.1))
    m.loft_z("Belly", (1.2, 0, 0.42, 0.65, 0.2), (2.75, 0, 0.72, 0.85, 0.16))
    m.loft_y("Body", (-0.9, 0, 1.4, 0.1, 0.1), (-0.3, 0, 1.55, 0.45, 0.4))
    # Wings: an arm bone along the top, with the skin hanging under it.
    for side in (-1, 1):
        letter = "L" if side < 0 else "R"
        m.use(f"Wing{letter}", (side * 0.55, 0.2, 2.72))
        m.loft_x("Body", (side * 0.55, 0.2, 2.72, 0.5, 0.42), (side * 2.9, 0.25, 3.5, 0.3, 0.28))
        m.loft_x("Accent", (side * 0.55, 0.1, 1.82, 0.12, 1.5), (side * 2.9, 0.1, 2.25, 0.12, 2.25))
        m.use(f"WingTip{letter}", (side * 2.85, 0.25, 3.5), f"Wing{letter}")
        m.loft_x("Body", (side * 2.85, 0.25, 3.5, 0.3, 0.28), (side * 6.8, 0.25, 2.5, 0.05, 0.08))
        m.stretch("Body", f"Wing{letter}")
        m.loft_x("Accent", (side * 2.85, 0.1, 2.25, 0.12, 2.25), (side * 6.7, 0.1, 2.42, 0.08, 0.08))
        m.stretch("Accent", f"Wing{letter}")
        m.bone = f"Wing{letter}"
        for y_off in (-0.1, 0.1):
            m.loft_z("Claw", (3.5, side * 2.95, 0.25 + y_off, 0.1, 0.1), (3.95, side * 3.0, 0.35 + y_off * 1.6, 0.03, 0.03))
    m.use("Neck", (0, 0.3, 2.8))
    m.loft_z("Body", (2.8, 0, 0.3, 0.72, 0.72), (3.75, 0, 0.75, 0.5, 0.5))
    m.stretch("Body", "Spine")

    w, d, h = 1.3, 1.25, 1.05
    yc, zc = 1.0, 4.25
    m.head_joint(yc, d, zc, h)
    front = yc + d / 2
    m.block("Body", 0, yc, zc, w, d, h)
    # The long beak, a smirk on it.
    jaws(m, front, zc - 0.28, w, 2.05, 0.3, 0.3, 0.16, 0.07, upper="Accent", lower="Accent", tongue=False, grin=0.3, skull_d=d)
    eyes(m, w / 2, front, zc + 0.16, 0.7, lid=0.28, brow=-0.3, look=(0.06, 0))
    # The crest runs far back from the skull.
    m.loft_y("Accent", (yc - 2.5, 0, zc + 0.85, 0.08, 0.14), (yc + 0.2, 0, zc + 0.38, 0.55, 0.62))
    nostrils(m, front + 0.75, zc - 0.03, 0.08, 0.06)
    m.head_centre = (0, front + 0.3, zc)
    return m


# ---------------------------------------------------------------------- props


def prop(name, **colours):
    return Model(f"prop_{name}", colours)


def cycad_tree(seed=3):
    """A fat trunk with fronds spraying out of the top: the map's signature tree."""
    m = prop("CycadTree", Trunk="#8a5a34", Frond="#6fd13f", Tip="#a6e84f")
    rng = random.Random(seed)
    m.loft_z("Trunk", (0, 0, 0, 3.2, 3.2), (4, 0, 0, 2.5, 2.5))
    m.loft_z("Trunk", (4, 0, 0, 2.5, 2.5), (9, 0, 0, 1.9, 1.9))
    m.block("Tip", 0, 0, 9.4, 2.4, 2.4, 1)
    for i in range(8):
        angle = i * math.pi / 4 + rng.uniform(-0.1, 0.1)
        dx, dy = math.cos(angle), math.sin(angle)
        length, width = rng.uniform(6.5, 8), rng.uniform(1.7, 2.2)
        spans = ((0.5, 10.1, 0.9, width), (length * 0.55, 11.2, 0.5, width * 1.1), (length, 8.7, 0.3, width * 0.25))
        for (d0, z0, t0, w0), (d1, z1, t1, w1) in zip(spans, spans[1:]):
            add_frond_segment(m, "Frond", dx, dy, d0, z0, t0, w0, d1, z1, t1, w1)
    return m


def add_frond_segment(m, role, dx, dy, d0, z0, t0, w0, d1, z1, t1, w1):
    """One stretch of a leaf running outwards in direction (dx, dy)."""
    px, py = -dy, dx
    verts = []
    for d, z, t, w in ((d0, z0, t0, w0), (d1, z1, t1, w1)):
        cx, cy = dx * d, dy * d
        for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            verts.append((cx + px * sx * w / 2, cy + py * sx * w / 2, z + sz * t / 2))
    faces = [[0, 1, 2, 3], [7, 6, 5, 4]]
    for i in range(4):
        faces.append([i, i + 4, (i + 1) % 4 + 4, (i + 1) % 4])
    m._add(role, verts, faces)


def block_tree(seed=5):
    """A chunky tree from big leaf cubes, for the rim. Big and readable from far away."""
    m = prop("BlockTree", Trunk="#8a5a34", Leaf="#7fd63c", LeafDark="#5cbb33")
    rng = random.Random(seed)
    m.loft_z("Trunk", (0, 0, 0, 3.4, 3.4), (11, 0, 0, 2.2, 2.2))
    m.loft_x("Trunk", (0.3, 0, 7.2, 1.5, 1.5), (3.8, 0, 9.5, 1, 1))
    m.loft_x("Trunk", (-0.3, 0, 8.5, 1.4, 1.4), (-3.4, 0, 10.8, 0.9, 0.9))
    m.block("Leaf", 0, 0, 14, 10, 10, 7)
    m.block("LeafDark", 0, 0, 10.9, 8, 8, 1.4)
    m.block("Leaf", 4.8, 1, 10.8, 6, 6, 4.2)
    m.block("LeafDark", 4.8, 1, 8.5, 4.6, 4.6, 0.9)
    m.block("Leaf", -4.4, -1, 12.2, 5, 5.5, 3.8)
    m.block("LeafDark", -4.4, -1, 10.1, 3.8, 4, 0.8)
    m.block("Leaf", rng.uniform(-1.5, 1.5), rng.uniform(-1.5, 1.5), 18.6, 5.5, 5.5, 2.6)
    return m


def fern(seed=9):
    """A low clump of fronds. Ferns are the valley's namesake, so they're everywhere."""
    m = prop("Fern", Frond="#5fc93a", Tip="#94e24c")
    rng = random.Random(seed)
    m.loft_z("Frond", (0, 0, 0, 1.6, 1.6), (1.6, 0, 0, 0.9, 0.9))
    m.block("Tip", 0, 0, 1.75, 0.7, 0.7, 0.4)
    for i in range(9):
        angle = i * 2 * math.pi / 9 + rng.uniform(-0.12, 0.12)
        dx, dy = math.cos(angle), math.sin(angle)
        length = rng.uniform(3.8, 5)
        width = rng.uniform(1.3, 1.7)
        rise = rng.uniform(1.9, 2.8)
        add_frond_segment(m, "Frond", dx, dy, 0.2, 0.7, 0.35, width * 0.55, length * 0.5, rise, 0.25, width)
        add_frond_segment(m, "Tip", dx, dy, length * 0.5, rise, 0.25, width, length, 0.5, 0.16, width * 0.25)
    return m


def hedge():
    """A stepped mound of grass, as on the corridor floor."""
    m = prop("Hedge", Grass="#74d84c", Top="#94e65f")
    m.block("Grass", 0, 0, 1.25, 12, 18, 2.5)
    m.block("Top", 0, 0, 3.25, 8, 12, 1.5)
    return m


def stump():
    m = prop("Stump", Bark="#8d4a2c", Rings="#e6bd7c", Sprout="#7fd63c")
    m.loft_z("Bark", (0, 0, 0, 4.4, 4.4), (2.4, 0, 0, 3.4, 3.4))
    m.block("Rings", 0, 0, 2.5, 3, 3, 0.2)
    m.block("Bark", 0, 0, 2.62, 1.2, 1.2, 0.08)
    for side, y in ((1, 0.5), (-1, -0.7)):
        m.loft_x("Bark", (side * 1.6, y, 0.45, 1.1, 0.9), (side * 3.2, y, 0.15, 0.5, 0.3))
    m.loft_z("Bark", (2.3, 1.1, 1.1, 0.25, 0.25), (3.2, 1.1, 1.1, 0.18, 0.18))
    m.block("Sprout", 1.5, 1.1, 3.25, 0.9, 0.5, 0.2)
    m.block("Sprout", 0.75, 1.1, 3.45, 0.8, 0.5, 0.2)
    return m


def rock():
    m = prop("Rock", Stone="#a4a7b0", Moss="#77c944")
    m.loft_z("Stone", (0, 0, 0, 5.5, 4.5), (3, 0.3, 0, 3.8, 3.2))
    m.loft_z("Stone", (0, -2.7, 0.8, 2.8, 2.6), (1.8, -2.5, 0.8, 1.6, 1.5))
    m.block("Moss", 0.3, 0, 3.08, 3.2, 2.6, 0.3)
    return m


def egg_shape(m, role, x, y, base_z, width, height, spots=None, seed=1):
    """A blocky egg: narrow at both ends, widest low down."""
    rows = ((0.0, 0.62), (0.18, 0.92), (0.45, 1.0), (0.75, 0.74), (1.0, 0.4))

    def scale_at(t):
        for (t0, s0), (t1, s1) in zip(rows, rows[1:]):
            if t <= t1:
                return s0 + (s1 - s0) * (t - t0) / (t1 - t0)
        return rows[-1][1]

    for (t0, s0), (t1, s1) in zip(rows, rows[1:]):
        m.loft_z(role, (base_z + height * t0, x, y, width * s0, width * s0), (base_z + height * t1, x, y, width * s1, width * s1))
    if spots:
        rng = random.Random(seed)
        for i in range(16):
            # Each speckle sits on one of the egg's four flat sides.
            t = rng.uniform(0.14, 0.82)
            half = width * scale_at(t) / 2
            along = rng.uniform(-0.7, 0.7) * half
            side = i % 4
            sx, sy = [(half, along), (-half, along), (along, half), (along, -half)][side]
            size = width * rng.uniform(0.07, 0.13)
            m.block(spots, x + sx, y + sy, base_z + height * t, size, size, size)


def rim_egg():
    """Our answer to the reference's rim pumpkins: a big speckled egg."""
    m = prop("RimEgg", Shell="#fff2d6", Speckle="#d98a4a", Grass="#7fd63c")
    m.block("Grass", 0, 0, 0.2, 5, 5, 0.4)
    egg_shape(m, "Shell", 0, 0, 0.3, 4, 5.2, "Speckle", 4)
    return m


def nest():
    """A straw nest with three eggs in it."""
    m = prop("Nest", Straw="#c79545", StrawDark="#a2762f", Shell="#fff2d6", Speckle="#6fb7c4")
    m.block("StrawDark", 0, 0, 0.3, 8, 8, 0.6)
    for side in (-1, 1):
        m.block("Straw", side * 4.2, 0, 0.6, 1.6, 6.5, 1.2)
        m.block("Straw", 0, side * 4.2, 0.6, 6.5, 1.6, 1.2)
        m.block("StrawDark", side * 3.2, side * 3.2, 0.5, 2, 2, 1)
        m.block("StrawDark", side * 3.2, -side * 3.2, 0.5, 2, 2, 1)
    egg_shape(m, "Shell", -1.6, -1.1, 0.5, 2.6, 3.4, "Speckle", 2)
    egg_shape(m, "Shell", 1.7, -0.8, 0.5, 2.5, 3.2, "Speckle", 3)
    egg_shape(m, "Shell", 0, 1.7, 0.5, 2.6, 3.4, "Speckle", 8)
    return m


def mushrooms():
    m = prop("Mushrooms", Stem="#f6e8cf", Cap="#ef5b4a", Spot="#fff7ea")
    for x, y, height, cap in ((0, 0, 2.2, 2.6), (1.9, 0.8, 1.2, 1.5), (-1.5, 1, 0.9, 1.2)):
        m.loft_z("Stem", (0, x, y, cap * 0.32, cap * 0.32), (height, x, y, cap * 0.26, cap * 0.26))
        m.loft_z("Cap", (height - 0.05, x, y, cap, cap), (height + cap * 0.4, x, y, cap * 0.55, cap * 0.55))
        m.block("Spot", x + cap * 0.12, y - cap * 0.1, height + cap * 0.41, cap * 0.18, cap * 0.18, cap * 0.05)
        m.block("Spot", x - cap * 0.13, y + cap * 0.1, height + cap * 0.41, cap * 0.13, cap * 0.13, cap * 0.05)
    return m


# ---------------------------------------------------------------------- animation

WALK_FRAMES = 30  # one full stride, at 30 frames a second
IDLE_FRAMES = 240  # the idle loop; the game holds idle for about 10 seconds by running it on


def pose_bone(armature, name, rotation=(0, 0, 0), location=None, frame=1):
    bone = armature.pose.bones.get(name)
    if not bone:
        return
    bone.rotation_mode = "XYZ"
    bone.rotation_euler = rotation
    bone.keyframe_insert("rotation_euler", frame=frame)
    if location is not None:
        bone.location = location
        bone.keyframe_insert("location", frame=frame)


def walk_pose(a, f):
    """Everything is a sine wave of the stride, so the last frame runs smoothly into the first."""
    p = 2 * math.pi * f / WALK_FRAMES
    sin = math.sin
    pose_bone(a, "Spine", (0.02 * sin(2 * p), 0.05 * sin(p), 0.05 * sin(p)), (0, 0, 0.07 * math.cos(2 * p)), f)
    for letter, phase in (("L", 0), ("R", math.pi)):
        q = p + phase
        pose_bone(a, f"Leg{letter}", (0.45 * sin(q), 0, 0), None, f)
        pose_bone(a, f"Shin{letter}", (-0.6 * (0.5 + 0.5 * math.cos(q)) ** 2, 0, 0), None, f)
        pose_bone(a, f"Arm{letter}", (-0.3 * sin(q), 0, 0), None, f)
        side = -1 if letter == "L" else 1
        pose_bone(a, f"Wing{letter}", (0, side * 0.14 * sin(2 * p), 0), None, f)
        pose_bone(a, f"WingTip{letter}", (0, side * 0.1 * sin(2 * p - 0.8), 0), None, f)
    # Four-legged walkers move opposite corners together.
    for name, phase in (("FrontL", 0), ("BackR", 0), ("FrontR", math.pi), ("BackL", math.pi)):
        pose_bone(a, name, (0.32 * sin(p + phase), 0, 0), None, f)
    for i in (1, 2, 3):
        pose_bone(a, f"Tail{i}", (0.03 * sin(2 * p - i * 0.6), 0, 0.16 * sin(p - i * 0.7)), None, f)
    pose_bone(a, "Neck", (0.05 * sin(2 * p + 0.5), 0, 0.05 * sin(p + 0.6)), None, f)
    pose_bone(a, "Head", (-0.06 * sin(2 * p + 0.5), 0, 0.08 * sin(p + 1.2)), None, f)


def idle_pose(a, f):
    """Standing: breathing, the head looking around, the tail swaying slowly."""
    t = 2 * math.pi * f / IDLE_FRAMES
    sin = math.sin
    pose_bone(a, "Spine", (0.025 * sin(4 * t), 0, 0), (0, 0, 0.03 * sin(4 * t)), f)
    for letter in "LR":
        side = -1 if letter == "L" else 1
        pose_bone(a, f"Arm{letter}", (0.08 * sin(4 * t + 0.5), 0, 0), None, f)
        pose_bone(a, f"Wing{letter}", (0, side * 0.07 * sin(4 * t), 0), None, f)
        pose_bone(a, f"WingTip{letter}", (0, side * 0.06 * sin(4 * t - 0.8), 0), None, f)
    for i in (1, 2, 3):
        pose_bone(a, f"Tail{i}", (0.02 * sin(4 * t - i * 0.5), 0, 0.14 * sin(2 * t - i * 0.6)), None, f)
    pose_bone(a, "Neck", (0.05 * sin(2 * t + 1), 0, 0.14 * sin(t)), None, f)
    pose_bone(a, "Head", (0.09 * sin(3 * t), 0, 0.36 * sin(t) + 0.08 * sin(3 * t)), None, f)


def add_action(armature, name, frames, pose, step):
    armature.animation_data_create()
    action = bpy.data.actions.new(f"{armature.name}_{name}")
    action.use_fake_user = True
    armature.animation_data.action = action
    for f in range(0, frames + 1, step):
        pose(armature, f)
    return action


def animate(armature):
    walk = add_action(armature, "Walk", WALK_FRAMES, walk_pose, 2)
    idle = add_action(armature, "Idle", IDLE_FRAMES, idle_pose, 4)
    return walk, idle


# ---------------------------------------------------------------------- scene and renders


def bounds(root):
    corners = []
    for child in root.children:
        for corner in child.bound_box:
            corners.append(child.matrix_world @ Vector(corner))
    low = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    high = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    return low, high


def set_visible(roots, shown):
    for root in roots:
        visible = root in shown
        for child in root.children:
            child.hide_render = not visible


def shoot(scene, name, position, target, size=(900, 900), lens=60):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.clip_end = 2000
    camera = bpy.data.objects.new(f"Cam_{name}", data)
    camera.location = Vector(position)
    scene.collection.objects.link(camera)
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.filepath = str(RENDERS / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera)


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "NONE"
    for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.eevee.taa_render_samples = 48
    scene.view_settings.view_transform = "Standard"

    world = bpy.data.worlds.new("Sky")
    world.use_nodes = True
    nodes, links = world.node_tree.nodes, world.node_tree.links
    ambient = nodes["Background"]
    ambient.inputs["Color"].default_value = (1, 1, 1, 1)
    ambient.inputs["Strength"].default_value = 0.8
    sky = nodes.new("ShaderNodeBackground")
    sky.inputs["Color"].default_value = (*srgb_to_linear("#8fd0ff"), 1)
    mix = nodes.new("ShaderNodeMixShader")
    path = nodes.new("ShaderNodeLightPath")
    links.new(path.outputs["Is Camera Ray"], mix.inputs[0])
    links.new(ambient.outputs[0], mix.inputs[1])
    links.new(sky.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], nodes["World Output"].inputs["Surface"])
    scene.world = world

    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 2.0
    sun.data.angle = math.radians(12)
    sun.rotation_euler = (math.radians(-50), math.radians(25), 0)
    scene.collection.objects.link(sun)
    return scene


def tint_mutation(animals, hex_colour):
    """Recolours each animal's skin roles for a preview, and returns how to undo it."""
    saved = []
    base = srgb_to_linear(hex_colour)
    for model in animals:
        for role, strength in MUTATION_ROLES.items():
            mat = bpy.data.materials.get(f"{model.name}_{role}")
            if not mat:
                continue
            node = mat.node_tree.nodes["Colour"]
            saved.append((node, tuple(node.outputs[0].default_value)))
            node.outputs[0].default_value = (*[min(c * strength, 1) for c in base], 1)
    return saved


def main():
    scene = setup_scene()
    RENDERS.mkdir(parents=True, exist_ok=True)

    animals_col = bpy.data.collections.new("Animals")
    props_col = bpy.data.collections.new("Props")
    stage_col = bpy.data.collections.new("Preview stage")
    for col in (animals_col, props_col, stage_col):
        scene.collection.children.link(col)

    animal_models = [compy(), gallimimus(), parasaurolophus(), stegosaurus(), velociraptor(), pteranodon()]
    prop_models = [cycad_tree(), block_tree(), fern(), hedge(), stump(), rock(), rim_egg(), nest(), mushrooms()]

    # Laid out in rows: animals along the X axis in a line, props behind them.
    x = 0
    animal_roots = []
    for model in animal_models:
        root = model.build(animals_col)
        root.location = (x, 0, 0)
        animal_roots.append(root)
        x += 18
    x = 0
    prop_roots = []
    for model in prop_models:
        root = model.build(props_col)
        root.location = (x, -40, 0)
        prop_roots.append(root)
        x += 24
    bpy.context.view_layer.update()

    # A ground and a 5.5 stud player, both only for the renders.
    ground_mesh = bpy.data.meshes.new("Ground")
    ground_mesh.from_pydata([(-300, -300, -0.01), (400, -300, -0.01), (400, 200, -0.01), (-300, 200, -0.01)], [], [(0, 1, 2, 3)])
    ground_mesh.materials.append(material("Ground", "#6ccf4a", False))
    ground = bpy.data.objects.new("Ground", ground_mesh)
    stage_col.objects.link(ground)
    player = Model("Player", {"Skin": "#3f4553"})
    player.block("Skin", 0, 0, 2.75, 2, 1, 5.5)
    player_root = player.build(stage_col)
    player_root.location = (-8, 0, 0)
    bpy.context.view_layer.update()

    everything = animal_roots + prop_roots + [player_root]

    for model, root in zip(animal_models, animal_roots):
        set_visible(everything, [root])
        low, high = bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 3)
        shoot(scene, f"{model.name}_full", centre + Vector((0.62, 0.85, 0.32)) * reach * 1.15, centre, (900, 900), 50)
        head = root.location + Vector(model.head_centre)
        head_size = 3.4 if model.name != "dino_Compy" else 3.0
        shoot(scene, f"{model.name}_face", head + Vector((0.55, 1.0, 0.16)) * head_size * 1.55, head, (700, 700), 50)
        shoot(scene, f"{model.name}_front", head + Vector((0, 1, 0.08)) * head_size * 1.7, head, (700, 700), 50)

    set_visible(everything, animal_roots + [player_root])
    lineup = ((41, 118, 22), (41, 0, 4), (1800, 700), 38)
    shoot(scene, "lineup", *lineup)

    for name, colour in MUTATIONS.items():
        saved = tint_mutation(animal_models, colour)
        shoot(scene, f"lineup_{name}", *lineup)
        for node, value in saved:
            node.outputs[0].default_value = value

    for model, root in zip(prop_models, prop_roots):
        player_root.location = root.location + Vector((-6 if model.name != "prop_BlockTree" else -9, 2, 0))
        bpy.context.view_layer.update()
        set_visible(everything, [root, player_root])
        low, high = bounds(root)
        centre = (low + high) / 2
        reach = max((high - low).length, 7)
        shoot(scene, model.name, centre + Vector((0.5, 0.9, 0.42)) * reach * 1.25, centre, (600, 600), 50)

    # The animation preview: the walk twice, then part of the idle, turned so the strides show.
    set_visible(everything, animal_roots)
    actions = [animate(root) for root in animal_roots]
    frames_dir = RENDERS / "anim_frames"
    frames_dir.mkdir(exist_ok=True)
    for root in animal_roots:
        root.rotation_euler = (0, 0, math.radians(-55))
    data = bpy.data.cameras.new("Preview")
    data.lens = 19
    camera = bpy.data.objects.new("Cam_Preview", data)
    camera.location = (45, 74, 15)
    scene.collection.objects.link(camera)
    camera.rotation_euler = (Vector((45, 0, 3.5)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = 1800, 620
    shots = [(0, f % WALK_FRAMES) for f in range(0, WALK_FRAMES * 2, 2)] + [(1, f) for f in range(0, 120, 2)]
    for number, (which, frame) in enumerate(shots):
        for root, pair in zip(animal_roots, actions):
            root.animation_data.action = pair[which]
        scene.frame_set(frame)
        scene.render.filepath = str(frames_dir / f"f{number:04d}.png")
        bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera)
    for root, pair in zip(animal_roots, actions):
        root.rotation_euler = (0, 0, 0)
        root.animation_data.action = pair[1]
    scene.frame_set(0)

    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "forest_models.blend"))
    print("saved", HERE / "forest_models.blend")
    for model in animal_models + prop_models:
        count = sum(len(faces) for _, faces in model.parts.values())
        print(f"  {model.name}: {count} faces, roles: {sorted(model.parts)}")


if __name__ == "__main__":
    main()
