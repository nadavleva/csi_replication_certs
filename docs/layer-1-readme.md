# CSI Replication Add-on

The CSI Replication Add-on is the primary project focus, facilitating various operations for managing volume replication in a Kubernetes environment.

## RPC Operations
1. **EnableVolumeReplication**: Activates replication for a specified volume.
2. **DisableVolumeReplication**: Deactivates replication for a specified volume.
3. **PromoteVolume**: Promotes a volume to become the primary volume.
4. **DemoteVolume**: Demotes a volume from being the primary volume.
5. **ResyncVolume**: Re-synchronizes the replicated volume with its primary version.
6. **GetVolumeReplicationInfo**: Retrieves information about the replication status of a volume.

## References
- [csi-addons/spec](https://github.com/csi-addons/spec)
- [kubevirt-storage-checkup API summary](https://your.api.link)

## Feature Flag Implementation Strategy
Details on how to implement feature flags can be referenced in the feature documentation.

## Test Categories
The test categories in total include approximately 40 tests that cover various aspects of volume replication for the CSI Replication Add-on. 

## Prerequisites
- Kubernetes cluster configured.
- Proper RBAC permissions set.

## Setup Instructions
Follow the official setup guide to configure the CSI Replication Add-on in your cluster.

## Troubleshooting Guide
Refer to the troubleshooting section for common issues and their solutions.
