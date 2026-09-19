from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.integrations.google_oauth import google_oauth_service
from app.models.user import User, OAuthAccount
from app.demo.seed_data import seed_demo_data

router = APIRouter()


@router.get("/google/url")
def get_google_auth_url(state: str = "login"):
    return google_oauth_service.get_authorization_url(state=state)


@router.get("/google/callback")
def google_auth_callback(code: str, db: Session = Depends(get_db)):
    token_info = google_oauth_service.exchange_code_for_tokens(code)
    email = token_info.get("email") or settings.DEMO_USER_EMAIL
    name = token_info.get("name") or settings.DEMO_USER_NAME

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            full_name=name,
            is_demo=token_info.get("is_demo", False)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Save or update oauth account
    oauth_acc = db.query(OAuthAccount).filter(OAuthAccount.user_id == user.id).first()
    if not oauth_acc:
        oauth_acc = OAuthAccount(
            user_id=user.id,
            provider="google",
            access_token=token_info["access_token"],
            refresh_token=token_info.get("refresh_token"),
            expires_at=token_info.get("expires_at"),
            scopes=settings.GOOGLE_SCOPES
        )
        db.add(oauth_acc)
    else:
        oauth_acc.access_token = token_info["access_token"]
        if token_info.get("refresh_token"):
            oauth_acc.refresh_token = token_info["refresh_token"]
        oauth_acc.expires_at = token_info.get("expires_at")
    db.commit()

    jwt_token = create_access_token(user.id, expires_delta=timedelta(days=7))
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_demo": user.is_demo
        }
    }


@router.post("/demo")
def login_demo_user(db: Session = Depends(get_db)):
    """Instant one-click demo login returning token and user details."""
    user = db.query(User).filter(User.email == settings.DEMO_USER_EMAIL).first()
    if not user:
        user = seed_demo_data(db)

    jwt_token = create_access_token(user.id, expires_delta=timedelta(days=7))
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_demo": True
        }
    }


@router.get("/me")
def get_current_user_profile(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_demo": user.is_demo,
        "preferences": user.preferences or {}
    }


@router.post("/switch-mode")
def switch_active_mode(mode: str = "personal", db: Session = Depends(get_db)):
    """
    Switch active dashboard view between 'personal' (synced Gmail) and 'demo' (synthetic scenario).
    """
    if mode.lower() == "demo":
        user = db.query(User).filter(User.email == settings.DEMO_USER_EMAIL).first()
        if not user:
            user = seed_demo_data(db)
    else:
        user = db.query(User).filter(User.is_demo == False).order_by(User.created_at.desc()).first()
        if not user:
            raise HTTPException(status_code=404, detail="No personal Gmail account has been synchronized yet. Use the Chrome Extension to sync your Gmail.")

    jwt_token = create_access_token(user.id, expires_delta=timedelta(days=7))
    return {
        "status": "SUCCESS",
        "mode": "demo" if user.is_demo else "personal",
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_demo": user.is_demo
        }
    }

