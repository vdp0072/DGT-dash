---
description: Use this workflow when an admin uploads a CSV, XLSX, or JSON file and data needs to be validated and inserted into the database.
---

# Ingest Data

Use this workflow when an admin uploads a CSV, XLSX, or JSON file
and data needs to be validated and inserted into the database.

## Steps to follow

1. Identify the uploaded file type (CSV, XLSX, or JSON).
2. Read and parse the file contents.
3. Normalize column names (lowercase, trim whitespace).
4. Validate headers against the database schema.
5. Identify required fields and check for missing values.
6. Separate valid rows from invalid rows.
7. Insert valid rows using a single database transaction.
8. Do not overwrite or modify existing records.
9. Roll back the transaction if a fatal error occurs.
10. Generate an ingestion summary.

## Ingestion summary must include

- Total rows processed
- Rows successfully inserted
- Rows rejected
- Reasons for rejection

## Constraints

- Only admin role may perform ingestion.
- Ingestion must be append-only.
- Unknown columns must be ignored.
- No partial inserts on failure.

## Output format

- Clear ingestion summary
- Sample of rejected rows (if any)
