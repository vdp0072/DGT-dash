---
trigger: always_on
---

# Authorization & Role Rules

These rules govern how roles and permissions are handled.

- The system has exactly two roles: admin and user.
- Default behavior is deny access unless explicitly allowed.
- Admin role:
  - Can upload data files.
  - Can modify database content via ingestion.
  - Can access administrative endpoints and views.
- User role:
  - Has read-only access.
  - Can search and download query results.
- Always validate role permissions before performing any database operation.
- Never expose admin-only actions, UI elements, or API endpoints to users.
- Role checks must occur before any business logic or database access.
