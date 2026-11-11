# Turns Figma exports (white art over the page colour 23,18,41) into white PNGs with real transparency.
import zlib, struct, sys
def read(path):
    d = open(path, 'rb').read()
    w, h, bd, ct = struct.unpack('>IIBB', d[16:26])
    assert bd == 8 and ct in (2, 6), (bd, ct)
    bpp = 4 if ct == 6 else 3
    pos, idat = 8, b''
    while pos < len(d):
        n, t = struct.unpack('>I4s', d[pos:pos+8])
        if t == b'IDAT': idat += d[pos+8:pos+8+n]
        pos += 12 + n
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev = [], bytearray(stride)
    for y in range(h):
        f = raw[y*(stride+1)]
        line = bytearray(raw[y*(stride+1)+1:(y+1)*(stride+1)])
        if f == 1:
            for i in range(bpp, stride): line[i] = (line[i] + line[i-bpp]) & 255
        elif f == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i-bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i-bpp] if i >= bpp else 0
                b = prev[i]; c = prev[i-bpp] if i >= bpp else 0
                p = a + b - c; pa = abs(p-a); pb = abs(p-b); pc = abs(p-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        rows.append(line); prev = line
    return w, h, bpp, rows
def write(path, w, h, rows):
    def chunk(t, data): return struct.pack('>I', len(data)) + t + data + struct.pack('>I', zlib.crc32(t + data) & 0xffffffff)
    raw = b''.join(b'\x00' + bytes(r) for r in rows)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
for path in sys.argv[1:]:
    w, h, bpp, rows = read(path)
    table = bytes(max(0, min(255, round((v - 23) / 232 * 255))) for v in range(256))
    out = []
    for line in rows:
        o = bytearray(b'\xff' * (w * 4))
        o[3::4] = line[0::bpp].translate(table)
        out.append(o)
    write(path, w, h, out)
    print(path, w, h, 'corner alpha', out[0][3], 'middle alpha', out[h//2][(w//2)*4+3])
