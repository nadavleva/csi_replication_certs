# Layer 1 CSI-Addons Spec — Test Cases Overview

High-level summary of VolumeReplication scenarios for the **CSI-Addons Spec track** of Layer 1 (same layer as core CSI E2E; separate until addon-spec merge). See [test-layers.md](test-layers.md).

**Runnable suite:** `make test-replication-e2e` in [kubernetes-csi-addons](https://github.com/nadavleva/kubernetes-csi-addons). What is implemented vs scaffolded: [layer-1-readme.md](layer-1-readme.md).

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
| PromoteVolume                   | **Complete Test Matrix**: Promote with/without force, split-brain, I/O workload, array down, already primary/secondary, planned vs unplanned failover intent (13 scenarios: L1-PROM-001 to L1-PROM-013) |
| DemoteVolume                    | **Complete Test Matrix**: Demote with/without force, I/O workload, array down, already secondary, peer connectivity (8 scenarios: L1-DEM-001 to L1-DEM-008) |
| ResyncVolume                    | After split-brain, autoResync, progress, called on primary |
| GetVolumeReplicationInfo        | Info for healthy/degraded replication, sync in progress |
| VRG API/Workflow                | VRG create/delete (both clusters), failover/failback, unavailable peer/S3, invalid PVC, cross-namespace |
| Capability Discovery            | Service support, mode support, handling non-capable driver |
| Error/Negative/Performance      | Driver timeout/crash/network partition, rapid operations, 100 VRs in single namespace |

---

## Planned vs Unplanned Failover Intent Flow

### Overview

A critical workflow distinction exists between **planned failover** (e.g., graceful relocate) and **unplanned failover** (e.g., DR after source cluster failure). Both result in a PromoteVolume call on the secondary, but the semantic intent and execution path differ significantly.

### Current Challenge

At the CSI driver level, both scenarios look identical:
- VolumeReplication patched to Primary on secondary
- PromoteVolume(force=false) called
- Driver cannot distinguish planned from unplanned from array state alone

However, array behavior differs:
- **Ceph**: Returns FailedPrecondition if primary has not been demoted → VRO retries with force=true
- **PowerStore**: Graceful sync and automatic re-protect (planned) vs immediate failover with manual re-protect (unplanned) → **needs explicit intent**

### Proposed Solution: Failover Intent Annotations

Ramen (the orchestrator) knows the semantic intent and can annotate VolumeReplication resources:

**Annotation Set for Planned Failover:**
```yaml
metadata:
  annotations:
    ramen.openshift.io/failover-intent: "planned"
    ramen.openshift.io/source-demoted: "true"  # DemoteVolume succeeded on primary
```

**Annotation Set for Unplanned Failover:**
```yaml
metadata:
  annotations:
    ramen.openshift.io/failover-intent: "unplanned"
    ramen.openshift.io/source-fenced: "true"  # Source is fenced/unreachable
```

### Test Scenario Flows

#### L1-PROM-009: Planned Failover - Graceful Promote

**Setup:**
1. Volume replication active with primary on Cluster A, secondary on Cluster B
2. Ramen decides planned failover (e.g., maintenance, scheduled migration)

**Flow:**
```
1. Ramen calls DemoteVolume on primary (Cluster A)
   - Primary array gracefully demotes volume
   - Awaits confirmation
2. DemoteVolume succeeds
3. Ramen patches VR on secondary with:
   - status.state = Primary
   - annotations: failover-intent=planned, source-demoted=true
4. VRO/CSI driver calls PromoteVolume(force=false)
5. Driver knows primary was demoted (from annotation)
6. Promote succeeds immediately
7. Replication reverses (new primary → old primary)
```

**Expected Outcome:**
- Graceful promotion with no force needed
- No data loss, consistent state
- Array re-protect initiated automatically (PowerStore) or manually (Ceph)

#### L1-PROM-010: Unplanned Failover with Intent Annotation

**Setup:**
1. Volume replication active with primary on Cluster A, secondary on Cluster B
2. Cluster A fails suddenly (network partition, etc.)

**Flow:**
```
1. Ramen detects primary cluster failure
2. Ramen initiates fencing (where applicable in MetroDR)
3. Ramen patches VR on secondary with:
   - status.state = Primary
   - annotations: failover-intent=unplanned, source-fenced=true
4. VRO/CSI driver calls PromoteVolume(force=false)
   - For Ceph-like drivers: Driver recognizes unplanned scenario,
     returns FailedPrecondition → VRO retries with force=true
   - For PowerStore-like drivers: Driver sees intent annotation,
     executes unplanned failover directly (no graceful sync)
```

**Expected Outcome (Array-dependent):**
- **Ceph**: FailedPrecondition → VRO escalates to force=true (L1-PROM-013)
- **PowerStore**: Unplanned failover executed immediately, manual re-protect required

#### L1-PROM-011: Source-Fenced Annotation

**Setup:**
1. Source cluster is fenced and unreachable
2. Secondary needs to know source is completely isolated

**Flow:**
```
1. Ramen ensures source cluster is fenced (network, storage, etc.)
2. Ramen patches VR: source-fenced=true
3. Driver uses this signal to:
   - Skip attempts to contact source
   - Execute unplanned failover safely
   - Avoid waiting for source response
```

**Expected Outcome:**
- Driver confirms source is unreachable before executing unplanned failover
- No retry loop waiting for fenced cluster
- Safe emergency promotion

#### L1-PROM-012 & L1-PROM-013: Array-Specific Behaviors

**PowerStore Planned Failover (L1-PROM-012):**
- Source initiates graceful sync (writes inflight data)
- Failover happens with array coordination
- Automatic re-protect (replication reverses)
- Zero data loss, minimal downtime

**PowerStore Unplanned Failover (L1-PROM-013):**
- No graceful sync (source unavailable)
- Immediate failover on target
- Manual re-protect required after source recovery
- Potential data loss if inflight data was not synced

### Implementation Considerations

1. **Annotation Naming**: Use `ramen.openshift.io/` prefix to namespace Ramen-specific metadata
2. **VRO Integration**: VRO should read intent annotation and:
   - For planned: Pass intent to driver via gRPC extension or driver-specific mechanism
   - For unplanned: Allow driver to make informed decisions
3. **Driver Behavior**:
   - Ceph: Continue with existing FailedPrecondition pattern (no annotation needed)
   - PowerStore: Use annotation to select graceful vs unplanned path
4. **Backward Compatibility**: Drivers without annotation support fall back to inferring intent from array state

### Regional vs Metro DR Considerations

- **MetroDR**: Fencing is applicable; use both failover-intent and source-fenced annotations
- **RegionalDR**: Fencing may not be performed; rely on failover-intent annotation alone

---



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