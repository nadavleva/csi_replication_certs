# Test Plan Matrix

| Test ID | Test Description | Prerequisites | Expected Results | Priority |
|---------|------------------|---------------|------------------|----------|

## Layer 1: CSI Driver Tests
| 1.1     | Basic provisioning (RWO, RWX, Block, Filesystem) | CSI Driver, Kubernetes cluster | Volumes successfully provisioned | P0 |
| 1.2     | Volume snapshots (create, delete, restore) | Volume must exist | Volumes can be created, deleted, and restored | P0 |
| 1.3     | Volume clones (from snapshot, from volume) | Snapshot must exist | Cloned volume is identical to original | P1 |
| 1.4     | Volume expansion (offline, online) | Volume must exist | Volume size updated without errors | P1 |
| 1.5     | Capacity tracking | CSI Driver, Metrics API | Accurate reporting of volume capacity | P2 |
| 1.6     | Multi-attach scenarios | Volume must support multi-attach | Concurrent access from multiple nodes | P2 |

## Layer 2: Volume Replication Tests
| 2.1     | Enable/disable replication | Volume must exist | Replication status changes as expected | P0 |
| 2.2     | Primary/secondary role transitions | Replication must be configured | Roles switch without data loss | P0 |
| 2.3     | Sync/async mode testing | Replication must be configured | Works as per chosen mode | P1 |
| 2.4     | Force resync operations | Replication must be running | Resync occurs with no errors | P1 |
| 2.5     | Replication health monitoring | Replication must be configured | Health is reported accurately | P2 |
| 2.6     | Split-brain scenarios | Replication must be running | Correct resolution of conflicts | P2 |

## Layer 3: VolumeReplicationGroup Tests
| 3.1     | Multi-PVC consistency groups | Multi-PVC setup done | Consistency group behaves as expected | P0 |
| 3.2     | S3 metadata management (upload, download, verify) | S3 bucket configured | Metadata correctly managed | P1 |
| 3.3     | Kubernetes object protection (ConfigMap, Secret, Deployment backups) | Objects must exist | Objects are backed up/restored as expected | P1 |
| 3.4     | Group snapshot operations | Multi-PVC setup done | Group snapshots succeed | P2 |
| 3.5     | PV/PVC metadata preservation | Metadata should exist | No data loss during operations | P2 |
| 3.6     | Recovery testing | Backup must exist | Recovery proceeds without errors | P2 |

## Layer 4: DR Orchestration Tests
| 4.1     | DRPolicy configuration | DRPolicy must be defined | Policy applies correctly | P0 |
| 4.2     | Planned failover | DRPolicy applied | System fails over as planned | P0 |
| 4.3     | Unplanned failover | DRPolicy applied | System fails over without data loss | P0 |
| 4.4     | Failback operations | DRPolicy applied post-failover | System returns to original state | P1 |
| 4.5     | Relocate operations | DRPolicy applied | Resources placed correctly | P1 |
| 4.6     | Application placement | Applications must be defined | Applications deploy correctly in new site | P2 |
| 4.7     | RPO/RTO validation | DRPolicy configured | RPO/RTO is verified as met | P2 |
| 4.8     | Multi-cluster scenarios | Multi-cluster environment set up | Operations succeed across clusters | P2 |
