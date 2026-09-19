from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.demo.seed_data import seed_demo_data
from app.core.config import settings

router = APIRouter()


@router.get("/status")
def get_demo_status():
    return {
        "demo_mode": settings.DEMO_MODE,
        "demo_user_email": settings.DEMO_USER_EMAIL,
        "demo_user_name": settings.DEMO_USER_NAME,
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER
    }


@router.post("/reset")
def reset_demo_dataset(
    db: Session = Depends(get_db)
):
    """
    Resets the database with fresh, clean seeded demo emails, resume, tasks, and jobs.
    """
    user = seed_demo_data(db)
    return {
        "status": "SUCCESS",
        "message": f"Demo dataset re-seeded successfully for {user.email}."
    }
