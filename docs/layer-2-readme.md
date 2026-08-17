# Layer 2: OCP Platform Certification

**Status:** Existing for core CSI on OpenShift (`openshift/csi`). Replication / VRG / RamenDR are **not** in this suite.

Layer 2 is **platform** certification: an already-installed CSI driver on OpenShift, using `openshift-tests run openshift/csi`. It is **not** Layer 1 Full DR mode (two kubeconfigs, driver promote/demote) and **not** Layer 3 (RamenDR).

Primary source: [openshift/origin `test/extended/storage/csi`](https://github.com/openshift/origin/tree/main/test/extended/storage/csi) ([README](https://github.com/openshift/origin/blob/main/test/extended/storage/csi/README.md)).

---

## What `openshift/csi` actually runs

The suite **extends** Kubernetes CSI e2e; it does not replace it.

```
openshift/csi
  = upstream External Storage tests  (TEST_CSI_DRIVER_FILES — required)
  + OpenShift CSI suites registered into the same CSISuites list
```

Selection (`openshift/csi` in origin `pkg/testsuites/standard_suites.go`):

- Include names containing `External Storage [Driver:`
- Exclude `[Disabled:]`, `[Flaky]`, `[Disruptive]`

Init (`pkg/clioptions/clusterdiscovery/csi.go`): load `TEST_OCP_CSI_DRIVER_FILES` first (`AddOpenShiftCSITests` appends OCP suites to `testsuites.CSISuites`), then `TEST_CSI_DRIVER_FILES` (`external.AddDriverDefinition`). The OCP driver name must match the upstream manifest.

### 1. Upstream External Storage (bulk of the suite)

Driven by the **upstream** YAML (`TEST_CSI_DRIVER_FILES`). Format: [Kubernetes CSI external tests](https://github.com/kubernetes/kubernetes/blob/master/test/e2e/storage/external/README.md). Capabilities in that file decide which Ginkgo specs run vs skip.

Typical coverage (names look like `External Storage [Driver: <name>] [Testpattern: …]`):

| Area | Examples |
|------|----------|
| Dynamic PV | Store data on default fs / ext4 / xfs (and ntfs if advertised) |
| Pre-provisioned PV | Filesystem and block |
| Expand | Online resize while pod is using the volume; reject expand when not allowed |
| Snapshots | Create snapshot; restore |
| Multi-volume | Two volumes, same node / different node, data retained across pod recreate |
| Stress (upstream) | Many pods: attach / publish / unpublish / detach |

This is **Layer 1 CSI Spec track** run **on OpenShift**, plus cluster health monitors that `openshift-tests` starts before any spec.

### 2. OpenShift CSI suites in this directory

These are extra `storageframework.TestSuite` implementations. They still show up as `External Storage [Driver: …]` so they pass the suite filter.

#### SCSI LUN overflow (`scsi_overflow.go`)

Registered only when `TEST_OCP_CSI_DRIVER_FILES` is set (`AddOpenShiftCSITests`).

```yaml
Driver: <CSI driver name>
LUNStressTest:
  PodsTotal: 260   # 0 disables the test
  Timeout: "40m"
```

**Spec:** `OpenShift CSI extended - SCSI LUN Overflow should use many PVs on a single node [Serial][Timeout:40m]`

**What it does:**

1. Picks one ready, schedulable node.
2. Creates a dynamic StorageClass from the driver.
3. Creates **PodsTotal** PVCs + pods **at once**, all pinned to that node (default 260).
4. Each pod mounts its PVC, runs `ls` on the mount, and exits (`Succeeded`).
5. Waits until **every** pod succeeds (default 40m). Serial: nothing else runs in parallel.

**What it is not:** 260 pods running at once. Attach limit (`CSINode`) should cap concurrency; sidecars retry on timeout. Scheduler can still overshoot attach limit ([kubernetes#126502](https://github.com/kubernetes/kubernetes/issues/126502)); the driver must return a sane error from `ControllerPublish` / `NodeStage` / `NodePublish`.

**Why 257+:** RHCOS / SCSI LUN numbering historically broke above 256. The test is still useful for non-SCSI drivers: attach limit + load + full provision/attach/mount/unmount/detach/delete of hundreds of volumes.

#### Clone to a larger PVC (`pvc_clone_larger.go`, origin `main`)

Always-on OCP suite when registered (`RegisterAlwaysOnCSISuites` on current origin `main`). Skips if the driver lacks `CapPVCDataSource` (and block/fs-resize caps as needed).

**Spec:** `OpenShift CSI extended - CSI Clone should provision volume with pvc data source larger than original volume`

**What it does:** write data on a source PVC, clone via `dataSourceRef` to a claim **1Gi larger**, wait for the source VolumeAttachment to terminate, then check the clone has the data and the larger size. Patterns: filesystem dynamic PV and raw block dynamic PV. Pins topology when the driver advertises topology keys.

Local `sources/origin` may predate this file; treat [origin `main`](https://github.com/openshift/origin/tree/main/test/extended/storage/csi) as current.

### 3. Related origin storage tests **not** in this folder / filter

These live under `test/extended/storage/` but **do not** match `External Storage [Driver:`, so they are **not** part of `openshift/csi`:

| Test | File | What |
|------|------|------|
| `[Feature:DisableStorageClass]` | `storageclass.go` | ClusterCSIDriver `storageClassState` disable/enable |
| `[Feature:CSIInlineVolumeAdmission]` | `inline.go` | Admit/reject CSI inline volume pods |

Red Hat CSI certification also requires **KubeVirt storage checkup** (VM workloads). That is a **separate** job, closer to Layer 3 / CNV, not this directory.

---

## What this suite does **not** test

- CSI Replication (Enable/Promote/Demote/Resync) or VolumeReplication CRs
- RamenDR, DRPolicy, two-cluster failover
- OLM install/upgrade of a vendor operator (assumes the driver is **already installed**)

That is why Layer 1 Addons (`test-replication-e2e`) and Layer 3 still exist.

---

## How to run

Use the **`openshift-tests` binary that matches the cluster version**.

```bash
export KUBECONFIG=/path/to/kubeconfig
export TEST_CSI_DRIVER_FILES=upstream-manifest.yaml          # required
export TEST_OCP_CSI_DRIVER_FILES=ocp-manifest.yaml           # optional; enables LUN stress
openshift-tests run openshift/csi |& tee test.log
```

```bash
openshift-tests run openshift/csi --dry-run
openshift-tests run openshift/csi --run='LUN Overflow'
openshift-tests run-test 'External Storage [Driver: …] …'   # exact --dry-run name, no monitors
```

From the release `tests` image (`oc adm release info --image-for=tests`):

```bash
podman run -v "$(pwd):/data:z" --rm -it "$(oc adm release info --image-for=tests)" \
  sh -c 'KUBECONFIG=/data/kubeconfig.yaml TEST_CSI_DRIVER_FILES=/data/upstream-manifest.yaml TEST_OCP_CSI_DRIVER_FILES=/data/ocp-manifest.yaml /usr/bin/openshift-tests run openshift/csi --junit-dir /data/results'
```

`openshift-tests` starts cluster-health **monitors** before specs; they write many files in the current directory.

Official submission: [Red Hat Software Certification Workflow Guide](https://docs.redhat.com/en/documentation/red_hat_software_certification/2025/html-single/red_hat_software_certification_workflow_guide/index) (CSI tests). The origin README is for debugging, not the supported cert process.

---

## Prerequisites (for this suite)

- OpenShift cluster, cluster-admin kubeconfig
- CSI driver **already installed**
- Worker capacity for LUN stress (260+ volumes if enabled)
- StorageClass / VolumeSnapshotClass as required by the upstream manifest

Layer 1 (CSI Spec track, and Addons track if the driver replicates) should pass before treating OCP CSI cert as complete for a replication driver.

---

## References

- [origin `test/extended/storage/csi`](https://github.com/openshift/origin/tree/main/test/extended/storage/csi)
- [Upstream CSI external README](https://github.com/kubernetes/kubernetes/blob/master/test/e2e/storage/external/README.md)
- [test-layers.md](test-layers.md)
