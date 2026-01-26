# Layer 1 CSI Replication Add-on Tests

## Overview
This document provides a comprehensive overview of Layer 1 CSI Replication Add-on tests. This is the primary focus of the project, aimed at ensuring the reliability and efficiency of the replication features. **This is an optional testing layer** that is only triggered when CSI drivers explicitly advertise replication capability support through CSI driver capability discovery or CRD annotations.

## Architecture
- **Technical Stack**: 
  - Go-based e2e tests
  - Ginkgo BDD framework 
  - Gomega matchers
- **Execution Environment**: 
  - Executed via `kubectl` and CSI replication sidecars
  - Runs against live Kubernetes clusters with replication-capable CSI drivers
  - Multi-cluster test scenarios with peer connectivity validation
- **Cluster Requirements**:
  - **Two clusters** with CSI drivers supporting replication capabilities
  - **Ceph as benchmark**: Reference implementation for replication-capable CSI drivers
  - Network connectivity between clusters for peer communication
  - S3-compatible storage for advanced disaster recovery scenarios (optional for basic VRG operations)

## API Categories

## VolumeReplication RPC Operations (CSI gRPC)
The following RPC operations test both individual volume replication and volume group replication via CSI gRPC endpoints:

### Individual Volume Operations
1. **EnableVolumeReplication** - Initiates the replication process for the specified volume.
2. **DisableVolumeReplication** - Stops the replication process for the specified volume.
3. **PromoteVolume** - Promotes a volume to be the primary for replication purposes.
4. **DemoteVolume** - Demotes a volume to a secondary state.
5. **ResyncVolume** - Resynchronizes the data of a volume with its replica.
6. **GetVolumeReplicationInfo** - Retrieves the replication status and information of a volume.

### Volume Group Operations
The same CSI gRPC APIs above handle volume group replication by using the **replicationsource** field to specify group membership. Volume group testing focuses on:
- **Happy path scenarios** - Basic enable/disable/promote/demote operations on volume groups
- **Negative scenarios** - Error handling when group operations fail
- **Mixed scenarios** - Operations on groups with mixed volume states

**For detailed VolumeReplication test matrix**: See [layer-1-vr-tests.md](layer-1-vr-tests.md)

## VolumeReplicationGroup Operations

**Note**: VolumeReplicationGroup (VRG) Kubernetes CRD tests are **not in scope for Phase 1**. Phase 1 focuses on CSI gRPC API testing only.

For **Volume Group Operations** using CSI gRPC APIs, the same VolumeReplication RPC endpoints handle group operations by using the **replicationsource** field to specify group membership. These group operations are tested as part of the CSI gRPC API validation.

**For detailed Volume Group test matrix using gRPC APIs**: See [layer-1-vrg-tests.md](layer-1-vrg-tests.md)

## Official References
- [CSI Add-ons Specification - Replication](https://github.com/csi-addons/spec/tree/main/replication)
- [CSI Add-ons Kubernetes Integration](https://github.com/csi-addons/kubernetes-csi-addons)
- [KubeVirt Storage Checkup](https://github.com/kiagnose/kubevirt-storage-checkup)
- [CSI Replication Add-on API Summary](https://github.com/nadavleva/kubevirt-storage-checkup/blob/main/docs/csi-addons-replication-api.md)

## Test Categories Summary
The tests are comprehensively categorized covering both VolumeReplication (CSI gRPC) and VolumeReplicationGroup operations:

### VolumeReplication Tests (CSI gRPC)
1. **EnableVolumeReplication** - Mode variants, error cases, idempotent operations
2. **DisableVolumeReplication** - All cluster/peer/array state combinations with force parameters
3. **PromoteVolume** - Healthy/degraded states with force options
4. **DemoteVolume** - Role transitions and error conditions
5. **ResyncVolume** - Split-brain recovery and synchronization scenarios
6. **GetVolumeReplicationInfo** - Health status and monitoring test cases
7. **Volume Group Operations** - Group operations using replicationsource field

### VolumeReplicationGroup Tests (Out of Scope for Phase 1)
1. **VRG Disable Operations** - Core scenarios covering active/disabled replication states with force parameters
2. **VRG Creation/Lifecycle** - Single/multiple PVC scenarios with cluster state variations
3. **VRG Failover/Failback** - Emergency and planned failover scenarios
4. **VRG Status/Monitoring** - Health checks and error reporting
5. **VRG Deletion/Cleanup** - Resource cleanup with various dependency states
6. **VRG Cross-Namespace** - Multi-namespace and multi-cluster scenarios

*For specific test counts, see the test matrices in [layer-1-vr-tests.md](layer-1-vr-tests.md) and [layer-1-vrg-tests.md](layer-1-vrg-tests.md)*

## Prerequisites
Before running the tests, ensure the following prerequisites are met:
- **Two Kubernetes clusters** set up and available with network connectivity between them.
- **CSI driver supporting replication** installed and configured on both clusters (Ceph CSI driver recommended as benchmark).
- CSI driver must **advertise replication capabilities** through:
  - CSI driver capability discovery, OR
  - CRD annotations indicating replication support
- Access to required RBAC permissions to perform replication operations on both clusters.
- **Network connectivity** between clusters for peer communication and data replication.
- **S3-compatible storage** accessible from both clusters (optional - only required for advanced disaster recovery scenarios and external metadata persistence)

## Setting Up Clusters for Testing

For detailed instructions on setting up a local multi-cluster environment for CSI replication testing, see the complete guide:

**[Setting Up Local Environment for CSI Replication API Testing](https://github.com/nadavleva/my-ramen-playground/blob/main/docs/testing/local-environment-setup.md)**

### Quick Setup Summary

The testing environment uses three minikube clusters:
- **Primary cluster (dr1)**: Active cluster where applications run initially
- **Secondary cluster (dr2)**: Standby cluster for failover/relocation  
- **Hub cluster**: Manages multi-cluster operations via OCM (Open Cluster Management)

**Key Components:**
- Ceph Storage with RBD mirroring between clusters
- CSI Addons for replication API support
- VolumeReplicationClasses with different sync intervals (1m, 5m)

**Setup Commands:**
```bash
# Activate environment
cd test && source venv

# Setup host for testing (run once)
drenv setup envs/regional-dr.yaml

# Start the multi-cluster environment (20-30 minutes)
drenv start envs/regional-dr.yaml
```

**Testing Access:**
```bash
# Switch between cluster contexts
kubectl config use-context dr1  # Primary cluster
kubectl config use-context dr2  # Secondary cluster

# Deploy and test applications
test/basic-test/deploy dr1
test/basic-test/enable-dr dr1
```

## CSI Replication API Parameters

The CSI Replication APIs support various parameters for controlling replication behavior. For comprehensive parameter documentation, see:

**[CSI Replication API Parameters and Values](https://github.com/nadavleva/my-ramen-playground/blob/main/docs/testing/replication-parameters.md)**

### Core Parameters

| Parameter | Type | Description | Values | Default | Used In |
|-----------|------|-------------|---------|---------|---------|
| **mirroringMode** | string | RBD mirroring mode | "snapshot", "journal" | "snapshot" | EnableVolumeReplication |
| **force** | bool | Force operations | "true", "false" | "false" | DisableVolumeReplication |
| **schedulingInterval** | string | Snapshot interval | "1m", "1h", "1d" | - | EnableVolumeReplication |
| **schedulingStartTime** | string | ISO 8601 start time | "14:00:00-05:00" | - | EnableVolumeReplication |
| **flattenMode** | string | Parent image handling | "never", "force" | "never" | EnableVolumeReplication |
| **replicationsource** | string | Volume group identifier | "group1", "group2" | - | All APIs (for groups) |

### Mirroring Modes

- **snapshot** (default): Uses RBD snapshots for periodic replication. Supports scheduling parameters.
- **journal**: Uses RBD journaling for real-time replication. Does not support scheduling parameters.

### Parameter Examples

**Enable Volume Replication - Snapshot Mode:**
```yaml
parameters:
  mirroringMode: "snapshot"
  schedulingInterval: "1h"
  schedulingStartTime: "14:00:00-05:00"
  flattenMode: "never"
```

**Enable Volume Group Replication:**
```yaml
parameters:
  mirroringMode: "snapshot"
  schedulingInterval: "5m"
  replicationsource: "group1"
```

**Disable Volume Replication with Force:**
```yaml
parameters:
  force: "true"
```

## Optional Testing Framework
This testing layer implements a **conditional execution model**:
- Tests are **automatically skipped** if CSI drivers do not advertise replication capabilities
- **Capability detection** occurs during test initialization phase  
- **Graceful degradation** when replication features are not supported
- **No false failures** for drivers that legitimately don't support replication

## Feature Flag Implementation Strategy
Feature flags are used to control the exposure of replication features. The strategy involves:
- Conditional checks based on the feature flag status.
- Wrapping new functionality under the feature flag to prevent breaking existing implementations.

## Running Tests Instructions

The actual test implementation and execution instructions are maintained in the forked Kubernetes CSI test repository:

**Test Implementation Repository**: [kubernetes_csiaddontests](https://github.com/nadavleva/kubernetes_csiaddontests)

**CSI Replication Tests Location**: 
- [test/e2e/storage](https://github.com/nadavleva/kubernetes_csiaddontests/tree/master/test/e2e/storage)
- CSI Replication Add-on specific tests and runners

### Quick Reference

For detailed execution instructions, test configuration, and implementation details:

1. **Clone the test repository**:
   ```bash
   git clone https://github.com/nadavleva/kubernetes_csiaddontests.git
   cd kubernetes_csiaddontests
   ```

2. **Follow the test execution guide** in the repository's documentation for:
   - Environment setup and configuration
   - CSI driver capability detection
   - Multi-cluster test execution
   - Test result interpretation

3. **Test Configuration**: The repository contains test manifests and configuration files for various CSI replication scenarios based on the test matrices defined in this documentation.

**Note**: This documentation repository ([csi_replication_certs](https://github.com/nadavleva/csi_replication_certs)) defines the test specifications and requirements, while the implementation repository contains the actual executable tests.

## Pass/Fail Criteria
The tests will be considered successful if:
- All assertions pass without any errors.
- There are no unexpected failures during execution.

## Example Workflow for Enabling Replication
1. Enable volume replication using the following command:
   ```bash
   csi-driver enable-replication --volume-id <volume_id>
   ```
2. Monitor the status of the replication process:
   ```bash
   csi-driver get-replication-status --volume-id <volume_id>
   ```

## Troubleshooting Guide
In case of issues, refer to the following steps for troubleshooting:
- Check the logs of the CSI components for any error messages.
- Ensure that the cluster meets all prerequisites mentioned above.
- Validate network connectivity between the source and destination volumes.

For further assistance, please refer to the official documentation or contact support.