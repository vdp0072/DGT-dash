---
trigger: always_on
---

# Security & Privacy Rules

These rules govern handling of sensitive data and system safety.

- Treat the following fields as sensitive by default:
  - Phone numbers
  - Email addresses
  - Social media links
  - Location identifiers beyond city/constituency
- Recommend masking or partial exposure of sensitive fields
  for user role views and downloads.
- Restrict bulk or large data exports for user role unless explicitly allowed.
- Require audit logging for:
  - Admin uploads
  - User search and download actions
- Never store or expose plaintext passwords or secrets.
- Never expose stack traces, SQL errors, or internal system details to users.
- Prefer explicit, user-friendly error messages over technical ones.
