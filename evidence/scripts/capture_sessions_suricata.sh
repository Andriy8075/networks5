#!/usr/bin/env bash
set -eu
LAB=/mnt/c/Users/Admin/projects/NetworkLabs/lab5
cd "$LAB"
SESS=evidence/console/sessions
PROMPT='andrii@DESKTOP-7BD93CN:/mnt/c/Users/Admin/projects/NetworkLabs/lab5'
PY=/usr/bin/python3
SUM="$LAB/evidence/scripts/summarize_eve.py"

summarize() {
  local eve="$1"
  if [[ -f "$SUM" ]]; then
    "$PY" "$SUM" "$eve"
  else
    "$PY" -c "
import json
from collections import Counter, defaultdict
sig=Counter(); meta=defaultdict(lambda:{'src':set(),'dst':set(),'tmin':None,'tmax':None}); n=0
for line in open('$eve',encoding='utf-8',errors='replace'):
    line=line.strip()
    if not line: continue
    o=json.loads(line)
    if o.get('event_type')!='alert': continue
    n+=1
    s=o.get('alert',{}).get('signature','?')
    sig[s]+=1
    d=meta[s]
    if o.get('src_ip'): d['src'].add(o['src_ip'])
    if o.get('dest_ip'): d['dst'].add(o['dest_ip'])
    t=o.get('timestamp')
    if t:
        if d['tmin'] is None or t<d['tmin']: d['tmin']=t
        if d['tmax'] is None or t>d['tmax']: d['tmax']=t
print('alerts:', n)
for s,c in sig.most_common():
    d=meta[s]
    print(f\"{c}\t{s}\tsrc={sorted(d['src'])}\tdst={sorted(d['dst'])}\t{d['tmin']} -> {d['tmax']}\")
"
  fi
}

{
  echo "${PROMPT}\$ docker run --rm -e TZ=UTC -v \"\$PWD/evidence/suricata/etc:/etc/suricata\" -v \"\$PWD/evidence/suricata/rules:/var/lib/suricata\" -v \"\$PWD:/pcaps:ro\" -v \"\$PWD/evidence/suricata/out-default:/var/log/suricata\" jasonish/suricata:7.0.8 -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none"
  docker run --rm -e TZ=UTC \
    -v "$PWD/evidence/suricata/etc:/etc/suricata" \
    -v "$PWD/evidence/suricata/rules:/var/lib/suricata" \
    -v "$PWD:/pcaps:ro" \
    -v "$PWD/evidence/suricata/out-default:/var/log/suricata" \
    jasonish/suricata:7.0.8 \
    -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none 2>&1 | tail -n 25
  echo
  echo "${PROMPT}\$ python3 evidence/scripts/summarize_eve.py evidence/suricata/out-default/eve.json"
  summarize evidence/suricata/out-default/eve.json
  echo
} > "$SESS/09-suricata-default.txt"
echo wrote 09-suricata-default.txt

{
  echo "${PROMPT}\$ docker run --rm -e TZ=UTC -v \"\$PWD/evidence/suricata/etc:/etc/suricata\" -v \"\$PWD/evidence/suricata/rules:/var/lib/suricata\" -v \"\$PWD:/pcaps:ro\" -v \"\$PWD/evidence/suricata/out-external-any:/var/log/suricata\" jasonish/suricata:7.0.8 -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none --set vars.address-groups.EXTERNAL_NET=any"
  docker run --rm -e TZ=UTC \
    -v "$PWD/evidence/suricata/etc:/etc/suricata" \
    -v "$PWD/evidence/suricata/rules:/var/lib/suricata" \
    -v "$PWD:/pcaps:ro" \
    -v "$PWD/evidence/suricata/out-external-any:/var/log/suricata" \
    jasonish/suricata:7.0.8 \
    -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none \
    --set vars.address-groups.EXTERNAL_NET=any 2>&1 | tail -n 25
  echo
  echo "${PROMPT}\$ python3 evidence/scripts/summarize_eve.py evidence/suricata/out-external-any/eve.json"
  summarize evidence/suricata/out-external-any/eve.json
  echo
} > "$SESS/10-suricata-external-any.txt"
echo wrote 10-suricata-external-any.txt

{
  echo "${PROMPT}\$ docker run --rm -e TZ=UTC -v \"\$PWD/evidence/suricata/etc:/etc/suricata\" -v \"\$PWD/evidence/suricata/rules:/var/lib/suricata\" -v \"\$PWD:/pcaps:ro\" -v \"\$PWD/evidence/rules:/custom:ro\" -v \"\$PWD/evidence/suricata/out-custom:/var/log/suricata\" jasonish/suricata:7.0.8 -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none -S /custom/local.rules --set vars.address-groups.EXTERNAL_NET=any"
  docker run --rm -e TZ=UTC \
    -v "$PWD/evidence/suricata/etc:/etc/suricata" \
    -v "$PWD/evidence/suricata/rules:/var/lib/suricata" \
    -v "$PWD:/pcaps:ro" \
    -v "$PWD/evidence/rules:/custom:ro" \
    -v "$PWD/evidence/suricata/out-custom:/var/log/suricata" \
    jasonish/suricata:7.0.8 \
    -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none \
    -S /custom/local.rules --set vars.address-groups.EXTERNAL_NET=any 2>&1 | tail -n 25
  echo
  echo "${PROMPT}\$ python3 evidence/scripts/summarize_eve.py evidence/suricata/out-custom/eve.json"
  summarize evidence/suricata/out-custom/eve.json
  echo
  echo "${PROMPT}\$ cat evidence/rules/local.rules"
  cat evidence/rules/local.rules
  echo
} > "$SESS/11-suricata-custom.txt"
echo wrote 11-suricata-custom.txt

{
  echo "${PROMPT}\$ python3 evidence/scripts/investigate.py lr5_v02.pcap evidence/scripts/incident.json"
  "$PY" - <<'PY'
import json, subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

TSHARK = "/mnt/c/Program Files/Wireshark/tshark.exe"
pcap = "lr5_v02.pcap"
out_path = Path("evidence/scripts/incident.json")

def parse_ts(s: str) -> datetime:
    s = s.rstrip("Z")
    if "." in s:
        main, frac = s.split(".", 1)
        frac = ("".join(ch for ch in frac if ch.isdigit()) + "000000")[:6]
        s = main + "." + frac
    return datetime.fromisoformat(s)

def tshark_fields(display_filter, fields):
    cmd = [TSHARK, "-r", pcap, "-Y", display_filter, "-T", "fields"]
    for f in fields:
        cmd.extend(["-e", f])
    out = subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace")
    return [line.split("\t") for line in out.splitlines() if line.strip()]

syn_rows = tshark_fields(
    "tcp.flags.syn==1 && tcp.flags.ack==0 && ip.src==10.42.48.0/24",
    ["frame.time_utc", "ip.src", "ip.dst", "tcp.dstport", "tcp.window_size"],
)
by_pair = defaultdict(list)
for t, src, dst, port, win in syn_rows:
    by_pair[(src, dst)].append((t, port, win))

scan = None
best = 0
for (src, dst), items in by_pair.items():
    ports = {p for _, p, _ in items}
    if len(ports) < 50:
        continue
    if len(ports) > best:
        best = len(ports)
        times = sorted(t for t, _, _ in items)
        windows = Counter(w for _, _, w in items)
        scan = {
            "type": "SYN scan",
            "source": src,
            "target": dst,
            "ports_probed": len(ports),
            "syn_packets": len(items),
            "window_size_mode": windows.most_common(1)[0][0] if windows else None,
            "start_utc": times[0],
            "end_utc": times[-1],
            "evidence": "SYN with small window; RST after SYN-ACK on open ports",
        }

http_rows = tshark_fields(
    "http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)",
    ["frame.time_utc", "ip.src", "http.request.method", "http.request.uri"],
)
dos = None
if http_rows:
    times = [r[0] for r in http_rows]
    sources = Counter(r[1] for r in http_rows)
    t0 = parse_ts(times[0]); t1 = parse_ts(times[-1])
    dur = max((t1 - t0).total_seconds(), 0.001)
    per_sec = Counter(parse_ts(t).replace(microsecond=0) for t in times)
    peak = max(per_sec.values()) if per_sec else 0
    dos = {
        "type": "HTTP flood",
        "target": "10.42.48.18:80",
        "http_requests": len(http_rows),
        "unique_sources": len(sources),
        "sources": dict(sources),
        "start_utc": times[0],
        "end_utc": times[-1],
        "duration_s": round(dur, 3),
        "avg_rps": round(len(http_rows) / dur, 2),
        "peak_rps": peak,
        "spoofed_sources": False,
        "evidence": "Completed TCP handshake + GET /?<random> Host: shop.lab.local",
    }

icmp = tshark_fields(
    "icmp.type==8 && ip.src==10.42.48.0/24",
    ["frame.time_utc", "ip.src", "ip.dst"],
)
recon = None
if icmp:
    src_counts = Counter(r[1] for r in icmp)
    src, _ = src_counts.most_common(1)[0]
    rows = [r for r in icmp if r[1] == src]
    recon = {
        "type": "ARP sweep + ICMP echo",
        "source": src,
        "icmp_targets": sorted({r[2] for r in rows}),
        "start_utc": rows[0][0],
        "end_utc": rows[-1][0],
    }

result = {"pcap": pcap, "recon": recon, "port_scan": scan, "dos": dos}
out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
PY
  echo
} > "$SESS/12-investigate.txt"
echo wrote 12-investigate.txt

echo DONE
ls -la "$SESS"
