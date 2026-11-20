import json, subprocess, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from layout_qor import cells
from layout_qor.netlist import parse
from layout_qor.placer import greedy, anneal, cost, placer_cli
from layout_qor.legalizer import legalize
from layout_qor.checker import check
from layout_qor.agent import RulePlanner
from layout_qor import surrogate as sg, sizing
from layout_qor.mcp_server import handle

def test_parse():
    nl = parse(open("examples/inv.sp").read()) if os.path.exists("examples/inv.sp") else cells()["inv"]
    assert nl.name == "inv" and len(nl.devices) == 2 and nl.devices[0].kind == "pmos"

def test_all_cells_place_and_check():
    for nl in cells().values():
        p = legalize(nl, anneal(nl, iters=500))
        assert check(nl, p)["pass"], nl.name
        assert cost(nl, anneal(nl, iters=2000))[0] <= cost(nl, greedy(nl))[0] + 5

def test_surrogate_and_sizing():
    cs = list(cells().values())
    _, r2 = sg.train_and_score(cs[:4])
    assert len(r2) == 2
    nl = cs[0]; base = sizing.objective(nl, [d.w for d in nl.devices])
    assert sizing.run(nl, base * 0.5, "random", max_calls=5)["calls"] <= 5

def test_agent_and_mcp():
    assert RulePlanner().run(cells()["inv"])["check"]["pass"]
    out = handle({"method": "tools/call", "id": 1, "params": {"name": "check", "arguments": {"cell": "inv"}}})
    assert "pass" in json.dumps(out)

def test_cpp_placer_if_built():
    b = "cpp/build/placer"
    if not os.path.exists(b): return
    p = placer_cli(cells()["inv"], b)
    assert p and len(p) == 2
