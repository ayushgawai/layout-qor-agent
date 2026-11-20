"""QoR ground truth: Elmore-style RC estimate; ngspice transient when installed."""
import math, shutil, subprocess, tempfile, os
C_PER_UNIT = 0.2   # fF per grid unit of HPWL (simplified, calibration knob)
R_PER_W = 1.0      # delay scales inversely with total width

def elmore(nl, place):
    from .placer import cost
    _, parts = cost(nl, place)
    cap = C_PER_UNIT * parts["hpwl"] + 0.5 * len(nl.devices)  # fF
    width = sum(d.w * d.nf for d in nl.devices) or 1
    delay = 0.69 * (R_PER_W / width) * cap * 10  # ps, toy Elmore RC
    return {"cap_fF": round(cap, 3), "delay_ps": round(delay, 3), "source": "elmore"}

def ngspice_delay(spice_text):
    """Returns None when ngspice is absent (callers fall back to Elmore)."""
    if not shutil.which("ngspice"): return None
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "c.sp"); open(p, "w").write(spice_text)
        r = subprocess.run(["ngspice", "-b", p], capture_output=True, text=True, timeout=60)
        return {"source": "ngspice", "ran": r.returncode == 0}  # ponytail: parse .meas when a deck supplies it
