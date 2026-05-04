# HighLatency

**HighLatency Runbook**

### Description

The `HighLatency` alert indicates that the average latency of incoming requests to our application is higher than the defined threshold ( currently set at 500ms). This can impact user experience, application performance, and overall system reliability.

### Likely Causes

* Insufficient resources (CPU/Memory) on Kubernetes nodes
* High network latency or congestion between nodes or between clusters
* Database or external service latency
* Misconfigured service meshes or network policies
* Application-level issues such as inefficient code or poor database queries

### Steps to Diagnose

1. **Monitor and verify the alert**: Check the monitoring dashboards, such as Grafana or Prometheus, to confirm that the high latency alert is indeed firing.
2. **Check node resource utilization**: Run `kubectl top nodes` to review CPU/Memory usage across all clusters and identify any significantly saturated nodes.
3. **Verify network conditions**: Run `kubectl get pod -A --show-labels` and filter for pods with high network I/O or packet loss (e.g., pods labeled with "slow" or "network-problems").
4. **Analyze database queries**: Review database query performance metrics, such as slow query log entries or query execution time.
5. **Inspect service meshes and network policies**: Check the configuration of service meshes (e.g., Istio) or network policies for any issues that could contribute to high latency.

### Steps to Fix

1. **Scale up nodes**: Run `kubectl scale deployment <deployment-name> --replicas=<new-replica-count>` to scale up nodes with sufficient resources.
2. **Tune service meshes and network policies**: Review configuration options and adjust settings as necessary (e.g., increase the maximum packet size).
3. **Optimize database queries**: Analyze query performance metrics, rewrite inefficient queries, or apply performance-tuning adjustments.
4. **Address high network conditions**: Run `kubectl delete pod <pod-name>` on pods identified in step 2, if applicable, and consider upgrading cluster networking configuration.
5. **Implement application-level optimizations**: Analyze code bottlenecks and implement optimizations to reduce latency.

### Escalate If:

* The alert remains active after completing the above steps
* High-latency persists despite scaling up resources or applying optimizations
* Critical system components (e.g., database, network) experience persistent issues
* Alert frequency exceeds 1/100 of the total number of requests in a 5-minute window

Escalation actions may include:

* Notifying SRE leadership and/or cloud providers for additional support
* Running emergency patches or software updates to address underlying causes