# Layer 1 CSI-Addons Spec — VolumeReplication Test Matrix

Written scenarios for the **CSI-Addons Spec track** of Layer 1 (same layer as core CSI E2E; separate until the replication addon-spec is approved into the CSI spec). See [test-layers.md](test-layers.md).

**Executable tests:** [kubernetes-csi-addons `test/e2e/replication/`](https://github.com/nadavleva/kubernetes-csi-addons/tree/main/test/e2e/replication) — `make test-replication-e2e`. Run book: [layer-1-readme.md](layer-1-readme.md). Suite docs: [replication-e2e-suite.md](https://github.com/nadavleva/kubernetes-csi-addons/blob/main/docs/testing/replication-e2e-suite.md).

### Implementation vs this matrix (`test-replication-e2e`)

| Status | IDs |
|--------|-----|
| **Implemented** | E-001…009; DIS-001…006, 009…012; PROM-001…004, 007, 008; DEM-001…004, 007, 008; RSYNC-001…006; INFO-001, 005, 008, 011–014 |
| **Scaffold / skip** (array unreachable, Issues #9/#13) | PROM-005, PROM-006, DEM-005, DEM-006 |
| **Not in suite** | DIS-007, 008, 013–016; PROM-009–013 (Issue #33); INFO-002, 003, 004, 006, 007, 009, 010 as standalone specs |
| **Peer-down** (E-003, DIS-005/006, PROM-003/004, DEM-003/004, RSYNC-003/006) | Implemented via `E2E_FAULT_INJECTOR` (iptables or NetworkFence). Rows below that still say “Not Supported” are **out of date** — the e2e suite is the source of truth. |

---

**Columns:** Test ID, API, Scenario, Role / peer / array, Params, Test Type, Setup, Expected outcome, Notes.

---

## EnableVolumeReplication

| Test ID   | API                    | Scenario                              | Role       | Peer State | Params          | Test Type   | Setup/Input                                    | Expected Outcome                                            | Notes/Link             |
|-----------|------------------------|---------------------------------------|------------|------------|-----------------|-------------|-----------------------------------------------|-------------------------------------------------------------|------------------------|
| L1-E-001  | EnableVolumeReplication| Enable snapshot mode                  | Primary    | Up         | mode=snapshot   | functional  | Volume present, PVC bound, rep. disabled      | VR CR created, status.replicationHandle populated           |                        |
| L1-E-002  | EnableVolumeReplication| Enable journal mode                   | Primary    | Up         | mode=journal    | functional  | Volume present, PVC bound, rep. disabled      | VR CR created, continuous replication active                 |                        |
| L1-E-003  | EnableVolumeReplication| Peer cluster unreachable              | Primary    | Down       | mode=snapshot   | negative    | Peer/all unreachable network                   | Operation fails: timeout, appropriate error in status        | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-E-004  | EnableVolumeReplication| Invalid interval parameter            | Primary    | Up         | interval=5x     | negative    | Bad parameter                                 | Returns gRPC InvalidArgument error                           |                        |
| L1-E-005  | EnableVolumeReplication| Already enabled volume                | Primary    | Up         | (none)          | functional  | VR CR exists, rep enabled already             | Idempotent, operation succeeds with no change                |                        |
| L1-E-006  | EnableVolumeReplication| Secret reference missing/invalid      | Primary    | Up         | secret=missing  | negative    | Bad rep. secret ref                            | gRPC FailedPrecondition error                                |                        |
| L1-E-007  | EnableVolumeReplication| Invalid mirroringMode parameter       | Primary    | Up         | mode=invalid    | negative    | Bad mirroringMode parameter                    | Returns gRPC InvalidArgument error                           |                        |
| L1-E-008  | EnableVolumeReplication| Future schedulingStartTime            | Primary    | Up         | mode=snapshot, startTime=+30s | functional | Valid future start time                        | VR CR created, scheduling starts at specified time          |                        |
| L1-E-009  | EnableVolumeReplication| Invalid schedulingStartTime format    | Primary    | Up         | mode=snapshot, startTime=invalid | negative | Bad time format parameter                      | Returns gRPC InvalidArgument error                           |                        |

**EnableVolumeReplication Test Count: 9 scenarios**

---

## DisableVolumeReplication (all key permutations)

| Test ID   | API                        | Scenario                             | Node Role  | Peer State | Array State | Params       | Test Type   | Setup/Input                                 | Expected Outcome                                     | Notes/Link             |
|-----------|----------------------------|--------------------------------------|------------|------------|-------------|--------------|-------------|----------------------------------------------|------------------------------------------------------|------------------------|
| L1-DIS-001| DisableVolumeReplication   | Disable, active, peer up             | Primary    | Up         | Up          | force=false  | functional  | Rep enabled, all healthy                    | Replication removed, volume writeable                |                        |
| L1-DIS-002| DisableVolumeReplication   | Disable, active, peer up             | Secondary  | Up         | Up          | force=false  | functional  | Rep enabled, all healthy                    | Replication stopped; secondary remains RO            |                        |
| L1-DIS-003| DisableVolumeReplication   | Previously disabled, peer up         | Primary    | Up         | Up          | force=false  | functional  | No replhttps://github.com/nicknevin/aws-ibm-gpfs-playground/blob/nadavclusters/scripts/install-rook-ceph.shication relationship                 | Idempotent, no error                                |                        |
| L1-DIS-004| DisableVolumeReplication   | Previously disabled, peer up         | Secondary  | Up         | Up          | force=false  | functional  | No replication relationship                 | Idempotent, no error                                |                        |
| L1-DIS-005| DisableVolumeReplication   | Peer down, force=false               | Primary    | Down       | Up          | force=false  | negative    | Peer unreachable (simulate network failure) | Fails gracefully, logs/unavailable                   | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-DIS-006| DisableVolumeReplication   | Peer down, force=true                | Primary    | Down       | Up          | force=true   | behavioral  | Peer unreachable, force=true                | Immediate disable, makes primary writeable (warn)    |                        |
| L1-DIS-007| DisableVolumeReplication   | Array unreachable, force=false       | Primary    | Up         | Down        | force=false  | negative    | Disconnect primary array                     | Fails, error code: array unreachable                 | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-DIS-008| DisableVolumeReplication   | Array unreachable, force=true        | Secondary  | Up         | Down        | force=true   | negative    | Disconnect secondary array                   | Fails, error code: array unreachable                 | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |

### DisableVolumeReplication with force=true (Complete Test Matrix)

| Test ID   | API                        | Scenario                                 | Node Role  | Peer State | Array State | Params       | Test Type   | Setup/Input                                 | Expected Outcome                                     | Notes/Link             |
|-----------|----------------------------|------------------------------------------|------------|------------|-------------|--------------|-------------|----------------------------------------------|------------------------------------------------------|------------------------|
| L1-DIS-009| DisableVolumeReplication   | Force disable, active, peer up           | Primary    | Up         | Up          | force=true   | behavioral  | Rep enabled, all healthy, force=true        | Immediate disable, volume writeable, warn logged     |                        |
| L1-DIS-010| DisableVolumeReplication   | Force disable, active, peer up           | Secondary  | Up         | Up          | force=true   | behavioral  | Rep enabled, all healthy, force=true        | Immediate disable, secondary disconnected, warn logged|                      |
| L1-DIS-011| DisableVolumeReplication   | Force disable, previously disabled       | Primary    | Up         | Up          | force=true   | functional  | No replication relationship, force=true     | Idempotent, no error                                |                        |
| L1-DIS-012| DisableVolumeReplication   | Force disable, previously disabled       | Secondary  | Up         | Up          | force=true   | functional  | No replication relationship, force=true     | Idempotent, no error                                |                        |
| L1-DIS-013| DisableVolumeReplication   | Force disable, peer down                 | Primary    | Down       | Up          | force=true   | behavioral  | Peer unreachable, force=true                | Immediate disable, split-brain warning logged       | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-DIS-014| DisableVolumeReplication   | Force disable, peer down                 | Secondary  | Down       | Up          | force=true   | behavioral  | Peer unreachable, force=true                | Emergency disable, cleanup attempted                 | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-DIS-015| DisableVolumeReplication   | Force disable, primary array down        | Primary    | Up         | Down        | force=true   | negative    | Primary array unreachable, force=true       | Still fails, cannot force without array access      | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-DIS-016| DisableVolumeReplication   | Force disable, secondary array down      | Secondary  | Up         | Down        | force=true   | behavioral  | Secondary array unreachable, force=true     | Forced cleanup, metadata inconsistency warnings     | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |

**DisableVolumeReplication Test Count: 16 scenarios (8 force=false + 8 force=true)**

---

## PromoteVolume (Complete Test Matrix)

| Test ID   | API                    | Scenario                                  | Node Role  | Peer State | Array State | Params      | Test Type  | Setup/Input | Expected Outcome                              | Notes/Link |
|-----------|------------------------|-------------------------------------------|------------|------------|-------------|-------------|-----------|-------------|-----------------------------------------------|------------|
| L1-PROM-001| PromoteVolume         | Promote secondary → primary, healthy      | Secondary  | Up         | Up          | force=false | functional| All VRs in sync, healthy                      | VR status.state=Primary, volume RW                  |            |
| L1-PROM-002| PromoteVolume         | Promote already primary, healthy          | Primary    | Up         | Up          | force=false | functional| Volume already primary                        | Idempotent operation, no change                     |            |
| L1-PROM-003| PromoteVolume         | Promote secondary, peer down, force=false | Secondary  | Down       | Up          | force=false | negative  | Primary cluster unreachable, attempt promote   | Fails, split-brain prevention active               | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-PROM-004| PromoteVolume         | Promote secondary, peer down, force=true  | Secondary  | Down       | Up          | force=true  | behavioral| Peer down, force emergency failover           | Promoted, warning about possible data loss          | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-PROM-005| PromoteVolume         | Promote, array unreachable, force=false   | Secondary  | Up         | Down        | force=false | negative  | Secondary array disconnected                   | Fails, cannot access volume for promotion          | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-PROM-006| PromoteVolume         | Promote, array unreachable, force=true    | Secondary  | Up         | Down        | force=true  | negative  | Secondary array disconnected, force attempted  | Still fails, cannot promote without array access   | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-PROM-007| PromoteVolume         | Promote with active I/O workload          | Secondary  | Up         | Up          | force=false | behavioral| Active workload on primary                     | Graceful promotion, I/O redirected                 |            |
| L1-PROM-008| PromoteVolume         | Force promote with active I/O workload    | Secondary  | Up         | Up          | force=true  | behavioral| Active workload, force promotion              | Immediate promotion, potential I/O disruption warning|           |
| L1-PROM-009| PromoteVolume         | Planned failover - graceful promote       | Secondary  | Up         | Up          | force=false, intent=planned | functional | DemoteVolume succeeded on primary first, then promote secondary | Graceful promote succeeds, array knows primary demoted |            |
| L1-PROM-010| PromoteVolume         | Unplanned failover with intent annotation | Secondary  | Down       | Up          | force=false, intent=unplanned | behavioral | Primary cluster down, VR annotated failover-intent=unplanned | Driver returns FailedPrecondition (Ceph-like) or executes unplanned failover (PowerStore-like) |            |
| L1-PROM-011| PromoteVolume         | Unplanned failover with source-fenced     | Secondary  | Down       | Up          | force=false, source-fenced=true | behavioral | Primary fenced, unplanned failover initiated | Driver knows source is fenced, safe to execute unplanned failover |            |
| L1-PROM-012| PromoteVolume         | PowerStore planned failover - graceful path | Secondary | Up         | Up          | force=false, intent=planned | functional | Planned failover on PowerStore, source demoted first | Graceful sync from primary, promote succeeds, auto re-protect initiated |            |
| L1-PROM-013| PromoteVolume         | PowerStore unplanned failover - force path | Secondary | Down       | Up          | force=true, intent=unplanned | behavioral | Unplanned failover on PowerStore, no source coordination | No graceful sync, immediate failover, manual re-protect required later |            |

**PromoteVolume Test Count: 13 scenarios**

---

## DemoteVolume (Complete Test Matrix)

| Test ID   | API                      | Scenario                                    | Node Role   | Peer State | Array State | Params      | Test Type  | Setup/Input  | Expected Outcome                             | Notes/Link |
|-----------|--------------------------|---------------------------------------------|-------------|------------|-------------|-------------|-----------|--------------|----------------------------------------------|------------|
| L1-DEM-001| DemoteVolume             | Demote primary to secondary, healthy        | Primary     | Up         | Up          | force=false | functional| Primary with healthy replication             | VR status.state=Secondary, volume RO         |            |
| L1-DEM-002| DemoteVolume             | Demote already secondary, healthy           | Secondary   | Up         | Up          | force=false | functional| Volume already secondary                     | Idempotent operation, no change              |            |
| L1-DEM-003| DemoteVolume             | Demote primary, peer down, force=false      | Primary     | Down       | Up          | force=false | negative  | Peer unreachable                             | Fails, cannot establish secondary relationship| *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-DEM-004| DemoteVolume             | Demote primary, peer down, force=true       | Primary     | Down       | Up          | force=true  | behavioral| Peer down, force demotion                    | Demoted locally, warning about peer state   | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-DEM-005| DemoteVolume             | Demote, array unreachable, force=false      | Primary     | Up         | Down        | force=false | negative  | Primary array disconnected                   | Fails, cannot access volume for demotion    | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-DEM-006| DemoteVolume             | Demote, array unreachable, force=true       | Primary     | Up         | Down        | force=true  | negative  | Primary array disconnected, force attempted  | Still fails, cannot demote without array access| *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-DEM-007| DemoteVolume             | Demote with active I/O workload, force=false| Primary     | Up         | Up          | force=false | behavioral| Active workload, graceful demotion           | Pending I/O completed, then demoted to RO   |            |
| L1-DEM-008| DemoteVolume             | Force demote with active I/O workload       | Primary     | Up         | Up          | force=true  | behavioral| Active workload, force=true                  | Immediate demotion, pending I/O may be dropped, warning issued |  |

**DemoteVolume Test Count: 8 scenarios**

---

## ResyncVolume

| Test ID   | API                    | Scenario                                      | Node Role | Peer State | Params      | Test Type  | Setup/Input  | Expected Outcome                                  | Notes/Link |
|-----------|------------------------|-----------------------------------------------|-----------|------------|-------------|-----------|--------------|---------------------------------------------------|------------|
| L1-RSYNC-001| ResyncVolume         | Resync secondary after split-brain            | Secondary | Up         | -           | functional| Split-brain resolved                            | Full resync completes, data consistent             |            |
| ...       | ...                    | ...                                           | ...       | ...        | ...         | ...       | ...          | ...                                              | ...        |

**ResyncVolume Test Count: 2+ scenarios (expandable)**

---

## GetVolumeReplicationInfo

| Test ID   | API                        | Scenario                                    | Node Role | Peer State | Array State | Params      | Test Type  | Setup/Input  | Expected Outcome                                  | Notes/Link |
|-----------|----------------------------|---------------------------------------------|-----------|------------|-------------|-------------|-----------|--------------|---------------------------------------------------|------------|
| L1-INFO-001| GetVolumeReplicationInfo  | Query for healthy replication                | Primary   | Up         | Up          | -           | functional| Volume in sync, replication active               | Returns lastSyncTime, status=healthy, replicationHandle | See L1-PROM-002 for related promote scenario |
| L1-INFO-002| GetVolumeReplicationInfo  | Query for healthy replication on secondary   | Secondary | Up         | Up          | -           | functional| Volume in sync, receiving replication            | Returns lastSyncTime, status=healthy, role=secondary    | See L1-DEM-002 for related demote scenario |
| L1-INFO-003| GetVolumeReplicationInfo  | Query during sync operation                  | Primary   | Up         | Up          | -           | functional| Sync in progress                                 | Returns status=syncing, progress percentage             |            |
| L1-INFO-004| GetVolumeReplicationInfo  | Query for degraded replication               | Primary   | Up         | Up          | -           | functional| Network issues, replication lagging              | Returns status=degraded, lastSyncTime old, error details| Related to L1-DIS-005, L1-PROM-003 peer down scenarios |
| L1-INFO-005| GetVolumeReplicationInfo  | Query with peer unreachable                 | Primary   | Down       | Up          | -           | behavioral| Peer cluster unreachable                         | Returns status=disconnected, connection error details   | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-INFO-006| GetVolumeReplicationInfo  | Query for disabled replication               | Primary   | Up         | Up          | -           | functional| Replication disabled                             | Returns status=disabled, no replicationHandle           | See L1-DIS-001, L1-DIS-002 for disable scenarios |
| L1-INFO-007| GetVolumeReplicationInfo  | Query with array unreachable                | Primary   | Up         | Down        | -           | behavioral| Storage array disconnected                        | Returns status=error, array connectivity error details  | *Not Supported - unreachable storage not supported in current K8s CSI tests will be implemented in later stage |
| L1-INFO-008| GetVolumeReplicationInfo  | Query for non-existent volume               | N/A       | Up         | Up          | invalid-vol | negative  | Volume ID that doesn't exist                     | Returns gRPC NotFound error                              |            |
| L1-INFO-009| GetVolumeReplicationInfo  | Query during split-brain condition          | Primary   | Partial    | Up          | -           | behavioral| Split-brain scenario detected                     | Returns status=split-brain, conflict details            | Related to L1-PROM-004, L1-DIS-013 force scenarios |
| L1-INFO-010| GetVolumeReplicationInfo  | Query for never-enabled replication         | Primary   | Up         | Up          | -           | functional| Volume never had replication enabled             | Returns status=not-configured, no replication metadata  |            |
| L1-INFO-011| GetVolumeReplicationInfo  | Query after invalid mirroringMode error     | Primary   | Up         | Up          | -           | functional| Enable failed due to invalid mirroringMode      | Returns status=not-configured, no replication metadata  | See L1-E-007 for related enable error |
| L1-INFO-012| GetVolumeReplicationInfo  | Query after invalid interval parameter error| Primary   | Up         | Up          | -           | functional| Enable failed due to bad interval parameter     | Returns status=not-configured, no replication metadata  | See L1-E-004 for related enable error |
| L1-INFO-013| GetVolumeReplicationInfo  | Query after secret reference error          | Primary   | Up         | Up          | -           | functional| Enable failed due to missing/invalid secret     | Returns status=error, FailedPrecondition details       | See L1-E-006 for related enable error |
| L1-INFO-014| GetVolumeReplicationInfo  | Query after invalid time format error       | Primary   | Up         | Up          | -           | functional| Enable failed due to bad schedulingStartTime    | Returns status=not-configured, no replication metadata  | See L1-E-009 for related enable error |

**GetVolumeReplicationInfo Test Count: 14 scenarios**

*For Volume Group Operations using VolumeReplication gRPC APIs with replicationsource field, see [layer-1-vrg-tests.md](layer-1-vrg-tests.md).*

---

**Total VolumeReplication API Test Count: 62+ scenarios**
- EnableVolumeReplication: 9 scenarios
- DisableVolumeReplication: 16 scenarios  
- PromoteVolume: 13 scenarios (includes intent-aware planned/unplanned failover paths)
- DemoteVolume: 8 scenarios
- ResyncVolume: 2+ scenarios
- GetVolumeReplicationInfo: 14 scenarios

*Peer-down (network partition) is implemented in `test-replication-e2e` via `E2E_FAULT_INJECTOR`. Array/storage unreachable remains scaffolded (Issues #9, #13). Run book: [layer-1-readme.md](layer-1-readme.md).*

---