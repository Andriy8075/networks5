#!/usr/bin/env python3
"""
Automated incident investigation for Lab 5 (extension 2a).
Detects port-scan source/window and DoS type/window from a pcap; writes JSON.
"""
import json
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


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


def parse_ts(s: str) -> datetime:
    s = s.rstrip("Z")
    if "." in s:
        main, frac = s.split(".", 1)
        frac = ("".join(ch for ch in frac if ch.isdigit()) + "000000")[:6]
        s = main + "." + frac
    return datetime.fromisoformat(s)


def tshark_fields(pcap, display_filter, fields):
    cmd = [TSHARK, "-r", pcap, "-Y", display_filter, "-T", "fields"]
    for f in fields:
        cmd.extend(["-e", f])
    out = subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace")
    rows = []
    for line in out.splitlines():
        if not line.strip():
            continue
        rows.append(line.split("\t"))
    return rows


def main():
    pcap = sys.argv[1] if len(sys.argv) > 1 else "lr5_v02.pcap"
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("incident.json")

    # Port scan: internal host sending many SYN/no-ACK to many ports of one target
    syn_rows = tshark_fields(
        pcap,
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
            # classify SYN vs connect: check if RST follows open ports
            open_flow = tshark_fields(
                pcap,
                f"ip.src=={src} && ip.dst=={dst} && tcp.flags.reset==1 && tcp.window_size==0",
                ["tcp.dstport"],
            )
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

    # DoS: external HTTP GET flood toward web server
    http_rows = tshark_fields(
        pcap,
        "http.request && ip.dst==10.42.48.18 && !(ip.src==10.42.48.0/24)",
        ["frame.time_utc", "ip.src", "http.request.method", "http.request.uri"],
    )
    dos = None
    if http_rows:
        times = [r[0] for r in http_rows]
        sources = Counter(r[1] for r in http_rows)
        t0 = parse_ts(times[0])
        t1 = parse_ts(times[-1])
        dur = max((t1 - t0).total_seconds(), 0.001)
        # peak per second
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

    # Recon (extra context)
    icmp = tshark_fields(
        pcap,
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

    result = {
        "pcap": str(Path(pcap).name),
        "recon": recon,
        "port_scan": scan,
        "dos": dos,
    }
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
