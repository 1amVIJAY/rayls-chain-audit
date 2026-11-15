import json, urllib.request, datetime
R = "https://mainnet-rpc.rayls.com"
def fmt(x): return datetime.datetime.fromtimestamp(x, datetime.timezone.utc).strftime("%m-%d %H:%M:%S")
def batch(nums):
    req = [{"jsonrpc":"2.0","id":n,"method":"eth_getBlockByNumber","params":[hex(n),False]} for n in nums]
    r = urllib.request.Request(R, data=json.dumps(req).encode(), headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
    out = json.load(urllib.request.urlopen(r, timeout=60))
    return {o["id"]: int(o["result"]["timestamp"],16) for o in out}
def scan(a, b, thr=20):
    ts = {}
    for s in range(a, b+1, 100):
        ts.update(batch(list(range(s, min(s+100, b+1)))))
    big = 0; cnt = 0
    for n in range(a+1, b+1):
        g = ts[n]-ts[n-1]
        if g >= thr:
            big += g; cnt += 1
            print(n-1, n, fmt(ts[n-1]), fmt(ts[n]), "gap", g)
    print("window", a, b, "total seconds", ts[b]-ts[a], "| gaps >= 20 s:", cnt, "summing", big)
for a, b in [(3360000,3370000),(13270000,13280000),(3390000,3410000)]:
    scan(a, b); print("---")
