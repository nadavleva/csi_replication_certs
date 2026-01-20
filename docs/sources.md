# References

## Layer 0: Core CSI Certification (Prerequisite)
- [Kubernetes CSI Specification](https://github.com/container-storage-interface/spec)
- [Kubernetes CSI External Storage Tests](https://github.com/kubernetes/kubernetes/tree/master/test/e2e/storage/external)
- CSI Test Driver documentation and examples
- Note: These are prerequisites, not implemented in this project

## Layer 1: CSI Replication Add-on (PRIMARY PROJECT FOCUS)
- [CSI Add-ons Specification - Replication](https://github.com/csi-addons/spec/tree/main/replication)
  * Complete protobuf definitions for replication RPCs
  * EnableVolumeReplication, DisableVolumeReplication, PromoteVolume, DemoteVolume, ResyncVolume, GetVolumeReplicationInfo
- [CSI Replication Add-on API Summary](https://github.com/nadavleva/kubevirt-storage-checkup/blob/main/docs/csi-addons-replication-api.md)
  * Workflow examples
  * VolumeReplication and VolumeReplicationClass CRD documentation
  * Replication modes and error handling
- [CSI Add-ons Kubernetes Integration](https://github.com/csi-addons/kubernetes-csi-addons)
- Reference implementations: Ceph CSI RBD mirroring examples

## Layer 2: OCP Platform Orchestration (Single Cluster)
- [OpenShift Origin Storage Tests](https://github.com/openshift/origin/tree/master/test/extended/storage/csi)
- OpenShift Storage Operators documentation
- VolumeReplicationGroup (single cluster) examples from OpenShift Data Foundation
- OpenShift CSI certification requirements

## Layer 3: Multi-Cluster DR & CNV Application Virtualization
- [RamenDR Project](https://github.com/RamenDR/ramen)
  * DRPolicy and DRPlacementControl API documentation
  * Multi-cluster orchestration architecture
  * Hub-and-spoke deployment patterns
- [KubeVirt Storage Checkup](https://github.com/kiagnose/kubevirt-storage-checkup)
  * VM storage validation framework
  * VM boot and migration test scenarios
  * Data consistency checks for VMs
- OpenShift Virtualization (CNV) documentation
- Multi-cluster failover workflow examples
