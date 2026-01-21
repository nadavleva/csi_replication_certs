# Layer-1 CSI Replication Add-on Test Cases Overview

This file provides a high-level summary of all Layer-1 test cases for CSI Replication Add-on driver certification.

- All endpoint tests for Enable/Disable/Promote/Demote/Resync/GetInfo are enumerated.
- All permutations of cluster/peer/array states and `force` parameter are considered.
- Includes user/workflow-level VRG API flows relevant for Layer-1 conformance.
- **CRD lifecycle/controller/unit/integration tests are no longer included** (these belong in Layer-2 or upstream).

For a fully detailed and explicit enumeration of every test scenario—including input steps, expected outcomes, error codes, automation links—**see [`docs/layer-1-vr-tests.md`](docs/layer-1-vr-tests.md)**.

---

## Categories & Example Scenarios

| Category                        | Coverage (Example)                                      |
|----------------------------------|--------------------------------------------------------|
| EnableVolumeReplication         | Mode=snapshot, mode=journal, invalid interval, idempotent, peer down (6 scenarios: L1-E-001 to L1-E-006) |
| DisableVolumeReplication        | **Complete Test Matrix**: All states of primary/secondary, peer up/down, force true/false, array up/down, previously disabled (16 scenarios: L1-DIS-001 to L1-DIS-016) |
| PromoteVolume                   | **Complete Test Matrix**: Promote with/without force, split-brain, I/O workload, array down, already primary/secondary (8 scenarios: L1-PROM-001 to L1-PROM-008) |
| DemoteVolume                    | **Complete Test Matrix**: Demote with/without force, I/O workload, array down, already secondary, peer connectivity (8 scenarios: L1-DEM-001 to L1-DEM-008) |
| ResyncVolume                    | After split-brain, autoResync, progress, called on primary |
| GetVolumeReplicationInfo        | Info for healthy/degraded replication, sync in progress |
| VRG API/Workflow                | VRG create/delete (both clusters), failover/failback, unavailable peer/S3, invalid PVC, cross-namespace |
| Capability Discovery            | Service support, mode support, handling non-capable driver |
| Error/Negative/Performance      | Driver timeout/crash/network partition, rapid operations, 100 VRs in single namespace |

---

## VRG (VolumeReplicationGroup) API Operations

| Category                        | Coverage (Example)                                      |
|----------------------------------|--------------------------------------------------------|
| VRG Create/Delete               | Single PVC, multiple PVCs, cross-namespace, invalid selectors |
| VRG Disable Operations          | **Complete Test Matrix**: Disable on primary/secondary, peer up/down, force true/false, array up/down (16 scenarios: L1-VRG-DIS-001 to L1-VRG-DIS-016) |
| VRG Failover/Failback           | Emergency failover, graceful failback, split-brain scenarios |
| VRG Status/Monitoring           | Health checks, sync status, error reporting |
| VRG S3 Integration              | S3 metadata handling, S3 unavailable scenarios (optional for advanced DR) |

---

**For detailed test specifications and matrices:**
- **CSI gRPC endpoints**: See [layer-1-vr-tests.md](layer-1-vr-tests.md) for explicit CSI API test enumeration
- **VRG API operations**: See [layer-1-vrg-tests.md](layer-1-vrg-tests.md) for comprehensive VRG test scenarios

---