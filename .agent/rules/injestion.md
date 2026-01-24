---
trigger: always_on
---

# Data Ingestion Rules

These rules apply whenever data is uploaded and inserted into the database.

- Only admin role may initiate data ingestion.
- Acceptable file formats are CSV, XLSX, and JSON only.
- Ingestion must be append-only; never overwrite existing records.
- Validate uploaded file headers against the database schema.
- Normalize column names to lowercase before processing.
- Ignore unknown or extra columns not present in the schema.
- Reject rows missing required fields.
- Perform all inserts inside a single database transaction.
- If validation fails, do not partially insert data.
- Always return a clear ingestion summary including:
  - Total rows processed
  - Rows inserted
  - Rows rejected
  - Reason for rejection
