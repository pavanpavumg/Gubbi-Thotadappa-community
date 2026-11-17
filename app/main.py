from contextlib import asynccontextmanager
from datetime import date
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.api.v1.router import api_v1_router
from app.models.user import AdminAllowlist, User, UserRole
from app.models.profile import Profile
from app.models.opening import Opening
from app.core.security import get_password_hash

async def seed_initial_data():
    """Seeds default admin allowlist and sample openings if database is new."""
    async with AsyncSessionLocal() as session:
        # 1. Admin allowlist
        default_admin_email = "pavanmg9964@gmail.com"
        admin_entry = await session.get(AdminAllowlist, default_admin_email)
        if not admin_entry:
            session.add(AdminAllowlist(email=default_admin_email))
            await session.commit()

        # 2. Seed initial openings if empty
        from sqlalchemy import select, func
        count_res = await session.execute(select(func.count(Opening.id)))
        if (count_res.scalar() or 0) == 0:
            sample_openings = [
                Opening(
                    poster_name="Kiran Gowda",
                    poster_batch=2016,
                    company="Infosys",
                    role="Systems Engineer",
                    domain="Software",
                    location="Mysuru",
                    experience="Fresher",
                    eligible_branches=["CSE", "ISE", "ECE", "EEE", "AIML", "MCA"],
                    apply_link="https://www.infosys.com/careers",
                    deadline=date(2027, 12, 20),
                    description="Campus-equivalent hiring for hostel residents. Strong DSA, OOP and DBMS basics.",
                    max_referrals=5,
                    status="open"
                ),
                Opening(
                    poster_name="Ananya Rao",
                    poster_batch=2018,
                    company="Bosch Global Software",
                    role="Embedded Software Trainee",
                    domain="Embedded",
                    location="Bengaluru",
                    experience="Fresher",
                    eligible_branches=["ECE", "EEE", "CSE", "MTech"],
                    apply_link="https://www.bosch-softwaretechnologies.com/careers",
                    deadline=date(2027, 12, 31),
                    description="Work on automotive ECUs. C, microcontrollers and RTOS basics expected.",
                    max_referrals=3,
                    status="open"
                ),
                Opening(
                    poster_name="Deepa Hegde",
                    poster_batch=2019,
                    company="Deloitte",
                    role="Business Analyst",
                    domain="Consulting",
                    location="Bengaluru",
                    experience="Fresher",
                    eligible_branches=["MBA", "CSE", "ISE"],
                    apply_link="https://www2.deloitte.com/in/en/careers.html",
                    deadline=date(2027, 12, 15),
                    description="Client-facing analyst role. Excel, SQL and structured problem solving.",
                    max_referrals=2,
                    status="open"
                )
            ]
            for op in sample_openings:
                session.add(op)
            await session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schemas on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    yield
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Independent, secure backend REST API for RBDGTC Referral Portal following SOLID principles.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# OWASP Defense: Secure CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin"],
)

# OWASP Defense: HTTP Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Central API Router
app.include_router(api_v1_router)

@app.get("/health", tags=["Health"])
async def health_check():
    """Service health and uptime check."""
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": "1.0.0"}
