# CSI Replication Certification Layers

CSI driver protocol tests (core CSI and CSI-Addons replication) sit in **one layer**. They are **separated by spec** until the replication addon-spec is approved into the CSI spec, then they merge.

Orchestration and DR remain later layers.

```
Layer 1  CSI driver protocol certification
         ├── CSI Spec track      Kubernetes CSI E2E / csi-test
         └── CSI-Addons track    make test-replication-e2e  (until merge)
                    │
                    │  when replication addon-spec is approved into CSI spec
                    ▼
         one CSI E2E suite (replication tests join core storage tests)

Layer 2  OCP / platform orchestration
Layer 3  Multi-cluster DR (RamenDR) and CNV
```

---

## Layer 1: CSI Driver Protocol Certification

**One layer.** Both tracks certify **driver protocol and semantics** (not operators, not RamenDR).

They stay **separated** only because replication is still an **addon-spec**, not the **CSI spec**.

| Track | Spec | What it certifies | Where tests live | Status |
|-------|------|-------------------|------------------|--------|
| **CSI Spec** | [CSI spec](https://github.com/container-storage-interface/spec) | Volume lifecycle: create, attach, mount, snapshot, clone, expand | Kubernetes CSI E2E, csi-sanity | Existing prerequisite |
| **CSI-Addons Spec** | [csi-addons/spec/replication](https://github.com/csi-addons/spec/tree/main/replication) | Enable / Disable / Promote / Demote / Resync / GetInfo via VolumeReplication CRs | [kubernetes-csi-addons](https://github.com/nadavleva/kubernetes-csi-addons) `test/e2e/replication/` | **Implemented** (`make test-replication-e2e`) |

### Why the same layer

- Same job: prove the **driver** implements the contract.
- Same style: Ginkgo e2e against a live cluster and a real CSI driver.
- Same skip rule: do not fail drivers that do not advertise the feature.
- Capability check for replication is part of the **Addons track**, not a separate layer.

### Why they stay separated for now

- Replication is **not** in the core CSI spec yet ([csi-test#583](https://github.com/kubernetes-csi/csi-test/issues/583)).
- Maintainer guidance (Jan Safranek): do not put addon tests in core **csi-test** until the spec belongs there.
- Addons tests need VolumeReplication CRDs, the CSI-Addons controller, sidecar, and optional NetworkFence / two kubeconfigs.

### Merge (after addon-spec approval)

When the replication addon-spec is **approved into the CSI spec**:

1. Replication RPCs become part of the CSI contract (optional capability, same as snapshots were).
2. The Addons-track suite **merges** into Kubernetes CSI E2E / csi-test.
3. Layer 1 is then a **single** CSI Spec track. The Addons split goes away.

Until that approval, run **both** tracks for a driver that claims replication.

### CSI Spec track (existing)

- Kubernetes storage e2e (`test/e2e/storage/external`).
- csi-sanity for isolated gRPC of **core** CSI.
- Not implemented in this repo. Drivers must already pass this.

### CSI-Addons track — `test-replication-e2e` (this project)

**Run:**

```bash
make test-replication-e2e
# or
./hack/run-replication-e2e.sh
```

**Repo:** [nadavleva/kubernetes-csi-addons](https://github.com/nadavleva/kubernetes-csi-addons)  
**Package:** `test/e2e/replication/`  
**Docs:** [replication-e2e-suite.md](https://github.com/nadavleva/kubernetes-csi-addons/blob/main/docs/testing/replication-e2e-suite.md)

**How it works:** tests create VolumeReplication / VolumeReplicationClass CRs. The controller checks `VOLUME_REPLICATION` on `CSIAddonsNode`, then calls Enable / Disable / Promote / Demote / Resync / GetInfo. Tests assert CR status and conditions (vendor-agnostic).

**Current status (from the test files):**

| API | Specs | Status |
|-----|-------|--------|
| EnableVolumeReplication | L1-E-001 … 009 | Implemented |
| DisableVolumeReplication | L1-DIS-001…006, 009…012 | Implemented |
| PromoteVolume | L1-PROM-001…004, 007, 008 | Implemented |
| DemoteVolume | L1-DEM-001…004, 007, 008 | Implemented |
| ResyncVolume | L1-RSYNC-001 … 006 | Implemented |
| GetVolumeReplicationInfo | INFO-001/005/008/011–014 | Implemented (mostly folded into Enable) |
| Full DR smoke | 1 spec | Implemented |
| Array unreachable | PROM-005/006, DEM-005/006 | Scaffold / skip (Issues #9, #13) |
| Failover intent | PROM-009–013 | Not in suite (Issue #33) |
| Volume group matrix | layer-1-vrg-tests.md | Not in this suite (generic VGR e2e is separate) |

~43 Ginkgo specs; ~39 runnable; 4 scaffolds. Full DR mode uses `DR1_CONTEXT` + `DR2_CONTEXT`. Peer-down uses `E2E_FAULT_INJECTOR` (`iptables` default, `networkfence`, `none`).

Scenario IDs: [layer-1-vr-tests.md](layer-1-vr-tests.md). How to run and env vars: [layer-1-readme.md](layer-1-readme.md).

---

## Layer 2: OCP / Platform (`openshift/csi`)

- **What exists:** [origin `test/extended/storage/csi`](https://github.com/openshift/origin/tree/main/test/extended/storage/csi) — `openshift-tests run openshift/csi`. Re-runs **upstream External Storage** tests on OpenShift and adds **LUN overflow** (260 pods / one node) and **clone-to-larger-PVC**. See [layer-2-readme.md](layer-2-readme.md).
- **Status:** Existing for core CSI on OCP. Does **not** cover replication, VRG, or RamenDR.
- **Not the same as** Layer 1 Full DR mode (two clusters, driver promote/demote).

---

## Layer 3: Multi-Cluster DR and CNV

- **Focus:** RamenDR (DRPolicy, DRPlacementControl), app/VM failover, KubeVirt.
- **Status:** Upcoming. Depends on Layer 2.

See [layer-3-readme.md](layer-3-readme.md).

---

## Dependencies

```
Layer 1 CSI Spec track     →  required for every CSI driver
Layer 1 CSI-Addons track   →  required if the driver advertises replication
Layer 2                    →  requires Layer 1
Layer 3                    →  requires Layer 2
```

After spec merge, Layer 1 is a single CSI E2E run (core + replication capability).

---

## Pass / fail (Layer 1 Addons track)

- Capability missing: skip or controller error — **not** a false pass.
- Implemented L1-* specs pass on a live driver (Ceph RBD is the reference).
- Idempotency and error cases match the matrix.
- Full DR specs skip cleanly if `DR1_CONTEXT` / `DR2_CONTEXT` are unset.

---

## References

- [CSI spec](https://github.com/container-storage-interface/spec)
- [csi-addons/spec/replication](https://github.com/csi-addons/spec/tree/main/replication)
- [kubernetes-csi-addons](https://github.com/nadavleva/kubernetes-csi-addons)
- [Kubernetes CSI storage tests](https://github.com/kubernetes/kubernetes/tree/master/test/e2e/storage)
- [csi-test#583](https://github.com/kubernetes-csi/csi-test/issues/583)
