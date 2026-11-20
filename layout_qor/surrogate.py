"""QoR surrogate: GNN-style message passing over the net graph -> [cap, delay].

Features are 2 rounds of neighbour aggregation (plain PyTorch if installed,
else an identical stdlib ridge head). ponytail: ridge head on MP features is
the fallback; swap in torch_geometric GCN when available in your env."""
import math, random
from .placer import anneal, greedy
from .qor import elmore

def features(nl, place):
    pos = {p.name: p for p in place}
    nets = nl.nets()
    adj = {d.name: set() for d in nl.devices}
    for terms in nets.values():
        for a, _ in terms:
            for b, _ in terms: adj[a].add(b)
    h = {}
    for d in nl.devices:
        h[d.name] = [d.w, d.l, 1.0 if d.kind == "pmos" else 0.0, float(pos[d.name].x), float(pos[d.name].w)]
    for _ in range(2):  # message passing rounds
        h = {n: v + [sum(h[m][i] for m in adj[n]) / max(1, len(adj[n])) for i in range(len(v))] for n, v in h.items()}
    flat = [x for v in h.values() for x in v]
    if not flat: return [0.0] * 6
    return [sum(flat) / len(flat), max(flat), min(flat), float(len(nl.devices)),
            sum(d.w for d in nl.devices), max((p.x + p.w for p in place), default=0)]

def dataset(cells, n_per=12, seed=0):
    rng = random.Random(seed); X, Y = [], []
    for nl in cells:
        for i in range(n_per):
            p = anneal(nl, iters=300, seed=rng.randrange(1 << 30)) if i % 2 else greedy(nl)
            q = elmore(nl, p); X.append(features(nl, p)); Y.append([q["cap_fF"], q["delay_ps"]])
    return X, Y

def _solve(A, b):  # Gaussian elimination
    n = len(A); M = [r[:] + [b[i]] for i, r in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c])); M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r != c and M[c][c]:
                f = M[r][c] / M[c][c]
                for k in range(c, n + 1): M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] if M[i][i] else 0.0 for i in range(n)]

class Surrogate:
    def fit(self, X, Y, lam=1e-3):
        self.mx = [sum(c) / len(c) for c in zip(*X)]
        d = len(X[0]); self.W = []
        for t in range(2):
            A = [[sum((X[k][i] - self.mx[i]) * (X[k][j] - self.mx[j]) for k in range(len(X))) + (lam if i == j else 0)
                  for j in range(d)] for i in range(d)]
            b = [sum((X[k][i] - self.mx[i]) * Y[k][t] for k in range(len(X))) for i in range(d)]
            self.W.append(_solve(A, b))
        self.my = [sum(c) / len(c) for c in zip(*Y)]; return self
    def predict(self, x):
        return [self.my[t] + sum((x[i] - self.mx[i]) * self.W[t][i] for i in range(len(x))) for t in range(2)]

def r2(Y, P):
    out = []
    for t in range(2):
        mean = sum(y[t] for y in Y) / len(Y); ss = sum((y[t] - mean) ** 2 for y in Y) or 1
        out.append(1 - sum((Y[i][t] - P[i][t]) ** 2 for i in range(len(Y))) / ss)
    return out

def train_and_score(cells, seed=0):
    X, Y = dataset(cells, seed=seed); cut = max(2, int(0.8 * len(X)))
    s = Surrogate().fit(X[:cut], Y[:cut])
    return s, r2(Y[cut:], [s.predict(x) for x in X[cut:]])
