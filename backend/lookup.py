from fastapi import APIRouter, Depends, HTTPException
from backend.models import LookupRequest, LookupResponse, UserData
from backend.auth import get_current_admin
from phone_lookup.service import lookup_single
from typing import Dict

router = APIRouter()

@router.post("/lookup", response_model=LookupResponse)
async def perform_lookup(
    req: LookupRequest,
    current_admin: UserData = Depends(get_current_admin)
):
    """
    Admin-only endpoint to perform a single phone lookup across multiple providers.
    Uses the decoupled phone-lookup service.
    """
    try:
        findings, errors = lookup_single(req.phone)
        return LookupResponse(
            phone=req.phone,
            findings=findings,
            errors=errors
        )
    except Exception as e:
        # We don't want to expose internal traces, but we want to log it
        print(f"Lookup error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during lookup processing.")
