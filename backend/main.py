from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from backend import auth, search, ingest
import time
import os

app = FastAPI(title="DGT Data Portal")

# CORS
origins = ["*"] # Allow all for easier deployment, or customize as needed

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
    print(f"INTERNAL ERROR: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please contact admin."},
    )

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(ingest.router, prefix="/api/admin", tags=["Ingestion"])

# Serve Static Files
# Mounted at /static for app.js and style.css
# The root / will serve index.html
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# Serve other static assets
@app.get("/style.css")
async def get_style():
    with open("style.css", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="text/css")

@app.get("/app.js")
async def get_app():
    with open("app.js", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="application/javascript")

