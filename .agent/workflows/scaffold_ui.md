---
description: Use this workflow when designing frontend UI for admin or user roles.
---

# Scaffold UI

Use this workflow when designing frontend UI for admin or user roles.

## Steps to follow

1. Identify the role (admin or user).
2. Identify the feature being implemented (upload, search, download).
3. Define required pages and routes.
4. Define UI components and their responsibilities.
5. Ensure strict separation between admin and user views.
6. Ensure admin-only controls are not visible to users.
7. Keep layouts minimal, functional, and easy to use.
8. Explicitly label actions that modify data or trigger downloads.

## Constraints

- UI must reflect backend role-based access rules.
- UI hiding does not replace backend authorization.
- Avoid exposing internal identifiers or system details.
- Prefer tables and simple forms over complex UI widgets.

## Output format

- Page and route list
- Component list
- Brief UX notes
