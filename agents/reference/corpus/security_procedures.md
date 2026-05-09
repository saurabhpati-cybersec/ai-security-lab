# Acme Corp — Security Incident Response Procedures

**Version:** 1.8  
**Owner:** Security Operations Center (SOC)  
**Classification:** INTERNAL

---

## Severity Levels

| Level    | Description                                  | Response SLA |
|----------|----------------------------------------------|--------------|
| Critical | Active breach, data exfiltration confirmed    | 15 minutes   |
| High     | Suspected breach, ransomware, insider threat  | 1 hour       |
| Medium   | Phishing campaign, policy violation           | 4 hours      |
| Low      | Suspicious activity, anomalous login          | 24 hours     |

---

## Phase 1 — Identification

1. Alert received via SIEM, user report, or automated detection.
2. SOC analyst triages alert and assigns severity within 15 minutes.
3. Affected systems and user accounts are identified and logged.

## Phase 2 — Containment

1. Isolate affected endpoints from the network (revoke VPN, disable AD account).
2. Preserve forensic evidence: do not power off affected machines — take memory snapshots.
3. Block malicious IPs/domains at the perimeter firewall.
4. Notify Legal and HR for any incidents involving employee accounts.

## Phase 3 — Eradication & Recovery

1. Remove malware or unauthorized access paths.
2. Rotate all credentials that may have been exposed.
3. Apply patches to exploited vulnerabilities before bringing systems back online.
4. Restore from verified clean backups if data integrity is in doubt.

## Phase 4 — Post-Incident Review

1. Conduct blameless post-mortem within 5 business days.
2. Document root cause, timeline, impact, and corrective actions.
3. Update runbooks and detection rules based on lessons learned.

---

*Contact: soc@acmecorp.example | Slack: #security-incidents*
