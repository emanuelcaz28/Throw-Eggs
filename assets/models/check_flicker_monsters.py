"""Finds flicker (z-fighting) on a monster: two surfaces of different parts lying almost on top of each other, looking the same way,
where you can see them. check_flicker.py finds flat faces in exactly the same plane, which is what props suffer from. Monsters also
suffer on curves: an iris a hair above its eyeball, a lip lying along a skull. Those pass that check and shimmer at a distance anyway,
because far from the camera the renderer can't tell two surfaces apart that are this close.

    Blender -b --python check_flicker_monsters.py -- build_<map>_monsters_7_8 [more scripts]
    GAP=0.03 ...     how close counts, in studs at the first map's size (default 0.03)

Lists each pair of parts with the area that fights, and where the worst of it is. Anything hidden inside the body is ignored: it
looks out along the surface, and a spot closed in on every side can't be seen. Exits 1 if it finds anything over 0.05 square studs.
"""
import importlib
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector
from mathutils.bvhtree import BVHTree

GAP = float(os.environ.get("GAP", "0.03"))
LIMIT = 0.05


def triangles(model):
    verts, polys, roles, bones = [], [], [], []
    for role, (vs, faces) in model.parts.items():
        start = len(verts)
        verts.extend(Vector(v) for v in vs)
        for f in faces:
            for k in range(1, len(f) - 1):
                polys.append((start + f[0], start + f[k], start + f[k + 1]))
                roles.append(role)
                bones.append(model.groups[role][f[0]])
    return verts, polys, roles, bones


def check(model):
    verts, polys, roles, bones = triangles(model)
    tree = BVHTree.FromPolygons(verts, polys, all_triangles=True)
    # Which way each face looks: out of the closed piece it belongs to, as Blender's recalculated normals do. Studio draws only the
    # outside of a mesh, so two faces back to back never fight; only two looking the same way do.
    parent = list(range(len(verts)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a, b, c in polys:
        parent[root(b)] = root(a)
        parent[root(c)] = root(a)
    sums = defaultdict(lambda: [Vector(), 0])
    for i, v in enumerate(verts):
        r = root(i)
        sums[r][0] += v
        sums[r][1] += 1
    normals = []
    for a, b, c in polys:
        n = (verts[b] - verts[a]).cross(verts[c] - verts[a])
        total, count = sums[root(a)]
        if n.dot((verts[a] + verts[b] + verts[c]) / 3 - total / count) < 0:
            n = -n
        normals.append(n)
    looks = [Vector(v) for v in ((0, 0, 1), (0.7, 0, 0.7), (-0.7, 0, 0.7), (0, 0.7, 0.7), (0, -0.7, 0.7), (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, -1))]

    def seen(p, n):
        """Can anything see this spot? It's seen if a line out of it, on the side it faces, reaches open air."""
        start = p + n * (GAP * 1.5)
        for d in looks:
            if d.dot(n) > 0.05 and tree.ray_cast(start, d, 1000.0)[0] is None:
                return True
        return False

    hits, worst = defaultdict(float), {}
    for i, (a, b, c) in enumerate(polys):
        n = normals[i]
        area = n.length / 2
        if area < 1e-4:
            continue
        n = n.normalized()
        pa, pb, pc = verts[a], verts[b], verts[c]
        spots = [(pa + pb + pc) / 3, (pa * 4 + pb + pc) / 6, (pa + pb * 4 + pc) / 6, (pa + pb + pc * 4) / 6]
        for p in spots:
            pair = None
            for _, _, j, _ in tree.find_nearest_range(p, GAP):
                if j is None or roles[j] == roles[i] or normals[j].length < 1e-9:
                    continue
                if n.dot(normals[j].normalized()) > 0.96:
                    pair = tuple(sorted((roles[i], roles[j])))
                    break
            if pair and seen(p, n):
                hits[pair] += area / len(spots)
                if pair not in worst or area > worst[pair][0]:
                    worst[pair] = (area, tuple(round(x, 1) for x in p), bones[i])
    return hits, worst


def main():
    bad = False
    for name in sys.argv[sys.argv.index("--") + 1:]:
        for make in importlib.import_module(name).ALL:
            model = make()
            hits, worst = check(model)
            shown = {k: v for k, v in hits.items() if v > LIMIT}
            print(f"FLICKER {model.name}: " + ("clear" if not shown else f"{len(shown)} pairs"))
            for pair, area in sorted(shown.items(), key=lambda kv: -kv[1]):
                bad = True
                print(f"FLICKER    {pair[0]} / {pair[1]}: {area:.2f} sq studs, worst at {worst[pair][1]} on {worst[pair][2]}")
    sys.exit(1 if bad else 0)


main()
