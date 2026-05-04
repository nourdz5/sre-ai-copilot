# RedisDown

**Runbook: Alert - Redis Down**
==============================

### Description

The `RedisDown` alert is triggered when the Redis service, responsible for storing and retrieving data in a cluster, becomes unavailable.

### Likely Causes

*   **Instance Failure**: One or more instances of the Redis pod may have failed or crashed.
*   **Network Connectivity Issues**: Issues with communication between the Redis pods or between Redis and other services may be causing unavailability.
*   **Configuration Errors**: Incorrect configuration settings may prevent Redis from functioning properly.
*   **Resource Exhaustion**: Low memory resources, disk space issues, or high CPU usage can lead to Redis crashing.

### Steps to Diagnose

#### 1. Verify Alert and Service Status

Check if the alert is accurate by accessing the Redis service using a client outside of Kubernetes (e.g., redis-cli).

```bash
# Outside of kubectl context, use this command to check Redis connectivity from cluster environment or load balancer/pod IP if defined
redis-cli ping <redis_pod_name_or_service_ip>
```

If there's no response:

*   Check the health status of Redis instances using `kubectl`:
    ```bash
kubectl get pods -l app=<app-name> -o jsonpath='{.items[].metadata.name}'
    ```
Check for any pods in pending, unknown or failed states.

### Steps to Fix

#### 1. Restart Redis Pods

Restart each affected pod:

```bash
# Identify all redis deployment names (redis is a common service)
deployment_names=$(kubectl get deployments -l app=<app-name> -o jsonpath='{.items[].metadata.name}')

for dep in "${deployment_names[@]}"; do
    kubectl delete pod --all --force --wait=false "$dep"
done

# Wait for pods to restart:
watch -n 1 "kubectl get deploy $dep; sleep 2"
```

This command will cycle through each deployment, scaling down and then back up (assuming the `deployment` configuration is set correctly) or simply restarting all pods if that's a possibility.

### Escalate If

If attempting to restart pods doesn’t resolve the issue:

*   Consult Kubernetes logs for relevant application and infrastructure information related to pod restarts.
```bash
kubectl logs <pod-name>
```
Verify Redis logs as well by accessing them directly through either an external Redis database or, if deployed separately, via Docker logs.

Also review monitoring dashboards for related services to identify network issues or any pattern indicating resource exhaustion.

Review Prometheus/Monitoring metrics for Kubernetes cluster resources over 24-hours period:

```bash
# This command will list out specific details which can be cross-checked. Below is example:
kubectl get hpa -o jsonpath='{.items[0].status.desiredReplicas}'
```
If the issue persists after addressing these steps, escalate to on-call and proceed with further investigation.

**Additional note:**
While reviewing logs it's always prudent to check network topology or whether there's a possibility of `node drain` causing issues due to not enough free capacity for containers.