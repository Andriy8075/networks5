#!/usr/bin/env bash
set -eu
# Re-capture tshark/capinfos sessions with short command names (tshark, capinfos)
LAB=/mnt/c/Users/Admin/projects/NetworkLabs/lab5
cd "$LAB"
export PATH="$HOME/bin:$PATH"
SESS=evidence/console/sessions
PROMPT='andrii@DESKTOP-7BD93CN:/mnt/c/Users/Admin/projects/NetworkLabs/lab5'
PCAP=lr5_v02.pcap

echo "tshark -> $(command -v tshark)"
echo "capinfos -> $(command -v capinfos)"

{
  echo "${PROMPT}\$ sha256sum ${PCAP}"
  sha256sum "$PCAP"
  echo
  echo "${PROMPT}\$ TZ=UTC capinfos ${PCAP}"
  TZ=UTC capinfos "$PCAP"
  echo
  echo "${PROMPT}\$ tshark -v | head -n 1"
  tshark -v 2>&1 | head -n 1
  echo
  echo "${PROMPT}\$ docker run --rm --entrypoint suricata jasonish/suricata:7.0.8 -V"
  docker run --rm --entrypoint suricata jasonish/suricata:7.0.8 -V 2>&1 | head -n 1
  echo
} > "$SESS/01-env-capinfos.txt"
echo wrote 01

{
  echo "${PROMPT}\$ tshark -r ${PCAP} -q -z io,phs"
  tshark -r "$PCAP" -q -z io,phs
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -q -z endpoints,ip"
  tshark -r "$PCAP" -q -z endpoints,ip
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -q -z conv,ip | head -n 25"
  tshark -r "$PCAP" -q -z conv,ip | head -n 25
  echo
} > "$SESS/02-map-stats.txt"
echo wrote 02

{
  echo "${PROMPT}\$ tshark -r ${PCAP} -q -z io,stat,10"
  tshark -r "$PCAP" -q -z io,stat,10
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -q -z \"io,stat,1,tcp.flags.syn==1 && tcp.flags.ack==0\" | head -n 40"
  tshark -r "$PCAP" -q -z 'io,stat,1,tcp.flags.syn==1 && tcp.flags.ack==0' | head -n 40
  echo
} > "$SESS/03-io-stat.txt"
echo wrote 03

{
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'arp.opcode==1 && arp.src.proto_ipv4==10.42.48.126' -T fields -e frame.time_utc -e arp.dst.proto_ipv4 | wc -l"
  tshark -r "$PCAP" -Y 'arp.opcode==1 && arp.src.proto_ipv4==10.42.48.126' -T fields -e frame.time_utc -e arp.dst.proto_ipv4 | wc -l
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'icmp.type==8 && ip.src==10.42.48.126' -T fields -e frame.time_utc -e ip.dst -e icmp.type"
  tshark -r "$PCAP" -Y 'icmp.type==8 && ip.src==10.42.48.126' -T fields -e frame.time_utc -e ip.dst -e icmp.type
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'arp.opcode==2 && arp.dst.proto_ipv4==10.42.48.126' -T fields -e frame.time_utc -e arp.src.proto_ipv4 -e arp.src.hw_mac"
  tshark -r "$PCAP" -Y 'arp.opcode==2 && arp.dst.proto_ipv4==10.42.48.126' -T fields -e frame.time_utc -e arp.src.proto_ipv4 -e arp.src.hw_mac
  echo
} > "$SESS/04-recon.txt"
echo wrote 04

{
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e frame.time_utc -e tcp.dstport -e tcp.window_size | head"
  tshark -r "$PCAP" -Y 'ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e frame.time_utc -e tcp.dstport -e tcp.window_size | head
  echo "..."
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e tcp.dstport | sort -u | wc -l"
  tshark -r "$PCAP" -Y 'ip.src==10.42.48.126 && tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e tcp.dstport | sort -u | wc -l
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'tcp.flags.syn==1 && tcp.flags.ack==1 && ip.src==10.42.48.18 && ip.dst==10.42.48.126' -T fields -e tcp.srcport -e frame.time_utc"
  tshark -r "$PCAP" -Y 'tcp.flags.syn==1 && tcp.flags.ack==1 && ip.src==10.42.48.18 && ip.dst==10.42.48.126' -T fields -e tcp.srcport -e frame.time_utc
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'ip.addr==10.42.48.126 && ip.addr==10.42.48.18 && tcp.port==80' -T fields -e frame.time_utc -e ip.src -e ip.dst -e tcp.flags.str -e tcp.window_size"
  tshark -r "$PCAP" -Y 'ip.addr==10.42.48.126 && ip.addr==10.42.48.18 && tcp.port==80' -T fields -e frame.time_utc -e ip.src -e ip.dst -e tcp.flags.str -e tcp.window_size
  echo
} > "$SESS/05-scan.txt"
echo wrote 05

{
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e frame.time_utc -e ip.src -e http.request.uri | head"
  tshark -r "$PCAP" -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e frame.time_utc -e ip.src -e http.request.uri | head
  echo "..."
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e ip.src | sort | uniq -c | sort -rn"
  tshark -r "$PCAP" -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e ip.src | sort | uniq -c | sort -rn
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e frame.time_utc | wc -l"
  tshark -r "$PCAP" -Y 'http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)' -T fields -e frame.time_utc | wc -l
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'ip.addr==54.85.25.140 && tcp' -T fields -e frame.time_utc -e ip.src -e ip.dst -e tcp.flags.str -e eth.src -e ip.ttl | head -n 15"
  tshark -r "$PCAP" -Y 'ip.addr==54.85.25.140 && tcp' -T fields -e frame.time_utc -e ip.src -e ip.dst -e tcp.flags.str -e eth.src -e ip.ttl | head -n 15
  echo
} > "$SESS/06-dos.txt"
echo wrote 06

{
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'http.response && ip.src==10.42.48.18 && (ip.dst==10.42.48.38 || ip.dst==10.42.48.42 || ip.dst==10.42.48.43 || ip.dst==10.42.48.51 || ip.dst==10.42.48.56 || ip.dst==10.42.48.59 || ip.dst==10.42.48.88)' -T fields -e frame.time_utc -e ip.dst -e http.response.code -e http.time | awk -F'\\t' '\$1 ~ /09:06:2/ || \$1 ~ /09:06:3/ || \$1 ~ /09:06:4/ || \$1 ~ /09:06:5/' | head -n 40"
  tshark -r "$PCAP" -Y 'http.response && ip.src==10.42.48.18 && (ip.dst==10.42.48.38 || ip.dst==10.42.48.42 || ip.dst==10.42.48.43 || ip.dst==10.42.48.51 || ip.dst==10.42.48.56 || ip.dst==10.42.48.59 || ip.dst==10.42.48.88)' -T fields -e frame.time_utc -e ip.dst -e http.response.code -e http.time | awk -F'\t' '$1 ~ /09:06:2/ || $1 ~ /09:06:3/ || $1 ~ /09:06:4/ || $1 ~ /09:06:5/' | head -n 40
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'http.response.code==503' -T fields -e frame.time_utc -e ip.dst -e http.response.code -e http.time"
  tshark -r "$PCAP" -Y 'http.response.code==503' -T fields -e frame.time_utc -e ip.dst -e http.response.code -e http.time
  echo
} > "$SESS/07-impact.txt"
echo wrote 07

{
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src | sort | uniq -c | sort -rn | head"
  tshark -r "$PCAP" -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src | sort | uniq -c | sort -rn | head
  echo
  echo "${PROMPT}\$ python3 evidence/scripts/count_syn_by_src.py ${PCAP} | head"
  # keep inline counter so it does not depend on Windows-only path inside the py script
  python3 - <<'PY'
import subprocess
from collections import Counte
out = subprocess.check_output(
    ["tshark", "-r", "lr5_v02.pcap", "-Y", "tcp.flags.syn==1 && tcp.flags.ack==0", "-T", "fields", "-e", "ip.src"],
    text=True, errors="replace",
)
c = Counter(l.strip() for l in out.splitlines() if l.strip())
for ip, n in c.most_common(12):
    print(f"{n:6d}  {ip}")
PY
  echo
} > "$SESS/08-syn-by-src.txt"
echo wrote 08

echo DONE
