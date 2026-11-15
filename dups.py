import json, time, urllib.request, datetime
from collections import defaultdict, Counter
R = "https://mainnet-rpc.rayls.com"
def fmt(x): return datetime.datetime.fromtimestamp(x, datetime.timezone.utc).strftime("%m-%d %H:%M:%S")
def post(req):
    h = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    for i in range(8):
        try:
            r = urllib.request.Request(R, data=json.dumps(req).encode(), headers=h)
            res = json.load(urllib.request.urlopen(r, timeout=60))
            if isinstance(res, list): return res
        except Exception as e:
            pass
        time.sleep(2 * (i + 1))
    raise SystemExit("RPC kept failing")
def batch(nums):
    req = [{"jsonrpc":"2.0","id":n,"method":"eth_getBlockByNumber","params":[hex(n),False]} for n in nums]
    out = post(req)
    return {o["id"]: (int(o["result"]["timestamp"],16), o["result"]["miner"].lower()[:8], int(o["result"]["nonce"],16), o["result"]["mixHash"], o["result"]["transactions"]) for o in out}
def scan(a, b):
    d = {}
    for s in range(a, b+1, 50):
        d.update(batch(list(range(s, min(s+50, b+1)))))
    reg = 0
    for n in range(a+1, b+1):
        e0, r0 = d[n-1][2] >> 32, d[n-1][2] & 0xffffffff
        e1, r1 = d[n][2] >> 32, d[n][2] & 0xffffffff
        if e0 == e1 and r1 < r0:
            reg += 1
            print("round regression", n-1, n, r0, "->", r1, "delta", r1-r0, "ts", fmt(d[n-1][0]), "->", fmt(d[n][0]))
    print("round regressions:", reg)
    g = defaultdict(list)
    for n in range(a, b+1): g[(d[n][2], d[n][3])].append(n)
    dups = sorted(v for v in g.values() if len(v) > 1)
    print("repeated (nonce, mixHash) groups:", len(dups))
    print("gap between copies, most common:", Counter(v[1]-v[0] for v in dups).most_common(5))
    for v in dups[:3] + dups[-3:]:
        print("  ", v, d[v[0]][1], d[v[1]][1], fmt(d[v[0]][0]), fmt(d[v[1]][0]), "tx", len(d[v[0]][4]), len(d[v[1]][4]))
    ne = [v for v in dups if d[v[0]][4] or d[v[1]][4]]
    print("repeated groups holding transactions:", len(ne))
    for v in ne[:10]: print("  ", v, "same txs" if d[v[0]][4] == d[v[1]][4] else "different txs", len(d[v[0]][4]), len(d[v[1]][4]))
for a, b in [(3360000,3370000),(13270000,13280000)]:
    scan(a, b); print("---")
