import json, urllib.request
from collections import Counter
R = "https://mainnet-rpc.rayls.com"
def batch(nums):
    req = [{"jsonrpc":"2.0","id":n,"method":"eth_getBlockByNumber","params":[hex(n),False]} for n in nums]
    r = urllib.request.Request(R, data=json.dumps(req).encode(), headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
    out = json.load(urllib.request.urlopen(r, timeout=60))
    return {o["id"]: o["result"]["miner"].lower() for o in out}
def count(label, a, b):
    m = {}
    for s in range(a, b+1, 100):
        m.update(batch(list(range(s, min(s+100, b+1)))))
    c = Counter(m.values())
    print(label, a, b, len(m), "blocks,", len(c), "distinct miners")
    for k, v in c.most_common(): print("  ", k, v)
for label, a, b in [
    ("jun-before", 3366800, 3367007), ("jun-after", 3367008, 3367215),
    ("oct-before", 13277640, 13277905), ("oct-during", 13277906, 13278170), ("oct-after", 13278171, 13278435)]:
    count(label, a, b)
