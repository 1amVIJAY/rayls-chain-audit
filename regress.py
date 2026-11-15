import json, urllib.request, datetime
R = "https://mainnet-rpc.rayls.com"
def fmt(x): return datetime.datetime.fromtimestamp(x, datetime.timezone.utc).strftime("%m-%d %H:%M:%S")
def batch(nums):
    req = [{"jsonrpc":"2.0","id":n,"method":"eth_getBlockByNumber","params":[hex(n),False]} for n in nums]
    r = urllib.request.Request(R, data=json.dumps(req).encode(), headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
    out = json.load(urllib.request.urlopen(r, timeout=60))
    return {o["id"]: (int(o["result"]["timestamp"],16), o["result"]["miner"].lower()[:8]) for o in out}
def scan(a, b):
    d = {}
    for s in range(a, b+1, 100):
        d.update(batch(list(range(s, min(s+100, b+1)))))
    cnt = 0
    for n in range(a+1, b+1):
        delta = d[n][0] - d[n-1][0]
        if delta <= 0:
            cnt += 1
            print("block", n-1, fmt(d[n-1][0]), d[n-1][1], "->", n, fmt(d[n][0]), d[n][1], "delta", delta)
    print("window", a, b, "non-forward steps:", cnt)
for a, b in [(3360000,3370000),(13270000,13280000)]:
    scan(a, b); print("---")
