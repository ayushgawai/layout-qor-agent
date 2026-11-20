"""Placement: greedy + simulated annealing on PMOS/NMOS rows.
Mirrors cpp/placer.cpp; uses the C++ binary instead when built (see placer_cli)."""
import json, math, os, random, subprocess
from dataclasses import dataclass, asdict

@dataclass
class Placed:
    name: str; x: int; row: int; w: int  # row 1=PMOS, 0=NMOS; x,w in grid units

def _rows(nl): return {dv.name: (1 if dv.kind == "pmos" else 0) for dv in nl.devices}

def cost(nl, place, w_hpwl=1.0, w_sym=2.0):
    pos = {p.name: p for p in place}
    hpwl = 0.0
    for net, terms in nl.nets().items():
        pts = [(pos[d].x + pos[d].w / 2, pos[d].row) for d, _ in terms if d in pos]
        if len(pts) > 1:
            hpwl += (max(p[0] for p in pts) - min(p[0] for p in pts)) + (max(p[1] for p in pts) - min(p[1] for p in pts))
    width = max((p.x + p.w for p in place), default=0)
    area = width * 2
    sym = sum(abs(pos[a].x - pos[b].x) for a, b in nl.matched_pairs() if a in pos and b in pos)
    return area + w_hpwl * hpwl + w_sym * sym, {"area": area, "hpwl": hpwl, "symmetry": sym}

def greedy(nl):
    rows = _rows(nl); cur = {0: 0, 1: 0}; out = []
    for dv in nl.devices:  # netlist order = greedy baseline
        r = rows[dv.name]; out.append(Placed(dv.name, cur[r], r, dv.width_units)); cur[r] += dv.width_units + 1
    return out

def anneal(nl, iters=4000, seed=0, w_hpwl=1.0, w_sym=2.0, folds=None):
    rng = random.Random(seed); folds = folds or {}
    devs = {dv.name: dv for dv in nl.devices}; rows = _rows(nl)
    def mk(order):
        cur = {0: 0, 1: 0}; out = []
        for n in order:
            r = rows[n]; w = max(1, devs[n].width_units // folds.get(n, 1))
            out.append(Placed(n, cur[r], r, w)); cur[r] += w + 1
        return out
    order = [dv.name for dv in nl.devices]
    cur_p = mk(order)
    cur_c, _ = cost(nl, cur_p, w_hpwl, w_sym); best, best_c = list(cur_p), cur_c
    for i in range(iters):
        T = max(0.01, 2.0 * (1 - i / iters))
        o = order[:]; a, b = rng.randrange(len(o)), rng.randrange(len(o)); o[a], o[b] = o[b], o[a]
        p = mk(o); c, _ = cost(nl, p, w_hpwl, w_sym)
        if c <= cur_c or rng.random() < math.exp(-(c - cur_c) / T):
            order, cur_c = o, c
            if c < best_c: best, best_c = [Placed(q.name, q.x, q.row, q.w) for q in p], c
    return best

def placer_cli(nl, binary, mode="sa", seed=0):
    """Run C++ placer via JSON stdin/stdout. Returns None if binary missing."""
    if not binary or not os.path.exists(binary): return None
    inp = {"mode": mode, "seed": seed, "matched": nl.matched_pairs(),
           "devices": [{"name": d.name, "kind": d.kind, "w": d.width_units,
                        "nets": [d.d, d.g, d.s]} for d in nl.devices]}
    r = subprocess.run([binary], input=json.dumps(inp), capture_output=True, text=True, timeout=60)
    if r.returncode: return None
    return [Placed(p["name"], p["x"], p["row"], p["w"]) for p in json.loads(r.stdout)["placement"]]

def place(nl, mode="sa", seed=0, binary=None, **kw):
    if binary:
        got = placer_cli(nl, binary, mode, seed)
        if got is not None: return got
    return anneal(nl, seed=seed, **kw) if mode == "sa" else greedy(nl)

def to_json(place): return [asdict(p) for p in place]
