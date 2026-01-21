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
| L1-E-003  | EnableVolumeReplication| Peer cluster unreachable              | Primary    | Down       | mode=snapshot   | negative    | Peer/all unreachable network                   | Operation fails: timeout, appropriate error in status        |                        |
| L1-E-004  | EnableVolumeReplication| Invalid interval parameter            | Primary    | Up         | interval=5x     | negative    | Bad parameter                                 | Returns gRPC InvalidArgument error                           |                        |
| L1-E-005  | EnableVolumeReplication| Already enabled volume                | Primary    | Up         | (none)          | functional  | VR CR exists, rep enabled already             | Idempotent, operation succeeds with no change                |                        |
| L1-E-006  | EnableVolumeReplication| Secret reference missing/invalid      | Primary    | Up         | secret=missing  | negative    | Bad rep. secret ref                            | gRPC FailedPrecondition error                                |                        |

---

## DisableVolumeReplication (all key permutations)

| Test ID   | API                        | Scenario                             | Node Role  | Peer State | Array State | Params       | Test Type   | Setup/Input                                 | Expected Outcome                                     | Notes/Link             |
|-----------|----------------------------|--------------------------------------|------------|------------|-------------|--------------|-------------|----------------------------------------------|------------------------------------------------------|------------------------|
| L1-DIS-001| DisableVolumeReplication   | Disable, active, peer up             | Primary    | Up         | Up          | force=false  | functional  | Rep enabled, all healthy                    | Replication removed, volume writeable                |                        |
| L1-DIS-002| DisableVolumeReplication   | Disable, active, peer up             | Secondary  | Up         | Up          | force=false  | functional  | Rep enabled, all healthy                    | Replication stopped; secondary remains RO            |                        |
| L1-DIS-003| DisableVolumeReplication   | Previously disabled, peer up         | Primary    | Up         | Up          | force=false  | functional  | No replication relationship                 | Idempotent, no error                                |                        |
| L1-DIS-004| DisableVolumeReplication   | Previously disabled, peer up         | Secondary  | Up         | Up          | force=false  | functional  | No replication relationship                 | Idempotent, no error                                |                        |
| L1-DIS-005| DisableVolumeReplication   | Peer down, force=false               | Primary    | Down       | Up          | force=false  | negative    | Peer unreachable (simulate network failure) | Fails gracefully, logs/unavailable                   |                        |
| L1-DIS-006| DisableVolumeReplication   | Peer down, force=true                | Primary    | Down       | Up          | force=true   | behavioral  | Peer unreachable, force=true                | Immediate disable, makes primary writeable (warn)    |                        |
| L1-DIS-007| DisableVolumeReplication   | Array unreachable, force=false       | Primary    | Up         | Down        | force=false  | negative    | Disconnect primary array                     | Fails, error code: array unreachable                 |                        |
| L1-DIS-008| DisableVolumeReplication   | Array unreachable, force=true        | Secondary  | Up         | Down        | force=true   | negative    | Disconnect secondary array                   | Fails, error code: array unreachable                 |                        |
| ...       | ...                        | ...                                  | ...        | ...        | ...         | ...          | ...         | ...                                          | ...                                                  |                        |

---

## PromoteVolume (all key permutations)

| Test ID   | API                    | Scenario                                  | Node Role  | Peer State | Params      | Test Type  | Setup/Input | Expected Outcome                              | Notes/Link |
|-----------|------------------------|-------------------------------------------|------------|------------|-------------|-----------|-------------|-----------------------------------------------|------------|
| L1-PROM-001| PromoteVolume         | Promote secondary → primary, healthy      | Secondary  | Up         | force=false | functional| All VRs in sync, healthy                      | VR status.state=Primary, volume RW                  |            |
| L1-PROM-002| PromoteVolume         | Promote secondary, peer down, force=false | Secondary  | Down       | force=false | negative  | Primary cluster unreachable, attempt promote   | Fails, split-brain error/prevents operation         |            |
| L1-PROM-003| PromoteVolume         | Promote secondary, peer down, force=true  | Secondary  | Down       | force=true  | behavioral| Peer down, force emergency failover           | Promoted, warning about possible data loss          |            |
| ...       | ...                    | ...                                       | ...        | ...        | ...         | ...       | ...         | ...                                           | ...        |

---

## DemoteVolume (all key permutations)

| Test ID   | API                      | Scenario                                    | Node Role   | Peer State | Params      | Test Type  | Setup/Input  | Expected Outcome                             | Notes/Link |
|-----------|--------------------------|---------------------------------------------|-------------|------------|-------------|-----------|--------------|----------------------------------------------|------------|
| L1-DEM-001| DemoteVolume             | Demote primary to secondary, healthy        | Primary     | Up         | force=false | functional|            | VR status.state=Secondary, volume RO         |            |
| L1-DEM-002| DemoteVolume             | Already secondary, healthy                  | Secondary   | Up         | force=false | functional|            | Idempotent                                   |            |
| L1-DEM-003| DemoteVolume             | Active workload, force=true                 | Primary     | Up         | force=true  | behavioral|            | Pending I/O may be dropped, warning issued   |            |
| ...       | ...                      | ...                                         | ...         | ...        | ...         | ...       | ...         | ...                                          | ...        |

---

## ResyncVolume

| Test ID   | API                    | Scenario                                      | Node Role | Peer State | Params      | Test Type  | Setup/Input  | Expected Outcome                                  | Notes/Link |
|-----------|------------------------|-----------------------------------------------|-----------|------------|-------------|-----------|--------------|---------------------------------------------------|------------|
| L1-RSYNC-001| ResyncVolume         | Resync secondary after split-brain            | Secondary | Up         | -           | functional| Split-brain resolved                            | Full resync completes, data consistent             |            |
| ...       | ...                    | ...                                           | ...       | ...        | ...         | ...       | ...          | ...                                              | ...        |

---

## GetVolumeReplicationInfo

| Test ID   | API                        | Scenario                                    | Node Role | Peer State | Params      | Test Type  | Setup/Input  | Expected Outcome                                  | Notes/Link |
|-----------|----------------------------|---------------------------------------------|-----------|------------|-------------|-----------|--------------|---------------------------------------------------|------------|
| L1-INFO-001| GetVolumeReplicationInfo  | Query for healthy replication                | Primary   | Up         | -           | functional| Volume in sync                                   | Returns lastSyncTime, status=healthy               |            |
| ...       | ...                        | ...                                         | ...       | ...        | ...         | ...       | ...          | ...                                              | ...        |

---

## VRG Functional/API/Flow Tests

| Test ID      | API/CRD                  | Scenario                                            | Cluster/Node   | Peer State | S3 State | Params         | Test Type     | Setup/Input                                    | Expected Outcome                               | Notes/Link |
|--------------|--------------------------|-----------------------------------------------------|----------------|------------|----------|----------------|---------------|------------------------------------------------|-----------------------------------------------|------------|
| L1-VRG-001   | VRG API/CRD              | VRG for 1 PVC, both clusters healthy               | primary/secondary| up        | up       | -              | functional     | Create VRG for matching PVC                     | VR, data, status healthy                      |            |
| L1-VRG-002   | VRG API/CRD              | VRG for multiple matching PVCs, both clusters healthy| p/s          | up        | up       | -              | functional     | Multiple PVC selector                           | All VRs created, bound as expected            |            |
| L1-VRG-003   | VRG API/CRD              | VRG created, secondary unreachable                 | primary        | down      | up       | -              | negative       | Create with peer down                           | VR status shows degraded/awaiting peer        |            |
| L1-VRG-004   | VRG API/CRD              | VRG deleted, S3 present, VRs present               | primary/secondary| up        | up       | -              | behavioral     | Delete VRG                                      | VRs deleted, S3 metadata removed, finalizer clears |        |
| L1-VRG-005   | VRG API/CRD              | VRG deletion, S3 down                              | primary/secondary| up        | down     | -              | negative       | Delete VRG with S3 unavailable                   | Delay/error, logs cleanup pending             |            |
| L1-VRG-006   | VRG API/CRD              | VRG failover (promote secondary, primary down)     | secondary      | down      | up       | action=Failover                                 | functional     | Simulate failover                              | Secondary promoted to primary, data consistent|        |
| ...          | ...                      | ...                                                | ...            | ...       | ...      | ...            | ...           | ...                                            | ...                                           | ...        |

---

*Expand for all endpoints/scenarios/flows as desired for complete conformance.*

---