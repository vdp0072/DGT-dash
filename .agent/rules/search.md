---
trigger: always_on
---

# Search & Query Rules

These rules govern how search and filtering are implemented and exposed.

- All search filters are optional.
- Build database queries dynamically based only on provided filters.
- Use parameterized queries exclusively; never interpolate raw user input.
- Prefer indexed columns when constructing query conditions.
- Apply a default result limit to prevent unbounded queries.
- Never expose internal fields such as:
  - Primary keys
  - Timestamps
  - Internal metadata
- Search results must respect role-based access rules.
- Queries must be read-only and must not modify database state.
