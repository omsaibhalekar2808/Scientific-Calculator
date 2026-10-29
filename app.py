import ast
import cmath
import math
import operator
import random
import re
from fractions import Fraction
from pathlib import Path
import os
from flask import Flask, jsonify, request, send_from_directory

BASE = Path(__file__).parent
app = Flask(__name__)


class CalcError(Exception):
    pass

CONSTANTS = [
    ("π", "Pi (Archimedes' constant)", math.pi, "", "Math"),
    ("e", "Euler's number", math.e, "", "Math"),
    ("φ", "Golden ratio", (1 + 5 ** 0.5) / 2, "", "Math"),
    ("√2", "Pythagoras' constant", math.sqrt(2), "", "Math"),
    ("ln(2)", "Natural log of 2", math.log(2), "", "Math"),
    ("ln(10)", "Natural log of 10", math.log(10), "", "Math"),
    ("c", "Speed of light in vacuum", 299792458.0, "m/s", "Universal"),
    ("G", "Newtonian constant of gravitation", 6.67430e-11, "N·m²/kg²", "Universal"),
    ("h", "Planck constant", 6.62607015e-34, "J·s", "Universal"),
    ("ħ", "Reduced Planck constant", 1.054571817e-34, "J·s", "Universal"),
    ("g", "Standard acceleration of gravity", 9.80665, "m/s²", "Universal"),
    ("e", "Elementary charge", 1.602176634e-19, "C", "Physics & EM"),
    ("ε₀", "Vacuum electric permittivity", 8.8541878128e-12, "F/m", "Physics & EM"),
    ("μ₀", "Vacuum magnetic permeability", 1.25663706212e-6, "N/A²", "Physics & EM"),
    ("σ", "Stefan-Boltzmann constant", 5.670374419e-8, "W/(m²·K⁴)", "Physics & EM"),
    ("atm", "Standard atmosphere", 101325.0, "Pa", "Universal"),
    ("Nₐ", "Avogadro constant", 6.02214076e23, "mol⁻¹", "Atomic"),
    ("k_B", "Boltzmann constant", 1.380649e-23, "J/K", "Physics & EM"),
    ("R", "Molar gas constant", 8.314462618, "J/(mol·K)", "Physics & EM"),
    ("F", "Faraday constant", 96485.33212, "C/mol", "Physics & EM"),
    ("mₑ", "Electron mass", 9.1093837015e-31, "kg", "Atomic"),
    ("mₚ", "Proton mass", 1.67262192369e-27, "kg", "Atomic"),
    ("u", "Atomic mass unit", 1.66053906660e-27, "kg", "Atomic"),
]


BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def prep(s, angle="D"):
    """Translate calculator tokens into a Python expression string."""
    s = (s.replace("×", "*").replace("÷", "/").replace("−", "-")
          .replace("π", "pi").replace("^", "**")
          .replace("√(", "sqrt(").replace("∛(", "cbrt("))
    deg_factor = {"D": "", "R": "*(pi/180)", "G": "*(10/9)"}[angle]
    s = s.replace("°", deg_factor)
    s = re.sub(r"Ran#", lambda m: "%.3f" % random.random(), s)
    s = s.replace("%", "/100")
    pat = re.compile(r"(\d+(?:\.\d+)?|\([^()]*\)|[A-Za-z]+)!")
    for _ in range(10):
        s2 = pat.sub(lambda m: "fact(%s)" % m.group(1), s)
        if s2 == s:
            break
        s = s2
    s = re.sub(r"(?<=[\d\)])\s*(?=[A-Za-z(])", "*", s)
    s = re.sub(r"\b(pi|e)\b(?=\()", r"\1*", s)
    return s


def build_namespace(angle, cplx, ans, variables, extra):
    m = cmath if cplx else math

    def rad(x):
        if angle == "D":
            return x * math.pi / 180
        if angle == "G":
            return x * math.pi / 200
        return x

    def deg(x):
        if angle == "D":
            return x * 180 / math.pi
        if angle == "G":
            return x * 200 / math.pi
        return x

    def clean(x):
        if isinstance(x, complex):
            return complex(clean(x.real), clean(x.imag))
        return 0.0 if abs(x) < 1e-14 else x

    def trig(fn):
        return lambda x: clean(fn(rad(x)))

    def itrig(fn):
        return lambda x: clean(deg(fn(x)))

    def tan(x):
        r = m.tan(rad(x))
        if not cplx and abs(r) > 1e14:
            raise CalcError("Math ERROR")
        return clean(r)

    def fact(n):
        if isinstance(n, complex) or n < 0 or n != int(n) or n > 170:
            raise CalcError("Math ERROR")
        return float(math.factorial(int(n)))

    def _ints(*vals):
        for v in vals:
            if isinstance(v, complex) or v != int(v) or v < 0:
                raise CalcError("Math ERROR")
        return [int(v) for v in vals]

    def nPr(n, r):
        n, r = _ints(n, r)
        if r > n:
            raise CalcError("Math ERROR")
        return float(math.perm(n, r))

    def nCr(n, r):
        n, r = _ints(n, r)
        if r > n:
            raise CalcError("Math ERROR")
        return float(math.comb(n, r))

    def cbrt(x):
        if isinstance(x, complex):
            return x ** (1 / 3)
        return math.copysign(abs(x) ** (1 / 3), x)

    def root(n, x):
        if not isinstance(x, complex) and x < 0 and float(n).is_integer() and int(n) % 2 == 1:
            return -((-x) ** (1 / n))
        return x ** (1 / n)

    def logb(a, b):
        return m.log(b) / m.log(a)

    funcs = {
        "sin": trig(m.sin), "cos": trig(m.cos), "tan": tan,
        "asin": itrig(m.asin), "acos": itrig(m.acos), "atan": itrig(m.atan),
        "sinh": m.sinh, "cosh": m.cosh, "tanh": m.tanh,
        "asinh": m.asinh, "acosh": m.acosh, "atanh": m.atanh,
        "sqrt": m.sqrt, "cbrt": cbrt, "ln": m.log, "log": m.log10,
        "logb": logb, "exp": m.exp, "abs": abs, "fact": fact,
        "nPr": nPr, "nCr": nCr, "root": root,
    }
    names = {"pi": math.pi, "e": math.e}
    for k in "ABCDEFMXY":
        names[k] = 0.0
    for k, v in (variables or {}).items():
        if k in names and k not in ("pi", "e"):
            names[k] = complex(*v) if isinstance(v, list) else float(v)
    names["Ans"] = complex(*ans) if isinstance(ans, list) else float(ans or 0)
    if cplx:
        names["i"] = 1j
    if extra:
        names.update(extra)
    return names, funcs


class Expr:
    """A compiled calculator expression that can be evaluated many times."""

    def __init__(self, text, angle="D", cplx=False):
        self.angle, self.cplx = angle, cplx
        try:
            self.tree = ast.parse(prep(text, angle), mode="eval")
        except SyntaxError:
            raise CalcError("Syntax ERROR")

    def __call__(self, ans=0, variables=None, extra=None):
        names, funcs = build_namespace(self.angle, self.cplx, ans, variables, extra)
        try:
            return self._ev(self.tree.body, names, funcs)
        except CalcError:
            raise
        except TypeError:
            raise CalcError("Syntax ERROR")
        except (ZeroDivisionError, ValueError, OverflowError, RecursionError):
            raise CalcError("Math ERROR")

    def _ev(self, n, names, funcs):
        ev = lambda x: self._ev(x, names, funcs)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) \
                and not isinstance(n.value, bool):
            return float(n.value)
        if isinstance(n, ast.BinOp) and type(n.op) in BINOPS:
            a, b = ev(n.left), ev(n.right)
            r = BINOPS[type(n.op)](a, b)
            if isinstance(n.op, (ast.Add, ast.Sub)) and abs(r) < 1e-12 * max(abs(a), abs(b)):
                r = 0.0  # cancellation noise, e.g. 0.1+0.2-0.3
            if isinstance(r, complex) and not self.cplx:
                raise CalcError("Math ERROR")
            return r
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            v = ev(n.operand)
            return -v if isinstance(n.op, ast.USub) else v
        if isinstance(n, ast.Name):
            if n.id in names:
                return names[n.id]
            raise CalcError("Syntax ERROR")
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                and n.func.id in funcs and not n.keywords:
            r = funcs[n.func.id](*[ev(a) for a in n.args])
            if isinstance(r, complex) and not self.cplx:
                raise CalcError("Math ERROR")
            return r
        raise CalcError("Syntax ERROR")

def fmt_real(x, fix=None, eng=False):
    x = float(x)
    if x != x or x in (math.inf, -math.inf):
        raise CalcError("Math ERROR")
    if x == 0:
        return "0" if fix is None else "%.*f" % (fix, 0)
    if eng:
        e = int(math.floor(math.log10(abs(x))))
        e3 = (e // 3) * 3
        mant = ("%.9g" % (x / 10 ** e3))
        return "%s×10^%d" % (mant, e3)
    if fix is not None and abs(x) < 1e10:
        return "%.*f" % (fix, x)
    if abs(x) >= 1e10 or abs(x) < 1e-9:
        mant, e = ("%.9e" % x).split("e")
        mant = mant.rstrip("0").rstrip(".")
        return "%s×10^%d" % (mant, int(e))
    s = "%.10g" % x
    if "e" in s:
        mant, e = ("%.9e" % x).split("e")
        return "%s×10^%d" % (mant.rstrip("0").rstrip("."), int(e))
    return "0" if s == "-0" else s


def fmt_complex(z, fix=None):
    re_, im = z.real, z.imag
    if abs(im) < 1e-12:
        return fmt_real(re_, fix)
    ims = fmt_real(abs(im), fix)
    ims = "" if ims == "1" else ims
    if abs(re_) < 1e-12:
        return ("-" if im < 0 else "") + ims + "i"
    return "%s%s%si" % (fmt_real(re_, fix), "-" if im < 0 else "+", ims)


def fraction_forms(x):
    try:
        f = Fraction(x).limit_denominator(10000)
    except (OverflowError, ValueError):
        return None, None
    if f.denominator == 1 or abs(float(f) - x) > 1e-11 * max(1.0, abs(x)):
        return None, None
    sign = "-" if f < 0 else ""
    f = abs(f)
    frac = "%s%d/%d" % (sign, f.numerator, f.denominator)
    whole, rem = divmod(f.numerator, f.denominator)
    mixed = "%s%d %d/%d" % (sign, whole, rem, f.denominator) if whole else None
    return frac, mixed


def num(text, angle="D"):
    v = Expr(text, angle)()
    return float(v)


def parse_fix(v):
    return None if v in (None, "", "norm") else int(v)


@app.route("/")
def index():
    return send_from_directory(BASE / "templates", "index.html")


@app.route("/api/constants")
def constants():
    return jsonify([
        {"symbol": s, "name": n, "value": v, "repr": repr(v), "unit": u, "category": c}
        for s, n, v, u, c in CONSTANTS
    ])


@app.route("/api/calc", methods=["POST"])
def calc():
    d = request.get_json(force=True)
    try:
        expr = Expr(d.get("expr", ""), d.get("angle", "D"), bool(d.get("cplx")))
        v = expr(d.get("ans", 0), d.get("vars"))
        fix = parse_fix(d.get("fix"))
        if isinstance(v, complex):
            if abs(v.imag) < 1e-12:
                v = v.real
            else:
                t = fmt_complex(v, fix)
                return jsonify(ok=True, text=t, eng=t, frac=None, mixed=None,
                               value=[v.real, v.imag])
        t = fmt_real(v, fix)
        frac, mixed = fraction_forms(v)
        return jsonify(ok=True, text=t, eng=fmt_real(v, eng=True),
                       frac=frac, mixed=mixed, value=float(v))
    except CalcError as e:
        return jsonify(ok=False, error=str(e))


UNITS = {
    "Length": {"m": 1, "km": 1000, "cm": 0.01, "mm": 0.001, "mi": 1609.344,
               "yd": 0.9144, "ft": 0.3048, "in": 0.0254, "nmi": 1852},
    "Mass": {"kg": 1, "g": 0.001, "mg": 1e-6, "t": 1000, "lb": 0.45359237, "oz": 0.028349523125},
    "Time": {"s": 1, "min": 60, "h": 3600, "day": 86400, "week": 604800},
    "Speed": {"m/s": 1, "km/h": 1 / 3.6, "mph": 0.44704, "kn": 0.514444444},
    "Energy": {"J": 1, "kJ": 1000, "cal": 4.184, "kcal": 4184, "Wh": 3600,
               "kWh": 3.6e6, "eV": 1.602176634e-19},
    "Pressure": {"Pa": 1, "kPa": 1000, "bar": 1e5, "atm": 101325, "psi": 6894.757293168,
                 "mmHg": 133.322387415},
    "Area": {"m²": 1, "ha": 1e4, "km²": 1e6, "acre": 4046.8564224, "ft²": 0.09290304},
    "Volume": {"L": 1, "mL": 0.001, "m³": 1000, "gal": 3.785411784, "pt": 0.473176473},
    "Angle": {"deg": 1, "rad": 180 / math.pi, "grad": 0.9},
    "Temperature": {"°C": None, "°F": None, "K": None},
}


@app.route("/api/units")
def units():
    return jsonify({k: list(v) for k, v in UNITS.items()})


def convert(value, cat, a, b):
    if cat == "Temperature":
        k = {"°C": value + 273.15, "°F": (value - 32) * 5 / 9 + 273.15, "K": value}[a]
        return {"°C": k - 273.15, "°F": (k - 273.15) * 9 / 5 + 32, "K": k}[b]
    return value * UNITS[cat][a] / UNITS[cat][b]


def parse_list(text, angle="D"):
    parts = [p for p in re.split(r"[,;\s]+", (text or "").strip()) if p]
    return [num(p, angle) for p in parts]


def parse_matrix(text, angle="D"):
    rows = [r for r in re.split(r"[;\n]", text.strip()) if r.strip()]
    m = [parse_list(r, angle) for r in rows]
    if not m or any(len(r) != len(m[0]) for r in m):
        raise CalcError("Syntax ERROR")
    return m


def mat_str(m):
    return [("Row %d" % (i + 1), "   ".join(fmt_real(v) for v in r)) for i, r in enumerate(m)]


def det(m):
    n = len(m)
    if any(len(r) != n for r in m):
        raise CalcError("Matrix must be square")
    a = [r[:] for r in m]
    d = 1.0
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(a[r][i]))
        if abs(a[p][i]) < 1e-14:
            return 0.0
        if p != i:
            a[i], a[p] = a[p], a[i]
            d = -d
        d *= a[i][i]
        for r in range(i + 1, n):
            f = a[r][i] / a[i][i]
            for c in range(i, n):
                a[r][c] -= f * a[i][c]
    return d


def inverse(m):
    n = len(m)
    if det(m) == 0:
        raise CalcError("Singular matrix (no inverse)")
    a = [m[i][:] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(a[r][i]))
        a[i], a[p] = a[p], a[i]
        piv = a[i][i]
        a[i] = [v / piv for v in a[i]]
        for r in range(n):
            if r != i:
                f = a[r][i]
                a[r] = [x - f * y for x, y in zip(a[r], a[i])]
    return [r[n:] for r in a]


def poly_roots(c):
    c = c[:]
    while c and abs(c[0]) < 1e-14:
        c.pop(0)
    n = len(c) - 1
    if n < 1 or n > 6:
        raise CalcError("Degree must be 1 to 6")
    if n == 1:
        return [complex(-c[1] / c[0])]
    if n == 2:
        a, b, cc = c
        s = cmath.sqrt(b * b - 4 * a * cc)
        return [(-b + s) / (2 * a), (-b - s) / (2 * a)]
    c = [v / c[0] for v in c]
    roots = [(0.4 + 0.9j) ** k for k in range(n)]
    for _ in range(1000):
        delta = 0
        for i in range(n):
            r = roots[i]
            p = sum(co * r ** (n - k) for k, co in enumerate(c))
            d = 1
            for j in range(n):
                if j != i:
                    d *= (r - roots[j])
            step = p / d
            roots[i] = r - step
            delta = max(delta, abs(step))
        if delta < 1e-14:
            break
    return roots


def fmt_root(z):
    z = complex(round(z.real, 10), round(z.imag, 10))
    return fmt_complex(z)


@app.route("/api/tool/<name>", methods=["POST"])
def tool(name):
    d = request.get_json(force=True)
    f = d.get("fields", {})
    ang = d.get("angle", "D")
    try:
        rows = TOOLS[name](f, ang)
        return jsonify(ok=True, rows=rows)
    except CalcError as e:
        return jsonify(ok=False, error=str(e))
    except (KeyError, ValueError, ZeroDivisionError, OverflowError):
        return jsonify(ok=False, error="Math ERROR")


def fx_of(text, ang):
    e = Expr(text, ang)
    return lambda v: float(e(extra={"x": v, "X": v}))


def t_integrate(f, ang):
    g = fx_of(f["f"], ang)
    a, b = num(f["a"], ang), num(f["b"], ang)
    n = 2000
    h = (b - a) / n
    s = g(a) + g(b)
    for i in range(1, n):
        s += g(a + i * h) * (4 if i % 2 else 2)
    return [["∫ f(x) dx", fmt_real(s * h / 3)], ["from → to", "%s → %s" % (fmt_real(a), fmt_real(b))]]


def t_derivative(f, ang):
    g = fx_of(f["f"], ang)
    x = num(f["x0"], ang)
    h = 1e-3 * max(1.0, abs(x))
    d = (-g(x + 2 * h) + 8 * g(x + h) - 8 * g(x - h) + g(x - 2 * h)) / (12 * h)
    return [["f′(x)", fmt_real(round(d, 8))], ["at x =", fmt_real(x)], ["f(x)", fmt_real(g(x))]]


def t_solve(f, ang):
    text = f["f"]
    if "=" in text:
        l, r = text.split("=", 1)
        text = "(%s)-(%s)" % (l, r)
    g = fx_of(text, ang)
    x = num(f.get("x0") or "1", ang)
    for _ in range(100):
        h = 1e-6 * max(1.0, abs(x))
        d = (g(x + h) - g(x - h)) / (2 * h)
        if d == 0:
            break
        nx = x - g(x) / d
        if abs(nx - x) < 1e-12:
            x = nx
            break
        x = nx
    if abs(g(x)) > 1e-7:
        found = None
        prev = None
        steps = [i / 10 for i in range(-1000, 1001)]
        for s in steps:
            try:
                v = g(s)
            except CalcError:
                prev = None
                continue
            if prev and prev[1] * v <= 0:
                lo, hi = prev[0], s
                for _ in range(100):
                    mid = (lo + hi) / 2
                    if g(lo) * g(mid) <= 0:
                        hi = mid
                    else:
                        lo = mid
                found = (lo + hi) / 2
                break
            prev = (s, v)
        if found is None:
            raise CalcError("Can't Solve")
        x = found
    return [["x =", fmt_real(round(x, 10))], ["residual", fmt_real(g(x))]]


def t_table(f, ang):
    g = fx_of(f["f"], ang)
    a, b, st = num(f["start"], ang), num(f["end"], ang), num(f["step"], ang)
    if st == 0 or (b - a) / st < 0 or (b - a) / st > 100:
        raise CalcError("Check start / end / step (max 100 rows)")
    rows, i = [], 0
    while a + i * st <= b + 1e-12 if st > 0 else a + i * st >= b - 1e-12:
        x = a + i * st
        try:
            rows.append(["x = " + fmt_real(round(x, 10)), fmt_real(g(x))])
        except CalcError as e:
            rows.append(["x = " + fmt_real(round(x, 10)), str(e)])
        i += 1
    return rows


def t_eqn(f, ang):
    c = parse_list(f["c"], ang)
    roots = poly_roots(c)
    rows = [["Degree", str(len(roots))]]
    if len(roots) == 2:
        rows.append(["Discriminant Δ", fmt_real(c[1] ** 2 - 4 * c[0] * c[2])])
    for i, r in enumerate(roots, 1):
        rows.append(["x%d" % i, fmt_root(r)])
    return rows


def t_stat(f, ang):
    xs = parse_list(f["x"], ang)
    if not xs:
        raise CalcError("Enter some data")
    n = len(xs)
    sx = sum(xs)
    sx2 = sum(v * v for v in xs)
    mean = sx / n
    var = sx2 / n - mean ** 2
    srt = sorted(xs)
    med = srt[n // 2] if n % 2 else (srt[n // 2 - 1] + srt[n // 2]) / 2
    rows = [["n", str(n)], ["Σx", fmt_real(sx)], ["Σx²", fmt_real(sx2)], ["x̄ (mean)", fmt_real(mean)],
            ["σx (population)", fmt_real(math.sqrt(max(var, 0)))]]
    if n > 1:
        rows.append(["sx (sample)", fmt_real(math.sqrt(max((sx2 - n * mean ** 2) / (n - 1), 0)))])
    rows += [["min", fmt_real(srt[0])], ["median", fmt_real(med)], ["max", fmt_real(srt[-1])]]
    if (f.get("y") or "").strip():
        ys = parse_list(f["y"], ang)
        if len(ys) != n:
            raise CalcError("X and Y need the same number of values")
        sy, sxy, sy2 = sum(ys), sum(a * b for a, b in zip(xs, ys)), sum(v * v for v in ys)
        den = n * sx2 - sx ** 2
        b = (n * sxy - sx * sy) / den
        a = (sy - b * sx) / n
        r = (n * sxy - sx * sy) / math.sqrt(den * (n * sy2 - sy ** 2))
        rows += [["ȳ (mean)", fmt_real(sy / n)], ["Regression y = A + Bx", ""],
                 ["A", fmt_real(a)], ["B", fmt_real(b)], ["r", fmt_real(r)]]
    return rows


def t_base(f, ang):
    base = {"DEC": 10, "HEX": 16, "BIN": 2, "OCT": 8}[f["base"]]
    try:
        v = int(f["value"].strip().replace(" ", ""), base)
    except ValueError:
        raise CalcError("Invalid number for that base")
    sgn = "-" if v < 0 else ""
    a = abs(v)
    return [["DEC", str(v)], ["HEX", sgn + format(a, "X")], ["BIN", sgn + format(a, "b")],
            ["OCT", sgn + format(a, "o")]]


def t_conv(f, ang):
    v = num(f["value"], ang)
    c1, a = f["from"].split("|")
    c2, b = f["to"].split("|")
    if c1 != c2:
        raise CalcError("Units are not compatible (%s vs %s)" % (c1, c2))
    r = convert(v, c1, a, b)
    return [["%s %s =" % (fmt_real(v), a), "%s %s" % (fmt_real(r), b)],
            ["Category", c1]]


def t_matrix(f, ang):
    A = parse_matrix(f["a"], ang)
    op = f["op"]
    if op == "det":
        return [["det(A)", fmt_real(det(A))]]
    if op == "inv":
        return mat_str(inverse(A))
    if op == "tr":
        return mat_str([list(r) for r in zip(*A)])
    B = parse_matrix(f["b"], ang)
    if op in ("add", "sub"):
        if len(A) != len(B) or len(A[0]) != len(B[0]):
            raise CalcError("Dimension ERROR")
        s = 1 if op == "add" else -1
        return mat_str([[x + s * y for x, y in zip(r1, r2)] for r1, r2 in zip(A, B)])
    if len(A[0]) != len(B):
        raise CalcError("Dimension ERROR")
    return mat_str([[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
                    for i in range(len(A))])


def t_vector(f, ang):
    A = parse_list(f["a"], ang)
    op = f["op"]
    mag = lambda v: math.sqrt(sum(x * x for x in v))
    if op == "abs":
        return [["|A|", fmt_real(mag(A))]]
    B = parse_list(f["b"], ang)
    if len(A) != len(B):
        raise CalcError("Dimension ERROR")
    if op in ("add", "sub"):
        s = 1 if op == "add" else -1
        r = [x + s * y for x, y in zip(A, B)]
        return [["(" + ", ".join(fmt_real(v) for v in r) + ")", ""]]
    if op == "dot":
        return [["A · B", fmt_real(sum(x * y for x, y in zip(A, B)))]]
    if op == "cross":
        if len(A) != 3:
            raise CalcError("Cross product needs 3D vectors")
        r = [A[1] * B[2] - A[2] * B[1], A[2] * B[0] - A[0] * B[2], A[0] * B[1] - A[1] * B[0]]
        return [["A × B", "(" + ", ".join(fmt_real(v) for v in r) + ")"]]
    c = sum(x * y for x, y in zip(A, B)) / (mag(A) * mag(B))
    return [["Angle (degrees)", fmt_real(math.degrees(math.acos(max(-1, min(1, c)))))]]


TOOLS = {
    "integrate": t_integrate, "derivative": t_derivative, "solve": t_solve,
    "table": t_table, "eqn": t_eqn, "stat": t_stat, "base": t_base,
    "conv": t_conv, "matrix": t_matrix, "vector": t_vector,
}

app.run(debug=False, host="127.0.0.1", port=5000)