# CSI Replication Certification Testing Framework

This repository contains a comprehensive multi-layer testing strategy for CSI (Container Storage Interface) replication certification, covering testing from the CSI driver level through disaster recovery orchestration.

## Overview

The testing framework is organized into distinct layers, each validating different aspects of CSI replication functionality:

1. **Layer 1: CSI Driver Tests** - Core CSI driver functionality
2. **Layer 2: Volume Replication Tests** - Storage-level replication capabilities  
3. **Layer 3: VolumeReplicationGroup Tests** - Multi-volume coordination
4. **Layer 4: Disaster Recovery Orchestration** - Full DR workflow validation

## Documentation Structure

- [Test Layers Overview](test-layers.md) - Detailed description of each testing layer
- [Reference Sources](reference-sources.md) - External projects and implementations referenced
- [Test Plan Matrix](test-plan-matrix.md) - Comprehensive test coverage matrix
- [Layer-Specific READMEs](#layer-documentation) - How to run tests for each layer

## Layer Documentation

Each test layer has its own README with execution instructions:

- [Layer 1: CSI Driver Tests](layer1-csi-driver/README.md)
- [Layer 2: Volume Replication Tests](layer2-volume-replication/README.md)
- [Layer 3: VolumeReplicationGroup Tests](layer3-vrg/README.md)
- [Layer 4: DR Orchestration Tests](layer4-dr-orchestration/README.md)

## Quick Start

### Prerequisites

- Kubernetes cluster (1.20+)
- CSI driver with replication support installed
- Volume Replication Operator
- S3-compatible object storage (for Layer 3+)

### Running Tests

Refer to each layer's README for specific execution instructions. Generally:

```bash
# Layer 1: CSI Driver Tests
cd layer1-csi-driver
./run-tests.sh

# Layer 2: Volume Replication Tests  
cd layer2-volume-replication
./run-tests.sh

# Layer 3: VRG Tests
cd layer3-vrg
./run-tests.sh

# Layer 4: DR Orchestration Tests
cd layer4-dr-orchestration
./run-tests.sh
```

## Reference Implementations

This framework draws from several established projects:

- **Kubernetes CSI External Storage Tests** - Standard CSI driver validation
- **Ceph CSI** - Reference implementation for RBD/CephFS replication
- **RamenDR** - Disaster recovery orchestration and VRG management
- **CNV/KubeVirt Storage** - Virtualization workload storage testing

See [Reference Sources](reference-sources.md) for detailed information.

## Contributing

Contributions are welcome! Please ensure:

1. Tests follow the established layer structure
2. Documentation is updated for new test cases
3. Test matrix is updated with new coverage
4. Code follows project conventions

## License

[Add your license information here]

## Contact

[Add contact/maintainer information here]