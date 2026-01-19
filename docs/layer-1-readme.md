# Layer 1 Kubernetes Core CSI Tests Documentation

## Prerequisites
- Kubernetes Cluster
- Valid CSI Driver
- Access to development and testing tools

## Driver Definition Templates
```yaml
# Example Driver Definition Template
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: my-csi-driver
provisioner: csi.example.com
parameters:
  type: pd-standard
```

## Test Execution Commands
```bash
# Command to execute all tests
./run-all-tests.sh
```

## Test Cases
1. **Test Case 1**: Validate Volume Creation
2. **Test Case 2**: Validate Volume Deletion
3. **Test Case 3**: Validate Volume Snapshotting
4. **Test Case 4**: Validate Volume Restoration
5. **Test Case 5**: Validate Volume Permissions

...

61. **Test Case 61**: Validate Plugin Interoperability

## Troubleshooting Guide
- **Problem**: Volume not attaching
  - **Solution**: Ensure the correct CSI driver is installed and configured.

## Complete Test Command Reference
- `create-volume`: Creates a volume.
- `delete-volume`: Deletes a volume.
- `snapshot-volume`: Takes a snapshot of the volume.
- `restore-volume`: Restores a volume from a snapshot.