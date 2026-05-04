# CertificateExpiring

**Certificate Expiring Runbook**
=====================================

### Description

The CertificateExpiring alert is triggered when a TLS certificate used by the Kubernetes cluster is about to expire within a specified time frame (7 days by default).

### Likely Causes

* Ignored certificate renewals or manual expiration of certificates
* Configuration errors in the certificate management tool (e.g., cert-manager)
* Cluster configuration changes affecting certificate expiration

### Steps to Diagnose

1. **Verify certificate status**: Run `kubectl get certificatessigningrequests -n <namespace>` to list all signing requests for the cluster.
2. **Check certificate Expiration**: Use `kubectl describe certificatesigingrequest` on the relevant object to view its lifecycle details, which includes expiration times.
3. **Review Cluster Configurations**: Verify the configuration of any certificate management tools (e.g., cert-manager) used in the cluster.

### Steps to Fix

1. **Initiate Renewal Process**:
	* For cert-manager: Update the `Issuer` resource and renew the certificates; e.g., `kubectl apply -f issuercfg.yaml`
	* Alternatively, manually obtain a certificate through your external issuer.
2. **Verify Certificate Installation**: Ensure that the renewed certificate is successfully applied to affected resources (e.g., ingress controllers).
3. **Review Post-Renewal Validation**:
	* Run `kubectl get certificatessigningrequests -n <namespace>` and confirm certificate updates have propagated across all relevant applications.

### Escalate if

1. **Certificate cannot be renewed**: If the renewal process fails, escalate for potential issues with external issuers.
2. **Multiple affected services** : When the impact of this issue is not limited to a single service or function, consider escalating as necessary based on team assignments for various services impacted by unfulfilled CertificateExpiring Alert.

Additional best practices:

* Regularly schedule automated certificate rotation scripts to minimize potential gaps between certificates expiration and renewal process.
* Ensure regular backup of your cluster configurations to facilitate rapid recovery in case anything goes wrong.