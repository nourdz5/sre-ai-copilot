# NodeNotReady

**NodeNotReady Runbook**
==========================

### Description

The `NodeNotReady` alert indicates that one or more nodes in the Kubernetes cluster are not ready for accepting new workloads. This can be caused by various issues, such as network connectivity problems, disk full, resource constraints, or software faults.

### Likely Causes

* Network connectivity issue: Check if the node can communicate with other nodes and the api-server.
* Disk full: Verify that there is sufficient free space on the node's filesystems.
* Resource constraint:
	+ Low memory (memory pressure >= 1)
	+ Low disk (diskpressure > 0.3 and not containerized)
	+ Unhealthy CPU load average
* Software faults: Check for software issues such as kernel panics, crashes, or errors in the log files.

### Steps to Diagnose

1. **Get node status**:
```bash
kubectl get nodes -o jsonpath='{.items[].status.conditions}'
```
This will show you the condition of each node. Look for nodes with a "Ready" condition of `false`.
2. **Check node logs**:
```bash
kubectl logs <node-name>
```
Review the log output to identify any error messages or warnings related to the issue.
3. **Verify network connectivity**:
```bash
kubectl debug <node-name>
```
This will create a temporary pod on the node with debugging tools, which can help you investigate networking issues.
4. **Check disk space and resource utilization**:
```bash
kubectl exec <node-name> -c systemd -- df -h
kubectl get pods -o jsonpath='{.items[].spec.containers[].resources}'
```
Verify that there is sufficient free space on the node's filesystems and that resource utilization is within acceptable limits.
5. **Check for software faults**:
```bash
kubectl exec <node-name> -c systemd -- journalctl
```
Review system log files (such as journald) to identify any kernel panics, crashes, or other errors.

### Steps to Fix

1. **Reboot the node** (if applicable):
	+ If the issue is specific to a particular node and not a widespread problem, you can try rebooting the node.
```bash
kubectl debug <node-name> --image=ubuntu:20.04 -- command '/sbin/reboot'
```
2. **Scale down clusters**:
	+ Temporarily reduce cluster resources (e.g., number of replicas) to prevent additional stress on the system.
3. **Free up disk space** (if necessary):
	+ Identify and delete any unnecessary data or logs to free up disk space.
4. **Add resources** (if necessary):
	+ Scale up clusters by adding more nodes if there are resource constraints.
5. **Troubleshoot further issues**: Use the troubleshooting guide linked below to identify and address additional problems.

### Escalate if

* The issue is not resolved after completing all steps above.
* Additional assistance from more experienced personnel is required.
* Critical applications or services affected by this outage require specialized support (e.g., team lead, architect).

**Troubleshooting Guide**: [Insert link to internal troubleshooting guide]

Note: Always verify that changes made during remediation do not introduce new issues before proceeding with further steps.