# PersistentVolumeError

**Runbook:** PersistentVolumeError

**Description**
----------------

The `PersistentVolumeError` alert occurs when a Persistent Volume (PV) is failing to attach to a node, or is in an error state. This can lead to failures in stateful applications that rely on persistent storage.

**Likely Causes**
-----------------

* Node failure: The node where the PV is attached has crashed or is unresponsive.
* Volume mismatch: The PV is not compatible with the node's Kubernetes version or storage configuration.
* Storage device failure: The underlying storage device (e.g. hard drive) is failing.
* Networking issue: Unable to communicate between nodes due to connectivity issues.

**Steps to Diagnose**
----------------------

1. **Check PVC status**: Run `kubectl get pvc <pvc-name> -o yaml` to view the PVC's current status and last error message (if any).
2. **Verify PV status**: Run `kubectl get pv <pv-name> -o yaml` to check the PV's current status, node attachment information, and capacity.
3. **Check node logs**: Check the kubectl logs for the problematic node: `kubectl logs <node-name> --since=1m`. Look for any storage or network-related errors.
4. **Verify network connectivity**: Run a network command (e.g., `ping`, `telnet`) to verify that nodes can communicate with each other.

**Steps to Fix**
-----------------

### Reattach PV

1. Check if the node has recovered: Before reattaching, ensure the node is up and running.
2. Deactivate the affected persistent volume: Run `kubectl patch pv <pv-name> -p '{"status":{"phase": "FailedReconnect"}}'`.
3. Let the cluster recognize the failure: Wait for 5-10 minutes to give the scheduler a chance to rediscover available nodes.

### Reclaim and re-create PV

1. Delete the affected persistent volume: Run `kubectl delete pv <pv-name> --force`.
2. Reclaim the related statefulsets (if any): Run `kubectl drain <node-name>` followed by `kubectl delete sts <sts-name> --ignore-existing`. Note: this will temporarily shut down your app, so plan downtime accordingly.
3. Create a new persistent volume and claim it: Use `kubectl create -f pv-spec.yaml` followed by `kubectl get pvc` to verify.

**Escalate if**
----------------

* The issue persists after exhausting troubleshooting steps above
* The node is unresponsive or has been terminated due to excessive errors.
* Application users report prolonged outages or issues writing data