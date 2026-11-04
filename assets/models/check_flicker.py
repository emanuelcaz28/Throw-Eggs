"""Finds flicker (z-fighting) in a map's props: two visible faces lying in the same plane, facing the same way and
overlapping, so the renderer (Blender's and Studio's) can't decide which to draw and they shimmer as the camera moves.

    Blender -b --python check_flicker.py -- build_<map>                       (every prop)
    Blender -b --python check_flicker.py -- build_<map> prop_A prop_B         (just these, with where each overlap is)

Lists the overlaps per prop, largest first. Faces resting on the ground and faces back to back inside a shape are
skipped. Fix anything between two different roles over about 0.2 square studs: move or resize one of the shapes a
little so its face sits inside the other, or clear of it. Same-role overlaps only shimmer the studs; tiny ones
hidden inside another shape (a spoke end in a cabin) don't show.
"""
import sys, math, importlib
from collections import defaultdict
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from mathutils import Vector
mod = importlib.import_module(sys.argv[sys.argv.index("--") + 1])
only = sys.argv[sys.argv.index("--") + 2:] 

def area2(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))) / 2

def clip(subject, clipper):
    out = subject
    for i in range(len(clipper)):
        a, b = clipper[i], clipper[(i + 1) % len(clipper)]
        inp, out = out, []
        if not inp:
            break
        def inside(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -1e-9
        def cross(p, q):
            x1, y1, x2, y2 = a[0], a[1], b[0], b[1]
            x3, y3, x4, y4 = p[0], p[1], q[0], q[1]
            den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(den) < 1e-12:
                return q
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        s = inp[-1]
        for e in inp:
            if inside(e):
                if not inside(s):
                    out.append(cross(s, e))
                out.append(e)
            elif inside(s):
                out.append(cross(s, e))
            s = e
    return out

for make in mod.ALL:
    m = make()
    if only and m.name not in only:
        continue
    faces = []
    for role, (verts, fs) in m.parts.items():
        if role == "Front":
            continue
        vs = [Vector(v) for v in verts]
        # each shape added is its own closed piece: find them by shared corners, and their middles
        parent = list(range(len(vs)))
        def root(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]; i = parent[i]
            return i
        for f in fs:
            for i in f[1:]:
                parent[root(i)] = root(f[0])
        sums = defaultdict(lambda: [Vector(), 0])
        for i, v in enumerate(vs):
            r = root(i); sums[r][0] += v; sums[r][1] += 1
        for f in fs:
            pts = [vs[i] for i in f]
            mid = sums[root(f[0])][0] / sums[root(f[0])][1]
            n = Vector()
            for i in range(len(pts)):  # Newell normal
                a, b = pts[i], pts[(i + 1) % len(pts)]
                n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
            if n.length < 1e-6:
                continue
            n.normalize()
            fc = sum(pts, Vector()) / len(pts)
            if n.dot(fc - mid) < 0:
                n = -n
            d = n.dot(pts[0])
            if n.z < -0.999 and abs(d) < 1e-3:  # resting on the ground: never seen
                continue
            if max(abs(n.dot(p) - d) for p in pts) > 1e-3:
                continue
            faces.append((role, n, d, pts))
    # orient normals consistently: compare as lines (z-fighting also happens back to back in the renders)
    buckets = defaultdict(list)
    for role, n, d, pts in faces:
        buckets[(round(n.x, 2), round(n.y, 2), round(n.z, 2))].append((d, role, n, pts))
    hits = defaultdict(float)
    for key, items in buckets.items():
        items.sort(key=lambda t: t[0])
        for i in range(len(items)):
            d1, r1, n1, p1 = items[i]
            u = n1.orthogonal().normalized(); v = n1.cross(u)
            for j in range(i + 1, len(items)):
                d2, r2, n2, p2 = items[j]
                if d2 - d1 > 0.01:
                    break
                A = [(p.dot(u), p.dot(v)) for p in p1]
                B = [(p.dot(u), p.dot(v)) for p in p2]
                if area2(A) < 0: A = A[::-1]
                if area2(B) < 0: B = B[::-1]
                inter = clip(A, B)
                if len(inter) >= 3:
                    a = abs(area2(inter))
                    if a > 0.02:
                        hits[tuple(sorted((r1, r2)))] += a
                        if a > 0.1 and len(sys.argv) > sys.argv.index("--") + 2:
                            c = sum(p1, Vector()) / len(p1)
                            print(f"      {r1}/{r2} n={tuple(round(x, 2) for x in n1)} at {tuple(round(x, 2) for x in c)} area {a:.2f}")
    if hits:
        print(m.name)
        for (r1, r2), a in sorted(hits.items(), key=lambda t: -t[1]):
            print(f"   {r1:12s} / {r2:12s} {a:8.2f} sq studs{'  (same role)' if r1 == r2 else ''}")
    else:
        print(m.name, "clean")
