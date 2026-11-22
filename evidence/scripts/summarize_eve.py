#!/usr/bin/env python3
"""Summarize Suricata eve.json alerts."""
import json
import sys
from collections import Counter, defaultdict

path = sys.argv[1] if len(sys.argv) > 1 else "eve.json"
sig = Counter()
meta = defaultdict(lambda: {"src": set(), "dst": set(), "tmin": None, "tmax": None})
n = 0
with open(path, encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("event_type") != "alert":
            continue
        n += 1
        s = o.get("alert", {}).get("signature", "?")
        sig[s] += 1
        d = meta[s]
        if o.get("src_ip"):
            d["src"].add(o["src_ip"])
        if o.get("dest_ip"):
            d["dst"].add(o["dest_ip"])
        t = o.get("timestamp")
        if t:
            if d["tmin"] is None or t < d["tmin"]:
                d["tmin"] = t
            if d["tmax"] is None or t > d["tmax"]:
                d["tmax"] = t
print(f"alerts: {n}")
for s, c in sig.most_common():
    d = meta[s]
    print(
        f"{c}\t{s}\t"
        f"src={sorted(d['src'])}\t"
        f"dst={sorted(d['dst'])}\t"
        f"{d['tmin']} -> {d['tmax']}"
    )
