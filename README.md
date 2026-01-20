# CSI Replication Certification Testing Framework

## Project Title and Purpose
This project extends the standard Container Storage Interface (CSI) certification process to cover replication capabilities, ensuring that CSI drivers can effectively manage replicated storage across various environments.

## Overview
Our testing strategy utilizes a multi-tiered approach, structured into four distinct layers:

- **Layer 0: Core CSI Prerequisite**  
  This layer encompasses the existing Kubernetes CSI tests that serve as a foundation for the certification process. It ensures that all fundamental functionalities are validated before extending to replication-specific scenarios.

- **Layer 1: CSI Replication Add-on Functionality**  
  This layer focuses on testing the core replication features of the CSI Replication Add-on. It validates the capabilities provided by the add-on to manage storage replication, ensuring compliance with expected behaviors and specifications.

- **Layer 2: OCP Platform Orchestration**  
  In this layer, we focus on testing the functionality and orchestration capabilities of the OpenShift Container Platform (OCP) with the CSI Replication Add-on, ensuring seamless integration and operational efficiency.

- **Layer 3: Multi-Cluster DR and CNV**  
  The final layer explores disaster recovery (DR) scenarios across multiple clusters and tests virtual machine (VM) cases using Container Native Virtualization (CNV). This ensures that storage replication strategies are resilient and effective across distributed environments.

## Documentation Structure
- [High-Level Test Overview](docs/test-plan-matrix.md)  
- [CSI Replication Add-on Detailed Tests](docs/layer-1-test-cases.md)  
- [OCP Platform Tests](docs/layer-2-test-cases.md)  
- [Multi-cluster DR and VM Tests](docs/layer-3-test-cases.md)  
- [Reference Implementations](docs/sources.md)  

## Layer Descriptions
- **Layer 0**: Represents prerequisite tests based on existing Kubernetes CSI functionality, ensuring that all drivers meet core performance standards.
- **Layer 1**: This layer serves as the primary focus of our framework, evaluating the additional capabilities that the CSI Replication Add-on introduces.
- **Layer 2**: Here, we assess how well the CSI Replication integrates with the OpenShift platform, emphasizing orchestration capacity and compatibility.
- **Layer 3**: Concentrating on multi-cluster scenarios, this layer tests the adaptability of the solution in a diverse and distributed environment, incorporating RamenDR and CNV validations.

## References
More details can be found in the following specifications:
- [CSI Add-ons Specification for Replication](csi-addons/spec/replication)
- [KubeVirt Storage Checkup Guide](kubevirt-storage-checkup)

## Target Audience
The primary audience for this framework includes:
- CSI driver vendors
- Storage providers

## Quick Start
To get started with the testing framework, refer to the respective layer documentation and ensure all prerequisites are met before executing the tests.

## Contributing
We welcome contributions from the community. Please refer to our contributing guidelines for more information on how to get involved!