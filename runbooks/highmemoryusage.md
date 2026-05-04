# HighMemoryUsage

**High Memory Usage Runbook**
==========================

### Description

This runbook is for high memory usage incidents in the Kubernetes cluster. High memory usage can lead to OutOfMemory errors, slow application performance, and even cluster crashes.

### Likely Causes

* **Insufficient resource allocation**: Containers or pods are allocated insufficient resources, leading to oversaturation of worker nodes.
* **Memory-intensive applications**: Applications or services with high memory requirements are running on the cluster, contributing to overall memory usage.
* **Resource leaks**: Memory leaks in applications or services that consume increasing amounts of memory over time, causing a gradual increase in overall memory usage.

### Steps to Diagnose

1. **Check node resource utilization**:
```bash
kubectl get nodes -o wide --sort-by='memory(bytes)'
```
This command will list all nodes with their available memory (in bytes). Monitor the node with the highest utilization.
2. **Check pod container logs**:
```bash
kubectl logs <pod_name> -c <container_name>
```
Navigate to the logs of relevant containers and check for resource-intensive applications or resource leaks.
3. **Check pod metrics**:
```bash
kubectl top pod <pod_name>
```
Examine the pod's CPU, memory, and other resources usage.
4. **View node logs**:
On a suspect node, use `kubectl logs -c` to examine the system logs for signs of resource exhaustion or high memory pressure.

### Steps to Fix

1. **Scale down or delete unnecessary pods**:
 Identify pods consuming excessive memory and scale them down or delete them if no longer needed.
```bash
kubectl scale deployments/<deployment_name> --replicas=<new_replica_count>
```
or
```bash
kubectl delete pod <pod_name>
```
2. **Increase resource allocations for pods**:
 If necessary, update the deployment configuration to allocate more resources (such as memory) to pods that require it.
```bash
kubectl apply -f <yaml_file.yaml> | kubectl diff -f -
```
3. **Fix application-level issues**:
 Investigate and resolve application-level performance problems by analyzing logs, performance metrics, or collaborating with the development team.

### Escalate if

* High memory usage persists on multiple nodes after applying runbook steps.
* System crashes occur due to exhaustion of available memory.
* Resource utilization exceeds expected levels for extensive periods (e.g., > 48 hours).

Note:

1. In case of a critical cluster situation where the root cause is uncertain, consider creating an emergency namespace or temporarily offloading some services onto separate clusters until normal operations can be resumed.

This runbook should provide effective guidance on reducing the frequency or impact of high memory usage in your Kubernetes cluster by providing clear step-by-step instructions for diagnosing and mitigating issues.