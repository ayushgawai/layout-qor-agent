"""CLI: layout-qor run --cell ota5t | layout-qor bench"""
import argparse, json, os
from . import cells
from .placer import place, cost, greedy, anneal
from .legalizer import legalize
from .checker import check
from .agent import RulePlanner
from . import surrogate as sg, sizing

BIN = os.path.join(os.path.dirname(__file__), "..", "cpp", "build", "placer")

def cmd_run(a):
    nl = cells()[a.cell]; r = RulePlanner().run(nl)
    print(json.dumps({"cell": a.cell, "devices": len(nl.devices), "cost": r["cost"], "check": r["check"], "qor": r["qor"],
                      "moves": [m for m, _ in r["log"]]}, indent=1))

def cmd_bench(a):
    cs = cells(); rows = []; passes = 0
    for name, nl in cs.items():
        g = cost(nl, greedy(nl))[0]; s = cost(nl, anneal(nl, iters=2000))[0]
        ok = check(nl, legalize(nl, anneal(nl, iters=500)))["pass"]; passes += ok
        rows.append((name, len(nl.devices), round(g, 1), round(s, 1), ok))
    print(f"{'cell':12} {'n':>3} {'greedy':>8} {'sa':>8}  pass")
    for r in rows: print(f"{r[0]:12} {r[1]:>3} {r[2]:>8} {r[3]:>8}  {r[4]}")
    _, r2 = sg.train_and_score(list(cs.values()))
    print(f"DRC/LVS pass: {passes}/{len(cs)}  surrogate R2 cap={r2[0]:.3f} delay={r2[1]:.3f}")
    nl = cs.get("ota5t") or next(iter(cs.values()))
    base = sizing.objective(nl, [d.w for d in nl.devices]); target = base * 0.8
    print("sizing (target delay<=%.2f): BO %s | random %s" % (target,
          sizing.run(nl, target, "bo", seed=1), sizing.run(nl, target, "random", seed=1)))

def main():
    p = argparse.ArgumentParser(prog="layout-qor"); s = p.add_subparsers(dest="cmd", required=True)
    r = s.add_parser("run"); r.add_argument("--cell", default="ota5t"); r.set_defaults(f=cmd_run)
    b = s.add_parser("bench"); b.set_defaults(f=cmd_bench)
    a = p.parse_args(); a.f(a)
if __name__ == "__main__": main()
