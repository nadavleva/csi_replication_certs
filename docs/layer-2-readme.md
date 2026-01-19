# Layer 2: OpenShift Platform & Replication Tests

## Overview
Layer 2 tests validate enterprise-grade CSI replication features specific to OpenShift Container Platform (OCP). These tests build upon Layer 1 by adding VolumeReplication capabilities, stress testing, and multi-cluster disaster recovery scenarios.

**Prerequisites:** All mandatory Layer 1 tests must pass before proceeding to Layer 2.

---

## Current Reference Implementations

### 1. OpenShift CSI Test Framework
**Source:** [openshift/origin/test/extended/storage/csi](https://github.com/openshift/origin/tree/master/test/extended/storage/csi)

The OpenShift CSI test suite extends upstream Kubernetes tests with OCP-specific features:

- **LUN Stress Test:** Tests driver stability with 260 pods/PVCs on a single node
- **CSI driver certification:** Validates OCP-specific requirements
- **Integration testing:** Tests with OCP storage operators and frameworks

**Key Files:**
- `csi.go` - Main test orchestration and OpenShift-specific test suite registration
- `scsi_overflow.go` - LUN stress test implementation (260 pods)
- `README.md` - Complete test execution guide

### 2. Ceph CSI E2E Tests
**Source:** [ceph/ceph-csi/e2e](https://github.com/ceph/ceph-csi/tree/devel/e2e)

Ceph CSI provides comprehensive E2E tests for replication features:

- **RBD Replication:** Volume replication for block storage
- **CephFS Replication:** File storage replication scenarios
- **Resize & Clone:** Volume expansion and cloning tests
- **Snapshot & Restore:** Complete snapshot lifecycle testing

**Key Files:**
- `rbd.go`, `cephfs.go` - Storage-specific test implementations
- `snapshot.go` - VolumeSnapshot test scenarios
- `resize.go` - Volume expansion tests
- `README.md` - Test execution parameters and commands

### 3. RamenDR VolumeReplicationGroup
**Source:** [RamenDR/ramen](https://github.com/RamenDR/ramen)

RamenDR implements VolumeReplicationGroup (VRG) for coordinated multi-volume replication:

**Architecture:**
```
┌─────────────────────────────────────────────┐
│           DRPlacementControl                │
│  (Hub Cluster - Multi-cluster orchestration)│
└──────────────────┬──────────────────────────┘
                   │
                   │ Creates VRG on each cluster
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼─────┐         ┌─────▼────┐
   │   VRG    │         │   VRG    │
   │ (Primary)│◄────────┤(Secondary)│
   │ Cluster-A│Replicate│ Cluster-B│
   └────┬─────┘         └────┬─────┘
        │                    │
   Creates VR CRs      Creates VR CRs
        │                    │
   ┌────▼─────┐         ┌────▼─────┐
   │ Volume   │         │ Volume   │
   │Replication│        │Replication│
   └──────────┘         └──────────┘
```

**Key Concepts:**
- **VRG (VolumeReplicationGroup):** Manages multiple PVCs as a group
- **PVC Selector:** Automatically discovers PVCs to replicate using labels
- **State Management:** Coordinates Primary/Secondary state transitions
- **S3 Integration:** Stores PV metadata for cross-cluster restore

**Key Files:**
- `api/v1alpha1/volumereplicationgroup_types.go` - VRG API definition
- `internal/controller/volumereplicationgroup_controller.go` - VRG reconciliation logic
- `docs/` - Architecture and usage documentation

---

## Test Categories (26 Tests, ~135 minutes)

### L2.1 - LUN Stress Test ⭐ CRITICAL
**Time:** ~40 minutes  
**Priority:** 🔴 Mandatory

Tests driver behavior under heavy load with 260 pods/PVCs on a single node.

**Key Tests:**
- 260 pod stress test
- Attach limit validation
- Error handling
- Driver recovery

### L2.2 - VolumeReplication Tests
**Time:** ~35 minutes  
**Priority:** 🔴 Mandatory

Tests individual volume replication using VolumeReplication CRD.

**Key Tests:**
- Primary/Secondary state transitions
- Promote/Demote operations
- Replication status reporting
- Resync operations

### L2.3 - VolumeReplicationGroup Tests
**Time:** ~45 minutes  
**Priority:** 🔴 Mandatory

Tests coordinated multi-volume replication using VRG.

**Key Tests:**
- VRG creation with PVC selector
- Group replication
- Coordinated failover
- Dynamic PVC addition/removal

### L2.4 - Multi-Cluster Failover Tests
**Time:** ~70 minutes  
**Priority:** 🔴 Mandatory

Tests disaster recovery across clusters.

**Key Tests:**
- Planned failover
- Unplanned failover
- Data validation
- Fencing and split-brain prevention

---

## Quick Start

### Prerequisites
```bash
# Verify Layer 1 passed
# Install OpenShift CLI
oc version

# Deploy test driver
oc apply -f driver-deployment.yaml

# Create test namespace
oc create namespace csi-test
```

### Run Layer 2 Tests

**Option 1: OpenShift Test Suite**
```bash
export TEST_CSI_DRIVER_FILES=/path/to/upstream-driver.yaml
export TEST_OCP_CSI_DRIVER_FILES=/path/to/ocp-driver.yaml

openshift-tests run openshift/csi \
  --provider=none \
  -o test-results/layer2-results.xml
```

**Option 2: Specific Test Focus**
```bash
# LUN Stress Test Only
openshift-tests run --file=<(
  openshift-tests run --dry-run openshift/csi | \
  grep -i "should use many PVs"
)

# VolumeReplication Tests
oc apply -f examples/volumereplication.yaml
# Monitor status
oc get volumereplication -w
```

---

## Expected Results

### Success Criteria
- ✅ LUN stress test completes in <40 minutes
- ✅ All 260 pods eventually reach Running/Completed state
- ✅ VolumeReplication state transitions work correctly
- ✅ VRG manages multiple PVCs successfully
- ✅ Failover completes with data integrity maintained
- ✅ No driver crashes or panics

### Common Issues

**Issue:** LUN stress test times out
- **Solution:** Check CSINode attach limits, verify driver can handle retries

**Issue:** VolumeReplication stuck in pending
- **Solution:** Check VolumeReplicationClass exists, verify backend connectivity

**Issue:** VRG not discovering PVCs
- **Solution:** Verify PVC labels match selector, check VRG namespace

---

## Next Steps

After successfully completing Layer 2:

1. ✅ Document all test results
2. ✅ Verify RTO < 5 minutes for failover
3. ✅ Verify RPO meets requirements
4. ➡️ Proceed to [Layer 3: CNV Application Tests](./layer-3-readme.md)

---

## Additional Resources

- [OpenShift Storage Documentation](https://docs.openshift.com/container-platform/latest/storage/index.html)
- [Ceph CSI Documentation](https://github.com/ceph/ceph-csi/tree/devel/docs)
- [RamenDR Documentation](https://github.com/RamenDR/ramen/tree/main/docs)
- [Complete Test Matrix](./test-plan-matrix.md)

---

## TBD - Suggested Advanced Tests

See [Suggested Tests](./suggested-tests.md) for additional scenarios:
- Extended stress testing (>260 pods)
- Performance benchmarking
- Failure injection testing
- Security and encryption validation