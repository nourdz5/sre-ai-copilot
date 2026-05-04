# HighCPU

Here is the SRE runbook for the "High CPU" alert:

### HighCPU Runbook

#### Description
When a cluster node's CPU usage exceeds 80% average utilization over a 5-minute window, this alert will be triggered.

#### Likely Causes
* Resource-intensive workloads running on the affected node
* Memory-allocated pods consuming more CPU than expected
* Node configuration issues (e.g. inadequate resource allocation)
* Containerized applications experiencing elevated performance demands

#### Steps to Diagnose

1. **Verify Alert**: Use `kubectl get alertmanagers` and check for alerts with title "High CPU" associated with the affected node.
2. **Check Resources**:
	* `kubectl describe node <node-name>`: Verify resource utilization metrics (CPU, memory).
	* Investigate pending pods' limits and requests to understand if sufficient resources have been allocated.
3. **Container and Pod Level Investigation**:
	* `kubectl get pods --all-namespaces -o wide`: Sort by CPU allocation and look for high-utilizing containers.
	* Use the `kubetail` command (if installed) or combine the output of `kubectl get logs <pod-name>` with `kubectl describe pod <pod-name>` to investigate excessive resource usage patterns
4. **Node Configuration Check**:
	* Review node configuration: `kubectl get nodes -o yaml | grep requested`/`kubectl get nodes -o yaml | egrep '(requested CPU|memory)'

#### Steps to Fix

1. **Scale Down Resources**: Reduce resources allocated to pods running on the affected node or the underlying persistent volume claims (e.g., PVs and PVCs).
2. **Increase Resource Quota**:
	* Review node configurations: Ensure sufficient resource settings are assigned (`kubectl edit nodes <node-name>`) 
3. **Monitor with Grafana**: Set up a custom Grafana dashboard that displays CPU usage, Memory Allocation.
4. **Update Workloads**: Consider horizontal pod autoscaling (HPA) strategy to dynamically adjust the number of replicas based on resources availability.

#### Escalate if

* Node-wide resource utilization stays above 80% average for more than an hour
* Frequent "High CPU" alerts indicate a recurring issue after attempting initial fixes.
* Alert does not reset despite adequate resolution (after scaling back PODs).

These are just some general best practices to guide your work as you respond to these types of high-priority operations.