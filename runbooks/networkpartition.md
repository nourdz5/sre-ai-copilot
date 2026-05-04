# NetworkPartition

**NetworkPartition Runbook**

### Description

The `NetworkPartition` alert indicates that there is a network partition between the application pod(s) and/or services. This can cause connectivity issues, slow performance, or even prevent communication between affected pods.

### Likely Causes

* Network misconfiguration (e.g., incorrect subnet settings)
* Kubernetes network policies or Calico rules blocking traffic
* Incorrect or expired IP addresses in service definitions
* Hardware failures (switches, routers, etc.)

### Steps to Diagnose

1. **Check pod status**: Verify that pods are running and networking is enabled using `kubectl get pods --all-namespaces`
2. **Inspect network policies**: Check if there are any network policies or Calico rules blocking traffic between pods/services: `kubectl describe deployment <deployment_name>` (for network policy) or `calicoctl get bgpconfig` (for Calico configuration)
3. **Review service definitions**: Inspect service definition files for expired or incorrect IP addresses: `kubectl get svc -o yaml`
4. **Check node networking**: Verify that nodes have a working network setup and can communicate with the cluster:
	* `kubectl get nodes -o jsonpath='{.items[0].status.conditions[?(@.type=="NetworkUnavailable")]} '
	* `kubectl describe node <node_name>`
5. **Use kubectl debug commands**:
	* `kubectl exec -it <pod_name> -- ping <other_pod_or_svc>` (attempt to establish a network connection)
	* `kubectl attach -i <pod_name>` ( attach to the pod container and inspect its networking settings)

### Steps to Fix

1. **Update pod subnet**: Adjust pod subnet settings in the `networkPolicy` configuration files (`yaml`/`json`): modify `/etc/kubernetes/config.yaml` (on etcd node)
2. **Modify network policies or Calico rules**: Update `yaml`/`json` definition of policies/rules to permit traffic flow
3. **Refresh service definitions**: Update IP addresses or change service port(s) in YAML/JSON:
	* Modify `spec.selector.*_port_*` section(s)
4. **Restart affected nodes/services**:
	* `kubectl drain <node_name>` (optional, only when necessary)
	* `kubernify restart -f /etc/kubernetes/config.yaml`

### Escalate if:

* Pod networking issues persist after all troubleshooting efforts
* Connectivity problems continue to hinder applications functionality despite resolved pod networking issues

Always **document** changes made during this process and ensure the SRE keeps up with the changes through version history of `etcd`.