#!/usr/bin/env python3
"""Summarize Suricata eve.json alerts."""
import json
import sys
from collections import Counter, defaultdict

eve_json_path = sys.argv[1] if len(sys.argv) > 1 else "eve.json"

# How many times each alert signature name appeared.
signature_counts = Counter()

# Per-signature extras: unique source/destination IPs and first/last timestamps.
signature_details = defaultdict(
    lambda: {
        "source_ips": set(),
        "destination_ips": set(),
        "first_timestamp": None,
        "last_timestamp": None,
    }
)

total_alert_events = 0

with open(eve_json_path, encoding="utf-8", errors="replace") as eve_file:
    for raw_line in eve_file:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            # Each line of eve.json is one JSON object (NDJSON), not one big array.
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        # Skip flow/http/dns/... records; keep only IDS alerts.
        if event.get("event_type") != "alert":
            continue

        total_alert_events += 1
        alert_info = event.get("alert", {})
        signature_name = alert_info.get("signature", "?")
        signature_counts[signature_name] += 1

        details = signature_details[signature_name]
        source_ip = event.get("src_ip")
        destination_ip = event.get("dest_ip")
        if source_ip:
            details["source_ips"].add(source_ip)
        if destination_ip:
            details["destination_ips"].add(destination_ip)

        event_timestamp = event.get("timestamp")
        if event_timestamp:
            if (
                details["first_timestamp"] is None
                or event_timestamp < details["first_timestamp"]
            ):
                details["first_timestamp"] = event_timestamp
            if (
                details["last_timestamp"] is None
                or event_timestamp > details["last_timestamp"]
            ):
                details["last_timestamp"] = event_timestamp

print(f"alerts: {total_alert_events}")
for signature_name, alert_count in signature_counts.most_common():
    details = signature_details[signature_name]
    print(
        f"{alert_count}\t{signature_name}\t"
        f"src={sorted(details['source_ips'])}\t"
        f"dst={sorted(details['destination_ips'])}\t"
        f"{details['first_timestamp']} -> {details['last_timestamp']}"
    )
