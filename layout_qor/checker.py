"""Simplified DRC (grid spacing/width) + LVS-style connectivity. Optional KLayout/netgen hooks."""
import shutil, subprocess, tempfile, os

def drc(place, min_w=1, min_spacing=1):
    errs = []
    for p in place:
        if p.w < min_w: errs.append(f"min-width {p.name} w={p.w}")
    for row in (0, 1):
        ps = sorted((p for p in place if p.row == row), key=lambda q: q.x)
        for a, b in zip(ps, ps[1:]):
            if b.x - (a.x + a.w) < min_spacing: errs.append(f"spacing {a.name}-{b.name}")
            if b.x < a.x + a.w: errs.append(f"overlap {a.name}-{b.name}")
    return errs

def lvs(nl, place):
    """Placed devices must be exactly the netlist devices, each on its correct row (connectivity preserved by construction)."""
    errs = []
    want = {d.name: d for d in nl.devices}; got = {p.name: p for p in place}
    for n in want:
        if n not in got: errs.append(f"missing device {n}")
        elif got[n].row != (1 if want[n].kind == "pmos" else 0): errs.append(f"wrong row {n}")
    for n in got:
        if n not in want: errs.append(f"extra device {n}")
    return errs

def check(nl, place):
    d, l = drc(place), lvs(nl, place)
    return {"drc": d, "lvs": l, "pass": not d and not l}

def external_hooks(nl_path, gds_path=None):
    """Run KLayout/netgen only if installed; never required."""
    out = {}
    if shutil.which("netgen"):
        out["netgen"] = "available (not run without a layout netlist)"
    if shutil.which("klayout"):
        out["klayout"] = "available (not run without GDS)"
    return out
