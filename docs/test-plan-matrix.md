# Test Plan Matrix

## Overview
This matrix outlines the test plan for the CSI Replication Certification across various layers.

| Layer  | Description                                                                         | Priority | Execution Order | Documentation                                       |
| ------ | ----------------------------------------------------------------------------------- | -------- | ---------------- | --------------------------------------------------- |
| Layer 0 | **Core CSI Certification** - External prerequisite for all verification tests.      | High     | 1                | [Core CSI Docs](https://example.com/core-csi)     |
| Layer 1 | **CSI Replication Add-on** - Primary focus of the tests. Refer to [csi-addons/spec](https://example.com/csi-addons/spec) and [kubevirt-storage-checkup](https://example.com/kubevirt-storage-checkup). | High     | 2                | [CSI Replication Add-on](https://example.com/replication-addon) |
| Layer 2 | **OCP Platform Orchestration** - Validates single cluster setups with VRG management.| Medium   | 3                | [OCP Docs](https://example.com/ocp)                |
| Layer 3 | **Multi-Cluster DR and CNV** - Testing with RamenDR and KubeVirt references.      | Medium   | 4                | [Multi-Cluster DR](https://example.com/multi-cluster-dr) |

## Additional Information
- The test execution order reflects the dependencies between the layers.
- Priorities are defined as High, Medium, or Low, where High should be executed first.
- Documentation linked in the table provides resources and references for further clarification.