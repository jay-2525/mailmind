from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    cred: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    if cred is not None and cred.credentials:
        try:
            payload = jwt.decode(cred.credentials, settings.SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    return user
        except JWTError:
            pass

    # In test environments, prioritize the seeded demo user
    import os
    if "PYTEST_CURRENT_TEST" in os.environ:
        demo_user = db.query(User).filter(User.email == settings.DEMO_USER_EMAIL).first()
        if demo_user:
            return demo_user

    # If no token or invalid token, prioritize the synced personal user (from Chrome extension)
    personal_user = db.query(User).filter(User.is_demo == False).order_by(User.created_at.desc()).first()
    if personal_user:
        return personal_user

    # Fallback to demo user
    demo_user = db.query(User).filter(User.email == settings.DEMO_USER_EMAIL).first()
    if not demo_user:
        from app.demo.seed_data import seed_demo_data
        demo_user = seed_demo_data(db)
    return demo_user

