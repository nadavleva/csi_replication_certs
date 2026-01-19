# Layer 1: Kubernetes Core CSI Tests

## Overview
Layer 1 tests validate that your CSI driver correctly implements the core CSI specification and integrates properly with upstream Kubernetes. These tests are provider-agnostic and focus on fundamental CSI functionality.

**Source:** [kubernetes/kubernetes/test/e2e/storage/external](https://github.com/kubernetes/kubernetes/tree/master/test/e2e/storage/external)

---

## Prerequisites

### 1. Test Environment
- Kubernetes cluster (v1.20+)
- Your CSI driver deployed and operational
- `kubectl` configured to access the cluster
- `ginkgo` test framework installed

### 2. Required Components
```bash
# Install ginkgo
go install github.com/onsi/ginkgo/v2/ginkgo@latest

# Download e2e.test binary
VERSION=v1.28.0  # Use your Kubernetes version
curl -L "https://dl.k8s.io/${VERSION}/kubernetes-test-linux-amd64.tar.gz" | tar -xz
```

### 3. CSI Driver Requirements
Your driver must be deployed with:
- CSI Controller component (for provisioning, attaching)
- CSI Node component (for mounting)
- StorageClass(es) pre-configured
- VolumeSnapshotClass (if snapshot support is claimed)

---

## Driver Definition File

### Basic Template
Create a driver definition file that describes your CSI driver's capabilities:

```yaml
# driver-definition.yaml
DriverInfo:
  Name: "your-driver.example.com"
  Capabilities:
    persistence: true          # Volumes persist across pod restarts
    block: false               # Supports raw block volumes
    exec: true                 # Supports kubectl exec
    snapshotDataSource: true   # Supports snapshots as data source
    pvcDataSource: true        # Supports PVC cloning
    volumeExpansion: true      # Supports online volume expansion
    controllerExpansion: true  # Expansion done at controller
    nodeExpansion: true        # Expansion requires node component
    topology: false            # Supports topology awareness
  SupportedFsType:
    - "ext4"
    - "xfs"
  SupportedSizeRange:
    Min: "1Gi"
    Max: "16Ti"

StorageClass:
  FromName: true  # Use existing StorageClass named after driver

SnapshotClass:
  FromName: true  # Use existing VolumeSnapshotClass named after driver
```

### Advanced Configuration

#### Using Custom StorageClass
```yaml
StorageClass:
  FromFile: "path/to/storageclass.yaml"
```

#### Specifying Existing Classes
```yaml
StorageClass:
  FromExistingClassName: "my-storage-class"

SnapshotClass:
  FromExistingClassName: "my-snapshot-class"
```

### Capability Reference

| Capability | Description | Required |
|------------|-------------|----------|
| `persistence` | Volumes survive pod restart | Yes |
| `block` | Raw block volume support | No |
| `exec` | Exec into pods with volumes | Recommended |
| `snapshot` | Volume snapshots | Recommended |
| `snapshotDataSource` | Clone from snapshot | No |
| `pvcDataSource` | Clone from PVC | No |
| `volumeExpansion` | Online volume resize | Recommended |
| `controllerExpansion` | Controller-side expansion | If volumeExpansion=true |
| `topology` | Topology-aware scheduling | No |

---

## Running Tests

### 1. Basic Test Run
```bash
# Run all conformance tests for your driver
ginkgo -p \
  -focus='External.Storage.*your-driver.example.com' \
  -skip='\[Feature:|\[Disruptive\]' \
  e2e.test \
  -- \
  -storage.testdriver=/path/to/driver-definition.yaml \
  -report-dir=./test-results
```

### 2. Test Specific Features

#### Snapshot Tests
```bash
ginkgo -p \
  -focus='External.Storage.*your-driver.example.com.*\[Feature:VolumeSnapshotDataSource\]' \
  e2e.test \
  -- \
  -storage.testdriver=/path/to/driver-definition.yaml
```

#### Volume Expansion Tests
```bash
ginkgo -p \
  -focus='External.Storage.*your-driver.example.com.*volume.expansion' \
  e2e.test \
  -- \
  -storage.testdriver=/path/to/driver-definition.yaml
```

#### Topology Tests
```bash
ginkgo -p \
  -focus='External.Storage.*your-driver.example.com.*topology' \
  e2e.test \
  -- \
  -storage.testdriver=/path/to/driver-definition.yaml
```

### 3. Test Selection Patterns

```bash
# Run only provisioning tests
-focus='.*provisioning'

# Skip disruptive tests
-skip='\[Disruptive\]'

# Run specific test suite
-focus='volumeMode'

# Combination
-focus='External.Storage.*mydriver' -skip='\[Feature:|\[Slow\]'
```

---

## Test Suites Explained

### 1. Provisioning Tests
**Focus:** `provisioning`

Tests dynamic volume provisioning:
- Create PVC → PV automatically provisioned
- PVC/PV binding
- Volume deletion
- Reclaim policies (Delete, Retain)

**Expected Behavior:**
- PVC reaches `Bound` status
- PV created with correct capacity
- Volume accessible in pod
- Volume deleted when PVC deleted (if reclaimPolicy=Delete)

### 2. Snapshot Tests
**Focus:** `snapshot`

Tests volume snapshot functionality:
- Create VolumeSnapshot from PVC
- VolumeSnapshot reaches `ReadyToUse=true`
- Create PVC from VolumeSnapshot (restore)
- Data consistency validation

**Expected Behavior:**
- Snapshot creation succeeds
- Snapshot contains correct data
- Restore from snapshot creates functional volume
- Data matches original

### 3. Volume Expansion Tests
**Focus:** `volume.expansion`

Tests online volume resize:
- Create PVC with initial size
- Update PVC to larger size
- Verify filesystem expansion
- Application can use expanded space

**Expected Behavior:**
- PVC status shows new size
- Filesystem reflects new size
- No pod restart required (for online expansion)
- Data preserved during expansion

### 4. Volume Cloning Tests
**Focus:** `pvcDataSource`

Tests PVC-to-PVC cloning:
- Create source PVC with data
- Create clone PVC referencing source
- Verify clone contains source data
- Clone is independent (modifications don't affect source)

**Expected Behavior:**
- Clone PVC provisions successfully
- Clone contains same data as source
- Clone and source are independent volumes

### 5. Topology Tests
**Focus:** `topology`

Tests topology-aware provisioning:
- Volume provisioned in correct zone/region
- Pod scheduled to node with volume access
- Cross-zone scenarios handled correctly

**Expected Behavior:**
- Volume created in allowed topology
- Pod scheduled correctly based on volume location
- Topology constraints respected

---

## Interpreting Results

### Success Criteria
```
Ran 87 of 245 Specs in 3600.123 seconds
SUCCESS! -- 87 Passed | 0 Failed | 0 Pending | 158 Skipped
```

**What this means:**
- ✅ 87 applicable tests ran and passed
- ✅ 158 tests skipped (optional features or inapplicable)
- ✅ 0 failures

### Common Failure Patterns

#### 1. Provisioning Failures
```
[FAIL] Provisioning should provision storage with defaults
Expected PVC to be bound, but was: Pending
```

**Possible Causes:**
- StorageClass not found or misconfigured
- CSI controller not running
- Incorrect provisioner name in StorageClass
- Resource quota exceeded

**Debug Steps:**
```bash
# Check CSI controller logs
kubectl logs -n kube-system deployment/csi-controller

# Describe PVC
kubectl describe pvc test-pvc

# Check StorageClass
kubectl get sc -o yaml
```

#### 2. Snapshot Failures
```
[FAIL] Snapshot should create snapshot
VolumeSnapshot never reached ReadyToUse=true
```

**Possible Causes:**
- VolumeSnapshotClass not configured
- CSI driver doesn't support snapshots
- Snapshot controller not deployed
- Backend storage doesn't support snapshots

**Debug Steps:**
```bash
# Check snapshot controller
kubectl logs -n kube-system deployment/snapshot-controller

# Describe VolumeSnapshot
kubectl describe volumesnapshot test-snap

# Check driver capabilities
kubectl get csidriver your-driver -o yaml
```

#### 3. Volume Expansion Failures
```
[FAIL] Volume Expansion should resize volume
PVC size not updated after resize request
```

**Possible Causes:**
- `allowVolumeExpansion: false` in StorageClass
- Driver doesn't support expansion
- Filesystem doesn't support online resize
- Node component not handling expansion

**Debug Steps:**
```bash
# Check StorageClass
kubectl get sc your-storage-class -o yaml | grep allowVolumeExpansion

# Check PVC conditions
kubectl get pvc test-pvc -o yaml | grep -A 10 conditions

# Check CSI node logs
kubectl logs -n kube-system daemonset/csi-node
```

---

## Test Matrix for Layer 1

| Test Category | Required | Test Count | Time Estimate |
|--------------|----------|------------|---------------|
| Basic Provisioning | ✅ Yes | ~15 tests | 5-10 min |
| Volume Attachment | ✅ Yes | ~10 tests | 5-10 min |
| Volume Snapshots | ⚠️ Optional | ~12 tests | 10-15 min |
| Volume Cloning | ⚠️ Optional | ~8 tests | 10-15 min |
| Volume Expansion | ⚠️ Recommended | ~6 tests | 5-10 min |
| Topology | ⚠️ Optional | ~10 tests | 10-15 min |
| **Total** | | **~61 tests** | **45-75 min** |

---

## Detailed Test Cases

### Provisioning Tests

#### Test 1.1: Basic Dynamic Provisioning
```
Scenario: Create PVC with default parameters
Steps:
  1. Create PVC requesting 1Gi
  2. Wait for PVC to bind
  3. Verify PV created
  4. Create pod using PVC
  5. Verify volume mounted in pod
  6. Delete pod
  7. Delete PVC
  8. Verify PV deleted (if reclaimPolicy=Delete)

Expected Result: All steps succeed, no errors
```

#### Test 1.2: Pre-Bound PVC
```
Scenario: Create PVC and PV with pre-binding
Steps:
  1. Create PV manually
  2. Create PVC with volumeName set to PV
  3. Verify PVC binds to specific PV
  4. Verify no additional PV created

Expected Result: PVC binds to pre-specified PV
```

#### Test 1.3: Storage Class Parameters
```
Scenario: Provision with custom parameters
Steps:
  1. Create StorageClass with custom parameters
  2. Create PVC using custom StorageClass
  3. Verify volume created with correct parameters
  4. Validate parameters on backend storage

Expected Result: Volume created with specified parameters
```

### Snapshot Tests

#### Test 2.1: Create Snapshot
```
Scenario: Create snapshot from existing PVC
Steps:
  1. Create PVC and write data
  2. Create VolumeSnapshot referencing PVC
  3. Wait for ReadyToUse=true
  4. Verify snapshot exists on backend
  5. Delete VolumeSnapshot
  6. Verify snapshot deleted from backend

Expected Result: Snapshot lifecycle works correctly
```

#### Test 2.2: Restore from Snapshot
```
Scenario: Create PVC from snapshot
Steps:
  1. Create source PVC with test data
  2. Create snapshot of source PVC
  3. Create new PVC with dataSource=snapshot
  4. Mount new PVC in pod
  5. Verify data matches original
  6. Modify data in new PVC
  7. Verify source PVC data unchanged

Expected Result: Restored data matches snapshot, volumes are independent
```

### Expansion Tests

#### Test 3.1: Online Volume Expansion
```
Scenario: Expand volume while pod is running
Steps:
  1. Create PVC with size=1Gi
  2. Create pod using PVC
  3. Write data close to capacity
  4. Update PVC to size=2Gi
  5. Verify PVC status shows 2Gi
  6. Verify filesystem shows 2Gi in pod
  7. Verify data still accessible
  8. Write additional data

Expected Result: Expansion succeeds without pod restart
```

---

## Troubleshooting Guide

### Issue: Tests Hang or Timeout

**Symptoms:**
- Tests run for extended period without completing
- Ginkgo shows "waiting for condition"

**Solutions:**
```bash
# Increase timeout
-ginkgo.timeout=2h

# Run with verbose output
-ginkgo.v

# Check CSI driver logs in real-time
kubectl logs -f -n kube-system deployment/csi-controller
```

### Issue: Permission Denied Errors

**Symptoms:**
- Tests fail with RBAC errors
- "Forbidden" messages in logs

**Solutions:**
```bash
# Verify CSI driver ServiceAccount has correct permissions
kubectl get clusterrole csi-driver-role -o yaml

# Check if CSI driver pods are running with correct ServiceAccount
kubectl get pods -n kube-system -l app=csi-driver -o yaml | grep serviceAccount
```

### Issue: StorageClass Not Found

**Symptoms:**
- Tests skip with "StorageClass not found"

**Solutions:**
1. Verify StorageClass exists:
   ```bash
   kubectl get sc
   ```

2. Ensure driver-definition.yaml references correct class:
   ```yaml
   StorageClass:
     FromExistingClassName: "correct-class-name"
   ```

3. Check provisioner name matches:
   ```bash
   kubectl get sc your-class -o jsonpath='{.provisioner}'
   ```

---

## Next Steps

After successfully completing Layer 1 tests:

1. ✅ Document all passed tests
2. ✅ Note any optional features not supported
3. ✅ Capture test logs and results
4. ➡️  Proceed to [Layer 2: OCP Platform Tests](./layer-2-readme.md)

---

## Appendix: Complete Test Command Reference

```bash
# Full test run with all options
ginkgo -p \
  --randomize-all \
  --randomize-suites \
  --fail-on-pending \
  --keep-going \
  --trace \
  -focus='External.Storage.*your-driver.example.com' \
  -skip='\[Feature:|\[Disruptive\]|\[Slow\]' \
  e2e.test \
  -- \
  -storage.testdriver=/path/to/driver-definition.yaml \
  -report-dir=./test-results \
  -report-prefix=layer1 \
  -disable-log-dump=false \
  -v=4
```

**Options Explained:**
- `-p`: Run tests in parallel
- `--randomize-all`: Randomize test order (find ordering dependencies)
- `--fail-on-pending`: Fail if tests are marked pending
- `--keep-going`: Continue after failures
- `-v=4`: Verbose Kubernetes client logging
- `-report-dir`: Save JUnit XML reports