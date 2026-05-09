# Acme Corp — Information Security Policy

**Version:** 2.4  
**Effective Date:** 2024-01-15  
**Owner:** Information Security Team

---

## 1. Password Policy

All employee passwords must meet the following requirements:

- Minimum length: 14 characters
- Must include uppercase, lowercase, digits, and at least one special character
- Passwords must be rotated every 90 days
- Do not reuse the last 12 passwords
- Multi-factor authentication (MFA) is mandatory for all corporate systems
- Shared passwords are strictly prohibited; each service must have a unique credential

## 2. Data Handling

- **Confidential** and **Internal** data must not be sent to personal email addresses
- Customer PII must be encrypted at rest (AES-256) and in transit (TLS 1.2+)
- Data must not be stored on unmanaged personal devices
- Removable media (USB drives) require IT approval and encryption before use
- Sensitive documents must be shredded before disposal; do not place in standard recycling

## 3. Approved Tools

The following tools are approved for corporate use:

| Category        | Approved Tool           |
|-----------------|-------------------------|
| Version control | GitHub Enterprise        |
| Communication   | Slack (corporate tenant) |
| Cloud storage   | Google Drive (corporate) |
| Password manager| 1Password (corporate)    |
| Video calls     | Zoom (licensed accounts) |

Any tool not on the approved list requires a security review request submitted to security@acmecorp.example.

## 4. Incident Reporting

Suspected security incidents must be reported to the Security Operations Center at soc@acmecorp.example or via the internal Slack channel #security-incidents within one hour of discovery.

Employees who fail to report known incidents may face disciplinary action up to and including termination.
