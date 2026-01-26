# Layer-1 CSI Replication Add-on Test Matrix: Full Expanded Enumeration

This file fully enumerates all endpoint, state, and workflow-driven scenarios for Layer-1 CSI Replication driver conformance.  
It is intended for use by certification tools, automation, and test writers.

**Columns:**
- Test ID
- API (gRPC/CRD)
- Scenario/Description
- Node Role / Cluster State / Peer State / S3 State
- Parameters (e.g., force)
- Test Type (functional, negative, behavioral, API, performance)
- Input/Setup Steps
- Expected Result/Pass Criteria
- Notes/Automation Link/Reference

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

**PromoteVolume Test Count: 8 scenarios**

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

| Test ID   | API                        | Scenario                                    | Node Role | Peer State | Params      | Test Type  | Setup/Input  | Expected Outcome                                  | Notes/Link |
|-----------|----------------------------|---------------------------------------------|-----------|------------|-------------|-----------|--------------|---------------------------------------------------|------------|
| L1-INFO-001| GetVolumeReplicationInfo  | Query for healthy replication                | Primary   | Up         | -           | functional| Volume in sync                                   | Returns lastSyncTime, status=healthy               |            |
| ...       | ...                        | ...                                         | ...       | ...        | ...         | ...       | ...          | ...                                              | ...        |

**GetVolumeReplicationInfo Test Count: 2+ scenarios (expandable)**

*For Volume Group Operations using VolumeReplication gRPC APIs with replicationsource field, see [layer-1-vrg-tests.md](layer-1-vrg-tests.md).*

---

**Total VolumeReplication API Test Count: 45+ scenarios**
- EnableVolumeReplication: 9 scenarios
- DisableVolumeReplication: 16 scenarios  
- PromoteVolume: 8 scenarios
- DemoteVolume: 8 scenarios
- ResyncVolume: 2+ scenarios
- GetVolumeReplicationInfo: 2+ scenarios

*Note: Tests marked with "Not Supported" involve unreachable storage/cluster scenarios that are not supported in the current Kubernetes CSI test framework and will be implemented in later stage. See [disruptive tests documentation](https://github.com/nadavleva/kubernetes_csiaddontests/blob/docs/storage-test-framework/test/e2e/storage/README.md#disruptive-tests) for details.*

---