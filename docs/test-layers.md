# Test Layers Overview

This document describes each testing layer in the CSI Replication Certification framework.

## Layer 1: CSI Driver Tests

### Purpose
Validate core CSI driver functionality including basic volume operations, snapshots, and clones.

### Scope
- Dynamic provisioning
- Volume attachment/detachment
- Volume snapshots
- Volume cloning
- Volume expansion
- Block and filesystem modes
- Storage capacity tracking

### Test Framework
Based on Kubernetes external storage test framework (test/e2e/storage/external)

### Key Test Suites
- Provisioning tests
- Snapshot tests
- Clone tests
- Capacity tests
- Multi-attach tests

### Example Tests
- Create PVC → Verify volume provisioned
- Create snapshot → Verify snapshot created
- Clone from snapshot → Verify clone successful
- Expand PVC → Verify new size

---

## Layer 2: Volume Replication Tests

### Purpose
Test storage-level replication capabilities using VolumeReplication CRD.

### Scope
- Enable replication on volumes
- Primary/Secondary role management
- Replication state transitions
- Sync/Async replication modes
- Force resync operations
- Replication health monitoring

### Dependencies
- Volume Replication Operator
- Storage backend with replication support (e.g., Ceph RBD mirroring)

### Key Test Scenarios
- Enable replication on new volume
- Promote secondary to primary
- Demote primary to secondary
- Force resync after split-brain
- Verify replication lag metrics

---

## Layer 3: VolumeReplicationGroup (VRG) Tests

### Purpose
Validate multi-volume coordination and consistency group replication.

### Scope
- Group multiple PVCs for consistent replication
- Crash-consistent point-in-time snapshots
- Application-consistent backups
- S3 metadata management
- PV/PVC metadata preservation
- Kubernetes object protection (ConfigMaps, Secrets, etc.)

### Dependencies
- VolumeReplicationGroup CRD (from RamenDR)
- S3-compatible object storage
- Volume Replication Operator
- VolSync (for sync mode)
- Velero (for Kubernetes object backup)

### Key Test Scenarios
- Create VRG for application with multiple PVCs
- Failover: Secondary → Primary promotion
- Failback: Return to original cluster
- Metadata upload/download to S3
- Application recovery with preserved PVCs
- Kubernetes resource restore (ConfigMap, Secret, Deployment)

---

## Layer 4: Disaster Recovery Orchestration Tests

### Purpose
End-to-end disaster recovery workflow testing across clusters.

### Scope
- Multi-cluster DR orchestration
- DRPolicy management
- DRPlacementControl workflows
- Failover automation
- Failback automation
- Application placement decisions
- Integration with OCM (Open Cluster Management)

### Dependencies
- RamenDR hub operator (OCM hub)
- RamenDR cluster operators (managed clusters)
- OCM
- All Layer 3 dependencies

### Key Components
- DRPolicy: Defines DR relationship between clusters
- DRPlacementControl (DRPC): Manages application DR lifecycle
- PlacementDecision: Controls workload placement

### Test Scenarios
- Basic Failover/Failback
- Planned Migration
- Disaster Scenarios (network partition, storage failure, complete cluster loss)

### Test Execution Order

For certification, tests should be executed in order:
1. Layer 1 - Ensure CSI driver basics work
2. Layer 2 - Verify replication at volume level
3. Layer 3 - Validate group replication and metadata
4. Layer 4 - Test full DR orchestration

Each layer builds on the previous, so failures at lower layers indicate issues that must be resolved before proceeding.