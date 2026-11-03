"""The throw: a crouched low swing, a spin and a lunging straight-arm release, keyed on the MrXen0 R15 rig and turned
into a Roblox KeyframeSequence (run with Blender in background mode). The poses follow the owner's recording of the
reference game (docs/GAME_SPEC.md section 7, "Throw").

    Blender -b ~/Downloads/MrXen0_R15RIG_v1.2.blend --python assets/animations/build_throw.py

Writes src/shared/Animations/ThrowWindup.rbxmx (Rojo syncs it into ReplicatedStorage.Shared.Animations), throw.blend
next to this script (open it and press play) and preview frames in design/animations/throw/.

The rig's IK/FK controls are switched off in the copy and the 15 R15 body bones are keyed directly, since those are
exactly the joints Roblox plays. Each key is a rotation in the rig's rest axes (the character faces +Y, its right is
+X, up is +Z) about the bone's joint, relative to its parent, so "raise the arm forward" is +X whatever the bone's
roll. The conversion to Roblox joints is the one from act-normal's walk and steal clips: each bone's change from
rest is put onto Studio's own R15 rig (studio_rig.json, the Motor6D C0 and C1 of a Rig Builder R15) and read back
as that joint's transform, checked to match.

Timing (seconds) is in T; RELEASE is when the egg leaves the hand, which Config/Throw windup.releaseInClip matches.
The clip holds the lunge after the release while the camera follows the egg, then stands back up.
"""
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PREVIEW = ROOT / "design" / "animations" / "throw"
CLIPS = ROOT / "src" / "shared" / "Animations"
NAME = "ThrowWindup"
FPS = 60  # baked in Blender
EXPORT_FPS = 30  # keyframes in the Roblox clip; Roblox blends between them
LENGTH = 2.0
RELEASE = 1.1

BODY = ["LowerTorso", "UpperTorso", "Head", "LeftUpperArm", "LeftLowerArm", "LeftHand", "RightUpperArm",
        "RightLowerArm", "RightHand", "LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "RightUpperLeg", "RightLowerLeg",
        "RightFoot"]

# Rotations in degrees (x, y, z) about the rest axes, per bone, at times in seconds. Every track starts and ends at
# rest, so the clip blends into the idle cleanly. LowerTorso turns the whole body: +Z is anticlockwise from above,
# towards the character's left, so a full turn ends at 360, which is rest again. Thighs are keyed against upright,
# not against the hips, so leaning the hips doesn't swing the legs back. Arms: +X raises the arm forward (180 is
# straight up), -Y swings the right arm out to its side and +Y the left arm to its side.
T = (0.0, 0.12, 0.32, 0.55, 0.72, 0.88, 1.0, RELEASE, 1.3, 1.6, LENGTH)
KEYS = {
    #                  start       lift           wind back      low swing      rise           cock           plant          release        follow         hold           rest
    "LowerTorso":     [(0, 0, 0),  (0, 0, -25),   (6, 0, -75),   (-6, 0, 40),   (0, 0, 175),   (4, 0, 265),   (-4, 0, 330),  (-10, 0, 360), (-12, 0, 366), (-11, 0, 364), (0, 0, 360)],
    "UpperTorso":     [(0, 0, 0),  (0, 0, -10),   (-32, 0, -25), (-48, 0, -8),  (-6, 0, -20),  (10, 0, -42),  (0, 0, -22),   (-30, 0, 24),  (-36, 0, 30),  (-33, 0, 28),  (0, 0, 0)],
    "Head":           [(0, 0, 0),  (0, 0, 10),    (24, 0, 30),   (34, 0, 8),    (6, 0, 12),    (-6, 0, 36),   (0, 0, 16),    (22, 0, -20),  (26, 0, -26),  (24, 0, -24),  (0, 0, 0)],
    "RightUpperArm":  [(10, 0, 0), (60, -10, 0),  (-55, -30, 0), (20, -65, 0),  (110, -55, 0), (200, -15, 0), (165, -20, 0), (92, -5, 0),   (80, 0, 10),   (84, 0, 6),    (0, 0, 0)],
    "RightLowerArm":  [(15, 0, 0), (70, 0, 0),    (20, 0, 0),    (10, 0, 0),    (30, 0, 0),    (95, 0, 0),    (60, 0, 0),    (5, 0, 0),     (10, 0, 0),    (10, 0, 0),    (0, 0, 0)],
    "RightHand":      [(0, 0, 0),  (0, 0, 0),     (0, 0, 0),     (0, 0, 0),     (0, 0, 0),     (-25, 0, 0),   (-10, 0, 0),   (20, 0, 0),    (15, 0, 0),    (15, 0, 0),    (0, 0, 0)],
    "LeftUpperArm":   [(0, 0, 0),  (20, 10, 0),   (40, 40, 0),   (10, 70, 0),   (60, 70, 0),   (80, 30, 0),   (70, 20, 0),   (10, 40, -10), (-20, 35, 0),  (-15, 35, 0),  (0, 0, 0)],
    "LeftLowerArm":   [(0, 0, 0),  (20, 0, 0),    (40, 0, 0),    (20, 0, 0),    (20, 0, 0),    (30, 0, 0),    (30, 0, 0),    (70, 0, 0),    (60, 0, 0),    (60, 0, 0),    (0, 0, 0)],
    "RightUpperLeg":  [(0, 0, 0),  (0, 0, 0),     (35, 0, 0),    (40, 0, 0),    (15, 0, 0),    (10, 0, 0),    (-10, 0, 0),   (-25, 0, 0),   (-30, 0, 0),   (-28, 0, 0),   (0, 0, 0)],
    "RightLowerLeg":  [(0, 0, 0),  (0, 0, 0),     (-55, 0, 0),   (-60, 0, 0),   (-25, 0, 0),   (-15, 0, 0),   (-20, 0, 0),   (-15, 0, 0),   (-20, 0, 0),   (-20, 0, 0),   (0, 0, 0)],
    "LeftUpperLeg":   [(0, 0, 0),  (0, 0, 0),     (30, 0, 0),    (35, 0, 0),    (15, 0, 0),    (25, 0, 0),    (55, 0, 0),    (65, 0, 0),    (70, 0, 0),    (68, 0, 0),    (0, 0, 0)],
    "LeftLowerLeg":   [(0, 0, 0),  (0, 0, 0),     (-50, 0, 0),   (-55, 0, 0),   (-25, 0, 0),   (-30, 0, 0),   (-50, 0, 0),   (-60, 0, 0),   (-65, 0, 0),   (-62, 0, 0),   (0, 0, 0)],
}
# The hips drop into the crouch, come up for the spin and sink into the lunge (studs, up).
HIPS = [0, 0, -0.6, -0.7, -0.15, -0.1, -0.5, -0.8, -0.9, -0.85, 0]


class Track:
    """A smooth curve through keys that never overshoots: a key between a rise and a fall comes to rest."""

    def __init__(self, times, values):
        self.t = list(times)
        self.v = [Vector(v) if isinstance(v, (tuple, list)) else Vector((v, 0.0)) for v in values]  # (Vectors need two numbers.)
        n = len(self.v[0])
        h = [b - a for a, b in zip(self.t, self.t[1:])]
        d = [(b - a) / step for a, b, step in zip(self.v, self.v[1:], h)]
        self.m = [Vector([0.0] * n) for _ in self.v]
        for i in range(1, len(self.v) - 1):
            for c in range(n):
                left, right = d[i - 1][c], d[i][c]
                if left * right > 0:
                    w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
                    self.m[i][c] = (w1 + w2) / (w1 / left + w2 / right)

    def at(self, time):
        if time <= self.t[0]:
            return self.v[0].copy()
        for i in range(len(self.t) - 1):
            t0, t1 = self.t[i], self.t[i + 1]
            if time <= t1:
                h = t1 - t0
                u = (time - t0) / h
                h00, h10, h01, h11 = 2 * u**3 - 3 * u**2 + 1, u**3 - 2 * u**2 + u, -2 * u**3 + 3 * u**2, u**3 - u**2
                return self.v[i] * h00 + self.m[i] * h * h10 + self.v[i + 1] * h01 + self.m[i + 1] * h * h11
        return self.v[-1].copy()


def rest_rotation(degrees):
    return Euler([math.radians(a) for a in degrees], "XYZ").to_matrix().to_4x4()


def animate(arm):
    tracks = {name: Track(T, keys) for name, keys in KEYS.items()}
    hips = Track(T, HIPS)
    action = bpy.data.actions.new(NAME)
    arm.animation_data_create()
    arm.animation_data.action = action
    frames = round(LENGTH * FPS)
    for frame in range(frames + 1):
        time = frame / FPS
        for name in BODY:
            bone = arm.pose.bones[name]
            rest = arm.data.bones[name].matrix_local.to_3x3().to_4x4()
            if name.endswith("UpperLeg"):
                angles = tracks[name].at(time)
                rotation = rest_rotation((angles[0] - tracks["LowerTorso"].at(time)[0], angles[1], angles[2]))
            elif name in tracks:
                rotation = rest_rotation(tracks[name].at(time))
            elif name.endswith("Foot"):
                # Feet stay nearly level: undo most of the thigh and knee (the thigh is already against upright).
                side = "Left" if name.startswith("Left") else "Right"
                tilt = tracks[side + "UpperLeg"].at(time)[0] + tracks[side + "LowerLeg"].at(time)[0]
                rotation = rest_rotation((-tilt * 0.8, 0, 0))
            else:
                rotation = Matrix.Identity(4)
            bone.rotation_mode = "QUATERNION"
            bone.rotation_quaternion = (rest.inverted() @ rotation @ rest).to_quaternion()
            bone.keyframe_insert("rotation_quaternion", frame=frame, group=name)
            if name == "LowerTorso":
                bone.location = rest.inverted() @ Vector((0, 0, hips.at(time)[0]))
                bone.keyframe_insert("location", frame=frame, group=name)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 0, frames
    return frames


# ---------------------------------------------------------------------- conversion to a KeyframeSequence


def cf(v):
    return Matrix((v[3:6] + [v[0]], v[6:9] + [v[1]], v[9:12] + [v[2]], [0, 0, 0, 1]))


def vals(m):
    return [m[0][3], m[1][3], m[2][3]] + [m[i][j] for i in range(3) for j in range(3)]


def convert(arm, frames):
    rig = json.loads((HERE / "studio_rig.json").read_text())
    rest = {"HumanoidRootPart": Matrix.Identity(4)}
    for name in BODY:
        joint = rig["motors"][name]
        rest[name] = rest[joint["parent"]] @ cf(joint["c0"]) @ cf(joint["c1"]).inverted()
    # Blender (x, y, z) -> Roblox (x, z, -y), with the root part at the origin (it's 3 studs up in the rig).
    swap = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
    origin = Matrix.Translation((0, -3, 0))
    scene = bpy.context.scene
    step = FPS // EXPORT_FPS
    keyframes, worst = [], 0.0
    # Every other baked frame, plus the release itself, so the clip has a keyframe named Release.
    for frame in sorted(set(range(0, frames + 1, step)) | {round(RELEASE * FPS)}):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        world = {}
        for name in ["HumanoidRootPart"] + BODY:
            delta = arm.pose.bones[name].matrix @ arm.data.bones[name].matrix_local.inverted()
            world[name] = origin @ swap @ delta @ swap.inverted() @ origin.inverted() @ rest[name]
        rows, rebuilt = [], {"HumanoidRootPart": world["HumanoidRootPart"]}
        for name in BODY:
            joint = rig["motors"][name]
            parent = joint["parent"]
            pose = cf(joint["c0"]).inverted() @ world[parent].inverted() @ world[name] @ cf(joint["c1"])
            rebuilt[name] = rebuilt[parent] @ cf(joint["c0"]) @ pose @ cf(joint["c1"]).inverted()
            worst = max(worst, max(abs(rebuilt[name][i][k] - world[name][i][k]) for i in range(4) for k in range(4)))
            rows.append((name, parent, vals(pose)))
        keyframes.append((frame / FPS, rows))
    assert worst < 1e-4, worst

    root = ET.Element("roblox", {"version": "4"})
    counter = [0]

    def item(parent, cls):
        counter[0] += 1
        return ET.SubElement(parent, "Item", {"class": cls, "referent": f"RBX{counter[0]}"})

    def prop(parent, tag, name, value):
        ET.SubElement(parent, tag, {"name": name}).text = str(value)

    def pose_item(parent, name, values, weight=1):
        pose = item(parent, "Pose")
        props = ET.SubElement(pose, "Properties")
        prop(props, "string", "Name", name)
        prop(props, "float", "Weight", weight)
        prop(props, "token", "EasingStyle", 0)
        prop(props, "token", "EasingDirection", 0)
        frame = ET.SubElement(props, "CoordinateFrame", {"name": "CFrame"})
        for tag, value in zip(["X", "Y", "Z", "R00", "R01", "R02", "R10", "R11", "R12", "R20", "R21", "R22"], values):
            ET.SubElement(frame, tag).text = f"{value:.6f}"
        return pose

    sequence = item(root, "KeyframeSequence")
    props = ET.SubElement(sequence, "Properties")
    prop(props, "string", "Name", NAME)
    prop(props, "bool", "Loop", "false")
    prop(props, "token", "Priority", 2)  # Action, over the idle and walk
    for time, rows in keyframes:
        keyframe = item(sequence, "Keyframe")
        props = ET.SubElement(keyframe, "Properties")
        prop(props, "string", "Name", "Release" if abs(time - RELEASE) < 1e-6 else "Keyframe")
        prop(props, "float", "Time", f"{time:.6f}")
        parents = {"HumanoidRootPart": pose_item(keyframe, "HumanoidRootPart", vals(Matrix.Identity(4)), 0)}
        for name, parent, values in rows:
            parents[name] = pose_item(parents[parent], name, values)
    ET.indent(root)
    CLIPS.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(str(CLIPS / f"{NAME}.rbxmx"), encoding="utf-8", xml_declaration=True)
    return {"keyframes": len(keyframes), "seconds": LENGTH, "release": RELEASE, "reconstruction_error": worst}


# ---------------------------------------------------------------------- preview


def preview(frames):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_shadows = True
    scene.render.resolution_x, scene.render.resolution_y = 480, 480
    scene.render.image_settings.file_format = "PNG"
    colours = {"Head": (1, 0.85, 0.3, 1), "UpperTorso": (0.25, 0.6, 0.95, 1), "LowerTorso": (0.2, 0.45, 0.8, 1),
               "RightUpperArm": (0.95, 0.4, 0.3, 1), "RightLowerArm": (0.95, 0.4, 0.3, 1), "RightHand": (1, 0.85, 0.3, 1)}
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.color = colours.get(obj.name, (0.55, 0.6, 0.65, 1))
            if obj.name.startswith("WGT"):
                obj.hide_render = True
    ground = bpy.data.meshes.new("Ground")
    ground.from_pydata([(-20, -20, 0), (20, -20, 0), (20, 20, 0), (-20, 20, 0)], [], [(0, 1, 2, 3)])
    floor = bpy.data.objects.new("Ground", ground)
    floor.color = (0.45, 0.8, 0.35, 1)
    scene.collection.objects.link(floor)
    camera = bpy.data.objects.new("PreviewCam", bpy.data.cameras.new("PreviewCam"))
    camera.data.lens = 35
    scene.collection.objects.link(camera)
    scene.camera = camera
    arm = bpy.data.objects["Roblox_R15"]
    target = arm.matrix_world @ Vector((0, 0, 2.6))
    PREVIEW.mkdir(parents=True, exist_ok=True)
    for view, offset in (("front", Vector((5, 9, 2.5))), ("side", Vector((10, 0, 2.5)))):
        camera.location = target + offset
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        folder = PREVIEW / f"frames_{view}"
        folder.mkdir(exist_ok=True)
        for frame in range(0, frames + 1, 2):
            scene.frame_set(frame)
            scene.render.filepath = str(folder / f"f{frame:03d}.png")
            bpy.ops.render.render(write_still=True)


def main():
    arm = bpy.data.objects["Roblox_R15"]
    for name in BODY:
        bone = arm.pose.bones[name]
        for constraint in list(bone.constraints):
            bone.constraints.remove(constraint)
    arm.animation_data_create()
    arm.animation_data.action = None
    for bone in arm.pose.bones:
        bone.rotation_mode = "QUATERNION"
        bone.rotation_quaternion = (1, 0, 0, 0)
        bone.location = (0, 0, 0)
    frames = animate(arm)
    report = convert(arm, frames)
    print("CONVERTED", json.dumps(report))
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "throw.blend"))
    if "--no-preview" not in sys.argv:
        preview(frames)
        bpy.context.scene.frame_set(0)


main()
