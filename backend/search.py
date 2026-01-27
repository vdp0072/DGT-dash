from fastapi import APIRouter, Depends, Query
from backend.models import SearchResponse, RecordOut, UserData
from backend.auth import get_current_user
from backend.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
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
    area: Optional[str] = None,
    sort_by: str = Query("name", regex="^(name|age)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    page: int = 1,
    limit: int = 50,
    current_user: UserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Log access
    db.execute(
        text("INSERT INTO access_logs (username, action, details) VALUES (:u, :a, :d)"),
        {"u": current_user.username, "a": "SEARCH", "d": f"q={q}, city={city}, area={area}, sort={sort_by} {order}"}
    )
    db.commit()

    # Build Query
    sql_base = "FROM records WHERE 1=1"
    params = {}

    if q:
        sql_base += " AND (name LIKE :q OR phone LIKE :q)"
        params["q"] = f"%{q}%"
    
    if city:
        sql_base += " AND city LIKE :city"
        params["city"] = f"%{city}%"
        
    if area:
        sql_base += " AND area LIKE :area"
        params["area"] = f"%{area}%"

    # Sorting
    sql_base += f" ORDER BY {sort_by} {order.upper()}"

    # Pagination
    offset = (page - 1) * limit
    
    # Count total
    count_sql = text(f"SELECT COUNT(*) FROM records WHERE 1=1 {''.join(sql_base.split('WHERE 1=1')[1:]).split('ORDER BY')[0]}")
    # Actually, simpler to just get the WHERE part
    where_parts = sql_base.split("WHERE 1=1")[1].split("ORDER BY")[0]
    count_sql = text(f"SELECT COUNT(*) FROM records WHERE 1=1 {where_parts}")
    total = db.execute(count_sql, params).scalar()

    # Execute main fetch
    fetch_sql = text(f"SELECT * {sql_base} LIMIT :limit OFFSET :offset")
    params.update({"limit": limit, "offset": offset})
    
    rows = db.execute(fetch_sql, params).fetchall()

    
    results = []
    for row in rows:
        data = dict(row._mapping)
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
