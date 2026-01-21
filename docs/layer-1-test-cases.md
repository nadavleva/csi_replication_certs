# Layer-1 CSI Replication Add-on Test Cases Overview

This file provides a high-level summary of all Layer-1 test cases for CSI Replication Add-on driver certification, following the guidance of Andrew and project consensus.

- All endpoint tests for Enable/Disable/Promote/Demote/Resync/GetInfo are enumerated.
- All permutations of cluster/peer/array states and `force` parameter are considered.
- Includes user/workflow-level VRG API flows relevant for Layer-1 conformance.
- **CRD lifecycle/controller/unit/integration tests are no longer included** (these belong in Layer-2 or upstream).

For a fully detailed and explicit enumeration of every test scenario—including input steps, expected outcomes, error codes, automation links—**see [`docs/layer-1-test-details.md`](docs/layer-1-test-details.md)**.

---

## Categories & Example Scenarios

| Category                        | Coverage (Example)                                      |
|----------------------------------|--------------------------------------------------------|
| EnableVolumeReplication         | Mode=snapshot, mode=journal, invalid interval, idempotent, peer down |
| DisableVolumeReplication        | All states of primary/secondary, peer up/down, force true/false, array up/down, previously disabled |
| Promote/DemoteVolume            | Promote with/without force, split-brain, I/O workload, array down, already primary/secondary |
| ResyncVolume                    | After split-brain, autoResync, progress, called on primary |
| GetVolumeReplicationInfo        | Info for healthy/degraded replication, sync in progress |
| VRG API/Workflow                | VRG create/delete (both clusters), failover/failback, unavailable peer/S3, invalid PVC, cross-namespace |
| Capability Discovery            | Service support, mode support, handling non-capable driver |
| Error/Negative/Performance      | Driver timeout/crash/network partition, rapid operations, 100 VRs in single namespace |

---

## Example Test Matrix Table

| Test ID          | API                    | Scenario                                                  | Role/State         | Params       | Test Type     | Pass Criteria/Outcome                        |
|------------------|------------------------|-----------------------------------------------------------|--------------------|--------------|---------------|-----------------------------------------------|
| L1-E-001         | EnableVolumeReplication| Enable replication, mode=snapshot, healthy                | Primary/secondary  | snapshot     | functional    | VR created, replicationHandle set             |
| L1-DIS-001       | DisableVolumeReplication| Disable, primary, peer up, force=false                   | Primary            | force=false  | functional    | Replication removed, volume RW                |
| L1-PROM-002      | PromoteVolume          | Promote secondary, peer down, force=false                 | Secondary          | force=false  | negative      | Error: split-brain guarded                    |
| L1-VRG-001       | VRG create             | VRG for 1 PVC, both healthy                              | Primary/secondary  | -            | functional    | VR, data, status healthy                      |
| ...              | ...                    | ...                                                       | ...                | ...          | ...           | ...                                           |

---

**This is just a summary! See [`layer-1-test-details`](layer-1-test-details.md) for the explicit, expanded tests list.**

---