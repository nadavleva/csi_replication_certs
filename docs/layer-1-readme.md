# Layer 1 Testing Instructions

## Prerequisites
- Kubernetes cluster version 1.18 or higher
- Access to cluster admin credentials
- Installed CSI driver for testing

## Driver Definition Examples
- Below are examples of how to define the CSI driver in your Kubernetes config:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: my-csi-storage
provisioner: csi.example.com
parameters:
  type: pd-standard
```  

- Example of PVC:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: my-csi-storage
```

## Test Execution Commands
- To execute the tests, use the following command:

```bash
kubectl apply -f test-deployment.yaml
kubectl logs -f deployment/test-deployment
```

## Expected Results
- The deployment should run successfully, and you should see logs indicating the tests are executing without errors.
- Pods should be in the Running state and PersistentVolumes should be bound to the claims.

## Troubleshooting
- If you encounter issues, check the following:
  - Use `kubectl describe pod <pod-name>` to see the events for the pod to identify the issue.
  - Ensure that the StorageClass is available in your cluster with `kubectl get storageclass`.
  - Check logs of the CSI driver for more details of what could be wrong using `kubectl logs -f <csi-driver-pod-name>`.
