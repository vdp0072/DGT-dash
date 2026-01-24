# DGT Data Portal - Implementation Complete

## Project Structure

```
d:/DGT_dash/
├── backend/
│   ├── __init__.py       (empty)
│   ├── auth.py           # JWT authentication, login endpoint
│   ├── database.py       # SQLite connection utilities
│   ├── init_db.py        # DB schema initialization & seeding
│   ├── ingest.py         # File upload & data ingestion (admin)
│   ├── main.py           # FastAPI app entrypoint
│   ├── models.py         # Pydantic schemas
│   └── search.py         # Search endpoint with role-based masking
├── index.html            # Frontend SPA
├── style.css             # Dark-mode glassmorphism styles
├── app.js                # Frontend logic (auth, search, ingest)
├── requirements.txt      # Python dependencies
├── dgt.db                # SQLite database (auto-created)
├── test_e2e.py           # End-to-end API tests
└── implementation_plan.md
```

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Stores credentials, roles (admin/user) |
| `records` | Core data: name, age, gender, constituency, city, company, phone, misc |
| `ingestion_logs` | Audit trail for file uploads |
| `access_logs` | Audit trail for searches |

## Role Permissions

| Feature | Admin | User |
|---------|-------|------|
| Login | ✓ | ✓ |
| Search | ✓ (full data) | ✓ (masked phone/misc) |
| Data Ingestion | ✓ | ✗ |
| View Logs | ✓ | ✗ |

## API Endpoints

- `POST /api/auth/login` – Authenticate user
- `GET /api/search` – Search records (with query params: q, city, constituency)
- `POST /api/admin/ingest` – Upload CSV/XLSX/JSON (admin only)

## Running the Application

```bash
# 1. Activate venv
cd d:/DGT_dash

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database (if not exists)
python backend/init_db.py

# 4. Start server
uvicorn backend.main:app --host 127.0.0.1 --port 8000

# 5. Open frontend
# Option A: Direct file (CORS now supported)
start index.html

# Option B: Local server (recommended)
python -m http.server 3000
# Then open http://localhost:3000
```

## Default Credentials

- **Admin**: `admin` / `admin123`

## Security Implementation

1. **Role-based masking**: User role sees masked phone numbers and "PROTECTED" misc fields
2. **Parameterized queries**: All SQL uses `?` placeholders
3. **Audit logging**: Every search is logged to `access_logs`
4. **JWT tokens**: 60-minute expiry with role claims
5. **Global error handler**: Hides stack traces from users
