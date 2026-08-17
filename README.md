# csi_replication_certs

CSI Replication certification strategy, **layer model**, and scenario matrices.

**Layer 1** is CSI **driver protocol** certification: Kubernetes CSI E2E (csi-spec) and CSI-Addons replication (addon-spec) are the **same layer**, kept separate until the replication addon-spec is approved into the CSI spec, then **merged**. See [docs/test-layers.md](docs/test-layers.md).

**Executable tests today:** [kubernetes-csi-addons](https://github.com/nadavleva/kubernetes-csi-addons) — `make test-replication-e2e`.

## Main documents

- **[CSI-Certification-Review.md](CSI-Certification-Review.md)** — strategy, gaps, `test-replication-e2e` status
- **[presentation.md](presentation.md)** — slides
- **[docs/](docs/README.md)** — layers, run book, matrices
