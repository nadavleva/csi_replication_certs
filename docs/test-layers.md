# 4-Layer Architecture for CSI Replication

## Layer 0: Core CSI Certification
- **Description**: An external prerequisite involving Kubernetes CSI conformance tests.

## Layer 1: CSI Replication Add-on
- **Focus**: Primary implementation of the CSI Replication Add-on.
- **RPCs**:
  - EnableVolumeReplication
  - DisableVolumeReplication
  - PromoteVolume
  - DemoteVolume
  - ResyncVolume
  - GetVolumeReplicationInfo
- **References**:
  - [csi-addons/spec/replication](https://example.com/csi-addons/spec/replication)
  - [kubevirt-storage-checkup CSI API Summary](https://example.com/kubevirt-storage-checkup)

## Layer 2: OCP Platform Orchestration
- **Overview**: Management within a single cluster utilizing VRG.
- **Focus Areas**:
  - Pod failover
  - OpenShift integration 

## Layer 3: Multi-Cluster DR and CNV
- **Technologies**: RamenDR for multi-cluster orchestration.
- **Key Components**:
  - DRPolicy
  - DRPlacementControl
  - VM failover
  - Integration with kubevirt-storage-checkup

## Additional Details
- **Dependencies**: 
  - Layer 1 depends on Layer 0 for certification.
  - Layer 2 depends on Layer 1 for replication functionality.
  - Layer 3 relies on Layer 2 for orchestration management.

## Testing Considerations
- **Pass/Fail Criteria**: Specific conditions that must be met for each layer to be considered successful. Document these criteria based on framework and performance metrics relevant to the application.
- **Test Execution Workflow**: Describe the process of executing tests across layers, ensuring that the dependencies are respected and that results can be traced through to their corresponding criteria.
- **Official References**: Provide authoritative sources for standards, requirements, and processes that govern each layer as applicable.