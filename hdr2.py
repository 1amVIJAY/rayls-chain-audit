import json, sys, datetime, urllib.request
R = "https://mainnet-rpc.rayls.com"
def blk(n):
    req = {"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(n),False]}
    r = urllib.request.Request(R, data=json.dumps(req).encode(), headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r, timeout=60))["result"]
for a in sys.argv[1:]:
    n = int(a); b = blk(n)
    t = int(b["timestamp"], 16); nc = int(b["nonce"], 16)
    print(n, datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%m-%d %H:%M:%S"), b["miner"][:8], "epoch", nc >> 32, "round", nc & 0xffffffff, "mix", b["mixHash"][:12], "req", b["requestsHash"][:12], "tx", len(b["transactions"]))
