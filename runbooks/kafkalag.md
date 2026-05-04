# KafkaLag

**KafkaLag Runbook**
================--------

### Description

The `KafkaLag` alert is triggered when the lag between a Kafka broker's commit log and the current state of the ZooKeeper metadata exceeds a certain threshold (set to 10 minutes in this case). This can indicate a range of issues, from transient problems with replication to more serious data integrity concerns.

### Likely Causes

*   Replication lag due to network or JVM pause
*   High CPU load on brokers causing GC issues
*   Data corruption or lost writes
*   Inconsistent leader election or partition allocation

### Steps to Diagnose

1.  **Check Broker Load and Resources**:
    ```bash
    kubectl get nodes -o CustomColumns=NAME,CPU REQUESTS,MEMORY REQUESTS | grep <broker_name>
    ```
    
    Verify that the broker has sufficient resources (CPU, RAM) and that there might not be other system-wide resource issues contributing to the high load.

2.  **Check Broker Logs**: Look for any error messages in the past few hours. Specifically check log4j logs.
    ```bash
    kubectl exec -it kafka-broker-<replica> cat /var/log/kafka.log | grep "ERROR" | tail -n 10
    ```
    
    If there are no errors, it's a good sign, but keep monitoring for potential problems.

3.  **Check ZooKeeper Quorum**:
    ```bash
    kubectl exec -it zookeeper-0-\<replica> /bin/bash
   zkCli.sh # type 'ls/' , check and confirm your quorums is ready 
     ```
    
    Verify that all nodes in the cluster can connect to each other within ZooKeeper.

4.  **Check for Data Corruption or Inconsistent Leader Election**:
    ```bash
    kubectl exec -it kafka-broker-<replica> bin/kafka-log-dirs.sh
    ```
    
    Make sure partitions are properly distributed, and there's no indication of data corruption.

### Steps to Fix

1.  **Identify Broker with the Highest Lag**: If a broker is consistently leading in terms of lag, it might be experiencing issues that need immediate attention or may indicate underlying network issues.
    ```bash
    kubectl exec -it kafka-broker-<replica> bash
    # Navigate to /var/log and run the following command
    grep "ERROR" logs/* | awk '{print $4}' | sort | uniq -c | sort -rn
    ```
    
    Note down any error messages for potential troubleshooting during restart.

2.  **Restart Problematic Broker**: This may resolve transient issues and get replication back on track.
    ```bash
    kubectl delete pod kafka-broker-<replica>
    ```

3.  **Adjust Replication Settings as Necessary**: If broker resources are under strain, consider reducing the minimum ISR size to allow replicas with high lag to participate in sync.

### Escalate if

*   This is a repeat offense and indicates systemic issues.
*   Broker performance consistently degrades over several alert triggers without signs of improvement after manual intervention.
*   Replication remains stuck for an extended period, likely indicating an underlying infrastructure problem that requires direct involvement of Ops team.