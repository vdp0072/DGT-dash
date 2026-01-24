from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend import auth, search, ingest
import time

app = FastAPI(title="DGT Data Portal")

# CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "null"  # For file:// protocol
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log error internally here (print or file)
    print(f"INTERNAL ERROR: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please contact admin."},
    )

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(ingest.router, prefix="/api/admin", tags=["Ingestion"])

@app.get("/")
def read_root():
    return {"message": "DGT Portal API is running"}
