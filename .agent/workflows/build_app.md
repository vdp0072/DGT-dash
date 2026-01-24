---
description: Use this workflow to design or review the entire application end-to-end. This workflow produces a complete implementation blueprint but does not execute code or make destructive changes.
---

# Build Full Application

Use this workflow to design or review the entire application end-to-end.
This workflow produces a complete implementation blueprint but does not
execute code or make destructive changes.

## Execution Order (must follow strictly)

1. **Clarify scope**
   - Confirm the application purpose.
   - Identify user roles (admin, user).
   - Identify data sensitivity.

2. **Database design**
   - Define required tables and columns.
   - Assign data types.
   - Define primary keys.
   - Recommend indexes for search-heavy fields.
   - Ensure schema supports append-only ingestion.

3. **Authorization & roles**
   - Define permissions for admin and user roles.
   - Map roles to allowed actions.
   - Identify protected operations.

4. **Data ingestion pipeline**
   - Define supported upload formats.
   - Define validation rules.
   - Define ingestion flow (parse → validate → insert).
   - Define ingestion error handling and summaries.

5. **Search & query design**
   - Identify supported search filters.
   - Define dynamic query strategy.
   - Define default limits and performance safeguards.
   - Define which fields are exposed in results.

6. **API design**
   - Define REST endpoints.
   - Define request and response schemas.
   - Define error cases.
   - Ensure APIs respect authorization rules.

7. **UI structure**
   - Define admin pages and features.
   - Define user pages and features.
   - Ensure strict separation of admin and user views.
   - Define download/export behavior.

8. **Security & privacy review**
   - Identify sensitive fields.
   - Recommend masking or restrictions.
   - Define audit logging points.
   - Identify misuse or abuse risks.

9. **Final consistency check**
   - Ensure schema, APIs, and UI align.
   - Ensure all rules are respected.
   - Highlight assumptions and open questions.

## Constraints

- Treat the local database as the single source of truth.
- Do not generate or run executable commands automatically.
- Do not perform destructive operations without confirmation.
- Follow all active agent rules.
- Prefer clarity and explicitness over brevity.

## Output format

Produce the following sections clearly labeled:

- Architecture overview
- Database schema (SQL)
- Role & permission matrix
- Ingestion flow
- Search/query strategy
- API contracts
- UI structure
- Security considerations
- Open questions / next steps
