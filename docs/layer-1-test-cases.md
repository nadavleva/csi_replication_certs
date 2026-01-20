# Layer 1 Test Cases

---

**Total Tests: 90** (80 original + 10 VolumeGroupSource tests)

---

## Important Note: VolumeReplicationGroup (VRG) Testing Scope

**VolumeReplicationGroup is NOT part of the CSI Replication Add-on gRPC specification.**

The CSI Add-ons spec defines volume-level RPCs that accept a `ReplicationSource` parameter, which can be either:
- **VolumeSource**: Single volume replication
- **VolumeGroupSource**: Volume group replication

**Layer 1** tests the CSI driver's ability to handle volume groups through the existing RPCs with the `ReplicationSource.volumegroup` parameter.

**VolumeReplicationGroup (VRG)** is a **Layer 2 (Kubernetes orchestration)** concept that:
- Is implemented as a Kubernetes CRD by RamenDR/OCM
- Orchestrates multiple VolumeReplication resources
- Translates VRG operations to individual volume replication RPCs

**Testing Strategy**:
- ✅ **Layer 1**: Test RPCs with `VolumeGroupSource` to validate driver capability
- ✅ **Layer 2**: Test VRG CRD lifecycle and orchestration behavior

## 1.1 gRPC Replication Endpoint Tests (31 tests)

### 1.1.1 EnableVolumeReplication Tests (9 tests)

| **L1-E-008** | **Enable with VolumeGroupSource** | Enable replication using replication_source.volumegroup | All volumes in group enabled, single replication handle returned | **High** |
| **L1-E-009** | **Enable VolumeGroup with invalid group_id** | Use non-existent volume_group_id | Returns gRPC NotFound error | **High** |

### 1.1.2 DisableVolumeReplication Tests (5 tests)

| **L1-D-005** | **Disable with VolumeGroupSource** | Disable replication for volume group | All volumes in group disabled, replication stopped | **High** |

### 1.1.3 PromoteVolume Tests (6 tests)

| **L1-P-006** | **Promote VolumeGroup to primary** | Promote volume group using replication_source.volumegroup | All volumes in group promoted atomically | **High** |

### 1.1.4 DemoteVolume Tests (4 tests)

| **L1-DM-004** | **Demote VolumeGroup to secondary** | Demote volume group using replication_source.volumegroup | All volumes in group demoted atomically | **High** |

### 1.1.5 ResyncVolume Tests (5 tests)

| **L1-R-005** | **Resync VolumeGroup** | Resync volume group using replication_source.volumegroup | All volumes in group resynced, progress reported | **High** |

### 1.1.6 GetVolumeReplicationInfo Tests (4 tests)

| **L1-I-004** | **Get info for VolumeGroup** | Query replication info for volume group | Returns aggregated status for all volumes in group | **High** |

---

- ≥95% tests pass (86/90 minimum)

### Layer 2 VRG Resources (NOT part of CSI spec)
- [RamenDR VolumeReplicationGroup](https://github.com/RamenDR/ramen) - Kubernetes orchestration layer
- [OCM Placement](https://open-cluster-management.io/) - Multi-cluster orchestration

| **VolumeGroupSource Tests** | ❌ Not Covered | N/A | New tests - not yet implemented in Ceph |

4. **Complete gRPC Endpoint Testing** (31 tests including VolumeGroupSource)
   - Ceph only covers validation logic, not actual RPC calls
   - VolumeGroupSource tests are new additions
   - Requires E2E integration tests

- VolumeGroupSource tests are mandatory for full certification

- ❌ Missing: CRD lifecycle, capability discovery, performance testing, VolumeGroupSource

1. Proceed to **Layer 2**: OCP Platform Orchestration (VRG single-cluster tests)
   - Test VolumeReplicationGroup CRD lifecycle
   - Test VRG → VolumeReplication orchestration
   - Test VRG with multiple PVCs
