#!/usr/bin/env bash
set -eu
LAB=/mnt/c/Users/Admin/projects/NetworkLabs/lab5
cd "$LAB"
export PATH="$HOME/bin:$PATH"
PROMPT='andrii@DESKTOP-7BD93CN:/mnt/c/Users/Admin/projects/NetworkLabs/lab5'
PCAP=lr5_v02.pcap
SESS=evidence/console/sessions

{
  echo "${PROMPT}\$ sha256sum ${PCAP}"
  sha256sum "$PCAP"
  echo
  echo "${PROMPT}\$ capinfos ${PCAP}"
  capinfos "$PCAP"
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -T fields -e frame.time_utc | head -n 1"
  tshark -r "$PCAP" -T fields -e frame.time_utc | head -n 1
  echo
  echo "${PROMPT}\$ tshark -r ${PCAP} -T fields -e frame.time_utc | tail -n 1"
  tshark -r "$PCAP" -T fields -e frame.time_utc | tail -n 1
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
  echo "${PROMPT}\$ tshark -r ${PCAP} -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src | sort | uniq -c | sort -rn | head"
  tshark -r "$PCAP" -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src | sort | uniq -c | sort -rn | head
  echo
  echo "${PROMPT}\$ python3 evidence/scripts/count_syn_by_src.py ${PCAP} | head"
  python3 evidence/scripts/count_syn_by_src.py "$PCAP" | head
  echo
} > "$SESS/08-syn-by-src.txt"
echo wrote 08

python3 - <<'PY'
from pathlib import Path
p = Path("evidence/console/sessions/07-impact.txt")
lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
if len(lines) > 80:
    out=[]; i=0
    while i < len(lines):
        out.append(lines[i])
        if lines[i].startswith("andrii@"):
            i += 1
            kept = 0
            while i < len(lines) and not lines[i].startswith("andrii@"):
                if kept < 40:
                    out.append(lines[i]); kept += 1
                i += 1
            if kept >= 40:
                out.append("... [скорочено]")
            continue
        i += 1
    p.write_text("\n".join(out).rstrip()+"\n", encoding="utf-8")
    print("truncated 07 to", len(out), "lines")
else:
    print("07 ok", len(lines))
PY

# Also rewrite investigate session prompt command to short form if needed
echo DONE
grep -n "tshark\|capinfos\|Program Files" "$SESS"/0*.txt | head -n 40
