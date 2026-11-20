"""Row legalizer: OR-Tools CP-SAT when installed, else left-pack fallback (same semantics)."""
from .placer import Placed

def legalize(nl, place, spacing=1):
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        return _pack(place, spacing)  # ponytail: fallback exact for fixed row order
    pos = {p.name: p for p in place}
    m = cp_model.CpModel(); xs = {}
    horizon = sum(p.w for p in place) + spacing * len(place) + 10
    for p in place: xs[p.name] = m.NewIntVar(0, horizon, "x_" + p.name)
    for row in (0, 1):
        ps = [p for p in place if p.row == row]
        ivs = [m.NewIntervalVar(xs[p.name], p.w, xs[p.name] + p.w, "i_" + p.name) for p in ps]
        m.AddNoOverlap(ivs)
        for a, b in zip(ps, ps[1:]): m.Add(xs[b.name] >= xs[a.name])  # keep order
    m.Minimize(sum(xs.values()))
    s = cp_model.CpSolver(); s.Solve(m)
    return [Placed(p.name, s.Value(xs[p.name]), p.row, p.w) for p in place]

def _pack(place, spacing=1):
    cur = {0: 0, 1: 0}; out = []
    for p in sorted(place, key=lambda q: (q.row, q.x)):
        out.append(Placed(p.name, cur[p.row], p.row, p.w)); cur[p.row] += p.w + spacing
    return sorted(out, key=lambda q: q.name)
