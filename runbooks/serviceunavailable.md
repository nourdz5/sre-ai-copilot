# ServiceUnavailable

**Runbook: ServiceUnavailable**
=================================

### Description
---------------

The `ServiceUnavailable` alert indicates that a service is not accessible or reachable, preventing users from interacting with it.

### Likely Causes
-----------------

*   **Deployment errors**: A failed deployment may leave the service unavailable.
*   **Rolling updates gone wrong**: An update to the service caused an unexpected error, resulting in service unavailability.
*   **Pod failures**: Pods running the service are not functioning correctly due to various reasons like configuration issues or crashes.
*   **Cluster connectivity issues**: Network connectivity problems between the clients and the cluster affecting service availability.

### Steps to Diagnose
----------------------

1.  **Initial Check**:
    *   Run `kubectl get pods -n <namespace>` to check if all pods are running as expected. Verify the replica count, pod status, and pod logs for any errors.
2.  **Service Check**:
    *   Use `kubectl describe svc <service_name> -n <namespace>` to inspect service details. Ensure that the selector matches with running pods and port types are correctly exposed.
3.  **Endpoint Inspection**:
    *   Run `kubectl get endpoints <service_name> -o yaml` to examine all endpoint information, including IP addresses, ports, and corresponding pod mappings.

### Steps to Fix
-----------------

1.  **Check Rolling Updates**: If the issue occurred after a rolling update, go through logs of involved pods and services for any clues. Revert the update if needed.
2.  **Pod Failure Resolution**:
    *   Use `kubectl replace <pod_name> --namespace=<namespace>` to recreate pods that have an unusual error in their pod spec or runtime issues.
    *   Adjust pod configurations with `kubectl patch` and roll them out if required, considering the scope of affected resources.
3.  **Cluster Connectivity Resolution**:
    *   Referencing k8s logging on a separate cluster might give insight into network errors occurring between clients. If possible, try accessing the service from within one node.
4.  **Service Configuration Adjustments**: Correctly adjust IP addresses in selectors and set ports according to needs specified by service spec definitions.

### Escalate if
----------------

If efforts to resolve issues result in:

*   Increased pod counts or rolling updates fail repeatedly.
*   Service configuration appears to be properly defined with no obvious errors.
*   Pod logs have unclear messages pointing towards an external system causing unavailability.
*   Inability to replicate errors despite troubleshooting at the pod and cluster levels.

Consider escalating this situation for more advanced assistance from Kubernetes experts who can explore deeper potential causes.