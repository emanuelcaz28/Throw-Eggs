"""Heads for maps 13 to 15's 7th and 8th monsters (owner, 2026-11-06: "improve the looks"). Bare, nothing glowing, like beast_head in rare_kit.py, which
maps 10 to 12 keep. What beast_head can't do, and this does:

  - every monster has its own skull: a table of stations instead of one shared wedge, so a boar, a toad, an ape and a bare skull come out of one function;
  - the teeth run right round the front of the jaw on a gum, so head on (how every reveal ends) you see a ring of teeth round a dark throat, not two rows end on;
  - the roof and floor of the mouth are their own faces, so an open mouth has an inside.

A skull or jaw table is rows of (t, half width, low, top): t from the back of the jaw (0) to the tip (1), half width as a share of width / 2, low and top as
shares of height, measured from the lip line. Build on the Head bone; fierce_head makes the Jaw and leaves m.bone on Head.
"""
import math
import random

from mathutils import Matrix, Vector

import rare_kit  # noqa: F401  (first: it turns the stud preview off)
from build_spore_hollow_monsters import egg
from rare_kit import curve, sabre, sheet, slit_eye, swing, sweep, sweep_fine


def power(v, e):
    return math.copysign(abs(v) ** e, v)


def between(table, t, column):
    """A table's column at t, by a smooth curve through its rows."""
    rows = sorted(table)
    if t <= rows[0][0]:
        return rows[0][column]
    if t >= rows[-1][0]:
        return rows[-1][column]
    for k in range(len(rows) - 1):
        if rows[k][0] <= t <= rows[k + 1][0]:
            p1, p2 = rows[k], rows[k + 1]
            p0, p3 = rows[max(k - 1, 0)], rows[min(k + 2, len(rows) - 1)]
            u = (t - p1[0]) / (p2[0] - p1[0])
            a, b, c, d = p0[column], p1[column], p2[column], p3[column]
            value = 0.5 * (2 * b + (c - a) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (3 * b - a - 3 * c + d) * u ** 3)
            return min(max(value, min(b, c) - abs(c - b) * 0.25), max(b, c) + abs(c - b) * 0.25)
    return rows[-1][column]


def ring_point(hw, low, top, angle, flat):
    """A point on a station: squarish, its underside (or top, if flat is negative) pressed flat against the lip."""
    x = hw * power(math.cos(angle), 0.72)
    s = math.sin(angle)
    mid, half = (low + top) / 2, (top - low) / 2
    e = abs(flat) if (s < 0) == (flat > 0) else 0.8
    return x, mid + half * power(s, e)


def loft(m, role, rows, sides=18, flat=0.35, inside="Mouth", arc=1.05):
    """A solid through stations (y, half width, low, top), closed at both ends. The faces on its flat side take the role inside."""
    centre = -math.pi / 2 if flat > 0 else math.pi / 2
    step = math.tau / sides
    verts, faces, flags = [], [], []
    for y, hw, low, top in rows:
        for j in range(sides):
            x, z = ring_point(hw, low, top, j * step, flat)
            verts.append((x, y, z))
    for i in range(len(rows) - 1):
        for j in range(sides):
            a, b = i * sides + j, i * sides + (j + 1) % sides
            faces.append([a, b, b + sides, a + sides])
            gap = abs(((j + 0.5) * step - centre + math.pi) % math.tau - math.pi)
            flags.append(gap < arc)
    ends = [list(range(sides))[::-1], [(len(rows) - 1) * sides + j for j in range(sides)]]
    for target, chosen in ((role, [f for f, inner in zip(faces, flags) if not inner] + ends), (inside, [f for f, inner in zip(faces, flags) if inner])):
        part_verts, part_faces = m.parts.setdefault(target, ([], []))
        start = len(part_verts)
        part_verts.extend(verts)
        part_faces.extend([[start + k for k in f] for f in chosen])
        m.groups.setdefault(target, []).extend([m.bone] * len(verts))


def stations(table, y, zm, length, width, height, count):
    return [(y + length * t, width / 2 * between(table, t, 1), zm + height * between(table, t, 2), zm + height * between(table, t, 3))
            for t in (k / (count - 1) for k in range(count))]


def outline(table, t0, width, y, length, inset):
    """The line of the gum, from t0 at the back to the middle of the front, evenly spaced: (x, y) pairs and how far along each is."""
    raw = [(width / 2 * between(table, t0 + (1 - t0) * k / 59, 1) * inset, y + length * (t0 + (1 - t0) * k / 59) * (1 - 0.14 * (1 - inset))) for k in range(60)]
    raw.append((0.0, raw[-1][1] + raw[-1][0] * 0.3))
    run = [0.0]
    for a, b in zip(raw, raw[1:]):
        run.append(run[-1] + math.dist(a, b))

    def at(s):
        goal = s * run[-1]
        for k in range(len(raw) - 1):
            if run[k + 1] >= goal:
                u = (goal - run[k]) / max(run[k + 1] - run[k], 1e-6)
                return raw[k][0] + (raw[k + 1][0] - raw[k][0]) * u, raw[k][1] + (raw[k + 1][1] - raw[k][1]) * u
        return raw[-1]

    return at


def gum(m, role, at, z, thick):
    """A ridge along the gum line, right round the front."""
    half = [at(k / 13) for k in range(14)]
    path = [((-x, yy, z), thick, thick) for x, yy in half] + [((x, yy, z), thick, thick) for x, yy in reversed(half[:-1])]
    sweep(m, role, path, sides=6, up=(0, 0, 1))


def row_of_teeth(m, at, z, count, tall, base, fangs, direction, rng, rake=0.12, start=0.02):
    """Teeth both sides of the jaw, along the gum from the back to the middle of the front. fangs: (how far along, how much bigger). direction: -1 upper, 1 lower."""
    for side in (-1, 1):
        for k in range(count):
            s = start + (0.985 - start) * (k + 0.5) / count
            x, yy = at(s)
            grow = 0.8 + 0.4 * rng.random()
            for where, big in fangs:
                grow = max(grow, big * max(0.0, 1 - abs(s - where) / 0.05))
            size = tall * grow
            inward = -side * size * 0.14 * (1 - s)
            root = Vector((side * x, yy, z))  # no higher: a big root's corner comes out through the front of the gum
            mid = root + Vector((inward * 0.3, size * rake * 0.2, direction * size * 0.6))
            tip = root + Vector((inward, -size * rake, direction * size * 1.05))
            sabre(m, "Teeth", [tuple(root), tuple(mid), tuple(tip)], base * min(grow, 1.35), 4, sides=5, power=1.1)


def skull_at(table, y, zm, length, width, height, t, angle, flat=0.35):
    """A point on the skull's surface: t along it, angle round it, 0 out to the right, pi / 2 on top."""
    x, z = ring_point(width / 2 * between(table, t, 1), zm + height * between(table, t, 2), zm + height * between(table, t, 3), angle, flat)
    return Vector((x, y + length * t, z))


def eye(m, at, r, look, side, socket=1.9, lid="Body", pupil="Pupil", top=0.5, tilt=0.9, low=0.36, slit=0.2, sink=0.5, ridge="Accent", ridge_size=1.0, proud=0.3):
    """A slit eye sunk in a black pit under a hard ridge that drives down to the nose. Round and open reads cute (map 14, 2026-11-06), so the lid cuts it off flat.
    at: on the skin. sink pushes the pit in, so it reads as a hollow and not a ball. proud: how far the eye's middle stands out of the skin, in eye sizes."""
    look = Vector(look).normalized()
    egg(m, "Socket", tuple(at - look * r * sink), r * socket, r * (sink + 0.3), r * socket * 0.72, 12, 6)  # stops short of the eye, or it shows through the iris
    slit_eye(m, tuple(at + look * r * proud), r, look, side, iris="EyeColour", lid_role=lid, top=top, tilt=tilt, low=low, slit=slit, pupil=pupil, layer=max(0.04, r * 0.1))  # a bigger ball has flatter facets, so its layers sit further apart
    if ridge:
        c = at + look * r * 0.6 - Vector((0, 0, r * ridge_size * 0.26))
        k = r * ridge_size
        sweep_fine(m, ridge, [(tuple(c + Vector((side * k * 1.9, -k * 1.0, k * 1.3))), k * 0.5, k * 0.4), (tuple(c + Vector((side * k * 0.9, -k * 0.3, k * 1.0))), k * 1.3, k * 1.0),
                              (tuple(c + Vector((-side * k * 0.4, k * 0.4, k * 0.56))), k * 1.1, k * 0.9), (tuple(c + Vector((-side * k * 1.9, k * 1.1, -k * 0.75))), k * 0.24, k * 0.24)], sides=8, per=3)


def knob(m, role, at, r):
    """A round end, so the top of a limb is a shoulder and not the flat end of a pipe."""
    egg(m, role, tuple(at), r, r, r, 12, 6)


def brow(m, role, points, widths):
    """A ridge through points, on both sides. Points are for the right-hand side."""
    for side in (-1, 1):
        sweep_fine(m, role, [((side * p[0], p[1], p[2]), w, w * 0.8) for p, w in zip(points, widths)], sides=8, per=3)


def fierce_head(m, y, zm, length, width, height, skull, jaw, gape=-0.7, upper="Body", lower=None, inside="Mouth", gums="Tongue",
                teeth=(9, 8), tall=1.0, base=0.5, fangs=(), low_fangs=None, rows=1, seed=1, jaw_drop=0.16, jaw_length=1.0, t0=0.26, throat=1.0, tongue=True, tongue_long=0.72, lower_inset=0.76, gum_lift=0.3):
    """The skull, the jaw, teeth right round both, a tongue and the skin at the corners of the mouth. Returns where(t, angle), a point on the skull."""
    lower = lower or upper
    rng = random.Random(seed)
    loft(m, upper, stations(skull, y, zm, length, width, height, 22), sides=20, inside=inside)
    upper_gum = outline(skull, t0, width, y, length, 0.86)
    if gums:
        gum(m, gums, upper_gum, zm + base * gum_lift, base * 1.7)
    row_of_teeth(m, upper_gum, zm + (0.0 if gums else 0.12), teeth[0], tall, base, fangs, -1, rng)
    for extra in range(1, rows):
        row_of_teeth(m, outline(skull, t0 + 0.1, width, y, length, 0.86 - 0.2 * extra), zm + 0.02, teeth[0] - 2, tall * 0.7, base * 0.8, (), -1, rng)
    egg(m, inside, (0, y + length * 0.1, zm + height * 0.02), width * 0.34 * throat, height * 0.5 * throat, height * 0.42 * throat, 12, 6)

    hinge = (0, y + length * 0.04, zm - 0.02)
    m.use("Jaw", hinge, "Head")
    z = zm - height * jaw_drop
    long_ = length * jaw_length
    loft(m, lower, stations(jaw, y, z, long_, width, height, 18), sides=18, flat=-0.35, inside=inside)
    lower_gum = outline(jaw, t0 + 0.02, width, y, long_, lower_inset)
    if gums:
        gum(m, gums, lower_gum, z - base * 0.1, base * 1.6)
    row_of_teeth(m, lower_gum, z - (0.0 if gums else 0.12), teeth[1], tall * 0.86, base * 0.92, fangs if low_fangs is None else low_fangs, 1, rng)
    for extra in range(1, rows):
        row_of_teeth(m, outline(jaw, t0 + 0.12, width, y, long_, lower_inset - 0.2 * extra), z, teeth[1] - 2, tall * 0.6, base * 0.7, (), 1, rng)
    if tongue:
        hw = width / 2 * between(jaw, 0.4, 1)
        sweep_fine(m, "Tongue", [((0, y + long_ * 0.12, z + 0.06), hw * 0.9, height * 0.12), ((0, y + long_ * 0.45, z + height * 0.06), hw * 0.78, height * 0.12),
                                 ((0, y + long_ * tongue_long, z + height * 0.03), hw * 0.34, height * 0.07)], sides=8, per=3)
    swing(m, ["Jaw"], hinge, gape)

    # Skin across the corners of the mouth, which stretches as the jaw moves.
    turn = Matrix.Rotation(gape, 3, Vector((1, 0, 0)))
    pivot = Vector(hinge)
    for side in (-1, 1):
        rows_, bones = [], []
        for t in (0.04, 0.1, 0.16, 0.22, 0.28):
            high = Vector((side * width / 2 * between(skull, t, 1) * 0.97, y + length * t, zm + height * 0.06))
            low = pivot + turn @ (Vector((side * width / 2 * between(jaw, t, 1) * 0.97, y + long_ * t, z - height * 0.02)) - pivot)
            sag = high.lerp(low, 0.5) - Vector((side * width * 0.03 * (t / 0.28), length * 0.05 * (t / 0.28), 0))
            rows_.append([tuple(high), tuple(sag), tuple(low)])
            bones.append(["Head", "Head", "Jaw"])
        sheet(m, upper, rows_, bones, 0.22)
    m.bone = "Head"

    def where(t, angle):
        return skull_at(skull, y, zm, length, width, height, t, angle)

    return where


def band(m, role, centre, width, height, length=0.9, bone=None, tilt=(0, 1, 0)):
    """A hoop of hard skin round a body, a little wider than it: a segment, a plate."""
    if bone:
        m.bone = bone
    c, d = Vector(centre), Vector(tilt).normalized() * length / 2
    sweep(m, role, [(tuple(c - d), width * 0.94, height * 0.94), (tuple(c - d * 0.3), width, height), (tuple(c + d * 0.3), width, height), (tuple(c + d), width * 0.94, height * 0.94)], sides=14)


def horn(m, role, base, tip, width, droop=0.0, count=6):
    """A curved spike from base to tip; droop bends its middle down, or up if negative."""
    a, b = Vector(base), Vector(tip)
    sabre(m, role, [tuple(a), tuple(a.lerp(b, 0.55) - Vector((0, 0, droop))), tuple(b)], width, count)


__all__ = ["band", "brow", "knob", "curve", "eye", "fierce_head", "horn"]
