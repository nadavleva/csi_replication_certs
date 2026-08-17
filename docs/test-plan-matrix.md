# Test Plan Matrix

CSI protocol certification is **one layer** with two spec tracks until the replication addon-spec is approved into the CSI spec. Then those tracks merge. See [test-layers.md](test-layers.md).

| Layer | Track / description | Priority | Order | Documentation | Test cases | Status |
|-------|---------------------|----------|-------|---------------|------------|--------|
| **1** | **CSI Spec** — core volume lifecycle (Kubernetes CSI E2E, csi-sanity) | High | 1 | [CSI spec](https://github.com/container-storage-interface/spec), [external storage tests](https://github.com/kubernetes/kubernetes/tree/master/test/e2e/storage/external) | Upstream CSI e2e | Existing (external) |
| **1** | **CSI-Addons Spec** — replication semantics via VolumeReplication CRs | High | 1 (same layer) | [kubernetes-csi-addons](https://github.com/nadavleva/kubernetes-csi-addons), [layer-1-readme.md](layer-1-readme.md) | [layer-1-vr-tests.md](layer-1-vr-tests.md), [layer-1-test-cases.md](layer-1-test-cases.md) | **Implemented** (`make test-replication-e2e`) |
| **2** | **OCP `openshift/csi`** — upstream External Storage on OpenShift + LUN overflow + clone-larger PVC | Medium | 2 | [origin CSI tests](https://github.com/openshift/origin/tree/main/test/extended/storage/csi) | [layer-2-readme.md](layer-2-readme.md) | Existing (no replication) |
| **3** | **Multi-cluster DR and CNV** — RamenDR, KubeVirt | Medium | 3 | [RamenDR](https://github.com/RamenDR/ramen) | [layer-3-readme.md](layer-3-readme.md) | Upcoming |

Layer 1 tracks run as **one certification layer**. They stay in different repos until replication is in the CSI spec; then the Addons suite merges into CSI E2E.

A replication driver must pass the CSI Spec track **and** the Addons track. After merge, that is a single CSI E2E run with a replication capability.

## Status legend

- **Existing (external)** — upstream CSI tests; not owned here
- **Implemented** — `test-replication-e2e` in kubernetes-csi-addons (gaps: array unreachable, failover intent, VGR matrix)
- **Existing (no replication)** — `openshift/csi` on OCP; does not cover VolumeReplication
- **Planned / Upcoming** — later layers
