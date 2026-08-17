# Layer 3: Multi-Cluster DR and CNV

**Status:** Upcoming. Depends on Layer 2.

Layer 3 is **orchestrator** certification (RamenDR, application/VM failover). It is **not** Layer 1 two-cluster driver tests (`DR1_CONTEXT` / `DR2_CONTEXT`).

### Components

- **RamenDR** — multi-cluster disaster recovery
- **DRPolicy** — how DR is applied to workloads
- **DRPlacementControl** — placement, failover, failback
- **CNV / KubeVirt** — VM boot, migration, storage checkup

### References

- [RamenDR](https://github.com/RamenDR/ramen)
- [KubeVirt Storage Checkup](https://github.com/kiagnose/kubevirt-storage-checkup)
- [test-layers.md](test-layers.md)
