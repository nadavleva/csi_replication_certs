# Layer 1: CSI Replication Add-on - Detailed Test Matrix

## Overview

Layer 1 tests validate the CSI Replication Add-on implementation at two levels:
- **1. 1 Driver-Level Tests**: gRPC endpoint implementation and driver-side logic
- **1.2 Kubernetes CRD/Controller Tests**: VolumeReplication and VolumeReplicationClass lifecycle management

**Total Tests:  90** (80 original + 10 VolumeGroupSource tests)

---

## Important Note:  VolumeReplicationGroup (VRG) Testing Scope

**VolumeReplicationGroup is NOT part of the CSI Replication Add-on gRPC specification.**

The CSI Add-ons spec defines volume-level RPCs that accept a `ReplicationSource` parameter, which can be either:
- **VolumeSource**: Single volume replication
- **VolumeGroupSource**:  Volume group replication

**Layer 1** tests the CSI driver's ability to handle volume groups through the existing RPCs with the `ReplicationSource. volumegroup` parameter.

**VolumeReplicationGroup (VRG)** is a **Layer 2 (Kubernetes orchestration)** concept that: 
- Is implemented as a Kubernetes CRD by RamenDR/OCM
- Orchestrates multiple VolumeReplication resources
- Translates VRG operations to individual volume replication RPCs

**Testing Strategy**:
- ✅ **Layer 1**:  Test RPCs with `VolumeGroupSource` to validate driver capability
- ✅ **Layer 2**: Test VRG CRD lifecycle and orchestration behavior

---

## 1.1 gRPC Replication Endpoint Tests (31 tests)

### 1.1.1 EnableVolumeReplication Tests (9 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-E-001 | Enable with snapshot mode | Enable replication with mirroringMode=snapshot | VR CR created, status. replicationHandle populated | High |
| L1-E-002 | Enable with journal mode | Enable replication with mirroringMode=journal | VR CR created, continuous replication active | High |
| L1-E-003 | Enable with scheduling interval | Parameters:  schedulingInterval="5m" | VR status shows nextSyncTime within 5 minutes | High |
| L1-E-004 | Enable with start time | schedulingStartTime="14: 00:00-05:00" | First sync occurs at specified time | Medium |
| L1-E-005 | Enable with invalid interval | schedulingInterval="5x" (invalid format) | Returns gRPC InvalidArgument error | High |
| L1-E-006 | Enable already enabled volume | Call EnableVolumeReplication twice | Idempotent:  returns success, no duplicate VR | Medium |
| L1-E-007 | Enable with missing secret | Reference non-existent replication secret | Returns gRPC FailedPrecondition error | High |
| **L1-E-008** | **Enable with VolumeGroupSource** | Enable replication using replication_source.volumegroup | All volumes in group enabled, single replication handle returned | **High** |
| **L1-E-009** | **Enable VolumeGroup with invalid group_id** | Use non-existent volume_group_id | Returns gRPC NotFound error | **High** |

### 1.1.2 DisableVolumeReplication Tests (5 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-D-001 | Disable active replication | Disable volume in Primary state | Replication relationship removed, volume writable | High |
| L1-D-002 | Disable secondary volume | Disable volume in Secondary state | Replication stopped, volume remains read-only | High |
| L1-D-003 | Disable with force=true | Parameters: force="true" | Immediate disable, ignores pending operations | Medium |
| L1-D-004 | Disable non-replicated volume | Call on volume without replication | Returns success (idempotent) | Low |
| **L1-D-005** | **Disable with VolumeGroupSource** | Disable replication for volume group | All volumes in group disabled, replication stopped | **High** |

### 1.1.3 PromoteVolume Tests (6 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-P-001 | Promote secondary to primary | Promote Secondary → Primary | VR status. state = Primary, volume writable | High |
| L1-P-002 | Promote with force=false | Safe promotion (data loss check) | Fails if split-brain detected | High |
| L1-P-003 | Promote with force=true | Force promotion (emergency failover) | Succeeds even with potential data loss | High |
| L1-P-004 | Promote already primary volume | Promote volume already in Primary state | Idempotent: returns success immediately | Medium |
| L1-P-005 | Promote during ongoing sync | Promote while sync in progress | Waits for sync or times out with retriable error | Medium |
| **L1-P-006** | **Promote VolumeGroup to primary** | Promote volume group using replication_source.volumegroup | All volumes in group promoted atomically | **High** |

### 1.1.4 DemoteVolume Tests (4 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-DM-001 | Demote primary to secondary | Demote Primary → Secondary | VR status.state = Secondary, volume read-only | High |
| L1-DM-002 | Demote with active I/O | Demote while workload writing | I/O flushed, volume cleanly demoted | High |
| L1-DM-003 | Demote already secondary volume | Demote Secondary state volume | Idempotent: returns success | Low |
| **L1-DM-004** | **Demote VolumeGroup to secondary** | Demote volume group using replication_source. volumegroup | All volumes in group demoted atomically | **High** |

### 1.1.5 ResyncVolume Tests (5 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-R-001 | Resync after split-brain | Resync Secondary after network partition | Full resync completes, data consistent | High |
| L1-R-002 | Resync with autoResync=true | Parameters: autoResync="true" | Automatic resync on replication re-establishment | High |
| L1-R-003 | Resync progress reporting | Monitor resync of 100GB volume | Status reports bytesRemaining, estimatedTime | Medium |
| L1-R-004 | Resync on primary volume | Call ResyncVolume on Primary state volume | Returns gRPC FailedPrecondition error | Medium |
| **L1-R-005** | **Resync VolumeGroup** | Resync volume group using replication_source.volumegroup | All volumes in group resynced, progress reported | **High** |

### 1.1.6 GetVolumeReplicationInfo Tests (4 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-I-001 | Get info for healthy replication | Query Primary volume info | Returns lastSyncTime, replicationStatus="healthy" | High |
| L1-I-002 | Get info during sync | Query while sync in progress | Returns bytesTransferred, syncInProgress=true | Medium |
| L1-I-003 | Get info for degraded replication | Query after peer cluster failure | Returns replicationStatus="degraded", error details | High |
| **L1-I-004** | **Get info for VolumeGroup** | Query replication info for volume group | Returns aggregated status for all volumes in group | **High** |

---

## 1.2 VolumeReplication CRD Lifecycle Tests (18 tests)

### 1.2.1 VR Creation Tests (5 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-VR-001 | Create VR for PVC | VR referencing existing PVC | VR accepted, controller calls EnableVolumeReplication | High |
| L1-VR-002 | Create VR with invalid PVC | VR referencing non-existent PVC | VR condition Degraded=True, error message | High |
| L1-VR-003 | Create VR without VRC | No VolumeReplicationClass specified | VR rejected by webhook (missing required field) | High |
| L1-VR-004 | Create VR with invalid VRC | VRC doesn't match driver provisioner | VR condition Degraded=True, "VRC not found" | High |
| L1-VR-005 | Create duplicate VR for same PVC | Two VRs reference same PVC | Second VR rejected (conflict) | Medium |

### 1.2.2 VR State Transition Tests (8 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-VR-006 | Primary → Secondary transition | Update spec.replicationState | Driver DemoteVolume called, status.state=Secondary | High |
| L1-VR-007 | Secondary → Primary transition | Update spec.replicationState | Driver PromoteVolume called, status.state=Primary | High |
| L1-VR-008 | Primary → Primary (no-op) | Update to same state | No driver calls, status unchanged | Medium |
| L1-VR-009 | State transition with autoResync | spec.autoResync=true on Secondary→Primary | Driver ResyncVolume called before PromoteVolume | High |
| L1-VR-010 | State transition during sync | Change state while sync active | Waits for sync completion or timeout | Medium |
| L1-VR-011 | Rapid state transitions | Primary→Secondary→Primary in <30s | Each transition completes, no race conditions | Medium |
| L1-VR-012 | State transition error recovery | Driver returns transient error | VR retries with exponential backoff | High |
| L1-VR-013 | State transition timeout | Driver hangs for >5min | VR reports timeout, sets Degraded condition | Medium |

### 1.2.3 VR Status Reporting Tests (5 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-VR-014 | Status reflects driver state | Poll VR status every 30s | status.state matches GetVolumeReplicationInfo | High |
| L1-VR-015 | Conditions on successful ops | Complete state transition | Conditions:  Completed=True, Degraded=False | High |
| L1-VR-016 | Conditions on driver errors | Driver returns FailedPrecondition | Conditions: Completed=False, Degraded=True, Resyncing=True | High |
| L1-VR-017 | Last sync time reporting | Check status. lastSyncTime | Updated after each successful sync | Medium |
| L1-VR-018 | Replication handle persistence | VR status.replicationHandle | Persisted across controller restarts | Medium |

---

## 1.3 VolumeReplicationClass Tests (12 tests)

### 1.3.1 VRC Parameter Propagation Tests (6 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-VRC-001 | Parameters passed to driver | VRC with schedulingInterval="10m" | Driver receives parameter in EnableVolumeReplication | High |
| L1-VRC-002 | Secret reference resolution | VRC with replication-secret-name | Driver receives secret data (not reference) | High |
| L1-VRC-003 | Multiple VRCs for same driver | 2 VRCs:  snapshot (5m) and journal | VRs use correct VRC parameters | Medium |
| L1-VRC-004 | VRC parameter validation | Invalid parameter (e.g., interval="foo") | VR creation fails with validation error | High |
| L1-VRC-005 | VRC provisioner mismatch | VRC provisioner != PVC CSI driver | VR rejected, error:  "provisioner mismatch" | High |
| L1-VRC-006 | VRC immutability | Update VRC parameters after VR creation | Existing VRs unaffected (parameters immutable) | Medium |

### 1.3.2 VRC Multi-Tenancy Tests (3 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-VRC-007 | Namespace-scoped secrets | VRC references secret in different namespace | VR fails if cross-namespace access denied | Medium |
| L1-VRC-008 | RBAC for VRC usage | User without VRC get permission | Cannot create VR referencing VRC | Medium |
| L1-VRC-009 | VRC deletion protection | Delete VRC with active VRs | Deletion blocked (finalizer) until VRs deleted | High |

### 1.3.3 VRC Replication Mode Tests (3 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-VRC-010 | Snapshot-based replication | mirroringMode=snapshot | Periodic snapshots created, incremental transfer | High |
| L1-VRC-011 | Journal-based replication | mirroringMode=journal | Continuous WAL/journal replication, RPO < 10s | High |
| L1-VRC-012 | Async vs Sync replication | Test both modes with same driver | Async: eventual consistency; Sync: zero RPO | Medium |

---

## 1.4 Driver Capability Discovery Tests (8 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-CAP-001 | Advertise VOLUME_REPLICATION | GetPluginCapabilities response | Contains VOLUME_REPLICATION service capability | High |
| L1-CAP-002 | Advertise replication modes | Driver metadata (annotations) | Lists supported modes (snapshot/journal/sync) | High |
| L1-CAP-003 | Skip tests for non-capable driver | Driver without replication capability | Framework skips replication tests gracefully | Medium |
| L1-CAP-004 | Capability change detection | Driver upgrade adds replication | Test suite auto-discovers new capability | Low |
| L1-CAP-005 | Controller vs Node capabilities | Replication is controller-only | Node plugin doesn't advertise replication | Medium |
| L1-CAP-006 | CSI spec version compatibility | Driver CSI version 1.5+ | Replication requires CSI 1.5 minimum | Medium |
| L1-CAP-007 | Feature gate enforcement | Replication feature gate disabled | VR CRD/controller not installed, VR creation fails | Medium |
| L1-CAP-008 | Negative test:  missing capability | Create VR for driver without capability | VR Degraded=True, message:  "driver doesn't support replication" | High |

---

## 1.5 Error Handling and Negative Tests (15 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-ERR-001 | Driver timeout on Enable | Driver takes >5min to enable | VR retries, sets timeout condition | High |
| L1-ERR-002 | Driver crash during operation | Kill driver pod mid-operation | Operation retried after driver restart | High |
| L1-ERR-003 | Invalid volume ID | EnableVolumeReplication with fake ID | Returns gRPC NotFound error | High |
| L1-ERR-004 | Network partition during RPC | Disconnect network during PromoteVolume | Retries after network restored | High |
| L1-ERR-005 | Driver returns Unavailable | Temporary backend storage failure | VR retries with backoff, reports transient error | High |
| L1-ERR-006 | Secret rotation during replication | Update replication secret credentials | Driver picks up new credentials, replication continues | Medium |
| L1-ERR-007 | PVC deletion with active VR | Delete PVC referenced by VR | VR blocks PVC deletion (finalizer) | High |
| L1-ERR-008 | VR deletion during sync | Delete VR while sync in progress | VR finalizer waits for sync abort | Medium |
| L1-ERR-009 | Driver version downgrade | Downgrade driver (removing replication) | Existing VRs report capability lost error | Medium |
| L1-ERR-010 | Concurrent state changes | Two controllers update VR state | Optimistic locking prevents conflicts | High |
| L1-ERR-011 | Invalid gRPC response | Driver returns malformed protobuf | VR logs error, reports Degraded condition | Medium |
| L1-ERR-012 | Storage backend quota exceeded | Backend rejects new replication pair | Driver returns ResourceExhausted, VR reports quota error | Medium |
| L1-ERR-013 | Split-brain scenario | Both volumes promoted to Primary | ResyncVolume required, data loss warning | High |
| L1-ERR-014 | Replication lag exceeds threshold | Secondary >1hr behind Primary | VR reports Degraded, lastSyncTime shows lag | Medium |
| L1-ERR-015 | Driver panic recovery | Driver panics during DemoteVolume | Controller detects failure, retries operation | High |

---

## 1.6 Performance and Scale Tests (6 tests)

| Test ID | Test Name | Description | Pass Criteria | Priority |
|---------|-----------|-------------|---------------|----------|
| L1-PERF-001 | 100 VRs in single namespace | Create 100 VRs simultaneously | All reach Completed state within 10 minutes | Medium |
| L1-PERF-002 | VR state transition latency | Measure Primary→Secondary time | <30s for 10GB volume, <5min for 1TB volume | Medium |
| L1-PERF-003 | Sync throughput | Measure replication bandwidth | Achieves ≥50% of backend network bandwidth | Medium |
| L1-PERF-004 | Controller reconcile efficiency | Monitor controller CPU/memory | <100MB memory per 100 VRs, <10% CPU | Low |
| L1-PERF-005 | Rapid create/delete cycles | Create+delete VR 50 times | No resource leaks, consistent performance | Medium |
| L1-PERF-006 | Large volume initial sync | Replicate 10TB volume | Completes within 24 hours at 1Gbps | Low |

---

## Test Execution Prerequisites

### Environment Setup
1. Kubernetes cluster version 1.23+
2. CSI driver with replication capability installed
3. CSI-addons controller deployed
4. VolumeReplication and VolumeReplicationClass CRDs installed
5. Storage backend with replication support configured
6. Two peer clusters for multi-cluster tests (Layer 2+)

### Required Permissions
- Cluster admin access for CRD installation
- Namespace admin for test execution
- Storage class creation permissions
- Secret management permissions

### Test Tools
- kubectl with cluster access
- CSI driver CLI tools (driver-specific)
- gRPC testing tools (grpcurl, ghz)
- Kubernetes test framework (e.g., Ginkgo)

---

## Success Criteria

### Per-Test Criteria
- All assertions pass without errors
- Expected gRPC responses received
- CRD status conditions match expected states
- No resource leaks after test completion
- Logs contain expected messages without errors

### Overall Layer 1 Pass Criteria
- ≥95% tests pass (86/90 minimum)
- All High priority tests pass (100%)
- All gRPC endpoints functional
- VR/VRC lifecycle working end-to-end
- No critical security issues discovered

---

## Test Execution Workflow

1. **Pre-flight Checks**:  Verify prerequisites and environment
2. **Capability Discovery**: Confirm driver supports replication
3. **gRPC Endpoint Tests** (1. 1): Test driver-level implementation
4. **CRD Lifecycle Tests** (1.2-1.3): Test Kubernetes integration
5. **Error Handling Tests** (1.5): Test failure scenarios
6. **Performance Tests** (1.6): Test scale and performance
7. **Cleanup**: Remove test resources and validate cleanup

---

## References

### Official Specifications
- [CSI Add-ons Specification - Replication](https://github.com/csi-addons/spec/tree/main/replication)
  - **ReplicationSource message definition**:  Defines VolumeSource and VolumeGroupSource
- [CSI Add-ons Kubernetes Integration](https://github.com/csi-addons/kubernetes-csi-addons)
- [Volume Replication Design Doc](https://github.com/csi-addons/kubernetes-csi-addons/blob/main/docs/design/volumereplication.md)
- [CSI Specification v1.5+](https://github.com/container-storage-interface/spec)

### Kubernetes Resources
- [VolumeReplication CRD Definition](https://github.com/csi-addons/kubernetes-csi-addons/blob/main/config/crd/bases/replication.storage.openshift.io_volumereplications.yaml)
- [VolumeReplicationClass CRD Definition](https://github.com/csi-addons/kubernetes-csi-addons/blob/main/config/crd/bases/replication.storage. openshift.io_volumereplicationclasses.yaml)
- [VolumeReplication Controller](https://github.com/csi-addons/kubernetes-csi-addons/blob/main/internal/controller/replication.storage/volumereplication_controller.go)

### Layer 2 VRG Resources (NOT part of CSI spec)
- [RamenDR VolumeReplicationGroup](https://github.com/RamenDR/ramen) - Kubernetes orchestration layer
- [OCM Placement](https://open-cluster-management.io/) - Multi-cluster orchestration

### Related Testing Resources
- [KubeVirt Storage Checkup](https://github.com/kiagnose/kubevirt-storage-checkup)
- [Kubernetes E2E Testing Guide](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-testing/e2e-tests.md)

### Reference Implementations
- [Ceph CSI Driver Reference Implementation](ceph-csi-reference. md) - Detailed mapping of Ceph CSI test coverage

---

## Next Steps

After completing Layer 1 tests: 
1. Proceed to **Layer 2**:  OCP Platform Orchestration (VRG single-cluster tests)
   - Test VolumeReplicationGroup CRD lifecycle
   - Test VRG → VolumeReplication orchestration
   - Test VRG with multiple PVCs
2. Proceed to **Layer 3**: Multi-Cluster DR and CNV (RamenDR, KubeVirt integration)
3. Execute **Cross-Layer Integration Tests**

For detailed Layer 2 and Layer 3 specifications, see:
- [Layer 2 README](layer-2-readme.md)
- [Layer 3 README](layer-3-readme.md)
- [Test Plan Matrix](test-plan-matrix.md)