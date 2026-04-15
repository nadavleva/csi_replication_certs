#!/usr/bin/env python3
"""
generate-tracking-csv.py

Generates the test-execution-tracking.csv from the canonical test list.
Optionally reads one or more JUnit XML files to populate run columns.

Usage:
    python3 scripts/generate-tracking-csv.py \
        [--junit <junit.xml> ...] \
        [--output tracking/test-execution-tracking.csv]
"""

import argparse
import csv
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Canonical test list
# Columns: Test ID, Category, Description, Node Role, Peer State, Array State,
#          Params, Test Type, Cluster Mode, Expected Duration, Implementation Status
# ---------------------------------------------------------------------------
TESTS = [
    # EnableVolumeReplication (9 specs)
    ["L1-E-001", "EnableVolumeReplication", "Enable snapshot mode replication", "Primary", "Up", "N/A", "mode=snapshot", "functional", "Single", "~6s", "Implemented"],
    ["L1-E-002", "EnableVolumeReplication", "Enable journal mode replication", "Primary", "Up", "N/A", "mode=journal", "functional", "Single", "~6s", "Implemented"],
    ["L1-E-003", "EnableVolumeReplication", "Peer cluster unreachable", "Primary", "Down", "N/A", "mode=snapshot", "negative", "Single", "~180s", "Implemented"],
    ["L1-E-004", "EnableVolumeReplication", "Invalid schedulingInterval parameter", "Primary", "Up", "N/A", "interval=5x", "negative", "Single", "~6s", "Implemented"],
    ["L1-E-005", "EnableVolumeReplication", "Idempotent enable (already-enabled volume)", "Primary", "Up", "N/A", "(none)", "functional", "Single", "~6s", "Implemented"],
    ["L1-E-006", "EnableVolumeReplication", "Invalid/missing secret reference", "Primary", "Up", "N/A", "secret=missing", "negative", "Single", "~6s", "Implemented"],
    ["L1-E-007", "EnableVolumeReplication", "Invalid mirroringMode parameter", "Primary", "Up", "N/A", "mode=invalid", "negative", "Single", "~6s", "Implemented"],
    ["L1-E-008", "EnableVolumeReplication", "Future schedulingStartTime (deferred replication)", "Primary", "Up", "N/A", "startTime=future", "functional", "Single", "~6s", "Implemented"],
    ["L1-E-009", "EnableVolumeReplication", "Invalid schedulingStartTime format", "Primary", "Up", "N/A", "startTime=bad", "negative", "Single", "~6s", "Implemented"],

    # GetVolumeReplicationInfo (7 specs, mostly integrated with Enable tests)
    ["L1-INFO-001", "GetVolumeReplicationInfo", "Successful replication info (Replicating=True)", "Primary", "Up", "N/A", "(none)", "functional", "Single", "integrated", "Implemented"],
    ["L1-INFO-005", "GetVolumeReplicationInfo", "Error info when peer is unreachable", "Primary", "Down", "N/A", "(none)", "negative", "Single", "integrated", "Implemented"],
    ["L1-INFO-008", "GetVolumeReplicationInfo", "Non-existent volume (error handling)", "Primary", "Up", "N/A", "vol=nonexistent", "negative", "Single", "~2s", "Implemented"],
    ["L1-INFO-011", "GetVolumeReplicationInfo", "Invalid mirroringMode (error in conditions)", "Primary", "Up", "N/A", "mode=invalid", "negative", "Single", "integrated", "Implemented"],
    ["L1-INFO-012", "GetVolumeReplicationInfo", "Invalid schedulingInterval (error in conditions)", "Primary", "Up", "N/A", "interval=5x", "negative", "Single", "integrated", "Implemented"],
    ["L1-INFO-013", "GetVolumeReplicationInfo", "Invalid secret (error in conditions)", "Primary", "Up", "N/A", "secret=missing", "negative", "Single", "integrated", "Implemented"],
    ["L1-INFO-014", "GetVolumeReplicationInfo", "Invalid time format (error in conditions)", "Primary", "Up", "N/A", "startTime=bad", "negative", "Single", "integrated", "Implemented"],

    # DisableVolumeReplication (12 specs)
    ["L1-DIS-001", "DisableVolumeReplication", "Disable active replication on primary", "Primary", "Up", "N/A", "force=false", "functional", "Single", "~6s", "Implemented"],
    ["L1-DIS-002", "DisableVolumeReplication", "Disable active replication on secondary", "Secondary", "Up", "N/A", "force=false", "functional", "Full DR", "~31s", "Implemented"],
    ["L1-DIS-003", "DisableVolumeReplication", "Idempotent disable (no VR on primary)", "Primary", "Up", "N/A", "force=false", "functional", "Single", "~4s", "Implemented"],
    ["L1-DIS-004", "DisableVolumeReplication", "Idempotent disable (no VR on secondary)", "Secondary", "Up", "N/A", "force=false", "functional", "Full DR", "~4s", "Implemented"],
    ["L1-DIS-005", "DisableVolumeReplication", "Disable with peer unreachable (force=false)", "Primary", "Down", "N/A", "force=false", "negative", "Full DR + NetworkFence", "~6s", "Implemented"],
    ["L1-DIS-006", "DisableVolumeReplication", "Disable with peer unreachable (force=true)", "Primary", "Down", "N/A", "force=true", "negative", "Full DR + NetworkFence", "~6s", "Implemented"],
    ["L1-DIS-007", "DisableVolumeReplication", "Disable with array unreachable (force=false)", "Primary", "Up", "Down", "force=false", "negative", "Full DR + iptables", "~6s", "Blocked (#9)"],
    ["L1-DIS-008", "DisableVolumeReplication", "Disable with array unreachable (force=true)", "Primary", "Up", "Down", "force=true", "negative", "Full DR + iptables", "~6s", "Blocked (#9)"],
    ["L1-DIS-009", "DisableVolumeReplication", "Force disable active replication (primary)", "Primary", "Up", "N/A", "force=true", "functional", "Single", "~6s", "Implemented"],
    ["L1-DIS-010", "DisableVolumeReplication", "Force disable active replication (secondary)", "Secondary", "Up", "N/A", "force=true", "functional", "Full DR", "~31s", "Implemented"],
    ["L1-DIS-011", "DisableVolumeReplication", "Force disable idempotent (no VR on primary)", "Primary", "Up", "N/A", "force=true", "functional", "Single", "~4s", "Implemented"],
    ["L1-DIS-012", "DisableVolumeReplication", "Force disable idempotent (no VR on secondary)", "Secondary", "Up", "N/A", "force=true", "functional", "Full DR", "~4s", "Implemented"],

    # PromoteVolumeReplication (8 specs)
    ["L1-PROM-001", "PromoteVolumeReplication", "Promote secondary to primary (healthy)", "Secondary", "Up", "N/A", "force=false", "functional", "Full DR", "~40s", "Implemented"],
    ["L1-PROM-002", "PromoteVolumeReplication", "Idempotent promote (already primary)", "Primary", "Up", "N/A", "force=false", "functional", "Full DR", "~8s", "Implemented"],
    ["L1-PROM-003", "PromoteVolumeReplication", "Promote with peer unreachable (force=false)", "Secondary", "Down", "N/A", "force=false", "negative", "Full DR + NetworkFence", "~6s", "Implemented"],
    ["L1-PROM-004", "PromoteVolumeReplication", "Promote with peer unreachable (force=true)", "Secondary", "Down", "N/A", "force=true", "negative", "Full DR + NetworkFence", "~6s", "Blocked (#7)"],
    ["L1-PROM-005", "PromoteVolumeReplication", "Promote with array unreachable (force=false)", "Secondary", "Up", "Down", "force=false", "negative", "Full DR + iptables", "~6s", "Blocked (#9)"],
    ["L1-PROM-006", "PromoteVolumeReplication", "Promote with array unreachable (force=true)", "Secondary", "Up", "Down", "force=true", "negative", "Full DR + iptables", "~6s", "Blocked (#9)"],
    ["L1-PROM-007", "PromoteVolumeReplication", "Promote with active I/O workload", "Secondary", "Up", "N/A", "force=false", "behavioral", "Full DR", "~45s", "Implemented"],
    ["L1-PROM-008", "PromoteVolumeReplication", "Force promote with active I/O workload", "Secondary", "Up", "N/A", "force=true", "behavioral", "Full DR", "~45s", "Implemented"],

    # DemoteVolumeReplication (8 specs)
    ["L1-DEM-001", "DemoteVolumeReplication", "Demote primary to secondary (healthy)", "Primary", "Up", "N/A", "force=false", "functional", "Full DR", "~225s", "Implemented"],
    ["L1-DEM-002", "DemoteVolumeReplication", "Idempotent demote (already secondary)", "Secondary", "Up", "N/A", "force=false", "functional", "Full DR", "~31s", "Implemented"],
    ["L1-DEM-003", "DemoteVolumeReplication", "Demote with peer unreachable (force=false)", "Primary", "Down", "N/A", "force=false", "negative", "Full DR + NetworkFence", "~6s", "Implemented"],
    ["L1-DEM-004", "DemoteVolumeReplication", "Demote with peer unreachable (force=true)", "Primary", "Down", "N/A", "force=true", "negative", "Full DR + NetworkFence", "~75s", "Implemented"],
    ["L1-DEM-005", "DemoteVolumeReplication", "Demote with array unreachable (force=false)", "Primary", "Up", "Down", "force=false", "negative", "Full DR + iptables", "~6s", "Blocked (#9)"],
    ["L1-DEM-006", "DemoteVolumeReplication", "Demote with array unreachable (force=true)", "Primary", "Up", "Down", "force=true", "negative", "Full DR + iptables", "~6s", "Blocked (#9)"],
    ["L1-DEM-007", "DemoteVolumeReplication", "Demote with active I/O workload (force=false)", "Primary", "Up", "N/A", "force=false", "behavioral", "Full DR", "~220s", "Implemented"],
    ["L1-DEM-008", "DemoteVolumeReplication", "Force demote with active I/O workload", "Primary", "Up", "N/A", "force=true", "behavioral", "Full DR", "~220s", "Implemented"],

    # ResyncVolumeReplication (5 specs - scaffolded)
    ["L1-RSYNC-001", "ResyncVolumeReplication", "Resync secondary after split-brain", "Secondary", "Up", "N/A", "(none)", "functional", "Full DR", "-", "Scaffold"],
    ["L1-RSYNC-002", "ResyncVolumeReplication", "Idempotent resync", "Secondary", "Up", "N/A", "(none)", "functional", "Full DR", "-", "Scaffold"],
    ["L1-RSYNC-003", "ResyncVolumeReplication", "Resync with NetworkFence", "Secondary", "Down", "N/A", "(none)", "functional", "Full DR + NetworkFence", "-", "Scaffold"],
    ["L1-RSYNC-004", "ResyncVolumeReplication", "Force resync", "Secondary", "Up", "N/A", "force=true", "functional", "Full DR", "-", "Scaffold"],
    ["L1-RSYNC-005", "ResyncVolumeReplication", "Resync error handling", "Secondary", "Up", "N/A", "(none)", "negative", "Full DR", "-", "Scaffold"],
]

# Number of pre-populated run columns in the template (blank placeholders)
TEMPLATE_RUNS = 3

METADATA_HEADERS = [
    "Test ID",
    "Category",
    "Description",
    "Node Role",
    "Peer State",
    "Array State",
    "Params",
    "Test Type",
    "Cluster Mode",
    "Expected Duration",
    "Implementation Status",
]

STATUS_VALUES = ("PASS", "FAIL", "SKIP", "BLOCKED", "")


def run_headers(run_number: int) -> list[str]:
    return [
        f"Run {run_number} - Execution Date",
        f"Run {run_number} - Status",
        f"Run {run_number} - Duration",
        f"Run {run_number} - Notes",
    ]


def parse_junit(path: str) -> dict[str, dict]:
    """Parse a JUnit XML file and return a mapping of test-name -> result dict."""
    tree = ET.parse(path)
    root = tree.getroot()

    # Support both <testsuites><testsuite> and bare <testsuite>
    if root.tag == "testsuites":
        suites = root.findall("testsuite")
    elif root.tag == "testsuite":
        suites = [root]
    else:
        suites = root.findall(".//testsuite")

    results = {}
    for suite in suites:
        suite_ts = suite.get("timestamp", "")
        for tc in suite.findall("testcase"):
            name = tc.get("name", "")
            classname = tc.get("classname", "")
            time_s = tc.get("time", "")

            failure = tc.find("failure")
            error = tc.find("error")
            skipped = tc.find("skipped")

            if skipped is not None:
                status = "SKIP"
            elif failure is not None or error is not None:
                status = "FAIL"
            else:
                status = "PASS"

            msg = ""
            if failure is not None:
                msg = failure.get("message", "") or (failure.text or "")[:120]
            elif error is not None:
                msg = error.get("message", "") or (error.text or "")[:120]
            elif skipped is not None:
                msg = skipped.get("message", "") or (skipped.text or "")[:120]

            # Try to match this test case to a L1-xxx ID embedded in the name
            results[name] = {
                "status": status,
                "duration": f"{float(time_s):.1f}s" if time_s else "",
                "date": suite_ts[:10] if suite_ts else "",
                "notes": msg.replace("\n", " ").strip(),
                "classname": classname,
            }

    return results


def match_junit_result(test_id: str, junit_results: dict) -> dict | None:
    """Find a JUnit result for the given test ID by scanning result names."""
    for name, result in junit_results.items():
        if test_id in name:
            return result
    return None


def build_rows(junit_runs: list[dict]) -> list[list]:
    """Build all CSV data rows from the canonical TESTS list and JUnit results."""
    num_runs = max(len(junit_runs), TEMPLATE_RUNS)
    rows = []

    for test in TESTS:
        row = list(test)
        for run_idx in range(num_runs):
            if run_idx < len(junit_runs):
                run_meta = junit_runs[run_idx]
                match = match_junit_result(test[0], run_meta["results"])
                if match:
                    row += [
                        match.get("date") or run_meta.get("date", ""),
                        match["status"],
                        match.get("duration", ""),
                        match.get("notes", ""),
                    ]
                else:
                    row += [run_meta.get("date", ""), "", "", ""]
            else:
                row += ["", "", "", ""]
        rows.append(row)

    return rows, num_runs


def build_summary_rows(data_rows: list[list], num_runs: int) -> list[list]:
    """Build summary rows counting PASS/FAIL/SKIP per run."""
    # Metadata columns = len(METADATA_HEADERS)
    meta_len = len(METADATA_HEADERS)
    run_width = 4  # date, status, duration, notes

    summaries = []
    for run_idx in range(num_runs):
        status_col = meta_len + run_idx * run_width + 1  # 0-based index
        counts = {"PASS": 0, "FAIL": 0, "SKIP": 0, "BLOCKED": 0, "": 0}
        for row in data_rows:
            val = row[status_col] if status_col < len(row) else ""
            counts[val if val in counts else ""] += 1

        run_label = f"Run {run_idx + 1}"
        row_pass = ["", "", f"PASS  ({run_label})", "", "", "", "", "", "", "", ""] + \
            [""] * (run_idx * run_width) + \
            ["", str(counts["PASS"]), "", ""]
        row_fail = ["", "", f"FAIL  ({run_label})", "", "", "", "", "", "", "", ""] + \
            [""] * (run_idx * run_width) + \
            ["", str(counts["FAIL"]), "", ""]
        row_skip = ["", "", f"SKIP  ({run_label})", "", "", "", "", "", "", "", ""] + \
            [""] * (run_idx * run_width) + \
            ["", str(counts["SKIP"]), "", ""]
        row_block = ["", "", f"BLOCKED ({run_label})", "", "", "", "", "", "", "", ""] + \
            [""] * (run_idx * run_width) + \
            ["", str(counts["BLOCKED"]), "", ""]
        row_total = ["", "", f"TOTAL  ({run_label})", "", "", "", "", "", "", "", ""] + \
            [""] * (run_idx * run_width) + \
            ["", str(len(data_rows)), "", ""]

    # Simpler flat summary at the bottom
    summary_rows = [[""] * (len(METADATA_HEADERS) + num_runs * run_width)]  # blank separator

    summary_header = ["", "SUMMARY", "", "", "", "", "", "", "", "", ""]
    for run_idx in range(num_runs):
        summary_header += [f"Run {run_idx + 1}", "", "", ""]
    summaries.append(summary_header)

    for label, key in [("PASS", "PASS"), ("FAIL", "FAIL"), ("SKIP", "SKIP"), ("BLOCKED", "BLOCKED"), ("TOTAL", None)]:
        row = ["", label, "", "", "", "", "", "", "", "", ""]
        for run_idx in range(num_runs):
            status_col = len(METADATA_HEADERS) + run_idx * run_width + 1
            if key is None:
                val = len(data_rows)
            else:
                val = sum(1 for r in data_rows if (r[status_col] if status_col < len(r) else "") == key)
            row += [str(val), "", "", ""]
        summaries.append(row)

    return [[""] * (len(METADATA_HEADERS) + num_runs * run_width)] + summaries


def write_csv(output_path: str, junit_runs: list[dict]):
    data_rows, num_runs = build_rows(junit_runs)
    summary_rows = build_summary_rows(data_rows, num_runs)

    # Build header row
    header = list(METADATA_HEADERS)
    for i in range(1, num_runs + 1):
        header += run_headers(i)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data_rows)
        writer.writerows(summary_rows)

    print(f"Wrote {len(data_rows)} test rows + {len(summary_rows)} summary rows to {output_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--junit", metavar="FILE", action="append", default=[],
                        help="JUnit XML file(s) to import (one per run, in chronological order)")
    parser.add_argument("--output", default="tracking/test-execution-tracking.csv",
                        help="Output CSV path (default: tracking/test-execution-tracking.csv)")
    args = parser.parse_args()

    junit_runs = []
    for path in args.junit:
        results = parse_junit(path)
        # Infer run date from first result with a date, else today
        dates = [r.get("date", "") for r in results.values() if r.get("date")]
        date = dates[0] if dates else datetime.now(timezone.utc).strftime("%Y-%m-%d")
        junit_runs.append({"date": date, "results": results})
        print(f"Loaded {len(results)} test results from {path} (date: {date})")

    write_csv(args.output, junit_runs)


if __name__ == "__main__":
    main()
