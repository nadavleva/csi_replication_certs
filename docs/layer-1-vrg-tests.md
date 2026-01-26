# Layer-1 VRG Test Matrix: Volume Group Operations Using CSI gRPC APIs

This file contains Volume Group test scenarios for Layer-1 CSI Replication driver conformance using **VolumeReplication gRPC APIs** with the **replicationsource** field.

**Important**: VolumeReplicationGroup (VRG) Kubernetes CRD tests are **not in scope for Phase 1**. This file focuses on Volume Group operations using CSI gRPC APIs only.

**Technical Implementation**: Volume group replication uses the same VolumeReplication gRPC APIs (EnableVolumeReplication, DisableVolumeReplication, PromoteVolume, DemoteVolume, etc.) with the **replicationsource** field to specify group membership.

---

## Volume Group Operations (using VolumeReplication gRPC APIs with replicationsource field)

*Note: These are simplified test cases focusing on core group scenarios using VolumeReplication RPC with replicationsource=group parameter.*

| Test ID   | RPC API                    | Scenario                                    | Group State | Params          | Test Type   | Setup/Input                                    | Expected Outcome                                          | Notes/Link             |
|-----------|----------------------------|---------------------------------------------|-------------|-----------------|-------------|------------------------------------------------|-----------------------------------------------------------|------------------------|
| L1-GRP-001| EnableVolumeReplication    | Enable replication for volume group         | All disabled| replicationsource=group1 | functional  | 3 volumes in group, all healthy                | All volumes in group enabled for replication             |                        |
| L1-GRP-002| DisableVolumeReplication   | Disable replication for volume group        | All enabled | replicationsource=group1 | functional  | 3 volumes in group, all replicating            | All volumes in group disabled, group consistent          |                        |
| L1-GRP-003| PromoteVolume              | Promote volume group to primary             | Secondary   | replicationsource=group1 | functional  | Volume group in secondary state                | All volumes in group promoted to primary                 |                        |
| L1-GRP-004| DemoteVolume               | Demote volume group to secondary            | Primary     | replicationsource=group1 | functional  | Volume group in primary state                  | All volumes in group demoted to secondary                |                        |
| L1-GRP-005| EnableVolumeReplication    | Enable group with mixed volume states       | Mixed       | replicationsource=group1 | negative    | Some volumes enabled, some disabled            | Operation fails, group state inconsistent                |                        |
| L1-GRP-006| DisableVolumeReplication   | Force disable group, peer unreachable       | Enabled     | replicationsource=group1, force=true | behavioral | Group enabled, peer cluster down              | Group disabled with warnings, split-brain risk           |                        |

**Volume Group Operations Test Count: 6 scenarios (Phase 1 - using VolumeReplication gRPC APIs)**

---

**VolumeReplicationGroup (VRG) CRD Operations - Out of Scope for Phase 1**

*The following VRG CRD-based operations are not included in Phase 1 testing scope:*

## VRG Disable Operations - Core Scenarios

### Active Replication (Both Sides Alive) - force=false

| Test ID        | API Operation | Scenario                                          | Primary State | Secondary State | Peer Conn | Array State | Params      | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|-----------------|-----------|-------------|-------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-DIS-001 | VRG Disable   | Disable on primary, active replication           | Active        | Active          | Up        | P:Up/S:Up   | force=false | functional | Active VRG with healthy replication             | VRG disabled, replication stopped, primary writable       |            |
| L1-VRG-DIS-002 | VRG Disable   | Disable on secondary, active replication         | Active        | Active          | Up        | P:Up/S:Up   | force=false | functional | Active VRG with healthy replication             | VRG disabled, replication stopped, secondary remains RO   |            |

### Previously Disabled Replication (Both Sides Alive) - force=false

| Test ID        | API Operation | Scenario                                          | Primary State | Secondary State | Peer Conn | Array State | Params      | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|-----------------|-----------|-------------|-------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-DIS-003 | VRG Disable   | Disable on primary, previously disabled          | Disabled      | Disabled        | Up        | P:Up/S:Up   | force=false | functional | VRG exists but replication already disabled     | Idempotent operation, no error                             |            |
| L1-VRG-DIS-004 | VRG Disable   | Disable on secondary, previously disabled        | Disabled      | Disabled        | Up        | P:Up/S:Up   | force=false | functional | VRG exists but replication already disabled     | Idempotent operation, no error                             |            |

### Broken Replication (Peer Dead) - force=false

| Test ID        | API Operation | Scenario                                          | Primary State | Secondary State | Peer Conn | Array State | Params      | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|-----------------|-----------|-------------|-------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-DIS-005 | VRG Disable   | Disable on primary, peer dead                    | Active        | Unknown         | Down      | P:Up/S:?    | force=false | negative   | Network partition, secondary cluster unreachable| Operation fails, appropriate timeout/error in status      |            |
| L1-VRG-DIS-006 | VRG Disable   | Disable on secondary, peer dead                  | Unknown       | Active          | Down      | P:?/S:Up    | force=false | negative   | Network partition, primary cluster unreachable | Operation fails, split-brain protection active            |            |

### Array Unreachable - force=false

| Test ID        | API Operation | Scenario                                          | Primary State | Secondary State | Peer Conn | Array State | Params      | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|-----------------|-----------|-------------|-------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-DIS-007 | VRG Disable   | Disable on primary, primary array unreachable    | Unknown       | Active          | Up        | P:Down/S:Up | force=false | negative   | Primary storage array disconnected              | Operation fails, cannot access primary volume metadata    |            |
| L1-VRG-DIS-008 | VRG Disable   | Disable on secondary, secondary array unreachable| Active        | Unknown         | Up        | P:Up/S:Down | force=false | negative   | Secondary storage array disconnected            | Operation fails, cannot clean up secondary resources      |            |

---

## VRG Disable Operations - With force=true

### Active Replication (Both Sides Alive) - force=true

| Test ID        | API Operation | Scenario                                          | Primary State | Secondary State | Peer Conn | Array State | Params     | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|-----------------|-----------|-------------|------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-DIS-009 | VRG Disable   | Force disable on primary, active replication     | Active        | Active          | Up        | P:Up/S:Up   | force=true | behavioral | Active VRG, force immediate disable             | Immediate disable, potential data loss warning logged     |            |
| L1-VRG-DIS-010 | VRG Disable   | Force disable on secondary, active replication   | Active        | Active          | Up        | P:Up/S:Up   | force=true | behavioral | Active VRG, force immediate disable             | Immediate disable, secondary disconnected                  |            |

### Previously Disabled Replication (Both Sides Alive) - force=true

| Test ID        | API Operation | Scenario                                          | Primary State | Secondary State | Peer Conn | Array State | Params     | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|-----------------|-----------|-------------|------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-DIS-011 | VRG Disable   | Force disable on primary, previously disabled    | Disabled      | Disabled        | Up        | P:Up/S:Up   | force=true | functional | VRG exists but replication already disabled     | Idempotent operation, no error                             |            |
| L1-VRG-DIS-012 | VRG Disable   | Force disable on secondary, previously disabled  | Disabled      | Disabled        | Up        | P:Up/S:Up   | force=true | functional | VRG exists but replication already disabled     | Idempotent operation, no error                             |            |

### Broken Replication (Peer Dead) - force=true

| Test ID        | API Operation | Scenario                                          | Primary State | Secondary State | Peer Conn | Array State | Params     | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|-----------------|-----------|-------------|------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-DIS-013 | VRG Disable   | Force disable on primary, peer dead              | Active        | Unknown         | Down      | P:Up/S:?    | force=true | behavioral | Network partition, force override               | Primary disabled immediately, split-brain warning         |            |
| L1-VRG-DIS-014 | VRG Disable   | Force disable on secondary, peer dead            | Unknown       | Active          | Down      | P:?/S:Up    | force=true | behavioral | Network partition, force override               | Secondary disabled, emergency cleanup                      |            |

### Array Unreachable - force=true

| Test ID        | API Operation | Scenario                                          | Primary State | Secondary State | Peer Conn | Array State | Params     | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|-----------------|-----------|-------------|------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-DIS-015 | VRG Disable   | Force disable on primary, primary array down     | Unknown       | Active          | Up        | P:Down/S:Up | force=true | negative   | Primary array disconnected, force attempted     | Still fails, cannot force without array access            |            |
| L1-VRG-DIS-016 | VRG Disable   | Force disable on secondary, secondary array down | Active        | Unknown         | Up        | P:Up/S:Down | force=true | behavioral | Secondary array disconnected, force cleanup     | Forced cleanup, metadata inconsistency warnings           |            |

**VRG Disable Operations Test Count: 16 scenarios (8 force=false + 8 force=true) - Out of Scope for Phase 1**

---

## VRG Creation and Lifecycle Operations

| Test ID        | API Operation | Scenario                                          | Cluster State | PVC State   | S3 State | Params         | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|-------------|----------|----------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-CRE-001 | VRG Create    | Create VRG for single PVC, healthy clusters      | Both Up       | Bound       | Up       | -              | functional | Valid PVC, both clusters healthy                | VRG created, VR resources provisioned                     |            |
| L1-VRG-CRE-002 | VRG Create    | Create VRG for multiple PVCs, healthy clusters   | Both Up       | Multiple    | Up       | -              | functional | Multiple matching PVCs                          | VRG created, multiple VR resources                         |            |
| L1-VRG-CRE-003 | VRG Create    | Create VRG, secondary cluster unreachable        | P:Up/S:Down   | Bound       | Up       | -              | negative   | Secondary cluster network failure               | VRG creation delayed/degraded state                        |            |
| L1-VRG-CRE-004 | VRG Create    | Create VRG, S3 unreachable                       | Both Up       | Bound       | Down     | -              | negative   | S3 metadata store unavailable                   | VRG creation fails, cannot store metadata                 |            |
| L1-VRG-CRE-005 | VRG Create    | Create VRG, invalid PVC selector                 | Both Up       | None        | Up       | bad-selector   | negative   | PVC selector matches no resources               | VRG created but no VR resources, appropriate status       |            |

**VRG Creation and Lifecycle Operations Test Count: 5 scenarios - Out of Scope for Phase 1**

---

## VRG Failover and Failback Operations

| Test ID        | API Operation | Scenario                                          | Primary State | Secondary State | Peer Conn | S3 State | Params            | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|-----------------|-----------|----------|-------------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-FAIL-001| VRG Failover  | Emergency failover, primary cluster down         | Down          | Active          | Down      | Up       | action=Failover   | functional | Primary cluster failure simulation              | Secondary promoted to primary, data accessible            |            |
| L1-VRG-FAIL-002| VRG Failover  | Planned failover, both clusters healthy          | Active        | Active          | Up        | Up       | action=Failover   | functional | Graceful planned failover                       | Clean role switch, minimal downtime                       |            |
| L1-VRG-FAIL-003| VRG Failback  | Failback after primary recovery                  | Recovered     | Primary         | Up        | Up       | action=Failback   | functional | Primary cluster restored after failure          | Original primary restored, data consistent                 |            |
| L1-VRG-FAIL-004| VRG Failover  | Split-brain scenario, force failover             | Isolated      | Isolated        | Partial   | Up       | action=Failover   | behavioral| Network split causing isolation                 | Emergency promotion with split-brain warnings             |            |

---

## VRG Status and Monitoring Operations

| Test ID        | API Operation | Scenario                                          | Replication State | Sync Status | Error State | Params | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|-------------------|-------------|-------------|--------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-STAT-001| VRG Status    | Query status, healthy replication                | Active            | InSync      | None        | -      | functional | Normal replication operation                    | Status shows healthy, lastSyncTime current                |            |
| L1-VRG-STAT-002| VRG Status    | Query status, sync in progress                   | Active            | Syncing     | None        | -      | functional | Replication sync operation ongoing              | Status shows sync progress, estimated completion          |            |
| L1-VRG-STAT-003| VRG Status    | Query status, error condition                    | Degraded          | OutOfSync   | NetworkError| -      | functional | Network issues affecting replication            | Status shows error details, troubleshooting info          |            |

---

## VRG Deletion and Cleanup Operations

| Test ID        | API Operation | Scenario                                          | VRG State     | VR State    | S3 State | Finalizers | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|-------------|----------|------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-DEL-001 | VRG Delete    | Delete VRG, all resources healthy                | Active        | Multiple    | Up       | Present    | functional | VRG with active VR resources                    | VRG deleted, all VRs cleaned up, finalizers cleared       |            |
| L1-VRG-DEL-002 | VRG Delete    | Delete VRG, S3 unavailable                       | Active        | Multiple    | Down     | Present    | negative   | S3 metadata store unreachable                   | Deletion blocked, finalizer remains, cleanup pending      |            |
| L1-VRG-DEL-003 | VRG Delete    | Delete VRG, peer cluster unreachable             | Active        | Multiple    | Up       | Present    | behavioral | Secondary cluster network failure               | Local cleanup, remote cleanup marked for retry            |            |
| L1-VRG-DEL-004 | VRG Delete    | Force delete VRG, resources stuck                | Terminating   | Stuck       | Up       | Stuck      | behavioral | VR resources cannot be cleaned normally         | Force deletion, resource leakage warnings                 |            |

---

## VRG Cross-Namespace and Multi-Cluster Scenarios

| Test ID        | API Operation | Scenario                                          | Namespace     | PVC Location | Cluster Config | Test Type  | Setup/Input                                     | Expected Outcome                                           | Notes/Link |
|----------------|---------------|---------------------------------------------------|---------------|--------------|----------------|------------|-------------------------------------------------|------------------------------------------------------------|------------|
| L1-VRG-NS-001  | VRG Create    | VRG in different namespace than PVCs              | Different     | ns1/ns2      | Standard       | functional | VRG in ns-a, PVCs in ns-b                       | Cross-namespace selection works correctly                  |            |
| L1-VRG-NS-002  | VRG Create    | VRG with PVCs across multiple namespaces         | Multiple      | Multiple     | Standard       | functional | PVC selector spans namespaces                   | All matching PVCs selected regardless of namespace        |            |
| L1-VRG-MC-001  | VRG Create    | VRG on cluster with different storage classes    | Standard      | Mixed SC     | Heterogeneous  | behavioral | Primary/secondary use different storage         | VRG handles storage class differences gracefully          |            |

---

*This matrix provides comprehensive coverage of VRG operations with particular emphasis on disable scenarios as requested. Each test case includes detailed state specifications and expected outcomes for thorough conformance testing.*

---

**Total VRG Test Count Summary:**

**Phase 1 - In Scope (Volume Group Operations using gRPC APIs):**
- Volume Group Operations: 6 scenarios

**Out of Scope for Phase 1 (VRG Kubernetes CRD Operations):**
- VRG Disable Operations: 16 scenarios
- VRG Creation/Lifecycle: 5 scenarios  
- VRG Failover/Failback: 4+ scenarios
- VRG Status/Monitoring: 3+ scenarios
- VRG Deletion/Cleanup: 4+ scenarios
- VRG Cross-Namespace: 3+ scenarios
- **Total CRD Operations**: 35+ scenarios (future phases)

---