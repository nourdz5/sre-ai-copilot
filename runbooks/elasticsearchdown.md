# ElasticsearchDown

**ElasticsearchDown Runbook**

### Description

The `ElasticsearchDown` alert indicates that the Elasticsearch service is not responding or is down. This can be a critical issue, as it affects data ingestion, search, and analytics.

### Likely Causes

*   Elasticsearch pods are not running or are terminated.
*   Elasticsearch service configuration is incorrect or missing.
*   Network issues affecting Elasticsearch communication with clients (e.g., Kubernetes cluster networking).
*   Disk space issues on the persistent storage volume used by Elasticsearch.
*   Overload or high CPU usage causing Elasticsearch to become unresponsive.

### Steps to Diagnose

1.  **Check Elasticsearch pod status**: Run `kubectl get pods -n <namespace> --watch` and verify that all Elasticsearch Pods are running in the expected state (Running or Completed).

    ```markdown
kubectl get pods -n logging -w
```

2.  **Verify service configuration**: Confirm that the Elasticsearch Service is correctly configured by checking its definition:

    ```bash
kubectl describe svc elasticsearch -n logging
```

3.  **Examine logs for issues**: Check the logs of the Elasticsearch Pods to ensure there are no error messages related to networking, disk space, or configuration:

    ```bash
kubectl logs <elspods-name> -n logging
```

4.  **Verify Kubernetes cluster network configuration**: Check that the Kubernetes cluster networking is properly configured and can communicate with the Elasticsearch service.

### Steps to Fix

1.  **Restart Elasticsearch pods**: If certain Pods are not running, you can restart them:

    ```bash
kubectl rollout.restart <elspods-name> -n logging
```

2.  **Correct or reconfigure Elasticsearch Service**: Make sure that the Elasticache service is correctly defined and configured. Common issues may include incorrect ports or misconfigured annotations.

3.  **Adjust resource limits for Elasticsearch Pods**: If overload or high CPU usage is suspected, consider adjusting Resource Requests to prevent overloading:

    ```yml
kubectl edit deployment <deployment-name> -n logging
```

4.  **Check and resolve disk space issues**: Investigate persistent storage volumes used by Elasticsearch and ensure they have sufficient space. Consider upgrading the Persistent Volumes if necessary.

### Escalate if

*   If restarting the pods does not resolve the issue, escalate to a more senior SRE member for further investigation.
*   If the cause of the issue involves multiple components or services, work with relevant teams (e.g., network, infra) to address any external problems.
*   If you're unable to fix the issue manually, raise an infrastructure ticket and request assistance from the Operations team.