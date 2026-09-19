from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
import app.models  # Register all SQLAlchemy models
from app.demo.seed_data import seed_demo_data

# Import API routers
from app.api.v1.auth import router as auth_router
from app.api.v1.emails import router as emails_router
from app.api.v1.storage import router as storage_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.resume import router as resume_router
from app.api.v1.rag import router as rag_router
from app.api.v1.approvals import router as approvals_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.audit import router as audit_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.demo import router as demo_router
from app.api.v1.academic_demo import router as academic_demo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema exists and initialize demo data if empty
    print(f"[{settings.APP_NAME}] Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        from app.models.user import User
        existing = db.query(User).filter(User.email == settings.DEMO_USER_EMAIL).first()
        if not existing:
            print(f"[{settings.APP_NAME}] Seeding initial demo dataset...")
            seed_demo_data(db)
        print(f"[{settings.APP_NAME}] System ready in {settings.APP_ENV.upper()} mode!")
    finally:
        db.close()

    yield
    print(f"[{settings.APP_NAME}] Shutting down cleanly.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Agentic AI Email and Career Intelligence System (Product: InboxGuard)",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST API routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(emails_router, prefix="/api/v1/emails", tags=["Emails & Threads"])
app.include_router(storage_router, prefix="/api/v1/storage", tags=["Storage Intelligence"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["Tasks & Commitments"])
app.include_router(jobs_router, prefix="/api/v1/jobs", tags=["Job Intelligence"])
app.include_router(resume_router, prefix="/api/v1/resume", tags=["Resume Management"])
app.include_router(rag_router, prefix="/api/v1/rag", tags=["Historical RAG"])
app.include_router(approvals_router, prefix="/api/v1/approvals", tags=["Approval Center"])
app.include_router(calendar_router, prefix="/api/v1/calendar", tags=["Google Calendar"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["Audit Logging"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard Intelligence"])
app.include_router(demo_router, prefix="/api/v1/demo", tags=["Demo Mode"])
app.include_router(academic_demo_router, prefix="/api/v1/academic-demo", tags=["Academic Viva Mode"])


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "application": settings.APP_NAME,
        "status": "ONLINE",
        "docs_url": "/docs",
        "demo_mode": settings.DEMO_MODE
    }


@app.get("/health")
def health():
    return {"status": "HEALTHY", "version": "1.0.0"}
