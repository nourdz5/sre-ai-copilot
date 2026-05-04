# ReplicaSetDown

**ReplicaSet Down Runbook**
=========================

### Description

When an application experiences a ReplicaSetDown alert, it indicates that the desired replication factor is not being met due to faulty or unhealthy replicas in the cluster. This runbook outlines the steps to diagnose and resolve the issue.

### Likely Causes

* Insufficient Pod replicas
* Pods in `CrashLoopBackOff` state
* Pods failing health checks
* Outdated Kubernetes manifests
* Incorrect deployment configurations

### Steps to Diagnose

1. **Check ReplicaSet status**: Run `kubectl get replicaset <namespace>/<replica-set-name> -o yaml` to verify the current replica set's status.
```bash
kubectl get replicaset default/your-replica-set -o yaml
```
2. **List Pods in the ReplicaSet**: Run `kubectl get pods <namespace> -l k8s-app=<replica-set-name>` to list all pods associated with the ReplicaSet .
```bash
kubectl get pods default -l k8s-app=your-replica-set
```
3. **Check Pod health status**: Run `kubectl describe pod <pod-name>` for each Pod listed in step 2 and verify their health status.
```bash
kubectl describe pod your-pod-name
```
4. **Inspect ReplicaSet manifest**: Review the ReplicaSet YAML file to ensure its configuration aligns with the desired replication factor.
```bash
kubectl get replicaset default/your-replica-set -o yaml > /path/to/local/file.yaml
```

### Steps to Fix

1. **Scale up or down**: Adjust the replica count in the ReplicaSet manifest according to necessity and execute the changes via `kubectl apply`.
```bash
sed 's/relicas: 3,/relicas: 4,/' /path/to/manifest.yaml > /path/to/temp-fix.yaml
kubectl apply -f /path/to/temp-fix.yaml
```
2. **Delete problematic Pods**: Use the output of step 2 to identify Pods in `CrashLoopBackOff` state and delete them with `kubectl delete`.
```bash
kubectl delete pod your-affected-pod
```
3. **Update outdated ReplicaSet manifest**: Update the YAML file for the affected ReplicaSet from its original location or use a tool like Kustomize/Keeper to manage versions.
```bash
kp diff mycluster --path /path/to/original/manifest.yaml > /path/to/temp-fix.yaml
kubectl apply -f /path/to/temp-fix.yaml
```
4. **Validate changes**:
Confirm the ReplicaSet status has improved by viewing its updated configuration and checking for Pods with failed health checks.

### Escalate if

* No improvements are seen after completing the above steps.
* Issue persists across multiple availability zones or regions.
* Changes require significant manual updates to Deployment/StatefulSet configurations.