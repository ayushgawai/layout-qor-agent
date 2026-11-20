# layout-qor-agent

Agentic custom-circuit (analog + standard-cell) transistor placement & sizing:
an LLM/rule agent drives a simulated-annealing placer, a CP-SAT row legalizer,
DRC/LVS-style checks and a GNN QoR surrogate, then sizes devices with Bayesian
optimisation.

```
 netlist (.sp) ──> parser ──> device graph ──┐
                                             v
  agent (LLM if a key is set, else      placer (C++17 SA / greedy,
  deterministic rule planner)  ──tools─> Python mirror, JSON CLI)
   │  moves: fold / swap / resize /          │
   │  re-weight cost                         v
   ├──────────────────────────────> legalizer (OR-Tools CP-SAT,
   │                                  greedy left-pack fallback)
   ├──────────────────────────────> checker (simplified DRC + LVS-style,
   │                                  optional KLayout/netgen hooks)
   └──────────────────────────────> QoR surrogate (GNN message passing
                                      -> cap/delay; Elmore ground truth,
                                      ngspice when installed)
 sizing: GP Bayesian optimisation vs random search over W/L
 tools also exposed as an MCP server (stdio JSON-RPC)
```

## Design

| Module | File | Notes |
|---|---|---|
| Netlist parser | `layout_qor/netlist.py` | SPICE `.subckt`, MOSFET W/L/nf, net graph, matched pairs |
| Placer | `cpp/placer.cpp`, `layout_qor/placer.py` | SA + greedy on PMOS/NMOS rows, folding, diffusion-sharing spacing, cost = area + HPWL + symmetry; C++ via JSON stdin/stdout (pybind11 optional, CMake) |
| Legalizer | `layout_qor/legalizer.py` | OR-Tools CP-SAT NoOverlap per row; stdlib fallback if ortools absent |
| Checker | `layout_qor/checker.py` | Grid min-width/spacing/overlap DRC, device/row LVS-style check; KLayout/netgen detected, never required |
| QoR | `layout_qor/qor.py`, `surrogate.py` | Elmore RC ground truth, ngspice hook; 2-round message-passing GNN features + regression head (PyTorch/torch-geometric can replace the head) |
| Agent | `layout_qor/agent.py`, `mcp_server.py` | Anthropic/OpenAI key → LLM planner; otherwise deterministic rule planner, same tool interface. MCP: `place`/`check`/`qor` |
| Sizing | `layout_qor/sizing.py` | Small GP (RBF, stdlib) BO vs random; scikit-optimize drop-in if installed |

10 example cells in `examples/` (inv, nand2, nor2, and2, buf, xor2, dff-lite,
ota5t, mirror, diffpair) with SKY130-style model names.

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install pytest   # core is stdlib-only
.venv/bin/python -m layout_qor.cli run --cell ota5t
.venv/bin/python -m layout_qor.cli bench
.venv/bin/python -m pytest tests/ -q
# C++ (needs cmake + a C++17 compiler):
cmake -S cpp -B cpp/build && cmake --build cpp/build && (cd cpp/build && ctest)
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | .venv/bin/python -m layout_qor.mcp_server
```

Optional: `pip install ortools torch scikit-optimize` and/or set
`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` to enable the enhanced paths.

## Sanity runs (this machine, scaled down, Python 3.15, no optional deps)

`layout-qor run --cell ota5t` → DRC/LVS `pass: true`, QoR (Elmore)
`cap_fF=7.3, delay_ps=2.29`, agent moves `[place, check, qor, fold]`, cost 72.0.

`layout-qor bench`:

```
cell           n   greedy       sa  pass
and2           6     71.0     62.5  True
buf            4     44.5     44.5  True
dff            6     73.0     62.0  True
diffpair       5     80.5     80.5  True
inv            2     13.0     13.0  True
mirror         3     74.0     74.0  True
nand2          4     33.5     33.0  True
nor2           4     33.5     32.0  True
ota5t          5    104.0     95.0  True
xor2           6     55.5     51.0  True
DRC/LVS pass: 10/10  surrogate R2 cap=0.343 delay=0.912
sizing (target delay<=2.33): BO {'calls': 40, 'best': 2.682, 'reached': False} | random {'calls': 40, 'best': 2.909, 'reached': False}
```

`pytest`: 5 passed. The C++ test is included (`cpp/test_placer.cpp`, CMake
`ctest`) but was **not compiled in the environment that produced the numbers
above** — no C++ compiler/cmake was available there; the Python placer mirror
is what the tests exercised, and the C++ JSON protocol test self-skips until
`cpp/build/placer` exists.

## Limitations (honest)

- DRC is a simplified grid model (min width/spacing/overlap only) — not signoff DRC.
- Parasitics are Elmore-style estimates from HPWL, not extraction; ngspice hook only reports that a run happened unless a deck supplies `.meas`.
- Surrogate is a small message-passing model trained on synthetic layouts from these 10 cells; cap R² above is modest. Not signoff QoR.
- Sizing BO did not reach the (arbitrary −20%) delay target in 40 calls above; it did beat random search's best. Results are seed-dependent toys.
- Placement is two device rows with unit spacing — no routing, no real diffusion-sharing geometry, matched-pair symmetry is a cost term, not a constraint.
- The LLM planner currently delegates the loop to the rule planner after a one-shot plan; the tool interface is identical so a full tool-calling loop can be dropped in.
- This is a research/teaching prototype, **not a signoff flow**.

MIT — see `LICENSE`.
