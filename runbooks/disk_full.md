# DiskFull Runbook

## Symptoms
- Disk usage above 85%
- Write errors in logs

## Steps
1. Check disk usage: `df -h`
2. Find large files: `du -sh /* | sort -rh | head -20`
3. Clean /tmp: `rm -rf /tmp/*`
4. Check log rotation config
5. Archive old logs if needed

## Escalate if
- Disk fills up faster than expected
- Unable to free enough space
