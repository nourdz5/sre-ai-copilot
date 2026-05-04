# DiskFull

**Runbook: DiskFull Alert**

**Description**
===============

The `DiskFull` alert indicates that one of our critical Kubernetes persistent volumes (PVs) is running out of disk space, potentially affecting the availability of pods relying on these PVs.

**Likely Causes**
================

1. **Inadequate provisioning**: The specified disk size for the PV was too small, leading to a quick depletion of available space.
2. **Data growth**: The data stored in the PV has grown unexpectedly due to high ingest rates or errors during deletion processes.
3. **Misconfigured PVCs** (Persistent Volume Claims): Incorrect specification of storageClass, accessMode, or selector led to an unexpected association with a small-capacity PV.

**Steps to Diagnose**
=====================

1. **Verify the affected PV**: Use `kubectl get pv <pv-name> -o yaml` to examine the disk capacity and usage details:

    ```bash
    kubectl get pv my-pv-example -o yaml
    ```
2. **Inspect the PVCs using this PV**:
   - Find all associated PVCs: `kubectl get pvc -l pv=<pv-name>`
   - Review the PVC specifications for correct storageClass, accessMode, and selector configurations.

    ```bash
    kubectl get pvc -l pv=my-pv-example
    ```
3. **Determine if space usage is normal**:
   - Check if there are any logs or monitoring signals indicating a sudden increase in data volume.

**Steps to Fix**
================

1. **Delete Pod and Volume**: If there's a large pod using the affected PV, delete it and wait for Kubernetes to reclaim its storage and allow deletion of the PV. Ensure no pods continue to rely on the PV that will be removed.

    ```bash
    kubectl delete pod <pod-name>
    ```
2. **Scale Persistent Volumes or Upgrade Storage**:
   - Scale up the persistent volume to increase available disk space: `kubectl patch pv <pv-name> --type=merge -p '{"spec": {"capacity": {"storage": "<new-capacity>"}}}"`
    
        ```bash
        kubectl patch pv my-pv-example --type=merge -p '{"spec": {"capacity": {"storage": "10Gi"}}}'
        ```
   - Alternatively, consider replacing or upgrading to larger disks if necessary.

3. **Verify fixes**: After applying the above steps, verify that disk space has been increased and is properly allocated:

    ```bash
    kubectl describe pv <pv-name>
    ```

**Escalate If**
================

- Thresholds for disk free space (%): Set your desired threshold here. Current default: 15%.

*   **If disk usage exceeds 80%**, take the above steps before proceeding.
*   **Additional actions required if disk usage exceeds this threshold:** Notify on-call, and have operations team intervene promptly if disk space cannot be reclaimed within a 1-hour window, to mitigate potential data loss.

### Commit Message

Example commit message when documenting runbooks: `Added runbook for DiskFull Alert with clear steps for diagnosis, resolution, and escalation`