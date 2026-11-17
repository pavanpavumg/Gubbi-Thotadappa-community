# RBDGTC Referral Portal - Python FastAPI Backend

An independent, production-ready REST API built with **Python 3.11+**, **FastAPI**, **SQLAlchemy 2.0 (Async)**, and **Pydantic v2**. 

Architected with **SOLID principles** and comprehensive **OWASP vulnerability mitigations**.

---

## Architecture & SOLID Principles

- **Single Responsibility (SRP)**: Distinct domains for Auth, Profiles, Openings, Referrals, Notifications, and Admin.
- **Open/Closed (OCP)**: Pluggable storage providers and notification handlers implementing common interfaces.
- **Liskov Substitution (LSP)**: Interchangeable storage adapters and repository layers.
- **Interface Segregation (ISP)**: Granular, role-based endpoint specifications.
- **Dependency Inversion (DIP)**: Controllers depend on abstractions via FastAPI's `Depends()` injection.

---

## Security Vulnerability Mitigations (OWASP Top 10)

1. **SQL Injection Defense**: 100% parameterized queries via Async SQLAlchemy 2.0 ORM.
2. **Password Security**: Bcrypt with automatic salt generation and work factor >= 12.
3. **Broken Object Level Authorization (BOLA/IDOR)**:
   - Resumes can ONLY be downloaded by: the student owner, the opening's reviewing alumnus, or an admin.
   - Openings can only be edited/managed by their alumni creator or admin.
4. **Malicious File Upload Defense**:
   - Enforces `application/pdf` MIME type AND `.pdf` extension.
   - Inspects file header magic bytes (`%PDF-`).
   - Caps upload size strictly to 5MB.
   - Prevents path traversal via UUID-based isolated file naming.
5. **CORS & HTTP Security Headers**:
   - Explicit allowed origins.
   - `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`.

---

## Quick Start (Local Development)

### 1. Create and Activate Virtual Environment
```bash
cd backend
python -m venv venv

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

- **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## Run with Docker Compose
To run both the Python API and PostgreSQL database with one command:
```bash
docker compose up --build
```

---

## Deployment & Hosting

- **API**: Deploy to **Railway.app** or **Render.com** (point to `backend/Dockerfile` or run command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
- **Database**: Connect to any PostgreSQL instance (Neon.tech, Supabase, RDS) by updating `DATABASE_URL` in `.env`.
