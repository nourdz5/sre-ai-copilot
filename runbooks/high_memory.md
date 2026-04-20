# HighMemoryUsage Runbook

## Symptoms
- Memory usage above 90%
- OOMKilled events in logs
- Pod restarts

## Steps
1. Check which pod is consuming memory: `kubectl top pods -n <namespace>`
2. Check for memory leaks in recent deployments: `kubectl rollout history deployment/<name>`
3. If OOMKilled: `kubectl rollout undo deployment/<name>`
4. Check DB connection pool — unclosed connections cause memory buildup
5. Restart if needed: `kubectl rollout restart deployment/<name>`

## Escalate if
- Memory leak persists after restart
- Multiple pods affected
