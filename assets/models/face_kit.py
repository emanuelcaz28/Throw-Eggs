"""Faces shared by the later maps' monsters, alongside the Volcano face in build_volcano.py.

classic_mouth is the first maps' mouth (dark inside, a tongue, white teeth) with the lower jaw on its own
Jaw bone, so these monsters snap and roar in the game like the Volcano's (DinoLifeController).
"""
from build_volcano import ring_at, top_of


def classic_mouth(m, front, mouth_z, skull_w, length, snout_w, upper_h, lower_h, gap, upper="Body", lower="Belly",
                  tooth=0.0, per_side=0, lower_teeth=False, tongue=True, grin=0.0, skull_d=1.0, underbite=1.0,
                  on_jaw=None, gold=None):
    """Upper jaw on the Head bone, lower jaw on a Jaw bone hinged at the back of the mouth. tooth and per_side
    put pointed teeth along the upper jaw (lower_teeth: along the lower one too); gold=(side, index) makes one
    of them gold. on_jaw(m, front, mouth_z, gap, lower_length) adds more to the jaw. Call it on the Head bone.
    Returns the snout's tip and its top height along it."""
    upper_z = mouth_z + gap / 2 + upper_h / 2
    lower_z = mouth_z - gap / 2 - lower_h / 2
    back = (front - 0.05, 0, upper_z + upper_h * 0.1, skull_w * 0.94, upper_h * 1.2)
    tip = (front + length, 0, upper_z, snout_w, upper_h)
    m.loft_y(upper, back, tip)
    m.block("Mouth", 0, front + length * 0.45, mouth_z + gap * 0.05, snout_w * 0.84, length * 0.9, gap + 0.04)
    m.block("Mouth", 0, front + 0.05, mouth_z - lower_h * 0.45, snout_w * 0.78, 0.12, gap + lower_h * 0.9)
    edge = mouth_z + gap / 2 + 0.02
    if tooth and per_side:
        for side in (-1, 1):
            for i in range(per_side):
                y = front + length * (0.14 + 0.72 * i / max(per_side - 1, 1))
                size = tooth * (1.0 if i % 2 == 0 else 0.7)
                x = side * (ring_at(back, tip, y)[3] / 2 - size * 0.5)
                role = "Gold" if gold == (side, i) else "Teeth"
                m.loft_z(role, (edge - size, x, y, size * 0.15, size * 0.15), (edge, x, y, size, size))

    m.use("Jaw", (0, front - 0.05, mouth_z), "Head")
    lower_length = length * 0.92 * underbite
    jaw_back = (front - 0.05, 0, lower_z, skull_w * 0.85, lower_h)
    jaw_tip = (front + lower_length, 0, lower_z, snout_w * 0.9, lower_h)
    m.loft_y(lower, jaw_back, jaw_tip)
    m.block("Mouth", 0, front + lower_length * 0.45, mouth_z - gap / 2 + 0.02, snout_w * 0.66, lower_length * 0.8, 0.05)
    if tongue:
        th = max(gap * 0.4, 0.07)
        m.block("Tongue", 0, front + lower_length * 0.42, mouth_z - gap / 2 + 0.04 + th / 2, snout_w * 0.5, lower_length * 0.7, th)
    if tooth and lower_teeth:
        floor = mouth_z - gap / 2 - 0.02
        count = max(per_side - 1, 1)
        for side in (-1, 1):
            for i in range(count):
                y = front + lower_length * (0.22 + 0.6 * i / max(count - 1, 1))
                size = tooth * (0.75 if i % 2 == 0 else 0.55)
                x = side * (ring_at(jaw_back, jaw_tip, y)[3] / 2 - size * 0.5)
                m.loft_z("Teeth", (floor, x, y, size, size), (floor + size, x, y, size * 0.15, size * 0.15))
    if on_jaw:
        on_jaw(m, front, mouth_z, gap, lower_length)
    m.bone = "Head"

    if grin:
        line_h = max(gap, 0.06) * 0.8
        for side in (-1, 1):
            x = side * (skull_w / 2 + 0.005)
            m.loft_y("Mouth", (front - skull_d * 0.38, x, mouth_z + grin, 0.04, line_h * 0.7), (front + 0.02, x, mouth_z, 0.04, line_h))
    return {"tip": front + length, "top": lambda y: top_of((back, tip), y), "width": lambda y: ring_at(back, tip, y)[3]}


def top_nostrils(m, snout, spread, size=0.12, role="Mouth"):
    """Two nostrils on top of the snout, near its tip."""
    y = snout["tip"] - size * 1.8
    z = snout["top"](y)
    for side in (-1, 1):
        m.block(role, side * spread, y, z + size * 0.15, size, size * 1.2, size * 0.4)


def icicle(m, role, x, y, top, length, width=0.4):
    """Something hanging from `top` and tapering to a point: an icicle, a drip."""
    m.loft_z(role, (top - length, x, y, 0.04, 0.04), (top, x, y, width, width))
