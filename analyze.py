import os, datetime
def fmt(x): return datetime.datetime.fromtimestamp(x, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
rows = []
for l in open(os.path.expanduser("~/chain_samples.csv")):
    p = l.strip().split(",")
    if len(p) == 4: rows.append((int(p[0]), int(p[1]), int(p[2]), p[3]))
print("samples", len(rows), "last block", rows[-1][0], fmt(rows[-1][1]))
for i in range(1, len(rows)):
    b0, t0, n0, _ = rows[i-1]; b1, t1, n1, _ = rows[i]
    dt = t1 - t0
    e0, r0, e1, r1 = n0 >> 32, n0 & 0xffffffff, n1 >> 32, n1 & 0xffffffff
    if dt < 30 or dt > 400 or (e0 == e1 and r1 < r0):
        print("ANOMALY", b0, "->", b1, fmt(t0), "->", fmt(t1), "dt", dt, "round", r0, "->", r1, "epoch", e0, e1)
