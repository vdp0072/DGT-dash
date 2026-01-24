---
description: Use this workflow when designing or reviewing the database schema.
---

# Design Database Schema

Use this workflow when designing or reviewing the database schema.

## Steps to follow

1. Identify all required entities and fields from the problem statement.
2. Define tables with clear, descriptive column names.
3. Assign appropriate data types for each column.
4. Define primary keys for all tables.
5. Identify fields that will be frequently searched or filtered.
6. Recommend indexes for those fields.
7. Check that the schema supports append-only ingestion.
8. Briefly explain the reasoning behind key design decisions.

## Constraints

- Treat the local database as the single source of truth.
- Avoid premature normalization unless clearly justified.
- Prefer simplicity and clarity over over-engineering.
- Do not introduce destructive schema changes without confirmation.

## Output format

- SQL schema definition
- Index recommendations
- Short explanation of design choices
