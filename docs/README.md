# Documentation Index

## Layer 0: Core CSI Certification
- **Description**: External prerequisite not implemented in this project. Core Kubernetes CSI driver conformance testing using the official e2e test framework. Tests run against CSI drivers to validate basic volume lifecycle operations (create, attach, mount, unmount, detach, delete), snapshots, cloning, and resizing functionality. Uses a standardized test suite that executes via external CSI driver sidecar pattern with focus on storage class provisioning and PV/PVC workflows.
- **Technical Stack**: 
  - Go-based e2e tests
  - Ginkgo BDD framework 
  - Gomega matchers
- **Architecture**: 
  - Executed via `kubectl` and CSI external-provisioner/external-attacher sidecars
  - Runs against live Kubernetes clusters
- **References**: 
  - [Kubernetes CSI External Storage Tests](https://github.com/kubernetes/kubernetes/blob/master/test/e2e/storage/external/README.md)
- **Criteria**: Must pass all conformance tests. (Pass/Fail)
- **Status**: Not implemented. 

## Layer 1: CSI Replication Add-on
- **Description**: This is the primary focus of this project. **Optional testing layer** that is only triggered when CSI drivers explicitly advertise replication capability support through CSI driver capability discovery or CRD annotations. Tests validate replication-specific functionality for both individual volumes and volume groups across single and multi-cluster scenarios.
- **Technical Stack**: 
  - Go-based e2e tests
  - Ginkgo BDD framework 
  - Gomega matchers
- **Architecture**: 
  - Executed via `kubectl` and CSI replication sidecars
  - Runs against live Kubernetes clusters with replication-capable CSI drivers
  - Multi-cluster test scenarios with peer connectivity validation
- **Integration Note**: This layer will be incorporated into the main CSI test repository. External teams will fork from this project, and once the CSI replication add-on becomes part of the standard specification, it will be merged upstream.
- **References**:  
  - [CSI Addons Spec: Replication](https://github.com/csi-addons/spec/tree/main/replication)
  - [VolumeGroupReplication CRD API](https://github.com/csi-addons/kubernetes-csi-addons/blob/main/api/replication.storage/v1alpha1/volumegroupreplication_types.go)
  - [Kubevirt Storage Checkup CSI API Summary](https://github.com/nadavleva/kubevirt-storage-checkup/blob/main/docs/csi-addons-replication-api.md)
  - [CSI Addons Volume Group Replication API & Arch](https://github.com/nadavleva/kubevirt-storage-checkup/blob/main/docs/csi-addons-volume-group-replication-api.md)
- **Functionality Covered**: 
  - **VolumeReplication APIs (CSI gRPC)**:
    - EnableVolumeReplication
    - DisableVolumeReplication
    - PromoteVolume
    - DemoteVolume
    - ResyncVolume
    - GetVolumeReplicationInfo
  - **VolumeReplicationGroup APIs (Kubernetes CRD)**:
    - EnableVolumeGroupReplication
    - DisableVolumeGroupReplication
    - PromoteVolumeGroup
    - DemoteVolumeGroup
    - ResyncVolumeGroup
    - GetVolumeGroupReplicationInfo
- **Criteria**: All functionalities must operate correctly. (Pass/Fail)
- **Status**: In progress.

## Layer 2: OCP Platform Orchestration (Single and Two Clusters)
- **Description**: Manage orchestration within single OpenShift cluster and two clusters test flows.
- **Technical Stack**: 
  - Language: Go-based (built into openshift-tests binary)
  - Framework: OpenShift Extended Test Suite with upstream Kubernetes CSI tests
  - Testing Framework: Ginkgo BDD framework with Gomega matchers
  - Container Platform: OpenShift with CSI driver integration
- **Architecture**: 
  - Uses `openshift-tests` binary extracted from OpenShift release images
  - Leverages upstream Kubernetes storage tests with OpenShift-specific additions
  - Runs cluster health monitors during test execution
  - YAML manifest-driven configuration (upstream + OpenShift specific)
- **Key Components**: 
  - `TEST_CSI_DRIVER_FILES`: Upstream test manifest (mandatory)
  - `TEST_OCP_CSI_DRIVER_FILES`: OpenShift-specific test manifest (optional)
  - LUN Stress Test: Validates CSI driver under load (260 Pods by default)
  - Cluster health monitoring during test execution
- **Execution Methods**: 
  - Direct binary execution with `openshift-tests run openshift/csi`
  - Container-based execution using OpenShift release `tests` image
  - Supports dry-run, regex filtering, and single test execution
- **References**: 
  - [OpenShift Origin Storage Tests](https://github.com/openshift/origin)
  - [OpenShift CSI Certification Tests](https://github.com/openshift/origin/tree/main/test/extended/storage/csi)
- **Focus Areas**: 
  - Pod failover
  - VRG management
  - Two cluster test scenarios
- **Criteria**: Must pass designated storage tests. (Pass/Fail)
- **Status**: Planned. 

## Layer 3: Multi-Cluster DR and CNV
- **Description**: Focus on disaster recovery across multiple clusters and Container Native Virtualization (CNV).
- **Technical Stack**: 
  - Language: Go 1.19
  - Framework: Kiagnose checkup engine for Kubernetes health validation
  - Testing Framework: Ginkgo v2 & Gomega for unit/integration tests
  - Container Platform: OpenShift with KubeVirt (CNV) virtualization
- **Architecture**: 
  - Two-tier execution: Host-side orchestration + In-cluster validation Job
  - Kubernetes Job runs actual checkup with comprehensive validation suite
  - Uses ServiceAccount, Role, RoleBinding for RBAC permissions
  - Results stored in ConfigMap for retrieval and analysis
- **Key Dependencies**: 
  - Kubernetes APIs: Core v1, Storage v1, Batch v1, RBAC v1
  - KubeVirt APIs: VirtualMachine, VirtualMachineInstance operations
  - CSI Components: External snapshotter client, VolumeSnapshot APIs
  - CDI Integration: Containerized Data Importer for VM disk management
  - OpenShift APIs: Cluster version detection, OpenShift-specific resources
- **References**: 
  - [RamenDR](https://github.com/ramendb/ramen)
  - [Kubevirt Storage Checkup](https://github.com/kiagnose/kubevirt-storage-checkup)
  - [CSI Tests Documentation & Architecture](https://github.com/nadavleva/kubevirt-storage-checkup/blob/main/docs/csi-tests.md)
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