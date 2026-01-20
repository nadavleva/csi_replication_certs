# Layer 3 Overview

## Work In Progress

This document provides a high-level overview of Layer 3, which encompasses key components and functionalities related to RamenDR multi-cluster orchestration.

### Components Overview:

- **RamenDR Multi-Cluster Orchestration**: A framework designed to manage disaster recovery across multiple clusters seamlessly.
- **DRPolicy**: Policies that determine how disaster recovery is implemented and managed for resources in a Kubernetes environment.
- **DRPlacementControl**: A mechanism responsible for controlling the placement of resources during failover and failback operations.
- **Multi-Site Failover/Failback**: Strategies and procedures that enable seamless failover to a secondary site and restoring back to the primary site without data loss.
- **CNV/KubeVirt VM Integration**: Integration of Container Native Virtualization (CNV) with KubeVirt to facilitate the management of virtual machines alongside container workloads.
- **VM Boot**: Processes involved in booting virtual machines in a disaster recovery scenario.
- **Migration**: Techniques for moving workloads from one cluster to another as part of disaster recovery and high availability.
- **Failover Scenarios**: Possible scenarios and responses when a primary resource becomes unavailable, ensuring minimal disruption.
- **Failback Scenarios**: Procedures to return workloads to the primary cluster after failover conditions are resolved.

### References:
- [RamenDR Repository](https://github.com/RamenDR/ramen)
- [KubeVirt Storage Checkup Tool](https://github.com/kiagnose/kubevirt-storage-checkup)