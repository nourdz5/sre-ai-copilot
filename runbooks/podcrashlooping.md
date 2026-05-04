# PodCrashLooping

**PodCrashLooping Runbook**
==========================

### Description

A Pod is considered Crash Looping Backoff when it enters a state of continuous restarts due to crashes, exceeding the maximum restart limit set by Kubernetes. This can be caused by various issues such as:

* Deadlocked or stuck pods
* Out-of-memory (OOM) errors
* Container misconfigurations
* Network issues

### Likely Causes

1. **Misconfigured containers**: Resources (CPU, memory, etc.) might not match the system's requirements.
2. **Incorrect container startup sequence**:
	* Containers that rely on other running services and fail to start in a stable order
3. **Lack of proper resource reservations**:
	* Inadequate CPU/RAM reservations limit pod's runtime stability
4. **Misbehaving containers**: Crashing, terminating abnormally or requiring excessive time

### Steps to Diagnose

1. **Get the namespaced resources**:
	+ Identify all pods within a specific namespace: `kubectl get pods --all-namespaces | grep <namespace>`
2. **View pod logs**:
	+ Tail recent log entries for a pod `kubectl logs -f <pod-name> --namespace=<namespace>` to identify symptoms of errors and crashes
3. **Verify resource utilization:**
	+ Check whether the pods consume available resources properly by executing: `kubectl describe pod <pod-name> | grep 'Containers:.*Resources'`
4. **Look up related services (if present)?**

### Steps to Fix

**Case 1: Resource Configuration Misalignment**

1. Verify CPU, Memory limits & requests:
	* Edit config file (`kubeadm`, `manifests/etc/...`)
	* Set more generous resource availability as needed
2. Check the container(s) configuration (image tags or version):

`kubectl describe deployment <deployment-name>`

**Case 2: Resource Reservation Issue**

1. Verify if CPU and/or Memory settings have been set to be too low:
	+ Identify correct min request, lims setting via a `kubeadm.yml`
```bash
$ kubectl get pods -l "app=<app_name>" -o jsonpath='{range .items[0]}' --namespace <namespace>

    spec:
      containers:
        ...
        resources:
          requests:
            cpu: 100m
          limits:
            cpu: 512m
```

2. Adjust as required

**Case 3: Container misconfiguration**

1. Review configuration for each container including their run script, environment variables (Env), and any mounted Volumes with correct paths: 
```bash
    kubectl describe pod <pod-name> | grep "Volumes"
```
Modify and adapt as necessary


### Escalate if:

* The cause is still unknown after executing all the steps above, it's crucial to raise the issue to relevant teams like DevOps, Infrastructure, or development
* Failure modes indicate potential security threats (crashing due to file system modifications)

Make sure to include any additional context and specific details as relevant. Regularly review these guidelines and ensure ongoing relevance by refining them with your team's shared knowledge over time!