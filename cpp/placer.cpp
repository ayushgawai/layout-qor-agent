#include <bits/stdc++.h>
using namespace std;
// JSON-in/out SA + greedy transistor placer (rows: 1=PMOS, 0=NMOS).
// ponytail: hand-rolled scan of the flat schema emitted by placer.py only, not general JSON.
struct Dev { string name, kind; int w = 1; vector<string> nets; };
static vector<string> strings_in(const string& s) {
  vector<string> out;
  for (size_t q = s.find('"'); q != string::npos; q = s.find('"', q + 1)) {
    auto e = s.find('"', q + 1); out.push_back(s.substr(q + 1, e - q - 1)); q = e;
  }
  return out;
}
int main() {
  string in((istreambuf_iterator<char>(cin)), istreambuf_iterator<char>());
  string mode = in.find("\"sa\"") != string::npos ? "sa" : "greedy";
  int seed = 0;
  if (auto p = in.find("\"seed\""); p != string::npos) seed = stoi(in.substr(in.find(':', p) + 1));
  vector<Dev> devs;
  for (size_t p = in.find("\"devices\""); (p = in.find("{\"name\"", p)) != string::npos;) {
    auto e = in.find('}', p); string obj = in.substr(p, e - p); auto strs = strings_in(obj);
    Dev d; d.name = strs[1]; d.kind = strs[3];  // "name",v,"kind",v,"w",..,"nets",d,g,s
    d.w = stoi(obj.substr(obj.find("\"w\"") + 4));
    for (size_t i = 6; i < strs.size(); i++) d.nets.push_back(strs[i]);
    devs.push_back(d); p = e;
  }
  mt19937 rng(seed);
  auto build = [&](vector<int> ord) {
    vector<array<int, 3>> pos(devs.size()); int cur[2] = {0, 0};
    for (int i : ord) { int r = devs[i].kind == "pmos" ? 1 : 0; pos[i] = {cur[r], r, devs[i].w}; cur[r] += devs[i].w + 1; }
    return pos;
  };
  auto cost = [&](vector<array<int, 3>>& pos) {
    map<string, vector<pair<double, double>>> by;
    for (size_t i = 0; i < devs.size(); i++) for (auto& n : devs[i].nets) by[n].push_back({pos[i][0] + pos[i][2] / 2.0, pos[i][1]});
    double hp = 0; int width = 0;
    for (auto& kv : by) if (kv.second.size() > 1) { double x0=1e9,x1=-1e9,y0=1e9,y1=-1e9; for (auto& p : kv.second){x0=min(x0,p.first);x1=max(x1,p.first);y0=min(y0,p.second);y1=max(y1,p.second);} hp += (x1-x0)+(y1-y0); }
    for (auto& p : pos) width = max(width, p[0] + p[2]);
    return width * 2.0 + hp;
  };
  vector<int> ord(devs.size()); iota(ord.begin(), ord.end(), 0);
  auto bestpos = build(ord); double cur = cost(bestpos), best = cur;
  if (mode == "sa" && devs.size() > 1)
    for (int it = 0; it < 4000; it++) {
      double T = max(0.01, 2.0 * (1.0 - it / 4000.0));
      int a = rng() % devs.size(), b = rng() % devs.size(); swap(ord[a], ord[b]);
      auto p2 = build(ord); double c = cost(p2);
      if (c <= cur || exp(-(c - cur) / T) > uniform_real_distribution<>(0, 1)(rng)) { cur = c; if (c < best) { best = c; bestpos = p2; } }
      else swap(ord[a], ord[b]);
    }
  cout << "{\"placement\":[";
  for (size_t i = 0; i < devs.size(); i++) { if (i) cout << ","; cout << "{\"name\":\"" << devs[i].name << "\",\"x\":" << bestpos[i][0] << ",\"row\":" << bestpos[i][1] << ",\"w\":" << bestpos[i][2] << "}"; }
  cout << "],\"cost\":" << best << "}\n";
}
