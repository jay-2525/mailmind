import json
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.core.config import settings


class GoogleOAuthService:
    """
    Handles Google OAuth 2.0 authorization code flow, token exchange,
    and credential construction for Gmail and Google Calendar APIs.
    """

    def get_authorization_url(self, state: Optional[str] = None) -> Dict[str, str]:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            # Fallback or demo authorization redirect
            return {
                "auth_url": f"http://localhost:8000/api/v1/auth/google/callback?code=demo_auth_code_mock&state={state or 'demo'}",
                "is_demo": True
            }

        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=settings.GOOGLE_SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        auth_url, state_val = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=state
        )
        return {"auth_url": auth_url, "state": state_val, "is_demo": False}

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET or code.startswith("demo_"):
            return {
                "access_token": "demo_access_token_mock",
                "refresh_token": "demo_refresh_token_mock",
                "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
                "email": settings.DEMO_USER_EMAIL,
                "name": settings.DEMO_USER_NAME,
                "is_demo": True
            }

        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=settings.GOOGLE_SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Fetch user info
        oauth2_service = build("oauth2", "v2", credentials=credentials)
        user_info = oauth2_service.userinfo().get().execute()

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=credentials.expiry.timestamp() - datetime.now().timestamp()) if credentials.expiry else None

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_at": expires_at,
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "is_demo": False
        }


google_oauth_service = GoogleOAuthService()
