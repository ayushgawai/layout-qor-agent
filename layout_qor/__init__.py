import glob, os
from .netlist import load
EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")
def cells():
    return {os.path.splitext(os.path.basename(p))[0]: load(p) for p in sorted(glob.glob(os.path.join(EXAMPLES, "*.sp")))}
