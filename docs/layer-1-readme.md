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
The tests are comprehensively categorized covering both VolumeReplication (CSI gRPC) and VolumeReplicationGroup (CRD) operations:

### VolumeReplication Tests (CSI gRPC)
1. **EnableVolumeReplication** - 6+ test scenarios including mode variants, error cases, idempotent operations
2. **DisableVolumeReplication** - 8+ test scenarios covering all cluster/peer/array state combinations with force parameters
3. **PromoteVolume** - Multiple test scenarios for healthy/degraded states with force options
4. **DemoteVolume** - Comprehensive scenarios for role transitions and error conditions
5. **ResyncVolume** - Split-brain recovery and synchronization scenarios
6. **GetVolumeReplicationInfo** - Health status and monitoring test cases

### VolumeReplicationGroup Tests (CRD)
1. **VRG Disable Operations** - 16 core scenarios covering active/disabled replication states with force parameters
2. **VRG Creation/Lifecycle** - Single/multiple PVC scenarios with cluster state variations
3. **VRG Failover/Failback** - Emergency and planned failover scenarios
4. **VRG Status/Monitoring** - Health checks and error reporting
5. **VRG Deletion/Cleanup** - Resource cleanup with various dependency states
6. **VRG Cross-Namespace** - Multi-namespace and multi-cluster scenarios

**Total Test Coverage**: 100+ individual test cases across all scenarios and state combinations

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
To run the tests, follow these instructions:
1. Clone the repository:  
   ```bash
   git clone https://github.com/nadavleva/csi_replication_certs.git
   cd csi_replication_certs
   ```
2. Install the necessary dependencies:  
   ```bash
   make setup
   ```
3. Execute the tests:  
   ```bash
   make test
   ```

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