# Documentation Index

CSI driver protocol tests (core CSI and CSI-Addons replication) are **one certification layer**, split by spec until the replication addon-spec is approved into the CSI spec. Then they merge. See [test-layers.md](test-layers.md).

## Layer 1: CSI Driver Protocol Certification

Two tracks, same layer:

| Track | Spec | Tests | Status |
|-------|------|-------|--------|
| **CSI Spec** | Core CSI | Kubernetes CSI E2E, csi-sanity | Existing prerequisite |
| **CSI-Addons Spec** | Replication addon-spec | `make test-replication-e2e` in kubernetes-csi-addons | **Implemented** (VolumeReplication) |

**Merge:** when the replication addon-spec is approved into the CSI spec, the Addons track joins CSI E2E.

### CSI Spec track

- Volume lifecycle (create, attach, mount, snapshot, clone, expand).
- [Kubernetes CSI External Storage Tests](https://github.com/kubernetes/kubernetes/blob/master/test/e2e/storage/external/README.md)
- Not implemented in this repo.

### CSI-Addons track (primary work in this project)

- Optional: runs when the driver advertises `VOLUME_REPLICATION`.
- Ginkgo e2e against live clusters; VolumeReplication CRs as the gRPC path.
- Enable, Disable, Promote, Demote, Resync, GetVolumeReplicationInfo; Full DR with two kubeconfigs; peer-down via iptables or NetworkFence.
- **Implementation:** [kubernetes-csi-addons `test/e2e/replication/`](https://github.com/nadavleva/kubernetes-csi-addons/tree/main/test/e2e/replication)
- **How to run:** [layer-1-readme.md](layer-1-readme.md)
- **Scenario matrix:** [layer-1-vr-tests.md](layer-1-vr-tests.md)
- **References:** [csi-addons/spec/replication](https://github.com/csi-addons/spec/tree/main/replication)

Volume group **matrix** (replicationsource / VRG) is not in `test-replication-e2e` yet. Generic VGR e2e exists separately in kubernetes-csi-addons. See [layer-1-vrg-tests.md](layer-1-vrg-tests.md).

## Layer 2: OCP Platform Orchestration

- `openshift/csi`: upstream External Storage e2e on OpenShift, plus LUN overflow and clone-to-larger-PVC. **No replication.**
- **Status:** Existing for core CSI on OCP. Replication/VRG/RamenDR not in this suite.
- Details: [layer-2-readme.md](layer-2-readme.md)

## Layer 3: Multi-Cluster DR and CNV

- RamenDR, DRPolicy, DRPlacementControl, KubeVirt/CNV.
- **Status:** Upcoming. Requires Layer 2.
- [layer-3-readme.md](layer-3-readme.md)

## Status

| Layer | Track | Status |
|-------|--------|--------|
| Layer 1 | CSI Spec | Existing (external) |
| Layer 1 | CSI-Addons Spec (`test-replication-e2e`) | Implemented (VR APIs; gaps listed in layer-1-readme) |
| Layer 2 | OCP `openshift/csi` | Existing (no replication) |
| Layer 3 | RamenDR / CNV | Upcoming |

## Navigation

- Architecture: [test-layers.md](test-layers.md)
- Plan matrix: [test-plan-matrix.md](test-plan-matrix.md)
- Sources: [sources.md](sources.md)
