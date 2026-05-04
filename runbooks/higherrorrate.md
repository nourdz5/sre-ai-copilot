# HighErrorRate

**High Error Rate Runbook**

### Description

Alerts with the name `HighErrorRate` are triggered when the average error rate of a service exceeds a certain threshold (configured as `min-error-rate-trigger` in the alerting configuration). This means that the service is experiencing an unusually high number of errors, which can be indicative of issues such as code bugs, resource congestion, or misconfigured dependencies.

### Likely Causes

* **Resource constraints**: Insufficient resources (e.g., CPU, memory) are causing the service to become unresponsive and resulting in increased error rates.
* **Dependent services issues**: Issues with dependent services (e.g., database connections, external API integrations) can cause errors upstream, cascading to the affected service.
* **Configuration or code issues**: Misconfigured dependencies, incorrect initialization parameters, or code defects are causing errors to be generated within the service.

### Steps to Diagnose

1. **Check the alert details**:
	```bash
kubectl get alerts --selector=alertname=HighErrorRate -o jsonpath='{.items[0].annotations.details}'
```
This will provide additional details about the alert, including the name of the pods that triggered the issue.
2. **List and describe impacted pods**:
```bash
kubectl get pods --selector=name=<service-name>,status=Running
kubectl describe pod <pod-name>
```
Here, replace `<service-name>` with the name of your service that is triggering the alert, and `<pod-name>` with one of the affected pods.
3. **View recent logs**: Inspect the system logs to identify potential causes:
```bash
kubectl logs -f pod=<pod-name>
```
This will show you the last few logs entries for the selected pod.

### Steps to Fix

1. **Increase resource allocation (if necessary)**: Check if resources (e.g., CPU, memory) are correctly allocated to the pods running your affected service.
```bash
kubectl get deployment <service-name> -o jsonpath='{.spec.template.spec.containers[0].resources.requests}'
```
Here, you'll see if any resource requests need updates.
2. **Check dependent services**: Verify that all required external resources (e.g., databases) are available and functioning correctly:
```bash
kubectl get svc <service-name>.<name-of-dependent-service>
kubectl logs -f pod=<pod-name> --since-time=1m # Check error messages
```
3. **Troubleshoot configuration or code issues**: Investigate if any misconfigurations, incorrect setup parameterizations, or internal code problems are causing errors:
```bash
kubectl exec -it <pod-name> -- /bin/bash # SSH into the container to debug local issues
# Debug code and configuration with your team
```
4. **Scale pods as required**: Adjust the number of replicas based on resource utilization and error rates:
```bash
kubectl scale deployment <service-name> --replicas=<adjusted-replica-count>
```

### Escalation if

* If the issue is complex or requires external expertise (e.g., networking, database administration).
* The issue persists for more than 30 minutes.
* No immediate solution can be identified.

For any above-scenario escalations raise an incident on your CM team with clear documentation about the alert history and previous steps taken.