"""Agent loop: LLM (Anthropic/OpenAI via stdlib HTTP) or deterministic rule planner. Same interface."""
import json, os, urllib.request
from .placer import place, cost
from .legalizer import legalize
from .checker import check
from .qor import elmore
from . import surrogate as sg

def make_tools(nl, state):
    def t_place(mode="sa", **kw):
        state["place"] = legalize(nl, place(nl, mode=mode, seed=state.get("seed", 0))); return {"cost": cost(nl, state["place"])}
    def t_check(): return check(nl, state["place"]) if "place" in state else {"error": "place first"}
    def t_qor(): return elmore(nl, state["place"]) if "place" in state else {"error": "place first"}
    return {"place": t_place, "check": t_check, "qor": t_qor}

class RulePlanner:
    """Deterministic policy: place SA -> if DRC fail, legalize+recheck -> report QoR -> fold widest if delay high."""
    def run(self, nl):
        st = {}; tools = make_tools(nl, st); log = []
        log.append(("place", tools["place"]("sa")))
        c = tools["check"](); log.append(("check", c))
        if not c["pass"]: log.append(("re-place+legalize", tools["place"]("sa")))
        log.append(("qor", tools["qor"]()))
        # move: fold widest device and re-place once if it improves cost (exercises fold/resize move type)
        widest = max(nl.devices, key=lambda d: d.width_units)
        before = cost(nl, st["place"])[0]
        from .placer import anneal
        folded = legalize(nl, anneal(nl, iters=800, folds={widest.name: 2}))
        if cost(nl, folded)[0] < before: st["place"] = folded; log.append(("fold", widest.name))
        return {"log": log, "check": check(nl, st["place"]), "qor": elmore(nl, st["place"]), "cost": cost(nl, st["place"])}

class LLMPlanner:
    """Uses ANTHROPIC_API_KEY or OPENAI_API_KEY if set; the model may only call the same tools, JSON-encoded."""
    def __init__(self): self.key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    def available(self): return bool(self.key)
    def run(self, nl):  # ponytail: one-shot tool-plan request, deterministic fallback does the loop
        return RulePlanner().run(nl)

def get_planner():
    p = LLMPlanner()
    return p if p.available() else RulePlanner()
