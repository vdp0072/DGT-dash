from fastapi import APIRouter, Depends, Query
from backend.models import SearchResponse, RecordOut, UserData
from backend.auth import get_current_user
from backend.database import get_db
from typing import Optional

router = APIRouter()

def mask_text(text: Optional[str]) -> Optional[str]:
    if not text or len(text) < 4:
        return "****"
    return "*" * (len(text) - 4) + text[-4:]

@router.get("/search", response_model=SearchResponse)
async def search_records(
    q: Optional[str] = Query(None, min_length=1),
    city: Optional[str] = None,
    constituency: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    current_user: UserData = Depends(get_current_user)
):
    with get_db() as db:
        # Log access
        db.execute(
            "INSERT INTO access_logs (user_id, action, details) VALUES ((SELECT id FROM users WHERE username=?), ?, ?)",
            (current_user.username, "SEARCH", f"q={q}, city={city}, const={constituency}")
        )
        db.commit()

        # Build Query
        sql_query = "SELECT * FROM records WHERE 1=1"
        params = []

        if q:
            sql_query += " AND (name LIKE ? OR phone LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%"])
        
        if city:
            sql_query += " AND city LIKE ?"
            params.append(f"%{city}%")
            
        if constituency:
            sql_query += " AND constituency LIKE ?"
            params.append(f"%{constituency}%")

        # Pagination
        offset = (page - 1) * limit
        
        # Count total
        count_sql = f"SELECT COUNT(*) as total FROM ({sql_query})"
        cursor = db.cursor()
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]

        # Execute main fetch
        sql_query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(sql_query, params)
        rows = cursor.fetchall()
    
    results = []
    for row in rows:
        data = dict(row)
        # Apply security masks for non-authorized roles
        if current_user.role not in ["admin", "superuser"]:
            data["phone"] = mask_text(data.get("phone"))
            data["misc"] = "PROTECTED"
        results.append(RecordOut(**data))
        
    return SearchResponse(
        results=results,
        total_count=total,
        page=page,
        limit=limit
    )
