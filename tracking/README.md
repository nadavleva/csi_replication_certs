# Test Execution Tracking

This directory contains the CSI Replication end-to-end test execution tracking spreadsheet.

## Files

| File | Description |
|------|-------------|
| `test-execution-tracking.csv` | Main tracking sheet — all 49 test specs with metadata and execution run columns |

## Sheet Layout

### Columns

| Column group | Columns | Description |
|---|---|---|
| **Test metadata** | Test ID, Category, Description, Node Role, Peer State, Array State, Params, Test Type, Cluster Mode, Expected Duration, Implementation Status | Static per test spec from the [full test plan](https://github.com/nadavleva/kubernetes-csi-addons/blob/csivgrtests-only/docs/testing/replication-e2e-suite.md#full-test-plan) |
| **Run N** (repeat as needed) | `Run N - Execution Date`, `Run N - Status`, `Run N - Duration`, `Run N - Notes` | One group per test run; Status is **PASS / FAIL / SKIP / BLOCKED** |

### Summary rows

At the bottom of the sheet there is a summary block that counts PASS / FAIL / SKIP / BLOCKED / TOTAL for each run column.

### Implementation Status values

| Value | Meaning |
|---|---|
| `Implemented` | Spec is fully implemented and runs in the suite |
| `Scaffold` | Spec exists as a stub (ResyncVolumeReplication) — skipped at runtime |
| `Blocked (#N)` | Spec blocked by an open issue; skipped with a log message |

## Importing to Google Sheets

1. Open [Google Sheets](https://sheets.google.com) and create a new spreadsheet.
2. **File → Import → Upload** → select `test-execution-tracking.csv`.
3. Choose **Replace spreadsheet** and set separator to **Comma**.
4. Apply conditional formatting on Status columns (columns L, P, T, …):
   - `PASS` → green fill
   - `FAIL` → red fill
   - `SKIP` → yellow fill
   - `BLOCKED` → orange fill

## Populating from JUnit XML

After a test run, the `scripts/generate-tracking-csv.py` script can read the JUnit XML produced by Ginkgo and populate the tracking sheet automatically.

### Generate blank template

```bash
python3 scripts/generate-tracking-csv.py
# writes to tracking/test-execution-tracking.csv with 3 blank run columns
```

### Import one or more JUnit runs

```bash
# Single run
python3 scripts/generate-tracking-csv.py \
  --junit Logs/junit_replication-e2e_2026-04-10.xml \
  --output tracking/test-execution-tracking.csv

# Two runs (Run 1 and Run 2)
python3 scripts/generate-tracking-csv.py \
  --junit Logs/junit_run1.xml \
  --junit Logs/junit_run2.xml \
  --output tracking/test-execution-tracking.csv
```

The script:
- Matches each JUnit `<testcase>` to a test spec by looking for the Test ID (e.g. `L1-E-001`) in the test case name.
- Reads the run date from the `<testsuite timestamp>` attribute.
- Sets **PASS / FAIL / SKIP** based on `<failure>`, `<error>`, or `<skipped>` child elements.
- Copies the failure / skip message into the **Notes** column.
- Writes one **Run N** group of columns per `--junit` argument.
- Appends a summary block at the bottom counting PASS / FAIL / SKIP per run.

### Ginkgo JUnit output

Ginkgo v2 produces JUnit XML when run with `--junit-report`:

```bash
REPORTS_DIR=Logs make test-replication-e2e
# or
ginkgo --junit-report=Logs/junit.xml ./test/e2e/replication/...
```

The `REPORTS_DIR` environment variable used by the suite maps to the `--output-dir` / `--junit-report` Ginkgo flags (see `suite_test.go`).
