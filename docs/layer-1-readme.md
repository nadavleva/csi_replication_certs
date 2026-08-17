# Layer 1 — CSI-Addons Spec Track

Layer 1 is **CSI driver protocol certification**. This document is the **CSI-Addons Spec track** (replication addon-spec). The **CSI Spec track** (core volume e2e) is upstream Kubernetes CSI tests.

Until the replication addon-spec is **approved into the CSI spec**, the tracks stay in different repos. After approval they **merge** into CSI E2E. Architecture: [test-layers.md](test-layers.md).

This track is **optional**: it runs when the driver advertises `VOLUME_REPLICATION` on `CSIAddonsNode`. Missing capability is a skip / controller error, not a false pass.

## Implementation (executable tests)

**Home:** [kubernetes-csi-addons](https://github.com/nadavleva/kubernetes-csi-addons)  
**Package:** `test/e2e/replication/`  
**Command:** `make test-replication-e2e` or `./hack/run-replication-e2e.sh`  
**Suite docs:** [replication-e2e-suite.md](https://github.com/nadavleva/kubernetes-csi-addons/blob/main/docs/testing/replication-e2e-suite.md)

This repo (`csi_replication_certs`) holds the **written matrix**. The **running suite** is kubernetes-csi-addons — not kubernetes_csiaddontests.

### Path under test

```
Test  →  VolumeReplication / VolumeReplicationClass CR
      →  CSI-Addons controller (VOLUME_REPLICATION capability)
      →  sidecar gRPC  →  CSI driver
      ←  VR status / conditions  (what tests assert)
```

| RPC | How the suite invokes it |
|-----|--------------------------|
| EnableVolumeReplication | Create VR (`replicationState: primary` or `secondary`) |
| DisableVolumeReplication | Delete VR (disable on finalizer) |
| PromoteVolume | Patch `replicationState: primary` |
| DemoteVolume | Patch `replicationState: secondary` |
| ResyncVolume | Patch `replicationState: resync` (controller uses force=true) |
| GetVolumeReplicationInfo | Assert VR status after ops; L1-INFO-008 standalone |

### test-replication-e2e status

| API | IDs | Status |
|-----|-----|--------|
| Enable | L1-E-001 … 009 | Implemented (`enable_volumereplication_test.go`) |
| Disable | L1-DIS-001…006, 009…012 | Implemented (`disable_volumereplication_test.go`) |
| Promote | L1-PROM-001…004, 007, 008 | Implemented; **005/006 scaffold** (array unreachable) |
| Demote | L1-DEM-001…004, 007, 008 | Implemented; **005/006 scaffold** (array unreachable) |
| Resync | L1-RSYNC-001 … 006 | Implemented (`resync_volumereplication_test.go`) |
| GetInfo | INFO-001, 005, 008, 011–014 | Implemented (008 standalone; others with Enable) |
| Full DR smoke | `full_dr_test.go` | Implemented |

**Not in this suite:** DIS-007/008/013–016 (array down); PROM-009–013 (failover intent, Issue #33); VRG matrix ([layer-1-vrg-tests.md](layer-1-vrg-tests.md)). Generic VGR e2e: `make test-e2e-volumegroupreplication` (separate, not the L1 matrix).

~43 specs, ~39 runnable. Written scenarios: [layer-1-vr-tests.md](layer-1-vr-tests.md).

### How to run

```bash
# Clone implementation repo
git clone https://github.com/nadavleva/kubernetes-csi-addons.git
cd kubernetes-csi-addons

# Single cluster (current kubeconfig)
make test-replication-e2e

# Full DR (primary DR1, secondary DR2)
DR1_CONTEXT=dr1 DR2_CONTEXT=dr2 \
REPLICATION_SECRET_NAME=rook-csi-rbd-provisioner \
REPLICATION_SECRET_NAMESPACE=rook-ceph \
make test-replication-e2e

# One spec
GINKGO_FOCUS="L1-E-001" ./hack/run-replication-e2e.sh

make clean-replication-e2e
./hack/diagnose-replication-vr.sh
```

Requires: live cluster, CRDs, CSI-Addons controller, CSI driver with replication (Ceph RBD reference). `USE_EXISTING_CLUSTER=true` is set by the run script. Do not use `make test` (envtest, no real driver).

| Variable | Role | Default |
|----------|------|---------|
| `STORAGE_CLASS` | PVC class | `rook-ceph-block` |
| `CSI_PROVISIONER` | Must match `CSIAddonsNode.spec.driver.name` | `rook-ceph.rbd.csi.ceph.com` |
| `REPLICATION_SECRET_NAME` / `_NAMESPACE` | Driver secret | Per-namespace placeholder |
| `GINKGO_FOCUS` | Spec filter | all |
| `DR1_CONTEXT` / `DR2_CONTEXT` | Full DR | unset (single cluster) |
| `E2E_FAULT_INJECTOR` | `iptables` / `networkfence` / `none` | iptables |
| `REPLICATION_POLL_TIMEOUT` | Seconds to wait Replicating/Completed | 300 |
| `REPLICATION_TEST_TIMEOUT` | Whole suite | 30m |

Logs: `Logs/replication-e2e_<timestamp>.log`. JUnit under `Reports/`.

**Single cluster:** enable, disable-on-primary, INFO-008, idempotent primary.  
**Full DR:** secondary PVC from mirror, promote/demote/resync, peer fence, disable-on-secondary. Unset contexts → those specs skip (`SkipIfNotFullDR`).

Peer-down: iptables DaemonSet (default) or NetworkFence CRs. That is **network** partition, not array unreachable (Issues #9, #13).

## Scenario matrices (this repo)

- Individual volumes: [layer-1-vr-tests.md](layer-1-vr-tests.md)
- Volume groups: [layer-1-vrg-tests.md](layer-1-vrg-tests.md) (not yet in `test-replication-e2e`)
- Summary: [layer-1-test-cases.md](layer-1-test-cases.md)

## RPCs covered

Enable, Disable, Promote, Demote, Resync, GetVolumeReplicationInfo. Group ops use the same RPCs with `replicationsource` (matrix only; e2e pending).

## Parameters (driver / VRC)

| Parameter | Values | Used in |
|-----------|--------|---------|
| mirroringMode | snapshot, journal | Enable |
| schedulingInterval | e.g. 1m, 1h | Enable (snapshot) |
| schedulingStartTime | ISO-8601 | Enable |
| force | true / false | Disable, Promote, Demote |
| replicationsource | group id | Group RPCs (future e2e) |

## Pass / fail

- Assertions on VR `Status.State` and conditions (`Replicating`, `Completed`, `Degraded`).
- No false fail when replication is not advertised.
- Full DR / fence specs skip with a reason when the environment cannot run them.

## Other suites in kubernetes-csi-addons

| Command | Role |
|---------|------|
| `make test-replication-e2e` | This track (L1-* matrix) |
| `make test-e2e-volumereplication` | Feature smoke |
| `make test-e2e-volumegroupreplication` | VGR CR lifecycle (not L1 VRG matrix) |
| `make test` | Unit / envtest, fake gRPC |
