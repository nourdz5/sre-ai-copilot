# DatabaseDown

**DatabaseDown**: PostgreSQL database instance is unavailable or non-responsive.

### Description
The **DatabaseDown** alert indicates that the PostgreSQL database instance, serving as a critical component for storing application data, is unreachable or unresponsive. This could be due to various reasons such as connectivity issues, incorrect configuration, or more severe problems within the database itself.

### Likely Causes

1. **Network issue**: There might be a network problem that prevents connections from being established with the database instance.
2. **Database cluster downtime**: The PostgreSQL standby database might not have automatically taken over in case of primary or replication issues.
3. **Incorrect configuration**: Configuration mistakes can occur when setting up new instances for failover, leading to an unresponsive situation upon attempting to switch to a different node.

### Steps to Diagnose

1. Verify the error message being reported by checking the application's logs where it attempts to interact with the database. This will likely indicate whether there was a specific problem that triggered the alert.
2. **Check for recent changes**: Check any deployments, upgrades, or configuration updates in the last 24 hours for potential causes.
3. Check if other instances are impacted: If using a distributed setup, verify that all other instances (both primary and standby) are operating without issues.

#### Diagnostic Command
```bash
kubectl exec -it <pod-name> -- ps aux | grep postgres
```
This will help in determining if it's the application consuming resources or other processes affecting database connectivity.

### Steps to Fix

1. **Initial Check**: Run `psql -h localhost:5432 --username db_username` and check for an empty list, indicating no sessions might mean network connectivity at minimum is intact.
   - Ensure correct configuration of hostname resolution (e.g., DNS). In cases with non-standard hostnames or configurations where DNS service relies on specific resolvers, there could be connectivity issues without raising alert-level symptoms.
2. **Verify Database Service Status**:
   ```sql
   SELECT pg_isready() AS "is_ready";
   ```
   - This query can sometimes bypass configuration problems while diagnosing service availability after reconnections or service restarts.

3. Run a test to isolate the issue: The database will likely not be accessible due to it being down, but running `pg_start_backup;` should let you assess if the cluster itself is alive and taking backups successfully (in terms of replication and data integrity when using physical replicas).

### Escalate If

1. **Database cluster unreachable indefinitely**: In cases where a database instance or its replica in a distributed or high-availability setup becomes completely unresponsive for an extended period.
2. **Replication issues persisting past service restarts**: Replication, failover, and backup statuses indicate any problems during switching from primary to standby.

Ensure the escalation follows established processes with relevant teams:

1. Inform on-call team about possible cause of issue if it's suspected to be outside immediate fix capabilities or a known incident.
2. Coordination with engineering management, and respective developers (in case an application-specific misconfiguration) for review of new features added around database interactions recently.

Regular communication is key during critical incidents like this to ensure swift resolution and the restoration of service without extensive data loss when replication strategies are employed.