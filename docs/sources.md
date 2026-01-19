# Reference Sources and Implementations

## Overview
This document provides detailed references to the key open-source projects that serve as the foundation and "gold standard" for CSI Replication certification. These projects demonstrate best practices and provide reference implementations for volume replication features.

---

## 1. RamenDR: Multi-Cluster Disaster Recovery

### Project Information
- **Repository:** [RamenDR/ramen](https://github.com/RamenDR/ramen)
- **Purpose:** Multi-cluster disaster recovery orchestration for Kubernetes/OpenShift
- **License:** Apache 2.0

### Key Components

#### VolumeReplicationGroup (VRG)
**API Reference:** `api/v1alpha1/volumereplicationgroup_types.go`

The VRG is the core custom resource for managing volume replication groups:

```yaml
apiVersion: ramendr.openshift.io/v1alpha1
kind: VolumeReplicationGroup
metadata:
  name: my-app-vrg
  namespace: my-app-namespace
spec:
  replicationState: "primary"  # or "secondary"
  pvcSelector:
    matchLabels:
      app: my-application
  s3Profiles:
    - s3-profile-east
    - s3-profile-west
  async:
    schedulingInterval: "10m"
  kubeObjectProtection:
    captureInterval: 1m
```

**Key Features:**
- PVC selection and grouping for coordinated replication
- State management (Primary ↔ Secondary transitions)
- S3-based PV metadata preservation
- Application resource protection (Recipes)
- VolSync integration for file-based replication

#### Controller Architecture
**Reference:** `internal/controller/volumereplicationgroup_controller.go`

The VRG controller orchestrates:
1. **PVC Discovery**: Finds PVCs matching the selector
2. **VolumeReplication Management**: Creates/manages VR CRs for each PVC
3. **State Transitions**: Handles primary→secondary and secondary→primary promotion
4. **Metadata Management**: Stores PV info in S3 for cross-cluster recovery
5. **Application Protection**: Coordinates with Velero for app resource backup/restore

### Replication Scenarios to Test

#### 1. VRG State Transitions
```go
// Test: Primary to Secondary Transition
1. Create VRG with replicationState: primary
2. Verify VolumeReplication CRs created for each PVC
3. Verify replication is active
4. Update VRG to replicationState: secondary
5. Verify replication direction changed
6. Verify data accessible in secondary mode
```

#### 2. Multi-Cluster Fencing
```go
// Test: Cluster Failure and Fence
1. Deploy app on Cluster A with VRG (primary)
2. Set up replication to Cluster B (VRG secondary)
3. Simulate Cluster A failure
4. Promote Cluster B VRG to primary
5. Verify app can access data on Cluster B
6. Verify Cluster A VRG is fenced (cannot become primary)
```

#### 3. VolSync Integration
```go
// Test: VolSync-based replication
1. Create VRG with VolSync replication method
2. Verify ReplicationSource created on primary
3. Verify ReplicationDestination created on secondary
4. Validate data sync occurs
5. Perform failover
6. Verify data integrity on secondary cluster
```

### Key Test Scenarios from RamenDR

**Test File:** `internal/controller/volumereplicationgroup_controller_test.go`

1. **VRG Creation and PVC Discovery**
   - VRG correctly identifies PVCs matching label selector
   - VolumeReplication CRs created for each PVC
   - Status updated with protected PVCs list

2. **Primary to Secondary Transition**
   - Replication state changes propagated to VR CRs
   - Application pods rescheduled appropriately
   - Data remains accessible after transition

3. **Secondary to Primary Promotion**
   - VRG promoted to primary on target cluster
   - Previous primary demoted
   - Fencing prevents split-brain scenarios

4. **PV Metadata Management**
   - PV information uploaded to S3
   - PV information retrieved from S3 on peer cluster
   - PVC binding succeeds using stored PV data

5. **Recipe-based Application Protection**
   - Kubernetes resources captured per Recipe workflow
   - Capture/Recover hooks executed in correct order
   - Application restored with proper resource ordering

---

## 2. Ceph CSI: Gold Standard Implementation

### Project Information
- **Repository:** [ceph/ceph-csi](https://github.com/ceph/ceph-csi)
- **Purpose:** Reference CSI driver implementation for Ceph RBD and CephFS
- **License:** Apache 2.0

### Why Ceph CSI is the Gold Standard

1. **Complete CSI Replication Support**
   - Implements VolumeReplication extensions
   - Supports both RBD (block) and CephFS (file) replication
   - Demonstrates proper gRPC call sequences

2. **Mature E2E Test Suite**
   - **Location:** `e2e/` directory
   - Comprehensive test coverage
   - Real-world failure scenarios

3. **Production-Ready**
   - Used in OpenShift Data Foundation
   - Battle-tested in enterprise environments
   - Active community and Red Hat support

### Key Replication Features

#### RBD Mirroring
**Reference:** E2E tests in `e2e/rbd_helper.go`

```bash
# RBD mirror modes
- snapshot-based: Periodic RBD snapshots
- journal-based: Continuous journal-based replication

# Key operations tested:
- Enable mirroring on image
- Promote/demote operations
- Force promotion (simulating primary failure)
- Resync after split-brain
```

#### VolumeReplication CRD Integration
```yaml
apiVersion: replication.storage.openshift.io/v1alpha1
kind: VolumeReplication
metadata:
  name: my-pvc-replication
spec:
  volumeReplicationClass: rbd-mirror-vrc
  replicationState: primary  # or secondary
  dataSource:
    apiGroup: ""
    kind: PersistentVolumeClaim
    name: my-pvc
```

### E2E Test Categories

**Test File:** `e2e/rbd.go`, `e2e/cephfs.go`

1. **Basic Replication Tests**
   - Create PVC with replication enabled
   - Verify VolumeReplication CR created
   - Validate replication status

2. **Failover Tests**
   - Primary cluster failure simulation
   - Promotion of secondary to primary
   - Data accessibility verification

3. **Resync Tests**
   - Image out-of-sync detection
   - Resync initiation
   - Sync completion validation

4. **Snapshot and Clone Tests**
   - Snapshot-based replication
   - Clone from replicated volume
   - Consistency verification

5. **Volume Group Replication**
   - **Reference:** `e2e/volumegroupsnapshot.go`
   - Coordinated snapshots of multiple volumes
   - Group consistency validation

### gRPC Call Sequences (Gold Standard)

#### Volume Provisioning with Replication
```
1. CreateVolume (Controller)
   → StorageClass parameters include replication config
   → Volume created on primary site
   
2. EnableVolumeReplication (Extension)
   → Replication enabled on volume
   → Secondary volume created on target site
   
3. ControllerPublishVolume
   → Volume attached to node
   
4. NodeStageVolume
   → Volume staged for use
   
5. NodePublishVolume
   → Volume mounted to pod
```

#### Promote (Secondary → Primary)
```
1. PromoteVolume (Extension)
   → Mark volume as primary
   → Stop receiving replication updates
   → Allow write access
   
2. Controller monitors replication state
   → Verify promotion completed
   → Update VolumeReplication status
```

#### Demote (Primary → Secondary)
```
1. DemoteVolume (Extension)
   → Ensure volume is unmounted
   → Mark volume as secondary
   → Begin accepting replication updates
   → Deny write access
```

---

## 3. CNV (KubeVirt) Tests: VM-Level Validation

### Project Information
- **Repository:** [kiagnose/kubevirt-storage-checkup](https://github.com/kiagnose/kubevirt-storage-checkup)
- **Purpose:** Validate storage for virtualized workloads
- **License:** Apache 2.0

### Key Test Scenarios

#### 1. VM Boot from Replicated Volume
```go
Test Scenario:
1. Create replicated PVC
2. Create VirtualMachine using replicated PVC
3. Start VM
4. Verify VM boots successfully
5. Write data to VM disk
6. Shutdown VM gracefully
7. Perform failover to secondary cluster
8. Boot VM from replicated volume
9. Verify data integrity
```

#### 2. Live Migration with Replication
```go
Test Scenario:
1. Start VM with replicated storage
2. Begin live migration to different node
3. Monitor replication during migration
4. Verify replication remains healthy
5. Complete migration
6. Validate data consistency
```

#### 3. Snapshot Consistency
```go
Test Scenario:
1. Run application inside VM (e.g., database)
2. Trigger application-consistent snapshot
   - Execute freeze hook
   - Create snapshot
   - Execute thaw hook
3. Replicate snapshot to secondary site
4. Restore VM from snapshot on secondary
5. Verify application data consistency
```

### Integration with VRG

CNV tests validate that VRG properly handles VM workloads:

```yaml
apiVersion: ramendr.openshift.io/v1alpha1
kind: VolumeReplicationGroup
metadata:
  name: vm-workload-vrg
spec:
  pvcSelector:
    matchLabels:
      vm.kubevirt.io/name: my-database-vm
  kubeObjectProtection:
    recipeRef:
      name: vm-consistency-recipe
      captureWorkflowName: vm-capture
      recoverWorkflowName: vm-recover
```

**Recipe for VM Workloads:**
```yaml
apiVersion: ramendr.openshift.io/v1alpha1
kind: Recipe
metadata:
  name: vm-consistency-recipe
spec:
  hooks:
    - name: vm-freeze
      namespace: vm-namespace
      labelSelector: vm.kubevirt.io/name=my-database-vm
      ops:
        - name: pre-backup
          container: virt-launcher
          command: ["/usr/bin/fsfreeze", "-f", "/mnt"]
        - name: post-backup
          container: virt-launcher
          command: ["/usr/bin/fsfreeze", "-u", "/mnt"]
  workflows:
    - name: vm-capture
      sequence:
        - hook: vm-freeze/pre-backup
        - group: volumes
        - hook: vm-freeze/post-backup
```

---

## 4. Cross-Reference Matrix

| Feature | RamenDR | Ceph CSI | CNV Tests |
|---------|---------|----------|-----------|
| VolumeReplication CR Management | ✅ Orchestrates | ✅ Implements | ⚠️ Consumes |
| Multi-Cluster Coordination | ✅ Core Feature | ❌ N/A | ❌ N/A |
| Block Replication | ⚠️ Via Driver | ✅ RBD Mirror | ✅ Validates |
| File Replication | ⚠️ Via VolSync | ✅ CephFS Mirror | ✅ Validates |
| Application Consistency | ✅ Recipes | ❌ Driver-level only | ✅ VM-level |
| Fencing/Split-Brain Protection | ✅ Yes | ⚠️ Limited | ❌ N/A |
| S3 Metadata Store | ✅ PV metadata | ❌ N/A | ❌ N/A |
| E2E Test Suite | ✅ Controller tests | ✅ Comprehensive | ✅ VM-focused |

---

## 5. How to Use These Sources for Certification

### Step 1: Study RamenDR VRG Controller
**Goal:** Understand orchestration patterns

1. Read VRG API types: `api/v1alpha1/volumereplicationgroup_types.go`
2. Study controller reconciliation loop
3. Understand state machine (Primary ↔ Secondary)
4. Learn PV metadata management patterns

**Key Takeaways for Certification:**
- How to group PVCs for coordinated replication
- Proper state transition sequences
- Fencing mechanisms to prevent data corruption

### Step 2: Analyze Ceph CSI Implementation
**Goal:** Learn correct gRPC sequences and CRD interactions

1. Review `internal/rbd/replication.go` for RBD mirror implementation
2. Study `e2e/rbd.go` test patterns
3. Understand VolumeReplication CR lifecycle
4. Learn error handling patterns

**Key Takeaways for Certification:**
- Correct gRPC call sequences for replication operations
- How to report replication status in VolumeReplication CR
- Proper handling of promote/demote operations
- Error cases and recovery procedures

### Step 3: Validate with CNV Tests
**Goal:** Ensure VM workloads are properly supported

1. Run kubevirt-storage-checkup against your driver
2. Validate VM boot from replicated volumes
3. Test live migration scenarios
4. Verify snapshot consistency

**Key Takeaways for Certification:**
- VM-specific requirements for storage
- Application consistency requirements
- Performance expectations for virtualized workloads

---

## 6. Certification Test Derivation

Based on these sources, derive your certification tests:

### From RamenDR:
- VRG creation and PVC discovery
- Primary to Secondary state transitions
- Cross-cluster failover
- Fencing scenarios
- Recipe-based application protection

### From Ceph CSI:
- VolumeReplication CR lifecycle
- Replication status reporting
- Promote/Demote operations
- Resync operations
- Volume group consistency

### From CNV:
- VM boot from replicated storage
- Live migration with replication
- Application-consistent snapshots
- VM failover scenarios

---

## 7. Additional Resources

### Documentation
- [RamenDR Documentation](https://github.com/RamenDR/ramen/tree/main/docs)
- [Ceph CSI Documentation](https://github.com/ceph/ceph-csi/tree/devel/docs)
- [KubeVirt Storage Documentation](https://kubevirt.io/user-guide/storage/)

### Community
- RamenDR Slack: #ramen-dr (Kubernetes Slack)
- Ceph CSI: #ceph-csi (Kubernetes Slack)
- KubeVirt: #kubevirt (Kubernetes Slack)

### Standards
- [CSI Spec](https://github.com/container-storage-interface/spec)
- [Volume Replication Operator](https://github.com/csi-addons/volume-replication-operator)
- [VolSync](https://volsync.readthedocs.io/)

---

## Next Steps

After reviewing these sources, proceed to:
1. [Layer 1 README](./layer-1-readme.md) - Kubernetes core CSI tests
2. [Layer 2 README](./layer-2-readme.md) - OpenShift platform tests
3. [Layer 3 README](./layer-3-readme.md) - CNV application tests
4. [Test Plan Matrix](./test-plan-matrix.md) - Comprehensive test coverage
