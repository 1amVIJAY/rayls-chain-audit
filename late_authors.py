import json, os, time, urllib.request, datetime
from collections import Counter
R = "https://mainnet-rpc.rayls.com"
H = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
def post(req):
    for i in range(8):
        try:
            r = urllib.request.Request(R, data=json.dumps(req).encode(), headers=H)
            res = json.load(urllib.request.urlopen(r, timeout=60))
            if isinstance(res, list): return res
        except Exception:
            pass
        time.sleep(2 * (i + 1))
    raise SystemExit("RPC kept failing")
def fetch(a, b):
    d = {}
    for s in range(a, b + 1, 50):
        req = [{"jsonrpc":"2.0","id":n,"method":"eth_getBlockByNumber","params":[hex(n),False]} for n in range(s, min(s + 50, b + 1))]
        for o in post(req):
            x = o["result"]
            d[o["id"]] = (int(x["timestamp"], 16), x["miner"][:8], len(x["transactions"]))
    return d
rows = {}
for l in open(os.path.expanduser("~/epoch_audit.csv")):
    p = l.strip().split(",")
    if len(p) == 7: rows[int(p[0])] = p
print("distinct epochs audited:", len(rows))
flag = [rows[e] for e in sorted(rows) if int(rows[e][3]) > 0]
print("epochs with late blocks at the end:", len(flag), "before block 12231705:", sum(1 for r in flag if int(r[1]) < 12231705))
total = Counter()
for r in flag:
    e, bound = int(r[0]), int(r[1])
    d = fetch(bound - 400, bound - 1)
    runmax = 0; c = Counter(); mx = 0
    for n in sorted(d):
        ts, m, tx = d[n]
        if ts < runmax - 30:
            c[m] += 1; mx = max(mx, runmax - ts)
        runmax = max(runmax, ts)
    total.update(c)
    print("epoch", e, "boundary", bound, r[2], "late", sum(c.values()), "max late s", mx, dict(c))
print("late blocks by author over all flagged epochs:", dict(total))
