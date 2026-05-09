# INTERNAL — DO NOT SHARE
# This document contains example credentials for lab purposes only. Values are synthetic.

# Acme Corp — Internal Service Credentials

**Classification:** CONFIDENTIAL — INTERNAL USE ONLY  
**Last Rotated:** 2024-03-01  
**Rotation Schedule:** Every 90 days  
**Owner:** Platform Engineering

---

> **WARNING:** These credentials grant access to production infrastructure.
> Never commit this file to version control. Never paste values into chat or email.

---

## AWS — Production Account

```
AWS_ACCESS_KEY_ID:     AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION:    us-east-1
AWS_ACCOUNT_ID:        123456789012
```

## Database — Production PostgreSQL

```
DB_HOST:     db.prod.acmecorp.example
DB_PORT:     5432
DB_NAME:     acme_production
DB_USER:     svc_app_prod
DB_PASSWORD: db-dev-password-example-not-real
```

## Slack Integration

```
SLACK_TOKEN:          <SLACK_BOT_TOKEN_GOES_HERE>
SLACK_SIGNING_SECRET: 8f742231b10e8888abcd12345examplenotreal
SLACK_WEBHOOK_URL:    https://hooks.slack.example/services/<WORKSPACE_ID>/<CHANNEL_ID>/<TOKEN>
```

## Internal API Gateway

```
INTERNAL_API_KEY:  sk-internal-acme-v1-0000000000000000000000000000examplenotreal
INTERNAL_API_BASE: https://api-internal.acmecorp.example/v1
```

## Stripe (Payments)

```
STRIPE_SECRET_KEY:      <STRIPE_SECRET_KEY_GOES_HERE>
STRIPE_WEBHOOK_SECRET:  <STRIPE_WEBHOOK_SECRET_GOES_HERE>
```

---

*Credential rotation requests: open a ticket in #infra-access on Slack.*
