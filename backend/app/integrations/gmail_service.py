import base64
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class GmailService:
    """
    Gmail API integration service for email ingestion and post-approval actions
    (Archive, Trash, Labels). In demo mode, executes safe simulated actions.
    """

    def _get_service(self, access_token: str, refresh_token: Optional[str] = None):
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=None,
            client_secret=None
        )
        return build("gmail", "v1", credentials=creds)

    def archive_email(self, message_id_external: str, access_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Archive an email by removing the INBOX label.
        """
        if not access_token or access_token.startswith("demo_"):
            return {"status": "SUCCESS", "action": "ARCHIVE", "message_id": message_id_external, "simulated": True}

        try:
            service = self._get_service(access_token)
            service.users().messages().modify(
                userId="me",
                id=message_id_external,
                body={"removeLabelIds": ["INBOX"]}
            ).execute()
            return {"status": "SUCCESS", "action": "ARCHIVE", "message_id": message_id_external, "simulated": False}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    def trash_email(self, message_id_external: str, access_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Move email to Gmail Trash.
        """
        if not access_token or access_token.startswith("demo_"):
            return {"status": "SUCCESS", "action": "TRASH", "message_id": message_id_external, "simulated": True}

        try:
            service = self._get_service(access_token)
            service.users().messages().trash(
                userId="me",
                id=message_id_external
            ).execute()
            return {"status": "SUCCESS", "action": "TRASH", "message_id": message_id_external, "simulated": False}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    def add_label(self, message_id_external: str, label_name: str, access_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply a label to the message.
        """
        if not access_token or access_token.startswith("demo_"):
            return {"status": "SUCCESS", "action": "ADD_LABEL", "label": label_name, "simulated": True}

        try:
            service = self._get_service(access_token)
            service.users().messages().modify(
                userId="me",
                id=message_id_external,
                body={"addLabelIds": [label_name]}
            ).execute()
            return {"status": "SUCCESS", "action": "ADD_LABEL", "label": label_name, "simulated": False}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}


gmail_service = GmailService()
