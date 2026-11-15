import json, os, time, datetime, urllib.request
R = "https://mainnet-rpc.rayls.com"
H = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
CSV = os.path.expanduser("~/chain_samples.csv")
OUT = os.path.expanduser("~/epoch_audit.csv")
def fmt(x): return datetime.datetime.fromtimestamp(x, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
def post(req):
    for i in range(8):
        try:
            r = urllib.request.Request(R, data=json.dumps(req).encode(), headers=H)
            res = json.load(urllib.request.urlopen(r, timeout=60))
            if isinstance(res, list): return res
        except Exception:
            pass
        time.sleep(2 * (i + 1))
    raise SystemExit("RPC kept failing, rerun to resume")
def fetch(a, b):
    d = {}
    for s in range(a, b + 1, 50):
        req = [{"jsonrpc":"2.0","id":n,"method":"eth_getBlockByNumber","params":[hex(n),False]} for n in range(s, min(s + 50, b + 1))]
        for o in post(req):
            x = o["result"]; nc = int(x["nonce"], 16)
            d[o["id"]] = (int(x["timestamp"], 16), nc >> 32, len(x["transactions"]))
    return d
rows = []
for l in open(CSV):
    p = l.strip().split(",")
    if len(p) == 4: rows.append((int(p[0]), int(p[2]) >> 32))
done = set()
if os.path.exists(OUT):
    for l in open(OUT): done.add(int(l.split(",")[0]))
changes = [(rows[i-1][0], rows[i][0], rows[i][1]) for i in range(1, len(rows)) if rows[i][1] != rows[i-1][1]]
print("epoch changes in csv:", len(changes), "already audited:", len(done))
with open(OUT, "a") as f:
    for b0, b1, e1 in changes:
        if e1 in done: continue
        d = fetch(max(b0 - 400, 0), b1 + 20)
        nums = sorted(d)
        bound = next((n for n in nums if d[n][1] == e1), None)
        if bound is None: continue
        runmax = 0; before = 0; after = 0; maxlate = 0; ltx = 0
        for n in nums:
            ts, ep, tx = d[n]
            if ts < runmax - 30:
                if n < bound: before += 1
                else: after += 1
                maxlate = max(maxlate, runmax - ts); ltx += tx
            runmax = max(runmax, ts)
        f.write("%d,%d,%s,%d,%d,%d,%d\n" % (e1, bound, fmt(d[bound][0]), before, maxlate, ltx, after))
        f.flush()
        if before or after: print("epoch", e1, "boundary block", bound, fmt(d[bound][0]), "late blocks before", before, "after", after, "max late s", maxlate, "tx in late blocks", ltx)
rows2 = [l.strip().split(",") for l in open(OUT)]
pre = [r for r in rows2 if int(r[1]) < 12231705]
post_ = [r for r in rows2 if int(r[1]) >= 12231705]
print("epochs audited before block 12231705:", len(pre), "with late blocks at the end:", sum(1 for r in pre if int(r[3]) > 0))
print("epochs audited from block 12231705:", len(post_), "with late blocks at the end:", sum(1 for r in post_ if int(r[3]) > 0))
