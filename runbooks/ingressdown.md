# IngressDown

**IngressDown Runbook**

### Description

The **IngressDown** alert is triggered when the ingress controller in the cluster is not functioning properly, preventing new incoming traffic from being routed to the services deployed within the cluster. This can be due to various reasons such as misconfiguration, downtime of the controller pods, or issues with external dependencies (e.g., DNS resolution).

### Likely Causes

1. **Ingress Controller Crash**: The ingress controller pod has crashed and is not running.
2. **Misconfigured Ingress Resource**: An ingress resource has been configured incorrectly, preventing it from generating HTTP/S requests to reach the service(s).
3. **Incorrect Annotation/Value**: Annotations or values on the ingress resource are incorrect or missing crucial information required for routing traffic correctly.
4. **External Dependency Issues**: Problems with external dependencies such as DNS resolution affecting the ingress controller's functionality.

### Steps to Diagnose

1. **Check Ingress Controller Pods**:
   - ```bash
     kubectl get pods -n <namespace> -l app=<ingress-controller-app>
     ```
   
   Verify that at least one pod is running and reporting in readiness.
2. **Check Ingress Resource Configuration**:
   - ```bash
     kubectl get ingress <ingress-name> -o yaml
     ```
   
   Review the `spec` section to ensure all necessary configuration parameters (e.g., rules, annotations) are correctly set up.
3. **Verify Ingress Controller Logs**:
   - ```bash
     kubectl logs <ingress-controller-pod>
     ```
   
   Examine logs for any errors or warning messages related to ingress configuration, DNS resolution, etc.
4. **Check External Dependencies** (e.g., DNS resolution):
   - Perform local tests and checks on the system level for issues that could be preventing access to the service.

### Steps to Fix

1. **Restart Ingress Controller Pods**:
   - ```bash
     kubectl rollout restart deploy/<ingress-controller-deployment-name>
     ```
   
   Restart the deployment to ensure new, properly configured pods come up online.
2. **Correct Misconfigured Ingress Resource or Annotations**:
   - **Edit and Update**: If the ingress resource is misconfigured, update it with correct values for routing. Alternatively, create a new ingress resource if necessary.

        ```bash
        kubectl edit ingress <ingress-name>
        ```
3. **Address External Dependency Issues**:
   - Resolve issues affecting external dependencies like DNS resolution as identified during diagnosis steps.
4. **Test Ingress**:
   - Test the ingress controller by navigating to an external endpoint and verifying that traffic is routed correctly.

### Escalate if

* Incidents persist after completing troubleshooting steps outlined in the runbook.
* The issue involves complex configurations or dependencies not covered here, such as HAProxy configuration with load balancers.
* There's a significant business impact or potential downtime because of service unavailability.