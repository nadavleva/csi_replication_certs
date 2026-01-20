# CSI Replication Certification - Test Plan Matrix

This document provides a high-level overview of test subjects across all three certification layers.

## Overview

The certification process is divided into three progressive layers, each building upon the previous one:

| Layer | Focus Area | Test Categories | Total Tests |
|-------|-----------|----------------|-------------|
| Layer 1 | Core CSI Storage Operations | 6 categories | 61 tests |
| Layer 2 | Replication & Disaster Recovery | 7 categories | 47 tests |
| Layer 3 | Advanced Integration & Production Readiness | 6 categories | 38 tests |

## Layer 1: Core CSI Storage Operations

High-level test subjects for foundational CSI driver functionality:

| Category | Description | Priority | Detailed Tests |
|----------|-------------|----------|----------------|
| **Volume Lifecycle** | Basic provisioning, deletion, and management | P0 | [Layer 1 Details](layer-1-test-cases.md#volume-lifecycle) |
| **Snapshot Operations** | Snapshot creation, deletion, and restoration | P0 | [Layer 1 Details](layer-1-test-cases.md#snapshot-operations) |
| **Volume Cloning** | Clone from volume and snapshot sources | P1 | [Layer 1 Details](layer-1-test-cases.md#volume-cloning) |
| **Volume Expansion** | Online and offline volume resizing | P1 | [Layer 1 Details](layer-1-test-cases.md#volume-expansion) |
| **Access Modes** | RWO, RWX, ROX, Block, and Filesystem modes | P0 | [Layer 1 Details](layer-1-test-cases.md#access-modes) |
| **Performance & Stability** | Stress testing and resource management | P2 | [Layer 1 Details](layer-1-test-cases.md#performance-stability) |

## Layer 2: Replication & Disaster Recovery

High-level test subjects for replication-aware functionality:

| Category | Description | Priority | Detailed Tests |
|----------|-------------|----------|----------------|
| **Replication Setup** | Enable/disable replication on volumes | P0 | [Layer 2 Details](layer-2-test-cases.md#replication-setup) |
| **Replication States** | State transitions and management | P0 | [Layer 2 Details](layer-2-test-cases.md#replication-states) |
| **Failover Operations** | Primary to secondary site transitions | P0 | [Layer 2 Details](layer-2-test-cases.md#failover-operations) |
| **Resync & Recovery** | Re-establish replication after failures | P1 | [Layer 2 Details](layer-2-test-cases.md#resync-recovery) |
| **Replication with Snapshots** | Snapshot behavior during replication | P1 | [Layer 2 Details](layer-2-test-cases.md#replication-snapshots) |
| **Multi-Site Scenarios** | Cross-cluster replication topologies | P1 | [Layer 2 Details](layer-2-test-cases.md#multi-site) |
| **Replication Monitoring** | Metrics and observability | P2 | [Layer 2 Details](layer-2-test-cases.md#monitoring) |

## Layer 3: Advanced Integration & Production Readiness

High-level test subjects for enterprise-grade deployments:

| Category | Description | Priority | Detailed Tests |
|----------|-------------|----------|----------------|
| **Application Integration** | Stateful workloads (DBs, Kafka, etc.) | P0 | [Layer 3 Details](layer-3-test-cases.md#application-integration) |
| **Disaster Recovery Orchestration** | Automated DR workflows with operators | P0 | [Layer 3 Details](layer-3-test-cases.md#dr-orchestration) |
| **Multi-Cluster Management** | Hub-and-spoke, mesh topologies | P1 | [Layer 3 Details](layer-3-test-cases.md#multi-cluster) |
| **Security & Compliance** | Encryption, RBAC, audit logging | P1 | [Layer 3 Details](layer-3-test-cases.md#security-compliance) |
| **Performance at Scale** | Large volume counts, cross-region latency | P1 | [Layer 3 Details](layer-3-test-cases.md#performance-scale) |
| **Upgrade & Lifecycle Management** | Zero-downtime upgrades, version compatibility | P2 | [Layer 3 Details](layer-3-test-cases.md#upgrade-lifecycle) |

## Priority Definitions

- **P0**: Critical - Must pass for certification
- **P1**: High - Should pass, may require justification if skipped
- **P2**: Medium - Optional but recommended for production readiness

## Test Execution Order

1. **Layer 1 must be completed first** - Establishes baseline CSI functionality
2. **Layer 2 builds on Layer 1** - Adds replication capabilities
3. **Layer 3 validates production readiness** - Comprehensive integration testing

## Documentation Links

- [Layer 1 README](layer-1-readme.md) - Overview and getting started
- [Layer 1 Test Cases](layer-1-test-cases.md) - Detailed 61 test specifications
- [Layer 2 Test Cases](layer-2-test-cases.md) - Detailed 47 test specifications  
- [Layer 3 Test Cases](layer-3-test-cases.md) - Detailed 38 test specifications

## Contributing

To add or modify test cases:
1. Update the appropriate layer-specific test case document
2. Update this matrix if adding new test categories
3. Ensure test IDs follow the format: `L<layer>-<category>-<number>`
4. Submit a pull request with justification for changes