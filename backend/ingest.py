import os
import pandas as pd
import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from backend.models import IngestionSummary, UserData
from backend.auth import get_current_admin
from backend.database import get_db

router = APIRouter()

REQUIRED_COLUMNS = {"name"}
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json"}

@router.post("/ingest", response_model=IngestionSummary)
async def ingest_data(
    file: UploadFile = File(...),
    current_user: UserData = Depends(get_current_admin)
):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    content = await file.read()
    
    # 1. Parse File
    try:
        if ext == ".csv":
            df = pd.read_csv(io.BytesIO(content))
        elif ext == ".xlsx":
            df = pd.read_excel(io.BytesIO(content))
        elif ext == ".json":
            df = pd.read_json(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    # 2. Normalize Headers
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Check Required Columns
    if not REQUIRED_COLUMNS.issubset(df.columns):
        missing = REQUIRED_COLUMNS - set(df.columns)
        raise HTTPException(status_code=400, detail=f"Missing required columns: {missing}")

    with get_db() as db:
        # 3. Create Ingestion Log Entry
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO ingestion_logs (filename, uploaded_by_user_id, total_rows, inserted_rows, rejected_rows) VALUES (?, (SELECT id FROM users WHERE username=?), 0, 0, 0)",
            (filename, current_user.username)
        )
        log_id = cursor.lastrowid
        db.commit()

        # 4. Process Rows
        total_rows = len(df)
        inserted_count = 0
        rejected_count = 0
        
        valid_records = []
        
        def get_val(row, col):
            if col in row.index and pd.notna(row[col]):
                return str(row[col])
            return None

        for _, row in df.iterrows():
            rec = {
                "name": get_val(row, "name"),
                "fathers_name": get_val(row, "fathers_name"),
                "age": int(row["age"]) if "age" in row.index and pd.notna(row["age"]) else None,
                "gender": get_val(row, "gender"),
                "constituency": get_val(row, "constituency"),
                "city": get_val(row, "city"),
                "company": get_val(row, "company"),
                "phone": get_val(row, "phone") or "",  # Default to empty string for index
                "misc": get_val(row, "misc"),
                "source_file_id": log_id
            }
            
            if not rec["name"]:
                rejected_count += 1
                continue
                
            valid_records.append(rec)

        # 5. Bulk Insert
        try:
            cursor.executemany('''
                INSERT OR IGNORE INTO records (name, fathers_name, age, gender, constituency, city, company, phone, misc, source_file_id)
                VALUES (:name, :fathers_name, :age, :gender, :constituency, :city, :company, :phone, :misc, :source_file_id)
            ''', valid_records)
            
            inserted_count = cursor.rowcount  # rowcount tells us how many were actually inserted
            rejected_count += len(valid_records) - inserted_count # Count ignored rows as rejected (or we can call them duplicates)
            
            cursor.execute('''
                UPDATE ingestion_logs 
                SET status='success', total_rows=?, inserted_rows=?, rejected_rows=?
                WHERE id=?
            ''', (total_rows, inserted_count, rejected_count, log_id))
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            cursor.execute('''
                UPDATE ingestion_logs 
                SET status='failed', rejection_reason=?
                WHERE id=?
            ''', (str(e), log_id))
            db.commit()
            raise HTTPException(status_code=500, detail=f"Database error during insertion: {str(e)}")

    return IngestionSummary(
        filename=filename,
        status="success",
        total_rows=total_rows,
        inserted_rows=inserted_count,
        rejected_rows=rejected_count,
        log_id=log_id
    )
