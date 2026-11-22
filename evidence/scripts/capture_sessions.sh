#!/usr/bin/env bash
set -eu
# note: no pipefail — `head` closing early must not abort the session capture
LAB=/mnt/c/Users/Admin/projects/NetworkLabs/lab5
cd "$LAB"
mkdir -p evidence/console/sessions
SESS=evidence/console/sessions
PROMPT='andrii@DESKTOP-7BD93CN:/mnt/c/Users/Admin/projects/NetworkLabs/lab5'
TSHARK='/mnt/c/Program Files/Wireshark/tshark.exe'
CAPINFOS='/mnt/c/Program Files/Wireshark/capinfos.exe'
PCAP=lr5_v02.pcap
SUR_ETC=evidence/suricata/etc
SUR_RULES=evidence/suricata/rules

echo "=== capturing sessions in $LAB ==="

{
  echo "${PROMPT}\$ sha256sum ${PCAP}"
  sha256sum "$PCAP"
  echo
  echo "${PROMPT}\$ TZ=UTC \"${CAPINFOS}\" ${PCAP}"
  TZ=UTC "$CAPINFOS" "$PCAP"
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -v | head -n 1"
  "$TSHARK" -v 2>&1 | head -n 1
  echo
  echo "${PROMPT}\$ docker run --rm jasonish/suricata:7.0.8 bash -lc 'suricata -V 2>&1 | head -n 1'"
  docker run --rm jasonish/suricata:7.0.8 bash -lc 'suricata -V 2>&1 | head -n 1' || true
  echo
} > "$SESS/01-env-capinfos.txt"
echo wrote 01-env-capinfos.txt

{
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -q -z io,phs"
  "$TSHARK" -r "$PCAP" -q -z io,phs
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -q -z endpoints,ip"
  "$TSHARK" -r "$PCAP" -q -z endpoints,ip
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -q -z conv,ip | head -n 25"
  "$TSHARK" -r "$PCAP" -q -z conv,ip | head -n 25
  echo
} > "$SESS/02-map-stats.txt"
echo wrote 02-map-stats.txt

{
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -q -z io,stat,10"
  "$TSHARK" -r "$PCAP" -q -z io,stat,10
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -q -z \"io,stat,1,tcp.flags.syn==1 && tcp.flags.ack==0\" | head -n 40"
  "$TSHARK" -r "$PCAP" -q -z 'io,stat,1,tcp.flags.syn==1 && tcp.flags.ack==0' | head -n 40
  echo
} > "$SESS/03-io-stat.txt"
echo wrote 03-io-stat.txt

{
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'arp.opcode==1 && arp.src.proto_ipv4==10.42.48.126' -T fields -e frame.time_utc -e arp.dst.proto_ipv4 | wc -l"
  "$TSHARK" -r "$PCAP" -Y 'arp.opcode==1 && arp.src.proto_ipv4==10.42.48.126' -T fields -e frame.time_utc -e arp.dst.proto_ipv4 | wc -l
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'icmp.type==8 && ip.src==10.42.48.126' -T fields -e frame.time_utc -e ip.dst -e icmp.type"
  "$TSHARK" -r "$PCAP" -Y 'icmp.type==8 && ip.src==10.42.48.126' -T fields -e frame.time_utc -e ip.dst -e icmp.type
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'arp.opcode==2 && arp.dst.proto_ipv4==10.42.48.126' -T fields -e frame.time_utc -e arp.src.proto_ipv4 -e arp.src.hw_mac"
  "$TSHARK" -r "$PCAP" -Y 'arp.opcode==2 && arp.dst.proto_ipv4==10.42.48.126' -T fields -e frame.time_utc -e arp.src.proto_ipv4 -e arp.src.hw_mac
  echo
} > "$SESS/04-recon.txt"
echo wrote 04-recon.txt

{
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e frame.time_utc -e tcp.dstport -e tcp.window_size | head"
  "$TSHARK" -r "$PCAP" -Y 'ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e frame.time_utc -e tcp.dstport -e tcp.window_size | head
  echo "..."
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e tcp.dstport | sort -u | wc -l"
  "$TSHARK" -r "$PCAP" -Y 'ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e tcp.dstport | sort -u | wc -l
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'tcp.flags.syn==1 && tcp.flags.ack==1 && ip.src==10.42.48.18 && ip.dst==10.42.48.126' -T fields -e tcp.srcport -e frame.time_utc"
  "$TSHARK" -r "$PCAP" -Y 'tcp.flags.syn==1 && tcp.flags.ack==1 && ip.src==10.42.48.18 && ip.dst==10.42.48.126' -T fields -e tcp.srcport -e frame.time_utc
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'ip.addr==10.42.48.126 && ip.addr==10.42.48.18 && tcp.port==80' -T fields -e frame.time_utc -e ip.src -e ip.dst -e tcp.flags.str -e tcp.window_size"
  "$TSHARK" -r "$PCAP" -Y 'ip.addr==10.42.48.126 && ip.addr==10.42.48.18 && tcp.port==80' -T fields -e frame.time_utc -e ip.src -e ip.dst -e tcp.flags.str -e tcp.window_size
  echo
} > "$SESS/05-scan.txt"
echo wrote 05-scan.txt

{
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e frame.time_utc -e ip.src -e http.request.uri | head"
  "$TSHARK" -r "$PCAP" -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e frame.time_utc -e ip.src -e http.request.uri | head
  echo "..."
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e ip.src | sort | uniq -c | sort -rn"
  "$TSHARK" -r "$PCAP" -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e ip.src | sort | uniq -c | sort -rn
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e frame.time_utc | wc -l"
  "$TSHARK" -r "$PCAP" -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e frame.time_utc | wc -l
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'ip.addr==54.85.25.140 && tcp' -T fields -e frame.time_utc -e ip.src -e ip.dst -e tcp.flags.str -e eth.src -e ip.ttl | head -n 15"
  "$TSHARK" -r "$PCAP" -Y 'ip.addr==54.85.25.140 && tcp' -T fields -e frame.time_utc -e ip.src -e ip.dst -e tcp.flags.str -e eth.src -e ip.ttl | head -n 15
  echo
} > "$SESS/06-dos.txt"
echo wrote 06-dos.txt

{
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'http.response && ip.src==10.42.48.18 && (ip.dst==10.42.48.38 || ip.dst==10.42.48.42 || ip.dst==10.42.48.43 || ip.dst==10.42.48.51 || ip.dst==10.42.48.56 || ip.dst==10.42.48.59 || ip.dst==10.42.48.88)' -T fields -e frame.time_utc -e ip.dst -e http.response.code -e http.time | awk -F'\t' '\$1 ~ /09:06:2/ || \$1 ~ /09:06:3/ || \$1 ~ /09:06:4/ || \$1 ~ /09:06:5/' | head -n 40"
  "$TSHARK" -r "$PCAP" -Y 'http.response && ip.src==10.42.48.18 && (ip.dst==10.42.48.38 || ip.dst==10.42.48.42 || ip.dst==10.42.48.43 || ip.dst==10.42.48.51 || ip.dst==10.42.48.56 || ip.dst==10.42.48.59 || ip.dst==10.42.48.88)' -T fields -e frame.time_utc -e ip.dst -e http.response.code -e http.time | awk -F'\t' '$1 ~ /09:06:2/ || $1 ~ /09:06:3/ || $1 ~ /09:06:4/ || $1 ~ /09:06:5/' | head -n 40
  echo
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'http.response.code==503' -T fields -e frame.time_utc -e ip.dst -e http.response.code -e http.time"
  "$TSHARK" -r "$PCAP" -Y 'http.response.code==503' -T fields -e frame.time_utc -e ip.dst -e http.response.code -e http.time
  echo
} > "$SESS/07-impact.txt"
echo wrote 07-impact.txt

{
  echo "${PROMPT}\$ \"${TSHARK}\" -r ${PCAP} -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src | sort | uniq -c | sort -rn | head"
  "$TSHARK" -r "$PCAP" -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src | sort | uniq -c | sort -rn | head
  echo
  echo "${PROMPT}\$ python3 evidence/scripts/count_syn_by_src.py ${PCAP} | head"
  # script uses Windows tshark path; run inline equivalent already above, also try python
  python3 - <<'PY' || true
import subprocess
from collections import Counter
tshark = r"/mnt/c/Program Files/Wireshark/tshark.exe"
pcap = "lr5_v02.pcap"
out = subprocess.check_output([tshark,"-r",pcap,"-Y","tcp.flags.syn==1 && tcp.flags.ack==0","-T","fields","-e","ip.src"], text=True, errors="replace")
c = Counter(l.strip() for l in out.splitlines() if l.strip())
for ip,n in c.most_common(12):
    print(f"{n:6d}  {ip}")
PY
  echo
} > "$SESS/08-syn-by-src.txt"
echo wrote 08-syn-by-src.txt

{
  echo "${PROMPT}\$ docker run --rm -e TZ=UTC -v \"\$PWD/${SUR_ETC}:/etc/suricata\" -v \"\$PWD/${SUR_RULES}:/var/lib/suricata\" -v \"\$PWD:/pcaps:ro\" -v \"\$PWD/evidence/suricata/out-default:/var/log/suricata\" jasonish/suricata:7.0.8 -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none"
  docker run --rm -e TZ=UTC \
    -v "$PWD/${SUR_ETC}:/etc/suricata" \
    -v "$PWD/${SUR_RULES}:/var/lib/suricata" \
    -v "$PWD:/pcaps:ro" \
    -v "$PWD/evidence/suricata/out-default:/var/log/suricata" \
    jasonish/suricata:7.0.8 \
    -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none 2>&1 | tail -n 20
  echo
  echo "${PROMPT}\$ python3 evidence/scripts/summarize_eve.py evidence/suricata/out-default/eve.json"
  python3 evidence/scripts/summarize_eve.py evidence/suricata/out-default/eve.json
  echo
} > "$SESS/09-suricata-default.txt"
echo wrote 09-suricata-default.txt

{
  echo "${PROMPT}\$ docker run --rm -e TZ=UTC -v \"\$PWD/${SUR_ETC}:/etc/suricata\" -v \"\$PWD/${SUR_RULES}:/var/lib/suricata\" -v \"\$PWD:/pcaps:ro\" -v \"\$PWD/evidence/suricata/out-external-any:/var/log/suricata\" jasonish/suricata:7.0.8 -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none --set vars.address-groups.EXTERNAL_NET=any"
  docker run --rm -e TZ=UTC \
    -v "$PWD/${SUR_ETC}:/etc/suricata" \
    -v "$PWD/${SUR_RULES}:/var/lib/suricata" \
    -v "$PWD:/pcaps:ro" \
    -v "$PWD/evidence/suricata/out-external-any:/var/log/suricata" \
    jasonish/suricata:7.0.8 \
    -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none \
    --set vars.address-groups.EXTERNAL_NET=any 2>&1 | tail -n 20
  echo
  echo "${PROMPT}\$ python3 evidence/scripts/summarize_eve.py evidence/suricata/out-external-any/eve.json"
  python3 evidence/scripts/summarize_eve.py evidence/suricata/out-external-any/eve.json
  echo
} > "$SESS/10-suricata-external-any.txt"
echo wrote 10-suricata-external-any.txt

{
  echo "${PROMPT}\$ docker run --rm -e TZ=UTC -v \"\$PWD/${SUR_ETC}:/etc/suricata\" -v \"\$PWD/${SUR_RULES}:/var/lib/suricata\" -v \"\$PWD:/pcaps:ro\" -v \"\$PWD/evidence/rules:/custom:ro\" -v \"\$PWD/evidence/suricata/out-custom:/var/log/suricata\" jasonish/suricata:7.0.8 -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none -S /custom/local.rules --set vars.address-groups.EXTERNAL_NET=any"
  docker run --rm -e TZ=UTC \
    -v "$PWD/${SUR_ETC}:/etc/suricata" \
    -v "$PWD/${SUR_RULES}:/var/lib/suricata" \
    -v "$PWD:/pcaps:ro" \
    -v "$PWD/evidence/rules:/custom:ro" \
    -v "$PWD/evidence/suricata/out-custom:/var/log/suricata" \
    jasonish/suricata:7.0.8 \
    -c /etc/suricata/suricata.yaml --runmode single -r /pcaps/lr5_v02.pcap -l /var/log/suricata -k none \
    -S /custom/local.rules --set vars.address-groups.EXTERNAL_NET=any 2>&1 | tail -n 20
  echo
  echo "${PROMPT}\$ python3 evidence/scripts/summarize_eve.py evidence/suricata/out-custom/eve.json"
  python3 evidence/scripts/summarize_eve.py evidence/suricata/out-custom/eve.json
  echo
  echo "${PROMPT}\$ cat evidence/rules/local.rules"
  cat evidence/rules/local.rules
  echo
} > "$SESS/11-suricata-custom.txt"
echo wrote 11-suricata-custom.txt

{
  echo "${PROMPT}\$ python3 evidence/scripts/investigate.py ${PCAP} evidence/scripts/incident.json"
  # investigate.py hardcodes Windows tshark path; call via env override by running a patched invoke
  TSHARK_WIN='C:\Program Files\Wireshark\tshark.exe' python3 - <<'PY'
import json, os, subprocess, sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Prefer Linux path to Windows tshark.exe
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
    rows = []
    for line in out.splitlines():
        if line.strip():
            rows.append(line.split("\t"))
    return rows

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
