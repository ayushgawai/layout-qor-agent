"""SPICE subcircuit parser -> device graph. Stdlib only."""
import re
from dataclasses import dataclass, field

@dataclass
class Device:
    name: str; kind: str  # nmos/pmos
    d: str; g: str; s: str; b: str
    model: str; w: float = 1.0; l: float = 0.15; nf: int = 1
    @property
    def width_units(self): return max(1, round(self.w * self.nf))  # grid units

@dataclass
class Netlist:
    name: str; pins: list; devices: list = field(default_factory=list)
    def nets(self):
        out = {}
        for dv in self.devices:
            for term, net in (("d", dv.d), ("g", dv.g), ("s", dv.s)):
                out.setdefault(net, []).append((dv.name, term))
        return out
    def matched_pairs(self):
        """Devices sharing model+W/L (heuristic for symmetry requirement)."""
        pairs, seen = [], {}
        for dv in self.devices:
            k = (dv.kind, dv.w, dv.l)
            if k in seen: pairs.append((seen[k], dv.name))
            else: seen[k] = dv.name
        return pairs

def _params(toks):
    p = {}
    for t in toks:
        if "=" in t:
            k, v = t.split("=", 1); p[k.lower()] = v
    return p

def _num(v, default):
    if v is None: return default
    m = re.match(r"([\d.]+)([a-z]*)", v.lower())
    scale = {"": 1, "u": 1, "n": 1e-3, "k": 1e3}.get(m.group(2), 1)  # treat u as unit grid
    return float(m.group(1)) * scale

def parse(text):
    name, pins, devs = None, [], []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("*"): continue
        if line.startswith("+"): continue  # ponytail: no line continuations in examples
        toks = line.split(); low = line.lower()
        if low.startswith(".subckt"):
            name, pins = toks[1], toks[2:]
        elif low.startswith(".ends"): break
        elif toks[0].lower().startswith("m") and len(toks) >= 6:
            p = _params(toks[6:])
            model = toks[5].lower()
            devs.append(Device(toks[0], "pmos" if "pfet" in model or model.startswith("p") else "nmos",
                               toks[1], toks[2], toks[3], toks[4], model,
                               _num(p.get("w"), 1.0), _num(p.get("l"), 0.15),
                               int(float(_num(p.get("nf", p.get("fingers")), 1)))))
    if name is None: raise ValueError("no .subckt found")
    return Netlist(name, pins, devs)

def load(path):
    with open(path) as f: return parse(f.read())
