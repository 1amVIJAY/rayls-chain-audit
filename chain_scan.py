import json, os, time, urllib.request, datetime
R = "https://mainnet-rpc.rayls.com"
F = os.path.expanduser("~/chain_samples.csv")
H = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
def post(req):
    for i in range(8):
        try:
            r = urllib.request.Request(R, data=json.dumps(req).encode(), headers=H)
            res = json.load(urllib.request.urlopen(r, timeout=60))
            if isinstance(res, list) or "result" in res: return res
        except Exception:
            pass
        time.sleep(2 * (i + 1))
    raise SystemExit("RPC kept failing, rerun to resume")
def fmt(x): return datetime.datetime.fromtimestamp(x, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
head = int(post({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})["result"], 16)
last = -100
if os.path.exists(F):
    for line in open(F): last = int(line.split(",")[0])
nums = list(range(last + 100, head + 1, 100))
print("head", head, "samples to fetch", len(nums))
with open(F, "a") as f:
    for s in range(0, len(nums), 100):
        chunk = nums[s:s+100]
        req = [{"jsonrpc":"2.0","id":n,"method":"eth_getBlockByNumber","params":[hex(n),False]} for n in chunk]
        out = {o["id"]: o["result"] for o in post(req)}
        for n in chunk:
            b = out[n]
            f.write("%d,%d,%d,%s\n" % (n, int(b["timestamp"],16), int(b["nonce"],16), b["miner"][:8]))
        f.flush()
        if (s // 100) % 10 == 0: print("done up to block", chunk[-1])
rows = [l.strip().split(",") for l in open(F)]
rows = [(int(a), int(b), int(c), d) for a, b, c, d in rows]
print("samples", len(rows))
for i in range(1, len(rows)):
    b0, t0, n0, _ = rows[i-1]; b1, t1, n1, m1 = rows[i]
    dt = t1 - t0
    e0, r0, e1, r1 = n0 >> 32, n0 & 0xffffffff, n1 >> 32, n1 & 0xffffffff
    if dt < 30 or dt > 400 or (e0 == e1 and r1 < r0):
        print("ANOMALY", b0, "->", b1, fmt(t0), "->", fmt(t1), "dt", dt, "round", r0, "->", r1, "epoch", e0, e1)
