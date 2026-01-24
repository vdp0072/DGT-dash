---
description: Use this workflow when implementing or reviewing user search functionality.
---

# Build Search

Use this workflow when implementing or reviewing user search functionality.

## Steps to follow

1. Identify all supported search filters (e.g. pincode, area, city, constituency).
2. Treat all filters as optional.
3. Build a dynamic database query using only provided filters.
4. Use parameterized queries exclusively.
5. Prefer indexed columns in query conditions.
6. Apply a default result limit to prevent unbounded queries.
7. Ensure the query is strictly read-only.
8. Filter output fields based on role permissions.
9. Prepare results for display and optional download.

## Constraints

- Only user-allowed fields may be returned.
- Internal fields (IDs, timestamps, metadata) must be excluded.
- Search must not modify database state.
- Queries must respect role-based access rules.

## Output format

- Example SQL query
- Example input filters
- Example output fields
