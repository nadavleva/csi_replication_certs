# Documentation Index

## Layer 0: Core CSI Certification
- **Description**: External prerequisite not implemented in this project.
- **References**: Kubernetes CSI conformance tests.
- **Criteria**: Must pass all conformance tests. (Pass/Fail)
- **Status**: Not implemented.

## Layer 1: CSI Replication Add-on
- **Description**: This is the primary focus of this project.
- **References**: 
  - [CSI Addons Spec: Replication](https://github.com/csi-addons/spec/replication)
  - [Kubevirt Storage Checkup CSI API Summary](https://github.com/kubevirt/kubevirt-storage-checkup)
- **Functionality Covered**: 
  - EnableVolumeReplication
  - DisableVolumeReplication
  - PromoteVolume
  - DemoteVolume
  - ResyncVolume
  - GetVolumeReplicationInfo
- **Criteria**: All functionalities must operate correctly. (Pass/Fail)
- **Status**: In progress.

## Layer 2: OCP Platform Orchestration (Single Cluster)
- **Description**: Manage orchestration within a single OpenShift cluster.
- **References**: 
  - [OpenShift Origin Storage Tests](https://github.com/openshift/origin)
- **Focus Areas**: 
  - Pod failover
  - VRG management
- **Criteria**: Must pass designated storage tests. (Pass/Fail)
- **Status**: Planned.

## Layer 3: Multi-Cluster DR and CNV
- **Description**: Focus on disaster recovery across multiple clusters and Container Native Virtualization (CNV).
- **References**: 
  - [RamenDR](https://github.com/ramendb/ramen)
  - [Kubevirt Storage Checkup](https://github.com/kubevirt/kubevirt-storage-checkup)
- **Focus Areas**: 
  - Multi-site failover
  - VM scenarios
- **Criteria**: All failover and VM scenarios must be validated. (Pass/Fail)
- **Status**: Upcoming.

## Documentation Status Table
| Layer | Status           | Pass/Fail Criteria | 
|-------|------------------|---------------------|
| Layer 0 | Not Implemented | N/A                 |
| Layer 1 | In Progress      | In progress         |
| Layer 2 | Planned          | Pending              |
| Layer 3 | Upcoming         | Pending              |

## Navigation
- **Testing Phase**: Detailed criteria for each layer.
- **Audience**: Developers and Operators.
- **Feature Area**: Core functionality, replication, orchestration, DR.

