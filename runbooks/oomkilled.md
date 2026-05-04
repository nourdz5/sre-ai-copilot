# OOMKilled

**OOM Killed Runbook**
=======================

### Description
-----------------

`oom-killed` means the Kubernetes node has terminated a container due to Out Of Memory (OOM) issues.

If you're seeing repeated `oom-killed` events, it may be indicative of:

* Resource bottlenecks or misconfigurations within the cluster or application.
* Unsustainable memory usage patterns.

This runbook guides you through identifying and addressing these potential root causes.

### Likely Causes
----------------

1. **Insufficient node resources**: Node cannot allocate enough memory to handle the requested container resource requirements.
2. **Misconfigured resource requests/limits**: Container resource requests are higher than what's available on the node, but limits allow for over-allocations, leading to OOMKilled events.

### Steps to Diagnose
--------------------

### 1. Check Node Resource Utilization

```bash
kubectl describe node <node_name>
```

Check if the node has enough remaining memory:

```bash
kubectl top nodes --sort-by=memory
```

Verify memory usage for running containers:

```bash
kubectl top pods -n <namespace> --containers --sort-by=memory
```

### 2. Verify Resource Requests and Limits

Check resource requests and limits set in your pod's YAML configuration.

```bash
kubectl get pods/<pod_name> -o yaml | grep resources
```

Verify these values match the provided node's capabilities (CPU and Memory).

**Step 3: Check System Level Metrics**

Use system level metrics, e.g., using Prometheus or other monitoring tools:
1. Identify `kube_node_oom_events` in Prometheus alert rules.

```markdown
# Identify OOM Events
alert: {
    expr: kube_node_oom_events{node="<node_name>"}
    for: 5m 
}
```
2. Check which pod(s) were terminated (OOMKilled).

```bash
kubectl describe node <node_name> | grep OOMEVENT
```

### Steps to Fix
----------------

**1. Increase Node Resources**

a. **Verify**: Scale up the related node(s):
   ```bash
   kubectl scale node <cluster_name>/<node_name> --replicas=<count>
   ```
b. **Apply**: Deploy these changes, or update YAML definitions (e.g., via `kustomize`).

**2. Adjust Container Resource Requests / Limits**

a. **Verify**: Check if container resource limits are sufficient to prevent OOMKills.

```markdown
# Example of updating yaml file for correct values.
apiVersion: v1
kind: Pod
metadata:
name: example-pod

spec:
containers:
  - name: nginx
    image: nginx 
    resources:
      requests:
        memory: "150Mi"
```
b. **Apply**: Deploy these changes.

### Escalate If
-----------------

* Persistent OOMKilled events affecting performance or availability.
* Insufficient knowledge to diagnose root causes or identify node misconfigurations.

Please engage your on-call incident handler, SRE team members, or an expert pod for further guidance and assistance.