"""Rig check for every dino_ in the open .blend: floating parts at rest, parts that split apart under the game's motions.

Blender -b <file>.blend --python check_rig_blend.py

Reports FLOATING (pieces not touching the body at rest), COMES LOOSE (a part that leaves everything it was attached to) and
STRIP BREAKS (one strip split over two bones that opens up). Upper and lower teeth parting as the mouth opens is normal.
The motions copy DinoLifeController's WALK, IDLE (+ROAR for Jaw monsters) and MAULER (Maul monsters), applied about each bone's
head in model axes: pitch = X, roll = Y (forward), yaw = Z, children inheriting their parent's turn.
"""
import math
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sin, cos = math.sin, math.cos


def islands(me):
    parent = list(range(len(me.vertices)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for e in me.edges:
        a, b = find(e.vertices[0]), find(e.vertices[1])
        if a != b:
            parent[a] = b
    groups = {}
    for v in range(len(me.vertices)):
        groups.setdefault(find(v), []).append(v)
    polys = {}
    for p in me.polygons:
        polys.setdefault(find(p.vertices[0]), []).append(list(p.vertices))
    return [(vs, polys.get(r, [])) for r, vs in groups.items()]


def bvh(coords, vs, polys):
    idx = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([coords[v] for v in vs], [[idx[v] for v in p] for p in polys])


def gap(coords, A, B, treeB):
    if treeA_overlap(A, B):
        return 0.0
    best = 1e9
    for v in A[0][::max(1, len(A[0]) // 60)]:
        hit = treeB.find_nearest(coords[v])
        if hit[0] is not None:
            best = min(best, hit[3])
    return best


def treeA_overlap(A, B):
    return bool(A[2].overlap(B[2]))


def keys(u, pts):
    for a, b in zip(pts, pts[1:]):
        if u <= b[0]:
            x = (u - a[0]) / (b[0] - a[0])
            return a[1] + (b[1] - a[1]) * x * x * (3 - 2 * x)
    return pts[-1][1]


def roar(t):
    return ((1 - cos(t)) / 2) ** 10


def walk(p):
    d = {"Spine": (0.02 * sin(2 * p), 0.05 * sin(p), 0.05 * sin(p)), "Neck": (0.05 * sin(2 * p + 0.5), 0, 0.05 * sin(p + 0.6)),
         "Head": (-0.06 * sin(2 * p + 0.5), 0, 0.08 * sin(p + 1.2)), "Jaw": (-0.08 * (0.5 + 0.5 * sin(2 * p)), 0, 0)}
    for L, ph in (("L", 0), ("R", math.pi)):
        side = -1 if L == "L" else 1
        d["Leg" + L] = (0.45 * sin(p + ph), 0, 0)
        d["Shin" + L] = (-0.6 * (0.5 + 0.5 * cos(p + ph)) ** 2, 0, 0)
        d["Arm" + L] = (-0.3 * sin(p + ph), 0, 0)
        d["Wing" + L] = (0, side * 0.14 * sin(2 * p), 0)
    for n, ph in (("FrontL", 0), ("BackR", 0), ("FrontR", math.pi), ("BackL", math.pi)):
        d[n] = (0.32 * sin(p + ph), 0, 0)
    for i in (1, 2, 3):
        d[f"Tail{i}"] = (0.03 * sin(2 * p - i * 0.6), 0, 0.16 * sin(p - i * 0.7))
    return d, {}


def idle(t):
    r = roar(t)
    d = {"Spine": (0.025 * sin(4 * t) + 0.03 * r, 0, 0), "Neck": (0.05 * sin(2 * t + 1) + 0.12 * r, 0, 0.14 * sin(t)),
         "Head": (0.09 * sin(3 * t) + 0.3 * r, 0, 0.36 * sin(t) + 0.08 * sin(3 * t) + 0.08 * sin(14 * t) * r),
         "Jaw": (-0.03 * (0.5 + 0.5 * sin(4 * t)) - 0.55 * r, 0, 0)}
    for L in "LR":
        side = -1 if L == "L" else 1
        d["Arm" + L] = (0.08 * sin(4 * t + 0.5) + 0.45 * r, 0, 0)
        d["Wing" + L] = (0, side * 0.07 * sin(4 * t), 0)
    for i in (1, 2, 3):
        d[f"Tail{i}"] = (0.02 * sin(4 * t - i * 0.5) + (0.08 * r if i == 1 else 0), 0, 0.14 * sin(2 * t - i * 0.6))
    return d, {}


AHEAD = [(0, 0), (0.26, -1.2), (0.33, 3), (0.5, 3), (0.8, 0), (1, 0)]
LEAN = [(0, 0), (0.26, 0.18), (0.33, -0.18), (0.5, -0.18), (0.8, 0), (1, 0)]
SURGE = [(0, 0), (0.26, -0.5), (0.33, 1.6), (0.5, 1.6), (0.8, 0), (1, 0)]
NECK = [(0, 0), (0.26, 0.2), (0.33, -0.3), (0.5, -0.2), (0.8, 0), (1, 0)]
HEAD = [(0, 0), (0.26, 0.1), (0.33, 0.22), (0.5, 0.12), (0.8, 0), (1, 0)]
JAW = [(0, 0), (0.26, -0.5), (0.32, -0.5), (0.345, 0.4), (0.39, -0.2), (0.42, 0.4), (0.46, -0.2), (0.49, 0.4), (0.8, 0), (1, 0)]
ARM = [(0, 0), (0.22, 1.5), (0.33, -0.3), (0.5, -0.3), (0.8, 0), (1, 0)]
FRONT = [(0, 0), (0.26, -0.2), (0.33, 0.45), (0.5, 0.3), (0.8, 0), (1, 0)]
BACK = [(0, 0), (0.26, 0.2), (0.33, -0.4), (0.5, -0.2), (0.8, 0), (1, 0)]


def maul(s, scale):
    u = (s / 2) % 1
    Q = math.pi / 2
    def shake(r):
        x = (u - 0.34) % 1
        return r * sin(32 * Q * s) * (sin(math.pi * x / 0.2) if x < 0.2 else 0)
    d = {"Spine": (0.012 * sin(20 * Q * s), 0, 0), "Maul": (keys(u, LEAN), 0, 0), "Neck": (keys(u, NECK), 0, shake(0.3)),
         "Head": (keys(u, HEAD), shake(0.16), 0), "Jaw": (keys(u, JAW), 0, 0), "ArmL": (keys(u, ARM), 0, 0),
         "ArmR": (keys((s / 2 - 0.5) % 1, ARM), 0, 0), "FrontL": (keys(u, FRONT), 0, 0), "FrontR": (keys(u, FRONT), 0, 0),
         "BackL": (keys(u, BACK), 0, 0), "BackR": (keys(u, BACK), 0, 0), "Tail1": (0, 0, 0.34 * sin(8 * Q * s))}
    move = {"Spine": keys(u, SURGE) * scale, "Maul": keys(u, AHEAD) * scale}
    return d, move


def pose(arm, angles, move):
    world = {}
    for pb in sorted(arm.pose.bones, key=lambda b: len(b.parent_recursive)):
        b = pb.bone
        h = b.head_local
        x, y, z = angles.get(pb.name, (0, 0, 0))
        R = (Matrix.Rotation(x, 4, "X") @ Matrix.Rotation(y, 4, "Y") @ Matrix.Rotation(z, 4, "Z"))
        D = Matrix.Translation(Vector((0, move.get(pb.name, 0), 0))) @ Matrix.Translation(h) @ R @ Matrix.Translation(-h)
        W = world[pb.parent.name] @ D if pb.parent else D
        world[pb.name] = W
        pb.matrix_basis = b.matrix_local.inverted() @ D @ b.matrix_local


def check(arm):
    meshes = [o for o in arm.children_recursive if o.type == "MESH"]
    report = []
    isl = []  # [vs, polys, bvh, bone, mat, lo, hi, mesh index]
    rests = []
    for mi, ob in enumerate(meshes):
        me = ob.data
        rest = [ob.matrix_world @ v.co for v in me.vertices]
        rests.append(rest)
        names = {g.index: g.name for g in ob.vertex_groups}
        for vs, polys in islands(me):
            if not polys:
                continue
            w = {}
            for v in vs:
                for g in me.vertices[v].groups:
                    w[names[g.group]] = w.get(names[g.group], 0) + g.weight
            bone = max(w, key=w.get) if w else "NONE"
            lo = Vector([min(rest[v][i] for v in vs) for i in range(3)])
            hi = Vector([max(rest[v][i] for v in vs) for i in range(3)])
            isl.append([vs, polys, bvh(rest, vs, polys), bone, ob.name.replace(arm.name + "_", ""), lo, hi, mi])
    height = max(i[6].z for i in isl) - min(i[5].z for i in isl)
    tol = height * 0.006
    pairs = {}
    for a in range(len(isl)):
        A = isl[a]
        for b in range(a + 1, len(isl)):
            B = isl[b]
            if any(A[5][k] > B[6][k] + tol or B[5][k] > A[6][k] + tol for k in range(3)):
                continue
            if A[2].overlap(B[2]):
                pairs[(a, b)] = 0
                continue
            g = min(near(rests[A[7]], A[0], B[2]), near(rests[B[7]], B[0], A[2]))
            if g <= tol:
                pairs[(a, b)] = g
    par = list(range(len(isl)))
    def f(i):
        while par[i] != i:
            i = par[i]
        return i
    for a, b in pairs:
        par[f(a)] = f(b)
    comps = {}
    for i in range(len(isl)):
        comps.setdefault(f(i), []).append(i)
    main = max(comps.values(), key=lambda c: sum(len(isl[i][0]) for i in c))
    mains = [i for i in main]
    floating = {}
    for c in comps.values():
        if c is main:
            continue
        for i in c:
            g = 1e9
            for j in mains:
                J = isl[j]
                if any(isl[i][5][k] > J[6][k] + 1.0 or J[5][k] > isl[i][6][k] + 1.0 for k in range(3)):
                    continue
                g = min(g, near(rests[isl[i][7]], isl[i][0], J[2]))
            key = f"{isl[i][4]} on {isl[i][3]}"
            n, worst_g = floating.get(key, (0, 0))
            floating[key] = (n + 1, max(worst_g, g))
    for key, (n, g) in floating.items():
        report.append(f"  FLOATING {n}x {key}, up to {g:.2f} studs from the body ({g / height * 100:.1f}% of height)")
    for i in isl:
        if i[3] == "NONE":
            report.append(f"  NO BONE {i[4]}")
    cross = [(a, b) for (a, b) in pairs if isl[a][3] != isl[b][3]]
    bones = {pb.name for pb in arm.pose.bones}
    motions = [("walk", walk(p * math.tau / 12)) for p in range(12)] + [("idle", idle(t * math.tau / 16)) for t in range(16)]
    if "Maul" in bones:
        motions += [("maul", maul(s * 2 / 24, 1.0)) for s in range(24)]
    worst = {}
    dg = bpy.context.evaluated_depsgraph_get()
    for label, (angles, move) in motions:
        pose(arm, angles, move)
        bpy.context.view_layer.update()
        posed = []
        for ob in meshes:
            ev = ob.evaluated_get(dg)
            em = ev.to_mesh()
            posed.append([ob.matrix_world @ v.co for v in em.vertices])
            ev.to_mesh_clear()
        trees = {}
        def tree(i):
            if i not in trees:
                trees[i] = bvh(posed[isl[i][7]], isl[i][0], isl[i][1])
            return trees[i]
        for a, b in cross:
            if tree(a).overlap(tree(b)):
                g = 0.0
            else:
                g = min(near(posed[isl[a][7]], isl[a][0], tree(b)), near(posed[isl[b][7]], isl[b][0], tree(a)))
            if g >= worst.get((a, b), (-1, ""))[0]:
                worst[(a, b)] = (g, label)
    thr = height * 0.015
    # clusters: pieces joined on the same bone move as one
    par = list(range(len(isl)))
    for (a, b) in pairs:
        if isl[a][3] == isl[b][3]:
            par[f(a)] = f(b)
    clusters = {}
    for i in range(len(isl)):
        clusters.setdefault(f(i), []).append(i)
    big = max(clusters.values(), key=lambda c: sum(len(isl[i][0]) for i in c))
    for c in clusters.values():
        if c is big:
            continue
        links = [worst[(a, b)] for (a, b) in cross if (a in c) != (b in c) and (a in c or b in c)]
        if links and min(g for g, _ in links) > thr:
            g, label = min(links)
            names = sorted({f"{isl[i][4]}({isl[i][3]})" for i in c})
            report.append(f"  COMES LOOSE {', '.join(names)}: {g:.2f} studs ({g / height * 100:.1f}%) in {label}")
    for (a, b), (g, label) in sorted(worst.items(), key=lambda kv: -kv[1][0]):
        if g > thr and isl[a][4] == isl[b][4]:
            report.append(f"  STRIP BREAKS {isl[a][4]} between {isl[a][3]} and {isl[b][3]}: {g:.2f} studs ({g / height * 100:.1f}%) in {label}; pieces {tuple(round(v, 1) for v in (isl[a][5] + isl[a][6]) / 2)} size {tuple(round(v, 1) for v in isl[a][6] - isl[a][5])} / {tuple(round(v, 1) for v in (isl[b][5] + isl[b][6]) / 2)} size {tuple(round(v, 1) for v in isl[b][6] - isl[b][5])}")
    pose(arm, {}, {})
    report.insert(0, f"{arm.name}: {len(isl)} pieces, {len(cross)} joints across bones, height {height:.1f}")
    return report


def near(coords, vs, tree):
    best = 1e9
    for v in vs[::max(1, len(vs) // 80)]:
        hit = tree.find_nearest(coords[v])
        if hit[0] is not None:
            best = min(best, hit[3])
    return best


for o in bpy.data.objects:
    if o.type == "ARMATURE" and o.name.startswith("dino_"):
        for line in check(o):
            print("RIG", line)
