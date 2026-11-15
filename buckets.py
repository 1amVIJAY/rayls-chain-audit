import json, urllib.request, datetime
R = "https://mainnet-rpc.rayls.com"
V = ["0x0808","0xba74","0xc2af","0x17a9","0x90ae","0xfc18","0xbbd0","0xeecf"]
def batch(nums):
    req = [{"jsonrpc":"2.0","id":n,"method":"eth_getBlockByNumber","params":[hex(n),False]} for n in nums]
    r = urllib.request.Request(R, data=json.dumps(req).encode(), headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
    out = json.load(urllib.request.urlopen(r, timeout=60))
    return {o["id"]: (int(o["result"]["timestamp"],16), o["result"]["miner"].lower()) for o in out}
def buckets(a, b, size):
    d = {}
    for s in range(a, b+1, 100):
        d.update(batch(list(range(s, min(s+100, b+1)))))
    print("blocks", a, "to", b, "bucket", size, "| columns:", " ".join(x[2:] for x in V))
    for s in range(a, b, size):
        e = min(s+size-1, b)
        cnt = [0]*len(V)
        for n in range(s, e+1):
            m = d[n][1]
            for i, v in enumerate(V):
                if m.startswith(v): cnt[i] += 1
        t0 = datetime.datetime.fromtimestamp(d[s][0], datetime.timezone.utc).strftime("%m-%d %H:%M:%S")
        print(s, t0, "secs", d[e][0]-d[s][0], " ".join("%4d" % c for c in cnt))
for a, b, size in [(13270000,13290000,1000),(13277000,13279000,100),(3360000,3380000,1000),(3366500,3368500,100)]:
    buckets(a, b, size); print("---")
