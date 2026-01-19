# Layer 1 Test Execution Guide

## Prerequisites
- Ensure the Kubernetes cluster is up and running.
- Install the necessary Core CSI drivers compatible with your storage system.
- Verify that the Kubernetes CLI (`kubectl`) is configured to interact with your cluster.
- Check that you have the right permissions to create resources in the target namespace.

## Driver Definition Creation
1. **Create a CSI Driver Definition**:
   - Use the provided YAML configuration to declare the driver.
   - Example:
   ```yaml
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: your-csi-driver-name
   provisioner: your.csi.driver
   parameters:
     type: type-of-storage
   reclaimPolicy: Retain
   volumeBindingMode: Immediate
   ```
   - Apply the configuration using:
   ```bash
   kubectl apply -f csi-driver-definition.yaml
   ```

## Test Execution Commands
- Use the following commands to execute the tests:
   1. Validate the driver:
   ```bash
   kubectl get csidrivers
   ```
   2. Run the sample application using the created driver:
   ```bash
   kubectl apply -f sample-application.yaml
   ```
   3. Check the status of the pods:
   ```bash
   kubectl get pods -n your-namespace
   ```

## Expected Outcomes
- The driver should be listed when running `kubectl get csidrivers`.
- Pods should be running without errors. If any pods are not running, check their logs with:
   ```bash
   kubectl logs pod-name -n your-namespace
   ```
- The application should function according to the intended specifications, successfully interacting with the storage system.

## Troubleshooting
- If the CSI driver fails to register:
   - Ensure the driver image is available and correctly specified in the deployment.
   - Check the logs of the driver pods:
   ```bash
   kubectl logs csi-driver-pod-name -n your-namespace
   ```
- If the tests fail:
   - Verify resource limits and quotas in the Kubernetes namespace.
   - Check for resource allocation errors through events:
   ```bash
   kubectl get events -n your-namespace
   ```

For further help, consult the CSI driver documentation or community forums.