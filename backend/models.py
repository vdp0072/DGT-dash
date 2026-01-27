from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime

# --- Auth Models ---
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserData(BaseModel):
    username: str
    role: str

# --- Record Models ---
class RecordBase(BaseModel):
    name: str = Field(..., description="Full Name")
    fathers_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    misc: Optional[str] = None

class RecordOut(RecordBase):
    id: Optional[int] = None
    source_file_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    results: List[RecordOut]
    total_count: int = 0
    page: int = 1
    limit: int = 50

# --- Ingestion Models ---
class IngestionSummary(BaseModel):
    filename: str
    status: str
    total_rows: int
    inserted_rows: int
    rejected_rows: int
    rejection_reason: Optional[str] = None
    log_id: int
