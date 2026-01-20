# Layer 1 CSI Replication Add-on Tests

## Overview
This document provides a comprehensive overview of Layer 1 CSI Replication Add-on tests. This is the primary focus of the project, aimed at ensuring the reliability and efficiency of the replication features.

## RPC Operations
The following RPC operations are central to the testing of the Layer 1 CSI Replication Add-on:
1. **EnableVolumeReplication** - Initiates the replication process for the specified volume.
2. **DisableVolumeReplication** - Stops the replication process for the specified volume.
3. **PromoteVolume** - Promotes a volume to be the primary for replication purposes.
4. **DemoteVolume** - Demotes a volume to a secondary state.
5. **ResyncVolume** - Resynchronizes the data of a volume with its replica.
6. **GetVolumeReplicationInfo** - Retrieves the replication status and information of a volume.

## Official References
- [CSI Add-ons Specification - Replication](https://github.com/csi-addons/spec/tree/main/replication)
- [CSI Add-ons Kubernetes Integration](https://github.com/csi-addons/kubernetes-csi-addons)
- [KubeVirt Storage Checkup](https://github.com/kiagnose/kubevirt-storage-checkup)
- [CSI Replication Add-on API Summary](https://github.com/nadavleva/kubevirt-storage-checkup/blob/main/docs/csi-addons-replication-api.md)

## Test Categories Summary
The tests are categorized into six main categories, with a total of 42 tests implemented to ensure comprehensive coverage of functionality:
1. **Basic Functionality** - 10 tests
2. **Edge Cases** - 8 tests
3. **Performance** - 6 tests
4. **Error Handling** - 8 tests
5. **Integration** - 5 tests
6. **End-to-End** - 5 tests

## Prerequisites
Before running the tests, ensure the following prerequisites are met:
- Kubernetes cluster is set up and available.
- CSI driver and associated components are deployed in the cluster.
- Access to required permissions to perform replication operations.

## Feature Flag Implementation Strategy
Feature flags are used to control the exposure of replication features. The strategy involves:
- Conditional checks based on the feature flag status.
- Wrapping new functionality under the feature flag to prevent breaking existing implementations.

## Running Tests Instructions
To run the tests, follow these instructions:
1. Clone the repository:  
   ```bash
   git clone https://github.com/nadavleva/csi_replication_certs.git
   cd csi_replication_certs
   ```
2. Install the necessary dependencies:  
   ```bash
   make setup
   ```
3. Execute the tests:  
   ```bash
   make test
   ```

## Pass/Fail Criteria
The tests will be considered successful if:
- All assertions pass without any errors.
- There are no unexpected failures during execution.

## Example Workflow for Enabling Replication
1. Enable volume replication using the following command:
   ```bash
   csi-driver enable-replication --volume-id <volume_id>
   ```
2. Monitor the status of the replication process:
   ```bash
   csi-driver get-replication-status --volume-id <volume_id>
   ```

## Troubleshooting Guide
In case of issues, refer to the following steps for troubleshooting:
- Check the logs of the CSI components for any error messages.
- Ensure that the cluster meets all prerequisites mentioned above.
- Validate network connectivity between the source and destination volumes.

For further assistance, please refer to the official documentation or contact support.