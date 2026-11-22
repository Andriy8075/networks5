#!/usr/bin/env python3
"""Count SYN-without-ACK packets per source IP (tshark automation)."""
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

PCAP = sys.argv[1] if len(sys.argv) > 1 else "lr5_v02.pcap"


def find_tshark() -> str:
    for name in ("tshark", "tshark.exe"):
        found = shutil.which(name)
        if found:
            return found
    win = Path(r"C:\Program Files\Wireshark\tshark.exe")
    if win.exists():
        return str(win)
    raise SystemExit("tshark not found in PATH")


TSHARK = find_tshark()

cmd = [
    TSHARK, "-r", PCAP,
    "-Y", "tcp.flags.syn==1 && tcp.flags.ack==0",
    "-T", "fields", "-e", "ip.src",
]
out = subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace")
counts = Counter(line.strip() for line in out.splitlines() if line.strip())
for ip, n in counts.most_common():
    print(f"{n:6d}  {ip}")
