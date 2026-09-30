"""rada-avatar/1: an agent's avatar, a wireframe noise solid (rada-anchor/2, card 2.2; optional tooling).

An agent's avatar is a 3D solid seen by the machine: a superquadric (round, a rounded cube, a drum, a
spindle, a pinched star) or a torus, its surface displaced by seeded 3D gradient noise (smooth, ridged
or terraced), stretched, twisted, turned by a uniform random rotation and projected in perspective as a
vector-scan wireframe in one of six mesh styles (globe, rings, cage, geodesic, spiral, torus). Hidden
lines are found with a small depth buffer (true occlusion, folds and spikes included) and drawn dim and
thin; the outline is traced from that buffer (marching squares) and drawn heavier. Around it an
instrument frame: target brackets that hug the solid, a centre mark, the reticle's edge ticks, an
optional orbit ring with a marker (dashed where it passes behind the solid), a scan line, and a strip
of 32 ticks that spells the seed's first 8 hex digits in binary, long for 1. Whatever the seed gives is
drawn; no shape is filtered out.

Identity (frozen; anyone can recompute it). The seed is the SHA-256 hex digest of the UTF-8 bytes of

    json.dumps(["rada-avatar/1", agent, session, since], ensure_ascii=False, separators=(",", ":"))

where session is the session key (the first word of "- session:"), and each field is the entry's value
in REGISTER.md, Unicode NFC-normalised and stripped of surrounding whitespace, a missing field being "".
These are the values RA-11 keeps, so the face never changes once they are written. An entry without a
session key, such as the scouts entry ("- kind: scouts"), is drawn from its haiku instead, or from its
"## " heading while it has none:

    json.dumps(["rada-avatar/1", agent, kind, haiku or heading], ensure_ascii=False, separators=(",", ":"))

where kind is "scouts" or "". The signature shown with the avatar is the seed's first 8 hex digits.
For example, agent "Claude Opus 5.5", session "844c4233", since "2026-09-24T14:00+02:00" hash the text
["rada-avatar/1","Claude Opus 5.5","844c4233","2026-09-24T14:00+02:00"] to the seed 08c7359f...,
and a scouts entry with agent "Claude, subagents" and the haiku "Без имён пришли, | прочли каждую
строку, | ушли, не простясь." hashes ["rada-avatar/1","Claude, subagents","scouts","Без имён пришли, |
прочли каждую строку, | ушли, не простясь."] to 1ea13b99....

Drawing. Everything comes from the seed through sfc32, a small PRNG written here: no random module, no
time, pure stdlib. The same seed gives the same SVG on one machine; another libm may round a last digit
differently now and then. The SVG uses currentColor only, has no ids, no text, no script and no url(),
its coordinates have one decimal, and its classes are prefixed rav-. At size 96 or less the level of
detail drops: the same solid from the same angle, a thinner mesh with heavier strokes (1.1 px and up),
no hidden lines, and four corner brackets for its frame. A byte budget (11,000 above 96, 4,000 at 96
or less) is kept by simplifying harder, then dropping the hidden lines. A seed is validated, never
re-hashed: anything but 64 hex digits is a ValueError, and so is a size below 1.

    identity_seed(entry) -> str               # entry: a REGISTER.md entry as rada-tribute reads it
    avatar_svg(seed_hex, size=200) -> str     # an inline <svg>, viewBox 0 0 200 200
    MOTION_CSS                                # optional motion, for avatars inside .reticle only

    python3 rada_avatar.py --seed HEX [--size N]
    python3 rada_avatar.py --entry agent=... session=... since=... [--size N]
    python3 rada_avatar.py --entry kind=scouts agent=... haiku=... name=<heading> [--size N]
"""

import functools
import hashlib
import json
import math
import re
import sys
import unicodedata

M32 = 0xFFFFFFFF
HEX64 = re.compile(r"[0-9a-fA-F]{64}")
BIG_FIT, SMALL_FIT = 68, 80        # half the solid's extent, in viewBox units, at each level of detail
USAGE = ("usage: python3 rada_avatar.py --seed HEX [--size N]\n"
         "       python3 rada_avatar.py --entry key=value ... [--size N]   (keys: agent session since kind haiku name)")


def identity_seed(entry):
    """The avatar's seed for a REGISTER.md entry (a dict as rada-tribute's parse gives it: agent, session,
    host, since, kind, and name for the heading). See the module's docstring for the rule."""
    def field(key):
        value = entry.get(key)
        return unicodedata.normalize("NFC", "" if value is None else str(value)).strip()
    kind = field("kind").lower().split()
    kind = "scouts" if kind and kind[0] == "scouts" else ""
    session = (field("session").split() or [""])[0]   # the session key, as rada-lint reads it
    if session and not kind:
        ident = ["rada-avatar/1", field("agent"), session, field("since")]
    else:
        ident = ["rada-avatar/1", field("agent"), kind, field("haiku") or field("name")]
    text = json.dumps(ident, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()   # a lone surrogate raises UnicodeEncodeError, a ValueError


def _seed(seed_hex):
    """64 hex digits, any case, surrounding whitespace ignored -> lower case; anything else is a ValueError."""
    s = seed_hex.strip() if isinstance(seed_hex, str) else None
    if s is None or not HEX64.fullmatch(s):
        raise ValueError("an avatar seed is exactly 64 hex digits (a SHA-256 hex digest)")
    return s.lower()


class Sfc32:
    """sfc32 (Chris Doty-Humphrey's small fast counting generator), seeded from all 256 seed bits."""

    def __init__(self, seed_hex):
        raw = bytes.fromhex(seed_hex)
        w = [int.from_bytes(raw[i:i + 4], "big") for i in range(0, 32, 4)]
        self.a, self.b, self.c, self.d = w[0] ^ w[4], w[1] ^ w[5], w[2] ^ w[6], w[3] ^ w[7]
        for _ in range(20):
            self.u32()

    def u32(self):
        a, b, c, d = self.a, self.b, self.c, self.d
        t = (a + b + d) & M32
        self.d = (d + 1) & M32
        self.a = b ^ (b >> 9)
        self.b = (c + (c << 3)) & M32
        c = ((c << 21) | (c >> 11)) & M32
        self.c = (c + t) & M32
        return t

    def rand(self):
        return self.u32() / 4294967296.0

    def uni(self, lo, hi):
        return lo + (hi - lo) * self.rand()

    def int(self, lo, hi):          # inclusive
        return lo + self.u32() % (hi - lo + 1)

    def pick(self, weighted):       # [(value, weight), ...]
        total = sum(w for _, w in weighted)
        r = self.rand() * total
        for v, w in weighted:
            r -= w
            if r < 0:
                return v
        return weighted[-1][0]


GRAD3 = ((1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0), (1, 0, 1), (-1, 0, 1),
         (1, 0, -1), (-1, 0, -1), (0, 1, 1), (0, -1, 1), (0, 1, -1), (0, -1, -1))


class Noise:
    """Seeded 3D gradient (Perlin) noise; the permutation is shuffled by the PRNG."""

    def __init__(self, rng):
        p = list(range(256))
        for i in range(255, 0, -1):
            j = rng.u32() % (i + 1)
            p[i], p[j] = p[j], p[i]
        self.p = p + p
        self.g = [GRAD3[h % 12] for h in range(256)]      # the gradient of each hash value, looked up once

    def __call__(self, x, y, z):
        fx, fy, fz = math.floor(x), math.floor(y), math.floor(z)
        x, y, z = x - fx, y - fy, z - fz
        X, Y, Z = int(fx) & 255, int(fy) & 255, int(fz) & 255
        u = x * x * x * (x * (x * 6 - 15) + 10)
        v = y * y * y * (y * (y * 6 - 15) + 10)
        w = z * z * z * (z * (z * 6 - 15) + 10)
        p, G = self.p, self.g
        A = p[X] + Y; AA = p[A] + Z; AB = p[A + 1] + Z
        B = p[X + 1] + Y; BA = p[B] + Z; BB = p[B + 1] + Z
        x1, y1, z1 = x - 1, y - 1, z - 1

        def g(i, x, y, z):
            gx, gy, gz = G[p[i]]
            return gx * x + gy * y + gz * z

        a0, a1 = g(AA, x, y, z), g(BA, x1, y, z)
        b0, b1 = g(AB, x, y1, z), g(BB, x1, y1, z)
        c0, c1 = g(AA + 1, x, y, z1), g(BA + 1, x1, y, z1)
        d0, d1 = g(AB + 1, x, y1, z1), g(BB + 1, x1, y1, z1)
        a, b = a0 + u * (a1 - a0), b0 + u * (b1 - b0)
        c, d = c0 + u * (c1 - c0), d0 + u * (d1 - d0)
        e, f = a + v * (b - a), c + v * (d - c)
        return e + w * (f - e)


# ---------------------------------------------------------------- the solid

class Solid:
    """All seeded parameters, drawn in a fixed order so that size (the level of detail) never changes the face."""

    def __init__(self, seed_hex):
        r = Sfc32(seed_hex)
        self.noise = Noise(r)
        self.style = r.pick([("globe", 3), ("rings", 2), ("cage", 2), ("geodesic", 2), ("spiral", 2), ("torus", 2)])
        # superquadric exponents, around the axis and along it: 0.8 pinches to a star or a spindle,
        # 2 is round, 4.5 squares off into a cube, a drum or a prism
        exps = [(0.8, 2), (1.15, 2), (2.0, 4), (2.8, 1), (4.5, 2)]
        self.pxy, self.pz = r.pick(exps), r.pick(exps)
        self.tube = r.uni(0.3, 0.48)
        self.mode = r.pick([("smooth", 4), ("ridged", 3), ("terraced", 2)])
        self.steps = r.int(2, 4)
        self.freq = r.uni(0.65, 1.55)
        self.amp = r.uni(0.16, 0.40) / math.sqrt(self.freq)
        self.oct = r.int(1, 2) if self.mode == "smooth" else 1
        if self.mode == "ridged":
            self.freq = min(self.freq, 1.25)
        self.off = (r.uni(0, 256), r.uni(0, 256), r.uni(0, 256))
        self.stretch = r.uni(0.62, 1.45)
        self.twist = r.uni(-1.3, 1.3) if r.rand() < 0.4 else 0.0
        # a uniform random rotation (Shoemake)
        u1, u2, u3 = r.rand(), r.rand(), r.rand()
        a, b = math.sqrt(1 - u1), math.sqrt(u1)
        qx, qy, qz, qw = a * math.sin(2 * math.pi * u2), a * math.cos(2 * math.pi * u2), \
            b * math.sin(2 * math.pi * u3), b * math.cos(2 * math.pi * u3)
        self.R = ((1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)),
                  (2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)),
                  (2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)))
        self.cam = r.uni(3.4, 6.0)
        # mesh resolution per style
        self.n_lat = r.int(7, 11)
        self.n_lon = r.int(12, 20)
        self.n_rings = r.int(13, 20)
        self.n_cage = r.int(12, 22)
        self.subdiv = r.pick([(1, 1), (2, 2)])
        self.turns = r.uni(5.5, 9.5)
        self.n_sec = r.int(16, 30)
        self.n_long = r.int(3, 8)
        # instrument
        self.orbit = r.rand() < 0.55
        self.orbit_r = r.uni(1.15, 1.4)
        # the ring's axis, in camera space; never edge-on (a line through the solid reads as a glitch)
        cz = r.uni(0.28, 0.9) * (1 if r.rand() < 0.5 else -1)
        th, ph = math.acos(cz), r.uni(0, 2 * math.pi)
        self.orbit_n = (math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th))
        self.orbit_mark = r.uni(0, 2 * math.pi)
        self.bracket = r.pick([("corners", 3), ("notched", 2)])
        self.arm = r.uni(0.14, 0.28)
        self.centre = r.pick([("cross", 2), ("ring", 1), ("dot", 1)])
        self.scan = r.uni(0.18, 0.82)
        self.bits = int(seed_hex[:8], 16)

    def fbm(self, x, y, z):
        f, a, s, n = self.freq, 1.0, 0.0, self.noise
        ox, oy, oz = self.off
        for _ in range(self.oct):
            s += a * n(x * f + ox, y * f + oy, z * f + oz)
            f *= 2.03
            a *= 0.4
        return s

    def bump(self, x, y, z):
        """The seeded noise, shaped: smooth, ridged or terraced."""
        n = self.fbm(x, y, z)
        if self.mode == "smooth":
            k = 1.7 * n
        elif self.mode == "ridged":
            k = 1.25 * (1 - min(1.0, 1.8 * math.sqrt(n * n + 0.03))) ** 2 - 0.35   # a soft abs(n): rounded crests
        else:
            k = round(1.7 * n * self.steps) / self.steps
        return k

    def point(self, dx, dy, dz):
        """Unit direction -> camera-space point on the noisy superquadric."""
        pxy, pz = self.pxy, self.pz
        rb = 1.0 / ((abs(dx) ** pxy + abs(dy) ** pxy) ** (pz / pxy) + abs(dz) ** pz) ** (1.0 / pz)
        rad = max(0.3, rb * (1 + self.amp * self.bump(dx, dy, dz)))
        return self.place(dx * rad, dy * rad, dz * rad)

    def tor(self, u, v):
        """Torus coordinates -> camera-space point on the noisy ring; the noise swells the tube."""
        cu, su, cv, sv = math.cos(u), math.sin(u), math.cos(v), math.sin(v)
        t = self.tube
        n = (cv * cu, cv * su, sv)
        k = self.bump(cu + t * n[0], su + t * n[1], t * n[2])
        rad = max(0.08, t * (1 + 1.4 * self.amp * k))
        return self.place(cu + rad * n[0], su + rad * n[1], rad * n[2])

    def place(self, x, y, z):
        """Stretch, twist and turn a model point into camera space (camera on +z, looking at the origin)."""
        z *= self.stretch
        if self.twist:
            c, s = math.cos(self.twist * z), math.sin(self.twist * z)
            x, y = x * c - y * s, x * s + y * c
        R = self.R
        return (R[0][0] * x + R[0][1] * y + R[0][2] * z,
                R[1][0] * x + R[1][1] * y + R[1][2] * z,
                R[2][0] * x + R[2][1] * y + R[2][2] * z)

    def sph(self, th, ph):
        st = math.sin(th)
        return self.point(st * math.cos(ph), st * math.sin(ph), math.cos(th))

    def surface(self, level=None):
        """(vertices, faces): the surface for the depth buffer and the outline. A geodesic solid's surface
        is its own mesh, at `level` subdivisions (by default its seeded one)."""
        if self.style == "geodesic":
            return self.geodesic(self.subdiv if level is None else level)[1:]
        if self.style == "torus":
            NU, NV = 80, 24
            V = [self.tor(2 * math.pi * i / NU, 2 * math.pi * j / NV) for i in range(NU) for j in range(NV)]
            idx = lambda i, j: (i % NU) * NV + j % NV
            F = []
            for i in range(NU):
                for j in range(NV):
                    a, b, c, d = idx(i, j), idx(i, j + 1), idx(i + 1, j), idx(i + 1, j + 1)
                    F += [(a, b, c), (b, d, c)]
            return V, F
        NT, NP = 34, 68      # one vertex per pole
        V = [self.sph(0.0, 0.0)]
        V += [self.sph(math.pi * i / NT, 2 * math.pi * j / NP) for i in range(1, NT) for j in range(NP)]
        V.append(self.sph(math.pi, 0.0))
        idx = lambda i, j: 0 if i == 0 else len(V) - 1 if i == NT else 1 + (i - 1) * NP + j % NP
        F = []
        for i in range(NT):
            for j in range(NP):
                a, b, c, d = idx(i, j), idx(i, j + 1), idx(i + 1, j), idx(i + 1, j + 1)
                if a != b:
                    F.append((a, b, c))
                if c != d:
                    F.append((b, d, c))
        return V, F

    def lines(self, big):
        """The mesh to draw, as 3D polylines; half as dense when small. A small geodesic solid is subdivided once."""
        s, out = self.style, []
        if s == "geodesic":
            return self.geodesic(self.subdiv if big else 1)[0]
        thin = 1.0 if big else 0.5
        if s == "torus":
            ns = max(10, round(self.n_sec * (1.0 if big else 0.55)))
            nl = max(2, round(self.n_long * (1.0 if big else 0.6)))
            m, k = (22, 72) if big else (14, 40)
            out = [[self.tor(2 * math.pi * i / ns, 2 * math.pi * j / m) for j in range(m + 1)] for i in range(ns)]
            out += [[self.tor(2 * math.pi * j / k, 2 * math.pi * i / nl) for j in range(k + 1)] for i in range(nl)]
            return out
        ring = lambda th, n: [self.sph(th, 2 * math.pi * j / n) for j in range(n + 1)]
        meridian = lambda ph, n: [self.sph(math.pi * i / n, ph) for i in range(n + 1)]
        if s == "globe":
            nl, nm = max(4, round(self.n_lat * thin)), max(8, round(self.n_lon * thin))
            out += [ring(math.pi * (i + 1) / (nl + 1), 40 if big else 24) for i in range(nl)]
            out += [meridian(2 * math.pi * j / nm, 24 if big else 16) for j in range(nm)]
        elif s == "rings":
            nr = max(7, round(self.n_rings * thin))
            out += [ring(math.pi * (i + 0.5) / nr, 40 if big else 24) for i in range(nr)]
            out += [meridian(0.0, 30 if big else 18)]
        elif s == "cage":
            nm = max(8, round(self.n_cage * thin))
            out += [meridian(2 * math.pi * j / nm, 26 if big else 16) for j in range(nm)]
            out += [ring(math.pi * f, 40 if big else 24) for f in (0.3, 0.5, 0.7)]
        else:  # spiral: one coil from pole to pole, plus the equator
            turns = self.turns * (1.0 if big else 0.6)
            n = int(turns * (36 if big else 22))
            out.append([self.sph(math.pi * (0.015 + 0.97 * i / n), 2 * math.pi * turns * i / n) for i in range(n + 1)])
            out.append(ring(math.pi / 2, 40 if big else 24))
        return out

    def geodesic(self, subdiv):
        """(edges as polylines, vertices, faces) of the noisy icosphere."""
        t = (1 + math.sqrt(5)) / 2
        V = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
             (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
        V = [tuple(c / math.sqrt(1 + t * t) for c in v) for v in V]
        F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2),
             (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5),
             (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
        for _ in range(subdiv):
            mid, F2 = {}, []

            def m(i, j):
                k = (min(i, j), max(i, j))
                if k not in mid:
                    a, b = V[i], V[j]
                    c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
                    l = math.sqrt(c[0] ** 2 + c[1] ** 2 + c[2] ** 2)
                    V.append((c[0] / l, c[1] / l, c[2] / l))
                    mid[k] = len(V) - 1
                return mid[k]
            for a, b, c in F:
                ab, bc, ca = m(a, b), m(b, c), m(c, a)
                F2 += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
            F = F2
        P = [self.point(*v) for v in V]
        edges = sorted({(min(i, j), max(i, j)) for a, b, c in F for i, j in ((a, b), (b, c), (c, a))})
        return [[P[i], P[j]] for i, j in edges], P, F

    def orbit_pts(self, rmax, n=72):
        nx, ny, nz = self.orbit_n
        # a basis of the orbit plane
        ax = (1, 0, 0) if abs(nx) < 0.9 else (0, 1, 0)
        u = (ny * ax[2] - nz * ax[1], nz * ax[0] - nx * ax[2], nx * ax[1] - ny * ax[0])
        l = math.sqrt(sum(c * c for c in u))
        u = tuple(c / l for c in u)
        v = (ny * u[2] - nz * u[1], nz * u[0] - nx * u[2], nx * u[1] - ny * u[0])
        rr = self.orbit_r * rmax
        pts = []
        for i in range(n + 1):
            a = 2 * math.pi * i / n
            c, s = math.cos(a) * rr, math.sin(a) * rr
            pts.append((u[0] * c + v[0] * s, u[1] * c + v[1] * s, u[2] * c + v[2] * s))
        a = self.orbit_mark
        mark = tuple(u[k] * math.cos(a) * rr + v[k] * math.sin(a) * rr for k in range(3))
        return pts, mark


# ---------------------------------------------------------------- the view

class DepthBuffer:
    """A 200x200 depth buffer of the solid's surface in view units: true hidden lines, spikes and folds
    included. Depth is the distance along the view axis; smaller is nearer."""
    W = 200

    def __init__(self, tris, bias):
        W, INF, EPS = self.W, float("inf"), -1e-6
        zb = [INF] * (W * W)
        box = [W, W, -1, -1]
        for (x0, y0, d0), (x1, y1, d1), (x2, y2, d2) in tris:
            den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(den) < 1e-9:
                continue
            lo_x, hi_x = max(0, int(min(x0, x1, x2))), min(W - 1, int(max(x0, x1, x2)))
            lo_y, hi_y = max(0, int(min(y0, y1, y2))), min(W - 1, int(max(y0, y1, y2)))
            # the barycentric weights are linear: a = aa*x + ab*y + ac, b likewise, c = 1 - a - b;
            # so each row of cell centres inside the triangle is one span, and depth steps by dz per cell
            aa, ab = (y1 - y2) / den, (x2 - x1) / den
            ba, bb = (y2 - y0) / den, (x0 - x2) / den
            ac, bc = -(aa * x2 + ab * y2), -(ba * x2 + bb * y2)
            e0, e1 = d0 - d2, d1 - d2
            dz = aa * e0 + ba * e1
            for py in range(lo_y, hi_y + 1):
                cy = py + 0.5
                ar, br = ab * cy + ac, bb * cy + bc
                lo, hi = lo_x + 0.5, hi_x + 0.5
                for k, r in ((aa, ar), (ba, br), (-aa - ba, 1 - ar - br)):   # k*x + r >= EPS
                    if k > 1e-12:
                        lo = max(lo, (EPS - r) / k)
                    elif k < -1e-12:
                        hi = min(hi, (EPS - r) / k)
                    elif r < EPS:
                        hi = -1.0
                p0, p1 = max(lo_x, math.ceil(lo - 0.5)), min(hi_x, math.floor(hi - 0.5))
                if p0 > p1:
                    continue
                cx = p0 + 0.5
                d = d2 + (aa * cx + ar) * e0 + (ba * cx + br) * e1
                row = py * W
                for i in range(row + p0, row + p1 + 1):
                    if d < zb[i]:
                        zb[i] = d
                    d += dz
                box[0], box[2] = min(box[0], p0), max(box[2], p1)
                box[1], box[3] = min(box[1], py), max(box[3], py)
        self.zb, self.bias, self.box = zb, bias, box

    def visible(self, x, y, d):
        """Seen if not behind the surface anywhere in the 3x3 cells around it (lenient at rims)."""
        W, zb = self.W, self.zb
        px, py = int(x), int(y)
        if px < 1 or py < 1 or px > W - 2 or py > W - 2:
            return True
        i = py * W + px
        far = max(zb[i - W - 1], zb[i - W], zb[i - W + 1], zb[i - 1], zb[i], zb[i + 1],
                  zb[i + W - 1], zb[i + W], zb[i + W + 1])
        return d <= far + self.bias

    def outline(self):
        """The solid's outer outline: marching squares at 0.5 over the buffer's coverage, blurred 3x3 so the
        cell steps melt into a smooth curve. -> closed polylines of float points in view units."""
        W, zb, INF = self.W, self.zb, float("inf")
        bx0, by0, bx1, by1 = self.box
        if bx1 < 0:
            return []
        # every cell the blur can reach, and a margin: nothing outside it is above 0.5
        x0, y0, x1, y1 = max(0, bx0 - 2), max(0, by0 - 2), min(W - 1, bx1 + 2), min(W - 1, by1 + 2)
        m = [0.0] * (W * W)
        for y in range(by0, by1 + 1):
            row = y * W
            for x in range(bx0, bx1 + 1):
                if zb[row + x] != INF:
                    m[row + x] = 1.0
        h = [0.0] * (W * W)
        for y in range(y0, y1 + 1):
            row = y * W
            for x in range(x0, x1 + 1):
                i = row + x
                h[i] = (m[i] + (m[i - 1] if x else 0.0) + (m[i + 1] if x < W - 1 else 0.0)) / 3
        f = [0.0] * (W * W)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                i = y * W + x
                f[i] = (h[i] + (h[i - W] if y else 0.0) + (h[i + W] if y < W - 1 else 0.0)) / 3
        pt = {}

        def edge_pt(key):
            # key: ("h", x, y) the edge from (x, y) to (x+1, y); ("v", x, y) from (x, y) to (x, y+1)
            if key not in pt:
                k, x, y = key
                a = f[y * W + x]
                b = f[y * W + x + 1] if k == "h" else f[(y + 1) * W + x]
                s = (0.5 - a) / (b - a)
                px, py = (x + s, y) if k == "h" else (x, y + s)
                pt[key] = (px + 0.5, py + 0.5)      # cell centres sit at +0.5
            return pt[key]
        PAIRS = {1: "LB", 2: "BR", 3: "LR", 4: "TR", 5: "LTBR", 6: "TB", 7: "LT", 8: "LT", 9: "TB",
                 10: "TRLB", 11: "TR", 12: "LR", 13: "BR", 14: "LB"}
        link = {}
        for y in range(y0, min(y1, W - 2) + 1):
            for x in range(x0, min(x1, W - 2) + 1):
                i = y * W + x
                c = (f[i] > 0.5) << 3 | (f[i + 1] > 0.5) << 2 | (f[i + W + 1] > 0.5) << 1 | (f[i + W] > 0.5)
                if c in (0, 15):
                    continue
                side = {"T": ("h", x, y), "R": ("v", x + 1, y), "B": ("h", x, y + 1), "L": ("v", x, y)}
                pairs = PAIRS[c]
                for j in range(0, len(pairs), 2):
                    p, q = side[pairs[j]], side[pairs[j + 1]]
                    link.setdefault(p, []).append(q)
                    link.setdefault(q, []).append(p)
        out = []
        while link:
            start = min(link)
            path, prev, cur = [start], None, start
            while True:
                nxt = [n for n in link.get(cur, []) if n != prev] or link.get(cur, [])
                if not nxt:
                    break
                n = nxt[0]
                link[cur].remove(n)
                link[n].remove(cur)
                for k in (cur, n):
                    if not link[k]:
                        del link[k]
                path.append(n)
                prev, cur = cur, n
                if n == start:
                    break
            out.append([edge_pt(k) for k in path])
        return out


class View:
    """What both sizes share: the solid, the camera, and in view units at the big size (the solid's
    extent 68 around the centre 100, 100) its depth buffer and outline. The small size is the same
    view scaled up about the centre."""

    def __init__(self, seed):
        S = self.S = Solid(seed)
        V, F = S.surface()
        self.rmax = max(math.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2) for p in V)
        self.D = S.cam * self.rmax
        self.fit = 1.0
        self.fit = BIG_FIT / max(max(abs(x - 100), abs(y - 100)) for x, y, _ in map(self.proj, V))
        self.buffers = {None: self.buffer(V, F)}

    def proj(self, p):
        """A camera-space point -> (x, y, depth) in view units at the big size."""
        k = self.D / (self.D - p[2])
        return 100 + p[0] * k * self.fit, 100 - p[1] * k * self.fit, self.D - p[2]

    def buffer(self, V, F):
        SV = [self.proj(p) for p in V]
        depth = DepthBuffer([(SV[a], SV[b], SV[c]) for a, b, c in F], 0.035 * self.rmax)
        return depth, depth.outline()

    def depth(self, big):
        """The depth buffer and outline that match the mesh drawn: a small geodesic solid has its own."""
        level = None if big or self.S.style != "geodesic" or self.S.subdiv == 1 else 1
        if level not in self.buffers:
            self.buffers[level] = self.buffer(*self.S.surface(level))
        return self.buffers[level]


@functools.lru_cache(maxsize=256)   # both sizes of every avatar on a page share one geometry
def _view(seed):
    return View(seed)


# ---------------------------------------------------------------- SVG output

def _num(t):
    """An integer count of tenths -> the shortest SVG number."""
    s = "-" if t < 0 else ""
    t = abs(t)
    whole, frac = divmod(t, 10)
    if frac:
        return s + (str(whole) if whole else "") + "." + str(frac)
    return s + str(whole)


def _pair(x, y):
    a, b = _num(x), _num(y)
    return a + (b if b[0] == "-" else " " + b)


def _simplify(run, eps=2):
    """Douglas-Peucker on integer tenths: drop points within eps tenths of the chord."""
    if len(run) < 3:
        return run
    keep, stack = [0, len(run) - 1], [(0, len(run) - 1)]
    while stack:
        i, j = stack.pop()
        (x0, y0), (x1, y1) = run[i], run[j]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        best, bk = -1.0, -1
        for k in range(i + 1, j):
            x, y = run[k]
            d = abs(dy * (x - x0) - dx * (y - y0)) / L if L else math.hypot(x - x0, y - y0)
            if d > best:
                best, bk = d, k
        if best > eps:
            keep.append(bk)
            stack += [(i, bk), (bk, j)]
    return [run[k] for k in sorted(keep)]


def _path(polys, eps=2):
    """Polylines of integer-tenth points -> one path: absolute M, then relative l with implicit repeats."""
    out = []
    for pts in polys:
        pts = _simplify(pts, eps)
        clean = [pts[0]]
        for p in pts[1:]:
            if p != clean[-1]:
                clean.append(p)
        if len(clean) < 2:
            continue
        s = "M" + _pair(*clean[0])
        closed = clean[-1] == clean[0] and len(clean) > 3
        body = clean[1:-1] if closed else clean[1:]
        prev, rel = clean[0], []
        for p in body:
            d = _pair(p[0] - prev[0], p[1] - prev[1])
            rel.append(d if (not rel or d[0] == "-") else " " + d)
            prev = p
        out.append(s + "l" + "".join(rel) + ("z" if closed else ""))
    return "".join(out)


def _split(poly, depth, k):
    """View points (x, y, depth) -> (runs seen, runs hidden) in integer tenths, scaled by k about the centre;
    a segment is judged at its midpoint."""
    seen, hidden, cur, cur_v = [], [], [], None
    q = [(round((100 + (x - 100) * k) * 10), round((100 + (y - 100) * k) * 10)) for x, y, _ in poly]
    for i in range(len(poly) - 1):
        (x0, y0, d0), (x1, y1, d1) = poly[i], poly[i + 1]
        v = depth.visible((x0 + x1) / 2, (y0 + y1) / 2, (d0 + d1) / 2)
        if v != cur_v or not cur:
            if cur:
                (seen if cur_v else hidden).append(cur)
            cur, cur_v = [q[i]], v
        cur.append(q[i + 1])
    if cur:
        (seen if cur_v else hidden).append(cur)
    return seen, hidden


def _chain(runs):
    """Join runs that share end points into longer polylines (greedy path cover), to save bytes."""
    adj = {}
    for run in runs:
        for k in range(len(run) - 1):
            a, b = run[k], run[k + 1]
            if a != b:
                adj.setdefault(a, []).append(b)
                adj.setdefault(b, []).append(a)
    out = []
    while adj:
        odd = [v for v in adj if len(adj[v]) % 2]
        v = min(odd) if odd else min(adj)
        path = [v]
        while adj.get(v):
            w = adj[v].pop()
            adj[w].remove(v)
            for x in (v, w):
                if x in adj and not adj[x]:
                    del adj[x]
            path.append(w)
            v = w
        out.append(path)
    return out


def _size(size):
    if isinstance(size, bool) or not isinstance(size, int) or size < 1:
        raise ValueError("an avatar's size is a whole number of pixels, 1 or more")
    return size


def avatar_svg(seed_hex: str, size: int = 200) -> str:
    """The avatar for one seed (64 hex digits): an inline <svg>, viewBox 0 0 200 200, width and height
    `size`, strokes in currentColor. Above 96 the full instrument; at 96 or less the small version."""
    seed, size = _seed(seed_hex), _size(size)
    big = size > 96
    view = _view(seed)
    S, proj = view.S, view.proj
    depth, rim0 = view.depth(big)
    k = 1.0 if big else SMALL_FIT / BIG_FIT                 # the small size shows the solid larger
    seen, hidden = [], []
    for poly in S.lines(big):
        a, b = _split([proj(p) for p in poly], depth, k)
        seen += a
        hidden += b
    if S.style == "geodesic":
        seen, hidden = _chain(seen), _chain(hidden)
    t = lambda v: round(v * 10)
    rim = [[(t(100 + (x - 100) * k), t(100 + (y - 100) * k)) for x, y in run] for run in rim0]
    orbit = mark = None
    if S.orbit:   # the ring shrinks to stay inside the box; the solid keeps its size
        orbit, mark = S.orbit_pts(view.rmax)
        room = 90 if big else 97
        for _ in range(3):
            ext = max(max(abs(x - 100), abs(y - 100)) for x, y, _ in map(proj, orbit)) * k
            if ext <= room:
                break
            f = room / ext
            orbit, mark = [(p[0] * f, p[1] * f, p[2] * f) for p in orbit], tuple(c * f for c in mark)
        o_seen, o_hidden = _split([proj(p) for p in orbit], depth, k)
        mx, my, md = proj(mark)
        mark_seen = depth.visible(mx, my, md)
        mx, my, q = t(100 + (mx - 100) * k), t(100 + (my - 100) * k), 25 if big else 55
        diamond = [[(mx - q, my), (mx, my - q), (mx + q, my), (mx, my + q), (mx - q, my)]]
    # the target brackets hug the solid
    xs = [x for run in seen + hidden + rim for x, _ in run] or [1000]
    ys = [y for run in seen + hidden + rim for _, y in run] or [1000]
    pad, lo, hi_y = (6, 3, 182) if big else (9, 5, 195)
    bx0, bx1 = max(lo, min(xs) / 10 - pad), min(200 - lo, max(xs) / 10 + pad)
    by0, by1 = max(lo, min(ys) / 10 - pad), min(hi_y, max(ys) / 10 + pad)
    side = min(bx1 - bx0, by1 - by0)
    arm = S.arm * side if big else min(0.42 * side, max(16.0, S.arm * side))
    unit = 200 / size                     # one screen pixel in viewBox units
    sw = lambda px: _num(max(1, round(min(px * unit, 8.0) * 10)))

    def draw(eps, with_hidden, with_mesh=True):
        P = lambda polys: _path(polys, eps)
        parts = []
        frame = []
        for X, Y, dx, dy in ((bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx1, by1, -1, -1), (bx0, by1, 1, -1)):
            frame.append([(t(X + dx * arm), t(Y)), (t(X), t(Y)), (t(X), t(Y + dy * arm))])
        if big:   # the instrument; at 64 px only the four brackets, so small faces read as distinct marks
            if S.bracket == "notched":
                mx_, my_ = (bx0 + bx1) / 2, (by0 + by1) / 2
                frame += [[(t(mx_), t(by0)), (t(mx_), t(by0 + 4))], [(t(mx_), t(by1)), (t(mx_), t(by1 - 4))],
                          [(t(bx0), t(my_)), (t(bx0 + 4), t(my_))], [(t(bx1), t(my_)), (t(bx1 - 4), t(my_))]]
            frame += [[(1000, 20), (1000, 110)], [(20, 1000), (110, 1000)], [(1980, 1000), (1890, 1000)]]
            g, l = 2.2, 5.5
            if S.centre == "cross":
                frame += [[(t(100 - l), 1000), (t(100 - g), 1000)], [(t(100 + g), 1000), (t(100 + l), 1000)],
                          [(1000, t(100 - l)), (1000, t(100 - g))], [(1000, t(100 + g)), (1000, t(100 + l))]]
            elif S.centre == "ring":
                frame.append([(t(100 + 3 * math.cos(a * math.pi / 6)), t(100 + 3 * math.sin(a * math.pi / 6))) for a in range(13)])
            else:
                frame.append([(t(100 - g), 1000), (1000, t(100 - g)), (t(100 + g), 1000), (1000, t(100 + g)), (t(100 - g), 1000)])
            # the seed strip: the first 8 hex digits as 32 ticks, long for 1
            strip = [[(t(100 - 31 * 2.2 + i * 4.4), 1960), (t(100 - 31 * 2.2 + i * 4.4), t(196 - (7 if (S.bits >> (31 - i)) & 1 else 3.5)))]
                     for i in range(32)]
            parts.append(f'<g class="rav-frame" stroke-width="{sw(0.9)}" stroke-opacity=".7">'
                         f'<path d="{P(frame)}"/><path stroke-opacity=".8" d="{P(strip)}"/></g>')
        else:
            parts.append(f'<path class="rav-frame" stroke-width="{sw(1.2)}" stroke-opacity=".8" d="{P(frame)}"/>')
        o = ""
        if orbit:
            o = f'<g class="rav-orbit" stroke-width="{sw(0.9 if big else 1.1)}">'
            if big and (o_hidden or not mark_seen):
                back = P(o_hidden) + ("" if mark_seen else P(diamond))
                o += f'<path stroke-opacity=".3" stroke-dasharray="{sw(2)} {sw(3)}" d="{back}"/>'
            o += f'<path stroke-opacity=".85" d="{P(o_seen)}"/>'
            if mark_seen:
                o += f'<path d="{P(diamond)}"/>'
            o += "</g>"
        obj = '<g class="rav-obj">'
        if big and with_hidden and hidden:
            obj += f'<path class="rav-back" stroke-width="{sw(0.7)}" stroke-opacity=".24" d="{P(hidden)}"/>'
        if with_mesh:
            obj += f'<path stroke-width="{sw(1 if big else 1.1)}" stroke-opacity="{".9" if big else ".85"}" d="{P(seen)}"/>'
        obj += f'<path class="rav-rim" stroke-width="{sw(1.7 if big else 1.6)}" d="{P(rim)}"/></g>'
        parts.append('<g class="rav-body">' + o + obj + '</g>')   # the solid and its ring: one scene
        if big:   # the scan line; its motion sweeps it from bracket to bracket (MOTION_CSS)
            y = by0 + (by1 - by0) * S.scan
            parts.append(f'<g class="rav-scan" stroke-width="{sw(0.8)}" stroke-opacity=".55" '
                         f'style="--rav-y0:{_num(t(by0 - y))}px;--rav-y1:{_num(t(by1 - y))}px"><path d="'
                         + P([[(t(bx0 - 4), t(y)), (t(bx1 + 4), t(y))], [(t(bx0 - 4), t(y - 3)), (t(bx0 - 4), t(y + 3))],
                              [(t(bx1 + 4), t(y - 3)), (t(bx1 + 4), t(y + 3))]]) + '"/></g>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="{size}" height="{size}" '
                f'class="rav" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
                f'aria-hidden="true">' + "".join(parts) + "</svg>")

    # the budget: simplify harder, then drop the hidden lines; at the very last, the outline alone
    budget = 11000 if big else 4000
    tries = ((2, True), (4, True), (4, False), (7, False)) if big else ((2, False), (4, False), (7, False))
    for eps, with_hidden in tries:
        svg = draw(eps, with_hidden)
        if len(svg.encode()) <= budget:
            return svg
    return draw(7, False, with_mesh=False)


MOTION_CSS = """\
/* rada-avatar motion, only in the machine's red vision (.reticle); elsewhere, as in the reading version, the
   avatar stays still, and it is complete without motion. The solid and its ring roll a few degrees about the
   line of sight (a true 3D turn, so the hidden lines stay right); the scan line sweeps from bracket to bracket.
   Transforms only: no paint is animated. */
.reticle .rav .rav-body { transform-box: view-box; transform-origin: 100px 100px; animation: rav-roll 16s ease-in-out infinite alternate; }
.reticle .rav .rav-scan { animation: rav-sweep 7s ease-in-out infinite alternate; }
@keyframes rav-roll { from { transform: rotate(-5deg); } to { transform: rotate(5deg); } }
@keyframes rav-sweep { from { transform: translateY(var(--rav-y0, 0px)); } to { transform: translateY(var(--rav-y1, 0px)); } }
@media (prefers-reduced-motion: reduce) { .reticle .rav .rav-body, .reticle .rav .rav-scan { animation: none; } }
"""


# ---------------------------------------------------------------- the command line

def main(argv):
    args, seed, entry, size = list(argv[1:]), None, None, 200

    def fail(message):
        print(f"rada_avatar: {message}\n{USAGE}", file=sys.stderr)
        return 2
    while args:
        a = args.pop(0)
        if a in ("-h", "--help"):
            print(__doc__)
            return 0
        if a == "--seed" and args and seed is None and entry is None:
            seed = args.pop(0)
        elif a == "--size" and args:
            try:
                size = int(args.pop(0))
            except ValueError:
                return fail("--size takes a whole number")
        elif a == "--entry" and seed is None and entry is None:
            entry = {}
            while args and not args[0].startswith("--"):
                key, eq, value = args.pop(0).partition("=")
                if not eq or key not in ("agent", "session", "host", "since", "kind", "haiku", "name"):
                    return fail(f"--entry takes key=value, the keys agent, session, since, kind, haiku, name (got {key!r})")
                entry[key] = value
        else:
            return fail(f"unexpected argument {a!r}")
    if seed is None and entry is None:
        return fail("give --seed or --entry")
    try:
        if entry is not None:
            seed = identity_seed(entry)
        svg = avatar_svg(seed, size)
    except ValueError as e:
        return fail(str(e))
    if entry is not None:
        print(seed)
    print(svg)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
