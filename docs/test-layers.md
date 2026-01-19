# CSI Replication Test Layers

## Overview
This document describes the multi-layer testing architecture for CSI Replication certification. The strategy is designed to validate storage replication capabilities across three distinct layers, each building upon the previous layer's validation.

## Test Architecture

### Layer 1: CSI/Kubernetes Core Tests (Upstream K8s)
**Repository:** [kubernetes/kubernetes/test/e2e/storage/external](https://github.com/kubernetes/kubernetes/tree/master/test/e2e/storage/external)

**Purpose:** Validate core CSI driver functionality and adherence to Kubernetes CSI specifications

**Key Components:**
- **Driver Definition Framework:** Uses YAML/JSON manifests to define driver capabilities
- **Test Suite Integration:** Pluggable architecture allowing external drivers to be tested against standard test suites
- **Capability Discovery:** Automatic detection of driver features through capability flags

**Test Categories:**
1. **Basic Provisioning Tests**
   - Dynamic volume provisioning
   - Volume attachment/detachment
   - Volume mounting/unmounting
   - Volume deletion

2. **Storage Class Tests**
   - StorageClass parameter validation
   - Default StorageClass handling
   - Multiple StorageClass support

3. **Snapshot Tests** (Optional Feature)
   - VolumeSnapshot creation
   - VolumeSnapshot deletion
   - VolumeSnapshot as data source for cloning

4. **Topology Tests**
   - Zone awareness
   - Node affinity
   - Volume scheduling

**How to Run:**
```bash
# Create driver definition file
cat > /tmp/driver-definition.yaml <<EOF
StorageClass:
  FromName: true
SnapshotClass:
  FromName: true
DriverInfo:
  Name: example.csi.driver.io
  Capabilities:
    persistence: true
    fsType: ext4
    exec: true
    volumeExpansion: true
    snapshotDataSource: true
EOF

# Run tests
ginkgo -p -focus='External.Storage.*example.csi.driver.io' \
       -skip='\[Feature:|\[Disruptive\]' \
       e2e.test \
       -- \
       -storage.testdriver=/tmp/driver-definition.yaml
```

---

### Layer 2: OCP Platform/Orchestration Tests
**Repository:** [openshift/origin/test/extended/storage/csi](https://github.com/openshift/origin/tree/main/test/extended/storage/csi)

**Purpose:** Validate enterprise platform-specific features and stress testing

**Key Components:**
- **OpenShift-specific CSI Extensions:** Platform integration validation
- **LUN Stress Testing:** High-volume attachment validation
- **Platform Integration:** Tests specific to OpenShift/OKD environments

**Test Categories:**

1. **LUN Stress Test (SCSI Overflow)**
   - **Default Configuration:** 260 Pods with PVCs on single node
   - **Timeout:** 40 minutes (configurable)
   - **Purpose:** Validate driver behavior under extreme attach/detach load
   - **Validation Points:**
     - CSI driver attach limit compliance (via CSINode)
     - Proper error handling when over limit
     - Recovery from timeout scenarios
     - LUN number handling (>256 LUNs)

2. **Multi-Cluster Tests**
   - Cross-cluster volume access
   - Cluster failover scenarios
   - Volume migration between clusters

3. **Performance Benchmarking**
   - Throughput testing
   - IOPS validation
   - Latency measurements

**Configuration Example:**
```yaml
Driver: my-csi-driver.example.com
LUNStressTest:
  PodsTotal: 260
  Timeout: "40m"
```

**How to Run:**
```bash
# Set environment variables
export TEST_CSI_DRIVER_FILES=/path/to/upstream-driver.yaml
export TEST_OCP_CSI_DRIVER_FILES=/path/to/ocp-driver.yaml

# Run OpenShift tests
openshift-tests run openshift/conformance/serial \
  --provider=external \
  -o test-results.txt
```

---

### Layer 3: CNV Application Tests (Virtualization)
**Repository:** [kiagnose/kubevirt-storage-checkup](https://github.com/kiagnose/kubevirt-storage-checkup)

**Purpose:** Validate VM-level storage consistency and application-aware replication

**Key Components:**
- **VM Consistency Checks:** Validate data integrity at VM level
- **Application Hooks:** Pre/post snapshot application quiescing
- **Live Migration Support:** Storage validation during VM migration

**Test Categories:**

1. **VM Storage Validation**
   - VM boot from replicated volumes
   - Live migration with storage replication
   - VM snapshot consistency
   - VM failover validation

2. **Application Consistency**
   - Database consistency checks (MySQL, PostgreSQL)
   - Application-specific hooks
   - Crash-consistency validation
   - Quiesced snapshot validation

3. **Performance Impact**
   - Replication overhead on VM performance
   - Live migration performance
   - Snapshot creation time

**How to Run:**
```bash
# Deploy kubevirt-storage-checkup
kubectl apply -f https://github.com/kiagnose/kubevirt-storage-checkup/releases/latest/download/checkup.yaml

# Run validation
kubectl wait --for=condition=ready pod/storage-checkup
kubectl logs -f storage-checkup
```

---

## Test Layer Dependencies

```
┌─────────────────────────────────────┐
│  Layer 3: CNV Application Tests     │
│  (VM-level consistency & failover)  │
└──────────────┬──────────────────────┘
               │ Depends on
               ▼
┌─────────────────────────────────────┐
│  Layer 2: OCP Platform Tests        │
│  (Enterprise features & stress)     │
└──────────────┬──────────────────────┘
               │ Depends on
               ▼
┌─────────────────────────────────────┐
│  Layer 1: Kubernetes Core CSI Tests │
│  (Basic CSI functionality)          │
└─────────────────────────────────────┘
```

**Certification Requirements:**
- Must pass Layer 1 before proceeding to Layer 2
- Must pass Layer 2 before proceeding to Layer 3
- All three layers must pass for full certification

---

## Test Execution Flow

### Phase 1: Core CSI Validation (Layer 1)
1. Define driver capabilities in YAML manifest
2. Run upstream Kubernetes CSI test suite
3. Validate all required capabilities
4. Document any optional features not supported

### Phase 2: Platform Integration (Layer 2)
1. Configure platform-specific manifest
2. Run LUN stress test (recommended: 257+ pods)
3. Execute platform-specific feature tests
4. Validate performance benchmarks

### Phase 3: Application Validation (Layer 3)
1. Deploy test VMs with replicated storage
2. Run consistency validation checks
3. Execute failover scenarios
4. Validate application-level data integrity

---

## Success Criteria

### Layer 1 (Core CSI)
- ✅ All provisioning tests pass
- ✅ Attachment/detachment works correctly
- ✅ Snapshot operations succeed (if supported)
- ✅ Topology awareness functions properly

### Layer 2 (Platform)
- ✅ LUN stress test completes within timeout
- ✅ All 260 pods successfully schedule and run
- ✅ Driver properly reports and enforces attach limits
- ✅ Platform-specific features work correctly

### Layer 3 (Application)
- ✅ VMs boot successfully from replicated volumes
- ✅ Live migration completes without data loss
- ✅ Application consistency checks pass
- ✅ Failover scenarios complete successfully

---

## Common Issues and Troubleshooting

### Layer 1 Issues
- **Problem:** Tests fail due to missing capabilities
  - **Solution:** Update driver definition YAML to accurately reflect supported capabilities

- **Problem:** Snapshot tests fail
  - **Solution:** Ensure VolumeSnapshotClass is properly configured

### Layer 2 Issues
- **Problem:** LUN stress test times out
  - **Solution:** Review CSINode attach limits, increase timeout if necessary

- **Problem:** Some pods fail to schedule
  - **Solution:** Verify scheduler is respecting CSI driver attach limits

### Layer 3 Issues
- **Problem:** VM fails to boot from replicated volume
  - **Solution:** Verify volume replication completed successfully and PV/PVC binding is correct

- **Problem:** Application consistency checks fail
  - **Solution:** Review application hook configuration and ensure proper quiescing

---

## Next Steps

After understanding the test layers, proceed to:
1. [Sources and References](./sources.md) - Learn about reference implementations
2. [Layer-Specific READMEs](./layer-1-readme.md) - Detailed instructions for each layer
3. [Test Plan Matrix](./test-plan-matrix.md) - Comprehensive test coverage matrix
4. [Suggested Tests](./suggested-tests.md) - Additional recommended test scenarios