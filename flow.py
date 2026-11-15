import json, sys, time, datetime, urllib.request
R = "https://mainnet-rpc.rayls.com"
H = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
def fmt(x): return datetime.datetime.fromtimestamp(x, datetime.timezone.utc).strftime("%m-%d %H:%M:%S")
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
a, b = int(sys.argv[1]), int(sys.argv[2])
d = {}
for s in range(a, b + 1, 50):
    req = [{"jsonrpc":"2.0","id":n,"method":"eth_getBlockByNumber","params":[hex(n),False]} for n in range(s, min(s + 50, b + 1))]
    for o in post(req):
        x = o["result"]; nc = int(x["nonce"], 16)
        d[o["id"]] = (int(x["timestamp"], 16), nc >> 32, nc & 0xffffffff, x["miner"][:8], len(x["transactions"]), x["requestsHash"][:10])
for n in range(a + 1, b + 1):
    t0, e0, r0, _, _, _ = d[n-1]; t1, e1, r1, m, tx, rq = d[n]
    if t1 < t0 or t1 - t0 >= 10 or (e0 == e1 and r1 < r0) or e1 != e0 or tx > 0:
        print(n, fmt(t1), "dt", t1 - t0, "epoch", e1, "round", r1, m, "tx", tx, "req", rq)
print("scanned", a, b)
