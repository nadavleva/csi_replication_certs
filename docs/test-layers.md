# 4-Layer Architecture for CSI Replication

## Layer 0: Core CSI Certification
- **Description**: An external prerequisite involving Kubernetes CSI conformance tests.
- **Status**: **Prerequisite** - Standard Kubernetes CSI Storage test suite validation

## Layer 1: CSI Replication Add-on
- **Focus**: Extended Kubernetes CSI Storage tests with replication add-on functionality
- **Implementation**: [kubernetes_csiaddontests](https://github.com/nadavleva/kubernetes_csiaddontests) (fork of kubernetes/kubernetes)
- **Status**: **Active Development** - Core APIs implemented, full suite in progress

### Architecture Integration
```
Test Code → Kubernetes API (CRs) → Kubernetes Components → gRPC → CSI Driver
```

Where:
- **Test Code**: Extended Ginkgo/Gomega test framework
- **Kubernetes API**: VolumeReplication, VolumeReplicationClass custom resources  
- **Kubernetes Components**: CSI external components with replication add-on support
- **gRPC**: CSI Replication Add-on gRPC calls
- **CSI Driver**: Storage driver with replication capabilities

### Technical Implementation

#### **Test Framework Components**
- **Main Test Suite** (`replication.go`): EnableVolumeReplication and GetVolumeReplicationInfo validation
- **Mock Tests** (`csi_replication.go`): Protocol validation with extensive debug logging
- **Unit Tests** (`replication_unit_test.go`): Standalone parameter validation tests
- **Framework Integration**: Added CapReplication capability to testdriver.go

#### **Build Infrastructure** 
- **Make Targets**: `replication-build`, `replication-lint`, `replication-test`, `replication-all`
- **E2E Scripts**: Automated test execution with `hack/replication-e2e.sh`
- **Quick Start**: Developer guidance with `hack/replication-quick-start.sh`

#### **Testing Modes**
- **Main Tests**: Real CSI driver certification (requires cluster + driver)
- **Mock Tests**: Protocol validation (standalone, no external dependencies)
- **Registration-Based**: Uses Kubernetes e2e import-based test discovery
- **Capability Driven**: Tests automatically skip if driver lacks replication support

### Local Development Environment

#### **Phase 1: Local Ceph Cluster Integration** (Current Sprint)
Infrastructure:
- **Primary Cluster**: Minikube with Ceph RBD CSI
- **Secondary Cluster**: Minikube with Ceph RBD CSI  
- **Storage Backend**: Local Ceph cluster (containerized)
- **Replication**: Ceph RBD mirroring between clusters

Setup Reference: [SetupCSICluster.md](https://github.com/nadavleva/ramen/blob/playground-csi-replication/docs/testing/SetupCSICluster.md)

#### **Test Scenarios with Local Ceph**
1. **Cross-Cluster Volume Replication**: Validate RBD mirroring between local clusters
2. **Disaster Recovery**: Test complete failover scenarios with real applications
3. **Data Consistency**: Verify data integrity during replication operations
4. **Performance Impact**: Measure replication overhead on application performance
5. **Network Resilience**: Test behavior during simulated network partitions

### References
- [csi-addons/spec/replication](https://github.com/csi-addons/spec/tree/main/replication)
- [kubevirt-storage-checkup CSI API Summary](https://github.com/nadavleva/kubevirt-storage-checkup/blob/main/docs/csi-addons-replication-api.md)
- [kubernetes_csiaddontests PR #1](https://github.com/nadavleva/kubernetes_csiaddontests/pull/1)
- [Build Guide](https://github.com/nadavleva/kubernetes_csiaddontests/pull/docs/replication-testing-guide.md)
- [Test Specifications](https://github.com/nadavleva/kubernetes_csiaddontests/pull/test/e2e/storage/testsuites/REPLICATION.md)

## Layer 2: OCP Platform Orchestration
- **Overview**: Management within a single cluster utilizing VRG (Volume Replication Group).
- **Status**: **Planned** - Depends on Layer 1 completion
- **Focus Areas**:
  - Pod failover and recovery
  - OpenShift integration and validation
  - VRG custom resource lifecycle management
  - Single-cluster disaster recovery scenarios

## Layer 3: Multi-Cluster DR and CNV
- **Technologies**: RamenDR for multi-cluster orchestration and Container-Native Virtualization.
- **Status**: **Future Phase** - Depends on Layer 2 validation
- **Key Components**:
  - **DRPolicy**: Define disaster recovery policies across clusters
  - **DRPlacementControl**: Control placement and failover of applications
  - **VM failover**: Virtual machine disaster recovery scenarios
  - **Integration with kubevirt-storage-checkup**: Storage validation for CNV workloads

## Implementation Timeline

### **Current Sprint** (Layer 1 - Active Development)
- EnableVolumeReplication and GetVolumeReplicationInfo APIs implemented
- Local Ceph cluster integration testing
- Complete CSI Replication API implementation (remaining 6 APIs)
- Build infrastructure and automation completion

### **Next 2-4 weeks** (Layer 1 - Completion)
- DisableVolumeReplication, PromoteVolume, DemoteVolume implementation
- ResyncVolume and GetVolumeReplicationCapabilities implementation  
- Volume Group Replication tests completion
- Advanced error handling and edge case testing
- Community review and feedback integration

### **Medium Term** (Layer 2 & 3 - Planning)
- Layer 2: VRG orchestration testing framework design
- Layer 3: Multi-cluster RamenDR integration planning
- CNCF CSI certification workflow integration

## Testing Strategy

### **Dual Testing Approach**
- **Protocol Validation**: Mock tests for gRPC API compliance (no cluster required)
- **Integration Testing**: Real CSI driver certification with local Ceph clusters
- **Certification Testing**: Complete driver validation against test matrices

### **Development Environment**
- **Reproducible Setup**: Local containerized Ceph clusters
- **Cost Effective**: No cloud infrastructure dependency
- **Rapid Iteration**: Quick setup/teardown for development cycles
- **Offline Capable**: Full testing without internet connectivity

## Dependencies and Validation Criteria

### **Layer Dependencies**
- **Layer 1** → Layer 0: Requires standard Kubernetes CSI Storage test certification
- **Layer 2** → Layer 1: Requires complete CSI Replication Add-on API validation  
- **Layer 3** → Layer 2: Requires single-cluster VRG orchestration validation

### **Pass/Fail Criteria**

#### **Layer 1 Validation Requirements**
- **API Compliance**: All 8 CSI Replication gRPC APIs pass protocol validation
- **Parameter Validation**: StorageClass replication parameters correctly processed
- **Error Handling**: Graceful handling of invalid requests and network failures
- **Idempotency**: Repeated calls produce consistent results
- **Capability Detection**: Tests skip gracefully when driver lacks replication support
- **Integration**: Successful operation with real storage backend (Ceph RBD)

#### **Performance Benchmarks**
- **Build Validation**: Complete compilation and integration checks via `make replication-all`
- **Protocol Tests**: Mock validation benchmarks for gRPC call overhead
- **Data Integrity**: Replication consistency validation across storage operations
- **Recovery Time**: Failover and recovery time measurements

## Official References and Standards

### **Authoritative Sources**
- **CSI Specification**: [Container Storage Interface](https://github.com/container-storage-interface/spec)
- **CSI Replication Add-on**: [csi-addons/spec/replication](https://github.com/csi-addons/spec/tree/main/replication)
- **Kubernetes CSI Tests**: [kubernetes/kubernetes storage tests](https://github.com/kubernetes/kubernetes/tree/master/test/e2e/storage)
- **Test Implementation**: [kubernetes_csiaddontests](https://github.com/nadavleva/kubernetes_csiaddontests)

### **Implementation Documentation**
- **Build Guide**: [Replication Testing Guide](https://github.com/nadavleva/kubernetes_csiaddontests/pull/docs/replication-testing-guide.md)
- **Technical Specifications**: [REPLICATION.md](https://github.com/nadavleva/kubernetes_csiaddontests/pull/test/e2e/storage/testsuites/REPLICATION.md)
- **Architecture Guide**: [README-replication.md](https://github.com/nadavleva/kubernetes_csiaddontests/pull/test/e2e/storage/testsuites/README-replication.md)
- **Test Matrices**: [Layer 1 Test Cases](layer-1-test-cases.md) and [Test Plan Matrix](test-plan-matrix.md)

## Current Implementation Status

Based on [PR #1](https://github.com/nadavleva/kubernetes_csiaddontests/pull/1) in the kubernetes_csiaddontests repository:

### **Completed APIs**
- **EnableVolumeReplication** 
  - Snapshot mode replication [L1-E-001]
  - Journal mode replication [L1-E-002] 
  - Idempotent operations [L1-E-005]
- **GetVolumeReplicationInfo**
  - Healthy replication status [L1-INFO-001]
  - Non-existent volume handling [L1-INFO-008]

### **Planned APIs** (Next Sprint)
- **DisableVolumeReplication** - Disable replication for specific volumes [L1-D-001 to L1-D-003]
- **PromoteVolume** - Promote secondary volume to primary (disaster recovery) [L1-P-001 to L1-P-005]
- **DemoteVolume** - Demote primary volume to secondary [L1-DM-001 to L1-DM-003]
- **ResyncVolume** - Force resynchronization between primary and secondary [L1-R-001 to L1-R-004]
- **GetVolumeReplicationCapabilities** - Query driver replication capabilities [L1-CAP-001 to L1-CAP-002]
- **Volume Group Replication** - Enable/disable/modify volume group replication [L1-GRP-001 to L1-GRP-006]

---

> **Note**: This architecture implements a comprehensive CSI replication certification framework, starting with protocol-level validation (Layer 1) and building toward full multi-cluster disaster recovery orchestration (Layer 3). The current implementation establishes the foundation for complete CSI driver replication compliance testing.