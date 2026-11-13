"""Takes the flicker (z-fighting) off a monster before it's exported: wherever a piece of one colour lies on a piece of another
(a belly panel along the body, a pupil on its eye, a shine on the pupil), the piece on top is lifted off the one under it, toward the
side you can see, pass after pass until nothing fights (a shine on a pupil on an eye goes up three times), so Studio never has
two surfaces at the same depth. Uses the same test as
check_flicker_monsters.py (surfaces closer than GAP, looking the same way, where you can see them).

export_fbx.py calls lift(armature) on every dino_ armature, on the copy in memory: the .blend and the build scripts stay as
they are. check_flicker_blend.py with FIXED=1 checks the result.
"""
from collections import defaultdict

from mathutils import Vector
from mathutils.bvhtree import BVHTree

GAP = 0.03  # how close counts as fighting, in studs at the built size (check_flicker_monsters.GAP)
STEP = 0.06  # how far each layer is lifted off the one under it, in studs at the built size
MAX_LIFTS = 3  # the most times one piece is lifted
# Which colour lies on which: lower numbers are underneath. A role not listed sits at 3, and between two at the same number the
# smaller one is on top.
RANK = {"Body": 0, "Skin": 0, "Shell": 0, "Fur": 0, "Belly": 2, "Accent": 2, "Accent2": 2, "Sail": 2, "Plate": 2,
        "Claw": 4, "Teeth": 4, "Tooth": 4, "Horn": 4, "Mouth": 4, "Tongue": 5, "Socket": 5, "Gum": 5,
        "EyeWhite": 6, "Eye": 6, "EyeGlow": 6, "Iris": 7, "Pupil": 8, "Slit": 8, "Highlight": 9, "Shine": 9}


def _role(armature, mesh):
    return mesh.name[len(armature.name) + 1:] if mesh.name.startswith(armature.name + "_") else mesh.name


def _pieces(mesh):
    """Each vertex's piece: the lump it belongs to (vertices joined by faces)."""
    parent = list(range(len(mesh.data.vertices)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for p in mesh.data.polygons:
        vs = p.vertices
        for v in vs[1:]:
            parent[root(v)] = root(vs[0])
    return [root(i) for i in range(len(parent))]


LOOKS = [Vector(v).normalized() for v in ((0, 0, 1), (0.7, 0, 0.7), (-0.7, 0, 0.7), (0, 0.7, 0.7), (0, -0.7, 0.7), (1, 0, 0), (-1, 0, 0),
                                          (0, 1, 0), (0, -1, 0), (0, 0, -1))]


def _pass(armature, meshes, pieces, area_of, before):
    """One pass: finds the fights and lifts each top piece STEP off what it lies on. Returns how many pieces moved."""
    verts, tris, owner = [], [], []  # owner[t] = (mesh index, piece id)
    for mi, mesh in enumerate(meshes):
        m = mesh.matrix_world
        start = len(verts)
        verts.extend(m @ v.co for v in mesh.data.vertices)
        for p in mesh.data.polygons:
            vs = p.vertices
            for k in range(1, len(vs) - 1):
                tris.append((start + vs[0], start + vs[k], start + vs[k + 1]))
                owner.append((mi, pieces[mi][vs[0]]))
    tree = BVHTree.FromPolygons(verts, tris, all_triangles=True)
    normals = [(verts[b] - verts[a]).cross(verts[c] - verts[a]) for a, b, c in tris]
    middle = defaultdict(lambda: [Vector(), 0])
    for t, (a, _, _) in enumerate(tris):
        entry = middle[owner[t]]
        entry[0] += verts[a]
        entry[1] += 1

    def open_air(p, n):
        start = p + n * (GAP * 1.5)
        return any(d.dot(n) > 0.05 and tree.ray_cast(start, d, 1000.0)[0] is None for d in LOOKS)

    def key(mi):
        return (RANK.get(_role(armature, meshes[mi]), 3), -area_of[mi])

    pushes = defaultdict(list)  # top piece -> [(world spot, world direction to lift)]
    for i, (a, b, c) in enumerate(tris):
        n = normals[i]
        if n.length < 2e-4:
            continue
        n = n.normalized()
        pa, pb, pc = verts[a], verts[b], verts[c]
        for p in ((pa + pb + pc) / 3, (pa * 4 + pb + pc) / 6, (pa + pb * 4 + pc) / 6, (pa + pb + pc * 4) / 6):
            for _, _, j, _ in tree.find_nearest_range(p, GAP):
                if j is None or owner[j][0] == owner[i][0] or normals[j].length < 1e-9:
                    continue
                if n.dot(normals[j].normalized()) < 0.96:
                    # Only faces looking the same way can fight (check_flicker_monsters' test): back to back, one is always
                    # culled. Lifting those too pushed stacked eyes and tooth roots apart pass after pass (map 11, 2026-11-12).
                    continue
                # The two lie together. Lift toward the side that can be seen (both sides of a thin sheet on a body can't).
                up, down = open_air(p, n), open_air(p, -n)
                if not up and not down:
                    break  # closed in on both sides: nobody sees it
                top = owner[i] if key(owner[i][0]) > key(owner[j][0]) else owner[j]
                k = i if owner[i] == top else j
                d = n if up else -n
                if up and down:
                    # Open both ways (a wing or a fin, two thin sheets one on the other): the same way as this piece's other
                    # lifts, so a flat sheet all goes off one side, or else out of the piece's middle.
                    ref = before[top][0] if before[top] else (pushes[top][0][1] if pushes[top] else None)
                    if ref is None:
                        total, count = middle[top]
                        ref = p - total / count
                    if d.dot(ref) < 0:
                        d = -d
                if any(d.dot(e) < -0.5 for e in before[top]):
                    d = -d  # never back down onto what it was lifted off: keep going the same way past the next surface
                pushes[top].append((p, d, tris[k]))
                break

    starts = []
    total = 0
    for mesh in meshes:
        starts.append(total)
        total += len(mesh.data.vertices)
    for (mi, pid), spots in pushes.items():
        # At most MAX_LIFTS lifts a piece: a shine on a pupil on an eye needs three; more is a piece being shoved on through
        # whatever it meets next (a tooth went through the mouth, the face and into the nose, map 11, 2026-11-12).
        if before[("passes", mi, pid)].count(1) >= MAX_LIFTS:
            continue
        before[("passes", mi, pid)].append(1)
        before[(mi, pid)].extend(d for _, d, _ in spots[:8])
        mesh = meshes[mi]
        inverse = mesh.matrix_world.inverted()
        turn = inverse.to_3x3()
        scale = mesh.matrix_world.to_scale()
        local = STEP / max(1e-6, (abs(scale.x) + abs(scale.y) + abs(scale.z)) / 3)
        # Each vertex of a fighting face goes up along every different lift of the faces it's on (a box corner on two fighting
        # faces goes out of both); the rest of the piece follows the nearest fighting spot.
        own = defaultdict(list)
        local_spots = []
        for p, d, corners in spots:
            d = (turn @ d).normalized()
            local_spots.append((inverse @ p, d))
            for g in corners:
                v = g - starts[mi]
                if not any(d.dot(e) > 0.95 for e in own[v]):
                    own[v].append(d)
        for v in mesh.data.vertices:
            if pieces[mi][v.index] != pid:
                continue
            if own.get(v.index):
                v.co += sum(own[v.index], Vector()) * local
            else:
                v.co += min(local_spots, key=lambda sd: (sd[0] - v.co).length_squared)[1] * local
    for mesh in meshes:
        mesh.data.update()
    return len(pushes)


def lift(armature, passes=16):
    """Lifts the pieces that fight, pass after pass. Returns how many pieces moved in all."""
    meshes = [m for m in armature.children if m.type == "MESH" and len(m.data.polygons)]
    if len(meshes) < 2:
        return 0
    for mesh in meshes:
        if mesh.data.users > 1:
            mesh.data = mesh.data.copy()  # never move a mesh another model shares
    pieces = [_pieces(m) for m in meshes]
    area_of = {mi: sum(p.area for p in m.data.polygons) for mi, m in enumerate(meshes)}
    moved = 0
    before = defaultdict(list)  # piece -> the ways it has been lifted
    for _ in range(passes):
        count = _pass(armature, meshes, pieces, area_of, before)
        moved += count
        if not count:
            break
    return moved
