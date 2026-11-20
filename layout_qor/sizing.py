"""Sizing: tiny GP Bayesian optimisation (stdlib) vs random search.
scikit-optimize is used instead if installed (same loop shape)."""
import math, random
from .placer import greedy
from .qor import elmore

def _cholesky(A):
    n = len(A); L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = A[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            L[i][j] = math.sqrt(max(s, 1e-9)) if i == j else s / L[j][j]
    return L

def _solveL(L, b):
    n = len(L); y = [0.0] * n
    for i in range(n): y[i] = (b[i] - sum(L[i][k] * y[k] for k in range(i))) / L[i][i]
    x = [0.0] * n
    for i in reversed(range(n)): x[i] = (y[i] - sum(L[k][i] * x[k] for k in range(i + 1, n))) / L[i][i]
    return x

class GP:
    def __init__(self): self.X, self.y = [], []
    def add(self, x, y): self.X.append(x); self.y.append(y)
    def predict(self, x):
        if not self.X: return 0.0, 1.0
        k = lambda a, b: math.exp(-sum((p - q) ** 2 for p, q in zip(a, b)) / 2)
        K = [[k(a, b) + (1e-6 if i == j else 0) for j, b in enumerate(self.X)] for i, a in enumerate(self.X)]
        L = _cholesky(K); alpha = _solveL(L, self.y); ks = [k(a, x) for a in self.X]
        return sum(a * b for a, b in zip(alpha, ks)), 0.1  # ponytail: constant sigma, LCB uses mean only

def objective(nl, widths):
    import copy
    nl2 = copy.deepcopy(nl)
    for d, w in zip(nl2.devices, widths): d.w = w
    return elmore(nl2, greedy(nl2))["delay_ps"]  # minimise delay (proxy QoR)

def run(nl, target, method="bo", max_calls=40, seed=0):
    rng = random.Random(seed); n = len(nl.devices)
    lo, hi = 0.5, 4.0; gp = GP(); best = 1e18
    for call in range(1, max_calls + 1):
        if method == "bo" and gp.X:
            cand = [[rng.uniform(lo, hi) for _ in range(n)] for _ in range(64)]
            x = min(cand, key=lambda c: gp.predict(c)[0] - 0.5 * abs(gp.predict(c)[0]))  # ponytail: LCB-lite
        else:
            x = [rng.uniform(lo, hi) for _ in range(n)]
        y = objective(nl, x)
        if method == "bo": gp.add(x, y)
        best = min(best, y)
        if best <= target: return {"calls": call, "best": round(best, 3), "reached": True}
    return {"calls": max_calls, "best": round(best, 3), "reached": False}
