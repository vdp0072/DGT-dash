import os
import pandas as pd
import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.models import IngestionSummary, UserData
from backend.auth import get_current_admin
from backend.database import get_db, is_sqlite

router = APIRouter()

REQUIRED_COLUMNS = {"name"}
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json"}

def get_val(row, col):
    if col in row.index and pd.notna(row[col]):
        return str(row[col])
    return None

@router.post("/ingest", response_model=IngestionSummary)
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserData = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # 1. Validation
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # 2. Log Entry
    # Create log entry
    if is_sqlite():
        db.execute(
            text("INSERT INTO ingestion_logs (filename, uploaded_by_username, total_rows, inserted_rows, rejected_rows) VALUES (:f, :u, 0, 0, 0)"),
            {"f": filename, "u": current_user.username}
        )
        db.commit()
        log_id = db.execute(text("SELECT last_insert_rowid()")).scalar()
    else:
        # Postgres supports RETURNING
        res = db.execute(
            text("INSERT INTO ingestion_logs (filename, uploaded_by_username, total_rows, inserted_rows, rejected_rows) VALUES (:f, :u, 0, 0, 0) RETURNING id"),
            {"f": filename, "u": current_user.username}
        )
        log_id = res.scalar()
        db.commit()

    try:
        # 3. Read Content
        contents = await file.read()
        if ext == '.csv':
            df = pd.read_csv(io.BytesIO(contents))
        elif ext == '.xlsx':
            df = pd.read_excel(io.BytesIO(contents))
        else:
            df = pd.read_json(io.BytesIO(contents))

        # 4. Normalize & Validate
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
        
        if 'name' not in df.columns:
            db.execute(
                text("UPDATE ingestion_logs SET status = 'failed', rejection_reason = 'Missing name column' WHERE id = :id"),
                {"id": log_id}
            )
            db.commit()
            raise HTTPException(status_code=400, detail="Missing 'name' column")

        total_rows = len(df)
        inserted_count = 0
        rejected_count = 0
        valid_records = []

        for _, row in df.iterrows():
            rec = {
                "name": get_val(row, "name"),
                "fathers_name": get_val(row, "fathers_name"),
                "age": int(row["age"]) if "age" in row.index and pd.notna(row["age"]) else None,
                "gender": get_val(row, "gender"),
                "area": get_val(row, "area") or get_val(row, "constituency"), # Fallback for old files
                "city": get_val(row, "city"),
                "company": get_val(row, "company"),
                "phone": str(get_val(row, "phone") or ""),
                "misc": str(get_val(row, "misc") or ""),
                "source_file_id": log_id
            }
            
            if not rec["name"]:
                rejected_count += 1
                continue
                
            valid_records.append(rec)

        # 5. Bulk Insert
        if valid_records:
            if is_sqlite():
                sql = '''
                    INSERT OR IGNORE INTO records (name, fathers_name, age, gender, area, city, company, phone, misc, source_file_id)
                    VALUES (:name, :fathers_name, :age, :gender, :area, :city, :company, :phone, :misc, :source_file_id)
                '''
            else:
                sql = '''
                    INSERT INTO records (name, fathers_name, age, gender, area, city, company, phone, misc, source_file_id)
                    VALUES (:name, :fathers_name, :age, :gender, :area, :city, :company, :phone, :misc, :source_file_id)
                    ON CONFLICT (name, phone) DO NOTHING
                '''
            
            result = db.execute(text(sql), valid_records)
            inserted_count = result.rowcount
            rejected_count += len(valid_records) - inserted_count

        # 6. Update Log
        status = "success" if rejected_count == 0 else ("partial" if inserted_count > 0 else "failed")
        db.execute(
            text("UPDATE ingestion_logs SET status = :s, total_rows = :t, inserted_rows = :i, rejected_rows = :r WHERE id = :id"),
            {"s": status, "t": total_rows, "i": inserted_count, "r": rejected_count, "id": log_id}
        )
        db.commit()

        return IngestionSummary(
            filename=filename,
            status=status,
            total_rows=total_rows,
            inserted_rows=inserted_count,
            rejected_rows=rejected_count,
            rejection_reason=None,
            log_id=log_id
        )

    except Exception as e:
        db.rollback()
        db.execute(
            text("UPDATE ingestion_logs SET status = 'failed', rejection_reason = :r WHERE id = :id"),
            {"r": str(e), "id": log_id}
        )
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/clear-db")
async def clear_database(
    current_user: UserData = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        # Delete records first (linked to logs)
        db.execute(text("DELETE FROM records"))
        # Delete logs
        db.execute(text("DELETE FROM ingestion_logs"))
        db.commit()
        return {"detail": "Database cleared successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear database: {str(e)}")
