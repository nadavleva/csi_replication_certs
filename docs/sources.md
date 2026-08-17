# References

## Layer 1: CSI Driver Protocol Certification

One layer, two spec tracks until the replication addon-spec is approved into the CSI spec. See [test-layers.md](test-layers.md).

### CSI Spec track

- [Kubernetes CSI Specification](https://github.com/container-storage-interface/spec)
- [Kubernetes CSI External Storage Tests](https://github.com/kubernetes/kubernetes/tree/master/test/e2e/storage/external)
- [csi-test](https://github.com/kubernetes-csi/csi-test) (csi-sanity for core CSI)
- Prerequisite for every driver; not implemented in this repo

### CSI-Addons Spec track (`test-replication-e2e`)

- [CSI-Addons specification — Replication](https://github.com/csi-addons/spec/tree/main/replication) — Enable, Disable, Promote, Demote, Resync, GetVolumeReplicationInfo
- [kubernetes-csi-addons](https://github.com/nadavleva/kubernetes-csi-addons) — controller, CRDs, **executable suite**
- [test/e2e/replication](https://github.com/nadavleva/kubernetes-csi-addons/tree/main/test/e2e/replication)
- [replication-e2e-suite.md](https://github.com/nadavleva/kubernetes-csi-addons/blob/main/docs/testing/replication-e2e-suite.md)
- [fault-injection-framework.md](https://github.com/nadavleva/kubernetes-csi-addons/blob/main/docs/testing/fault-injection-framework.md)
- [CSI Replication API summary](https://github.com/nadavleva/kubevirt-storage-checkup/blob/main/docs/csi-addons-replication-api.md)
- Reference backend: Ceph CSI RBD mirroring

## Layer 2: OCP Platform (`openshift/csi`)

Suite docs: [layer-2-readme.md](layer-2-readme.md). Code: [openshift/origin `test/extended/storage/csi`](https://github.com/openshift/origin/tree/main/test/extended/storage/csi).

`openshift-tests run openshift/csi` = **upstream External Storage e2e** (`TEST_CSI_DRIVER_FILES`, required) **plus** OCP suites in that directory:

| Suite | File | When it runs |
|-------|------|----------------|
| SCSI LUN overflow (default 260 pods on one node, serial, 40m) | `scsi_overflow.go` | `TEST_OCP_CSI_DRIVER_FILES` set |
| Clone PVC to a **larger** volume (fs + block) | `pvc_clone_larger.go` | origin `main`; skips without clone capability |

Filter: name contains `External Storage [Driver:` and is not `[Disabled:]` / `[Flaky]` / `[Disruptive]`. Driver must already be installed. **No replication / VolumeReplication tests.**

Related origin tests **outside** this filter: `test/extended/storage/storageclass.go` (ClusterCSIDriver disable StorageClass), `inline.go` (CSI inline admission). KubeVirt storage checkup is a separate Red Hat cert suite.

- [Upstream CSI external tests](https://github.com/kubernetes/kubernetes/blob/master/test/e2e/storage/external/README.md)
- [Red Hat CSI certification workflow](https://docs.redhat.com/en/documentation/red_hat_software_certification/2025/html-single/red_hat_software_certification_workflow_guide/index)

## Layer 3: Multi-Cluster DR and CNV

- [RamenDR](https://github.com/RamenDR/ramen) — DRPolicy, DRPlacementControl
- [KubeVirt Storage Checkup](https://github.com/kiagnose/kubevirt-storage-checkup)
